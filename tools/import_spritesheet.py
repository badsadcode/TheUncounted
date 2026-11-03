#!/usr/bin/env python3
"""
Imports a hand-painted / external 8x6 sprite sheet into the engine's sheet contract.

Input: an image laid out as 8 columns (directions: 0 front, 1 front-left, 2 left, 3 back-left, 4 back, 5 back-right,
6 right, 7 front-right) x 6 rows (idle, walk A, walk B, windup, attack, stagger cols 0-3 / corpse cols 4-7), on a flat
black (or any solid) background.

What it does: removes the background (soft alpha ramp so the edges don't fringe), slices the even grid, scales every
frame by one shared factor chosen so the new art is as tall in its frame as the sheet it replaces (so in-game size
stays the same), keeps each frame's horizontal position relative to its cell (no walk-cycle jitter), plants the feet on
the pivot row, and writes a matching animation JSON with the new frame size.

Run:  python tools/import_spritesheet.py SRC DST_PNG --frame 128 --match assets/sprites/enemies/old.png \
          --anim-from assets/animations/old.json --anim-out assets/animations/new.json
"""
import argparse
import json

import numpy as np
from PIL import Image

COLS, ROWS, PIVOT_Y = 8, 6, 0.92


def remove_background(img, bg, lo, hi):
    a = np.asarray(img.convert("RGB")).astype(np.int32)
    d = np.abs(a - np.array(bg)).max(axis=2)
    alpha = np.clip((d - lo) * 255 // max(1, hi - lo), 0, 255).astype(np.uint8)
    rgba = np.dstack([a.astype(np.uint8), alpha])
    return Image.fromarray(rgba, "RGBA")


def label_components(alpha, thresh=8):
    """8-connected components of the opaque pixels. Returns (labels array, list of (count, sum_x, sum_y))."""
    from collections import deque
    h, w = alpha.shape
    mask = alpha > thresh
    labels = np.zeros((h, w), dtype=np.int32)
    stats = [None]
    ys, xs = np.nonzero(mask)
    for y0, x0 in zip(ys.tolist(), xs.tolist()):
        if labels[y0, x0]:
            continue
        lab = len(stats)
        labels[y0, x0] = lab
        q = deque([(y0, x0)])
        n = sx = sy = 0
        while q:
            y, x = q.popleft()
            n += 1; sx += x; sy += y
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    yy, xx = y + dy, x + dx
                    if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not labels[yy, xx]:
                        labels[yy, xx] = lab
                        q.append((yy, xx))
        stats.append((n, sx / n, sy / n))
    return labels, stats


def old_height_fraction(path, col):
    im = Image.open(path).convert("RGBA")
    fw = im.width // COLS
    bb = im.crop((col * fw, 0, col * fw + fw, fw)).getbbox()
    return (bb[3] - bb[1]) / fw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--frame", type=int, default=128)
    ap.add_argument("--match", help="existing sheet whose in-frame height to match")
    ap.add_argument("--match-col", type=int, default=2, help="idle column used to compare heights")
    ap.add_argument("--height", type=float, default=0.85, help="target idle height fraction when --match is not given")
    ap.add_argument("--bg", default="0,0,0")
    ap.add_argument("--lo", type=int, default=10)
    ap.add_argument("--hi", type=int, default=34)
    ap.add_argument("--anim-from")
    ap.add_argument("--anim-out")
    a = ap.parse_args()

    src = remove_background(Image.open(a.src), [int(v) for v in a.bg.split(",")], a.lo, a.hi)
    cw, ch = src.width / COLS, src.height / ROWS
    # Assign every blob (connected opaque region) to the cell its centre lies in, so a tail that pokes across a cell
    # border stays with its owner instead of turning up as a stray sliver next door. Specks are dropped.
    arr = np.asarray(src)
    labels, stats = label_components(arr[:, :, 3])
    owner = np.zeros(len(stats), dtype=np.int32) - 1
    for lab in range(1, len(stats)):
        n, mx, my = stats[lab]
        if n >= 12:
            owner[lab] = min(ROWS - 1, int(my // ch)) * COLS + min(COLS - 1, int(mx // cw))
    own = owner[labels]
    cells, boxes = {}, {}
    pad = int(max(cw, ch) * 0.25)
    for r in range(ROWS):
        for c in range(COLS):
            x0, y0 = max(0, round(c * cw) - pad), max(0, round(r * ch) - pad)
            x1, y1 = min(src.width, round((c + 1) * cw) + pad), min(src.height, round((r + 1) * ch) + pad)
            sub = arr[y0:y1, x0:x1].copy()
            sub[:, :, 3] = np.where(own[y0:y1, x0:x1] == r * COLS + c, sub[:, :, 3], 0)
            cell = Image.fromarray(sub, "RGBA")
            cells[r, c] = (cell, (round(c * cw) - x0 + cw / 2))  # cell image and where the grid cell's centre is in it
            boxes[r, c] = cell.getbbox()

    F = a.frame
    target = old_height_fraction(a.match, a.match_col) if a.match else a.height
    ref = boxes[0, a.match_col]
    scale = target * F / (ref[3] - ref[1])
    # Never let any frame spill out of its cell.
    for (r, c), bb in boxes.items():
        if bb:
            scale = min(scale, (F - 2) / (bb[2] - bb[0]), (F * PIVOT_Y - 1) / (bb[3] - bb[1]))

    sheet = Image.new("RGBA", (F * COLS, F * ROWS), (0, 0, 0, 0))
    for (r, c), (cell, centre) in cells.items():
        bb = boxes[r, c]
        if not bb:
            continue
        part = cell.crop(bb)
        w, h = max(1, round(part.width * scale)), max(1, round(part.height * scale))
        part = part.resize((w, h), Image.LANCZOS)
        # Horizontal: keep the offset from the cell centre. Vertical: feet on the pivot row.
        cx = (bb[0] + bb[2]) / 2 - centre
        x = round(F / 2 + cx * scale - w / 2)
        x = max(0, min(F - w, x))
        y = round(F * PIVOT_Y - h)
        sheet.alpha_composite(part, (c * F + x, r * F + max(0, y)))
    sheet.save(a.dst)
    print(f"Wrote {a.dst}: {F}px frames, scale {scale:.3f}")

    if a.anim_from and a.anim_out:
        anim = json.load(open(a.anim_from))
        anim["frame_width"] = anim["frame_height"] = F
        anim["pivot"] = [0.5, PIVOT_Y]
        json.dump(anim, open(a.anim_out, "w"), indent=2)
        print("Wrote", a.anim_out)


if __name__ == "__main__":
    main()

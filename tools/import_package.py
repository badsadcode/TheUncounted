#!/usr/bin/env python3
"""
Batch-import a whole package of hand-painted 8x6 sprite sheets (a folder or a .zip) in one go.

    python tools/import_package.py PATH_TO_FOLDER_OR_ZIP            # dry run: shows which file goes to which character
    python tools/import_package.py PATH_TO_FOLDER_OR_ZIP --apply    # import everything and update the content files

For every image (png / webp / jpg) it:
  1. works out which character it is from the file name (e.g. "Vampire Ashgrave.webp", "vampire_ashgrave_v2.png",
     "Ashgrave.png", "12 - Kaelen.webp" all work; numbers, "sheet", "final", "v2" and similar noise are ignored),
  2. checks the sheet is roughly an 8x6 grid (4:3),
  3. copies the original to art_source/spritesheets/<sheet>.<ext> and runs tools/import_spritesheet.py on it
     (same in-game size as before; side-on animals compared on their profile column),
  4. points every NPC/creature that uses that sheet at the new PNG + the matching 128px animation,
  5. adds/keeps the row in art_source/README.md and drops the character from art_source/to_remake/,
  6. writes a review picture (--report, default import_report.png) with every imported sheet on grey with the grid
     drawn, and lists frames that look clipped (figure touching its cell edge) or are missing.

Files it can't place are listed and skipped; rename them (or pass --map file=sheet) and run again.
"""
import argparse
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT = [("content/npcs/core_npcs.json", "npcs"), ("content/creatures/core_creatures.json", "creatures")]
SIDE_ON_ANIMS = ("grave_rat", "ash_crawler")          # sheets whose idle height is best measured side-on
SIDE_ON_IDS = {"trout", "figure_snacks"}
NOISE = {"sheet", "sprite", "sprites", "spritesheet", "final", "new", "v", "v1", "v2", "v3", "fixed", "remake", "painted", "copy",
         "the", "of", "a", "png", "webp", "img", "image"}
EXTRA_ALIASES = {"kaelen": "ashbound_scout", "witness": "erased_spirit", "uncounted_witness": "erased_spirit", "morvath": "crypt_keeper",
                 "archivist": "crypt_keeper", "skeleton": "skeleton", "drowned": "the_drowned", "avatar": "name_eater_avatar",
                 "limb": "dreaming_limb", "hog": "truffle_hog", "sentinel": None, "host": "wrathful_host", "percival": "ghost_percival",
                 "silas": "silas_gale", "tom": "gale_elder", "thomas": "gale_elder", "abel": "gale_younger", "odette": "impresario_odette",
                 "mortimer": "critic_mortimer", "harbor_master": "harbourmaster", "rodrick": "figure_rodrick", "primrose": "figure_primrose",
                 "agnes": "figure_agnes", "snacks": "figure_snacks", "owlbear": "figure_snacks"}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def tokens(s):
    return [t for t in slug(s).split("_") if t and t not in NOISE and not t.isdigit()]


def load_sheets():
    """sheet base name -> {dir, users: [(file, list, index)], aliases, side_on, anim}"""
    loc = json.load(open(os.path.join(ROOT, "content/localization/en.json")))["strings"]
    sheets = {}
    for path, key in CONTENT:
        data = json.load(open(os.path.join(ROOT, path)))
        for i, e in enumerate(data[key]):
            a = e.get("appearance", {})
            if a.get("type") != "sprite_8dir" or not a.get("sprite_sheet"):
                continue
            if e["id"].startswith("core:npc.unmask_"):
                continue                                      # disguised suspects borrow other characters' sheets
            rel = a["sprite_sheet"]
            base = os.path.basename(rel).rsplit(".", 1)[0].replace("_painted", "")
            s = sheets.setdefault(base, {"dir": os.path.dirname(rel), "users": [], "aliases": set(), "side_on": False,
                                         "anim": a.get("animation_data", "")})
            sid = e["id"].split(".")[-1]
            s["users"].append((path, key, i, e["id"]))
            s["aliases"] |= {base, sid, slug(loc.get(e.get("name_key", ""), ""))}
            anim = os.path.basename(a.get("animation_data", ""))
            if any(anim.startswith(p) for p in SIDE_ON_ANIMS) or sid in SIDE_ON_IDS:
                s["side_on"] = True
    for alias, base in EXTRA_ALIASES.items():
        if base in sheets:
            sheets[base]["aliases"].add(alias)
    return sheets


def match(fname, sheets, forced):
    stem = os.path.basename(fname).rsplit(".", 1)[0]
    if stem in forced:
        return forced[stem], "forced"
    s = slug(stem)
    toks = tokens(stem)
    joined = "_".join(toks)
    for cand in (s, joined):
        hits = [b for b, d in sheets.items() if cand in d["aliases"]]
        if len(hits) == 1:
            return hits[0], "exact"
    # every word of the file name appears in exactly one character's aliases
    if toks:
        hits = [b for b, d in sheets.items() if any(set(toks) <= set(a.split("_")) for a in d["aliases"] if a)]
        if len(hits) == 1:
            return hits[0], "words"
        # or one distinctive word identifies a single character
        for t in toks:
            hits = [b for b, d in sheets.items() if any(t in a.split("_") for a in d["aliases"] if a)]
            if len(hits) == 1:
                return hits[0], f"word '{t}'"
    allal = {a: b for b, d in sheets.items() for a in d["aliases"] if a}
    close = difflib.get_close_matches(joined or s, list(allal), n=2, cutoff=0.82)
    if len(close) == 1 or (len(close) == 2 and allal[close[0]] == allal[close[1]]):
        return allal[close[0]], f"close to '{close[0]}'"
    return None, "no match" if not close else "ambiguous: " + ", ".join(allal[c] for c in close)


def anim_128(anim):
    if anim.endswith("_128.json"):
        return anim, None
    cand = anim.replace(".json", "_128.json")
    if os.path.exists(os.path.join(ROOT, cand)):
        return cand, None
    return cand, anim  # needs generating from the old one


def check_frames(png):
    """Return (clipped, missing) cell lists for an imported 128px sheet."""
    from PIL import Image
    im = Image.open(png).convert("RGBA")
    a = im.split()[3]
    F = im.width // 8
    clipped, missing = [], []
    for r in range(6):
        for c in range(8):
            if r == 5 and c > 4:
                continue
            cell = a.crop((c * F, r * F, (c + 1) * F, (r + 1) * F))
            if cell.getbbox() is None:
                missing.append((r, c))
                continue
            px = cell.load()
            edge = sum(1 for i in range(F) for (x, y) in ((i, 0), (i, F - 1), (0, i), (F - 1, i)) if px[x, y] > 128)
            if edge > 6:
                clipped.append((r, c))
    return clipped, missing


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package", help="folder or .zip of sprite sheets")
    ap.add_argument("--apply", action="store_true", help="actually import (default: dry run)")
    ap.add_argument("--map", action="append", default=[], help="force a match: FILE_STEM=SHEET (repeatable)")
    ap.add_argument("--report", default="import_report.png", help="review picture to write")
    a = ap.parse_args()

    tmp = None
    src = a.package
    if zipfile.is_zipfile(src):
        tmp = tempfile.mkdtemp()
        with zipfile.ZipFile(src) as z:
            for n in z.namelist():
                if n.endswith("/") or ".." in n or n.startswith("/"):
                    continue
                if n.lower().endswith((".png", ".webp", ".jpg", ".jpeg")) and "__MACOSX" not in n:
                    out = os.path.join(tmp, os.path.basename(n))
                    with z.open(n) as f, open(out, "wb") as o:
                        o.write(f.read())
        src = tmp
    files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(src) for f in fs
                   if f.lower().endswith((".png", ".webp", ".jpg", ".jpeg")) and not f.startswith("."))
    sheets = load_sheets()
    forced = dict(m.split("=", 1) for m in a.map)

    from PIL import Image
    plan, skipped, taken = [], [], {}
    for f in files:
        base, how = match(f, sheets, forced)
        w, h = Image.open(f).size
        ratio = (w / 8) / (h / 6)
        if base is None:
            skipped.append((f, how))
            continue
        if base in taken:
            skipped.append((f, f"duplicate of {os.path.basename(taken[base])} for {base}"))
            continue
        if not 0.8 < ratio < 1.25:
            skipped.append((f, f"not an 8x6 grid? {w}x{h} (cells {w / 8:.0f}x{h / 6:.0f})"))
            continue
        taken[base] = f
        plan.append((f, base, how))

    print(f"{len(files)} image(s), {len(plan)} matched, {len(skipped)} skipped\n")
    for f, base, how in plan:
        who = ", ".join(u[3].split(".")[-1] for u in sheets[base]["users"])
        print(f"  {os.path.basename(f):40s} -> {base:22s} ({who}) [{how}]")
    for f, why in skipped:
        print(f"  SKIP {os.path.basename(f):35s} {why}")
    missing_chars = sorted(b for b in sheets if b not in taken)
    if missing_chars:
        print("\nCharacters with no sheet in this package:", ", ".join(missing_chars))
    if not a.apply:
        print("\nDry run. Add --apply to import.")
        return 0

    contents = {p: json.load(open(os.path.join(ROOT, p))) for p, _ in CONTENT}
    readme_p = os.path.join(ROOT, "art_source/README.md")
    readme = open(readme_p).read()
    remake_p = os.path.join(ROOT, "art_source/to_remake/README.md")
    remake = open(remake_p).read() if os.path.exists(remake_p) else ""
    report = []
    for f, base, how in plan:
        d = sheets[base]
        ext = f.rsplit(".", 1)[1].lower()
        for old in ("png", "webp", "jpg", "jpeg"):
            p = os.path.join(ROOT, "art_source/spritesheets", f"{base}.{old}")
            if old != ext and os.path.exists(p):
                os.remove(p)
        orig = os.path.join(ROOT, "art_source/spritesheets", f"{base}.{ext}")
        shutil.copyfile(f, orig)
        dst = f"{d['dir']}/{base}_painted.png"
        old_ref = os.path.join(ROOT, d["dir"], base + ".png")
        new_anim, gen_from = anim_128(d["anim"])
        cmd = [sys.executable, os.path.join(ROOT, "tools/import_spritesheet.py"), orig, os.path.join(ROOT, dst), "--frame", "128",
               "--match-col", "2" if d["side_on"] else "0"]
        if os.path.exists(old_ref):
            cmd += ["--match", old_ref]
        if gen_from:
            cmd += ["--anim-from", os.path.join(ROOT, gen_from), "--anim-out", os.path.join(ROOT, new_anim)]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  FAILED {base}: {r.stderr.strip().splitlines()[-1] if r.stderr.strip() else r.returncode}")
            continue
        for path, key, i, _ in d["users"]:
            ap_ = contents[path][key][i]["appearance"]
            ap_["sprite_sheet"] = dst
            ap_["animation_data"] = new_anim
        row = f"| `spritesheets/{base}.{ext}` | `{dst}` |"
        lines = readme.split("\n")
        hit = next((k for k, ln in enumerate(lines) if f"| `{dst}` |" in ln), None)
        if hit is not None:
            m = re.match(r"\| `spritesheets/([^`]+)` \| `[^`]*` \|(.*)", lines[hit])
            if m:
                prev = os.path.join(ROOT, "art_source/spritesheets", m.group(1))
                if os.path.abspath(prev) != os.path.abspath(orig) and os.path.exists(prev):
                    os.remove(prev)                       # the old original under a different name
                lines[hit] = row + m.group(2)
            readme = "\n".join(lines)
        else:
            name = d["users"][0][3].split(".")[-1].replace("_", " ").title()
            if "\n\nRe-convert" in readme:
                readme = readme.replace("\n\nRe-convert", f"\n{row} {name} |\n\nRe-convert", 1)
            else:
                readme = readme.rstrip("\n") + f"\n{row} {name} |\n"
        if f"`{base}.png`" in remake:
            remake = re.sub(rf"\| `{re.escape(base)}\.png` .*\n", "", remake)
            p = os.path.join(ROOT, "art_source/to_remake", base + ".png")
            if os.path.exists(p):
                os.remove(p)
        clipped, missing = check_frames(os.path.join(ROOT, dst))
        report.append((base, dst, clipped, missing))
        flag = ""
        if clipped: flag += f"  clipped? rows/cols {clipped}"
        if missing: flag += f"  EMPTY {missing}"
        print(f"  imported {base:22s}{flag}")
    for p, key in CONTENT:
        open(os.path.join(ROOT, p), "w").write(json.dumps(contents[p], indent=2, ensure_ascii=False))
    open(readme_p, "w").write(readme)
    if remake:
        open(remake_p, "w").write(remake)

    # review picture: one strip per sheet (all 6 rows), grey background, red grid, name label
    if report:
        from PIL import ImageDraw
        S = 0.5
        W, H = int(1024 * S), int(768 * S)
        cols = 4
        rows = (len(report) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * W, rows * (H + 16)), (40, 40, 46))
        dr = ImageDraw.Draw(sheet)
        for n, (base, dst, clipped, missing) in enumerate(report):
            im = Image.open(os.path.join(ROOT, dst)).convert("RGBA")
            bg = Image.new("RGBA", im.size, (120, 120, 130, 255))
            bg.alpha_composite(im)
            g = ImageDraw.Draw(bg)
            for x in range(0, im.width + 1, 128): g.line([(x, 0), (x, im.height)], fill=(200, 40, 40, 255))
            for y in range(0, im.height + 1, 128): g.line([(0, y), (im.width, y)], fill=(200, 40, 40, 255))
            for (r, c) in clipped: g.rectangle([c * 128 + 2, r * 128 + 2, c * 128 + 125, r * 128 + 125], outline=(255, 220, 0, 255), width=4)
            for (r, c) in missing: g.rectangle([c * 128 + 2, r * 128 + 2, c * 128 + 125, r * 128 + 125], outline=(255, 0, 255, 255), width=4)
            x, y = (n % cols) * W, (n // cols) * (H + 16)
            sheet.paste(bg.convert("RGB").resize((W, H)), (x, y + 16))
            dr.text((x + 4, y + 2), base + ("  (check yellow frames)" if clipped else ""), fill=(255, 255, 255))
        sheet.save(a.report)
        print(f"\nReview picture: {a.report} (yellow = figure touches its cell edge, magenta = empty frame)")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)
    print("Next: ./game --validate, then look at a few characters in game.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

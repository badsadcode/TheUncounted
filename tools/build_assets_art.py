#!/usr/bin/env python3
"""
Offline Pixel-Art Texture, 8-Directional Sprite Sheet, UI Icon & Font Builder
for THE UNCOUNTED.
Writes standalone, replaceable PNG, JSON, and TTF files into assets/ and mods/.
The C++ runtime never calls this script; it loads the resulting external files.
"""

import json
import math
import os
import sys
import random
import shutil
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ensure_dir(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)


def clamp(v, lo=0, hi=255):
    return max(lo, min(hi, int(v)))


def make_noise_grid(w, h, seed):
    rng = random.Random(seed)
    return [[rng.randint(-18, 18) for _ in range(w)] for _ in range(h)]


# =============================================================================
# 1. ENVIRONMENT PIXEL-ART TEXTURES (64x64 tileable PNGs)
# =============================================================================
def build_textures():
    tex_dir = os.path.join(ROOT, "assets", "textures")
    os.makedirs(tex_dir, exist_ok=True)
    # The world textures are now Noor's hand-made set (128 px). Never overwrite them with these generated 64 px ones.
    if os.path.exists(os.path.join(tex_dir, "mossy_cobble.png")) and "--force-textures" not in sys.argv:
        print("Skipping generated textures (hand-made set present; pass --force-textures to regenerate)")
        return

    # 1. stone_wall.png - Medieval grey-blue cut stone blocks
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 101)
    for y in range(64):
        row = y // 16
        y_in_row = y % 16
        offset = (row % 2) * 16
        for x in range(64):
            x_in_brick = (x + offset) % 32
            is_mortar = (y_in_row == 0 or y_in_row == 15 or x_in_brick == 0 or x_in_brick == 31)
            if is_mortar:
                c = 42 + n[y][x] // 3
                px[x, y] = (clamp(c), clamp(c + 2), clamp(c + 5), 255)
            else:
                brick_id = row * 7 + ((x + offset) // 32)
                b_tint = ((brick_id * 19) % 24) - 12
                bevel = 10 if (y_in_row == 1 or x_in_brick == 1) else (-10 if (y_in_row == 14 or x_in_brick == 30) else 0)
                base = 105 + b_tint + bevel + n[y][x] // 2
                px[x, y] = (clamp(base - 4), clamp(base), clamp(base + 8), 255)
    img.save(os.path.join(tex_dir, "stone_wall.png"))

    # 2. crypt_brick.png - Dark mossy ancient crypt masonry
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 202)
    for y in range(64):
        row = y // 12
        y_in_row = y % 12
        offset = (row % 2) * 12
        for x in range(64):
            x_in_brick = (x + offset) % 24
            is_mortar = (y_in_row == 0 or x_in_brick == 0)
            moss = ((x * 13 + y * 29 + n[y][x]) % 37 < 6) and (y > 36 or is_mortar)
            if moss:
                g = 68 + n[y][x] // 2
                px[x, y] = (clamp(g - 32), clamp(g + 12), clamp(g - 28), 255)
            elif is_mortar:
                c = 26 + n[y][x] // 4
                px[x, y] = (clamp(c), clamp(c + 2), clamp(c + 4), 255)
            else:
                bevel = 8 if y_in_row == 1 else (-8 if y_in_row == 11 else 0)
                base = 64 + bevel + n[y][x] // 2
                px[x, y] = (clamp(base - 6), clamp(base - 2), clamp(base + 6), 255)
    img.save(os.path.join(tex_dir, "crypt_brick.png"))

    # 3. mossy_cobble.png - Village cobblestone / dungeon floor
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 303)
    centers = [
        (8, 8, 9), (26, 10, 10), (46, 8, 9), (58, 12, 8),
        (14, 26, 10), (34, 28, 11), (52, 26, 9),
        (8, 44, 9), (26, 46, 10), (46, 44, 10),
        (16, 58, 8), (36, 58, 9), (54, 58, 8)
    ]
    for y in range(64):
        for x in range(64):
            best_d = 999.0
            best_idx = 0
            for idx, (cx, cy, r) in enumerate(centers):
                for ox in (-64, 0, 64):
                    for oy in (-64, 0, 64):
                        d = math.hypot(x - (cx + ox), y - (cy + oy)) / r
                        if d < best_d:
                            best_d = d
                            best_idx = idx
            if best_d > 0.88:
                # Mud/moss gap
                px[x, y] = (clamp(38 + n[y][x] // 3), clamp(48 + n[y][x] // 2), clamp(36 + n[y][x] // 3), 255)
            else:
                shade = int((1.0 - best_d * 0.45) * 95) + ((best_idx * 13) % 18 - 9) + n[y][x] // 2
                px[x, y] = (clamp(shade - 4), clamp(shade), clamp(shade + 4), 255)
    img.save(os.path.join(tex_dir, "mossy_cobble.png"))

    # 4. wood_planks.png - Warm oak planks for doors, floors, furniture
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 404)
    for y in range(64):
        for x in range(64):
            plank = x // 16
            x_in_p = x % 16
            seam = (x_in_p == 0 or (y == (plank * 23 + 12) % 64))
            if seam:
                px[x, y] = (46, 30, 18, 255)
            else:
                grain = int(math.sin((y * 0.35) + plank * 2.1) * 8) + n[y][x] // 3
                r = 122 + grain + (plank % 2) * 8
                g = 84 + grain + (plank % 2) * 5
                b = 48 + grain // 2
                px[x, y] = (clamp(r), clamp(g), clamp(b), 255)
    img.save(os.path.join(tex_dir, "wood_planks.png"))

    # 5. timber_plaster.png - Tudor timber-framed cottage wall for Bellwether
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 505)
    for y in range(64):
        for x in range(64):
            beam = (x < 6 or x >= 58 or y < 6 or y >= 58 or (29 <= x <= 34) or abs(x - y) < 4)
            if beam:
                g = n[y][x] // 3
                px[x, y] = (clamp(76 + g), clamp(50 + g), clamp(32 + g), 255)
            else:
                c = 196 + n[y][x] // 2
                px[x, y] = (clamp(c), clamp(c - 8), clamp(c - 24), 255)
    img.save(os.path.join(tex_dir, "timber_plaster.png"))

    # 6. roof_shingles.png - Dark slate/wood roof tiles
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 606)
    for y in range(64):
        row = y // 8
        y_in = y % 8
        off = (row % 2) * 8
        for x in range(64):
            x_in = (x + off) % 16
            edge = (y_in == 7 or x_in == 0)
            c = (38 if edge else (62 + y_in * 2)) + n[y][x] // 3
            px[x, y] = (clamp(c - 6), clamp(c), clamp(c + 12), 255)
    img.save(os.path.join(tex_dir, "roof_shingles.png"))

    # 7. forest_grass.png - Rich dark woodland turf
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 707)
    for y in range(64):
        for x in range(64):
            blade = ((x * 7 + y * 13) % 11 == 0)
            base_g = 76 + n[y][x] // 2 + (14 if blade else 0)
            px[x, y] = (clamp(base_g - 34), clamp(base_g), clamp(base_g - 38), 255)
    img.save(os.path.join(tex_dir, "forest_grass.png"))

    # 8. dirt_road.png - Earthy gravel road texture
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 808)
    for y in range(64):
        for x in range(64):
            pebble = ((x * 17 + y * 31) % 19 == 0)
            v = 96 + n[y][x] // 2 + (18 if pebble else 0)
            px[x, y] = (clamp(v), clamp(v - 18), clamp(v - 38), 255)
    img.save(os.path.join(tex_dir, "dirt_road.png"))

    # 9. iron_metal.png - Forged dark iron for gates, chests, levers, weapons
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 909)
    for y in range(64):
        for x in range(64):
            rivet = ((x % 16 in (3, 4)) and (y % 16 in (3, 4)))
            v = 84 + n[y][x] // 2 + (28 if rivet else 0)
            px[x, y] = (clamp(v - 4), clamp(v), clamp(v + 8), 255)
    img.save(os.path.join(tex_dir, "iron_metal.png"))

    # 10. bookshelf_tex.png - Library shelves packed with old ledgers & tomes
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 1010)
    book_colors = [(145, 42, 38), (46, 92, 68), (52, 68, 128), (138, 108, 46), (92, 48, 98), (112, 76, 52)]
    for y in range(64):
        shelf_y = y % 16
        for x in range(64):
            if shelf_y < 3 or x < 3 or x >= 61:
                px[x, y] = (86, 56, 32, 255)
            elif shelf_y < 5:
                px[x, y] = (24, 18, 16, 255)
            else:
                book_idx = (x // 5) + (y // 16) * 13
                col = book_colors[book_idx % len(book_colors)]
                spine_edge = (x % 5 == 0)
                gold_band = (shelf_y in (7, 12)) and not spine_edge
                if spine_edge:
                    px[x, y] = (28, 20, 18, 255)
                elif gold_band:
                    px[x, y] = (210, 175, 75, 255)
                else:
                    d = n[y][x] // 3
                    px[x, y] = (clamp(col[0] + d), clamp(col[1] + d), clamp(col[2] + d), 255)
    img.save(os.path.join(tex_dir, "bookshelf_tex.png"))

    # 11. rune_crystal.png - Glowing pale-blue arcane / Great Silence stone
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 1111)
    for y in range(64):
        for x in range(64):
            cx, cy = abs(x - 32), abs(y - 32)
            rune = (cx in (8, 9, 18) and cy < 22) or (cy in (8, 9, 18) and cx < 22)
            if rune:
                px[x, y] = (120, 225, 255, 255)
            else:
                v = 56 + n[y][x] // 2
                px[x, y] = (clamp(v - 10), clamp(v + 8), clamp(v + 28), 255)
    img.save(os.path.join(tex_dir, "rune_crystal.png"))

    # 12. gold_trim.png - Warm brass/gold accents for shrines, chests, hilts
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 1212)
    for y in range(64):
        for x in range(64):
            d = n[y][x] // 2
            px[x, y] = (clamp(212 + d), clamp(172 + d), clamp(68 + d), 255)
    img.save(os.path.join(tex_dir, "gold_trim.png"))

    # 13. foliage_pine.png - Pine needle texture
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 1313)
    for y in range(64):
        for x in range(64):
            d = n[y][x] // 2
            px[x, y] = (clamp(32 + d // 2), clamp(72 + d), clamp(42 + d // 2), 255)
    img.save(os.path.join(tex_dir, "foliage_pine.png"))

    # 14. parchment_tex.png - Aged paper for scrolls, ledgers, notices
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    n = make_noise_grid(64, 64, 1414)
    for y in range(64):
        for x in range(64):
            ink = (8 <= x <= 55) and (y % 6 == 3) and ((x + y) % 7 != 0)
            if ink:
                px[x, y] = (52, 38, 28, 255)
            else:
                d = n[y][x] // 3
                px[x, y] = (clamp(224 + d), clamp(204 + d), clamp(162 + d), 255)
    img.save(os.path.join(tex_dir, "parchment_tex.png"))

    # 15. diag_missing.png - Diagnostic checkerboard when a mod/content path is missing
    img = Image.new("RGBA", (64, 64))
    px = img.load()
    for y in range(64):
        for x in range(64):
            chk = ((x // 8) + (y // 8)) % 2 == 0
            px[x, y] = (255, 0, 220, 255) if chk else (24, 0, 32, 255)
    img.save(os.path.join(tex_dir, "diag_missing.png"))


# =============================================================================
# 2. 8-DIRECTIONAL & ANIMATED SPRITE SHEETS (PNG + JSON)
# =============================================================================
# Layout convention for 8-directional character/creature sheets:
#   Frame size: 64x64 pixels
#   Columns (0..7): 8 directions relative to viewer:
#     0 = Front (facing camera)
#     1 = Front-Left
#     2 = Left
#     3 = Back-Left
#     4 = Back (facing away)
#     5 = Back-Right
#     6 = Right
#     7 = Front-Right
#   Rows (0..5): Animation states:
#     Row 0: Idle frame 0
#     Row 1: Walk frame 0 (left step)
#     Row 2: Walk frame 1 (right step)
#     Row 3: Attack windup / telegraph
#     Row 4: Attack strike
#     Row 5: Hit stagger / Death (cols 0..3 = hit stagger, cols 4..7 = corpse)
# Total sheet size: 512 x 384 pixels.

def draw_8dir_humanoid_frame(draw, ox, oy, dir_idx, row_idx, style):
    """Draws a crisp pixel-art character/creature frame at (ox, oy) in a 64x64 cell."""
    # Determine facing angle: 0=front, 4=back, 2=left, 6=right
    is_back = dir_idx in (3, 4, 5)
    is_front = dir_idx in (7, 0, 1)
    side_shift = 0
    if dir_idx in (1, 2, 3):
        side_shift = -3
    elif dir_idx in (5, 6, 7):
        side_shift = 3

    # Death state (Row 5, cols 4..7)
    if row_idx == 5 and dir_idx >= 4:
        # Lying down on the ground
        body_col = style["body"]
        armor_col = style["armor"]
        draw.rectangle([ox + 12, oy + 50, ox + 52, oy + 58], fill=armor_col, outline=(18, 18, 22, 255))
        draw.ellipse([ox + 8, oy + 48, ox + 20, oy + 59], fill=body_col, outline=(18, 18, 22, 255))
        draw.rectangle([ox + 22, oy + 54, ox + 46, oy + 60], fill=style.get("cloak", armor_col))
        return

    bob = 0
    leg_l_off = 0
    leg_r_off = 0
    arm_r_raise = 0
    if row_idx == 1:
        bob = -1
        leg_l_off = -3
        leg_r_off = 2
    elif row_idx == 2:
        bob = -1
        leg_l_off = 2
        leg_r_off = -3
    elif row_idx == 3:  # Windup telegraph
        arm_r_raise = -10
    elif row_idx == 4:  # Strike
        arm_r_raise = 6
        bob = 2
    elif row_idx == 5:  # Stagger
        bob = 2
        side_shift += 3

    cx = ox + 32 + side_shift
    cy = oy + bob

    kind = style.get("kind", "humanoid")
    outline = (16, 14, 20, 255)

    if kind == "rat":
        # Low-slung monstrous grave rat
        ry = oy + 38 + bob
        # Tail
        tail_x = cx - 16 if dir_idx < 4 else cx + 16
        draw.line([cx, ry + 10, tail_x, ry + 16], fill=(168, 110, 108, 255), width=3)
        # Body
        draw.ellipse([cx - 15, ry, cx + 15, ry + 18], fill=style["body"], outline=outline)
        # Legs / claws
        draw.rectangle([cx - 12, ry + 14 + leg_l_off // 2, cx - 7, oy + 59], fill=style["armor"], outline=outline)
        draw.rectangle([cx + 7, ry + 14 + leg_r_off // 2, cx + 12, oy + 59], fill=style["armor"], outline=outline)
        # Head
        hx = cx + (6 if dir_idx in (5, 6, 7) else (-6 if dir_idx in (1, 2, 3) else 0))
        hy = ry + (2 if is_front else -2) + (arm_r_raise // 3)
        draw.ellipse([hx - 10, hy - 4, hx + 10, hy + 12], fill=style["body"], outline=outline)
        # Ears
        draw.ellipse([hx - 11, hy - 8, hx - 5, hy - 1], fill=(155, 95, 95, 255), outline=outline)
        draw.ellipse([hx + 5, hy - 8, hx + 11, hy - 1], fill=(155, 95, 95, 255), outline=outline)
        if not is_back:
            # Glowing red eyes & fangs
            draw.rectangle([hx - 5, hy + 1, hx - 2, hy + 4], fill=style["eye"])
            draw.rectangle([hx + 2, hy + 1, hx + 5, hy + 4], fill=style["eye"])
            if row_idx in (3, 4):
                draw.rectangle([hx - 4, hy + 7, hx - 2, hy + 12], fill=(240, 235, 210, 255))
                draw.rectangle([hx + 2, hy + 7, hx + 4, hy + 12], fill=(240, 235, 210, 255))
        return

    if kind == "crawler":
        # Chitinous Ash Crawler (multi-legged crypt arthropod)
        ry = oy + 34 + bob
        for i in (-14, -6, 6, 14):
            ly = oy + 58 + ((leg_l_off if i < 0 else leg_r_off) // 2)
            draw.line([cx + i // 2, ry + 8, cx + int(i * 1.4), ry + 12], fill=style["armor"], width=3)
            draw.line([cx + int(i * 1.4), ry + 12, cx + int(i * 1.6), ly], fill=style["body"], width=2)
        # Carapace segments
        draw.ellipse([cx - 16, ry - 4, cx + 16, ry + 16], fill=style["armor"], outline=outline)
        draw.ellipse([cx - 12, ry - 8, cx + 12, ry + 8], fill=style["body"], outline=outline)
        if not is_back:
            for ex in (-6, -2, 2, 6):
                draw.rectangle([cx + ex - 1, ry + 2, cx + ex + 1, ry + 5], fill=style["eye"])
            # Mandibles
            m_open = 4 if row_idx in (3, 4) else 1
            draw.polygon([(cx - 5 - m_open, ry + 14), (cx - 8, ry + 6), (cx - 2, ry + 8)], fill=(220, 195, 160, 255))
            draw.polygon([(cx + 5 + m_open, ry + 14), (cx + 8, ry + 6), (cx + 2, ry + 8)], fill=(220, 195, 160, 255))
        return

    # Humanoid / Skeleton / Boss / NPC
    # Cloak behind if facing front
    if is_front and "cloak" in style:
        draw.polygon([(cx - 14, cy + 20), (cx + 14, cy + 20), (cx + 18, oy + 56), (cx - 18, oy + 56)],
                     fill=style["cloak"], outline=outline)

    # Legs / Boots
    draw.rectangle([cx - 9, oy + 42 + leg_l_off, cx - 2, oy + 59], fill=style["legs"], outline=outline)
    draw.rectangle([cx + 2, oy + 42 + leg_r_off, cx + 9, oy + 59], fill=style["legs"], outline=outline)

    # Torso / Tunic / Ribcage
    draw.rectangle([cx - 11, cy + 20, cx + 11, cy + 43], fill=style["armor"], outline=outline)
    if style.get("ribs", False) and not is_back:
        for ry_rib in (24, 29, 34):
            draw.line([cx - 7, cy + ry_rib, cx + 7, cy + ry_rib], fill=(215, 208, 188, 255), width=2)
    if style.get("trim"):
        draw.rectangle([cx - 3, cy + 20, cx + 3, cy + 43], fill=style["trim"])

    # Cloak over back if facing away
    if is_back and "cloak" in style:
        draw.polygon([(cx - 13, cy + 19), (cx + 13, cy + 19), (cx + 17, oy + 55), (cx - 17, oy + 55)],
                     fill=style["cloak"], outline=outline)

    # Shield / Offhand (left arm)
    arm_lx = cx - 14
    arm_rx = cx + 14
    if dir_idx in (5, 6, 7):
        arm_lx, arm_rx = cx + 10, cx - 10

    draw.rectangle([arm_lx - 3, cy + 22, arm_lx + 3, cy + 38], fill=style["body"], outline=outline)
    if style.get("shield"):
        draw.ellipse([arm_lx - 8, cy + 24, arm_lx + 6, cy + 42], fill=style["shield"], outline=outline)
        draw.ellipse([arm_lx - 3, cy + 30, arm_lx + 1, cy + 36], fill=(200, 175, 95, 255))

    # Weapon / Right arm
    wy = cy + 22 + arm_r_raise
    draw.rectangle([arm_rx - 3, wy, arm_rx + 3, wy + 16], fill=style["body"], outline=outline)
    wep = style.get("weapon")
    if wep == "sword":
        if row_idx == 3:  # Telegraph: raised high with bright glint!
            draw.line([arm_rx + 1, wy - 16, arm_rx + 5, wy + 4], fill=(210, 220, 235, 255), width=3)
            draw.ellipse([arm_rx - 2, wy - 20, arm_rx + 6, wy - 12], fill=(255, 230, 120, 255))
        elif row_idx == 4:  # Slash forward
            draw.line([arm_rx - 14, wy + 12, arm_rx + 14, wy + 16], fill=(225, 235, 248, 255), width=3)
        else:
            draw.line([arm_rx + 2, wy - 10, arm_rx + 2, wy + 10], fill=(185, 195, 210, 255), width=3)
        draw.line([arm_rx - 3, wy + 6, arm_rx + 7, wy + 6], fill=(165, 130, 55, 255), width=2)
    elif wep == "staff":
        draw.line([arm_rx + 2, wy - 14, arm_rx + 2, oy + 58], fill=(110, 75, 42, 255), width=3)
        orb_col = (255, 120, 60, 255) if row_idx in (3, 4) else (110, 220, 255, 255)
        draw.ellipse([arm_rx - 3, wy - 20, arm_rx + 7, wy - 10], fill=orb_col, outline=outline)
    elif wep == "ledger":
        draw.rectangle([arm_rx - 4, wy + 6, arm_rx + 6, wy + 16], fill=(140, 45, 40, 255), outline=outline)
        draw.rectangle([arm_rx - 2, wy + 8, arm_rx + 4, wy + 14], fill=(230, 215, 175, 255))

    # Head / Helmet / Hood
    draw.ellipse([cx - 8, cy + 6, cx + 8, cy + 21], fill=style["body"], outline=outline)
    if style.get("hat") == "hood":
        draw.polygon([(cx - 10, cy + 18), (cx, cy + 3), (cx + 10, cy + 18)], fill=style["cloak"], outline=outline)
        if not is_back:
            draw.ellipse([cx - 6, cy + 9, cx + 6, cy + 20], fill=(28, 24, 34, 255))
    elif style.get("hat") == "cap":
        draw.rectangle([cx - 9, cy + 5, cx + 9, cy + 10], fill=style.get("cloak", (70, 50, 40, 255)), outline=outline)
    elif style.get("hat") == "crown":
        draw.polygon([(cx - 8, cy + 9), (cx - 6, cy + 2), (cx, cy + 7), (cx + 6, cy + 2), (cx + 8, cy + 9)],
                     fill=(215, 178, 68, 255), outline=outline)

    # Eyes (if not facing away)
    if not is_back:
        eye_x_shift = -2 if dir_idx in (1, 2) else (2 if dir_idx in (6, 7) else 0)
        draw.rectangle([cx - 4 + eye_x_shift, cy + 12, cx - 2 + eye_x_shift, cy + 14], fill=style["eye"])
        draw.rectangle([cx + 2 + eye_x_shift, cy + 12, cx + 4 + eye_x_shift, cy + 14], fill=style["eye"])


def save_8dir_sheet(sprite_rel, anim_rel, style):
    img = Image.new("RGBA", (512, 384), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for row in range(6):
        for col in range(8):
            draw_8dir_humanoid_frame(draw, col * 64, row * 64, col, row, style)
    sprite_path = os.path.join(ROOT, sprite_rel)
    ensure_dir(sprite_path)
    img.save(sprite_path)

    anim_data = {
        "schema_version": 1,
        "frame_width": 64,
        "frame_height": 64,
        "directions": 8,
        "pivot": [0.5, 0.92],
        "states": {
            "idle": {"row": 0, "frames": 1, "fps": 2.0, "loop": True},
            "walk": {"rows": [1, 2], "frames": 2, "fps": 6.0, "loop": True},
            "windup": {"row": 3, "frames": 1, "fps": 4.0, "loop": False},
            "attack": {"row": 4, "frames": 1, "fps": 6.0, "loop": False},
            "stagger": {"row": 5, "col_offset": 0, "frames": 1, "fps": 4.0, "loop": False},
            "dead": {"row": 5, "fixed_col": 4, "frames": 1, "fps": 1.0, "loop": False}
        }
    }
    anim_path = os.path.join(ROOT, anim_rel)
    ensure_dir(anim_path)
    with open(anim_path, "w", encoding="utf-8") as f:
        json.dump(anim_data, f, indent=2)


def build_sprites():
    # Enemies
    save_8dir_sheet(
        "assets/sprites/enemies/grave_rat.png",
        "assets/animations/grave_rat.json",
        {"kind": "rat", "body": (92, 74, 66, 255), "armor": (64, 50, 44, 255), "eye": (255, 50, 50, 255)}
    )
    save_8dir_sheet(
        "assets/sprites/enemies/skeleton.png",
        "assets/animations/skeleton.json",
        {
            "kind": "humanoid",
            "body": (215, 206, 186, 255),
            "armor": (58, 54, 66, 255),
            "legs": (175, 166, 148, 255),
            "cloak": (88, 36, 38, 255),
            "eye": (90, 225, 255, 255),
            "ribs": True,
            "shield": (92, 78, 62, 255),
            "weapon": "sword"
        }
    )
    save_8dir_sheet(
        "assets/sprites/enemies/ash_crawler.png",
        "assets/animations/ash_crawler.json",
        {"kind": "crawler", "body": (74, 82, 92, 255), "armor": (46, 52, 64, 255), "eye": (255, 165, 45, 255)}
    )
    save_8dir_sheet(
        "assets/sprites/enemies/crypt_keeper.png",
        "assets/animations/crypt_keeper.json",
        {
            "kind": "humanoid",
            "body": (165, 210, 225, 255),
            "armor": (42, 32, 68, 255),
            "legs": (32, 24, 52, 255),
            "cloak": (68, 42, 98, 255),
            "trim": (210, 175, 75, 255),
            "eye": (120, 245, 255, 255),
            "hat": "crown",
            "weapon": "staff"
        }
    )

    # Example Mod variant sprite (Crimson Revenant Skeleton)
    save_8dir_sheet(
        "mods/example_mod/assets/sprites/enemies/crimson_skeleton.png",
        "assets/animations/skeleton.json",
        {
            "kind": "humanoid",
            "body": (235, 190, 180, 255),
            "armor": (135, 28, 32, 255),
            "legs": (195, 150, 140, 255),
            "cloak": (180, 35, 40, 255),
            "eye": (255, 220, 60, 255),
            "ribs": True,
            "shield": (140, 40, 40, 255),
            "weapon": "sword"
        }
    )

    # NPCs
    save_8dir_sheet(
        "assets/sprites/npcs/clerk_oakhaven.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (218, 182, 152, 255),
            "armor": (48, 62, 88, 255),
            "legs": (38, 42, 54, 255),
            "cloak": (36, 48, 68, 255),
            "trim": (192, 158, 72, 255),
            "eye": (40, 50, 70, 255),
            "hat": "cap",
            "weapon": "ledger"
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/merchant_vaelen.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (210, 185, 160, 255),
            "armor": (118, 74, 42, 255),
            "legs": (68, 52, 38, 255),
            "cloak": (48, 92, 58, 255),
            "trim": (210, 175, 70, 255),
            "eye": (40, 80, 50, 255),
            "hat": "cap"
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/innkeeper_marta.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (224, 186, 158, 255),
            "armor": (136, 58, 48, 255),
            "legs": (78, 54, 46, 255),
            "trim": (228, 218, 198, 255),
            "eye": (60, 42, 32, 255)
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/librarian_fenwick.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (195, 165, 142, 255),
            "armor": (78, 56, 92, 255),
            "legs": (52, 42, 62, 255),
            "cloak": (62, 44, 76, 255),
            "eye": (50, 50, 70, 255),
            "weapon": "ledger"
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/brother_aldous.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (212, 178, 148, 255),
            "armor": (210, 198, 172, 255),
            "legs": (140, 128, 108, 255),
            "cloak": (185, 145, 65, 255),
            "trim": (225, 185, 75, 255),
            "eye": (60, 50, 40, 255),
            "hat": "hood",
            "weapon": "staff"
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/ashbound_scout.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (142, 168, 132, 255),  # Orcish Ashbound chronicler/scout
            "armor": (64, 78, 58, 255),
            "legs": (48, 56, 44, 255),
            "cloak": (54, 66, 48, 255),
            "eye": (210, 160, 50, 255),
            "hat": "hood",
            "weapon": "sword"
        }
    )
    save_8dir_sheet(
        "assets/sprites/npcs/erased_spirit.png",
        "assets/animations/npc_standard.json",
        {
            "kind": "humanoid",
            "body": (135, 215, 235, 195),
            "armor": (85, 165, 195, 185),
            "legs": (65, 135, 165, 165),
            "cloak": (95, 185, 215, 175),
            "eye": (220, 255, 255, 255),
            "hat": "hood"
        }
    )

    # VFX Billboards (4 frames horizontal, 32x32 each = 128x32)
    vfx_dir = os.path.join(ROOT, "assets", "sprites", "vfx")
    os.makedirs(vfx_dir, exist_ok=True)

    # torch_flame.png
    img = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for f in range(4):
        ox = f * 32
        shift = (-1 if f % 2 == 0 else 1)
        draw.ellipse([ox + 9, 10, ox + 23, 28], fill=(255, 110, 25, 220))
        draw.polygon([(ox + 16 + shift, 3 + (f % 3)), (ox + 23, 18), (ox + 9, 18)], fill=(255, 185, 45, 240))
        draw.ellipse([ox + 12, 14, ox + 20, 25], fill=(255, 245, 160, 255))
    img.save(os.path.join(vfx_dir, "torch_flame.png"))

    # spell_ember.png
    img = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for f in range(4):
        ox = f * 32
        r = 10 + (f % 2) * 2
        draw.ellipse([ox + 16 - r, 16 - r, ox + 16 + r, 16 + r], fill=(255, 90, 20, 230))
        draw.ellipse([ox + 11, 11, ox + 21, 21], fill=(255, 230, 110, 255))
    img.save(os.path.join(vfx_dir, "spell_ember.png"))

    # spell_arcane.png
    img = Image.new("RGBA", (128, 32), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    for f in range(4):
        ox = f * 32
        r = 10 + (f % 2) * 2
        draw.ellipse([ox + 16 - r, 16 - r, ox + 16 + r, 16 + r], fill=(70, 195, 255, 230))
        draw.ellipse([ox + 11, 11, ox + 21, 21], fill=(215, 250, 255, 255))
    img.save(os.path.join(vfx_dir, "spell_arcane.png"))


# =============================================================================
# 3. UI ICONS, PORTRAITS, AND HUD PANELS (PNGs)
# =============================================================================
def draw_icon_bg(size=32, border=(110, 92, 64, 255), fill=(26, 22, 30, 240)):
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, size - 1, size - 1], fill=fill, outline=border)
    draw.rectangle([1, 1, size - 2, size - 2], outline=(48, 40, 32, 255))
    return img, draw


def build_ui_icons():
    items_dir = os.path.join(ROOT, "assets", "ui", "items")
    spells_dir = os.path.join(ROOT, "assets", "ui", "spells")
    portraits_dir = os.path.join(ROOT, "assets", "ui", "portraits")
    panels_dir = os.path.join(ROOT, "assets", "ui", "panels")

    # Weapons
    weapon_specs = {
        "rusted_sword.png": ((155, 138, 128, 255), (125, 82, 48, 255), "sword"),
        "iron_longsword.png": ((205, 215, 228, 255), (185, 152, 68, 255), "sword"),
        "widowmaker.png": ((135, 225, 255, 255), (225, 175, 65, 255), "greatsword"),
        "steel_dagger.png": ((195, 205, 218, 255), (110, 80, 55, 255), "dagger"),
        "iron_mace.png": ((168, 175, 188, 255), (120, 85, 50, 255), "mace"),
        "oak_staff.png": ((138, 92, 52, 255), (95, 215, 255, 255), "staff"),
        "hunting_bow.png": ((148, 96, 52, 255), (220, 215, 195, 255), "bow"),
        "wooden_arrow.png": ((158, 112, 64, 255), (195, 205, 215, 255), "arrow"),
    }
    for fname, (c1, c2, kind) in weapon_specs.items():
        img, d = draw_icon_bg()
        if kind in ("sword", "greatsword", "dagger"):
            length = 22 if kind != "dagger" else 14
            d.line([8, 24, 8 + length - 4, 24 - length + 4], fill=c1, width=3 if kind == "greatsword" else 2)
            d.line([6, 20, 12, 26], fill=c2, width=2)
            d.rectangle([5, 24, 8, 27], fill=c2)
        elif kind == "mace":
            d.line([7, 25, 22, 10], fill=c2, width=2)
            d.ellipse([17, 5, 27, 15], fill=c1, outline=(40, 40, 50, 255))
        elif kind == "staff":
            d.line([7, 26, 24, 9], fill=c1, width=3)
            d.ellipse([20, 4, 28, 12], fill=c2)
        elif kind == "bow":
            d.arc([6, 4, 26, 28], start=290, end=70, fill=c1, width=2)
            d.line([14, 5, 14, 27], fill=c2, width=1)
        elif kind == "arrow":
            d.line([6, 25, 25, 6], fill=c1, width=2)
            d.polygon([(26, 5), (20, 6), (25, 11)], fill=c2)
        img.save(os.path.join(items_dir, fname))

    # Example mod weapon icon
    img, d = draw_icon_bg(border=(205, 75, 75, 255))
    d.line([7, 25, 25, 7], fill=(255, 95, 75, 255), width=3)
    d.line([6, 19, 13, 26], fill=(225, 185, 70, 255), width=2)
    img.save(os.path.join(ROOT, "mods", "example_mod", "assets", "ui", "items", "ashbrand_blade.png"))

    # Armor, Shields, Consumables, Quest items, Books
    misc_icons = {
        "iron_shield.png": ("shield", (155, 165, 180, 255), (205, 168, 72, 255)),
        "leather_jerkin.png": ("armor", (132, 84, 48, 255), (92, 58, 34, 255)),
        "chain_hauberk.png": ("armor", (165, 175, 190, 255), (110, 120, 135, 255)),
        "scholar_robe.png": ("armor", (62, 82, 138, 255), (205, 172, 72, 255)),
        "iron_helm.png": ("helm", (162, 172, 186, 255), (90, 95, 105, 255)),
        "traveler_boots.png": ("boots", (118, 76, 44, 255), (82, 52, 30, 255)),
        "ring_of_recall.png": ("ring", (215, 178, 68, 255), (95, 215, 255, 255)),
        "health_potion.png": ("potion", (215, 48, 52, 255), (235, 215, 185, 255)),
        "mana_potion.png": ("potion", (52, 128, 225, 255), (235, 215, 185, 255)),
        "stamina_tonic.png": ("potion", (62, 185, 82, 255), (235, 215, 185, 255)),
        "bread_loaf.png": ("bread", (195, 142, 72, 255), (145, 98, 44, 255)),
        "lockpick.png": ("key", (185, 192, 205, 255), (120, 125, 135, 255)),
        "annex_key.png": ("key", (215, 178, 72, 255), (165, 132, 48, 255)),
        "crypt_key.png": ("key", (125, 215, 235, 255), (75, 145, 165, 255)),
        "death_notice.png": ("scroll", (225, 208, 172, 255), (165, 38, 38, 255)),
        "form_27b.png": ("scroll", (228, 215, 182, 255), (52, 95, 165, 255)),
        "uncounted_ledger.png": ("book", (138, 38, 42, 255), (110, 225, 255, 255)),
        "tome_ember.png": ("book", (168, 58, 32, 255), (255, 185, 65, 255)),
        "tome_mend.png": ("book", (48, 128, 78, 255), (215, 235, 145, 255)),
        "tome_ward.png": ("book", (58, 92, 158, 255), (195, 215, 245, 255)),
        "tome_glimmer.png": ("book", (175, 152, 58, 255), (255, 245, 175, 255)),
        "tome_veil.png": ("book", (82, 52, 118, 255), (185, 145, 235, 255)),
        "signet_ring.png": ("ring", (212, 172, 65, 255), (175, 42, 42, 255)),
        "gold_coins.png": ("ring", (235, 195, 65, 255), (185, 142, 38, 255)),
    }
    for fname, (shape, c1, c2) in misc_icons.items():
        img, d = draw_icon_bg()
        if shape == "shield":
            d.polygon([(8, 6), (24, 6), (24, 17), (16, 27), (8, 17)], fill=c1, outline=c2)
        elif shape == "armor":
            d.polygon([(9, 7), (23, 7), (26, 13), (22, 15), (22, 26), (10, 26), (10, 15), (6, 13)], fill=c1, outline=c2)
        elif shape == "helm":
            d.chord([8, 6, 24, 24], start=180, end=360, fill=c1, outline=c2)
            d.rectangle([9, 15, 23, 24], fill=c1, outline=c2)
            d.rectangle([13, 17, 19, 23], fill=(25, 25, 30, 255))
        elif shape == "boots":
            d.polygon([(11, 7), (18, 7), (18, 19), (24, 21), (24, 25), (10, 25)], fill=c1, outline=c2)
        elif shape == "ring":
            d.ellipse([9, 9, 23, 23], outline=c1, width=3)
            d.ellipse([13, 6, 19, 12], fill=c2)
        elif shape == "potion":
            d.rectangle([13, 5, 19, 10], fill=c2)
            d.ellipse([8, 10, 24, 26], fill=c1, outline=(230, 235, 245, 255))
        elif shape == "bread":
            d.ellipse([6, 11, 26, 24], fill=c1, outline=c2)
        elif shape == "key":
            d.ellipse([7, 11, 15, 19], outline=c1, width=2)
            d.line([15, 15, 25, 15], fill=c1, width=2)
            d.line([21, 15, 21, 20], fill=c1, width=2)
            d.line([24, 15, 24, 19], fill=c1, width=2)
        elif shape == "scroll":
            d.rectangle([8, 6, 24, 26], fill=c1, outline=(120, 95, 65, 255))
            d.ellipse([14, 18, 20, 24], fill=c2)
        elif shape == "book":
            d.rectangle([7, 5, 25, 26], fill=c1, outline=(35, 25, 25, 255))
            d.rectangle([10, 8, 22, 23], outline=c2, width=1)
        img.save(os.path.join(items_dir, fname))

    # Spells
    spell_icons = {
        "ember_bolt.png": ((255, 95, 25, 255), (255, 225, 95, 255)),
        "mend.png": ((55, 205, 110, 255), (210, 255, 220, 255)),
        "ward.png": ((65, 145, 245, 255), (195, 230, 255, 255)),
        "glimmer.png": ((255, 225, 95, 255), (255, 252, 215, 255)),
        "veil.png": ((145, 85, 225, 255), (215, 185, 255, 255)),
    }
    for fname, (c1, c2) in spell_icons.items():
        img, d = draw_icon_bg(border=c1)
        d.ellipse([6, 6, 26, 26], fill=c1)
        d.ellipse([11, 11, 21, 21], fill=c2)
        img.save(os.path.join(spells_dir, fname))

    # Race Portraits (64x64)
    races = {
        "human.png": ((215, 178, 148, 255), (92, 64, 44, 255), (58, 82, 118, 255), False),
        "dwarf.png": ((208, 168, 138, 255), (158, 78, 38, 255), (118, 92, 58, 255), True),
        "elf.png": ((225, 202, 178, 255), (218, 205, 142, 255), (48, 102, 78, 255), False),
        "orc.png": ((132, 162, 118, 255), (42, 38, 36, 255), (112, 48, 42, 255), False),
        "halfling.png": ((218, 182, 152, 255), (128, 86, 48, 255), (82, 112, 58, 255), False),
    }
    for fname, (skin, hair, tunic, beard) in races.items():
        img = Image.new("RGBA", (64, 64), (24, 20, 28, 255))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 63, 63], outline=(138, 112, 72, 255), width=2)
        d.polygon([(12, 62), (52, 62), (46, 42), (18, 42)], fill=tunic)
        d.ellipse([18, 14, 46, 44], fill=skin, outline=(25, 20, 20, 255))
        d.chord([17, 11, 47, 32], start=180, end=360, fill=hair)
        if beard:
            d.polygon([(20, 32), (44, 32), (38, 52), (26, 52)], fill=hair)
        d.rectangle([25, 26, 28, 29], fill=(30, 35, 45, 255))
        d.rectangle([36, 26, 39, 29], fill=(30, 35, 45, 255))
        img.save(os.path.join(portraits_dir, fname))

    # Crosshair & Panel Frame
    cross = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cross)
    cd.rectangle([7, 3, 8, 6], fill=(235, 225, 195, 220))
    cd.rectangle([7, 9, 8, 12], fill=(235, 225, 195, 220))
    cd.rectangle([3, 7, 6, 8], fill=(235, 225, 195, 220))
    cd.rectangle([9, 7, 12, 8], fill=(235, 225, 195, 220))
    cross.save(os.path.join(panels_dir, "crosshair.png"))

    # Default title_bg.png (will be upgraded if title_bg_raw.png from image-generator finishes)
    title_path = os.path.join(panels_dir, "title_bg.png")
    if not os.path.exists(title_path):
        timg = Image.new("RGBA", (320, 180), (14, 16, 26, 255))
        td = ImageDraw.Draw(timg)
        for y in range(180):
            c = clamp(14 + y // 6)
            td.line([0, y, 320, y], fill=(c, c + 4, c + 16, 255))
        # Distant Bellwether silhouettes & lantern glow
        td.polygon([(20, 130), (55, 95), (90, 130)], fill=(22, 24, 36, 255))
        td.rectangle([30, 130, 80, 165], fill=(26, 28, 40, 255))
        td.rectangle([48, 140, 58, 152], fill=(245, 175, 65, 255))
        # Crypt archway
        td.ellipse([180, 70, 290, 180], fill=(38, 42, 54, 255))
        td.ellipse([196, 86, 274, 180], fill=(12, 18, 28, 255))
        td.ellipse([226, 118, 244, 136], fill=(95, 215, 255, 180))
        timg.save(title_path)


# =============================================================================
# 4. COPY REPLACEABLE EXTERNAL FONTS (.TTF)
# =============================================================================
def build_fonts():
    font_dir = os.path.join(ROOT, "assets", "fonts")
    os.makedirs(font_dir, exist_ok=True)
    win_fonts = "C:\\Windows\\Fonts"
    serif_candidates = ["georgia.ttf", "times.ttf", "palabi.ttf", "arial.ttf"]
    mono_candidates = ["consola.ttf", "cour.ttf", "lucon.ttf", "arial.ttf"]

    for cand in serif_candidates:
        src = os.path.join(win_fonts, cand)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(font_dir, "uncounted_serif.ttf"))
            break

    for cand in mono_candidates:
        src = os.path.join(win_fonts, cand)
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(font_dir, "uncounted_mono.ttf"))
            break


if __name__ == "__main__":
    build_textures()
    build_sprites()
    build_ui_icons()
    build_fonts()
    print("External pixel-art textures, 8-dir sprites, UI icons, and TTF fonts generated.")

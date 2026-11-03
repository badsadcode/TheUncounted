#!/usr/bin/env python3
"""
Offline builder for small item models (bread, garments, boots, helm, rings) as self-contained .glb files.

Meshes are low-poly and flat-shaded with baked per-face vertex colours (COLOR_0, u8), so they need no
textures and match the pixel-art look. Every model is authored with its base at y=0 and centred on X/Z.

Run:  python tools/build_item_models.py
"""

import json
import math
import os
import random
import struct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "models", "items")


class Mesh:
    def __init__(self, seed=1):
        self.pos, self.nrm, self.col = [], [], []
        self.rng = random.Random(seed)

    # --- core: append one flat-shaded triangle
    def tri(self, a, b, c, color):
        color = tuple(int(x) for x in color[:3]) + (255,)
        ux, uy, uz = b[0] - a[0], b[1] - a[1], b[2] - a[2]
        vx, vy, vz = c[0] - a[0], c[1] - a[1], c[2] - a[2]
        n = (uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx)
        ln = math.sqrt(n[0] ** 2 + n[1] ** 2 + n[2] ** 2) or 1.0
        n = (n[0] / ln, n[1] / ln, n[2] / ln)
        # Emit both windings (with opposite normals) so face orientation never matters under culling.
        for p in (a, b, c):
            self.pos.append(p)
            self.nrm.append(n)
            self.col.append(color)
        for p in (a, c, b):
            self.pos.append(p)
            self.nrm.append((-n[0], -n[1], -n[2]))
            self.col.append(color)

    def quad(self, a, b, c, d, color):
        k = 0.9 + self.rng.random() * 0.18  # per-face grain reads like hand-painted texels
        col = tuple(max(0, min(255, int(x * k))) for x in color[:3]) + (255,)
        self.tri(a, b, c, col)
        self.tri(a, c, d, col)

    # --- primitives
    def box(self, c, s, color, rot_y=0.0, rot_x=0.0, rot_z=0.0):
        hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
        corners = [(x, y, z) for x in (-hx, hx) for y in (-hy, hy) for z in (-hz, hz)]

        def tf(p):
            x, y, z = p
            cz, sz = math.cos(rot_z), math.sin(rot_z)
            x, y = x * cz - y * sz, x * sz + y * cz
            cx, sx = math.cos(rot_x), math.sin(rot_x)
            y, z = y * cx - z * sx, y * sx + z * cx
            cy, sy = math.cos(rot_y), math.sin(rot_y)
            x, z = x * cy + z * sy, -x * sy + z * cy
            return (x + c[0], y + c[1], z + c[2])

        v = [tf(p) for p in corners]
        # index = xi*4 + yi*2 + zi
        faces = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
        for f in faces:
            self.quad(v[f[0]], v[f[1]], v[f[2]], v[f[3]], color)

    def ellipsoid(self, c, r, color, seg=8, rings=6, y_min=-1.0, color_fn=None):
        def p(i, j):
            th = math.pi * j / rings - math.pi / 2
            th = max(th, math.asin(y_min))
            ph = 2 * math.pi * i / seg
            return (c[0] + r[0] * math.cos(th) * math.cos(ph), c[1] + r[1] * math.sin(th), c[2] + r[2] * math.cos(th) * math.sin(ph))

        for j in range(rings):
            for i in range(seg):
                a, b, cc, d = p(i, j), p(i + 1, j), p(i + 1, j + 1), p(i, j + 1)
                col = color_fn(i, j) if color_fn else color
                self.quad(a, d, cc, b, col)
        if y_min > -1.0:  # cap the flat bottom
            ring = [p(i, 0) for i in range(seg)]
            center = (c[0], ring[0][1], c[2])
            for i in range(seg):
                self.tri(center, ring[i], ring[(i + 1) % seg], tuple(int(x * 0.7) for x in color[:3]) + (255,))

    def cylinder(self, c, r, h, color, seg=10, r_top=None):
        rt = r if r_top is None else r_top
        for i in range(seg):
            a0, a1 = 2 * math.pi * i / seg, 2 * math.pi * (i + 1) / seg
            b0 = (c[0] + r * math.cos(a0), c[1], c[2] + r * math.sin(a0))
            b1 = (c[0] + r * math.cos(a1), c[1], c[2] + r * math.sin(a1))
            t0 = (c[0] + rt * math.cos(a0), c[1] + h, c[2] + rt * math.sin(a0))
            t1 = (c[0] + rt * math.cos(a1), c[1] + h, c[2] + rt * math.sin(a1))
            self.quad(b0, t0, t1, b1, color)
            top = tuple(min(255, int(x * 1.1)) for x in color[:3]) + (255,)
            self.tri((c[0], c[1] + h, c[2]), t1, t0, top)
            self.tri((c[0], c[1], c[2]), b0, b1, color)

    def torus(self, c, R, r, color, seg=14, sides=6, axis="z"):
        def p(i, j):
            u = 2 * math.pi * i / seg
            v = 2 * math.pi * j / sides
            x = (R + r * math.cos(v)) * math.cos(u)
            y = (R + r * math.cos(v)) * math.sin(u)
            z = r * math.sin(v)
            if axis == "y":
                x, y, z = x, z, y
            return (c[0] + x, c[1] + y, c[2] + z)

        for i in range(seg):
            for j in range(sides):
                self.quad(p(i, j), p(i + 1, j), p(i + 1, j + 1), p(i, j + 1), color)

    # --- export
    def write_glb(self, rel_name):
        n = len(self.pos)
        # Ground the model: base at y=0, centred on X/Z.
        xs = [p[0] for p in self.pos]
        ys = [p[1] for p in self.pos]
        zs = [p[2] for p in self.pos]
        ox, oy, oz = (min(xs) + max(xs)) / 2, min(ys), (min(zs) + max(zs)) / 2
        pos = [(p[0] - ox, p[1] - oy, p[2] - oz) for p in self.pos]

        pos_b = b"".join(struct.pack("<3f", *p) for p in pos)
        nrm_b = b"".join(struct.pack("<3f", *v) for v in self.nrm)
        uv_b = b"".join(struct.pack("<2f", 0.5, 0.5) for _ in range(n))
        col_b = b"".join(struct.pack("<4B", *c) for c in self.col)
        chunks = [pos_b, nrm_b, uv_b, col_b]
        offsets, blob = [], b""
        for c in chunks:
            offsets.append(len(blob))
            blob += c
            blob += b"\x00" * ((4 - len(blob) % 4) % 4)

        mn = [min(p[k] for p in pos) for k in range(3)]
        mx = [max(p[k] for p in pos) for k in range(3)]
        gltf = {
            "asset": {"version": "2.0", "generator": "uncounted build_item_models.py"},
            "scene": 0,
            "scenes": [{"nodes": [0]}],
            "nodes": [{"mesh": 0, "name": os.path.splitext(rel_name)[0]}],
            "materials": [{"name": "VertexColour", "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1], "metallicFactor": 0.0, "roughnessFactor": 0.9}}],
            "meshes": [{"primitives": [{"attributes": {"POSITION": 0, "NORMAL": 1, "TEXCOORD_0": 2, "COLOR_0": 3}, "material": 0, "mode": 4}]}],
            "buffers": [{"byteLength": len(blob)}],
            "bufferViews": [
                {"buffer": 0, "byteOffset": offsets[0], "byteLength": len(pos_b), "target": 34962},
                {"buffer": 0, "byteOffset": offsets[1], "byteLength": len(nrm_b), "target": 34962},
                {"buffer": 0, "byteOffset": offsets[2], "byteLength": len(uv_b), "target": 34962},
                {"buffer": 0, "byteOffset": offsets[3], "byteLength": len(col_b), "target": 34962},
            ],
            "accessors": [
                {"bufferView": 0, "componentType": 5126, "count": n, "type": "VEC3", "min": mn, "max": mx},
                {"bufferView": 1, "componentType": 5126, "count": n, "type": "VEC3"},
                {"bufferView": 2, "componentType": 5126, "count": n, "type": "VEC2"},
                {"bufferView": 3, "componentType": 5121, "normalized": True, "count": n, "type": "VEC4"},
            ],
        }
        js = json.dumps(gltf, separators=(",", ":")).encode()
        js += b" " * ((4 - len(js) % 4) % 4)
        total = 12 + 8 + len(js) + 8 + len(blob)
        data = struct.pack("<4sII", b"glTF", 2, total)
        data += struct.pack("<I4s", len(js), b"JSON") + js
        data += struct.pack("<I4s", len(blob), b"BIN\x00") + blob
        path = os.path.join(OUT, rel_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        print("Wrote", os.path.relpath(path, ROOT), "(%d tris)" % (n // 3))


def bread():
    m = Mesh(3)
    crust, dark = (196, 132, 62), (140, 86, 38)
    m.ellipsoid((0, 0, 0), (0.09, 0.075, 0.16), crust, seg=10, rings=6, y_min=-0.15)
    for k in (-0.07, 0.0, 0.07):
        m.box((0, 0.068, k), (0.11, 0.012, 0.02), dark, rot_y=0.5)
    m.write_glb("bread_loaf.glb")


def garment(name, body, trim, chain=False, robe=False):
    m = Mesh(len(name))
    length = 0.62 if robe else 0.42
    if chain:
        # mail rings as alternating light/dark bands
        for i in range(8):
            y = i * length / 8
            col = body if i % 2 == 0 else tuple(int(c * 0.78) for c in body)
            m.box((0, y + length / 16, 0), (0.36 + (0.04 if robe else 0), length / 8 + 0.002, 0.13), col)
    else:
        m.box((0, length / 2, 0), (0.36 if not robe else 0.42, length, 0.13), body)
    top = length
    m.box((0, top - 0.03, 0), (0.46, 0.08, 0.14), body)  # shoulders
    for sx in (-1, 1):
        m.box((sx * 0.27, top - 0.14, 0), (0.09, 0.24, 0.1), body, rot_z=sx * 0.35)  # sleeves
        m.box((sx * 0.31, top - 0.27, 0), (0.1, 0.04, 0.11), trim, rot_z=sx * 0.35)  # cuffs
    m.box((0, top + 0.01, 0.0), (0.14, 0.04, 0.15), trim)  # collar
    m.box((0, length * 0.42, 0.0), (0.38 if not robe else 0.44, 0.04, 0.145), trim)  # belt
    if not chain:
        m.box((0, length * 0.42, 0.075), (0.05, 0.05, 0.02), (214, 180, 80))  # buckle
    m.write_glb(name + ".glb")


def boots():
    m = Mesh(7)
    leather, sole = (106, 70, 40), (52, 36, 24)
    for sx in (-1, 1):
        x = sx * 0.07
        m.box((x, 0.012, 0.03), (0.08, 0.024, 0.2), sole)
        m.box((x, 0.05, 0.035), (0.075, 0.06, 0.18), leather)
        m.box((x, 0.14, -0.02), (0.08, 0.2, 0.08), leather)
        m.box((x, 0.235, -0.02), (0.09, 0.03, 0.09), (140, 98, 58))
    m.write_glb("traveler_boots.glb")


def helm():
    m = Mesh(11)
    iron, dark = (150, 158, 170), (96, 100, 112)
    m.ellipsoid((0, 0.0, 0), (0.12, 0.13, 0.13), iron, seg=10, rings=5, y_min=0.0)
    m.cylinder((0, 0.0, 0), 0.125, 0.03, dark, seg=12)
    m.box((0, -0.035, 0.125), (0.025, 0.1, 0.02), dark)  # nasal guard
    m.box((0, 0.115, 0), (0.025, 0.03, 0.22), dark)  # crest
    m.write_glb("iron_helm.glb")


def ring(name, metal, gem):
    m = Mesh(len(name) * 3)
    m.torus((0, 0.06, 0), 0.05, 0.013, metal, axis="z")
    m.ellipsoid((0, 0.122, 0), (0.024, 0.02, 0.024), gem, seg=6, rings=4)
    m.box((0, 0.105, 0), (0.04, 0.012, 0.03), metal)
    m.write_glb(name + ".glb")


def seal_quill():
    """Raven quill with a black-iron nib (reward for signing the Seal of Names) + its 32x32 inventory icon."""
    m = Mesh(21)
    raven, sheen, iron = (34, 36, 48), (60, 74, 110), (70, 72, 80)
    m.cylinder((0, 0.0, 0), 0.001, 0.07, iron, seg=6, r_top=0.009)        # nib
    m.cylinder((0, 0.07, 0), 0.007, 0.36, (200, 190, 170), seg=6)        # shaft
    m.ellipsoid((0.018, 0.27, 0), (0.04, 0.16, 0.008), raven, seg=8, rings=6,
                color_fn=lambda i, j: sheen if (i + j) % 3 == 0 else raven)
    m.write_glb("seal_quill.glb")

    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (32, 32), (26, 22, 30, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], outline=(110, 92, 64, 255))
    d.rectangle([1, 1, 30, 30], outline=(48, 40, 32, 255))
    for k in range(17):  # feather vane along the diagonal, wider in the middle
        x, y = 22 - k, 6 + k
        w = 3 if 3 < k < 13 else (2 if k > 1 else 1)
        for t in range(-w, w + 1):
            col = (92, 112, 160, 255) if (k + t) % 4 == 0 else (58, 62, 84, 255)
            for dx in (0, 1):  # offsets run across the shaft so the vane frames it
                img.putpixel((min(30, max(1, x + t + dx)), min(30, max(1, y + t))), col)
    d.line([(24, 4), (8, 20)], fill=(210, 200, 180, 255))      # shaft
    d.line([(8, 20), (5, 25)], fill=(150, 154, 166, 255))      # iron nib
    img.putpixel((5, 26), (20, 20, 30, 255))
    d.ellipse([3, 26, 7, 29], fill=(14, 16, 30, 255))          # ink drop
    path = os.path.join(ROOT, "assets", "ui", "items", "seal_quill.png")
    img.save(path)
    print("Wrote", os.path.relpath(path, ROOT))


def icon_canvas():
    from PIL import Image, ImageDraw
    img = Image.new("RGBA", (32, 32), (26, 22, 30, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 31, 31], outline=(110, 92, 64, 255))
    d.rectangle([1, 1, 30, 30], outline=(48, 40, 32, 255))
    return img, d


def save_icon(img, name):
    path = os.path.join(ROOT, "assets", "ui", "items", name + ".png")
    img.save(path)
    print("Wrote", os.path.relpath(path, ROOT))


def baggy_umbrella():
    """A detective's furled black umbrella with a hooked cane handle. Grip (handle) at the bottom, tip up, like the swords."""
    m = Mesh(31)
    cloth, cloth2, wood, brass = (34, 34, 40), (52, 50, 60), (110, 70, 40), (205, 170, 80)
    m.box((0.035, 0.03, 0), (0.07, 0.025, 0.025), wood)                 # hook, bottom
    m.box((0.065, 0.06, 0), (0.025, 0.06, 0.025), wood)
    m.cylinder((0, 0.0, 0), 0.013, 0.2, wood, seg=8)                      # handle shaft
    m.cylinder((0, 0.2, 0), 0.016, 0.02, brass, seg=8)                    # ferrule
    m.cylinder((0, 0.22, 0), 0.03, 0.12, cloth2, seg=10, r_top=0.045)     # furled canopy swelling...
    m.cylinder((0, 0.34, 0), 0.045, 0.38, cloth, seg=10, r_top=0.008)     # ...and tapering to the tip
    m.box((0, 0.42, 0.04), (0.012, 0.04, 0.012), brass)                   # strap button
    m.cylinder((0, 0.72, 0), 0.006, 0.07, brass, seg=6, r_top=0.002)      # tip
    m.write_glb("baggy_umbrella.glb")
    img, d = icon_canvas()
    d.line([(25, 5), (11, 23)], fill=(30, 30, 38, 255), width=4)          # canopy
    d.line([(24, 6), (12, 21)], fill=(70, 68, 84, 255), width=1)
    d.line([(26, 4), (28, 2)], fill=(205, 170, 80, 255))                  # tip
    d.line([(11, 23), (8, 27)], fill=(120, 78, 44, 255), width=2)         # handle
    d.arc([3, 24, 9, 30], 0, 200, fill=(120, 78, 44, 255), width=2)       # hook
    save_icon(img, "baggy_umbrella")


def sabrino_hat():
    """A tall, dented, pointed witch's hat with a faded sash. Base at y=0."""
    m = Mesh(37)
    felt, felt2, sash, buckle = (60, 30, 66), (78, 42, 86), (150, 36, 40), (214, 180, 80)
    m.cylinder((0, 0.0, 0), 0.2, 0.015, felt2, seg=14)                    # brim
    m.cylinder((0, 0.015, 0), 0.105, 0.05, sash, seg=12, r_top=0.1)       # sash band
    m.box((0, 0.04, 0.1), (0.04, 0.035, 0.012), buckle)
    m.cylinder((0, 0.065, 0), 0.1, 0.17, felt, seg=12, r_top=0.055)       # crown
    m.cylinder((0.02, 0.235, 0), 0.055, 0.12, felt2, seg=10, r_top=0.004) # bent tip
    m.write_glb("sabrino_hat.glb")
    img, d = icon_canvas()
    d.polygon([(16, 3), (10, 22), (22, 22)], fill=(70, 36, 78, 255))
    d.polygon([(16, 3), (21, 7), (17, 9)], fill=(90, 50, 100, 255))       # dented tip
    d.rectangle([10, 19, 22, 22], fill=(150, 36, 40, 255))                # sash
    d.rectangle([15, 19, 17, 22], fill=(214, 180, 80, 255))
    d.ellipse([3, 21, 29, 27], fill=(84, 46, 92, 255))                    # brim
    d.line([(6, 24), (26, 24)], fill=(60, 30, 66, 255))
    save_icon(img, "sabrino_hat")


def tinted(src, dst, rgb_mul, folder="items"):
    """Recolour an existing icon/sprite (keeps the pixel art, shifts its palette)."""
    from PIL import Image
    img = Image.open(os.path.join(ROOT, src)).convert("RGBA")
    px = img.load()
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            r, g, b, a = px[x, y]
            lum = (r + g + b) / 3.0
            mixed = [min(255, int(lum * k[0] + c * k[1])) for c, k in zip((r, g, b), rgb_mul)]
            px[x, y] = (mixed[0], mixed[1], mixed[2], a)
    img.save(os.path.join(ROOT, dst))
    print("Wrote", dst)


def build_extra_icons():
    # (luminance weight, original-channel weight) per channel
    frost = ((0.55, 0.0), (0.95, 0.0), (1.35, 0.0))
    ink = ((0.75, 0.1), (1.25, 0.0), (0.55, 0.0))
    sabrino = ((1.5, 0.2), (0.55, 0.1), (0.35, 0.0))
    letter = ((1.1, 0.1), (0.95, 0.1), (0.6, 0.1))
    tinted("assets/ui/items/tome_ember.png", "assets/ui/items/tome_frost.png", frost)
    tinted("assets/ui/items/tome_mend.png", "assets/ui/items/tome_siphon.png", ink)
    tinted("assets/ui/items/tome_ember.png", "assets/ui/items/tome_sabrino.png", sabrino)
    tinted("assets/ui/items/steel_dagger.png", "assets/ui/items/letter_opener.png", letter)
    tinted("assets/ui/spells/ember_bolt.png", "assets/ui/spells/frost_lance.png", frost)
    tinted("assets/ui/spells/mend.png", "assets/ui/spells/siphon_ink.png", ink)
    tinted("assets/ui/spells/ember_bolt.png", "assets/ui/spells/sabrino_fireball.png", sabrino)
    tinted("assets/sprites/vfx/spell_ember.png", "assets/sprites/vfx/spell_frost.png", frost)
    tinted("assets/sprites/vfx/spell_arcane.png", "assets/sprites/vfx/spell_ink.png", ink)
    tinted("assets/sprites/vfx/spell_ember.png", "assets/sprites/vfx/spell_sabrino.png", sabrino)


def dinner_items():
    """Models and icons for 'Dinner at Eight': ingredients, dishes, the Ladle of Justice and the Bone Clerk's spectacles."""
    # Grave-cap truffle (world pickup)
    m = Mesh(41)
    m.ellipsoid((0, 0.0, 0), (0.07, 0.055, 0.06), (70, 50, 40), seg=8, rings=5, y_min=0.0,
                color_fn=lambda i, j: (96, 72, 56) if (i * 3 + j) % 4 == 0 else (64, 46, 36))
    m.ellipsoid((0.05, 0.0, 0.03), (0.04, 0.035, 0.035), (80, 58, 44), seg=6, rings=4, y_min=0.0)
    m.write_glb("grave_truffle.glb")
    # Ladle of Justice: handle at the bottom (grip), bowl at the top, like the other melee weapons
    m = Mesh(43)
    copper, wood = (190, 110, 60), (120, 80, 46)
    m.cylinder((0, 0.0, 0), 0.016, 0.22, wood, seg=8)
    m.cylinder((0, 0.22, 0), 0.012, 0.3, copper, seg=8, r_top=0.01)
    m.ellipsoid((0, 0.56, 0.03), (0.075, 0.06, 0.075), copper, seg=10, rings=6,
                color_fn=lambda i, j: (230, 150, 90) if j > 3 else copper)
    m.write_glb("ladle_of_justice.glb")
    # Wine bottle (world model for Vallo Red)
    m = Mesh(47)
    m.cylinder((0, 0.0, 0), 0.04, 0.16, (60, 20, 30), seg=10)
    m.cylinder((0, 0.16, 0), 0.04, 0.05, (60, 20, 30), seg=10, r_top=0.015)
    m.cylinder((0, 0.21, 0), 0.015, 0.06, (60, 20, 30), seg=8)
    m.box((0, 0.08, 0.041), (0.05, 0.05, 0.004), (220, 200, 160))
    m.write_glb("vallo_red.glb")

    def icon(name, draw):
        img, d = icon_canvas()
        draw(d)
        save_icon(img, name)

    def bowl(d, food, garnish):
        d.ellipse([5, 13, 27, 23], fill=food)
        for x, y in ((10, 15), (15, 14), (20, 16), (13, 18), (18, 18)):
            d.ellipse([x, y, x + 3, y + 2], fill=garnish)
        d.chord([4, 10, 28, 28], 0, 180, fill=(190, 180, 160, 255))
        d.line([(6, 19), (26, 19)], fill=(150, 140, 120, 255))

    icon("sabrino_gnocchi", lambda d: bowl(d, (236, 214, 150, 255), (110, 160, 70, 255)))
    icon("ash_pepper_stew", lambda d: bowl(d, (170, 60, 30, 255), (255, 170, 60, 255)))

    def braid(d):
        for k in range(4):
            d.ellipse([5 + k * 5, 11 + (k % 2) * 3, 13 + k * 5, 20 + (k % 2) * 3], fill=(196, 132, 64, 255), outline=(140, 86, 40, 255))
        d.line([(7, 14), (24, 18)], fill=(240, 230, 210, 255))
    icon("oakhallow_braid", braid)

    def roll(d):
        d.ellipse([7, 10, 25, 25], fill=(214, 156, 84, 255), outline=(150, 98, 50, 255))
        d.arc([10, 13, 22, 22], 200, 340, fill=(240, 220, 180, 255), width=2)
        for x, y in ((12, 12), (17, 11), (20, 14)):
            d.point((x, y), fill=(255, 255, 255, 255))
    icon("sweet_roll", roll)

    def bottle(d):
        d.rectangle([12, 12, 20, 28], fill=(80, 24, 36, 255))
        d.rectangle([14, 5, 18, 12], fill=(80, 24, 36, 255))
        d.rectangle([14, 3, 18, 5], fill=(170, 130, 80, 255))
        d.rectangle([12, 17, 20, 22], fill=(226, 206, 160, 255))
        d.line([(13, 13), (13, 27)], fill=(140, 60, 80, 255))
    icon("vallo_red", bottle)

    def truffle(d):
        d.ellipse([7, 10, 25, 25], fill=(70, 50, 40, 255))
        for x, y in ((10, 14), (15, 12), (19, 17), (13, 20), (21, 21)):
            d.point((x, y), fill=(120, 96, 76, 255))
        d.ellipse([18, 8, 27, 16], fill=(84, 60, 46, 255))
    icon("grave_truffle", truffle)

    def pepper(d):
        d.polygon([(9, 25), (12, 12), (17, 9), (22, 12), (14, 26)], fill=(200, 60, 30, 255))
        d.line([(17, 9), (20, 4)], fill=(70, 120, 50, 255), width=2)
        d.line([(12, 16), (15, 23)], fill=(255, 140, 80, 255))
        for x, y in ((8, 8), (25, 20), (6, 15)):
            d.point((x, y), fill=(255, 170, 60, 255))
    icon("ash_pepper", pepper)

    def ladle(d):
        d.line([(6, 27), (20, 11)], fill=(120, 80, 46, 255), width=2)
        d.ellipse([17, 4, 28, 14], fill=(200, 116, 62, 255), outline=(140, 76, 40, 255))
        d.arc([19, 6, 26, 12], 20, 160, fill=(240, 170, 110, 255))
    icon("ladle_of_justice", ladle)

    def specs(d):
        d.ellipse([4, 12, 14, 21], outline=(200, 190, 160, 255), width=2)
        d.ellipse([18, 12, 28, 21], outline=(200, 190, 160, 255), width=2)
        d.line([(14, 15), (18, 15)], fill=(200, 190, 160, 255))
        d.line([(4, 15), (2, 12)], fill=(200, 190, 160, 255))
        d.line([(28, 15), (30, 12)], fill=(200, 190, 160, 255))
        d.ellipse([6, 14, 12, 19], fill=(120, 150, 170, 120))
        d.ellipse([20, 14, 26, 19], fill=(120, 150, 170, 120))
    icon("bone_spectacles", specs)


def manor_items():
    """Icons for the Hollowmere quests (models reuse existing GLBs)."""
    def icon(name, draw):
        img, d = icon_canvas()
        draw(d)
        save_icon(img, name)

    def bucket(d):
        d.polygon([(8, 10), (24, 10), (22, 27), (10, 27)], fill=(150, 156, 166, 255), outline=(90, 96, 106, 255))
        d.line([(9, 15), (23, 15)], fill=(110, 116, 126, 255))
        d.line([(10, 22), (22, 22)], fill=(110, 116, 126, 255))
        d.arc([7, 3, 25, 19], 180, 360, fill=(120, 126, 136, 255), width=1)
        d.ellipse([18, 17, 21, 20], fill=(90, 96, 106, 255))  # the dent
    icon("dented_bucket", bucket)

    def party_hat(d):
        d.polygon([(16, 3), (8, 27), (24, 27)], fill=(230, 90, 160, 255))
        for k, col in enumerate([(255, 220, 80, 255), (100, 200, 255, 255), (140, 230, 120, 255)]):
            y = 10 + k * 6
            d.line([(16 - (y - 3) // 3, y), (16 + (y - 3) // 3, y)], fill=col, width=2)
        d.ellipse([13, 1, 19, 6], fill=(255, 230, 120, 255))
    icon("party_hat", party_hat)

    def crown(d):
        d.polygon([(6, 24), (6, 11), (11, 17), (16, 8), (21, 17), (26, 11), (26, 24)], fill=(230, 190, 70, 255), outline=(160, 120, 40, 255))
        for x in (10, 16, 22):
            d.ellipse([x - 1, 19, x + 1, 21], fill=(200, 40, 60, 255))
        d.line([(24, 26), (29, 29)], fill=(200, 140, 140, 255))  # a tail, peeking out
    icon("rat_crown", crown)

    def cape(d):
        d.polygon([(10, 5), (22, 5), (27, 28), (5, 28)], fill=(30, 24, 34, 255))
        d.polygon([(12, 7), (20, 7), (24, 26), (8, 26)], fill=(130, 24, 40, 255))
        for x, y in ((9, 12), (22, 18), (14, 22), (25, 9), (6, 20)):
            d.point((x, y), fill=(255, 255, 255, 255))  # sparkles
    icon("cape_brooding", cape)

    def jerky(d):
        d.polygon([(6, 20), (14, 9), (26, 12), (22, 24), (10, 26)], fill=(130, 70, 40, 255), outline=(90, 46, 26, 255))
        d.line([(9, 21), (22, 13)], fill=(170, 100, 60, 255))
    icon("moonlit_jerky", jerky)

    def guide(d):
        d.rectangle([7, 5, 25, 27], fill=(60, 70, 90, 255), outline=(30, 34, 44, 255))
        d.rectangle([9, 7, 23, 25], outline=(170, 180, 200, 255))
        d.ellipse([12, 11, 20, 19], outline=(200, 230, 255, 255))
        d.line([(16, 19), (16, 23)], fill=(200, 230, 255, 255))
    icon("field_guide", guide)
    silver = ((0.95, 0.15), (1.0, 0.15), (1.15, 0.15))
    tinted("assets/ui/items/iron_longsword.png", "assets/ui/items/silver_sword.png", silver)
    tinted("assets/ui/items/signet_ring.png", "assets/ui/items/hollowmere_signet.png", ((0.8, 0.0), (0.9, 0.0), (1.4, 0.0)))
    tinted("assets/ui/items/annex_key.png", "assets/ui/items/hollowmere_key.png", ((1.0, 0.0), (0.7, 0.0), (1.2, 0.0)))
    tinted("assets/ui/items/crypt_key.png", "assets/ui/items/study_key.png", ((1.2, 0.0), (1.0, 0.0), (0.6, 0.0)))


def players_items():
    """Icons for The Bellwether Players."""
    def icon(name, draw):
        img, d = icon_canvas()
        draw(d)
        save_icon(img, name)

    def script(d):
        d.rectangle([8, 5, 25, 27], fill=(120, 30, 70, 255), outline=(70, 16, 40, 255))
        d.rectangle([10, 7, 23, 25], outline=(230, 190, 90, 255))
        d.line([(12, 12), (21, 12)], fill=(230, 190, 90, 255))
        d.line([(12, 16), (19, 16)], fill=(230, 190, 90, 255))
        d.line([(20, 20), (24, 26)], fill=(200, 40, 50, 255), width=2)  # the critic's red quill
    icon("script_tragedie", script)

    def tomato(d):
        d.ellipse([7, 10, 25, 27], fill=(210, 50, 40, 255), outline=(150, 30, 26, 255))
        d.polygon([(13, 10), (16, 6), (19, 10), (16, 12)], fill=(70, 140, 60, 255))
        d.ellipse([11, 13, 15, 17], fill=(240, 120, 110, 255))
    icon("thrown_tomato", tomato)

    def mask(d):
        d.pieslice([4, 6, 28, 30], 180, 360, fill=(220, 180, 70, 255))
        d.rectangle([4, 17, 28, 20], fill=(220, 180, 70, 255))
        d.ellipse([8, 12, 14, 17], fill=(26, 22, 30, 255))
        d.ellipse([18, 12, 24, 17], fill=(26, 22, 30, 255))
        d.line([(16, 8), (16, 12)], fill=(255, 230, 140, 255))
        d.line([(5, 18), (1, 26)], fill=(160, 30, 80, 255), width=2)  # ribbon
    icon("mask_uncounted", mask)

    def paper_crown(d):
        d.polygon([(6, 24), (6, 12), (11, 18), (16, 9), (21, 18), (26, 12), (26, 24)], fill=(236, 210, 120, 255), outline=(170, 140, 70, 255))
        d.line([(8, 21), (24, 21)], fill=(200, 120, 160, 255))  # chapter nine, showing through
    icon("paper_crown", paper_crown)

    def dragon(d):
        d.polygon([(5, 22), (12, 12), (22, 10), (27, 15), (22, 18), (14, 20), (10, 26)], fill=(70, 130, 70, 255), outline=(40, 80, 40, 255))
        d.polygon([(14, 12), (18, 4), (20, 11)], fill=(90, 160, 90, 255))
        d.ellipse([22, 12, 25, 15], fill=(255, 220, 80, 255))
    icon("dragon_costume", dragon)

    def fireworks(d):
        for i, col in enumerate([(240, 200, 60, 255), (120, 220, 120, 255), (180, 90, 230, 255)]):
            x = 9 + i * 6
            d.rectangle([x, 12, x + 3, 27], fill=col)
            d.polygon([(x, 12), (x + 1.5, 7), (x + 3, 12)], fill=(220, 60, 50, 255))
        d.line([(25, 6), (28, 3)], fill=(255, 240, 160, 255))
        d.line([(27, 8), (30, 8)], fill=(255, 240, 160, 255))
    icon("fireworks", fireworks)

    def thunder(d):
        d.rectangle([6, 6, 26, 26], fill=(160, 166, 176, 255), outline=(100, 106, 116, 255))
        d.line([(18, 8), (12, 16), (19, 16), (13, 25)], fill=(255, 230, 90, 255), width=2)
    icon("thunder_sheet", thunder)


BUILDERS = {
    "bread": bread,
    "leather_jerkin": lambda: garment("leather_jerkin", (122, 80, 46), (84, 54, 32)),
    "chain_hauberk": lambda: garment("chain_hauberk", (160, 166, 176), (90, 70, 50), chain=True),
    "scholar_robe": lambda: garment("scholar_robe", (88, 60, 112), (200, 176, 110), robe=True),
    "boots": boots,
    "helm": helm,
    "signet_ring": lambda: ring("signet_ring", (214, 178, 76), (170, 30, 40)),
    "ring_of_recall": lambda: ring("ring_of_recall", (196, 204, 220), (90, 170, 255)),
    "seal_quill": seal_quill,
    "baggy_umbrella": baggy_umbrella,
    "sabrino_hat": sabrino_hat,
    "extra_icons": build_extra_icons,
    "dinner_items": dinner_items,
    "manor_items": manor_items,
    "players_items": players_items,
}


if __name__ == "__main__":
    # python tools/build_item_models.py [name ...]   (no names = build everything)
    import sys
    only = sys.argv[1:]
    for name, fn in BUILDERS.items():
        if not only or name in only:
            fn()

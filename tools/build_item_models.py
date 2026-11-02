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


if __name__ == "__main__":
    bread()
    garment("leather_jerkin", (122, 80, 46), (84, 54, 32))
    garment("chain_hauberk", (160, 166, 176), (90, 70, 50), chain=True)
    garment("scholar_robe", (88, 60, 112), (200, 176, 110), robe=True)
    boots()
    helm()
    ring("signet_ring", (214, 178, 76), (170, 30, 40))
    ring("ring_of_recall", (196, 204, 220), (90, 170, 255))
    seal_quill()

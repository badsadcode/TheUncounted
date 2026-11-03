#!/usr/bin/env python3
"""
Offline pre-rendered sprite builder for THE UNCOUNTED.

Characters and creatures are modelled as small sets of signed-distance primitives (spheres,
ellipsoids, capsules, tapered capsules, rounded boxes), posed per animation row, raymarched
orthographically from the 8 sheet directions, then cel-shaded and outlined into crisp pixel art.

Output keeps the engine's sheet contract (see build_assets_art.py):
    64x64 frames, 8 columns = directions (0 front, 1 front-left, 2 left, 3 back-left, 4 back,
    5 back-right, 6 right, 7 front-right), rows 0 idle, 1-2 walk, 3 windup, 4 attack,
    5 stagger (cols 0-3, one per 90 degrees) / corpse (cols 4-7).

Run:  python tools/build_sprites_prerendered.py
"""

import math
import os

import numpy as np
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRAME = 64
PIVOT_Y = 58.9          # feet row (matches "pivot": [0.5, 0.92])
PX_PER_UNIT = 56.0      # 1.0 model unit spans 56 px
CAM_PITCH = math.radians(14.0)


# =============================================================================
# Math helpers
# =============================================================================
def v3(x, y, z):
    return np.array([x, y, z], dtype=np.float64)


def rot_x(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_y(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rot_z(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def norm(v):
    n = np.linalg.norm(v)
    return v / n if n > 1e-9 else v


# =============================================================================
# Materials
# =============================================================================
class Mat:
    def __init__(self, color, emissive=False, stripes=None, alpha=255, shine=0.0):
        self.color = np.array(color[:3], dtype=np.float64)
        self.emissive = emissive
        self.stripes = stripes  # (axis, frequency, threshold, color2) evaluated in model space
        self.alpha = alpha if len(color) < 4 else color[3]
        self.shine = shine


# =============================================================================
# SDF primitives (all vectorised over an (N,3) array of points)
# =============================================================================
class Prim:
    def __init__(self, kind, mat, **kw):
        self.kind = kind
        self.mat = mat
        self.kw = kw

    def sdf(self, p):
        k = self.kw
        if "rot" in k:
            p = (p - k["origin"]) @ k["rot"] + k["origin"]
        if self.kind == "sphere":
            return np.linalg.norm(p - k["c"], axis=1) - k["r"]
        if self.kind == "ellipsoid":
            q = (p - k["c"]) / k["r"]
            k0 = np.linalg.norm(q, axis=1)
            k1 = np.linalg.norm((p - k["c"]) / (k["r"] * k["r"]), axis=1)
            return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)
        if self.kind == "capsule":
            a, b = k["a"], k["b"]
            pa = p - a
            ba = b - a
            h = np.clip((pa @ ba) / max(ba @ ba, 1e-12), 0.0, 1.0)
            r = k["r1"] + (k["r2"] - k["r1"]) * h
            return np.linalg.norm(pa - np.outer(h, ba), axis=1) - r
        if self.kind == "box":
            q = np.abs(p - k["c"]) - k["h"]
            outside = np.linalg.norm(np.maximum(q, 0.0), axis=1)
            inside = np.minimum(np.max(q, axis=1), 0.0)
            return outside + inside - k.get("round", 0.0)
        raise ValueError(self.kind)


def sphere(c, r, mat):
    return Prim("sphere", mat, c=np.asarray(c, float), r=r)


def ellipsoid(c, r, mat, rot=None):
    p = Prim("ellipsoid", mat, c=np.asarray(c, float), r=np.asarray(r, float))
    if rot is not None:
        p.kw["rot"] = rot
        p.kw["origin"] = np.asarray(c, float)
    return p


def capsule(a, b, r1, mat, r2=None):
    return Prim("capsule", mat, a=np.asarray(a, float), b=np.asarray(b, float), r1=r1, r2=r1 if r2 is None else r2)


def box(c, h, mat, rnd=0.0, rot=None):
    p = Prim("box", mat, c=np.asarray(c, float), h=np.asarray(h, float), round=rnd)
    if rot is not None:
        p.kw["rot"] = rot
        p.kw["origin"] = np.asarray(c, float)
    return p


# =============================================================================
# Renderer
# =============================================================================
def render(prims, view_angle, global_rot=None, global_off=None, scale=1.0):
    """Raymarches the primitive set from `view_angle` (radians around Y, 0 = in front of the model)."""
    a = view_angle
    back = v3(math.sin(a) * math.cos(CAM_PITCH), math.sin(CAM_PITCH), math.cos(a) * math.cos(CAM_PITCH))
    fwd = -back
    right = norm(np.cross(fwd, v3(0, 1, 0)))
    up = np.cross(right, fwd)

    ys, xs = np.mgrid[0:FRAME, 0:FRAME]
    px = (xs.ravel() + 0.5 - FRAME / 2) / PX_PER_UNIT
    py = (PIVOT_Y - (ys.ravel() + 0.5)) / PX_PER_UNIT
    origins = np.outer(px, right) + np.outer(py, up) + back * 3.0
    n = origins.shape[0]

    def scene(p):
        q = p
        if global_off is not None:
            q = q - global_off
        if global_rot is not None:
            q = q @ global_rot
        q = q / scale
        best = np.full(q.shape[0], 1e9)
        idx = np.full(q.shape[0], -1, dtype=np.int32)
        for i, pr in enumerate(prims):
            d = pr.sdf(q) * scale
            m = d < best
            best[m] = d[m]
            idx[m] = i
        return best, idx, q

    t = np.zeros(n)
    alive = np.ones(n, dtype=bool)
    hit = np.zeros(n, dtype=bool)
    for _ in range(90):
        if not alive.any():
            break
        ai = np.nonzero(alive)[0]
        p = origins[ai] + np.outer(t[ai], fwd)
        d, _, _ = scene(p)
        h = d < 0.0015
        hit[ai[h]] = True
        alive[ai[h]] = False
        t[ai[~h]] += np.maximum(d[~h] * 0.85, 0.002)
        far = t > 6.0
        alive &= ~far

    rgba = np.zeros((n, 4))
    depth = np.full(n, 1e9)
    matid = np.full(n, -1, dtype=np.int32)
    hi = np.nonzero(hit)[0]
    if len(hi):
        p = origins[hi] + np.outer(t[hi], fwd)
        _, idx, local = scene(p)
        eps = 0.002
        nx = np.zeros((len(hi), 3))
        for k in range(3):
            o = np.zeros(3)
            o[k] = eps
            d1, _, _ = scene(p + o)
            d2, _, _ = scene(p - o)
            nx[:, k] = d1 - d2
        nx /= np.maximum(np.linalg.norm(nx, axis=1, keepdims=True), 1e-9)

        light = norm(-right * 0.55 + up * 0.85 + back * 0.6)
        lam = np.clip(nx @ light, 0.0, 1.0)
        rim = np.clip(1.0 - np.abs(nx @ back), 0.0, 1.0) ** 3
        # Cel bands: deep shadow, shadow, lit, highlight
        band = np.where(lam > 0.82, 1.18, np.where(lam > 0.45, 1.0, np.where(lam > 0.12, 0.78, 0.6)))
        for j, h_i in enumerate(hi):
            pr = prims[idx[j]]
            mat = pr.mat
            col = mat.color.copy()
            if mat.stripes is not None:
                axis, freq, thr, col2 = mat.stripes
                if math.sin(local[j][axis] * freq) > thr:
                    col = np.array(col2[:3], float)
            if mat.emissive:
                out = col
            else:
                out = col * band[j] + 40.0 * rim[j] * 0.25
                if mat.shine > 0 and lam[j] > 0.9:
                    out = out + mat.shine * 60.0
            rgba[h_i, :3] = np.clip(out, 0, 255)
            rgba[h_i, 3] = mat.alpha
            depth[h_i] = t[h_i]
            matid[h_i] = idx[j]

    img = rgba.reshape(FRAME, FRAME, 4)
    depth = depth.reshape(FRAME, FRAME)
    matid = matid.reshape(FRAME, FRAME)
    emissive = np.zeros((FRAME, FRAME), dtype=bool)
    for i, pr in enumerate(prims):
        if pr.mat.emissive:
            emissive |= matid == i

    def shift(a, dy, dx, fill):
        r = np.full_like(a, fill)
        h, w = a.shape[:2]
        ys0, ys1 = max(dy, 0), h + min(dy, 0)
        xs0, xs1 = max(dx, 0), w + min(dx, 0)
        r[ys0:ys1, xs0:xs1] = a[ys0 - dy:ys1 - dy, xs0 - dx:xs1 - dx]
        return r

    # Inner contour lines where depth jumps (limb in front of torso etc.)
    out = img.copy()
    opaque = img[:, :, 3] > 0
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        nd = shift(depth, dy, dx, 1e9)
        no = shift(opaque, dy, dx, False)
        edge = opaque & no & (depth - nd > 0.06) & ~emissive
        out[edge, :3] *= 0.62
    # Selective outer outline: darkened colour of the neighbouring sprite pixel.
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        src = shift(img, dy, dx, 0)
        so = src[:, :, 3] > 0
        m = ~opaque & so & (out[:, :, 3] == 0)
        out[m, :3] = src[m, :3] * 0.28
        out[m, 3] = np.maximum(src[m, 3], 200)
    return out.astype(np.uint8)


# =============================================================================
# Character rigs
# =============================================================================
def shade(c, k):
    return tuple(int(max(0, min(255, x * k))) for x in c[:3]) + ((c[3],) if len(c) > 3 else ())


def limb(shoulder, pitch, roll, upper, lower, bend):
    """Returns elbow & hand positions for an arm/leg hanging down then rotated by pitch (forward +) and roll."""
    d1 = rot_z(roll) @ rot_x(-pitch) @ v3(0, -1, 0)
    elbow = shoulder + d1 * upper
    d2 = rot_z(roll) @ rot_x(-(pitch + bend)) @ v3(0, -1, 0)
    hand = elbow + d2 * lower
    return elbow, hand


def humanoid(style, row, col_dir=0):
    """Builds primitives for a humanoid in the pose for sheet `row`. Model faces +Z; its right hand is -X."""
    alpha = style.get("alpha", 255)

    def M(c, **kw):
        return Mat(c if len(c) == 4 else tuple(c) + (alpha,), **kw)

    skin = M(style["body"])
    tunic = M(style["armor"], stripes=(1, 95.0, 0.55, shade(style["armor"], 0.55)) if style.get("ribs") else None)
    legs_m = M(style.get("legs", style["armor"]))
    cloak_m = M(style.get("cloak", shade(style["armor"], 0.8)))
    trim_m = M(style.get("trim", shade(style["armor"], 1.25)), shine=0.4)
    eye_m = Mat(style.get("eye", (30, 30, 30)), emissive=style.get("glow_eyes", False))
    hair_m = M(style.get("hair", (70, 50, 36)))
    boot_m = M(style.get("boots", shade(style.get("legs", style["armor"]), 0.6)))
    metal = Mat((178, 186, 196), shine=1.0)
    wood = Mat((110, 76, 44))
    skeletal = style.get("ribs", False)
    robe = style.get("robe", False)
    hover = style.get("hover", False)
    limb_r = 0.027 if skeletal else 0.04

    walk = {1: 1.0, 2: -1.0}.get(row, 0.0)
    prims = []

    hip_y = 0.49
    if hover:
        hip_y += 0.04
    bob = 0.012 * abs(walk)

    # Legs
    if not robe:
        for side, sx in (("r", -1), ("l", 1)):
            swing = math.radians(26) * walk * (1 if side == "l" else -1)
            hip = v3(0.062 * sx, hip_y + bob, 0)
            knee, ankle = limb(hip, swing, 0.0, 0.235, 0.225, -abs(swing) * 0.6 - 0.05)
            prims.append(capsule(hip, knee, limb_r + 0.008, legs_m, limb_r))
            prims.append(capsule(knee, ankle, limb_r, legs_m if skeletal else boot_m, limb_r * 0.95))
            foot = ankle + v3(0, -0.012, 0.035)
            prims.append(ellipsoid(foot, (0.034, 0.022, 0.058), boot_m if not skeletal else legs_m))
        if skeletal:
            prims.append(ellipsoid(v3(0, hip_y + 0.03, 0), (0.085, 0.045, 0.05), skin))
    else:
        sway = 0.025 * walk
        prims.append(capsule(v3(0, 0.56, 0), v3(sway, 0.035 if not hover else 0.07, 0), 0.105, tunic, 0.19))
        prims.append(capsule(v3(0, 0.555, 0), v3(0, 0.555, 0), 0.112, trim_m))
        if not hover:
            for sx in (-1, 1):
                prims.append(ellipsoid(v3(0.06 * sx, 0.02, 0.08 + 0.03 * walk * sx), (0.035, 0.022, 0.05), boot_m))

    # Torso
    lean = 0.0
    chest_c = v3(0, 0.68 + bob, 0)
    if skeletal:
        prims.append(capsule(v3(0, hip_y, -0.01), v3(0, 0.79 + bob, -0.01), 0.018, skin))
        prims.append(ellipsoid(chest_c + v3(0, 0.02, 0), (0.105, 0.105, 0.07), tunic))
    else:
        prims.append(ellipsoid(chest_c, (0.135, 0.175, 0.09), tunic))
        prims.append(box(v3(0, 0.555 + bob, 0), (0.125, 0.018, 0.085), trim_m, rnd=0.01))
    if style.get("apron"):
        prims.append(box(v3(0, 0.45, 0.075), (0.085, 0.16, 0.008), trim_m, rnd=0.01))

    # Cloak (behind the back, flaring toward the ground)
    if "cloak" in style and not robe:
        tilt = rot_x(math.radians(-7 - 4 * abs(walk)))
        prims.append(box(v3(0, 0.47 + bob, -0.105), (0.135, 0.33, 0.012), cloak_m, rnd=0.012, rot=tilt))
        prims.append(box(v3(0, 0.8 + bob, -0.03), (0.15, 0.035, 0.07), cloak_m, rnd=0.025))
    if robe and "cloak" in style:
        prims.append(box(v3(0, 0.79 + bob, 0), (0.135, 0.035, 0.085), cloak_m, rnd=0.025))

    # Head
    head_c = v3(0, 0.915 + bob, 0.005)
    prims.append(capsule(v3(0, 0.8 + bob, 0), head_c, 0.03 if not skeletal else 0.018, skin))
    prims.append(sphere(head_c, 0.088 if not skeletal else 0.082, skin))
    if skeletal:
        prims.append(ellipsoid(head_c + v3(0, -0.055, 0.03), (0.045, 0.025, 0.04), skin))
    hat = style.get("hat")
    eye_y = head_c[1] + 0.008
    if hat == "hood":
        hood_m = M(style.get("hood", style.get("cloak", style["armor"])))
        prims.append(sphere(head_c + v3(0, 0.012, -0.012), 0.104, hood_m))
        prims.append(capsule(head_c + v3(0, 0.07, -0.03), head_c + v3(0, 0.13, -0.07), 0.04, hood_m, 0.005))
        shadow = Mat((22, 20, 26, alpha))
        prims.append(ellipsoid(head_c + v3(0, -0.005, 0.078), (0.062, 0.07, 0.04), shadow))
        eye_z = head_c[2] + 0.112
    else:
        eye_z = head_c[2] + 0.081
        if hat == "cap":
            cap_m = M(style.get("cap", shade(style["armor"], 0.7)))
            prims.append(ellipsoid(head_c + v3(0, 0.055, -0.005), (0.093, 0.048, 0.095), cap_m))
            prims.append(box(head_c + v3(0, 0.04, 0.08), (0.075, 0.008, 0.032), cap_m, rnd=0.004))
        elif hat == "crown":
            gold = Mat((222, 182, 70), shine=1.0)
            prims.append(capsule(head_c + v3(0, 0.07, 0), head_c + v3(0, 0.095, 0), 0.07, gold))
            for k in range(6):
                ang = k * math.pi / 3
                base = head_c + v3(math.sin(ang) * 0.065, 0.1, math.cos(ang) * 0.065)
                prims.append(capsule(base, base + v3(0, 0.05, 0), 0.016, gold, 0.003))
        elif hat == "bun":
            prims.append(sphere(head_c + v3(0, 0.022, -0.014), 0.092, hair_m))
            prims.append(sphere(head_c + v3(0, 0.07, -0.07), 0.04, hair_m))
        elif hat == "witch":
            felt = M(style.get("cap", (70, 36, 80)))
            sash = M(style.get("band", (150, 36, 40)))
            prims.append(sphere(head_c + v3(0, 0.02, -0.016), 0.09, hair_m))
            prims.append(ellipsoid(head_c + v3(0, 0.06, -0.004), (0.18, 0.012, 0.18), felt))                      # brim
            prims.append(ellipsoid(head_c + v3(0, 0.08, -0.004), (0.088, 0.018, 0.088), sash))                    # sash
            prims.append(capsule(head_c + v3(0, 0.08, -0.004), head_c + v3(0, 0.22, -0.02), 0.08, felt, 0.04))  # crown
            prims.append(capsule(head_c + v3(0, 0.22, -0.02), head_c + v3(0.0, 0.3, -0.09), 0.04, felt, 0.008))  # bent tip
        elif hat == "fedora":
            felt = M(style.get("cap", (90, 70, 50)))
            band = M(style.get("band", (40, 30, 24)))
            prims.append(sphere(head_c + v3(0, 0.02, -0.016), 0.09, hair_m))
            prims.append(ellipsoid(head_c + v3(0, 0.062, -0.004), (0.15, 0.012, 0.15), felt))           # brim
            prims.append(ellipsoid(head_c + v3(0, 0.105, -0.004), (0.082, 0.055, 0.09), felt))         # crown
            prims.append(ellipsoid(head_c + v3(0, 0.08, -0.004), (0.086, 0.016, 0.094), band))         # band
        elif hat == "bald":
            prims.append(ellipsoid(head_c + v3(0, -0.01, -0.035), (0.092, 0.055, 0.065), hair_m))
        elif not skeletal and hat != "none":
            prims.append(sphere(head_c + v3(0, 0.024, -0.018), 0.09, hair_m))
        if style.get("beard"):
            prims.append(ellipsoid(head_c + v3(0, -0.065, 0.048), (0.06, 0.065, 0.042), hair_m))
    if skeletal:
        sock = Mat((24, 20, 26))
        for sx in (-1, 1):
            prims.append(sphere(v3(0.031 * sx, eye_y, head_c[2] + 0.062), 0.025, sock))
    for sx in (-1, 1):
        prims.append(sphere(v3(0.031 * sx, eye_y, eye_z - (0.005 if skeletal else 0)), 0.014 if not style.get("glow_eyes") else 0.017, eye_m))

    # Arms. Right arm (-X) carries the weapon.
    weapon = style.get("weapon")
    r_pitch, r_roll, r_bend = math.radians(-22) * walk + math.radians(8), math.radians(-8), math.radians(-18)
    l_pitch, l_roll, l_bend = math.radians(22) * walk + math.radians(8), math.radians(8), math.radians(-18)
    if weapon in ("sword", "staff", "umbrella"):
        r_bend = math.radians(-60)
        r_pitch = math.radians(14) + math.radians(-8) * walk
    if weapon == "ledger":
        l_pitch, l_bend = math.radians(30), math.radians(-70)
    if style.get("shield"):
        l_pitch, l_bend, l_roll = math.radians(25), math.radians(-70), math.radians(6)
    if row == 3:  # windup: weapon arm raised back
        r_pitch, r_roll, r_bend = math.radians(-150), math.radians(-25), math.radians(-30)
        if weapon == "staff":
            r_pitch, r_bend = math.radians(150), math.radians(-10)
    elif row == 4:  # strike: arm thrown forward
        r_pitch, r_roll, r_bend = math.radians(80), math.radians(-5), math.radians(-5)
    elif row == 5:  # stagger: arms flung out
        r_pitch, r_roll, r_bend = math.radians(-30), math.radians(-55), math.radians(-30)
        l_pitch, l_roll, l_bend = math.radians(-30), math.radians(55), math.radians(-30)

    r_sh = v3(-0.15, 0.8 + bob, 0)
    l_sh = v3(0.15, 0.8 + bob, 0)
    sleeve = tunic if not skeletal else skin
    r_el, r_hand = limb(r_sh, r_pitch, r_roll, 0.17, 0.16, r_bend)
    l_el, l_hand = limb(l_sh, l_pitch, l_roll, 0.17, 0.16, l_bend)
    for sh, el, hd in ((r_sh, r_el, r_hand), (l_sh, l_el, l_hand)):
        prims.append(capsule(sh, el, limb_r + 0.006, sleeve, limb_r))
        prims.append(capsule(el, hd, limb_r, skin if skeletal or style.get("bare_arms") else sleeve, limb_r * 0.9))
        prims.append(sphere(hd, limb_r * 1.15, skin))

    fdir = norm(r_hand - r_el)
    if weapon == "sword":
        # Blade points along the forearm turned upward-forward.
        bdir = norm(rot_x(-math.radians(80)) @ fdir) if row != 4 else norm(fdir + v3(0, 0, 0.3))
        if row == 3:
            bdir = norm(v3(0.1, 0.6, -0.8))
        tip = r_hand + bdir * 0.33
        prims.append(capsule(r_hand + bdir * 0.04, tip, 0.016, metal, 0.006))
        side = norm(np.cross(bdir, v3(0, 0, 1)) + 1e-6)
        prims.append(capsule(r_hand + bdir * 0.035 - side * 0.05, r_hand + bdir * 0.035 + side * 0.05, 0.011, trim_m))
        prims.append(capsule(r_hand - bdir * 0.05, r_hand + bdir * 0.02, 0.012, wood))
    elif weapon == "staff":
        sdir = v3(0, 1, 0.08) if row != 4 else norm(v3(0, 0.4, 1))
        if row == 3:
            sdir = norm(v3(0, 1, -0.3))
        top = r_hand + norm(sdir) * 0.42
        bottom = r_hand - norm(sdir) * 0.48
        prims.append(capsule(bottom, top, 0.014, wood))
        orb = Mat(style.get("orb", (110, 220, 255)), emissive=True)
        prims.append(sphere(top + norm(sdir) * 0.03, 0.04, orb))
    elif weapon == "umbrella":
        udir = v3(0, 1, 0.1) if row != 4 else norm(v3(0, 0.4, 1))
        if row == 3:
            udir = norm(v3(0, 1, -0.3))
        udir = norm(udir)
        cloth = Mat((36, 36, 44))
        prims.append(capsule(r_hand - udir * 0.06, r_hand + udir * 0.05, 0.012, wood))
        prims.append(capsule(r_hand + udir * 0.06, r_hand + udir * 0.42, 0.034, cloth, 0.006))
    elif weapon == "ledger":
        book = Mat(style.get("book", (140, 40, 36)))
        page = Mat((236, 226, 196))
        prims.append(box(l_hand + v3(0, 0.03, 0.03), (0.06, 0.075, 0.018), book, rnd=0.006))
        prims.append(box(l_hand + v3(0, 0.03, 0.047), (0.052, 0.067, 0.004), page))
    if style.get("shield"):
        sh_m = Mat(style["shield"])
        c = l_hand + v3(0.03, 0.02, 0.05)
        prims.append(ellipsoid(c, (0.1, 0.12, 0.022), sh_m))
        prims.append(sphere(c + v3(0, 0, 0.02), 0.03, Mat((205, 170, 80), shine=1.0)))
    return prims


def rat(style, row):
    body = Mat(style["body"])
    belly = Mat(shade(style["body"], 1.25))
    pink = Mat((210, 140, 140))
    eye = Mat(style["eye"], emissive=True)
    tooth = Mat((240, 236, 210))
    walk = {1: 1.0, 2: -1.0}.get(row, 0.0)
    lunge = 0.06 if row == 4 else (-0.03 if row == 3 else 0.0)
    rear = 0.04 if row == 3 else 0.0
    p = []
    p.append(ellipsoid(v3(0, 0.12, -0.02), (0.1, 0.085, 0.16), body))
    p.append(ellipsoid(v3(0, 0.095, 0.0), (0.075, 0.05, 0.12), belly))
    hc = v3(0, 0.15 + rear, 0.16 + lunge)
    p.append(ellipsoid(hc, (0.065, 0.06, 0.08), body))
    p.append(ellipsoid(hc + v3(0, -0.015, 0.075), (0.032, 0.03, 0.05), body))
    p.append(sphere(hc + v3(0, -0.012, 0.125), 0.014, pink))
    for sx in (-1, 1):
        p.append(ellipsoid(hc + v3(0.045 * sx, 0.055, -0.03), (0.03, 0.035, 0.012), pink))
        p.append(sphere(hc + v3(0.035 * sx, 0.02, 0.055), 0.013, eye))
    if row in (3, 4):
        p.append(box(hc + v3(0, -0.045, 0.1), (0.016, 0.016, 0.006), tooth))
    for k, (sx, sz) in enumerate(((-1, 1), (1, 1), (-1, -1), (1, -1))):
        ph = walk * (1 if (k in (0, 3)) else -1)
        top = v3(0.065 * sx, 0.08, 0.09 * sz)
        foot = v3(0.07 * sx, 0.012, 0.09 * sz + 0.04 * ph)
        p.append(capsule(top, foot, 0.02, body, 0.014))
        p.append(ellipsoid(foot + v3(0, -0.004, 0.015), (0.018, 0.01, 0.024), pink))
    prev = v3(0, 0.1, -0.17)
    for i in range(6):
        nxt = prev + v3(0.025 * math.sin(i * 0.9 + walk), -0.012 if i < 3 else 0.004, -0.045)
        p.append(capsule(prev, nxt, 0.013 - i * 0.0015, pink))
        prev = nxt
    return p


def crawler(style, row):
    shell = Mat(style["body"], shine=0.6)
    under = Mat(style["armor"])
    ember = Mat(style.get("glow", (255, 120, 40)), emissive=True)
    eye = Mat(style["eye"], emissive=True)
    walk = {1: 1.0, 2: -1.0}.get(row, 0.0)
    raise_front = {3: 0.06, 4: -0.02}.get(row, 0.0)
    lunge = 0.07 if row == 4 else 0.0
    p = []
    p.append(ellipsoid(v3(0, 0.2, -0.04), (0.19, 0.11, 0.24), shell))
    p.append(ellipsoid(v3(0, 0.15, -0.04), (0.16, 0.06, 0.2), under))
    # glowing cracks along the carapace
    for k in range(3):
        p.append(capsule(v3(-0.1 + k * 0.1, 0.3, 0.05 - k * 0.02), v3(-0.07 + k * 0.08, 0.29, -0.2 + k * 0.03), 0.009, ember))
    hc = v3(0, 0.19 + raise_front, 0.22 + lunge)
    p.append(ellipsoid(hc, (0.1, 0.075, 0.08), shell))
    for sx in (-1, 1):
        for k in range(3):
            p.append(sphere(hc + v3(0.025 * sx + 0.02 * sx * k, 0.035 - 0.012 * k, 0.07 - 0.01 * k), 0.012, eye))
        open_ = 0.05 if row in (3, 4) else 0.02
        p.append(capsule(hc + v3(0.04 * sx, -0.03, 0.06), hc + v3((0.02 + open_) * sx, -0.06, 0.14), 0.014, under, 0.006))
    for k in range(3):
        z = 0.12 - k * 0.14
        for sx in (-1, 1):
            ph = walk * (1 if (k + (sx > 0)) % 2 == 0 else -1)
            hip = v3(0.15 * sx, 0.2, z)
            knee = v3(0.29 * sx, 0.28, z + 0.04 * ph)
            foot = v3(0.35 * sx, 0.0, z + 0.07 * ph)
            p.append(capsule(hip, knee, 0.026, shell, 0.02))
            p.append(capsule(knee, foot, 0.02, under, 0.008))
    return p


def corpse_transform(kind):
    if kind == "humanoid":
        return rot_x(math.radians(-88)), v3(0, 0.07, 0.42)
    if kind == "rat":
        return rot_z(math.radians(85)), v3(0.1, 0.07, 0)
    return rot_z(math.radians(170)), v3(0, 0.36, 0)


def build_prims(style, row):
    kind = style["kind"]
    if kind == "rat":
        return rat(style, row)
    if kind == "crawler":
        return crawler(style, row)
    return humanoid(style, row)


def build_sheet(sprite_rel, style):
    sheet = np.zeros((FRAME * 6, FRAME * 8, 4), dtype=np.uint8)
    kind = style["kind"]
    sc = style.get("scale", 1.0)
    for row in range(6):
        for col in range(8):
            if row == 5 and col >= 4:
                prims = build_prims(style, 0)
                grot, goff = corpse_transform(kind)
                img = render(prims, math.radians(45 * col + 30), global_rot=grot, global_off=goff * sc, scale=sc)
            elif row == 5:
                prims = build_prims(style, 5)
                stagger = rot_x(math.radians(-14)) if kind == "humanoid" else rot_x(math.radians(-10))
                img = render(prims, math.radians(90 * col), global_rot=stagger, global_off=v3(0, 0, -0.03), scale=sc)
            else:
                prims = build_prims(style, row)
                img = render(prims, math.radians(45 * col), scale=sc)
            sheet[row * FRAME:(row + 1) * FRAME, col * FRAME:(col + 1) * FRAME] = img
    path = os.path.join(ROOT, sprite_rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(sheet, "RGBA").save(path)
    print("Rendered", sprite_rel)


SHEETS = {
    "assets/sprites/enemies/grave_rat.png": {"kind": "rat", "scale": 1.7, "body": (104, 84, 74), "armor": (70, 56, 48), "eye": (255, 60, 50)},
    "assets/sprites/enemies/ash_crawler.png": {"kind": "crawler", "scale": 1.15, "body": (66, 72, 84), "armor": (40, 40, 48), "eye": (255, 170, 50), "glow": (255, 110, 30)},
    "assets/sprites/enemies/skeleton.png": {
        "kind": "humanoid", "ribs": True, "body": (222, 212, 188), "armor": (205, 196, 172), "legs": (205, 196, 172),
        "cloak": (96, 34, 36), "eye": (110, 230, 255), "glow_eyes": True, "hat": "none", "weapon": "sword",
        "shield": (104, 84, 62), "trim": (150, 120, 70),
    },
    "mods/example_mod/assets/sprites/enemies/crimson_skeleton.png": {
        "kind": "humanoid", "ribs": True, "body": (236, 196, 184), "armor": (226, 180, 168), "legs": (226, 180, 168),
        "cloak": (176, 32, 38), "eye": (255, 220, 70), "glow_eyes": True, "hat": "none", "weapon": "sword",
        "shield": (150, 40, 42), "trim": (220, 180, 80),
    },
    "assets/sprites/enemies/crypt_keeper.png": {
        "kind": "humanoid", "robe": True, "hover": True, "body": (170, 214, 230), "armor": (58, 38, 92), "cloak": (40, 26, 70),
        "trim": (214, 176, 74), "eye": (130, 250, 255), "glow_eyes": True, "hat": "crown", "weapon": "staff",
        "orb": (120, 235, 255), "bare_arms": True,
    },
    "assets/sprites/enemies/lullaby_warden.png": {
        "kind": "humanoid", "robe": True, "hover": True, "body": (214, 208, 196), "armor": (34, 70, 78), "cloak": (22, 40, 48),
        "trim": (196, 204, 214), "eye": (255, 190, 90), "glow_eyes": True, "hat": "hood", "hood": (28, 54, 62), "weapon": "staff",
        "orb": (255, 196, 110), "bare_arms": True,
    },
    "assets/sprites/npcs/clerk_oakhaven.png": {
        "kind": "humanoid", "body": (222, 186, 156), "armor": (52, 68, 98), "legs": (40, 44, 58), "cloak": (34, 44, 66),
        "trim": (196, 160, 74), "eye": (30, 34, 48), "hat": "cap", "cap": (30, 36, 52), "weapon": "ledger", "book": (120, 34, 32),
    },
    "assets/sprites/npcs/merchant_vaelen.png": {
        "kind": "humanoid", "body": (214, 182, 150), "armor": (124, 80, 44), "legs": (72, 54, 38), "cloak": (52, 98, 60),
        "trim": (214, 178, 72), "eye": (34, 40, 30), "hat": "cap", "cap": (60, 100, 64), "beard": True, "hair": (110, 70, 40),
    },
    "assets/sprites/npcs/innkeeper_marta.png": {
        "kind": "humanoid", "body": (228, 190, 160), "armor": (146, 60, 50), "legs": (84, 56, 46), "trim": (236, 226, 204),
        "eye": (40, 30, 24), "hat": "bun", "hair": (120, 64, 38), "apron": True,
    },
    "assets/sprites/npcs/librarian_fenwick.png": {
        "kind": "humanoid", "robe": True, "body": (204, 172, 146), "armor": (84, 60, 100), "cloak": (60, 42, 74),
        "trim": (200, 176, 110), "eye": (34, 30, 40), "hat": "bald", "hair": (186, 182, 176), "beard": True, "weapon": "ledger",
        "book": (40, 70, 110),
    },
    "assets/sprites/npcs/brother_aldous.png": {
        "kind": "humanoid", "robe": True, "body": (214, 180, 150), "armor": (216, 204, 176), "cloak": (190, 148, 64),
        "trim": (230, 190, 80), "eye": (40, 34, 30), "hat": "hood", "hood": (190, 148, 64), "weapon": "staff", "orb": (255, 236, 150),
    },
    "assets/sprites/npcs/ashbound_scout.png": {
        "kind": "humanoid", "body": (130, 160, 112), "armor": (70, 84, 60), "legs": (52, 58, 46), "cloak": (58, 70, 50),
        "eye": (230, 170, 50), "glow_eyes": True, "hat": "hood", "hood": (62, 76, 54), "weapon": "sword", "trim": (130, 100, 60),
    },
    "assets/sprites/npcs/detective_baggy.png": {
        "kind": "humanoid", "body": (226, 190, 160), "armor": (176, 150, 104), "legs": (64, 58, 52), "cloak": (160, 134, 92),
        "trim": (120, 96, 64), "eye": (36, 30, 26), "hat": "fedora", "cap": (96, 78, 56), "band": (44, 34, 28),
        "hair": (90, 64, 44), "weapon": "umbrella", "boots": (60, 40, 30),
    },
    "assets/sprites/npcs/witch_sabrino.png": {
        "kind": "humanoid", "robe": True, "body": (226, 188, 152), "armor": (96, 44, 108), "cloak": (64, 30, 76),
        "trim": (214, 180, 80), "eye": (40, 26, 20), "hat": "witch", "cap": (78, 40, 90), "band": (150, 36, 40),
        "hair": (40, 30, 26), "weapon": "staff", "orb": (255, 140, 50),
    },
    "assets/sprites/enemies/bone_clerk.png": {
        "kind": "humanoid", "ribs": True, "body": (214, 204, 180), "armor": (200, 190, 166), "legs": (200, 190, 166),
        "cloak": (44, 54, 80), "eye": (255, 220, 120), "glow_eyes": True, "hat": "cap", "cap": (34, 40, 58),
        "weapon": "ledger", "book": (120, 34, 32), "trim": (190, 160, 80),
    },
    "assets/sprites/enemies/ink_wraith.png": {
        "kind": "humanoid", "robe": True, "hover": True, "alpha": 225, "body": (40, 44, 56), "armor": (22, 24, 34),
        "cloak": (14, 16, 24), "trim": (90, 220, 130), "eye": (120, 255, 150), "glow_eyes": True, "hat": "hood",
        "hood": (18, 20, 30), "weapon": "staff", "orb": (90, 255, 140), "bare_arms": True,
    },
    "assets/sprites/enemies/truffle_hog.png": {"kind": "rat", "scale": 2.5, "body": (176, 120, 108), "armor": (112, 74, 62), "eye": (30, 20, 20)},
    "assets/sprites/npcs/erased_spirit.png": {
        "kind": "humanoid", "robe": True, "hover": True, "alpha": 210, "body": (150, 220, 238), "armor": (96, 170, 204),
        "cloak": (110, 190, 222), "trim": (200, 240, 255), "eye": (235, 255, 255), "glow_eyes": True, "hat": "hood",
        "hood": (110, 186, 220),
    },
}


if __name__ == "__main__":
    import sys
    only = sys.argv[1:]
    for rel, style in SHEETS.items():
        if only and not any(o in rel for o in only):
            continue
        build_sheet(rel, style)

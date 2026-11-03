#!/usr/bin/env python3
"""
Composes the seamless overworld content/maps/edrath_world.json from the authored regions in content/regions/.

Layout (no loading screens, no portals):
  * Bellwether Village at the origin.
  * The Old Road directly east, its west end meeting Bellwether's east gate (x = 20).
  * The Registry Annex & Forgotten Crypt *underground* beneath the road's east end. A tunnel leaves the road
    through the cliff arch and descends two stone flights (4.8 m) to a landing that opens into the Annex foyer.
Each region becomes a zone with its own sky, fog, light, weather, music and ambience; the engine blends
between zones as the player walks.

Run:  python tools/build_world.py
"""

import copy
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = os.path.join(ROOT, "content", "regions")
OUT = os.path.join(ROOT, "content", "maps", "edrath_world.json")
BASE_OUT = os.path.join(ROOT, "content", "maps", "edrath_world.base.json")    # the level before the Blender changes
BLENDER_EDITS = os.path.join(ROOT, "content", "maps", "edrath_blender.json")  # the changes made in Blender

ROAD_OFF = (48.0, 0.0, 0.0)
ANNEX_OFF = (87.0, -4.8, -8.4)
VAULT_OFF = (54.6, -10.4, -22.0)   # Vault III: the Nursery lies 5.6 m below the crypt, the Seal Chamber 5.6 m below that
VAULT_Z = VAULT_OFF[2]
HOLLOW_OFF = (0.0, 0.0, 42.0)
WOOD_OFF = (-46.0, 0.0, 0.0)   # the Whistling Wood: west of Bellwether, through a gap in the west wall
REEF_OFF = (1.6, 0.0, -150.0)   # the Sleeper's Reef: far out past the fog, only reachable by boat
SEASIDE_OFF = (160.0, 0.0, -60.0)   # "The Late Cindermaw": Quillsby's seaside house, only reachable by boat
HERE_OFF = (0.0, 0.0, 190.0)   # "Here", the city whose name was eaten (Chapter One): only by the dusk road from the Old Road
DOCKS_OFF = (1.6, 0.0, -42.0)   # Saltmere Docks: north of Bellwether, through a gap in the village's north wall  # Hollowmere Manor: south of Bellwether, through a gap in the village's south wall
WALL = "assets/models/env/wall_crypt.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"


def load(name):
    with open(os.path.join(REGIONS, name), encoding="utf-8") as f:
        return apply_materials(name, json.load(f))


# ============================================================================ per-area materials (Noor's texture set)
# Region files keep the base pieces (cobble, stone, timber...); here each area gets its own surfaces by swapping the
# model of matching prop ids (region-local ids, regex, full match) and laying thin floor overlays (rugs, marble).
ENV = "assets/models/env/"
MAT_FLOOR = lambda t: ENV + "floor_" + t + ".glb"
MAT_WALL = lambda t: ENV + "wall_" + t + ".glb"
MATERIALS = {
    "bellwether.json": [
        (r"rec_floor|lib_floor", MAT_FLOOR("flagstones")), (r"inn_floor", MAT_FLOOR("tavern_floor")),
        (r"rec_roof", MAT_FLOOR("roof_slate_mossy")), (r"inn_roof", MAT_FLOOR("roof_thatch")), (r"shop_back", MAT_WALL("red_brick")),
    ],
    "old_road.json": [
        (r"road_path", MAT_FLOOR("dirt_road")), (r"cliff_(north|south|west)", MAT_WALL("cave_rock")),
    ],
    "whistling_wood.json": [
        (r"wood_floor", MAT_FLOOR("forest_floor")), (r"lane_path|path_\d+|fork_\d+", MAT_FLOOR("dirt_road")),
        (r"wood_rock_.*|lane_wall_.*|corner_.*|camp_fire_stone\d+|pond_rim_\d+", MAT_WALL("cave_rock")),
        (r"tent_bedroll", MAT_FLOOR("straw_hay")),
    ],
    "hollowmere.json": [
        (r"grave_mound_\d+|garden_bed_\d+", MAT_FLOOR("graveyard_soil")), (r"drive", MAT_FLOOR("gravel_path")),
        (r"chimney_\d+", MAT_WALL("red_brick")), (r"roof", MAT_FLOOR("roof_slate_mossy")),
        (r"g_(foyer|mid)_.*", MAT_WALL("manor_wallpaper"), 1.0), (r"u_.*|stair_block|rail_[wn]", MAT_WALL("wood_panelling"), 1.0),
        (r"stairs_(lower|upper)", ENV + "stairs_carpet.glb"),
    ],
    "saltmere.json": [
        (r"sea_floor", MAT_FLOOR("sand_wet")), (r"well_floor", MAT_FLOOR("mud_puddles")), (r"chapel_floor", MAT_FLOOR("flagstones")),
        (r"sea_wall|well_wall_.*|chapel_ceiling|ch_.*", MAT_WALL("barnacle_stone")),
        (r"wh_w_.*|wh_[ns]_end|tav_e_.*|tav_[sn]_end", MAT_WALL("weathered_planks")),
        (r"tav_floor", MAT_FLOOR("tavern_floor")), (r"tav_roof|wh_roof", MAT_FLOOR("roof_slate_mossy")),
    ],
    "seaside_house.json": [
        (r"cove_sand|cove_sea_floor", MAT_FLOOR("sand_wet")), (r"house_floor", MAT_FLOOR("checker_marble")),
        (r"house_roof", MAT_FLOOR("roof_slate_mossy")), (r"cliff_[nswe]", MAT_WALL("cave_rock")), (r"rock_\d+", MAT_WALL("barnacle_stone")),
        (r"ext_.*", MAT_WALL("red_brick")), (r"int_.*|vault_.*", MAT_WALL("manor_wallpaper"), 1.0),
        (r"cushions_\d+", MAT_FLOOR("carpet_red")), (r"shoe_rack_\d+", MAT_WALL("wood_panelling")),
    ],
    "sleepers_reef.json": [
        (r"reef_sea_floor|isle_main", MAT_FLOOR("sand_wet")), (r"isle_[wen]", MAT_FLOOR("cave_rock")),
        (r"cliff_[nswe]|boulder_\d+", MAT_WALL("barnacle_stone")),
    ],
}
# Thin rugs/tiles laid over a floor (region-local box: x0, x1, y0, y1, z0, z1, uv)
OVERLAYS = {
    "hollowmere.json": [
        ("ballroom_marble", MAT_FLOOR("checker_marble"), (-3.85, 13.85, 0.02, 0.035, 6.15, 15.85), [7.0, 4.0]),
        ("kitchen_flags", MAT_FLOOR("flagstones"), (-13.85, -4.15, 0.02, 0.035, 6.15, 15.85), [4.0, 4.0]),
        ("foyer_runner", MAT_FLOOR("carpet_red"), (-1.0, 1.0, 0.02, 0.035, -7.85, 5.85), [1.0, 6.0]),
        ("dining_rug", MAT_FLOOR("carpet_red"), (-12.6, -5.4, 0.02, 0.035, -2.2, 1.8), [1.0, 1.0]),
    ],
}


# ============================================================================ ground scatter (Noor's cut-out sprites)
SC = "assets/sprites/scatter/"
SCATTER_KINDS = {  # sprite, height in metres
    "grass": (SC + "grass_tuft.png", 0.55), "flowers": (SC + "flowers_wild.png", 0.45), "fern": (SC + "fern.png", 0.8),
    "bush": (SC + "bush.png", 0.95), "mushrooms": (SC + "mushrooms.png", 0.42), "reeds": (SC + "reeds.png", 1.3),
}
# (area name, world x range, world z range, ground models it may sit on, {kind: weight}, count)
SCATTER_AREAS = [
    ("bellwether", (-21, 21), (-21, 21), ("floor_grass",), {"grass": 6, "flowers": 3, "bush": 1}, 150),
    ("old_road", (22, 76), (-17, 17), ("floor_grass",), {"grass": 6, "flowers": 2, "fern": 2, "bush": 2}, 240),
    ("hollowmere", (-20, 20), (21, 66), ("floor_grass", "floor_graveyard_soil"), {"grass": 6, "flowers": 2, "bush": 2, "mushrooms": 1}, 190),
    ("whistling_wood", (-69, -25), (-21, 21), ("floor_forest_floor",), {"fern": 5, "grass": 3, "mushrooms": 2, "bush": 2}, 320),
    ("reef", (-12, 15), (-166, -136), ("floor_sand_wet",), {"grass": 2, "reeds": 3}, 60),
    ("seaside", (145, 175), (-80, -48), ("floor_sand_wet",), {"grass": 3, "reeds": 2, "flowers": 1}, 45),
]
NO_BLOCK = ("tree_pine", "oak_canopy", "floor_")   # these don't push scatter away (trees only near the trunk)


def build_scatter(props, interactables, npcs):
    import random
    rng = random.Random(1234)
    boxes = []
    for p in props:
        (x0, x1), (y0, y1), (z0, z1) = extents(p)
        name = p["model"].split("/")[-1].replace(".glb", "")
        boxes.append((name, x0, x1, y0, y1, z0, z1, p["pos"]))
    keep_clear = [e["pos"] for e in interactables] + [e["pos"] for e in npcs]
    out = []
    for area, (ax0, ax1), (az0, az1), grounds, weights, count in SCATTER_AREAS:
        kinds = [k for k, w in weights.items() for _ in range(w)]
        placed, tries = 0, 0
        while placed < count and tries < count * 40:
            tries += 1
            x, z = rng.uniform(ax0, ax1), rng.uniform(az0, az1)
            top, ok = None, True
            for name, x0, x1, y0, y1, z0, z1, pos in boxes:
                if name.startswith(("tree_pine", "oak_")):
                    if (x - pos[0]) ** 2 + (z - pos[2]) ** 2 < 0.8 ** 2:
                        ok = False
                    continue
                if name in grounds and x0 <= x <= x1 and z0 <= z <= z1 and y1 <= 0.1:
                    top = y1 if top is None else max(top, y1)
                    continue
                if x0 - 0.35 <= x <= x1 + 0.35 and z0 - 0.35 <= z <= z1 + 0.35 and y1 > -0.6:
                    ok = False   # a road, a wall, a house, a bench...
                    break
            if not ok or top is None:
                continue
            if any((x - q[0]) ** 2 + (z - q[2]) ** 2 < 1.0 for q in keep_clear):
                continue
            sprite, size = SCATTER_KINDS[rng.choice(kinds)]
            out.append({"sprite": sprite, "pos": [round(x, 2), round(top, 3), round(z, 2)], "size": round(size * rng.uniform(0.8, 1.2), 2)})
            placed += 1
    # reeds round the Whistling Wood pond
    pond = [p["pos"] for p in props if p["id"].startswith("wood_pond_rim_")]
    if pond:
        cx = sum(q[0] for q in pond) / len(pond); cz = sum(q[2] for q in pond) / len(pond)
        r = max(((q[0] - cx) ** 2 + (q[2] - cz) ** 2) ** 0.5 for q in pond)
        for i in range(14):
            a = i / 14 * 6.2832 + rng.uniform(-0.15, 0.15)
            rr = r + rng.uniform(0.5, 1.1)
            out.append({"sprite": SCATTER_KINDS["reeds"][0], "pos": [round(cx + rr * math.cos(a), 2), 0.0, round(cz + rr * math.sin(a), 2)],
                        "size": round(rng.uniform(1.1, 1.5), 2)})
    # cobwebs across the upper corners of Hollowmere's ground-floor rooms (fixed quads, not billboards)
    for cx, cz, sx, sz in [(3.85, -7.85, 1, -1), (-13.85, -7.85, -1, -1), (13.85, -7.85, 1, -1), (-13.85, 15.85, -1, 1),
                           (13.85, 15.85, 1, 1), (-3.85, 6.15, -1, 1), (-4.15, -7.85, -1, -1)]:
        yaw = math.degrees(math.atan2(-sx, -sz))
        out.append({"sprite": SC + "cobweb.png", "pos": [round(HOLLOW_OFF[0] + cx - sx * 0.354, 3), 2.7, round(HOLLOW_OFF[2] + cz - sz * 0.354, 3)],
                    "size": 1.0, "yaw": round(yaw, 1)})
    return out



# ============================================================================ door frames
def _glb_bounds(path):
    import struct
    b = open(os.path.join(ROOT, path), "rb").read()
    n = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + n])
    mn, mx = [1e9] * 3, [-1e9] * 3
    for m in j["meshes"]:
        for prim in m["primitives"]:
            a = j["accessors"][prim["attributes"]["POSITION"]]
            mn = [min(x, y) for x, y in zip(mn, a["min"])]
            mx = [max(x, y) for x, y in zip(mx, a["max"])]
    return mn, mx


_frame_along_x = []


def door_frames(props, interactables):
    """Doors are narrower and shorter than the gaps left for them in the walls, so you could see past them. For every
    door: find the wall on each side and the lintel above, and fill what's left with dark wooden frame pieces."""
    frames = []
    _frame_along_x.clear()
    boxes = [(p, extents(p)) for p in props if p.get("solid", True)]
    for d in interactables:
        if d.get("type") != "door" or not d.get("model"):
            continue
        mn, mx = _glb_bounds(d["model"])
        hw, h = (mx[0] - mn[0]) / 2, mx[1] - mn[1]
        x, y, z = d["pos"]
        along_x = round(d.get("rot_y", 0.0)) % 180 == 0       # the door spans x (else z)
        a0 = x if along_x else z                               # along the doorway
        c0 = z if along_x else x                               # across it (the wall's plane)
        def span(e):
            (ex0, ex1), (ey0, ey1), (ez0, ez1) = e
            return ((ex0, ex1), (ez0, ez1)) if along_x else ((ez0, ez1), (ex0, ex1))
        side_edges, depth = {}, None
        for sgn in (-1, 1):
            edge = a0 + sgn * hw
            best = None
            for p, e in boxes:
                (pa0, pa1), (pc0, pc1) = span(e)
                (ey0, ey1) = e[1]
                if not (pc0 - 0.05 <= c0 <= pc1 + 0.05) or ey1 < y + 0.5 or ey0 > y + 1.0 or not (0.15 <= pc1 - pc0 <= 1.5):
                    continue
                gap = (pa0 - edge) if sgn > 0 else (edge - pa1)
                if -0.05 <= gap <= 1.5 and (best is None or gap < best[0]):
                    best = (gap, pa0 if sgn > 0 else pa1, pc0, pc1)
            if best:
                side_edges[sgn] = best[1]
                depth = (best[2], best[3]) if depth is None else (min(depth[0], best[2]), max(depth[1], best[3]))
                if best[0] > 0.02:
                    lo, hi = sorted((edge, best[1]))
                    frames.append((lo, hi, y, y + h + 0.02, best[2], best[3])); _frame_along_x.append(along_x)
        if depth is None:
            continue
        left, right = side_edges.get(-1, a0 - hw), side_edges.get(1, a0 + hw)
        # the lintel: the lowest wall piece above the doorway
        top = None
        for p, e in boxes:
            (pa0, pa1), (pc0, pc1) = span(e)
            (ey0, ey1) = e[1]
            if pc0 - 0.05 <= c0 <= pc1 + 0.05 and pa0 < a0 < pa1 and ey0 > y + h - 0.05 and ey0 - (y + h) < 1.5:
                top = ey0 if top is None else min(top, ey0)
        if top is not None and top - (y + h) > 0.02:
            frames.append((left, right, y + h, top, depth[0], depth[1])); _frame_along_x.append(along_x)
    out = []
    for i, (a_lo, a_hi, y0, y1, c_lo, c_hi) in enumerate(frames):
        c_lo, c_hi = c_lo - 0.03, c_hi + 0.03              # a hair proud of the wall, like a real frame
        x0, x1, z0, z1 = a_lo, a_hi, c_lo, c_hi
        if not _frame_along_x[i]:
            x0, x1, z0, z1 = c_lo, c_hi, a_lo, a_hi
        out.append(box_prop(f"door_frame_{i}", MAT_WALL("wood_panelling"), x0, x1, y0, y1, z0, z1, uv=[0.2, 0.5]))
    return out

SKIES = {"bellwether": "night", "old_road": "night", "hollowmere": "night", "saltmere": "night", "sleepers_reef": "night",
         "whistling_wood": "dusk", "seaside_house": "dusk", "here": "night"}


def with_skies(zones):
    for z in zones:
        if z["id"] in SKIES:
            z["sky_panorama"] = "assets/textures/sky/sky_%s.png" % SKIES[z["id"]]
    return zones


def apply_materials(name, region):
    import re
    rules = MATERIALS.get(name, [])
    for p in region.get("props", []):
        for rule in rules:
            if re.fullmatch(rule[0], p["id"]):
                p["model"] = rule[1]
                if len(rule) > 2 and "uv_scale" in p:
                    p["uv_scale"] = [p["uv_scale"][0], rule[2]]   # wallpaper/panelling: one pattern per wall height
                break
    for pid, model, (x0, x1, y0, y1, z0, z1), uv in OVERLAYS.get(name, []):
        region.setdefault("props", []).append(box_prop(pid, model, x0, x1, y0, y1, z0, z1, uv=uv, solid=False))
    return region


def offset(v, off):
    return [round(v[0] + off[0], 3), round(v[1] + off[1], 3), round(v[2] + off[2], 3)]


def shift_region(m, off, prefix):
    """Moves every positioned element of a region by `off`; prop ids get a region prefix (they are not persisted)."""
    for p in m.get("props", []):
        p["pos"] = offset(p["pos"], off)
        p["id"] = prefix + p["id"]
    for key in ("npcs", "creatures", "interactables"):
        for e in m.get(key, []):
            e["pos"] = offset(e["pos"], off)
            for k in ("patrol_a", "patrol_b"):
                if k in e:
                    e[k] = offset(e[k], off)
    for l in m.get("lights", []):
        l["pos"] = offset(l["pos"], off)
    for sp in m.get("spawns", {}).values():
        sp["pos"] = offset(sp["pos"], off)
    return m


def box_prop(pid, model, x0, x1, y0, y1, z0, z1, uv=None, solid=True):
    """Unit-cube model stretched to an axis-aligned box (models are anchored at their bottom centre)."""
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    p = {"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
         "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid}
    p["uv_scale"] = uv or [round(max(sx, sz) / 2.6, 2), round(sy / 3.0, 2)]
    return p


def extents(p):
    x, y, z = p["pos"]
    sx, sy, sz = p["scale"]
    return [x - sx / 2, x + sx / 2], [y, y + sy], [z - sz / 2, z + sz / 2]


def clip_x(p, lo=None, hi=None):
    """Clips an unrotated unit-cube prop along X (used where regions meet)."""
    (x0, x1), _, _ = extents(p)
    if lo is not None:
        x0 = max(x0, lo)
    if hi is not None:
        x1 = min(x1, hi)
    if x1 - x0 < 0.05:
        return None
    k = (x1 - x0) / p["scale"][0]
    p["pos"][0] = round((x0 + x1) / 2, 3)
    p["scale"][0] = round(x1 - x0, 3)
    if "uv_scale" in p:
        p["uv_scale"][0] = round(p["uv_scale"][0] * k, 2)
    return p


def clip_z(p, lo=None, hi=None):
    _, _, (z0, z1) = extents(p)
    if lo is not None:
        z0 = max(z0, lo)
    if hi is not None:
        z1 = min(z1, hi)
    k = (z1 - z0) / p["scale"][2]
    p["pos"][2] = round((z0 + z1) / 2, 3)
    p["scale"][2] = round(z1 - z0, 3)
    if "uv_scale" in p:
        p["uv_scale"][1 if p["scale"][1] < 1 else 0] = round(p["uv_scale"][1 if p["scale"][1] < 1 else 0] * k, 2)
    return p


def torch(tid, x, y, z, rot, ghost=False):
    return {"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False,
            "emitter": {"sprite": "assets/sprites/vfx/spell_arcane.png" if ghost else "assets/sprites/vfx/torch_flame.png",
                        "offset": [0.0, 0.86, 0.0], "size": 0.32 if ghost else 0.38,
                        "light_color": [0.45, 0.8, 1.0] if ghost else [1.0, 0.62, 0.28], "light_radius": 6.5}}


def zone_from(region, zid, box_min, box_max, blend):
    z = {"id": zid, "display_name_key": region["display_name_key"], "box_min": box_min, "box_max": box_max, "blend": blend}
    for k in ("music", "ambience", "sky_color", "ambient_color", "sun_direction", "sun_color", "fog_color", "fog_density"):
        z[k] = region[k]
    z["weather"] = region.get("weather", "")
    return z


def build():
    bell = shift_region(load("bellwether.json"), (0, 0, 0), "bell_")
    road = shift_region(load("old_road.json"), ROAD_OFF, "road_")
    annex = shift_region(load("registry_annex.json"), ANNEX_OFF, "annex_")
    vault = shift_region(load("vault_three.json"), VAULT_OFF, "vault_")
    hollow = shift_region(load("hollowmere.json"), HOLLOW_OFF, "hollow_")
    docks = shift_region(load("saltmere.json"), DOCKS_OFF, "docks_")
    wood = shift_region(load("whistling_wood.json"), WOOD_OFF, "wood_")
    reef = shift_region(load("sleepers_reef.json"), REEF_OFF, "reef_")
    seaside = shift_region(load("seaside_house.json"), SEASIDE_OFF, "sea_")
    here = shift_region(load("here.json"), HERE_OFF, "here_")

    props = []
    for p in bell["props"]:
        if p["id"] == "bell_wall_north":
            west = clip_x(copy.deepcopy(p), hi=0.0)
            east = clip_x(copy.deepcopy(p), lo=3.2)
            west["id"], east["id"] = "bell_wall_north_w", "bell_wall_north_e"
            props += [west, east]
            continue
        if p["id"] == "bell_wall_west":
            # A 3.2 m gap in the middle of the west wall leads out to the Whistling Wood.
            north = clip_z(copy.deepcopy(p), hi=-1.6)
            south = clip_z(copy.deepcopy(p), lo=1.6)
            north["id"], south["id"] = "bell_wall_west_n", "bell_wall_west_s"
            props += [north, south]
            continue
        if p["id"] == "bell_wall_south":
            # A 3.2 m gap in the middle of the south wall leads down the drive to Hollowmere Manor.
            west = clip_x(copy.deepcopy(p), hi=-1.6)
            east = clip_x(copy.deepcopy(p), lo=1.6)
            west["id"], east["id"] = "bell_wall_south_w", "bell_wall_south_e"
            props += [west, east]
            continue
        props.append(p)
    props += [
        {"id": "bell_south_gate_w", "model": "assets/models/env/pillar_stone.glb", "pos": [-2.1, 0.0, 20.0], "scale": [1.1, 1.25, 1.4], "solid": True},
        {"id": "bell_south_gate_e", "model": "assets/models/env/pillar_stone.glb", "pos": [2.1, 0.0, 20.0], "scale": [1.1, 1.25, 1.4], "solid": True},
    ]
    props += hollow["props"]
    props += wood["props"]
    props += reef["props"]
    props += seaside["props"]
    props += here["props"]
    props += [
        {"id": "bell_west_gate_n", "model": "assets/models/env/pillar_stone.glb", "pos": [-20.0, 0.0, -2.1], "scale": [1.4, 1.25, 1.1], "solid": True},
        {"id": "bell_west_gate_s", "model": "assets/models/env/pillar_stone.glb", "pos": [-20.0, 0.0, 2.1], "scale": [1.4, 1.25, 1.1], "solid": True},
    ]
    props += docks["props"]
    props += [
        {"id": "bell_north_gate_w", "model": "assets/models/env/pillar_stone.glb", "pos": [-0.5, 0.0, -20.0], "scale": [1.1, 1.25, 1.4], "solid": True},
        {"id": "bell_north_gate_e", "model": "assets/models/env/pillar_stone.glb", "pos": [3.7, 0.0, -20.0], "scale": [1.1, 1.25, 1.4], "solid": True},
    ]

    # --- Old Road: drop its west cliff (Bellwether's east wall + gate is the boundary) and trim overlaps.
    road_east_x = ROAD_OFF[0] + 28.0 + 0.75  # outer face of the east cliff
    for p in road["props"]:
        pid = p["id"]
        if pid == "road_cliff_west":
            continue
        if pid == "road_cliff_east":
            # Split around a 3.2 m opening for the tunnel and close the top with a lintel.
            north = clip_z(copy.deepcopy(p), hi=-1.6)
            south = clip_z(copy.deepcopy(p), lo=1.6)
            north["id"], south["id"] = "road_cliff_east_n", "road_cliff_east_s"
            props += [north, south]
            lintel = copy.deepcopy(p)
            lintel.update({"id": "road_cliff_east_lintel"})
            lintel["pos"] = [p["pos"][0], 3.0, 0.0]
            lintel["scale"] = [p["scale"][0], p["scale"][1] - 3.0, 3.2]
            lintel["uv_scale"] = [1.2, 0.8]
            props.append(lintel)
            continue
        if pid in ("road_ground_forest", "road_road_path", "road_cliff_north", "road_cliff_south"):
            p = clip_x(p, lo=20.6, hi=road_east_x if pid == "road_ground_forest" else None)
            if p is None:
                continue
        props.append(p)

    # --- Tunnel: cliff opening -> two flights down -> landing -> Annex foyer.
    tx0 = road_east_x
    props += [
        box_prop("tunnel_threshold", COBBLE, ROAD_OFF[0] + 27.0, 77.0, -0.48, 0.02, -1.6, 1.6, uv=[1.2, 1.0], solid=False),
        {"id": "tunnel_stairs_upper", "model": STAIRS, "pos": [79.0, -2.4, 0.0], "rot_y": 90.0, "scale": [1.0, 1.2, 1.0],
         "solid": False, "ramp": "-x"},
        {"id": "tunnel_stairs_lower", "model": STAIRS, "pos": [83.0, -4.8, 0.0], "rot_y": 90.0, "scale": [1.0, 1.2, 1.0],
         "solid": False, "ramp": "-x"},
        box_prop("tunnel_wall_n", WALL, tx0, 85.15, -4.8, 3.4, -1.85, -1.55),
        box_prop("tunnel_wall_s", WALL, tx0, 85.15, -4.8, 3.4, 1.55, 1.85),
        box_prop("tunnel_ceiling_upper", WALL, tx0, 81.0, 3.0, 3.4, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_step", WALL, 80.85, 81.15, 1.0, 3.4, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_lower", WALL, 81.0, 85.0, 0.6, 1.0, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_drop", WALL, 84.85, 85.15, -1.6, 1.0, -1.85, 1.85, solid=False),
        box_prop("landing_floor", COBBLE, 85.0, 89.6, -5.3, -4.8, -1.6, 2.3, uv=[1.8, 1.5], solid=False),
        box_prop("landing_ceiling", WALL, 85.0, 89.6, -1.6, -1.2, -1.6, 2.3, solid=False),
        box_prop("landing_wall_s", WALL, 84.85, 89.6, -4.8, -1.2, 2.0, 2.3),
        box_prop("landing_wall_e", WALL, 89.3, 89.6, -4.8, -1.2, -1.6, 2.3),
        box_prop("landing_wall_w", WALL, 84.85, 85.15, -4.8, -1.2, 1.55, 2.3),
        torch("torch_tunnel_upper", 79.5, -0.3, 1.45, 180.0),
        torch("torch_landing", 89.2, -3.1, 0.3, -90.0),
    ]

    # --- Annex: open the foyer's south wall onto the landing; keep its floor/ceiling out of the tunnel.
    for p in annex["props"]:
        pid = p["id"]
        if pid == "annex_foyer_s":
            west = clip_x(copy.deepcopy(p), hi=85.8)
            east = clip_x(copy.deepcopy(p), lo=88.2)
            west["id"], east["id"] = "annex_foyer_s_w", "annex_foyer_s_e"
            props += [west, east]
            continue
        if pid == "annex_crypt_w":
            # Gap in the crypt's west wall for the stair down to Vault III, closed above by a lintel.
            north = clip_z(copy.deepcopy(p), hi=VAULT_Z - 1.6)
            south = clip_z(copy.deepcopy(p), lo=VAULT_Z + 1.6)
            north["id"], south["id"] = "annex_crypt_w_n", "annex_crypt_w_s"
            lintel = copy.deepcopy(p)
            lintel.update({"id": "annex_crypt_w_lintel", "uv_scale": [1.2, 0.5]})
            lintel["pos"] = [p["pos"][0], -1.8, VAULT_Z]
            lintel["scale"] = [p["scale"][0], p["pos"][1] + p["scale"][1] + 1.8, 3.2]
            props += [north, south, lintel]
            continue
        if pid in ("annex_dungeon_floor", "annex_dungeon_ceiling"):
            p = clip_z(p, hi=-1.6)
            p = clip_x(p, lo=65.4 if pid == "annex_dungeon_floor" else 64.6)
        props.append(p)

    # --- Vault III descent: crypt west wall -> two flights down (5.6 m) -> the Nursery landing.
    vz = VAULT_Z
    props += [
        box_prop("vault_threshold", COBBLE, 64.4, 65.4, -5.3, -4.8, vz - 1.6, vz + 1.6, uv=[0.5, 1.2], solid=False),
        {"id": "vault_stairs_upper", "model": STAIRS, "pos": [62.4, -7.6, vz], "rot_y": -90.0, "scale": [1.0, 1.4, 1.0],
         "solid": False, "ramp": "+x"},
        {"id": "vault_stairs_lower", "model": STAIRS, "pos": [58.4, -10.4, vz], "rot_y": -90.0, "scale": [1.0, 1.4, 1.0],
         "solid": False, "ramp": "+x"},
        box_prop("vault_tunnel_wall_n", WALL, 56.4, 64.6, -10.4, -1.4, vz + 1.55, vz + 1.85),
        box_prop("vault_tunnel_wall_s", WALL, 56.4, 64.6, -10.4, -1.4, vz - 1.85, vz - 1.55),
        box_prop("vault_tunnel_ceiling_upper", WALL, 60.4, 64.6, -1.8, -1.4, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_step", WALL, 60.25, 60.55, -4.6, -1.4, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_lower", WALL, 56.4, 60.4, -4.6, -4.2, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_drop", WALL, 56.25, 56.55, -7.0, -4.2, vz - 1.85, vz + 1.85, solid=False),
        torch("torch_vault_stairs", 62.5, -4.9, vz + 1.45, 180.0, ghost=True),
    ]
    props += vault["props"]

    interactables = bell["interactables"] + road["interactables"] + annex["interactables"] + vault["interactables"] + hollow["interactables"] + docks["interactables"] + wood["interactables"] + reef["interactables"] + seaside["interactables"] + here["interactables"]
    interactables.append({
        "instance_id": "flour_handprints", "type": "readable", "model": "", "pos": [65.75, -3.8, VAULT_Z + 2.3], "rot_y": 0.0,
        "prompt": "Look at the Marks on the Wall", "title": "Handprints in Old Flour",
        "text": ("Small handprints, a child's, pressed into the stone in old flour. They lead along the wall to a gap where the "
                 "masonry has been opened, and a stair going down: deeper than the Annex was ever built.\n\n"
                 "Someone has chalked beside them, in an archivist's neat hand: \"VAULT III. THE NURSERY. DO NOT WAKE.\""),
        "quest_id": "core:quest.vault_three", "set_stage": 0,
    })
    interactables.append({
        "instance_id": "landing_warning", "type": "readable", "model": "", "pos": [87.0, -3.8, 1.75], "rot_y": 0.0,
        "prompt": "Read the Scratches on the Wall", "title": "Scratched into the Stone",
        "text": ("Dozens of hands have cut the same words into the wall, over and over, in different scripts and different "
                 "centuries:\n\nTURN BACK. THE NAMES ARE LISTENING.\n\n"
                 "Beneath them, newer and neater, in Bureau ink: \"Graffiti is a Class III municipal offence.\""),
    })
    npcs = bell["npcs"] + road["npcs"] + annex["npcs"] + vault["npcs"] + hollow["npcs"] + docks["npcs"] + wood["npcs"] + reef["npcs"] + seaside["npcs"] + here["npcs"]
    creatures = bell["creatures"] + road["creatures"] + annex["creatures"] + vault["creatures"] + hollow["creatures"] + docks["creatures"] + wood["creatures"] + reef["creatures"] + seaside["creatures"] + here["creatures"]
    lights = bell["lights"] + road["lights"] + annex["lights"] + vault["lights"] + hollow["lights"] + docks["lights"] + wood["lights"] + reef["lights"] + seaside["lights"] + here["lights"]
    spawns = {}
    for m in (bell, road, annex, vault, hollow, docks, wood, reef, seaside, here):
        spawns.update(m["spawns"])

    for kind, items in (("interactable", interactables), ("npc", npcs), ("creature", creatures)):
        ids = [e["instance_id"] for e in items]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise SystemExit("duplicate %s ids: %s" % (kind, dup))
    pids = [p["id"] for p in props]
    dup = {i for i in pids if pids.count(i) > 1}
    if dup:
        raise SystemExit("duplicate prop ids: %s" % dup)

    bell_zone = zone_from(bell, "bellwether", [-21.0, -2.0, -21.0], [20.6, 40.0, 21.0], 4.0)
    # Signing the Seal of Names in Vault III ends seventeen years of rain over the village.
    bell_zone["flag_override"] = {"flag": "seal_renewed", "weather": "", "ambience": "assets/audio/ambience/forest_wind.wav"}
    seal_zone = zone_from(vault, "seal_chamber", [3.5, -17.0, -30.0], [21.0, -10.6, -14.0], 2.0)
    seal_zone.update({"display_name_key": "map.seal_chamber.name", "fog_density": 0.05, "ambient_color": [0.15, 0.19, 0.32]})
    manor_zone = zone_from(hollow, "hollowmere_manor", [-14.0, -1.0, 34.0], [14.0, 9.0, 58.0], 1.5)
    manor_zone.update({"display_name_key": "map.hollowmere_manor.name", "weather": "", "fog_density": 0.03,
                       "ambience": "assets/audio/ambience/crypt_drips.wav", "ambient_color": [0.3, 0.3, 0.42], "sky_color": [10, 10, 16]})
    grounds_zone = zone_from(hollow, "hollowmere", [-21.0, -1.0, 20.7], [21.0, 40.0, 67.0], 3.0)
    grounds_zone["flag_override"] = {"flag": "seal_renewed", "weather": "", "ambience": "assets/audio/ambience/forest_wind.wav"}
    ox, oz = DOCKS_OFF[0], DOCKS_OFF[2]
    chapel_zone = zone_from(docks, "sunken_chapel", [ox + 2.0, -7.5, oz - 22.0], [ox + 19.0, -1.6, oz - 4.0], 2.0)
    chapel_zone.update({"display_name_key": "map.sunken_chapel.name", "fog_color": [0.04, 0.12, 0.09], "fog_density": 0.06,
                        "ambient_color": [0.18, 0.32, 0.26], "sky_color": [6, 14, 12], "ambience": "assets/audio/ambience/crypt_drips.wav",
                        "music": "assets/audio/music/crypt_theme.wav", "sanity_drain": 1.6})
    docks_zone = zone_from(docks, "saltmere", [ox - 20.6, -1.6, oz - 35.0], [ox + 20.6, 40.0, -20.6], 3.0)
    wx = WOOD_OFF[0]
    wood_zone = zone_from(wood, "whistling_wood", [wx - 24.6, -1.0, -22.6], [-21.0, 40.0, 22.6], 3.0)
    rx, rz = REEF_OFF[0], REEF_OFF[2]
    reef_zone = zone_from(reef, "sleepers_reef", [rx - 27.0, -2.0, rz - 27.0], [rx + 27.0, 40.0, rz + 27.0], 3.0)
    reef_zone["sanity_drain"] = 0.5
    sx, sz = SEASIDE_OFF[0], SEASIDE_OFF[2]
    seaside_zone = zone_from(seaside, "seaside_house", [sx - 17.0, -2.0, sz - 21.0], [sx + 17.0, 40.0, sz + 27.0], 3.0)
    hx, hz = HERE_OFF[0], HERE_OFF[2]
    here_zone = zone_from(here, "here", [hx - 31.0, -2.0, hz - 41.0], [hx + 31.0, 40.0, hz + 45.0], 3.0)
    here_zone["day_fog_density"] = 0.12       # by day the city goes thin: it fades into a pale fog
    archive_zone = zone_from(here, "here_archive", [hx - 10.0, -1.0, hz - 38.0], [hx + 10.0, 12.0, hz - 24.0], 1.5)
    archive_zone.update({"display_name_key": "map.here_archive.name", "fog_color": [0.05, 0.05, 0.1], "fog_density": 0.05,
                         "ambient_color": [0.24, 0.24, 0.36], "sky_color": [8, 8, 16], "weather": "",
                         "ambience": "assets/audio/ambience/crypt_drips.wav", "music": "assets/audio/music/crypt_theme.wav",
                         "sanity_drain": 0.6, "priority": 1})
    zones = [
        archive_zone,
        here_zone,
        seaside_zone,
        reef_zone,
        wood_zone,
        chapel_zone,
        docks_zone,
        manor_zone,
        grounds_zone,
        seal_zone,
        zone_from(vault, "vault_three", [3.5, -17.0, -30.0], [57.0, -5.2, -14.0], 3.0),
        zone_from(annex, "annex", [59.0, -14.0, -46.0], [104.0, -0.9, 2.6], 3.0),
        zone_from(road, "old_road", [20.6, -0.9, -16.0], [77.0, 40.0, 16.0], 4.0),
        bell_zone,
    ]

    props += door_frames(props, interactables)
    world = {
        "schema_version": 1,
        "id": "core:map.edrath",
        "display_name_key": "map.edrath.name",
        "music": bell["music"], "ambience": bell["ambience"],
        "sky_color": bell["sky_color"], "ambient_color": bell["ambient_color"], "sun_direction": bell["sun_direction"],
        "sun_color": bell["sun_color"], "fog_color": bell["fog_color"], "fog_density": bell["fog_density"],
        "weather": bell.get("weather", ""),
        "zones": with_skies(zones),
        "scatter": build_scatter(props, interactables, npcs),
        "spawns": spawns,
        "props": props,
        "lights": lights,
        "npcs": npcs,
        "creatures": creatures,
        "interactables": interactables,
        "portals": [],
    }
    with open(BASE_OUT, "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    if os.path.exists(BLENDER_EDITS):
        # The level as changed in Blender (tools/blender/uncounted_level_editor.py): those changes always win.
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from map_edits import apply_edits
        with open(BLENDER_EDITS, encoding="utf-8") as f:
            world = apply_edits(world, json.load(f), warn=lambda m: print("  warning:", m))
        print("Applied the Blender changes from", os.path.relpath(BLENDER_EDITS, ROOT))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    print("Wrote %s: %d props, %d interactables, %d creatures, %d zones" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                           len(creatures), len(zones)))


if __name__ == "__main__":
    build()

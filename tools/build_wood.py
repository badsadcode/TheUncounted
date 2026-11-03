#!/usr/bin/env python3
"""
Generates content/regions/whistling_wood.json: the Whistling Wood, west of Bellwether (Case File #3).

Region-local frame (build_world.py places it at WOOD_OFF = (-46, 0, 0); local x = +25.4 is the outer face of
Bellwether's west wall, which gets a 3.2 m gap at z -1.6..1.6):
  * Forest floor x -24..22, z -22..22, ringed by rock; a short walled lane x 22..25.4 joins it to the village gap.
  * A winding path west to the Old Oak (a huge hollow oak, x -14, z 6), Steve's camp (x -2, z -12) and the ruin of
    Grandmother's cottage (x 10, z 13).
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python tools/build_wood.py
"""

import json
import math
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "whistling_wood.json")
STONE = "assets/models/env/wall_stone.glb"
TIMBER = "assets/models/env/wall_timber.glb"
WOOD = "assets/models/env/floor_wood.glb"
GRASS = "assets/models/env/floor_grass.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
PINE = "assets/models/env/tree_pine.glb"
TORCH = "assets/models/props/wall_torch.glb"
LECTERN = "assets/models/props/lectern_ledger.glb"
SIGN = "assets/models/props/signpost.glb"
CRATE = "assets/models/props/wooden_crate.glb"
QUEST = "core:quest.trout"

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def prop(pid, model, x, y, z, rot=0.0, scale=(1, 1, 1), solid=True):
    props.append({"id": pid, "model": model, "pos": [x, y, z], "rot_y": rot, "scale": list(scale), "solid": solid})


def fire(fid, x, z):
    """A campfire: a ring of stones and a flame emitter at ground level."""
    for k in range(6):
        a = k * math.pi / 3
        box(f"{fid}_stone{k}", STONE, x + math.cos(a) * 0.5 - 0.12, x + math.cos(a) * 0.5 + 0.12, 0.0, 0.2,
            z + math.sin(a) * 0.5 - 0.12, z + math.sin(a) * 0.5 + 0.12, solid=False, uv=[0.2, 0.1])
    props.append({"id": fid, "model": TORCH, "pos": [x, -0.55, z], "rot_y": 0.0, "scale": [1, 1, 1], "solid": False,
                  "emitter": {"sprite": "assets/sprites/vfx/torch_flame.png", "offset": [0.0, 0.86, 0.0], "size": 0.6,
                              "light_color": [1.0, 0.6, 0.28], "light_radius": 8.0}})


def readable(iid, x, y, z, prompt, title, text, model="", rot=0.0, **extra):
    d = {"instance_id": iid, "type": "readable", "model": model, "pos": [x, y, z], "rot_y": rot, "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ ground, boundary, the lane from the village
box("wood_floor", GRASS, -24.0, 22.0, -0.5, 0.0, -22.0, 22.0, solid=False, uv=[16, 16])
box("wood_rock_w", STONE, -24.6, -23.4, -0.5, 5.5, -22.6, 22.6)
box("wood_rock_n", STONE, -24.6, 25.6, -0.5, 5.5, -22.6, -21.4)
box("wood_rock_s", STONE, -24.6, 25.6, -0.5, 5.5, 21.4, 22.6)
box("wood_rock_e_n", STONE, 21.4, 22.6, -0.5, 5.5, -21.4, -1.6)
box("wood_rock_e_s", STONE, 21.4, 22.6, -0.5, 5.5, 1.6, 21.4)
# The lane (on the village's own grass) between the wood and Bellwether's west wall, walled both sides
box("lane_wall_n", STONE, 22.6, 25.6, -0.5, 4.5, -2.2, -1.6)
box("lane_wall_s", STONE, 22.6, 25.6, -0.5, 4.5, 1.6, 2.2)
box("corner_n", STONE, 24.8, 25.6, -0.5, 4.5, -22.6, -19.4)   # closes the gap to Bellwether's wall corners
box("corner_s", STONE, 24.8, 25.6, -0.5, 4.5, 19.4, 22.6)
box("lane_path", COBBLE, 21.4, 25.0, -0.48, 0.02, -1.6, 1.6, solid=False, uv=[1.4, 1.2])
# A winding dirt-and-stone path west, then forking to the camp, the oak and the cottage
path = [(21.4, 0.0), (14.0, 0.0), (8.0, -2.0), (3.0, -4.0), (-2.0, -7.0), (-2.0, -10.0)]
for i in range(len(path) - 1):
    (ax, az), (bx, bz) = path[i], path[i + 1]
    box(f"path_{i}", COBBLE, min(ax, bx) - 0.9, max(ax, bx) + 0.9, -0.49, 0.015, min(az, bz) - 0.9, max(az, bz) + 0.9, solid=False,
        uv=[round(abs(ax - bx) / 2.2 + 0.6, 1), round(abs(az - bz) / 2.2 + 0.6, 1)])
for i, ((ax, az), (bx, bz)) in enumerate([((3.0, -4.0), (-6.0, 1.0)), ((-6.0, 1.0), (-11.5, 5.0)), ((8.0, -2.0), (9.5, 9.5))]):
    box(f"fork_{i}", COBBLE, min(ax, bx) - 0.8, max(ax, bx) + 0.8, -0.495, 0.012, min(az, bz) - 0.8, max(az, bz) + 0.8, solid=False,
        uv=[round(abs(ax - bx) / 2.2 + 0.6, 1), round(abs(az - bz) / 2.2 + 0.6, 1)])

# Pines, thick round the edges, scattered inside (kept off the paths and clearings)
trees = [(-21, -19), (-17, -20), (-12, -19.5), (-7, -20), (2, -19.5), (7, -20), (12, -19), (17, -20), (20, -16), (19.5, -9),
         (20, 7), (19.5, 12), (20, 18), (15, 20), (6, 20), (1, 19.5), (-5, 20), (-10, 20), (-16, 19.5), (-21, 19), (-21, 13),
         (-21.5, 7), (-21, 0), (-21.5, -6), (-21, -12), (14, -12), (11, -15), (6, -14), (-9, -15), (-13, -10), (-18, -14),
         (16, 6), (13, 5), (4, 6), (1, 12), (-5, 13), (-8, 9), (-19, 3), (-4, -2), (12, -6), (17, -4), (-10, -4), (-16, -4)]
for i, (x, z) in enumerate(trees):
    s = 1.2 + 0.35 * ((i * 7) % 5) / 4
    prop(f"pine_{i}", PINE, float(x), 0.0, float(z), rot=i * 37.0, scale=(s, s * 1.15, s))

readable("wood_sign", 19.0, 0.0, 2.6, "Read the Signpost", "THE WHISTLING WOOD",
         ("THE WHISTLING WOOD\n\nNamed for the wind in the Old Oak, which whistles. Visitors are asked not to whistle back. It only "
          "encourages it.\n\nBeneath, in a different hand: \"WOLVES. Some of them dressed as relatives. Do not let them in.\"\n\n"
          "Beneath that, in a third hand, very small and very shaky: \"also there's a horse in my tent. help. - S\""),
         model=SIGN, rot=-90.0, set_flag="trout_c_sign")

# ============================================================================ the Old Oak
OX, OZ = -14.0, 6.0
prop("oak_trunk", "assets/models/env/oak_trunk.glb", OX, 0.0, OZ)
prop("oak_canopy", "assets/models/env/oak_canopy.glb", OX, 0.0, OZ, solid=False)
readable("oak_hollow", OX + 1.75, 0.0, OZ, "Listen at the Hollow", "The Old Oak's Hollow",
         ("A knot-hole the size of a fist, low on the trunk, worn smooth. As you lean close, the wind moves through the wood, and "
          "the hollow whistles.\n\nTwo notes. Low, then high. Sharp and short, the way a man whistles who has done it ten thousand "
          "times without thinking.\n\nSomewhere above you, in the branches, something large shifts its weight and snorts, as if "
          "answering.\n\nYou've heard that whistle before. Outside the Lantern Inn. Across a card table. It's Hollis's."),
         set_flag="trout_c_whistle")
npcs.append({"instance_id": "npc_trout_oak", "npc_id": "core:npc.trout", "pos": [OX, 11.45, OZ], "yaw": 90.0,
             "requires_flag": "trout_case", "hidden_flag": "oak_plugged"})
lights.append({"pos": [OX + 2.5, 3.0, OZ + 1.0], "color": [0.6, 0.8, 0.55], "radius": 9.0})

# ============================================================================ Steve's camp
SX, SZ = -2.0, -13.0
prop("tent", "assets/models/env/tent.glb", SX, 0.0, SZ)
box("tent_bedroll", WOOD, SX - 1.0, SX + 1.0, 0.0, 0.12, SZ - 0.6, SZ + 0.3, solid=False, uv=[0.8, 0.3])
fire("camp_fire", SX, SZ + 3.0)
for i, (x, z) in enumerate([(SX + 2.6, SZ + 0.4), (SX + 3.2, SZ + 1.2)]):
    prop(f"camp_crate_{i}", CRATE, x, 0.0, z, rot=i * 30.0)
npcs.append({"instance_id": "npc_steve", "npc_id": "core:npc.steve", "pos": [SX + 1.2, 0.0, SZ + 1.6], "yaw": 10.0,
             "requires_flag": "trout_case", "hidden_flag": "steve_in_town"})
readable("ransom_drafts", SX - 3.2, 0.0, SZ + 0.5, "Read the Notes Pinned to the Tree", "Crumpled Drafts",
         ("Seven sheets of paper, nailed to a pine one above the other, each one crossed out.\n\n"
          "1. \"Dear Sir. I have your horse. Sorry.\"\n"
          "2. \"WE have your horse.\" (There is only one person here.)\n"
          "3. \"WE HAVE YOUR HORSE.\"\n"
          "4. \"WE HAV YOUR HORS.\" (Margin note: more frightening if spelled wrong? check with night school)\n"
          "5. \"300 gold or you will never see her again.\" (Margin note: he will though. she keeps turning up. on the TENT.)\n"
          "6. \"Please come and get your horse.\"\n"
          "7. \"PLEASE come and get your horse she has eaten all my carrots and she was in the soup.\"\n\n"
          "On the back of every sheet, faintly, the printed grid of a Lantern Inn character sheet."),
         model=LECTERN, rot=90.0, set_flag="trout_c_drafts")
for i, (pos, a, b) in enumerate([((SX + 5.0, 0.0, SZ + 4.0), (SX + 5.0, 0.0, SZ + 1.0), (SX + 6.0, 0.0, SZ + 6.0)),
                                 ((SX - 4.5, 0.0, SZ + 4.5), (SX - 6.0, 0.0, SZ + 3.0), (SX - 3.0, 0.0, SZ + 6.0)),
                                 ((SX + 2.5, 0.0, SZ + 7.0), (SX, 0.0, SZ + 7.5), (SX + 4.0, 0.0, SZ + 7.0)),
                                 ((SX - 2.5, 0.0, SZ + 7.0), (SX - 4.0, 0.0, SZ + 6.5), (SX - 1.0, 0.0, SZ + 8.0))]):
    creature(f"camp_wolf_{i}", "core:enemy.grey_wolf", pos, a, b, requires_flag="trout_wood", group="camp_wolves",
             group_set_flag="steve_safe")

# ============================================================================ Grandmother's cottage (a ruin)
GX, GZ = 10.0, 14.0
box("cottage_floor", WOOD, GX - 3.0, GX + 3.0, 0.0, 0.04, GZ - 2.5, GZ + 2.5, solid=False, uv=[2, 2])
box("cottage_w", TIMBER, GX - 3.0, GX - 2.6, 0.0, 2.4, GZ - 2.5, GZ + 2.5)
box("cottage_n_a", TIMBER, GX - 3.0, GX - 0.8, 0.0, 1.6, GZ - 2.5, GZ - 2.1)
box("cottage_n_b", TIMBER, GX + 0.8, GX + 3.0, 0.0, 2.8, GZ - 2.5, GZ - 2.1)
box("cottage_e", TIMBER, GX + 2.6, GX + 3.0, 0.0, 1.2, GZ - 2.5, GZ + 2.5)
box("cottage_s", TIMBER, GX - 3.0, GX + 3.0, 0.0, 2.0, GZ + 2.1, GZ + 2.5)
box("cottage_bed", WOOD, GX + 0.6, GX + 2.4, 0.0, 0.55, GZ + 0.2, GZ + 2.0, uv=[0.7, 0.3])
readable("cottage_notice", GX - 1.6, 0.9, GZ + 1.6, "Read the Note on the Bed", "A Note, in Grandmotherly Handwriting",
         ("\"To whoever finds this:\n\nI have gone to live with my sister in Saltmere, where there are no wolves, only the "
          "unspeakable horrors of the deep, which at least have the decency not to wear your clothes.\n\nThe wolf is wearing my "
          "second-best nightgown. If you see him, tell him the bonnet does not suit him and it never did.\n\nThe red hood is "
          "in the wardrobe. My granddaughter has given up on it. She does archery now. She is very good. The wolf knows.\n\n"
          "Love, Granny\n\nP.S. A horse has been standing on my roof for two days. It is a very polite horse. I left it a "
          "carrot.\""),
         set_flag="trout_c_granny")
creature("granny_wolf", "core:enemy.granny_wolf", (GX, 0.0, GZ - 4.5), (GX - 3.0, 0.0, GZ - 5.0), (GX + 3.0, 0.0, GZ - 5.0),
         requires_flag="trout_wood")
interactables.append({"instance_id": "cottage_chest", "type": "chest", "model": "assets/models/props/treasure_chest.glb",
                      "pos": [GX - 1.8, 0.0, GZ - 1.0], "rot_y": 90.0, "locked": False, "fixed_items": ["core:item.red_hood"],
                      "loot_table": "core:loot.wolf"})

# A pair of wolves that live here regardless (the wood is dangerous even without a case)
creature("wood_wolf_0", "core:enemy.grey_wolf", (12.0, 0.0, -9.0), (9.0, 0.0, -10.0), (16.0, 0.0, -8.0))
creature("wood_wolf_1", "core:enemy.grey_wolf", (-12.0, 0.0, -7.0), (-15.0, 0.0, -8.0), (-9.0, 0.0, -6.0))
interactables.append({"instance_id": "wood_carrots", "type": "pickup", "item_id": "core:item.carrot", "qty": 3, "pos": [-6.4, 0.2, -9.2]})

region = {
    "schema_version": 1,
    "id": "core:map.whistling_wood",
    "display_name_key": "map.whistling_wood.name",
    "music": "assets/audio/music/old_road_theme.wav",
    "ambience": "assets/audio/ambience/forest_wind.wav",
    "sky_color": [40, 52, 50],
    "ambient_color": [0.42, 0.5, 0.42],
    "sun_direction": [0.3, 0.8, 0.2],
    "sun_color": [0.62, 0.66, 0.52],
    "fog_color": [0.2, 0.26, 0.22],
    "fog_density": 0.04,
    "weather": "",
    "spawns": {"wood_lane": {"pos": [20.0, 0.0, 0.0], "yaw_degrees": -90.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

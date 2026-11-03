#!/usr/bin/env python3
"""
Generates content/regions/seaside_house.json: "The Late Cindermaw", Grubnik Quillsby's seaside house in a hidden cove,
bought with a third of a dragon's hoard (quest core:quest.missing_third). Only reachable by Silas's boat (dialogue action
"travel" to spawn "seaside_landing"); not connected to the rest of the world on foot.

Region-local frame (build_world.py places it at SEASIDE_OFF):
  * A sandy cove x -16..16, z -20..18, cliffs all round, the sea to the south (z 14..26) with Silas's boat at a jetty.
  * The house x -8..8, z -16..-4: the Cushion Room (W) and the Shoe Room (E) at the front, Quillsby's office at the back,
    and the vault (NE corner of the office, locked: Quillsby carries the key).
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python tools/build_seaside.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "seaside_house.json")
STONE = "assets/models/env/wall_stone.glb"
TIMBER = "assets/models/env/wall_timber.glb"
WOOD = "assets/models/env/floor_wood.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
TORCH = "assets/models/props/wall_torch.glb"
QUEST = "core:quest.missing_third"
H = 3.6

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def wall_x(pid, z, x0, x1, y0, y1, gaps=(), model=TIMBER, t=0.4, door_h=2.6):
    cur = x0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, cur, a, y0, y1, z - t / 2, z + t / 2)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, a, b, y0 + door_h, y1, z - t / 2, z + t / 2)
        cur = b
    if x1 > cur:
        box(f"{pid}_end", model, cur, x1, y0, y1, z - t / 2, z + t / 2)


def wall_z(pid, x, z0, z1, y0, y1, gaps=(), model=TIMBER, t=0.4, door_h=2.6):
    cur = z0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, x - t / 2, x + t / 2, y0, y1, cur, a)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, x - t / 2, x + t / 2, y0 + door_h, y1, a, b)
        cur = b
    if z1 > cur:
        box(f"{pid}_end", model, x - t / 2, x + t / 2, y0, y1, cur, z1)


def torch(tid, x, y, z, rot):
    props.append({"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False,
                  "emitter": {"sprite": "assets/sprites/vfx/torch_flame.png", "offset": [0.0, 0.86, 0.0], "size": 0.45,
                              "light_color": [1.0, 0.66, 0.36], "light_radius": 7.5}})


def readable(iid, x, y, z, prompt, title, text, **extra):
    d = {"instance_id": iid, "type": "readable", "model": "", "pos": [x, y, z], "rot_y": 0.0, "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ the cove
box("cove_sand", COBBLE, -16.0, 16.0, -0.5, 0.0, -20.0, 14.0, solid=False, uv=[12, 13])
box("cove_sea_floor", COBBLE, -16.0, 16.0, -0.9, -0.45, 14.0, 26.0, uv=[12, 5])
props.append({"id": "cove_water", "model": "assets/models/env/harbour_water.glb", "pos": [0.0, -0.14, 20.0], "rot_y": 0.0,
              "scale": [0.85, 1.0, 0.6], "solid": False})
for pid, (x0, x1, z0, z1) in {"cliff_n": (-16.6, 16.6, -20.6, -19.4), "cliff_w": (-16.6, -15.4, -20.6, 26.6),
                              "cliff_e": (15.4, 16.6, -20.6, 26.6), "cliff_s": (-16.6, 16.6, 25.4, 26.6)}.items():
    box(pid, STONE, x0, x1, -0.9, 6.0 if pid != "cliff_s" else 1.4, z0, z1, uv=[10, 2])
for i, (x, z, w, h) in enumerate([(-12.5, 8.0, 1.6, 1.0), (11.0, 6.5, 1.2, 1.4), (-11.0, -1.0, 1.0, 0.7), (12.5, -12.0, 1.4, 0.9)]):
    box(f"rock_{i}", STONE, x - w / 2, x + w / 2, -0.2, h, z - w / 2, z + w / 2, uv=[0.5, 0.4])
# the jetty and Silas's boat
box("jetty", WOOD, -1.2, 1.2, -0.5, 0.0, 12.0, 21.0, uv=[1, 3])
for i, (x, z) in enumerate([(-1.35, 16.0), (1.35, 16.0), (-1.35, 20.8), (1.35, 20.8)]):
    box(f"jetty_pile_{i}", WOOD, x - 0.15, x + 0.15, -0.9, 0.5, z - 0.15, z + 0.15)
box("boat_hull", WOOD, 1.9, 3.3, -0.5, 0.25, 16.6, 20.6, uv=[1, 0.4])
box("boat_seat", WOOD, 1.9, 3.3, 0.25, 0.35, 18.4, 18.8, solid=False, uv=[0.6, 0.2])
npcs.append({"instance_id": "npc_silas_seaside", "npc_id": "core:npc.silas_gale", "pos": [-0.4, 0.0, 14.0], "yaw": 180.0})
readable("cove_sign", 2.2, 0.0, 9.0, "Read the Sign", "A Very Expensive Sign",
         "A sign of polished mahogany with gold-leaf letters:\n\nTHE LATE CINDERMAW\nPrivate Residence of G. Quillsby, Esq.\n"
         "NO DRAGONS\nNO CLERKS\nNO VISITORS\n(This means you.)\n\nSomeone has painted over 'LATE' in red and written 'VERY MUCH ALIVE'. The "
         "brushstrokes look like they were made with a claw.")

# ============================================================================ the house
X0, X1, Z0, Z1 = -8.0, 8.0, -16.0, -4.0
box("house_floor", WOOD, X0, X1, -0.4, 0.02, Z0, Z1, solid=False, uv=[6, 5])
box("house_roof", WOOD, X0 - 0.5, X1 + 0.5, H, H + 0.3, Z0 - 0.5, Z1 + 0.5, uv=[6, 5])
wall_x("ext_s", Z1, X0, X1, 0.0, H, gaps=[(-1.0, 1.0)])          # the front door (open: Quillsby left in a hurry)
wall_x("ext_n", Z0, X0, X1, 0.0, H)
wall_z("ext_w", X0, Z0, Z1, 0.0, H)
wall_z("ext_e", X1, Z0, Z1, 0.0, H)
wall_z("int_front", 0.0, -10.0, Z1, 0.0, H, gaps=[(-6.0, -4.8)])   # between the two front rooms
wall_x("int_mid", -10.0, X0, X1, 0.0, H, gaps=[(-5.0, -3.8), (2.0, 3.2)])
wall_z("vault_w", 4.0, Z0, -12.5, 0.0, H, gaps=[(-14.6, -13.4)])
wall_x("vault_s", -12.5, 4.0, X1, 0.0, H)
interactables.append({"instance_id": "quillsby_vault_door", "type": "door", "model": "assets/models/props/oak_door.glb", "pos": [4.0, 0.0, -14.0],
                      "rot_y": 90.0, "locked": True, "key_id": "core:item.quillsby_vault_key", "lock_difficulty": 25, "prompt": "Vault Door"})
torch("torch_cushion", -7.75, 1.9, -7.0, 90.0)
torch("torch_shoe", 7.75, 1.9, -7.0, -90.0)
torch("torch_office", -7.75, 1.9, -13.0, 90.0)
torch("torch_vault", 7.75, 1.9, -14.3, -90.0)

# Cushion Room (W): 1,200 silk cushions
for i, (x, z, w, h) in enumerate([(-6.5, -8.5, 1.2, 0.9), (-5.0, -6.0, 1.4, 1.3), (-2.0, -8.8, 1.6, 0.7), (-6.8, -5.0, 1.0, 0.5),
                                  (-3.0, -5.6, 1.2, 1.0), (-1.4, -6.8, 0.8, 0.5)]):
    box(f"cushions_{i}", WOOD, x - w / 2, x + w / 2, 0.0, h, z - w / 2, z + w / 2, solid=False, uv=[0.4, 0.3])
readable("cushion_ledger", -4.0, 0.0, -9.4, "Read the Inventory", "Cushion Inventory (Partial)",
         "CUSHIONS, SILK: 1,200\nCUSHIONS, VELVET: 340\nCUSHIONS, 'FOR SITTING ON CUSHIONS': 12\nCUSHION, ONE (1), EMBROIDERED 'GRUBNIK IS A GOOD BOY': "
         "1, a gift from Mother\n\nTotal: 2,104 gold of the dragon's money, and not one chair in the house.")
# Shoe Room (E): 300 pairs of bespoke kobold shoes
for i in range(5):
    box(f"shoe_rack_{i}", WOOD, 1.0 + i * 1.3, 1.9 + i * 1.3, 0.0, 2.0, -9.6, -9.2, uv=[0.3, 0.7])
readable("shoe_room", 4.0, 0.0, -8.4, "Look at the Shoes", "The Shoe Room",
         "Racks and racks of tiny shoes, floor to ceiling: buckled, beribboned, patent leather, one pair entirely of gold with little ruby "
         "toes. Each pair has a label: 'TUESDAY', 'COURT', 'GLOATING', 'GLOATING (FORMAL)'.\n\nThree hundred pairs. Kobolds have four toes. "
         "These were all made to measure. The cobbler's bill alone was worth a small village.", sanity=2)
# Quillsby's office (back)
box("office_desk", WOOD, -3.0, 1.0, 0.0, 0.85, -14.6, -13.4, uv=[1.5, 0.4])
readable("quillsby_letter", -1.0, 0.85, -14.0, "Read the Letter on the Desk", "A Letter, Half-Written",
         "To the Royal Bureau of Records, Name Change Department\n\nDear Sirs,\n\nI wish to formally change my name from Grubnik Quillsby to "
         "Cindermaw the Elder, as the previous holder of the name is legally deceased and will not be needing it. I enclose the fee "
         "(eleven gold, one sheep, one apology).\n\nP.S. Please also transfer the title 'Terror of the Eastern Mountains'.\n\n[The letter "
         "stops. There's a large ink blot, as if the writer heard something enormous land outside.]")
creature("kobold_cushion_0", "core:enemy.kobold_bookkeeper", (-5.5, 0.0, -7.0), (-6.5, 0.0, -7.0), (-2.0, 0.0, -7.0))
creature("kobold_cushion_1", "core:enemy.kobold_bookkeeper", (-2.5, 0.0, -5.0), (-6.0, 0.0, -5.0), (-1.5, 0.0, -5.0))
creature("kobold_shoe_0", "core:enemy.kobold_bookkeeper", (3.0, 0.0, -6.0), (1.5, 0.0, -6.0), (6.5, 0.0, -6.0))
creature("kobold_shoe_1", "core:enemy.kobold_bookkeeper", (6.0, 0.0, -8.0), (1.5, 0.0, -8.0), (6.5, 0.0, -8.0))
creature("quillsby_cornered", "core:enemy.quillsby_cornered", (-2.0, 0.0, -12.0), (-5.0, 0.0, -12.0), (2.0, 0.0, -12.0),
         requires_flag="missing_third_open", group="quillsby", group_quest_id=QUEST, group_set_stage=30, group_set_flag="quillsby_caught")
# the vault: the missing third of the hoard
interactables.append({"instance_id": "missing_third_hoard", "type": "quest_pedestal", "model": "assets/models/props/treasure_chest.glb",
                      "pos": [6.0, 0.0, -14.3], "rot_y": -90.0, "prompt": "Recover the Missing Third of the Hoard", "quest_id": QUEST, "set_stage": 40,
                      "grant_items": ["core:item.hoard_third"], "narration": ["story.missing_third.vault"]})

region = {
    "schema_version": 1,
    "id": "core:map.seaside_house",
    "display_name_key": "map.seaside_house.name",
    "music": "assets/audio/music/old_road_theme.wav",
    "ambience": "assets/audio/ambience/forest_wind.wav",
    "sky_color": [34, 30, 52],
    "ambient_color": [0.42, 0.4, 0.5],
    "sun_direction": [-0.3, 0.7, 0.4],
    "sun_color": [0.55, 0.45, 0.5],
    "fog_color": [0.16, 0.14, 0.22],
    "fog_density": 0.03,
    "weather": "",
    "spawns": {"seaside_landing": {"pos": [0.0, 0.0, 11.0], "yaw_degrees": 180.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

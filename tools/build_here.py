#!/usr/bin/env python3
"""
Generates content/regions/here.json: "Here", the city whose name was eaten (Chapter One: The City Formerly Known As).
One of the seven cities the Archivists struck off every map during the Great Silence. Reached only by the dusk road
from the Old Road (a "travel" milestone there, dusk to dawn). A blockout: simple shapes, real collision and lights,
meant to be rebuilt in the Blender level editor later.

Region-local frame (build_world.py places it at HERE_OFF), north is -z:
  * The Gate (south, z 28..40): the arrival road, the road back, Gatekeeper Ottoline Pell's customs booth, the inner
    gate (locked until you hold a Visitor's Permit).
  * The Market of the Unwritten (centre): stalls, the dry fountain, Butt-Butt; the midnight market stall.
  * West: the Baker's house and the ruined bakery. East: the Cartographer's house.
  * North-east: the bell tower, a stair up the outside to a lookout at 7 m.
  * North: the Archive Tower (z -38..-24), locked; inside, the Hunger's Mouths, a stair to the gallery (4 m) where the
    Last Archivist waits at the empty plinth.
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python3 tools/build_here.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "here.json")
STONE = "assets/models/env/wall_stone.glb"
TIMBER = "assets/models/env/wall_timber.glb"
WOOD = "assets/models/env/floor_wood.glb"
FLAGS = "assets/models/env/floor_flagstones.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
ROOF = "assets/models/env/floor_roof_slate_mossy.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"
Q = "core:quest.ch1_here"
NIGHT = [18.0, 7.0]          # the city is solid from dusk to dawn

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def wall_x(pid, z, x0, x1, y0, y1, gaps=(), model=STONE, t=0.4, door_h=2.8):
    cur = x0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, cur, a, y0, y1, z - t / 2, z + t / 2)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, a, b, y0 + door_h, y1, z - t / 2, z + t / 2)
        cur = b
    if x1 > cur:
        box(f"{pid}_end", model, cur, x1, y0, y1, z - t / 2, z + t / 2)


def wall_z(pid, x, z0, z1, y0, y1, gaps=(), model=STONE, t=0.4, door_h=2.8):
    cur = z0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, x - t / 2, x + t / 2, y0, y1, cur, a)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, x - t / 2, x + t / 2, y0 + door_h, y1, a, b)
        cur = b
    if z1 > cur:
        box(f"{pid}_end", model, x - t / 2, x + t / 2, y0, y1, cur, z1)


def house(pid, x0, x1, z0, z1, h=3.4, door=None, model=TIMBER, roof=True):
    """A simple house; door = (side, a, b): side in 'n','s','e','w', a..b along that wall."""
    side, a, b = door or ("-", 0.0, 0.0)          # no door: a closed house
    wall_x(f"{pid}_n", z0, x0, x1, 0, h, gaps=[(a, b)] if side == "n" else (), model=model)
    wall_x(f"{pid}_s", z1, x0, x1, 0, h, gaps=[(a, b)] if side == "s" else (), model=model)
    wall_z(f"{pid}_w", x0, z0, z1, 0, h, gaps=[(a, b)] if side == "w" else (), model=model)
    wall_z(f"{pid}_e", x1, z0, z1, 0, h, gaps=[(a, b)] if side == "e" else (), model=model)
    box(f"{pid}_floor", WOOD, x0, x1, -0.4, 0.02, z0, z1, solid=False)
    if roof:
        box(f"{pid}_roof", ROOF, x0 - 0.4, x1 + 0.4, h, h + 0.35, z0 - 0.4, z1 + 0.4)


def torch(tid, x, y, z, rot):
    props.append({"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False})


def lamp(lid, x, z, color=(0.7, 0.75, 1.0), radius=9.0, y=2.6):
    lights.append({"pos": [x, y, z], "color": list(color), "radius": radius})


def readable(iid, x, y, z, prompt, title, text, **extra):
    d = {"instance_id": iid, "type": "readable", "model": "", "pos": [x, y, z], "rot_y": 0.0, "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def npc(iid, nid, x, z, yaw, **extra):
    d = {"instance_id": iid, "npc_id": nid, "pos": [x, 0.0, z], "yaw": yaw}
    d.update(extra)
    npcs.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ ground and city walls
box("here_ground", FLAGS, -30.0, 30.0, -0.5, 0.0, -40.0, 28.0, solid=False, uv=[22, 26])
box("here_road", COBBLE, -4.0, 4.0, -0.5, 0.0, 28.0, 44.0, solid=False, uv=[3, 6])
box("here_verge_w", FLAGS, -30.0, -4.0, -0.5, -0.02, 28.0, 44.0, solid=False, uv=[10, 6])
box("here_verge_e", FLAGS, 4.0, 30.0, -0.5, -0.02, 28.0, 44.0, solid=False, uv=[10, 6])
wall_x("citywall_n", -40.0, -30.0, 30.0, 0, 7.0, t=1.2)
wall_z("citywall_w", -30.0, -40.0, 44.0, 0, 7.0, t=1.2)
wall_z("citywall_e", 30.0, -40.0, 44.0, 0, 7.0, t=1.2)
box("fogbank_s", STONE, -30.0, 30.0, 0.0, 7.0, 43.4, 44.6)       # the fog you came through: a wall you can't see past
# the gatehouse wall across the road, with the inner gate
wall_x("gatewall", 28.0, -30.0, 30.0, 0, 5.0, gaps=[(-2.0, 2.0)], t=1.0, door_h=4.0)
box("gatetower_w", STONE, -4.0, -2.0, 0.0, 6.5, 27.0, 29.0)
box("gatetower_e", STONE, 2.0, 4.0, 0.0, 6.5, 27.0, 29.0)
interactables.append({"instance_id": "here_inner_gate", "type": "door", "model": "assets/models/props/iron_gate.glb", "pos": [0.0, 0.0, 28.0],
                      "rot_y": 0.0, "scale": [2.2, 1.4, 1.0], "locked": True, "key_id": "core:item.here_permit", "lock_difficulty": 99,
                      "prompt": "City Gate"})
# Ottoline's customs booth, outside the gate
box("booth_desk", WOOD, -8.0, -5.0, 0.0, 1.05, 30.4, 31.2, uv=[1.2, 0.4])
box("booth_back", TIMBER, -8.2, -4.8, 0.0, 2.8, 29.0, 29.3)
box("booth_roof", ROOF, -8.6, -4.4, 2.8, 3.1, 29.0, 31.6)
npc("npc_here_gatekeeper", "core:npc.here_gatekeeper", -6.5, 30.0, 0.0)
readable("here_customs_sign", -9.0, 0.0, 31.0, "Read the Sign", "CUSTOMS",
         "CUSTOMS\n[CITY NAME HERE] MUNICIPAL BOUNDARY\n\nOPEN: DUSK TO DAWN\nCLOSED: DAWN TO DUSK\n\nAll visitors must present Form 1 "
         "(Entry, Municipal, Non-Existent), correctly completed, in ink.\n\nNo pencils.\nNo exceptions.\nNo one has come in four hundred years. "
         "We are VERY ready for you.")
interactables.append({"instance_id": "here_road_back", "type": "travel", "model": "", "pos": [0.0, 0.0, 40.5], "rot_y": 0.0,
                      "prompt": "Follow the Road Back to the Old Road", "travel_spawn": "road_dusk"})
lamp("lamp_gate", 0.0, 31.5, (0.8, 0.8, 1.0), 10.0)
torch("torch_gate_w", -2.6, 2.2, 29.1, 0.0)
torch("torch_gate_e", 2.6, 2.2, 29.1, 0.0)

# ============================================================================ the Market of the Unwritten (centre)
box("fountain_ring", STONE, -2.6, 2.6, 0.0, 0.7, 2.4, 7.6, uv=[2, 0.3])
box("fountain_pillar", STONE, -0.5, 0.5, 0.0, 2.4, 4.5, 5.5)
readable("here_fountain", 0.0, 0.7, 7.8, "Look into the Fountain", "The Dry Fountain",
         "The fountain is dry. Carved round its rim, worn almost smooth, are the words: 'WELCOME TO ' and then a long gouge where "
         "a name used to be, as if something bit it out of the stone.\n\nSomeone has chalked underneath, in big wobbly letters: "
         "'BUTT-BUTT WOZ ERE'.")
for i, (x, z) in enumerate([(-10.0, 0.0), (-10.0, 10.0), (10.0, 0.0), (10.0, 10.0), (-5.0, -6.0), (5.0, -6.0)]):
    box(f"stall_{i}_counter", WOOD, x - 1.6, x + 1.6, 0.0, 1.0, z - 0.6, z + 0.6, uv=[1.2, 0.4])
    box(f"stall_{i}_roof", ROOF, x - 1.9, x + 1.9, 2.5, 2.7, z - 1.4, z + 0.9, solid=False)
    for j, px in enumerate((x - 1.7, x + 1.7)):
        box(f"stall_{i}_post{j}", WOOD, px - 0.08, px + 0.08, 0.0, 2.5, z - 1.3, z - 1.14)
npc("npc_here_butt_butt", "core:npc.here_butt_butt", 3.2, 9.0, 160.0, hours=NIGHT)
npc("npc_here_hat", "core:npc.here_person_in_hat", 10.0, 1.6, 180.0, hours=NIGHT)
npc("npc_here_night_merchant", "core:npc.here_night_merchant", -5.0, -4.6, 180.0, hours=[0.0, 2.0])
readable("here_midnight_sign", -5.0, 0.0, -7.6, "Read the Stall Sign", "The Midnight Market",
         "THE MIDNIGHT MARKET\nOpen from Midnight until Two\n(Closed at all other times, including yesterday)\n\nToday's Specials:\n"
         "- Yesterdays (slightly used)\n- Lost Umbrellas (all colours, all owners)\n- One (1) Tuesday\n- Names (NOT FOR SALE. Do not ask.)")
for i, (x, z) in enumerate([(-6.0, 12.0), (6.0, -2.0), (-14.0, -6.0), (14.0, 14.0)]):
    lamp(f"lamp_market_{i}", x, z, (0.75, 0.78, 1.0), 9.0)

# ============================================================================ west: the Baker's house and the ruined bakery
house("baker_house", -24.0, -16.0, 2.0, 10.0, door=("e", 5.0, 7.0))
npc("npc_here_baker", "core:npc.here_baker", -14.0, 6.0, -90.0, hours=NIGHT)
torch("torch_baker", -15.7, 2.1, 4.0, -90.0)
house("bakery", -24.0, -16.0, -10.0, -2.0, door=("e", -7.0, -5.0), roof=False)   # the roof fell in long ago
box("bakery_oven", STONE, -23.6, -21.0, 0.0, 1.8, -9.6, -7.0)
box("bakery_rubble_0", STONE, -20.0, -18.6, 0.0, 0.6, -4.4, -3.2, uv=[0.5, 0.3])
box("bakery_rubble_1", ROOF, -22.5, -20.2, 0.0, 0.35, -5.0, -3.0, solid=False, uv=[0.8, 0.3])
interactables.append({"instance_id": "here_recipe", "type": "pickup", "model": "", "pos": [-22.0, 0.0, -8.4],
                      "item_id": "core:item.here_recipe", "qty": 1, "prompt": "Take the Recipe Card"})
lamp("lamp_bakery", -20.0, -6.0, (0.9, 0.7, 0.5), 7.0)

# ============================================================================ east: the Cartographer's house
house("carto_house", 16.0, 24.0, 2.0, 10.0, door=("w", 5.0, 7.0))
npc("npc_here_cartographer", "core:npc.here_cartographer", 14.4, 6.0, 90.0, hours=NIGHT)
box("carto_table", WOOD, 18.0, 21.0, 0.0, 0.9, 4.0, 6.0, uv=[1.2, 0.4])
torch("torch_carto", 15.7, 2.1, 4.0, 90.0)

# ============================================================================ houses along the streets (closed, with chalked walls)
for i, (x0, x1, z0, z1) in enumerate([(-24, -16, 14, 22), (16, 24, 14, 22), (-24, -16, -22, -14), (-13, -7, 14, 22), (7, 13, 14, 22)]):
    house(f"house_{i}", x0, x1, z0, z1, door=None)
readable("here_verse_1", -12.8, 1.2, 18.0, "Read the Chalk on the Wall", "Chalked Verse (One)",
         "In a child's chalk, big and careful, only legible by moonlight:\n\n'OUR TOWN IS BY THE BENDING RIVER,\nOUR BREAD IS WARM, OUR BELLS ARE "
         "SILVER...'\n\n(and a drawing of a bell with a face)", hours=NIGHT, set_flag="here_verse1")
readable("here_verse_2", 16.0, 1.2, -18.0, "Read the Chalk on the Wall", "Chalked Verse (Two)",
         "'...WE NEVER LOCK OUR DOORS AT NIGHT,\nWE SING OUR NAME TO KEEP IT RIGHT...'\n\n(and a drawing of a door, open, with a smiley sun)",
         hours=NIGHT, set_flag="here_verse2")
readable("here_verse_3", -26.4, 1.2, 0.0, "Read the Chalk on the Wall", "Chalked Verse (Three)",
         "'...AND IF YOU FORGET, THE BELL WILL TELL:\nWE ARE ...'\n\nThe last word has been rubbed out, hard, by something that wasn't a hand. "
         "Underneath, the same child has written: 'I DIDN'T DO THAT. - BUTT-BUTT'.", hours=NIGHT, set_flag="here_verse3")
for i, (x, z) in enumerate([(-20.0, 12.0), (20.0, 12.0), (-20.0, -12.0), (0.0, 20.0)]):
    lamp(f"lamp_street_{i}", x, z, (0.75, 0.78, 1.0), 8.0)
# Death and Taxes: a ghost tax inspector still counting the city's chimneys, and the register at the customs post
npc("npc_here_inspector", "core:npc.here_inspector", -20.0, 23.2, 180.0, hours=NIGHT)
readable("here_hearth_register", -7.8, 1.05, 30.9, "Read the Register of Hearths", "Register of Hearths (Here)",
         "REGISTER OF HEARTHS, kept at the Municipal Boundary\n\nOne copper per hearth per year, payable to the Inspector of Hearths.\n\n"
         "Houses: 41. Hearths: 47. (The bakery has three.)\n\nAt the bottom, in a different, very neat hand: 'Inspector's residence, "
         "Gatehouse Lane: one hearth. EXEMPT (the Inspector does not tax himself).' Someone has crossed out EXEMPT and written, in "
         "Ottoline's handwriting: 'NOT A REAL EXEMPTION. I CHECKED.'", set_flag="here_hearths_read")

# ============================================================================ north-east: the bell tower
box("tower_body", STONE, 20.0, 26.0, 0.0, 7.0, -26.0, -20.0, uv=[2.4, 2.4])
box("tower_walkway", STONE, 17.5, 20.0, 0.0, 7.0, -26.0, -20.0, uv=[1, 2.4])
props.append({"id": "tower_stairs", "model": STAIRS, "pos": [18.75, 0.0, -13.0], "rot_y": 0.0, "scale": [2.5, 7.0, 14.0],
              "solid": False, "ramp": "-z"})
box("tower_top", FLAGS, 17.5, 26.0, 6.98, 7.06, -26.0, -20.0, solid=False, uv=[3, 2])
for pid, (x0, x1, z0, z1) in {"parapet_n": (17.5, 26.0, -26.3, -26.0), "parapet_e": (26.0, 26.3, -26.3, -19.7),
                              "parapet_s": (20.0, 26.3, -20.0, -19.7), "parapet_w": (17.2, 17.5, -26.3, -19.7)}.items():
    box(pid, STONE, x0, x1, 7.0, 7.9, z0, z1, uv=[1, 0.3])
for i, (x, z) in enumerate([(20.3, -25.7), (25.7, -25.7), (25.7, -20.3), (20.3, -20.3)]):
    box(f"tower_post_{i}", STONE, x - 0.25, x + 0.25, 7.0, 10.0, z - 0.25, z + 0.25)
box("tower_belfry", ROOF, 19.8, 26.2, 10.0, 10.4, -26.2, -19.8)
box("tower_bell", "assets/models/env/wall_stone.glb", 22.3, 23.7, 8.2, 9.8, -23.7, -22.3, solid=False, uv=[0.6, 0.6])
readable("here_tower_view", 21.5, 7.0, -21.2, "Look Out over the City", "From the Bell Tower",
         "You lean on the parapet. Under the moon, the streets of Here spread out below you, and for the first time you see their shape: "
         "not a grid, not a tangle, but letters. The streets spell something, the way a river spells a valley.\n\nYou trace it with your "
         "finger, street by street, and hold it in your head before it can slip away.\n\nThe Cartographer will want to hear about this.",
         hours=NIGHT, set_flag="here_tower_view")
lamp("lamp_tower", 22.0, -23.0, (0.8, 0.85, 1.0), 9.0, y=8.0)

# ============================================================================ north: the Archive Tower
AX0, AX1, AZ0, AZ1, AH = -10.0, 10.0, -38.0, -24.0, 9.0
box("archive_floor", FLAGS, AX0, AX1, -0.4, 0.02, AZ0, AZ1, solid=False, uv=[6, 4])
wall_x("archive_s", AZ1, AX0, AX1, 0, AH, gaps=[(-1.2, 1.2)])
wall_x("archive_n", AZ0, AX0, AX1, 0, AH)
wall_z("archive_w", AX0, AZ0, AZ1, 0, AH)
wall_z("archive_e", AX1, AZ0, AZ1, 0, AH)
box("archive_roof", ROOF, AX0 - 0.5, AX1 + 0.5, AH, AH + 0.4, AZ0 - 0.5, AZ1 + 0.5)
interactables.append({"instance_id": "here_archive_door", "type": "door", "model": "assets/models/props/oak_door.glb", "pos": [0.0, 0.0, AZ1],
                      "rot_y": 0.0, "locked": True, "key_id": "core:item.here_archive_key", "lock_difficulty": 99, "prompt": "Archive Door"})
readable("here_archive_plaque", 2.4, 1.4, AZ1 + 0.3, "Read the Plaque", "The Archive",
         "THE ARCHIVE OF [CITY NAME HERE]\nWherein Is Kept the Name\n\nThe brass where the name should be is chewed, like a pencil end.")
# the hall: shelves, the Mouths
for i, x in enumerate((-6.0, -2.0, 2.0, 6.0)):
    box(f"archive_shelf_{i}", "assets/models/props/bookshelf_prop.glb", x - 0.3, x + 0.3, 0.0, 2.6, -31.0, -27.0, uv=[1, 1])
creature("here_mouth_0", "core:enemy.here_mouth", (-4.0, 0.0, -29.0), (-8.0, 0.0, -29.0), (0.0, 0.0, -29.0))
creature("here_mouth_1", "core:enemy.here_mouth", (4.0, 0.0, -29.0), (0.0, 0.0, -29.0), (8.0, 0.0, -29.0))
creature("here_mouth_2", "core:enemy.here_mouth", (0.0, 0.0, -34.0), (-6.0, 0.0, -34.0), (6.0, 0.0, -34.0))
creature("here_unsaying", "core:enemy.here_unsaying", (0.0, 0.0, -30.0), (-4.0, 0.0, -30.0), (4.0, 0.0, -30.0),
         requires_flag="here_spoken", group="here_unsaying", group_quest_id=Q, group_set_stage=90, group_set_flag="here_unsaying_down")
# the gallery: a stair up the west wall to a floor at 4 m over the north end
props.append({"id": "archive_stairs", "model": STAIRS, "pos": [-8.6, 0.0, -28.5], "rot_y": 0.0, "scale": [2.4, 4.0, 7.0],
              "solid": False, "ramp": "-z"})
box("archive_gallery", WOOD, AX0 + 0.2, AX1 - 0.2, 3.7, 4.0, AZ0 + 0.2, -32.0, uv=[6, 2])
box("archive_gallery_rail", WOOD, -7.4, AX1 - 0.2, 4.0, 4.9, -32.1, -31.9, uv=[5, 0.3])
box("archive_plinth", STONE, -0.6, 0.6, 4.0, 5.1, -36.6, -35.4)
npc("npc_here_echo", "core:npc.here_echo", 2.2, -35.0, 180.0)
for i, (x, z, y) in enumerate([(-6.0, -27.0, 2.6), (6.0, -27.0, 2.6), (0.0, -35.0, 6.4)]):
    lamp(f"lamp_archive_{i}", x, z, (0.65, 0.7, 1.0), 9.0, y=y)
torch("torch_archive_w", -9.75, 2.2, -30.0, 90.0)
torch("torch_archive_e", 9.75, 2.2, -30.0, -90.0)

region = {
    "schema_version": 1,
    "id": "core:map.here",
    "display_name_key": "map.here.name",
    "music": "assets/audio/music/vault_lullaby.wav",
    "ambience": "assets/audio/ambience/forest_wind.wav",
    "sky_color": [30, 28, 46],
    "ambient_color": [0.36, 0.36, 0.48],
    "sun_direction": [-0.3, 0.8, -0.3],
    "sun_color": [0.45, 0.45, 0.6],
    "fog_color": [0.17, 0.16, 0.24],
    "fog_density": 0.045,
    "weather": "dust",
    "spawns": {"here_gate": {"pos": [0.0, 0.0, 36.0], "yaw_degrees": 180.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

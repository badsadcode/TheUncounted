#!/usr/bin/env python3
"""
Generates content/regions/saltmere.json: Saltmere Docks and the Sunken Chapel beneath them, north of Bellwether.

Region-local frame (build_world.py places it at DOCKS_OFF; local z = +22 is Bellwether's north wall):
  * The quay x -20..20, z -10..21.4 (cobbles), the harbour beyond (shallow water over a sea floor) to z -34, two piers.
  * The Drowned Lantern (tavern, west), the harbourmaster's post, Gale & Sons Fish Co. (warehouse, east).
  * Inside the warehouse, a gated stairwell goes down 5.6 m to the Sunken Chapel (x 2..19, z -22..-6, floor y -5.6).
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python tools/build_docks.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "saltmere.json")
STONE = "assets/models/env/wall_stone.glb"
TIMBER = "assets/models/env/wall_timber.glb"
CRYPT = "assets/models/env/wall_crypt.glb"
WOOD = "assets/models/env/floor_wood.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"
LECTERN = "assets/models/props/lectern_ledger.glb"
PILLAR = "assets/models/env/pillar_stone.glb"
QUEST = "core:quest.saltmere"
CY = -5.6  # chapel floor

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def wall_x(pid, z, x0, x1, y0, y1, gaps=(), model=TIMBER, t=0.6, door_h=2.8):
    cur = x0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, cur, a, y0, y1, z - t / 2, z + t / 2)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, a, b, y0 + door_h, y1, z - t / 2, z + t / 2)
        cur = b
    if x1 > cur:
        box(f"{pid}_end", model, cur, x1, y0, y1, z - t / 2, z + t / 2)


def wall_z(pid, x, z0, z1, y0, y1, gaps=(), model=TIMBER, t=0.6, door_h=2.8):
    cur = z0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, x - t / 2, x + t / 2, y0, y1, cur, a)
        if y0 + door_h < y1:
            box(f"{pid}_lintel{i}", model, x - t / 2, x + t / 2, y0 + door_h, y1, a, b)
        cur = b
    if z1 > cur:
        box(f"{pid}_end", model, x - t / 2, x + t / 2, y0, y1, cur, z1)


def prop(pid, model, x, y, z, rot=0.0, scale=(1, 1, 1), solid=True):
    props.append({"id": pid, "model": model, "pos": [x, y, z], "rot_y": rot, "scale": list(scale), "solid": solid})


def torch(tid, x, y, z, rot, eldritch=False):
    props.append({"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False,
                  "emitter": {"sprite": "assets/sprites/vfx/spell_ink.png" if eldritch else "assets/sprites/vfx/torch_flame.png",
                              "offset": [0.0, 0.86, 0.0], "size": 0.34 if eldritch else 0.38,
                              "light_color": [0.35, 1.0, 0.6] if eldritch else [1.0, 0.66, 0.32], "light_radius": 6.5}})


def light(x, y, z, color, r):
    lights.append({"pos": [x, y, z], "color": color, "radius": r})


def readable(iid, x, y, z, prompt, title, text, model="", rot=0.0, **extra):
    d = {"instance_id": iid, "type": "readable", "model": model, "pos": [x, y, z], "rot_y": rot, "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ the quay and the harbour
# Quay cobbles, leaving a hole for the warehouse stairwell (x 14..17, z -4..4).
for pid, (x0, x1, z0, z1) in {"quay_w": (-20.0, 14.0, -10.0, 21.4), "quay_e": (17.0, 20.0, -10.0, 21.4),
                              "quay_s": (14.0, 17.0, 4.0, 21.4), "quay_n": (14.0, 17.0, -10.0, -4.0)}.items():
    box(pid, COBBLE, x0, x1, -0.5, 0.0, z0, z1, solid=False, uv=[round((x1 - x0) / 2.2, 1), round((z1 - z0) / 2.2, 1)])
box("sea_floor", COBBLE, -20.0, 20.0, -0.9, -0.4, -34.0, -10.0, uv=[14, 9])
props.append({"id": "harbour_water", "model": "assets/models/env/harbour_water.glb", "pos": [0.0, -0.14, -22.0], "rot_y": 0.0,
              "scale": [0.84, 1.0, 1.0], "solid": False})
box("bound_w", STONE, -20.6, -19.4, -0.9, 4.5, -34.0, 21.4)
box("bound_e", STONE, 19.4, 20.6, -0.9, 4.5, -34.0, 21.4)
box("sea_wall", STONE, -20.6, 20.6, -0.9, 1.0, -34.6, -33.4)
# Quay edge: a low timber kerb with gaps where the piers and a slipway meet it (you can wade; it's shallow)
for i, (x0, x1) in enumerate([(-20.0, -12.2), (-8.8, -2.0), (2.0, 7.8), (11.2, 20.0)]):
    box(f"kerb_{i}", TIMBER, x0, x1, 0.0, 0.5, -10.25, -9.95)
# Piers
box("pier_a", WOOD, -12.0, -9.0, -0.5, 0.0, -26.0, -10.0, uv=[1.2, 6])
box("pier_b", WOOD, 8.0, 11.0, -0.5, 0.0, -22.0, -10.0, uv=[1.2, 5])
for i, (x, z) in enumerate([(-12.2, -14), (-8.8, -14), (-12.2, -20), (-8.8, -20), (-12.2, -25.8), (-8.8, -25.8), (7.8, -16), (11.2, -16), (7.8, -21.8), (11.2, -21.8)]):
    box(f"pile_{i}", WOOD, x - 0.15, x + 0.15, -0.9, 0.5, z - 0.15, z + 0.15)
# Moored boats
for i, (x, z, w, d) in enumerate([(-15.5, -15.0, 1.4, 4.0), (-5.0, -14.0, 1.3, 3.6), (14.5, -14.5, 1.4, 4.2)]):
    box(f"boat_{i}_hull", WOOD, x - w / 2, x + w / 2, -0.5, 0.25, z - d / 2, z + d / 2, uv=[1, 0.4])
    box(f"boat_{i}_seat", WOOD, x - w / 2, x + w / 2, 0.25, 0.35, z - 0.2, z + 0.2, solid=False, uv=[0.6, 0.2])
# Out in the fog: something enormous, very still
prop("tentacle_far_a", "assets/models/env/tentacle_a.glb", -13.0, -0.4, -31.5, rot=30.0, scale=(1.4, 1.4, 1.4), solid=False)
prop("tentacle_far_b", "assets/models/env/tentacle_b.glb", 13.0, -0.4, -32.0, rot=200.0, scale=(1.5, 1.5, 1.5), solid=False)
prop("tentacle_near", "assets/models/env/tentacle_b.glb", -2.5, -0.4, -29.0, rot=110.0, scale=(0.55, 0.55, 0.55), solid=False)
# Lamp posts along the quay
for i, (x, z) in enumerate([(-6.0, -8.6), (6.0, -8.6), (-6.0, 4.0), (5.5, 4.0), (0.0, 15.0)]):
    box(f"lamp_post_{i}", TIMBER, x - 0.12, x + 0.12, 0.0, 2.6, z - 0.12, z + 0.12)
    torch(f"lamp_{i}", x, 2.0, z + 0.2, 0.0)
for i, (x, z) in enumerate([(-3.0, 9.0), (-2.4, 9.8), (3.8, 11.0), (12.0, -7.5), (-17.0, -6.0), (-16.2, -6.6)]):
    prop(f"crate_{i}", "assets/models/props/wooden_crate.glb", x, 0.0, z, rot=i * 23.0)

# ============================================================================ The Drowned Lantern (tavern)
TX0, TX1, TZ0, TZ1 = -19.4, -9.0, 2.0, 14.0
wall_z("tav_e", TX1, TZ0, TZ1, 0.0, 3.8, gaps=[(6.6, 8.6)])
wall_x("tav_s", TZ0, TX0, TX1, 0.0, 3.8)
wall_x("tav_n", TZ1, TX0, TX1, 0.0, 3.8)
box("tav_roof", WOOD, TX0, TX1 + 0.3, 3.8, 4.1, TZ0 - 0.3, TZ1 + 0.3, uv=[4, 4])
box("tav_floor", WOOD, TX0, TX1, 0.0, 0.03, TZ0, TZ1, solid=False, uv=[4, 4])
box("tav_bar", WOOD, -18.6, -14.0, 0.0, 1.05, 12.2, 13.0, uv=[2, 0.4])
for i, (x, z) in enumerate([(-14.0, 5.0), (-11.5, 9.5)]):
    box(f"tav_table_{i}", WOOD, x - 0.9, x + 0.9, 0.72, 0.82, z - 0.6, z + 0.6, uv=[1, 0.2])
    box(f"tav_table_{i}_leg", WOOD, x - 0.1, x + 0.1, 0.0, 0.72, z - 0.1, z + 0.1, solid=False)
light(-14.0, 3.0, 8.0, [1.0, 0.6, 0.35], 10.0)
torch("torch_tavern", -18.95, 2.0, 8.0, 90.0)
readable("tavern_sign", -8.4, 0.0, 9.6, "Read the Tavern Sign", "The Drowned Lantern",
         ("THE DROWNED LANTERN\nAles, Chowder, Lodgings\nPROP. M. BRINE\n\nUnderneath, a smaller sign, newer, nailed on crooked:\n\n"
          "\"PATRONS ARE KINDLY REMINDED NOT TO SAY THEIR NAMES ON THE PREMISES.\nIt only encourages it.\""), model=LECTERN, rot=-90.0)
npcs.append({"instance_id": "npc_brine", "npc_id": "core:npc.mother_brine", "pos": [-16.0, 0.0, 11.4], "yaw": 180.0})
npcs.append({"instance_id": "npc_pickering", "npc_id": "core:npc.professor_pickering", "pos": [-12.0, 0.0, 4.2], "yaw": 60.0})
readable("pickering_notes", -14.0, 0.95, 5.0, "Read the Professor's Notes", "Field Notes, Prof. A. Pickering (Collegium, Dept. of Unusual Studies)",
         ("Day 3. The fishermen will not say their names. Not in the tavern, not on the boats, not to their own children. When "
          "pressed, one wrote his name on a napkin, then ate the napkin.\n\nDay 4. The tide comes in nine minutes late, every day, "
          "and goes out nine minutes early. Something is drinking it.\n\nDay 5. Found a fish-shaped idol in a net. It was warm. "
          "It is still warm. It is warm in my pocket now and I do not remember putting it there.\n\nDay 6. I have begun to dream in "
          "a language with too many vowels. In the dream I am being counted. The count does not end.\n\nDay 7. Must not say my "
          "name. Must not say my name. Must not say my name. Ambrose. Ambrose Pickering. I am Ambrose Pickering. I"),
         sanity=-6, set_flag="pickering_notes_read")

# ============================================================================ the harbourmaster's post
npcs.append({"instance_id": "npc_harbourmaster", "npc_id": "core:npc.harbourmaster", "pos": [-1.2, 0.0, -7.6], "yaw": 180.0})
readable("tide_ledger", 1.0, 0.0, -8.2, "Read the Tide Ledger", "Saltmere Tide Ledger",
         ("HIGH WATER / LOW WATER / REMARKS\n\nMon. - 9 min late. 9 min early. Fair.\nTue. - 9 min late. 9 min early. Fog.\n"
          "Wed. - 9 min late. 9 min early. Fog. Boats came back one short. Nobody can say who.\nThu. - Fog.\nFri. - The water was "
          "counting. Could hear it. One, two, three. Stopped at a number I didn't like.\nSat. - \nSun. - "
          "\n\nThe last two lines are blank except for wet fingerprints, too long, with too many joints."),
         model=LECTERN, rot=180.0, sanity=-3)
readable("harbour_notice", -3.5, 0.0, 14.6, "Read the Harbour Notice", "BY ORDER OF THE HARBOURMASTER",
         ("NOTICE TO ALL VESSELS AND PERSONS:\n\n1. Fishing is permitted between dawn and the fog.\n2. Do not fish in the fog.\n"
          "3. Do not answer if the fog calls you by name.\n4. Do not say your name in the fog, in case it is listening.\n5. If you "
          "hear bells under the water, you did not hear bells under the water.\n6. Chowder at the Drowned Lantern, two coppers.\n\n"
          "Pinned beneath it, a cheerful pamphlet:\n\n\"THE ESOTERIC ORDER OF THE DROWNED LEDGER welcomes NEW MEMBERS! Tired of "
          "having a name? Let the Deep carry it for you! Benefits include: eternal life (partial), gills (most members), a lovely "
          "robe, and the peace of never being counted again. Meetings: under the fish warehouse, every tide. Bring nothing. "
          "Especially not your name.\""), model=LECTERN, rot=180.0)
interactables.append({"instance_id": "saltmere_idol", "type": "pickup", "item_id": "core:item.fish_idol", "qty": 1, "pos": [-6.4, 0.2, -12.8]})

# ============================================================================ Silas, at the end of pier B
npcs.append({"instance_id": "npc_silas", "npc_id": "core:npc.silas_gale", "pos": [9.5, 0.0, -20.6], "yaw": 180.0})

# ============================================================================ Gale & Sons Fish Co. (warehouse) and the stairwell
WX0, WX1, WZ0, WZ1 = 8.0, 19.4, -6.0, 12.0
wall_z("wh_w", WX0, WZ0, WZ1, 0.0, 4.2, gaps=[(2.0, 4.0)], model=STONE)
wall_x("wh_n", WZ0, WX0, WX1, 0.0, 4.2, model=STONE)
wall_x("wh_s", WZ1, WX0, WX1, 0.0, 4.2, model=STONE)
box("wh_roof", WOOD, WX0 - 0.3, WX1, 4.2, 4.5, WZ0 - 0.3, WZ1 + 0.3, uv=[5, 6])
light(12.0, 3.4, 4.0, [0.8, 0.85, 0.7], 10.0)
torch("torch_wh", 8.45, 2.0, 7.0, 90.0)
for i, (x, z) in enumerate([(9.2, -4.8), (10.2, -4.9), (9.4, 10.6), (18.2, 10.8), (18.4, 9.8), (12.0, 10.9)]):
    prop(f"wh_crate_{i}", "assets/models/props/wooden_crate.glb", x, 0.0, z, rot=i * 17.0)
readable("wh_ledger", 11.0, 0.0, 9.0, "Read the Shipping Ledger", "Gale & Sons Fish Co. - Shipping Ledger",
         ("CATCH / WEIGHT / BUYER\n\nCod, 40 lb, the Drowned Lantern\nHerring, 112 lb, Bellwether\nNames, 9, The Order\nNames, 14, "
          "The Order\nNames, 31, The Order\nNames, ALL OF THEM, The Order\n\nThe last entry is in a different hand, and the ink is "
          "still wet, and it is salt water."), model=LECTERN, rot=90.0, sanity=-4)
# Stair hole railings and the cellar gate
box("well_rail_w", TIMBER, 13.85, 14.0, 0.0, 1.0, -4.0, 4.0)
box("well_rail_e", TIMBER, 17.0, 17.15, 0.0, 1.0, -4.0, 4.0)
box("well_rail_n", TIMBER, 14.0, 17.0, 0.0, 1.0, -4.15, -4.0)
box("gate_post_w", STONE, 13.6, 14.4, 0.0, 3.0, 4.2, 4.7)
box("gate_post_e", STONE, 16.6, 17.4, 0.0, 3.0, 4.2, 4.7)
interactables.append({"instance_id": "cellar_gate", "type": "door", "model": "assets/models/props/iron_gate.glb", "pos": [15.5, 0.0, 4.45],
                      "rot_y": 0.0, "locked": True, "key_id": "core:item.cellar_key", "lock_difficulty": 13,
                      "prompt": "Cellar Gate (it smells of the sea)"})
# Two flights down toward -z: (z 4, y 0) -> (z 0, y -2.8) -> (z -4, y -5.6)
prop("stairs_upper", STAIRS, 15.5, -2.8, 2.0, rot=180.0, scale=(1.0, 1.4, 1.0), solid=False)
props[-1]["ramp"] = "+z"
prop("stairs_lower", STAIRS, 15.5, CY, -2.0, rot=180.0, scale=(1.0, 1.4, 1.0), solid=False)
props[-1]["ramp"] = "+z"
box("well_floor", COBBLE, 14.0, 17.0, CY - 0.5, CY, -6.0, -4.0, solid=False, uv=[1, 1])
box("well_wall_w", CRYPT, 13.7, 14.0, CY, 0.0, -6.0, 4.2)
box("well_wall_e", CRYPT, 17.0, 17.3, CY, 0.0, -6.0, 4.2)
box("well_wall_s", CRYPT, 13.7, 17.3, CY, -0.5, 4.2, 4.5)
torch("torch_well", 14.05, -3.4, -1.0, 90.0, eldritch=True)

# ============================================================================ the Sunken Chapel
box("chapel_floor", COBBLE, 2.0, 19.0, CY - 0.5, CY, -22.0, -6.0, solid=False, uv=[7, 7])
box("chapel_ceiling", CRYPT, 2.0, 19.0, -1.0, -0.6, -22.0, -4.0, solid=False, uv=[7, 7])
wall_z("ch_w", 2.0, -22.3, -5.7, CY, -1.0, model=CRYPT)
wall_z("ch_e", 19.0, -22.3, -5.7, CY, -1.0, model=CRYPT)
wall_x("ch_n", -22.0, 2.0, 19.0, CY, -1.0, model=CRYPT)
wall_x("ch_s", -6.0, 2.0, 19.0, CY, -1.0, gaps=[(14.0, 17.0)], model=CRYPT, door_h=4.6)
props.append({"id": "chapel_pool", "model": "assets/models/env/chapel_pool.glb", "pos": [10.5, CY + 0.06, -14.5], "rot_y": 0.0,
              "scale": [1.0, 1.0, 1.0], "solid": False})
for i, (x, z) in enumerate([(5.0, -9.0), (16.0, -9.0), (5.0, -19.5), (16.0, -19.5)]):
    prop(f"ch_pillar_{i}", PILLAR, x, CY, z, scale=(1.0, 1.15, 1.0))
    torch(f"ch_torch_{i}", x + (0.55 if x < 10 else -0.55), CY + 2.4, z, 90.0 if x < 10 else -90.0, eldritch=True)
prop("ch_altar", "assets/models/props/altar_dawn.glb", 10.5, CY, -20.6, rot=0.0)
prop("ch_tentacle", "assets/models/env/tentacle_b.glb", 14.5, CY, -14.0, rot=250.0, scale=(0.32, 0.32, 0.32), solid=False)
light(10.5, CY + 3.6, -14.5, [0.3, 0.9, 0.55], 14.0)
for i, (x, z, text) in enumerate([
        (3.2, -10.5, "A great bronze bell hangs from a beam, green with age, covered in barnacles that shouldn't grow this deep. It is "
                      "ringing. Nobody is ringing it. With every stroke, the pool in the middle of the chapel ripples outward, in rings, "
                      "like something below is listening.\n\nYou wrap your coat round the clapper and hold it still until the ringing "
                      "stops. Your hands are wet afterwards. They stay wet for an hour."),
        (17.8, -10.5, "The second bell. Its rim is engraved with names, hundreds of them, so small and so close together that they "
                      "look like a pattern of scales. Some of the names are very old. Some of them are fresh. One of them, near the "
                      "bottom, is still being engraved, by nothing, letter by letter.\n\nYou stop the bell before it finishes the "
                      "name. You do not look to see whose it was."),
        (10.5, -7.0, "The third bell is small, a ship's bell, polished, the kind that marks the watches on a voyage. It rings eight "
                     "bells: end of the watch. Then a ninth. Then a tenth. It keeps counting.\n\nYou silence it, and in the "
                     "silence afterwards you hear, from very far below the floor, something enormous turn over in its sleep.")]):
    readable(f"tide_bell_{i + 1}", x, CY + 1.4, z, "Silence the Tide Bell", f"Tide Bell ({['First', 'Second', 'Third'][i]})", text,
             set_flag=f"bell_{i + 1}", sanity=-8, quest_id=QUEST, set_stage=30)
readable("drowned_hymn", 7.0, CY + 1.0, -20.8, "Read the Hymn Carved in the Wall", "The Drowned Hymn",
         ("Carved deep in the stone, the letters worn by centuries of wet fingers:\n\n"
          "    Iä! Iä! N'gahl th'ruun!\n    The Name-Eater dreams beneath the tide.\n    Speak, and be counted. Be counted, and be eaten.\n"
          "    Iä! The ledger of the deep is never closed.\n\n"
          "    What is written, it can find.\n    What is spoken, it can taste.\n    What is struck out, it cannot see,\n"
          "    and what it cannot see, it fears.\n\n"
          "The last four lines have been scratched at, furiously, as if someone tried to erase them and couldn't."),
         set_flag="hymn_read", sanity=-12)
npcs.append({"instance_id": "npc_tide_priest", "npc_id": "core:npc.tide_priest", "pos": [10.5, CY, -19.0], "yaw": 0.0,
             "hidden_flag": "saltmere_resolved"})
for i, (pos, a, b) in enumerate([((6.5, CY, -12.0), (5.0, CY, -12.0), (6.5, CY, -17.0)),
                                 ((15.0, CY, -17.0), (16.0, CY, -12.0), (15.0, CY, -18.5)),
                                 ((8.0, CY, -8.0), (5.0, CY, -8.0), (12.0, CY, -8.0))]):
    creature(f"chapel_drowned_{i}", "core:enemy.the_drowned", pos, a, b)
creature("chapel_acolyte_0", "core:enemy.tide_acolyte", (4.5, CY, -15.0), (4.0, CY, -12.0), (4.0, CY, -18.0))
creature("chapel_acolyte_1", "core:enemy.tide_acolyte", (17.0, CY, -15.0))
creature("wh_drowned", "core:enemy.the_drowned", (15.5, CY, -5.0), (15.5, CY, -5.0), (15.5, CY, -9.0))
creature("avatar", "core:enemy.name_eater_avatar", (10.5, CY, -14.5), requires_flag="avatar_rises",
         group="avatar", group_quest_id=QUEST, group_set_stage=40, group_set_flag="saltmere_resolved")

region = {
    "schema_version": 1,
    "id": "core:map.saltmere",
    "display_name_key": "map.saltmere.name",
    "music": "assets/audio/music/vault_lullaby.wav",
    "ambience": "assets/audio/ambience/forest_wind.wav",
    "sky_color": [26, 34, 36],
    "ambient_color": [0.34, 0.42, 0.42],
    "sun_direction": [-0.2, 0.7, -0.5],
    "sun_color": [0.42, 0.5, 0.5],
    "fog_color": [0.16, 0.2, 0.2],
    "fog_density": 0.05,
    "weather": "",
    "spawns": {"saltmere_quay": {"pos": [0.0, 0.0, 16.0], "yaw_degrees": 180.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

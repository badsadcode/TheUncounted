#!/usr/bin/env python3
"""
Generates content/regions/sleepers_reef.json: the Sleeper's Reef, a rocky island far out past Saltmere's fog, ringed by
the Name-Eater's sleeping limbs, with the drowned Saltmere Light on it. Reached only by Silas's boat (dialogue action
"travel" to spawn "reef_landing"); it is not connected to the rest of the world on foot.

Region-local frame (build_world.py places it at REEF_OFF): island x -12..12, z -14..14 (rock, y 0), shallow sea to
+-26 under a water model, cliffs at the edge (lost in fog). The lighthouse tower (x -2..2, z -10..-6) has a gallery at
y 5.6, reached by two flights of stone stairs on its east side. Silas's jetty is at the south (z 14..20).
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python tools/build_reef.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "sleepers_reef.json")
STONE = "assets/models/env/wall_stone.glb"
CRYPT = "assets/models/env/wall_crypt.glb"
WOOD = "assets/models/env/floor_wood.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
PILLAR = "assets/models/env/pillar_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"
LECTERN = "assets/models/props/lectern_ledger.glb"
QUEST = "core:quest.reef"
GY = 5.6  # gallery floor

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def prop(pid, model, x, y, z, rot=0.0, scale=(1, 1, 1), solid=True):
    props.append({"id": pid, "model": model, "pos": [x, y, z], "rot_y": rot, "scale": list(scale), "solid": solid})


def flame(fid, x, y, z, color=(1.0, 0.62, 0.3), size=0.5, radius=8.0):
    props.append({"id": fid, "model": TORCH, "pos": [x, y - 0.55, z], "rot_y": 0.0, "scale": [1, 1, 1], "solid": False,
                  "emitter": {"sprite": "assets/sprites/vfx/torch_flame.png", "offset": [0.0, 0.86, 0.0], "size": size,
                              "light_color": list(color), "light_radius": radius}})


def readable(iid, x, y, z, prompt, title, text, model="", rot=0.0, **extra):
    d = {"instance_id": iid, "type": "readable", "model": model, "pos": [x, y, z], "rot_y": rot, "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ sea, cliffs, the island
box("reef_sea_floor", COBBLE, -26.0, 26.0, -0.9, -0.45, -26.0, 26.0, uv=[18, 18])
props.append({"id": "reef_water", "model": "assets/models/env/harbour_water.glb", "pos": [0.0, -0.14, 0.0], "rot_y": 0.0,
              "scale": [1.1, 1.0, 2.2], "solid": False})
for pid, (x0, x1, z0, z1) in {"cliff_n": (-26.6, 26.6, -26.6, -25.4), "cliff_s": (-26.6, 26.6, 25.4, 26.6),
                              "cliff_w": (-26.6, -25.4, -26.6, 26.6), "cliff_e": (25.4, 26.6, -26.6, 26.6)}.items():
    box(pid, CRYPT, x0, x1, -0.9, 1.7, z0, z1, uv=[14, 0.6])  # a low reef rim; the fog hides the rest
for pid, (x0, x1, z0, z1) in {"isle_main": (-12.0, 12.0, -14.0, 14.0), "isle_w": (-15.0, -12.0, -6.0, 8.0),
                              "isle_e": (12.0, 14.5, -10.0, 4.0), "isle_n": (-6.0, 5.0, -17.0, -14.0)}.items():
    box(pid, COBBLE, x0, x1, -0.5, 0.0, z0, z1, solid=False, uv=[round((x1 - x0) / 2.4, 1), round((z1 - z0) / 2.4, 1)])
# Scattered boulders and the stumps of an older wall
for i, (x, z, w, h, d) in enumerate([(-10.5, 11.5, 1.6, 1.1, 1.2), (9.5, 11.0, 1.2, 0.8, 1.4), (12.5, -2.0, 1.0, 1.4, 1.6),
                                     (-13.5, 2.0, 1.2, 0.9, 1.0), (7.5, -13.0, 1.8, 1.0, 1.0), (-8.5, -13.5, 1.4, 1.3, 1.2),
                                     (3.0, 12.5, 0.9, 0.6, 0.9), (-4.0, -15.5, 1.0, 0.7, 1.4)]):
    box(f"boulder_{i}", STONE, x - w / 2, x + w / 2, -0.2, h, z - d / 2, z + d / 2, uv=[0.5, 0.4])
for i, (x, z) in enumerate([(-11.0, -9.0), (11.0, 8.0), (-12.5, 6.0)]):
    prop(f"old_pillar_{i}", PILLAR, x, 0.0, z, scale=(1.0, 0.55 + 0.25 * i, 1.0))

# ============================================================================ the jetty and Silas's boat
box("jetty", WOOD, -1.2, 1.2, -0.5, 0.0, 13.5, 21.0, uv=[1, 3])
for i, (x, z) in enumerate([(-1.35, 16.0), (1.35, 16.0), (-1.35, 20.8), (1.35, 20.8)]):
    box(f"jetty_pile_{i}", WOOD, x - 0.15, x + 0.15, -0.9, 0.5, z - 0.15, z + 0.15)
box("boat_hull", WOOD, 1.9, 3.3, -0.5, 0.25, 16.6, 20.6, uv=[1, 0.4])
box("boat_seat", WOOD, 1.9, 3.3, 0.25, 0.35, 18.4, 18.8, solid=False, uv=[0.6, 0.2])
box("boat_oar", WOOD, 3.3, 4.6, 0.3, 0.38, 18.5, 18.7, solid=False, uv=[0.6, 0.1])
flame("jetty_lantern", -1.0, 1.4, 20.4, color=(1.0, 0.7, 0.4), size=0.3, radius=6.0)
box("jetty_lantern_post", WOOD, -1.12, -0.88, 0.0, 1.0, 20.28, 20.52)
npcs.append({"instance_id": "npc_silas_reef", "npc_id": "core:npc.silas_gale", "pos": [-0.4, 0.0, 18.8], "yaw": 180.0,
             "requires_flag": "reef_trip"})

# ============================================================================ the Saltmere Light
TX0, TX1, TZ0, TZ1 = -2.0, 2.0, -10.0, -6.0
box("light_tower", STONE, TX0, TX1, 0.0, GY - 0.3, TZ0, TZ1, uv=[1.6, 1.8])
box("light_band_low", CRYPT, TX0 - 0.08, TX1 + 0.08, 1.6, 1.9, TZ0 - 0.08, TZ1 + 0.08, uv=[1.6, 0.1])
box("light_band_high", CRYPT, TX0 - 0.08, TX1 + 0.08, 3.6, 3.9, TZ0 - 0.08, TZ1 + 0.08, uv=[1.6, 0.1])
box("light_door", WOOD, -0.7, 0.7, 0.0, 2.2, TZ1, TZ1 + 0.08, solid=False, uv=[0.5, 0.7])
# Gallery deck round the top, and the stair-top strip on the east
box("gallery_deck", WOOD, -3.5, 3.5, GY - 0.3, GY, -11.5, -4.5, solid=False, uv=[3, 3])
box("gallery_strip", WOOD, 3.5, 7.5, GY - 0.3, GY, -12.0, -9.0, solid=False, uv=[2, 1.5])
box("gallery_strip_base", STONE, 3.6, 7.4, 0.0, GY - 0.3, -11.9, -9.1, uv=[1.5, 1.8])
for pid, (x0, x1, z0, z1) in {"rail_w": (-3.6, -3.4, -11.6, -4.4), "rail_n": (-3.6, 3.6, -11.6, -11.4), "rail_s": (-3.6, 3.6, -4.6, -4.4),
                              "rail_e": (3.4, 3.6, -9.0, -4.4), "rail_strip_n": (3.5, 7.6, -12.1, -11.9),
                              "rail_strip_e": (7.4, 7.6, -12.1, -9.0), "rail_strip_s": (3.5, 4.5, -9.1, -8.9)}.items():
    box(pid, CRYPT, x0, x1, GY, GY + 1.0, z0, z1, uv=[1.5, 0.3])
# Two flights up the east side: (z 2, y 0) -> (z -2, y 2.8) -> landing -> (z -5, y 2.8) -> (z -9, y 5.6)
prop("stairs_a", STAIRS, 6.0, 0.0, 0.0, rot=0.0, scale=(1.0, 1.4, 1.0), solid=False)
props[-1]["ramp"] = "-z"
box("landing", WOOD, 4.5, 7.5, 2.3, 2.8, -5.0, -2.0, solid=False, uv=[1.2, 1.2])
box("landing_base", STONE, 4.6, 7.4, 0.0, 2.3, -4.9, -2.1, uv=[1.2, 0.8])
prop("stairs_b", STAIRS, 6.0, 2.8, -7.0, rot=0.0, scale=(1.0, 1.4, 1.0), solid=False)
props[-1]["ramp"] = "-z"
box("stairs_b_base", STONE, 4.6, 7.4, 0.0, 2.8, -8.9, -5.1, uv=[1.2, 0.9])
# The lamp itself, dark, on the deck
box("lamp_plinth", STONE, -0.8, 0.8, GY, GY + 0.9, -8.8, -7.2, uv=[0.6, 0.3])
box("lamp_cage", CRYPT, -0.6, 0.6, GY + 0.9, GY + 2.0, -8.6, -7.4, solid=False, uv=[0.5, 0.4])
box("lamp_cap", STONE, -0.8, 0.8, GY + 2.0, GY + 2.2, -8.8, -7.2, uv=[0.6, 0.1])
lights.append({"pos": [0.0, GY + 1.6, -8.0], "color": [0.55, 0.62, 0.7], "radius": 9.0})
lights.append({"pos": [6.0, 3.6, -3.5], "color": [0.5, 0.6, 0.65], "radius": 7.0})
readable("light_plaque", 0.0, 0.0, TZ1 + 0.4, "Read the Plaque by the Door", "The Saltmere Light",
         ("SALTMERE LIGHT\nRaised in the Year of the Long Tide by the Fishermen's Guild\n\"So that every boat comes home, and "
          "every name with it.\"\n\nKEEPERS: J. Marsh. P. Marsh. E. Marsh. O. Marsh.\n\nThe last name has no end date. Below it, "
          "scratched with something sharp, a tally of days: so many that they cover the bottom of the plaque, the doorframe, and "
          "the first yard of the tower wall."), model="", set_flag="reef_plaque")
readable("keeper_log", -2.6, GY, -10.6, "Read the Keeper's Log", "Log of the Saltmere Light, O. Marsh",
         ("\"Day 1. Father's gone. I keep the light now. It's not hard. Trim the wick, fill the oil, wind the clock. And never let "
          "it go out.\"\n\n\"Day 900. Father said the light isn't for ships. It's for the thing under the reef. While it can see "
          "the light, it dreams. While it dreams, it isn't hungry. I thought he was joking. He wasn't.\"\n\n\"Day 20,000 (I think). "
          "I died some time ago. I've kept the light anyway. Nobody has come to relieve me. I don't mind. Somebody has to.\"\n\n"
          "\"Day ?. The men in robes came and sang, and the light went out. It has never gone out. I can't relight it. My "
          "hands go through the matches now. I need someone who's still solid. I need someone it can't see.\""),
         set_flag="reef_log", sanity=-4)
npcs.append({"instance_id": "npc_keeper", "npc_id": "core:npc.keeper_ondine", "pos": [-2.2, GY, -7.0], "yaw": 90.0,
             "requires_flag": "reef_trip", "hidden_flag": "keeper_rests"})
npcs.append({"instance_id": "npc_trout_light", "npc_id": "core:npc.trout", "pos": [2.6, GY, -5.4], "yaw": 220.0,
             "requires_flag": "oak_plugged"})

# ============================================================================ the brothers' fire
FX, FZ = -6.0, 3.0
for k, (dx, dz) in enumerate([(0.5, 0.0), (-0.5, 0.0), (0.0, 0.5), (0.0, -0.5), (0.35, 0.35), (-0.35, -0.35)]):
    box(f"bro_fire_stone{k}", STONE, FX + dx - 0.12, FX + dx + 0.12, 0.0, 0.2, FZ + dz - 0.12, FZ + dz + 0.12, solid=False, uv=[0.2, 0.1])
flame("bro_fire", FX, 0.0, FZ, color=(1.0, 0.55, 0.3), size=0.55, radius=8.0)
box("bro_driftwood", WOOD, FX - 1.6, FX + 1.6, 0.0, 0.35, FZ + 1.8, FZ + 2.3, uv=[1.2, 0.2])
npcs.append({"instance_id": "npc_gale_elder", "npc_id": "core:npc.gale_elder", "pos": [FX + 0.9, 0.0, FZ + 1.3], "yaw": 200.0,
             "requires_flag": "reef_trip", "hidden_flag": "reef_done"})
npcs.append({"instance_id": "npc_gale_younger", "npc_id": "core:npc.gale_younger", "pos": [FX - 1.1, 0.0, FZ + 1.2], "yaw": 160.0,
             "requires_flag": "reef_trip", "hidden_flag": "reef_done"})

# ============================================================================ names in bottles
BOTTLES = [
    ("reef_bottle_tom", 8.5, 6.5, "THOMAS GALE",
     "A green bottle, stoppered with wax, wedged between two rocks. Inside, a strip of sailcloth with a name stitched on it in "
     "red thread, the stitches small and careful, the kind a mother makes:\n\nTHOMAS GALE\n\nUnderneath, in smaller stitches: "
     "\"Eldest. Bad at knots. Good at laughing.\"\n\nIt feels warm in your hand. It feels like it's been waiting.", "reef_tom"),
    ("reef_bottle_abel", -10.0, -3.5, "ABEL GALE",
     "A brown bottle, half buried in sand. Inside, a page torn from a school primer, the alphabet down one side and, in a "
     "child's enormous letters, practised over and over until the page ran out:\n\nABEL GALE  ABEL GALE  ABEL GALE  ABEL GALE\n\n"
     "At the bottom, in an adult hand: \"He was so proud when he could write it. -S.\"", "reef_abel"),
    ("reef_bottle_fenn", 10.5, -6.5, "BARTHOLOMEW FENN",
     "A bottle with a ship in it. A very small ship. On the deck of the very small ship, a very small man is holding up a very "
     "small fish, triumphantly. The label reads:\n\nBARTHOLOMEW 'BART' FENN\nWanted to be remembered as the man who caught the "
     "Big One. Caught it. It ate him. Remember him anyway.", "reef_fenn"),
    ("reef_bottle_nan", -4.5, 10.5, "GRANNY WEATHERBY",
     "A jam jar. The label still says 'DAMSON, LAST SUMMER'. Inside, a recipe card:\n\nGRANNY WEATHERBY'S CHOWDER\n(Do not tell "
     "Brine. Brine thinks hers is better. Brine is wrong.)\n\nThe recipe is long, specific, and ends with: \"...and a pinch of "
     "salt for every name you love. Use a lot of salt.\"", "reef_nan"),
    ("reef_bottle_nobody", 3.5, 9.0, "(blank)",
     "A clear glass bottle, very old, the glass gone milky with salt. There's a slip of paper inside. You shake it out.\n\n"
     "It's blank.\n\nNot faded. Blank. Somebody put a name in here once, and the sea took the name and left the paper, and "
     "sent the paper home anyway, because the sea, for all its hunger, has a sense of form.\n\nYou keep the paper. It seems "
     "wrong not to. Nobody should be nobody.", "reef_nobody"),
    ("reef_bottle_marsh", -13.5, 6.5, "ONDINE MARSH",
     "A lamp-glass, of all things, the chimney off an old oil lamp, stoppered at both ends with cork. Inside, a lock of grey "
     "hair tied with string, and a label in a neat, tired hand:\n\nONDINE MARSH. Keeper.\n\n\"If anyone finds this, I was here. "
     "I kept the light. Please tell somebody.\"", "reef_ondine"),
]
for iid, x, z, title, text, flag in BOTTLES:
    readable(iid, x, 0.0, z, "Pick Up the Bottle", f"A Name in a Bottle: {title}", text, set_flag=flag, sanity=2)

# ============================================================================ the sleeping limbs, and what wakes
for i, (x, z, rot, sc, model) in enumerate([(-20.0, -18.0, 30.0, 2.4, "a"), (19.0, -16.0, 200.0, 2.0, "b"), (-21.0, 12.0, 120.0, 1.8, "b"),
                                            (20.5, 15.0, 300.0, 2.6, "a"), (2.0, -23.0, 80.0, 2.2, "a"), (-16.0, -4.0, 250.0, 0.9, "b"),
                                            (16.5, 2.0, 160.0, 1.1, "b"), (8.0, 21.0, 20.0, 1.4, "a")]):
    prop(f"limb_{i}", f"assets/models/env/tentacle_{model}.glb", x, -0.6, z, rot=rot, scale=(sc, sc, sc), solid=False)
creature("dreaming_limb", "core:enemy.dreaming_limb", (-8.5, 0.0, -11.5), requires_flag="lamp_lit", group="limb",
         group_quest_id=QUEST, group_set_stage=40, group_set_flag="limb_down")
creature("limb_drowned_0", "core:enemy.the_drowned", (-5.0, 0.0, -13.0), (-5.0, 0.0, -13.0), (-9.0, 0.0, -8.0),
         requires_flag="lamp_lit", group="limb")
creature("limb_drowned_1", "core:enemy.the_drowned", (-11.0, 0.0, -6.5), (-11.0, 0.0, -6.5), (-7.0, 0.0, -10.0),
         requires_flag="lamp_lit", group="limb")
creature("reef_drowned_0", "core:enemy.the_drowned", (9.0, 0.0, -11.0), (9.0, 0.0, -11.0), (11.0, 0.0, -3.0))
creature("reef_drowned_1", "core:enemy.the_drowned", (10.0, 0.0, 9.0), (10.0, 0.0, 9.0), (6.0, 0.0, 12.0))

# ============================================================================ gathering (tools/authoring/crafting.py)
interactables.append({"instance_id": "reef_bladderwrack_80_80", "type": "harvest", "model": "assets/models/props/seaweed.glb", "pos": [-8.0, 0.0, 8.0], "rot_y": 152.0, "item_id": "core:item.bladderwrack", "qty": 1, "qty_max": 2, "respawn_seconds": 480, "prompt": "Gather Bladderwrack", "scale": [1.4, 1.4, 1.4]})
interactables.append({"instance_id": "reef_bladderwrack_90_20", "type": "harvest", "model": "assets/models/props/seaweed.glb", "pos": [9.0, 0.0, -2.0], "rot_y": 311.0, "item_id": "core:item.bladderwrack", "qty": 1, "qty_max": 2, "respawn_seconds": 480, "prompt": "Gather Bladderwrack", "scale": [1.4, 1.4, 1.4]})
interactables.append({"instance_id": "reef_sea_salt_120_35", "type": "harvest", "model": "assets/models/props/salt_crust.glb", "pos": [12.0, 0.0, 3.5], "rot_y": 122.5, "item_id": "core:item.sea_salt", "qty": 1, "qty_max": 2, "respawn_seconds": 480, "prompt": "Scrape Sea Salt", "scale": [1.4, 1.4, 1.4]})
interactables.append({"instance_id": "reef_sea_salt_120_10", "type": "harvest", "model": "assets/models/props/salt_crust.glb", "pos": [-12.0, 0.0, -1.0], "rot_y": 265.0, "item_id": "core:item.sea_salt", "qty": 1, "qty_max": 2, "respawn_seconds": 480, "prompt": "Scrape Sea Salt", "scale": [1.4, 1.4, 1.4]})
interactables.append({"instance_id": "reef_glowcap_35_125", "type": "harvest", "model": "assets/models/props/mushroom_glowcap.glb", "pos": [-3.5, 0.0, -12.5], "rot_y": 93.0, "item_id": "core:item.glowcap", "qty": 1, "qty_max": 2, "respawn_seconds": 480, "prompt": "Pick Glowcap", "scale": [1.4, 1.4, 1.4]})

# ============================================================================ fishing & cooking (tools/authoring/fishing.py)
interactables.append({"instance_id": "fish_jetty", "type": "fishing", "model": "", "pos": [0.0, 0.0, 20.6], "rot_y": 0.0, "loot_table": "core:loot.fish_reef", "prompt": "Fish off the jetty"})

# ============================================================================ more monsters (Sleeper's Reef, tools/authoring/more_monsters.py)
creature("reef_wight_0", "core:enemy.salt_wight", (4.0, 0.0, 8.0), (1.0, 0.0, 8.0), (7.0, 0.0, 8.0))
creature("reef_wight_1", "core:enemy.salt_wight", (-7.0, 0.0, 4.0), (-7.0, 0.0, 1.0), (-7.0, 0.0, 7.0))

region = {
    "schema_version": 1,
    "id": "core:map.sleepers_reef",
    "display_name_key": "map.sleepers_reef.name",
    "music": "assets/audio/music/vault_lullaby.wav",
    "ambience": "assets/audio/ambience/forest_wind.wav",
    "sky_color": [43, 54, 56],
    "ambient_color": [0.36, 0.44, 0.46],
    "sun_direction": [-0.3, 0.7, -0.4],
    "sun_color": [0.42, 0.5, 0.52],
    "fog_color": [0.17, 0.21, 0.22],
    "fog_density": 0.06,
    "weather": "",
    "spawns": {"reef_landing": {"pos": [0.0, 0.0, 15.0], "yaw_degrees": 180.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

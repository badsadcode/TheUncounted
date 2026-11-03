#!/usr/bin/env python3
"""
Generates content/regions/hollowmere.json: Hollowmere Manor and its grounds, south of Bellwether.

Region-local frame (build_world.py places it at HOLLOW_OFF; local z = -22 is Bellwether's south wall):
  * Grounds x -20..20, z -21.4..24: cobbled drive, an adventurers' graveyard (west), Rolf's garden (east).
  * The house x -14..14, z -8..16, two storeys (ground y 0..4, upper y 4..8) joined by a grand stair in the foyer.
      Ground:  Foyer (centre) | Dining room (W) | Library (E) | Kitchen (SW) | Ballroom (S/SE)
      Upper:   Landing (centre) | Master bedroom (W) | Study (E, locked) | Portrait gallery (S) | Sealed room (SE)
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python tools/build_mansion.py
"""

import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "hollowmere.json")

STONE = "assets/models/env/wall_stone.glb"
TIMBER = "assets/models/env/wall_timber.glb"
CRYPT = "assets/models/env/wall_crypt.glb"
WOOD = "assets/models/env/floor_wood.glb"
GRASS = "assets/models/env/floor_grass.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"
DOOR = "assets/models/props/oak_door.glb"
LECTERN = "assets/models/props/lectern_ledger.glb"
PILLAR = "assets/models/env/pillar_stone.glb"
QUEST_HAUNT = "core:quest.hollowmere"
QUEST_RATS = "core:quest.rats"

props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def wall_x(pid, z, x0, x1, y0, y1, gaps=(), model=TIMBER, t=0.6, door_h=2.8):
    """Wall running along X at z, from x0 to x1, with door gaps [(a, b), ...] closed above by lintels."""
    cur = x0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, cur, a, y0, y1, z - t / 2, z + t / 2)
        box(f"{pid}_lintel{i}", model, a, b, y0 + door_h, y1, z - t / 2, z + t / 2)
        cur = b
    if x1 > cur:
        box(f"{pid}_end", model, cur, x1, y0, y1, z - t / 2, z + t / 2)


def wall_z(pid, x, z0, z1, y0, y1, gaps=(), model=TIMBER, t=0.6, door_h=2.8):
    cur = z0
    for i, (a, b) in enumerate(sorted(gaps)):
        if a > cur:
            box(f"{pid}_{i}", model, x - t / 2, x + t / 2, y0, y1, cur, a)
        box(f"{pid}_lintel{i}", model, x - t / 2, x + t / 2, y0 + door_h, y1, a, b)
        cur = b
    if z1 > cur:
        box(f"{pid}_end", model, x - t / 2, x + t / 2, y0, y1, cur, z1)


def torch(tid, x, y, z, rot, ghost=False):
    props.append({"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False,
                  "emitter": {"sprite": "assets/sprites/vfx/spell_arcane.png" if ghost else "assets/sprites/vfx/torch_flame.png",
                              "offset": [0.0, 0.86, 0.0], "size": 0.32 if ghost else 0.38,
                              "light_color": [0.45, 0.8, 1.0] if ghost else [1.0, 0.62, 0.28], "light_radius": 6.5}})


def light(x, y, z, color, r):
    lights.append({"pos": [x, y, z], "color": color, "radius": r})


def prop(pid, model, x, y, z, rot=0.0, scale=(1, 1, 1), solid=True):
    props.append({"id": pid, "model": model, "pos": [x, y, z], "rot_y": rot, "scale": list(scale), "solid": solid})


def readable(iid, x, y, z, prompt, title, text, model="", rot=0.0, **extra):
    d = {"instance_id": iid, "type": "readable", "model": model, "pos": [x, y, z], "rot_y": rot,
         "prompt": prompt, "title": title, "text": text}
    d.update(extra)
    interactables.append(d)


def creature(iid, cid, pos, a=None, b=None, **extra):
    d = {"instance_id": iid, "creature_id": cid, "pos": list(pos), "patrol_a": list(a or pos), "patrol_b": list(b or pos)}
    d.update(extra)
    creatures.append(d)


# ============================================================================ grounds
box("grounds", GRASS, -20.0, 20.0, -0.5, 0.0, -21.4, 24.0, solid=False, uv=[16, 18])
box("drive", COBBLE, -1.6, 1.6, -0.46, 0.04, -21.4, -8.0, solid=False, uv=[1.2, 5])
box("bound_w", STONE, -20.6, -19.4, 0.0, 4.5, -21.4, 24.6)
box("bound_e", STONE, 19.4, 20.6, 0.0, 4.5, -21.4, 24.6)
box("bound_s", STONE, -20.6, 20.6, 0.0, 4.5, 23.4, 24.6)
for i, (x, z) in enumerate([(-17, -4), (-17, 6), (-17, 16), (17, -4), (17, 6), (17, 16), (-7, -19), (7, -19), (-12, 20), (12, 20)]):
    prop(f"tree_{i}", "assets/models/env/tree_pine.glb", x, 0.0, z, scale=(1.1, 1.3, 1.1))
torch("torch_gate_w", -2.2, 1.6, -20.6, 0.0)
torch("torch_gate_e", 2.2, 1.6, -20.6, 0.0)
torch("torch_porch_w", -2.0, 1.8, -8.35, 180.0)
torch("torch_porch_e", 2.0, 1.8, -8.35, 180.0)

# --- The adventurers' graveyard (west lawn)
graves = [
    ("Here lies GROGNAK THE MIGHTY.\nStrength 18. Intelligence 3.\nHe tried to intimidate a door. The door won."),
    ("Here lies SIR REGINALD, who split the party.\n\"You lot take the left corridor, I'll be fine.\"\nHe was not fine."),
    ("Here lies ELARA MOONWHISPER SHADOWBLADE NIGHTSONG,\nlast of her clan, orphaned twice, cursed thrice.\nHer tragic backstory ran to fourteen pages. The game master read two."),
    ("Here lies the BARD, who rolled to seduce the dragon.\nIt was a natural 20.\nThe dragon has not stopped writing letters."),
    ("Here lies PIP THE QUICK, rogue,\nwho checked the chest for traps.\nThe chest was the trap. It had teeth."),
    ("Here lies BRANDT, who stepped on the same pressure plate four times\nto see if it would still do that.\nIt still did that."),
    ("Here lies a GNOME, name unknown, who ate an amulet\nbecause it was 'probably food'.\nIt was an amulet of strangulation. It was not food."),
    ("Here lies a HERO who saved the realm, the king, the princess and a goat,\nthen spent eleven hours deciding what to put in the stash.\nHe died of old age at the chest. The goat lived."),
    ("Here lies a MONSTER HUNTER who swore he'd finish the contract\nright after one more hand of cards.\nThat was nine years ago. The monster died of old age."),
    ("Here lies TOMAS THE SAVE-SCUMMER.\nHe reloaded so many times the world grew suspicious.\nOn the last attempt, the world reloaded him."),
]
for i, text in enumerate(graves):
    gx, gz = -17.0 + (i % 5) * 2.2, -16.5 + (i // 5) * 3.0
    readable(f"grave_{i}", gx, 0.0, gz, "Read the Gravestone", "Here Lies...", text, model=STONE, rot=0.0)
    interactables[-1]["scale"] = [0.75, 1.05, 0.2]  # a slab headstone (unit cube)
    box(f"grave_mound_{i}", GRASS, gx - 0.45, gx + 0.45, 0.0, 0.18, gz + 0.2, gz + 1.9, solid=False, uv=[0.6, 0.2])
readable("graveyard_sign", -12.6, 0.0, -10.8, "Read the Little Sign", "The Lawn of Ill-Advised Choices",
         ("A small, cheerful sign planted in the grass:\n\n\"MEMORIAL LAWN for Adventurers Who Came Before You.\nPlease don't loot "
          "the graves.\nWe KNOW you're going to loot the graves.\nThey're empty. The previous adventurers looted them.\"\n\n- P. Hollowmere"),
         model=LECTERN, rot=180.0)

# --- Entrance
readable("gate_sign", 2.6, 0.0, -19.6, "Read the Gate Sign", "Hollowmere Manor - Private Grounds",
         ("HOLLOWMERE MANOR\nHome of Sir Percival Hollowmere, Bart., Host of the Finest Parties in the Marches\n\n"
          "Underneath, carved later and much less neatly:\n\n\"YOU MUST GATHER YOUR PARTY BEFORE VENTURING FORTH.\"\n\n"
          "And under that, in fresh chalk: \"we tried. nobody came. - P.\""), model=LECTERN, rot=180.0,
         quest_id=QUEST_HAUNT, set_stage=0, set_flag="hollowmere_visited")

# --- Rolf's garden (east lawn): the "wailing" herring
readable("garden_howl", 12.0, 1.2, -13.0, "Listen to the Wailing", "A Mournful Wail",
         ("A long, heartbroken wail rolls across the garden and makes the hairs on your neck stand up. It is exactly the "
          "kind of noise a Banshee is supposed to make.\n\nIt is also exactly the kind of noise a very large, very sad dog "
          "would make.\n\nYou note it down as evidence. Probably."), set_flag="clue_wailing")
box("garden_bed_1", WOOD, 9.0, 15.0, 0.0, 0.3, -17.0, -15.6, uv=[2, 0.2])
box("garden_bed_2", WOOD, 9.0, 15.0, 0.0, 0.3, -11.4, -10.0, uv=[2, 0.2])
npcs.append({"instance_id": "npc_rolf", "npc_id": "core:npc.werewolf_rolf", "pos": [14.0, 0.0, -13.2], "yaw": -100.0})

# ============================================================================ the house shell
H0, H1, TOP = 0.0, 4.0, 8.0
# Exterior: front door gap (z = -8, x -1.2..1.2), kitchen back door (x = -14, z 11..13)
wall_x("ext_n", -8.0, -14.3, 14.3, H0, TOP, gaps=[(-1.2, 1.2)], model=STONE)
wall_x("ext_s", 16.0, -14.3, 14.3, H0, TOP, model=STONE)
wall_z("ext_w", -14.0, -7.7, 15.7, H0, TOP, gaps=[(11.0, 13.0)], model=STONE)
wall_z("ext_e", 14.0, -7.7, 15.7, H0, TOP, model=STONE)
box("roof", STONE, -14.6, 14.6, TOP, TOP + 0.4, -8.6, 16.6, uv=[10, 10])
for i, (x, z) in enumerate([(-10.0, -4.0), (10.0, 12.0)]):
    box(f"chimney_{i}", STONE, x - 0.8, x + 0.8, TOP, TOP + 2.6, z - 0.8, z + 0.8)
# Floors
box("floor_ground", WOOD, -14.0, 14.0, -0.5, 0.02, -8.0, 16.0, solid=False, uv=[12, 10])
# Upper floor slab with a stairwell hole at x 1..4, z -5..3
for pid, (x0, x1, z0, z1) in {"slab_w": (-14.0, 1.0, -8.0, 16.0), "slab_e": (4.0, 14.0, -8.0, 16.0),
                              "slab_s": (1.0, 4.0, 3.0, 16.0), "slab_n": (1.0, 4.0, -8.0, -5.0)}.items():
    box(pid, WOOD, x0, x1, H1 - 0.3, H1, z0, z1, uv=[round((x1 - x0) / 2.4, 1), round((z1 - z0) / 2.4, 1)])
# Stair railings round the hole (upper floor)
box("rail_w", TIMBER, 0.85, 1.0, H1, H1 + 1.0, -5.0, 3.0)
box("rail_n", TIMBER, 1.0, 4.0, H1, H1 + 1.0, -5.15, -5.0)
# Grand stair: two flights rising toward +z along the foyer's east side (x 1..4), z -5 -> 3, y 0 -> 4
prop("stairs_lower", STAIRS, 2.5, 0.0, -3.0, rot=180.0, scale=(1.0, 1.0, 1.0), solid=False)
props[-1]["ramp"] = "+z"
prop("stairs_upper", STAIRS, 2.5, 2.0, 1.0, rot=180.0, scale=(1.0, 1.0, 1.0), solid=False)
props[-1]["ramp"] = "+z"
box("stair_block", TIMBER, 1.0, 4.0, 0.0, 2.0, -1.0, 3.0)  # solid plinth under the upper flight

# ============================================================================ ground floor rooms
# Foyer x -4..4, z -8..6 | Dining x -14..-4, z -8..6 | Library x 4..14, z -8..6 | Kitchen x -14..-4, z 6..16 | Ballroom x -4..14, z 6..16
wall_z("g_foyer_w", -4.0, -7.7, 16.0, H0, H1 - 0.3, gaps=[(-3.0, -1.0), (9.0, 11.0)])
wall_z("g_foyer_e", 4.0, -7.7, 6.0, H0, H1 - 0.3, gaps=[(3.8, 5.6)])
wall_x("g_mid_w", 6.0, -13.7, -4.0, H0, H1 - 0.3, gaps=[(-10.0, -8.0)])
wall_x("g_mid_e", 6.0, -4.0, 13.7, H0, H1 - 0.3, gaps=[(-1.0, 1.0), (8.0, 10.0)])
interactables.append({"instance_id": "hollowmere_front_door", "type": "door", "model": DOOR, "pos": [0.0, 0.0, -8.0], "rot_y": 0.0,
                      "locked": True, "key_id": "core:item.hollowmere_key", "lock_difficulty": 14, "prompt": "Hollowmere Manor Front Door"})
interactables.append({"instance_id": "hollowmere_kitchen_door", "type": "door", "model": DOOR, "pos": [-14.0, 0.0, 12.0], "rot_y": 90.0,
                      "locked": False, "prompt": "Kitchen Back Door (it's open; it's always open; that's the problem)"})

# --- Foyer
for x in (-3.2, 3.2):
    prop(f"foyer_pillar_{x}", PILLAR, x, 0.0, -6.8)
light(0.0, 3.2, -3.0, [1.0, 0.8, 0.55], 11.0)
torch("torch_foyer_w", -3.65, 2.0, -5.0, 90.0)
readable("foyer_chalkboard", -2.6, 0.0, 4.6, "Read the Hunter's Chalkboard", "EVIDENCE BOARD (Property of Hollis)",
         ("Somebody has set up a chalkboard in the foyer, like a hunter's wagon parked outside a haunting.\n\n"
          "EVIDENCE FOUND:\n[ ] Cold spots\n[ ] Ghost writing\n[ ] Floating objects\n[ ] Spirit box response\n[ ] Ectoplasm handprints\n"
          "[ ] Wailing\n\nRULES:\n1. Find three kinds of evidence.\n2. Check the Field Guide.\n3. Do NOT say its name out loud. "
          "Especially not in the dark. Especially not as a joke.\n4. If the lights start flickering, that's normal. If they start "
          "flickering in Morse code, leave.\n5. Do not hide in the wardrobe. It always finds you in the wardrobe."),
         model=LECTERN, rot=180.0)
readable("foyer_tpose", 2.8, 1.2, 5.0, "Inspect the Figure in the Hall", "A Figure in the Hall",
         ("A mannequin stands in the corner of the foyer, arms stuck rigidly straight out to either side, legs together, face "
          "perfectly blank.\n\nIt has been standing like that for weeks, the butler's diary says. It doesn't move. It doesn't "
          "attack. It just stands there in that pose, as if it is waiting for somebody, somewhere, to finish loading its "
          "animations.\n\nYou back away slowly. Its arms do not follow you. You're almost disappointed."))
creature("foyer_armor", "core:enemy.animated_armor", (0.0, 0.0, 1.0), (-2.5, 0.0, 1.0), (0.0, 0.0, -4.5))

# --- Dining room: floating objects (true evidence) and a key in the most obvious place
box("dining_table", WOOD, -12.0, -6.0, 0.75, 0.9, -1.2, 0.8, uv=[2.2, 0.4])
for i, (x, z) in enumerate([(-11.7, -0.9), (-6.3, -0.9), (-11.7, 0.5), (-6.3, 0.5)]):
    box(f"dining_leg_{i}", WOOD, x - 0.08, x + 0.08, 0.0, 0.75, z - 0.08, z + 0.08, solid=False)
light(-9.0, 3.0, -1.0, [1.0, 0.74, 0.5], 9.0)
torch("torch_dining", -13.65, 2.0, -1.0, 90.0)
readable("dining_floating", -9.0, 1.1, -0.2, "Look at the Table Settings", "The Table Is Laid",
         ("The long table is laid for twelve. Silver, crystal, folded napkins shaped like swans.\n\nAs you watch, a fork lifts "
          "itself off the tablecloth, turns slowly in the air, and settles back down a finger's width to the left, exactly in line "
          "with its neighbours. Then a spoon does the same. Then a whole place setting shuffles over to make room for a guest "
          "who isn't there.\n\nFLOATING OBJECTS. Somebody is setting the table. Somebody who has been setting it for a very long time."),
         set_flag="ev_floating")
interactables.append({"instance_id": "dining_key_plate", "type": "chest", "model": "assets/models/props/treasure_chest.glb",
                      "pos": [-12.8, 0.0, 4.6], "rot_y": 0.0, "locked": False, "loot_table": "core:loot.vermin_drop",
                      "prompt": "Sideboard Drawer (labelled 'STUDY KEY - DO NOT LOOK HERE')", "fixed_items": ["core:item.study_key"]})
creature("dining_footman", "core:enemy.wailing_footman", (-9.0, 0.0, 3.4), (-12.5, 0.0, 3.4), (-6.0, 0.0, 3.4))

# --- Library: bestsellers and the oldest search in the game
for i, (x, z, r) in enumerate([(13.6, -6.0, -90), (13.6, -3.0, -90), (13.6, 0.0, -90), (13.6, 3.0, -90), (6.0, -7.6, 0), (10.0, -7.6, 0)]):
    prop(f"lib_shelf_{i}", "assets/models/props/bookshelf_prop.glb", x, 0.0, z, rot=r)
light(9.0, 3.0, -1.0, [1.0, 0.82, 0.6], 9.5)
readable("library_bestsellers", 8.0, 0.0, 2.6, "Browse the Bestseller Stand", "Hollowmere Library: Most Borrowed",
         ("A brass placard: MOST BORROWED THIS CENTURY.\n\n"
          "1. 'Dusk' - A girl moves to a rainy town and falls for a three-hundred-year-old who still attends school, on purpose.\n"
          "2. 'Moon of Longing' - The sequel. The same girl, but now a wolf with abs is also involved. Nobody wears a shirt.\n"
          "3. 'A Lament of Frost and Furnace, Vol. 6' - The author promises Vol. 7 'soon'. The placard is very old.\n"
          "4. 'The Boy Who Was Prophesied' - Seven volumes. The prophecy turns out to be about a different boy.\n"
          "5. 'The Fellowship of the Very Long Walk' - Three hundred pages of walking. Twelve of fighting. Forty of songs.\n"
          "6. 'Fifty Shades of Grey Robes' - An archivist romance. Fenwick has borrowed it eleven times. Fenwick denies this.\n"
          "7. 'So You've Been Chosen' - A self-help pamphlet for farm boys with mysterious birthmarks.\n\n"
          "Somebody has written 'TEAM ROLF' in the margin of the second book, and 'TEAM ASHGRAVE' beneath it, and the two have been "
          "arguing in the margins for several pages."), model=LECTERN, rot=180.0)
readable("library_search", 11.0, 0.8, -6.6, "Search for Treasure", "You Search for Treasure",
         ("You search the library for treasure.\n\nYou find... nothing.\n\nSomewhere, a deep and booming voice you can't quite "
          "place adds, with enormous satisfaction: \"A WANDERING MONSTER APPEARS.\"\n\nNo monster appears. The voice sounds "
          "disappointed."))
readable("library_rules", 5.0, 0.8, -6.6, "Read the Rulebook on the Floor", "Page 212 of a Very Thick Rulebook",
         ("A heavy rulebook lies open, its margins crowded with arguments in at least six different hands.\n\n"
          "\"Technically, page 212 says a crossbow can be fired while falling.\" - \"It does NOT say that.\" - \"It doesn't say "
          "you CAN'T.\" - \"We are not doing this again.\" - \"I cast Fireball on the rules discussion.\" - \"You can't, you're a "
          "Fighter.\" - \"Page 212.\"\n\nSomeone has drawn a very small, very sad dragon at the bottom, with a speech bubble: "
          "\"can we please just play.\""))

# --- Kitchen: the rat problem's source, claw marks, a very particular bucket
box("kitchen_counter", WOOD, -13.6, -9.0, 0.0, 0.95, 14.6, 15.6, uv=[2, 0.4])
light(-9.0, 3.0, 11.0, [1.0, 0.7, 0.45], 9.0)
torch("torch_kitchen", -9.0, 2.0, 15.65, 180.0)
readable("kitchen_claws", -13.4, 1.2, 9.8, "Examine the Claw Marks", "Claw Marks on the Back Door Frame",
         ("Deep gouges, four at a time, scored into the frame of the kitchen's back door at about head height.\n\n"
          "Something big came in this way. Something with claws, that walks on two legs, that apparently also wiped its feet on the "
          "mat afterwards, because the mat is spotless.\n\nIt LOOKS like evidence. You note it down."), set_flag="clue_claws")
interactables.append({"instance_id": "kitchen_bucket", "type": "pickup", "item_id": "core:item.dented_bucket", "qty": 1, "pos": [-12.5, 1.15, 15.1]})
for i, (x, z) in enumerate([(-7.0, 9.0), (-11.0, 8.0), (-6.0, 13.5)]):
    creature(f"kitchen_rat_{i}", "core:enemy.grave_rat", (x, 0.0, z), (x - 1.5, 0.0, z), (x + 1.5, 0.0, z),
             group="rat_king", group_quest_id=QUEST_RATS, group_set_stage=40)
creature("rat_king", "core:enemy.rat_king", (-9.5, 0.0, 12.0), (-11.0, 0.0, 12.0), (-8.0, 0.0, 12.0),
         group="rat_king", group_quest_id=QUEST_RATS, group_set_stage=40)

# --- Ballroom: the cold spot (true evidence), the gramophone, and the Host
for i, x in enumerate((0.0, 6.0, 12.0)):
    prop(f"ball_pillar_{i}", PILLAR, x, 0.0, 11.0, scale=(1.0, 1.0, 1.0))
light(5.0, 3.2, 11.0, [0.55, 0.7, 1.0], 13.0)
torch("torch_ball_e", 13.65, 2.0, 9.0, -90.0, ghost=True)
torch("torch_ball_w", -3.65, 2.0, 13.0, 90.0, ghost=True)
readable("ballroom_cold", 3.0, 1.2, 13.6, "Stand in the Cold Patch", "A Cold Spot",
         ("You step into the middle of the dance floor and your breath turns to frost in front of your face. It is much, much colder "
          "here than anywhere else in the room. The cold has a shape: a little circle, the size of one person standing still, "
          "waiting to be asked to dance.\n\nCOLD SPOTS. You write it down with fingers that have gone stiff."), set_flag="ev_cold")
readable("ballroom_gramophone", 9.0, 0.0, 15.2, "Wind the Gramophone", "The Gramophone",
         ("A beautiful brass gramophone with a horn like a lily. The record on it is labelled 'For My Guests - The Last Waltz'.\n\n"
          "You wind it. It plays four bars of a waltz, skips, and plays the same four bars again. And again. Somewhere above you, "
          "very faintly, something hums along."), model=LECTERN, rot=0.0)
npcs.append({"instance_id": "npc_percival", "npc_id": "core:npc.ghost_percival", "pos": [6.0, 0.0, 13.6], "yaw": 180.0,
             "requires_flag": "host_identified", "hidden_flag": "host_banish"})
creature("wrathful_host", "core:enemy.wrathful_host", (6.0, 0.0, 12.5), (2.0, 0.0, 12.5), (10.0, 0.0, 12.5),
         requires_flag="host_banish", group="host", group_quest_id=QUEST_HAUNT, group_set_stage=100, group_set_flag="host_banished")

# ============================================================================ upper floor
U = H1
wall_z("u_landing_w", -4.0, -7.7, 6.0, U, TOP, gaps=[(-3.0, -1.0)])
wall_z("u_landing_e", 4.0, -7.7, 6.0, U, TOP, gaps=[(3.8, 5.6)])
wall_x("u_mid", 6.0, -13.7, 13.7, U, TOP, gaps=[(-1.0, 1.0)])
wall_z("u_sealed", 8.0, 6.0, 15.7, U, TOP, gaps=[(10.0, 12.0)])
interactables.append({"instance_id": "study_door", "type": "door", "model": DOOR, "pos": [4.0, U, 4.7], "rot_y": 90.0,
                      "locked": True, "key_id": "core:item.study_key", "lock_difficulty": 12, "prompt": "Study Door"})
interactables.append({"instance_id": "sealed_door", "type": "door", "model": "assets/models/props/iron_gate.glb", "pos": [8.0, U, 11.0],
                      "rot_y": 90.0, "locked": True, "mechanism_only": True, "prompt": "Sealed Room (a lever somewhere opens this)"})
light(0.0, U + 3.0, -2.0, [1.0, 0.8, 0.55], 10.0)
torch("torch_landing", -3.65, U + 2.0, 2.0, 90.0)

# --- Master bedroom: the vampire's coffin and the bitten decanter
prop("coffin", "assets/models/props/sarcophagus.glb", -11.0, U, -4.0, rot=90.0)
box("bed", WOOD, -13.6, -11.0, U, U + 0.6, 1.5, 5.0, uv=[1, 0.3])
light(-9.0, U + 3.0, -1.0, [0.9, 0.35, 0.4], 9.0)
readable("bedroom_decanter", -6.0, U + 1.0, -6.8, "Examine the Decanters", "Sherry Decanters, Bitten",
         ("A row of crystal decanters on the dresser. Every one of them has two neat little puncture holes in the stopper, as if "
          "someone tried to drink through them with their teeth.\n\nThey all contain beetroot juice.\n\nIt LOOKS like evidence. "
          "You note it down, slightly confused."), set_flag="clue_bites")
npcs.append({"instance_id": "npc_ashgrave", "npc_id": "core:npc.vampire_ashgrave", "pos": [-9.0, U, -5.5], "yaw": 150.0})

# --- Study (locked): ghost writing (true evidence), the lever, the missing puzzle
box("study_desk", WOOD, 7.0, 11.0, U, U + 0.85, -6.8, -5.6, uv=[1.5, 0.4])
light(9.0, U + 3.0, -2.0, [1.0, 0.85, 0.6], 9.0)
readable("study_writing", 9.0, U + 1.05, -6.2, "Read the Open Journal", "Sir Percival's Guest Book",
         ("A leather guest book lies open on the desk with a quill beside it. The last hundred pages are blank, every one of them "
          "headed with a date, as if waiting for signatures that never came.\n\nWhile you watch, the quill lifts on its own, dips "
          "itself in the ink, and writes in a looping, old-fashioned hand:\n\n    you came    you came    please stay for dinner\n\n"
          "GHOST WRITING. Your hand is shaking a little as you note it down."), set_flag="ev_writing")
readable("study_puzzle", 12.6, U + 1.2, -2.0, "Read the Note by the Lever", "A Note from the Architect",
         ("\"To whomever it may concern:\n\nThere was going to be a puzzle here. Four rotating busts, a riddle about the seasons, "
          "and a sliding-tile mural of Sir Percival's prize hound.\n\nAfter the third guest starved to death trying to solve it, Sir "
          "Percival asked us to take it out. The lever opens the sealed room. That's it. That's the whole puzzle. You're welcome.\n\n"
          "- G. Fairweather, Architect\n\nP.S. The answer to the riddle was 'a candle'. It's always a candle.\""))
interactables.append({"instance_id": "study_lever", "type": "lever", "model": "assets/models/props/iron_lever.glb", "pos": [13.6, U, -0.5],
                      "rot_y": -90.0, "target_id": "sealed_door", "prompt": "Pull the Lever (no puzzle required)"})

# --- Portrait gallery: the spirit box that never answers, portraits, the second armour
light(-3.0, U + 3.0, 11.0, [0.75, 0.75, 1.0], 12.0)
torch("torch_gallery_w", -13.65, U + 2.0, 11.0, 90.0, ghost=True)
readable("gallery_spiritbox", -6.0, U, 14.6, "Speak into the Spirit Trumpet", "The Spirit Trumpet",
         ("A brass speaking-trumpet on a stand, the kind ghost-hunters swear by. You lean in and ask, very politely: \"Is anyone "
          "here? Give us a sign.\"\n\nStatic.\n\n\"Where are you?\"\n\nStatic.\n\n\"How old are you?\"\n\nA long pause. Then, very "
          "faintly, from somewhere downstairs: four bars of a waltz, skipping.\n\nNo voice. No answer. NOT spirit box evidence, then. "
          "Whatever lives here doesn't want to chat through a trumpet. It wants company."), model=LECTERN, rot=0.0,
         set_flag="spirit_box_tried")
portraits = [
    ("Portrait: Sir Percival at Thirty", "A handsome young man in a velvet coat, laughing, a glass raised. The plaque reads: "
     "'Host of the Year, eleven years running.' In the background of the painting, a crowded ballroom."),
    ("Portrait: Sir Percival at Sixty", "The same man, older, still smiling. The ballroom behind him is half empty. The painter "
     "has been very kind about it."),
    ("Portrait: Sir Percival at Ninety", "An old man sitting alone at a very long table laid for twelve. He is still smiling. The "
     "smile has not reached his eyes for some time."),
    ("Portrait: A Monster Hunter", "A grizzled, white-haired man with two swords, scowling at the painter. The painting is titled "
     "'Hmm.' He is holding a hand of cards behind his back."),
]
for i, (title, text) in enumerate(portraits):
    readable(f"gallery_portrait_{i}", -12.0 + i * 3.6, U + 1.6, 15.65, "Look at the Portrait", title, text)
creature("gallery_armor", "core:enemy.animated_armor", (-6.0, U, 9.0), (-12.0, U, 9.0), (4.0, U, 9.0))
creature("gallery_footman", "core:enemy.wailing_footman", (-10.0, U, 12.5), (-12.5, U, 12.5), (-2.0, U, 12.5))

# --- Sealed room: the treasure, such as it is
light(11.0, U + 3.0, 11.0, [1.0, 0.85, 0.5], 8.0)
interactables.append({"instance_id": "sealed_chest", "type": "chest", "model": "assets/models/props/treasure_chest.glb",
                      "pos": [11.0, U, 14.6], "rot_y": 180.0, "locked": False, "loot_table": "core:loot.crypt_elite",
                      "fixed_items": ["core:item.party_hat", "core:item.tome_frost", "core:item.health_potion"]})
readable("sealed_note", 12.6, U + 1.2, 8.6, "Read the Note on the Chest", "A Note Taped to the Treasure",
         ("\"Congratulations on finding the Secret Treasure of Hollowmere!\n\nIt's a party hat. I'm sorry. I had it made for "
          "my last party. Nobody came, so nobody wore it.\n\nThey always say the real treasure is the friends you made along the "
          "way. I never made any. Perhaps you could wear it for me, the next time you're somewhere with friends.\n\n- P.\""))

region = {
    "schema_version": 1,
    "id": "core:map.hollowmere",
    "display_name_key": "map.hollowmere.name",
    "music": "assets/audio/music/vault_lullaby.wav",
    "ambience": "assets/audio/ambience/village_rain.wav",
    "sky_color": [20, 24, 40],
    "ambient_color": [0.36, 0.38, 0.52],
    "sun_direction": [-0.3, 0.8, -0.4],
    "sun_color": [0.45, 0.45, 0.62],
    "fog_color": [0.09, 0.11, 0.18],
    "fog_density": 0.026,
    "weather": "rain",
    "spawns": {"hollowmere_gate": {"pos": [0.0, 0.0, -19.0], "yaw_degrees": 0.0}},
    "props": props,
    "lights": lights,
    "npcs": npcs,
    "creatures": creatures,
    "interactables": interactables,
    "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables, %d creatures, %d npcs" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                      len(creatures), len(npcs)))

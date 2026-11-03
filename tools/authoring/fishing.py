"""Fishing and cooking: a rod (Silas has a spare), fishing spots at Saltmere, the Reef and a new pond in the Whistling
Wood, catches (fish, junk, one or two oddities), cooking pots and meals that give build buffs.

ARCHIVE: this one-off authoring script already ran (its output lives in content/ and the region builder scripts).
Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
CI = load("content/items/consumables_and_books.json")
def item(iid, name, desc, cat="misc", value=3, icon=None, model="assets/models/items/bread_loaf.glb", effects=None, book=None, stack=True):
    e = {"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": cat,
         "icon": f"assets/ui/items/{icon or iid}.png", "world_model": model, "slots": [], "stackable": stack, "value": value, "weight": 0.3}
    if effects: e["effects"] = effects
    if book:
        e["book_text_key"] = f"book.{iid}.text"
        S[f"book.{iid}.text"] = book
    CI["items"].append(e)
    S[f"item.{iid}.name"] = name
    S[f"item.{iid}.description"] = desc

FISH = "assets/models/items/grave_truffle.glb"
item("fishing_rod", "Fishing Rod", "Ashwood, gut line, a hook Silas swears by. Stand by water and cast. Press interact the moment something bites.",
     value=15, model="assets/models/items/oak_staff.glb", stack=False)
item("fish_cod", "Saltmere Cod", "A fat grey cod. Edible raw, if you're desperate. Much better cooked.", "consumable", 6, model=FISH,
     effects=[{"type": "consumable_heal", "amount": 8}])
item("fish_mackerel", "Mackerel", "Striped, oily, and looking at you. Edible raw. Better smoked.", "consumable", 5, model=FISH,
     effects=[{"type": "consumable_heal", "amount": 6}])
item("fish_perch", "Pond Perch", "A small, spiny, cheerful fish from the Whistling Wood pond.", "consumable", 4, model=FISH,
     effects=[{"type": "consumable_heal", "amount": 5}])
item("fish_trout", "A Trout (Fish)", "A speckled trout. Not the horse. Hollis will want to know why you're laughing.", "consumable", 9, model=FISH,
     effects=[{"type": "consumable_heal", "amount": 8}])
item("fish_eel", "Eldritch Eel", "Too many eyes. One of them winked. Eating it raw costs you some sanity; cooking it costs you some dignity.", "consumable", 14,
     model=FISH, effects=[{"type": "consumable_heal", "amount": 10}, {"type": "consumable_sanity", "amount": -8}])
item("old_boot", "An Old Boot", "Waterlogged. There's a smaller boot inside it. Inside that, a crab, who is not pleased.", value=1)
item("grumpy_frog", "A Grumpy Frog", "It is grumpy. It will not be kissed. It has been asked.", value=2)
item("glimmering_pearl", "Glimmering Pearl", "A pearl that glows faintly green from the inside. Worth a fortune to the right merchant. It hums when you hold it.",
     value=90)
item("bottle_message", "A Message in a Bottle", "Corked, salt-crusted, with a letter inside.", "book", 2, model="assets/models/items/vallo_red.glb", stack=False,
     book="Rolled up inside the bottle, in a careful hand:\n\n\"To whoever finds this,\n\nIf you are reading this, I have either been rescued or very much not. "
          "I am on an island. There is a lighthouse. There is a horse on the lighthouse. I did not bring the horse. Nobody brought the horse.\n\n"
          "I am going to throw this bottle into the sea and then I am going to try to make friends with the horse.\n\n-B. Fenn\n\n"
          "P.S. If you see a very large fish, please let it know I am still looking for it.\"")
MEALS = [
    ("grilled_cod", "Grilled Cod", "Crisp skin, flaky inside, a squeeze of salt. Heals 30, then +1.5 health per second for three minutes.",
     [{"type": "consumable_heal", "amount": 30}, {"type": "buff", "stat": "health_regen", "value": 1.5, "duration": 180}]),
    ("smoked_mackerel", "Smoked Mackerel", "Smoked over pine resin until it tastes of a whole forest and a whole sea. Heals 25, +3 stamina per second for three minutes.",
     [{"type": "consumable_heal", "amount": 25}, {"type": "buff", "stat": "stamina_regen", "value": 3.0, "duration": 180}]),
    ("saltmere_chowder", "Saltmere Chowder (Brine's Recipe)", "Thick, creamy, unreasonably good. Heals 40, +1 sanity per second for five minutes. Mother Brine will deny giving you the recipe.",
     [{"type": "consumable_heal", "amount": 40}, {"type": "buff", "stat": "sanity_regen", "value": 1.0, "duration": 300}]),
    ("eel_pie", "Eldritch Eel Pie", "The eyes have been baked shut. Mostly. +12% spell power for four minutes, -5 sanity. Worth it.",
     [{"type": "consumable_heal", "amount": 20}, {"type": "consumable_sanity", "amount": -5}, {"type": "buff", "stat": "spell_power_bonus", "value": 0.12, "duration": 240}]),
    ("trout_hollis", "Trout à la Hollis", "Grilled with marigold petals. +8% critical chance for four minutes. Hollis tried it, said 'Hmm', and had seconds.",
     [{"type": "consumable_heal", "amount": 25}, {"type": "buff", "stat": "crit_chance_bonus", "value": 0.08, "duration": 240}]),
    ("perch_skewers", "Perch Skewers", "Little fish on sticks with sage. Heals 20, +8% movement speed for four minutes.",
     [{"type": "consumable_heal", "amount": 20}, {"type": "buff", "stat": "move_speed_bonus", "value": 0.08, "duration": 240}]),
]
for iid, name, desc, eff in MEALS:
    item(iid, name, desc, "consumable", 20, model="assets/models/items/bread_loaf.glb", effects=eff)
save("content/items/consumables_and_books.json", CI)

R = load("content/recipes/recipes.json")
for rid, res, ing in [("grilled_cod", "grilled_cod", [("fish_cod", 1), ("sea_salt", 1)]),
                      ("smoked_mackerel", "smoked_mackerel", [("fish_mackerel", 1), ("pine_resin", 1)]),
                      ("saltmere_chowder", "saltmere_chowder", [("fish_cod", 1), ("fish_mackerel", 1), ("wayside_sage", 1)]),
                      ("eel_pie", "eel_pie", [("fish_eel", 1), ("bread_loaf", 1)]),
                      ("trout_hollis", "trout_hollis", [("fish_trout", 1), ("marigold", 1)]),
                      ("perch_skewers", "perch_skewers", [("fish_perch", 2), ("wayside_sage", 1)])]:
    R["recipes"].append({"id": f"core:recipe.{rid}", "station": "cooking", "result": f"core:item.{res}", "qty": 1,
                         "ingredients": [{"item": f"core:item.{i}", "qty": n} for i, n in ing], "skill": "restoration", "skill_level": 0})
save("content/recipes/recipes.json", R)

LT = load("content/loot_tables/core_loot.json")
LT["loot_tables"] += [
    {"id": "core:loot.fish_harbour", "gold_min": 0, "gold_max": 0, "entries": [
        {"item_id": "core:item.fish_cod", "weight": 40, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.fish_mackerel", "weight": 35, "min_qty": 1, "max_qty": 1},
        {"item_id": "core:item.fish_eel", "weight": 7, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.old_boot", "weight": 10, "min_qty": 1, "max_qty": 1},
        {"item_id": "core:item.bottle_message", "weight": 3, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.bladderwrack", "weight": 5, "min_qty": 1, "max_qty": 2}]},
    {"id": "core:loot.fish_reef", "gold_min": 0, "gold_max": 0, "entries": [
        {"item_id": "core:item.fish_mackerel", "weight": 30, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.fish_eel", "weight": 25, "min_qty": 1, "max_qty": 1},
        {"item_id": "core:item.glimmering_pearl", "weight": 8, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.fish_cod", "weight": 20, "min_qty": 1, "max_qty": 1},
        {"item_id": "core:item.bottle_message", "weight": 4, "min_qty": 1, "max_qty": 1}]},
    {"id": "core:loot.fish_pond", "gold_min": 0, "gold_max": 0, "entries": [
        {"item_id": "core:item.fish_perch", "weight": 45, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.fish_trout", "weight": 25, "min_qty": 1, "max_qty": 1},
        {"item_id": "core:item.old_boot", "weight": 10, "min_qty": 1, "max_qty": 1}, {"item_id": "core:item.grumpy_frog", "weight": 12, "min_qty": 1, "max_qty": 1}]},
]
save("content/loot_tables/core_loot.json", LT)

# ---------------------------------------------------------------- Silas's spare rod, Vaelen's stock
D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
sn = DL["core:dialogue.silas_gale"]["nodes"]
ch = sn["root"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
S["dlg.silas.rod.t"] = '"Silas, have you got a spare fishing rod?"'
ch.insert(idx, {"text_key": "dlg.silas.rod.t", "next": "rod", "conditions": [{"type": "flag_not_set", "flag": "silas_rod"}]})
S["dlg.silas.rod"] = ("Silas looks at you, then at his own line, which has no hook on it, and laughs: a dry, surprised sound.\n\n"
                      "\"A spare. I've got nine. Made one for every lad who ever said he'd come fishing with me, and most of them never did.\"\n\n"
                      "He fishes one out from under the pier: ashwood, gut line, a proper hook. \"Cast it out. Watch the float. When it dips, PULL. "
                      "Not before. Not after. The sea's not patient, but it's fair.\"\n\n\"And if you catch anything with more than two eyes, throw it back. "
                      "Or bake it. Brine does a pie.\"")
S["dlg.silas.rod.c0"] = '"Thank you, Silas."'
sn["rod"] = {"speaker_key": "npc.silas_gale.name", "text_key": "dlg.silas.rod",
             "actions": [{"type": "give_item", "item_id": "core:item.fishing_rod", "qty": 1}, {"type": "set_flag", "flag": "silas_rod", "value": True}],
             "choices": [{"text_key": "dlg.silas.rod.c0", "next": "root"}]}
save("content/dialogue/chapter_zero_dialogue.json", D)
N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.merchant_vaelen":
        n["vendor_inventory"].append({"item_id": "core:item.fishing_rod", "stock": 2, "price": 15})
save("content/npcs/core_npcs.json", N)

# ---------------------------------------------------------------- spots, the pond, cooking pots
def spot(iid, x, y, z, table, prompt="Fish here"):
    return {"instance_id": iid, "type": "fishing", "model": "", "pos": [x, y, z], "rot_y": 0.0, "loot_table": table, "prompt": prompt}
FLAME = lambda pid, x, z: {"id": pid, "model": "assets/models/props/wall_torch.glb", "pos": [x, -0.55, z], "rot_y": 0.0, "scale": [1, 1, 1], "solid": False,
                           "emitter": {"sprite": "assets/sprites/vfx/torch_flame.png", "offset": [0.0, 0.86, 0.0], "size": 0.4,
                                       "light_color": [1.0, 0.6, 0.3], "light_radius": 5.0}}
POT = lambda iid, x, z, rot, prompt: {"instance_id": iid, "type": "station", "station": "cooking", "model": "assets/models/props/cooking_pot.glb",
                                      "pos": [x, 0.0, z], "rot_y": rot, "prompt": prompt}
GEN = {
    "tools/build_docks.py": ("interactables.append(" + json.dumps(spot("fish_pier_a", -10.5, 0.0, -25.4, "core:loot.fish_harbour", "Fish off the pier")) + ")\n"
                             "interactables.append(" + json.dumps(spot("fish_pier_b", 10.8, 0.0, -21.6, "core:loot.fish_harbour", "Fish off the pier")) + ")\n"
                             "interactables.append(" + json.dumps(spot("fish_quay", -5.0, 0.0, -9.6, "core:loot.fish_harbour", "Fish from the quay")) + ")\n"
                             "interactables.append(" + json.dumps(POT("docks_cooking_pot", -10.6, 13.0, 0.0, "Cook at Mother Brine's Pot")) + ")\n"
                             "props.append(" + json.dumps(FLAME("docks_pot_fire", -10.6, 13.0)) + ")\n"),
    "tools/build_reef.py": ("interactables.append(" + json.dumps(spot("fish_jetty", 0.0, 0.0, 20.6, "core:loot.fish_reef", "Fish off the jetty")) + ")\n"),
    "tools/build_wood.py": ("# The pond\n"
                            "props.append({\"id\": \"pond_water\", \"model\": \"assets/models/env/harbour_water.glb\", \"pos\": [-16.0, 0.02, -0.5], \"rot_y\": 0.0,"
                            " \"scale\": [0.08, 1.0, 0.15], \"solid\": False})\n"
                            "for _k in range(10):\n"
                            "    _a = _k * 0.628\n"
                            "    box(f\"pond_rim_{_k}\", STONE, -16.0 + math.cos(_a) * 2.1 - 0.25, -16.0 + math.cos(_a) * 2.1 + 0.25, 0.0, 0.18,"
                            " -0.5 + math.sin(_a) * 2.0 - 0.25, -0.5 + math.sin(_a) * 2.0 + 0.25, solid=False, uv=[0.3, 0.1])\n"
                            "interactables.append(" + json.dumps(spot("fish_pond", -16.0, 0.0, -0.5, "core:loot.fish_pond", "Fish in the pond")) + ")\n"),
}
for path, block in GEN.items():
    src = open(path).read()
    if path.endswith("build_wood.py") and "import math" not in src:
        src = src.replace("import json\n", "import json\nimport math\n", 1)
    src = src.replace("region = {", "# ============================================================================ fishing & cooking (tools/authoring/fishing.py)\n"
                      + block + "\nregion = {", 1)
    open(path, "w").write(src)
B = load("content/regions/bellwether.json")
B["interactables"].append(POT("bell_cooking_pot", -3.2, 13.4, 0.0, "Cook at Marta's Hearth"))
B["props"].append(FLAME("bell_pot_fire", -3.2, 13.4))
save("content/regions/bellwether.json", B)

S["tip.36"] = "Fishing: cast, watch the float, and press interact the instant it bites. Too early and it's gone. Silas has a spare rod."
S["tip.37"] = "Anything caught with more than two eyes should be thrown back. Or baked into a pie. Mother Brine recommends the pie."
loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

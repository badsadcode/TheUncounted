"""Gathering, alchemy and the workbench: materials, harvest nodes in every region, recipes, potions, weapon oils,
two kinds of crafting station.

ARCHIVE: this one-off authoring script already ran (its output lives in content/ and the region builder scripts).
Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
PROPS = "assets/models/props/"

# ---------------------------------------------------------------- materials
MATS = [
    ("marigold", "Marigold", "Bright orange petals. Brother Aldous grows them for the shrine and pretends not to notice them going missing. Healing.", "herb_marigold"),
    ("wayside_sage", "Wayside Sage", "Grey-green, peppery, grows along every road in the Marches. Good for stamina, better for soup.", "herb_sage"),
    ("wolfsbane", "Wolfsbane", "Purple hooded flowers from the Whistling Wood. Rolf asks that you not wave it near him. Makes wounds that won't close.", "herb_wolfsbane"),
    ("glowcap", "Glowcap", "A mushroom that glows faintly blue. Tastes of static. The base of most mana-work.", "mushroom_glowcap"),
    ("grave_moss", "Grave Moss", "Soft, dark moss that only grows on graves. Calms the mind. Nobody asks why.", "moss_grave"),
    ("bladderwrack", "Bladderwrack", "Saltmere seaweed, rubbery and cold. Holds a chill like nothing else.", "seaweed"),
    ("sea_salt", "Sea Salt", "Crusted on the quay stones by the tide. Preserves, purifies, and keeps very old things asleep.", "salt_crust"),
    ("iron_scrap", "Iron Ore", "A lump of rusty iron ore. Arrowheads, lockpicks, whetstones.", "ore_iron"),
    ("ashwood_branch", "Ashwood Branch", "Straight, pale and springy. Arrows, handles, walking sticks for people who refuse to admit they need one.", "branches_ash"),
    ("pine_resin", "Pine Resin", "Sticky amber resin from old stumps. Burns hot and slow. Smells like a whole forest at once.", "resin_stump"),
]
CI = load("content/items/consumables_and_books.json")
for iid, name, desc, model in MATS:
    CI["items"].append({"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": "misc",
                        "icon": f"assets/ui/items/{iid}.png", "world_model": PROPS + model + ".glb", "slots": [], "stackable": True,
                        "value": 3, "weight": 0.05})
    S[f"item.{iid}.name"] = name
    S[f"item.{iid}.description"] = desc + " (Crafting material.)"

# ---------------------------------------------------------------- products
OILS = [("oil_fire", "Dragon's Breath Oil", "burn", 0.45, 5, 120, "Coat your weapon: for two minutes, hits have a 45% chance to set the target on fire. Arrows count."),
        ("oil_frost", "Rimewater Oil", "chill", 0.5, 0, 120, "For two minutes, your hits have a 50% chance to chill. Three chills and they freeze."),
        ("oil_storm", "Stormglass Oil", "shock", 0.4, 0, 120, "For two minutes, your hits have a 40% chance to shock (+25% damage taken)."),
        ("oil_venom", "Wolfsbane Venom", "bleed", 0.5, 3, 120, "For two minutes, your hits have a 50% chance to cause bleeding. Bleeding stacks three times."),
        ("oil_ink", "Ink of Obscurity", "ink", 0.35, 0, 120, "For two minutes, your hits have a 35% chance to blind the target.")]
for iid, name, status, chance, power, dur, desc in OILS:
    CI["items"].append({"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": "consumable",
                        "icon": f"assets/ui/items/{iid}.png", "world_model": "assets/models/items/potion_flask.glb", "slots": [], "stackable": True,
                        "value": 30, "weight": 0.3,
                        "effects": [{"type": "weapon_oil", "stat": status, "value": chance, "amount": power, "duration": dur}]})
    S[f"item.{iid}.name"] = name
    S[f"item.{iid}.description"] = desc + " Only one oil at a time."
CI["items"] += [
    {"id": "core:item.quiet_mind_tea", "name_key": "item.quiet_mind_tea.name", "description_key": "item.quiet_mind_tea.description", "category": "consumable",
     "icon": "assets/ui/items/quiet_mind_tea.png", "world_model": "assets/models/items/potion_flask.glb", "slots": [], "stackable": True, "value": 25, "weight": 0.3,
     "effects": [{"type": "consumable_sanity", "amount": 40}, {"type": "buff", "stat": "sanity_regen", "value": 1.0, "duration": 180}]},
    {"id": "core:item.bureaucrats_brew", "name_key": "item.bureaucrats_brew.name", "description_key": "item.bureaucrats_brew.description", "category": "consumable",
     "icon": "assets/ui/items/bureaucrats_brew.png", "world_model": "assets/models/items/potion_flask.glb", "slots": [], "stackable": True, "value": 45, "weight": 0.3,
     "effects": [{"type": "buff", "stat": "combo_damage_bonus", "value": 0.4, "duration": 240}, {"type": "buff", "stat": "status_duration_bonus", "value": 0.25, "duration": 240}]},
    {"id": "core:item.whetstone", "name_key": "item.whetstone.name", "description_key": "item.whetstone.description", "category": "consumable",
     "icon": "assets/ui/items/whetstone.png", "world_model": "assets/models/items/annex_key.glb", "slots": [], "stackable": True, "value": 15, "weight": 0.3,
     "effects": [{"type": "buff", "stat": "melee_bonus_magic_damage", "value": 4, "duration": 300}]},
    {"id": "core:item.hunters_draught", "name_key": "item.hunters_draught.name", "description_key": "item.hunters_draught.description", "category": "consumable",
     "icon": "assets/ui/items/hunters_draught.png", "world_model": "assets/models/items/potion_flask.glb", "slots": [], "stackable": True, "value": 35, "weight": 0.3,
     "effects": [{"type": "buff", "stat": "crit_chance_bonus", "value": 0.1, "duration": 240}, {"type": "buff", "stat": "move_speed_bonus", "value": 0.1, "duration": 240}]},
]
save("content/items/consumables_and_books.json", CI)
S.update({
    "item.quiet_mind_tea.name": "Quiet Mind Tea",
    "item.quiet_mind_tea.description": "Grave moss, marigold and a pinch of sea salt. Restores 40 sanity and steadies you for three minutes. Mother Brine's grandmother's recipe. Tastes like a rainy afternoon.",
    "item.bureaucrats_brew.name": "Bureaucrat's Brew",
    "item.bureaucrats_brew.description": "Fizzing, blue, and faintly smells of toner. For four minutes: Shatter and Overload hit 40% harder and status effects last 25% longer.",
    "item.whetstone.name": "Whetstone",
    "item.whetstone.description": "A gritty stone and a lot of patience. For five minutes, your melee hits deal +4 damage.",
    "item.hunters_draught.name": "Hunter's Draught",
    "item.hunters_draught.description": "Sage, resin and something with teeth in it. For four minutes: +10% critical chance and +10% movement speed.",
})

# ---------------------------------------------------------------- recipes
R = [
    ("health_potion", "alchemy", "core:item.health_potion", 1, [("marigold", 2), ("wayside_sage", 1)], "restoration", 0),
    ("mana_potion", "alchemy", "core:item.mana_potion", 1, [("glowcap", 2), ("sea_salt", 1)], "restoration", 0),
    ("stamina_tonic", "alchemy", "core:item.stamina_tonic", 1, [("wayside_sage", 2), ("pine_resin", 1)], "restoration", 0),
    ("quiet_mind_tea", "alchemy", "core:item.quiet_mind_tea", 1, [("grave_moss", 1), ("marigold", 1), ("sea_salt", 1)], "restoration", 0),
    ("oil_fire", "alchemy", "core:item.oil_fire", 1, [("pine_resin", 2), ("marigold", 1)], "elemental", 0),
    ("oil_frost", "alchemy", "core:item.oil_frost", 1, [("bladderwrack", 2), ("sea_salt", 1)], "elemental", 0),
    ("oil_storm", "alchemy", "core:item.oil_storm", 1, [("glowcap", 2), ("iron_scrap", 1)], "elemental", 8),
    ("oil_venom", "alchemy", "core:item.oil_venom", 1, [("wolfsbane", 2), ("pine_resin", 1)], "lore", 0),
    ("oil_ink", "alchemy", "core:item.oil_ink", 1, [("grave_moss", 2), ("glowcap", 1)], "illusion", 8),
    ("hunters_draught", "alchemy", "core:item.hunters_draught", 1, [("wayside_sage", 1), ("pine_resin", 1), ("wolfsbane", 1)], "lore", 10),
    ("bureaucrats_brew", "alchemy", "core:item.bureaucrats_brew", 1, [("glowcap", 1), ("bladderwrack", 1), ("pine_resin", 1), ("sea_salt", 1)], "lore", 14),
    ("arrows", "workbench", "core:item.wooden_arrow", 10, [("ashwood_branch", 1), ("iron_scrap", 1)], "bows", 0),
    ("lockpicks", "workbench", "core:item.lockpick", 3, [("iron_scrap", 2)], "lockpicking", 0),
    ("whetstone", "workbench", "core:item.whetstone", 2, [("iron_scrap", 1), ("sea_salt", 1)], "swords", 0),
    ("wand_sparks", "workbench", "core:item.wand_sparks", 3, [("ashwood_branch", 1), ("glowcap", 2), ("iron_scrap", 1)], "elemental", 12),
    ("wand_frost", "workbench", "core:item.wand_frost", 3, [("ashwood_branch", 1), ("bladderwrack", 2), ("sea_salt", 1)], "elemental", 12),
    ("wand_entry", "workbench", "core:item.wand_entry", 3, [("ashwood_branch", 1), ("iron_scrap", 2)], "lockpicking", 15),
]
import os
os.makedirs("content/recipes", exist_ok=True)
save("content/recipes/recipes.json", {"schema_version": 1, "recipes": [
    {"id": f"core:recipe.{rid}", "station": st, "result": res, "qty": q, "ingredients": [{"item": f"core:item.{i}", "qty": n} for i, n in ing],
     "skill": sk, "skill_level": lv} for rid, st, res, q, ing, sk, lv in R]})
M = load("content/manifest.json")
M["recipes"] = "content/recipes/recipes.json"
save("content/manifest.json", M)

# ---------------------------------------------------------------- harvest nodes and stations
VERB = {"marigold": "Pick", "wayside_sage": "Pick", "wolfsbane": "Pick", "glowcap": "Pick", "grave_moss": "Scrape",
        "bladderwrack": "Gather", "sea_salt": "Scrape", "iron_scrap": "Mine", "ashwood_branch": "Gather", "pine_resin": "Collect"}
MODEL = {m[0]: PROPS + m[3] + ".glb" for m in MATS}
NAME = {m[0]: m[1] for m in MATS}

def node(prefix, mat, x, z, y=0.0, lo=1, hi=2, respawn=480):
    return {"instance_id": f"{prefix}_{mat}_{abs(int(x * 10))}_{abs(int(z * 10))}", "type": "harvest", "model": MODEL[mat], "pos": [x, y, z],
            "rot_y": (x * 37 + z * 11) % 360, "item_id": f"core:item.{mat}", "qty": lo, "qty_max": hi, "respawn_seconds": respawn,
            "prompt": f"{VERB[mat]} {NAME[mat]}"}

HAND = {  # hand-authored regions: append to the region JSON
    "content/regions/bellwether.json": [("marigold", -16.0, -11.0), ("marigold", -12.5, 17.5), ("marigold", 16.5, 2.5), ("wayside_sage", -17.0, -2.5),
                                        ("wayside_sage", 3.5, 17.2)],
    "content/regions/old_road.json": [("wayside_sage", -2.0, 8.0), ("wayside_sage", 14.0, 9.0), ("iron_scrap", 18.0, -11.0), ("iron_scrap", -14.0, -11.0),
                                      ("ashwood_branch", -6.0, 10.0), ("ashwood_branch", 9.0, 11.0), ("pine_resin", 0.0, 11.5), ("marigold", 20.0, 6.0)],
}
for path, nodes in HAND.items():
    reg = load(path)
    for mat, x, z in nodes:
        reg["interactables"].append(node(path.split("/")[-1][:4], mat, x, z))
    if path.endswith("bellwether.json"):
        reg["interactables"].append({"instance_id": "bell_alchemy_bench", "type": "station", "station": "alchemy", "model": PROPS + "alchemy_bench.glb",
                                     "pos": [-10.2, 0.0, 7.4], "rot_y": 90.0, "prompt": "Use the Alchemy Bench"})
        reg["interactables"].append({"instance_id": "bell_workbench", "type": "station", "station": "workbench", "model": PROPS + "workbench.glb",
                                     "pos": [11.0, 0.0, -13.6], "rot_y": 0.0, "prompt": "Use the Workbench"})
    save(path, reg)

GEN = {  # generated regions: inject into the builder script before the region dict
    "tools/build_wood.py": [("wolfsbane", 5.0, 17.5), ("wolfsbane", 15.0, 9.5), ("wolfsbane", -3.0, 16.0), ("glowcap", -10.0, 10.0), ("glowcap", -17.5, 9.0),
                            ("glowcap", -18.0, -8.0), ("pine_resin", -6.0, -17.0), ("pine_resin", 16.0, -12.0), ("ashwood_branch", -7.0, -6.0),
                            ("iron_scrap", -20.0, -17.0), ("marigold", 2.0, 4.0)],
    "tools/build_mansion.py": [("grave_moss", -15.9, -14.0), ("grave_moss", -11.5, -14.0), ("grave_moss", -13.7, -10.8), ("marigold", 16.5, -14.0),
                               ("wolfsbane", 17.0, -10.0)],
    "tools/build_docks.py": [("bladderwrack", 0.0, -9.3), ("bladderwrack", -13.5, -8.6), ("bladderwrack", 12.5, -9.0), ("sea_salt", 17.5, -8.4),
                             ("sea_salt", -18.0, -2.0), ("sea_salt", 4.0, -8.8)],
    "tools/build_reef.py": [("bladderwrack", -8.0, 8.0), ("bladderwrack", 9.0, -2.0), ("sea_salt", 12.0, 3.5), ("sea_salt", -12.0, -1.0),
                            ("glowcap", -3.5, -12.5)],
}
for path, nodes in GEN.items():
    src = open(path).read()
    block = "# ============================================================================ gathering (tools/authoring/crafting.py)\n"
    for mat, x, z in nodes:
        block += "interactables.append(" + json.dumps(node(path.split("_")[-1][:4], mat, x, z)) + ")\n"
    if path.endswith("build_docks.py"):
        block += "interactables.append(" + json.dumps({"instance_id": "docks_alchemy_bench", "type": "station", "station": "alchemy",
                                                       "model": PROPS + "alchemy_bench.glb", "pos": [-17.8, 0.0, 6.2], "rot_y": 90.0,
                                                       "prompt": "Use Mother Brine's Alchemy Bench"}) + ")\n"
    block += "\n"
    src = src.replace("region = {", block + "region = {", 1)
    open(path, "w").write(src)

S["tip.34"] = "Herbs, mushrooms, salt and ore grow back a while after you take them. The Alchemy Bench is in the Lantern Inn; the Workbench is by Vaelen's stall."
S["tip.35"] = "Weapon oils work on arrows too. Rimewater Oil plus Dragon's Breath Oil, one after the other, makes a Shatter waiting to happen."
loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

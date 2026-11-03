"""Deeper crafting: every boss drops a unique reagent; three recipe books (sold by Vaelen, Sabrino and Mother Brine)
teach nine recipes that turn those reagents into build-defining gear, draughts and meals.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
I = lambda n: f"core:item.{n}"

def item(n, name, desc, cat, icon, model, value, weight=0.2, **kw):
    d = {"id": I(n), "name_key": f"item.{n}.name", "description_key": f"item.{n}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": f"assets/models/items/{model}.glb", "slots": kw.pop("slots", []),
         "value": value, "weight": weight}
    d.update(kw)
    S[f"item.{n}.name"] = name
    S[f"item.{n}.description"] = desc
    return d

# ------------------------------------------------------------------ boss reagents
REAGENTS = [
    item("rat_whisker", "Rat King's Whisker", "A single whisker from the Rat King, long as a rapier and twice as sharp. It still twitches when you mention cheese. A crafting reagent.", "misc", "rat_whisker", "seal_quill", 60, 0.05, stackable=True),
    item("ink_heart", "Archivist's Ink Heart", "What was left of Archivist Morvath: a fist-sized knot of black ink that beats, slowly, in time with nothing. A crafting reagent.", "misc", "ink_heart", "potion_flask", 90, 0.4, stackable=True),
    item("host_ember", "Ember of the Wrathful Host", "A coal from Sir Percival's fury, still warm and still faintly offended. A crafting reagent.", "misc", "host_ember", "potion_flask", 90, 0.2, stackable=True),
    item("warden_bell", "The Warden's Silver Bell", "The little bell the Lullaby Warden rang for lights-out. Ring it and you feel sleepy. Don't ring it. A crafting reagent.", "misc", "warden_bell", "potion_flask", 90, 0.2, stackable=True),
    item("name_eater_tooth", "Tooth of the Name-Eater", "A tooth from the Avatar of the Name-Eater. Hold it and, for a moment, you can't remember your own name. A crafting reagent.", "misc", "name_eater_tooth", "potion_flask", 120, 0.3, stackable=True),
    item("dreaming_ink", "Dreaming Ink Sac", "From the Dreaming Limb: a sac of ink that shows you somebody else's dream if you stare too long. A crafting reagent.", "misc", "dreaming_ink", "potion_flask", 80, 0.3, stackable=True),
    item("bonnet_thread", "Grandmother's Bonnet Thread", "A spool of lace from the bonnet of the wolf in grandmother's nightgown. Unreasonably strong. Smells of biscuits. A crafting reagent.", "misc", "bonnet_thread", "potion_flask", 60, 0.1, stackable=True),
]
# ------------------------------------------------------------------ crafted results
RESULTS = [
    item("whiskerblade", "Whiskerblade", "A dagger made around the Rat King's whisker. Quick, mean, and it makes things bleed. Rats nearby go very quiet when you draw it.", "weapon", "whiskerblade", "steel_dagger", 220, 0.9, slots=["main_hand"],
         weapon={"kind": "melee", "skill": "daggers", "damage_type": "piercing", "base_damage": 13, "attack_time_seconds": 0.33, "stamina_cost": 5,
                 "reach_meters": 1.75, "crit_chance": 0.22, "crit_mult": 2.1, "on_hit_status": "bleed", "status_chance": 0.4, "status_power": 4, "status_duration": 4.0}),
    item("hostbrand", "Hostbrand", "A longsword quenched in the Wrathful Host's ember. It's always slightly warmer than the room, and sets enemies alight when it's in the mood.", "weapon", "hostbrand", "iron_longsword", 320, 3.0, slots=["main_hand"],
         weapon={"kind": "melee", "skill": "swords", "damage_type": "fire", "base_damage": 19, "attack_time_seconds": 0.55, "stamina_cost": 9,
                 "reach_meters": 2.1, "crit_chance": 0.1, "crit_mult": 1.9, "on_hit_status": "burn", "status_chance": 0.35, "status_power": 6, "status_duration": 4.0}),
    item("ink_heart_quill", "Ink-Heart Quill", "A quill whose nib dips itself in the Archivist's ink heart. Spells written with it cost less and stick harder.", "accessory", "ink_heart_quill", "seal_quill", 300, 0.1, slots=["accessory"],
         effects=[{"type": "bonus", "stat": "spell_cost_reduction", "value": 0.15}, {"type": "bonus", "stat": "status_chance_bonus", "value": 0.1},
                  {"type": "bonus", "stat": "spell_power_bonus", "value": 0.1}]),
    item("fang_unwritten", "Fang of the Unwritten", "The Name-Eater's tooth on a cord. It takes a little of every enemy you hit and gives it to you. It would like your name too. It can't have it.", "accessory", "fang_unwritten", "signet_ring", 360, 0.1, slots=["accessory"],
         effects=[{"type": "bonus", "stat": "life_steal", "value": 0.06}, {"type": "bonus", "stat": "crit_damage_bonus", "value": 0.25}]),
    item("granny_mittens", "Grandmother's Fighting Mittens", "Knitted from bonnet thread, impossibly tough. Blocking in them is like being hugged by a very stern grandmother. You carry more, too: deep pockets.", "accessory", "granny_mittens", "leather_jerkin", 240, 0.3, slots=["accessory"],
         effects=[{"type": "bonus", "stat": "armor_bonus", "value": 3.0}, {"type": "bonus", "stat": "heal_on_block", "value": 6.0},
                  {"type": "bonus", "stat": "carry_capacity_bonus", "value": 15.0}]),
    item("ember_draught", "Ember Draught", "Bottled indignation. For five minutes your fire burns hotter and your spells hit harder. Tastes of smoke and grievance.", "consumable", "ember_draught", "potion_flask", 70, 0.3, stackable=True,
         effects=[{"type": "buff", "stat": "burn_damage_bonus", "value": 0.5, "duration": 300}, {"type": "buff", "stat": "spell_power_bonus", "value": 0.15, "duration": 300}]),
    item("lullaby_tonic", "Lullaby Tonic", "Brewed round the Warden's bell. Restores your nerve completely, then keeps it topped up for five minutes. You may hum.", "consumable", "lullaby_tonic", "potion_flask", 70, 0.3, stackable=True,
         effects=[{"type": "consumable_sanity", "amount": 100}, {"type": "consumable_heal", "amount": 30}, {"type": "buff", "stat": "sanity_regen", "value": 1.0, "duration": 300}]),
    item("oil_forgetting", "Oil of Forgetting", "Dreaming ink thinned with salt water. Enemies struck with an oiled weapon forget who they were fighting, and sometimes who they are.", "consumable", "oil_forgetting", "potion_flask", 60, 0.3, stackable=True,
         effects=[{"type": "weapon_oil", "stat": "confuse", "value": 0.3, "amount": 0, "duration": 120}]),
    item("dreaming_calamari", "Dreaming Calamari", "Mother Brine's speciality, made with ink from the Dreaming Limb. You dream a little while awake. Your spells feel lighter, and your curses last longer.", "consumable", "dreaming_calamari", "bread_loaf", 60, 0.4, stackable=True,
         effects=[{"type": "consumable_heal", "amount": 40}, {"type": "buff", "stat": "spell_cost_reduction", "value": 0.2, "duration": 300},
                  {"type": "buff", "stat": "status_duration_bonus", "value": 0.3, "duration": 300}]),
    item("fish_pie", "Saltmere Fish Pie", "Perch, bread and sage under a lid of pastry. Heals well and keeps healing, slowly, for five minutes. Mother Brine says you have to eat the crust.", "consumable", "fish_pie", "bread_loaf", 30, 0.5, stackable=True,
         effects=[{"type": "consumable_heal", "amount": 35}, {"type": "buff", "stat": "health_regen", "value": 1.5, "duration": 300}]),
]
# ------------------------------------------------------------------ recipe books
R = lambda n: f"core:recipe.{n}"
BOOKS = [
    ("book_monster_bits", "Hollis's Field Notes: Useful Bits of Monsters", "tome_paper",
     "A hunter's notebook, stained with things you'd rather not identify. Teaches workbench recipes for boss parts.",
     "HOLLIS'S FIELD NOTES\nUseful Bits of Monsters (and What to Hit Them With)\n\nRat King: the whiskers. Bind one to a hilt and it bleeds whatever it touches. Burn the rest of the rat. Burn it twice.\n\nThe Wrathful Host: if you put him to rest the hard way, he leaves embers. Quench a blade in one. It holds a grudge, which is useful in a sword.\n\nThe Archivist: the ink heart. Don't eat it. Put it in a quill.\n\nThe Name-Eater: a tooth. Wear it. It drinks from them and not from you. Probably.\n\nThe wolf in the nightgown: the bonnet thread. Make mittens. I'm serious. Best block of my life.\n\n- H.",
     ["whiskerblade", "hostbrand", "ink_heart_quill", "fang_unwritten", "granny_mittens"], "core:npc.merchant_vaelen", 150),
    ("book_forbidden_footnotes", "Sabrino's Forbidden Footnotes", "tome_sabrino",
     "The footnotes Sabrino tore out of a respectable alchemy textbook, because the footnotes were the good part. Teaches alchemy with boss reagents.",
     "FOOTNOTES (FORBIDDEN)\n\n1. The ember of an angry ghost, two marigolds and a splash of resin: drink it and your fire forgets how to stop. Delicious. Don't breathe on anyone.\n\n2. A lullaby bell, grave moss, sea salt. You will feel like a child who has been tucked in by someone who loves you. Weep if you need to.\n\n3. Dreaming ink and sea water on a blade: they forget who they are fighting. Very rude. Very effective.\n\n- S. (The Italian Witch. Wanted. Correct.)",
     ["ember_draught", "lullaby_tonic", "oil_forgetting"], "core:npc.witch_sabrino", 180),
    ("book_brine_card", "Mother Brine's Greasy Recipe Card", "tome_late",
     "A recipe card so greasy it's translucent. Teaches two of Mother Brine's specials.",
     "MOTHER BRINE'S SPECIALS (do not show the Harbourmaster)\n\nDREAMING CALAMARI: one sac of ink from the big arm in the reef (you know the one). One cod. Salt. Fry until it stops looking at you.\n\nSALTMERE FISH PIE: two perch, a loaf, a sprig of sage. Lid on. Eat the crust. EAT THE CRUST.\n\nDon't ask what's in the chowder.",
     ["dreaming_calamari", "fish_pie"], "core:npc.mother_brine", 40),
]
BOOK_ITEMS = []
for bid, name, icon, desc, text, recipes, vendor, price in BOOKS:
    d = item(bid, name, desc, "book", icon, "spell_tome", price, 0.6, book_text_key=f"book.{bid}.text",
             effects=[{"type": "learn_recipe", "recipe_id": R(r)} for r in recipes])
    S[f"book.{bid}.text"] = text
    BOOK_ITEMS.append(d)
book_of = {r: I(b[0]) for b in BOOKS for r in b[5]}

A = load("content/items/armor_and_gear.json"); W = load("content/items/weapons.json"); CB = load("content/items/consumables_and_books.json")
for d in REAGENTS + BOOK_ITEMS: CB["items"].append(d)
for d in RESULTS:
    (W if d["category"] == "weapon" else A if d["category"] == "accessory" else CB)["items"].append(d)
save("content/items/armor_and_gear.json", A); save("content/items/weapons.json", W); save("content/items/consumables_and_books.json", CB)

RC = load("content/recipes/recipes.json")
def recipe(n, station, ings, skill, lvl, qty=1):
    RC["recipes"].append({"id": R(n), "station": station, "result": I(n), "qty": qty,
                          "ingredients": [{"item": I(i), "qty": q} for i, q in ings], "skill": skill, "skill_level": lvl, "book": book_of[n]})
recipe("whiskerblade", "workbench", [("rat_whisker", 1), ("iron_scrap", 3), ("ashwood_branch", 1)], "daggers", 8)
recipe("hostbrand", "workbench", [("host_ember", 1), ("iron_scrap", 4), ("ashwood_branch", 1)], "swords", 10)
recipe("ink_heart_quill", "workbench", [("ink_heart", 1), ("ashwood_branch", 1), ("glowcap", 2)], "lore", 10)
recipe("fang_unwritten", "workbench", [("name_eater_tooth", 1), ("glimmering_pearl", 1), ("iron_scrap", 1)], "lore", 12)
recipe("granny_mittens", "workbench", [("bonnet_thread", 1), ("wolfsbane", 2), ("pine_resin", 1)], "block", 6)
recipe("ember_draught", "alchemy", [("host_ember", 1), ("marigold", 2), ("pine_resin", 1)], "elemental", 8, 2)
recipe("lullaby_tonic", "alchemy", [("warden_bell", 1), ("grave_moss", 1), ("sea_salt", 1)], "restoration", 8, 2)
recipe("oil_forgetting", "alchemy", [("dreaming_ink", 1), ("sea_salt", 1)], "illusion", 8, 2)
recipe("dreaming_calamari", "cooking", [("dreaming_ink", 1), ("fish_cod", 1), ("sea_salt", 1)], "restoration", 0)
recipe("fish_pie", "cooking", [("fish_perch", 2), ("bread_loaf", 1), ("wayside_sage", 1)], "restoration", 0)
save("content/recipes/recipes.json", RC)

# ------------------------------------------------------------------ boss drops
L = load("content/loot_tables/core_loot.json")
T = {t["id"]: t for t in L["loot_tables"]}
def clone(src, new, guaranteed):
    t = json.loads(json.dumps(T[src])); t["id"] = new; t["guaranteed"] = guaranteed
    L["loot_tables"].append(t); T[new] = t
T["core:loot.rat_king"]["guaranteed"].append(I("rat_whisker"))
T["core:loot.crypt_boss"]["guaranteed"].append(I("ink_heart"))
T["core:loot.vault_warden"]["guaranteed"].append(I("warden_bell"))
T["core:loot.avatar"]["guaranteed"].append(I("name_eater_tooth"))
clone("core:loot.crypt_boss", "core:loot.wrathful_host", [I("host_ember"), I("host_ember"), I("health_potion")])
clone("core:loot.avatar", "core:loot.dreaming_limb", [I("dreaming_ink"), I("dreaming_ink")])
clone("core:loot.wolf", "core:loot.granny_wolf", [I("bonnet_thread")])
save("content/loot_tables/core_loot.json", L)
C = load("content/creatures/core_creatures.json")
for c in C["creatures"]:
    if c["id"] == "core:enemy.wrathful_host": c["loot_table"] = "core:loot.wrathful_host"
    if c["id"] == "core:enemy.dreaming_limb": c["loot_table"] = "core:loot.dreaming_limb"
    if c["id"] == "core:enemy.granny_wolf": c["loot_table"] = "core:loot.granny_wolf"
save("content/creatures/core_creatures.json", C)

# ------------------------------------------------------------------ vendors sell the books
N = load("content/npcs/core_npcs.json")
for bid, name, icon, desc, text, recipes, vendor, price in BOOKS:
    for n in N["npcs"]:
        if n["id"] == vendor:
            n.setdefault("vendor_inventory", []).append({"item_id": I(bid), "stock": 1, "price": price})
save("content/npcs/core_npcs.json", N)

S["tip.41"] = "Every boss leaves something behind worth crafting with. Hollis's Field Notes, Sabrino's Footnotes and Mother Brine's recipe card tell you what."
S["tip.42"] = "Can't see a recipe? Greyed-out entries at the crafting bench come from recipe books you haven't read yet."
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

"""Roguelike-inspired spells, wands and weapons (in the spirit of games like Barony; names, text and code are our own).

Statuses bleed / confuse / charm, spell primitives knock / buff_stat, and wands (stackable consumables whose stack
size is the charge count; effect type cast_spell).

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
SP = load("content/spells/core_spells.json")
NEW = [
    ("bewilder", "Bewilder", "illusion", 13, 1.0, {"primitive": "projectile_damage", "damage_type": "ink", "base_power": 6, "projectile_speed": 17.0,
        "projectile_sprite": "assets/sprites/vfx/spell_arcane.png", "status": "confuse", "status_duration": 7.0,
        "light_color": [0.85, 0.55, 1.0], "light_radius": 4.0},
     "The target forgets which way is up, who it was fighting, and what a 'you' is. It wanders about and swings at whatever's nearest, friend or foe."),
    ("sudden_friendship", "Sudden Friendship", "illusion", 24, 2.5, {"primitive": "projectile_damage", "damage_type": "ink", "base_power": 1,
        "projectile_speed": 15.0, "projectile_sprite": "assets/sprites/vfx/spell_arcane.png", "status": "charm", "status_duration": 14.0,
        "light_color": [1.0, 0.6, 0.85], "light_radius": 4.5},
     "For fourteen seconds, the target thinks you are the best person it has ever met, and fights anything that disagrees. Hitting your new friend ends the friendship. Bosses have trust issues."),
    ("unauthorised_entry", "Unauthorised Entry", "illusion", 9, 1.0, {"primitive": "knock", "base_power": 11, "light_color": [0.8, 0.7, 1.0], "light_radius": 4.0},
     "The lock you are looking at is persuaded that it was never locked in the first place. Works on locks up to a difficulty that grows with your Illusion. Leaves no lockpicks broken and no paperwork filed."),
    ("borrowed_vitality", "Borrowed Vitality", "restoration", 20, 2.0, {"primitive": "buff_stat", "bonus_key": "life_steal", "bonus_value": 0.18,
        "duration_seconds": 25.0, "light_color": [0.8, 0.2, 0.3], "light_radius": 3.0},
     "For twenty-five seconds, every blow you land gives a little of their life to you. Lord Ashgrave says it's 'not like that'. It's exactly like that."),
    ("late_for_appointment", "Late for an Appointment", "illusion", 12, 1.5, {"primitive": "buff_stat", "bonus_key": "move_speed_bonus", "bonus_value": 0.35,
        "duration_seconds": 18.0, "light_color": [0.6, 0.9, 1.0], "light_radius": 3.0},
     "The universal panic of being late, bottled. You move 35% faster for eighteen seconds. Your heart rate does too."),
    ("paper_storm", "Paper Storm", "illusion", 18, 1.8, {"primitive": "nova", "damage_type": "slashing", "base_power": 9, "radius": 4.0,
        "status": "bleed", "status_power": 3, "status_duration": 5.0, "light_color": [0.95, 0.92, 0.85], "light_radius": 5.0},
     "A whirlwind of razor-edged Bureau forms bursts out around you. Everything nearby takes a thousand paper cuts and bleeds. Bleeding stacks up to three times."),
]
for sid, name, skill, cost, cd, eff, desc in NEW:
    SP["spells"].append({"id": f"core:spell.{sid}", "name_key": f"spell.{sid}.name", "description_key": f"spell.{sid}.desc",
                         "icon": f"assets/ui/spells/{sid}.png", "skill": skill, "mana_cost": cost, "cooldown_seconds": cd,
                         "cast_sfx": "assets/audio/sfx/spell_cast.wav", "effect": eff})
    S[f"spell.{sid}.name"] = name
    S[f"spell.{sid}.desc"] = desc
save("content/spells/core_spells.json", SP)

# ---------------------------------------------------------------- tomes for the new spells
CI = load("content/items/consumables_and_books.json")
TOMES = [("tome_bewilder", "bewilder", "Bewilder: A Primer in Confusion",
          "Chapter One: Where Am I?\nChapter Two: Who Are You?\nChapter Three: Why Is That Wolf Hitting The Other Wolf?\n\nThe author's note: \"I wrote this book in a single sitting and have no memory of doing so.\""),
         ("tome_friendship", "sudden_friendship", "Sudden Friendship (Abridged)",
          "\"Every monster is merely a friend you have not yet hexed.\"\n\nThe illustrations show a smiling wizard, a grinning troll, and the troll later eating a different troll. The caption reads: TEAMWORK."),
         ("tome_entry", "unauthorised_entry", "Unauthorised Entry: The Lawyer's Edition",
          "Section 1. A lock is a contract between a door and a frame.\nSection 2. Contracts can be voided.\nSection 3. Here's how.\n\nStamped on every page: NOT FOR USE ON BUREAU PREMISES. Someone has crossed out NOT."),
         ("tome_vitality", "borrowed_vitality", "Borrowed Vitality",
          "A slim, elegant volume bound in red velvet. The handwritten dedication reads: \"For when you need a little more life than you have. -A.\" It smells faintly of roses and something metallic."),
         ("tome_late", "late_for_appointment", "Late for an Appointment",
          "This book is very short because the author did not have time to finish it. The spell is on page one. Page two just says \"SORRY SORRY SORRY\"."),
         ("tome_paper", "paper_storm", "Paper Storm: A Bureau Self-Defence Manual",
          "\"Clerks are often told they are harmless. This manual exists to correct that impression.\"\n\nThe pages have unusually sharp edges. Handle with care.")]
for iid, spell, title, text in TOMES:
    CI["items"].append({"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": "book",
                        "icon": f"assets/ui/items/{iid}.png", "world_model": "assets/models/items/spell_tome.glb", "slots": [], "value": 70, "weight": 0.8,
                        "book_text_key": f"book.{iid}.text", "effects": [{"type": "learn_spell", "spell_id": f"core:spell.{spell}"}]})
    S[f"item.{iid}.name"] = "Tome: " + title
    S[f"item.{iid}.description"] = "Reading it teaches the spell (and the tome crumbles)."
    S[f"book.{iid}.text"] = text

# ---------------------------------------------------------------- wands
WANDS = [("wand_sparks", "chain_of_command", "Wand of Sparks", "A copper rod that buzzes in your hand. Each charge casts Chain of Command without mana."),
         ("wand_frost", "frost_lance", "Wand of Frost", "Rimed with ice at the tip. Each charge fires a Frost Lance."),
         ("wand_bewilder", "bewilder", "Wand of Bewilderment", "Twisted like a question mark. Each charge casts Bewilder."),
         ("wand_friendship", "sudden_friendship", "Wand of Sudden Friendship", "Pink, with a little bow on it. Deeply unsettling. Each charge casts Sudden Friendship."),
         ("wand_entry", "unauthorised_entry", "Wand of Unauthorised Entry", "Shaped like a key, if a key were also a crowbar. Each charge casts Unauthorised Entry.")]
for iid, spell, name, desc in WANDS:
    CI["items"].append({"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": "consumable",
                        "icon": f"assets/ui/items/{iid}.png", "world_model": "assets/models/items/oak_staff.glb", "slots": [], "stackable": True,
                        "value": 12, "weight": 0.05, "effects": [{"type": "cast_spell", "spell_id": f"core:spell.{spell}"}]})
    S[f"item.{iid}.name"] = name
    S[f"item.{iid}.description"] = desc + " The number on the stack is the charges left. Put it on a quick slot."
save("content/items/consumables_and_books.json", CI)

# ---------------------------------------------------------------- weapons
W = load("content/items/weapons.json")
W["items"] += [
    {"id": "core:item.serrated_cleaver", "name_key": "item.serrated_cleaver.name", "description_key": "item.serrated_cleaver.description", "category": "weapon",
     "icon": "assets/ui/items/serrated_cleaver.png", "world_model": "assets/models/items/rusted_sword.glb", "slots": ["main_hand"], "value": 110, "weight": 2.6,
     "weapon": {"kind": "melee", "skill": "swords", "damage_type": "slashing", "base_damage": 15, "attack_time_seconds": 0.55, "stamina_cost": 8,
                "reach_meters": 1.9, "on_hit_status": "bleed", "status_chance": 0.45, "status_power": 3, "status_duration": 4.0}},
    {"id": "core:item.thornbow", "name_key": "item.thornbow.name", "description_key": "item.thornbow.description", "category": "weapon",
     "icon": "assets/ui/items/thornbow.png", "world_model": "assets/models/items/hunting_bow.glb", "slots": ["main_hand"], "value": 140, "weight": 1.6,
     "weapon": {"kind": "ranged", "skill": "bows", "damage_type": "piercing", "base_damage": 16, "attack_time_seconds": 0.9, "stamina_cost": 6,
                "reach_meters": 2.0, "ammo_item": "core:item.wooden_arrow", "projectile_speed": 30.0, "crit_chance": 0.08,
                "on_hit_status": "bleed", "status_chance": 0.4, "status_power": 3, "status_duration": 5.0}},
    {"id": "core:item.inconvenient_sword", "name_key": "item.inconvenient_sword.name", "description_key": "item.inconvenient_sword.description",
     "category": "weapon", "icon": "assets/ui/items/inconvenient_sword.png", "world_model": "assets/models/items/iron_longsword.glb", "slots": ["main_hand"],
     "value": 95, "weight": 2.8,
     "weapon": {"kind": "melee", "skill": "swords", "damage_type": "slashing", "base_damage": 13, "attack_time_seconds": 0.55, "stamina_cost": 8,
                "reach_meters": 2.1, "on_hit_status": "confuse", "status_chance": 0.2, "status_duration": 4.0}},
]
save("content/items/weapons.json", W)
S.update({
    "item.serrated_cleaver.name": "Serrated Cleaver",
    "item.serrated_cleaver.description": "A butcher's cleaver with a saw-tooth back, 'confiscated' from the Hollowmere kitchens. Opens wounds that keep on giving. Bleeding stacks three times.",
    "item.thornbow.name": "Thornbow",
    "item.thornbow.description": "A bow grown, not carved, from a thornbush in the Whistling Wood. The arrows come out barbed. Things it hits bleed.",
    "item.inconvenient_sword.name": "The Sword of Mild Inconvenience",
    "item.inconvenient_sword.description": "Enchanted by a wizard with a grudge and a short attention span. Sometimes the person it hits forgets what they were doing. Sometimes so do you. (Only them, actually. Probably.)",
})

# ---------------------------------------------------------------- where they come from
N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.merchant_vaelen":
        n["vendor_inventory"] += [{"item_id": "core:item.wand_entry", "stock": 4, "price": 30}, {"item_id": "core:item.wand_sparks", "stock": 5, "price": 28},
                                  {"item_id": "core:item.tome_late", "stock": 1, "price": 80}, {"item_id": "core:item.tome_entry", "stock": 1, "price": 90},
                                  {"item_id": "core:item.serrated_cleaver", "stock": 1, "price": 110}, {"item_id": "core:item.thornbow", "stock": 1, "price": 140}]
save("content/npcs/core_npcs.json", N)
LT = load("content/loot_tables/core_loot.json")
adds = {
    "core:loot.crypt_basic": [("core:item.wand_frost", 6, 2, 4), ("core:item.wand_entry", 6, 2, 3)],
    "core:loot.crypt_elite": [("core:item.wand_sparks", 10, 3, 6), ("core:item.wand_bewilder", 8, 3, 5), ("core:item.tome_bewilder", 5, 1, 1),
                              ("core:item.tome_paper", 5, 1, 1)],
    "core:loot.crypt_boss": [("core:item.wand_friendship", 15, 3, 5), ("core:item.tome_friendship", 10, 1, 1), ("core:item.inconvenient_sword", 8, 1, 1)],
    "core:loot.drowned": [("core:item.wand_frost", 6, 2, 4)],
    "core:loot.avatar": [("core:item.tome_vitality", 20, 1, 1), ("core:item.wand_friendship", 15, 3, 6)],
    "core:loot.wolf": [("core:item.wand_bewilder", 4, 2, 3)],
}
for t in LT["loot_tables"]:
    for item, w, lo, hi in adds.get(t["id"], []):
        t["entries"].append({"item_id": item, "weight": w, "min_qty": lo, "max_qty": hi})
save("content/loot_tables/core_loot.json", LT)
# Ashgrave hands over Borrowed Vitality after the grimoire conversation (if you were honest about his poetry)
D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
node = DL["core:dialogue.vampire_ashgrave"]["nodes"].get("od_ash_true")
if node:
    node.setdefault("actions", []).append({"type": "give_item", "item_id": "core:item.tome_vitality", "qty": 1})
    S["dlg.overdue.ash.od_ash_true"] = ("Ashgrave stares at you. Nobody has ever said that to him before.\n\nASHGRAVE (very quietly): \"...Thank you.\" "
                                        "He hands you the book, and then, after a moment, a second, slimmer one bound in red velvet. \"This one is mine. "
                                        "Not the library's. It's... a little more personal. For when you need more life than you have.\"\n\n"
                                        "\"I'm going to write a poem about this. It will be very bad. I will mean every word.\"")
save("content/dialogue/chapter_zero_dialogue.json", D)
S["tip.32"] = "Wands are free spells. The number on the stack is how many charges are left. Wands go in quick slots too."
S["tip.33"] = "A confused wolf will happily bite another wolf. A charmed wolf will do it on purpose."

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

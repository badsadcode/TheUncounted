"""The Dragon's Pension, part two: The Missing Third. Quillsby fled to 'The Late Cindermaw', his seaside house bought with
a third of the hoard. Silas rows you there; kobold bookkeepers, the cornered Quillsby (he carries the vault key), and the
hoard in the vault. ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q, DP = "core:quest.missing_third", "core:quest.dragon_pension"
I = lambda n: f"core:item.{n}"
QE = lambda q, s: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda q, s: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda q, s: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
SF = lambda f, v=True: {"type": "set_flag", "flag": f, "value": v}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}

D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
def topics(did, prefix, speaker, items):
    dlg = DL[did]
    root = dlg["nodes"][dlg["root_node"]]
    end = next(i for i, c in enumerate(root["choices"]) if c["next"] == "END")
    for ctext, nid, cond, ntext, acts, back, back_next in items:
        S[f"{prefix}.choice_{nid}"] = ctext
        root["choices"].insert(end, {"text_key": f"{prefix}.choice_{nid}", "next": nid, "conditions": cond}); end += 1
        S[f"{prefix}.{nid}"] = ntext
        S[f"{prefix}.{nid}.c0"] = back
        n = {"speaker_key": speaker, "text_key": f"{prefix}.{nid}", "choices": [{"text_key": f"{prefix}.{nid}.c0", "next": back_next}]}
        if acts: n["actions"] = acts
        dlg["nodes"][nid] = n
topics("core:dialogue.dragon_cindermaw", "dlg.mt.dr", "npc.dragon_cindermaw.name", [
    ('"About the missing third of your hoard..."', "mt_start", [QA(DP, 100), QB(Q, 0)],
     "\"THE KOBOLD.\" The dragon's eyes narrow to slits. \"I HAVE READ HIS LEDGER. SHOES. CUSHIONS. A HOUSE BY THE SEA, NAMED AFTER MY "
     "FUNERAL.\"\n\nSmoke pours from its nostrils. Gerald the sheep moves, quietly, to a safer distance.\n\n\"I CANNOT GO. I AM TOO LARGE FOR "
     "COVES, AND IF I GO I WILL BURN THE HOUSE, AND THE GOLD WILL MELT, AND THEN WHERE ARE WE.\" A pause. \"THE FISHERMAN KNOWS THE COVE. "
     "GO WITH HIM. BRING BACK MY GOLD. BRING BACK THE KOBOLD, IF YOU LIKE. OR DON'T. I AM NOT FUSSY.\"",
     [SQ(0), SQ(10), SF("missing_third_open")], '"I\'ll get your gold back."', "root"),
    ('"I\'ve recovered the missing third of your hoard."', "mt_done", [QE(Q, 40), {"type": "has_item", "item_id": I("hoard_third")}],
     "You drag the sacks across the square. Coins spill out. The dragon looks at them for a long moment, then lowers its enormous head "
     "and breathes on them, very gently, until they glow. It purrs. Dragons purr. Nobody in Bellwether knew that.\n\n\"MY GOLD.\"\n\n"
     "\"A FINDER'S FEE. ONE TENTH. THAT IS THE OLD LAW.\" A heap of coins slides your way. \"AND THESE. THE KOBOLD WORE THEM TO 'GLOAT, "
     "FORMAL'. THEY BRING LUCK WITH MONEY. HE WILL NOT BE NEEDING LUCK WHERE HE IS GOING.\"\n\nTwo tiny gold cufflinks, shaped like dragons, "
     "land in your palm.",
     [{"type": "take_item", "item_id": I("hoard_third"), "qty": 1}, {"type": "give_gold", "amount": 400},
      {"type": "give_item", "item_id": I("quillsby_cufflinks"), "qty": 1}, SQ(100), {"type": "give_xp", "skill": "persuasion", "amount": 60}],
     '"Enjoy your gold, Cindermaw."', "root"),
])
topics("core:dialogue.silas_gale", "dlg.mt.silas", "npc.silas_gale.name", [
    ('"Do you know a cove with a house called The Late Cindermaw?"', "mt_row1", [QE(Q, 10), FN("at_seaside")],
     "Silas spits over the side of the pier. \"Know it? Watched it go up. Kobold paid in solid gold and wanted everything in red. Little cove "
     "past the headland, can't get there on foot.\" He unties the boat. \"Hop in. Mind the gold leaf on the jetty: it's slippy.\"\n\nHe rows "
     "you round the headland in silence, then, as the cove comes into view: \"Three hundred pairs of shoes, they say. For a lizard.\"",
     [SF("at_seaside"), SQ(20), {"type": "travel", "spawn": "seaside_landing"}], "Climb out onto the jetty.", "END"),
    ('"Row me to Quillsby\'s cove."', "mt_row", [QA(Q, 20), FN("at_seaside")],
     "\"Again? Fair enough.\" Silas rows you round the headland.", [SF("at_seaside"), {"type": "travel", "spawn": "seaside_landing"}], "Climb out.", "END"),
    ('"Take me back to Saltmere, Silas."', "mt_home", [FS("at_seaside")],
     "Silas rows you home past the headland, humming the shanty about the woman who married a whale.",
     [SF("at_seaside", False), {"type": "travel", "spawn": "saltmere_pier"}], "Climb out at the pier.", "END"),
])
save("content/dialogue/chapter_zero_dialogue.json", D)

CR = load("content/creatures/core_creatures.json")
def creature(cid, name, sheet, scale, hp, armor, dmg, xp, loot, alert, death, speed=2.8):
    CR["creatures"].append({"id": f"core:enemy.{cid}", "name_key": f"enemy.{cid}.name",
        "appearance": {"type": "sprite_8dir", "sprite_sheet": sheet, "animation_data": "assets/animations/npc_standard.json", "scale": scale},
        "stats": {"health": hp, "armor": armor, "move_speed": speed, "xp_reward": xp}, "behavior": "melee_patroller", "family": "beast",
        "perception": {"sight_meters": 12.0, "hearing_meters": 9.0},
        "attack": {"name": "ledger_swipe", "damage": dmg, "reach_meters": 1.5, "windup_seconds": 0.5, "cooldown_seconds": 1.2}, "loot_table": loot,
        "audio": {"alert": "assets/audio/sfx/rat_squeak.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav",
                  "death": "assets/audio/sfx/enemy_death.wav"},
        "hit_fx": {"color": [140, 200, 110], "glow": False}, "lines": {"alert": f"line.{cid}.alert", "death": f"line.{cid}.death"}})
    S[f"enemy.{cid}.name"] = name; S[f"line.{cid}.alert"] = alert; S[f"line.{cid}.death"] = death
creature("kobold_bookkeeper", "Kobold Bookkeeper", "assets/sprites/enemies/kobold_bookkeeper.png", 1.25, 60, 1, 8, 25, "core:loot.kobold_bookkeeper",
         "Trespasser! This is a PRIVATE residence! I'll have you audited!", "My... receipts...")
creature("quillsby_cornered", "Grubnik Quillsby, Esq. (Cornered)", "assets/sprites/npcs/kobold_quillsby.png", 1.3, 190, 3, 12, 110, "core:loot.quillsby",
         "YOU! The dragon's errand-runner! You'll never take my SHOES!", "Not... the shoes... anything but... the shoes...", speed=3.2)
save("content/creatures/core_creatures.json", CR)
import os
ok = os.path.exists("assets/audio/sfx/rat_squeak.wav")
if not ok:
    CR = load("content/creatures/core_creatures.json")
    for c in CR["creatures"]:
        if c["id"] in ("core:enemy.kobold_bookkeeper", "core:enemy.quillsby_cornered"): c["audio"]["alert"] = "assets/audio/sfx/sword_swing.wav"
    save("content/creatures/core_creatures.json", CR)
L = load("content/loot_tables/core_loot.json")
L["loot_tables"] += [
    {"id": "core:loot.kobold_bookkeeper", "gold_min": 8, "gold_max": 20, "entries": [{"item_id": I("health_potion"), "weight": 30, "min_qty": 1, "max_qty": 1},
                                                                                     {"item_id": I("bread_loaf"), "weight": 30, "min_qty": 1, "max_qty": 1}]},
    {"id": "core:loot.quillsby", "gold_min": 40, "gold_max": 60, "guaranteed": [I("quillsby_vault_key")],
     "entries": [{"item_id": I("health_potion"), "weight": 100, "min_qty": 1, "max_qty": 2}]}]
save("content/loot_tables/core_loot.json", L)

CB = load("content/items/consumables_and_books.json"); A = load("content/items/armor_and_gear.json")
def item(n, name, desc, cat, icon, model, value, **kw):
    d = {"id": I(n), "name_key": f"item.{n}.name", "description_key": f"item.{n}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": f"assets/models/{model}.glb", "slots": kw.pop("slots", []), "value": value, "weight": kw.pop("weight", 0.2)}
    d.update(kw)
    S[f"item.{n}.name"] = name; S[f"item.{n}.description"] = desc
    return d
CB["items"].append(item("quillsby_vault_key", "Quillsby's Vault Key", "A tiny gold key on a velvet ribbon, engraved 'MINE'.", "key", "quillsby_vault_key", "items/annex_key", 0))
CB["items"].append(item("hoard_third", "The Missing Third", "Four thousand gold in heavy sacks stamped 'INVESTMENTS'. It belongs to a dragon. Take it back to Bellwether.", "misc", "hoard_third", "props/treasure_chest", 0, weight=8.0))
A["items"].append(item("quillsby_cufflinks", "Quillsby's Gloating Cufflinks", "Two tiny gold cufflinks shaped like dragons, worn to 'gloat, formal'. Lucky with money: +25% gold found, 10% off at every shop.",
                       "accessory", "quillsby_cufflinks", "items/signet_ring", 200, slots=["accessory"],
                       effects=[{"type": "bonus", "stat": "gold_find_bonus", "value": 0.25}, {"type": "bonus", "stat": "shop_discount", "value": 0.1}]))
save("content/items/consumables_and_books.json", CB); save("content/items/armor_and_gear.json", A)

QQ = load("content/quests/chapter_zero_quests.json")
QQ["quests"].append({"id": Q, "title_key": "quest.mt.title", "summary_key": "quest.mt.summary", "campaign": "dragon_pension", "stages": [
    {"stage": 0, "objective_key": "quest.mt.stage0", "journal_key": "quest.mt.journal0", "markers": ["npc_dragon_cindermaw"]},
    {"stage": 10, "objective_key": "quest.mt.stage10", "journal_key": "quest.mt.journal10", "markers": ["npc_silas"]},
    {"stage": 20, "objective_key": "quest.mt.stage20", "journal_key": "quest.mt.journal20", "markers": ["quillsby_cornered"]},
    {"stage": 30, "objective_key": "quest.mt.stage30", "journal_key": "quest.mt.journal30", "markers": ["missing_third_hoard"]},
    {"stage": 40, "objective_key": "quest.mt.stage40", "journal_key": "quest.mt.journal40", "markers": ["npc_dragon_cindermaw"]},
    {"stage": 100, "objective_key": "quest.mt.stage100", "journal_key": "quest.mt.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "map.seaside_house.name": "The Late Cindermaw",
    "quest.mt.title": "The Missing Third", "quest.mt.summary": "Quillsby spent a third of a dragon's hoard on a seaside house. The dragon would like it back.",
    "quest.mt.stage0": "Ask Cindermaw about the missing third of the hoard.", "quest.mt.journal0": "Cindermaw has read Quillsby's second ledger.",
    "quest.mt.stage10": "Ask Old Silas (Saltmere's north pier) to row you to Quillsby's cove.",
    "quest.mt.journal10": "Quillsby fled to 'The Late Cindermaw', a house in a cove you can only reach by boat.",
    "quest.mt.stage20": "Get into Quillsby's house and deal with Quillsby. He carries the vault key.",
    "quest.mt.journal20": "A sandy cove, a red-brick house, a sign saying NO DRAGONS. Somebody's painted 'VERY MUCH ALIVE' on it.",
    "quest.mt.stage30": "Open the vault and recover the missing third of the hoard.",
    "quest.mt.journal30": "Quillsby is down. 'Not the shoes...' He had a tiny gold key engraved 'MINE'.",
    "quest.mt.stage40": "Take the missing third back to Cindermaw in Bellwether (Silas will row you home).",
    "quest.mt.journal40": "Four thousand gold in sacks stamped INVESTMENTS.",
    "quest.mt.stage100": "Completed: the hoard is whole again.", "quest.mt.journal100": "Cindermaw purred. Nobody knew dragons purred. I got a finder's fee and his gloating cufflinks.",
    "story.missing_third.vault": "The vault door swings open on a little room lined in red velvet. In the middle, on a pedestal, under a glass dome, sits a single golden shoe.\n\nBehind it, stacked to the ceiling, are sacks. Dozens of them. Each one is stamped INVESTMENTS. You open one. Gold. All of them: gold.\n\nThere's a small framed note on the wall: 'In the event of my untimely arrest, this is all still MINE. - G.Q.'\n\nYou take the gold. You leave the note. You think about it, and you take the shoe too. It's a very nice shoe.",
    "tip.47": "Silas's boat goes more places than the reef. Ask him about coves.",
})
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

"""The Figure It Out Gang, Episode 3: The Headless Knight of the Old Road (Rodrick teased it after episode 2;
Agnes said it was a hat on a stick; Agnes was right). It's Steve. Steve is thrilled to be a real villain with a reveal.
Snacks is brave, once.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
F2, F3 = "core:quest.figure_ep2", "core:quest.figure_ep3"
QE = lambda q, s: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda q, s: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda q, s: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FL = lambda v: {"type": "flags_at_least", "flags": ["fig3_c1", "fig3_c2", "fig3_c3"], "value": v}
FF = lambda v: {"type": "flags_fewer_than", "flags": ["fig3_c1", "fig3_c2", "fig3_c3"], "value": v}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
SQ = lambda q, s: {"type": "set_quest_stage", "quest_id": q, "stage": s}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
ROD = "npc.figure_rodrick.name"

D = load("content/dialogue/chapter_zero_dialogue.json")
dl = {d["id"]: d for d in D["dialogues"]}

def node(dlg, prefix, nid, text, choices, actions=None, speaker=ROD):
    key = f"{prefix}.{nid}"
    S[key] = text
    n = {"speaker_key": speaker, "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, c in enumerate(choices):
        ck = f"{key}.c{i}"
        S[ck] = c[0]
        d = {"text_key": ck, "next": c[1]}
        if len(c) > 2 and c[2]: d["conditions"] = c[2]
        if len(c) > 3 and c[3]: d["actions"] = c[3]
        n["choices"].append(d)
    dlg["nodes"][nid] = n

# ---------------------------------------------------------------- Rodrick: episode three
rod = dl["core:dialogue.figure_rodrick"]
P = "dlg.fig.rod"
rc = rod["nodes"]["root"]["choices"]
later = next(i for i, c in enumerate(rc) if c["next"] == "later")
rc[later]["conditions"] = [QA(F3, 100)]
new = []
for text, nxt, cond in [
        ('"Any news about that headless knight?"', "e3_open", [QA(F2, 100), QB(F3, 0)]),
        ('"I\'ve got the clues about the Headless Knight."', "e3_trap", [QE(F3, 10), FL(3)]),
        ('"Where were the knight clues again?"', "e3_hint", [QE(F3, 10), FF(3)]),
        ('"The Headless Knight is unmasked. Unhelmeted. Whatever."', "e3_done", [QE(F3, 50)])]:
    k = f"{P}.root.e3_{nxt}"
    S[k] = text
    new.append({"text_key": k, "next": nxt, "conditions": cond})
rc[later:later] = new
node(rod, P, "e3_open",
     "Rodrick unrolls a third poster. This one he has clearly painted himself: 'THE HEADLESS KNIGHT OF THE OLD ROAD'.\n\n"
     "RODRICK: \"Every night, a knight in full armour, with NO HEAD, stands in the middle of the Old Road and demands a toll from "
     "travellers! Five gold! Or, according to one witness, 'four, or three, three is fine'.\"\n\n"
     "AGNES (not looking up from her book): \"It's a hat on a stick.\"\n\n"
     "PRIMROSE: \"It could be a very short knight, darling.\"\n\n"
     "BAGGY: \"It could be a knight who lost his head. Emotionally. It happens.\"\n\n"
     "RODRICK: \"It could be ANYTHING! Gang! Let's split up and look for clues! On the road! It's right there! We can see it from here!\"",
     [('"Splitting up. Ten feet apart."', "root", None, [SQ(F3, 0), SQ(F3, 10), SF("fig3_open")])])
node(rod, P, "e3_hint",
     "RODRICK: \"Up and down the Old Road! The ditches, the verges, the bushes! A knight with no head leaves clues! Possibly his head!\"",
     [('"Back to the road."', "root")])
node(rod, P, "e3_trap",
     "You lay out the clues: a hat nailed to a stick, a hand-painted toll sign with a spelling mistake, and a receipt from Vaelen for "
     "one suit of armour, slightly haunted, sold to 'S.'.\n\n"
     "AGNES: \"A hat. On a stick. I'd like that noted.\"\n\nRODRICK: \"Noted! Now: the TRAP. A giant cake in the middle of the road. A "
     "net in the tree above. The knight comes for the cake, the net comes for the knight. Foolproof.\"\n\n"
     "PRIMROSE: \"Why would a knight want cake?\"\n\nRODRICK: \"Everyone wants cake, Primrose.\"\n\n"
     "SNACKS (staring at the cake with its entire soul): \"Hrrrrrrrrrr.\"",
     [('"I\'ll set it up on the road."', "root", None, [SQ(F3, 20), SF("fig3_trap_ready")])])
node(rod, P, "e3_done",
     "RODRICK: \"Another mystery...\"\n\nTHE GANG: \"FIGURED OUT!\"\n\nSNACKS (loudly, first, for once): \"HRRROOT!\"\n\n"
     "Everyone turns to look at Snacks. Snacks puffs its feathers out, enormous with pride.\n\n"
     "AGNES: \"For the record: the trap caught the cake, Rodrick and a passing goose. The knight was stopped by SNACKS. Snacks charged "
     "a man in full armour. Snacks has never charged anything except a cake.\"\n\n"
     "RODRICK (wiping away a single manly tear): \"I've never been prouder of anyone. Snacks wants you to have something.\"\n\n"
     "Snacks waddles over and solemnly presents you with a single brown feather. Then it hides behind you again.",
     [('"Thank you, Snacks."', "root", None, [SQ(F3, 100), GI("core:item.snacks_feather"), GI("core:item.crumb_cake", 3),
                                              {"type": "give_gold", "amount": 100}, {"type": "give_xp", "skill": "perception", "amount": 50}])])

# ---------------------------------------------------------------- Snacks: a new memory
sn = dl["core:dialogue.figure_snacks"]
c = sn["nodes"]["root"]["choices"]
end = next(i for i, ch in enumerate(c) if ch["next"] == "END")
S["dlg.fig.sna.root.c_hero"] = '"You were so brave, Snacks."'
c.insert(end, {"text_key": "dlg.fig.sna.root.c_hero", "next": "hero", "conditions": [{"type": "flag_set", "flag": "fig3_done"}]})
node(sn, "dlg.fig.sna", "hero",
     "Snacks sits up very straight, puffs out its chest feathers to roughly twice their size, and hoots, once, nobly.\n\nThen a leaf "
     "blows past, and Snacks hides behind you.\n\nStill counts.", [("Still counts.", "root")], [{"type": "sanity", "amount": 5}],
     speaker="npc.figure_snacks.name")

# ---------------------------------------------------------------- the unmasking
D["dialogues"].append({"id": "core:dialogue.unmask_knight", "root_node": "root", "nodes": {}})
uk = D["dialogues"][-1]
U = "dlg.fig.unmask3"
node(uk, U, "root",
     "The Headless Knight lies on its back in the middle of the Old Road, flattened by one triumphant owlbear cub, which is sitting on its "
     "breastplate and refusing to move. Cake everywhere. A goose in the net.\n\n"
     "From inside the armour, a muffled voice: \"...Can somebody get the bird off me?\"\n\n"
     "RODRICK: \"Not until we see who you REALLY are!\"",
     [('"It\'s Steve. The bandit from the Whistling Wood."', "reveal", [FL(3)], [SF("fig3_guessed")]),
      ('"It\'s... Trout? Hollis\'s horse?"', "wrong_trout"),
      ("Just lift the helmet off.", "reveal")], speaker="npc.unmask_knight.name")
node(uk, U, "wrong_trout",
     "AGNES: \"Trout is a horse. Horses do not wear armour.\" A pause. \"Trout was on the inn roof at the time, anyway. I checked.\"\n\n"
     "BAGGY (nodding wisely): \"Good alibi, Trout.\"", [("Lift the helmet off.", "reveal")], speaker="npc.unmask_knight.name")
node(uk, U, "reveal",
     "Rodrick lifts off the empty helmet. Inside the collar of the armour, where the knight's neck should be, is a head, very much "
     "attached, wearing a too-big hood: a young man, red-faced and grinning.\n\nIt's Steve.\n\nTHE GANG: \"STEVE?!\"\n\n"
     "BAGGY: \"I barely knew her!\"\n\nSTEVE: \"We've MET, Baggy. Twice.\"\n\nBAGGY: \"Still barely.\"\n\n"
     "STEVE (puffing up, as much as a man can puff up while an owlbear sits on him): \"Yes! Me! Steve! Bandit! I bought the armour off "
     "Vaelen, cut a hole in the top, and stuck my hat on a stick! Nobody pays a toll to a bandit, but EVERYBODY pays a toll to a "
     "headless knight!\"\n\n\"And I would have got away with it, too, if it weren't for you nosy busybodies and your... surprisingly "
     "heavy owlbear.\"",
     [('"Steve. Why are you smiling?"', "smile")], [SF("fig3_unmasked")], speaker="npc.unmask_knight.name")
node(uk, U, "smile",
     "STEVE (eyes shining): \"Because I've always wanted to say that. 'I would have got away with it.' You don't get to say that "
     "as a level-one bandit. You get to say it as a VILLAIN. A real villain, with a reveal and a poster and everything.\" He sniffs. "
     "\"Can I keep the poster?\"\n\nRodrick, deeply moved, gives him the poster.\n\nSnacks, sensing the moment, finally gets off.\n\n"
     "STEVE: \"I'll give the tolls back. All eleven gold of it.\"",
     [("Head back to the wagon.", "END")], [SQ(F3, 50), SF("fig3_done")], speaker="npc.unmask_knight.name")
save("content/dialogue/chapter_zero_dialogue.json", D)

# ---------------------------------------------------------------- NPC, creature, item, quest
N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.unmask_knight", "name_key": "npc.unmask_knight.name", "title_key": "npc.unmask_knight.title",
                  "faction": "core:faction.ashbound", "dialogue_id": "core:dialogue.unmask_knight",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/steve_painted.png",
                                 "animation_data": "assets/animations/npc_standard_128.json", "scale": 1.62}, "barks": []})
for n in N["npcs"]:
    if n["id"] == "core:npc.steve":
        n.setdefault("barks", []).append({"text_key": "bark.steve.villain", "flag": "fig3_done"})
    if n["id"] == "core:npc.figure_snacks":
        n["barks"].append({"text_key": "bark.fig.sna.hero", "flag": "fig3_done"})
save("content/npcs/core_npcs.json", N)
CR = load("content/creatures/core_creatures.json")
CR["creatures"].append({"id": "core:enemy.headless_knight", "name_key": "enemy.headless_knight.name",
    "appearance": {"type": "model_glb", "model": "assets/models/characters/lost_sentinel.glb", "scale": 0.85},
    "stats": {"health": 85, "armor": 4, "move_speed": 1.8, "xp_reward": 40}, "behavior": "melee_patroller", "family": "construct",
    "perception": {"sight_meters": 12.0, "hearing_meters": 8.0},
    "attack": {"name": "toll_demand", "damage": 8, "reach_meters": 2.0, "windup_seconds": 0.7, "cooldown_seconds": 1.6, "sanity_damage": 2},
    "loot_table": "core:loot.vermin_drop",
    "audio": {"alert": "assets/audio/sfx/sentinel_clang.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav",
              "death": "assets/audio/sfx/enemy_death.wav"},
    "hit_fx": {"color": [200, 200, 210], "glow": False}, "lines": {"alert": "line.headless_knight.alert", "death": "line.headless_knight.death"}})
save("content/creatures/core_creatures.json", CR)
A = load("content/items/armor_and_gear.json")
A["items"].append({"id": "core:item.snacks_feather", "name_key": "item.snacks_feather.name", "description_key": "item.snacks_feather.description",
                   "category": "accessory", "icon": "assets/ui/items/snacks_feather.png", "world_model": "assets/models/items/seal_quill.glb",
                   "slots": ["accessory"], "value": 200, "weight": 0.0, "armor": 0,
                   "effects": [{"type": "bonus", "stat": "armor_bonus", "value": 2.0}, {"type": "bonus", "stat": "heal_on_block", "value": 3.0},
                               {"type": "bonus", "stat": "sanity_regen", "value": 0.5}, {"type": "bonus", "stat": "crit_damage_bonus", "value": 0.15}]})
save("content/items/armor_and_gear.json", A)
QQ = load("content/quests/chapter_zero_quests.json")
QQ["quests"].append({"id": F3, "title_key": "quest.fig3.title", "summary_key": "quest.fig3.summary", "campaign": "figure_it_out", "stages": [
    {"stage": 0, "objective_key": "quest.fig3.stage0", "journal_key": "quest.fig3.journal0", "markers": ["npc_figure_rodrick"]},
    {"stage": 10, "objective_key": "quest.fig3.stage10", "journal_key": "quest.fig3.journal10", "markers": ["fig3_clue_hat", "fig3_clue_sign", "fig3_clue_receipt", "npc_figure_rodrick"]},
    {"stage": 20, "objective_key": "quest.fig3.stage20", "journal_key": "quest.fig3.journal20", "markers": ["fig3_trap"]},
    {"stage": 30, "objective_key": "quest.fig3.stage30", "journal_key": "quest.fig3.journal30", "markers": ["fig3_knight"]},
    {"stage": 40, "objective_key": "quest.fig3.stage40", "journal_key": "quest.fig3.journal40", "markers": ["npc_unmask_knight"]},
    {"stage": 50, "objective_key": "quest.fig3.stage50", "journal_key": "quest.fig3.journal50", "markers": ["npc_figure_rodrick"]},
    {"stage": 100, "objective_key": "quest.fig3.stage100", "journal_key": "quest.fig3.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)

# ---------------------------------------------------------------- placement on the Old Road
def readable(iid, x, z, prompt, title, text, flag):
    return {"instance_id": iid, "type": "readable", "model": "", "pos": [x, 0.0, z], "rot_y": 0.0, "prompt": prompt, "title": title,
            "text": text, "set_flag": flag, "requires_flag": "fig3_open"}
R = load("content/regions/old_road.json")
R["interactables"] += [
    readable("fig3_clue_hat", -9.0, 3.8, "Look in the Ditch", "A Hat on a Stick",
             "In the ditch beside the road: a broom handle with a battered felt hat nailed to the top. Seen from a distance, at night, through "
             "a visor, it would look exactly like a knight's plume.\n\nOr a hat on a stick. Which is what it is.\n\nAgnes is going to be "
             "unbearable about this.", "fig3_c1"),
    readable("fig3_clue_sign", 2.5, -3.6, "Read the Sign", "A Hand-Painted Sign",
             "A wooden board, propped against a rock, painted in big careful letters:\n\nTOLL ROAD\nPAY THE HEDLESS KNIGHT\n5 GOLD\n(OR 4)\n"
             "(THIS IS NOT A BANDIT THING)\n\nThe 'A' in HEADLESS has been added later, above, with a little arrow.", "fig3_c2"),
    readable("fig3_clue_receipt", 11.5, 3.6, "Pick Up the Paper", "A Receipt in the Verge",
             "VAELEN'S PROVISIONS & ODDITIES\n1 x suit of plate armour, used, slightly haunted (the haunting is free) ... 30 gold\n"
             "Customer is paying in instalments of 1 gold.\nCustomer has paid 1 gold.\nSold to: S.\n\nOn the back, in different handwriting: "
             "'cut hole in top for my head. hat on stick. DONT FORGET THE STICK'", "fig3_c3"),
    {"instance_id": "fig3_trap", "type": "readable", "model": "", "pos": [0.0, 0.0, 0.6], "rot_y": 0.0, "prompt": "Set Rodrick's Trap",
     "title": "The Trap", "text": "(The trap is set.)", "set_flag": "fig3_trap", "requires_flag": "fig3_trap_ready", "hidden_flag": "fig3_trap",
     "quest_id": F3, "set_stage": 30, "narration": ["story.fig3.trap"]},
]
R.setdefault("creatures", []).append({"instance_id": "fig3_knight", "creature_id": "core:enemy.headless_knight", "pos": [-5.0, 0.0, 0.0],
    "patrol_a": [-7.0, 0.0, 0.0], "patrol_b": [-3.0, 0.0, 0.0], "requires_flag": "fig3_trap", "group": "fig3", "group_quest_id": F3,
    "group_set_stage": 40, "group_set_flag": "fig3_caught"})
R["npcs"].append({"instance_id": "npc_unmask_knight", "npc_id": "core:npc.unmask_knight", "pos": [-1.5, 0.0, 1.2], "yaw": 90.0,
                  "requires_flag": "fig3_caught", "hidden_flag": "fig3_done"})
save("content/regions/old_road.json", R)

S.update({
    "npc.unmask_knight.name": "The Headless Knight (Sat On)", "npc.unmask_knight.title": "Mystery Suspect",
    "enemy.headless_knight.name": "The Headless Knight of the Old Road",
    "line.headless_knight.alert": "HALT! I AM THE HEADLESS KNIGHT! PAY THE TOLL! Five gold! ...Four. Three is fine.",
    "line.headless_knight.death": "OW! Okay! Okay! I yield! Get the bird off!",
    "bark.steve.villain": "I would have got away with it, too. ...Did you hear me say it? I'm a VILLAIN now. I have a poster.",
    "bark.fig.sna.hero": "HRRROOT! (Snacks is standing very bravely. Behind you.)",
    "item.snacks_feather.name": "Snacks's Brave Feather",
    "item.snacks_feather.description": "A single brown feather from the bravest owlbear cub on the Old Road (it charged once; it counts). +2 armour, heals 3 when you block, steadier nerves, +15% critical damage.",
    "quest.fig3.title": "The Figure It Out Gang: The Headless Knight of the Old Road",
    "quest.fig3.summary": "A knight with no head stands in the road at night demanding tolls. Agnes says it's a hat on a stick.",
    "quest.fig3.stage0": "Talk to Sir Rodrick at the Figure It Out Wagon.",
    "quest.fig3.journal0": "A third poster. Rodrick painted this one himself.",
    "quest.fig3.stage10": "Split up and look for clues along the Old Road, then report to Rodrick.",
    "quest.fig3.journal10": "The Headless Knight of the Old Road. Five gold toll. Or four. Three is fine.",
    "quest.fig3.stage20": "Set Rodrick's trap in the middle of the Old Road.",
    "quest.fig3.journal20": "A giant cake, a net in a tree. Snacks has not stopped staring at the cake.",
    "quest.fig3.stage30": "Stop the Headless Knight!",
    "quest.fig3.journal30": "The trap caught the cake, Rodrick and a goose. Then the knight came clanking down the road.",
    "quest.fig3.stage40": "Unmask the Headless Knight.",
    "quest.fig3.journal40": "The knight is down. An owlbear cub is sitting on it.",
    "quest.fig3.stage50": "Tell Rodrick.",
    "quest.fig3.journal50": "It was Steve. He was so happy to be a real villain. Baggy barely knew her.",
    "quest.fig3.stage100": "Completed: FIGURED OUT. Snacks was brave.",
    "quest.fig3.journal100": "Snacks gave me a feather. I will treasure it forever.",
    "story.fig3.trap": "You set the trap in the middle of the Old Road: an enormous three-tier cake on a plate, a net hung in the oak above it, and a rope that runs to Rodrick, crouched in the ditch.\n\nThe gang hides. Snacks does not hide. Snacks is staring at the cake.\n\nA goose wanders up to the cake. Rodrick yanks the rope. The net catches the goose, the cake, and, somehow, Rodrick.\n\nAnd then, clank by clank, out of the dark, comes a knight in full armour. No head. Just a plume, wobbling, on top. It points a gauntlet at Baggy.\n\n\"HALT! PAY THE TOLL!\"\n\nBaggy screams. Primrose rolls up her sleeves. And Snacks, for the first time in its whole life, does not run away.",
    "tip.39": "Owlbear cubs are cowards, until somebody threatens their friends. Then they are very heavy cowards.",
})
loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("ok", len(S))

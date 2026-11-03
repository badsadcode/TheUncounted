"""Chapter One extras: companions' lines in Here (Kaelen, Baggy, Doobie, Grout), two banters about the city, and a side tale,
"Death and Taxes": Inspector Aldric Thrupp, Inspector of Hearths, deceased, still counting the chimneys of Here and unable to
rest until his ledger balances. Persuade him a struck city has no hearths on record, or find in the Register of Hearths
that he never taxed his own house: he owes himself four hundred coppers, pays himself, the ledger balances, he rests.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q = "core:quest.here_taxes"
I = lambda n: f"core:item.{n}"
QE = lambda s: {"type": "quest_stage_equals", "quest_id": Q, "stage": s}
QA = lambda s: {"type": "quest_stage_at_least", "quest_id": Q, "stage": s}
QB = lambda s: {"type": "quest_stage_below", "quest_id": Q, "stage": s}
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}
GI = lambda i, q=1: {"type": "give_item", "item_id": I(i), "qty": q}

D = load("content/dialogue/chapter_zero_dialogue.json")
D["dialogues"].append({"id": "core:dialogue.here_inspector", "root_node": "root", "nodes": {}})
dlg = D["dialogues"][-1]
def node(nid, text, choices, actions=None):
    key = f"dlg.ch1.ins.{nid}"
    S[key] = text
    n = {"speaker_key": "npc.here_inspector.name", "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, c in enumerate(choices):
        ck = f"{key}.c{i}"
        S[ck] = c[0]
        d = {"text_key": ck, "next": c[1]}
        for k, v in (c[2] if len(c) > 2 else {}).items(): d[k] = v
        n["choices"].append(d)
    dlg["nodes"][nid] = n
node("root",
     "A grey, upright ghost in a tall collar is standing in the lane, counting chimneys on a set of ghostly fingers and writing in a "
     "ledger that's mostly holes. A tin badge: INSPECTOR OF HEARTHS. Below it, a smaller badge: DECEASED (NOT RELEVANT).\n\n"
     "\"Aldric Thrupp, Inspector of Hearths. One copper per hearth per year.\" He doesn't look up. \"Forty-seven hearths. Four hundred "
     "years. Eighteen thousand eight hundred coppers outstanding. I cannot rest until the ledger balances.\" A pause. \"It does not "
     "balance.\"",
     [('"That\'s a lot of coppers."', "start", {"conditions": [QB(0)]}),
      ('"A struck city isn\'t on any record. Legally, it has no hearths." (Persuasion)', "persuaded",
       {"conditions": [QE(10), FN("here_tax_denied")], "roll": {"skill": "persuasion", "dc": 14, "fail_next": "denied"}}),
      ('"I read the Register of Hearths. About your own house..."', "himself", {"conditions": [QE(10), FS("here_hearths_read")]}),
      ('"How\'s the ledger?"', "after", {"conditions": [QA(100)]}),
      ("Leave.", "END")])
node("start",
     "\"It is EXACTLY the right number of coppers.\" He snaps the ledger shut, and a few holes fall out of it. \"Nobody has paid since "
     "the Silence. I have knocked on every door. Some of them knocked back. Nobody PAYS.\"\n\n\"I'm not unreasonable. Find me a reason "
     "the ledger should balance, and I'll go. Gladly. I have been counting chimneys for four hundred years. I would like to stop.\"\n\n"
     "(The Register of Hearths is kept at the customs post, on Ottoline's desk.)",
     [('"I\'ll see what I can do."', "root")], [SQ(0), SQ(10)])
node("persuaded",
     "You explain, slowly, as to a clerk: the Archivists struck the city off every record. It isn't on any map, any roll, any register "
     "of the realm. Legally, it doesn't exist. And a city that doesn't exist cannot have any hearths.\n\nThe Inspector's pen stops. His "
     "mouth opens. Closes. He turns back through four hundred years of ledger, very fast, holes flying.\n\n\"No hearths,\" he whispers. "
     "\"Nought owed.\" He draws a line under the total. It's the most beautiful line you've ever seen. \"It BALANCES.\"\n\nHe starts "
     "to fade, smiling, and presses something into your hand on the way out: an abacus, cold as a coin.",
     [('"Rest well, Inspector."', "root")], [SQ(100), GI("inspector_abacus"), {"type": "give_xp", "skill": "persuasion", "amount": 60}])
node("denied", "\"Every city has hearths. Even this one. ESPECIALLY this one: the bakery has three.\" He keeps counting.", [("Back.", "root")],
     [SF("here_tax_denied")])
node("himself",
     "You show him the line at the bottom of the Register: 'Inspector's residence: one hearth. EXEMPT (the Inspector does not tax "
     "himself).' And Ottoline's note underneath: NOT A REAL EXEMPTION.\n\nThe Inspector reads it nine times.\n\n\"Then I owe... one "
     "copper a year. Four hundred years.\" He takes out a ghostly purse. \"To... myself.\" He counts four hundred ghostly coppers from one "
     "hand into the other, very carefully, and writes it down.\n\n\"Received with thanks,\" he says, to himself. \"Paid in full,\" he "
     "replies.\n\nThe ledger glows. Every column adds up. He laughs, the first laugh in four hundred years, and it's a nice one.\n\n"
     "\"It's not the eighteen thousand. But it BALANCES. The rest...\" He waves a fading hand at the city. \"Forgiven. Don't tell "
     "anyone I said that.\" He presses something into your hand as he goes: an abacus, cold as a coin.",
     [('"Rest well, Inspector."', "root")], [SQ(100), GI("inspector_abacus"), {"type": "give_xp", "skill": "lore", "amount": 60},
                                             {"type": "give_gold", "amount": 40}])
node("after", "There's no one here. Just a neat little pile of four hundred very old coppers on a doorstep, and a note: PAID.", [("Leave.", "END")])
save("content/dialogue/chapter_zero_dialogue.json", D)

N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.here_inspector", "name_key": "npc.here_inspector.name", "title_key": "npc.here_inspector.title",
                  "faction": "core:faction.bureau", "dialogue_id": "core:dialogue.here_inspector",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/here_inspector.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 1.85},
                  "barks": [{"text_key": "bark.here_inspector.0"}, {"text_key": "bark.here_inspector.1"}]})
S.update({"npc.here_inspector.name": "Inspector Aldric Thrupp", "npc.here_inspector.title": "Inspector of Hearths (Deceased)",
          "bark.here_inspector.0": "Forty-five. Forty-six. Forty-seven hearths. Nobody PAYS.",
          "bark.here_inspector.1": "One copper per hearth per year. It's not complicated. It's just OVERDUE."})

# companions in Here
lines = {
    "core:npc.ashbound_scout": ("kaelen", "We're not on any map. Good. The Hunger reads maps too. Keep your name in your mouth.",
                                "Archivists. Like the ones under the Annex. They hid people the only way they knew: on paper. Off paper."),
    "core:npc.detective_baggy": ("baggy", "A whole city full of people who don't know who they are. As a detective, I find this professionally thrilling and personally terrifying.",
                                 "Shelves. Mouths. Nobody's labelled anything. I'm going to stand very close to you."),
    "core:npc.figure_snacks": ("snacks", "(Doobie sniffs the air, smells bread from four hundred years ago, and whines with longing.)",
                               "(Doobie takes one look at the Mouths, sits down behind you, and puts both wings over its head.)"),
    "core:npc.grout": ("grout", "...Old stone. Older than me. Doesn't know its own name either.\n\nI like it.",
                       "...Quiet in here.\n\nToo quiet. Something's chewing."),
}
for n in N["npcs"]:
    if n["id"] in lines and n.get("companion"):
        tag, here, archive = lines[n["id"]]
        n["companion"]["zone_lines"]["here"] = f"comp.{tag}.zone.here"
        n["companion"]["zone_lines"]["here_archive"] = f"comp.{tag}.zone.here_archive"
        S[f"comp.{tag}.zone.here"] = here
        S[f"comp.{tag}.zone.here_archive"] = archive
    if n["id"] == "core:npc.ashbound_scout":
        n["companion"].setdefault("banter", []).append({"id": "here_names", "partner": "core:npc.detective_baggy", "flag": "here_visited", "lines": [
            {"by": "partner", "text_key": "comp.kaelen.banter.here_names.0"}, {"by": "self", "text_key": "comp.kaelen.banter.here_names.1"},
            {"by": "partner", "text_key": "comp.kaelen.banter.here_names.2"}, {"by": "self", "text_key": "comp.kaelen.banter.here_names.3"}]})
    if n["id"] == "core:npc.grout":
        n["companion"].setdefault("banter", []).append({"id": "here_bread", "partner": "core:npc.figure_snacks", "flag": "here_frag_smell", "lines": [
            {"by": "partner", "text_key": "comp.grout.banter.here_bread.0"}, {"by": "self", "text_key": "comp.grout.banter.here_bread.1"},
            {"by": "partner", "text_key": "comp.grout.banter.here_bread.2"}, {"by": "self", "text_key": "comp.grout.banter.here_bread.3"}]})
S.update({
    "comp.kaelen.banter.here_names.0": "BAGGY: \"Kaelen. If someone ate YOUR name, what would you pick? I'd pick Butt-Butt. That child is a genius.\"",
    "comp.kaelen.banter.here_names.1": "KAELEN: \"The Ashbound don't pick names. We keep the ones we're given, and say them out loud every night so nothing can take them.\"",
    "comp.kaelen.banter.here_names.2": "BAGGY: \"...That's beautiful. That's genuinely beautiful. So what's yours? Your whole name?\"",
    "comp.kaelen.banter.here_names.3": "KAELEN: \"Nice try, detective.\"",
    "comp.grout.banter.here_bread.0": "(Doobie trots up to Grout, holding a loaf of the Bread of Here very carefully in its beak, and offers it up.)",
    "comp.grout.banter.here_bread.1": "GROUT: \"...I'm stone. I don't eat.\"",
    "comp.grout.banter.here_bread.2": "(Doobie keeps holding it up. Hopefully. For a long time.)",
    "comp.grout.banter.here_bread.3": "GROUT: \"...Fine.\" (Grout puts the loaf in a crack in its shoulder, for later. Doobie is overjoyed.)",
})
save("content/npcs/core_npcs.json", N)

A = load("content/items/armor_and_gear.json")
A["items"].append({"id": I("inspector_abacus"), "name_key": "item.inspector_abacus.name", "description_key": "item.inspector_abacus.description",
                   "category": "accessory", "icon": "assets/ui/items/inspector_abacus.png", "world_model": "assets/models/items/signet_ring.glb",
                   "slots": ["accessory"], "value": 260, "weight": 0.4,
                   "effects": [{"type": "bonus", "stat": "gold_find_bonus", "value": 0.15}, {"type": "bonus", "stat": "lockpick_bonus", "value": 2.0}]})
S["item.inspector_abacus.name"] = "The Inspector's Abacus"
S["item.inspector_abacus.description"] = ("Aldric Thrupp's ghostly abacus, cold as a coin. Its beads slide on their own when there's money nearby, and click "
                                          "disapprovingly at locks. More gold finds you, and locks give a little.")
save("content/items/armor_and_gear.json", A)

QQ = load("content/quests/chapter_zero_quests.json")
QQ["quests"].append({"id": Q, "title_key": "quest.taxes.title", "summary_key": "quest.taxes.summary", "campaign": "chapter_one", "stages": [
    {"stage": 0, "objective_key": "quest.taxes.stage0", "journal_key": "quest.taxes.journal0", "markers": ["npc_here_inspector"]},
    {"stage": 10, "objective_key": "quest.taxes.stage10", "journal_key": "quest.taxes.journal10", "markers": ["here_hearth_register", "npc_here_inspector"]},
    {"stage": 100, "objective_key": "quest.taxes.stage100", "journal_key": "quest.taxes.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.taxes.title": "Death and Taxes", "quest.taxes.summary": "A ghost tax inspector can't rest until his ledger balances. It does not balance.",
    "quest.taxes.stage0": "Talk to the Inspector of Hearths.", "quest.taxes.journal0": "A ghost is counting chimneys in Here.",
    "quest.taxes.stage10": "Find a reason Inspector Thrupp's ledger should balance (the Register of Hearths is at the customs post), or argue the point.",
    "quest.taxes.journal10": "Forty-seven hearths, four hundred years, eighteen thousand eight hundred coppers owed, and nobody pays. He'd like to stop.",
    "quest.taxes.stage100": "Completed: the ledger balances.", "quest.taxes.journal100": "Inspector Thrupp's ledger balances at last, and he can rest.",
})
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

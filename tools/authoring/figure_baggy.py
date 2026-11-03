"""The Figure It Out Gang, revision: Toasty's original gang had BAGGY in the cowardly-hungry role, so Crumbs is written
out and Baggy (they/them, the private eye) takes the part, with new gang topics in Baggy's own dialogue.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

loc = load("content/localization/en.json")
S = loc["strings"]
EDITS = [
    ("dlg.fig.rod.root", "Lady Primrose, Agnes, Crumbs, and Snacks.", "Lady Primrose, Agnes, Baggy, and Snacks. You might know Baggy. Everyone knows Baggy."),
    ("dlg.fig.rod.what", "CRUMBS (from under the wagon)", "BAGGY (from under the wagon)"),
    ("dlg.fig.rod.e1_open", "something chases Crumbs.", "something chases Baggy."),
    ("dlg.fig.rod.e1_open", "CRUMBS: \"Every time.\"", "BAGGY: \"Every time. I've started to take it personally.\""),
    ("dlg.fig.rod.e1_trap", "We'll use Crumbs as the bait.", "We'll use Baggy as the bait."),
    ("dlg.fig.rod.e1_trap", "CRUMBS: \"No.\"", "BAGGY: \"Absolutely not. I'm a professional.\""),
    ("dlg.fig.rod.e1_done", "our trap caught Baggy, a pigeon, and Rodrick", "our trap caught Clerk Oakhaven, a pigeon, and Rodrick"),
    ("dlg.fig.rod.e1_done", "Crumbs's favourite.", "Baggy's favourite."),
    ("dlg.fig.rod.e2_trap", "CRUMBS: \"I ate the marrow.\"", "BAGGY (brushing crumbs off the coat): \"I ate the marrow. It was evidence. I was examining it.\""),
    ("dlg.fig.rod.later", "Crumbs barely knew her.", "Baggy barely knew her."),
    ("dlg.fig.rod.later", "CRUMBS (from somewhere)", "BAGGY (from somewhere)"),
    ("dlg.fig.prim.advice", "Never let Crumbs hold the bait.", "Never let Baggy hold the bait. Baggy will eat the bait."),
    ("dlg.fig.unmask1.root", "after Baggy, a pigeon and Rodrick", "after Clerk Oakhaven, a pigeon and Rodrick"),
    ("dlg.fig.unmask1.reveal", "CRUMBS: \"I barely knew her!\"", "BAGGY: \"I barely knew her!\""),
    ("dlg.fig.unmask2.root", "CRUMBS: \"I barely knew her.\"", "BAGGY: \"I barely knew her.\""),
    ("dlg.fig.unmask2.reveal", "CRUMBS: \"I barely knew her!\"", "BAGGY: \"I barely knew her!\""),
    ("dlg.fig.unmask2.rolf", "So does Crumbs, for some reason.", "So does Baggy, for some reason, into the magnifying glass."),
    ("item.crumb_cake.description", "Crumbs's favourite.", "Baggy's favourite (kept loose in the coat pockets, hence the name)."),
    ("quest.fig1.journal10", "Crumbs ran.", "Baggy ran."),
    ("quest.fig1.journal30", "The trap caught Baggy, a pigeon and Rodrick.", "The trap caught Clerk Oakhaven, a pigeon and Rodrick."),
    ("quest.fig1.journal50", "Crumbs barely knew her.", "Baggy barely knew her."),
    ("quest.fig2.journal20", "Crumbs ate the marrow.", "Baggy ate the marrow."),
    ("story.fig1.trap", "Snacks hides behind Crumbs. Crumbs hides behind Snacks.", "Snacks hides behind Baggy. Baggy hides behind Snacks."),
    ("story.fig1.trap", "catches Baggy, who was just passing, investigating something.",
     "catches Clerk Oakhaven, who was just passing with a form about the lantern post."),
    ("story.fig2.trap", "and Crumbs crouched in the middle of the bed pretending to be a marrow. He's not very convincing. He's eating.",
     "and Baggy crouched in the middle of the bed in the long coat, pretending to be a marrow. Baggy is not very convincing. Baggy is eating."),
]
for k, old, new in EDITS:
    assert old in S[k], (k, old)
    S[k] = S[k].replace(old, new)
for k in [k for k in S if k.startswith("dlg.fig.cru.") or k.startswith("npc.figure_crumbs.") or k == "bark.fig.cru"]:
    del S[k]
NEW = {
    "dlg.baggy.choice_gang": "\"You're in the Figure It Out Gang?\"",
    "dlg.baggy.gang": "Baggy straightens the coat with enormous dignity, and a Crumb Cake falls out of it.\n\n\"Founding member. Before the agency, before the magnifying glass, there was the wagon. Rodrick, Primrose, Agnes, Snacks and me. Every weekend, a monster. Every monster, a mask. It's where I learned everything I know about detection.\"\n\nA pause. \"Mostly I learned to run. But running IS detection, if you do it in the direction of clues. Or away from them. It's about direction.\"\n\nSnacks, at the wagon, hoots hopefully at the sound of Baggy's voice.",
    "dlg.baggy.gang.c0": "\"Do you ever get scared?\"",
    "dlg.baggy.gang.c1": "\"Why do you always say 'I barely knew her'?\"",
    "dlg.baggy.gang.c2": "\"Back to business.\"",
    "dlg.baggy.gang_scared": "BAGGY: \"Scared? Me? Only of ghosts. And monsters. And the dark. And skeletons. And Rodrick's plans. And the wagon when it makes that noise going downhill.\" Baggy produces a sandwich from an inside pocket and takes a thoughtful bite. \"Snacks is braver than me. Snacks is NOT brave.\"",
    "dlg.baggy.gang_scared.c0": "\"Fair.\"",
    "dlg.baggy.gang_barely": "BAGGY (thinking very hard, magnifying glass to chin): \"Every time we pull off a mask, everyone goes 'IT WAS HIM ALL ALONG!' or 'IT WAS HER!' and everyone's shocked. And I just... I barely knew her. Whoever it is. I barely knew her.\"\n\n\"Even the time it was a horse.\"",
    "dlg.baggy.gang_barely.c0": "\"It was a horse?\"",
    "dlg.baggy.gang_horse": "BAGGY: \"Brown one. White blaze on the nose. Standing on a roof. Wasn't even a mystery. It was just a horse on a roof.\" A long, meaningful chew. \"I barely knew her.\"\n\n\"I know her quite well now, actually. Lovely horse. Terrible witness.\"",
    "dlg.baggy.gang_horse.c0": "\"Trout.\"",
    "bark.baggy.barely": "I barely knew her!",
}
S.update(NEW)
save("content/localization/en.json", loc)

D = load("content/dialogue/chapter_zero_dialogue.json")
D["dialogues"] = [d for d in D["dialogues"] if d["id"] != "core:dialogue.figure_crumbs"]
b = [d for d in D["dialogues"] if d["id"] == "core:dialogue.detective_baggy"][0]
sp = "npc.detective_baggy.name"
def node(nid, choices):
    b["nodes"][nid] = {"speaker_key": sp, "text_key": f"dlg.baggy.{nid}",
                       "choices": [{"text_key": f"dlg.baggy.{nid}.c{i}", "next": n} for i, n in enumerate(choices)]}
node("gang", ["gang_scared", "gang_barely", "root"])
node("gang_scared", ["gang"])
node("gang_barely", ["gang_horse"])
node("gang_horse", ["gang"])
ch = b["nodes"]["root"]["choices"]
end = next(i for i, c in enumerate(ch) if c["next"] == "END")
ch.insert(end, {"text_key": "dlg.baggy.choice_gang", "next": "gang"})
save("content/dialogue/chapter_zero_dialogue.json", D)

N = load("content/npcs/core_npcs.json")
N["npcs"] = [n for n in N["npcs"] if n["id"] != "core:npc.figure_crumbs"]
for n in N["npcs"]:
    if n["id"] == "core:npc.detective_baggy":
        n.setdefault("barks", []).append({"text_key": "bark.baggy.barely", "flag": "fig1_unmasked"})
save("content/npcs/core_npcs.json", N)
R = load("content/regions/old_road.json")
R["npcs"] = [n for n in R["npcs"] if n["instance_id"] != "npc_figure_crumbs"]
save("content/regions/old_road.json", R)
print("ok")

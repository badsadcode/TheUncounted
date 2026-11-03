"""Snacks the cowardly owlbear cub as a companion (after the Figure It Out Gang's third episode, when Snacks was brave
once). Hides in fights, hoots a lot, brings you snacks when you're hurt. Banter with Grout, Baggy and Kaelen.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
SP = "npc.figure_snacks.name"

D = load("content/dialogue/chapter_zero_dialogue.json")
dl = [d for d in D["dialogues"] if d["id"] == "core:dialogue.figure_snacks"][0]
ch = dl["nodes"]["root"]["choices"]
end = next(i for i, c in enumerate(ch) if c["next"] == "END")
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
new = [("c_join", '"Want to come adventuring with me, Snacks?"', "join", [FS("fig3_done"), FN("snacks_following"), {"type": "party_has_room"}]),
       ("c_full", '"Want to come adventuring with me, Snacks?"', "full", [FS("fig3_done"), FN("snacks_following"), {"type": "party_full"}]),
       ("c_home", '"Go back to the wagon for a bit, Snacks."', "home", [FS("snacks_following")])]
for k, t, nxt, cond in new:
    S[f"dlg.fig.sna.root.{k}"] = t
ch[end:end] = [{"text_key": f"dlg.fig.sna.root.{k}", "next": nxt, "conditions": cond} for k, t, nxt, cond in new]
def node(nid, text, choices, actions=None):
    key = f"dlg.fig.sna.{nid}"
    S[key] = text
    n = {"speaker_key": SP, "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, (t, nx) in enumerate(choices):
        S[f"{key}.c{i}"] = t
        n["choices"].append({"text_key": f"{key}.c{i}", "next": nx})
    dl["nodes"][nid] = n
node("join",
     "Snacks looks at you. Then at Rodrick. Then at you. Then, very slowly, at your pockets.\n\nRODRICK (from the wagon, wiping away a tear): \"Go on, "
     "Snacks. You were brave once. You can be brave again. Have it back by bedtime!\"\n\nSnacks trots to your side, sits down on your foot, and looks up at "
     "you with enormous trusting eyes.\n\n\"Hrrr-oo.\"",
     [("\"Let's go, Snacks.\"", "END")], [{"type": "set_flag", "flag": "snacks_following", "value": True}, {"type": "recruit_companion"}])
node("full", "Snacks peers at your companions, counts them on its talons (it gets to three and gives up), and sits down again, disappointed.\n\n\"Hrrr.\"",
     [("\"Another time, Snacks.\"", "root")])
node("home", "Snacks trudges back to the wagon, looking over its shoulder every three steps in case you change your mind. You don't. It's very hard.",
     [("Leave.", "END")], [{"type": "set_flag", "flag": "snacks_following", "value": False}, {"type": "dismiss_companion"}])
save("content/dialogue/chapter_zero_dialogue.json", D)

def lines(group, items):
    out = []
    for i, it in enumerate(items, 1):
        text, cond = (it, {}) if isinstance(it, str) else it
        k = f"comp.snacks.{group}.{i}"
        S[k] = text
        out.append((k, cond))
    return out
idle = lines("idle", [
    "Hrrr-oo? (Snacks has found a beetle. Snacks is showing you the beetle.)", "(Snacks walks exactly in your footprints. All of them.)",
    "Hoot. (A very small, contented hoot.)", "(Snacks is looking at your pockets again.)", "(Snacks has fallen over. On purpose, it seems. For fun.)",
    "Hrrr. (Snacks sniffs the air and decides something is suspicious. Possibly a leaf.)", "(A leaf blows past. Snacks hides behind you. The leaf leaves.)",
    "Hrrr-OOT! (Snacks has seen a moth. Snacks is going to catch the moth. Snacks did not catch the moth.)",
    ("(Snacks walks a little closer to Grout. Grout pretends not to notice. Grout notices.)", {"flag": "grout_following"}),
    ("(Snacks keeps checking that Baggy is still there. Baggy keeps checking that Snacks is still there.)", {"flag": "baggy_following"}),
])
combat = lines("combat", ["HRRRR-OO! (Snacks hides behind you.)", "(Snacks hides behind the nearest rock. The rock is too small.)",
                          "Hoot! Hoot! (moral support, from a distance)", "(Snacks puffs up to twice its size. Then hides.)"])
kill = lines("kill", ["Hrrr-OOT! (Snacks does a victory spin.)", "(Snacks comes out from behind you, very proud of both of you.)",
                      "Hoot. (Snacks pats the defeated monster on the head, just to be sure.)"])
heal = lines("heal", ["(Snacks drops a slightly chewed Crumb Cake at your feet. For you. Its last one.)",
                      "Hrrr-oo. (Snacks presses a crumpled honey bun into your hand and looks very worried.)",
                      "(Snacks gives you a snack and a long, careful look, the way you'd check on a friend.)"])
level = lines("level", ["HOOT! (Snacks is very proud of you.)", "(Snacks does a little dance. You're not sure it knows why. It's happy for you.)"])
catchup = lines("catchup", ["(Snacks comes galloping up, breathless and offended.) HRRR-OO!", "(Snacks arrives, hoots once, and sits on your foot so you can't leave again.)"])
zones = {"bellwether": "Hrrr-oo! (Snacks loves Bellwether. Snacks loves everything.)", "old_road": "(Snacks looks for the wagon. Snacks waves at the wagon.)",
         "annex": "Hrrr... (Snacks does not like the basement. Snacks walks very close to you.)", "vault_three": "(Snacks is trembling. Snacks is still here, though.)",
         "seal_chamber": "(Snacks has closed its eyes. Snacks is walking with its eyes closed. This is not safer.)",
         "hollowmere": "Hoot? (Snacks remembers the Howler. Snacks keeps an eye on the garden.)",
         "hollowmere_manor": "(Snacks sees the grand staircase and immediately wants to slide down the banister.)",
         "saltmere": "Hrrr-oo! (Fish smell. Snacks approves of the fish smell.)", "sunken_chapel": "(Snacks does not like water. Snacks does not like this at all.)",
         "whistling_wood": "Hoot! Hoot! (Snacks is home. Snacks is very, very home.)", "sleepers_reef": "(Snacks is in the boat. Snacks will stay in the boat, thank you.)"}
banter = []
def bant(bid, partner, convo):
    ls = []
    for i, (who, t) in enumerate(convo):
        k = f"comp.snacks.banter.{bid}.{i}"
        S[k] = t
        ls.append({"by": "self" if who == "SNACKS" else "partner", "text_key": k})
    banter.append({"id": bid, "partner": partner, "lines": ls})
bant("grout_stare", "core:npc.grout", [("SNACKS", "Hrrr-oo?"), ("GROUT", "No."), ("SNACKS", "Hrrr-oo?"), ("GROUT", "...Fine. One pat."),
                                       ("SNACKS", "(Snacks receives one pat. Snacks has never been happier.)")])
bant("grout_perch", "core:npc.grout", [("SNACKS", "(Snacks has climbed onto Grout's shoulders.)"), ("GROUT", "Get down."),
                                       ("SNACKS", "Hoot."), ("GROUT", "...Stay there, then. Don't tell anyone.")])
bant("baggy_bravery", "core:npc.detective_baggy", [("BAGGY", "Snacks, if something jumps out at us, the plan is: we both run."),
                                                   ("SNACKS", "Hrrr-oo!"), ("BAGGY", "In different directions, so it has to choose."),
                                                   ("SNACKS", "(Snacks thinks about this, and moves to stand behind Baggy.)"), ("BAGGY", "...That's fair.")])
bant("baggy_barely", "core:npc.detective_baggy", [("BAGGY", "Remember the Howler, Snacks? When the mask came off?"), ("SNACKS", "Hoot!"),
                                                  ("BAGGY", "I barely knew her."), ("SNACKS", "HRRR-OO! (Snacks barely knew her either.)")])
bant("kaelen_chronicle", "core:npc.ashbound_scout", [("KAELEN", "I'm putting you in the chronicle, Snacks. 'A small owlbear of great courage.'"),
                                                     ("SNACKS", "(Snacks hides behind Kaelen.)"), ("KAELEN", "'Of occasional courage.'"),
                                                     ("SNACKS", "Hoot. (agreed)")])

N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.figure_snacks":
        n["companion"] = {"damage": 6, "attack_time": 1.1, "reach": 1.5, "heal_amount": 28, "heal_cooldown": 38,
                          "zone_lines": {z: f"comp.snacks.zone.{z}" for z in zones},
                          "idle_lines": [dict({"text_key": k}, **c) for k, c in idle], "combat_lines": [k for k, _ in combat],
                          "kill_lines": [k for k, _ in kill], "heal_lines": [k for k, _ in heal], "level_lines": [k for k, _ in level],
                          "catchup_lines": [k for k, _ in catchup], "banter": banter}
save("content/npcs/core_npcs.json", N)
for z, t in zones.items(): S[f"comp.snacks.zone.{z}"] = t
S["tip.43"] = "After the Headless Knight, ask Snacks along. Snacks won't fight much, but Snacks always shares its snacks when you're hurt."
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

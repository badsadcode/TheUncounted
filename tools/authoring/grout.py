"""Grout: a grumpy, terse gargoyle companion (written for the user to voice on stream; recordings go in
assets/audio/voice/<line key>.ogg). The Bureau classified Grout as a 'fixture, not a citizen', so Grout is
legally nobody too. Punches hard. Says little.

Also writes docs/GROUT_VOICE_SCRIPT.md (every line, in script format, with its file name).

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
SCRIPT = []   # (section, key, speaker, text)
SP = "npc.grout.name"

# ------------------------------------------------------------------ dialogue
D = load("content/dialogue/chapter_zero_dialogue.json")
D["dialogues"].append({"id": "core:dialogue.grout", "root_node": "root", "nodes": {}})
dn = D["dialogues"][-1]["nodes"]
def node(nid, text, choices, actions=None):
    key = f"dlg.grout.{nid}"
    S[key] = text
    SCRIPT.append(("Conversation", key, "GROUT", text))
    n = {"speaker_key": SP, "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, c in enumerate(choices):
        ck = f"{key}.c{i}"
        S[ck] = c[0]
        d = {"text_key": ck, "next": c[1]}
        if len(c) > 2 and c[2]: d["conditions"] = c[2]
        n["choices"].append(d)
    dn[nid] = n
FN = lambda f: {"type": "flag_not_set", "flag": f}
FS = lambda f: {"type": "flag_set", "flag": f}
node("root",
     "A squat stone gargoyle sits on an upturned bucket beside the Records Office door, arms folded, glaring at the rain. Moss on the "
     "shoulders. One horn chipped.\n\nIt looks at you. Keeps looking.\n\n\"What.\"",
     [('"Who are you?"', "who"),
      ('"Want to come along?"', "join", [FN("grout_following"), {"type": "party_has_room"}]),
      ('"Want to come along?"', "full", [FN("grout_following"), {"type": "party_full"}]),
      ('"Wait here a while, Grout."', "wait", [FS("grout_following")]),
      ('"Any advice?"', "advice"),
      ('"Do you like anything?"', "like"),
      ("Leave.", "END")])
node("who", "\"Grout.\"\n\nA long pause.\n\n\"Gargoyle. Records Office roof. Two hundred years.\" Another pause. \"Then the Bureau did an inventory.\"",
     [('"What happened?"', "fixture")])
node("fixture", "\"Classified me. 'Fixture. Not citizen.' Same form as the gutters.\"\n\nA stone thumb jabs at the roof.\n\n\"Gutters kept their job.\"",
     [('"So you\'re legally nobody. Like me."', "same", [FN("grout_kin")]), ('"Rough."', "root")])
node("same", "Grout looks at you properly for the first time.\n\n\"Huh.\"\n\nThat's it. That's the whole reaction. Somehow it feels like a lot.",
     [('"Huh."', "root")], [{"type": "set_flag", "flag": "grout_kin", "value": True}])
node("join", "\"No.\"\n\nGrout stands up anyway. The bucket stays dented.\n\n\"Somebody's got to hit things. You look like you'd talk to them.\"",
     [('"Let\'s go."', "END")], [{"type": "set_flag", "flag": "grout_following", "value": True}, {"type": "recruit_companion"}])
node("full", "Grout looks past you at your companions.\n\n\"Too many people.\" Arms fold. \"Hate crowds.\"", [('"Fair."', "root")])
node("wait", "\"Fine.\"\n\nGrout sits down exactly where Grout is standing.\n\n\"Don't be long. Or do. Whatever.\"",
     [("Leave.", "END")], [{"type": "set_flag", "flag": "grout_following", "value": False}, {"type": "dismiss_companion"}])
node("advice", "\"Hit first.\"\n\n\"Hit hard.\"\n\n\"Don't explain yourself.\"\n\nA pause.\n\n\"That's it. That's all the advice.\"", [('"Noted."', "root")])
node("like", "\"Rain. Quiet. Pigeons.\"\n\nGrout considers.\n\n\"Not the pigeons.\"", [('"Noted."', "root")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ companion lines
L = {}
def lines(group, items):
    out = []
    for i, it in enumerate(items, 1):
        text, cond = (it, {}) if isinstance(it, str) else it
        key = f"comp.grout.{group}.{i}"
        S[key] = text
        L.setdefault(group, []).append((key, cond))
        out.append(key)
    return out
idle = lines("idle", [
    "Hm.", "Walking. Great. Love walking.", "Stone doesn't get tired. Stone gets bored.", "Two hundred years on a roof. This is worse.",
    "You're doing the thing where you look at everything. Stop it.", "...No. Nothing. Keep going.", "If anyone asks, I'm decorative.",
    "Rain's nice. Don't tell anyone.", "Your bag. Too much stuff. Drop the spoon.", "I'm not lost. You're lost.",
    ("The detective talks a lot.", {"flag": "baggy_following"}), ("Rain stopped. Shame.", {"flag": "seal_renewed"}),
    ("That witch set fire to my bucket. Respect.", {"flag": "sabrino_in_town"}), ("The owlbear. Brave. Stupid. Brave.", {"flag": "fig3_done"}),
    ("Fixtures. Us. Hm. Good team.", {"flag": "grout_kin"}), ("A horse on a roof. Amateur. Try two hundred years.", {"flag": "trout_case"}),
])
combat = lines("combat", ["Finally.", "Mine.", "Hold still.", "Here we go.", "Stand back."])
kill = lines("kill", ["Done.", "Next.", "Stayed down. Good.", "That was it?"])
heal = lines("heal", ["Eat. Don't argue.", "Bread. Found it. Don't ask where.", "You're leaking. Fix that."])
level = lines("level", ["Stronger. Barely.", "Huh. Progress."])
catchup = lines("catchup", ["Door. Closed. In my face.", "You left. I noticed.", "Stairs. Hate stairs.", "Here. Don't do that again."])
zones = {"bellwether": "Home. Roof's that way. Don't look at it.", "old_road": "Road. Long. Dusty. Great.", "annex": "Bureau basement. Smells like forms.",
         "vault_three": "Old stone in here. Older than me. Show-offs.", "seal_chamber": "Don't touch anything. ...You're going to touch something.",
         "hollowmere": "Haunted house. Course it is.", "hollowmere_manor": "Good ceilings. Good roof. I'd perch there.", "saltmere": "Fish. Everywhere. Fish.",
         "sunken_chapel": "Underwater church. Stone hates water. I hate water.", "whistling_wood": "Trees. Whistling. Make it stop.",
         "sleepers_reef": "I sink. Remember that. I sink."}
zone_lines = {}
for z, t in zones.items():
    k = f"comp.grout.zone.{z}"
    S[k] = t
    zone_lines[z] = k
banter = []
def bant(bid, partner, convo):
    ls = []
    for i, (who, text) in enumerate(convo):
        k = f"comp.grout.banter.{bid}.{i}"
        S[k] = text
        ls.append({"by": "self" if who == "GROUT" else "partner", "text_key": k})
        SCRIPT.append((f"Banter ({bid})", k, who, text))
    banter.append({"id": bid, "partner": partner, "lines": ls})
B, K = "core:npc.detective_baggy", "core:npc.ashbound_scout"
bant("baggy_story", B, [("BAGGY", "So, Grout! What's your story? Every gargoyle has a story."), ("GROUT", "No."),
                         ("BAGGY", "Mysterious! I like it."), ("GROUT", "Not mysterious. Just no.")])
bant("baggy_masks", B, [("BAGGY", "Grout, have you ever unmasked a monster?"), ("GROUT", "Punched one."),
                         ("BAGGY", "Did it turn out to be someone in a mask?"), ("GROUT", "Did after.")])
bant("baggy_barely", B, [("BAGGY", "I barely knew her!"), ("GROUT", "Who?"), ("BAGGY", "Nobody. It's just a thing I say."), ("GROUT", "Stop.")])
bant("kaelen_roof", K, [("KAELEN", "Two hundred years on that roof. You must have seen everything."), ("GROUT", "Pigeons."),
                         ("KAELEN", "And?"), ("GROUT", "More pigeons.")])
bant("kaelen_chronicle", K, [("KAELEN", "I'm writing a chronicle of this journey. Anything you want recorded?"), ("GROUT", "Hit things."),
                              ("KAELEN", "...I'll paraphrase.")])

N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.grout", "name_key": SP, "title_key": "npc.grout.title", "faction": "core:faction.ashbound",
    "dialogue_id": "core:dialogue.grout",
    "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/grout.png", "animation_data": "assets/animations/npc_standard.json", "scale": 1.5},
    "barks": [{"text_key": "bark.grout.1"}, {"text_key": "bark.grout.2"}],
    "companion": {"damage": 11, "attack_time": 1.5, "reach": 1.7, "heal_amount": 15, "heal_cooldown": 60, "zone_lines": zone_lines,
                  "idle_lines": [dict({"text_key": k}, **c) for k, c in L["idle"]], "combat_lines": combat, "kill_lines": kill,
                  "heal_lines": heal, "level_lines": level, "catchup_lines": catchup, "banter": banter}})
save("content/npcs/core_npcs.json", N)
S.update({"npc.grout.name": "Grout", "npc.grout.title": "Gargoyle (Fixture, Not Citizen)", "bark.grout.1": "What.", "bark.grout.2": "Move along."})

R = load("content/regions/bellwether.json")
R["npcs"].append({"instance_id": "npc_grout", "npc_id": "core:npc.grout", "pos": [-12.0, 0.0, -6.0], "yaw": 135.0, "hidden_flag": "grout_following_never"})
save("content/regions/bellwether.json", R)
S["tip.40"] = "Grout, the gargoyle by the Records Office, hits harder than anyone in Bellwether. Grout will not tell you this. Grout will not tell you anything."
loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)

# ------------------------------------------------------------------ the voice script
out = ["# Grout: voice script", "",
       "Every line Grout says, in read-aloud script format. You can read them live on stream as they pop up as subtitles,",
       "or record them: save each one as `assets/audio/voice/<file name>.ogg` (or `.wav` / `.mp3`) and the game plays",
       "your recording with the subtitle. Lines without a recording just show as text, so you can record a few at a time.",
       "", "**Grout:** a squat, mossy stone gargoyle. Grumpy. Few words. Every line is short and dry; the pause is part of it.",
       "Two hundred years on the Records Office roof, until the Bureau classified Grout as 'a fixture, not a citizen'.",
       "", "Tip: record in a quiet room, a little closer to the mic than normal, and leave half a second of silence at the end.",
       "Mono, 44.1 or 48 kHz. Any line key in the game works the same way, so this also works for other characters.", ""]
def section(title, pairs):
    out.extend([f"## {title}", "", "| File name | Line |", "|---|---|"])
    for k, t in pairs:
        out.append(f"| `{k}` | GROUT: {t} |")
    out.append("")
section("When Grout joins, walks, chats (random, every minute or two)", [(k, S[k] + (f" *(after: {c['flag']})*" if c else "")) for k, c in L["idle"]])
section("First time in each area", [(zone_lines[z], S[zone_lines[z]]) for z in zones])
section("A fight starts", [(k, S[k]) for k in combat])
section("A fight ends", [(k, S[k]) for k in kill])
section("Hands you food when you're badly hurt", [(k, S[k]) for k in heal])
section("You level up", [(k, S[k]) for k in level])
section("Catching up after being left behind", [(k, S[k]) for k in catchup])
section("Passing by (before Grout joins)", [("bark.grout.1", "What."), ("bark.grout.2", "Move along.")])
out.extend(["## Conversation (when you talk to Grout)", "",
            "The file name plays when that page of the conversation opens. Narration (the bits not in quotes) can be left out.", ""])
for sec, k, who, t in SCRIPT:
    if sec == "Conversation":
        out.append(f"**`{k}`**\n\n> " + t.replace("\n\n", "\n>\n> ") + "\n")
out.extend(["## Banter with Baggy and Kaelen", "", "Only Grout's lines need recording (the other parts are someone else's), but here's the whole exchange.", ""])
cur = None
for sec, k, who, t in SCRIPT:
    if sec.startswith("Banter"):
        if sec != cur:
            out.append(f"**{sec}**\n"); cur = sec
        out.append(f"- `{k}` **{who}:** {t}" if who == "GROUT" else f"- *{who}: {t}*")
out.append("")
open("docs/GROUT_VOICE_SCRIPT.md", "w").write("\n".join(out))
print("ok", len(S))

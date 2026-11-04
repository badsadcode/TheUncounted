"""Dunstan's favourite games, as affectionate unnamed references: turn-based squad tactics (the 95% shot that misses,
overwatch, never end your turn out of cover, naming your squad after your friends), a hardcore roguelike RPG (broken
legs, fevers, bandaging the bandages) and an open-world survival game (waking up naked in a desert, punching rocks,
building a fortress). He's good at all of them. Includes a rigged 95% Athletics roll that always fails the first time.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
P = {"eranu": "core:npc.eranu", "coth": "core:npc.coth", "baggy": "core:npc.detective_baggy"}

D = load("content/dialogue/chapter_zero_dialogue.json")
dl = next(d for d in D["dialogues"] if d["id"] == "core:dialogue.dunstan")
root = dl["nodes"]["root"]
end = next(i for i, c in enumerate(root["choices"]) if c["next"] == "END")
new = [("c_help", "[Athletics] \"Let me help you lift Big Margaret.\"", "lift_together",
        {"roll": {"skill": "athletics", "dc": 2, "fail_next": "ninety_five", "rigged": True}}),
       ("c_tactics", "\"Do you plan your fights?\"", "tactics", {}),
       ("c_scars", "\"That's a lot of scars for a squire.\"", "scars", {}),
       ("c_armour", "\"Where did you get your armour?\"", "armour", {})]
for k, t, nx, opt in new:
    S[f"dlg.dunstan.root.{k}"] = t
root["choices"][end:end] = [dict({"text_key": f"dlg.dunstan.root.{k}", "next": nx}, **opt) for k, t, nx, opt in new]


def node(nid, text, choices, actions=None):
    key = f"dlg.dunstan.{nid}"
    S[key] = text
    n = {"speaker_key": "npc.dunstan.name", "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, (t, nx) in enumerate(choices):
        S[f"{key}.c{i}"] = t
        n["choices"].append({"text_key": f"{key}.c{i}", "next": nx})
    dl["nodes"][nid] = n


node("ninety_five",
     "You take one side of the hilt, Dunstan takes the other. Ninety-five percent. A sure thing.\n\nYou both heave. Big Margaret "
     "does not move. You both fall over.\n\nDunstan lies flat on his back on the cobbles, staring at the sky.\n\n\"Ninety-five "
     "percent,\" he says quietly. \"NINETY-FIVE. It's always the ninety-five. I have lost entire squads to ninety-five percent.\"",
     [("\"Try again?\"", "root")])
node("lift_together",
     "You both heave, and this time Big Margaret rises, gleaming, into the air, and stays there.\n\n\"WE DID IT!\" Dunstan's "
     "voice cracks. \"Two-person sword technique! Nobody in my family ever thought of that!\" A pause. \"Probably because it "
     "needs two people. We were never very good at asking for help.\"\n\nBig Margaret comes down very gently, which is a first.",
     [("\"Teamwork.\"", "root")], [{"type": "give_xp", "skill": "athletics", "amount": 15}])
node("tactics",
     "\"ALWAYS.\" He drops into a crouch and draws in the dust with one finger. \"Flank them. Somebody stays on overwatch. "
     "And never, ever end your turn out of cover.\"\n\nYou point out that life doesn't have turns.\n\n\"That's what they WANT "
     "you to think.\" He taps the drawing. \"And name your soldiers after your friends. You fight harder to bring them home.\" "
     "A pause. \"It hurts more when you don't, though. I lost a whole squad of cousins once.\" Another pause. \"So I went back to "
     "the start of the day and did it again. Nobody needs to know.\"",
     [("\"Your secret's safe.\"", "root")])
node("scars",
     "\"These?\" He rolls up a sleeve proudly. \"Last winter I went into a crypt with a fever, a broken left leg and a terrible "
     "fear of the dark. All at once! I bandaged my bandages. I ate a raw mushroom to stay alive and it made me see colours "
     "for two days.\"\n\n\"I cleared the crypt, though.\" He beams. \"Mostly. Then I starved a bit. Then I found a sausage. "
     "Best sausage of my life.\"",
     [("\"That sounds awful.\"", "scars_fun")])
node("scars_fun", "\"It was WONDERFUL.\" He means it completely. \"I'd do it again tomorrow. I'm doing it again tomorrow, actually. "
                  "Different crypt.\"", [("\"Bring bandages.\"", "root")])
node("armour",
     "\"I made it!\" He knocks on his chainmail. \"I once woke up in the middle of a desert with nothing. No sword, no armour, "
     "not even trousers. I punched a rock until it turned into a pickaxe, then I punched a lot more rocks, and by the end of the "
     "week I had a fortress.\"\n\nA wistful sigh. \"It had a door that mostly worked and a cooking fire that set things on fire. "
     "I miss that fortress.\"",
     [("\"You punched a rock into a pickaxe?\"", "armour_rock")])
node("armour_rock", "\"Everyone can! You just have to believe in the rock.\" He says it with total confidence, and for a moment you almost "
                    "believe it too.", [("\"Noted.\"", "root")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ companion lines and banter
N = load("content/npcs/core_npcs.json")
du = next(n for n in N["npcs"] if n["id"] == "core:npc.dunstan")
c = du["companion"]


def add(group, texts):
    start = 1 + len([x for x in S if x.startswith(f"comp.dunstan.{group}.")]) + {
        "idle": len(c["idle_lines"]), "combat": len(c["combat_lines"]), "kill": len(c["kill_lines"])}[group]
    keys = []
    for i, t in enumerate(texts, start):
        text, cond = (t, {}) if isinstance(t, str) else t
        k = f"comp.dunstan.{group}.{i}"
        S[k] = text
        keys.append((k, cond))
    return keys


c["idle_lines"] += [dict({"text_key": k}, **cd) for k, cd in add("idle", [
    "Ninety-five percent chance to hit, and I missed. That's how I know it's a real fight.",
    "Never end your turn out of cover. I know we don't have turns. I still don't trust it.",
    "My leg aches. Probably broken. I'll bandage it later. I always bandage it later.",
    "If we ever get lost, I can build us a base. Give me some rocks and a weekend.",
    "I'm naming my next sword after you. Big Margaret won't mind. She's very secure."])]
c["combat_lines"] += [k for k, _ in add("combat", ["Flanking! I'm flanking!", "Overwatch! ...That means I'm waiting. Strategically."])]
c["kill_lines"] += [k for k, _ in add("kill", ["Ninety-five percent and it HIT! Write that down! Somebody write that down!"])]


def bant(bid, partner, convo):
    ls = []
    for i, (by, t) in enumerate(convo):
        k = f"comp.dunstan.banter.{bid}.{i}"
        S[k] = t
        ls.append({"by": "self" if by == "DUNSTAN" else "partner", "text_key": k})
    c["banter"].append({"id": f"dunstan_{bid}", "partner": P[partner], "lines": ls})


bant("desert", "coth", [("DUNSTAN", "Coth, I once woke up naked in the middle of a desert, with nothing at all."), ("COTH", "Paradise."),
                        ("DUNSTAN", "The first thing I did was make some trousers."), ("COTH", "...Rookie mistake.")])
bant("odds", "eranu", [("ERANU", "Ye look worried, lad."), ("DUNSTAN", "That beast only has a five percent chance to hit us."),
                       ("ERANU", "So we're fine."), ("DUNSTAN", "Eranu. I have seen what five percent can do.")])
bant("squad", "baggy", [("DUNSTAN", "Baggy, can I name a soldier after you?"), ("BAGGY", "What soldier?"),
                        ("DUNSTAN", "In my head. I command a squad in my head."), ("BAGGY", "...Is it a good squad?"),
                        ("DUNSTAN", "You're the sniper. You never miss."), ("BAGGY", "I'll take it. Don't tell anyone how I actually shoot.")])
save("content/npcs/core_npcs.json", N)
S["tip.51"] = "A 95% chance is not a promise. Ask Dunstan."

loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

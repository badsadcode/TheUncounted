"""Old Tobble by the well in Bellwether: an affectionate, unnamed nod to a certain beloved elder who asks you to stay
a while. Ours says "Stay a while, and hear me out!" and tells eight stories that go nowhere, in turn (the last one
starts the cycle again), forgetting every ending. Also builds the well he leans on. He.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
SP = "npc.old_tobble.name"
D = load("content/dialogue/chapter_zero_dialogue.json")
dl = {"id": "core:dialogue.old_tobble", "root_node": "root", "nodes": {}}
D["dialogues"].append(dl)


def node(nid, text, choices, actions=None):
    key = f"dlg.tobble.{nid}"
    S[key] = text
    n = {"speaker_key": SP, "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, ch in enumerate(choices):
        S[f"{key}.c{i}"] = ch[0]
        c = {"text_key": f"{key}.c{i}", "next": ch[1]}
        if len(ch) > 2: c.update(ch[2])
        n["choices"].append(c)
    dl["nodes"][nid] = n


STORIES = [
    "\"Did I ever tell you about the winter the river froze? Froze solid, it did. Whole village skated on it for a month. "
    "Then it thawed, and we realised it hadn't been the river at all. It had been Mrs. Pennyworth's washing, laid out to "
    "dry.\"\n\nHe nods gravely. \"Very large washing. Very cross Mrs. Pennyworth.\"",
    "\"When I was a lad, I had a goat called Duke. Duke could count to four. Not three. Not five. Four. Anything else, "
    "he'd just look at you.\"\n\n\"We entered him in the county fair, and he lost to a turnip. The turnip couldn't count "
    "at all.\" A long, bitter pause. \"Politics, that was.\"",
    "\"I once walked all the way to the edge of the world. It's just past Saltmere, second on the left. There's a fence. "
    "Somebody had put a sign on the fence. It said: 'NO.'\"\n\n\"So I came back.\" He taps his nose. \"Good sign, that. "
    "Clear.\"",
    "\"Long ago, before the Great Silence, before the Bureau, before soup, there lived a king who was afraid of Tuesdays. "
    "Every Monday night he'd go to bed and sleep straight through to Wednesday.\"\n\n\"Ruled for forty years. Never once "
    "saw a Tuesday.\" He leans in. \"Died on a Thursday. Of surprise.\"",
    "\"This well. You know why it's here? Neither do I. It was here when I came, and I came before the village.\"\n\n\"I "
    "asked it once. It said nothing. Wells are like that. Very discreet.\" He pats the stones. \"I tell it everything.\"",
    "\"There was a dragon, once, came to Bellwether demanding gold. We offered it a pie instead. It ate the pie, cried a "
    "little, and left.\"\n\n\"Never saw it again. Best pie Marta's grandmother ever made.\" He frowns. \"Or worst. Hard to "
    "tell, with dragons.\"",
    "\"Did you know I invented the chair? Before me, everybody just sort of hovered. Exhausting.\"\n\n\"I patented it, but "
    "the Bureau lost the form. So now everyone sits for free and I get nothing.\" He sighs. \"Sit down sometime. You'll "
    "feel it. That's guilt, that is. That's me.\"",
    "\"Once, I fought a skeleton for three days and three nights. On the fourth morning we both stopped, sat down, and "
    "realised we were cousins.\"\n\n\"Lovely fellow. Bit thin. We still write.\" A thoughtful pause. \"Well. I write. He "
    "mostly rattles.\"",
]
N = len(STORIES)
F = lambda i: f"tobble_story_{i}"

tell = []
for i in range(N):
    cond = [] if i == 0 else [{"type": "flag_set", "flag": F(i - 1)}]
    cond.append({"type": "flag_not_set", "flag": F(i)})
    tell.append(("\"Tell me a story.\"", f"story{i}", {"conditions": cond}))
node("root",
     "An old man in brown robes, more patch than robe, leans on the well as if it were an old friend. His hair has mostly "
     "left him; what remains is grey and has opinions. He sees you, and his whole face lights up.\n\n\"Stay a while, and "
     "hear me out!\"",
     tell + [("\"Who are you?\"", "who"), ("\"Do your stories have a point?\"", "point"), ("\"Not today.\"", "bye")])
for i, story in enumerate(STORIES):
    acts = [{"type": "set_flag", "flag": F(i), "value": True}]
    if i == N - 1:  # the last one: he starts again from the beginning next time
        acts = [{"type": "set_flag", "flag": F(k), "value": False} for k in range(N)]
    node(f"story{i}", story, [("\"...And then what?\"", "andthen"), ("\"Thank you, Tobble.\"", "thanks")], acts)
node("andthen", "\"And then?\" He thinks very hard. His eyebrows think too. Something deep in his beard thinks.\n\n\"...I've forgotten. "
                "Stay a while, and I'll tell you another!\"", [("\"Go on, then.\"", "root"), ("\"Maybe later.\"", "bye")])
node("thanks", "\"Thank YOU. Nobody ever stays a while any more. They're all off saving the world, or the village, or a horse.\" He "
               "settles back against the well, content. \"Come back tomorrow. I've a story about a turnip.\"",
     [("\"Another one now?\"", "root"), ("Leave.", "END")])
node("who", "\"Me? Old Tobble. I've been standing by this well since before it was a well. Before it was a hole, even. It was a "
            "sort of dent, then.\" He pats the stonework fondly. \"People come, people go. I stay a while. You should too.\"",
     [("\"I'll stay a while.\"", "root")])
node("point", "\"A point?\" He looks genuinely wounded. \"A story doesn't need a point. A story needs a beginning, a middle, and "
              "someone polite enough to stand there until it stops.\"\n\nHe beams at you. \"You're very polite.\"",
     [("\"Thank you?\"", "root")])
node("bye", "\"Not today? Ah, well. I'll be here. I'm always here.\" He waves cheerfully. \"Tomorrow you'll stay a while, and hear "
            "me out, and you'll thank me. Or you won't. Also fine.\"", [("Leave.", "END")])
save("content/dialogue/chapter_zero_dialogue.json", D)

NP = load("content/npcs/core_npcs.json")
barks = ["Stay a while, and hear me out...", "Did I ever tell you about the goat?", "Where was I? Ah, yes. The turnip.",
         "Stay a while! ...No? Another time, then."]
NP["npcs"].append({"id": "core:npc.old_tobble", "name_key": SP, "title_key": "npc.old_tobble.title", "faction": "core:faction.ashbound",
                   "dialogue_id": "core:dialogue.old_tobble",
                   "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/old_tobble.png",
                                  "animation_data": "assets/animations/npc_standard.json", "scale": 1.7},
                   "barks": [{"text_key": f"bark.old_tobble.{i}"} for i in range(1, len(barks) + 1)]})
save("content/npcs/core_npcs.json", NP)
for i, b in enumerate(barks, 1): S[f"bark.old_tobble.{i}"] = b
S[SP] = "Old Tobble"
S["npc.old_tobble.title"] = "Teller of Tales (Unverified)"
S["tip.52"] = "If an old man by the well asks you to stay a while, you may as well. The goat story is worth it."

# ---- the well (Bellwether square) and Tobble beside it
B = load("content/regions/bellwether.json")
STONE, WOOD, CRYPT = "assets/models/env/wall_stone.glb", "assets/models/env/floor_wood.glb", "assets/models/env/wall_crypt.glb"
wx, wz = 5.2, -2.8
def box(pid, model, cx, y0, cz, sx, sy, sz, solid=True, uv=None):
    B["props"].append({"id": pid, "model": model, "pos": [round(cx, 3), round(y0, 3), round(cz, 3)], "scale": [sx, sy, sz],
                       "solid": solid, "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})
box("well_ring", STONE, wx, 0.0, wz, 1.6, 0.85, 1.6, uv=[0.7, 0.35])
box("well_water", CRYPT, wx, 0.86, wz, 1.2, 0.02, 1.2, solid=False, uv=[0.4, 0.1])
box("well_post_w", WOOD, wx - 0.72, 0.85, wz, 0.14, 1.35, 0.14, uv=[0.1, 0.5])
box("well_post_e", WOOD, wx + 0.72, 0.85, wz, 0.14, 1.35, 0.14, uv=[0.1, 0.5])
box("well_beam", WOOD, wx, 2.1, wz, 1.6, 0.12, 0.14, solid=False, uv=[0.6, 0.1])
box("well_roof", WOOD, wx, 2.25, wz, 1.9, 0.08, 1.15, solid=False, uv=[0.7, 0.4])
B["npcs"].append({"instance_id": "npc_old_tobble", "npc_id": "core:npc.old_tobble", "pos": [wx + 1.25, 0.0, wz + 0.6], "yaw": 250.0})
save("content/regions/bellwether.json", B)

loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

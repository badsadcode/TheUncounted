"""Friends from Toasty's streams as NPCs and companions: Eranu (a brave, smart Scottish warrior), Coth (Cothfotmeoo: a
skinny castaway of a man with a heavy black beard and, as usual, no trousers; Eranu calls him her waifu, and
sometimes Cothepoo) and Dunstan (young, keen, with an enormous sword).

Side quest "Cothepoo, Come Home" (core:quest.cothepoo, Tales of Bellwether): Eranu waits in the Lantern Inn; Coth went
out three days ago "to find trousers" and is camped in the Whistling Wood, convinced he has been lost for a thousand
years. Convince him (Persuasion, or count his tally marks with him: Perception), then the reunion at the inn. After
that, Eranu and Coth can join the party; Dunstan can join any time (he's been waiting for someone to ask).

Pronouns: Eranu she, Coth he, Dunstan he.
ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q = "core:quest.cothepoo"
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
QA = lambda s: {"type": "quest_stage_at_least", "quest_id": Q, "stage": s}
QE = lambda s: {"type": "quest_stage_equals", "quest_id": Q, "stage": s}
QB = lambda s: {"type": "quest_stage_below", "quest_id": Q, "stage": s}
SETF = lambda f, v=True: {"type": "set_flag", "flag": f, "value": v}
STAGE = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}
ROOM, FULL = {"type": "party_has_room"}, {"type": "party_full"}

D = load("content/dialogue/chapter_zero_dialogue.json")


class Dlg:
    """Builds one dialogue. node(id, text, [(choice text, next, {conditions, actions, roll})], actions)."""
    def __init__(self, did, speaker, prefix):
        self.d = {"id": did, "root_node": "root", "nodes": {}}
        self.speaker, self.prefix = speaker, prefix
        D["dialogues"].append(self.d)

    def node(self, nid, text, choices, actions=None):
        key = f"{self.prefix}.{nid}"
        S[key] = text
        n = {"speaker_key": self.speaker, "text_key": key, "choices": []}
        if actions: n["actions"] = actions
        for i, ch in enumerate(choices):
            t, nx = ch[0], ch[1]
            opt = ch[2] if len(ch) > 2 else {}
            S[f"{key}.c{i}"] = t
            c = {"text_key": f"{key}.c{i}", "next": nx}
            c.update(opt)
            n["choices"].append(c)
        self.d["nodes"][nid] = n


# ============================================================================ Eranu
er = Dlg("core:dialogue.eranu", "npc.eranu.name", "dlg.eranu")
er.node("root",
        "A tall, broad-shouldered woman with a long blonde braid sits in the window seat: green kilt, a round targe propped beside her, "
        "a sword across her knees. She keeps one eye on you and the other on the door.\n\n\"Aye?\"",
        [("\"Who are you?\"", "who"),
         ("\"You look like you're waiting for someone.\"", "waiting", {"conditions": [QB(0)]}),
         ("\"No sign of Coth yet. Any advice?\"", "news", {"conditions": [QE(10)]}),
         ("\"I found Coth. He's here.\"", "reunion", {"conditions": [QE(20)]}),
         ("\"Why 'Cothepoo'?\"", "nickname", {"conditions": [QA(10)]}),
         ("\"Will you come adventuring with me?\"", "join", {"conditions": [QA(100), FN("eranu_following"), ROOM]}),
         ("\"Will you come adventuring with me?\"", "full", {"conditions": [QA(100), FN("eranu_following"), FULL]}),
         ("\"Wait here for a while, Eranu.\"", "wait", {"conditions": [FS("eranu_following")]}),
         ("Leave.", "END")])
er.node("who",
        "\"Eranu. From the Glens, up north, where the weather has opinions.\" She pats the sword. \"I hit things that need hitting and "
        "I read things that need reading. Folk round here are always surprised I do both. Then they're surprised again.\"",
        [("\"Noted.\"", "root")])
er.node("waiting",
        "\"I'm waiting for my waifu.\"\n\nShe says it with complete confidence, as if it's a word everyone knows.\n\n\"Coth. Tall, skinny, beard "
        "down to here, hair down to there. Usually no trousers. You'd remember him.\" A frown at the door. \"Three days ago he said he was "
        "going out to find some trousers. He's not come back. Coth doesn't find trousers. Trousers find Coth, and he runs.\"",
        [("\"I'll find him.\"", "accept", {"actions": [STAGE(10)]}),
         ("\"Your... waifu?\"", "waifu"),
         ("\"Sorry, I can't help right now.\"", "END")])
er.node("waifu",
        "\"Aye. My waifu.\" A long, level look, daring you to make something of it. \"He protests. He's wrong.\"\n\n\"So. Will you find him?\"",
        [("\"I'll find him.\"", "accept", {"actions": [STAGE(10)]}), ("\"Not right now.\"", "END")])
er.node("accept",
        "\"Good.\" She stands, and she's taller than you expected. \"He went west, into the Whistling Wood. He'll have made camp somewhere "
        "daft, he'll have made a friend out of something that isn't alive, and he'll have lost count of the days. He always loses count "
        "of the days.\"\n\n\"Bring him home. Tell him Eranu says come home, Cothepoo.\"",
        [("\"I'll bring him back.\"", "END")])
er.node("news",
        "\"West, in the Whistling Wood. Look for a camp somewhere daft, a wee fire, and a beard.\" Her grip tightens on the sword. "
        "\"And if he says it's been a thousand years, he's wrong. He'll have been counting something. Make him count it out loud.\"",
        [("\"I'll keep looking.\"", "END")])
er.node("nickname",
        "Eranu's mouth twitches.\n\n\"Because he's Coth, and because he's a wee poo sometimes.\" She shrugs. \"He hates it. That's how "
        "you know it's love.\"",
        [("\"Fair.\"", "root")])
er.node("reunion",
        "When the clapping dies down, Eranu presses something into your hands: a pair of trousers, neatly folded, never worn.\n\n\"His,\" "
        "she says. \"I've carried them since he left, for when we found him. He says he doesn't want them back.\"\n\nCoth, from behind "
        "her, through a mouthful of stew: \"I DON'T.\"\n\n\"And this, for your trouble.\" A heavy little purse. \"If you ever need a "
        "sword arm, or two, you know where the window seat is.\"",
        [("\"Glad he's home.\"", "END")],
        [{"type": "narrate", "pages": [{"key": "story.cothepoo.1"}, {"key": "story.cothepoo.2"}, {"key": "story.cothepoo.3"}]},
         STAGE(100), {"type": "give_item", "item_id": "core:item.trousers_of_coth", "qty": 1}, {"type": "give_gold", "amount": 80},
         {"type": "give_xp", "skill": "persuasion", "amount": 25}])
er.node("join",
        "Eranu picks up targe and sword in one easy movement.\n\n\"Aye, go on, then. Somebody has to keep you alive.\" A glance across "
        "the table. \"Don't wander off, Cothepoo.\"\n\nCoth, wounded: \"I have NEVER wandered.\"",
        [("\"Let's go.\"", "END")], [SETF("eranu_following"), {"type": "recruit_companion"}])
er.node("full", "\"You've a full party already. I'll not be the extra wheel on anyone's cart.\"", [("\"Another time.\"", "root")])
er.node("wait", "\"Aye. I'll be at the window.\" She heads back to her seat, and her eyes go straight to the door, out of habit.",
        [("Leave.", "END")], [SETF("eranu_following", False), {"type": "dismiss_companion"}])

# ============================================================================ Coth, the castaway (in the Whistling Wood)
cc = Dlg("core:dialogue.coth_castaway", "npc.coth.name", "dlg.coth_cast")
cc.node("root",
        "A skinny man sits by a tiny fire, staring into the middle distance. His black beard reaches his belt; his hair reaches further. "
        "He wears a ragged tunic and, below that, a great deal of leg. Beside him on a log, a round stone with a face painted on it "
        "sits as if it's part of the conversation.\n\nHe sees you, and his eyes fill with tears.\n\n\"A PERSON. A real one. Tell me, "
        "traveller: what year is it? I have been lost in these woods for a thousand years.\"",
        [("\"Are you Coth?\"", "coth"),
         ("\"It's been three days.\"", "three"),
         ("\"Who's your friend?\"", "rock"),
         ("\"Where are your trousers?\"", "trousers"),
         ("[Persuasion] \"Eranu sent me. She's waiting for you.\"", "home",
          {"conditions": [QA(10)], "roll": {"skill": "persuasion", "dc": 9, "fail_next": "not_yet"}}),
         ("[Perception] \"Those marks on the pine. Let's count them together.\"", "marks",
          {"conditions": [FS("coth_seen_tally")], "roll": {"skill": "perception", "dc": 8, "fail_next": "lost_count"}}),
         ("Leave him to it.", "END")])
cc.node("coth",
        "\"Coth. Cothfotmeoo, if we're being formal, and out here, a thousand years from anyone, I've had a lot of time to be formal.\" He "
        "gestures at the stone. \"Sir Pebbleton and I keep a very proper camp.\"",
        [("\"Of course you do.\"", "root")])
cc.node("three",
        "Coth laughs: a long, slightly unhinged laugh.\n\n\"Three DAYS? Look at this beard, stranger! Is this a three-day beard?\"\n\nYou "
        "look at the beard. It is enormous. It is also, you suspect, exactly the beard he left home with.",
        [("\"...Fair point.\"", "root")])
cc.node("rock",
        "\"Sir Pebbleton.\" Coth lowers his voice. \"He's been with me since the beginning. He doesn't say much, but when he does...\" A "
        "pause. \"He doesn't, actually. That's what I like about him.\"\n\nSir Pebbleton regards you with painted, unblinking eyes.",
        [("\"Hello, Sir Pebbleton.\"", "root")])
cc.node("trousers",
        "\"I set out to find trousers,\" Coth says, with great dignity. \"A thousand years ago. I have not found them. I've stopped "
        "looking. There comes a point where a man and his legs reach an understanding.\"\n\n\"Also, it's very freeing. Even in winter. "
        "ESPECIALLY in winter.\"",
        [("\"I'll take your word for it.\"", "root")])
cc.node("not_yet",
        "Coth strokes his beard thoughtfully and gazes past you into the trees.\n\n\"Nice try, stranger. But I know what I know, and what "
        "I know is: a thousand years. Sir Pebbleton agrees.\"\n\nSir Pebbleton says nothing, which Coth takes as agreement.",
        [("\"Hm.\"", "root")])
cc.node("lost_count",
        "You start counting. Coth joins in, loudly. Somewhere around forty he starts counting the gaps as well, then the knots in the bark, "
        "then Sir Pebbleton, twice.\n\n\"...a thousand and six,\" he finishes, triumphant. \"As I said.\"",
        [("\"Let's... try that again later.\"", "root")])
_go = ("\n\nHe picks up Sir Pebbleton, looks at him for a long moment, and sets him gently back on the log. \"He has a life here,\" he "
       "says. \"I won't take him from it.\"\n\n\"See you at the Lantern Inn, stranger from the future!\"")
cc.node("home",
        "The word 'Eranu' lands like a stone in a pond. Coth goes very still.\n\n\"Eranu? She... waited? A thousand years?\"\n\nThree days, "
        "you tell him.\n\nHe thinks about it. \"Felt like a thousand,\" he says at last, and stands, and kicks dirt over the fire. \"Right. "
        "Home, then. Before she comes looking. You do NOT want Eranu to come looking.\"" + _go,
        [("\"See you there.\"", "END")], [SETF("coth_home"), STAGE(20)])
cc.node("marks",
        "You count the marks together, out loud. Coth's voice gets quieter with every group of five.\n\n\"...seventy... seventy-one... "
        "seventy-two.\"\n\nSeventy-two. One for every hour. Coth looks at the pine, then at his fingers, then at Sir Pebbleton.\n\n"
        "\"That's three days,\" he says. \"That's only three days. But the beard...\"\n\nThe beard, you point out gently, was always like "
        "that.\n\n\"...It was always like this,\" Coth whispers. Then he brightens. \"Well! Eranu will be worried sick. Home, then!\"" + _go,
        [("\"See you there.\"", "END")], [SETF("coth_home"), STAGE(20)])

# ============================================================================ Coth, at home in the Lantern Inn
ch = Dlg("core:dialogue.coth", "npc.coth.name", "dlg.coth")
ch.node("root",
        "Coth sits next to Eranu's window seat, still without trousers, working through a bowl of stew with the focus of a man who has been "
        "away for a thousand years (three days).\n\n\"Ah! My rescuer from the future!\"",
        [("\"How does it feel to be back?\"", "settle"),
         ("\"So you're Eranu's waifu?\"", "waifu"),
         ("\"What happened to Sir Pebbleton?\"", "pebbleton"),
         ("\"Want to come adventuring?\"", "join", {"conditions": [QA(100), FN("coth_following"), ROOM]}),
         ("\"Want to come adventuring?\"", "full", {"conditions": [QA(100), FN("coth_following"), FULL]}),
         ("\"Stay here and finish your stew, Coth.\"", "wait", {"conditions": [FS("coth_following")]}),
         ("Leave.", "END")])
ch.node("settle",
        "\"Strange, being back. Everything's so... the same. Marta says the stew hasn't changed in a thousand years.\" A pause. \"She says "
        "three days. She's in on it too.\"",
        [("\"We all are.\"", "root")])
ch.node("waifu",
        "Coth opens his mouth to protest.\n\nAcross the table, Eranu raises one eyebrow by perhaps a millimetre.\n\nCoth closes his mouth. "
        "\"...Apparently,\" he says.",
        [("\"Congratulations.\"", "root")])
ch.node("pebbleton",
        "\"Still in the wood. Guarding the camp.\" Coth stares into his stew. \"I go out and visit him sometimes. We don't talk. We don't "
        "have to.\"",
        [("\"That's beautiful, Coth.\"", "root")])
ch.node("join",
        "Coth leaps up, scattering stew. \"An ADVENTURE? Out THERE? Where the trousers are?\" He considers this. \"I'll come. But I'm not "
        "wearing them.\"\n\nEranu, without looking up: \"Don't lose him.\"",
        [("\"Let's go.\"", "END")], [SETF("coth_following"), {"type": "recruit_companion"}])
ch.node("full", "\"Your party's full. I know how it is. I had a party once: me and Sir Pebbleton. He was the quiet one.\"",
        [("\"Another time.\"", "root")])
ch.node("wait", "\"Back to the stew, then.\" Coth sits down by Eranu, who slides the bowl back over to him without a word.",
        [("Leave.", "END")], [SETF("coth_following", False), {"type": "dismiss_companion"}])

# ============================================================================ Dunstan (Bellwether square)
du = Dlg("core:dialogue.dunstan", "npc.dunstan.name", "dlg.dunstan")
du.node("root",
        "A young man in a red cloak and polished mail is practising sword forms in the square. Or trying to. The sword is enormous: taller "
        "than he is, broad as a door, and every swing carries him half a step after it.\n\nHe spots you, plants the sword point-first in "
        "the cobbles (it stays there; the cobbles will never be the same) and straightens up.\n\n\"Hello! Are you an adventurer? You look "
        "like an adventurer.\"",
        [("\"That's a big sword.\"", "sword"),
         ("\"Who are you?\"", "who"),
         ("\"Can you actually lift that?\"", "lift"),
         ("\"Want to come adventuring with me?\"", "join", {"conditions": [FN("dunstan_following"), ROOM]}),
         ("\"Want to come adventuring with me?\"", "full", {"conditions": [FN("dunstan_following"), FULL]}),
         ("\"Wait here and practise, Dunstan.\"", "wait", {"conditions": [FS("dunstan_following")]}),
         ("Leave.", "END")])
du.node("sword",
        "\"Isn't it?\" Dunstan beams at it. \"It was my grandfather's. And his grandfather's. None of them could lift it either. It's a "
        "family tradition.\"\n\n\"I call her Big Margaret.\"",
        [("\"Hello, Big Margaret.\"", "root")])
du.node("who",
        "\"Dunstan! Squire. Well, nearly a squire. I applied. They said come back when I can lift the sword.\" He looks at the sword. The "
        "sword looks back. \"So I've been practising. Every day. For a year. I'm SO much better at falling over than I was.\"",
        [("\"That's a kind of progress.\"", "root")])
du.node("lift",
        "\"Absolutely. Watch.\"\n\nDunstan grips the hilt, sets his feet, and heaves. Big Margaret rises magnificently into the air, "
        "hangs there for a long, heroic moment, and comes down exactly where she was, taking Dunstan with her.\n\n\"...Up is easy,\" he says "
        "from the ground. \"It's the rest of it.\"",
        [("\"Need a hand up?\"", "root")])
du.node("join",
        "Dunstan's face lights up like a festival.\n\n\"REALLY? An actual adventure? With monsters?\" He wrenches Big Margaret out of the "
        "cobbles on the third try. \"I won't let you down! I might let HER down, now and then. On things. On monsters, mostly. That's "
        "the plan.\"",
        [("\"Glad to have you, Dunstan.\"", "END")], [SETF("dunstan_following"), {"type": "recruit_companion"}])
du.node("full", "\"Oh. You've got a full party.\" He tries very hard to look like he doesn't mind. \"Next time! I'll keep practising!\"",
        [("\"Next time.\"", "root")])
du.node("wait", "\"Right! I'll practise!\" Dunstan drags Big Margaret back to the middle of the square, leaving a long groove in the cobbles.",
        [("Leave.", "END")], [SETF("dunstan_following", False), {"type": "dismiss_companion"}])
save("content/dialogue/chapter_zero_dialogue.json", D)

S.update({
    "story.cothepoo.1": "The door of the Lantern Inn bangs open. Coth stands in the doorway: hair wild, beard magnificent, legs entirely out "
                        "in the open air.\n\n\"I HAVE RETURNED,\" he announces, \"AFTER A THOUSAND YEARS.\"",
    "story.cothepoo.2": "Eranu crosses the inn in four strides. For a moment it looks like she might hit him.\n\nShe hugs him instead, hard "
                        "enough to lift him off the floor.\n\n\"COTHEPOO. Three days, ya numpty. Three DAYS.\"",
    "story.cothepoo.3": "\"Felt like a thousand,\" Coth says, muffled, into her shoulder.\n\n\"Aye,\" says Eranu, more quietly. \"It did.\"\n\n"
                        "Marta puts two bowls of stew on the table without being asked. Somebody by the fire starts a slow clap. It "
                        "catches on.",
})

# ============================================================================ companions
ZONES = ["bellwether", "old_road", "annex", "vault_three", "seal_chamber", "hollowmere", "hollowmere_manor", "saltmere",
         "sunken_chapel", "whistling_wood", "sleepers_reef", "here", "here_archive"]
P = {"eranu": "core:npc.eranu", "coth": "core:npc.coth", "dunstan": "core:npc.dunstan", "baggy": "core:npc.detective_baggy",
     "kaelen": "core:npc.ashbound_scout", "grout": "core:npc.grout", "snacks": "core:npc.figure_snacks"}


def companion(who, stats, idle, combat, kill, heal, level, catchup, zones, banter):
    def lines(group, items):
        out = []
        for i, it in enumerate(items, 1):
            text, cond = (it, {}) if isinstance(it, str) else it
            k = f"comp.{who}.{group}.{i}"
            S[k] = text
            out.append((k, cond))
        return out
    c = dict(stats)
    c["zone_lines"] = {}
    for z in ZONES:
        S[f"comp.{who}.zone.{z}"] = zones[z]
        c["zone_lines"][z] = f"comp.{who}.zone.{z}"
    c["idle_lines"] = [dict({"text_key": k}, **cd) for k, cd in lines("idle", idle)]
    for g, items in (("combat", combat), ("kill", kill), ("heal", heal), ("level", level), ("catchup", catchup)):
        c[f"{g}_lines"] = [k for k, _ in lines(g, items)]
    c["banter"] = []
    for bid, partner, convo in banter:
        ls = []
        for i, (by, t) in enumerate(convo):
            k = f"comp.{who}.banter.{bid}.{i}"
            S[k] = t
            ls.append({"by": "self" if by == who.upper() else "partner", "text_key": k})
        c["banter"].append({"id": f"{who}_{bid}", "partner": P[partner], "lines": ls})
    return c


ERANU = companion("eranu", {"damage": 10, "attack_time": 1.05, "reach": 1.9, "heal_amount": 18, "heal_cooldown": 50},
    idle=["Keep your guard up. No, higher. Aye, that's it.",
          "Back home, this would count as a nice day. Back home, the rain comes sideways.",
          "I read once that this road was built by a king who wanted to see the sea. He never did. The road did.",
          "If anything jumps out at us, you go left, I go through it.",
          ("Cothepoo, stop licking that mushroom.", {"flag": "coth_following"}),
          ("Dunstan, lift with your legs. Your LEGS, lad.", {"flag": "dunstan_following"}),
          ("Baggy, you've had that magnifying glass on my boots for a full minute.", {"flag": "baggy_following"})],
    combat=["Come on, then!", "Behind the shield!", "Is that all you've got?", "For the Glens!"],
    kill=["Next.", "Aye. Stay down.", "That's for Cothepoo, whatever you did to him.", "Tidy."],
    heal=["Here. Drink this and stop bleeding on my kilt.", "Hold still. Ma's recipe: oats, honey, and a bit of shouting.",
          "You're no use to me dead. Get that down you."],
    level=["Look at you! Stronger already.", "Aye, you're getting the hang of it."],
    catchup=["There you are. Don't run off like that, you're worse than Coth.", "Right behind you. Always."],
    zones={"bellwether": "Bellwether. Small, but they keep a good fire at the Lantern.",
           "old_road": "Old roads remember who walked them. Let's give this one something good to remember.",
           "annex": "Records. Filing cabinets. I've fought worse. Not much worse.",
           "vault_three": "Smells like a tomb, because it is one. Shield up.",
           "seal_chamber": "Whatever's down here, it's not getting past me.",
           "hollowmere": "Fine old house. Shame about the haunting.",
           "hollowmere_manor": "Mind the stairs. Mind the portraits. Mind everything, really.",
           "saltmere": "Sea air! Proper air. Reminds me of home, except home's colder and the fish argue back.",
           "sunken_chapel": "Underwater church. Aye, nothing sinister about that at all.",
           "whistling_wood": "This is where I'd have found Cothepoo myself, if I'd trusted my own nose.",
           "sleepers_reef": "Out past the fog. Steady. I've sailed in worse.",
           "here": "A city nobody remembers. I'll remember it. That's a start.",
           "here_archive": "Books with teeth. I've read some like that."},
    banter=[("waifu", "coth", [("ERANU", "Cothepoo, tell them what you are."), ("COTH", "A free man of the wilds."),
                                 ("ERANU", "Tell them what you ARE."), ("COTH", "...Your waifu."), ("ERANU", "There we go.")]),
            ("trousers", "coth", [("COTH", "It's getting cold."), ("ERANU", "You know what helps with the cold, Coth?"),
                                  ("COTH", "Don't say it."), ("ERANU", "Trousers."), ("COTH", "Never.")]),
            ("thousand", "coth", [("ERANU", "Promise me you'll not go missing for a thousand years again."),
                                  ("COTH", "I promise."), ("ERANU", "Three days, even."), ("COTH", "...I'll try for two.")]),
            ("squire", "dunstan", [("ERANU", "Your stance is good, Dunstan. Your sword's daft."), ("DUNSTAN", "It's a family sword!"),
                                   ("ERANU", "It's a family of daft swords.")]),
            ("detective", "baggy", [("BAGGY", "Eranu, may I ask you a few questions?"), ("ERANU", "You may ask."),
                                    ("BAGGY", "Where were you on the night of-"), ("ERANU", "Asleep. With my sword. Next question."),
                                    ("BAGGY", "...That's all, actually.")]),
            ("statue", "grout", [("ERANU", "You're a fine bit of stonework, Grout."), ("GROUT", "I know."), ("ERANU", "Modest, too."),
                                 ("GROUT", "No.")])])

COTH = companion("coth", {"damage": 9, "attack_time": 0.85, "reach": 1.7, "heal_amount": 14, "heal_cooldown": 55},
    idle=["When I was lost, I ate bark for a thousand years. Three days. It was a long three days.",
          "Feel that breeze? You don't, do you. Trousers. They're holding you back.",
          "Sir Pebbleton would love this view.",
          "I counted the trees in this wood once. I got to seventy-two. Then I counted the hours. Also seventy-two. Spooky.",
          "Is it winter yet? I'm ready for winter. My legs are ready for winter.",
          ("Eranu is looking at me. I can feel Eranu looking at me.", {"flag": "eranu_following"}),
          ("Dunstan, if you ever want to give up trousers, I'll show you the way.", {"flag": "dunstan_following"})],
    combat=["AAAAAA!", "Have at you, foul creature!", "Not the legs! Anything but the legs!", "A thousand years of rage!"],
    kill=["Sir Pebbleton would be proud.", "Hah! Barefoot and victorious!", "Another one for the tally!"],
    heal=["Here. Bark tea. It's mostly bark. It works, though.", "Chew this root. Don't ask what it is. I don't know either.",
          "Have my emergency stew. I keep it in my beard."],
    level=["You've grown! A thousand years of growth in a day!", "You're glowing. Is that power, or the sun? Either way, nice."],
    catchup=["Wait for me! I've been lost before, I don't recommend it!", "Found you! I'm getting better at finding things. Not trousers."],
    zones={"bellwether": "Home! Marta! Stew! The window seat!",
           "old_road": "This road goes on for a thousand years. Or about an afternoon.",
           "annex": "So many forms. So few of them ask about trousers. Good.",
           "vault_three": "Cold down here. Wonderful. My legs feel alive.",
           "seal_chamber": "I don't like this room. Even Sir Pebbleton wouldn't like this room.",
           "hollowmere": "Haunted house. I once lived in a haunted wood. For a thousand years.",
           "hollowmere_manor": "Fancy. Do you think the ghosts wear trousers? I bet they don't.",
           "saltmere": "The sea! I could live on a beach. Just me and a rock with a face.",
           "sunken_chapel": "Wet. Everything is wet. I'm used to wet.",
           "whistling_wood": "My old camp is near here. Sir Pebbleton's still there, keeping watch. Hello, Sir Pebbleton!",
           "sleepers_reef": "An island! I've been practising for this my whole life. Well, three days of it.",
           "here": "A forgotten city. I know how it feels. I was forgotten for a thousand years. Three days.",
           "here_archive": "Whatever ate this city's name, it had better not try my legs."},
    banter=[("bark", "eranu", [("COTH", "Eranu, did you know bark is edible?"), ("ERANU", "No, Coth."), ("COTH", "Neither is it, really."),
                               ("ERANU", "Did you eat bark, Coth?"), ("COTH", "...For a thousand years.")]),
            ("legs", "dunstan", [("DUNSTAN", "Coth, aren't your legs cold?"), ("COTH", "Dunstan, my legs have seen things."),
                                 ("DUNSTAN", "What things?"), ("COTH", "Winter. Several. Proudly.")]),
            ("castaway", "baggy", [("BAGGY", "So you were missing for three days and thought it was a thousand years?"),
                                   ("COTH", "And you were a detective for three days and thought you were good at it?"),
                                   ("BAGGY", "...That's fair. Truce?"), ("COTH", "Truce.")]),
            ("rocks", "grout", [("COTH", "Grout, I once had a friend a lot like you."), ("GROUT", "Stone?"), ("COTH", "Sir Pebbleton."),
                                ("GROUT", "Good name."), ("COTH", "He was a good rock."), ("GROUT", "We all are.")]),
            ("snacks", "snacks", [("COTH", "Snacks! A fellow creature of the wild!"), ("SNACKS", "Hrrr-oo?"),
                                  ("COTH", "You don't wear trousers either!"), ("SNACKS", "(Snacks looks down at itself, then at Coth, and hoots with approval.)")])])

DUNSTAN = companion("dunstan", {"damage": 15, "attack_time": 1.9, "reach": 2.3, "heal_amount": 12, "heal_cooldown": 60},
    idle=["Big Margaret's getting lighter. Or I'm getting stronger. Or I've stopped feeling my arms.",
          "Do you think the squires would let me in now? I've been on an ACTUAL adventure.",
          "My grandfather fought a troll with this sword. Well, he dropped it on the troll. It counts.",
          "I'm going to write all this down. Dear Diary, today I swung the sword and it mostly went where I wanted.",
          "Is it bad that I'm having the best time?",
          ("Coth, please, I'm begging you, at least a kilt. Eranu wears a kilt.", {"flag": "coth_following"}),
          ("Eranu showed me how to stand. I'm standing SO much better now.", {"flag": "eranu_following"})],
    combat=["For Big Margaret!", "Stand back! I don't know where this is going to land!", "Here she comes!", "Hyaaah!"],
    kill=["I DID IT! Did you see that? I did it!", "Sorry! Sorry. No, actually, you had it coming.",
          "Big Margaret, you beautiful brick!"],
    heal=["Here! My mum packed me bandages. She packed me a LOT of bandages.", "Have a ration bar! It's mostly oats and hope.",
          "Hold on! I've got a potion. I think it's a potion. It's purple."],
    level=["You're getting so strong! Can you lift Big Margaret? No? Same.", "Look at you go! Teach me that!"],
    catchup=["Wait up! Big Margaret doesn't run!", "Here! Sorry! She got stuck on a door again."],
    zones={"bellwether": "Home square! I've left grooves in every cobble here.",
           "old_road": "An actual road to an actual adventure! Big Margaret, we're on our way!",
           "annex": "The ceilings are very low for a sword this size. I'll be careful. Ish.",
           "vault_three": "A crypt! Like in the stories! Is it bad that I'm excited?",
           "seal_chamber": "Okay. Okay. This one's scary. Big Margaret, be brave for both of us.",
           "hollowmere": "A haunted house. I've always wanted to swing a sword at a ghost.",
           "hollowmere_manor": "Lots of fragile things in here. I'll keep Big Margaret very, very still.",
           "saltmere": "Boats! Could Big Margaret sink a boat? Don't answer that.",
           "sunken_chapel": "If I drop her in here, she's gone forever. I'm holding on so tight.",
           "whistling_wood": "Wolves! Badgers! Big Margaret was MADE for this!",
           "sleepers_reef": "Sea monsters. My grandfather never fought a sea monster. I'm going to be the first!",
           "here": "A forgotten city. I'll make sure they remember us. Big Margaret is very memorable.",
           "here_archive": "Books that bite? Big Margaret bites back."},
    banter=[("stance", "eranu", [("DUNSTAN", "Eranu, how do you swing your sword so fast?"), ("ERANU", "It's a normal-sized sword, Dunstan."),
                                  ("DUNSTAN", "Oh."), ("ERANU", "That's the whole secret.")]),
            ("kilt", "coth", [("DUNSTAN", "Coth, you could just borrow some of my trousers."), ("COTH", "Dunstan."),
                              ("DUNSTAN", "Yes?"), ("COTH", "No.")]),
            ("squires", "kaelen", [("DUNSTAN", "Kaelen, do the Ashbound take squires?"), ("KAELEN", "We take anyone who can keep up."),
                                   ("DUNSTAN", "I can keep up!"), ("KAELEN", "With the sword?"), ("DUNSTAN", "...Mostly.")]),
            ("case", "baggy", [("BAGGY", "Dunstan, that sword is the biggest piece of evidence I've ever seen."), ("DUNSTAN", "Evidence of what?"),
                               ("BAGGY", "Of a family that never learned."), ("DUNSTAN", "That's... actually fair.")]),
            ("lift", "grout", [("DUNSTAN", "Grout, could you lift Big Margaret?"), ("GROUT", "Yes."), ("DUNSTAN", "Could you show me how?"),
                               ("GROUT", "Be made of stone."), ("DUNSTAN", "I'll work on it!")])])

# ============================================================================ NPC definitions
N = load("content/npcs/core_npcs.json")
def npc(nid, name, title, dlg, sheet, comp=None, barks=()):
    n = {"id": f"core:npc.{nid}", "name_key": f"npc.{nid}.name", "title_key": f"npc.{nid}.title", "faction": "core:faction.ashbound",
         "dialogue_id": dlg, "appearance": {"type": "sprite_8dir", "sprite_sheet": sheet, "animation_data": "assets/animations/npc_standard.json",
                                            "scale": 1.8}, "barks": []}
    for i, b in enumerate(barks, 1):
        text, cond = (b, {}) if isinstance(b, str) else b
        S[f"bark.{nid}.{i}"] = text
        n["barks"].append(dict({"text_key": f"bark.{nid}.{i}"}, **cond))
    if comp: n["companion"] = comp
    N["npcs"].append(n)
    S[f"npc.{nid}.name"], S[f"npc.{nid}.title"] = name, title
npc("eranu", "Eranu", "Shieldmaiden of the Glens", "core:dialogue.eranu", "assets/sprites/npcs/friend_eranu.png", ERANU,
    [("Three days. Three DAYS.", {"not_flag": "coth_home"}), ("Have you seen a man with no trousers? You'd know.", {"not_flag": "coth_home"}),
     ("Aye, he's back. Don't tell him I was worried.", {"flag": "coth_home"})])
npc("coth_castaway", "Coth", "Lost for a Thousand Years (Three Days)", "core:dialogue.coth_castaway", "assets/sprites/npcs/friend_coth.png",
    None, ["A thousand years... a thousand years...", "Sir Pebbleton, we have a visitor!"])
S["npc.coth.name"] = "Coth"
npc("coth", "Coth", "Eranu's Waifu (Disputed, by Coth)", "core:dialogue.coth", "assets/sprites/npcs/friend_coth.png", COTH,
    ["The stew hasn't changed in a thousand years.", "Trousers? Never heard of them."])
npc("dunstan", "Dunstan", "Nearly a Squire", "core:dialogue.dunstan", "assets/sprites/npcs/friend_dunstan.png", DUNSTAN,
    ["Hyah! ...Ow.", "Up is easy. It's the rest of it.", "Big Margaret, please. People are watching."])
save("content/npcs/core_npcs.json", N)

# ============================================================================ the trousers
A = load("content/items/armor_and_gear.json")
A["items"].append({"id": "core:item.trousers_of_coth", "name_key": "item.trousers_of_coth.name", "description_key": "item.trousers_of_coth.description",
                   "category": "armor", "icon": "assets/ui/items/trousers_of_coth.png", "world_model": "assets/models/items/traveler_boots.glb",
                   "slots": ["legs"], "value": 120, "weight": 1.0, "armor": 3,
                   "effects": [{"type": "stat_bonus", "stat": "endurance", "amount": 1}, {"type": "stat_bonus", "stat": "agility", "amount": 1}]})
S["item.trousers_of_coth.name"] = "The Trousers of Coth"
S["item.trousers_of_coth.description"] = ("Sturdy, warm, beautifully stitched, and never once worn by their owner, who refuses to take them back. "
                                          "Eranu carried them for three days, just in case. Comfortable in winter, which is more than Coth can say.")
save("content/items/armor_and_gear.json", A)

# ============================================================================ the quest
QD = load("content/quests/chapter_zero_quests.json")
QD["quests"].append({"id": Q, "title_key": "quest.cothepoo.title", "summary_key": "quest.cothepoo.summary", "campaign": "tales_of_bellwether",
                     "stages": [{"stage": 10, "objective_key": "quest.cothepoo.stage10", "journal_key": "quest.cothepoo.journal10",
                                 "markers": ["npc_coth_wood", "coth_tally"]},
                                {"stage": 20, "objective_key": "quest.cothepoo.stage20", "journal_key": "quest.cothepoo.journal20",
                                 "markers": ["npc_eranu"]},
                                {"stage": 100, "objective_key": "quest.cothepoo.stage100", "journal_key": "quest.cothepoo.journal100",
                                 "completed": True}]})
save("content/quests/chapter_zero_quests.json", QD)
S.update({
    "quest.cothepoo.title": "Cothepoo, Come Home",
    "quest.cothepoo.summary": "Eranu's waifu went out to find trousers three days ago and hasn't come back.",
    "quest.cothepoo.stage10": "Find Coth in the Whistling Wood",
    "quest.cothepoo.journal10": "Eranu, in the Lantern Inn, is waiting for Coth: tall, skinny, long hair, a heavy black beard, usually no "
                                "trousers. He went west into the Whistling Wood three days ago, 'to find trousers'. He'll have lost count "
                                "of the days. Eranu says: make him count it out loud.",
    "quest.cothepoo.stage20": "Return to Eranu at the Lantern Inn",
    "quest.cothepoo.journal20": "Found Coth camped in the wood with a rock called Sir Pebbleton, sure he'd been lost for a thousand years. "
                                "He's on his way home. Eranu will want to know.",
    "quest.cothepoo.stage100": "Coth is home",
    "quest.cothepoo.journal100": "Coth came home after a thousand years (three days). Eranu gave me his trousers, which he refuses to take "
                                 "back. Both of them would come adventuring now, if I asked.",
    "tip.49": "Eranu in the Lantern Inn is waiting for someone. Dunstan in the square is waiting for someone to ask him along.",
})

# ============================================================================ placement: Bellwether (Lantern Inn, the square)
B = load("content/regions/bellwether.json")
B["npcs"] += [
    {"instance_id": "npc_eranu", "npc_id": "core:npc.eranu", "pos": [-9.4, 0.0, 8.4], "yaw": 150.0},
    {"instance_id": "npc_coth_inn", "npc_id": "core:npc.coth", "pos": [-8.7, 0.0, 10.3], "yaw": 130.0, "requires_flag": "coth_home"},
    {"instance_id": "npc_dunstan", "npc_id": "core:npc.dunstan", "pos": [-3.2, 0.0, 3.4], "yaw": 30.0},
]
save("content/regions/bellwether.json", B)

# ============================================================================ placement: Coth's camp (Whistling Wood, south-west)
block = '''# ============================================================================ Coth's camp (tools/authoring/friends.py)
props.append({"id": "coth_fire", "model": "assets/models/props/fire_embers_small.glb", "pos": [-14.6, 0.0, 15.4], "scale": [1, 1, 1], "solid": False})
for i, (dx, dz) in enumerate([(0.45, 0), (-0.45, 0), (0, 0.45), (0, -0.45), (0.32, 0.32), (-0.32, -0.32)]):
    props.append({"id": f"coth_fire_stone{i}", "model": STONE, "pos": [-14.6 + dx, 0.0, 15.4 + dz], "scale": [0.22, 0.18, 0.22],
                  "solid": False, "uv_scale": [0.2, 0.1]})
props.append({"id": "coth_log", "model": WOOD, "pos": [-15.9, 0.0, 15.2], "rot_y": 80.0, "scale": [1.8, 0.32, 0.42], "solid": False, "uv_scale": [0.8, 0.2]})
props.append({"id": "coth_lean_to", "model": "assets/models/props/branches_ash.glb", "pos": [-16.6, 0.0, 16.8], "rot_y": 30.0, "scale": [2.2, 1.6, 2.2],
              "solid": False})
props.append({"id": "coth_bed", "model": GRASS, "pos": [-16.0, 0.0, 17.2], "rot_y": 30.0, "scale": [1.9, 0.08, 0.9], "solid": False, "uv_scale": [0.7, 0.3]})
props.append({"id": "sir_pebbleton", "model": "assets/models/props/ore_iron.glb", "pos": [-15.9, 0.3, 14.7], "rot_y": 200.0, "scale": [0.45, 0.45, 0.45], "solid": False})
npcs.append({"instance_id": "npc_coth_wood", "npc_id": "core:npc.coth_castaway", "pos": [-15.4, 0.0, 15.9], "yaw": 120.0, "hidden_flag": "coth_home"})
interactables.append({"instance_id": "sir_pebbleton_note", "type": "readable", "model": "", "pos": [-15.9, 0.3, 14.6], "rot_y": 0.0,
                      "prompt": "Look at the Stone", "title": "Sir Pebbleton",
                      "text": "A round grey stone with a face painted on it in berry juice: two dots, and a mouth that has decided to be "
                              "patient about things. Someone has given it a little moss hat.\\n\\nIt is, somehow, the most dignified thing in the wood."})
interactables.append({"instance_id": "coth_tally", "type": "readable", "model": "", "pos": [-15.6, 0.0, 18.7], "rot_y": 0.0,
                      "prompt": "Look at the Marks on the Pine", "title": "Marks on a Pine", "set_flag": "coth_seen_tally",
                      "text": "Somebody has scratched rows of marks into the bark, in tidy groups of five, under a heading carved in big letters:\\n\\n"
                              "DAYS LOST\\n\\nUnderneath, smaller: (hours?)\\nSmaller still: (no. days.)\\nTiny, near the roots: (maybe hours.)\\n\\n"
                              "There are a lot of marks. You could count them. Ideally with whoever made them."})

'''
src = open("tools/build_wood.py").read()
assert "region = {" in src and "GRASS" in src and "STONE" in src
open("tools/build_wood.py", "w").write(src.replace("region = {", block + "region = {", 1))

loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

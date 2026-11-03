"""Dungeons & Debtors II: The Lich Who Forgot to File. Oakhaven's second tabletop campaign (four sessions).

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends.
Same table as the first campaign, plus two new players: Sabrino (a wizard also called Sabrino) and Kaelen (the
party chronicler, who opens every session with a recap). Written to be read aloud, with voices."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
QE = lambda q, s: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda q, s: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda q, s: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FL = lambda fl, v: {"type": "flags_at_least", "flags": fl, "value": v}
FF = lambda fl, v: {"type": "flags_fewer_than", "flags": fl, "value": v}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
XP = lambda k, a: {"type": "give_xp", "skill": k, "amount": a}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
GG = lambda a: {"type": "give_gold", "amount": a}
SQ = lambda q, s: {"type": "set_quest_stage", "quest_id": q, "stage": s}

FIRST_DONE = "core:quest.dnd_session3"
L1, L2, L3, L4 = ("core:quest.lich_s1", "core:quest.lich_s2", "core:quest.lich_s3", "core:quest.lich_s4")
WINS = [f"lich_win_{i}" for i in range(1, 9)]
GM, KAELEN = "npc.clerk_oakhaven.name", "npc.ashbound_scout.name"


class Dlg:
    def __init__(self, prefix, nodes):
        self.prefix, self.nodes = prefix, nodes

    def node(self, nid, text, choices, actions=None, speaker=GM):
        key = f"{self.prefix}.{nid}"
        S[key] = text
        n = {"speaker_key": speaker, "text_key": key}
        if actions:
            n["actions"] = actions
        out = []
        for i, c in enumerate(choices):
            ck = f"{key}.c{i}"
            S[ck] = c[0]
            d = {"text_key": ck, "next": c[1]}
            for k, v in (c[2] if len(c) > 2 else {}).items():
                d[k] = v
            out.append(d)
        n["choices"] = out
        self.nodes[nid] = n


def C(text, nxt, cond=None, actions=None, roll=None):
    o = {}
    if cond: o["conditions"] = cond
    if actions: o["actions"] = actions
    if roll: o["roll"] = roll
    return (text, nxt, o)


D = load("content/dialogue/chapter_zero_dialogue.json")
clerk = {d["id"]: d for d in D["dialogues"]}["core:dialogue.clerk_oakhaven"]["nodes"]
g = Dlg("dlg.lich", clerk)

topics = [
    ("dlg.lich.topic.s1", '"Is it Thursday? Is the new campaign starting?"', [QA(FIRST_DONE, 100), QB(L1, 100)], "l1_start"),
    ("dlg.lich.topic.s2", '"Game night! Back to the Underdark."', [QE(L1, 100), QB(L2, 100)], "l2_start"),
    ("dlg.lich.topic.s3", '"Tonight\'s the heist, Game Master."', [QE(L2, 100), QB(L3, 100)], "l3_start"),
    ("dlg.lich.topic.s4", '"The final session. Let\'s meet the Lich."', [QE(L3, 100), QB(L4, 100)], "l4_start"),
    ("dlg.lich.topic.after", '"How was the holiday, Oakhaven?"', [QA(L4, 100)], "l_after"),
]
ch = clerk["greeting"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
new = []
for key, text, cond, nxt in topics:
    S[key] = text
    new.append({"text_key": key, "conditions": cond, "next": nxt})
clerk["greeting"]["choices"] = ch[:idx] + new + ch[idx:]

# ======================================================================= SESSION ONE: THE DESCENT
g.node("l1_start",
    "Thursday. The back table of the Lantern Inn has grown. Somebody has pushed a second table against the first. Marta's "
    "teapot has been replaced with a larger teapot. And there are two new chairs.\n\n"
    "In one sits Sabrino, hat off for once, with a stack of character sheets, all of them for wizards.\n\n"
    "In the other sits Kaelen, journal open, quill ready. \"I'm not playing,\" Kaelen says. \"I'm chronicling. Somebody "
    "should write down what happens at this table. It's important.\"\n\n"
    "Oakhaven sets down a new dragon screen, painted with skulls, filing cabinets and a single elegant quill.\n\n"
    "OAKHAVEN (GM): \"Welcome back, adventurers. Your characters are now level five. This is Campaign Two. It is called... "
    "THE LICH WHO FORGOT TO FILE.\"",
    [C('"A lich? What did he forget to file?"', "l1_lore"),
     C('"Sabrino, what are you playing?"', "l1_sabrino")])
g.node("l1_sabrino",
    "SABRINO: \"A wizard.\"\n\nOAKHAVEN (GM): \"What is your wizard's name?\"\n\nSABRINO: \"Sabrino.\"\n\n"
    "OAKHAVEN (GM): \"Your character cannot have the same name as you.\"\n\nSABRINO: \"Sabrino the Second. The FIRST Sabrino "
    "is the MOTHER. Also a wizard. Also called Sabrino. It is a family of wizards called Sabrino.\"\n\n"
    "OAKHAVEN (GM, writing it down with the expression of a man choosing his battles): \"...Fine. What spells does Sabrino "
    "the Second know?\"\n\nSABRINO: \"Fireball.\"\n\nOAKHAVEN (GM): \"And?\"\n\nSABRINO: \"A bigger Fireball.\"",
    [C('"So. This lich."', "l1_lore")])
g.node("l1_lore",
    "Oakhaven lowers his voice. The candles on the table seem to dim of their own accord. (Marta is turning them down.)\n\n"
    "OAKHAVEN (GM): \"Six hundred years ago, in the Underdark city of Inkwell, there lived an Archchancellor named Vellum "
    "Dreadquill. The greatest administrator who ever lived. He filed every form in the city. Every permit. Every receipt.\"\n\n"
    "\"Every form... except one.\"\n\n"
    "\"His own tax return. Due on the first of the month. And rather than face the deadline, Vellum Dreadquill performed "
    "the darkest ritual known to clerkdom, and became... a LICH. Undying. Unfiling. Six hundred years overdue.\"\n\n"
    "ROLF (genuinely horrified): \"Six hundred years of late fees.\"\n\n"
    "OAKHAVEN (GM): \"Your quest is to descend into the Underdark, find his phylactery, and bring Vellum Dreadquill to... "
    "justice.\"",
    [C('"Before we start, Kaelen, can we have a recap of last campaign?"', "l1_recap_win", [FS("dnd_dragon_down")]),
     C('"Before we start, Kaelen, can we have a recap of last campaign?"', "l1_recap_friend", [FN("dnd_dragon_down")])])
recap_tail = ("\n\nKaelen closes the journal. The whole table applauds. Hollis, in a small voice, says \"That was good.\"\n\n"
              "OAKHAVEN (GM, visibly moved, pretending he isn't): \"...Thank you, Kaelen. We descend.\"")
g.node("l1_recap_win",
    "Kaelen stands, opens the journal, and reads in a low, steady chronicler's voice:\n\n"
    "\"PREVIOUSLY. Six brave fools met in a tavern, and never left it. They bought a great deal of rope. They poked a "
    "dungeon with a ten-foot pole until the pole died. They solved the riddle of the candle. And at the end of all things, "
    "in a cave of gold, they faced Debtrax the Insolvent, and struck him down, and returned the Amulet of Unpaid Taxes to "
    "the Treasury, where it was immediately lost again.\"" + recap_tail,
    [C("Descend into the Underdark.", "l1_mush")], speaker=KAELEN)
g.node("l1_recap_friend",
    "Kaelen stands, opens the journal, and reads in a low, steady chronicler's voice:\n\n"
    "\"PREVIOUSLY. Six brave fools met in a tavern, and never left it. They bought a great deal of rope. They poked a "
    "dungeon with a ten-foot pole until the pole died. They solved the riddle of the candle. And at the end of all things, "
    "in a cave of gold, they faced Debtrax the Insolvent, and instead of killing him, they talked to him. Debtrax still "
    "writes to them. The letters are long. The poetry is bad. They keep every one.\"" + recap_tail,
    [C("Descend into the Underdark.", "l1_mush")], speaker=KAELEN)
g.node("l1_mush",
    "OAKHAVEN (GM): \"Down, and down, and down. The tunnels open into a vast cavern lit by mushrooms the size of houses, "
    "glowing in soft blues and greens. The air smells of damp earth and, faintly, of ink. What do you do?\"\n\n"
    "SABRINO: \"Fireball.\"\n\nOAKHAVEN (GM): \"There's nothing to fireball.\"\n\nSABRINO: \"Preventative fireball.\"",
    [C("[Barbarian] Eat the biggest, glowiest mushroom.", "l1_mush_barb", [FS("dnd_barbarian")]),
     C("[Bard] Sing to the mushrooms. They look like they'd appreciate it.", "l1_mush_bard", [FS("dnd_bard")], [SF("lich_win_1")]),
     C("[Rogue] Scout ahead, silently, through the stalks.", "l1_mush_rogue", [FS("dnd_rogue")],
       roll={"skill": "stealth", "dc": 10, "fail_next": "l1_mush_rogue_fail"}, actions=[SF("lich_win_1")]),
     C("[Wizard] Identify the mushrooms with a careful arcane analysis.", "l1_mush_wiz", [FS("dnd_wizard")], [SF("lich_win_1")]),
     C("[Paladin] Bless the mushrooms. All of them. Individually.", "l1_mush_pal", [FS("dnd_paladin")], [SF("lich_win_1")]),
     C("[Anyone] \"Let's stick together and keep moving.\"", "l1_rivals")])
g.node("l1_mush_barb", "You eat the biggest, glowiest mushroom.\n\nOAKHAVEN (GM, rolling something behind the screen, then rolling "
       "it again because he likes the sound): \"You can now see sounds. You can hear colours. Gerald is a very loud beige.\"\n\n"
       "ROLF: \"Gerald is OFFENDED.\"\n\nFor the next hour of real time, your character narrates everything as a symphony. "
       "Sister Crumb eventually cures you with a slice of toast. You are, somehow, a better person for it.",
       [C("Onward.", "l1_rivals")], [SF("lich_win_1")])
g.node("l1_mush_bard", "You sing. The mushrooms lean towards you. One of them, very slowly, begins to hum along in a deep, "
       "fungal baritone.\n\nOAKHAVEN (GM): \"The mushrooms... are now your fans. They will follow your career with great "
       "interest.\"\n\nBAGGY: \"Do they have names?\"\n\nOAKHAVEN (GM, closing his eyes): \"They are all called Stuart.\"",
       [C("Onward, with an audience of Stuarts.", "l1_rivals")])
g.node("l1_mush_rogue", "You slip through the mushroom stalks like a shadow, and come back with a full map of the cavern, a pouch of "
       "glowing spores, and a note pinned to a stalk: 'Inkwell: 3 miles. Rival adventurers: 1 mile. Their healer cheats at "
       "dice.'\n\nHOLLIS (very quietly): \"Respect.\"", [C("Onward.", "l1_rivals")])
g.node("l1_mush_rogue_fail", "You step silently into the mushroom forest, onto a mushroom that squeaks. Loudly. Like a dog toy.\n\n"
       "Every mushroom in the cavern squeaks back. It goes on for some time.\n\nOAKHAVEN (GM, with deep joy): \"Roll "
       "initiative against your own dignity.\"", [C("Onward, squeakily.", "l1_rivals")])
g.node("l1_mush_wiz", "You perform a careful arcane analysis. The mushrooms are: edible (three), poisonous (forty), and sentient "
       "(one, which asks you to stop analysing it, it finds it invasive).\n\nSABRINO: \"Can I fireball the poisonous ones?\"\n\n"
       "OAKHAVEN (GM): \"They're mushrooms, Sabrino.\"\n\nSABRINO: \"POISONOUS mushrooms.\"",
       [C("Onward.", "l1_rivals")])
g.node("l1_mush_pal", "You bless every mushroom. It takes forty minutes. Lord Definitely-Not-A-Vampire helps, standing well back from "
       "the glowing ones 'for unrelated reasons'.\n\nOAKHAVEN (GM): \"The mushrooms are now holy. They glow gold instead of "
       "blue. Several of them have started a small church.\"", [C("Onward.", "l1_rivals")])
g.node("l1_rivals",
    "OAKHAVEN (GM): \"Ahead, on the path, another adventuring party blocks the way. Five of them. Matching capes. Perfect "
    "teeth. Their armour is polished. Their weapons are glowing. They are all level twenty.\"\n\n"
    "He produces a second sheet of paper and reads, in an insufferable voice:\n\n"
    "OAKHAVEN (as GRIMSBY OPTIMUS): \"Well, well. If it isn't a party of AMATEURS. I am Grimsby Optimus, half-elf Paladin, "
    "Warlock, Sorcerer and Bard. We are THE GLORIOUS FIVE. Our stats are all eighteen. Our backstories are one sentence long. "
    "We have done this dungeon nine times. We know where every trap is. Out of our way.\"\n\n"
    "HOLLIS (narrowing his eyes): \"Their stats are all eighteen?\"\n\nOAKHAVEN (GM): \"Yes.\"\n\nHOLLIS: \"...Suspicious.\"",
    [C("[Challenge] \"Race you to Inkwell, Grimsby.\"", "l1_race", roll={"skill": "athletics", "dc": 12, "fail_next": "l1_race_lose"},
       actions=[SF("lich_win_2")]),
     C("[Rogue] While they gloat, steal their map.", "l1_steal_map", [FS("dnd_rogue")], [SF("lich_win_2"), SF("lich_their_map")]),
     C("[Hollis] Let Grizzlebeard handle it.", "l1_hollis_hmm"),
     C("[Kind] \"There's room on the path for everyone. After you.\"", "l1_kind")])
g.node("l1_race", "You win. Somehow. Grimsby Optimus trips over his own glorious cape at the last bend, and his party lands in a "
       "heap of matching boots.\n\nOAKHAVEN (as GRIMSBY): \"This isn't OVER, amateurs!\"\n\nBAGGY (standing up at the real "
       "table, fists raised): \"YEAH!\"", [C("Onward.", "l1_steve")])
g.node("l1_race_lose", "You lose. Badly. The Glorious Five speedrun past you, leaping traps they already know about, collecting "
       "treasure without stopping, and Grimsby salutes you from the far end of the cavern.\n\nOAKHAVEN (as GRIMSBY): "
       "\"Better luck next campaign!\"\n\nMARTA: \"I hope they all get indigestion.\"\n\nOAKHAVEN (GM, making a note): \"...Noted.\"",
       [C("Onward.", "l1_steve")])
g.node("l1_steal_map", "While Grimsby Optimus explains, at length, how optimised his build is, you lift their map from the healer's "
       "pack. It is annotated with every trap, every secret door, and a note in the margin: 'Phylactery: Tower of Unfiled "
       "Things. Front door is trapped. Use the back door. Nobody ever uses the back door.'\n\nOAKHAVEN (GM, staring at his own "
       "notes): \"...I wrote that for MY reference.\"", [C("Onward.", "l1_steve")])
g.node("l1_hollis_hmm", "HOLLIS (as Grizzlebeard, slowly standing, real-world chair scraping): \"Hmm.\"\n\nOAKHAVEN (GM): \"...The "
       "Glorious Five look at Grizzlebeard. Grizzlebeard looks at the Glorious Five. Roll Intimidation.\"\n\nHOLLIS: \"Twenty.\"\n\n"
       "OAKHAVEN (GM): \"Hollis, you haven't ROLLED.\"\n\nHOLLIS: \"I'm intimidating you. Hmm.\"\n\nThe Glorious Five step aside. "
       "Grimsby Optimus looks shaken. So does Oakhaven, slightly.", [C("Onward.", "l1_steve")], [SF("lich_win_2")])
g.node("l1_kind", "You step aside and wave them through. Grimsby Optimus looks deeply confused. Nobody has ever been nice to him "
       "before. He hesitates, then hands you a potion.\n\nOAKHAVEN (as GRIMSBY, gruffly): \"...Trap on the third bridge. Don't "
       "say I told you.\"\n\nThey march away. One of the Glorious Five, the healer, looks back at you, and waves.\n\n"
       "OAKHAVEN (GM, softly, out of character): \"Huh. I'd planned for them to be villains.\"",
       [C("Onward.", "l1_steve")], [SF("lich_win_2"), SF("lich_glorious_kind")])
g.node("l1_steve",
    "OAKHAVEN (GM): \"At the edge of the cavern, at a crossroads, a figure in a battered helmet sits by a campfire, roasting "
    "a mushroom on a stick. He looks up. He has a scar. He has a familiar face.\"\n\n"
    "OAKHAVEN (as the figure): \"...You. YOU. From the tavern. You threw a table at me. Or sang at me. Or lectured me. It's "
    "all a blur.\"\n\n"
    "BAGGY (whispering, delighted): \"It's STEVE.\"\n\n"
    "OAKHAVEN (as STEVE): \"I gave up banditry after that. Went to night school. I'm an adventurer now. A bad one. Can I "
    "come with you?\"",
    [C("\"Welcome to the party, Steve.\"", "l1_end", actions=[SF("lich_steve"), SF("lich_win_3")]),
     C("\"Absolutely not, Steve.\"", "l1_end_nosteve")])
g.node("l1_end", "Steve joins the party. The whole table cheers. Steve has four hit points and a spoon.\n\n"
       "OAKHAVEN (GM): \"You make camp with Steve. And as you sleep, far below, in a tower of black paper, something with no "
       "heartbeat opens a drawer marked IN, and finds it is still full.\" He lowers the screen. \"And that's where we'll stop "
       "for tonight.\"", [C('"Same time next week."', "greeting")], [SQ(L1, 100), XP("lore", 40)])
g.node("l1_end_nosteve", "Steve looks heartbroken. Then he nods, puts out his campfire, and walks off into the dark with his spoon.\n\n"
       "MARTA: \"...Oh, now I feel terrible.\"\n\nOAKHAVEN (GM): \"Steve will remember this.\"\n\nROLF (quietly): \"Can we go "
       "back for Steve?\"\n\nOAKHAVEN (GM): \"Next week. And that's where we'll stop for tonight.\"",
       [C('"Same time next week."', "greeting")], [SQ(L1, 100), XP("lore", 30)])

# ======================================================================= SESSION TWO: THE CITY OF INKWELL
g.node("l2_start",
    "KAELEN (journal open, reading): \"PREVIOUSLY. The party descended into the Underdark. They met mushrooms with opinions. "
    "They met the Glorious Five, who are glorious and five. They met Steve again, and the table is still arguing about what "
    "happened to Steve.\"\n\n"
    "OAKHAVEN (GM): \"Session Two. The city of INKWELL.\" He sounds happier than you have ever heard him. \"A city of a "
    "hundred thousand gnome clerks, carved into a stalactite, lit by lanterns of luminous ink. Every street is a queue. "
    "Every door has a stamp. At the gate stands a gnome behind a desk.\"\n\n"
    "OAKHAVEN (as the GATE CLERK): \"Form 1-UD, please. Underdark Residency Permit. In triplicate.\"\n\n"
    "The whole table groans. Oakhaven has never looked so content.",
    [C("[Fill in the form] Every field. Honestly. Carefully.", "l2_form"),
     C("[Gerald] \"Rolf, this is your moment.\"", "l2_gerald", actions=[SF("lich_win_4")]),
     C("[Sabrino] \"Sabrino, don't.\"", "l2_sabrino_form")])
g.node("l2_form",
    "OAKHAVEN (as the GATE CLERK): \"Question one. Purpose of visit: (a) business, (b) pleasure, (c) slaying a lich.\"",
    [C('"(a) Business."', "l2_form2"), C('"(c) Slaying a lich."', "l2_form2_honest")])
g.node("l2_form2", "OAKHAVEN (as the GATE CLERK): \"Business. Very good. Question two: are you, or have you ever been, a "
       "dragon?\"\n\nYou look round the table. Everyone looks at Hollis. Hollis says nothing. The clerk stamps the form anyway.",
       [C("Enter Inkwell.", "l2_city")], [SF("lich_win_4")])
g.node("l2_form2_honest", "OAKHAVEN (as the GATE CLERK, not looking up): \"Slaying a lich. Third this month. Queue on the left.\"\n\n"
       "There is, in fact, a queue on the left. It is very long. At the front, bored, wearing matching capes, are the Glorious Five.\n\n"
       "OAKHAVEN (as GRIMSBY): \"Oh, not YOU again.\"", [C("Enter Inkwell (eventually).", "l2_city")], [SF("lich_win_4")])
g.node("l2_gerald",
    "ROLF (cracking his knuckles, putting on imaginary spectacles): \"Gerald approaches the desk.\"\n\n"
    "What follows is the greatest piece of roleplay the back table has ever seen. Gerald the accountant fills in Form 1-UD in "
    "four minutes flat. He corrects two errors on the form itself. He points out that Section Nine contradicts Section Four. "
    "He asks to speak to the gate clerk's supervisor, and then to the supervisor's supervisor, and by the end of it the gnome "
    "bureaucracy of Inkwell has offered Gerald a job.\n\n"
    "OAKHAVEN (GM, standing, applauding): \"Gerald... Gerald, I have been waiting nine years for someone to do that.\"\n\n"
    "ROLF (glowing, shirtless, ecstatic): \"Gerald declines the job. Gerald has a party now.\"",
    [C("Enter Inkwell.", "l2_city")])
g.node("l2_sabrino_form", "SABRINO: \"Sabrino the Second casts Fireball on the form.\"\n\nOAKHAVEN (GM): \"The form is fireproof. "
       "All gnome forms are fireproof. Everyone in Inkwell is Sabrino-proof. We planned for you.\"\n\nSABRINO (outraged): "
       "\"WE?\"\n\nOAKHAVEN (GM): \"The gnomes. The gnomes planned for you.\" He fills in the form himself, in character, and "
       "lets you through out of pity.", [C("Enter Inkwell.", "l2_city")])
g.node("l2_city",
    "OAKHAVEN (GM): \"Inkwell. Lanterns of glowing ink hang over streets so narrow you can touch both walls. Gnomes hurry past "
    "carrying towers of paper. Somewhere a bell rings, and every gnome in the street stops, stamps something, and moves on.\"\n\n"
    "\"In the centre of the city stands a tower of black paper, folded like a vast origami spire. The Tower of Unfiled "
    "Things. The Lich's phylactery is somewhere inside.\"\n\n"
    "\"Before you is a tavern called the Damp Quill. What do you do?\"",
    [C("[Gather information] Head into the Damp Quill and listen.", "l2_tavern"),
     C("[Baggy] \"Detective Inspector Baggington will investigate.\"", "l2_baggy")])
g.node("l2_tavern",
    "OAKHAVEN (GM): \"The Damp Quill is full of off-duty gnome clerks, all complaining about the same thing.\"\n\n"
    "OAKHAVEN (as a GNOME CLERK, gloomily): \"Six hundred years he's been up in that tower. Never comes out. Just files. Files "
    "everyone's forms, perfect, every one. Mine, yours, the dragon's. But never his OWN. Sits up there with it on his desk, "
    "they say. Six hundred years. Can't bring himself to do it.\"\n\n"
    "MARTA (out of character, quietly): \"That's sad, actually.\"\n\n"
    "OAKHAVEN (GM, quickly): \"It's a FANTASY tax return, Marta. Moving on.\"",
    [C("Plan the heist.", "l2_plan")], [SF("lich_win_5"), SF("lich_heard_rumour")])
g.node("l2_baggy",
    "BAGGY (rising, magnifying glass raised): \"Sir Detective Inspector Baggington examines the city of Inkwell. ALL of it.\"\n\n"
    "OAKHAVEN (GM): \"All of it.\"\n\nBAGGY: \"I've got a magnifying glass of plus-one perception.\"\n\n"
    "OAKHAVEN (GM, sighing): \"Roll.\"\n\nBaggy rolls a natural twenty, and screams, and knocks the tea over. Marta saves the "
    "biscuits.\n\nOAKHAVEN (GM, in awe): \"Baggington notices that the Tower of Unfiled Things has a back door. Nobody ever "
    "uses the back door. It is not trapped. There is a doormat. It says WELCOME, in very small, hopeful letters.\"",
    [C("Plan the heist.", "l2_plan")], [SF("lich_win_5"), SF("lich_their_map")])
g.node("l2_plan",
    "OAKHAVEN (GM): \"You retreat to a rented room above the Damp Quill to plan the heist.\"\n\n"
    "Two hours pass. Real hours. Marta makes a second pot of tea, then a third. Kaelen's journal fills with diagrams. At one "
    "point Ashgrave proposes a plan involving a dramatic entrance through a stained-glass window, and is overruled. At another "
    "point Sabrino proposes a plan that is just the word 'fireball' written forty times.\n\n"
    "OAKHAVEN (GM, checking the clock): \"Have you decided on a plan?\"",
    [C("[Elaborate] Baggy's plan: nine stages, three disguises, a diversion, a goose.", "l2_end", actions=[SF("lich_plan_elaborate")]),
     C("[Simple] \"We go in the back door. We take the cabinet. We leave.\"", "l2_end", actions=[SF("lich_plan_simple"), SF("lich_win_6")]),
     C("[Chaos] \"Sabrino, you're in charge.\"", "l2_end", actions=[SF("lich_plan_sabrino")])])
g.node("l2_end",
    "OAKHAVEN (GM): \"The plan is set. Tomorrow night, you go in.\"\n\n"
    "He looks round the table, at the tea, at the diagrams, at Kaelen still writing, and smiles very slightly.\n\n"
    "\"I want everyone to know that no plan has ever survived its first contact with this table. Not one. In nine years.\"\n\n"
    "\"And that's where we'll stop for tonight.\"",
    [C('"Same time next week."', "greeting")], [SQ(L2, 100), XP("persuasion", 40)])

# ======================================================================= SESSION THREE: THE HEIST
g.node("l3_start",
    "KAELEN (reading): \"PREVIOUSLY. The party reached the city of Inkwell. They filled in a form. Gerald was magnificent. "
    "They learned that the Lich sits alone in his tower with one unfiled form on his desk, and has done for six hundred years, "
    "and Marta said that was sad, and the Game Master said it wasn't. They made a plan.\" A pause. \"It was a plan.\"\n\n"
    "OAKHAVEN (GM): \"Session Three. The Heist. Midnight. The Tower of Unfiled Things looms over you, black paper rustling in "
    "a wind that comes from nowhere. You put the plan into action.\"\n\n"
    "OAKHAVEN (GM): \"Roll for the first step.\"\n\nYou roll. The die skitters across the table, bounces off Sabrino's hat, "
    "and lands on a one.\n\nOAKHAVEN (GM, with the serene satisfaction of a man proven right): \"The plan is ruined.\"",
    [C("\"Already?\"", "l3_ruined")])
g.node("l3_ruined",
    "OAKHAVEN (GM): \"Already. Every part of it.\"\n\n"
    "\"The diversion goose escapes and joins the city guard. The disguises turn out to be the uniforms of a department that "
    "was closed in the year 412. Somebody, and I'm not saying who, Sabrino, has already set fire to the front door.\"\n\n"
    "\"Alarm bells are ringing all over the tower. Paper golems are unfolding from the walls. What do you do?\"\n\n"
    "Around the table, everyone looks at each other. And then, at once, everyone starts improvising.",
    [C("[Rally the party] \"Everyone! Do what you're good at!\"", "l3_moments", actions=[SF("lich_win_6")]),
     C("[Panic] \"RUN.\"", "l3_moments")])
g.node("l3_moments",
    "It's chaos, and it's glorious.\n\n"
    "Sister Crumb throws bread at the paper golems; it turns out paper golems love bread, and three of them sit down to eat. "
    "Lord Definitely-Not-A-Vampire stands in a beam of magical lantern light and sparkles so brightly the guards are blinded. "
    "Gerald stops the head guard and audits him on the spot. Sir Detective Inspector Baggington investigates a suspicious "
    "door, which turns out to be the right door. Sabrino the Second casts Fireball, finally, on something that deserves it.\n\n"
    "OAKHAVEN (GM): \"And you?\"",
    [C("[Rogue] Pick the lock on the vault door.", "l3_vault", [FS("dnd_rogue")], roll={"skill": "lockpicking", "dc": 11, "fail_next": "l3_vault_kick"},
       actions=[SF("lich_win_7")]),
     C("[Barbarian] Kick the vault door in.", "l3_vault_kick", [FS("dnd_barbarian")], [SF("lich_win_7")]),
     C("[Bard] Sing the vault door a lullaby until it nods off and swings open.", "l3_vault", [FS("dnd_bard")], [SF("lich_win_7")]),
     C("[Wizard] Cast Knock.", "l3_vault", [FS("dnd_wizard")], [SF("lich_win_7")]),
     C("[Paladin] Knock. Politely. With your hand.", "l3_vault_polite", [FS("dnd_paladin")], [SF("lich_win_7")]),
     C("[Steve] \"Steve! You're up!\"", "l3_steve", [FS("lich_steve")], [SF("lich_win_7")])])
g.node("l3_vault", "The vault door swings open with a sound like a very old book being opened for the first time.", [C("Go inside.", "l3_cabinet")])
g.node("l3_vault_kick", "You kick the vault door. It's made of six hundred years of compressed paperwork. It does not move. You "
       "kick it again. Hollis gets up, walks round the table, and kicks the real table leg in solidarity. The vault door, "
       "for reasons nobody can explain, opens.\n\nOAKHAVEN (GM): \"...Narrative momentum.\"", [C("Go inside.", "l3_cabinet")])
g.node("l3_vault_polite", "You knock on the vault door. Politely.\n\nOAKHAVEN (GM, after a long pause): \"...From inside, a dry, quiet "
       "voice says: 'Come in.'\"\n\nThe whole table goes silent.\n\nOAKHAVEN (GM): \"Nobody has ever knocked before.\"",
       [C("Go inside.", "l3_cabinet")], [SF("lich_knocked")])
g.node("l3_steve", "OAKHAVEN (as STEVE, trembling, gripping his spoon): \"Me? Really?\"\n\nSteve, four hit points, armed with a "
       "spoon, walks up to the vault door, and turns the handle.\n\nIt was never locked. Nobody had ever tried the handle.\n\n"
       "OAKHAVEN (as STEVE, in a whisper): \"...Night school.\"\n\nThe table erupts. Rolf is crying. Baggy is standing on a "
       "chair. Steve is, briefly, the greatest hero in the history of the Lantern Inn.", [C("Go inside.", "l3_cabinet")])
g.node("l3_cabinet",
    "OAKHAVEN (GM): \"Inside the vault there is no gold. No treasure. Only a single, ordinary, four-drawer filing cabinet, "
    "standing alone in the middle of the room. The top drawer is labelled IN. The bottom drawer is labelled OUT. The OUT "
    "drawer is empty. It has been empty for six hundred years.\"\n\n"
    "\"This is the phylactery. In the IN drawer is a single sheet of paper: a tax return, every field blank, and pinned to it, "
    "a note in thin, shaking handwriting.\"\n\n"
    "He reads the note aloud, and his voice is very quiet.\n\n"
    "OAKHAVEN (GM): \"'To whoever finds this. Please file it for me. I find that I cannot. I have filed everyone else's "
    "for six hundred years, and I cannot do my own, because when it is done, there will be nothing left for me to do. "
    "I am so tired.'\"",
    [C("Pick up the tax return.", "l3_end")])
g.node("l3_end",
    "As your fingers touch the paper, every lantern in the vault goes out.\n\n"
    "OAKHAVEN (GM, slowly, in a voice like dry pages): \"A figure stands in the doorway. Robes the colour of old ink. A face "
    "like a skull wearing spectacles. In one bony hand, a quill.\"\n\n"
    "OAKHAVEN (as THE LICH): \"Who... has touched... my IN tray?\"\n\n"
    "He lowers the screen.\n\nOAKHAVEN (GM): \"And that's where we'll stop for tonight.\"\n\nThe entire back table of the "
    "Lantern Inn screams at him in unison. Sabrino throws a biscuit. Oakhaven has clearly never been happier.",
    [C('"OAKHAVEN."', "greeting")], [SQ(L3, 100), XP("lockpicking", 40)])

# ======================================================================= SESSION FOUR: THE LICH
g.node("l4_start",
    "Word has got round. The back table is surrounded. Fenwick has brought his bookshelf again. Vaelen is selling snacks. "
    "Brother Aldous is pretending he just happened to be passing. Even Mortimer Quill, the ghost critic, is floating by the "
    "fireplace with his notebook, \"strictly in a professional capacity\".\n\n"
    "KAELEN (reading, voice catching slightly): \"PREVIOUSLY. The plan failed in the first ten seconds. The party improvised. "
    "They found the phylactery, and it was a filing cabinet, and inside it was a note from a very tired man. And then he "
    "came home, and found them in his vault.\"\n\n"
    "OAKHAVEN (GM, quietly): \"Session Four. The Lich.\"\n\n"
    "OAKHAVEN (as ARCHCHANCELLOR VELLUM DREADQUILL): \"Who... has touched... my IN tray?\"",
    [C("[Fight] \"Roll for initiative!\"", "l4_fight"),
     C("[Talk] \"We read your note, Archchancellor.\"", "l4_talk"),
     C("[Paladin who knocked] \"You said 'come in'. So we came in.\"", "l4_talk", [FS("lich_knocked")], [SF("lich_win_8")])])
g.node("l4_fight",
    "OAKHAVEN (as THE LICH): \"So be it.\" Bony hands rise. Paper whirls up from every drawer in the room like a storm.\n\n"
    "OAKHAVEN (GM): \"The Lich casts... Audit. Everyone make a saving throw against paperwork.\"\n\n"
    "Around the table, dice fly. Gerald makes his save with ease. Sabrino the Second fails the save and is buried in receipts. "
    "Hollis rolls a d6, very obviously, and says \"Twenty.\" Oakhaven doesn't even look.\n\n"
    "OAKHAVEN (GM): \"Your turn.\"",
    [C("[Roll] Strike the Lich with everything you have.", "l4_fight_win", roll={"skill": "athletics", "dc": 13, "fail_next": "l4_fight_stop"},
       actions=[SF("lich_win_8")]),
     C("[Stop] Lower your weapon. Something about this feels wrong.", "l4_fight_stop")])
g.node("l4_fight_win",
    "Your blow lands. The Lich staggers. Paper scatters. For a moment, it looks as though you might actually win.\n\n"
    "And then the Lich does something nobody expects. He doesn't fight back. He just sits down, very slowly, on the floor of "
    "his vault, among the drifting paper, and puts his skull in his hands.\n\n"
    "OAKHAVEN (as THE LICH, very quietly): \"Thank goodness. I thought no one would ever come.\"\n\n"
    "The whole table goes silent.",
    [C('"...You wanted someone to come?"', "l4_talk")])
g.node("l4_fight_stop",
    "You lower your weapon. One by one, the others lower theirs. Even Sabrino.\n\n"
    "SABRINO (quietly): \"He's not attacking. Look at him. He's just... tired.\"\n\n"
    "The paper storm settles. The Lich stands alone in the middle of his vault, a skull in spectacles, holding a quill he "
    "hasn't put down in six hundred years.",
    [C('"Archchancellor. We read your note."', "l4_talk")])
g.node("l4_talk",
    "OAKHAVEN (as THE LICH): \"You read it.\" The skull tilts. \"Then you know. I am the greatest administrator who ever "
    "lived. I have filed four million, six hundred thousand and twelve forms. Births. Deaths. Permits. Complaints.\"\n\n"
    "\"And I cannot file my own. Because when it is done, I will be done. There will be nothing left on my desk. No reason "
    "to stay. And I do not know who I am without something left to do.\"\n\n"
    "Behind the dragon screen, Oakhaven has stopped doing the voice. He is just reading. His hands, you notice, are not "
    "quite steady.",
    [C("[Gerald] \"Rolf. Gerald could help him file it.\"", "l4_file"),
     C("[Bard] Sing the Lich a song about rest.", "l4_song", [FS("dnd_bard")], roll={"skill": "persuasion", "dc": 12, "fail_next": "l4_song_crack"}),
     C("[Heart] \"You don't have to finish everything to be allowed to rest.\"", "l4_heart")])
g.node("l4_file",
    "ROLF (softly, putting on the imaginary spectacles): \"Gerald pulls up a chair. 'Archchancellor. May I?'\"\n\n"
    "And the whole table does it together. Gerald reads out each field. Sister Crumb finds the receipts. Baggington "
    "investigates six hundred years of deductions. Sabrino the Second, very carefully, does not set anything on fire. Kaelen "
    "writes down every line as it's filled in. And at the bottom, where it says SIGNATURE, Gerald hands the Lich his own "
    "quill.\n\n"
    "OAKHAVEN (as THE LICH, barely a whisper): \"...Oh. Oh, that wasn't so hard. Was it.\"\n\n"
    "He signs. He places the form in the OUT tray.",
    [C("Watch.", "l4_rest")], [SF("lich_filed"), SF("lich_win_8")])
g.node("l4_song",
    "You stand at the real table and sing. A lullaby, slow and simple, about putting down your pen at the end of a long day, "
    "about a desk that's finally clear, about someone waiting for you at home.\n\n"
    "Nobody laughs. Nobody even moves. In the crowd round the table, Mortimer Quill has stopped writing.\n\n"
    "OAKHAVEN (as THE LICH): \"...Someone waiting. I had forgotten that was a thing that could happen.\"",
    [C("Watch.", "l4_rest")], [SF("lich_sung")])
g.node("l4_song_crack",
    "Your voice cracks on the high note. You stop. You're embarrassed.\n\nAnd then, from round the table, Marta picks it up. "
    "Then Rolf. Then Baggy, very off-key. Then the whole crowd, Fenwick and Vaelen and even Hollis, humming, until the song "
    "isn't yours any more, it's everyone's.\n\nOAKHAVEN (as THE LICH): \"...All of you. For me.\"",
    [C("Watch.", "l4_rest")], [SF("lich_sung"), SF("lich_win_8")])
g.node("l4_heart",
    "You put down your dice.\n\n\"You don't have to finish everything to be allowed to rest,\" you say. \"Nobody does. Not a "
    "lich. Not a clerk. Nobody's desk is ever really empty. You're allowed to stop anyway.\"\n\n"
    "There's a long silence. Behind the dragon screen, Oakhaven takes his spectacles off. He doesn't do the Lich's voice "
    "when he speaks. He just speaks.\n\n"
    "OAKHAVEN: \"...Nineteen years. Excellent attendance. Not one day off. Not one.\" He looks round the table, at all of "
    "you. \"I wrote the Lich nine years ago. I didn't realise until just now who I'd written.\"",
    [C('"Then take a day off, Oakhaven. We\'ll still be here on Thursday."', "l4_rest"),
     C("Reach across the table and put a hand on his shoulder.", "l4_rest")], [SF("lich_heart"), SF("lich_win_8")])
g.node("l4_rest",
    "OAKHAVEN (GM, his voice steady again, gentle): \"The Archchancellor looks at the OUT tray. For the first time in six "
    "hundred years, it is not empty.\"\n\n"
    "\"He sets down his quill. He takes off his spectacles. He folds them, carefully, and places them on the desk.\"\n\n"
    "\"'Thank you,' says Vellum Dreadquill. 'I think I'll take the rest of the day off.'\"\n\n"
    "\"And he walks out of the vault, and out of the tower, and out of the city of Inkwell, and nobody in the Underdark "
    "ever sees him again, though some say there's a skeleton in spectacles who sits by an underground lake, feeding the "
    "fish, doing absolutely nothing at all.\"",
    [C("The campaign is over.", "l4_bow_great", [FL(WINS, 6)]),
     C("The campaign is over.", "l4_bow", [FF(WINS, 6)])])
reward = [SQ(L4, 100), GI("core:item.lich_quill"), GI("core:item.oakhaven_postcard"), XP("lore", 150)]
g.node("l4_bow_great",
    "The crowd around the back table bursts into applause. It goes on and on. Mortimer Quill is applauding. Hollis is "
    "applauding. Steve, somewhere in everyone's imagination, is applauding with his spoon.\n\n"
    "Oakhaven slides something across the table to you: a slim, elegant quill, black as ink, with a silver nib.\n\n"
    "\"The Archchancellor's quill,\" he says. \"I carved it for the campaign. I'd like you to have it.\" Then, after a "
    "moment: \"I've booked a day off. Monday. My first in nineteen years. I don't know what people do on days off. I'll "
    "write and tell you.\"",
    [C('"Write and tell me everything, Oakhaven."', "greeting")], reward + [GG(160), SF("lich_legend")])
g.node("l4_bow",
    "Everyone applauds. It's a little messy, a little teary, and nobody is quite sure how the session ended up being about "
    "Oakhaven, but everybody knows it was.\n\n"
    "He slides a black quill across the table to you. \"The Archchancellor's. I carved it. Keep it.\" And then: \"I've "
    "booked a day off. Monday. I'll write.\"",
    [C('"I\'ll be waiting for the postcard."', "greeting")], reward + [GG(100)])
g.node("l_after",
    "Oakhaven is at his desk, as always. But there's a seashell beside his inkwell that wasn't there before, and a very "
    "faint sunburn across his nose.\n\n"
    "\"I went to the coast,\" he says. \"I sat on a beach. I did nothing. For six hours.\" He considers. \"It was terrifying. "
    "I'm going again next month.\"\n\n"
    "He taps a stack of papers. \"Campaign Three. 'The Mimic Who Wanted to Be a Real Chest.' Chester returns. Steve gets a "
    "subplot. Thursdays.\"",
    [C('"Wouldn\'t miss it."', "greeting")])

save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= quests, items
QQ = load("content/quests/chapter_zero_quests.json")
for qid, short in [(L1, "lich1"), (L2, "lich2"), (L3, "lich3"), (L4, "lich4")]:
    QQ["quests"].append({"id": qid, "title_key": f"quest.{short}.title", "summary_key": f"quest.{short}.summary", "campaign": "dungeons_debtors",
                         "stages": [{"stage": 0, "objective_key": f"quest.{short}.stage0", "journal_key": f"quest.{short}.journal0", "markers": ["npc_oakhaven"]},
                                    {"stage": 100, "objective_key": f"quest.{short}.stage100", "journal_key": f"quest.{short}.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
# Sessions start at stage 0 when the topic appears via the session's first line: set it on entry.
for nid, qid in (("l1_start", L1), ("l2_start", L2), ("l3_start", L3), ("l4_start", L4)):
    clerk[nid].setdefault("actions", []).append(SQ(qid, 0))
save("content/dialogue/chapter_zero_dialogue.json", D)
S.update({
    "campaign.dnd.desc": "Thursday nights at the back table of the Lantern Inn. Clerk Oakhaven is the Game Master. Hollis cheats. Bring snacks. Campaign One: The Amulet of Unpaid Taxes. Campaign Two: The Lich Who Forgot to File.",
    "quest.lich1.title": "The Lich Who Forgot to File I: The Descent",
    "quest.lich1.summary": "Oakhaven's second campaign. A lich, six hundred years overdue on his tax return. Two new players at the table.",
    "quest.lich1.stage0": "Play the session with Oakhaven's Thursday group.",
    "quest.lich1.journal0": "Campaign Two. Sabrino is playing a wizard called Sabrino. Kaelen is writing everything down.",
    "quest.lich1.stage100": "Completed: the party is in the Underdark (and Steve's story continues).",
    "quest.lich1.journal100": "Mushrooms with opinions, a rival party called the Glorious Five, and Steve. Steve went to night school.",
    "quest.lich2.title": "The Lich Who Forgot to File II: The City of Inkwell",
    "quest.lich2.summary": "A city of a hundred thousand gnome clerks. Oakhaven has never been happier.",
    "quest.lich2.stage0": "Play the session with Oakhaven's Thursday group.",
    "quest.lich2.journal0": "The city of Inkwell. Every street is a queue. Every door has a stamp.",
    "quest.lich2.stage100": "Completed: the party has a plan. Oakhaven says no plan has ever survived this table.",
    "quest.lich2.journal100": "We spent two real hours planning a heist. Oakhaven looked delighted the whole time, which is worrying.",
    "quest.lich3.title": "The Lich Who Forgot to File III: The Heist",
    "quest.lich3.summary": "The Tower of Unfiled Things. The plan. The plan's first ten seconds.",
    "quest.lich3.stage0": "Play the session with Oakhaven's Thursday group.",
    "quest.lich3.journal0": "Heist night. I rolled a one on the first step. The plan is gone. Everyone is improvising.",
    "quest.lich3.stage100": "Completed: the phylactery was a filing cabinet. Oakhaven stopped RIGHT THERE.",
    "quest.lich3.journal100": "Inside the vault: a filing cabinet, an empty OUT tray, and a note from a very tired man. Then the Lich came home.",
    "quest.lich4.title": "The Lich Who Forgot to File IV: The Lich",
    "quest.lich4.summary": "Archchancellor Vellum Dreadquill, and the one form he could never file.",
    "quest.lich4.stage0": "Play the final session with Oakhaven's Thursday group.",
    "quest.lich4.journal0": "Half of Bellwether is crowded round the back table. Even the ghost critic came.",
    "quest.lich4.stage100": "Completed: the Lich took the rest of the day off. So did Oakhaven.",
    "quest.lich4.journal100": "The Lich's form went in the OUT tray at last. Somewhere in the middle of it, the session stopped being about the Lich and started being about Oakhaven. He's booked a day off. His first in nineteen years.",
    "item.lich_quill.name": "The Archchancellor's Quill",
    "item.lich_quill.description": "A slim black quill with a silver nib, carved by Oakhaven for the Lich who finally put his down. +2 Intellect, +8% spell power, +1 to dice rolls in conversation.",
    "item.oakhaven_postcard.name": "A Postcard from Oakhaven",
    "item.oakhaven_postcard.description": "A postcard of a beach, written in neat Bureau handwriting.",
    "book.oakhaven_postcard.text": "A painted postcard of a pale beach, a grey sea and a very blue sky. On the back, in small, careful Bureau handwriting:\n\n\"Dear friend,\n\nI am at the coast. I have been sitting on the sand for three hours. I have done nothing. Nobody has asked me to stamp anything. A gull stole my sandwich. I did not file a complaint.\n\nI found myself thinking of the Archchancellor, by his underground lake, feeding the fish. I think he would have liked it here.\n\nThank you for Thursdays. Thank you for knocking.\n\nYours, unofficially,\nOakhaven\n\nP.S. There is a seashell in the envelope. It is for your desk. Everyone should have something on their desk that isn't work.\"",
})
def additem(path, e):
    d = load(path); d["items"].append(e); save(path, d)
additem("content/items/armor_and_gear.json",
        {"id": "core:item.lich_quill", "name_key": "item.lich_quill.name", "description_key": "item.lich_quill.description", "category": "accessory",
         "icon": "assets/ui/items/lich_quill.png", "world_model": "assets/models/items/seal_quill.glb", "slots": ["accessory"], "value": 260,
         "weight": 0.05, "armor": 0, "effects": [{"type": "stat_bonus", "stat": "intellect", "amount": 2},
                                                {"type": "bonus", "stat": "spell_power_bonus", "value": 0.08},
                                                {"type": "bonus", "stat": "dice_bonus", "value": 1.0}]})
additem("content/items/consumables_and_books.json",
        {"id": "core:item.oakhaven_postcard", "name_key": "item.oakhaven_postcard.name", "description_key": "item.oakhaven_postcard.description",
         "category": "book", "icon": "assets/ui/items/oakhaven_postcard.png", "world_model": "assets/models/items/spell_tome.glb", "slots": [],
         "value": 0, "weight": 0.01, "book_text_key": "book.oakhaven_postcard.text"})

# Oakhaven notices the holiday
N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.clerk_oakhaven":
        n["barks"].append({"text_key": "bark.clerk.holiday", "quest_id": L4, "min_stage": 100})
save("content/npcs/core_npcs.json", N)
S["bark.clerk.holiday"] = "Did you know the sea just... keeps going? Nobody tells you that. There's no form for it."

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

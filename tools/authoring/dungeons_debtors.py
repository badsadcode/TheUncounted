"""Dungeons & Debtors: Thursday tabletop nights at the Lantern Inn, with Clerk Oakhaven as Game Master.

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends.
It is a worked example of writing a long, read-aloud campaign with the Dlg helper (auto localization keys)."""
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

S0, S1, S2, S3 = ("core:quest.dnd_session0", "core:quest.dnd_session1", "core:quest.dnd_session2", "core:quest.dnd_session3")
GM = "npc.clerk_oakhaven.name"
CLASSES = ["dnd_barbarian", "dnd_bard", "dnd_rogue", "dnd_wizard", "dnd_paladin"]
WINS = ["dnd_win_1", "dnd_win_2", "dnd_win_3", "dnd_win_4", "dnd_win_5", "dnd_win_6"]


class Dlg:
    def __init__(self, did, speaker, prefix, nodes):
        self.id, self.speaker, self.prefix, self.nodes = did, speaker, prefix, nodes

    def node(self, nid, text, choices, actions=None, speaker=None):
        key = f"{self.prefix}.{nid}"
        S[key] = text
        n = {"speaker_key": speaker or self.speaker, "text_key": key}
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
dl = {d["id"]: d for d in D["dialogues"]}
clerk = dl["core:dialogue.clerk_oakhaven"]["nodes"]
g = Dlg("core:dialogue.clerk_oakhaven", GM, "dlg.dnd", clerk)

# Topics in Oakhaven's greeting
topics = [
    ("dlg.dnd.topic.pitch", '"Oakhaven, what do you do on Thursdays?"', [QB(S0, 0)], "pitch"),
    ("dlg.dnd.topic.s1", '"Is it Thursday? Is it game night?"', [QE(S0, 100), QB(S1, 100)], "s1_start"),
    ("dlg.dnd.topic.s2", '"Game night. The dungeon awaits, Game Master."', [QE(S1, 100), QB(S2, 100)], "s2_start"),
    ("dlg.dnd.topic.s3", '"Final session. Let\'s face the dragon."', [QE(S2, 100), QB(S3, 100)], "s3_start"),
    ("dlg.dnd.topic.after", '"Same time next Thursday?"', [QA(S3, 100)], "after"),
]
ch = clerk["greeting"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
new = []
for key, text, cond, nxt in topics:
    S[key] = text
    new.append({"text_key": key, "conditions": cond, "next": nxt})
clerk["greeting"]["choices"] = ch[:idx] + new + ch[idx:]

# ======================================================================= SESSION ZERO
g.node("pitch",
    "Oakhaven goes very still. He glances left, right, then lowers his voice as if confessing to a crime.\n\n"
    "\"On Thursdays, after the office closes, a few of us gather at the back table of the Lantern Inn and play... a game.\" "
    "He produces a battered rulebook roughly the thickness of a paving stone. \"DUNGEONS & DEBTORS. A game of heroic "
    "adventure, perilous dungeons and meticulous record-keeping.\"\n\n"
    "\"I am the Game Master.\" He says it with a dignity you have never seen in him before. \"We are short a player. "
    "Hollis cheats, Rolf cries, and Baggy keeps trying to arrest the furniture. Would you... care to roll up a character?\"",
    [C('"I would love to roll up a character."', "s0_rules", actions=[SQ(S0, 0)]),
     C('"What\'s a character? What\'s rolling?"', "s0_rules", actions=[SQ(S0, 0)]),
     C('"Maybe another Thursday."', "greeting")])
g.node("s0_rules",
    "Thursday. The back table of the Lantern Inn. Marta has put out bread, cheese and a pot of tea the size of a bucket. "
    "Around the table: Baggy, Rolf, Hollis, Lord Ashgrave (\"I am only here for the atmosphere\"), and Marta herself, "
    "pencil behind her ear.\n\n"
    "Oakhaven sits behind a folding screen painted with dragons and tax tables. He hands you a sheet of paper.\n\n"
    "OAKHAVEN (GM): \"Form 1-CS. Character Sheet. Please print clearly. First, we roll your attributes. Four dice, drop the "
    "lowest. No, Hollis, you may not 'help'.\"\n\n"
    "HOLLIS: \"Hmm.\"",
    [C("[Roll for Strength] Shake the dice in both hands and blow on them.", "s0_stats",
       roll={"skill": "athletics", "dc": 10, "fail_next": "s0_stats_bad"}, actions=[SF("dnd_good_stats")]),
     C("[Let Hollis roll for you] He's very insistent.", "s0_hollis")])
g.node("s0_stats", "Sixteen! A respectable number. The table makes approving noises. Rolf claps. Baggy writes \"16\" in a notebook "
       "for reasons nobody understands.\n\nOAKHAVEN (GM): \"Excellent. Now. Your class.\"", [C("Choose a class.", "s0_class")])
g.node("s0_stats_bad", "Four. You rolled a four. Two ones and a two and a... you check... another one.\n\nThere is a respectful "
       "silence around the table, the kind usually reserved for funerals.\n\nMARTA (patting your hand): \"You'll be a lovely "
       "character, dear. Characters with low numbers have the best stories.\"\n\nOAKHAVEN (GM): \"...Your class.\"",
       [C("Choose a class.", "s0_class")])
g.node("s0_hollis", "Hollis takes your dice, turns his back to the table, and rolls. \"Eighteen,\" he announces. \"Eighteen. "
       "Eighteen. Eighteen. Eighteen. And an eighteen.\"\n\nOAKHAVEN (GM): \"Hollis, show me the dice.\"\n\nHOLLIS: \"They rolled "
       "under the table.\"\n\nOAKHAVEN (GM): \"All six of them?\"\n\nHOLLIS: \"Hmm.\"\n\nYou are given a ten in everything. "
       "Hollis looks satisfied anyway.", [C("Choose a class.", "s0_class")])
g.node("s0_class",
    "OAKHAVEN (GM): \"Choose your class. Each is described in Chapter Four, pages eighty through four hundred.\"\n\n"
    "BAGGY (whispering): \"I'm a Paladin of Justice. I can arrest people with my mind.\"\n\n"
    "ROLF (whispering): \"I'm playing a human accountant called Gerald. It's the most exotic thing I can imagine.\"",
    [C("[Barbarian] Big. Angry. Shirtless. Rolf looks at you with new respect.", "s0_backstory", actions=[SF("dnd_barbarian")]),
     C("[Bard] You will solve every problem by singing at it. Including the dragon.", "s0_backstory", actions=[SF("dnd_bard")]),
     C("[Rogue] Sneaky, stabby, and you will absolutely steal from the party.", "s0_backstory", actions=[SF("dnd_rogue")]),
     C("[Wizard] Robes. Fireballs. A beard you have to describe in detail.", "s0_backstory", actions=[SF("dnd_wizard")]),
     C("[Paladin] Holy, righteous, and contractually obliged to lecture everyone.", "s0_backstory", actions=[SF("dnd_paladin")])])
g.node("s0_backstory",
    "OAKHAVEN (GM): \"And finally: your backstory. Briefly, please. Ashgrave's was forty-one pages.\"\n\n"
    "LORD ASHGRAVE: \"It was a tragedy in five movements.\"\n\n"
    "OAKHAVEN (GM): \"It was a tragedy in the sense that I had to read it.\"",
    [C("[Tragic] \"Orphaned. Twice. My village burned. Also my second village. I have a brooding scar and a sworn enemy.\"",
       "s0_party", actions=[SF("dnd_tragic")]),
     C("[Simple] \"Farmer. Nothing happened. I'm just here for the adventure.\"", "s0_party", actions=[SF("dnd_simple")]),
     C("[Relatable] \"Amnesiac. Legally dead. Owes burial tax. Nobody remembers them.\"", "s0_party", actions=[SF("dnd_relatable")])])
g.node("s0_party",
    "One by one, the others introduce their characters, in character, with voices.\n\n"
    "BAGGY: \"Sir Detective Inspector Baggington, Paladin of Justice. I have a magnifying glass of plus-one perception.\"\n\n"
    "ROLF: \"Gerald. Human. Accountant. I enjoy spreadsheets and wearing shirts.\" He looks so happy about the shirts.\n\n"
    "HOLLIS: \"Grizzlebeard. Monster hunter. White hair. Two swords. Says 'hmm'.\"\n\nOAKHAVEN (GM): \"That's just you, Hollis.\"\n\n"
    "HOLLIS: \"Hmm.\"\n\n"
    "LORD ASHGRAVE: \"Lord Definitely-Not-A-Vampire. A paladin who avoids sunlight for entirely unrelated reasons.\"\n\n"
    "MARTA: \"Sister Crumb. A cleric. I heal with bread.\" She passes round actual bread. Everyone's hit points go up.",
    [C('"So... when do we start?"', "s0_end")])
g.node("s0_end",
    "OAKHAVEN (GM): \"We start next Thursday. Character creation took four hours. It always takes four hours.\"\n\n"
    "He gathers the sheets into a folder labelled CAMPAIGN: THE AMULET OF UNPAID TAXES, and almost, almost smiles.\n\n"
    "\"Same time next week. Bring dice. Bring snacks. Hollis, bring HONEST dice.\"",
    [C('"Same time next week."', "greeting")], [SQ(S0, 100), XP("lore", 30)])

# ======================================================================= SESSION ONE
g.node("s1_start",
    "Thursday again. The back table. The dragon screen goes up, Marta's tea goes round, and Oakhaven clears his throat.\n\n"
    "OAKHAVEN (GM): \"Session One. You all meet in a tavern.\"\n\n"
    "A pause. Everyone looks around the Lantern Inn. At the bar. At Marta, pouring.\n\n"
    "ROLF: \"...We ARE in a tavern.\"\n\nOAKHAVEN (GM): \"Then this will be very immersive. A hooded stranger approaches your "
    "table.\" He pulls up the hood of his coat, without moving from behind the screen. \"'Greetings, adventurers. I have a "
    "quest.'\"",
    [C("[In character] \"Speak, stranger. What do you need?\"", "s1_quest", actions=[SF("dnd_win_1")]),
     C("[Suspicious] \"I roll Insight on the hooded stranger.\"", "s1_insight", roll={"skill": "perception", "dc": 8, "fail_next": "s1_insight"}),
     C("[Out of character] \"Oakhaven, that's just you in a hood.\"", "s1_hood")])
g.node("s1_insight", "OAKHAVEN (GM): \"You sense that the hooded stranger is... the Game Master. In a hood.\"\n\n"
       "HOLLIS: \"I roll Insight too.\"\n\nOAKHAVEN (GM): \"He's still me, Hollis.\"\n\nHOLLIS: \"Hmm. Suspicious.\"",
       [C("Let the stranger speak.", "s1_quest")])
g.node("s1_hood", "OAKHAVEN (GM): \"It is NOT me. It is Mysterious Hooded Stranger Number Four. He has a completely different "
       "voice.\" He clears his throat and does a completely identical voice. \"'Greetings, adventurers.'\"\n\nThe table "
       "dissolves. Marta snorts tea out of her nose. Oakhaven waits it out with tremendous patience.",
       [C("Let the stranger speak.", "s1_quest")])
g.node("s1_quest",
    "OAKHAVEN (GM, as the Stranger): \"Deep beneath the hills lies the Dungeon of Mild Peril. Within it rests the Amulet of "
    "Unpaid Taxes, stolen from the Royal Treasury four hundred years ago by Debtrax the Insolvent, an ancient red dragon.\"\n\n"
    "\"Bring it back, and you shall be rewarded with five hundred gold pieces.\"\n\n"
    "BAGGY (instantly): \"I'd like to see some identification.\"\n\n"
    "ROLF: \"Gerald would like to know if the five hundred gold is taxable.\"\n\n"
    "OAKHAVEN (GM, visibly delighted): \"It IS, Gerald. Thank you for asking.\"\n\n"
    "Just then, the door of the fictional tavern bursts open. A gang of fictional bandits stomps in, looking for trouble.",
    [C("Deal with the bandits.", "s1_brawl")])
g.node("s1_brawl",
    "OAKHAVEN (GM): \"Roll for initiative! Three bandits, one of them called Steve. What do you do?\"",
    [C("[Barbarian] Pick up a table. Throw the table. Throw Steve.", "s1_brawl_win", [FS("dnd_barbarian")], [SF("dnd_win_2")]),
     C("[Bard] Sing a song so moving the bandits lay down their weapons and weep.", "s1_brawl_bard", [FS("dnd_bard")],
       roll={"skill": "persuasion", "dc": 12, "fail_next": "s1_brawl_fail"}),
     C("[Rogue] Pick Steve's pocket during the fight. Then the other two. Then Baggy's.", "s1_brawl_rogue", [FS("dnd_rogue")],
       roll={"skill": "stealth", "dc": 11, "fail_next": "s1_brawl_fail"}),
     C("[Wizard] Cast Fireball. In the tavern. With everyone in it.", "s1_brawl_wizard", [FS("dnd_wizard")]),
     C("[Paladin] Lecture the bandits on the moral consequences of banditry.", "s1_brawl_paladin", [FS("dnd_paladin")],
       roll={"skill": "persuasion", "dc": 10, "fail_next": "s1_brawl_fail"})])
g.node("s1_brawl_win", "The table hits Steve squarely. Steve hits the wall. The other two bandits look at Steve, look at you, and "
       "leave very quickly.\n\nOAKHAVEN (GM): \"Steve is unconscious. You may loot Steve.\"\n\nROLF: \"Gerald would like to "
       "file Steve's tax return.\"", [C("Onward!", "s1_shop")])
g.node("s1_brawl_bard", "You sing. Your fictional voice soars. The bandits drop their weapons, put their arms round each "
       "other's shoulders and sway. One of them, Steve, sobs openly. They buy you a drink.\n\nOAKHAVEN (GM): \"Steve would "
       "like to join your party.\"\n\nEVERYONE: \"NO.\"", [C("Onward!", "s1_shop")], [SF("dnd_win_2")])
g.node("s1_brawl_rogue", "In the confusion you lift three purses, a dagger, a love letter addressed to Steve, and Baggy's "
       "magnifying glass.\n\nBAGGY: \"My magnifying glass! There's a THIEF among us!\"\n\nYOU: \"Shocking. We should "
       "investigate.\"\n\nBAGGY: \"YES. Partner!\" You investigate together. You do not find the thief.",
       [C("Onward!", "s1_shop")], [SF("dnd_win_2")])
g.node("s1_brawl_wizard", "OAKHAVEN (GM): \"You cast Fireball in a small wooden tavern.\" He stares at you for a long time. "
       "\"Roll damage. For everyone. Including yourself.\"\n\nThe fictional tavern burns down. The fictional bandits are very "
       "surprised. So is the fictional party. Marta's cleric heals everyone with bread, one slice at a time, muttering.\n\n"
       "MARTA: \"Every Thursday. EVERY Thursday somebody casts Fireball in the tavern.\"", [C("Onward! (Somewhat singed.)", "s1_shop")])
g.node("s1_brawl_paladin", "You deliver a stirring forty-minute lecture on the ethics of banditry, the social conditions that "
       "lead to it, and the importance of a good pension. The bandits, defeated, enrol in a correspondence course.\n\n"
       "LORD ASHGRAVE (as Lord Definitely-Not-A-Vampire): \"I too shall lecture.\"\n\nOAKHAVEN (GM): \"Please don't.\"",
       [C("Onward!", "s1_shop")], [SF("dnd_win_2")])
g.node("s1_brawl_fail", "It goes badly. Very badly. In the end Hollis's character, Grizzlebeard, wins the fight by saying \"Hmm\" "
       "at the bandits until they leave.\n\nOAKHAVEN (GM): \"That... worked. I don't know why that worked.\"\n\nHOLLIS: "
       "\"Natural twenty.\"\n\nOAKHAVEN (GM): \"You didn't roll.\"", [C("Onward!", "s1_shop")])
g.node("s1_shop",
    "OAKHAVEN (GM): \"Before you leave town, you may visit the general store.\"\n\n"
    "Two hours later, the party is still in the general store.\n\n"
    "Marta's cleric has bought fifty feet of rope, then another fifty feet \"in case\". Baggy has bought eleven magnifying "
    "glasses. Rolf has done a full audit of the shopkeeper's books and found a discrepancy. Ashgrave has bought a single "
    "black rose and refuses to explain why.\n\n"
    "OAKHAVEN (GM, faintly): \"And that's where we'll stop for tonight.\"\n\nROLF: \"We haven't left the tavern.\"\n\n"
    "OAKHAVEN (GM): \"We never leave the tavern on the first session. It's tradition.\"",
    [C('"Same time next Thursday?"', "greeting")], [SQ(S1, 100), XP("persuasion", 40)])

# ======================================================================= SESSION TWO
g.node("s2_start",
    "OAKHAVEN (GM): \"Session Two. The Dungeon of Mild Peril. You stand before a great stone door. Cold air breathes from "
    "the darkness beyond.\"\n\n"
    "BAGGY: \"I check for traps.\"\n\nOAKHAVEN (GM): \"On the door?\"\n\nBAGGY: \"On everything. Every five feet. For the "
    "whole dungeon. I'm a very thorough Paladin.\"\n\nOAKHAVEN (GM, sighing): \"Fine. Everybody move very slowly. What's "
    "your plan?\"",
    [C("[Classic] \"I prod the floor ahead of us with a ten-foot pole.\"", "s2_trap", actions=[SF("dnd_win_3")]),
     C("[Bold] \"I walk confidently down the middle of the corridor.\"", "s2_trap_hit"),
     C("[Delegate] \"Gerald goes first. Accountants are expendable.\"", "s2_gerald")])
g.node("s2_trap", "The ten-foot pole taps a flagstone. CLICK. Forty arrows fly out of the walls and hit nothing but the pole.\n\n"
       "OAKHAVEN (GM, through gritted teeth): \"The pole. Is. Destroyed.\"\n\nMARTA: \"I've got another fifty feet of rope and "
       "a broom.\"\n\nThe party proceeds, poking everything with a broom.", [C("Deeper into the dungeon.", "s2_room")])
g.node("s2_trap_hit", "CLICK. Forty arrows fly out of the walls. You make a saving throw.\n\nOAKHAVEN (GM): \"You take... "
       "forty arrows.\"\n\nSister Crumb hands you a slice of bread. You are healed to one hit point, and very full.\n\n"
       "BAGGY: \"I did say I'd check for traps.\"", [C("Deeper into the dungeon. Carefully.", "s2_room")])
g.node("s2_gerald", "ROLF (horrified, then resigned): \"Gerald... goes first.\"\n\nGerald steps on a pressure plate. Gerald is "
       "fine; Gerald's armour is a cardigan, and the arrows pass harmlessly through the knitting.\n\nOAKHAVEN (GM): \"That is "
       "not how arrows work.\"\n\nROLF: \"Gerald is very good at knitting.\"", [C("Deeper into the dungeon.", "s2_room")],
       [SF("dnd_win_3")])
g.node("s2_room",
    "OAKHAVEN (GM): \"You enter a chamber. In the centre stands a treasure chest. It is a very nice chest. It is, if anything, "
    "suspiciously nice.\"\n\nLORD ASHGRAVE: \"It's a mimic.\"\n\nBAGGY: \"It's DEFINITELY a mimic.\"\n\nHOLLIS: \"Mimic.\"\n\n"
    "OAKHAVEN (GM, innocently): \"It is a normal chest. What do you do?\"",
    [C("[Rogue: Search it for traps] Use your thieves' tools on the 'lock'.", "s2_mimic_rogue", [FS("dnd_rogue")], [SF("dnd_win_4")]),
     C("[Search for treasure] Ignore the chest. Search the room for treasure.", "s2_search"),
     C("[Open it] It's probably fine.", "s2_mimic"),
     C("[Feed it] Give the chest a slice of Marta's bread and see what happens.", "s2_mimic_bread", actions=[SF("dnd_win_4")])])
g.node("s2_mimic_rogue", "Your lockpick goes into the keyhole. The keyhole licks it.\n\nYou withdraw the lockpick very slowly, "
       "pocket it, and back away, while the 'chest' grins at you with a mouth full of teeth.\n\nOAKHAVEN (GM, disappointed): "
       "\"...Fine. It's a mimic. Well spotted.\"", [C("Carry on.", "s2_puzzle")])
g.node("s2_search", "You search the room for treasure.\n\nOAKHAVEN (GM, leaning forward, in a deep and booming voice he has "
       "clearly been practising): \"You find... NOTHING.\"\n\nA beat.\n\n\"A WANDERING MONSTER APPEARS.\"\n\nIt is a very "
       "small goblin. It looks at the six of you, looks at the chest with teeth, and wanders off again.\n\nOAKHAVEN (GM): "
       "\"I'd been saving that for three years.\"", [C("Carry on.", "s2_puzzle")])
g.node("s2_mimic", "You open the chest. The chest opens you.\n\nOAKHAVEN (GM): \"Roll a saving throw.\"\n\nYou roll. You "
       "survive, barely, smelling of chest. Rolf's accountant Gerald files an insurance claim on your behalf. It is denied.",
       [C("Carry on, slightly chewed.", "s2_puzzle")])
g.node("s2_mimic_bread", "You toss a slice of Marta's bread at the chest. The chest's lid snaps open, catches the bread "
       "out of the air, and closes again.\n\nThen it makes a small happy noise, sidles over, and leans against your leg like "
       "a cat.\n\nMARTA: \"Aww.\"\n\nOAKHAVEN (GM, defeated): \"The mimic... is now your pet. It is called...\"\n\nBAGGY: "
       "\"CHESTER.\"\n\nOAKHAVEN (GM): \"...It is called Chester.\"", [C("Carry on, with Chester.", "s2_puzzle")])
g.node("s2_puzzle",
    "OAKHAVEN (GM): \"A great door bars your way. Carved into it is a riddle. 'I am tall when I am young, and short when I am "
    "old. What am I?' Answer correctly, and the door will open.\"\n\n"
    "There is a long silence around the table. Rolf is counting on his fingers. Ashgrave whispers \"Me?\" Hollis says "
    "\"Hmm\" in a thoughtful sort of way.",
    [C("\"A candle.\"", "s2_riddle_win", actions=[SF("dnd_win_5")]),
     C("\"A tax return.\"", "s2_riddle_lose"),
     C("\"Ashgrave's patience.\"", "s2_riddle_lose"),
     C("[Barbarian] \"I hit the door.\"", "s2_riddle_door", [FS("dnd_barbarian")], [SF("dnd_win_5")])])
g.node("s2_riddle_win", "OAKHAVEN (GM): \"...Correct.\" He looks genuinely surprised. \"Nobody has ever got that.\"\n\n"
       "YOU: \"It's always a candle.\"\n\nOAKHAVEN (GM, writing it down): \"It's always a candle,\" he agrees softly. "
       "The door grinds open.", [C("Onward, to the dragon's lair.", "s2_split")])
g.node("s2_riddle_lose", "The door does not open. The riddle rearranges itself to say: 'NO.'\n\nMARTA (gently): \"It's "
       "a candle, dear.\"\n\nOAKHAVEN (GM): \"MARTA.\"\n\nMARTA: \"What? They looked so sad.\" The door opens anyway, out of "
       "pity.", [C("Onward, to the dragon's lair.", "s2_split")])
g.node("s2_riddle_door", "You hit the door. The door has an armour class of twenty-five. You hit it again. And again. "
       "Eventually Oakhaven, who has been watching the clock, says \"The door gives up\", and it does.\n\nROLF: \"That was "
       "beautiful.\"", [C("Onward, to the dragon's lair.", "s2_split")])
g.node("s2_split",
    "OAKHAVEN (GM): \"The corridor forks. Left: a faint smell of gold and brimstone. Right: a faint smell of... soup?\"\n\n"
    "Every player at the table turns to look at you.\n\n"
    "BAGGY (whispering urgently): \"Whatever you do, don't split the-\"",
    [C("[Wisdom] \"We stay together. Left, all of us.\"", "s2_end", actions=[SF("dnd_win_6")]),
     C("[Classic mistake] \"Let's split up. We'll cover more ground.\"", "s2_split_bad")])
g.node("s2_split_bad", "The table goes silent. Hollis puts his head in his hands. Oakhaven's smile is slow, terrible, and "
       "completely professional.\n\nTen minutes later, three of you are hanging upside down in a net, Gerald is being "
       "audited by a goblin, and Lord Definitely-Not-A-Vampire has been accidentally exposed to sunlight via a "
       "conveniently placed skylight.\n\nASHGRAVE: \"I SPARKLE.\"\n\nOAKHAVEN (GM): \"You take no damage, but your dignity "
       "takes four.\"\n\nYou regroup, eventually, at the dragon's door.", [C("At the dragon's door...", "s2_end")])
g.node("s2_end",
    "OAKHAVEN (GM): \"You stand at the threshold of a vast cavern. Gold, everywhere. Mountains of it. And on the largest "
    "mountain, asleep, curled around a single glittering amulet...\"\n\n"
    "He reaches behind the screen and produces the dragon: a red-painted salt shaker with paper wings.\n\n"
    "\"...DEBTRAX THE INSOLVENT. One eye opens.\" He puts the salt shaker down with a heavy click. \"And that's where we'll "
    "stop for tonight.\"\n\nThe whole table screams.",
    [C('"OAKHAVEN."', "greeting")], [SQ(S2, 100), XP("perception", 50)])

# ======================================================================= SESSION THREE
g.node("s3_start",
    "The back table is packed. Word has got around. Fenwick is watching from behind a bookshelf he has brought for the "
    "purpose. Kaelen is taking notes. Sabrino has provided snacks shaped like dice.\n\n"
    "OAKHAVEN (GM): \"Session Three. The salt shaker... I mean, DEBTRAX THE INSOLVENT rises from his hoard. His voice is "
    "like a landslide in a counting-house.\"\n\nHe does the voice. It is unexpectedly terrifying.\n\n"
    "OAKHAVEN (as DEBTRAX): \"WHO DARES DISTURB MY ACCOUNTS?\"",
    [C("[Fight] \"Roll for initiative! Everybody attack!\"", "s3_fight"),
     C("[Talk] \"We come in peace. Mostly. About the amulet...\"", "s3_talk"),
     C("[Bard] Seduce the dragon.", "s3_bard", [FS("dnd_bard")])])
g.node("s3_fight",
    "OAKHAVEN (GM): \"Debtrax breathes fire. Everyone make a saving throw.\"\n\n"
    "HOLLIS (instantly): \"Twenty.\"\n\nOAKHAVEN (GM): \"Hollis. That's a six-sided die.\"\n\nHOLLIS: \"It's a big six.\"\n\n"
    "The fire washes over the party. It's your turn.",
    [C("[Roll: Athletics] Charge the dragon with everything you have.", "s3_fight_win", actions=[SF("dnd_dragon_down")],
       roll={"skill": "athletics", "dc": 14, "fail_next": "s3_tpk"}),
     C("[Teamwork] \"Everyone, together, on three!\"", "s3_fight_team", [FL(WINS, 3)], [SF("dnd_dragon_down")])])
g.node("s3_fight_win", "Your dice hit the table and come up a nineteen. The whole back table of the Lantern Inn erupts. Rolf "
       "knocks over the tea. Baggy stands on a chair. Marta screams \"GET HIM!\" in a voice that has stopped tavern brawls "
       "for seventeen years.\n\nOAKHAVEN (GM, slowly, with deep respect): \"Debtrax the Insolvent... is defeated.\"",
       [C("Claim the Amulet.", "s3_end")])
g.node("s3_fight_team", "Everyone at the table rolls at once. Six dice clatter across the wood, and every single one comes up "
       "high, even Hollis's, which for once is clearly an honest twenty-sided die.\n\nHOLLIS (quietly): \"...Huh. Didn't "
       "need to cheat.\"\n\nOAKHAVEN (GM): \"Debtrax the Insolvent falls. Together.\"",
       [C("Claim the Amulet.", "s3_end")])
g.node("s3_tpk", "Your dice skitter off the table, bounce off the teapot, and land on a one.\n\nOAKHAVEN (GM, very gently): "
       "\"Debtrax breathes fire again. That's... a total party kill.\"\n\nA terrible silence falls over the table. Rolf's eyes "
       "fill with tears. Gerald. Poor Gerald.\n\nThen Oakhaven looks round at all of them, sighs, and turns over a card from "
       "behind his screen.\n\nOAKHAVEN (GM): \"...But a passing cleric of the Last Dawn happens to be walking past the "
       "dungeon, entirely by coincidence, with a big bag of resurrection bread.\"\n\nMARTA: \"That's me! That's Sister Crumb!\"\n\n"
       "OAKHAVEN (GM): \"Yes. It is. Somehow. Roll again.\"",
       [C("[Second chance] Roll again. Together, this time.", "s3_fight_team", actions=[SF("dnd_dragon_down")])])
g.node("s3_talk",
    "OAKHAVEN (as DEBTRAX): \"TALK? No adventurer has ever tried to TALK to me. They usually just stab.\" The salt shaker "
    "leans in. \"Very well. Speak.\"",
    [C("[Roll: Persuasion] \"You stole the Amulet of Unpaid Taxes. We'd like to settle the account. Fairly.\"", "s3_talk_win",
       actions=[SF("dnd_dragon_friend")], roll={"skill": "persuasion", "dc": 13, "fail_next": "s3_talk_audit"}),
     C("[Gerald] Let Rolf's accountant do the talking.", "s3_talk_audit")])
g.node("s3_talk_win", "OAKHAVEN (as DEBTRAX): \"Fairly? FAIRLY?\" A long pause. \"In four hundred years, nobody has ever "
       "offered to settle anything fairly.\"\n\nThe salt shaker settles back onto its hoard. \"Take the amulet. And tell the "
       "Treasury... tell them I was always going to give it back. I was just waiting for someone to ask nicely.\"\n\n"
       "Around the table there is a stunned silence. Then Baggy starts clapping. Then everyone is clapping.",
       [C("Claim the Amulet.", "s3_end")])
g.node("s3_talk_audit", "ROLF (as Gerald, adjusting imaginary spectacles): \"Mr. Insolvent. I've reviewed your hoard. Four hundred "
       "years of undeclared income. No receipts. No depreciation schedule.\"\n\nOAKHAVEN (as DEBTRAX, nervously): \"I'm a "
       "DRAGON.\"\n\nROLF: \"The law doesn't care, sir.\"\n\nTwenty minutes later the dragon has agreed to a payment plan, "
       "handed over the amulet as collateral, and is weeping quietly into its gold.\n\nROLF (out of character, glowing): "
       "\"I have never been so powerful.\"", [C("Claim the Amulet.", "s3_end")], [SF("dnd_dragon_friend")])
g.node("s3_bard", "You stand up from the table. In character. You clear your throat. You begin to sing.\n\nOAKHAVEN (GM): "
       "\"You're seducing the dragon.\"\n\nYOU: \"I'm seducing the dragon.\"\n\nOAKHAVEN (GM, closing his eyes): \"There is a "
       "gravestone at Hollowmere about this exact thing.\"\n\nYOU (still singing): \"I know.\"",
       [C("[Roll: Persuasion] Hit the high note.", "s3_bard_win", actions=[SF("dnd_dragon_friend")],
          roll={"skill": "persuasion", "dc": 15, "fail_next": "s3_bard_lose"})])
g.node("s3_bard_win", "The high note rings out across the Lantern Inn. Marta drops a plate. Fenwick, behind his bookshelf, "
       "forgets to shush anybody.\n\nOAKHAVEN (as DEBTRAX, slowly): \"...I am going to write you letters. So many letters.\"\n\n"
       "The dragon gives you the amulet, a lock of its, um, dragon hair, and a poem. The poem is very bad. You keep it anyway.",
       [C("Claim the Amulet.", "s3_end")])
g.node("s3_bard_lose", "The high note cracks. The dragon winces. Then, to everyone's surprise, laughs: a huge, rumbling, "
       "salt-shaker laugh.\n\nOAKHAVEN (as DEBTRAX): \"Nobody has made me laugh in four hundred years. Take the amulet. Take "
       "it! Just never sing again.\"", [C("Claim the Amulet.", "s3_end")])
g.node("s3_end",
    "OAKHAVEN (GM): \"And so the heroes returned the Amulet of Unpaid Taxes to the Royal Treasury, where it was promptly "
    "filed, stamped, and lost again.\"\n\n"
    "He lowers the dragon screen. Behind it, it turns out, is a whole little world: hand-drawn maps, a painted salt-shaker "
    "dragon, notes in neat Bureau handwriting going back years. Years of Thursdays.\n\n"
    "\"That's the end of the campaign,\" he says, and for once his voice isn't quite steady. \"Thank you. All of you. I've "
    "been writing this for nine years. You're the first group that ever finished it.\"",
    [C("End of campaign. Take a bow.", "s3_bow_great", [FL(WINS, 4)]),
     C("End of campaign. Take a bow.", "s3_bow", [FF(WINS, 4)])])
rew = [SQ(S3, 100), GI("core:item.lucky_d20"), GI("core:item.gm_screen"), XP("lore", 120)]
g.node("s3_bow_great", "The whole back table stands up and gives the Game Master a round of applause. Oakhaven takes off his "
       "spectacles, cleans them for much longer than spectacles need, and puts them back on.\n\nThen he hands you a single "
       "twenty-sided die, worn smooth, the numbers nearly rubbed away.\n\n\"My first die,\" he says. \"It always rolled "
       "well for people who deserved it. And the screen, too. I'll make a new one. I'm starting a new campaign.\"",
       [C('"What\'s it called?"', "after")], rew + [GG(150), SF("dnd_legend")])
g.node("s3_bow", "Everybody applauds. Hollis applauds loudest, which surprises everyone, including Hollis.\n\nOakhaven hands "
       "you his first die, worn smooth with years of Thursdays, and his old dragon screen.\n\n\"Keep them,\" he says. \"I'm "
       "starting a new campaign. Same time next week?\"", [C('"What\'s it called?"', "after")], rew + [GG(90)])
g.node("after",
    "Oakhaven straightens a stack of papers that is already straight.\n\n"
    "\"The next campaign is called 'The Lich Who Forgot to File'. It is set in the Underdark. There is a riddle. It is a "
    "candle.\" A very small smile. \"Every Thursday, after the office closes. Bring dice. Bring snacks.\"\n\n"
    "\"And bring Hollis honest dice. I've given up asking him.\"",
    [C('"Wouldn\'t miss it."', "greeting")])

save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= quests, campaign, items, props
QQ = load("content/quests/chapter_zero_quests.json")
def quest(qid, short, stages):
    QQ["quests"].append({"id": qid, "title_key": f"quest.{short}.title", "summary_key": f"quest.{short}.summary", "campaign": "dungeons_debtors",
                         "stages": [{"stage": s, "objective_key": f"quest.{short}.stage{s}", "journal_key": f"quest.{short}.journal{s}",
                                     "markers": ["npc_oakhaven"], **({"completed": True} if s == 100 else {})} for s in stages]})
quest(S0, "dnd0", (0, 100)); quest(S1, "dnd1", (0, 100)); quest(S2, "dnd2", (0, 100)); quest(S3, "dnd3", (0, 100))
for q in QQ["quests"]:
    if q["id"] in (S0, S1, S2, S3):
        for st in q["stages"]:
            if st.get("completed"):
                st.pop("markers", None)
QQ["campaigns"].append({"id": "dungeons_debtors", "name_key": "campaign.dnd.name", "desc_key": "campaign.dnd.desc", "kind": "tales", "order": 27})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "campaign.dnd.name": "Dungeons & Debtors",
    "campaign.dnd.desc": "Thursday nights at the back table of the Lantern Inn. Clerk Oakhaven is the Game Master. Hollis cheats. Bring snacks.",
    "quest.dnd0.title": "Session Zero: Character Creation",
    "quest.dnd0.summary": "Oakhaven has a secret: on Thursdays, he runs a tabletop game. He needs one more player.",
    "quest.dnd0.stage0": "Roll up a character with Oakhaven's Thursday group at the Lantern Inn (talk to Oakhaven).",
    "quest.dnd0.journal0": "Clerk Oakhaven is a Game Master. I did not see this coming, and yet it explains everything about him.",
    "quest.dnd0.stage100": "Completed: you have a character. It took four hours.",
    "quest.dnd0.journal100": "Character creation took four hours. I'm told it always takes four hours.",
    "quest.dnd1.title": "Session One: You All Meet in a Tavern",
    "quest.dnd1.summary": "A hooded stranger (definitely not Oakhaven) has a quest for the party.",
    "quest.dnd1.stage0": "Play the next session with Oakhaven.",
    "quest.dnd1.journal0": "Session One. We are in a tavern. We are also in a tavern.",
    "quest.dnd1.stage100": "Completed: the party never left the tavern.",
    "quest.dnd1.journal100": "We spent two hours in the general store. We never left the tavern. Apparently that's tradition.",
    "quest.dnd2.title": "Session Two: The Dungeon of Mild Peril",
    "quest.dnd2.summary": "Traps, a suspiciously nice chest, a riddle, and a fork in the corridor.",
    "quest.dnd2.stage0": "Play the next session with Oakhaven.",
    "quest.dnd2.journal0": "The Dungeon of Mild Peril awaits. Baggy will be checking for traps. Every five feet.",
    "quest.dnd2.stage100": "Completed: Debtrax the Insolvent opens one eye.",
    "quest.dnd2.journal100": "The dragon is a red-painted salt shaker with paper wings, and it is somehow terrifying. Oakhaven stopped the session RIGHT THERE.",
    "quest.dnd3.title": "Session Three: Debtrax the Insolvent",
    "quest.dnd3.summary": "The final session. A dragon, a hoard, and four hundred years of unpaid taxes.",
    "quest.dnd3.stage0": "Play the final session with Oakhaven.",
    "quest.dnd3.journal0": "The final session. Word has got around. Half of Bellwether is watching the back table.",
    "quest.dnd3.stage100": "Completed: the campaign is finished. The first group ever to finish it.",
    "quest.dnd3.journal100": "Oakhaven has been writing that campaign for nine years. We were the first group to finish it. He gave me his first die. Next Thursday: 'The Lich Who Forgot to File'.",
    "item.lucky_d20.name": "Oakhaven's Lucky d20",
    "item.lucky_d20.description": "A twenty-sided die worn smooth by years of Thursdays. It always rolled well for people who deserved it. +2 to every dice roll in conversation, +2% critical chance.",
    "item.gm_screen.name": "The Game Master's Screen",
    "item.gm_screen.description": "A folding screen painted with dragons and tax tables. Surprisingly good at stopping arrows. Held up, it makes you feel like you know something everyone else doesn't.",
    "dnd.table.title": "The Thursday Table",
    "dnd.table.text": "",
})
def additem(path, e):
    d = load(path); d["items"].append(e); save(path, d)
additem("content/items/armor_and_gear.json",
        {"id": "core:item.lucky_d20", "name_key": "item.lucky_d20.name", "description_key": "item.lucky_d20.description", "category": "accessory",
         "icon": "assets/ui/items/lucky_d20.png", "world_model": "assets/models/items/signet_ring.glb", "slots": ["accessory"], "value": 200,
         "weight": 0.05, "armor": 0, "effects": [{"type": "bonus", "stat": "dice_bonus", "value": 2.0}, {"type": "bonus", "stat": "crit_chance_bonus", "value": 0.02}]})
additem("content/items/armor_and_gear.json",
        {"id": "core:item.gm_screen", "name_key": "item.gm_screen.name", "description_key": "item.gm_screen.description", "category": "armor",
         "icon": "assets/ui/items/gm_screen.png", "world_model": "assets/models/items/iron_shield.glb", "slots": ["off_hand"], "value": 120,
         "weight": 2.5, "armor": 4, "effects": [{"type": "stat_bonus", "stat": "intellect", "amount": 1}, {"type": "stat_bonus", "stat": "presence", "amount": 1}]})
S.pop("dnd.table.title"); S.pop("dnd.table.text")

BW = load("content/regions/bellwether.json")
for pid, x0, x1, y0, y1, z0, z1 in [("thursday_table", -5.6, -3.4, 0.72, 0.82, 7.9, 9.3)] + \
        [(f"thursday_leg_{i}", x - 0.05, x + 0.05, 0.0, 0.72, z - 0.05, z + 0.05) for i, (x, z) in
         enumerate([(-5.5, 8.0), (-3.5, 8.0), (-5.5, 9.2), (-3.5, 9.2)])]:
    BW["props"].append({"id": pid, "model": "assets/models/env/floor_wood.glb", "pos": [round((x0 + x1) / 2, 3), y0, round((z0 + z1) / 2, 3)],
                        "scale": [round(x1 - x0, 3), round(y1 - y0, 3), round(z1 - z0, 3)], "solid": pid == "thursday_table", "uv_scale": [1, 0.2]})
BW["interactables"].append({"instance_id": "thursday_sheets", "type": "readable", "model": "", "pos": [-4.5, 0.95, 8.6], "rot_y": 0.0,
    "prompt": "Read the Character Sheets", "title": "Form 1-CS: Character Sheets (Thursday Group)",
    "text": ("A neat stack of character sheets, every one filled out on official Bureau Form 1-CS.\n\n"
             "SIR DETECTIVE INSPECTOR BAGGINGTON. Paladin of Justice. Equipment: magnifying glass (+1), eleven spare magnifying "
             "glasses, a hat. Notes: 'Suspects the hedge.'\n\n"
             "GERALD. Human. Accountant. Equipment: abacus, cardigan (+3 AC, knitted). Notes: 'Wants to audit the dragon.'\n\n"
             "GRIZZLEBEARD. Monster hunter. White hair. Two swords. Says 'hmm'. All attributes listed as 18. In pencil, in "
             "Oakhaven's hand: 'NO.'\n\n"
             "LORD DEFINITELY-NOT-A-VAMPIRE. Paladin. Avoids sunlight 'for unrelated reasons'. Backstory: see attached, 41 pages.\n\n"
             "SISTER CRUMB. Cleric. Heals with bread. Spell list: 'bread'. Notes: 'Brings real snacks. Protect at all costs.'\n\n"
             "Under the stack, a blank sheet with your name already written at the top in neat Bureau handwriting, as if "
             "somebody hoped you'd say yes.")})
save("content/regions/bellwether.json", BW)

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

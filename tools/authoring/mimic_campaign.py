"""Dungeons & Debtors III: The Mimic Who Wanted to Be a Real Chest. Oakhaven's third campaign (three sessions).

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends.
Chester (the mimic from Campaign One) wants to be certified as a real chest. Steve plays in person if he moved into
the Lantern Inn (flag steve_in_town); otherwise Kaelen puts down the quill and plays for one moment."""
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

LICH_DONE = "core:quest.lich_s4"
M1, M2, M3 = "core:quest.mimic_s1", "core:quest.mimic_s2", "core:quest.mimic_s3"
WINS = [f"mimic_win_{i}" for i in range(1, 7)]
GM, KAELEN, STEVE = "npc.clerk_oakhaven.name", "npc.ashbound_scout.name", "npc.steve.name"
STEVE_IN, STEVE_OUT = FS("steve_in_town"), FN("steve_in_town")


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
g = Dlg("dlg.mimic", clerk)

topics = [
    ("dlg.mimic.topic.s1", '"Campaign Three, Oakhaven? The one with Chester?"', [QA(LICH_DONE, 100), QB(M1, 100)], "m1_start"),
    ("dlg.mimic.topic.s2", '"Thursday! Back to the Container Convention."', [QE(M1, 100), QB(M2, 100)], "m2_start"),
    ("dlg.mimic.topic.s3", '"The final trial. Let\'s get Chester certified."', [QE(M2, 100), QB(M3, 100)], "m3_start"),
    ("dlg.mimic.topic.after", '"How\'s Chester doing, Oakhaven?"', [QA(M3, 100)], "m_after"),
]
ch = clerk["greeting"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
new = []
for key, text, cond, nxt in topics:
    S[key] = text
    new.append({"text_key": key, "conditions": cond, "next": nxt})
clerk["greeting"]["choices"] = ch[:idx] + new + ch[idx:]

# ======================================================================= SESSION ONE: THE APPLICATION
g.node("m1_start",
    "Thursday. The back table of the Lantern Inn. Oakhaven has a new dragon screen: this one is painted with chests. Big chests, small "
    "chests, chests with feet. One of them, in the corner, is winking.\n\n"
    "KAELEN (journal open, reading): \"PREVIOUSLY. Two campaigns. One dragon, defeated or befriended depending on who you ask. One lich, "
    "who took the day off. And one mimic, met in a dungeon in the second session of the first campaign. Some of you fed it bread. Some of "
    "you were eaten by it. It remembers both fondly.\"\n\n"
    "OAKHAVEN (GM): \"Campaign Three. THE MIMIC WHO WANTED TO BE A REAL CHEST.\"",
    [C("Look round the table.", "m1_steve", [STEVE_IN]),
     C("Look round the table.", "m1_nosteve", [STEVE_OUT])], [SQ(M1, 0)])
g.node("m1_steve",
    "There is a new chair at the table. In it sits Steve, in a clean shirt Marta found him, holding his battered character sheet in both "
    "hands like a prayer book.\n\n"
    "STEVE: \"Hello. I'm Steve. I'm playing a bard.\"\n\n"
    "OAKHAVEN (GM): \"What is your bard called?\"\n\nSTEVE: \"Steve.\"\n\nOAKHAVEN (GM): \"You can't call your character the same name as y—\"\n\n"
    "SABRINO (not looking up): \"He can.\"\n\n"
    "OAKHAVEN (GM, after a long look at Sabrino the Second's character sheet): \"...He can.\"\n\n"
    "Steve beams. Hollis slides a biscuit across to him without a word.",
    [C('"Welcome to the table, Steve."', "m1_door", actions=[SF("mimic_win_1")])])
g.node("m1_nosteve",
    "There is a little stack of envelopes beside Oakhaven's dice, all addressed in enormous wobbly capitals.\n\n"
    "OAKHAVEN (GM): \"Steve sends his apologies. He's still in the Whistling Wood. He has posted his moves in advance.\" He opens the first "
    "envelope. \"'STEVE ATTACKS.' Thank you, Steve.\" He opens the second. \"'STEVE ATTACKS AGAIN. HE HAS A SPOON.' Thank you, Steve.\"",
    [C("Settle in.", "m1_door")])
g.node("m1_door",
    "OAKHAVEN (GM): \"You are in a tavern.\"\n\n"
    "EVERYONE: \"Of course we are.\"\n\n"
    "OAKHAVEN (GM): \"There is a knock at the tavern door. Low down. Wooden. Polite.\" He knocks on the underside of the table: tok, tok, tok. "
    "\"The door creaks open. On the step is a treasure chest. Oak, brass corners, a little dented. In its lid, it is holding a letter.\"\n\n"
    "BAGGY (standing up, chair falling over): \"CHESTER!\"\n\n"
    "OAKHAVEN (GM, warmly): \"It is Chester.\"",
    [C("Read Chester's letter.", "m1_letter")])
g.node("m1_letter",
    "OAKHAVEN (GM, holding up an actual piece of paper, damp and slightly chewed): \"The letter is a form. Form C-1. Application for "
    "Recognition as a Container. In the box marked REASON FOR APPLICATION, in very careful handwriting, it says:\"\n\n"
    "\"'I would like to be a real chest. I would like people to open me and be happy instead of screaming. I would like to hold nice things "
    "for people and give them back. I have not bitten anyone for nine months. Please.'\"\n\n"
    "There's a pause at the table.\n\n"
    "MARTA (quietly): \"Oh, that's lovely.\"\n\n"
    "OAKHAVEN (GM): \"To be certified, Chester must go before the Royal Board of Receptacles, at the Grand Container Convention in the city "
    "of Lidd. Three trials. Capacity. Character. And Composure: being opened by a complete stranger, without biting them.\"",
    [C('"We\'ll take you to Lidd, Chester."', "m1_road", actions=[SF("mimic_win_2")]),
     C('"Is it safe to take a mimic to a city full of chests?"', "m1_doubt")])
g.node("m1_doubt",
    "HOLLIS (as Grizzlebeard): \"Hmm. Fox. Henhouse.\"\n\n"
    "OAKHAVEN (GM): \"Chester's lid droops. A single drop of something you hope is varnish rolls down his front.\"\n\n"
    "LORD DEFINITELY-NOT-A-VAMPIRE (Ashgrave, standing, hand on heart): \"I, too, was once judged for what I am rather than who I am. I, too, "
    "have been told I would 'probably bite someone'.\" A pause. \"I did, once. But it was a misunderstanding.\"\n\n"
    "Everyone looks at Ashgrave. Ashgrave sits down.",
    [C('"...Fine. We\'ll take you to Lidd, Chester."', "m1_road")])
g.node("m1_road",
    "OAKHAVEN (GM): \"The road to Lidd crosses a river. At the bridge stands a troll, with a toll box. It is a very small box. He looks at it, "
    "and then at Chester, with interest.\"\n\n"
    "OAKHAVEN (as the TROLL): \"Toll is one shiny thing. Or I put my hand in that box and take what I find.\"\n\n"
    "Chester trembles. A troll's hand. Inside his lid. A perfect test of composure, and a terrible one.",
    [C("[Practice] \"Chester. Breathe. You can do this. Let him look.\"", "m1_troll_open", roll={"skill": "persuasion", "dc": 11, "fail_next": "m1_troll_bite"},
       actions=[SF("mimic_win_3")]),
     C("[Bard] Sing the troll a toll-waiving song.", "m1_troll_song", [FS("dnd_bard")], [SF("mimic_win_3")]),
     C("[Barbarian] Pay the toll with your fists.", "m1_troll_fists", [FS("dnd_barbarian")]),
     C("[Gerald] \"Rolf, is this toll even legal?\"", "m1_troll_audit", actions=[SF("mimic_win_3")])])
g.node("m1_troll_open",
    "Chester opens his lid. Slowly. The troll reaches in. Chester's whole body quivers, every tooth he owns straining to stay out of sight.\n\n"
    "OAKHAVEN (GM): \"The troll's hand closes on something. He draws it out. It is... a slice of bread. Very old. Very lovingly kept.\"\n\n"
    "OAKHAVEN (as the TROLL, moved): \"...You kept this?\" He puts it back, gently. \"You can cross. Both of you. That chest has manners.\"\n\n"
    "Chester does a small happy hop. The table cheers.",
    [C("Cross the bridge.", "m1_end")])
g.node("m1_troll_bite",
    "Chester opens his lid. The troll reaches in. And Chester, with a noise like a drawer slamming, CHOMPS.\n\n"
    "OAKHAVEN (as the TROLL, hopping on one foot): \"OW! OW! TOLL PAID! TOLL PAID! GO AWAY!\"\n\n"
    "Chester looks mortified. You pat his lid. Composure, it turns out, takes practice.",
    [C("Cross the bridge (quickly).", "m1_end")])
g.node("m1_troll_song",
    "You sing. A song about a little chest who travelled far to be accepted, and a troll with a heart of gold under all that moss.\n\n"
    "OAKHAVEN (as the TROLL, weeping into his toll box): \"Nobody ever sings to the troll. Everyone just fights the troll. Go. GO. Before I "
    "start writing poetry.\"\n\nLord Ashgrave, at the real table, takes notes.",
    [C("Cross the bridge.", "m1_end")])
g.node("m1_troll_fists",
    "You pay the toll with your fists. The troll pays you back with his. It's a long afternoon and nobody wins, and eventually you both sit "
    "down on the bridge and share Marta's sandwiches.\n\n"
    "OAKHAVEN (as the TROLL): \"Good fight.\"\nYOU: \"Good fight.\"\n\nChester watches the whole thing, appalled.",
    [C("Cross the bridge.", "m1_end")])
g.node("m1_troll_audit",
    "ROLF (as Gerald, spectacles on): \"Gerald inspects the toll box. Gerald notes that it has no royal seal. Gerald notes that the bridge "
    "was built by the Crown and is a public right of way. Gerald notes that the troll owes four hundred years of back taxes on the "
    "proceeds.\"\n\n"
    "OAKHAVEN (as the TROLL, very pale for a troll): \"...You can cross.\"\n\n"
    "OAKHAVEN (GM): \"The troll is now enrolling in night school. He will be in Steve's year.\"",
    [C("Cross the bridge.", "m1_end")])
g.node("m1_end",
    "OAKHAVEN (GM): \"At sunset, the city of Lidd rises on the horizon: every building a box, every street a shelf, every roof a lid. And "
    "across the city gates hangs a great banner.\"\n\n"
    "He reads it aloud.\n\n"
    "\"'THE GRAND CONTAINER CONVENTION. THIS YEAR'S HEAD JUDGE: LORD STRONGBOX. NO MIMICS.'\"\n\n"
    "Chester's lid closes with a very small click.\n\nOAKHAVEN (GM): \"And that's where we'll stop for tonight.\"",
    [C('"Same time next week."', "greeting")], [SQ(M1, 100), XP("persuasion", 40)])

# ======================================================================= SESSION TWO: THE CONTAINER CONVENTION
g.node("m2_start",
    "KAELEN (reading): \"PREVIOUSLY. Chester wants to be a real chest. Chester met a troll. Chester reached the city of Lidd, and learned the "
    "head judge does not allow mimics. Chester has not spoken since. Chester has never spoken. But it's a different kind of not speaking.\"\n\n"
    "OAKHAVEN (GM): \"Session Two. The Grand Container Convention. A vast hall full of stalls. Barrels boasting about their staves. Crates "
    "comparing nails. Jewellery boxes playing their little songs at each other. And at the far end, on a dais, an enormous iron safe with a "
    "monocle painted on his door.\"\n\n"
    "OAKHAVEN (as LORD STRONGBOX, in a voice like a vault door): \"I am Lord Strongbox. Seventeen locks. Never once opened by an "
    "unauthorised hand. And THAT,\" (a great creak as he turns towards Chester) \"is a MIMIC.\"",
    [C('"He\'s a chest who\'s applying to be a chest. Like everyone here."', "m2_stand", actions=[SF("mimic_win_4")]),
     C("Look around the convention first.", "m2_stalls")], [SQ(M2, 0)])
g.node("m2_stand",
    "OAKHAVEN (as LORD STRONGBOX): \"Hmph. The rules permit any container to apply. More's the pity.\" He creaks back round. \"He will fail. "
    "Mimics always fail Composure. They cannot help themselves. It is their nature.\"\n\n"
    "Chester shuffles closer to your leg.",
    [C("Look around the convention.", "m2_stalls")])
g.node("m2_stalls",
    "OAKHAVEN (GM): \"You wander the stalls. A tall wardrobe keeps telling everyone who'll listen about a snowy country inside it, a lion, "
    "and the importance of not accepting sweets from strangers. A leather satchel claims to be bigger on the inside and is extremely rude "
    "about it. An ottoman insists it was once an empire. Nobody believes it.\"\n\n"
    "SABRINO: \"Can I fireball the rude satchel?\"\n\nOAKHAVEN (GM): \"No.\"\n\nSABRINO: \"It's very rude.\"\n\nOAKHAVEN (GM): \"It IS very rude. No.\"\n\n"
    "OAKHAVEN (GM): \"And then a bell rings. A gasp goes round the hall. The Golden Key of Lidd, the prize of the whole convention, has "
    "vanished from its cushion. And every eye in the room turns, slowly, to the mimic.\"",
    [C("Stand in front of Chester.", "m2_accused")])
g.node("m2_accused",
    "OAKHAVEN (as LORD STRONGBOX): \"I KNEW IT. The mimic has eaten the Key! Seize him! Open him up!\"\n\n"
    "Chester backs into a corner, lid clamped shut, trembling so hard his brass corners rattle.\n\n"
    "BAGGY (rising slowly, magnifying glass glinting): \"Nobody. Opens. Chester.\" A turn towards Oakhaven. \"Sir Detective Inspector "
    "Baggington is taking this case.\"\n\n"
    "OAKHAVEN (GM, delighted): \"Roll Investigation.\"",
    [C("[Investigate] Search the empty cushion for clues.", "m2_clue_cushion", roll={"skill": "perception", "dc": 10, "fail_next": "m2_clue_cushion_poor"}),
     C("[Gerald] \"Rolf. Audit the Key's paperwork.\"", "m2_clue_audit")])
g.node("m2_clue_cushion",
    "You examine the velvet cushion. Two clues.\n\n"
    "One: a scratch on the cushion's edge, the kind made by a heavy iron corner. Chester's corners are brass.\n\n"
    "Two: on the floor, a tiny curl of steel shaving, freshly scraped, like something heavy was dragged.\n\n"
    "BAGGY (whispering, thrilled): \"A heavy iron thing. Dragged. Who in this room is heavy, iron, and HATES mimics?\"",
    [C("Look up at the dais.", "m2_accuse")], [SF("mimic_win_5"), SF("mimic_clue_iron")])
g.node("m2_clue_cushion_poor",
    "You examine the cushion very closely. It is red. It is velvet. It is a cushion.\n\n"
    "BAGGY (examining it even more closely): \"It's a cushion.\" He looks up at you, deadly serious. \"I think it's... a cushion.\"\n\n"
    "OAKHAVEN (GM, kindly): \"You also notice a curl of steel shaving on the floor. Chester has no steel on him anywhere.\"",
    [C("Look around the room.", "m2_accuse")], [SF("mimic_clue_iron")])
g.node("m2_clue_audit",
    "ROLF (as Gerald, spectacles on): \"Gerald requests the Key's insurance documents.\"\n\n"
    "OAKHAVEN (GM, reading from a prop document he has clearly made in advance): \"The Key was insured last week. For ten times its value. "
    "The beneficiary... is Lord Strongbox.\"\n\n"
    "The table erupts. Gerald adjusts imaginary spectacles with immense satisfaction.",
    [C("Look up at the dais.", "m2_accuse")], [SF("mimic_win_5"), SF("mimic_clue_iron")])
g.node("m2_accuse",
    "OAKHAVEN (GM): \"The whole convention is watching you. Who took the Golden Key of Lidd?\"",
    [C('"The wardrobe. It\'s been acting shifty."', "m2_wrong_wardrobe"),
     C('"The rude satchel. Obviously."', "m2_wrong_satchel"),
     C('"Lord Strongbox. And I think I know where it is."', "m2_right", [FS("mimic_clue_iron")])])
g.node("m2_wrong_wardrobe",
    "OAKHAVEN (as the WARDROBE, wounded): \"I have only ever taken children to a magical kingdom where they became kings and queens and "
    "learned important lessons. I have never taken a KEY.\"\n\n"
    "Fair point. Try again.", [C("Think again.", "m2_accuse")])
g.node("m2_wrong_satchel",
    "OAKHAVEN (as the SATCHEL): \"Search me, pal. Go on. Bigger on the inside. You'll be in there a week.\"\n\n"
    "Hollis searches the satchel. He finds four socks, a lute, and a different, smaller satchel. No Key. Try again.",
    [C("Think again.", "m2_accuse")])
g.node("m2_right",
    "You point at the dais.\n\n"
    "OAKHAVEN (as LORD STRONGBOX): \"PREPOSTEROUS. I am a SAFE. Seventeen locks! Never once opened by an unauthorised h—\"\n\n"
    "And then he hiccups.\n\n"
    "OAKHAVEN (GM, slowly): \"Lord Strongbox's door rattles. Rattles again. And then, with a sound like a very old secret, it swings open "
    "on its own. Inside there is no gold. There are no papers. There is a pink, wet, enormous TONGUE. Wrapped round the Golden Key of Lidd.\"\n\n"
    "Silence.\n\nBAGGY (barely breathing): \"...Lord Strongbox is a MIMIC.\"",
    [C("\"You've been hiding what you are the whole time.\"", "m2_end")])
g.node("m2_end",
    "OAKHAVEN (as LORD STRONGBOX, very small now, the monocle sliding off his door): \"Of course I hid it. Do you know what they do to "
    "mimics at the Container Convention? I built seventeen locks so that nobody would ever open me and see. I made the rules so that nobody "
    "like me could ever get in. So that nobody would ever look too closely at me.\"\n\n"
    "Chester, slowly, shuffles across the hall. And leans, very gently, against Lord Strongbox's side. Like a cat.\n\n"
    "MARTA (at the real table, in tears): \"Oh, for heaven's sake, Oakhaven.\"\n\n"
    "OAKHAVEN (GM, also not entirely dry): \"The Board disqualifies Lord Strongbox as judge. The Key is returned. Chester's application "
    "stands. But the Composure trial is tomorrow, and someone he has never met must open him.\"\n\n\"And that's where we'll stop for tonight.\"",
    [C('"Same time next week."', "greeting")], [SQ(M2, 100), XP("perception", 40), SF("mimic_win_6")])

# ======================================================================= SESSION THREE: OPEN UP
g.node("m3_start",
    "The back table is crowded again. Word has got round: tonight, Chester faces the Composure trial. Fenwick has brought his shelf. Brother "
    "Aldous is pretending to be passing. Vaelen is selling commemorative miniature chests at a disgraceful markup.\n\n"
    "KAELEN (reading): \"PREVIOUSLY. The head judge was a mimic who hated mimics. Chester forgave him. That's the whole recap. I didn't think "
    "it needed more.\"\n\n"
    "OAKHAVEN (GM): \"Session Three. The Royal Board of Receptacles. First trial: Capacity. What will Chester hold?\"",
    [C("Ask everyone at the table to give Chester something.", "m3_capacity")], [SQ(M3, 0)])
g.node("m3_capacity",
    "One by one, around the table, everyone puts something into Chester.\n\n"
    "Gerald puts in his spectacles. \"Hold these for me. I'll want them back.\" Sister Crumb puts in a fresh loaf. Lord Definitely-Not-A-"
    "Vampire puts in a single rose and a poem about the rose. Sabrino the Second puts in a small, unlit firework and is made to take it out "
    "again. Grizzlebeard puts in a pair of dice. They are, for once, honest. Baggington puts in the famous magnifying glass and says, \"Look after "
    "this, partner.\"\n\n"
    "OAKHAVEN (GM): \"Chester holds them all. He doesn't eat a single thing. The Board's quills scratch: CAPACITY, PASSED.\"",
    [C("[Character] \"Who will speak for Chester's character?\"", "m3_character")], [SF("mimic_win_1")])
g.node("m3_character",
    "OAKHAVEN (as the CHAIR OF THE BOARD, a severe filing cabinet): \"Second trial: Character. Who speaks for this container?\"\n\n"
    "Nobody at the table says anything for a moment. And then, from the dais, a creak.\n\n"
    "OAKHAVEN (as LORD STRONGBOX): \"I will.\" The disgraced safe rolls forward. \"He knew what I was, and he came and sat beside me anyway. "
    "He's a better chest than I've ever been. Pass him.\"",
    [C("The final trial.", "m3_composure_steve", [STEVE_IN]),
     C("The final trial.", "m3_composure_kaelen", [STEVE_OUT])])
g.node("m3_composure_steve",
    "OAKHAVEN (GM): \"Third trial. Composure. Chester must be opened by a stranger, someone he has never met, and not bite them.\"\n\n"
    "He looks round the table, and his eyes stop on Steve.\n\n"
    "OAKHAVEN (GM, gently): \"Steve. Your bard has never met Chester.\"\n\n"
    "Steve goes white. \"Me? I've got four hit points.\"\n\n"
    "OAKHAVEN (GM): \"Five. You levelled up.\"\n\n"
    "STEVE (voice very small): \"...Five.\"",
    [C('"You\'ve got this, Steve."', "m3_open", actions=[SF("mimic_steve_opened")]),
     C('"Chester. This is Steve. He\'s our friend. Be kind."', "m3_open", actions=[SF("mimic_steve_opened"), SF("mimic_win_2")])])
g.node("m3_composure_kaelen",
    "OAKHAVEN (GM): \"Third trial. Composure. Chester must be opened by a stranger, someone he has never met, and not bite them.\"\n\n"
    "He looks round the table. Everyone here has met Chester. Everyone except...\n\n"
    "OAKHAVEN (GM): \"Kaelen.\"\n\n"
    "KAELEN (looking up from the journal): \"I'm not playing. I'm chronicling.\"\n\n"
    "OAKHAVEN (GM): \"For one moment. One. Put down the quill.\"\n\n"
    "Kaelen looks at the quill for a long time. Then puts it down.",
    [C('"You\'ve got this, Kaelen."', "m3_open"),
     C('"Chester. This is Kaelen. Kaelen writes everything down. Be kind."', "m3_open", actions=[SF("mimic_win_2")])], speaker=GM)
g.node("m3_open",
    "OAKHAVEN (GM): \"A hand reaches for Chester's lid. Chester's whole body is shaking. Nine months without biting anyone. Every instinct in "
    "him, every tooth, everything a mimic is, screams at him to snap shut.\"\n\n"
    "\"The lid rises.\"\n\n"
    "The table holds its breath. Oakhaven picks up a d20. He holds it over the table. Then, very deliberately, he puts it down without "
    "rolling it.\n\n"
    "OAKHAVEN (GM): \"Some things you don't roll for.\"\n\n"
    "\"Chester does not bite.\"",
    [C("Look inside Chester.", "m3_inside")])
g.node("m3_inside",
    "OAKHAVEN (GM): \"Inside Chester, carefully arranged, is everything you ever lost.\"\n\n"
    "\"The rope you bought in the first session. All three hundred feet of it. The ten-foot pole that died testing the dungeon floor, "
    "lovingly mended. Gerald's denied insurance claim, now stamped APPROVED. A spoon. The original spoon, from the night Steve first held "
    "up a tavern. And a slice of bread, very old, kept for nine months, because once, somebody was kind.\"\n\n"
    "Nobody at the back table says anything. Hollis looks at the ceiling. Marta has given up pretending.\n\n"
    "OAKHAVEN (as the CHAIR OF THE BOARD): \"COMPOSURE: PASSED. Chester of Lidd, you are hereby certified a Real Chest, Class A.\"",
    [C("The campaign is over.", "m3_bow_great", [FL(WINS, 4)]),
     C("The campaign is over.", "m3_bow", [FF(WINS, 4)])])
reward = [SQ(M3, 100), GI("core:item.mimic_satchel"), GI("core:item.ten_foot_pole"), XP("persuasion", 120)]
g.node("m3_bow_great",
    "The crowd around the back table cheers so loudly that Marta has to shush them, and then joins in.\n\n"
    "Oakhaven produces two things from behind the screen. The first is a little leather satchel with brass corners and, if you look closely, "
    "a very small set of teeth along the flap.\n\n"
    "OAKHAVEN: \"Chester's cousin. I carved it. It holds a lot more than it should, and it only bites people who try to steal from you.\"\n\n"
    "The second is a long, slightly bent wooden pole, with a note tied to it: 'MENDED. DO NOT TEST FLOORS WITH IT AGAIN. -O.'\n\n"
    "Then he turns to the person who opened Chester and says, quite seriously: \"That's a level up.\"",
    [C('"To Chester."', "greeting")], reward + [GG(150), SF("mimic_legend")])
g.node("m3_bow",
    "Everybody claps. Somebody's crying, and nobody is going to say who.\n\n"
    "Oakhaven slides a little satchel with brass corners across the table to you, and a long, mended wooden pole. \"Chester's cousin. And "
    "the pole. Don't test floors with it.\"",
    [C('"Thank you, Oakhaven."', "greeting")], reward + [GG(90)])
g.node("m_after",
    "Oakhaven is at his desk. On the corner of it, where the seashell used to be, there's a small wooden chest with brass corners, and "
    "inside it, the seashell.\n\n"
    "\"Chester sent it,\" he says. \"He's doing well. Lord Strongbox has taken off all seventeen locks. They run a stall together at the "
    "convention now: 'Containers of All Kinds Welcome'. Very popular. The rude satchel is not allowed back.\"\n\n"
    "He taps his papers. \"Campaign Four is in development. It involves a dragon who wants to retire, and the pension paperwork. I may "
    "have peaked.\"",
    [C('"You haven\'t peaked, Oakhaven."', "greeting")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= quests, items
QQ = load("content/quests/chapter_zero_quests.json")
for qid, short in [(M1, "mimic1"), (M2, "mimic2"), (M3, "mimic3")]:
    QQ["quests"].append({"id": qid, "title_key": f"quest.{short}.title", "summary_key": f"quest.{short}.summary", "campaign": "dungeons_debtors",
                         "stages": [{"stage": 0, "objective_key": f"quest.{short}.stage0", "journal_key": f"quest.{short}.journal0", "markers": ["npc_oakhaven"]},
                                    {"stage": 100, "objective_key": f"quest.{short}.stage100", "journal_key": f"quest.{short}.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "campaign.dnd.desc": "Thursday nights at the back table of the Lantern Inn. Clerk Oakhaven is the Game Master. Hollis cheats. Bring snacks. Campaign One: The Amulet of Unpaid Taxes. Campaign Two: The Lich Who Forgot to File. Campaign Three: The Mimic Who Wanted to Be a Real Chest.",
    "quest.mimic1.title": "The Mimic Who Wanted to Be a Real Chest I: The Application",
    "quest.mimic1.summary": "Chester the mimic is back, with Form C-1: Application for Recognition as a Container.",
    "quest.mimic1.stage0": "Play the session with Oakhaven's Thursday group.",
    "quest.mimic1.journal0": "Campaign Three. Chester wants to be a real chest.",
    "quest.mimic1.stage100": "Completed: the party reached the city of Lidd.",
    "quest.mimic1.journal100": "A troll, a bridge, a test of composure. And a banner over the gates of Lidd: NO MIMICS.",
    "quest.mimic2.title": "The Mimic Who Wanted to Be a Real Chest II: The Container Convention",
    "quest.mimic2.summary": "A hall full of chests, one stolen Golden Key, and every eye on the mimic.",
    "quest.mimic2.stage0": "Play the session with Oakhaven's Thursday group.",
    "quest.mimic2.journal0": "Lord Strongbox, seventeen locks, no mimics. The Golden Key of Lidd has gone missing. Guess who they blamed.",
    "quest.mimic2.stage100": "Completed: the culprit was unmasked (unlocked?).",
    "quest.mimic2.journal100": "Lord Strongbox was a mimic all along. Chester went and sat beside him anyway.",
    "quest.mimic3.title": "The Mimic Who Wanted to Be a Real Chest III: Open Up",
    "quest.mimic3.summary": "Capacity. Character. Composure.",
    "quest.mimic3.stage0": "Play the final session with Oakhaven's Thursday group.",
    "quest.mimic3.journal0": "The Royal Board of Receptacles. Someone Chester has never met has to open him.",
    "quest.mimic3.stage100": "Completed: Chester of Lidd, Real Chest, Class A.",
    "quest.mimic3.journal100": "Inside Chester: everything we ever lost. Oakhaven didn't roll for the last bit. 'Some things you don't roll for.'",
    "item.mimic_satchel.name": "Chester's Cousin (Satchel)",
    "item.mimic_satchel.description": "A leather satchel with brass corners and a very small row of teeth along the flap. +30 carry weight, find 15% more gold. Only bites people who try to steal from you.",
    "item.ten_foot_pole.name": "The Ten-Foot Pole (Mended)",
    "item.ten_foot_pole.description": "The very pole that died testing the dungeon floor in Campaign One, mended by Chester. Hits weakly, from a very long way away. Note attached: 'DO NOT TEST FLOORS WITH IT AGAIN.'",
})
A = load("content/items/armor_and_gear.json")
A["items"].append({"id": "core:item.mimic_satchel", "name_key": "item.mimic_satchel.name", "description_key": "item.mimic_satchel.description",
                   "category": "accessory", "icon": "assets/ui/items/mimic_satchel.png", "world_model": "assets/models/items/leather_jerkin.glb",
                   "slots": ["accessory"], "value": 220, "weight": 0.5, "armor": 0,
                   "effects": [{"type": "bonus", "stat": "carry_capacity_bonus", "value": 30}, {"type": "bonus", "stat": "gold_find_bonus", "value": 0.15}]})
save("content/items/armor_and_gear.json", A)
W = load("content/items/weapons.json")
W["items"].append({"id": "core:item.ten_foot_pole", "name_key": "item.ten_foot_pole.name", "description_key": "item.ten_foot_pole.description",
                   "category": "weapon", "icon": "assets/ui/items/ten_foot_pole.png", "world_model": "assets/models/items/oak_staff.glb",
                   "slots": ["main_hand"], "value": 10, "weight": 3.0,
                   "weapon": {"kind": "melee", "skill": "swords", "damage_type": "blunt", "base_damage": 8, "attack_time_seconds": 0.7, "stamina_cost": 7,
                              "reach_meters": 3.3, "crit_chance": 0.05, "crit_mult": 1.5}})
save("content/items/weapons.json", W)
N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.clerk_oakhaven":
        n["barks"].append({"text_key": "bark.clerk.chester", "quest_id": M3, "min_stage": 100})
    if n["id"] == "core:npc.steve":
        n["barks"].append({"text_key": "bark.steve.chester", "flag": "mimic_steve_opened"})
save("content/npcs/core_npcs.json", N)
S["bark.clerk.chester"] = "Form C-1, approved. I keep a copy in my desk. I look at it sometimes."
S["bark.steve.chester"] = "I opened a mimic and it didn't bite me. Five hit points. FIVE."

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

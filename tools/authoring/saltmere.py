"""Case File #2: The Silence at Saltmere. A Lovecraftian case for Hollis's Hollowmere Mysteries campaign.

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends."""
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
HI = lambda i: {"type": "has_item", "item_id": i}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
XP = lambda k, a: {"type": "give_xp", "skill": k, "amount": a}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
GG = lambda a: {"type": "give_gold", "amount": a}
SQ = lambda q, s: {"type": "set_quest_stage", "quest_id": q, "stage": s}
SAN = lambda a: {"type": "sanity", "amount": a}
Q = "core:quest.saltmere"
TESTIMONY = ["saltmere_t_harbour", "saltmere_t_brine", "saltmere_t_pickering", "saltmere_t_silas"]
BELLS = ["bell_1", "bell_2", "bell_3"]


class Dlg:
    def __init__(self, did, speaker, prefix, nodes=None):
        self.id, self.speaker, self.prefix = did, speaker, prefix
        self.nodes = nodes if nodes is not None else {}

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

    def json(self):
        return {"id": self.id, "root_node": "root", "nodes": self.nodes}


def C(text, nxt, cond=None, actions=None, roll=None):
    o = {}
    if cond: o["conditions"] = cond
    if actions: o["actions"] = actions
    if roll: o["roll"] = roll
    return (text, nxt, o)


BACK = C('"Let\'s talk about something else."', "root")
LEAVE = C('"I\'ll be going."', "END")

# ======================================================================= the Harbourmaster
hm = Dlg("core:dialogue.harbourmaster", "npc.harbourmaster.name", "dlg.harbour")
hm.node("root",
    "A broad, weather-beaten man in a navy coat stands at the end of the quay, staring out into the fog. He doesn't turn "
    "round when you approach.\n\n\"If you're here to fish, don't. If you're here to sightsee, don't. If you're here to say "
    "your name out loud, for the love of all that's dry, DON'T.\"\n\nHe finally looks at you. \"Harbourmaster. That's all "
    "you'll get. That's all I am, these days.\"",
    [C('"I\'m investigating the silence in Saltmere. For Hollis the Grey."', "case", [QB(Q, 10)], [SQ(Q, 10), SF("saltmere_visited")]),
     C('"Tell me about the fog. And the tides."', "fog", actions=[SF("saltmere_t_harbour"), SF("saltmere_visited")]),
     C('"Who\'s missing from Saltmere?"', "missing", [FN("priest_name_known")]),
     C('"Your name. Say it. It\'s safe now."', "named", [FS("saltmere_resolved"), FN("harbour_named")]),
     LEAVE])
hm.node("case",
    "\"Hollis.\" A short laugh, like a rope snapping. \"Good. He's the only one in the Marches mad enough.\"\n\n"
    "\"Here's your case. Six weeks ago, the fog came in and didn't leave. The tide started coming in nine minutes late. "
    "And the men stopped saying their names. Not just the fishermen. All of us. You say your name on Saltmere quay, and "
    "something out there,\" he nods at the fog, \"writes it down.\"\n\n"
    "\"Talk to Mother Brine at the Drowned Lantern. The professor in her back room. Old Silas at the end of the north pier, "
    "if he's still talking. And then you tell me what's under my harbour.\"",
    [BACK], [SF("saltmere_t_harbour")])
hm.node("fog",
    "\"The fog came in on a Tuesday. It never goes out. It just thins, sometimes, enough to let you see what's standing in "
    "it.\" He doesn't elaborate on what's standing in it. He doesn't have to; out past the piers, through the grey, there "
    "are shapes too tall to be masts, and they are not quite still.\n\n"
    "\"The tide comes in nine minutes late and goes out nine minutes early. Every day. Something is drinking it. Or "
    "counting it.\" He spits into the water. \"The bells started last week. Under the water. You'll hear them at night.\"",
    [BACK], [SAN(-3)])
hm.node("missing",
    "The Harbourmaster is quiet for a long time.\n\n\"My brother.\" He grips the rail. \"Joined the Order a month ago. "
    "Said the Deep would carry his name for him so he'd never have to be afraid of losing it. He gave it to them. Walked "
    "down under the fish warehouse and never came back up.\"\n\n"
    "He takes your hand, turns it palm up, and with a wet fingertip writes a word on it. He won't say it aloud. He just "
    "looks at you until you read it.\n\nEZEKIEL.\n\n\"If you find him,\" he says, \"remind him.\"",
    [C('"I will."', "root")], [SF("priest_name_known"), SF("saltmere_t_harbour")])
hm.node("named",
    "He opens his mouth. Closes it. Looks at the fog, which is thinner today than it has been in six weeks, thin enough to "
    "see the actual sea.\n\n\"Wick,\" he says. Then louder: \"Josiah Wick.\" Then he shouts it, at the water, at the whole "
    "grey horizon: \"JOSIAH WICK! HARBOURMASTER OF SALTMERE!\"\n\nNothing answers. Nothing writes it down. He laughs, and "
    "doesn't stop for a while.",
    [C('"Pleased to meet you, Josiah."', "root")], [SF("harbour_named"), XP("persuasion", 40)])

# ======================================================================= Mother Brine
mb = Dlg("core:dialogue.mother_brine", "npc.mother_brine.name", "dlg.brine")
mb.node("root",
    "A tiny, ancient woman with forearms like ship's rope is wiping down the bar with a rag that has seen things.\n\n"
    "\"Sit down, dearie, you're dripping on my floor. Chowder's two coppers. Ale's three. Don't tell me your name, I don't "
    "want it, it's bad for business.\" She squints at you. \"You've got the look of somebody nobody remembers. Lucky you. "
    "Around here that's practically armour.\"",
    [C('"What\'s happening to Saltmere, Mother Brine?"', "town", actions=[SF("saltmere_t_brine")]),
     C('"What do you know about the Esoteric Order of the Drowned Ledger?"', "order", actions=[SF("saltmere_t_brine")]),
     C('"I\'ll have some chowder."', "END", actions=[{"type": "open_shop"}]),
     C('"Can I rest here a while?"', "rest", actions=[{"type": "heal_player"}]),
     LEAVE])
mb.node("town",
    "\"What's happening?\" She snorts. \"Same thing that happens every eighty years or so, dearie. The fog comes, the "
    "tides go funny, folk start hearing bells, and the young ones start thinking the sea's got something better to offer "
    "than a hard day's fishing and a bowl of my chowder.\"\n\n"
    "\"My grandmother saw it. Her grandmother saw it. Every time, it takes a few. Every time, the rest of us shut our "
    "mouths and wait for it to go back to sleep.\" She slams the rag down. \"I'm ninety-one and I'm tired of waiting.\"",
    [BACK], [SAN(-2)])
mb.node("order",
    "\"The Esoteric Order of the Drowned Ledger.\" She says it the way you'd say the name of a skin rash. \"Started as a "
    "fishermen's burial club. Pay a copper a week, the club buries you proper when the sea takes you. Then somebody found "
    "an old book in a net.\"\n\n"
    "\"Now they meet under Gale and Sons' fish warehouse every tide. They take their names off, like hats. They say "
    "there's something out past the shelf that eats names, and if you give it yours freely, it'll keep you forever.\"\n\n"
    "She leans in. \"I've seen what it keeps, dearie. It keeps the eyes.\"",
    [BACK], [SAN(-4)])
mb.node("rest",
    "You sit by the fire with a bowl of chowder so thick the spoon stands up in it. Mother Brine sings something under her "
    "breath, an old shanty, off-key. The bells under the water are very far away. For a while you remember, clearly and "
    "easily, exactly who you are.",
    [C('"Thank you."', "root")])

# ======================================================================= Professor Pickering
pk = Dlg("core:dialogue.professor_pickering", "npc.professor_pickering.name", "dlg.pickering")
pk.node("root",
    "A rumpled scholar in a stained travelling coat sits hunched over a table covered in notes, sketches of fish, and a "
    "great many empty cups. He looks up with red-rimmed eyes.\n\n"
    "\"Ah! A visitor! A sane one, by the look of you. Or sane-ish. Sit, sit.\" He sweeps a pile of papers off a chair, "
    "onto a different pile of papers. \"Professor... Professor...\" He stops. A long, awful pause. \"...I had it a moment "
    "ago. Department of Unusual Studies. The Collegium. I'm here to study the phenomenon. The phenomenon is studying me back.\"",
    [C('"What phenomenon, Professor?"', "phenomenon", actions=[SF("saltmere_t_pickering")]),
     C('"What\'s that idol in your notes?"', "idol", [HI("core:item.fish_idol")]),
     C('"What do you make of it all, Professor? I\'ve heard from the Harbourmaster, Mother Brine and Silas."', "theory",
       [QE(Q, 10), FL(TESTIMONY, 3)]),
     C('"Your name is Ambrose Pickering."', "named", [FS("pickering_notes_read"), FN("pickering_named")]),
     LEAVE])
pk.node("phenomenon",
    "\"Where to BEGIN.\" He grips the table. \"The angles are wrong. I've measured the quay six times. The corners add up to "
    "three hundred and sixty-one degrees. ONE degree too many. Where does it GO?\"\n\n"
    "\"The fog has a smell. Not of the sea. Of old paper. Of ink. Of a library left underwater for a thousand years. And "
    "at night, the bells. Bronze, under the harbour, rung by nothing, and with every stroke, I feel something very large "
    "turn a page.\"\n\n"
    "He seizes your sleeve. \"I have read, in the Collegium's sealed stacks, of a thing that dwells beyond the edge of the "
    "world and finds its way in through names. The old texts call it the Hunger. The fishermen here call it the Name-Eater. "
    "And I believe, I am very nearly certain, that it is dreaming directly beneath us.\"\n\nHe lets go. \"Tea?\"",
    [BACK], [SAN(-5), XP("lore", 20)])
pk.node("idol",
    "You set the fish-shaped idol on the table. Pickering recoils so violently he falls off his chair.\n\n"
    "\"Don't- it's- put it- PUT IT DOWN.\" From the floor: \"It's warm, isn't it. They're always warm. That's the "
    "worst part. Cold, you could stand. Warm means it's been HELD.\"\n\n"
    "He climbs back up and studies it through a magnifying lens, very carefully, without touching. \"The script on its "
    "belly is the same as the hymn the Order sings. 'What is struck out, it cannot see.' Whatever this thing is, it's blind "
    "to the things that have been erased.\" He looks up at you slowly. \"You said your name was... what was your name?\"\n\n"
    "You tell him you're legally dead. His eyes go very wide.",
    [BACK], [SAN(-3), XP("lore", 30), SF("pickering_idol")])
pk.node("theory",
    "Pickering lays his notes out across the table like a map, and as you tell him what you've heard, he connects them with "
    "string, pins, and a frankly unnecessary amount of red ink.\n\n"
    "\"The fog. The late tides. The bells. A burial club that became a cult. Men handing over their names like coats at a "
    "party.\" He stabs the warehouse on his map. \"They're FEEDING it. Every name they give to the sea is a door it can "
    "open. And when it has enough doors...\"\n\n"
    "He doesn't finish the sentence. He doesn't need to.\n\n"
    "\"The meetings are under Gale and Sons' fish warehouse. The cellar gate is locked. Silas Gale has the only key, and "
    "Silas Gale has not been entirely himself since the fog came.\" He presses a hand to his forehead. \"Neither have I. "
    "Go. Quickly. Before I forget why I'm telling you.\"",
    [C('"Thank you, Professor."', "root")], [SQ(Q, 20), XP("lore", 50)])
pk.node("named",
    "\"Ambrose,\" he repeats, very slowly. \"Ambrose Pickering.\" The colour comes back into his face, a little at a time, "
    "like a tide coming in. \"Yes. YES. Professor Ambrose Pickering, Department of Unusual Studies, the Collegium, "
    "thirty-one published monographs, two of them good.\"\n\n"
    "He grips your hand. \"You read my notes. You read my name in them. Do you know, in all my years of study, I never "
    "once considered that the cure for an eldritch horror might simply be... someone who remembers you?\" He writes it "
    "down at once.",
    [C('"You\'re welcome, Ambrose."', "root")], [SF("pickering_named"), SAN(10), XP("lore", 30)])

# ======================================================================= Silas Gale
sg = Dlg("core:dialogue.silas_gale", "npc.silas_gale.name", "dlg.silas")
sg.node("root",
    "At the very end of the north pier an old man in yellow oilskins sits with a fishing line in the water. There is no "
    "hook on the line. There has never been a hook on the line. He is singing, softly, to the fog.\n\n"
    "    \"Oh, the tide comes in, and the tide goes out,\n"
    "    and it counts us every time,\n"
    "    one for the boat and two for the net\n"
    "    and three for the drowned man's rhyme...\"\n\n"
    "He stops, and looks up at you with very pale eyes. \"You're not on the list,\" he says. \"I'd remember. I counted.\"",
    [C('"What list, Silas?"', "list", actions=[SF("saltmere_t_silas")]),
     C('"Sing me the rest of the song."', "shanty"),
     C('"I need the key to your warehouse cellar."', "key", [QA(Q, 10), FN("silas_key_given")]),
     LEAVE])
sg.node("list",
    "\"The list.\" He taps his temple. \"The sea keeps a ledger, see. Every name that's spoken over the water, it writes "
    "down. Every name that's given, it keeps. And once a lifetime, when the fog comes, it reads the ledger back.\"\n\n"
    "\"It's reading now. Down there. Can't you hear it? Silas Gale. Silas Gale. Silas Gale.\" He smiles, horribly gently. "
    "\"It's got to me twice this week. Third time, I think I'll answer.\"",
    [BACK], [SAN(-4)])
sg.node("shanty",
    "Silas closes his eyes and sings, in a cracked, true old voice:\n\n"
    "    \"Oh, the tide comes in, and the tide goes out,\n"
    "    and it counts us every time,\n"
    "    one for the boat and two for the net\n"
    "    and three for the drowned man's rhyme.\n\n"
    "    So never you say your name, my lad,\n"
    "    where the grey fog rolls ashore,\n"
    "    for the thing that sleeps where the bells still ring\n"
    "    is hungry evermore.\n\n"
    "    But the names that are struck from the ledger, lad,\n"
    "    and the souls that the books forgot,\n"
    "    they can walk the deep where the eaters sleep,\n"
    "    for the deep can see them not.\"\n\n"
    "He opens his eyes and looks straight at you. \"Funny verse, that last one. Never knew what it meant.\"",
    [BACK], [XP("lore", 20), SF("shanty_heard")])
sg.node("key",
    "Silas reaches into his oilskins and brings out a heavy iron key, crusted with salt, and holds it for a long moment "
    "without giving it to you.\n\n"
    "\"I stopped going down there,\" he says. \"They kept counting me. Every tide, one more time. I'm Gale. My father was "
    "Gale. Gale and Sons. They're down there, my sons. Wearing robes. Not saying their names.\"\n\n"
    "He puts the key in your hand and closes your fingers over it. \"If you see two lads with my nose, tell them their "
    "father's on the pier. Tell them dinner's at eight. Tell them...\" His voice cracks. \"Tell them their names.\"",
    [C('"I\'ll tell them, Silas."', "root")], [SF("silas_key_given"), GI("core:item.cellar_key"), SF("saltmere_t_silas")])

# ======================================================================= the Tide Priest (the finale)
tp = Dlg("core:dialogue.tide_priest", "npc.tide_priest.name", "dlg.priest")
tp.node("root",
    "Before the altar, at the edge of the glowing pool, stands a tall figure in sea-green robes, a crown of coral on his "
    "head, his face a fisherman's face gone grey and wet and very far away. His eyes are too large. They glow.\n\n"
    "\"Welcome,\" he says, in a voice like water in a cave. \"Welcome, nameless one. We have been waiting for you. Or rather: "
    "It has been waiting for you, and could not see you coming. Do you know how rare that is?\"",
    [C('"Who are you?"', "who"),
     C('"What is the Name-Eater?"', "eater"),
     C('"What do you want with me?"', "want", [FL(BELLS, 1)]),
     C('"The bells are silent. It\'s over."', "final", [FL(BELLS, 3), FN("saltmere_resolved")]),
     LEAVE])
tp.node("who",
    "\"I have no name. I gave it to the Deep, freely, as a gift. It was the most beautiful thing I have ever done.\" He "
    "smiles, and something moves behind his teeth. \"I am the Tide Priest of the Esoteric Order of the Drowned Ledger. I am "
    "the voice of the Ledger in this world. I am the one who reads it aloud.\"\n\n"
    "\"Once, I think, I had a brother. I cannot remember his face. It doesn't matter. Nothing that has a name matters, in "
    "the end. The Deep will have it all.\"",
    [C("Back.", "root")], [SAN(-4)])
tp.node("eater",
    "\"You call it the Hunger. The Collegium calls it a theory. The fishermen call it the Name-Eater.\" He spreads his arms "
    "to the pool, which ripples in rings. \"It dwells beyond the edge of everything, where there is nothing, and it is "
    "lonely there. It finds its way to us through names. Each name spoken is a door left open. Each name given is a door "
    "held wide.\"\n\n"
    "\"Your Archivists hid seven cities from it, four hundred years ago. Then a town called Oakhallow. They thought they were "
    "clever. We think they were cruel. Why hide from a god that only wants to know you?\"",
    [C("Back.", "root")], [SAN(-8), XP("lore", 30)])
tp.node("want",
    "The Priest walks slowly around the edge of the pool, never taking his huge, glowing eyes off you.\n\n"
    "\"Every soul in the Marches is written in some ledger. Every soul but YOU. The Bureau struck you out seventeen years "
    "ago. It cannot see you. You could walk to the very bottom of the Deep, to the place where It dreams, and It would never "
    "know you were there.\"\n\n"
    "\"Do you understand what you are? You are the only key that turns both ways. Speak your name, freely, here, into the "
    "pool, and It will see, for the first time, through the one door the Archivists left unlocked.\" He holds out a webbed "
    "hand. \"Give It your name. Be counted. Forever.\"",
    [C('"No."', "root"), C("Say nothing. Look at the pool for a long time.", "root", actions=[SAN(-6)])])
tp.node("final",
    "The Priest looks at the silent bells, one after another, and the light in his eyes flickers.\n\n"
    "\"You have stopped the count. Do you know what you have done? The Ledger is unread. It is AWAKE, and it cannot hear its "
    "names, and it is ANGRY.\" The pool begins to boil. Shapes move under the surface: long, pale, many-jointed. \"It "
    "rises. It rises for the first time in eighty years, and It will want something to eat.\"\n\n"
    "The water in the pool begins to climb, in a column, towards the ceiling.\n\nWhat do you do?",
    [C("[Fight] Draw your weapon. \"Then let it come up here and try.\"", "fight"),
     C("[Lore] Read the Drowned Hymn backwards: 'What is struck out, it cannot see, and what it cannot see, it fears.'", "hymn_win",
       [FS("hymn_read")], [SAN(-25)], roll={"skill": "lore", "dc": 14, "fail_next": "hymn_fail"}),
     C("[Ezekiel] Look the Priest in his enormous eyes and say: \"Ezekiel. Ezekiel Wick. Your brother is waiting on the quay.\"",
       "brother", [FS("priest_name_known")]),
     C("[Form 27-B] Take out your Application for Temporary Exemption from Being Dead, and feed it to the Name-Eater.", "form",
       [HI("core:item.form_27b")])])
tp.node("fight",
    "The column of water bursts. Something comes up out of the pool: a vast, heaving body of green-black flesh, a crown of "
    "pale tentacles, and eyes, so many eyes, all opening at once, all of them looking for you and not quite finding you.\n\n"
    "THE TIDE PRIEST (ecstatic): \"BEHOLD! The Avatar of the Name-Eater! Iä! IÄ!\"\n\nIt cannot see you. But it can feel "
    "where you are by the shape of the hole you make in the world. It lashes out.",
    [C("Fight!", "END")], [SF("avatar_rises"), SQ(Q, 30), SAN(-10)])
tp.node("hymn_fail",
    "You read the hymn backwards. Your tongue trips on the third line. A word comes out that was never meant for a human "
    "mouth, and the pool hears it.\n\nTHE TIDE PRIEST: \"You SPOKE to it! Oh, you beautiful fool, you spoke to it in its own "
    "tongue!\"\n\nThe water erupts, and something rises out of it.",
    [C("Fight!", "END")], [SF("avatar_rises"), SQ(Q, 30)])
tp.node("hymn_win",
    "You read the hymn backwards, every word, every impossible vowel, and your voice does not shake.\n\n"
    "    \"...fears it, see cannot it what and. See cannot it, out struck is what.\"\n\n"
    "The column of water stops climbing. It hangs there, trembling. And you understand, all at once, what the last four "
    "lines of the hymn mean, why someone tried to scratch them out: the Name-Eater is afraid of the erased. Of the things "
    "it cannot count. Of you.\n\n"
    "You step into the pool, up to your knees. It cannot see you. It can only feel a hole in the world, standing in its "
    "house, unafraid. And for the first time in its endless existence, the Hunger is the one that is afraid of the dark.\n\n"
    "The water falls. The pool goes still. Somewhere very far below, something very large curls up and goes back to sleep.",
    [C("Climb out of the pool.", "END")], [SF("saltmere_resolved"), SF("saltmere_hymn_ending"), SQ(Q, 40), XP("lore", 120),
     {"type": "narrate", "pages": [{"key": "story.saltmere.calm"}]}])
tp.node("brother",
    "\"Ezekiel,\" you say. \"Ezekiel Wick. Your brother Josiah is standing at the end of the quay. He's been standing there for "
    "a month. He wrote your name on my hand because he was too afraid to say it.\"\n\n"
    "The Tide Priest goes absolutely still. The coral crown slips sideways. His eyes, those huge, glowing eyes, are "
    "shrinking, slowly, back towards something human.\n\n"
    "\"Ezekiel,\" he whispers. \"I... Josiah. Josiah used to take me out on the boat when I was small. He let me hold the "
    "tiller.\" He looks down at his webbed hands. \"What have I done? What have I DONE?\"\n\n"
    "Behind him, the column of water wavers, and loses its shape, and falls. Without a voice to read it, the Ledger of the "
    "Deep has nothing to say. The pool goes quiet.",
    [C('"Come on, Ezekiel. Let\'s get you home."', "END")],
    [SF("saltmere_resolved"), SF("saltmere_brother_ending"), SQ(Q, 40), XP("persuasion", 120),
     {"type": "narrate", "pages": [{"key": "story.saltmere.brothers"}]}])
tp.node("form",
    "You take out Form 27-B, Application for Temporary Exemption from Being Dead, stamped, countersigned, initialled, in "
    "triplicate, and you hold it out over the boiling water.\n\n"
    "THE TIDE PRIEST: \"What... what is that?\"\n\n"
    "YOU: \"A name. Well. Lots of names. Section One alone has my name, my date of decease, my date of un-decease, and the "
    "signature of a Chief Archivist who's been dead for seventeen years.\"\n\n"
    "You drop it in the pool.\n\n"
    "The water stops boiling. Something deep below takes the form, and tries to read it, and tries to eat it, and finds that "
    "the name on it belongs to someone who is legally dead and also legally alive and also exempt, temporarily, pending "
    "review, from being either. It tries to digest a contradiction notarised in triplicate.\n\n"
    "Far below, something enormous makes a noise like a cathedral with indigestion. Then, very slowly, it sinks back into "
    "the dark, to lie down for a very, very long time.",
    [C('"Oakhaven would be so proud."', "END")],
    [SF("saltmere_resolved"), SF("saltmere_form_ending"), SQ(Q, 40), XP("persuasion", 80), XP("lore", 80),
     {"type": "narrate", "pages": [{"key": "story.saltmere.form"}]}])

# ======================================================================= Hollis: the case, and the payout
D = load("content/dialogue/chapter_zero_dialogue.json")
dl = {d["id"]: d for d in D["dialogues"]}
hol = dl["core:dialogue.hunter_hollis"]["nodes"]
g = Dlg("core:dialogue.hunter_hollis", "npc.hunter_hollis.name", "dlg.hollis.saltmere", hol)
g.node("case2",
    "Hollis lays a sodden letter on his folding card table. The seal is a fish.\n\n"
    "\"Case File Two. Saltmere. Fishing harbour, north of here, through the gap in the wall.\" He taps the letter. "
    "\"Harbourmaster writes that his men have stopped saying their names. Fog won't lift. Tide's late. Bells under the "
    "water.\"\n\n"
    "\"I've been to Saltmere. Once. Eighty years ago, with my old master.\" He's quiet for a moment. \"Hmm. We didn't fix "
    "it. We just waited till it went back to sleep.\" He pushes the letter across. \"You fix it. And whatever you hear down "
    "there, don't answer.\"",
    [C('"I won\'t answer."', "root")], [SQ(Q, 0)])
g.node("case2_done",
    "You tell Hollis everything. He listens without interrupting, his cards forgotten in his hand.\n\n"
    "\"Hmm.\" A long pause. \"Eighty years ago my master and I sat on that quay for three weeks and waited. You went DOWN.\"\n\n"
    "He reaches behind his chair and brings out a long, barbed harpoon, black iron, wrapped in old whaleskin. \"My master's. "
    "Made for exactly the thing you just put back to bed. He never got to use it. I think he'd want you to have it.\"\n\n"
    "He counts out the fee, then adds a little more. \"Case closed. Next one's on me. Literally. I'll deal.\"",
    [C('"Deal."', "root")], [SQ(Q, 100), GG(250), GI("core:item.saltmere_harpoon"), XP("lore", 60)])
ch = hol["root"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
S["dlg.hollis.saltmere.topic_case2"] = '"Got another case, Hollis?"'
S["dlg.hollis.saltmere.topic_done"] = '"Saltmere is quiet again. Case closed."'
hol["root"]["choices"] = ch[:idx] + [
    {"text_key": "dlg.hollis.saltmere.topic_case2", "conditions": [QB(Q, 0), {"type": "quest_stage_at_least", "quest_id": "core:quest.hollowmere", "stage": 20}], "next": "case2"},
    {"text_key": "dlg.hollis.saltmere.topic_done", "conditions": [QE(Q, 40)], "next": "case2_done"}] + ch[idx:]

D["dialogues"] += [hm.json(), mb.json(), pk.json(), sg.json(), tp.json()]
save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= quest
QQ = load("content/quests/chapter_zero_quests.json")
markers = {0: ["npc_harbourmaster"], 10: ["npc_brine", "npc_pickering", "npc_silas", "npc_harbourmaster"], 20: ["cellar_gate"],
           30: ["tide_bell_1", "tide_bell_2", "tide_bell_3", "npc_tide_priest", "avatar"], 40: ["npc_hollis"]}
QQ["quests"].append({"id": Q, "title_key": "quest.saltmere.title", "summary_key": "quest.saltmere.summary", "campaign": "hollowmere_mysteries",
    "stages": [dict({"stage": s, "objective_key": f"quest.saltmere.stage{s}", "journal_key": f"quest.saltmere.journal{s}"},
                    **({"markers": markers[s]} if s in markers else {}), **({"completed": True} if s == 100 else {}))
               for s in (0, 10, 20, 30, 40, 100)]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.saltmere.title": "Case File #2: The Silence at Saltmere",
    "quest.saltmere.summary": "In the fishing harbour of Saltmere, the fog won't lift, the tide comes in nine minutes late, and the fishermen have stopped saying their names.",
    "quest.saltmere.stage0": "Go north through the gap in Bellwether's wall to Saltmere Docks and find the Harbourmaster.",
    "quest.saltmere.journal0": "Hollis's second case. A fishing harbour where nobody says their name any more. He was there eighty years ago. He waited. He wants me to go down.",
    "quest.saltmere.stage10": "Find out what's happening in Saltmere: talk to the Harbourmaster, Mother Brine at the Drowned Lantern, Professor Pickering in her back room, and old Silas Gale on the north pier. Then ask the Professor what he makes of it.",
    "quest.saltmere.journal10": "Fog that never lifts. Tides nine minutes late. Bells under the water. A burial club that turned into a cult. Everyone here talks about the Name-Eater the way you'd talk about the weather.",
    "quest.saltmere.stage20": "The Order meets under Gale & Sons' fish warehouse. Get the cellar key from Silas Gale (or pick the lock) and go down.",
    "quest.saltmere.journal20": "Pickering strung it all together with red ink: the Order is feeding names to the sea, and every name is a door. Their meetings are under the fish warehouse. Silas has the only key.",
    "quest.saltmere.stage30": "Silence the three Tide Bells in the Sunken Chapel and confront the Tide Priest. Mind your sanity down there; company helps.",
    "quest.saltmere.journal30": "There's a chapel under the harbour, green with drowned light, and a pool in the middle of it that's listening. The bells are ringing on their own. Every time they ring, my head goes a little quieter, in the wrong way.",
    "quest.saltmere.stage40": "Saltmere is quiet. Report back to Hollis.",
    "quest.saltmere.journal40": "The Name-Eater has gone back to sleep. The fog is lifting. On the quay, somebody is shouting his own name at the sea, and nothing is writing it down.",
    "quest.saltmere.stage100": "Completed: Case File #2 is closed.",
    "quest.saltmere.journal100": "Hollis gave me his old master's harpoon. Eighty years ago, they waited on the quay for three weeks. This time somebody went down. I'm glad it was me. Mostly.",
    "story.sanity.break": "The bells. The bells. The count does not end. You are counted and counted again and the numbers have too many vowels in them and-\n\n...\n\nYou wake up on the cold stones of Saltmere quay, soaked through, with salt in your mouth and no memory of the last hour. Somebody has put a blanket over you. Somebody has written your name on your hand in charcoal, so you won't forget it.\n\nYou don't.",
    "story.saltmere.calm": "When you climb the stairs out of the warehouse, the fog over Saltmere is thinning. For the first time in six weeks you can see the actual sea: grey, ordinary, beautiful, and empty.\n\nThe tentacles out past the piers are gone. On the quay, a fisherman says his own name, very quietly, to see what happens. Nothing happens. He says it again, louder. Somebody laughs. Somebody else starts crying.\n\nBy evening, the whole of Saltmere is down at the Drowned Lantern, shouting their names at each other across the tables, and Mother Brine can't pour the ale fast enough.",
    "story.saltmere.brothers": "You come up out of the warehouse with Ezekiel Wick leaning on your shoulder, his robe dripping, his eyes almost human again, blinking at the light.\n\nThe Harbourmaster is at the end of the quay, where he's stood for a month. He turns. He sees. He drops the lantern he's holding.\n\n\"Ezekiel,\" he says. Out loud. On the quay. In the fog. And the fog, for the first time in six weeks, has nothing to say back.\n\nThe brothers hold each other for a very long time. Behind them, the fog lifts off the water like a sheet being pulled from a bed, and underneath it there is only sea.",
    "story.saltmere.form": "Twenty minutes later Clerk Oakhaven, in Bellwether, receives a letter delivered by a very wet seagull.\n\nIt is a standard Bureau acknowledgement slip. It reads: RECEIVED: one (1) Form 27-B, Application for Temporary Exemption from Being Dead. STATUS: Unprocessable. Applicant both deceased and not. Please resubmit in a format that does not violate the fundamental nature of reality. Yours, the Deep.\n\nOakhaven reads it three times, frames it, and hangs it on his office wall, beside his certificate for nineteen years of excellent attendance.\n\nIn Saltmere, the fog lifts. Down in the dark, something very large has a headache that will last eight hundred years.",
    "campaign.hollowmere.desc": "Hollis the Grey's case files: a haunted manor, a silent harbour, and whatever comes next, just as soon as he finishes this hand of cards.",
    "map.saltmere.name": "Saltmere Docks",
    "map.sunken_chapel.name": "The Sunken Chapel",
})

# ======================================================================= creatures
CR = load("content/creatures/core_creatures.json")
def cr(cid, appearance, hp, armor, speed, xp, beh, attack, loot, hit, lines, alert="assets/audio/sfx/crawler_hiss.wav"):
    return {"id": "core:enemy." + cid, "name_key": f"enemy.{cid}.name", "appearance": appearance,
            "stats": {"health": hp, "armor": armor, "move_speed": speed, "xp_reward": xp}, "behavior": beh, "family": "eldritch",
            "perception": {"sight_meters": 12.0, "hearing_meters": 9.0}, "attack": attack, "loot_table": loot,
            "audio": {"alert": alert, "attack": "assets/audio/sfx/spell_cast.wav", "hit": "assets/audio/sfx/sword_hit.wav",
                      "death": "assets/audio/sfx/enemy_death.wav"}, "hit_fx": hit, "lines": lines}
SP = lambda sheet, anim, scale: {"type": "sprite_8dir", "sprite_sheet": sheet, "animation_data": anim, "scale": scale}
CR["creatures"] += [
    cr("the_drowned", SP("assets/sprites/enemies/the_drowned.png", "assets/animations/skeleton.json", 1.8), 85, 3, 2.3, 45, "melee_patroller",
       {"name": "drowning_grip", "damage": 11, "reach_meters": 2.0, "windup_seconds": 0.55, "cooldown_seconds": 1.3, "sanity_damage": 3},
       "core:loot.drowned", {"color": [110, 200, 160], "glow": False},
       {"alert": "line.drowned.alert", "death": "line.drowned.death"}),
    cr("tide_acolyte", SP("assets/sprites/enemies/tide_acolyte.png", "assets/animations/crypt_keeper.json", 1.8), 65, 1, 2.0, 50, "melee_patroller",
       {"name": "brine_bolt", "damage": 9, "reach_meters": 2.0, "ranged_range_meters": 11.0, "projectile_speed": 10.0,
        "projectile_sprite": "assets/sprites/vfx/spell_ink.png", "windup_seconds": 0.7, "cooldown_seconds": 1.8, "sanity_damage": 4},
       "core:loot.drowned", {"color": [110, 255, 170], "glow": True},
       {"alert": "line.acolyte.alert", "death": "line.acolyte.death"}),
    cr("name_eater_avatar", SP("assets/sprites/enemies/name_eater_avatar.png", "assets/animations/crypt_keeper.json", 3.4), 460, 5, 1.6, 260,
       "boss_avatar",
       {"name": "unwriting", "damage": 19, "reach_meters": 3.2, "ranged_range_meters": 13.0, "projectile_speed": 9.0,
        "projectile_sprite": "assets/sprites/vfx/spell_ink.png", "windup_seconds": 0.9, "cooldown_seconds": 1.7, "sanity_damage": 6},
       "core:loot.avatar", {"color": [120, 255, 180], "glow": True},
       {"alert": "line.avatar.alert", "death": "line.avatar.death"}, alert="assets/audio/sfx/boss_roar.wav"),
]
save("content/creatures/core_creatures.json", CR)
S.update({
    "enemy.the_drowned.name": "The Drowned",
    "enemy.tide_acolyte.name": "Tide Acolyte",
    "enemy.name_eater_avatar.name": "Avatar of the Name-Eater",
    "line.drowned.alert": "...say... your... name...",
    "line.drowned.death": "...forgot... it... too...",
    "line.acolyte.alert": "Iä! A nameless one walks among us!",
    "line.acolyte.death": "The Ledger... remembers... me...",
    "line.avatar.alert": "WHERE. WHERE ARE YOU. I CANNOT COUNT YOU.",
    "line.avatar.death": "...a hole... in the ledger... ... sleep...",
})
L = load("content/loot_tables/core_loot.json")
L["loot_tables"] += [
    {"id": "core:loot.drowned", "gold_min": 4, "gold_max": 14, "entries": [{"item_id": "core:item.health_potion", "weight": 30, "min_qty": 1, "max_qty": 1},
                                                                         {"item_id": "core:item.mana_potion", "weight": 25, "min_qty": 1, "max_qty": 1},
                                                                         {"item_id": "core:item.brine_chowder", "weight": 25, "min_qty": 1, "max_qty": 1}]},
    {"id": "core:loot.avatar", "gold_min": 80, "gold_max": 140, "guaranteed": ["core:item.tide_charm"],
     "entries": [{"item_id": "core:item.mana_potion", "weight": 60, "min_qty": 1, "max_qty": 2}]},
]
save("content/loot_tables/core_loot.json", L)

# ======================================================================= items
def additem(path, e):
    d = load(path); d["items"].append(e); save(path, d)
def it(iid, cat, icon, model, val, w, **kw):
    e = {"id": "core:item." + iid, "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": model, "slots": [], "value": val, "weight": w}
    e.update(kw); return e
additem("content/items/quest_and_keys.json", it("cellar_key", "key", "cellar_key", "assets/models/items/annex_key.glb", 0, 0.1, quest_item=True))
additem("content/items/quest_and_keys.json", it("fish_idol", "misc", "fish_idol", "assets/models/items/grave_truffle.glb", 40, 0.6))
additem("content/items/weapons.json", it("saltmere_harpoon", "weapon", "saltmere_harpoon", "assets/models/items/oak_staff.glb", 280, 3.0,
        slots=["main_hand"], weapon={"kind": "melee", "skill": "swords", "damage_type": "piercing", "base_damage": 20, "attack_time_seconds": 0.62,
                                     "stamina_cost": 10, "reach_meters": 2.7, "crit_chance": 0.1, "crit_mult": 1.8, "bane_family": "eldritch", "bane_mult": 1.6}))
additem("content/items/armor_and_gear.json", it("tide_charm", "accessory", "tide_charm", "assets/models/items/ring_of_recall.glb", 180, 0.1,
        slots=["accessory"], armor=0, effects=[{"type": "stat_bonus", "stat": "will", "amount": 2}, {"type": "bonus", "stat": "sanity_regen", "value": 0.6}]))
additem("content/items/consumables_and_books.json", it("brine_chowder", "consumable", "brine_chowder", "assets/models/items/bread_loaf.glb", 8, 0.5,
        stackable=True, effects=[{"type": "consumable_heal", "amount": 22}, {"type": "buff", "stat": "sanity_regen", "value": 1.2, "duration": 300}]))
S.update({
    "item.cellar_key.name": "Gale & Sons Cellar Key",
    "item.cellar_key.description": "Heavy iron, crusted with salt. It's always slightly damp, no matter how long you keep it in your pocket.",
    "item.fish_idol.name": "Warm Fish Idol",
    "item.fish_idol.description": "A small stone fish with too many eyes, carved with script that hurts to look at. It is warm. It is always warm. Professor Pickering would want to see it, and then want you to take it away again.",
    "item.saltmere_harpoon.name": "The Old Master's Harpoon",
    "item.saltmere_harpoon.description": "Black iron, barbed, wrapped in old whaleskin. Made by Hollis's master for a thing in the deep he never got to fight. Long reach, and terrible to anything eldritch.",
    "item.tide_charm.name": "Charm of the Quiet Tide",
    "item.tide_charm.description": "A smooth grey pebble with a hole through it, strung on fishing line. Hold it to your ear and you hear only the sea, and nothing counting. +2 Will, steadies a shaken mind.",
    "item.brine_chowder.name": "Mother Brine's Chowder",
    "item.brine_chowder.description": "So thick the spoon stands up in it. Restores health, and for a while you remember, clearly and easily, exactly who you are.",
})

# ======================================================================= NPCs
N = load("content/npcs/core_npcs.json")
def npc(nid, sheet, barks, scale=1.75, **kw):
    e = {"id": "core:npc." + nid, "name_key": f"npc.{nid}.name", "title_key": f"npc.{nid}.title", "faction": "core:faction.ashbound",
         "dialogue_id": "core:dialogue." + nid,
         "appearance": {"type": "sprite_8dir", "sprite_sheet": sheet, "animation_data": "assets/animations/npc_standard.json", "scale": scale},
         "barks": barks}
    e.update(kw); return e
B = lambda k, **kw: dict({"text_key": k}, **kw)
N["npcs"] += [
    npc("harbourmaster", "assets/sprites/npcs/harbourmaster.png", [B("bark.harbour.1", not_flag="saltmere_resolved"), B("bark.harbour.2", not_flag="saltmere_resolved"), B("bark.harbour.after", flag="saltmere_resolved")]),
    npc("mother_brine", "assets/sprites/npcs/mother_brine.png", [B("bark.brine.1"), B("bark.brine.2"), B("bark.brine.after", flag="saltmere_resolved")], scale=1.55,
        vendor_inventory=[{"item_id": "core:item.brine_chowder", "stock": 10, "price": 8}, {"item_id": "core:item.health_potion", "stock": 4, "price": 20}]),
    npc("professor_pickering", "assets/sprites/npcs/professor_pickering.png", [B("bark.pickering.1"), B("bark.pickering.2"), B("bark.pickering.after", flag="pickering_named")]),
    npc("silas_gale", "assets/sprites/npcs/silas_gale.png", [B("bark.silas.1"), B("bark.silas.2"), B("bark.silas.after", flag="saltmere_resolved")]),
    npc("tide_priest", "assets/sprites/npcs/tide_priest.png", [B("bark.priest.1"), B("bark.priest.2")], scale=1.95),
]
for n in N["npcs"]:
    comp = n.get("companion")
    if not comp:
        continue
    if n["id"] == "core:npc.detective_baggy":
        comp["zone_lines"]["saltmere"] = "comp.baggy.zone.saltmere"
        comp["zone_lines"]["sunken_chapel"] = "comp.baggy.zone.sunken_chapel"
    if n["id"] == "core:npc.ashbound_scout":
        comp["zone_lines"]["saltmere"] = "comp.kaelen.zone.saltmere"
        comp["zone_lines"]["sunken_chapel"] = "comp.kaelen.zone.sunken_chapel"
        out = []
        for i, (by, text) in enumerate([
                ("partner", "Kaelen. Kaelen. Did that tentacle just move?"),
                ("self", "No."),
                ("partner", "Are you sure?"),
                ("self", "I'm writing down that it didn't. If it moves again, I'm writing that down too. That's how this works."),
                ("partner", "...It moved."),
                ("self", "I KNOW, Baggy.")]):
            key = f"comp.kaelen.banter.tentacle.{i}"
            S[key] = text
            out.append({"by": by, "text_key": key})
        comp["banter"].append({"id": "tentacle", "partner": "core:npc.detective_baggy", "lines": out, "flag": "saltmere_visited",
                               "not_flag": "saltmere_resolved"})
save("content/npcs/core_npcs.json", N)
S.update({
    "npc.harbourmaster.name": "The Harbourmaster",
    "npc.harbourmaster.title": "Saltmere Harbour (Name Withheld)",
    "npc.mother_brine.name": "Mother Brine",
    "npc.mother_brine.title": "Keeper of the Drowned Lantern",
    "npc.professor_pickering.name": "The Professor",
    "npc.professor_pickering.title": "Collegium, Dept. of Unusual Studies",
    "npc.silas_gale.name": "Old Silas",
    "npc.silas_gale.title": "Fisherman, North Pier",
    "npc.tide_priest.name": "The Tide Priest",
    "npc.tide_priest.title": "Esoteric Order of the Drowned Ledger",
    "bark.harbour.1": "Don't say it. Whatever it is, don't say it.",
    "bark.harbour.2": "Nine minutes late again. It's always nine.",
    "bark.harbour.after": "JOSIAH WICK! ...Sorry. I'll stop. I won't stop.",
    "bark.brine.1": "Chowder's two coppers. Names are free, which is why nobody wants 'em.",
    "bark.brine.2": "Ninety-one years and I've never once said my name over open water. Look at me now. Thriving.",
    "bark.brine.after": "Fog's gone. Folk are shouting their names across my tables. Rudest, loveliest night in eighty years.",
    "bark.pickering.1": "Three hundred and sixty-one degrees. Where does the extra degree GO?",
    "bark.pickering.2": "I am... I am... I had it a moment ago.",
    "bark.pickering.after": "Ambrose Pickering! Still got it. Writing it on everything, just in case.",
    "bark.silas.1": "One for the boat and two for the net...",
    "bark.silas.2": "No hook on the line. I'm not fishing. I'm listening.",
    "bark.silas.after": "Caught a herring today. A real one. First in six weeks. Named him Ezekiel.",
    "bark.priest.1": "Iä. Iä. The Ledger is never closed.",
    "bark.priest.2": "Nameless one. Come closer. It cannot see you. Isn't that wonderful?",
    "comp.baggy.zone.saltmere": "Fog. Bells. Tentacles in the harbour. I'm going to be very brave and very quiet and very slightly behind you.",
    "comp.baggy.zone.sunken_chapel": "The water's listening. Don't say my name. Don't say yours. Let's just... point at each other.",
    "comp.kaelen.zone.saltmere": "Saltmere. The Ashbound have one page on this place. It says 'Don't.' Underlined.",
    "comp.kaelen.zone.sunken_chapel": "Stay close. Say something to me every so often. Anything. It helps.",
    "whisper.1": "Count yourself. Count yourself again. Was it the same?",
    "whisper.2": "Your name tastes of salt.",
    "whisper.3": "Nine minutes. Nine minutes. Where do the nine minutes go?",
    "whisper.4": "Say it. Just once. Just to see.",
    "whisper.5": "There is one more person in your party than there was.",
    "whisper.6": "The ledger has a page for you. It is blank. It is waiting.",
    "whisper.7": "Iä. Iä. N'gahl th'ruun.",
    "whisper.8": "Don't look behind you. It isn't there. It's never there when you look.",
    "whisper.9": "The water is very warm today.",
    "whisper.10": "One for the boat, and two for the net, and three for you.",
    "tip.23": "If the fog calls you by name, it doesn't know your name. Don't help it.",
    "tip.24": "Sanity returns faster in good company. This is also true outside of video games.",
    "tip.25": "A bowl of chowder will not save you from an elder god. It will, however, help.",
    "tip.26": "Reading forbidden texts aloud is not recommended. Reading them aloud on stream is mandatory.",
})

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

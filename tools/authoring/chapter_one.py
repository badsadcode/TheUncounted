"""Chapter One: The City Formerly Known As. The Great Silence struck seven cities off every map to hide them from the
Hunger. The first one's name was eaten; its people forgot their own names; its signs say [CITY NAME HERE] and everyone
calls it Here. Only an uncounted person can find it, by a road that appears on the Old Road at dusk. Get past Gatekeeper
Ottoline Pell (Form 1), gather the three pieces of the name (its smell from the Baker, Probably; its song from Butt-Butt;
its shape from the bell tower, for the Cartographer), open the Archive Tower, and decide at the empty plinth: say it
aloud (The Unsaying comes), write it quietly, or hand it to whoever keeps the Ledger. The name turns out to be "Here".

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q = "core:quest.ch1_here"
LD = "core:quest.legally_deceased"
I = lambda n: f"core:item.{n}"
QE = lambda s, q=Q: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda s, q=Q: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda s, q=Q: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
HI = lambda i: {"type": "has_item", "item_id": I(i)}
NI = lambda i: {"type": "item_not_held", "item_id": I(i)}
NIGHT = {"type": "hour_between", "from": 18.0, "to": 7.0}
DAY = {"type": "not_hour_between", "from": 18.0, "to": 7.0}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}
GI = lambda i, q=1: {"type": "give_item", "item_id": I(i), "qty": q}
TI = lambda i, q=1: {"type": "take_item", "item_id": I(i), "qty": q}
XP = lambda sk, n: {"type": "give_xp", "skill": sk, "amount": n}
FRAGS = ["here_frag_smell", "here_frag_song", "here_frag_shape"]
ALL3 = {"type": "flags_at_least", "flags": FRAGS, "value": 3}

D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
def builder(dlg, prefix, speaker):
    def node(nid, text, choices, actions=None):
        key = f"{prefix}.{nid}"
        S[key] = text
        n = {"speaker_key": speaker, "text_key": key, "choices": []}
        if actions: n["actions"] = actions
        for i, c in enumerate(choices):
            ck = f"{key}.c{i}"
            S[ck] = c[0]
            d = {"text_key": ck, "next": c[1]}
            for k, v in (c[2] if len(c) > 2 else {}).items(): d[k] = v
            n["choices"].append(d)
        dlg["nodes"][nid] = n
    return node
def add_topics(did, prefix, speaker, topics):
    dlg = DL[did]
    root = dlg["nodes"][dlg["root_node"]]
    end = next(i for i, c in enumerate(root["choices"]) if c["next"] == "END")
    node = builder(dlg, prefix, speaker)
    for ctext, nid, cond, ntext, nact, back in topics:
        ck = f"{prefix}.choice_{nid}"
        S[ck] = ctext
        root["choices"].insert(end, {"text_key": ck, "next": nid, "conditions": cond}); end += 1
        node(nid, ntext, [(back, dlg["root_node"])], nact)
def new_dialogue(did, prefix, speaker):
    D["dialogues"].append({"id": did, "root_node": "root", "nodes": {}})
    DL[did] = D["dialogues"][-1]
    return builder(DL[did], prefix, speaker)

# ------------------------------------------------------------------ the start: Oakhaven (either Chapter Zero ending)
add_topics("core:dialogue.clerk_oakhaven", "dlg.ch1.oak", "npc.clerk_oakhaven.name", [
    ('"Any word from the capital?"', "ch1_bureau", [QE(100, LD), QB(0)],
     "Oakhaven is holding a letter sealed in black wax with a seal you've never seen: a closed eye.\n\n\"From the High Chroniclers. "
     "Addressed to me.\" He has clearly read it many times. \"They have read the Ledger. They say the seven struck cities were never "
     "destroyed, only... misfiled. Struck off every record, so the Hunger couldn't find them.\"\n\n\"And they say a struck place can only "
     "be found by a struck person.\" He looks at you over his spectacles. \"They are requesting that an uncounted person of good "
     "standing audit the first of the seven. I wrote back that I know exactly one.\"\n\nHe slides a page across: a hand-drawn map of the "
     "Old Road, and beside the third milestone, a note: 'AT DUSK, THERE IS ONE MORE.'\n\n\"I have never been so excited about a form in my "
     "life,\" says Oakhaven, quietly. \"Please don't die. Again.\"",
     [SQ(0), SQ(10), SF("here_known")], '"I\'ll go at dusk."'),
    ('"Anything strange happen while I was away?"', "ch1_ashbound", [QE(101, LD), QB(0)],
     "Oakhaven puts down his pen.\n\n\"Your friend Kaelen was here at dusk yesterday. Sat in that chair with the Ledger and read the "
     "first page aloud. Very quietly. To see what would happen.\"\n\n\"Nothing happened. Then a carter came in, white as a sheet, to report "
     "a milestone on the Old Road that was not there that morning. I checked the survey. There is no milestone there. There has never "
     "been a milestone there.\"\n\nHe lowers his voice. \"The Ledger says the first of the seven struck cities lay east. A struck place "
     "can only be found by a struck person.\" He looks at you. \"That's you. At dusk. Please don't die. Again.\"",
     [SQ(0), SQ(10), SF("here_known")], '"I\'ll go at dusk."'),
    ('"About Here..."', "ch1_after", [QA(100)],
     "\"I've added it to the register,\" Oakhaven says, and shows you: a fresh page, a single line in his best hand. Then he frowns. "
     "\"Or I've added the fact that it isn't in the register. Which, for the purposes of the Bureau, is the same thing. The forms for this "
     "do not exist yet. I am writing them.\" He looks happier than you've ever seen him.",
     None, '"Good luck with the forms."'),
])

# ------------------------------------------------------------------ Gatekeeper Ottoline Pell
gk = new_dialogue("core:dialogue.here_gatekeeper", "dlg.ch1.gk", "npc.here_gatekeeper.name")
gk("root",
   "Behind a customs desk at the edge of the fog sits a woman in a faded uniform, very straight, very still, with a stamp in one hand "
   "and the patience of four centuries in the other. A name badge reads OTTOLINE PELL, and below it, scratched in later, (I THINK).\n\n"
   "She looks up. Then she looks up again. Her eyes fill with tears.\n\n\"A VISITOR.\"",
   [('"Can I come in?"', "day", {"conditions": [QE(20), DAY]}),
    ('"Can I come in?"', "form1", {"conditions": [QE(20), NIGHT]}),
    ('"What is this place?"', "here", {"conditions": [QA(30)]}),
    ('"How do I find the city\'s name?"', "how", {"conditions": [QE(30)]}),
    ('"I have all three pieces of the name."', "three", {"conditions": [QE(30), ALL3]}),
    ('"About the Archive..."', "archive", {"conditions": [QA(40), QB(100)]}),
    ('"It\'s done."', "after", {"conditions": [QA(100)]}),
    ("Leave.", "END")])
gk("day",
   "\"Not by day, I'm afraid.\" She gestures behind her. Through the gate, the city is there and not there: walls you can see through, "
   "a fountain like a reflection in a window, people as faint as breath on glass.\n\n\"In daylight the world remembers it has forgotten "
   "us, and we go thin. Come back after dusk. We're much more convincing at night.\" She brightens. \"I'll get the forms ready.\"",
   [('"I\'ll wait for dusk."', "root")])
gk("form1",
   "She produces, from somewhere in the desk, a single sheet of paper, yellowed with age and beautifully blank. She looks at it with "
   "enormous love.\n\n\"Form One. Entry, Municipal, Non-Existent. Nobody has filled it in for four hundred years.\" She dips a pen. "
   "\"Question one. Name, in full, in ink.\"",
   [('Give your name.', "q2", {"actions": [SF("here_gave_name")]}),
    ('"I\'d rather not. Names get eaten around here."', "q1_wise")])
gk("q1_wise",
   "Ottoline puts down the pen and looks at you with deep respect.\n\n\"Correct answer. Four hundred years, and you're the first to get "
   "it right.\" She writes 'DECLINED (WISELY)' in the box. \"Question two.\"",
   [('"Go on."', "q2")])
gk("q2",
   "\"Question two. Are you, at present, dead?\"",
   [('"Legally? It\'s complicated."', "q3"), ('"No."', "q3"), ('"Ask my clerk."', "q3")])
gk("q3",
   "She ticks a box marked 'COMPLICATED (SEE ATTACHED)'. \"Question three. Purpose of visit: tourism, commerce, or existential?\"",
   [('"Tourism."', "stamp"), ('"Commerce."', "stamp"), ('"Existential."', "stamp_ex")])
gk("stamp_ex",
   "\"OH,\" says Ottoline, delighted. \"Nobody ever picks existential.\" She underlines it twice.",
   [('"It\'s been a strange year."', "stamp")])
gk("stamp",
   "She raises the stamp, holds it above the form for a long, trembling moment, and brings it down: THUD. APPROVED. A small cloud of "
   "four-hundred-year-old ink dust rises from it like a sigh.\n\nShe tears off the bottom of the form and hands it to you. \"Your "
   "Visitor's Permit. It opens the gate. Keep it on you: if the city forgets you're allowed in, show it this.\"\n\nThen, very quietly: "
   "\"Thank you. I was beginning to think I'd made the whole job up.\"",
   [('"Thank you, Ottoline."', "root")], [GI("here_permit"), SQ(30), XP("persuasion", 30)])
gk("here",
   "\"Here.\" She says it the way you'd say the name of someone you love. \"That's what we call it. It had a real name once. Four hundred "
   "years ago the Archivists struck it off every map and every record, to hide it from the Hunger. It worked. Nothing could find us. "
   "Including us.\"\n\n\"The Hunger couldn't find the city, so it ate what it could reach: the name on the signs, the name on the fountain. "
   "Then, one by one, our own names. Most of us are descriptions now. The Baker, Probably. Person in a Hat. Butt-Butt.\" A pause. "
   "\"Butt-Butt chose that one. We couldn't talk them out of it.\"\n\n\"By night the city remembers itself well enough to be solid. "
   "By day...\" She waves a hand at the faded streets. \"We do our best.\"",
   [('"I see."', "root")])
gk("how",
   "\"The name isn't gone. It's in pieces, in people. Things that remember a place without words.\" She counts on her fingers.\n\n"
   "\"Its SMELL: the Baker, Probably, by the west wall, keeps trying to bake our bread and can't remember how. The recipe was in the old "
   "bakery before the roof fell in.\"\n\n\"Its SONG: Butt-Butt, by the fountain, knows a song about the city, but the verses are "
   "chalked all over town and the last word's been rubbed out.\"\n\n\"Its SHAPE: the Cartographer, east side, Retired. Insists the "
   "streets spell something, but the knees won't do the bell tower stairs any more.\"\n\n\"Bring me all three, and I'll give you the "
   "key to the Archive. The name was kept there. Something is still... eating, in there.\"",
   [('"Smell, song, shape. Got it."', "root")])
gk("three",
   "You tell her: the bread, the song, the streets. Ottoline listens with her eyes closed.\n\nWhen you finish, she opens a drawer she "
   "clearly hasn't opened in a very long time, and takes out a heavy iron key, and something else: a slip of paper with a single "
   "word on it that you can't read, because it isn't there.\n\n\"The Archive key. And this was the last thing the Archivists left at "
   "the gate: their trick for walking past the Hunger's Mouths. You say a thing so quietly that it un-happens. They called it "
   "Unsaying.\" The slip of paper dissolves on your palm like a snowflake, and you know how.\n\n\"The Archive is north. The name was kept "
   "on a plinth in the gallery. Someone is still up there, I think. Keeping it company.\"",
   [('"I\'ll go up."', "root")], [GI("here_archive_key"), {"type": "learn_spell", "spell_id": "core:spell.unsay"}, SQ(40)])
gk("archive",
   "\"Be careful with the Mouths. They're what's left of the Hunger's attention: they don't see you, exactly, but they hear names. Don't "
   "say anything you'd like to keep.\"",
   [('"Noted."', "root")])
gk("after",
   "Ottoline is filling in a form. It's a long one. She looks up, and for the first time since you met her, she's laughing.\n\n\"A "
   "Census of Residents. Name, age, occupation. Some of them are getting their names back, and they want them WRITTEN DOWN.\" She "
   "shakes her head. \"Four hundred years without a single form, and now there's a queue.\"",
   [('"Enjoy it, Ottoline."', "root")])

# ------------------------------------------------------------------ The Baker, Probably (smell)
bk = new_dialogue("core:dialogue.here_baker", "dlg.ch1.bk", "npc.here_baker.name")
bk("root",
   "A floury figure in an apron stands outside a house on the west side, kneading thin air with great concentration. Flour drifts from "
   "nowhere and settles nowhere.\n\n\"Morning! Evening. Whatever it is.\" A floury wave. \"I'm the baker. Probably. My hands are sure of it, "
   "anyway. They keep doing this.\" Knead, knead.",
   [('"What are you baking?"', "what", {"conditions": [QE(30), FN("here_frag_smell"), NI("here_recipe")]}),
    ('"I found a recipe card in the old bakery."', "bake", {"conditions": [QE(30), HI("here_recipe")]}),
    ('"How\'s the bread?"', "after", {"conditions": [FS("here_frag_smell")]}),
    ("Leave.", "END")])
bk("what",
   "\"OUR bread. The one the whole town ate. Every morning, the smell came out of the bakery and up the streets, and you KNEW where you "
   "were.\" The hands stop. \"I can't remember how it goes. Every time I try, it's just... air.\"\n\n\"The recipe was on a card in the old "
   "bakery, next door. The roof came down years ago. Decades. Centuries? I can't go in. Every time I try, I forget why I went in.\"",
   [('"I\'ll find it."', "root")])
bk("bake",
   "The baker takes the card in both floury hands and reads it, lips moving. Then reads it again. Then the hands start moving on "
   "their own: flour, salt, a pinch of something dark, a long slow knead, a fold, a fold.\n\nThe old oven next door, cold for four "
   "hundred years, coughs, and glows.\n\nAnd the smell comes. Warm, dark, a little sour, a little sweet, rolling out of the bakery and "
   "up the streets of Here. Doors open. Faint faces appear at windows. Somebody, somewhere, laughs.\n\nThe baker breathes it in, and "
   "says, very softly, a sound more than a word: \"Hhh...\"\n\nIt's the start of something. The start of a name. You hold onto it.\n\n"
   "\"Take a loaf,\" says the baker, wiping their eyes. \"Take two. I remembered! I don't know my own name, but I remembered the BREAD.\"",
   [('"It smells wonderful."', "root")], [TI("here_recipe"), GI("here_bread", 2), SF("here_frag_smell"), XP("lore", 30)])
bk("after",
   "\"Selling out every night!\" The baker beams. \"Nobody can pay, because nobody remembers what money is, but they come for the "
   "smell. It's the best review I've ever had.\"",
   [('"I\'m glad."', "root")])

# ------------------------------------------------------------------ Butt-Butt (song)
bb = new_dialogue("core:dialogue.here_butt_butt", "dlg.ch1.bb", "npc.here_butt_butt.name")
bb("root",
   "A small, loud child is sitting on the rim of the dry fountain, kicking their heels and drawing on the stones with a stub of "
   "chalk.\n\n\"HELLO. I'M BUTT-BUTT.\" A pause, to let that land. \"I picked it myself. Everyone forgot their names, so I picked a "
   "better one. It's the BEST name.\"",
   [('"Butt-Butt. Excellent name."', "name", {"conditions": [FN("here_bb_named")], "actions": [SF("here_bb_named")]}),
    ('"Do you know a song about the city?"', "song", {"conditions": [QE(30), FN("here_frag_song")]}),
    ('"I found all three verses."', "sing", {"conditions": [QE(30), FN("here_frag_song"), FS("here_verse1"), FS("here_verse2"), FS("here_verse3")]}),
    ('"How are you, Butt-Butt?"', "after", {"conditions": [FS("here_frag_song")]}),
    ("Leave.", "END")])
bb("name",
   "\"I KNOW.\" Butt-Butt beams. \"The Gatekeeper wanted to put 'Small Loud Child' on a form. I said NO. I said BUTT-BUTT. She cried. I "
   "think it was happy crying.\"",
   [('"Probably."', "root")])
bb("song",
   "\"YES. There's a song. We used to sing it on the bell tower, the whole town, so we wouldn't forget who we were.\" The heels stop "
   "kicking. \"But I only remember the tune. The words are chalked on walls all over town. I wrote them down before I forgot. Three "
   "bits.\"\n\n\"You can only read them at night. The chalk goes thin in the day. Like everything.\" A shrug. \"Find all three and I'll "
   "sing it. I'm REALLY loud.\"",
   [('"I\'ll find the verses."', "root")])
bb("sing",
   "You read the three verses out. Butt-Butt listens with eyes screwed shut, mouthing along. Then stands up on the rim of the fountain, "
   "takes an enormous breath, and sings.\n\nIt's not a good voice. It's a very, very loud voice. It bounces off every wall in the "
   "city:\n\n'OUR TOWN IS BY THE BENDING RIVER,\nOUR BREAD IS WARM, OUR BELLS ARE SILVER,\nWE NEVER LOCK OUR DOORS AT NIGHT,\nWE SING OUR "
   "NAME TO KEEP IT RIGHT,\nAND IF YOU FORGET, THE BELL WILL TELL:\nWE ARE...'\n\nThe last word was rubbed out. But Butt-Butt knows the "
   "tune, and holds the last note, long and rising, the shape of a word without the word: \"...EERRRR...\"\n\nThe second piece. You hold "
   "onto it next to the first.\n\nButt-Butt sits down, very pleased. \"Told you. REALLY loud.\" Then rummages in a pocket. \"Here. My "
   "lucky chalk. It's best at night. Everything is.\"",
   [('"That was amazing, Butt-Butt."', "root")], [SF("here_frag_song"), GI("butt_butt_chalk"), XP("persuasion", 20)])
bb("after",
   "\"The Gatekeeper says when people get their names back I can have mine back too.\" Butt-Butt considers this seriously. \"I'm keeping "
   "Butt-Butt.\"",
   [('"Good choice."', "root")])

# ------------------------------------------------------------------ The Cartographer (Retired) (shape)
ca = new_dialogue("core:dialogue.here_cartographer", "dlg.ch1.ca", "npc.here_cartographer.name")
ca("root",
   "An elderly figure in a much-mended coat sits in the doorway of the house on the east side, surrounded by maps of the city, every "
   "one of them with a blank space at the top where the name should be.\n\n\"The Cartographer. Retired.\" A sniff. \"Retired, because "
   "it's hard to keep a job mapping a place that isn't on any map.\"",
   [('"What are all these maps?"', "maps", {"conditions": [QE(30), FN("here_frag_shape"), FN("here_tower_view")]}),
    ('"I climbed the bell tower and looked at the streets."', "shape", {"conditions": [QE(30), FN("here_frag_shape"), FS("here_tower_view")]}),
    ('"How are the maps?"', "after", {"conditions": [FS("here_frag_shape")]}),
    ("Leave.", "END")])
ca("maps",
   "\"Every street of Here. Measured, drawn, checked twice.\" A bony finger taps a map. \"And something's wrong with all of them. Not the "
   "streets: the streets are right. It's that from up high, they're not just streets. They SPELL something. I'm sure of it.\"\n\n\"I used "
   "to climb the bell tower every night to look. The stairs are on the outside, north-east. My knees retired before I did.\" A sigh. \"Go "
   "up at night. By day you can't see the streets for the fog. Then come and tell me what they say.\"",
   [('"I\'ll climb it tonight."', "root")])
ca("shape",
   "You describe what you saw from the tower: the streets curving and joining, the way the market loops round and the long road runs "
   "out of it like a tail.\n\nThe Cartographer grabs a fresh map and draws as you talk, faster and faster, and then stops, and turns the "
   "map round to show you.\n\nThe streets of Here, drawn from above, make a single, enormous letter. A long curl, closed at the bottom: "
   "\"...E,\" the Cartographer whispers. \"It ends in E. The whole town is the last letter of its own name.\"\n\nThe third piece. You hold "
   "it next to the others. H... ER... E.\n\n\"Take this.\" A rolled map, the finest one, with the blank space still at the top. \"When "
   "you find it, write it in. I'd like that.\"",
   [('"I will."', "root")], [SF("here_frag_shape"), GI("here_map"), XP("lore", 30)])
ca("after",
   "\"Busy! Everyone wants their street on a map again.\" The Cartographer is drawing with both hands. \"Retirement is cancelled.\"",
   [('"Good."', "root")])

# ------------------------------------------------------------------ Person in a Hat (flavour)
ph = new_dialogue("core:dialogue.here_person_in_hat", "dlg.ch1.ph", "npc.here_person_in_hat.name")
ph("root",
   "A person in a very tall hat is standing by a market stall, selling nothing to no one with great dignity.\n\n\"Evening. I'm the "
   "Person in a Hat.\" A tip of the hat. \"It used to be the Person in the Market Selling Hats. Then I forgot what a market was. Then "
   "what selling was. I've held onto the hat.\"",
   [('"It\'s a very good hat."', "hat"), ('"Do you remember your name?"', "name"), ("Leave.", "END")])
ph("hat", "\"It is. It's all I've got, and it's a good one. Some people don't even have a hat.\"", [('"True."', "root")])
ph("name",
   "\"Not a letter of it.\" Unbothered. \"But I'll tell you what I do remember. Every night at the bell, the whole town would shout it at "
   "once, so loud the Hunger couldn't hear itself think. You can't eat a word that everyone's shouting.\" A pause. \"Then one night "
   "we were too tired. And it got in.\"",
   [('"I\'m sorry."', "root")])

# ------------------------------------------------------------------ The Night Merchant (midnight to two)
nm = new_dialogue("core:dialogue.here_night_merchant", "dlg.ch1.nm", "npc.here_night_merchant.name")
nm("root",
   "A hooded figure behind a stall that wasn't there a minute ago. Lanterns hang from it, each one lit with a different colour of "
   "nothing.\n\n\"The Midnight Market. Open from midnight until two. Closed at all other times, including yesterday.\" A long, thin hand "
   "gestures at the wares. \"Yesterdays. Lost umbrellas. One Tuesday, slightly used. And practical things, for practical people who "
   "walk at night.\"",
   [('"Show me the practical things."', "END", {"actions": [{"type": "open_shop"}]}),
    ('"Do you sell names?"', "names"), ("Leave.", "END")])
nm("names", "\"NO.\" The lanterns flicker. \"Never. Not even good ones. Not even Butt-Butt.\"", [('"Fair."', "root")])

# ------------------------------------------------------------------ The Last Archivist (the plinth, the endings)
ec = new_dialogue("core:dialogue.here_echo", "dlg.ch1.ec", "npc.here_echo.name")
ec("root",
   "At the top of the Archive, beside an empty stone plinth, stands a figure made of almost nothing: robes, a pair of spectacles, the "
   "outline of someone who once sat here every day. The Last Archivist of Here.\n\n\"You came up the stairs. You came past the Mouths. "
   "You must be uncounted, like us.\"",
   [('"I have the three pieces of the name."', "pieces", {"conditions": [QE(40)]}),
    ('"It\'s done. The Unsaying is gone."', "end_a", {"conditions": [QE(90)]}),
    ('"What happens now?"', "after", {"conditions": [QA(100)]}),
    ("Leave.", "END")])
ec("pieces",
   "\"Then lay them down.\"\n\nYou do. Not on the plinth: in the air, the way you've been carrying them. The smell of the Baker's bread. The "
   "long rising note of Butt-Butt's song. The great curling letter of the streets.\n\nH. ER. E.\n\nThe Archivist laughs, very softly, "
   "like a page turning.\n\n\"Yes. That's it. That was always it. Four hundred years of everyone calling it Here because they'd forgotten "
   "the name, and the name was Here. They never forgot. They just didn't know they remembered.\"\n\n\"So. Now you hold the name of a city. "
   "The question is what you do with it.\"",
   [('"What are my choices?"', "choice")])
ec("choice",
   "\"You can SAY it. Aloud, here, where it was kept. The city comes back to the world: every map, every road. And the Hunger will hear "
   "it. The part of it that's still here, the part that ate our name, will come for it. You'd have to stop it.\"\n\n\"You can WRITE it. "
   "Quietly, on the plinth, in your own hand. The city stays hidden, but whole: everyone here gets their own name back. Nobody outside "
   "will ever know it's here.\"\n\n\"Or you can give it to whoever keeps the Ledger, and let them decide. That's what Archivists do, in "
   "the end. We hand things on.\"",
   [('Say it aloud: "HERE."', "say", {"actions": [SF("here_spoken"), SQ(50)]}),
    ("Write it on the plinth, quietly.", "write"),
    ('"I\'ll give it to the Bureau." (seal it for the High Chroniclers)', "give_bureau", {"conditions": [QE(100, LD)]}),
    ('"I\'ll give it to the Ashbound." (Kaelen will read it in their halls)', "give_ashbound", {"conditions": [QE(101, LD)]}),
    ('"I need to think."', "root")])
ec("say",
   "You take a breath, and say it, aloud, the whole name, the way Butt-Butt would: \"HERE.\"\n\nThe word goes out of the Archive like a bell. "
   "You hear it go down the stairs and out of the door and across the market and up the bell tower, and the bell catches it and rings, "
   "and every window in the city lights up at once.\n\nAnd then the hall below goes quiet. Very quiet. The kind of quiet that's "
   "listening.\n\nSomething is standing up in the dark between the shelves. Something made of the spaces between words.\n\nIt heard.",
   [('Go down and face it.', "END")])
ec("end_a",
   "The Archivist is clearer now: you can see a face, kind and tired, and ink on the fingers.\n\n\"It's gone. The last of it. Do you "
   "hear?\" Outside, the bell is still ringing, and under it, faintly, voices: people calling their own names out of windows, testing "
   "them, laughing.\n\n\"Here is back on the map. Every map. Some clerk in the capital is going to have a very confusing morning.\"",
   [('"Oakhaven will be thrilled."', "root")], [SQ(100), SF("here_ending_spoken"), GI("here_silver_bell"), {"type": "give_gold", "amount": 300},
                                                  XP("lore", 120), {"type": "narrate", "pages": [{"key": "story.here.end_spoken"}, {"key": "story.here.epilogue"}]}])
ec("write",
   "You take the pen from the Archivist's desk, dip it, and on the empty stone of the plinth, in your own hand, very small, you write: "
   "Here.\n\nThe ink sinks into the stone like rain into dry ground.\n\nNothing rings. Nothing comes. But outside, down in the market, "
   "somebody says, wonderingly, \"...Margery. I'm Margery,\" and someone else starts to cry, and someone else is laughing, and Butt-Butt, "
   "unmistakably, shouts: \"I'M STILL BUTT-BUTT.\"\n\n\"Hidden, and whole,\" says the Archivist. \"Nobody outside will ever know. That's "
   "the kindest thing anyone has done for us in four hundred years.\"",
   [('"Look after them."', "root")], [SQ(101), SF("here_ending_written"), GI("here_quiet_name"), XP("lore", 120),
                                       {"type": "narrate", "pages": [{"key": "story.here.end_written"}, {"key": "story.here.epilogue"}]}])
ec("give_bureau",
   "You write the name on a sheet of the Archive's paper, fold it twice, and the Archivist seals it with black wax and a closed eye.\n\n"
   "\"The High Chroniclers will decide. That's their job: deciding what the world may know.\" A pause. \"I hope they decide kindly.\"\n\n"
   "When you get back, Oakhaven will send it on with a rider, and a covering form, in triplicate.",
   [('"They will."', "root")], [SQ(102), SF("here_ending_given"), {"type": "give_gold", "amount": 400}, XP("persuasion", 100),
                                 {"type": "narrate", "pages": [{"key": "story.here.end_bureau"}, {"key": "story.here.epilogue"}]}])
ec("give_ashbound",
   "You write the name on a sheet of the Archive's paper and fold it into your copy of the Ledger, beside four hundred years of other "
   "names.\n\n\"The Ashbound,\" says the Archivist. \"They read names aloud. All of them, one day, so loud the Hunger can't keep up.\" A "
   "faint smile. \"That was our idea once, too.\"\n\nKaelen will want to read this one first.",
   [('"Kaelen will do it justice."', "root")], [SQ(102), SF("here_ending_given"), {"type": "give_gold", "amount": 250}, XP("lore", 100),
                                                 {"type": "narrate", "pages": [{"key": "story.here.end_ashbound"}, {"key": "story.here.epilogue"}]}])
ec("after", "\"Now? Now we have a lot of forms to fill in.\" The Archivist sounds delighted about it.", [('"Good luck."', "root")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ NPCs
N = load("content/npcs/core_npcs.json")
def npc(nid, name, title, dlg, sheet, scale=1.75, barks=(), **extra):
    d = {"id": f"core:npc.{nid}", "name_key": f"npc.{nid}.name", "title_key": f"npc.{nid}.title", "faction": "core:faction.ashbound",
         "dialogue_id": dlg, "appearance": {"type": "sprite_8dir", "sprite_sheet": f"assets/sprites/npcs/{sheet}.png",
                                            "animation_data": "assets/animations/npc_standard.json", "scale": scale},
         "barks": [{"text_key": f"bark.{nid}.{i}"} for i in range(len(barks))]}
    d.update(extra)
    N["npcs"].append(d)
    S[f"npc.{nid}.name"] = name; S[f"npc.{nid}.title"] = title
    for i, b in enumerate(barks): S[f"bark.{nid}.{i}"] = b
npc("here_gatekeeper", "Ottoline Pell", "Gatekeeper of Here (I Think)", "core:dialogue.here_gatekeeper", "here_gatekeeper",
    barks=["Form One. Entry, Municipal, Non-Existent. In ink, please.", "Four hundred years, and finally a queue. Well, a queue of one."])
npc("here_baker", "The Baker, Probably", "Resident of Here", "core:dialogue.here_baker", "here_baker",
    barks=["Knead, fold, knead. My hands know. I don't.", "Can you smell that? No? Me neither. Yet."])
npc("here_butt_butt", "Butt-Butt", "Small, Loud, Self-Named", "core:dialogue.here_butt_butt", "here_butt_butt", scale=1.15,
    barks=["I'M BUTT-BUTT.", "I picked it myself!", "Want to hear a song? It's LOUD."])
npc("here_cartographer", "The Cartographer", "Retired", "core:dialogue.here_cartographer", "here_cartographer",
    barks=["The streets spell something. I'm sure of it.", "My knees retired before I did."])
npc("here_person_in_hat", "Person in a Hat", "Resident of Here", "core:dialogue.here_person_in_hat", "here_person_in_hat",
    barks=["Lovely evening. I assume. I've forgotten what the others were like."])
npc("here_night_merchant", "The Night Merchant", "Midnight to Two", "core:dialogue.here_night_merchant", "here_night_merchant",
    barks=["Yesterdays, lightly used. Lost umbrellas."],
    vendor_inventory=[{"item_id": I("health_potion"), "stock": 6, "price": 20}, {"item_id": I("mana_potion"), "stock": 6, "price": 22},
                      {"item_id": I("here_bread"), "stock": 5, "price": 8}, {"item_id": I("lockpick"), "stock": 4, "price": 12},
                      {"item_id": I("moonlit_cloak"), "stock": 1, "price": 260}])
npc("here_echo", "The Last Archivist", "Keeper of the Plinth", "core:dialogue.here_echo", "here_echo",
    barks=["H... no. Not yet. Not until someone brings the pieces."])
save("content/npcs/core_npcs.json", N)

# ------------------------------------------------------------------ monsters
CR = load("content/creatures/core_creatures.json")
CR["creatures"].append({"id": "core:enemy.here_mouth", "name_key": "enemy.here_mouth.name",
    "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/enemies/here_mouth.png", "animation_data": "assets/animations/npc_standard.json", "scale": 1.5},
    "stats": {"health": 70, "armor": 2, "move_speed": 3.0, "xp_reward": 40}, "behavior": "melee_patroller", "family": "eldritch",
    "perception": {"sight_meters": 9.0, "hearing_meters": 12.0},
    "attack": {"name": "unsay", "damage": 10, "reach_meters": 1.8, "windup_seconds": 0.5, "cooldown_seconds": 1.3},
    "loot_table": "core:loot.here_mouth",
    "audio": {"alert": "assets/audio/sfx/rat_squeak.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav", "death": "assets/audio/sfx/enemy_death.wav"},
    "hit_fx": {"color": [180, 170, 220], "glow": True}, "lines": {"alert": "line.here_mouth.alert", "death": "line.here_mouth.death"}})
CR["creatures"].append({"id": "core:enemy.here_unsaying", "name_key": "enemy.here_unsaying.name",
    "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/enemies/here_unsaying.png", "animation_data": "assets/animations/npc_standard.json", "scale": 3.0},
    "stats": {"health": 420, "armor": 5, "move_speed": 2.3, "xp_reward": 220}, "behavior": "melee_patroller", "family": "eldritch", "boss": True,
    "perception": {"sight_meters": 18.0, "hearing_meters": 18.0},
    "attack": {"name": "unsay", "damage": 18, "reach_meters": 2.6, "windup_seconds": 0.75, "cooldown_seconds": 1.5},
    "loot_table": "core:loot.here_unsaying",
    "audio": {"alert": "assets/audio/sfx/sentinel_clang.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav", "death": "assets/audio/sfx/enemy_death.wav"},
    "hit_fx": {"color": [200, 190, 255], "glow": True}, "lines": {"alert": "line.here_unsaying.alert", "death": "line.here_unsaying.death"}})
save("content/creatures/core_creatures.json", CR)
S.update({"enemy.here_mouth.name": "Mouth of the Hunger", "enemy.here_unsaying.name": "The Unsaying",
          "line.here_mouth.alert": "(a sound like a word being swallowed)", "line.here_mouth.death": "(a hiccup, and silence)",
          "line.here_unsaying.alert": "THERE IS NO SUCH PLACE. THERE IS NO SUCH PERSON. THERE IS NO SUCH...",
          "line.here_unsaying.death": "...here. (It says it, at the end. It can't help it.)",
          "bestiary.here_mouth": "What's left of the Hunger's attention in a struck place: a mouth with no face, listening for names. Doesn't see you, exactly. Hears you fine. - H.",
          "bestiary.here_unsaying": "The part of the Hunger that ate a city's name and stayed for the crumbs. Made of the gaps between words. Say its name? It hasn't got one. That's the problem. - H."})
L = load("content/loot_tables/core_loot.json")
L["loot_tables"].append({"id": "core:loot.here_mouth", "gold_min": 4, "gold_max": 14,
                         "entries": [{"item_id": I("mana_potion"), "weight": 40, "min_qty": 1, "max_qty": 1}, {"item_id": I("health_potion"), "weight": 30, "min_qty": 1, "max_qty": 1}]})
L["loot_tables"].append({"id": "core:loot.here_unsaying", "gold_min": 80, "gold_max": 140, "guaranteed": [I("red_pen")],
                         "entries": [{"item_id": I("health_potion"), "weight": 60, "min_qty": 2, "max_qty": 3}]})
save("content/loot_tables/core_loot.json", L)

# ------------------------------------------------------------------ items
CB = load("content/items/consumables_and_books.json"); A = load("content/items/armor_and_gear.json")
WP = load("content/items/weapons.json") if __import__("os").path.exists("content/items/weapons.json") else None
def item(n, name, desc, cat, model, value, **kw):
    d = {"id": I(n), "name_key": f"item.{n}.name", "description_key": f"item.{n}.description", "category": cat,
         "icon": f"assets/ui/items/{n}.png", "world_model": f"assets/models/items/{model}.glb", "slots": kw.pop("slots", []), "value": value,
         "weight": kw.pop("weight", 0.3)}
    d.update(kw)
    S[f"item.{n}.name"] = name; S[f"item.{n}.description"] = desc
    return d
CB["items"] += [
    item("here_permit", "Visitor's Permit (Here)", "The bottom of Form One, stamped APPROVED in four-hundred-year-old ink. Purpose of visit: see attached.", "key", "form_27b_scroll", 0),
    item("here_archive_key", "Key to the Archive of Here", "Heavy, iron, and warm from four hundred years in Ottoline's drawer.", "key", "annex_key", 0),
    item("here_recipe", "Recipe Card (Bread of Here)", "Flour, salt, a pinch of something dark. A long slow knead, a fold, a fold. In the corner, a smudge of four-hundred-year-old flour.", "misc", "form_27b_scroll", 0),
    item("here_map", "The Cartographer's Map", "Every street of Here, measured and checked twice. From above, the streets make one great curling letter. There's a blank space at the top for the name.", "misc", "form_27b_scroll", 30),
    item("here_bread", "Bread of Here", "Warm, dark, a little sour, a little sweet. It smells like knowing where you are. Steadies the mind.", "consumable", "bread_loaf", 8,
         stackable=True, weight=0.3, effects=[{"type": "consumable_heal", "amount": 20}, {"type": "consumable_sanity", "amount": 15}]),
    item("here_quiet_name", "The Quiet Name", "A sliver of the plinth's stone with a single word written on it in your own hand. Whoever reads it remembers where they are, and who.", "book", "spell_tome", 50,
         book_text_key="book.here_quiet_name.text"),
]
S["book.here_quiet_name.text"] = ("A sliver of stone from the plinth in the Archive of Here. On it, in your own handwriting, very small:\n\nHere.\n\n"
                                  "Underneath, added later by many different hands, a list that goes on and on: 'Margery.' 'Tobias Fenn.' 'Old Wick.' "
                                  "'Ottoline Pell (CONFIRMED).' 'The Baker, Probably (Ada, actually).' And at the very bottom, in enormous chalk letters "
                                  "that somehow fit: 'BUTT-BUTT (KEEPING IT).'")
A["items"] += [
    item("butt_butt_chalk", "Butt-Butt's Lucky Chalk", "A stub of chalk worn to a nub from writing BUTT-BUTT WOZ ERE on every wall in town. 'It's best at night. Everything is.' At night, you strike truer and luckier.",
         "accessory", "signet_ring", 180, slots=["accessory"], weight=0.1,
         effects=[{"type": "bonus_night", "stat": "crit_chance_bonus", "value": 0.08}, {"type": "bonus_night", "stat": "crit_damage_bonus", "value": 0.25},
                  {"type": "bonus", "stat": "gold_find_bonus", "value": 0.05}]),
    item("moonlit_cloak", "Moonlit Cloak", "From the Midnight Market: a cloak that's slightly more there at night. You move quicker after dark, and gold finds its way to you.",
         "accessory", "scholar_robe", 260, slots=["accessory"], weight=1.0,
         effects=[{"type": "bonus_night", "stat": "move_speed_bonus", "value": 0.1}, {"type": "bonus_night", "stat": "status_chance_bonus", "value": 0.1}]),
    item("here_silver_bell", "Silver Bell of Here", "A small silver bell from the tower of Here, given by the whole town. When it rings, things that eat names flinch. Your spells hit harder; you see further into the dark.",
         "accessory", "signet_ring", 500, slots=["accessory"], weight=0.2,
         effects=[{"type": "bonus", "stat": "spell_power_bonus", "value": 0.12}, {"type": "bonus", "stat": "status_duration_bonus", "value": 0.2},
                  {"type": "stat_bonus", "stat": "will", "amount": 1}]),
]
red_pen = item("red_pen", "The Red Pen", "An Archivist's editing pen, long enough to use as a dagger, still wet with red ink after four hundred years. It strikes things out: a hit can make a foe forget what it was doing.",
               "weapon", "steel_dagger", 420, slots=["main_hand"], weight=0.6,
               weapon={"kind": "melee", "skill": "daggers", "damage_type": "piercing", "base_damage": 15, "attack_time_seconds": 0.34, "stamina_cost": 5,
                       "reach_meters": 1.8, "crit_chance": 0.18, "crit_mult": 2.0, "on_hit_status": "confuse", "status_chance": 0.2, "status_power": 0,
                       "status_duration": 3.0})
(WP or A)["items"].append(red_pen)
save("content/items/consumables_and_books.json", CB); save("content/items/armor_and_gear.json", A)
if WP: save("content/items/weapons.json", WP)

# ------------------------------------------------------------------ spell
SPL = load("content/spells/core_spells.json")
SPL["spells"].append({"id": "core:spell.unsay", "name_key": "spell.unsay.name", "description_key": "spell.unsay.desc",
                      "icon": "assets/ui/spells/unsay.png", "skill": "illusion", "mana_cost": 16, "cooldown_seconds": 4.0,
                      "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                      "effect": {"primitive": "projectile_damage", "damage_type": "ink", "base_power": 2, "projectile_speed": 18.0,
                                 "projectile_sprite": "assets/sprites/vfx/spell_arcane.png", "light_color": [0.8, 0.8, 1.0], "light_radius": 4.0,
                                 "status": "forget", "status_chance": 1.0, "status_duration": 8.0}})
save("content/spells/core_spells.json", SPL)
S["spell.unsay.name"] = "Unsay"
S["spell.unsay.desc"] = ("The Archivists' last trick: say something so quietly it un-happens. The target forgets it ever saw you, and can't see you again "
                         "for eight seconds (less for the very large). For walking past things that shouldn't notice you.")

# ------------------------------------------------------------------ quest, campaign, story, names
QQ = load("content/quests/chapter_zero_quests.json")
QQ["campaigns"].append({"id": "chapter_one", "name_key": "campaign.ch1.name", "desc_key": "campaign.ch1.desc", "kind": "main", "order": 1})
S["campaign.ch1.name"] = "Chapter One: The City Formerly Known As"
S["campaign.ch1.desc"] = "The Great Silence struck seven cities off every map. The first one is still there, behind the fog, waiting for someone to remember it."
QQ["quests"].append({"id": Q, "title_key": "quest.ch1.title", "summary_key": "quest.ch1.summary", "campaign": "chapter_one", "stages": [
    {"stage": 0, "objective_key": "quest.ch1.stage0", "journal_key": "quest.ch1.journal0", "markers": ["npc_oakhaven"]},
    {"stage": 10, "objective_key": "quest.ch1.stage10", "journal_key": "quest.ch1.journal10", "markers": ["road_dusk_milestone"]},
    {"stage": 20, "objective_key": "quest.ch1.stage20", "journal_key": "quest.ch1.journal20", "markers": ["npc_here_gatekeeper"]},
    {"stage": 30, "objective_key": "quest.ch1.stage30", "journal_key": "quest.ch1.journal30",
     "markers": ["npc_here_baker", "here_recipe", "npc_here_butt_butt", "here_verse_1", "here_verse_2", "here_verse_3", "npc_here_cartographer",
                 "here_tower_view", "npc_here_gatekeeper"]},
    {"stage": 40, "objective_key": "quest.ch1.stage40", "journal_key": "quest.ch1.journal40", "markers": ["here_archive_door", "npc_here_echo"]},
    {"stage": 50, "objective_key": "quest.ch1.stage50", "journal_key": "quest.ch1.journal50", "markers": ["here_unsaying"]},
    {"stage": 90, "objective_key": "quest.ch1.stage90", "journal_key": "quest.ch1.journal90", "markers": ["npc_here_echo"]},
    {"stage": 100, "objective_key": "quest.ch1.stage100", "journal_key": "quest.ch1.journal100", "completed": True},
    {"stage": 101, "objective_key": "quest.ch1.stage101", "journal_key": "quest.ch1.journal101", "completed": True},
    {"stage": 102, "objective_key": "quest.ch1.stage102", "journal_key": "quest.ch1.journal102", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.ch1.title": "The City Formerly Known As", "quest.ch1.summary": "A city struck off every map, a name eaten by the Hunger, and a road that only appears at dusk.",
    "quest.ch1.stage0": "Talk to Clerk Oakhaven.", "quest.ch1.journal0": "Something new has come up in Bellwether.",
    "quest.ch1.stage10": "Go to the Old Road between dusk and dawn (18:00 to 6:00) and follow the road that wasn't there. (Press T to wait.)",
    "quest.ch1.journal10": "The first of the seven struck cities lies east. A struck place can only be found by a struck person, and the road only appears at dusk, by a milestone that has never been on any survey.",
    "quest.ch1.stage20": "Get past the Gatekeeper at the gate of Here (she can only let you in at night).",
    "quest.ch1.journal20": "The road led through the fog to a city whose signs say [CITY NAME HERE]. There is a customs post. Someone is very excited to see me.",
    "quest.ch1.stage30": "Find the three pieces of the city's name: its smell (the Baker, Probably), its song (Butt-Butt and the chalked verses), its shape (the bell tower, for the Cartographer). Then tell Ottoline. All of it works best at night.",
    "quest.ch1.journal30": "Four hundred years ago the Archivists struck this city off every map to hide it from the Hunger. The Hunger ate its name instead, and then its people's names. The name survives in pieces, in people.",
    "quest.ch1.stage40": "Open the Archive Tower (north) and climb to the empty plinth in the gallery.",
    "quest.ch1.journal40": "Ottoline gave me the Archive key and the Archivists' last trick, Unsay. The name was kept on a plinth in the Archive. Something there is still eating.",
    "quest.ch1.stage50": "The Unsaying heard the name. Stop it in the Archive hall!",
    "quest.ch1.journal50": "I said the name aloud: Here. The whole city heard it. So did the thing that ate it.",
    "quest.ch1.stage90": "Go back up to the Last Archivist.", "quest.ch1.journal90": "The Unsaying is gone. The bell is still ringing.",
    "quest.ch1.stage100": "Chapter One Complete: Here is back on every map.",
    "quest.ch1.journal100": "I said the name aloud and stopped the Unsaying. Here is back in the world: every map, every road. Its people are calling their own names out of their windows.",
    "quest.ch1.stage101": "Chapter One Complete: Here is hidden, and whole.",
    "quest.ch1.journal101": "I wrote the name on the plinth, quietly. Here stays hidden from the world, but everyone in it has their own name back. Except Butt-Butt, by choice.",
    "quest.ch1.stage102": "Chapter One Complete: the name is in other hands.",
    "quest.ch1.journal102": "I gave the city's name to whoever keeps the Ledger, and let them decide. That's what Archivists do, in the end.",
    "map.here.name": "Here", "map.here_archive.name": "The Archive of Here",
    "story.here.road": "The sun goes down behind you on the Old Road. Where there was nothing this morning, there is a milestone: old, mossy, carved with a number that doesn't match any other milestone on the road, and an arrow pointing at a road that wasn't there either.\n\nYou follow it. The fog comes up to meet you, cold and soft. The Old Road disappears behind you. The stars go out, one by one, and come back different.\n\nAnd then, out of the fog: a gate, a customs post, a lamp, and a city, with every window dark but one.",
    "story.here.end_spoken": "All night the bell of Here rings. People lean out of their windows and shout their names into the street, testing them, laughing, getting them slightly wrong and shouting them again.\n\nIn the morning, the fog is gone. Carters on the Old Road find a turning they're sure was never there, and a city at the end of it, and a woman at a customs desk who is so pleased to see them that she makes every single one fill in Form One.\n\nIn the capital, a clerk unrolls the great map of the kingdom and finds, east of Bellwether, a city that was not there yesterday, labelled in a hand nobody recognises: HERE.",
    "story.here.end_written": "Nobody outside ever learns what you did. The fog stays. The road still only appears at dusk, and only for people who have been uncounted.\n\nBut behind the fog, every night, there's bread in the bakery, and a bell rung at nine, and a city full of people who know their own names, and say them to each other, and write them on everything, just in case.\n\nOn the wall by the fountain, in enormous chalk: BUTT-BUTT (STILL).",
    "story.here.end_bureau": "Oakhaven sends the sealed name to the capital by rider, with a covering form in triplicate. For a month, nothing. Then a letter comes back, sealed with the closed eye: 'Received. Under consideration. Thank you for your service to the Record.'\n\nOakhaven reads it nine times. \"They'll decide,\" he says. \"That's their job.\" He doesn't sound sure. He frames the letter anyway.",
    "story.here.end_ashbound": "Kaelen reads the name aloud at dusk in the Ashbound's hall, with the Ledger open and every lamp lit, the way the Ashbound read all the names they find: loudly, clearly, so that nothing can eat them.\n\nSomewhere east, behind the fog, a bell rings once, as if in answer.\n\n\"One city,\" Kaelen says afterwards, closing the Ledger. \"Six to go.\"",
    "story.here.epilogue": "Chapter One: The City Formerly Known As, is complete.\n\nSix struck cities remain somewhere in Edrath, behind fog, under lakes, inside mountains, waiting for someone uncounted to remember them.\n\nAnd somewhere, very far away, something that eats names has noticed that one has got away.",
    "tip.46": "Some places are only there at night. Press T to wait for dusk.",
    "tip.47": "Unsay makes a foe forget it saw you. The very large forget faster.",
})

# ------------------------------------------------------------------ companions: a word in Here
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

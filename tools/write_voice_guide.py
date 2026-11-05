#!/usr/bin/env python3
"""Writes two plain-text files from the game's data (via write_voice_script.py); rerun after changing their dialogue:
  docs/VOICE_GUIDE_COTH_AND_ERANU.txt  for the two friends: performance notes and every line, numbered E1.. and C1..
  docs/VOICE_GUIDE_FILE_NAMES.txt      for BadSad: which file name each numbered line needs once the takes are cut

    python tools/write_voice_guide.py
"""
import os
import re
import textwrap

import write_voice_script as vs

WIDTH = 78
OUT = os.path.join(vs.ROOT, "docs", "VOICE_GUIDE_COTH_AND_ERANU.txt")
OUT_NAMES = os.path.join(vs.ROOT, "docs", "VOICE_GUIDE_FILE_NAMES.txt")

INTRO = """
Hi Coth, hi Eranu!

You two are in the game as yourselves, and this file is everything you need to
give those characters your real voices: who they are, how the lines should
feel, how to record them, and every line you say.

Nothing here is a rule. If a line wants to go somewhere funnier or more natural,
follow it. You know these two characters better than anyone.
"""

STORY = """
You only need the side quest called "Cothepoo, Come Home".

Eranu sits in the window seat of the Lantern Inn, watching the door. Three days
ago her waifu, Coth, went out to find some trousers and never came back. She
asks the player to fetch him.

The player finds Coth in the Whistling Wood, camped with Sir Pebbleton, a round
stone with a face painted on it. Coth is completely certain he has been lost for
a thousand years. It has been three days. Tally marks on a tree prove it: 72
hours. His enormous beard, it turns out, was always like that.

He goes home. He bursts into the inn. Eranu crosses the room in four strides,
looks like she might hit him, and hugs him off the floor instead. Marta brings
two bowls of stew. Somebody starts a slow clap.

After that, both of them can join the player's party and walk the world,
chatting, fighting and teasing each other.
"""

TOGETHER = """
THE MAIN THING: play it straight. These characters never know they are funny.
Coth truly believes it has been a thousand years. Eranu truly thinks "waifu" is
a normal word that everybody knows. Skip the wink at the audience and the jokes
get bigger.

UNDER THE JOKE: she was scared, and he was lonely. They would both rather die
than say so. A few lines let that show for a moment. Those are marked in the
notes. Keep them small, and they will be the best moments you record.

THE RHYTHM: Eranu is calm and speaks in short, level sentences. Coth swings
between grand speeches and tiny defeated mumbles. She wins every exchange, and
she barely has to raise her voice to do it.
"""

ERANU_GUIDE = """
WHO SHE IS: a tall, confident warrior from the Glens, in a green kilt, with a
round shield and a sword across her knees. She hits things that need hitting and
reads things that need reading. Dry, unimpressed, secretly soft about exactly
one person.

YOUR VOICE: speak low and unhurried. She is never the one in a hurry, and she
gets quieter when she means it. Save real volume for the fights and for one
word: "COTHEPOO."

THE SCOTS: you're the Scot here, and these lines weren't written by one. The
spelling is only there so the subtitles read nicely. Ignore it and say every
line the way you'd really say it. If a word or a whole line sounds wrong, change
it. If you change a lot, tell BadSad so the subtitle can match.
"""

COTH_GUIDE = """
WHO HE IS: skinny, scruffy, with a beard to his belt and hair longer still. No
trousers, ever, in any weather. There are two Coths in this script, and the
difference is what makes him work.

COTH IN THE WOOD (the castaway): wide-eyed and hoarse, with too much dignity for
a man with no trousers. He has had nobody to talk to but a rock for three days,
and it has gone straight to his head. Big, formal, theatrical speech, as if he
is reciting his memoirs. He loves that rock, and that love is real.

COTH AT HOME (the companion): cheerful, a bit unhinged, proud of his legs. Still
insists on the thousand years, but now it's more of a hobby. Easy, happy,
usually eating something.

YOUR VOICE: talk as yourself and turn it up. No accent is needed. Go big when he
is proud, and go tiny when Eranu looks at him. That drop is his best joke: he
can go from "A free man of the wilds" to "...Your waifu" in a single breath.

SIR PEBBLETON: always speak of him with complete respect. He is a person. He is
the quiet one.
"""

RECORDING = """
GEAR: a phone or a headset is fine. No studio needed.

ROOM: somewhere quiet and soft. A wardrobe full of clothes is a famous trick.
Turn off fans and close the window.

MIC: about a hand's width from your mouth and slightly to one side, so the P's
in "Pebbleton" and "poo" don't pop. For shouts, lean back or turn away a little
so the sound doesn't distort.

TAKES: do two or three of anything you care about. If you redo a line, just say
its number again and go. BadSad can pick the last one.

KEEP IT EVEN: try to record in one sitting, or at least in the same spot at the
same distance, so the character doesn't change sound between lines.

SENDING: don't worry about file types or file names. Record however is easiest,
even one long recording, and send it to BadSad, who will do the cutting and
naming. Before each line, say its number out loud (like "E12"), leave a pause,
then read the line. That's how BadSad finds it.

NO RUSH: you can record a few at a time. Any line without a recording just shows
as a subtitle in the game, so nothing breaks.
"""

READING = """
E12 or C7          The line's number. E is for Eranu, C is for Coth. Say it
                   before the line so BadSad can find it.

[beat]             A pause. Something happens here in the game: the player
                   reads a bit of description, or the character does something.
                   Leave about a second and carry on. The note usually says
                   what is happening.

CAPITALS           Lean on that word. It doesn't always mean louder.

...                Trailing off, or working up to saying something.

Note:              A suggestion about how the line could feel. Ignore freely.

You only read your own numbered lines. Anyone else's lines are there so you know
what you're answering, and they have no number.

SOME LINES REPEAT: the first line of each conversation plays every time the
player talks to you, so keep those light. Fight lines come up over and over, so
keep them short and punchy, without leaning too hard on the joke.
"""

START_HERE = """
Short on time? Record in this order. The most important lines come first:

  1. The Reunion (the scene right below this list)
  2. Your scenes with each other
  3. Your conversations
  4. Fight lines and everything else
"""

REUNION_NOTES = """
This is the peak of the whole story, so give it your best takes. It plays on
full-screen cards while the player reads the description. Don't worry about
timing. Just give the words, and BadSad will put the scene together.
"""

APART = """
You'll each record your half on your own, and BadSad will put the scenes
together. That works fine here, because the game plays every line as its own
clip, so nobody has to match anyone's timing.

Before each of your lines, read the other person's line in your head, then
answer it. Picture them right in front of you, the way you know they'd say it.
Stop cleanly at the end of your line, and don't talk over where they would be.
"""

SECTION_TIPS = {
    "barks": "Muttered while the player walks past, to nobody in particular. Keep it low and half to yourself. Nobody is meant to answer.",
    "conversation": "The player is standing right in front of you. Only your spoken words are listed; the description around them appears on screen.",
    "idle": "Random chatter while walking. Say it offhand, as if the thought just wandered in. Silence is normal between these.",
    "combat": "Shouted mid-fight, often. Short, with full energy from the belly. Back off the mic.",
    "kill": "Right after an enemy falls. You're catching your breath and pleased with yourself.",
    "heal": "You're patching the player up, close by and a little distracted, hands busy.",
    "level": "The player just got stronger. A quick, real compliment.",
    "catchup": "You fell behind and jogged to catch up. A little out of breath is perfect.",
    "zone": "Said once, on first arriving somewhere. A first impression while looking around.",
}

NOTES = {
    # ---------------------------------------------------------------- Eranu
    "bark.eranu.1": "To herself. It's the grievance she has been chewing on for days. Lean on the second DAYS.",
    "bark.eranu.2": "Asking a stranger, completely matter of fact. This is a normal thing to ask.",
    "bark.eranu.3": "After he's home. Low and sideways, like a secret. A small smile you can hear.",
    "dlg.eranu.root": "This plays every time. One eye on the player, one on the door. She's listening, but only just.",
    "dlg.eranu.who": "[beat]: she pats her sword. 'Then they're surprised again' is a friendly warning.",
    "dlg.eranu.waiting": "Their big introduction. Say 'ma waifu' with complete confidence, as though everyone knows the word. [beat]s: she lets that land, then frowns at the door. Finish deadpan: 'Trousers find Coth, an' he runs' is simply a fact.",
    "dlg.eranu.waifu": "She looks straight at the player, daring them to say something. 'He protests. He's wrang.' Case closed. Then right back to business.",
    "dlg.eranu.accept": "'Guid' is one word and a nod. [beat]: she stands up, taller than expected. She knows him so well that the list comes easily. SOFTER ON THE LAST LINE: 'Tell him Eranu says come hame, Cothepoo' is the first crack in the armour. Barely let it show.",
    "dlg.eranu.news": "Worry disguised as instructions. [beat]: her grip tightens on the sword.",
    "dlg.eranu.nickname": "Her mouth twitches: she's almost smiling and refuses to. 'That's how ye ken it's love' is dry and completely sincere.",
    "dlg.eranu.reunion": "Right after the big hug, and she has got herself back under control. 'His' is one quiet word as she hands over the folded trousers. Second [beat]: Coth yells 'I DON'T' behind her, and she ignores him. Third [beat]: she hands over a purse. Warm by the end.",
    "dlg.eranu.join": "[beat]: she glances across the table. 'Dinnae wander aff, Cothepoo' is half threat, half love.",
    "dlg.eranu.wait": "Quiet. She's already heading back to her seat, and her eyes go to the door out of habit.",
    "comp.eranu.idle.1": "Coaching the player, without looking up. The 'Aye' is approval and costs her something.",
    "comp.eranu.idle.5": "No surprise at all. A woman who has said this many times before.",
    "comp.eranu.idle.6": "Called across a distance, like a tired PE teacher. Lean on LEGS.",
    "comp.eranu.combat.4": "Full war cry. This is the one to really let go on.",
    "comp.eranu.kill.1": "Bored. One word, already looking for the next enemy.",
    "comp.eranu.kill.3": "A little joke to herself. She has no idea if it did anything to him. Doesn't matter.",
    "comp.eranu.kill.4": "One satisfied word. Like the last bite of something good.",
    "comp.eranu.heal.2": "You can get a bit of the 'shoutin'' into the line itself.",
    "comp.eranu.heal.3": "Gruff, and it's how she says she cares. 'Get that doon ye' like a mum with soup.",
    "comp.eranu.zone.whistling_wood": "A little rueful. She's still annoyed she didn't go herself.",
    "comp.eranu.zone.here": "QUIET AND SINCERE. A city everyone forgot, in a game about being forgotten. She means every word.",
    "comp.eranu.banter.squire.2": "Perfectly deadpan. She's enjoying herself and won't show it.",
    "comp.eranu.banter.detective.3": "Instant, like she has been waiting for this question.",
    "comp.eranu.banter.statue.2": "Dry. Grout is a stone gargoyle of very few words, and she respects that.",
    "comp.dunstan.banter.stance.1": "Dunstan's sword is absurdly huge. Say this gently, like breaking bad news to a child.",
    "comp.dunstan.banter.stance.3": "Passing down ancient wisdom.",
    "comp.dunstan.banter.mate_eranu.2": "Mate is a bitter herbal tea. She has just taken a sip. You can make a noise first. Pure disgust, carefully measured.",
    "comp.dunstan.banter.mate_eranu.4": "Surprised at herself. She's been converted and resents it.",
    "comp.dunstan.banter.odds.2": "Confident. Dunstan knows otherwise, and his next line lands because she's so sure.",
    # ---------------------------------------------------------------- Coth, in the wood
    "bark.coth_castaway.1": "Lost in thought, staring at nothing. Barely above a whisper.",
    "bark.coth_castaway.2": "Delighted. Announcing company to a rock, like a butler.",
    "dlg.coth_cast.root": "He sees a person and his eyes fill with tears. Start hoarse with disbelief: 'A PERSON.' Build into grand, trembling drama. He has clearly rehearsed 'what year is it?'",
    "dlg.coth_cast.coth": "Absurdly formal, like introducing himself at court. [beat]: he gestures at the stone. Say 'a very proper camp' with real pride.",
    "dlg.coth_cast.three": "This is where the game says he laughs: a long, slightly unhinged laugh. Please record it, right before the words, and take your time. Then real outrage: 'Is this a three-day beard?'",
    "dlg.coth_cast.rock": "He lowers his voice, because Sir Pebbleton is right there. Before the second [beat] he trails off, as if about to reveal something profound. Then, simply: 'He doesn't, actually.' Tender at the end.",
    "dlg.coth_cast.trousers": "Great dignity, like a sailor recalling a lost voyage. Leave a real gap before 'Also.' Then 'ESPECIALLY in winter' goes up, triumphant.",
    "dlg.coth_cast.not_yet": "Serene, stroking his beard, gazing past the player. Nothing can reach him.",
    "dlg.coth_cast.lost_count": "They have been counting, and he got distracted and counted the rock twice. Triumphant. 'As I said' is a man resting his case.",
    "dlg.coth_cast.home": "THE TURN. First [beat] follows 'A thousand years?': the player says three days, and he sits with that. 'Felt like a thousand' is the most honest thing he says, so play it small. Then shake it off. 'You do NOT want Eranu to come looking' is real fear. Next, he picks up Sir Pebbleton and looks at him for a long moment: 'He has a life here' is a real goodbye. No joke at all. Cheer up for the last line.",
    "dlg.coth_cast.marks": "THE BIG ONE. Count slowly, getting quieter with each number. 'That's only three days' is a real shock. '...It was always like this' is a whisper, a man's whole world collapsing. Then snap to bright: 'Well!' Then the same gentle goodbye to Sir Pebbleton, and cheerful on the last line.",
    # ---------------------------------------------------------------- Coth, at home
    "bark.coth.1": "Happily, between mouthfuls. It's a compliment.",
    "bark.coth.2": "Honest confusion. He vaguely recalls the word.",
    "dlg.coth.root": "Plays every time. Delighted to see them, mouth maybe still full of stew.",
    "dlg.coth.settle": "Suspicious and cheerful about it. [beat]: a pause while the thought arrives. Everyone's in on it.",
    "dlg.coth.waifu": "He opens his mouth to protest. Eranu raises one eyebrow about a millimetre. He closes his mouth. Then this one tiny, defeated word. Take a breath first, like you were about to say something. A favourite line, so get a few takes.",
    "dlg.coth.pebbleton": "DON'T PLAY THIS FOR LAUGHS. Staring into his stew. He means it, and that's why it's funny and sad at once.",
    "dlg.coth.join": "Leaps up, scattering stew. Then [beat]: he considers this, and gets serious. He has conditions.",
    "dlg.coth.full": "Fond and a little wistful. 'He was the quiet one' is an old inside joke with himself.",
    "dlg.coth.wait": "Perfectly content. Stew is waiting.",
    "comp.coth.idle.1": "The correction arrives on its own, then he defends it. 'It was a long three days' is quite sincere.",
    "comp.coth.idle.2": "A man trying to convert you to his religion.",
    "comp.coth.idle.3": "Wistful. He misses him.",
    "comp.coth.idle.4": "Getting spooked by his own arithmetic. 'Spooky' in a hushed voice.",
    "comp.coth.idle.6": "Low, not turning around. He really can feel it.",
    "comp.coth.combat.1": "No technique. Just a skinny man running at something. Hold it two seconds or so.",
    "comp.coth.combat.3": "Real panic, and it's completely about the legs.",
    "comp.coth.combat.4": "Pure theatre. He has waited for three days to say this.",
    "comp.coth.kill.2": "Peak joy. This is what freedom sounds like.",
    "comp.coth.heal.3": "Proud and unashamed of where it was kept.",
    "comp.coth.catchup.2": "Genuinely pleased with his progress. 'Not trousers' is quick and under the breath.",
    "comp.coth.zone.bellwether": "Four separate bursts of pure joy.",
    "comp.coth.zone.seal_chamber": "He has dropped the act for a moment. The only room that frightens him.",
    "comp.coth.zone.whistling_wood": "Then call out 'Hello, Sir Pebbleton!' into the trees, warm and hopeful.",
    "comp.coth.zone.here": "A flicker of real feeling under the joke, and it's over quickly.",
    "comp.coth.banter.legs.1": "A war veteran staring into the distance.",
    "comp.coth.banter.legs.3": "Short and heroic, with a pause on each word.",
    "comp.coth.banter.rocks.4": "A eulogy. He's not joking.",
    "comp.coth.banter.snacks.0": "Greeting an equal: the owlbear cub, known as both Snacks and Doobie.",
    "comp.coth.banter.castaway.1": "He finally got a good one in. Enjoy it.",
    "comp.dunstan.banter.kilt.1": "Calm, as if about to deliver a long and reasoned reply.",
    "comp.dunstan.banter.kilt.3": "That was the reply.",
    "comp.dunstan.banter.mate_coth.2": "He has decided, and he won't be argued out of it.",
    "comp.dunstan.banter.mate_coth.4": "Smug. A true expert.",
    "comp.dunstan.banter.desert.1": "Soft, dreamy, eyes closed.",
    "comp.dunstan.banter.desert.3": "Real pity for a lost opportunity.",
    # ---------------------------------------------------------------- Scenes together
    "comp.eranu.banter.waifu.0": "Pleasant. She knows exactly how this ends.",
    "comp.eranu.banter.waifu.1": "Chest out. His finest self. He believes he can win this time.",
    "comp.eranu.banter.waifu.2": "Quieter than the first time, which is much worse for him.",
    "comp.eranu.banter.waifu.3": "All the air leaves him. The tiniest voice you have.",
    "comp.eranu.banter.waifu.4": "Satisfied, and already moving on.",
    "comp.eranu.banter.trousers.2": "He can see it coming. He has heard this one before.",
    "comp.eranu.banter.trousers.3": "One word, then let it hang in the air.",
    "comp.eranu.banter.trousers.4": "A vow, like a king refusing to surrender.",
    "comp.eranu.banter.thousand.0": "SINCERE, the most open she gets. She tries to make it sound like a joke, and it almost works.",
    "comp.eranu.banter.thousand.1": "He hears what she really means. No jokes, just gentle.",
    "comp.eranu.banter.thousand.2": "Quieter still.",
    "comp.eranu.banter.thousand.3": "And he breaks the tension, because somebody has to. Warm, and she knows why he did it.",
    "comp.coth.banter.bark.0": "Bright, sharing a fun fact he learned the hard way.",
    "comp.coth.banter.bark.1": "Patient. She's looking at him and already suspects.",
    "comp.coth.banter.bark.2": "He has just realised this fact doesn't quite help him.",
    "comp.coth.banter.bark.3": "She already knows the answer.",
    "comp.coth.banter.bark.4": "Haunted. The thousand-yard stare of a man who ate bark for three days.",
    # ---------------------------------------------------------------- The reunion
    "story.cothepoo.1": "Door flies open. He has rehearsed this. Announce it to the whole inn, as loudly as you can, with a proud pause at the [beat].",
    "story.cothepoo.2": "Everything she's been holding in for three days. 'COTHEPOO' is the one really big shout she gets, right into his ear. Then it starts to crack. She's still holding him off the floor.",
    "story.cothepoo.3.coth": "Muffled, into her shoulder. A hand over your mouth or your face in your sleeve works. All the theatre is gone. This is the truest thing he says.",
    "story.cothepoo.3.eranu": "Quiet, and nothing like the shout before it. He just said it felt like a thousand years, and she's agreeing: it did for her too. Let her be soft for exactly this long.",
}

# Lines in the reunion cards: (file name, speaker, localization key, indexes of the quotes that speaker has on that page)
REUNION = [("story.cothepoo.1", "COTH", "story.cothepoo.1", (0, 1)),
           ("story.cothepoo.2", "ERANU", "story.cothepoo.2", (0,)),
           ("story.cothepoo.3.coth", "COTH", "story.cothepoo.3", (0,)),
           ("story.cothepoo.3.eranu", "ERANU", "story.cothepoo.3", (1, 2))]

used_notes = set()
line_numbers = []  # (number, speaker, file name, text), in script order, for BadSad's list
next_number = {"ERANU": 0, "COTH": 0}


def heading(text, char="="):
    return ["", char * WIDTH, text, char * WIDTH, ""]


def para(text, indent=""):
    return textwrap.wrap(" ".join(text.split()), WIDTH, initial_indent=indent, subsequent_indent=indent)


def clean(text):
    return " ".join(text.replace(" … ", " [beat] ").split())


def line_block(key, text, who, show_name=False):
    next_number[who] += 1
    number = f"{who[0]}{next_number[who]}"
    line_numbers.append((number, who, key, clean(text)))
    out = [f"{number} - {who}" if show_name else number] + para(f'"{clean(text)}"', "    ")
    note = NOTES.get(key)
    if note:
        used_notes.add(key)
        out += textwrap.wrap("Note: " + " ".join(note.split()), WIDTH, initial_indent="    ", subsequent_indent="          ")
    return out + [""]


def tip_for(title):
    t = title.lower()
    for marker, tip in (("barks", "barks"), ("conversation", "conversation"), ("walking", "idle"), ("in a fight", "combat"), ("after a kill", "kill"),
                        ("healing", "heal"), ("level up", "level"), ("catching", "catchup"), ("first time", "zone")):
        if marker in t:
            return SECTION_TIPS[tip]
    return ""


def short_title(title):
    return title.split(" (")[0].upper()


def sections_for(npc_id, who, label=""):
    out, count = [], 0
    _, sections = vs.lines_for(npc_id)
    for title, rows in sections:
        name = short_title(title) + (f" - {label}" if label else "")
        out += ["", name, "-" * len(name)] + para(tip_for(title)) + [""]
        for key, text in rows:
            out += line_block(key, text, who)
            count += 1
    return out, count


def scene_block(a, b, rows, voices):
    out = ["", f"{a} & {b}", "-" * len(f"{a} & {b}")]
    count = 0
    both = len(voices) > 1
    for key, who, text, _ in rows:
        if who in voices:
            out += line_block(key, text, who, show_name=both)
            count += 1
        else:
            out += para(f'{who}: "{clean(text)}"') + [""]
    return out, count


def reunion_block():
    out, count = _paras(REUNION_NOTES), 0
    for name, who, loc_key, picks in REUNION:
        quoted = [q.strip().rstrip(",") for q in re.findall(r'"([^"]+)"', vs.L[loc_key])]
        out += line_block(name, " … ".join(quoted[i] for i in picks), who, show_name=True)
        count += 1
    return out, count


def main():
    scenes = vs.banter_for(["core:npc.eranu", "core:npc.coth", "core:npc.coth_castaway"])
    both, eranu_only, coth_only = [], [], []
    for a, b, rows in scenes:
        whos = {r[1] for r in rows}
        if {"ERANU", "COTH"} <= whos:
            both.append((a, b, rows))
        elif "ERANU" in whos:
            eranu_only.append((a, b, rows))
        else:
            coth_only.append((a, b, rows))

    rb, n_reunion = reunion_block()
    tb, n_both = [], 0
    for a, b, rows in both:
        blk, c = scene_block(a, b, rows, {"ERANU", "COTH"})
        tb += blk
        n_both += c
    eb, n_eranu = sections_for("core:npc.eranu", "ERANU")
    for a, b, rows in eranu_only:
        blk, c = scene_block(a, b, rows, {"ERANU"})
        eb += blk
        n_eranu += c
    cb1, c1 = sections_for("core:npc.coth_castaway", "COTH", "Lost in the Wood")
    cb2, c2 = sections_for("core:npc.coth", "COTH", "Back Home")
    n_coth = c1 + c2
    for a, b, rows in coth_only:
        blk, c = scene_block(a, b, rows, {"COTH"})
        cb2 += blk
        n_coth += c

    out = ["THE UNCOUNTED", "A voice guide for Coth and Eranu", ""] + _paras(INTRO)
    out += para(f"In total: {n_eranu} lines just for Eranu, {n_coth} just for Coth, plus {n_both + n_reunion} in scenes with each other.")
    out += heading("1. THE STORY YOU'RE IN") + _paras(STORY)
    out += heading("2. PLAYING THEM TOGETHER") + _paras(TOGETHER)
    out += heading("3. PLAYING ERANU") + _paras(ERANU_GUIDE)
    out += heading("4. PLAYING COTH") + _paras(COTH_GUIDE)
    out += heading("5. RECORDING") + _paras(RECORDING)
    out += heading("6. HOW TO READ THE SCRIPT") + READING.strip("\n").split("\n")
    out += heading("7. WHERE TO START") + START_HERE.strip("\n").split("\n")
    out += heading("8. THE REUNION (both of you)") + rb
    out += heading("9. YOUR SCENES WITH EACH OTHER") + _paras(APART) + tb
    out += heading("10. ERANU'S LINES") + eb
    out += heading("11. COTH'S LINES") + cb1 + cb2
    out += heading("THANK YOU", "=")
    out += para("That's everything. Have fun with it, and send your recordings to BadSad. This game is a gift for Toasty, and it'll mean a lot to hear the two of you in it.") + [""]

    missing = sorted(set(NOTES) - used_notes)
    if missing:
        raise SystemExit("Notes for lines not in the script: " + ", ".join(missing))
    with open(OUT, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")
    write_names()
    print(f"Wrote {os.path.relpath(OUT, vs.ROOT)}: Eranu {n_eranu}, Coth {n_coth}, shared {n_both + n_reunion}, notes {len(used_notes)}")


def _paras(text):
    out = []
    for block in text.strip("\n").split("\n\n"):
        out += para(block) + [""]
    return out


def write_names():
    out = ["THE UNCOUNTED: voice file names for Coth and Eranu (for BadSad)", ""]
    out += para("Coth and Eranu say each line's number on their recordings. Cut each line out and name it as listed below, in assets/audio/voice/, as .ogg, .wav or .mp3. The game plays nothing else, so convert any .m4a. Mono, 44.1 or 48 kHz, with half a second of silence at the end. Scene files are named after whoever starts the scene, so some of Coth's lines say 'eranu'; that's correct.") + [""]
    out += heading("THE REUNION CARDS NEED A LITTLE WORK")
    out += _paras("""
The game plays one file per story card, and a voiced card turns by itself 1.4 seconds after its recording ends.

Card 3 has both voices, but the game plays only story.cothepoo.3. Join Coth's line and Eranu's line into that one file, with a pause between them. The names story.cothepoo.3.coth and story.cothepoo.3.eranu below are only labels, and the game won't play them.

Cards 2 and 3 also carry description to read, so add silence to those files or the card may turn too soon. Silence before the line works well: the player reads about the hug first, then hears the shout.
""")
    for who, title in (("ERANU", "ERANU"), ("COTH", "COTH")):
        out += heading(title)
        for number, speaker, key, text in line_numbers:
            if speaker == who:
                out.append(f"{number:<6}{key}")
                out += textwrap.wrap(text, WIDTH, initial_indent="      ", subsequent_indent="      ")
        out.append("")
    with open(OUT_NAMES, "w", encoding="utf-8-sig", newline="\r\n") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()

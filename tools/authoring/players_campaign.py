"""The Bellwether Players: a four-quest theatre campaign written to be read aloud.

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends.
Kept as a worked example of the Dlg helper (auto-generated localization keys) for writing long dialogue.

Adds quests, campaign, NPCs (Odette, Mortimer), items, dialogue (with auto-generated localization keys), and the
recruit/rehearsal/prop topics in existing characters' conversations. Run once from the repo root."""
import json

ROOT = "."
def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}  # new localization strings

# ---------------------------------------------------------------- conditions / actions
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
QE = lambda q, s: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda q, s: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda q, s: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FL = lambda fl, v: {"type": "flags_at_least", "flags": fl, "value": v}
FF = lambda fl, v: {"type": "flags_fewer_than", "flags": fl, "value": v}
HI = lambda i: {"type": "has_item", "item_id": i}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
XP = lambda k, a: {"type": "give_xp", "skill": k, "amount": a}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
GG = lambda a: {"type": "give_gold", "amount": a}
SQ = lambda q, s: {"type": "set_quest_stage", "quest_id": q, "stage": s}

Q1, Q2, Q3, Q4 = ("core:quest.players_casting", "core:quest.players_script", "core:quest.players_rehearsal",
                  "core:quest.players_opening")
CAST = ["cast_baggy", "cast_rolf", "cast_ashgrave", "cast_hollis", "cast_sabrino", "cast_marta", "cast_fenwick", "cast_oakhaven"]
PAGES = ["page_1", "page_2", "page_3", "page_4", "page_5"]
DUEL = ["critic_r1", "critic_r2", "critic_r3"]
REH = ["reh_baggy", "reh_rolf", "reh_ashgrave", "reh_hollis", "reh_sabrino", "reh_marta", "reh_fenwick", "reh_oakhaven"]
PROPS = ["prop_crown", "prop_dragon", "prop_effects"]
GOOD = ["show_good_1", "show_good_2", "show_good_3", "show_good_4", "show_good_5", "show_good_6"]

ODETTE, MORT = "npc.odette.name", "npc.mortimer.name"
NAMES = {"marta": "npc.innkeeper_marta.name", "baggy": "npc.detective_baggy.name", "rolf": "npc.werewolf_rolf.name",
         "ashgrave": "npc.vampire_ashgrave.name", "hollis": "npc.hunter_hollis.name", "sabrino": "npc.witch_sabrino.name",
         "fenwick": "npc.librarian_fenwick.name", "oakhaven": "npc.clerk_oakhaven.name"}


class Dlg:
    """Builds a dialogue whose text lives in localization under `prefix`."""
    def __init__(self, did, speaker, prefix, nodes=None):
        self.id, self.speaker, self.prefix = did, speaker, prefix
        self.nodes = nodes if nodes is not None else {}

    def node(self, nid, text, choices, actions=None, speaker=None):
        key = f"{self.prefix}.{nid}"
        S[key] = text
        n = {"speaker_key": speaker or self.speaker, "text_key": key}
        if actions:
            n["actions"] = actions
        n["choices"] = [self.choice(nid, i, c) for i, c in enumerate(choices)]
        self.nodes[nid] = n
        return self

    def choice(self, nid, i, c):
        text, nxt = c[0], c[1]
        opts = c[2] if len(c) > 2 else {}
        key = f"{self.prefix}.{nid}.c{i}"
        S[key] = text
        out = {"text_key": key, "next": nxt}
        for k in ("conditions", "actions", "roll"):
            if k in opts:
                out[k] = opts[k]
        return out

    def json(self, root="root"):
        return {"id": self.id, "root_node": root, "nodes": self.nodes}


def C(text, nxt, cond=None, actions=None, roll=None):
    o = {}
    if cond: o["conditions"] = cond
    if actions: o["actions"] = actions
    if roll: o["roll"] = roll
    return (text, nxt, o)


BACK = lambda r="root": C('"Let\'s get back to it."', r)
LEAVE = C('"I\'ll be going."', "END")

# ================================================================ ODETTE
od = Dlg("core:dialogue.odette", ODETTE, "dlg.odette")
od.node("root",
    "A small woman in a very large magenta hat sweeps towards you with both arms out, a silver-topped cane in one hand and "
    "a feather boa trailing behind her like a comet's tail.\n\n"
    "\"DARLING. Look at you. Look at that FACE. That is a face that has suffered. That is a face that has been declared "
    "legally deceased. You,\" she jabs the cane at your nose, \"are exactly what the theatre has been missing.\"",
    [C('"Who are you?"', "who"),
     C('"I\'m here about the casting call."', "aud_1", [QB(Q1, 10)], [SQ(Q1, 0)]),
     C('"Who do we still need for the cast?"', "cast_status", [QE(Q1, 10)]),
     C('"The cast is assembled, Madame."', "cast_done", [QE(Q1, 10), FL(CAST, 4)]),
     C('"Any news about the stolen script?"', "script_status", [QA(Q2, 0), QB(Q2, 20)]),
     C('"I got the script back from Mortimer Quill."', "script_back", [QE(Q2, 20)]),
     C('"Ready to rehearse, Madame."', "reh_hub", [QE(Q3, 0)]),
     C('"How are the props coming along?"', "props_status", [QE(Q3, 10)]),
     C('"We have a crown, a dragon and something that goes bang."', "props_done", [QE(Q3, 10), FL(PROPS, 3)]),
     C('"Curtain up. Let\'s do this."', "show_open", [QE(Q4, 0)]),
     C('"About last night, Madame..."', "after", [QA(Q4, 100)]),
     LEAVE])
od.node("who",
    "\"Madame Odette Velour! Impresario! Director! Visionary! Founder, owner and, as of last Tuesday, sole remaining member "
    "of the Velour Travelling Players!\"\n\n"
    "She lowers her voice. \"The rest of the troupe left over artistic differences. Mostly about being paid. Philistines.\"\n\n"
    "\"I have a cart, a costume trunk, and the greatest play ever written. The Tragedie of the Uncounted King. Five acts. "
    "Two intervals. One dragon. All I need now is a cast. And a lead.\" The cane swings round to point at you again. "
    "\"Hmm? HMM?\"",
    [BACK()])
# --- Audition
od.node("aud_1",
    "Odette thrusts a crumpled sheet of paper into your hands and retreats three paces, framing you with her fingers.\n\n"
    "\"The Great Speech of the Uncounted King. Act Five. Read it to me, darling. From the top. Make me FEEL something.\"\n\n"
    "The paper reads:\n\n"
    "    Though the ledger strike my name, though the ink run dry,\n"
    "    Though every clerk in every hall forget that I was I,\n"
    "    I stand here still, I breathe here still, and this I swear:\n"
    "    A name held true by one who loves is never truly bare.\n\n"
    "\"How will you play it?\"",
    [C("[Dramatic] Fling one arm at the heavens and bellow every word.", "aud_2", actions=[SF("style_dramatic")]),
     C("[Haunted] Whisper it, as if the words might break.", "aud_2", actions=[SF("style_whisper")]),
     C("[As Sabrino] Do it as a flamboyant Italian witch. With hand gestures.", "aud_2", actions=[SF("style_sabrino")]),
     C("[As Baggy] Do it as a nervous detective who has just found a clue.", "aud_2", actions=[SF("style_baggy")]),
     C("[As Hollis] Read the whole thing, then say \"Hmm.\"", "aud_2", actions=[SF("style_hollis")])])
od.node("aud_2",
    "Odette has gone very still. Her hand is pressed to her heart. A single tear is making its way through a remarkable "
    "quantity of face powder.\n\n"
    "\"That,\" she says at last, \"was a CHOICE. I have seen kings weep and dwarves faint and once a goose stand up and "
    "applaud, and I have never seen anything like that.\"\n\n"
    "She snaps back to business. \"Now. The last line. Act Five, the King stands before the Bureau itself, and cries: "
    "'I AM COUNTED!' It is the line that brings the house down. Give me EVERYTHING you have.\"",
    [C("[Presence] Take a breath. Give it everything. \"I AM COUNTED!\"", "aud_win",
       actions=[XP("persuasion", 30)], roll={"skill": "persuasion", "dc": 12, "fail_next": "aud_flub"}),
     C("[Play it safe] Say it clearly, with quiet dignity.", "aud_safe")])
od.node("aud_win",
    "Your voice rings off the rooftops of Bellwether. Somewhere a dog barks back. Three windows open. Marta, in the inn "
    "doorway, drops a loaf.\n\n"
    "Odette is applauding with her whole body. \"BRAVO! BRAVISSIMO! The rafters, darling, you hit the RAFTERS, and we're "
    "outdoors!\"",
    [C('"So... did I get the part?"', "aud_3")])
od.node("aud_flub",
    "You take a mighty breath, open your mouth, and what comes out is: \"I AM CUCUMBER!\"\n\n"
    "There is a long silence. Somewhere, a crow laughs.\n\n"
    "Odette doesn't blink. \"Interesting. INTERESTING. A bold reinterpretation. The King, in his hour of despair, "
    "identifies with a humble vegetable. It's avant-garde. It's subversive. We'll workshop it.\"",
    [C('"So... did I get the part?"', "aud_3")])
od.node("aud_safe",
    "\"I am counted,\" you say, quietly and clearly, and for a moment the rain seems to hush to listen.\n\n"
    "Odette lowers her cane. \"Oh,\" she says softly. \"Oh, that's lovely. Understated. Nobody ever does it understated.\" "
    "Then, briskly: \"Louder on the night, though. The back row is always full of farmers.\"",
    [C('"So... did I get the part?"', "aud_3")])
od.node("aud_3",
    "\"Did you get the part? DARLING. You were always going to get the part. The only other person who auditioned was a "
    "goat, and it ate the script.\"\n\n"
    "She produces a long list. \"Now! A play needs a cast. Prince Valiant, the Ghost of the Old King, the Dragon, a Herald, "
    "a Narrator, a Second Guard, a prompter and somebody who knows about fire. I have none of these. You know everyone in "
    "this soggy little town. Go and find me at least four. Charm them! Bribe them! Lie to them about the money!\"",
    [C('"Leave it to me."', "END")], [SQ(Q1, 10), XP("persuasion", 20)])
od.node("cast_status",
    "Odette consults her list with a monocle she was not wearing a moment ago.\n\n"
    "\"PRINCE VALIANT: dashing, heroic, ideally owns a sword. THE GHOST OF THE OLD KING: pale, tragic, good at standing "
    "very still. THE DRAGON: large, menacing, one line. THE HERALD: loud, official, fond of paperwork. THE NARRATOR: a "
    "commanding voice, a love of words. THE SECOND GUARD: anyone, honestly. A PROMPTER: somebody who remembers everything "
    "and whispers well. And PYROTECHNICS: somebody who is not afraid of fire, or the law.\"\n\n"
    "She lowers the monocle. \"Four at the very least. Eight if you love me.\"",
    [BACK()])
od.node("cast_done",
    "Odette counts your recruits on her fingers, then counts them again, then hugs you so hard your spine makes a noise.\n\n"
    "\"A CAST! A real cast! Do you know how long it has been since I had a cast that wasn't me in four different hats?\"\n\n"
    "She flings open her costume trunk with a flourish. \"And now, the script! The only copy of The Tragedie of the "
    "Uncounted King, written in my own fair hand, bound in velvet, kept safe in...\"\n\n"
    "The trunk is empty except for a single card. On it, in spidery red ink: \"One and a half stars. Derivative. - M.Q.\"\n\n"
    "Odette screams. It is, you have to admit, an excellent scream. Very well projected.",
    [C('"Who is M.Q.?"', "stolen")], [SQ(Q1, 100)])
od.node("stolen",
    "\"MORTIMER QUILL.\" She spits the name like a bad oyster. \"The most feared critic in the history of the stage. He "
    "panned my first play, my second play, and my wedding. He gave the moon two stars. He said the sea was 'overlong'.\"\n\n"
    "\"He has been dead for two hundred years, darling. It hasn't slowed him down.\"\n\n"
    "She grips your sleeve. \"He'll have torn it up. He always tears them up. He scatters the pages wherever he goes, like "
    "a toddler with opinions. Find them. Find the pages, find Mortimer, and get my play BACK.\"",
    [C('"I\'ll find every page."', "END")], [SQ(Q2, 0), XP("lore", 20)])
od.node("script_status",
    "\"Five pages, darling, five! He'll have strewn them across the whole province. Look anywhere dusty, gloomy, or "
    "important. Critics adore all three.\"\n\n"
    "\"And when you've found the trail's end, you'll find HIM. Some draughty old house, no doubt, full of books to sneer at.\"",
    [BACK()])
od.node("script_back",
    "You hand Odette the velvet-bound script. She holds it to her chest, rocks it like a baby, and kisses the cover three "
    "times.\n\n"
    "\"My PLAY. My beautiful, bruised, heavily annotated play.\" She flips it open and her eyebrows climb. \"He's written in "
    "the margins. In red. 'Act Three: needs a dragon.' Well. It HAS a dragon. 'Then it needs a better one.' Hmph.\"\n\n"
    "\"Now. We need a rehearsal space. Something grand. Atmospheric. Haunted, ideally. I hear there's a manor south of town "
    "with a ballroom and its own ghost.\" She is already walking. \"Meet me at Hollowmere, darling! Bring the cast! Bring "
    "SNACKS!\"",
    [C('"See you at Hollowmere."', "END")],
    [SQ(Q2, 100), SQ(Q3, 0), SF("players_at_hollowmere"), GI("core:item.script_tragedie"), XP("lore", 40)])
# --- Rehearsal hub: one scene per cast member present
od.node("reh_hub",
    "Odette has turned the Hollowmere ballroom into a theatre: a low stage at the far end, chalk marks on the floor, a "
    "folding chair labelled DIRECTOR in letters a foot high.\n\n"
    "\"PLACES, everyone! Act One, Scene One!\" Nobody moves to their places. Somebody is on fire, briefly. \"Darling, you're "
    "the lead. Leads solve problems. Who shall we deal with first?\"",
    [C("Deal with Rolf, who has a question about the costume.", "reh_rolf", [FS("cast_rolf"), FN("reh_rolf")]),
     C("Deal with Lord Ashgrave, who has notes on his death scene.", "reh_ashgrave", [FS("cast_ashgrave"), FN("reh_ashgrave")]),
     C("Deal with Hollis, who will not roar.", "reh_hollis", [FS("cast_hollis"), FN("reh_hollis")]),
     C("Deal with Baggy, who is investigating the scenery.", "reh_baggy", [FS("cast_baggy"), FN("reh_baggy")]),
     C("Deal with Sabrino and the small fire.", "reh_sabrino", [FS("cast_sabrino"), FN("reh_sabrino")]),
     C("Deal with Marta, whose prompting is very loud.", "reh_marta", [FS("cast_marta"), FN("reh_marta")]),
     C("Deal with Fenwick, who keeps shushing the actors.", "reh_fenwick", [FS("cast_fenwick"), FN("reh_fenwick")]),
     C("Deal with Clerk Oakhaven, who has stopped the rehearsal.", "reh_oakhaven", [FS("cast_oakhaven"), FN("reh_oakhaven")]),
     C('"I think we\'re ready, Madame."', "reh_done", [FL(REH, 3)]),
     C('"Give me a minute."', "END")])
od.node("reh_rolf",
    "ROLF (holding up a frilly white shirt with enormous puffed sleeves): \"Madame Odette says Prince Valiant wears THIS.\"\n\n"
    "He turns it round. It has a ruff. \"I'm a werewolf. If I get excited during the sword fight, I change. If I change, "
    "this shirt explodes. That'll be shirt number forty-two.\" He looks at you with enormous golden eyes. \"What do I do?\"",
    [C("[Practical] \"Wear it. If it explodes, it explodes. That's live theatre.\"", "reh_rolf_2", actions=[SF("reh_rolf")]),
     C("[Kind] \"Go shirtless. It's a bold artistic choice. Odette will love it.\"", "reh_rolf_3", actions=[SF("reh_rolf")]),
     C("[Sneaky] \"Put the shirt on Ashgrave instead and see what happens.\"", "reh_rolf_4", actions=[SF("reh_rolf")])],
    speaker=NAMES["rolf"])
od.node("reh_rolf_2", "Rolf puts the shirt on with tremendous solemnity. The ruff frames his jaw. He looks, unfortunately, magnificent.\n\n"
    "ODETTE (from the director's chair): \"YES. That's my prince. Do NOT get excited.\"\n\nROLF: \"I'm already a bit excited.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["rolf"])
od.node("reh_rolf_3", "ODETTE (rising slowly from the director's chair): \"A shirtless prince. Raw. Primal. Unprecedented.\" She sits back "
    "down. \"I hate that I love it.\"\n\nRolf flexes, very slightly, in the direction of the upstairs gallery. Somebody up "
    "there drops a candlestick.", [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_rolf_4", "Five minutes later Lord Ashgrave is wearing a frilly white shirt with a ruff. He has caught sight of himself in a "
    "mirror and appears to be having a crisis.\n\nASHGRAVE: \"I look like a wedding cake. A HAPPY wedding cake.\"\n\n"
    "ROLF (very quietly): \"...You look nice.\"\n\nNobody speaks for a while.", [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_ashgrave",
    "LORD ASHGRAVE (lying flat on the stage, arms folded across his chest): \"I have notes on my death scene.\"\n\n"
    "He raises one finger without opening his eyes. \"The script says, 'The Ghost of the Old King fades away.' Fades. Away. "
    "Three hundred years of brooding, and I am asked to simply FADE.\" He sits bolt upright. \"A death scene should last at "
    "least forty minutes. There should be a monologue. There should be WEATHER.\"",
    [C("[Diplomatic] \"Ten minutes. With weather. Final offer.\"", "reh_ash_2", actions=[SF("reh_ashgrave")]),
     C("[Flattering] \"Less is more. You could do it with one look. Only you could.\"", "reh_ash_3", actions=[SF("reh_ashgrave")]),
     C("[Blunt] \"Two minutes, Ashgrave. People have dinners to get home to.\"", "reh_ash_4", actions=[SF("reh_ashgrave")])],
    speaker=NAMES["ashgrave"])
od.node("reh_ash_2", "ASHGRAVE: \"Ten minutes.\" He considers. \"With thunder?\"\n\nYOU: \"With thunder.\"\n\nASHGRAVE: \"And a single tear?\"\n\n"
    "YOU: \"Two tears, if you can manage it.\"\n\nASHGRAVE (lying back down, satisfied): \"I can manage nine.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["ashgrave"])
od.node("reh_ash_3", "Ashgrave opens his eyes. He looks at you for a very long time, with the full weight of three centuries of tragedy.\n\n"
    "Then he looks at the empty seats, just once, the way you'd look at the sea.\n\n"
    "Odette, in the director's chair, has quietly started crying. \"Fine,\" she sniffs. \"FINE. One look. Keep the look.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_ash_4", "ASHGRAVE: \"Two minutes.\" He sits up very slowly. \"Two. Minutes.\"\n\n\"In my day, people died properly. Over "
    "several days. In verse.\" He lies back down. \"I shall do it in two minutes. And it will be the longest two minutes "
    "of their lives.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["ashgrave"])
od.node("reh_hollis",
    "HOLLIS (in a dragon costume made of a green blanket and two oven gloves, arms folded): \"No.\"\n\n"
    "ODETTE: \"It says ROAR, darling. In capitals. With three exclamation marks.\"\n\n"
    "HOLLIS: \"I don't roar. I've killed eleven real dragons. None of them roared. They hissed, mostly. One of them coughed.\"\n\n"
    "He looks at you. \"Hmm.\"",
    [C("[Encouraging] \"Just do your normal 'Hmm', but louder. Make it menacing.\"", "reh_hol_2", actions=[SF("reh_hollis")]),
     C("[Bargain] \"Roar once, properly, and I'll play you at cards afterwards.\"", "reh_hol_3", actions=[SF("reh_hollis")]),
     C("[Respect] \"Play it your way. Show them what a real dragon sounds like.\"", "reh_hol_4", actions=[SF("reh_hollis")])],
    speaker=NAMES["hollis"])
od.node("reh_hol_2", "Hollis takes a deep breath, fills his chest, and delivers the loudest, most menacing \"HMMMMMMM\" ever heard in the "
    "Marches. The chandelier rattles. A Wailing Footman in the next room drops a tray.\n\nODETTE (very quietly): \"...That'll do.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_hol_3", "HOLLIS (instantly): \"Deal.\"\n\nHe throws back his head and ROARS. It is genuinely terrifying. Two candles go out. "
    "Ashgrave hides behind a curtain. Rolf's ears go flat.\n\nHollis lowers his head. \"Hmm. Deal the cards.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["hollis"])
od.node("reh_hol_4", "Hollis drops into a low crouch in his blanket. He doesn't roar. He just goes absolutely, completely still, and "
    "breathes, slowly, through his nose.\n\nIt is the most frightening thing you've ever seen on a stage. Odette has "
    "climbed onto her chair.\n\nHOLLIS (standing up, brushing off the oven gloves): \"That's what they do right before.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["hollis"])
od.node("reh_baggy",
    "BAGGY (crawling around the back of the stage with a magnifying glass): \"Don't mind me! Investigating! This painted "
    "castle backdrop has a door in it, but the door doesn't open. Why would a castle have a door that doesn't open? "
    "Who are they keeping OUT?\"\n\n"
    "ODETTE: \"It's SCENERY, darling.\"\n\n"
    "BAGGY: \"That's exactly what a suspicious door would want us to think.\"",
    [C("[Join in] Get down and investigate with Baggy.", "reh_bag_2", actions=[SF("reh_baggy")]),
     C("[Redirect] \"Baggy, the Second Guard investigates. That's your character's whole thing.\"", "reh_bag_3", actions=[SF("reh_baggy")]),
     C("[Remind] \"Baggy. Your line. Do you remember your line?\"", "reh_bag_4", actions=[SF("reh_baggy")])],
    speaker=NAMES["baggy"])
od.node("reh_bag_2", "The two of you crawl round the backdrop for a while, Odette screaming the whole time. Eventually you find that the "
    "painted door has a small real hinge, and behind it, a small real cupboard, and in the cupboard, a small real bottle of "
    "wine with a note: 'For opening night. Don't tell Odette. - the previous cast.'\n\n"
    "BAGGY (holding it up, beaming): \"Case CLOSED.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["baggy"])
od.node("reh_bag_3", "Baggy's eyes widen. \"The Second Guard... is a detective.\" The magnifying glass trembles. \"Method acting. I've "
    "been method acting this ENTIRE time.\"\n\nBaggy stands, squares both shoulders, and adds, with enormous dignity: "
    "\"Who goes there. And WHY.\"\n\nODETTE: \"...Keep the 'and why'.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["baggy"])
od.node("reh_bag_4", "BAGGY: \"My line. Yes. Of course I remember my line. My line is... 'Who goes there.'\" A pause. \"Who GOES there. "
    "WHO goes there. Who goes THERE. Who goes there?\" Another pause. \"Which one's right? They're all right, aren't they? "
    "That's the problem with a good line.\"\n\nYou spend twenty minutes on 'Who goes there.' It is, in the end, perfect.",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["baggy"])
od.node("reh_sabrino",
    "The left-hand curtain is on fire. Sabrino is standing next to it, beaming, with a ladle.\n\n"
    "SABRINO: \"It is FINE. It is a rehearsal fire. It is practising.\" The fire gets bigger. \"For the dragon scene! I am "
    "testing the special effects! Fireworks in Act Three, a little smoke in Act Four, and for the finale...\" Sabrino makes "
    "an explosion noise with both hands.\n\n"
    "ODETTE (from behind her chair): \"THE CURTAINS ARE VELVET.\"",
    [C("[Calm] Put the fire out with Sabrino's soup pot. Discuss safety afterwards.", "reh_sab_2", actions=[SF("reh_sabrino")]),
     C("[Enthusiastic] \"Bigger! The back row deserves to feel the heat!\"", "reh_sab_3", actions=[SF("reh_sabrino")]),
     C("[Bureaucratic] \"Have you filed the correct pyrotechnics form?\"", "reh_sab_4", actions=[SF("reh_sabrino")])],
    speaker=NAMES["sabrino"])
od.node("reh_sab_2", "The fire goes out with a hiss and a smell of minestrone. Sabrino looks into the empty pot, heartbroken.\n\n"
    "SABRINO: \"That was dinner.\"\n\nODETTE: \"That was my CURTAIN.\"\n\nSABRINO (brightening): \"Then tonight, we eat the curtain. "
    "I can do things with velvet. You would be amazed.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["sabrino"])
od.node("reh_sab_3", "SABRINO: \"FINALLY. Somebody who UNDERSTANDS.\"\n\nThe fire gets very much bigger. Then it turns green. Then it "
    "turns into the shape of a goose, honks once, and goes out on its own.\n\nEveryone stares at Sabrino. Sabrino stares at "
    "the smoke. \"...I did not do that,\" Sabrino says. \"I am going to take the credit, but I did not do that.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["sabrino"])
od.node("reh_sab_4", "SABRINO: \"A FORM?\" Sabrino's hat quivers with outrage. \"I have set fire to the finest stages in seven kingdoms! "
    "I have never filled in a form in my LIFE!\"\n\nFrom the side of the stage, Clerk Oakhaven, or the memory of him, coughs "
    "meaningfully. Sabrino puts the fire out with one finger, extremely sulkily.", [C("Back to the rehearsal.", "reh_hub")],
    speaker=NAMES["sabrino"])
od.node("reh_marta",
    "MARTA (from the prompter's box, at a volume that could stop a cart): \"LINE: 'THOUGH THE LEDGER STRIKE MY NAME.'\"\n\n"
    "Everyone flinches.\n\n"
    "MARTA: \"Sorry. Sorry! I'm used to calling orders across a full tavern.\" She clears her throat and tries again, in "
    "what she clearly thinks is a whisper: \"LINE: 'THOUGH THE LEDGER-'\"",
    [C("[Gentle] Show Marta how to whisper so only the actor can hear.", "reh_mar_2", actions=[SF("reh_marta")]),
     C("[Inspired] \"Keep it loud. Make it part of the show. The audience will love you.\"", "reh_mar_3", actions=[SF("reh_marta")]),
     C("[Honest] \"Marta, you could just learn the lines and come on stage.\"", "reh_mar_4", actions=[SF("reh_marta")])],
    speaker=NAMES["marta"])
od.node("reh_mar_2", "You crouch by the prompter's box and show her: lips close, breath soft, words shaped rather than spoken. Marta "
    "practises. By the fifth try it's perfect: a voice right at your ear, warm and sure, like someone reading you a story.\n\n"
    "MARTA (whispering, smiling): \"I used to read to Ilse like this. Funny what your mouth remembers.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["marta"])
od.node("reh_mar_3", "ODETTE: \"A PROMPTER WHO IS PART OF THE PLAY. A chorus of one! A Greek tragedy with a bakery! Oh, I'm going to "
    "be SO FAMOUS.\"\n\nMarta looks pleased and alarmed in equal measure. \"So I just... shout the lines? On purpose?\"\n\n"
    "ODETTE: \"WITH CONVICTION.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_mar_4", "Marta goes red to the ears. \"On the STAGE? Me?\" She looks at the boards, at the lights, at the empty chairs. "
    "\"I'm a baker. I'm not... I don't...\"\n\nThen, quietly: \"I'll stay in the box. But thank you for asking. Nobody's ever "
    "asked.\" She squeezes your hand. \"LINE,\" she whispers, perfectly, \"'THOUGH THE LEDGER STRIKE MY NAME.'\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["marta"])
od.node("reh_fenwick",
    "FENWICK (from the narrator's lectern, every time anyone speaks): \"SHH!\"\n\n"
    "ROLF: \"I'm not even-\"\n\nFENWICK: \"SHHH!\"\n\nODETTE: \"Darling, you are the NARRATOR, the actors are SUPPOSED to talk-\"\n\n"
    "FENWICK: \"I have spent forty years in a library. I cannot hear voices in a room full of words without shushing them. "
    "It is a REFLEX.\"",
    [C("[Clever] Give Fenwick a bell to ring instead. One ring per shush.", "reh_fen_2", actions=[SF("reh_fenwick")]),
     C("[Patient] Hold a reading of the script, library-style. Silent. Turn the pages together.", "reh_fen_3", actions=[SF("reh_fenwick")]),
     C("[Bribe] \"Sabrino has your cookbook. You can have it back after the show.\"", "reh_fen_4", actions=[SF("reh_fenwick")])],
    speaker=NAMES["fenwick"])
od.node("reh_fen_2", "Fenwick rings the bell. Then rings it again. Then rings it in a little rhythm. By the end of the scene he is "
    "accompanying the entire sword fight on bell, with tremendous dramatic timing.\n\nODETTE: \"...Keep the bell. Keep ALL of "
    "the bell.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=ODETTE)
od.node("reh_fen_3", "For one strange, peaceful half-hour the whole cast sits on the edge of the stage and reads the script in total "
    "silence, turning pages together. Hollis reads with his lips moving. Ashgrave weeps quietly at Act Two. Rolf falls "
    "asleep on Baggy's shoulder.\n\nFENWICK (closing the script, whispering): \"There. Now you understand it. Now you can "
    "make noise.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["fenwick"])
od.node("reh_fen_4", "Fenwick stops mid-shush. His mouth stays in the shape of the 'sh' for several seconds.\n\n"
    "FENWICK: \"The cookbook. ELEVEN YEARS OVERDUE.\" He straightens his robe with trembling dignity. \"I shall narrate like "
    "no narrator has ever narrated. I shall narrate the paint off the walls.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["fenwick"])
od.node("reh_oakhaven",
    "CLERK OAKHAVEN (standing centre stage, holding up one hand): \"I'm afraid I must stop the rehearsal.\"\n\n"
    "ODETTE: \"WHY.\"\n\n"
    "OAKHAVEN: \"Form 12-F, Fire Safety in Places of Public Entertainment. Section three: 'No live flames within six feet of "
    "any curtain.' Section four: 'No dragons.'\" He looks at Hollis in the blanket. \"I'll need to see the dragon's papers.\"",
    [C("[Bureaucratic] Fill in Form 12-F on the spot, in triplicate.", "reh_oak_2", actions=[SF("reh_oakhaven")]),
     C("[Theatrical] \"The dragon is a metaphor, Oakhaven. For grief.\"", "reh_oak_3", actions=[SF("reh_oakhaven")]),
     C("[Distract] \"Oakhaven, your Herald costume has a very official hat.\"", "reh_oak_4", actions=[SF("reh_oakhaven")])],
    speaker=NAMES["oakhaven"])
od.node("reh_oak_2", "You fill in Form 12-F in triplicate, while the whole cast watches in silence. Under 'Nature of dragon' you write "
    "'Hollis.' Under 'Is the dragon licensed?' you write 'He has eleven real ones on his record.'\n\nOakhaven reads it twice, "
    "stamps it, and hands it back with real respect. \"Exemplary. You have the soul of a clerk.\"",
    [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["oakhaven"])
od.node("reh_oak_3", "OAKHAVEN: \"A metaphor.\" He writes it down. \"For grief.\" He writes that down too. He looks at Hollis for a long "
    "time. Hollis looks back, in his oven gloves.\n\nOAKHAVEN (quietly): \"There's no form for grief.\" He closes his folder. "
    "\"Carry on.\"", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["oakhaven"])
od.node("reh_oak_4", "Oakhaven looks at the Herald's hat: three tiers, gold braid, a plume like a startled pheasant. He puts it on. He "
    "looks in the mirror.\n\nOAKHAVEN: \"The fire safety inspection is concluded. Everything is fine. I am the Herald.\"\n\n"
    "He does not take the hat off for the rest of the day.", [C("Back to the rehearsal.", "reh_hub")], speaker=NAMES["oakhaven"])
od.node("reh_done",
    "Odette climbs onto her director's chair and claps her hands three times.\n\n"
    "\"That's a WRAP on rehearsal, my darlings! You are a disaster. A beautiful, magnificent disaster. Which is exactly what "
    "every great company is the night before it opens.\"\n\n"
    "She turns to you. \"Props, darling! We need three. A CROWN for the King. A DRAGON costume that isn't a blanket. And "
    "SOMETHING THAT GOES BANG for Act Three. Get them, and we open!\"",
    [C('"A crown, a dragon, and a bang. On it."', "END")], [SQ(Q3, 10), XP("persuasion", 40)])
od.node("props_status",
    "\"A CROWN: the King must have a crown. Paper will do, gold would be better, a crown with a story would be best.\n\n"
    "A DRAGON: that blanket is an insult to dragons. Try the quartermaster. He sells everything.\n\n"
    "SOMETHING THAT GOES BANG: fireworks, thunder, a controlled explosion. Ask the witch. Or a clerk, clerks confiscate "
    "everything.\"",
    [C("[Offer the Rat King's crown] \"Will a real crown do? It was a rat's.\"", "props_ratcrown", [HI("core:item.rat_crown"), FN("prop_crown")]),
     BACK()])
od.node("props_ratcrown",
    "Odette holds the tiny golden crown up to the light. \"A real crown. Taken from a real king. In real combat.\" She lowers "
    "her voice. \"Was it a very large rat?\"\n\nYou nod. She sighs with deep satisfaction. \"Method props. Divine. I'll give it "
    "back after the show, darling.\"",
    [BACK()], [SF("prop_crown"), SF("prop_real_crown")])
od.node("props_done",
    "Odette lays them out on the edge of the stage like holy relics: the crown, the dragon, the thing that goes bang.\n\n"
    "\"We have a theatre. We have a cast. We have a script, however annotated. We have props.\" She turns to you, eyes "
    "shining. \"And we have a lead.\"\n\n"
    "\"Tonight, darling. The Tragedie of the Uncounted King. Opening night. Mortimer Quill has promised to attend, which "
    "means he's promised to hate it.\" She grips your hands. \"Let's make him hate it LESS.\"",
    [C('"Tell me when it\'s curtain up."', "END")], [SQ(Q3, 100), SQ(Q4, 0)])

# ---------------------------------------------------------------- THE SHOW
od.node("show_open",
    "The Hollowmere ballroom is full. Every borrowed chair is taken; people are standing at the back, sitting on the stairs, "
    "hanging off the gallery. Somewhere in the third row, a pale figure in a top hat sits with a notebook open and a red quill "
    "poised. Mortimer Quill.\n\n"
    "Odette steps in front of the curtain and the room goes quiet.\n\n"
    "ODETTE: \"Ladies, gentlemen, ghosts and assorted others. The Velour Players present: The Tragedie of the Uncounted King!\"\n\n"
    "The curtain rises. You are standing in a pool of light. Two hundred faces look at you. Your mouth is completely dry.",
    [C("[Breathe] Find one friendly face in the crowd, and begin.", "act1", actions=[SF("show_good_1")]),
     C("[Bow first] Take a deep, theatrical bow before saying a single word.", "act1", actions=[SF("show_good_1")]),
     C("[Freeze] Stare at the audience in silent terror.", "act1_freeze")])
od.node("act1_freeze",
    "You open your mouth. Nothing comes out. The silence goes on for long enough that somebody coughs. Then a little longer. "
    "Mortimer Quill writes something down.\n\n"
    "From the prompter's box, a voice right at your ear, warm and sure: \"Line. 'I wake. And no one knows my name.'\"\n\n"
    "And suddenly, you do remember. Of course you do.",
    [C("\"I wake. And no one knows my name.\"", "act1")])
od.node("act1",
    "ACT ONE. The stage is the inside of a great ledger, pages towering like walls. You are the Uncounted King, waking in the "
    "margin of a book where your name has been struck out.\n\n"
    "THE NARRATOR: \"Once there was a King whom all the world forgot. Not by war, nor plague, nor the slow grey dust of years, "
    "but by a single stroke of ink.\"\n\n"
    "The script says the King now delivers a sorrowful line. The audience is waiting.",
    [C("[As written] \"Who struck my name? Who dares to strike a king?\"", "act2", actions=[SF("show_good_2")]),
     C("[Improvise] \"Is this the Bureau? I'd like to file a complaint.\"", "act1_laugh"),
     C("[Your audition voice] Deliver it exactly the way you did for Odette.", "act1_style")])
od.node("act1_laugh",
    "The audience laughs. Then laughs harder. Somebody in the back shouts \"FORM 27-B!\" and the whole room loses it. In the "
    "front row, Clerk Oakhaven is wiping his eyes.\n\n"
    "Odette, in the wings, is making frantic 'more of that' gestures. Mortimer Quill's quill has stopped moving.",
    [C("Carry on with the scene.", "act2")], [SF("show_good_2")])
od.node("act1_style",
    "You give it your audition voice. The audience has no idea what's coming.",
    [C("[The dramatic one] Arms flung wide. \"WHO STRUCK MY NAME?!\"", "act2", [FS("style_dramatic")], [SF("show_good_2")]),
     C("[The haunted whisper] Barely audible. Everyone leans in.", "act2", [FS("style_whisper")], [SF("show_good_2")]),
     C("[The Italian witch] \"Who struck-a my NAME? Mamma mia, the PAPERWORK!\"", "act2", [FS("style_sabrino")], [SF("show_good_2")]),
     C("[The nervous detective] \"Who struck my name? And, more importantly... WHY?\"", "act2", [FS("style_baggy")], [SF("show_good_2")]),
     C("[The monster hunter] Stare at the ledger. \"Hmm.\"", "act2", [FS("style_hollis")], [SF("show_good_2")])])
od.node("act2",
    "ACT TWO. Enter PRINCE VALIANT, sword drawn, and the GHOST OF THE OLD KING, rising from behind the ledger in a drift of "
    "dry ice. They are meant to duel over your fate.",
    [C("Watch Rolf and Ashgrave take the stage.", "act2_pair", [FS("cast_rolf"), FS("cast_ashgrave")]),
     C("Watch Odette play both parts at once, in a false moustache.", "act2_solo", [FF(["cast_rolf", "cast_ashgrave"], 2)])])
od.node("act2_pair",
    "ROLF (as Prince Valiant, raising his sword): \"Spectre! Release the King!\"\n\n"
    "ASHGRAVE (as the Ghost, sweeping his cape): \"Never! For I too was forgotten, and I will not be forgotten ALONE!\"\n\n"
    "They circle each other. Swords touch. And then Rolf, very quietly, not in the script at all, says: \"You don't have to "
    "be alone.\"\n\n"
    "Ashgrave freezes. The audience freezes. Odette, in the wings, has stopped breathing. They are both looking at you, the "
    "King, for what comes next.",
    [C("[Stay in character] \"Then let us all be counted. Together.\" Join their hands.", "act3", actions=[SF("show_good_3")]),
     C("[Break character] Step back, gesture to the two of them, and let them have the moment.", "act2_moment"),
     C("[Prompt them back] Cough, loudly, and say \"Act Two, Scene Two?\"", "act3")])
od.node("act2_moment",
    "You step back into the shadows. On the stage, a werewolf and a vampire stand very close together under a single spotlight, "
    "not saying anything at all.\n\n"
    "Then Ashgrave, very slowly, takes Rolf's hand. Somewhere in the gallery, someone starts clapping. Then everyone is "
    "clapping. Then everyone is standing.\n\n"
    "Mortimer Quill has put his quill down entirely.",
    [C("Let the applause die down, and carry on.", "act3")], [SF("show_good_3")])
od.node("act2_solo",
    "Odette sweeps on in a cape, a moustache and a crown, and plays both the Prince and the Ghost by spinning round between "
    "every line. \"Spectre! Release the King!\" Spin. \"NEVER!\" Spin. \"Then have at thee!\" Spin, spin, spin.\n\n"
    "By the end of the duel she is very dizzy and has stabbed herself twice. The audience has never seen anything like it.",
    [C("[Roll] Catch her before she falls off the stage.", "act3", actions=[SF("show_good_3")],
       roll={"skill": "athletics", "dc": 10, "fail_next": "act3"})])
od.node("act3",
    "ACT THREE. The lights go red. The floor trembles. From the back of the stage, rising over the painted mountains, comes "
    "THE DRAGON.",
    [C("Face the dragon.", "act3_hollis", [FS("cast_hollis")]),
     C("Face the dragon.", "act3_blanket", [FN("cast_hollis")])])
od.node("act3_hollis",
    "Hollis, in the dragon costume, rises up behind the mountains. He looks out at two hundred people. Two hundred people look "
    "back.\n\n"
    "HOLLIS (as THE DRAGON, in a voice like a cellar door): \"Hmm.\"\n\n"
    "It is the scariest thing anyone in the room has ever heard. A child in the front row bursts into delighted tears. "
    "The dragon's one line is delivered. Now the King must face it.",
    [C("[Roll: Athletics] Dodge the dragon's lunge with a dramatic roll across the stage.", "act3_fx", actions=[SF("show_good_4")],
       roll={"skill": "athletics", "dc": 12, "fail_next": "act3_fall"}),
     C("[Speak to it] \"I know you. You were forgotten too.\" Offer the dragon your hand.", "act3_fx", actions=[SF("show_good_4")])])
od.node("act3_blanket",
    "Two stagehands under a green blanket shuffle out from behind the mountains. One of them is clearly Odette. The other "
    "one might be a goat.\n\n"
    "ODETTE (from inside the blanket): \"ROAR.\"\n\nThe goat bleats. The audience is delighted.",
    [C("[Roll: Athletics] Dodge the 'dragon' with a dramatic roll across the stage.", "act3_fx", actions=[SF("show_good_4")],
       roll={"skill": "athletics", "dc": 12, "fail_next": "act3_fall"}),
     C("[Speak to it] \"I know you. You were forgotten too.\" Offer the dragon your hand.", "act3_fx", actions=[SF("show_good_4")])])
od.node("act3_fall",
    "You roll dramatically across the stage, misjudge the edge, and roll straight off it into the orchestra pit, which is "
    "Sabrino's soup pot. There is a splash. There is a silence.\n\n"
    "Then you climb back onto the stage, dripping minestrone, raise one fist, and the audience goes absolutely wild.",
    [C("Shake off the soup. On with the show.", "act3_fx")])
od.node("act3_fx",
    "Now: the big moment of Act Three. The dragon is defeated, and the stage directions say simply: SOMETHING GOES BANG.",
    [C("Give Sabrino the signal.", "act3_bang", [FS("cast_sabrino")]),
     C("Give the stagehands the signal.", "act3_thunder", [FN("cast_sabrino")])])
od.node("act3_bang",
    "Sabrino, in the wings, raises a ladle like a conductor.\n\n"
    "The fireworks go off. All of them. At once. Gold and green and purple stars burst over the stage, a rocket shoots up "
    "into the ballroom chandelier and turns it, briefly, into a second sun. For one glorious moment the whole room is full "
    "of light, and smoke, and somewhere, faintly, the smell of garlic.\n\n"
    "When the smoke clears, the curtains are only slightly on fire. Nobody minds.",
    [C("ACT FOUR.", "act4")], [SF("show_good_5")])
od.node("act3_thunder",
    "Backstage, someone shakes the great tin thunder-sheet that Oakhaven confiscated in a previous decade. It makes a noise "
    "like the sky falling down a staircase. The candles shiver. A dog outside howls back. Rolf, somewhere, howls back at the "
    "dog.\n\nIt is magnificent.",
    [C("ACT FOUR.", "act4")], [SF("show_good_5")])
od.node("act4",
    "ACT FOUR. The finale. The stage is bare now, except for a single desk: the desk of the Bureau, and behind it, a clerk "
    "with a quill, ready to strike the last name from the ledger. Yours.\n\n"
    "The room goes completely still. This is the Great Speech. In the prompter's box, someone is holding their breath.",
    [C("[As written] Deliver the Great Speech exactly as Odette wrote it.", "act4_speech"),
     C("[From the heart] Put down the script. Speak about being remembered, in your own words.", "act4_heart"),
     C("[Your audition voice] Do it the way you did it the very first time.", "act4_style")])
od.node("act4_speech",
    "    \"Though the ledger strike my name, though the ink run dry,\n"
    "    Though every clerk in every hall forget that I was I,\n"
    "    I stand here still, I breathe here still, and this I swear:\n"
    "    A name held true by one who loves is never truly bare.\"\n\n"
    "And now, the line. The one that brings the house down.",
    [C("[Roll: Presence] \"I AM COUNTED!\"", "act4_counted", roll={"skill": "persuasion", "dc": 14, "fail_next": "act4_cucumber"})])
od.node("act4_heart",
    "You put the script down on the clerk's desk.\n\n"
    "You tell them about the notice that arrived saying you were dead. About a baker who couldn't remember her sister's name, "
    "and a detective who never stopped looking for a girl with flour on her nose. About a ghost who laid a table for ninety "
    "years. About how a ledger can say anything it likes, but it can't stop people remembering each other.\n\n"
    "Nobody in the room is moving. Odette is crying openly in the wings. And now, the last line.",
    [C("[Roll: Presence] \"I am counted.\"", "act4_counted", actions=[SF("show_good_6")],
       roll={"skill": "persuasion", "dc": 10, "fail_next": "act4_counted"})])
od.node("act4_style",
    "You give the Great Speech your audition voice, the very one that got you the part.",
    [C("[The dramatic one] Every word to the rafters.", "act4_counted", [FS("style_dramatic")], [SF("show_good_6")]),
     C("[The haunted whisper] So quiet that two hundred people hold their breath to hear it.", "act4_counted", [FS("style_whisper")], [SF("show_good_6")]),
     C("[The Italian witch] With hand gestures. ALL the hand gestures.", "act4_counted", [FS("style_sabrino")], [SF("show_good_6")]),
     C("[The nervous detective] As if you've just solved the case of your own existence.", "act4_counted", [FS("style_baggy")], [SF("show_good_6")]),
     C("[The monster hunter] Read the entire speech. Pause. \"Hmm.\"", "act4_counted", [FS("style_hollis")], [SF("show_good_6")])])
od.node("act4_cucumber",
    "You take a mighty breath. You open your mouth. And from somewhere deep in your memory, from the audition, it comes "
    "out again:\n\n"
    "\"I AM CUCUMBER!\"\n\n"
    "A silence. And then the entire audience, who have all heard about the audition because it is a very small town, roars "
    "it back at you: \"I AM CUCUMBER!\" It becomes a chant. It goes on for some time.\n\n"
    "It's not what Odette wrote. It might be better.",
    [C("Take your bow.", "bow_hub")], [SF("show_good_6")])
od.node("act4_counted",
    "\"I AM COUNTED.\"\n\n"
    "For a heartbeat there is nothing. Then the clerk behind the desk, Oakhaven or Odette or someone in a borrowed hat, lowers "
    "the quill, and closes the ledger, and stands, and begins to applaud.\n\n"
    "The curtain comes down.",
    [C("Take your bow.", "bow_hub")])
od.node("bow_hub",
    "Behind the curtain the whole cast is clutching each other, shaking, laughing, half of them crying. Odette has fainted "
    "into Hollis's arms. On the other side of the velvet, the noise of the audience is like rain on a roof.\n\n"
    "The curtain begins to rise again for the curtain call.",
    [C("Step forward and bow.", "bow_triumph", [FL(GOOD, 5)]),
     C("Step forward and bow.", "bow_good", [FL(GOOD, 3), FF(GOOD, 5)]),
     C("Step forward and bow.", "bow_disaster", [FF(GOOD, 3)])])
reward = [SQ(Q4, 100), GI("core:item.mask_uncounted"), XP("persuasion", 150)]
od.node("bow_triumph", "A standing ovation.", [C("...", "END")],
    reward + [GG(200), SF("show_triumph"),
              {"type": "narrate", "pages": [{"key": "story.show.curtain"}, {"key": "story.show.review_triumph"}, {"key": "story.show.after"}]}])
od.node("bow_good", "Warm, loud, honest applause.", [C("...", "END")],
    reward + [GG(120), SF("show_good"),
              {"type": "narrate", "pages": [{"key": "story.show.curtain"}, {"key": "story.show.review_good"}, {"key": "story.show.after"}]}])
od.node("bow_disaster", "Applause, laughter, and at least one thrown vegetable.", [C("...", "END")],
    reward + [GG(60), GI("core:item.thrown_tomato", 3), SF("show_disaster"),
              {"type": "narrate", "pages": [{"key": "story.show.curtain"}, {"key": "story.show.review_disaster"}, {"key": "story.show.after"}]}])
od.node("after",
    "Odette is sitting on the edge of the stage with her hat in her lap, looking at the empty ballroom with an expression you "
    "haven't seen on her before. Peaceful.\n\n"
    "\"Do you know, darling, I've been travelling with that cart for thirty years. Every town, the same: set up the stage, "
    "find a cast, open, close, move on. Never stayed long enough to learn anybody's name.\"\n\n"
    "\"Bellwether is the first place that learned mine.\" She puts her hat back on. \"I think the Velour Players might stay a "
    "while. There's a ghost in the library who's already writing reviews of the next one.\"",
    [BACK(), LEAVE])

# ================================================================ MORTIMER
mo = Dlg("core:dialogue.mortimer", MORT, "dlg.mortimer")
mo.node("root",
    "Between two bookshelves, a thin, translucent gentleman in a top hat is reading a book with an expression of profound "
    "disgust. Without looking up, he licks a ghostly finger and turns the page.\n\n"
    "\"An intruder. How derivative.\" He makes a note in a red notebook. \"Your entrance: one star. Your coat: two. Your "
    "general air of having been declared legally dead: three and a half. That's quite good, actually. Don't let it go to "
    "your head.\"",
    [C('"Mortimer Quill, I presume?"', "who"),
     C('"Review something for me."', "review"),
     C('"You stole Madame Odette\'s script. I want it back."', "duel_1", [QE(Q2, 10)]),
     C('"Are you coming to opening night?"', "coming", [QA(Q3, 0), QB(Q4, 100)]),
     C('"So. What did you think of the show?"', "after_show", [QA(Q4, 100)]),
     LEAVE])
mo.node("who",
    "\"Mortimer Quill. Critic. The most feared pen in the history of the stage.\" He says it without pride, as a simple "
    "statement of fact, like 'the sea is wet'.\n\n"
    "\"In life I reviewed four thousand plays. Three thousand nine hundred and ninety-eight of them were bad. Then I died, "
    "during the second act of a farce, which I maintain was the farce's fault. And I found I simply couldn't stop.\"\n\n"
    "\"I have been reviewing ever since. The weather. Furniture. Other ghosts. This library: two stars. The bestsellers: one.\"",
    [BACK()])
mo.node("review",
    "Mortimer looks around for something to review. His eyes settle on you.\n\n"
    "\"THE ADVENTURER. A production in one act, apparently endless. The lead has energy, if not direction. The costume is "
    "practical but uninspired. The sword work: competent. The inventory management: frankly alarming. Why are you carrying "
    "nine loaves of bread?\"\n\n"
    "He snaps the notebook shut. \"Two and a half stars. Shows promise. Needs an editor.\"",
    [BACK()])
mo.node("duel_1",
    "Mortimer closes his book with a soft, final thump.\n\n"
    "\"The Velour woman's play. Yes. I have it.\" He pats a pocket that rustles. \"I took it to save the public from "
    "another evening of her work. It is a kindness. One day, they will thank me.\"\n\n"
    "\"But you are welcome to try to change my mind. In the traditional way.\" He rises, hovering slightly. \"A duel of "
    "criticism. Three rounds. I critique. You defend. If you win, the play is yours. Round one: the opening. 'A King wakes "
    "in a ledger.' Derivative. Done to death. Literally, in my case. Defend it.\"",
    [C("[Roll: Lore] \"Every great story starts with someone forgotten. That's not derivative. That's ancient.\"", "duel_1w",
       actions=[SF("critic_r1")], roll={"skill": "lore", "dc": 11, "fail_next": "duel_1l"}),
     C("[Personal] \"I woke up last week to a letter saying I was dead. It's not derivative. It's documentary.\"", "duel_1w",
       actions=[SF("critic_r1")])])
mo.node("duel_1w", "Mortimer's quill hovers over the notebook. Hovers a little longer.\n\n\"...Point taken.\" He writes something. It might "
    "be the first point he has conceded in two hundred years. \"Round two.\"", [C("Round two.", "duel_2")])
mo.node("duel_1l", "\"Hm. Weak. Fumbled. You started a sentence with 'Um'.\" He writes a single scathing word. \"Round one to me. Round two.\"",
    [C("Round two.", "duel_2")])
mo.node("duel_2",
    "\"Round two: the characters. A werewolf who wants to be loved. A vampire who wants to be tragic. A dragon who says "
    "nothing. A baker who shouts. These are not characters. These are your NEIGHBOURS.\" He sneers. \"Where is the art in "
    "that?\"",
    [C("[Roll: Persuasion] \"That's exactly the art. You've watched kings and gods for two hundred years. When did you last "
       "watch your neighbours?\"", "duel_2w", actions=[SF("critic_r2")], roll={"skill": "persuasion", "dc": 13, "fail_next": "duel_2l"}),
     C("[Theatrical] \"They're not my neighbours. They're my FRIENDS. Two stars for you, sir.\"", "duel_2l")])
mo.node("duel_2w", "Mortimer opens his mouth to reply. Then closes it.\n\n\"...When did I last...\" He looks, for just a moment, out of the "
    "library window, towards the lights of Bellwether. Then he coughs, very firmly. \"Irrelevant. Round two to you. Barely. "
    "Final round.\"", [C("The final round.", "duel_3")])
mo.node("duel_2l", "\"Sentiment! Pure sentiment!\" Mortimer makes a long, scratchy note. \"Round two to me. One more, and I keep the play. "
    "Final round.\"", [C("The final round.", "duel_3")])
mo.node("duel_3",
    "\"Final round. And I warn you, I have been saving this one for forty years.\" He leans in. \"Act Three. What, precisely, "
    "is WRONG with Act Three?\"",
    [C("\"It needs more songs.\"", "duel_3l"),
     C("\"It's too long.\"", "duel_3l"),
     C("\"It needs a dragon. A better one.\"", "duel_3w", actions=[SF("critic_r3")]),
     C("\"Nothing. Act Three is perfect.\"", "duel_3l")])
mo.node("duel_3w", "Mortimer Quill goes absolutely still. His quill falls out of his hand and floats gently to the floor.\n\n"
    "\"...It needs a better dragon,\" he whispers. \"I wrote that in the margin. Forty years ago. Of her first draft. Nobody "
    "ever READ the margins.\" He stares at you. \"You read the margins.\"", [C("\"Of course I read the margins.\"", "verdict")])
mo.node("duel_3l", "\"Wrong.\" He sounds almost disappointed. \"The answer was in the margins. It's always in the margins. Nobody ever reads "
    "the margins.\"", [C("Await the verdict.", "verdict")])
mo.node("verdict",
    "Mortimer gathers himself, straightens his hat, and makes a final, ceremonial note.",
    [C("Hear the verdict.", "verdict_win", [FL(DUEL, 2)]),
     C("Hear the verdict.", "verdict_lose", [FF(DUEL, 2)])])
mo.node("verdict_win",
    "\"The duel is yours.\" He draws a velvet-bound script out of his coat and holds it out with both hands, the way you'd "
    "return a sword.\n\n"
    "\"Tell the Velour woman I shall attend her opening night. In the third row, where I have always sat. I shall bring my "
    "notebook. I shall almost certainly hate it.\" A pause. \"But I shall attend.\"\n\n"
    "He drifts back towards his bookshelf. Without turning round, he adds: \"Your defence: four stars. Don't tell anyone.\"",
    [C('"See you in the third row, Mortimer."', "END")], [SF("script_recovered"), SQ(Q2, 20), SF("critic_respect"), XP("lore", 60)])
mo.node("verdict_lose",
    "\"The duel is mine.\" Mortimer looks at the script in his hand for a long moment. Then, with a sound like a very old door, "
    "he sighs, and holds it out anyway.\n\n"
    "\"Take it. I've read it eleven times now. It's... it's not as bad as I said. Don't tell her that.\"\n\n"
    "\"Tell the Velour woman I shall attend. Third row. To make sure it's as bad as I remember.\" He turns away. \"It won't "
    "be. That's the worst part.\"",
    [C('"Third row it is."', "END")], [SF("script_recovered"), SQ(Q2, 20), XP("lore", 30)])
mo.node("coming",
    "\"Opening night?\" He sniffs. \"I wouldn't miss it. Somebody has to be there to be disappointed.\"\n\n"
    "He tries to look disdainful. It doesn't quite work. \"Third row. Centre. Reserve it. And tell the Velour woman I will "
    "not tolerate a goat in the dragon costume. Again.\"",
    [BACK()])
mo.node("after_show",
    "Mortimer is sitting on the edge of a bookshelf, his notebook closed in his lap. He doesn't look up.\n\n"
    "\"Two hundred years,\" he says quietly. \"Four thousand plays. And I never once watched one with people I knew in it.\"\n\n"
    "He opens the notebook to the review he wrote last night and looks at it for a long time. \"I'm going to keep coming, "
    "you know. To her plays. Every one. Third row.\" A pause. \"To be disappointed, obviously.\"",
    [BACK(), LEAVE])

# ================================================================ recruitment & props in existing conversations
D = load("content/dialogue/chapter_zero_dialogue.json")
dl = {d["id"]: d for d in D["dialogues"]}


def extend(did, prefix, root, entries, speaker):
    """Adds topics (choices before 'leave') and their nodes to an existing conversation."""
    g = Dlg(did, speaker, prefix, nodes=dl[did]["nodes"])
    chs = dl[did]["nodes"][root]["choices"]
    idx = max(i for i, c in enumerate(chs) if c["next"] == "END")
    new = []
    for nid, choice_text, cond, node_text, node_choices, actions in entries:
        key = f"{prefix}.topic_{nid}"
        S[key] = choice_text
        new.append({"text_key": key, "conditions": cond, "next": nid})
        g.node(nid, node_text, node_choices, actions)
    dl[did]["nodes"][root]["choices"] = chs[:idx] + new + chs[idx:]


CASTING = [QE(Q1, 10)]
extend("core:dialogue.detective_baggy", "dlg.baggy.players", "root", [
    ("cast_baggy", '"Baggy, how would you feel about being in a play?"', CASTING + [FN("cast_baggy")],
     "Baggy freezes. \"A play. On a STAGE. With an AUDIENCE.\" The magnifying glass is clutched to the chest.\n\n"
     "\"What's the part? Is it a detective? It's a detective, isn't it. Tell me it's a detective.\"\n\n"
     "You explain it's the Second Guard. One line. 'Who goes there.'\n\n"
     "\"Who goes there.\" A long pause. \"WHO goes there. Who goes THERE.\" Baggy's eyes are shining. \"I can work with this. "
     "There's a lot of character in 'who'. I'm in. I'm so in. I'm going to need a hat.\"",
     [C('"Welcome to the Velour Players, Baggy."', "root")], [SF("cast_baggy")]),
], "npc.detective_baggy.name")
extend("core:dialogue.werewolf_rolf", "dlg.rolf.players", "root", [
    ("cast_rolf", '"Rolf, a theatre company needs a Prince Valiant. Dashing, heroic, sword fight. Interested?"',
     CASTING + [FN("cast_rolf")],
     "Rolf drops his trowel. \"A PRINCE?\" He looks down at himself, then up at you. \"Me? I'm a gardener. I'm a werewolf "
     "gardener. Princes don't have fur on their knuckles.\"\n\n"
     "Then, slowly, with growing hope: \"...Is there a ghost in it? Like, a pale tragic ghost? Who might need rescuing? "
     "Or who might rescue me? Either. Both.\" He clears his throat. \"I'll do it. Will I have to wear a shirt?\"",
     [C('"Probably a shirt, yes."', "root", actions=[SF("cast_rolf")]),
      C('"We\'ll see what Odette says."', "root", actions=[SF("cast_rolf")])], []),
], "npc.werewolf_rolf.name")
extend("core:dialogue.vampire_ashgrave", "dlg.ashgrave.players", "root", [
    ("cast_ashgrave", '"Lord Ashgrave, a play needs a Ghost of the Old King. Pale. Tragic. Very still."',
     CASTING + [FN("cast_ashgrave")],
     "Ashgrave turns from the window so fast his cape wraps round him twice.\n\n"
     "\"A GHOST. A tragic, forgotten king, doomed to haunt the halls of his own lost glory.\" He places a hand on his chest. "
     "\"I have been rehearsing for this role for three hundred years.\"\n\n"
     "Then, suspiciously: \"Who plays the Prince?\"",
     [C('"Rolf, probably."', "root", actions=[SF("cast_ashgrave")]),
      C('"Undecided. Possibly a goat."', "root", actions=[SF("cast_ashgrave")])], []),
], "npc.vampire_ashgrave.name")
extend("core:dialogue.hunter_hollis", "dlg.hollis.players", "root", [
    ("cast_hollis", '"Hollis. How do you feel about playing a dragon?"', CASTING + [FN("cast_hollis")],
     "\"No.\"\n\nYou explain about the play. Hollis listens without blinking.\n\n\"No.\"\n\n"
     "You explain that the dragon has only one line. Hollis looks at you for a long moment.\n\n\"...What's the line?\"",
     [C('[Roll: Persuasion] "\'ROAR.\' With three exclamation marks. Nobody else could do it justice."', "cast_hollis_yes",
        roll={"skill": "persuasion", "dc": 13, "fail_next": "cast_hollis_cards"}),
      C('"Whatever you want it to be."', "cast_hollis_yes")], []),
], "npc.hunter_hollis.name")
g = Dlg("core:dialogue.hunter_hollis", "npc.hunter_hollis.name", "dlg.hollis.players", nodes=dl["core:dialogue.hunter_hollis"]["nodes"])
g.node("cast_hollis_yes", "Hollis is quiet for a long time.\n\n\"Hmm,\" he says at last, which you have learned means yes.", [BACK()],
       [SF("cast_hollis")])
g.node("cast_hollis_cards", "\"No.\" He shuffles a deck. \"Tell you what. I win this hand, I'm not doing it.\"\n\n"
       "He loses the hand. He looks at his cards for a long time. You're fairly sure he lost on purpose.\n\n\"Hmm. Fine. Dragon.\"",
       [BACK()], [SF("cast_hollis")])
extend("core:dialogue.witch_sabrino", "dlg.sabrino.players", "root", [
    ("cast_sabrino", '"Sabrino, a theatre company needs someone who knows about fire."', CASTING + [FN("cast_sabrino")],
     "Sabrino stops stirring. Sabrino turns, very slowly, ladle dripping.\n\n"
     "\"Pyrotechnics?\" A whisper. \"You are asking ME to set things on fire, on purpose, in front of an audience, for ART?\"\n\n"
     "\"I accept. I also do the catering. Interval snacks. Fireworks in Act Three. A small, tasteful explosion for the finale. "
     "I will not be taking questions.\"",
     [C('"Welcome aboard, Sabrino."', "root")], [SF("cast_sabrino")]),
    ("prop_bang", '"Odette needs something that goes BANG for Act Three."', [QE(Q3, 10), FN("prop_effects")],
     "Sabrino opens the hat. It contains, among other things, a frankly alarming number of rockets.\n\n"
     "\"Gold, green, purple, and one I call The Goose. Do not ask about The Goose.\" They are pressed into your arms. "
     "\"Light the fuse, step back, then step back further. Then further than that. Then, enjoy.\"",
     [C('"Thank you. I think."', "root")], [SF("prop_effects"), GI("core:item.fireworks")]),
], "npc.witch_sabrino.name")
extend("core:dialogue.innkeeper_marta", "dlg.marta.players", "root", [
    ("cast_marta", '"Marta, a theatre company needs a prompter. Someone who remembers everything."', CASTING + [FN("cast_marta")],
     "Marta laughs. \"Me? Remember everything? Seventeen years I couldn't remember my own sister's face.\"\n\n"
     "Then she stops laughing, and thinks about it. \"...But I remember every order in this inn. Who takes their ale warm, "
     "who wants the crust, who's not to be served after the third.\" She dusts off her hands. \"I'll do it. I'll whisper "
     "your lines. I'm very good at whispering. I whisper to the bread.\"",
     [C('"Thank you, Marta."', "root")], [SF("cast_marta")]),
], "npc.innkeeper_marta.name")
extend("core:dialogue.librarian_fenwick", "dlg.fenwick.players", "root", [
    ("cast_fenwick", '"Fenwick, a play needs a Narrator. A commanding voice. A love of words."', CASTING + [FN("cast_fenwick")],
     "Fenwick draws himself up to his full height, which is not very high, and adjusts his spectacles with great ceremony.\n\n"
     "\"A Narrator. The voice that carries the tale. The one who stands between the story and the dark.\" He clears his "
     "throat. \"I have been reading stories aloud to empty aisles for forty years. Yes. YES. I accept.\"\n\n"
     "\"I shall require a lectern. And absolute silence from the audience. Absolute.\"",
     [C('"I\'ll tell Odette."', "root")], [SF("cast_fenwick")]),
    ("prop_crown", '"Odette needs a crown for the King. Anything in the library?"', [QE(Q3, 10), FN("prop_crown")],
     "Fenwick vanishes into the stacks and comes back with a crown made of gold paper, carefully folded from the dust jacket "
     "of a very bad romance novel.\n\n"
     "\"'Fifty Shades of Grey Robes',\" he says, without meeting your eye. \"Chapter Nine is printed on the inside. Wear it "
     "facing forward, and nobody will know.\"",
     [C('"Nobody will ever know."', "root")], [SF("prop_crown"), GI("core:item.paper_crown")]),
], "npc.librarian_fenwick.name")
extend("core:dialogue.clerk_oakhaven", "dlg.clerk.players", "greeting", [
    ("cast_oakhaven", '"Clerk Oakhaven, a play needs a Herald. Loud. Official. Fond of paperwork."', CASTING + [FN("cast_oakhaven")],
     "Oakhaven puts down his quill. \"A Herald.\" He considers it. \"I would of course require Form 99-T, Application to "
     "Participate in Theatrical Entertainment.\" He produces it. It is four pages long. \"Question one. Is the performance "
     "intended to be: (a) amusing, (b) tragic, or (c) a tax write-off?\"",
     [C('"(a) Amusing."', "form_2"), C('"(b) Tragic."', "form_2"), C('"(c) A tax write-off."', "form_2")], []),
], "npc.clerk_oakhaven.name")
g = Dlg("core:dialogue.clerk_oakhaven", "npc.clerk_oakhaven.name", "dlg.clerk.players", nodes=dl["core:dialogue.clerk_oakhaven"]["nodes"])
g.node("form_2", "He ticks a box. \"Question two. Will the performance contain any of the following: dragons, fire, ghosts, "
       "witches, or singing?\"",
       [C('"Yes."', "form_3"), C('"All of them. At once."', "form_3"), C('"...Define \'singing\'."', "form_3")])
g.node("form_3", "He ticks another box, slightly faster. \"Question three, final question. Is the applicant, at the time of "
       "application, legally alive?\"\n\nHe looks up at you over his spectacles. You look back at him.",
       [C('"You tell me, Oakhaven."', "form_done"), C('"Pending."', "form_done"), C('"I have a Form 27-B for that."', "form_done")])
g.node("form_done", "Oakhaven stamps Form 99-T with a sound like a judge's gavel, then, after a moment's thought, stamps it again "
       "for luck.\n\n\"Approved. I shall be the Herald.\" He looks down at his plain grey coat. \"Is there... a hat?\"\n\n"
       "You assure him there is a hat.\n\n\"Then I am at your service.\" A very small smile. \"Nobody has ever asked me to be "
       "in anything before.\"", [C('"Welcome to the company, Herald."', "greeting")], [SF("cast_oakhaven")])
extend("core:dialogue.clerk_oakhaven", "dlg.clerk.players", "greeting", [
    ("prop_thunder", '"Odette needs something that goes BANG. Anything in the confiscated property cupboard?"',
     [QE(Q3, 10), FN("prop_effects")],
     "Oakhaven's eyes light up the way a clerk's only do when asked about a cupboard. He returns with a huge sheet of tin "
     "and a label: CONFISCATED - 'THUNDER, THEATRICAL, ONE (1)'.\n\n\"Shake it,\" he says. \"Firmly. Fill out the receipt.\"",
     [C('"I\'ll fill out the receipt."', "greeting")], [SF("prop_effects"), GI("core:item.thunder_sheet")]),
], "npc.clerk_oakhaven.name")
extend("core:dialogue.merchant_vaelen", "dlg.vaelen.players", "root", [
    ("prop_dragon", '"I need a dragon costume. A proper one."', [QE(Q3, 10), FN("prop_dragon")],
     "Vaelen doesn't even blink. He disappears into the back room and returns with an enormous green costume: scales "
     "sewn from old leather, wings of oilcloth on willow frames, a head with real glass eyes and a jaw that opens.\n\n"
     "\"Somebody ordered it nine years ago and never collected it. A monster hunter, I think. Said it was 'for a contract'.\" "
     "He shrugs. \"On the house. Just get it out of my shop. It watches me.\"",
     [C('"Thank you, Vaelen."', "root")], [SF("prop_dragon"), GI("core:item.dragon_costume")]),
], "npc.merchant_vaelen.name")

D["dialogues"] += [od.json(), mo.json()]
save("content/dialogue/chapter_zero_dialogue.json", D)

# ================================================================ quests & campaign
QQ = load("content/quests/chapter_zero_quests.json")
def quest(qid, short, stages):
    QQ["quests"].append({"id": qid, "title_key": f"quest.{short}.title", "summary_key": f"quest.{short}.summary", "campaign": "bellwether_players",
                         "stages": [{"stage": s, "objective_key": f"quest.{short}.stage{s}", "journal_key": f"quest.{short}.journal{s}",
                                     **({"completed": True} if s == 100 else {})} for s in stages]})
quest(Q1, "casting", (0, 10, 100))
quest(Q2, "script", (0, 10, 20, 100))
quest(Q3, "rehearsal", (0, 10, 100))
quest(Q4, "opening", (0, 100))
QQ["campaigns"].append({"id": "bellwether_players", "name_key": "campaign.players.name", "desc_key": "campaign.players.desc",
                        "kind": "side", "order": 25})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "campaign.players.name": "The Bellwether Players",
    "campaign.players.desc": "Madame Odette Velour has a cart, a costume trunk and the greatest play ever written. All she needs is a cast. And you.",
    "quest.casting.title": "Act I: Casting Call",
    "quest.casting.summary": "A travelling impresario needs a lead for The Tragedie of the Uncounted King. Apparently you have the face for it.",
    "quest.casting.stage0": "Audition for Madame Odette Velour, near Bellwether's south gate.",
    "quest.casting.journal0": "A woman in a very large magenta hat told me I have a face that has suffered. She wants me to audition.",
    "quest.casting.stage10": "Recruit at least four cast members and tell Odette. Prince, Ghost, Dragon, Herald, Narrator, Second Guard, prompter, fireworks: ask around Bellwether, the Old Road and Hollowmere.",
    "quest.casting.journal10": "I got the lead. The only other person who auditioned was a goat. Now I need a cast, and I know exactly the right collection of lovely, ridiculous people.",
    "quest.casting.stage100": "Completed: the Velour Players have a cast.",
    "quest.casting.journal100": "The cast is assembled. Odette hugged me hard enough to realign my spine. Then she opened her trunk and the script was gone.",
    "quest.script.title": "Act II: The Missing Script",
    "quest.script.summary": "Mortimer Quill, the most feared critic in history (deceased), has stolen the only copy of Odette's play and scattered the pages.",
    "quest.script.stage0": "Find the five scattered script pages. Look anywhere dusty, gloomy or important: the Records Office, the Old Road, the Annex, Vault III, Hollowmere's library.",
    "quest.script.journal0": "Somebody stole Odette's script and left a card: 'One and a half stars. Derivative. - M.Q.' Mortimer Quill, a critic who has been dead for two hundred years and hasn't let it slow him down.",
    "quest.script.stage10": "The trail ends in Hollowmere's library. Confront Mortimer Quill and win back the script.",
    "quest.script.journal10": "The last page was in Hollowmere's library, and so was the critic: a thin ghost in a top hat, reviewing the books. I'll have to win the script back. In a duel. Of criticism.",
    "quest.script.stage20": "Bring the script back to Madame Odette.",
    "quest.script.journal20": "Mortimer gave me the script. He's coming to opening night, third row, to be disappointed.",
    "quest.script.stage100": "Completed: the script is home.",
    "quest.script.journal100": "Odette kissed the script three times and read the margins with growing outrage. We rehearse at Hollowmere.",
    "quest.rehearsal.title": "Act III: Dress Rehearsal",
    "quest.rehearsal.summary": "A cast of a werewolf, a vampire, a monster hunter, a detective, a witch, a baker, a librarian and a clerk, in one ballroom. What could go wrong?",
    "quest.rehearsal.stage0": "Join Odette in the Hollowmere ballroom and get the cast through rehearsal (solve at least three backstage dramas).",
    "quest.rehearsal.journal0": "Odette has turned Hollowmere's ballroom into a theatre. The cast has turned it into a circus.",
    "quest.rehearsal.stage10": "Find the three props: a CROWN (Fenwick, or a real one), a DRAGON costume (Vaelen) and SOMETHING THAT GOES BANG (Sabrino, or Oakhaven's confiscated cupboard). Then tell Odette.",
    "quest.rehearsal.journal10": "We survived rehearsal. Odette says we're a magnificent disaster, which is apparently what every great company is the night before it opens.",
    "quest.rehearsal.stage100": "Completed: the props are ready.",
    "quest.rehearsal.journal100": "Crown, dragon, bang. Opening night is tonight.",
    "quest.opening.title": "Act IV: Opening Night",
    "quest.opening.summary": "The Tragedie of the Uncounted King. One night only. Probably.",
    "quest.opening.stage0": "Tell Odette when you're ready for curtain up, in the Hollowmere ballroom.",
    "quest.opening.journal0": "Two hundred people, one ballroom, one ghost critic in the third row. My mouth is already dry.",
    "quest.opening.stage100": "Completed: the Tragedie of the Uncounted King has opened.",
    "quest.opening.journal100": "We did it. Whatever Mortimer Quill wrote, the whole town was in that room, and every one of them knows my name now.",
    "npc.odette.name": "Madame Odette Velour",
    "npc.odette.title": "Impresario of the Velour Players",
    "npc.mortimer.name": "Mortimer Quill",
    "npc.mortimer.title": "The Last Critic (Deceased, Unimpressed)",
    "bark.odette.1": "DARLING! Yes, you! The face! The SUFFERING!",
    "bark.odette.2": "Five acts, two intervals, one dragon. And a cast of NOBODY. Yet.",
    "bark.odette.3": "Projection, darlings! The back row is always full of farmers!",
    "bark.odette.after": "Bellwether learned my name. I think I'll stay a while.",
    "bark.mortimer.1": "This bookshelf: two stars. Overlong.",
    "bark.mortimer.2": "Rain. Again. Derivative.",
    "bark.mortimer.after": "Third row. Every play. To be disappointed. Obviously.",
    "story.show.curtain": "The curtain rises for the bows, and the room is on its feet.\n\nThe cast comes forward in a ragged line, holding hands: whoever you brought, in whatever costumes survived. Somebody is still slightly on fire. Somebody is still wearing oven gloves. Odette, in the middle, bows so low her hat falls off, and two hundred people in a ballroom in the rain cheer for a play about a king nobody remembered.\n\nIn the third row, Mortimer Quill is writing.",
    "story.show.review_triumph": "The next morning, a review is nailed to the door of the Lantern Inn, in spidery red ink:\n\n\"THE TRAGEDIE OF THE UNCOUNTED KING. The Velour Players, Hollowmere.\n\nI have attended four thousand and one plays. This was the first at which I forgot to take notes.\n\nThe lead was luminous. The dragon was terrifying. The second act contained an unscripted moment between a prince and a ghost that I will not describe, because it was not mine to review.\n\nFive stars. I have never given five stars. I have checked whether I am still dead. I am. - M.Q.\"",
    "story.show.review_good": "The next morning, a review is nailed to the door of the Lantern Inn, in spidery red ink:\n\n\"THE TRAGEDIE OF THE UNCOUNTED KING. The Velour Players, Hollowmere.\n\nUneven. Overlong. A dragon of questionable provenance. At least one actor was clearly reading from the inside of a paper crown.\n\nAnd yet. When the lead spoke the final line, an entire village stood up at once, and I found that I had stood up with them. I am not sure how this happened. I am investigating.\n\nThree and a half stars. Would attend again. Do not quote me. - M.Q.\"",
    "story.show.review_disaster": "The next morning, a review is nailed to the door of the Lantern Inn, in spidery red ink:\n\n\"THE TRAGEDIE OF THE UNCOUNTED KING. The Velour Players, Hollowmere.\n\nA catastrophe. A triumph of catastrophe. Lines were forgotten, scenery collapsed, a goat appeared in a role for which it was not cast, and the climax of the evening was the word 'cucumber', chanted by two hundred people.\n\nI have not laughed since 1592. I laughed last night until I was nearly corporeal.\n\nOne star. The best one star I have ever given. I shall be back for the second night. - M.Q.\"",
    "story.show.after": "Long after the audience has gone home, the cast is still sitting on the edge of the stage, sharing Sabrino's interval snacks, passing round the paper crown, retelling the night to each other as if none of them were there.\n\nOdette, hat in her lap, looks round at all of them, and then at you.\n\n\"A cast,\" she says softly. \"I'd forgotten what it was like to have one.\"",
    "item.script_tragedie.name": "Script: The Tragedie of the Uncounted King",
    "item.script_tragedie.description": "Odette's play, bound in velvet, heavily annotated in red by a ghost.",
    "book.script_tragedie.text": "THE TRAGEDIE OF THE UNCOUNTED KING\nA play in five acts (four, after cuts), by Odette Velour\n\nDRAMATIS PERSONAE:\nTHE UNCOUNTED KING, forgotten by all\nPRINCE VALIANT, a hero with a sword and feelings\nTHE GHOST OF THE OLD KING, pale, tragic, very still\nTHE DRAGON, one line\nTHE HERALD, loud, official\nTHE NARRATOR, who would prefer you were quiet\nSECOND GUARD (there is no First Guard; budget)\n\n[In red, in the margin: 'There is no First Guard. Why is there a Second Guard. - M.Q.']\n\nACT ONE: The King wakes in the margin of a ledger, his name struck out.\nACT TWO: The Prince and the Ghost duel for the King's fate.\n[Margin: 'They are clearly in love. Write it in or I will. - M.Q.']\nACT THREE: The Dragon.\n[Margin: 'Needs a dragon. A better one. - M.Q.']\nACT FOUR: The Great Speech.\n\n    Though the ledger strike my name, though the ink run dry,\n    Though every clerk in every hall forget that I was I,\n    I stand here still, I breathe here still, and this I swear:\n    A name held true by one who loves is never truly bare.\n\n    I AM COUNTED.\n\n[Margin, in very small, shaky red letters: 'This bit is good. - M.']",
    "item.mask_uncounted.name": "Mask of the Uncounted King",
    "item.mask_uncounted.description": "The gilded half-mask you wore on opening night. Odette insisted you keep it. When you wear it, people turn to look at you, and for once you don't mind. +3 Presence, +5% spell power, +3% critical chance.",
    "item.thrown_tomato.name": "Thrown Tomato",
    "item.thrown_tomato.description": "Caught mid-air during the curtain call. A critic's gift. Still perfectly good to eat, and oddly motivating: +0.2 critical multiplier for 2 minutes.",
    "item.paper_crown.name": "Paper Crown",
    "item.paper_crown.description": "Folded from the dust jacket of a romance novel. Chapter Nine is printed on the inside. Wear it facing forward.",
    "item.dragon_costume.name": "Dragon Costume",
    "item.dragon_costume.description": "Leather scales, oilcloth wings, real glass eyes. Ordered nine years ago by a monster hunter 'for a contract'. It watches you.",
    "item.fireworks.name": "Sabrino's Fireworks",
    "item.fireworks.description": "Gold, green, purple, and one labelled THE GOOSE. Do not ask about The Goose.",
    "item.thunder_sheet.name": "Thunder Sheet (Confiscated)",
    "item.thunder_sheet.description": "A great sheet of tin. Shake firmly for weather. Comes with a receipt.",
})

# ================================================================ items
def additem(path, e):
    d = load(path); d["items"].append(e); save(path, d)
def it(iid, cat, icon, model, val, w, **kw):
    e = {"id": "core:item." + iid, "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": model, "slots": [], "value": val, "weight": w}
    e.update(kw); return e
Q = "content/items/quest_and_keys.json"
additem("content/items/consumables_and_books.json",
        it("script_tragedie", "book", "script_tragedie", "assets/models/items/spell_tome.glb", 0, 0.5, book_text_key="book.script_tragedie.text"))
additem("content/items/consumables_and_books.json",
        it("thrown_tomato", "consumable", "thrown_tomato", "assets/models/items/bread_loaf.glb", 1, 0.2, stackable=True,
           effects=[{"type": "consumable_heal", "amount": 6}, {"type": "buff", "stat": "crit_damage_bonus", "value": 0.2, "duration": 120}]))
additem("content/items/armor_and_gear.json",
        it("mask_uncounted", "accessory", "mask_uncounted", "assets/models/items/signet_ring.glb", 300, 0.3, slots=["accessory"], armor=0,
           effects=[{"type": "stat_bonus", "stat": "presence", "amount": 3}, {"type": "bonus", "stat": "spell_power_bonus", "value": 0.05},
                    {"type": "bonus", "stat": "crit_chance_bonus", "value": 0.03}]))
for iid, icon, model in [("paper_crown", "paper_crown", "assets/models/items/signet_ring.glb"),
                         ("dragon_costume", "dragon_costume", "assets/models/items/leather_jerkin.glb"),
                         ("fireworks", "fireworks", "assets/models/items/bread_loaf.glb"),
                         ("thunder_sheet", "thunder_sheet", "assets/models/items/iron_shield.glb")]:
    additem(Q, it(iid, "misc", icon, model, 0, 0.5, quest_item=True))

# ================================================================ NPCs
N = load("content/npcs/core_npcs.json")
N["npcs"] += [
    {"id": "core:npc.odette", "name_key": "npc.odette.name", "title_key": "npc.odette.title", "faction": "core:faction.ashbound",
     "dialogue_id": "core:dialogue.odette",
     "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/impresario_odette.png",
                    "animation_data": "assets/animations/npc_standard.json", "scale": 1.7},
     "barks": [{"text_key": "bark.odette.1", "not_flag": "players_at_hollowmere"}, {"text_key": "bark.odette.2", "quest_id": Q1, "max_stage": 99},
               {"text_key": "bark.odette.3", "flag": "players_at_hollowmere"},
               {"text_key": "bark.odette.after", "quest_id": Q4, "min_stage": 100}]},
    {"id": "core:npc.mortimer", "name_key": "npc.mortimer.name", "title_key": "npc.mortimer.title", "faction": "core:faction.ashbound",
     "dialogue_id": "core:dialogue.mortimer",
     "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/critic_mortimer.png",
                    "animation_data": "assets/animations/npc_standard.json", "scale": 1.75},
     "barks": [{"text_key": "bark.mortimer.1"}, {"text_key": "bark.mortimer.2"},
               {"text_key": "bark.mortimer.after", "quest_id": Q4, "min_stage": 100}]},
]
save("content/npcs/core_npcs.json", N)

# ================================================================ world placements (script pages, Odette in town)
PAGE_TEXT = {
    1: ("page_1", "THE TRAGEDIE OF THE UNCOUNTED KING - Page One",
        "ACT ONE, SCENE ONE. The inside of a great ledger.\n\nNARRATOR: Once there was a King whom all the world forgot. Not by war, "
        "nor plague, nor the slow grey dust of years, but by a single stroke of ink.\n\nKING (waking): Who struck my name? Who dares "
        "to strike a king?\n\nSECOND GUARD: Who goes there?\n\nKING: I do! Your King!\n\nSECOND GUARD: ...Who?\n\n"
        "[In spidery red ink, in the margin: 'The guard's line is the best in the scene. This is not a compliment to the guard. "
        "One star. - M.Q.']\n\n[Below, in pencil, in a different hand: 'Filed under FICTION, UNLICENSED. - O.']"),
    2: ("page_2", "THE TRAGEDIE OF THE UNCOUNTED KING - Page Two",
        "ACT TWO, SCENE ONE. A haunted battlement. Moonlight.\n\nPRINCE VALIANT: Spectre! Release the King!\n\nGHOST OF THE OLD "
        "KING: Never! For I too was forgotten, and I will not be forgotten alone!\n\nPRINCE VALIANT: Then have at thee!\n\n"
        "(They duel. It goes on for some time.)\n\n(It goes on for a bit longer.)\n\n[Margin, red ink: 'These two are clearly in "
        "love. The playwright appears to be the only person in the audience who has not noticed. - M.Q.']\n\n"
        "The page has been nailed to a pine tree, at exactly the height of a critic's top hat."),
    3: ("page_3", "THE TRAGEDIE OF THE UNCOUNTED KING - Page Three",
        "ACT THREE, SCENE ONE. A mountain. Red light.\n\nNARRATOR: And from the mountain came the Dragon, and the Dragon spoke.\n\n"
        "THE DRAGON: ROAR!!!\n\nKING: Foul worm! I am not afraid!\n\nTHE DRAGON: ROAR!!!\n\nKING: Still not afraid!\n\nTHE DRAGON: "
        "...roar.\n\n[Margin, red ink, underlined three times: 'NEEDS A DRAGON. A BETTER ONE. - M.Q.']\n\n"
        "Someone, probably a Bone Clerk, has stamped the page RECEIVED and filed it between two tax returns."),
    4: ("page_4", "THE TRAGEDIE OF THE UNCOUNTED KING - Page Four",
        "ACT FOUR, SCENE ONE. A nursery, in the dark.\n\nHERALD: Hear ye! Hear ye! The King is not dead!\n\nNARRATOR: But the "
        "King was tired, so very tired, and the night was long, and somewhere a lullaby was playing.\n\nKING: Then let me sleep a "
        "little. But wake me. Promise you will wake me. Promise you will say my name.\n\n[Margin, red ink, much smaller than the "
        "others: 'This scene should not be set here. Not in this room. Not with these children asleep. - M.Q.' And beneath it, "
        "fainter: 'But it is good.']"),
    5: ("page_5", "THE TRAGEDIE OF THE UNCOUNTED KING - Page Five",
        "ACT FOUR, SCENE TWO. The Bureau.\n\nKING: Though the ledger strike my name, though the ink run dry, though every clerk "
        "in every hall forget that I was I...\n\n(The rest of the speech has been torn away.)\n\n[Margin, red ink: 'I have kept "
        "the rest. If the Velour woman wants it, she may come and fetch it herself. Or send someone braver. I shall be in the "
        "library. I am always in the library. - M.Q.']\n\nAs you finish reading, the temperature in the library drops, and "
        "between two bookshelves, a thin figure in a top hat lowers a book and looks at you over it."),
}
def page(region, n, pos):
    d = load(f"content/regions/{region}.json")
    flag, title, text = PAGE_TEXT[n]
    entry = {"instance_id": f"script_{flag}", "type": "readable", "model": "", "pos": pos, "rot_y": 0.0,
             "prompt": "Pick Up the Torn Script Page", "title": title, "text": text, "set_flag": flag}
    d["interactables"].append(entry)
    save(f"content/regions/{region}.json", d)
page("bellwether", 1, [-2.5, 1.2, -13.6])
page("old_road", 2, [-6.0, 1.6, -8.35])
page("registry_annex", 3, [1.5, 1.2, -16.6])
page("vault_three", 4, [-13.5, 1.0, 5.0])
BW = load("content/regions/bellwether.json")
BW["npcs"].append({"instance_id": "npc_odette", "npc_id": "core:npc.odette", "pos": [4.6, 0.0, 17.0], "yaw": 200.0,
                   "hidden_flag": "players_at_hollowmere"})
BW["interactables"].append({"instance_id": "casting_poster", "type": "readable", "model": "assets/models/props/lectern_ledger.glb",
    "pos": [6.4, 0.0, 17.8], "rot_y": 180.0, "prompt": "Read the Casting Call", "title": "CASTING CALL!",
    "text": ("THE VELOUR TRAVELLING PLAYERS\nproudly present\nTHE TRAGEDIE OF THE UNCOUNTED KING\n\nA play in five acts. Two intervals. "
             "One dragon.\n\nNOW CASTING: a LEAD (must have suffered), a PRINCE (must own sword), a GHOST (must be pale), a DRAGON "
             "(must be large), a HERALD, a NARRATOR, a SECOND GUARD (there is no First Guard; budget), a PROMPTER, and someone who "
             "is not afraid of fire, or the law.\n\nNo experience required. No pay guaranteed. Glory almost certain.\n\nApply to "
             "Madame Odette Velour, in person, in the large hat.\n\nUnderneath, in red ink: 'Two stars. The font is overwrought. - M.Q.'")})
save("content/regions/bellwether.json", BW)

# Page five lives in Hollowmere's library: written into tools/build_mansion.py (with Mortimer, Odette's stage and the stage).
open("/tmp/claude-0/-home-user-TheUncounted/f133b020-d64c-572e-960b-947ecb06fbfa/scratchpad/page5.json", "w").write(json.dumps(PAGE_TEXT[5]))

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

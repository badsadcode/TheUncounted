"""The Figure It Out Gang: a meddling mystery-solving gang (originals, in the spirit of classic cartoon sleuths; a
spinoff idea Toasty made up) with a painted wagon on the Old Road. Episodes follow the formula: split up, find
clues, set a trap that goes wrong, catch the 'monster', unmask the culprit. Running gag: "I barely knew her!"
(no matter who is under the mask). Silly, not very competent, spooky, and somehow successful.

ARCHIVE: this one-off authoring script already ran (its output lives in content/ and the region builder scripts).
Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
F1, F2 = "core:quest.figure_ep1", "core:quest.figure_ep2"
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
QE = lambda q, s: {"type": "quest_stage_equals", "quest_id": q, "stage": s}
QA = lambda q, s: {"type": "quest_stage_at_least", "quest_id": q, "stage": s}
QB = lambda q, s: {"type": "quest_stage_below", "quest_id": q, "stage": s}
FL = lambda fl, v: {"type": "flags_at_least", "flags": fl, "value": v}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
XP = lambda k, a: {"type": "give_xp", "skill": k, "amount": a}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
TI = lambda i, q=1: {"type": "take_item", "item_id": i, "qty": q}
GG = lambda a: {"type": "give_gold", "amount": a}
SQ = lambda q, s: {"type": "set_quest_stage", "quest_id": q, "stage": s}
NAR = lambda *k: {"type": "narrate", "pages": list(k)}
CLUES1 = ["fig1_c1", "fig1_c2", "fig1_c3"]
CLUES2 = ["fig2_c1", "fig2_c2", "fig2_c3"]
ROD, PRIM, AGN, CRU, SNA = ("npc.figure_rodrick.name", "npc.figure_primrose.name", "npc.figure_agnes.name", "npc.figure_crumbs.name",
                            "npc.figure_snacks.name")


class Dlg:
    def __init__(self, prefix, nodes, speaker):
        self.prefix, self.nodes, self.speaker = prefix, nodes, speaker

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


def C(text, nxt, cond=None, actions=None):
    o = {}
    if cond: o["conditions"] = cond
    if actions: o["actions"] = actions
    return (text, nxt, o)


D = load("content/dialogue/chapter_zero_dialogue.json")
def new_dialogue(did):
    D["dialogues"].append({"id": did, "root_node": "root", "nodes": {}})
    return D["dialogues"][-1]["nodes"]

# ======================================================================= Rodrick: the leader, the cases, the traps
rn = new_dialogue("core:dialogue.figure_rodrick")
r = Dlg("dlg.fig.rod", rn, ROD)
r.node("root",
    "Beside a gaudily painted caravan (teal, orange stripes, flowers, and an enormous question mark on the side) stands a square-jawed young "
    "man in a white tunic and an orange cravat, holding a coil of rope and a net, and looking at you as though you might be a mystery.\n\n"
    "\"Sir Rodrick Ascot-Smythe! Leader of the Figure It Out Gang. That's our wagon. The Figure It Out Wagon. We drive around, we find "
    "monsters, we figure them out.\" He gestures grandly at the others. \"Lady Primrose, Agnes, Crumbs, and Snacks. Snacks is an owlbear. "
    "Don't ask him to do anything brave.\"",
    [C('"What do you do, exactly?"', "what"),
     C('"Got a mystery for me?"', "e1_open", [QB(F1, 0)]),
     C('"I found clues about the Phantom Clerk."', "e1_trap", [QE(F1, 10), FL(CLUES1, 3)]),
     C('"What were we looking for again?"', "e1_hint", [QE(F1, 10), {"type": "flags_fewer_than", "flags": CLUES1, "value": 3}]),
     C('"We unmasked the Phantom Clerk."', "e1_done", [QE(F1, 50)]),
     C('"Any more mysteries, Rodrick?"', "e2_open", [QA(F1, 100), QB(F2, 0)]),
     C('"I\'ve got the clues about the Howler."', "e2_trap", [QE(F2, 10), FL(CLUES2, 3)]),
     C('"Remind me about the Howler?"', "e2_hint", [QE(F2, 10), {"type": "flags_fewer_than", "flags": CLUES2, "value": 3}]),
     C('"The Howler of Hollowmere is unmasked."', "e2_done", [QE(F2, 50)]),
     C('"How\'s the gang?"', "later", [QA(F2, 100)]),
     C("Leave.", "END")])
r.node("what",
    "RODRICK: \"Mysteries! Hauntings! Things that go bump, and things that go bump in a costume! Every monster is just someone in a mask, "
    "and every mask comes off in the end.\"\n\n"
    "AGNES (from inside the wagon): \"Statistically, Rodrick, we've caught eleven people in masks and one actual ghost.\"\n\n"
    "RODRICK: \"We don't talk about the actual ghost.\"\n\n"
    "CRUMBS (from under the wagon): \"I barely knew her!\"",
    [C('"...Right."', "root")])
r.node("e1_open",
    "Rodrick unrolls a poster, slightly damp: 'BEWARE THE PHANTOM CLERK OF BELLWETHER'.\n\n"
    "RODRICK: \"Every night, a glowing spectre in Bureau robes walks the streets of Bellwether and stamps DECEASED on people's doors. People "
    "who are, and I cannot stress this enough, alive. Half the village is too scared to go out. And yet. Somebody, somewhere, is selling "
    "a LOT of ghost-repelling charms.\"\n\n"
    "He strikes a pose. \"Gang! Let's split up and look for clues!\"\n\n"
    "AGNES: \"Every time we split up, something chases Crumbs.\"\n\nCRUMBS: \"Every time.\"\n\nRODRICK: \"And it works every time! You "
    "take the Records Office step. And the alleys. And behind the market stalls. Look for anything ghostly. Or anything that ISN'T.\"",
    [C('"Splitting up."', "root", actions=[SQ(F1, 0), SQ(F1, 10), SF("fig1_open")])])
r.node("e1_hint",
    "RODRICK: \"The Records Office step, the alleys of Bellwether, and behind the market stalls! Three clues. Agnes says you need three. "
    "Agnes is always right. Except about the actual ghost.\"",
    [C('"On it."', "root")])
r.node("e1_trap",
    "You lay the clues out on the wagon's tailboard: luminous ink, a receipt for one extra-large bedsheet, and a box of price tags for "
    "Ghost-B-Gone charms.\n\n"
    "AGNES (pushing her spectacles up her nose): \"Jumping jellyfish. It's someone who sells things.\"\n\n"
    "RODRICK (not listening): \"Gang! I've got a plan! We set a trap in the square! A net, a pulley, a barrel of feathers, and some bait. "
    "We'll use Crumbs as the bait.\"\n\nCRUMBS: \"No.\"\n\nRODRICK: \"We'll use Snacks as the bait.\"\n\nSNACKS: \"Hrrrr-oo?\"\n\n"
    "RODRICK: \"Fine. We'll use you as the bait. Go and set the trap in the middle of the square. What could go wrong?\"",
    [C('"Everything, probably."', "root", actions=[SQ(F1, 20), SF("fig1_trap_ready")])])
r.node("e1_done",
    "RODRICK: \"Another mystery... FIGURED OUT!\"\n\nThe whole gang, in unison: \"FIGURED OUT!\" (Snacks, a beat late: \"Hrr-oot!\")\n\n"
    "AGNES: \"For the record, our trap caught Baggy, a pigeon, and Rodrick, in that order. The culprit fell over Snacks.\"\n\n"
    "RODRICK: \"And that's TEAMWORK.\" He hands you a box. \"Crumb Cakes. Snacks's favourite. Crumbs's favourite. Everybody's favourite. "
    "Welcome to the gang. Honorary member. You get a cravat if you do another one.\"",
    [C('"Thanks, Rodrick."', "root", actions=[SQ(F1, 100), GI("core:item.crumb_cake", 5), GG(80), XP("perception", 40)])])
r.node("e2_open",
    "RODRICK (unrolling another poster): \"'THE HOWLER OF HOLLOWMERE'. Every night, something huge and hairy tears through the vegetable "
    "garden at Hollowmere Manor and steals the prize marrows. Howling. Glowing eyes. Claws.\"\n\n"
    "PRIMROSE: \"There's a werewolf who lives there, darling. Rolf. Lovely man. Grows the marrows.\"\n\n"
    "RODRICK: \"Exactly! The obvious suspect! Which means it's DEFINITELY not him! Or it's DEFINITELY him! We'll know when we pull his face "
    "off.\"\n\nAGNES: \"We are not pulling Rolf's face off.\"\n\nRODRICK: \"Gang! Let's split up and look for clues! In the garden!\"",
    [C('"Splitting up. Again."', "root", actions=[SQ(F2, 0), SQ(F2, 10), SF("fig2_open")])])
r.node("e2_hint",
    "RODRICK: \"Rolf's garden at Hollowmere! Footprints! Fabric! Paperwork! Agnes says paperwork. I don't know why there would be paperwork. "
    "Agnes knows things.\"",
    [C('"Back to the garden."', "root")])
r.node("e2_trap",
    "AGNES (examining your clues through spectacles she has only just found again): \"Pawprints with a sandal underneath. A scrap of brown "
    "wool, rough, like a habit. And the entry list for the Bellwether Marrow Show: Rolf, champion four years running. Second place, four years "
    "running: Brother Al...\" She stops. \"Oh, you've GOT to be kidding.\"\n\n"
    "RODRICK (not listening, again): \"Gang! Trap! In the garden! A giant marrow, a net, a seesaw, a bucket and a very long rope. And for "
    "bait, the biggest, juiciest marrow in Bellwether!\"\n\nCRUMBS: \"I ate the marrow.\"\n\nRODRICK: \"...Then YOU'RE the bait.\"",
    [C('"I\'ll set it up in the garden."', "root", actions=[SQ(F2, 20), SF("fig2_trap_ready")])])
r.node("e2_done",
    "RODRICK: \"Another mystery...\"\n\nTHE GANG: \"FIGURED OUT!\"\n\nSNACKS: \"Hrrrroot!\"\n\n"
    "AGNES: \"Our trap caught a seesaw, a bucket, and Rodrick. Twice. Rolf caught the culprit, gently, and then gave him a cup of tea.\"\n\n"
    "RODRICK: \"TEAMWORK.\" He presents you, with enormous ceremony, a long orange scarf with a little embroidered question mark. \"The Figure "
    "It Out Gang scarf. Full member. You can't take it off. Well, you can. But you won't want to.\"",
    [C('"I\'ll wear it with pride."', "root", actions=[SQ(F2, 100), GI("core:item.gang_scarf"), GI("core:item.crumb_cake", 3), GG(120), XP("persuasion", 50)])])
r.node("later",
    "RODRICK: \"Never better! We're thinking about our next case. There's talk of a headless knight on the Old Road. Primrose says it's just "
    "a knight who's very short. Agnes says it's a hat on a stick. Crumbs barely knew her.\"\n\nCRUMBS (from somewhere): \"I BARELY KNEW HER!\"",
    [C('"Let me know."', "root")])

# ======================================================================= the rest of the gang
pn = new_dialogue("core:dialogue.figure_primrose")
p = Dlg("dlg.fig.prim", pn, PRIM)
p.node("root",
    "A tall, glamorous young woman in purple with red hair pinned up and a green silk scarf, examining her nails while leaning on the wagon.\n\n"
    "\"Lady Primrose Vane. I'm the one who gets kidnapped. It's a whole thing. Last week I was carried off by a ghost pirate. Turned out to "
    "be the harbour-master's cousin. I broke his nose.\"\n\nShe smiles sweetly. \"They always forget I can punch.\"",
    [C('"Any advice for a new member?"', "advice"), C('"Lovely to meet you."', "END")])
p.node("advice", "PRIMROSE: \"Never stand near Rodrick when he says 'trap'. Never let Crumbs hold the bait. And if anything grabs you from "
       "behind a bookcase, aim for the mask. It's always a mask.\" She considers. \"Except the one time.\"", [C('"The actual ghost."', "root")])
an = new_dialogue("core:dialogue.figure_agnes")
a = Dlg("dlg.fig.agn", an, AGN)
a.node("root",
    "A short young woman in a huge orange jumper, red skirt and very thick spectacles, reading three books at once.\n\n"
    "\"Agnes Thimble. I'm the one who actually solves it. They're the ones who fall into things.\" She pushes her spectacles up. They slide "
    "straight back down. \"My spectacles are perfectly fine. I lose them maybe once an episode. Twice, at most.\"",
    [C('"What do you make of the Phantom Clerk?"', "e1", [QE(F1, 10)]),
     C('"What do you make of the Howler?"', "e2", [QE(F2, 10)]),
     C('"Nice to meet you."', "END")])
a.node("e1", "AGNES: \"Ghosts don't need receipts. Look for one. And ghosts don't need to sell anything, either. Somebody's making money off "
       "this. Follow the money. Follow the luminous ink.\" A pause. \"Has anyone seen my spectacles?\" They are on her head.",
       [C('"On your head."', "root")])
a.node("e2", "AGNES: \"Real werewolves don't wear sandals, and Rolf doesn't steal his own marrows. Check the soil, check the fence, and check "
       "who comes second at the vegetable show. Jealousy is the oldest monster there is.\"", [C('"Got it."', "root")])
cn = new_dialogue("core:dialogue.figure_crumbs")
c = Dlg("dlg.fig.cru", cn, CRU)
c.node("root",
    "A lanky, scruffy young man in a baggy green shirt with a straggly beard, sitting on the wagon step eating a sandwich bigger than his head.\n\n"
    "\"Barnaby Moss. Everyone calls me Crumbs. Because of the... \" He gestures at his shirt, which is covered in crumbs. \"...the crumbs. "
    "I'm the one who gets chased.\"",
    [C('"Do you ever get scared?"', "scared"),
     C('"Why do you always say \'I barely knew her\'?"', "barely"),
     C('"Enjoy your sandwich."', "END")])
c.node("scared", "CRUMBS: \"Scared? Me? Only of ghosts. And monsters. And the dark. And skeletons. And Rodrick's plans. And the wagon "
       "when it makes that noise going downhill.\" He takes a bite. \"Snacks is braver than me. Snacks is NOT brave.\"", [C('"Fair."', "root")])
c.node("barely", "CRUMBS (thinking very hard): \"Every time we pull off a mask, everyone goes 'IT WAS HIM ALL ALONG!' or 'IT WAS HER!' and "
       "everyone's shocked. And I just... I barely knew her. Whoever it is. I barely knew her.\"\n\n\"Even the time it was a horse.\"",
       [C('"It was a horse?"', "horse")])
c.node("horse", "CRUMBS: \"Brown one. White blaze on the nose. Standing on a roof. Wasn't even a mystery. It was just a horse on a roof.\" "
       "He chews. \"I barely knew her.\"", [C('"...I think I know that horse."', "root")])
sn = new_dialogue("core:dialogue.figure_snacks")
s = Dlg("dlg.fig.sna", sn, SNA)
s.node("root",
    "An owlbear cub the size of a large dog, all brown feathers and fluffy fur, with an owl's face and enormous worried eyes. It looks at you, "
    "then at your pockets, then at you again, with naked hope.\n\n\"Hrrr-oo?\"",
    [C("Give Snacks a Crumb Cake.", "cake", [{"type": "has_item", "item_id": "core:item.crumb_cake"}], [TI("core:item.crumb_cake")]),
     C('"Are you brave, Snacks?"', "brave"),
     C("Scratch Snacks behind the ear-tufts.", "scratch"),
     C("Leave.", "END")])
s.node("cake", "Snacks catches the Crumb Cake out of the air, swallows it whole, and does a little spin. Then a backflip. Then, overwhelmed "
       "with joy, it falls over and lies there with all four feet in the air.\n\nRODRICK (from the wagon): \"Would you do something brave for a "
       "Crumb Cake, Snacks?\"\n\nSNACKS (from the ground, considering): \"Hrrr... HRRR-nope.\"", [C("Laugh.", "root")], [{"type": "sanity", "amount": 8}])
s.node("brave", "Snacks immediately hides behind you. It does not fit behind you. Most of it is still visible. It seems happy with the arrangement.",
       [C('"Very brave."', "root")])
s.node("scratch", "Snacks leans into the scratch with its whole weight, makes a noise halfway between a purr and a hoot, and slowly falls "
       "over sideways. You feel better. You're not sure why.", [C("Keep scratching.", "root")], [{"type": "sanity", "amount": 5}])

# ======================================================================= the unmaskings
vn = new_dialogue("core:dialogue.unmask_clerk")
v = Dlg("dlg.fig.unmask1", vn, "npc.unmask_clerk.name")
v.node("root",
    "The net (on its fourth attempt, after Baggy, a pigeon and Rodrick) has finally caught the right person: the Phantom Clerk lies in a heap of "
    "glowing bedsheet, tangled, groaning. The whole gang gathers round. Somewhere a dramatic chord plays, although nobody brought an instrument.\n\n"
    "RODRICK: \"Now let's see who the Phantom Clerk REALLY is!\"",
    [C('"It\'s Vaelen. The merchant. Selling ghost charms to a frightened village."', "reveal", [FL(CLUES1, 3)], [SF("fig1_guessed")]),
     C('"It\'s... Clerk Oakhaven?"', "wrong_oak"),
     C("Just pull the mask off.", "reveal")])
v.node("wrong_oak", "PRIMROSE: \"Darling, Oakhaven stamps DECEASED on paperwork, not doors. He'd never deface a door. He'd fill in a form "
       "to request permission to deface a door, and then decide against it.\"", [C("Fair. Pull the mask off.", "reveal")])
v.node("reveal",
    "Rodrick grabs the glowing hood and pulls. The sheet comes away.\n\nIt's Vaelen.\n\nTHE GANG: \"VAELEN?!\"\n\nCRUMBS: \"I barely knew her!\"\n\n"
    "VAELEN (still tangled in the net, furious): \"Yes, all right, it's me! I bought a crate of Ghost-B-Gone charms from a man in Saltmere "
    "and NOBODY WANTED THEM. So I gave the village a ghost! Business was BOOMING!\"\n\n\"And I would have got away with it, too, if it "
    "weren't for you nosy busybodies and your cowardly owlbear!\"\n\nSNACKS (proudly): \"Hrrr-oo!\"",
    [C('"Refund everybody, Vaelen."', "refund")], [SF("fig1_unmasked")])
v.node("refund", "VAELEN (sulking): \"Fine. FINE. Refunds. Two silver a charm.\" A pause. \"...Although if anyone wants to keep one as a "
       "souvenir of the Night of the Phantom Clerk, it's five.\"\n\nAgnes writes something in a notebook. It is the word 'INCORRIGIBLE'.",
       [C("Head back to the wagon.", "END")], [SQ(F1, 50), SF("fig1_done")])
hn = new_dialogue("core:dialogue.unmask_howler")
h = Dlg("dlg.fig.unmask2", hn, "npc.unmask_howler.name")
h.node("root",
    "The Howler lies tangled in a net, a seesaw, and most of a bucket, in the middle of Rolf's ruined marrow bed. It whimpers. It's very "
    "hairy. It's wearing sandals.\n\n"
    "RODRICK: \"Before we unmask this fiend, let's be thorough!\" He marches over to Rolf, who's watching from the greenhouse door, and grabs "
    "him by the face. \"FIRST, WE UNMASK THE OBVIOUS SUSPECT!\"\n\n"
    "He pulls.\n\nROLF: \"OW. That's my face. That's my actual face.\"\n\nRODRICK: \"...So it is. Sorry, Rolf.\"\n\nCRUMBS: \"I barely knew her.\"",
    [C("Unmask the actual Howler.", "guess")])
h.node("guess", "RODRICK (rubbing his hands): \"Right! The REAL Howler of Hollowmere is...!\"",
       [C('"Brother Aldous. Second place at the Marrow Show. Four years running."', "reveal", [FL(CLUES2, 3)], [SF("fig2_guessed")]),
        C('"Lord Ashgrave. He\'s been looking at those marrows."', "wrong_ash"),
        C("Just pull the mask off.", "reveal")])
h.node("wrong_ash", "LORD ASHGRAVE (appearing at an upstairs window, wounded): \"I do not EAT marrows. I gaze upon them. In the moonlight. "
       "It's different.\"", [C("Pull the mask off.", "reveal")])
h.node("reveal",
    "The fur comes away in one piece. Underneath, red-faced and covered in soil, is Brother Aldous.\n\nTHE GANG: \"BROTHER ALDOUS?!\"\n\n"
    "CRUMBS: \"I barely knew her!\"\n\n"
    "BROTHER ALDOUS: \"Four years! FOUR YEARS I've come second to a werewolf's marrows! I prayed! I fertilised! I sang to my marrows every "
    "dawn! And he just... grows them! Shirtless! Effortlessly!\"\n\n\"And I would have got away with it, too, if it weren't for you nosy "
    "busybodies and that... that BEAUTIFUL owlbear.\"\n\nSNACKS (melting): \"Hrrr-ooo.\"",
    [C("Look at Rolf.", "rolf")], [SF("fig2_unmasked")])
h.node("rolf",
    "Rolf walks over, very slowly. Everyone braces.\n\nRolf kneels down in the soil, and puts a huge hand on Brother Aldous's shoulder.\n\n"
    "ROLF: \"You should have just ASKED. It's the eggshells. And talking to them. Not singing: talking. They like conversation.\" He helps "
    "the brother up. \"Come round tomorrow. I'll show you. We'll grow marrows together. Next year we can share first place.\"\n\n"
    "Brother Aldous bursts into tears. So does Crumbs, for some reason.",
    [C("Head back to the wagon.", "END")], [SQ(F2, 50), SF("fig2_done")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= NPCs, creatures, items, quests, campaign
N = load("content/npcs/core_npcs.json")
def npc(nid, sprite, dlg, scale, title=True, barks=None, anim="assets/animations/npc_standard.json"):
    e = {"id": nid, "name_key": f"npc.{nid.split('.')[-1]}.name", "faction": "core:faction.ashbound", "dialogue_id": dlg,
         "appearance": {"type": "sprite_8dir", "sprite_sheet": sprite, "animation_data": anim, "scale": scale}, "barks": barks or []}
    if title:
        e["title_key"] = f"npc.{nid.split('.')[-1]}.title"
    N["npcs"].append(e)
npc("core:npc.figure_rodrick", "assets/sprites/npcs/figure_rodrick.png", "core:dialogue.figure_rodrick", 1.8, barks=[{"text_key": "bark.fig.rod"}])
npc("core:npc.figure_primrose", "assets/sprites/npcs/figure_primrose.png", "core:dialogue.figure_primrose", 1.78, barks=[{"text_key": "bark.fig.prim"}])
npc("core:npc.figure_agnes", "assets/sprites/npcs/figure_agnes.png", "core:dialogue.figure_agnes", 1.6, barks=[{"text_key": "bark.fig.agn"}])
npc("core:npc.figure_crumbs", "assets/sprites/npcs/figure_crumbs.png", "core:dialogue.figure_crumbs", 1.82, barks=[{"text_key": "bark.fig.cru"}])
npc("core:npc.figure_snacks", "assets/sprites/npcs/figure_snacks.png", "core:dialogue.figure_snacks", 1.5, barks=[{"text_key": "bark.fig.sna"}])
npc("core:npc.unmask_clerk", "assets/sprites/npcs/merchant_vaelen_painted.png", "core:dialogue.unmask_clerk", 1.75,
    anim="assets/animations/npc_standard_128.json")
npc("core:npc.unmask_howler", "assets/sprites/npcs/brother_aldous_painted.png", "core:dialogue.unmask_howler", 1.75,
    anim="assets/animations/npc_standard_128.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.merchant_vaelen":
        n["barks"].append({"text_key": "bark.vaelen.unmasked", "flag": "fig1_done"})
    if n["id"] == "core:npc.brother_aldous":
        n["barks"].append({"text_key": "bark.aldous.unmasked", "flag": "fig2_done"})
    if n["id"] == "core:npc.werewolf_rolf":
        n["barks"].append({"text_key": "bark.rolf.unmasked", "flag": "fig2_done"})
save("content/npcs/core_npcs.json", N)
S.update({
    "npc.figure_rodrick.name": "Sir Rodrick Ascot-Smythe", "npc.figure_rodrick.title": "Leader, Figure It Out Gang",
    "npc.figure_primrose.name": "Lady Primrose Vane", "npc.figure_primrose.title": "Professionally Kidnapped",
    "npc.figure_agnes.name": "Agnes Thimble", "npc.figure_agnes.title": "The One Who Actually Solves It",
    "npc.figure_crumbs.name": "Barnaby 'Crumbs' Moss", "npc.figure_crumbs.title": "Gets Chased",
    "npc.figure_snacks.name": "Snacks", "npc.figure_snacks.title": "Owlbear (Cowardly)",
    "npc.unmask_clerk.name": "The Phantom Clerk (Netted)", "npc.unmask_clerk.title": "Mystery Suspect",
    "npc.unmask_howler.name": "The Howler (Netted, Bucketed)", "npc.unmask_howler.title": "Mystery Suspect",
    "bark.fig.rod": "Gang! Let's split up and look for clues!",
    "bark.fig.prim": "If I get kidnapped again this week, I'm charging.",
    "bark.fig.agn": "Has anyone seen my spectacles? ...They're on my head, aren't they.",
    "bark.fig.cru": "I barely knew her!",
    "bark.fig.sna": "Hrrr-oo? (It's looking at your pockets.)",
    "bark.vaelen.unmasked": "Ghost-B-Gone charms! Half price! Souvenir of the Night of the Phantom Clerk! ...No? Nobody?",
    "bark.aldous.unmasked": "Eggshells. And conversation. Who knew. Rolf knew.",
    "bark.rolf.unmasked": "Brother Aldous and I are co-growing a marrow this year. It's going to be ENORMOUS.",
})
CR = load("content/creatures/core_creatures.json")
for cid, name, sheet, scale, hp, dmg, alert, death in [
        ("phantom_clerk", "The Phantom Clerk", "phantom_clerk", 1.9, 70, 6, "DECEEEEASED... DECEEEEASED... (it sounds a lot like someone with a cold)",
         "OW! Watch the sheet! This is good linen!"),
        ("howler", "The Howler of Hollowmere", "howler", 2.0, 90, 8, "AWOOOO! (It's a very human 'awooo'. Like someone reading the word 'awooo' out loud.)",
         "My marrows... MY MARROWS..."),
]:
    CR["creatures"].append({"id": f"core:enemy.{cid}", "name_key": f"enemy.{cid}.name",
        "appearance": {"type": "sprite_8dir", "sprite_sheet": f"assets/sprites/enemies/{sheet}.png", "animation_data": "assets/animations/skeleton.json", "scale": scale},
        "stats": {"health": hp, "armor": 0, "move_speed": 2.6, "xp_reward": 30}, "behavior": "melee_patroller", "family": "beast",
        "perception": {"sight_meters": 12.0, "hearing_meters": 9.0},
        "attack": {"name": "spooky_flail", "damage": dmg, "reach_meters": 1.6, "windup_seconds": 0.6, "cooldown_seconds": 1.4, "sanity_damage": 2},
        "loot_table": "core:loot.vermin_drop",
        "audio": {"alert": "assets/audio/sfx/boss_roar.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav",
                  "death": "assets/audio/sfx/enemy_death.wav"},
        "hit_fx": {"color": [240, 240, 230], "glow": False},
        "lines": {"alert": f"line.{cid}.alert", "death": f"line.{cid}.death"}})
    S[f"enemy.{cid}.name"] = name
    S[f"line.{cid}.alert"] = alert
    S[f"line.{cid}.death"] = death
save("content/creatures/core_creatures.json", CR)

CI = load("content/items/consumables_and_books.json")
CI["items"].append({"id": "core:item.crumb_cake", "name_key": "item.crumb_cake.name", "description_key": "item.crumb_cake.description", "category": "consumable",
                    "icon": "assets/ui/items/crumb_cake.png", "world_model": "assets/models/items/bread_loaf.glb", "slots": [], "stackable": True, "value": 6,
                    "weight": 0.1, "effects": [{"type": "consumable_heal", "amount": 15}, {"type": "consumable_sanity", "amount": 10},
                                               {"type": "buff", "stat": "move_speed_bonus", "value": 0.12, "duration": 60}]})
save("content/items/consumables_and_books.json", CI)
A = load("content/items/armor_and_gear.json")
A["items"].append({"id": "core:item.gang_scarf", "name_key": "item.gang_scarf.name", "description_key": "item.gang_scarf.description", "category": "accessory",
                   "icon": "assets/ui/items/gang_scarf.png", "world_model": "assets/models/items/leather_jerkin.glb", "slots": ["accessory"], "value": 180,
                   "weight": 0.2, "armor": 0, "effects": [{"type": "bonus", "stat": "crit_chance_bonus", "value": 0.05}, {"type": "bonus", "stat": "sanity_regen", "value": 0.6},
                                                          {"type": "bonus", "stat": "dice_bonus", "value": 1.0}, {"type": "bonus", "stat": "move_speed_bonus", "value": 0.05}]})
save("content/items/armor_and_gear.json", A)
S.update({
    "item.crumb_cake.name": "Crumb Cake",
    "item.crumb_cake.description": "Snacks's favourite. Crumbs's favourite. A dense little honey cake that makes you feel briefly braver than you are. Heals 15, +10 sanity, and you run 12% faster for a minute (away from things, mostly).",
    "item.gang_scarf.name": "Figure It Out Gang Scarf",
    "item.gang_scarf.description": "Long, orange, with a little embroidered question mark. Full membership of the Figure It Out Gang. +5% critical chance, +5% speed, steadier nerves, +1 to dice rolls. You will be chased by something at least once a week.",
})

QQ = load("content/quests/chapter_zero_quests.json")
QQ["campaigns"].append({"id": "figure_it_out", "name_key": "campaign.figure.name", "desc_key": "campaign.figure.desc", "kind": "tales", "order": 32})
S["campaign.figure.name"] = "The Figure It Out Gang"
S["campaign.figure.desc"] = "A wagon, four meddling young sleuths, a cowardly owlbear, and a lot of people in masks. Silly, not especially competent, spooky, and somehow always successful."
for qid, short, clue_markers, trap, monster, unmask in [
        (F1, "fig1", ["fig1_clue_ink", "fig1_clue_receipt", "fig1_clue_tags"], "fig1_trap", "fig1_phantom", "npc_unmask_clerk"),
        (F2, "fig2", ["fig2_clue_prints", "fig2_clue_wool", "fig2_clue_list"], "fig2_trap", "fig2_howler", "npc_unmask_howler")]:
    QQ["quests"].append({"id": qid, "title_key": f"quest.{short}.title", "summary_key": f"quest.{short}.summary", "campaign": "figure_it_out",
        "stages": [
            {"stage": 0, "objective_key": f"quest.{short}.stage0", "journal_key": f"quest.{short}.journal0", "markers": ["npc_figure_rodrick"]},
            {"stage": 10, "objective_key": f"quest.{short}.stage10", "journal_key": f"quest.{short}.journal10", "markers": clue_markers + ["npc_figure_rodrick"]},
            {"stage": 20, "objective_key": f"quest.{short}.stage20", "journal_key": f"quest.{short}.journal20", "markers": [trap]},
            {"stage": 30, "objective_key": f"quest.{short}.stage30", "journal_key": f"quest.{short}.journal30", "markers": [monster]},
            {"stage": 40, "objective_key": f"quest.{short}.stage40", "journal_key": f"quest.{short}.journal40", "markers": [unmask]},
            {"stage": 50, "objective_key": f"quest.{short}.stage50", "journal_key": f"quest.{short}.journal50", "markers": ["npc_figure_rodrick"]},
            {"stage": 100, "objective_key": f"quest.{short}.stage100", "journal_key": f"quest.{short}.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.fig1.title": "The Figure It Out Gang: The Phantom Clerk of Bellwether",
    "quest.fig1.summary": "A glowing ghost in Bureau robes stamps DECEASED on the doors of living people. Somebody is selling a lot of ghost charms.",
    "quest.fig1.stage0": "Talk to Sir Rodrick at the Figure It Out Wagon (Old Road).",
    "quest.fig1.journal0": "A painted wagon on the Old Road. A gang of young sleuths. A mystery.",
    "quest.fig1.stage10": "Split up and look for clues in Bellwether: the Records Office step, the alleys, behind the market stalls. Then report to Rodrick.",
    "quest.fig1.journal10": "The Phantom Clerk of Bellwether. Rodrick said 'let's split up'. Agnes sighed. Crumbs ran.",
    "quest.fig1.stage20": "Set Rodrick's trap in the middle of Bellwether's square.",
    "quest.fig1.journal20": "A net, a pulley, a barrel of feathers, and me as the bait. What could go wrong.",
    "quest.fig1.stage30": "Catch the Phantom Clerk!",
    "quest.fig1.journal30": "The trap caught Baggy, a pigeon and Rodrick. Then the Phantom Clerk appeared.",
    "quest.fig1.stage40": "Unmask the Phantom Clerk.",
    "quest.fig1.journal40": "The Phantom Clerk is down, tangled in the net. Time to see who's under the sheet.",
    "quest.fig1.stage50": "Tell Rodrick the mystery is figured out.",
    "quest.fig1.journal50": "It was Vaelen. Of course it was Vaelen. Crumbs barely knew her.",
    "quest.fig1.stage100": "Completed: another mystery FIGURED OUT.",
    "quest.fig1.journal100": "Honorary member of the Figure It Out Gang. Paid in Crumb Cakes.",
    "quest.fig2.title": "The Figure It Out Gang: The Howler of Hollowmere",
    "quest.fig2.summary": "Something huge and hairy is stealing the prize marrows from Rolf's garden. Rolf is a werewolf. Rodrick finds this suspicious.",
    "quest.fig2.stage0": "Talk to Sir Rodrick at the Figure It Out Wagon.",
    "quest.fig2.journal0": "Another case for the gang.",
    "quest.fig2.stage10": "Look for clues in Rolf's garden at Hollowmere Manor, then report to Rodrick.",
    "quest.fig2.journal10": "The Howler of Hollowmere: howling, claws, stolen marrows. Agnes says check who comes second at the vegetable show.",
    "quest.fig2.stage20": "Set the trap in Rolf's garden.",
    "quest.fig2.journal20": "A giant marrow, a net, a seesaw, a bucket and a very long rope. Crumbs ate the marrow.",
    "quest.fig2.stage30": "Catch the Howler!",
    "quest.fig2.journal30": "The seesaw launched Rodrick. The Howler appeared.",
    "quest.fig2.stage40": "Unmask the Howler.",
    "quest.fig2.journal40": "The Howler is tangled in a net, a seesaw and most of a bucket.",
    "quest.fig2.stage50": "Tell Rodrick.",
    "quest.fig2.journal50": "It was Brother Aldous, jealous of four years of second place. Rolf offered to teach him. Everyone cried.",
    "quest.fig2.stage100": "Completed: mystery FIGURED OUT. Full member of the gang.",
    "quest.fig2.journal100": "I have the scarf. I'll be chased by something at least once a week.",
    "story.fig1.trap": "You set the trap in the middle of the square: a net hung from the lantern post, a pulley, a rope, a barrel of feathers balanced on top, and you, standing on the X, feeling like bait.\n\nThe gang hides behind a cart. Snacks hides behind Crumbs. Crumbs hides behind Snacks.\n\nFootsteps. Rodrick yanks the rope. The net falls, and catches Baggy, who was just passing, investigating something. Rodrick resets it. It catches a pigeon. Rodrick, in his excitement, steps on the rope and catches himself. The barrel of feathers tips over onto all three.\n\nAnd then, out of the mist, glowing, moaning, comes the Phantom Clerk.",
    "story.fig2.trap": "You set the trap in Rolf's garden: a net over the marrow bed, a seesaw, a bucket, a very long rope, and Crumbs crouched in the middle of the bed pretending to be a marrow. He's not very convincing. He's eating.\n\nMidnight. A howl. Rodrick, overexcited, jumps on the seesaw. The seesaw launches the bucket. The bucket lands on Rodrick. Rodrick, blind, pulls the rope. The net falls on Agnes, who has lost her spectacles.\n\nAnd from behind the greenhouse, huge, hairy and wearing what are very clearly sandals, comes the Howler of Hollowmere.",
})

# ======================================================================= placement
def readable(iid, x, y, z, prompt, title, text, flag, req, model=""):
    return {"instance_id": iid, "type": "readable", "model": model, "pos": [x, y, z], "rot_y": 0.0, "prompt": prompt, "title": title, "text": text,
            "set_flag": flag, "requires_flag": req}
R = load("content/regions/old_road.json")
R["props"].append({"id": "figure_wagon", "model": "assets/models/props/figure_wagon.glb", "pos": [22.5, 0.0, -9.6], "rot_y": 0.0, "scale": [1, 1, 1], "solid": True})
R["props"].append({"id": "figure_campfire", "model": "assets/models/props/wall_torch.glb", "pos": [20.5, -0.55, -6.0], "rot_y": 0.0, "scale": [1, 1, 1], "solid": False,
                   "emitter": {"sprite": "assets/sprites/vfx/torch_flame.png", "offset": [0.0, 0.86, 0.0], "size": 0.5, "light_color": [1.0, 0.6, 0.3], "light_radius": 7.0}})
for i, (nid, x, z, yaw) in enumerate([("figure_rodrick", 18.6, -6.4, 160.0), ("figure_primrose", 20.0, -4.6, 200.0), ("figure_agnes", 22.4, -5.2, 210.0),
                                      ("figure_crumbs", 24.2, -7.4, 240.0), ("figure_snacks", 25.2, -8.4, 250.0)]):
    R["npcs"].append({"instance_id": f"npc_{nid}", "npc_id": f"core:npc.{nid}", "pos": [x, 0.0, z], "yaw": yaw})
R["interactables"].append({"instance_id": "figure_wagon_sign", "type": "readable", "model": "", "pos": [21.0, 0.0, -8.6], "rot_y": 0.0,
                           "prompt": "Read the Wagon's Side", "title": "The Figure It Out Wagon",
                           "text": "Painted along the side in enormous wobbly letters, between the flowers:\n\nTHE FIGURE IT OUT GANG\nMysteries Solved! Monsters Unmasked! Reasonable Rates!\n\nUnderneath, in smaller letters, added later: \"Not responsible for traps.\"\n\nUnderneath THAT, smaller still, in Agnes's handwriting: \"Rodrick is responsible for traps.\""})
save("content/regions/old_road.json", R)
B = load("content/regions/bellwether.json")
B["interactables"] += [
    readable("fig1_clue_ink", -6.5, 0.0, -8.6, "Examine the Glowing Smear", "A Smear of Glowing Ink",
             "A smear of something that glows faintly green on the Records Office step, like a footprint. You dab it with a finger. It's luminous ink, the expensive kind they sell in Saltmere. It comes off on your hand.\n\nGhosts, as far as you know, don't leave footprints. And they certainly don't buy ink.", "fig1_c1", "fig1_open"),
    readable("fig1_clue_receipt", -13.0, 0.0, -1.0, "Pick Up the Crumpled Paper", "A Crumpled Receipt",
             "A receipt, screwed up and thrown into the alley:\n\nSALTMERE DRAPERS & SUNDRIES\n1 x bedsheet, extra large, white ... 6 silver\n1 x jar luminous ink ... 1 gold\n1 x 'Ghost-B-Gone' charms, crate of 200 ... 40 gold (NO REFUNDS)\nPaid in full. Thank you, V.\n\nThe 'V' is underlined twice.", "fig1_c2", "fig1_open"),
    readable("fig1_clue_tags", 7.0, 0.0, -12.4, "Look Behind the Stall", "A Box Behind the Market Stall",
             "Behind the market stall, half-hidden under a tarpaulin: an empty crate stencilled GHOST-B-GONE, a pot of glue, and a stack of new price tags.\n\nThe old tags say 1 SILVER. The new tags say 5 GOLD. The dates on them are the morning after the Phantom Clerk first appeared.", "fig1_c3", "fig1_open"),
    {"instance_id": "fig1_trap", "type": "readable", "model": "", "pos": [0.0, 0.0, 2.0], "rot_y": 0.0, "prompt": "Set Rodrick's Trap", "title": "The Trap",
     "text": "(The trap is set.)", "set_flag": "fig1_trap", "requires_flag": "fig1_trap_ready", "hidden_flag": "fig1_trap", "quest_id": F1, "set_stage": 30,
     "narration": ["story.fig1.trap"]},
]
B["creatures"].append({"instance_id": "fig1_phantom", "creature_id": "core:enemy.phantom_clerk", "pos": [0.0, 0.0, -3.0], "patrol_a": [-2.0, 0.0, -3.0],
                       "patrol_b": [2.0, 0.0, -3.0], "requires_flag": "fig1_trap", "group": "fig1", "group_quest_id": F1, "group_set_stage": 40,
                       "group_set_flag": "fig1_caught"})
B["npcs"].append({"instance_id": "npc_unmask_clerk", "npc_id": "core:npc.unmask_clerk", "pos": [0.6, 0.0, -2.2], "yaw": 180.0,
                  "requires_flag": "fig1_caught", "hidden_flag": "fig1_done"})
save("content/regions/bellwether.json", B)

block = "# ============================================================================ Figure It Out Gang, episode 2 (tools/authoring/figure_it_out.py)\n"
for d in [readable("fig2_clue_prints", 10.5, 0.0, -12.6, "Examine the Pawprints", "Pawprints in the Soil",
                   "Huge pawprints, deep in the soft soil between the marrow beds. Very convincing. Very scary.\n\nExcept that pressed into the bottom of every single one is the clear, neat tread of a sandal. A size nine. With a little sun stamped on the heel.", "fig2_c1", "fig2_open"),
          readable("fig2_clue_wool", 17.0, 0.0, -12.5, "Look at the Fence", "A Scrap Caught on the Fence",
                   "A scrap of rough brown wool caught on a nail in the garden fence. Coarse, hand-woven, the kind used for religious habits.\n\nAnd a single fake claw, made of painted wood, lying in the grass beneath it.", "fig2_c2", "fig2_open"),
          readable("fig2_clue_list", 9.0, 0.0, -14.3, "Read the Pinned-Up List", "Bellwether Marrow Show: Previous Results",
                   "Pinned to the potting shed, a list in Rolf's enormous handwriting:\n\nBELLWETHER MARROW SHOW\nYear 1: 1st Rolf. 2nd Br. Aldous.\nYear 2: 1st Rolf. 2nd Br. Aldous.\nYear 3: 1st Rolf. 2nd Br. Aldous.\nYear 4: 1st Rolf. 2nd Br. Aldous (protest lodged, dismissed).\n\nAt the bottom: \"This year's show is next week! Good luck everyone! Especially Aldous! -Rolf\"", "fig2_c3", "fig2_open"),
          {"instance_id": "fig2_trap", "type": "readable", "model": "", "pos": [12.5, 0.0, -14.3], "rot_y": 0.0, "prompt": "Set Rodrick's Trap",
           "title": "The Trap", "text": "(The trap is set.)", "set_flag": "fig2_trap", "requires_flag": "fig2_trap_ready", "hidden_flag": "fig2_trap",
           "quest_id": F2, "set_stage": 30, "narration": ["story.fig2.trap"]}]:
    block += "interactables.append(" + repr(d) + ")\n"
block += ("creature(\"fig2_howler\", \"core:enemy.howler\", (11.5, 0.0, -14.3), (10.0, 0.0, -14.3), (13.0, 0.0, -14.3), requires_flag=\"fig2_trap\", "
          "group=\"fig2\", group_quest_id=\"" + F2 + "\", group_set_stage=40, group_set_flag=\"fig2_caught\")\n")
block += ("npcs.append({\"instance_id\": \"npc_unmask_howler\", \"npc_id\": \"core:npc.unmask_howler\", \"pos\": [11.8, 0.0, -13.6], \"yaw\": 180.0, "
          "\"requires_flag\": \"fig2_caught\", \"hidden_flag\": \"fig2_done\"})\n\n")
src = open("tools/build_mansion.py").read()
src = src.replace("region = {", block + "region = {", 1)
open("tools/build_mansion.py", "w").write(src)

S["tip.38"] = "If a mystery gang tells you to split up, split up. It never works. It always works."
loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

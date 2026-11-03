"""Campaign Four: The Dragon's Pension. Cindermaw the Elder, nine hundred years old, slept through three centuries of census
letters and has been declared legally deceased; the pension (eleven gold, one sheep and one apology per century) is
cancelled and the hoard is to be 'transferred to the designated heir'. The dragon lands in Bellwether's square, furious.
Prove it's alive (three witnesses, the Register of Hatchings from Fenwick, a likeness taken with Pickering's box), file
Form 9-L with Oakhaven, then win the hearing against the kobold executor who filed the death notice. He summons a
Repossession Golem. Reward: Dragon's Sigh (a fire nova) and one of Cindermaw's scales.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q = "core:quest.dragon_pension"
I = lambda n: f"core:item.{n}"
QE = lambda s: {"type": "quest_stage_equals", "quest_id": Q, "stage": s}
QA = lambda s: {"type": "quest_stage_at_least", "quest_id": Q, "stage": s}
QB = lambda s: {"type": "quest_stage_below", "quest_id": Q, "stage": s}
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
HI = lambda i: {"type": "has_item", "item_id": I(i)}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}
GI = lambda i, q=1: {"type": "give_item", "item_id": I(i), "qty": q}
TI = lambda i, q=1: {"type": "take_item", "item_id": I(i), "qty": q}
WIT = ["dwit_marta", "dwit_vaelen", "dwit_baggy", "dwit_hollis", "dwit_sabrino", "dwit_steve", "dwit_grout"]
W3 = {"type": "flags_at_least", "flags": WIT, "value": 3}
DRAGON = "npc.dragon_cindermaw.name"

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
    """topics: (choice text, node id, conditions, node text, node actions, back-choice text)"""
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

# ------------------------------------------------------------------ Oakhaven: the start, the filing, the epilogue
add_topics("core:dialogue.clerk_oakhaven", "dlg.dp.oak", "npc.clerk_oakhaven.name", [
    ('"You look worried, Oakhaven."', "dp_start", [QB(0)],
     "Oakhaven is holding a letter in both hands. They are shaking, slightly.\n\n\"I have made... an error. Possibly. The Bureau has. "
     "Three hundred years ago, the census letters to a certain address in the eastern mountains stopped being answered. After three "
     "centuries of silence, the procedure is automatic.\" He swallows. \"The resident was declared legally deceased. Their pension "
     "was cancelled. Their estate was released to the designated heir.\"\n\n\"This morning I received a reply.\" He turns the letter round. "
     "It is scorched around the edges. In letters a foot high, burned into the paper: I AM NOT DEAD. I WAS ASLEEP. I AM COMING.\n\n"
     "Outside, something very large lands in the square. The windows rattle. Somebody screams. A pigeon faints.\n\n\"That,\" says "
     "Oakhaven quietly, \"will be the resident.\"",
     [SQ(0), SQ(10), SF("dragon_arrived")], "\"I'll go and talk to it.\""),
    ('"I have the proof of life: witnesses, the hatching record, a likeness."', "dp_file",
     [QE(20), W3, HI("hatching_record"), HI("dragon_likeness")],
     "Oakhaven lays everything out on the desk, squares the edges, and reads it all twice. Then he takes out a fresh Form 9-L (Proof of "
     "Continued Existence, Non-Human, Large) and fills it in with enormous care.\n\n\"Witnesses: sufficient. Hatching record: genuine. "
     "Likeness: unflattering, but accurate.\" He stamps it. ALIVE. The stamp has clearly never been used before. He looks at it fondly.\n\n"
     "Then he frowns, and pulls the original death notice from the file.\n\n\"The death notice was filed by the designated heir. A "
     "'G. Quillsby, Esquire, Hoard Executor'.\" He reads further. His eyebrows climb. \"Filed... the day after the last census letter "
     "went unanswered. That is very prompt. Suspiciously prompt.\"\n\n\"Mr Quillsby is here. Today. To collect the estate at noon. He's "
     "waiting in the side office.\" Oakhaven straightens his cuffs. \"I believe this calls for a hearing.\"",
     [SQ(30), SF("dragon_hearing"), TI("hatching_record"), TI("dragon_likeness")], "\"Let's have a hearing.\""),
    ('"About Quillsby..."', "dp_epilogue", [QA(100)],
     "\"Mr Quillsby has been arrested for fraud, and for repossessing a living dragon without a permit.\" Oakhaven allows himself a "
     "very small smile.\n\n\"I have also declared him legally deceased. As a precaution. He can appeal. The forms take three hundred "
     "years.\"",
     None, "\"Perfect.\""),
])

# ------------------------------------------------------------------ Cindermaw the Elder
dr = new_dialogue("core:dialogue.dragon_cindermaw", "dlg.dp.dr", DRAGON)
dr("root",
   "A dragon is lying in the middle of Bellwether's square, which it fills. Its scales are the dull red of old embers, its horns are "
   "chipped with age, and it is wearing, on one claw, a pair of tiny reading spectacles. Smoke curls from its nostrils with every "
   "breath. The village has gone very quiet.\n\nOne vast golden eye swivels to look at you.\n\n\"YOU. SMALL ONE. ARE YOU THE BUREAU?\"",
   [('"I\'m here to help sort out your pension."', "intro", {"conditions": [QE(10)]}),
    ('"How are you holding up?"', "waiting", {"conditions": [QA(20), QB(50)]}),
    ('"Could I take your likeness? With this box."', "likeness", {"conditions": [QE(20), HI("likeness_box")]}),
    ('"It\'s done. Your pension is restored."', "done", {"conditions": [QE(50)]}),
    ('"How\'s retirement?"', "after", {"conditions": [QA(100)]}),
    ("Back away slowly.", "END")])
dr("intro",
   "\"PENSION? WHAT ABOUT TENSION?\" The dragon squints. \"SPEAK UP. I AM NINE HUNDRED YEARS OLD.\"\n\nYou speak up.\n\n"
   "\"AH. THE PENSION.\" A great sigh, like a forge cooling. \"ELEVEN GOLD COINS, ONE SHEEP, AND ONE APOLOGY. PER CENTURY. THE TREATY OF "
   "ASHFALL, SIGNED BY MY GRANDMOTHER AND YOUR KING, IN EXCHANGE FOR NOT EATING THE KINGDOM.\"\n\n\"I TAKE A NAP. A SMALL NAP. THREE "
   "HUNDRED YEARS. I WAKE UP, AND I AM DEAD. MY PENSION: GONE. MY HOARD: 'TRANSFERRED TO THE DESIGNATED HEIR'. I HAVE NO HEIR. I HAVE "
   "A HOARD-KEEPER. A KOBOLD. VERY GOOD WITH NUMBERS.\" The eye narrows. \"TOO GOOD, PERHAPS.\"",
   [('"What do you need?"', "deal")])
dr("deal",
   "\"I NEED TO NOT BE DEAD. ON PAPER. I AM QUITE ALIVE OFF PAPER.\" A small puff of flame. A hay cart nearby catches fire; somebody "
   "puts it out with a bucket, apologising.\n\n\"YOUR CLERK SAYS THERE IS A FORM. HE SAYS I NEED WITNESSES WHO HAVE SEEN ME ALIVE: THREE. "
   "MY HATCHING RECORD, FROM YOUR LIBRARY. AND A 'RECENT LIKENESS'.\" The dragon looks deeply offended. \"I HAVE NOT SAT FOR A PORTRAIT "
   "IN SIX HUNDRED YEARS.\"\n\n\"BRING THESE THINGS. I WILL WAIT. I WILL WAIT HERE. IN YOUR SQUARE.\" It settles its chin on its claws. \"I AM "
   "VERY GOOD AT WAITING.\"",
   [('"Three witnesses, the hatching record, a likeness. Got it."', "root", {"actions": [SQ(20)]})])
dr("waiting",
   "\"A CHILD BROUGHT ME A SHEEP.\" The dragon looks moved. \"I DID NOT EAT IT. WE ARE FRIENDS NOW. HIS NAME IS GERALD.\"\n\nA sheep is "
   "sleeping peacefully against the dragon's foreleg.",
   [('"That\'s lovely."', "root")])
dr("likeness",
   "You set up Professor Pickering's likeness box: a wooden case on legs with a brass lens and a black cloth. You duck under the cloth.\n\n"
   "\"HOLD STILL,\" you shout.\n\n\"I AM A DRAGON. I HAVE NOT MOVED IN THREE HUNDRED YEARS.\"\n\nThere is a flash. The dragon blinks. "
   "The box whirs, clunks, and slides out a silvery plate. It's a perfect likeness, including the reading spectacles, and the dragon is "
   "very clearly in the middle of sneezing.\n\n\"...BURN IT.\"\n\n\"It's accurate.\"\n\n\"...KEEP IT. BUT TELL NO ONE.\"",
   [('"Thank you, Cindermaw."', "root")], [TI("likeness_box"), GI("dragon_likeness")])
dr("done",
   "You tell the dragon everything: the hearing, the kobold, the golem.\n\nCindermaw listens without moving. Then, very slowly, it "
   "lifts its great head, opens its jaws, and breathes a long plume of fire straight up into the sky. It bursts like a firework over "
   "Bellwether. The whole village cheers. Gerald the sheep baas.\n\n\"ALIVE,\" says the dragon. \"OFFICIALLY.\" It sounds the word out "
   "like it tastes good. \"THANK YOU, SMALL ONE.\"\n\n\"THE BACK PAY: THIRTY-THREE GOLD, THREE SHEEP AND THREE APOLOGIES. A FORTUNE. TAKE "
   "SOME.\" A clawful of coins clatters at your feet. \"AND THIS.\"\n\nThe dragon breathes on you, gently. It is warm, not burning, "
   "and you feel something settle in your chest like an ember.\n\n\"DRAGON'S SIGH. WHEN THEY CROWD YOU: SIGH AT THEM.\"\n\nThen it pulls "
   "a single scale from its own chest, with a wince, and hands it over. \"A DRAGON'S SCALE. FIRE WILL REMEMBER YOU KINDLY.\"",
   [("Bow.", "root")], [{"type": "learn_spell", "spell_id": "core:spell.dragon_sigh"}, GI("cindermaw_scale"), {"type": "give_gold", "amount": 250},
                         SQ(100), SF("dragon_retired"), {"type": "give_xp", "skill": "persuasion", "amount": 80}])
dr("after",
   "\"RETIREMENT IS EXCELLENT. I HAVE A SHEEP. I HAVE A PENSION. THE CHILDREN OF THIS VILLAGE BRING ME BREAD AND I PRETEND TO BE "
   "FRIGHTENING.\"\n\nA pause.\n\n\"THE CLERK ASKED IF I WOULD LIKE TO FILL IN THE CENSUS EARLY. FOR THE NEXT THREE CENTURIES.\" Smoke curls "
   "from its nostrils. \"I SAID YES. HE CRIED. I THINK IT WAS HAPPINESS.\"",
   [('"Enjoy it, Cindermaw."', "root")])

# ------------------------------------------------------------------ Quillsby and the hearing
kq = new_dialogue("core:dialogue.kobold_quillsby", "dlg.dp.kq", "npc.kobold_quillsby.name")
kq("root",
   "In the Records Office's side room, a small green kobold in a beautifully tailored waistcoat sits on three cushions, writing in a "
   "ledger. Gold spectacles. A briefcase chained to one wrist. Oakhaven stands by the desk, holding Form 9-L like a sword.\n\n"
   "\"Grubnik Quillsby, Esquire. Hoard Executor to the late Cindermaw.\" He doesn't look up. \"The estate is to be transferred to me at "
   "noon. I have the paperwork. I have ALL the paperwork.\"\n\nOAKHAVEN: \"This is a formal hearing on the legal status of Cindermaw "
   "the Elder. Present your evidence.\"",
   [("Present the witnesses who've seen the dragon alive.", "p_wit", {"conditions": [W3, FN("dhear_w")], "actions": [SF("dhear_w")]}),
    ("Present the Register of Hatchings.", "p_rec", {"conditions": [FN("dhear_r")], "actions": [SF("dhear_r")]}),
    ("Present the likeness.", "p_lik", {"conditions": [FN("dhear_l")], "actions": [SF("dhear_l")]}),
    ("Ask about the missing third of the hoard. (Persuasion)", "confess",
     {"conditions": [FN("dragon_confession"), FN("dragon_denied")], "roll": {"skill": "persuasion", "dc": 13, "fail_next": "deny"}}),
    ("\"I rest my case.\"", "panic", {"conditions": [FS("dhear_w"), FS("dhear_r"), FS("dhear_l")]}),
    ("Step out for a moment.", "END")])
kq("p_wit",
   "You read out the witness statements. Marta saw the dragon eat a pie. Vaelen sold it a hat. Baggy investigated it from very close up "
   "and survived. Each one: 'definitely alive, regrettably large'.\n\nQUILLSBY (writing faster): \"Hearsay. Villagers. Easily confused. "
   "Probably saw a large red barn.\"",
   [("Continue.", "root")])
kq("p_rec",
   "You lay down the Register of Hatchings, Volume IX. Entry 4,211: 'One egg, red, enormous. Hatched. Very loud. Named Cindermaw.' "
   "And beneath it, nothing: no date of death. Dragons live for thousands of years.\n\nQUILLSBY (adjusting his spectacles): \"A "
   "clerical oversight. Records are often incomplete. Much like the dragon. Who is dead.\"",
   [("Continue.", "root")])
kq("p_lik",
   "You slide the likeness across the desk: the dragon in Bellwether's square this very morning, mid-sneeze, reading spectacles on one "
   "claw. The date is etched into the silver.\n\nQuillsby looks at it for a long time. A bead of sweat runs down his scaly forehead.\n\n"
   "QUILLSBY: \"...That could be ANY enormous red dragon with reading spectacles.\"",
   [("Continue.", "root")])
kq("confess",
   "\"The hoard was counted,\" you say, \"in the treaty of Ashfall. Eleven thousand gold. Your inventory says seven thousand. Where is "
   "the rest?\"\n\nQuillsby's pen stops. His tail twitches. He looks at Oakhaven. Oakhaven looks back, perfectly still, like a clerk who "
   "has been waiting three hundred years for exactly this moment.\n\nQUILLSBY (very small): \"...Investments.\"\n\nOAKHAVEN: \"Noted.\"",
   [("Continue.", "root")], [SF("dragon_confession")])
kq("deny", "QUILLSBY: \"I have no idea what you're talking about. The inventory is perfect. I am perfect. Next question.\"", [("Continue.", "root")],
   [SF("dragon_denied")])
kq("panic",
   "OAKHAVEN (rising, holding up Form 9-L): \"On the evidence presented, this hearing finds that Cindermaw the Elder is ALIVE. The death "
   "notice is void. The estate is NOT to be transferred. And Mr Quillsby...\"\n\nQuillsby is already on his feet on his cushions. He "
   "snaps open the briefcase. Inside, curled up like a sleeping cat, is a tiny iron figure covered in seals and stamps.\n\n"
   "QUILLSBY: \"If the courts won't give me what I'm owed, I'll REPOSSESS it!\" He hurls the figure out of the window. It hits the square "
   "and starts to grow.\n\nOutside, something enormous and iron stands up, stamped all over with the word REPOSSESSED.\n\nWhen you look "
   "back, Quillsby is gone. So are the cushions.",
   [("Get out to the square!", "END")], [SF("dragon_golem"), SQ(40)])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ witnesses, the record, the box (topics on existing NPCs)
D = load("content/dialogue/chapter_zero_dialogue.json"); DL = {d["id"]: d for d in D["dialogues"]}
wit = lambda f: [QE(20), FN(f)]
add_topics("core:dialogue.innkeeper_marta", "dlg.dp.marta", "npc.innkeeper_marta.name", [
    ('"Have you seen the dragon? Alive, I mean. Officially."', "dp_wit", wit("dwit_marta"),
     "\"Seen it? It ate a whole pie off my window ledge this morning. Blueberry. Then it said THANK YOU, very loudly, and the windows broke.\" "
     "She signs your list with a flourish. \"Alive. Definitely alive. Owes me for a pie.\"", [SF("dwit_marta")], '"Thank you, Marta."')])
add_topics("core:dialogue.merchant_vaelen", "dlg.dp.vaelen", "npc.merchant_vaelen.name", [
    ('"Will you witness that the dragon is alive?"', "dp_wit", wit("dwit_vaelen"),
     "\"Alive? I sold it a hat. A very large hat. Well, a tablecloth with a hole in it. It said it was the finest hat it had ever "
     "owned.\" Vaelen signs. \"Alive, and a satisfied customer. The second one this year.\"", [SF("dwit_vaelen")], '"Thanks, Vaelen."')])
add_topics("core:dialogue.detective_baggy", "dlg.dp.baggy", "npc.detective_baggy.name", [
    ('"Would you witness that the dragon is alive?"', "dp_wit", wit("dwit_baggy"),
     "\"I investigated it! From very close up. I checked for a pulse.\" Baggy shows you a slightly scorched magnifying glass. \"It has a "
     "pulse. It's very loud. It also has opinions about detectives.\" Baggy signs. \"Alive. Case closed. Eyebrows regrowing.\"",
     [SF("dwit_baggy")], '"Thanks, Baggy."')])
add_topics("core:dialogue.hunter_hollis", "dlg.dp.hollis", "npc.hunter_hollis.name", [
    ('"You\'re a monster hunter. Is the dragon alive?"', "dp_wit", wit("dwit_hollis"),
     "Hollis doesn't look up from the cards. \"Old red. Nine centuries, give or take. Breathing, warm, hasn't hurt anyone, ate a pie. "
     "Not a contract.\" Signs without looking. \"Alive. Leave it be.\"", [SF("dwit_hollis")], '"Thanks, Hollis."')])
add_topics("core:dialogue.witch_sabrino", "dlg.dp.sabrino", "npc.witch_sabrino.name", [
    ('"Will you witness the dragon is alive?"', "dp_wit", wit("dwit_sabrino"),
     "\"Alive? We had TEA. It told me my fireball technique was 'adorable'.\" Sabrino signs with a flourish that sets the corner of the "
     "page on fire, then pats it out. \"Alive. And rude. I liked it enormously.\"", [SF("dwit_sabrino")], '"Thanks, Sabrino."')])
add_topics("core:dialogue.steve", "dlg.dp.steve", "npc.steve.name", [
    ('"Steve, will you witness that the dragon is alive?"', "dp_wit", wit("dwit_steve"),
     "\"I tried to rob it.\" Steve looks proud. \"It laughed so hard it fell over. Then it gave me a gold coin for 'effort'. Best day of "
     "my career.\" He signs: STEVE (BANDIT). \"Alive. Generous. Ten out of ten, would rob again.\"", [SF("dwit_steve")], '"Thanks, Steve."')])
add_topics("core:dialogue.grout", "dlg.dp.grout", "npc.grout.name", [
    ('"Grout, will you witness the dragon is alive?"', "dp_wit", wit("dwit_grout"),
     "\"It sat on my roof. For an hour.\"\n\nA long pause.\n\n\"Roof's fine.\" Grout signs with one stone fingertip, carving it into the "
     "paper. \"Alive.\"", [SF("dwit_grout")], '"Thanks, Grout."')])
add_topics("core:dialogue.librarian_fenwick", "dlg.dp.fen", "npc.librarian_fenwick.name", [
    ('"Do you have the Register of Hatchings? For the dragon."', "dp_rec", [QE(20), {"type": "item_not_held", "item_id": I("hatching_record")}],
     "Fenwick goes pale, then disappears into the stacks, and comes back twenty minutes later covered in dust, holding an enormous book "
     "with a scorch mark on the spine.\n\n\"The Register of Hatchings, Volume Nine. Entry four thousand two hundred and eleven.\" He "
     "hugs it. \"Last borrowed... three hundred and twelve years ago. By a kobold. Returned four days late.\" His eye twitches. \"I "
     "remember the fine.\"\n\nHe hands it over. \"Bring it BACK.\"", [GI("hatching_record")], '"I promise."')])
add_topics("core:dialogue.professor_pickering", "dlg.dp.pick", "npc.professor_pickering.name", [
    ('"I need a likeness of a dragon. Today."', "dp_box", [QE(20), {"type": "item_not_held", "item_id": I("likeness_box")},
                                                           {"type": "item_not_held", "item_id": I("dragon_likeness")}],
     "The Professor's eyes light up. \"A likeness! Of a DRAGON! Oh, I've waited my whole career to say this.\" He hauls a wooden box on "
     "legs out from under a desk: brass lens, black cloth, a lot of handles.\n\n\"The Pickering Patent Likeness Engine. Point, duck under "
     "the cloth, shout 'hold still', pull the lever. It captures the exact light of a moment on a silver plate.\" He beams. \"It has only "
     "exploded twice.\"", [GI("likeness_box")], '"Thank you, Professor."')])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ NPCs, creature, items, spell, quest, campaign
N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.dragon_cindermaw", "name_key": DRAGON, "title_key": "npc.dragon_cindermaw.title", "faction": "core:faction.ashbound",
                  "dialogue_id": "core:dialogue.dragon_cindermaw",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/dragon_cindermaw.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 4.2},
                  "barks": [{"text_key": "bark.dragon.1"}, {"text_key": "bark.dragon.2"}, {"text_key": "bark.dragon.3", "flag": "dragon_retired"}]})
N["npcs"].append({"id": "core:npc.kobold_quillsby", "name_key": "npc.kobold_quillsby.name", "title_key": "npc.kobold_quillsby.title",
                  "faction": "core:faction.ashbound", "dialogue_id": "core:dialogue.kobold_quillsby",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/kobold_quillsby.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 1.25}, "barks": []})
save("content/npcs/core_npcs.json", N)
S.update({DRAGON: "Cindermaw the Elder", "npc.dragon_cindermaw.title": "Dragon (Legally Deceased, Allegedly)",
          "npc.kobold_quillsby.name": "Grubnik Quillsby, Esq.", "npc.kobold_quillsby.title": "Hoard Executor",
          "bark.dragon.1": "I AM NOT DEAD. I AM RIGHT HERE. LOOK AT ME. I AM ENORMOUS.",
          "bark.dragon.2": "(The dragon sighs. A nearby hay bale catches fire. Someone puts it out, apologising.)",
          "bark.dragon.3": "ALIVE. OFFICIALLY. (The dragon says it like it tastes good.)"})
CR = load("content/creatures/core_creatures.json")
CR["creatures"].append({"id": "core:enemy.repossession_golem", "name_key": "enemy.repossession_golem.name",
    "appearance": {"type": "model_glb", "model": "assets/models/characters/lost_sentinel.glb", "scale": 1.3},
    "stats": {"health": 300, "armor": 8, "move_speed": 1.9, "xp_reward": 120}, "behavior": "melee_patroller", "family": "construct",
    "perception": {"sight_meters": 14.0, "hearing_meters": 10.0},
    "attack": {"name": "repossess", "damage": 16, "reach_meters": 2.3, "windup_seconds": 0.8, "cooldown_seconds": 1.7},
    "loot_table": "core:loot.repossession_golem",
    "audio": {"alert": "assets/audio/sfx/sentinel_clang.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav", "death": "assets/audio/sfx/enemy_death.wav"},
    "hit_fx": {"color": [200, 190, 160], "glow": False}, "lines": {"alert": "line.golem.alert", "death": "line.golem.death"}})
save("content/creatures/core_creatures.json", CR)
S.update({"enemy.repossession_golem.name": "The Repossession Golem", "line.golem.alert": "ASSETS. WILL. BE. RECOVERED. PLEASE. REMAIN. CALM.",
          "line.golem.death": "FORM... INCOMPLETE..."})
L = load("content/loot_tables/core_loot.json")
L["loot_tables"].append({"id": "core:loot.repossession_golem", "gold_min": 60, "gold_max": 100, "guaranteed": [I("quillsby_ledger")],
                         "entries": [{"item_id": I("iron_scrap"), "weight": 100, "min_qty": 3, "max_qty": 5}, {"item_id": I("health_potion"), "weight": 60, "min_qty": 1, "max_qty": 2}]})
save("content/loot_tables/core_loot.json", L)

CB = load("content/items/consumables_and_books.json"); A = load("content/items/armor_and_gear.json")
def item(n, name, desc, cat, icon, model, value, **kw):
    d = {"id": I(n), "name_key": f"item.{n}.name", "description_key": f"item.{n}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": f"assets/models/items/{model}.glb", "slots": kw.pop("slots", []), "value": value, "weight": kw.pop("weight", 0.3)}
    d.update(kw)
    S[f"item.{n}.name"] = name; S[f"item.{n}.description"] = desc
    return d
CB["items"] += [
    item("hatching_record", "Register of Hatchings, Vol. IX", "Entry 4,211: one egg, red, enormous. Hatched. Very loud. Named Cindermaw. No date of death. Fenwick wants it BACK.", "misc", "hatching_record", "spell_tome", 0, weight=2.0),
    item("likeness_box", "Pickering Patent Likeness Engine", "A wooden box on legs with a brass lens and a black cloth. Point it at a dragon, shout 'hold still', pull the lever. Has only exploded twice.", "misc", "likeness_box", "wooden_crate", 0, weight=3.0),
    item("dragon_likeness", "Likeness of Cindermaw", "A silver plate: the dragon in Bellwether's square, reading spectacles on one claw, mid-sneeze. Accurate. Tell no one.", "misc", "dragon_likeness", "form_27b_scroll", 0),
    item("quillsby_ledger", "Quillsby's Second Ledger", "The real accounts. Eleven thousand gold in, seven thousand declared, and a column headed 'INVESTMENTS (SHOES)'.", "book", "quillsby_ledger", "spell_tome", 25,
         book_text_key="book.quillsby_ledger.text"),
]
S["book.quillsby_ledger.text"] = ("QUILLSBY'S SECOND LEDGER (PRIVATE. VERY PRIVATE.)\n\nHoard as counted, Treaty of Ashfall: 11,000 gold.\nHoard as declared: 7,000 gold.\n"
                                  "Difference: 'Investments'.\n\nInvestments:\n - Shoes (kobold, bespoke, 300 pairs)\n - Cushions (silk, 1,200)\n - Waistcoats (many)\n"
                                  " - One (1) Repossession Golem, 'for emergencies'\n - A small house by the sea, named 'The Late Cindermaw'\n\n"
                                  "Note to self: file the death notice the MOMENT the census letter goes unanswered. Dragons sleep for centuries. Nobody will notice.")
A["items"].append(item("cindermaw_scale", "Cindermaw's Scale", "Pulled from the dragon's own chest, with a wince. Warm to the touch, always. Fire burns hotter for you, fire hurts you less, and your spells hit harder.",
                       "accessory", "cindermaw_scale", "signet_ring", 400, slots=["accessory"], weight=0.2,
                       effects=[{"type": "bonus", "stat": "burn_damage_bonus", "value": 0.35}, {"type": "bonus", "stat": "armor_bonus", "value": 2.0},
                                {"type": "bonus", "stat": "spell_power_bonus", "value": 0.1}, {"type": "bonus", "stat": "status_duration_bonus", "value": 0.15}]))
save("content/items/consumables_and_books.json", CB); save("content/items/armor_and_gear.json", A)
SPL = load("content/spells/core_spells.json")
SPL["spells"].append({"id": "core:spell.dragon_sigh", "name_key": "spell.dragon_sigh.name", "description_key": "spell.dragon_sigh.desc",
                      "icon": "assets/ui/spells/dragon_sigh.png", "skill": "elemental", "mana_cost": 26, "cooldown_seconds": 3.0,
                      "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                      "effect": {"primitive": "nova", "damage_type": "fire", "base_power": 16, "radius": 5.0, "status": "burn", "status_duration": 5.0,
                                 "light_color": [1.0, 0.55, 0.2], "light_radius": 7.0}})
save("content/spells/core_spells.json", SPL)
S["spell.dragon_sigh.name"] = "Dragon's Sigh"
S["spell.dragon_sigh.desc"] = "Cindermaw's gift: sigh, and a ring of dragonfire rolls out around you, burning everything within five metres. 'WHEN THEY CROWD YOU: SIGH AT THEM.'"

QQ = load("content/quests/chapter_zero_quests.json")
QQ["campaigns"].append({"id": "dragon_pension", "name_key": "campaign.dragon.name", "desc_key": "campaign.dragon.desc", "kind": "tales", "order": 34})
S["campaign.dragon.name"] = "The Dragon's Pension"
S["campaign.dragon.desc"] = "A nine-hundred-year-old dragon slept through three centuries of census letters and was declared legally deceased. It would like a word."
QQ["quests"].append({"id": Q, "title_key": "quest.dp.title", "summary_key": "quest.dp.summary", "campaign": "dragon_pension", "stages": [
    {"stage": 0, "objective_key": "quest.dp.stage0", "journal_key": "quest.dp.journal0", "markers": ["npc_oakhaven"]},
    {"stage": 10, "objective_key": "quest.dp.stage10", "journal_key": "quest.dp.journal10", "markers": ["npc_dragon_cindermaw"]},
    {"stage": 20, "objective_key": "quest.dp.stage20", "journal_key": "quest.dp.journal20", "markers": ["npc_fenwick", "npc_pickering", "npc_dragon_cindermaw", "npc_oakhaven"]},
    {"stage": 30, "objective_key": "quest.dp.stage30", "journal_key": "quest.dp.journal30", "markers": ["npc_kobold_quillsby"]},
    {"stage": 40, "objective_key": "quest.dp.stage40", "journal_key": "quest.dp.journal40", "markers": ["dp_golem"]},
    {"stage": 50, "objective_key": "quest.dp.stage50", "journal_key": "quest.dp.journal50", "markers": ["npc_dragon_cindermaw"]},
    {"stage": 100, "objective_key": "quest.dp.stage100", "journal_key": "quest.dp.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.dp.title": "The Dragon's Pension", "quest.dp.summary": "Cindermaw the Elder is not dead. Cindermaw was asleep. The Bureau disagrees.",
    "quest.dp.stage0": "Ask Clerk Oakhaven what's wrong.", "quest.dp.journal0": "Oakhaven looks worried.",
    "quest.dp.stage10": "Talk to the dragon in Bellwether's square.",
    "quest.dp.journal10": "A dragon has landed in the square. Its pension was cancelled when the Bureau declared it legally deceased. It was asleep.",
    "quest.dp.stage20": "Gather proof of life: three witnesses who've seen the dragon alive, the Register of Hatchings (Fenwick), and a likeness (Professor Pickering's box). Then see Oakhaven.",
    "quest.dp.journal20": "Form 9-L: Proof of Continued Existence, Non-Human, Large. Witnesses: Marta? Vaelen? Baggy? Hollis? Sabrino? Steve? Grout?",
    "quest.dp.stage30": "Win the hearing against Grubnik Quillsby in the Records Office side room.",
    "quest.dp.journal30": "The death notice was filed by the 'designated heir': Cindermaw's own hoard-keeper, a kobold, the day after the last letter went unanswered.",
    "quest.dp.stage40": "Stop the Repossession Golem in the square!",
    "quest.dp.journal40": "Quillsby lost the hearing and threw a golem out of the window. It is repossessing the square.",
    "quest.dp.stage50": "Tell Cindermaw the good news.", "quest.dp.journal50": "The golem is scrap. Quillsby fled. The dragon is officially alive.",
    "quest.dp.stage100": "Completed: one dragon, officially alive.",
    "quest.dp.journal100": "Back pay: thirty-three gold, three sheep and three apologies. I got Dragon's Sigh and one of Cindermaw's scales.",
    "tip.45": "If a dragon asks you to speak up, speak up. It's nine hundred years old.",
})

# ------------------------------------------------------------------ placement (Bellwether)
B = load("content/regions/bellwether.json")
B["npcs"].append({"instance_id": "npc_dragon_cindermaw", "npc_id": "core:npc.dragon_cindermaw", "pos": [5.2, 0.0, 4.6], "yaw": -100.0, "requires_flag": "dragon_arrived"})
B["npcs"].append({"instance_id": "npc_kobold_quillsby", "npc_id": "core:npc.kobold_quillsby", "pos": [-3.8, 0.0, -11.8], "yaw": -60.0,
                  "requires_flag": "dragon_hearing", "hidden_flag": "dragon_golem"})
B["creatures"].append({"instance_id": "dp_golem", "creature_id": "core:enemy.repossession_golem", "pos": [-3.5, 0.0, -4.5], "patrol_a": [-6.0, 0.0, -4.5],
                       "patrol_b": [-1.0, 0.0, -4.5], "requires_flag": "dragon_golem", "group": "dp_golem", "group_quest_id": Q, "group_set_stage": 50,
                       "group_set_flag": "dragon_golem_down"})
save("content/regions/bellwether.json", B)
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

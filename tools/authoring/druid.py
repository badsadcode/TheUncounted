"""'A Druid in Distress': Bramble Thistlewick, Druid of the Whistling Wood (Third Class), sneezed mid-shapeshift and has
been a squirrel for six weeks. Gather the reversal ingredients (an acorn from the Old Oak, a glowcap, a tuft of Rolf's
fur), read the incantation (a rigged roll: the first try turns him into a goose), and he teaches you Barkskin.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
Q = "core:quest.druid_distress"
I = lambda n: f"core:item.{n}"
QE = lambda s: {"type": "quest_stage_equals", "quest_id": Q, "stage": s}
QB = lambda s: {"type": "quest_stage_below", "quest_id": Q, "stage": s}
HI = lambda i: {"type": "has_item", "item_id": I(i)}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}

D = load("content/dialogue/chapter_zero_dialogue.json")
def new_dialogue(did, speaker, prefix):
    D["dialogues"].append({"id": did, "root_node": "root", "nodes": {}})
    nodes = D["dialogues"][-1]["nodes"]
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
        nodes[nid] = n
    return node

# ------------------------------------------------------------------ the squirrel
sq = new_dialogue("core:dialogue.druid_squirrel", "npc.druid_squirrel.name", "dlg.druid.sq")
sq("root",
   "A red squirrel is sitting on a root of the Old Oak, glaring at you with tremendous dignity. It is wearing a very small necklace "
   "of acorns.\n\nIt clears its throat.\n\n\"Oh, thank the Green, a person. Don't scream. Don't throw anything. I am a druid.\"",
   [('"A talking squirrel?"', "who", {"conditions": [QB(0)]}),
    ('"How do I turn you back?"', "task", {"conditions": [QB(10)]}),
    ('"Remind me what you need?"', "hint", {"conditions": [QE(10)]}),
    ('"I\'ve got the acorn, the glowcap and Rolf\'s fur."', "ritual",
     {"conditions": [QE(10), HI("oak_acorn"), HI("glowcap"), HI("rolf_fur")]}),
    ("Leave.", "END")])
sq("who",
   "\"Bramble Thistlewick. Druid of the Whistling Wood. Third Class.\" The squirrel puffs out its chest. \"Second Class pending an "
   "appeal.\"\n\n\"Six weeks ago I was performing the Rite of the Swift Grey Hare. Very advanced. Beautiful rite. And halfway through the "
   "final verse...\" The squirrel's whiskers droop. \"...I sneezed.\"\n\n\"Hay fever. A druid with hay fever. Do you know how humiliating "
   "that is? I live in a FOREST.\"",
   [('"So you\'re stuck."', "stuck")])
sq("stuck",
   "\"Stuck. Six weeks. I've buried four hundred nuts. I don't know why. I can't stop. I don't even LIKE nuts.\"\n\nA pause.\n\n\"I've "
   "been chased by an owlbear cub. Twice. It just wanted to play. I know that now. I did not know that then.\"",
   [('"How do I turn you back?"', "task")])
sq("task",
   "\"The Rite of Unbecoming. Three things.\" The squirrel counts on its claws.\n\n\"One: an acorn from the Old Oak itself. Right here. "
   "I'd fetch it, but every time I pick one up, I bury it.\"\n\n\"Two: a glowcap. Those glowing mushrooms in the wood. For the light of "
   "remembering.\"\n\n\"Three: a tuft of fur from someone who changes shape and changes back. A werewolf. There's a very nice one gardening "
   "at Hollowmere. Ask politely. Werewolves can be touchy about their fur.\"",
   [('"An acorn, a glowcap, werewolf fur. Got it."', "root", {"actions": [SQ(0), SQ(10), SF("druid_quest")]})])
sq("hint",
   "\"An acorn from the Old Oak. A glowcap from the wood. A tuft of Rolf's fur from Hollowmere.\" The squirrel buries something "
   "absent-mindedly as it talks, then looks horrified. \"Please hurry.\"",
   [('"On it."', "root")])
sq("ritual",
   "The squirrel sets out the acorn, the glowcap and the fur in a careful triangle on the root, and hands you a scrap of bark covered in "
   "tiny scratched words.\n\n\"You'll have to read the incantation. I can't. Every time I try, it comes out as chattering.\"\n\n"
   "The words look... difficult. Several of them are mostly consonants. One appears to be a sneeze.",
   [("Read the incantation. (Lore)", "restored", {"roll": {"skill": "lore", "dc": 11, "fail_next": "goose", "rigged": True}}),
    ('"Give me a minute."', "root")])
sq("goose",
   "You read the incantation. You get the third word wrong. There is a flash of green light, a smell of wet leaves, and a loud, furious "
   "\"HONK.\"\n\nWhere the squirrel was, there is now a goose. A large, white, extremely angry goose.\n\nThe goose looks at you. You look at "
   "the goose. The goose bites you on the knee.\n\nBramble (honking with remarkable clarity): \"THAT'S. NOT. IT. Again. AGAIN. Read it "
   "AGAIN. And it's 'frrrth-wyn', not 'frith-win'. Roll the R. Like a hedgehog.\"",
   [("Read the incantation again, rolling the R like a hedgehog. (Lore)", "restored", {"roll": {"skill": "lore", "dc": 9, "fail_next": "goose_again"}}),
    ("Apologise to the goose.", "goose_sorry")], [SF("druid_was_goose"), {"type": "sanity", "amount": -3}])
sq("goose_sorry", "Bramble (as a goose): \"Apology accepted. Partially. Read it again.\"", [("Read it again. (Lore)", "restored", {"roll": {"skill": "lore", "dc": 9, "fail_next": "goose_again"}})])
sq("goose_again",
   "Another flash. The goose becomes, briefly, a very surprised turnip, then a goose again.\n\nBramble: \"...HONK. Once more. With "
   "FEELING.\"",
   [("Read it once more, with feeling. (Lore)", "restored", {"roll": {"skill": "lore", "dc": 6, "fail_next": "goose_again"}})])
sq("restored",
   "The words come out right. Green light swirls up from the triangle of acorn, glowcap and fur, and spins, and spins, and with a sound "
   "like a cork leaving a bottle...\n\n...a tall, bearded man in a mossy green robe is sitting on the root of the Old Oak, blinking. He has "
   "small antlers. He did not have antlers before. He feels them, carefully.\n\n\"...Close enough.\"",
   [("Help him up.", "END")], [SF("druid_restored"), SQ(50), {"type": "take_item", "item_id": I("oak_acorn"), "qty": 1},
                                {"type": "take_item", "item_id": I("glowcap"), "qty": 1}, {"type": "take_item", "item_id": I("rolf_fur"), "qty": 1},
                                {"type": "give_xp", "skill": "lore", "amount": 40}])
save_needed = True

# ------------------------------------------------------------------ the druid, restored
dr = new_dialogue("core:dialogue.druid_bramble", "npc.druid_bramble.name", "dlg.druid.dr")
dr("root",
   "Bramble Thistlewick, Druid of the Whistling Wood (Third Class), is standing very carefully on two legs, like someone who has only "
   "just remembered how. Every so often his hand drifts towards an acorn on the ground. He stops it.\n\n\"My friend! My saviour! My "
   "reader of difficult consonants!\"",
   [('"How do you feel?"', "feel", {"conditions": [QE(50)]}),
    ('"About the antlers..."', "antlers"),
    ('"Teach me some druid magic?"', "teach", {"conditions": [QE(50)]}),
    ('"Any more shapeshifting planned?"', "later", {"conditions": [{"type": "quest_stage_at_least", "quest_id": Q, "stage": 100}]}),
    ("Leave.", "END")])
dr("feel",
   "\"Tall. Very tall. Everything is so far down.\" He sneezes. A small shower of leaves falls out of his beard. \"And still allergic. The "
   "Green has a sense of humour.\"\n\n\"I want you to know I remember all of it. The nuts. The owlbear. Being a goose.\" He shudders. \"I bit "
   "you. I'm sorry I bit you. I'm not sorry I honked. It felt right.\"",
   [('"Glad you\'re back."', "root")])
dr("antlers",
   "\"Ah. Yes.\" He touches them. \"A small side effect. The rite takes a little of every shape you've been, and I have been, recently, a "
   "squirrel, a goose and briefly a turnip.\"\n\nHe lowers his voice. \"The turnip part is somewhere. I haven't found it yet.\"",
   [('"...Right."', "root")])
dr("teach",
   "\"Of course! A druid always repays a debt.\" He presses his palm to your forearm. It goes rough and brown and hard as oak for a moment, "
   "then fades.\n\n\"Barkskin. Call on it and your skin becomes bark: blades skid off, claws find nothing to hold. It doesn't last, nothing "
   "good does, but it's long enough to win an argument with a wolf.\"\n\nHe also hands you a small, fluffy, slightly embarrassing object.\n\n"
   "\"And this. When the rite finished, it was... left over. I think it's mine. I don't want it. It's lucky. Probably.\"\n\nIt's a squirrel tail.",
   [('"Thank you, Bramble."', "root")],
   [{"type": "learn_spell", "spell_id": "core:spell.barkskin"}, {"type": "give_item", "item_id": I("squirrel_tail"), "qty": 1},
    {"type": "give_gold", "amount": 60}, SQ(100)])
dr("later",
   "\"Never again.\" He sneezes. A small acorn falls out of his sleeve. He looks at it for a long moment, then, very deliberately, does not "
   "bury it.\n\n\"Progress.\"",
   [('"Progress."', "root")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ Rolf's fur
D = load("content/dialogue/chapter_zero_dialogue.json")
rolf = [d for d in D["dialogues"] if d["id"] == "core:dialogue.werewolf_rolf"][0]
rc = rolf["nodes"]["root"]["choices"]
end = next(i for i, c in enumerate(rc) if c["next"] == "END")
S["dlg.druid.rolf.choice"] = '"Could I have a tuft of your fur? It\'s for a druid. Who is a squirrel."'
rc.insert(end, {"text_key": "dlg.druid.rolf.choice", "next": "druid_fur",
                "conditions": [QE(10), {"type": "item_not_held", "item_id": I("rolf_fur")}]})
S["dlg.druid.rolf.fur"] = ("Rolf blinks his enormous golden eyes.\n\n\"A druid. Who is a squirrel.\" He thinks about this for a long time. \"Is it "
                           "Bramble? It's Bramble, isn't it. He sneezed, didn't he.\"\n\nHe turns round, very carefully pulls a soft tuft from between "
                           "his shoulder blades, and hands it to you.\n\n\"Take it from the back. The front is for show.\" A pause. \"Tell him to try "
                           "nettle tea for the hay fever.\"")
S["dlg.druid.rolf.fur.c0"] = '"Thanks, Rolf."'
rolf["nodes"]["druid_fur"] = {"speaker_key": "npc.werewolf_rolf.name", "text_key": "dlg.druid.rolf.fur",
                              "actions": [{"type": "give_item", "item_id": I("rolf_fur"), "qty": 1}],
                              "choices": [{"text_key": "dlg.druid.rolf.fur.c0", "next": "root"}]}
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ NPCs, items, spell, quest
N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.druid_squirrel", "name_key": "npc.druid_squirrel.name", "title_key": "npc.druid_squirrel.title",
                  "faction": "core:faction.ashbound", "dialogue_id": "core:dialogue.druid_squirrel",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/druid_squirrel.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 0.75},
                  "barks": [{"text_key": "bark.druid.sq.1"}, {"text_key": "bark.druid.sq.2"}]})
N["npcs"].append({"id": "core:npc.druid_bramble", "name_key": "npc.druid_bramble.name", "title_key": "npc.druid_bramble.title",
                  "faction": "core:faction.ashbound", "dialogue_id": "core:dialogue.druid_bramble",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/druid_bramble.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 1.82},
                  "barks": [{"text_key": "bark.druid.dr.1"}]})
save("content/npcs/core_npcs.json", N)
S.update({"npc.druid_squirrel.name": "A Squirrel (Dignified)", "npc.druid_squirrel.title": "Allegedly a Druid",
          "npc.druid_bramble.name": "Bramble Thistlewick", "npc.druid_bramble.title": "Druid of the Whistling Wood (Third Class)",
          "bark.druid.sq.1": "Psst. You. Yes, you. I'm a druid. Don't laugh.", "bark.druid.sq.2": "(The squirrel buries an acorn, then looks horrified at itself.)",
          "bark.druid.dr.1": "Achoo! ...Sorry. Leaves. Everywhere. Always leaves."})

CB = load("content/items/consumables_and_books.json"); A = load("content/items/armor_and_gear.json")
def item(n, name, desc, cat, icon, model, value, **kw):
    d = {"id": I(n), "name_key": f"item.{n}.name", "description_key": f"item.{n}.description", "category": cat,
         "icon": f"assets/ui/items/{icon}.png", "world_model": f"assets/models/items/{model}.glb", "slots": kw.pop("slots", []), "value": value, "weight": 0.1}
    d.update(kw)
    S[f"item.{n}.name"] = name; S[f"item.{n}.description"] = desc
    return d
CB["items"].append(item("oak_acorn", "Acorn of the Old Oak", "A fat, glossy acorn from the Old Oak. You feel a strange urge to bury it. Don't.", "misc", "oak_acorn", "bread_loaf", 5, stackable=True))
CB["items"].append(item("rolf_fur", "Tuft of Rolf's Fur", "Soft, warm, and from the back (the front is for show). Smells faintly of marrows.", "misc", "rolf_fur", "bread_loaf", 5, stackable=True))
A["items"].append(item("squirrel_tail", "Bramble's Spare Squirrel Tail", "Left over from the Rite of Unbecoming. Probably lucky. Worn on a belt, it makes you quicker on your feet and you recover your breath faster. You keep wanting to bury things.",
                       "accessory", "squirrel_tail", "leather_jerkin", 120, slots=["accessory"],
                       effects=[{"type": "bonus", "stat": "move_speed_bonus", "value": 0.08}, {"type": "bonus", "stat": "stamina_regen", "value": 2.0},
                                {"type": "bonus", "stat": "gold_find_bonus", "value": 0.1}]))
save("content/items/consumables_and_books.json", CB); save("content/items/armor_and_gear.json", A)

SPL = load("content/spells/core_spells.json")
SPL["spells"].append({"id": "core:spell.barkskin", "name_key": "spell.barkskin.name", "description_key": "spell.barkskin.desc",
                      "icon": "assets/ui/spells/barkskin.png", "skill": "restoration", "mana_cost": 18, "cooldown_seconds": 2.0,
                      "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                      "effect": {"primitive": "buff_stat", "bonus_key": "armor_bonus", "bonus_value": 8.0, "duration_seconds": 40.0,
                                 "light_color": [0.4, 0.8, 0.3], "light_radius": 3.0}})
save("content/spells/core_spells.json", SPL)
S["spell.barkskin.name"] = "Barkskin"
S["spell.barkskin.desc"] = "Bramble Thistlewick's thanks: your skin turns to oak bark for 40 seconds (+8 armour). Blades skid off. Hay fever not included."

QQ = load("content/quests/chapter_zero_quests.json")
QQ["quests"].append({"id": Q, "title_key": "quest.druid.title", "summary_key": "quest.druid.summary", "campaign": "tales_of_bellwether", "stages": [
    {"stage": 0, "objective_key": "quest.druid.stage0", "journal_key": "quest.druid.journal0", "markers": ["npc_druid_squirrel"]},
    {"stage": 10, "objective_key": "quest.druid.stage10", "journal_key": "quest.druid.journal10", "markers": ["druid_acorn", "npc_rolf", "npc_druid_squirrel"]},
    {"stage": 50, "objective_key": "quest.druid.stage50", "journal_key": "quest.druid.journal50", "markers": ["npc_druid_bramble"]},
    {"stage": 100, "objective_key": "quest.druid.stage100", "journal_key": "quest.druid.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.druid.title": "A Druid in Distress", "quest.druid.summary": "A squirrel by the Old Oak claims to be a druid. A druid with hay fever.",
    "quest.druid.stage0": "Talk to the dignified squirrel by the Old Oak.", "quest.druid.journal0": "A squirrel wants a word.",
    "quest.druid.stage10": "Bring the squirrel an acorn from the Old Oak, a glowcap, and a tuft of Rolf's fur (Hollowmere).",
    "quest.druid.journal10": "Bramble Thistlewick, Druid (Third Class), sneezed mid-shapeshift six weeks ago. He has buried four hundred nuts.",
    "quest.druid.stage50": "Talk to Bramble, now he's a person again (mostly).",
    "quest.druid.journal50": "I read the incantation. He was a goose for a bit. Then a turnip. Then himself, with antlers.",
    "quest.druid.stage100": "Completed: one druid, restored (antlers extra).",
    "quest.druid.journal100": "Bramble taught me Barkskin and gave me his spare squirrel tail. It's probably lucky.",
    "tip.44": "If a squirrel in the Whistling Wood asks for help, roll the R like a hedgehog.",
})

# ------------------------------------------------------------------ placement (Whistling Wood, near the Old Oak)
block = ("# ============================================================================ A Druid in Distress (tools/authoring/druid.py)\n"
         "npcs.append({\"instance_id\": \"npc_druid_squirrel\", \"npc_id\": \"core:npc.druid_squirrel\", \"pos\": [-11.6, 0.0, 4.2], \"yaw\": 200.0, "
         "\"hidden_flag\": \"druid_restored\"})\n"
         "npcs.append({\"instance_id\": \"npc_druid_bramble\", \"npc_id\": \"core:npc.druid_bramble\", \"pos\": [-11.4, 0.0, 3.8], \"yaw\": 200.0, "
         "\"requires_flag\": \"druid_restored\"})\n"
         "interactables.append({\"instance_id\": \"druid_acorn\", \"type\": \"pickup\", \"item_id\": \"core:item.oak_acorn\", \"qty\": 1, "
         "\"pos\": [-12.8, 0.15, 5.0], \"requires_flag\": \"druid_quest\"})\n\n")
src = open("tools/build_wood.py").read()
assert "region = {" in src
open("tools/build_wood.py", "w").write(src.replace("region = {", block + "region = {", 1))
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

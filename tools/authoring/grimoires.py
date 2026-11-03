"""Overdue: The Restricted Section. Fenwick's six missing grimoires, the borrowers who have them, six new spells
that use the status-effect system, status gear at Vaelen's, and a new synergy.

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
Q = "core:quest.overdue"
FS = lambda f: {"type": "flag_set", "flag": f}
FN = lambda f: {"type": "flag_not_set", "flag": f}
QA = lambda s: {"type": "quest_stage_at_least", "quest_id": Q, "stage": s}
QB = lambda s: {"type": "quest_stage_below", "quest_id": Q, "stage": s}
HAS = lambda i: {"type": "has_item", "item_id": i}
FL = lambda fl, v: {"type": "flags_at_least", "flags": fl, "value": v}
SF = lambda f: {"type": "set_flag", "flag": f, "value": True}
XP = lambda k, a: {"type": "give_xp", "skill": k, "amount": a}
GI = lambda i, q=1: {"type": "give_item", "item_id": i, "qty": q}
TI = lambda i, q=1: {"type": "take_item", "item_id": i, "qty": q}
GG = lambda a: {"type": "give_gold", "amount": a}
SQ = lambda s: {"type": "set_quest_stage", "quest_id": Q, "stage": s}
LS = lambda sp: {"type": "learn_spell", "spell_id": sp}


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


def C(text, nxt, cond=None, actions=None, roll=None):
    o = {}
    if cond: o["conditions"] = cond
    if actions: o["actions"] = actions
    if roll: o["roll"] = roll
    return (text, nxt, o)


def topics(nodes, root, items):
    ch = nodes[root]["choices"]
    idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
    new = []
    for key, text, cond, nxt in items:
        S[key] = text
        d = {"text_key": key, "next": nxt}
        if cond: d["conditions"] = cond
        new.append(d)
    nodes[root]["choices"] = ch[:idx] + new + ch[idx:]


# ======================================================================= spells
SP = load("content/spells/core_spells.json")
for s in SP["spells"]:  # existing spells learn the new status system
    e = s["effect"]
    if s["id"] == "core:spell.ember_bolt": e.update(status="burn", status_power=4, status_duration=3.0, status_chance=0.35)
    if s["id"] == "core:spell.frost_lance": e.update(status="chill", status_duration=3.5, status_chance=1.0)
    if s["id"] == "core:spell.sabrino_fireball": e.update(status="burn", status_power=5, status_duration=4.0, status_chance=1.0)
    if s["id"] == "core:spell.siphon_ink": e.update(status="ink", status_duration=3.0, status_chance=0.5)
NEW = [
    ("cold_shoulder", "Cold Shoulder", "elemental", 18, 1.6, {"primitive": "nova", "damage_type": "frost", "base_power": 10, "radius": 4.5,
        "status": "chill", "status_duration": 4.0, "light_color": [0.55, 0.8, 1.0], "light_radius": 6.0},
     "A ring of brittle, disapproving frost bursts out from you. Everyone nearby is chilled (slowed). Chill anything three times and it freezes solid. Set fire to something frozen and it SHATTERS."),
    ("chain_of_command", "Chain of Command", "elemental", 16, 1.1, {"primitive": "chain", "damage_type": "shock", "base_power": 16, "chain_count": 3,
        "chain_range": 14.0, "status": "shock", "status_duration": 4.0, "light_color": [1.0, 0.95, 0.55], "light_radius": 6.0},
     "Lightning passed down the line: it hits the nearest foe in front of you, then jumps to three more, each jump a little weaker. Shocked foes take 25% more damage from everything. Shock something that's on fire and it OVERLOADS."),
    ("standing_ovation", "Standing Ovation", "illusion", 22, 2.4, {"primitive": "nova", "damage_type": "shock", "base_power": 14, "radius": 5.0,
        "status": "shock", "status_duration": 5.0, "light_color": [1.0, 0.85, 0.5], "light_radius": 7.0},
     "Thunderous applause from nowhere. Everything near you is staggered and shocked. Odette says it's the only spell that has ever made a critic leave early."),
    ("slow_burn", "Slow Burn", "elemental", 12, 0.9, {"primitive": "projectile_damage", "damage_type": "fire", "base_power": 7, "projectile_speed": 15.0,
        "projectile_sprite": "assets/sprites/vfx/spell_ember.png", "status": "burn", "status_power": 9, "status_duration": 6.0,
        "light_color": [1.0, 0.5, 0.15], "light_radius": 5.0},
     "A small, patient flame. Barely stings on impact, then burns for six seconds. Mother Brine used it to keep the chowder warm for eleven years."),
    ("redacted", "[REDACTED]", "illusion", 11, 1.0, {"primitive": "projectile_damage", "damage_type": "ink", "base_power": 9, "projectile_speed": 18.0,
        "projectile_sprite": "assets/sprites/vfx/spell_ink.png", "status": "ink", "status_duration": 6.0, "light_color": [0.3, 0.3, 0.45], "light_radius": 3.0},
     "A bar of perfect black blots out a target's eyes. Inked foes can barely see, lose track of you, and miss almost half their attacks. [The remainder of this description has been redacted.]"),
    ("clerical_error", "Clerical Error", "illusion", 10, 1.4, {"primitive": "blink", "blink_distance": 6.0, "light_color": [0.75, 0.6, 1.0], "light_radius": 4.0},
     "The universe briefly misfiles your position. You are six metres further forward than you were. (Never through walls: even the universe has rules.)"),
]
for sid, name, skill, cost, cd, eff, desc in NEW:
    SP["spells"].append({"id": f"core:spell.{sid}", "name_key": f"spell.{sid}.name", "description_key": f"spell.{sid}.desc",
                         "icon": f"assets/ui/spells/{sid}.png", "skill": skill, "mana_cost": cost, "cooldown_seconds": cd,
                         "cast_sfx": "assets/audio/sfx/spell_cast.wav", "effect": eff})
    S[f"spell.{sid}.name"] = name
    S[f"spell.{sid}.desc"] = desc
save("content/spells/core_spells.json", SP)

# ======================================================================= grimoire items
BOOKS = [
    ("grimoire_cold", "On Cold Shoulders", "cold_shoulder",
     "ON COLD SHOULDERS: A PRACTICAL GUIDE TO BROODING AT A DISTANCE\n\nChapter One: The Turn. Present the shoulder. Not the whole back; that is rude. The shoulder says: I am wounded, and you may not ask why.\n\nChapter Two: The Frost. Should the observer approach regardless, channel your disdain outward in a ring. It should sparkle. Everything sparkles, eventually.\n\nIn the margins, in elegant violet ink: \"so true\" ... \"SO true\" ... \"this is me\" ... \"she never understood this\" -A."),
    ("grimoire_chain", "Chain of Command: Lightning in the Workplace", "chain_of_command",
     "CHAIN OF COMMAND\nLightning in the Workplace\n\nA directive issued at the top must reach every desk. So it is with lightning. Strike the nearest subordinate; the charge will be passed down the line, losing a little conviction at each desk, until it reaches someone who simply does not care.\n\nPickering's pencilled notes: \"cf. tide-bell harmonics?? the bells passed the COUNT down the line the same way. must ask Fenwick for an extension. must ask Fenwick for an extension. must\""),
    ("grimoire_ovation", "The Standing Ovation (Advanced Theatrical Thaumaturgy)", "standing_ovation",
     "THE STANDING OVATION\nAdvanced Theatrical Thaumaturgy\n\nThe audience must be ROUSED. Not persuaded. Not charmed. ROUSED. Gather the room's anticipation into your hands and RELEASE it as applause so overwhelming that everyone within five paces is physically knocked back by your genius.\n\nWarning: do not cast during the quiet bit.\n\nOn the flyleaf, in magenta: \"Borrowed for research. Returning SOON. Darling. -O\" (dated nine years ago)"),
    ("grimoire_slow", "Slow Burn: Patience in Pyromancy", "slow_burn",
     "SLOW BURN: PATIENCE IN PYROMANCY\n\nThe impatient pyromancer throws the biggest fire they can. The patient one throws a small fire and waits. The small fire is still going when the impatient pyromancer is being rebuilt by a healer.\n\nThe book smells strongly of chowder. Every page has a ring where a hot pot was set down on it. Pencilled at the back: \"Low simmer = 3 pages of Chapter Two. Rolling boil = Chapter Four. DO NOT READ CHAPTER SIX NEAR THE STEW. -B\""),
    ("grimoire_redacted", "[REDACTED]: A Guide to Discreet Omission", "redacted",
     "[REDACTED]\nA Guide to Discreet Omission\n\nChapter One. ████ ███ ██████ ███ ███ ███████. ██ ███ ████, ████████.\n\nChapter Two. ███████████████████████████████████████████████████████.\n\nThe only unredacted line in the book, on the last page: \"Brother Aldous: Please return the hymn book's naughty verses when you've finished blacking them out. They're library property. -F\""),
    ("grimoire_clerical", "Spatial Misfiling and You", "clerical_error",
     "SPATIAL MISFILING AND YOU\n(Bureau Internal Circular 9-Q)\n\nShould an object (or clerk) be filed in the wrong place, the universe will, in a small number of cases, simply accept the new location as correct. This circular explains how to make that happen ON PURPOSE.\n\nStep one: fill in Form 9-Q in your head. Step two: believe it. Step three: you are now somewhere else.\n\nStamped in red across the cover: FILED UNDER Q. Underneath, in Oakhaven's neat hand: \"Q for 'Quite Lost'. Note to self: tell nobody.\""),
]
CI = load("content/items/consumables_and_books.json")
for iid, title, spell, text in BOOKS:
    CI["items"].append({"id": f"core:item.{iid}", "name_key": f"item.{iid}.name", "description_key": f"item.{iid}.description", "category": "book",
                        "icon": f"assets/ui/items/{iid}.png", "world_model": "assets/models/items/spell_tome.glb", "slots": [], "value": 0, "weight": 0.8,
                        "book_text_key": f"book.{iid}.text"})
    S[f"item.{iid}.name"] = title
    S[f"item.{iid}.description"] = f"A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy {NEW[[n[0] for n in NEW].index(spell)][1]} into your spellbook."
    S[f"book.{iid}.text"] = text + "\n\n[The spell inside is locked behind a library binding-charm. Fenwick can unlock it.]"
save("content/items/consumables_and_books.json", CI)

# ======================================================================= status gear (Vaelen) + reward
W = load("content/items/weapons.json")
W["items"].append({"id": "core:item.cinderglass_dagger", "name_key": "item.cinderglass_dagger.name", "description_key": "item.cinderglass_dagger.description",
                   "category": "weapon", "icon": "assets/ui/items/cinderglass_dagger.png", "world_model": "assets/models/items/steel_dagger.glb",
                   "slots": ["main_hand"], "value": 120, "weight": 1.0,
                   "weapon": {"kind": "melee", "skill": "daggers", "damage_type": "fire", "base_damage": 11, "attack_time_seconds": 0.36, "stamina_cost": 5,
                              "reach_meters": 1.7, "crit_chance": 0.12, "crit_mult": 1.8, "on_hit_status": "burn", "status_chance": 0.3,
                              "status_power": 5, "status_duration": 3.0}})
W["items"].append({"id": "core:item.rimecaller_mace", "name_key": "item.rimecaller_mace.name", "description_key": "item.rimecaller_mace.description",
                   "category": "weapon", "icon": "assets/ui/items/rimecaller_mace.png", "world_model": "assets/models/items/iron_mace.glb",
                   "slots": ["main_hand"], "value": 135, "weight": 3.4,
                   "weapon": {"kind": "melee", "skill": "swords", "damage_type": "frost", "base_damage": 16, "attack_time_seconds": 0.62, "stamina_cost": 10,
                              "reach_meters": 2.0, "on_hit_status": "chill", "status_chance": 0.4, "status_duration": 3.0}})
save("content/items/weapons.json", W)
A = load("content/items/armor_and_gear.json")
A["items"].append({"id": "core:item.storm_stamp", "name_key": "item.storm_stamp.name", "description_key": "item.storm_stamp.description", "category": "accessory",
                   "icon": "assets/ui/items/storm_stamp.png", "world_model": "assets/models/items/signet_ring.glb", "slots": ["accessory"], "value": 160, "weight": 0.3,
                   "armor": 0, "effects": [{"type": "bonus", "stat": "combo_damage_bonus", "value": 0.35}, {"type": "bonus", "stat": "status_chance_bonus", "value": 0.05}]})
A["items"].append({"id": "core:item.library_card", "name_key": "item.library_card.name", "description_key": "item.library_card.description", "category": "accessory",
                   "icon": "assets/ui/items/library_card.png", "world_model": "assets/models/items/spell_tome.glb", "slots": ["accessory"], "value": 300, "weight": 0.05,
                   "armor": 0, "effects": [{"type": "stat_bonus", "stat": "intellect", "amount": 1}, {"type": "bonus", "stat": "status_duration_bonus", "value": 0.3},
                                           {"type": "bonus", "stat": "spell_cost_reduction", "value": 0.06}]})
save("content/items/armor_and_gear.json", A)
S.update({
    "item.cinderglass_dagger.name": "Cinderglass Dagger",
    "item.cinderglass_dagger.description": "Volcanic glass, still warm. Sets things on fire, and keeps them that way. Pairs dangerously well with anything that chills.",
    "item.rimecaller_mace.name": "Rimecaller Mace",
    "item.rimecaller_mace.description": "A mace with a head of blue ice that never melts. Every few hits, the target slows. Three chills and it's a statue.",
    "item.storm_stamp.name": "The Storm-Clerk's Stamp",
    "item.storm_stamp.description": "A brass Bureau stamp that reads APPROVED in lightning. Shatters and Overloads hit 35% harder, and status effects land a little more often.",
    "item.library_card.name": "Fenwick's Library Card (Lifetime, Laminated)",
    "item.library_card.description": "Card number 0000001. There has never been a card 0000001 before. +1 Intellect, status effects last 30% longer, spells cost 6% less. All fines waived. All of them. Forever.",
})
N = load("content/npcs/core_npcs.json")
for n in N["npcs"]:
    if n["id"] == "core:npc.merchant_vaelen":
        n["vendor_inventory"] += [{"item_id": "core:item.cinderglass_dagger", "stock": 1, "price": 120},
                                  {"item_id": "core:item.rimecaller_mace", "stock": 1, "price": 135},
                                  {"item_id": "core:item.storm_stamp", "stock": 1, "price": 160}]
    if n["id"] == "core:npc.librarian_fenwick":
        n["barks"].append({"text_key": "bark.fenwick.overdue_done", "quest_id": Q, "min_stage": 100})
save("content/npcs/core_npcs.json", N)
S["bark.fenwick.overdue_done"] = "Six for six. The Restricted Section is complete. I may frame the returns ledger."

SY = load("content/synergies/synergies.json")
SY["synergies"].append({"id": "core:synergy.storm_clerk", "name_key": "synergy.storm_clerk.name", "description_key": "synergy.storm_clerk.desc",
                        "requirements": {"elemental": 14, "illusion": 8}, "bonuses": {"status_duration_bonus": 0.25, "combo_damage_bonus": 0.25}})
save("content/synergies/synergies.json", SY)
S["synergy.storm_clerk.name"] = "Thermal Paperwork"
S["synergy.storm_clerk.desc"] = "Elemental 14 + Illusion 8. You have learned to file fire, frost and lightning in the right order. Statuses last 25% longer; Shatter and Overload hit 25% harder."

# ======================================================================= dialogue
D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
fn = DL["core:dialogue.librarian_fenwick"]["nodes"]
f = Dlg("dlg.overdue.fenwick", fn, "npc.librarian_fenwick.name")
RETURNED = [f"ret_{b[0]}" for b in BOOKS]
topics(fn, "root", [
    ("dlg.overdue.t.start", '"Is anything else overdue, Fenwick?"', [QB(0)], "od_start"),
    ("dlg.overdue.t.return", '"I\'ve brought back some overdue books."', [QA(0), QB(100)], "od_return"),
    ("dlg.overdue.t.who", '"Remind me who has the books?"', [QA(0), QB(100)], "od_who"),
])
f.node("od_start",
    "Fenwick goes very still. Then he reaches under the desk and brings out a ledger bound in black, with a small brass lock and the words "
    "RESTRICTED SECTION: OUTSTANDING on the cover.\n\n"
    "FENWICK: \"Since you ask.\" He unlocks it with a key he wears round his neck. \"Six grimoires. Six borrowers. A combined total of "
    "two hundred and four years overdue. The fines alone could rebuild the east wing. Twice.\"\n\n"
    "\"These are not cookbooks. These are SPELLBOOKS. Real ones. Collegium originals. Every one of them holds a working spell under a "
    "binding-charm, which I alone can open.\"\n\n"
    "He slides the ledger across.\n\n"
    "\"Bring them back, and I will let you copy every spell into your own book while I stamp them in. That is not policy. That is "
    "desperation.\"",
    [C('"Let\'s see that list."', "od_who", actions=[SQ(0), SF("overdue_started")])])
f.node("od_who",
    "FENWICK (running a finger down the ledger): \"'On Cold Shoulders'. Lord Ashgrave, Hollowmere Manor. Borrowed to 'brood more "
    "effectively'. He did not need help.\"\n\n"
    "\"'Chain of Command'. Professor Pickering, Saltmere. Borrowed for 'research'. Seven extension requests, all written in a hand that "
    "gets worse each time.\"\n\n"
    "\"'The Standing Ovation'. Madame Odette. Signed out 'for one night only'. Nine years ago.\"\n\n"
    "\"'Slow Burn'. Mother Brine, of the Drowned Lantern. I'm told it's under a pot.\"\n\n"
    "\"'[REDACTED]'. Brother Aldous. He says he never borrowed it. The ledger says otherwise. The ledger does not lie.\"\n\n"
    "\"And 'Spatial Misfiling and You'.\" He hesitates. \"Clerk Oakhaven. Who has never once returned a book late in his life. Which is why "
    "I find this one so... troubling.\"",
    [C('"I\'ll get them back."', "root")])
f.node("od_return", "FENWICK (stamp raised, eyes shining): \"Yes? YES? Which ones?\"",
       [C("Hand over 'On Cold Shoulders'.", "od_r0", [HAS("core:item.grimoire_cold")]),
        C("Hand over 'Chain of Command'.", "od_r1", [HAS("core:item.grimoire_chain")]),
        C("Hand over 'The Standing Ovation'.", "od_r2", [HAS("core:item.grimoire_ovation")]),
        C("Hand over 'Slow Burn'.", "od_r3", [HAS("core:item.grimoire_slow")]),
        C("Hand over '[REDACTED]'.", "od_r4", [HAS("core:item.grimoire_redacted")]),
        C("Hand over 'Spatial Misfiling and You'.", "od_r5", [HAS("core:item.grimoire_clerical")]),
        C('"That\'s all of them, Fenwick."', "od_done", [FL(RETURNED, 6)]),
        C('"None yet. Sorry."', "root")])
quips = [
    "FENWICK: \"It's... sparkling.\" He holds it at arm's length. \"There is glitter in the spine. There is glitter in the GUTTER of every page. "
    "I am going to be finding glitter in this library until I die.\" Stamp. \"Copy it quickly. Cold Shoulder: it's in the ring, on page nine.\"",
    "FENWICK reads the margins and goes pale. \"'must ask Fenwick for an extension'. Forty-one times. On one page.\" He closes it gently. "
    "\"Poor man. Stamp. Copy it. Chain of Command. Mind the jumps.\"",
    "FENWICK: \"'For one night only'.\" Stamp. \"Nine years. I suppose it was a long night.\" A pause. \"Did she say anything about me?\" "
    "Another pause. \"Never mind. Standing Ovation. Copy it. Don't cast it in here.\"",
    "FENWICK sniffs it. \"Chowder.\" Sniffs again. \"Good chowder, admittedly.\" Stamp. \"Slow Burn. Copy it. Chapter Six is the spell. "
    "Chapter Four is, apparently, a fish stew.\"",
    "FENWICK opens it, flicks through, and turns it upside down. \"It's ALL redacted. Every page. He blacked out his own copy of the book about "
    "blacking things out.\" He looks at the ceiling. \"Somehow the spell still works. [REDACTED]. Copy it. I can't read it, but you can.\"",
    "FENWICK holds it for a long moment. \"Filed under Q. Oakhaven filed it under Q.\" He sits down. \"Nineteen years, never late, not once, "
    "and he misfiled his OWN library book.\" Something like a smile. \"I think I like him more now. Clerical Error. Copy it.\"",
]
for i, (iid, title, spell, _) in enumerate(BOOKS):
    f.node(f"od_r{i}", quips[i], [C('"Thank you, Fenwick."', "od_return")],
           [TI(f"core:item.{iid}"), LS(f"core:spell.{spell}"), SF(f"ret_{iid}"), XP("lore", 25)])
f.node("od_done",
    "Fenwick closes the black ledger. He turns the key in its little brass lock. Then, for the first time in your acquaintance, he takes the "
    "key off from round his neck and drops it in a drawer.\n\n"
    "FENWICK: \"Two hundred and four years. Six books. Every one back on its shelf.\" His voice catches slightly. \"Do you know what that "
    "is? That's a complete collection. I have never in my life had a complete collection.\"\n\n"
    "He takes a card from his breast pocket, laminated, with a number embossed in gold: 0000001.\n\n"
    "\"Lifetime membership. All fines waived. Every fine. Including the ones you haven't incurred yet.\" He presses it into your hand. "
    "\"Including the Restricted Section. Go anywhere. Read anything.\" Then, quickly: \"Within reason. Shh.\"",
    [C('"I\'ll treasure it, Fenwick."', "root")], [SQ(100), GI("core:item.library_card"), GG(150), XP("lore", 80)])

# --- the borrowers
def borrower(did, root, prefix, speaker, topic, nid, text, iid, flag, extra=None):
    nodes = DL[did]["nodes"]
    topics(nodes, root, [(f"{prefix}.t", topic, [QA(0), QB(100), FN(flag)], nid)])
    b = Dlg(prefix, nodes, speaker)
    if extra:
        extra(b, nodes)
    else:
        b.node(nid, text, [C('"Thank you."', root)], [GI(f"core:item.{iid}"), SF(flag)])

def ash(b, nodes):
    b.node("od_ash",
        "Ashgrave turns from the window with infinite slowness.\n\n"
        "ASHGRAVE: \"'On Cold Shoulders'. Yes. It speaks to me. It is the only book that has ever understood me.\" He clutches it to his chest. "
        "\"I cannot give it up. Unless...\"\n\n"
        "\"Unless someone were to tell me, honestly, what they thought of my poetry.\"",
        [C('"Your poetry is magnificent, my lord."', "od_ash_lie", roll={"skill": "persuasion", "dc": 12, "fail_next": "od_ash_caught"}),
         C('"Honestly? It\'s quite bad. But you clearly mean every word, and that counts."', "od_ash_true")])
    b.node("od_ash_lie", "ASHGRAVE (glittering, overcome): \"Magnificent. MAGNIFICENT.\" He hands you the book without looking at it. \"Take it. "
           "I no longer need a guide. I have a fan.\"", [C('"...Thank you."', "root")], [GI("core:item.grimoire_cold"), SF("got_grimoire_cold")])
    b.node("od_ash_caught", "ASHGRAVE: \"You're lying. I can always tell. I've been lied to by the finest.\" He sighs, tragically, and hands it over "
           "anyway. \"Take it. Take everything. Nobody understands me.\"", [C('"...Sorry."', "root")], [GI("core:item.grimoire_cold"), SF("got_grimoire_cold")])
    b.node("od_ash_true", "Ashgrave stares at you. Nobody has ever said that to him before.\n\nASHGRAVE (very quietly): \"...Thank you.\" "
           "He hands you the book. \"I'm going to write a poem about this. It will be very bad. I will mean every word.\"",
           [C('"I look forward to it."', "root")], [GI("core:item.grimoire_cold"), SF("got_grimoire_cold"), XP("persuasion", 20)])

borrower("core:dialogue.vampire_ashgrave", "root", "dlg.overdue.ash", "npc.vampire_ashgrave.name",
         '"Fenwick wants \'On Cold Shoulders\' back, my lord."', "od_ash", "", "grimoire_cold", "got_grimoire_cold", ash)
borrower("core:dialogue.professor_pickering", "root", "dlg.overdue.pick", "npc.professor_pickering.name",
         '"Professor, the library needs \'Chain of Command\' back."', "od_pick",
         "Pickering produces the book from inside his coat, where it has clearly lived for some time.\n\n"
         "PICKERING: \"Ah. Yes. I was going to ask for an extension.\" He pats it. \"The lightning passes down the line, you see, just like the "
         "tide-bells passed the count. Fascinating parallel. Possibly a paper.\" He hands it over reluctantly. \"Tell Fenwick... tell him "
         "I'm sorry about the margins.\"", "grimoire_chain", "got_grimoire_chain")
borrower("core:dialogue.odette", "root", "dlg.overdue.odette", "npc.odette.name",
         '"Madame, \'The Standing Ovation\' is nine years overdue."', "od_odette",
         "ODETTE (one gloved hand to her heart): \"Nine YEARS? Darling, I borrowed it for one night only!\"\n\n"
         "She produces it from somewhere inside the fur stole.\n\n"
         "ODETTE: \"It was a very long night. The understudy was a disaster. I needed something to bring the house down, and it DID, literally, "
         "the balcony is still being repaired.\" She hands it over with a flourish. \"Tell Fenwick he's welcome at any opening night. Front row. "
         "Bring earplugs.\"", "grimoire_ovation", "got_grimoire_ovation")
borrower("core:dialogue.mother_brine", "root", "dlg.overdue.brine", "npc.mother_brine.name",
         '"Mother Brine, the library wants \'Slow Burn\' back."', "od_brine",
         "Mother Brine lifts a large pot of chowder off the bar. Underneath, steaming gently, is a book.\n\n"
         "BRINE: \"Keeps it warm. Eleven years. Best chowder on the coast and I'll thank you not to ask why.\"\n\n"
         "She hands it over, then catches your arm. \"Chapter Four's a fish stew. Chapter Six is the spell. Do NOT get them mixed up.\"",
         "grimoire_slow", "got_grimoire_slow")
borrower("core:dialogue.brother_aldous", "root", "dlg.overdue.aldous", "npc.brother_aldous.name",
         '"Brother, Fenwick says you have \'[REDACTED]\'."', "od_aldous",
         "BROTHER ALDOUS: \"I have never borrowed any such book.\"\n\nYou wait.\n\n"
         "BROTHER ALDOUS: \"...It was for the hymn book. Some of the old verses were very rude. 'O Lord, Thy Bounteous Melons'. I couldn't have "
         "children singing that.\" He produces a book, every page solid black. \"I may have got carried away. I redacted the instructions as well. "
         "And the cover. And the index.\" He hands it over. \"The spell still works. I checked. On the melons verse.\"",
         "grimoire_redacted", "got_grimoire_redacted")
borrower("core:dialogue.clerk_oakhaven", "greeting", "dlg.overdue.oak", "npc.clerk_oakhaven.name",
         '"Oakhaven, Fenwick has you down for \'Spatial Misfiling and You\'."', "od_oak",
         "Oakhaven freezes with his pen in mid-air.\n\nOAKHAVEN: \"That is not possible. I have never been late with a library book. "
         "Nineteen years. Not one day.\" He goes to his filing cabinet, opens the drawer marked S, closes it, opens the drawer marked M, closes it, "
         "stands very still for a long time, and opens the drawer marked Q.\n\nThe book is there.\n\n"
         "OAKHAVEN (in a very small voice): \"Q for 'Quite Lost'.\" He hands it to you as if it were radioactive. \"Please tell Fenwick I'm "
         "sorry. Please tell nobody else. Please.\"", "grimoire_clerical", "got_grimoire_clerical")
save("content/dialogue/chapter_zero_dialogue.json", D)

# ======================================================================= quest
QQ = load("content/quests/chapter_zero_quests.json")
QQ["quests"].append({"id": Q, "title_key": "quest.overdue.title", "summary_key": "quest.overdue.summary", "campaign": "tales_of_bellwether",
    "stages": [
        {"stage": 0, "objective_key": "quest.overdue.stage0", "journal_key": "quest.overdue.journal0",
         "markers": ["npc_ashgrave", "npc_pickering", "npc_odette", "npc_odette_stage", "npc_brine", "npc_aldous", "npc_oakhaven", "npc_fenwick"]},
        {"stage": 100, "objective_key": "quest.overdue.stage100", "journal_key": "quest.overdue.journal100", "completed": True}]})
save("content/quests/chapter_zero_quests.json", QQ)
S.update({
    "quest.overdue.title": "Overdue: The Restricted Section",
    "quest.overdue.summary": "Six Collegium spellbooks, six borrowers, two hundred and four years overdue. Fenwick will let you copy each spell when you bring it back.",
    "quest.overdue.stage0": "Recover the six overdue grimoires (Ashgrave, Pickering, Odette, Mother Brine, Brother Aldous, Oakhaven) and return them to Fenwick.",
    "quest.overdue.journal0": "Fenwick's black ledger: 'On Cold Shoulders' (Ashgrave), 'Chain of Command' (Pickering), 'The Standing Ovation' (Odette), 'Slow Burn' (Mother Brine), '[REDACTED]' (Brother Aldous) and 'Spatial Misfiling and You' (Oakhaven, apparently). Each one I return, I can copy.",
    "quest.overdue.stage100": "Completed: the Restricted Section is complete.",
    "quest.overdue.journal100": "Six books, all back on the shelf. Fenwick took the key off from round his neck. I have library card number 0000001, and no fines, ever.",
    "tip.29": "Chill something three times and it freezes. Set fire to something frozen and it shatters. Fenwick does not approve of this, but he did write it down.",
    "tip.30": "Lightning on a burning foe causes an Overload. Lightning on a burning library causes a lifetime ban.",
})

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("strings:", len(S))

"""Perks: at skill milestones, pick one of two. Writes content/perks/perks.json, registers it in the manifest, adds
localization, and Brother Aldous's respec ("The Rite of Second Thoughts").

ARCHIVE: this one-off authoring script already ran (its output lives in content/). Do NOT rerun it: it appends."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))

S = {}
# (skill, level, [(id, name, description, bonuses), (id, name, description, bonuses)])
P = [
    # ---------------------------------------------------------------- swords
    ("swords", 15, [("blade_rhythm", "Blade Rhythm", "Your swings fall into a rhythm. +8% critical chance.", {"crit_chance_bonus": 0.08}),
                    ("heavy_handed", "Heavy-Handed", "Heavy attacks hit 30% harder. Subtlety is for other people.", {"heavy_damage_bonus": 0.3})]),
    ("swords", 25, [("riposte", "Riposte School", "A blocked blow is a lesson. Blocking takes 40% less stamina.", {"block_stamina_reduction": 0.4}),
                    ("first_cut", "The First Cut", "The first blow on an unhurt foe deals 40% more damage.", {"opener_damage_bonus": 0.4})]),
    ("swords", 40, [("last_stand", "Last Stand", "Below 35% health, all your damage is 35% higher. The bards will be thrilled.", {"desperation_damage_bonus": 0.35}),
                    ("battle_trance", "Battle Trance", "Every kill restores 12 health.", {"heal_on_kill": 12})]),
    # ---------------------------------------------------------------- daggers
    ("daggers", 15, [("from_shadows", "From the Shadows", "Sneak attacks deal an extra x0.75 damage.", {"sneak_damage_bonus": 0.75}),
                     ("quick_hands", "Quick Hands", "+0.4 critical multiplier.", {"crit_damage_bonus": 0.4})]),
    ("daggers", 25, [("ember_edge", "Ember Edge", "Critical hits have a 50% chance to set the target on fire.", {"crit_burn": 0.5}),
                     ("vampire_cut", "Paper Cut", "8% life steal. It's the little ones that really hurt.", {"life_steal": 0.08})]),
    ("daggers", 40, [("assassin", "Professional Courtesy", "Sneak attacks deal another x1.0. Kills restore 15 mana.", {"sneak_damage_bonus": 1.0, "mana_on_kill": 15}),
                     ("thousand_cuts", "Death by a Thousand Forms", "+10% critical chance and +0.3 critical multiplier.", {"crit_chance_bonus": 0.1, "crit_damage_bonus": 0.3})]),
    # ---------------------------------------------------------------- bows
    ("bows", 15, [("eagle_eye", "Eagle Eye", "Sneak arrows deal x1.25 more.", {"ranged_crit_multiplier": 1.25}),
                  ("steady_breath", "Steady Breath", "+6% critical chance, and you move 5% faster.", {"crit_chance_bonus": 0.06, "move_speed_bonus": 0.05})]),
    ("bows", 25, [("hunters_mark", "Hunter's Mark", "The first hit on an unhurt foe deals 50% more damage.", {"opener_damage_bonus": 0.5}),
                  ("quiet_quiver", "Quiet Quiver", "Crouching makes you 25% harder to spot.", {"sneak_visibility_reduction": 0.25})]),
    ("bows", 40, [("deadeye", "Deadeye", "Sneak attacks deal another x0.75, and +0.3 critical multiplier.", {"sneak_damage_bonus": 0.75, "crit_damage_bonus": 0.3}),
                  ("ranger_stride", "Ranger's Stride", "+12% movement speed and +3 stamina per second.", {"move_speed_bonus": 0.12, "stamina_regen": 3.0})]),
    # ---------------------------------------------------------------- block
    ("block", 15, [("shieldwall", "Shieldwall", "Blocking stops a further 12% of damage.", {"block_reduction_bonus": 0.12}),
                   ("thick_skin", "Thick Skin", "+3 armor.", {"armor_bonus": 3})]),
    ("block", 25, [("second_wind", "Second Wind", "Each block restores 5 health.", {"heal_on_block": 5}),
                   ("iron_will", "Iron Grip", "Blocking takes 50% less stamina.", {"block_stamina_reduction": 0.5})]),
    ("block", 40, [("unbreakable", "Unbreakable", "+5 armor and blocking stops a further 10% of damage.", {"armor_bonus": 5, "block_reduction_bonus": 0.1}),
                   ("counterweight", "Counterweight", "Heavy attacks hit 40% harder.", {"heavy_damage_bonus": 0.4})]),
    # ---------------------------------------------------------------- elemental
    ("elemental", 15, [("kindling", "Kindling", "Burning deals 50% more damage.", {"burn_damage_bonus": 0.5}),
                       ("permafrost", "Permafrost", "Foes freeze after one fewer chill.", {"freeze_stacks_reduction": 1})]),
    ("elemental", 25, [("forked", "Forked Lightning", "Chain spells jump to one more foe. Shocked foes take a further 10% damage.",
                        {"chain_jump_bonus": 1, "shock_damage_bonus": 0.1}),
                       ("wide_berth", "Wide Berth", "Novas reach 35% further.", {"nova_radius_bonus": 0.35})]),
    ("elemental", 40, [("pyre", "Funeral Pyre", "Anything that dies burning spreads its flames to everyone nearby.", {"burn_spread_on_death": 1}),
                       ("thermal_shock", "Thermal Shock", "Shatter and Overload deal 60% more damage.", {"combo_damage_bonus": 0.6})]),
    # ---------------------------------------------------------------- restoration
    ("restoration", 15, [("bedside", "Bedside Manner", "Healing and warding spells are 30% stronger.", {"heal_power_bonus": 0.3}),
                         ("herbalist", "Field Medic", "Potions restore 40% more.", {"potion_bonus": 0.4})]),
    ("restoration", 25, [("renewal", "Renewal", "Regenerate 1.2 health per second.", {"health_regen": 1.2}),
                         ("siphoner", "Siphoner", "Kills restore 10 mana and 6 health.", {"mana_on_kill": 10, "heal_on_kill": 6})]),
    ("restoration", 40, [("sanctuary", "Sanctuary", "+4 armor, and healing is 25% stronger still.", {"armor_bonus": 4, "heal_power_bonus": 0.25}),
                         ("lifeline", "Lifeline", "6% life steal on everything, and +0.5 sanity per second.", {"life_steal": 0.06, "sanity_regen": 0.5})]),
    # ---------------------------------------------------------------- illusion
    ("illusion", 15, [("misdirection", "Misdirection", "Status effects last 25% longer.", {"status_duration_bonus": 0.25}),
                      ("quickening", "Quick Study", "All spells recharge 15% faster.", {"spell_cooldown_reduction": 0.15})]),
    ("illusion", 25, [("long_hop", "Long Hop", "Blink spells carry you 50% further.", {"blink_distance_bonus": 0.5}),
                      ("smoke_mirrors", "Smoke and Mirrors", "Crouching makes you 30% harder to spot.", {"sneak_visibility_reduction": 0.3})]),
    ("illusion", 40, [("hex_master", "Hex Master", "Status effects land 15% more often.", {"status_chance_bonus": 0.15}),
                      ("cheap_tricks", "Cheap Tricks", "Spells cost 12% less and recharge 10% faster.", {"spell_cost_reduction": 0.12, "spell_cooldown_reduction": 0.1})]),
    # ---------------------------------------------------------------- utility (two milestones)
    ("athletics", 15, [("long_legs", "Long Legs", "+8% movement speed.", {"move_speed_bonus": 0.08}),
                       ("deep_lungs", "Deep Lungs", "+3 stamina per second.", {"stamina_regen": 3.0})]),
    ("athletics", 30, [("marathon", "Marathon", "+10% movement speed and +2 stamina per second.", {"move_speed_bonus": 0.1, "stamina_regen": 2.0}),
                       ("brawler", "Tavern Brawler", "Heavy attacks hit 25% harder.", {"heavy_damage_bonus": 0.25})]),
    ("perception", 15, [("keen_eye", "Keen Eye", "+5% critical chance.", {"crit_chance_bonus": 0.05}),
                        ("magpie", "Magpie", "Find 30% more gold.", {"gold_find_bonus": 0.3})]),
    ("perception", 30, [("weak_spot", "Weak Spot", "+0.35 critical multiplier.", {"crit_damage_bonus": 0.35}),
                        ("treasure_nose", "Treasure Nose", "Find another 40% more gold, and lockpicking is 10% easier.", {"gold_find_bonus": 0.4, "lockpick_bonus": 0.1})]),
    ("stealth", 15, [("light_step", "Light Step", "Crouching makes you 20% harder to spot.", {"sneak_visibility_reduction": 0.2}),
                     ("backstabber", "Backstabber", "Sneak attacks deal an extra x0.5.", {"sneak_damage_bonus": 0.5})]),
    ("stealth", 30, [("ghost", "Like a Ghost", "Crouching makes you another 25% harder to spot.", {"sneak_visibility_reduction": 0.25}),
                     ("ambusher", "Ambusher", "The first blow on an unhurt foe deals 50% more damage.", {"opener_damage_bonus": 0.5})]),
    ("lockpicking", 15, [("tumbler", "Tumbler Whisperer", "Locks are 12% easier.", {"lockpick_bonus": 0.12}),
                         ("pocket_lint", "Pocket Lint", "Find 25% more gold.", {"gold_find_bonus": 0.25})]),
    ("lockpicking", 30, [("master_key", "Master Key", "Locks are another 15% easier.", {"lockpick_bonus": 0.15}),
                         ("quick_fingers", "Quick Fingers", "+6% critical chance.", {"crit_chance_bonus": 0.06})]),
    ("persuasion", 15, [("haggler", "Haggler", "+10% shop discount.", {"shop_discount": 0.1}),
                        ("rally", "Rally the Party", "Your companions deal 40% more damage.", {"companion_damage_bonus": 0.4})]),
    ("persuasion", 30, [("silver_tongue", "Silver Tongue", "+2 to every dialogue roll.", {"dice_bonus": 2.0}),
                        ("inspiring", "Inspiring Presence", "Companions deal another 50% more damage, and you regenerate 0.5 sanity per second.",
                         {"companion_damage_bonus": 0.5, "sanity_regen": 0.5})]),
    ("lore", 15, [("scholar", "Scholar", "All skills improve 15% faster.", {"skill_xp_bonus": 0.15}),
                  ("arcanist", "Arcanist", "+8% spell power.", {"spell_power_bonus": 0.08})]),
    ("lore", 30, [("polymath", "Polymath", "All skills improve another 20% faster.", {"skill_xp_bonus": 0.2}),
                  ("forbidden", "Forbidden Reading", "+12% spell power, but it costs you: -0.3 sanity per second.", {"spell_power_bonus": 0.12, "sanity_regen": -0.3})]),
]

perks = []
for skill, level, options in P:
    for pid, name, desc, bonuses in options:
        perks.append({"id": f"core:perk.{pid}", "skill": skill, "level": level, "name_key": f"perk.{pid}.name", "desc_key": f"perk.{pid}.desc",
                      "bonuses": bonuses})
        S[f"perk.{pid}.name"] = name
        S[f"perk.{pid}.desc"] = desc
import os
os.makedirs("content/perks", exist_ok=True)
save("content/perks/perks.json", {"schema_version": 1, "perks": perks})
M = load("content/manifest.json")
M["perks"] = "content/perks/perks.json"
save("content/manifest.json", M)

# ---------------------------------------------------------------- Brother Aldous: the Rite of Second Thoughts
D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}
an = DL["core:dialogue.brother_aldous"]["nodes"]
ch = an["root"]["choices"]
idx = max(i for i, c in enumerate(ch) if c["next"] == "END")
S["dlg.aldous.respec.t"] = '"Brother, I\'d like to rethink some choices I\'ve made."'
ch.insert(idx, {"text_key": "dlg.aldous.respec.t", "next": "respec"})
S["dlg.aldous.respec"] = ("Brother Aldous folds his hands.\n\n\"The Rite of Second Thoughts. Very old. Very holy. Mostly paperwork.\"\n\n"
                          "\"You kneel. You reflect. You think about every path you've chosen, the swords you chose instead of shields, the fire you chose "
                          "instead of frost, and the Dawn gently says: 'Are you SURE?' And then you may choose again. Every perk you hold returns to you, "
                          "to be chosen anew.\"\n\n\"There is a suggested donation of fifty gold. The Dawn is not mercenary. The roof, however, leaks.\"")
S["dlg.aldous.respec.c0"] = "Donate 50 gold and kneel. (Choose all your perks again.)"
S["dlg.aldous.respec.c1"] = '"Maybe later, Brother."'
S["dlg.aldous.respec_done"] = ("You kneel. The candles flicker. Somewhere, very faintly, a choir sings a single questioning note: \"Are you SURE?\"\n\n"
                               "You stand, lighter. Every perk you held is yours to choose again.\n\nBROTHER ALDOUS: \"The Dawn bless your new choices. "
                               "And your old ones, which were also fine. Mostly.\"")
S["dlg.aldous.respec_done.c0"] = '"Thank you, Brother."'
an["respec"] = {"speaker_key": "npc.brother_aldous.name", "text_key": "dlg.aldous.respec",
                "choices": [{"text_key": "dlg.aldous.respec.c0", "next": "respec_done", "conditions": [{"type": "gold_at_least", "value": 50}],
                             "actions": [{"type": "take_gold", "amount": 50}]},
                            {"text_key": "dlg.aldous.respec.c1", "next": "root"}]}
an["respec_done"] = {"speaker_key": "npc.brother_aldous.name", "text_key": "dlg.aldous.respec_done", "actions": [{"type": "reset_perks"}],
                     "choices": [{"text_key": "dlg.aldous.respec_done.c0", "next": "root"}]}
save("content/dialogue/chapter_zero_dialogue.json", D)
S["tip.31"] = "Perks: every few skill levels you choose one of two. Brother Aldous will let you choose again, for a small donation to the roof."

loc = load("content/localization/en.json")
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("perks:", len(perks))

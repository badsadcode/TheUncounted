#!/usr/bin/env python3
"""
Populates the human-readable, editable JSON content files in content/ and mods/example_mod/
for THE UNCOUNTED: Chapter Zero - Legally Deceased.
All produced JSON files are standalone data files loaded and validated by game.exe at runtime.
"""

# NOTE: bootstrap generator. content/* has since been extended by hand (story, side quest, readables, torches,
# tuning). Re-running this script overwrites those files; edit the JSON directly instead.


import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def write_json(rel_path, data):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_all_content():
    # 1. content/manifest.json
    write_json("content/manifest.json", {
        "schema_version": 1,
        "pack_id": "core",
        "pack_name": "The Uncounted: Chapter Zero - Legally Deceased",
        "version": "1.0.0",
        "localization": ["content/localization/en.json"],
        "balancing": "content/balancing/combat_and_progression.json",
        "attributes": "content/attributes/attributes.json",
        "races": "content/races/races.json",
        "backgrounds": "content/backgrounds/backgrounds.json",
        "archetypes": "content/archetypes/archetypes.json",
        "skills": "content/skills/skills.json",
        "synergies": "content/synergies/synergies.json",
        "factions": "content/factions/factions.json",
        "spells": ["content/spells/core_spells.json"],
        "items": [
            "content/items/weapons.json",
            "content/items/armor_and_gear.json",
            "content/items/consumables_and_books.json",
            "content/items/quest_and_keys.json"
        ],
        "loot_tables": ["content/loot_tables/core_loot.json"],
        "creatures": ["content/creatures/core_creatures.json"],
        "npcs": ["content/npcs/core_npcs.json"],
        "dialogue": ["content/dialogue/chapter_zero_dialogue.json"],
        "quests": ["content/quests/chapter_zero_quests.json"],
        # One seamless world composed from content/regions/ by tools/build_world.py
        "maps": ["content/maps/edrath_world.json"]
    })

    # 2. content/balancing/combat_and_progression.json
    write_json("content/balancing/combat_and_progression.json", {
        "schema_version": 1,
        "base_health": 60,
        "health_per_endurance": 8,
        "base_stamina": 70,
        "stamina_per_endurance": 5,
        "stamina_per_agility": 3,
        "base_mana": 40,
        "mana_per_intellect": 6,
        "mana_per_will": 4,
        "base_carry_weight": 35.0,
        "carry_weight_per_might": 4.5,
        "stamina_regen_per_sec": 11.5,
        "mana_regen_per_sec": 3.2,
        "heavy_attack_damage_mult": 1.65,
        "heavy_attack_stamina_mult": 1.75,
        "block_damage_reduction": 0.65,
        "parry_window_seconds": 0.25,
        "parry_stamina_bonus": 12.0,
        "skill_anti_exploit_cooldown_sec": 1.2,
        "skill_diminishing_factor": 0.08,
        "difficulties": {
            "story": {"player_damage_mult": 1.35, "enemy_damage_mult": 0.65},
            "standard": {"player_damage_mult": 1.0, "enemy_damage_mult": 1.0},
            "veteran": {"player_damage_mult": 0.85, "enemy_damage_mult": 1.30}
        }
    })

    # 3. content/attributes/attributes.json
    write_json("content/attributes/attributes.json", {
        "schema_version": 1,
        "attributes": [
            {"id": "might", "name_key": "attr.might.name", "desc_key": "attr.might.desc", "base": 10},
            {"id": "agility", "name_key": "attr.agility.name", "desc_key": "attr.agility.desc", "base": 10},
            {"id": "endurance", "name_key": "attr.endurance.name", "desc_key": "attr.endurance.desc", "base": 10},
            {"id": "intellect", "name_key": "attr.intellect.name", "desc_key": "attr.intellect.desc", "base": 10},
            {"id": "will", "name_key": "attr.will.name", "desc_key": "attr.will.desc", "base": 10},
            {"id": "presence", "name_key": "attr.presence.name", "desc_key": "attr.presence.desc", "base": 10}
        ]
    })

    # 4. content/races/races.json
    write_json("content/races/races.json", {
        "schema_version": 1,
        "races": [
            {
                "id": "core:race.human",
                "name_key": "race.human.name",
                "description_key": "race.human.desc",
                "portrait": "assets/ui/portraits/human.png",
                "attribute_modifiers": {"presence": 1, "will": 1},
                "skill_bonuses": {"persuasion": 5, "lore": 5},
                "trait_key": "race.human.trait",
                "xp_gain_multiplier": 1.08
            },
            {
                "id": "core:race.dwarf",
                "name_key": "race.dwarf.name",
                "description_key": "race.dwarf.desc",
                "portrait": "assets/ui/portraits/dwarf.png",
                "attribute_modifiers": {"endurance": 2, "will": 1},
                "skill_bonuses": {"lore": 6, "block": 5},
                "trait_key": "race.dwarf.trait",
                "xp_gain_multiplier": 1.0
            },
            {
                "id": "core:race.elf",
                "name_key": "race.elf.name",
                "description_key": "race.elf.desc",
                "portrait": "assets/ui/portraits/elf.png",
                "attribute_modifiers": {"intellect": 2, "agility": 1},
                "skill_bonuses": {"perception": 6, "elemental": 5},
                "trait_key": "race.elf.trait",
                "xp_gain_multiplier": 1.0
            },
            {
                "id": "core:race.orc",
                "name_key": "race.orc.name",
                "description_key": "race.orc.desc",
                "portrait": "assets/ui/portraits/orc.png",
                "attribute_modifiers": {"might": 2, "endurance": 1},
                "skill_bonuses": {"athletics": 6, "persuasion": 4},
                "trait_key": "race.orc.trait",
                "xp_gain_multiplier": 1.0
            },
            {
                "id": "core:race.halfling",
                "name_key": "race.halfling.name",
                "description_key": "race.halfling.desc",
                "portrait": "assets/ui/portraits/halfling.png",
                "attribute_modifiers": {"agility": 2, "presence": 1},
                "skill_bonuses": {"stealth": 6, "lockpicking": 5},
                "trait_key": "race.halfling.trait",
                "xp_gain_multiplier": 1.0
            }
        ]
    })

    # 5. content/backgrounds/backgrounds.json
    write_json("content/backgrounds/backgrounds.json", {
        "schema_version": 1,
        "backgrounds": [
            {
                "id": "core:bg.displaced_heir",
                "name_key": "bg.displaced_heir.name",
                "description_key": "bg.displaced_heir.desc",
                "starting_gold": 45,
                "skill_bonuses": {"lore": 5, "persuasion": 5},
                "starting_items": ["core:item.signet_ring"]
            },
            {
                "id": "core:bg.border_watch",
                "name_key": "bg.border_watch.name",
                "description_key": "bg.border_watch.desc",
                "starting_gold": 30,
                "skill_bonuses": {"perception": 5, "athletics": 5},
                "starting_items": ["core:item.stamina_tonic"]
            },
            {
                "id": "core:bg.collegium_dropout",
                "name_key": "bg.collegium_dropout.name",
                "description_key": "bg.collegium_dropout.desc",
                "starting_gold": 25,
                "skill_bonuses": {"lore": 8, "elemental": 4},
                "starting_items": ["core:item.mana_potion"]
            },
            {
                "id": "core:bg.tomb_surveyor",
                "name_key": "bg.tomb_surveyor.name",
                "description_key": "bg.tomb_surveyor.desc",
                "starting_gold": 35,
                "skill_bonuses": {"lockpicking": 6, "stealth": 4},
                "starting_items": ["core:item.lockpick", "core:item.lockpick"]
            }
        ]
    })

    # 6. content/archetypes/archetypes.json
    # Starting packages ONLY - never lock progression, weapons, or spells!
    write_json("content/archetypes/archetypes.json", {
        "schema_version": 1,
        "archetypes": [
            {
                "id": "core:archetype.warrior",
                "name_key": "arch.warrior.name",
                "description_key": "arch.warrior.desc",
                "attribute_bonuses": {"might": 2, "endurance": 2},
                "skill_bonuses": {"swords": 12, "block": 10, "athletics": 6},
                "starting_equipment": ["core:item.iron_longsword", "core:item.iron_shield", "core:item.chain_hauberk"],
                "starting_inventory": ["core:item.health_potion", "core:item.health_potion", "core:item.death_notice"],
                "starting_spells": ["core:spell.glimmer"]
            },
            {
                "id": "core:archetype.ranger",
                "name_key": "arch.ranger.name",
                "description_key": "arch.ranger.desc",
                "attribute_bonuses": {"agility": 2, "endurance": 1, "will": 1},
                "skill_bonuses": {"bows": 14, "perception": 10, "stealth": 6},
                "starting_equipment": ["core:item.hunting_bow", "core:item.leather_jerkin", "core:item.traveler_boots"],
                "starting_inventory": ["core:item.rusted_sword", "core:item.wooden_arrow", "core:item.health_potion", "core:item.death_notice"],
                "starting_ammo": 28,
                "starting_spells": ["core:spell.glimmer"]
            },
            {
                "id": "core:archetype.mage",
                "name_key": "arch.mage.name",
                "description_key": "arch.mage.desc",
                "attribute_bonuses": {"intellect": 3, "will": 1},
                "skill_bonuses": {"elemental": 14, "lore": 10, "restoration": 6},
                "starting_equipment": ["core:item.oak_staff", "core:item.scholar_robe"],
                "starting_inventory": ["core:item.mana_potion", "core:item.mana_potion", "core:item.health_potion", "core:item.death_notice"],
                "starting_spells": ["core:spell.ember_bolt", "core:spell.glimmer", "core:spell.ward"]
            },
            {
                "id": "core:archetype.rogue",
                "name_key": "arch.rogue.name",
                "description_key": "arch.rogue.desc",
                "attribute_bonuses": {"agility": 3, "presence": 1},
                "skill_bonuses": {"daggers": 12, "stealth": 12, "lockpicking": 12},
                "starting_equipment": ["core:item.steel_dagger", "core:item.leather_jerkin", "core:item.traveler_boots"],
                "starting_inventory": ["core:item.lockpick", "core:item.lockpick", "core:item.lockpick", "core:item.health_potion", "core:item.death_notice"],
                "starting_spells": ["core:spell.veil", "core:spell.glimmer"]
            },
            {
                "id": "core:archetype.cleric",
                "name_key": "arch.cleric.name",
                "description_key": "arch.cleric.desc",
                "attribute_bonuses": {"will": 2, "endurance": 1, "presence": 1},
                "skill_bonuses": {"restoration": 14, "swords": 8, "block": 8, "lore": 6},
                "starting_equipment": ["core:item.iron_mace", "core:item.iron_shield", "core:item.chain_hauberk"],
                "starting_inventory": ["core:item.health_potion", "core:item.mana_potion", "core:item.death_notice"],
                "starting_spells": ["core:spell.mend", "core:spell.ward", "core:spell.glimmer"]
            },
            {
                "id": "core:archetype.adventurer",
                "name_key": "arch.adventurer.name",
                "description_key": "arch.adventurer.desc",
                "attribute_bonuses": {"might": 1, "agility": 1, "intellect": 1, "presence": 1},
                "skill_bonuses": {"swords": 10, "bows": 8, "elemental": 8, "perception": 8, "lockpicking": 6},
                "starting_equipment": ["core:item.rusted_sword", "core:item.leather_jerkin", "core:item.traveler_boots"],
                "starting_inventory": ["core:item.hunting_bow", "core:item.wooden_arrow", "core:item.lockpick", "core:item.health_potion", "core:item.death_notice"],
                "starting_ammo": 15,
                "starting_spells": ["core:spell.ember_bolt", "core:spell.mend", "core:spell.glimmer"]
            }
        ]
    })

    # 7. content/skills/skills.json
    write_json("content/skills/skills.json", {
        "schema_version": 1,
        "skills": [
            {"id": "swords", "domain": "combat", "name_key": "skill.swords.name", "desc_key": "skill.swords.desc", "effect_per_point": 0.015},
            {"id": "daggers", "domain": "combat", "name_key": "skill.daggers.name", "desc_key": "skill.daggers.desc", "effect_per_point": 0.016},
            {"id": "bows", "domain": "combat", "name_key": "skill.bows.name", "desc_key": "skill.bows.desc", "effect_per_point": 0.015},
            {"id": "block", "domain": "combat", "name_key": "skill.block.name", "desc_key": "skill.block.desc", "effect_per_point": 0.012},
            {"id": "elemental", "domain": "magic", "name_key": "skill.elemental.name", "desc_key": "skill.elemental.desc", "effect_per_point": 0.018},
            {"id": "restoration", "domain": "magic", "name_key": "skill.restoration.name", "desc_key": "skill.restoration.desc", "effect_per_point": 0.018},
            {"id": "illusion", "domain": "magic", "name_key": "skill.illusion.name", "desc_key": "skill.illusion.desc", "effect_per_point": 0.015},
            {"id": "athletics", "domain": "exploration", "name_key": "skill.athletics.name", "desc_key": "skill.athletics.desc", "effect_per_point": 0.008},
            {"id": "perception", "domain": "exploration", "name_key": "skill.perception.name", "desc_key": "skill.perception.desc", "effect_per_point": 0.015},
            {"id": "stealth", "domain": "exploration", "name_key": "skill.stealth.name", "desc_key": "skill.stealth.desc", "effect_per_point": 0.015},
            {"id": "lockpicking", "domain": "exploration", "name_key": "skill.lockpicking.name", "desc_key": "skill.lockpicking.desc", "effect_per_point": 0.020},
            {"id": "persuasion", "domain": "social", "name_key": "skill.persuasion.name", "desc_key": "skill.persuasion.desc", "effect_per_point": 0.015},
            {"id": "lore", "domain": "social", "name_key": "skill.lore.name", "desc_key": "skill.lore.desc", "effect_per_point": 0.015}
        ]
    })

    # 8. content/synergies/synergies.json
    write_json("content/synergies/synergies.json", {
        "schema_version": 1,
        "synergies": [
            {
                "id": "core:synergy.spellblade_conduit",
                "name_key": "synergy.spellblade.name",
                "description_key": "synergy.spellblade.desc",
                "requirements": {"swords": 10, "elemental": 10},
                "bonuses": {"melee_bonus_magic_damage": 5, "mana_on_melee_hit": 3}
            },
            {
                "id": "core:synergy.sanctified_bastion",
                "name_key": "synergy.bastion.name",
                "description_key": "synergy.bastion.desc",
                "requirements": {"block": 10, "restoration": 10},
                "bonuses": {"heal_on_block": 4, "armor_bonus": 3}
            },
            {
                "id": "core:synergy.phantom_stalker",
                "name_key": "synergy.stalker.name",
                "description_key": "synergy.stalker.desc",
                "requirements": {"stealth": 10, "bows": 10},
                "bonuses": {"ranged_crit_multiplier": 1.35, "move_speed_bonus": 0.10}
            }
        ]
    })

    # 9. content/factions/factions.json
    write_json("content/factions/factions.json", {
        "schema_version": 1,
        "factions": [
            {"id": "core:faction.bureau", "name_key": "faction.bureau.name", "desc_key": "faction.bureau.desc"},
            {"id": "core:faction.last_dawn", "name_key": "faction.last_dawn.name", "desc_key": "faction.last_dawn.desc"},
            {"id": "core:faction.ashbound", "name_key": "faction.ashbound.name", "desc_key": "faction.ashbound.desc"},
            {"id": "core:faction.collegium", "name_key": "faction.collegium.name", "desc_key": "faction.collegium.desc"}
        ]
    })

    # 10. content/spells/core_spells.json
    write_json("content/spells/core_spells.json", {
        "schema_version": 1,
        "spells": [
            {
                "id": "core:spell.ember_bolt",
                "name_key": "spell.ember_bolt.name",
                "description_key": "spell.ember_bolt.desc",
                "icon": "assets/ui/spells/ember_bolt.png",
                "skill": "elemental",
                "mana_cost": 10,
                "cooldown_seconds": 0.75,
                "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                "effect": {
                    "primitive": "projectile_damage",
                    "damage_type": "fire",
                    "base_power": 18,
                    "projectile_speed": 16.0,
                    "projectile_sprite": "assets/sprites/vfx/spell_ember.png",
                    "light_color": [1.0, 0.45, 0.15],
                    "light_radius": 5.5
                }
            },
            {
                "id": "core:spell.mend",
                "name_key": "spell.mend.name",
                "description_key": "spell.mend.desc",
                "icon": "assets/ui/spells/mend.png",
                "skill": "restoration",
                "mana_cost": 14,
                "cooldown_seconds": 1.2,
                "cast_sfx": "assets/audio/sfx/spell_heal.wav",
                "effect": {
                    "primitive": "self_heal",
                    "base_power": 28,
                    "stamina_restore": 15
                }
            },
            {
                "id": "core:spell.ward",
                "name_key": "spell.ward.name",
                "description_key": "spell.ward.desc",
                "icon": "assets/ui/spells/ward.png",
                "skill": "restoration",
                "mana_cost": 12,
                "cooldown_seconds": 1.0,
                "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                "effect": {
                    "primitive": "buff_armor",
                    "base_power": 8,
                    "duration_seconds": 35.0
                }
            },
            {
                "id": "core:spell.glimmer",
                "name_key": "spell.glimmer.name",
                "description_key": "spell.glimmer.desc",
                "icon": "assets/ui/spells/glimmer.png",
                "skill": "elemental",
                "mana_cost": 6,
                "cooldown_seconds": 0.6,
                "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                "effect": {
                    "primitive": "buff_light",
                    "light_radius": 11.0,
                    "light_color": [0.95, 0.88, 0.62],
                    "duration_seconds": 90.0
                }
            },
            {
                "id": "core:spell.veil",
                "name_key": "spell.veil.name",
                "description_key": "spell.veil.desc",
                "icon": "assets/ui/spells/veil.png",
                "skill": "illusion",
                "mana_cost": 14,
                "cooldown_seconds": 1.5,
                "cast_sfx": "assets/audio/sfx/spell_cast.wav",
                "effect": {
                    "primitive": "buff_stealth",
                    "visibility_multiplier": 0.35,
                    "duration_seconds": 25.0
                }
            }
        ]
    })

    # 11. content/items/weapons.json
    write_json("content/items/weapons.json", {
        "schema_version": 1,
        "items": [
            {
                "id": "core:item.rusted_sword",
                "name_key": "item.rusted_sword.name",
                "description_key": "item.rusted_sword.description",
                "category": "weapon",
                "icon": "assets/ui/items/rusted_sword.png",
                "world_model": "assets/models/items/rusted_sword.glb",
                "slots": ["main_hand"],
                "value": 15,
                "weight": 2.4,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "slashing",
                    "base_damage": 11,
                    "attack_time_seconds": 0.55,
                    "stamina_cost": 8,
                    "reach_meters": 2.1
                }
            },
            {
                "id": "core:item.iron_longsword",
                "name_key": "item.iron_longsword.name",
                "description_key": "item.iron_longsword.description",
                "category": "weapon",
                "icon": "assets/ui/items/iron_longsword.png",
                "world_model": "assets/models/items/iron_longsword.glb",
                "slots": ["main_hand"],
                "value": 55,
                "weight": 2.8,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "slashing",
                    "base_damage": 16,
                    "attack_time_seconds": 0.58,
                    "stamina_cost": 9,
                    "reach_meters": 2.25
                }
            },
            {
                "id": "core:item.widowmaker",
                "name_key": "item.widowmaker.name",
                "description_key": "item.widowmaker.description",
                "category": "weapon",
                "icon": "assets/ui/items/widowmaker.png",
                "world_model": "assets/models/items/widowmaker_blade.glb",
                "slots": ["main_hand"],
                "value": 240,
                "weight": 3.2,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "slashing",
                    "base_damage": 26,
                    "attack_time_seconds": 0.62,
                    "stamina_cost": 11,
                    "reach_meters": 2.5
                },
                "effects": [
                    {"type": "stat_bonus", "stat": "might", "amount": 2},
                    {"type": "stat_bonus", "stat": "will", "amount": 2}
                ]
            },
            {
                "id": "core:item.steel_dagger",
                "name_key": "item.steel_dagger.name",
                "description_key": "item.steel_dagger.description",
                "category": "weapon",
                "icon": "assets/ui/items/steel_dagger.png",
                "world_model": "assets/models/items/steel_dagger.glb",
                "slots": ["main_hand"],
                "value": 38,
                "weight": 1.1,
                "weapon": {
                    "kind": "melee",
                    "skill": "daggers",
                    "damage_type": "piercing",
                    "base_damage": 10,
                    "attack_time_seconds": 0.36,
                    "stamina_cost": 5,
                    "reach_meters": 1.75
                }
            },
            {
                "id": "core:item.iron_mace",
                "name_key": "item.iron_mace.name",
                "description_key": "item.iron_mace.description",
                "category": "weapon",
                "icon": "assets/ui/items/iron_mace.png",
                "world_model": "assets/models/items/iron_mace.glb",
                "slots": ["main_hand"],
                "value": 48,
                "weight": 3.4,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "blunt",
                    "base_damage": 15,
                    "attack_time_seconds": 0.60,
                    "stamina_cost": 10,
                    "reach_meters": 2.0
                }
            },
            {
                "id": "core:item.oak_staff",
                "name_key": "item.oak_staff.name",
                "description_key": "item.oak_staff.description",
                "category": "weapon",
                "icon": "assets/ui/items/oak_staff.png",
                "world_model": "assets/models/items/oak_staff.glb",
                "slots": ["main_hand"],
                "value": 45,
                "weight": 2.0,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "blunt",
                    "base_damage": 10,
                    "attack_time_seconds": 0.54,
                    "stamina_cost": 7,
                    "reach_meters": 2.35
                },
                "effects": [
                    {"type": "stat_bonus", "stat": "intellect", "amount": 2}
                ]
            },
            {
                "id": "core:item.hunting_bow",
                "name_key": "item.hunting_bow.name",
                "description_key": "item.hunting_bow.description",
                "category": "weapon",
                "icon": "assets/ui/items/hunting_bow.png",
                "world_model": "assets/models/items/hunting_bow.glb",
                "slots": ["main_hand"],
                "value": 52,
                "weight": 1.8,
                "weapon": {
                    "kind": "ranged",
                    "skill": "bows",
                    "damage_type": "piercing",
                    "base_damage": 15,
                    "attack_time_seconds": 0.72,
                    "stamina_cost": 8,
                    "reach_meters": 32.0,
                    "ammo_item": "core:item.wooden_arrow",
                    "projectile_speed": 24.0
                }
            },
            {
                "id": "core:item.wooden_arrow",
                "name_key": "item.wooden_arrow.name",
                "description_key": "item.wooden_arrow.description",
                "category": "ammo",
                "icon": "assets/ui/items/wooden_arrow.png",
                "world_model": "assets/models/items/wooden_arrow.glb",
                "slots": [],
                "stackable": True,
                "value": 2,
                "weight": 0.05
            }
        ]
    })

    # 12. content/items/armor_and_gear.json
    write_json("content/items/armor_and_gear.json", {
        "schema_version": 1,
        "items": [
            {
                "id": "core:item.iron_shield",
                "name_key": "item.iron_shield.name",
                "description_key": "item.iron_shield.description",
                "category": "armor",
                "icon": "assets/ui/items/iron_shield.png",
                "world_model": "assets/models/items/iron_shield.glb",
                "slots": ["off_hand"],
                "value": 42,
                "weight": 3.5,
                "armor": 5
            },
            {
                "id": "core:item.leather_jerkin",
                "name_key": "item.leather_jerkin.name",
                "description_key": "item.leather_jerkin.description",
                "category": "armor",
                "icon": "assets/ui/items/leather_jerkin.png",
                "world_model": "assets/models/items/leather_jerkin.glb",
                "slots": ["torso"],
                "value": 36,
                "weight": 3.0,
                "armor": 4
            },
            {
                "id": "core:item.chain_hauberk",
                "name_key": "item.chain_hauberk.name",
                "description_key": "item.chain_hauberk.description",
                "category": "armor",
                "icon": "assets/ui/items/chain_hauberk.png",
                "world_model": "assets/models/items/chain_hauberk.glb",
                "slots": ["torso"],
                "value": 78,
                "weight": 6.5,
                "armor": 8
            },
            {
                "id": "core:item.scholar_robe",
                "name_key": "item.scholar_robe.name",
                "description_key": "item.scholar_robe.description",
                "category": "armor",
                "icon": "assets/ui/items/scholar_robe.png",
                "world_model": "assets/models/items/scholar_robe.glb",
                "slots": ["torso"],
                "value": 48,
                "weight": 1.8,
                "armor": 2,
                "effects": [
                    {"type": "stat_bonus", "stat": "intellect", "amount": 2},
                    {"type": "stat_bonus", "stat": "will", "amount": 1}
                ]
            },
            {
                "id": "core:item.iron_helm",
                "name_key": "item.iron_helm.name",
                "description_key": "item.iron_helm.description",
                "category": "armor",
                "icon": "assets/ui/items/iron_helm.png",
                "world_model": "assets/models/items/iron_helm.glb",
                "slots": ["head"],
                "value": 34,
                "weight": 2.2,
                "armor": 3
            },
            {
                "id": "core:item.traveler_boots",
                "name_key": "item.traveler_boots.name",
                "description_key": "item.traveler_boots.description",
                "category": "armor",
                "icon": "assets/ui/items/traveler_boots.png",
                "world_model": "assets/models/items/traveler_boots.glb",
                "slots": ["legs"],
                "value": 28,
                "weight": 1.4,
                "armor": 2,
                "effects": [
                    {"type": "stat_bonus", "stat": "agility", "amount": 1}
                ]
            },
            {
                "id": "core:item.ring_of_recall",
                "name_key": "item.ring_of_recall.name",
                "description_key": "item.ring_of_recall.description",
                "category": "accessory",
                "icon": "assets/ui/items/ring_of_recall.png",
                "world_model": "assets/models/items/ring_of_recall.glb",
                "slots": ["accessory"],
                "value": 110,
                "weight": 0.1,
                "armor": 1,
                "effects": [
                    {"type": "stat_bonus", "stat": "will", "amount": 2},
                    {"type": "stat_bonus", "stat": "intellect", "amount": 1}
                ]
            },
            {
                "id": "core:item.signet_ring",
                "name_key": "item.signet_ring.name",
                "description_key": "item.signet_ring.description",
                "category": "accessory",
                "icon": "assets/ui/items/signet_ring.png",
                "world_model": "assets/models/items/signet_ring.glb",
                "slots": ["accessory"],
                "value": 65,
                "weight": 0.1,
                "effects": [
                    {"type": "stat_bonus", "stat": "presence", "amount": 2}
                ]
            }
        ]
    })

    # 13. content/items/consumables_and_books.json
    write_json("content/items/consumables_and_books.json", {
        "schema_version": 1,
        "items": [
            {
                "id": "core:item.health_potion",
                "name_key": "item.health_potion.name",
                "description_key": "item.health_potion.description",
                "category": "consumable",
                "icon": "assets/ui/items/health_potion.png",
                "world_model": "assets/models/items/potion_flask.glb",
                "slots": [],
                "stackable": True,
                "value": 18,
                "weight": 0.4,
                "effects": [{"type": "consumable_heal", "amount": 35}]
            },
            {
                "id": "core:item.mana_potion",
                "name_key": "item.mana_potion.name",
                "description_key": "item.mana_potion.description",
                "category": "consumable",
                "icon": "assets/ui/items/mana_potion.png",
                "world_model": "assets/models/items/potion_flask.glb",
                "slots": [],
                "stackable": True,
                "value": 20,
                "weight": 0.4,
                "effects": [{"type": "consumable_mana", "amount": 30}]
            },
            {
                "id": "core:item.stamina_tonic",
                "name_key": "item.stamina_tonic.name",
                "description_key": "item.stamina_tonic.description",
                "category": "consumable",
                "icon": "assets/ui/items/stamina_tonic.png",
                "world_model": "assets/models/items/potion_flask.glb",
                "slots": [],
                "stackable": True,
                "value": 15,
                "weight": 0.4,
                "effects": [{"type": "consumable_stamina", "amount": 45}]
            },
            {
                "id": "core:item.bread_loaf",
                "name_key": "item.bread_loaf.name",
                "description_key": "item.bread_loaf.description",
                "category": "consumable",
                "icon": "assets/ui/items/bread_loaf.png",
                "world_model": "assets/models/items/bread_loaf.glb",
                "slots": [],
                "stackable": True,
                "value": 6,
                "weight": 0.3,
                "effects": [
                    {"type": "consumable_heal", "amount": 12},
                    {"type": "consumable_stamina", "amount": 20}
                ]
            },
            {
                "id": "core:item.tome_ember",
                "name_key": "item.tome_ember.name",
                "description_key": "item.tome_ember.description",
                "category": "book",
                "icon": "assets/ui/items/tome_ember.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "value": 55,
                "weight": 0.8,
                "book_text_key": "book.tome_ember.text",
                "effects": [{"type": "learn_spell", "spell_id": "core:spell.ember_bolt"}]
            },
            {
                "id": "core:item.tome_mend",
                "name_key": "item.tome_mend.name",
                "description_key": "item.tome_mend.description",
                "category": "book",
                "icon": "assets/ui/items/tome_mend.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "value": 55,
                "weight": 0.8,
                "book_text_key": "book.tome_mend.text",
                "effects": [{"type": "learn_spell", "spell_id": "core:spell.mend"}]
            },
            {
                "id": "core:item.tome_ward",
                "name_key": "item.tome_ward.name",
                "description_key": "item.tome_ward.description",
                "category": "book",
                "icon": "assets/ui/items/tome_ward.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "value": 50,
                "weight": 0.8,
                "book_text_key": "book.tome_ward.text",
                "effects": [{"type": "learn_spell", "spell_id": "core:spell.ward"}]
            },
            {
                "id": "core:item.tome_glimmer",
                "name_key": "item.tome_glimmer.name",
                "description_key": "item.tome_glimmer.description",
                "category": "book",
                "icon": "assets/ui/items/tome_glimmer.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "value": 40,
                "weight": 0.8,
                "book_text_key": "book.tome_glimmer.text",
                "effects": [{"type": "learn_spell", "spell_id": "core:spell.glimmer"}]
            },
            {
                "id": "core:item.tome_veil",
                "name_key": "item.tome_veil.name",
                "description_key": "item.tome_veil.description",
                "category": "book",
                "icon": "assets/ui/items/tome_veil.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "value": 60,
                "weight": 0.8,
                "book_text_key": "book.tome_veil.text",
                "effects": [{"type": "learn_spell", "spell_id": "core:spell.veil"}]
            }
        ]
    })

    # 14. content/items/quest_and_keys.json
    write_json("content/items/quest_and_keys.json", {
        "schema_version": 1,
        "items": [
            {
                "id": "core:item.lockpick",
                "name_key": "item.lockpick.name",
                "description_key": "item.lockpick.description",
                "category": "key",
                "icon": "assets/ui/items/lockpick.png",
                "world_model": "assets/models/items/annex_key.glb",
                "slots": [],
                "stackable": True,
                "value": 10,
                "weight": 0.1
            },
            {
                "id": "core:item.annex_key",
                "name_key": "item.annex_key.name",
                "description_key": "item.annex_key.description",
                "category": "key",
                "icon": "assets/ui/items/annex_key.png",
                "world_model": "assets/models/items/annex_key.glb",
                "slots": [],
                "quest_item": True,
                "value": 0,
                "weight": 0.2
            },
            {
                "id": "core:item.crypt_key",
                "name_key": "item.crypt_key.name",
                "description_key": "item.crypt_key.description",
                "category": "key",
                "icon": "assets/ui/items/crypt_key.png",
                "world_model": "assets/models/items/annex_key.glb",
                "slots": [],
                "quest_item": True,
                "value": 0,
                "weight": 0.2
            },
            {
                "id": "core:item.death_notice",
                "name_key": "item.death_notice.name",
                "description_key": "item.death_notice.description",
                "category": "book",
                "icon": "assets/ui/items/death_notice.png",
                "world_model": "assets/models/items/form_27b_scroll.glb",
                "slots": [],
                "quest_item": True,
                "value": 0,
                "weight": 0.1,
                "book_text_key": "book.death_notice.text"
            },
            {
                "id": "core:item.form_27b",
                "name_key": "item.form_27b.name",
                "description_key": "item.form_27b.description",
                "category": "book",
                "icon": "assets/ui/items/form_27b.png",
                "world_model": "assets/models/items/form_27b_scroll.glb",
                "slots": [],
                "quest_item": True,
                "value": 0,
                "weight": 0.1,
                "book_text_key": "book.form_27b.text"
            },
            {
                "id": "core:item.uncounted_ledger",
                "name_key": "item.uncounted_ledger.name",
                "description_key": "item.uncounted_ledger.description",
                "category": "book",
                "icon": "assets/ui/items/uncounted_ledger.png",
                "world_model": "assets/models/items/spell_tome.glb",
                "slots": [],
                "quest_item": True,
                "value": 0,
                "weight": 1.2,
                "book_text_key": "book.uncounted_ledger.text"
            }
        ]
    })

    # 15. content/loot_tables/core_loot.json
    write_json("content/loot_tables/core_loot.json", {
        "schema_version": 1,
        "loot_tables": [
            {
                "id": "core:loot.vermin_drop",
                "gold_min": 2,
                "gold_max": 7,
                "entries": [
                    {"item_id": "core:item.bread_loaf", "weight": 35, "min_qty": 1, "max_qty": 1},
                    {"item_id": "core:item.health_potion", "weight": 20, "min_qty": 1, "max_qty": 1}
                ]
            },
            {
                "id": "core:loot.crypt_basic",
                "gold_min": 8,
                "gold_max": 22,
                "entries": [
                    {"item_id": "core:item.health_potion", "weight": 40, "min_qty": 1, "max_qty": 1},
                    {"item_id": "core:item.wooden_arrow", "weight": 45, "min_qty": 5, "max_qty": 10},
                    {"item_id": "core:item.lockpick", "weight": 30, "min_qty": 1, "max_qty": 2},
                    {"item_id": "core:item.rusted_sword", "weight": 15, "min_qty": 1, "max_qty": 1}
                ]
            },
            {
                "id": "core:loot.crypt_elite",
                "gold_min": 25,
                "gold_max": 55,
                "entries": [
                    {"item_id": "core:item.iron_longsword", "weight": 35, "min_qty": 1, "max_qty": 1},
                    {"item_id": "core:item.health_potion", "weight": 60, "min_qty": 1, "max_qty": 2},
                    {"item_id": "core:item.mana_potion", "weight": 50, "min_qty": 1, "max_qty": 2},
                    {"item_id": "core:item.iron_helm", "weight": 30, "min_qty": 1, "max_qty": 1}
                ]
            },
            {
                "id": "core:loot.crypt_boss",
                "gold_min": 80,
                "gold_max": 120,
                "guaranteed": ["core:item.form_27b", "core:item.uncounted_ledger", "core:item.ring_of_recall"],
                "entries": [
                    {"item_id": "core:item.health_potion", "weight": 100, "min_qty": 2, "max_qty": 2},
                    {"item_id": "core:item.mana_potion", "weight": 100, "min_qty": 2, "max_qty": 2}
                ]
            },
            {
                "id": "core:loot.secret_widowmaker",
                "gold_min": 50,
                "gold_max": 75,
                "guaranteed": ["core:item.widowmaker", "core:item.tome_veil"],
                "entries": []
            }
        ]
    })

    # 16. content/creatures/core_creatures.json
    write_json("content/creatures/core_creatures.json", {
        "schema_version": 1,
        "creatures": [
            {
                "id": "core:enemy.grave_rat",
                "name_key": "enemy.grave_rat.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/enemies/grave_rat.png",
                    "animation_data": "assets/animations/grave_rat.json",
                    "scale": 1.15
                },
                "stats": {
                    "health": 42,
                    "armor": 1,
                    "move_speed": 3.4,
                    "xp_reward": 18
                },
                "behavior": "melee_patroller",
                "perception": {"sight_meters": 11.0, "hearing_meters": 7.0},
                "attack": {
                    "name": "diseased_bite",
                    "damage": 7,
                    "reach_meters": 1.75,
                    "windup_seconds": 0.42,
                    "cooldown_seconds": 1.15
                },
                "loot_table": "core:loot.vermin_drop",
                "audio": {
                    "alert": "assets/audio/sfx/rat_squeak.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            },
            {
                "id": "core:enemy.restless_skeleton",
                "name_key": "enemy.restless_skeleton.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/enemies/skeleton.png",
                    "animation_data": "assets/animations/skeleton.json",
                    "scale": 1.75
                },
                "stats": {
                    "health": 90,
                    "armor": 3,
                    "move_speed": 2.4,
                    "xp_reward": 35
                },
                "behavior": "melee_patroller",
                "perception": {"sight_meters": 13.0, "hearing_meters": 8.0},
                "attack": {
                    "name": "skeleton_swing",
                    "damage": 12,
                    "reach_meters": 2.1,
                    "windup_seconds": 0.52,
                    "cooldown_seconds": 1.35
                },
                "loot_table": "core:loot.crypt_basic",
                "audio": {
                    "alert": "assets/audio/sfx/skeleton_alert.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            },
            {
                "id": "core:enemy.ash_crawler",
                "name_key": "enemy.ash_crawler.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/enemies/ash_crawler.png",
                    "animation_data": "assets/animations/ash_crawler.json",
                    "scale": 1.35
                },
                "stats": {
                    "health": 78,
                    "armor": 4,
                    "move_speed": 3.0,
                    "xp_reward": 30
                },
                "behavior": "melee_stalker",
                "perception": {"sight_meters": 12.0, "hearing_meters": 9.0},
                "attack": {
                    "name": "mandible_lunge",
                    "damage": 10,
                    "reach_meters": 1.9,
                    "windup_seconds": 0.45,
                    "cooldown_seconds": 1.2
                },
                "loot_table": "core:loot.crypt_basic",
                "audio": {
                    "alert": "assets/audio/sfx/crawler_hiss.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            },
            {
                "id": "core:enemy.lost_sentinel",
                "name_key": "enemy.lost_sentinel.name",
                "appearance": {
                    "type": "model_glb",
                    "model": "assets/models/characters/lost_sentinel.glb",
                    "scale": 1.0
                },
                "stats": {
                    "health": 170,
                    "armor": 7,
                    "move_speed": 1.95,
                    "xp_reward": 65
                },
                "behavior": "elite_guardian",
                "perception": {"sight_meters": 14.0, "hearing_meters": 9.0},
                "attack": {
                    "name": "halberd_cleave",
                    "damage": 19,
                    "reach_meters": 2.5,
                    "windup_seconds": 0.68,
                    "cooldown_seconds": 1.65
                },
                "loot_table": "core:loot.crypt_elite",
                "audio": {
                    "alert": "assets/audio/sfx/sentinel_clang.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/shield_block.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            },
            {
                "id": "core:enemy.crypt_keeper",
                "name_key": "enemy.crypt_keeper.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/enemies/crypt_keeper.png",
                    "animation_data": "assets/animations/crypt_keeper.json",
                    "scale": 2.05
                },
                "stats": {
                    "health": 280,
                    "armor": 5,
                    "move_speed": 2.25,
                    "xp_reward": 140
                },
                "behavior": "boss_archivist",
                "perception": {"sight_meters": 16.0, "hearing_meters": 12.0},
                "attack": {
                    "name": "erasure_bolt",
                    "damage": 18,
                    "reach_meters": 2.6,
                    "ranged_range_meters": 13.0,
                    "projectile_speed": 12.5,
                    "projectile_sprite": "assets/sprites/vfx/spell_arcane.png",
                    "windup_seconds": 0.65,
                    "cooldown_seconds": 1.55
                },
                "loot_table": "core:loot.crypt_boss",
                "audio": {
                    "alert": "assets/audio/sfx/boss_roar.wav",
                    "attack": "assets/audio/sfx/spell_cast.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            }
        ]
    })

    # 17. content/npcs/core_npcs.json
    write_json("content/npcs/core_npcs.json", {
        "schema_version": 1,
        "npcs": [
            {
                "id": "core:npc.clerk_oakhaven",
                "name_key": "npc.clerk_oakhaven.name",
                "title_key": "npc.clerk_oakhaven.title",
                "faction": "core:faction.bureau",
                "dialogue_id": "core:dialogue.clerk_oakhaven",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/clerk_oakhaven.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.75
                }
            },
            {
                "id": "core:npc.merchant_vaelen",
                "name_key": "npc.merchant_vaelen.name",
                "title_key": "npc.merchant_vaelen.title",
                "faction": "core:faction.bureau",
                "dialogue_id": "core:dialogue.merchant_vaelen",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/merchant_vaelen.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.75
                },
                "vendor_inventory": [
                    {"item_id": "core:item.health_potion", "stock": 8, "price": 18},
                    {"item_id": "core:item.mana_potion", "stock": 6, "price": 20},
                    {"item_id": "core:item.stamina_tonic", "stock": 6, "price": 15},
                    {"item_id": "core:item.wooden_arrow", "stock": 40, "price": 2},
                    {"item_id": "core:item.lockpick", "stock": 6, "price": 10},
                    {"item_id": "core:item.iron_longsword", "stock": 1, "price": 55},
                    {"item_id": "core:item.hunting_bow", "stock": 1, "price": 52},
                    {"item_id": "core:item.iron_shield", "stock": 1, "price": 42},
                    {"item_id": "core:item.chain_hauberk", "stock": 1, "price": 78},
                    {"item_id": "core:item.tome_ember", "stock": 1, "price": 55},
                    {"item_id": "core:item.tome_mend", "stock": 1, "price": 55},
                    {"item_id": "core:item.tome_ward", "stock": 1, "price": 50}
                ]
            },
            {
                "id": "core:npc.innkeeper_marta",
                "name_key": "npc.innkeeper_marta.name",
                "title_key": "npc.innkeeper_marta.title",
                "faction": "core:faction.ashbound",
                "dialogue_id": "core:dialogue.innkeeper_marta",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/innkeeper_marta.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.72
                }
            },
            {
                "id": "core:npc.librarian_fenwick",
                "name_key": "npc.librarian_fenwick.name",
                "title_key": "npc.librarian_fenwick.title",
                "faction": "core:faction.collegium",
                "dialogue_id": "core:dialogue.librarian_fenwick",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/librarian_fenwick.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.74
                }
            },
            {
                "id": "core:npc.brother_aldous",
                "name_key": "npc.brother_aldous.name",
                "title_key": "npc.brother_aldous.title",
                "faction": "core:faction.last_dawn",
                "dialogue_id": "core:dialogue.brother_aldous",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/brother_aldous.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.76
                }
            },
            {
                "id": "core:npc.ashbound_scout",
                "name_key": "npc.ashbound_scout.name",
                "title_key": "npc.ashbound_scout.title",
                "faction": "core:faction.ashbound",
                "dialogue_id": "core:dialogue.ashbound_scout",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/ashbound_scout.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.80
                }
            },
            {
                "id": "core:npc.erased_spirit",
                "name_key": "npc.erased_spirit.name",
                "title_key": "npc.erased_spirit.title",
                "faction": "core:faction.ashbound",
                "dialogue_id": "core:dialogue.erased_spirit",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "assets/sprites/npcs/erased_spirit.png",
                    "animation_data": "assets/animations/npc_standard.json",
                    "scale": 1.75
                }
            }
        ]
    })

    # 18. content/quests/chapter_zero_quests.json
    write_json("content/quests/chapter_zero_quests.json", {
        "schema_version": 1,
        "quests": [
            {
                "id": "core:quest.legally_deceased",
                "title_key": "quest.legally_deceased.title",
                "summary_key": "quest.legally_deceased.summary",
                "stages": [
                    {
                        "stage": 0,
                        "objective_key": "quest.legally_deceased.stage0",
                        "journal_key": "quest.legally_deceased.journal0"
                    },
                    {
                        "stage": 10,
                        "objective_key": "quest.legally_deceased.stage10",
                        "journal_key": "quest.legally_deceased.journal10"
                    },
                    {
                        "stage": 20,
                        "objective_key": "quest.legally_deceased.stage20",
                        "journal_key": "quest.legally_deceased.journal20"
                    },
                    {
                        "stage": 30,
                        "objective_key": "quest.legally_deceased.stage30",
                        "journal_key": "quest.legally_deceased.journal30"
                    },
                    {
                        "stage": 100,
                        "objective_key": "quest.legally_deceased.stage100",
                        "journal_key": "quest.legally_deceased.journal100",
                        "completed": True
                    },
                    {
                        "stage": 101,
                        "objective_key": "quest.legally_deceased.stage101",
                        "journal_key": "quest.legally_deceased.journal101",
                        "completed": True
                    }
                ]
            }
        ]
    })

    # 19. content/dialogue/chapter_zero_dialogue.json
    write_json("content/dialogue/chapter_zero_dialogue.json", {
        "schema_version": 1,
        "dialogues": [
            {
                "id": "core:dialogue.clerk_oakhaven",
                "root_node": "greeting",
                "nodes": {
                    "greeting": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.greeting",
                        "choices": [
                            {
                                "text_key": "dlg.clerk.choice_dead_notice",
                                "conditions": [{"type": "quest_stage_equals", "quest_id": "core:quest.legally_deceased", "stage": 0}],
                                "next": "explain_27b"
                            },
                            {
                                "text_key": "dlg.clerk.choice_have_proof",
                                "conditions": [{"type": "has_item", "item_id": "core:item.uncounted_ledger"}],
                                "next": "inspect_ledger"
                            },
                            {
                                "text_key": "dlg.clerk.choice_where_annex",
                                "conditions": [{"type": "quest_stage_at_least", "quest_id": "core:quest.legally_deceased", "stage": 10}],
                                "next": "annex_directions"
                            },
                            {
                                "text_key": "dlg.clerk.choice_race_dwarf",
                                "conditions": [{"type": "race_is", "race_id": "core:race.dwarf"}],
                                "next": "dwarf_remark"
                            },
                            {
                                "text_key": "dlg.clerk.choice_race_elf",
                                "conditions": [{"type": "race_is", "race_id": "core:race.elf"}],
                                "next": "elf_remark"
                            },
                            {
                                "text_key": "dlg.clerk.choice_leave",
                                "next": "END"
                            }
                        ]
                    },
                    "explain_27b": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.explain_27b",
                        "actions": [
                            {"type": "set_quest_stage", "quest_id": "core:quest.legally_deceased", "stage": 10},
                            {"type": "give_item", "item_id": "core:item.annex_key", "qty": 1},
                            {"type": "give_xp", "skill": "lore", "amount": 25}
                        ],
                        "choices": [
                            {"text_key": "dlg.clerk.choice_three_copies", "next": "annex_directions"},
                            {"text_key": "dlg.clerk.choice_persuade_fee", "conditions": [{"type": "skill_at_least", "skill": "persuasion", "value": 8}], "next": "persuade_stipend"}
                        ]
                    },
                    "persuade_stipend": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.persuade_stipend",
                        "actions": [
                            {"type": "give_gold", "amount": 35},
                            {"type": "give_xp", "skill": "persuasion", "amount": 35}
                        ],
                        "choices": [
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "annex_directions": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.annex_directions",
                        "choices": [
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "dwarf_remark": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.dwarf_remark",
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "greeting"}]
                    },
                    "elf_remark": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.elf_remark",
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "greeting"}]
                    },
                    "inspect_ledger": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.inspect_ledger",
                        "choices": [
                            {
                                "text_key": "dlg.clerk.choice_surrender_ledger",
                                "next": "ending_bureau"
                            },
                            {
                                "text_key": "dlg.clerk.choice_keep_ledger",
                                "next": "ending_independent"
                            }
                        ]
                    },
                    "ending_bureau": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.ending_bureau",
                        "actions": [
                            {"type": "take_item", "item_id": "core:item.uncounted_ledger", "qty": 1},
                            {"type": "set_quest_stage", "quest_id": "core:quest.legally_deceased", "stage": 100},
                            {"type": "set_flag", "flag": "chapter_zero_ending_bureau", "value": True},
                            {"type": "give_gold", "amount": 150},
                            {"type": "give_xp", "skill": "persuasion", "amount": 80}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_finish_chapter", "next": "END"}]
                    },
                    "ending_independent": {
                        "speaker_key": "npc.clerk_oakhaven.name",
                        "text_key": "dlg.clerk.ending_independent",
                        "actions": [
                            {"type": "set_quest_stage", "quest_id": "core:quest.legally_deceased", "stage": 101},
                            {"type": "set_flag", "flag": "chapter_zero_ending_ashbound", "value": True},
                            {"type": "give_gold", "amount": 90},
                            {"type": "give_xp", "skill": "lore", "amount": 100}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_finish_chapter", "next": "END"}]
                    }
                }
            },
            {
                "id": "core:dialogue.merchant_vaelen",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.merchant_vaelen.name",
                        "text_key": "dlg.merchant.greeting",
                        "choices": [
                            {"text_key": "dlg.merchant.choice_shop", "actions": [{"type": "open_shop"}], "next": "END"},
                            {"text_key": "dlg.merchant.choice_rumors", "next": "rumors"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "rumors": {
                        "speaker_key": "npc.merchant_vaelen.name",
                        "text_key": "dlg.merchant.rumors",
                        "choices": [
                            {"text_key": "dlg.merchant.choice_shop", "actions": [{"type": "open_shop"}], "next": "END"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    }
                }
            },
            {
                "id": "core:dialogue.innkeeper_marta",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.innkeeper_marta.name",
                        "text_key": "dlg.marta.greeting",
                        "choices": [
                            {"text_key": "dlg.marta.choice_remember_me", "next": "remember_witness"},
                            {"text_key": "dlg.marta.choice_rest", "actions": [{"type": "heal_player"}], "next": "rested"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "remember_witness": {
                        "speaker_key": "npc.innkeeper_marta.name",
                        "text_key": "dlg.marta.remember_witness",
                        "actions": [
                            {"type": "set_flag", "flag": "marta_testimony", "value": True},
                            {"type": "give_xp", "skill": "lore", "amount": 20}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "root"}]
                    },
                    "rested": {
                        "speaker_key": "npc.innkeeper_marta.name",
                        "text_key": "dlg.marta.rested",
                        "choices": [{"text_key": "dlg.clerk.choice_leave", "next": "END"}]
                    }
                }
            },
            {
                "id": "core:dialogue.librarian_fenwick",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.librarian_fenwick.name",
                        "text_key": "dlg.fenwick.greeting",
                        "choices": [
                            {"text_key": "dlg.fenwick.choice_ghosts", "next": "ghost_fees"},
                            {"text_key": "dlg.fenwick.choice_train_magic", "next": "train_magic"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "ghost_fees": {
                        "speaker_key": "npc.librarian_fenwick.name",
                        "text_key": "dlg.fenwick.ghost_fees",
                        "actions": [{"type": "give_xp", "skill": "lore", "amount": 25}],
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "root"}]
                    },
                    "train_magic": {
                        "speaker_key": "npc.librarian_fenwick.name",
                        "text_key": "dlg.fenwick.train_magic",
                        "actions": [
                            {"type": "give_xp", "skill": "elemental", "amount": 30},
                            {"type": "give_item", "item_id": "core:item.tome_glimmer", "qty": 1}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_leave", "next": "END"}]
                    }
                }
            },
            {
                "id": "core:dialogue.brother_aldous",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.brother_aldous.name",
                        "text_key": "dlg.aldous.greeting",
                        "choices": [
                            {"text_key": "dlg.aldous.choice_silence", "next": "great_silence"},
                            {"text_key": "dlg.aldous.choice_blessing", "actions": [{"type": "heal_player"}], "next": "blessed"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "great_silence": {
                        "speaker_key": "npc.brother_aldous.name",
                        "text_key": "dlg.aldous.great_silence",
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "root"}]
                    },
                    "blessed": {
                        "speaker_key": "npc.brother_aldous.name",
                        "text_key": "dlg.aldous.blessed",
                        "choices": [{"text_key": "dlg.clerk.choice_leave", "next": "END"}]
                    }
                }
            },
            {
                "id": "core:dialogue.ashbound_scout",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.ashbound_scout.name",
                        "text_key": "dlg.scout.greeting",
                        "choices": [
                            {"text_key": "dlg.scout.choice_annex", "next": "annex_warning"},
                            {"text_key": "dlg.scout.choice_orc_kinship", "conditions": [{"type": "race_is", "race_id": "core:race.orc"}], "next": "orc_gift"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "annex_warning": {
                        "speaker_key": "npc.ashbound_scout.name",
                        "text_key": "dlg.scout.annex_warning",
                        "actions": [
                            {"type": "set_quest_stage", "quest_id": "core:quest.legally_deceased", "stage": 20},
                            {"type": "give_xp", "skill": "perception", "amount": 25}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_leave", "next": "END"}]
                    },
                    "orc_gift": {
                        "speaker_key": "npc.ashbound_scout.name",
                        "text_key": "dlg.scout.orc_gift",
                        "actions": [{"type": "give_item", "item_id": "core:item.health_potion", "qty": 2}],
                        "choices": [{"text_key": "dlg.clerk.choice_back", "next": "root"}]
                    }
                }
            },
            {
                "id": "core:dialogue.erased_spirit",
                "root_node": "root",
                "nodes": {
                    "root": {
                        "speaker_key": "npc.erased_spirit.name",
                        "text_key": "dlg.spirit.greeting",
                        "choices": [
                            {"text_key": "dlg.spirit.choice_who", "next": "explain_prison"},
                            {"text_key": "dlg.clerk.choice_leave", "next": "END"}
                        ]
                    },
                    "explain_prison": {
                        "speaker_key": "npc.erased_spirit.name",
                        "text_key": "dlg.spirit.explain_prison",
                        "actions": [
                            {"type": "set_flag", "flag": "spirit_clue_learned", "value": True},
                            {"type": "give_item", "item_id": "core:item.crypt_key", "qty": 1},
                            {"type": "give_xp", "skill": "lore", "amount": 40}
                        ],
                        "choices": [{"text_key": "dlg.clerk.choice_leave", "next": "END"}]
                    }
                }
            }
        ]
    })

    # 20. content/localization/en.json
    write_json("content/localization/en.json", {
        "schema_version": 1,
        "language": "en",
        "strings": {
            "game.title": "THE UNCOUNTED",
            "game.subtitle": "Chapter Zero: Legally Deceased",
            "game.quote": "\"Some things are better left forgotten. Unfortunately, someone forgot why.\"",

            "attr.might.name": "Might",
            "attr.might.desc": "Physical power, melee impact, and carrying capacity.",
            "attr.agility.name": "Agility",
            "attr.agility.desc": "Balance, ranged accuracy, stealth, and stamina reserves.",
            "attr.endurance.name": "Endurance",
            "attr.endurance.desc": "Vitality, maximum health, and stamina recovery.",
            "attr.intellect.name": "Intellect",
            "attr.intellect.desc": "Arcane comprehension, spell power, and mana capacity.",
            "attr.will.name": "Will",
            "attr.will.desc": "Mental fortitude, restoration potency, and mana stability.",
            "attr.presence.name": "Presence",
            "attr.presence.desc": "Force of personality, persuasion, and barter terms.",

            "race.human.name": "Human",
            "race.human.desc": "Adaptable citizens of Edrath's fractured kingdoms.",
            "race.human.trait": "Quick Study (+8% Skill XP, +5 Persuasion & Lore)",
            "race.dwarf.name": "Dwarf",
            "race.dwarf.desc": "Deep-vault chroniclers and stone-wrights who remember older ledgers.",
            "race.dwarf.trait": "Stone Memory (+2 Endurance, +6 Lore, +5 Block)",
            "race.elf.name": "Elf",
            "race.elf.desc": "Long-lived observers sensitive to thin places left by the Great Silence.",
            "race.elf.trait": "Veil Sight (+2 Intellect, +6 Perception, +5 Elemental)",
            "race.orc.name": "Orc",
            "race.orc.desc": "Stalwart march-wardens and Ashbound pathfinders.",
            "race.orc.trait": "Iron Resolve (+2 Might, +6 Athletics, +4 Persuasion)",
            "race.halfling.name": "Halfling",
            "race.halfling.desc": "Nimble burrow-folk who slip past bureaucracy and locked doors alike.",
            "race.halfling.trait": "Quiet Footsteps (+2 Agility, +6 Stealth, +5 Lockpicking)",

            "bg.displaced_heir.name": "Displaced Heir",
            "bg.displaced_heir.desc": "Your family estate vanished from the county map overnight.",
            "bg.border_watch.name": "Border Watch Veteran",
            "bg.border_watch.desc": "You patrolled roads that occasionally stopped leading anywhere.",
            "bg.collegium_dropout.name": "Candle Collegium Dropout",
            "bg.collegium_dropout.desc": "Expelled for asking why the library's third floor only exists on Tuesdays.",
            "bg.tomb_surveyor.name": "Licensed Tomb Surveyor",
            "bg.tomb_surveyor.desc": "Contracted to inventory ruins before the Bureau seals them.",

            "arch.warrior.name": "Warrior",
            "arch.warrior.desc": "Starts with Longsword, Iron Shield, and Chain Hauberk. (No class lock)",
            "arch.ranger.name": "Ranger",
            "arch.ranger.desc": "Starts with Hunting Bow, Arrows, Blade, and Leather Jerkin. (No class lock)",
            "arch.mage.name": "Mage",
            "arch.mage.desc": "Starts with Oak Staff, Scholar Robe, Ember Bolt, and Ward. (No class lock)",
            "arch.rogue.name": "Rogue",
            "arch.rogue.desc": "Starts with Steel Dagger, Lockpicks, and the Veil spell. (No class lock)",
            "arch.cleric.name": "Cleric",
            "arch.cleric.desc": "Starts with Iron Mace, Shield, Hauberk, Mend, and Ward. (No class lock)",
            "arch.adventurer.name": "Adventurer",
            "arch.adventurer.desc": "Balanced blade, bow, lockpick, and starter magic package. (No class lock)",

            "skill.swords.name": "Blades & Melee",
            "skill.swords.desc": "Increases damage with swords, maces, and staves.",
            "skill.daggers.name": "Close Blades",
            "skill.daggers.desc": "Increases speed and critical precision with daggers.",
            "skill.bows.name": "Archery",
            "skill.bows.desc": "Increases ranged bow damage and projectile velocity.",
            "skill.block.name": "Block & Parry",
            "skill.block.desc": "Reduces damage taken while blocking and widens parry timing.",
            "skill.elemental.name": "Elemental Magic",
            "skill.elemental.desc": "Increases potency of Ember Bolt and Glimmer.",
            "skill.restoration.name": "Restoration",
            "skill.restoration.desc": "Increases healing from Mend and protection from Ward.",
            "skill.illusion.name": "Illusion",
            "skill.illusion.desc": "Enhances Veil duration and stealth effectiveness.",
            "skill.athletics.name": "Athletics",
            "skill.athletics.desc": "Improves sprint efficiency and movement speed.",
            "skill.perception.name": "Perception",
            "skill.perception.desc": "Helps spot hidden switches, traps, and distant threats.",
            "skill.stealth.name": "Stealth",
            "skill.stealth.desc": "Reduces enemy detection range while crouching or veiled.",
            "skill.lockpicking.name": "Lockpicking",
            "skill.lockpicking.desc": "Allows opening locked doors and chests with lockpicks.",
            "skill.persuasion.name": "Persuasion",
            "skill.persuasion.desc": "Unlocks diplomatic options and improves vendor prices.",
            "skill.lore.name": "Historical Lore",
            "skill.lore.desc": "Deciphers ancient ledgers and Great Silence inscriptions.",

            "synergy.spellblade.name": "Spellblade Conduit",
            "synergy.spellblade.desc": "Blades & Melee 10 + Elemental 10: Melee strikes deal +5 Fire damage and restore 3 Mana.",
            "synergy.bastion.name": "Sanctified Bastion",
            "synergy.bastion.desc": "Block 10 + Restoration 10: Passive +3 Armor and blocking attacks restores 4 Health.",
            "synergy.stalker.name": "Phantom Stalker",
            "synergy.stalker.desc": "Stealth 10 + Archery 10: +10% Move Speed and +35% Ranged sneak damage.",

            "faction.bureau.name": "Royal Bureau of Records",
            "faction.bureau.desc": "Clerks whose ledgers define legal reality across Edrath.",
            "faction.last_dawn.name": "Church of the Last Dawn",
            "faction.last_dawn.desc": "Devotees who preach that the gods saved creation during the Great Silence.",
            "faction.ashbound.name": "The Ashbound",
            "faction.ashbound.desc": "Seekers who excavate erased towns and preserve contradictory memories.",
            "faction.collegium.name": "The Candle Collegium",
            "faction.collegium.desc": "Arcane scholars debating the mechanism behind the Great Silence.",

            "spell.ember_bolt.name": "Ember Bolt",
            "spell.ember_bolt.desc": "Launches a searing bolt of condensed fire that illuminates dark halls.",
            "spell.mend.name": "Mend",
            "spell.mend.desc": "Knits wounds and restores flagging stamina.",
            "spell.ward.name": "Ward",
            "spell.ward.desc": "Sheathes the caster in a resonant arcane barrier (+8 Armor).",
            "spell.glimmer.name": "Glimmer",
            "spell.glimmer.desc": "Conjures a warm floating orb of lantern-light around the caster.",
            "spell.veil.name": "Veil",
            "spell.veil.desc": "Dulls sound and bends shadow, reducing enemy sight detection.",

            "item.rusted_sword.name": "Rusted Broadsword",
            "item.rusted_sword.description": "Pitted with rain, yet balanced enough to split bone.",
            "item.iron_longsword.name": "Bellwether Iron Longsword",
            "item.iron_longsword.description": "Standard watchman's steel forged in the northern hills.",
            "item.widowmaker.name": "The Widowmaker",
            "item.widowmaker.description": "Forged for King Edric's final battle. Unfortunately, Edric survived. His wife did not appreciate the name.",
            "item.steel_dagger.name": "Surveyor's Dirk",
            "item.steel_dagger.description": "A fast, narrow blade favored for close quarters and quiet work.",
            "item.iron_mace.name": "Flanged Iron Mace",
            "item.iron_mace.description": "Designed to dent ancient armor and shatter brittle ribs.",
            "item.oak_staff.name": "Collegium Focus Staff",
            "item.oak_staff.description": "Shod with iron and tipped with a resonant pale-blue Silence shard.",
            "item.hunting_bow.name": "Yew Hunting Bow",
            "item.hunting_bow.description": "A dependable recurve bow used by woodsmen along the Old Road.",
            "item.wooden_arrow.name": "Bodkin Arrow",
            "item.wooden_arrow.description": "Iron-tipped shaft capable of piercing bone and chitin.",
            "item.iron_shield.name": "Ironbanded Heater Shield",
            "item.iron_shield.description": "Sturdy oak reinforced with forged iron straps.",
            "item.leather_jerkin.name": "Boiled Leather Jerkin",
            "item.leather_jerkin.description": "Supple road armor that won't slow your stride.",
            "item.chain_hauberk.name": "Riveted Chain Hauberk",
            "item.chain_hauberk.description": "Heavy interlocking iron rings offering reliable protection.",
            "item.scholar_robe.name": "Collegium Archivist Robe",
            "item.scholar_robe.description": "Woven with silver thread that steadies the mind during casting.",
            "item.iron_helm.name": "Watchman's Kettle Helm",
            "item.iron_helm.description": "Deflects overhead blows and dripping cavern stalactites.",
            "item.traveler_boots.name": "Wayfarer's Dry-Stitched Boots",
            "item.traveler_boots.description": "Waxed against Bellwether's unending drizzle.",
            "item.ring_of_recall.name": "Ring of Unwritten Recall",
            "item.ring_of_recall.description": "Warm to the touch. You remember wearing it tomorrow.",
            "item.signet_ring.name": "Tarnished House Signet",
            "item.signet_ring.description": "Bears the crest of a manor that no longer appears on royal tax rolls.",
            "item.health_potion.name": "Crimson Draught",
            "item.health_potion.description": "Bitter herbal tincture that rapidly closes wounds (+35 Health).",
            "item.mana_potion.name": "Aether Phial",
            "item.mana_potion.description": "Distilled starlight and frost-mint that restores 30 Mana.",
            "item.stamina_tonic.name": "Wayfarer's Cordial",
            "item.stamina_tonic.description": "Brisk pine-resin tonic that restores 45 Stamina.",
            "item.bread_loaf.name": "Bellwether Crust Loaf",
            "item.bread_loaf.description": "Dense tavern bread baked by Marta. Best eaten warm.",
            "item.tome_ember.name": "Tome: Ember Bolt",
            "item.tome_ember.description": "Use from inventory to permanently learn the Ember Bolt spell.",
            "item.tome_mend.name": "Tome: Mend",
            "item.tome_mend.description": "Use from inventory to permanently learn the Mend spell.",
            "item.tome_ward.name": "Tome: Ward",
            "item.tome_ward.description": "Use from inventory to permanently learn the Ward spell.",
            "item.tome_glimmer.name": "Tome: Glimmer",
            "item.tome_glimmer.description": "Use from inventory to permanently learn the Glimmer spell.",
            "item.tome_veil.name": "Tome: Veil",
            "item.tome_veil.description": "Use from inventory to permanently learn the Veil spell.",
            "item.lockpick.name": "Tempered Lockpick",
            "item.lockpick.description": "Used to bypass mechanical locks when you lack the matching key.",
            "item.annex_key.name": "Brass Registry Annex Key",
            "item.annex_key.description": "Stamped with 'ARCHIVE III - DO NOT ENTER WITHOUT FORM 27-B'.",
            "item.crypt_key.name": "Cold-Iron Sanctum Key",
            "item.crypt_key.description": "Given by the Erased Spirit. Opens the inner vault of the Forgotten Crypt.",
            "item.death_notice.name": "Writ of Legal Decease",
            "item.death_notice.description": "Official notice declaring you died seventeen years ago and owe burial arrears.",
            "item.form_27b.name": "Form 27-B (Stamped)",
            "item.form_27b.description": "Application for Temporary Exemption from Being Dead. In triplicate.",
            "item.uncounted_ledger.name": "The Uncounted Ledger",
            "item.uncounted_ledger.description": "A heavy stone-vellum register recording events that have not yet occurred.",

            "book.death_notice.text": "ROYAL BUREAU OF RECORDS — DISTRICT OF BELLWETHER\n\nNotice of Administrative Decease:\nBe it known that the bearer of this writ expired seventeen (17) winters past. All chattels were auctioned to cover municipal interment fees. Remaining balance due: 142 crowns in unpaid burial tax.\n\nIf you wish to contest your deceased status, report immediately to Clerk Oakhaven at the Bellwether Registry Office and submit Form 27-B.",
            "book.form_27b.text": "FORM 27-B: APPLICATION FOR TEMPORARY EXEMPTION FROM BEING DEAD\n\nSection I: Applicant certifies under penalty of perjury that they are currently breathing, corporeal, and occupying no more than one (1) point in history.\nSection II: Attach corroborating ledger entry from Annex III.\n\n[Stamped in glowing pale ink: APPROVED BY ARCHIVIST MORVATH BEFORE THE GREAT SILENCE]",
            "book.uncounted_ledger.text": "THE UNCOUNTED LEDGER — FOLIO IX\n\n\"We did not erase the seven cities out of malice. When the flaw in the world's foundation widened, every name spoken aloud gave the Hunger another door. We struck their names from the Grand Register so the dark could not find them.\n\nYet the ink is fading. Today a traveler walked into Bellwether seventeen years after we hid their name to save their life. Worse still: the final page records that Bellwether itself will be uncounted at the next new moon unless the seal is renewed.\"",
            "book.tome_ember.text": "On the Ignition of Aether: Speak the syllable of cinder and project the spark outward.",
            "book.tome_mend.text": "Litany of the Dawn: Recall the body's unblemished pattern from yesterday's ledger.",
            "book.tome_ward.text": "Treatise on Abjuration: Fold ambient stone-memory into a shield before the blow lands.",
            "book.tome_glimmer.text": "Cantrip of the Archivist: A steady light that neither smokes nor scorches vellum.",
            "book.tome_veil.text": "Notes on Un-Noticing: Step between the lines of the observer's attention.",

            "enemy.grave_rat.name": "Grave Rat",
            "enemy.restless_skeleton.name": "Restless Skeleton",
            "enemy.ash_crawler.name": "Ash Crawler",
            "enemy.lost_sentinel.name": "Lost Sentinel",
            "enemy.crypt_keeper.name": "Archivist Shade Morvath",

            "npc.clerk_oakhaven.name": "Clerk Oakhaven",
            "npc.clerk_oakhaven.title": "Royal Bureau of Records",
            "npc.merchant_vaelen.name": "Vaelen the Quartermaster",
            "npc.merchant_vaelen.title": "Provisions & Oddities",
            "npc.innkeeper_marta.name": "Marta Kettleburn",
            "npc.innkeeper_marta.title": "Keeper of the Lantern Inn",
            "npc.librarian_fenwick.name": "Librarian Fenwick",
            "npc.librarian_fenwick.title": "Bellwether Municipal Library",
            "npc.brother_aldous.name": "Brother Aldous",
            "npc.brother_aldous.title": "Church of the Last Dawn",
            "npc.ashbound_scout.name": "Kaelen of the Ashbound",
            "npc.ashbound_scout.title": "Ruin Chronicler",
            "npc.erased_spirit.name": "The Uncounted Witness",
            "npc.erased_spirit.title": "Remnant of Annex III",

            "map.bellwether.name": "Bellwether Village",
            "map.old_road.name": "The Old Road",
            "map.registry_annex.name": "Registry Annex & Forgotten Crypt",

            "quest.legally_deceased.title": "Legally Deceased",
            "quest.legally_deceased.summary": "The Royal Bureau of Records insists you died seventeen years ago. Clear your name—or uncover why it was erased.",
            "quest.legally_deceased.stage0": "Speak with Clerk Oakhaven inside the Bellwether Records Office.",
            "quest.legally_deceased.journal0": "I arrived in Bellwether carrying a formal notice declaring that I died seventeen years ago and owe burial taxes. I should confront the local records clerk.",
            "quest.legally_deceased.stage10": "Travel east along the Old Road to the abandoned Registry Annex and retrieve Form 27-B.",
            "quest.legally_deceased.journal10": "Clerk Oakhaven informed me that I am legally dead and cannot file a correction without Form 27-B from the old Registry Annex east of town. He handed me the brass key to the Annex door.",
            "quest.legally_deceased.stage20": "Explore the Registry Annex & Forgotten Crypt to find Form 27-B and the truth behind the altered records.",
            "quest.legally_deceased.journal20": "Kaelen of the Ashbound warned me that the Registry Annex has physically shifted—its lower vaults now open into a pre-Silence crypt where names were deliberately erased.",
            "quest.legally_deceased.stage30": "Return to Clerk Oakhaven in Bellwether with Form 27-B and The Uncounted Ledger.",
            "quest.legally_deceased.journal30": "Deep beneath the Annex, I defeated the Archivist Shade and recovered both Form 27-B and The Uncounted Ledger—which reveals that names were erased to hide people from an ancient catastrophe, and Bellwether is next.",
            "quest.legally_deceased.stage100": "Chapter Zero Complete: You entrusted the Uncounted Ledger to the Royal Bureau.",
            "quest.legally_deceased.journal100": "I surrendered the Uncounted Ledger to Clerk Oakhaven. My legal existence is restored, and the Bureau has quietly dispatched riders to the capital—though I wonder whether they intend to repair the seal or bury the truth.",
            "quest.legally_deceased.stage101": "Chapter Zero Complete: You kept the Uncounted Ledger for the Ashbound.",
            "quest.legally_deceased.journal101": "I forced Clerk Oakhaven to stamp Form 27-B while keeping the Uncounted Ledger out of the Bureau's hands. I am legally alive again, and I hold the key to the Great Silence.",

            "dlg.clerk.greeting": "\"Name? ...Ah. Deceased. Seventeen years ago, third column from the bottom. Terribly sorry. If you're here to pay your burial arrears, the coffer is on the left.\"",
            "dlg.clerk.choice_dead_notice": "\"I'm standing right here. Breathing.\"",
            "dlg.clerk.explain_27b": "\"Yes, and that's highly irregular. You'll need Form 27-B: Application for Temporary Exemption from Being Dead. Three copies, please. Unfortunately, our last stack was stored in the Old Registry Annex down the eastern road before the floorboards started humming. Take this brass key and fetch a copy yourself.\"",
            "dlg.clerk.choice_three_copies": "\"Fine. Point me toward the Annex.\"",
            "dlg.clerk.choice_persuade_fee": "[Persuasion] \"If I'm retrieving Bureau property from a hazardous ruin, I'm entitled to a courier stipend.\"",
            "dlg.clerk.persuade_stipend": "Oakhaven blinks behind his spectacles, consults a subsection of the municipal code, and sighs. \"Sub-clause 14: Perilous Retrieval by a Non-Living Contractor. Very well. Thirty-five crowns in advance. Try not to die a second time; the paperwork is dreadful.\"",
            "dlg.clerk.choice_where_annex": "\"Remind me where the Registry Annex is.\"",
            "dlg.clerk.annex_directions": "\"Follow the cobbles east out of Bellwether onto the Old Road. Pass the ruined watch-arch and you'll find the Annex door set into the hillside.\"",
            "dlg.clerk.choice_race_dwarf": "[Dwarf] \"My clan's stone-rolls don't misplace a living person by seventeen years, clerk.\"",
            "dlg.clerk.dwarf_remark": "\"With respect to the mountain vaults, master dwarf, parchment is much more accommodating when history changes its mind.\"",
            "dlg.clerk.choice_race_elf": "[Elf] \"This ink smells of Silence-era abjuration, not clerical error.\"",
            "dlg.clerk.elf_remark": "Oakhaven lowers his voice. \"Then you understand why I don't go down into the Annex cellar myself.\"",
            "dlg.clerk.choice_have_proof": "\"I have Form 27-B—and this Uncounted Ledger from the vault beneath the Annex.\"",
            "dlg.clerk.inspect_ledger": "Oakhaven's ink-stained fingers tremble as he reads the stone-vellum pages. \"Merciful dawn... these entries are dated next month. It says the Great Silence wasn't an attack—it was an emergency erasure to keep something locked away, and the seal under Bellwether is failing. Give me that Ledger at once so I can seal it in the Royal Vault!\"",
            "dlg.clerk.choice_surrender_ledger": "\"Take the Ledger. The Bureau has the resources to warn the realm.\"",
            "dlg.clerk.choice_keep_ledger": "\"No. Stamp my Form 27-B, Oakhaven, and I'll take the Ledger to those who won't bury the truth.\"",
            "dlg.clerk.ending_bureau": "Oakhaven stamps Form 27-B with a resounding thud and locks the Ledger inside his iron safe. \"You are officially alive, citizen. Take this compensation from the Bureau treasury. When the High Chroniclers read this... Edrath will never be the same.\"",
            "dlg.clerk.ending_independent": "Oakhaven swallows hard, stamps your Form 27-B three times, and steps back. \"Legally, you exist again. Off the record? Run. If the Ledger is right, the road beyond Bellwether is waking up.\"",
            "dlg.clerk.choice_finish_chapter": "\"Thank you, Oakhaven.\"",
            "dlg.clerk.choice_back": "\"Let's return to the matter at hand.\"",
            "dlg.clerk.choice_leave": "\"I'll be going.\"",

            "dlg.merchant.greeting": "\"Welcome to Bellwether Provisions! Whether you're legally alive, administratively misplaced, or somewhere in between, your gold spends the same.\"",
            "dlg.merchant.choice_shop": "\"Show me your wares.\"",
            "dlg.merchant.choice_rumors": "\"Heard anything strange along the Old Road?\"",
            "dlg.merchant.rumors": "\"Caravan guards swear there used to be a whole toll-village two leagues east called Oakhallow. Last week the road-sign went blank, and now nobody can remember who lived there—except my ledger still shows they owe me for twelve barrels of salt.\"",

            "dlg.marta.greeting": "\"Come in out of the damp, traveler. The fire's warm, even if half the town is pretending the sky doesn't look wrong at dusk.\"",
            "dlg.marta.choice_remember_me": "\"Do you remember me, Marta? The Bureau claims I died seventeen years ago.\"",
            "dlg.marta.remember_witness": "Marta stares at you closely, rubbing her temples. \"I... I remember pouring ale for your father when you were a child—no, wait. Half the memory feels like pages torn out of a book. Something in that Annex down the Old Road is eating our yesterdays.\"",
            "dlg.marta.choice_rest": "\"Could I rest by the hearth a moment?\"",
            "dlg.marta.rested": "\"There now. Warm soup and a dry cloak do wonders for the living.\"",

            "dlg.fenwick.greeting": "\"Shh! Keep your voice down! And if you see a translucent gentleman shelving books in the history aisle, do NOT engage him.\"",
            "dlg.fenwick.choice_ghosts": "\"Is your library haunted?\"",
            "dlg.fenwick.ghost_fees": "\"Certainly not! Hauntings require municipal certification. Those apparitions are merely delinquent patrons who expired before paying their late fees—and until they settle three centuries of overdue fines, I refuse to acknowledge them!\"",
            "dlg.fenwick.choice_train_magic": "\"Can you teach me anything of Collegium magic?\"",
            "dlg.fenwick.train_magic": "\"A fellow seeker of illumination! Take this Glimmer primer and remember: light reveals what the ledgers try to hide.\"",

            "dlg.aldous.greeting": "\"May the Last Dawn keep your name written in the sun's memory, traveler.\"",
            "dlg.aldous.choice_silence": "\"What does the Church teach about the Great Silence?\"",
            "dlg.aldous.great_silence": "\"That the gods drew a curtain of mercy across a broken world. Though between you and me... curtains are meant to keep something out, not merely hide the view.\"",
            "dlg.aldous.choice_blessing": "\"I could use a blessing for the road ahead.\"",
            "dlg.aldous.blessed": "Aldous traces a warm golden circle above your brow. Your wounds ache less.",

            "dlg.scout.greeting": "\"Halt—ah, steady. You don't move like one of those bone-rattlers from the ruin. I'm Kaelen of the Ashbound.\"",
            "dlg.scout.choice_annex": "\"I'm heading into the Registry Annex for Form 27-B.\"",
            "dlg.scout.annex_warning": "\"Watch your footing inside. The upper offices collapsed into an older pre-Silence vault. Look for an iron wall-lever in the eastern archive to raise the crypt portcullis—and check the cracked northern wall if you have keen eyes.\"",
            "dlg.scout.choice_orc_kinship": "[Orc] \"Good to see another of the marches out here, Kaelen.\"",
            "dlg.scout.orc_gift": "\"Blood and stone, cousin! Take these healing draughts. Don't let the Bureau clerks write your story for you.\"",

            "dlg.spirit.greeting": "\"...Are you real? Or another line of ink waiting to be scraped from the vellum?\"",
            "dlg.spirit.choice_who": "\"Who are you? What happened in this vault?\"",
            "dlg.spirit.explain_prison": "\"I was an Archivist when the Great Silence fell. We built the Uncounted Vaults to hide living souls from the Unmaking—but Chief Archivist Morvath bound himself to the Ledger and went mad guarding it. Take this Cold-Iron Key. Open the northern sanctum, defeat Morvath's shade, and read the Ledger before Bellwether is erased next!\""
        }
    })


if __name__ == "__main__":
    build_all_content()
    print("Core JSON content generated.")


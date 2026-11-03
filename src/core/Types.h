#pragma once

#include <string>
#include <vector>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <cstdint>
#include "raylib.h"
#include "raymath.h"

namespace uncounted {

// ============================================================================
// Configuration Structs (loaded from config/*.json)
// ============================================================================
struct GraphicsConfig {
    int window_width = 1280;
    int window_height = 720;
    bool fullscreen = false;
    bool vsync = true;
    int target_fps = 60;
    std::string internal_resolution = "640x360";
    std::vector<std::string> available_internal_resolutions = {"320x180", "426x240", "640x360", "native"};
    bool integer_scaling = false;
    std::string texture_filter = "nearest";
    float fov_degrees = 75.0f;
    float ui_scale = 1.0f;
    bool fog_enabled = true;
    bool dynamic_lights_enabled = true;
};

struct ControlsConfig {
    float mouse_sensitivity = 0.16f;
    bool invert_y = false;
    bool head_bob = true;
    float head_bob_amount = 0.035f;
    std::map<std::string, std::string> bindings;
};

struct GameConfig {
    std::string language = "en";
    std::string difficulty = "standard";
    float master_volume = 0.85f;
    float music_volume = 0.65f;
    float ambience_volume = 0.70f;
    float sfx_volume = 0.85f;
    bool subtitles_enabled = true;
    float text_scale = 1.0f;   // dialogue / subtitles / books / narration size (1.0 - 1.5), for reading on stream
    bool enable_mods = false;
    std::string starting_map = "core:map.edrath";
    std::string starting_spawn = "village_gate";
    std::string starting_quest = "core:quest.legally_deceased";
};

// ============================================================================
// Content Definitions (loaded from content/**/*.json and mods/**/*.json)
// ============================================================================
struct DifficultyPreset {
    float player_damage_mult = 1.0f;
    float enemy_damage_mult = 1.0f;
};

struct BalancingDef {
    int base_health = 60;
    int health_per_endurance = 8;
    int base_stamina = 70;
    int stamina_per_endurance = 5;
    int stamina_per_agility = 3;
    int base_mana = 40;
    int mana_per_intellect = 6;
    int mana_per_will = 4;
    float base_carry_weight = 35.0f;
    float carry_weight_per_might = 4.5f;
    float stamina_regen_per_sec = 11.5f;
    float mana_regen_per_sec = 3.2f;
    float heavy_attack_damage_mult = 1.65f;
    float heavy_attack_stamina_mult = 1.75f;
    float block_damage_reduction = 0.65f;
    float parry_window_seconds = 0.25f;
    float parry_stamina_bonus = 12.0f;
    float skill_anti_exploit_cooldown_sec = 1.2f;
    float skill_diminishing_factor = 0.08f;
    std::map<std::string, DifficultyPreset> difficulties;
};

struct AttributeDef {
    std::string id;
    std::string name_key;
    std::string desc_key;
    int base = 10;
};

struct RaceDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    std::string portrait;
    std::map<std::string, int> attribute_modifiers;
    std::map<std::string, int> skill_bonuses;
    std::string trait_key;
    float xp_gain_multiplier = 1.0f;
};

struct BackgroundDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    int starting_gold = 25;
    std::map<std::string, int> skill_bonuses;
    std::vector<std::string> starting_items;
};

struct ArchetypeDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    std::map<std::string, int> attribute_bonuses;
    std::map<std::string, int> skill_bonuses;
    std::vector<std::string> starting_equipment;
    std::vector<std::string> starting_inventory;
    int starting_ammo = 0;
    std::vector<std::string> starting_spells;
};

struct SkillDef {
    std::string id;
    std::string domain;
    std::string name_key;
    std::string desc_key;
    float effect_per_point = 0.015f;
};

struct SynergyDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    std::map<std::string, int> requirements;
    std::map<std::string, float> bonuses;
};

struct FactionDef {
    std::string id;
    std::string name_key;
    std::string desc_key;
};

struct SpellEffectDef {
    std::string primitive; // projectile_damage, self_heal, buff_armor, buff_light, buff_stealth
    std::string damage_type = "fire";
    int base_power = 15;
    int stamina_restore = 0;
    float projectile_speed = 15.0f;
    std::string projectile_sprite;
    Vector3 light_color = {1.0f, 0.6f, 0.2f};
    float light_radius = 6.0f;
    float duration_seconds = 30.0f;
    float visibility_multiplier = 0.5f;
    float splash_radius = 0.0f;   // projectile_damage: also hurts other creatures within this radius of impact
    float drain_fraction = 0.0f;  // projectile_damage: heals the caster for this share of damage dealt
};

struct SpellDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    std::string icon;
    std::string skill = "elemental";
    int mana_cost = 10;
    float cooldown_seconds = 1.0f;
    std::string cast_sfx;
    SpellEffectDef effect;
};

struct WeaponStatsDef {
    bool is_weapon = false;
    std::string kind = "melee"; // melee or ranged
    std::string skill = "swords";
    std::string damage_type = "slashing";
    int base_damage = 10;
    float attack_time_seconds = 0.55f;
    float stamina_cost = 8.0f;
    float reach_meters = 2.1f;
    std::string ammo_item;
    float projectile_speed = 22.0f;
    // Traits
    float crit_chance = 0.0f;      // base chance per hit (0..1), before Agility / Perception / bonuses
    float crit_mult = 1.5f;        // damage multiplier on a critical hit
    float life_steal = 0.0f;       // share of damage dealt returned as health
    float mana_on_hit = 0.0f;      // mana restored per hit
    std::string bane_family;       // creature family this weapon is especially good against
    float bane_mult = 1.0f;
};

struct ItemEffectDef {
    // stat_bonus (attribute +amount), bonus (named build bonus +value, e.g. crit_chance_bonus),
    // consumable_heal, consumable_mana, consumable_stamina, learn_spell
    std::string type;
    std::string stat;
    std::string spell_id;
    int amount = 0;
    float value = 0.0f;
    float duration = 0.0f;   // buff: seconds the named bonus lasts (food)
};

struct ItemDef {
    std::string id;
    std::string name_key;
    std::string description_key;
    std::string category; // weapon, armor, accessory, consumable, book, key, ammo
    std::string icon;
    std::string world_model;
    std::vector<std::string> slots;
    bool stackable = false;
    bool quest_item = false;
    int value = 10;
    float weight = 1.0f;
    int armor = 0;
    std::string book_text_key;
    WeaponStatsDef weapon;
    std::vector<ItemEffectDef> effects;
};

struct LootEntryDef {
    std::string item_id;
    int weight = 50;
    int min_qty = 1;
    int max_qty = 1;
};

struct LootTableDef {
    std::string id;
    int gold_min = 0;
    int gold_max = 10;
    std::vector<std::string> guaranteed;
    std::vector<LootEntryDef> entries;
};

struct AppearanceDef {
    std::string type = "sprite_8dir"; // sprite_8dir, model_glb
    std::string sprite_sheet;
    std::string animation_data;
    std::string model;
    float scale = 1.5f;
};

struct CreatureAttackDef {
    std::string name;
    int damage = 10;
    float reach_meters = 2.0f;
    float ranged_range_meters = 0.0f;
    float projectile_speed = 12.0f;
    std::string projectile_sprite;
    float windup_seconds = 0.5f;
    float cooldown_seconds = 1.3f;
};

struct CreatureDef {
    std::string id;
    std::string name_key;
    AppearanceDef appearance;
    int health = 40;
    int armor = 2;
    float move_speed = 2.3f;
    int xp_reward = 30;
    std::string behavior = "melee_patroller";
    float sight_meters = 12.0f;
    float hearing_meters = 8.0f;
    CreatureAttackDef attack;
    std::string loot_table;
    std::string sfx_alert;
    std::string sfx_attack;
    std::string sfx_hit;
    std::string sfx_death;
    Color hit_color = {150, 140, 130, 255}; // particle colour when struck
    std::string alert_line_key;  // spoken (subtitled) on first noticing the player
    std::string death_line_key;
    bool hit_glow = false;
    std::string family;          // undead, beast, construct, spirit (weapon banes key off this)
};

struct VendorStockEntry {
    std::string item_id;
    int stock = 5;
    int price = 20;
};

struct NpcBarkDef {
    std::string text_key;
    std::string quest_id;      // optional gate
    int min_stage = -1000;
    int max_stage = 100000;
    std::string flag;          // optional: only once this story flag is set
    std::string not_flag;      // optional: only while this story flag is unset
};

struct CompanionLineDef {
    std::string text_key;
    std::string flag;       // only once this story flag is set
    std::string not_flag;   // only while this story flag is unset
};

// Optional: lets an NPC travel with the player (recruited/dismissed by dialogue actions).
struct CompanionDef {
    bool enabled = false;
    int damage = 6;                    // per swing, grows a little with the player's level
    float attack_time = 1.15f;
    float reach = 1.7f;
    int heal_amount = 18;              // handed over when the player is badly hurt
    float heal_cooldown = 45.0f;
    std::map<std::string, std::string> zone_lines;   // zone id -> line said on first arrival
    std::vector<CompanionLineDef> idle_lines;        // quiet-moment chatter
    std::vector<std::string> combat_lines;           // a fight starts
    std::vector<std::string> kill_lines;             // a fight ends
    std::vector<std::string> heal_lines;             // hands the player food
    std::vector<std::string> level_lines;            // the player levels up
    std::vector<std::string> catchup_lines;          // had to catch up (stuck behind a door, left on another floor)
    // Conversations with another companion, when both travel with the player. Each plays once per save.
    struct Banter {
        std::string id;
        std::string partner;                             // the other companion's NPC id
        std::vector<std::pair<bool, std::string>> lines; // (spoken by partner?, text key)
        std::string flag, not_flag;
    };
    std::vector<Banter> banter;
};

struct NpcDef {
    std::string id;
    std::string name_key;
    std::string title_key;
    std::string faction;
    std::string dialogue_id;
    AppearanceDef appearance;
    std::vector<VendorStockEntry> vendor_inventory;
    std::vector<NpcBarkDef> barks; // ambient lines spoken when the player passes by
    CompanionDef companion;
};

struct DialogueCondition {
    std::string type; // quest_stage_equals, quest_stage_at_least, has_item, race_is, skill_at_least, flag_set
    std::string quest_id;
    int stage = 0;
    std::string item_id;
    std::string race_id;
    std::string skill;
    int value = 0;
    std::string flag;
    std::vector<std::string> flags;   // flags_at_least: at least `value` of these are set
};

struct DialogueAction {
    std::string type; // set_quest_stage, give_item, take_item, give_gold, give_xp, set_flag, open_shop, heal_player
    std::string quest_id;
    int stage = 0;
    std::string item_id;
    int qty = 1;
    int amount = 0;
    std::string skill;
    std::string flag;
    bool bool_value = true;
    // narrate: full-screen cards; each shown only if its flag is set (empty = always)
    std::vector<std::pair<std::string, std::string>> pages;
};

struct DialogueChoice {
    std::string text_key;
    std::vector<DialogueCondition> conditions;
    std::vector<DialogueAction> actions;
    std::string next = "END";
    // Optional d20 check: success runs actions and goes to `next`, failure goes to `fail_next`.
    std::string roll_skill;       // bonus = skill / 4 (+ Presence modifier for persuasion)
    int roll_dc = 0;
    std::string fail_next = "END";
    bool roll_rigged = false;     // the first attempt is always a natural 1 (for comedy)
};

struct DialogueNode {
    std::string id;
    std::string speaker_key;
    std::string text_key;
    std::vector<DialogueAction> actions;
    std::vector<DialogueChoice> choices;
};

struct DialogueDef {
    std::string id;
    std::string root_node = "root";
    std::map<std::string, DialogueNode> nodes;
};

struct QuestStageDef {
    int stage = 0;
    std::string objective_key;
    std::string journal_key;
    bool completed = false;
    // Where to go: instance ids of NPCs, interactables or creatures (the nearest one still relevant is shown).
    std::vector<std::string> markers;
};

struct QuestDef {
    std::string id;
    std::string title_key;
    std::string summary_key;
    std::string campaign;   // campaign id: groups quests in the journal (chapters, side campaigns, tales)
    std::vector<QuestStageDef> stages;
};

// A campaign is a set of quests told together: a chapter of the main story, a side campaign, a collection of tales.
struct CampaignDef {
    std::string id;
    std::string name_key;
    std::string desc_key;
    std::string kind = "side";   // main, side, tales
    int order = 100;
};

// Map Definitions
struct MapSpawnDef {
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    float yaw_degrees = 0.0f;
};

struct MapPropDef {
    std::string id;
    std::string model;
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    float rot_y = 0.0f;
    Vector3 scale = {1.0f, 1.0f, 1.0f};
    Vector2 uv_scale = {1.0f, 1.0f};
    bool solid = true;
    // Optional animated emitter (flame sprite + point light) attached to the prop, offset in prop-local space.
    std::string ramp_dir;  // walkable slope rising toward "+x", "-x", "+z" or "-z" (stairs)
    std::string emitter_sprite;
    Vector3 emitter_offset = {0.0f, 0.0f, 0.0f};
    float emitter_size = 0.35f;
    Vector3 emitter_light_color = {0.0f, 0.0f, 0.0f};
    float emitter_light_radius = 0.0f;
};

struct MapLightDef {
    Vector3 pos = {0.0f, 2.5f, 0.0f};
    Vector3 color = {1.0f, 0.75f, 0.4f};
    float radius = 10.0f;
};

struct MapNpcSpawnDef {
    std::string instance_id;
    std::string npc_id;
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    float yaw = 0.0f;
    std::string requires_flag;   // only present once this story flag is set
    std::string hidden_flag;     // gone once this story flag is set
};

struct MapCreatureSpawnDef {
    std::string instance_id;
    std::string creature_id;
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    Vector3 patrol_a = {0.0f, 0.0f, 0.0f};
    Vector3 patrol_b = {0.0f, 0.0f, 0.0f};
    std::string requires_flag;    // spawns only once this story flag is set (appears live, mid-game)
    std::string group;            // when every creature of a group is dead...
    std::string group_quest_id;   // ...this quest moves to group_set_stage
    int group_set_stage = 0;
    std::string group_set_flag;   // ...and/or this flag is raised
};

struct MapInteractableDef {
    std::string instance_id;
    std::string type; // door, chest, lever, pressure_plate, readable, pickup, quest_pedestal
    std::string model;
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    float rot_y = 0.0f;
    bool locked = false;
    bool mechanism_only = false;
    std::string key_id;
    int lock_difficulty = 5;
    std::string target_id;
    std::string prompt;
    std::string title;
    std::string text;
    std::string loot_table;
    std::vector<std::string> fixed_items;
    std::string item_id;
    int qty = 1;
    std::string quest_id;
    int set_stage = 0;
    std::vector<std::string> grant_items;
    Vector3 scale = {1.0f, 1.0f, 1.0f};
    std::string set_flag;                    // flag raised when used (readables, pedestals)
    std::vector<std::string> narration_keys; // full-screen narration cards shown after use
    std::string requires_dead;               // creature instance that must be defeated before use
};

struct MapPortalDef {
    std::string id;
    Vector3 pos = {0.0f, 0.0f, 0.0f};
    float radius = 2.2f;
    std::string prompt;
    std::string destination_map;
    std::string destination_spawn;
};

// A region inside a map with its own atmosphere. Atmosphere blends across `blend` metres at the edges, so
// one continuous map can hold a village, a forest road and a crypt without loading screens.
struct MapZoneDef {
    std::string id;
    std::string display_name_key;
    Vector3 box_min = {0, 0, 0};
    Vector3 box_max = {0, 0, 0};
    float blend = 4.0f;
    std::string music;
    std::string ambience;
    std::string weather;
    Color sky_color = {20, 24, 36, 255};
    Vector3 ambient_color = {0.4f, 0.42f, 0.5f};
    Vector3 sun_direction = {-0.3f, 0.8f, -0.3f};
    Vector3 sun_color = {0.5f, 0.5f, 0.6f};
    Vector3 fog_color = {0.08f, 0.10f, 0.16f};
    float fog_density = 0.025f;
    // Optional story-driven change: once `override_flag` is set, weather/ambience switch (e.g. the rain stops).
    std::string override_flag;
    std::string override_weather;
    std::string override_ambience;
};

struct MapDef {
    std::string id;
    std::string display_name_key;
    std::string music;
    std::string ambience;
    Color sky_color = {20, 24, 36, 255};
    Vector3 ambient_color = {0.4f, 0.42f, 0.5f};
    Vector3 sun_direction = {-0.3f, 0.8f, -0.3f};
    Vector3 sun_color = {0.5f, 0.5f, 0.6f};
    Vector3 fog_color = {0.08f, 0.10f, 0.16f};
    float fog_density = 0.025f;
    std::string weather; // "", "rain", "dust"
    std::vector<MapZoneDef> zones;
    std::map<std::string, MapSpawnDef> spawns;
    std::vector<MapPropDef> props;
    std::vector<MapLightDef> lights;
    std::vector<MapNpcSpawnDef> npcs;
    std::vector<MapCreatureSpawnDef> creatures;
    std::vector<MapInteractableDef> interactables;
    std::vector<MapPortalDef> portals;
};

struct ValidationIssue {
    std::string file_path;
    std::string offending_key;
    std::string explanation;
    bool is_error = true;
};

} // namespace uncounted

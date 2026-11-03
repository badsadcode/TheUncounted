#include <set>
#include <algorithm>
#include "content/ContentRegistry.h"
#include "core/Logger.h"
#include "nlohmann/json.hpp"
#include <fstream>
#include <filesystem>

namespace fs = std::filesystem;
using json = nlohmann::json;

namespace uncounted {

static bool ReadJsonFile(const std::string& fullPath, json& outJson, std::string& outErr) {
    std::ifstream ifs(fullPath);
    if (!ifs.is_open()) {
        outErr = "Unable to open file on disk";
        return false;
    }
    try {
        ifs >> outJson;
        return true;
    } catch (const std::exception& e) {
        outErr = std::string("JSON syntax error: ") + e.what();
        return false;
    }
}

void ContentRegistry::RecordIssue(const std::string& file, const std::string& key, const std::string& reason, bool isError) {
    validation_issues.push_back({file, key, reason, isError});
    Logger::Validation(file, key, reason);
}

bool ContentRegistry::CheckFileExists(const std::string& rootDir, const std::string& relPath, const std::string& sourceContext, const std::string& keyName) {
    if (relPath.empty()) {
        RecordIssue(sourceContext, keyName, "Asset path is empty");
        return false;
    }
    fs::path p = fs::path(rootDir) / relPath;
    if (!fs::exists(p)) {
        RecordIssue(sourceContext, keyName, "Referenced external asset file does not exist: '" + relPath + "'");
        return false;
    }
    return true;
}

bool ContentRegistry::LoadConfigs(const std::string& rootDir) {
    json j;
    std::string err;

    // 1. graphics.json
    std::string gPath = (fs::path(rootDir) / "config/graphics.json").string();
    if (ReadJsonFile(gPath, j, err)) {
        graphics.window_width = j.value("window_width", 1280);
        graphics.window_height = j.value("window_height", 720);
        graphics.fullscreen = j.value("fullscreen", false);
        graphics.vsync = j.value("vsync", true);
        graphics.target_fps = j.value("target_fps", 60);
        graphics.internal_resolution = j.value("internal_resolution", "640x360");
        graphics.integer_scaling = j.value("integer_scaling", false);
        graphics.texture_filter = j.value("texture_filter", "nearest");
        graphics.fov_degrees = j.value("fov_degrees", 75.0f);
        graphics.ui_scale = j.value("ui_scale", 1.0f);
        graphics.fog_enabled = j.value("fog_enabled", true);
        graphics.dynamic_lights_enabled = j.value("dynamic_lights_enabled", true);
        graphics.retro_dither = j.value("retro_dither", true);
        graphics.glow = j.value("glow", true);
        graphics.glow_level = std::clamp(j.value("glow_level", graphics.glow ? 2 : 0), 0, 3);
        graphics.glow = graphics.glow_level > 0;
        graphics.world_motion = j.value("world_motion", true);
        graphics.screen_effect = j.value("screen_effect", "off");
        if (j.contains("available_internal_resolutions") && j["available_internal_resolutions"].is_array()) {
            graphics.available_internal_resolutions.clear();
            for (const auto& r : j["available_internal_resolutions"]) {
                graphics.available_internal_resolutions.push_back(r.get<std::string>());
            }
        }
    } else {
        RecordIssue("config/graphics.json", "root", err);
    }

    // 2. controls.json
    std::string cPath = (fs::path(rootDir) / "config/controls.json").string();
    if (ReadJsonFile(cPath, j, err)) {
        controls.mouse_sensitivity = j.value("mouse_sensitivity", 0.16f);
        controls.invert_y = j.value("invert_y", false);
        controls.head_bob = j.value("head_bob", true);
        controls.head_bob_amount = j.value("head_bob_amount", 0.035f);
        if (j.contains("bindings") && j["bindings"].is_object()) {
            for (auto it = j["bindings"].begin(); it != j["bindings"].end(); ++it) {
                controls.bindings[it.key()] = it.value().get<std::string>();
            }
        }
    } else {
        RecordIssue("config/controls.json", "root", err);
    }

    // 3. game.json
    std::string gmPath = (fs::path(rootDir) / "config/game.json").string();
    if (ReadJsonFile(gmPath, j, err)) {
        game_cfg.language = j.value("language", "en");
        game_cfg.difficulty = j.value("difficulty", "standard");
        game_cfg.master_volume = j.value("master_volume", 0.85f);
        game_cfg.music_volume = j.value("music_volume", 0.65f);
        game_cfg.ambience_volume = j.value("ambience_volume", 0.70f);
        game_cfg.sfx_volume = j.value("sfx_volume", 0.85f);
        game_cfg.subtitles_enabled = j.value("subtitles_enabled", true);
        game_cfg.text_scale = std::clamp(j.value("text_scale", 1.0f), 1.0f, 1.5f);
        game_cfg.day_length_minutes = std::clamp(j.value("day_length_minutes", 48.0f), 0.0f, 600.0f);
        game_cfg.enable_mods = j.value("enable_mods", false);
        game_cfg.starting_map = j.value("starting_map", "core:map.edrath");
        game_cfg.starting_spawn = j.value("starting_spawn", "village_gate");
        game_cfg.starting_quest = j.value("starting_quest", "core:quest.legally_deceased");
    } else {
        RecordIssue("config/game.json", "root", err);
    }

    return true;
}

bool ContentRegistry::SaveConfigs(const std::string& rootDir) const {
    {
        json j;
        j["schema_version"] = 1;
        j["window_width"] = graphics.window_width;
        j["window_height"] = graphics.window_height;
        j["fullscreen"] = graphics.fullscreen;
        j["vsync"] = graphics.vsync;
        j["target_fps"] = graphics.target_fps;
        j["internal_resolution"] = graphics.internal_resolution;
        j["available_internal_resolutions"] = graphics.available_internal_resolutions;
        j["integer_scaling"] = graphics.integer_scaling;
        j["texture_filter"] = graphics.texture_filter;
        j["fov_degrees"] = graphics.fov_degrees;
        j["ui_scale"] = graphics.ui_scale;
        j["fog_enabled"] = graphics.fog_enabled;
        j["dynamic_lights_enabled"] = graphics.dynamic_lights_enabled;
        j["retro_dither"] = graphics.retro_dither;
        j["glow"] = graphics.glow;
        j["glow_level"] = graphics.glow_level;
        j["world_motion"] = graphics.world_motion;
        j["screen_effect"] = graphics.screen_effect;
        std::ofstream ofs((fs::path(rootDir) / "config/graphics.json").string());
        if (ofs.is_open()) ofs << j.dump(2);
    }
    {
        json j;
        j["schema_version"] = 1;
        j["mouse_sensitivity"] = controls.mouse_sensitivity;
        j["invert_y"] = controls.invert_y;
        j["head_bob"] = controls.head_bob;
        j["head_bob_amount"] = controls.head_bob_amount;
        j["bindings"] = controls.bindings;
        std::ofstream ofs((fs::path(rootDir) / "config/controls.json").string());
        if (ofs.is_open()) ofs << j.dump(2);
    }
    {
        json j;
        j["schema_version"] = 1;
        j["language"] = game_cfg.language;
        j["difficulty"] = game_cfg.difficulty;
        j["master_volume"] = game_cfg.master_volume;
        j["music_volume"] = game_cfg.music_volume;
        j["ambience_volume"] = game_cfg.ambience_volume;
        j["sfx_volume"] = game_cfg.sfx_volume;
        j["subtitles_enabled"] = game_cfg.subtitles_enabled;
        j["text_scale"] = game_cfg.text_scale;
        j["day_length_minutes"] = game_cfg.day_length_minutes;
        j["enable_mods"] = game_cfg.enable_mods;
        j["starting_map"] = game_cfg.starting_map;
        j["starting_spawn"] = game_cfg.starting_spawn;
        j["starting_quest"] = game_cfg.starting_quest;
        std::ofstream ofs((fs::path(rootDir) / "config/game.json").string());
        if (ofs.is_open()) ofs << j.dump(2);
    }
    return true;
}

bool ContentRegistry::LoadAllContent(const std::string& rootDir, const std::vector<std::string>& extraModManifests) {
    loc_strings.clear();
    attributes.clear();
    races.clear();
    backgrounds.clear();
    archetypes.clear();
    skills.clear();
    synergies.clear();
    perks.clear();
    recipes.clear();
    factions.clear();
    spells_ordered.clear();
    spells.clear();
    items_ordered.clear();
    items.clear();
    loot_tables.clear();
    creatures_ordered.clear();
    creatures.clear();
    npcs.clear();
    dialogues.clear();
    quests.clear();
    campaigns.clear();
    maps.clear();
    validation_issues.clear();
    loaded_packs.clear();

    if (!LoadManifestFile(rootDir, "content/manifest.json")) {
        return false;
    }

    if (game_cfg.enable_mods) {
        // Every mods/<name>/manifest.json, in alphabetical order (later mods win when they redefine the same id).
        std::vector<std::string> mods;
        std::error_code ec;
        for (const auto& e : fs::directory_iterator(fs::path(rootDir) / "mods", ec))
            if (e.is_directory() && fs::exists(e.path() / "manifest.json"))
                mods.push_back("mods/" + e.path().filename().string() + "/manifest.json");
        std::sort(mods.begin(), mods.end());
        for (const auto& m : mods) {
            Logger::Info("Loading mod: " + m);
            LoadManifestFile(rootDir, m);
        }
    }

    for (const auto& modRel : extraModManifests) {
        LoadManifestFile(rootDir, modRel);
    }
    {   // Character portraits: any PNG in assets/ui/portraits ("<race>_<calling>_<n>.png" sorts them by race and calling)
        std::error_code pec;
        portraits.clear();
        for (const auto& e : fs::directory_iterator(fs::path(rootDir) / "assets" / "ui" / "portraits", pec))
            if (e.is_regular_file() && e.path().extension() == ".png")
                portraits.push_back("assets/ui/portraits/" + e.path().filename().string());
        std::sort(portraits.begin(), portraits.end());
    }
    LoadUserMaps(rootDir);    // maps you built in Blender (New Map): mods/user_maps/<name>/map.json, always on
    ApplyMapEdits(rootDir);   // your own Blender edits: always on (delete mods/level_edits/map_edits.json to undo them)
    ApplyPropPresets(rootDir); // fires burn and torches glow wherever they're placed (content/props/prop_presets.json)

    Logger::Info("Loaded " + std::to_string(items.size()) + " items, " +
                 std::to_string(creatures.size()) + " creatures, " +
                 std::to_string(spells.size()) + " spells, " +
                 std::to_string(npcs.size()) + " NPCs, " +
                 std::to_string(maps.size()) + " region maps.");
    return true;
}

bool ContentRegistry::LoadManifestFile(const std::string& rootDir, const std::string& manifestRelPath) {
    json m;
    std::string err;
    std::string fullPath = (fs::path(rootDir) / manifestRelPath).string();
    if (!ReadJsonFile(fullPath, m, err)) {
        RecordIssue(manifestRelPath, "manifest", err);
        return false;
    }

    std::string packName = m.value("pack_name", manifestRelPath);
    loaded_packs.push_back(packName);
    Logger::Info("Loading content pack: " + packName + " (" + manifestRelPath + ")");

    if (m.contains("localization")) {
        for (const auto& p : m["localization"]) LoadLocalizationFile(rootDir, p.get<std::string>());
    }

    if (m.contains("balancing")) {
        std::string bRel = m["balancing"].get<std::string>();
        json jb;
        if (ReadJsonFile((fs::path(rootDir) / bRel).string(), jb, err)) {
            balancing.base_health = jb.value("base_health", 60);
            balancing.health_per_endurance = jb.value("health_per_endurance", 8);
            balancing.base_stamina = jb.value("base_stamina", 70);
            balancing.stamina_per_endurance = jb.value("stamina_per_endurance", 5);
            balancing.stamina_per_agility = jb.value("stamina_per_agility", 3);
            balancing.base_mana = jb.value("base_mana", 40);
            balancing.mana_per_intellect = jb.value("mana_per_intellect", 6);
            balancing.mana_per_will = jb.value("mana_per_will", 4);
            balancing.base_carry_weight = jb.value("base_carry_weight", 35.0f);
            balancing.carry_weight_per_might = jb.value("carry_weight_per_might", 4.5f);
            balancing.stamina_regen_per_sec = jb.value("stamina_regen_per_sec", 11.5f);
            balancing.mana_regen_per_sec = jb.value("mana_regen_per_sec", 3.2f);
            balancing.heavy_attack_damage_mult = jb.value("heavy_attack_damage_mult", 1.65f);
            balancing.heavy_attack_stamina_mult = jb.value("heavy_attack_stamina_mult", 1.75f);
            balancing.block_damage_reduction = jb.value("block_damage_reduction", 0.65f);
            balancing.parry_window_seconds = jb.value("parry_window_seconds", 0.25f);
            balancing.parry_stamina_bonus = jb.value("parry_stamina_bonus", 12.0f);
            balancing.skill_anti_exploit_cooldown_sec = jb.value("skill_anti_exploit_cooldown_sec", 1.2f);
            balancing.skill_diminishing_factor = jb.value("skill_diminishing_factor", 0.08f);
            if (jb.contains("difficulties")) {
                for (auto it = jb["difficulties"].begin(); it != jb["difficulties"].end(); ++it) {
                    DifficultyPreset dp;
                    dp.player_damage_mult = it.value().value("player_damage_mult", 1.0f);
                    dp.enemy_damage_mult = it.value().value("enemy_damage_mult", 1.0f);
                    balancing.difficulties[it.key()] = dp;
                }
            }
        } else {
            RecordIssue(bRel, "root", err);
        }
    }

    if (m.contains("attributes")) {
        std::string rel = m["attributes"].get<std::string>();
        json ja;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), ja, err)) {
            for (const auto& el : ja["attributes"]) {
                AttributeDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.desc_key = el.value("desc_key", "");
                d.base = el.value("base", 10);
                attributes.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("races")) {
        std::string rel = m["races"].get<std::string>();
        json jr;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), jr, err)) {
            for (const auto& el : jr["races"]) {
                RaceDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.description_key = el.value("description_key", "");
                d.portrait = el.value("portrait", "");
                d.trait_key = el.value("trait_key", "");
                d.xp_gain_multiplier = el.value("xp_gain_multiplier", 1.0f);
                if (el.contains("attribute_modifiers")) {
                    for (auto it = el["attribute_modifiers"].begin(); it != el["attribute_modifiers"].end(); ++it)
                        d.attribute_modifiers[it.key()] = it.value().get<int>();
                }
                if (el.contains("skill_bonuses")) {
                    for (auto it = el["skill_bonuses"].begin(); it != el["skill_bonuses"].end(); ++it)
                        d.skill_bonuses[it.key()] = it.value().get<int>();
                }
                races.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("backgrounds")) {
        std::string rel = m["backgrounds"].get<std::string>();
        json jb;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), jb, err)) {
            for (const auto& el : jb["backgrounds"]) {
                BackgroundDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.description_key = el.value("description_key", "");
                d.starting_gold = el.value("starting_gold", 25);
                if (el.contains("skill_bonuses")) {
                    for (auto it = el["skill_bonuses"].begin(); it != el["skill_bonuses"].end(); ++it)
                        d.skill_bonuses[it.key()] = it.value().get<int>();
                }
                if (el.contains("starting_items")) {
                    for (const auto& it : el["starting_items"]) d.starting_items.push_back(it.get<std::string>());
                }
                backgrounds.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("archetypes")) {
        std::string rel = m["archetypes"].get<std::string>();
        json ja;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), ja, err)) {
            for (const auto& el : ja["archetypes"]) {
                ArchetypeDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.description_key = el.value("description_key", "");
                d.starting_ammo = el.value("starting_ammo", 0);
                if (el.contains("attribute_bonuses")) {
                    for (auto it = el["attribute_bonuses"].begin(); it != el["attribute_bonuses"].end(); ++it)
                        d.attribute_bonuses[it.key()] = it.value().get<int>();
                }
                if (el.contains("skill_bonuses")) {
                    for (auto it = el["skill_bonuses"].begin(); it != el["skill_bonuses"].end(); ++it)
                        d.skill_bonuses[it.key()] = it.value().get<int>();
                }
                if (el.contains("starting_equipment")) {
                    for (const auto& s : el["starting_equipment"]) d.starting_equipment.push_back(s.get<std::string>());
                }
                if (el.contains("starting_inventory")) {
                    for (const auto& s : el["starting_inventory"]) d.starting_inventory.push_back(s.get<std::string>());
                }
                if (el.contains("starting_spells")) {
                    for (const auto& s : el["starting_spells"]) d.starting_spells.push_back(s.get<std::string>());
                }
                archetypes.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("skills")) {
        std::string rel = m["skills"].get<std::string>();
        json js;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), js, err)) {
            for (const auto& el : js["skills"]) {
                SkillDef d;
                d.id = el.value("id", "");
                d.domain = el.value("domain", "combat");
                d.name_key = el.value("name_key", "");
                d.desc_key = el.value("desc_key", "");
                d.effect_per_point = el.value("effect_per_point", 0.015f);
                skills.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("synergies")) {
        std::string rel = m["synergies"].get<std::string>();
        json js;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), js, err)) {
            for (const auto& el : js["synergies"]) {
                SynergyDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.description_key = el.value("description_key", "");
                if (el.contains("requirements")) {
                    for (auto it = el["requirements"].begin(); it != el["requirements"].end(); ++it)
                        d.requirements[it.key()] = it.value().get<int>();
                }
                if (el.contains("bonuses")) {
                    for (auto it = el["bonuses"].begin(); it != el["bonuses"].end(); ++it)
                        d.bonuses[it.key()] = it.value().get<float>();
                }
                synergies.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("perks")) {
        std::string rel = m["perks"].get<std::string>();
        json jp;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), jp, err)) {
            for (const auto& el : jp["perks"]) {
                PerkDef d;
                d.id = el.value("id", "");
                d.skill = el.value("skill", "");
                d.level = el.value("level", 15);
                d.name_key = el.value("name_key", "");
                d.desc_key = el.value("desc_key", "");
                if (el.contains("bonuses"))
                    for (auto it = el["bonuses"].begin(); it != el["bonuses"].end(); ++it) d.bonuses[it.key()] = it.value().get<float>();
                perks.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("recipes")) {
        std::string rel = m["recipes"].get<std::string>();
        json jr;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), jr, err)) {
            for (const auto& el : jr["recipes"]) {
                RecipeDef d;
                d.id = el.value("id", "");
                d.station = el.value("station", "alchemy");
                d.result = el.value("result", "");
                d.qty = el.value("qty", 1);
                d.skill = el.value("skill", "");
                d.skill_level = el.value("skill_level", 0);
                d.book = el.value("book", "");
                if (el.contains("ingredients"))
                    for (const auto& ing : el["ingredients"]) d.ingredients.push_back({ing.value("item", ""), ing.value("qty", 1)});
                recipes.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("factions")) {
        std::string rel = m["factions"].get<std::string>();
        json jf;
        if (ReadJsonFile((fs::path(rootDir) / rel).string(), jf, err)) {
            for (const auto& el : jf["factions"]) {
                FactionDef d;
                d.id = el.value("id", "");
                d.name_key = el.value("name_key", "");
                d.desc_key = el.value("desc_key", "");
                factions.push_back(d);
            }
        } else RecordIssue(rel, "root", err);
    }

    if (m.contains("spells")) {
        for (const auto& p : m["spells"]) LoadSpellsFile(rootDir, p.get<std::string>());
    }
    if (m.contains("items")) {
        for (const auto& p : m["items"]) LoadItemsFile(rootDir, p.get<std::string>());
    }
    if (m.contains("loot_tables")) {
        for (const auto& p : m["loot_tables"]) LoadLootTablesFile(rootDir, p.get<std::string>());
    }
    if (m.contains("creatures")) {
        for (const auto& p : m["creatures"]) LoadCreaturesFile(rootDir, p.get<std::string>());
    }
    if (m.contains("npcs")) {
        for (const auto& p : m["npcs"]) LoadNpcsFile(rootDir, p.get<std::string>());
    }
    if (m.contains("dialogue")) {
        for (const auto& p : m["dialogue"]) LoadDialoguesFile(rootDir, p.get<std::string>());
    }
    if (m.contains("quests")) {
        for (const auto& p : m["quests"]) LoadQuestsFile(rootDir, p.get<std::string>());
    }
    if (m.contains("maps")) {
        for (const auto& p : m["maps"]) LoadMapFile(rootDir, p.get<std::string>());
    }

    return true;
}

void ContentRegistry::LoadLocalizationFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    if (!j.contains("strings") || !j["strings"].is_object()) {
        RecordIssue(relPath, "strings", "Missing 'strings' object in localization file");
        return;
    }
    for (auto it = j["strings"].begin(); it != j["strings"].end(); ++it) {
        loc_strings[it.key()] = it.value().get<std::string>();
    }
}

void ContentRegistry::LoadSpellsFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    for (const auto& el : j["spells"]) {
        SpellDef d;
        d.id = el.value("id", "");
        if (d.id.empty()) {
            RecordIssue(relPath, "id", "Spell definition is missing 'id'");
            continue;
        }
        d.name_key = el.value("name_key", "");
        d.description_key = el.value("description_key", "");
        d.icon = el.value("icon", "");
        d.skill = el.value("skill", "elemental");
        d.mana_cost = el.value("mana_cost", 10);
        d.cooldown_seconds = el.value("cooldown_seconds", 1.0f);
        d.cast_sfx = el.value("cast_sfx", "");
        if (el.contains("effect")) {
            const auto& ef = el["effect"];
            d.effect.primitive = ef.value("primitive", "projectile_damage");
            d.effect.damage_type = ef.value("damage_type", "fire");
            d.effect.base_power = ef.value("base_power", 15);
            d.effect.stamina_restore = ef.value("stamina_restore", 0);
            d.effect.projectile_speed = ef.value("projectile_speed", 15.0f);
            d.effect.projectile_sprite = ef.value("projectile_sprite", "");
            d.effect.light_radius = ef.value("light_radius", 6.0f);
            d.effect.duration_seconds = ef.value("duration_seconds", 30.0f);
            d.effect.visibility_multiplier = ef.value("visibility_multiplier", 0.5f);
            d.effect.splash_radius = ef.value("splash_radius", 0.0f);
            d.effect.drain_fraction = ef.value("drain_fraction", 0.0f);
            d.effect.status = ef.value("status", "");
            d.effect.status_power = ef.value("status_power", 0.0f);
            d.effect.status_duration = ef.value("status_duration", 0.0f);
            d.effect.status_chance = ef.value("status_chance", 1.0f);
            d.effect.chain_count = ef.value("chain_count", 0);
            d.effect.chain_range = ef.value("chain_range", 14.0f);
            d.effect.radius = ef.value("radius", 0.0f);
            d.effect.blink_distance = ef.value("blink_distance", 0.0f);
            d.effect.bonus_key = ef.value("bonus_key", "");
            d.effect.bonus_value = ef.value("bonus_value", 0.0f);
            if (ef.contains("light_color") && ef["light_color"].is_array() && ef["light_color"].size() == 3) {
                d.effect.light_color = {
                    ef["light_color"][0].get<float>(),
                    ef["light_color"][1].get<float>(),
                    ef["light_color"][2].get<float>()
                };
            }
        }
        if (spells.find(d.id) == spells.end()) {
            spells_ordered.push_back(d);
        } else {
            for (auto& existing : spells_ordered) {
                if (existing.id == d.id) existing = d;
            }
        }
        spells[d.id] = d;
    }
}

void ContentRegistry::LoadItemsFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    if (!j.contains("items") || !j["items"].is_array()) {
        RecordIssue(relPath, "items", "Missing 'items' array");
        return;
    }
    for (const auto& el : j["items"]) {
        ItemDef d;
        d.id = el.value("id", "");
        if (d.id.empty()) {
            RecordIssue(relPath, "id", "Item definition is missing required key 'id'");
            continue;
        }
        d.name_key = el.value("name_key", "");
        d.description_key = el.value("description_key", "");
        d.category = el.value("category", "misc");
        d.icon = el.value("icon", "");
        d.world_model = el.value("world_model", "");
        d.stackable = el.value("stackable", false);
        d.quest_item = el.value("quest_item", false);
        d.value = el.value("value", 10);
        d.weight = el.value("weight", 1.0f);
        d.armor = el.value("armor", 0);
        d.book_text_key = el.value("book_text_key", "");
        if (el.contains("slots") && el["slots"].is_array()) {
            for (const auto& s : el["slots"]) d.slots.push_back(s.get<std::string>());
        }
        if (el.contains("weapon") && el["weapon"].is_object()) {
            const auto& w = el["weapon"];
            d.weapon.is_weapon = true;
            d.weapon.kind = w.value("kind", "melee");
            d.weapon.skill = w.value("skill", "swords");
            d.weapon.damage_type = w.value("damage_type", "slashing");
            d.weapon.base_damage = w.value("base_damage", 10);
            d.weapon.attack_time_seconds = w.value("attack_time_seconds", 0.55f);
            d.weapon.stamina_cost = w.value("stamina_cost", 8.0f);
            d.weapon.reach_meters = w.value("reach_meters", 2.0f);
            d.weapon.ammo_item = w.value("ammo_item", "");
            d.weapon.projectile_speed = w.value("projectile_speed", 22.0f);
            d.weapon.crit_chance = w.value("crit_chance", 0.0f);
            d.weapon.crit_mult = w.value("crit_mult", 1.5f);
            d.weapon.life_steal = w.value("life_steal", 0.0f);
            d.weapon.mana_on_hit = w.value("mana_on_hit", 0.0f);
            d.weapon.bane_family = w.value("bane_family", "");
            d.weapon.bane_mult = w.value("bane_mult", 1.0f);
            d.weapon.on_hit_status = w.value("on_hit_status", "");
            d.weapon.status_chance = w.value("status_chance", 0.0f);
            d.weapon.status_power = w.value("status_power", 0.0f);
            d.weapon.status_duration = w.value("status_duration", 0.0f);
        }
        if (el.contains("effects") && el["effects"].is_array()) {
            for (const auto& ef : el["effects"]) {
                ItemEffectDef ie;
                ie.type = ef.value("type", "");
                ie.stat = ef.value("stat", "");
                ie.spell_id = ef.value("spell_id", "");
                ie.recipe_id = ef.value("recipe_id", "");
                ie.amount = ef.value("amount", 0);
                ie.value = ef.value("value", 0.0f);
                ie.duration = ef.value("duration", 0.0f);
                d.effects.push_back(ie);
            }
        }
        if (items.find(d.id) == items.end()) {
            items_ordered.push_back(d);
        } else {
            for (auto& existing : items_ordered) {
                if (existing.id == d.id) existing = d;
            }
        }
        items[d.id] = d;
    }
}

void ContentRegistry::LoadLootTablesFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    for (const auto& el : j["loot_tables"]) {
        LootTableDef d;
        d.id = el.value("id", "");
        d.gold_min = el.value("gold_min", 0);
        d.gold_max = el.value("gold_max", 10);
        if (el.contains("guaranteed")) {
            for (const auto& g : el["guaranteed"]) d.guaranteed.push_back(g.get<std::string>());
        }
        if (el.contains("entries")) {
            for (const auto& en : el["entries"]) {
                LootEntryDef le;
                le.item_id = en.value("item_id", "");
                le.weight = en.value("weight", 50);
                le.min_qty = en.value("min_qty", 1);
                le.max_qty = en.value("max_qty", 1);
                d.entries.push_back(le);
            }
        }
        loot_tables[d.id] = d;
    }
}

void ContentRegistry::LoadCreaturesFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    if (!j.contains("creatures") || !j["creatures"].is_array()) {
        RecordIssue(relPath, "creatures", "Missing 'creatures' array");
        return;
    }
    for (const auto& el : j["creatures"]) {
        CreatureDef d;
        d.id = el.value("id", "");
        if (d.id.empty()) {
            RecordIssue(relPath, "id", "Creature is missing 'id'");
            continue;
        }
        d.name_key = el.value("name_key", "");
        if (el.contains("appearance")) {
            const auto& ap = el["appearance"];
            d.appearance.type = ap.value("type", "sprite_8dir");
            d.appearance.sprite_sheet = ap.value("sprite_sheet", "");
            d.appearance.animation_data = ap.value("animation_data", "");
            d.appearance.model = ap.value("model", "");
            d.appearance.scale = ap.value("scale", 1.5f);
        }
        if (el.contains("stats")) {
            const auto& st = el["stats"];
            d.health = st.value("health", 40);
            d.armor = st.value("armor", 2);
            d.move_speed = st.value("move_speed", 2.3f);
            d.xp_reward = st.value("xp_reward", 30);
        }
        d.behavior = el.value("behavior", "melee_patroller");
        d.family = el.value("family", "");
        if (el.contains("perception")) {
            d.sight_meters = el["perception"].value("sight_meters", 12.0f);
            d.hearing_meters = el["perception"].value("hearing_meters", 8.0f);
        }
        if (el.contains("attack")) {
            const auto& at = el["attack"];
            d.attack.name = at.value("name", "strike");
            d.attack.damage = at.value("damage", 10);
            d.attack.reach_meters = at.value("reach_meters", 2.0f);
            d.attack.ranged_range_meters = at.value("ranged_range_meters", 0.0f);
            d.attack.projectile_speed = at.value("projectile_speed", 12.0f);
            d.attack.projectile_sprite = at.value("projectile_sprite", "");
            d.attack.windup_seconds = at.value("windup_seconds", 0.5f);
            d.attack.cooldown_seconds = at.value("cooldown_seconds", 1.3f);
            d.attack.sanity_damage = at.value("sanity_damage", 0);
        }
        d.loot_table = el.value("loot_table", "");
        if (el.contains("hit_fx") && el["hit_fx"].is_object()) {
            const auto& hf = el["hit_fx"];
            if (hf.contains("color") && hf["color"].is_array() && hf["color"].size() >= 3) {
                d.hit_color = {static_cast<unsigned char>(hf["color"][0].get<int>()), static_cast<unsigned char>(hf["color"][1].get<int>()),
                               static_cast<unsigned char>(hf["color"][2].get<int>()), 255};
            }
            d.hit_glow = hf.value("glow", false);
        }
        if (el.contains("lines") && el["lines"].is_object()) {
            d.alert_line_key = el["lines"].value("alert", "");
            d.death_line_key = el["lines"].value("death", "");
        }
        if (el.contains("audio")) {
            const auto& au = el["audio"];
            d.sfx_alert = au.value("alert", "");
            d.sfx_attack = au.value("attack", "");
            d.sfx_hit = au.value("hit", "");
            d.sfx_death = au.value("death", "");
        }

        if (creatures.find(d.id) == creatures.end()) {
            creatures_ordered.push_back(d);
        } else {
            for (auto& existing : creatures_ordered) {
                if (existing.id == d.id) existing = d;
            }
        }
        creatures[d.id] = d;
    }
}

void ContentRegistry::LoadNpcsFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    for (const auto& el : j["npcs"]) {
        NpcDef d;
        d.id = el.value("id", "");
        d.name_key = el.value("name_key", "");
        d.title_key = el.value("title_key", "");
        d.faction = el.value("faction", "");
        d.dialogue_id = el.value("dialogue_id", "");
        if (el.contains("appearance")) {
            const auto& ap = el["appearance"];
            d.appearance.type = ap.value("type", "sprite_8dir");
            d.appearance.sprite_sheet = ap.value("sprite_sheet", "");
            d.appearance.animation_data = ap.value("animation_data", "");
            d.appearance.model = ap.value("model", "");
            d.appearance.scale = ap.value("scale", 1.75f);
        }
        if (el.contains("barks") && el["barks"].is_array()) {
            for (const auto& bj : el["barks"]) {
                NpcBarkDef b;
                b.text_key = bj.value("text_key", "");
                b.quest_id = bj.value("quest_id", "");
                b.min_stage = bj.value("min_stage", -1000);
                b.max_stage = bj.value("max_stage", 100000);
                b.flag = bj.value("flag", "");
                b.not_flag = bj.value("not_flag", "");
                d.barks.push_back(b);
            }
        }
        if (el.contains("companion") && el["companion"].is_object()) {
            const auto& cj = el["companion"];
            CompanionDef& cd = d.companion;
            cd.enabled = true;
            cd.damage = cj.value("damage", 6);
            cd.attack_time = cj.value("attack_time", 1.15f);
            cd.reach = cj.value("reach", 1.7f);
            cd.heal_amount = cj.value("heal_amount", 18);
            cd.heal_cooldown = cj.value("heal_cooldown", 45.0f);
            if (cj.contains("zone_lines")) cd.zone_lines = cj["zone_lines"].get<std::map<std::string, std::string>>();
            auto strs = [&](const char* k) { return cj.contains(k) ? cj[k].get<std::vector<std::string>>() : std::vector<std::string>{}; };
            cd.combat_lines = strs("combat_lines");
            cd.kill_lines = strs("kill_lines");
            cd.heal_lines = strs("heal_lines");
            cd.level_lines = strs("level_lines");
            cd.catchup_lines = strs("catchup_lines");
            if (cj.contains("banter")) {
                for (const auto& bj : cj["banter"]) {
                    CompanionDef::Banter b;
                    b.id = bj.value("id", "");
                    b.partner = bj.value("partner", "");
                    b.flag = bj.value("flag", "");
                    b.not_flag = bj.value("not_flag", "");
                    for (const auto& lj : bj["lines"]) b.lines.push_back({lj.value("by", "self") == "partner", lj.value("text_key", "")});
                    cd.banter.push_back(b);
                }
            }
            if (cj.contains("idle_lines")) {
                for (const auto& lj : cj["idle_lines"]) {
                    CompanionLineDef l;
                    l.text_key = lj.value("text_key", "");
                    l.flag = lj.value("flag", "");
                    l.not_flag = lj.value("not_flag", "");
                    cd.idle_lines.push_back(l);
                }
            }
        }
        if (el.contains("vendor_inventory")) {
            for (const auto& v : el["vendor_inventory"]) {
                VendorStockEntry vs;
                vs.item_id = v.value("item_id", "");
                vs.stock = v.value("stock", 5);
                vs.price = v.value("price", 20);
                d.vendor_inventory.push_back(vs);
            }
        }
        npcs[d.id] = d;
    }
}

static DialogueAction ParseAction(const json& a) {
    DialogueAction da;
    da.type = a.value("type", "");
    da.quest_id = a.value("quest_id", "");
    da.stage = a.value("stage", 0);
    da.item_id = a.value("item_id", "");
    da.qty = a.value("qty", 1);
    da.amount = a.value("amount", 0);
    da.skill = a.value("skill", "");
    da.flag = a.value("flag", "");
    da.bool_value = a.value("value", true);
    da.spawn = a.value("spawn", "");
    da.spell_id = a.value("spell_id", "");
    if (a.contains("pages")) {
        for (const auto& pj : a["pages"]) {
            if (pj.is_string()) da.pages.push_back({pj.get<std::string>(), ""});
            else da.pages.push_back({pj.value("key", ""), pj.value("flag", "")});
        }
    }
    return da;
}

void ContentRegistry::LoadDialoguesFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    for (const auto& el : j["dialogues"]) {
        DialogueDef d;
        d.id = el.value("id", "");
        d.root_node = el.value("root_node", "root");
        if (el.contains("nodes") && el["nodes"].is_object()) {
            for (auto it = el["nodes"].begin(); it != el["nodes"].end(); ++it) {
                DialogueNode dn;
                dn.id = it.key();
                const auto& nj = it.value();
                dn.speaker_key = nj.value("speaker_key", "");
                dn.text_key = nj.value("text_key", "");
                if (nj.contains("actions")) {
                    for (const auto& a : nj["actions"]) dn.actions.push_back(ParseAction(a));
                }
                if (nj.contains("choices")) {
                    for (const auto& cj : nj["choices"]) {
                        DialogueChoice dc;
                        dc.text_key = cj.value("text_key", "");
                        dc.next = cj.value("next", "END");
                        if (cj.contains("roll") && cj["roll"].is_object()) {
                            dc.roll_skill = cj["roll"].value("skill", "persuasion");
                            dc.roll_dc = cj["roll"].value("dc", 10);
                            dc.fail_next = cj["roll"].value("fail_next", "END");
                            dc.roll_rigged = cj["roll"].value("rigged", false);
                        }
                        if (cj.contains("conditions")) {
                            for (const auto& condj : cj["conditions"]) {
                                DialogueCondition cond;
                                cond.type = condj.value("type", "");
                                cond.quest_id = condj.value("quest_id", "");
                                cond.stage = condj.value("stage", 0);
                                cond.item_id = condj.value("item_id", "");
                                cond.race_id = condj.value("race_id", "");
                                cond.skill = condj.value("skill", "");
                                cond.value = condj.value("value", 0);
                                cond.flag = condj.value("flag", "");
                                if (condj.contains("flags")) cond.flags = condj["flags"].get<std::vector<std::string>>();
                                dc.conditions.push_back(cond);
                            }
                        }
                        if (cj.contains("actions")) {
                            for (const auto& a : cj["actions"]) dc.actions.push_back(ParseAction(a));
                        }
                        dn.choices.push_back(dc);
                    }
                }
                d.nodes[dn.id] = dn;
            }
        }
        dialogues[d.id] = d;
    }
}

void ContentRegistry::LoadQuestsFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    for (const auto& el : j["quests"]) {
        QuestDef d;
        d.id = el.value("id", "");
        d.title_key = el.value("title_key", "");
        d.summary_key = el.value("summary_key", "");
        d.campaign = el.value("campaign", "");
        if (el.contains("stages")) {
            for (const auto& sj : el["stages"]) {
                QuestStageDef qs;
                qs.stage = sj.value("stage", 0);
                qs.objective_key = sj.value("objective_key", "");
                qs.journal_key = sj.value("journal_key", "");
                qs.completed = sj.value("completed", false);
                if (sj.contains("markers")) qs.markers = sj["markers"].get<std::vector<std::string>>();
                d.stages.push_back(qs);
            }
        }
        quests[d.id] = d;
    }
    if (j.contains("campaigns")) {
        for (const auto& cj : j["campaigns"]) {
            CampaignDef c;
            c.id = cj.value("id", "");
            c.name_key = cj.value("name_key", "");
            c.desc_key = cj.value("desc_key", "");
            c.kind = cj.value("kind", "side");
            c.order = cj.value("order", 100);
            campaigns.erase(std::remove_if(campaigns.begin(), campaigns.end(), [&](const CampaignDef& o) { return o.id == c.id; }), campaigns.end());
            campaigns.push_back(c);
        }
        std::sort(campaigns.begin(), campaigns.end(), [](const CampaignDef& a, const CampaignDef& b) { return a.order < b.order; });
    }
}

const CampaignDef* ContentRegistry::GetCampaign(const std::string& id) const {
    for (const auto& c : campaigns) if (c.id == id) return &c;
    return nullptr;
}

static Vector3 JsonToVec3(const json& j, Vector3 fallback = {0.0f, 0.0f, 0.0f}) {
    if (j.is_array() && j.size() >= 3) {
        return {j[0].get<float>(), j[1].get<float>(), j[2].get<float>()};
    }
    return fallback;
}

static MapNpcSpawnDef NpcSpawnFromJson(const json& nj) {
    MapNpcSpawnDef ns;
    ns.instance_id = nj.value("instance_id", "");
    ns.npc_id = nj.value("npc_id", "");
    ns.pos = JsonToVec3(nj["pos"]);
    ns.yaw = nj.value("yaw", 0.0f);
    ns.requires_flag = nj.value("requires_flag", "");
    ns.hidden_flag = nj.value("hidden_flag", "");
    if (nj.contains("hours") && nj["hours"].is_array() && nj["hours"].size() == 2) {
        ns.hours_from = nj["hours"][0].get<float>();
        ns.hours_to = nj["hours"][1].get<float>();
    }
    return ns;
}

static MapCreatureSpawnDef CreatureSpawnFromJson(const json& cj) {
    MapCreatureSpawnDef cs;
    cs.instance_id = cj.value("instance_id", "");
    cs.creature_id = cj.value("creature_id", "");
    cs.pos = JsonToVec3(cj["pos"]);
    cs.patrol_a = cj.contains("patrol_a") ? JsonToVec3(cj["patrol_a"]) : cs.pos;
    cs.patrol_b = cj.contains("patrol_b") ? JsonToVec3(cj["patrol_b"]) : cs.pos;
    cs.requires_flag = cj.value("requires_flag", "");
    cs.group = cj.value("group", "");
    cs.group_quest_id = cj.value("group_quest_id", "");
    cs.group_set_stage = cj.value("group_set_stage", 0);
    cs.group_set_flag = cj.value("group_set_flag", "");
    return cs;
}

static MapInteractableDef InteractableFromJson(const json& ij) {
    MapInteractableDef in;
    in.instance_id = ij.value("instance_id", "");
    in.type = ij.value("type", "prop");
    in.model = ij.value("model", "");
    in.pos = JsonToVec3(ij["pos"]);
    in.rot_y = ij.value("rot_y", 0.0f);
    in.locked = ij.value("locked", false);
    in.mechanism_only = ij.value("mechanism_only", false);
    in.key_id = ij.value("key_id", "");
    in.lock_difficulty = ij.value("lock_difficulty", 5);
    in.target_id = ij.value("target_id", "");
    in.prompt = ij.value("prompt", "Interact");
    in.title = ij.value("title", "");
    in.text = ij.value("text", "");
    in.loot_table = ij.value("loot_table", "");
    if (ij.contains("fixed_items")) {
        for (const auto& fi : ij["fixed_items"]) in.fixed_items.push_back(fi.get<std::string>());
    }
    in.item_id = ij.value("item_id", "");
    in.qty = ij.value("qty", 1);
    in.quest_id = ij.value("quest_id", "");
    in.set_stage = ij.value("set_stage", 0);
    if (ij.contains("grant_items")) {
        for (const auto& gi : ij["grant_items"]) in.grant_items.push_back(gi.get<std::string>());
    }
    if (ij.contains("scale")) in.scale = JsonToVec3(ij["scale"], {1.0f, 1.0f, 1.0f});
    in.set_flag = ij.value("set_flag", "");
    in.sanity = ij.value("sanity", 0);
    in.requires_dead = ij.value("requires_dead", "");
    in.qty_max = ij.value("qty_max", 0);
    in.respawn_seconds = ij.value("respawn_seconds", 600.0f);
    in.station = ij.value("station", "");
    in.requires_flag = ij.value("requires_flag", "");
    in.hidden_flag = ij.value("hidden_flag", "");
    if (ij.contains("narration") && ij["narration"].is_array())
        for (const auto& nk : ij["narration"]) in.narration_keys.push_back(nk.get<std::string>());
    return in;
}

static MapPortalDef PortalFromJson(const json& pj) {
    MapPortalDef pt;
    pt.id = pj.value("id", "");
    pt.pos = JsonToVec3(pj["pos"]);
    pt.radius = pj.value("radius", 2.2f);
    pt.prompt = pj.value("prompt", "Travel");
    pt.destination_map = pj.value("destination_map", "");
    pt.destination_spawn = pj.value("destination_spawn", "");
    return pt;
}

static MapPropDef PropFromJson(const json& pj) {
    MapPropDef p;
    p.id = pj.value("id", "");
    p.model = pj.value("model", "");
    p.pos = JsonToVec3(pj["pos"]);
    p.rot_y = pj.value("rot_y", 0.0f);
    if (pj.contains("scale")) p.scale = JsonToVec3(pj["scale"], {1.0f, 1.0f, 1.0f});
    if (pj.contains("uv_scale") && pj["uv_scale"].is_array() && pj["uv_scale"].size() >= 2) {
        p.uv_scale = {pj["uv_scale"][0].get<float>(), pj["uv_scale"][1].get<float>()};
    }
    p.solid = pj.value("solid", true);
    p.invisible = pj.value("invisible", false);
    p.ramp_dir = pj.value("ramp", "");
    if (pj.contains("emitter") && pj["emitter"].is_object()) {
        const auto& ej = pj["emitter"];
        p.emitter_sprite = ej.value("sprite", "");
        if (ej.contains("offset")) p.emitter_offset = JsonToVec3(ej["offset"]);
        p.emitter_size = ej.value("size", 0.35f);
        if (ej.contains("light_color")) p.emitter_light_color = JsonToVec3(ej["light_color"]);
        p.emitter_light_radius = ej.value("light_radius", 0.0f);
    }
    return p;
}

// Level edits made in Blender (tools/blender/uncounted_level_editor.py): every mods/<name>/map_edits.json, in
// alphabetical order, modifies/adds/removes props and moves NPCs, creatures and objects of one map. Kept out of the
// generated level files so rebuilding the world never overwrites them.
void ContentRegistry::ApplyPropPresets(const std::string& rootDir) {
    const fs::path path = fs::path(rootDir) / "content" / "props" / "prop_presets.json";
    if (!fs::exists(path)) return;
    json root;
    try {
        std::ifstream f(path);
        root = json::parse(f);
    } catch (const std::exception& e) {
        RecordIssue("content/props/prop_presets.json", "json", std::string("Invalid JSON: ") + e.what());
        return;
    }
    if (!root.contains("presets") || !root["presets"].is_object()) return;
    std::unordered_map<std::string, MapPropDef> presets;
    for (auto it = root["presets"].begin(); it != root["presets"].end(); ++it) {
        json pj = it.value();
        pj["id"] = "preset";
        pj["model"] = it.key();
        pj["pos"] = json::array({0, 0, 0});
        presets[it.key()] = PropFromJson(pj);
        const auto& pr = presets[it.key()];
        if (!pr.emitter_sprite.empty()) CheckFileExists(rootDir, pr.emitter_sprite, "PropPreset:" + it.key(), "emitter.sprite");
    }
    for (auto& [id, m] : maps) {
        for (auto& p : m.props) {
            auto it = presets.find(p.model);
            if (it == presets.end() || !p.emitter_sprite.empty() || p.emitter_light_radius > 0.0f) continue;
            p.emitter_sprite = it->second.emitter_sprite;
            p.emitter_offset = it->second.emitter_offset;
            p.emitter_size = it->second.emitter_size;
            p.emitter_light_color = it->second.emitter_light_color;
            p.emitter_light_radius = it->second.emitter_light_radius;
        }
    }
}

void ContentRegistry::LoadUserMaps(const std::string& rootDir) {
    std::error_code uec;
    std::vector<std::string> userMaps;
    // New maps built in Blender: content/maps/custom/<name>/map.json (part of the game); mods/user_maps/<name>/ (older add-on)
    for (const char* dir : {"content/maps/custom", "mods/user_maps"})
        for (const auto& e : fs::directory_iterator(fs::path(rootDir) / dir, uec))
            if (e.is_directory() && fs::exists(e.path() / "map.json"))
                userMaps.push_back(std::string(dir) + "/" + e.path().filename().string() + "/map.json");
    std::sort(userMaps.begin(), userMaps.end());
    for (const auto& um : userMaps) { Logger::Info("Loading your map: " + um); LoadMapFile(rootDir, um); }
}

void ContentRegistry::ApplyMapEdits(const std::string& rootDir) {
    std::vector<fs::path> files;
    std::error_code ec;
    for (const auto& e : fs::directory_iterator(fs::path(rootDir) / "mods", ec))
        if (e.is_directory() && fs::exists(e.path() / "map_edits.json")) files.push_back(e.path() / "map_edits.json");
    std::sort(files.begin(), files.end());
    for (const auto& f : files) {
        json j;
        std::string err;
        std::string rel = fs::relative(f, rootDir, ec).generic_string();
        if (!ReadJsonFile(f.string(), j, err)) { RecordIssue(rel, "root", err); continue; }
        std::string mapId = j.value("map", maps.empty() ? std::string() : maps.begin()->first);
        auto mit = maps.find(mapId);
        if (mit == maps.end()) { RecordIssue(rel, "map", "Unknown map '" + mapId + "'"); continue; }
        MapDef& m = mit->second;
        int changed = 0;
        auto vec3 = [](const json& a, Vector3 d) { return (a.is_array() && a.size() >= 3) ? Vector3{a[0].get<float>(), a[1].get<float>(), a[2].get<float>()} : d; };
        if (j.contains("props")) {
            const json& pj = j["props"];
            if (pj.contains("remove"))
                for (const auto& id : pj["remove"]) {
                    std::string sid = id.get<std::string>();
                    auto before = m.props.size();
                    m.props.erase(std::remove_if(m.props.begin(), m.props.end(), [&](const MapPropDef& p) { return p.id == sid; }), m.props.end());
                    changed += static_cast<int>(before - m.props.size());
                }
            if (pj.contains("modify"))
                for (const auto& [id, mod] : pj["modify"].items())
                    for (auto& p : m.props) {
                        if (p.id != id) continue;
                        if (mod.contains("pos")) p.pos = vec3(mod["pos"], p.pos);
                        if (mod.contains("rot_y")) p.rot_y = mod["rot_y"].get<float>();
                        if (mod.contains("scale")) p.scale = vec3(mod["scale"], p.scale);
                        if (mod.contains("model")) p.model = mod["model"].get<std::string>();
                        if (mod.contains("solid")) p.solid = mod["solid"].get<bool>();
                        if (mod.contains("uv_scale") && mod["uv_scale"].size() >= 2) p.uv_scale = {mod["uv_scale"][0].get<float>(), mod["uv_scale"][1].get<float>()};
                        changed++;
                    }
            if (pj.contains("add"))
                for (const auto& a : pj["add"]) { m.props.push_back(PropFromJson(a)); changed++; }
        }
        // npcs / creatures / interactables: "remove" by instance id, "set" = full definitions (replace or add)
        auto removeSet = [&](const char* key, auto& list, auto parse) {
            if (!j.contains(key)) return;
            const json& kj = j[key];
            if (kj.contains("remove"))
                for (const auto& id : kj["remove"]) {
                    std::string sid = id.get<std::string>();
                    auto before = list.size();
                    list.erase(std::remove_if(list.begin(), list.end(), [&](const auto& e) { return e.instance_id == sid; }), list.end());
                    changed += static_cast<int>(before - list.size());
                }
            if (kj.contains("set"))
                for (const auto& def : kj["set"]) {
                    auto e = parse(def);
                    bool replaced = false;
                    for (auto& old : list) if (old.instance_id == e.instance_id) { old = e; replaced = true; }
                    if (!replaced) list.push_back(e);
                    changed++;
                }
        };
        removeSet("npcs", m.npcs, NpcSpawnFromJson);
        removeSet("creatures", m.creatures, CreatureSpawnFromJson);
        removeSet("interactables", m.interactables, InteractableFromJson);
        if (j.contains("portals")) {
            const json& kj = j["portals"];
            if (kj.contains("remove"))
                for (const auto& id : kj["remove"]) {
                    std::string sid = id.get<std::string>();
                    m.portals.erase(std::remove_if(m.portals.begin(), m.portals.end(), [&](const MapPortalDef& p) { return p.id == sid; }), m.portals.end());
                    changed++;
                }
            if (kj.contains("set"))
                for (const auto& def : kj["set"]) {
                    MapPortalDef pt = PortalFromJson(def);
                    bool replaced = false;
                    for (auto& old : m.portals) if (old.id == pt.id) { old = pt; replaced = true; }
                    if (!replaced) m.portals.push_back(pt);
                    changed++;
                }
        }
        auto moveAll = [&](const char* key, auto& list, auto apply) {
            if (!j.contains(key) || !j[key].contains("modify")) return;
            for (const auto& [id, mod] : j[key]["modify"].items())
                for (auto& e : list) if (e.instance_id == id) { apply(e, mod); changed++; }
        };
        moveAll("npcs", m.npcs, [&](MapNpcSpawnDef& e, const json& mod) {
            if (mod.contains("pos")) e.pos = vec3(mod["pos"], e.pos);
            if (mod.contains("yaw")) e.yaw = mod["yaw"].get<float>();
        });
        moveAll("creatures", m.creatures, [&](MapCreatureSpawnDef& e, const json& mod) {
            if (!mod.contains("pos")) return;
            Vector3 np = vec3(mod["pos"], e.pos);
            Vector3 d = {np.x - e.pos.x, np.y - e.pos.y, np.z - e.pos.z};   // the patrol route moves with it
            e.pos = np;
            e.patrol_a = {e.patrol_a.x + d.x, e.patrol_a.y + d.y, e.patrol_a.z + d.z};
            e.patrol_b = {e.patrol_b.x + d.x, e.patrol_b.y + d.y, e.patrol_b.z + d.z};
        });
        moveAll("interactables", m.interactables, [&](MapInteractableDef& e, const json& mod) {
            if (mod.contains("pos")) e.pos = vec3(mod["pos"], e.pos);
            if (mod.contains("rot_y")) e.rot_y = mod["rot_y"].get<float>();
        });
        Logger::Info("Applied level edits " + rel + " to " + mapId + " (" + std::to_string(changed) + " changes)");
    }
}

void ContentRegistry::LoadMapFile(const std::string& rootDir, const std::string& relPath) {
    json j;
    std::string err;
    if (!ReadJsonFile((fs::path(rootDir) / relPath).string(), j, err)) {
        RecordIssue(relPath, "root", err);
        return;
    }
    MapDef m;
    m.id = j.value("id", "");
    m.display_name_key = j.value("display_name_key", "");
    m.music = j.value("music", "");
    m.ambience = j.value("ambience", "");
    if (j.contains("sky_color") && j["sky_color"].size() >= 3) {
        m.sky_color = {
            static_cast<unsigned char>(j["sky_color"][0].get<int>()),
            static_cast<unsigned char>(j["sky_color"][1].get<int>()),
            static_cast<unsigned char>(j["sky_color"][2].get<int>()),
            255
        };
    }
    if (j.contains("ambient_color")) m.ambient_color = JsonToVec3(j["ambient_color"], m.ambient_color);
    if (j.contains("sun_direction")) m.sun_direction = JsonToVec3(j["sun_direction"], m.sun_direction);
    if (j.contains("sun_color")) m.sun_color = JsonToVec3(j["sun_color"], m.sun_color);
    if (j.contains("fog_color")) m.fog_color = JsonToVec3(j["fog_color"], m.fog_color);
    m.fog_density = j.value("fog_density", 0.025f);
    m.weather = j.value("weather", "");
    m.sky_panorama = j.value("sky_panorama", "");
    if (j.contains("day_night")) m.day_night = j.value("day_night", true) ? 1 : 0;
    if (j.contains("zones") && j["zones"].is_array()) {
        for (const auto& zj : j["zones"]) {
            MapZoneDef z;
            z.id = zj.value("id", "");
            z.display_name_key = zj.value("display_name_key", m.display_name_key);
            z.box_min = JsonToVec3(zj["box_min"]);
            z.box_max = JsonToVec3(zj["box_max"]);
            z.blend = zj.value("blend", 4.0f);
            z.music = zj.value("music", m.music);
            z.ambience = zj.value("ambience", m.ambience);
            z.weather = zj.value("weather", "");
            z.sky_panorama = zj.value("sky_panorama", m.sky_panorama);
            z.day_night = zj.contains("day_night") ? (zj.value("day_night", true) ? 1 : 0) : m.day_night;
            z.sky_color = m.sky_color;
            if (zj.contains("sky_color") && zj["sky_color"].size() >= 3)
                z.sky_color = {static_cast<unsigned char>(zj["sky_color"][0].get<int>()), static_cast<unsigned char>(zj["sky_color"][1].get<int>()),
                               static_cast<unsigned char>(zj["sky_color"][2].get<int>()), 255};
            z.ambient_color = zj.contains("ambient_color") ? JsonToVec3(zj["ambient_color"]) : m.ambient_color;
            z.sun_direction = zj.contains("sun_direction") ? JsonToVec3(zj["sun_direction"]) : m.sun_direction;
            z.sun_color = zj.contains("sun_color") ? JsonToVec3(zj["sun_color"]) : m.sun_color;
            z.fog_color = zj.contains("fog_color") ? JsonToVec3(zj["fog_color"]) : m.fog_color;
            z.fog_density = zj.value("fog_density", m.fog_density);
            if (zj.contains("flag_override") && zj["flag_override"].is_object()) {
                const auto& fo = zj["flag_override"];
                z.override_flag = fo.value("flag", "");
                z.override_weather = fo.value("weather", "");
                z.override_ambience = fo.value("ambience", z.ambience);
            }
            z.sanity_drain = zj.value("sanity_drain", 0.0f);
            m.zones.push_back(z);
        }
    }

    if (j.contains("spawns") && j["spawns"].is_object()) {
        for (auto it = j["spawns"].begin(); it != j["spawns"].end(); ++it) {
            MapSpawnDef sp;
            sp.pos = JsonToVec3(it.value()["pos"]);
            sp.yaw_degrees = it.value().value("yaw_degrees", 0.0f);
            m.spawns[it.key()] = sp;
        }
    }

    if (j.contains("props")) {
        for (const auto& pj : j["props"]) {
            MapPropDef p = PropFromJson(pj);
            m.props.push_back(p);
        }
    }

    if (j.contains("lights")) {
        for (const auto& lj : j["lights"]) {
            MapLightDef l;
            l.pos = JsonToVec3(lj["pos"]);
            l.color = JsonToVec3(lj["color"], {1.0f, 0.8f, 0.4f});
            l.radius = lj.value("radius", 10.0f);
            m.lights.push_back(l);
        }
    }

    if (j.contains("npcs")) {
        for (const auto& nj : j["npcs"]) {
            MapNpcSpawnDef ns = NpcSpawnFromJson(nj);
            m.npcs.push_back(ns);
        }
    }

    if (j.contains("creatures")) {
        for (const auto& cj : j["creatures"]) {
            MapCreatureSpawnDef cs = CreatureSpawnFromJson(cj);
            m.creatures.push_back(cs);
        }
    }

    if (j.contains("interactables")) {
        for (const auto& ij : j["interactables"]) {
            MapInteractableDef in = InteractableFromJson(ij);
            m.interactables.push_back(in);
        }
    }

    if (j.contains("portals")) {
        for (const auto& pj : j["portals"]) {
            MapPortalDef pt = PortalFromJson(pj);
            m.portals.push_back(pt);
        }
    }
    if (j.contains("scatter") && j["scatter"].is_array()) {
        for (const auto& sj : j["scatter"]) {
            MapScatterDef sc;
            sc.sprite = sj.value("sprite", "");
            sc.pos = JsonToVec3(sj["pos"]);
            sc.size = sj.value("size", 0.7f);
            sc.yaw = sj.value("yaw", -1000.0f);
            m.scatter.push_back(sc);
        }
    }

    maps[m.id] = m;
}

bool ContentRegistry::ValidateAll(const std::string& rootDir) {
    for (const auto& [qid, q] : quests) {
        if (!q.campaign.empty() && !GetCampaign(q.campaign)) RecordIssue("Quest:" + qid, "campaign", "Unknown campaign '" + q.campaign + "'");
    }
    {
        std::unordered_set<std::string> placed;
        for (const auto& [mid, m] : maps) {
            for (const auto& n : m.npcs) placed.insert(n.instance_id);
            for (const auto& c : m.creatures) placed.insert(c.instance_id);
            for (const auto& i : m.interactables) placed.insert(i.instance_id);
        }
        for (const auto& [qid, q] : quests)
            for (const auto& st : q.stages)
                for (const auto& mk : st.markers)
                    if (!placed.count(mk)) RecordIssue("Quest:" + qid, "markers", "Marker '" + mk + "' is not placed in any map");
    }
    for (const auto& c : campaigns) {
        if (!loc_strings.count(c.name_key)) RecordIssue("Campaign:" + c.id, "name_key", "Missing localization string '" + c.name_key + "'");
        if (!loc_strings.count(c.desc_key)) RecordIssue("Campaign:" + c.id, "desc_key", "Missing localization string '" + c.desc_key + "'");
    }
    // 1. Validate Races
    for (const auto& r : races) {
        CheckFileExists(rootDir, r.portrait, "Race:" + r.id, "portrait");
        if (loc_strings.find(r.name_key) == loc_strings.end())
            RecordIssue("Race:" + r.id, "name_key", "Missing localization string '" + r.name_key + "'");
    }

    // 2. Validate Archetypes cross-references
    for (const auto& a : archetypes) {
        for (const auto& eq : a.starting_equipment) {
            if (items.find(eq) == items.end())
                RecordIssue("Archetype:" + a.id, "starting_equipment", "Unknown item ID '" + eq + "'");
        }
        for (const auto& inv : a.starting_inventory) {
            if (items.find(inv) == items.end())
                RecordIssue("Archetype:" + a.id, "starting_inventory", "Unknown item ID '" + inv + "'");
        }
        for (const auto& sp : a.starting_spells) {
            if (spells.find(sp) == spells.end())
                RecordIssue("Archetype:" + a.id, "starting_spells", "Unknown spell ID '" + sp + "'");
        }
    }

    // 3. Validate Items
    for (const auto& [id, it] : items) {
        CheckFileExists(rootDir, it.icon, "Item:" + id, "icon");
        CheckFileExists(rootDir, it.world_model, "Item:" + id, "world_model");
        if (loc_strings.find(it.name_key) == loc_strings.end())
            RecordIssue("Item:" + id, "name_key", "Missing localization string '" + it.name_key + "'");
        if (it.weapon.is_weapon && it.weapon.kind == "ranged" && !it.weapon.ammo_item.empty()) {
            if (items.find(it.weapon.ammo_item) == items.end())
                RecordIssue("Item:" + id, "weapon.ammo_item", "Unknown ammo item ID '" + it.weapon.ammo_item + "'");
        }
        for (const auto& ef : it.effects) {
            if (ef.type == "learn_spell" && spells.find(ef.spell_id) == spells.end()) {
                RecordIssue("Item:" + id, "effects.spell_id", "Unknown spell ID '" + ef.spell_id + "'");
            }
        }
    }

    // 4. Validate Spells
    for (const auto& [id, sp] : spells) {
        CheckFileExists(rootDir, sp.icon, "Spell:" + id, "icon");
        CheckFileExists(rootDir, sp.cast_sfx, "Spell:" + id, "cast_sfx");
    }

    // 5. Validate Creatures
    for (const auto& [id, cr] : creatures) {
        if (cr.appearance.type == "sprite_8dir") {
            CheckFileExists(rootDir, cr.appearance.sprite_sheet, "Creature:" + id, "appearance.sprite_sheet");
            CheckFileExists(rootDir, cr.appearance.animation_data, "Creature:" + id, "appearance.animation_data");
        } else if (cr.appearance.type == "model_glb") {
            CheckFileExists(rootDir, cr.appearance.model, "Creature:" + id, "appearance.model");
        } else {
            RecordIssue("Creature:" + id, "appearance.type", "Unsupported appearance type '" + cr.appearance.type + "'");
        }
        if (!cr.loot_table.empty() && loot_tables.find(cr.loot_table) == loot_tables.end()) {
            RecordIssue("Creature:" + id, "loot_table", "Unknown loot table ID '" + cr.loot_table + "'");
        }
    }

    // 5b. Validate loot tables
    for (const auto& [id, lt] : loot_tables) {
        for (const auto& g : lt.guaranteed)
            if (items.find(g) == items.end()) RecordIssue("LootTable:" + id, "guaranteed", "Unknown item ID '" + g + "'");
        for (const auto& e : lt.entries)
            if (items.find(e.item_id) == items.end()) RecordIssue("LootTable:" + id, "entries.item_id", "Unknown item ID '" + e.item_id + "'");
    }

    // 6. Validate NPCs & Dialogues
    // Recipes must make and use real items.
    for (const auto& r : recipes) {
        if (!GetItem(r.result)) RecordIssue("Recipe:" + r.id, "result", "Unknown item '" + r.result + "'");
        for (const auto& [it, q] : r.ingredients)
            if (!GetItem(it)) RecordIssue("Recipe:" + r.id, "ingredients", "Unknown item '" + it + "'");
        if (!r.book.empty()) {
            const ItemDef* b = GetItem(r.book);
            bool teaches = false;
            if (b) for (const auto& e : b->effects) teaches = teaches || (e.type == "learn_recipe" && e.recipe_id == r.id);
            if (!teaches) RecordIssue("Recipe:" + r.id, "book", "Book '" + r.book + "' doesn't teach this recipe (needs a learn_recipe effect)");
        }
    }
    for (const auto& [iid, it] : items)
        for (const auto& e : it.effects)
            if (e.type == "learn_recipe") {
                bool found = false;
                for (const auto& r : recipes) found = found || r.id == e.recipe_id;
                if (!found) RecordIssue("Item:" + iid, "effects.recipe_id", "Unknown recipe '" + e.recipe_id + "'");
            }
    for (const auto& [mid, map] : maps)
        for (const auto& in : map.interactables)
            if (in.type == "harvest" && !GetItem(in.item_id)) RecordIssue("Map:" + mid + "/" + in.instance_id, "item_id", "Unknown harvest item '" + in.item_id + "'");

    // Perks must belong to a real skill, and every milestone should offer a choice.
    for (const auto& p : perks) {
        bool known = false;
        for (const auto& s : skills) known = known || s.id == p.skill;
        if (!known) RecordIssue("Perk:" + p.id, "skill", "Unknown skill '" + p.skill + "'");
        int options = 0;
        for (const auto& o : perks) options += (o.skill == p.skill && o.level == p.level) ? 1 : 0;
        if (options < 2) RecordIssue("Perk:" + p.id, "level", "Milestone has only one perk to choose from");
    }

    // Dialogue actions that move the player must name a spawn some map actually has.
    for (const auto& [did, dlg] : dialogues) {
        auto checkTravel = [&](const DialogueAction& a) {
            if (a.type != "travel") return;
            bool found = false;
            for (const auto& [mid, map] : maps) found = found || map.spawns.count(a.spawn) > 0;
            if (!found) RecordIssue("Dialogue:" + did, "travel", "Unknown spawn '" + a.spawn + "'");
        };
        for (const auto& [nid, node] : dlg.nodes) {
            for (const auto& a : node.actions) checkTravel(a);
            for (const auto& c : node.choices)
                for (const auto& a : c.actions) checkTravel(a);
        }
    }

    for (const auto& [id, npc] : npcs) {
        if (npc.appearance.type == "sprite_8dir") {
            CheckFileExists(rootDir, npc.appearance.sprite_sheet, "NPC:" + id, "appearance.sprite_sheet");
        }
        if (!npc.dialogue_id.empty() && dialogues.find(npc.dialogue_id) == dialogues.end()) {
            RecordIssue("NPC:" + id, "dialogue_id", "Unknown dialogue ID '" + npc.dialogue_id + "'");
        }
        {
            std::vector<std::string> keys;
            for (const auto& [z, k] : npc.companion.zone_lines) keys.push_back(k);
            for (const auto& l : npc.companion.idle_lines) keys.push_back(l.text_key);
            for (const auto* v : {&npc.companion.combat_lines, &npc.companion.kill_lines, &npc.companion.heal_lines, &npc.companion.level_lines,
                                  &npc.companion.catchup_lines})
                keys.insert(keys.end(), v->begin(), v->end());
            for (const auto& b : npc.companion.banter) {
                for (const auto& l : b.lines) keys.push_back(l.second);
                if (!npcs.count(b.partner)) RecordIssue("NPC:" + id, "companion.banter", "Unknown partner NPC '" + b.partner + "'");
            }
            for (const auto& k : keys)
                if (!loc_strings.count(k)) RecordIssue("NPC:" + id, "companion", "Missing localization string '" + k + "'");
        }
        for (const auto& b : npc.barks) {
            if (loc_strings.find(b.text_key) == loc_strings.end())
                RecordIssue("NPC:" + id, "barks.text_key", "Missing localization string '" + b.text_key + "'");
            if (!b.quest_id.empty() && quests.find(b.quest_id) == quests.end())
                RecordIssue("NPC:" + id, "barks.quest_id", "Unknown quest ID '" + b.quest_id + "'");
        }
        for (const auto& v : npc.vendor_inventory) {
            if (items.find(v.item_id) == items.end()) {
                RecordIssue("NPC:" + id, "vendor_inventory.item_id", "Unknown vendor item ID '" + v.item_id + "'");
            }
        }
    }

    // 7. Validate Maps, Portals, Spawns, Props, and Interactables
    for (const auto& [id, mp] : maps) {
        if (!mp.music.empty()) CheckFileExists(rootDir, mp.music, "Map:" + id, "music");          // empty = a silent map
        if (!mp.ambience.empty()) CheckFileExists(rootDir, mp.ambience, "Map:" + id, "ambience");
        {
            std::set<std::string> seen;
            for (const auto& sc : mp.scatter)
                if (seen.insert(sc.sprite).second) CheckFileExists(rootDir, sc.sprite, "Map:" + id + "/scatter", "sprite");
        }
        for (const auto& z : mp.zones) {
            if (!z.music.empty()) CheckFileExists(rootDir, z.music, "Map:" + id + "/Zone:" + z.id, "music");
            if (!z.sky_panorama.empty()) CheckFileExists(rootDir, z.sky_panorama, "Map:" + id + "/Zone:" + z.id, "sky_panorama");
            if (!z.ambience.empty()) CheckFileExists(rootDir, z.ambience, "Map:" + id + "/Zone:" + z.id, "ambience");
            if (loc_strings.find(z.display_name_key) == loc_strings.end())
                RecordIssue("Map:" + id + "/Zone:" + z.id, "display_name_key", "Missing localization string '" + z.display_name_key + "'");
        }
        for (const auto& p : mp.props) {
            if (!p.ramp_dir.empty() && p.ramp_dir != "+x" && p.ramp_dir != "-x" && p.ramp_dir != "+z" && p.ramp_dir != "-z")
                RecordIssue("Map:" + id + "/Prop:" + p.id, "ramp", "Ramp direction must be +x, -x, +z or -z");
        }
        for (const auto& p : mp.props) {
            CheckFileExists(rootDir, p.model, "Map:" + id + "/Prop:" + p.id, "model");
            if (!p.emitter_sprite.empty()) CheckFileExists(rootDir, p.emitter_sprite, "Map:" + id + "/Prop:" + p.id, "emitter.sprite");
        }
        for (const auto& n : mp.npcs) {
            if (npcs.find(n.npc_id) == npcs.end())
                RecordIssue("Map:" + id, "npcs.npc_id", "Unknown NPC ID '" + n.npc_id + "'");
        }
        for (const auto& in : mp.interactables) {
            for (const auto& nk : in.narration_keys)
                if (loc_strings.find(nk) == loc_strings.end())
                    RecordIssue("Map:" + id + "/Interactable:" + in.instance_id, "narration", "Missing localization string '" + nk + "'");
            for (const auto& g : in.grant_items)
                if (items.find(g) == items.end())
                    RecordIssue("Map:" + id + "/Interactable:" + in.instance_id, "grant_items", "Unknown item ID '" + g + "'");
            if (!in.requires_dead.empty()) {
                bool found = false;
                for (const auto& c : mp.creatures) found = found || c.instance_id == in.requires_dead;
                if (!found) RecordIssue("Map:" + id + "/Interactable:" + in.instance_id, "requires_dead", "Unknown creature instance '" + in.requires_dead + "'");
            }
        }
        for (const auto& c : mp.creatures) {
            if (creatures.find(c.creature_id) == creatures.end())
                RecordIssue("Map:" + id, "creatures.creature_id", "Unknown creature ID '" + c.creature_id + "'");
        }
        for (const auto& pt : mp.portals) {
            auto destIt = maps.find(pt.destination_map);
            if (destIt == maps.end()) {
                RecordIssue("Map:" + id + "/Portal:" + pt.id, "destination_map", "Unknown destination map '" + pt.destination_map + "'");
            } else if (destIt->second.spawns.find(pt.destination_spawn) == destIt->second.spawns.end()) {
                RecordIssue("Map:" + id + "/Portal:" + pt.id, "destination_spawn", "Missing spawn '" + pt.destination_spawn + "' in destination map '" + pt.destination_map + "'");
            }
        }
    }

    int errCount = 0;
    for (const auto& iss : validation_issues) {
        if (iss.is_error) errCount++;
    }
    if (errCount == 0) {
        Logger::Info("Content & cross-reference validation PASSED with 0 errors.");
    } else {
        Logger::Error("Content validation found " + std::to_string(errCount) + " error(s).");
    }
    return errCount == 0;
}

std::string ContentRegistry::Tr(const std::string& key) const {
    auto it = loc_strings.find(key);
    if (it != loc_strings.end()) return it->second;
    return key;
}

const ItemDef* ContentRegistry::GetItem(const std::string& id) const {
    auto it = items.find(id);
    return it != items.end() ? &it->second : nullptr;
}

const SpellDef* ContentRegistry::GetSpell(const std::string& id) const {
    auto it = spells.find(id);
    return it != spells.end() ? &it->second : nullptr;
}

const CreatureDef* ContentRegistry::GetCreature(const std::string& id) const {
    auto it = creatures.find(id);
    return it != creatures.end() ? &it->second : nullptr;
}

const NpcDef* ContentRegistry::GetNpc(const std::string& id) const {
    auto it = npcs.find(id);
    return it != npcs.end() ? &it->second : nullptr;
}

const DialogueDef* ContentRegistry::GetDialogue(const std::string& id) const {
    auto it = dialogues.find(id);
    return it != dialogues.end() ? &it->second : nullptr;
}

const QuestDef* ContentRegistry::GetQuest(const std::string& id) const {
    auto it = quests.find(id);
    return it != quests.end() ? &it->second : nullptr;
}

const MapDef* ContentRegistry::GetMap(const std::string& id) const {
    auto it = maps.find(id);
    return it != maps.end() ? &it->second : nullptr;
}

const RaceDef* ContentRegistry::GetRace(const std::string& id) const {
    for (const auto& r : races) if (r.id == id) return &r;
    return races.empty() ? nullptr : &races[0];
}

const BackgroundDef* ContentRegistry::GetBackground(const std::string& id) const {
    for (const auto& b : backgrounds) if (b.id == id) return &b;
    return backgrounds.empty() ? nullptr : &backgrounds[0];
}

const ArchetypeDef* ContentRegistry::GetArchetype(const std::string& id) const {
    for (const auto& a : archetypes) if (a.id == id) return &a;
    return archetypes.empty() ? nullptr : &archetypes[0];
}

} // namespace uncounted

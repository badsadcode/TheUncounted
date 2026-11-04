// `game.exe --balance`: headless duels between every starting archetype and every creature, using the real
// combat, AI and projectile code with a simple scripted player. Prints a table used for tuning.
#include "gameplay/GameEngine.h"
#include "core/Logger.h"
#include "raymath.h"
#include <cmath>
#include <cstdio>
#include <filesystem>
#include <fstream>
#include <iterator>
#include <map>

namespace uncounted {

void GameEngine::RunBalanceReport() {
    if (audit_balance_) { RunAuditBalance(); return; }
    const float dt = 1.0f / 60.0f;
    const int trials = 6;
    Logger::Info("=== Balance report: archetype vs creature (" + std::to_string(trials) + " duels each, open ground) ===");
    Logger::Info("archetype        creature                  win%  avg_time  avg_hp_left  potions");

    for (int a = 0; a < static_cast<int>(content_.archetypes.size()); a++) {
        for (const auto& cdef : content_.creatures_ordered) {
            int wins = 0;
            float timeSum = 0, hpSum = 0;
            int potions = 0;
            for (int t = 0; t < trials; t++) {
                creation_race_ = 0;
                creation_bg_ = 1; // Border Watch: no social bonuses, neutral pick
                creation_arch_ = a;
                NewGame();
                SetOverlay(Overlay::None);
                LoadMap(content_.game_cfg.starting_map, content_.game_cfg.starting_spawn);
                scene_.npcs.clear();
                scene_.creatures.clear();
                // Elites and the boss are met later: model a level-3 character with two extra potions.
                bool late = cdef.behavior.find("guardian") != std::string::npos || cdef.behavior.find("boss") != std::string::npos;
                if (late) {
                    player_.level = 3;
                    player_.attributes["endurance"] += 2;
                    AddItem("core:item.health_potion", 2, false);
                    player_.health = static_cast<float>(MaxHealth());
                    player_.stamina = static_cast<float>(MaxStamina());
                    player_.mana = static_cast<float>(MaxMana());
                }
                player_.xp = -1000000; // no mid-duel level-up heals
                player_.pos = {0, 0, 2.0f};
                player_.pos.y = GroundHeight({0, 0.5f, 2.0f}, 0.45f);

                CreatureInstance c;
                c.instance_id = "duel";
                c.def = &cdef;
                c.pos = c.spawn = c.patrol_a = c.patrol_b = {0, player_.pos.y, -6.0f};
                c.health = c.max_health = cdef.health;
                float s = cdef.appearance.scale;
                c.radius = Clamp(s * 0.24f, 0.28f, 0.55f);
                c.height = cdef.appearance.type == "model_glb" ? 1.9f * s : s * 0.92f;
                c.alerted = true;
                c.state = CreatureState::Chase;
                c.last_known = player_.pos;
                scene_.creatures.push_back(c);

                const ItemDef* w = Equipped("main_hand");
                bool ranged = w && w->weapon.kind == "ranged";
                bool caster = false;
                for (const auto& sp : player_.known_spells) if (sp == "core:spell.ember_bolt") caster = true;
                float reach = w ? w->weapon.reach_meters : 1.6f;
                float elapsed = 0;
                bool won = false;

                while (elapsed < 90.0f && player_.health > 0) {
                    CreatureInstance& e = scene_.creatures[0];
                    if (e.state == CreatureState::Dead) { won = true; break; }
                    elapsed += dt;
                    player_.play_time += dt;
                    float dist = Vector3Distance(player_.pos, e.pos);
                    player_.yaw = atan2f(e.pos.x - player_.pos.x, e.pos.z - player_.pos.z);
                    Vector3 dir = Vector3Normalize({e.pos.x - player_.pos.x, 0, e.pos.z - player_.pos.z});

                    if (player_.health < MaxHealth() * 0.35f && CountItem("core:item.health_potion") > 0) {
                        UseItem("core:item.health_potion");
                        potions++;
                    }

                    bool keepAway = (ranged && CountItem(w->weapon.ammo_item) > 0) || (caster && player_.mana >= 10);
                    // Block when an attack is about to land (most humans react mid-windup, so no perfect parries).
                    bool threat = e.state == CreatureState::Windup && !e.ranged_attack && dist < e.def->attack.reach_meters + 1.0f &&
                                  e.state_timer < 0.3f;
                    bool wantBlock = threat && !keepAway && attack_timer_ < 0 && player_.stamina > 25;
                    if (wantBlock && !blocking_) block_start_ = player_.play_time - 0.3f;
                    blocking_ = wantBlock;

                    Vector3 move{};
                    bool boltIncoming = (e.state == CreatureState::Windup && e.ranged_attack) || !scene_.projectiles.empty();
                    Vector3 side = {-dir.z, 0, dir.x};
                    if (boltIncoming && dist > 3.0f) {
                        move = Vector3Scale(side, MoveSpeed() * (static_cast<int>(elapsed / 1.5f) % 2 ? 1.0f : -1.0f));
                    } else if (keepAway) {
                        if (dist < 5.0f) move = Vector3Scale(dir, -MoveSpeed() * 0.9f);
                    } else if (dist > reach * 0.8f) {
                        move = Vector3Scale(dir, MoveSpeed());
                    }
                    player_.pos = MoveWithCollision(player_.pos, Vector3Scale(move, dt), 0.32f, 1.75f, true);
                    player_.pos.y = GroundHeight({player_.pos.x, player_.pos.y + 0.3f, player_.pos.z}, 0.45f);
                    player_.pitch = atan2f((e.pos.y + e.height * 0.5f) - (player_.pos.y + 1.6f), std::max(0.1f, dist));

                    if (!blocking_) {
                        if (caster && player_.mana >= 10 && spell_cooldown_ <= 0) {
                            for (size_t k = 0; k < player_.known_spells.size(); k++)
                                if (player_.known_spells[k] == "core:spell.ember_bolt") player_.selected_spell = static_cast<int>(k);
                            CastSelectedSpell();
                        } else if (ranged && CountItem(w->weapon.ammo_item) > 0) {
                            bow_draw_ += dt / std::max(0.2f, w->weapon.attack_time_seconds);
                            if (bow_draw_ >= 1.0f) { FireArrow(1.0f); bow_draw_ = 0; }
                        } else if (attack_timer_ < 0 && dist < reach + e.radius && player_.stamina > 10) {
                            StartAttack(false);
                        }
                    }

                    UpdateCombat(dt);
                    UpdateCreatures(dt);
                    UpdateProjectiles(dt);
                    UpdateBuffs(dt);
                    UpdateParticles(dt);
                    stamina_delay_ -= dt;
                    if (stamina_delay_ <= 0 && !blocking_) player_.stamina += content_.balancing.stamina_regen_per_sec * dt;
                    player_.mana += content_.balancing.mana_regen_per_sec * dt;
                    ClampVitals();
                }
                if (!won && t == 0) {
                    const CreatureInstance& e = scene_.creatures[0];
                    Logger::Info("  lost: t=" + std::to_string(elapsed) + " php=" + std::to_string(player_.health) + " ehp=" + std::to_string(e.health) +
                                 " dist=" + std::to_string(Vector3Distance(player_.pos, e.pos)) + " estate=" + std::to_string(static_cast<int>(e.state)) +
                                 " stamina=" + std::to_string(player_.stamina) + " epos=" + std::to_string(e.pos.x) + "," + std::to_string(e.pos.z) +
                                 " ppos=" + std::to_string(player_.pos.x) + "," + std::to_string(player_.pos.z));
                }
                if (won) {
                    wins++;
                    timeSum += elapsed;
                    hpSum += player_.health / MaxHealth();
                }
            }
            char line[256];
            snprintf(line, sizeof(line), "%-16s %-24s %4d%%  %7.1fs  %10.0f%%  %7.1f", content_.Tr(content_.archetypes[a].name_key).c_str(),
                     content_.Tr(cdef.name_key).c_str(), wins * 100 / trials, wins ? timeSum / wins : 0.0f, wins ? hpSum / wins * 100.0f : 0.0f,
                     static_cast<float>(potions) / trials);
            Logger::Info(line);
        }
    }
}

// `game.exe --audit-balance`: whole runs of the Audit (ten waves, groups of monsters, the Forms) with the same scripted
// player, who fights the nearest examiner. Two profiles: fresh from Chapter Zero (level 4) and after Chapter One (7).
void GameEngine::RunAuditBalance() {
    const float dt = 1.0f / 60.0f;
    const int trials = 4;
    std::string recPath = SavePath("audit_records"), backup;     // the player's real records survive the simulation
    { std::ifstream f(recPath); if (f.is_open()) backup.assign(std::istreambuf_iterator<char>(f), {}); }
    Logger::Info("=== Audit report: waves cleared per build (" + std::to_string(trials) + " runs each) ===");
    Logger::Info("archetype        level  waves cleared (each run)   passed  avg potions");
    static const std::map<std::string, std::string> mainAttr = {
        {"core:archetype.warrior", "might"}, {"core:archetype.ranger", "agility"}, {"core:archetype.mage", "intellect"},
        {"core:archetype.rogue", "agility"}, {"core:archetype.cleric", "will"}, {"core:archetype.adventurer", "might"}};
    for (int level : {4, 7}) {
        for (int a = 0; a < static_cast<int>(content_.archetypes.size()); a++) {
            std::string waves;
            int passed = 0, potions = 0;
            for (int t = 0; t < trials; t++) {
                creation_race_ = 0;
                creation_bg_ = 1;
                creation_arch_ = a;
                NewGame();
                SetOverlay(Overlay::None);
                LoadMap(content_.game_cfg.starting_map, content_.game_cfg.starting_spawn);
                player_.level = level;
                auto ma = mainAttr.find(content_.archetypes[a].id);
                player_.attributes[ma != mainAttr.end() ? ma->second : "might"] += (level - 1 + 1) / 2;
                player_.attributes["endurance"] += (level - 1) / 2;
                for (auto& [id, sk] : player_.skills) sk.level += 3 * (level - 1);   // skills grow with use
                AddItem("core:item.health_potion", level, false);
                player_.health = static_cast<float>(MaxHealth());
                player_.stamina = static_cast<float>(MaxStamina());
                player_.mana = static_cast<float>(MaxMana());
                player_.xp = -1000000;
                DialogueAction go; go.type = "travel"; go.spawn = "audit_entry";
                ExecAction(go, "");
                for (auto& n : scene_.npcs) n.hidden = true;
                StartAudit();
                audit_.seed = static_cast<unsigned>(1234 + t * 7919 + a * 31 + level);
                const ItemDef* w = Equipped("main_hand");
                bool ranged = w && w->weapon.kind == "ranged";
                bool caster = false;
                for (const auto& sp : player_.known_spells) if (sp == "core:spell.ember_bolt") caster = true;
                float reach = w ? w->weapon.reach_meters : 1.6f;
                float elapsed = 0;
                int startPotions = CountItem("core:item.health_potion");
                while (elapsed < 900.0f && audit_.active) {
                    elapsed += dt;
                    player_.play_time += dt;
                    UpdateAudit(dt);
                    if (!audit_.active) break;
                    CreatureInstance* e = nullptr;
                    float best = 1e9f;
                    for (auto& c : scene_.creatures)
                        if (IsAuditCreature(c) && c.state != CreatureState::Dead) {
                            float d = Vector3Distance(player_.pos, c.pos);
                            if (d < best) { best = d; e = &c; }
                        }
                    if (player_.health < MaxHealth() * 0.35f && CountItem("core:item.health_potion") > 0) UseItem("core:item.health_potion");
                    if (e) {
                        float dist = best;
                        player_.yaw = atan2f(e->pos.x - player_.pos.x, e->pos.z - player_.pos.z);
                        Vector3 dir = Vector3Normalize({e->pos.x - player_.pos.x, 0, e->pos.z - player_.pos.z});
                        bool keepAway = (ranged && CountItem(w->weapon.ammo_item) > 0) || (caster && player_.mana >= 10);
                        bool threat = e->state == CreatureState::Windup && !e->ranged_attack && dist < e->def->attack.reach_meters + 1.0f && e->state_timer < 0.3f;
                        bool wantBlock = threat && !keepAway && attack_timer_ < 0 && player_.stamina > 25;
                        if (wantBlock && !blocking_) block_start_ = player_.play_time - 0.3f;
                        blocking_ = wantBlock;
                        Vector3 move{};
                        if (keepAway) { if (dist < 5.0f) move = Vector3Scale(dir, -MoveSpeed() * 0.9f); }
                        else if (dist > reach * 0.8f) move = Vector3Scale(dir, MoveSpeed());
                        player_.pos = MoveWithCollision(player_.pos, Vector3Scale(move, dt), 0.32f, 1.75f, true);
                        player_.pos.y = GroundHeight({player_.pos.x, player_.pos.y + 0.3f, player_.pos.z}, 0.45f);
                        player_.pitch = atan2f((e->pos.y + e->height * 0.5f) - (player_.pos.y + 1.6f), std::max(0.1f, dist));
                        if (!blocking_) {
                            if (caster && player_.mana >= 10 && spell_cooldown_ <= 0) {
                                for (size_t k = 0; k < player_.known_spells.size(); k++)
                                    if (player_.known_spells[k] == "core:spell.ember_bolt") player_.selected_spell = static_cast<int>(k);
                                CastSelectedSpell();
                            } else if (ranged && CountItem(w->weapon.ammo_item) > 0) {
                                bow_draw_ += dt / std::max(0.2f, w->weapon.attack_time_seconds);
                                if (bow_draw_ >= 1.0f) { FireArrow(1.0f); bow_draw_ = 0; }
                            } else if (attack_timer_ < 0 && dist < reach + e->radius && player_.stamina > 10) {
                                StartAttack(false);
                            }
                        }
                    }
                    UpdateCombat(dt);
                    UpdateCreatures(dt);
                    UpdateProjectiles(dt);
                    UpdateBuffs(dt);
                    UpdateParticles(dt);
                    stamina_delay_ -= dt;
                    if (stamina_delay_ <= 0 && !blocking_) player_.stamina += content_.balancing.stamina_regen_per_sec * dt;
                    player_.mana += content_.balancing.mana_regen_per_sec * dt;
                    ClampVitals();
                    if (player_.health <= 0.0f) break;
                }
                int cleared = player_.health > 0.0f && !audit_.active ? kAuditWaves : std::max(0, audit_.wave - 1);
                if (cleared == kAuditWaves) passed++;
                potions += startPotions - CountItem("core:item.health_potion");
                waves += (waves.empty() ? "" : " ") + std::to_string(cleared);
                if (audit_.active) EndAudit(false);
            }
            char line[256];
            snprintf(line, sizeof(line), "%-16s %5d  %-26s %4d/%d  %8.1f", content_.Tr(content_.archetypes[a].name_key).c_str(), level, waves.c_str(),
                     passed, trials, static_cast<float>(potions) / trials);
            Logger::Info(line);
        }
    }
    std::error_code ec;
    std::filesystem::remove(recPath, ec);
    if (!backup.empty()) { std::ofstream f(recPath); f << backup; }
}

} // namespace uncounted

#pragma once

#include "core/Types.h"
#include <string>
#include <vector>

namespace uncounted {

// Runtime instances built from a MapDef plus the persistent per-map state.

struct PropInstance {
    std::string id;
    std::string model_path;
    Matrix transform{};
    Vector2 uv_scale = {1.0f, 1.0f};
    BoundingBox world_box{};
    BoundingBox collider{};
    bool solid = false;
    bool walkable = false; // flat slab the player can stand on
    bool invisible = false; // collision only, not drawn
    int ramp_axis = 0;     // 0 none; 1 rises toward +x, 2 -x, 3 +z, 4 -z
};

enum class CreatureState { Idle, Patrol, Notice, Chase, Windup, Recover, Stagger, Search, Return, Dead };

struct CreatureInstance {
    std::string instance_id;
    const MapCreatureSpawnDef* spawn_def = nullptr;  // for group-clear quest triggers
    const CreatureDef* def = nullptr;
    Vector3 pos{};
    Vector3 spawn{};
    Vector3 patrol_a{};
    Vector3 patrol_b{};
    float yaw = 0.0f;           // radians, facing direction around +Y
    int health = 1;
    int max_health = 1;
    CreatureState state = CreatureState::Patrol;
    float state_timer = 0.0f;
    float attack_cooldown = 0.0f;
    bool alerted = false;
    bool patrol_to_b = true;
    bool moving = false;
    bool ranged_attack = false;
    Vector3 last_known{};
    float hit_flash = 0.0f;
    float anim_time = 0.0f;
    float radius = 0.4f;
    float height = 1.6f;
    float last_damaged_time = -100.0f;
    double last_stagger_time = -100.0; // poise: brief immunity after being staggered
    // Status effects
    float burn_time = 0.0f, burn_dps = 0.0f, burn_tick = 0.0f;
    float chill_time = 0.0f, frozen_time = 0.0f;
    int chill_stacks = 0;
    float shock_time = 0.0f;
    float ink_time = 0.0f;
    float bleed_time = 0.0f, bleed_tick = 0.0f;
    int bleed_stacks = 0;
    float bleed_power = 0.0f;
    float confuse_time = 0.0f, charm_time = 0.0f, forget_time = 0.0f;
    float wander_timer = 0.0f;
    Vector3 wander_to{};
    int foe = -1;   // index of another creature it's fighting (charmed/confused brawls)
};

struct NpcInstance {
    std::string instance_id;
    const NpcDef* def = nullptr;
    Vector3 pos{};
    float yaw = 0.0f;       // radians
    float base_yaw = 0.0f;
    float anim_time = 0.0f;
    Vector3 home{};          // where the map placed it (companions return here when dismissed)
    std::string requires_flag, hidden_flag;
    float hours_from = -1.0f, hours_to = -1.0f;   // only around between these hours (-1 = always)
    bool hidden = false;     // not present right now (story flags, or outside its hours)
    bool companion = false;  // currently travelling with the player
    std::string anim = "idle";
    float attack_cd = 0.0f;
    float anim_hold = 0.0f;  // keeps a one-shot animation (attack) on screen briefly
    float heal_cd = 0.0f;    // companions: time until they can hand over food again
};

struct InteractableInstance {
    MapInteractableDef def;
    Matrix base_transform{};
    BoundingBox world_box{};
    float open_anim = 0.0f; // 0 closed .. 1 open (doors, levers, plates, chests)
    bool open = false;
    bool locked = false;
    bool used = false;
    bool hidden = false;  // requires_flag not yet set, or hidden_flag set
};

struct Projectile {
    Vector3 pos{};
    Vector3 vel{};
    bool from_player = true;
    int damage = 10;
    std::string skill;
    std::string sprite;   // billboard sprite strip (4 frames)
    std::string model;    // physical model (arrows)
    Vector3 light_color = {0, 0, 0};
    float light_radius = 0.0f;
    float gravity = 0.0f;
    float life = 4.0f;
    float age = 0.0f;
    bool is_arrow = false;
    bool sneak = false;
    bool alive = true;
    std::string ammo_item;
    // Build traits carried to impact
    float crit_chance = 0.0f;
    float crit_mult = 1.5f;
    std::string bane_family;
    float bane_mult = 1.0f;
    float life_steal = 0.0f;
    float splash_radius = 0.0f;
    float drain = 0.0f;
    int sanity = 0;          // enemy projectiles: sanity lost on hit
    std::string status;      // status applied on hit (burn, chill, shock, ink)
    float status_power = 0.0f, status_duration = 0.0f, status_chance = 0.0f;
};

struct WorldPickup {
    std::string key;      // persistence key (empty for transient drops)
    std::string item_id;
    std::string model;
    int qty = 1;
    Vector3 pos{};
    float spin = 0.0f;
    bool stuck = false;   // arrows embedded in geometry keep their orientation
    Vector3 dir = {0, 0, -1};
};

struct Emitter {
    Vector3 pos{};
    std::string sprite;   // horizontal strip of square frames
    float size = 0.35f;
    float phase = 0.0f;
};

struct Particle {
    Vector3 pos{};
    Vector3 vel{};
    Color color = WHITE;
    float life = 1.0f;
    float max_life = 1.0f;
    float size = 0.05f;
    float gravity = 6.0f;
    bool glow = false;
};

struct SceneLight {
    Vector3 pos{};
    Vector3 color{};
    float radius = 1.0f;
};

struct Scene {
    const MapDef* map = nullptr;
    std::vector<PropInstance> props;
    std::vector<InteractableInstance> interactables;
    std::vector<NpcInstance> npcs;
    std::vector<CreatureInstance> creatures;
    std::vector<Projectile> projectiles;
    std::vector<WorldPickup> pickups;
    std::vector<SceneLight> static_lights;
    std::vector<Emitter> emitters;
    std::vector<Particle> particles;
};

} // namespace uncounted

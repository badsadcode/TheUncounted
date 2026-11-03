#include "gameplay/GameEngine.h"
#include "core/Logger.h"
#include "nlohmann/json.hpp"
#include "raymath.h"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <random>
#include <cstdio>
#include <cstdlib>
#include <ctime>

namespace fs = std::filesystem;
using json = nlohmann::json;

namespace uncounted {

static std::mt19937& Rng() {
    static std::mt19937 rng(std::random_device{}());
    return rng;
}
static int RandInt(int lo, int hi) {
    if (hi < lo) std::swap(lo, hi);
    return std::uniform_int_distribution<int>(lo, hi)(Rng());
}
static float RandF() { return std::uniform_real_distribution<float>(0.0f, 1.0f)(Rng()); }

static float WrapAngle(float a) {
    while (a > PI) a -= 2.0f * PI;
    while (a < -PI) a += 2.0f * PI;
    return a;
}
static float YawTo(Vector3 from, Vector3 to) { return atan2f(to.x - from.x, to.z - from.z); }
static Vector3 Forward(float yaw) { return {sinf(yaw), 0.0f, cosf(yaw)}; }
static float HDist(Vector3 a, Vector3 b) { return sqrtf((a.x - b.x) * (a.x - b.x) + (a.z - b.z) * (a.z - b.z)); }

static const float kFixedDt = 1.0f / 60.0f;
static const float kPlayerRadius = 0.32f;
static const float kStepHeight = 0.45f;
static const float kGravity = 16.0f;

// ============================================================================
// Input bindings
// ============================================================================
static int KeyFromName(const std::string& n) {
    if (n.size() == 1) {
        char c = n[0];
        if (c >= 'A' && c <= 'Z') return KEY_A + (c - 'A');
        if (c >= 'a' && c <= 'z') return KEY_A + (c - 'a');
        if (c >= '0' && c <= '9') return KEY_ZERO + (c - '0');
    }
    if (n.size() >= 2 && n[0] == 'F') {
        int f = atoi(n.c_str() + 1);
        if (f >= 1 && f <= 12) return KEY_F1 + (f - 1);
    }
    static const std::map<std::string, int> named = {
        {"SPACE", KEY_SPACE}, {"LEFT_SHIFT", KEY_LEFT_SHIFT}, {"RIGHT_SHIFT", KEY_RIGHT_SHIFT},
        {"LEFT_CONTROL", KEY_LEFT_CONTROL}, {"RIGHT_CONTROL", KEY_RIGHT_CONTROL}, {"LEFT_ALT", KEY_LEFT_ALT},
        {"TAB", KEY_TAB}, {"ENTER", KEY_ENTER}, {"ESCAPE", KEY_ESCAPE}, {"BACKSPACE", KEY_BACKSPACE},
        {"UP", KEY_UP}, {"DOWN", KEY_DOWN}, {"LEFT", KEY_LEFT}, {"RIGHT", KEY_RIGHT},
        {"MOUSE_LEFT", 1000 + MOUSE_BUTTON_LEFT}, {"MOUSE_RIGHT", 1000 + MOUSE_BUTTON_RIGHT},
        {"MOUSE_MIDDLE", 1000 + MOUSE_BUTTON_MIDDLE},
    };
    auto it = named.find(n);
    return it != named.end() ? it->second : 0;
}

static const std::map<std::string, std::string>& DefaultBindings() {
    static const std::map<std::string, std::string> d = {
        {"move_forward", "W"}, {"move_backward", "S"}, {"move_left", "A"}, {"move_right", "D"},
        {"sprint", "LEFT_SHIFT"}, {"crouch", "LEFT_CONTROL"}, {"jump", "SPACE"}, {"interact", "E"},
        {"attack", "MOUSE_LEFT"}, {"block_or_aim", "MOUSE_RIGHT"}, {"cast_spell", "Q"}, {"cycle_spell", "R"},
        {"quick_slot_1", "1"}, {"quick_slot_2", "2"}, {"quick_slot_3", "3"}, {"quick_slot_4", "4"},
        {"inventory", "I"}, {"character", "C"}, {"journal", "J"}, {"map", "M"},
        {"quick_save", "F6"}, {"quick_load", "F9"}, {"hot_reload", "F5"}, {"debug_overlay", "F3"},
    };
    return d;
}

static int BindingCode(const ControlsConfig& c, const std::string& name) {
    auto it = c.bindings.find(name);
    if (it != c.bindings.end()) return KeyFromName(it->second);
    auto d = DefaultBindings().find(name);
    return d != DefaultBindings().end() ? KeyFromName(d->second) : 0;
}

bool GameEngine::ActionDown(const std::string& name) const {
    int code = BindingCode(content_.controls, name);
    if (code >= 1000) return IsMouseButtonDown(code - 1000);
    return code > 0 && IsKeyDown(code);
}
bool GameEngine::ActionPressed(const std::string& name) const {
    int code = BindingCode(content_.controls, name);
    if (code >= 1000) return IsMouseButtonPressed(code - 1000);
    return code > 0 && IsKeyPressed(code);
}
bool GameEngine::ActionReleased(const std::string& name) const {
    int code = BindingCode(content_.controls, name);
    if (code >= 1000) return IsMouseButtonReleased(code - 1000);
    return code > 0 && IsKeyReleased(code);
}
std::string GameEngine::BindingLabel(const std::string& name) const {
    auto it = content_.controls.bindings.find(name);
    std::string s = it != content_.controls.bindings.end() ? it->second : DefaultBindings().at(name);
    if (s == "MOUSE_LEFT") return "LMB";
    if (s == "MOUSE_RIGHT") return "RMB";
    if (s == "LEFT_SHIFT") return "Shift";
    if (s == "LEFT_CONTROL") return "Ctrl";
    return s;
}

// ============================================================================
// Init / shutdown / main loop
// ============================================================================
bool GameEngine::Init(int argc, char** argv) {
    // Locate the game root (folder containing content/manifest.json): cwd first, then the exe folder.
    std::string root = ".";
    if (!fs::exists("content/manifest.json")) {
        std::string appDir = GetApplicationDirectory();
        if (fs::exists(fs::path(appDir) / "content/manifest.json")) root = appDir;
    }
    fs::current_path(root);

    Logger::Init("uncounted.log");
    content_.LoadConfigs(".");

    bool validateOnly = false;
    std::string shotMap, shotSpawn;
    float shotYaw = -9999.0f, shotPitch = 0.0f;
    bool shotHasPos = false;
    Vector3 shotPos{};
    for (int i = 1; i < argc; i++) {
        std::string a = argv[i];
        auto next = [&]() { return i + 1 < argc ? std::string(argv[++i]) : std::string(); };
        if (a == "--validate") validateOnly = true;
        else if (a == "--shot") boot_shot_ = next();
        else if (a == "--frames") boot_shot_frames_ = atoi(next().c_str());
        else if (a == "--map") shotMap = next();
        else if (a == "--spawn") shotSpawn = next();
        else if (a == "--yaw") shotYaw = static_cast<float>(atof(next().c_str()));
        else if (a == "--pitch") shotPitch = static_cast<float>(atof(next().c_str()));
        else if (a == "--overlay") boot_shot_overlay_ = next();
        else if (a == "--flag") boot_shot_flags_.push_back(next());          // --shot: set a story flag first
        else if (a == "--sanity") boot_shot_sanity_ = static_cast<float>(atof(next().c_str()));  // --shot: start at this sanity
        else if (a == "--companion") boot_shot_companions_.push_back(next());  // --shot: travel with this NPC (repeatable)
        else if (a == "--pos" && i + 3 < argc) {
            shotPos = {static_cast<float>(atof(argv[i + 1])), static_cast<float>(atof(argv[i + 2])), static_cast<float>(atof(argv[i + 3]))};
            shotHasPos = true;
            i += 3;
        }
        else if (a == "--mods") content_.game_cfg.enable_mods = true;
        else if (a == "--selftest") selftest_ = true;
        else if (a == "--balance") balance_ = true;
        else if (a == "--mute") mute_ = true;
        else if (a == "--arch") creation_arch_ = atoi(next().c_str());
        else if (a == "--showcase") boot_shot_overlay_ = "showcase";
    }

    if (validateOnly) {
        content_.LoadAllContent(".");
        bool ok = content_.ValidateAll(".");
        Logger::Info(ok ? "Validation OK" : "Validation FAILED");
        running_ = false;
        return ok;
    }

    const GraphicsConfig& g = content_.graphics;
    unsigned int flags = FLAG_WINDOW_RESIZABLE;
    if (g.vsync) flags |= FLAG_VSYNC_HINT;
    SetConfigFlags(flags);
    SetTraceLogLevel(LOG_WARNING);
    InitWindow(g.window_width, g.window_height, "The Uncounted - Chapter Zero: Legally Deceased");
    if (!IsWindowReady()) return false;
    SetWindowMinSize(640, 360);
    if (g.fullscreen) ToggleBorderlessWindowed();
    SetExitKey(KEY_NULL);
    SetTargetFPS(g.target_fps);
    // Automated runs (tests, balance sims, screenshots) stay silent; --mute does the same for normal play.
    if (!mute_ && !selftest_ && !balance_ && boot_shot_.empty()) InitAudioDevice();

    res_.Init(".", g.texture_filter == "nearest");
    content_.LoadAllContent(".");
    content_.ValidateAll(".");
    int errs = 0;
    for (const auto& v : content_.validation_issues) errs += v.is_error ? 1 : 0;
    validation_summary_ = errs == 0 ? "Content validation passed" : std::to_string(errs) + " content validation error(s) - see uncounted.log";

    renderer_.Init(&res_, &content_.graphics);
    ApplyAudioVolumes();

    if (!boot_shot_.empty()) {
        NewGame();
        if (!shotMap.empty()) LoadMap(shotMap, shotSpawn);
        if (shotHasPos) {
            player_.pos = shotPos;
            player_.pos.y = GroundHeight({shotPos.x, shotPos.y + 0.5f, shotPos.z}, kStepHeight);
        }
        if (shotYaw > -9000.0f) player_.yaw = shotYaw * DEG2RAD;
        player_.pitch = shotPitch * DEG2RAD;
        overlay_ = Overlay::None;
        for (const auto& f : boot_shot_flags_) player_.flags.insert(f);
        if (boot_shot_sanity_ >= 0.0f) player_.sanity = boot_shot_sanity_;
        for (size_t k = 0; k < boot_shot_companions_.size(); k++) {
            player_.companions.push_back(boot_shot_companions_[k]);
            for (auto& n : scene_.npcs) {
                if (n.def->id != boot_shot_companions_[k]) continue;
                // Stand each companion where the follow logic would settle, a little ahead so they're in shot.
                Vector3 f = Forward(player_.yaw);
                Vector3 sd = {f.z, 0.0f, -f.x};
                float sgn = k == 0 ? 1.0f : -1.0f;
                n.pos = Vector3Add(player_.pos, Vector3Add(Vector3Scale(f, 2.4f), Vector3Scale(sd, 1.1f * sgn)));
                n.pos.y = GroundHeight({n.pos.x, player_.pos.y + 0.5f, n.pos.z}, kStepHeight);
            }
            companion_last_zone_ = "none";
        }
        if (boot_shot_overlay_ == "showcase") {
            // Line up every wearable/consumable as a world pickup in front of the camera (asset review aid).
            std::vector<const ItemDef*> show;
            for (const auto& it : content_.items_ordered)
                if (it.category == "armor" || it.category == "accessory" || it.category == "consumable") show.push_back(&it);
            Vector3 fwd = Forward(player_.yaw);
            Vector3 right = {-cosf(player_.yaw), 0.0f, sinf(player_.yaw)};
            for (size_t i = 0; i < show.size(); i++) {
                WorldPickup wp;
                wp.item_id = show[i]->id;
                wp.model = show[i]->world_model;
                float off = (static_cast<float>(i) - (show.size() - 1) * 0.5f) * 0.55f;
                wp.pos = Vector3Add(player_.pos, Vector3Add(Vector3Scale(fwd, 2.4f), Vector3Scale(right, off)));
                wp.pos.y += 0.9f;
                scene_.pickups.push_back(wp);
            }
            Vector3 c = Vector3Add(player_.pos, Vector3Add(Vector3Scale(fwd, 2.0f), {0, 1.6f, 0}));
            SpawnBurst(Vector3Add(c, Vector3Scale(right, -0.8f)), Color{255, 120, 40, 255}, 24, 2.5f, true, 2.0f);
            SpawnBurst(c, Color{226, 216, 192, 255}, 24, 2.5f, false);
            SpawnBurst(Vector3Add(c, Vector3Scale(right, 0.8f)), Color{130, 230, 255, 255}, 24, 2.5f, true, 2.0f);
        }
        if (boot_shot_overlay_ == "prologue") { narration_page_ = 1; narration_time_ = 5.0f; overlay_ = Overlay::Narration; }
        if (boot_shot_overlay_ == "story") {
            SetQuestStage("core:quest.bakers_daughter", 0);
            SetQuestStage("core:quest.bakers_daughter", 10);
            toasts_.clear();
            Say(content_.Tr("npc.innkeeper_marta.name"), content_.Tr("bark.marta.2"), 30.0f);
        }
        if (boot_shot_overlay_ == "inventory") overlay_ = Overlay::Inventory;
        else if (boot_shot_overlay_ == "character") overlay_ = Overlay::Character;
        else if (boot_shot_overlay_ == "combat") {
            // Combat sheet with a crit build: letter-opener, Sabrino's hat and a couple of extra spells
            for (const char* id : {"core:item.letter_opener", "core:item.sabrino_hat", "core:item.baggy_umbrella"}) AddItem(id, 1, false);
            EquipItem("core:item.letter_opener");
            EquipItem("core:item.sabrino_hat");
            for (const char* sp : {"core:spell.sabrino_fireball", "core:spell.siphon_ink", "core:spell.frost_lance", "core:spell.chain_of_command",
                                   "core:spell.cold_shoulder", "core:spell.clerical_error"}) player_.known_spells.push_back(sp);
            char_tab_ = 1;
            overlay_ = Overlay::Character;
        } else if (boot_shot_overlay_ == "compare") {
            AddItem("core:item.baggy_umbrella", 1, false);
            inv_selected_ = "core:item.baggy_umbrella";
            overlay_ = Overlay::Inventory;
            ui_ignore_hover_ = true;
        }
        else if (boot_shot_overlay_ == "journal") overlay_ = Overlay::Journal;
        else if (boot_shot_overlay_ == "options") overlay_ = Overlay::Options;
        else if (boot_shot_overlay_ == "fishing") {
            fishing_ = true;
            fish_state_ = 1;
            fish_timer_ = 999.0f;
            fish_from_ = player_.pos;
            Vector3 f = Forward(player_.yaw);
            fish_bob_ = {player_.pos.x + f.x * 3.0f, player_.pos.y + 0.02f, player_.pos.z + f.z * 3.0f};
            toasts_.clear();
        }
        else if (boot_shot_overlay_ == "crafting") {
            for (const char* m : {"core:item.marigold", "core:item.pine_resin", "core:item.bladderwrack", "core:item.sea_salt", "core:item.glowcap"})
                AddItem(m, 3, false);
            craft_station_ = "alchemy";
            craft_selected_ = "core:recipe.oil_fire";
            overlay_ = Overlay::Crafting;
            toasts_.clear();
        }
        else if (boot_shot_overlay_ == "perks") {
            // A mid-game mage: Elemental 27 with one perk chosen and one waiting.
            player_.skills["elemental"].level = 27;
            player_.perks.insert("core:perk.kindling");
            perk_skill_ = "elemental";
            char_tab_ = 2;
            overlay_ = Overlay::Character;
            toasts_.clear();
        }
        else if (boot_shot_overlay_ == "status_demo" || boot_shot_overlay_ == "status_demo2") {
            // Four wolves in a row in front of the camera: burning, chilled, frozen, shocked + inked.
            const CreatureDef* wolf = content_.GetCreature("core:enemy.grey_wolf");
            Vector3 fwd = Forward(player_.yaw), side = {-fwd.z, 0.0f, fwd.x};
            for (int i = 0; i < 4; i++) {
                CreatureInstance c;
                c.instance_id = "demo_" + std::to_string(i);
                c.def = wolf;
                c.pos = c.spawn = c.patrol_a = c.patrol_b = Vector3Add(player_.pos, Vector3Add(Vector3Scale(fwd, 4.5f), Vector3Scale(side, (i - 1.8f) * 1.5f)));
                c.yaw = player_.yaw + PI + 0.5f;
                c.health = c.max_health = 999;
                c.radius = 0.4f; c.height = 1.2f;
                c.state = CreatureState::Idle; c.state_timer = 999.0f;
                scene_.creatures.push_back(c);
            }
            size_t n = scene_.creatures.size();
            ApplyStatus(scene_.creatures[n - 4], "burn", 1.0f, 999.0f);
            ApplyStatus(scene_.creatures[n - 3], "chill", 0.0f, 999.0f);
            for (int k = 0; k < 3; k++) ApplyStatus(scene_.creatures[n - 2], "chill", 0.0f, 999.0f);
            scene_.creatures[n - 2].frozen_time = 999.0f;
            ApplyStatus(scene_.creatures[n - 1], "shock", 0.0f, 999.0f);
            ApplyStatus(scene_.creatures[n - 1], "ink", 0.0f, 999.0f);
            if (boot_shot_overlay_ == "status_demo2") {  // the roguelike set: charmed, confused, bleeding
                scene_.creatures[n - 4].burn_time = 0.0f;
                ApplyStatus(scene_.creatures[n - 4], "charm", 0.0f, 999.0f);
                scene_.creatures[n - 3].chill_time = 0.0f;
                ApplyStatus(scene_.creatures[n - 3], "confuse", 0.0f, 999.0f);
                scene_.creatures[n - 2].frozen_time = scene_.creatures[n - 2].chill_time = 0.0f;
                for (int k = 0; k < 3; k++) ApplyStatus(scene_.creatures[n - 2], "bleed", 0.01f, 999.0f);
                scene_.creatures[n - 1].ink_time = scene_.creatures[n - 1].shock_time = 0.0f;
            }
            player_.known_spells.push_back("core:spell.chain_of_command");
            player_.known_spells.push_back("core:spell.cold_shoulder");
            toasts_.clear();
        }
        else if (boot_shot_overlay_ == "journal_demo") {
            // A journal mid-playthrough: several campaigns under way
            SetQuestStage("core:quest.legally_deceased", 10);
            SetQuestStage("core:quest.bakers_daughter", 0);
            SetQuestStage("core:quest.bakers_daughter", 10);
            SetQuestStage("core:quest.rats", 0);
            SetQuestStage("core:quest.rats", 100);
            SetQuestStage("core:quest.dinner_at_eight", 0);
            SetQuestStage("core:quest.hollowmere", 0);
            SetQuestStage("core:quest.hollowmere", 10);
            toasts_.clear();
            overlay_ = Overlay::Journal;
        }
        else if (boot_shot_overlay_ == "map") overlay_ = Overlay::Map;
        else if (boot_shot_overlay_ == "title") screen_ = Screen::Title;
        else if (boot_shot_overlay_ == "creation") screen_ = Screen::Creation;
        else if (boot_shot_overlay_.rfind("narration:", 0) == 0) {
            StartNarration({boot_shot_overlay_.substr(10)});
            narration_time_ = 30.0f;  // fully faded in
        }
        else if (boot_shot_overlay_.rfind("reader:", 0) == 0) {
            // reader:<item id> — preview a book/document's reader page
            if (const ItemDef* it = content_.GetItem(boot_shot_overlay_.substr(7))) { ReadItem(*it); SetOverlay(Overlay::Reader); }
        }
        else if (boot_shot_overlay_ == "ending") {
            // Longest possible epilogue, for layout checks
            for (const char* f : {"marta_testimony", "spirit_clue_learned", "witness_named", "ilse_remembered", "marta_knows_ilse", "seal_renewed"})
                player_.flags.insert(f);
            ending_stage_ = 101;
            screen_ = Screen::Ending;
        }
        else if (boot_shot_overlay_ == "dialogue") {
            for (size_t i = 0; i < scene_.npcs.size(); i++) { StartDialogue(static_cast<int>(i)); break; }
        } else if (boot_shot_overlay_.rfind("dialogue:", 0) == 0) {
            // dialogue:<npc id>[:<node>] — preview a specific conversation node (all its choices shown)
            std::string spec = boot_shot_overlay_.substr(9);
            size_t colon = spec.find(':', spec.find(':') + 1);
            std::string npcId = spec.substr(0, colon), node = colon == std::string::npos ? "" : spec.substr(colon + 1);
            for (size_t i = 0; i < scene_.npcs.size(); i++) {
                if (scene_.npcs[i].def->id != npcId) continue;
                StartDialogue(static_cast<int>(i));
                if (!node.empty()) dialogue_node_ = node;
                break;
            }
        }
        if (boot_shot_frames_ <= 0) boot_shot_frames_ = 30;
    }
    return true;
}

void GameEngine::Shutdown() {
    if (!IsWindowReady()) return;
    StopMapAudio();
    renderer_.Shutdown();
    res_.UnloadAll();
    if (IsAudioDeviceReady()) CloseAudioDevice();
    CloseWindow();
}

void GameEngine::Run() {
    int frame = 0;
    while (running_ && !WindowShouldClose()) {
        float dt = std::min(GetFrameTime(), 0.1f);
        if (!boot_shot_.empty()) dt = kFixedDt;
        Frame(dt);
        DrawFrame();
        frame++;
        if (!boot_shot_.empty() && frame >= boot_shot_frames_) {
            Image img = LoadImageFromScreen();
            ExportImage(img, boot_shot_.c_str());
            UnloadImage(img);
            Logger::Info("Saved verification screenshot to " + boot_shot_);
            running_ = false;
        }
    }
}

void GameEngine::ApplyAudioVolumes() {
    const GameConfig& c = content_.game_cfg;
    if (IsAudioDeviceReady()) SetMasterVolume(c.master_volume);
    res_.SetSfxVolume(c.sfx_volume);
    // Stream volumes are re-applied every frame by UpdateAudio().
}

void GameEngine::StopMapAudio() {
    for (auto& s : streams_) {
        StopMusicStream(s.music);
        UnloadMusicStream(s.music);
    }
    streams_.clear();
    want_music_.clear();
    want_ambience_.clear();
}

void GameEngine::PlayMapAudio(const MapDef* map) {
    if (!map) return;
    const MapZoneDef* z = CurrentZone();
    std::string amb = z ? z->ambience : map->ambience;
    if (z && !z->override_flag.empty() && player_.flags.count(z->override_flag)) amb = z->override_ambience;
    SetWantedAudio(z ? z->music : map->music, amb);
}

void GameEngine::SetWantedAudio(const std::string& music, const std::string& ambience) {
    want_music_ = music;
    want_ambience_ = ambience;
    if (!IsAudioDeviceReady()) return;
    auto ensure = [&](const std::string& path, bool isMusic) {
        if (path.empty()) return;
        for (const auto& s : streams_)
            if (s.path == path && s.is_music == isMusic) return;
        if (!res_.Exists(path)) { Logger::Error("Missing audio stream '" + path + "'"); return; }
        StreamTrack t;
        t.music = LoadMusicStream(res_.Resolve(path).c_str());
        if (t.music.frameCount == 0) { Logger::Error("Failed to stream audio '" + path + "'"); return; }
        t.music.looping = true;
        t.path = path;
        t.is_music = isMusic;
        t.vol = streams_.empty() ? 1.0f : 0.0f; // first track of a session starts audible
        SetMusicVolume(t.music, 0.0f);
        PlayMusicStream(t.music);
        streams_.push_back(t);
    };
    ensure(music, true);
    ensure(ambience, false);
}

void GameEngine::UpdateAudio(float dt) {
    const GameConfig& c = content_.game_cfg;
    for (auto& s : streams_) {
        bool wanted = s.path == (s.is_music ? want_music_ : want_ambience_);
        // Crossfade: new tracks swell in over ~3 s while the previous region's fade out over ~2 s.
        s.vol = wanted ? std::min(1.0f, s.vol + dt / 3.0f) : std::max(0.0f, s.vol - dt / 2.0f);
        SetMusicVolume(s.music, s.vol * (s.is_music ? c.music_volume : c.ambience_volume));
        UpdateMusicStream(s.music);
    }
    for (size_t i = 0; i < streams_.size();) {
        StreamTrack& s = streams_[i];
        bool wanted = s.path == (s.is_music ? want_music_ : want_ambience_);
        if (!wanted && s.vol <= 0.0f) {
            StopMusicStream(s.music);
            UnloadMusicStream(s.music);
            streams_.erase(streams_.begin() + static_cast<long>(i));
        } else {
            i++;
        }
    }
}

// ============================================================================
// Zones & atmosphere
// ============================================================================
static float BoxDistance(const Vector3& p, const Vector3& mn, const Vector3& mx) {
    float dx = std::max(std::max(mn.x - p.x, 0.0f), p.x - mx.x);
    float dy = std::max(std::max(mn.y - p.y, 0.0f), p.y - mx.y);
    float dz = std::max(std::max(mn.z - p.z, 0.0f), p.z - mx.z);
    return sqrtf(dx * dx + dy * dy + dz * dz);
}

Atmosphere GameEngine::ComputeAtmosphere(Vector3 p, const MapZoneDef** dominant) const {
    Atmosphere a;
    const MapDef* m = scene_.map;
    if (dominant) *dominant = nullptr;
    if (!m) return a;
    a.sky = m->sky_color;
    a.ambient = m->ambient_color;
    a.sun_dir = m->sun_direction;
    a.sun_color = m->sun_color;
    a.fog_color = m->fog_color;
    a.fog_density = m->fog_density;
    a.weather = m->weather;
    if (m->zones.empty()) return a;

    float wsum = 0.0f, best = 0.0f;
    float sky[3] = {0, 0, 0};
    Vector3 amb{}, sd{}, sc{}, fc{};
    float fd = 0.0f;
    for (const auto& z : m->zones) {
        float d = BoxDistance(p, z.box_min, z.box_max);
        float w = Clamp(1.0f - d / std::max(0.01f, z.blend), 0.0f, 1.0f);
        w *= w;
        if (w <= 0.0f) continue;
        if (w > best) { best = w; if (dominant) *dominant = &z; }
        wsum += w;
        sky[0] += z.sky_color.r * w; sky[1] += z.sky_color.g * w; sky[2] += z.sky_color.b * w;
        amb = Vector3Add(amb, Vector3Scale(z.ambient_color, w));
        sd = Vector3Add(sd, Vector3Scale(z.sun_direction, w));
        sc = Vector3Add(sc, Vector3Scale(z.sun_color, w));
        fc = Vector3Add(fc, Vector3Scale(z.fog_color, w));
        fd += z.fog_density * w;
    }
    if (wsum <= 0.0f) return a;
    float k = 1.0f / wsum;
    a.sky = {static_cast<unsigned char>(sky[0] * k), static_cast<unsigned char>(sky[1] * k), static_cast<unsigned char>(sky[2] * k), 255};
    a.ambient = Vector3Scale(amb, k);
    a.sun_dir = Vector3Scale(sd, k);
    a.sun_color = Vector3Scale(sc, k);
    a.fog_color = Vector3Scale(fc, k);
    a.fog_density = fd * k;
    a.weather = (dominant && *dominant) ? (*dominant)->weather : m->weather;
    if (dominant && *dominant && !(*dominant)->override_flag.empty() && player_.flags.count((*dominant)->override_flag))
        a.weather = (*dominant)->override_weather;
    return a;
}

const MapZoneDef* GameEngine::CurrentZone() const {
    if (!scene_.map) return nullptr;
    for (const auto& z : scene_.map->zones)
        if (z.id == zone_id_) return &z;
    return nullptr;
}

void GameEngine::UpdateAtmosphere(float dt, bool snap) {
    if (!scene_.map) return;
    const MapZoneDef* dom = nullptr;
    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    Atmosphere target = ComputeAtmosphere(eye, &dom);
    if (snap) {
        atmo_ = target;
    } else {
        float k = 1.0f - expf(-dt * 2.5f);
        auto lc = [&](unsigned char a, unsigned char b) { return static_cast<unsigned char>(a + (b - a) * k); };
        atmo_.sky = {lc(atmo_.sky.r, target.sky.r), lc(atmo_.sky.g, target.sky.g), lc(atmo_.sky.b, target.sky.b), 255};
        atmo_.ambient = Vector3Lerp(atmo_.ambient, target.ambient, k);
        atmo_.sun_dir = Vector3Lerp(atmo_.sun_dir, target.sun_dir, k);
        atmo_.sun_color = Vector3Lerp(atmo_.sun_color, target.sun_color, k);
        atmo_.fog_color = Vector3Lerp(atmo_.fog_color, target.fog_color, k);
        atmo_.fog_density += (target.fog_density - atmo_.fog_density) * k;
        atmo_.weather = target.weather;
    }
    std::string id = dom ? dom->id : "";
    if (id != zone_id_) {
        zone_id_ = id;
        const MapZoneDef* z = CurrentZone();
        region_banner_ = content_.Tr(z ? z->display_name_key : scene_.map->display_name_key);
        region_banner_time_ = 4.0f;
        PlayMapAudio(scene_.map);
    }
}

// ============================================================================
// New game / maps
// ============================================================================
void GameEngine::NewGame() {
    player_ = PlayerState{};
    persist_.clear();
    vendor_sold_.clear();
    ending_shown_ = false;
    ending_stage_ = 0;
    toasts_.clear();

    const RaceDef* race = content_.races.empty() ? nullptr : &content_.races[std::min<size_t>(creation_race_, content_.races.size() - 1)];
    const BackgroundDef* bg = content_.backgrounds.empty() ? nullptr : &content_.backgrounds[std::min<size_t>(creation_bg_, content_.backgrounds.size() - 1)];
    const ArchetypeDef* arch = content_.archetypes.empty() ? nullptr : &content_.archetypes[std::min<size_t>(creation_arch_, content_.archetypes.size() - 1)];

    player_.name = creation_name_.empty() ? "Nameless" : creation_name_;
    for (const auto& a : content_.attributes) player_.attributes[a.id] = a.base;
    for (const auto& s : content_.skills) player_.skills[s.id].level = 5;
    if (race) {
        player_.race_id = race->id;
        for (auto& [k, v] : race->attribute_modifiers) player_.attributes[k] += v;
        for (auto& [k, v] : race->skill_bonuses) player_.skills[k].level += v;
    }
    if (bg) {
        player_.background_id = bg->id;
        player_.gold = bg->starting_gold;
        for (auto& [k, v] : bg->skill_bonuses) player_.skills[k].level += v;
        for (const auto& it : bg->starting_items) AddItem(it, 1, false);
    }
    if (arch) {
        player_.archetype_id = arch->id;
        for (auto& [k, v] : arch->attribute_bonuses) player_.attributes[k] += v;
        for (auto& [k, v] : arch->skill_bonuses) player_.skills[k].level += v;
        for (const auto& it : arch->starting_equipment) { AddItem(it, 1, false); EquipItem(it); }
        for (const auto& it : arch->starting_inventory) AddItem(it, 1, false);
        if (arch->starting_ammo > 0) {
            for (const auto& eq : arch->starting_equipment) {
                const ItemDef* d = content_.GetItem(eq);
                if (d && d->weapon.kind == "ranged" && !d->weapon.ammo_item.empty()) AddItem(d->weapon.ammo_item, arch->starting_ammo, false);
            }
            for (const auto& eq : arch->starting_inventory) {
                const ItemDef* d = content_.GetItem(eq);
                if (d && d->weapon.kind == "ranged" && !d->weapon.ammo_item.empty() && CountItem(d->weapon.ammo_item) < arch->starting_ammo)
                    AddItem(d->weapon.ammo_item, arch->starting_ammo - CountItem(d->weapon.ammo_item), false);
            }
        }
        player_.known_spells = arch->starting_spells;
    }
    player_.quick_slots = {"core:item.health_potion", "core:item.mana_potion", "core:item.stamina_tonic", "core:item.bread_loaf"};
    player_.health = static_cast<float>(MaxHealth());
    player_.stamina = static_cast<float>(MaxStamina());
    player_.mana = static_cast<float>(MaxMana());

    if (!content_.game_cfg.starting_quest.empty()) {
        player_.quest_stages[content_.game_cfg.starting_quest] = 0;
        player_.quest_log[content_.game_cfg.starting_quest].push_back(0);
    }

    screen_ = Screen::Playing;
    overlay_ = Overlay::None;
    LoadMap(content_.game_cfg.starting_map, content_.game_cfg.starting_spawn);
    if (boot_shot_.empty() && !selftest_ && !balance_) SaveGame("autosave"); // always leave something to reload after an early death

    // Prologue cards (story.prologue.1..N), then the death notice: the inciting document of Chapter Zero.
    narration_pages_.clear();
    for (int i = 1; i < 32; i++) {
        auto it = content_.loc_strings.find("story.prologue." + std::to_string(i));
        if (it == content_.loc_strings.end()) break;
        narration_pages_.push_back(it->second);
    }
    narration_page_ = 0;
    narration_time_ = 0.0f;
    narration_is_prologue_ = true;
    if (!narration_pages_.empty()) SetOverlay(Overlay::Narration);
    else AdvanceNarration();
}

void GameEngine::LoadMap(const std::string& mapId, const std::string& spawnId, bool keepPosition) {
    const MapDef* map = content_.GetMap(mapId);
    if (!map && !content_.maps.empty()) {
        // Older saves/configs may name a region that is now part of the seamless world.
        Logger::Warn("LoadMap: unknown map '" + mapId + "', falling back to the first loaded map");
        map = content_.GetMap(content_.game_cfg.starting_map);
        if (!map) map = &content_.maps.begin()->second;
    }
    if (!map) {
        Logger::Error("LoadMap: no maps loaded");
        return;
    }
    current_map_ = map->id;
    BuildScene();
    if (!keepPosition) {
        auto sp = map->spawns.find(spawnId);
        if (sp == map->spawns.end()) sp = map->spawns.begin();
        if (sp != map->spawns.end()) {
            player_.pos = sp->second.pos;
            player_.yaw = sp->second.yaw_degrees * DEG2RAD;
        }
        player_.pitch = 0.0f;
    }
    player_.pos.y = GroundHeight({player_.pos.x, player_.pos.y + 0.5f, player_.pos.z}, kStepHeight);
    player_.vel = {0, 0, 0};
    attack_timer_ = -1.0f;
    drawing_bow_ = false;
    bow_draw_ = 0.0f;
    charging_ = false;
    sim_accum_ = 0.0f;
    zone_id_ = "?"; // force the banner + audio for the arrival zone
    UpdateAtmosphere(0.0f, true);
    Logger::Info("Entered region " + mapId);
}

void GameEngine::BuildScene() {
    const MapDef* map = content_.GetMap(current_map_);
    scene_ = Scene{};
    scene_.map = map;
    if (!map) return;
    MapPersist& ps = persist_[current_map_];

    for (const auto& p : map->props) {
        PropInstance pi;
        pi.id = p.id;
        pi.model_path = p.model;
        BoundingBox lb = res_.GetModelBounds(p.model);
        pi.transform = AnchoredTransform(lb, p.pos, p.rot_y, p.scale);
        pi.uv_scale = p.uv_scale;
        pi.world_box = TransformBox(lb, pi.transform);
        pi.collider = pi.world_box;
        pi.solid = p.solid;
        float h = pi.world_box.max.y - pi.world_box.min.y;
        pi.walkable = !p.solid && h <= 0.7f && p.ramp_dir.empty();
        if (p.ramp_dir == "+x") pi.ramp_axis = 1;
        else if (p.ramp_dir == "-x") pi.ramp_axis = 2;
        else if (p.ramp_dir == "+z") pi.ramp_axis = 3;
        else if (p.ramp_dir == "-z") pi.ramp_axis = 4;
        if (p.model.find("tree") != std::string::npos) {
            // Foliage is soft; only the trunk blocks movement.
            Vector3 c = Vector3Scale(Vector3Add(pi.world_box.min, pi.world_box.max), 0.5f);
            pi.collider = {{c.x - 0.35f, pi.world_box.min.y, c.z - 0.35f}, {c.x + 0.35f, pi.world_box.max.y, c.z + 0.35f}};
        }
        scene_.props.push_back(pi);
    }

    for (const auto& d : map->interactables) {
        if (d.type == "pickup") {
            if (ps.used.count(d.instance_id)) continue;
            WorldPickup wp;
            wp.key = d.instance_id;
            wp.item_id = d.item_id;
            wp.qty = d.qty;
            wp.pos = d.pos;
            wp.spin = static_cast<float>(scene_.pickups.size()) * 1.7f;
            if (const ItemDef* it = content_.GetItem(d.item_id)) wp.model = it->world_model;
            scene_.pickups.push_back(wp);
            continue;
        }
        InteractableInstance in;
        in.def = d;
        if (d.type == "harvest") {
            auto h = ps.harvested.find(d.instance_id);
            in.used = h != ps.harvested.end() && player_.play_time - h->second < d.respawn_seconds;
        }
        if (!d.model.empty()) {
            BoundingBox lb = res_.GetModelBounds(d.model);
            in.base_transform = AnchoredTransform(lb, d.pos, d.rot_y, d.scale);
            in.world_box = TransformBox(lb, in.base_transform);
        } else {
            in.base_transform = MatrixTranslate(d.pos.x, d.pos.y, d.pos.z);
            in.world_box = {{d.pos.x - 0.4f, d.pos.y, d.pos.z - 0.4f}, {d.pos.x + 0.4f, d.pos.y + 0.8f, d.pos.z + 0.4f}};
        }
        in.open = ps.open.count(d.instance_id) > 0;
        in.open_anim = in.open ? 1.0f : 0.0f;
        in.locked = d.locked && !ps.unlocked.count(d.instance_id);
        in.used = ps.used.count(d.instance_id) > 0;
        scene_.interactables.push_back(in);
    }

    for (const auto& n : map->npcs) {
        const NpcDef* def = content_.GetNpc(n.npc_id);
        if (!def) continue;
        NpcInstance ni;
        ni.instance_id = n.instance_id;
        ni.def = def;
        ni.pos = n.pos;
        ni.yaw = ni.base_yaw = n.yaw * DEG2RAD;
        ni.anim_time = RandF() * 3.0f;
        ni.home = n.pos;
        ni.requires_flag = n.requires_flag;
        ni.hidden_flag = n.hidden_flag;
        ni.hidden = (!n.requires_flag.empty() && !player_.flags.count(n.requires_flag)) ||
                    (!n.hidden_flag.empty() && player_.flags.count(n.hidden_flag));  // right from the first frame
        scene_.npcs.push_back(ni);
    }

    pending_spawns_.clear();
    for (const auto& c : map->creatures) {
        if (!c.requires_flag.empty() && !player_.flags.count(c.requires_flag)) { pending_spawns_.push_back(&c); continue; }
        SpawnCreature(c);
    }

    for (const auto& l : map->lights) scene_.static_lights.push_back({l.pos, l.color, l.radius});
    for (const auto& p : map->props) {
        if (p.emitter_sprite.empty() && p.emitter_light_radius <= 0.0f) continue;
        Vector3 world = Vector3Add(p.pos, Vector3RotateByAxisAngle(p.emitter_offset, {0, 1, 0}, p.rot_y * DEG2RAD));
        if (!p.emitter_sprite.empty())
            scene_.emitters.push_back({world, p.emitter_sprite, p.emitter_size, static_cast<float>(scene_.emitters.size()) * 0.37f});
        if (p.emitter_light_radius > 0.0f) scene_.static_lights.push_back({world, p.emitter_light_color, p.emitter_light_radius});
    }

    RebuildColliders();
    for (auto& c : scene_.creatures) c.pos.y = GroundHeight({c.pos.x, c.pos.y + 0.5f, c.pos.z}, kStepHeight);
    for (auto& n : scene_.npcs) n.pos.y = GroundHeight({n.pos.x, n.pos.y + 0.5f, n.pos.z}, kStepHeight);
}

void GameEngine::HotReload() {
    Logger::Info("Hot reload requested (F5)");
    content_.LoadAllContent(".");
    content_.ValidateAll(".");
    res_.UnloadAll();
    renderer_.ReloadShaders();
    if (screen_ == Screen::Playing && !current_map_.empty()) {
        Vector3 pos = player_.pos;
        float yaw = player_.yaw;
        LoadMap(current_map_, "", true);
        player_.pos = pos;
        player_.yaw = yaw;
        StopMapAudio();
        PlayMapAudio(scene_.map);
    }
    int errs = 0;
    for (const auto& v : content_.validation_issues) errs += v.is_error ? 1 : 0;
    Toast(errs == 0 ? "Hot reload complete: content valid" : "Hot reload: " + std::to_string(errs) + " validation error(s)",
          errs == 0 ? Color{140, 220, 140, 255} : Color{255, 120, 100, 255});
}

void GameEngine::ReturnToTitle() {
    StopMapAudio();
    screen_ = Screen::Title;
    overlay_ = Overlay::None;
    scene_ = Scene{};
    current_map_.clear();
    EnableCursor();
}

// ============================================================================
// Frame update
// ============================================================================
void GameEngine::SetOverlay(Overlay o) {
    if (o == Overlay::None && overlay_ == Overlay::Dialogue) dialogue_id_.clear();
    overlay_ = o;
    ui_scroll_ = 0.0f;
    charging_ = false;
    drawing_bow_ = false;
    bow_draw_ = 0.0f;
    blocking_ = false;
}

void GameEngine::Frame(float dt) {
    time_ += dt;
    UpdateAudio(dt);
    for (auto& t : toasts_) t.time -= dt;
    toasts_.erase(std::remove_if(toasts_.begin(), toasts_.end(), [](const ToastMsg& t) { return t.time <= 0; }), toasts_.end());
    if (region_banner_time_ > 0) region_banner_time_ -= dt;

    if (ActionPressed("debug_overlay")) debug_overlay_ = !debug_overlay_;
    if (IsKeyPressed(KEY_ENTER) && (IsKeyDown(KEY_LEFT_ALT) || IsKeyDown(KEY_RIGHT_ALT))) ToggleBorderlessWindowed();

    bool wantCursor = !(screen_ == Screen::Playing && overlay_ == Overlay::None);
    if (!boot_shot_.empty()) wantCursor = true;
    if (wantCursor && IsCursorHidden()) EnableCursor();
    if (!wantCursor && !IsCursorHidden()) { DisableCursor(); skip_mouse_frames_ = 2; }

    if (screen_ == Screen::Playing) UpdatePlaying(dt);
}

void GameEngine::UpdatePlaying(float dt) {
    UpdateAtmosphere(dt, false);
    if (ActionPressed("hot_reload")) { HotReload(); return; }

    if (overlay_ != Overlay::None) {
        bool esc = IsKeyPressed(KEY_ESCAPE);
        auto toggle = [&](const char* action, Overlay o) {
            if (ActionPressed(action) && overlay_ == o) { SetOverlay(Overlay::None); return true; }
            if (ActionPressed(action) && (overlay_ == Overlay::Inventory || overlay_ == Overlay::Character ||
                                          overlay_ == Overlay::Journal || overlay_ == Overlay::Map)) { SetOverlay(o); return true; }
            return false;
        };
        if (toggle("inventory", Overlay::Inventory) || toggle("character", Overlay::Character) ||
            toggle("journal", Overlay::Journal) || toggle("map", Overlay::Map)) return;
        if (overlay_ == Overlay::Dialogue) {
            std::vector<int> vis = VisibleChoices();
            for (int k = 0; k < 9; k++) {
                if (IsKeyPressed(KEY_ONE + k)) {
                    const DialogueDef* d = content_.GetDialogue(dialogue_id_);
                    auto nit = d ? d->nodes.find(dialogue_node_) : decltype(d->nodes.end()){};
                    if (d && nit != d->nodes.end() && nit->second.choices.empty() && k == 0) { EndDialogue(); return; }
                    if (k < static_cast<int>(vis.size())) { ChooseDialogue(vis[k]); return; }
                }
            }
            if (esc) EndDialogue();
            return;
        }
        if (overlay_ == Overlay::Container && ActionPressed("interact")) { TakeAllFromContainer(); return; }
        if (overlay_ == Overlay::Reader && (ActionPressed("interact") || IsKeyPressed(KEY_ENTER))) { SetOverlay(Overlay::None); return; }
        if (overlay_ == Overlay::Narration) {
            narration_time_ += dt;
            bool next = ActionPressed("interact") || IsKeyPressed(KEY_ENTER) || IsKeyPressed(KEY_SPACE) || IsMouseButtonPressed(MOUSE_BUTTON_LEFT);
            if (esc) { narration_page_ = static_cast<int>(narration_pages_.size()); AdvanceNarration(); return; }
            if (next && narration_time_ > 0.35f) { narration_page_++; narration_time_ = 0.0f; AdvanceNarration(); }
            return;
        }
        if (esc) {
            if (overlay_ == Overlay::Options) SetOverlay(options_from_title_ ? Overlay::None : Overlay::Pause);
            else SetOverlay(Overlay::None);
        }
        return;
    }

    player_.play_time += dt;

    // Mouse look (per frame for responsiveness)
    Vector2 md = GetMouseDelta();
    if (skip_mouse_frames_ > 0 || !boot_shot_.empty()) { skip_mouse_frames_--; md = {0, 0}; }
    float sens = content_.controls.mouse_sensitivity * DEG2RAD;
    player_.yaw -= md.x * sens;
    player_.pitch += (content_.controls.invert_y ? md.y : -md.y) * sens;
    player_.pitch = Clamp(player_.pitch, -1.45f, 1.45f);

    HandleGameplayInput(dt);
    if (fishing_) UpdateFishing(dt);
    if (overlay_ != Overlay::None || screen_ != Screen::Playing) return;

    sim_accum_ += dt;
    int steps = 0;
    while (sim_accum_ >= kFixedDt && steps < 6) {
        FixedUpdate(kFixedDt);
        sim_accum_ -= kFixedDt;
        steps++;
        if (screen_ != Screen::Playing) return;
    }
    if (steps == 6) sim_accum_ = 0.0f;

    UpdateInteractTarget();
}

void GameEngine::HandleGameplayInput(float dt) {
    if (IsKeyPressed(KEY_ESCAPE)) { SetOverlay(Overlay::Pause); return; }
    if (ActionPressed("inventory")) { SetOverlay(Overlay::Inventory); return; }
    if (ActionPressed("character")) { SetOverlay(Overlay::Character); return; }
    if (ActionPressed("journal")) { SetOverlay(Overlay::Journal); return; }
    if (ActionPressed("map")) { SetOverlay(Overlay::Map); return; }
    if (ActionPressed("quick_save")) { if (SaveGame("slot_1")) Toast("Game saved"); }
    if (ActionPressed("quick_load")) {
        if (SaveExists("slot_1")) { LoadGame("slot_1"); return; }
        Toast("No quick save found");
    }
    if (ActionPressed("interact")) { Interact(); if (overlay_ != Overlay::None) return; }

    const ItemDef* weapon = Equipped("main_hand");
    bool ranged = weapon && weapon->weapon.is_weapon && weapon->weapon.kind == "ranged";

    if (ranged) {
        const std::string& ammo = weapon->weapon.ammo_item;
        if (ActionPressed("attack") && attack_timer_ < 0) {
            if (ammo.empty() || CountItem(ammo) > 0) { drawing_bow_ = true; bow_draw_ = 0.0f; }
            else Toast("No arrows");
        }
        if (drawing_bow_) {
            bow_draw_ = std::min(1.0f, bow_draw_ + dt / std::max(0.2f, weapon->weapon.attack_time_seconds));
            if (ActionReleased("attack") || !ActionDown("attack")) {
                drawing_bow_ = false;
                if (bow_draw_ > 0.25f) FireArrow(bow_draw_);
                bow_draw_ = 0.0f;
            }
        }
        blocking_ = false;
    } else {
        if (ActionPressed("attack") && attack_timer_ < 0 && !blocking_) { charging_ = true; charge_time_ = 0.0f; }
        if (charging_) {
            charge_time_ += dt;
            if (ActionReleased("attack") || !ActionDown("attack")) {
                charging_ = false;
                StartAttack(charge_time_ >= 0.35f);
            }
        }
        bool wantBlock = ActionDown("block_or_aim") && attack_timer_ < 0 && player_.stamina > 1.0f;
        if (wantBlock && !blocking_) block_start_ = player_.play_time;
        blocking_ = wantBlock;
        if (blocking_) charging_ = false;
    }

    if (ActionPressed("cast_spell")) CastSelectedSpell();
    if (ActionPressed("cycle_spell") && !player_.known_spells.empty()) {
        player_.selected_spell = (player_.selected_spell + 1) % static_cast<int>(player_.known_spells.size());
        if (const SpellDef* s = content_.GetSpell(player_.known_spells[player_.selected_spell])) Toast("Spell: " + content_.Tr(s->name_key));
    }
    float wheel = GetMouseWheelMove();
    if (wheel != 0 && !player_.known_spells.empty()) {
        int n = static_cast<int>(player_.known_spells.size());
        player_.selected_spell = ((player_.selected_spell + (wheel < 0 ? 1 : -1)) % n + n) % n;
    }
    for (int i = 0; i < 4; i++) {
        if (ActionPressed("quick_slot_" + std::to_string(i + 1))) UseQuickSlot(i);
    }
}

void GameEngine::FixedUpdate(float dt) {
    UpdatePlayerMovement(dt);
    UpdateCombat(dt);
    UpdateCreatures(dt);
    UpdateProjectiles(dt);
    UpdateWorldObjects(dt);
    UpdateBuffs(dt);
    UpdateParticles(dt);
    CheckPressurePlates();

    if (player_.health <= 0.0f) {
        player_.health = 0.0f;
        screen_ = Screen::Dead;
        death_tip_ = static_cast<int>(RandF() * 1000.0f);
        overlay_ = Overlay::None;
        PlaySfxAt("assets/audio/sfx/player_hurt.wav", player_.pos, 1.0f);
        EnableCursor();
    }
}

// ============================================================================
// Player movement
// ============================================================================
void GameEngine::UpdatePlayerMovement(float dt) {
    Vector3 fwd = Forward(player_.yaw);
    // Right vector for forward (sin y, 0, cos y).
    Vector3 right = {-cosf(player_.yaw), 0.0f, sinf(player_.yaw)};

    Vector3 wish = {0, 0, 0};
    if (ActionDown("move_forward")) wish = Vector3Add(wish, fwd);
    if (ActionDown("move_backward")) wish = Vector3Subtract(wish, fwd);
    if (ActionDown("move_right")) wish = Vector3Add(wish, right);
    if (ActionDown("move_left")) wish = Vector3Subtract(wish, right);
    bool moving = Vector3LengthSqr(wish) > 0.01f;
    if (moving) wish = Vector3Normalize(wish);

    player_.crouching = ActionDown("crouch");
    float targetEye = player_.crouching ? 1.05f : 1.6f;
    player_.eye_height += (targetEye - player_.eye_height) * std::min(1.0f, dt * 12.0f);

    bool overweight = CarriedWeight() > CarryCapacity();
    bool sprinting = moving && ActionDown("sprint") && !player_.crouching && !overweight && player_.stamina > 2.0f &&
                     !blocking_ && !drawing_bow_;
    float speed = MoveSpeed();
    if (sprinting) speed *= 1.55f;
    if (player_.crouching) speed *= 0.5f;
    if (blocking_ || drawing_bow_) speed *= 0.6f;

    if (sprinting) {
        player_.stamina -= 13.0f * dt;
        stamina_delay_ = 0.6f;
        sprint_accum_ += dt;
        if (sprint_accum_ > 5.0f) { sprint_accum_ = 0; GainSkillXp("athletics", 1.0f, true); }
    }

    // Horizontal velocity responds quickly on the ground, sluggishly in the air.
    float accel = player_.on_ground ? 14.0f : 3.0f;
    Vector3 target = Vector3Scale(wish, speed);
    player_.vel.x += (target.x - player_.vel.x) * std::min(1.0f, accel * dt);
    player_.vel.z += (target.z - player_.vel.z) * std::min(1.0f, accel * dt);

    if (ActionPressed("jump") && player_.on_ground && player_.stamina > 5.0f && !player_.crouching) {
        player_.vel.y = 5.4f;
        player_.on_ground = false;
        player_.stamina -= 6.0f;
        stamina_delay_ = 0.6f;
        GainSkillXp("athletics", 0.3f);
    }
    player_.vel.y -= kGravity * dt;

    float height = player_.crouching ? 1.2f : 1.75f;
    Vector3 delta = {player_.vel.x * dt, 0, player_.vel.z * dt};
    player_.pos = MoveWithCollision(player_.pos, delta, kPlayerRadius, height, true);

    float wasY = player_.pos.y;
    player_.pos.y += player_.vel.y * dt;
    float ground = GroundHeight({player_.pos.x, std::max(player_.pos.y, wasY), player_.pos.z}, kStepHeight);
    bool wasGround = player_.on_ground;
    if (player_.pos.y <= ground + 0.001f) {
        if (!wasGround && player_.vel.y < -9.0f) {
            float fallDmg = (-player_.vel.y - 9.0f) * 4.0f;
            player_.health -= fallDmg;
            damage_flash_ = 0.4f;
        }
        player_.pos.y = ground;
        player_.vel.y = 0.0f;
        player_.on_ground = true;
    } else if (wasGround && player_.vel.y <= 0.0f && player_.pos.y - ground < 0.35f) {
        player_.pos.y = ground; // stick to stairs / slab edges going down
        player_.vel.y = 0.0f;
        player_.on_ground = true;
    } else {
        player_.on_ground = false;
    }

    // Head bob, footsteps & noise
    float hspeed = sqrtf(player_.vel.x * player_.vel.x + player_.vel.z * player_.vel.z);
    if (player_.on_ground && hspeed > 0.5f) {
        bob_phase_ += dt * hspeed * 2.2f;
        step_timer_ -= dt * hspeed;
        if (step_timer_ <= 0.0f) {
            step_timer_ = 2.1f;
            float vol = player_.crouching ? 0.12f : (sprinting ? 0.45f : 0.3f);
            res_.PlaySfx("assets/audio/sfx/footstep_stone.wav", vol, 0.9f + RandF() * 0.2f);
        }
    }
    making_noise_ = (sprinting || attack_timer_ >= 0.0f) || (hspeed > 0.5f && !player_.crouching);
    UpdateSanity(dt);

    if (player_.crouching && hspeed > 0.3f) {
        for (const auto& c : scene_.creatures) {
            if (c.state != CreatureState::Dead && !c.alerted && Vector3Distance(c.pos, player_.pos) < 8.0f) {
                sneak_accum_ += dt;
                break;
            }
        }
        if (sneak_accum_ > 3.0f) { sneak_accum_ = 0; GainSkillXp("stealth", 1.0f, true); }
    }

    // Regeneration
    stamina_delay_ -= dt;
    if (stamina_delay_ <= 0.0f && !blocking_)
        player_.stamina += content_.balancing.stamina_regen_per_sec * dt;
    player_.mana += content_.balancing.mana_regen_per_sec * (1.0f + (Attr("will") - 10) * 0.04f) * dt;
    player_.health += Bonus("health_regen") * dt;
    player_.stamina += Bonus("stamina_regen") * dt;
    ClampVitals();
}

void GameEngine::RebuildColliders() {
    solids_.clear();
    walkables_.clear();
    ramps_.clear();
    for (const auto& p : scene_.props) {
        if (p.ramp_axis != 0) ramps_.push_back({p.world_box, p.ramp_axis});
        else if (p.solid) solids_.push_back(p.collider);
        else if (p.walkable) walkables_.push_back(p.world_box);
    }
    for (const auto& in : scene_.interactables) {
        const std::string& t = in.def.type;
        if (t == "door") {
            if (in.open_anim < 0.5f && !in.open) solids_.push_back(in.world_box);
        } else if (t == "chest" || t == "readable" || t == "quest_pedestal") {
            solids_.push_back(in.world_box);
        } else if (t == "pressure_plate") {
            walkables_.push_back(in.world_box);
        }
    }
}

float GameEngine::GroundHeight(Vector3 pos, float stepHeight) const {
    float best = -1000.0f;
    auto consider = [&](const BoundingBox& b) {
        if (pos.x < b.min.x || pos.x > b.max.x || pos.z < b.min.z || pos.z > b.max.z) return;
        float top = b.max.y;
        if (top <= pos.y + stepHeight && top > best) best = top;
    };
    for (const auto& b : walkables_) consider(b);
    for (const auto& b : solids_) consider(b);
    for (const auto& [b, axis] : ramps_) {
        if (pos.x < b.min.x || pos.x > b.max.x || pos.z < b.min.z || pos.z > b.max.z) continue;
        float t = 0.0f;
        switch (axis) {
            case 1: t = (pos.x - b.min.x) / std::max(0.01f, b.max.x - b.min.x); break;
            case 2: t = (b.max.x - pos.x) / std::max(0.01f, b.max.x - b.min.x); break;
            case 3: t = (pos.z - b.min.z) / std::max(0.01f, b.max.z - b.min.z); break;
            default: t = (b.max.z - pos.z) / std::max(0.01f, b.max.z - b.min.z); break;
        }
        float top = b.min.y + (b.max.y - b.min.y) * Clamp(t, 0.0f, 1.0f);
        if (top <= pos.y + stepHeight && top > best) best = top;
    }
    return best < -999.0f ? 0.0f : best;
}

Vector3 GameEngine::MoveWithCollision(Vector3 pos, Vector3 delta, float radius, float height, bool isPlayer, int selfCreature) {
    float len = Vector3Length(delta);
    int steps = std::max(1, static_cast<int>(std::ceil(len / 0.15f)));
    Vector3 step = Vector3Scale(delta, 1.0f / steps);
    for (int s = 0; s < steps; s++) {
        pos.x += step.x;
        pos.z += step.z;
        for (int iter = 0; iter < 3; iter++) {
            for (const auto& b : solids_) {
                if (b.max.y <= pos.y + kStepHeight || b.min.y >= pos.y + height) continue;
                float minX = b.min.x - radius, maxX = b.max.x + radius;
                float minZ = b.min.z - radius, maxZ = b.max.z + radius;
                if (pos.x <= minX || pos.x >= maxX || pos.z <= minZ || pos.z >= maxZ) continue;
                float pl = pos.x - minX, pr = maxX - pos.x, pb = pos.z - minZ, pf = maxZ - pos.z;
                float m = std::min(std::min(pl, pr), std::min(pb, pf));
                if (m == pl) pos.x = minX;
                else if (m == pr) pos.x = maxX;
                else if (m == pb) pos.z = minZ;
                else pos.z = maxZ;
            }
        }
        // Soft circle pushes between actors.
        auto pushFrom = [&](Vector3 other, float otherR) {
            float dx = pos.x - other.x, dz = pos.z - other.z;
            float d = sqrtf(dx * dx + dz * dz);
            float minD = radius + otherR;
            if (d < minD && d > 0.0001f) {
                pos.x = other.x + dx / d * minD;
                pos.z = other.z + dz / d * minD;
            }
        };
        for (size_t i = 0; i < scene_.creatures.size(); i++) {
            const auto& c = scene_.creatures[i];
            if (c.state == CreatureState::Dead || static_cast<int>(i) == selfCreature) continue;
            pushFrom(c.pos, c.radius);
        }
        for (const auto& n : scene_.npcs)
            if (!n.companion && !n.hidden) pushFrom(n.pos, 0.35f);  // a companion never body-blocks a corridor
        if (!isPlayer) pushFrom(player_.pos, kPlayerRadius);
    }
    return pos;
}

bool GameEngine::SegmentHitsWorld(Vector3 a, Vector3 b, float& tHit, Vector3& normal) const {
    Vector3 d = Vector3Subtract(b, a);
    float len = Vector3Length(d);
    if (len < 1e-5f) return false;
    Ray ray = {a, Vector3Scale(d, 1.0f / len)};
    bool hit = false;
    tHit = len;
    auto test = [&](const BoundingBox& box) {
        RayCollision rc = GetRayCollisionBox(ray, box);
        if (rc.hit && rc.distance >= 0.0f && rc.distance < tHit) {
            tHit = rc.distance;
            normal = rc.normal;
            hit = true;
        }
    };
    for (const auto& box : solids_) test(box);
    for (const auto& box : walkables_) test(box);
    if (hit) tHit /= len;
    return hit;
}

bool GameEngine::LineOfSight(Vector3 a, Vector3 b) const {
    Vector3 d = Vector3Subtract(b, a);
    float len = Vector3Length(d);
    if (len < 1e-4f) return true;
    Ray ray = {a, Vector3Scale(d, 1.0f / len)};
    float lowY = std::min(a.y, b.y);
    for (const auto& box : solids_) {
        if (box.max.y < lowY) continue;
        RayCollision rc = GetRayCollisionBox(ray, box);
        if (rc.hit && rc.distance > 0.0f && rc.distance < len - 0.05f) return false;
    }
    return true;
}

// ============================================================================
// Character
// ============================================================================
const ItemDef* GameEngine::Equipped(const std::string& slot) const {
    auto it = player_.equipment.find(slot);
    if (it == player_.equipment.end() || it->second.empty()) return nullptr;
    return content_.GetItem(it->second);
}

int GameEngine::Attr(const std::string& id) const {
    auto it = player_.attributes.find(id);
    int v = it != player_.attributes.end() ? it->second : 10;
    for (const auto& [slot, itemId] : player_.equipment) {
        if (const ItemDef* d = content_.GetItem(itemId)) {
            for (const auto& e : d->effects)
                if (e.type == "stat_bonus" && e.stat == id) v += e.amount;
        }
    }
    return v;
}

int GameEngine::SkillLevel(const std::string& id) const {
    auto it = player_.skills.find(id);
    return it != player_.skills.end() ? it->second.level : 0;
}

float GameEngine::SkillEffect(const std::string& id) const {
    float per = 0.015f;
    for (const auto& s : content_.skills) if (s.id == id) per = s.effect_per_point;
    return SkillLevel(id) * per;
}

int GameEngine::MaxHealth() const {
    const BalancingDef& b = content_.balancing;
    return std::max(10, b.base_health + b.health_per_endurance * (Attr("endurance") - 10) + 6 * (player_.level - 1));
}
int GameEngine::MaxStamina() const {
    const BalancingDef& b = content_.balancing;
    return std::max(10, b.base_stamina + b.stamina_per_endurance * (Attr("endurance") - 10) + b.stamina_per_agility * (Attr("agility") - 10));
}
int GameEngine::MaxMana() const {
    const BalancingDef& b = content_.balancing;
    return std::max(0, b.base_mana + b.mana_per_intellect * (Attr("intellect") - 10) + b.mana_per_will * (Attr("will") - 10));
}
float GameEngine::CarryCapacity() const {
    return content_.balancing.base_carry_weight + content_.balancing.carry_weight_per_might * Attr("might");
}
float GameEngine::CarriedWeight() const {
    float w = 0;
    for (const auto& it : player_.inventory)
        if (const ItemDef* d = content_.GetItem(it.id)) w += d->weight * it.qty;
    return w;
}
int GameEngine::ArmorRating() const {
    int a = 0;
    for (const auto& [slot, id] : player_.equipment)
        if (const ItemDef* d = content_.GetItem(id)) a += d->armor;
    for (const auto& b : player_.buffs)
        if (b.primitive == "buff_armor") a += static_cast<int>(b.power);
    a += static_cast<int>(Bonus("armor_bonus"));
    return a;
}
bool GameEngine::SynergyActive(const SynergyDef& s) const {
    for (const auto& [skill, lvl] : s.requirements)
        if (SkillLevel(skill) < lvl) return false;
    return true;
}
float GameEngine::SynergyBonus(const std::string& key) const {
    float v = 0.0f;
    for (const auto& s : content_.synergies) {
        if (!SynergyActive(s)) continue;
        auto it = s.bonuses.find(key);
        if (it != s.bonuses.end()) v += it->second;
    }
    return v;
}
float GameEngine::GearBonus(const std::string& key) const {
    float v = 0.0f;
    for (const auto& [slot, id] : player_.equipment)
        if (const ItemDef* d = content_.GetItem(id))
            for (const auto& e : d->effects)
                if (e.type == "bonus" && e.stat == key) v += e.value;
    return v;
}
float GameEngine::BuffBonus(const std::string& key) const {
    float v = 0.0f;
    for (const auto& b : player_.buffs)
        if (b.bonus_key == key) v += b.bonus_value;
    return v;
}
float GameEngine::Bonus(const std::string& key) const { return SynergyBonus(key) + GearBonus(key) + BuffBonus(key) + PerkBonus(key); }

float GameEngine::PerkBonus(const std::string& key) const {
    float v = 0.0f;
    for (const auto& id : player_.perks)
        if (const PerkDef* p = content_.GetPerk(id)) {
            auto it = p->bonuses.find(key);
            if (it != p->bonuses.end()) v += it->second;
        }
    return v;
}

bool GameEngine::PerkAvailable(const PerkDef& p) const {
    if (SkillLevel(p.skill) < p.level || player_.perks.count(p.id)) return false;
    for (const auto& o : content_.perks)
        if (o.skill == p.skill && o.level == p.level && player_.perks.count(o.id)) return false;  // that milestone's choice is made
    return true;
}

int GameEngine::PendingPerks() const {
    std::set<std::pair<std::string, int>> open;
    for (const auto& p : content_.perks)
        if (PerkAvailable(p)) open.insert({p.skill, p.level});
    return static_cast<int>(open.size());
}

void GameEngine::ChoosePerk(const std::string& id) {
    const PerkDef* p = content_.GetPerk(id);
    if (!p || !PerkAvailable(*p)) return;
    player_.perks.insert(id);
    res_.PlaySfx("assets/audio/sfx/level_up.wav", 0.6f, 1.2f);
    Toast("Perk: " + content_.Tr(p->name_key), Color{255, 210, 120, 255});
    ClampVitals();
}

float GameEngine::MeleeHitDamage(const ItemDef* w, bool heavy) const {
    std::string skill = w ? w->weapon.skill : "athletics";
    float base = w ? static_cast<float>(w->weapon.base_damage) : 4.0f;
    float dmg = base * (1.0f + SkillEffect(skill)) * (1.0f + (Attr("might") - 10) * 0.03f) * DifficultyPlayerMult();
    if (heavy) dmg *= content_.balancing.heavy_attack_damage_mult;
    return dmg + Bonus("melee_bonus_magic_damage");
}
float GameEngine::ArrowHitDamage(const ItemDef* w, float draw) const {
    if (!w) return 0.0f;
    return w->weapon.base_damage * (1.0f + SkillEffect(w->weapon.skill)) * (0.35f + 0.65f * draw) * DifficultyPlayerMult();
}
float GameEngine::CritChance(const ItemDef* w) const {
    float c = (w ? w->weapon.crit_chance : 0.0f) + (Attr("agility") - 10) * 0.005f + SkillEffect("perception") * 0.15f + Bonus("crit_chance_bonus");
    return Clamp(c, 0.0f, 0.75f);
}
float GameEngine::CritMult(const ItemDef* w) const { return (w ? w->weapon.crit_mult : 1.5f) + Bonus("crit_damage_bonus"); }
float GameEngine::SpellPowerMult(const SpellDef& s) const {
    float m = (1.0f + SkillEffect(s.skill)) * (1.0f + Bonus("spell_power_bonus"));
    if (s.effect.primitive == "projectile_damage") m *= (1.0f + (Attr("intellect") - 10) * 0.025f) * DifficultyPlayerMult();
    return m;
}
float GameEngine::SpellCost(const SpellDef& s) const {
    float red = std::min(0.3f, SkillEffect(s.skill) * 0.4f) + Bonus("spell_cost_reduction");
    return s.mana_cost * (1.0f - std::min(0.5f, red));
}
float GameEngine::LockpickChance(int difficulty) const {
    return Clamp(0.45f + (SkillLevel("lockpicking") - difficulty) * 0.035f + (Attr("agility") - 10) * 0.02f + Bonus("lockpick_bonus"), 0.08f, 0.95f);
}
float GameEngine::ShopDiscount() const {
    return std::min(0.35f, std::min(0.3f, SkillLevel("persuasion") * 0.006f + (Attr("presence") - 10) * 0.02f) + Bonus("shop_discount"));
}

float GameEngine::MoveSpeed() const {
    float s = 4.2f * (1.0f + SkillEffect("athletics") * 0.5f) * (1.0f + Bonus("move_speed_bonus")) * (1.0f + (Attr("agility") - 10) * 0.01f);
    if (CarriedWeight() > CarryCapacity()) s *= 0.55f;
    return s;
}
float GameEngine::Visibility() const {
    float v = 1.0f;
    if (player_.crouching) v *= 0.55f * (1.0f - std::min(0.5f, SkillEffect("stealth"))) * (1.0f - std::min(0.5f, Bonus("sneak_visibility_reduction")));
    for (const auto& b : player_.buffs) {
        if (b.primitive == "buff_stealth") v *= b.visibility;
        if (b.primitive == "buff_light") v *= 1.15f;
    }
    return v;
}

void GameEngine::ClampVitals() {
    player_.health = std::min(player_.health, static_cast<float>(MaxHealth()));
    player_.stamina = Clamp(player_.stamina, 0.0f, static_cast<float>(MaxStamina()));
    player_.mana = Clamp(player_.mana, 0.0f, static_cast<float>(MaxMana()));
}

void GameEngine::GainSkillXp(const std::string& skill, float amount, bool bypassCooldown) {
    if (skill.empty() || amount <= 0) return;
    auto& s = player_.skills[skill];
    double now = player_.play_time;
    if (!bypassCooldown && now - s.last_gain < content_.balancing.skill_anti_exploit_cooldown_sec) return;
    s.last_gain = now;
    amount /= (1.0f + content_.balancing.skill_diminishing_factor * (s.level / 10.0f));
    amount *= 1.0f + Bonus("skill_xp_bonus");
    s.xp += amount;
    for (;;) {
        float needed = 6.0f + s.level * 0.6f;
        if (s.xp < needed || s.level >= 100) break;
        s.xp -= needed;
        s.level++;
        std::string name = skill;
        for (const auto& sd : content_.skills) if (sd.id == skill) name = content_.Tr(sd.name_key);
        Toast(name + " increased to " + std::to_string(s.level), Color{150, 200, 255, 255});
        for (const auto& p : content_.perks)
            if (p.skill == skill && p.level == s.level) {
                Toast("New perk available in " + name + "! [" + BindingLabel("character") + "]", Color{255, 210, 120, 255});
                break;
            }
        for (const auto& syn : content_.synergies) {
            auto req = syn.requirements.find(skill);
            if (req != syn.requirements.end() && req->second == s.level && SynergyActive(syn))
                Toast("Synergy unlocked: " + content_.Tr(syn.name_key), Color{255, 210, 120, 255});
        }
    }
}

void GameEngine::GainXp(int amount) {
    const RaceDef* race = content_.GetRace(player_.race_id);
    float mult = race ? race->xp_gain_multiplier : 1.0f;
    player_.xp += static_cast<int>(std::round(amount * mult));
    while (player_.xp >= 100 * player_.level) {
        player_.xp -= 100 * player_.level;
        player_.level++;
        player_.unspent_points++;
        player_.health = static_cast<float>(MaxHealth());
        player_.stamina = static_cast<float>(MaxStamina());
        player_.mana = static_cast<float>(MaxMana());
        res_.PlaySfx("assets/audio/sfx/level_up.wav", 0.8f);
        Toast("Level " + std::to_string(player_.level) + "! Attribute point available [" + BindingLabel("character") + "]",
              Color{255, 220, 120, 255});
        if (int ci = CompanionIndex(); ci >= 0) CompanionSay(scene_.npcs[ci].def->companion.level_lines);
    }
}

// ============================================================================
// Inventory
// ============================================================================
int GameEngine::CountItem(const std::string& id) const {
    int n = 0;
    for (const auto& it : player_.inventory) if (it.id == id) n += it.qty;
    return n;
}

bool GameEngine::IsEquipped(const std::string& id) const {
    for (const auto& [slot, e] : player_.equipment) if (e == id) return true;
    return false;
}

void GameEngine::AddItem(const std::string& id, int qty, bool announce) {
    const ItemDef* d = content_.GetItem(id);
    if (!d || qty <= 0) {
        if (!d) Logger::Warn("AddItem: unknown item '" + id + "'");
        return;
    }
    if (d->quest_item && CountItem(id) > 0) return; // quest documents are unique
    bool merged = false;
    if (d->stackable || d->category == "ammo") {
        for (auto& it : player_.inventory) {
            if (it.id == id) { it.qty += qty; merged = true; break; }
        }
    }
    if (!merged) {
        if (d->stackable || d->category == "ammo") player_.inventory.push_back({id, qty});
        else for (int i = 0; i < qty; i++) player_.inventory.push_back({id, 1});
    }
    if (announce) Toast("+ " + content_.Tr(d->name_key) + (qty > 1 ? " x" + std::to_string(qty) : ""));
}

bool GameEngine::RemoveItem(const std::string& id, int qty) {
    if (CountItem(id) < qty) return false;
    for (auto it = player_.inventory.begin(); it != player_.inventory.end() && qty > 0;) {
        if (it->id == id) {
            int take = std::min(qty, it->qty);
            it->qty -= take;
            qty -= take;
            if (it->qty <= 0) { it = player_.inventory.erase(it); continue; }
        }
        ++it;
    }
    if (CountItem(id) == 0) {
        for (auto& [slot, e] : player_.equipment) if (e == id) e.clear();
    }
    return true;
}

void GameEngine::EquipItem(const std::string& id) {
    const ItemDef* d = content_.GetItem(id);
    if (!d || d->slots.empty() || CountItem(id) == 0) return;
    const std::string& slot = d->slots[0];
    // Two-handed bows and shields don't mix.
    if (slot == "main_hand" && d->weapon.kind == "ranged") UnequipSlot("off_hand");
    if (slot == "off_hand") {
        const ItemDef* main = Equipped("main_hand");
        if (main && main->weapon.kind == "ranged") UnequipSlot("main_hand");
    }
    player_.equipment[slot] = id;
    attack_timer_ = -1.0f;
    ClampVitals();
}

void GameEngine::UnequipSlot(const std::string& slot) {
    player_.equipment.erase(slot);
    ClampVitals();
}

void GameEngine::ReadItem(const ItemDef& item) {
    reader_title_ = content_.Tr(item.name_key);
    reader_text_ = content_.Tr(item.book_text_key.empty() ? item.description_key : item.book_text_key);
    res_.PlaySfx("assets/audio/sfx/page_turn.wav", 0.7f);
    if (!player_.claimed.count("read:" + item.id)) {
        player_.claimed.insert("read:" + item.id);
        GainSkillXp("lore", 2.0f, true);
    }
    for (const auto& e : item.effects) {
        if (e.type != "learn_spell") continue;
        if (std::find(player_.known_spells.begin(), player_.known_spells.end(), e.spell_id) == player_.known_spells.end()) {
            player_.known_spells.push_back(e.spell_id);
            if (const SpellDef* s = content_.GetSpell(e.spell_id)) {
                Toast("Learned spell: " + content_.Tr(s->name_key), Color{180, 160, 255, 255});
                reader_text_ += "\n\n[You have learned " + content_.Tr(s->name_key) + ". The tome crumbles to ash.]";
            }
            RemoveItem(item.id, 1);
        } else {
            reader_text_ += "\n\n[You already know this spell.]";
        }
    }
    SetOverlay(Overlay::Reader);
}

void GameEngine::UseItem(const std::string& id) {
    const ItemDef* d = content_.GetItem(id);
    if (!d || CountItem(id) == 0) return;
    if (d->category == "book") { ReadItem(*d); return; }
    if (!d->slots.empty()) {
        if (IsEquipped(id)) UnequipSlot(d->slots[0]);
        else EquipItem(id);
        return;
    }
    if (d->category == "consumable") {
        for (const auto& e : d->effects) {
            float pot = 1.0f + Bonus("potion_bonus");
            if (e.type == "consumable_heal") player_.health += e.amount * pot;
            else if (e.type == "consumable_mana") player_.mana += e.amount * pot;
            else if (e.type == "consumable_stamina") player_.stamina += e.amount * pot;
            else if (e.type == "consumable_sanity") ChangeSanity(static_cast<float>(e.amount) * pot);
            else if (e.type == "weapon_oil") {
                // Coat your weapon: hits apply a status for a while. A new oil replaces the old one.
                player_.buffs.erase(std::remove_if(player_.buffs.begin(), player_.buffs.end(), [](const ActiveBuff& b) { return b.primitive == "oil"; }),
                                    player_.buffs.end());
                ActiveBuff b;
                b.primitive = "oil";
                b.item_id = d->id;
                b.status = e.stat;
                b.status_chance = e.value;
                b.status_power = static_cast<float>(e.amount);
                b.status_duration = 4.0f;
                b.remaining = b.duration = e.duration;
                player_.buffs.push_back(b);
            }
            else if (e.type == "cast_spell") {
                // Wands: each charge casts its spell for free. The stack size is the charge count.
                if (const SpellDef* ws = content_.GetSpell(e.spell_id)) {
                    cast_flash_ = 1.0f;
                    cast_color_ = ws->effect.light_color;
                    cast_sprite_ = ws->effect.projectile_sprite.empty() ? "assets/sprites/vfx/spell_arcane.png" : ws->effect.projectile_sprite;
                    res_.PlaySfx(ws->cast_sfx, 0.75f);
                    CastSpell(*ws, true);
                }
            }
            else if (e.type == "buff") {
                // Food: a named build bonus for a while. Eating the same dish again refreshes it.
                ActiveBuff* slot = nullptr;
                for (auto& b : player_.buffs)
                    if (b.item_id == d->id && b.bonus_key == e.stat) slot = &b;
                if (!slot) { player_.buffs.push_back({}); slot = &player_.buffs.back(); }
                slot->primitive = "food";
                slot->item_id = d->id;
                slot->bonus_key = e.stat;
                slot->bonus_value = e.value;
                slot->remaining = slot->duration = e.duration;
            }
        }
        ClampVitals();
        RemoveItem(id, 1);
        res_.PlaySfx("assets/audio/sfx/spell_heal.wav", 0.5f, 1.2f);
        Toast("Used " + content_.Tr(d->name_key));
    }
}

void GameEngine::UseQuickSlot(int index) {
    const std::string& id = player_.quick_slots[index];
    if (id.empty()) return;
    if (CountItem(id) == 0) {
        const ItemDef* d = content_.GetItem(id);
        Toast(std::string("Out of ") + (d ? content_.Tr(d->name_key) : id));
        return;
    }
    UseItem(id);
}

// ============================================================================
// Combat
// ============================================================================
float GameEngine::DifficultyPlayerMult() const {
    auto it = content_.balancing.difficulties.find(content_.game_cfg.difficulty);
    return it != content_.balancing.difficulties.end() ? it->second.player_damage_mult : 1.0f;
}
float GameEngine::DifficultyEnemyMult() const {
    auto it = content_.balancing.difficulties.find(content_.game_cfg.difficulty);
    return it != content_.balancing.difficulties.end() ? it->second.enemy_damage_mult : 1.0f;
}

void GameEngine::StartAttack(bool heavy) {
    if (attack_timer_ >= 0) return;
    const ItemDef* w = Equipped("main_hand");
    float cost = w ? w->weapon.stamina_cost : 5.0f;
    float time = w ? w->weapon.attack_time_seconds : 0.45f;
    if (heavy) { cost *= content_.balancing.heavy_attack_stamina_mult; time *= 1.35f; }
    if (player_.stamina < cost * 0.5f) { Toast("Too exhausted to attack"); return; }
    player_.stamina -= cost;
    stamina_delay_ = 0.8f;
    attack_timer_ = 0.0f;
    attack_duration_ = time * (1.0f - std::min(0.25f, (Attr("agility") - 10) * 0.015f));
    attack_heavy_ = heavy;
    attack_hit_done_ = false;
    res_.PlaySfx("assets/audio/sfx/sword_swing.wav", heavy ? 0.8f : 0.6f, heavy ? 0.8f : 1.0f + RandF() * 0.15f);
}

void GameEngine::UpdateCombat(float dt) {
    if (attack_timer_ >= 0.0f) {
        attack_timer_ += dt;
        if (!attack_hit_done_ && attack_timer_ >= attack_duration_ * 0.4f) {
            attack_hit_done_ = true;
            ResolveMeleeHit();
        }
        if (attack_timer_ >= attack_duration_) attack_timer_ = -1.0f;
    }
    block_amount_ += ((blocking_ ? 1.0f : 0.0f) - block_amount_) * std::min(1.0f, dt * 14.0f);
    spell_cooldown_ = std::max(0.0f, spell_cooldown_ - dt);
    cast_flash_ = std::max(0.0f, cast_flash_ - dt * 2.5f);
    damage_flash_ = std::max(0.0f, damage_flash_ - dt * 1.5f);
    target_enemy_time_ = std::max(0.0f, target_enemy_time_ - dt);
}

void GameEngine::ResolveMeleeHit() {
    const ItemDef* w = Equipped("main_hand");
    float reach = w ? w->weapon.reach_meters : 1.6f;
    std::string skill = w ? w->weapon.skill : "athletics";
    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    Vector3 fwd = Forward(player_.yaw);

    CreatureInstance* best = nullptr;
    float bestD = 1e9f;
    for (auto& c : scene_.creatures) {
        if (c.state == CreatureState::Dead) continue;
        float d = HDist(c.pos, player_.pos) - c.radius;
        if (d > reach) continue;
        if (c.pos.y > player_.pos.y + 2.0f || c.pos.y + c.height < player_.pos.y) continue;
        Vector3 to = Vector3Subtract(c.pos, player_.pos);
        to.y = 0;
        float ang = acosf(Clamp(Vector3DotProduct(Vector3Normalize(to), fwd), -1.0f, 1.0f));
        if (ang > 55.0f * DEG2RAD && d > 0.4f) continue;
        if (!LineOfSight(eye, {c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z})) continue;
        if (d < bestD) { bestD = d; best = &c; }
    }
    if (!best) return;

    float dmg = MeleeHitDamage(w, attack_heavy_);
    bool sneak = !best->alerted;
    if (sneak) dmg *= (skill == "daggers" ? 2.5f : 1.75f) + Bonus("sneak_damage_bonus");
    if (attack_heavy_) dmg *= 1.0f + Bonus("heavy_damage_bonus");
    bool crit = RandF() < CritChance(w);
    if (crit) dmg *= CritMult(w);
    if (w && !w->weapon.bane_family.empty() && w->weapon.bane_family == best->def->family) dmg *= w->weapon.bane_mult;
    player_.mana += Bonus("mana_on_melee_hit") + (w ? w->weapon.mana_on_hit : 0.0f);
    int dealt = DamageCreature(*best, static_cast<int>(std::round(dmg)), sneak, skill, attack_heavy_, crit);
    if (crit && Bonus("crit_burn") > 0.0f && RandF() < Bonus("crit_burn")) ApplyStatus(*best, "burn", 6.0f, 3.0f);
    ApplyOilOnHit(*best);
    if (w && !w->weapon.on_hit_status.empty())
        TryStatus(*best, w->weapon.on_hit_status, w->weapon.status_chance * (attack_heavy_ ? 1.5f : 1.0f), w->weapon.status_power,
                  w->weapon.status_duration);
    float steal = (w ? w->weapon.life_steal : 0.0f) + Bonus("life_steal");
    if (steal > 0.0f && dealt > 0) player_.health += dealt * steal;
    ClampVitals();
    GainSkillXp(skill, attack_heavy_ ? 1.6f : 1.1f);
}

void GameEngine::FireArrow(float power) {
    const ItemDef* w = Equipped("main_hand");
    if (!w) return;
    const std::string& ammo = w->weapon.ammo_item;
    if (!ammo.empty() && !RemoveItem(ammo, 1)) { Toast("No arrows"); return; }
    if (player_.stamina < 2.0f) return;
    player_.stamina -= w->weapon.stamina_cost * 0.5f;
    stamina_delay_ = 0.6f;
    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    Vector3 dir = {sinf(player_.yaw) * cosf(player_.pitch), sinf(player_.pitch), cosf(player_.yaw) * cosf(player_.pitch)};
    Projectile p;
    p.pos = Vector3Add(eye, Vector3Scale(dir, 0.4f));
    p.vel = Vector3Scale(dir, w->weapon.projectile_speed * (0.45f + 0.55f * power));
    p.from_player = true;
    p.damage = static_cast<int>(std::round(ArrowHitDamage(w, power)));
    p.crit_chance = CritChance(w);
    p.crit_mult = CritMult(w);
    p.bane_family = w->weapon.bane_family;
    p.bane_mult = w->weapon.bane_mult;
    p.life_steal = w->weapon.life_steal + Bonus("life_steal");
    p.skill = w->weapon.skill;
    p.gravity = 6.0f;
    p.life = 5.0f;
    p.is_arrow = true;
    p.ammo_item = ammo;
    p.status = w->weapon.on_hit_status;
    p.status_chance = w->weapon.status_chance;
    p.status_power = w->weapon.status_power;
    p.status_duration = w->weapon.status_duration;
    if (const ItemDef* a = content_.GetItem(ammo)) p.model = a->world_model;
    scene_.projectiles.push_back(p);
    res_.PlaySfx("assets/audio/sfx/bow_release.wav", 0.7f, 0.95f + RandF() * 0.1f);
    making_noise_ = true;
}

void GameEngine::CastSelectedSpell() {
    if (player_.known_spells.empty()) { Toast("You know no spells"); return; }
    player_.selected_spell = std::clamp(player_.selected_spell, 0, static_cast<int>(player_.known_spells.size()) - 1);
    const SpellDef* sp = content_.GetSpell(player_.known_spells[player_.selected_spell]);
    if (!sp || spell_cooldown_ > 0.0f) return;
    float cost = SpellCost(*sp);
    if (player_.mana < cost) {
        Toast("Not enough mana", Color{140, 160, 255, 255});
        return;
    }
    player_.mana -= cost;
    spell_cooldown_ = sp->cooldown_seconds * (1.0f - std::min(0.5f, Bonus("spell_cooldown_reduction")));
    CastSpell(*sp, false);
}

void GameEngine::CastSpell(const SpellDef& spell, bool freeCast) {
    const SpellDef* s = &spell;
    (void)freeCast;
    cast_flash_ = 1.0f;
    cast_color_ = s->effect.light_color;
    cast_sprite_ = s->effect.projectile_sprite.empty() ? "assets/sprites/vfx/spell_arcane.png" : s->effect.projectile_sprite;
    res_.PlaySfx(s->cast_sfx, 0.75f);
    float power = s->effect.base_power * SpellPowerMult(*s);
    const std::string& prim = s->effect.primitive;

    auto addBuff = [&](float pw) {
        for (auto& b : player_.buffs) {
            if (b.primitive == prim) { b.remaining = b.duration = s->effect.duration_seconds; b.power = pw; return; }
        }
        ActiveBuff b;
        b.spell_id = s->id;
        b.primitive = prim;
        b.remaining = b.duration = s->effect.duration_seconds;
        b.power = pw;
        b.light_color = s->effect.light_color;
        b.light_radius = s->effect.light_radius;
        b.visibility = s->effect.visibility_multiplier;
        player_.buffs.push_back(b);
    };

    if (prim == "projectile_damage") {
        Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height - 0.15f, player_.pos.z};
        Vector3 dir = {sinf(player_.yaw) * cosf(player_.pitch), sinf(player_.pitch), cosf(player_.yaw) * cosf(player_.pitch)};
        Projectile p;
        p.pos = Vector3Add(eye, Vector3Scale(dir, 0.6f));
        p.vel = Vector3Scale(dir, s->effect.projectile_speed);
        p.from_player = true;
        p.damage = static_cast<int>(std::round(power));
        p.splash_radius = s->effect.splash_radius;
        p.drain = s->effect.drain_fraction;
        p.skill = s->skill;
        p.sprite = s->effect.projectile_sprite;
        p.status = s->effect.status;
        p.status_chance = s->effect.status_chance;
        p.status_power = s->effect.status_power * SpellPowerMult(*s);
        p.status_duration = s->effect.status_duration;
        p.light_color = s->effect.light_color;
        p.light_radius = s->effect.light_radius;
        p.life = 3.0f;
        scene_.projectiles.push_back(p);
        making_noise_ = true;
    } else if (prim == "chain") {
        // Lightning: the nearest foe in front (line of sight), then up to N more within 6 m of the last, 80% each jump.
        Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
        Vector3 fwd = Forward(player_.yaw);
        std::vector<CreatureInstance*> hitList;
        CreatureInstance* cur = nullptr;
        float best = 1e9f;
        for (auto& c : scene_.creatures) {
            if (c.state == CreatureState::Dead) continue;
            Vector3 to = Vector3Subtract(c.pos, player_.pos);
            to.y = 0;
            float d = Vector3Length(to);
            if (d > s->effect.chain_range || d < 0.01f) continue;
            if (Vector3DotProduct(Vector3Scale(to, 1.0f / d), fwd) < cosf(40.0f * DEG2RAD)) continue;
            if (!LineOfSight(eye, {c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z})) continue;
            if (d < best) { best = d; cur = &c; }
        }
        Vector3 from = Vector3Add(eye, Vector3Scale(fwd, 0.5f));
        float dmg = power;
        auto arc = [&](Vector3 a, Vector3 b) {
            Vector3 dv = Vector3Subtract(b, a);
            float len = Vector3Length(dv);
            for (float t = 0; t < len; t += 0.35f) {
                Vector3 p = Vector3Add(a, Vector3Scale(dv, t / len));
                p.x += (RandF() - 0.5f) * 0.25f; p.y += (RandF() - 0.5f) * 0.25f; p.z += (RandF() - 0.5f) * 0.25f;
                SpawnBurst(p, Color{255, 240, 150, 255}, 1, 0.4f, true, 0.0f, 0.06f);
            }
        };
        if (!cur) arc(from, Vector3Add(from, Vector3Scale(fwd, 4.0f)));
        int jumps = s->effect.chain_count + static_cast<int>(Bonus("chain_jump_bonus"));
        for (int jump = 0; cur && jump <= jumps; jump++) {
            Vector3 to = {cur->pos.x, cur->pos.y + cur->height * 0.6f, cur->pos.z};
            arc(from, to);
            hitList.push_back(cur);
            CreatureInstance& tgt = *cur;
            DamageCreature(tgt, static_cast<int>(std::round(dmg)), !tgt.alerted, s->skill, false);
            TryStatus(tgt, s->effect.status, s->effect.status_chance, s->effect.status_power * SpellPowerMult(*s), s->effect.status_duration);
            from = to;
            dmg *= 0.8f;
            CreatureInstance* next = nullptr;
            float nd = 6.0f;
            for (auto& c : scene_.creatures) {
                if (c.state == CreatureState::Dead || std::find(hitList.begin(), hitList.end(), &c) != hitList.end()) continue;
                float d = Vector3Distance(c.pos, tgt.pos);
                if (d < nd && LineOfSight(from, {c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z})) { nd = d; next = &c; }
            }
            cur = next;
        }
        making_noise_ = true;
        GainSkillXp(s->skill, hitList.empty() ? 0.5f : 1.5f);
    } else if (prim == "nova") {
        // A ring around the caster: damage and a status to every foe within the radius.
        float r = s->effect.radius * (1.0f + Bonus("nova_radius_bonus"));
        for (int i = 0; i < 36; i++) {
            float a = i * 2.0f * PI / 36.0f;
            SpawnBurst({player_.pos.x + sinf(a) * r * 0.9f, player_.pos.y + 0.5f, player_.pos.z + cosf(a) * r * 0.9f},
                       Color{static_cast<unsigned char>(cast_color_.x * 255), static_cast<unsigned char>(cast_color_.y * 255), static_cast<unsigned char>(cast_color_.z * 255), 255},
                       2, 1.2f, true, 0.0f, 0.07f);
        }
        int n = 0;
        for (auto& c : scene_.creatures) {
            if (c.state == CreatureState::Dead || Vector3Distance(c.pos, player_.pos) > r) continue;
            DamageCreature(c, static_cast<int>(std::round(power)), false, s->skill, s->effect.status == "shock");
            TryStatus(c, s->effect.status, s->effect.status_chance, s->effect.status_power * SpellPowerMult(*s), s->effect.status_duration);
            n++;
        }
        making_noise_ = true;
        GainSkillXp(s->skill, n > 0 ? 1.5f : 0.5f);
    } else if (prim == "blink") {
        // A short hop forward through open space (never through walls).
        Vector3 start = player_.pos;
        SpawnBurst({start.x, start.y + 1.0f, start.z}, Color{190, 160, 255, 255}, 24, 2.0f, true, 0.5f);
        Vector3 fwd = Forward(player_.yaw);
        player_.pos = MoveWithCollision(player_.pos, Vector3Scale(fwd, s->effect.blink_distance * (1.0f + Bonus("blink_distance_bonus"))), kPlayerRadius, 1.75f, true);
        player_.pos.y = GroundHeight({player_.pos.x, player_.pos.y + 0.5f, player_.pos.z}, kStepHeight);
        SpawnBurst({player_.pos.x, player_.pos.y + 1.0f, player_.pos.z}, Color{190, 160, 255, 255}, 24, 2.0f, true, 0.5f);
        GainSkillXp(s->skill, 1.5f);
    } else if (prim == "knock") {
        // Unauthorised Entry: the nearest locked door or chest you're looking at, within 6 m, simply... isn't.
        Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
        Vector3 fwd = Forward(player_.yaw);
        InteractableInstance* best = nullptr;
        float bd = 6.0f;
        for (auto& in : scene_.interactables) {
            if (!in.locked || in.def.mechanism_only) continue;
            Vector3 c = Vector3Scale(Vector3Add(in.world_box.min, in.world_box.max), 0.5f);
            Vector3 to = Vector3Subtract(c, player_.pos);
            to.y = 0;
            float d = Vector3Length(to);
            if (d > bd || (d > 0.8f && Vector3DotProduct(Vector3Scale(to, 1.0f / d), fwd) < 0.5f)) continue;
            bd = d;
            best = &in;
        }
        if (!best) Toast("Nothing locked in reach.", Color{200, 190, 255, 255});
        else if (best->def.lock_difficulty > power) Toast("This lock is above your clearance level.", Color{255, 180, 150, 255});
        else {
            best->locked = false;
            Persist().unlocked.insert(best->def.instance_id);
            Vector3 c = Vector3Scale(Vector3Add(best->world_box.min, best->world_box.max), 0.5f);
            SpawnBurst(c, Color{200, 170, 255, 255}, 30, 2.5f, true, 0.5f);
            res_.PlaySfx("assets/audio/sfx/door_open.wav", 0.6f, 1.5f);
            Toast("Unlocked. (Form 12-K filed retroactively.)", Color{200, 190, 255, 255});
            (void)eye;
        }
        GainSkillXp(s->skill, best ? 2.0f : 0.5f);
    } else if (prim == "buff_stat") {
        // A timed build bonus (lifesteal aura, haste...): stored like food buffs so Bonus() picks it up.
        ActiveBuff* slot = nullptr;
        for (auto& b : player_.buffs) if (b.spell_id == s->id) slot = &b;
        if (!slot) { player_.buffs.push_back({}); slot = &player_.buffs.back(); }
        slot->spell_id = s->id;
        slot->primitive = "buff_stat";
        slot->bonus_key = s->effect.bonus_key;
        slot->bonus_value = s->effect.bonus_value * (1.0f + SkillEffect(s->skill));
        slot->remaining = slot->duration = s->effect.duration_seconds;
        slot->light_color = s->effect.light_color;
        GainSkillXp(s->skill, 2.0f);
    } else if (prim == "self_heal") {
        player_.health += power * (1.0f + Bonus("heal_power_bonus"));
        player_.stamina += s->effect.stamina_restore;
        ClampVitals();
        cast_color_ = {0.5f, 1.0f, 0.6f};
        GainSkillXp(s->skill, 2.0f);
    } else if (prim == "buff_armor") {
        addBuff(power * (1.0f + Bonus("heal_power_bonus")));
        cast_color_ = {0.6f, 0.8f, 1.0f};
        GainSkillXp(s->skill, 2.0f);
    } else if (prim == "buff_light") {
        addBuff(power);
        GainSkillXp(s->skill, 1.0f);
    } else if (prim == "buff_stealth") {
        addBuff(power);
        cast_color_ = {0.6f, 0.5f, 0.9f};
        GainSkillXp(s->skill, 2.0f);
    }
    // Tag a cast as an attempt for the governing skill even if it is a projectile that later misses.
    if (prim == "projectile_damage") GainSkillXp(s->skill, 0.5f);
}

void GameEngine::UpdateBuffs(float dt) {
    for (auto& b : player_.buffs) b.remaining -= dt;
    size_t before = player_.buffs.size();
    for (const auto& b : player_.buffs) {
        if (b.remaining <= 0.0f) {
            if (const SpellDef* s = content_.GetSpell(b.spell_id)) Toast(content_.Tr(s->name_key) + " has faded", Color{170, 170, 190, 255});
        }
    }
    player_.buffs.erase(std::remove_if(player_.buffs.begin(), player_.buffs.end(), [](const ActiveBuff& b) { return b.remaining <= 0; }),
                        player_.buffs.end());
    if (before != player_.buffs.size()) ClampVitals();
}

// ============================================================================
// Companion: follows, fights alongside, looks after the player, and talks
// ============================================================================
void GameEngine::SpawnCreature(const MapCreatureSpawnDef& c) {
    const CreatureDef* def = content_.GetCreature(c.creature_id);
    if (!def) return;
    MapPersist& ps = Persist();
    CreatureInstance ci;
    ci.instance_id = c.instance_id;
    ci.spawn_def = &c;
    ci.def = def;
    ci.pos = ci.spawn = c.pos;
    ci.patrol_a = c.patrol_a;
    ci.patrol_b = c.patrol_b;
    ci.health = ci.max_health = def->health;
    ci.yaw = YawTo(c.patrol_a, c.patrol_b);
    float s = def->appearance.scale;
    ci.radius = Clamp(s * 0.24f, 0.28f, 0.55f);
    ci.height = def->appearance.type == "model_glb" ? 1.9f * s : s * 0.92f;
    ci.anim_time = RandF();
    ci.state = Vector3Distance(c.patrol_a, c.patrol_b) > 0.5f ? CreatureState::Patrol : CreatureState::Idle;
    if (ps.dead.count(c.instance_id)) {
        ci.state = CreatureState::Dead;
        ci.health = 0;
        auto cp = ps.corpse_pos.find(c.instance_id);
        if (cp != ps.corpse_pos.end()) ci.pos = cp->second;
    }
    scene_.creatures.push_back(ci);
}

void GameEngine::CheckGroupCleared(const CreatureInstance& dead) {
    const MapCreatureSpawnDef* d = dead.spawn_def;
    if (!d || d->group.empty()) return;
    for (const auto* p : pending_spawns_) if (p->group == d->group) return;
    for (const auto& c : scene_.creatures)
        if (c.spawn_def && c.spawn_def->group == d->group && c.state != CreatureState::Dead) return;
    // Any member may carry the trigger; use the first that does.
    for (const auto& c : scene_.creatures) {
        const MapCreatureSpawnDef* g = c.spawn_def;
        if (!g || g->group != d->group) continue;
        if (!g->group_set_flag.empty()) player_.flags.insert(g->group_set_flag);
        if (!g->group_quest_id.empty()) { SetQuestStage(g->group_quest_id, g->group_set_stage); break; }
    }
}

bool GameEngine::ObjectiveMarker(Vector3& out, std::string& questTitle) const {
    auto stageFor = [&](const std::string& qid) -> const QuestStageDef* {
        const QuestDef* q = content_.GetQuest(qid);
        auto it = player_.quest_stages.find(qid);
        if (!q || it == player_.quest_stages.end()) return nullptr;
        for (const auto& st : q->stages)
            if (st.stage == it->second) return st.completed || st.markers.empty() ? nullptr : &st;
        return nullptr;
    };
    std::string qid = player_.tracked_quest;
    const QuestStageDef* st = qid.empty() ? nullptr : stageFor(qid);
    if (!st) { qid = content_.game_cfg.starting_quest; st = stageFor(qid); }
    if (!st) return false;
    float best = 1e9f;
    bool found = false;
    auto consider = [&](Vector3 p) {
        float d = Vector3Distance(p, player_.pos);
        if (d < best) { best = d; out = p; found = true; }
    };
    for (const auto& id : st->markers) {
        for (const auto& n : scene_.npcs)
            if (n.instance_id == id && !n.hidden) consider(n.pos);
        for (const auto& in : scene_.interactables) {
            if (in.def.instance_id != id || in.used) continue;
            if (!in.def.set_flag.empty() && player_.flags.count(in.def.set_flag)) continue;  // already read / done
            consider(in.def.pos);
        }
        for (const auto& c : scene_.creatures)
            if (c.instance_id == id && c.state != CreatureState::Dead) consider(c.pos);
        for (const auto& p : scene_.pickups)
            if (p.key == id || p.key.find(":" + id) != std::string::npos) consider(p.pos);
    }
    if (found)
        if (const QuestDef* q = content_.GetQuest(qid)) questTitle = content_.Tr(q->title_key);
    return found;
}

void GameEngine::ChangeSanity(float delta) {
    float before = player_.sanity;
    player_.sanity = Clamp(player_.sanity + delta, 0.0f, 100.0f);
    if (delta < -4.0f) {
        damage_flash_ = std::max(damage_flash_, 0.25f);
        Toast("Sanity " + std::to_string(static_cast<int>(std::round(delta))), Color{190, 130, 255, 255});
    }
    if (before >= 60.0f && player_.sanity < 60.0f) whisper_cd_ = std::min(whisper_cd_, 3.0f);
}

void GameEngine::UpdateSanity(float dt) {
    const MapZoneDef* z = CurrentZone();
    float drain = z ? z->sanity_drain : 0.0f;
    sanity_drain_now_ = drain;
    if (drain > 0.0f) {
        // Company steadies the mind, even in the worst places.
        drain *= 1.0f - 0.25f * std::min<size_t>(player_.companions.size(), 2);
        player_.sanity = std::max(0.0f, player_.sanity - drain * dt);
    } else if (player_.sanity < 100.0f) {
        float regen = 0.25f + 0.35f * std::min<size_t>(player_.companions.size(), 2) + Bonus("sanity_regen");
        player_.sanity = std::min(100.0f, player_.sanity + regen * dt);
    }
    // Whispers below 60; more often the lower it goes.
    if (player_.sanity < 60.0f && screen_ == Screen::Playing && overlay_ == Overlay::None) {
        whisper_cd_ -= dt;
        if (whisper_cd_ <= 0.0f) {
            int n = 0;
            while (content_.Tr("whisper." + std::to_string(n + 1)) != "whisper." + std::to_string(n + 1)) n++;
            if (n > 0) QueueSay("...", content_.Tr("whisper." + std::to_string(1 + static_cast<int>(RandF() * n) % n)));
            whisper_cd_ = 12.0f + player_.sanity * 0.5f + RandF() * 10.0f;
        }
    }
    // Breaking point: you black out and wake somewhere safer, soaked and shaken.
    if (player_.sanity <= 0.0f && screen_ == Screen::Playing) {
        player_.sanity = 50.0f;
        say_queue_.clear();
        if (scene_.map) {
            auto it = scene_.map->spawns.find("saltmere_quay");
            if (it == scene_.map->spawns.end()) it = scene_.map->spawns.find(content_.game_cfg.starting_spawn);
            if (it != scene_.map->spawns.end()) {
                player_.pos = it->second.pos;
                player_.yaw = it->second.yaw_degrees * DEG2RAD;
                player_.vel = {0, 0, 0};
            }
        }
        StartNarration({"story.sanity.break"});
    }
}

int GameEngine::CompanionIndex() const {
    auto all = CompanionIndices();
    return all.empty() ? -1 : all.front();
}

std::vector<int> GameEngine::CompanionIndices() const {
    std::vector<int> out;
    for (const auto& id : player_.companions)
        for (size_t i = 0; i < scene_.npcs.size(); i++)
            if (scene_.npcs[i].def && scene_.npcs[i].def->id == id) { out.push_back(static_cast<int>(i)); break; }
    return out;
}

bool GameEngine::IsCompanion(const std::string& npcId) const {
    return std::find(player_.companions.begin(), player_.companions.end(), npcId) != player_.companions.end();
}

void GameEngine::QueueSay(const std::string& speaker, const std::string& text) {
    if (subtitle_time_ <= 0.0f && say_queue_.empty()) Say(speaker, text);
    else if (say_queue_.size() < 6) say_queue_.push_back({speaker, text});
}

void GameEngine::CompanionSay(const std::vector<std::string>& keys, float chance, int npcIndex) {
    int ci = npcIndex >= 0 ? npcIndex : CompanionIndex();
    if (ci < 0 || keys.empty() || RandF() > chance) return;
    QueueSay(content_.Tr(scene_.npcs[ci].def->name_key), content_.Tr(keys[static_cast<size_t>(RandF() * keys.size()) % keys.size()]));
}

void GameEngine::UpdateCompanion(float dt) {
    for (auto& n : scene_.npcs) n.companion = false;
    if (subtitle_time_ <= 0.0f && !say_queue_.empty()) {
        Say(say_queue_.front().first, say_queue_.front().second);
        say_queue_.erase(say_queue_.begin());
    }
    std::vector<int> party = CompanionIndices();
    if (party.empty()) return;
    companion_idle_cd_ -= dt;
    companion_calm_ += dt;
    bool zoneChanged = !zone_id_.empty() && zone_id_ != companion_last_zone_;
    bool fighting = false;
    Vector3 fwd = Forward(player_.yaw);
    Vector3 side = {fwd.z, 0.0f, -fwd.x};

    for (size_t slot = 0; slot < party.size(); slot++) {
        NpcInstance& n = scene_.npcs[party[slot]];
        const CompanionDef& cd = n.def->companion;
        n.companion = true;
        n.attack_cd = std::max(0.0f, n.attack_cd - dt);
        n.anim_hold = std::max(0.0f, n.anim_hold - dt);
        n.heal_cd = std::max(0.0f, n.heal_cd - dt);
        if (overlay_ == Overlay::Dialogue || overlay_ == Overlay::Shop) {
            n.yaw = YawTo(n.pos, player_.pos);
            if (n.anim_hold <= 0.0f) n.anim = "idle";
            continue;
        }
        float sideSign = slot == 0 ? 1.0f : -1.0f;  // first companion one side, second the other

        // Lost (other storey, far behind, behind a closed door): catch up out of sight, behind the player.
        float hd = HDist(n.pos, player_.pos);
        if (hd > 15.0f || fabsf(n.pos.y - player_.pos.y) > 2.2f) {
            Vector3 behind = Vector3Add(player_.pos, Vector3Add(Vector3Scale(fwd, -1.3f), Vector3Scale(side, 0.6f * sideSign)));
            float t;
            Vector3 nrm;
            Vector3 eye = {player_.pos.x, player_.pos.y + 1.0f, player_.pos.z};
            if (SegmentHitsWorld(eye, {behind.x, behind.y + 1.0f, behind.z}, t, nrm))
                behind = Vector3Add(player_.pos, Vector3Scale(side, 0.7f * sideSign));
            n.pos = behind;
            n.pos.y = GroundHeight({n.pos.x, player_.pos.y + 0.5f, n.pos.z}, kStepHeight);
            hd = HDist(n.pos, player_.pos);
            if (!companion_last_zone_.empty() && subtitle_time_ <= 0.0f) CompanionSay(cd.catchup_lines, 0.4f, party[slot]);
        }

        auto stepToward = [&](Vector3 target, float speed) {
            float ty = YawTo(n.pos, target);
            n.yaw = ty;
            Vector3 before = n.pos;
            n.pos = MoveWithCollision(n.pos, Vector3Scale(Forward(ty), speed * dt), 0.3f, 1.7f, false);
            n.pos.y = GroundHeight({n.pos.x, n.pos.y + 0.3f, n.pos.z}, kStepHeight);
            return HDist(before, n.pos) > speed * dt * 0.2f;
        };

        // Pick a fight: the nearest creature that has noticed us, near the player, in view.
        CreatureInstance* target = nullptr;
        float best = 1e9f;
        Vector3 eye = {n.pos.x, n.pos.y + 1.4f, n.pos.z};
        for (auto& c : scene_.creatures) {
            if (c.state == CreatureState::Dead || !c.alerted || c.charm_time > 0.0f) continue;
            float dp = HDist(c.pos, player_.pos);
            float dc = HDist(c.pos, n.pos);
            if (dp > 12.0f || fabsf(c.pos.y - n.pos.y) > 2.0f) continue;
            if (!LineOfSight(eye, {c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z})) continue;
            if (dc < best) { best = dc; target = &c; }
        }
        bool moved = false;
        if (target) {
            fighting = true;
            if (companion_calm_ > 8.0f) CompanionSay(cd.combat_lines, slot == 0 ? 0.6f : 0.35f, party[slot]);
            float reach = cd.reach + target->radius;
            if (best > reach) {
                moved = stepToward(target->pos, 4.4f);
            } else {
                n.yaw = YawTo(n.pos, target->pos);
                if (n.attack_cd <= 0.0f) {
                    int dmg = static_cast<int>(std::round(cd.damage * (1.0f + 0.12f * (player_.level - 1)) * (0.85f + RandF() * 0.3f) *
                                                          (1.0f + Bonus("companion_damage_bonus"))));
                    bool killed = target->health <= std::max(1, dmg - static_cast<int>(std::round(target->def->armor * 0.6f)));
                    DamageCreature(*target, dmg, false, "companion", false);
                    PlaySfxAt("assets/audio/sfx/sword_hit.wav", n.pos, 0.6f);
                    n.attack_cd = cd.attack_time;
                    n.anim = "attack";
                    n.anim_hold = 0.3f;
                    if (killed) CompanionSay(cd.kill_lines, 0.5f, party[slot]);
                }
            }
        } else {
            // Follow a little behind and to the side, so the companion stays in the corner of your eye.
            Vector3 spot = Vector3Add(player_.pos, Vector3Add(Vector3Scale(fwd, -1.5f - 0.3f * slot), Vector3Scale(side, 0.9f * sideSign)));
            float ds = HDist(n.pos, spot);
            if (hd > 2.4f || ds > 1.6f) moved = stepToward(spot, Clamp(ds * 1.7f, 2.2f, 7.5f));
            else n.yaw += WrapAngle(player_.yaw - n.yaw) * std::min(1.0f, dt * 2.0f);
        }
        if (n.anim_hold <= 0.0f) n.anim = moved ? "walk" : "idle";

        // Looking after you: food when you're badly hurt (one companion at a time).
        if (player_.health < MaxHealth() * 0.35f && player_.health > 0.0f && n.heal_cd <= 0.0f && companion_heal_cd_ <= 0.0f) {
            player_.health += cd.heal_amount;
            ClampVitals();
            n.heal_cd = cd.heal_cooldown;
            companion_heal_cd_ = 4.0f;
            res_.PlaySfx("assets/audio/sfx/spell_heal.wav", 0.5f, 1.2f);
            Toast("+" + std::to_string(cd.heal_amount) + " health", Color{150, 255, 170, 255});
            CompanionSay(cd.heal_lines, 1.0f, party[slot]);
        }

        // First time in each area: a remark from each companion, in turn.
        if (zoneChanged) {
            auto it = cd.zone_lines.find(zone_id_);
            std::string key = "companion_zone:" + n.def->id + ":" + zone_id_;
            if (it != cd.zone_lines.end() && !player_.claimed.count(key)) {
                player_.claimed.insert(key);
                QueueSay(content_.Tr(n.def->name_key), content_.Tr(it->second));
                companion_idle_cd_ = std::max(companion_idle_cd_, 30.0f);
            }
        }
    }
    companion_heal_cd_ = std::max(0.0f, companion_heal_cd_ - dt);
    if (fighting) companion_calm_ = 0.0f;
    if (zoneChanged) companion_last_zone_ = zone_id_;

    // Quiet moments: banter between two companions if there's any left, otherwise one of them chats.
    if (companion_idle_cd_ > 0.0f || companion_calm_ <= 15.0f || subtitle_time_ > 0.0f || !say_queue_.empty() || overlay_ != Overlay::None) return;
    companion_idle_cd_ = 75.0f + RandF() * 45.0f;
    auto flagsOk = [&](const std::string& f, const std::string& nf) {
        return (f.empty() || player_.flags.count(f)) && (nf.empty() || !player_.flags.count(nf));
    };
    if (party.size() >= 2 && RandF() < 0.6f) {
        for (int a : party) {
            for (int b : party) {
                if (a == b) continue;
                const NpcInstance& na = scene_.npcs[a];
                const NpcInstance& nb = scene_.npcs[b];
                for (const auto& bt : na.def->companion.banter) {
                    std::string key = "banter:" + na.def->id + ":" + bt.id;
                    if (bt.partner != nb.def->id || player_.claimed.count(key) || !flagsOk(bt.flag, bt.not_flag)) continue;
                    player_.claimed.insert(key);
                    for (const auto& [byPartner, k] : bt.lines)
                        QueueSay(content_.Tr((byPartner ? nb : na).def->name_key), content_.Tr(k));
                    return;
                }
            }
        }
    }
    const NpcInstance& talker = scene_.npcs[party[companion_idle_next_ % party.size()]];
    const CompanionDef& cd = talker.def->companion;
    if (cd.idle_lines.empty()) return;
    size_t start = static_cast<size_t>(RandF() * cd.idle_lines.size());
    for (size_t k = 0; k < cd.idle_lines.size(); k++) {
        const CompanionLineDef& l = cd.idle_lines[(start + k) % cd.idle_lines.size()];
        if (!flagsOk(l.flag, l.not_flag)) continue;
        QueueSay(content_.Tr(talker.def->name_key), content_.Tr(l.text_key));
        break;
    }
    companion_idle_next_++;
}

int GameEngine::SplashDamage(const Projectile& p, Vector3 at, const std::string& skipId) {
    int total = 0;
    SpawnBurst(at, Color{255, 150, 60, 255}, 40, 5.0f, true, 2.5f);
    for (auto& c : scene_.creatures) {
        if (c.state == CreatureState::Dead || c.instance_id == skipId) continue;
        float d = Vector3Distance({c.pos.x, c.pos.y + c.height * 0.5f, c.pos.z}, at);
        if (d > p.splash_radius) continue;
        float falloff = 1.0f - 0.5f * (d / p.splash_radius);
        total += DamageCreature(c, static_cast<int>(std::round(p.damage * 0.6f * falloff)), false, p.skill, false);
        if (!p.status.empty()) TryStatus(c, p.status, p.status_chance * 0.6f, p.status_power, p.status_duration);
    }
    return total;
}

// ---------------------------------------------------------------------------- status effects
// burn: damage over time. chill: slower; three stacks freeze solid. shock: +25% damage taken. ink: blinded.
// Combos: fire on a chilled/frozen foe SHATTERS (big hit); lightning on a burning foe OVERLOADS (explosion).
void GameEngine::StatusDamage(CreatureInstance& c, int amount, Color color) {
    if (c.state == CreatureState::Dead || amount <= 0) return;
    c.health -= amount;
    c.last_damaged_time = time_;
    SpawnBurst({c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z}, color, 4, 1.6f, true, 1.0f);
    if (c.health <= 0) KillCreature(c);
}

void GameEngine::TryStatus(CreatureInstance& c, const std::string& status, float chance, float power, float duration) {
    if (status.empty() || c.state == CreatureState::Dead) return;
    if (RandF() >= chance + Bonus("status_chance_bonus")) return;
    ApplyStatus(c, status, power, duration);
}

void GameEngine::ApplyStatus(CreatureInstance& c, const std::string& status, float power, float duration) {
    if (c.state == CreatureState::Dead) return;
    bool boss = c.def->behavior.find("boss") != std::string::npos;
    duration *= 1.0f + Bonus("status_duration_bonus");
    if (boss) duration *= 0.6f;  // bosses shake things off faster
    float combo = 1.0f + Bonus("combo_damage_bonus");
    Vector3 mid = {c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z};
    if (status == "burn") {
        if (c.chill_time > 0.0f || c.frozen_time > 0.0f) {
            int dmg = static_cast<int>(std::round((18.0f + power * 3.0f) * (c.frozen_time > 0.0f ? 1.6f : 1.0f) * combo));
            c.chill_time = c.frozen_time = 0.0f;
            c.chill_stacks = 0;
            SpawnBurst(mid, Color{200, 235, 255, 255}, 40, 5.0f, true, 3.0f, 0.07f);
            Toast("Shatter! (" + std::to_string(dmg) + ")", Color{170, 220, 255, 255});
            StatusDamage(c, dmg, Color{200, 235, 255, 255});
            return;
        }
        c.burn_time = std::max(c.burn_time, duration);
        c.burn_dps = std::max(c.burn_dps, power * (1.0f + Bonus("burn_damage_bonus")));
    } else if (status == "shock") {
        if (c.burn_time > 0.0f) {
            float dmg = (14.0f + c.burn_dps * 3.0f) * combo;
            c.burn_time = 0.0f;
            SpawnBurst(mid, Color{255, 230, 120, 255}, 50, 6.0f, true, 2.0f, 0.07f);
            Toast("Overload! (" + std::to_string(static_cast<int>(dmg)) + ")", Color{255, 230, 120, 255});
            res_.PlaySfx("assets/audio/sfx/boss_roar.wav", 0.35f, 1.6f);
            std::string id = c.instance_id;
            for (auto& o : scene_.creatures) {
                if (o.state == CreatureState::Dead) continue;
                float d = Vector3Distance(o.pos, c.pos);
                if (d > 3.5f) continue;
                StatusDamage(o, static_cast<int>(std::round(dmg * (o.instance_id == id ? 1.0f : 0.6f))), Color{255, 230, 120, 255});
            }
            return;
        }
        c.shock_time = std::max(c.shock_time, duration);
    } else if (status == "chill") {
        c.chill_time = std::max(c.chill_time, duration);
        int need = std::max(2, (boss ? 5 : 3) - static_cast<int>(Bonus("freeze_stacks_reduction")));
        if (++c.chill_stacks >= need && c.frozen_time <= 0.0f) {
            c.frozen_time = boss ? 1.0f : 2.2f;
            c.chill_stacks = 0;
            SpawnBurst(mid, Color{180, 220, 255, 255}, 30, 2.5f, true, 0.5f, 0.06f);
            Toast("Frozen solid!", Color{170, 220, 255, 255});
        }
    } else if (status == "bleed") {
        c.bleed_time = std::max(c.bleed_time, duration);
        c.bleed_stacks = std::min(3, c.bleed_stacks + 1);
        c.bleed_power = std::max(c.bleed_power, power);
        if (c.bleed_stacks == 3) Toast("Bleeding heavily!", Color{230, 90, 90, 255});
    } else if (status == "confuse") {
        if (boss) duration *= 0.5f;
        c.confuse_time = std::max(c.confuse_time, duration);
        c.wander_timer = 0.0f;
        SpawnBurst(mid, Color{220, 140, 255, 255}, 16, 1.5f, true, -0.5f, 0.05f);
    } else if (status == "charm") {
        if (boss) { Toast(content_.Tr(c.def->name_key) + " is not that easily won over.", Color{255, 180, 200, 255}); return; }
        c.charm_time = std::max(c.charm_time, duration);
        c.alerted = false;
        c.foe = -1;
        SpawnBurst(mid, Color{255, 150, 210, 255}, 22, 1.8f, true, -0.8f, 0.06f);
        Toast(content_.Tr(c.def->name_key) + " is your new best friend (for now)", Color{255, 170, 220, 255});
    } else if (status == "ink") {
        c.ink_time = std::max(c.ink_time, duration);
        SpawnBurst(mid, Color{30, 30, 40, 255}, 14, 2.0f, false, 2.0f, 0.06f);
    }
}

bool GameEngine::CanCraft(const RecipeDef& r) const {
    if (r.skill_level > 0 && SkillLevel(r.skill) < r.skill_level) return false;
    for (const auto& [it, q] : r.ingredients)
        if (CountItem(it) < q) return false;
    return true;
}

bool GameEngine::Craft(const std::string& recipeId) {
    for (const auto& r : content_.recipes) {
        if (r.id != recipeId) continue;
        if (!CanCraft(r)) return false;
        for (const auto& [it, q] : r.ingredients) RemoveItem(it, q);
        AddItem(r.result, r.qty, false);
        if (!r.skill.empty()) GainSkillXp(r.skill, 1.5f, true);
        res_.PlaySfx(r.station == "alchemy" ? "assets/audio/sfx/spell_heal.wav" : "assets/audio/sfx/sword_hit.wav", 0.5f, 1.2f);
        const ItemDef* d = content_.GetItem(r.result);
        Toast("Made " + (r.qty > 1 ? std::to_string(r.qty) + "x " : std::string()) + (d ? content_.Tr(d->name_key) : r.result), Color{180, 230, 150, 255});
        return true;
    }
    return false;
}

void GameEngine::StartFishing(int spotIndex) {
    if (CountItem("core:item.fishing_rod") == 0) { Toast("You need a fishing rod. Old Silas might have a spare."); return; }
    const InteractableInstance& in = scene_.interactables[spotIndex];
    fishing_ = true;
    fish_state_ = 0;
    fish_spot_ = spotIndex;
    fish_from_ = player_.pos;
    // The bobber lands a few metres out, in the direction you're facing.
    Vector3 f = Forward(player_.yaw);
    fish_bob_ = {player_.pos.x + f.x * 3.0f, in.def.pos.y + 0.02f, player_.pos.z + f.z * 3.0f};
    fish_timer_ = 2.5f + RandF() * 4.5f - std::min(1.5f, SkillLevel("perception") * 0.03f);
    res_.PlaySfx("assets/audio/sfx/bow_release.wav", 0.4f, 0.7f);
    SpawnBurst(fish_bob_, Color{200, 220, 230, 255}, 8, 1.2f, false, 4.0f);
}

void GameEngine::UpdateFishing(float dt) {
    if (HDist(player_.pos, fish_from_) > 0.6f || ActionPressed("attack")) {
        fishing_ = false;
        Toast("You reel in your line.");
        return;
    }
    fish_timer_ -= dt;
    if (fish_state_ == 0) {
        if (RandF() < dt * 1.5f) SpawnBurst(fish_bob_, Color{190, 210, 220, 255}, 1, 0.3f, false, 2.0f, 0.03f);
        if (fish_timer_ <= 0.0f) {
            fish_state_ = 1;
            fish_timer_ = 0.75f + std::min(0.5f, SkillLevel("perception") * 0.01f);
            SpawnBurst(fish_bob_, Color{230, 240, 255, 255}, 18, 2.4f, false, 5.0f);
            res_.PlaySfx("assets/audio/sfx/item_pickup.wav", 0.8f, 0.6f);
        }
    } else if (fish_timer_ <= 0.0f) {
        fishing_ = false;
        Toast("It got away!", Color{255, 190, 150, 255});
    }
}

void GameEngine::FishPress() {
    if (fish_state_ == 1) CatchFish();
    else Toast("Too soon! You scared it off.", Color{255, 190, 150, 255});
    fishing_ = false;
}

void GameEngine::CatchFish() {
    if (fish_spot_ < 0 || fish_spot_ >= static_cast<int>(scene_.interactables.size())) return;
    auto lt = content_.loot_tables.find(scene_.interactables[fish_spot_].def.loot_table);
    if (lt == content_.loot_tables.end() || lt->second.entries.empty()) return;
    int total = 0;
    for (const auto& e : lt->second.entries) total += e.weight;
    int roll = static_cast<int>(RandF() * total);
    for (const auto& e : lt->second.entries) {
        if ((roll -= e.weight) >= 0) continue;
        int q = e.min_qty + static_cast<int>(RandF() * (e.max_qty - e.min_qty + 1));
        AddItem(e.item_id, std::max(1, q), false);
        const ItemDef* d = content_.GetItem(e.item_id);
        Toast("Caught: " + (d ? content_.Tr(d->name_key) : e.item_id) + "!", Color{150, 220, 255, 255});
        break;
    }
    SpawnBurst(fish_bob_, Color{230, 240, 255, 255}, 24, 3.0f, false, 6.0f);
    res_.PlaySfx("assets/audio/sfx/coin_jingle.wav", 0.5f, 1.4f);
    GainSkillXp("perception", 1.5f, true);
}

void GameEngine::ApplyOilOnHit(CreatureInstance& c) {
    for (const auto& b : player_.buffs)
        if (b.primitive == "oil" && !b.status.empty()) TryStatus(c, b.status, b.status_chance, b.status_power, b.status_duration);
}

void GameEngine::UpdateCreatureStatus(CreatureInstance& c, float dt) {
    if (c.burn_time > 0.0f) {
        c.burn_time -= dt;
        c.burn_tick -= dt;
        if (RandF() < dt * 10.0f) {
            Particle pt;
            pt.pos = {c.pos.x + (RandF() - 0.5f) * c.radius * 1.4f, c.pos.y + RandF() * c.height, c.pos.z + (RandF() - 0.5f) * c.radius * 1.4f};
            pt.vel = {0.0f, 0.8f + RandF() * 0.8f, 0.0f};
            pt.color = RandF() < 0.5f ? Color{255, 150, 40, 255} : Color{255, 210, 90, 255};
            pt.life = pt.max_life = 0.5f + RandF() * 0.4f;
            pt.glow = true;
            pt.size = 0.05f;
            pt.gravity = -0.5f;
            scene_.particles.push_back(pt);
        }
        if (c.burn_tick <= 0.0f) {
            c.burn_tick = 0.5f;
            StatusDamage(c, std::max(1, static_cast<int>(std::round(c.burn_dps * 0.5f))), Color{255, 140, 50, 255});
        }
        if (c.burn_time <= 0.0f) c.burn_dps = 0.0f;
    }
    if (c.chill_time > 0.0f && (c.chill_time -= dt) <= 0.0f) c.chill_stacks = 0;
    if (c.frozen_time > 0.0f) c.frozen_time -= dt;
    if (c.shock_time > 0.0f) {
        c.shock_time -= dt;
        if (RandF() < dt * 6.0f) SpawnBurst({c.pos.x, c.pos.y + c.height * (0.3f + RandF() * 0.6f), c.pos.z}, Color{255, 240, 150, 255}, 2, 2.5f, true, 0.0f, 0.04f);
    }
    if (c.ink_time > 0.0f) c.ink_time -= dt;
    if (c.bleed_time > 0.0f) {
        c.bleed_time -= dt;
        c.bleed_tick -= dt;
        if (c.bleed_tick <= 0.0f) {
            c.bleed_tick = 0.5f;
            StatusDamage(c, std::max(1, static_cast<int>(std::round(c.bleed_power * c.bleed_stacks * 0.5f))), Color{170, 20, 30, 255});
        }
        if (c.bleed_time <= 0.0f) { c.bleed_stacks = 0; c.bleed_power = 0.0f; }
    }
    if (c.bleed_time > 0.0f && RandF() < dt * 5.0f) {
        Particle pt;
        pt.pos = {c.pos.x + (RandF() - 0.5f) * c.radius, c.pos.y + c.height * (0.3f + RandF() * 0.4f), c.pos.z + (RandF() - 0.5f) * c.radius};
        pt.vel = {0.0f, -0.5f, 0.0f};
        pt.color = Color{150, 10, 20, 255};
        pt.life = pt.max_life = 0.6f;
        pt.size = 0.04f;
        pt.gravity = 6.0f;
        scene_.particles.push_back(pt);
    }
    if (c.confuse_time > 0.0f) {
        c.confuse_time -= dt;
        if (RandF() < dt * 3.0f) SpawnBurst({c.pos.x, c.pos.y + c.height + 0.15f, c.pos.z}, Color{230, 200, 255, 255}, 1, 0.8f, true, 0.0f, 0.05f);
    }
    if (c.charm_time > 0.0f && RandF() < dt * 2.5f)
        SpawnBurst({c.pos.x, c.pos.y + c.height + 0.15f, c.pos.z}, Color{255, 130, 200, 255}, 1, 0.6f, true, -0.4f, 0.06f);
    if (c.charm_time > 0.0f && (c.charm_time -= dt) <= 0.0f) {
        c.alerted = true;  // the spell wears off; it remembers who did it
        c.last_known = player_.pos;
        c.state = CreatureState::Chase;
    }
}

void GameEngine::CreatureHitCreature(CreatureInstance& a, CreatureInstance& v) {
    if (v.state == CreatureState::Dead) return;
    int dmg = std::max(1, a.def->attack.damage * 2 - static_cast<int>(std::round(v.def->armor * 0.6f)));
    v.health -= dmg;
    v.hit_flash = 0.15f;
    v.last_damaged_time = time_;
    SpawnBurst({v.pos.x, v.pos.y + v.height * 0.6f, v.pos.z}, v.def->hit_color, 8, 2.4f, v.def->hit_glow);
    PlaySfxAt(v.def->sfx_hit.empty() ? "assets/audio/sfx/sword_hit.wav" : v.def->sfx_hit, v.pos, 0.7f);
    // Whoever gets hit hits back.
    for (size_t i = 0; i < scene_.creatures.size(); i++)
        if (&scene_.creatures[i] == &a) v.foe = static_cast<int>(i);
    if (v.health <= 0) KillCreature(v);
}

int GameEngine::DamageCreature(CreatureInstance& c, int amount, bool sneak, const std::string& skill, bool heavy, bool crit) {
    if (c.state == CreatureState::Dead) return 0;
    if (c.charm_time > 0.0f) c.charm_time = 0.01f;  // betrayal ends friendships
    if (c.shock_time > 0.0f) amount = static_cast<int>(std::round(amount * (1.25f + Bonus("shock_damage_bonus"))));
    if (c.health >= c.max_health) amount = static_cast<int>(std::round(amount * (1.0f + Bonus("opener_damage_bonus"))));
    if (player_.health < MaxHealth() * 0.35f) amount = static_cast<int>(std::round(amount * (1.0f + Bonus("desperation_damage_bonus"))));
    // Armour blunts each blow; 60% weighting keeps fast light weapons viable against armoured foes.
    int final = std::max(1, amount - static_cast<int>(std::round(c.def->armor * 0.6f)));
    c.health -= final;
    c.hit_flash = 0.15f;
    c.last_damaged_time = time_;
    SpawnBurst({c.pos.x, c.pos.y + c.height * 0.6f, c.pos.z}, c.def->hit_color, 8 + std::min(16, final / 2), 2.6f, c.def->hit_glow);
    target_enemy_ = c.instance_id;
    target_enemy_time_ = 4.0f;
    PlaySfxAt(c.def->sfx_hit.empty() ? "assets/audio/sfx/sword_hit.wav" : c.def->sfx_hit, c.pos, 0.8f);
    if (sneak) {
        Toast(std::string(crit ? "Critical sneak attack! (" : "Sneak attack! (") + std::to_string(final) + ")", Color{200, 170, 255, 255});
        GainSkillXp("stealth", 2.0f, true);
    } else if (crit) {
        Toast("Critical hit! (" + std::to_string(final) + ")", Color{255, 214, 120, 255});
    }
    if (crit) SpawnBurst({c.pos.x, c.pos.y + c.height * 0.7f, c.pos.z}, Color{255, 220, 120, 255}, 18, 3.4f, true, 1.5f);
    if (c.health <= 0) {
        int overkill = c.health;
        KillCreature(c);
        return final + overkill;  // damage actually absorbed (no life steal from overkill)
    }
    bool wasUnaware = !c.alerted;
    c.alerted = true;
    c.last_known = player_.pos;
    bool boss = c.def->behavior.find("boss") != std::string::npos;
    bool guardian = c.def->behavior.find("guardian") != std::string::npos;
    bool poiseBroken = heavy || (!guardian && final * 100 >= c.max_health * 35);
    bool poiseReady = player_.play_time - c.last_stagger_time > 2.0;
    if (poiseBroken && poiseReady && !boss && c.state != CreatureState::Stagger) {
        c.state = CreatureState::Stagger;
        c.state_timer = heavy ? 0.7f : 0.45f;
        c.anim_time = 0.0f;
        c.last_stagger_time = player_.play_time;
    } else if (wasUnaware || c.state == CreatureState::Idle || c.state == CreatureState::Patrol || c.state == CreatureState::Search ||
               c.state == CreatureState::Return || c.state == CreatureState::Notice) {
        c.state = CreatureState::Chase;
        if (wasUnaware) PlaySfxAt(c.def->sfx_alert, c.pos, 0.8f);
        if (wasUnaware && !c.def->alert_line_key.empty() && spoke_alert_.insert(c.instance_id).second)
            Say(content_.Tr(c.def->name_key), content_.Tr(c.def->alert_line_key));
    }
    (void)skill;
    return final;
}

void GameEngine::KillCreature(CreatureInstance& c) {
    c.state = CreatureState::Dead;
    c.health = 0;
    c.anim_time = 0.0f;
    c.moving = false;
    MapPersist& ps = Persist();
    ps.dead.insert(c.instance_id);
    ps.corpse_pos[c.instance_id] = c.pos;
    Container("corpse:" + c.instance_id, c.def->loot_table, {});
    PlaySfxAt(c.def->sfx_death.empty() ? "assets/audio/sfx/enemy_death.wav" : c.def->sfx_death, c.pos, 0.9f);
    if (!c.def->death_line_key.empty()) Say(content_.Tr(c.def->name_key), content_.Tr(c.def->death_line_key));
    Toast("Defeated " + content_.Tr(c.def->name_key) + "  (+" + std::to_string(c.def->xp_reward) + " XP)", Color{230, 200, 160, 255});
    GainXp(c.def->xp_reward);
    if (float h = Bonus("heal_on_kill"); h > 0.0f) player_.health += h;
    if (float m = Bonus("mana_on_kill"); m > 0.0f) player_.mana += m;
    ClampVitals();
    if (c.burn_time > 0.0f && Bonus("burn_spread_on_death") > 0.0f) {
        // Pyre perk: the flames jump to whoever's standing too close.
        float dps = c.burn_dps, dur = std::max(2.0f, c.burn_time);
        c.burn_time = 0.0f;
        for (auto& o : scene_.creatures)
            if (o.state != CreatureState::Dead && &o != &c && Vector3Distance(o.pos, c.pos) < 3.5f) ApplyStatus(o, "burn", dps, dur);
    }
    CheckGroupCleared(c);
    if (c.def->behavior == "boss_archivist") {
        Toast("The Archivist Shade dissolves into loose pages. Search its remains.", Color{180, 220, 255, 255});
    }
}

void GameEngine::DamagePlayer(int raw, Vector3 from, CreatureInstance* attacker) {
    float dmg = raw * DifficultyEnemyMult();
    Vector3 to = Vector3Subtract(from, player_.pos);
    to.y = 0;
    bool front = Vector3Length(to) < 0.01f ||
                 acosf(Clamp(Vector3DotProduct(Vector3Normalize(to), Forward(player_.yaw)), -1.0f, 1.0f)) < 75.0f * DEG2RAD;
    if (blocking_ && front) {
        const BalancingDef& b = content_.balancing;
        bool shield = Equipped("off_hand") != nullptr;
        if (player_.play_time - block_start_ <= b.parry_window_seconds && attacker) {
            player_.stamina += b.parry_stamina_bonus;
            attacker->state = CreatureState::Stagger;
            attacker->state_timer = 0.9f;
            attacker->anim_time = 0.0f;
            res_.PlaySfx("assets/audio/sfx/shield_block.wav", 1.0f, 1.25f);
            SpawnBurst(Vector3Add(player_.pos, Vector3Add({0, 1.3f, 0}, Vector3Scale(Forward(player_.yaw), 0.7f))), Color{255, 220, 120, 255}, 14, 3.5f, true);
            Toast("Parry!", Color{255, 230, 140, 255});
            GainSkillXp("block", 2.5f, true);
            ClampVitals();
            return;
        }
        float red = b.block_damage_reduction * (shield ? 1.0f : 0.6f) * (1.0f + SkillEffect("block") * 0.5f);
        red = std::min(red + Bonus("block_reduction_bonus"), 0.92f);
        dmg *= (1.0f - red);
        player_.stamina -= raw * 0.6f * (1.0f - std::min(0.7f, Bonus("block_stamina_reduction")));
        stamina_delay_ = 0.8f;
        res_.PlaySfx("assets/audio/sfx/shield_block.wav", 0.9f, 0.95f + RandF() * 0.1f);
        player_.health += Bonus("heal_on_block");
        GainSkillXp("block", 1.2f);
        if (player_.stamina <= 0.0f) {
            blocking_ = false;
            Toast("Guard broken!", Color{255, 140, 120, 255});
        }
    }
    float armor = static_cast<float>(ArmorRating());
    dmg *= 40.0f / (40.0f + armor);
    int final = std::max(1, static_cast<int>(std::round(dmg)));
    player_.health -= final;
    damage_flash_ = std::min(1.0f, 0.35f + final / 30.0f);
    res_.PlaySfx("assets/audio/sfx/player_hurt.wav", 0.8f, 0.9f + RandF() * 0.2f);
    ClampVitals();
}

void GameEngine::SpawnEnemyProjectile(CreatureInstance& c) {
    Projectile p;
    Vector3 start = {c.pos.x, c.pos.y + c.height * 0.65f, c.pos.z};
    Vector3 target = {player_.pos.x, player_.pos.y + 1.1f, player_.pos.z};
    Vector3 dir = Vector3Normalize(Vector3Subtract(target, start));
    p.pos = Vector3Add(start, Vector3Scale(dir, c.radius + 0.3f));
    p.vel = Vector3Scale(dir, c.def->attack.projectile_speed);
    p.from_player = false;
    p.damage = c.def->attack.damage;
    p.sanity = c.def->attack.sanity_damage;
    p.sprite = c.def->attack.projectile_sprite.empty() ? "assets/sprites/vfx/spell_arcane.png" : c.def->attack.projectile_sprite;
    p.light_color = {0.45f, 0.75f, 1.0f};
    p.light_radius = 5.0f;
    p.life = 4.0f;
    scene_.projectiles.push_back(p);
}

void GameEngine::UpdateCreatures(float dt) {
    Vector3 playerEye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    float vis = Visibility();
    float noise = making_noise_ ? 1.0f : (player_.crouching ? 0.0f : 0.25f);

    for (size_t idx = 0; idx < scene_.creatures.size(); idx++) {
        CreatureInstance& c = scene_.creatures[idx];
        c.anim_time += dt;
        c.hit_flash = std::max(0.0f, c.hit_flash - dt);
        if (c.state == CreatureState::Dead) continue;
        UpdateCreatureStatus(c, dt);
        if (c.state == CreatureState::Dead) continue;
        const CreatureDef& d = *c.def;
        c.moving = false;
        if (c.frozen_time > 0.0f) continue;  // frozen solid: no thinking, no moving, no attacking
        float slow = c.chill_time > 0.0f ? 0.55f : 1.0f;
        c.attack_cooldown -= dt * (c.chill_time > 0.0f ? 0.65f : 1.0f);

        // Charmed, confused or brawling: fight other creatures instead of the player.
        {
            CreatureInstance* other = nullptr;
            bool charmed = c.charm_time > 0.0f, confused = c.confuse_time > 0.0f;
            auto nearest = [&](bool skipCharmed) -> CreatureInstance* {
                CreatureInstance* best = nullptr;
                float bd = 14.0f;
                for (size_t j = 0; j < scene_.creatures.size(); j++) {
                    CreatureInstance& o = scene_.creatures[j];
                    if (j == idx || o.state == CreatureState::Dead || (skipCharmed && o.charm_time > 0.0f)) continue;
                    float dd = HDist(o.pos, c.pos);
                    if (dd < bd && fabsf(o.pos.y - c.pos.y) < 2.5f) { bd = dd; best = &o; }
                }
                return best;
            };
            if (charmed) other = nearest(true);
            else if (confused) {
                CreatureInstance* n = nearest(false);
                if (n && HDist(n->pos, c.pos) < d.attack.reach_meters * 1.3f + n->radius) other = n;
            } else if (c.foe >= 0 && c.foe < static_cast<int>(scene_.creatures.size()) && static_cast<size_t>(c.foe) != idx) {
                CreatureInstance& f = scene_.creatures[c.foe];
                if (f.state != CreatureState::Dead && (f.charm_time > 0.0f || f.confuse_time > 0.0f) && HDist(f.pos, c.pos) < 15.0f) other = &f;
                else c.foe = -1;
            }
            if (other || charmed || confused) {
                float spd = d.move_speed * slow;
                auto step = [&](Vector3 target, float stop) {
                    float hd = HDist(c.pos, target);
                    if (hd <= stop) return;
                    float ty = YawTo(c.pos, target);
                    c.yaw = ty;
                    Vector3 before = c.pos;
                    c.pos = MoveWithCollision(c.pos, Vector3Scale(Forward(ty), spd * dt), c.radius, c.height, false, static_cast<int>(idx));
                    c.pos.y = GroundHeight({c.pos.x, c.pos.y + 0.3f, c.pos.z}, kStepHeight);
                    c.moving = HDist(before, c.pos) > spd * dt * 0.2f;
                };
                if (other) {
                    float reach = d.attack.reach_meters + other->radius;
                    if (HDist(c.pos, other->pos) > reach * 0.9f) step(other->pos, reach * 0.8f);
                    else if (c.attack_cooldown <= 0.0f) {
                        c.yaw = YawTo(c.pos, other->pos);
                        c.state = CreatureState::Recover;
                        c.state_timer = 0.4f;
                        c.anim_time = 0.0f;
                        c.attack_cooldown = d.attack.cooldown_seconds;
                        PlaySfxAt(d.sfx_attack, c.pos, 0.6f);
                        CreatureHitCreature(c, *other);
                    }
                } else if (charmed) {
                    if (HDist(c.pos, player_.pos) > 3.0f) step(player_.pos, 2.5f);  // nobody to fight: tag along
                } else {
                    c.wander_timer -= dt;
                    if (c.wander_timer <= 0.0f) {
                        float a = RandF() * 2.0f * PI;
                        c.wander_to = {c.pos.x + sinf(a) * 3.0f, c.pos.y, c.pos.z + cosf(a) * 3.0f};
                        c.wander_timer = 1.2f + RandF();
                    }
                    step(c.wander_to, 0.3f);
                }
                if (c.state == CreatureState::Recover && (c.state_timer -= dt) <= 0.0f) c.state = CreatureState::Idle;
                continue;
            }
        }

        Vector3 eye = {c.pos.x, c.pos.y + c.height * 0.85f, c.pos.z};
        float dist = Vector3Distance(c.pos, player_.pos);
        float yawToPlayer = YawTo(c.pos, player_.pos);
        float facingDiff = fabsf(WrapAngle(yawToPlayer - c.yaw));
        float sight = d.sight_meters * vis;
        bool inCone = c.alerted ? true : facingDiff < 70.0f * DEG2RAD;
        if (c.ink_time > 0.0f) sight = std::min(sight, 2.5f);  // inked: can barely see past its own nose
        bool canSee = dist < sight && inCone && LineOfSight(eye, playerEye);
        bool heard = dist < d.hearing_meters * noise && LineOfSight(eye, playerEye);
        if (!canSee && dist < 1.6f) canSee = true; // bumping into someone is hard to miss
        bool boss = d.behavior.find("boss") != std::string::npos;
        bool guardian = d.behavior.find("guardian") != std::string::npos;
        float speed = d.move_speed * (boss && c.health < c.max_health / 2 ? 1.3f : 1.0f) * slow;

        auto turnTo = [&](float targetYaw, float rate) {
            float diff = WrapAngle(targetYaw - c.yaw);
            float stepA = rate * dt;
            c.yaw = WrapAngle(c.yaw + Clamp(diff, -stepA, stepA));
        };
        auto moveTo = [&](Vector3 target, float spd, float stopDist) -> bool {
            float hd = HDist(c.pos, target);
            if (hd <= stopDist) return true;
            float ty = YawTo(c.pos, target);
            turnTo(ty, 7.0f);
            Vector3 dir = Forward(ty);
            Vector3 before = c.pos;
            c.pos = MoveWithCollision(c.pos, Vector3Scale(dir, spd * dt), c.radius, c.height, false, static_cast<int>(idx));
            c.pos.y = GroundHeight({c.pos.x, c.pos.y + 0.3f, c.pos.z}, kStepHeight);
            c.moving = HDist(before, c.pos) > spd * dt * 0.2f;
            return false;
        };
        auto beginNotice = [&]() {
            c.state = CreatureState::Notice;
            c.state_timer = boss ? 0.8f : 0.45f;
            c.alerted = true;
            c.last_known = player_.pos;
            PlaySfxAt(d.sfx_alert, c.pos, 0.9f);
            if (!d.alert_line_key.empty() && spoke_alert_.insert(c.instance_id).second) Say(content_.Tr(d.name_key), content_.Tr(d.alert_line_key));
        };

        switch (c.state) {
            case CreatureState::Idle:
            case CreatureState::Patrol: {
                if (canSee || heard) { beginNotice(); break; }
                if (c.state == CreatureState::Idle) {
                    c.state_timer -= dt;
                    if (c.state_timer <= 0 && Vector3Distance(c.patrol_a, c.patrol_b) > 0.5f) c.state = CreatureState::Patrol;
                    break;
                }
                Vector3 target = c.patrol_to_b ? c.patrol_b : c.patrol_a;
                if (moveTo(target, speed * 0.45f, 0.3f)) {
                    c.patrol_to_b = !c.patrol_to_b;
                    c.state = CreatureState::Idle;
                    c.state_timer = 1.2f + RandF() * 1.5f;
                }
                break;
            }
            case CreatureState::Notice:
                turnTo(yawToPlayer, 8.0f);
                c.state_timer -= dt;
                if (c.state_timer <= 0) c.state = CreatureState::Chase;
                break;
            case CreatureState::Chase: {
                if (canSee) { c.last_known = player_.pos; c.state_timer = 0.0f; }
                else c.state_timer += dt;
                if (guardian && HDist(c.pos, c.spawn) > 14.0f) { c.state = CreatureState::Return; c.alerted = false; break; }
                if (c.state_timer > 4.0f) { c.state = CreatureState::Search; c.state_timer = 6.0f; break; }
                bool rangedReady = d.attack.ranged_range_meters > 0 && canSee && dist > d.attack.reach_meters + 1.5f &&
                                   dist < d.attack.ranged_range_meters && c.attack_cooldown <= 0;
                if (rangedReady) {
                    c.state = CreatureState::Windup;
                    c.ranged_attack = true;
                    c.state_timer = d.attack.windup_seconds;
                    c.anim_time = 0;
                    break;
                }
                if (canSee && dist < d.attack.reach_meters * 0.85f + kPlayerRadius) {
                    turnTo(yawToPlayer, 9.0f);
                    if (c.attack_cooldown <= 0) {
                        c.state = CreatureState::Windup;
                        c.ranged_attack = false;
                        c.state_timer = d.attack.windup_seconds;
                        c.anim_time = 0;
                    }
                    break;
                }
                moveTo(c.last_known, speed, d.attack.reach_meters * 0.6f);
                break;
            }
            case CreatureState::Windup:
                turnTo(yawToPlayer, c.ranged_attack ? 6.0f : 3.5f);
                c.state_timer -= dt * slow;
                if (c.state_timer <= 0) {
                    if (c.ranged_attack) {
                        SpawnEnemyProjectile(c);
                        PlaySfxAt(d.sfx_attack, c.pos, 0.9f);
                    } else {
                        PlaySfxAt(d.sfx_attack, c.pos, 0.7f);
                        float facing = fabsf(WrapAngle(yawToPlayer - c.yaw));
                        bool inkMiss = c.ink_time > 0.0f && RandF() < 0.45f;
                        if (dist <= d.attack.reach_meters + kPlayerRadius + 0.25f && facing < 60.0f * DEG2RAD && LineOfSight(eye, playerEye) && !inkMiss) {
                            DamagePlayer(d.attack.damage, c.pos, &c);
                            if (d.attack.sanity_damage > 0) ChangeSanity(-static_cast<float>(d.attack.sanity_damage));
                        }
                    }
                    float cd = d.attack.cooldown_seconds * (boss && c.health < c.max_health / 2 ? 0.7f : 1.0f);
                    if (c.ranged_attack) cd *= 1.7f; // bolts are the opener, not a machine gun
                    c.attack_cooldown = cd;
                    c.state = CreatureState::Recover;
                    c.state_timer = std::min(cd, 0.6f);
                    c.anim_time = 0;
                }
                break;
            case CreatureState::Recover:
                c.state_timer -= dt;
                if (c.state_timer <= 0) c.state = CreatureState::Chase;
                break;
            case CreatureState::Stagger:
                c.state_timer -= dt;
                if (c.state_timer <= 0) { c.state = CreatureState::Chase; c.attack_cooldown = std::max(c.attack_cooldown, 0.3f); }
                break;
            case CreatureState::Search:
                if (canSee) { c.state = CreatureState::Chase; c.state_timer = 0; break; }
                c.state_timer -= dt;
                if (moveTo(c.last_known, speed * 0.6f, 0.5f) || c.state_timer <= 0) {
                    turnTo(c.yaw + 1.5f, 1.5f);
                    if (c.state_timer <= 0) { c.state = CreatureState::Return; c.alerted = false; }
                }
                break;
            case CreatureState::Return:
                if (canSee || heard) { beginNotice(); break; }
                if (moveTo(c.patrol_a, speed * 0.5f, 0.4f)) { c.state = CreatureState::Patrol; c.patrol_to_b = true; }
                if (c.health < c.max_health) c.health = std::min(c.max_health, c.health + static_cast<int>(std::ceil(dt * 4)));
                break;
            case CreatureState::Dead:
                break;
        }
    }
}

void GameEngine::UpdateProjectiles(float dt) {
    for (auto& p : scene_.projectiles) {
        if (!p.alive) continue;
        p.age += dt;
        if (p.age > p.life) { p.alive = false; continue; }
        p.vel.y -= p.gravity * dt;
        Vector3 next = Vector3Add(p.pos, Vector3Scale(p.vel, dt));

        // Actor hits first (closest along the segment).
        Vector3 seg = Vector3Subtract(next, p.pos);
        float segLen2 = std::max(1e-6f, Vector3LengthSqr(seg));
        auto closestT = [&](Vector3 c) { return Clamp(Vector3DotProduct(Vector3Subtract(c, p.pos), seg) / segLen2, 0.0f, 1.0f); };

        float tWorld = 2.0f;
        Vector3 nrm{};
        bool worldHit = SegmentHitsWorld(p.pos, next, tWorld, nrm);

        if (p.from_player) {
            CreatureInstance* hit = nullptr;
            float hitT = 2.0f;
            for (auto& c : scene_.creatures) {
                if (c.state == CreatureState::Dead) continue;
                Vector3 center = {c.pos.x, c.pos.y + c.height * 0.5f, c.pos.z};
                float t = closestT(center);
                Vector3 q = Vector3Add(p.pos, Vector3Scale(seg, t));
                float hd = HDist(q, center);
                if (hd < c.radius + 0.15f && q.y > c.pos.y - 0.1f && q.y < c.pos.y + c.height + 0.1f && t < hitT) { hit = &c; hitT = t; }
            }
            if (hit && (!worldHit || hitT <= tWorld)) {
                bool sneak = !hit->alerted;
                float dmg = static_cast<float>(p.damage);
                if (sneak) dmg *= (p.is_arrow ? 1.6f * std::max(1.0f, Bonus("ranged_crit_multiplier")) : 1.4f) + Bonus("sneak_damage_bonus");
                bool crit = p.crit_chance > 0.0f && RandF() < p.crit_chance;
                if (crit) dmg *= p.crit_mult;
                if (!p.bane_family.empty() && p.bane_family == hit->def->family) dmg *= p.bane_mult;
                if (!p.is_arrow) SpawnBurst(p.pos, Color{static_cast<unsigned char>(Clamp(p.light_color.x * 255, 0.0f, 255.0f)), static_cast<unsigned char>(Clamp(p.light_color.y * 255, 0.0f, 255.0f)),
                      static_cast<unsigned char>(Clamp(p.light_color.z * 255, 0.0f, 255.0f)), 255}, 16, 3.0f, true, 2.0f);
                Vector3 impact = {hit->pos.x, hit->pos.y + hit->height * 0.5f, hit->pos.z};
                std::string hitId = hit->instance_id;
                CreatureInstance* hitPtr = hit;
                int dealt = DamageCreature(*hit, static_cast<int>(std::round(dmg)), sneak, p.skill, false, crit);
                if (!p.status.empty()) TryStatus(*hitPtr, p.status, p.status_chance, p.status_power, p.status_duration);
                if (p.is_arrow) ApplyOilOnHit(*hitPtr);
                if (p.splash_radius > 0.0f) dealt += SplashDamage(p, impact, hitId);
                float heal = dealt * (p.drain + p.life_steal);
                if (heal > 0.0f) { player_.health += heal; ClampVitals(); }
                GainSkillXp(p.skill, p.is_arrow ? 1.4f : 1.2f);
                // Arrows that strike flesh sometimes survive to be looted from the corpse.
                if (p.is_arrow && !p.ammo_item.empty() && RandF() < 0.4f) {
                    std::string key = "corpse:" + hit->instance_id;
                    if (hit->state == CreatureState::Dead) Persist().containers[key].items.push_back({p.ammo_item, 1});
                }
                p.alive = false;
                continue;
            }
        } else {
            Vector3 center = {player_.pos.x, player_.pos.y + 1.0f, player_.pos.z};
            float t = closestT(center);
            Vector3 q = Vector3Add(p.pos, Vector3Scale(seg, t));
            if (Vector3Distance(q, center) < 0.65f && (!worldHit || t <= tWorld)) {
                DamagePlayer(p.damage, p.pos, nullptr);
                if (p.sanity > 0) ChangeSanity(-static_cast<float>(p.sanity));
                p.alive = false;
                continue;
            }
        }

        if (worldHit) {
            Vector3 hitPos = Vector3Add(p.pos, Vector3Scale(seg, tWorld));
            if (p.from_player && p.splash_radius > 0.0f) {
                int dealt = SplashDamage(p, hitPos, "");
                if (dealt > 0 && p.drain > 0.0f) { player_.health += dealt * p.drain; ClampVitals(); }
            }
            if (p.is_arrow && !p.ammo_item.empty() && RandF() < 0.75f) {
                WorldPickup wp;
                wp.item_id = p.ammo_item;
                wp.model = p.model;
                wp.qty = 1;
                wp.stuck = true;
                wp.dir = Vector3Normalize(p.vel);
                wp.pos = Vector3Subtract(hitPos, Vector3Scale(wp.dir, 0.05f));
                scene_.pickups.push_back(wp);
            } else if (!p.is_arrow) {
                PlaySfxAt("assets/audio/sfx/spell_cast.wav", hitPos, 0.3f);
            }
            if (p.is_arrow) SpawnBurst(hitPos, Color{120, 104, 84, 255}, 6, 1.4f, false);
            else SpawnBurst(hitPos, Color{static_cast<unsigned char>(Clamp(p.light_color.x * 255, 0.0f, 255.0f)), static_cast<unsigned char>(Clamp(p.light_color.y * 255, 0.0f, 255.0f)),
                      static_cast<unsigned char>(Clamp(p.light_color.z * 255, 0.0f, 255.0f)), 255}, 18, 3.2f, true, 2.0f);
            p.alive = false;
            continue;
        }
        p.pos = next;
    }
    scene_.projectiles.erase(std::remove_if(scene_.projectiles.begin(), scene_.projectiles.end(), [](const Projectile& p) { return !p.alive; }),
                             scene_.projectiles.end());
}

void GameEngine::UpdateWorldObjects(float dt) {
    for (auto& in : scene_.interactables) {
        if (in.def.type != "harvest" || !in.used) continue;
        auto h = Persist().harvested.find(in.def.instance_id);
        if (h == Persist().harvested.end() || player_.play_time - h->second >= in.def.respawn_seconds) in.used = false;  // it's grown back
    }
    bool collidersDirty = false;
    for (auto& in : scene_.interactables) {
        float target = in.open ? 1.0f : 0.0f;
        if (in.def.type == "chest") target = in.used ? 1.0f : 0.0f;
        if (in.open_anim != target) {
            float before = in.open_anim;
            float rate = in.def.type == "door" ? 1.6f : 5.0f;
            in.open_anim = target > in.open_anim ? std::min(target, in.open_anim + dt * rate) : std::max(target, in.open_anim - dt * rate);
            if (in.def.type == "door" && ((before < 0.5f) != (in.open_anim < 0.5f))) collidersDirty = true;
        }
    }
    if (collidersDirty) RebuildColliders();

    UpdateBarks(dt);

    for (size_t i = 0; i < pending_spawns_.size();) {
        if (player_.flags.count(pending_spawns_[i]->requires_flag)) {
            SpawnCreature(*pending_spawns_[i]);
            pending_spawns_.erase(pending_spawns_.begin() + i);
        } else {
            i++;
        }
    }
    for (auto& n : scene_.npcs)
        n.hidden = (!n.requires_flag.empty() && !player_.flags.count(n.requires_flag)) ||
                   (!n.hidden_flag.empty() && player_.flags.count(n.hidden_flag) && !IsCompanion(n.def->id));
    UpdateCompanion(dt);

    // NPCs idly turn to face a nearby player and back again.
    for (auto& n : scene_.npcs) {
        n.anim_time += dt;
        if (n.companion) continue;
        float d = HDist(n.pos, player_.pos);
        float target = d < 4.5f ? YawTo(n.pos, player_.pos) : n.base_yaw;
        float diff = WrapAngle(target - n.yaw);
        n.yaw = WrapAngle(n.yaw + Clamp(diff, -2.5f * dt, 2.5f * dt));
    }
}

void GameEngine::CheckPressurePlates() {
    for (auto& in : scene_.interactables) {
        if (in.def.type != "pressure_plate" || in.open) continue;
        if (HDist(player_.pos, in.def.pos) < 0.7f && fabsf(player_.pos.y - in.def.pos.y) < 0.5f) {
            in.open = true;
            Persist().open.insert(in.def.instance_id);
            for (auto& t : scene_.interactables) {
                if (t.def.instance_id == in.def.target_id) {
                    t.open = true;
                    Persist().open.insert(t.def.instance_id);
                }
            }
            res_.PlaySfx("assets/audio/sfx/lever_pull.wav", 0.9f, 0.7f);
            Toast("The rune plate sinks. Somewhere, stone grinds against stone.", Color{180, 220, 255, 255});
            GainSkillXp("perception", 3.0f, true);
        }
    }
}

// ============================================================================
// Interaction
// ============================================================================
void GameEngine::UpdateInteractTarget() {
    interact_ = InteractTarget{};
    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    Vector3 fwd = {sinf(player_.yaw) * cosf(player_.pitch), sinf(player_.pitch), cosf(player_.yaw) * cosf(player_.pitch)};
    float bestScore = 1e9f;
    const float reach = 2.6f;

    auto consider = [&](InteractTarget::Kind kind, int index, Vector3 center, float radius, const std::string& prompt) {
        Vector3 v = Vector3Subtract(center, eye);
        float t = Vector3DotProduct(v, fwd);
        if (t < 0.0f || t > reach + radius) return;
        float perp = Vector3Length(Vector3Subtract(v, Vector3Scale(fwd, t)));
        if (perp > radius) return;
        Vector3 stop = Vector3Add(eye, Vector3Scale(Vector3Normalize(v), std::max(0.0f, Vector3Length(v) - radius - 0.1f)));
        if (!LineOfSight(eye, stop)) return;
        float score = t + perp * 2.0f;
        if (score < bestScore) {
            bestScore = score;
            interact_.kind = kind;
            interact_.index = index;
            interact_.prompt = prompt;
        }
    };

    for (size_t i = 0; i < scene_.interactables.size(); i++) {
        const auto& in = scene_.interactables[i];
        const auto& d = in.def;
        Vector3 c = Vector3Scale(Vector3Add(in.world_box.min, in.world_box.max), 0.5f);
        float r = std::max(0.6f, std::min(1.0f, Vector3Distance(in.world_box.min, in.world_box.max) * 0.45f));
        std::string prompt;
        if (d.type == "door") {
            if (in.open) prompt = d.mechanism_only ? "" : "Close " + d.prompt;
            else if (d.mechanism_only) prompt = d.prompt;
            else if (in.locked) {
                if (!d.key_id.empty() && CountItem(d.key_id) > 0) prompt = "Unlock " + d.prompt;
                else prompt = d.prompt + " (Locked - " + (CountItem("core:item.lockpick") > 0 ? "pick lock" : "needs key") + ")";
            } else prompt = "Open " + d.prompt;
        } else if (d.type == "chest") {
            if (in.locked) prompt = std::string("Locked Chest (") + (CountItem("core:item.lockpick") > 0 ? "pick lock, difficulty " + std::to_string(d.lock_difficulty) : "needs lockpick") + ")";
            else prompt = in.used ? "Search Chest" : "Open Chest";
        } else if (d.type == "readable" || d.type == "lever") {
            prompt = d.prompt;
        } else if (d.type == "quest_pedestal") {
            if (in.used) continue;
            prompt = d.prompt;
            if (!d.requires_dead.empty() && !Persist().dead.count(d.requires_dead)) prompt += " (guarded)";
        } else if (d.type == "pressure_plate") {
            if (in.open) continue;
            prompt = d.prompt;
        } else if (d.type == "harvest") {
            if (in.used) continue;
            prompt = d.prompt;
        } else if (d.type == "station") {
            prompt = d.prompt;
        } else if (d.type == "fishing") {
            prompt = CountItem("core:item.fishing_rod") > 0 ? d.prompt : d.prompt + " (needs a fishing rod)";
        } else continue;
        if (!prompt.empty()) consider(InteractTarget::Interactable, static_cast<int>(i), c, r, prompt);
    }
    for (size_t i = 0; i < scene_.npcs.size(); i++) {
        const auto& n = scene_.npcs[i];
        if (n.hidden) continue;
        consider(InteractTarget::Npc, static_cast<int>(i), {n.pos.x, n.pos.y + 1.0f, n.pos.z}, 0.6f, "Talk to " + content_.Tr(n.def->name_key));
    }
    for (size_t i = 0; i < scene_.creatures.size(); i++) {
        const auto& c = scene_.creatures[i];
        if (c.state != CreatureState::Dead) continue;
        auto it = Persist().containers.find("corpse:" + c.instance_id);
        if (it == Persist().containers.end() || (it->second.items.empty() && it->second.gold == 0)) continue;
        consider(InteractTarget::Corpse, static_cast<int>(i), {c.pos.x, c.pos.y + 0.3f, c.pos.z}, 0.8f, "Search " + content_.Tr(c.def->name_key));
    }
    for (size_t i = 0; i < scene_.pickups.size(); i++) {
        const auto& p = scene_.pickups[i];
        const ItemDef* d = content_.GetItem(p.item_id);
        if (!d) continue;
        consider(InteractTarget::Pickup, static_cast<int>(i), {p.pos.x, p.pos.y + 0.15f, p.pos.z}, 0.45f,
                 "Take " + content_.Tr(d->name_key) + (p.qty > 1 ? " (" + std::to_string(p.qty) + ")" : ""));
    }
    if (interact_.kind == InteractTarget::None && scene_.map) {
        for (size_t i = 0; i < scene_.map->portals.size(); i++) {
            const auto& pt = scene_.map->portals[i];
            if (HDist(player_.pos, pt.pos) < pt.radius) {
                interact_.kind = InteractTarget::Portal;
                interact_.index = static_cast<int>(i);
                interact_.prompt = pt.prompt;
            }
        }
    }
}

void GameEngine::Interact() {
    if (fishing_) { FishPress(); return; }
    UpdateInteractTarget();
    MapPersist& ps = Persist();
    switch (interact_.kind) {
        case InteractTarget::None: return;
        case InteractTarget::Npc: StartDialogue(interact_.index); return;
        case InteractTarget::Portal: {
            const MapPortalDef pt = scene_.map->portals[interact_.index];
            LoadMap(pt.destination_map, pt.destination_spawn);
            SaveGame("autosave");
            return;
        }
        case InteractTarget::Pickup: {
            WorldPickup p = scene_.pickups[interact_.index];
            AddItem(p.item_id, p.qty);
            if (!p.key.empty()) ps.used.insert(p.key);
            scene_.pickups.erase(scene_.pickups.begin() + interact_.index);
            res_.PlaySfx("assets/audio/sfx/item_pickup.wav", 0.7f);
            return;
        }
        case InteractTarget::Corpse: {
            const auto& c = scene_.creatures[interact_.index];
            container_key_ = "corpse:" + c.instance_id;
            container_title_ = content_.Tr(c.def->name_key);
            SetOverlay(Overlay::Container);
            return;
        }
        case InteractTarget::Interactable: break;
    }

    InteractableInstance& in = scene_.interactables[interact_.index];
    const MapInteractableDef& d = in.def;

    auto tryUnlock = [&]() -> bool {
        if (!in.locked) return true;
        if (!d.key_id.empty() && CountItem(d.key_id) > 0) {
            in.locked = false;
            ps.unlocked.insert(d.instance_id);
            const ItemDef* k = content_.GetItem(d.key_id);
            Toast("Unlocked with " + (k ? content_.Tr(k->name_key) : d.key_id));
            return true;
        }
        if (CountItem("core:item.lockpick") > 0) {
            float chance = LockpickChance(d.lock_difficulty);
            if (RandF() < chance) {
                in.locked = false;
                ps.unlocked.insert(d.instance_id);
                res_.PlaySfx("assets/audio/sfx/door_open.wav", 0.5f, 1.4f);
                Toast("Lock picked!", Color{180, 255, 180, 255});
                GainSkillXp("lockpicking", 2.0f + d.lock_difficulty * 0.2f, true);
                return true;
            }
            GainSkillXp("lockpicking", 0.6f, true);
            if (RandF() < 0.5f) {
                RemoveItem("core:item.lockpick", 1);
                Toast("Your lockpick snapped (" + std::to_string(CountItem("core:item.lockpick")) + " left)", Color{255, 160, 120, 255});
            } else {
                Toast("The lock resists...", Color{255, 200, 150, 255});
            }
            res_.PlaySfx("assets/audio/sfx/door_locked.wav", 0.6f, 1.3f);
            return false;
        }
        res_.PlaySfx("assets/audio/sfx/door_locked.wav", 0.8f);
        Toast(d.key_id.empty() ? "Locked. You need a lockpick." : "Locked. You need the right key or a lockpick.");
        return false;
    };

    if (d.type == "door") {
        if (d.mechanism_only && !in.open) {
            res_.PlaySfx("assets/audio/sfx/door_locked.wav", 0.8f, 0.8f);
            Toast("It won't budge. Some mechanism must control it.");
            return;
        }
        if (!tryUnlock()) return;
        in.open = !in.open;
        if (in.open) ps.open.insert(d.instance_id);
        else ps.open.erase(d.instance_id);
        res_.PlaySfx("assets/audio/sfx/door_open.wav", 0.8f, in.open ? 1.0f : 0.85f);
    } else if (d.type == "chest") {
        if (!tryUnlock()) return;
        if (!in.used) {
            in.used = true;
            ps.used.insert(d.instance_id);
            res_.PlaySfx("assets/audio/sfx/chest_open.wav", 0.8f);
        }
        Container(d.instance_id, d.loot_table, d.fixed_items);
        container_key_ = d.instance_id;
        container_title_ = "Chest";
        SetOverlay(Overlay::Container);
    } else if (d.type == "readable") {
        reader_title_ = d.title;
        reader_text_ = d.text;
        res_.PlaySfx("assets/audio/sfx/page_turn.wav", 0.7f);
        if (!ps.used.count(d.instance_id)) {
            ps.used.insert(d.instance_id);
            GainSkillXp("lore", 2.0f, true);
            if (d.sanity != 0) ChangeSanity(static_cast<float>(d.sanity));
        }
        SetOverlay(Overlay::Reader);
        if (!d.set_flag.empty()) player_.flags.insert(d.set_flag);
        if (!d.quest_id.empty() && QuestStage(d.quest_id) < d.set_stage) SetQuestStage(d.quest_id, d.set_stage);
        else if (!d.quest_id.empty() && d.set_stage == 0 && QuestStage(d.quest_id) < 0) SetQuestStage(d.quest_id, 0);
    } else if (d.type == "lever") {
        in.open = !in.open;
        if (in.open) ps.open.insert(d.instance_id); else ps.open.erase(d.instance_id);
        res_.PlaySfx("assets/audio/sfx/lever_pull.wav", 0.9f);
        for (auto& t : scene_.interactables) {
            if (t.def.instance_id == d.target_id) {
                t.open = in.open;
                if (t.open) ps.open.insert(t.def.instance_id); else ps.open.erase(t.def.instance_id);
                Toast(in.open ? "With a grinding clank, a portcullis rises somewhere nearby." : "A portcullis slams shut.");
            }
        }
    } else if (d.type == "harvest") {
        if (in.used) return;
        int n = d.qty_max > d.qty ? d.qty + static_cast<int>(RandF() * (d.qty_max - d.qty + 1)) : d.qty;
        n = std::max(1, n);
        AddItem(d.item_id, n);
        in.used = true;
        ps.harvested[d.instance_id] = player_.play_time;
        Vector3 c = Vector3Scale(Vector3Add(in.world_box.min, in.world_box.max), 0.5f);
        SpawnBurst(c, Color{150, 210, 110, 255}, 12, 1.6f, false, 3.0f);
        res_.PlaySfx("assets/audio/sfx/item_pickup.wav", 0.6f, 1.1f + RandF() * 0.2f);
        GainSkillXp("lore", 0.6f, true);
    } else if (d.type == "fishing") {
        StartFishing(interact_.index);
    } else if (d.type == "station") {
        craft_station_ = d.station;
        craft_selected_.clear();
        SetOverlay(Overlay::Crafting);
    } else if (d.type == "pressure_plate") {
        player_.pos = {d.pos.x, player_.pos.y, d.pos.z};
        CheckPressurePlates();
    } else if (d.type == "quest_pedestal") {
        if (in.used) return;
        if (!d.requires_dead.empty() && !ps.dead.count(d.requires_dead)) {
            const CreatureDef* guard = nullptr;
            for (const auto& c : scene_.creatures) if (c.instance_id == d.requires_dead) guard = c.def;
            Toast((guard ? content_.Tr(guard->name_key) : std::string("Something")) + " will not let you near it.", Color{255, 170, 140, 255});
            return;
        }
        in.used = true;
        ps.used.insert(d.instance_id);
        for (const auto& g : d.grant_items) AddItem(g, 1);
        if (!d.set_flag.empty()) player_.flags.insert(d.set_flag);
        if (!d.quest_id.empty()) SetQuestStage(d.quest_id, d.set_stage);
        res_.PlaySfx("assets/audio/sfx/page_turn.wav", 0.9f);
        if (!d.narration_keys.empty()) StartNarration(d.narration_keys);
    }
}

// ============================================================================
// Quests & dialogue
// ============================================================================
int GameEngine::QuestStage(const std::string& id) const {
    auto it = player_.quest_stages.find(id);
    return it != player_.quest_stages.end() ? it->second : -1;
}

void GameEngine::SetQuestStage(const std::string& id, int stage) {
    if (QuestStage(id) >= stage) return; // quests only move forward
    const QuestDef* q = content_.GetQuest(id);
    if (!q) { Logger::Warn("SetQuestStage: unknown quest '" + id + "'"); return; }
    player_.quest_stages[id] = stage;
    player_.quest_log[id].push_back(stage);
    for (const auto& st : q->stages) {
        if (st.stage != stage) continue;
        Toast("Journal: " + content_.Tr(st.objective_key), Color{255, 225, 150, 255});
        // The side quest you last made progress in is the one on screen; finishing it frees the slot.
        if (id != content_.game_cfg.starting_quest) {
            if (!st.completed) player_.tracked_quest = id;
            else if (player_.tracked_quest == id) player_.tracked_quest.clear();
        }
        // Only the main quest ends the chapter; side quests completing must not trigger the ending screen.
        if (st.completed && id == content_.game_cfg.starting_quest) ending_stage_ = stage;
    }
    res_.PlaySfx("assets/audio/sfx/page_turn.wav", 0.8f, 0.9f);
}

bool GameEngine::EvalCondition(const DialogueCondition& c) const {
    if (c.type == "quest_stage_equals") return QuestStage(c.quest_id) == c.stage;
    if (c.type == "quest_stage_at_least") return QuestStage(c.quest_id) >= c.stage;
    if (c.type == "quest_stage_below") return QuestStage(c.quest_id) < c.stage;
    if (c.type == "has_item") return CountItem(c.item_id) > 0;
    if (c.type == "race_is") return player_.race_id == c.race_id;
    if (c.type == "skill_at_least") return SkillLevel(c.skill) >= c.value;
    if (c.type == "flag_set") return player_.flags.count(c.flag) > 0;
    if (c.type == "flag_not_set") return player_.flags.count(c.flag) == 0;
    if (c.type == "party_has_room") return static_cast<int>(player_.companions.size()) < kMaxCompanions;
    if (c.type == "party_full") return static_cast<int>(player_.companions.size()) >= kMaxCompanions;
    if (c.type == "item_equipped") return IsEquipped(c.item_id);
    if (c.type == "item_not_equipped") return !IsEquipped(c.item_id);
    if (c.type == "flags_at_least" || c.type == "flags_fewer_than") {
        int n = 0;
        for (const auto& f : c.flags) n += player_.flags.count(f) ? 1 : 0;
        return c.type == "flags_at_least" ? n >= c.value : n < c.value;
    }
    if (c.type == "gold_at_least") return player_.gold >= c.value;
    Logger::Warn("Unknown dialogue condition type '" + c.type + "'");
    return false;
}

void GameEngine::ExecAction(const DialogueAction& a, const std::string& rewardKey) {
    bool reward = a.type == "give_item" || a.type == "give_gold" || a.type == "give_xp";
    if (reward && player_.claimed.count(rewardKey)) return; // conversation rewards can only be collected once
    if (a.type == "set_quest_stage") SetQuestStage(a.quest_id, a.stage);
    else if (a.type == "give_item") AddItem(a.item_id, a.qty);
    else if (a.type == "take_item") {
        if (RemoveItem(a.item_id, a.qty))
            if (const ItemDef* d = content_.GetItem(a.item_id)) Toast("- " + content_.Tr(d->name_key));
    } else if (a.type == "give_gold") {
        player_.gold += a.amount;
        Toast("+ " + std::to_string(a.amount) + " gold", Color{255, 215, 100, 255});
        res_.PlaySfx("assets/audio/sfx/coin_jingle.wav", 0.8f);
    } else if (a.type == "give_xp") {
        GainXp(a.amount);
        if (!a.skill.empty()) GainSkillXp(a.skill, a.amount * 0.15f, true);
    } else if (a.type == "set_flag") {
        if (a.bool_value) player_.flags.insert(a.flag); else player_.flags.erase(a.flag);
    } else if (a.type == "sanity") {
        ChangeSanity(static_cast<float>(a.amount));
    } else if (a.type == "heal_player") {
        player_.sanity = 100.0f;
        player_.health = static_cast<float>(MaxHealth());
        player_.stamina = static_cast<float>(MaxStamina());
        player_.mana = static_cast<float>(MaxMana());
        res_.PlaySfx("assets/audio/sfx/spell_heal.wav", 0.7f);
        Toast("You feel restored", Color{150, 255, 170, 255});
    } else if (a.type == "narrate") {
        std::vector<std::string> keys;
        for (const auto& [key, flag] : a.pages)
            if (flag.empty() || player_.flags.count(flag)) keys.push_back(key);
        if (!keys.empty()) StartNarration(keys);
    } else if (a.type == "recruit_companion") {
        if (dialogue_npc_ >= 0 && dialogue_npc_ < static_cast<int>(scene_.npcs.size()) && scene_.npcs[dialogue_npc_].def->companion.enabled) {
            const NpcDef* d = scene_.npcs[dialogue_npc_].def;
            if (IsCompanion(d->id)) {
            } else if (static_cast<int>(player_.companions.size()) >= kMaxCompanions) {
                Toast("Your party is full. Ask someone to wait first.", Color{255, 180, 140, 255});
            } else {
                player_.companions.push_back(d->id);
                if (player_.companions.size() == 1) companion_last_zone_ = zone_id_;
                companion_idle_cd_ = 40.0f;
                Toast(content_.Tr(d->name_key) + " is travelling with you", Color{255, 220, 150, 255});
            }
        }
    } else if (a.type == "dismiss_companion") {
        if (dialogue_npc_ >= 0 && dialogue_npc_ < static_cast<int>(scene_.npcs.size())) {
            NpcInstance& n = scene_.npcs[dialogue_npc_];
            if (IsCompanion(n.def->id)) {
                player_.companions.erase(std::find(player_.companions.begin(), player_.companions.end(), n.def->id));
                n.companion = false;
                n.pos = n.home;
                n.yaw = n.base_yaw;
                n.anim = "idle";
                Toast(content_.Tr(n.def->name_key) + " heads back to wait for you");
            }
        }
    } else if (a.type == "take_gold") {
        player_.gold = std::max(0, player_.gold - a.amount);
        Toast("- " + std::to_string(a.amount) + " gold", Color{255, 215, 100, 255});
    } else if (a.type == "reset_perks") {
        player_.perks.clear();
        Toast("Your perks are yours to choose again", Color{255, 210, 120, 255});
        ClampVitals();
    } else if (a.type == "learn_spell") {
        if (std::find(player_.known_spells.begin(), player_.known_spells.end(), a.spell_id) == player_.known_spells.end()) {
            player_.known_spells.push_back(a.spell_id);
            if (const SpellDef* s = content_.GetSpell(a.spell_id)) Toast("Learned spell: " + content_.Tr(s->name_key), Color{180, 160, 255, 255});
        }
    } else if (a.type == "travel") {
        // Boats and the like: jump to a spawn in the current map. Companions catch up on their own (they're "lost").
        if (scene_.map) {
            auto it = scene_.map->spawns.find(a.spawn);
            if (it != scene_.map->spawns.end()) {
                player_.pos = it->second.pos;
                player_.pos.y = GroundHeight({it->second.pos.x, it->second.pos.y + 0.5f, it->second.pos.z}, kStepHeight);
                player_.yaw = it->second.yaw_degrees * DEG2RAD;
                player_.vel = {0, 0, 0};
            } else {
                Logger::Warn("travel: unknown spawn '" + a.spawn + "'");
            }
        }
    } else if (a.type == "open_shop") {
        if (dialogue_npc_ >= 0 && dialogue_npc_ < static_cast<int>(scene_.npcs.size())) shop_npc_ = scene_.npcs[dialogue_npc_].def->id;
    } else {
        Logger::Warn("Unknown dialogue action type '" + a.type + "'");
    }
}

void GameEngine::StartDialogue(int npcIndex) {
    const NpcInstance& n = scene_.npcs[npcIndex];
    const DialogueDef* d = content_.GetDialogue(n.def->dialogue_id);
    if (!d) {
        Toast(content_.Tr(n.def->name_key) + " has nothing to say.");
        return;
    }
    dialogue_npc_ = npcIndex;
    dialogue_id_ = d->id;
    shop_npc_.clear();
    SetOverlay(Overlay::Dialogue);
    dialogue_id_ = d->id;
    EnterDialogueNode(d->root_node);
}

void GameEngine::EnterDialogueNode(const std::string& node) {
    const DialogueDef* d = content_.GetDialogue(dialogue_id_);
    if (!d || node == "END") { EndDialogue(); return; }
    auto it = d->nodes.find(node);
    if (it == d->nodes.end()) {
        Logger::Error("Dialogue '" + dialogue_id_ + "' references missing node '" + node + "'");
        EndDialogue();
        return;
    }
    dialogue_node_ = node;
    std::string key = dialogue_id_ + "/" + node;
    for (size_t i = 0; i < it->second.actions.size(); i++) ExecAction(it->second.actions[i], key);
    player_.claimed.insert(key);
    ui_scroll_ = 0.0f;
}

std::vector<int> GameEngine::VisibleChoices() const {
    std::vector<int> out;
    const DialogueDef* d = content_.GetDialogue(dialogue_id_);
    if (!d) return out;
    auto it = d->nodes.find(dialogue_node_);
    if (it == d->nodes.end()) return out;
    for (size_t i = 0; i < it->second.choices.size(); i++) {
        bool ok = true;
        for (const auto& c : it->second.choices[i].conditions) ok = ok && EvalCondition(c);
        if (ok) out.push_back(static_cast<int>(i));
    }
    return out;
}

void GameEngine::ChooseDialogue(int choiceIndex) {
    const DialogueDef* d = content_.GetDialogue(dialogue_id_);
    if (!d) { EndDialogue(); return; }
    auto it = d->nodes.find(dialogue_node_);
    if (it == d->nodes.end() || choiceIndex >= static_cast<int>(it->second.choices.size())) { EndDialogue(); return; }
    const DialogueChoice ch = it->second.choices[choiceIndex];
    std::string key = dialogue_id_ + "/" + dialogue_node_ + "#" + std::to_string(choiceIndex);
    if (ch.roll_dc > 0) {
        int bonus = 0;
        bool rigged = false;
        int d20 = RollD20(ch, bonus, rigged);
        if (rigged) player_.claimed.insert("rigged:" + key);
        bool ok = d20 == 20 || (d20 != 1 && d20 + bonus >= ch.roll_dc);
        std::string verdict = d20 == 20 ? "CRITICAL SUCCESS!" : d20 == 1 ? "Natural 1. Critical failure." : ok ? "Success" : "Failure";
        Toast("[d20] " + std::to_string(d20) + " + " + std::to_string(bonus) + " vs DC " + std::to_string(ch.roll_dc) + "  -  " + verdict,
              ok ? Color{150, 230, 150, 255} : Color{255, 140, 120, 255});
        if (!ok) { EnterDialogueNode(ch.fail_next); return; }
    }
    for (const auto& a : ch.actions) ExecAction(a, key);
    player_.claimed.insert(key);
    if (!shop_npc_.empty()) {
        dialogue_id_.clear();
        SetOverlay(Overlay::Shop);
        return;
    }
    EnterDialogueNode(ch.next);
}

int GameEngine::DialogueRollChance(const DialogueChoice& ch) const {
    int bonus = SkillLevel(ch.roll_skill) / 4 + (ch.roll_skill == "persuasion" ? (Attr("presence") - 10) / 2 : 0) +
                static_cast<int>(Bonus("dice_bonus"));
    int need = ch.roll_dc - bonus;  // d20 >= need passes; 1 always fails, 20 always passes
    int pass = 21 - std::clamp(need, 2, 20);
    return pass * 5;
}

int GameEngine::RollD20(const DialogueChoice& ch, int& bonus, bool& rigged) {
    bonus = SkillLevel(ch.roll_skill) / 4 + (ch.roll_skill == "persuasion" ? (Attr("presence") - 10) / 2 : 0) +
            static_cast<int>(Bonus("dice_bonus"));
    std::string key = dialogue_id_ + "/" + dialogue_node_;
    rigged = false;
    if (ch.roll_rigged) {
        // The dice remember. The first attempt at a 'sure thing' is always a natural 1.
        bool already = false;
        for (const auto& c : player_.claimed) if (c.rfind("rigged:" + key, 0) == 0) already = true;
        if (!already) { rigged = true; return 1; }
    }
    return 1 + std::min(19, static_cast<int>(RandF() * 20.0f));
}

void GameEngine::EndDialogue() {
    dialogue_id_.clear();
    dialogue_node_.clear();
    if (overlay_ == Overlay::Dialogue) SetOverlay(Overlay::None);
    if (ending_stage_ != 0 && !ending_shown_) {
        ending_shown_ = true;
        screen_ = Screen::Ending;
        SaveGame("autosave");
    }
}

// ============================================================================
// Containers & trade
// ============================================================================
void GameEngine::RollLoot(const std::string& tableId, ContainerState& out) {
    auto it = content_.loot_tables.find(tableId);
    if (it == content_.loot_tables.end()) return;
    const LootTableDef& t = it->second;
    out.gold += RandInt(t.gold_min, t.gold_max);
    auto addUnique = [&](const std::string& id, int qty) {
        const ItemDef* d = content_.GetItem(id);
        if (!d) return;
        if (!d->stackable && d->category != "ammo") {
            for (const auto& e : out.items) if (e.id == id) return;
        }
        for (auto& e : out.items) {
            if (e.id == id && (d->stackable || d->category == "ammo")) { e.qty += qty; return; }
        }
        out.items.push_back({id, qty});
    };
    for (const auto& g : t.guaranteed) addUnique(g, 1);
    for (const auto& e : t.entries) {
        if (RandInt(1, 100) <= e.weight) addUnique(e.item_id, RandInt(e.min_qty, e.max_qty));
    }
}

ContainerState& GameEngine::Container(const std::string& key, const std::string& lootTable, const std::vector<std::string>& fixed) {
    ContainerState& c = Persist().containers[key];
    if (!c.generated) {
        c.generated = true;
        for (const auto& f : fixed) {
            const ItemDef* d = content_.GetItem(f);
            bool merged = false;
            if (d && (d->stackable || d->category == "ammo")) {
                for (auto& e : c.items) if (e.id == f) { e.qty += (d->category == "ammo" ? 10 : 1); merged = true; }
            }
            if (!merged) c.items.push_back({f, d && d->category == "ammo" ? 10 : 1});
        }
        RollLoot(lootTable, c);
    }
    return c;
}

void GameEngine::TakeFromContainer(int index) {
    ContainerState& c = Persist().containers[container_key_];
    if (index == -1) {
        if (c.gold > 0) {
            c.gold = static_cast<int>(std::round(c.gold * (1.0f + Bonus("gold_find_bonus"))));
            player_.gold += c.gold;
            Toast("+ " + std::to_string(c.gold) + " gold", Color{255, 215, 100, 255});
            res_.PlaySfx("assets/audio/sfx/coin_jingle.wav", 0.7f);
            c.gold = 0;
        }
        return;
    }
    if (index < 0 || index >= static_cast<int>(c.items.size())) return;
    InvItem it = c.items[index];
    c.items.erase(c.items.begin() + index);
    AddItem(it.id, it.qty);
    res_.PlaySfx("assets/audio/sfx/item_pickup.wav", 0.5f);
}

void GameEngine::TakeAllFromContainer() {
    TakeFromContainer(-1);
    ContainerState& c = Persist().containers[container_key_];
    while (!c.items.empty()) TakeFromContainer(0);
    SetOverlay(Overlay::None);
}

int GameEngine::VendorStock(const NpcDef& npc, const VendorStockEntry& e) const {
    auto it = vendor_sold_.find(npc.id);
    int sold = 0;
    if (it != vendor_sold_.end()) {
        auto s = it->second.find(e.item_id);
        if (s != it->second.end()) sold = s->second;
    }
    return std::max(0, e.stock - sold);
}

int GameEngine::BuyPrice(const VendorStockEntry& e) const {
    float disc = ShopDiscount();
    return std::max(1, static_cast<int>(std::round(e.price * (1.0f - disc))));
}

int GameEngine::SellPrice(const ItemDef& item) const {
    float mult = 0.35f + std::min(0.2f, SkillLevel("persuasion") * 0.004f + (Attr("presence") - 10) * 0.01f);
    return std::max(1, static_cast<int>(std::round(item.value * mult)));
}

void GameEngine::BuyItem(const VendorStockEntry& e) {
    const NpcDef* npc = content_.GetNpc(shop_npc_);
    if (!npc || VendorStock(*npc, e) <= 0) return;
    int price = BuyPrice(e);
    if (player_.gold < price) { Toast("Not enough gold", Color{255, 150, 120, 255}); return; }
    player_.gold -= price;
    vendor_sold_[npc->id][e.item_id]++;
    AddItem(e.item_id, 1);
    res_.PlaySfx("assets/audio/sfx/coin_jingle.wav", 0.7f);
    GainSkillXp("persuasion", 0.8f);
}

void GameEngine::SellItem(const std::string& id) {
    const ItemDef* d = content_.GetItem(id);
    const NpcDef* npc = content_.GetNpc(shop_npc_);
    if (!d || !npc || d->quest_item || CountItem(id) == 0) return;
    if (IsEquipped(id) && CountItem(id) == 1) {
        for (auto& [slot, e] : player_.equipment) if (e == id) e.clear();
    }
    RemoveItem(id, 1);
    player_.gold += SellPrice(*d);
    // Sold goods return to a vendor's stock if they carry that line.
    auto& sold = vendor_sold_[npc->id];
    if (sold.count(id) && sold[id] > 0) sold[id]--;
    res_.PlaySfx("assets/audio/sfx/coin_jingle.wav", 0.6f, 1.1f);
    GainSkillXp("persuasion", 0.8f);
}

// ============================================================================
// Save / load (atomic: write .tmp, back up previous to .bak, rename)
// ============================================================================
static json V3(Vector3 v) { return json::array({v.x, v.y, v.z}); }
static Vector3 V3(const json& j) {
    if (j.is_array() && j.size() >= 3) return {j[0].get<float>(), j[1].get<float>(), j[2].get<float>()};
    return {0, 0, 0};
}

std::string GameEngine::SavePath(const std::string& slot) const { return "saves/" + slot + ".json"; }
bool GameEngine::SaveExists(const std::string& slot) const { return fs::exists(SavePath(slot)); }

bool GameEngine::SaveGame(const std::string& slot) {
    if (screen_ != Screen::Playing && screen_ != Screen::Ending) return false;
    json j;
    j["save_version"] = 1;
    j["map"] = current_map_;
    j["ending_shown"] = ending_shown_;
    j["timestamp"] = static_cast<long long>(time(nullptr));
    const PlayerState& p = player_;
    json pj;
    pj["name"] = p.name;
    pj["race"] = p.race_id;
    pj["background"] = p.background_id;
    pj["archetype"] = p.archetype_id;
    pj["attributes"] = p.attributes;
    json sk = json::object();
    for (const auto& [id, s] : p.skills) sk[id] = {{"level", s.level}, {"xp", s.xp}};
    pj["skills"] = sk;
    pj["level"] = p.level;
    pj["xp"] = p.xp;
    pj["unspent_points"] = p.unspent_points;
    pj["health"] = p.health;
    pj["stamina"] = p.stamina;
    pj["mana"] = p.mana;
    pj["gold"] = p.gold;
    json inv = json::array();
    for (const auto& it : p.inventory) inv.push_back({{"id", it.id}, {"qty", it.qty}});
    pj["inventory"] = inv;
    pj["equipment"] = p.equipment;
    pj["known_spells"] = p.known_spells;
    pj["perks"] = std::vector<std::string>(p.perks.begin(), p.perks.end());
    pj["selected_spell"] = p.selected_spell;
    pj["quick_slots"] = std::vector<std::string>(p.quick_slots.begin(), p.quick_slots.end());
    json buffs = json::array();
    for (const auto& b : p.buffs) {
        if (b.primitive == "food")
            buffs.push_back({{"item", b.item_id}, {"remaining", b.remaining}, {"bonus", b.bonus_key}, {"value", b.bonus_value}, {"duration", b.duration}});
        else
            buffs.push_back({{"spell", b.spell_id}, {"remaining", b.remaining}, {"power", b.power}});
    }
    pj["buffs"] = buffs;
    pj["quest_stages"] = p.quest_stages;
    pj["quest_log"] = p.quest_log;
    pj["flags"] = p.flags;
    pj["companions"] = p.companions;
    pj["sanity"] = p.sanity;
    pj["tracked_quest"] = p.tracked_quest;
    pj["claimed"] = p.claimed;
    pj["play_time"] = p.play_time;
    pj["pos"] = V3(p.pos);
    pj["yaw"] = p.yaw;
    pj["pitch"] = p.pitch;
    j["player"] = pj;

    json maps = json::object();
    for (const auto& [id, ps] : persist_) {
        json m;
        m["open"] = ps.open;
        m["unlocked"] = ps.unlocked;
        m["used"] = ps.used;
        m["dead"] = ps.dead;
        json cp = json::object();
        for (const auto& [k, v] : ps.corpse_pos) cp[k] = V3(v);
        m["corpse_pos"] = cp;
        json hv = json::object();
        for (const auto& [k, t] : ps.harvested) hv[k] = t;
        m["harvested"] = hv;
        json cs = json::object();
        for (const auto& [k, c] : ps.containers) {
            json items = json::array();
            for (const auto& it : c.items) items.push_back({{"id", it.id}, {"qty", it.qty}});
            cs[k] = {{"generated", c.generated}, {"gold", c.gold}, {"items", items}};
        }
        m["containers"] = cs;
        maps[id] = m;
    }
    j["maps"] = maps;
    j["vendor_sold"] = vendor_sold_;

    std::error_code ec;
    fs::create_directories("saves", ec);
    std::string path = SavePath(slot);
    std::string tmp = path + ".tmp";
    {
        std::ofstream ofs(tmp, std::ios::trunc);
        if (!ofs.is_open()) { Logger::Error("Cannot write save file " + tmp); Toast("Save failed!", RED); return false; }
        ofs << j.dump(1);
        if (!ofs.good()) { Logger::Error("Write error on " + tmp); return false; }
    }
    if (fs::exists(path)) fs::copy_file(path, path + ".bak", fs::copy_options::overwrite_existing, ec);
    fs::rename(tmp, path, ec);
    if (ec) {
        fs::remove(path, ec);
        ec.clear();
        fs::rename(tmp, path, ec);
        if (ec) { Logger::Error("Failed to finalise save " + path + ": " + ec.message()); return false; }
    }
    Logger::Info("Saved game to " + path);
    return true;
}

bool GameEngine::LoadGame(const std::string& slot) {
    std::string path = SavePath(slot);
    json j;
    auto readJson = [&](const std::string& p) {
        std::ifstream ifs(p);
        if (!ifs.is_open()) return false;
        try { ifs >> j; return true; } catch (const std::exception& e) {
            Logger::Error("Corrupt save '" + p + "': " + e.what());
            return false;
        }
    };
    if (!readJson(path)) {
        if (!readJson(path + ".bak")) { Toast("Could not load save", RED); return false; }
        Toast("Save was damaged; restored the backup copy", Color{255, 200, 120, 255});
    }
    try {
        PlayerState p;
        const json& pj = j.at("player");
        p.name = pj.value("name", "Nameless");
        p.race_id = pj.value("race", "");
        p.background_id = pj.value("background", "");
        p.archetype_id = pj.value("archetype", "");
        p.attributes = pj.value("attributes", std::map<std::string, int>{});
        for (auto it = pj["skills"].begin(); it != pj["skills"].end(); ++it) {
            p.skills[it.key()].level = it.value().value("level", 5);
            p.skills[it.key()].xp = it.value().value("xp", 0.0f);
        }
        p.level = pj.value("level", 1);
        p.xp = pj.value("xp", 0);
        p.unspent_points = pj.value("unspent_points", 0);
        p.health = pj.value("health", 50.0f);
        p.stamina = pj.value("stamina", 50.0f);
        p.mana = pj.value("mana", 30.0f);
        p.gold = pj.value("gold", 0);
        for (const auto& it : pj["inventory"]) p.inventory.push_back({it.value("id", ""), it.value("qty", 1)});
        p.equipment = pj.value("equipment", std::map<std::string, std::string>{});
        p.known_spells = pj.value("known_spells", std::vector<std::string>{});
        {
            auto v = pj.value("perks", std::vector<std::string>{});
            p.perks = std::set<std::string>(v.begin(), v.end());
        }
        p.selected_spell = pj.value("selected_spell", 0);
        auto qs = pj.value("quick_slots", std::vector<std::string>{});
        for (size_t i = 0; i < qs.size() && i < 4; i++) p.quick_slots[i] = qs[i];
        p.quest_stages = pj.value("quest_stages", std::map<std::string, int>{});
        p.quest_log = pj.value("quest_log", std::map<std::string, std::vector<int>>{});
        p.flags = pj.value("flags", std::set<std::string>{});
        p.companions = pj.value("companions", std::vector<std::string>{});
        if (p.companions.empty() && !pj.value("companion", std::string{}).empty()) p.companions.push_back(pj["companion"].get<std::string>());
        p.tracked_quest = pj.value("tracked_quest", std::string{});
        p.sanity = pj.value("sanity", 100.0f);
        p.claimed = pj.value("claimed", std::set<std::string>{});
        p.play_time = pj.value("play_time", 0.0);
        p.pos = V3(pj["pos"]);
        p.yaw = pj.value("yaw", 0.0f);
        p.pitch = pj.value("pitch", 0.0f);
        if (pj.contains("buffs")) {
            for (const auto& b : pj["buffs"]) {
                if (b.contains("item")) {
                    ActiveBuff fb;
                    fb.primitive = "food";
                    fb.item_id = b.value("item", "");
                    fb.bonus_key = b.value("bonus", "");
                    fb.bonus_value = b.value("value", 0.0f);
                    fb.remaining = b.value("remaining", 1.0f);
                    fb.duration = b.value("duration", fb.remaining);
                    p.buffs.push_back(fb);
                    continue;
                }
                const SpellDef* s = content_.GetSpell(b.value("spell", ""));
                if (!s) continue;
                ActiveBuff ab;
                ab.spell_id = s->id;
                ab.primitive = s->effect.primitive;
                ab.remaining = b.value("remaining", 1.0f);
                ab.duration = s->effect.duration_seconds;
                ab.power = b.value("power", 0.0f);
                ab.light_color = s->effect.light_color;
                ab.light_radius = s->effect.light_radius;
                ab.visibility = s->effect.visibility_multiplier;
                p.buffs.push_back(ab);
            }
        }

        std::map<std::string, MapPersist> persist;
        for (auto it = j["maps"].begin(); it != j["maps"].end(); ++it) {
            MapPersist ps;
            const json& m = it.value();
            ps.open = m.value("open", std::set<std::string>{});
            ps.unlocked = m.value("unlocked", std::set<std::string>{});
            ps.used = m.value("used", std::set<std::string>{});
            ps.dead = m.value("dead", std::set<std::string>{});
            if (m.contains("corpse_pos"))
                for (auto c = m["corpse_pos"].begin(); c != m["corpse_pos"].end(); ++c) ps.corpse_pos[c.key()] = V3(c.value());
            if (m.contains("harvested"))
                for (auto h = m["harvested"].begin(); h != m["harvested"].end(); ++h) ps.harvested[h.key()] = h.value().get<double>();
            if (m.contains("containers")) {
                for (auto c = m["containers"].begin(); c != m["containers"].end(); ++c) {
                    ContainerState cs;
                    cs.generated = c.value().value("generated", true);
                    cs.gold = c.value().value("gold", 0);
                    for (const auto& it2 : c.value()["items"]) cs.items.push_back({it2.value("id", ""), it2.value("qty", 1)});
                    ps.containers[c.key()] = cs;
                }
            }
            persist[it.key()] = ps;
        }

        player_ = p;
        persist_ = persist;
        vendor_sold_ = j.value("vendor_sold", std::map<std::string, std::map<std::string, int>>{});
        ending_shown_ = j.value("ending_shown", false);
        ending_stage_ = 0;
        for (const auto& [qid, st] : player_.quest_stages) {
            if (qid != content_.game_cfg.starting_quest) continue;
            if (const QuestDef* q = content_.GetQuest(qid))
                for (const auto& s : q->stages) if (s.stage == st && s.completed) ending_stage_ = st;
        }
        screen_ = Screen::Playing;
        overlay_ = Overlay::None;
        toasts_.clear();
        std::string map = j.value("map", content_.game_cfg.starting_map);
        Vector3 pos = player_.pos;
        float yaw = player_.yaw, pitch = player_.pitch;
        LoadMap(map, "", true);
        player_.pos = pos;
        player_.pos.y = GroundHeight({pos.x, pos.y + 0.5f, pos.z}, kStepHeight);
        player_.yaw = yaw;
        player_.pitch = pitch;
        ClampVitals();
        Toast("Game loaded");
        return true;
    } catch (const std::exception& e) {
        Logger::Error(std::string("Save load failed: ") + e.what());
        Toast("Save file is incompatible", RED);
        return false;
    }
}

// ============================================================================
// Story presentation: subtitles, ambient barks, prologue
// ============================================================================
void GameEngine::Say(const std::string& speaker, const std::string& text, float seconds) {
    subtitle_speaker_ = speaker;
    subtitle_text_ = text;
    subtitle_time_ = seconds > 0 ? seconds : Clamp(2.5f + text.size() * 0.055f, 3.0f, 9.0f);
}

void GameEngine::UpdateBarks(float dt) {
    subtitle_time_ = std::max(0.0f, subtitle_time_ - dt);
    bark_global_cd_ = std::max(0.0f, bark_global_cd_ - dt);
    for (auto& [id, cd] : bark_cd_) cd = std::max(0.0f, cd - dt);
    if (subtitle_time_ > 0.0f || bark_global_cd_ > 0.0f || overlay_ != Overlay::None) return;

    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height, player_.pos.z};
    for (const auto& n : scene_.npcs) {
        if (n.companion || n.hidden || n.def->barks.empty() || bark_cd_[n.instance_id] > 0.0f) continue;  // companions use their own chatter
        if (Vector3Distance(n.pos, player_.pos) > 6.5f || !LineOfSight({n.pos.x, n.pos.y + 1.5f, n.pos.z}, eye)) continue;
        int count = static_cast<int>(n.def->barks.size());
        for (int k = 0; k < count; k++) {
            int idx = (bark_next_[n.instance_id] + k) % count;
            const NpcBarkDef& b = n.def->barks[idx];
            if (!b.quest_id.empty()) {
                int st = QuestStage(b.quest_id);
                if (st < b.min_stage || st > b.max_stage) continue;
            }
            if (!b.flag.empty() && !player_.flags.count(b.flag)) continue;
            if (!b.not_flag.empty() && player_.flags.count(b.not_flag)) continue;
            bark_next_[n.instance_id] = idx + 1;
            Say(content_.Tr(n.def->name_key), content_.Tr(b.text_key));
            bark_cd_[n.instance_id] = 22.0f + RandF() * 18.0f;
            bark_global_cd_ = 7.0f;
            return;
        }
    }
}

void GameEngine::AdvanceNarration() {
    if (narration_page_ < static_cast<int>(narration_pages_.size())) return;
    narration_pages_.clear();
    SetOverlay(Overlay::None);
    if (!narration_is_prologue_) return;
    narration_is_prologue_ = false;
    if (const ItemDef* notice = content_.GetItem("core:item.death_notice"); notice && CountItem(notice->id) > 0) {
        reader_title_ = content_.Tr(notice->name_key);
        reader_text_ = content_.Tr(notice->book_text_key);
        SetOverlay(Overlay::Reader);
    }
}

void GameEngine::StartNarration(const std::vector<std::string>& keys) {
    narration_pages_.clear();
    for (const auto& k : keys) narration_pages_.push_back(content_.Tr(k));
    narration_page_ = 0;
    narration_time_ = 0.0f;
    narration_is_prologue_ = false;
    if (!narration_pages_.empty()) SetOverlay(Overlay::Narration);
}

std::vector<std::string> GameEngine::QuestOrder() const {
    // Main quest first, then side quests in the order they were started (by id for stability).
    std::vector<std::string> out;
    if (player_.quest_stages.count(content_.game_cfg.starting_quest)) out.push_back(content_.game_cfg.starting_quest);
    for (const auto& [qid, st] : player_.quest_stages)
        if (qid != content_.game_cfg.starting_quest) out.push_back(qid);
    return out;
}

// ============================================================================
// Particles
// ============================================================================
void GameEngine::SpawnBurst(Vector3 pos, Color color, int count, float speed, bool glow, float gravity, float size) {
    for (int i = 0; i < count; i++) {
        Particle pt;
        pt.pos = pos;
        Vector3 dir = {RandF() * 2 - 1, RandF() * 1.4f - 0.3f, RandF() * 2 - 1};
        pt.vel = Vector3Scale(Vector3Normalize(dir), speed * (0.4f + RandF() * 0.8f));
        float k = 0.75f + RandF() * 0.4f;
        pt.color = {static_cast<unsigned char>(Clamp(color.r * k, 0.0f, 255.0f)), static_cast<unsigned char>(Clamp(color.g * k, 0.0f, 255.0f)),
                    static_cast<unsigned char>(Clamp(color.b * k, 0.0f, 255.0f)), 255};
        pt.life = pt.max_life = 0.35f + RandF() * 0.45f;
        pt.size = size * (0.7f + RandF() * 0.8f);
        pt.gravity = gravity;
        pt.glow = glow;
        scene_.particles.push_back(pt);
    }
    if (scene_.particles.size() > 600)
        scene_.particles.erase(scene_.particles.begin(), scene_.particles.begin() + static_cast<long>(scene_.particles.size() - 600));
}

void GameEngine::UpdateParticles(float dt) {
    for (auto& pt : scene_.particles) {
        pt.vel.y -= pt.gravity * dt;
        pt.vel = Vector3Scale(pt.vel, 1.0f - std::min(1.0f, dt * 1.5f));
        pt.pos = Vector3Add(pt.pos, Vector3Scale(pt.vel, dt));
        pt.life -= dt;
    }
    scene_.particles.erase(std::remove_if(scene_.particles.begin(), scene_.particles.end(), [](const Particle& p) { return p.life <= 0; }),
                           scene_.particles.end());
}

// ============================================================================
// Feedback
// ============================================================================
void GameEngine::Toast(const std::string& text, Color color) {
    toasts_.push_back({text, color, 4.5f});
    if (toasts_.size() > 7) toasts_.erase(toasts_.begin());
}

void GameEngine::PlaySfxAt(const std::string& path, Vector3 pos, float volume) {
    float d = Vector3Distance(pos, player_.pos);
    float att = Clamp(1.0f - d / 28.0f, 0.0f, 1.0f);
    if (att <= 0.01f) return;
    res_.PlaySfx(path, volume * att, 0.95f + RandF() * 0.1f);
}

} // namespace uncounted

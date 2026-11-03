// UI layer of GameEngine: HUD, menus, overlays. All layout is in a virtual space whose height is ~720 units,
// scaled by U() to the window, so the interface stays crisp at any resolution.
#include "gameplay/GameEngine.h"
#include "core/Logger.h"
#include "raymath.h"
#include <algorithm>
#include <cmath>
#include <filesystem>
#include <cstdio>

namespace fs = std::filesystem;

namespace uncounted {

static const Color kGold = {226, 196, 128, 255};
static const Color kText = {228, 222, 206, 255};
static const Color kDim = {150, 146, 136, 255};
static const Color kAccent = {120, 190, 255, 255};
static const Color kPanelEdge = {120, 100, 70, 255};

static std::string Pct(float v) {
    char b[32];
    snprintf(b, sizeof(b), "%.0f%%", v * 100.0f);
    return b;
}

// Human-readable line for a named build bonus (synergies and "bonus" gear effects).
static std::string BonusLabel(const std::string& key, float v) {
    char b[96];
    if (key == "melee_bonus_magic_damage") snprintf(b, sizeof(b), "+%.0f magic damage per melee hit", v);
    else if (key == "mana_on_melee_hit") snprintf(b, sizeof(b), "+%.0f mana per melee hit", v);
    else if (key == "heal_on_block") snprintf(b, sizeof(b), "+%.0f health per block", v);
    else if (key == "armor_bonus") snprintf(b, sizeof(b), "+%.0f armor", v);
    else if (key == "ranged_crit_multiplier") snprintf(b, sizeof(b), "x%.2f sneak-arrow damage", v);
    else if (key == "move_speed_bonus") snprintf(b, sizeof(b), "+%.0f%% move speed", v * 100);
    else if (key == "crit_chance_bonus") snprintf(b, sizeof(b), "+%.0f%% critical chance", v * 100);
    else if (key == "crit_damage_bonus") snprintf(b, sizeof(b), "+%.2f critical multiplier", v);
    else if (key == "life_steal") snprintf(b, sizeof(b), "%.0f%% life steal", v * 100);
    else if (key == "spell_power_bonus") snprintf(b, sizeof(b), "+%.0f%% spell power", v * 100);
    else if (key == "spell_cost_reduction") snprintf(b, sizeof(b), "-%.0f%% spell cost", v * 100);
    else if (key == "shop_discount") snprintf(b, sizeof(b), "+%.0f%% shop discount", v * 100);
    else if (key == "lockpick_bonus") snprintf(b, sizeof(b), "+%.0f%% lockpick chance", v * 100);
    else if (key == "sanity_regen") snprintf(b, sizeof(b), "+%.1f sanity per second", v);
    else if (key == "dice_bonus") snprintf(b, sizeof(b), "+%.0f to dice rolls", v);
    else if (key == "health_regen") snprintf(b, sizeof(b), "+%.1f health per second", v);
    else if (key == "stamina_regen") snprintf(b, sizeof(b), "+%.1f stamina per second", v);
    else snprintf(b, sizeof(b), "%s %+.2f", key.c_str(), v);
    return b;
}

static std::string Signed(int v) { return (v >= 0 ? "+" : "") + std::to_string(v); }

static std::string Fmt1(float v) {
    char b[32];
    snprintf(b, sizeof(b), "%.1f", v);
    return b;
}

// ============================================================================
// Primitives
// ============================================================================
float GameEngine::U() const {
    float u = std::min(GetScreenWidth() / 1280.0f, GetScreenHeight() / 720.0f) * content_.graphics.ui_scale;
    return std::max(0.4f, u);
}
Font GameEngine::UiFont() const { return const_cast<ResourceManager&>(res_).GetFont("assets/fonts/uncounted_serif.ttf", 48); }
Font GameEngine::MonoFont() const { return const_cast<ResourceManager&>(res_).GetFont("assets/fonts/uncounted_mono.ttf", 32); }

void GameEngine::Text(const std::string& s, float x, float y, float size, Color c) const {
    float u = U();
    DrawTextEx(UiFont(), s.c_str(), {std::round(x * u), std::round(y * u)}, size * u, size * u * 0.04f, c);
}

float GameEngine::TextWidth(const std::string& s, float size) const {
    float u = U();
    return MeasureTextEx(UiFont(), s.c_str(), size * u, size * u * 0.04f).x / u;
}

float GameEngine::TextWrapped(const std::string& s, Rectangle r, float size, Color c, bool draw) const {
    float lineH = size * 1.28f;
    float y = r.y;
    std::string line;
    auto flush = [&]() {
        if (draw && y + lineH > r.y - lineH && y < r.y + r.height + 2000) Text(line, r.x, y, size, c);
        y += lineH;
        line.clear();
    };
    size_t i = 0;
    while (i <= s.size()) {
        size_t nl = s.find('\n', i);
        std::string para = s.substr(i, nl == std::string::npos ? std::string::npos : nl - i);
        size_t p = 0;
        if (para.empty()) flush();
        while (p < para.size()) {
            size_t sp = para.find(' ', p);
            std::string word = para.substr(p, sp == std::string::npos ? std::string::npos : sp - p);
            std::string test = line.empty() ? word : line + " " + word;
            if (TextWidth(test, size) > r.width && !line.empty()) {
                flush();
                line = word;
            } else {
                line = test;
            }
            if (sp == std::string::npos) break;
            p = sp + 1;
        }
        if (!line.empty()) flush();
        if (nl == std::string::npos) break;
        i = nl + 1;
    }
    return y - r.y;
}

void GameEngine::Panel(Rectangle r, Color fill) const {
    float u = U();
    Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
    DrawRectangleRec(s, fill);
    DrawRectangleLinesEx(s, std::max(1.0f, 2.0f * u), kPanelEdge);
    DrawRectangleLinesEx({s.x + 4 * u, s.y + 4 * u, s.width - 8 * u, s.height - 8 * u}, std::max(1.0f, u), Color{70, 58, 42, 200});
}

bool GameEngine::Button(Rectangle r, const std::string& label, bool enabled, float size) {
    float u = U();
    Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
    bool hover = enabled && CheckCollisionPointRec(GetMousePosition(), s);
    Color fill = !enabled ? Color{30, 28, 30, 220} : hover ? Color{74, 60, 40, 240} : Color{36, 32, 34, 235};
    DrawRectangleRec(s, fill);
    DrawRectangleLinesEx(s, std::max(1.0f, 1.5f * u), hover ? kGold : kPanelEdge);
    float tw = TextWidth(label, size);
    Text(label, r.x + (r.width - tw) * 0.5f, r.y + (r.height - size) * 0.5f, size, enabled ? (hover ? kGold : kText) : kDim);
    return hover && IsMouseButtonPressed(MOUSE_BUTTON_LEFT);
}

void GameEngine::Bar(Rectangle r, float frac, Color fill, const std::string& label) const {
    float u = U();
    Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
    DrawRectangleRec(s, Color{10, 10, 12, 210});
    DrawRectangleRec({s.x + 2 * u, s.y + 2 * u, (s.width - 4 * u) * Clamp(frac, 0.0f, 1.0f), s.height - 4 * u}, fill);
    DrawRectangleLinesEx(s, std::max(1.0f, u), Color{90, 78, 60, 255});
    if (!label.empty()) Text(label, r.x + 6, r.y + (r.height - 14) * 0.5f - 1, 14, Color{240, 236, 228, 230});
}

void GameEngine::Icon(const std::string& path, Rectangle r, Color tint) {
    if (path.empty()) return;
    float u = U();
    Texture2D t = res_.GetTexture(path);
    DrawTexturePro(t, {0, 0, static_cast<float>(t.width), static_cast<float>(t.height)}, {r.x * u, r.y * u, r.width * u, r.height * u}, {0, 0}, 0, tint);
}

// ============================================================================
// Render view
// ============================================================================
void GameEngine::BuildRenderView(RenderView& view) {
    const ControlsConfig& cc = content_.controls;
    float hspeed = sqrtf(player_.vel.x * player_.vel.x + player_.vel.z * player_.vel.z);
    float bobAmt = (cc.head_bob && player_.on_ground) ? cc.head_bob_amount * std::min(1.0f, hspeed / 4.0f) : 0.0f;
    float bobY = sinf(bob_phase_ * 2.0f) * bobAmt;
    Vector3 eye = {player_.pos.x, player_.pos.y + player_.eye_height + bobY, player_.pos.z};
    Vector3 dir = {sinf(player_.yaw) * cosf(player_.pitch), sinf(player_.pitch), cosf(player_.yaw) * cosf(player_.pitch)};
    view.camera.position = eye;
    view.camera.target = Vector3Add(eye, dir);
    view.camera.up = {0, 1, 0};
    view.camera.fovy = Clamp(content_.graphics.fov_degrees * 0.8f, 40.0f, 100.0f);
    view.camera.projection = CAMERA_PERSPECTIVE;
    view.time = time_;

    std::vector<SceneLight> lights = scene_.static_lights;
    for (size_t i = 0; i < lights.size(); i++) {
        // Warm lights are flames: give them a gentle, per-light flicker.
        SceneLight& l = lights[i];
        if (l.color.x > l.color.z) {
            float f = 1.0f + 0.06f * sinf(time_ * 9.0f + i * 1.7f) + 0.04f * sinf(time_ * 23.0f + i * 3.1f);
            l.color = Vector3Scale(l.color, f);
            l.radius *= 0.98f + 0.02f * f;
        }
    }
    for (const auto& p : scene_.projectiles)
        if (p.alive && p.light_radius > 0) lights.push_back({p.pos, p.light_color, p.light_radius});
    for (const auto& b : player_.buffs)
        if (b.primitive == "buff_light") lights.push_back({{eye.x, eye.y + 0.3f, eye.z}, b.light_color, b.light_radius});
    if (cast_flash_ > 0.05f) lights.push_back({Vector3Add(eye, Vector3Scale(dir, 0.6f)), Vector3Scale(cast_color_, cast_flash_), 4.0f});
    std::sort(lights.begin(), lights.end(), [&](const SceneLight& a, const SceneLight& b) {
        return Vector3Distance(eye, a.pos) - a.radius < Vector3Distance(eye, b.pos) - b.radius;
    });
    if (lights.size() > WorldRenderer::kMaxLights) lights.resize(WorldRenderer::kMaxLights);
    view.lights = lights;

    view.atmo = atmo_;
    Vector3 lp = view.light_at_player = scene_.map ? Vector3Add(atmo_.ambient, Vector3Scale(atmo_.sun_color, 0.4f)) : Vector3{0.6f, 0.6f, 0.6f};
    for (const auto& l : lights) {
        float d = Vector3Distance(l.pos, eye);
        if (d < l.radius) {
            float a = 1.0f - d / l.radius;
            lp = Vector3Add(lp, Vector3Scale(l.color, a * a * 1.3f));
        }
    }
    view.light_at_player = {std::min(lp.x, 1.5f), std::min(lp.y, 1.5f), std::min(lp.z, 1.5f)};

    ViewModelState& vm = view.vm;
    const ItemDef* main = Equipped("main_hand");
    const ItemDef* off = Equipped("off_hand");
    if (main) vm.main_model = main->world_model;
    if (off) vm.off_model = off->world_model;
    vm.ranged = main && main->weapon.kind == "ranged";
    if (vm.ranged && main) {
        if (const ItemDef* a = content_.GetItem(main->weapon.ammo_item)) vm.ammo_model = a->world_model;
    }
    vm.swing = attack_timer_ >= 0 ? attack_timer_ / std::max(0.01f, attack_duration_) : -1.0f;
    vm.heavy = attack_heavy_;
    vm.charge = charging_ && charge_time_ > 0.12f ? std::min(1.0f, (charge_time_ - 0.12f) / 0.25f) : 0.0f;
    vm.draw = bow_draw_;
    vm.block = block_amount_;
    vm.bob_x = cosf(bob_phase_) * bobAmt * 0.8f;
    vm.bob_y = fabsf(sinf(bob_phase_)) * bobAmt * 0.8f;
    vm.cast_flash = cast_flash_;
    vm.cast_color = cast_color_;
    vm.cast_sprite = cast_sprite_;
    view.show_viewmodel = screen_ == Screen::Playing;
}

// ============================================================================
// Frame
// ============================================================================
void GameEngine::DrawFrame() {
    BeginDrawing();
    ClearBackground(BLACK);

    bool world = (screen_ == Screen::Playing || screen_ == Screen::Dead || screen_ == Screen::Ending) && scene_.map;
    if (world) {
        RenderView view;
        BuildRenderView(view);
        renderer_.Render(scene_, view, scene_.map);
        renderer_.BlitToScreen();
    }

    if (screen_ == Screen::Title) {
        if (overlay_ == Overlay::Options) DrawOptions(); else DrawTitle();
    } else if (screen_ == Screen::Creation) {
        DrawCreation();
    } else if (screen_ == Screen::Playing) {
        if (overlay_ != Overlay::Map && overlay_ != Overlay::Options && overlay_ != Overlay::Dialogue && overlay_ != Overlay::Narration) DrawHud();
        if (overlay_ == Overlay::None) DrawSubtitle();
        if (overlay_ != Overlay::None && overlay_ != Overlay::Dialogue)
            DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Color{0, 0, 0, 110});
        switch (overlay_) {
            case Overlay::Pause: DrawPause(); break;
            case Overlay::Inventory: DrawInventory(); break;
            case Overlay::Character: DrawCharacter(); break;
            case Overlay::Journal: DrawJournal(); break;
            case Overlay::Map: DrawMapOverlay(); break;
            case Overlay::Dialogue: DrawDialogue(); break;
            case Overlay::Shop: DrawShop(); break;
            case Overlay::Container: DrawContainer(); break;
            case Overlay::Reader: DrawReader(); break;
            case Overlay::Options: DrawOptions(); break;
            case Overlay::Narration: DrawNarration(); break;
            case Overlay::None: break;
        }
    } else if (screen_ == Screen::Dead) {
        DrawDead();
    } else if (screen_ == Screen::Ending) {
        DrawEnding();
    }

    DrawToasts();
    if (debug_overlay_) DrawDebug();
    EndDrawing();
}

// ============================================================================
// HUD
// ============================================================================
void GameEngine::DrawHud() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;

    // Sanity: a slow violet pulse at the edges of vision below 60
    if (player_.sanity < 60.0f) {
        float k = (60.0f - player_.sanity) / 60.0f;
        float pulse = 0.6f + 0.4f * sinf(time_ * (1.5f + k * 3.0f));
        unsigned char a = static_cast<unsigned char>(Clamp(k * pulse * 150.0f, 0.0f, 150.0f));
        int w = GetScreenWidth(), h = GetScreenHeight(), e = static_cast<int>(h * (0.12f + 0.15f * k));
        DrawRectangleGradientV(0, 0, w, e, Color{70, 20, 110, a}, Color{70, 20, 110, 0});
        DrawRectangleGradientV(0, h - e, w, e, Color{70, 20, 110, 0}, Color{70, 20, 110, a});
        DrawRectangleGradientH(0, 0, e, h, Color{70, 20, 110, a}, Color{70, 20, 110, 0});
        DrawRectangleGradientH(w - e, 0, e, h, Color{70, 20, 110, 0}, Color{70, 20, 110, a});
    }
    // Damage vignette
    if (damage_flash_ > 0.01f || player_.health < MaxHealth() * 0.25f) {
        float a = damage_flash_ * 0.55f;
        if (player_.health < MaxHealth() * 0.25f) a = std::max(a, 0.18f + 0.1f * sinf(time_ * 5.0f));
        Color c = {140, 0, 0, static_cast<unsigned char>(Clamp(a, 0.0f, 1.0f) * 255)};
        int w = GetScreenWidth(), h = GetScreenHeight();
        int edge = static_cast<int>(120 * u);
        DrawRectangleGradientH(0, 0, edge, h, c, BLANK);
        DrawRectangleGradientH(w - edge, 0, edge, h, BLANK, c);
        DrawRectangleGradientV(0, 0, w, edge, c, BLANK);
        DrawRectangleGradientV(0, h - edge, w, edge, BLANK, c);
    }

    if (overlay_ == Overlay::None) {
        Texture2D ch = res_.GetTexture("assets/ui/panels/crosshair.png");
        float cs = 24.0f;
        Icon("assets/ui/panels/crosshair.png", {VW * 0.5f - cs * 0.5f, VH * 0.5f - cs * 0.5f, cs, cs}, Color{255, 255, 255, 200});
        (void)ch;
        if (!interact_.prompt.empty()) {
            std::string p = "[" + BindingLabel("interact") + "] " + interact_.prompt;
            float tw = TextWidth(p, 20);
            float u2 = U();
            DrawRectangle(static_cast<int>((VW * 0.5f - tw * 0.5f - 10) * u2), static_cast<int>((VH * 0.5f + 30) * u2),
                          static_cast<int>((tw + 20) * u2), static_cast<int>(30 * u2), Color{0, 0, 0, 150});
            Text(p, VW * 0.5f - tw * 0.5f, VH * 0.5f + 34, 20, kGold);
        }
    }

    // Vitals
    float bx = 20, by = VH - 92;
    Bar({bx, by, 250, 22}, player_.health / MaxHealth(), Color{176, 40, 40, 255}, "Health " + std::to_string(static_cast<int>(std::ceil(player_.health))) + "/" + std::to_string(MaxHealth()));
    Bar({bx, by + 26, 250, 22}, player_.stamina / std::max(1, MaxStamina()), Color{70, 150, 60, 255}, "Stamina " + std::to_string(static_cast<int>(player_.stamina)));
    Bar({bx, by + 52, 250, 22}, MaxMana() > 0 ? player_.mana / MaxMana() : 0.0f, Color{50, 90, 190, 255}, "Mana " + std::to_string(static_cast<int>(player_.mana)) + "/" + std::to_string(MaxMana()));
    if (player_.sanity < 99.5f || sanity_drain_now_ > 0.0f) {
        Bar({bx, by + 78, 250, 10}, player_.sanity / 100.0f, Color{140, 80, 200, 255}, "");
        Text(player_.sanity < 30.0f ? "S A N I T Y" : "Sanity", bx + 256, by + 75, 13, Color{190, 150, 240, 255});
    }
    float xpFrac = static_cast<float>(player_.xp) / (100.0f * player_.level);
    Bar({bx, by - 14, 250, 8}, xpFrac, Color{200, 170, 90, 255}, "");
    Text("Lv " + std::to_string(player_.level) + (player_.unspent_points > 0 ? "  (+" + std::to_string(player_.unspent_points) + " pt)" : ""), bx, by - 34, 16, kGold);

    // Quick slots
    float qx = VW * 0.5f - 2 * 58, qy = VH - 70;
    for (int i = 0; i < 4; i++) {
        Rectangle r = {qx + i * 58, qy, 52, 52};
        Panel(r, Color{12, 12, 16, 200});
        const std::string& id = player_.quick_slots[i];
        if (const ItemDef* d = content_.GetItem(id)) {
            int n = CountItem(id);
            Icon(d->icon, {r.x + 10, r.y + 8, 32, 32}, n > 0 ? WHITE : Color{255, 255, 255, 70});
            Text(std::to_string(n), r.x + 36, r.y + 34, 14, n > 0 ? kText : kDim);
        }
        Text(std::to_string(i + 1), r.x + 5, r.y + 3, 13, kDim);
    }

    // Weapon & spell
    float rx = VW - 290;
    const ItemDef* w = Equipped("main_hand");
    Panel({rx, VH - 132, 270, 56}, Color{12, 12, 16, 200});
    if (w) {
        Icon(w->icon, {rx + 10, VH - 124, 40, 40});
        Text(content_.Tr(w->name_key), rx + 58, VH - 124, 17, kText);
        if (w->weapon.kind == "ranged" && !w->weapon.ammo_item.empty())
            Text("Arrows: " + std::to_string(CountItem(w->weapon.ammo_item)), rx + 58, VH - 103, 15, kDim);
        else
            Text("Hold " + BindingLabel("attack") + " for heavy", rx + 58, VH - 103, 14, kDim);
    } else {
        Text("Bare hands", rx + 58, VH - 118, 17, kDim);
    }
    Panel({rx, VH - 70, 270, 56}, Color{12, 12, 16, 200});
    if (!player_.known_spells.empty()) {
        int idx = std::clamp(player_.selected_spell, 0, static_cast<int>(player_.known_spells.size()) - 1);
        if (const SpellDef* s = content_.GetSpell(player_.known_spells[idx])) {
            bool affordable = player_.mana >= s->mana_cost * (1.0f - std::min(0.3f, SkillEffect(s->skill) * 0.4f));
            Icon(s->icon, {rx + 10, VH - 62, 40, 40}, affordable ? WHITE : Color{255, 255, 255, 90});
            if (spell_cooldown_ > 0) {
                float f = spell_cooldown_ / std::max(0.01f, s->cooldown_seconds);
                DrawRectangle(static_cast<int>((rx + 10) * u), static_cast<int>((VH - 62) * u), static_cast<int>(40 * u), static_cast<int>(40 * f * u), Color{0, 0, 0, 150});
            }
            Text(content_.Tr(s->name_key), rx + 58, VH - 62, 17, affordable ? kText : kDim);
            Text("[" + BindingLabel("cast_spell") + "] cast  " + std::to_string(s->mana_cost) + " mana  [" + BindingLabel("cycle_spell") + "] next", rx + 58, VH - 41, 13, kDim);
        }
    } else {
        Text("No spells known", rx + 58, VH - 56, 16, kDim);
    }

    // Quest objectives: the main quest, then any unfinished side quests (over a soft backdrop for legibility).
    float questY = 16;
    for (int pass = 0; pass < 2; pass++) {
        bool draw = pass == 1;
        if (draw && questY > 16) {
            int w = static_cast<int>(470 * u), h = static_cast<int>((questY + 8) * u);
            DrawRectangleGradientH(0, 0, w, h, Color{0, 0, 0, 120}, Color{0, 0, 0, 0});
        }
        questY = 16;
        for (const auto& qid : QuestOrder()) {
            const QuestDef* q = content_.GetQuest(qid);
            if (!q) continue;
            int stage = player_.quest_stages.at(qid);
            for (const auto& st : q->stages) {
                if (st.stage != stage) continue;
                bool main = qid == content_.game_cfg.starting_quest;
                if (!main && st.completed) break;
                if (!main && qid != player_.tracked_quest) break;  // only the tracked side quest; the rest live in the journal
                if (draw) Text(content_.Tr(q->title_key), 20, questY, main ? 18 : 15, main ? kGold : Color{214, 190, 140, 255});
                questY += main ? 22 : 18;
                questY += TextWrapped(content_.Tr(st.objective_key), {20, questY, 420, 80}, main ? 15 : 13,
                                      main ? kText : Color{190, 184, 170, 255}, draw) + 6;
            }
        }
    }

    float bfy = std::max(92.0f, questY + 4);
    for (const auto& b : player_.buffs) {
        std::string icon, name;
        if (const SpellDef* s = content_.GetSpell(b.spell_id)) { icon = s->icon; name = content_.Tr(s->name_key); }
        else if (const ItemDef* it = content_.GetItem(b.item_id)) { icon = it->icon; name = BonusLabel(b.bonus_key, b.bonus_value); }
        else continue;
        Icon(icon, {20, bfy, 24, 24});
        Text(name + "  " + std::to_string(static_cast<int>(std::ceil(b.remaining))) + "s", 50, bfy + 4, 14, kText);
        bfy += 28;
    }

    // Stealth indicator
    if (player_.crouching) {
        bool detected = false;
        for (const auto& c : scene_.creatures)
            if (c.state != CreatureState::Dead && c.alerted && Vector3Distance(c.pos, player_.pos) < c.def->sight_meters * 1.5f) detected = true;
        std::string s = detected ? "DETECTED" : "HIDDEN";
        Text(s, VW * 0.5f - TextWidth(s, 16) * 0.5f, VH * 0.5f - 46, 16, detected ? Color{255, 120, 100, 230} : Color{170, 200, 255, 200});
    }

    // Target enemy
    if (target_enemy_time_ > 0) {
        for (const auto& c : scene_.creatures) {
            if (c.instance_id != target_enemy_ || c.state == CreatureState::Dead) continue;
            std::string name = content_.Tr(c.def->name_key);
            Text(name, VW * 0.5f - TextWidth(name, 17) * 0.5f, 18, 17, kText);
            Bar({VW * 0.5f - 160, 40, 320, 12}, static_cast<float>(c.health) / c.max_health, Color{170, 40, 40, 255}, "");
        }
    }

    // Region banner
    if (region_banner_time_ > 0 && !region_banner_.empty()) {
        float a = Clamp(std::min(region_banner_time_, 4.0f - region_banner_time_) * 1.5f, 0.0f, 1.0f);
        Color c = {kGold.r, kGold.g, kGold.b, static_cast<unsigned char>(a * 255)};
        float tw = TextWidth(region_banner_, 38);
        Text(region_banner_, VW * 0.5f - tw * 0.5f, VH * 0.22f, 38, c);
    }

    // Charge / draw meter
    if (bow_draw_ > 0 || (charging_ && charge_time_ > 0.12f)) {
        float f = bow_draw_ > 0 ? bow_draw_ : std::min(1.0f, charge_time_ / 0.35f);
        Bar({VW * 0.5f - 40, VH * 0.5f + 18, 80, 6}, f, f >= 1.0f ? kGold : Color{200, 200, 200, 255}, "");
    }
    DrawCompass();
}

void GameEngine::DrawCompass() {
    Vector3 obj;
    std::string title;
    if (!ObjectiveMarker(obj, title)) return;
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    float cx = VW * 0.5f, y = VH - 104.0f, half = 170.0f;
    DrawRectangle(static_cast<int>((cx - half) * u), static_cast<int>(y * u), static_cast<int>(half * 2 * u), static_cast<int>(2 * u), Color{226, 196, 128, 90});
    for (int k = -2; k <= 2; k++)
        DrawRectangle(static_cast<int>((cx + k * half * 0.5f) * u), static_cast<int>((y - 3) * u), static_cast<int>(1 * u), static_cast<int>(8 * u), Color{226, 196, 128, 90});
    float want = atan2f(obj.x - player_.pos.x, obj.z - player_.pos.z);
    float rel = want - player_.yaw;
    while (rel > PI) rel -= 2 * PI;
    while (rel < -PI) rel += 2 * PI;
    // yaw grows to the left of the screen in this engine (forward = sin, cos), so screen x runs against the angle
    float x = cx - Clamp(rel / (PI * 0.5f), -1.0f, 1.0f) * half;
    bool edge = fabsf(rel) > PI * 0.5f;
    Color c = edge ? Color{255, 150, 60, 150} : Color{255, 160, 70, 255};
    DrawPoly({x * u, (y + 1) * u}, 4, 7 * u, 45.0f, c);
    float dist = sqrtf((obj.x - player_.pos.x) * (obj.x - player_.pos.x) + (obj.z - player_.pos.z) * (obj.z - player_.pos.z));
    std::string lbl = std::to_string(static_cast<int>(dist)) + " m";
    if (player_.sanity < 30.0f) {  // the mind stops trusting numbers
        static const char* odd[] = {"?? m", "it is close", "too many m", "behind you", "count again"};
        lbl = odd[static_cast<int>(time_ * 0.7f) % 5];
        x += sinf(time_ * 3.1f) * 30.0f * (30.0f - player_.sanity) / 30.0f;
    }
    if (obj.y > player_.pos.y + 2.0f) lbl += "  (up)";
    else if (obj.y < player_.pos.y - 2.0f) lbl += "  (down)";
    Text(lbl, x - TextWidth(lbl, 13) * 0.5f, y + 9, 13, Color{255, 200, 140, 230});
}

void GameEngine::DrawToasts() {
    float u = U();
    float VW = GetScreenWidth() / u;
    float y = 120;
    for (const auto& t : toasts_) {
        float a = Clamp(t.time, 0.0f, 1.0f);
        Color c = {t.color.r, t.color.g, t.color.b, static_cast<unsigned char>(a * 255)};
        float tw = TextWidth(t.text, 17);
        DrawRectangle(static_cast<int>((VW - tw - 34) * u), static_cast<int>((y - 3) * u), static_cast<int>((tw + 20) * u), static_cast<int>(26 * u),
                      Color{0, 0, 0, static_cast<unsigned char>(a * 140)});
        Text(t.text, VW - tw - 24, y, 17, c);
        y += 30;
    }
}

// ============================================================================
// Title & creation
// ============================================================================
void GameEngine::DrawTitle() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Texture2D bg = res_.GetTexture("assets/ui/panels/title_bg.png");
    float s = std::max(GetScreenWidth() / static_cast<float>(bg.width), GetScreenHeight() / static_cast<float>(bg.height));
    float drift = sinf(time_ * 0.05f) * 20.0f;
    DrawTexturePro(bg, {0, 0, static_cast<float>(bg.width), static_cast<float>(bg.height)},
                   {GetScreenWidth() * 0.5f + drift, GetScreenHeight() * 0.5f, bg.width * s * 1.06f, bg.height * s * 1.06f},
                   {bg.width * s * 0.53f, bg.height * s * 0.53f}, 0, WHITE);
    DrawRectangleGradientV(0, 0, GetScreenWidth(), GetScreenHeight(), Color{0, 0, 0, 60}, Color{0, 0, 0, 200});

    std::string title = content_.Tr("game.title");
    Text(title, VW * 0.5f - TextWidth(title, 76) * 0.5f, VH * 0.14f, 76, kGold);
    std::string sub = content_.Tr("game.subtitle");
    Text(sub, VW * 0.5f - TextWidth(sub, 28) * 0.5f, VH * 0.14f + 88, 28, kText);
    std::string quote = content_.Tr("game.quote");
    Text(quote, VW * 0.5f - TextWidth(quote, 17) * 0.5f, VH * 0.14f + 130, 17, kDim);

    std::string latest;
    {
        std::error_code ec;
        fs::file_time_type best{};
        for (const char* slot : {"slot_1", "autosave"}) {
            if (!SaveExists(slot)) continue;
            auto t = fs::last_write_time(SavePath(slot), ec);
            if (latest.empty() || t > best) { best = t; latest = slot; }
        }
    }
    float bw = 300, bh = 46, x = VW * 0.5f - bw * 0.5f, y = VH * 0.48f;
    if (Button({x, y, bw, bh}, "Continue", !latest.empty())) { LoadGame(latest); return; }
    if (Button({x, y + 56, bw, bh}, "New Game")) { screen_ = Screen::Creation; return; }
    if (Button({x, y + 112, bw, bh}, "Load Quick Save", SaveExists("slot_1"))) { LoadGame("slot_1"); return; }
    if (Button({x, y + 168, bw, bh}, "Options")) { options_from_title_ = true; overlay_ = Overlay::Options; return; }
    if (Button({x, y + 224, bw, bh}, "Quit")) { running_ = false; return; }

    std::string ded = content_.Tr("game.dedication");
    if (ded != "game.dedication") Text(ded, VW * 0.5f - TextWidth(ded, 16) * 0.5f, VH - 58, 16, Color{214, 186, 120, 220});
    Text(validation_summary_, 16, VH - 28, 14, validation_summary_.find("passed") != std::string::npos ? Color{130, 190, 130, 255} : Color{230, 120, 100, 255});
    std::string packs;
    for (const auto& p : content_.loaded_packs) packs += (packs.empty() ? "" : " + ") + p;
    Text(packs, VW - TextWidth(packs, 13) - 16, VH - 26, 13, kDim);
}

void GameEngine::DrawCreation() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    DrawRectangleGradientV(0, 0, GetScreenWidth(), GetScreenHeight(), Color{14, 16, 24, 255}, Color{6, 6, 10, 255});
    Text("Who were you, before they counted you dead?", VW * 0.5f - TextWidth("Who were you, before they counted you dead?", 30) * 0.5f, 24, 30, kGold);

    // Name entry
    int key = GetCharPressed();
    while (key > 0) {
        if (key >= 32 && key < 127 && creation_name_.size() < 20) creation_name_ += static_cast<char>(key);
        key = GetCharPressed();
    }
    if (IsKeyPressed(KEY_BACKSPACE) && !creation_name_.empty()) creation_name_.pop_back();
    float ox = VW * 0.5f - 600;
    Text("Name:", ox, 76, 20, kDim);
    Panel({ox + 70, 70, 300, 34}, Color{10, 10, 14, 240});
    Text(creation_name_ + ((static_cast<int>(time_ * 2) % 2) ? "_" : ""), ox + 82, 76, 20, kText);

    auto column = [&](float x, const char* title, int count, int& sel, auto nameOf) {
        Text(title, x, 122, 22, kGold);
        for (int i = 0; i < count; i++) {
            Rectangle r = {x, 152.0f + i * 42, 280, 36};
            bool selected = i == sel;
            float uu = U();
            if (selected) DrawRectangleRec({r.x * uu, r.y * uu, r.width * uu, r.height * uu}, Color{70, 56, 36, 230});
            if (Button(r, nameOf(i), true, 19)) sel = i;
            if (selected) DrawRectangleLinesEx({r.x * uu, r.y * uu, r.width * uu, r.height * uu}, 2 * uu, kGold);
        }
    };
    int nr = static_cast<int>(content_.races.size()), nb = static_cast<int>(content_.backgrounds.size()), na = static_cast<int>(content_.archetypes.size());
    if (nr == 0 || nb == 0 || na == 0) { Text("Content missing races/backgrounds/archetypes.", ox, 200, 20, RED); return; }
    creation_race_ = std::clamp(creation_race_, 0, nr - 1);
    creation_bg_ = std::clamp(creation_bg_, 0, nb - 1);
    creation_arch_ = std::clamp(creation_arch_, 0, na - 1);
    column(ox, "Race", nr, creation_race_, [&](int i) { return content_.Tr(content_.races[i].name_key); });
    column(ox + 300, "Background", nb, creation_bg_, [&](int i) { return content_.Tr(content_.backgrounds[i].name_key); });
    column(ox + 600, "Calling", na, creation_arch_, [&](int i) { return content_.Tr(content_.archetypes[i].name_key); });

    const RaceDef& r = content_.races[creation_race_];
    const BackgroundDef& b = content_.backgrounds[creation_bg_];
    const ArchetypeDef& a = content_.archetypes[creation_arch_];

    // Portrait & descriptions
    float dx = ox + 900;
    Panel({dx, 116, 300, 300});
    Icon(r.portrait, {dx + 20, 130, 96, 96});
    Text(content_.Tr(r.name_key), dx + 130, 140, 24, kGold);
    TextWrapped(content_.Tr(r.trait_key), {dx + 130, 172, 160, 60}, 13, kAccent);
    TextWrapped(content_.Tr(r.description_key), {dx + 18, 238, 266, 170}, 14, kText);

    Panel({ox, 410, 580, 200});
    Text(content_.Tr(b.name_key), ox + 16, 420, 20, kGold);
    float h = TextWrapped(content_.Tr(b.description_key), {ox + 16, 446, 548, 60}, 14, kText);
    Text(content_.Tr(a.name_key), ox + 16, 452 + h, 20, kGold);
    TextWrapped(content_.Tr(a.description_key), {ox + 16, 478 + h, 548, 80}, 14, kText);

    // Resulting stats preview
    std::map<std::string, int> attrs;
    for (const auto& at : content_.attributes) attrs[at.id] = at.base;
    for (auto& [k, v] : r.attribute_modifiers) attrs[k] += v;
    for (auto& [k, v] : a.attribute_bonuses) attrs[k] += v;
    std::map<std::string, int> skills;
    for (const auto& s : content_.skills) skills[s.id] = 5;
    for (auto& [k, v] : r.skill_bonuses) skills[k] += v;
    for (auto& [k, v] : b.skill_bonuses) skills[k] += v;
    for (auto& [k, v] : a.skill_bonuses) skills[k] += v;
    Panel({ox + 600, 410, 600, 200});
    float yy = 422;
    for (const auto& at : content_.attributes) {
        Text(content_.Tr(at.name_key), ox + 616, yy, 16, kText);
        Text(std::to_string(attrs[at.id]), ox + 740, yy, 16, attrs[at.id] > at.base ? kGold : kText);
        yy += 22;
    }
    std::vector<std::pair<int, std::string>> top;
    for (auto& [k, v] : skills) top.push_back({v, k});
    std::sort(top.rbegin(), top.rend());
    yy = 422;
    for (size_t i = 0; i < top.size() && i < 8; i++) {
        std::string nm = top[i].second;
        for (const auto& s : content_.skills) if (s.id == nm) nm = content_.Tr(s.name_key);
        Text(nm, ox + 800, yy, 15, kText);
        Text(std::to_string(top[i].first), ox + 960, yy, 15, top[i].first > 5 ? kGold : kText);
        yy += 21;
    }
    std::string kit;
    for (const auto& e : a.starting_equipment) if (const ItemDef* d = content_.GetItem(e)) kit += (kit.empty() ? "" : ", ") + content_.Tr(d->name_key);
    std::string sp;
    for (const auto& e : a.starting_spells) if (const SpellDef* d = content_.GetSpell(e)) sp += (sp.empty() ? "" : ", ") + content_.Tr(d->name_key);
    TextWrapped("Kit: " + kit, {ox + 1000, 422, 190, 90}, 13, kDim);
    TextWrapped("Spells: " + sp, {ox + 1000, 520, 190, 80}, 13, kDim);

    if (Button({VW * 0.5f - 320, VH - 80, 300, 50}, "Back")) { screen_ = Screen::Title; return; }
    if (Button({VW * 0.5f + 20, VH - 80, 300, 50}, "Begin Chapter Zero")) { NewGame(); return; }
}

// ============================================================================
// Pause & options
// ============================================================================
void GameEngine::DrawPause() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Panel({VW * 0.5f - 200, VH * 0.5f - 250, 400, 500});
    Text("Paused", VW * 0.5f - TextWidth("Paused", 34) * 0.5f, VH * 0.5f - 232, 34, kGold);
    float x = VW * 0.5f - 150, y = VH * 0.5f - 175, bw = 300, bh = 42, g = 50;
    if (Button({x, y, bw, bh}, "Resume")) SetOverlay(Overlay::None);
    if (Button({x, y + g, bw, bh}, "Save Game")) { if (SaveGame("slot_1")) Toast("Game saved"); SetOverlay(Overlay::None); }
    if (Button({x, y + g * 2, bw, bh}, "Load Quick Save", SaveExists("slot_1"))) { LoadGame("slot_1"); return; }
    if (Button({x, y + g * 3, bw, bh}, "Load Autosave", SaveExists("autosave"))) { LoadGame("autosave"); return; }
    if (Button({x, y + g * 4, bw, bh}, "Options")) { options_from_title_ = false; SetOverlay(Overlay::Options); return; }
    if (Button({x, y + g * 5, bw, bh}, "Quit to Title")) { ReturnToTitle(); return; }
    if (Button({x, y + g * 6, bw, bh}, "Quit Game")) running_ = false;
    std::string help = "WASD move  Shift sprint  Ctrl sneak  Space jump  E interact  LMB attack (hold: heavy)  RMB block  Q cast  R next spell  I/C/J/M menus  F6/F9 quick save/load";
    TextWrapped(help, {VW * 0.5f - 190, y + g * 7 + 4, 380, 80}, 12, kDim);
}

void GameEngine::DrawOptions() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    if (screen_ == Screen::Title) DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Color{8, 8, 12, 255});
    Panel({VW * 0.5f - 330, VH * 0.5f - 350, 660, 700});
    Text("Options", VW * 0.5f - TextWidth("Options", 32) * 0.5f, VH * 0.5f - 338, 32, kGold);

    GameConfig& gc = content_.game_cfg;
    GraphicsConfig& gfx = content_.graphics;
    ControlsConfig& cc = content_.controls;
    bool changed = false;
    float x = VW * 0.5f - 300, y = VH * 0.5f - 296;
    auto row = [&](const std::string& label, const std::string& value, auto onLeft, auto onRight) {
        Text(label, x, y + 6, 18, kText);
        if (Button({x + 330, y, 40, 32}, "<")) { onLeft(); changed = true; }
        Text(value, x + 380 + (170 - TextWidth(value, 18)) * 0.5f, y + 6, 18, kGold);
        if (Button({x + 560, y, 40, 32}, ">")) { onRight(); changed = true; }
        y += 30;
    };
    auto pct = [](float v) { return std::to_string(static_cast<int>(std::round(v * 100))) + "%"; };
    auto step = [](float& v, float d) { v = Clamp(std::round((v + d) * 100) / 100, 0.0f, 1.0f); };
    row("Master volume", pct(gc.master_volume), [&] { step(gc.master_volume, -0.05f); }, [&] { step(gc.master_volume, 0.05f); });
    row("Music volume", pct(gc.music_volume), [&] { step(gc.music_volume, -0.05f); }, [&] { step(gc.music_volume, 0.05f); });
    row("Ambience volume", pct(gc.ambience_volume), [&] { step(gc.ambience_volume, -0.05f); }, [&] { step(gc.ambience_volume, 0.05f); });
    row("Effects volume", pct(gc.sfx_volume), [&] { step(gc.sfx_volume, -0.05f); }, [&] { step(gc.sfx_volume, 0.05f); });
    row("Mouse sensitivity", Fmt1(cc.mouse_sensitivity * 10), [&] { cc.mouse_sensitivity = std::max(0.02f, cc.mouse_sensitivity - 0.02f); },
        [&] { cc.mouse_sensitivity = std::min(1.0f, cc.mouse_sensitivity + 0.02f); });
    row("Invert mouse Y", cc.invert_y ? "On" : "Off", [&] { cc.invert_y = !cc.invert_y; }, [&] { cc.invert_y = !cc.invert_y; });
    row("Head bob", cc.head_bob ? "On" : "Off", [&] { cc.head_bob = !cc.head_bob; }, [&] { cc.head_bob = !cc.head_bob; });
    row("Field of view", std::to_string(static_cast<int>(gfx.fov_degrees)), [&] { gfx.fov_degrees = std::max(55.0f, gfx.fov_degrees - 5); },
        [&] { gfx.fov_degrees = std::min(110.0f, gfx.fov_degrees + 5); });
    auto cycleRes = [&](int d) {
        auto& list = gfx.available_internal_resolutions;
        if (list.empty()) return;
        auto it = std::find(list.begin(), list.end(), gfx.internal_resolution);
        int i = it == list.end() ? 0 : static_cast<int>(it - list.begin());
        i = (i + d + static_cast<int>(list.size())) % static_cast<int>(list.size());
        gfx.internal_resolution = list[i];
    };
    row("Internal resolution", gfx.internal_resolution, [&] { cycleRes(-1); }, [&] { cycleRes(1); });
    auto toggleFilter = [&] {
        gfx.texture_filter = gfx.texture_filter == "nearest" ? "bilinear" : "nearest";
        res_.SetPointFilter(gfx.texture_filter == "nearest");
        renderer_.RecreateTargets();
    };
    row("Texture filtering", gfx.texture_filter, toggleFilter, toggleFilter);
    row("Fog", gfx.fog_enabled ? "On" : "Off", [&] { gfx.fog_enabled = !gfx.fog_enabled; }, [&] { gfx.fog_enabled = !gfx.fog_enabled; });
    row("Dynamic lights", gfx.dynamic_lights_enabled ? "On" : "Off", [&] { gfx.dynamic_lights_enabled = !gfx.dynamic_lights_enabled; },
        [&] { gfx.dynamic_lights_enabled = !gfx.dynamic_lights_enabled; });
    row("Retro dithering", gfx.retro_dither ? "On" : "Off", [&] { gfx.retro_dither = !gfx.retro_dither; }, [&] { gfx.retro_dither = !gfx.retro_dither; });
    row("Glow", gfx.glow ? "On" : "Off", [&] { gfx.glow = !gfx.glow; }, [&] { gfx.glow = !gfx.glow; });
    auto cycleFx = [&](int d) {
        static const std::vector<std::string> ids = {"off", "crt", "vhs", "fisheye", "film", "handheld"};
        auto it = std::find(ids.begin(), ids.end(), gfx.screen_effect);
        int i = it == ids.end() ? 0 : static_cast<int>(it - ids.begin());
        gfx.screen_effect = ids[(i + d + ids.size()) % ids.size()];
    };
    static const std::map<std::string, std::string> fxName = {{"off", "Off"}, {"crt", "Old TV"}, {"vhs", "VHS tape"},
                                                              {"fisheye", "Fisheye"}, {"film", "Silent film"}, {"handheld", "Handheld"}};
    row("Screen effect", fxName.count(gfx.screen_effect) ? fxName.at(gfx.screen_effect) : "Off", [&] { cycleFx(-1); }, [&] { cycleFx(1); });
    row("Swaying trees & water", gfx.world_motion ? "On" : "Off", [&] { gfx.world_motion = !gfx.world_motion; },
        [&] { gfx.world_motion = !gfx.world_motion; });
    auto cycleDiff = [&](int d) {
        std::vector<std::string> ds = {"story", "standard", "veteran"};
        auto it = std::find(ds.begin(), ds.end(), gc.difficulty);
        int i = it == ds.end() ? 1 : static_cast<int>(it - ds.begin());
        gc.difficulty = ds[(i + d + 3) % 3];
    };
    row("Difficulty", gc.difficulty, [&] { cycleDiff(-1); }, [&] { cycleDiff(1); });
    row("Dialogue text size", pct(gc.text_scale), [&] { gc.text_scale = std::max(1.0f, gc.text_scale - 0.1f); },
        [&] { gc.text_scale = std::min(1.5f, gc.text_scale + 0.1f); });
    row("Enable mods (restart)", gc.enable_mods ? "On" : "Off", [&] { gc.enable_mods = !gc.enable_mods; }, [&] { gc.enable_mods = !gc.enable_mods; });

    if (changed) {
        ApplyAudioVolumes();
        content_.SaveConfigs(".");
    }
    bool back = Button({VW * 0.5f - 120, VH * 0.5f + 296, 240, 44}, "Back") || (screen_ == Screen::Title && IsKeyPressed(KEY_ESCAPE));
    if (back) {
        content_.SaveConfigs(".");
        overlay_ = (screen_ == Screen::Title || options_from_title_) && screen_ != Screen::Playing ? Overlay::None : Overlay::Pause;
    }
}

// ============================================================================
// Inventory
// ============================================================================
void GameEngine::DrawInventory() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Rectangle P = {VW * 0.5f - 560, VH * 0.5f - 310, 1120, 620};
    Panel(P);
    Text("Inventory", P.x + 20, P.y + 14, 30, kGold);
    std::string hdr = "Gold: " + std::to_string(player_.gold) + "     Weight: " + Fmt1(CarriedWeight()) + " / " + Fmt1(CarryCapacity()) +
                      "     Armor: " + std::to_string(ArmorRating());
    Text(hdr, P.x + P.width - TextWidth(hdr, 17) - 24, P.y + 22, 17, CarriedWeight() > CarryCapacity() ? Color{255, 120, 100, 255} : kText);

    const char* tabs[] = {"All", "Weapons", "Apparel", "Consumables", "Books", "Keys & Misc"};
    for (int i = 0; i < 6; i++) {
        if (Button({P.x + 20 + i * 102, P.y + 58, 98, 30}, tabs[i], true, 15)) { inv_filter_ = i; ui_scroll_ = 0; }
        if (i == inv_filter_) DrawRectangle(static_cast<int>((P.x + 20 + i * 102) * u), static_cast<int>((P.y + 86) * u), static_cast<int>(98 * u), static_cast<int>(3 * u), kGold);
    }
    auto matches = [&](const ItemDef& d) {
        switch (inv_filter_) {
            case 1: return d.category == "weapon" || d.category == "ammo";
            case 2: return d.category == "armor" || d.category == "accessory";
            case 3: return d.category == "consumable";
            case 4: return d.category == "book";
            case 5: return d.category == "key" || d.category == "misc";
            default: return true;
        }
    };
    std::vector<std::pair<std::string, int>> rows;
    for (const auto& it : player_.inventory) {
        const ItemDef* d = content_.GetItem(it.id);
        if (!d || !matches(*d)) continue;
        bool merged = false;
        for (auto& r : rows) if (r.first == it.id) { r.second += it.qty; merged = true; }
        if (!merged) rows.push_back({it.id, it.qty});
    }

    Rectangle list = {P.x + 20, P.y + 98, 620, 500};
    float wheel = GetMouseWheelMove();
    if (CheckCollisionPointRec(GetMousePosition(), {list.x * u, list.y * u, list.width * u, list.height * u})) ui_scroll_ -= wheel * 40;
    float maxScroll = std::max(0.0f, rows.size() * 40.0f - list.height);
    ui_scroll_ = Clamp(ui_scroll_, 0.0f, maxScroll);
    BeginScissorMode(static_cast<int>(list.x * u), static_cast<int>(list.y * u), static_cast<int>(list.width * u), static_cast<int>(list.height * u));
    std::string hovered;
    for (size_t i = 0; i < rows.size(); i++) {
        const ItemDef* d = content_.GetItem(rows[i].first);
        Rectangle r = {list.x, list.y + i * 40 - ui_scroll_, list.width - 10, 36};
        Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
        bool hover = !ui_ignore_hover_ && CheckCollisionPointRec(GetMousePosition(), s) && CheckCollisionPointRec(GetMousePosition(), {list.x * u, list.y * u, list.width * u, list.height * u});
        bool sel = inv_selected_ == d->id;
        DrawRectangleRec(s, sel ? Color{70, 56, 36, 220} : hover ? Color{40, 36, 34, 220} : Color{20, 20, 24, 160});
        if (hover) hovered = d->id;
        if (hover && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) inv_selected_ = d->id;
        if (hover && IsMouseButtonPressed(MOUSE_BUTTON_RIGHT)) UseItem(d->id);
        Icon(d->icon, {r.x + 4, r.y + 2, 32, 32});
        std::string name = content_.Tr(d->name_key) + (rows[i].second > 1 ? "  (" + std::to_string(rows[i].second) + ")" : "");
        Text(name, r.x + 44, r.y + 8, 18, IsEquipped(d->id) ? kGold : kText);
        if (IsEquipped(d->id)) Text("equipped", r.x + r.width - 170, r.y + 10, 14, kGold);
        Text(Fmt1(d->weight * rows[i].second) + " wt", r.x + r.width - 80, r.y + 10, 14, kDim);
    }
    EndScissorMode();
    if (rows.empty()) Text("Nothing here.", list.x + 10, list.y + 10, 18, kDim);

    if (!hovered.empty()) {
        const ItemDef* d = content_.GetItem(hovered);
        if (d && d->category == "consumable") {
            for (int k = 0; k < 4; k++) {
                if (IsKeyPressed(KEY_ONE + k)) { player_.quick_slots[k] = hovered; Toast("Assigned to quick slot " + std::to_string(k + 1)); }
            }
        }
    }

    // Detail panel
    Rectangle D = {P.x + 660, P.y + 98, 440, 500};
    Panel(D, Color{18, 18, 24, 230});
    std::string show = inv_selected_.empty() || CountItem(inv_selected_) == 0 ? hovered : inv_selected_;
    if (!hovered.empty()) show = hovered;
    const ItemDef* d = content_.GetItem(show);
    if (!d) {
        TextWrapped("Select an item to inspect it.\n\nRight-click to use or equip.\nHover a consumable and press 1-4 to assign it to a quick slot.", {D.x + 20, D.y + 20, D.width - 40, 200}, 16, kDim);
        return;
    }
    Icon(d->icon, {D.x + 20, D.y + 20, 64, 64});
    Text(content_.Tr(d->name_key), D.x + 100, D.y + 24, 22, kGold);
    Text(d->category + (d->quest_item ? "  (quest item)" : ""), D.x + 100, D.y + 54, 15, kDim);
    float y = D.y + 98;
    y += TextWrapped(content_.Tr(d->description_key), {D.x + 20, y, D.width - 40, 140}, 15, kText) + 10;
    auto stat = [&](const std::string& s) { Text(s, D.x + 20, y, 16, kAccent); y += 22; };
    auto statC = [&](const std::string& s, Color c) { Text(s, D.x + 20, y, 16, c); y += 22; };
    if (d->weapon.is_weapon) {
        const WeaponStatsDef& wp = d->weapon;
        bool ranged = wp.kind == "ranged";
        stat("Damage " + std::to_string(wp.base_damage) + " " + wp.damage_type + "   Skill: " + wp.skill + " (" + std::to_string(SkillLevel(wp.skill)) + ")");
        stat("Speed " + Fmt1(wp.attack_time_seconds) + "s   Reach " + Fmt1(wp.reach_meters) + "m   Stamina " + Fmt1(wp.stamina_cost));
        // What it would do in *your* hands, and how that compares with what you're holding.
        auto expected = [&](const ItemDef* w) {
            if (!w) return MeleeHitDamage(nullptr, false) / 0.45f;
            float cc = CritChance(w), cm = CritMult(w);
            if (w->weapon.kind == "ranged") return ArrowHitDamage(w, 1.0f) * (1.0f + cc * (cm - 1.0f));
            float t = w->weapon.attack_time_seconds * (1.0f - std::min(0.25f, (Attr("agility") - 10) * 0.015f));
            return MeleeHitDamage(w, false) / std::max(0.1f, t) * (1.0f + cc * (cm - 1.0f));
        };
        float mine = expected(d);
        std::string line = (ranged ? "Your arrow: " : "Your DPS: ") + Fmt1(mine);
        const ItemDef* cur = Equipped("main_hand");
        if (cur && cur->id != d->id && (cur->weapon.kind == "ranged") == ranged) {
            float delta = mine - expected(cur);
            line += "  (" + std::string(delta >= 0 ? "+" : "") + Fmt1(delta) + " vs equipped)";
            statC(line, delta >= 0 ? Color{140, 230, 140, 255} : Color{255, 140, 120, 255});
        } else {
            statC(line, kGold);
        }
        if (wp.crit_chance > 0.0f || wp.crit_mult != 1.5f) statC("Critical " + Pct(wp.crit_chance) + " base, x" + Fmt1(wp.crit_mult), kGold);
        if (!wp.bane_family.empty()) statC("Bane: x" + Fmt1(wp.bane_mult) + " vs " + wp.bane_family, kGold);
        if (wp.life_steal > 0.0f) statC("Life steal " + Pct(wp.life_steal), kGold);
        if (wp.mana_on_hit > 0.0f) statC("+" + Fmt1(wp.mana_on_hit) + " mana per hit", kGold);
    }
    if (d->armor > 0) {
        std::string a = "Armor +" + std::to_string(d->armor);
        if (!d->slots.empty() && d->category != "weapon") {
            const ItemDef* cur = Equipped(d->slots[0]);
            if (cur && cur->id != d->id) a += "  (" + Signed(d->armor - cur->armor) + " vs equipped)";
        }
        stat(a);
    }
    for (const auto& e : d->effects) {
        if (e.type == "stat_bonus") statC(e.stat + " " + Signed(e.amount), e.amount >= 0 ? kAccent : Color{255, 140, 120, 255});
        else if (e.type == "bonus") statC(BonusLabel(e.stat, e.value), kGold);
        else if (e.type == "buff") statC(BonusLabel(e.stat, e.value) + " for " + std::to_string(static_cast<int>(e.duration)) + "s", kGold);
        else if (e.type == "consumable_heal") stat("Restores " + std::to_string(e.amount) + " health");
        else if (e.type == "consumable_mana") stat("Restores " + std::to_string(e.amount) + " mana");
        else if (e.type == "consumable_stamina") stat("Restores " + std::to_string(e.amount) + " stamina");
        else if (e.type == "learn_spell") if (const SpellDef* s = content_.GetSpell(e.spell_id)) stat("Teaches: " + content_.Tr(s->name_key));
    }
    if (!d->slots.empty()) stat("Slot: " + d->slots[0]);
    Text("Value " + std::to_string(d->value) + "   Weight " + Fmt1(d->weight), D.x + 20, D.y + D.height - 100, 15, kDim);

    if (show == inv_selected_ && CountItem(show) > 0) {
        std::string label = d->category == "book" ? "Read" : !d->slots.empty() ? (IsEquipped(show) ? "Unequip" : "Equip") : d->category == "consumable" ? "Use" : "";
        if (!label.empty() && Button({D.x + 20, D.y + D.height - 64, 180, 42}, label)) UseItem(show);
        if (d->category == "consumable") {
            for (int k = 0; k < 4; k++)
                if (Button({D.x + 220 + k * 52, D.y + D.height - 64, 46, 42}, std::to_string(k + 1), true, 18)) player_.quick_slots[k] = show;
        }
    }
}

// ============================================================================
// Character sheet
// ============================================================================
void GameEngine::DrawCharacter() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Rectangle P = {VW * 0.5f - 560, VH * 0.5f - 310, 1120, 620};
    Panel(P);
    const RaceDef* race = content_.GetRace(player_.race_id);
    const BackgroundDef* bg = content_.GetBackground(player_.background_id);
    const ArchetypeDef* arch = content_.GetArchetype(player_.archetype_id);
    if (race) Icon(race->portrait, {P.x + 20, P.y + 20, 80, 80});
    Text(player_.name, P.x + 116, P.y + 20, 30, kGold);
    std::string line = (race ? content_.Tr(race->name_key) : "") + "  -  " + (bg ? content_.Tr(bg->name_key) : "") + "  -  " + (arch ? content_.Tr(arch->name_key) : "");
    Text(line, P.x + 116, P.y + 56, 17, kText);
    Text("Level " + std::to_string(player_.level) + "   XP " + std::to_string(player_.xp) + " / " + std::to_string(100 * player_.level), P.x + 116, P.y + 80, 16, kDim);
    if (race) TextWrapped(content_.Tr(race->trait_key), {P.x + 560, P.y + 24, 540, 50}, 14, kAccent);
    const char* tabs[] = {"Overview", "Combat Sheet"};
    for (int i = 0; i < 2; i++) {
        Rectangle t = {P.x + P.width - 360 + i * 172, P.y + 78, 166, 30};
        if (Button(t, tabs[i], true, 15)) char_tab_ = i;
        if (char_tab_ == i) DrawRectangle(static_cast<int>(t.x * u), static_cast<int>((t.y + 28) * u), static_cast<int>(t.width * u), static_cast<int>(3 * u), kGold);
    }
    if (char_tab_ == 1) { DrawCombatSheet(P); return; }

    float y = P.y + 120;
    Text("Attributes", P.x + 20, y, 22, kGold);
    if (player_.unspent_points > 0) Text(std::to_string(player_.unspent_points) + " point(s) to spend", P.x + 160, y + 4, 15, kAccent);
    y += 34;
    for (const auto& a : content_.attributes) {
        Text(content_.Tr(a.name_key), P.x + 24, y + 4, 18, kText);
        int base = player_.attributes[a.id], total = Attr(a.id);
        Text(std::to_string(total) + (total != base ? " (" + std::to_string(base) + ")" : ""), P.x + 170, y + 4, 18, total > base ? kGold : kText);
        if (player_.unspent_points > 0 && Button({P.x + 250, y, 30, 28}, "+", true, 18)) {
            player_.attributes[a.id]++;
            player_.unspent_points--;
        }
        Rectangle tip = {P.x + 20, y, 260, 28};
        if (CheckCollisionPointRec(GetMousePosition(), {tip.x * u, tip.y * u, tip.width * u, tip.height * u}))
            TextWrapped(content_.Tr(a.desc_key), {P.x + 20, P.y + 470, 300, 60}, 13, kDim);
        y += 34;
    }
    y += 10;
    Text("Health " + std::to_string(MaxHealth()) + "   Stamina " + std::to_string(MaxStamina()) + "   Mana " + std::to_string(MaxMana()), P.x + 24, y, 15, kText);
    Text("Armor " + std::to_string(ArmorRating()) + "   Carry " + Fmt1(CarryCapacity()) + "   Speed " + Fmt1(MoveSpeed()) + " m/s", P.x + 24, y + 22, 15, kText);

    // Skills
    float sx = P.x + 340, sy = P.y + 120;
    Text("Skills (improve by use)", sx, sy, 22, kGold);
    sy += 34;
    std::string lastDomain;
    float col = 0;
    int idx = 0;
    for (const auto& s : content_.skills) {
        if (idx == 7) { col = 380; sy = P.y + 154; }
        const SkillState& st = player_.skills[s.id];
        float x = sx + col;
        Text(content_.Tr(s.name_key), x, sy, 17, kText);
        Text(std::to_string(st.level), x + 170, sy, 17, st.level > 5 ? kGold : kText);
        Bar({x + 210, sy + 4, 140, 12}, st.xp / (6.0f + st.level * 0.6f), Color{90, 130, 200, 255}, "");
        Rectangle tip = {x, sy, 350, 24};
        if (CheckCollisionPointRec(GetMousePosition(), {tip.x * u, tip.y * u, tip.width * u, tip.height * u}))
            TextWrapped(content_.Tr(s.desc_key), {sx, P.y + 430, 740, 40}, 13, kDim);
        sy += 36;
        idx++;
    }

    float yy = P.y + 466;
    int activeCount = 0;
    for (const auto& syn : content_.synergies) activeCount += SynergyActive(syn) ? 1 : 0;
    Text("Synergies  " + std::to_string(activeCount) + "/" + std::to_string(content_.synergies.size()) + "  (hover for details)", sx, yy, 20, kGold);
    yy += 30;
    int n = 0;
    std::string hoverDesc;
    for (const auto& syn : content_.synergies) {
        bool on = SynergyActive(syn);
        float x = sx + (n % 2) * 380, ry = yy + (n / 2) * 24;
        std::string req;
        for (const auto& [k, v] : syn.requirements) {
            req += (req.empty() ? "" : " + ") + k + " " + std::to_string(SkillLevel(k)) + "/" + std::to_string(v);
        }
        Text(std::string(on ? "* " : "  ") + content_.Tr(syn.name_key), x, ry, 15, on ? kGold : kDim);
        Rectangle tip = {x, ry, 370, 22};
        if (CheckCollisionPointRec(GetMousePosition(), {tip.x * u, tip.y * u, tip.width * u, tip.height * u})) {
            hoverDesc = content_.Tr(syn.name_key) + (on ? "  (active)" : "  (needs " + req + ")") + "\n" + content_.Tr(syn.description_key) + "\n";
            for (const auto& [k, v] : syn.bonuses) hoverDesc += "  " + BonusLabel(k, v) + "\n";
        }
        n++;
    }
    if (!hoverDesc.empty()) {
        Rectangle box = {P.x + 16, P.y + 536, 316, 78};
        Panel(box, Color{12, 12, 16, 245});
        TextWrapped(hoverDesc, {box.x + 8, box.y + 6, box.width - 16, box.height - 8}, 12, kText);
    }
}

// ============================================================================
// Combat sheet: the numbers behind the build
// ============================================================================
void GameEngine::DrawCombatSheet(Rectangle P) {
    const ItemDef* w = Equipped("main_hand");
    auto row = [&](float x, float& y, const std::string& label, const std::string& value, Color vc = kText) {
        Text(label, x, y, 15, kDim);
        Text(value, x + 330 - TextWidth(value, 15), y, 15, vc);
        y += 21;
    };
    auto head = [&](float x, float& y, const std::string& t) { y += 6; Text(t, x, y, 19, kGold); y += 27; };

    // --- Column 1: weapon
    float x = P.x + 24, y = P.y + 116;
    head(x, y, "Weapon: " + (w ? content_.Tr(w->name_key) : std::string("Bare hands")));
    float cc = CritChance(w), cm = CritMult(w);
    if (w && w->weapon.kind == "ranged") {
        float full = ArrowHitDamage(w, 1.0f);
        row(x, y, "Arrow damage (full draw)", Fmt1(full));
        row(x, y, "Arrow damage (quick shot)", Fmt1(ArrowHitDamage(w, 0.3f)));
        row(x, y, "Sneak-shot multiplier", "x" + Fmt1(1.6f * std::max(1.0f, Bonus("ranged_crit_multiplier"))));
        row(x, y, "Critical chance / multiplier", Pct(cc) + "  /  x" + Fmt1(cm), cc > 0.1f ? kGold : kText);
        row(x, y, "Expected damage per arrow", Fmt1(full * (1.0f + cc * (cm - 1.0f))), kAccent);
    } else {
        float light = MeleeHitDamage(w, false), heavy = MeleeHitDamage(w, true);
        float t = (w ? w->weapon.attack_time_seconds : 0.45f) * (1.0f - std::min(0.25f, (Attr("agility") - 10) * 0.015f));
        float dps = light / std::max(0.1f, t);
        row(x, y, "Light / heavy hit", Fmt1(light) + "  /  " + Fmt1(heavy));
        row(x, y, "Swing time", Fmt1(t) + " s");
        row(x, y, "Stamina per swing", Fmt1(w ? w->weapon.stamina_cost : 5.0f));
        row(x, y, "Reach", Fmt1(w ? w->weapon.reach_meters : 1.6f) + " m");
        row(x, y, "Critical chance / multiplier", Pct(cc) + "  /  x" + Fmt1(cm), cc > 0.1f ? kGold : kText);
        row(x, y, "Sneak-attack multiplier", std::string("x") + ((w && w->weapon.skill == "daggers") ? "2.5" : "1.75"));
        row(x, y, "Damage per second (light)", Fmt1(dps));
        row(x, y, "Expected DPS incl. crits", Fmt1(dps * (1.0f + cc * (cm - 1.0f))), kAccent);
    }
    if (w && !w->weapon.bane_family.empty()) row(x, y, "Bane vs " + w->weapon.bane_family, "x" + Fmt1(w->weapon.bane_mult), kGold);
    float steal = (w ? w->weapon.life_steal : 0.0f) + Bonus("life_steal");
    if (steal > 0) row(x, y, "Life steal", Pct(steal), kGold);
    float moh = (w ? w->weapon.mana_on_hit : 0.0f) + Bonus("mana_on_melee_hit");
    if (moh > 0) row(x, y, "Mana per hit", "+" + Fmt1(moh), kGold);
    TextWrapped("Crit = weapon base + 0.5% per Agility above 10 + 15% of Perception's effect + bonuses (max 75%).", {x, y + 4, 330, 40}, 12, kDim);
    y += 44;

    head(x, y, "Defence");
    int armor = ArmorRating();
    row(x, y, "Armor", std::to_string(armor) + "  (takes " + Pct(40.0f / (40.0f + armor)) + " damage)");
    float red = std::min(0.92f, content_.balancing.block_damage_reduction * (Equipped("off_hand") ? 1.0f : 0.6f) * (1.0f + SkillEffect("block") * 0.5f));
    row(x, y, Equipped("off_hand") ? "Block with shield" : "Block with weapon", "-" + Pct(red) + " damage");
    row(x, y, "Parry window", Fmt1(content_.balancing.parry_window_seconds * 1000.0f) + " ms");

    // --- Column 2: magic
    x = P.x + 384;
    y = P.y + 116;
    head(x, y, "Magic");
    row(x, y, "Mana regeneration", Fmt1(content_.balancing.mana_regen_per_sec * (1.0f + (Attr("will") - 10) * 0.04f)) + " /s");
    if (Bonus("spell_power_bonus") > 0) row(x, y, "Spell power bonus", "+" + Pct(Bonus("spell_power_bonus")), kGold);
    if (Bonus("spell_cost_reduction") > 0) row(x, y, "Spell cost reduction", "-" + Pct(Bonus("spell_cost_reduction")), kGold);
    if (player_.known_spells.empty()) { Text("No spells known.", x, y, 15, kDim); y += 21; }
    for (const auto& id : player_.known_spells) {
        const SpellDef* s = content_.GetSpell(id);
        if (!s) continue;
        float pw = s->effect.base_power * SpellPowerMult(*s);
        std::string what;
        const std::string& pr = s->effect.primitive;
        if (pr == "projectile_damage") {
            what = Fmt1(pw) + " dmg";
            if (s->effect.splash_radius > 0) what += ", splash " + Fmt1(s->effect.splash_radius) + "m";
            if (s->effect.drain_fraction > 0) what += ", drain " + Pct(s->effect.drain_fraction);
        } else if (pr == "self_heal") what = "heals " + Fmt1(pw);
        else if (pr == "buff_armor") what = "+" + Fmt1(pw) + " armor, " + Fmt1(s->effect.duration_seconds) + "s";
        else if (pr == "buff_stealth") what = Pct(1.0f - s->effect.visibility_multiplier) + " less visible";
        else what = Fmt1(s->effect.duration_seconds) + "s light";
        Text(content_.Tr(s->name_key), x, y, 15, kText);
        std::string cost = Fmt1(SpellCost(*s)) + " mp";
        Text(cost, x + 330 - TextWidth(cost, 15), y, 15, kAccent);
        y += 19;
        Text("  " + what + "   (" + Fmt1(s->cooldown_seconds) + "s cooldown)", x, y, 13, kDim);
        y += 21;
    }

    // --- Column 3: utility & bonuses
    x = P.x + 744;
    y = P.y + 116;
    head(x, y, "Exploration & Trade");
    row(x, y, "Move speed", Fmt1(MoveSpeed()) + " m/s");
    row(x, y, "Carry weight", Fmt1(CarriedWeight()) + " / " + Fmt1(CarryCapacity()));
    float vis = 0.55f * (1.0f - std::min(0.5f, SkillEffect("stealth")));
    row(x, y, "Visibility while sneaking", Pct(vis));
    row(x, y, "Lockpick: easy / average / hard", Pct(LockpickChance(5)) + " / " + Pct(LockpickChance(9)) + " / " + Pct(LockpickChance(12)));
    row(x, y, "Shop discount", Pct(ShopDiscount()));
    row(x, y, "Sell price (of item value)", Pct(0.35f + std::min(0.2f, SkillLevel("persuasion") * 0.004f + (Attr("presence") - 10) * 0.01f)));

    head(x, y, "Active bonuses");
    static const char* keys[] = {"crit_chance_bonus", "crit_damage_bonus", "life_steal", "spell_power_bonus", "spell_cost_reduction",
                                 "melee_bonus_magic_damage", "mana_on_melee_hit", "heal_on_block", "armor_bonus",
                                 "ranged_crit_multiplier", "move_speed_bonus", "shop_discount", "lockpick_bonus", "health_regen", "stamina_regen",
                                 "dice_bonus"};
    bool any = false;
    for (const char* k : keys) {
        float syn = SynergyBonus(k), gear = GearBonus(k), food = BuffBonus(k);
        if (syn == 0.0f && gear == 0.0f && food == 0.0f) continue;
        any = true;
        std::string src;
        if (syn != 0.0f) src += "synergy";
        if (gear != 0.0f) src += std::string(src.empty() ? "" : " + ") + "gear";
        if (food != 0.0f) src += std::string(src.empty() ? "" : " + ") + "food";
        Text(BonusLabel(k, syn + gear + food), x, y, 14, kGold);
        Text(src, x + 330 - TextWidth(src, 13), y + 1, 13, kDim);
        y += 20;
    }
    if (!any) TextWrapped("None yet. Raise two skills to unlock a synergy, or equip gear with special properties.", {x, y, 330, 60}, 14, kDim);
}

// ============================================================================
// Journal
// ============================================================================
void GameEngine::DrawJournal() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Rectangle P = {VW * 0.5f - 560, VH * 0.5f - 310, 1120, 620};
    Panel(P, Color{30, 26, 20, 245});
    Text("Journal", P.x + 24, P.y + 16, 32, kGold);
    auto hit = [&](Rectangle r) { return CheckCollisionPointRec(GetMousePosition(), {r.x * u, r.y * u, r.width * u, r.height * u}); };

    // Which quest is each started quest's campaign, in campaign order; quests without one go last.
    std::vector<std::pair<const CampaignDef*, std::vector<std::string>>> groups;
    for (const auto& c : content_.campaigns) groups.push_back({&c, {}});
    groups.push_back({nullptr, {}});
    for (const auto& qid : QuestOrder()) {
        const QuestDef* q = content_.GetQuest(qid);
        if (!q) continue;
        bool placed = false;
        for (auto& [c, list] : groups) if (c && c->id == q->campaign) { list.push_back(qid); placed = true; }
        if (!placed) groups.back().second.push_back(qid);
    }
    auto stageOf = [&](const std::string& qid, bool& done) -> const QuestStageDef* {
        const QuestDef* q = content_.GetQuest(qid);
        done = false;
        if (!q) return nullptr;
        int stage = player_.quest_stages.at(qid);
        for (const auto& st : q->stages) if (st.stage == stage) { done = st.completed; return &st; }
        return nullptr;
    };
    if (journal_selected_.empty() || !player_.quest_stages.count(journal_selected_))
        journal_selected_ = !player_.tracked_quest.empty() ? player_.tracked_quest : content_.game_cfg.starting_quest;

    // --- Left: campaigns and their quests (active first, then completed)
    Rectangle L = {P.x + 20, P.y + 64, 380, P.height - 84};
    float y = L.y;
    for (auto& [c, list] : groups) {
        if (list.empty()) continue;
        std::string head = c ? content_.Tr(c->name_key) : std::string("Other Tales");
        Text(head, L.x, y, 18, kAccent);
        y += 24;
        for (int pass = 0; pass < 2; pass++) {
            for (const auto& qid : list) {
                bool done;
                stageOf(qid, done);
                if ((pass == 0) == done) continue;
                const QuestDef* q = content_.GetQuest(qid);
                Rectangle r = {L.x, y, L.width, 26};
                bool sel = qid == journal_selected_;
                if (sel) DrawRectangleRec({r.x * u, r.y * u, r.width * u, r.height * u}, Color{70, 56, 36, 220});
                else if (hit(r)) DrawRectangleRec({r.x * u, r.y * u, r.width * u, r.height * u}, Color{44, 38, 30, 220});
                if (hit(r) && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) { journal_selected_ = qid; journal_scroll_ = 0; }
                std::string mark = qid == content_.game_cfg.starting_quest ? "* " : qid == player_.tracked_quest ? "> " : "  ";
                Text(mark + content_.Tr(q->title_key), r.x + 8, r.y + 4, 16, done ? kDim : sel ? kGold : kText);
                y += 28;
            }
        }
        y += 10;
    }
    Text("* main story    > shown on screen", L.x, P.y + P.height - 30, 13, kDim);

    // --- Right: the selected quest
    Rectangle D = {P.x + 420, P.y + 64, P.width - 440, P.height - 84};
    Panel(D, Color{22, 20, 16, 235});
    const QuestDef* q = content_.GetQuest(journal_selected_);
    if (!q) return;
    bool done;
    const QuestStageDef* cur = stageOf(journal_selected_, done);
    if (const CampaignDef* c = content_.GetCampaign(q->campaign)) Text(content_.Tr(c->name_key), D.x + 20, D.y + 14, 14, kDim);
    Text(content_.Tr(q->title_key) + (done ? "  (completed)" : ""), D.x + 20, D.y + 32, 24, done ? kDim : kGold);
    bool isMain = journal_selected_ == content_.game_cfg.starting_quest;
    if (!done && !isMain) {
        bool tracked = player_.tracked_quest == journal_selected_;
        if (Button({D.x + D.width - 150, D.y + 14, 130, 30}, tracked ? "On screen" : "Show on screen", !tracked, 14))
            player_.tracked_quest = journal_selected_;
    }
    Rectangle body = {D.x + 20, D.y + 70, D.width - 40, D.height - 84};
    float wheel = GetMouseWheelMove();
    if (hit(D)) journal_scroll_ -= wheel * 40;
    // Measure, clamp, then draw clipped.
    auto layout = [&](bool draw) {
        float yy = body.y - journal_scroll_;
        yy += TextWrapped(content_.Tr(q->summary_key), {body.x, yy, body.width, 400}, 15, kDim, draw) + 12;
        if (cur) {
            if (draw) Text(done ? "Outcome:" : "Current objective:", body.x, yy, 16, kAccent);
            yy += 22;
            yy += TextWrapped(content_.Tr(cur->objective_key), {body.x, yy, body.width, 200}, 17, kText, draw) + 16;
        }
        auto log = player_.quest_log[journal_selected_];
        for (auto it = log.rbegin(); it != log.rend(); ++it) {
            for (const auto& st : q->stages) {
                if (st.stage != *it) continue;
                if (draw) Text("-", body.x, yy, 15, kDim);
                yy += TextWrapped(content_.Tr(st.journal_key), {body.x + 18, yy, body.width - 18, 400}, 15, kText, draw) + 10;
            }
        }
        return yy + journal_scroll_ - body.y;
    };
    float total = layout(false);
    journal_scroll_ = Clamp(journal_scroll_, 0.0f, std::max(0.0f, total - body.height));
    BeginScissorMode(static_cast<int>(body.x * u), static_cast<int>(body.y * u), static_cast<int>(body.width * u), static_cast<int>(body.height * u));
    layout(true);
    EndScissorMode();
    if (journal_scroll_ < total - body.height - 1.0f) Text("(scroll for more)", D.x + D.width - 140, D.y + D.height - 20, 13, kDim);
}

// ============================================================================
// Map
// ============================================================================
void GameEngine::DrawMapOverlay() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Color{10, 9, 8, 235});
    if (!scene_.map) return;
    // Show only the current zone and the storey the player stands on.
    const MapZoneDef* zone = CurrentZone();
    std::string title = content_.Tr(zone ? zone->display_name_key : scene_.map->display_name_key);
    Text(title, VW * 0.5f - TextWidth(title, 30) * 0.5f, 18, 30, kGold);
    float lowY = player_.pos.y - 1.6f, highY = player_.pos.y + 3.2f;
    auto inView = [&](const BoundingBox& b) {
        if (b.max.y < lowY || b.min.y > highY) return false;
        if (!zone) return true;
        return b.max.x > zone->box_min.x - 2 && b.min.x < zone->box_max.x + 2 && b.max.z > zone->box_min.z - 2 && b.min.z < zone->box_max.z + 2;
    };
    auto pointInView = [&](Vector3 p) { return inView({{p.x, p.y, p.z}, {p.x, p.y + 1.0f, p.z}}); };

    BoundingBox bounds = {{1e9f, 0, 1e9f}, {-1e9f, 0, -1e9f}};
    for (const auto& p : scene_.props) {
        if (!inView(p.world_box)) continue;
        bounds.min.x = std::min(bounds.min.x, p.world_box.min.x);
        bounds.min.z = std::min(bounds.min.z, p.world_box.min.z);
        bounds.max.x = std::max(bounds.max.x, p.world_box.max.x);
        bounds.max.z = std::max(bounds.max.z, p.world_box.max.z);
    }
    float mw = bounds.max.x - bounds.min.x, mh = bounds.max.z - bounds.min.z;
    if (mw <= 0 || mh <= 0) return;
    Rectangle area = {60, 70, VW - 120, VH - 130};
    float sc = std::min(area.width / mw, area.height / mh);
    float ox = area.x + (area.width - mw * sc) * 0.5f, oy = area.y + (area.height - mh * sc) * 0.5f;
    auto toS = [&](float x, float z) { return Vector2{(ox + (x - bounds.min.x) * sc) * u, (oy + (z - bounds.min.z) * sc) * u}; };
    auto rect = [&](const BoundingBox& b, Color c) {
        Vector2 a = toS(b.min.x, b.min.z), bb = toS(b.max.x, b.max.z);
        DrawRectangleV(a, {bb.x - a.x, bb.y - a.y}, c);
    };
    bool indoor = atmo_.sun_color.x < 0.2f;
    for (const auto& p : scene_.props) {
        if (!inView(p.world_box)) continue;
        if ((p.walkable || p.ramp_axis) && p.world_box.max.y < player_.pos.y + 1.0f) {
            bool wood = p.model_path.find("wood") != std::string::npos;
            rect(p.world_box, wood ? Color{72, 54, 36, 255} : p.model_path.find("grass") != std::string::npos ? Color{34, 48, 30, 255} : Color{58, 56, 52, 255});
        }
    }
    for (const auto& p : scene_.props) {
        if (!p.solid || !inView(p.world_box)) continue;
        bool tree = p.model_path.find("tree") != std::string::npos;
        if (tree) { DrawCircleV(toS((p.collider.min.x + p.collider.max.x) * 0.5f, (p.collider.min.z + p.collider.max.z) * 0.5f), 1.4f * sc * u, Color{30, 70, 36, 255}); continue; }
        rect(p.world_box, indoor ? Color{150, 140, 125, 255} : Color{165, 155, 135, 255});
    }
    for (const auto& in : scene_.interactables) {
        if (!inView(in.world_box)) continue;
        Color c = {200, 200, 200, 255};
        if (in.def.type == "door") c = in.open ? Color{90, 200, 110, 255} : in.locked || in.def.mechanism_only ? Color{200, 80, 60, 255} : Color{170, 120, 60, 255};
        else if (in.def.type == "chest") c = in.used ? Color{110, 100, 80, 255} : kGold;
        else if (in.def.type == "readable") c = Color{220, 210, 180, 255};
        else if (in.def.type == "lever" || in.def.type == "pressure_plate") c = kAccent;
        else if (in.def.type == "quest_pedestal") c = in.used ? kDim : Color{255, 240, 140, 255};
        if (in.def.type == "door") rect(in.world_box, c);
        else DrawCircleV(toS(in.def.pos.x, in.def.pos.z), std::max(3.0f, 0.35f * sc) * u, c);
    }
    for (const auto& n : scene_.npcs) {
        if (n.hidden || !pointInView(n.pos)) continue;
        Vector2 p = toS(n.pos.x, n.pos.z);
        DrawCircleV(p, 5 * u, Color{255, 220, 90, 255});
        Text(content_.Tr(n.def->name_key), p.x / u + 8, p.y / u - 8, 13, Color{255, 230, 150, 255});
    }
    for (const auto& pt : scene_.map->portals) {
        if (!pointInView(pt.pos)) continue;
        Vector2 p = toS(pt.pos.x, pt.pos.z);
        DrawCircleLinesV(p, pt.radius * sc * u, Color{100, 220, 255, 255});
        std::string label = pt.prompt;
        float tw = TextWidth(label, 13);
        float lx = Clamp(p.x / u - tw * 0.5f, 10.0f, VW - tw - 10);
        Text(label, lx, p.y / u + pt.radius * sc + 4, 13, Color{140, 230, 255, 255});
    }
    // Objective pin
    Vector3 obj;
    std::string objTitle;
    if (ObjectiveMarker(obj, objTitle)) {
        bool here = pointInView(obj);
        Vector2 op = toS(obj.x, obj.z);
        if (!here) {  // on another storey or in another area: pin at the map's edge in its direction
            op.x = Clamp(op.x, (area.x + 10) * u, (area.x + area.width - 10) * u);
            op.y = Clamp(op.y, (area.y + 10) * u, (area.y + area.height - 10) * u);
        }
        float pulse = 6.0f + 2.0f * sinf(time_ * 5.0f);
        DrawCircleV(op, (pulse + 3) * u, Color{40, 20, 10, 200});
        DrawCircleV(op, pulse * u, Color{255, 150, 60, 255});
        std::string lbl = objTitle + (here ? "" : obj.y > player_.pos.y + 2.0f ? "  (upstairs)" : obj.y < player_.pos.y - 2.0f ? "  (below)" : "  (that way)");
        Text(lbl, op.x / u - TextWidth(lbl, 14) * 0.5f, op.y / u + 12, 14, Color{255, 190, 110, 255});
    }
    // Player arrow
    Vector2 pp = toS(player_.pos.x, player_.pos.z);
    Vector2 f = {sinf(player_.yaw), cosf(player_.yaw)};
    Vector2 r = {-f.y, f.x};
    float L = 12 * u;
    Vector2 tip = {pp.x + f.x * L, pp.y + f.y * L};
    Vector2 bl = {pp.x - f.x * L * 0.6f + r.x * L * 0.6f, pp.y - f.y * L * 0.6f + r.y * L * 0.6f};
    Vector2 br = {pp.x - f.x * L * 0.6f - r.x * L * 0.6f, pp.y - f.y * L * 0.6f - r.y * L * 0.6f};
    DrawTriangle(tip, br, bl, Color{255, 80, 60, 255});
    DrawTriangle(tip, bl, br, Color{255, 80, 60, 255});
    Text("[" + BindingLabel("map") + "] close     Orange: objective   Yellow: people   Gold: unopened chests   Red: locked doors   Blue: mechanisms", 60, VH - 40, 14, kDim);
}

// ============================================================================
// Dialogue
// ============================================================================
void GameEngine::DrawDialogue() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    const DialogueDef* d = content_.GetDialogue(dialogue_id_);
    if (!d) return;
    auto it = d->nodes.find(dialogue_node_);
    if (it == d->nodes.end()) return;
    const DialogueNode& node = it->second;
    std::vector<int> vis = VisibleChoices();
    std::vector<std::string> labels;
    for (size_t k = 0; k < vis.size(); k++) {
        const DialogueChoice& c = node.choices[vis[k]];
        std::string label = std::to_string(k + 1) + ". " + content_.Tr(c.text_key);
        if (c.roll_dc > 0) label += "   (d20, DC " + std::to_string(c.roll_dc) + ": " + std::to_string(DialogueRollChance(c)) + "%)";
        labels.push_back(label);
    }
    if (labels.empty()) labels.push_back("1. [Continue]");
    const std::string body = content_.Tr(node.text_key);
    const float W = 1040.0f;
    // Text size follows the player's setting, shrinking only if the whole scene wouldn't fit on screen.
    float fs = 17.0f * content_.game_cfg.text_scale, textH = 0, choicesH = 0;
    for (int fit = 0; fit < 12; fit++) {
        textH = TextWrapped(body, {0, 0, W - 48, 0}, fs, kText, false);
        choicesH = 0;
        for (const auto& l : labels) choicesH += TextWrapped(l, {0, 0, W - 64, 0}, fs, kText, false) + 10;
        if (62 + textH + choicesH + 16 <= VH - 40 || fs <= 13.0f) break;
        fs -= 1.0f;
    }
    float panelH = std::clamp(62 + textH + choicesH + 16, 310.0f, VH - 40);
    Rectangle P = {VW * 0.5f - W * 0.5f, VH - 20 - panelH, W, panelH};
    Panel(P, Color{14, 13, 18, 240});
    std::string speaker = content_.Tr(node.speaker_key);
    std::string title;
    if (dialogue_npc_ >= 0 && dialogue_npc_ < static_cast<int>(scene_.npcs.size())) {
        const NpcDef* npc = scene_.npcs[dialogue_npc_].def;
        if (speaker.empty() || speaker == node.speaker_key) speaker = content_.Tr(npc->name_key);
        // Group scenes: a node may be spoken by someone else; show *their* title, not the host's.
        if (node.speaker_key.empty() || node.speaker_key == npc->name_key) title = content_.Tr(npc->title_key);
        else
            for (const auto& other : content_.npcs)
                if (other.second.name_key == node.speaker_key) title = content_.Tr(other.second.title_key);
    }
    float ns = 24.0f * std::min(content_.game_cfg.text_scale, 1.25f);
    Text(speaker, P.x + 24, P.y + 16, ns, kGold);
    if (!title.empty()) Text(title, P.x + 30 + TextWidth(speaker, ns), P.y + 16 + ns - 17, 15, kDim);
    float y = P.y + 52 + TextWrapped(body, {P.x + 24, P.y + 52, P.width - 48, 140}, fs, kText) + 10;
    if (vis.empty()) {
        float h = TextWrapped(labels[0], {0, 0, W - 64, 0}, fs, kText, false) + 8;
        if (Button({P.x + 24, y, P.width - 48, h}, labels[0], true, fs)) { EndDialogue(); return; }
        return;
    }
    for (size_t k = 0; k < vis.size(); k++) {
        float h = TextWrapped(labels[k], {0, 0, W - 64, 0}, fs, kText, false) + 8;
        Rectangle r = {P.x + 24, y, P.width - 48, h};
        Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
        bool hover = CheckCollisionPointRec(GetMousePosition(), s);
        if (hover) DrawRectangleRec(s, Color{60, 48, 32, 200});
        TextWrapped(labels[k], {r.x + 8, r.y + 4, r.width - 16, h}, fs, hover ? kGold : Color{210, 200, 180, 255});
        if (hover && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) { ChooseDialogue(vis[k]); return; }
        y += h + 2;
    }
    if (y > VH) ui_scroll_ = 0;
}

// ============================================================================
// Shop
// ============================================================================
void GameEngine::DrawShop() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    const NpcDef* npc = content_.GetNpc(shop_npc_);
    if (!npc) { SetOverlay(Overlay::None); return; }
    Rectangle P = {VW * 0.5f - 560, VH * 0.5f - 310, 1120, 620};
    Panel(P);
    Text(content_.Tr(npc->name_key) + " - Wares", P.x + 20, P.y + 14, 28, kGold);
    std::string g = "Your gold: " + std::to_string(player_.gold);
    Text(g, P.x + P.width - TextWidth(g, 20) - 24, P.y + 20, 20, Color{255, 215, 100, 255});
    Text("Buy (click)", P.x + 20, P.y + 56, 18, kDim);
    Text("Sell (click)", P.x + 580, P.y + 56, 18, kDim);
    float y = P.y + 84;
    for (const auto& e : npc->vendor_inventory) {
        const ItemDef* d = content_.GetItem(e.item_id);
        if (!d) continue;
        int stock = VendorStock(*npc, e);
        int price = BuyPrice(e);
        Rectangle r = {P.x + 20, y, 530, 34};
        Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
        bool can = stock > 0 && player_.gold >= price;
        bool hover = CheckCollisionPointRec(GetMousePosition(), s);
        DrawRectangleRec(s, hover && can ? Color{60, 48, 32, 220} : Color{20, 20, 24, 160});
        Icon(d->icon, {r.x + 4, r.y + 1, 32, 32}, stock > 0 ? WHITE : Color{255, 255, 255, 80});
        Text(content_.Tr(d->name_key), r.x + 44, r.y + 7, 17, stock > 0 ? kText : kDim);
        Text("x" + std::to_string(stock), r.x + 340, r.y + 8, 15, kDim);
        Text(std::to_string(price) + "g", r.x + 440, r.y + 7, 17, can ? Color{255, 215, 100, 255} : Color{160, 90, 80, 255});
        if (hover && can && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) BuyItem(e);
        y += 38;
    }
    y = P.y + 84;
    std::vector<std::string> seen;
    for (const auto& it : player_.inventory) {
        if (std::find(seen.begin(), seen.end(), it.id) != seen.end()) continue;
        seen.push_back(it.id);
        const ItemDef* d = content_.GetItem(it.id);
        if (!d || d->quest_item) continue;
        if (y > P.y + P.height - 80) break;
        Rectangle r = {P.x + 580, y, 520, 34};
        Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
        bool hover = CheckCollisionPointRec(GetMousePosition(), s);
        DrawRectangleRec(s, hover ? Color{60, 48, 32, 220} : Color{20, 20, 24, 160});
        Icon(d->icon, {r.x + 4, r.y + 1, 32, 32});
        int cnt = CountItem(it.id);
        Text(content_.Tr(d->name_key) + (cnt > 1 ? " (" + std::to_string(cnt) + ")" : "") + (IsEquipped(it.id) ? " [E]" : ""), r.x + 44, r.y + 7, 17, kText);
        Text(std::to_string(SellPrice(*d)) + "g", r.x + 440, r.y + 7, 17, Color{255, 215, 100, 255});
        if (hover && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) { SellItem(it.id); break; }
        y += 38;
    }
    if (Button({P.x + P.width * 0.5f - 100, P.y + P.height - 60, 200, 42}, "Leave")) SetOverlay(Overlay::None);
}

// ============================================================================
// Container
// ============================================================================
void GameEngine::DrawContainer() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    ContainerState& c = Persist().containers[container_key_];
    Rectangle P = {VW * 0.5f - 300, VH * 0.5f - 260, 600, 520};
    Panel(P);
    Text(container_title_, P.x + 20, P.y + 14, 26, kGold);
    float y = P.y + 60;
    int clicked = -2;
    auto row = [&](int index, const std::string& icon, const std::string& label) {
        Rectangle r = {P.x + 20, y, P.width - 40, 36};
        Rectangle s = {r.x * u, r.y * u, r.width * u, r.height * u};
        bool hover = CheckCollisionPointRec(GetMousePosition(), s);
        DrawRectangleRec(s, hover ? Color{60, 48, 32, 220} : Color{20, 20, 24, 160});
        Icon(icon, {r.x + 4, r.y + 2, 32, 32});
        Text(label, r.x + 44, r.y + 8, 18, kText);
        if (hover && IsMouseButtonPressed(MOUSE_BUTTON_LEFT)) clicked = index;
        y += 40;
    };
    if (c.gold > 0) row(-1, "assets/ui/items/gold_coins.png", std::to_string(c.gold) + " gold");
    for (size_t i = 0; i < c.items.size(); i++) {
        const ItemDef* d = content_.GetItem(c.items[i].id);
        if (!d) continue;
        row(static_cast<int>(i), d->icon, content_.Tr(d->name_key) + (c.items[i].qty > 1 ? "  x" + std::to_string(c.items[i].qty) : ""));
    }
    if (c.gold == 0 && c.items.empty()) Text("Empty.", P.x + 24, y, 18, kDim);
    if (clicked != -2) TakeFromContainer(clicked);
    if (Button({P.x + 20, P.y + P.height - 60, 270, 42}, "Take All [" + BindingLabel("interact") + "]")) { TakeAllFromContainer(); return; }
    if (Button({P.x + 310, P.y + P.height - 60, 270, 42}, "Close")) SetOverlay(Overlay::None);
}

// ============================================================================
// Reader
// ============================================================================
void GameEngine::DrawReader() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    Rectangle P = {VW * 0.5f - 380, VH * 0.5f - 300, 760, 600};
    float uu = u;
    DrawRectangleRec({P.x * uu, P.y * uu, P.width * uu, P.height * uu}, Color{214, 196, 160, 250});
    DrawRectangleLinesEx({P.x * uu, P.y * uu, P.width * uu, P.height * uu}, 3 * uu, Color{110, 80, 50, 255});
    DrawRectangleLinesEx({(P.x + 8) * uu, (P.y + 8) * uu, (P.width - 16) * uu, (P.height - 16) * uu}, 1 * uu, Color{140, 110, 70, 255});
    Color ink = {48, 34, 22, 255};
    float tw = TextWidth(reader_title_, 26);
    Text(reader_title_, P.x + (P.width - tw) * 0.5f, P.y + 26, 26, Color{90, 30, 20, 255});
    Rectangle body = {P.x + 40, P.y + 76, P.width - 80, P.height - 150};
    float rfs = 18.0f * content_.game_cfg.text_scale;
    float total = TextWrapped(reader_text_, body, rfs, ink, false);
    float wheel = GetMouseWheelMove();
    ui_scroll_ = Clamp(ui_scroll_ - wheel * 40, 0.0f, std::max(0.0f, total - body.height));
    BeginScissorMode(static_cast<int>(body.x * u), static_cast<int>(body.y * u), static_cast<int>(body.width * u), static_cast<int>(body.height * u));
    TextWrapped(reader_text_, {body.x, body.y - ui_scroll_, body.width, body.height}, rfs, ink);
    EndScissorMode();
    if (ui_scroll_ < total - body.height - 1.0f) {
        const std::string more = "(scroll for more)";
        Text(more, P.x + P.width - 40 - TextWidth(more, 14), P.y + P.height - 82, 14, Color{120, 90, 60, 255});
    }
    if (Button({P.x + P.width * 0.5f - 100, P.y + P.height - 60, 200, 40}, "Close [" + BindingLabel("interact") + "]")) SetOverlay(Overlay::None);
}

// ============================================================================
// Prologue narration & subtitles
// ============================================================================
void GameEngine::DrawNarration() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), BLACK);
    if (narration_page_ >= static_cast<int>(narration_pages_.size())) return;
    float a = Clamp(narration_time_ / 1.2f, 0.0f, 1.0f);
    Color c = {kText.r, kText.g, kText.b, static_cast<unsigned char>(a * 255)};
    const std::string& page = narration_pages_[narration_page_];
    float bw = 720.0f * std::min(content_.game_cfg.text_scale, 1.4f);
    Rectangle box = {VW * 0.5f - bw * 0.5f, 0, bw, 400};
    float fs = 24.0f * content_.game_cfg.text_scale;
    float h = TextWrapped(page, box, fs, c, false);
    while (h > VH - 140 && fs > 16.0f) { fs -= 1.0f; h = TextWrapped(page, box, fs, c, false); }
    box.y = VH * 0.5f - h * 0.5f - 20;
    TextWrapped(page, box, fs, c);
    std::string hint = content_.Tr("ui.prologue.continue");
    Color hc = {kDim.r, kDim.g, kDim.b, static_cast<unsigned char>(a * 160)};
    Text(hint, VW * 0.5f - TextWidth(hint, 14) * 0.5f, VH - 50, 14, hc);
    for (size_t i = 0; i < narration_pages_.size(); i++) {
        Color dc = i == static_cast<size_t>(narration_page_) ? kGold : Color{70, 66, 60, 255};
        DrawCircleV({(VW * 0.5f - (narration_pages_.size() - 1) * 9.0f + i * 18.0f) * u, (VH - 70) * u}, 3.0f * u, dc);
    }
}

void GameEngine::DrawSubtitle() {
    if (subtitle_time_ <= 0.0f || subtitle_text_.empty()) return;
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    float a = Clamp(subtitle_time_ * 2.0f, 0.0f, 1.0f);
    float width = 760 * std::min(content_.game_cfg.text_scale, 1.3f);
    float fs = 18.0f * content_.game_cfg.text_scale;
    float h = TextWrapped(subtitle_text_, {0, 0, width, 200}, fs, kText, false);
    float y = VH - 132 - h;
    DrawRectangle(static_cast<int>((VW * 0.5f - width * 0.5f - 14) * u), static_cast<int>((y - 26) * u), static_cast<int>((width + 28) * u),
                  static_cast<int>((h + 36) * u), Color{0, 0, 0, static_cast<unsigned char>(a * 150)});
    Text(subtitle_speaker_, VW * 0.5f - width * 0.5f, y - 22, 16, Color{kGold.r, kGold.g, kGold.b, static_cast<unsigned char>(a * 255)});
    TextWrapped(subtitle_text_, {VW * 0.5f - width * 0.5f, y, width, 200}, fs, Color{kText.r, kText.g, kText.b, static_cast<unsigned char>(a * 255)});
}

// ============================================================================
// Death & ending
// ============================================================================
void GameEngine::DrawDead() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Color{40, 0, 0, 190});
    std::string t = "YOU HAVE BEEN COUNTED";
    Text(t, VW * 0.5f - TextWidth(t, 54) * 0.5f, VH * 0.3f, 54, Color{220, 60, 50, 255});
    std::string s = "The Bureau will be delighted to finally process your paperwork.";
    Text(s, VW * 0.5f - TextWidth(s, 18) * 0.5f, VH * 0.3f + 70, 18, kText);
    // A loading-screen style tip, chosen per death and kept while the screen is up.
    int tips = 0;
    while (content_.Tr("tip." + std::to_string(tips + 1)) != "tip." + std::to_string(tips + 1)) tips++;
    if (tips > 0) {
        std::string tip = "TIP: " + content_.Tr("tip." + std::to_string(1 + death_tip_ % tips));
        TextWrapped(tip, {VW * 0.5f - 380, VH * 0.3f + 120, 760, 80}, 16, kDim);
    }
    float x = VW * 0.5f - 150, y = VH * 0.55f;
    if (Button({x, y, 300, 46}, "Load Autosave", SaveExists("autosave"))) { LoadGame("autosave"); return; }
    if (Button({x, y + 56, 300, 46}, "Load Quick Save", SaveExists("slot_1"))) { LoadGame("slot_1"); return; }
    if (Button({x, y + 112, 300, 46}, "Quit to Title")) ReturnToTitle();
}

void GameEngine::DrawEnding() {
    float u = U();
    float VW = GetScreenWidth() / u, VH = GetScreenHeight() / u;
    DrawRectangle(0, 0, GetScreenWidth(), GetScreenHeight(), Color{6, 6, 10, 225});
    std::string t = "Chapter Zero Complete";
    Text(t, VW * 0.5f - TextWidth(t, 50) * 0.5f, VH * 0.12f, 50, kGold);
    const QuestDef* q = content_.GetQuest(content_.game_cfg.starting_quest);
    float y = VH * 0.12f + 80;
    if (q) {
        for (const auto& st : q->stages) {
            if (st.stage != ending_stage_) continue;
            std::string obj = content_.Tr(st.objective_key);
            Text(obj, VW * 0.5f - TextWidth(obj, 20) * 0.5f, y, 20, kText);
            y += 48;
            y += TextWrapped(content_.Tr(st.journal_key), {VW * 0.5f - 400, y, 800, 220}, 18, kText) + 20;
        }
    }
    std::string epi;
    auto add = [&](const char* key) { epi += content_.Tr(key) + " "; };
    if (player_.flags.count("marta_testimony")) add("ending.marta_testimony");
    if (player_.flags.count("spirit_clue_learned")) add(player_.flags.count("witness_named") ? "ending.spirit_named" : "ending.spirit_waiting");
    if (player_.flags.count("ilse_remembered")) add("ending.ilse");
    if (player_.flags.count("ilse_remembered") && player_.flags.count("marta_knows_ilse")) add("ending.ilse_alive");
    add(player_.flags.count("seal_renewed") ? "ending.seal" : "ending.no_seal");
    TextWrapped(epi, {VW * 0.5f - 420, y, 840, 200}, 16, kDim);
    std::string stats = "Level " + std::to_string(player_.level) + "   Gold " + std::to_string(player_.gold) + "   Time played " +
                        std::to_string(static_cast<int>(player_.play_time / 60)) + " min";
    Text(stats, VW * 0.5f - TextWidth(stats, 16) * 0.5f, VH - 150, 16, kDim);
    if (Button({VW * 0.5f - 320, VH - 100, 300, 48}, "Keep Exploring")) { screen_ = Screen::Playing; overlay_ = Overlay::None; }
    if (Button({VW * 0.5f + 20, VH - 100, 300, 48}, "Return to Title")) ReturnToTitle();
}

// ============================================================================
// Debug overlay (F3)
// ============================================================================
void GameEngine::DrawDebug() {
    float u = U();
    DrawRectangle(0, 0, static_cast<int>(560 * u), static_cast<int>(400 * u), Color{0, 0, 0, 180});
    float y = 8;
    auto line = [&](const std::string& s, Color c = Color{180, 255, 180, 255}) {
        DrawTextEx(MonoFont(), s.c_str(), {8 * u, y * u}, 14 * u, 0, c);
        y += 16;
    };
    line("FPS " + std::to_string(GetFPS()) + "  internal " + std::to_string(renderer_.InternalWidth()) + "x" + std::to_string(renderer_.InternalHeight()));
    line("map " + current_map_ + "  pos " + Fmt1(player_.pos.x) + ", " + Fmt1(player_.pos.y) + ", " + Fmt1(player_.pos.z) + "  yaw " + Fmt1(player_.yaw * RAD2DEG));
    line("props " + std::to_string(scene_.props.size()) + "  solids " + std::to_string(solids_.size()) + "  creatures " + std::to_string(scene_.creatures.size()) +
         "  projectiles " + std::to_string(scene_.projectiles.size()));
    int issues = 0;
    for (const auto& v : content_.validation_issues) issues += v.is_error ? 1 : 0;
    line("validation errors: " + std::to_string(issues) + "   [F5] hot reload", issues ? Color{255, 140, 120, 255} : Color{180, 255, 180, 255});
    static const char* states[] = {"idle", "patrol", "notice", "chase", "windup", "recover", "stagger", "search", "return", "dead"};
    for (const auto& c : scene_.creatures)
        line("  " + c.instance_id + " " + states[static_cast<int>(c.state)] + " hp " + std::to_string(c.health), Color{200, 200, 255, 255});
    const auto& log = Logger::GetRecentEntries();
    size_t start = log.size() > 8 ? log.size() - 8 : 0;
    for (size_t i = start; i < log.size(); i++) {
        std::string s = log[i].message.substr(0, 80);
        line(s, log[i].level == LogLevel::Info ? Color{200, 200, 200, 255} : Color{255, 170, 120, 255});
    }
}

} // namespace uncounted

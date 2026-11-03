#include "renderer/WorldRenderer.h"
#include "core/Logger.h"
#include "raymath.h"
#include "rlgl.h"
#include <algorithm>
#include <cmath>
#include <cstdio>

namespace uncounted {

static const char* kWorldVs = "assets/shaders/world_lit.vs";
static const char* kWorldFs = "assets/shaders/world_lit.fs";
static const char* kSpriteVs = "assets/shaders/sprite_lit.vs";
static const char* kSpriteFs = "assets/shaders/sprite_lit.fs";

Matrix AnchoredTransform(const BoundingBox& local, Vector3 pos, float rotYDeg, Vector3 scale) {
    Vector3 c = {(local.min.x + local.max.x) * 0.5f, local.min.y, (local.min.z + local.max.z) * 0.5f};
    Matrix m = MatrixTranslate(-c.x, -c.y, -c.z);
    m = MatrixMultiply(m, MatrixScale(scale.x, scale.y, scale.z));
    m = MatrixMultiply(m, MatrixRotateY(rotYDeg * DEG2RAD));
    m = MatrixMultiply(m, MatrixTranslate(pos.x, pos.y, pos.z));
    return m;
}

BoundingBox TransformBox(const BoundingBox& b, const Matrix& m) {
    Vector3 corners[8] = {
        {b.min.x, b.min.y, b.min.z}, {b.max.x, b.min.y, b.min.z}, {b.min.x, b.max.y, b.min.z}, {b.max.x, b.max.y, b.min.z},
        {b.min.x, b.min.y, b.max.z}, {b.max.x, b.min.y, b.max.z}, {b.min.x, b.max.y, b.max.z}, {b.max.x, b.max.y, b.max.z},
    };
    BoundingBox out = {{1e9f, 1e9f, 1e9f}, {-1e9f, -1e9f, -1e9f}};
    for (auto& c : corners) {
        Vector3 p = Vector3Transform(c, m);
        out.min = Vector3Min(out.min, p);
        out.max = Vector3Max(out.max, p);
    }
    return out;
}

static void ParseResolution(const GraphicsConfig& g, int& w, int& h) {
    w = GetScreenWidth();
    h = GetScreenHeight();
    if (g.internal_resolution == "native") return;
    int rw = 0, rh = 0;
    if (sscanf(g.internal_resolution.c_str(), "%dx%d", &rw, &rh) == 2 && rw > 0 && rh > 0) {
        w = rw;
        h = rh;
    }
}

bool WorldRenderer::Init(ResourceManager* res, const GraphicsConfig* gfx) {
    res_ = res;
    gfx_ = gfx;
    ReloadShaders();
    RecreateTargets();
    return world_shader_.id != 0;
}

void WorldRenderer::ResolveLocs(Shader s, ShaderLocs& l) {
    auto loc = [&](const char* a, const char* b) {
        int v = GetShaderLocation(s, a);
        if (v < 0 && b) v = GetShaderLocation(s, b);
        return v;
    };
    l.light_count = loc("uLightCount", nullptr);
    l.light_pos = loc("uLightPos[0]", "uLightPos");
    l.light_color = loc("uLightColor[0]", "uLightColor");
    l.light_radius = loc("uLightRadius[0]", "uLightRadius");
    l.view_pos = loc("uViewPos", nullptr);
    l.ambient = loc("uAmbientColor", nullptr);
    l.sun_dir = loc("uSunDir", nullptr);
    l.sun_color = loc("uSunColor", nullptr);
    l.fog_color = loc("uFogColor", nullptr);
    l.fog_density = loc("uFogDensity", nullptr);
    l.emissive = loc("uEmissive", nullptr);
    l.uv_scale = loc("uUvScale", nullptr);
}

void WorldRenderer::ReloadShaders() {
    if (world_shader_.id > 0 && world_shader_.id != rlGetShaderIdDefault()) UnloadShader(world_shader_);
    if (sprite_shader_.id > 0 && sprite_shader_.id != rlGetShaderIdDefault()) UnloadShader(sprite_shader_);

    world_shader_ = LoadShader(res_->Resolve(kWorldVs).c_str(), res_->Resolve(kWorldFs).c_str());
    if (world_shader_.id == 0 || world_shader_.id == rlGetShaderIdDefault()) {
        Logger::Error(std::string("World shader failed to compile/load: '") + kWorldVs + "' / '" + kWorldFs + "'. Using raylib default shader.");
    }
    sprite_shader_ = LoadShader(res_->Resolve(kSpriteVs).c_str(), res_->Resolve(kSpriteFs).c_str());
    if (sprite_shader_.id == 0 || sprite_shader_.id == rlGetShaderIdDefault()) {
        Logger::Error(std::string("Sprite shader failed to compile/load: '") + kSpriteVs + "' / '" + kSpriteFs + "'.");
    }
    ResolveLocs(world_shader_, wl_);
    ResolveLocs(sprite_shader_, sl_);
    res_->SetModelShader(world_shader_);
}

void WorldRenderer::RecreateTargets() {
    int w, h;
    ParseResolution(*gfx_, w, h);
    if (w == target_w_ && h == target_h_ && target_.id != 0) return;
    if (target_.id != 0) UnloadRenderTexture(target_);
    if (vm_target_.id != 0) UnloadRenderTexture(vm_target_);
    target_ = LoadRenderTexture(w, h);
    vm_target_ = LoadRenderTexture(w, h);
    int filter = gfx_->texture_filter == "nearest" ? TEXTURE_FILTER_POINT : TEXTURE_FILTER_BILINEAR;
    SetTextureFilter(target_.texture, filter);
    SetTextureFilter(vm_target_.texture, TEXTURE_FILTER_POINT);
    target_w_ = w;
    target_h_ = h;
}

void WorldRenderer::Shutdown() {
    if (target_.id != 0) UnloadRenderTexture(target_);
    if (vm_target_.id != 0) UnloadRenderTexture(vm_target_);
    target_ = {};
    vm_target_ = {};
    if (world_shader_.id > 0 && world_shader_.id != rlGetShaderIdDefault()) UnloadShader(world_shader_);
    if (sprite_shader_.id > 0 && sprite_shader_.id != rlGetShaderIdDefault()) UnloadShader(sprite_shader_);
    world_shader_ = {};
    sprite_shader_ = {};
}

void WorldRenderer::SetEmissive(Shader s, const ShaderLocs& l, float e) {
    if (l.emissive >= 0) SetShaderValue(s, l.emissive, &e, SHADER_UNIFORM_FLOAT);
}

void WorldRenderer::ApplyEnvironment(Shader s, const ShaderLocs& l, const RenderView& view, const MapDef* map, bool fog) {
    int count = gfx_->dynamic_lights_enabled ? static_cast<int>(std::min<size_t>(view.lights.size(), kMaxLights)) : 0;
    Vector3 pos[kMaxLights]{};
    Vector3 col[kMaxLights]{};
    float rad[kMaxLights]{};
    for (int i = 0; i < count; i++) {
        pos[i] = view.lights[i].pos;
        col[i] = view.lights[i].color;
        rad[i] = view.lights[i].radius;
    }
    SetShaderValue(s, l.light_count, &count, SHADER_UNIFORM_INT);
    if (count > 0) {
        SetShaderValueV(s, l.light_pos, pos, SHADER_UNIFORM_VEC3, count);
        SetShaderValueV(s, l.light_color, col, SHADER_UNIFORM_VEC3, count);
        SetShaderValueV(s, l.light_radius, rad, SHADER_UNIFORM_FLOAT, count);
    }
    Vector3 camPos = view.camera.position;
    SetShaderValue(s, l.view_pos, &camPos, SHADER_UNIFORM_VEC3);
    const Atmosphere& at = view.atmo;
    Vector3 amb = at.ambient;
    Vector3 sunDir = at.sun_dir;
    Vector3 sunCol = at.sun_color;
    Vector3 fogCol = at.fog_color;
    float fogD = (map && fog && gfx_->fog_enabled) ? at.fog_density : 0.0f;
    SetShaderValue(s, l.ambient, &amb, SHADER_UNIFORM_VEC3);
    if (l.sun_dir >= 0) SetShaderValue(s, l.sun_dir, &sunDir, SHADER_UNIFORM_VEC3);
    SetShaderValue(s, l.sun_color, &sunCol, SHADER_UNIFORM_VEC3);
    SetShaderValue(s, l.fog_color, &fogCol, SHADER_UNIFORM_VEC3);
    SetShaderValue(s, l.fog_density, &fogD, SHADER_UNIFORM_FLOAT);
    SetEmissive(s, l, 0.0f);
}

void WorldRenderer::DrawModelAt(const std::string& path, const Matrix& m, Vector2 uv, Color tint) {
    Model& model = res_->GetModel(path);
    if (wl_.uv_scale >= 0) SetShaderValue(world_shader_, wl_.uv_scale, &uv, SHADER_UNIFORM_VEC2);
    model.transform = m;
    DrawModel(model, {0, 0, 0}, 1.0f, tint);
    model.transform = MatrixIdentity();
}

static const char* AnimStateFor(const CreatureInstance& c) {
    switch (c.state) {
        case CreatureState::Dead: return "dead";
        case CreatureState::Stagger: return "stagger";
        case CreatureState::Windup: return "windup";
        case CreatureState::Recover: return c.state_timer > 0.0f && c.anim_time < 0.3f ? "attack" : "idle";
        default: return c.moving ? "walk" : "idle";
    }
}

void WorldRenderer::DrawSprite8(const std::string& sheet, const std::string& animPath, const std::string& state, float animTime,
                                Vector3 feet, float yaw, float scale, const Camera3D& cam, Color tint) {
    Texture2D tex = res_->GetTexture(sheet);
    const SpriteAnimData& anim = res_->GetAnimData(animPath);
    auto it = anim.states.find(state);
    if (it == anim.states.end()) it = anim.states.find("idle");
    const SpriteAnimState& st = it->second;

    // Pick the direction column from the angle between the creature's facing and the camera.
    float toCam = atan2f(cam.position.x - feet.x, cam.position.z - feet.z);
    float rel = toCam - yaw;
    while (rel < 0) rel += 2.0f * PI;
    while (rel >= 2.0f * PI) rel -= 2.0f * PI;
    int dirs = std::max(1, anim.directions);
    int dir = static_cast<int>(std::floor(rel / (2.0f * PI / dirs) + 0.5f)) % dirs;

    int frame = 0;
    if (st.frames > 1 || st.rows.size() > 1) {
        int f = static_cast<int>(animTime * st.fps);
        int total = std::max(st.frames, static_cast<int>(st.rows.size()));
        frame = st.loop ? f % total : std::min(f, total - 1);
    }
    int row = st.rows.empty() ? 0 : st.rows[frame % st.rows.size()];
    int col = dir;
    if (st.fixed_col >= 0) col = st.fixed_col;
    else if (state == "stagger") col = st.col_offset + dir / 2; // stagger strip only holds 4 facings
    else col += st.col_offset;

    Rectangle src = {static_cast<float>(col * anim.frame_width), static_cast<float>(row * anim.frame_height),
                     static_cast<float>(anim.frame_width), static_cast<float>(anim.frame_height)};
    float h = scale;
    float w = scale * static_cast<float>(anim.frame_width) / static_cast<float>(anim.frame_height);
    Vector2 origin = {w * anim.pivot.x, h * (1.0f - anim.pivot.y)};
    DrawBillboardPro(cam, tex, src, feet, {0, 1, 0}, {w, h}, origin, 0.0f, tint);
}

void WorldRenderer::Render(const Scene& scene, const RenderView& view, const MapDef* map) {
    RecreateTargets();

    if (view.show_viewmodel) RenderViewModel(view, map);

    BeginTextureMode(target_);
    ClearBackground(map ? view.atmo.sky : Color{10, 10, 16, 255});
    if (map) {
        // Sky gradient: zenith colour fading into the fog colour at the (pitch-dependent) horizon.
        Vector3 dir = Vector3Normalize(Vector3Subtract(view.camera.target, view.camera.position));
        float pitch = asinf(Clamp(dir.y, -1.0f, 1.0f));
        float th = static_cast<float>(target_.texture.height);
        float horizon = th * 0.5f + tanf(pitch) / tanf(view.camera.fovy * 0.5f * DEG2RAD) * th * 0.5f;
        Color fogC = {static_cast<unsigned char>(Clamp(view.atmo.fog_color.x * 255.0f, 0.0f, 255.0f)),
                      static_cast<unsigned char>(Clamp(view.atmo.fog_color.y * 255.0f, 0.0f, 255.0f)),
                      static_cast<unsigned char>(Clamp(view.atmo.fog_color.z * 255.0f, 0.0f, 255.0f)), 255};
        int tw = target_.texture.width;
        int hy = static_cast<int>(horizon);
        int top = hy - static_cast<int>(th * 0.9f);
        DrawRectangleGradientV(0, top, tw, hy - top, view.atmo.sky, fogC);
        if (hy < th) DrawRectangle(0, hy, tw, static_cast<int>(th) - hy + 1, fogC);
    }
    BeginMode3D(view.camera);

    ApplyEnvironment(world_shader_, wl_, view, map, true);

    // --- Static architecture & props
    for (const auto& p : scene.props) DrawModelAt(p.model_path, p.transform, p.uv_scale);

    // --- Interactables
    Vector2 one = {1, 1};
    for (const auto& in : scene.interactables) {
        if (in.def.model.empty()) continue;
        Matrix m = in.base_transform;
        const std::string& t = in.def.type;
        BoundingBox lb = res_->GetModelBounds(in.def.model);
        if (t == "door") {
            if (in.def.model.find("gate") != std::string::npos) {
                m = MatrixMultiply(m, MatrixTranslate(0, in.open_anim * 2.7f, 0));
            } else {
                float hw = (lb.max.x - lb.min.x) * 0.5f;
                Matrix anchor = AnchoredTransform(lb, {0, 0, 0}, 0, {1, 1, 1});
                Matrix swing = MatrixMultiply(MatrixTranslate(-hw, 0, 0), MatrixRotateY(-in.open_anim * 100.0f * DEG2RAD));
                swing = MatrixMultiply(swing, MatrixTranslate(hw, 0, 0));
                m = MatrixMultiply(MatrixMultiply(anchor, swing),
                                   MatrixMultiply(MatrixRotateY(in.def.rot_y * DEG2RAD), MatrixTranslate(in.def.pos.x, in.def.pos.y, in.def.pos.z)));
            }
        } else if (t == "lever") {
            Matrix anchor = AnchoredTransform(lb, {0, 0, 0}, 0, {1, 1, 1});
            float ang = (in.open_anim * 2.0f - 1.0f) * 35.0f;
            m = MatrixMultiply(MatrixMultiply(anchor, MatrixRotateX(ang * DEG2RAD)),
                               MatrixMultiply(MatrixRotateY(in.def.rot_y * DEG2RAD), MatrixTranslate(in.def.pos.x, in.def.pos.y, in.def.pos.z)));
        } else if (t == "pressure_plate") {
            m = MatrixMultiply(m, MatrixTranslate(0, -0.06f * in.open_anim, 0));
        }
        Color tint = WHITE;
        if (t == "chest" && in.used) tint = Color{170, 160, 150, 255};
        if (t == "quest_pedestal" && !in.used) {
            float pulse = 0.5f + 0.5f * sinf(view.time * 3.0f);
            tint = Color{static_cast<unsigned char>(220 + 35 * pulse), static_cast<unsigned char>(215 + 40 * pulse), 255, 255};
        }
        DrawModelAt(in.def.model, m, one, tint);
    }

    // --- GLB creatures
    for (const auto& c : scene.creatures) {
        if (!c.def || c.def->appearance.type != "model_glb") continue;
        BoundingBox lb = res_->GetModelBounds(c.def->appearance.model);
        float s = c.def->appearance.scale;
        Matrix m = AnchoredTransform(lb, {0, 0, 0}, 0, {s, s, s});
        if (c.state == CreatureState::Dead) {
            m = MatrixMultiply(m, MatrixRotateX(-85.0f * DEG2RAD));
            m = MatrixMultiply(m, MatrixTranslate(0, 0.3f, 0));
        } else if (c.state == CreatureState::Windup) {
            m = MatrixMultiply(m, MatrixRotateX(-12.0f * DEG2RAD));
        } else if (c.moving) {
            m = MatrixMultiply(m, MatrixTranslate(0, fabsf(sinf(c.anim_time * 7.0f)) * 0.06f, 0));
        }
        m = MatrixMultiply(m, MatrixRotateY(c.yaw));
        m = MatrixMultiply(m, MatrixTranslate(c.pos.x, c.pos.y, c.pos.z));
        Color tint = c.hit_flash > 0 ? Color{255, 90, 90, 255} : WHITE;
        DrawModelAt(c.def->appearance.model, m, one, tint);
    }

    // --- Arrows in flight and stuck in geometry
    auto drawArrow = [&](const std::string& model, Vector3 pos, Vector3 dir) {
        Vector3 d = Vector3Normalize(dir);
        Vector3 up = {0, 1, 0};
        Vector3 axis = Vector3CrossProduct(up, d);
        float ang = acosf(Clamp(Vector3DotProduct(up, d), -1.0f, 1.0f));
        Matrix rot = Vector3Length(axis) < 1e-4f ? (d.y < 0 ? MatrixRotateX(PI) : MatrixIdentity()) : MatrixRotate(Vector3Normalize(axis), ang);
        BoundingBox lb = res_->GetModelBounds(model);
        Vector3 c = Vector3Scale(Vector3Add(lb.min, lb.max), 0.5f);
        Matrix m = MatrixMultiply(MatrixTranslate(-c.x, -lb.max.y + 0.05f, -c.z), rot);
        m = MatrixMultiply(m, MatrixTranslate(pos.x, pos.y, pos.z));
        DrawModelAt(model, m, one);
    };
    for (const auto& pr : scene.projectiles) {
        if (pr.alive && !pr.model.empty()) drawArrow(pr.model, pr.pos, pr.vel);
    }

    for (const auto& pk : scene.pickups) {
        // Item models are reused as world pickups; normalise them so crates/rings read as hand-held loot.
        const std::string& model = pk.model;
        if (model.empty()) continue;
        if (pk.stuck) {
            drawArrow(model, pk.pos, pk.dir);
            continue;
        }
        BoundingBox lb = res_->GetModelBounds(model);
        Vector3 size = Vector3Subtract(lb.max, lb.min);
        float maxDim = std::max(size.x, std::max(size.y, size.z));
        float s = maxDim > 0.0001f ? std::min(1.0f, 0.5f / maxDim) : 1.0f;
        float bob = sinf(view.time * 2.0f + pk.spin) * 0.05f;
        Matrix m = AnchoredTransform(lb, {pk.pos.x, pk.pos.y + 0.08f + bob, pk.pos.z}, view.time * 60.0f + pk.spin * 57.0f, {s, s, s});
        DrawModelAt(model, m, one);
    }

    // --- Billboard sprites (creatures, NPCs, spell projectiles), sorted back-to-front
    struct SpriteDraw {
        float dist;
        int kind; // 0 creature, 1 npc, 2 projectile
        size_t index;
    };
    std::vector<SpriteDraw> sprites;
    Vector3 cam = view.camera.position;
    for (size_t i = 0; i < scene.creatures.size(); i++) {
        const auto& c = scene.creatures[i];
        if (c.def && c.def->appearance.type == "sprite_8dir") sprites.push_back({Vector3DistanceSqr(cam, c.pos), 0, i});
    }
    for (size_t i = 0; i < scene.npcs.size(); i++) {
        if (scene.npcs[i].def && !scene.npcs[i].hidden) sprites.push_back({Vector3DistanceSqr(cam, scene.npcs[i].pos), 1, i});
    }
    for (size_t i = 0; i < scene.projectiles.size(); i++) {
        const auto& p = scene.projectiles[i];
        if (p.alive && !p.sprite.empty()) sprites.push_back({Vector3DistanceSqr(cam, p.pos), 2, i});
    }
    std::sort(sprites.begin(), sprites.end(), [](const SpriteDraw& a, const SpriteDraw& b) { return a.dist > b.dist; });

    // Soft contact shadows ground the billboards.
    rlDisableDepthMask();
    for (const auto& c : scene.creatures) {
        if (!c.def || c.state == CreatureState::Dead) continue;
        DrawCylinder({c.pos.x, c.pos.y + 0.015f, c.pos.z}, c.radius * 1.25f, c.radius * 1.25f, 0.005f, 14, Color{0, 0, 0, 90});
    }
    for (const auto& n : scene.npcs)
        if (!n.hidden) DrawCylinder({n.pos.x, n.pos.y + 0.015f, n.pos.z}, 0.32f, 0.32f, 0.005f, 14, Color{0, 0, 0, 90});
    rlDrawRenderBatchActive();
    rlEnableDepthMask();

    BeginShaderMode(sprite_shader_);
    ApplyEnvironment(sprite_shader_, sl_, view, map, true);
    float emissive = 0.0f;
    for (const auto& sd : sprites) {
        if (sd.kind == 0) {
            const auto& c = scene.creatures[sd.index];
            Color tint = c.hit_flash > 0 ? Color{255, 110, 110, 255} : WHITE;
            float t = (c.state == CreatureState::Recover) ? c.anim_time : c.anim_time;
            if (emissive != 0.0f) { rlDrawRenderBatchActive(); emissive = 0.0f; SetEmissive(sprite_shader_, sl_, 0.0f); }
            DrawSprite8(c.def->appearance.sprite_sheet, c.def->appearance.animation_data, AnimStateFor(c), t, c.pos, c.yaw,
                        c.def->appearance.scale, view.camera, tint);
        } else if (sd.kind == 1) {
            const auto& n = scene.npcs[sd.index];
            if (emissive != 0.0f) { rlDrawRenderBatchActive(); emissive = 0.0f; SetEmissive(sprite_shader_, sl_, 0.0f); }
            Color tint = WHITE;
            if (n.def->id.find("spirit") != std::string::npos) tint = Color{200, 230, 255, 255};
            DrawSprite8(n.def->appearance.sprite_sheet, n.def->appearance.animation_data, n.anim, n.anim_time, n.pos, n.yaw,
                        n.def->appearance.scale, view.camera, tint);
        } else {
            const auto& p = scene.projectiles[sd.index];
            if (emissive != 1.0f) { rlDrawRenderBatchActive(); emissive = 1.0f; SetEmissive(sprite_shader_, sl_, 1.0f); }
            Texture2D tex = res_->GetTexture(p.sprite);
            int frames = std::max(1, tex.width / std::max(1, tex.height));
            int f = static_cast<int>(p.age * 14.0f) % frames;
            float fw = static_cast<float>(tex.width) / frames;
            Rectangle src = {f * fw, 0, fw, static_cast<float>(tex.height)};
            DrawBillboardRec(view.camera, tex, src, p.pos, {0.55f, 0.55f}, WHITE);
        }
    }
    rlDrawRenderBatchActive();

    // Flames and other prop emitters (always emissive).
    SetEmissive(sprite_shader_, sl_, 1.0f);
    for (const auto& e : scene.emitters) {
        Texture2D tex = res_->GetTexture(e.sprite);
        int frames = std::max(1, tex.width / std::max(1, tex.height));
        float fw = static_cast<float>(tex.width) / frames;
        int f = static_cast<int>(view.time * 10.0f + e.phase * 7.0f) % frames;
        float flick = 1.0f + 0.08f * sinf(view.time * 17.0f + e.phase * 5.0f);
        DrawBillboardRec(view.camera, tex, {f * fw, 0, fw, static_cast<float>(tex.height)}, e.pos, {e.size * flick, e.size * flick}, WHITE);
    }
    rlDrawRenderBatchActive();

    // Particles: a 1x1 white texel scaled into small squares.
    Texture2D white = {rlGetTextureIdDefault(), 1, 1, 1, PIXELFORMAT_UNCOMPRESSED_R8G8B8A8};
    for (int pass = 0; pass < 2; pass++) {
        SetEmissive(sprite_shader_, sl_, pass == 1 ? 1.0f : 0.0f);
        for (const auto& pt : scene.particles) {
            if (pt.glow != (pass == 1)) continue;
            float k = Clamp(pt.life / pt.max_life, 0.0f, 1.0f);
            DrawBillboardRec(view.camera, white, {0, 0, 1, 1}, pt.pos, {pt.size * (0.5f + 0.5f * k), pt.size * (0.5f + 0.5f * k)}, pt.color);
        }
        rlDrawRenderBatchActive();
    }

    // Weather
    if (map && view.atmo.weather == "dust") {
        SetEmissive(sprite_shader_, sl_, 0.55f);
        Vector3 c = view.camera.position;
        for (int i = 0; i < 90; i++) {
            float h1 = fmodf(sinf(i * 12.9898f) * 43758.5453f, 1.0f), h2 = fmodf(sinf(i * 78.233f) * 12345.678f, 1.0f), h3 = fmodf(sinf(i * 39.42f) * 24634.63f, 1.0f);
            h1 = fabsf(h1); h2 = fabsf(h2); h3 = fabsf(h3);
            float span = 9.0f;
            float x = c.x - span + fmodf(h1 * span * 2 - c.x + span * 64 + sinf(view.time * 0.3f + i) * 0.4f, span * 2.0f);
            float z = c.z - span + fmodf(h2 * span * 2 - c.z + span * 64 + cosf(view.time * 0.25f + i) * 0.4f, span * 2.0f);
            float y = 0.3f + fmodf(h3 * 3.6f + view.time * 0.05f * (0.5f + h1), 3.6f);
            DrawBillboardRec(view.camera, white, {0, 0, 1, 1}, {x, y, z}, {0.022f, 0.022f}, Color{200, 205, 190, 140});
        }
        rlDrawRenderBatchActive();
    }
    SetEmissive(sprite_shader_, sl_, 0.0f);
    EndShaderMode();

    if (map && view.atmo.weather == "rain") {
        // Streaks recycle through a box around the camera; drops under a roof are skipped.
        Vector3 c = view.camera.position;
        Color rc = {150, 165, 200, 110};
        for (int i = 0; i < 520; i++) {
            float h1 = fabsf(fmodf(sinf(i * 12.9898f) * 43758.5453f, 1.0f));
            float h2 = fabsf(fmodf(sinf(i * 78.233f) * 12345.678f, 1.0f));
            float h3 = fabsf(fmodf(sinf(i * 39.42f) * 24634.63f, 1.0f));
            float span = 14.0f;
            float x = c.x - span + fmodf(h1 * span * 2 - c.x + span * 64, span * 2.0f);
            float z = c.z - span + fmodf(h2 * span * 2 - c.z + span * 64, span * 2.0f);
            float y = c.y - 2.0f + fmodf(h3 * 9.0f - view.time * 11.0f + 900.0f, 9.0f);
            bool covered = false;
            for (const auto& p : scene.props) {
                const BoundingBox& b = p.world_box;
                if (!p.walkable || b.min.y < 2.0f) continue;
                if (x > b.min.x && x < b.max.x && z > b.min.z && z < b.max.z && y < b.min.y) { covered = true; break; }
            }
            if (covered || y < 0.0f) continue;
            DrawLine3D({x, y, z}, {x + 0.03f, y + 0.45f, z + 0.02f}, rc);
        }
        rlDrawRenderBatchActive();
    }

    EndMode3D();

    if (view.show_viewmodel) {
        DrawTextureRec(vm_target_.texture, {0, 0, static_cast<float>(vm_target_.texture.width), -static_cast<float>(vm_target_.texture.height)},
                       {0, 0}, WHITE);
    }
    EndTextureMode();
}

void WorldRenderer::RenderViewModel(const RenderView& view, const MapDef* map) {
    const ViewModelState& vm = view.vm;
    BeginTextureMode(vm_target_);
    ClearBackground(BLANK);

    Camera3D cam{};
    cam.position = {0, 0, 0};
    cam.target = {0, 0, -1};
    cam.up = {0, 1, 0};
    cam.fovy = 62.0f;
    cam.projection = CAMERA_PERSPECTIVE;
    BeginMode3D(cam);

    // Viewmodel is lit by the light sampled at the player's position, without fog.
    RenderView lit = view;
    lit.lights.clear();
    lit.camera = cam;
    ApplyEnvironment(world_shader_, wl_, lit, map, false);
    Vector3 amb = Vector3Add(view.light_at_player, Vector3Scale(vm.cast_color, vm.cast_flash * 0.8f));
    SetShaderValue(world_shader_, wl_.ambient, &amb, SHADER_UNIFORM_VEC3);
    Vector3 sunDir = {0.3f, 0.8f, 0.5f};
    Vector3 sunCol = Vector3Scale(view.light_at_player, 0.35f);
    if (wl_.sun_dir >= 0) SetShaderValue(world_shader_, wl_.sun_dir, &sunDir, SHADER_UNIFORM_VEC3);
    SetShaderValue(world_shader_, wl_.sun_color, &sunCol, SHADER_UNIFORM_VEC3);

    Vector2 one = {1, 1};
    float bx = vm.bob_x, by = vm.bob_y;

    if (!vm.main_model.empty()) {
        BoundingBox lb = res_->GetModelBounds(vm.main_model);
        // Grip point: slightly above the bottom of the model (handle end).
        Vector3 grip = {(lb.min.x + lb.max.x) * 0.5f, lb.min.y + 0.1f, (lb.min.z + lb.max.z) * 0.5f};
        Matrix m = MatrixMultiply(MatrixTranslate(-grip.x, -grip.y, -grip.z), MatrixScale(0.75f, 0.75f, 0.75f));
        if (vm.ranged) {
            // Bow held upright left of centre (string facing the eye), raised and pulled in while drawing.
            float d = vm.draw;
            Vector3 c = Vector3Scale(Vector3Add(lb.min, lb.max), 0.5f);
            m = MatrixMultiply(MatrixTranslate(-c.x, -c.y, -c.z), MatrixScale(0.55f, 0.55f, 0.55f));
            m = MatrixMultiply(m, MatrixRotateY(90.0f * DEG2RAD));
            m = MatrixMultiply(m, MatrixRotateZ((-18.0f + d * 14.0f) * DEG2RAD));
            m = MatrixMultiply(m, MatrixTranslate(Lerp(-0.34f, -0.12f, d) + bx, Lerp(-0.2f, -0.06f, d) + by, -0.72f));
            DrawModelAt(vm.main_model, m, one);
            if (d > 0.05f && !vm.ammo_model.empty()) {
                BoundingBox ab = res_->GetModelBounds(vm.ammo_model);
                Matrix am = MatrixTranslate(-(ab.min.x + ab.max.x) * 0.5f, -ab.max.y, -(ab.min.z + ab.max.z) * 0.5f);
                am = MatrixMultiply(am, MatrixRotateX(-90.0f * DEG2RAD));
                am = MatrixMultiply(am, MatrixScale(0.6f, 0.6f, 0.6f));
                am = MatrixMultiply(am, MatrixTranslate(Lerp(-0.3f, -0.1f, d) + bx, Lerp(-0.2f, -0.07f, d) + by, -0.95f + d * 0.22f));
                DrawModelAt(vm.ammo_model, am, one);
            }
        } else {
            float rx = -35.0f, rz = -18.0f, ry = 0.0f;
            float px = 0.36f, py = -0.44f, pz = -0.72f;
            if (vm.swing >= 0.0f) {
                float s = vm.swing;
                if (s < 0.25f) {
                    float k = s / 0.25f;
                    rx = Lerp(-35.0f, 20.0f, k);
                    rz = Lerp(-18.0f, 35.0f, k);
                    px = Lerp(0.36f, 0.42f, k);
                    py = Lerp(-0.42f, -0.28f, k);
                } else if (s < 0.6f) {
                    float k = (s - 0.25f) / 0.35f;
                    k = 1.0f - (1.0f - k) * (1.0f - k);
                    rx = Lerp(20.0f, -95.0f, k);
                    rz = Lerp(35.0f, -55.0f, k);
                    ry = Lerp(0.0f, -25.0f, k);
                    px = Lerp(0.42f, -0.05f, k);
                    py = Lerp(-0.28f, -0.48f, k);
                    pz = Lerp(-0.62f, -0.75f, k);
                } else {
                    float k = (s - 0.6f) / 0.4f;
                    rx = Lerp(-95.0f, -35.0f, k);
                    rz = Lerp(-55.0f, -18.0f, k);
                    ry = Lerp(-25.0f, 0.0f, k);
                    px = Lerp(-0.05f, 0.36f, k);
                    py = Lerp(-0.48f, -0.42f, k);
                    pz = Lerp(-0.75f, -0.62f, k);
                }
            } else if (vm.charge > 0.0f) {
                rx = Lerp(-35.0f, 30.0f, vm.charge);
                rz = Lerp(-18.0f, 45.0f, vm.charge);
                py = Lerp(-0.42f, -0.25f, vm.charge);
            } else if (vm.block > 0.0f && vm.off_model.empty()) {
                rx = Lerp(-35.0f, 5.0f, vm.block);
                rz = Lerp(-18.0f, 80.0f, vm.block);
                px = Lerp(0.36f, 0.1f, vm.block);
                py = Lerp(-0.42f, -0.22f, vm.block);
            }
            m = MatrixMultiply(m, MatrixRotateX(rx * DEG2RAD));
            m = MatrixMultiply(m, MatrixRotateZ(rz * DEG2RAD));
            m = MatrixMultiply(m, MatrixRotateY(ry * DEG2RAD));
            m = MatrixMultiply(m, MatrixTranslate(px + bx, py + by, pz));
            DrawModelAt(vm.main_model, m, one);
        }
    }

    if (!vm.off_model.empty() && !vm.ranged) {
        BoundingBox lb = res_->GetModelBounds(vm.off_model);
        Vector3 c = Vector3Scale(Vector3Add(lb.min, lb.max), 0.5f);
        float b = vm.block;
        Matrix m = MatrixMultiply(MatrixTranslate(-c.x, -c.y, -c.z), MatrixScale(0.7f, 0.7f, 0.7f));
        m = MatrixMultiply(m, MatrixRotateY(Lerp(68.0f, 10.0f, b) * DEG2RAD));
        m = MatrixMultiply(m, MatrixTranslate(Lerp(-0.74f, -0.16f, b) + bx * 0.6f, Lerp(-0.66f, -0.24f, b) + by * 0.6f, Lerp(-0.9f, -0.62f, b)));
        DrawModelAt(vm.off_model, m, one);
    }

    // Spell flash: an emissive sprite in the casting hand.
    if (vm.cast_flash > 0.01f && !vm.cast_sprite.empty()) {
        BeginShaderMode(sprite_shader_);
        ApplyEnvironment(sprite_shader_, sl_, lit, map, false);
        SetEmissive(sprite_shader_, sl_, 1.0f);
        Texture2D tex = res_->GetTexture(vm.cast_sprite);
        int frames = std::max(1, tex.width / std::max(1, tex.height));
        float fw = static_cast<float>(tex.width) / frames;
        int f = static_cast<int>(view.time * 14.0f) % frames;
        float sz = 0.18f + 0.12f * vm.cast_flash;
        unsigned char a = static_cast<unsigned char>(255 * Clamp(vm.cast_flash * 1.5f, 0.0f, 1.0f));
        DrawBillboardRec(cam, tex, {f * fw, 0, fw, static_cast<float>(tex.height)}, {-0.28f + bx, -0.3f + by, -0.6f}, {sz, sz}, Color{255, 255, 255, a});
        rlDrawRenderBatchActive();
        SetEmissive(sprite_shader_, sl_, 0.0f);
        EndShaderMode();
    }

    EndMode3D();
    EndTextureMode();
}

void WorldRenderer::BlitToScreen() {
    float sw = static_cast<float>(GetScreenWidth());
    float sh = static_cast<float>(GetScreenHeight());
    float tw = static_cast<float>(target_.texture.width);
    float th = static_cast<float>(target_.texture.height);
    float scale = std::min(sw / tw, sh / th);
    if (gfx_->integer_scaling && scale >= 1.0f) scale = std::floor(scale);
    float dw = tw * scale, dh = th * scale;
    Rectangle src = {0, 0, tw, -th};
    Rectangle dst = {(sw - dw) * 0.5f, (sh - dh) * 0.5f, dw, dh};
    DrawTexturePro(target_.texture, src, dst, {0, 0}, 0.0f, WHITE);
}

} // namespace uncounted

#pragma once

#include <unordered_map>
#include "core/Types.h"
#include "resource/ResourceManager.h"
#include "world/Scene.h"
#include <string>
#include <vector>

namespace uncounted {

class ContentRegistry;

// First-person viewmodel pose, driven by the gameplay layer each frame.
struct ViewModelState {
    std::string main_model;   // equipped main-hand world model (empty = bare hands)
    std::string off_model;    // equipped off-hand model (shield)
    std::string ammo_model;   // nocked arrow while drawing a bow
    bool ranged = false;
    float swing = -1.0f;      // 0..1 attack progress, <0 when idle
    bool heavy = false;
    float charge = 0.0f;      // heavy-attack wind-up 0..1
    float draw = 0.0f;        // bow draw 0..1
    float block = 0.0f;       // block raise 0..1
    float bob_x = 0.0f;
    float bob_y = 0.0f;
    float cast_flash = 0.0f;  // 0..1 hand glow after casting
    Vector3 cast_color = {1.0f, 0.7f, 0.3f};
    std::string cast_sprite;
};

// Blended environment at the camera (from the map's zones).
struct Atmosphere {
    Color sky = {20, 24, 36, 255};
    Vector3 ambient = {0.4f, 0.42f, 0.5f};
    Vector3 sun_dir = {-0.3f, 0.8f, -0.3f};
    Vector3 sun_color = {0.5f, 0.5f, 0.6f};
    Vector3 fog_color = {0.08f, 0.10f, 0.16f};
    float fog_density = 0.025f;
    std::string weather;
    std::string sky_panorama;   // horizon image for the dominant zone ("" = none)
};

struct RenderView {
    Camera3D camera{};
    std::vector<SceneLight> lights; // already culled to the nearest MAX_LIGHTS
    Vector3 light_at_player = {0.5f, 0.5f, 0.5f};
    Atmosphere atmo;
    ViewModelState vm;
    bool show_viewmodel = true;
    float time = 0.0f;
};

// Places a model so that its bounding-box bottom-centre sits at `pos`, then rotates and scales it.
Matrix AnchoredTransform(const BoundingBox& local, Vector3 pos, float rotYDeg, Vector3 scale);
BoundingBox TransformBox(const BoundingBox& local, const Matrix& m);

class WorldRenderer {
public:
    static constexpr int kMaxLights = 16;

    bool Init(ResourceManager* res, const GraphicsConfig* gfx);
    void Shutdown();
    void ReloadShaders();
    void RecreateTargets();

    // Renders the 3D world + viewmodel into the internal-resolution target, then blits it to the window.
    void Render(const Scene& scene, const RenderView& view, const MapDef* map);
    void BlitToScreen();

    Shader WorldShader() const { return world_shader_; }
    int InternalWidth() const { return target_.texture.width; }
    int InternalHeight() const { return target_.texture.height; }

private:
    // Sky panorama: crossfades when the zone's image changes.
    void DrawScatter(const MapDef& map, const RenderView& view);
    void DrawPanorama(const std::string& path, float alpha, const RenderView& view, float yaw, float pitch, int tw, float th, Color tint);
    std::string pano_cur_, pano_prev_;
    float pano_fade_ = 1.0f, pano_last_time_ = 0.0f;
    ResourceManager* res_ = nullptr;
    const GraphicsConfig* gfx_ = nullptr;
    Shader world_shader_{};
    Shader sprite_shader_{};
    RenderTexture2D target_{};
    RenderTexture2D vm_target_{};
    int target_w_ = 0;
    int target_h_ = 0;

    struct ShaderLocs {
        int light_count = -1, light_pos = -1, light_color = -1, light_radius = -1;
        int view_pos = -1, ambient = -1, sun_dir = -1, sun_color = -1, fog_color = -1, fog_density = -1;
        int emissive = -1, uv_scale = -1, time = -1, sway = -1, wave = -1, water = -1;
    };
    Shader post_shader_{};
    int post_texel_ = -1, post_dither_ = -1, post_glow_ = -1, post_vignette_ = -1, post_effect_ = -1, post_time_ = -1, post_res_ = -1;
    float time_ = 0.0f;
    std::unordered_map<std::string, bool> water_textured_;  // water models given the water_surface texture
    std::unordered_map<std::string, int> motion_kind_;  // model path -> 0 none, 1 sway, 2 water, 3 tentacle
    ShaderLocs wl_{};
    ShaderLocs sl_{};

    void ResolveLocs(Shader s, ShaderLocs& l);
    void ApplyEnvironment(Shader s, const ShaderLocs& l, const RenderView& view, const MapDef* map, bool fog);
    void SetEmissive(Shader s, const ShaderLocs& l, float e);
    void DrawModelAt(const std::string& path, const Matrix& m, Vector2 uv, Color tint = WHITE);
    void DrawSprite8(const std::string& sheet, const std::string& animPath, const std::string& state, float animTime,
                     Vector3 feet, float yaw, float scale, const Camera3D& cam, Color tint);
    void RenderViewModel(const RenderView& view, const MapDef* map);
};

} // namespace uncounted

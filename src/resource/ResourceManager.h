#pragma once

#include "raylib.h"
#include <string>
#include <unordered_map>
#include <vector>

namespace uncounted {

// Sprite animation metadata parsed from assets/animations/*.json
struct SpriteAnimState {
    std::vector<int> rows;
    int frames = 1;
    float fps = 4.0f;
    bool loop = true;
    int col_offset = 0;
    int fixed_col = -1;
};

struct SpriteAnimData {
    int frame_width = 64;
    int frame_height = 64;
    int directions = 8;
    Vector2 pivot = {0.5f, 0.92f};
    std::unordered_map<std::string, SpriteAnimState> states;
};

// Central cache for every external asset. Missing files are logged with context and replaced by the
// external diagnostic fallbacks (assets/textures/diag_missing.png, assets/models/diag_missing.glb).
class ResourceManager {
public:
    void Init(const std::string& rootDir, bool pointFilter);
    void UnloadAll();

    std::string Resolve(const std::string& relPath) const;
    bool Exists(const std::string& relPath) const;

    Texture2D GetTexture(const std::string& relPath);
    Model& GetModel(const std::string& relPath);
    BoundingBox GetModelBounds(const std::string& relPath);
    const SpriteAnimData& GetAnimData(const std::string& relPath);
    Font GetFont(const std::string& relPath, int baseSize);

    // Every loaded and future model material uses this shader.
    void SetModelShader(Shader shader);

    void SetSfxVolume(float v) { sfx_volume_ = v; }
    void PlaySfx(const std::string& relPath, float volume = 1.0f, float pitch = 1.0f);
    // Recorded voice lines: assets/audio/voice/<line key>.ogg|.wav|.mp3 (the line's localization key, e.g.
    // comp.grout.idle.1.ogg). Plays it if it exists, cutting off the previous voice line; returns its length in seconds
    // (0 when there's no recording, so the game just shows the subtitle as usual).
    float PlayVoice(const std::string& lineKey);
    void SetVoiceVolume(float v) { voice_volume_ = v; }

    void SetPointFilter(bool point);

private:
    struct ModelEntry {
        Model model{};
        BoundingBox bounds{};
    };
    struct SoundEntry {
        std::vector<Sound> voices;
        size_t next = 0;
    };

    std::string root_ = ".";
    bool point_filter_ = true;
    float sfx_volume_ = 1.0f;
    float voice_volume_ = 1.0f;
    Sound voice_{};
    bool voice_loaded_ = false;
    Shader model_shader_{};
    bool has_model_shader_ = false;

    std::unordered_map<std::string, Texture2D> textures_;
    std::unordered_map<std::string, ModelEntry> models_;
    std::unordered_map<std::string, SpriteAnimData> anims_;
    std::unordered_map<std::string, Font> fonts_;
    std::unordered_map<std::string, SoundEntry> sounds_;
    std::unordered_map<std::string, bool> reported_missing_;

    void ReportMissing(const std::string& relPath, const std::string& kind);
    void PrepareModel(Model& model);
};

} // namespace uncounted

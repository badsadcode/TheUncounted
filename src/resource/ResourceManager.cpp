#include "resource/ResourceManager.h"
#include "core/Logger.h"
#include "nlohmann/json.hpp"
#include "raymath.h"
#include "rlgl.h"
#include <filesystem>
#include <fstream>

namespace fs = std::filesystem;
using json = nlohmann::json;

namespace uncounted {

static const char* kMissingTexture = "assets/textures/diag_missing.png";
static const char* kMissingModel = "assets/models/diag_missing.glb";

void ResourceManager::Init(const std::string& rootDir, bool pointFilter) {
    root_ = rootDir;
    point_filter_ = pointFilter;
}

std::string ResourceManager::Resolve(const std::string& relPath) const {
    return (fs::path(root_) / relPath).string();
}

bool ResourceManager::Exists(const std::string& relPath) const {
    if (relPath.empty()) return false;
    std::error_code ec;
    return fs::exists(fs::path(root_) / relPath, ec);
}

void ResourceManager::ReportMissing(const std::string& relPath, const std::string& kind) {
    if (reported_missing_[relPath]) return;
    reported_missing_[relPath] = true;
    Logger::Error("Missing or unreadable " + kind + " '" + relPath + "' - substituting diagnostic fallback asset.");
}

void ResourceManager::SetPointFilter(bool point) {
    point_filter_ = point;
    int filter = point ? TEXTURE_FILTER_POINT : TEXTURE_FILTER_BILINEAR;
    for (auto& [path, tex] : textures_) SetTextureFilter(tex, filter);
    for (auto& [path, entry] : models_) {
        for (int i = 0; i < entry.model.materialCount; i++) {
            Texture2D t = entry.model.materials[i].maps[MATERIAL_MAP_DIFFUSE].texture;
            if (t.id > 0) SetTextureFilter(t, filter);
        }
    }
}

Texture2D ResourceManager::GetTexture(const std::string& relPath) {
    auto it = textures_.find(relPath);
    if (it != textures_.end()) return it->second;

    Texture2D tex{};
    if (Exists(relPath)) tex = LoadTexture(Resolve(relPath).c_str());
    if (tex.id == 0) {
        ReportMissing(relPath, "texture");
        if (relPath != kMissingTexture) {
            tex = GetTexture(kMissingTexture);
            textures_[relPath] = tex;
            return tex;
        }
        return tex;
    }
    SetTextureFilter(tex, point_filter_ ? TEXTURE_FILTER_POINT : TEXTURE_FILTER_BILINEAR);
    SetTextureWrap(tex, TEXTURE_WRAP_REPEAT);
    textures_[relPath] = tex;
    return tex;
}

void ResourceManager::PrepareModel(Model& model) {
    for (int i = 0; i < model.materialCount; i++) {
        Texture2D& t = model.materials[i].maps[MATERIAL_MAP_DIFFUSE].texture;
        if (t.id > 0) {
            SetTextureFilter(t, point_filter_ ? TEXTURE_FILTER_POINT : TEXTURE_FILTER_BILINEAR);
            SetTextureWrap(t, TEXTURE_WRAP_REPEAT);
        }
        if (has_model_shader_) model.materials[i].shader = model_shader_;
    }
}

Model& ResourceManager::GetModel(const std::string& relPath) {
    auto it = models_.find(relPath);
    if (it != models_.end()) return it->second.model;

    ModelEntry entry;
    if (Exists(relPath)) entry.model = LoadModel(Resolve(relPath).c_str());
    if (entry.model.meshCount == 0) {
        ReportMissing(relPath, "model");
        if (relPath != kMissingModel) {
            Model& fallback = GetModel(kMissingModel);
            ModelEntry alias;
            alias.model = fallback;
            alias.bounds = models_[kMissingModel].bounds;
            // Alias entries share GPU data with the fallback; they are never unloaded separately.
            models_[relPath] = alias;
            return models_[relPath].model;
        }
        // Even the diagnostic model is gone: fall back to a unit cube so the game remains debuggable.
        entry.model = LoadModelFromMesh(GenMeshCube(0.8f, 0.8f, 0.8f));
    }
    PrepareModel(entry.model);
    entry.bounds = GetModelBoundingBox(entry.model);
    models_[relPath] = entry;
    return models_[relPath].model;
}

BoundingBox ResourceManager::GetModelBounds(const std::string& relPath) {
    GetModel(relPath);
    return models_[relPath].bounds;
}

void ResourceManager::SetModelShader(Shader shader) {
    model_shader_ = shader;
    has_model_shader_ = true;
    for (auto& [path, entry] : models_) PrepareModel(entry.model);
}

const SpriteAnimData& ResourceManager::GetAnimData(const std::string& relPath) {
    auto it = anims_.find(relPath);
    if (it != anims_.end()) return it->second;

    SpriteAnimData data;
    std::ifstream ifs(Resolve(relPath));
    if (ifs.is_open()) {
        try {
            json j;
            ifs >> j;
            data.frame_width = j.value("frame_width", 64);
            data.frame_height = j.value("frame_height", 64);
            data.directions = j.value("directions", 8);
            if (j.contains("pivot") && j["pivot"].is_array() && j["pivot"].size() >= 2) {
                data.pivot = {j["pivot"][0].get<float>(), j["pivot"][1].get<float>()};
            }
            if (j.contains("states")) {
                for (auto st = j["states"].begin(); st != j["states"].end(); ++st) {
                    SpriteAnimState s;
                    const auto& sj = st.value();
                    if (sj.contains("rows")) {
                        for (const auto& r : sj["rows"]) s.rows.push_back(r.get<int>());
                    } else {
                        s.rows.push_back(sj.value("row", 0));
                    }
                    s.frames = sj.value("frames", 1);
                    s.fps = sj.value("fps", 4.0f);
                    s.loop = sj.value("loop", true);
                    s.col_offset = sj.value("col_offset", 0);
                    s.fixed_col = sj.value("fixed_col", -1);
                    data.states[st.key()] = s;
                }
            }
        } catch (const std::exception& e) {
            Logger::Validation(relPath, "root", std::string("Animation JSON parse error: ") + e.what());
        }
    } else {
        ReportMissing(relPath, "animation data");
    }
    if (data.states.find("idle") == data.states.end()) {
        SpriteAnimState idle;
        idle.rows = {0};
        data.states["idle"] = idle;
    }
    anims_[relPath] = data;
    return anims_[relPath];
}

Font ResourceManager::GetFont(const std::string& relPath, int baseSize) {
    std::string key = relPath + "@" + std::to_string(baseSize);
    auto it = fonts_.find(key);
    if (it != fonts_.end()) return it->second;

    std::vector<int> codepoints;
    for (int c = 32; c < 127; c++) codepoints.push_back(c);
    for (int c = 0xA0; c <= 0xFF; c++) codepoints.push_back(c);
    for (int c : {0x2013, 0x2014, 0x2018, 0x2019, 0x201C, 0x201D, 0x2022, 0x2026}) codepoints.push_back(c);

    Font font{};
    if (Exists(relPath)) {
        font = LoadFontEx(Resolve(relPath).c_str(), baseSize, codepoints.data(), static_cast<int>(codepoints.size()));
    }
    if (font.texture.id == 0) {
        ReportMissing(relPath, "font");
        font = GetFontDefault();
    } else {
        SetTextureFilter(font.texture, TEXTURE_FILTER_BILINEAR);
    }
    fonts_[key] = font;
    return font;
}

void ResourceManager::PlaySfx(const std::string& relPath, float volume, float pitch) {
    if (relPath.empty() || !IsAudioDeviceReady()) return;
    auto it = sounds_.find(relPath);
    if (it == sounds_.end()) {
        SoundEntry entry;
        if (Exists(relPath)) {
            Sound base = LoadSound(Resolve(relPath).c_str());
            if (base.frameCount > 0) {
                entry.voices.push_back(base);
                for (int i = 0; i < 3; i++) entry.voices.push_back(LoadSoundAlias(base));
            }
        }
        if (entry.voices.empty()) ReportMissing(relPath, "sound");
        it = sounds_.emplace(relPath, std::move(entry)).first;
    }
    SoundEntry& se = it->second;
    if (se.voices.empty()) return;
    Sound& s = se.voices[se.next];
    se.next = (se.next + 1) % se.voices.size();
    SetSoundVolume(s, Clamp(volume * sfx_volume_, 0.0f, 1.0f));
    SetSoundPitch(s, pitch);
    PlaySound(s);
}

void ResourceManager::UnloadAll() {
    for (auto& [path, tex] : textures_) {
        if (path != kMissingTexture && tex.id > 0) {
            bool isAlias = false;
            auto miss = textures_.find(kMissingTexture);
            if (miss != textures_.end() && miss->second.id == tex.id) isAlias = true;
            if (!isAlias) UnloadTexture(tex);
        }
    }
    auto miss = textures_.find(kMissingTexture);
    if (miss != textures_.end() && miss->second.id > 0) UnloadTexture(miss->second);
    textures_.clear();

    unsigned int missingVao = 0;
    auto mm = models_.find(kMissingModel);
    if (mm != models_.end() && mm->second.model.meshCount > 0) missingVao = mm->second.model.meshes[0].vaoId;
    for (auto& [path, entry] : models_) {
        if (path == kMissingModel) continue;
        if (entry.model.meshCount > 0 && missingVao != 0 && entry.model.meshes[0].vaoId == missingVao) continue;
        // Keep the shader alive: it is owned by the renderer, not by individual models.
        for (int i = 0; i < entry.model.materialCount; i++) entry.model.materials[i].shader = Shader{rlGetShaderIdDefault(), nullptr};
        UnloadModel(entry.model);
    }
    if (mm != models_.end()) {
        for (int i = 0; i < mm->second.model.materialCount; i++) mm->second.model.materials[i].shader = Shader{rlGetShaderIdDefault(), nullptr};
        UnloadModel(mm->second.model);
    }
    models_.clear();

    for (auto& [key, font] : fonts_) {
        if (font.texture.id != GetFontDefault().texture.id) UnloadFont(font);
    }
    fonts_.clear();

    for (auto& [path, se] : sounds_) {
        for (size_t i = 1; i < se.voices.size(); i++) UnloadSoundAlias(se.voices[i]);
        if (!se.voices.empty()) UnloadSound(se.voices[0]);
    }
    sounds_.clear();
    anims_.clear();
    reported_missing_.clear();
}

} // namespace uncounted

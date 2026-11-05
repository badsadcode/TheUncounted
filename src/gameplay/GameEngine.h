#pragma once

#include "content/ContentRegistry.h"
#include "renderer/WorldRenderer.h"
#include "resource/ResourceManager.h"
#include "world/Scene.h"
#include <array>
#include <map>
#include <set>
#include <string>
#include <vector>
#include <deque>

namespace uncounted {

enum class Screen { Title, Creation, Playing, Dead, Ending, Credits, Opening };
enum class Overlay { None, Pause, Inventory, Character, Journal, Map, Dialogue, Shop, Container, Reader, Options, Narration, Crafting, Wait };

struct InvItem {
    std::string id;
    int qty = 1;
};

struct SkillState {
    int level = 5;
    float xp = 0.0f;
    double last_gain = -100.0;
};

struct ActiveBuff {
    std::string spell_id;
    std::string primitive;
    float remaining = 0.0f;
    float duration = 0.0f;
    float power = 0.0f;
    Vector3 light_color{};
    float light_radius = 0.0f;
    float visibility = 1.0f;
    std::string bonus_key;   // food buffs: named build bonus while active
    float bonus_value = 0.0f;
    std::string item_id;     // food buffs: what was eaten (HUD icon/name)
    std::string status;      // weapon oils: status applied by your hits while it lasts
    float status_chance = 0.0f, status_power = 0.0f, status_duration = 0.0f;
};

struct PlayerState {
    std::string name = "Nameless";
    std::string race_id, background_id, archetype_id;
    std::string portrait;   // chosen at creation (cosmetic); empty = the race's default
    float hour = 21.0f;     // time of day, 0-24 (a new game starts at nine in the evening)
    std::map<std::string, int> attributes; // permanent values (base + race + archetype + spent points)
    std::map<std::string, SkillState> skills;
    int level = 1;
    int xp = 0;
    int unspent_points = 0;
    float health = 60, stamina = 70, mana = 40;
    float sanity = 100.0f;         // 0..100; eldritch things wear it down, company and rest restore it
    int gold = 0;
    std::vector<InvItem> inventory;
    std::map<std::string, std::string> equipment; // slot -> item id
    std::vector<std::string> known_spells;
    std::set<std::string> perks;   // chosen perk ids (one per skill milestone)
    std::map<std::string, int> kills;  // creature id -> times defeated (the Bestiary)
    int selected_spell = 0;
    std::array<std::string, 4> quick_slots;
    std::vector<ActiveBuff> buffs;
    std::map<std::string, int> quest_stages;
    std::map<std::string, std::vector<int>> quest_log;
    std::set<std::string> flags;
    std::set<std::string> claimed; // one-time dialogue rewards
    std::vector<std::string> companions;  // NPC def ids of whoever travels with the player (party of up to kMaxCompanions)
    std::string tracked_quest;     // side quest shown on the HUD next to the main story
    double play_time = 0.0;

    Vector3 pos{};
    Vector3 vel{};
    float yaw = 0.0f;   // radians; forward = (sin yaw, 0, cos yaw)
    float pitch = 0.0f;
    bool on_ground = true;
    bool crouching = false;
    float eye_height = 1.6f;
};

struct ContainerState {
    bool generated = false;
    std::vector<InvItem> items;
    int gold = 0;
};

struct MapPersist {
    std::set<std::string> open;      // doors opened, levers pulled, plates pressed
    std::set<std::string> unlocked;
    std::set<std::string> used;      // pedestals claimed, pickups taken, chests opened
    std::set<std::string> dead;      // defeated creatures
    std::map<std::string, Vector3> corpse_pos;
    std::map<std::string, ContainerState> containers;
    std::map<std::string, double> harvested;   // harvest node -> play time it was picked
};

struct ToastMsg {
    std::string text;
    Color color;
    float time;
};

struct InteractTarget {
    enum Kind { None, Interactable, Npc, Corpse, Pickup, Portal } kind = None;
    int index = -1;
    std::string prompt;
};

class GameEngine {
public:
    bool Init(int argc, char** argv);
    void Run();
    void Shutdown();
    int RunSelfTest(); // headless quest walkthrough; returns number of failures
    bool SelfTestRequested() const { return selftest_; }
    void RunBalanceReport(); // headless archetype-vs-creature duels
    bool BalanceRequested() const { return balance_; }

private:
    friend class GameUI;

    // ---- subsystems
    ContentRegistry content_;
    ResourceManager res_;
    WorldRenderer renderer_;
    Scene scene_;

    // ---- state
    Screen screen_ = Screen::Title;
    Overlay overlay_ = Overlay::None;
    PlayerState player_;
    std::map<std::string, MapPersist> persist_;
    std::map<std::string, std::map<std::string, int>> vendor_sold_; // npc -> item -> sold count
    std::string current_map_;
    bool running_ = true;
    float sim_accum_ = 0.0f;
    float time_ = 0.0f;
    bool debug_overlay_ = false;
    bool selftest_ = false;
    bool balance_ = false;
    bool mute_ = false;
    int skip_mouse_frames_ = 0; // ignore the delta spike after the cursor is captured
    std::vector<ToastMsg> toasts_;
    // ---- story presentation
    std::string subtitle_speaker_, subtitle_text_;
    float subtitle_time_ = 0.0f;
    float bark_global_cd_ = 4.0f;
    std::map<std::string, float> bark_cd_;
    std::map<std::string, int> bark_next_;
    std::set<std::string> spoke_alert_;
    std::vector<std::string> narration_pages_;
    int narration_page_ = 0;
    float narration_time_ = 0.0f;
    bool narration_is_prologue_ = false;
    std::vector<std::string> narration_keys_;  // localization key per page: also the voice-over file name
    float intro_duck_ = 0.0f;                  // 0..1: how far the intro's audio mix (no ambience, quieter music) is faded in
    float narration_voice_ = 0.0f;             // length of the current page's recording (0 = none)
    void EnterNarrationPage();
    void StartNarration(const std::vector<std::string>& keys);
    void Say(const std::string& speaker, const std::string& text, float seconds = 0.0f, const std::string& voiceKey = "");
    void UpdateBarks(float dt);
    void AdvanceNarration();
    void DrawNarration();
    void DrawSubtitle();
    std::vector<std::string> QuestOrder() const;
    std::string region_banner_;
    float region_banner_time_ = 0.0f;
    std::string validation_summary_;
    std::string boot_shot_;      // --shot path: render a frame and exit (headless verification)
    int boot_shot_frames_ = 0;
    std::string boot_shot_overlay_;
    std::vector<std::string> boot_shot_flags_;
    float boot_shot_sanity_ = -1.0f;
    std::vector<std::string> boot_shot_companions_;

    // ---- combat/animation
    float attack_timer_ = -1.0f;    // >=0 while a swing is in progress
    float attack_duration_ = 0.5f;
    bool attack_heavy_ = false;
    bool attack_hit_done_ = false;
    float charge_time_ = 0.0f;
    bool charging_ = false;
    float bow_draw_ = 0.0f;
    bool drawing_bow_ = false;
    float block_amount_ = 0.0f;
    bool blocking_ = false;
    double block_start_ = -10.0;
    float stamina_delay_ = 0.0f;
    float spell_cooldown_ = 0.0f;
    float cast_flash_ = 0.0f;
    Vector3 cast_color_{1, 0.6f, 0.2f};
    std::string cast_sprite_;
    float damage_flash_ = 0.0f;
    float bob_phase_ = 0.0f;
    float step_timer_ = 0.0f;
    float sprint_accum_ = 0.0f;
    float sneak_accum_ = 0.0f;
    bool making_noise_ = false;
    std::string target_enemy_;
    float target_enemy_time_ = 0.0f;
    InteractTarget interact_;

    // ---- overlays
    std::string dialogue_id_;
    std::string dialogue_node_;
    int dialogue_npc_ = -1;
    std::string shop_npc_;
    std::string container_key_;
    std::string container_title_;
    std::string reader_title_;
    std::string reader_text_;
    float ui_scroll_ = 0.0f;
    // dialogue window: scroll offsets for the speech and the choices, the keyboard/pad highlight, and which page they belong to
    float dlg_text_scroll_ = 0.0f, dlg_choice_scroll_ = 0.0f;
    int dlg_sel_ = -1;
    std::string dlg_scroll_page_;
    int inv_filter_ = 0;
    int char_tab_ = 0;
    std::string journal_selected_;
    float journal_scroll_ = 0.0f;
    int death_tip_ = 0;
    bool ui_ignore_hover_ = false;   // screenshot previews: show the selected item, not whatever is under the cursor   // character screen: 0 overview, 1 combat sheet
    std::string inv_selected_;
    int creation_race_ = 0, creation_bg_ = 0, creation_arch_ = 0, creation_portrait_ = 0;
    std::vector<std::string> PortraitChoices(const RaceDef& r, const ArchetypeDef& a) const;
    const std::string& PlayerPortrait() const;
    // --- Day and night
    void AdvanceClock(float realSeconds);
    float Daylight() const;          // 0 night .. 1 day (outdoors)
    float Twilight() const;          // 0..1, strongest in the middle of dawn and dusk
    bool InHours(float from, float to) const;
    bool NightOutdoors() const { return night_outdoors_; }
    std::string WaitBlockedReason() const;
    void WaitUntil(float hour);
    void DrawWait();
    // --- The Audit: a challenge arena (waves, Forms, score, records)
    struct AuditRun {
        bool active = false;
        int wave = 0;            // current wave (1..kAuditWaves); 0 before the first
        float break_timer = 0;   // seconds until the next wave arrives
        int kills = 0;
        int score = 0;
        float damage_taken = 0;
        int form = 0;            // this wave's Form (modifier)
        int run = 0;
        unsigned seed = 1;
    } audit_;
    static constexpr int kAuditWaves = 10;
    std::deque<MapCreatureSpawnDef> audit_spawns_;
    void StartAudit();
    void EndAudit(bool victory);
    void UpdateAudit(float dt);
    void SpawnAuditWave();
    bool IsAuditCreature(const CreatureInstance& c) const { return c.instance_id.rfind("audit_", 0) == 0; }
    std::string AuditFormName(int form) const;
    std::string AuditRecordsText() const;
    // --- Gamepad: the first connected pad plays alongside mouse and keyboard; in menus the left stick moves the cursor
    bool pad_active_ = false;       // the pad was the last thing used (prompts show pad buttons)
    int Pad() const;                // index of the first connected gamepad, or -1
    bool PadDown(int button) const;
    bool PadPressed(int button) const;
    bool PadReleased(int button) const;
    float PadAxis(int axis) const;  // with a dead zone
    int PadButtonFor(const std::string& action) const;
    bool UiClick() const;           // left mouse button, or A on the pad
    bool UiRightClick() const;      // right mouse button, or X on the pad
    bool BackPressed() const;       // Escape, Start, or B while a menu is open
    void UpdateGamepad(float dt);
    Vector2 pad_cursor_ = {-1.0f, -1.0f};   // where the stick last put the cursor (so that move isn't taken for the mouse)
    bool night_outdoors_ = false;
    bool audit_balance_ = false;
    void RunAuditBalance();
    float boot_shot_hour_ = -1.0f;
    bool clean_shot_ = false;
    std::string creation_name_ = "Wren";
    bool options_from_title_ = false;
    int ending_stage_ = 0;
    bool ending_shown_ = false;
    // ---- credits (content/credits.json): from the title menu, and once after Chapter One's finale
    struct CreditEntry { std::string heading, style; std::vector<std::string> lines; int gap = 0; };
    std::vector<CreditEntry> credits_;
    float credits_time_ = 0.0f;
    Screen credits_return_ = Screen::Title;
    bool credits_pending_ = false;
    void LoadCredits();
    // the opening: after character creation, the logo on black for a few seconds, then the illustrated intro
    float opening_t_ = 0.0f;
    static constexpr float kOpeningEnd = 6.2f;
    void StartOpening();
    void DrawOpening();
    void StartCredits(Screen returnTo);
    void EndCredits();
    void DrawCredits();

    // ---- audio
    struct StreamTrack {
        Music music{};
        std::string path;
        bool is_music = true;
        float vol = 0.0f; // fade level 0..1 (multiplied by the configured volume)
    };
    std::vector<StreamTrack> streams_;
    std::string want_music_, want_ambience_;
    void SetWantedAudio(const std::string& music, const std::string& ambience);
    void UpdateAudio(float dt);

    // ---- zones / atmosphere
    Atmosphere atmo_;
    std::string zone_id_ = "?";
    Atmosphere ComputeAtmosphere(Vector3 p, const MapZoneDef** dominant) const;
    void UpdateAtmosphere(float dt, bool snap);
    const MapZoneDef* CurrentZone() const;

    // ---- setup / flow
    void ApplyAudioVolumes();
    void PlayMapAudio(const MapDef* map);
    void StopMapAudio();
    void NewGame();
    void LoadMap(const std::string& mapId, const std::string& spawnId, bool keepPosition = false);
    void BuildScene();
    void HotReload();
    void ReturnToTitle();

    // ---- frame update
    void Frame(float dt);
    void UpdatePlaying(float dt);
    void FixedUpdate(float dt);
    void HandleGameplayInput(float dt);
    void UpdatePlayerMovement(float dt);
    void UpdateCombat(float dt);
    void UpdateCreatures(float dt);
    void UpdateProjectiles(float dt);
    void UpdateWorldObjects(float dt);
    void UpdateBuffs(float dt);
    void UpdateInteractTarget();
    void Interact();
    void UseInteractTarget();   // use whatever interact_ points at (Interact() picks it first)
    void CheckPressurePlates();
    void UpdateParticles(float dt);
    void SpawnBurst(Vector3 pos, Color color, int count, float speed, bool glow, float gravity = 6.0f, float size = 0.05f);

    // ---- input bindings
    bool ActionDown(const std::string& name) const;
    bool ActionPressed(const std::string& name) const;
    bool ActionReleased(const std::string& name) const;
    std::string BindingLabel(const std::string& name) const;

    // ---- collision & queries
    std::vector<BoundingBox> solids_;
    std::vector<BoundingBox> walkables_;
    std::vector<std::pair<BoundingBox, int>> ramps_;
    void RebuildColliders();
    float GroundHeight(Vector3 pos, float stepHeight) const;
    Vector3 MoveWithCollision(Vector3 pos, Vector3 delta, float radius, float height, bool isPlayer, int selfCreature = -1);
    bool LineOfSight(Vector3 a, Vector3 b) const;
    bool SegmentHitsWorld(Vector3 a, Vector3 b, float& tHit, Vector3& normal) const;

    // ---- character
public:
    int Attr(const std::string& id) const;
    int SkillLevel(const std::string& id) const;
    float SkillEffect(const std::string& id) const;
    int MaxHealth() const;
    int MaxStamina() const;
    int MaxMana() const;
    float CarryCapacity() const;
    float CarriedWeight() const;
    int ArmorRating() const;
    float SynergyBonus(const std::string& key) const;
    float GearBonus(const std::string& key) const;   // "bonus" effects on equipped items
    float BuffBonus(const std::string& key) const;   // active food buffs
    float Bonus(const std::string& key) const;       // synergies + gear + food + perks
    float PerkBonus(const std::string& key) const;
    bool PerkAvailable(const PerkDef& p) const;       // skill high enough and no perk chosen at that milestone yet
    void ChoosePerk(const std::string& id);
    int PendingPerks() const;
    // Build maths shared by combat and the character sheet, so what you read is what you hit for.
    float MeleeHitDamage(const ItemDef* w, bool heavy) const;   // before crit, sneak, bane and enemy armour
    float ArrowHitDamage(const ItemDef* w, float draw) const;
    float CritChance(const ItemDef* w) const;
    float CritMult(const ItemDef* w) const;
    float SpellPowerMult(const SpellDef& s) const;
    float SpellCost(const SpellDef& s) const;
    float LockpickChance(int difficulty) const;
    float ShopDiscount() const;
    bool SynergyActive(const SynergyDef& s) const;
    float MoveSpeed() const;
    float Visibility() const;
    const ItemDef* Equipped(const std::string& slot) const;
private:
    void GainSkillXp(const std::string& skill, float amount, bool bypassCooldown = false);
    void GainXp(int amount);
    void ClampVitals();

    // ---- inventory
public:
    int CountItem(const std::string& id) const;
    bool IsEquipped(const std::string& id) const;
private:
    void AddItem(const std::string& id, int qty, bool announce = true);
    bool RemoveItem(const std::string& id, int qty);
    void EquipItem(const std::string& id);
    void UnequipSlot(const std::string& slot);
    void UseItem(const std::string& id);
    void UseQuickSlot(int index);
    void ReadItem(const ItemDef& item);

    // ---- combat
    void StartAttack(bool heavy);
    void ResolveMeleeHit();
    // Companion
    void UpdateCompanion(float dt);
    // Sanity
    void ChangeSanity(float delta);
    void UpdateSanity(float dt);
    float whisper_cd_ = 20.0f;
    float sanity_drain_now_ = 0.0f;  // for the HUD
    // Objective markers for the HUD compass and the map: the tracked side quest, else the main story.
    bool ObjectiveMarker(Vector3& out, std::string& questTitle) const;
    void DrawCompass();
    void SpawnCreature(const MapCreatureSpawnDef& c);
    void CheckGroupCleared(const CreatureInstance& c);
    std::vector<const MapCreatureSpawnDef*> pending_spawns_;   // waiting for their requires_flag
    int RollD20(const DialogueChoice& ch, int& bonus, bool& rigged);
    int DialogueRollChance(const DialogueChoice& ch) const;   // % chance to pass, shown on the choice
    int CompanionIndex() const;                 // the first companion's NPC index, or -1
    std::vector<int> CompanionIndices() const;  // every companion present in the scene
    bool IsCompanion(const std::string& npcId) const;
    void CompanionSay(const std::vector<std::string>& keys, float chance = 1.0f, int npcIndex = -1);
    static constexpr int kMaxCompanions = 2;
    // Subtitles queued to play one after another (party chatter and banter).
    struct SayItem { std::string first, second, voice; };
    std::vector<SayItem> say_queue_;
    void QueueSay(const std::string& speaker, const std::string& text, const std::string& voiceKey = "");
    float companion_heal_cd_ = 0.0f;
    float companion_idle_cd_ = 60.0f;
    float companion_calm_ = 10.0f;        // seconds since the companion last fought
    std::string companion_target_;
    std::string companion_last_zone_;
    size_t companion_idle_next_ = 0;
    int SplashDamage(const Projectile& p, Vector3 at, const std::string& skipId);
    void ApplyStatus(CreatureInstance& c, const std::string& status, float power, float duration);
    void TryStatus(CreatureInstance& c, const std::string& status, float chance, float power, float duration);
    void StatusDamage(CreatureInstance& c, int amount, Color color);
    void UpdateCreatureStatus(CreatureInstance& c, float dt);
    void FireArrow(float power);
    void CastSelectedSpell();
    void CastSpell(const SpellDef& s, bool freeCast);
    void CreatureHitCreature(CreatureInstance& attacker, CreatureInstance& victim);
    int DamageCreature(CreatureInstance& c, int amount, bool sneak, const std::string& skill, bool heavy, bool crit = false);
    void KillCreature(CreatureInstance& c);
    void DamagePlayer(int raw, Vector3 from, CreatureInstance* attacker);
    void SpawnEnemyProjectile(CreatureInstance& c);
    float DifficultyPlayerMult() const;
    float DifficultyEnemyMult() const;

    // ---- quests & dialogue
    int QuestStage(const std::string& id) const;
    void SetQuestStage(const std::string& id, int stage);
    bool EvalCondition(const DialogueCondition& c) const;
    void ExecAction(const DialogueAction& a, const std::string& rewardKey);
    void StartDialogue(int npcIndex);
    void EnterDialogueNode(const std::string& node);
    void ChooseDialogue(int choiceIndex);
    std::vector<int> VisibleChoices() const;
    void EndDialogue();

    // ---- containers & shop
    ContainerState& Container(const std::string& key, const std::string& lootTable, const std::vector<std::string>& fixed);
    void RollLoot(const std::string& tableId, ContainerState& out);
    void TakeFromContainer(int index);
    void TakeAllFromContainer();
    int VendorStock(const NpcDef& npc, const VendorStockEntry& e) const;
    int BuyPrice(const VendorStockEntry& e) const;
    int SellPrice(const ItemDef& item) const;
    void BuyItem(const VendorStockEntry& e);
    void SellItem(const std::string& id);

    // ---- persistence
    std::string SavePath(const std::string& slot) const;
    bool SaveGame(const std::string& slot);
    bool LoadGame(const std::string& slot);
    bool SaveExists(const std::string& slot) const;

    // ---- feedback
    void Toast(const std::string& text, Color color = Color{235, 225, 200, 255});
    void PlaySfxAt(const std::string& path, Vector3 pos, float volume = 1.0f);
    MapPersist& Persist() { return persist_[current_map_]; }

    // ---- rendering / UI (GameUI.cpp)
    void BuildRenderView(RenderView& view);
    void DrawFrame();
    void DrawHud();
    void DrawTitle();
    void DrawCreation();
    void DrawPause();
    void DrawInventory();
    void DrawCharacter();
    void DrawCombatSheet(Rectangle P);
    void DrawPerks(Rectangle P);
    void DrawBestiary(Rectangle P);
    std::string bestiary_sel_;
    float bestiary_scroll_ = 0.0f;
    void DrawCrafting();
    bool RecipeKnown(const RecipeDef& r) const;
    bool CanCraft(const RecipeDef& r) const;
    bool Craft(const std::string& recipeId);
    void ApplyOilOnHit(CreatureInstance& c);
    std::string craft_station_, craft_selected_;
    float craft_scroll_ = 0.0f;
    // Fishing: cast at a spot, wait, and press interact quickly when something bites.
    bool fishing_ = false;
    int fish_state_ = 0;          // 0 waiting, 1 biting
    float fish_timer_ = 0.0f;
    int fish_spot_ = -1;
    Vector3 fish_from_{}, fish_bob_{};
    void StartFishing(int spotIndex);
    void UpdateFishing(float dt);
    void FishPress();
    void CatchFish();
    std::string perk_skill_;
    void DrawJournal();
    void DrawMapOverlay();
    void DrawDialogue();
    void DrawShop();
    void DrawContainer();
    void DrawReader();
    void DrawOptions();
    void DrawDead();
    void DrawEnding();
    void DrawDebug();
    void DrawToasts();
    void SetOverlay(Overlay o);

    // UI primitives
    float U() const; // ui scale factor
    Font UiFont() const;
    Font MonoFont() const;
    void Text(const std::string& s, float x, float y, float size, Color c) const;
    // Text that shrinks (down to 11 px) and then trims with an ellipsis so it never runs past maxWidth.
    void TextFit(const std::string& s, float x, float y, float size, float maxWidth, Color c) const;
    float TextWidth(const std::string& s, float size) const;
    float TextWrapped(const std::string& s, Rectangle r, float size, Color c, bool draw = true) const;
    bool Button(Rectangle r, const std::string& label, bool enabled = true, float size = 22.0f);
    void Panel(Rectangle r, Color fill = Color{14, 14, 20, 236}) const;
    void Bar(Rectangle r, float frac, Color fill, const std::string& label) const;
    void Icon(const std::string& path, Rectangle r, Color tint = WHITE);
    bool mouse_consumed_ = false;
};

} // namespace uncounted

// Headless walkthrough of Chapter Zero used by `game.exe --selftest`. It drives the real gameplay code
// (dialogue, interaction, collision, combat, loot, saves) and reports every broken step to the log.
#include "gameplay/GameEngine.h"
#include "core/Logger.h"
#include "raymath.h"
#include <filesystem>

namespace uncounted {

int GameEngine::RunSelfTest() {
    int failures = 0;
    auto check = [&](bool ok, const std::string& what) {
        Logger::Info(std::string(ok ? "[PASS] " : "[FAIL] ") + what);
        if (!ok) failures++;
    };
    auto simulate = [&](float seconds) {
        for (float t = 0; t < seconds; t += 1.0f / 60.0f) {
            UpdateWorldObjects(1.0f / 60.0f);
            UpdateCreatures(1.0f / 60.0f);
            UpdateProjectiles(1.0f / 60.0f);
        }
    };
    auto npcIndex = [&](const std::string& id) {
        for (size_t i = 0; i < scene_.npcs.size(); i++)
            if (scene_.npcs[i].def->id == id) return static_cast<int>(i);
        return -1;
    };
    auto chooseNext = [&](const std::string& next) {
        const DialogueDef* d = content_.GetDialogue(dialogue_id_);
        if (!d) return false;
        const auto& node = d->nodes.at(dialogue_node_);
        for (int ci : VisibleChoices()) {
            if (node.choices[ci].next == next) {
                ChooseDialogue(ci);
                return true;
            }
        }
        return false;
    };
    auto interactable = [&](const std::string& id) -> InteractableInstance* {
        for (auto& in : scene_.interactables)
            if (in.def.instance_id == id) return &in;
        return nullptr;
    };
    auto standAndUse = [&](Vector3 pos, float yawDeg, float pitchDeg) {
        player_.pos = pos;
        player_.pos.y = GroundHeight({pos.x, pos.y + 0.5f, pos.z}, 0.45f);
        player_.yaw = yawDeg * DEG2RAD;
        player_.pitch = pitchDeg * DEG2RAD;
        player_.crouching = false;
        player_.eye_height = 1.6f;
        Interact();
    };
    const std::string quest = "core:quest.legally_deceased";

    // --- New game as a Human Displaced Heir Warrior
    creation_race_ = 0;
    creation_bg_ = 0;
    creation_arch_ = 0;
    NewGame();
    check(overlay_ == Overlay::Narration && narration_pages_.size() >= 3, "new game opens with the prologue narration");
    narration_page_ = static_cast<int>(narration_pages_.size());
    AdvanceNarration();
    check(overlay_ == Overlay::Reader, "prologue hands over to the death notice");
    SetOverlay(Overlay::None);
    const std::string side = "core:quest.bakers_daughter";
    check(current_map_ == content_.game_cfg.starting_map, "new game starts in the world map");
    check(zone_id_ == "bellwether", "player starts in the Bellwether zone");
    check(atmo_.weather == "rain", "it is raining in Bellwether at the start");
    const Vector3 road = {48.0f, 0.0f, 0.0f};
    const Vector3 annex = {87.0f, -4.8f, -8.4f};
    auto at = [](Vector3 o, float x, float y, float z) { return Vector3{o.x + x, o.y + y, o.z + z}; };
    auto walk = [&](Vector3 from, Vector3 delta) {
        // Walks in small steps with ground snapping, like a player holding a movement key.
        Vector3 p = from;
        int steps = static_cast<int>(Vector3Length(delta) / 0.05f);
        for (int i = 0; i < steps; i++) {
            p = MoveWithCollision(p, Vector3Scale(delta, 1.0f / steps), 0.32f, 1.75f, true);
            p.y = GroundHeight({p.x, p.y + 0.05f, p.z}, 0.45f);
        }
        return p;
    };
    check(QuestStage(quest) == 0, "quest starts at stage 0");
    check(Equipped("main_hand") != nullptr, "starting weapon equipped");
    check(player_.health == MaxHealth(), "starts at full health");
    check(player_.pos.y > -0.05f && player_.pos.y < 0.2f, "player stands on the ground at spawn (y=" + std::to_string(player_.pos.y) + ")");

    Vector3 p = MoveWithCollision({-18.0f, 0, 0}, {-5.0f, 0, 0}, 0.32f, 1.75f, true);
    check(p.x > -19.5f, "town wall blocks movement (x=" + std::to_string(p.x) + ")");

    // --- Clerk: receive the Annex key
    int clerk = npcIndex("core:npc.clerk_oakhaven");
    check(clerk >= 0, "clerk present");
    StartDialogue(clerk);
    check(overlay_ == Overlay::Dialogue, "dialogue opens");
    check(chooseNext("explain_27b"), "clerk offers the death-notice topic");
    check(QuestStage(quest) == 10, "quest advanced to 10");
    check(CountItem("core:item.annex_key") == 1, "received annex key");
    int xpMark = player_.xp + player_.level * 100000;
    EndDialogue();
    StartDialogue(clerk);
    check(!chooseNext("explain_27b"), "death-notice topic no longer offered");
    EndDialogue();
    check(player_.xp + player_.level * 100000 == xpMark, "no repeat reward");

    // --- Vendor
    StartDialogue(npcIndex("core:npc.merchant_vaelen"));
    {
        const DialogueDef* d = content_.GetDialogue(dialogue_id_);
        const auto& node = d->nodes.at(dialogue_node_);
        for (int ci : VisibleChoices()) {
            if (!node.choices[ci].actions.empty() && node.choices[ci].actions[0].type == "open_shop") {
                ChooseDialogue(ci);
                break;
            }
        }
    }
    check(overlay_ == Overlay::Shop, "merchant opens shop");
    int gold = player_.gold;
    const NpcDef* vaelen = content_.GetNpc("core:npc.merchant_vaelen");
    int before = CountItem(vaelen->vendor_inventory[0].item_id);
    BuyItem(vaelen->vendor_inventory[0]);
    check(player_.gold < gold && CountItem(vaelen->vendor_inventory[0].item_id) == before + 1, "bought a potion");
    SetOverlay(Overlay::None);

    // --- Old Road: scout sets stage 20
    Vector3 gate = walk({15.0f, 0.0f, 0.0f}, {12.0f, 0.0f, 0.0f});
    check(gate.x > 26.0f, "walked through Bellwether's east gate onto the Old Road (x=" + std::to_string(gate.x) + ")");
    player_.pos = gate;
    UpdateAtmosphere(0.0f, true);
    check(zone_id_ == "old_road", "Old Road zone entered without a loading screen");
    StartDialogue(npcIndex("core:npc.ashbound_scout"));
    check(chooseNext("annex_warning"), "scout warns about the Annex");
    EndDialogue();
    check(QuestStage(quest) == 20, "quest advanced to 20");

    // --- Combat: a rat notices and fights
    CreatureInstance* rat = nullptr;
    for (auto& c : scene_.creatures)
        if (c.instance_id == "road_rat_1") rat = &c;
    check(rat != nullptr, "road rat spawned");
    if (rat) {
        player_.pos = Vector3Add(rat->pos, {0, 0, 1.4f});
        player_.yaw = atan2f(rat->pos.x - player_.pos.x, rat->pos.z - player_.pos.z);
        float hp = player_.health;
        simulate(4.0f);
        check(rat->alerted, "rat noticed the player");
        check(player_.health < hp, "rat attacked the player");
        player_.health = static_cast<float>(MaxHealth());
        player_.yaw = atan2f(rat->pos.x - player_.pos.x, rat->pos.z - player_.pos.z);
        attack_heavy_ = true;
        for (int i = 0; i < 10 && rat->state != CreatureState::Dead; i++) ResolveMeleeHit();
        check(rat->state == CreatureState::Dead, "rat killed with melee");
        check(Persist().containers.count("corpse:road_rat_1") == 1, "rat corpse has a loot container");
    }

    // --- Locked chest with lockpicks
    AddItem("core:item.lockpick", 20, false);
    InteractableInstance* chest = interactable("road_ranger_chest");
    for (int i = 0; i < 20 && chest && chest->locked; i++) {
        standAndUse(at(road, 5.5f, 0, -7.6f), 180.0f, -30.0f);
        if (overlay_ != Overlay::None) SetOverlay(Overlay::None);
    }
    check(chest && !chest->locked, "ranger chest lock picked");

    // --- Side quest: A Name Worth Keeping (boundary stone -> Marta)
    check(QuestStage(side) < 0, "side quest not started before reading the stone");
    standAndUse(at(road, 4.0f, 0, -4.6f), 180.0f, -30.0f);
    check(overlay_ == Overlay::Reader && QuestStage(side) == 0, "Oakhallow boundary stone starts the side quest");
    SetOverlay(Overlay::None);
    int marta = npcIndex("core:npc.innkeeper_marta");
    StartDialogue(marta);
    check(!chooseNext("ilse"), "Marta cannot be told the name before it is found");
    check(chooseNext("oakhallow"), "Marta asked about Oakhallow");
    EndDialogue();
    check(QuestStage(side) == 10, "side quest advanced to 10");

    // --- Ambient barks: Marta speaks when the player lingers nearby
    player_.pos = Vector3Add(scene_.npcs[marta].pos, {0, 0, -2.0f});
    subtitle_time_ = 0;
    bark_global_cd_ = 0;
    bark_cd_.clear();
    for (int i = 0; i < 10; i++) UpdateBarks(0.1f);
    check(subtitle_time_ > 0 && subtitle_speaker_ == content_.Tr("npc.innkeeper_marta.name"), "Marta says an ambient line nearby");

    // --- Registry Annex
    // Descend the tunnel stairs into the underground Annex and come back up again.
    Vector3 down = walk({75.5f, 0.0f, 0.0f}, {11.5f, 0.0f, 0.0f});
    check(down.x > 86.5f && fabsf(down.y - annex.y) < 0.1f, "walked down the stairs to the Annex landing (x=" + std::to_string(down.x) +
                                                                    " y=" + std::to_string(down.y) + ")");
    Vector3 up = walk(down, {-11.0f, 0.0f, 0.0f});
    check(up.x < 76.5f && fabsf(up.y) < 0.1f, "climbed back up to the road (y=" + std::to_string(up.y) + ")");
    Vector3 foyer = walk({87.0f, annex.y, 0.5f}, {0.0f, 0.0f, -5.0f});
    check(foyer.z < -4.0f, "entered the Annex foyer through the landing (z=" + std::to_string(foyer.z) + ")");
    player_.pos = foyer;
    UpdateAtmosphere(0.0f, true);
    check(zone_id_ == "annex", "Annex zone active underground");

    InteractableInstance* door = interactable("annex_inner_door");
    Vector3 blocked = MoveWithCollision(at(annex, 0, 0, -2.5f), {0, 0, -3.0f}, 0.32f, 1.75f, true);
    check(blocked.z > annex.z - 4.0f, "locked archive door blocks the way (z=" + std::to_string(blocked.z) + ")");
    standAndUse(at(annex, 0, 0, -2.4f), 180.0f, 0.0f);
    check(door && door->open, "archive door unlocked with the key and opened");
    simulate(1.5f);
    for (auto& c : scene_.creatures) {
        // Clear only the Annex's own guards; the boss and Vault III's creatures are tested separately.
        static const std::set<std::string> annexGuards = {"foyer_rat", "archive_skel_1", "archive_crawler_1", "crypt_sentinel_1"};
        if (c.state != CreatureState::Dead && annexGuards.count(c.instance_id)) {
            c.state = CreatureState::Dead;
            Persist().dead.insert(c.instance_id);
        }
    }
    RebuildColliders();
    Vector3 through = MoveWithCollision(at(annex, 0, 0, -2.5f), {0, 0, -3.0f}, 0.32f, 1.75f, true);
    check(through.z < annex.z - 5.0f, "open door is passable (z=" + std::to_string(through.z) + ")");

    InteractableInstance* portcullis = interactable("crypt_portcullis");
    standAndUse(at(annex, 7.4f, 0, -11.0f), 90.0f, -30.0f);
    check(portcullis && portcullis->open, "lever raised the portcullis");
    simulate(2.0f);

    InteractableInstance* vault = interactable("secret_wall_door");
    player_.pos = at(annex, -7.5f, 0.0f, -15.5f);
    CheckPressurePlates();
    check(vault && vault->open, "rune plate opened the vault gate");
    standAndUse(at(annex, -4.5f, 0, -15.4f), 180.0f, -30.0f);
    check(QuestStage(side) == 20, "struck census folio names Ilse Brannock (stage 20)");
    SetOverlay(Overlay::None);
    simulate(2.0f);

    InteractableInstance* vchest = interactable("secret_widowmaker_chest");
    standAndUse(at(annex, 6.0f, 0, -21.8f), 180.0f, -30.0f);
    check(overlay_ == Overlay::Container, "vault chest opens");
    int widow = 0;
    for (const auto& it : Persist().containers["secret_widowmaker_chest"].items)
        if (it.id == "core:item.widowmaker") widow += it.qty;
    check(widow == 1, "vault chest holds exactly one Widowmaker");
    TakeAllFromContainer();
    check(CountItem("core:item.widowmaker") == 1 && vchest && vchest->used, "looted the Widowmaker");

    StartDialogue(npcIndex("core:npc.erased_spirit"));
    check(chooseNext("explain_prison"), "spirit explains the prison");
    EndDialogue();
    check(CountItem("core:item.crypt_key") == 1, "received crypt key");
    StartDialogue(npcIndex("core:npc.erased_spirit"));
    check(chooseNext("ilse"), "asked the Witness about Ilse");
    EndDialogue();
    check(QuestStage(side) == 30, "side quest advanced to 30");

    // --- Vault III: two more levels below the crypt
    const std::string vq = "core:quest.vault_three";
    const float vz = -22.0f;
    standAndUse({67.2f, annex.y, vz + 2.3f}, -90.0f, 0.0f);
    check(QuestStage(vq) == 0, "floury handprints start The Sleepers of Vault III");
    SetOverlay(Overlay::None);
    Vector3 nursery = walk({67.0f, annex.y, vz}, {-14.0f, 0.0f, 0.0f});
    check(nursery.x < 54.0f && fabsf(nursery.y - (-10.4f)) < 0.1f,
          "descended from the crypt to the Nursery (x=" + std::to_string(nursery.x) + " y=" + std::to_string(nursery.y) + ")");
    player_.pos = nursery;
    UpdateAtmosphere(0.0f, true);
    check(zone_id_ == "vault_three", "Vault III zone active");
    Vector3 back = walk(nursery, {14.0f, 0.0f, 0.0f});
    check(back.x > 65.0f && fabsf(back.y - annex.y) < 0.1f, "climbed back up into the crypt (y=" + std::to_string(back.y) + ")");
    standAndUse({38.6f, -10.4f, -26.6f}, 180.0f, -35.0f);
    check(QuestStage(vq) == 10 && player_.flags.count("found_ilse"), "found Ilse asleep in the Nursery");
    SetOverlay(Overlay::None);
    Vector3 seal = walk({30.6f, -10.4f, vz}, {-14.0f, 0.0f, 0.0f});
    check(fabsf(seal.y - (-16.0f)) < 0.1f, "descended to the Seal Chamber (y=" + std::to_string(seal.y) + ")");
    player_.pos = seal;
    UpdateAtmosphere(0.0f, true);
    check(zone_id_ == "seal_chamber", "Seal Chamber has its own zone");
    standAndUse({10.2f, -16.0f, vz}, -90.0f, -25.0f);
    check(QuestStage(vq) == 10, "the Seal cannot be signed while the Warden lives");
    CreatureInstance* warden = nullptr;
    for (auto& c : scene_.creatures) if (c.instance_id == "lullaby_warden") warden = &c;
    check(warden != nullptr, "Lullaby Warden present");
    if (warden) DamageCreature(*warden, 999, false, "swords", false);
    check(warden && warden->state == CreatureState::Dead, "Lullaby Warden defeated");
    standAndUse({10.2f, -16.0f, vz}, -90.0f, -25.0f);
    check(QuestStage(vq) == 100 && player_.flags.count("seal_renewed"), "signed the Seal of Names");
    check(overlay_ == Overlay::Narration && narration_pages_.size() == 4, "the signing plays its narration");
    check(CountItem("core:item.seal_quill") == 1, "received the Archivist's Seal-Quill");
    narration_page_ = static_cast<int>(narration_pages_.size());
    AdvanceNarration();
    check(overlay_ == Overlay::None, "narration returns to play (no stray death notice)");
    player_.pos = {0.0f, 0.0f, 0.0f};
    UpdateAtmosphere(0.0f, true);
    check(atmo_.weather.empty(), "the rain over Bellwether has stopped");

    InteractableInstance* sanctum = interactable("sanctum_gate");
    standAndUse(at(annex, -16.0f, 0, -14.4f), 180.0f, 0.0f);
    check(sanctum && sanctum->open, "sanctum gate unlocked with crypt key");

    CreatureInstance* boss = nullptr;
    for (auto& c : scene_.creatures)
        if (c.instance_id == "sanctum_boss") boss = &c;
    int levelBefore = player_.level;
    if (boss) DamageCreature(*boss, 999, false, "swords", false);
    check(boss && boss->state == CreatureState::Dead, "boss defeated");
    check(player_.level > levelBefore || player_.level >= 2, "boss XP counts toward levelling (level " + std::to_string(player_.level) + ")");

    simulate(2.0f);
    standAndUse(at(annex, -16.0f, 0, -26.2f), 180.0f, -15.0f);
    check(QuestStage(quest) == 30, "pedestal advanced quest to 30");
    check(CountItem("core:item.uncounted_ledger") == 1 && CountItem("core:item.form_27b") == 1, "holding the ledger and Form 27-B");
    container_key_ = "corpse:sanctum_boss";
    TakeAllFromContainer();
    check(CountItem("core:item.uncounted_ledger") == 1, "quest documents stay unique after looting the boss");

    // --- Save / load round trip
    check(SaveGame("selftest"), "saved game");
    int stage = QuestStage(quest);
    size_t items = player_.inventory.size();
    player_.inventory.clear();
    check(LoadGame("selftest"), "loaded game");
    check(QuestStage(quest) == stage && player_.inventory.size() == items, "save round trip preserves quest & inventory");
    InteractableInstance* door2 = interactable("annex_inner_door");
    check(door2 && door2->open && !door2->locked, "door state persisted across save/load");
    std::error_code ec;
    std::filesystem::remove(SavePath("selftest"), ec);
    std::filesystem::remove(SavePath("selftest") + ".bak", ec);

    // --- Speak Ilse's name to Marta
    StartDialogue(npcIndex("core:npc.innkeeper_marta"));
    check(chooseNext("ilse"), "spoke Ilse's name to Marta");
    check(!chooseNext("ilse_alive"), "Marta isn't told the Warden still sings once the Seal is signed");
    int breadBefore = CountItem("core:item.bread_loaf");
    check(chooseNext("ilse_alive_safe"), "told Marta that Ilse is alive and safe");
    EndDialogue();
    check(QuestStage(side) == 100 && player_.flags.count("ilse_remembered"), "A Name Worth Keeping completed");
    check(player_.flags.count("marta_knows_ilse") && player_.flags.count("marta_knows_seal") &&
          CountItem("core:item.bread_loaf") == breadBefore + 2, "Marta learns Ilse sleeps safely (bread gift)");
    StartDialogue(npcIndex("core:npc.innkeeper_marta"));
    check(!chooseNext("ilse") && !chooseNext("oakhallow") && !chooseNext("ilse_alive_safe") && !chooseNext("seal_signed") &&
          !chooseNext("sleeper_unnamed"), "side quest topics retire after completion");
    EndDialogue();
    {
        const NpcDef* marta = content_.GetNpc("core:npc.innkeeper_marta");
        bool rainyBarkGated = false, dryBark = false;
        for (const auto& b : marta ? marta->barks : std::vector<NpcBarkDef>{}) {
            if (b.text_key == "bark.marta.1") rainyBarkGated = b.not_flag == "seal_renewed";
            if (b.text_key == "bark.marta.dry") dryBark = b.flag == "seal_renewed";
        }
        check(rainyBarkGated && dryBark, "Marta's rain barks follow the Seal");
    }

    // --- Return to the clerk and finish the chapter
    player_.pos = {-4.0f, 0.0f, -8.0f};
    UpdateAtmosphere(0.0f, true);
    StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
    check(chooseNext("rain_stopped"), "clerk remarks on the rain stopping");
    check(player_.flags.count("clerk_seal_talk") && chooseNext("greeting"), "clerk returns to business");
    check(!chooseNext("rain_stopped"), "clerk's rain remark plays once");
    check(chooseNext("inspect_ledger"), "clerk recognises the ledger");
    check(chooseNext("ending_independent"), "chose to keep the ledger");
    EndDialogue();
    check(QuestStage(quest) == 101, "quest completed (101)");
    check(screen_ == Screen::Ending, "ending screen shown");
    check(CountItem("core:item.uncounted_ledger") == 1, "kept the ledger");
    screen_ = Screen::Playing;
    StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
    check(!chooseNext("inspect_ledger"), "ending cannot be replayed");
    EndDialogue();

    // --- Alternate orders for Marta's Vault III news (flags only; restored afterwards)
    {
        auto savedFlags = player_.flags;
        auto savedClaimed = player_.claimed;
        player_.flags = {"found_ilse"};
        StartDialogue(npcIndex("core:npc.innkeeper_marta"));
        check(!chooseNext("ilse_alive") && chooseNext("sleeper_unnamed"), "Marta aches for an unnamed sleeper");
        check(chooseNext("root") && !chooseNext("sleeper_unnamed"), "the unnamed sleeper is mentioned once");
        EndDialogue();
        player_.flags = {"found_ilse", "ilse_remembered"};
        StartDialogue(npcIndex("core:npc.innkeeper_marta"));
        check(!chooseNext("ilse_alive_safe") && !chooseNext("seal_signed") && chooseNext("ilse_alive"),
              "before the Seal, Marta begs you to go back down");
        EndDialogue();
        player_.flags.insert("seal_renewed");
        StartDialogue(npcIndex("core:npc.innkeeper_marta"));
        check(!chooseNext("ilse_alive_safe") && chooseNext("seal_signed") && player_.flags.count("marta_knows_seal"),
              "after the Seal, Marta hears the sleepers are safe");
        EndDialogue();
        player_.flags = savedFlags;
        player_.claimed = savedClaimed;
    }

    std::filesystem::remove(SavePath("autosave"), ec);
    std::filesystem::remove(SavePath("autosave") + ".bak", ec);
    Logger::Info("Self-test finished with " + std::to_string(failures) + " failure(s).");
    return failures;
}

} // namespace uncounted

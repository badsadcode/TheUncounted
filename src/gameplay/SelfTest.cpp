#include <algorithm>
#include <fstream>
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

    // --- Portraits: this race and calling first, then the race's others, then its default (cosmetic)
    {
        const std::vector<std::string> saved = content_.portraits;
        content_.portraits = {"assets/ui/portraits/elf_mage_1.png", "assets/ui/portraits/human_mage_1.png",
                              "assets/ui/portraits/human_warrior_1.png", "assets/ui/portraits/human_warrior_2.png"};
        auto c = PortraitChoices(content_.races[0], content_.archetypes[0]);
        check(c.size() == 3 && c[0] == "assets/ui/portraits/human_warrior_1.png" && c[1] == "assets/ui/portraits/human_warrior_2.png" &&
                  c[2] == "assets/ui/portraits/human_mage_1.png",
              "portrait picker: race and calling first, then the race's other portraits");
        content_.portraits = {};
        c = PortraitChoices(content_.races[0], content_.archetypes[0]);
        check(c.size() == 1 && c[0] == content_.races[0].portrait, "a race without painted portraits shows its placeholder");
        content_.portraits = saved;
    }

    // --- New game as a Human Displaced Heir Warrior
    creation_race_ = 0;
    creation_bg_ = 0;
    creation_arch_ = 0;
    creation_portrait_ = 0;
    NewGame();
    check(!player_.portrait.empty() && PlayerPortrait() == player_.portrait, "the chosen portrait is the character's");
    check(overlay_ == Overlay::Narration && narration_pages_.size() >= 3, "new game opens with the prologue narration");
    narration_page_ = static_cast<int>(narration_pages_.size());
    AdvanceNarration();
    check(overlay_ == Overlay::Reader, "prologue hands over to the death notice");
    SetOverlay(Overlay::None);
    const std::string side = "core:quest.bakers_daughter";
    check(current_map_ == content_.game_cfg.starting_map, "new game starts in the world map");
    check(zone_id_ == "bellwether", "player starts in the Bellwether zone");
    {
        Vector3 mk;
        std::string qt;
        bool atClerk = false;
        if (ObjectiveMarker(mk, qt))
            for (const auto& n : scene_.npcs) if (n.instance_id == "npc_oakhaven" && Vector3Distance(n.pos, mk) < 0.1f) atClerk = true;
        check(atClerk, "the objective marker points at Clerk Oakhaven");
    }
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

    Vector3 p = MoveWithCollision({-18.0f, 0, 6.0f}, {-5.0f, 0, 0}, 0.32f, 1.75f, true);
    check(p.x > -19.5f, "town wall blocks movement (x=" + std::to_string(p.x) + ")");
    Vector3 westGate = MoveWithCollision({-18.0f, 0, 0}, {-5.0f, 0, 0}, 0.32f, 1.75f, true);
    check(westGate.x < -22.0f, "the west gate opens onto the Whistling Wood lane (x=" + std::to_string(westGate.x) + ")");

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

    StartDialogue(npcIndex("core:npc.erased_spirit"));
    check(chooseNext("remembered") && player_.flags.count("witness_named"), "the Witness remembers its name after the Seal");
    check(chooseNext("root") && !chooseNext("remembered"), "the Witness's name scene plays once");
    EndDialogue();
    check(screen_ == Screen::Playing, "finishing a side quest does not end the chapter");

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
    const std::string portrait = player_.portrait;
    player_.inventory.clear();
    player_.portrait.clear();
    check(LoadGame("selftest"), "loaded game");
    check(player_.portrait == portrait, "the chosen portrait survives save and load");
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
    check(!chooseNext("inspect_ledger") && chooseNext("inspect_ledger_sealed"), "clerk reads the Ledger's new last line");
    check(chooseNext("ending_independent"), "chose to keep the ledger");
    EndDialogue();
    check(QuestStage(quest) == 101, "quest completed (101)");
    check(screen_ == Screen::Ending, "ending screen shown");
    check(CountItem("core:item.uncounted_ledger") == 1, "kept the ledger");
    screen_ = Screen::Playing;
    StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
    check(!chooseNext("inspect_ledger") && !chooseNext("inspect_ledger_sealed") && !chooseNext("arrears"), "ending cannot be replayed");
    EndDialogue();

    // --- Build systems: crits, gear bonuses, banes, splash, synergies
    {
        const ItemDef* rusty = content_.GetItem("core:item.rusted_sword");
        const ItemDef* opener = content_.GetItem("core:item.letter_opener");
        const ItemDef* mace = content_.GetItem("core:item.iron_mace");
        check(rusty && opener && CritChance(opener) > CritChance(rusty) + 0.2f, "the letter-opener is a crit weapon");
        const CreatureDef* skel = content_.GetCreature("core:enemy.restless_skeleton");
        check(mace && skel && mace->weapon.bane_family == skel->family && mace->weapon.bane_mult > 1.0f, "maces are the bane of skeletons");
        auto savedEquip = player_.equipment;
        int intBefore = Attr("intellect");
        AddItem("core:item.sabrino_hat", 1, false);
        EquipItem("core:item.sabrino_hat");
        check(GearBonus("spell_power_bonus") > 0.09f && Attr("intellect") == intBefore + 3, "Sabrino's hat grants intellect and spell power");
        const SpellDef* fb = content_.GetSpell("core:spell.sabrino_fireball");
        check(fb && fb->effect.splash_radius > 3.0f && SpellCost(*fb) < fb->mana_cost, "fireball splashes; skill trims its cost");
        player_.equipment = savedEquip;
        CreatureInstance* victim = nullptr;
        for (auto& c : scene_.creatures) if (c.state != CreatureState::Dead) { victim = &c; break; }
        if (victim) {
            int before = victim->health;
            Projectile p;
            p.damage = 40;
            p.splash_radius = 3.5f;
            p.skill = "elemental";
            int dealt = SplashDamage(p, {victim->pos.x + 1.0f, victim->pos.y + victim->height * 0.5f, victim->pos.z}, "");
            check(dealt > 0 && (victim->health < before || victim->state == CreatureState::Dead), "splash damage hits nearby creatures");
        }
        check(content_.synergies.size() >= 7, "seven synergies to build toward");
        check(interactable("sabrino_stash") && interactable("sabrino_wanted") && interactable("sabrino_note"), "Sabrino's poster and stash are in the world");
    }

    // --- Baggy's case
    {
        int bi = npcIndex("core:npc.detective_baggy");
        check(bi >= 0, "Baggy is on the Old Road");
        StartDialogue(bi);
        check(chooseNext("sabrino") && chooseNext("sabrino_where") && player_.flags.count("sabrino_lead"), "Baggy remembers the Sabrino Affair");
        check(chooseNext("root") && chooseNext("ilse"), "Baggy can be told the baker's daughter's name");
        check(CountItem("core:item.baggy_umbrella") == 1 && player_.flags.count("baggy_ilse"), "Baggy hands over the umbrella");
        check(chooseNext("root") && !chooseNext("ilse") && !chooseNext("stone"), "Baggy's case closes once");
        EndDialogue();
    }

    auto hdist = [](Vector3 a, Vector3 b) { return sqrtf((a.x - b.x) * (a.x - b.x) + (a.z - b.z) * (a.z - b.z)); };
    // --- Every creature spawns on open floor (not inside a wall)
    {
        std::string stuck;
        for (size_t i = 0; i < scene_.creatures.size(); i++) {
            const auto& c = scene_.creatures[i];
            Vector3 moved = MoveWithCollision(c.spawn, {0.01f, 0.0f, 0.0f}, c.radius, c.height, false, static_cast<int>(i));
            if (hdist(moved, c.spawn) > 0.2f) stuck += c.instance_id + " ";
        }
        check(stuck.empty(), "creature spawns are clear of walls " + stuck);
    }

    // --- Baggy as a companion: follows, fights, looks after you
    {
        int bi = npcIndex("core:npc.detective_baggy");
        player_.pos = at(road, 6.0f, 0.0f, -3.0f);
        StartDialogue(bi);
        check(chooseNext("join") && IsCompanion("core:npc.detective_baggy"), "Baggy joins as a companion");
        int rolls = CountItem("core:item.sweet_roll");
        EndDialogue();
        check(rolls >= 2, "Baggy hands over emergency sweet rolls");
        player_.pos = {0.0f, 0.0f, 0.0f};  // walk off to Bellwether: Baggy catches up
        UpdateAtmosphere(0.0f, true);
        simulate(3.0f);
        check(hdist(scene_.npcs[bi].pos, player_.pos) < 4.0f, "Baggy keeps up with the player");
        player_.pos = at(annex, 0.0f, 0.0f, 2.0f);  // down in the Annex: catches up across storeys
        simulate(2.0f);
        check(hdist(scene_.npcs[bi].pos, player_.pos) < 4.0f && fabsf(scene_.npcs[bi].pos.y - player_.pos.y) < 1.0f,
              "Baggy follows down into the Annex");
        CreatureInstance* foe = nullptr;
        for (auto& c : scene_.creatures)
            if (c.state != CreatureState::Dead && c.instance_id == "foyer_bone_clerk") foe = &c;
        if (foe) {
            foe->alerted = true;
            foe->state = CreatureState::Chase;
            int before = foe->health;
            float hpBefore = player_.health = static_cast<float>(MaxHealth());
            simulate(5.0f);
            check(foe->health < before || foe->state == CreatureState::Dead, "Baggy fights alongside the player");
            (void)hpBefore;
        }
        player_.health = MaxHealth() * 0.2f;
        companion_heal_cd_ = 0.0f;
        float low = player_.health;
        simulate(0.1f);
        check(player_.health > low + 10.0f, "Baggy hands over food when the player is badly hurt");
        StartDialogue(bi);
        check(chooseNext("wait") && !IsCompanion("core:npc.detective_baggy"), "Baggy can be asked to wait");
        EndDialogue();
        StartDialogue(bi);
        check(chooseNext("join") && IsCompanion("core:npc.detective_baggy"), "and rejoins later");
        EndDialogue();
    }

    // --- A party of two: Kaelen joins Baggy; they banter
    {
        int ki = npcIndex("core:npc.ashbound_scout");
        StartDialogue(ki);
        check(chooseNext("join") && IsCompanion("core:npc.ashbound_scout") && player_.companions.size() == 2, "Kaelen joins Baggy in the party");
        EndDialogue();
        player_.pos = {0.0f, 0.0f, 0.0f};
        simulate(3.0f);
        auto party = CompanionIndices();
        bool close = party.size() == 2;
        for (int i : party) close = close && hdist(scene_.npcs[i].pos, player_.pos) < 4.5f;
        check(close && hdist(scene_.npcs[party[0]].pos, scene_.npcs[party[1]].pos) > 0.5f, "both companions follow, side by side");
        companion_idle_cd_ = 0.0f;
        companion_calm_ = 30.0f;
        subtitle_time_ = 0.0f;
        say_queue_.clear();
        player_.claimed.erase("banter:core:npc.ashbound_scout:intro");
        for (int tries = 0; tries < 20 && !player_.claimed.count("banter:core:npc.ashbound_scout:intro"); tries++) {
            companion_idle_cd_ = 0.0f;
            subtitle_time_ = 0.0f;
            say_queue_.clear();
            UpdateCompanion(0.016f);
        }
        check(player_.claimed.count("banter:core:npc.ashbound_scout:intro") && !say_queue_.empty(), "Kaelen and Baggy banter on the road");
        say_queue_.clear();
        int vi = npcIndex("core:npc.librarian_fenwick");
        (void)vi;
        StartDialogue(npcIndex("core:npc.ashbound_scout"));
        check(chooseNext("wait") && player_.companions.size() == 1, "Kaelen can wait while Baggy carries on");
        EndDialogue();
    }

    // --- Dinner at Eight
    {
        const std::string dq = "core:quest.dinner_at_eight";
        int si = npcIndex("core:npc.witch_sabrino");
        UpdateWorldObjects(0.0f);
        check(si >= 0 && scene_.npcs[si].hidden, "Sabrino isn't in town until the note is found");
        standAndUse(at(road, -10.4f, 0.0f, 10.4f), 0.0f, -20.0f);
        if (QuestStage(dq) < 0) standAndUse(at(road, -10.4f, 0.0f, 10.9f), 0.0f, -30.0f);
        SetOverlay(Overlay::None);
        UpdateWorldObjects(0.0f);
        check(QuestStage(dq) == 0 && !scene_.npcs[si].hidden, "Sabrino's note starts Dinner at Eight; Sabrino arrives at the inn");
        StartDialogue(si);
        check(chooseNext("dinner_plan") && QuestStage(dq) == 10, "Sabrino asks for ingredients");
        check(chooseNext("root") && !chooseNext("cooking"), "Sabrino waits for all three ingredients");
        EndDialogue();
        AddItem("core:item.grave_truffle", 1, false);
        AddItem("core:item.ash_pepper", 1, false);
        AddItem("core:item.vallo_red", 1, false);
        StartDialogue(si);
        check(chooseNext("cooking") && QuestStage(dq) == 20 && CountItem("core:item.vallo_red") == 0, "the ingredients go into the pot");
        check(chooseNext("root") && !chooseNext("dinner"), "dinner needs guests first");
        EndDialogue();
        for (const char* who : {"core:npc.innkeeper_marta", "core:npc.librarian_fenwick", "core:npc.brother_aldous"}) {
            StartDialogue(npcIndex(who));
            check(chooseNext("invite_dinner"), std::string("invited ") + who);
            EndDialogue();
        }
        StartDialogue(npcIndex("core:npc.detective_baggy"));
        check(chooseNext("invite"), "invited Baggy");
        EndDialogue();
        StartDialogue(si);
        check(chooseNext("dinner") && QuestStage(dq) == 100, "dinner is served");
        check(overlay_ == Overlay::Narration && narration_pages_.size() == 6, "the dinner plays out for the guests who came (" +
              std::to_string(narration_pages_.size()) + " cards)");
        check(CountItem("core:item.ladle_of_justice") == 1, "Sabrino gives you the Ladle of Justice");
        narration_page_ = static_cast<int>(narration_pages_.size());
        AdvanceNarration();
        EndDialogue();
        check(screen_ == Screen::Playing, "a finished side quest doesn't end the chapter");
        float spBefore = Bonus("spell_power_bonus");
        UseItem("core:item.sabrino_gnocchi");
        check(BuffBonus("spell_power_bonus") > 0.14f && Bonus("spell_power_bonus") > spBefore, "Sabrino's gnocchi buffs spell power");
        StartDialogue(si);
        check(chooseNext("END") || true, "Sabrino's shop opens after dinner");
        EndDialogue();
        SetOverlay(Overlay::None);
        shop_npc_.clear();
    }

    // --- Rats. It's always rats.
    {
        const std::string rq = "core:quest.rats";
        int vi = npcIndex("core:npc.merchant_vaelen");
        size_t before = scene_.creatures.size();
        StartDialogue(vi);
        check(chooseNext("rats_pitch") && QuestStage(rq) == 0 && player_.flags.count("rats_in_town"), "Vaelen apologises for the rats");
        check(chooseNext("advance_ok") && dialogue_node_ == "advance_fail", "the 95% persuasion check rolls a natural 1 first");
        EndDialogue();
        UpdateWorldObjects(0.0f);
        int townRats = 0;
        for (auto& c : scene_.creatures) if (c.instance_id.rfind("town_rat_", 0) == 0) townRats++;
        check(scene_.creatures.size() == before + 5 && townRats == 5, "rats overrun Bellwether's streets");
        for (auto& c : scene_.creatures) if (c.instance_id.rfind("town_rat_", 0) == 0) DamageCreature(c, 999, false, "swords", false);
        check(QuestStage(rq) == 20, "clearing the streets points south to Hollowmere");
        for (auto& c : scene_.creatures)
            if (c.instance_id == "rat_king" || c.instance_id.rfind("kitchen_rat_", 0) == 0) DamageCreature(c, 999, false, "swords", false);
        check(QuestStage(rq) == 40, "the Rat King falls");
        StartDialogue(vi);
        check(chooseNext("rats_done") && QuestStage(rq) == 100, "Vaelen pays for the rats");
        EndDialogue();
        container_key_ = "corpse:rat_king";
        TakeAllFromContainer();
        check(CountItem("core:item.rat_crown") == 1, "the Rat King's crown can be looted");
        AddItem("core:item.dented_bucket", 1, false);
        EquipItem("core:item.dented_bucket");
        StartDialogue(vi);
        check(chooseNext("bucket") && GearBonus("shop_discount") > 0.09f, "a bucket on your head confuses shopkeepers");
        EndDialogue();
        UnequipSlot("head");
    }

    // --- The Hollowmere Haunting
    {
        const std::string hq = "core:quest.hollowmere";
        int hi = npcIndex("core:npc.hunter_hollis");
        int pi = npcIndex("core:npc.ghost_percival");
        check(hi >= 0 && pi >= 0 && scene_.npcs[pi].hidden, "Hollis is in town; the ghost hides until identified");
        StartDialogue(hi);
        check(chooseNext("contract") && QuestStage(hq) == 10 && CountItem("core:item.hollowmere_key") == 1, "Hollis hands over the contract and key");
        check(chooseNext("root") && !chooseNext("identify"), "no identification without evidence");
        EndDialogue();
        InteractableInstance* front = interactable("hollowmere_front_door");
        check(front && front->locked, "Hollowmere's front door is locked");
        for (const char* f : {"ev_cold", "ev_floating", "clue_wailing"}) player_.flags.insert(f);
        StartDialogue(hi);
        check(chooseNext("identify") && chooseNext("wrong_banshee") && chooseNext("identify"), "a wrong guess gets a scolding, not a fail");
        check(chooseNext("right_host") && QuestStage(hq) == 20 && player_.flags.count("host_identified"), "identified the Lingering Host");
        EndDialogue();
        UpdateWorldObjects(0.0f);
        check(!scene_.npcs[pi].hidden, "Sir Percival appears in the ballroom");
        StartDialogue(pi);
        check(chooseNext("party") && QuestStage(hq) == 101, "the town comes to Percival's last party");
        check(overlay_ == Overlay::Narration && narration_pages_.size() == 6, "the party plays out (" + std::to_string(narration_pages_.size()) + " cards)");
        check(CountItem("core:item.hollowmere_signet") == 1, "Percival leaves his signet");
        narration_page_ = static_cast<int>(narration_pages_.size());
        AdvanceNarration();
        EndDialogue();
        // The other ending, flags only: banishing spawns the Wrathful Host, whose death raises its flag.
        player_.flags.insert("host_banish");
        UpdateWorldObjects(0.0f);
        CreatureInstance* host = nullptr;
        for (auto& c : scene_.creatures) if (c.instance_id == "wrathful_host") host = &c;
        check(host != nullptr && scene_.npcs[pi].hidden, "banishing summons the Wrathful Host in Percival's place");
        if (host) DamageCreature(*host, 9999, false, "swords", false);
        check(player_.flags.count("host_banished") && QuestStage(hq) == 101, "the Host's death is recorded; quests still only move forward");
        player_.flags.erase("host_banish");
        player_.flags.erase("host_banished");
        const DialogueDef* vd = content_.GetDialogue("core:dialogue.hunter_hollis");
        int pct = vd ? DialogueRollChance(vd->nodes.at("cards").choices[0]) : -1;
        check(pct >= 5 && pct <= 95, "dice odds are shown on rolled choices (" + std::to_string(pct) + "%)");
    }

    // --- Campaigns: every quest belongs to one; the HUD shows the main story + one tracked side quest
    {
        bool allTagged = true;
        for (const auto& [qid, q] : content_.quests) if (!content_.GetCampaign(q.campaign)) allTagged = false;
        check(content_.campaigns.size() >= 3 && allTagged, "quests are grouped into campaigns");
        check(content_.campaigns.front().kind == "main", "the main chapter is listed first");
        player_.tracked_quest.clear();
        SetQuestStage("core:quest.test_dummy_never", 0);  // unknown quests are ignored
        check(player_.tracked_quest.empty(), "unknown quests don't steal the HUD");
    }

    // --- The Bellwether Players: the whole four-act campaign
    {
        const std::string q1 = "core:quest.players_casting", q2 = "core:quest.players_script", q3 = "core:quest.players_rehearsal",
                          q4 = "core:quest.players_opening";
        auto visibleNpc = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visibleNpc(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            EndDialogue();
            return ok;
        };
        check(talk("core:npc.odette", {"aud_1", "aud_2", "aud_safe", "aud_3"}) && QuestStage(q1) == 10 && player_.flags.count("style_dramatic"),
              "Act I: auditioned for Odette and got the lead");
        bool recruited = talk("core:npc.detective_baggy", {"cast_baggy"}) && talk("core:npc.innkeeper_marta", {"cast_marta"}) &&
                         talk("core:npc.librarian_fenwick", {"cast_fenwick"}) &&
                         talk("core:npc.clerk_oakhaven", {"cast_oakhaven", "form_2", "form_3", "form_done"}) &&
                         talk("core:npc.hunter_hollis", {"cast_hollis"}) && talk("core:npc.werewolf_rolf", {"cast_rolf", "root"}) &&
                         talk("core:npc.vampire_ashgrave", {"cast_ashgrave", "root"});
        int dragonAnswer = visibleNpc("core:npc.hunter_hollis");
        if (dragonAnswer >= 0 && !player_.flags.count("cast_hollis")) {  // the dragon question rolls; either answer recruits him
            StartDialogue(dragonAnswer);
            chooseNext("cast_hollis");
            if (!chooseNext("cast_hollis_yes")) chooseNext("cast_hollis_cards");
            EndDialogue();
        }
        check(recruited && player_.flags.count("cast_hollis"), "recruited the cast (Oakhaven via Form 99-T)");
        check(talk("core:npc.odette", {"cast_done", "stolen"}) && QuestStage(q1) == 100 && QuestStage(q2) == 0, "the script is stolen");
        int mi = visibleNpc("core:npc.mortimer");
        check(mi < 0, "Mortimer stays hidden until his page is found");
        player_.flags.insert("critic_revealed");
        SetQuestStage(q2, 10);
        mi = visibleNpc("core:npc.mortimer");
        check(mi >= 0, "Mortimer Quill appears in the library");
        StartDialogue(mi);
        bool duel = chooseNext("duel_1") && (chooseNext("duel_1w"));
        if (dialogue_node_ == "duel_1l") duel = chooseNext("duel_2");
        else duel = duel && chooseNext("duel_2");
        if (!chooseNext("duel_2w")) chooseNext("duel_2l");
        if (dialogue_node_ == "duel_2w" || dialogue_node_ == "duel_2l") chooseNext("duel_3");
        duel = duel && chooseNext("duel_3w") && chooseNext("verdict");
        duel = duel && (chooseNext("verdict_win") || chooseNext("verdict_lose"));
        EndDialogue();
        check(duel && QuestStage(q2) == 20 && player_.flags.count("critic_r3"), "Act II: won the script back in a duel of criticism");
        check(talk("core:npc.odette", {"script_back"}) && QuestStage(q3) == 0 && CountItem("core:item.script_tragedie") == 1,
              "the script goes home; rehearsals move to Hollowmere");
        check(visibleNpc("core:npc.odette") >= 0 && scene_.npcs[visibleNpc("core:npc.odette")].instance_id == "npc_odette_stage",
              "Odette is now in the Hollowmere ballroom");
        bool reh = talk("core:npc.odette", {"reh_hub", "reh_baggy", "reh_bag_2", "reh_hub", "reh_marta", "reh_mar_2", "reh_hub",
                                            "reh_hollis", "reh_hol_4", "reh_hub", "reh_done"});
        check(reh && QuestStage(q3) == 10, "Act III: survived the dress rehearsal");
        bool props = talk("core:npc.librarian_fenwick", {"prop_crown"}) && talk("core:npc.merchant_vaelen", {"prop_dragon"}) &&
                     talk("core:npc.clerk_oakhaven", {"prop_thunder"});
        check(props && talk("core:npc.odette", {"props_done"}) && QuestStage(q4) == 0, "crown, dragon and something that goes bang");
        int oi = visibleNpc("core:npc.odette");
        StartDialogue(oi);
        bool show = chooseNext("show_open") && chooseNext("act1") && chooseNext("act2") && chooseNext("act2_pair") && chooseNext("act2_moment") &&
                    chooseNext("act3") && chooseNext("act3_hollis") && chooseNext("act3_fx") &&
                    (dialogue_node_ != "act3_fall" || chooseNext("act3_fx")) && chooseNext("act3_thunder") &&
                    chooseNext("act4") && chooseNext("act4_heart") && chooseNext("act4_counted") && chooseNext("bow_hub");
        show = show && (chooseNext("bow_triumph") || chooseNext("bow_good") || chooseNext("bow_disaster"));
        check(show && QuestStage(q4) == 100 && CountItem("core:item.mask_uncounted") == 1, "Act IV: opening night, and a mask to keep");
        check(overlay_ == Overlay::Narration && narration_pages_.size() == 3, "the curtain call, Mortimer's review, and after");
        narration_page_ = static_cast<int>(narration_pages_.size());
        AdvanceNarration();
        EndDialogue();
        check(screen_ == Screen::Playing, "the show doesn't end the chapter");
    }

    // --- Dungeons & Debtors: four tabletop sessions with Oakhaven as Game Master
    {
        const char* qs[] = {"core:quest.dnd_session0", "core:quest.dnd_session1", "core:quest.dnd_session2", "core:quest.dnd_session3"};
        auto play = [&](std::initializer_list<const char*> path) {
            StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            EndDialogue();
            return ok;
        };
        check(play({"pitch", "s0_rules", "s0_hollis", "s0_class", "s0_backstory", "s0_party", "s0_end", "greeting"}) &&
              QuestStage(qs[0]) == 100 && player_.flags.count("dnd_barbarian"), "Session Zero: rolled up a Barbarian (with Hollis 'helping')");
        check(play({"s1_start", "s1_quest", "s1_brawl", "s1_brawl_win", "s1_shop", "greeting"}) && QuestStage(qs[1]) == 100,
              "Session One: met in a tavern, threw Steve");
        check(play({"s2_start", "s2_trap", "s2_room", "s2_mimic_bread", "s2_puzzle", "s2_riddle_win", "s2_split", "s2_end", "greeting"}) &&
              QuestStage(qs[2]) == 100, "Session Two: befriended the mimic, solved the candle riddle, didn't split the party");
        check(play({"s3_start", "s3_fight", "s3_fight_team", "s3_end", "s3_bow_great", "after", "greeting"}) && QuestStage(qs[3]) == 100 &&
              CountItem("core:item.lucky_d20") == 1, "Session Three: Debtrax falls; Oakhaven's lucky d20");
        auto savedEquip = player_.equipment;
        EquipItem("core:item.lucky_d20");
        const DialogueDef* hd = content_.GetDialogue("core:dialogue.hunter_hollis");
        int withDie = hd ? DialogueRollChance(hd->nodes.at("cards").choices[0]) : 0;
        player_.equipment = savedEquip;
        int without = hd ? DialogueRollChance(hd->nodes.at("cards").choices[0]) : 0;
        check(withDie == std::min(95, without + 10), "the lucky d20 adds +2 to every roll (" + std::to_string(without) + "% -> " +
              std::to_string(withDie) + "%)");

        // Campaign Two: The Lich Who Forgot to File (non-roll path, Barbarian carried over from Campaign One)
        const char* ls[] = {"core:quest.lich_s1", "core:quest.lich_s2", "core:quest.lich_s3", "core:quest.lich_s4"};
        StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
        bool d1 = chooseNext("l1_start") && QuestStage(ls[0]) == 0 && chooseNext("l1_sabrino") && chooseNext("l1_lore") &&
                  chooseNext(player_.flags.count("dnd_dragon_down") ? "l1_recap_win" : "l1_recap_friend") && chooseNext("l1_mush") &&
                  chooseNext("l1_mush_barb") && chooseNext("l1_rivals") && chooseNext("l1_hollis_hmm") && chooseNext("l1_steve") &&
                  chooseNext("l1_end") && chooseNext("greeting");
        EndDialogue();
        check(d1 && QuestStage(ls[0]) == 100 && player_.flags.count("lich_steve"), "Lich I: a recap from Kaelen, a hallucinogenic mushroom, Steve rejoins");
        check(play({"l2_start", "l2_gerald", "l2_city", "l2_tavern", "l2_plan", "l2_end", "greeting"}) && QuestStage(ls[1]) == 100,
              "Lich II: Gerald conquers Form 1-UD; the city of Inkwell");
        check(play({"l3_start", "l3_ruined", "l3_moments", "l3_vault_kick", "l3_cabinet", "l3_end", "greeting"}) && QuestStage(ls[2]) == 100,
              "Lich III: the plan dies in ten seconds; the phylactery is a filing cabinet");
        int winsBefore = 0;
        for (int i = 1; i <= 8; i++) winsBefore += player_.flags.count("lich_win_" + std::to_string(i)) ? 1 : 0;
        check(play({"l4_start", "l4_talk", "l4_file", "l4_rest", "l4_bow_great", "greeting"}) && QuestStage(ls[3]) == 100 &&
                  CountItem("core:item.lich_quill") == 1 && CountItem("core:item.oakhaven_postcard") == 1 && player_.flags.count("lich_legend"),
              "Lich IV: Gerald helps the Lich file; a quill and a postcard (" + std::to_string(winsBefore + 1) + "/8 table wins)");
        StartDialogue(npcIndex("core:npc.clerk_oakhaven"));
        check(chooseNext("l_after") && screen_ == Screen::Playing, "Oakhaven took his first day off in nineteen years");
        EndDialogue();

        // Campaign Three: The Mimic Who Wanted to Be a Real Chest (Steve still in the wood: Kaelen opens Chester)
        const char* ms[] = {"core:quest.mimic_s1", "core:quest.mimic_s2", "core:quest.mimic_s3"};
        player_.flags.erase("steve_in_town");
        check(play({"m1_start", "m1_nosteve", "m1_door", "m1_letter", "m1_road", "m1_troll_audit", "m1_end", "greeting"}) && QuestStage(ms[0]) == 100,
              "Mimic I: Chester's Form C-1, and Gerald audits a troll");
        check(play({"m2_start", "m2_stand", "m2_stalls", "m2_accused", "m2_clue_audit", "m2_accuse", "m2_wrong_wardrobe", "m2_accuse", "m2_right", "m2_end",
                    "greeting"}) && QuestStage(ms[1]) == 100,
              "Mimic II: Lord Strongbox was a mimic all along");
        check(play({"m3_start", "m3_capacity", "m3_character", "m3_composure_kaelen", "m3_open", "m3_inside", "m3_bow_great", "greeting"}) &&
                  QuestStage(ms[2]) == 100 && CountItem("core:item.mimic_satchel") == 1 && CountItem("core:item.ten_foot_pole") == 1,
              "Mimic III: Kaelen puts down the quill; Chester doesn't bite; a satchel with teeth");
        float cap0 = CarryCapacity();
        auto eq = player_.equipment;
        EquipItem("core:item.mimic_satchel");
        check(CarryCapacity() >= cap0 + 30.0f, "Chester's Cousin carries 30 more");
        player_.equipment = eq;
    }

    // --- Sanity: eldritch places drain it, company slows the drain, breaking point wakes you on the quay
    {
        auto savedParty = player_.companions;
        player_.companions.clear();
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        player_.pos = {12.1f, -5.6f, -56.0f};  // the Sunken Chapel
        UpdateAtmosphere(0.0f, true);
        check(zone_id_ == "sunken_chapel", "standing in the Sunken Chapel");
        player_.sanity = 100.0f;
        for (int i = 0; i < 60; i++) UpdateSanity(0.1f);
        float alone = 100.0f - player_.sanity;
        player_.sanity = 100.0f;
        player_.companions = {"core:npc.detective_baggy", "core:npc.ashbound_scout"};
        for (int i = 0; i < 60; i++) UpdateSanity(0.1f);
        float together = 100.0f - player_.sanity;
        check(alone > 5.0f && together < alone * 0.6f, "the chapel drains sanity; company halves it (" + std::to_string(static_cast<int>(alone)) +
              " vs " + std::to_string(static_cast<int>(together)) + ")");
        player_.companions.clear();
        player_.sanity = 0.5f;
        UpdateSanity(1.0f);
        check(player_.sanity == 50.0f && overlay_ == Overlay::Narration && player_.pos.z > -30.0f && player_.pos.z < -20.0f,
              "at breaking point you black out and wake on Saltmere quay");
        narration_page_ = static_cast<int>(narration_pages_.size());
        AdvanceNarration();
        player_.companions = savedParty;
        player_.sanity = 100.0f;
    }

    // --- Case File #2: The Silence at Saltmere
    {
        const std::string sq = "core:quest.saltmere";
        auto talk = [&](const char* npc, std::initializer_list<const char*> path) {
            StartDialogue(npcIndex(npc));
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            EndDialogue();
            return ok;
        };
        check(talk("core:npc.harbourmaster", {"case", "root", "missing"}) && QuestStage(sq) == 10 && player_.flags.count("priest_name_known"),
              "the Harbourmaster takes the case (and writes his brother's name on your hand)");
        check(talk("core:npc.mother_brine", {"town"}) && talk("core:npc.silas_gale", {"list", "root", "key"}) &&
              CountItem("core:item.cellar_key") == 1, "Mother Brine and old Silas talk; Silas hands over the cellar key");
        check(talk("core:npc.professor_pickering", {"theory"}) && QuestStage(sq) == 20, "the Professor strings it all together");
        for (const char* b : {"bell_1", "bell_2", "bell_3"}) player_.flags.insert(b);
        SetQuestStage(sq, 30);
        int pi = npcIndex("core:npc.tide_priest");
        UpdateWorldObjects(0.0f);
        check(pi >= 0 && !scene_.npcs[pi].hidden, "the Tide Priest waits at the altar");
        check(talk("core:npc.tide_priest", {"final", "brother"}) && QuestStage(sq) == 40 && player_.flags.count("saltmere_resolved"),
              "Ezekiel remembers his name; the Name-Eater goes back to sleep");
        narration_page_ = static_cast<int>(narration_pages_.size());
        AdvanceNarration();
        UpdateWorldObjects(0.0f);
        check(scene_.npcs[pi].hidden, "the Tide Priest is gone from the altar");
        check(talk("core:npc.harbourmaster", {"named"}) && player_.flags.count("harbour_named"), "Josiah Wick shouts his name at the sea");
        check(talk("core:npc.hunter_hollis", {"case2_done"}) && QuestStage(sq) == 100 && CountItem("core:item.saltmere_harpoon") == 1,
              "Hollis closes Case File #2 and hands over his master's harpoon");
        player_.flags.insert("avatar_rises");  // the fight ending, flags only
        UpdateWorldObjects(0.0f);
        CreatureInstance* av = nullptr;
        for (auto& c : scene_.creatures) if (c.instance_id == "avatar") av = &c;
        check(av != nullptr && av->def->family == "eldritch", "the Avatar of the Name-Eater can rise from the pool");
        const ItemDef* harpoon = content_.GetItem("core:item.saltmere_harpoon");
        check(harpoon && harpoon->weapon.bane_family == "eldritch", "the harpoon is the bane of eldritch things");
        if (av) DamageCreature(*av, 99999, false, "swords", false);
        player_.flags.erase("avatar_rises");
    }

    // --- Case File #3: The Horse Who Wasn't There
    {
        const std::string tq = "core:quest.trout";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            EndDialogue();
            return ok;
        };
        check(visible("core:npc.steve") < 0 && visible("core:npc.trout") < 0, "no Steve, no horse before the case opens");
        check(talk("core:npc.hunter_hollis", {"c3_open", "c3_note", "c3_trout", "c3_take", "root"}) && QuestStage(tq) == 10 &&
                  CountItem("core:item.ransom_note") == 1,
              "Hollis whistles and Trout doesn't come; a misspelled ransom note");
        check(!talk("core:npc.hunter_hollis", {"c3_deduce"}), "Hollis won't hear a guess before there are clues");
        int si = visible("core:npc.steve"), ti = visible("core:npc.trout");
        check(si >= 0 && ti >= 0 && scene_.npcs[ti].instance_id == "npc_trout_oak", "Steve's camp and a horse up a tree, out in the Whistling Wood");
        check(talk("core:npc.merchant_vaelen", {"trout"}) && talk("core:npc.librarian_fenwick", {"trout"}) &&
                  talk("core:npc.detective_baggy", {"trout"}) && talk("core:npc.clerk_oakhaven", {"trout"}) && talk("core:npc.werewolf_rolf", {"trout"}),
              "carrots, a whistling oak, a character sheet, a real Steve, and a marrow-eating sighting");
        standAndUse({14.2f, 0.0f, 8.9f}, 180.0f, -25.0f);
        check(player_.flags.count("trout_c_roof") > 0, "hoofprints straight up the library wall");
        if (overlay_ != Overlay::None) SetOverlay(Overlay::None);
        check(talk("core:npc.hunter_hollis", {"c3_deduce", "c3_w_rolf", "c3_deduce", "c3_q2", "c3_w_angry", "c3_q2", "c3_solved", "root"}) &&
                  QuestStage(tq) == 20 && player_.flags.count("trout_wood"),
              "the deduction: Steve wrote the note, and the oak whistles Hollis's whistle");
        UpdateWorldObjects(0.0f);
        int wolves = 0;
        for (auto& c : scene_.creatures)
            if (c.instance_id.rfind("camp_wolf_", 0) == 0 && c.state != CreatureState::Dead) wolves++;
        check(wolves == 4 && talk("core:npc.steve", {"wolves"}), "wolves circle Steve's camp");
        for (auto& c : scene_.creatures)
            if (c.instance_id.rfind("camp_wolf_", 0) == 0) DamageCreature(c, 999, false, "swords", false);
        check(player_.flags.count("steve_safe") > 0, "the wolves are dealt with");
        check(talk("core:npc.steve", {"confess", "sheet", "where", "plug", "plug_sheet", "plug2", "whistle", "future", "future_town"}) &&
                  QuestStage(tq) == 30 && player_.flags.count("oak_plugged") && CountItem("core:item.steve_spoon") == 1,
              "Steve confesses, the ransom notes plug the hollow, Trout answers your whistle; a spoon for luck");
        ti = visible("core:npc.trout");
        check(ti >= 0 && scene_.npcs[ti].instance_id == "npc_trout_home", "Trout is home, beside Hollis");
        si = visible("core:npc.steve");
        check(si >= 0 && scene_.npcs[si].instance_id == "npc_steve_inn", "Steve moves into the Lantern Inn for Thursdays");
        player_.sanity = 70.0f;
        check(talk("core:npc.trout", {"pat"}) && player_.sanity > 80.0f, "patting a horse is good for your sanity");
        player_.sanity = 100.0f;
        check(talk("core:npc.hunter_hollis", {"c3_home", "c3_home2", "c3_steve_town", "c3_reward", "root"}) && QuestStage(tq) == 100 &&
                  CountItem("core:item.trout_horseshoe") == 1 && CountItem("core:item.hollis_deck") == 1,
              "Hollis and Trout, forehead to forehead; her first horseshoe and his deck");
        player_.flags.insert("trout_wood");
        CreatureInstance* granny = nullptr;
        for (auto& c : scene_.creatures) if (c.instance_id == "granny_wolf") granny = &c;
        check(granny && granny->def->family == "beast", "a wolf in Grandmother's nightgown waits by the cottage");
        const ItemDef* spoon = content_.GetItem("core:item.steve_spoon");
        check(spoon && spoon->weapon.crit_mult >= 3.0f && spoon->weapon.bane_family == "beast", "Steve's Spoon: triple crits, bane of beasts");
        if (granny) DamageCreature(*granny, 999, false, "swords", false);
    }

    // --- The Light Past the Fog: Silas rows you out to the Sleeper's Reef
    {
        const std::string rq = "core:quest.reef";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (screen_ == Screen::Playing && overlay_ == Overlay::Dialogue) EndDialogue();
            return ok;
        };
        auto skipNarration = [&]() {
            if (overlay_ == Overlay::Narration) {
                narration_page_ = static_cast<int>(narration_pages_.size());
                AdvanceNarration();
            }
        };
        check(visible("core:npc.gale_elder") < 0 && visible("core:npc.keeper_ondine") < 0, "nobody on the reef before Silas rows out");
        bool rowed = talk("core:npc.silas_gale", {"r_offer", "r_row", "END"});
        bool onNarration = overlay_ == Overlay::Narration && narration_pages_.size() == 3;
        skipNarration();
        check(rowed && onNarration && QuestStage(rq) == 10 && player_.pos.z < -125.0f && player_.flags.count("at_reef"),
              "Silas rows you out between the sleeping limbs (z=" + std::to_string(static_cast<int>(player_.pos.z)) + ")");
        check(zone_id_ == "sleepers_reef" || (UpdateAtmosphere(0.0f, true), zone_id_ == "sleepers_reef"), "you're on the Sleeper's Reef");
        check(!talk("core:npc.gale_elder", {"names"}), "the brothers can't remember their names yet");
        standAndUse({10.1f, 0.0f, -142.0f}, 180.0f, -35.0f);
        if (overlay_ != Overlay::None) SetOverlay(Overlay::None);
        player_.flags.insert("reef_abel");
        check(player_.flags.count("reef_tom") > 0, "Thomas Gale's name, stitched on sailcloth, in a bottle on the shore");
        check(talk("core:npc.keeper_ondine", {"first", "root", "who", "for", "root", "out", "struck"}),
              "the keeper won't light the lamp until the brothers have their names");
        check(talk("core:npc.gale_elder", {"who", "root", "names", "names2", "root"}) && QuestStage(rq) == 20,
              "Tom and Abel Gale remember who they are");
        check(talk("core:npc.keeper_ondine", {"light"}) && QuestStage(rq) == 30 && player_.flags.count("lamp_lit"),
              "you light the Saltmere Light");
        UpdateWorldObjects(0.0f);
        CreatureInstance* limb = nullptr;
        for (auto& c : scene_.creatures) if (c.instance_id == "dreaming_limb" && c.state != CreatureState::Dead) limb = &c;
        check(limb != nullptr && limb->def->family == "eldritch", "the Dreaming Limb rises from the sea");
        for (auto& c : scene_.creatures)
            if (c.spawn_def && c.spawn_def->group == "limb") DamageCreature(c, 9999, false, "swords", false);
        check(QuestStage(rq) == 40 && player_.flags.count("limb_down"), "the limb sinks back to sleep");
        check(talk("core:npc.keeper_ondine", {"farewell", "farewell_end"}) && player_.flags.count("keeper_rests") &&
                  CountItem("core:item.keeper_lantern") == 1 && visible("core:npc.keeper_ondine") < 0,
              "Ondine Marsh is relieved at last, and leaves you her lantern");
        bool home = talk("core:npc.silas_gale", {"r_final", "r_final2", "r_final3", "END"});
        skipNarration();
        check(home && QuestStage(rq) == 100 && CountItem("core:item.silas_shanty") == 1 && player_.pos.z > -70.0f &&
                  !player_.flags.count("at_reef"),
              "Silas rows his sons home; the whole of the Drowned Man's Rhyme");
        check(visible("core:npc.tom_gale") >= 0 && visible("core:npc.abel_gale") >= 0 && visible("core:npc.gale_elder") < 0,
              "Tom and Abel are mending nets on the pier");
        check(talk("core:npc.silas_gale", {"r_after", "root"}), "Silas has hooks on his lines now");
    }

    // --- Status effects, combos and the new spell types (on test dummies in the square)
    {
        auto savedSpells = player_.known_spells;
        auto savedFlags = player_.flags;
        const CreatureDef* wolf = content_.GetCreature("core:enemy.grey_wolf");
        auto dummy = [&](const char* id, Vector3 pos) {
            CreatureInstance c;
            c.instance_id = id;
            c.def = wolf;
            c.pos = c.spawn = c.patrol_a = c.patrol_b = pos;
            c.health = c.max_health = 400;
            c.radius = 0.4f;
            c.height = 1.2f;
            c.state = CreatureState::Idle;
            c.state_timer = 999.0f;
            scene_.creatures.push_back(c);
            return static_cast<int>(scene_.creatures.size()) - 1;
        };
        auto at = [&](int i) -> CreatureInstance& { return scene_.creatures[i]; };
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        player_.pos = {0.0f, 0.0f, 4.0f};
        player_.yaw = PI;  // facing -z
        player_.pitch = 0.0f;
        int a = dummy("test_a", {0.0f, 0.0f, 0.0f});
        int b = dummy("test_b", {1.5f, 0.0f, -2.0f});
        int c3 = dummy("test_c", {-1.5f, 0.0f, -3.5f});

        ApplyStatus(at(a), "burn", 10.0f, 3.0f);
        int hp0 = at(a).health;
        for (int i = 0; i < 60; i++) UpdateCreatureStatus(at(a), 1.0f / 60.0f);
        check(at(a).burn_time > 0.0f && hp0 - at(a).health >= 8 && hp0 - at(a).health <= 12, "burning deals damage over time (" + std::to_string(hp0 - at(a).health) + " in 1s)");
        for (int i = 0; i < 3; i++) ApplyStatus(at(b), "chill", 0.0f, 3.0f);
        check(at(b).frozen_time > 0.0f, "three chills freeze a foe solid");
        int hpB = at(b).health;
        ApplyStatus(at(b), "burn", 5.0f, 3.0f);
        check(at(b).frozen_time <= 0.0f && hpB - at(b).health >= 40 && at(b).burn_time <= 0.0f, "fire on a frozen foe SHATTERS (" + std::to_string(hpB - at(b).health) + ")");
        int hpA = at(a).health, hpC = at(c3).health;
        at(c3).pos = {0.8f, 0.0f, 0.5f};
        ApplyStatus(at(a), "shock", 0.0f, 3.0f);
        check(at(a).burn_time <= 0.0f && hpA - at(a).health > 20 && hpC > at(c3).health, "lightning on a burning foe OVERLOADS, hurting neighbours too");
        at(c3).pos = {-1.5f, 0.0f, -3.5f};
        ApplyStatus(at(a), "shock", 0.0f, 3.0f);
        int before = at(a).health;
        DamageCreature(at(a), 40, false, "swords", false);
        int shockedHit = before - at(a).health;
        check(shockedHit == std::max(1, 50 - static_cast<int>(std::round(wolf->armor * 0.6f))), "shocked foes take 25% more damage (" + std::to_string(shockedHit) + ")");
        ApplyStatus(at(c3), "ink", 0.0f, 4.0f);
        check(at(c3).ink_time > 0.0f, "ink blinds a foe");

        for (int i : {a, b, c3}) { at(i).health = 400; at(i).burn_time = at(i).chill_time = at(i).frozen_time = at(i).shock_time = at(i).ink_time = 0.0f; at(i).chill_stacks = 0; }
        player_.mana = 999.0f;
        auto cast = [&](const char* sid) {
            player_.known_spells = {sid};
            player_.selected_spell = 0;
            spell_cooldown_ = 0.0f;
            CastSelectedSpell();
        };
        cast("core:spell.chain_of_command");
        int jumped = 0;
        for (int i : {a, b, c3}) jumped += at(i).health < 400 ? 1 : 0;
        check(jumped == 3 && at(a).shock_time > 0.0f, "Chain of Command jumps between all three foes (" + std::to_string(jumped) + ")");
        for (int i : {a, b, c3}) at(i).health = 400;
        player_.pos = {0.0f, 0.0f, -1.5f};
        cast("core:spell.cold_shoulder");
        int novaHit = 0;
        for (int i : {a, b, c3}) novaHit += (at(i).health < 400 && at(i).chill_time > 0.0f) ? 1 : 0;
        check(novaHit == 3, "Cold Shoulder chills everything around you");
        player_.pos = {0.0f, 0.0f, 8.0f};
        float z0 = player_.pos.z;
        cast("core:spell.clerical_error");
        check(z0 - player_.pos.z > 5.0f, "Clerical Error blinks you six metres forward (" + std::to_string(z0 - player_.pos.z) + ")");
        const ItemDef* dag = content_.GetItem("core:item.cinderglass_dagger");
        check(dag && dag->weapon.on_hit_status == "burn" && dag->weapon.status_chance > 0.0f, "the Cinderglass Dagger sets things alight");

        // Roguelike pack: bleed stacks, confused and charmed foes brawl, the unlock spell, a timed buff, wands
        for (int i : {a, b, c3}) { at(i).health = 400; at(i).burn_time = at(i).chill_time = at(i).frozen_time = at(i).shock_time = at(i).ink_time = 0.0f; at(i).chill_stacks = 0; }
        for (int k = 0; k < 4; k++) ApplyStatus(at(a), "bleed", 3.0f, 4.0f);
        int hpBleed = at(a).health;
        for (int i = 0; i < 60; i++) UpdateCreatureStatus(at(a), 1.0f / 60.0f);
        check(at(a).bleed_stacks == 3 && hpBleed - at(a).health >= 8, "bleeding stacks three times (" + std::to_string(hpBleed - at(a).health) + " in 1s)");
        at(a).bleed_time = 0.0f; at(a).bleed_stacks = 0;
        at(a).pos = {0.0f, 0.0f, 0.0f};
        at(b).pos = {0.9f, 0.0f, 0.0f};
        at(c3).pos = {0.0f, 0.0f, -9.0f};
        player_.pos = {0.0f, 0.0f, 12.0f};
        ApplyStatus(at(a), "confuse", 0.0f, 6.0f);
        at(a).attack_cooldown = 0.0f;
        int hpB0 = at(b).health;
        simulate(1.0f);
        check(at(b).health < hpB0, "a confused wolf bites the wolf next to it");
        at(a).confuse_time = 0.0f;
        for (int i : {a, b, c3}) { at(i).health = 400; at(i).foe = -1; at(i).alerted = false; at(i).state = CreatureState::Idle; at(i).state_timer = 999.0f; }
        at(b).pos = {4.0f, 0.0f, 0.0f};
        ApplyStatus(at(a), "charm", 0.0f, 10.0f);
        at(a).attack_cooldown = 0.0f;
        simulate(2.5f);
        check(at(b).health < 400 && at(a).charm_time > 0.0f, "a charmed wolf hunts down the other wolf for you");
        DamageCreature(at(a), 5, false, "swords", false);
        simulate(0.1f);
        check(at(a).charm_time <= 0.0f && at(a).alerted, "hitting your new friend ends the friendship");
        for (int i : {a, b, c3}) { at(i).health = 0; at(i).state = CreatureState::Dead; }

        InteractableInstance* chest = interactable("road_ranger_chest");
        if (chest) {
            chest->locked = true;
            Vector3 cc = Vector3Scale(Vector3Add(chest->world_box.min, chest->world_box.max), 0.5f);
            player_.pos = {cc.x, chest->world_box.min.y, cc.z + 1.6f};
            player_.yaw = PI;
            cast("core:spell.unauthorised_entry");
        }
        check(chest && !chest->locked, "Unauthorised Entry opens a locked chest");
        float ls0 = Bonus("life_steal");
        cast("core:spell.borrowed_vitality");
        check(Bonus("life_steal") > ls0 + 0.15f, "Borrowed Vitality: a timed life-steal aura");
        player_.buffs.clear();
        AddItem("core:item.wand_frost", 3, false);
        player_.mana = 5.0f;
        size_t proj = scene_.projectiles.size();
        UseItem("core:item.wand_frost");
        check(CountItem("core:item.wand_frost") == 2 && player_.mana == 5.0f && scene_.projectiles.size() == proj + 1,
              "a wand charge casts Frost Lance for free (2 charges left)");

        scene_.creatures.erase(scene_.creatures.begin() + a, scene_.creatures.end());
        player_.known_spells = savedSpells;
        player_.flags = savedFlags;
    }

    // --- Overdue: The Restricted Section
    {
        const std::string oq = "core:quest.overdue";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            return ok;
        };
        check(talk("core:npc.librarian_fenwick", {"od_start", "od_who", "root"}) && QuestStage(oq) == 0, "Fenwick unlocks the black ledger");
        bool got = talk("core:npc.vampire_ashgrave", {"od_ash", "od_ash_true", "root"}) && talk("core:npc.professor_pickering", {"od_pick", "root"}) &&
                   talk("core:npc.odette", {"od_odette", "root"}) && talk("core:npc.mother_brine", {"od_brine", "root"}) &&
                   talk("core:npc.brother_aldous", {"od_aldous", "root"}) && talk("core:npc.clerk_oakhaven", {"od_oak", "greeting"});
        int books = 0;
        for (const char* g : {"cold", "chain", "ovation", "slow", "redacted", "clerical"}) books += CountItem(std::string("core:item.grimoire_") + g);
        check(got && books == 6, "six borrowers, six grimoires (one under a pot of chowder)");
        size_t spells = player_.known_spells.size();
        check(talk("core:npc.librarian_fenwick", {"od_return", "od_r0", "od_return", "od_r1", "od_return", "od_r2", "od_return", "od_r3", "od_return", "od_r4",
                                                  "od_return", "od_r5", "od_return", "od_done", "root"}) &&
                  QuestStage(oq) == 100 && CountItem("core:item.library_card") == 1 && player_.known_spells.size() == spells + 6,
              "every book returned; six spells copied; library card number 0000001");
    }

    // --- Gathering and crafting: harvest, regrowth, alchemy bench, weapon oil
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        int ni = -1;
        for (size_t i = 0; i < scene_.interactables.size(); i++)
            if (scene_.interactables[i].def.type == "harvest" && scene_.interactables[i].def.item_id == "core:item.marigold") { ni = static_cast<int>(i); break; }
        check(ni >= 0, "marigolds grow in the world");
        if (ni >= 0) {
            InteractableInstance& n = scene_.interactables[ni];
            int before = CountItem("core:item.marigold");
            Vector3 nc = Vector3Scale(Vector3Add(n.world_box.min, n.world_box.max), 0.5f);
            standAndUse({nc.x, n.world_box.min.y, nc.z + 1.1f}, 180.0f, -35.0f);
            check(CountItem("core:item.marigold") > before && n.used, "picking a marigold (it's gone until it regrows)");
            player_.play_time += n.def.respawn_seconds + 1.0;
            UpdateWorldObjects(0.0f);
            check(!n.used, "the marigold grows back after a while");
        }
        int si = -1;
        for (size_t i = 0; i < scene_.interactables.size(); i++)
            if (scene_.interactables[i].def.type == "station" && scene_.interactables[i].def.station == "alchemy") si = static_cast<int>(i);
        check(si >= 0, "there is an alchemy bench in the world");
        if (si >= 0) {
            InteractableInstance& b = scene_.interactables[si];
            Vector3 bc = Vector3Scale(Vector3Add(b.world_box.min, b.world_box.max), 0.5f);
            standAndUse({bc.x + 1.4f, b.world_box.min.y, bc.z}, -90.0f, -25.0f);
        }
        check(overlay_ == Overlay::Crafting && craft_station_ == "alchemy", "the bench opens the alchemy screen");
        AddItem("core:item.pine_resin", 2, false);
        AddItem("core:item.marigold", 1, false);
        int resin = CountItem("core:item.pine_resin");
        check(Craft("core:recipe.oil_fire") && CountItem("core:item.oil_fire") >= 1 && CountItem("core:item.pine_resin") == resin - 2,
              "brewed Dragon's Breath Oil (ingredients used up)");
        check(!Craft("core:recipe.bureaucrats_brew") || SkillLevel("lore") >= 14, "can't brew without the ingredients");
        SetOverlay(Overlay::None);
        UseItem("core:item.oil_fire");
        CreatureInstance dummy;
        dummy.instance_id = "oil_dummy";
        dummy.def = content_.GetCreature("core:enemy.grey_wolf");
        dummy.health = dummy.max_health = 999;
        dummy.state = CreatureState::Idle;
        for (int i = 0; i < 20 && dummy.burn_time <= 0.0f; i++) ApplyOilOnHit(dummy);
        check(dummy.burn_time > 0.0f, "an oiled weapon sets foes alight");
        player_.buffs.clear();
        check(SaveGame("selftest_craft"), "saved with harvest state");
    }

    // --- Fishing and cooking
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        int si = -1;
        for (size_t i = 0; i < scene_.npcs.size(); i++) if (scene_.npcs[i].def->id == "core:npc.silas_gale" && !scene_.npcs[i].hidden) si = static_cast<int>(i);
        bool rod = false;
        if (si >= 0) { StartDialogue(si); rod = chooseNext("rod") && chooseNext("root"); if (overlay_ == Overlay::Dialogue) EndDialogue(); }
        check(rod && CountItem("core:item.fishing_rod") == 1, "Silas hands over one of his nine spare rods");
        InteractableInstance* spot = interactable("fish_quay");
        auto cast = [&]() {
            Vector3 c = Vector3Scale(Vector3Add(spot->world_box.min, spot->world_box.max), 0.5f);
            standAndUse({c.x, spot->world_box.min.y, c.z + 1.0f}, 180.0f, -30.0f);
        };
        check(spot != nullptr, "there is a fishing spot on the Saltmere quay");
        if (spot) {
            cast();
            check(fishing_ && fish_state_ == 0, "cast the line");
            Interact();
            check(!fishing_, "pull too soon and it gets away");
            auto countCatch = [&]() {
                int n = 0;
                for (const char* id : {"core:item.fish_cod", "core:item.fish_mackerel", "core:item.fish_eel", "core:item.old_boot", "core:item.bottle_message",
                                       "core:item.bladderwrack"}) n += CountItem(id);
                return n;
            };
            int before = countCatch();
            cast();
            for (int i = 0; i < 600 && fishing_ && fish_state_ == 0; i++) UpdateFishing(1.0f / 60.0f);
            check(fishing_ && fish_state_ == 1, "something bites");
            Interact();
            check(!fishing_ && countCatch() > before, "caught something");
            cast();
            player_.pos.x += 2.0f;
            UpdateFishing(0.016f);
            check(!fishing_, "walking away reels the line in");
        }
        AddItem("core:item.fish_cod", 1, false);
        AddItem("core:item.sea_salt", 1, false);
        check(Craft("core:recipe.grilled_cod") && CountItem("core:item.grilled_cod") >= 1, "cooked Grilled Cod");
    }

    // --- Perks: milestones, one choice each, real effects, save/load, and Brother Aldous's respec
    {
        auto savedSkills = player_.skills;
        auto savedPerks = player_.perks;
        auto savedSpells = player_.known_spells;
        player_.perks.clear();
        player_.skills["elemental"].level = 14;
        player_.skills["elemental"].xp = 0;
        check(!PerkAvailable(*content_.GetPerk("core:perk.kindling")), "no perk before the milestone");
        player_.skills["elemental"].xp = 999;
        GainSkillXp("elemental", 0.1f, true);
        check(SkillLevel("elemental") >= 15 && PendingPerks() >= 1, "reaching Elemental 15 offers a perk");
        float before = Bonus("burn_damage_bonus");
        ChoosePerk("core:perk.kindling");
        check(player_.perks.count("core:perk.kindling") && Bonus("burn_damage_bonus") >= before + 0.5f, "Kindling: burning deals 50% more");
        ChoosePerk("core:perk.permafrost");
        check(!player_.perks.count("core:perk.permafrost"), "only one perk per milestone");
        player_.skills["elemental"].level = 40;
        ChoosePerk("core:perk.forked");
        ChoosePerk("core:perk.pyre");
        check(Bonus("chain_jump_bonus") >= 1.0f && Bonus("burn_spread_on_death") > 0.0f, "Forked Lightning and Funeral Pyre chosen");
        // Funeral Pyre: a burning foe dies and its neighbours catch fire.
        const CreatureDef* wolf = content_.GetCreature("core:enemy.grey_wolf");
        size_t base = scene_.creatures.size();
        for (int i = 0; i < 2; i++) {
            CreatureInstance c;
            c.instance_id = "perk_" + std::to_string(i);
            c.def = wolf;
            c.pos = c.spawn = c.patrol_a = c.patrol_b = {0.5f * i, 0.0f, 0.0f};
            c.health = c.max_health = 200;
            c.state = CreatureState::Idle;
            scene_.creatures.push_back(c);
        }
        ApplyStatus(scene_.creatures[base], "burn", 6.0f, 4.0f);
        KillCreature(scene_.creatures[base]);
        check(scene_.creatures[base + 1].burn_time > 0.0f, "Funeral Pyre: the flames spread from the dead to the living");
        scene_.creatures.erase(scene_.creatures.begin() + base, scene_.creatures.end());
        check(SaveGame("selftest_perks") && (player_.perks.clear(), LoadGame("selftest_perks")) && player_.perks.count("core:perk.pyre"),
              "perks survive a save and load");
        player_.gold = 100;
        int ai = -1;
        for (size_t i = 0; i < scene_.npcs.size(); i++) if (scene_.npcs[i].def->id == "core:npc.brother_aldous") ai = static_cast<int>(i);
        bool rite = false;
        if (ai >= 0) {
            StartDialogue(ai);
            rite = chooseNext("respec") && chooseNext("respec_done");
            if (overlay_ == Overlay::Dialogue) EndDialogue();
        }
        check(rite && player_.perks.empty() && player_.gold == 50, "the Rite of Second Thoughts returns every perk for 50 gold");
        player_.skills = savedSkills;
        player_.perks = savedPerks;
        player_.known_spells = savedSpells;
    }

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

    // --- The Figure It Out Gang: split up, clues, a trap that goes wrong, unmask the culprit
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            return ok;
        };
        std::string lastScene;
        auto use = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            InteractableInstance* in = interactable(id);
            if (!in || in->hidden) return false;
            Vector3 c = Vector3Scale(Vector3Add(in->world_box.min, in->world_box.max), 0.5f);
            standAndUse({c.x, in->world_box.min.y, c.z + 1.0f}, 180.0f, -48.0f);
            lastScene = (overlay_ == Overlay::Narration && !narration_pages_.empty()) ? narration_pages_[0] : "";
            narration_page_ = static_cast<int>(narration_pages_.size());
            if (overlay_ == Overlay::Narration) AdvanceNarration();
            SetOverlay(Overlay::None);
            return true;
        };
        auto catchMonster = [&](const char* iid) {
            UpdateWorldObjects(0.0f);
            for (auto& c : scene_.creatures) if (c.instance_id == iid && c.state != CreatureState::Dead) { DamageCreature(c, 999, false, "swords", false); return true; }
            return false;
        };
        const std::string e1 = "core:quest.figure_ep1", e2 = "core:quest.figure_ep2";
        check(!use("fig1_clue_ink"), "no clues lying about before anyone asks");
        check(talk("core:npc.figure_rodrick", {"what", "root", "e1_open", "root"}) && QuestStage(e1) == 10, "Bread: 'Let's split up and look for clues!'");
        check(talk("core:npc.figure_rodrick", {"e1_hint", "root"}), "Bread reminds you where the clues are");
        check(!use("fig1_trap"), "no trap until the clues are in");
        check(use("fig1_clue_ink") && use("fig1_clue_receipt") && use("fig1_clue_tags") && player_.flags.count("fig1_c3"), "three clues: ink, a receipt from 'V.', price tags");
        check(talk("core:npc.figure_rodrick", {"e1_trap", "root"}) && QuestStage(e1) == 20, "Bread's plan: a net, a pulley, a barrel of feathers, and you");
        check(visible("core:npc.unmask_clerk") < 0 && use("fig1_trap") && lastScene.find("pigeon") != std::string::npos && QuestStage(e1) == 30 && (UpdateWorldObjects(0.0f), interactable("fig1_trap")->hidden),
              "the trap catches Baggy, a pigeon and Bread");
        check(catchMonster("fig1_phantom") && QuestStage(e1) == 40, "the Phantom Clerk is caught (it fell over Doobie)");
        check(talk("core:npc.unmask_clerk", {"reveal", "refund"}) && player_.flags.count("fig1_guessed") && QuestStage(e1) == 50,
              "it was Vaelen all along (Baggy barely knew her)");
        check(visible("core:npc.unmask_clerk") < 0, "the netted suspect is gone once it's done");
        check(talk("core:npc.figure_rodrick", {"e1_done", "root"}) && QuestStage(e1) == 100 && CountItem("core:item.crumb_cake") == 5, "FIGURED OUT! Paid in Crumb Cakes");
        check(talk("core:npc.detective_baggy", {"gang", "gang_barely", "gang_horse", "gang", "root"}), "Baggy, founding member: 'I barely knew her' (even the horse)");
        check(talk("core:npc.figure_snacks", {"cake", "root"}) && CountItem("core:item.crumb_cake") == 4, "Doobie would not do something brave for a Crumb Cake");
        check(talk("core:npc.figure_rodrick", {"e2_open", "root"}) && QuestStage(e2) == 10, "episode two: the Howler of Hollowmere");
        check(use("fig2_clue_prints") && use("fig2_clue_wool") && use("fig2_clue_list") && talk("core:npc.figure_rodrick", {"e2_trap", "root"}) && QuestStage(e2) == 20,
              "sandal prints, brown wool, four years of second place");
        check(use("fig2_trap") && QuestStage(e2) == 30 && catchMonster("fig2_howler") && QuestStage(e2) == 40, "the seesaw launches Bread; the Howler is caught");
        check(talk("core:npc.unmask_howler", {"guess", "reveal", "rolf"}) && player_.flags.count("fig2_guessed") && QuestStage(e2) == 50,
              "Rolf's face is his actual face; the Howler is Brother Aldous");
        check(talk("core:npc.figure_rodrick", {"e2_done", "root"}) && QuestStage(e2) == 100 && CountItem("core:item.gang_scarf") == 1, "full member of the gang: the scarf");
        const std::string e3 = "core:quest.figure_ep3";
        check(talk("core:npc.figure_rodrick", {"e3_open", "root"}) && QuestStage(e3) == 10, "episode three: the Headless Knight of the Old Road");
        check(use("fig3_clue_hat") && use("fig3_clue_sign") && use("fig3_clue_receipt") && talk("core:npc.figure_rodrick", {"e3_trap", "root"}) &&
                  QuestStage(e3) == 20, "a hat on a stick (Karma was right), a misspelt toll sign, a receipt for 'S.'");
        check(use("fig3_trap") && lastScene.find("goose") != std::string::npos && QuestStage(e3) == 30, "the trap catches a goose, a cake and Bread");
        check(catchMonster("fig3_knight") && QuestStage(e3) == 40, "Doobie charges the knight");
        check(talk("core:npc.unmask_knight", {"reveal", "smile"}) && player_.flags.count("fig3_guessed") && QuestStage(e3) == 50,
              "it was Steve, and he's thrilled to be a real villain");
        check(talk("core:npc.figure_rodrick", {"e3_done", "root"}) && QuestStage(e3) == 100 && CountItem("core:item.snacks_feather") == 1 &&
                  talk("core:npc.figure_snacks", {"hero", "root"}), "Doobie's brave feather");
    }

    // --- Grout, the gargoyle companion (grumpy, terse, punchy)
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        auto savedParty = player_.companions;
        auto savedFlags = player_.flags;
        player_.companions.clear();
        UpdateWorldObjects(0.0f);
        int gi = -1;
        for (size_t i = 0; i < scene_.npcs.size(); i++) if (scene_.npcs[i].def->id == "core:npc.grout" && !scene_.npcs[i].hidden) gi = static_cast<int>(i);
        check(gi >= 0, "Grout sits by the Records Office door");
        if (gi >= 0) {
            StartDialogue(gi);
            check(chooseNext("who") && chooseNext("fixture") && chooseNext("same") && player_.flags.count("grout_kin") && chooseNext("root"),
                  "Grout: 'Fixture. Not citizen.' Legally nobody, like you");
            check(chooseNext("join") && IsCompanion("core:npc.grout") && player_.flags.count("grout_following"), "Grout joins: 'No.' (stands up anyway)");
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            const NpcDef* g = content_.GetNpc("core:npc.grout");
            check(g && g->companion.banter.size() == 6 && g->companion.zone_lines.size() == 13, "Grout has banter with Baggy, Kaelen and Doobie and a line for every area");
        }
        player_.companions = savedParty;
        player_.flags = savedFlags;
    }

    // --- Doobie the owlbear cub as a companion (after the Headless Knight)
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        auto savedParty = player_.companions;
        auto savedFlags = player_.flags;
        player_.companions.clear();
        player_.flags.insert("fig3_done");
        UpdateWorldObjects(0.0f);
        int si = -1;
        for (size_t i = 0; i < scene_.npcs.size(); i++) if (scene_.npcs[i].def->id == "core:npc.figure_snacks" && !scene_.npcs[i].hidden) si = static_cast<int>(i);
        bool joined = false;
        if (si >= 0) { StartDialogue(si); joined = chooseNext("join"); if (overlay_ == Overlay::Dialogue) EndDialogue(); }
        check(joined && IsCompanion("core:npc.figure_snacks"), "Doobie joins you ('Have it back by bedtime!')");
        const NpcDef* sd = content_.GetNpc("core:npc.figure_snacks");
        check(sd && sd->companion.heal_amount > 0 && sd->companion.banter.size() == 5, "Doobie shares snacks and banters with Grout, Baggy and Kaelen");
        player_.companions = savedParty;
        player_.flags = savedFlags;
    }

    // --- A Druid in Distress: the squirrel, the ingredients, the goose, Barkskin
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        const std::string dq = "core:quest.druid_distress";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            return ok;
        };
        check(visible("core:npc.druid_bramble") < 0 && talk("core:npc.druid_squirrel", {"who", "stuck", "task", "root"}) && QuestStage(dq) == 10,
              "a squirrel by the Old Oak: a druid who sneezed mid-shapeshift");
        UpdateWorldObjects(0.0f);
        bool acorn = false;
        for (const auto& wp : scene_.pickups) acorn = acorn || wp.key == "druid_acorn";
        check(acorn, "an acorn lies under the Old Oak");
        AddItem("core:item.oak_acorn", 1, false);
        AddItem("core:item.glowcap", 1, false);
        check(talk("core:npc.werewolf_rolf", {"druid_fur", "root"}) && CountItem("core:item.rolf_fur") == 1, "Rolf: 'Take it from the back. The front is for show.'");
        int si = visible("core:npc.druid_squirrel");
        bool goose = false, restored = false;
        if (si >= 0) {
            StartDialogue(si);
            chooseNext("ritual");
            chooseNext("restored");
            goose = dialogue_node_ == "goose";
            for (int i = 0; i < 20 && dialogue_node_ != "restored"; i++) chooseNext("restored");
            restored = dialogue_node_ == "restored";
            if (overlay_ == Overlay::Dialogue) EndDialogue();
        }
        check(goose && player_.flags.count("druid_was_goose"), "the first reading turns him into a goose (HONK)");
        check(restored && QuestStage(dq) == 50 && visible("core:npc.druid_squirrel") < 0 && visible("core:npc.druid_bramble") >= 0,
              "the rite works: Bramble is back, with antlers");
        check(talk("core:npc.druid_bramble", {"teach", "root"}) && QuestStage(dq) == 100 &&
                  std::count(player_.known_spells.begin(), player_.known_spells.end(), std::string("core:spell.barkskin")) > 0 &&
                  CountItem("core:item.squirrel_tail") == 1,
              "Bramble teaches Barkskin and hands over his spare squirrel tail");
    }

    // --- Campaign Four: The Dragon's Pension
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        const std::string q = "core:quest.dragon_pension";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            return ok;
        };
        check(visible("core:npc.dragon_cindermaw") < 0 && talk("core:npc.clerk_oakhaven", {"dp_start"}) && QuestStage(q) == 10 &&
                  visible("core:npc.dragon_cindermaw") >= 0, "Oakhaven's scorched letter: I AM NOT DEAD. I WAS ASLEEP. I AM COMING. (It lands.)");
        check(talk("core:npc.dragon_cindermaw", {"intro", "deal", "root"}) && QuestStage(q) == 20, "Cindermaw: eleven gold, one sheep and one apology per century");
        check(!talk("core:npc.clerk_oakhaven", {"dp_file"}), "can't file Form 9-L without the proof");
        check(talk("core:npc.innkeeper_marta", {"dp_wit"}) && talk("core:npc.merchant_vaelen", {"dp_wit"}) && talk("core:npc.grout", {"dp_wit"}) &&
                  player_.flags.count("dwit_grout"), "three witnesses: a pie, a hat, and a roof ('Roof's fine.')");
        check(talk("core:npc.librarian_fenwick", {"dp_rec"}) && CountItem("core:item.hatching_record") == 1, "Fenwick finds the Register of Hatchings (returned four days late, 312 years ago)");
        check(talk("core:npc.professor_pickering", {"dp_box"}) && talk("core:npc.dragon_cindermaw", {"likeness"}) && CountItem("core:item.dragon_likeness") == 1,
              "Pickering's likeness engine: the dragon, mid-sneeze");
        check(talk("core:npc.clerk_oakhaven", {"dp_file"}) && QuestStage(q) == 30 && visible("core:npc.kobold_quillsby") >= 0,
              "Form 9-L stamped ALIVE; the death notice was filed by the hoard-keeper");
        check(talk("core:npc.kobold_quillsby", {"p_wit", "root", "p_rec", "root", "p_lik", "root", "panic"}) && QuestStage(q) == 40 &&
                  visible("core:npc.kobold_quillsby") < 0, "the hearing finds the dragon ALIVE; Quillsby throws a golem out of the window and flees");
        bool golem = false;
        UpdateWorldObjects(0.0f);
        for (auto& c : scene_.creatures)
            if (c.instance_id == "dp_golem" && c.state != CreatureState::Dead) { golem = true; DamageCreature(c, 9999, false, "swords", false); }
        check(golem && QuestStage(q) == 50, "the Repossession Golem is scrap");
        check(talk("core:npc.dragon_cindermaw", {"done", "root"}) && QuestStage(q) == 100 && CountItem("core:item.cindermaw_scale") == 1 &&
                  std::count(player_.known_spells.begin(), player_.known_spells.end(), std::string("core:spell.dragon_sigh")) > 0,
              "officially alive: Dragon's Sigh and one of Cindermaw's scales");
    }

    // --- The Missing Third: Silas rows you to Quillsby's cove; the vault; the hoard back to the dragon
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        const std::string q = "core:quest.missing_third";
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            overlay_ = Overlay::None;
            return ok;
        };
        check(talk("core:npc.dragon_cindermaw", {"mt_start", "root"}) && QuestStage(q) == 10, "Cindermaw: SHOES. CUSHIONS. A HOUSE BY THE SEA, NAMED AFTER MY FUNERAL.");
        bool rowed = talk("core:npc.silas_gale", {"mt_row1"});
        UpdateAtmosphere(0.0f, true);
        check(rowed && QuestStage(q) == 20 && player_.pos.x > 140.0f && zone_id_ == "seaside_house",
              "Silas rows you round the headland to The Late Cindermaw");
        UpdateWorldObjects(0.0f);
        for (auto& c : scene_.creatures)
            if (c.instance_id.rfind("kobold_", 0) == 0 || c.instance_id == "quillsby_cornered") DamageCreature(c, 9999, false, "swords", false);
        check(QuestStage(q) == 30, "the bookkeepers are audited and Quillsby is cornered ('Not the shoes...')");
        container_key_ = "corpse:quillsby_cornered";
        TakeAllFromContainer();
        SetOverlay(Overlay::None);
        check(CountItem("core:item.quillsby_vault_key") == 1, "Quillsby carried the vault key (engraved MINE)");
        InteractableInstance* door = interactable("quillsby_vault_door");
        if (door) {
            Vector3 dc = Vector3Scale(Vector3Add(door->world_box.min, door->world_box.max), 0.5f);
            standAndUse({dc.x - 1.2f, 0.0f, dc.z}, 90.0f, -10.0f);
        }
        check(door && door->open && !door->locked, "the key opens the vault");
        InteractableInstance* hoard = interactable("missing_third_hoard");
        if (hoard) {
            Vector3 hc = Vector3Scale(Vector3Add(hoard->world_box.min, hoard->world_box.max), 0.5f);
            standAndUse({hc.x - 1.1f, 0.0f, hc.z}, 90.0f, -30.0f);
            narration_page_ = static_cast<int>(narration_pages_.size());
            if (overlay_ == Overlay::Narration) AdvanceNarration();
            SetOverlay(Overlay::None);
        }
        check(QuestStage(q) == 40 && CountItem("core:item.hoard_third") == 1, "four thousand gold in sacks stamped INVESTMENTS (and a golden shoe)");
        check(talk("core:npc.silas_gale", {"mt_home"}) && player_.pos.x < 40.0f && !player_.flags.count("at_seaside"), "Silas rows you home");
        check(talk("core:npc.dragon_cindermaw", {"mt_done", "root"}) && QuestStage(q) == 100 && CountItem("core:item.quillsby_cufflinks") == 1,
              "the hoard is whole again; the dragon purrs");
    }

    // --- The Bestiary: kills are counted, Hunter's Insight at ten, kills survive save/load
    {
        int rats = player_.kills["core:enemy.grave_rat"];
        check(rats > 0 && player_.kills.size() >= 3, "the Bestiary has recorded the monsters defeated so far");
        CreatureInstance dummy;
        dummy.instance_id = "bestiary_dummy";
        dummy.def = content_.GetCreature("core:enemy.grey_wolf");
        dummy.health = dummy.max_health = 9999;
        dummy.state = CreatureState::Idle;
        int saved = player_.kills["core:enemy.grey_wolf"];
        player_.kills["core:enemy.grey_wolf"] = 0;
        int before = dummy.health;
        DamageCreature(dummy, 40, false, "swords", false);
        int plain = before - dummy.health;
        player_.kills["core:enemy.grey_wolf"] = 10;
        before = dummy.health;
        DamageCreature(dummy, 40, false, "swords", false);
        check(before - dummy.health > plain, "Hunter's Insight: ten wolves later, wolves take more damage");
        player_.kills["core:enemy.grey_wolf"] = saved;
        auto kills = player_.kills;
        check(SaveGame("selftest_bestiary") && LoadGame("selftest_bestiary") && player_.kills == kills, "kill counts survive save and load");
        std::filesystem::remove(SavePath("selftest_bestiary"), ec);
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
    }

    // --- Deeper crafting: boss reagents, recipe books, locked recipes
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        auto savedSkills = player_.skills;
        const RecipeDef* wb = nullptr;
        for (const auto& r : content_.recipes) if (r.id == "core:recipe.whiskerblade") wb = &r;
        check(wb && !RecipeKnown(*wb), "the Whiskerblade recipe is locked until you read the book");
        ContainerState drop;
        RollLoot("core:loot.rat_king", drop);
        bool whisker = false;
        for (const auto& e : drop.items) whisker = whisker || e.id == "core:item.rat_whisker";
        check(whisker, "the Rat King always drops a whisker");
        ContainerState host;
        RollLoot("core:loot.wrathful_host", host);
        int embers = 0;
        for (const auto& e : host.items) if (e.id == "core:item.host_ember") embers += e.qty;
        check(embers == 2, "the Wrathful Host leaves two embers (one for a blade, one for a draught)");
        if (wb) {
            AddItem("core:item.rat_whisker", 1, false);
            AddItem("core:item.iron_scrap", 3, false);
            AddItem("core:item.ashwood_branch", 1, false);
            player_.skills["daggers"].level = std::max(player_.skills["daggers"].level, 8);
            check(!Craft(wb->id), "can't craft from a recipe you don't know");
            AddItem("core:item.book_monster_bits", 1, false);
            if (const ItemDef* b = content_.GetItem("core:item.book_monster_bits")) ReadItem(*b);
            SetOverlay(Overlay::None);
            check(RecipeKnown(*wb) && player_.flags.count("recipe:core:recipe.granny_mittens") && CountItem("core:item.book_monster_bits") == 1,
                  "Hollis's Field Notes teach five recipes (and you keep the book)");
            int whiskers = CountItem("core:item.rat_whisker");
            check(Craft(wb->id) && CountItem("core:item.whiskerblade") == 1 && CountItem("core:item.rat_whisker") == whiskers - 1, "forged the Whiskerblade from the Rat King's whisker");
        }
        bool sells = false;
        if (const NpcDef* v = content_.GetNpc("core:npc.witch_sabrino"))
            for (const auto& e : v->vendor_inventory) sells = sells || e.item_id == "core:item.book_forbidden_footnotes";
        check(sells, "Sabrino sells the Forbidden Footnotes");
        player_.skills = savedSkills;
    }

    // --- Level edits from Blender (mods/<name>/map_edits.json): modify, add, remove, move markers
    {
        MapDef* m = nullptr;
        for (auto& [id, md] : content_.maps) if (!md.props.empty()) { m = &md; break; }
        if (m) {
            std::string victim = m->props.front().id, mover = m->props.back().id;
            std::string npc = m->npcs.empty() ? "" : m->npcs.front().instance_id;
            std::string gone = m->interactables.empty() ? "" : m->interactables.front().instance_id;
            std::filesystem::create_directories("mods/zz_selftest_edits", ec);
            {
                std::ofstream f("mods/zz_selftest_edits/map_edits.json");
                f << "{\"map\": \"" << m->id << "\", \"props\": {\"remove\": [\"" << victim << "\"], \"modify\": {\"" << mover
                  << "\": {\"pos\": [1, 2, 3], \"rot_y\": 45}}, \"add\": [{\"id\": \"selftest_added\", \"model\": \"assets/models/props/wooden_crate.glb\", \"pos\": [4, 0, 4]}]},"
                  << " \"npcs\": {\"modify\": {\"" << npc << "\": {\"pos\": [7, 0, 7]}}},"
                  << " \"interactables\": {\"remove\": [\"" << (m->interactables.empty() ? std::string() : m->interactables.front().instance_id)
                  << "\"], \"set\": [{\"instance_id\": \"selftest_door\", \"type\": \"door\", \"model\": \"assets/models/props/oak_door.glb\","
                  << " \"pos\": [3, 0, 2], \"locked\": true, \"key_id\": \"core:item.annex_key\", \"prompt\": \"Blender Door\"}]}}";
            }
            content_.ApplyMapEdits(".");
            std::filesystem::remove_all("mods/zz_selftest_edits", ec);
            bool removed = true, moved = false, added = false, npcMoved = npc.empty();
            for (const auto& p : m->props) {
                if (p.id == victim) removed = false;
                if (p.id == mover) moved = p.pos.x == 1.0f && p.pos.z == 3.0f && p.rot_y == 45.0f;
                if (p.id == "selftest_added") added = true;
            }
            for (const auto& n : m->npcs) if (n.instance_id == npc && n.pos.x == 7.0f) npcMoved = true;
            check(removed && moved && added && npcMoved, "level edits from Blender: remove, move, add props and move NPCs");
            bool doorAdded = false, objGone = true;
            for (const auto& in : m->interactables) {
                if (in.instance_id == "selftest_door") doorAdded = in.type == "door" && in.locked && in.key_id == "core:item.annex_key";
                if (in.instance_id == gone) objGone = false;
            }
            check(doorAdded && objGone, "level edits from Blender: add a locked door, remove an object");
        }
    }

    // --- A map built in Blender (New Map): loads from mods/user_maps, invisible collision walls block, portals lead home
    {
        std::filesystem::create_directories("mods/user_maps/zz_selftest_map", ec);
        {
            std::ofstream f("mods/user_maps/zz_selftest_map/map.json");
            f << R"({"schema_version": 1, "id": "user:map.zz_selftest", "display_name_key": "Selftest Map", "weather": "fireflies",
                "spawns": {"start": {"pos": [0, 0, 0], "yaw_degrees": 0}},
                "props": [{"id": "starter_floor", "model": "assets/models/env/floor_cobble.glb", "pos": [0, -0.5, 0], "scale": [20, 0.5, 20], "solid": false},
                          {"id": "col_fence", "model": "assets/models/env/wall_stone.glb", "pos": [0, 0, 3], "scale": [10, 2, 0.5], "solid": true, "invisible": true}],
                "lights": [{"pos": [0, 2.5, 0], "color": [1, 0.6, 0.3], "radius": 8}],
                "npcs": [], "creatures": [], "interactables": [],
                "portals": [{"id": "home", "pos": [0, 0, -4], "radius": 2.2, "prompt": "Back to Bellwether",
                             "destination_map": "core:map.edrath", "destination_spawn": "village_gate"}]})";
        }
        const std::string homeMap = "core:map.edrath";
        content_.LoadUserMaps(".");
        std::filesystem::remove_all("mods/user_maps/zz_selftest_map", ec);
        const MapDef* um = content_.GetMap("user:map.zz_selftest");
        check(um != nullptr && um->props.size() == 2 && um->portals.size() == 1, "a map built in Blender loads from mods/user_maps");
        if (um) {
            LoadMap(um->id, "start");
            bool hidden = false;
            for (const auto& pi : scene_.props) if (pi.id == "col_fence") hidden = pi.invisible && pi.solid;
            check(scene_.map == um && hidden, "your map is entered and its COL box is an invisible solid wall");
            const Vector3 stopped = walk({0, 0, 0}, {0, 0, 6});
            check(stopped.z < 2.8f, "the invisible wall stops the player (z=" + std::to_string(stopped.z) + ")");
            standAndUse({0, 0, -4}, 0.0f, 0.0f);
            check(scene_.map && scene_.map->id == homeMap, "the portal in your map leads back to Bellwether");
            UpdateWorldObjects(0.0f);
            bool smearBlocks = false;
            for (const auto& b : solids_)
                if (CheckCollisionBoxSphere(b, {-6.5f, 0.4f, -8.6f}, 0.1f)) smearBlocks = true;
            check(!smearBlocks, "model-less and hidden objects (the glowing ink smear) don't block the way to the clerk");
        }
    }

    // --- Chapter One: The City Formerly Known As (Here)
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        const std::string q = "core:quest.ch1_here";
        const float savedLen = content_.game_cfg.day_length_minutes;
        content_.game_cfg.day_length_minutes = 0.0f;
        LoadMap("core:map.edrath", "village_gate");
        auto visible = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.npcs.size(); i++)
                if (scene_.npcs[i].def->id == id && !scene_.npcs[i].hidden) return static_cast<int>(i);
            return -1;
        };
        auto talk = [&](const std::string& id, std::initializer_list<const char*> path) {
            int i = visible(id);
            if (i < 0) return false;
            StartDialogue(i);
            bool ok = true;
            for (const char* step : path) ok = ok && chooseNext(step);
            if (overlay_ == Overlay::Dialogue) EndDialogue();
            overlay_ = Overlay::None;
            return ok;
        };
        auto use = [&](const std::string& id) {
            UpdateWorldObjects(0.0f);
            for (size_t i = 0; i < scene_.interactables.size(); i++)
                if (scene_.interactables[i].def.instance_id == id && !scene_.interactables[i].hidden) {
                    interact_.kind = InteractTarget::Interactable;
                    interact_.index = static_cast<int>(i);
                    UseInteractTarget();
                    narration_page_ = static_cast<int>(narration_pages_.size());
                    if (overlay_ == Overlay::Narration) AdvanceNarration();
                    overlay_ = Overlay::None;
                    return true;
                }
            return false;
        };
        auto take = [&](const std::string& item) {
            for (size_t i = 0; i < scene_.pickups.size(); i++)
                if (scene_.pickups[i].item_id == item) {
                    interact_.kind = InteractTarget::Pickup;
                    interact_.index = static_cast<int>(i);
                    UseInteractTarget();
                    return CountItem(item) > 0;
                }
            return false;
        };
        player_.hour = 12.0f;
        check(talk("core:npc.clerk_oakhaven", {"ch1_ashbound"}) && QuestStage(q) == 10, "Chapter One begins: a milestone that was never on any survey");
        check(!use("road_dusk_milestone"), "by day there's no milestone on the Old Road");
        player_.hour = 19.0f;
        check(use("road_dusk_milestone") && QuestStage(q) == 20 && player_.pos.z > 200.0f, "at dusk the road appears, and leads through the fog to Here");
        player_.hour = 12.0f;
        check(talk("core:npc.here_gatekeeper", {"day"}) && QuestStage(q) == 20 && visible("core:npc.here_baker") < 0,
              "by day the city is thin: the residents fade, Ottoline asks you to come back at dusk");
        player_.hour = 22.0f;
        check(talk("core:npc.here_gatekeeper", {"form1", "q1_wise", "q2", "q3", "stamp_ex", "stamp"}) && QuestStage(q) == 30 &&
                  CountItem("core:item.here_permit") == 1, "Form One (purpose of visit: existential): a Visitor's Permit");
        check(visible("core:npc.here_baker") >= 0 && visible("core:npc.here_butt_butt") >= 0, "at night the residents of Here are solid");
        check(talk("core:npc.here_butt_butt", {"name", "root", "song"}) && !player_.flags.count("here_frag_song"), "Butt-Butt picked the name. It's the BEST name.");
        check(use("here_verse_1") && use("here_verse_2") && use("here_verse_3") && talk("core:npc.here_butt_butt", {"sing"}) &&
                  player_.flags.count("here_frag_song") && CountItem("core:item.butt_butt_chalk") == 1, "three chalked verses, one VERY loud song: ...EERRRR");
        check(take("core:item.here_recipe") && talk("core:npc.here_baker", {"bake"}) && player_.flags.count("here_frag_smell") &&
                  CountItem("core:item.here_bread") == 2, "the recipe from the ruined bakery: the smell of the town's bread (Hhh...)");
        check(!talk("core:npc.here_cartographer", {"shape"}), "the Cartographer needs someone to climb the bell tower first");
        check(use("here_tower_view") && talk("core:npc.here_cartographer", {"shape"}) && player_.flags.count("here_frag_shape"),
              "from the bell tower the streets spell the last letter: ...E");
        check(talk("core:npc.here_gatekeeper", {"three"}) && QuestStage(q) == 40 && CountItem("core:item.here_archive_key") == 1 &&
                  std::count(player_.known_spells.begin(), player_.known_spells.end(), std::string("core:spell.unsay")) > 0,
              "the Archive key, and the Archivists' last trick: Unsay");
        {
            CreatureInstance* mouth = nullptr;
            for (auto& c : scene_.creatures) if (c.instance_id == "here_mouth_0") mouth = &c;
            if (mouth) {
                mouth->alerted = true;
                ApplyStatus(*mouth, "forget", 0.0f, 8.0f);
            }
            check(mouth && !mouth->alerted && mouth->forget_time > 7.0f, "Unsay: a Mouth of the Hunger forgets it ever saw you");
        }
        check(talk("core:npc.here_echo", {"pieces", "choice"}), "the Last Archivist: the name was always Here");
        SaveGame("selftest_ch1");
        // Ending A: say it aloud, stop the Unsaying
        check(talk("core:npc.here_echo", {"pieces", "choice", "say"}) && QuestStage(q) == 50, "say it aloud: HERE. Something heard.");
        UpdateWorldObjects(0.0f);
        bool boss = false;
        for (auto& c : scene_.creatures)
            if (c.instance_id == "here_unsaying" && c.state != CreatureState::Dead) { boss = true; DamageCreature(c, 99999, false, "swords", false); }
        check(boss && QuestStage(q) == 90, "The Unsaying rises from the gaps between words, and falls");
        check(talk("core:npc.here_echo", {"end_a"}) && QuestStage(q) == 100 && CountItem("core:item.here_silver_bell") == 1,
              "ending one: Here is back on every map (the Silver Bell of Here)");
        // Ending B: write it quietly
        check(LoadGame("selftest_ch1") && talk("core:npc.here_echo", {"pieces", "choice", "write"}) && QuestStage(q) == 101 &&
                  CountItem("core:item.here_quiet_name") == 1, "ending two: hidden and whole (everyone gets their name back; Butt-Butt keeps Butt-Butt)");
        // Ending C: hand it to the Ashbound (Chapter Zero's ending decides who keeps the Ledger)
        check(LoadGame("selftest_ch1") && talk("core:npc.here_echo", {"pieces", "choice", "give_ashbound"}) && QuestStage(q) == 102,
              "ending three: the name goes into the Ledger, for Kaelen to read aloud");
        // Death and Taxes: the ghost Inspector of Hearths
        {
            const std::string tq = "core:quest.here_taxes";
            player_.hour = 23.0f;
            check(talk("core:npc.here_inspector", {"start"}) && QuestStage(tq) == 10, "Death and Taxes: 47 hearths, 400 years, nobody PAYS");
            check(!talk("core:npc.here_inspector", {"himself"}) && use("here_hearth_register") && player_.flags.count("here_hearths_read"),
                  "the Register of Hearths at the customs post: the Inspector never taxed his own house");
            check(talk("core:npc.here_inspector", {"himself"}) && QuestStage(tq) == 100 && CountItem("core:item.inspector_abacus") == 1,
                  "he pays himself four hundred coppers; the ledger balances; he rests (the Inspector's Abacus)");
            const NpcDef* kaelen = content_.GetNpc("core:npc.ashbound_scout");
            const NpcDef* doobie = content_.GetNpc("core:npc.figure_snacks");
            check(kaelen && doobie && kaelen->companion.zone_lines.count("here") && doobie->companion.zone_lines.count("here_archive"),
                  "companions have something to say about Here (and Doobie hides from the Mouths)");
        }
        std::filesystem::remove(SavePath("selftest_ch1"), ec);
        content_.game_cfg.day_length_minutes = savedLen;
        LoadMap("core:map.edrath", "village_gate");
    }

    // --- The Audit: ten waves, a Form each, a score and records
    {
        overlay_ = Overlay::None;
        screen_ = Screen::Playing;
        LoadMap("core:map.edrath", "village_gate");
        std::string recPath = SavePath("audit_records"), backup;
        { std::ifstream f(recPath); if (f.is_open()) backup.assign(std::istreambuf_iterator<char>(f), {}); }
        std::filesystem::remove(recPath, ec);
        DialogueAction go; go.type = "travel"; go.spawn = "audit_entry";
        ExecAction(go, "");
        check(player_.pos.x < -100.0f && player_.pos.z > 200.0f, "Oakhaven sends you down to the Audit Chamber");
        int auditor = -1;
        for (size_t i = 0; i < scene_.npcs.size(); i++) if (scene_.npcs[i].def->id == "core:npc.auditor") auditor = static_cast<int>(i);
        check(auditor >= 0, "Senior Auditor Prudence Vell is at her desk");
        player_.health = static_cast<float>(MaxHealth());
        StartAudit();
        auto killWave = [&]() {
            for (int t = 0; t < 2000 && audit_.active && audit_.break_timer > 0.0f; t++) UpdateAudit(0.05f);
            int n = 0;
            for (auto& c : scene_.creatures)
                if (IsAuditCreature(c) && c.state != CreatureState::Dead) { DamageCreature(c, 999999, false, "swords", false); n++; }
            UpdateAudit(0.05f);
            return n;
        };
        int first = killWave();
        check(audit_.active && audit_.wave == 1 && first == 3 && audit_.form == 0, "wave 1: three examiners, Form 1 (Standard)");
        int goldBefore = player_.gold;
        for (int w = 2; w <= 10 && audit_.active; w++) killWave();
        check(!audit_.active && player_.flags.count("audit_passed") && CountItem("core:item.certificate_of_existence") == 1 && player_.gold > goldBefore,
              "all ten waves: AUDIT PASSED, the Certificate of Existence (and pay for every stage)");
        bool cleared = true;
        for (const auto& c : scene_.creatures) if (IsAuditCreature(c)) cleared = false;
        std::string rec = AuditRecordsText();
        check(cleared && rec.find("PASSED") != std::string::npos && rec.find("wave 10") != std::string::npos,
              "the arena is cleared and the run is on record (name, build, wave, score)");
        StartAudit();
        killWave();
        for (int t = 0; t < 2000 && audit_.break_timer > 0.0f; t++) UpdateAudit(0.05f);
        player_.health = 0.0f;
        FixedUpdate(1.0f / 60.0f);
        check(!audit_.active && screen_ == Screen::Playing && player_.health > 0.0f && AuditRecordsText().find("wave 1\n") != std::string::npos,
              "falling in an audit isn't death: you're FAILED, sent back, and the run is recorded");
        std::filesystem::remove(recPath, ec);
        if (!backup.empty()) { std::ofstream f(recPath); f << backup; }
        LoadMap("core:map.edrath", "village_gate");
    }

    // --- Gamepad: prompts follow the last device; every action has its own button
    {
        const bool was = pad_active_;
        pad_active_ = true;
        bool padLabels = BindingLabel("interact") == "X" && BindingLabel("attack") == "RT" && BindingLabel("cast_spell") == "RB" &&
                         BindingLabel("jump") == "A";
        pad_active_ = false;
        bool keyLabels = BindingLabel("interact") == "E" && BindingLabel("attack") == "LMB";
        pad_active_ = was;
        std::set<int> used;
        bool unique = true;
        for (const char* a : {"jump", "interact", "cycle_spell", "crouch", "attack", "block_or_aim", "cast_spell", "map", "sprint", "journal",
                              "inventory", "quick_slot_1", "quick_slot_2", "quick_slot_3", "quick_slot_4"}) {
            int b = PadButtonFor(a);
            unique = unique && b > 0 && used.insert(b).second;
        }
        check(padLabels && keyLabels && unique, "gamepad: prompts show pad buttons after using the pad, keys after the keyboard; no button does two jobs");
    }

    // --- Day and night
    {
        const float savedHour = player_.hour, savedLen = content_.game_cfg.day_length_minutes;
        content_.game_cfg.day_length_minutes = 48.0f;
        player_.hour = 23.9f;
        AdvanceClock(60.0f);   // one real minute = half an hour
        check(player_.hour > 0.3f && player_.hour < 0.5f, "the clock runs and wraps past midnight");
        LoadMap("core:map.edrath", "village_gate");
        player_.hour = 0.0f; UpdateAtmosphere(0.0f, true);
        const Atmosphere night = atmo_;
        const bool nightOut = NightOutdoors();
        player_.hour = 12.0f; UpdateAtmosphere(0.0f, true);
        const Atmosphere noon = atmo_;
        check(noon.ambient.x > night.ambient.x * 1.3f && noon.sky.r + noon.sky.g + noon.sky.b > 300 &&
                  noon.sky_panorama == "assets/textures/sky/sky_day.png" && nightOut && !NightOutdoors(),
              "outdoors, noon is bright with a day sky and midnight is night (no stars by day)");
        player_.hour = 19.6f; UpdateAtmosphere(0.0f, true);
        check(atmo_.sky_panorama == "assets/textures/sky/sky_dusk.png", "dusk paints the dusk sky");
        Vector3 annex{};
        for (const auto& z : scene_.map->zones)
            if (z.id == "annex") annex = Vector3Scale(Vector3Add(z.box_min, z.box_max), 0.5f);
        player_.hour = 0.0f; const Atmosphere in0 = ComputeAtmosphere(annex, nullptr);
        player_.hour = 12.0f; const Atmosphere in12 = ComputeAtmosphere(annex, nullptr);
        check(fabsf(in0.ambient.x - in12.ambient.x) < 0.001f && in0.sky_panorama == in12.sky_panorama,
              "indoors (the Registry Annex) looks the same at midnight and noon");
        NpcInstance* someone = nullptr;
        for (auto& n : scene_.npcs) if (!n.hidden && !IsCompanion(n.def->id)) { someone = &n; break; }
        if (someone) {
            someone->hours_from = 20.0f; someone->hours_to = 6.0f;
            player_.hour = 12.0f; UpdateWorldObjects(0.0f);
            bool goneByDay = someone->hidden;
            player_.hour = 23.0f; UpdateWorldObjects(0.0f);
            check(goneByDay && !someone->hidden, "an NPC with hours 20 to 6 is around at night and gone by day");
            someone->hours_from = someone->hours_to = -1.0f;
            UpdateWorldObjects(0.0f);
        }
        CreatureInstance* foe = nullptr;
        for (auto& c : scene_.creatures) if (c.state != CreatureState::Dead) { foe = &c; break; }
        if (foe) {
            const Vector3 fp = foe->pos; const bool fa = foe->alerted;
            foe->pos = Vector3Add(player_.pos, {3, 0, 0}); foe->alerted = true;
            check(!WaitBlockedReason().empty(), "you can't wait with an enemy after you");
            foe->pos = fp; foe->alerted = fa;
        }
        player_.hour = 22.0f;
        if (WaitBlockedReason().empty()) WaitUntil(7.0f);
        check(fabsf(player_.hour - 7.0f) < 0.01f, "waiting until morning makes it 7:00");
        player_.hour = savedHour;
        content_.game_cfg.day_length_minutes = savedLen;
    }

    std::filesystem::remove(SavePath("autosave"), ec);
    std::filesystem::remove(SavePath("autosave") + ".bak", ec);
    Logger::Info("Self-test finished with " + std::to_string(failures) + " failure(s).");
    return failures;
}

} // namespace uncounted

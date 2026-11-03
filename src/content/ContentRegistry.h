#pragma once

#include "core/Types.h"
#include <string>
#include <vector>
#include <unordered_map>

namespace uncounted {

class ContentRegistry {
public:
    GraphicsConfig graphics;
    ControlsConfig controls;
    GameConfig game_cfg;
    BalancingDef balancing;

    std::unordered_map<std::string, std::string> loc_strings;
    std::vector<AttributeDef> attributes;
    std::vector<RaceDef> races;
    std::vector<BackgroundDef> backgrounds;
    std::vector<ArchetypeDef> archetypes;
    std::vector<SkillDef> skills;
    std::vector<SynergyDef> synergies;
    std::vector<FactionDef> factions;

    std::vector<SpellDef> spells_ordered;
    std::unordered_map<std::string, SpellDef> spells;

    std::vector<ItemDef> items_ordered;
    std::unordered_map<std::string, ItemDef> items;

    std::unordered_map<std::string, LootTableDef> loot_tables;

    std::vector<CreatureDef> creatures_ordered;
    std::unordered_map<std::string, CreatureDef> creatures;

    std::unordered_map<std::string, NpcDef> npcs;
    std::unordered_map<std::string, DialogueDef> dialogues;
    std::unordered_map<std::string, QuestDef> quests;
    std::vector<CampaignDef> campaigns;   // sorted by order
    const CampaignDef* GetCampaign(const std::string& id) const;
    std::unordered_map<std::string, MapDef> maps;

    std::vector<ValidationIssue> validation_issues;
    std::vector<std::string> loaded_packs;

    bool LoadConfigs(const std::string& rootDir = ".");
    bool SaveConfigs(const std::string& rootDir = ".") const;

    bool LoadAllContent(const std::string& rootDir = ".", const std::vector<std::string>& extraModManifests = {});
    bool ValidateAll(const std::string& rootDir = ".");

    std::string Tr(const std::string& key) const;
    const ItemDef* GetItem(const std::string& id) const;
    const SpellDef* GetSpell(const std::string& id) const;
    const CreatureDef* GetCreature(const std::string& id) const;
    const NpcDef* GetNpc(const std::string& id) const;
    const DialogueDef* GetDialogue(const std::string& id) const;
    const QuestDef* GetQuest(const std::string& id) const;
    const MapDef* GetMap(const std::string& id) const;
    const RaceDef* GetRace(const std::string& id) const;
    const BackgroundDef* GetBackground(const std::string& id) const;
    const ArchetypeDef* GetArchetype(const std::string& id) const;

private:
    bool LoadManifestFile(const std::string& rootDir, const std::string& manifestRelPath);
    void LoadLocalizationFile(const std::string& rootDir, const std::string& relPath);
    void LoadSpellsFile(const std::string& rootDir, const std::string& relPath);
    void LoadItemsFile(const std::string& rootDir, const std::string& relPath);
    void LoadLootTablesFile(const std::string& rootDir, const std::string& relPath);
    void LoadCreaturesFile(const std::string& rootDir, const std::string& relPath);
    void LoadNpcsFile(const std::string& rootDir, const std::string& relPath);
    void LoadDialoguesFile(const std::string& rootDir, const std::string& relPath);
    void LoadQuestsFile(const std::string& rootDir, const std::string& relPath);
    void LoadMapFile(const std::string& rootDir, const std::string& relPath);

    void RecordIssue(const std::string& file, const std::string& key, const std::string& reason, bool isError = true);
    bool CheckFileExists(const std::string& rootDir, const std::string& relPath, const std::string& sourceContext, const std::string& keyName);
};

} // namespace uncounted

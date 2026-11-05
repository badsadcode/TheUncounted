# Map checklist: what lives where, and what must survive a redesign

Generated from the built world by `tools/write_map_checklist.py` (rerun it after you rebuild). Use it alongside `docs/LEVEL_EDITOR.md`, which explains the building rules (heights, stairs, doorways, collision).

**The rule of thumb:** buildings, ground, walls, trees and decorations are entirely yours: delete, reshape, rebuild. Everything in **Uncounted Objects** (people, monsters, chests, doors, notes, levers, arrival points) can be **moved** freely onto your new floors; only the ones marked **keep** must not be **deleted**, because a quest, the journal markers or the self-test needs them. After a rebuild, `./game --validate` and the self-test tell you if anything the story needs went missing.

Legend: `requires_flag` = appears only after that story moment; `hidden_flag` = disappears after it (both are automatic, you just place them once).


## Bellwether Village

**People** (move freely; never delete):

- **Clerk Oakhaven** (`npc_oakhaven`)
- **Vaelen the Quartermaster** (`npc_vaelen`)
- **Marta Kettleburn** (`npc_marta`)
- **Librarian Fenwick** (`npc_fenwick`)
- **Brother Aldous** (`npc_aldous`)
- **Sabrino** (`npc_sabrino`) (only after `sabrino_in_town`)
- **Hollis the Grey** (`npc_hollis`)
- **Madame Odette Velour** (`npc_odette`) (gone after `players_at_hollowmere`)
- **Trout** (`npc_trout_home`) (only after `oak_plugged`)
- **Steve** (`npc_steve_inn`) (only after `steve_in_town`)
- **The Phantom Clerk (Netted)** (`npc_unmask_clerk`) (only after `fig1_caught`, gone after `fig1_done`)
- **Grout** (`npc_grout`)
- **Cindermaw the Elder** (`npc_dragon_cindermaw`) (only after `dragon_arrived`)
- **Grubnik Quillsby, Esq.** (`npc_kobold_quillsby`) (only after `dragon_hearing`, gone after `dragon_golem`)
- **Eranu** (`npc_eranu`)
- **Coth** (`npc_coth_inn`) (only after `coth_home`)
- **Dunstan** (`npc_dunstan`)

**Keep (move, don't delete):**

- `records_supply_chest` — chest — *chest (fixed items)*
- `shrine_free_tome` — Tome: Mend — *pickup*
- `inn_free_bread` — Bellwether Crust Loaf — *pickup*
- `sabrino_wanted` — WANTED - By Order of the Royal Bureau of Records — *used by the self-test*
- `script_page_1` — THE TRAGEDIE OF THE UNCOUNTED KING - Page One — *quest marker: Act II: The Missing Script; sets `page_1`*
- `trout_roof` — Hoofprints, Going Up — *quest marker: Case File #3: The Horse Who Wasn't There; sets `trout_c_roof`*
- `bell_alchemy_bench` — Use the Alchemy Bench — *station*
- `bell_workbench` — Use the Workbench — *station*
- `bell_cooking_pot` — Cook at Marta's Hearth — *station*
- `fig1_clue_ink` — A Smear of Glowing Ink (only after `fig1_open`) — *quest marker: The Figure It Out Gang: The Phantom Clerk of Bellwether; used by the self-test; sets `fig1_c1`*
- `fig1_clue_receipt` — A Crumpled Receipt (only after `fig1_open`) — *quest marker: The Figure It Out Gang: The Phantom Clerk of Bellwether; used by the self-test; sets `fig1_c2`*
- `fig1_clue_tags` — A Box Behind the Market Stall (only after `fig1_open`) — *quest marker: The Figure It Out Gang: The Phantom Clerk of Bellwether; used by the self-test; sets `fig1_c3`*
- `fig1_trap` — The Trap (only after `fig1_trap_ready`, gone after `fig1_trap`) — *quest marker: The Figure It Out Gang: The Phantom Clerk of Bellwether; used by the self-test; sets `fig1_trap`; advances a quest*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 5 × **Grave Rat** (`town_rat_0`…) — group `town_rats`, only after `rats_in_town`, story/test: keep
- 1 × **The Phantom Clerk** (`fig1_phantom`) — group `fig1`, only after `fig1_trap`, story/test: keep
- 1 × **The Repossession Golem** (`dp_golem`) — group `dp_golem`, only after `dragon_golem`, story/test: keep

**Arrival points:** `village_gate` — *arrival point for a door, boat, dialogue or new game: keep*, `from_old_road`, `from_audit` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (11): flavour notes, gathering spots, fishing spots</summary>

`records_notice_lectern` (readable: Municipal Ordinance 404), `census_board` (readable: Bellwether Census, Spring Posting), `hollis_board` (readable: CONTRACTS (Monster Hunters Only. That Means You, Baggy.)), `horse_notice` (readable: NOTICE from the Church of the Last Dawn), `casting_poster` (readable: CASTING CALL!), `thursday_sheets` (readable: Form 1-CS: Character Sheets (Thursday Group)), `bell_marigold_160_110` (harvest), `bell_marigold_125_175` (harvest), `bell_marigold_165_25` (harvest), `bell_wayside_sage_170_25` (harvest), `bell_wayside_sage_35_172` (harvest)

</details>


## The Audit Chamber

**People** (move freely; never delete):

- **Prudence Vell** (`npc_auditor`)

**Keep (move, don't delete):**

- `audit_exit` — Leave the Audit Chamber — *travel; travels to `from_audit`*

**Arrival points:** `audit_entry` — *arrival point for a door, boat, dialogue or new game: keep*, `audit_center`

<details><summary>Free to move or delete (1): flavour notes, gathering spots, fishing spots</summary>

`audit_rules` (readable: Notice to Persons Under Audit)

</details>


## The Archive of Here

**People** (move freely; never delete):

- **The Last Archivist** (`npc_here_echo`)

**Keep (move, don't delete):**

- `here_archive_door` — Archive Door — *quest marker: The City Formerly Known As; door*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 3 × **Mouth of the Hunger** (`here_mouth_0`…) — story/test: keep
- 1 × **The Unsaying** (`here_unsaying`) — group `here_unsaying`, only after `here_spoken`, story/test: keep


## Here

**People** (move freely; never delete):

- **Ottoline Pell** (`npc_here_gatekeeper`)
- **Butt-Butt** (`npc_here_butt_butt`)
- **Person in a Hat** (`npc_here_hat`)
- **The Night Merchant** (`npc_here_night_merchant`)
- **The Baker, Probably** (`npc_here_baker`)
- **The Cartographer** (`npc_here_cartographer`)
- **Inspector Aldric Thrupp** (`npc_here_inspector`)

**Keep (move, don't delete):**

- `here_inner_gate` — City Gate — *door*
- `here_road_back` — Follow the Road Back to the Old Road — *travel; travels to `road_dusk`*
- `here_recipe` — Take the Recipe Card — *quest marker: The City Formerly Known As; pickup*
- `here_verse_1` — Chalked Verse (One) — *quest marker: The City Formerly Known As; used by the self-test; sets `here_verse1`*
- `here_verse_2` — Chalked Verse (Two) — *quest marker: The City Formerly Known As; used by the self-test; sets `here_verse2`*
- `here_verse_3` — Chalked Verse (Three) — *quest marker: The City Formerly Known As; used by the self-test; sets `here_verse3`*
- `here_hearth_register` — Register of Hearths (Here) — *quest marker: Death and Taxes; used by the self-test; sets `here_hearths_read`*
- `here_tower_view` — From the Bell Tower — *quest marker: The City Formerly Known As; used by the self-test; sets `here_tower_view`*

**Arrival points:** `here_gate` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (4): flavour notes, gathering spots, fishing spots</summary>

`here_customs_sign` (readable: CUSTOMS), `here_fountain` (readable: The Dry Fountain), `here_midnight_sign` (readable: The Midnight Market), `here_archive_plaque` (readable: The Archive)

</details>


## The Late Cindermaw

**People** (move freely; never delete):

- **Old Silas** (`npc_silas_seaside`)

**Keep (move, don't delete):**

- `quillsby_vault_door` — Vault Door — *used by the self-test; door*
- `missing_third_hoard` — Recover the Missing Third of the Hoard — *quest marker: The Missing Third; used by the self-test; quest_pedestal; advances a quest*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 4 × **Kobold Bookkeeper** (`kobold_cushion_0`…)
- 1 × **Grubnik Quillsby, Esq. (Cornered)** (`quillsby_cornered`) — group `quillsby`, only after `missing_third_open`, story/test: keep

**Arrival points:** `seaside_landing` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (4): flavour notes, gathering spots, fishing spots</summary>

`cove_sign` (readable: A Very Expensive Sign), `cushion_ledger` (readable: Cushion Inventory (Partial)), `shoe_room` (readable: The Shoe Room), `quillsby_letter` (readable: A Letter, Half-Written)

</details>


## The Sleeper's Reef

**People** (move freely; never delete):

- **Old Silas** (`npc_silas_reef`) (only after `reef_trip`)
- **Ondine Marsh** (`npc_keeper`) (only after `reef_trip`, gone after `keeper_rests`)
- **Trout** (`npc_trout_light`) (only after `oak_plugged`)
- **The Taller Stranger** (`npc_gale_elder`) (only after `reef_trip`, gone after `reef_done`)
- **The Shorter Stranger** (`npc_gale_younger`) (only after `reef_trip`, gone after `reef_done`)

**Keep (move, don't delete):**

- `light_plaque` — The Saltmere Light — *sets `reef_plaque`*
- `keeper_log` — Log of the Saltmere Light, O. Marsh — *sets `reef_log`*
- `reef_bottle_tom` — A Name in a Bottle: THOMAS GALE — *quest marker: The Light Past the Fog; sets `reef_tom`*
- `reef_bottle_abel` — A Name in a Bottle: ABEL GALE — *quest marker: The Light Past the Fog; sets `reef_abel`*
- `reef_bottle_fenn` — A Name in a Bottle: BARTHOLOMEW FENN — *sets `reef_fenn`*
- `reef_bottle_nan` — A Name in a Bottle: GRANNY WEATHERBY — *sets `reef_nan`*
- `reef_bottle_nobody` — A Name in a Bottle: (blank) — *sets `reef_nobody`*
- `reef_bottle_marsh` — A Name in a Bottle: ONDINE MARSH — *sets `reef_ondine`*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **The Dreaming Limb** (`dreaming_limb`) — group `limb`, only after `lamp_lit`, story/test: keep
- 2 × **Salt Wight** (`reef_wight_0`…)
- 2 × **The Drowned** (`reef_drowned_0`…)
- 2 × **The Drowned** (`limb_drowned_0`…) — group `limb`, only after `lamp_lit`, story/test: keep

**Arrival points:** `reef_landing` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (6): flavour notes, gathering spots, fishing spots</summary>

`reef_bladderwrack_80_80` (harvest), `reef_bladderwrack_90_20` (harvest), `reef_sea_salt_120_35` (harvest), `reef_sea_salt_120_10` (harvest), `reef_glowcap_35_125` (harvest), `fish_jetty` (fishing)

</details>


## The Whistling Wood

**People** (move freely; never delete):

- **Trout** (`npc_trout_oak`) (only after `trout_case`, gone after `oak_plugged`)
- **Steve** (`npc_steve`) (only after `trout_case`, gone after `steve_in_town`)
- **A Squirrel (Dignified)** (`npc_druid_squirrel`) (gone after `druid_restored`)
- **Bramble Thistlewick** (`npc_druid_bramble`) (only after `druid_restored`)
- **Coth** (`npc_coth_wood`) (gone after `coth_home`)

**Keep (move, don't delete):**

- `wood_sign` — THE WHISTLING WOOD — *quest marker: Case File #3: The Horse Who Wasn't There; sets `trout_c_sign`*
- `oak_hollow` — The Old Oak's Hollow — *quest marker: Case File #3: The Horse Who Wasn't There; sets `trout_c_whistle`*
- `ransom_drafts` — Crumpled Drafts — *sets `trout_c_drafts`*
- `cottage_notice` — A Note, in Grandmotherly Handwriting — *sets `trout_c_granny`*
- `cottage_chest` — chest — *chest (fixed items)*
- `wood_carrots` — Carrot — *pickup*
- `druid_acorn` — Acorn of the Old Oak — *quest marker: A Druid in Distress; used by the self-test; pickup*
- `sir_pebbleton_note` — Sir Pebbleton — *used by the self-test*
- `coth_tally` — Marks on a Pine — *quest marker: Cothepoo, Come Home; used by the self-test; sets `coth_seen_tally`*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 2 × **Angry Badger** (`wood_badger_0`…)
- 1 × **A Wolf in Grandmother's Nightgown** (`granny_wolf`) — only after `trout_wood`, story/test: keep
- 2 × **Grey Wolf** (`wood_wolf_0`…)
- 4 × **Grey Wolf** (`camp_wolf_0`…) — group `camp_wolves`, only after `trout_wood`, story/test: keep
- 2 × **Will-o'-the-Wisp** (`wood_wisp_0`…)

**Arrival points:** `wood_lane`

<details><summary>Free to move or delete (12): flavour notes, gathering spots, fishing spots</summary>

`wood_wolfsbane_50_175` (harvest), `wood_wolfsbane_150_95` (harvest), `wood_wolfsbane_30_160` (harvest), `wood_glowcap_100_100` (harvest), `wood_glowcap_175_90` (harvest), `wood_glowcap_180_80` (harvest), `wood_pine_resin_60_170` (harvest), `wood_pine_resin_160_120` (harvest), `wood_ashwood_branch_70_60` (harvest), `wood_iron_scrap_200_170` (harvest), `wood_marigold_20_40` (harvest), `fish_pond` (fishing)

</details>


## The Sunken Chapel

**People** (move freely; never delete):

- **Old Silas** (`npc_silas`)
- **Thomas Gale** (`npc_tom_home`) (only after `reef_done`)
- **Abel Gale** (`npc_abel_home`) (only after `reef_done`)
- **The Tide Priest** (`npc_tide_priest`) (gone after `saltmere_resolved`)

**Keep (move, don't delete):**

- `tide_bell_1` — Tide Bell (First) — *quest marker: Case File #2: The Silence at Saltmere; sets `bell_1`; advances a quest*
- `tide_bell_2` — Tide Bell (Second) — *quest marker: Case File #2: The Silence at Saltmere; sets `bell_2`; advances a quest*
- `tide_bell_3` — Tide Bell (Third) — *quest marker: Case File #2: The Silence at Saltmere; sets `bell_3`; advances a quest*
- `drowned_hymn` — The Drowned Hymn — *sets `hymn_read`*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Avatar of the Name-Eater** (`avatar`) — group `avatar`, only after `avatar_rises`, story/test: keep
- 1 × **Pinchwick Crab** (`quay_crab_1`)
- 4 × **The Drowned** (`chapel_drowned_0`…)
- 2 × **Tide Acolyte** (`chapel_acolyte_0`…)

**Arrival points:** `saltmere_pier` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (4): flavour notes, gathering spots, fishing spots</summary>

`dock_bladderwrack_125_90` (harvest), `dock_sea_salt_175_84` (harvest), `dock_sea_salt_40_88` (harvest), `fish_pier_b` (fishing)

</details>


## Saltmere Docks

**People** (move freely; never delete):

- **Mother Brine** (`npc_brine`)
- **The Professor** (`npc_pickering`)
- **The Harbourmaster** (`npc_harbourmaster`)

**Keep (move, don't delete):**

- `pickering_notes` — Field Notes, Prof. A. Pickering (Collegium, Dept. of Unusual Studies) — *sets `pickering_notes_read`*
- `trout_sea` — A Horseshoe, Dripping — *quest marker: Case File #3: The Horse Who Wasn't There; sets `trout_c_sea`*
- `saltmere_idol` — Warm Fish Idol — *pickup*
- `cellar_gate` — Cellar Gate (it smells of the sea) — *quest marker: Case File #2: The Silence at Saltmere; door*
- `docks_alchemy_bench` — Use Mother Brine's Alchemy Bench — *station*
- `fish_quay` — Fish from the quay — *used by the self-test*
- `docks_cooking_pot` — Cook at Mother Brine's Pot — *station*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Pinchwick Crab** (`quay_crab_0`)

**Arrival points:** `saltmere_quay`

<details><summary>Free to move or delete (8): flavour notes, gathering spots, fishing spots</summary>

`tavern_sign` (readable: The Drowned Lantern), `tide_ledger` (readable: Saltmere Tide Ledger), `harbour_notice` (readable: BY ORDER OF THE HARBOURMASTER), `wh_ledger` (readable: Gale & Sons Fish Co. - Shipping Ledger), `dock_bladderwrack_0_93` (harvest), `dock_bladderwrack_135_86` (harvest), `dock_sea_salt_180_20` (harvest), `fish_pier_a` (fishing)

</details>


## Hollowmere Manor

**People** (move freely; never delete):

- **Sir Percival Hollowmere** (`npc_percival`) (only after `host_identified`, gone after `host_banish`)
- **Madame Odette Velour** (`npc_odette_stage`) (only after `players_at_hollowmere`)
- **Mortimer Quill** (`npc_mortimer`) (only after `critic_revealed`)
- **Lord Ashgrave** (`npc_ashgrave`)

**Keep (move, don't delete):**

- `hollowmere_front_door` — Hollowmere Manor Front Door — *used by the self-test; door*
- `hollowmere_kitchen_door` — Kitchen Back Door (it's open; it's always open; that's the problem) — *quest marker: Rats. It's Always Rats.; door*
- `dining_floating` — The Table Is Laid — *quest marker: Case File #1: The Hollowmere Haunting; sets `ev_floating`*
- `dining_key_plate` — Sideboard Drawer (labelled 'STUDY KEY - DO NOT LOOK HERE') — *chest (fixed items)*
- `kitchen_claws` — Claw Marks on the Back Door Frame — *quest marker: Case File #1: The Hollowmere Haunting; sets `clue_claws`*
- `kitchen_bucket` — Dented Bucket — *pickup*
- `ballroom_cold` — A Cold Spot — *quest marker: Case File #1: The Hollowmere Haunting; sets `ev_cold`*
- `script_page_5` — THE TRAGEDIE OF THE UNCOUNTED KING - Page Five — *quest marker: Act II: The Missing Script; sets `critic_revealed`; advances a quest*
- `study_door` — Study Door — *door*
- `sealed_door` — Sealed Room (a lever somewhere opens this) — *door*
- `bedroom_decanter` — Sherry Decanters, Bitten — *quest marker: Case File #1: The Hollowmere Haunting; sets `clue_bites`*
- `study_writing` — Sir Percival's Guest Book — *quest marker: Case File #1: The Hollowmere Haunting; sets `ev_writing`*
- `study_lever` — Pull the Lever (no puzzle required) — *lever*
- `gallery_spiritbox` — The Spirit Trumpet — *sets `spirit_box_tried`*
- `sealed_chest` — chest — *chest (fixed items)*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 2 × **Animated Armour** (`foyer_armor`…)
- 3 × **Grave Rat** (`kitchen_rat_0`…) — group `rat_king`
- 1 × **The Rat King** (`rat_king`) — group `rat_king`, story/test: keep
- 2 × **Wailing Footman** (`dining_footman`…)
- 1 × **Sir Percival, the Wrathful Host** (`wrathful_host`) — group `host`, only after `host_banish`, story/test: keep

<details><summary>Free to move or delete (12): flavour notes, gathering spots, fishing spots</summary>

`foyer_chalkboard` (readable: EVIDENCE BOARD (Property of Hollis)), `foyer_tpose` (readable: A Figure in the Hall), `library_bestsellers` (readable: Hollowmere Library: Most Borrowed), `library_search` (readable: You Search for Treasure), `library_rules` (readable: Page 212 of a Very Thick Rulebook), `ballroom_gramophone` (readable: The Gramophone), `study_puzzle` (readable: A Note from the Architect), `gallery_portrait_0` (readable: Portrait: Sir Percival at Thirty), `gallery_portrait_1` (readable: Portrait: Sir Percival at Sixty), `gallery_portrait_2` (readable: Portrait: Sir Percival at Ninety), `gallery_portrait_3` (readable: Portrait: A Monster Hunter), `sealed_note` (readable: A Note Taped to the Treasure)

</details>


## Hollowmere Grounds

**People** (move freely; never delete):

- **Rolf** (`npc_rolf`)
- **The Howler (Netted, Bucketed)** (`npc_unmask_howler`) (only after `fig2_caught`, gone after `fig2_done`)

**Keep (move, don't delete):**

- `gate_sign` — Hollowmere Manor - Private Grounds — *sets `hollowmere_visited`; advances a quest*
- `garden_howl` — A Mournful Wail — *quest marker: Case File #1: The Hollowmere Haunting; sets `clue_wailing`*
- `fig2_clue_prints` — Pawprints in the Soil (only after `fig2_open`) — *quest marker: The Figure It Out Gang: The Howler of Hollowmere; used by the self-test; sets `fig2_c1`*
- `fig2_clue_wool` — A Scrap Caught on the Fence (only after `fig2_open`) — *quest marker: The Figure It Out Gang: The Howler of Hollowmere; used by the self-test; sets `fig2_c2`*
- `fig2_clue_list` — Bellwether Marrow Show: Previous Results (only after `fig2_open`) — *quest marker: The Figure It Out Gang: The Howler of Hollowmere; used by the self-test; sets `fig2_c3`*
- `fig2_trap` — The Trap (only after `fig2_trap_ready`, gone after `fig2_trap`) — *quest marker: The Figure It Out Gang: The Howler of Hollowmere; used by the self-test; sets `fig2_trap`; advances a quest*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Gravedigger Ghoul** (`grave_ghoul_0`)
- 1 × **The Howler of Hollowmere** (`fig2_howler`) — group `fig2`, only after `fig2_trap`, story/test: keep

**Arrival points:** `hollowmere_gate`

<details><summary>Free to move or delete (16): flavour notes, gathering spots, fishing spots</summary>

`grave_0` (readable: Here Lies...), `grave_1` (readable: Here Lies...), `grave_2` (readable: Here Lies...), `grave_3` (readable: Here Lies...), `grave_4` (readable: Here Lies...), `grave_5` (readable: Here Lies...), `grave_6` (readable: Here Lies...), `grave_7` (readable: Here Lies...), `grave_8` (readable: Here Lies...), `grave_9` (readable: Here Lies...), `graveyard_sign` (readable: The Lawn of Ill-Advised Choices), `mans_grave_moss_159_140` (harvest), `mans_grave_moss_115_140` (harvest), `mans_grave_moss_137_108` (harvest), `mans_marigold_165_140` (harvest), `mans_wolfsbane_170_100` (harvest)

</details>


## The Seal Chamber

**Keep (move, don't delete):**

- `seal_of_names` — Sign the Seal of Names — *quest marker: The Sleepers of Vault III; quest_pedestal; sets `seal_renewed`; advances a quest*
- `seal_chest` — chest — *chest (fixed items)*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **The Lullaby Warden** (`lullaby_warden`) — story/test: keep


## Vault III: The Nursery

**Keep (move, don't delete):**

- `ilse_cradle` — Held in Trust — *quest marker: The Sleepers of Vault III; sets `found_ilse`; advances a quest*
- `nursery_chest` — chest — *chest (fixed items)*
- `nursery_truffle` — Grave-cap Truffle — *quest marker: Dinner at Eight; pickup*
- `script_page_4` — THE TRAGEDIE OF THE UNCOUNTED KING - Page Four — *quest marker: Act II: The Missing Script; sets `page_4`*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Ash Crawler** (`nursery_crawler`) — story/test: keep
- 1 × **Ink Wraith** (`nursery_ink_wraith`)
- 2 × **Restless Skeleton** (`nursery_skel_1`…)
- 1 × **Truffle Hog** (`nursery_truffle_hog`)

**Arrival points:** `vault_landing`

<details><summary>Free to move or delete (1): flavour notes, gathering spots, fishing spots</summary>

`warden_lullaby` (readable: The Night-Warden's Lullaby)

</details>


## Registry Annex & Forgotten Crypt

**People** (move freely; never delete):

- **The Uncounted Witness** (`npc_spirit`)

**Keep (move, don't delete):**

- `annex_inner_door` — Archive Door — *quest marker: Legally Deceased; used by the self-test; door*
- `crypt_portcullis` — Lower Crypt Portcullis (Controlled by Archive Lever) — *used by the self-test; door*
- `crypt_gate_lever` — Pull Iron Archive Lever — *used by the self-test; lever*
- `secret_wall_door` — Sealed Royal Vault Gate (Step on Rune Plate) — *used by the self-test; door*
- `secret_plate` — Ancient Rune Pressure Plate — *pressure_plate*
- `sanctum_gate` — Sanctum of the Uncounted Gate — *used by the self-test; door*
- `secret_widowmaker_chest` — chest — *used by the self-test; chest (fixed items)*
- `archive_supply_chest` — chest — *chest (fixed items)*
- `grand_ledger_lectern` — Claim Form 27-B & The Uncounted Ledger — *quest marker: Legally Deceased; quest_pedestal; advances a quest*
- `oakhallow_census` — Census of Oakhallow, Folio III (Struck) — *quest marker: A Name Worth Keeping; advances a quest*
- `crypt_truffle` — Grave-cap Truffle — *quest marker: Dinner at Eight; pickup*
- `script_page_3` — THE TRAGEDIE OF THE UNCOUNTED KING - Page Three — *quest marker: Act II: The Missing Script; sets `page_3`*
- `flour_handprints` — Handprints in Old Flour — *advances a quest*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Ash Crawler** (`archive_crawler_1`) — story/test: keep
- 2 × **Bone Clerk** (`foyer_bone_clerk`…) — story/test: keep
- 1 × **Archivist Shade Morvath** (`sanctum_boss`) — story/test: keep
- 1 × **Grave Rat** (`foyer_rat`) — story/test: keep
- 1 × **Ink Wraith** (`archive_ink_wraith`)
- 1 × **Lost Sentinel** (`crypt_sentinel_1`) — story/test: keep
- 2 × **Paperwork Elemental** (`archive_paperwork_0`…)
- 1 × **Restless Skeleton** (`archive_skel_1`) — story/test: keep
- 1 × **Truffle Hog** (`crypt_truffle_hog`)

**Arrival points:** `annex_entry`

<details><summary>Free to move or delete (3): flavour notes, gathering spots, fishing spots</summary>

`archive_clue_lectern` (readable: Chief Archivist Morvath's Log), `duty_roster` (readable: Annex III Duty Roster), `landing_warning` (readable: Scratched into the Stone)

</details>


## The Old Road

**People** (move freely; never delete):

- **Kaelen of the Ashbound** (`npc_kaelen`)
- **Baggy** (`npc_baggy`)
- **Bread** (`npc_figure_rodrick`)
- **Badnee** (`npc_figure_primrose`)
- **Karma** (`npc_figure_agnes`)
- **Doobie** (`npc_figure_snacks`)
- **The Headless Knight (Sat On)** (`npc_unmask_knight`) (only after `fig3_caught`, gone after `fig3_done`)

**Keep (move, don't delete):**

- `monolith_inscription` — Boundary Marker of the Third Reign — *advances a quest*
- `road_ranger_chest` — chest — *used by the self-test; chest (fixed items)*
- `road_arrow_bundle` — Bodkin Arrow — *pickup*
- `sabrino_stash` — chest — *used by the self-test; chest (fixed items)*
- `sabrino_note` — A Note, Weighed Down with a Clove of Garlic — *used by the self-test; sets `sabrino_in_town`; advances a quest*
- `script_page_2` — THE TRAGEDIE OF THE UNCOUNTED KING - Page Two — *quest marker: Act II: The Missing Script; sets `page_2`*
- `trout_stone` — On Top of the Boundary Stone — *quest marker: Case File #3: The Horse Who Wasn't There; sets `trout_c_stone`*
- `fig3_clue_hat` — A Hat on a Stick (only after `fig3_open`) — *quest marker: The Figure It Out Gang: The Headless Knight of the Old Road; used by the self-test; sets `fig3_c1`*
- `fig3_clue_sign` — A Hand-Painted Sign (only after `fig3_open`) — *quest marker: The Figure It Out Gang: The Headless Knight of the Old Road; used by the self-test; sets `fig3_c2`*
- `fig3_clue_receipt` — A Receipt in the Verge (only after `fig3_open`) — *quest marker: The Figure It Out Gang: The Headless Knight of the Old Road; used by the self-test; sets `fig3_c3`*
- `fig3_trap` — The Trap (only after `fig3_trap_ready`, gone after `fig3_trap`) — *quest marker: The Figure It Out Gang: The Headless Knight of the Old Road; used by the self-test; sets `fig3_trap`; advances a quest*
- `road_dusk_milestone` — Follow the Road That Wasn't There (only after `here_known`) — *quest marker: The City Formerly Known As; used by the self-test; travel; sets `here_visited`; advances a quest; travels to `here_gate`*

**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):

- 1 × **Ash Crawler** (`road_crawler_1`) — story/test: keep
- 2 × **Grave Rat** (`road_rat_1`…) — story/test: keep
- 1 × **The Headless Knight of the Old Road** (`fig3_knight`) — group `fig3`, only after `fig3_trap`, story/test: keep
- 3 × **Hedge Goblin** (`road_goblin_0`…)
- 2 × **Kevin, Bandit (Level Zero)** (`road_kevin_0`…)

**Arrival points:** `from_bellwether`, `from_annex`, `road_dusk` — *arrival point for a door, boat, dialogue or new game: keep*

<details><summary>Free to move or delete (11): flavour notes, gathering spots, fishing spots</summary>

`scout_journal` (readable: Field Journal of Kaelen, Ashbound), `baggy_case_board` (readable: CASE FILE #1: THE MISSING TOWN), `old__wayside_sage_20_80` (harvest), `old__wayside_sage_140_90` (harvest), `old__iron_scrap_180_110` (harvest), `old__iron_scrap_140_110` (harvest), `old__ashwood_branch_60_100` (harvest), `old__ashwood_branch_90_110` (harvest), `old__pine_resin_0_115` (harvest), `old__marigold_200_60` (harvest), `figure_wagon_sign` (readable: The Figure It Out Wagon)

</details>


## Adding new monster areas and dungeons

Everything you need is in the Blender palette (**Uncounted Objects**): Shift+D a monster, chest, door, lever, torch or gathering spot and move it where you want it. A few tips:

- **Monsters**: each one patrols between two points (its `patrol_a` / `patrol_b` fields) or stands guard if they're the same. Mix tougher ones deeper in. Rough difficulty below (health / damage per hit); the player starts with about 75 health and reaches 150+ by the end of Chapter One.
- **Chests**: set `loot_table` to one of the tables below (or add `fixed_items` for a guaranteed reward). Locked chests (`locked`) need lockpicks or a key (`key_id`).
- **A dungeon's feel**: each area has a **zone** (its own music, ambience like the crypt drips, fog, light and the name banner when you enter). Zones aren't editable in Blender yet: tell me roughly where the new area is and the mood you want, and I'll add its zone (or extend an existing one).
- **Doors between areas** use the `travel` type with a `travel_spawn` (an arrival point you place inside).
- **Tell me what you built** (a sentence or a screenshot): I can write a quest, a boss, notes and loot to go with it, rebalance the monsters for the new length, and add your areas to the companions' comments ("Smells like a tomb, 'cause it is one").

| Monster | Health | Damage | XP |
|---|---|---|---|
| Will-o'-the-Wisp (`wisp`) | 35 | 7 | 16 |
| Hedge Goblin (`hedge_goblin`) | 40 | 6 | 12 |
| Grave Rat (`grave_rat`) | 42 | 7 | 18 |
| Angry Badger (`angry_badger`) | 45 | 8 | 14 |
| Grey Wolf (`grey_wolf`) | 48 | 8 | 24 |
| Kevin, Bandit (Level Zero) (`kevin_bandit`) | 50 | 7 | 15 |
| Pinchwick Crab (`pinchwick_crab`) | 50 | 8 | 15 |
| Truffle Hog (`truffle_hog`) | 55 | 8 | 20 |
| Kobold Bookkeeper (`kobold_bookkeeper`) | 60 | 8 | 25 |
| Tide Acolyte (`tide_acolyte`) | 65 | 9 | 50 |
| Bone Clerk (`bone_clerk`) | 70 | 9 | 30 |
| Mouth of the Hunger (`here_mouth`) | 70 | 10 | 40 |
| Paperwork Elemental (`paperwork_elemental`) | 70 | 9 | 22 |
| The Phantom Clerk (`phantom_clerk`) | 70 | 6 | 30 |
| Wailing Footman (`wailing_footman`) | 70 | 9 | 45 |
| Ink Wraith (`ink_wraith`) | 75 | 8 | 45 |
| Ash Crawler (`ash_crawler`) | 78 | 10 | 30 |
| Gravedigger Ghoul (`ghoul_gravedigger`) | 80 | 10 | 25 |
| Salt Wight (`salt_wight`) | 85 | 11 | 28 |
| The Drowned (`the_drowned`) | 85 | 11 | 45 |
| The Headless Knight of the Old Road (`headless_knight`) | 85 | 8 | 40 |
| Restless Skeleton (`restless_skeleton`) | 90 | 12 | 35 |
| The Howler of Hollowmere (`howler`) | 90 | 8 | 30 |
| Animated Armour (`animated_armor`) | 120 | 14 | 55 |
| A Wolf in Grandmother's Nightgown (`granny_wolf`) | 150 | 13 | 85 |
| The Rat King (`rat_king`) | 160 | 13 | 90 |
| Lost Sentinel (`lost_sentinel`) | 170 | 19 | 65 |
| Grubnik Quillsby, Esq. (Cornered) (`quillsby_cornered`) | 190 | 12 | 110 |
| The Repossession Golem (`repossession_golem`) | 230 | 12 | 120 |
| Archivist Shade Morvath (`crypt_keeper`) | 280 | 18 | 140 |
| Sir Percival, the Wrathful Host (`wrathful_host`) | 280 | 17 | 170 |
| The Dreaming Limb (`dreaming_limb`) | 300 | 15 | 160 |
| The Lullaby Warden (`lullaby_warden`) | 300 | 18 | 160 |
| Avatar of the Name-Eater (`name_eater_avatar`) | 340 | 16 | 260 |
| The Unsaying (`here_unsaying`) | 380 | 16 | 220 |

**Loot tables:** `core:loot.vermin_drop`, `core:loot.crypt_basic`, `core:loot.crypt_elite`, `core:loot.crypt_boss`, `core:loot.secret_widowmaker`, `core:loot.vault_warden`, `core:loot.ash_crawler`, `core:loot.bone_clerk`, `core:loot.ink_wraith`, `core:loot.truffle_hog`, `core:loot.rat_king`, `core:loot.drowned`, `core:loot.avatar`, `core:loot.wolf`, `core:loot.fish_harbour`, `core:loot.fish_reef`, `core:loot.fish_pond`, `core:loot.wrathful_host`, `core:loot.dreaming_limb`, `core:loot.granny_wolf`, `core:loot.repossession_golem`, `core:loot.kobold_bookkeeper`, `core:loot.quillsby`, `core:loot.here_mouth`, `core:loot.here_unsaying`


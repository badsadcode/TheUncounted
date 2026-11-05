# Source art

Original hand-painted sprite sheets (8 columns = directions, 6 rows = idle, walk A, walk B, windup, attack,
stagger/corpse; black background). The game uses the converted 128 px sheets in `assets/sprites/`, made with
`tools/import_spritesheet.py`. Keep the originals here so the conversion can be redone or improved.

| Original | In-game sheet | Used by |
|---|---|---|
| `spritesheets/grave_rat.png` | `assets/sprites/enemies/grave_rat_painted.png` | Grave Rat |
| `spritesheets/skeleton.png` | `assets/sprites/enemies/skeleton_painted.png` | Restless Skeleton |
| `spritesheets/crypt_keeper.png` | `assets/sprites/enemies/crypt_keeper_painted.png` | Crypt Keeper |
| `spritesheets/lullaby_warden.png` | `assets/sprites/enemies/lullaby_warden_painted.png` | The Lullaby Warden |
| `spritesheets/ash_crawler.png` | `assets/sprites/enemies/ash_crawler_painted.png` | Ash Crawler |
| `spritesheets/ashbound_scout.png` | `assets/sprites/npcs/ashbound_scout_painted.png` | Kaelen |
| `spritesheets/brother_aldous.png` | `assets/sprites/npcs/brother_aldous_painted.png` | Brother Aldous |
| `spritesheets/clerk_oakhaven.png` | `assets/sprites/npcs/clerk_oakhaven_painted.png` | Clerk Oakhaven |
| `spritesheets/erased_spirit.png` | `assets/sprites/npcs/erased_spirit_painted.png` | The Erased Spirit |
| `spritesheets/innkeeper_marta.png` | `assets/sprites/npcs/innkeeper_marta_painted.png` | Marta |
| `spritesheets/librarian_fenwick.png` | `assets/sprites/npcs/librarian_fenwick_painted.png` | Fenwick |
| `spritesheets/merchant_vaelen.png` | `assets/sprites/npcs/merchant_vaelen_painted.png` | Vaelen |
| `spritesheets/bone_clerk.png` | `assets/sprites/enemies/bone_clerk_painted.png` | Bone Clerk |
| `spritesheets/critic_mortimer.png` | `assets/sprites/npcs/critic_mortimer_painted.png` | Mortimer Quill |
| `spritesheets/detective_baggy.png` | `assets/sprites/npcs/detective_baggy_painted.png` | Baggy |
| `spritesheets/dreaming_limb.png` | `assets/sprites/enemies/dreaming_limb_painted.png` | The Dreaming Limb |
| `spritesheets/witch_sabrino.png` | `assets/sprites/npcs/witch_sabrino_painted.png` | Sabrino |
| `spritesheets/gale_elder.png` | `assets/sprites/npcs/gale_elder_painted.png` | Tom Gale (and the Taller Stranger) |
| `spritesheets/gale_younger.png` | `assets/sprites/npcs/gale_younger_painted.png` | Abel Gale (and the Shorter Stranger) |
| `spritesheets/ghost_percival.png` | `assets/sprites/npcs/ghost_percival_painted.png` | Sir Percival |
| `spritesheets/granny_wolf.png` | `assets/sprites/enemies/granny_wolf_painted.png` | Wolf in Grandmother's Nightgown |
| `spritesheets/grey_wolf.png` | `assets/sprites/enemies/grey_wolf_painted.png` | Grey Wolf |
| `spritesheets/harbourmaster.png` | `assets/sprites/npcs/harbourmaster_painted.png` | The Harbourmaster |
| `spritesheets/hunter_hollis.png` | `assets/sprites/npcs/hunter_hollis_painted.png` | Hollis the Grey |
| `spritesheets/impresario_odette.png` | `assets/sprites/npcs/impresario_odette_painted.png` | Odette |
| `spritesheets/ink_wraith.png` | `assets/sprites/enemies/ink_wraith_painted.png` | Ink Wraith |
| `spritesheets/keeper_ondine.png` | `assets/sprites/npcs/keeper_ondine_painted.png` | Ondine Marsh |
| `spritesheets/mother_brine.png` | `assets/sprites/npcs/mother_brine_painted.png` | Mother Brine |
| `spritesheets/name_eater_avatar.png` | `assets/sprites/enemies/name_eater_avatar_painted.png` | Avatar of the Name-Eater |
| `spritesheets/professor_pickering.png` | `assets/sprites/npcs/professor_pickering_painted.png` | Professor Pickering |
| `spritesheets/rat_king.png` | `assets/sprites/enemies/rat_king_painted.png` | The Rat King |
| `spritesheets/silas_gale.png` | `assets/sprites/npcs/silas_gale_painted.png` | Old Silas |
| `spritesheets/steve.png` | `assets/sprites/npcs/steve_painted.png` | Steve |
| `spritesheets/the_drowned.png` | `assets/sprites/enemies/the_drowned_painted.png` | The Drowned |
| `spritesheets/tide_acolyte.png` | `assets/sprites/enemies/tide_acolyte_painted.png` | Tide Acolyte |
| `spritesheets/tide_priest.png` | `assets/sprites/npcs/tide_priest_painted.png` | The Tide Priest |
| `spritesheets/trout.png` | `assets/sprites/npcs/trout_painted.png` | Trout |
| `spritesheets/truffle_hog.png` | `assets/sprites/enemies/truffle_hog_painted.png` | Truffle Hog |
| `spritesheets/vampire_ashgrave.png` | `assets/sprites/npcs/vampire_ashgrave_painted.png` | Lord Ashgrave |
| `spritesheets/wailing_footman.png` | `assets/sprites/enemies/wailing_footman_painted.png` | Wailing Footman |
| `spritesheets/werewolf_rolf.png` | `assets/sprites/npcs/werewolf_rolf_painted.png` | Rolf |
| `spritesheets/wrathful_host.png` | `assets/sprites/enemies/wrathful_host_painted.png` | The Wrathful Host |
| `spritesheets/grout.webp` | `assets/sprites/npcs/grout_painted.png` | Grout |

**A whole package at once** (folder or .zip; file names just need to contain the character's name):

```bash
python tools/import_package.py path/to/package.zip            # dry run: which file goes to which character
python tools/import_package.py path/to/package.zip --apply    # import all, update content, write import_report.png
```
| `spritesheets/figure_agnes.png` | `assets/sprites/npcs/figure_agnes_painted.png` | Figure Agnes |
| `spritesheets/howler.png` | `assets/sprites/enemies/howler_painted.png` | Howler |
| `spritesheets/figure_primrose.png` | `assets/sprites/npcs/figure_primrose_painted.png` | Figure Primrose |
| `spritesheets/phantom_clerk.png` | `assets/sprites/enemies/phantom_clerk_painted.png` | Phantom Clerk |
| `spritesheets/figure_rodrick.png` | `assets/sprites/npcs/figure_rodrick_painted.png` | Figure Rodrick |
| `spritesheets/figure_snacks.png` | `assets/sprites/npcs/figure_snacks_painted.png` | Figure Snacks |
| `spritesheets/angry_badger.png` | `assets/sprites/enemies/angry_badger_painted.png` | Angry Badger |
| `spritesheets/druid_bramble.png` | `assets/sprites/npcs/druid_bramble_painted.png` | Druid Bramble |
| `spritesheets/druid_squirrel.png` | `assets/sprites/npcs/druid_squirrel_painted.png` | Druid Squirrel |
| `spritesheets/dragon_cindermaw.png` | `assets/sprites/npcs/dragon_cindermaw_painted.png` | Dragon Cindermaw |
| `spritesheets/ghoul_gravedigger.png` | `assets/sprites/enemies/ghoul_gravedigger_painted.png` | Ghoul Gravedigger |
| `spritesheets/kobold_quillsby.png` | `assets/sprites/npcs/kobold_quillsby_painted.png` | Kobold Quillsby |
| `spritesheets/hedge_goblin.png` | `assets/sprites/enemies/hedge_goblin_painted.png` | Hedge Goblin |
| `spritesheets/kevin_bandit.png` | `assets/sprites/enemies/kevin_bandit_painted.png` | Kevin Bandit |
| `spritesheets/kobold_bookkeeper.png` | `assets/sprites/enemies/kobold_bookkeeper_painted.png` | Kobold Bookkeeper |
| `spritesheets/paperwork_elemental.png` | `assets/sprites/enemies/paperwork_elemental_painted.png` | Paperwork Elemental |
| `spritesheets/pinchwick_crab.png` | `assets/sprites/enemies/pinchwick_crab_painted.png` | Pinchwick Crab |
| `spritesheets/salt_wight.png` | `assets/sprites/enemies/salt_wight_painted.png` | Salt Wight |
| `spritesheets/wisp.png` | `assets/sprites/enemies/wisp_painted.png` | Wisp |
| `spritesheets/animated_armor.png` | `assets/sprites/enemies/animated_armor_painted.png` | Animated Armor |
| `spritesheets/headless_knight.png` | `assets/sprites/enemies/headless_knight_painted.png` | Headless Knight |
| `spritesheets/lost_sentinel.png` | `assets/sprites/enemies/lost_sentinel_painted.png` | Lost Sentinel |
| `spritesheets/repossession_golem.png` | `assets/sprites/enemies/repossession_golem_painted.png` | Repossession Golem |
| `spritesheets/auditor.png` | `assets/sprites/npcs/auditor_painted.png` | Auditor |
| `spritesheets/friend_coth.png` | `assets/sprites/npcs/friend_coth_painted.png` | Coth Castaway |
| `spritesheets/friend_dunstan.png` | `assets/sprites/npcs/friend_dunstan_painted.png` | Dunstan |
| `spritesheets/friend_eranu.png` | `assets/sprites/npcs/friend_eranu_painted.png` | Eranu |
| `spritesheets/here_baker.png` | `assets/sprites/npcs/here_baker_painted.png` | Here Baker |
| `spritesheets/here_butt_butt.png` | `assets/sprites/npcs/here_butt_butt_painted.png` | Here Butt Butt |
| `spritesheets/here_cartographer.png` | `assets/sprites/npcs/here_cartographer_painted.png` | Here Cartographer |
| `spritesheets/here_echo.png` | `assets/sprites/npcs/here_echo_painted.png` | Here Echo |
| `spritesheets/here_gatekeeper.png` | `assets/sprites/npcs/here_gatekeeper_painted.png` | Here Gatekeeper |
| `spritesheets/here_inspector.png` | `assets/sprites/npcs/here_inspector_painted.png` | Here Inspector |
| `spritesheets/here_mouth.png` | `assets/sprites/enemies/here_mouth_painted.png` | Here Mouth |
| `spritesheets/here_night_merchant.png` | `assets/sprites/npcs/here_night_merchant_painted.png` | Here Night Merchant |
| `spritesheets/here_person_in_hat.png` | `assets/sprites/npcs/here_person_in_hat_painted.png` | Here Person In Hat |
| `spritesheets/here_unsaying.png` | `assets/sprites/enemies/here_unsaying_painted.png` | Here Unsaying |
| `spritesheets/old_tobble.png` | `assets/sprites/npcs/old_tobble_painted.png` | Old Tobble |

Re-convert one (example; `--match` keeps the in-game size equal to the old generated sheet, `--match-col` picks the
idle column used for that comparison: 0 for upright figures, 2 for side-on animals):

```bash
python tools/import_spritesheet.py art_source/spritesheets/clerk_oakhaven.webp assets/sprites/npcs/clerk_oakhaven_painted.png --frame 128 --match assets/sprites/npcs/clerk_oakhaven.png --match-col 0
```

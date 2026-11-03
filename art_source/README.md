# Source art

Original hand-painted sprite sheets (8 columns = directions, 6 rows = idle, walk A, walk B, windup, attack,
stagger/corpse; black background). The game uses the converted 128 px sheets in `assets/sprites/`, made with
`tools/import_spritesheet.py`. Keep the originals here so the conversion can be redone or improved.

| Original | In-game sheet | Used by |
|---|---|---|
| `spritesheets/grave_rat.webp` | `assets/sprites/enemies/grave_rat_painted.png` | Grave Rat |
| `spritesheets/skeleton.webp` | `assets/sprites/enemies/skeleton_painted.png` | Restless Skeleton |
| `spritesheets/crypt_keeper.webp` | `assets/sprites/enemies/crypt_keeper_painted.png` | Crypt Keeper |
| `spritesheets/lullaby_warden.webp` | `assets/sprites/enemies/lullaby_warden_painted.png` | The Lullaby Warden |
| `spritesheets/ash_crawler.webp` | `assets/sprites/enemies/ash_crawler_painted.png` | Ash Crawler |
| `spritesheets/ashbound_scout.webp` | `assets/sprites/npcs/ashbound_scout_painted.png` | Kaelen |
| `spritesheets/brother_aldous.webp` | `assets/sprites/npcs/brother_aldous_painted.png` | Brother Aldous |
| `spritesheets/clerk_oakhaven.webp` | `assets/sprites/npcs/clerk_oakhaven_painted.png` | Clerk Oakhaven |
| `spritesheets/erased_spirit.webp` | `assets/sprites/npcs/erased_spirit_painted.png` | The Erased Spirit |
| `spritesheets/innkeeper_marta.webp` | `assets/sprites/npcs/innkeeper_marta_painted.png` | Marta |
| `spritesheets/librarian_fenwick.webp` | `assets/sprites/npcs/librarian_fenwick_painted.png` | Fenwick |
| `spritesheets/merchant_vaelen.webp` | `assets/sprites/npcs/merchant_vaelen_painted.png` | Vaelen |
| `spritesheets/bone_clerk.webp` | `assets/sprites/enemies/bone_clerk_painted.png` | Bone Clerk |
| `spritesheets/critic_mortimer.webp` | `assets/sprites/npcs/critic_mortimer_painted.png` | Mortimer Quill |
| `spritesheets/detective_baggy.webp` | `assets/sprites/npcs/detective_baggy_painted.png` | Baggy |
| `spritesheets/dreaming_limb.webp` | `assets/sprites/enemies/dreaming_limb_painted.png` | The Dreaming Limb |
| `spritesheets/witch_sabrino.webp` | `assets/sprites/npcs/witch_sabrino_painted.png` | Sabrino |
| `spritesheets/gale_elder.webp` | `assets/sprites/npcs/gale_elder_painted.png` | Tom Gale (and the Taller Stranger) |
| `spritesheets/gale_younger.webp` | `assets/sprites/npcs/gale_younger_painted.png` | Abel Gale (and the Shorter Stranger) |
| `spritesheets/ghost_percival.webp` | `assets/sprites/npcs/ghost_percival_painted.png` | Sir Percival |
| `spritesheets/granny_wolf.webp` | `assets/sprites/enemies/granny_wolf_painted.png` | Wolf in Grandmother's Nightgown |
| `spritesheets/grey_wolf.webp` | `assets/sprites/enemies/grey_wolf_painted.png` | Grey Wolf |
| `spritesheets/harbourmaster.webp` | `assets/sprites/npcs/harbourmaster_painted.png` | The Harbourmaster |
| `spritesheets/hunter_hollis.webp` | `assets/sprites/npcs/hunter_hollis_painted.png` | Hollis the Grey |
| `spritesheets/impresario_odette.webp` | `assets/sprites/npcs/impresario_odette_painted.png` | Odette |
| `spritesheets/ink_wraith.webp` | `assets/sprites/enemies/ink_wraith_painted.png` | Ink Wraith |
| `spritesheets/keeper_ondine.webp` | `assets/sprites/npcs/keeper_ondine_painted.png` | Ondine Marsh |
| `spritesheets/mother_brine.webp` | `assets/sprites/npcs/mother_brine_painted.png` | Mother Brine |
| `spritesheets/name_eater_avatar.webp` | `assets/sprites/enemies/name_eater_avatar_painted.png` | Avatar of the Name-Eater |
| `spritesheets/professor_pickering.webp` | `assets/sprites/npcs/professor_pickering_painted.png` | Professor Pickering |
| `spritesheets/rat_king.webp` | `assets/sprites/enemies/rat_king_painted.png` | The Rat King |
| `spritesheets/silas_gale.webp` | `assets/sprites/npcs/silas_gale_painted.png` | Old Silas |
| `spritesheets/steve.webp` | `assets/sprites/npcs/steve_painted.png` | Steve |
| `spritesheets/the_drowned.webp` | `assets/sprites/enemies/the_drowned_painted.png` | The Drowned |
| `spritesheets/tide_acolyte.webp` | `assets/sprites/enemies/tide_acolyte_painted.png` | Tide Acolyte |
| `spritesheets/tide_priest.webp` | `assets/sprites/npcs/tide_priest_painted.png` | The Tide Priest |
| `spritesheets/trout.webp` | `assets/sprites/npcs/trout_painted.png` | Trout |
| `spritesheets/truffle_hog.webp` | `assets/sprites/enemies/truffle_hog_painted.png` | Truffle Hog |
| `spritesheets/vampire_ashgrave.webp` | `assets/sprites/npcs/vampire_ashgrave_painted.png` | Lord Ashgrave |
| `spritesheets/wailing_footman.webp` | `assets/sprites/enemies/wailing_footman_painted.png` | Wailing Footman |
| `spritesheets/werewolf_rolf.webp` | `assets/sprites/npcs/werewolf_rolf_painted.png` | Rolf |
| `spritesheets/wrathful_host.webp` | `assets/sprites/enemies/wrathful_host_painted.png` | The Wrathful Host |
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

Re-convert one (example; `--match` keeps the in-game size equal to the old generated sheet, `--match-col` picks the
idle column used for that comparison: 0 for upright figures, 2 for side-on animals):

```bash
python tools/import_spritesheet.py art_source/spritesheets/clerk_oakhaven.webp assets/sprites/npcs/clerk_oakhaven_painted.png --frame 128 --match assets/sprites/npcs/clerk_oakhaven.png --match-col 0
```

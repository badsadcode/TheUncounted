# Sprite sheets still to remake

These are the game's current *generated* sheets, scaled up 3x on black so they match the layout of the hand-painted
ones: **8 columns** (front, front-left, left, back-left, back, back-right, right, front-right) x **6 rows**
(idle, walk A, walk B, windup, attack, then stagger in columns 1-4 and corpse/lying-down in columns 5-8).
Keep the same order and a plain black background; the importer handles the rest. `_overview.png` shows them all.
Write the 8 directions turning the same way as the earlier sheets (front, then turning to the character's right).

Suggested order: the characters Toasty spends the most time with first.

## Main characters
| File | Who | Notes for the remake |
|---|---|---|
| `trout.png` | **Trout**, Hollis's horse | Bay mare, white blaze, red saddle. Calm, unbothered. (Four-legged: the walk rows should be a trot.) |

## Hollowmere Manor
| File | Who | Notes |
|---|---|---|
| `werewolf_rolf.png` | **Rolf** | Huge shaggy werewolf-man, golden eyes, no shirt, gardener with a trowel. Gentle. |
| `vampire_ashgrave.png` | **Lord Ashgrave** | Pale brooding young vampire, long black coat, blood-red cloak lining, skin that glitters faintly. |
| `wrathful_host.png` | **The Wrathful Host** (boss) | Same ghost as Percival but furious: red, flaring, floating robes. |
| `wailing_footman.png` | **Wailing Footman** (enemy) | Ghostly servant in old livery, pale blue, mouth open in a wail. |

## Saltmere Docks
| File | Who | Notes |
|---|---|---|
| `tide_priest.png` | **The Tide Priest** | Cult leader, dark teal robes with gold trim, unsettling. |

## Monsters
| File | What | Notes |
|---|---|---|
| `the_drowned.png` | The Drowned | Waterlogged greenish corpse-men, glowing eyes, seaweed. |
| `tide_acolyte.png` | Tide Acolyte | Hooded teal cultist with a glowing green spell. |
| `truffle_hog.png` | Truffle Hog | A pink-brown pig snuffling for truffles. |

## The Figure It Out Gang (Toasty's mystery-gang spinoff)
Placeholder sheets rendered by `tools/build_sprites_prerendered.py`. Same 8x6 layout. (Not in `_overview.png`.)
| File | Who | Notes |
|---|---|---|
| `figure_rodrick.png` | **Sir Rodrick Ascot-Smythe** | Square-jawed blond leader, white tunic, orange cravat, coil of rope. Heroic poses, bad plans. |
| `figure_primrose.png` | **Lady Primrose Vane** | Tall, glamorous, red hair pinned up, purple gown, green silk scarf. Secretly a brawler. |
| `figure_agnes.png` | **Agnes Thimble** | Short, huge orange jumper, red skirt, thick spectacles (sliding off), a book. |
| `figure_crumbs.png` | **Barnaby "Crumbs" Moss** | Lanky, scruffy beard, baggy green shirt, brown trousers, sandwich. Permanently about to flee. |
| `figure_snacks.png` | **Snacks** | Owlbear *cub*: dog-sized, brown feathers and fur, owl face, enormous worried eyes. (Four-legged.) |
| `phantom_clerk.png` | **The Phantom Clerk** (enemy) | A bedsheet ghost in Bureau robes, glowing green ink smears, a DECEASED stamp. Clearly someone underneath. |
| `howler.png` | **The Howler of Hollowmere** (enemy) | A shaggy "werewolf" costume, wooden claws, and very obvious sandals. |

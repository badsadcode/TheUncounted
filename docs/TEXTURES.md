# The Uncounted: texture list and spec

A brief for painting the world textures of **The Uncounted**, a first-person fantasy RPG. Environments are simple
low-poly 3D (boxes, walls, floors, stairs, pillars) wrapped in small pixel-art textures, shown with crisp nearest-neighbour
filtering, a little colour dithering and warm torch light. Think 90s dungeon crawlers made today: chunky readable
pixels, not photo-real. The characters (painted sprites) should sit in front of these without clashing.

---

## 1. Technical spec (applies to every texture)

- **Size:** 128 x 128 px. (The current set is 64 x 64; 128 is the sweet spot for more detail with the same chunky
  look. Keep pixels crisp: no blur, no soft gradients, no JPEG artefacts.)
- **Seamless:** must tile perfectly on all four edges. Walls and floors repeat many times (a street might repeat a cobble
  texture 20 times), so avoid any single standout feature (one big crack, one skull) that makes the repetition obvious.
- **Even lighting:** no strong baked-in shadow direction, no vignette. The game lights everything itself (torches,
  moonlight). A soft top-left light is fine for small details like brick edges.
- **Mid-tones:** not too dark, not too bright. The game adds night-time darkness and fog, so a texture that's already very
  dark becomes a black smear. Aim for roughly 35–65% brightness overall.
- **Palette:** muted, slightly desaturated fantasy colours with a few accents (moss green, rust, gold). About 16–32
  colours per texture keeps the pixel-art feel.
- **Format:** PNG, square, no transparency, unless the texture is marked *(cut-out)* below, which needs a transparent
  background.
- **Naming:** use the exact file names below, e.g. `mossy_cobble.png`.
- **Scale guide:** one texture tile covers about 2.6 m of wall horizontally and 3 m vertically, or about 2.6 m of floor.
  So a brick is about 1/8 of the tile wide, a floor plank about 1/6.

---

## 2. Textures in the game now (replacements)

| File | What it is | Where it's used |
|---|---|---|
| `mossy_cobble.png` | Grey cobblestones with moss in the gaps, worn smooth. | Village streets, dungeon floors, every stone staircase. *The most-seen texture in the game.* |
| `forest_grass.png` | Dark, rich woodland turf: short grass with a few darker clumps. | All grass ground: village edges, Old Road verges, Hollowmere grounds, the Whistling Wood. |
| `stone_wall.png` | Large grey ashlar blocks, mortar lines, a little weathering. | Town walls, manor exterior, pillars, the altar, levers, sarcophagi. |
| `timber_plaster.png` | Half-timbered wall: cream plaster between dark oak beams (diagonal braces). | Every village house and the inn. |
| `crypt_brick.png` | Small dark old bricks, damp, some crumbling, faint green-blue cast. | Crypts, the Registry Annex basement, the Sunken Chapel, stone archways, the ruin monolith. |
| `wood_planks.png` | Warm brown floorboards with nail heads and grain. | Every wooden floor (inn, manor, docks, piers); also handles of weapons and tools. |
| `roof_shingles.png` | Overlapping dark slate or wooden shingles, rows slightly uneven. | Every gabled roof. |
| `foliage_pine.png` | Dense dark-green pine needles, clumped. | Pine tree canopies. |
| `rune_crystal.png` | Glowing blue-violet crystal with carved runes. | The Silence monolith, staff and potion crystals, pressure plates, magic sword inlays. |
| `iron_metal.png` | Dark forged iron with rivets, slight rust at the edges. | Swords, maces, shields, gates, door bands, chests, torch brackets. |
| `gold_trim.png` | Ornate tarnished brass or gold trim with a simple pattern. | Chest corners, door studs, sword guards, lectern edges, keys. |
| `bookshelf_tex.png` | Rows of old book spines (mixed reds, browns, greens), shelf boards between rows. | Bookshelves, spell tomes. |
| `parchment_tex.png` | Aged cream paper with faint ink lines. | Ledgers, scrolls, the Records Office desk, bow grips. |

*(`diag_missing.png` is the purple "missing texture" checkerboard used for debugging. Don't replace it.)*

---

## 3. New textures that would make the world feel better (suggested additions)

The world currently re-uses the same handful of textures everywhere, so a fishing town looks like a crypt looks like a
manor. These would give each area its own feel. Ordered by how much they'd help.

### Ground
| File | What it is | Where it would go |
|---|---|---|
| `dirt_road.png` | Packed brown earth with cart ruts, small stones, the odd hoofprint. | The Old Road, village lanes, the Whistling Wood path. |
| `forest_floor.png` | Leaf litter, pine needles, twigs, small roots over dark soil. | Under the trees in the Whistling Wood. |
| `sand_wet.png` | Grey-brown wet sand with pebbles, bits of shell and kelp. | Saltmere's shore, the Sleepers' Reef. |
| `graveyard_soil.png` | Dark turned earth with sparse dead grass. | Hollowmere's graveyard, garden beds (Rolf's marrows). |
| `gravel_path.png` | Pale crunchy gravel. | Hollowmere's drive and garden paths. |
| `mud_puddles.png` | Dark mud with small reflective puddles. | Rainy Bellwether lanes, the docks' edges. |

### Walls
| File | What it is | Where it would go |
|---|---|---|
| `weathered_planks.png` | Grey sea-bleached boards, salt stains, barnacles near the bottom. | Saltmere: warehouses, tavern, fish sheds. |
| `manor_wallpaper.png` | Faded dark-green or burgundy damask wallpaper with a dado rail. | Hollowmere Manor interior rooms. |
| `wood_panelling.png` | Dark polished oak panels. | Manor library and study, the Records Office interior. |
| `cave_rock.png` | Rough natural rock, wet and uneven. | Caves under the reef, the Sunken Chapel's broken parts. |
| `red_brick.png` | Warm red bricks, sooty. | Chimneys, the bakery, a bit of variety in the village. |
| `barnacle_stone.png` | Sea-worn stone covered in barnacles and green weed. | The Sunken Chapel, harbour walls, the reef. |

### Floors
| File | What it is | Where it would go |
|---|---|---|
| `checker_marble.png` | Black-and-white marble tiles, a bit cracked. | The manor ballroom and foyer. |
| `flagstones.png` | Big irregular church flagstones. | The Church of the Last Dawn, the chapel nave, the Records Office. |
| `carpet_red.png` | Worn red carpet with a gold border pattern (a tileable runner). | Manor corridors, the grand stair. |
| `tavern_floor.png` | Dark sticky boards with ale stains and sawdust. | The Lantern Inn, the Drowned Lantern tavern. |
| `straw_hay.png` | Loose straw over boards. | Stables (Trout's home), barns, Steve's camp. |

### Roofs
| File | What it is | Where it would go |
|---|---|---|
| `roof_thatch.png` | Golden-brown straw thatch. | Cottages, farm buildings. |
| `roof_slate_mossy.png` | Blue-grey slate with moss and a few missing tiles. | Saltmere houses, the manor. |

### Water and sky (these need a small engine addition, which I'll handle)
| File | What it is | Where it would go |
|---|---|---|
| `water_surface.png` | Dark teal water with soft pixel highlights (seamless; the game scrolls it). | The harbour, the chapel pools, the reef. |
| `sky_night.png` | A wide panorama, 1024 x 256 (tiles left to right): night sky with clouds, a few stars and dark distant hills or forest at the bottom edge. | The horizon behind everything. *Big improvement to the mood.* |
| `sky_dusk.png` | Same layout at dusk: orange-to-purple sky, darker silhouette. | Optional for special scenes. |

### Scatter sprites *(cut-out, transparent background, these need a small engine addition)*
Small billboard sprites scattered on the ground to break up flat floors. 64 x 64 px each, standing upright, the bottom
edge is the ground.
| File | What it is |
|---|---|
| `grass_tuft.png` | A clump of tall grass. |
| `fern.png` | A woodland fern. |
| `bush.png` | A round low bush. |
| `flowers_wild.png` | A few small wildflowers (white, yellow). |
| `mushrooms.png` | A cluster of small toadstools. |
| `reeds.png` | Tall shoreline reeds. |
| `cobweb.png` | A corner cobweb (for crypt and manor ceilings). |

---

## 4. Getting them into the game

Send them over in a zip like the sprite sheets. The current textures are baked into the 3D models that use them, so I'll
swap them in with a script and rebuild. The new ones also need new wall/floor pieces and a bit of world editing, which
I'll do area by area. Partial sets are fine.

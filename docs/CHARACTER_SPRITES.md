# The Uncounted: character list and sprite-sheet spec

A brief for anyone (human or AI) painting character sprite sheets for **The Uncounted**, a first-person fantasy RPG
with low-poly 3D environments and hand-painted 2D characters (billboard sprites that turn to face the camera, like
classic 90s shooters). The tone is cosy-spooky comedy: bureaucratic afterlife, a haunted manor, a fishing town with a
cult, a meddling mystery gang.

**Pronouns:** Baggy, Sabrino and Kaelen are always *they/them*. For everyone else, follow the descriptions below.

---

## 1. Sheet layout (the important bit)

One PNG/WEBP per character: **8 columns x 6 rows**, an even grid, every cell the same size.

### Columns = facing direction (as seen by the viewer)

| Col | Facing |
|---|---|
| 0 | **Front**: looking straight at the viewer |
| 1 | Front, turned three-quarters (body pointing towards screen-left) |
| 2 | **Profile facing screen-left** |
| 3 | Back three-quarters (walking away, towards the upper left) |
| 4 | **Back**: seen from directly behind |
| 5 | Back three-quarters (walking away, towards the upper right) |
| 6 | **Profile facing screen-right** |
| 7 | Front, turned three-quarters (body pointing towards screen-right) |

So it's front, then the character turns on the spot until we see the back, then turns on round to the front again.
Columns 5-7 are usually mirror images of 3-1, but painting them separately lets asymmetric details (a sword on one
hip, a staff in one hand, a missing eye) stay on the correct side.

### Rows = animation state

| Row | State | What to draw |
|---|---|---|
| 0 | **Idle** | Standing relaxed, weight even. The pose players see most. |
| 1 | **Walk A** | Mid-stride: left leg forward, right arm forward. |
| 2 | **Walk B** | The opposite stride: right leg forward, left arm forward. (Rows 1 and 2 alternate, so together they make the walk cycle.) |
| 3 | **Wind-up** | Getting ready to act: weapon raised, staff lifted, fist drawn back, or a hand to the head for talkers. |
| 4 | **Attack / gesture** | The strike or the point: arm or weapon fully extended towards the facing direction. |
| 5 | **Stagger + corpse** | Columns 0-3: **hit-recoil**, flinching from a blow, arms flung out. Only 4 facings here: col 0 front, col 1 profile facing screen-left, col 2 back, col 3 profile facing screen-right. Columns 4-7: **lying on the ground** (knocked out or dead), drawn side-on and fitted inside the cell's width. The game uses column 4; columns 5-7 are spare variations. |

Four-legged animals (horse, wolf, pig-rat, owlbear cub) use the same grid. Their walk rows are a trot, wind-up is
rearing or crouching, and attack is a lunge or bite.

### Technical rules

- **Background:** one flat colour, ideally pure black `#000000`, with no gradient, texture, vignette, shadows on the floor,
  grid lines, labels or text. The importer removes the background by flood-filling from the edges, so dark paint
  *inside* the character is fine.
- **Keep every figure inside its own cell.** Nothing (tails, staffs, capes, outstretched arms, the corpse) should
  touch or cross into the neighbouring cell. Leave a small gap of background all round. Overlapping figures are the
  number-one cause of clipped frames.
- **Same scale and same ground line in every frame.** The feet should sit at the same height in every cell (about 92%
  of the way down the cell). The character must not grow, shrink or bob between columns.
- **Cell size:** anything from about 128 to 256 px square works. The game resamples to 128 x 128 per frame. Sheets so far
  have been about 1448 x 1086 (about 181 px cells).
- **Style:** painterly pixel art, readable at small size: clear silhouette, strong contrast between the figure and
  black, about a 3/4 top-down camera tilt, lit from the upper left. Glowing bits (eyes, orbs, flames) look great
  because the game adds a soft bloom.
- **One character per sheet**, with a consistent look in every frame (same outfit, same props in the same hand).
- **Format:** PNG or WEBP. Transparency is fine but not needed (black background works).

### How it gets into the game (for reference)

A whole package (folder or .zip) goes in with `python tools/import_package.py PACKAGE --apply`. Name each file after its character ("Vampire Ashgrave.png", "Kaelen.webp"...). The tool matches names, imports everything and writes a review picture that flags clipped or empty frames. Single sheets:

```bash
python tools/import_spritesheet.py art_source/spritesheets/NAME.webp assets/sprites/npcs/NAME_painted.png \
    --frame 128 --match assets/sprites/npcs/NAME.png --match-col 0
```

`--match` keeps the in-game height equal to the old sheet; `--match-col` is 0 for upright figures, 2 for side-on
animals. The original goes in `art_source/spritesheets/`. The character's `appearance` (in `content/npcs/core_npcs.json` or
`content/creatures/core_creatures.json`) then points at the new PNG and the matching `*_128.json` animation.

---

## 2. Characters

**Status:** ✅ hand-painted sheet in game · 🟡 generated placeholder (would love a painted one) · 🧊 3D model (no sheet needed)

### Bellwether village and the Bureau
| Character | Status | Description |
|---|---|---|
| **Clerk Oakhaven** | ✅ | Ancient, dusty clerk of the Royal Bureau of Records. Grey robes, ink-stained fingers, spectacles, a stamp always within reach. Kind beneath the paperwork. He runs the tabletop game nights. |
| **Vaelen the Quartermaster** | ✅ | Market trader: leather apron, satchels, a wide-brimmed hat, a coin purse and a salesperson's smile. Will sell anything, including ghost-repelling charms. |
| **Marta Kettleburn** | ✅ | Innkeeper of the Lantern Inn. Sturdy, apron, rolled sleeves, a tankard or ladle. Warm, worried about the villagers. |
| **Librarian Fenwick** | ✅ | Thin, anxious librarian, cardigan and robe, armfuls of books, tiny reading glasses. Takes overdue books very personally. |
| **Brother Aldous** | ✅ | Round, cheerful monk in a brown habit with a rope belt and sandals. Grows marrows, has come second at the vegetable show four years running. |
| **Kaelen of the Ashbound** (they/them) | ✅ | Ruin chronicler and companion. Hooded scout, travel-worn cloak, scroll case, bow or short blade. Quiet, observant. |
| **The Uncounted Witness** | ✅ | A spirit erased from the records: pale, translucent, faded edges, half there. |
| **Baggy** (they/them) | ✅ | Bumbling, good-hearted private eye (licence pending) and founding member of the Figure It Out Gang. Long rain-dark coat, hat, a magnifying glass, crumbs in the pockets. Always about to run away. Toasty's recurring character. |
| **Sabrino** (they/them) | ✅ | The Italian Witch (Wanted): a theatrical, slightly war-criminal witch. Tall dented pointed hat with a red sash, purple robes, a confident grin, fire at the fingertips. Toasty's recurring character. |
| **Steve** | ✅ | A level-one bandit living in the Whistling Wood. He's a human, and very proud of being a bandit. Patched leathers, a too-big hood, a rusty knife. |
| **Grout** | ✅ | Companion. A squat, mossy stone gargoyle: grey stone, stubby horns (one chipped), folded stone wings, glowing amber eyes, big fists, a scowl. Two hundred years on the Records Office roof. Grumpy, few words, punches hard. |
| **Cindermaw the Elder** | ✅ | Ancient dragon: dull ember-red scales, chipped horns, great leathery wings, golden eyes, tiny reading spectacles. Four-legged, huge. |
| **Grubnik Quillsby, Esq.** | ✅ | Small green kobold in a tailored waistcoat, gold spectacles, briefcase chained to one wrist, a ledger. |
| **Bramble Thistlewick** (squirrel) | ✅ | A red squirrel with tremendous dignity and a tiny acorn necklace. Four-legged, small. Really a druid. |
| **Bramble Thistlewick** (druid) | ✅ | Tall, bearded, mossy green robe, wooden staff with a green glow, small antlers, leaves in his beard. Goofy, kind, hay fever. |
| **Professor Pickering** | ✅ | Collegium academic, Dept. of Unusual Studies. Tweed, a notebook, wild hair, an excited pointing finger. |

### Hollowmere Manor
| Character | Status | Description |
|---|---|---|
| **Hollis the Grey** | ✅ | Grizzled monster hunter: grey hair, scarred face, leather armour, two swords on the back. Plays cards. Owns a horse. |
| **Trout** | ✅ | Hollis's horse: bay mare, white blaze, red saddle. Calm, unbothered, keeps ending up on roofs. |
| **Lord Ashgrave** | ✅ | Brooding young vampire lodger. Pale, black slicked hair, long black coat, blood-red high-collared cape, faint glitter. |
| **Rolf** | ✅ | Gentle werewolf head gardener: shaggy brown wolf-man, golden eyes, a brown work jumper, trousers, boots. Grows prize marrows. |
| **Sir Percival Hollowmere** | ✅ | The friendly ghost host of the manor: pale blue, translucent, old-fashioned finery, still hosting dinner parties. |
| **Madame Odette Velour** | ✅ | Impresario of the Velour Players: feathers, a long cigarette holder, a dramatic gown, very theatrical. |
| **Mortimer Quill** | ✅ | The Last Critic: a ghostly theatre critic. Deceased, unimpressed, notebook and quill, a sneer. |

### Saltmere Docks and the Sunken Chapel
| Character | Status | Description |
|---|---|---|
| **The Harbourmaster** | ✅ | Salt-crusted harbourmaster in a heavy coat and cap, ledger under one arm. Name withheld, for reasons. |
| **Mother Brine** | ✅ | Old, hunched keeper of the Drowned Lantern tavern. Shawl, a ladle, cooks a suspicious chowder. |
| **Old Silas** | ✅ | Weathered fisherman of the North Pier: oilskins, a beard, a fishing rod, nine spare rods. |
| **Ondine Marsh** | ✅ | Keeper of the Saltmere lighthouse: practical coat, lantern, sharp eyes. |
| **The Tide Priest** | ✅ | Cult leader of the Esoteric Order of the Drowned Ledger: dark teal robes with gold wave trim, golden mitre, a gold orb staff. |
| **The Gale brothers** (Thomas & Abel) | ✅ | Two nameless-seeming strangers, one tall and one short, in long coats and hats. |

### The Figure It Out Gang (a mystery-gang spinoff Toasty invented)
| Character | Status | Description |
|---|---|---|
| **Bread** | ✅ | Square-jawed blond leader. White tunic, orange cravat, a coil of rope. Heroic poses, terrible trap plans. |
| **Badnee** | ✅ | Tall and glamorous, red hair pinned up, purple gown, green silk scarf. Always being kidnapped; secretly punches very hard. |
| **Karma** | ✅ | Short, huge orange jumper, red skirt, very thick spectacles (always sliding off), a book. Actually solves every case. |
| **Doobie** | ✅ | Owlbear *cub*: dog-sized, four-legged, brown feathers and fluffy fur, owl face, enormous worried eyes. Cowardly. Loves Crumb Cakes. |
| *(Baggy)* | ✅ | Gang member, see above. |
| **The Figure It Out Wagon** | 🧊 | A painted caravan (3D prop): teal, orange stripes, flowers, a big question mark. |

### Monsters
| Creature | Status | Description |
|---|---|---|
| **Grave Rat** | ✅ | Dog-sized graveyard rat, mangy, red eyes. |
| **Restless Skeleton** | ✅ | Classic shambling skeleton with a rusty sword. |
| **Ash Crawler** | ✅ | Low insect-like crawler made of ash and embers. |
| **Archivist Shade Morvath** | ✅ | Boss: a towering spectral archivist, robes and ledgers. |
| **The Lullaby Warden** | ✅ | Boss: tall, eerie nursery spirit. |
| **Bone Clerk** | ✅ | Skeletal Bureau clerk with spectacles and a ledger. |
| **Ink Wraith** | ✅ | Floating wraith made of dripping black ink. |
| **Truffle Hog** | ✅ | A very large pink rat that believes it is a pig. |
| **Wailing Footman** | ✅ | Ghostly servant in old livery and chains, pale blue, mouth open in a wail. |
| **The Rat King** | ✅ | Boss: a crowned, oversized rat monarch. |
| **Sir Percival, the Wrathful Host** | ✅ | Boss: Percival enraged, red, flaming head, tattered floating robes, fire staff. |
| **The Drowned** | ✅ | Hooded, waterlogged dead from the sea: teal-green tattered cloak, glowing eyes. |
| **Tide Acolyte** | ✅ | Cultist in dark teal robes with a rope sash and a glowing orb staff. |
| **Avatar of the Name-Eater** | ✅ | Huge eldritch boss of the Sunken Chapel. |
| **Grey Wolf** | ✅ | A grey wolf (four-legged). |
| **A Wolf in Grandmother's Nightgown** | ✅ | Exactly what it says: a wolf in a nightgown and bonnet. |
| **The Dreaming Limb** | ✅ | Giant eldritch tentacle from the reef. |
| **The Phantom Clerk** | ✅ | A bedsheet "ghost" in Bureau robes with glowing green ink smears and a DECEASED stamp. Clearly someone underneath. |
| **The Howler of Hollowmere** | ✅ | A shaggy fake-werewolf costume: wooden claws and very obvious sandals. |
| **Kobold Bookkeeper** | ✅ | Junior kobold clerk: green scales, blue waistcoat, spectacles, swings a red ledger. |
| **Kevin, Bandit (Level Zero)** | ✅ | Steve's cousin: patched leathers, a too-big green hood, a rusty sword held the wrong way round. Earnest. |
| **Hedge Goblin** | ✅ | Small green goblin wearing a cooking pot as a helmet, waving a big spoon. Glowing yellow eyes. Leaves in its hair. |
| **Angry Badger** | ✅ | A badger: black and white stripes, very small, absolutely furious. Four-legged. |
| **Will-o'-the-Wisp** | ✅ | A floating ball of pale green-blue light with wispy trails, giggling. No body. |
| **Gravedigger Ghoul** | ✅ | Gaunt grey-green undead gravedigger in a flat cap and rags, holding a shovel. Glowing green eyes. |
| **Pinchwick Crab** | ✅ | A big red harbour crab with oversized claws and an indignant face. Many-legged, sideways. |
| **Paperwork Elemental** | ✅ | A floating figure made of folded forms and loose paper in a hooded robe, holding a red ledger. Pages flutter off it. |
| **Salt Wight** | ✅ | A drowned sailor's ghost crusted in white salt, pale blue robes, a staff with a frosty orb. Translucent, floating. |
| **The Repossession Golem** | 🧊 | Iron golem stamped REPOSSESSED (uses the sentinel 3D model). |
| **Lost Sentinel** | 🧊 | Stone construct (3D model). |
| **Animated Armour** | 🧊 | Walking suit of armour (3D model). |

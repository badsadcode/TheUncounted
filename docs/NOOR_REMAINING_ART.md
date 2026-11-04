# The Uncounted: art still needed (for Noor)

**The Uncounted** is a first-person fantasy RPG made as a gift for a streamer friend, Toasty: low-poly 3D places and hand-painted 2D pixel-art characters that turn to face the camera, like classic 90s games. The tone is cosy-spooky comedy: a bureaucratic afterlife (the hero has been declared legally dead), a haunted manor, a fishing town with a cult, a city whose name was eaten. Muted, earthy colours with candlelight; gentle humour in faces and objects.

Everything listed here is **still missing**: the game runs with simple placeholders until each file arrives, and anything delivered goes straight in. Partial deliveries are very welcome. Already delivered (thank you!): all 62 original characters, the 4 monster sheets, all 60 portraits, the spell effects, the world textures, skies and fire, and most of the icons.

**Delivery**: a zip with one folder per section (`characters/`, `spell_icons/`, `item_icons/`, `revisions/` ...), files named exactly as listed. **Style**: the same painted pixel-art style as the earlier characters and icons; PNG; sizes exact.

**Suggested order**: characters first (they're seen most), then the spell icon, then item icons.


## How character sheets work

**Sheet layout (all characters):** one PNG per character, **8 columns × 6 rows**, every cell the same size (128–256 px square; earlier sheets used 192 px cells), on a flat **pure black** background.
- **Columns = facing**: 0 front, 1 front three-quarter (body towards screen-left), 2 profile facing screen-left, 3 back three-quarter, 4 back, 5 back three-quarter (other side), 6 profile facing screen-right, 7 front three-quarter (towards screen-right).
- **Rows**: 0 idle, 1 walk A (left leg forward), 2 walk B (right leg forward), 3 wind-up (weapon raised, or a hand to the head for talkers), 4 attack / gesture, 5 columns 0–3 hit-recoil (front, left profile, back, right profile) and columns 4–7 lying on the ground (side-on, inside the cell).
- Same scale and the same ground line (feet about 92 % down the cell) in every frame; nothing crosses into a neighbouring cell; one character per sheet, same outfit and props in every frame; about a 3/4 top-down view, lit from the upper left. Glowing bits (eyes, orbs) look great: the game adds bloom.


## Chapter One: the people of Here (and the Auditor) — 11 sprite sheets

A city struck off every map 400 years ago; its people have forgotten their own names and go by descriptions. The residents are slightly faded, like a memory (soft, pale edges are fine: the game keeps them a little see-through itself). Deliver in `characters/`.

| File | Who | Look |
|---|---|---|
| `here_gatekeeper.png` | Ottoline Pell, Gatekeeper | A very upright woman in a faded blue customs uniform and cap, a big rubber stamp in one hand and a form in the other. Four hundred years of patience; tearfully delighted to finally have a visitor. |
| `here_baker.png` | The Baker, Probably | A floury baker in a white apron and a hair bun, flour on their face and arms, forever kneading dough that isn't there. |
| `here_butt_butt.png` | Butt-Butt | A small, loud child (about 1.15 m) with messy ginger hair, a stub of chalk, chalk dust everywhere, an orange jumper, enormous grin. Picked their own name: Butt-Butt. Toasty's character! |
| `here_cartographer.png` | The Cartographer (Retired) | An elderly mapmaker with white hair and beard, a much-mended brown coat, a battered hat, maps rolled under one arm. |
| `here_person_in_hat.png` | Person in a Hat | Someone in a VERY tall, slightly bent hat (the most important part), a purple coat, dignified and vague. |
| `here_night_merchant.png` | The Night Merchant | A tall, thin, hooded figure in deep night-blue, glowing pale eyes, a staff hung with little lanterns of different colours. |
| `here_inspector.png` | Inspector Aldric Thrupp (ghost) | A grey, upright ghost tax inspector in a tall collar and a battered hat, a tin badge, holding a ledger full of holes; faint and see-through, counting chimneys on his fingers. |
| `here_echo.png` | The Last Archivist | A ghostly archivist made of almost nothing: robes, spectacles, ink-stained fingers, an open ledger; floats slightly, faintly glowing. |
| `auditor.png` | Prudence Vell, Senior Auditor of Existence (the Audit) | A severe Bureau official in a black coat with silver buttons, hair in a tight bun, a pen behind each ear and one in her hand, a red ledger. Not unkind; extremely thorough. |
| `here_mouth.png` | Mouth of the Hunger (monster) | A floating mouth with no face: a dark, papery shape like a torn page, a ring of teeth, faint pale glow. Hunts by hearing names. |
| `here_unsaying.png` | The Unsaying (boss) | Big (about 2.8 m), made of the gaps between words: a tall dark silhouette full of torn paper, crossed-out letters drifting off it, a pale glowing hollow where a face would be. |

## Friends from Toasty's streams — 3 sprite sheets

Real friends of Toasty's, as characters (two can join the party). Deliver in `characters/`.

| File | Who | Look |
|---|---|---|
| `friend_eranu.png` | Eranu, Shieldmaiden of the Glens | A tall, broad-shouldered Scottish warrior woman: long blonde braid, green tartan kilt, blue-grey tunic, round wooden targe (shield) and a sword. Brave and clever; confident, a little amused. She. |
| `friend_coth.png` | Coth (Cothfotmeoo) | Looks like a castaway lost for a thousand years: skinny, scruffy, long dark hair down his back, a long heavy black beard to his belt, a ragged tunic, and NO TROUSERS (bare legs, bare feet; plain undershorts). Carries a sword. Cheerful, slightly unhinged. He. |
| `friend_dunstan.png` | Dunstan, Nearly a Squire | A keen young warrior in polished mail and a red cloak, short brown hair, with an absurdly huge sword (taller than he is, broad as a door) that he drags point-down because he can barely lift it. A round mate gourd with a silver straw (bombilla) hangs at his hip: he's from Uruguay. Sunny, eager, a bit homesick. He. |

## Spell icons — 1 icon

Shown in the spell bar and spellbook. **64 × 64 px**, opaque square (dark background), a clear symbol of the spell, readable at 32 px, a coloured border per school (fire orange, frost blue, restoration green, arcane violet...), matching the delivered ones.

| File | Spell | What it does |
|---|---|---|
| `unsay.png` | Unsay | The Archivists' last trick: say something so quietly it un-happens. The target forgets it ever saw you, and can't see you again for eight seconds (less for the very large). For walking past things that shouldn't notice you. |

## Item icons — 63 icons

Shown in the inventory, shop and loot windows. **64 × 64 px**, transparent background, the object on its own, slightly angled, readable at 32 px, matching the delivered ones. Grouped by kind; the description is what the game says about it.


### Weapon (1)

| File | Item | Description |
|---|---|---|
| `red_pen.png` | The Red Pen | An Archivist's editing pen, long enough to use as a dagger, still wet with red ink after four hundred years. It strikes things out: a hit can make a foe forget what it was doing. |

### Armor (1)

| File | Item | Description |
|---|---|---|
| `trousers_of_coth.png` | The Trousers of Coth | Sturdy, warm, beautifully stitched, and never once worn by their owner, who refuses to take them back. Eranu carried them for three days, just in case. Comfortable in winter, which is more than Coth can say. |

### Accessory (5)

| File | Item | Description |
|---|---|---|
| `butt_butt_chalk.png` | Butt-Butt's Lucky Chalk | A stub of chalk worn to a nub from writing BUTT-BUTT WOZ ERE on every wall in town. 'It's best at night. Everything is.' At night, you strike truer and luckier. |
| `certificate_of_existence.png` | Certificate of Existence (Audited) | Signed by Senior Auditor Vell, stamped nine times, and laminated in something that isn't quite wax. It certifies that the bearer exists, thoroughly. Being officially real is good for you: tougher, more convincing, and sl… |
| `here_silver_bell.png` | Silver Bell of Here | A small silver bell from the tower of Here, given by the whole town. When it rings, things that eat names flinch. Your spells hit harder; you see further into the dark. |
| `inspector_abacus.png` | The Inspector's Abacus | Aldric Thrupp's ghostly abacus, cold as a coin. Its beads slide on their own when there's money nearby, and click disapprovingly at locks. More gold finds you, and locks give a little. |
| `moonlit_cloak.png` | Moonlit Cloak | From the Midnight Market: a cloak that's slightly more there at night. You move quicker after dark, and gold finds its way to you. |

### Consumable (3)

| File | Item | Description |
|---|---|---|
| `ash_pepper_stew.png` | Ash-Pepper Stew | Hot enough to make your eyes water and your aim improve. Nobody understands why. +8% critical chance for 5 minutes. |
| `dunstan_mate.png` | Mate (Dunstan's) | Dried yerba from the Eastern Shore, a gift from Dunstan. Hot, grassy, bitter, and then somehow good. Restores a little health, and for 5 minutes your stamina comes back much faster. Best shared. Don't stir the bombilla. |
| `here_bread.png` | Bread of Here | Warm, dark, a little sour, a little sweet. It smells like knowing where you are. Steadies the mind. |

### Book (7)

| File | Item | Description |
|---|---|---|
| `here_quiet_name.png` | The Quiet Name | A sliver of the plinth's stone with a single word written on it in your own hand. Whoever reads it remembers where they are, and who. |
| `tome_glimmer.png` | Tome: Glimmer | Use from inventory to permanently learn the Glimmer spell. |
| `tome_siphon.png` | Tome: Siphon Ink | Use from inventory to permanently learn Siphon Ink. The pages are blotted with something that isn't quite ink. |
| `tome_veil.png` | Tome: Veil | Use from inventory to permanently learn the Veil spell. |
| `tome_vitality.png` | Tome: Borrowed Vitality | Reading it teaches the spell (and the tome crumbles). |
| `tome_ward.png` | Tome: Ward | Use from inventory to permanently learn the Ward spell. |
| `uncounted_ledger.png` | The Uncounted Ledger | A heavy stone-vellum register in which the Archivists of Annex III recorded every name they hid. Its last pages describe things that have not happened yet. |

### Key (9)

| File | Item | Description |
|---|---|---|
| `annex_key.png` | Brass Registry Annex Key | Stamped 'ANNEX III - DO NOT ENTER WITHOUT FORM 27-B'. Form 27-B is kept inside. Nobody at the Bureau sees the problem. |
| `cellar_key.png` | Gale & Sons Cellar Key | Heavy iron, crusted with salt. It's always slightly damp, no matter how long you keep it in your pocket. |
| `crypt_key.png` | Cold-Iron Sanctum Key | Given by the Uncounted Witness. Cold enough to ache. Opens the Sanctum of the Uncounted, where Chief Archivist Morvath keeps the Ledger. |
| `here_archive_key.png` | Key to the Archive of Here | Heavy, iron, and warm from four hundred years in Ottoline's drawer. |
| `here_permit.png` | Visitor's Permit (Here) | The bottom of Form One, stamped APPROVED in four-hundred-year-old ink. Purpose of visit: see attached. |
| `hollowmere_key.png` | Key to Hollowmere Manor | A heavy iron key with a bow shaped like a wine glass. Hollis says it was 'acquired'. Hollis does not elaborate. |
| `lockpick.png` | Tempered Lockpick | Used to bypass mechanical locks when you lack the matching key. |
| `quillsby_vault_key.png` | Quillsby's Vault Key | A tiny gold key on a velvet ribbon, engraved 'MINE'. |
| `study_key.png` | Study Key | Found in a drawer clearly labelled 'STUDY KEY - DO NOT LOOK HERE'. Security at Hollowmere was a matter of trust. |

### Misc (37)

| File | Item | Description |
|---|---|---|
| `ash_pepper.png` | Ash-Pepper | A glowing red gland from an Ash Crawler. Hot to the touch. Sabrino calls it 'the only good thing about those horrible little ovens with legs'. |
| `ashwood_branch.png` | Ashwood Branch | Straight, pale and springy. Arrows, handles, walking sticks for people who refuse to admit they need one. (Crafting material.) |
| `bladderwrack.png` | Bladderwrack | Saltmere seaweed, rubbery and cold. Holds a chill like nothing else. (Crafting material.) |
| `bonnet_thread.png` | Grandmother's Bonnet Thread | A spool of lace from the bonnet of the wolf in grandmother's nightgown. Unreasonably strong. Smells of biscuits. A crafting reagent. |
| `dragon_costume.png` | Dragon Costume | Leather scales, oilcloth wings, real glass eyes. Ordered nine years ago by a monster hunter 'for a contract'. It watches you. |
| `dragon_likeness.png` | Likeness of Cindermaw | A silver plate: the dragon in Bellwether's square, reading spectacles on one claw, mid-sneeze. Accurate. Tell no one. |
| `dreaming_ink.png` | Dreaming Ink Sac | From the Dreaming Limb: a sac of ink that shows you somebody else's dream if you stare too long. A crafting reagent. |
| `fireworks.png` | Sabrino's Fireworks | Gold, green, purple, and one labelled THE GOOSE. Do not ask about The Goose. |
| `fish_idol.png` | Warm Fish Idol | A small stone fish with too many eyes, carved with script that hurts to look at. It is warm. It is always warm. Professor Pickering would want to see it, and then want you to take it away again. |
| `fishing_rod.png` | Fishing Rod | Ashwood, gut line, a hook Silas swears by. Stand by water and cast. Press interact the moment something bites. |
| `glimmering_pearl.png` | Glimmering Pearl | A pearl that glows faintly green from the inside. Worth a fortune to the right merchant. It hums when you hold it. |
| `glowcap.png` | Glowcap | A mushroom that glows faintly blue. Tastes of static. The base of most mana-work. (Crafting material.) |
| `grave_moss.png` | Grave Moss | Soft, dark moss that only grows on graves. Calms the mind. Nobody asks why. (Crafting material.) |
| `grave_truffle.png` | Grave-cap Truffle | A knobbly black truffle that grows only where it's very quiet for a very long time. Sabrino would know what to do with it. |
| `grumpy_frog.png` | A Grumpy Frog | It is grumpy. It will not be kissed. It has been asked. |
| `hatching_record.png` | Register of Hatchings, Vol. IX | Entry 4,211: one egg, red, enormous. Hatched. Very loud. Named Cindermaw. No date of death. Fenwick wants it BACK. |
| `here_map.png` | The Cartographer's Map | Every street of Here, measured and checked twice. From above, the streets make one great curling letter. There's a blank space at the top for the name. |
| `here_recipe.png` | Recipe Card (Bread of Here) | Flour, salt, a pinch of something dark. A long slow knead, a fold, a fold. In the corner, a smudge of four-hundred-year-old flour. |
| `hoard_third.png` | The Missing Third | Four thousand gold in heavy sacks stamped 'INVESTMENTS'. It belongs to a dragon. Take it back to Bellwether. |
| `host_ember.png` | Ember of the Wrathful Host | A coal from Sir Percival's fury, still warm and still faintly offended. A crafting reagent. |
| `ink_heart.png` | Archivist's Ink Heart | What was left of Archivist Morvath: a fist-sized knot of black ink that beats, slowly, in time with nothing. A crafting reagent. |
| `iron_scrap.png` | Iron Ore | A lump of rusty iron ore. Arrowheads, lockpicks, whetstones. (Crafting material.) |
| `likeness_box.png` | Pickering Patent Likeness Engine | A wooden box on legs with a brass lens and a black cloth. Point it at a dragon, shout 'hold still', pull the lever. Has only exploded twice. |
| `marigold.png` | Marigold | Bright orange petals. Brother Aldous grows them for the shrine and pretends not to notice them going missing. Healing. (Crafting material.) |
| `name_eater_tooth.png` | Tooth of the Name-Eater | A tooth from the Avatar of the Name-Eater. Hold it and, for a moment, you can't remember your own name. A crafting reagent. |
| `oak_acorn.png` | Acorn of the Old Oak | A fat, glossy acorn from the Old Oak. You feel a strange urge to bury it. Don't. |
| `old_boot.png` | An Old Boot | Waterlogged. There's a smaller boot inside it. Inside that, a crab, who is not pleased. |
| `paper_crown.png` | Paper Crown | Folded from the dust jacket of a romance novel. Chapter Nine is printed on the inside. Wear it facing forward. |
| `pine_resin.png` | Pine Resin | Sticky amber resin from old stumps. Burns hot and slow. Smells like a whole forest at once. (Crafting material.) |
| `rat_whisker.png` | Rat King's Whisker | A single whisker from the Rat King, long as a rapier and twice as sharp. It still twitches when you mention cheese. A crafting reagent. |
| `rolf_fur.png` | Tuft of Rolf's Fur | Soft, warm, and from the back (the front is for show). Smells faintly of marrows. |
| `sea_salt.png` | Sea Salt | Crusted on the quay stones by the tide. Preserves, purifies, and keeps very old things asleep. (Crafting material.) |
| `thunder_sheet.png` | Thunder Sheet (Confiscated) | A great sheet of tin. Shake firmly for weather. Comes with a receipt. |
| `vallo_red.png` | Bottle of Vallo Red | A dusty bottle of good red wine from the hills of Vallo. Vaelen swears it's the last one. Vaelen swears that about every bottle. |
| `warden_bell.png` | The Warden's Silver Bell | The little bell the Lullaby Warden rang for lights-out. Ring it and you feel sleepy. Don't ring it. A crafting reagent. |
| `wayside_sage.png` | Wayside Sage | Grey-green, peppery, grows along every road in the Marches. Good for stamina, better for soup. (Crafting material.) |
| `wolfsbane.png` | Wolfsbane | Purple hooded flowers from the Whistling Wood. Rolf asks that you not wave it near him. Makes wounds that won't close. (Crafting material.) |

## Revisions

| File | What to change |
|---|---|
| `item_icons/ransom_note.png` | Currently a bound notebook. Should be a loose sheet of paper with charcoal scribbles (a crossed-out ransom note) and a faint grid showing through from the back. |

## Small extras (optional, whenever)

| File | What | Notes |
|---|---|---|
| `item_icons/gold_coins.png` | The gold icon (inventory, loot, shops) | 64 × 64, a small pile of coins, transparent background. |
| `sprites/vfx/torch_flame.png` | The small flame on wall torches | Like the fireplace fire, but small and narrow: one row of square frames, 32 or 64 px, hard edges, flame touching the bottom. |

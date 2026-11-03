# Art brief for Noor: everything that still needs painting

Thank you for all the characters, textures and skies! This is the rest of the game's art, in order of how much it shows during play. Everything is placeholder art right now, so any part you deliver goes straight in.

**Delivery**: a zip with one folder per section (`portraits/`, `monsters/`, `spell_effects/`, `spell_icons/`, `item_icons/`, `characters/` for Chapter One's people, `skies/`), files named exactly as listed. Partial deliveries are welcome.

**Everywhere**: the same painted pixel-art style as the character sheets; PNG; sizes exact.


## 1. Character portraits (character creation) — 60 portraits

Toasty picks one when creating the character (it's cosmetic; the character is never seen in the game, only here and on the character sheet). **Two per race per calling**, ideally one woman and one man, with varied ages and looks within each race, so there's lots to choose from.

- **Size**: 128 × 128 px, square, opaque (a dark painted background is fine, no transparency needed).
- **Framing**: head and shoulders, facing the viewer or slightly turned, like an RPG party portrait. Shown at about 96 px, so keep faces bold and readable.
- **The calling shows** in clothing and gear: armour and a sword hilt for a warrior, a hood and bow for a ranger, robes and a glowing hand or staff for a mage, leathers and a dagger for a rogue, vestments and a holy symbol for a cleric, practical mixed travelling gear for an adventurer.
- **The world**: Edrath, a gloomy, slightly absurd fantasy of bureaucrats and the 'officially dead'. Muted colours, candlelight, a bit of humour in the faces is welcome.
- **Names**: `<race>_<calling>_<1 or 2>.png`, e.g. `human_warrior_1.png`, `orc_mage_2.png`.

| Race | What they're like |
|---|---|
| `human` — Human | Adaptable citizens of Edrath's fractured kingdoms. |
| `dwarf` — Dwarf | Deep-vault chroniclers and stone-wrights who remember older ledgers. |
| `elf` — Elf | Long-lived observers sensitive to thin places left by the Great Silence. |
| `orc` — Orc | Stalwart march-wardens and Ashbound pathfinders. |
| `halfling` — Halfling | Nimble burrow-folk who slip past bureaucracy and locked doors alike. |

Callings: `warrior` (Warrior), `ranger` (Ranger), `mage` (Mage), `rogue` (Rogue), `cleric` (Cleric), `adventurer` (Adventurer).

That's 5 races × 6 callings × 2 = 60 files, from `human_warrior_1.png` to `halfling_adventurer_2.png`. More than two of a kind (`_3`, `_4`...) also work, and fewer is fine: whatever exists shows up.


## 2. Four monsters that need their own sprite sheets

Right now all four share one plain 3D model. Same 8 × 6 sheet layout and rules as all the other characters (see `docs/CHARACTER_SPRITES.md`: 8 directions × idle, walk A, walk B, windup, attack, stagger/corpse).

| File | Who | Look |
|---|---|---|
| `lost_sentinel.png` | Lost Sentinel | Ancient Bureau guardian of stone and rusted iron, tall and heavy, a halberd or great seal-hammer, a faded official crest on its chest. Slow, patient, still guarding a door nobody remembers. |
| `animated_armor.png` | Animated Armour | An empty, polished suit of manor armour (Hollowmere), nothing inside — you can see darkness through the visor slits. Carries a guest list on a clipboard and a sword. Prim and officious. |
| `headless_knight.png` | The Headless Knight of the Old Road | Comedy: it's obviously Steve (the level-one bandit from your Steve sheet) in ill-fitting, mismatched armour, the helmet pulled down over his head, holding a hat on a stick above it to look 'headless'; his patched leathers and too-big hood poke out. Proudly dramatic poses. |
| `repossession_golem.png` | The Repossession Golem | A big, blocky iron golem stamped REPOSSESSED all over in red, riveted plates, glowing furnace eyes, bought with a dragon's money. Bigger than a person (about 2.3 m). |

## 2b. Chapter One: the people of Here — 9 sprite sheets

A city struck off every map 400 years ago; its people have forgotten their own names and go by descriptions. Same 8 × 6 layout as the other characters. The residents are slightly faded, like a memory (soft, pale edges are fine: the game keeps them a little see-through itself). Simple placeholders are in the game until yours arrive.

| File | Who | Look |
|---|---|---|
| `here_gatekeeper.png` | Ottoline Pell, Gatekeeper | A very upright woman in a faded blue customs uniform and cap, a big rubber stamp in one hand and a form in the other. Four hundred years of patience; tearfully delighted to finally have a visitor. |
| `here_baker.png` | The Baker, Probably | A floury baker in a white apron and a hair bun, flour on their face and arms, forever kneading dough that isn't there. |
| `here_butt_butt.png` | Butt-Butt | A small, loud child (about 1.15 m) with messy ginger hair, a stub of chalk, chalk dust everywhere, an orange jumper, enormous grin. Picked their own name: Butt-Butt. Toasty's character! |
| `here_cartographer.png` | The Cartographer (Retired) | An elderly mapmaker with white hair and beard, a much-mended brown coat, a battered hat, maps rolled under one arm. |
| `here_person_in_hat.png` | Person in a Hat | Someone in a VERY tall, slightly bent hat (the most important part), a purple coat, dignified and vague. |
| `here_night_merchant.png` | The Night Merchant | A tall, thin, hooded figure in deep night-blue, glowing pale eyes, a staff hung with little lanterns of different colours. |
| `here_echo.png` | The Last Archivist | A ghostly archivist made of almost nothing: robes, spectacles, ink-stained fingers, an open ledger; floats slightly, faintly glowing. |
| `here_mouth.png` | Mouth of the Hunger (monster) | A floating mouth with no face: a dark, papery shape like a torn page, a ring of teeth, faint pale glow. Hunts by hearing names. |
| `here_unsaying.png` | The Unsaying (boss) | Big (about 2.8 m), made of the gaps between words: a tall dark silhouette full of torn paper, crossed-out letters drifting off it, a pale glowing hollow where a face would be. |

## 3. Spell effects in flight — 5 animated strips

The ball you see flying when a spell is cast. Currently plain coloured circles.

- **Layout**: one row of **square frames**, 4 to 8 frames, **64 × 64 px** each (e.g. 6 frames = 384 × 64). Loops at 14 frames per second; it's shown about half a metre across.
- **Hard edges only**: pixels fully opaque or fully transparent (the game drops anything under 50 % opacity). Do glow with colour, not transparency. Drawn at full brightness, centred in the frame, always facing the camera.

| File | Used by | Look |
|---|---|---|
| `spell_arcane.png` | Bewilder, Sudden Friendship, Unsay | a pulsing violet orb with orbiting runes |
| `spell_ember.png` | Ember Bolt, Slow Burn | a tumbling ball of flame with sparks |
| `spell_frost.png` | Frost Lance | a spinning shard of ice with frosty mist |
| `spell_ink.png` | Siphon Ink, [REDACTED] | a splattering glob of black ink with drips |
| `spell_sabrino.png` | Sabrino's Questionable Fireball | Sabrino the witch's signature hex: a green-purple swirl with a tiny grinning face |

## 4. Spell icons — 23 icons

Shown in the spell bar and spellbook, all the time. **64 × 64 px**, opaque square (dark background), a clear symbol of the spell, readable at 32 px. A coloured border per school is welcome (fire orange, frost blue, restoration green, arcane violet...).

| File | Spell | What it does |
|---|---|---|
| `barkskin.png` | Barkskin | Bramble Thistlewick's thanks: your skin turns to oak bark for 40 seconds (+8 armour). Blades skid off. Hay fever not included. |
| `bewilder.png` | Bewilder | The target forgets which way is up, who it was fighting, and what a 'you' is. It wanders about and swings at whatever's nearest, friend or foe. |
| `borrowed_vitality.png` | Borrowed Vitality | For twenty-five seconds, every blow you land gives a little of their life to you. Lord Ashgrave says it's 'not like that'. It's exactly like that. |
| `chain_of_command.png` | Chain of Command | Lightning passed down the line: it hits the nearest foe in front of you, then jumps to three more, each jump a little weaker. Shocked foes take 25% more damage from everything. Shock something that's on fire and it OVERLOADS. |
| `clerical_error.png` | Clerical Error | The universe briefly misfiles your position. You are six metres further forward than you were. (Never through walls: even the universe has rules.) |
| `cold_shoulder.png` | Cold Shoulder | A ring of brittle, disapproving frost bursts out from you. Everyone nearby is chilled (slowed). Chill anything three times and it freezes solid. Set fire to something frozen and it SHATTERS. |
| `dragon_sigh.png` | Dragon's Sigh | Cindermaw's gift: sigh, and a ring of dragonfire rolls out around you, burning everything within five metres. 'WHEN THEY CROWD YOU: SIGH AT THEM.' |
| `ember_bolt.png` | Ember Bolt | Launches a searing bolt of condensed fire that illuminates dark halls. |
| `frost_lance.png` | Frost Lance | A fast shard of ice. Hits harder than Ember Bolt and flies straighter, but costs more mana. |
| `glimmer.png` | Glimmer | Conjures a warm floating orb of lantern-light around the caster. |
| `late_for_appointment.png` | Late for an Appointment | The universal panic of being late, bottled. You move 35% faster for eighteen seconds. Your heart rate does too. |
| `mend.png` | Mend | Knits wounds and restores flagging stamina. |
| `paper_storm.png` | Paper Storm | A whirlwind of razor-edged Bureau forms bursts out around you. Everything nearby takes a thousand paper cuts and bleeds. Bleeding stacks up to three times. |
| `redacted.png` | [REDACTED] | A bar of perfect black blots out a target's eyes. Inked foes can barely see, lose track of you, and miss almost half their attacks. [The remainder of this description has been redacted.] |
| `sabrino_fireball.png` | Sabrino's Questionable Fireball | A slow, heavy fireball that bursts on impact, scorching every enemy within 3.5 m. Expensive, glorious, and legally a war crime. |
| `siphon_ink.png` | Siphon Ink | A slow bolt of black ink that returns 60% of the damage it deals to you as health. Governed by Restoration. |
| `slow_burn.png` | Slow Burn | A small, patient flame. Barely stings on impact, then burns for six seconds. Mother Brine used it to keep the chowder warm for eleven years. |
| `standing_ovation.png` | Standing Ovation | Thunderous applause from nowhere. Everything near you is staggered and shocked. Odette says it's the only spell that has ever made a critic leave early. |
| `sudden_friendship.png` | Sudden Friendship | For fourteen seconds, the target thinks you are the best person it has ever met, and fights anything that disagrees. Hitting your new friend ends the friendship. Bosses have trust issues. |
| `unauthorised_entry.png` | Unauthorised Entry | The lock you are looking at is persuaded that it was never locked in the first place. Works on locks up to a difficulty that grows with your Illusion. Leaves no lockpicks broken and no paperwork filed. |
| `unsay.png` | Unsay | The Archivists' last trick: say something so quietly it un-happens. The target forgets it ever saw you, and can't see you again for eight seconds (less for the very large). For walking past things that shouldn't notice you. |
| `veil.png` | Veil | Dulls sound and bends shadow, reducing enemy sight detection. |
| `ward.png` | Ward | Sheathes the caster in a resonant arcane barrier (+8 Armor). |

## 5. Item icons — 186 icons (a big set: any part helps)

Shown in the inventory, shop and loot windows. **64 × 64 px**, transparent background, the object on its own, slightly angled, readable at 32 px. Grouped by kind below; the description is what the game says about it.


### Weapon (22)

| File | Item | Description |
|---|---|---|
| `baggy_umbrella.png` | Baggy's Trusty Umbrella | A furled black umbrella with a hooked cane handle. Baggy carried it for seventeen years in Bellwether's rain and never once opened it, "for dramatic reasons". Quick, well balanced, and the brass ferrule picks a lock if y… |
| `cinderglass_dagger.png` | Cinderglass Dagger | Volcanic glass, still warm. Sets things on fire, and keeps them that way. Pairs dangerously well with anything that chills. |
| `hostbrand.png` | Hostbrand | A longsword quenched in the Wrathful Host's ember. It's always slightly warmer than the room, and sets enemies alight when it's in the mood. |
| `hunting_bow.png` | Yew Hunting Bow | A dependable recurve bow used by woodsmen along the Old Road. |
| `inconvenient_sword.png` | The Sword of Mild Inconvenience | Enchanted by a wizard with a grudge and a short attention span. Sometimes the person it hits forgets what they were doing. Sometimes so do you. (Only them, actually. Probably.) |
| `iron_longsword.png` | Bellwether Iron Longsword | Standard watchman's steel forged in the northern hills. |
| `iron_mace.png` | Flanged Iron Mace | Designed to dent ancient armor and shatter brittle ribs. |
| `ladle_of_justice.png` | The Ladle of Justice | Sabrino's own copper ladle, warm from a hundred kitchens. It has stirred risottos, settled arguments and once, memorably, a ghost. Restores mana on every hit and is unkind to spirits. |
| `letter_opener.png` | Morvath's Letter-Opener | The Chief Archivist's silver letter-opener. Slits envelopes, wax seals and, it is rumoured, one auditor. Tiny, fast and vicious: built for critical hits. |
| `oak_staff.png` | Collegium Focus Staff | Shod with iron and tipped with a resonant pale-blue Silence shard. |
| `red_pen.png` | The Red Pen | An Archivist's editing pen, long enough to use as a dagger, still wet with red ink after four hundred years. It strikes things out: a hit can make a foe forget what it was doing. |
| `rimecaller_mace.png` | Rimecaller Mace | A mace with a head of blue ice that never melts. Every few hits, the target slows. Three chills and it's a statue. |
| `rusted_sword.png` | Rusted Broadsword | Pitted with rain, yet balanced enough to split bone. |
| `saltmere_harpoon.png` | The Old Master's Harpoon | Black iron, barbed, wrapped in old whaleskin. Made by Hollis's master for a thing in the deep he never got to fight. Long reach, and terrible to anything eldritch. |
| `serrated_cleaver.png` | Serrated Cleaver | A butcher's cleaver with a saw-tooth back, 'confiscated' from the Hollowmere kitchens. Opens wounds that keep on giving. Bleeding stacks three times. |
| `silver_sword.png` | Silver Sword of the Grey | One of Hollis's two swords. The silver one is for monsters; the steel one is for people. Hollis is unclear which one is for rats. Deals heavy extra damage to spirits. |
| `steel_dagger.png` | Surveyor's Dirk | A fast, narrow blade favored for close quarters and quiet work. |
| `steve_spoon.png` | Steve's Spoon | Tin. Bent. Nineteen years of brandishing. Hilariously weak, until it isn't: 30% critical chance, triple critical damage, and +50% against beasts. Night school taught Steve one thing: aim for the eyes. |
| `ten_foot_pole.png` | The Ten-Foot Pole (Mended) | The very pole that died testing the dungeon floor in Campaign One, mended by Chester. Hits weakly, from a very long way away. Note attached: 'DO NOT TEST FLOORS WITH IT AGAIN.' |
| `thornbow.png` | Thornbow | A bow grown, not carved, from a thornbush in the Whistling Wood. The arrows come out barbed. Things it hits bleed. |
| `whiskerblade.png` | Whiskerblade | A dagger made around the Rat King's whisker. Quick, mean, and it makes things bleed. Rats nearby go very quiet when you draw it. |
| `widowmaker.png` | The Widowmaker | Forged for King Edric's final battle. Unfortunately, Edric survived. His wife did not appreciate the name. |

### Armor (13)

| File | Item | Description |
|---|---|---|
| `chain_hauberk.png` | Riveted Chain Hauberk | Heavy interlocking iron rings offering reliable protection. |
| `dented_bucket.png` | Dented Bucket | A tin bucket with a dent in it. Worn on the head, it makes you look ridiculous (-1 Presence) and makes shopkeepers strangely unable to keep track of their stock (+10% shop discount). Nobody knows why this works. It just … |
| `gm_screen.png` | The Game Master's Screen | A folding screen painted with dragons and tax tables. Surprisingly good at stopping arrows. Held up, it makes you feel like you know something everyone else doesn't. |
| `iron_helm.png` | Watchman's Kettle Helm | Deflects overhead blows and dripping cavern stalactites. |
| `iron_shield.png` | Ironbanded Heater Shield | Sturdy oak reinforced with forged iron straps. |
| `keeper_lantern.png` | The Keeper's Lantern | Ondine Marsh's lantern on its pole, lit at last. Carried in the off hand. +1 Will, +8% spell power, steady sanity recovery. Things in the dark find it soothing, which is not the same as friendly. |
| `leather_jerkin.png` | Boiled Leather Jerkin | Supple road armor that won't slow your stride. |
| `party_hat.png` | Percival's Party Hat | A pointed paper hat in four colours, made for a party nobody came to. Wearing it makes you feel, briefly, like the guest of honour. +3 Presence, slowly mends you. |
| `rat_crown.png` | Crown of the Rat King | A tiny golden crown, sized for a very large rat. It fits you if you push. +2 Agility, +4% critical chance, -1 Presence because people can tell where it's been. |
| `red_hood.png` | The Red Hood | Grandmother's granddaughter gave up on it and took up archery. She's very good. +1 Agility, +30% ranged critical damage. Wolves look at you funny. |
| `sabrino_hat.png` | Sabrino's Pointed Hat | Tall, dented and gloriously purple, with a sash that smells of garlic and brimstone. Makes your spells hit harder and your opinions louder. Mildly cursed: you can't stop thinking about dinner. |
| `scholar_robe.png` | Collegium Archivist Robe | Woven with silver thread that steadies the mind during casting. |
| `traveler_boots.png` | Wayfarer's Dry-Stitched Boots | Waxed against Bellwether's unending drizzle. |

### Accessory (25)

| File | Item | Description |
|---|---|---|
| `bone_spectacles.png` | Bone Clerk's Spectacles | Wire-rimmed reading glasses, still perched on the nose of a clerk who had no nose. Everything looks slightly more like a typo. +1 Intellect, +5% critical chance, +5% lockpick chance. |
| `butt_butt_chalk.png` | Butt-Butt's Lucky Chalk | A stub of chalk worn to a nub from writing BUTT-BUTT WOZ ERE on every wall in town. 'It's best at night. Everything is.' At night, you strike truer and luckier. |
| `cape_brooding.png` | Cape of Eternal Brooding | Black velvet, blood-red lining, and a high collar to stare moodily out of. Sparkles faintly in sunlight, which ruins the effect. +2 Presence, 3% life steal. |
| `cindermaw_scale.png` | Cindermaw's Scale | Pulled from the dragon's own chest, with a wince. Warm to the touch, always. Fire burns hotter for you, fire hurts you less, and your spells hit harder. |
| `fang_unwritten.png` | Fang of the Unwritten | The Name-Eater's tooth on a cord. It takes a little of every enemy you hit and gives it to you. It would like your name too. It can't have it. |
| `gang_scarf.png` | Figure It Out Gang Scarf | Long, orange, with a little embroidered question mark. Full membership of the Figure It Out Gang. +5% critical chance, +5% speed, steadier nerves, +1 to dice rolls. You will be chased by something at least once a week. |
| `granny_mittens.png` | Grandmother's Fighting Mittens | Knitted from bonnet thread, impossibly tough. Blocking in them is like being hugged by a very stern grandmother. You carry more, too: deep pockets. |
| `here_silver_bell.png` | Silver Bell of Here | A small silver bell from the tower of Here, given by the whole town. When it rings, things that eat names flinch. Your spells hit harder; you see further into the dark. |
| `hollowmere_signet.png` | Hollowmere Signet | Sir Percival's own ring, given freely at the end of a very good party. It feels warm, like a hand on your shoulder. +2 Presence, +1 Will, slowly mends you. |
| `ink_heart_quill.png` | Ink-Heart Quill | A quill whose nib dips itself in the Archivist's ink heart. Spells written with it cost less and stick harder. |
| `library_card.png` | Fenwick's Library Card (Lifetime, Laminated) | Card number 0000001. There has never been a card 0000001 before. +1 Intellect, status effects last 30% longer, spells cost 6% less. All fines waived. All of them. Forever. |
| `lich_quill.png` | The Archchancellor's Quill | A slim black quill with a silver nib, carved by Oakhaven for the Lich who finally put his down. +2 Intellect, +8% spell power, +1 to dice rolls in conversation. |
| `lucky_d20.png` | Oakhaven's Lucky d20 | A twenty-sided die worn smooth by years of Thursdays. It always rolled well for people who deserved it. +2 to every dice roll in conversation, +2% critical chance. |
| `mask_uncounted.png` | Mask of the Uncounted King | The gilded half-mask you wore on opening night. Odette insisted you keep it. When you wear it, people turn to look at you, and for once you don't mind. +3 Presence, +5% spell power, +3% critical chance. |
| `mimic_satchel.png` | Chester's Cousin (Satchel) | A leather satchel with brass corners and a very small row of teeth along the flap. +30 carry weight, find 15% more gold. Only bites people who try to steal from you. |
| `moonlit_cloak.png` | Moonlit Cloak | From the Midnight Market: a cloak that's slightly more there at night. You move quicker after dark, and gold finds its way to you. |
| `quillsby_cufflinks.png` | Quillsby's Gloating Cufflinks | Two tiny gold cufflinks shaped like dragons, worn to 'gloat, formal'. Lucky with money: +25% gold found, 10% off at every shop. |
| `ring_of_recall.png` | Ring of Unwritten Recall | Warm to the touch. You remember wearing it tomorrow. |
| `seal_quill.png` | Archivist's Seal-Quill | A raven quill with a nib of black iron, still wet with ink that never dries. It wrote the Seal of Names. Worn at the belt, it steadies the mind. +2 Will, +2 Intellect. |
| `signet_ring.png` | Tarnished House Signet | Bears the crest of a manor that no longer appears on royal tax rolls. |
| `snacks_feather.png` | Doobie's Brave Feather | A single brown feather from the bravest owlbear cub on the Old Road (it charged once; it counts). +2 armour, heals 3 when you block, steadier nerves, +15% critical damage. |
| `squirrel_tail.png` | Bramble's Spare Squirrel Tail | Left over from the Rite of Unbecoming. Probably lucky. Worn on a belt, it makes you quicker on your feet and you recover your breath faster. You keep wanting to bury things. |
| `storm_stamp.png` | The Storm-Clerk's Stamp | A brass Bureau stamp that reads APPROVED in lightning. Shatters and Overloads hit 35% harder, and status effects land a little more often. |
| `tide_charm.png` | Charm of the Quiet Tide | A smooth grey pebble with a hole through it, strung on fishing line. Hold it to your ear and you hear only the sea, and nothing counting. +2 Will, steadies a shaken mind. |
| `trout_horseshoe.png` | Trout's First Horseshoe | Worn smooth on one side, scratched with tiny pictures: a lighthouse, a well, a tower, a roof, a roof, another roof. +1 Agility, +8% movement speed, faster stamina and sanity recovery. You will occasionally turn up somewh… |

### Consumable (44)

| File | Item | Description |
|---|---|---|
| `ash_pepper_stew.png` | Ash-Pepper Stew | Hot enough to make your eyes water and your aim improve. Nobody understands why. +8% critical chance for 5 minutes. |
| `bread_loaf.png` | Bellwether Crust Loaf | Dense tavern bread baked by Marta, folded into a four-strand braid she has never been able to explain. Best eaten warm. |
| `brine_chowder.png` | Mother Brine's Chowder | So thick the spoon stands up in it. Restores health, and for a while you remember, clearly and easily, exactly who you are. |
| `bureaucrats_brew.png` | Bureaucrat's Brew | Fizzing, blue, and faintly smells of toner. For four minutes: Shatter and Overload hit 40% harder and status effects last 25% longer. |
| `carrot.png` | Carrot | Crunchy. Restores a little health and puts a spring in your step. Horses go mad for them. One particular horse goes mad for them in several places at once. |
| `crumb_cake.png` | Crumb Cake | Doobie's favourite. Baggy's favourite (kept loose in the coat pockets, hence the name). A dense little honey cake that makes you feel briefly braver than you are. Heals 15, +10 sanity, and you run 12% faster for a minute… |
| `dreaming_calamari.png` | Dreaming Calamari | Mother Brine's speciality, made with ink from the Dreaming Limb. You dream a little while awake. Your spells feel lighter, and your curses last longer. |
| `eel_pie.png` | Eldritch Eel Pie | The eyes have been baked shut. Mostly. +12% spell power for four minutes, -5 sanity. Worth it. |
| `ember_draught.png` | Ember Draught | Bottled indignation. For five minutes your fire burns hotter and your spells hit harder. Tastes of smoke and grievance. |
| `fish_cod.png` | Saltmere Cod | A fat grey cod. Edible raw, if you're desperate. Much better cooked. |
| `fish_eel.png` | Eldritch Eel | Too many eyes. One of them winked. Eating it raw costs you some sanity; cooking it costs you some dignity. |
| `fish_mackerel.png` | Mackerel | Striped, oily, and looking at you. Edible raw. Better smoked. |
| `fish_perch.png` | Pond Perch | A small, spiny, cheerful fish from the Whistling Wood pond. |
| `fish_pie.png` | Saltmere Fish Pie | Perch, bread and sage under a lid of pastry. Heals well and keeps healing, slowly, for five minutes. Mother Brine says you have to eat the crust. |
| `fish_trout.png` | A Trout (Fish) | A speckled trout. Not the horse. Hollis will want to know why you're laughing. |
| `grilled_cod.png` | Grilled Cod | Crisp skin, flaky inside, a squeeze of salt. Heals 30, then +1.5 health per second for three minutes. |
| `health_potion.png` | Crimson Draught | Bitter herbal tincture that rapidly closes wounds (+35 Health). |
| `here_bread.png` | Bread of Here | Warm, dark, a little sour, a little sweet. It smells like knowing where you are. Steadies the mind. |
| `hunters_draught.png` | Hunter's Draught | Sage, resin and something with teeth in it. For four minutes: +10% critical chance and +10% movement speed. |
| `lullaby_tonic.png` | Lullaby Tonic | Brewed round the Warden's bell. Restores your nerve completely, then keeps it topped up for five minutes. You may hum. |
| `mana_potion.png` | Aether Phial | Distilled starlight and frost-mint that restores 30 Mana. |
| `moonlit_jerky.png` | Rolf's Moonlit Jerky | Dried and smoked under a full moon by a werewolf who swears there's no wolf in it. Chewy. Restores stamina quickly for 5 minutes. |
| `oakhallow_braid.png` | Oakhallow Braid | Marta's four-strand braid, baked the way a girl with flour on her nose once taught her. Slowly mends you: +1.5 health per second for 5 minutes. |
| `oil_fire.png` | Dragon's Breath Oil | Coat your weapon: for two minutes, hits have a 45% chance to set the target on fire. Arrows count. Only one oil at a time. |
| `oil_forgetting.png` | Oil of Forgetting | Dreaming ink thinned with salt water. Enemies struck with an oiled weapon forget who they were fighting, and sometimes who they are. |
| `oil_frost.png` | Rimewater Oil | For two minutes, your hits have a 50% chance to chill. Three chills and they freeze. Only one oil at a time. |
| `oil_ink.png` | Ink of Obscurity | For two minutes, your hits have a 35% chance to blind the target. Only one oil at a time. |
| `oil_storm.png` | Stormglass Oil | For two minutes, your hits have a 40% chance to shock (+25% damage taken). Only one oil at a time. |
| `oil_venom.png` | Wolfsbane Venom | For two minutes, your hits have a 50% chance to cause bleeding. Bleeding stacks three times. Only one oil at a time. |
| `perch_skewers.png` | Perch Skewers | Little fish on sticks with sage. Heals 20, +8% movement speed for four minutes. |
| `quiet_mind_tea.png` | Quiet Mind Tea | Grave moss, marigold and a pinch of sea salt. Restores 40 sanity and steadies you for three minutes. Mother Brine's grandmother's recipe. Tastes like a rainy afternoon. |
| `sabrino_gnocchi.png` | Sabrino's Gnocchi | Pillowy potato gnocchi in brown butter and sage. Eating it feels like being hugged by someone who believes in you. +15% spell power for 5 minutes. |
| `saltmere_chowder.png` | Saltmere Chowder (Brine's Recipe) | Thick, creamy, unreasonably good. Heals 40, +1 sanity per second for five minutes. Mother Brine will deny giving you the recipe. |
| `smoked_mackerel.png` | Smoked Mackerel | Smoked over pine resin until it tastes of a whole forest and a whole sea. Heals 25, +3 stamina per second for three minutes. |
| `stamina_tonic.png` | Wayfarer's Cordial | Brisk pine-resin tonic that restores 45 Stamina. |
| `sweet_roll.png` | Baggy's Emergency Sweet Roll | Slightly squashed from living in a coat pocket. Baggy keeps a supply 'for clues and emergencies'. +0.3 critical multiplier for 3 minutes. |
| `thrown_tomato.png` | Thrown Tomato | Caught mid-air during the curtain call. A critic's gift. Still perfectly good to eat, and oddly motivating: +0.2 critical multiplier for 2 minutes. |
| `trout_hollis.png` | Trout à la Hollis | Grilled with marigold petals. +8% critical chance for four minutes. Hollis tried it, said 'Hmm', and had seconds. |
| `wand_bewilder.png` | Wand of Bewilderment | Twisted like a question mark. Each charge casts Bewilder. The number on the stack is the charges left. Put it on a quick slot. |
| `wand_entry.png` | Wand of Unauthorised Entry | Shaped like a key, if a key were also a crowbar. Each charge casts Unauthorised Entry. The number on the stack is the charges left. Put it on a quick slot. |
| `wand_friendship.png` | Wand of Sudden Friendship | Pink, with a little bow on it. Deeply unsettling. Each charge casts Sudden Friendship. The number on the stack is the charges left. Put it on a quick slot. |
| `wand_frost.png` | Wand of Frost | Rimed with ice at the tip. Each charge fires a Frost Lance. The number on the stack is the charges left. Put it on a quick slot. |
| `wand_sparks.png` | Wand of Sparks | A copper rod that buzzes in your hand. Each charge casts Chain of Command without mana. The number on the stack is the charges left. Put it on a quick slot. |
| `whetstone.png` | Whetstone | A gritty stone and a lot of patience. For five minutes, your melee hits deal +4 damage. |

### Ammo (1)

| File | Item | Description |
|---|---|---|
| `wooden_arrow.png` | Bodkin Arrow | Iron-tipped shaft capable of piercing bone and chitin. |

### Book (35)

| File | Item | Description |
|---|---|---|
| `bottle_message.png` | A Message in a Bottle | Corked, salt-crusted, with a letter inside. |
| `death_notice.png` | Writ of Legal Decease | Official notice declaring you died seventeen years ago and owe 142 crowns in burial arrears. The wax seal is very nicely done. |
| `field_guide.png` | Hollis's Field Guide to the Restless Dead | A battered notebook full of ghost lore, card-game scores and one very detailed drawing of a horse. |
| `form_27b.png` | Form 27-B (Stamped) | Application for Temporary Exemption from Being Dead. In triplicate. |
| `grimoire_chain.png` | Chain of Command: Lightning in the Workplace | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy Chain of Command into your spellbook. |
| `grimoire_clerical.png` | Spatial Misfiling and You | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy Clerical Error into your spellbook. |
| `grimoire_cold.png` | On Cold Shoulders | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy Cold Shoulder into your spellbook. |
| `grimoire_ovation.png` | The Standing Ovation (Advanced Theatrical Thaumaturgy) | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy Standing Ovation into your spellbook. |
| `grimoire_redacted.png` | [REDACTED]: A Guide to Discreet Omission | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy [REDACTED] into your spellbook. |
| `grimoire_slow.png` | Slow Burn: Patience in Pyromancy | A grimoire from the Bellwether Library's Restricted Section, decades overdue. Return it to Fenwick, who will let you copy Slow Burn into your spellbook. |
| `here_quiet_name.png` | The Quiet Name | A sliver of the plinth's stone with a single word written on it in your own hand. Whoever reads it remembers where they are, and who. |
| `hollis_deck.png` | Hollis's Deck | A battered deck of cards in a leather case. The rules are folded inside. They are long. |
| `oakhaven_postcard.png` | A Postcard from Oakhaven | A postcard of a beach, written in neat Bureau handwriting. |
| `quillsby_ledger.png` | Quillsby's Second Ledger | The real accounts. Eleven thousand gold in, seven thousand declared, and a column headed 'INVESTMENTS (SHOES)'. |
| `ransom_note.png` | The Ransom Note | Charcoal on paper, spelled with great confidence. There's a grid printed faintly on the back. |
| `script_tragedie.png` | Script: The Tragedie of the Uncounted King | Odette's play, bound in velvet, heavily annotated in red by a ghost. |
| `silas_shanty.png` | The Drowned Man's Rhyme | Old Silas's song, all of it, written out on salt-stained paper. Spelled wrong. Meant to be sung. |
| `tome_bewilder.png` | Tome: Bewilder: A Primer in Confusion | Reading it teaches the spell (and the tome crumbles). |
| `tome_ember.png` | Tome: Ember Bolt | Use from inventory to permanently learn the Ember Bolt spell. |
| `tome_entry.png` | Tome: Unauthorised Entry: The Lawyer's Edition | Reading it teaches the spell (and the tome crumbles). |
| `tome_friendship.png` | Tome: Sudden Friendship (Abridged) | Reading it teaches the spell (and the tome crumbles). |
| `tome_frost.png` | Tome: Frost Lance | Use from inventory to permanently learn Frost Lance. |
| `tome_glimmer.png` | Tome: Glimmer | Use from inventory to permanently learn the Glimmer spell. |
| `tome_late.png` | Tome: Late for an Appointment | Reading it teaches the spell (and the tome crumbles). |
| `tome_late.png` | Mother Brine's Greasy Recipe Card | A recipe card so greasy it's translucent. Teaches two of Mother Brine's specials. |
| `tome_mend.png` | Tome: Mend | Use from inventory to permanently learn the Mend spell. |
| `tome_paper.png` | Tome: Paper Storm: A Bureau Self-Defence Manual | Reading it teaches the spell (and the tome crumbles). |
| `tome_paper.png` | Hollis's Field Notes: Useful Bits of Monsters | A hunter's notebook, stained with things you'd rather not identify. Teaches workbench recipes for boss parts. |
| `tome_sabrino.png` | Grimoire: Sabrino's Questionable Fireball | Use from inventory to learn Sabrino's Questionable Fireball. Banned by the Bureau, the Collegium, and two cookery schools. The margins are full of recipes. |
| `tome_sabrino.png` | Sabrino's Forbidden Footnotes | The footnotes Sabrino tore out of a respectable alchemy textbook, because the footnotes were the good part. Teaches alchemy with boss reagents. |
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

## 6. A daytime sky

The game now has day and night. Your night and dusk horizons are used at night and at dawn/dusk; daytime needs a third one in the same format: `sky_day.png`, **1024 × 256 px**, a 360° strip that repeats left to right, opaque. An overcast, slightly melancholy day (it's Edrath): pale grey-blue sky, soft white-grey clouds, the same distant hills and pine line along the bottom as the other two so they cross-fade smoothly. Deliver it in a `skies/` folder (a placeholder made from your night sky is in the game until then).


## Done, thank you!

Fire (main, small and magic: in the game since 3 Nov), all 62 characters, the world textures, skies and ground scatter.


# HANDOFF — The Uncounted (for the next/cloud session)

You are picking up a first-person, data-driven action RPG written in C++20 on raylib 5.5. Everything below is what
the previous session (Windows desktop, MinGW) knew and you won't: read this file first, then `README.md` and
`docs/ARCHITECTURE.md`.

## 1. State at handoff (2026-11-02)

- **Playable start to finish.** Chapter Zero, *Legally Deceased*: character creation → prologue → Bellwether →
  Old Road → underground Registry Annex → boss → two endings. Plus two side quests and a two-level optional dungeon.
- **One seamless world, no loading screens.** `core:map.edrath` is composed from five region files. The Annex sits
  under the Old Road; Vault III sits under the Annex's crypt (three storeys of descent via walkable stairs).
- **Target platform: Windows 10/11 only** (MinGW build). Linux is *not* a shipping target; it is only used as a headless
  test box in cloud sessions (which run Linux and cannot execute `game.exe`). Don't add Linux packaging or Linux-only code.
- `--validate` → 0 errors; `--selftest` → 0 failures (197 checks); `--balance` → every calling beats every creature
  (36/36 at 100%). Last cloud verification 2026-11-02; re-check on Windows after pulling.
- **Not play-tested by a human for feel.** Everything was verified by headless tests and screenshots.

## 2. Testing in a Linux cloud box (testing only — the game ships for Windows 10/11)

```bash
git clone --recurse-submodules https://github.com/badsadcode/TheUncounted.git
cd TheUncounted
# if you cloned without submodules:
git submodule update --init --depth 1
```

raylib (desktop/GLFW) needs X11 + GL headers; tests need a window, so use a virtual framebuffer with Mesa:

```bash
sudo apt-get update && sudo apt-get install -y build-essential cmake python3-numpy python3-pil \
  libx11-dev libxrandr-dev libxinerama-dev libxcursor-dev libxi-dev libgl1-mesa-dev xvfb mesa-utils
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j"$(nproc)"          # writes ./game to the project root
./game --validate                         # no window needed
xvfb-run -a -s "-screen 0 1280x720x24" ./game --selftest     # expect "Self-test finished with 0 failure(s)."
xvfb-run -a -s "-screen 0 1280x720x24" ./game --balance       # table lands in uncounted.log
xvfb-run -a -s "-screen 0 1280x720x24" ./game --shot /tmp/s.png --pos 48 -10.4 -22 --yaw -90 --frames 20
```

Linux notes (verified 2026-11-02 on Ubuntu 24.04 / GCC 13.3):
- The only fix needed: GCC 13 rejected `GameEngine::Toast()` because it changed the meaning of a `struct Toast` used
  earlier in the class (`-Wchanges-meaning` is a hard error). The struct is now `ToastMsg`. Keep type and member
  function names distinct.
- Xvfb + Mesa llvmpipe gave an OpenGL 3.3 context with no extra env vars; screenshots look identical to Windows.
- `python3-numpy`/`python3-pil` may already be present; only the X11/GL `-dev` packages had to be installed.

Original expectations (kept for reference):
- OpenGL 3.3 under Xvfb comes from Mesa llvmpipe; if the context fails, try `LIBGL_ALWAYS_SOFTWARE=1`.
- No audio device in the cloud: harmless, and automated modes never open audio anyway (see §6).
- Paths are case-sensitive on Linux. All 181 asset references were checked to match file names exactly at handoff;
  keep it that way (`tools/` scripts and content must use the real case).
- `CMakeLists.txt` only adds `winmm/gdi32/opengl32` on WIN32 and `-static` on MinGW; raylib's own CMake brings
  X11/GL/pthread/dl/m on Linux.

## 3. Verification loop (use it after every change)

| Command | What it proves |
|---|---|
| `./game --validate` | All JSON loads; every cross-reference (items, loot, quests, dialogue, assets, zones, barks, narration keys) resolves |
| `./game --selftest` | 87 scripted checks through the real gameplay code: movement/collision, stairs between all storeys, zones, dialogue gating, keys/lever/plate/doors, combat, loot, both side quests, the Seal, save/load round trip, ending |
| `./game --balance` | 6 callings × 6 creatures duels (elites/bosses at level 3 + 2 potions); edit content stats, rerun |
| `./game --shot out.png [--pos x y z] [--yaw deg] [--pitch deg] [--overlay …] [--showcase] [--arch n]` | Renders frame N and saves a PNG; look at it to judge visuals |

`src/gameplay/SelfTest.cpp` uses **world coordinates**; if you move geometry, update it.

## 4. Code map

| Path | Role |
|---|---|
| `src/main.cpp` | Entry; dispatches `--selftest` / `--balance` / normal run |
| `src/core/Types.h` | All content structs (items, creatures, NPCs+barks, dialogue, quests, maps, zones, interactables, emitters, ramps) |
| `src/content/ContentRegistry.*` | JSON loading (manifest + mods) and cross-reference validation |
| `src/resource/ResourceManager.*` | Texture/model/font/sound caches with diagnostic fallbacks |
| `src/renderer/WorldRenderer.*` | Internal-res render target, lit models, 8-direction billboard sprites, emitters, particles, rain/dust, viewmodel |
| `src/world/Scene.h` | Runtime instances (props, interactables, NPCs, creatures, projectiles, pickups, particles) |
| `src/gameplay/GameEngine.*` | Everything gameplay: input, movement & collision (AABB + ramps), AI, combat, quests, dialogue, loot, shop, saves, zones & atmosphere blending, audio crossfades, barks, narration |
| `src/gameplay/GameUI.cpp` | HUD, menus, overlays (inventory, character, journal, map, dialogue, shop, container, reader, options, narration, subtitles) |
| `src/gameplay/SelfTest.cpp`, `BalanceSim.cpp` | Headless test and balance harnesses |

## 5. Content pipeline — which files are the source of truth

- **Hand-edited sources:** `content/**/*.json` (except `content/maps/edrath_world.json`), `content/regions/*.json`, `config/*.json`, `mods/`.
- **Generated — rerun after editing sources:**
  - `python3 tools/build_world.py` → `content/maps/edrath_world.json`. It places the regions (Bellwether at the origin,
    Old Road +48 x, Annex at (87, −4.8, −8.4), Vault III at (54.6, −10.4, −22.0)), cuts the connecting openings, builds
    the stair tunnels, and defines the five zones.
  - `python3 tools/build_sprites_prerendered.py [name]` → 8-direction sprite sheets (SDF models raymarched, cel-shaded).
  - `python3 tools/build_item_models.py` → small item GLBs + the seal-quill icon.
  - `python3 tools/build_music_ambience.py` → music/ambience WAVs (long, drone-free, seamless loops).
- **Bootstrap-only — do NOT rerun:** `tools/build_content_json.py`, `tools/build_maps_and_mod_json.py` (they would
  overwrite the hand-written story, regions and tuning). `build_assets_art.py`, `build_assets_audio.py` (SFX only) and
  `build_assets_blender.py` are the original asset generators.

## 6. Conventions & gotchas

- **Model anchoring:** props are placed by their bounding-box *bottom centre* at `pos`; ground slabs have their top at y≈0.
- **Yaw:** forward = (sin yaw, 0, cos yaw); yaw 90° faces +X. Map JSON uses degrees.
- **Sprite sheets:** 64×64 frames, 8 columns = directions relative to the viewer (0 front, 2 left, 4 back, 6 right),
  rows idle / walk ×2 / windup / attack / stagger+corpse. Pivot (0.5, 0.92).
- **Stairs:** `stairs_stone.glb` rises toward its local −Z; at `rot_y` 90 it climbs toward −X, at −90 toward +X. Give the
  prop `"ramp"` with the rising direction so it is walkable.
- **Zones** blend atmosphere spatially; the dominant zone names the area, drives music/ambience crossfades and weather;
  `flag_override` swaps weather/ambience after a story flag (signing the Seal stops Bellwether's rain).
- **Quests only move forward; dialogue/readable rewards pay out once per save** (`player_.claimed`).
- **Silent testing is a hard user requirement:** `--selftest`, `--balance`, `--shot` never initialise audio; use
  `--mute` for any other automated launch. Don't remove that guard.
- Saves from before the seamless world fall back to the world start (pre-release, acceptable).

## 7. Story at handoff

- Main: *Legally Deceased* (stages 0/10/20/30, endings 100 Bureau / 101 Ashbound).
- Side: *A Name Worth Keeping* — Oakhallow boundary stone → Marta → struck census in the Annex archive → the Witness →
  tell Marta "Ilse Brannock" (flag `ilse_remembered`).
- Side: *The Sleepers of Vault III* — flour handprints in the crypt → Ilse asleep in the Nursery (`found_ilse`) → kill the
  Lullaby Warden → sign the Seal of Names (`seal_renewed`, 4 narration cards, Seal-Quill, rain stops).
- Marta reacts to Vault III in any order: `found_ilse` before the name is known → `sleeper_unnamed`; name known but
  Seal unsigned → `ilse_alive` (sets `marta_knows_ilse`, she begs you to go back); Seal signed → `ilse_alive_safe` or,
  if she already knew, `seal_signed` (both set `marta_knows_seal`, bread gift). The "alive" choices also appear straight
  after naming Ilse. The clerk's `rain_stopped` topic (flag `clerk_seal_talk`) shows forty Oakhallow children
  reappearing in the register. Barks can now be gated by `flag` / `not_flag`; Marta's rain bark stops after the Seal.
- Ending epilogue reacts to `marta_testimony`, `spirit_clue_learned`, `ilse_remembered`, `marta_knows_ilse`, `seal_renewed`.
- Preview any conversation node: `--shot out.png --overlay dialogue:core:npc.innkeeper_marta:ilse_alive`. The dialogue
  panel grows upward to fit long text.

### Content structure: campaigns, not one storyline

The user's direction: not everything has to belong to one plot. New content should usually be its **own campaign,
chapter or tale** that stands on its own, with optional light cross-links (a cameo, a bark, a bonus ending) rather than
hard dependencies. Quests carry a `campaign` id; campaigns are defined in a quests file (`"campaigns"`: id, name_key,
desc_key, kind main/side/tales, order). The journal groups quests by campaign; the HUD shows the main story plus one
tracked side quest (`player.tracked_quest`: the latest side quest advanced, or whatever the player picks in the
journal). Current campaigns: **Chapter Zero: Legally Deceased** (main + its own side threads), **Tales of Bellwether**
(rats, Dinner at Eight), **The Hollowmere Mysteries** (Hollis's case files; Case #1 is the haunting — add Case #2...).
A future main chapter would be a new campaign (`chapter_one`, kind main) with its own quests and regions.

### The Bellwether Players (campaign `bellwether_players`) — written to be read aloud

Toasty streams and likes to read dialogue aloud and roleplay. Write for that: named speakers, script-style lines
(`ROLF (as Prince Valiant): "..."`), stage directions, distinct voices, roleplay-flavoured choices ([Dramatic],
[As Sabrino], [Blunt]...), and choices that matter later. Group scenes use per-node `speaker_key` (the dialogue box shows
that speaker's own name and title).

1. **Act I: Casting Call** (`players_casting`): Madame Odette Velour (south gate) auditions you — your delivery style is
   remembered (`style_*`) and called back on opening night; recruit ≥4 of `cast_*` (Baggy, Rolf, Ashgrave, Hollis,
   Sabrino, Marta, Fenwick, Oakhaven — Oakhaven makes you fill in Form 99-T).
2. **Act II: The Missing Script** (`players_script`): five page readables (Records Office, Old Road pine, Annex archive,
   Vault III, Hollowmere library — page five starts stage 10 and reveals Mortimer Quill, the ghost critic) → a
   three-round "duel of criticism" (`critic_r1..3`; the right answer to round three is in the margins) → script back.
3. **Act III: Dress Rehearsal** (`players_rehearsal`): Odette moves to the Hollowmere ballroom (second NPC instance,
   `players_at_hollowmere`); solve ≥3 backstage dramas (one per cast member, `reh_*`), then props: crown (Fenwick's paper
   crown or the Rat King's crown), dragon (Vaelen), bang (Sabrino or Oakhaven's confiscated thunder sheet).
4. **Act IV: Opening Night** (`players_opening`): the play as an interactive script; `show_good_1..6` tally the good
   moments → three bows/endings (triumph ≥5, good ≥3, glorious disaster), each with Mortimer's review read in narration.
`tools/authoring/players_campaign.py` is the (already-run, do-not-rerun) authoring script — copy its `Dlg` helper for new long dialogue.
Engine additions: condition `flags_fewer_than`; dialogue box shows the node speaker's own title.

### Quest markers, party, text size, Dungeons & Debtors (added 2026-11-03)

- **Quest markers:** a quest stage may list `markers` (instance ids of NPCs / interactables / creatures / pickups); the
  nearest relevant one is shown (hidden NPCs, dead creatures, used objects and readables whose `set_flag` is already set
  are skipped). The HUD compass (above the quick slots) points at the tracked side quest's marker, else the main
  story's, with distance and up/down; the map pins it (at the edge if it's on another storey/area). Validation fails if
  a marker isn't placed in any map. **Give every new quest stage markers.**
- **Party:** `player.companions` (max 2, `kMaxCompanions`; old saves' `companion` still loads). Companions take the two
  slots behind you; subtitles from party members queue (`QueueSay`) instead of overwriting each other. Companion `banter`
  blocks (`id`, `partner`, `lines` [{by: self|partner, text_key}], `flag`/`not_flag`) play once per save when both are
  present. Conditions `party_has_room` / `party_full`. **Kaelen** is the second companion (8 banter scenes with Baggy).
- **Options → Dialogue text size** (100–150%, `text_scale` in config/game.json) scales dialogue, choices, subtitles,
  books and narration; the dialogue panel shrinks the font only if a scene wouldn't fit. For streaming.
- **Campaign `dungeons_debtors`** (Dungeons & Debtors): Session Zero–Three, started from Clerk Oakhaven ("What do you
  do on Thursdays?"); Oakhaven is the Game Master, Baggy/Rolf/Hollis/Ashgrave/Marta the players (in script format).
  Class flags `dnd_*` unlock class moves; `dnd_win_*` tally good play. Reward: Oakhaven's Lucky d20 (`dice_bonus` +2:
  added to every dialogue roll) and the GM's Screen (off-hand). Authoring script: `tools/authoring/dungeons_debtors.py`
  (already run — do not rerun).
- Fixes: hidden NPCs no longer appear on the map, and NPC visibility is right from the first frame.

### Saltmere Docks, sanity, Case File #2 (added 2026-11-03)

- **Saltmere Docks** (`tools/build_docks.py` → `content/regions/saltmere.json`, generated) north of Bellwether through a
  gap in the north wall (DOCKS_OFF = (1.6, 0, -42)): fog-bound quay, shallow harbour (walkable sea floor under a water
  model — you can wade, never get stuck), two piers, boats, giant tentacles in the fog, the Drowned Lantern tavern
  (Mother Brine, Professor Pickering), the Harbourmaster's post, Silas on the north pier, Gale & Sons' warehouse with a
  gated stair (cellar key from Silas / lockpick 13) down 5.6 m to the **Sunken Chapel** (zone `sunken_chapel`, drains
  sanity). Models from `python tools/build_item_models.py docks_models`; the Avatar uses the new `eldritch` sprite kind.
- **Sanity** (`player.sanity`, 0–100, saved): zones may set `sanity_drain`; readables `sanity` (first read); dialogue
  action `sanity` (amount); creature attacks `sanity_damage` (melee and projectiles). Companions cut the drain by 25%
  each and speed regeneration; resting (`heal_player`) restores it; food bonus `sanity_regen`. Below 60: whispers
  (`whisper.N`) and a violet pulse; below 30 the compass stops making sense; at 0 you black out and wake on the quay
  (spawn `saltmere_quay`) at 50. HUD bar appears whenever sanity < 100 or the zone drains it.
- **Case File #2: The Silence at Saltmere** (`core:quest.saltmere`, campaign `hollowmere_mysteries`): from Hollis
  (after the haunting is identified) or the Harbourmaster directly → interview ≥3 (`saltmere_t_*`) → Pickering's theory
  (stage 20) → cellar → silence the three tide bells (stage 30) → the Tide Priest. Four endings: fight the Avatar of the
  Name-Eater (group trigger → 40 + `saltmere_resolved`), read the hymn backwards (lore DC 14, needs `hymn_read`), say
  the Priest's real name (Ezekiel Wick — learned from his brother the Harbourmaster), or feed it **Form 27-B** (needs
  the item). Then Hollis → 100 (harpoon, bane `eldritch`). New family `eldritch`; Kaelen/Baggy zone lines and a banter.
  Authoring script: `tools/authoring/saltmere.py` (already run — do not rerun).
- Lore tie-in: the Name-Eater *is* the Hunger from Chapter Zero; the player is invisible to it because their name was
  struck. Keep future eldritch content consistent with that.

### Dungeons & Debtors II: The Lich Who Forgot to File (added 2026-11-03)

- Oakhaven's second tabletop campaign: four sessions (`core:quest.lich_s1`..`lich_s4`, campaign `dungeons_debtors`),
  unlocked by finishing Campaign One (`dnd_session3` = 100); topics on Oakhaven's greeting, one per Thursday. Each
  session's first node sets its quest to stage 0; the last sets 100.
- New at the table: **Sabrino** (playing the wizard *Sabrino the Second*: only casts Fireball) and **Kaelen** (the
  chronicler: reads a "PREVIOUSLY…" recap at the start of every session; Campaign One's recap branches on `dnd_dragon_down`).
- I The Descent (opinionated mushrooms, rival party *The Glorious Five*, Steve returns → `lich_steve`); II The City of
  Inkwell (gnome bureaucracy, Form 1-UD, Gerald's finest hour, heist plan → `lich_plan_*`); III The Heist (the plan dies
  on a natural 1; everyone improvises; class moves on the vault door, incl. Steve's; the phylactery is a filing cabinet
  with an empty OUT tray); IV The Lich (Archchancellor Vellum Dreadquill: fight/stop, help him file it, a Bard's
  lullaby, or "you don't have to finish everything to be allowed to rest" → Oakhaven breaks character: the Lich was
  about him). `lich_win_1..8` tally good play (≥6 → `lich_legend`, bigger gold).
- Rewards: **The Archchancellor's Quill** (accessory: +2 Intellect, +8% spell power, +1 dice) and **A Postcard from
  Oakhaven** (book). Afterwards Oakhaven has a seashell, a sunburn, a new bark, and teases Campaign Three ("The Mimic Who
  Wanted to Be a Real Chest"). Icons: `python tools/build_item_models.py lich_items`.
- Authoring script: `tools/authoring/lich_campaign.py` (already run — do not rerun). Selftest plays all four sessions.

### Story canon (keep new writing consistent with this)

- **412 years ago — the Great Silence.** Something beyond the world, *the Hunger*, finds its way in through spoken names.
  The Archivists (a quiet order inside the Bureau, later staffed in *Annex III*) struck seven cities from the Grand
  Register, hid them in the *Uncounted Ledger* and signed the *Seal of Names* over them. The Church teaches it was a
  divine "curtain of mercy"; Brother Aldous knows better.
- **17 years ago — the Seal cracked.** Chief Archivist Morvath struck Oakhallow (pop. 412) in one night. Forty children
  went into enchanted sleep in Vault III (the Nursery); some adults were scattered with sealed memories (Marta Brannock →
  "Marta Kettleburn" in Bellwether; hinted: the player, a child of Mill Lane); the rest, incl. Tomas Brannock, were
  unwritten by the Hunger. Morvath bound himself to the Ledger and went mad (sanctum boss). Night-Warden Sister Hessa
  Vane kept singing the children asleep and became the Lullaby Warden. Junior Archivist Wendel Ashcombe is the
  Witness (remembers his name after the Seal: flag `witness_named`). The Annex "closed for refurbishment" and sank.
- **Ordinary Bureau clerks** (Oakhaven) only record what's left: a struck name with no body goes in the deceased column
  — hence the player's death notice and burial bill.
- **Now:** the ink is fading; the Ledger's final folio says Bellwether is struck at the next new moon unless the Seal is
  signed by a name freely given by its owner — the player's struck name. It has rained on Bellwether for 17 years.
- **Tone:** bureaucratic absurdity (forms, arrears, Fenwick's late fees, Vaelen's prices) layered over real grief
  (Marta, Ilse, Oakhallow). Keep both; let the jokes stop when the grief arrives. Kaelen has no fixed gender — avoid
  pronouns for Kaelen.
- **Reactive topics** (all gated, all once-only where it matters): clerk `who_struck` / `key_paradox` / `arrears` /
  `inspect_ledger_sealed`; Vaelen `rumors_bureau`; Marta `news` / `father`; Fenwick `history` / `history_after`; Aldous
  `hunger` / `bells`; Kaelen `ashbound` / `ledger` / `road_quiet`; Witness `oakhallow` / `morvath` / `remembered`.
  Most NPCs have a post-Seal bark (`flag: seal_renewed`).
- Previews: `--overlay reader:<item id>` (books), `--overlay ending` (longest epilogue), `--overlay dialogue:<npc>:<node>`.

### Build systems & the Toasty easter eggs (added 2026-11-02)

The game is a gift for the user's friend **Toasty (TaoistDragon)**, who loves digging into builds, spells and weapon stats.
His characters: **Sabrino**, the Italian witch "war criminal" (ESO), and **Baggy**, a bumbling but good-hearted private eye
(Shadows of Doubt). Keep both affectionate and funny; the title screen carries a dedication (`game.dedication`).

- **Weapon traits** (`weapon` block): `crit_chance`, `crit_mult`, `life_steal`, `mana_on_hit`, `bane_family` + `bane_mult`.
  Creatures have a `family` (undead / beast / construct / spirit).
- **Gear bonuses:** item effect `{"type": "bonus", "stat": <key>, "value": x}` feeds the same pool as synergies.
  Keys: crit_chance_bonus, crit_damage_bonus, life_steal, spell_power_bonus, spell_cost_reduction, shop_discount,
  lockpick_bonus, melee_bonus_magic_damage, mana_on_melee_hit, heal_on_block, armor_bonus, ranged_crit_multiplier,
  move_speed_bonus. `Bonus(key)` = synergies + gear. Labels live in `BonusLabel()` (GameUI.cpp) — add new keys there too.
- **Crit chance** = weapon base + 0.5% per Agility over 10 + 15% of Perception's effect + bonuses (cap 75%).
- **Spells:** `splash_radius` and `drain_fraction` on `projectile_damage`. New: Frost Lance (Vaelen sells the tome),
  Siphon Ink (Vault III nursery chest), Sabrino's Questionable Fireball (Sabrino's stash).
- **Synergies (7):** + Sabrino's Doctrine, Baggy's Hunch, Cutpurse's Grace, Iron Liturgy.
- **Character screen → Combat Sheet tab**: every derived number, computed by the same helpers combat uses
  (`MeleeHitDamage`, `CritChance`, `SpellPowerMult`, `SpellCost`, `LockpickChance`, `ShopDiscount`). Inventory shows
  traits and "Your DPS (± vs equipped)".
- **Sabrino:** wanted poster by Bellwether's gate (`sabrino_wanted`), stash behind a pine on the Old Road's north side
  (`sabrino_stash` + `sabrino_note`: Pointed Hat, Fireball grimoire), Fenwick's `overdue` topic, clerk/Fenwick barks.
- **Baggy** (`core:npc.detective_baggy`, Old Road by the boundary stone, sprite style `detective_baggy`): wrote the
  charcoal note on the stone; was an Oakhallow child. Topics: case, board, stone, Sabrino (+ stash hint), build advice
  (real tips), rain. Telling Baggy Ilse's name (`ilse_remembered`) → `baggy_ilse`, gives **Baggy's Trusty Umbrella**.
  Write Baggy and Sabrino without third-person pronouns.
- Assets: `python tools/build_item_models.py baggy_umbrella sabrino_hat extra_icons` (now takes builder names; running
  it with no names rebuilds every item model, which is not byte-identical — prefer names).
- Previews: `--overlay combat` (Combat Sheet with a crit build), `--overlay compare` (inventory comparison).

### Companion, Dinner at Eight, food & new monsters (added 2026-11-03)

Toasty has been feeling lonely; the user asked for company in the game above all. Keep that spirit: warm, funny,
nobody left out.

- **Companions** (`"companion"` block on an NpcDef: damage, attack_time, reach, heal_amount/heal_cooldown, zone_lines,
  idle_lines [flag/not_flag gated], combat/kill/heal/level lines). Dialogue actions `recruit_companion` /
  `dismiss_companion`; the player's companion is saved (`player.companion`). `UpdateCompanion()` follows a slot behind
  and to the right, catches up out of sight across storeys/doors, fights alerted creatures near the player, hands over
  food below 35% health, comments on first arrival in each zone (once per save) and chats every ~2 minutes. Companions
  don't body-block and don't bark. **Baggy** is the companion (`join` / `wait` topics, flag `baggy_following`).
- **Map NPCs** may set `requires_flag` / `hidden_flag` (present only with/without a story flag; live, no reload).
- **Dialogue:** condition `flags_at_least` (`flags` + `value`); action `narrate` (`pages`: keys or {key, flag}).
- **Food buffs:** item effect `{"type": "buff", "stat": <bonus key>, "value": v, "duration": s}`; new keys
  `health_regen`, `stamina_regen`. Bonus() = synergies + gear + food. Saved with the game.
- **Quest `core:quest.dinner_at_eight`:** read Sabrino's note (Old Road stash) → Sabrino appears in the Lantern Inn
  (`sabrino_in_town`) → bring Grave-cap Truffle (Truffle Hogs / crypt & Nursery pickups), Ash-Pepper (every Ash
  Crawler drops one) and Vallo Red (Vaelen) → invite ≥3 of Marta, Baggy, Kaelen, Fenwick, Aldous, Oakhaven, Vaelen,
  Wendel (`invited_*`) → the dinner (narration cards for whoever came) → Ladle of Justice, food, Sabrino's food shop.
- **Monsters:** Bone Clerk (undead, Annex foyer & archive; drops Bone Clerk's Spectacles), Ink Wraith (spirit, ranged;
  archive & Nursery), Truffle Hog (beast — it's a rat; nobody has told it). Self-test checks every spawn is clear of walls.
- Previews: `--flag <name>` (repeatable) and `--companion <npc id>` for `--shot`; `--overlay narration:<key>`.

### Hollowmere Manor, rats, dice and parody (added 2026-11-03)

The user wants lots of affectionate, *unnamed* references to popular RPGs (open-world fantasy, monster-hunter, party-based
CRPGs, roguelikes, ghost-hunting co-op, old-school tabletop & board-game dungeon crawls) and pop culture (YA vampires and
werewolves, fantasy bestsellers), plus typical game bugs players complain about. Never name the games; keep it clever.

- **Hollowmere Manor** (`tools/build_mansion.py` → `content/regions/hollowmere.json`, generated — edit the script) sits
  south of Bellwether (HOLLOW_OFF = (0, 0, 42)) through a gap cut in the village's south wall. Grounds (graveyard of
  adventuring-party mistakes, Rolf's garden) + a two-storey house: foyer with grand stair, dining room, library,
  kitchen, ballroom; landing, master bedroom, locked study, portrait gallery, sealed room. Zones `hollowmere` (grounds,
  rain) and `hollowmere_manor` (interior).
- **Quest `core:quest.rats`** (Vaelen): town rats spawn live (`requires_flag: rats_in_town`), clearing group
  `town_rats` → 20; the kitchen rats + Rat King (group `rat_king`) → 40 (works even if never started) → Vaelen → 100.
- **Quest `core:quest.hollowmere`** (Hollis or the gate sign): collect ≥3 of `ev_cold`, `ev_writing`, `ev_floating`
  (true) / `clue_bites`, `clue_claws`, `clue_wailing` (red herrings explained by Ashgrave/Rolf), identify with Hollis
  (wrong guesses are scolded, retryable) → 20, Percival appears (`host_identified`). Endings: banish via Hollis
  (`host_banish` spawns the Wrathful Host; group trigger → 100, `host_banished`, Hollis pays + Silver Sword) or a party:
  Percival + ≥3 dinner guests (`invited_*`) or a DC 15 persuasion roll → 101 (`host_at_peace`, signet).
- **Engine:** creature spawns may set `requires_flag`, `group`, `group_quest_id`/`group_set_stage`/`group_set_flag`
  (fires when the whole group is dead). Dialogue choices may carry `"roll": {skill, dc, fail_next, rigged}` — d20 +
  skill/4 (+ Presence mod for persuasion); the odds show on the choice; `rigged` makes the first attempt a natural 1.
  Conditions `item_equipped` / `item_not_equipped`. Death screen shows a random `tip.N`. Companion `catchup_lines`.
- New NPCs: Hollis the Grey (monster hunter, cards, horse on the chapel roof), Lord Ashgrave (sparkly vampire lodger),
  Rolf (shirtless werewolf gardener), Sir Percival (the Host). Monsters: Animated Armour, Wailing Footman, Rat King,
  Wrathful Host. Items: Dented Bucket (shopkeeper discount), Party Hat, Crown of the Rat King, Cape of Eternal
  Brooding, Hollowmere Signet, Silver Sword of the Grey, Moonlit Jerky, Field Guide, keys.

### The Figure It Out Gang (added 2026-11-03)

A spinoff Toasty made up: a meddling mystery gang in the spirit of the classic Saturday-morning sleuths (originals, never
named after them), with the **Figure It Out Wagon** instead of a famous van. Running gag: **Baggy** (Toasty's recurring character, in the cowardly-hungry role) yells **"I barely knew
her!"** at every unmasking, whoever (or whatever) is under the mask. Tone: silly, not competent, spooky, successful.
Authoring script `tools/authoring/figure_it_out.py` (archive, already ran, do not rerun). Campaign `figure_it_out` (tales).

- **Camp** on the Old Road (local ~(18..25, -4..-10)): the wagon prop (`figure_wagon.glb`, `build_item_models.py
  wagon_models`), a campfire, Sir Rodrick (leader, every trap catches the wrong person), Lady Primrose (always kidnapped,
  punches), Agnes (actually solves it, loses spectacles), Snacks the cowardly owlbear cub
  (feed it Crumb Cakes; scratch it for sanity). Baggy is a founding member: gang topics in
  Baggy's own dialogue (`gang`, `gang_barely`, `gang_horse`, a Trout callback); the trap in ep 1 catches Oakhaven instead.
  (A first draft had an extra character, Crumbs, in that role; `tools/authoring/figure_baggy.py` wrote him out.)
- **Formula per episode** (stages 0 → 10 clues → 20 trap → 30 catch → 40 unmask → 50 → 100): clue readables use
  `requires_flag` (`fig1_open` / `fig2_open`) and set `fig*_c1..3`; Rodrick needs all three (`flags_at_least`); the trap is
  a readable with `requires_flag` + `hidden_flag` + `narration` (readables now play narration as a story scene); it
  spawns the monster (`requires_flag`, group trigger → 40, `fig*_caught`), then a netted-suspect NPC appears
  (`requires_flag: fig*_caught`, `hidden_flag: fig*_done`) for the unmasking dialogue.
  - **Ep 1 "The Phantom Clerk of Bellwether"** (Bellwether): it was Vaelen, selling Ghost-B-Gone charms. Reward: Crumb
    Cakes + gold.
  - **Ep 2 "The Howler of Hollowmere"** (Rolf's garden, placed via `tools/build_mansion.py`): Rodrick unmasks Rolf first
    ("OW. That's my face."); it was Brother Aldous, four years second at the Marrow Show; Rolf offers to teach him.
    Reward: the Gang Scarf (accessory: crit, speed, sanity regen, +1 dice).
  - **Ep 3 "The Headless Knight of the Old Road"** (`tools/authoring/figure_ep3.py`; clues on the Old Road itself):
    Agnes was right, it's a hat on a stick; it's Steve in Vaelen's haunted armour, thrilled to finally be a villain
    with a reveal. Snacks is brave once (charges the knight). Reward: Snacks's Brave Feather (accessory).
- **Engine:** interactables may set `requires_flag` / `hidden_flag` (hidden ones are skipped by the prompt and renderer).
- Sprites are prerendered placeholders (`build_sprites_prerendered.py`: figure_*, phantom_clerk, howler); the user may
  paint proper sheets later.

### Grout and recorded voice lines (added 2026-11-03)

- **Grout** (`core:npc.grout`, `tools/authoring/grout.py`): a grumpy, terse gargoyle companion by the Records Office
  door, written for the user to voice on stream. Classified by the Bureau as "a fixture, not a citizen" (legally nobody,
  like the player; `grout_kin`). Hits hard (11 per swing, slow). Banter with Baggy and Kaelen, a line per area. The full
  line list in script format is `docs/GROUT_VOICE_SCRIPT.md`. Avoid pronouns for Grout in text.
- **Voice playback:** `ResourceManager::PlayVoice(key)` plays `assets/audio/voice/<localization key>.ogg|wav|mp3` if it
  exists, for companion lines, banter, barks, creature alert/death lines and dialogue nodes (on entering the node).
  The subtitle stays up at least as long as the clip. No file = text only, as before.
- **Snacks** (`tools/authoring/snacks_companion.py`) can join after the Headless Knight (`fig3_done`; flag
  `snacks_following`): weak in fights, generous healer (snacks), banter with Grout, Baggy and Kaelen.
- **Bestiary** (character screen, 4th tab): `PlayerState.kills` (saved) counted in `KillCreature`; entries show stats
  + a field note (`bestiary.<creature suffix>`, `tools/authoring/bestiary.py`) after 1 kill, drops after 3, and at 10 kills
  Hunter's Insight (+5% damage vs that kind, in `DamageCreature`). Preview: `--shot X --overlay bestiary`.
- **More monsters** (`tools/authoring/more_monsters.py`): Kevin the bandit + hedge goblins (Old Road), angry badgers + wisps
  (Wood), a gravedigger ghoul (Hollowmere graveyard), Pinchwick crabs (Saltmere quay), paperwork elementals (Annex), salt
  wights (reef). Placeholder sprites; Bestiary notes included.
- **Windows build:** `.github/workflows/windows-build.yml` tests on Linux, cross-compiles `game.exe` (`tools/mingw-w64.cmake`),
  uploads `TheUncounted-windows.zip` as an artifact (and to a Release on `v*` tags). `GAME_BUILD` labels the title screen.
- **Playtest fixes (2026-11-03):** the sky panorama and stars used the wrong azimuth direction (they turned against the
  world; raylib's screen-right is decreasing azimuth). Bloom is `glow_level` 0-3 (default Medium) with a higher
  brightness threshold. Rain/wind ambience low-passed (no hiss). Levers: mesh 0 (base) fixed, the rest pivot.
  `door_frames()` in build_world.py fills the gaps between doors and their walls/lintels with wooden frames.
- **Level editing in Blender** (`tools/blender/uncounted_level_editor.py`, guide `docs/LEVEL_EDITOR.md`): Import World builds
  the map in Blender (meshes re-originated at the game's bottom-centre anchor, game (x,y,z) = Blender (x,-z,y), rot_y =
  rotation about Z); Export writes `mods/level_edits/map_edits.json` (props modify/add/remove, npcs/creatures/interactables
  modify). `ContentRegistry::ApplyMapEdits` applies every `mods/*/map_edits.json` after loading (always, even with mods
  disabled). To bake a user's edits into the real levels, apply them to the region builders/JSON by prop id.
  v2: npcs/creatures/interactables also take `set` (full definitions, replace or add) and `remove`; props `modify` takes
  `solid`/`uv_scale`. The add-on shows doors/chests as their models with editable `game_*` custom properties (types kept
  in `unc_types`), has templates in the palette, and bakes user-made meshes to `mods/level_edits/models/*.glb`
  (world-space, origin at the bottom-centre). Tested headless: an untouched import exports nothing; round trips are stable.
  v3 (new maps): `ContentRegistry::LoadUserMaps` loads every `mods/user_maps/<slug>/map.json` (id `user:map.<slug>`, a
  full map file) before the edits are applied; portals can be `set`/`remove`d by edits too. Props take `invisible: true`
  (collision only, not drawn): the add-on exports meshes named `COL*` as stretched invisible `wall_stone.glb` boxes. Own
  meshes carry `uncounted_solid`, `uncounted_ramp` and `uncounted_tile` (box-projected UVs, one repeat per N metres);
  Blender POINT lights become map lights (radius = W / 60) in New Map mode only. Selftest builds a tiny user map, walks
  into its invisible wall and takes its portal home.
  v4 (not a mod any more): World Export writes `content/maps/edrath_blender.json` (the cumulative diff against
  `content/maps/edrath_world.base.json`) and rewrites `content/maps/edrath_world.json` = base + diff; own models go to
  `assets/models/level/`. `tools/build_world.py` writes the base, then applies `edrath_blender.json` (via
  `tools/map_edits.py`, warning about changes to props that no longer exist), so region rebuilds keep Blender work. New
  maps: `content/maps/custom/<slug>/map.json` (id `core:map.<slug>`), models `assets/models/custom/<slug>/`; the engine
  loads them (and the legacy `mods/user_maps`). Older `mods/` saves are imported and renamed `*.moved_into_game` on export.
  Blender preview: imported materials get a node chain multiplying UVs by the object's `game_uv_x/y` (Attribute nodes),
  so Material Preview tiles like the game. "Pack My Changes" zips the level files for sending.
  v4.1: game pieces reshaped in Blender are detected by a mesh fingerprint (`unc_hash`: vertices, UVs, material
  indices, material names) and baked per mesh datablock in object space (`<model>_editN.glb`), keeping pos/rot/scale.
  Solid meshes get shape-fitting collision: the closed mesh is voxelised (BVH inside test, cell >= 0.2 m) and greedily
  merged into invisible `<id>__fitN` boxes (<= 120, else one box); the visible piece becomes non-solid. `__fit` props are
  skipped on import and rebuilt on export.
  v4.2: World mode also brings in the map's lights (POINT lights, W = radius x 60) and spawns (arrows); when they differ
  from the base, the edits carry the whole `lights` / `spawns` list; `scatter: []` when "Keep grass & flowers" is off
  (`tools/map_edits.py` handles all three). Fit collision now works per loose part with a six-ray back-face vote, so
  overlapping boxes and imperfect meshes work (no closed-mesh requirement), grid >= 0.12 m, <= 150k cells per part.
  v4.3: `uncounted_tile` defaults to 0 (keep the user's unwrap; it used to overwrite UVs at 2 m). Reshaped game pieces
  whose UVs differ from the original (`unc_uvhash`) export with `uv_scale` [1, 1].
  Tested headless on Blender 4.0.2 (`blender -b --python`) and 5.1.1 (`pip install bpy==5.1.1` in a venv, then
  `python script.py`): Toasty uses 5.1.
  v4.4: fit collision is built in world directions (object rotation and scale applied, boxes rot_y 0, matching the
  engine's world AABBs) with cells at most 0.2 m tall, so any slope becomes walkable steps (diagonal 35° ramp: 264 boxes,
  walked to the top in a simulation of MoveWithCollision/GroundHeight; spiral stairs need >= 0.65 m step depth).
  v4.5: NPC/creature markers are IMAGE empties showing the sheet's first frame (cropped with numpy into a packed
  `UNC_SPRITE:<sheet>` image; height = appearance.scale, offset from the animation pivot), stood up with rotation X 90°
  (`unc_upright`, ignored by the tilt warning; yaw stays rotation Z) plus a crossed non-selectable `sprite_child`. Model
  creatures (`model_glb`) are their mesh at the appearance scale. "Update Sprite" re-reads the id.
  v4.6: own meshes without auto-tile or tilt are baked once per mesh fingerprint in object space (copies share one
  file, keep rot/scale; own-dir models keep their file name on re-export). "Trunk Collision" adds a parented `COL_*_trunk`
  box from the bottom 0.4 m footprint, 2.4 m tall, and turns the mesh's solid off. COL exports tag `unc_custom_id` so
  re-import skips them.
- **Fire** (`tools/build_fire_assets.py`: `python3` for the flame sheet and ember texture, `blender -b -P` for
  `fire_embers.glb` and `campfire.glb`). `content/props/prop_presets.json` gives every prop using a model a default
  emitter unless it sets its own (`ContentRegistry::ApplyPropPresets`, after edits). Emitter offset scales with the
  prop's scale, size with max(scale.x, scale.z), light radius with its square root. Noor's brief for a proper flame
  sheet: `docs/FIRE_SPRITE_BRIEF.md`. Maps may leave music/ambience empty (silent).
  Noor's flames arrived (10 frames of 64 px; main, small, magic; originals in art_source/fire/). Pieces: fire_embers,
  fire_embers_small, fire_embers_magic (teal coals texture embers_magic.png), campfire. build_fire_assets.py keeps her
  sheet unless --placeholder.
- **Noor's art package**: `python3 tools/import_art_package.py ZIP` (dry run) then `--apply`: portraits, spell/item icons,
  spell effects (alpha made hard) and the four model monsters (switched to sprite_8dir, then tools/import_package.py).
- **Portraits**: any assets/ui/portraits/<race>_<calling>_<n>.png appears in the creation picker (race+calling first);
  PlayerState.portrait is saved. Remaining art is listed in docs/NOOR_ART_BRIEF.md (tools/write_art_brief.py).
- **The Figure It Out Gang** uses Toasty's spin-off names: Baggy, Bread (was Rodrick), Badnee (Primrose), Karma (Agnes),
  Doobie (Snacks the owlbear). Internal ids are unchanged (npc.figure_rodrick etc.).
- **Updating Toasty's copy**: never "just game.exe" (content/assets go stale: an old placeholder dragon showed up). The
  add-on's "Move My Work to New Version" copies edrath_blender.json, assets/models/level, content/maps/custom and
  assets/models/custom into a freshly unzipped build and rebuilds its edrath_world.json = new base + changes.
- **Sprite packages:** `tools/import_package.py` (dry run, then `--apply`) imports a whole folder/zip of sheets.

### World textures (Noor's set, added 2026-11-03)

- 33 surface textures (128 px) in `assets/textures/`, skies in `assets/textures/sky/`, scatter cut-outs in
  `assets/sprites/scatter/`; previews in `art_source/textures/`; the brief is `docs/TEXTURES.md`.
- Textures are embedded in the .glb models. `tools/glb_textures.py swap <names>` re-embeds `assets/textures/<name>.png`
  into every model; `clone SRC DST old=new` makes a variant piece (`floor_<tex>.glb`, `wall_<tex>.glb`, `stairs_carpet.glb`).
- Per-area materials live in `tools/build_world.py` (`MATERIALS`: region-local prop id regex -> model; `OVERLAYS`: thin
  rugs/tiles), applied when regions are loaded, so the region builders stay untouched. `build_assets_art.py` no longer
  regenerates textures unless `--force-textures`.
- **Sky panoramas:** zones may set `sky_panorama` (`build_world.py` `SKIES`); drawn as a 360-degree horizon tinted by
  the zone's sky colour, faded by rain/fog, crossfading between zones. **Water** models (path contains water/pool)
  get `water_surface.png` with world-space, drifting UVs (`uWater`). **Scatter:** map `scatter` entries (sprite,
  pos, size, optional yaw for fixed quads such as cobwebs) generated by `build_scatter()` in `build_world.py`
  (seeded; only on allowed ground per area, clear of props, NPCs and interactables).

### Boss reagents and recipe books (added 2026-11-03)

- `tools/authoring/boss_crafting.py`: every boss guarantees a reagent (Rat King's Whisker, Archivist's Ink Heart, Ember of
  the Wrathful Host x2, the Warden's Silver Bell, Tooth of the Name-Eater, Dreaming Ink Sac x2, Grandmother's Bonnet
  Thread); the Wrathful Host, Dreaming Limb and Granny Wolf got their own loot tables.
- Recipes may set `book` (an item with `learn_recipe` effects). Reading it sets `recipe:<id>` flags (saved with flags);
  unknown recipes show greyed at the bottom of the bench list with the book's name. The list scrolls.
- Books: Hollis's Field Notes (Vaelen, 150: Whiskerblade, Hostbrand, Ink-Heart Quill, Fang of the Unwritten, Grandmother's
  Fighting Mittens), Sabrino's Forbidden Footnotes (Sabrino, 180: Ember Draught, Lullaby Tonic, Oil of Forgetting),
  Mother Brine's Greasy Recipe Card (Mother Brine, 40: Dreaming Calamari, Saltmere Fish Pie).

### A Druid in Distress (added 2026-11-03)

- `tools/authoring/druid.py` (tales_of_bellwether): a squirrel by the Old Oak is Bramble Thistlewick, Druid (Third Class),
  stuck since he sneezed mid-shapeshift. Bring an Acorn of the Old Oak (pickup under the oak), a glowcap and a tuft of
  Rolf's fur (new Rolf topic); the incantation is a rigged Lore roll (first try: goose; then DC 9, then DC 6). Restored
  (`druid_restored`), with antlers: he teaches **Barkskin** (buff_stat armour +8 / 40 s) and gives his spare squirrel tail.
- New dialogue condition `item_not_held`. Placeholder sprites `druid_squirrel.png`, `druid_bramble.png`.

### Campaign Four: The Dragon's Pension (added 2026-11-03)

- `tools/authoring/dragon_pension.py`, campaign `dragon_pension` (tales). Oakhaven topic `dp_start` -> Cindermaw the Elder
  lands in Bellwether's square (`dragon_arrived`), legally deceased after sleeping through 300 years of census letters.
  Proof of life: >=3 of 7 witness topics (`dwit_*`: Marta, Vaelen, Baggy, Hollis, Sabrino, Steve, Grout), the Register of
  Hatchings (Fenwick), a likeness (Pickering's box, used on the dragon). Oakhaven files Form 9-L (`dp_file`) -> hearing
  with Grubnik Quillsby, Esq. in the Records Office (present all three; optional Persuasion DC 13 for the confession) ->
  the Repossession Golem in the square (group -> 50) -> Cindermaw: Dragon's Sigh (fire nova) + Cindermaw's Scale + 250 g.
- Sprites are placeholders (the quadruped generator now has `dragon`: horns, spines, wings).
- **Part two, The Missing Third** (`tools/authoring/missing_third.py`, region `tools/build_seaside.py` -> `seaside_house.json`
  at SEASIDE_OFF, boat-only like the reef): Cindermaw topic `mt_start` -> Silas rows you (`mt_row1`, flag `at_seaside`, spawn
  `seaside_landing`; `mt_home` back) -> kobold bookkeepers + Quillsby (Cornered) (group -> 30, drops the vault key) -> locked
  vault door -> quest pedestal (the hoard, narration) -> Cindermaw `mt_done`: 400 g + Quillsby's Gloating Cufflinks.

## 8. The user (what they care about)

- **Story and immersion are the priority.** Bigger, multi-level spaces without loading screens. Better graphics/sprites welcome.
- Hates audible noise during tests (see §6). Plays on Windows; final builds must still work with MinGW there.
- Open-ended asks like "keep working on the game" are normal; pick high-value improvements, verify with the loop, report honestly.

## 9. Suggested next steps

1. Get the Linux build + `--selftest` green under Xvfb; record any fixes in this file.
2. ~~Marta acknowledges `found_ilse` and the clerk reacts to `seal_renewed`~~ — done (see §7).
3. More world: the mod's unused *Crimson Revenant* could guard a new area; Bellwether interiors (Fenwick's library upstairs).
4. Visual polish: textures are still simple 64×64 procedurals; the bread pickup and some props reuse generic models.
5. Combat feel needs a human play-test (sensitivity, swing timing, enemy windups).

### The Whistling Wood and Case File #3: The Horse Who Wasn't There (added 2026-11-03)

- **The Whistling Wood** (`tools/build_wood.py` → `content/regions/whistling_wood.json`, generated; WOOD_OFF = (-46, 0, 0))
  west of Bellwether through a new 3.2 m gap in the west wall (`bell_wall_west` is split in `build_world.py`; a short
  walled lane crosses the village's outer grass). Pines, a winding path, **the Old Oak** (models `oak_trunk.glb`, solid,
  and `oak_canopy.glb`, walk-under — the canopy carries a zero-area triangle at the origin because props anchor at their
  bounding-box bottom), Steve's camp (`tent.glb`, campfire), and Grandmother's ruined cottage (chest with the Red Hood).
  Models: `python tools/build_item_models.py wood_models`. Zone `whistling_wood`.
- **Sprites:** new `quadruped` kind in `build_sprites_prerendered.py` (horse with mane/blaze/saddle, or wolf with ruff;
  optional `bonnet`/`gown`), plus humanoid `hat: "pot"` and `weapon: "spoon"`. Sheets: `trout`, `grey_wolf`,
  `granny_wolf`, `steve`. Creatures `core:enemy.grey_wolf` and `core:enemy.granny_wolf` (beasts, loot `core:loot.wolf`).
- **Case File #3** (`core:quest.trout`, campaign `hollowmere_mysteries`, after Saltmere = 100): Hollis's horse Trout
  stopped coming when he whistles; a misspelled ransom note (item, readable; back of Steve's character sheet).
  Stage 10: gather ≥4 of the `trout_c_*` clues (readables: library-wall hoofprints in Bellwether, the boundary stone on
  the Old Road, a horseshoe on the Saltmere bollard, the wood's signpost, Steve's pinned drafts, Granny's note, the oak's
  hollow; interviews: Vaelen, Fenwick, Baggy, Oakhaven, Rolf, Ashgrave, Steve; Sabrino is a red herring). Deduce with
  Hollis: who wrote it (Steve — needs a Steve lead) and why she won't come (the oak whistles Hollis's whistle — needs
  `trout_c_whistle`) → stage 20, `trout_wood` (spawns 4 camp wolves, group flag `steve_safe`, and the granny wolf).
  Steve confesses, his ransom notes plug the hollow (`oak_plugged`, stage 30), you whistle and Trout comes, then goes
  home (Trout NPC beside Hollis). Steve's future: `steve_in_town` (moves to the Lantern Inn's Thursday table),
  `steve_honest` or `steve_scared`; all give Steve's Spoon (dagger: 30% crit, ×3, bane beast). Hollis → 100:
  Trout's First Horseshoe (accessory) and Hollis's Deck (book: the rules of 'Hmm'). Trout can be patted (+sanity).
  Authoring script: `tools/authoring/case3.py` (already run — do not rerun).
- Steve is canon now: a real bandit Oakhaven met nineteen years ago and wrote into his game. Keep that consistent.


### Hand-painted sprite sheets (added 2026-11-03, trial)

- The user's original sheets live in `art_source/spritesheets/` (see `art_source/README.md` for the mapping).

- `tools/import_spritesheet.py SRC DST --frame 128 --match OLD.png [--match-col N] --anim-from OLD.json --anim-out NEW.json`
  converts an external 8x6 sheet (same direction/row order as the engine) on a flat background: background removal by
  connectivity (flood fill from the border + flat enclosed pockets only, so dark paint inside a figure stays opaque),
  blob-to-cell assignment (limbs/tails crossing cell borders stay with their owner), one shared scale matched to the old
  sheet's in-frame height, feet on the pivot, and an animation JSON with the new frame size (world size is unchanged).
- In use (trial, from the user's own art): `grave_rat_painted.png` / `grave_rat_128.json` and `skeleton_painted.png` /
  `skeleton_128.json` for `core:enemy.grave_rat` and `core:enemy.restless_skeleton`; `crypt_keeper_painted.png`
  (Crypt Keeper, and the Lullaby Warden's `lullaby_warden_painted.png`, both on `crypt_keeper_128.json`) and
  `ash_crawler_painted.png` / `ash_crawler_128.json`; NPCs Kaelen (`ashbound_scout_painted.png`) and Brother Aldous
  (`brother_aldous_painted.png`), Oakhaven, Marta, Fenwick and the Erased Spirit (`*_painted.png`), all on
  `npc_standard_128.json`. The old generated sheets are kept; revert by pointing the
  creatures back at them. Blobs bigger than a cell (two figures touching) are split at their thinnest slice near the
  grid line.

### The Sleeper's Reef and "The Light Past the Fog" (added 2026-11-03)

- **Engine:** dialogue action `travel` (`spawn`): moves the player to a spawn in the current map (companions catch up
  as "lost" party members). Validation fails if no map has that spawn. Used for Silas's boat.
- **The Sleeper's Reef** (`tools/build_reef.py` → `content/regions/sleepers_reef.json`, generated; REEF_OFF =
  (1.6, 0, -150)): an island far out past Saltmere's fog, *not* connected on foot (low reef rim, sky = fog colour so the
  sea seems endless). Spawn `reef_landing`; return spawn `saltmere_pier` (in `build_docks.py`). Zone `sleepers_reef`
  (sanity drain 0.5). The drowned Saltmere Light: tower + two stone flights to a gallery at y 5.6, lamp, keeper's log.
  Six name-bottles (readables, `reef_*` flags), sleeping tentacles, the Gale brothers' fire.
- **Sprites:** new `tentacle` kind (`dreaming_limb`), plus `keeper_ondine`, `gale_elder`, `gale_younger`.
  Creature `core:enemy.dreaming_limb` (eldritch, rooted: move_speed 0.01, reach 3.6, sanity damage).
- **Quest `core:quest.reef`** (campaign `hollowmere_mysteries`, after Saltmere = 100): Silas (pier) → `r_row` (travel +
  3 narration cards; flags `at_reef`, `reef_trip`; stage 10) → bottles `reef_tom` + `reef_abel` → the brothers remember
  (20) → keeper Ondine Marsh: light the lamp (`lamp_lit`, 30) → the Dreaming Limb + 2 Drowned (group `limb` → 40,
  `limb_down`) → Ondine is relieved (`keeper_rests`, Keeper's Lantern, off-hand) → Silas at the jetty: the sons come home
  (travel back, `reef_done`, 100, the Drowned Man's Rhyme book). Tom and Abel then stand on the pier (`core:npc.tom_gale`,
  `core:npc.abel_gale`). Silas can row you out again any time (`at_reef` toggles the boat topics).
  Authoring script: `tools/authoring/reef.py` (already run — do not rerun). Trout is on the lighthouse gallery too.

### Mods (added 2026-11-03)

- With `--mods` / `enable_mods`, every `mods/<name>/manifest.json` loads in alphabetical order (previously only
  `example_mod`). Redefining an existing id replaces it (last wins), so mods can swap models and sprites. Guide for
  3D replacements: `docs/MODDING_3D.md`.

### Retro visuals pass (added 2026-11-03)

- **Post pass** (`assets/shaders/post.fs`, applied in `WorldRenderer::BlitToScreen`): soft glow around bright pixels
  (`glow`), ordered 4x4 Bayer dithering with 22-level colour banding on a ~360-line grid even at native resolution
  (`retro_dither`), and a light vignette. Options: Retro dithering / Glow.
- **World motion** (`world_lit.vs` uniforms `uTime`, `uSway`, `uWave`; option `world_motion`): models whose path
  contains `tree`/`canopy` sway (bend grows with height, phase from position), `water`/`pool` ripple, `tentacle`
  breathe slowly. Collision is unaffected (it uses the static bounds).
- **Weather `fireflies`** (pulsing emissive motes around the camera; the Whistling Wood) and **stars** in dark,
  clear, low-fog skies (none when raining or fog density >= 0.045).
- New graphics config keys: `retro_dither`, `glow`, `world_motion`. `--shot … --overlay options` shows the menu.
- **Screen effects** (`screen_effect` in graphics.json; Options → Screen effect): `crt` (Old TV: curvature, scanlines,
  RGB mask, tube edge), `vhs` (chroma bleed, wobble, rolling tracking band, noise, PLAY/counter/date overlay top-right),
  `fisheye` (strong barrel lens), `film` (sepia, grain, scratches, gate weave, dust), `handheld` (4-shade green LCD at
  144 lines). All in `post.fs`; the HUD is drawn afterwards, so it stays crisp.
  More: `noir` (hard B&W, grain, heavy vignette), `nightvision` (green gain, noise, REC/EMF/BATT overlay — the EMF
  reading is random, purely for show), `ega` (16-colour PC palette at 200 lines, saturation boosted before matching),
  `ale` (tavern-ale sway, breathing zoom, drifting double vision, warm vignette).

### Status effects, new spell types, "Overdue: The Restricted Section" (added 2026-11-03)

- **Creature statuses** (`CreatureInstance` burn/chill/frozen/shock/ink fields; `GameEngine::ApplyStatus`, `TryStatus`,
  `UpdateCreatureStatus`, `StatusDamage`): **burn** = damage per second (`status_power`), embers; **chill** = 55% speed,
  slower attacks/windups, 3 stacks (5 for bosses) freeze for 2.2 s (1 s); **shock** = +25% damage taken; **ink** =
  sight 2.5 m and 45% melee misses. Combos: fire on chilled/frozen = **Shatter**; shock on burning = **Overload**
  (3.5 m explosion). Bosses get 60% durations. Sprites are tinted per status.
- Sources: spell `effect.status / status_power / status_duration / status_chance`; weapon `on_hit_status /
  status_chance / status_power / status_duration` (melee heavy hits x1.5 chance; arrows carry it). Build bonuses
  `status_duration_bonus`, `status_chance_bonus`, `burn_damage_bonus`, `combo_damage_bonus`.
- New spell primitives: `chain` (`chain_count`, `chain_range`; 80% per jump, 6 m hops, LOS), `nova` (`radius`), `blink`
  (`blink_distance`, collision-safe). Dialogue action `learn_spell` (`spell_id`).
- Existing spells now apply statuses (Ember Bolt 35% burn, Frost Lance chill, Sabrino's Fireball burn, Siphon Ink 50% ink).
  New spells: Cold Shoulder (frost nova), Chain of Command (chain shock), Standing Ovation (shock nova, staggers), Slow
  Burn (DoT bolt), [REDACTED] (ink bolt), Clerical Error (blink). Vaelen sells the Cinderglass Dagger (burn), Rimecaller
  Mace (chill) and the Storm-Clerk's Stamp (+35% combo). Synergy **Thermal Paperwork** (Elemental 14 + Illusion 8).
- **Quest `core:quest.overdue`** (tales_of_bellwether): Fenwick's black ledger; grimoires from Ashgrave (persuasion
  option), Pickering, Odette, Mother Brine, Brother Aldous, Oakhaven (filed under Q). Returning each teaches its spell;
  all six = Fenwick's Library Card (accessory). Authoring: `tools/authoring/grimoires.py` (already run — do not rerun).
- `--shot … --overlay status_demo` lines up four wolves with each status.

### Perks (added 2026-11-03)

- `content/perks/perks.json` (manifest key `perks`; `PerkDef`): combat/magic skills have milestones at 15/25/40,
  utility skills at 15/30; two perks per milestone, choose one (`PerkAvailable`, `ChoosePerk`, `PendingPerks`;
  `player.perks`, saved). Perk `bonuses` feed `Bonus()` like gear/synergies. Validation: perk skill exists, every
  milestone has ≥2 options. Character screen → **Perks** tab (count of pending choices on the tab).
- New mechanical bonus keys: `heal_on_kill`, `mana_on_kill`, `burn_spread_on_death`, `chain_jump_bonus`,
  `nova_radius_bonus`, `freeze_stacks_reduction`, `shock_damage_bonus`, `opener_damage_bonus` (vs unhurt foes),
  `desperation_damage_bonus` (below 35% hp), `sneak_damage_bonus`, `heavy_damage_bonus`, `crit_burn`,
  `spell_cooldown_reduction`, `heal_power_bonus` (heals + wards), `blink_distance_bonus`, `block_reduction_bonus`,
  `block_stamina_reduction`, `potion_bonus`, `gold_find_bonus`, `companion_damage_bonus`, `skill_xp_bonus`,
  `sneak_visibility_reduction`.
- Dialogue actions `take_gold`, `reset_perks`; Brother Aldous's "Rite of Second Thoughts" (50 gold) resets perks.
  Authoring: `tools/authoring/perks.py` (already run — do not rerun). `--shot … --overlay perks`.

### Gathering, alchemy, workbench (added 2026-11-03; was the user's planned request)

The user asked for "stuff to do besides quests — gathering, alchemy, basic crafting, to bring some life to the
world", to come after spells/character building. Ideas that fit the existing systems: harvestable herb/mushroom/ore
nodes per region (respawning), an alchemy table (Mother Brine / Fenwick?) making potions and status-themed
tonics (burn/chill oils that add `on_hit_status` to weapons for a while; resist potions), a simple workbench (arrows,
lockpicks, upgrading weapon base damage), fishing at Saltmere, and recipes as readable books.

### Roguelike pack: bleed, confuse, charm, knock, buff_stat, wands (added 2026-11-03)

Inspired by classic roguelikes such as Barony (mechanics only; names, writing and code are our own).
- Statuses: **bleed** (stacks to 3, `status_power` × stacks per second, blood drips), **confuse** (wanders; attacks the
  nearest creature in reach, friend or foe; bosses half duration), **charm** (fights the nearest non-charmed creature,
  follows you otherwise; bosses immune; hitting it ends the charm and it turns on you). Creature-vs-creature hits go
  through `CreatureHitCreature` (2× the attacker's damage; the victim's `foe` makes it fight back). Companions ignore
  charmed creatures. Tints: charm pink, confuse flickering violet, bleed reddened.
- Spell primitives: `knock` (nearest locked door/chest you face within 6 m, if `lock_difficulty` ≤ power), `buff_stat`
  (`bonus_key`, `bonus_value`, `duration_seconds`; stored as an ActiveBuff so `Bonus()` sees it). `CastSpell(spell,
  freeCast)` is the shared cast path.
- Wands: consumables with effect `cast_spell` (`spell_id`); the stack size is the charge count; quick-slot friendly.
- New spells: Bewilder, Sudden Friendship, Unauthorised Entry, Borrowed Vitality, Late for an Appointment, Paper Storm
  (tomes in loot/Vaelen; Ashgrave gives Borrowed Vitality if you're honest about his poetry). Wands of Sparks, Frost,
  Bewilderment, Sudden Friendship, Unauthorised Entry. Weapons: Serrated Cleaver and Thornbow (bleed), the Sword of
  Mild Inconvenience (confuse). Authoring: `tools/authoring/roguelike.py` (already run — do not rerun).
  `--shot … --overlay status_demo2` shows charm/confuse/bleed.

- **Done:** interactable types `harvest` (`item_id`, `qty`..`qty_max`, `respawn_seconds` of play time; picked nodes vanish,
  `MapPersist.harvested` saves when) and `station` (`station`: alchemy / workbench → `Overlay::Crafting`).
  `content/recipes/recipes.json` (manifest `recipes`; `RecipeDef`: station, result, qty, ingredients, skill,
  skill_level); `CanCraft` / `Craft`. Item effects `weapon_oil` (`stat` = status, `value` = chance, `amount` = power,
  `duration`; one oil at a time; melee and arrows) and `consumable_sanity`. Validation checks recipe and harvest items.
- 10 materials (marigold, wayside sage, wolfsbane, glowcap, grave moss, bladderwrack, sea salt, iron ore, ashwood
  branch, pine resin) placed per region (40 nodes; models `python tools/build_item_models.py harvest_models`). Alchemy
  benches: Lantern Inn and Mother Brine's tavern; Workbench by Vaelen. 11 alchemy recipes (potions, five weapon oils,
  Quiet Mind Tea, Hunter's Draught, Bureaucrat's Brew), 6 workbench recipes (arrows, lockpicks, whetstones, three wands).
  Authoring: `tools/authoring/crafting.py` (already run — do not rerun; it also injected node blocks into the region
  builder scripts). `--shot … --overlay crafting`.
- **Fishing** (interactable type `fishing`, `loot_table`; needs `core:item.fishing_rod` from Silas or Vaelen): cast, a
  random wait (shorter with Perception), then a ~0.75 s bite window to press interact; too early or too late and it's
  gone; moving or attacking reels in (`StartFishing`/`UpdateFishing`/`FishPress`/`CatchFish`). Spots: Saltmere piers
  and quay, the Reef jetty, a new pond in the Whistling Wood. Loot tables `fish_harbour`, `fish_reef`, `fish_pond`
  (cod, mackerel, perch, a trout (fish), eldritch eel, old boot, grumpy frog, glimmering pearl, message in a bottle).
- **Cooking** (station `cooking`: Marta's hearth in the Lantern Inn, Mother Brine's pot): six meals with build buffs.
  Authoring: `tools/authoring/fishing.py` (already run — do not rerun). `--shot … --overlay fishing`.
- Not yet: recipes found as books, rare reagents from bosses.

### Dungeons & Debtors III: The Mimic Who Wanted to Be a Real Chest (added 2026-11-03)

- Three sessions (`core:quest.mimic_s1..s3`, campaign `dungeons_debtors`, after `lich_s4` = 100) on Oakhaven's greeting:
  Chester's Form C-1 and the troll bridge (class moves, a persuasion roll, Gerald's audit); the Container Convention (a
  stolen Golden Key, Chester framed, Baggington investigates; Lord Strongbox turns out to be a mimic himself); the
  Royal Board's trials (Capacity, Character, Composure). If `steve_in_town`, Steve plays in person (a bard called Steve)
  and opens Chester; otherwise Steve posts his moves and **Kaelen** puts down the quill to open Chester. Oakhaven
  doesn't roll for the last bit. `mimic_win_1..6` (≥4 → `mimic_legend`).
- Rewards: Chester's Cousin (satchel accessory: `carry_capacity_bonus` 30 — new bonus key — and +15% gold) and the
  Ten-Foot Pole (reach 3.3 m). Oakhaven teases Campaign Four (a dragon's pension paperwork).
  Authoring: `tools/authoring/mimic_campaign.py` (already run — do not rerun).


### Day and night (added 2026-11-03)

- `PlayerState.hour` (0-24, saved; new games start at 21:00) advances while playing: a day takes
  `game.json` `day_length_minutes` real minutes (default 48; Options "Length of a day": 24/48/96 min, 3 h, clock stopped).
- Outdoor zones (those with a `sky_panorama`, or `day_night: true` on a zone or map) treat their authored look as the
  night and blend towards an overcast day (`DayNightLook` in GameEngine.cpp) with warm dawn (5-7) and dusk (18.5-20.5);
  the sun direction follows the hour. Panorama: authored at night, `sky_dusk.png` at twilight, `sky_day.png` by day
  (a placeholder recoloured from Noor's night sky; a real one is in her brief). Fireflies only at night; stars hide
  when the sky is bright. Indoor zones never change.
- `night_outdoors_`: monster sight x0.75 at night outdoors. NPC spawns take `"hours": [from, to]` (wraps past midnight).
- **T** opens Wait (1 h, 3 h, until 7:00, 19:00, midnight); refused when an alerted enemy is within 30 m; restores
  stamina and advances play_time so gathering nodes regrow. HUD clock top right. `--hour h` for screenshots.

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

- `tools/import_spritesheet.py SRC DST --frame 128 --match OLD.png [--match-col N] --anim-from OLD.json --anim-out NEW.json`
  converts an external 8x6 sheet (same direction/row order as the engine) on a flat background: soft background removal,
  blob-to-cell assignment (limbs/tails crossing cell borders stay with their owner), one shared scale matched to the old
  sheet's in-frame height, feet on the pivot, and an animation JSON with the new frame size (world size is unchanged).
- In use (trial, from the user's own art): `grave_rat_painted.png` / `grave_rat_128.json` and `skeleton_painted.png` /
  `skeleton_128.json` for `core:enemy.grave_rat` and `core:enemy.restless_skeleton`; `crypt_keeper_painted.png`
  (Crypt Keeper, and the Lullaby Warden's `lullaby_warden_painted.png`, both on `crypt_keeper_128.json`) and
  `ash_crawler_painted.png` / `ash_crawler_128.json`; NPCs Kaelen (`ashbound_scout_painted.png`) and Brother Aldous
  (`brother_aldous_painted.png`), both on `npc_standard_128.json`. The old generated sheets are kept; revert by pointing the
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


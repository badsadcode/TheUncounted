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
- `--validate` → 0 errors; `--selftest` → 0 failures (158 checks); `--balance` → every calling beats every creature
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

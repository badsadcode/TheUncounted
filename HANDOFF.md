# HANDOFF — The Uncounted (for the next/cloud session)

You are picking up a first-person, data-driven action RPG written in C++20 on raylib 5.5. Everything below is what
the previous session (Windows desktop, MinGW) knew and you won't: read this file first, then `README.md` and
`docs/ARCHITECTURE.md`.

## 1. State at handoff (2026-11-02)

- **Playable start to finish.** Chapter Zero, *Legally Deceased*: character creation → prologue → Bellwether →
  Old Road → underground Registry Annex → boss → two endings. Plus two side quests and a two-level optional dungeon.
- **One seamless world, no loading screens.** `core:map.edrath` is composed from five region files. The Annex sits
  under the Old Road; Vault III sits under the Annex's crypt (three storeys of descent via walkable stairs).
- **Verified on Windows and Linux.** `--validate` → 0 errors; `--selftest` → 0 failures (now ~100 checks); `--balance` →
  every calling beats every creature (36/36 at 100%). Linux (Ubuntu 24.04, GCC 13.3, Xvfb + Mesa) verified 2026-11-02.
- **Not play-tested by a human for feel.** Everything was verified by headless tests and screenshots.

## 2. First steps in a Linux cloud box

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

# THE UNCOUNTED — Technical Architecture & Content Schema Specification

## 1. Overview & Philosophy
*The Uncounted* is a standalone, single-player, first-person action RPG set in Edrath. In strict accordance with the design specification:
- **No bulky prebuilt engines** (no Unity, Unreal, or Godot).
- **Zero hardcoded or procedurally synthesized art assets in the runtime binary.** Every mesh (`.glb`), texture (`.png`), sprite sheet (`.png` + `.json`), UI icon (`.png`), font (`.ttf`), shader (`.vs`/`.fs`), and sound/music clip (`.wav`/`.ogg`) is an external, replaceable file on disk.
- **Data-driven architecture:** The C++20 executable (`game.exe`) is strictly an interpreter of external JSON definitions (`content/`, `config/`, `mods/`) and external assets (`assets/`).

---

## 2. Technology Stack & Licenses
| Component | Technology | License | Role |
|---|---|---|---|
| Core Language | **C++20** | Standard | Gameplay systems, ECS/entity state, AI, combat, quests, validation |
| Platform / Renderer / Audio | **raylib 5.5** (incl. `rlgl`, `raymath`, `cgltf`, `miniaudio`) | zlib/libpng | Windowing, OpenGL 3.3 context, GLB loading, audio playback, input |
| JSON Parser | **nlohmann/json 3.11.3** | MIT | Parsing and serializing config, content definitions, and save files |
| Build System | **CMake 3.20+** (MinGW-w64 GCC 13 / MSVC 2022) | BSD-3 | Reproducible cross-compiler builds |
| Asset Authoring | **Blender 4.x/5.x** + **Python** offline scripts (`tools/`) | GPL / MIT | Offline authoring of replaceable `.glb`, `.png`, and `.wav` files |

---

## 3. Directory Structure
```text
TheUncounted/
├── game.exe                        # Compiled C++20 runtime interpreter
├── CMakeLists.txt                  # Build configuration
├── README.md                       # Build, run, controls, and overview documentation
├── docs/
│   ├── ARCHITECTURE.md             # System architecture and schema specifications
│   └── MODDING_GUIDE.md            # Step-by-step guide to swapping assets and adding content
├── config/
│   ├── graphics.json               # Window size, internal resolution (320x180, 426x240, 640x360, native), FOV, filtering
│   ├── controls.json               # Keybindings, mouse sensitivity, invert Y, head bob
│   └── game.json                   # Difficulty tuning, audio volume sliders, default language
├── content/
│   ├── manifest.json               # Ordered list of content files to load and validate
│   ├── localization/               # String tables (e.g., en.json) — no hardcoded gameplay text in C++
│   ├── attributes/                 # Might, Agility, Endurance, Intellect, Will, Presence definitions
│   ├── races/                      # Human, Dwarf, Elf, Orc, Halfling definitions & traits
│   ├── backgrounds/                # Character backgrounds & starting lore/social flags
│   ├── archetypes/                 # Warrior, Ranger, Mage, Rogue, Cleric, Adventurer starting packages
│   ├── skills/                     # Use-improved skills (Combat, Magic, Exploration, Social)
│   ├── synergies/                  # Data-driven skill combinations (e.g., Flame Blade, Shadow Step)
│   ├── spells/                     # Spell definitions using reusable effect primitives
│   ├── items/                      # Weapons, bows, ammo, armor, potions, books, keys, quest items
│   ├── loot_tables/                # Weighted drop tables for enemies and containers
│   ├── creatures/                  # Enemy stats, AI behavior profiles, attacks, perception, sprite/GLB refs
│   ├── npcs/                       # NPC definitions, schedules/idle stances, dialogue & vendor links
│   ├── factions/                   # Royal Bureau of Records, Church of the Last Dawn, Ashbound, Candle Collegium
│   ├── dialogue/                   # Branching conversation trees with conditions and actions
│   ├── quests/                     # Quest stages, journal entries, objectives, completion rewards
│   ├── maps/                       # Region scenes: Bellwether, Old Road, Registry Annex / Forgotten Crypt
│   └── balancing/                  # Global combat, stamina, leveling, and anti-exploit skill curves
├── assets/
│   ├── textures/                   # Tileable pixel-art environment textures (.png)
│   ├── models/                     # Architectural pieces, props, weapons, and 3D entities (.glb)
│   ├── sprites/                    # 8-directional & animated billboards for creatures, NPCs, VFX (.png)
│   ├── animations/                 # Sprite frame rect, pivot, timing, and direction metadata (.json)
│   ├── audio/
│   │   ├── music/                  # Regional atmospheric music tracks (.wav)
│   │   ├── ambience/               # Looping environmental soundscapes (.wav)
│   │   └── sfx/                    # Combat, footsteps, doors, spells, UI audio (.wav)
│   ├── fonts/                      # Replaceable TrueType fonts (.ttf)
│   ├── ui/                         # HUD frames, icons, crosshair, portraits, panels (.png)
│   └── shaders/                    # External GLSL vertex/fragment shaders (lighting, fog, postprocess)
├── mods/
│   └── example_mod/                # Working mod demonstrating asset replacement & new content without recompile
├── saves/                          # Atomic versioned JSON save files (slot_1.json, autosave.json, .bak)
└── tools/                          # Offline Blender/Python tools used to author the external asset pack
```

---

## 4. Modular Engine Architecture (`src/`)

1. **`core/` (`Types.h`, `Logger.h`, `Config.h`)**
   - Structured logging with severity levels (`INFO`, `WARN`, `ERROR`, `VALIDATION`) and in-game diagnostic overlay.
   - Configuration loader/saver for `config/graphics.json`, `config/controls.json`, and `config/game.json`.
   - Fixed simulation timestep accumulator (`dt = 1.0f / 60.0f`) decoupled from variable render framerate.

2. **`resource/` (`ResourceManager.h/.cpp`)**
   - Central cache mapping file paths to loaded GPU/audio resources (`Texture2D`, `Model`, `Shader`, `Sound`, `Music`, `Font`).
   - Applies user-selected texture filtering (`TEXTURE_FILTER_POINT` by default for crisp pixel art, or `BILINEAR` if toggled).
   - If a referenced file is missing or corrupt, logs a clear diagnostic error (`file path + offending key + explanation`) and substitutes an external diagnostic fallback asset (`assets/textures/diag_missing.png` or `assets/models/diag_missing.glb`) rather than crashing silently or synthesizing art in code.
   - Supports runtime **Dev Hot-Reload (`F5`)** to reload modified JSON definitions, textures, and shaders on the fly.

3. **`content/` (`ContentRegistry.h/.cpp`, `ContentValidator.h/.cpp`)**
   - Loads `content/manifest.json` followed by any enabled mod manifests in `mods/*/manifest.json`.
   - Parses all namespaced IDs (`core:item.*`, `core:enemy.*`, `core:spell.*`, `core:map.*`, etc.). Mods can override existing IDs or register new ones.
   - **Cross-Reference & Schema Validator:** At startup (and on `--validate` or `F5`), verifies that every required JSON field is present, types match, and every cross-referenced ID (`loot_table`, `key_id`, `destination_map`, `dialogue_id`, `spell_id`, `icon`, `world_model`, `sprite_sheet`, `audio`) resolves to an existing definition or file on disk.

4. **`renderer/` (`WorldRenderer.h/.cpp`)**
   - Renders the 3D world to an offscreen framebuffer (`RenderTexture2D`) at the configured internal resolution (`320x180`, `426x240`, `640x360`, or `native`), then scales cleanly to the window with nearest-neighbor integer/aspect-preserving scaling.
   - **External Shader (`assets/shaders/world_lit.vs`, `assets/shaders/world_lit.fs`):** Computes dynamic point lights (torches, crystals, spell projectiles, `Glimmer` light buff), directional/ambient hemisphere lighting, and exponential distance fog.
   - **Hybrid Entity Rendering:** Entities declare `"appearance": {"type": "sprite_8dir" | "sprite_billboard" | "model_glb"}` in JSON. The renderer draws GLB meshes or depth-sorted directional/animated 2D sprites in 3D space accordingly, plus a first-person weapon/spell viewmodel rig.
   - **UI Pass:** Drawn at crisp window resolution (scaled by `ui_scale`) over the 3D viewport using external `.ttf` fonts and `.png` icons/panels.

5. **`world/` (`SceneManager.h/.cpp`, `Collision.h/.cpp`)**
   - Instantiates map geometry, props, doors, containers, levers, pressure plates, portals, point lights, NPCs, and creatures from `content/maps/*.json`.
   - Continuous 3D AABB/cylinder-vs-world collision detection with sliding wall response, step-up handling for stairs, floor height queries, and raycast line-of-sight / interaction queries.
   - Preserves persistent per-map state (unlocked doors, toggled levers, looted containers, defeated unique enemies, dropped items) across region transitions and save/load.

6. **`gameplay/` (`Player.h/.cpp`, `CombatSystem.h/.cpp`, `AISystem.h/.cpp`, `QuestSystem.h/.cpp`, `DialogueSystem.h/.cpp`, `SaveSystem.h/.cpp`)**
   - **Classless Character Progression:** Tracks race traits, background, 6 attributes, derived stats (Health, Stamina, Mana, Carry Weight, Armor, Move Speed), use-based skill XP with anti-exploit challenge scaling, and data-driven skill synergies.
   - **Real-Time Combat:** Light/heavy melee swings with reach & arc checks, active blocking/parry, bow drawing & physical arrow projectiles with retrieval, and data-driven spell casting (`projectile_damage`, `self_heal`, `buff_armor`, `buff_light`, `buff_stealth`).
   - **Enemy AI:** State machine (`Idle`, `Patrol`, `Notice`, `Approach`, `Attack` with telegraph windup, `Stagger`, `Search`, `Dead`) using 3D line-of-sight raycasts so enemies never see or attack through walls.
   - **Quests, Dialogue & Economy:** Condition evaluator (`has_item`, `quest_stage`, `flag_set`, `race_is`, `skill_at_least`, `gold_at_least`) and action executor (`set_quest_stage`, `set_flag`, `give_item`, `take_item`, `give_xp`, `give_gold`, `open_shop`, `heal_player`).
   - **Atomic Save/Load:** Writes versioned JSON to `saves/slot_X.json.tmp`, creates a `.bak` backup of the previous save, and atomically renames the file.

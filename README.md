# The Uncounted — Chapter Zero: Legally Deceased

A data-driven, first-person action RPG built on raylib 5.5 and C++20. The executable interprets JSON content
(`content/`, `config/`, `mods/`) and external assets (`assets/`); see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

Continuing development (e.g. in a cloud session)? Start with [HANDOFF.md](HANDOFF.md).

## Build

**Target platform: Windows 10/11.** Requires CMake 3.20+ and MinGW-w64 GCC 13 (or MSVC 2022).

```bash
cmake -S . -B build -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release
```

```bash
cmake --build build -j 8
```

`game.exe` is written to the project root. MinGW builds link the runtime statically, so it runs without the toolchain on `PATH`.

## Run

```bash
./game.exe
```

| Flag | Purpose |
|---|---|
| `--validate` | Load and cross-validate all content, print issues, exit (non-zero on errors) |
| `--selftest` | Headless walkthrough of the whole chapter (dialogue, keys, lever, plate, boss, pedestal, save/load, ending); exit code 0 = all passed |
| `--shot out.png [--map id] [--spawn id] [--pos x y z] [--yaw deg] [--pitch deg] [--arch n] [--overlay inventory\|character\|journal\|map\|dialogue\|dialogue:<npc id>:<node>\|reader:<item id>\|ending\|combat\|compare\|title\|creation\|prologue\|story] [--frames n]` | Render a frame and save a screenshot (used for visual checks) |
| `--balance` | Headless duels of every starting calling vs every creature; prints win rate, time-to-kill, HP left and potions used to the log |
| `--showcase` | With `--shot`: lines up every wearable/consumable pickup and sample hit particles in front of the camera |
| `--mods` | Enable `mods/example_mod` for this run |
| `--mute` | Run without audio (automated modes — `--selftest`, `--balance`, `--shot` — are always silent) |

## Controls (rebind in `config/controls.json`)

| Action | Key |
|---|---|
| Move / sprint / sneak / jump | WASD / Shift / Ctrl (hold) / Space |
| Interact, take all | E |
| Attack (hold for heavy), draw bow | Left mouse |
| Block (tap just before a hit to parry) | Right mouse |
| Cast spell / next spell | Q / R (or mouse wheel) |
| Quick slots | 1–4 (hover a consumable in the inventory and press 1–4 to assign) |
| Inventory / character / journal / map | I / C / J / M |
| Quick save / quick load | F6 / F9 |
| Hot-reload content & shaders / debug overlay | F5 / F3 |
| Pause | Esc |

## World & story

- **One seamless world.** `content/maps/edrath_world.json` is composed by `python tools/build_world.py` from the
  hand-authored regions in `content/regions/` (Bellwether, the Old Road, the Registry Annex). The Annex lies
  underground: walk through the cliff arch at the end of the road and down the stairs. Below it, through a gap in
  the crypt's west wall, two more levels descend: **Vault III, the Nursery** and **the Seal Chamber** (quest
  *The Sleepers of Vault III*). Re-run the composer after editing a region.
- **Zones** (`"zones"` in a map) give parts of one map their own name, sky, light, fog, weather, music and ambience;
  the engine blends them spatially and crossfades the audio, and the map screen shows only your zone and storey.
- **Story systems:** a prologue (`story.prologue.N` strings), ambient NPC `barks` (optionally gated by quest stage, or by a story `flag` / `not_flag`),
  creature `lines` (`alert` / `death`, shown as subtitles), and readables that advance quests (`quest_id` + `set_stage`).
  Side quest *A Name Worth Keeping* starts at Oakhallow's boundary stone on the Old Road.
- **Music & ambience** are composed offline by `python tools/build_music_ambience.py` (long, drone-free, seamless loops).

## Content notes

- Map props are anchored at their bounding-box bottom centre; ground slabs sit with their top at about y = 0.
- Dialogue conditions: `quest_stage_equals`, `quest_stage_at_least`, `quest_stage_below`, `has_item`, `race_is`,
  `skill_at_least`, `flag_set`, `flag_not_set`, `gold_at_least`. Quest stages only move forward, and `give_item` /
  `give_gold` / `give_xp` rewards in a dialogue node or choice are paid out once per save.
- Interactables may set `scale`, `set_flag`, `narration` (localization keys shown as full-screen cards after use) and
  `requires_dead` (a creature instance that must be defeated first). A zone's `flag_override` (`flag`, `weather`,
  `ambience`) changes it once a story flag is set; signing the Seal stops Bellwether's rain this way.
- Props may set `"ramp": "+x" | "-x" | "+z" | "-z"` to become a walkable slope rising in that direction (stairs).
- Props may carry an `emitter` (`sprite`, `offset`, `size`, `light_color`, `light_radius`) — wall torches use it for
  animated flames with their own light. Maps may set `"weather": "rain"` (skipped under roofs) or `"dust"`.
- Weapons may set `crit_chance`, `crit_mult`, `life_steal`, `mana_on_hit` and `bane_family`/`bane_mult` (vs a creature's
  `family`). Items may grant named build bonuses with `{"type": "bonus", "stat": "crit_chance_bonus", "value": 0.05}`;
  synergies use the same keys. Spells may set `splash_radius` and `drain_fraction`. The character screen's Combat Sheet
  shows every derived number.
- Creatures may set `hit_fx` (`color`, `glow`) for the particles they shed when struck.
- Enemies are staggered by heavy attacks or blows dealing 35%+ of their health, then get 2 s of stagger immunity;
  elites (`*guardian*`) only stagger from heavy attacks and bosses never do. Armour subtracts 60% of its value per hit.
- Small item models (bread, garments, boots, helm, rings) are built by `python tools/build_item_models.py`
  (flat-shaded vertex-coloured GLBs, no textures).
- Character sprites are pre-rendered by `tools/build_sprites_prerendered.py` (SDF models raymarched from 8 directions,
  cel-shaded and outlined). Edit a style in `SHEETS` and run `python tools/build_sprites_prerendered.py [name-filter]`.

# Building and editing levels in Blender

Rearrange the world, add doors, chests, NPCs and monsters, and model your own pieces (proper roofs, door frames,
arches, whole buildings) in Blender, then play your changes straight away.

Your work is saved in its own folder, `mods/level_edits/` (the `map_edits.json` file plus a `models/` folder for your own
models). Game updates never overwrite it. Send that folder to the developer to make it a permanent part of the game.

## One-time setup

1. Install **Blender 4.0 or newer** (free, blender.org).
2. In Blender: **Edit → Preferences → Add-ons → Install...** and pick `tools/blender/uncounted_level_editor.py` from the
   game folder. Tick **The Uncounted: Level Editor**.
3. Start a new **General** scene and delete the default cube, camera and light (**A** to select all, then **X**).
4. In the 3D view press **N** and click the **Uncounted** tab. Set **Game folder** to the folder with `game.exe`.

## The workflow

1. **Import World**. The whole world appears with its real models and textures, plus your earlier edits. It's in three
   collections:
   - **Uncounted World**: every wall, floor, roof, prop and tree, named with the game's ids.
   - **Uncounted Objects**: doors, chests, levers and signs as their real models; pickups as cubes; NPCs as arrows;
     monsters as spheres. All are labelled.
   - **Uncounted Palette**, beside the world (+Y): one of every building piece, plus a row of **templates**: door, locked
     door, gate, chest, lever, sign, pickup, NPC and monster.
2. **Edit** with normal Blender tools (table below).
3. **Export Edits**. The status bar shows what was saved.
4. Start the game.

Run **Import World** again whenever you like. It rebuilds the scene from the game's level plus your saved edits, and
your own models stay as you left them.

| To... | Do this |
|---|---|
| Move | **G** (then **X**/**Y**/**Z** to lock an axis; hold **Ctrl** to snap: great for closing gaps between walls) |
| Turn | **R**, then **Z**: the game only turns things around the vertical axis |
| Stretch / resize | **S** (or **S**, **X** to stretch along one axis: walls and floors are stretched boxes) |
| Copy | **Shift+D** |
| Delete | **X** |
| Add a wall/floor/prop | find it in the Palette, **Shift+D**, move it into the world |
| Add a door, chest, lever, sign, pickup, NPC or monster | **Shift+D** its template from the Palette, move it, then fill in its settings |
| Change settings | select it: the **game_** fields appear in the sidebar (also in Object Properties → Custom Properties) |
| Undo | **Ctrl+Z** |

## Settings you can change (the game_ fields)

- **Doors**: `locked` (on/off), `key_id` (the item that opens it, for example `core:item.annex_key`), `lock_difficulty`
  (lockpicking, 1 to 30), `prompt` (what the game shows: "Open *prompt*").
- **Chests**: `loot_table` (for example `core:loot.crypt_basic`), `locked`, `lock_difficulty`.
- **Levers**: `target_id` (the id of the gate or door it opens, for example `edit_gate_4`).
- **Signs (readables)**: `prompt`, `title`, `text`.
- **Pickups**: `item_id`, `qty`.
- **NPCs**: `npc_id` (who it is, for example `core:npc.figure_snacks`). **Monsters**: `creature_id` (for example
  `core:enemy.grey_wolf`). A monster patrols the same route relative to wherever you put it.
- **Walls, floors, props**: `solid` (can you walk through it?), `uv_x` / `uv_y` (how many times the texture repeats).
- Fields ending in `_flag` control when things appear or vanish in the story. Leave them alone unless you know the flag.
- Ids of the game's items, monsters and NPCs are in `content/items`, `content/creatures` and `content/npcs`.

## Your own models (roofs, door frames, buildings...)

Any mesh you make yourself (**Add → Mesh**, then edit it in Edit Mode, extrude, bevel...) becomes a game piece when you
export. Put it in any collection; hidden meshes are skipped.

- **Textures**: give it one of the materials that came in with the imported pieces (Material tab → browse: look for
  names such as roof shingles, wood planks, stone wall). Those are the game's own textures. UV-unwrap it (**U → Smart UV
  Project**) so the texture lies nicely.
- **Solid or not**: the game blocks the player with the model's bounding box. That's fine for walls, frames and roofs
  overhead. For arches you walk through, build the posts and the top as separate meshes.
- Each model is saved as `mods/level_edits/models/<name>.glb`. Keep the object's name stable and it keeps the same file.

## Good to know

- **Textures look stretched in Blender** on big walls and floors. The game tiles them, so ignore it.
- **Doors and gaps**: doors are 1.84 m wide and 2.8 m tall. Move the walls in (with snapping) or model a frame around them.
- **Tilting** something (rotating around X or Y) isn't kept, and Export warns you.
- **Undo everything**: delete or rename `mods/level_edits`.
- **Updating the game**: copy your `mods/level_edits` folder into the new game folder.
- Coordinates: the game is Y-up and Blender is Z-up. The add-on converts between them; you never need to.

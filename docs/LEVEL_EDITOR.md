# Building and editing levels in Blender

Rearrange the world, add doors, chests, NPCs and monsters, model your own pieces (proper roofs, door frames, arches,
whole buildings), or build a **brand-new map** from scratch in Blender, then play it straight away.

The add-on has two modes (the buttons at the top of the **Uncounted** tab):

- **Edit World** changes the game's own level: Export saves straight into `content/maps/edrath_world.json`, the file
  the game plays. Your own models go to `assets/models/level/`.
- **New Map** builds a new map for the game: `content/maps/custom/<map name>/map.json`, models in
  `assets/models/custom/<map name>/`.

Nothing is a mod: it's the game's real level. Behind the scenes Export also keeps a list of your changes
(`content/maps/edrath_blender.json`, measured against `edrath_world.base.json`, the level before Blender). That way, when
the developer rebuilds the world from its source, your changes are put back on top instead of lost.

**Getting your changes into the official game**: press **Pack My Changes**. It makes `my_level_changes.zip` in the game
folder with everything you changed. Send that zip to the developer. Do this before you download a new version of the
game, because unzipping a new version over your folder replaces the level files.

## Seeing it as it looks in the game

Import switches the 3D view to **Material Preview**, with textures repeated exactly as the game repeats them (walls and
floors are stretched boxes whose texture repeats `uv_x` × `uv_y` times). If the view goes grey or untextured, press
**Z** in the 3D view and pick **Material Preview**. Pixels stay sharp (no blur), like the game. Lighting in Blender is
brighter than the game's night, so judge colours in the game.

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
     door, gate, chest, lever, sign, pickup, NPC, monster, portal and spawn point.
2. **Edit** with normal Blender tools (table below).
3. **Export**. The status bar shows what was saved.
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
- **Portals** (the cones): `destination_map` (a map id: `core:map.edrath` for the game's world, `core:map.<name>` for
  yours), `destination_spawn` (a spawn point in that map), `prompt` (shown as "[E] *prompt*"), `radius` (how close you
  must stand). A portal is an invisible spot: put a door, archway or stairs model on it so players see where to go.
- Fields ending in `_flag` control when things appear or vanish in the story. Leave them alone unless you know the flag.
- Ids of the game's items, monsters and NPCs are in `content/items`, `content/creatures` and `content/npcs`.

## Your own models (roofs, door frames, buildings...)

Any mesh you make yourself (**Add → Mesh**, then edit it in Edit Mode, extrude, bevel...) becomes a game piece when you
export. Put it in any collection; hidden meshes are skipped.

- **Textures**: give it one of the materials that came in with the imported pieces (Material tab → browse: look for
  names such as roof shingles, wood planks, stone wall). Those are the game's own textures. UV-unwrap it (**U → Smart UV
  Project**) so the texture lies nicely.
- **Texture size (m)** in the sidebar: the texture repeats every this many metres, however big the mesh is, like the
  game's own walls (2 m by default). Set it to 0 to keep your own UV unwrap instead.
- **Solid**: the game blocks the player with the model's bounding box (a box around the whole mesh). That's fine for
  walls, pillars and roofs overhead. For an arch you walk through, build the posts and the top as separate meshes, or
  untick Solid and add **COL** boxes (below).
- **Ramp**: for slopes and stairs you walk up. Pick the direction it rises (+X, -X, +Y, -Y in Blender) and untick Solid.
  The game walks you up a straight slope from the bottom of the box to the top.
- **Invisible walls**: any mesh whose name starts with **COL** (COL_fence, COL_roofblock...) becomes an invisible solid
  box in the game, the size of the mesh. Use them to give odd shapes simple collision, or to stop players falling off the
  edge of your map. They show as wireframes when you import again.
- Each model is saved in the mode's `models/` folder as `<name>.glb`. Keep the object's name stable and it keeps the
  same file. Any texture image you put in a material is packed into the model, so your own textures work too.
- A mesh with no material shows plain white in the game.
- **Several materials on one mesh** work: add them in the Material tab, then in Edit Mode select faces and press
  **Assign** (for example shingles on the roof faces, planks on the gable). Each keeps its own texture in the game.
- **Tile Texture Now** (under Texture size) shows the game's texture repeat on the selected meshes straight away;
  Export does it anyway.

## Reshaping the game's own pieces (roofs, walls with doorways...)

You can change any wall, roof or prop in **Edit Mode**: cut a doorway (Boolean modifier or knife), raise a roof
ridge, bevel edges, give faces other materials, or **Ctrl+A → Apply** its rotation and scale. Export notices the piece
differs from the original model and saves your shape as a new model in `assets/models/level/` (named after the original,
like `wall_stone_edit1.glb`), keeping where it stands, how it's turned and how big it is.

- **Shared meshes**: pieces of the same kind share one mesh in Blender, so Edit Mode on one roof changes every roof of
  that kind (the sidebar says how many share it). That's handy for "all roofs like this". To change just one, press
  **Make Only This One Editable** first. Copies made with **Shift+D** are already separate.
- **Collision fits the shape** (sidebar, on by default): Export fills your mesh with invisible boxes that follow its
  shape, so a doorway, arch or window stays open and the rest is solid. Turn it off for one box around the whole thing.
  It needs a closed mesh (no holes in the surface); an open mesh gets one box.

## Making a new map

1. Pick **New Map**, type a **Map name**, and press **New Map**. You get a 20 m cobblestone floor, a spawn point
   called `start` (the arrows) and the palette.
2. Build: palette pieces, your own meshes, templates (doors, NPCs, monsters...), as above.
3. **Lights**: add Blender **Point** lights (**Shift+A → Light → Point**). Their colour is kept, and their Power sets
   how far they reach (600 W ≈ 10 m). Palette torches already glow.
4. **Map atmosphere** in the sidebar: sky and fog colours, fog density (0 = clear, 0.05 = thick), ambient light,
   moon/sun light, weather (rain, dust, fireflies), horizon picture (night or dusk sky), music and ambience (file paths
   under `assets/audio/...`).
5. **Spawn points**: the `start` arrows are where players arrive. Copy the spawn template for more (each gets a name in
   the export; rename the copy to `spawn:<name>` to choose it). Turn the arrows to set which way players face.
6. **Export**. Your map is `content/maps/custom/<name>/map.json`, with the id `core:map.<name>` (lower case, spaces
   become underscores: "Toasty Test" is `core:map.toasty_test`).
7. **A way in**: switch to **Edit World**, **Import World**, copy the **portal** template next to a door somewhere in
   the world, set `destination_map` to your map's id and `destination_spawn` to `start`, and Export. And a **way back**:
   in your map, a portal with `destination_map` `core:map.edrath` and `destination_spawn` `village_gate` (outside
   Bellwether's gate).

To keep working on it later, pick **New Map**, type the same name, and press **Import My Map**.

What a map can't do (yet): collision is boxes, walkable surfaces are flat floors or straight ramps, and the game only
turns things around the vertical axis. Huge maps are fine, but very many separate pieces cost frame rate: join meshes
that belong together (**Ctrl+J**).

## Good to know

- **Textures look stretched in Blender** on big walls and floors. The game tiles them, so ignore it.
- **Doors and gaps**: doors are 1.84 m wide and 2.8 m tall. Move the walls in (with snapping) or model a frame around them.
- **Tilting** something (rotating around X or Y) isn't kept, and Export warns you.
- **Undo everything**: delete `content/maps/edrath_blender.json` and copy `edrath_world.base.json` over
  `edrath_world.json` (or delete your map's folder in `content/maps/custom`).
- **Updating the game**: Pack My Changes first and send the zip, so the next version has them.
- Maps or edits saved by the older add-on (in `mods/`) are picked up by Import and moved into the game on your next Export.
- Blender lights only count in a new map; in Edit World they are ignored.
- Coordinates: the game is Y-up and Blender is Z-up. The add-on converts between them; you never need to.

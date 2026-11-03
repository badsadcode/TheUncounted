# Editing levels in Blender

You can rearrange and add to the game world in Blender, then play your changes straight away. Your edits are saved in
their own small file (`mods/level_edits/map_edits.json`), so game updates never overwrite them, and you can send that
file to the developer to make them permanent.

## One-time setup

1. Install **Blender 4.0 or newer** (free, blender.org).
2. In Blender: **Edit → Preferences → Add-ons → Install...** and pick
   `tools/blender/uncounted_level_editor.py` from the game folder. Tick **The Uncounted: Level Editor** in the list.
3. Start a new General scene and delete the default cube, camera and light (select all with **A**, then **X**).
4. In the 3D view press **N** to open the sidebar and click the **Uncounted** tab.
5. Set **Game folder** to the folder that contains `game.exe`.

## Editing

1. Click **Import World**. After a few seconds the whole world appears with real models and textures, along with your
   earlier edits.
   - **Uncounted World**: every wall, floor, roof, prop and tree. Object names are the game's ids.
   - **Uncounted Markers**: NPCs (arrows), monsters (spheres) and objects such as doors, chests and levers (cubes),
     each labelled.
   - **Uncounted Palette**: one of every building piece, in a row to the side (+Y) of the world.
2. Edit with normal Blender tools:
   | To... | Do this |
   |---|---|
   | Move something | select it, **G** (then **X**/**Y**/**Z** to lock an axis; hold **Ctrl** to snap) |
   | Turn it | **R**, then **Z**: the game only turns things around the vertical axis |
   | Resize it | **S** (or **S**, **X** to stretch along one axis: walls and floors are stretched boxes) |
   | Copy it | **Shift+D** |
   | Delete it | **X** |
   | Add a new piece | find it in the Palette, **Shift+D**, move it into the world |
   | Move an NPC or monster | move its marker (a monster's patrol route moves with it) |
   | Undo | **Ctrl+Z** |
3. Click **Export Edits**. The bar at the bottom says what was saved, for example "3 changed, 2 added, 1 removed".
4. Start the game. Your changes are there.

Run **Import World** again at any time: it starts from the game's level plus your saved edits, so nothing is lost.

## Good to know

- **Walls and floors** are stretched boxes. To make a wall longer, scale it along one axis rather than copying it.
- **Textures look stretched in Blender** on big walls and floors. The game tiles them properly, so ignore it.
- **Pieces you add are scenery**: walls, floors, rocks, furniture. Doors, chests, levers, NPCs and monsters can be
  moved but not added from Blender (ask the developer for those).
- Turning something on its side (rotating around X or Y) isn't kept: the game ignores it, and Export warns you.
- To **undo all your edits**, delete `mods/level_edits/map_edits.json` (or rename it to switch it off).
- Keep the `mods/level_edits` folder when you update to a new build: copy it into the new game folder.
- Coordinates: the game is Y-up and Blender is Z-up. The add-on converts between them; you never need to.

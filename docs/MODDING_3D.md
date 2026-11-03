# Making 3D models and mods for The Uncounted

A practical guide for replacing or adding 3D models (weapons, items, props, scenery). Characters and monsters are
2D sprite sheets, not 3D: see `art_source/to_remake/README.md` for those.

---

## 1. The short version

1. Model in **Blender** (free). **1 Blender unit = 1 metre. Up is +Z in Blender** (the exporter turns it into the
   game's +Y for you).
2. Keep it **low-poly** (see the triangle budgets below) and give it either **one small texture** or **vertex colours**.
3. Export as **glTF Binary (.glb)** with textures embedded.
4. Either **overwrite** the game's file with the same name (quick test), or put it in a **mod folder** (the clean way,
   section 6).
5. Run `game.exe --validate --mods` to check for mistakes, then play with `game.exe --mods`. Press **F5** in game to
   reload content after changing files.

---

## 2. What the engine supports (and what it doesn't)

| Supported | Not supported (ignored or broken) |
|---|---|
| `.glb` (glTF 2.0 binary), static meshes | Skeletal animation, shape keys, rigs (3D creatures don't animate: they bob and tilt) |
| One base-colour texture per material (PNG or JPEG, **embedded** in the .glb) | Normal maps, roughness/metal maps, emission maps, PBR in general |
| Vertex colours (`COLOR_0`), multiplied with the texture | Draco/meshopt compression, KTX/Basis textures, texture transforms |
| Several materials per model | Glass, transparency, alpha *blending* |
| Alpha *cut-out*: pixels with alpha below 10% are thrown away (leaves, fences, chains) | More than one UV map (only the first is used) |
| Flat or smooth shading (whatever normals you export) | Lights or cameras inside the file (ignored) |

The game has its own lighting (sun, torches, fog), so **paint flat colours, not baked lighting or shadows.**
A light ambient-occlusion tint in the corners is fine. Textures are shown with crisp, pixelated filtering by default,
so small pixel-art textures (32×32 to 256×256) suit the look best.

---

## 3. Size, origin and orientation (the most important part)

**The engine re-centres every model by its bounding box**: the *bottom-centre* of the box is placed on the spot the
map or item points to. So:

- **Where your origin is doesn't matter.** What matters is the overall box. A stray vertex far away makes the box
  huge and shifts the whole model (the giant oak uses this on purpose to keep its canopy in the air).
- **Real-world size matters.** A door 2.8 m tall in Blender is 2.8 m tall in game. Map props can be scaled per
  placement, but items and weapons use your size directly.
- **Facing:** the model's front should face Blender's **−Y** (the default "front" view, numpad 1).

### Held weapons (first-person view)
- Model it **standing upright, handle at the bottom, blade or head pointing up (+Z in Blender)**.
- The hand grips **10 cm above the lowest point** of the model. Put the pommel or handle end at the bottom.
- The view model is drawn at 75% size, so make it its real size (a longsword about 1.0–1.1 m).
- **Bows** are centred instead (held by the middle). Model them upright, string facing −Y.
- **Arrows:** upright, tip pointing up.

### Doors and gates
- **Doors** swing around their **left edge** (as seen from the front). Model them closed, lying flat in the X–Z plane
  (wide in X, thin in Y in Blender).
- **Gates** (anything with "gate" in the filename) slide **straight up** 2.7 m instead of swinging.

### Walls, floors and stretchy blocks
`wall_stone`, `wall_timber`, `wall_crypt`, `floor_*` are **1×1×1 m cubes** that maps stretch to any size and tile with
`uv_scale`. If you replace one, keep it a 1 m cube with each face's UVs filling 0–1, and use a **seamless, tileable**
texture.

### Size reference (current models, metres, width × height × depth)
| Model | Size | Triangles |
|---|---|---|
| `items/iron_longsword.glb` | 0.28 × 1.08 × 0.08 | 48 |
| `items/steel_dagger.glb` | 0.28 × 0.66 × 0.08 | 48 |
| `items/iron_mace.glb` | 0.18 × 0.78 × 0.18 | 32 |
| `items/oak_staff.glb` | 0.15 × 1.52 × 0.15 | 32 |
| `items/hunting_bow.glb` | 0.05 × 0.90 × 0.13 | 48 |
| `items/iron_shield.glb` | 0.55 × 0.68 × 0.10 | 24 |
| `items/iron_helm.glb` | 0.25 × 0.22 × 0.26 | 364 |
| `items/potion_flask.glb` | 0.24 × 0.32 × 0.24 | 48 |
| `props/treasure_chest.glb` | 1.10 × 0.90 × 0.76 | 76 |
| `props/oak_door.glb` | 1.84 × 2.80 × 0.30 | 48 |
| `props/iron_gate.glb` | 2.20 × 2.90 × 0.16 | 144 |
| `props/wall_torch.glb` | 0.16 × 0.82 × 0.31 | 44 |
| `props/lectern_ledger.glb` | 0.75 × 1.28 × 0.65 | 88 |
| `props/bookshelf_prop.glb` | 1.80 × 2.60 × 0.55 | 12 |
| `env/tree_pine.glb` | 3.2 × 5.6 × 3.1 | 96 |
| `env/pillar_stone.glb` | 0.95 × 4.0 × 0.95 | 52 |
| `characters/lost_sentinel.glb` (3D creature) | 1.29 × 2.16 × 0.67 | 156 |

(In the game Y is up; in Blender read "height" as the Z size.) Run the measuring snippet at the end of this guide to
see every model.

### Triangle budgets
The style is chunky and low-poly. Rough limits: **small items 50–500**, **weapons 50–800**, **props 50–1,500**,
**big scenery 2,000–5,000**. Many copies of a prop (crates, torches, trees) should stay at the low end.

---

## 4. Blender walk-through (replacing the longsword)

1. **Start from the original** (recommended): *File → Import → glTF 2.0* and pick `assets/models/items/iron_longsword.glb`.
   You now have the exact size and position to match.
2. Model your sword next to it, upright, handle at the bottom. Delete the original when you're done.
3. **Colour it**, either way:
   - *Texture:* UV-unwrap (U → Smart UV Project), make a small image (e.g. 64×64 PNG), connect it to the material's
     **Base Color**. Nothing else in the material matters.
   - *Vertex colours:* Vertex Paint mode, or Color Attributes in the Data tab. No texture needed.
4. For a crisp faceted look: select all, right-click → **Shade Flat**.
5. **Apply transforms**: Ctrl+A → *All Transforms*.
6. **Export:** *File → Export → glTF 2.0*, with these settings:
   - Format: **glTF Binary (.glb)**
   - Include: *Selected Objects* (if other things are in the scene)
   - Transform: **+Y Up** ✅ (the default)
   - Mesh: *Apply Modifiers* ✅, *UVs* ✅, *Normals* ✅, *Vertex Colors* ✅ (if you used them)
   - Material: *Export*; Images: *Automatic*
   - Compression: **off**
   - Animation: off
7. Save it as `iron_longsword.glb` and test it (section 5 or 6).

**Common gotchas**
- Model shows **pink/missing or as a grey box**: the path is wrong or the file failed to load. The log line
  `Missing or unreadable model '…'` names the file.
- **Black or inside-out:** normals are flipped. In Edit Mode, select all and press Shift+N.
- **Floating or sunk into the floor:** a stray vertex is stretching the bounding box. Find and delete it.
- **Huge or tiny:** the scale wasn't applied (Ctrl+A), or it was modelled in centimetres.
- **Held at the wrong place:** the handle isn't at the lowest point, or there's a lower bit (a tassel, a chain).

---

## 5. Quick test: overwrite the original

Back up the original, then save your .glb over it, e.g. `assets/models/items/iron_longsword.glb`. Start the game (or
press F5). Every place that uses that file now shows yours. This is the fastest way to try something, but it changes
the base game, so for anything you want to keep or share, use a mod.

---

## 6. The clean way: a mod

Mods live in `mods/<your_mod_name>/`. With mods enabled, the game loads **every** mod folder, in alphabetical order.
A mod can **add** new things, or **replace** existing ones by redefining the same id (the last one loaded wins).

Enable mods with the `--mods` launch flag, or by setting `"enable_mods": true` in `config/game.json`.

### Example: replace the longsword's model
```
mods/
  toasty_swords/
    manifest.json
    content/items.json
    assets/models/longsword.glb
    assets/ui/longsword.png        (optional new inventory icon, 32×32)
```

`manifest.json`:
```json
{
  "schema_version": 1,
  "pack_id": "toasty_swords",
  "pack_name": "Toasty's Swords",
  "version": "1.0.0",
  "items": ["mods/toasty_swords/content/items.json"]
}
```

`content/items.json`: copy the **whole** item entry from `content/items/weapons.json` (search for
`core:item.iron_longsword`) and change only what you want. Redefining an id replaces the entire entry, so anything
you leave out is lost:
```json
{
  "schema_version": 1,
  "items": [
    {
      "id": "core:item.iron_longsword",
      "...": "(every other field copied from the original)",
      "world_model": "mods/toasty_swords/assets/models/longsword.glb",
      "icon": "mods/toasty_swords/assets/ui/longsword.png"
    }
  ]
}
```

### Adding a brand-new weapon
Same layout, but use a new id like `"toasty:item.flaming_spoon"`, plus a localization file for its name and
description. `mods/example_mod/` is a complete working example (a new sword, a new monster and a loot table), so copy it
as a starting point.

### What can a mod replace?
| Thing | How |
|---|---|
| Items (weapons, armour, food, books) | Redefine the item id with a new `world_model` / `icon` |
| 3D creatures (`"type": "model_glb"`) | Redefine the creature id with a new `appearance.model` |
| Sprite creatures and NPCs | Redefine the id with a new `appearance.sprite_sheet` |
| Map props, doors, chests, walls, trees | Not yet through a mod, because they're placed in the world map by file path. Overwrite the file in `assets/models/...` (section 5), or ask me to add a way. |

### Files a mod can list in `manifest.json`
`items`, `creatures`, `npcs`, `loot_tables`, `localization`, `spells`, `quests`, `dialogue`, `maps`, `factions`,
`races`, `archetypes`, `backgrounds`, `skills`, `synergies` (each a list of JSON file paths).

---

## 7. Checking your work

```bash
game.exe --validate --mods
```
This checks every file path and id, then prints `Validation OK` or a list of problems with the file and field.

```bash
game.exe --mods --showcase --shot showcase.png
```
This lines up every wearable and consumable pickup in front of the camera and saves a screenshot, which is a quick
way to see your items in the game's lighting.

In game, **F5** reloads content and shaders, so you can re-export from Blender and press F5 without restarting.

---

## 8. Measuring models (optional)

To print the size and triangle count of any .glb (needs Python):
```python
import json, struct, sys
b = open(sys.argv[1], 'rb').read(); n = struct.unpack('<I', b[12:16])[0]; j = json.loads(b[20:20 + n])
mn, mx = [1e9] * 3, [-1e9] * 3
for m in j['meshes']:
    for p in m['primitives']:
        a = j['accessors'][p['attributes']['POSITION']]
        mn = [min(x, y) for x, y in zip(mn, a['min'])]; mx = [max(x, y) for x, y in zip(mx, a['max'])]
print('size x,y(up),z =', [round(mx[i] - mn[i], 2) for i in range(3)])
```

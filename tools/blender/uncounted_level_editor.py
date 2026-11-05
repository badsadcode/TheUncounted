"""
The Uncounted: level editor add-on for Blender (4.0+).

Edit the game world, or build brand-new maps, in Blender. Full guide: docs/LEVEL_EDITOR.md.

  Install:  Edit > Preferences > Add-ons > Install... > pick this file > tick "The Uncounted: Level Editor".
  Use:      3D Viewport > press N > "Uncounted" tab. Set "Game folder" (the folder with game.exe).

  Edit the world:  Import World -> edit -> Export. Saved straight into the game's level (content/maps/edrath_world.json).
  Build a map:     New Map (or Import My Map) -> build -> Export. Saved into the game as content/maps/custom/<name>/.
                   Put a portal (palette template) in the world that leads to it, and one in your map that leads back.

  * Everything can be moved, turned (around Z), stretched, copied and deleted.
  * Doors, chests, levers, signs, pickups, NPCs, monsters, portals and spawn points come from the palette templates;
    their settings are the "game_..." fields in the sidebar.
  * Your own meshes become game pieces with their materials and textures. Name a mesh "COL..." to make it an invisible
    collision box (the game collides with boxes, so give odd shapes simple invisible boxes). Your mesh settings
    (solid, ramp) are in the sidebar.
  * In a new map, Blender point lights become game lights, and the sidebar has the map's sky, fog, light and music.

Coordinates: the game is Y-up, Blender is Z-up: game (x, y, z) is Blender (x, -z, y). A piece's game position is the
bottom-centre of its model, so imported meshes have their origin there and turn about it, as in the game.
"""

bl_info = {
    "name": "The Uncounted: Level Editor",
    "author": "The Uncounted",
    "version": (4, 10, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar (N) > Uncounted",
    "description": "Edit The Uncounted's world or build new maps, then export them for the game",
    "category": "Import-Export",
}

import json
import math
import os
import re
import shutil

import bpy
from mathutils import Vector

MAP_REL = "content/maps/edrath_world.json"              # the level the game plays
BASE_REL = "content/maps/edrath_world.base.json"        # the level before your Blender changes (made by tools/build_world.py)
CHANGES_REL = "content/maps/edrath_blender.json"        # your Blender changes, kept so rebuilding the world never loses them
LEVEL_MODELS = "assets/models/level"                    # your own models in the world
CUSTOM_MAPS = "content/maps/custom"                     # your new maps: content/maps/custom/<name>/map.json
CUSTOM_MODELS = "assets/models/custom"                  # their models: assets/models/custom/<name>/
OLD_EDITS_DIR = "mods/level_edits"                      # where version 2 and 3 saved (moved into the game on the next Export)
OLD_EDITS_REL = OLD_EDITS_DIR + "/map_edits.json"
OLD_USER_MAPS = "mods/user_maps"
OWN_MODEL_DIRS = (LEVEL_MODELS + "/", CUSTOM_MODELS + "/", OLD_EDITS_DIR + "/models", OLD_USER_MAPS + "/")
WORLD_ID = "core:map.edrath"
PACK_NAME = "my_level_changes.zip"
COL_WORLD, COL_OBJECTS, COL_PALETTE = "Uncounted World", "Uncounted Objects", "Uncounted Palette"
KINDS = ("npcs", "creatures", "interactables", "portals")
IDKEY = {"npcs": "instance_id", "creatures": "instance_id", "interactables": "instance_id", "portals": "id", "spawns": "id"}
PREFIX = {"npcs": "npc:", "creatures": "monster:", "interactables": "obj:", "portals": "portal:", "spawns": "spawn:"}
ROTKEY = {"npcs": "yaw", "creatures": None, "interactables": "rot_y", "portals": None, "spawns": "yaw_degrees"}
SHAPE = {"npcs": "SINGLE_ARROW", "creatures": "SPHERE", "interactables": "CUBE", "portals": "CONE", "spawns": "ARROWS"}
MARKER_LIFT = 0.4
EPS = 1e-3
BOX_MODEL = "assets/models/env/wall_stone.glb"      # a 1 m cube: collision boxes are this model, stretched and invisible

TEMPLATES = [
    ("door", "interactables", {"type": "door", "model": "assets/models/props/oak_door.glb", "prompt": "Door", "locked": False}),
    ("door_locked", "interactables", {"type": "door", "model": "assets/models/props/oak_door.glb", "prompt": "Door", "locked": True,
                                      "key_id": "", "lock_difficulty": 10}),
    ("gate", "interactables", {"type": "door", "model": "assets/models/props/iron_gate.glb", "prompt": "Gate", "locked": False}),
    ("chest", "interactables", {"type": "chest", "model": "assets/models/props/treasure_chest.glb", "loot_table": "core:loot.crypt_basic",
                                "locked": False, "lock_difficulty": 5}),
    ("lever", "interactables", {"type": "lever", "model": "assets/models/props/iron_lever.glb", "prompt": "Pull the Lever", "target_id": ""}),
    ("sign", "interactables", {"type": "readable", "model": "assets/models/props/lectern_ledger.glb", "prompt": "Read",
                               "title": "A Sign", "text": "Write the text here."}),
    ("pickup", "interactables", {"type": "pickup", "item_id": "core:item.health_potion", "qty": 1}),
    ("npc", "npcs", {"npc_id": "core:npc.grout"}),
    ("monster", "creatures", {"creature_id": "core:enemy.grave_rat"}),
    ("portal", "portals", {"prompt": "Travel", "radius": 2.2, "destination_map": WORLD_ID, "destination_spawn": "village_gate"}),
    ("spawn", "spawns", {}),
]


# ----------------------------------------------------------------------------------------------- helpers
def to_blender(p):
    return Vector((p[0], -p[2], p[1]))


def to_game(v):
    return [round(v.x, 3) + 0.0, round(v.z, 3) + 0.0, round(-v.y, 3) + 0.0]


def scale_to_blender(s):
    return (s[0], s[2], s[1])


def scale_to_game(s):
    return [round(s[0], 3), round(s[2], 3), round(s[1], 3)]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def safe_name(s):
    return re.sub(r"[^a-z0-9_]+", "_", s.lower()).strip("_") or "piece"


def game_dir(context):
    return bpy.path.abspath(context.scene.uncounted_game_dir)


def map_slug(context):
    return safe_name(context.scene.uncounted_map_name)


def apply_edits(world, edits):
    """The same rules as the game (ContentRegistry::ApplyMapEdits), so Blender shows what the game will show."""
    pe = edits.get("props", {})
    removed = set(pe.get("remove", []))
    props = [p for p in world.get("props", []) if p["id"] not in removed]
    for p in props:
        p.update(pe.get("modify", {}).get(p["id"], {}))
    world["props"] = props + pe.get("add", [])
    for key in KINDS:
        ke, idk = edits.get(key, {}), IDKEY[key]
        gone = set(ke.get("remove", []))
        lst = [e for e in world.get(key, []) if e[idk] not in gone]
        by_id = {e[idk]: i for i, e in enumerate(lst)}
        for d in ke.get("set", []):
            if d[idk] in by_id:
                lst[by_id[d[idk]]] = d
            else:
                lst.append(d)
        for e in lst:
            e.update(ke.get("modify", {}).get(e[idk], {}))
        world[key] = lst
    for key in ("lights", "spawns", "scatter"):        # replaced whole when changed in Blender
        if key in edits:
            world[key] = edits[key]
    return world


def collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def clear_collection(name):
    col = bpy.data.collections.get(name)
    if col:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)


def game_tiling(mat):
    """Make Blender repeat a texture the way the game does: the mesh's UVs times the object's game_uv_x / game_uv_y."""
    if mat is None or not mat.use_nodes or mat.get("unc_tiled"):
        return
    nt = mat.node_tree
    images = [n for n in nt.nodes if n.type == "TEX_IMAGE"]
    if not images:
        return
    uvn = nt.nodes.new("ShaderNodeUVMap")
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    comb.inputs[2].default_value = 1.0
    for axis, name in ((0, "game_uv_x"), (1, "game_uv_y")):
        attr = nt.nodes.new("ShaderNodeAttribute")
        attr.attribute_type = "OBJECT"
        attr.attribute_name = name
        none = nt.nodes.new("ShaderNodeMath")             # objects without the field (doors, chests...) repeat once
        none.operation = "COMPARE"
        none.inputs[1].default_value = 0.0
        none.inputs[2].default_value = 1e-4
        nt.links.new(attr.outputs["Fac"], none.inputs[0])
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "ADD"
        nt.links.new(attr.outputs["Fac"], add.inputs[0])
        nt.links.new(none.outputs[0], add.inputs[1])
        nt.links.new(add.outputs[0], comb.inputs[axis])
    mul = nt.nodes.new("ShaderNodeVectorMath")
    mul.operation = "MULTIPLY"
    nt.links.new(uvn.outputs["UV"], mul.inputs[0])
    nt.links.new(comb.outputs[0], mul.inputs[1])
    for img in images:
        img.interpolation = "Closest"
        if not img.inputs["Vector"].is_linked:
            nt.links.new(mul.outputs[0], img.inputs["Vector"])
    mat["unc_tiled"] = True


def game_view(context, sc=None):
    """Show the scene textured, as in the game: Material Preview in every 3D view, the map's sky colour behind it."""
    for win in context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                for sp in area.spaces:
                    if sp.type == "VIEW_3D":
                        sp.shading.type = "MATERIAL"
                        sp.shading.use_scene_world = False
                        sp.clip_end = 2000.0


def mesh_hash(me):
    """A fingerprint of a mesh's shape, UVs and materials: tells whether a game piece was reshaped or retextured."""
    import hashlib
    from array import array
    h = hashlib.md5()
    co = [0.0] * (len(me.vertices) * 3)
    me.vertices.foreach_get("co", co)
    h.update(array("f", [round(c, 4) for c in co]).tobytes())
    mi = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", mi)
    h.update(array("i", mi).tobytes())
    if me.uv_layers.active:
        uv = [0.0] * (len(me.loops) * 2)
        me.uv_layers.active.data.foreach_get("uv", uv)
        h.update(array("f", [round(c, 4) for c in uv]).tobytes())
    names = [re.sub(r"\.\d{3}$", "", m.name) if m else "" for m in me.materials]
    h.update("|".join(names).encode())
    return h.hexdigest()


def uv_hash(me):
    """A fingerprint of a mesh's UVs only: tells whether you unwrapped a game piece yourself."""
    import hashlib
    from array import array
    if not me.uv_layers.active:
        return ""
    uv = [0.0] * (len(me.loops) * 2)
    me.uv_layers.active.data.foreach_get("uv", uv)
    return hashlib.md5(array("f", [round(c, 4) for c in uv]).tobytes()).hexdigest()


def model_mesh(gdir, model, cache):
    """Import a .glb once and join it into one mesh whose origin is the bottom-centre (the game's anchor)."""
    if model in cache:
        return cache[model]
    path = os.path.join(gdir, model)
    mesh = None
    if model and os.path.exists(path):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=path)
        new = [o for o in bpy.data.objects if o not in before]
        meshes = [o for o in new if o.type == "MESH"]
        if meshes:
            bpy.ops.object.select_all(action="DESELECT")
            for o in meshes:
                o.select_set(True)
            bpy.context.view_layer.objects.active = meshes[0]
            bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
            if len(meshes) > 1:
                bpy.ops.object.join()
            mesh = bpy.context.view_layer.objects.active.data
            xs = [v.co.x for v in mesh.vertices]
            ys = [v.co.y for v in mesh.vertices]
            zs = [v.co.z for v in mesh.vertices]
            anchor = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
            for v in mesh.vertices:
                v.co -= anchor
            mesh.name = "UNC:" + model
            mesh["unc_hash"] = mesh_hash(mesh)
            mesh["unc_uvhash"] = uv_hash(mesh)
            for mat in mesh.materials:
                game_tiling(mat)
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
    cache[model] = mesh
    return mesh


SKIP_FIELDS = {"instance_id", "id", "pos", "rot_y", "yaw", "yaw_degrees", "scale", "patrol_a", "patrol_b"}


def set_fields(o, d):
    """Every simple field becomes an editable "game_<field>" property; lists/objects stay as JSON text."""
    types = {}
    for k, v in d.items():
        if k in SKIP_FIELDS:
            continue
        if isinstance(v, (bool, int, float, str)):
            o["game_" + k] = v
            types[k] = type(v).__name__
        else:
            o["game_json_" + k] = json.dumps(v)
            types[k] = "json"
    o["unc_types"] = json.dumps(types)


def get_fields(o):
    types = json.loads(o.get("unc_types", "{}"))
    d = {}
    for key in o.keys():
        if key.startswith("game_json_"):
            k = key[len("game_json_"):]
            try:
                d[k] = json.loads(o[key])
            except ValueError:
                d[k] = o[key]
        elif key.startswith("game_"):
            k, v = key[len("game_"):], o[key]
            t = types.get(k)
            v = bool(v) if t == "bool" else int(v) if t == "int" else float(v) if t == "float" else str(v) if t == "str" else v
            d[k] = v
    return d


_DEFS = {}


def game_defs(gdir):
    """id -> appearance for every NPC and monster (content/npcs, content/creatures)."""
    if gdir not in _DEFS:
        found = {}
        for sub, key in (("npcs", "npcs"), ("creatures", "creatures")):
            folder = os.path.join(gdir, "content", sub)
            for f in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
                if f.endswith(".json"):
                    try:
                        data = read_json(os.path.join(folder, f))
                    except ValueError:
                        continue
                    for e in (data.get(key, []) if isinstance(data, dict) else data):
                        if isinstance(e, dict) and "id" in e and "appearance" in e:
                            found[e["id"]] = e["appearance"]
        _DEFS[gdir] = found
    return _DEFS[gdir]


def sprite_image(gdir, sheet, anim_rel):
    """The first frame of a sprite sheet (facing you, standing) as its own Blender image, and the sheet's pivot."""
    import numpy as np
    anim = read_json(os.path.join(gdir, anim_rel)) if anim_rel and os.path.exists(os.path.join(gdir, anim_rel)) else {}
    fw, fh = anim.get("frame_width", 128), anim.get("frame_height", 128)
    pivot = anim.get("pivot", [0.5, 0.92])
    name = "UNC_SPRITE:" + sheet
    img = bpy.data.images.get(name)
    if img is None:
        path = os.path.join(gdir, sheet)
        if not os.path.exists(path):
            return None, pivot, fw / fh
        src = bpy.data.images.load(path, check_existing=True)
        src.reload()                                      # images load lazily: make sure the pixels are there
        w, h = src.size
        if w < fw or h < fh or len(src.pixels) != w * h * 4:
            bpy.data.images.remove(src)
            return None, pivot, fw / fh
        px = np.empty(w * h * 4, dtype=np.float32)
        src.pixels.foreach_get(px)
        px = px.reshape(h, w, 4)[h - fh:h, 0:fw, :]          # Blender rows run bottom-up: the top-left frame
        img = bpy.data.images.new(name, fw, fh, alpha=True)
        img.pixels.foreach_set(np.ascontiguousarray(px).ravel())
        img.pack()
        bpy.data.images.remove(src)
    return img, pivot, fw / fh


def apply_sprite(gdir, o):
    """Show an NPC or monster as its game sprite: upright, its game height, feet on its spot, plus a crossed copy so
    it's visible from every side. Falls back to the marker when the sprite can't be found."""
    for c in list(o.children):
        if c.get("unc_kind") == "sprite_child":
            bpy.data.objects.remove(c, do_unlink=True)
    kind = o.get("unc_kind")
    did = o.get("game_npc_id") if kind == "npcs" else o.get("game_creature_id")
    app = game_defs(gdir).get(did or "", {})
    img, pivot, aspect = sprite_image(gdir, app.get("sprite_sheet", ""), app.get("animation_data", "")) if app else (None, None, 1)
    yaw = o.rotation_euler.z
    if img is None:
        o.empty_display_type = SHAPE[kind]
        o.empty_display_size = 0.4
        o.location.z += MARKER_LIFT - o.get("unc_lift", 0.0)
        o["unc_lift"] = MARKER_LIFT
        o["unc_upright"] = False
        o.rotation_euler = (0.0, 0.0, yaw)
        return
    height = float(app.get("scale", 1.7))
    o.location.z -= o.get("unc_lift", 0.0)
    o["unc_lift"] = 0.0
    o["unc_upright"] = True
    o.empty_display_type = "IMAGE"
    o.data = img
    o.empty_display_size = height * max(1.0, aspect)
    o.empty_image_offset = (-pivot[0], -(1.0 - pivot[1]))
    o.use_empty_image_alpha = True
    o.empty_image_side = "DOUBLE_SIDED"
    o.rotation_euler = (math.radians(90), 0.0, yaw)    # stood up; turning around Z still sets the facing
    c = bpy.data.objects.new(o.name + " (side)", None)
    for k in ("empty_display_type", "empty_display_size", "empty_image_offset", "use_empty_image_alpha", "empty_image_side"):
        if k == "empty_display_type":
            c.empty_display_type = "IMAGE"
            c.data = img
        else:
            setattr(c, k, getattr(o, k))
    c.parent = o
    c.rotation_euler = (0.0, math.radians(90), 0.0)
    c.hide_select = True
    c["unc_kind"] = "sprite_child"
    for col in o.users_collection:
        col.objects.link(c)


def link_tree(col, o):
    col.objects.link(o)
    for c in o.children:
        if c.get("unc_kind") == "sprite_child" and col not in c.users_collection:
            col.objects.link(c)
    return o


def make_object(gdir, cache, kind, d, name):
    """A game object as a Blender object: its real model when it has one, else a labelled marker."""
    mesh = model_mesh(gdir, d.get("model", ""), cache) if kind == "interactables" else None
    app = None
    if kind in ("npcs", "creatures"):                  # monsters drawn as 3D models in the game: show that model
        app = game_defs(gdir).get(d.get("npc_id" if kind == "npcs" else "creature_id", ""), {})
        if app.get("type") == "model_glb":
            mesh = model_mesh(gdir, app.get("model", ""), cache)
    o = bpy.data.objects.new(name, mesh)
    if mesh is None:
        o.empty_display_type = SHAPE[kind]
        o.empty_display_size = 0.5 if kind in ("portals", "spawns") else 0.4
        o.location = to_blender(d.get("pos", [0, 0, 0])) + Vector((0, 0, MARKER_LIFT))
        o["unc_lift"] = MARKER_LIFT
    else:
        o.location = to_blender(d.get("pos", [0, 0, 0]))
        o.scale = scale_to_blender(d.get("scale", [1, 1, 1]))
        if app:
            sc = float(app.get("scale", 1.0))
            o.scale = (sc, sc, sc)
        o["unc_lift"] = 0.0
    o.show_name = True
    rk = ROTKEY[kind]
    o.rotation_euler = (0.0, 0.0, math.radians(d.get(rk, 0.0) if rk else 0.0))
    o["unc_kind"] = kind
    o["unc_id"] = d.get(IDKEY[kind], "")
    pos = d.get("pos", [0, 0, 0])
    if kind == "creatures":
        o["unc_patrol"] = json.dumps([[a - b for a, b in zip(d.get(k, pos), pos)] for k in ("patrol_a", "patrol_b")])
    set_fields(o, d)
    if kind in ("npcs", "creatures") and o.type == "EMPTY":
        apply_sprite(gdir, o)
    return o


def object_def(o, kind, oid):
    d = get_fields(o)
    d[IDKEY[kind]] = oid
    d["pos"] = to_game(o.location - Vector((0, 0, o.get("unc_lift", 0.0))))
    rk = ROTKEY[kind]
    if rk:
        d[rk] = round(math.degrees(o.rotation_euler.z), 2)
    if kind == "interactables" and o.type == "MESH":
        sc = scale_to_game(o.scale)
        if any(abs(c - 1.0) > EPS for c in sc):
            d["scale"] = sc
    if kind == "creatures":
        offs = json.loads(o.get("unc_patrol", "[[0,0,0],[0,0,0]]"))
        d["patrol_a"] = [round(a + b, 3) for a, b in zip(d["pos"], offs[0])]
        d["patrol_b"] = [round(a + b, 3) for a, b in zip(d["pos"], offs[1])]
    return d


def round_def(d, kind):
    """Compare definitions without float noise or missing defaults (facing 0, patrol = spawn point, scale 1)."""
    def r(v):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return round(float(v), 2) + 0.0
        if isinstance(v, list):
            return [r(x) for x in v]
        if isinstance(v, dict):
            return {k: r(x) for k, x in v.items()}
        return v
    d = dict(d)
    rk = ROTKEY[kind]
    if rk:
        d.setdefault(rk, 0.0)
    if kind == "creatures":
        d.setdefault("patrol_a", d.get("pos"))
        d.setdefault("patrol_b", d.get("pos"))
    if "scale" in d and all(abs(c - 1.0) < EPS for c in d["scale"]):
        del d["scale"]
    return json.dumps(r(d), sort_keys=True)


def add_prop_object(gdir, cache, p, col, base_props=None):
    mesh = model_mesh(gdir, p["model"], cache)
    if mesh is None:
        return None
    o = bpy.data.objects.new(p["id"], mesh)
    o.location = to_blender(p["pos"])
    o.rotation_euler = (0.0, 0.0, math.radians(p.get("rot_y", 0.0)))
    o.scale = scale_to_blender(p.get("scale", [1, 1, 1]))
    o["unc_kind"] = "prop"
    o["unc_id"] = p["id"]
    o["unc_model"] = p["model"]
    o["unc_prop"] = json.dumps({k: v for k, v in p.items() if k not in ("pos", "rot_y", "scale", "solid", "uv_scale", "invisible")})
    o["game_solid"] = bool(p.get("solid", True))
    uv = p.get("uv_scale", [1, 1])
    o["game_uv_x"], o["game_uv_y"] = float(uv[0]), float(uv[1])
    if p.get("invisible"):
        o["game_invisible"] = True
        o.display_type = "WIRE"
    if p["model"].startswith(OWN_MODEL_DIRS):
        o.uncounted_solid = bool(p.get("solid", True))       # one of your own models, already baked: keep its settings
        o.uncounted_ramp = {"+x": "PX", "-x": "NX", "-z": "PY", "+z": "NY"}.get(p.get("ramp", ""), "NONE")
        o.uncounted_tile = 0.0                                # its texture tiling is already in the model
    if base_props is not None and p["id"] in base_props:
        b = base_props[p["id"]]
        o["unc_base"] = json.dumps({"pos": b["pos"], "rot_y": b.get("rot_y", 0.0), "scale": b.get("scale", [1, 1, 1]),
                                    "solid": b.get("solid", True), "uv_scale": b.get("uv_scale", [1, 1])})
    col.objects.link(o)
    return o


def build_palette(gdir, cache, world_props):
    """One of every building piece in a row, the object templates in the next. Torches keep their flames."""
    cp = collection(COL_PALETTE)
    first = {}
    for p in world_props:
        first.setdefault(p["model"], p)
    models = sorted(set(first) | {f"assets/models/{d}/{f}" for d in ("env", "props")
                                  for f in sorted(os.listdir(os.path.join(gdir, "assets", "models", d))) if f.endswith(".glb")})
    x = 0.0
    for model in models:
        mesh = model_mesh(gdir, model, cache)
        if mesh is None:
            continue
        name = "PALETTE:" + os.path.basename(model)[:-4]
        o = bpy.data.objects.new(name, mesh)
        o.location = Vector((x, 60.0, 0.0))
        o.show_name = True
        o["unc_kind"] = "palette"
        o["unc_id"] = name
        o["unc_model"] = model
        src = first.get(model, {"model": model})
        o["unc_prop"] = json.dumps({k: v for k, v in src.items() if k in ("model", "emitter", "ramp")})
        o["game_solid"] = bool(src.get("solid", True))
        o["game_uv_x"], o["game_uv_y"] = 1.0, 1.0
        cp.objects.link(o)
        w = max(v.co.x for v in mesh.vertices) - min(v.co.x for v in mesh.vertices) if mesh.vertices else 1.0
        x += max(2.5, w + 1.5)
    for i, (tname, kind, d) in enumerate(TEMPLATES):
        d = dict(d, pos=[i * 3.0, 0.0, -66.0])
        d[IDKEY[kind]] = "TEMPLATE:" + tname
        o = make_object(gdir, cache, kind, d, "TEMPLATE:" + tname)
        o["unc_template"] = True
        link_tree(cp, o)


def add_lights(lights, col):
    """The map's lights as Blender point lights: colour kept, reach (radius) as Power (W = radius x 60)."""
    for i, l in enumerate(lights):
        ld = bpy.data.lights.new(f"light_{i}", "POINT")
        ld.color = l.get("color", [1, 0.75, 0.4])
        ld.energy = l.get("radius", 10.0) * 60.0
        ld.shadow_soft_size = 0.1
        lo = bpy.data.objects.new(f"light_{i}", ld)
        lo.location = to_blender(l["pos"])
        col.objects.link(lo)


def lights_key(lights):
    return sorted(json.dumps([[round(float(c), 2) + 0.0 for c in l["pos"]], [round(float(c), 2) + 0.0 for c in l.get("color", [1, 1, 1])],
                              round(float(l.get("radius", 10.0)), 1)]) for l in lights)


def spawns_key(spawns):
    return {k: [[round(float(c), 2) + 0.0 for c in v["pos"]], round(float(v.get("yaw_degrees", 0.0)), 1) + 0.0] for k, v in spawns.items()}


# ----------------------------------------------------------------------------------------------- import / new map
class UNC_OT_import_world(bpy.types.Operator):
    bl_idname = "uncounted.import_world"
    bl_label = "Import World"
    bl_description = "Edit the game world: load it (with your earlier edits) into this scene"

    def execute(self, context):
        gdir = game_dir(context)
        map_path = os.path.join(gdir, MAP_REL)
        if not os.path.exists(map_path):
            self.report({"ERROR"}, f"Can't find {MAP_REL} in {gdir}. Set the game folder first.")
            return {"CANCELLED"}
        context.scene.uncounted_mode = "WORLD"
        base_path = os.path.join(gdir, BASE_REL)
        base = read_json(base_path if os.path.exists(base_path) else map_path)
        world = json.loads(json.dumps(base))
        for rel in (CHANGES_REL, OLD_EDITS_REL):        # your changes so far (and any saved by the older version)
            if os.path.exists(os.path.join(gdir, rel)):
                world = apply_edits(world, read_json(os.path.join(gdir, rel)))
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co = collection(COL_WORLD), collection(COL_OBJECTS)
        cache, skipped = {}, 0
        base_props = {p["id"]: p for p in base.get("props", [])}
        own = {o.get("unc_custom_id") for o in context.scene.objects if o.get("unc_custom_id")}
        fitted = {p["id"].split("__fit")[0] for p in world.get("props", []) if "__fit" in p["id"]}
        for p in world.get("props", []):
            if p["id"] in own or "__fit" in p["id"]:
                continue                               # your own model (its mesh is in the scene) or its collision (rebuilt on export)
            o = add_prop_object(gdir, cache, p, cw, base_props)
            if o is None:
                skipped += 1
            elif p["id"] in fitted:                    # blocked by shape-fitting boxes: it is solid
                o.uncounted_solid = True
                o["game_solid"] = True
        for kind in KINDS:
            for e in world.get(kind, []):
                link_tree(co, make_object(gdir, cache, kind, e, PREFIX[kind] + e[IDKEY[kind]]))
        for sid, sp in world.get("spawns", {}).items():   # where players arrive (from portals, boats, new games)
            link_tree(co, make_object(gdir, cache, "spawns", {"id": sid, "pos": sp["pos"], "yaw_degrees": sp.get("yaw_degrees", 0.0)},
                                        "spawn:" + sid))
        add_lights(world.get("lights", []), cw)
        context.scene.uncounted_keep_scatter = bool(world.get("scatter")) or not base.get("scatter")
        context.scene["unc_base_extra"] = json.dumps({"lights": lights_key(base.get("lights", [])),
                                                      "spawns": spawns_key(base.get("spawns", {}))})
        build_palette(gdir, cache, base.get("props", []))
        context.scene["unc_base"] = json.dumps({k: {e[IDKEY[k]]: e for e in base.get(k, [])} for k in KINDS})
        context.scene["unc_base_ids"] = json.dumps(sorted(base_props))
        game_view(context)
        self.report({"INFO"}, f"Imported the world: {len(cw.objects)} pieces, {len(co.objects)} objects"
                              + (f" ({skipped} skipped: model missing)" if skipped else ""))
        return {"FINISHED"}


class UNC_OT_new_map(bpy.types.Operator):
    bl_idname = "uncounted.new_map"
    bl_label = "New Map"
    bl_description = "Start a brand-new map: an empty scene with a spawn point, a starter floor and the palette"

    def execute(self, context):
        gdir = game_dir(context)
        if not os.path.exists(os.path.join(gdir, MAP_REL)):
            self.report({"ERROR"}, "Set the game folder first.")
            return {"CANCELLED"}
        if map_slug(context) == "edrath":
            self.report({"ERROR"}, "That name belongs to the game's world. Pick another map name.")
            return {"CANCELLED"}
        context.scene.uncounted_mode = "MAP"
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co, cache = collection(COL_WORLD), collection(COL_OBJECTS), {}
        add_prop_object(gdir, cache, {"id": "starter_floor", "model": "assets/models/env/floor_cobble.glb", "pos": [0, -0.5, 0],
                                      "scale": [20, 0.5, 20], "solid": False, "uv_scale": [8, 8]}, cw)
        link_tree(co, make_object(gdir, cache, "spawns", {"id": "start", "pos": [0, 0, 0]}, "spawn:start"))
        build_palette(gdir, cache, read_json(os.path.join(gdir, MAP_REL)).get("props", []))
        game_view(context)
        self.report({"INFO"}, f"New map '{context.scene.uncounted_map_name}': build away, then Export.")
        return {"FINISHED"}


class UNC_OT_import_map(bpy.types.Operator):
    bl_idname = "uncounted.import_map"
    bl_label = "Import My Map"
    bl_description = "Load the map named above from mods/user_maps to keep working on it"

    def execute(self, context):
        gdir = game_dir(context)
        path = os.path.join(gdir, CUSTOM_MAPS, map_slug(context), "map.json")
        if not os.path.exists(path):
            path = os.path.join(gdir, OLD_USER_MAPS, map_slug(context), "map.json")
        if not os.path.exists(path):
            self.report({"ERROR"}, f"No map called '{context.scene.uncounted_map_name}' yet ({path}). Use New Map.")
            return {"CANCELLED"}
        context.scene.uncounted_mode = "MAP"
        m = read_json(path)
        sc = context.scene
        sc.uncounted_sky = [c / 255.0 for c in m.get("sky_color", [20, 24, 36])]
        sc.uncounted_fog = m.get("fog_color", [0.08, 0.1, 0.16])
        sc.uncounted_fog_density = m.get("fog_density", 0.025)
        sc.uncounted_ambient = m.get("ambient_color", [0.4, 0.42, 0.5])
        sc.uncounted_sun = m.get("sun_color", [0.5, 0.5, 0.6])
        sc.uncounted_weather = m.get("weather", "") or "NONE"
        sc.uncounted_panorama = {"": "NONE", "assets/textures/sky/sky_night.png": "NIGHT", "assets/textures/sky/sky_dusk.png": "DUSK"}.get(
            m.get("sky_panorama", ""), "NONE")
        sc.uncounted_day_night = bool(m.get("day_night", bool(m.get("sky_panorama"))))
        sc.uncounted_music = m.get("music", "")
        sc.uncounted_ambience = m.get("ambience", "")
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co, cache = collection(COL_WORLD), collection(COL_OBJECTS), {}
        own = {o.get("unc_custom_id") for o in sc.objects if o.get("unc_custom_id")}
        fitted = {p["id"].split("__fit")[0] for p in m.get("props", []) if "__fit" in p["id"]}
        for p in m.get("props", []):
            if p["id"] not in own and "__fit" not in p["id"]:
                o = add_prop_object(gdir, cache, p, cw)
                if o is not None and p["id"] in fitted:
                    o.uncounted_solid = True
                    o["game_solid"] = True
        for kind in KINDS:
            for e in m.get(kind, []):
                link_tree(co, make_object(gdir, cache, kind, e, PREFIX[kind] + e[IDKEY[kind]]))
        for sid, s in m.get("spawns", {}).items():
            link_tree(co, make_object(gdir, cache, "spawns", {"id": sid, "pos": s["pos"], "yaw_degrees": s.get("yaw_degrees", 0.0)},
                                        "spawn:" + sid))
        add_lights(m.get("lights", []), cw)
        build_palette(gdir, cache, read_json(os.path.join(gdir, MAP_REL)).get("props", []))
        game_view(context)
        self.report({"INFO"}, f"Loaded your map '{sc.uncounted_map_name}'.")
        return {"FINISHED"}


# ----------------------------------------------------------------------------------------------- export
def tile_uvs(mesh, size, matrix=None):
    """Box-project the texture so it repeats every `size` metres, however big the mesh is (like the game's walls).
    With `matrix` (the object's), works in world space on the object's own mesh, so Blender shows what the game will."""
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        n = poly.normal if matrix is None else (matrix.to_3x3() @ poly.normal)
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
            if matrix is not None:
                co = matrix @ co
            u, v = ((co.y, co.z) if ax == 0 else (co.x, co.z) if ax == 1 else (co.x, co.y))
            if (ax == 0 and n[0] < 0) or (ax == 1 and n[1] > 0):
                u = -u
            uv[li].uv = (u / size, v / size)


def export_mesh_glb(o, gdir, rel):
    """Bake a hand-made mesh into a game model: world-space geometry, origin at its bottom-centre."""
    mesh = o.data.copy()
    mesh.transform(o.matrix_world)
    if o.uncounted_tile > 0.0:
        tile_uvs(mesh, o.uncounted_tile)
        tile_uvs(o.data, o.uncounted_tile, o.matrix_world)   # and show the same tiling in Blender
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    anchor = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    for v in mesh.vertices:
        v.co -= anchor
    tmp = bpy.data.objects.new("__unc_export__", mesh)
    bpy.context.scene.collection.objects.link(tmp)
    for s in bpy.context.selected_objects:
        s.select_set(False)
    tmp.select_set(True)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.export_scene.gltf(filepath=os.path.join(gdir, rel), export_format="GLB", use_selection=True, export_yup=True, export_apply=True)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    return anchor


def export_local_glb(me, gdir, rel):
    """Bake an edited game piece in its own (object) space, origin moved to its bottom-centre. Returns that local point."""
    mesh = me.copy()
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    anchor = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
    for v in mesh.vertices:
        v.co -= anchor
    tmp = bpy.data.objects.new("__unc_export__", mesh)
    bpy.context.scene.collection.objects.link(tmp)
    for s in bpy.context.selected_objects:
        s.select_set(False)
    tmp.select_set(True)
    bpy.context.view_layer.objects.active = tmp
    bpy.ops.export_scene.gltf(filepath=os.path.join(gdir, rel), export_format="GLB", use_selection=True, export_yup=True, export_apply=True)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    return anchor


def fit_boxes(o, max_boxes=400):
    """Collision that follows the shape (also slopes: they become steps under 0.2 m). Each loose part of the mesh is filled with a fine grid (a cell counts when its
    centre is inside or a surface passes through it, so thin walls are caught) and the filled cells are merged into as
    few boxes as possible. Boxes are (min, max) in the object's scaled
    space (location and turn not applied). None means one box around everything will do."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    bm = bmesh.new()
    bm.from_mesh(o.data)
    # Turned and scaled like the object but not moved: the game's collision boxes are straight (world-aligned), so build
    # them in world directions. A diagonal ramp becomes small, exact steps instead of oversized turned boxes.
    bmesh.ops.transform(bm, matrix=o.matrix_world.to_3x3().to_4x4(), verts=bm.verts)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)   # models split vertices at texture seams: weld them back
    left_faces, islands = set(bm.faces), []
    while left_faces:
        f = left_faces.pop()
        isl, stack = {f}, [f]
        while stack:
            g = stack.pop()
            for e in g.edges:
                for h in e.link_faces:
                    if h not in isl:
                        isl.add(h)
                        stack.append(h)
        left_faces -= isl
        islands.append(isl)
    boxes = []
    for isl in islands:
        verts = list({v for f in isl for v in f.verts})
        lo = Vector((min(v.co.x for v in verts), min(v.co.y for v in verts), min(v.co.z for v in verts)))
        hi = Vector((max(v.co.x for v in verts), max(v.co.y for v in verts), max(v.co.z for v in verts)))
        index = {v: i for i, v in enumerate(verts)}
        tree = BVHTree.FromPolygons([v.co.copy() for v in verts], [[index[v] for v in f.verts] for f in isl])
        size = hi - lo
        reach = size.length + 1.0
        cell = max(0.12, max(size) / 120.0)
        up = min(cell, 0.2)                            # never taller than 0.2 m: slopes become steps you walk up
        while math.ceil(size.x / cell) * math.ceil(size.y / cell) * math.ceil(size.z / up) > 200000:
            cell *= 1.25
        n = [max(1, math.ceil(size.x / cell - 1e-6)), max(1, math.ceil(size.y / cell - 1e-6)), max(1, math.ceil(size.z / up - 1e-6))]
        step = [size[i] / n[i] for i in range(3)]
        near = 0.5 * max(step)
        dirs = [Vector(d) for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))]

        def inside(p):
            # Look out in six directions: from inside a solid you see the back of its surfaces. Works with overlapping
            # pieces and meshes that aren't perfectly closed.
            votes = 0
            for k, d in enumerate(dirs):
                hit = tree.ray_cast(p, d, reach)
                if hit[0] is not None and hit[1].dot(d) > 0.0:
                    votes += 1
                if votes >= 4 or votes + (5 - k) < 4:
                    break
            return votes >= 4

        filled = set()
        for i in range(n[0]):
            for j in range(n[1]):
                for k in range(n[2]):
                    p = Vector((lo.x + (i + 0.5) * step[0], lo.y + (j + 0.5) * step[1], lo.z + (k + 0.5) * step[2]))
                    hit = tree.find_nearest(p)
                    if hit[0] is not None and (hit[3] < near * 0.999 or inside(p)):
                        filled.add((i, j, k))
        if len(filled) == n[0] * n[1] * n[2]:
            boxes.append((lo, hi))
            continue
        cells = set(filled)
        for c in sorted(filled):
            if c not in cells:
                continue
            i0, j0, k0 = c
            i1 = i0
            while (i1 + 1, j0, k0) in cells:
                i1 += 1
            j1 = j0
            while all((i, j1 + 1, k0) in cells for i in range(i0, i1 + 1)):
                j1 += 1
            k1 = k0
            while all((i, j, k1 + 1) in cells for i in range(i0, i1 + 1) for j in range(j0, j1 + 1)):
                k1 += 1
            for i in range(i0, i1 + 1):
                for j in range(j0, j1 + 1):
                    for k in range(k0, k1 + 1):
                        cells.discard((i, j, k))
            boxes.append((Vector((lo.x + i0 * step[0], lo.y + j0 * step[1], lo.z + k0 * step[2])),
                          Vector((lo.x + (i1 + 1) * step[0], lo.y + (j1 + 1) * step[1], lo.z + (k1 + 1) * step[2]))))
        if len(boxes) > max_boxes:
            break
    bm.free()
    if len(boxes) <= 1 or len(boxes) > max_boxes:
        return None
    return boxes


def fit_props(o, pid):
    """Invisible solid boxes for a mesh's collision, straight (world-aligned) like all the game's collision. [] when one
    box will do."""
    if not o.uncounted_fit:
        return []
    boxes = fit_boxes(o)
    if not boxes:
        return []
    out = []
    for i, (mn, mx) in enumerate(boxes):
        c = Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))
        out.append({"id": f"{pid}__fit{i + 1}", "model": BOX_MODEL, "pos": to_game(o.matrix_world.translation + c), "rot_y": 0.0,
                    "scale": [round(mx.x - mn.x, 3), round(mx.z - mn.z, 3), round(mx.y - mn.y, 3)], "solid": True, "invisible": True})
    return out


def world_box(o):
    """Axis-aligned bounds of an object in Blender space: (min, max)."""
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), \
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))


def is_own_model(o):
    m = o.get("unc_model", "")
    return o.type == "MESH" and (o.get("unc_kind") is None or m.startswith(OWN_MODEL_DIRS))


def collect(context, models_rel, base_ids, base_objs):
    """Walk the scene once: pieces (props), objects, spawns and lights, ready for either export."""
    gdir = game_dir(context)
    models_dir = os.path.join(gdir, models_rel)
    if os.path.isdir(models_dir):
        shutil.rmtree(models_dir)          # your own models are rebuilt from the scene every time
    os.makedirs(models_dir, exist_ok=True)
    palette = bpy.data.collections.get(COL_PALETTE)
    in_palette = set(palette.objects) if palette else set()
    used = {o.name for o in context.scene.objects} | base_ids | {i for k in KINDS for i in base_objs.get(k, {})}
    counter = [0]
    renames = []        # new objects get their final name after the walk, so their id stays the same next time

    def chosen_id(o, prefix):
        """A new object renamed by the user to e.g. 'obj:my_gate' gets that id (if it's free)."""
        if not o.name.startswith(prefix):
            return None
        want = safe_name(re.sub(r"\.\d+$", "", o.name[len(prefix):]))
        if not want or want.startswith("TEMPLATE") or want == o.get("unc_id") or want in used:
            return None
        used.add(want)
        return want

    def keep_id(o, prefix, oid):
        renames.append((o, prefix + oid, oid))

    def new_id(stem):
        while True:
            counter[0] += 1
            nid = f"edit_{safe_name(stem)}_{counter[0]}"
            if nid not in used:
                used.add(nid)
                return nid

    out = {"modify": {}, "props": [], "seen_props": set(), "objs": {k: [] for k in KINDS}, "seen": {k: set() for k in KINDS},
           "spawns": {}, "lights": [], "tilted": 0, "custom": 0}
    used_custom = set()
    baked = {}          # mesh name -> (model path, local anchor): edited pieces that share a mesh share one model file
    ref_hash = {}       # model -> fingerprint of the untouched model
    cache = {}

    def own_uvs(o):
        """True when the UVs differ from the original model's: you unwrapped it, so the game mustn't scale them."""
        model = o["unc_model"]
        if model.startswith(OWN_MODEL_DIRS):
            return False
        if "unc_uvhash" in o.data:
            ref = o.data["unc_uvhash"]
        else:
            m = model_mesh(gdir, model, cache)
            ref = uv_hash(m) if m else None
        return ref is not None and uv_hash(o.data) != ref

    def edited(o):
        if o.get("unc_model", "").startswith(OWN_MODEL_DIRS):
            return True
        model = o["unc_model"]
        if "unc_hash" in o.data:
            ref = o.data["unc_hash"]
        else:                                   # a scene saved before fingerprints: load the original to compare
            if model not in ref_hash:
                m = model_mesh(gdir, model, cache)
                ref_hash[model] = mesh_hash(m) if m else None
            ref = ref_hash[model]
        return ref is not None and mesh_hash(o.data) != ref

    for o in context.scene.objects:
        kind = o.get("unc_kind")
        if o in in_palette and o.name == o.get("unc_id"):
            continue                       # the palette itself
        if o.name.startswith("__unc"):
            continue
        if o.type == "LIGHT" and o.data.type == "POINT":
            c = o.data.color
            out["lights"].append({"pos": to_game(o.location), "color": [round(c[0], 3), round(c[1], 3), round(c[2], 3)],
                                  "radius": round(max(0.5, o.data.energy / 60.0), 2)})
            continue
        if o.type not in ("MESH", "EMPTY") or (kind is None and o.hide_get()):
            continue
        if kind == "sprite_child":
            continue
        tilt_x = o.rotation_euler.x - (math.radians(90) if o.get("unc_upright") else 0.0)
        if kind is not None and (abs(tilt_x) > EPS or abs(o.rotation_euler.y) > EPS):
            out["tilted"] += 1
        rot = round(math.degrees(o.rotation_euler.z), 2) + 0.0
        # --- collision boxes: meshes named COL... become invisible solid boxes
        if o.type == "MESH" and kind is None and o.name.lower().startswith("col"):
            mn, mx = world_box(o)
            o["unc_custom_id"] = safe_name(o.name)        # Import skips it next time: this object is the source
            out["props"].append({"id": safe_name(o.name), "model": BOX_MODEL,
                                 "pos": to_game(Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))), "rot_y": 0.0,
                                 "scale": [round(mx.x - mn.x, 3), round(mx.z - mn.z, 3), round(mx.y - mn.y, 3)], "solid": True, "invisible": True})
            continue
        # --- game pieces you reshaped or retextured (Edit Mode, materials, Ctrl+A): saved as your own model, still turned
        if kind in ("prop", "palette") and o.type == "MESH" and o.data.vertices and edited(o):
            if o.data.name not in baked:
                taken = {os.path.basename(v[0])[:-4] for v in baked.values()}
                stem = re.sub(r"(_edit\d+)+$", "", safe_name(os.path.basename(o["unc_model"])[:-4]))
                if o["unc_model"].startswith(OWN_MODEL_DIRS) and os.path.basename(o["unc_model"])[:-4] not in taken:
                    name = os.path.basename(o["unc_model"])[:-4]       # already one of yours: keep its file name
                else:
                    n = 1
                    while f"{stem}_edit{n}" in taken:
                        n += 1
                    name = f"{stem}_edit{n}"
                rel = f"{models_rel}/{name}.glb"
                baked[o.data.name] = (rel, export_local_glb(o.data, gdir, rel))
                out["custom"] += 1
            rel, anchor = baked[o.data.name]
            own = o["unc_model"].startswith(OWN_MODEL_DIRS)
            src = json.loads(o.get("unc_prop", "{}"))
            if own_uvs(o):
                o["game_uv_x"], o["game_uv_y"] = 1.0, 1.0    # your unwrap is used as it is (also in Blender's preview)
            p = {"model": rel, "pos": to_game(o.matrix_world @ anchor), "rot_y": rot, "scale": scale_to_game(o.scale),
                 "solid": bool(o.uncounted_solid) if own else bool(o.get("game_solid", True)),
                 "uv_scale": [round(float(o.get("game_uv_x", 1.0)), 3), round(float(o.get("game_uv_y", 1.0)), 3)]}
            ramp = {"PX": "+x", "NX": "-x", "PY": "-z", "NY": "+z"}.get(o.uncounted_ramp) if own else src.get("ramp")
            if ramp:
                p["ramp"] = ramp
            if "emitter" in src:
                p["emitter"] = src["emitter"]
            pid = o.name if (kind == "prop" and o.name == o["unc_id"]) else new_id(os.path.basename(o["unc_model"])[:-4])
            if p["solid"] and not ramp:
                cols = fit_props(o, pid)
                if cols:
                    p["solid"] = False                 # the shape-fitting boxes do the blocking
                    out["props"].extend(cols)
            if kind == "prop" and o.name == o["unc_id"] and o["unc_id"] in base_ids:
                out["seen_props"].add(o.name)
                out["modify"][o.name] = p
            else:
                p["id"] = pid
                out["props"].append(p)
            continue
        # --- your own models
        if is_own_model(o) and kind is None:
            if not o.data.vertices:
                continue
            cid = o.get("unc_custom_id") or (safe_name(o.name) if safe_name(o.name).startswith("custom_") else "custom_" + safe_name(o.name))
            if cid in used_custom:
                cid = new_id(cid)
            used_custom.add(cid)
            if o.uncounted_tile <= 0.0 and abs(o.rotation_euler.x) < EPS and abs(o.rotation_euler.y) < EPS:
                # Kept in its own space, turned and scaled in the game: identical copies (50 trees) share one model file.
                key = "own:" + mesh_hash(o.data)
                if key not in baked:
                    rel = f"{models_rel}/{cid[len('custom_'):] if cid.startswith('custom_') else cid}.glb"
                    baked[key] = (rel, export_local_glb(o.data, gdir, rel))
                rel, anchor = baked[key]
                p = {"id": cid, "model": rel, "pos": to_game(o.matrix_world @ anchor), "rot_y": rot, "scale": scale_to_game(o.scale),
                     "solid": bool(o.uncounted_solid)}
            else:
                rel = f"{models_rel}/{cid[len('custom_'):] if cid.startswith('custom_') else cid}.glb"
                anchor = export_mesh_glb(o, gdir, rel)
                p = {"id": cid, "model": rel, "pos": to_game(anchor), "rot_y": 0.0, "scale": [1, 1, 1], "solid": bool(o.uncounted_solid)}
            if o.uncounted_ramp != "NONE":
                p["ramp"] = {"PX": "+x", "NX": "-x", "PY": "-z", "NY": "+z"}[o.uncounted_ramp]
            elif p["solid"]:
                cols = fit_props(o, cid)
                if cols:
                    p["solid"] = False
                    out["props"].extend(cols)
            out["props"].append(p)
            if kind is None:
                o["unc_custom_id"] = cid
            out["custom"] += 1
            continue
        if kind in ("prop", "palette"):
            pos, sc = to_game(o.location), scale_to_game(o.scale)
            solid = bool(o.get("game_solid", True))
            uv = [round(float(o.get("game_uv_x", 1.0)), 3), round(float(o.get("game_uv_y", 1.0)), 3)]
            if kind == "prop" and o.name == o["unc_id"] and o["unc_id"] in base_ids:
                out["seen_props"].add(o.name)
                b = json.loads(o["unc_base"])
                mod = {}
                if any(abs(a - c) > EPS for a, c in zip(pos, b["pos"])):
                    mod["pos"] = pos
                if abs(((rot - b["rot_y"]) + 180) % 360 - 180) > 0.05:
                    mod["rot_y"] = rot
                if any(abs(a - c) > EPS for a, c in zip(sc, b["scale"])):
                    mod["scale"] = sc
                if solid != b["solid"]:
                    mod["solid"] = solid
                if any(abs(a - c) > EPS for a, c in zip(uv, b["uv_scale"])):
                    mod["uv_scale"] = uv
                if mod:
                    out["modify"][o.name] = mod
            else:
                src = json.loads(o["unc_prop"])
                keep = kind == "prop" and o.name == o["unc_id"]
                nid = o.name if keep else new_id(os.path.basename(o["unc_model"])[:-4])
                p = {"id": nid, "model": o["unc_model"], "pos": pos, "rot_y": rot, "scale": sc, "solid": solid}
                if o.get("game_invisible"):
                    p["invisible"] = True
                else:
                    p["uv_scale"] = uv
                for k in ("ramp", "emitter"):
                    if k in src:
                        p[k] = src[k]
                out["props"].append(p)
        elif kind == "spawns":
            original = o.name == "spawn:" + o["unc_id"] and not o.get("unc_template")
            sid = o["unc_id"] if original else (chosen_id(o, "spawn:") or new_id("spawn"))
            if not original:
                keep_id(o, "spawn:", sid)
            out["spawns"][sid] = {"pos": to_game(o.location - Vector((0, 0, o.get("unc_lift", 0.0)))), "yaw_degrees": rot}
        elif kind in KINDS:
            original = o.name == PREFIX[kind] + o["unc_id"] and not o.get("unc_template")
            oid = o["unc_id"] if original else (chosen_id(o, PREFIX[kind]) or new_id(o["unc_id"].replace("TEMPLATE:", "").split(":")[-1]))
            if not original:
                keep_id(o, PREFIX[kind], oid)   # from now on this object keeps its id (levers can point at it)
            d = object_def(o, kind, oid)
            base = base_objs.get(kind, {})
            if original:
                out["seen"][kind].add(oid)
            if not (original and oid in base and round_def(d, kind) == round_def(base[oid], kind)):
                out["objs"][kind].append(d)
    for o, name, oid in renames:
        o.name = name
        o["unc_id"] = oid
        if "unc_template" in o:
            del o["unc_template"]
    return out


class UNC_OT_export(bpy.types.Operator):
    bl_idname = "uncounted.export"
    bl_label = "Export"
    bl_description = "Save into the game: the world's level, or your new map in content/maps/custom/<name>"

    def execute(self, context):
        gdir = game_dir(context)
        sc = context.scene
        if sc.uncounted_mode == "WORLD":
            if "unc_base_ids" not in sc:
                self.report({"ERROR"}, "Import the world first (or start a New Map).")
                return {"CANCELLED"}
            base_ids = set(json.loads(sc["unc_base_ids"]))
            base_objs = json.loads(sc["unc_base"])
            r = collect(context, LEVEL_MODELS, base_ids, base_objs)
            edits = {"schema": 4, "map": WORLD_ID,
                     "props": {"modify": r["modify"], "add": r["props"], "remove": sorted(base_ids - r["seen_props"])}}
            for k in KINDS:
                edits[k] = {"set": r["objs"][k], "remove": sorted(set(base_objs.get(k, {})) - r["seen"][k])}
            extra = json.loads(sc.get("unc_base_extra", "{}"))
            if "lights" in extra and lights_key(r["lights"]) != extra["lights"]:
                edits["lights"] = r["lights"]              # lights changed: the whole list is yours now
            if "spawns" in extra and spawns_key(r["spawns"]) != extra["spawns"]:
                edits["spawns"] = r["spawns"]
            if not sc.uncounted_keep_scatter:
                edits["scatter"] = []                      # no grass tufts and flowers: you're making your own ground
            base_path, map_path = os.path.join(gdir, BASE_REL), os.path.join(gdir, MAP_REL)
            if not os.path.exists(base_path):
                shutil.copyfile(map_path, base_path)        # first save: keep the untouched level as the base
            base = read_json(base_path)
            ids = {p["id"] for p in base.get("props", [])}
            if ids != base_ids:
                self.report({"ERROR"}, "The game's level changed since you imported it. Import World again, then redo this change.")
                return {"CANCELLED"}
            with open(os.path.join(gdir, CHANGES_REL), "w", encoding="utf-8") as f:
                json.dump(edits, f, indent=2)
            with open(map_path, "w", encoding="utf-8") as f:   # the level the game plays: the base plus your changes
                json.dump(apply_edits(base, edits), f, indent=2, ensure_ascii=False)
            old = os.path.join(gdir, OLD_EDITS_REL)
            if os.path.exists(old):                            # changes saved by the older version are now in the game
                os.replace(old, old + ".moved_into_game")
            msg = (f"Saved into the game's level: {len(r['modify'])} changed, {len(r['props'])} added ({r['custom']} your own models), "
                   f"{len(edits['props']['remove'])} removed; {sum(len(edits[k]['set']) for k in KINDS)} objects added or changed, "
                   f"{sum(len(edits[k]['remove']) for k in KINDS)} removed")
        else:
            slug = map_slug(context)
            r = collect(context, f"{CUSTOM_MODELS}/{slug}", set(), {})
            spawns = r["spawns"] or {"start": {"pos": [0.0, 0.0, 0.0], "yaw_degrees": 0.0}}
            pano = {"NONE": "", "NIGHT": "assets/textures/sky/sky_night.png", "DUSK": "assets/textures/sky/sky_dusk.png"}[sc.uncounted_panorama]
            m = {"schema_version": 1, "id": "core:map." + slug, "display_name_key": sc.uncounted_map_name,
                 "music": sc.uncounted_music, "ambience": sc.uncounted_ambience,
                 "sky_color": [int(round(c * 255)) for c in sc.uncounted_sky], "ambient_color": [round(c, 3) for c in sc.uncounted_ambient],
                 "sun_direction": [-0.3, 0.8, -0.3], "sun_color": [round(c, 3) for c in sc.uncounted_sun],
                 "fog_color": [round(c, 3) for c in sc.uncounted_fog], "fog_density": round(sc.uncounted_fog_density, 4),
                 "weather": "" if sc.uncounted_weather == "NONE" else sc.uncounted_weather, "sky_panorama": pano,
                 "day_night": bool(sc.uncounted_day_night),
                 "spawns": spawns, "props": r["props"], "lights": r["lights"]}
            for k in KINDS:
                m[k] = r["objs"][k]
            os.makedirs(os.path.join(gdir, CUSTOM_MAPS, slug), exist_ok=True)
            with open(os.path.join(gdir, CUSTOM_MAPS, slug, "map.json"), "w", encoding="utf-8") as f:
                json.dump(m, f, indent=2)
            old = os.path.join(gdir, OLD_USER_MAPS, slug, "map.json")
            if os.path.exists(old):                            # saved by the older version: now it's in the game
                os.replace(old, old + ".moved_into_game")
            msg = (f"Saved map '{sc.uncounted_map_name}' (id core:map.{slug}): {len(r['props'])} pieces ({r['custom']} your own), "
                   f"{sum(len(m[k]) for k in KINDS)} objects, {len(spawns)} spawn points, {len(r['lights'])} lights")
        if r["tilted"]:
            msg += f". Note: {r['tilted']} tilted object(s): the game only turns things around Z"
        self.report({"INFO"}, msg)
        return {"FINISHED"}


class UNC_OT_sprite(bpy.types.Operator):
    bl_idname = "uncounted.sprite"
    bl_label = "Update Sprite"
    bl_description = "Show the selected NPCs and monsters with the sprite of their current npc_id / creature_id"

    def execute(self, context):
        gdir = game_dir(context)
        _DEFS.pop(gdir, None)
        for o in list(context.selected_objects):
            if o.get("unc_kind") in ("npcs", "creatures") and o.type == "EMPTY":
                apply_sprite(gdir, o)
        return {"FINISHED"}


class UNC_OT_trunk(bpy.types.Operator):
    bl_idname = "uncounted.trunk"
    bl_label = "Trunk Collision"
    bl_description = ("Trees and lamp posts: block the player only at the trunk. Adds an invisible COL post the size of the "
                      "bottom of the mesh (attached, so it moves with it) and turns the mesh's own collision off")

    def execute(self, context):
        n = 0
        for o in list(context.selected_objects):
            if o.type != "MESH" or o.name.lower().startswith("col") or not o.data.vertices:
                continue
            for c in list(o.children):                 # replace an earlier trunk post
                if c.name.lower().startswith("col") and c.get("unc_trunk"):
                    bpy.data.objects.remove(c, do_unlink=True)
            pts = [o.matrix_world @ v.co for v in o.data.vertices]
            z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
            low = [p for p in pts if p.z <= z0 + 0.4] or pts
            x0, x1 = min(p.x for p in low), max(p.x for p in low)
            y0, y1 = min(p.y for p in low), max(p.y for p in low)
            w, d, h = max(0.25, x1 - x0), max(0.25, y1 - y0), min(2.4, max(0.5, z1 - z0))
            import bmesh
            bm = bmesh.new()
            bmesh.ops.create_cube(bm, size=1.0)
            me = bpy.data.meshes.new("COL_trunk")
            bm.to_mesh(me)
            bm.free()
            col = bpy.data.objects.new(f"COL_{o.name}_trunk", me)
            for uc in o.users_collection:
                uc.objects.link(col)
            col.location = ((x0 + x1) / 2, (y0 + y1) / 2, z0 + h / 2)
            col.scale = (w, d, h)
            col.display_type = "WIRE"
            col.hide_render = True
            col["unc_trunk"] = True
            col.parent = o
            col.matrix_parent_inverse = o.matrix_world.inverted()
            o.uncounted_solid = False
            if "game_solid" in o:
                o["game_solid"] = False
            n += 1
        self.report({"INFO"}, f"Trunk collision on {n} object(s). Copy a tree together with its COL post (select both, Shift+D)")
        return {"FINISHED"}


class UNC_OT_unique(bpy.types.Operator):
    bl_idname = "uncounted.unique"
    bl_label = "Make Only This One Editable"
    bl_description = "Give the selected pieces their own copy of the mesh, so Edit Mode changes only them"

    def execute(self, context):
        for o in context.selected_objects:
            if o.type == "MESH" and o.data.users > 1:
                o.data = o.data.copy()
        return {"FINISHED"}


class UNC_OT_tile(bpy.types.Operator):
    bl_idname = "uncounted.tile"
    bl_label = "Tile Texture Now"
    bl_description = "Replace the UVs of the selected meshes so the texture repeats every 'Auto-tile texture' metres"

    def execute(self, context):
        n = 0
        for o in context.selected_objects:
            if o.type == "MESH" and is_own_model(o) and o.uncounted_tile > 0.0:
                tile_uvs(o.data, o.uncounted_tile, o.matrix_world)
                n += 1
        self.report({"INFO"}, f"Tiled {n} mesh(es)")
        return {"FINISHED"}


class UNC_OT_move_work(bpy.types.Operator):
    bl_idname = "uncounted.move_work"
    bl_label = "Move My Work to New Version"
    bl_description = ("After downloading a new version of the game: unzip it to a NEW folder, pick that folder here. Your "
                      "level changes, models and maps are copied into it and its level is rebuilt with your changes")
    directory: bpy.props.StringProperty(subtype="DIR_PATH")

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        src, dst = game_dir(context), bpy.path.abspath(self.directory)
        if not os.path.exists(os.path.join(dst, MAP_REL)):
            self.report({"ERROR"}, f"{dst} isn't a game folder (no {MAP_REL}). Pick the folder with game.exe in it.")
            return {"CANCELLED"}
        if os.path.normpath(src) == os.path.normpath(dst):
            self.report({"ERROR"}, "That's the folder you're already using. Unzip the new version to a different folder.")
            return {"CANCELLED"}
        copied = 0
        for rel in (CHANGES_REL, LEVEL_MODELS, CUSTOM_MAPS, CUSTOM_MODELS):
            a, b = os.path.join(src, rel), os.path.join(dst, rel)
            if os.path.isfile(a):
                os.makedirs(os.path.dirname(b), exist_ok=True)
                shutil.copyfile(a, b)
                copied += 1
            elif os.path.isdir(a):
                shutil.copytree(a, b, dirs_exist_ok=True)
                copied += sum(len(f) for _, _, f in os.walk(a))
        base_path = os.path.join(dst, BASE_REL)
        if not os.path.exists(base_path):
            shutil.copyfile(os.path.join(dst, MAP_REL), base_path)
        missing = []
        changes = os.path.join(dst, CHANGES_REL)
        if os.path.exists(changes):
            base = read_json(base_path)
            edits = read_json(changes)
            ids = {p["id"] for p in base.get("props", [])}
            pe = edits.get("props", {})
            missing = [i for i in list(pe.get("remove", [])) + list(pe.get("modify", {})) if i not in ids]
            with open(os.path.join(dst, MAP_REL), "w", encoding="utf-8") as f:
                json.dump(apply_edits(base, edits), f, indent=2, ensure_ascii=False)
        _DEFS.clear()
        context.scene.uncounted_game_dir = dst
        msg = f"Moved {copied} files of your work into {dst} and rebuilt its level. Game folder is now the new one."
        if missing:
            msg += f" Note: {len(missing)} changed piece(s) no longer exist in the new version: {', '.join(missing[:5])}"
        self.report({"INFO"}, msg + " Press Import World to see it.")
        return {"FINISHED"}


class UNC_OT_pack(bpy.types.Operator):
    bl_idname = "uncounted.pack"
    bl_label = "Pack My Changes"
    bl_description = "Zip your level changes, new maps and models into my_level_changes.zip in the game folder, to send to the developer"

    def execute(self, context):
        import zipfile
        gdir = game_dir(context)
        out = os.path.join(gdir, PACK_NAME)
        n = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for rel in (MAP_REL, BASE_REL, CHANGES_REL, LEVEL_MODELS, CUSTOM_MAPS, CUSTOM_MODELS):
                path = os.path.join(gdir, rel)
                if os.path.isfile(path):
                    z.write(path, rel)
                    n += 1
                elif os.path.isdir(path):
                    for root, _, files in os.walk(path):
                        for f in files:
                            full = os.path.join(root, f)
                            z.write(full, os.path.relpath(full, gdir).replace(os.sep, "/"))
                            n += 1
        self.report({"INFO"}, f"Packed {n} files into {out}")
        return {"FINISHED"}


# ----------------------------------------------------------------------------------------------- UI
class UNC_PT_panel(bpy.types.Panel):
    bl_label = "The Uncounted"
    bl_idname = "UNC_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Uncounted"

    def draw(self, context):
        sc = context.scene
        lay = self.layout
        lay.prop(sc, "uncounted_game_dir")
        row = lay.row()
        row.prop(sc, "uncounted_mode", expand=True)
        if sc.uncounted_mode == "WORLD":
            lay.operator("uncounted.import_world", icon="IMPORT")
            lay.prop(sc, "uncounted_keep_scatter")
        else:
            lay.prop(sc, "uncounted_map_name")
            row = lay.row(align=True)
            row.operator("uncounted.new_map", icon="ADD")
            row.operator("uncounted.import_map", icon="IMPORT")
            box = lay.box()
            box.label(text="Map atmosphere", icon="WORLD")
            box.prop(sc, "uncounted_day_night")
            for p in ("uncounted_sky", "uncounted_fog", "uncounted_fog_density", "uncounted_ambient", "uncounted_sun",
                      "uncounted_weather", "uncounted_panorama", "uncounted_music", "uncounted_ambience"):
                box.prop(sc, p)
        lay.operator("uncounted.export", icon="EXPORT")
        lay.operator("uncounted.pack", icon="PACKAGE")
        lay.operator("uncounted.move_work", icon="FILE_REFRESH")
        o = context.active_object
        if o is not None:
            box = lay.box()
            box.label(text=o.name, icon="OBJECT_DATA")
            if o.type == "MESH" and is_own_model(o) and not o.name.lower().startswith("col"):
                box.label(text="Your own model")
                box.prop(o, "uncounted_solid")
                box.prop(o, "uncounted_ramp")
                box.prop(o, "uncounted_fit")
                box.prop(o, "uncounted_tile")
                box.operator("uncounted.tile", icon="TEXTURE")
            elif o.type == "MESH" and o.get("unc_kind") is None and o.name.lower().startswith("col"):
                box.label(text="Invisible collision box")
            if o.type == "MESH" and o.get("unc_kind") in ("prop", "palette") and not o.get("game_invisible"):
                box.prop(o, "uncounted_fit")
            if o.type == "MESH" and not o.name.lower().startswith("col"):
                box.operator("uncounted.trunk", icon="OUTLINER_OB_FORCE_FIELD")
            if o.type == "MESH" and o.data.users > 1 and o.get("unc_kind") in ("prop", "palette"):
                box.label(text=f"Shares its mesh with {o.data.users - 1} other(s):")
                box.label(text="Edit Mode changes them all.")
                box.operator("uncounted.unique", icon="DUPLICATE")
            for k in sorted(k for k in o.keys() if k.startswith("game_")):
                box.prop(o, f'["{k}"]', text=k[5:])
            if o.get("unc_kind") in ("npcs", "creatures"):
                box.operator("uncounted.sprite", icon="IMAGE_DATA")
        col = lay.column(align=True)
        col.label(text="Add: Shift+D a palette piece or template")
        col.label(text="Turn around Z only (R, Z)")
        col.label(text="Name a mesh COL... for an invisible wall")


CLASSES = (UNC_OT_import_world, UNC_OT_new_map, UNC_OT_import_map, UNC_OT_export, UNC_OT_sprite, UNC_OT_trunk, UNC_OT_unique, UNC_OT_tile, UNC_OT_move_work, UNC_OT_pack, UNC_PT_panel)


def register():
    S, O, P = bpy.types.Scene, bpy.types.Object, bpy.props
    S.uncounted_game_dir = P.StringProperty(name="Game folder", subtype="DIR_PATH", default="")
    S.uncounted_mode = P.EnumProperty(name="Mode", items=[("WORLD", "Edit World", "Change the game's world"),
                                                          ("MAP", "New Map", "Build your own map")], default="WORLD")
    S.uncounted_map_name = P.StringProperty(name="Map name", default="My Map")
    S.uncounted_day_night = P.BoolProperty(name="Day and night", default=True,
                                           description="Outdoor map: follows the game's clock (dawn, day, dusk, night). "
                                                       "Untick for caves and interiors that always look as you set them")
    S.uncounted_keep_scatter = P.BoolProperty(name="Keep grass & flowers", default=True,
                                              description="The game's grass tufts and wild flowers on the ground. Untick when you rebuild the ground yourself")
    S.uncounted_sky = P.FloatVectorProperty(name="Sky", subtype="COLOR", min=0, max=1, default=(0.09, 0.11, 0.17))
    S.uncounted_fog = P.FloatVectorProperty(name="Fog", subtype="COLOR", min=0, max=1, default=(0.08, 0.10, 0.16))
    S.uncounted_fog_density = P.FloatProperty(name="Fog density", min=0.0, max=0.2, default=0.025, precision=3)
    S.uncounted_ambient = P.FloatVectorProperty(name="Ambient light", subtype="COLOR", min=0, max=1.5, default=(0.4, 0.42, 0.5))
    S.uncounted_sun = P.FloatVectorProperty(name="Moon/sun light", subtype="COLOR", min=0, max=1.5, default=(0.5, 0.5, 0.6))
    S.uncounted_weather = P.EnumProperty(name="Weather", items=[("NONE", "Clear", ""), ("rain", "Rain", ""), ("dust", "Dust", ""),
                                                                ("fireflies", "Fireflies", "")], default="NONE")
    S.uncounted_panorama = P.EnumProperty(name="Horizon", items=[("NONE", "None", ""), ("NIGHT", "Night sky", ""), ("DUSK", "Dusk sky", "")],
                                          default="NIGHT")
    S.uncounted_music = P.StringProperty(name="Music", default="assets/audio/music/old_road_theme.wav")
    S.uncounted_ambience = P.StringProperty(name="Ambience", default="assets/audio/ambience/forest_wind.wav")
    O.uncounted_solid = P.BoolProperty(name="Solid (blocks the player)", default=True)
    O.uncounted_ramp = P.EnumProperty(name="Ramp", items=[("NONE", "Not a ramp", ""), ("PX", "Rises towards +X", ""), ("NX", "Rises towards -X", ""),
                                                          ("PY", "Rises towards +Y", ""), ("NY", "Rises towards -Y", "")], default="NONE")
    O.uncounted_fit = P.BoolProperty(name="Collision fits the shape", default=True,
                                     description="Block the player with boxes that follow the mesh (doorways and arches stay open). "
                                                 "Off: one box around the whole mesh")
    O.uncounted_tile = P.FloatProperty(name="Auto-tile texture (m)", min=0.0, max=20.0, default=0.0, precision=2,
                                       description="0 (default): your own UV unwrap is used exactly as it is. Above 0: Export "
                                                   "replaces the UVs so the texture repeats every this many metres")
    for c in CLASSES:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
    for name in ("uncounted_game_dir", "uncounted_mode", "uncounted_map_name", "uncounted_keep_scatter", "uncounted_day_night", "uncounted_sky", "uncounted_fog", "uncounted_fog_density",
                 "uncounted_ambient", "uncounted_sun", "uncounted_weather", "uncounted_panorama", "uncounted_music", "uncounted_ambience"):
        delattr(bpy.types.Scene, name)
    del bpy.types.Object.uncounted_solid
    del bpy.types.Object.uncounted_ramp
    del bpy.types.Object.uncounted_tile
    del bpy.types.Object.uncounted_fit


if __name__ == "__main__":
    register()

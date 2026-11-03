"""
The Uncounted: level editor add-on for Blender (4.0+).

Edit the game world, or build brand-new maps, in Blender. Full guide: docs/LEVEL_EDITOR.md.

  Install:  Edit > Preferences > Add-ons > Install... > pick this file > tick "The Uncounted: Level Editor".
  Use:      3D Viewport > press N > "Uncounted" tab. Set "Game folder" (the folder with game.exe).

  Edit the world:  Import World -> edit -> Export. Saved to mods/level_edits/ (only your changes).
  Build a map:     New Map (or Import My Map) -> build -> Export. Saved to mods/user_maps/<name>/ (the whole map).
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
    "version": (3, 0, 0),
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

EDITS_DIR = "mods/level_edits"
EDITS_REL = EDITS_DIR + "/map_edits.json"
USER_MAPS = "mods/user_maps"
MAP_REL = "content/maps/edrath_world.json"
WORLD_ID = "core:map.edrath"
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
            for mat in mesh.materials:
                if mat and mat.use_nodes:
                    for n in mat.node_tree.nodes:
                        if n.type == "TEX_IMAGE":
                            n.interpolation = "Closest"
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


def make_object(gdir, cache, kind, d, name):
    """A game object as a Blender object: its real model when it has one, else a labelled marker."""
    mesh = model_mesh(gdir, d.get("model", ""), cache) if kind == "interactables" else None
    o = bpy.data.objects.new(name, mesh)
    if mesh is None:
        o.empty_display_type = SHAPE[kind]
        o.empty_display_size = 0.5 if kind in ("portals", "spawns") else 0.4
        o.location = to_blender(d.get("pos", [0, 0, 0])) + Vector((0, 0, MARKER_LIFT))
        o["unc_lift"] = MARKER_LIFT
    else:
        o.location = to_blender(d.get("pos", [0, 0, 0]))
        o.scale = scale_to_blender(d.get("scale", [1, 1, 1]))
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
    if p["model"].startswith(EDITS_DIR + "/models") or p["model"].startswith(USER_MAPS + "/"):
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
        cp.objects.link(o)


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
        base = read_json(map_path)
        edits_path = os.path.join(gdir, EDITS_REL)
        world = apply_edits(json.loads(json.dumps(base)), read_json(edits_path)) if os.path.exists(edits_path) else base
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co = collection(COL_WORLD), collection(COL_OBJECTS)
        cache, skipped = {}, 0
        base_props = {p["id"]: p for p in base.get("props", [])}
        own = {o.get("unc_custom_id") for o in context.scene.objects if o.get("unc_custom_id")}
        for p in world.get("props", []):
            if p["id"] in own:
                continue                               # your own model: its source mesh is already in the scene
            if add_prop_object(gdir, cache, p, cw, base_props) is None:
                skipped += 1
        for kind in KINDS:
            for e in world.get(kind, []):
                co.objects.link(make_object(gdir, cache, kind, e, PREFIX[kind] + e[IDKEY[kind]]))
        build_palette(gdir, cache, base.get("props", []))
        context.scene["unc_base"] = json.dumps({k: {e[IDKEY[k]]: e for e in base.get(k, [])} for k in KINDS})
        context.scene["unc_base_ids"] = json.dumps(sorted(base_props))
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
        context.scene.uncounted_mode = "MAP"
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co, cache = collection(COL_WORLD), collection(COL_OBJECTS), {}
        add_prop_object(gdir, cache, {"id": "starter_floor", "model": "assets/models/env/floor_cobble.glb", "pos": [0, -0.5, 0],
                                      "scale": [20, 0.5, 20], "solid": False, "uv_scale": [8, 8]}, cw)
        co.objects.link(make_object(gdir, cache, "spawns", {"id": "start", "pos": [0, 0, 0]}, "spawn:start"))
        build_palette(gdir, cache, read_json(os.path.join(gdir, MAP_REL)).get("props", []))
        self.report({"INFO"}, f"New map '{context.scene.uncounted_map_name}': build away, then Export.")
        return {"FINISHED"}


class UNC_OT_import_map(bpy.types.Operator):
    bl_idname = "uncounted.import_map"
    bl_label = "Import My Map"
    bl_description = "Load the map named above from mods/user_maps to keep working on it"

    def execute(self, context):
        gdir = game_dir(context)
        path = os.path.join(gdir, USER_MAPS, map_slug(context), "map.json")
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
        sc.uncounted_music = m.get("music", "")
        sc.uncounted_ambience = m.get("ambience", "")
        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co, cache = collection(COL_WORLD), collection(COL_OBJECTS), {}
        own = {o.get("unc_custom_id") for o in sc.objects if o.get("unc_custom_id")}
        for p in m.get("props", []):
            if p["id"] not in own:
                add_prop_object(gdir, cache, p, cw)
        for kind in KINDS:
            for e in m.get(kind, []):
                co.objects.link(make_object(gdir, cache, kind, e, PREFIX[kind] + e[IDKEY[kind]]))
        for sid, s in m.get("spawns", {}).items():
            co.objects.link(make_object(gdir, cache, "spawns", {"id": sid, "pos": s["pos"], "yaw_degrees": s.get("yaw_degrees", 0.0)},
                                        "spawn:" + sid))
        for i, l in enumerate(m.get("lights", [])):
            ld = bpy.data.lights.new(f"light_{i}", "POINT")
            ld.color = l.get("color", [1, 0.75, 0.4])
            ld.energy = l.get("radius", 10.0) * 60.0
            lo = bpy.data.objects.new(f"light_{i}", ld)
            lo.location = to_blender(l["pos"])
            cw.objects.link(lo)
        build_palette(gdir, cache, read_json(os.path.join(gdir, MAP_REL)).get("props", []))
        self.report({"INFO"}, f"Loaded your map '{sc.uncounted_map_name}'.")
        return {"FINISHED"}


# ----------------------------------------------------------------------------------------------- export
def tile_uvs(mesh, size):
    """Box-project the texture so it repeats every `size` metres, however big the mesh is (like the game's walls)."""
    if not mesh.uv_layers:
        mesh.uv_layers.new(name="UVMap")
    uv = mesh.uv_layers.active.data
    for poly in mesh.polygons:
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = mesh.vertices[mesh.loops[li].vertex_index].co
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


def world_box(o):
    """Axis-aligned bounds of an object in Blender space: (min, max)."""
    pts = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts))), \
        Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))


def is_own_model(o):
    m = o.get("unc_model", "")
    return o.type == "MESH" and (o.get("unc_kind") is None or m.startswith(EDITS_DIR + "/models") or m.startswith(USER_MAPS + "/"))


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
    for o in context.scene.objects:
        kind = o.get("unc_kind")
        if o in in_palette and o.name == o.get("unc_id"):
            continue                       # the palette itself
        if o.name.startswith("__unc"):
            continue
        if o.type == "LIGHT" and o.data.type == "POINT":
            c = o.data.color
            out["lights"].append({"pos": to_game(o.location), "color": [round(c[0], 3), round(c[1], 3), round(c[2], 3)],
                                  "radius": round(max(3.0, min(25.0, o.data.energy / 60.0)), 2)})
            continue
        if o.type not in ("MESH", "EMPTY") or (kind is None and o.hide_get()):
            continue
        if kind is not None and (abs(o.rotation_euler.x) > EPS or abs(o.rotation_euler.y) > EPS):
            out["tilted"] += 1
        rot = round(math.degrees(o.rotation_euler.z), 2) + 0.0
        # --- collision boxes: meshes named COL... become invisible solid boxes
        if o.type == "MESH" and kind is None and o.name.lower().startswith("col"):
            mn, mx = world_box(o)
            out["props"].append({"id": safe_name(o.name), "model": BOX_MODEL,
                                 "pos": to_game(Vector(((mn.x + mx.x) / 2, (mn.y + mx.y) / 2, mn.z))), "rot_y": 0.0,
                                 "scale": [round(mx.x - mn.x, 3), round(mx.z - mn.z, 3), round(mx.y - mn.y, 3)], "solid": True, "invisible": True})
            continue
        # --- your own models
        if is_own_model(o):
            if not o.data.vertices:
                continue
            cid = o.get("unc_custom_id") or (safe_name(o.name) if safe_name(o.name).startswith("custom_") else "custom_" + safe_name(o.name))
            if cid in used_custom:
                cid = new_id(cid)
            used_custom.add(cid)
            rel = f"{models_rel}/{cid[len('custom_'):] if cid.startswith('custom_') else cid}.glb"
            anchor = export_mesh_glb(o, gdir, rel)
            p = {"id": cid, "model": rel, "pos": to_game(anchor), "rot_y": 0.0, "scale": [1, 1, 1], "solid": bool(o.uncounted_solid)}
            if o.uncounted_ramp != "NONE":
                p["ramp"] = {"PX": "+x", "NX": "-x", "PY": "-z", "NY": "+z"}[o.uncounted_ramp]
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
            sid = o["unc_id"] if o.name == "spawn:" + o["unc_id"] and not o.get("unc_template") else new_id("spawn")
            out["spawns"][sid] = {"pos": to_game(o.location - Vector((0, 0, o.get("unc_lift", 0.0)))), "yaw_degrees": rot}
        elif kind in KINDS:
            original = o.name == PREFIX[kind] + o["unc_id"] and not o.get("unc_template")
            oid = o["unc_id"] if original else new_id(o["unc_id"].replace("TEMPLATE:", "").split(":")[-1])
            d = object_def(o, kind, oid)
            base = base_objs.get(kind, {})
            if original:
                out["seen"][kind].add(oid)
            if not (original and oid in base and round_def(d, kind) == round_def(base[oid], kind)):
                out["objs"][kind].append(d)
    return out


class UNC_OT_export(bpy.types.Operator):
    bl_idname = "uncounted.export"
    bl_label = "Export"
    bl_description = "World: save your changes to mods/level_edits. New map: save the whole map to mods/user_maps/<name>"

    def execute(self, context):
        gdir = game_dir(context)
        sc = context.scene
        if sc.uncounted_mode == "WORLD":
            if "unc_base_ids" not in sc:
                self.report({"ERROR"}, "Import the world first (or start a New Map).")
                return {"CANCELLED"}
            base_ids = set(json.loads(sc["unc_base_ids"]))
            base_objs = json.loads(sc["unc_base"])
            r = collect(context, EDITS_DIR + "/models", base_ids, base_objs)
            edits = {"schema": 3, "map": WORLD_ID,
                     "props": {"modify": r["modify"], "add": r["props"], "remove": sorted(base_ids - r["seen_props"])}}
            for k in KINDS:
                edits[k] = {"set": r["objs"][k], "remove": sorted(set(base_objs.get(k, {})) - r["seen"][k])}
            os.makedirs(os.path.join(gdir, EDITS_DIR), exist_ok=True)
            with open(os.path.join(gdir, EDITS_REL), "w", encoding="utf-8") as f:
                json.dump(edits, f, indent=2)
            msg = (f"Saved world edits: {len(r['modify'])} changed, {len(r['props'])} added ({r['custom']} your own models), "
                   f"{len(edits['props']['remove'])} removed; {sum(len(edits[k]['set']) for k in KINDS)} objects added or changed, "
                   f"{sum(len(edits[k]['remove']) for k in KINDS)} removed")
        else:
            slug = map_slug(context)
            r = collect(context, f"{USER_MAPS}/{slug}/models", set(), {})
            spawns = r["spawns"] or {"start": {"pos": [0.0, 0.0, 0.0], "yaw_degrees": 0.0}}
            pano = {"NONE": "", "NIGHT": "assets/textures/sky/sky_night.png", "DUSK": "assets/textures/sky/sky_dusk.png"}[sc.uncounted_panorama]
            m = {"schema_version": 1, "id": "user:map." + slug, "display_name_key": sc.uncounted_map_name,
                 "music": sc.uncounted_music, "ambience": sc.uncounted_ambience,
                 "sky_color": [int(round(c * 255)) for c in sc.uncounted_sky], "ambient_color": [round(c, 3) for c in sc.uncounted_ambient],
                 "sun_direction": [-0.3, 0.8, -0.3], "sun_color": [round(c, 3) for c in sc.uncounted_sun],
                 "fog_color": [round(c, 3) for c in sc.uncounted_fog], "fog_density": round(sc.uncounted_fog_density, 4),
                 "weather": "" if sc.uncounted_weather == "NONE" else sc.uncounted_weather, "sky_panorama": pano,
                 "spawns": spawns, "props": r["props"], "lights": r["lights"]}
            for k in KINDS:
                m[k] = r["objs"][k]
            os.makedirs(os.path.join(gdir, USER_MAPS, slug), exist_ok=True)
            with open(os.path.join(gdir, USER_MAPS, slug, "map.json"), "w", encoding="utf-8") as f:
                json.dump(m, f, indent=2)
            msg = (f"Saved map '{sc.uncounted_map_name}' (id user:map.{slug}): {len(r['props'])} pieces ({r['custom']} your own), "
                   f"{sum(len(m[k]) for k in KINDS)} objects, {len(spawns)} spawn points, {len(r['lights'])} lights")
        if r["tilted"]:
            msg += f". Note: {r['tilted']} tilted object(s): the game only turns things around Z"
        self.report({"INFO"}, msg)
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
        else:
            lay.prop(sc, "uncounted_map_name")
            row = lay.row(align=True)
            row.operator("uncounted.new_map", icon="ADD")
            row.operator("uncounted.import_map", icon="IMPORT")
            box = lay.box()
            box.label(text="Map atmosphere", icon="WORLD")
            for p in ("uncounted_sky", "uncounted_fog", "uncounted_fog_density", "uncounted_ambient", "uncounted_sun",
                      "uncounted_weather", "uncounted_panorama", "uncounted_music", "uncounted_ambience"):
                box.prop(sc, p)
        lay.operator("uncounted.export", icon="EXPORT")
        o = context.active_object
        if o is not None:
            box = lay.box()
            box.label(text=o.name, icon="OBJECT_DATA")
            if o.type == "MESH" and is_own_model(o) and not o.name.lower().startswith("col"):
                box.label(text="Your own model")
                box.prop(o, "uncounted_solid")
                box.prop(o, "uncounted_ramp")
                box.prop(o, "uncounted_tile")
            elif o.type == "MESH" and o.get("unc_kind") is None and o.name.lower().startswith("col"):
                box.label(text="Invisible collision box")
            for k in sorted(k for k in o.keys() if k.startswith("game_")):
                box.prop(o, f'["{k}"]', text=k[5:])
        col = lay.column(align=True)
        col.label(text="Add: Shift+D a palette piece or template")
        col.label(text="Turn around Z only (R, Z)")
        col.label(text="Name a mesh COL... for an invisible wall")


CLASSES = (UNC_OT_import_world, UNC_OT_new_map, UNC_OT_import_map, UNC_OT_export, UNC_PT_panel)


def register():
    S, O, P = bpy.types.Scene, bpy.types.Object, bpy.props
    S.uncounted_game_dir = P.StringProperty(name="Game folder", subtype="DIR_PATH", default="")
    S.uncounted_mode = P.EnumProperty(name="Mode", items=[("WORLD", "Edit World", "Change the game's world"),
                                                          ("MAP", "New Map", "Build your own map")], default="WORLD")
    S.uncounted_map_name = P.StringProperty(name="Map name", default="My Map")
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
    O.uncounted_tile = P.FloatProperty(name="Texture size (m)", min=0.0, max=20.0, default=2.0, precision=2,
                                       description="The texture repeats every this many metres, whatever the mesh's size. "
                                                   "0 keeps your own UV unwrap")
    for c in CLASSES:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
    for name in ("uncounted_game_dir", "uncounted_mode", "uncounted_map_name", "uncounted_sky", "uncounted_fog", "uncounted_fog_density",
                 "uncounted_ambient", "uncounted_sun", "uncounted_weather", "uncounted_panorama", "uncounted_music", "uncounted_ambience"):
        delattr(bpy.types.Scene, name)
    del bpy.types.Object.uncounted_solid
    del bpy.types.Object.uncounted_ramp
    del bpy.types.Object.uncounted_tile


if __name__ == "__main__":
    register()

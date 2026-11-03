"""
The Uncounted: level editor add-on for Blender (4.0+).

Build and change the game world in Blender, then save it as an edits file the game applies on start.

  Install:  Edit > Preferences > Add-ons > Install... > pick this file > tick "The Uncounted: Level Editor".
  Use:      3D Viewport > press N > "Uncounted" tab. Set "Game folder" (the folder with game.exe), then:
            Import World  ->  edit with normal Blender tools  ->  Export Edits  ->  start the game.

What you can do:
  * Move / turn (around Z) / stretch / copy / delete every wall, floor, roof, prop and tree.
  * Add, copy, delete and edit doors, chests, levers, signs, pickups, NPCs and monsters. Their settings (locked, key,
    sign text, which NPC, which monster...) are the "game_..." fields in the sidebar panel and in Object Properties >
    Custom Properties.
  * Model your own pieces (roofs, door frames, arches, whole buildings) as ordinary Blender meshes in any collection.
    On export each one is saved as a game model (mods/level_edits/models/<name>.glb) with its materials, so you can
    reuse the game's textures by assigning the materials that came in with the imported pieces.
  * The "Uncounted Palette" collection, to the side of the world, has one of every building piece and ready-made
    templates (door, locked door, chest, lever, sign, pickup, NPC, monster). Shift+D one and move it into the world.

Only differences from the game's own level are written, to mods/level_edits/map_edits.json. The game's level files are
never touched, so updates don't overwrite your work; send the file (and the models folder) to the developer to make it
permanent.

Coordinates: the game is Y-up, Blender is Z-up: game (x, y, z) is Blender (x, -z, y). A piece's game position is the
bottom-centre of its model, so imported meshes have their origin there and turn about it, as in the game.
"""

bl_info = {
    "name": "The Uncounted: Level Editor",
    "author": "The Uncounted",
    "version": (2, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar (N) > Uncounted",
    "description": "Import The Uncounted's world, build and edit it, export the edits for the game",
    "category": "Import-Export",
}

import json
import math
import os
import re
import shutil

import bpy
from mathutils import Vector

EDITS_DIR = os.path.join("mods", "level_edits")
EDITS_REL = os.path.join(EDITS_DIR, "map_edits.json")
MODELS_REL = "mods/level_edits/models"
MAP_REL = os.path.join("content", "maps", "edrath_world.json")
COL_WORLD, COL_OBJECTS, COL_PALETTE = "Uncounted World", "Uncounted Objects", "Uncounted Palette"
KINDS = ("npcs", "creatures", "interactables")
PREFIX = {"npcs": "npc:", "creatures": "monster:", "interactables": "obj:"}
ROTKEY = {"npcs": "yaw", "creatures": None, "interactables": "rot_y"}
MARKER_LIFT = 0.4          # markers float a little above the ground so you can see them
EPS = 1e-3

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
]


# ----------------------------------------------------------------------------------------------- helpers
def to_blender(p):
    return Vector((p[0], -p[2], p[1]))


def to_game(v):
    return [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]


def scale_to_blender(s):
    return (s[0], s[2], s[1])


def scale_to_game(s):
    return [round(s[0], 3), round(s[2], 3), round(s[1], 3)]


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def apply_edits(world, edits):
    """The same rules as the game (ContentRegistry::ApplyMapEdits), so Blender shows what the game will show."""
    pe = edits.get("props", {})
    removed = set(pe.get("remove", []))
    props = [p for p in world.get("props", []) if p["id"] not in removed]
    for p in props:
        p.update(pe.get("modify", {}).get(p["id"], {}))
    world["props"] = props + pe.get("add", [])
    for key in KINDS:
        ke = edits.get(key, {})
        gone = set(ke.get("remove", []))
        lst = [e for e in world.get(key, []) if e["instance_id"] not in gone]
        by_id = {e["instance_id"]: i for i, e in enumerate(lst)}
        for d in ke.get("set", []):
            if d["instance_id"] in by_id:
                lst[by_id[d["instance_id"]]] = d
            else:
                lst.append(d)
        for e in lst:
            e.update(ke.get("modify", {}).get(e["instance_id"], {}))
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


def model_mesh(game_dir, model, cache):
    """Import a .glb once and join it into one mesh whose origin is the bottom-centre (the game's anchor)."""
    if model in cache:
        return cache[model]
    path = os.path.join(game_dir, model)
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


# Editable settings: every simple field of a game object becomes a "game_<field>" custom property; lists/objects are
# kept as JSON text ("game_json_<field>"). Types are remembered so a 'locked' switch stays true/false, not 1/0.
SKIP_FIELDS = {"instance_id", "pos", "rot_y", "yaw", "scale", "patrol_a", "patrol_b"}


def set_fields(o, d):
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
            if t == "bool":
                v = bool(v)
            elif t == "int":
                v = int(v)
            elif t == "float":
                v = float(v)
            elif t == "str":
                v = str(v)
            d[k] = v
    return d


def norm(d):
    return json.dumps(d, sort_keys=True)


def make_object(game_dir, cache, kind, d, name):
    """A game object (NPC, monster, door, chest...) as a Blender object: its real model when it has one, else a marker."""
    mesh = model_mesh(game_dir, d.get("model", ""), cache) if kind == "interactables" else None
    o = bpy.data.objects.new(name, mesh)
    if mesh is None:
        o.empty_display_type = {"npcs": "SINGLE_ARROW", "creatures": "SPHERE"}.get(kind, "CUBE")
        o.empty_display_size = 0.4
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
    o["unc_id"] = d.get("instance_id", "")
    pos = d.get("pos", [0, 0, 0])
    if kind == "creatures":       # the patrol route moves with the monster
        o["unc_patrol"] = json.dumps([[a - b for a, b in zip(d.get(k, pos), pos)] for k in ("patrol_a", "patrol_b")])
    set_fields(o, d)
    return o


def object_def(o, kind, instance_id):
    d = get_fields(o)
    d["instance_id"] = instance_id
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


def safe_name(s):
    return re.sub(r"[^a-z0-9_]+", "_", s.lower()).strip("_") or "piece"


# ----------------------------------------------------------------------------------------------- import
class UNC_OT_import_world(bpy.types.Operator):
    bl_idname = "uncounted.import_world"
    bl_label = "Import World"
    bl_description = "Load the game world (with your earlier edits) into this scene"

    def execute(self, context):
        game_dir = bpy.path.abspath(context.scene.uncounted_game_dir)
        map_path = os.path.join(game_dir, MAP_REL)
        if not os.path.exists(map_path):
            self.report({"ERROR"}, f"Can't find {MAP_REL} in {game_dir}. Set the game folder first.")
            return {"CANCELLED"}
        base = read_json(map_path)
        edits_path = os.path.join(game_dir, EDITS_REL)
        world = apply_edits(json.loads(json.dumps(base)), read_json(edits_path)) if os.path.exists(edits_path) else base

        for name in (COL_WORLD, COL_OBJECTS, COL_PALETTE):
            clear_collection(name)
        cw, co, cp = collection(COL_WORLD), collection(COL_OBJECTS), collection(COL_PALETTE)
        cache, skipped = {}, 0
        base_props = {p["id"]: p for p in base.get("props", [])}
        own = {o.get("unc_custom_id") for o in context.scene.objects if o.get("unc_custom_id")}
        for p in world.get("props", []):
            if p["id"] in own:
                continue                               # your own model: its source mesh is already in the scene
            mesh = model_mesh(game_dir, p["model"], cache)
            if mesh is None:
                skipped += 1
                continue
            o = bpy.data.objects.new(p["id"], mesh)
            o.location = to_blender(p["pos"])
            o.rotation_euler = (0.0, 0.0, math.radians(p.get("rot_y", 0.0)))
            o.scale = scale_to_blender(p.get("scale", [1, 1, 1]))
            o["unc_kind"] = "prop"
            o["unc_id"] = p["id"]
            o["unc_model"] = p["model"]
            o["unc_prop"] = json.dumps({k: v for k, v in p.items() if k not in ("pos", "rot_y", "scale", "solid", "uv_scale")})
            o["game_solid"] = bool(p.get("solid", True))
            uv = p.get("uv_scale", [1, 1])
            o["game_uv_x"], o["game_uv_y"] = float(uv[0]), float(uv[1])
            if p["id"] in base_props:
                b = base_props[p["id"]]
                o["unc_base"] = json.dumps({"pos": b["pos"], "rot_y": b.get("rot_y", 0.0), "scale": b.get("scale", [1, 1, 1]),
                                            "solid": b.get("solid", True), "uv_scale": b.get("uv_scale", [1, 1])})
            cw.objects.link(o)
        for kind in KINDS:
            for e in world.get(kind, []):
                co.objects.link(make_object(game_dir, cache, kind, e, PREFIX[kind] + e["instance_id"]))
        # the palette: every building piece in one row, the object templates in the next
        models = sorted({p["model"] for p in world.get("props", [])} |
                        {f"assets/models/{d}/{f}" for d in ("env", "props")
                         for f in sorted(os.listdir(os.path.join(game_dir, "assets", "models", d))) if f.endswith(".glb")})
        x = 0.0
        for model in models:
            mesh = model_mesh(game_dir, model, cache)
            if mesh is None:
                continue
            name = "PALETTE:" + os.path.basename(model)[:-4]
            o = bpy.data.objects.new(name, mesh)
            o.location = Vector((x, 60.0, 0.0))
            o.show_name = True
            o["unc_kind"] = "palette"
            o["unc_id"] = name
            o["unc_model"] = model
            o["unc_prop"] = json.dumps({"model": model})
            o["game_solid"] = True
            o["game_uv_x"], o["game_uv_y"] = 1.0, 1.0
            cp.objects.link(o)
            w = max(v.co.x for v in mesh.vertices) - min(v.co.x for v in mesh.vertices) if mesh.vertices else 1.0
            x += max(2.5, w + 1.5)
        for i, (tname, kind, d) in enumerate(TEMPLATES):
            d = dict(d, instance_id="TEMPLATE:" + tname, pos=[i * 3.0, 0.0, -66.0])
            o = make_object(game_dir, cache, kind, d, "TEMPLATE:" + tname)
            o["unc_template"] = True
            cp.objects.link(o)
        context.scene["unc_base"] = json.dumps({k: {e["instance_id"]: e for e in base.get(k, [])} for k in KINDS})
        context.scene["unc_base_ids"] = json.dumps(sorted(base_props))
        self.report({"INFO"}, f"Imported {len(cw.objects)} pieces, {len(co.objects)} objects, {len(cp.objects)} palette entries"
                              + (f" ({skipped} skipped: model missing)" if skipped else ""))
        return {"FINISHED"}


# ----------------------------------------------------------------------------------------------- export
def export_custom_mesh(o, game_dir, name):
    """Bake a hand-made Blender mesh into a game model: world-space geometry, origin moved to its bottom-centre."""
    mesh = o.data.copy()
    mesh.transform(o.matrix_world)
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
    rel = f"{MODELS_REL}/{name}.glb"
    bpy.ops.export_scene.gltf(filepath=os.path.join(game_dir, rel), export_format="GLB", use_selection=True, export_yup=True,
                              export_apply=True)
    bpy.data.objects.remove(tmp, do_unlink=True)
    bpy.data.meshes.remove(mesh)
    return rel, anchor


class UNC_OT_export_edits(bpy.types.Operator):
    bl_idname = "uncounted.export_edits"
    bl_label = "Export Edits"
    bl_description = "Save your changes (and your own models) to mods/level_edits in the game folder"

    def execute(self, context):
        game_dir = bpy.path.abspath(context.scene.uncounted_game_dir)
        if "unc_base_ids" not in context.scene:
            self.report({"ERROR"}, "Import the world first.")
            return {"CANCELLED"}
        base_ids = set(json.loads(context.scene["unc_base_ids"]))
        base_objs = json.loads(context.scene["unc_base"])
        edits = {"schema": 2, "map": "core:map.edrath", "props": {"modify": {}, "add": [], "remove": []}}
        for k in KINDS:
            edits[k] = {"set": [], "remove": []}
        models_dir = os.path.join(game_dir, MODELS_REL)
        if os.path.isdir(models_dir):
            shutil.rmtree(models_dir)          # rebuilt from the scene every time
        os.makedirs(models_dir, exist_ok=True)

        palette = bpy.data.collections.get(COL_PALETTE)
        in_palette = set(palette.objects) if palette else set()
        objs = [o for o in context.scene.objects if o not in in_palette or o.name != o.get("unc_id")]
        used = {o.name for o in context.scene.objects} | base_ids | {i for k in KINDS for i in base_objs[k]}
        counter = [0]

        def new_id(stem):
            while True:
                counter[0] += 1
                nid = f"edit_{safe_name(stem)}_{counter[0]}"
                if nid not in used:
                    used.add(nid)
                    return nid

        seen_props, seen_objs, tilted, custom = set(), {k: set() for k in KINDS}, 0, 0
        used_custom = set()
        for o in objs:
            kind = o.get("unc_kind")
            if o.type not in ("MESH", "EMPTY") or o.name.startswith("__unc") or (kind is None and o.hide_get()):
                continue
            if abs(o.rotation_euler.x) > EPS or abs(o.rotation_euler.y) > EPS:
                if kind is not None:
                    tilted += 1
            rot = round(math.degrees(o.rotation_euler.z), 2)
            # --- your own models (meshes not from the game, or from an earlier export of your own models)
            model_path = o.get("unc_model", "")
            if o.type == "MESH" and (kind is None or model_path.startswith(MODELS_REL)):
                if not o.data.vertices:
                    continue
                cid = o.get("unc_custom_id") or (safe_name(o.name) if safe_name(o.name).startswith("custom_") else "custom_" + safe_name(o.name))
                if cid in used_custom:
                    cid = new_id(cid)
                used_custom.add(cid)
                rel, anchor = export_custom_mesh(o, game_dir, cid[len("custom_"):] if cid.startswith("custom_") else cid)
                edits["props"]["add"].append({"id": cid, "model": rel, "pos": to_game(anchor), "rot_y": 0.0,
                                              "scale": [1, 1, 1], "solid": bool(o.get("game_solid", True))})
                if kind is None:
                    o["unc_custom_id"] = cid           # your mesh stays the source; re-importing won't add a copy
                custom += 1
                continue
            if kind in ("prop", "palette"):
                pos, sc = to_game(o.location), scale_to_game(o.scale)
                solid = bool(o.get("game_solid", True))
                uv = [round(float(o.get("game_uv_x", 1.0)), 3), round(float(o.get("game_uv_y", 1.0)), 3)]
                if kind == "prop" and o.name == o["unc_id"] and o["unc_id"] in base_ids:
                    seen_props.add(o.name)
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
                        edits["props"]["modify"][o.name] = mod
                else:
                    src = json.loads(o["unc_prop"])
                    keep = kind == "prop" and o.name == o["unc_id"]          # added in an earlier session: keep its id
                    nid = o.name if keep else new_id(os.path.basename(o["unc_model"])[:-4])
                    newp = {"id": nid, "model": o["unc_model"], "pos": pos, "rot_y": rot, "scale": sc, "solid": solid, "uv_scale": uv}
                    for k in ("ramp", "emitter"):
                        if k in src:
                            newp[k] = src[k]
                    edits["props"]["add"].append(newp)
            elif kind in KINDS:
                is_original = o.name == PREFIX[kind] + o["unc_id"] and not o.get("unc_template")
                iid = o["unc_id"] if is_original else new_id(o["unc_id"].replace("TEMPLATE:", "").split(":")[-1])
                d = object_def(o, kind, iid)
                if is_original and iid in base_objs[kind]:
                    seen_objs[kind].add(iid)
                    b = dict(base_objs[kind][iid])
                    if norm(round_def(d, kind)) != norm(round_def(b, kind)):
                        edits[kind]["set"].append(d)
                else:
                    if is_original:
                        seen_objs[kind].add(iid)
                    edits[kind]["set"].append(d)
        edits["props"]["remove"] = sorted(base_ids - seen_props)
        for k in KINDS:
            edits[k]["remove"] = sorted(set(base_objs[k]) - seen_objs[k])
        out = os.path.join(game_dir, EDITS_REL)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(edits, f, indent=2)
        pe = edits["props"]
        objs_set = sum(len(edits[k]["set"]) for k in KINDS)
        objs_rm = sum(len(edits[k]["remove"]) for k in KINDS)
        msg = (f"Saved: {len(pe['modify'])} pieces changed, {len(pe['add'])} added ({custom} your own models), {len(pe['remove'])} removed; "
               f"{objs_set} objects/NPCs/monsters added or changed, {objs_rm} removed")
        if tilted:
            msg += f". Note: {tilted} tilted object(s): the game only turns things around Z"
        self.report({"INFO"}, msg)
        return {"FINISHED"}


def round_def(d, kind):
    """Compare definitions without float noise or missing defaults (facing 0, patrol = spawn point, scale 1)."""
    def r(v):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return round(float(v), 2) + 0.0    # 2 and 2.0 (and -0.0 and 0.0) are the same number
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
        d.setdefault("patrol_a", d.get("pos")); d.setdefault("patrol_b", d.get("pos"))
    if "scale" in d and all(abs(c - 1.0) < EPS for c in d["scale"]):
        del d["scale"]
    return r(d)


# ----------------------------------------------------------------------------------------------- UI
class UNC_PT_panel(bpy.types.Panel):
    bl_label = "The Uncounted"
    bl_idname = "UNC_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Uncounted"

    def draw(self, context):
        col = self.layout.column(align=True)
        col.prop(context.scene, "uncounted_game_dir")
        col.separator()
        col.operator("uncounted.import_world", icon="IMPORT")
        col.operator("uncounted.export_edits", icon="EXPORT")
        o = context.active_object
        if o is not None:
            box = self.layout.box()
            box.label(text=o.name, icon="OBJECT_DATA")
            keys = sorted(k for k in o.keys() if k.startswith("game_"))
            if keys:
                for k in keys:
                    box.prop(o, f'["{k}"]', text=k[5:])
            elif o.get("unc_kind") is None and o.type == "MESH":
                box.label(text="Your own model: exported as a game piece")
        help_ = self.layout.column(align=True)
        help_.label(text="Add: Shift+D a palette piece or template")
        help_.label(text="Turn around Z only (R, Z)")


CLASSES = (UNC_OT_import_world, UNC_OT_export_edits, UNC_PT_panel)


def register():
    bpy.types.Scene.uncounted_game_dir = bpy.props.StringProperty(name="Game folder", subtype="DIR_PATH", default="")
    for c in CLASSES:
        bpy.utils.register_class(c)


def unregister():
    for c in reversed(CLASSES):
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.uncounted_game_dir


if __name__ == "__main__":
    register()

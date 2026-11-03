"""
The Uncounted: level editor add-on for Blender (4.0+).

Edit the game world visually in Blender, then save your changes as a small edits file the game applies on start.

  Install:  Edit > Preferences > Add-ons > Install... > pick this file > tick "The Uncounted: Level Editor".
  Use:      3D Viewport > press N > "Uncounted" tab.
            1. Set "Game folder" (the folder with game.exe).
            2. "Import World": every wall, floor, prop and tree appears as its real model; NPCs, monsters and objects
               appear as labelled markers. Your earlier edits (mods/level_edits/map_edits.json) are already applied.
            3. Edit with normal Blender tools: move (G), rotate (R, around Z only), scale (S), duplicate (Shift+D),
               delete (X). To add something new, duplicate a piece from the "Uncounted Palette" collection (off to the
               side of the world) and move it into place.
            4. "Export Edits": writes mods/level_edits/map_edits.json in the game folder. Start the game to see it.

Coordinates: the game is Y-up, Blender is Z-up: game (x, y, z) is Blender (x, -z, y). A prop's game position
is the bottom-centre of its model, so imported meshes have their origin moved there; rotating an object turns it about
that point, exactly like the game does.

Only changes are written: moved/rotated/scaled props, removed props, new props, and moved markers. The game's own level
files are never touched, so updates to the game don't overwrite your edits (and you can send the edits file to the
developer to make them permanent).
"""

bl_info = {
    "name": "The Uncounted: Level Editor",
    "author": "The Uncounted",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "3D Viewport > Sidebar (N) > Uncounted",
    "description": "Import The Uncounted's world, edit it, export the edits for the game",
    "category": "Import-Export",
}

import json
import math
import os

import bpy
from mathutils import Vector

EDITS_REL = os.path.join("mods", "level_edits", "map_edits.json")
MAP_REL = os.path.join("content", "maps", "edrath_world.json")
COL_WORLD, COL_MARKERS, COL_PALETTE = "Uncounted World", "Uncounted Markers", "Uncounted Palette"
EPS = 1e-3


# ----------------------------------------------------------------------------------------------- coordinates
def to_blender(p):
    """game (x, y, z), Y-up -> Blender (x, -z, y), Z-up"""
    return Vector((p[0], -p[2], p[1]))


def to_game(v):
    return [round(v.x, 3), round(v.z, 3), round(-v.y, 3)]


def scale_to_blender(s):
    return (s[0], s[2], s[1])


def scale_to_game(s):
    return [round(s[0], 3), round(s[2], 3), round(s[1], 3)]


# ----------------------------------------------------------------------------------------------- edits
def apply_edits(world, edits):
    """The same rules as the game (ContentRegistry::ApplyMapEdits), so Blender shows what the game will show."""
    props = world.get("props", [])
    pe = edits.get("props", {})
    removed = set(pe.get("remove", []))
    props = [p for p in props if p["id"] not in removed]
    for p in props:
        mod = pe.get("modify", {}).get(p["id"])
        if mod:
            p.update(mod)
    props += pe.get("add", [])
    world["props"] = props
    for key in ("npcs", "creatures", "interactables"):
        for e in world.get(key, []):
            mod = edits.get(key, {}).get("modify", {}).get(e["instance_id"])
            if mod:
                e.update(mod)
    return world


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


# ----------------------------------------------------------------------------------------------- models
def model_mesh(game_dir, model, cache):
    """Import a .glb once, join it into one mesh with its origin at the bottom-centre (the game's anchor)."""
    if model in cache:
        return cache[model]
    path = os.path.join(game_dir, model)
    mesh = None
    if os.path.exists(path):
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
            obj = bpy.context.view_layer.objects.active
            mesh = obj.data
            xs = [v.co.x for v in mesh.vertices]
            ys = [v.co.y for v in mesh.vertices]
            zs = [v.co.z for v in mesh.vertices]
            anchor = Vector(((min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2, min(zs)))
            for v in mesh.vertices:
                v.co -= anchor
            mesh.name = "UNC:" + model
            for mat in mesh.materials:          # crisp pixel textures, like the game
                if mat and mat.use_nodes:
                    for n in mat.node_tree.nodes:
                        if n.type == "TEX_IMAGE":
                            n.interpolation = "Closest"
        for o in new:
            bpy.data.objects.remove(o, do_unlink=True)
    cache[model] = mesh
    return mesh


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


# ----------------------------------------------------------------------------------------------- operators
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
        base_props = {p["id"]: p for p in base.get("props", [])}
        base_marks = {(k, e["instance_id"]): e for k in ("npcs", "creatures", "interactables") for e in base.get(k, [])}

        for name in (COL_WORLD, COL_MARKERS, COL_PALETTE):
            clear_collection(name)
        cw, cm, cp = collection(COL_WORLD), collection(COL_MARKERS), collection(COL_PALETTE)
        cache, skipped = {}, 0
        for p in world.get("props", []):
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
            o["unc_prop"] = json.dumps({k: v for k, v in p.items() if k not in ("pos", "rot_y", "scale")})
            if p["id"] in base_props:
                b = base_props[p["id"]]
                o["unc_base"] = json.dumps({"pos": b["pos"], "rot_y": b.get("rot_y", 0.0), "scale": b.get("scale", [1, 1, 1]), "model": b["model"]})
            cw.objects.link(o)
        # NPCs, monsters and objects: labelled markers you can move (and turn)
        for kind, rotkey, shape in (("npcs", "yaw", "SINGLE_ARROW"), ("creatures", None, "SPHERE"), ("interactables", "rot_y", "CUBE")):
            for e in world.get(kind, []):
                o = bpy.data.objects.new(f"{kind[:-1]}:{e['instance_id']}", None)
                o.empty_display_type = shape
                o.empty_display_size = 0.4
                o.show_name = True
                o.location = to_blender(e["pos"]) + Vector((0, 0, 0.4))
                o.rotation_euler = (0.0, 0.0, math.radians(e.get(rotkey, 0.0) if rotkey else 0.0))
                o["unc_kind"] = kind
                o["unc_id"] = e["instance_id"]
                o["unc_rotkey"] = rotkey or ""
                b = base_marks.get((kind, e["instance_id"]), e)
                o["unc_base"] = json.dumps({"pos": b["pos"], "rot": b.get(rotkey, 0.0) if rotkey else 0.0})
                cm.objects.link(o)
        # the palette: one of every piece, in a row south of the world
        models = sorted({p["model"] for p in world.get("props", [])} |
                        {os.path.join("assets", "models", d, f).replace(os.sep, "/") for d in ("env", "props")
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
            o["unc_prop"] = json.dumps({"model": model, "solid": True, "uv_scale": [1, 1]})
            cp.objects.link(o)
            dims = mesh.vertices and max(v.co.x for v in mesh.vertices) - min(v.co.x for v in mesh.vertices)
            x += max(2.5, (dims or 1.0) + 1.5)
        context.scene["unc_base_ids"] = json.dumps(sorted(base_props))
        self.report({"INFO"}, f"Imported {len(cw.objects)} props, {len(cm.objects)} markers, {len(cp.objects)} palette pieces"
                              + (f" ({skipped} props skipped: model missing)" if skipped else ""))
        return {"FINISHED"}


class UNC_OT_export_edits(bpy.types.Operator):
    bl_idname = "uncounted.export_edits"
    bl_label = "Export Edits"
    bl_description = "Save your changes to mods/level_edits/map_edits.json in the game folder"

    def execute(self, context):
        game_dir = bpy.path.abspath(context.scene.uncounted_game_dir)
        if "unc_base_ids" not in context.scene:
            self.report({"ERROR"}, "Import the world first.")
            return {"CANCELLED"}
        base_ids = set(json.loads(context.scene["unc_base_ids"]))
        edits = {"schema": 1, "map": "core:map.edrath", "props": {"modify": {}, "add": [], "remove": []},
                 "npcs": {"modify": {}}, "creatures": {"modify": {}}, "interactables": {"modify": {}}}
        seen, used_ids, tilted = set(), set(), 0
        objs = [o for o in context.scene.objects if "unc_kind" in o]
        for o in objs:
            used_ids.add(o.name)
        n_new = 0
        for o in objs:
            kind = o["unc_kind"]
            if abs(o.rotation_euler.x) > EPS or abs(o.rotation_euler.y) > EPS:
                tilted += 1                       # the game only turns things about the vertical axis
            pos = to_game(o.location)
            rot = round(math.degrees(o.rotation_euler.z), 2)
            if kind in ("prop", "palette"):
                original = kind == "prop" and o.name == o["unc_id"] and o["unc_id"] in base_ids
                if original:
                    seen.add(o.name)
                    b = json.loads(o["unc_base"])
                    mod = {}
                    if any(abs(a - c) > EPS for a, c in zip(pos, b["pos"])):
                        mod["pos"] = pos
                    if abs(((rot - b["rot_y"]) + 180) % 360 - 180) > 0.05:
                        mod["rot_y"] = rot
                    sc = scale_to_game(o.scale)
                    if any(abs(a - c) > EPS for a, c in zip(sc, b["scale"])):
                        mod["scale"] = sc
                    if mod:
                        edits["props"]["modify"][o.name] = mod
                elif kind == "prop" or o.name != o["unc_id"]:   # a duplicate, or a copy of a palette piece
                    if kind == "palette" and o.users_collection and o.users_collection[0].name == COL_PALETTE and o.name == o["unc_id"]:
                        continue
                    src = json.loads(o["unc_prop"])
                    base = os.path.basename(o["unc_model"])[:-4]
                    keep = kind == "prop" and o.name == o["unc_id"]      # added in an earlier session: keep its id
                    while not keep:
                        n_new += 1
                        nid = f"edit_{base}_{n_new}"
                        if nid not in used_ids and nid not in base_ids:
                            break
                    if keep:
                        nid = o.name
                    used_ids.add(nid)
                    newp = {"id": nid, "model": o["unc_model"], "pos": pos, "rot_y": rot, "scale": scale_to_game(o.scale),
                            "solid": src.get("solid", True)}
                    for k in ("uv_scale", "ramp", "emitter"):
                        if k in src:
                            newp[k] = src[k]
                    edits["props"]["add"].append(newp)
            else:
                b = json.loads(o["unc_base"])
                gp = to_game(o.location - Vector((0, 0, 0.4)))
                mod = {}
                if any(abs(a - c) > EPS for a, c in zip(gp, b["pos"])):
                    mod["pos"] = gp
                if o["unc_rotkey"] and abs(((rot - b["rot"]) + 180) % 360 - 180) > 0.05:
                    mod[o["unc_rotkey"]] = rot
                if mod:
                    edits[kind]["modify"][o["unc_id"]] = mod
        edits["props"]["remove"] = sorted(base_ids - seen)
        out = os.path.join(game_dir, EDITS_REL)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as f:
            json.dump(edits, f, indent=2)
        pe = edits["props"]
        moved = sum(len(edits[k]["modify"]) for k in ("npcs", "creatures", "interactables"))
        msg = (f"Saved {EDITS_REL}: {len(pe['modify'])} changed, {len(pe['add'])} added, {len(pe['remove'])} removed props, "
               f"{moved} moved markers")
        if tilted:
            msg += f". Note: {tilted} object(s) are tilted; the game only uses rotation around Z"
        self.report({"INFO"}, msg)
        return {"FINISHED"}


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
        col.separator()
        col.label(text="Add pieces: Shift+D a palette piece")
        col.label(text="Rotate around Z only (R, Z)")


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

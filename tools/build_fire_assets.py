"""
Fire for fireplaces, forges, campfires and cauldrons.

  python3 tools/build_fire_assets.py            -> assets/sprites/vfx/fire_flames.png (8 frames, 64 px), assets/textures/embers.png
  blender -b -P tools/build_fire_assets.py      -> assets/models/props/fire_embers.glb, assets/models/props/campfire.glb

The flames and their light come from content/props/prop_presets.json, so any piece using these models burns, wherever
it's placed (including from the Blender level editor's palette).
"""
import math
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIRE = [(255, 250, 215), (255, 222, 110), (255, 170, 50), (236, 108, 30), (186, 58, 22), (110, 28, 16)]


def build_images():
    from PIL import Image
    frames, size = 8, 64
    sheet = Image.new("RGBA", (frames * size, size), (0, 0, 0, 0))
    rnd = random.Random(7)
    tongues = [(rnd.uniform(0.18, 0.82), rnd.uniform(0.45, 0.95), rnd.uniform(0.10, 0.17), rnd.uniform(0, 6.3)) for _ in range(7)]
    px = 2                                                      # chunky pixels, like the torch flame
    for f in range(frames):
        t = f / frames * 2 * math.pi
        img = Image.new("RGBA", (size // px, size // px), (0, 0, 0, 0))
        w = h = size // px
        for y in range(h):
            for x in range(w):
                u, v = (x + 0.5) / w, 1.0 - (y + 0.5) / h      # v: 0 at the bottom
                heat = 0.0
                for cx, height, width, ph in tongues:
                    sway = 0.06 * math.sin(t + ph + v * 5.0) * v
                    hh = height * (0.85 + 0.15 * math.sin(t * 2 + ph))
                    if v > hh:
                        continue
                    wid = width * (1.0 - (v / hh) ** 1.6) + 0.01
                    d = abs(u - cx - sway) / wid
                    heat = max(heat, (1.0 - d) * (1.0 - 0.55 * v / hh))
                base = max(0.0, 1.0 - abs(u - 0.5) / 0.42) * max(0.0, 1.0 - v / 0.22)   # a hot bed along the bottom
                heat = max(heat, base)
                heat += rnd.uniform(-0.06, 0.06)
                if heat <= 0.12:
                    continue
                i = min(len(FIRE) - 1, int((1.0 - min(heat, 1.0)) * len(FIRE)))
                r, g, b = FIRE[i]
                img.putpixel((x, y), (r, g, b, 255 if heat > 0.2 else 170))
        sheet.paste(img.resize((size, size), Image.NEAREST), (f * size, 0))
    out = os.path.join(ROOT, "assets", "sprites", "vfx", "fire_flames.png")
    if os.path.exists(out) and "--placeholder" not in sys.argv:
        print("Kept", out, "(Noor's flames; pass --placeholder to overwrite with the generated one)")
    else:
        sheet.save(out)
        print("Wrote", out)

    tex = Image.new("RGB", (64, 64))
    rnd = random.Random(3)
    for y in range(64):
        for x in range(64):
            n = (math.sin(x * 0.7 + math.sin(y * 0.4) * 2) + math.sin(y * 0.9 + math.sin(x * 0.3) * 2)) * 0.25 + rnd.uniform(-0.15, 0.15)
            if n > 0.32:
                c = (255, 196, 80) if n > 0.45 else (238, 112, 34)        # glowing cracks
            elif n > 0.15:
                c = (120, 38, 18)
            else:
                k = rnd.randint(18, 40)
                c = (k + 8, k, k - 4)                                        # charcoal
            tex.putpixel((x, y), c)
    tex = tex.resize((32, 32), Image.NEAREST).resize((64, 64), Image.NEAREST)
    out = os.path.join(ROOT, "assets", "textures", "embers.png")
    tex.save(out)
    print("Wrote", out)
    magic = Image.new("RGB", tex.size)                            # the same coals, burning teal (for magic fire)
    for y in range(tex.height):
        for x in range(tex.width):
            r, g, b = tex.getpixel((x, y))
            magic.putpixel((x, y), (int(b * 0.4), int(r * 0.9), int(r * 0.85)) if r > 90 else (r - 6, g, b + 6))
    out = os.path.join(ROOT, "assets", "textures", "embers_magic.png")
    magic.save(out)
    print("Wrote", out)


def build_models():
    import bpy
    import bmesh

    def material(name, tex):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes["Principled BSDF"]
        img = nt.nodes.new("ShaderNodeTexImage")
        img.image = bpy.data.images.load(os.path.join(ROOT, "assets", "textures", tex))
        img.interpolation = "Closest"
        nt.links.new(img.outputs["Color"], bsdf.inputs["Base Color"])
        bsdf.inputs["Roughness"].default_value = 0.95
        return m

    def mesh_obj(name, bm, mat):
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        me.materials.append(mat)
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        return o

    def box_uv(o, scale=1.0):
        bm = bmesh.new()
        bm.from_mesh(o.data)
        uv = bm.loops.layers.uv.verify()
        for f in bm.faces:
            ax = max(range(3), key=lambda i: abs(f.normal[i]))
            for l in f.loops:
                c = l.vert.co
                l[uv].uv = ((c.y, c.z) if ax == 0 else (c.x, c.z) if ax == 1 else (c.x, c.y))
                l[uv].uv = (l[uv].uv[0] * scale, l[uv].uv[1] * scale)
        bm.to_mesh(o.data)
        bm.free()

    def ember_bed(radius, height, seed):
        rnd = random.Random(seed)
        bm = bmesh.new()
        n = 14
        rim = [bm.verts.new((radius * (0.8 + 0.2 * rnd.random()) * math.cos(a), radius * (0.8 + 0.2 * rnd.random()) * math.sin(a), 0.0))
               for a in [i / n * 2 * math.pi for i in range(n)]]
        top = [bm.verts.new((v.co.x * 0.7, v.co.y * 0.7, height * (0.7 + 0.3 * rnd.random()))) for v in rim]
        centre = bm.verts.new((0, 0, height * 1.15))
        bot = bm.verts.new((0, 0, 0))
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new([rim[i], rim[j], top[j], top[i]])
            bm.faces.new([top[i], top[j], centre])
            bm.faces.new([rim[j], rim[i], bot])
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        return bm

    def export(rel):
        bpy.ops.object.select_all(action="SELECT")
        objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
        bpy.context.view_layer.objects.active = objs[0]
        if len(objs) > 1:
            bpy.ops.object.join()
        bpy.ops.export_scene.gltf(filepath=os.path.join(ROOT, rel), export_format="GLB", export_apply=True, export_yup=True)
        print("Exported", rel)

    # 1. fire_embers.glb: just the fire's bed of glowing coals, 0.7 m across (fireplaces, forges, under a cauldron).
    #    Scale it in the editor: the flames and light grow with it.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    embers = material("MatEmbers", "embers.png")
    o = mesh_obj("Embers", ember_bed(0.35, 0.08, 1), embers)
    box_uv(o, 2.5)
    export("assets/models/props/fire_embers.glb")

    # 1b. fire_embers_small.glb: a smaller, calmer bed (0.5 m) for under a cooking pot.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    o = mesh_obj("Embers", ember_bed(0.25, 0.06, 3), material("MatEmbers", "embers.png"))
    box_uv(o, 2.5)
    export("assets/models/props/fire_embers_small.glb")

    # 1c. fire_embers_magic.glb: teal coals for magic fire (shrines, wizards, haunted places).
    bpy.ops.wm.read_factory_settings(use_empty=True)
    o = mesh_obj("Embers", ember_bed(0.35, 0.08, 4), material("MatEmbersMagic", "embers_magic.png"))
    box_uv(o, 2.5)
    export("assets/models/props/fire_embers_magic.glb")

    # 2. campfire.glb: a ring of stones, crossed logs and embers, 1.2 m across.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    embers, stone, wood = material("MatEmbers", "embers.png"), material("MatStone", "stone_wall.png"), material("MatWood", "wood_planks.png")
    o = mesh_obj("Embers", ember_bed(0.34, 0.07, 2), embers)
    box_uv(o, 2.5)
    rnd = random.Random(5)
    for i in range(9):
        a = i / 9 * 2 * math.pi + rnd.uniform(-0.1, 0.1)
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=1, radius=0.11)
        for v in bm.verts:
            v.co.x *= rnd.uniform(1.0, 1.5)
            v.co.z *= 0.7
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(a, 3, "Z"))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0.5 * math.cos(a), 0.5 * math.sin(a), 0.07))
        s = mesh_obj(f"Stone{i}", bm, stone)
        box_uv(s, 2.0)
    for i, a in enumerate((0.3, 1.9, 3.6)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.05, depth=0.62, location=(0.12 * math.cos(a), 0.12 * math.sin(a), 0.16),
                                            rotation=(math.radians(62), 0, a + math.pi / 2))
        log = bpy.context.active_object
        log.data.materials.append(wood)
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
        box_uv(log, 2.0)
    export("assets/models/props/campfire.glb")


if __name__ == "__main__":
    if "bpy" in sys.modules or any(a.endswith(".py") and "blender" in sys.argv[0] for a in sys.argv):
        build_models()
    else:
        build_images()

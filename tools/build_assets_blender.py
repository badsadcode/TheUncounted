"""
Offline Blender Headless GLB Asset Builder for THE UNCOUNTED.
Run with:
  blender -b -P tools/build_assets_blender.py
Exports clean, UV-mapped, textured .glb files to assets/models/ and mods/example_mod/.
"""

import os
import math
import bpy
import bmesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEX_DIR = os.path.join(ROOT, "assets", "textures")


def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def make_material(name, tex_filename, tint=(1.0, 1.0, 1.0, 1.0)):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type="ShaderNodeOutputMaterial")
    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.inputs["Roughness"].default_value = 0.9
    if "Specular IOR Level" in bsdf.inputs:
        bsdf.inputs["Specular IOR Level"].default_value = 0.1
    elif "Specular" in bsdf.inputs:
        bsdf.inputs["Specular"].default_value = 0.1

    tex_path = os.path.join(TEX_DIR, tex_filename)
    if os.path.exists(tex_path):
        tex_node = nodes.new(type="ShaderNodeTexImage")
        img = bpy.data.images.load(tex_path, check_existing=True)
        tex_node.image = img
        tex_node.interpolation = "Closest"
        links.new(tex_node.outputs["Color"], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = tint

    links.new(bsdf.outputs["BSDF"], out_node.inputs["Surface"])
    return mat


def add_box(name, size_xyz, center_xyz, mat, uv_scale=1.0):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=center_xyz)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size_xyz
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # Smart UV project or cube project
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    for face in bm.faces:
        n = face.normal
        for loop in face.loops:
            co = loop.vert.co
            if abs(n.z) > 0.7:
                u, v = co.x * uv_scale, co.y * uv_scale
            elif abs(n.x) > 0.7:
                u, v = co.y * uv_scale, co.z * uv_scale
            else:
                u, v = co.x * uv_scale, co.z * uv_scale
            loop[uv_layer].uv = (u * 0.5 + 0.5, v * 0.5 + 0.5)
    bm.to_mesh(obj.data)
    bm.free()

    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def add_cylinder(name, radius, depth, center_xyz, vertices, mat, rot_euler=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=vertices, radius=radius, depth=depth, location=center_xyz, rotation=rot_euler
    )
    obj = bpy.context.active_object
    obj.name = name
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def add_cone(name, r1, r2, depth, center_xyz, vertices, mat):
    bpy.ops.mesh.primitive_cone_add(
        vertices=vertices, radius1=r1, radius2=r2, depth=depth, location=center_xyz
    )
    obj = bpy.context.active_object
    obj.name = name
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return obj


def export_glb(rel_path):
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    # Join all mesh objects into a single clean mesh where appropriate so materials/transforms export cleanly
    bpy.ops.object.select_all(action="SELECT")
    objs = [o for o in bpy.context.selected_objects if o.type == "MESH"]
    if len(objs) > 1:
        bpy.context.view_layer.objects.active = objs[0]
        bpy.ops.object.join()
    if objs:
        obj = bpy.context.active_object
        obj.location = (0.0, 0.0, 0.0)

    bpy.ops.export_scene.gltf(
        filepath=full_path,
        export_format="GLB",
        export_apply=True,
        export_texcoords=True,
        export_normals=True,
        export_materials="EXPORT",
        export_yup=True
    )
    print(f"Exported: {rel_path}")


def build_env_models():
    # 1. wall_stone.glb (1x1x1 unit cube centered at origin so scale in map JSON sets exact dimensions)
    clear_scene()
    mat = make_material("MatStoneWall", "stone_wall.png")
    add_box("WallStone", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/wall_stone.glb")

    # 2. wall_crypt.glb
    clear_scene()
    mat = make_material("MatCryptBrick", "crypt_brick.png")
    add_box("WallCrypt", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/wall_crypt.glb")

    # 3. wall_timber.glb
    clear_scene()
    mat = make_material("MatTimber", "timber_plaster.png")
    add_box("WallTimber", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/wall_timber.glb")

    # 4. floor_cobble.glb
    clear_scene()
    mat = make_material("MatCobble", "mossy_cobble.png")
    add_box("FloorCobble", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/floor_cobble.glb")

    # 5. floor_grass.glb
    clear_scene()
    mat = make_material("MatGrass", "forest_grass.png")
    add_box("FloorGrass", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/floor_grass.glb")

    # 6. floor_wood.glb
    clear_scene()
    mat = make_material("MatWood", "wood_planks.png")
    add_box("FloorWood", (1.0, 1.0, 1.0), (0, 0, 0.5), mat, uv_scale=1.0)
    export_glb("assets/models/env/floor_wood.glb")

    # 7. roof_gable.glb
    clear_scene()
    mat = make_material("MatRoof", "roof_shingles.png")
    add_cone("RoofGable", 0.75, 0.05, 1.0, (0, 0, 0.5), 4, mat)
    export_glb("assets/models/env/roof_gable.glb")

    # 8. pillar_stone.glb
    clear_scene()
    mat = make_material("MatPillar", "stone_wall.png")
    add_box("Base", (0.9, 0.9, 0.35), (0, 0, 0.175), mat)
    add_cylinder("Shaft", 0.34, 3.3, (0, 0, 1.85), 8, mat)
    add_box("Capital", (0.95, 0.95, 0.35), (0, 0, 3.825), mat)
    export_glb("assets/models/env/pillar_stone.glb")

    # 9. archway_stone.glb
    clear_scene()
    mat = make_material("MatArch", "crypt_brick.png")
    add_box("LeftPier", (0.7, 0.6, 3.6), (-1.45, 0, 1.8), mat)
    add_box("RightPier", (0.7, 0.6, 3.6), (1.45, 0, 1.8), mat)
    add_box("Lintel", (3.6, 0.65, 0.7), (0, 0, 3.65), mat)
    export_glb("assets/models/env/archway_stone.glb")

    # 10. stairs_stone.glb (6 steps rising 2.0m over 4.0m depth, 3.0m width)
    clear_scene()
    mat = make_material("MatStairs", "mossy_cobble.png")
    steps = 8
    for i in range(steps):
        h = (i + 1) * (2.0 / steps)
        y = -1.75 + i * (4.0 / steps)
        add_box(f"Step_{i}", (3.0, 4.0 / steps, h), (0, y, h * 0.5), mat)
    export_glb("assets/models/env/stairs_stone.glb")

    # 11. tree_pine.glb
    clear_scene()
    mat_wood = make_material("MatTrunk", "wood_planks.png")
    mat_leaf = make_material("MatPine", "foliage_pine.png")
    add_cylinder("Trunk", 0.28, 2.2, (0, 0, 1.1), 7, mat_wood)
    add_cone("Tier1", 1.65, 0.2, 2.2, (0, 0, 2.4), 7, mat_leaf)
    add_cone("Tier2", 1.30, 0.15, 2.0, (0, 0, 3.6), 7, mat_leaf)
    add_cone("Tier3", 0.90, 0.05, 1.8, (0, 0, 4.7), 7, mat_leaf)
    export_glb("assets/models/env/tree_pine.glb")

    # 12. ruin_monolith.glb
    clear_scene()
    mat_stone = make_material("MatMonoStone", "crypt_brick.png")
    mat_rune = make_material("MatMonoRune", "rune_crystal.png")
    add_box("Pedestal", (1.4, 1.4, 0.5), (0, 0, 0.25), mat_stone)
    add_cone("Obelisk", 0.55, 0.25, 3.2, (0, 0, 2.1), 4, mat_rune)
    add_cone("Cap", 0.25, 0.01, 0.5, (0, 0, 3.95), 4, mat_stone)
    export_glb("assets/models/env/ruin_monolith.glb")


def build_prop_models():
    mat_wood = lambda: make_material("MatWood", "wood_planks.png")
    mat_iron = lambda: make_material("MatIron", "iron_metal.png")
    mat_gold = lambda: make_material("MatGold", "gold_trim.png")
    mat_stone = lambda: make_material("MatStone", "stone_wall.png")
    mat_rune = lambda: make_material("MatRune", "rune_crystal.png")
    mat_paper = lambda: make_material("MatPaper", "parchment_tex.png")

    # 1. oak_door.glb
    clear_scene()
    mw, mi, mg = mat_wood(), mat_iron(), mat_gold()
    add_box("DoorSlab", (1.8, 0.18, 2.8), (0, 0, 1.4), mw)
    add_box("BandTop", (1.84, 0.22, 0.12), (0, 0, 2.3), mi)
    add_box("BandBot", (1.84, 0.22, 0.12), (0, 0, 0.5), mi)
    add_box("Handle", (0.14, 0.30, 0.14), (0.65, 0, 1.3), mg)
    export_glb("assets/models/props/oak_door.glb")

    # 2. iron_gate.glb
    clear_scene()
    mi = mat_iron()
    add_box("TopBar", (2.2, 0.16, 0.16), (0, 0, 2.8), mi)
    add_box("MidBar", (2.2, 0.16, 0.14), (0, 0, 1.5), mi)
    for x in (-0.9, -0.54, -0.18, 0.18, 0.54, 0.9):
        add_cylinder(f"Bar_{x}", 0.05, 2.9, (x, 0, 1.45), 6, mi)
    export_glb("assets/models/props/iron_gate.glb")

    # 3. treasure_chest.glb
    clear_scene()
    mw, mi, mg = mat_wood(), mat_iron(), mat_gold()
    add_box("ChestBox", (1.1, 0.7, 0.55), (0, 0, 0.275), mw)
    add_cylinder("ChestLid", 0.35, 1.1, (0, 0, 0.55), 8, mw, rot_euler=(0, math.pi / 2, 0))
    add_box("StrapL", (0.12, 0.74, 0.72), (-0.38, 0, 0.36), mi)
    add_box("StrapR", (0.12, 0.74, 0.72), (0.38, 0, 0.36), mi)
    add_box("LockPlate", (0.18, 0.76, 0.22), (0, 0, 0.52), mg)
    export_glb("assets/models/props/treasure_chest.glb")

    # 4. iron_lever.glb
    clear_scene()
    ms, mi, mg = mat_stone(), mat_iron(), mat_gold()
    add_box("LeverBase", (0.5, 0.35, 0.25), (0, 0, 0.125), ms)
    add_cylinder("LeverArm", 0.04, 0.85, (0, 0, 0.55), 6, mi, rot_euler=(0.35, 0, 0))
    add_box("LeverGrip", (0.16, 0.14, 0.14), (0, -0.15, 0.92), mg)
    export_glb("assets/models/props/iron_lever.glb")

    # 5. pressure_plate.glb
    clear_scene()
    ms, mr = mat_stone(), mat_rune()
    add_box("PlateRim", (1.3, 1.3, 0.08), (0, 0, 0.04), ms)
    add_box("PlateCenter", (1.0, 1.0, 0.13), (0, 0, 0.065), mr)
    export_glb("assets/models/props/pressure_plate.glb")

    # 6. lectern_ledger.glb
    clear_scene()
    mw, mp, mg = mat_wood(), mat_paper(), mat_gold()
    add_box("Foot", (0.65, 0.65, 0.15), (0, 0, 0.075), mw)
    add_cylinder("Post", 0.12, 1.05, (0, 0, 0.6), 8, mw)
    add_box("Desk", (0.75, 0.55, 0.10), (0, 0, 1.18), mw)
    add_box("LedgerPageL", (0.30, 0.42, 0.06), (-0.16, 0, 1.25), mp)
    add_box("LedgerPageR", (0.30, 0.42, 0.06), (0.16, 0, 1.25), mp)
    add_box("Spine", (0.06, 0.44, 0.07), (0, 0, 1.25), mg)
    export_glb("assets/models/props/lectern_ledger.glb")

    # 7. registry_desk.glb
    clear_scene()
    mw, mp = mat_wood(), mat_paper()
    add_box("DeskTop", (2.2, 1.0, 0.12), (0, 0, 0.95), mw)
    add_box("PanelFront", (2.0, 0.12, 0.90), (0, 0.42, 0.45), mw)
    add_box("LegL", (0.18, 0.90, 0.90), (-0.95, 0, 0.45), mw)
    add_box("LegR", (0.18, 0.90, 0.90), (0.95, 0, 0.45), mw)
    add_box("Stack1", (0.35, 0.28, 0.18), (-0.55, 0.1, 1.08), mp)
    add_box("Stack2", (0.32, 0.25, 0.12), (0.48, -0.1, 1.05), mp)
    export_glb("assets/models/props/registry_desk.glb")

    # 8. bookshelf_prop.glb
    clear_scene()
    mb = make_material("MatBookshelf", "bookshelf_tex.png")
    add_box("Bookcase", (1.8, 0.55, 2.6), (0, 0, 1.3), mb)
    export_glb("assets/models/props/bookshelf_prop.glb")

    # 9. wall_torch.glb
    clear_scene()
    mi, mw, mg = mat_iron(), mat_wood(), mat_gold()
    add_box("Bracket", (0.16, 0.22, 0.25), (0, 0, 1.4), mi)
    add_cylinder("TorchStick", 0.05, 0.65, (0, 0.12, 1.65), 6, mw)
    add_box("EmberHead", (0.16, 0.16, 0.18), (0, 0.12, 2.0), mg)
    export_glb("assets/models/props/wall_torch.glb")

    # 10. sarcophagus.glb
    clear_scene()
    ms, mr = mat_stone(), mat_rune()
    add_box("TombBox", (1.2, 2.3, 0.75), (0, 0, 0.375), ms)
    add_box("TombLid", (1.28, 2.38, 0.20), (0, 0, 0.85), ms)
    add_box("RuneInlay", (0.5, 1.6, 0.06), (0, 0, 0.96), mr)
    export_glb("assets/models/props/sarcophagus.glb")

    # 11. wooden_crate.glb
    clear_scene()
    mw = mat_wood()
    add_box("Crate", (0.9, 0.9, 0.9), (0, 0, 0.45), mw)
    export_glb("assets/models/props/wooden_crate.glb")

    # 12. signpost.glb
    clear_scene()
    mw = mat_wood()
    add_cylinder("Post", 0.09, 2.1, (0, 0, 1.05), 6, mw)
    add_box("Plank1", (0.95, 0.08, 0.24), (0.35, 0, 1.75), mw)
    add_box("Plank2", (0.85, 0.08, 0.22), (-0.30, 0, 1.45), mw)
    export_glb("assets/models/props/signpost.glb")

    # 13. altar_dawn.glb
    clear_scene()
    ms, mg = mat_stone(), mat_gold()
    add_box("AltarBase", (1.8, 1.0, 1.0), (0, 0, 0.5), ms)
    add_cylinder("SunDisc", 0.42, 0.12, (0, 0, 1.48), 12, mg, rot_euler=(math.pi / 2, 0, 0))
    export_glb("assets/models/props/altar_dawn.glb")


def build_item_and_character_models():
    mat_iron = lambda: make_material("MatIron", "iron_metal.png")
    mat_wood = lambda: make_material("MatWood", "wood_planks.png")
    mat_gold = lambda: make_material("MatGold", "gold_trim.png")
    mat_rune = lambda: make_material("MatRune", "rune_crystal.png")
    mat_paper = lambda: make_material("MatPaper", "parchment_tex.png")
    mat_crypt = lambda: make_material("MatCrypt", "crypt_brick.png")

    def build_sword(path, blade_len, blade_w, blade_mat_fn, guard_mat_fn):
        clear_scene()
        mw = mat_wood()
        blade_mat = blade_mat_fn()
        guard_mat = guard_mat_fn()
        add_box("Grip", (0.05, 0.05, 0.22), (0, 0, 0.11), mw)
        add_box("Pommel", (0.08, 0.08, 0.06), (0, 0, 0.02), guard_mat)
        add_box("Crossguard", (0.28, 0.06, 0.05), (0, 0, 0.23), guard_mat)
        add_box("Blade", (blade_w, 0.025, blade_len), (0, 0, 0.25 + blade_len * 0.5), blade_mat)
        export_glb(path)

    build_sword("assets/models/items/rusted_sword.glb", 0.68, 0.07, mat_iron, mat_wood)
    build_sword("assets/models/items/iron_longsword.glb", 0.82, 0.075, mat_iron, mat_gold)
    build_sword("assets/models/items/widowmaker_blade.glb", 0.98, 0.10, mat_rune, mat_gold)
    build_sword("assets/models/items/steel_dagger.glb", 0.40, 0.055, mat_iron, mat_iron)
    build_sword("mods/example_mod/assets/models/items/ashbrand_blade.glb", 0.88, 0.09, mat_gold, mat_iron)

    # iron_mace.glb
    clear_scene()
    mw, mi = mat_wood(), mat_iron()
    add_cylinder("Haft", 0.03, 0.65, (0, 0, 0.325), 6, mw)
    add_box("MaceHead", (0.18, 0.18, 0.20), (0, 0, 0.68), mi)
    export_glb("assets/models/items/iron_mace.glb")

    # oak_staff.glb
    clear_scene()
    mw, mr = mat_wood(), mat_rune()
    add_cylinder("Shaft", 0.035, 1.35, (0, 0, 0.675), 6, mw)
    add_box("Crystal", (0.15, 0.15, 0.20), (0, 0, 1.42), mr)
    export_glb("assets/models/items/oak_staff.glb")

    # hunting_bow.glb
    clear_scene()
    mw, mp = mat_wood(), mat_paper()
    add_box("BowCenter", (0.05, 0.05, 0.35), (0, 0, 0.45), mw)
    add_box("LimbTop", (0.04, 0.12, 0.32), (0, -0.05, 0.74), mw)
    add_box("LimbBot", (0.04, 0.12, 0.32), (0, -0.05, 0.16), mw)
    add_cylinder("BowString", 0.008, 0.84, (0, -0.10, 0.45), 4, mp)
    export_glb("assets/models/items/hunting_bow.glb")

    # wooden_arrow.glb
    clear_scene()
    mw, mi = mat_wood(), mat_iron()
    add_cylinder("Shaft", 0.015, 0.65, (0, 0, 0.325), 5, mw)
    add_cone("Tip", 0.035, 0.002, 0.10, (0, 0, 0.68), 4, mi)
    export_glb("assets/models/items/wooden_arrow.glb")

    # iron_shield.glb
    clear_scene()
    mi, mg = mat_iron(), mat_gold()
    add_box("ShieldPlate", (0.55, 0.06, 0.68), (0, 0, 0.38), mi)
    add_box("ShieldBoss", (0.16, 0.10, 0.16), (0, 0, 0.38), mg)
    export_glb("assets/models/items/iron_shield.glb")

    # potion_flask.glb
    clear_scene()
    mr, mw = mat_rune(), mat_wood()
    add_cylinder("FlaskBody", 0.12, 0.24, (0, 0, 0.12), 8, mr)
    add_cylinder("Cork", 0.05, 0.10, (0, 0, 0.27), 6, mw)
    export_glb("assets/models/items/potion_flask.glb")

    # annex_key.glb
    clear_scene()
    mg = mat_gold()
    add_box("KeyBow", (0.14, 0.03, 0.14), (0, 0, 0.07), mg)
    add_box("KeyStem", (0.04, 0.03, 0.24), (0, 0, 0.24), mg)
    add_box("KeyBit", (0.10, 0.03, 0.08), (0.05, 0, 0.31), mg)
    export_glb("assets/models/items/annex_key.glb")

    # form_27b_scroll.glb
    clear_scene()
    mp, mg = mat_paper(), mat_gold()
    add_cylinder("ScrollRoll", 0.07, 0.42, (0, 0, 0.07), 8, mp, rot_euler=(0, math.pi / 2, 0))
    add_box("SealBand", (0.08, 0.16, 0.16), (0, 0, 0.07), mg)
    export_glb("assets/models/items/form_27b_scroll.glb")

    # spell_tome.glb
    clear_scene()
    mb = make_material("MatTome", "bookshelf_tex.png")
    mg = mat_gold()
    add_box("Cover", (0.34, 0.44, 0.10), (0, 0, 0.05), mb)
    add_box("Clasp", (0.36, 0.12, 0.11), (0, 0, 0.05), mg)
    export_glb("assets/models/items/spell_tome.glb")

    # 3D Character Entity: lost_sentinel.glb (Ancient Great Silence Construct Knight)
    clear_scene()
    mc, mr, mg, mi = mat_crypt(), mat_rune(), mat_gold(), mat_iron()
    add_box("LegL", (0.24, 0.26, 0.85), (-0.20, 0, 0.425), mc)
    add_box("LegR", (0.24, 0.26, 0.85), (0.20, 0, 0.425), mc)
    add_box("Torso", (0.68, 0.40, 0.82), (0, 0, 1.25), mc)
    add_box("RuneCore", (0.28, 0.44, 0.32), (0, 0, 1.30), mr)
    add_box("PauldronL", (0.28, 0.44, 0.28), (-0.48, 0, 1.52), mg)
    add_box("PauldronR", (0.28, 0.44, 0.28), (0.48, 0, 1.52), mg)
    add_box("ArmL", (0.20, 0.22, 0.68), (-0.48, 0, 1.12), mc)
    add_box("ArmR", (0.20, 0.22, 0.68), (0.48, 0, 1.12), mc)
    add_box("Shield", (0.10, 0.56, 0.76), (-0.62, 0.12, 1.12), mg)
    add_box("HalberdShaft", (0.07, 0.07, 1.95), (0.55, 0.22, 1.10), mi)
    add_box("HalberdBlade", (0.04, 0.34, 0.48), (0.55, 0.28, 1.92), mr)
    add_box("Helm", (0.36, 0.36, 0.40), (0, 0, 1.88), mc)
    add_box("VisorGlow", (0.26, 0.38, 0.08), (0, 0, 1.90), mr)
    export_glb("assets/models/characters/lost_sentinel.glb")

    # diag_missing.glb
    clear_scene()
    md = make_material("MatDiag", "diag_missing.png")
    add_box("DiagCube", (0.8, 0.8, 0.8), (0, 0, 0.4), md)
    export_glb("assets/models/diag_missing.glb")


if __name__ == "__main__":
    build_env_models()
    build_prop_models()
    build_item_and_character_models()
    print("All GLB 3D models exported successfully via Blender.")

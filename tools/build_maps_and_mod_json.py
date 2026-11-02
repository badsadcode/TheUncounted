#!/usr/bin/env python3
"""
Generates the 3 interconnected region maps (Bellwether, The Old Road, Registry Annex / Crypt)
and the working Example Mod (mods/example_mod/) in external JSON format.
"""

# NOTE: bootstrap generator. content/regions/*.json has since been extended by hand (story, side quest, readables, torches,
# tuning). Re-running this script overwrites those files; edit the JSON directly instead.


import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


TORCH_MODEL = "assets/models/props/wall_torch.glb"


def torch(tid, x, y, z, rot, ghost=False):
    """Wall torch prop with a flame emitter (sprite + point light) at its head."""
    return {
        "id": tid, "model": TORCH_MODEL, "pos": [x, y, z], "rot_y": rot, "scale": [1.0, 1.0, 1.0], "solid": False,
        "emitter": {
            "sprite": "assets/sprites/vfx/spell_arcane.png" if ghost else "assets/sprites/vfx/torch_flame.png",
            "offset": [0.0, 0.86, 0.0], "size": 0.32 if ghost else 0.38,
            "light_color": [0.45, 0.8, 1.0] if ghost else [1.0, 0.62, 0.28], "light_radius": 6.5,
        },
    }


MAP_TORCHES = {
    "core:map.bellwether": [
        torch("torch_records_back", -6.0, 1.7, -14.45, 0.0),
        torch("torch_records_side", -10.45, 1.7, -10.0, 90.0),
        torch("torch_shop_back", 8.0, 1.6, -12.95, 0.0),
        torch("torch_inn_back", -6.5, 1.7, 13.95, 180.0),
        torch("torch_gate_n", 19.15, 2.0, -3.4, -90.0),
        torch("torch_gate_s", 19.15, 2.0, 3.4, -90.0),
        torch("torch_wall_n", 0.0, 2.1, -19.15, 0.0),
        torch("torch_wall_s", 0.0, 2.1, 19.15, 180.0),
        torch("torch_wall_w", -19.15, 2.1, -6.0, 90.0),
    ],
    "core:map.old_road": [
        torch("torch_annex_l", 23.95, 2.3, -3.5, -90.0),
        torch("torch_annex_r", 23.95, 2.3, 3.5, -90.0),
    ],
    "core:map.registry_annex": [
        torch("torch_foyer_w", -5.45, 1.8, 1.5, 90.0),
        torch("torch_foyer_e", 5.45, 1.8, -1.0, -90.0),
        torch("torch_archive_e", 9.45, 1.8, -7.0, -90.0),
        torch("torch_archive_n", -6.0, 1.8, -17.45, 0.0),
        torch("torch_vault", 6.0, 1.8, -24.45, 0.0, ghost=True),
        torch("torch_crypt_w", -21.45, 1.8, -9.0, 90.0, ghost=True),
        torch("torch_sanctum_w", -21.45, 1.8, -22.0, 90.0, ghost=True),
        torch("torch_sanctum_e", -10.55, 1.8, -22.0, -90.0, ghost=True),
    ],
}
MAP_WEATHER = {'core:map.bellwether': 'rain', 'core:map.registry_annex': 'dust'}


def write_json(rel_path, data):
    # Models are anchored at their bounding-box bottom by the runtime; ground slabs listed with a
    # negative "center" height are shifted so their walkable top surface lands at ~y=0.
    for prop in data.get("props", []) if isinstance(data, dict) else []:
        if "/floor_" in prop["model"] and prop["pos"][1] < 0:
            prop["pos"][1] = round(prop["pos"][1] - prop["scale"][1] / 2, 3)
    if isinstance(data, dict) and data.get("id") in MAP_TORCHES:
        data["props"] = data["props"] + MAP_TORCHES[data["id"]]
        if data["id"] in MAP_WEATHER:
            data["weather"] = MAP_WEATHER[data["id"]]
    full_path = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def build_bellwether():
    props = []
    # Ground tiles (cobble main road + grass surroundings)
    props.append({"id": "ground_grass", "model": "assets/models/env/floor_grass.glb", "pos": [0.0, -0.25, 0.0], "scale": [48.0, 0.5, 48.0], "uv_scale": [16.0, 16.0], "solid": False})
    props.append({"id": "road_main", "model": "assets/models/env/floor_cobble.glb", "pos": [0.0, -0.22, 0.0], "scale": [40.0, 0.5, 7.0], "uv_scale": [12.0, 2.5], "solid": False})
    props.append({"id": "plaza_center", "model": "assets/models/env/floor_cobble.glb", "pos": [0.0, -0.21, 0.0], "scale": [16.0, 0.5, 18.0], "uv_scale": [5.0, 5.0], "solid": False})

    # Perimeter town walls
    props.append({"id": "wall_north", "model": "assets/models/env/wall_stone.glb", "pos": [0.0, 0.0, -20.0], "scale": [42.0, 4.5, 1.2], "uv_scale": [10.0, 1.5], "solid": True})
    props.append({"id": "wall_south", "model": "assets/models/env/wall_stone.glb", "pos": [0.0, 0.0, 20.0], "scale": [42.0, 4.5, 1.2], "uv_scale": [10.0, 1.5], "solid": True})
    props.append({"id": "wall_west", "model": "assets/models/env/wall_stone.glb", "pos": [-20.0, 0.0, 0.0], "scale": [1.2, 4.5, 40.0], "uv_scale": [10.0, 1.5], "solid": True})
    props.append({"id": "wall_east_n", "model": "assets/models/env/wall_stone.glb", "pos": [20.0, 0.0, -11.5], "scale": [1.2, 4.5, 17.0], "uv_scale": [4.0, 1.5], "solid": True})
    props.append({"id": "wall_east_s", "model": "assets/models/env/wall_stone.glb", "pos": [20.0, 0.0, 11.5], "scale": [1.2, 4.5, 17.0], "uv_scale": [4.0, 1.5], "solid": True})
    props.append({"id": "east_arch", "model": "assets/models/env/archway_stone.glb", "pos": [19.5, 0.0, 0.0], "rot_y": 90.0, "scale": [1.8, 1.2, 1.5], "solid": False})

    # Building 1: Royal Bureau of Records Office (North-West: x=-8..0, z=-14..-5)
    props.append({"id": "rec_floor", "model": "assets/models/env/floor_wood.glb", "pos": [-6.0, -0.18, -10.5], "scale": [10.0, 0.5, 9.0], "uv_scale": [4.0, 4.0], "solid": False})
    props.append({"id": "rec_roof", "model": "assets/models/env/floor_wood.glb", "pos": [-6.0, 3.8, -10.5], "scale": [10.4, 0.4, 9.4], "uv_scale": [4.0, 4.0], "solid": False})
    props.append({"id": "rec_w_back", "model": "assets/models/env/wall_timber.glb", "pos": [-6.0, 0.0, -15.0], "scale": [10.0, 3.8, 0.6], "uv_scale": [3.0, 1.0], "solid": True})
    props.append({"id": "rec_w_left", "model": "assets/models/env/wall_timber.glb", "pos": [-11.0, 0.0, -10.5], "scale": [0.6, 3.8, 9.0], "uv_scale": [3.0, 1.0], "solid": True})
    props.append({"id": "rec_w_right", "model": "assets/models/env/wall_timber.glb", "pos": [-1.0, 0.0, -10.5], "scale": [0.6, 3.8, 9.0], "uv_scale": [3.0, 1.0], "solid": True})
    props.append({"id": "rec_w_front_l", "model": "assets/models/env/wall_timber.glb", "pos": [-9.0, 0.0, -6.0], "scale": [4.0, 3.8, 0.6], "uv_scale": [1.5, 1.0], "solid": True})
    props.append({"id": "rec_w_front_r", "model": "assets/models/env/wall_timber.glb", "pos": [-3.0, 0.0, -6.0], "scale": [4.0, 3.8, 0.6], "uv_scale": [1.5, 1.0], "solid": True})
    props.append({"id": "rec_desk", "model": "assets/models/props/registry_desk.glb", "pos": [-6.0, 0.0, -11.2], "rot_y": 0.0, "scale": [1.1, 1.0, 1.1], "solid": True})
    props.append({"id": "rec_shelf_1", "model": "assets/models/props/bookshelf_prop.glb", "pos": [-9.5, 0.0, -14.2], "rot_y": 0.0, "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "rec_shelf_2", "model": "assets/models/props/bookshelf_prop.glb", "pos": [-2.5, 0.0, -14.2], "rot_y": 0.0, "scale": [1.0, 1.0, 1.0], "solid": True})

    # Building 2: Vaelen's Provisions Pavilion (North-East: x=4..12, z=-13..-6)
    props.append({"id": "shop_floor", "model": "assets/models/env/floor_wood.glb", "pos": [8.0, -0.18, -10.0], "scale": [8.0, 0.5, 7.0], "uv_scale": [3.0, 3.0], "solid": False})
    props.append({"id": "shop_back", "model": "assets/models/env/wall_timber.glb", "pos": [8.0, 0.0, -13.5], "scale": [8.0, 3.6, 0.6], "uv_scale": [2.5, 1.0], "solid": True})
    props.append({"id": "shop_crate1", "model": "assets/models/props/wooden_crate.glb", "pos": [5.2, 0.0, -12.0], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "shop_crate2", "model": "assets/models/props/wooden_crate.glb", "pos": [10.8, 0.0, -12.0], "scale": [1.0, 1.2, 1.0], "solid": True})

    # Building 3: The Lantern Inn (South-West: x=-11..-2, z=6..14)
    props.append({"id": "inn_floor", "model": "assets/models/env/floor_wood.glb", "pos": [-6.5, -0.18, 10.5], "scale": [9.0, 0.5, 8.0], "uv_scale": [3.5, 3.5], "solid": False})
    props.append({"id": "inn_roof", "model": "assets/models/env/floor_wood.glb", "pos": [-6.5, 3.8, 10.5], "scale": [9.4, 0.4, 8.4], "uv_scale": [3.5, 3.5], "solid": False})
    props.append({"id": "inn_back", "model": "assets/models/env/wall_timber.glb", "pos": [-6.5, 0.0, 14.5], "scale": [9.0, 3.8, 0.6], "uv_scale": [3.0, 1.0], "solid": True})
    props.append({"id": "inn_left", "model": "assets/models/env/wall_timber.glb", "pos": [-11.0, 0.0, 10.5], "scale": [0.6, 3.8, 8.0], "uv_scale": [2.5, 1.0], "solid": True})
    props.append({"id": "inn_right", "model": "assets/models/env/wall_timber.glb", "pos": [-2.0, 0.0, 10.5], "scale": [0.6, 3.8, 8.0], "uv_scale": [2.5, 1.0], "solid": True})

    # Building 4: Library & Dawn Shrine (South-East: x=4..13, z=6..14)
    props.append({"id": "lib_floor", "model": "assets/models/env/floor_cobble.glb", "pos": [8.5, -0.18, 10.5], "scale": [9.0, 0.5, 8.0], "uv_scale": [3.0, 3.0], "solid": False})
    props.append({"id": "lib_shelf1", "model": "assets/models/props/bookshelf_prop.glb", "pos": [5.5, 0.0, 13.5], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "lib_shelf2", "model": "assets/models/props/bookshelf_prop.glb", "pos": [7.5, 0.0, 13.5], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "dawn_altar", "model": "assets/models/props/altar_dawn.glb", "pos": [11.5, 0.0, 12.5], "rot_y": 180.0, "scale": [1.0, 1.0, 1.0], "solid": True})

    # Trees & Landmarks
    for idx, (tx, tz) in enumerate([(-15, -16), (-16, 15), (15, -16), (15, 16), (-14, -5), (14, -4)]):
        props.append({"id": f"tree_{idx}", "model": "assets/models/env/tree_pine.glb", "pos": [float(tx), 0.0, float(tz)], "scale": [1.0, 1.1, 1.0], "solid": True})
    props.append({"id": "road_sign", "model": "assets/models/props/signpost.glb", "pos": [14.5, 0.0, -2.5], "rot_y": 45.0, "scale": [1.0, 1.0, 1.0], "solid": True})

    write_json("content/regions/bellwether.json", {
        "schema_version": 1,
        "id": "core:map.bellwether",
        "display_name_key": "map.bellwether.name",
        "music": "assets/audio/music/bellwether_theme.wav",
        "ambience": "assets/audio/ambience/village_rain.wav",
        "sky_color": [22, 28, 44],
        "ambient_color": [0.42, 0.45, 0.56],
        "sun_direction": [-0.4, 0.8, -0.3],
        "sun_color": [0.55, 0.52, 0.65],
        "fog_color": [0.10, 0.13, 0.20],
        "fog_density": 0.022,
        "spawns": {
            "village_gate": {"pos": [-15.0, 0.0, 0.0], "yaw_degrees": 90.0},
            "from_old_road": {"pos": [16.5, 0.0, 0.0], "yaw_degrees": -90.0}
        },
        "props": props,
        "lights": [
            {"pos": [-6.0, 2.8, -9.5], "color": [1.0, 0.76, 0.42], "radius": 11.0},
            {"pos": [8.0, 2.8, -9.5], "color": [1.0, 0.78, 0.46], "radius": 10.0},
            {"pos": [-6.5, 2.8, 9.5], "color": [1.0, 0.72, 0.38], "radius": 11.0},
            {"pos": [8.5, 2.8, 10.5], "color": [0.85, 0.82, 1.0], "radius": 11.0},
            {"pos": [17.5, 3.0, 0.0], "color": [1.0, 0.72, 0.38], "radius": 10.0}
        ],
        "npcs": [
            {"instance_id": "npc_oakhaven", "npc_id": "core:npc.clerk_oakhaven", "pos": [-6.0, 0.0, -12.6], "yaw": 0.0},
            {"instance_id": "npc_vaelen", "npc_id": "core:npc.merchant_vaelen", "pos": [8.0, 0.0, -10.5], "yaw": 0.0},
            {"instance_id": "npc_marta", "npc_id": "core:npc.innkeeper_marta", "pos": [-6.5, 0.0, 11.5], "yaw": 180.0},
            {"instance_id": "npc_fenwick", "npc_id": "core:npc.librarian_fenwick", "pos": [6.5, 0.0, 11.2], "yaw": 180.0},
            {"instance_id": "npc_aldous", "npc_id": "core:npc.brother_aldous", "pos": [11.5, 0.0, 10.5], "yaw": 180.0}
        ],
        "creatures": [],
        "interactables": [
            {
                "instance_id": "records_notice_lectern",
                "type": "readable",
                "model": "assets/models/props/lectern_ledger.glb",
                "pos": [-3.5, 0.0, -7.8],
                "rot_y": 0.0,
                "prompt": "Read Bureau Notice",
                "title": "Municipal Ordinance 404",
                "text": "NOTICE TO CITIZENS:\nAny resident discovering that their house, spouse, or childhood never existed must file Form 88-A before sundown. Unregistered nostalgia is punishable by a five-crown fine."
            },
            {
                "instance_id": "records_supply_chest",
                "type": "chest",
                "model": "assets/models/props/treasure_chest.glb",
                "pos": [-9.2, 0.0, -9.0],
                "rot_y": 90.0,
                "locked": False,
                "loot_table": "core:loot.vermin_drop",
                "fixed_items": ["core:item.health_potion", "core:item.lockpick"]
            },
            {
                "instance_id": "shrine_free_tome",
                "type": "pickup",
                "item_id": "core:item.tome_mend",
                "qty": 1,
                "pos": [10.0, 0.2, 12.2]
            },
            {
                "instance_id": "inn_free_bread",
                "type": "pickup",
                "item_id": "core:item.bread_loaf",
                "qty": 2,
                "pos": [-4.5, 0.2, 10.0]
            }
        ],
        "portals": [
            {
                "id": "to_old_road",
                "pos": [19.0, 0.0, 0.0],
                "radius": 2.2,
                "prompt": "Travel East to The Old Road",
                "destination_map": "core:map.old_road",
                "destination_spawn": "from_bellwether"
            }
        ]
    })


def build_old_road():
    props = []
    # Woodland ground + winding dirt road
    props.append({"id": "ground_forest", "model": "assets/models/env/floor_grass.glb", "pos": [0.0, -0.25, 0.0], "scale": [64.0, 0.5, 36.0], "uv_scale": [20.0, 12.0], "solid": False})
    props.append({"id": "road_path", "model": "assets/models/env/floor_cobble.glb", "pos": [0.0, -0.21, 0.0], "scale": [56.0, 0.5, 5.5], "uv_scale": [18.0, 2.0], "solid": False})

    # Canyon / Woodland boundary walls
    props.append({"id": "cliff_north", "model": "assets/models/env/wall_stone.glb", "pos": [0.0, 0.0, -15.0], "scale": [60.0, 5.0, 1.5], "uv_scale": [15.0, 1.5], "solid": True})
    props.append({"id": "cliff_south", "model": "assets/models/env/wall_stone.glb", "pos": [0.0, 0.0, 15.0], "scale": [60.0, 5.0, 1.5], "uv_scale": [15.0, 1.5], "solid": True})
    props.append({"id": "cliff_west", "model": "assets/models/env/wall_stone.glb", "pos": [-28.0, 0.0, 0.0], "scale": [1.5, 5.0, 30.0], "uv_scale": [8.0, 1.5], "solid": True})
    props.append({"id": "cliff_east", "model": "assets/models/env/wall_crypt.glb", "pos": [28.0, 0.0, 0.0], "scale": [1.5, 5.5, 30.0], "uv_scale": [8.0, 1.5], "solid": True})

    # Annex Facade at East End (x=25..28)
    props.append({"id": "annex_arch", "model": "assets/models/env/archway_stone.glb", "pos": [25.5, 0.0, 0.0], "rot_y": 90.0, "scale": [1.6, 1.2, 1.5], "solid": False})
    props.append({"id": "annex_pillar_l", "model": "assets/models/env/pillar_stone.glb", "pos": [24.5, 0.0, -3.5], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "annex_pillar_r", "model": "assets/models/env/pillar_stone.glb", "pos": [24.5, 0.0, 3.5], "scale": [1.0, 1.0, 1.0], "solid": True})

    # Mid-road Ruined Watch Arch & Great Silence Monolith
    props.append({"id": "mid_arch", "model": "assets/models/env/archway_stone.glb", "pos": [0.0, 0.0, 0.0], "rot_y": 90.0, "scale": [1.8, 1.2, 1.5], "solid": False})
    props.append({"id": "silence_monolith", "model": "assets/models/env/ruin_monolith.glb", "pos": [4.0, 0.0, -7.5], "scale": [1.0, 1.0, 1.0], "solid": True})

    # Pine forest clusters
    tree_coords = [
        (-20, -8), (-14, -10), (-6, -9), (8, -10), (16, -8), (20, -10),
        (-20, 8), (-12, 9), (-4, 10), (6, 9), (14, 8), (21, 9)
    ]
    for i, (tx, tz) in enumerate(tree_coords):
        props.append({"id": f"forest_tree_{i}", "model": "assets/models/env/tree_pine.glb", "pos": [float(tx), 0.0, float(tz)], "scale": [1.1, 1.2, 1.1], "solid": True})

    write_json("content/regions/old_road.json", {
        "schema_version": 1,
        "id": "core:map.old_road",
        "display_name_key": "map.old_road.name",
        "music": "assets/audio/music/old_road_theme.wav",
        "ambience": "assets/audio/ambience/forest_wind.wav",
        "sky_color": [18, 26, 36],
        "ambient_color": [0.36, 0.42, 0.48],
        "sun_direction": [-0.3, 0.7, 0.4],
        "sun_color": [0.45, 0.50, 0.55],
        "fog_color": [0.08, 0.12, 0.16],
        "fog_density": 0.028,
        "spawns": {
            "from_bellwether": {"pos": [-24.0, 0.0, 0.0], "yaw_degrees": 90.0},
            "from_annex": {"pos": [21.5, 0.0, 0.0], "yaw_degrees": -90.0}
        },
        "props": props,
        "lights": [
            {"pos": [-18.0, 2.5, -3.5], "color": [1.0, 0.72, 0.35], "radius": 10.0},
            {"pos": [4.0, 2.8, -7.5], "color": [0.45, 0.85, 1.0], "radius": 11.0},
            {"pos": [24.0, 2.8, 0.0], "color": [1.0, 0.68, 0.32], "radius": 11.0}
        ],
        "npcs": [
            {"instance_id": "npc_kaelen", "npc_id": "core:npc.ashbound_scout", "pos": [-17.5, 0.0, -3.8], "yaw": 45.0}
        ],
        "creatures": [
            {"instance_id": "road_rat_1", "creature_id": "core:enemy.grave_rat", "pos": [-5.0, 0.0, 1.2], "patrol_a": [-8.0, 0.0, 1.2], "patrol_b": [-2.0, 0.0, -1.2]},
            {"instance_id": "road_rat_2", "creature_id": "core:enemy.grave_rat", "pos": [6.0, 0.0, -1.5], "patrol_a": [3.0, 0.0, -1.5], "patrol_b": [10.0, 0.0, 1.5]},
            {"instance_id": "road_crawler_1", "creature_id": "core:enemy.ash_crawler", "pos": [15.5, 0.0, 2.0], "patrol_a": [12.0, 0.0, 2.0], "patrol_b": [19.0, 0.0, -2.0]}
        ],
        "interactables": [
            {
                "instance_id": "monolith_inscription",
                "type": "readable",
                "model": "assets/models/props/lectern_ledger.glb",
                "pos": [4.0, 0.0, -5.8],
                "rot_y": 0.0,
                "prompt": "Inspect Weathered Boundary Stone",
                "title": "Boundary Marker of the Third Reign",
                "text": "\"Here stood the market-borough of Oakhallow, population 412.\"\n\nBeneath the chiseled letters, someone has scratched in fresh charcoal: \"There is only forest here. Why do I remember the baker's daughter?\""
            },
            {
                "instance_id": "road_ranger_chest",
                "type": "chest",
                "model": "assets/models/props/treasure_chest.glb",
                "pos": [5.5, 0.0, -8.8],
                "rot_y": 0.0,
                "locked": True,
                "lock_difficulty": 5,
                "loot_table": "core:loot.crypt_basic",
                "fixed_items": ["core:item.tome_ember", "core:item.wooden_arrow"]
            },
            {
                "instance_id": "road_arrow_bundle",
                "type": "pickup",
                "item_id": "core:item.wooden_arrow",
                "qty": 12,
                "pos": [-16.0, 0.2, -2.5]
            }
        ],
        "portals": [
            {
                "id": "to_bellwether",
                "pos": [-26.5, 0.0, 0.0],
                "radius": 2.4,
                "prompt": "Return West to Bellwether Village",
                "destination_map": "core:map.bellwether",
                "destination_spawn": "from_old_road"
            },
            {
                "id": "to_registry_annex",
                "pos": [25.2, 0.0, 0.0],
                "radius": 2.4,
                "prompt": "Enter Registry Annex & Forgotten Crypt",
                "destination_map": "core:map.registry_annex",
                "destination_spawn": "annex_entry"
            }
        ]
    })


def build_registry_annex():
    """
    Layout of Registry Annex & Forgotten Crypt (all coordinates in X, Z):
    - Room 1 (Foyer): x = -6..6, z = -4..6
    - Room 2 (Archive Hall, North of Foyer): x = -10..10, z = -18..-4
      - Doorway between Foyer and Archive at (0, -4) guarded by locked door `annex_inner_door` (uses `core:item.annex_key` or Lockpick)
      - East Alcove of Archive (x=8, z=-11): Iron Lever `crypt_gate_lever` -> opens `crypt_portcullis` at West corridor (-10, -11)
      - West Alcove of Archive (x=-8, z=-15): Pressure Plate `secret_plate` -> opens `secret_wall_door` at (6, -18)
    - Room 3 (Secret Royal Treasury): x = 3..9, z = -25..-18 (behind `secret_wall_door` at x=6, z=-18)
      - Contains `secret_widowmaker_chest` with *The Widowmaker* (`core:item.widowmaker`) and `core:item.tome_veil`!
    - Room 4 (Western Crypt Passage): x = -22..-10, z = -16..-6 (entered through `crypt_portcullis` at x=-10, z=-11)
      - Guarded by 3D `core:enemy.lost_sentinel` (`lost_sentinel.glb`) and `core:enemy.ash_crawler`.
      - Contains `core:npc.erased_spirit` (gives `core:item.crypt_key`).
    - Room 5 (Sanctum of the Uncounted Ledger, North of Crypt Passage): x = -24..-10, z = -32..-16
      - Entered through `sanctum_gate` at (-16, -16) (unlocked with `core:item.crypt_key` or Lockpick).
      - Final Boss: `core:enemy.crypt_keeper` (Archivist Shade Morvath) + Grand Lectern (`grand_ledger_lectern`).
    """
    props = []
    # Unified floor & ceiling slabs covering the dungeon footprint
    props.append({"id": "dungeon_floor", "model": "assets/models/env/floor_cobble.glb", "pos": [-6.0, -0.25, -14.0], "scale": [44.0, 0.5, 46.0], "uv_scale": [18.0, 18.0], "solid": False})
    props.append({"id": "dungeon_ceiling", "model": "assets/models/env/wall_crypt.glb", "pos": [-6.0, 4.2, -14.0], "scale": [44.0, 0.5, 46.0], "uv_scale": [18.0, 18.0], "solid": False})

    # Outer shell & dividing walls
    walls = [
        # Room 1 Foyer walls (x=-6..6, z=-4..6)
        ("foyer_s", [0.0, 0.0, 6.0], [13.0, 4.2, 0.8]),
        ("foyer_w", [-6.0, 0.0, 1.0], [0.8, 4.2, 10.0]),
        ("foyer_e", [6.0, 0.0, 1.0], [0.8, 4.2, 10.0]),
        ("foyer_n_l", [-3.8, 0.0, -4.0], [5.2, 4.2, 0.8]),
        ("foyer_n_r", [3.8, 0.0, -4.0], [5.2, 4.2, 0.8]),

        # Room 2 Archive Hall walls (x=-10..10, z=-18..-4)
        ("arch_s_l", [-8.0, 0.0, -4.0], [4.0, 4.2, 0.8]),
        ("arch_s_r", [8.0, 0.0, -4.0], [4.0, 4.2, 0.8]),
        ("arch_e", [10.0, 0.0, -11.0], [0.8, 4.2, 14.0]),
        ("arch_n_l", [-2.5, 0.0, -18.0], [15.0, 4.2, 0.8]),
        ("arch_n_r", [8.8, 0.0, -18.0], [2.8, 4.2, 0.8]),
        ("arch_w_s", [-10.0, 0.0, -6.8], [0.8, 4.2, 5.6]),
        ("arch_w_n", [-10.0, 0.0, -15.2], [0.8, 4.2, 5.6]),

        # Room 3 Secret Treasury walls (x=3..9, z=-25..-18, doorway at x=6, z=-18)
        ("sec_w", [3.0, 0.0, -21.5], [0.8, 4.2, 7.0]),
        ("sec_e", [9.0, 0.0, -21.5], [0.8, 4.2, 7.0]),
        ("sec_n", [6.0, 0.0, -25.0], [6.8, 4.2, 0.8]),

        # Room 4 Western Crypt Passage (x=-22..-10, z=-16..-6)
        ("crypt_s", [-16.0, 0.0, -6.0], [12.8, 4.2, 0.8]),
        ("crypt_w", [-22.0, 0.0, -11.0], [0.8, 4.2, 10.8]),
        ("crypt_n_l", [-19.8, 0.0, -16.0], [5.2, 4.2, 0.8]),
        ("crypt_n_r", [-12.2, 0.0, -16.0], [5.2, 4.2, 0.8]),

        # Room 5 Sanctum of the Uncounted Ledger (x=-22..-10, z=-30..-16)
        ("sanc_w", [-22.0, 0.0, -23.0], [0.8, 4.2, 14.0]),
        ("sanc_e", [-10.0, 0.0, -23.0], [0.8, 4.2, 14.0]),
        ("sanc_n", [-16.0, 0.0, -30.0], [12.8, 4.2, 0.8])
    ]
    for wid, wpos, wscale in walls:
        props.append({
            "id": wid,
            "model": "assets/models/env/wall_crypt.glb",
            "pos": wpos,
            "scale": wscale,
            "uv_scale": [max(1.0, (wscale[0] + wscale[2]) * 0.35), 1.4],
            "solid": True
        })

    # Atmospheric props inside the dungeon
    props.append({"id": "foyer_desk", "model": "assets/models/props/registry_desk.glb", "pos": [-3.2, 0.0, 1.5], "rot_y": 25.0, "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "arch_pillar_1", "model": "assets/models/env/pillar_stone.glb", "pos": [-4.5, 0.0, -11.0], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "arch_pillar_2", "model": "assets/models/env/pillar_stone.glb", "pos": [4.5, 0.0, -11.0], "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "arch_shelf_1", "model": "assets/models/props/bookshelf_prop.glb", "pos": [0.0, 0.0, -17.1], "scale": [1.2, 1.0, 1.0], "solid": True})
    props.append({"id": "crypt_sarc_1", "model": "assets/models/props/sarcophagus.glb", "pos": [-19.5, 0.0, -11.0], "rot_y": 90.0, "scale": [1.0, 1.0, 1.0], "solid": True})
    props.append({"id": "sanc_mono_l", "model": "assets/models/env/ruin_monolith.glb", "pos": [-19.5, 0.0, -26.5], "scale": [0.9, 0.9, 0.9], "solid": True})
    props.append({"id": "sanc_mono_r", "model": "assets/models/env/ruin_monolith.glb", "pos": [-12.5, 0.0, -26.5], "scale": [0.9, 0.9, 0.9], "solid": True})

    write_json("content/regions/registry_annex.json", {
        "schema_version": 1,
        "id": "core:map.registry_annex",
        "display_name_key": "map.registry_annex.name",
        "music": "assets/audio/music/crypt_theme.wav",
        "ambience": "assets/audio/ambience/crypt_drips.wav",
        "sky_color": [8, 10, 16],
        "ambient_color": [0.22, 0.25, 0.34],
        "sun_direction": [0.0, 1.0, 0.0],
        "sun_color": [0.10, 0.12, 0.18],
        "fog_color": [0.04, 0.05, 0.09],
        "fog_density": 0.038,
        "spawns": {
            "annex_entry": {"pos": [0.0, 0.0, 4.0], "yaw_degrees": 180.0}
        },
        "props": props,
        "lights": [
            {"pos": [0.0, 2.8, 2.0], "color": [1.0, 0.68, 0.32], "radius": 10.5},
            {"pos": [0.0, 2.8, -10.5], "color": [1.0, 0.65, 0.30], "radius": 12.0},
            {"pos": [8.2, 2.6, -11.0], "color": [1.0, 0.75, 0.35], "radius": 8.5},
            {"pos": [6.0, 2.8, -22.0], "color": [0.40, 0.88, 1.0], "radius": 10.0},
            {"pos": [-15.5, 2.8, -11.0], "color": [0.55, 0.85, 1.0], "radius": 11.5},
            {"pos": [-16.0, 3.0, -25.0], "color": [0.45, 0.90, 1.0], "radius": 14.0}
        ],
        "npcs": [
            {"instance_id": "npc_spirit", "npc_id": "core:npc.erased_spirit", "pos": [-19.5, 0.0, -7.8], "yaw": 45.0}
        ],
        "creatures": [
            {"instance_id": "foyer_rat", "creature_id": "core:enemy.grave_rat", "pos": [2.5, 0.0, 0.5], "patrol_a": [-2.5, 0.0, 0.5], "patrol_b": [3.0, 0.0, 0.5]},
            {"instance_id": "archive_skel_1", "creature_id": "core:enemy.restless_skeleton", "pos": [-2.5, 0.0, -9.5], "patrol_a": [-6.0, 0.0, -9.5], "patrol_b": [4.0, 0.0, -9.5]},
            {"instance_id": "archive_crawler_1", "creature_id": "core:enemy.ash_crawler", "pos": [5.5, 0.0, -14.0], "patrol_a": [2.0, 0.0, -14.0], "patrol_b": [8.0, 0.0, -12.0]},
            {"instance_id": "crypt_sentinel_1", "creature_id": "core:enemy.lost_sentinel", "pos": [-14.5, 0.0, -11.5], "patrol_a": [-14.5, 0.0, -9.0], "patrol_b": [-14.5, 0.0, -14.0]},
            {"instance_id": "sanctum_boss", "creature_id": "core:enemy.crypt_keeper", "pos": [-16.0, 0.0, -24.5], "patrol_a": [-18.0, 0.0, -24.5], "patrol_b": [-14.0, 0.0, -24.5]}
        ],
        "interactables": [
            {
                "instance_id": "annex_inner_door",
                "type": "door",
                "model": "assets/models/props/oak_door.glb",
                "pos": [0.0, 0.0, -4.0],
                "rot_y": 0.0,
                "locked": True,
                "key_id": "core:item.annex_key",
                "lock_difficulty": 8,
                "prompt": "Archive Door"
            },
            {
                "instance_id": "crypt_portcullis",
                "type": "door",
                "model": "assets/models/props/iron_gate.glb",
                "pos": [-10.0, 0.0, -11.0],
                "rot_y": 90.0,
                "locked": True,
                "mechanism_only": True,
                "prompt": "Lower Crypt Portcullis (Controlled by Archive Lever)"
            },
            {
                "instance_id": "crypt_gate_lever",
                "type": "lever",
                "model": "assets/models/props/iron_lever.glb",
                "pos": [8.6, 0.0, -11.0],
                "rot_y": -90.0,
                "target_id": "crypt_portcullis",
                "prompt": "Pull Iron Archive Lever"
            },
            {
                "instance_id": "secret_wall_door",
                "type": "door",
                "model": "assets/models/props/iron_gate.glb",
                "pos": [6.0, 0.0, -18.0],
                "rot_y": 0.0,
                "locked": True,
                "mechanism_only": True,
                "prompt": "Sealed Royal Vault Gate (Step on Rune Plate)"
            },
            {
                "instance_id": "secret_plate",
                "type": "pressure_plate",
                "model": "assets/models/props/pressure_plate.glb",
                "pos": [-7.5, 0.0, -15.5],
                "rot_y": 0.0,
                "target_id": "secret_wall_door",
                "prompt": "Ancient Rune Pressure Plate"
            },
            {
                "instance_id": "sanctum_gate",
                "type": "door",
                "model": "assets/models/props/oak_door.glb",
                "pos": [-16.0, 0.0, -16.0],
                "rot_y": 0.0,
                "locked": True,
                "key_id": "core:item.crypt_key",
                "lock_difficulty": 12,
                "prompt": "Sanctum of the Uncounted Gate"
            },
            {
                "instance_id": "archive_clue_lectern",
                "type": "readable",
                "model": "assets/models/props/lectern_ledger.glb",
                "pos": [2.2, 0.0, -15.8],
                "rot_y": 0.0,
                "prompt": "Read Chief Archivist's Log",
                "title": "Chief Archivist Morvath's Log",
                "text": "\"The portcullis to the lower crypt is controlled by the eastern wall-lever. Should the King's inquisitors ever breach this hall, the Royal Treasury gate to the north opens only when weight is placed upon the rune-plate in the north-west corner.\""
            },
            {
                "instance_id": "secret_widowmaker_chest",
                "type": "chest",
                "model": "assets/models/props/treasure_chest.glb",
                "pos": [6.0, 0.0, -23.2],
                "rot_y": 0.0,
                "locked": False,
                "loot_table": "core:loot.secret_widowmaker",
                "fixed_items": ["core:item.widowmaker", "core:item.tome_veil"]
            },
            {
                "instance_id": "archive_supply_chest",
                "type": "chest",
                "model": "assets/models/props/treasure_chest.glb",
                "pos": [-7.8, 0.0, -6.2],
                "rot_y": 0.0,
                "locked": False,
                "loot_table": "core:loot.crypt_basic",
                "fixed_items": ["core:item.health_potion", "core:item.mana_potion"]
            },
            {
                "instance_id": "grand_ledger_lectern",
                "type": "quest_pedestal",
                "model": "assets/models/props/lectern_ledger.glb",
                "pos": [-16.0, 0.0, -27.8],
                "rot_y": 0.0,
                "prompt": "Claim Form 27-B & The Uncounted Ledger",
                "quest_id": "core:quest.legally_deceased",
                "set_stage": 30,
                "grant_items": ["core:item.form_27b", "core:item.uncounted_ledger"]
            }
        ],
        "portals": [
            {
                "id": "to_old_road",
                "pos": [0.0, 0.0, 5.2],
                "radius": 2.2,
                "prompt": "Exit to The Old Road",
                "destination_map": "core:map.old_road",
                "destination_spawn": "from_annex"
            }
        ]
    })


def build_example_mod():
    """
    Creates a complete, valid mod in mods/example_mod/ that demonstrates:
    1. Replacing the appearance of core:enemy.restless_skeleton with a Crimson Revenant sprite sheet.
    2. Adding a brand-new weapon (mod:item.ashbrand_blade) with its own external GLB model & PNG icon.
    3. Adding a brand-new enemy variant (mod:enemy.crimson_revenant).
    4. Overriding a core loot table so the Lost Sentinel can drop the new weapon.
    All without touching or recompiling C++!
    """
    write_json("mods/example_mod/manifest.json", {
        "schema_version": 1,
        "pack_id": "example_mod",
        "pack_name": "Crimson Ashbound Expansion (Modding Proof)",
        "version": "1.0.0",
        "localization": ["mods/example_mod/content/localization.json"],
        "items": ["mods/example_mod/content/items/mod_items.json"],
        "creatures": ["mods/example_mod/content/creatures/mod_creatures.json"],
        "loot_tables": ["mods/example_mod/content/loot_tables/mod_loot.json"]
    })

    write_json("mods/example_mod/content/loot_tables/mod_loot.json", {
        "schema_version": 1,
        "loot_tables": [
            {
                "id": "core:loot.crypt_elite",
                "gold_min": 25,
                "gold_max": 55,
                "entries": [
                    {
                        "item_id": "core:item.iron_longsword",
                        "weight": 35,
                        "min_qty": 1,
                        "max_qty": 1
                    },
                    {
                        "item_id": "core:item.health_potion",
                        "weight": 60,
                        "min_qty": 1,
                        "max_qty": 2
                    },
                    {
                        "item_id": "core:item.mana_potion",
                        "weight": 50,
                        "min_qty": 1,
                        "max_qty": 2
                    },
                    {
                        "item_id": "core:item.iron_helm",
                        "weight": 30,
                        "min_qty": 1,
                        "max_qty": 1
                    },
                    {
                        "item_id": "mod:item.ashbrand_blade",
                        "weight": 45,
                        "min_qty": 1,
                        "max_qty": 1
                    }
                ]
            }
        ]
    })

    write_json("mods/example_mod/content/localization.json", {
        "schema_version": 1,
        "language": "en",
        "strings": {
            "item.ashbrand_blade.name": "Ashbrand Sun-Blade",
            "item.ashbrand_blade.description": "A gilded relic blade added via external JSON + GLB mod with zero recompilation.",
            "enemy.crimson_revenant.name": "Crimson Revenant"
        }
    })

    write_json("mods/example_mod/content/items/mod_items.json", {
        "schema_version": 1,
        "items": [
            {
                "id": "mod:item.ashbrand_blade",
                "name_key": "item.ashbrand_blade.name",
                "description_key": "item.ashbrand_blade.description",
                "category": "weapon",
                "icon": "mods/example_mod/assets/ui/items/ashbrand_blade.png",
                "world_model": "mods/example_mod/assets/models/items/ashbrand_blade.glb",
                "slots": ["main_hand"],
                "value": 180,
                "weight": 2.5,
                "weapon": {
                    "kind": "melee",
                    "skill": "swords",
                    "damage_type": "fire",
                    "base_damage": 22,
                    "attack_time_seconds": 0.52,
                    "stamina_cost": 8,
                    "reach_meters": 2.4
                }
            }
        ]
    })

    write_json("mods/example_mod/content/creatures/mod_creatures.json", {
        "schema_version": 1,
        "creatures": [
            {
                "id": "core:enemy.restless_skeleton",
                "name_key": "enemy.restless_skeleton.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "mods/example_mod/assets/sprites/enemies/crimson_skeleton.png",
                    "animation_data": "assets/animations/skeleton.json",
                    "scale": 1.80
                },
                "stats": {"health": 52, "armor": 4, "move_speed": 2.5, "xp_reward": 45},
                "behavior": "melee_patroller",
                "perception": {"sight_meters": 13.0, "hearing_meters": 8.0},
                "attack": {
                    "name": "crimson_slash",
                    "damage": 13,
                    "reach_meters": 2.1,
                    "windup_seconds": 0.50,
                    "cooldown_seconds": 1.30
                },
                "loot_table": "core:loot.crypt_basic",
                "audio": {
                    "alert": "assets/audio/sfx/skeleton_alert.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            },
            {
                "id": "mod:enemy.crimson_revenant",
                "name_key": "enemy.crimson_revenant.name",
                "appearance": {
                    "type": "sprite_8dir",
                    "sprite_sheet": "mods/example_mod/assets/sprites/enemies/crimson_skeleton.png",
                    "animation_data": "assets/animations/skeleton.json",
                    "scale": 1.90
                },
                "stats": {"health": 65, "armor": 5, "move_speed": 2.6, "xp_reward": 55},
                "behavior": "melee_patroller",
                "perception": {"sight_meters": 14.0, "hearing_meters": 9.0},
                "attack": {
                    "name": "revenant_cleave",
                    "damage": 16,
                    "reach_meters": 2.2,
                    "windup_seconds": 0.50,
                    "cooldown_seconds": 1.25
                },
                "loot_table": "core:loot.crypt_elite",
                "audio": {
                    "alert": "assets/audio/sfx/skeleton_alert.wav",
                    "attack": "assets/audio/sfx/sword_swing.wav",
                    "hit": "assets/audio/sfx/sword_hit.wav",
                    "death": "assets/audio/sfx/enemy_death.wav"
                }
            }
        ]
    })


if __name__ == "__main__":
    build_bellwether()
    build_old_road()
    build_registry_annex()
    build_example_mod()
    print("All 3 region maps and example_mod JSON files generated.")

#!/usr/bin/env python3
"""
Composes the seamless overworld content/maps/edrath_world.json from the authored regions in content/regions/.

Layout (no loading screens, no portals):
  * Bellwether Village at the origin.
  * The Old Road directly east, its west end meeting Bellwether's east gate (x = 20).
  * The Registry Annex & Forgotten Crypt *underground* beneath the road's east end. A tunnel leaves the road
    through the cliff arch and descends two stone flights (4.8 m) to a landing that opens into the Annex foyer.
Each region becomes a zone with its own sky, fog, light, weather, music and ambience; the engine blends
between zones as the player walks.

Run:  python tools/build_world.py
"""

import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGIONS = os.path.join(ROOT, "content", "regions")
OUT = os.path.join(ROOT, "content", "maps", "edrath_world.json")

ROAD_OFF = (48.0, 0.0, 0.0)
ANNEX_OFF = (87.0, -4.8, -8.4)
VAULT_OFF = (54.6, -10.4, -22.0)   # Vault III: the Nursery lies 5.6 m below the crypt, the Seal Chamber 5.6 m below that
VAULT_Z = VAULT_OFF[2]
WALL = "assets/models/env/wall_crypt.glb"
COBBLE = "assets/models/env/floor_cobble.glb"
STAIRS = "assets/models/env/stairs_stone.glb"
TORCH = "assets/models/props/wall_torch.glb"


def load(name):
    with open(os.path.join(REGIONS, name), encoding="utf-8") as f:
        return json.load(f)


def offset(v, off):
    return [round(v[0] + off[0], 3), round(v[1] + off[1], 3), round(v[2] + off[2], 3)]


def shift_region(m, off, prefix):
    """Moves every positioned element of a region by `off`; prop ids get a region prefix (they are not persisted)."""
    for p in m.get("props", []):
        p["pos"] = offset(p["pos"], off)
        p["id"] = prefix + p["id"]
    for key in ("npcs", "creatures", "interactables"):
        for e in m.get(key, []):
            e["pos"] = offset(e["pos"], off)
            for k in ("patrol_a", "patrol_b"):
                if k in e:
                    e[k] = offset(e[k], off)
    for l in m.get("lights", []):
        l["pos"] = offset(l["pos"], off)
    for sp in m.get("spawns", {}).values():
        sp["pos"] = offset(sp["pos"], off)
    return m


def box_prop(pid, model, x0, x1, y0, y1, z0, z1, uv=None, solid=True):
    """Unit-cube model stretched to an axis-aligned box (models are anchored at their bottom centre)."""
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    p = {"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
         "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid}
    p["uv_scale"] = uv or [round(max(sx, sz) / 2.6, 2), round(sy / 3.0, 2)]
    return p


def extents(p):
    x, y, z = p["pos"]
    sx, sy, sz = p["scale"]
    return [x - sx / 2, x + sx / 2], [y, y + sy], [z - sz / 2, z + sz / 2]


def clip_x(p, lo=None, hi=None):
    """Clips an unrotated unit-cube prop along X (used where regions meet)."""
    (x0, x1), _, _ = extents(p)
    if lo is not None:
        x0 = max(x0, lo)
    if hi is not None:
        x1 = min(x1, hi)
    if x1 - x0 < 0.05:
        return None
    k = (x1 - x0) / p["scale"][0]
    p["pos"][0] = round((x0 + x1) / 2, 3)
    p["scale"][0] = round(x1 - x0, 3)
    if "uv_scale" in p:
        p["uv_scale"][0] = round(p["uv_scale"][0] * k, 2)
    return p


def clip_z(p, lo=None, hi=None):
    _, _, (z0, z1) = extents(p)
    if lo is not None:
        z0 = max(z0, lo)
    if hi is not None:
        z1 = min(z1, hi)
    k = (z1 - z0) / p["scale"][2]
    p["pos"][2] = round((z0 + z1) / 2, 3)
    p["scale"][2] = round(z1 - z0, 3)
    if "uv_scale" in p:
        p["uv_scale"][1 if p["scale"][1] < 1 else 0] = round(p["uv_scale"][1 if p["scale"][1] < 1 else 0] * k, 2)
    return p


def torch(tid, x, y, z, rot, ghost=False):
    return {"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False,
            "emitter": {"sprite": "assets/sprites/vfx/spell_arcane.png" if ghost else "assets/sprites/vfx/torch_flame.png",
                        "offset": [0.0, 0.86, 0.0], "size": 0.32 if ghost else 0.38,
                        "light_color": [0.45, 0.8, 1.0] if ghost else [1.0, 0.62, 0.28], "light_radius": 6.5}}


def zone_from(region, zid, box_min, box_max, blend):
    z = {"id": zid, "display_name_key": region["display_name_key"], "box_min": box_min, "box_max": box_max, "blend": blend}
    for k in ("music", "ambience", "sky_color", "ambient_color", "sun_direction", "sun_color", "fog_color", "fog_density"):
        z[k] = region[k]
    z["weather"] = region.get("weather", "")
    return z


def build():
    bell = shift_region(load("bellwether.json"), (0, 0, 0), "bell_")
    road = shift_region(load("old_road.json"), ROAD_OFF, "road_")
    annex = shift_region(load("registry_annex.json"), ANNEX_OFF, "annex_")
    vault = shift_region(load("vault_three.json"), VAULT_OFF, "vault_")

    props = list(bell["props"])

    # --- Old Road: drop its west cliff (Bellwether's east wall + gate is the boundary) and trim overlaps.
    road_east_x = ROAD_OFF[0] + 28.0 + 0.75  # outer face of the east cliff
    for p in road["props"]:
        pid = p["id"]
        if pid == "road_cliff_west":
            continue
        if pid == "road_cliff_east":
            # Split around a 3.2 m opening for the tunnel and close the top with a lintel.
            north = clip_z(copy.deepcopy(p), hi=-1.6)
            south = clip_z(copy.deepcopy(p), lo=1.6)
            north["id"], south["id"] = "road_cliff_east_n", "road_cliff_east_s"
            props += [north, south]
            lintel = copy.deepcopy(p)
            lintel.update({"id": "road_cliff_east_lintel"})
            lintel["pos"] = [p["pos"][0], 3.0, 0.0]
            lintel["scale"] = [p["scale"][0], p["scale"][1] - 3.0, 3.2]
            lintel["uv_scale"] = [1.2, 0.8]
            props.append(lintel)
            continue
        if pid in ("road_ground_forest", "road_road_path", "road_cliff_north", "road_cliff_south"):
            p = clip_x(p, lo=20.6, hi=road_east_x if pid == "road_ground_forest" else None)
            if p is None:
                continue
        props.append(p)

    # --- Tunnel: cliff opening -> two flights down -> landing -> Annex foyer.
    tx0 = road_east_x
    props += [
        box_prop("tunnel_threshold", COBBLE, ROAD_OFF[0] + 27.0, 77.0, -0.48, 0.02, -1.6, 1.6, uv=[1.2, 1.0], solid=False),
        {"id": "tunnel_stairs_upper", "model": STAIRS, "pos": [79.0, -2.4, 0.0], "rot_y": 90.0, "scale": [1.0, 1.2, 1.0],
         "solid": False, "ramp": "-x"},
        {"id": "tunnel_stairs_lower", "model": STAIRS, "pos": [83.0, -4.8, 0.0], "rot_y": 90.0, "scale": [1.0, 1.2, 1.0],
         "solid": False, "ramp": "-x"},
        box_prop("tunnel_wall_n", WALL, tx0, 85.15, -4.8, 3.4, -1.85, -1.55),
        box_prop("tunnel_wall_s", WALL, tx0, 85.15, -4.8, 3.4, 1.55, 1.85),
        box_prop("tunnel_ceiling_upper", WALL, tx0, 81.0, 3.0, 3.4, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_step", WALL, 80.85, 81.15, 1.0, 3.4, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_lower", WALL, 81.0, 85.0, 0.6, 1.0, -1.85, 1.85, solid=False),
        box_prop("tunnel_ceiling_drop", WALL, 84.85, 85.15, -1.6, 1.0, -1.85, 1.85, solid=False),
        box_prop("landing_floor", COBBLE, 85.0, 89.6, -5.3, -4.8, -1.6, 2.3, uv=[1.8, 1.5], solid=False),
        box_prop("landing_ceiling", WALL, 85.0, 89.6, -1.6, -1.2, -1.6, 2.3, solid=False),
        box_prop("landing_wall_s", WALL, 84.85, 89.6, -4.8, -1.2, 2.0, 2.3),
        box_prop("landing_wall_e", WALL, 89.3, 89.6, -4.8, -1.2, -1.6, 2.3),
        box_prop("landing_wall_w", WALL, 84.85, 85.15, -4.8, -1.2, 1.55, 2.3),
        torch("torch_tunnel_upper", 79.5, -0.3, 1.45, 180.0),
        torch("torch_landing", 89.2, -3.1, 0.3, -90.0),
    ]

    # --- Annex: open the foyer's south wall onto the landing; keep its floor/ceiling out of the tunnel.
    for p in annex["props"]:
        pid = p["id"]
        if pid == "annex_foyer_s":
            west = clip_x(copy.deepcopy(p), hi=85.8)
            east = clip_x(copy.deepcopy(p), lo=88.2)
            west["id"], east["id"] = "annex_foyer_s_w", "annex_foyer_s_e"
            props += [west, east]
            continue
        if pid == "annex_crypt_w":
            # Gap in the crypt's west wall for the stair down to Vault III, closed above by a lintel.
            north = clip_z(copy.deepcopy(p), hi=VAULT_Z - 1.6)
            south = clip_z(copy.deepcopy(p), lo=VAULT_Z + 1.6)
            north["id"], south["id"] = "annex_crypt_w_n", "annex_crypt_w_s"
            lintel = copy.deepcopy(p)
            lintel.update({"id": "annex_crypt_w_lintel", "uv_scale": [1.2, 0.5]})
            lintel["pos"] = [p["pos"][0], -1.8, VAULT_Z]
            lintel["scale"] = [p["scale"][0], p["pos"][1] + p["scale"][1] + 1.8, 3.2]
            props += [north, south, lintel]
            continue
        if pid in ("annex_dungeon_floor", "annex_dungeon_ceiling"):
            p = clip_z(p, hi=-1.6)
            p = clip_x(p, lo=65.4 if pid == "annex_dungeon_floor" else 64.6)
        props.append(p)

    # --- Vault III descent: crypt west wall -> two flights down (5.6 m) -> the Nursery landing.
    vz = VAULT_Z
    props += [
        box_prop("vault_threshold", COBBLE, 64.4, 65.4, -5.3, -4.8, vz - 1.6, vz + 1.6, uv=[0.5, 1.2], solid=False),
        {"id": "vault_stairs_upper", "model": STAIRS, "pos": [62.4, -7.6, vz], "rot_y": -90.0, "scale": [1.0, 1.4, 1.0],
         "solid": False, "ramp": "+x"},
        {"id": "vault_stairs_lower", "model": STAIRS, "pos": [58.4, -10.4, vz], "rot_y": -90.0, "scale": [1.0, 1.4, 1.0],
         "solid": False, "ramp": "+x"},
        box_prop("vault_tunnel_wall_n", WALL, 56.4, 64.6, -10.4, -1.4, vz + 1.55, vz + 1.85),
        box_prop("vault_tunnel_wall_s", WALL, 56.4, 64.6, -10.4, -1.4, vz - 1.85, vz - 1.55),
        box_prop("vault_tunnel_ceiling_upper", WALL, 60.4, 64.6, -1.8, -1.4, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_step", WALL, 60.25, 60.55, -4.6, -1.4, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_lower", WALL, 56.4, 60.4, -4.6, -4.2, vz - 1.85, vz + 1.85, solid=False),
        box_prop("vault_tunnel_ceiling_drop", WALL, 56.25, 56.55, -7.0, -4.2, vz - 1.85, vz + 1.85, solid=False),
        torch("torch_vault_stairs", 62.5, -4.9, vz + 1.45, 180.0, ghost=True),
    ]
    props += vault["props"]

    interactables = bell["interactables"] + road["interactables"] + annex["interactables"] + vault["interactables"]
    interactables.append({
        "instance_id": "flour_handprints", "type": "readable", "model": "", "pos": [65.75, -3.8, VAULT_Z + 2.3], "rot_y": 0.0,
        "prompt": "Look at the Marks on the Wall", "title": "Handprints in Old Flour",
        "text": ("Small handprints, a child's, pressed into the stone in old flour. They lead along the wall to a gap where the "
                 "masonry has been opened, and a stair going down: deeper than the Annex was ever built.\n\n"
                 "Someone has chalked beside them, in an archivist's neat hand: \"VAULT III. THE NURSERY. DO NOT WAKE.\""),
        "quest_id": "core:quest.vault_three", "set_stage": 0,
    })
    interactables.append({
        "instance_id": "landing_warning", "type": "readable", "model": "", "pos": [87.0, -3.8, 1.75], "rot_y": 0.0,
        "prompt": "Read the Scratches on the Wall", "title": "Scratched into the Stone",
        "text": ("Dozens of hands have cut the same words into the wall, over and over, in different scripts and different "
                 "centuries:\n\nTURN BACK. THE NAMES ARE LISTENING.\n\n"
                 "Beneath them, newer and neater, in Bureau ink: \"Graffiti is a Class III municipal offence.\""),
    })
    npcs = bell["npcs"] + road["npcs"] + annex["npcs"] + vault["npcs"]
    creatures = bell["creatures"] + road["creatures"] + annex["creatures"] + vault["creatures"]
    lights = bell["lights"] + road["lights"] + annex["lights"] + vault["lights"]
    spawns = {}
    for m in (bell, road, annex, vault):
        spawns.update(m["spawns"])

    for kind, items in (("interactable", interactables), ("npc", npcs), ("creature", creatures)):
        ids = [e["instance_id"] for e in items]
        dup = {i for i in ids if ids.count(i) > 1}
        if dup:
            raise SystemExit("duplicate %s ids: %s" % (kind, dup))
    pids = [p["id"] for p in props]
    dup = {i for i in pids if pids.count(i) > 1}
    if dup:
        raise SystemExit("duplicate prop ids: %s" % dup)

    bell_zone = zone_from(bell, "bellwether", [-21.0, -2.0, -21.0], [20.6, 40.0, 21.0], 4.0)
    # Signing the Seal of Names in Vault III ends seventeen years of rain over the village.
    bell_zone["flag_override"] = {"flag": "seal_renewed", "weather": "", "ambience": "assets/audio/ambience/forest_wind.wav"}
    seal_zone = zone_from(vault, "seal_chamber", [3.5, -17.0, -30.0], [21.0, -10.6, -14.0], 2.0)
    seal_zone.update({"display_name_key": "map.seal_chamber.name", "fog_density": 0.05, "ambient_color": [0.15, 0.19, 0.32]})
    zones = [
        seal_zone,
        zone_from(vault, "vault_three", [3.5, -17.0, -30.0], [57.0, -5.2, -14.0], 3.0),
        zone_from(annex, "annex", [59.0, -14.0, -46.0], [104.0, -0.9, 2.6], 3.0),
        zone_from(road, "old_road", [20.6, -0.9, -16.0], [77.0, 40.0, 16.0], 4.0),
        bell_zone,
    ]

    world = {
        "schema_version": 1,
        "id": "core:map.edrath",
        "display_name_key": "map.edrath.name",
        "music": bell["music"], "ambience": bell["ambience"],
        "sky_color": bell["sky_color"], "ambient_color": bell["ambient_color"], "sun_direction": bell["sun_direction"],
        "sun_color": bell["sun_color"], "fog_color": bell["fog_color"], "fog_density": bell["fog_density"],
        "weather": bell.get("weather", ""),
        "zones": zones,
        "spawns": spawns,
        "props": props,
        "lights": lights,
        "npcs": npcs,
        "creatures": creatures,
        "interactables": interactables,
        "portals": [],
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    print("Wrote %s: %d props, %d interactables, %d creatures, %d zones" % (os.path.relpath(OUT, ROOT), len(props), len(interactables),
                                                                           len(creatures), len(zones)))


if __name__ == "__main__":
    build()

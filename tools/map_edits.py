"""
Applies a level-change file (the Blender editor's diff) to a map, exactly like the game and the Blender add-on do.

Used by tools/build_world.py: it composes the regions into content/maps/edrath_world.base.json, then applies
content/maps/edrath_blender.json (the changes made in Blender) to write content/maps/edrath_world.json, the level the
game loads. So rebuilding the world never loses what was changed in Blender.
"""

KINDS = ("npcs", "creatures", "interactables", "portals")
IDKEY = {"npcs": "instance_id", "creatures": "instance_id", "interactables": "instance_id", "portals": "id"}


def apply_edits(world, edits, warn=None):
    pe = edits.get("props", {})
    ids = {p["id"] for p in world.get("props", [])}
    if warn:
        for pid in list(pe.get("remove", [])) + list(pe.get("modify", {})):
            if pid not in ids:
                warn(f"Blender change for prop '{pid}', which no longer exists")
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

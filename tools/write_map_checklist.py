#!/usr/bin/env python3
"""Writes docs/MAP_CHECKLIST.md from the built world (content/maps/edrath_world.json): for every area, the people,
the objects the story needs (KEEP) and the ones that are free to move, the monsters, and the arrival points; plus a
guide to adding new monster areas and dungeons. Rerun after rebuilding the world in Blender:

    python3 tools/write_map_checklist.py
"""
import glob
import json
import os
import re
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
J = lambda p: json.load(open(os.path.join(ROOT, p)))
W = J("content/maps/edrath_world.json")
L = J("content/localization/en.json")["strings"]
tr = lambda k: L.get(k, k)


def load(kind):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content", kind, "*.json"))):
        d = json.load(open(f))
        out += d.get(kind, [])
    return out


NPCS = {n["id"]: n for n in load("npcs")}
CREATURES = {c["id"]: c for c in load("creatures")}
QUESTS = J("content/quests/chapter_zero_quests.json")["quests"]
ITEMS = {i["id"]: i for i in load("items")}
item_name = lambda iid: tr(ITEMS[iid]["name_key"]) if iid in ITEMS else iid

# ---- what the story and the tests refer to
marker_of = defaultdict(set)
for q in QUESTS:
    for st in q["stages"]:
        for m in st.get("markers", []):
            marker_of[m].add(tr(q["title_key"]))
selftest = open(os.path.join(ROOT, "src/gameplay/SelfTest.cpp")).read()
tested = set(re.findall(r'"([a-z][a-z0-9_]+)"', selftest))
travel_targets = {i.get("travel_spawn") for i in W["interactables"] if i.get("travel_spawn")}
dlg = open(os.path.join(ROOT, "content/dialogue/chapter_zero_dialogue.json")).read()
travel_targets |= set(re.findall(r'"type": "travel",\s*"spawn": "([^"]+)"', dlg))
travel_targets.add(json.load(open(os.path.join(ROOT, "config/game.json"))).get("starting_spawn", "village_gate"))

# ---- areas
zones = sorted(W["zones"], key=lambda z: (z["box_max"][0] - z["box_min"][0]) * (z["box_max"][2] - z["box_min"][2]))
def area_of(p):
    for z in zones:
        a, b = z["box_min"], z["box_max"]
        if a[0] <= p[0] <= b[0] and a[1] - 2 <= p[1] <= b[1] + 2 and a[2] <= p[2] <= b[2]:
            return tr(z["display_name_key"])
    return "Bellwether Village"


def why(iid, extra=()):
    r = []
    if iid in marker_of: r.append("quest marker: " + ", ".join(sorted(marker_of[iid])))
    if iid in tested: r.append("used by the self-test")
    r += list(extra)
    return "; ".join(r)


def cond(o):
    c = []
    if o.get("requires_flag"): c.append(f"only after `{o['requires_flag']}`")
    if o.get("hidden_flag"): c.append(f"gone after `{o['hidden_flag']}`")
    return " (" + ", ".join(c) + ")" if c else ""


areas = defaultdict(lambda: {"npcs": [], "keep": [], "free": [], "creatures": [], "spawns": []})
for n in W["npcs"]:
    d = NPCS.get(n["npc_id"], {})
    areas[area_of(n["pos"])]["npcs"].append(f"**{tr(d.get('name_key', n['npc_id']))}** (`{n['instance_id']}`){cond(n)}")
STORY_TYPES = {"door", "lever", "pressure_plate", "quest_pedestal", "travel", "station"}
for i in W["interactables"]:
    iid, t = i["instance_id"], i["type"]
    label = i.get("title") or i.get("prompt") or (item_name(i["item_id"]) if i.get("item_id") else t)
    reasons = []
    if t in STORY_TYPES: reasons.append(t)
    if i.get("set_flag"): reasons.append(f"sets `{i['set_flag']}`")
    if i.get("quest_id"): reasons.append("advances a quest")
    if t == "chest": reasons.append("chest" + (" (fixed items)" if i.get("fixed_items") else ""))
    if t == "pickup": reasons.append("pickup")
    if i.get("travel_spawn"): reasons.append(f"travels to `{i['travel_spawn']}`")
    w = why(iid, reasons)
    line = f"`{iid}` — {label}{cond(i)}"
    if w or i.get("requires_flag") or i.get("hidden_flag"):
        areas[area_of(i["pos"])]["keep"].append(line + (f" — *{w}*" if w else ""))
    else:
        areas[area_of(i["pos"])]["free"].append(f"`{iid}` ({t}{': ' + label if t == 'readable' else ''})")
groups = defaultdict(list)
for c in W["creatures"]:
    groups[(area_of(c["pos"]), c["creature_id"], c.get("group", ""), c.get("requires_flag", ""))].append(c["instance_id"])
for (area, cid, group, req), ids in sorted(groups.items()):
    d = CREATURES.get(cid, {})
    name = tr(d.get("name_key", cid))
    notes = []
    if group: notes.append(f"group `{group}`")
    if req: notes.append(f"only after `{req}`")
    w = why(ids[0])
    if any(i in marker_of or i in tested for i in ids): notes.append("story/test: keep")
    areas[area]["creatures"].append(f"{len(ids)} × **{name}** (`{ids[0]}`{'…' if len(ids) > 1 else ''})" +
                                    (f" — {', '.join(notes)}" if notes else ""))
for sid, s in W["spawns"].items():
    keep = sid in travel_targets
    areas[area_of(s["pos"])]["spawns"].append(f"`{sid}`" + (" — *arrival point for a door, boat, dialogue or new game: keep*" if keep else ""))

order = ["Bellwether Village"] + [tr(z["display_name_key"]) for z in W["zones"] if tr(z["display_name_key"]) != "Bellwether Village"]
out = []
w = out.append
w("# Map checklist: what lives where, and what must survive a redesign\n")
w("Generated from the built world by `tools/write_map_checklist.py` (rerun it after you rebuild). Use it alongside "
  "`docs/LEVEL_EDITOR.md`, which explains the building rules (heights, stairs, doorways, collision).\n")
w("**The rule of thumb:** buildings, ground, walls, trees and decorations are entirely yours: delete, reshape, rebuild. "
  "Everything in **Uncounted Objects** (people, monsters, chests, doors, notes, levers, arrival points) can be **moved** "
  "freely onto your new floors; only the ones marked **keep** must not be **deleted**, because a quest, the journal "
  "markers or the self-test needs them. After a rebuild, `./game --validate` and the self-test tell you if anything the "
  "story needs went missing.\n")
w("Legend: `requires_flag` = appears only after that story moment; `hidden_flag` = disappears after it (both are "
  "automatic, you just place them once).\n")
for area in order:
    if area not in areas: continue
    a = areas[area]
    w(f"\n## {area}\n")
    if a["npcs"]:
        w("**People** (move freely; never delete):\n")
        for x in a["npcs"]: w(f"- {x}")
        w("")
    if a["keep"]:
        w("**Keep (move, don't delete):**\n")
        for x in a["keep"]: w(f"- {x}")
        w("")
    if a["creatures"]:
        w("**Monsters** (move freely; ones in a *group* or marked *keep* are part of a quest):\n")
        for x in a["creatures"]: w(f"- {x}")
        w("")
    if a["spawns"]:
        w("**Arrival points:** " + ", ".join(a["spawns"]) + "\n")
    if a["free"]:
        w(f"<details><summary>Free to move or delete ({len(a['free'])}): flavour notes, gathering spots, fishing spots</summary>\n")
        w(", ".join(a["free"]) + "\n")
        w("</details>\n")

# ---- adding new areas
w("\n## Adding new monster areas and dungeons\n")
w("Everything you need is in the Blender palette (**Uncounted Objects**): Shift+D a monster, chest, door, lever, torch "
  "or gathering spot and move it where you want it. A few tips:\n")
w("- **Monsters**: each one patrols between two points (its `patrol_a` / `patrol_b` fields) or stands guard if they're "
  "the same. Mix tougher ones deeper in. Rough difficulty below (health / damage per hit); the player starts with about "
  "75 health and reaches 150+ by the end of Chapter One.")
w("- **Chests**: set `loot_table` to one of the tables below (or add `fixed_items` for a guaranteed reward). Locked "
  "chests (`locked`) need lockpicks or a key (`key_item`).")
w("- **A dungeon's feel**: each area has a **zone** (its own music, ambience like the crypt drips, fog, light and the "
  "name banner when you enter). Zones aren't editable in Blender yet: tell me roughly where the new area is and the mood "
  "you want, and I'll add its zone (or extend an existing one).")
w("- **Doors between areas** use the `travel` type with a `travel_spawn` (an arrival point you place inside).")
w("- **Tell me what you built** (a sentence or a screenshot): I can write a quest, a boss, notes and loot to go with "
  "it, rebalance the monsters for the new length, and add your areas to the companions' comments (\"Smells like a "
  "tomb, 'cause it is one\").\n")
w("| Monster | Health | Damage | XP |")
w("|---|---|---|---|")
rows = []
for cid, c in CREATURES.items():
    st, at = c.get("stats", {}), c.get("attack", {})
    rows.append((st.get("health", 0), tr(c.get("name_key", cid)), cid, at.get("damage", 0), st.get("xp_reward", 0)))
for hp, name, cid, dmg, xp in sorted(rows):
    w(f"| {name} (`{cid.split('.')[-1]}`) | {hp} | {dmg} | {xp} |")
w("\n**Loot tables:** " + ", ".join(f"`{t['id']}`" for t in load("loot_tables")) + "\n")
open(os.path.join(ROOT, "docs", "MAP_CHECKLIST.md"), "w").write("\n".join(out) + "\n")
print("Wrote docs/MAP_CHECKLIST.md:", ", ".join(f"{a} ({len(areas[a]['keep'])} keep)" for a in order if a in areas))

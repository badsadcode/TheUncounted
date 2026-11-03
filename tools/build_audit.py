#!/usr/bin/env python3
"""
Generates content/regions/audit_chamber.json: the Audit Chamber, where the Royal Bureau audits your existence (a
challenge arena: ten waves, a Form per wave, a score and records; the engine runs it, see GameEngine "The Audit").
Reached from Clerk Oakhaven ("Request an audit", a travel action to spawn audit_entry); a door leads back to Bellwether.

Region-local frame (build_world.py places it at AUDIT_OFF): a hall x -15..15, z -15..15, the Auditor's desk on a dais
at the north end, the way out at the south. Spawns: audit_entry (south), audit_center (the arena's middle).
This file is generated: edit this script and rerun it, then rerun build_world.py.

Run:  python3 tools/build_audit.py
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "regions", "audit_chamber.json")
STONE = "assets/models/env/wall_stone.glb"
FLAGS = "assets/models/env/floor_flagstones.glb"
WOOD = "assets/models/env/floor_wood.glb"
CARPET = "assets/models/env/floor_carpet.glb"
TORCH = "assets/models/props/wall_torch.glb"
H = 8.0
props, lights, interactables, creatures, npcs = [], [], [], [], []


def box(pid, model, x0, x1, y0, y1, z0, z1, solid=True, uv=None):
    sx, sy, sz = x1 - x0, y1 - y0, z1 - z0
    props.append({"id": pid, "model": model, "pos": [round((x0 + x1) / 2, 3), round(y0, 3), round((z0 + z1) / 2, 3)],
                  "scale": [round(sx, 3), round(sy, 3), round(sz, 3)], "solid": solid,
                  "uv_scale": uv or [round(max(sx, sz) / 2.6, 2), round(max(sy, 0.3) / 3.0, 2)]})


def torch(tid, x, y, z, rot):
    props.append({"id": tid, "model": TORCH, "pos": [x, y, z], "rot_y": rot, "scale": [1, 1, 1], "solid": False})


box("floor", FLAGS, -15.0, 15.0, -0.4, 0.02, -15.0, 15.0, solid=False, uv=[10, 10])
box("ceiling", STONE, -15.5, 15.5, H, H + 0.5, -15.5, 15.5, uv=[10, 10])
box("wall_n", STONE, -15.5, 15.5, 0.0, H, -15.5, -15.0)
box("wall_s", STONE, -15.5, 15.5, 0.0, H, 15.0, 15.5)
box("wall_w", STONE, -15.5, -15.0, 0.0, H, -15.0, 15.0)
box("wall_e", STONE, 15.0, 15.5, 0.0, H, -15.0, 15.0)
for i, (x, z) in enumerate([(-7.0, -7.0), (7.0, -7.0), (-7.0, 7.0), (7.0, 7.0)]):
    box(f"pillar_{i}", STONE, x - 0.7, x + 0.7, 0.0, H, z - 0.7, z + 0.7, uv=[1, 2.6])
    torch(f"torch_pillar_{i}_a", x, 2.2, z + 0.72, 180.0)
    torch(f"torch_pillar_{i}_b", x, 2.2, z - 0.72, 0.0)
# the dais and the Auditor's desk
box("dais", WOOD, -5.0, 5.0, -0.4, 0.5, -15.0, -11.0, uv=[4, 2])
box("dais_step", WOOD, -3.0, 3.0, -0.4, 0.25, -11.0, -10.2, solid=False, uv=[2, 0.4])
box("auditor_desk", WOOD, -2.0, 2.0, 0.5, 1.5, -13.0, -12.2, uv=[1.6, 0.4])
npcs.append({"instance_id": "npc_auditor", "npc_id": "core:npc.auditor", "pos": [0.0, 0.5, -13.8], "yaw": 0.0})
# banners: forms pinned to the walls
for i, x in enumerate((-11.0, -4.0, 4.0, 11.0)):
    box(f"banner_{i}", "assets/models/env/wall_timber.glb", x - 1.0, x + 1.0, 3.0, 6.5, -14.98, -14.9, solid=False, uv=[0.6, 1])
interactables.append({"instance_id": "audit_rules", "type": "readable", "model": "", "pos": [6.0, 0.5, -12.0], "rot_y": 0.0,
                      "prompt": "Read the Notice", "title": "Notice to Persons Under Audit",
                      "text": "THE ROYAL BUREAU OF RECORDS\nAUDIT OF EXISTENCE\n\n1. You will be audited in ten stages.\n2. At each stage, a Form "
                              "applies. Forms are not optional. Forms are never optional.\n3. Persons who fall during an audit are not dead. "
                              "They are FAILED, which is worse, administratively.\n4. Successful persons receive a Certificate of Existence "
                              "(Audited) and the right to tell everyone about it.\n5. Records are kept. Of everything. Forever.\n\n"
                              "The Bureau thanks you for your continued existence."})
interactables.append({"instance_id": "audit_exit", "type": "travel", "model": "assets/models/props/oak_door.glb", "pos": [0.0, 0.0, 14.8],
                      "rot_y": 0.0, "prompt": "Leave the Audit Chamber", "travel_spawn": "from_audit"})
for i, (x, z) in enumerate([(0.0, 0.0), (-10.0, -10.0), (10.0, -10.0), (-10.0, 10.0), (10.0, 10.0)]):
    lights.append({"pos": [x, 5.5, z], "color": [1.0, 0.86, 0.62], "radius": 13.0})

region = {
    "schema_version": 1,
    "id": "core:map.audit_chamber",
    "display_name_key": "map.audit_chamber.name",
    "music": "assets/audio/music/old_road_theme.wav",
    "ambience": "assets/audio/ambience/crypt_drips.wav",
    "sky_color": [14, 12, 10],
    "ambient_color": [0.5, 0.46, 0.4],
    "sun_direction": [-0.3, 0.8, -0.3],
    "sun_color": [0.4, 0.36, 0.3],
    "fog_color": [0.08, 0.07, 0.06],
    "fog_density": 0.02,
    "weather": "",
    "spawns": {"audit_entry": {"pos": [0.0, 0.0, 12.5], "yaw_degrees": 180.0}, "audit_center": {"pos": [0.0, 0.0, 0.0], "yaw_degrees": 180.0}},
    "props": props, "lights": lights, "npcs": npcs, "creatures": creatures, "interactables": interactables, "portals": [],
}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(region, f, indent=2, ensure_ascii=False)
print("Wrote %s: %d props, %d interactables" % (os.path.relpath(OUT, ROOT), len(props), len(interactables)))

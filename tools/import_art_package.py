#!/usr/bin/env python3
"""
Import Noor's art package (the one described in docs/NOOR_ART_BRIEF.md) in one go.

    python3 tools/import_art_package.py PATH_TO_ZIP_OR_FOLDER            # dry run: what goes where, what's wrong/missing
    python3 tools/import_art_package.py PATH_TO_ZIP_OR_FOLDER --apply    # import

Folders it understands (anywhere in the zip, any letter case):
  portraits/      <race>_<calling>_<n>.png -> assets/ui/portraits/          (shown in the creation picker automatically)
  spell_icons/    <spell icon name>.png    -> assets/ui/spells/              (must match an existing icon's file name)
  item_icons/     <item icon name>.png     -> assets/ui/items/               (must match an existing icon's file name)
  spell_effects/  spell_*.png              -> assets/sprites/vfx/            (square frames in one row; alpha made hard)
  monsters/       lost_sentinel / animated_armor / headless_knight / repossession_golem 8x6 sheets:
                  the four monsters are switched from the shared 3D model to sprites, then imported with
                  tools/import_package.py like every other character sheet.
Originals are kept in art_source/<folder>/. Partial packages are fine: whatever is there is imported.
"""
import argparse
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECTIONS = ("portraits", "spell_icons", "item_icons", "spell_effects", "monsters")
MONSTERS = {  # sheet name -> (creature id, height in metres)
    "lost_sentinel": ("core:enemy.lost_sentinel", 2.2),
    "animated_armor": ("core:enemy.animated_armor", 1.95),
    "headless_knight": ("core:enemy.headless_knight", 1.85),
    "repossession_golem": ("core:enemy.repossession_golem", 2.6),
}
MONSTER_ALIASES = {"sentinel": "lost_sentinel", "armour": "animated_armor", "animated_armour": "animated_armor", "armor": "animated_armor",
                   "knight": "headless_knight", "headless": "headless_knight", "golem": "repossession_golem"}


def load(kind):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content", kind, "*.json"))):
        d = json.load(open(f))
        out += d.get(kind, []) if isinstance(d, dict) else d
    return out


def expected():
    races = [r["id"].split(".")[-1] for r in load("races")]
    callings = [a["id"].split(".")[-1] for a in load("archetypes")]
    spells, items = load("spells"), load("items")
    return {
        "portraits": {f"{r}_{c}_{n}.png" for r in races for c in callings for n in (1, 2)},
        "portrait_re": re.compile(r"^(%s)_(%s)_\d+\.png$" % ("|".join(races), "|".join(callings))),
        "spell_icons": {os.path.basename(s["icon"]) for s in spells if s.get("icon")},
        "item_icons": {os.path.basename(i["icon"]) for i in items if i.get("icon")},
        "spell_effects": {os.path.basename(s["effect"]["projectile_sprite"]) for s in spells
                          if s.get("effect", {}).get("projectile_sprite")},
    }


def section_of(path):
    for part in reversed(path.replace("\\", "/").lower().split("/")[:-1]):
        p = part.replace(" ", "_").replace("-", "_")
        for s in SECTIONS:
            if p == s or p.rstrip("s") == s.rstrip("s"):
                return s
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("package")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    from PIL import Image

    tmp = None
    src = args.package
    if zipfile.is_zipfile(src):
        tmp = tempfile.mkdtemp(prefix="artpkg_")
        with zipfile.ZipFile(src) as z:
            z.extractall(tmp)
        src = tmp
    exp = expected()
    found = {s: [] for s in SECTIONS}
    unknown = []
    for root, _, files in os.walk(src):
        for f in sorted(files):
            if not f.lower().endswith(".png") or ".tmp." in f.lower() or f.startswith("."):
                continue
            path = os.path.join(root, f)
            sec = section_of(os.path.relpath(path, src))
            (found[sec] if sec else unknown).append(path)

    problems, plan = [], []          # plan: (section, source, destination, fix)
    for path in found["portraits"]:
        name = os.path.basename(path).lower()
        if not exp["portrait_re"].match(name):
            problems.append(f"portraits/{os.path.basename(path)}: name should be <race>_<calling>_<n>.png")
            continue
        w, h = Image.open(path).size
        fix = None
        if w != h:
            problems.append(f"portraits/{name}: {w}x{h}, not square (it will be squashed)")
        if (w, h) != (128, 128):
            fix = "resize128"
        plan.append(("portraits", path, f"assets/ui/portraits/{name}", fix))
    for sec, dest in (("spell_icons", "assets/ui/spells"), ("item_icons", "assets/ui/items")):
        for path in found[sec]:
            name = os.path.basename(path).lower()
            if name not in exp[sec]:
                problems.append(f"{sec}/{os.path.basename(path)}: no {sec.replace('_', ' ')[:-1]} has this file name")
                continue
            w, h = Image.open(path).size
            if w != h:
                problems.append(f"{sec}/{name}: {w}x{h}, not square")
            plan.append((sec, path, f"{dest}/{name}", None))
    for path in found["spell_effects"]:
        name = os.path.basename(path).lower()
        if name not in exp["spell_effects"]:
            problems.append(f"spell_effects/{os.path.basename(path)}: no spell uses this file name")
            continue
        w, h = Image.open(path).size
        if w % h:
            problems.append(f"spell_effects/{name}: {w}x{h} isn't a row of square frames")
            continue
        plan.append(("spell_effects", path, f"assets/sprites/vfx/{name}", "hard_alpha"))
    monsters = []
    for path in found["monsters"]:
        stem = re.sub(r"[^a-z0-9]+", "_", os.path.basename(path).lower().rsplit(".", 1)[0]).strip("_")
        key = stem if stem in MONSTERS else next((v for k, v in MONSTER_ALIASES.items() if k in stem.split("_")), None)
        if key is None:
            problems.append(f"monsters/{os.path.basename(path)}: not one of {', '.join(MONSTERS)}")
            continue
        monsters.append((key, path))

    print(f"Found: " + ", ".join(f"{len(found[s])} {s.replace('_', ' ')}" for s in SECTIONS) +
          (f", {len(unknown)} outside the known folders" if unknown else ""))
    for s in ("portraits", "spell_icons", "item_icons", "spell_effects"):
        done = {os.path.basename(d) for sec, _, d, _ in plan if sec == s}
        todo = sorted(exp[s] - done) if s != "portraits" else sorted(n for n in exp[s] if n not in done)
        print(f"  {s}: importing {len(done)}; still to come {len(todo)}" + (f" (e.g. {', '.join(todo[:4])})" if todo else ""))
    print(f"  monsters: importing {len(monsters)}: {', '.join(k for k, _ in monsters) or '-'}")
    for p in problems:
        print("  ! " + p)
    for p in unknown:
        print("  ? skipped (not in a known folder): " + os.path.relpath(p, src))
    if not args.apply:
        print("\nDry run. Add --apply to import.")
        return

    for sec, path, dest, fix in plan:
        keep = os.path.join(ROOT, "art_source", sec, os.path.basename(dest))
        os.makedirs(os.path.dirname(keep), exist_ok=True)
        shutil.copyfile(path, keep)
        im = Image.open(path).convert("RGBA")
        if fix == "resize128":
            im = im.resize((128, 128), Image.LANCZOS if im.width > 128 else Image.NEAREST)
        if fix == "hard_alpha":
            a = im.getchannel("A").point(lambda v: 255 if v >= 128 else 0)
            im.putalpha(a)
            if a.histogram()[255] < 0.02 * im.width * im.height:
                print(f"  ! {dest}: almost nothing is left once see-through pixels are dropped (the game shows only "
                      "pixels over 50% opacity). Ask for a version with solid pixels.")
        os.makedirs(os.path.dirname(os.path.join(ROOT, dest)), exist_ok=True)
        im.save(os.path.join(ROOT, dest))
    if monsters:
        cpath = os.path.join(ROOT, "content/creatures/core_creatures.json")
        data = json.load(open(cpath))
        mdir = tempfile.mkdtemp(prefix="monsters_")
        for key, path in monsters:
            cid, height = MONSTERS[key]
            for c in data["creatures"]:
                if c["id"] == cid and c["appearance"].get("type") != "sprite_8dir":
                    c["appearance"] = {"type": "sprite_8dir", "sprite_sheet": f"assets/sprites/enemies/{key}.png",
                                       "animation_data": "assets/animations/npc_standard_128.json", "scale": height}
            shutil.copyfile(path, os.path.join(mdir, key + os.path.splitext(path)[1]))
        json.dump(data, open(cpath, "w"), indent=2, ensure_ascii=False)
        open(cpath, "a").write("\n")
        subprocess.run([sys.executable, os.path.join(ROOT, "tools/import_package.py"), mdir, "--apply",
                        "--report", os.path.join(ROOT, "import_report_monsters.png")], check=False)
        shutil.rmtree(mdir, ignore_errors=True)
    print(f"\nImported {len(plan)} images and {len(monsters)} monster sheet(s). Originals are in art_source/. "
          "Run ./game --validate, then rerun tools/write_art_brief.py to refresh the brief.")
    if tmp:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

"""Writes docs/NOOR_ART_BRIEF.md (everything still needing Noor's art) from the game's own data, so names and descriptions
always match the game. Rerun after adding items or spells: python3 tools/write_art_brief.py"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
loc = json.load(open(os.path.join(ROOT, "content/localization/en.json")))
loc = loc.get("strings", loc)


def load(kind):
    out = []
    for f in sorted(glob.glob(os.path.join(ROOT, "content", kind, "*.json"))):
        d = json.load(open(f))
        out += d.get(kind, []) if isinstance(d, dict) else d
    return out


def short(i):
    return i.split(".")[-1]


def tr(k):
    return " ".join(loc.get(k, "").split())


races, callings = load("races"), load("archetypes")
spells, items = load("spells"), load("items")
out = []
w = out.append
w("# Art brief for Noor: everything that still needs painting\n")
w("Thank you for all the characters, textures and skies! This is the rest of the game's art, in order of how much it "
  "shows during play. Everything is placeholder art right now, so any part you deliver goes straight in.\n")
w("**Delivery**: a zip with one folder per section (`portraits/`, `monsters/`, `spell_effects/`, `spell_icons/`, "
  "`item_icons/`), files named exactly as listed. Partial deliveries are welcome.\n")
w("**Everywhere**: the same painted pixel-art style as the character sheets; PNG; sizes exact.\n")

w("\n## 1. Character portraits (character creation) — %d portraits\n" % (len(races) * len(callings) * 2))
w("Toasty picks one when creating the character (it's cosmetic; the character is never seen in the game, only here and "
  "on the character sheet). **Two per race per calling**, ideally one woman and one man, with varied ages and looks "
  "within each race, so there's lots to choose from.\n")
w("- **Size**: 128 × 128 px, square, opaque (a dark painted background is fine, no transparency needed).")
w("- **Framing**: head and shoulders, facing the viewer or slightly turned, like an RPG party portrait. Shown at about "
  "96 px, so keep faces bold and readable.")
w("- **The calling shows** in clothing and gear: armour and a sword hilt for a warrior, a hood and bow for a ranger, "
  "robes and a glowing hand or staff for a mage, leathers and a dagger for a rogue, vestments and a holy symbol for a "
  "cleric, practical mixed travelling gear for an adventurer.")
w("- **The world**: Edrath, a gloomy, slightly absurd fantasy of bureaucrats and the 'officially dead'. Muted colours, "
  "candlelight, a bit of humour in the faces is welcome.")
w("- **Names**: `<race>_<calling>_<1 or 2>.png`, e.g. `human_warrior_1.png`, `orc_mage_2.png`.\n")
w("| Race | What they're like |")
w("|---|---|")
for r in races:
    w(f"| `{short(r['id'])}` — {tr(r['name_key'])} | {tr(r['description_key'])} |")
w("")
w("Callings: " + ", ".join(f"`{short(a['id'])}` ({tr(a['name_key'])})" for a in callings) + ".\n")
w(f"That's {len(races)} races × {len(callings)} callings × 2 = {len(races) * len(callings) * 2} files, from "
  f"`{short(races[0]['id'])}_{short(callings[0]['id'])}_1.png` to `{short(races[-1]['id'])}_{short(callings[-1]['id'])}_2.png`. "
  "More than two of a kind (`_3`, `_4`...) also work, and fewer is fine: whatever exists shows up.\n")

w("\n## 2. Four monsters that need their own sprite sheets\n")
w("Right now all four share one plain 3D model. Same 8 × 6 sheet layout and rules as all the other characters "
  "(see `docs/CHARACTER_SPRITES.md`: 8 directions × idle, walk A, walk B, windup, attack, stagger/corpse).\n")
w("| File | Who | Look |")
w("|---|---|---|")
w("| `lost_sentinel.png` | Lost Sentinel | Ancient Bureau guardian of stone and rusted iron, tall and heavy, a halberd or great "
  "seal-hammer, a faded official crest on its chest. Slow, patient, still guarding a door nobody remembers. |")
w("| `animated_armor.png` | Animated Armour | An empty, polished suit of manor armour (Hollowmere), nothing inside — you "
  "can see darkness through the visor slits. Carries a guest list on a clipboard and a sword. Prim and officious. |")
w("| `headless_knight.png` | The Headless Knight of the Old Road | Comedy: it's obviously Steve (the level-one bandit "
  "from your Steve sheet) in ill-fitting, mismatched armour, the helmet pulled down over his head, holding a hat on a "
  "stick above it to look 'headless'; his patched leathers and too-big hood poke out. Proudly dramatic poses. |")
w("| `repossession_golem.png` | The Repossession Golem | A big, blocky iron golem stamped REPOSSESSED all over in red, "
  "riveted plates, glowing furnace eyes, bought with a dragon's money. Bigger than a person (about 2.3 m). |")

w("\n## 3. Spell effects in flight — 5 animated strips\n")
w("The ball you see flying when a spell is cast. Currently plain coloured circles.\n")
w("- **Layout**: one row of **square frames**, 4 to 8 frames, **64 × 64 px** each (e.g. 6 frames = 384 × 64). Loops at "
  "14 frames per second; it's shown about half a metre across.")
w("- **Hard edges only**: pixels fully opaque or fully transparent (the game drops anything under 50 % opacity). Do "
  "glow with colour, not transparency. Drawn at full brightness, centred in the frame, always facing the camera.\n")
w("| File | Used by | Look |")
w("|---|---|---|")
by_sprite = {}
for s in spells:
    ps = s.get("effect", {}).get("projectile_sprite")
    if ps:
        by_sprite.setdefault(os.path.basename(ps), []).append(tr(s["name_key"]))
looks = {"spell_ember.png": "a tumbling ball of flame with sparks", "spell_frost.png": "a spinning shard of ice with frosty mist",
         "spell_arcane.png": "a pulsing violet orb with orbiting runes", "spell_ink.png": "a splattering glob of black ink with drips",
         "spell_sabrino.png": "Sabrino the witch's signature hex: a green-purple swirl with a tiny grinning face"}
for f, names in sorted(by_sprite.items()):
    w(f"| `{f}` | {', '.join(names)} | {looks.get(f, '')} |")

w("\n## 4. Spell icons — %d icons\n" % len(spells))
w("Shown in the spell bar and spellbook, all the time. **64 × 64 px**, opaque square (dark background), a clear symbol "
  "of the spell, readable at 32 px. A coloured border per school is welcome (fire orange, frost blue, restoration "
  "green, arcane violet...).\n")
w("| File | Spell | What it does |")
w("|---|---|---|")
for s in sorted(spells, key=lambda s: s["icon"]):
    w(f"| `{os.path.basename(s['icon'])}` | {tr(s['name_key'])} | {tr(s['description_key'])} |")

w("\n## 5. Item icons — %d icons (a big set: any part helps)\n" % len(items))
w("Shown in the inventory, shop and loot windows. **64 × 64 px**, transparent background, the object on its own, "
  "slightly angled, readable at 32 px. Grouped by kind below; the description is what the game says about it.\n")
cats = {}
for i in items:
    cats.setdefault(i.get("category", "misc"), []).append(i)
for cat in ("weapon", "armor", "accessory", "consumable", "ammo", "book", "key", "misc"):
    if cat not in cats:
        continue
    w(f"\n### {cat.title()} ({len(cats[cat])})\n")
    w("| File | Item | Description |")
    w("|---|---|---|")
    for i in sorted(cats[cat], key=lambda i: i["icon"]):
        d = tr(i.get("description_key", ""))
        w(f"| `{os.path.basename(i['icon'])}` | {tr(i['name_key'])} | {d[:220] + ('…' if len(d) > 220 else '')} |")

w("\n## 6. Fire for fireplaces\n")
w("Already described in `docs/FIRE_SPRITE_BRIEF.md`.\n")
open(os.path.join(ROOT, "docs", "NOOR_ART_BRIEF.md"), "w").write("\n".join(out) + "\n")
print("Wrote docs/NOOR_ART_BRIEF.md:", len(items), "items,", len(spells), "spells")

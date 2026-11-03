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
  "`item_icons/`, `characters/` for Chapter One's people, `skies/`), files named exactly as listed. Partial deliveries are welcome.\n")
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

w("\n## 2b. Chapter One: the people of Here (and the Auditor) — 11 sprite sheets\n")
w("A city struck off every map 400 years ago; its people have forgotten their own names and go by descriptions. Same 8 × 6 "
  "layout as the other characters. The residents are slightly faded, like a memory (soft, pale edges are fine: the game "
  "keeps them a little see-through itself). Simple placeholders are in the game until yours arrive.\n")
w("| File | Who | Look |")
w("|---|---|---|")
for f, who, look in [
    ("here_gatekeeper.png", "Ottoline Pell, Gatekeeper", "A very upright woman in a faded blue customs uniform and cap, a big rubber stamp in one hand and a form in the other. Four hundred years of patience; tearfully delighted to finally have a visitor."),
    ("here_baker.png", "The Baker, Probably", "A floury baker in a white apron and a hair bun, flour on their face and arms, forever kneading dough that isn't there."),
    ("here_butt_butt.png", "Butt-Butt", "A small, loud child (about 1.15 m) with messy ginger hair, a stub of chalk, chalk dust everywhere, an orange jumper, enormous grin. Picked their own name: Butt-Butt. Toasty's character!"),
    ("here_cartographer.png", "The Cartographer (Retired)", "An elderly mapmaker with white hair and beard, a much-mended brown coat, a battered hat, maps rolled under one arm."),
    ("here_person_in_hat.png", "Person in a Hat", "Someone in a VERY tall, slightly bent hat (the most important part), a purple coat, dignified and vague."),
    ("here_night_merchant.png", "The Night Merchant", "A tall, thin, hooded figure in deep night-blue, glowing pale eyes, a staff hung with little lanterns of different colours."),
    ("here_inspector.png", "Inspector Aldric Thrupp (ghost)", "A grey, upright ghost tax inspector in a tall collar and a battered hat, a tin badge, holding a ledger full of holes; faint and see-through, counting chimneys on his fingers."),
    ("here_echo.png", "The Last Archivist", "A ghostly archivist made of almost nothing: robes, spectacles, ink-stained fingers, an open ledger; floats slightly, faintly glowing."),
    ("auditor.png", "Prudence Vell, Senior Auditor of Existence (the Audit)", "A severe Bureau official in a black coat with silver buttons, hair in a tight bun, a pen behind each ear and one in her hand, a red ledger. Not unkind; extremely thorough."),
    ("here_mouth.png", "Mouth of the Hunger (monster)", "A floating mouth with no face: a dark, papery shape like a torn page, a ring of teeth, faint pale glow. Hunts by hearing names."),
    ("here_unsaying.png", "The Unsaying (boss)", "Big (about 2.8 m), made of the gaps between words: a tall dark silhouette full of torn paper, crossed-out letters drifting off it, a pale glowing hollow where a face would be."),
]:
    w(f"| `{f}` | {who} | {look} |")

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

w("\n## 6. A daytime sky\n")
w("The game now has day and night. Your night and dusk horizons are used at night and at dawn/dusk; daytime needs a "
  "third one in the same format: `sky_day.png`, **1024 × 256 px**, a 360° strip that repeats left to right, opaque. "
  "An overcast, slightly melancholy day (it's Edrath): pale grey-blue sky, soft white-grey clouds, the same distant hills "
  "and pine line along the bottom as the other two so they cross-fade smoothly. Deliver it in a `skies/` folder (a "
  "placeholder made from your night sky is in the game until then).\n")
w("\n## Done, thank you!\n")
w("Fire (main, small and magic: in the game since 3 Nov), all 62 characters, the world textures, skies and ground "
  "scatter.\n")
open(os.path.join(ROOT, "docs", "NOOR_ART_BRIEF.md"), "w").write("\n".join(out) + "\n")
print("Wrote docs/NOOR_ART_BRIEF.md:", len(items), "items,", len(spells), "spells")

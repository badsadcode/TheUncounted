"""Writes Noor's art brief from the game's own data, so names and descriptions always match the game.

    python3 tools/write_art_brief.py              # docs/NOOR_ART_BRIEF.md: the full brief
    python3 tools/write_art_brief.py --remaining  # docs/NOOR_REMAINING_ART.md: only what hasn't been delivered, self-contained

Delivered = Noor's original is in art_source/ (the importers keep every original there). Rerun after imports."""
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


import sys

REMAINING = "--remaining" in sys.argv  # write only what's still missing (a self-contained brief for a fresh start)
SRC = os.path.join(ROOT, "art_source")


def delivered(section, fname):
    """Noor's originals are kept in art_source/ by the importers, so that's the record of what has arrived."""
    stem = os.path.splitext(os.path.basename(fname))[0]
    if section in ("characters", "monsters"):
        d = os.path.join(SRC, "spritesheets")
        return os.path.isdir(d) and any(os.path.splitext(f)[0] == stem for f in os.listdir(d))
    if section == "portraits":
        return os.path.exists(os.path.join(ROOT, "assets", "ui", "portraits", os.path.basename(fname)))
    return os.path.exists(os.path.join(SRC, section, os.path.basename(fname)))


def rows(section, entries, key=lambda e: e[0]):
    return [e for e in entries if not (REMAINING and delivered(section, key(e)))]


races, callings = load("races"), load("archetypes")
spells, items = load("spells"), load("items")
out = []
w = out.append
counts = {}

MONSTERS = [
    ("lost_sentinel.png", "Lost Sentinel", "Ancient Bureau guardian of stone and rusted iron, tall and heavy, a halberd or great seal-hammer, a faded official crest on its chest. Slow, patient, still guarding a door nobody remembers."),
    ("animated_armor.png", "Animated Armour", "An empty, polished suit of manor armour (Hollowmere), nothing inside — you can see darkness through the visor slits. Carries a guest list on a clipboard and a sword. Prim and officious."),
    ("headless_knight.png", "The Headless Knight of the Old Road", "Comedy: it's obviously Steve (the level-one bandit) in ill-fitting, mismatched armour, the helmet pulled down over his head, holding a hat on a stick above it to look 'headless'; his patched leathers and too-big hood poke out. Proudly dramatic poses."),
    ("repossession_golem.png", "The Repossession Golem", "A big, blocky iron golem stamped REPOSSESSED all over in red, riveted plates, glowing furnace eyes, bought with a dragon's money. Bigger than a person (about 2.3 m)."),
]
CHAPTER_ONE = [
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
]
FRIENDS = [
    ("friend_eranu.png", "Eranu, Shieldmaiden of the Glens", "A tall, broad-shouldered Scottish warrior woman: long blonde braid, green tartan kilt, blue-grey tunic, round wooden targe (shield) and a sword. Brave and clever; confident, a little amused. She."),
    ("friend_coth.png", "Coth (Cothfotmeoo)", "Looks like a castaway lost for a thousand years: skinny, scruffy, long dark hair down his back, a long heavy black beard to his belt, a ragged tunic, and NO TROUSERS (bare legs, bare feet; plain undershorts). Carries a sword. Cheerful, slightly unhinged. He."),
    ("friend_dunstan.png", "Dunstan, Nearly a Squire", "A keen young warrior in polished mail and a red cloak, short brown hair, with an absurdly huge sword (taller than he is, broad as a door) that he drags point-down because he can barely lift it. A round mate gourd with a silver straw (bombilla) hangs at his hip: he's from Uruguay. Sunny, eager, a bit homesick. He."),
]
SPELL_LOOKS = {"spell_ember.png": "a tumbling ball of flame with sparks", "spell_frost.png": "a spinning shard of ice with frosty mist",
               "spell_arcane.png": "a pulsing violet orb with orbiting runes", "spell_ink.png": "a splattering glob of black ink with drips",
               "spell_sabrino.png": "Sabrino the witch's signature hex: a green-purple swirl with a tiny grinning face"}
REVISED = {"characters/friend_dunstan.png", "item_icons/ransom_note.png"}  # redone by Noor on 5 Nov
REVISIONS = [("characters/friend_dunstan.png", "Body larger in the frame (about the same height as Eranu's and Coth's), the huge "
                                              "sword held diagonally so it fits, clearer wind-up and attack poses. Keep the mate gourd and red cloak."),
             ("item_icons/ransom_note.png", "Currently a bound notebook. Should be a loose sheet of paper with charcoal scribbles (a crossed-out ransom "
                                            "note) and a faint grid showing through from the back.")]

# ---------------------------------------------------------------- header
if REMAINING:
    w("# The Uncounted: art still needed (for Noor)\n")
    w("**The Uncounted** is a first-person fantasy RPG made as a gift for a streamer friend, Toasty: low-poly 3D places and "
      "hand-painted 2D pixel-art characters that turn to face the camera, like classic 90s games. The tone is cosy-spooky "
      "comedy: a bureaucratic afterlife (the hero has been declared legally dead), a haunted manor, a fishing town with a "
      "cult, a city whose name was eaten. Muted, earthy colours with candlelight; gentle humour in faces and objects.\n")
    w("Everything listed here is **still missing**: the game runs with simple placeholders until each file arrives, and "
      "anything delivered goes straight in. Partial deliveries are very welcome. Already delivered (thank you!): every character sheet, all 60 portraits, the spell effects and icons, "
      "the world textures, skies and fire, and most of the item icons.\n")
    w("**Delivery**: a zip with one folder per section (`characters/`, `spell_icons/`, `item_icons/`, `revisions/` ...), "
      "files named exactly as listed. **Style**: the same painted pixel-art style as the earlier characters and icons; PNG; "
      "sizes exact.\n")
    w("**Suggested order**: top to bottom (things seen most often come first).\n")
else:
    w("# Art brief for Noor: everything that still needs painting\n")
    w("Thank you for all the characters, textures and skies! This is the rest of the game's art, in order of how much it "
      "shows during play. Everything is placeholder art right now, so any part you deliver goes straight in.\n")
    w("**Delivery**: a zip with one folder per section (`portraits/`, `monsters/`, `spell_effects/`, `spell_icons/`, "
      "`item_icons/`, `characters/` for Chapter One's people, `skies/`), files named exactly as listed. Partial deliveries are welcome.\n")
    w("**Everywhere**: the same painted pixel-art style as the character sheets; PNG; sizes exact.\n")
    w("(A shorter list with only what's still missing: `docs/NOOR_REMAINING_ART.md`.)\n")

SHEET_RULES = (
    "**Sheet layout (all characters):** one PNG per character, **8 columns × 6 rows**, every cell the same size (128–256 px "
    "square; earlier sheets used 192 px cells), on a flat **pure black** background.\n"
    "- **Columns = facing**: 0 front, 1 front three-quarter (body towards screen-left), 2 profile facing screen-left, "
    "3 back three-quarter, 4 back, 5 back three-quarter (other side), 6 profile facing screen-right, 7 front three-quarter "
    "(towards screen-right).\n"
    "- **Rows**: 0 idle, 1 walk A (left leg forward), 2 walk B (right leg forward), 3 wind-up (weapon raised, or a hand to "
    "the head for talkers), 4 attack / gesture, 5 columns 0–3 hit-recoil (front, left profile, back, right profile) and "
    "columns 4–7 lying on the ground (side-on, inside the cell).\n"
    "- Same scale and the same ground line (feet about 92 % down the cell) in every frame; nothing crosses into a "
    "neighbouring cell; one character per sheet, same outfit and props in every frame; about a 3/4 top-down view, lit "
    "from the upper left. Glowing bits (eyes, orbs) look great: the game adds bloom.\n")

# ---------------------------------------------------------------- 1. portraits
todo = [f"{short(r['id'])}_{short(c['id'])}_{n}.png" for r in races for c in callings for n in (1, 2)
        if not delivered("portraits", f"{short(r['id'])}_{short(c['id'])}_{n}.png")]
if not REMAINING or todo:
    w("\n## Character portraits (character creation) — %d portraits\n" % (len(races) * len(callings) * 2))
    w("Toasty picks one when creating the character. **Two per race per calling**: `_1` a woman, `_2` a man. 128 × 128 px, "
      "opaque, head and shoulders; the calling shows in clothing and gear. Names `<race>_<calling>_<1 or 2>.png`.\n")
    w(f"**Delivered: {len(races) * len(callings) * 2 - len(todo)}. Still to come: {len(todo)}**" +
      (": " + ", ".join(f"`{t}`" for t in todo) if todo else " (all done!)") + ".\n")
    counts["portraits"] = len(todo)


def char_table(title, intro, entries, section="characters"):
    left = rows(section, entries)
    counts[title] = len(left)
    if not left:
        return
    w(f"\n## {title} — {len(left)} sprite sheet{'s' if len(left) != 1 else ''}\n")
    w(intro + "\n")
    w("| File | Who | Look |")
    w("|---|---|---|")
    for f, who, look in left:
        w(f"| `{f}` | {who} | {look} |")


if REMAINING and (rows("monsters", MONSTERS) or rows("characters", CHAPTER_ONE + FRIENDS)):
    w("\n## How character sheets work\n")
    w(SHEET_RULES)
char_table("Four monsters", "Same 8 × 6 layout as every character" + ("" if REMAINING else " (see `docs/CHARACTER_SPRITES.md`)") + ".",
           MONSTERS, "monsters")
char_table("Chapter One: the people of Here (and the Auditor)",
           "A city struck off every map 400 years ago; its people have forgotten their own names and go by descriptions. The "
           "residents are slightly faded, like a memory (soft, pale edges are fine: the game keeps them a little see-through "
           "itself). Deliver in `characters/`.", CHAPTER_ONE)
char_table("More Bellwether folk",
           "New faces in the village. Deliver in `characters/`.",
           [("old_tobble.png", "Old Tobble, Teller of Tales (Unverified)",
             "An old storyteller who leans on the village well: long, patched, grubby brown robes, grey hair mostly gone on top "
             "(a balding crown with a grey fringe), a scruffy grey beard, kind crinkled eyes, a slight stoop, hands that wave "
             "while he talks. Cheerful and harmless; tells stories that go nowhere. He.")])
char_table("Friends from Toasty's streams",
           "Real friends of Toasty's, as characters (two can join the party). Deliver in `characters/`.", FRIENDS)

# ---------------------------------------------------------------- spell effects
by_sprite = {}
for s in spells:
    ps = s.get("effect", {}).get("projectile_sprite")
    if ps:
        by_sprite.setdefault(os.path.basename(ps), []).append(tr(s["name_key"]))
fx = rows("spell_effects", sorted(by_sprite.items()))
counts["spell effects"] = len(fx)
if fx:
    w(f"\n## Spell effects in flight — {len(fx)} animated strips\n")
    w("One row of **square 64 × 64 frames**, 4 to 8 frames (e.g. 6 frames = 384 × 64), loops at 14 fps. Pixels fully opaque "
      "or fully transparent; glow with colour, not transparency.\n")
    w("| File | Used by | Look |")
    w("|---|---|---|")
    for f, names in fx:
        w(f"| `{f}` | {', '.join(names)} | {SPELL_LOOKS.get(f, '')} |")

# ---------------------------------------------------------------- spell icons
si = rows("spell_icons", sorted(spells, key=lambda s: s["icon"]), key=lambda s: s["icon"])
counts["spell icons"] = len(si)
if si:
    w(f"\n## Spell icons — {len(si)} icon{'s' if len(si) != 1 else ''}\n")
    w("Shown in the spell bar and spellbook. **64 × 64 px**, opaque square (dark background), a clear symbol of the spell, "
      "readable at 32 px, a coloured border per school (fire orange, frost blue, restoration green, arcane violet...), "
      "matching the delivered ones.\n")
    w("| File | Spell | What it does |")
    w("|---|---|---|")
    for s in si:
        w(f"| `{os.path.basename(s['icon'])}` | {tr(s['name_key'])} | {tr(s['description_key'])} |")

# ---------------------------------------------------------------- item icons (one row per file; shared icons listed once)
by_icon = {}
for i in items:
    by_icon.setdefault(os.path.basename(i["icon"]), []).append(i)
ii = rows("item_icons", sorted(by_icon.items()))
counts["item icons"] = len(ii)
if ii:
    w(f"\n## Item icons — {len(ii)} icons\n")
    w("Shown in the inventory, shop and loot windows. **64 × 64 px**, transparent background, the object on its own, "
      "slightly angled, readable at 32 px, matching the delivered ones. Grouped by kind; the description is what the game "
      "says about it.\n")
    cats = {}
    for f, its in ii:
        cats.setdefault(its[0].get("category", "misc"), []).append((f, its))
    for cat in ("weapon", "armor", "accessory", "consumable", "ammo", "book", "key", "material", "misc") + tuple(c for c in cats if c not in (
            "weapon", "armor", "accessory", "consumable", "ammo", "book", "key", "material", "misc")):
        if cat not in cats:
            continue
        w(f"\n### {cat.title()} ({len(cats[cat])})\n")
        w("| File | Item | Description |")
        w("|---|---|---|")
        for f, its in cats[cat]:
            d = tr(its[0].get("description_key", ""))
            names = " / ".join(tr(i["name_key"]) for i in its)
            w(f"| `{f}` | {names} | {d[:220] + ('…' if len(d) > 220 else '')} |")

# ---------------------------------------------------------------- sky
if not (REMAINING and delivered("skies", "sky_day.png")):
    counts["sky"] = 1
    w("\n## A daytime sky\n")
    w("`sky_day.png`, **1024 × 256 px**, a 360° strip that repeats left to right, opaque: an overcast, slightly melancholy "
      "day, the same distant hills and pine line as the night and dusk skies. Deliver in `skies/`.\n")

# ---------------------------------------------------------------- the illustrated intro
INTRO = [
    ("intro_1.png", "Edrath, in the four hundred and twelfth year after the Great Silence. The kingdoms keep their ledgers carefully now. "
                    "What is written down, exists. What is struck out was never there at all.",
     "A vast, candlelit hall of the Royal Bureau of Records: endless desks and shelves of enormous ledgers fading into the "
     "dark, clerks in grey robes bent over them with quills, a great open ledger in front. Awe and dust."),
    ("intro_2.png", "Seventeen years ago, by order of the Royal Bureau of Records, you died. You do not remember it. Nobody does.",
     "Close on a ledger page: a quill drawing a firm line of ink through one name among hundreds; a red wax seal beside it; "
     "a single candle. The name itself unreadable."),
    ("intro_3.png", "This morning a notice arrived anyway, sealed in Bureau wax: proof of your death, and a bill for your burial.",
     "A plain table by a rainy window at dawn: a folded letter with a big red Bureau wax seal, a cup of tea going cold, a "
     "traveller's hand reaching for it (no face)."),
    ("intro_4.png", "So you have walked to Bellwether, where the rain never quite stops, to argue with a clerk about whether you are alive.",
     "A lone hooded traveller seen from behind on a muddy road in the rain, walking towards a small walled village with "
     "warm windows and a stone gate, at dusk. (The title painting is a good mood reference.)"),
]
intro_left = rows("intro", INTRO)
counts["intro"] = len(intro_left)
if intro_left:
    w(f"\n## The illustrated intro — {len(intro_left)} painting{'s' if len(intro_left) != 1 else ''}\n")
    w("A new game opens with a few still pictures, a line of text along the bottom and (soon) a narrator's voice, like an old "
      "storybook. **1920 × 1080 px**, 16:9, opaque, painted in the same style as the title painting. Keep the **bottom third "
      "calm and darker** (the text sits there) and the important parts in the middle (the picture drifts and zooms slowly). "
      "Deliver in `intro/`. Placeholders made from game screenshots are in until then.\n")
    w("| File | The words on screen | The picture |")
    w("|---|---|---|")
    for f, words, look in intro_left:
        w(f"| `{f}` | {words} | {look} |")

# ---------------------------------------------------------------- revisions and extras
if REMAINING:
    w("\n## Revisions\n")
    w("| File | What to change |")
    w("|---|---|")
    left = [(f, what) for f, what in REVISIONS if f not in REVISED]
    for f, what in left:
        w(f"| `{f}` | {what} |")
    counts["revisions"] = len(left)
    if not left:
        out.pop(); out.pop(); out.pop()  # no revisions left: drop the empty table
extras = rows("item_icons", [("gold_coins.png",)])
torch = rows("vfx", [("torch_flame.png",)])
if extras or torch:
    w("\n## Small extras (optional, whenever)\n")
    w("| File | What | Notes |")
    w("|---|---|---|")
    if extras:
        w("| `item_icons/gold_coins.png` | The gold icon (inventory, loot, shops) | 64 × 64, a small pile of coins, transparent background. |")
    if torch:
        w("| `sprites/vfx/torch_flame.png` | The small flame on wall torches | Like the fireplace fire, but small and narrow: one row of square frames, 32 or 64 px, hard edges, flame touching the bottom. |")

if not REMAINING:
    w("\n## Done, thank you!\n")
    w("Fire (main, small and magic), all 62 characters, the 4 monsters, all portraits, the spell effects, most icons, the "
      "world textures, skies and ground scatter.\n")
if REMAINING and not any(counts.values()):
    out[:] = ["# The Uncounted: art still needed (for Noor)\n",
              "**Nothing!** Every portrait, character, monster, spell effect, icon, sky, texture and flame the game needs has been "
              "delivered and is in the game. Thank you, Noor. 🎉\n",
              "(New art will only be needed when new content is added; rerun `python3 tools/write_art_brief.py --remaining` then.)\n"]
name = "NOOR_REMAINING_ART.md" if REMAINING else "NOOR_ART_BRIEF.md"
open(os.path.join(ROOT, "docs", name), "w").write("\n".join(out) + "\n")
print(f"Wrote docs/{name}:", ", ".join(f"{k} {v}" for k, v in counts.items()))

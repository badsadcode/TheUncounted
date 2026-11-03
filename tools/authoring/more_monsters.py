"""More monsters, one or two per area, mostly variations on existing fighters: Kevin the bandit and hedge goblins on the
Old Road, angry badgers and wisps in the Whistling Wood, a gravedigger ghoul in Hollowmere's graveyard, Pinchwick crabs on
Saltmere's quay, paperwork elementals in the Registry Annex, salt wights on the reef.
ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
CR = load("content/creatures/core_creatures.json")
SFX = {"alert": "assets/audio/sfx/rat_squeak.wav", "attack": "assets/audio/sfx/sword_swing.wav", "hit": "assets/audio/sfx/sword_hit.wav",
       "death": "assets/audio/sfx/enemy_death.wav"}
def mon(cid, name, anim, scale, family, hp, armor, dmg, speed, xp, loot, alert, death, note, hit=(220, 200, 170), glow=False, sanity=0, alert_sfx=None):
    a = {"name": "strike", "damage": dmg, "reach_meters": 1.6, "windup_seconds": 0.55, "cooldown_seconds": 1.3}
    if sanity: a["sanity_damage"] = sanity
    CR["creatures"].append({"id": f"core:enemy.{cid}", "name_key": f"enemy.{cid}.name",
        "appearance": {"type": "sprite_8dir", "sprite_sheet": f"assets/sprites/enemies/{cid}.png", "animation_data": f"assets/animations/{anim}.json", "scale": scale},
        "stats": {"health": hp, "armor": armor, "move_speed": speed, "xp_reward": xp}, "behavior": "melee_patroller", "family": family,
        "perception": {"sight_meters": 12.0, "hearing_meters": 9.0}, "attack": a, "loot_table": loot,
        "audio": dict(SFX, alert=alert_sfx or SFX["alert"]), "hit_fx": {"color": list(hit), "glow": glow},
        "lines": {"alert": f"line.{cid}.alert", "death": f"line.{cid}.death"}})
    S[f"enemy.{cid}.name"] = name; S[f"line.{cid}.alert"] = alert; S[f"line.{cid}.death"] = death; S[f"bestiary.{cid}"] = note
SW = "assets/audio/sfx/sword_swing.wav"
mon("kevin_bandit", "Kevin, Bandit (Level Zero)", "skeleton", 1.7, "humanoid", 50, 1, 7, 2.7, 15, "core:loot.vermin_drop",
    "Stand and deliver! ...Is that how it goes? Steve said that's how it goes.", "Tell Steve... I did the voice...",
    "Steve's cousin. Learned banditry from Steve, which explains a lot. Means well. Robs badly. Apologises afterwards. - H.", alert_sfx=SW)
mon("hedge_goblin", "Hedge Goblin", "skeleton", 1.3, "humanoid", 40, 2, 6, 3.1, 12, "core:loot.vermin_drop",
    "Oi! That's OUR hedge!", "Tell the hedge... I loved it...",
    "Lives in hedges. Wears a pot. Fights with a spoon. Not dangerous alone; never alone. They steal socks, nobody knows why. - H.")
mon("angry_badger", "Angry Badger", "grave_rat", 1.25, "beast", 45, 2, 8, 3.3, 14, "core:loot.wolf",
    "(The badger makes a noise like a kettle full of wasps.)", "(The badger glares at you, even now.)",
    "Small. Furious. Unafraid of anything, including you, wolves and the concept of mortality. Respect the badger. - H.")
mon("wisp", "Will-o'-the-Wisp", "crypt_keeper", 0.9, "spirit", 35, 0, 7, 3.0, 16, "core:loot.ink_wraith",
    "(A light bobs between the trees, beckoning. It giggles.)", "(The light goes out with a small, disappointed 'aww'.)",
    "A floating light that leads travellers off the path and into the pond. Thinks it's hilarious. It is not hilarious. - H.",
    hit=(150, 255, 220), glow=True, sanity=1, alert_sfx=SW)
mon("ghoul_gravedigger", "Gravedigger Ghoul", "skeleton", 1.75, "undead", 80, 2, 10, 2.4, 25, "core:loot.crypt_basic",
    "Who's been walking on my graves? I just DID these.", "Back... in the... hole...",
    "Dug graves at Hollowmere for forty years, then kept going. Takes it very personally if you walk on the mounds. Maces work. - H.")
mon("pinchwick_crab", "Pinchwick Crab", "ash_crawler", 1.05, "beast", 50, 4, 8, 2.6, 15, "core:loot.fish_harbour",
    "(Click. Click click. CLICK.)", "(The crab goes very still, then rolls over, offended.)",
    "Saltmere's quay crabs: armoured, sideways, sure of themselves. Armour-piercing helps. Mother Brine puts them in the chowder. - H.",
    hit=(255, 170, 130))
mon("paperwork_elemental", "Paperwork Elemental", "skeleton", 1.8, "construct", 70, 1, 9, 2.5, 22, "core:loot.bone_clerk",
    "INCOMPLETE. INCOMPLETE. INCOMPLETE.", "(The elemental collapses into a heap of forms, all of them filled in wrong.)",
    "Three hundred years of unfiled forms in the Annex, folded into a person by sheer resentment. Fire works wonders. - H.",
    hit=(240, 235, 215), sanity=1, alert_sfx=SW)
mon("salt_wight", "Salt Wight", "skeleton", 1.85, "spirit", 85, 2, 11, 2.5, 28, "core:loot.drowned",
    "...the tide... remembers you...", "...the tide... forgets...",
    "A sailor the sea kept, crusted in salt and patience. Slow, cold, relentless. Fire dries them out. - H.",
    hit=(190, 230, 255), glow=True, sanity=2, alert_sfx=SW)
save("content/creatures/core_creatures.json", CR)

def place_builder(path, lines, tag):
    src = open(path).read()
    block = f"# ============================================================================ more monsters ({tag}, tools/authoring/more_monsters.py)\n" + "".join(lines) + "\n"
    assert "region = {" in src
    open(path, "w").write(src.replace("region = {", block + "region = {", 1))
C = lambda iid, cid, p, a, b: f'creature("{iid}", "core:enemy.{cid}", {p}, {a}, {b})\n'
place_builder("tools/build_wood.py", [
    C("wood_badger_0", "angry_badger", (8.0, 0.0, 12.0), (6.0, 0.0, 12.0), (11.0, 0.0, 12.0)),
    C("wood_badger_1", "angry_badger", (14.0, 0.0, -4.0), (14.0, 0.0, -7.0), (14.0, 0.0, -1.0)),
    C("wood_wisp_0", "wisp", (-18.0, 0.4, -12.0), (-19.0, 0.4, -15.0), (-15.0, 0.4, -9.0)),
    C("wood_wisp_1", "wisp", (-19.0, 0.4, 3.0), (-19.0, 0.4, -1.0), (-19.0, 0.4, 5.0))], "Whistling Wood")
place_builder("tools/build_mansion.py", [
    C("grave_ghoul_0", "ghoul_gravedigger", (-12.6, 0.0, -14.0), (-16.5, 0.0, -14.0), (-8.5, 0.0, -14.0))], "Hollowmere graveyard")
place_builder("tools/build_docks.py", [
    C("quay_crab_0", "pinchwick_crab", (-6.0, 0.0, -8.0), (-9.0, 0.0, -8.0), (-3.0, 0.0, -8.0)),
    C("quay_crab_1", "pinchwick_crab", (5.0, 0.0, -8.5), (2.0, 0.0, -8.5), (8.0, 0.0, -8.5))], "Saltmere quay")
place_builder("tools/build_reef.py", [
    C("reef_wight_0", "salt_wight", (4.0, 0.0, 8.0), (1.0, 0.0, 8.0), (7.0, 0.0, 8.0)),
    C("reef_wight_1", "salt_wight", (-7.0, 0.0, 4.0), (-7.0, 0.0, 1.0), (-7.0, 0.0, 7.0))], "Sleeper's Reef")
def place_json(path, items):
    R = load(path)
    for iid, cid, p, a, b in items:
        R["creatures"].append({"instance_id": iid, "creature_id": f"core:enemy.{cid}", "pos": list(p), "patrol_a": list(a), "patrol_b": list(b)})
    save(path, R)
place_json("content/regions/old_road.json", [
    ("road_kevin_0", "kevin_bandit", (8.0, 0.0, 9.0), (4.0, 0.0, 9.0), (12.0, 0.0, 9.0)),
    ("road_kevin_1", "kevin_bandit", (-15.0, 0.0, -9.0), (-18.0, 0.0, -9.0), (-11.0, 0.0, -9.0)),
    ("road_goblin_0", "hedge_goblin", (-12.0, 0.0, 10.0), (-14.0, 0.0, 11.0), (-8.0, 0.0, 11.0)),
    ("road_goblin_1", "hedge_goblin", (-4.0, 0.0, 12.0), (-6.0, 0.0, 13.0), (-1.0, 0.0, 13.0)),
    ("road_goblin_2", "hedge_goblin", (2.0, 0.0, -12.0), (-1.0, 0.0, -12.5), (5.0, 0.0, -12.5))])
place_json("content/regions/registry_annex.json", [
    ("archive_paperwork_0", "paperwork_elemental", (1.0, 0.0, -11.0), (-1.0, 0.0, -11.0), (3.5, 0.0, -11.0)),
    ("crypt_paperwork_1", "paperwork_elemental", (-11.5, 0.0, -13.0), (-12.5, 0.0, -10.5), (-12.5, 0.0, -15.0))])
S["tip.48"] = "Kevin is Steve's cousin. If Kevin robs you, Kevin will apologise. Kevin will still rob you."
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

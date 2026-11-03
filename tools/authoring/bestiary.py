"""Bestiary field notes (one per creature, Hollis's voice). ARCHIVE: one-off, already ran. Do NOT rerun."""
import json
N = {
 "grave_rat": "Graveyard rat, the size of a terrier and twice as rude. Comes in packs. Hates fire. Loves you, specifically, for dinner. - H.",
 "restless_skeleton": "Somebody's grandfather, still on his feet out of sheer stubbornness. Blunt weapons rattle them; arguments don't. - H.",
 "ash_crawler": "Looks like a spider, smells like a bonfire, bites like both. Don't set it on fire. It likes that. - H.",
 "lost_sentinel": "Old Bureau guardian, still guarding a door nobody remembers. Slow. Heavy. Patient. Don't stand in front of it. - H.",
 "crypt_keeper": "Archivist Morvath: a clerk so dedicated he kept filing after death. Ink, pages, grudges. Keep moving or get catalogued. - H.",
 "lullaby_warden": "Sang the vault's sleepers to sleep for a hundred years. Still singing. Cover your ears and hit it with something. - H.",
 "bone_clerk": "Skeletal clerk with spectacles. Stamps you, then fights you. Wants Form 27-B. Nobody has Form 27-B. - H.",
 "ink_wraith": "A ghost made of spilled ink. Throws itself at you, literally. Leaves stains. Light hurts it. - H.",
 "truffle_hog": "It is a rat. It believes it is a pig. It is wrong about everything except truffles. - H.",
 "animated_armor": "Hollowmere's guest list enforcement. Empty inside. Asks if you're on the list. You are not on the list. - H.",
 "wailing_footman": "A servant still serving dinner to a party that ended a century ago. Furious about the cutlery. - H.",
 "rat_king": "Wears a crown. Thinks it's royalty. Bites like a king, at least. Bring fire, and a second set of boots. - H.",
 "wrathful_host": "Sir Percival on a bad night: a host whose guests stopped coming. Fire, fury, a staff. Sad, really. Still hits hard. - H.",
 "the_drowned": "The sea's dead, come back up to ask your name. Don't tell them. Strike before they finish asking. - H.",
 "tide_acolyte": "Cultist with a glowing staff and a lot of salt in their hair. Casts from range. Close the distance. - H.",
 "name_eater_avatar": "The thing under the chapel. I don't write its name down. It would like that. Don't look at it longer than you need to. - H.",
 "grey_wolf": "A wolf. A real one, not a costume, not a werewolf, not somebody's grandmother. Fast, smart, hungry. Fight it near a tree. - H.",
 "granny_wolf": "A wolf in a nightgown and a bonnet. Big eyes. Big ears. Big teeth. You know the rest. Bring an axe. - H.",
 "dreaming_limb": "One arm of something asleep under the reef. Just the arm. I don't want to meet the rest of it. - H.",
 "phantom_clerk": "Not a ghost. A merchant in a bedsheet. Easy to beat; hard to stop laughing. - H.",
 "howler": "Not a werewolf. A monk in a fur suit, wearing sandals. Hits harder than you'd think. Jealousy does that. - H.",
 "headless_knight": "Not headless. Steve. In armour. With a hat on a stick. Go easy on him; he's having the best day of his life. - H.",
 "repossession_golem": "Iron, stamped REPOSSESSED all over, bought with a dragon's money. Slow to start, hard to stop. Hit the joints. - H.",
}
loc = json.load(open("content/localization/en.json"))
for k, v in N.items():
    loc["strings"][f"bestiary.{k}"] = v
loc["strings"]["tip.46"] = "The Bestiary (character screen) remembers every monster you defeat. Ten of a kind and you know where to hit them: +5% damage."
open("content/localization/en.json", "w").write(json.dumps(loc, indent=2, ensure_ascii=False))
ids = [c["id"].split(".")[-1] for c in json.load(open("content/creatures/core_creatures.json"))["creatures"]]
print("missing notes:", [i for i in ids if i not in N])

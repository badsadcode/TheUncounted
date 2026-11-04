"""Eranu sounds more Scottish: her lines rewritten in light, readable Scots (aye, wee, ken, dinnae, cannae, no', hame,
oot, doon, guid, braw, havering, numpty). Only her own words change; narration and other characters stay as they were.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

S = {
    # --- her dialogue (Lantern Inn)
    "dlg.eranu.root": "A tall, broad-shouldered woman with a long blonde braid sits in the window seat: green kilt, a round targe propped "
                      "beside her, a sword across her knees. She keeps one eye on you and the other on the door.\n\n\"Aye? Whit is it?\"",
    "dlg.eranu.who": "\"Eranu. Fae the Glens, up north, where the weather has opinions an' shares them.\" She pats the sword. \"I hit things "
                     "that need hittin' and I read things that need readin'. Folk roond here are aye surprised I dae both. Then they're "
                     "surprised again.\"",
    "dlg.eranu.waiting": "\"I'm waitin' on ma waifu.\"\n\nShe says it with complete confidence, as if it's a word everyone kens.\n\n\"Coth. "
                         "Tall, skinny, beard doon tae here, hair doon tae there. Nae trousers, usually. Ye'd mind him.\" A frown at the "
                         "door. \"Three days ago he said he was awa' oot tae find some trousers. He's no' come back. Coth doesnae find "
                         "trousers. Trousers find Coth, an' he runs.\"",
    "dlg.eranu.waifu": "\"Aye. Ma waifu.\" A long, level look, daring you to make something of it. \"He protests. He's wrang.\"\n\n\"So. "
                       "Are ye gonnae find him or no'?\"",
    "dlg.eranu.accept": "\"Guid.\" She stands, and she's taller than you expected. \"He went west, intae the Whistling Wood. He'll have made "
                        "camp somewhere daft, he'll have made a pal oot o' somethin' that's no' alive, an' he'll have lost count o' the "
                        "days. He aye loses count o' the days.\"\n\n\"Bring him hame. Tell him Eranu says come hame, Cothepoo.\"",
    "dlg.eranu.news": "\"West, in the Whistling Wood. Look for a camp somewhere daft, a wee fire, an' a beard.\" Her grip tightens on the "
                      "sword. \"An' if he tells ye it's been a thousand years, he's havering. He'll have been countin' somethin'. Make "
                      "him count it oot loud.\"",
    "dlg.eranu.nickname": "Eranu's mouth twitches.\n\n\"Because he's Coth, an' because he's a wee poo sometimes.\" She shrugs. \"He hates it. "
                          "That's how ye ken it's love.\"",
    "dlg.eranu.reunion": "When the clapping dies down, Eranu presses something into your hands: a pair of trousers, neatly folded, never "
                         "worn.\n\n\"His,\" she says. \"I've carried them since he left, for when we found him. He says he doesnae want "
                         "them back.\"\n\nCoth, from behind her, through a mouthful of stew: \"I DON'T.\"\n\n\"An' this, for yer "
                         "trouble.\" A heavy wee purse. \"If ye ever need a sword arm, or two, ye ken where the windae seat is.\"",
    "dlg.eranu.join": "Eranu picks up targe and sword in one easy movement.\n\n\"Aye, go on, then. Somebody's got tae keep ye alive.\" A "
                      "glance across the table. \"Dinnae wander aff, Cothepoo.\"\n\nCoth, wounded: \"I have NEVER wandered.\"",
    "dlg.eranu.full": "\"Ye've a full party already. I'll no' be the spare wheel on anybody's cart.\"",
    "dlg.eranu.wait": "\"Aye. I'll be at the windae.\" She heads back to her seat, and her eyes go straight to the door, out of habit.",
    "dlg.coth.join": "Coth leaps up, scattering stew. \"An ADVENTURE? Out THERE? Where the trousers are?\" He considers this. \"I'll come. "
                     "But I'm not wearing them.\"\n\nEranu, without looking up: \"Dinnae lose him.\"",
    "story.cothepoo.2": "Eranu crosses the inn in four strides. For a moment it looks like she might hit him.\n\nShe hugs him instead, hard "
                        "enough to lift him off the floor.\n\n\"COTHEPOO. Three days, ya absolute numpty. Three DAYS.\"",
    "story.cothepoo.3": "\"Felt like a thousand,\" Coth says, muffled, into her shoulder.\n\n\"Aye,\" says Eranu, more quietly. \"It did, ya "
                        "daftie.\"\n\nMarta puts two bowls of stew on the table without being asked. Somebody by the fire starts a slow "
                        "clap. It catches on.",
    # --- barks
    "bark.eranu.2": "Have ye seen a man wi' nae trousers? Ye'd ken.",
    "bark.eranu.3": "Aye, he's back. Dinnae tell him I was worried.",
    # --- companion lines
    "comp.eranu.idle.1": "Keep yer guard up. Naw, higher. Aye, that's it.",
    "comp.eranu.idle.2": "Back hame, this'd count as a braw day. Back hame, the rain comes sideways.",
    "comp.eranu.idle.3": "I read once this road was built by a king who wanted tae see the sea. He never did. The road did.",
    "comp.eranu.idle.4": "If anythin' jumps oot at us, you go left, I go through it.",
    "comp.eranu.idle.5": "Cothepoo, stop lickin' that mushroom.",
    "comp.eranu.idle.6": "Dunstan, lift wi' yer legs. Yer LEGS, lad.",
    "comp.eranu.idle.7": "Baggy, ye've had that magnifyin' glass on ma boots for a full minute.",
    "comp.eranu.combat.2": "Get behind the shield!",
    "comp.eranu.combat.3": "Is that aw ye've got?",
    "comp.eranu.kill.2": "Aye. Stay doon.",
    "comp.eranu.kill.3": "That's for Cothepoo, whatever ye did tae him.",
    "comp.eranu.kill.4": "Braw.",
    "comp.eranu.heal.1": "Here. Drink this an' stop bleedin' on ma kilt.",
    "comp.eranu.heal.2": "Haud still. Ma's recipe: oats, honey, an' a bit o' shoutin'.",
    "comp.eranu.heal.3": "Ye're nae use tae me deid. Get that doon ye.",
    "comp.eranu.level.2": "Aye, ye're gettin' the hang o' it.",
    "comp.eranu.catchup.1": "There ye are. Dinnae run aff like that, ye're worse than Coth.",
    "comp.eranu.catchup.2": "Right behind ye. Aye.",
    "comp.eranu.zone.bellwether": "Bellwether. Wee place, but they keep a guid fire at the Lantern.",
    "comp.eranu.zone.old_road": "Auld roads remember who walked them. Let's gie this one somethin' guid tae remember.",
    "comp.eranu.zone.annex": "Records. Filin' cabinets. I've fought worse. No' much worse.",
    "comp.eranu.zone.vault_three": "Smells like a tomb, 'cause it is one. Shield up.",
    "comp.eranu.zone.seal_chamber": "Whatever's doon here, it's no' gettin' past me.",
    "comp.eranu.zone.hollowmere": "Fine auld hoose. Shame aboot the hauntin'.",
    "comp.eranu.zone.hollowmere_manor": "Mind the stairs. Mind the portraits. Mind everythin', really.",
    "comp.eranu.zone.saltmere": "Sea air! Proper air. Minds me o' hame, except hame's colder an' the fish argue back.",
    "comp.eranu.zone.sunken_chapel": "A kirk underwater. Aye, nothin' sinister aboot that at aw.",
    "comp.eranu.zone.whistling_wood": "This is where I'd have found Cothepoo masel', if I'd trusted ma ain nose.",
    "comp.eranu.zone.sleepers_reef": "Oot past the haar. Steady, now. I've sailed in worse.",
    "comp.eranu.zone.here": "A city naebody remembers. I'll remember it. That's a start.",
    "comp.eranu.zone.here_archive": "Books wi' teeth. I've read a few like that.",
    # --- her lines in banter
    "comp.eranu.banter.waifu.0": "Cothepoo, tell them whit ye are.",
    "comp.eranu.banter.waifu.2": "Tell them whit ye ARE.",
    "comp.eranu.banter.trousers.1": "Ye ken whit helps wi' the cold, Coth?",
    "comp.eranu.banter.thousand.0": "Promise me ye'll no' go missin' for a thousand years again.",
    "comp.eranu.banter.squire.0": "Yer stance is guid, Dunstan. Yer sword's daft.",
    "comp.eranu.banter.squire.2": "It's a family o' daft swords.",
    "comp.eranu.banter.detective.1": "Ye can ask.",
    "comp.eranu.banter.detective.3": "Asleep. Wi' ma sword. Next question.",
    "comp.eranu.banter.statue.0": "Ye're a braw bit o' stonework, Grout.",
    "comp.eranu.banter.statue.2": "Modest, an' aw.",
    "comp.coth.banter.bark.1": "Naw, Coth.",
    "comp.coth.banter.bark.3": "Did ye eat bark, Coth?",
    "comp.dunstan.banter.stance.1": "It's a normal-sized sword, son.",
    "comp.dunstan.banter.stance.3": "That's the hale secret.",
}
loc = json.load(open("content/localization/en.json"))
missing = [k for k in S if k not in loc["strings"]]
assert not missing, missing
loc["strings"].update(S)
open("content/localization/en.json", "w").write(json.dumps(loc, indent=2, ensure_ascii=False))
print("ok", len(S))

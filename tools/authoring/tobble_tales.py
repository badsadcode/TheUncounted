"""Old Tobble's tales become proper told stories: "Tell me a story" opens a list of titles; picking one opens the tale
window (dialogue action tell_tale), where the text scrolls in time with its recording, assets/audio/voice/
tale.tobble.<n>.ogg|wav|mp3 (made by BadSad with ElevenLabs), or at reading pace until it exists.
Replaces the earlier in-dialogue stories (tools/authoring/old_tobble.py). He.

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
TALES = [
    ("The Winter the River Froze",
     "Now. This was the winter the river froze. You won't remember it. Nobody remembers it. That's how cold it was: it froze "
     "the remembering.\n\nThe whole village went down to the river, and there it was, white and hard as a bishop's heart. So "
     "we skated. Every day for a month. Old Marta's grandmother did a pirouette so beautiful the crows applauded. The miller "
     "skated to Saltmere and back before breakfast and was never the same again. I taught a pig to skate. Not well. But "
     "enthusiastically.\n\nAnd then, one morning, the sun came out, and the river began to flap.\n\nFlap, I said. Rivers don't "
     "flap. And it turned out it wasn't the river at all. It was Mrs. Pennyworth's washing. She'd laid out every sheet she "
     "owned to dry, and the frost had got them, and we'd been skating on her bedlinen for a month.\n\nShe was very cross. "
     "Very cross Mrs. Pennyworth. She made us all wash it again.\n\nWe never did find the river. I think it left. Can't say "
     "I blame it."),
    ("Duke, the Goat Who Could Count to Four",
     "When I was a lad, I had a goat. His name was Duke, and Duke could count to four.\n\nNot three. Not five. Four. You'd "
     "hold up four turnips and Duke would stamp four times. Clever as a magistrate. You'd hold up three turnips and Duke "
     "would just look at you. Disappointed, like. As if you'd let the both of you down.\n\nSo I entered him in the county "
     "fair. The Grand Arithmetical Livestock Competition. There was a sheep that could nod yes. A pig that could spell 'pig', "
     "almost. And a turnip. Just a turnip. Its owner said it was a very good listener.\n\nDuke stamped to four in front of the "
     "whole county. Perfect. The crowd wept. And then the judges gave first prize to the turnip.\n\nThe turnip couldn't count "
     "at all! It couldn't do anything! It was a turnip!\n\nTurned out the turnip's owner was the judge's brother-in-law.\n\n"
     "Politics, that was. Duke never stamped again. He took up the flute. Badly. But with feeling."),
    ("The Edge of the World",
     "I once walked all the way to the edge of the world. People say you can't. People say it's too far, or it isn't there, "
     "or there are dragons. Well, I went.\n\nYou go out past Saltmere. Past the last pier, past the last fish, past the last "
     "fisherman who'll admit to being one. Then it's second on the left, by the rock that looks like Oakhaven if you squint. "
     "Then straight on for three days. Bring a sandwich.\n\nAnd there it is. The edge of the world. And do you know what's "
     "there?\n\nA fence.\n\nJust an ordinary fence. Wooden. Bit wobbly. And somebody, long ago, had nailed a sign to it, and "
     "the sign said, in big careful letters: NO.\n\nThat's all. Just: NO.\n\nWell, I thought about it. I thought about it "
     "for a good long while. And then I turned around and came home.\n\nGood sign, that. Clear. Doesn't waste your time. I "
     "wish more signs were like it. I wish more people were like it."),
    ("The King Who Was Afraid of Tuesdays",
     "Long ago, before the Great Silence, before the Bureau, before soup, there lived a king who was afraid of Tuesdays.\n\n"
     "Nobody knew why. Some said a Tuesday had been rude to him as a boy. Some said he'd been born on one and never got "
     "over it. But every Monday night, regular as the tide, the king would go to bed and sleep straight through to "
     "Wednesday morning.\n\nAnd the kingdom carried on without him. Taxes on Tuesdays were voluntary. Weddings on Tuesdays "
     "didn't count. A whole army once invaded on a Tuesday, found nobody to surrender to, and went home confused.\n\nHe "
     "ruled for forty years, that king. Forty years, and never once saw a Tuesday.\n\nAnd then, one week, he woke up early. "
     "Just a little bit early. He opened his eyes, and it was dark, and he didn't know what day it was. And he lay there, "
     "trembling, until the sun came up.\n\nIt was a Thursday. He'd overslept the Wednesday as well.\n\nDied on the spot. Of "
     "surprise."),
    ("Why the Well Is Here",
     "This well. You've been looking at it. Everyone does. Wondering why it's here, right in the middle of everything.\n\n"
     "Well. I don't know either.\n\nIt was here when I came, and I came before the village. Before the road. Before the "
     "Bureau put up its first sign telling everyone where they were and what they owed. There was just me, and a field, and "
     "this well. Already here. Already old.\n\nI asked it, once. I leaned right over and said: well, well, why are you "
     "here? And it said nothing. Wells are like that. Very discreet.\n\nSo I tell it things instead. Everything, really. "
     "Fifty years of things. My secrets. Other people's secrets. What I really think about the Bureau. The thing about Mrs. "
     "Pennyworth's washing.\n\nAnd the well keeps them. Every one. Down there in the dark, all the things this village ever "
     "whispered.\n\nSometimes, late at night, if you put your ear to the stones, you can hear them. All the secrets. Talking "
     "to each other.\n\nThey're mostly about me. I don't mind. It's nice to be thought of."),
    ("The Dragon and the Pie",
     "There was a dragon, once. Came to Bellwether. Huge thing, red as a bad sunset, and it landed right there in the square "
     "and roared, and it said: GOLD. BRING ME ALL YOUR GOLD.\n\nWell. We didn't have any gold. This is Bellwether. We had "
     "turnips, and opinions, and a lot of rain.\n\nSo Marta's grandmother, who was afraid of nothing except draughts, "
     "walked straight up to that dragon with a pie. Rabbit and onion. Still warm. And she held it up and said: you look "
     "tired, love. Have you eaten?\n\nThe dragon looked at the pie. The dragon looked at Marta's grandmother. And then it ate "
     "the pie, very carefully, in one bite, and a single tear rolled down its great scaly cheek.\n\nAnd it flew away, and we "
     "never saw it again.\n\nWe argued for years afterwards about why. Some said it was the best pie Marta's grandmother "
     "ever made. Some said it was the worst.\n\nHard to tell, with dragons. They're very private about their feelings."),
    ("How I Invented the Chair",
     "Did you know I invented the chair?\n\nIt's true. Before me, there were no chairs. None. Everybody just sort of hovered. "
     "You'd go to a feast and everyone would be hovering round the table, knees bent, arms out, sweating. Exhausting. Nobody "
     "lived past forty. Their legs gave out.\n\nAnd one day I thought: what if the hovering was done by a thing, instead of "
     "by you?\n\nI built it out of four sticks and a plank and a great deal of hope. I sat on it. And I tell you, the whole "
     "village came running. People wept. A man proposed to it.\n\nSo I went to the Bureau to patent it. Filled in Form "
     "Twelve: Inventions, Domestic. Stamped. Signed. Witnessed by a goat.\n\nAnd they lost it.\n\nSo now everyone in the "
     "kingdom sits for free, and I get nothing. Not a penny.\n\nNext time you sit down, you'll feel it. A little twinge. "
     "Somewhere about the conscience.\n\nThat's guilt, that is. That's me."),
    ("My Cousin the Skeleton",
     "Once, in my younger days, I fought a skeleton.\n\nDown in the crypt, it was. I'd gone looking for my hat. Don't ask why "
     "my hat was in the crypt. It was a different time. And out of the dark comes this skeleton, rattling and clacking, and "
     "it squares up to me, and we fight.\n\nFor three days and three nights we fought. It hit me with a femur. I hit it with "
     "a candlestick. It hit me with my own hat. Terrible business.\n\nAnd on the fourth morning, we were both so tired we "
     "just sat down. Side by side on a coffin. And it looked at me, and I looked at it, and I said: you've got my "
     "grandfather's chin.\n\nAnd it had! It was my cousin Albert! Been dead a hundred years and never told anyone!\n\n"
     "Lovely fellow, Albert. Bit thin. We still write to each other, you know.\n\nWell. I write. He mostly rattles. But you "
     "can tell he means well."),
]
N = len(TALES)
for i, (title, text) in enumerate(TALES, 1):
    S[f"tale.tobble.{i}.title"] = title
    S[f"tale.tobble.{i}.text"] = text

D = load("content/dialogue/chapter_zero_dialogue.json")
dl = next(d for d in D["dialogues"] if d["id"] == "core:dialogue.old_tobble")
nodes = dl["nodes"]
for k in [k for k in nodes if k.startswith("story") or k in ("andthen", "thanks")]:
    del nodes[k]
root = nodes["root"]
root["choices"] = [c for c in root["choices"] if not c["next"].startswith("story")]
S["dlg.tobble.root.c_tell"] = "\"Tell me a story.\""
root["choices"].insert(0, {"text_key": "dlg.tobble.root.c_tell", "next": "pick"})
S["dlg.tobble.pick"] = ("\"A story! Oh, wonderful. Sit down. Well, stand, then. Which one shall it be?\"\n\nHe counts them off on his "
                        "fingers, runs out of fingers, and starts again on the same ones.")
pick = {"speaker_key": "npc.old_tobble.name", "text_key": "dlg.tobble.pick", "choices": []}
for i in range(1, N + 1):
    pick["choices"].append({"text_key": f"tale.tobble.{i}.title", "next": "END",
                            "actions": [{"type": "tell_tale", "key": f"tale.tobble.{i}"}]})
S["dlg.tobble.pick.back"] = "\"Maybe later.\""
pick["choices"].append({"text_key": "dlg.tobble.pick.back", "next": "bye"})
nodes["pick"] = pick
save("content/dialogue/chapter_zero_dialogue.json", D)

loc = load("content/localization/en.json")
for k in [k for k in loc["strings"] if k.startswith("dlg.tobble.story") or k.startswith("dlg.tobble.andthen") or k.startswith("dlg.tobble.thanks")
          or k == "dlg.tobble.root.c0" or k.startswith("dlg.tobble.root.c") and loc["strings"][k] == "\"Tell me a story.\""]:
    del loc["strings"][k]
loc["strings"].update(S)
save("content/localization/en.json", loc)
print("ok", N)

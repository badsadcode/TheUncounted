"""Dunstan is from Uruguay (in-world: the Eastern Shore, after Uruguay's old name, the Banda Oriental). A mate gourd on his
belt (sprite style key "mate"), "¡Vamos!" / "¡Dale!" / "¡GOLAZO!" in fights, stories of asado and home, a "What's in
the cup?" conversation where he shares his mate (with the rules: you finish it and hand it back; only say thanks when
you don't want more), a stamina item, and banter where Eranu and Coth try mate.

Pronouns: Dunstan he. ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
P = {"eranu": "core:npc.eranu", "coth": "core:npc.coth", "grout": "core:npc.grout", "baggy": "core:npc.detective_baggy"}

# ------------------------------------------------------------------ dialogue
D = load("content/dialogue/chapter_zero_dialogue.json")
dl = next(d for d in D["dialogues"] if d["id"] == "core:dialogue.dunstan")
root = dl["nodes"]["root"]
end = next(i for i, c in enumerate(root["choices"]) if c["next"] == "END")
S["dlg.dunstan.root.c_mate"] = "\"What's in the cup on your belt?\""
S["dlg.dunstan.root.c_home"] = "\"Where are you from, Dunstan?\""
root["choices"][end:end] = [{"text_key": "dlg.dunstan.root.c_mate", "next": "mate"}, {"text_key": "dlg.dunstan.root.c_home", "next": "home"}]


def node(nid, text, choices, actions=None):
    key = f"dlg.dunstan.{nid}"
    S[key] = text
    n = {"speaker_key": "npc.dunstan.name", "text_key": key, "choices": []}
    if actions: n["actions"] = actions
    for i, ch in enumerate(choices):
        S[f"{key}.c{i}"] = ch[0]
        c = {"text_key": f"{key}.c{i}", "next": ch[1]}
        if len(ch) > 2: c.update(ch[2])
        n["choices"].append(c)
    dl["nodes"][nid] = n


node("mate",
     "Dunstan lights up and unhooks a little round gourd from his belt, a silver straw sticking out of a heap of green leaves.\n\n"
     "\"Mate! From home. You pour hot water on the yerba, you drink it through the bombilla, and then you pass it on. "
     "You never drink mate alone. Well. I do, a lot, lately. But you're not SUPPOSED to.\"\n\nHe holds it out hopefully.",
     [("\"Can I try?\"", "mate_share", {"conditions": [{"type": "flag_not_set", "flag": "dunstan_mate_shared"}]}),
      ("\"Another round?\"", "mate_again", {"conditions": [{"type": "flag_set", "flag": "dunstan_mate_shared"}]}),
      ("\"Maybe later.\"", "root")])
node("mate_share",
     "\"YES! Okay, rules.\" He counts on his fingers, very serious. \"One: you drink it all, until it gurgles. The gurgle is "
     "important. Two: you hand it back to me, and I fill it again for the next person. Three: don't stir the bombilla. "
     "Never stir the bombilla. And four...\"\n\nYou drink. It's hot, grassy and bitter, and then, somehow, good. It gurgles.\n\n"
     "\"...four: don't say thank you unless you're finished. 'Thank you' means 'no more for me'.\" He grins. \"So? Another?\"\n\n"
     "He presses a little bundle into your hands before you can answer: dried yerba, wrapped in cloth. \"For the road. "
     "It keeps you going. My grandfather swore by it. He swung Big Margaret for forty years on mate alone.\"",
     [("\"Thank you, Dunstan.\"", "mate_thanks")],
     [{"type": "set_flag", "flag": "dunstan_mate_shared", "value": True}, {"type": "give_item", "item_id": "core:item.dunstan_mate", "qty": 3}])
node("mate_thanks", "\"Ahh, you said thank you! That means you're done.\" He laughs and refills the gourd for himself. \"You learn fast. "
                    "You're practically from the Eastern Shore now.\"", [("\"¡Dale!\"", "root")])
node("mate_again",
     "Dunstan refills the gourd and hands it over without a word. That's how it works, apparently: you came back, so you're family.\n\n"
     "It gurgles. You hand it back. Nobody says thank you, so it keeps going round for a while, there in the middle of the square.",
     [("\"...Thank you.\"", "root")], [{"type": "heal_player"}])
node("home",
     "\"The Eastern Shore! Across the sea, far south. Rolling green plains, cattle as far as you can see, a river so wide you'd "
     "think it was the ocean.\" He gets a faraway look. \"On Sundays the whole family does an asado: a fire, a grill, meat, "
     "and three hours of everyone talking at once. Nobody's ever in a hurry. Nobody's ever alone.\"\n\n\"And football on "
     "the beach, with my cousins. I was terrible. Mostly I was the goalpost.\" He pats Big Margaret. \"I came north to become "
     "a squire. I miss it every day. But I'm making friends here!\" A glance at you. \"I think I'm making friends here.\"",
     [("\"You definitely are.\"", "home_friends")])
node("home_friends", "Dunstan goes a bit pink and pretends to be very interested in Big Margaret's hilt.\n\n\"...¡Vamos!\" he says, to nobody "
                     "in particular, and swings the sword in delight. It takes him three steps across the square.", [("\"¡Vamos!\"", "root")])
save("content/dialogue/chapter_zero_dialogue.json", D)

# ------------------------------------------------------------------ the mate item
C = load("content/items/consumables_and_books.json")
C["items"].append({"id": "core:item.dunstan_mate", "name_key": "item.dunstan_mate.name", "description_key": "item.dunstan_mate.description",
                   "category": "consumable", "icon": "assets/ui/items/dunstan_mate.png", "world_model": "assets/models/items/potion_flask.glb",
                   "slots": [], "stackable": True, "value": 15, "weight": 0.2,
                   "effects": [{"type": "consumable_heal", "amount": 10}, {"type": "buff", "stat": "stamina_regen", "value": 6.0, "duration": 300}]})
save("content/items/consumables_and_books.json", C)
S["item.dunstan_mate.name"] = "Mate (Dunstan's)"
S["item.dunstan_mate.description"] = ("Dried yerba from the Eastern Shore, a gift from Dunstan. Hot, grassy, bitter, and then somehow good. "
                                      "Restores a little health, and for 5 minutes your stamina comes back much faster. Best shared. "
                                      "Don't stir the bombilla.")

# ------------------------------------------------------------------ companion lines and banter
N = load("content/npcs/core_npcs.json")
du = next(n for n in N["npcs"] if n["id"] == "core:npc.dunstan")
c = du["companion"]


def add(group, texts, start):
    keys = []
    for i, t in enumerate(texts, start):
        text, cond = (t, {}) if isinstance(t, str) else t
        k = f"comp.dunstan.{group}.{i}"
        S[k] = text
        keys.append((k, cond))
    return keys


c["idle_lines"] += [dict({"text_key": k}, **cd) for k, cd in add("idle", [
    "Mate break? A quick one. You can't fight properly without mate. That's science.",
    "Back home it's Sunday. Somebody's lighting the fire for the asado right now. I can almost smell it.",
    "My grandmother says I should come home and stop dragging that sword around. I write back: never. Then I send her a drawing of Big Margaret.",
    "The sky here is grey a lot. Back home it's grey too, sometimes. But a warmer grey.",
    ("Eranu, want some mate? It's tradition! You can't say no to tradition!", {"flag": "eranu_following"})], 8)]
c["combat_lines"] += [k for k, _ in add("combat", ["¡Vamos!", "¡Dale, dale, dale!", "¡Vamos, Big Margaret!"], 5)]
c["kill_lines"] += [k for k, _ in add("kill", ["¡GOLAZO! ...Sorry. Old habit.", "¡Dale! Did you see that?!"], 4)]
c["level_lines"] += [k for k, _ in add("level", ["¡Vamos! Look at you! This calls for an asado!"], 3)]
c["heal_lines"] += [k for k, _ in add("heal", ["Here, drink some mate. All of it, till it gurgles. You'll feel better, I promise."], 4)]
S["comp.dunstan.zone.saltmere"] = "Smells like the port back home! Sea, fish, and somebody grilling something somewhere."


def bant(bid, partner, convo):
    ls = []
    for i, (by, t) in enumerate(convo):
        k = f"comp.dunstan.banter.{bid}.{i}"
        S[k] = t
        ls.append({"by": "self" if by == "DUNSTAN" else "partner", "text_key": k})
    c["banter"].append({"id": f"dunstan_{bid}", "partner": P[partner], "lines": ls})


bant("mate_eranu", "eranu", [("DUNSTAN", "Eranu! Mate?"), ("ERANU", "Go on, then."), ("ERANU", "...It's like drinkin' a hot lawn."),
                             ("DUNSTAN", "That's the best part!"), ("ERANU", "Aye. Aye, it kind o' is. Gie's another.")])
bant("mate_coth", "coth", [("COTH", "Is that bark tea?"), ("DUNSTAN", "It's mate! Yerba! From the Eastern Shore!"), ("COTH", "So... bark tea."),
                           ("DUNSTAN", "It's NOT- ...okay, it's a bit like bark tea."), ("COTH", "I knew it. I'm a connoisseur.")])
bant("mate_grout", "grout", [("DUNSTAN", "Grout, want some mate?"), ("GROUT", "Stone doesn't drink."), ("DUNSTAN", "More for me, then!"),
                             ("GROUT", "...Pass it here.")])
bant("asado_baggy", "baggy", [("BAGGY", "Dunstan, what exactly is an asado?"), ("DUNSTAN", "A fire, a grill, and the whole family for three hours."),
                              ("BAGGY", "Three hours? What happens in three hours?"), ("DUNSTAN", "Everybody becomes friends. It's the law."),
                              ("BAGGY", "...Can I come?"), ("DUNSTAN", "You're already invited!")])
save("content/npcs/core_npcs.json", N)
S["tip.50"] = "If Dunstan offers you mate, drink it all until it gurgles. And only say thank you when you're finished."

loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

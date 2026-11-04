#!/usr/bin/env python3
"""Writes a voice script (docs/VOICE_SCRIPT_<NAME>.md) for one or more characters, straight from the game's data:
every line they say, with the exact file name to save the recording as.

    python3 tools/write_voice_script.py eranu coth          # NPC ids without the 'core:npc.' prefix
    python3 tools/write_voice_script.py coth coth_castaway --name coth

Recordings go in assets/audio/voice/<file name>.ogg (or .wav / .mp3); the game plays them with the subtitle
(ResourceManager::PlayVoice). Lines without a recording just show as text, so they can be recorded a few at a time.
"""
import argparse
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = json.load(open(os.path.join(ROOT, "content/localization/en.json")))["strings"]
NPCS = {n["id"]: n for n in json.load(open(os.path.join(ROOT, "content/npcs/core_npcs.json")))["npcs"]}
DLG = {d["id"]: d for d in json.load(open(os.path.join(ROOT, "content/dialogue/chapter_zero_dialogue.json")))["dialogues"]}


def name_of(npc_id):
    n = NPCS.get(npc_id)
    return L.get(n["name_key"], npc_id) if n else npc_id


SPEAKER_NAMES = {L.get(n["name_key"], "") for n in NPCS.values()} - {""}


def quotes(text, speaker):
    """The spoken parts of a dialogue node (the narration around them is shown, not read). A paragraph whose narration
    names someone else ("Eranu, without looking up: ...") is that person's line, so it's left out."""
    out = []
    for para in text.split("\n\n"):
        narration = re.sub(r'"[^"]*"', "", para)
        others = [nm for nm in SPEAKER_NAMES if nm != speaker and re.search(r"\b%s\b" % re.escape(nm), narration)]
        if others and not re.search(r"\b%s\b" % re.escape(speaker), narration):
            continue
        out += [q.strip().rstrip(",") for q in re.findall(r'"([^"]+)"', para)]
    return out


def lines_for(npc_id):
    n = NPCS[npc_id]
    who = name_of(npc_id).upper()
    sections = []
    barks = [(b["text_key"], L.get(b["text_key"], "")) for b in n.get("barks", [])]
    if barks:
        sections.append(("Barks (said to passers-by)", barks))
    d = DLG.get(n.get("dialogue_id", ""))
    if d:
        rows = []
        for nid, node in d["nodes"].items():
            if L.get(node.get("speaker_key", ""), "") != L.get(n["name_key"], ""):
                continue
            q = quotes(L.get(node["text_key"], ""), L.get(n["name_key"], ""))
            if q:
                rows.append((node["text_key"], " … ".join(q)))
        if rows:
            sections.append(("Conversation (record only the spoken words; the game plays it when the page opens. If a page also has someone else's words, skip those)", rows))
    c = n.get("companion")
    if c:
        groups = [("Walking and chatting (random)", [x["text_key"] for x in c.get("idle_lines", [])]),
                  ("In a fight", c.get("combat_lines", [])), ("After a kill", c.get("kill_lines", [])),
                  ("Healing you", c.get("heal_lines", [])), ("When you level up", c.get("level_lines", [])),
                  ("Catching up with you", c.get("catchup_lines", [])),
                  ("First time in each area", list(c.get("zone_lines", {}).values()))]
        for title, keys in groups:
            if keys:
                sections.append((title, [(k, L.get(k, "")) for k in keys]))
    return who, sections


def banter_for(npc_ids):
    """Banter scenes this character is in (their own and other companions'), with every line, so the scene reads
    like a script; only the lines marked with the character's name need recording."""
    scenes = []
    for owner in NPCS.values():
        comp = owner.get("companion") or {}
        for b in comp.get("banter", []):
            if owner["id"] not in npc_ids and b["partner"] not in npc_ids:
                continue
            rows = []
            for ln in b["lines"]:
                speaker = owner["id"] if ln["by"] == "self" else b["partner"]
                rows.append((ln["text_key"], name_of(speaker).upper(), L.get(ln["text_key"], ""), speaker in npc_ids))
            scenes.append((name_of(owner["id"]), name_of(b["partner"]), rows))
    return scenes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("npcs", nargs="+")
    ap.add_argument("--name", help="output name (default: the first NPC)")
    ap.add_argument("--about", default="", help="a line about the character, for the reader")
    args = ap.parse_args()
    ids = ["core:npc." + x for x in args.npcs]
    for i in ids:
        if i not in NPCS:
            raise SystemExit(f"unknown NPC {i}")
    title = name_of(ids[0])
    out = [f"# {title}: voice script\n",
           f"Every line {title} says in the game, ready to read aloud. Save each recording as "
           "`assets/audio/voice/<file name>.ogg` (or `.wav` / `.mp3`), using the file name in the left column. The game "
           "plays it along with the subtitle. Lines without a recording just show as text, so record as many or as few as "
           "you like, a few at a time.\n",
           "**How to record (no studio needed):** a phone or headset is fine. A quiet room (a wardrobe full of clothes is a "
           "famous trick), a hand's width from the mic, and half a second of silence at the end. Mono, 44.1 or 48 kHz. Have "
           "fun with it: shouting, laughing and ad-libs are all welcome.\n"]
    if args.about:
        out.append(args.about + "\n")
    total = 0
    for npc in ids:
        who, sections = lines_for(npc)
        for stitle, rows in sections:
            out.append(f"\n## {stitle}" + (f": {L.get(NPCS[npc]['title_key'], '')}" if len(ids) > 1 else "") + "\n")
            out.append("| File name | Line |")
            out.append("|---|---|")
            for k, text in rows:
                out.append(f"| `{k}` | {who}: {' '.join(text.split())} |")
                total += 1
    scenes = banter_for(ids)
    if scenes:
        out.append("\n## Banter with the party\n")
        out.append("Little scenes between companions. Only the **bold** lines are this character's to record; the others are "
                   "there so the scene reads naturally (or record them together with a friend!).\n")
        for a, b, rows in scenes:
            out.append(f"\n**{a} & {b}**\n")
            out.append("| File name | Line |")
            out.append("|---|---|")
            for k, who, text, mine in rows:
                line = f"{who}: {' '.join(text.split())}"
                out.append(f"| `{k}` | **{line}** |" if mine else f"| `{k}` | {line} |")
                total += int(mine)
    name = (args.name or args.npcs[0]).upper()
    path = os.path.join(ROOT, "docs", f"VOICE_SCRIPT_{name}.md")
    open(path, "w").write("\n".join(out) + "\n")
    print(f"Wrote docs/VOICE_SCRIPT_{name}.md: {total} lines to record")


if __name__ == "__main__":
    main()

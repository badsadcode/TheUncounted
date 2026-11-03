"""The Audit: a challenge arena for showing off builds. Oakhaven can send you to the Audit Chamber, where Senior Auditor
Prudence Vell audits your existence in ten waves (the engine runs it: "start_audit", "stop_audit", "show_audit_records"
dialogue actions). Passing earns the Certificate of Existence (Audited).

ARCHIVE: one-off, already ran. Do NOT rerun."""
import json

def load(p): return json.load(open(p))
def save(p, d): open(p, "w").write(json.dumps(d, indent=2, ensure_ascii=False))
S = {}
I = lambda n: f"core:item.{n}"
D = load("content/dialogue/chapter_zero_dialogue.json")
DL = {d["id"]: d for d in D["dialogues"]}

# Oakhaven: the way in
oak = DL["core:dialogue.clerk_oakhaven"]
root = oak["nodes"][oak["root_node"]]
end = next(i for i, c in enumerate(root["choices"]) if c["next"] == "END")
root["choices"].insert(end, {"text_key": "dlg.audit.oak.choice", "next": "audit_offer"})
oak["nodes"]["audit_offer"] = {"speaker_key": "npc.clerk_oakhaven.name", "text_key": "dlg.audit.oak.offer", "choices": [
    {"text_key": "dlg.audit.oak.go", "next": "END", "actions": [{"type": "travel", "spawn": "audit_entry"}]},
    {"text_key": "dlg.audit.oak.later", "next": oak["root_node"]}]}
S.update({
    "dlg.audit.oak.choice": '"Can I be audited?"',
    "dlg.audit.oak.offer": "Oakhaven's eyes light up in a way that's slightly alarming.\n\n\"An AUDIT. A voluntary audit. Nobody has ever asked for one "
                           "voluntarily.\" He's already writing a referral. \"The Audit Chamber is through the back, down the stairs, past the door "
                           "marked 'NOT THAT ONE'. Senior Auditor Vell will examine your existence in ten stages. If you pass, you'll be the most "
                           "thoroughly alive person in the kingdom.\"\n\n\"It's mostly monsters,\" he adds. \"The Bureau keeps them for the purpose.\"",
    "dlg.audit.oak.go": '"Send me down."',
    "dlg.audit.oak.later": '"Another time."',
})

# The Auditor
D["dialogues"].append({"id": "core:dialogue.auditor", "root_node": "root", "nodes": {}})
au = D["dialogues"][-1]["nodes"]
au["root"] = {"speaker_key": "npc.auditor.name", "text_key": "dlg.audit.root", "choices": [
    {"text_key": "dlg.audit.begin", "next": "begin"},
    {"text_key": "dlg.audit.records", "next": "END", "actions": [{"type": "show_audit_records"}]},
    {"text_key": "dlg.audit.forms", "next": "forms"},
    {"text_key": "dlg.audit.abandon", "next": "END", "actions": [{"type": "stop_audit"}]},
    {"text_key": "dlg.audit.leave", "next": "END"}]}
au["begin"] = {"speaker_key": "npc.auditor.name", "text_key": "dlg.audit.begin_text", "choices": [
    {"text_key": "dlg.audit.begin_go", "next": "END", "actions": [{"type": "start_audit"}]},
    {"text_key": "dlg.audit.begin_not", "next": "root"}]}
au["forms"] = {"speaker_key": "npc.auditor.name", "text_key": "dlg.audit.forms_text", "choices": [{"text_key": "dlg.audit.forms_back", "next": "root"}]}
S.update({
    "dlg.audit.root": "Behind a tall desk on a dais sits a woman with a pen behind each ear and one in her hand, in a black Bureau coat with silver "
                      "buttons. A brass plate: PRUDENCE VELL, SENIOR AUDITOR OF EXISTENCE.\n\n\"Name. Purpose. Proof.\" She looks up. \"Ah. "
                      "Oakhaven's referral. The one who was dead.\" A tick on a list. \"You're here to be audited.\"",
    "dlg.audit.begin": '"Audit me."',
    "dlg.audit.begin_text": "\"Ten stages. At each one, the Bureau's examiners will test whether you continue to exist. They are monsters. "
                            "The Bureau keeps them for the purpose.\"\n\n\"Each stage has a Form. Read the Form. The Form applies whether you read it "
                            "or not.\" She dips the pen. \"If you fall, you are not dead. You are FAILED, and I write down how far you got. "
                            "Everyone's results are kept. Forever. On that wall.\"\n\n\"Ready?\"",
    "dlg.audit.begin_go": '"Begin the audit."',
    "dlg.audit.begin_not": '"Not yet."',
    "dlg.audit.records": '"Show me the records."',
    "dlg.audit.forms": '"What are the Forms?"',
    "dlg.audit.forms_text": "\"Form 1: Standard. Form 12-B: Reinforced, the examiners are sturdier. Form 3: Aggravated, they hit harder. Form "
                            "4-A: Expedited, they're faster. Form 19: Bulk Processing, more of them, slightly flimsier. Form 7: Refund, double "
                            "pay for the stage. Form 22: Rest Break, you get some health back.\"\n\n\"Stage five is supervised by a "
                            "Repossession Golem. Stage ten is supervised by... senior management.\" She doesn't elaborate.",
    "dlg.audit.forms_back": '"Understood."',
    "dlg.audit.abandon": '"I\'d like to stop the audit." (if one is running)',
    "dlg.audit.leave": "Leave.",
    "npc.auditor.name": "Prudence Vell", "npc.auditor.title": "Senior Auditor of Existence",
    "bark.auditor.0": "Next. NEXT.", "bark.auditor.1": "Your existence is noted. Provisionally.",
    "map.audit_chamber.name": "The Audit Chamber",
})
save("content/dialogue/chapter_zero_dialogue.json", D)

N = load("content/npcs/core_npcs.json")
N["npcs"].append({"id": "core:npc.auditor", "name_key": "npc.auditor.name", "title_key": "npc.auditor.title", "faction": "core:faction.bureau",
                  "dialogue_id": "core:dialogue.auditor",
                  "appearance": {"type": "sprite_8dir", "sprite_sheet": "assets/sprites/npcs/auditor.png",
                                 "animation_data": "assets/animations/npc_standard.json", "scale": 1.8},
                  "barks": [{"text_key": "bark.auditor.0"}, {"text_key": "bark.auditor.1"}]})
save("content/npcs/core_npcs.json", N)

A = load("content/items/armor_and_gear.json")
A["items"].append({"id": I("certificate_of_existence"), "name_key": "item.certificate_of_existence.name",
                   "description_key": "item.certificate_of_existence.description", "category": "accessory",
                   "icon": "assets/ui/items/certificate_of_existence.png", "world_model": "assets/models/items/form_27b_scroll.glb",
                   "slots": ["accessory"], "value": 600, "weight": 0.1,
                   "effects": [{"type": "stat_bonus", "stat": "endurance", "amount": 1}, {"type": "stat_bonus", "stat": "presence", "amount": 1},
                               {"type": "bonus", "stat": "armor_bonus", "value": 2.0}, {"type": "bonus", "stat": "crit_chance_bonus", "value": 0.03}]})
S["item.certificate_of_existence.name"] = "Certificate of Existence (Audited)"
S["item.certificate_of_existence.description"] = ("Signed by Senior Auditor Vell, stamped nine times, and laminated in something that isn't quite wax. It "
                                                  "certifies that the bearer exists, thoroughly. Being officially real is good for you: tougher, more "
                                                  "convincing, and slightly luckier.")
save("content/items/armor_and_gear.json", A)
S["tip.48"] = "Ask Clerk Oakhaven for an audit: ten waves, a Form each, and a record of every run, build and all."
loc = load("content/localization/en.json"); loc["strings"].update(S); save("content/localization/en.json", loc)
print("ok", len(S))

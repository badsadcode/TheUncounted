# Grout: voice script

Every line Grout says, in read-aloud script format. You can read them live on stream as they pop up as subtitles,
or record them: save each one as `assets/audio/voice/<file name>.ogg` (or `.wav` / `.mp3`) and the game plays
your recording with the subtitle. Lines without a recording just show as text, so you can record a few at a time.

**Grout:** a squat, mossy stone gargoyle. Grumpy. Few words. Every line is short and dry; the pause is part of it.
Two hundred years on the Records Office roof, until the Bureau classified Grout as 'a fixture, not a citizen'.

Tip: record in a quiet room, a little closer to the mic than normal, and leave half a second of silence at the end.
Mono, 44.1 or 48 kHz. Any line key in the game works the same way, so this also works for other characters.

## When Grout joins, walks, chats (random, every minute or two)

| File name | Line |
|---|---|
| `comp.grout.idle.1` | GROUT: Hm. |
| `comp.grout.idle.2` | GROUT: Walking. Great. Love walking. |
| `comp.grout.idle.3` | GROUT: Stone doesn't get tired. Stone gets bored. |
| `comp.grout.idle.4` | GROUT: Two hundred years on a roof. This is worse. |
| `comp.grout.idle.5` | GROUT: You're doing the thing where you look at everything. Stop it. |
| `comp.grout.idle.6` | GROUT: ...No. Nothing. Keep going. |
| `comp.grout.idle.7` | GROUT: If anyone asks, I'm decorative. |
| `comp.grout.idle.8` | GROUT: Rain's nice. Don't tell anyone. |
| `comp.grout.idle.9` | GROUT: Your bag. Too much stuff. Drop the spoon. |
| `comp.grout.idle.10` | GROUT: I'm not lost. You're lost. |
| `comp.grout.idle.11` | GROUT: The detective talks a lot. *(after: baggy_following)* |
| `comp.grout.idle.12` | GROUT: Rain stopped. Shame. *(after: seal_renewed)* |
| `comp.grout.idle.13` | GROUT: That witch set fire to my bucket. Respect. *(after: sabrino_in_town)* |
| `comp.grout.idle.14` | GROUT: The owlbear. Brave. Stupid. Brave. *(after: fig3_done)* |
| `comp.grout.idle.15` | GROUT: Fixtures. Us. Hm. Good team. *(after: grout_kin)* |
| `comp.grout.idle.16` | GROUT: A horse on a roof. Amateur. Try two hundred years. *(after: trout_case)* |

## First time in each area

| File name | Line |
|---|---|
| `comp.grout.zone.bellwether` | GROUT: Home. Roof's that way. Don't look at it. |
| `comp.grout.zone.old_road` | GROUT: Road. Long. Dusty. Great. |
| `comp.grout.zone.annex` | GROUT: Bureau basement. Smells like forms. |
| `comp.grout.zone.vault_three` | GROUT: Old stone in here. Older than me. Show-offs. |
| `comp.grout.zone.seal_chamber` | GROUT: Don't touch anything. ...You're going to touch something. |
| `comp.grout.zone.hollowmere` | GROUT: Haunted house. Course it is. |
| `comp.grout.zone.hollowmere_manor` | GROUT: Good ceilings. Good roof. I'd perch there. |
| `comp.grout.zone.saltmere` | GROUT: Fish. Everywhere. Fish. |
| `comp.grout.zone.sunken_chapel` | GROUT: Underwater church. Stone hates water. I hate water. |
| `comp.grout.zone.whistling_wood` | GROUT: Trees. Whistling. Make it stop. |
| `comp.grout.zone.sleepers_reef` | GROUT: I sink. Remember that. I sink. |

## A fight starts

| File name | Line |
|---|---|
| `comp.grout.combat.1` | GROUT: Finally. |
| `comp.grout.combat.2` | GROUT: Mine. |
| `comp.grout.combat.3` | GROUT: Hold still. |
| `comp.grout.combat.4` | GROUT: Here we go. |
| `comp.grout.combat.5` | GROUT: Stand back. |

## A fight ends

| File name | Line |
|---|---|
| `comp.grout.kill.1` | GROUT: Done. |
| `comp.grout.kill.2` | GROUT: Next. |
| `comp.grout.kill.3` | GROUT: Stayed down. Good. |
| `comp.grout.kill.4` | GROUT: That was it? |

## Hands you food when you're badly hurt

| File name | Line |
|---|---|
| `comp.grout.heal.1` | GROUT: Eat. Don't argue. |
| `comp.grout.heal.2` | GROUT: Bread. Found it. Don't ask where. |
| `comp.grout.heal.3` | GROUT: You're leaking. Fix that. |

## You level up

| File name | Line |
|---|---|
| `comp.grout.level.1` | GROUT: Stronger. Barely. |
| `comp.grout.level.2` | GROUT: Huh. Progress. |

## Catching up after being left behind

| File name | Line |
|---|---|
| `comp.grout.catchup.1` | GROUT: Door. Closed. In my face. |
| `comp.grout.catchup.2` | GROUT: You left. I noticed. |
| `comp.grout.catchup.3` | GROUT: Stairs. Hate stairs. |
| `comp.grout.catchup.4` | GROUT: Here. Don't do that again. |

## Passing by (before Grout joins)

| File name | Line |
|---|---|
| `bark.grout.1` | GROUT: What. |
| `bark.grout.2` | GROUT: Move along. |

## Conversation (when you talk to Grout)

The file name plays when that page of the conversation opens. Narration (the bits not in quotes) can be left out.

**`dlg.grout.root`**

> A squat stone gargoyle sits on an upturned bucket beside the Records Office door, arms folded, glaring at the rain. Moss on the shoulders. One horn chipped.
>
> The gargoyle looks at you. Keeps looking.
>
> "What."

**`dlg.grout.who`**

> "Grout."
>
> A long pause.
>
> "Gargoyle. Records Office roof. Two hundred years." Another pause. "Then the Bureau did an inventory."

**`dlg.grout.fixture`**

> "Classified me. 'Fixture. Not citizen.' Same form as the gutters."
>
> A stone thumb jabs at the roof.
>
> "Gutters kept their job."

**`dlg.grout.same`**

> Grout looks at you properly for the first time.
>
> "Huh."
>
> That's it. That's the whole reaction. Somehow it feels like a lot.

**`dlg.grout.join`**

> "No."
>
> Grout stands up anyway. The bucket stays dented.
>
> "Somebody's got to hit things. You look like you'd talk to them."

**`dlg.grout.full`**

> Grout looks past you at your companions.
>
> "Too many people." Arms fold. "Hate crowds."

**`dlg.grout.wait`**

> "Fine."
>
> Grout sits down exactly where Grout is standing.
>
> "Don't be long. Or do. Whatever."

**`dlg.grout.advice`**

> "Hit first."
>
> "Hit hard."
>
> "Don't explain yourself."
>
> A pause.
>
> "That's it. That's all the advice."

**`dlg.grout.like`**

> "Rain. Quiet. Pigeons."
>
> Grout considers.
>
> "Not the pigeons."

## Banter with Baggy and Kaelen

Only Grout's lines need recording (the other parts are someone else's), but here's the whole exchange.

**Banter (baggy_story)**

- *BAGGY: So, Grout! What's your story? Every gargoyle has a story.*
- `comp.grout.banter.baggy_story.1` **GROUT:** No.
- *BAGGY: Mysterious! I like it.*
- `comp.grout.banter.baggy_story.3` **GROUT:** Not mysterious. Just no.
**Banter (baggy_masks)**

- *BAGGY: Grout, have you ever unmasked a monster?*
- `comp.grout.banter.baggy_masks.1` **GROUT:** Punched one.
- *BAGGY: Did it turn out to be someone in a mask?*
- `comp.grout.banter.baggy_masks.3` **GROUT:** Did after.
**Banter (baggy_barely)**

- *BAGGY: I barely knew her!*
- `comp.grout.banter.baggy_barely.1` **GROUT:** Who?
- *BAGGY: Nobody. It's just a thing I say.*
- `comp.grout.banter.baggy_barely.3` **GROUT:** Stop.
**Banter (kaelen_roof)**

- *KAELEN: Two hundred years on that roof. You must have seen everything.*
- `comp.grout.banter.kaelen_roof.1` **GROUT:** Pigeons.
- *KAELEN: And?*
- `comp.grout.banter.kaelen_roof.3` **GROUT:** More pigeons.
**Banter (kaelen_chronicle)**

- *KAELEN: I'm writing a chronicle of this journey. Anything you want recorded?*
- `comp.grout.banter.kaelen_chronicle.1` **GROUT:** Hit things.
- *KAELEN: ...I'll paraphrase.*

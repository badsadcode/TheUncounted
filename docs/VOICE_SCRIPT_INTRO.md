# The intro: narration script (BadSad)

The opening of a new game: a few still pictures with a line of text along the bottom. Record each card as `assets/audio/voice/<file name>.ogg` (or `.wav` / `.mp3`). When a card has a recording, the game plays it and turns to the next card by itself about a second after it ends, so the intro plays like a short film. Cards without a recording wait for a click, as now.

**Tone:** a storyteller by the fire, calm and a little dry: the joke is that something absurd (you've been declared dead and billed for your own funeral) is told completely seriously. Take your time; pauses are good. A quiet room, a hand's width from the mic, half a second of silence at the start and the end.

| File name | Read |
|---|---|
| `story.prologue.1` | Edrath, in the four hundred and twelfth year after the Great Silence. The kingdoms keep their ledgers carefully now. What is written down, exists. What is struck out was never there at all. |
| `story.prologue.2` | Seventeen years ago, by order of the Royal Bureau of Records, you died. You do not remember it. Nobody does. That is rather the point of a ledger. |
| `story.prologue.3` | This morning a notice arrived anyway, sealed in Bureau wax: proof of your death, and a bill for your burial. |
| `story.prologue.4` | So you have walked to Bellwether, where the rain never quite stops, to argue with a clerk about whether you are alive. |

To change the words, edit these lines in `content/localization/en.json` (keys `story.prologue.1` …); adding `story.prologue.5` adds a fifth card (with `assets/ui/intro/intro_5.png` as its picture).

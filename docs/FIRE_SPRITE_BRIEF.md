# Brief for Noor: fireplace fire animation

**Done**: Noor delivered `fire_flames.png`, `fire_flames_small.png` and `fire_flames_magic.png` (originals in
`art_source/fire/`). They are the palette pieces `fire_embers`, `fire_embers_small` and `fire_embers_magic`.

One animated sprite sheet: the flames of a fire in a fireplace, a forge or under a cooking pot. The game shows it
standing on a bed of glowing embers (a small 3D model), always facing the camera, at full brightness and with a warm
light around it. (Torches keep their own small flame: this is only for the bigger fires.)

## The file

- **Name**: `fire_flames.png` (it replaces the placeholder at `assets/sprites/vfx/fire_flames.png`).
- **Layout**: one horizontal row of **square frames**, left to right, no gaps, no padding. The game counts frames as
  width ÷ height, so every frame must be exactly square.
- **Frames**: **8 to 12**. The game plays them at **10 frames per second**, looping, so the last frame must lead back
  into the first without a jump.
- **Frame size**: **64 × 64 px** (128 × 128 is fine too if you want more detail; keep the chunky pixel look either way).
  Example: 8 frames of 64 px = a 512 × 64 image.
- **Background**: transparent.

## How it's drawn (what matters for the art)

- **Hard edges only.** Every pixel is either fully opaque or fully transparent: the game drops anything under 50 %
  opacity, so soft glows, blurred edges and see-through smoke disappear. Do the glow with colour (bright core, darker
  edges), not transparency.
- **Full brightness, no shading from the scene.** Draw the flames as bright as they should look; night doesn't darken
  them.
- **The bottom of the frame is the bottom of the fire.** Flames should start at (or just above) the bottom edge and
  fill the width there, so they sit on the embers with no gap. Let the tips reach about 2/3 to the full height and
  vary between frames.
- **It's shown about 0.7 m wide** (bigger when the fire is scaled up for a forge), so think "a fireplace fire seen
  from a few metres away": 3 to 6 tongues of flame, not a single candle flame.

## Style

Same painted pixel-art feel as your other sprites. Colours from a white-yellow core through orange to deep red at the
tips and edges; a few loose sparks or flickers above the flames are welcome (as solid pixels). The placeholder in the
game today shows the size and placement; yours replaces it one-for-one.

## Nice to have (optional)

- `fire_flames_small.png`: the same in a smaller, calmer version for under a cooking pot.
- A blue/green "magic fire" recolour for spooky places (same layout).

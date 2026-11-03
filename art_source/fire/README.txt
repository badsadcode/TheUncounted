THE UNCOUNTED: FIRE ANIMATIONS

assets/sprites/vfx/fire_flames.png: main fireplace/forge fire
assets/sprites/vfx/fire_flames_small.png: calmer cooking fire
assets/sprites/vfx/fire_flames_magic.png: blue-green magic fire

Every PNG is 640 x 64 pixels: TEN 64 x 64 square frames in ONE horizontal row, no frame spacing or atlas padding. Play left to right at 10 FPS, loop enabled, one second per cycle.

All alpha values are exactly 0 or 255. Flame bases touch the bottom edge in every frame. Use nearest-neighbour filtering, unlit/full-bright billboard rendering, and your existing warm light/ember-bed model. No ember or log artwork is baked into the flame frames.

The previews folder contains a looping GIF comparison and first-frame preview composited over a dark background; these preview backgrounds are not part of the production textures.

Artwork was generated with image generation, then exported from an intermediate 5 x 2 layout into the requested strip. Export uses nearest-neighbour sampling, binary alpha, stray-fragment cleanup, bottom anchoring and a consistent color palette. The loop preview was reviewed outside the game renderer.

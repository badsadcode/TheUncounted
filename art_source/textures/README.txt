THE UNCOUNTED: PIXEL-ART WORLD TEXTURES

42 separate game PNG assets using the exact filenames from the brief.

textures/: 33 opaque surface textures, each 128 x 128 pixels.
sky/: 2 opaque panoramas, each 1024 x 256 pixels; intended to repeat horizontally only.
scatter/: 7 transparent billboard cut-outs, each 64 x 64 pixels.
previews/: material overview, scatter overview, and sample 3 x 3 material repeats; these are reference images, not game textures.

Use nearest-neighbour filtering for crisp pixels. Use repeat wrapping on materials and horizontal repeat on skies. Cut-outs retain their generated alpha channel. The cobweb is intended for a ceiling corner, not a ground scatter placement. Existing debugging texture diag_missing.png is not included.

Artwork was generated individually with image generation, then exported to the required dimensions using nearest-neighbour resizing and compact palettes. Surface midtones were balanced for nighttime lighting. All opaque assets use at most 32 colors. No PBR maps are included; these are color/albedo assets. Sample repeat previews were inspected, but textures have not been tested inside the game renderer.

asset_index.json records the output dimensions and checksums. Full art-generation prompts are included in generation_prompts.json.

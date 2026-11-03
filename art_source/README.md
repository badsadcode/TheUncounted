# Source art

Original hand-painted sprite sheets (8 columns = directions, 6 rows = idle, walk A, walk B, windup, attack,
stagger/corpse; black background). The game uses the converted 128 px sheets in `assets/sprites/`, made with
`tools/import_spritesheet.py`. Keep the originals here so the conversion can be redone or improved.

| Original | In-game sheet | Used by |
|---|---|---|
| `spritesheets/grave_rat.webp` | `assets/sprites/enemies/grave_rat_painted.png` | Grave Rat |
| `spritesheets/skeleton.webp` | `assets/sprites/enemies/skeleton_painted.png` | Restless Skeleton |
| `spritesheets/crypt_keeper.webp` | `assets/sprites/enemies/crypt_keeper_painted.png` | Crypt Keeper |
| `spritesheets/lullaby_warden.webp` | `assets/sprites/enemies/lullaby_warden_painted.png` | The Lullaby Warden |
| `spritesheets/ash_crawler.webp` | `assets/sprites/enemies/ash_crawler_painted.png` | Ash Crawler |
| `spritesheets/kaelen_ashbound_scout.webp` | `assets/sprites/npcs/ashbound_scout_painted.png` | Kaelen |
| `spritesheets/brother_aldous.webp` | `assets/sprites/npcs/brother_aldous_painted.png` | Brother Aldous |
| `spritesheets/clerk_oakhaven.webp` | `assets/sprites/npcs/clerk_oakhaven_painted.png` | Clerk Oakhaven |
| `spritesheets/erased_spirit.webp` | `assets/sprites/npcs/erased_spirit_painted.png` | The Erased Spirit |
| `spritesheets/innkeeper_marta.webp` | `assets/sprites/npcs/innkeeper_marta_painted.png` | Marta |
| `spritesheets/librarian_fenwick.webp` | `assets/sprites/npcs/librarian_fenwick_painted.png` | Fenwick |
| `spritesheets/merchant_vaelen.webp` | `assets/sprites/npcs/merchant_vaelen_painted.png` | Vaelen |
| `spritesheets/bone_clerk.webp` | `assets/sprites/enemies/bone_clerk_painted.png` | Bone Clerk |
| `spritesheets/critic_mortimer.webp` | `assets/sprites/npcs/critic_mortimer_painted.png` | Mortimer Quill |
| `spritesheets/detective_baggy.webp` | `assets/sprites/npcs/detective_baggy_painted.png` | Baggy |
| `spritesheets/dreaming_limb.webp` | `assets/sprites/enemies/dreaming_limb_painted.png` | The Dreaming Limb |

Re-convert one (example; `--match` keeps the in-game size equal to the old generated sheet, `--match-col` picks the
idle column used for that comparison: 0 for upright figures, 2 for side-on animals):

```bash
python tools/import_spritesheet.py art_source/spritesheets/clerk_oakhaven.webp assets/sprites/npcs/clerk_oakhaven_painted.png --frame 128 --match assets/sprites/npcs/clerk_oakhaven.png --match-col 0
```

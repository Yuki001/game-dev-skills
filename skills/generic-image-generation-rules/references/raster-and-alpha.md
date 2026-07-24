# Raster and alpha workflow

## Delivery defaults

Unless the engine/user specifies otherwise:

- deliver lossless PNG for sprites, UI, icons, VFX, and transparent props;
- use sRGB color data;
- preserve straight alpha in source assets;
- avoid indexed PNG when downstream tooling handles it inconsistently;
- keep a high-resolution working source when final assets are small;
- downsample once with an appropriate filter; use nearest-neighbor for pixel art.

Confirm engine-specific premultiplied-alpha, texture compression, mipmap, and color-space settings rather than guessing.

These alpha defaults do not apply when the black-background additive VFX path is intentionally selected.

## Transparency paths

### A. Native alpha

Request a truly transparent background. After generation, inspect the alpha channel. Models may render a checkerboard or white backdrop while returning fully opaque pixels.

### B. Removable matte

When native alpha is unreliable:

1. choose a flat matte color absent from the subject;
2. avoid contact shadows and ambient color spill unless required;
3. leave safe space around the subject;
4. remove the matte with an image-edit/background-removal path;
5. reconstruct occluded holes and semitransparent edges;
6. inspect over black, white, and a saturated test color.

Green is not always a good matte; use a color far from the subject palette.

### C. Masked edit

Use a mask when the boundary is known or only a local background region should change. State the change and preservation invariants explicitly.

### D. Black-background additive VFX

Use this path for emissive effects such as fire, sparks, magic, glow, and energy when the target engine/material supports additive or alpha-additive blending:

1. generate or retain the effect over intentional pure black;
2. keep the source lossless and avoid lifted blacks, compression blocks, backdrop texture, or non-effect haze;
3. do not run background removal solely to create transparency;
4. declare and verify the engine blend mode—commonly `One, One` or `SrcAlpha, One`, with engine-specific naming;
5. preview through the actual material over dark, light, saturated, and expected gameplay backgrounds;
6. record whether alpha participates in the blend equation.

Black contributes zero under additive blending, so it disappears during composition while bright RGB adds light. This path cannot darken or normally occlude the scene and may wash out on bright backgrounds. Do not use it for smoke, shadows, dark particles, opaque cores, refraction masks, or assets that require ordinary translucency.

## Background-removal capability differences

Distinguish the host tool from the selected model and configuration:

| Route | Capability guidance |
|---|---|
| `rembg` | A background-removal runner with selectable models and optional alpha-matting post-processing. It can output partial alpha; do not classify it as binary-only. Quality depends on the chosen model, alpha-matting settings, and source image. |
| General/DIS BiRefNet weights | High-resolution foreground segmentation with strong fine-boundary reconstruction. A soft-looking mask or clean edge does not guarantee faithful recovery of intrinsic translucency. |
| `BiRefNet-matting` / `BiRefNet_HR-matting` | Matting-specific weights intended for fractional alpha and fine semitransparent structures; prefer these when hair, fur, motion blur, glass-like edges, or soft transparency must survive. |

Probe the exact model/variant, alpha-matting option, mask value range, output mode, and—when processing frames—temporal consistency. Use ordinary segmentation for mostly opaque subjects; use a matting-capable model/configuration when meaningful partial alpha is a hard requirement. For smoke, glow, and other VFX, also consider whether the additive-black path is the correct engine contract instead of forcing a cutout.

## Alpha checks

Check:

- at least some pixels are actually transparent when transparency is required;
- corners and unused padding are transparent;
- internal holes remain transparent;
- antialiased edge pixels have plausible partial alpha;
- no white/dark fringe from the former matte;
- no accidental erasure of thin features;
- RGB values in transparent pixels do not create bleed during filtering/mipmaps;
- shadow policy is intentional.

Use `scripts/inspect_asset.py IMAGE --expect-transparent` for evidence. The script reports alpha availability, transparent/partial pixel counts when decodable, nontransparent bounds, and border transparency.

Do not use `--expect-transparent` as a gate for an intentional additive-black asset. Instead verify pure-black neutrality, clean effect-only RGB, the declared blend equation, and the in-engine composite.

## Edge cleanup

Common fixes:

- decontaminate edge RGB from the old matte;
- expand subject color beneath transparent edge pixels before mipmapping;
- remove isolated alpha speckles;
- preserve soft edges for smoke, hair, fur, glow, and motion blur;
- keep hard edges for pixel art and deliberately crisp UI;
- add padding/extrusion around atlas cells to avoid texture bleeding.

Do not threshold all alpha to binary unless the art direction demands a hard mask.

## Crop and occupied bounds

Record:

- canvas size;
- nontransparent bounding box;
- intended safe margin;
- pivot/origin;
- whether trim is permitted.

Do not auto-trim animation frames independently; that creates visible jitter. Use a shared canvas and stable pivot across the sequence.

## Inspection backgrounds

Review transparency on:

1. black;
2. white;
3. saturated magenta/cyan or the expected game background;
4. checkerboard only as a UI aid, never as image content.

Review at 100% and at the intended display scale.

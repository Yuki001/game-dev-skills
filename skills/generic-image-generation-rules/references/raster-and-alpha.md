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

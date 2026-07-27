# Prompt compilation

Keep a backend-neutral semantic specification as the authoritative source. Compile backend prompts from it so that switching tools does not silently change the asset.

## Semantic prompt schema

Write these blocks in this order:

1. **Deliverable** — asset type, format, canvas, aspect ratio, transparency, sheet/grid requirements.
2. **Usage** — game genre, camera/viewing distance, readability target, engine context.
3. **Subject** — identity, count, silhouette, proportions, pose/action, held items.
4. **Composition** — projection, camera, framing, orientation, occupied bounds, safe margins.
5. **Rendering** — medium, shape language, line treatment, value structure, material.
6. **Lighting and palette** — light direction, contrast, named colors, saturation limits.
7. **Background** — environment or explicit isolation/matte behavior.
8. **Consistency invariants** — identity, costume, scale, camera, palette, text, or topology that must not drift.
9. **Avoid** — only likely failure modes.

Put exact layout and format constraints before decorative detail.

## Native instruction prompt

Use complete, direct clauses. State the canvas and artifact type first. Quote exact visible text. For complex assets, use labeled sections or a JSON-like visual specification.

Example:

```text
Create one game-ready inventory icon on a 512×512 square canvas.
SUBJECT: a chipped obsidian dagger with a wrapped crimson handle, pointing from lower-left to upper-right.
SILHOUETTE: readable at 48 px; blade and hilt clearly separated; no cropped tip.
RENDERING: painterly dark-fantasy icon, hard outer contour, restrained surface detail, cool black stone with a single red accent.
LIGHTING: upper-left key light, cool violet form shadow, narrow warm rim.
BACKGROUND: fully transparent outside the object; no checkerboard, no floor, no cast shadow beyond the object bounds.
AVOID: text, border, duplicate weapon, photoreal product photography.
```

For edits, use:

```text
CHANGE: remove the background and reconstruct clean edge pixels.
PRESERVE: subject identity, pose, proportions, crop, internal holes, colors, lighting, and canvas size.
OUTPUT: true straight-alpha PNG; no white fringe, checkerboard, shadow plate, or added outline.
```

Identify multiple references by index and role. Do not say merely “use these references.”

## Danbooru/SD/ComfyUI compilation

Compile tags from the semantic prompt; do not translate the native prompt word-for-word.

Recommended positive-tag order:

```text
[asset/quality tokens],
[count + subject identity],
[pose/action/expression],
[camera/projection/composition],
[costume/prop/material details],
[environment/background],
[lighting/palette],
[medium/style/rendering],
[technical output tokens]
```

Example:

```text
game asset, inventory icon, 1 weapon, obsidian dagger, chipped blade,
red wrapped handle, diagonal composition, centered, full object,
three-quarter view, strong silhouette, dark fantasy, painterly,
hard rim light, limited palette, isolated object, transparent background
```

Negative prompt:

```text
cropped, out of frame, multiple objects, text, logo, border, pedestal,
busy background, blurry, low contrast silhouette, malformed blade,
white background, checkerboard background
```

Rules:

- Prefer tags known by the selected checkpoint/embedding/LoRA ecosystem. Preserve exact recognized spelling.
- Treat “Danbooru-style” as a comma-separated controlled vocabulary, not a guarantee that every natural-language concept has a tag.
- Keep identity and geometry tags early; put broad style tokens later.
- Use weights sparingly and only with syntax supported by the selected workflow.
- Keep negative prompts targeted. Long generic “bad anatomy” lists can suppress desired features.
- Put sampler, scheduler, CFG, steps, resolution, seed, ControlNet, IP-Adapter, LoRA weights, and denoise strength in backend parameters, not in the semantic prompt.
- If a needed concept has no reliable tag, retain a short natural-language phrase only if the text encoder supports it, or encode it through references/control inputs.
- For pixel art, prompt the visual constraints but enforce exact pixel dimensions, palette, nearest-neighbor scaling, and no antialiasing during post-processing.

## Batch variation

Change named axes, not arbitrary words:

```text
variant A/B: silhouette — narrow / broad
variant C/D: palette — cool violet / oxidized green
variant E/F: camera — strict side / three-quarter
```

Keep the remaining prompt and parameters fixed where the backend allows it. Retain the active prompt differences in context until the comparison is complete.

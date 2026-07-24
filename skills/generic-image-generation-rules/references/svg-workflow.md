# SVG workflow

Use SVG when scalable geometry, editability, clean paths, exact layout, or compact reuse matters. Prefer raster generation for organic painterly assets unless vectorization is explicitly required.

## Workflow

```text
PLAN → BUILD SVG → TEXT-ONLY VALIDATE & REVIEW
                        ├─ placeholder → STOP
                        └─ production → RENDER ONCE → VIEW
                                                        ├─ pass → DELIVER
                                                        └─ defect → REVISE → RENDER/VIEW
```

## 1. Plan

Decide whether SVG is appropriate, then judge its validation level:

- **Placeholder/prototype**: temporary art used to prove layout, interaction, or gameplay. Complete Step 3, then stop without rendering.
- **Production**: explicitly final, official, shippable, release-quality, or promoted from placeholder status. Complete Step 3, then require one successful render/view gate.

Default unclear cases to placeholder. Do not ask the user solely to resolve this judgment.

## 2. Build

Use a predictable structure:

```xml
<svg xmlns="http://www.w3.org/2000/svg"
     viewBox="0 0 512 512"
     role="img"
     aria-labelledby="title desc">
  <title id="title">Asset title</title>
  <desc id="desc">Short description</desc>
  <defs><!-- gradients, filters, masks, symbols --></defs>
  <g id="asset"><!-- visible geometry --></g>
</svg>
```

Prefer:

- a meaningful `viewBox`;
- stable grouping and IDs;
- `<symbol>`/`<use>` for repeated components;
- `vector-effect="non-scaling-stroke"` when stroke width must stay constant;
- explicit filter bounds to prevent clipping;
- paths and shapes over embedded raster data when vector editability matters.

Avoid external fonts, remote images, scripts, or network dependencies unless the target runtime explicitly supports them.

## 3. Code-validate and text-evaluate every SVG

First, run `scripts/inspect_asset.py` and inspect the source for objective validity:

- XML parses and the root element is `<svg>`;
- a valid positive-size `viewBox` or explicit dimensions exist;
- IDs are stable and references such as `<use>`, masks, filters, and clip paths resolve;
- graphic elements exist and numeric geometry is finite;
- no unintended remote images, fonts, scripts, or network dependencies exist;
- naming, canvas, and accessibility conventions are satisfied;
- the target runtime supports deliberately used SVG features.

Then evaluate the SVG shapes only from the SVG code text against the intended asset. This is a subjective semantic check, not another parser check. Reconstruct the likely composition from element types, groups, path data, coordinates, transforms, draw order, fills, and strokes. Judge whether:

- all requested objects and meaningful parts are represented;
- the chosen primitives and paths plausibly describe the intended silhouettes;
- proportions, positions, orientation, spacing, and occupied bounds make sense within the `viewBox`;
- layering and draw order produce the intended foreground/background and occlusion;
- fills, strokes, gradients, and detail density fit the requested visual role;
- no obvious shape is missing, duplicated, disconnected, inverted, or placed outside the useful canvas;
- repeated assets or icon-set elements follow the expected shared geometry conventions.

Do not claim pixel-level visual certainty from text alone. For placeholders, this is the final subjective plausibility gate. For production SVGs, it catches semantic mistakes before the render/view gate.

Fix failures from either the objective validation or the text-only shape review before continuing. Both checks are required for every SVG.

## 4. Stop placeholders after Step 3

When objective code validation and the text-only shape review both pass, stop. Do not render, call vision, or create a PNG preview merely to validate a placeholder.

Keep placeholders simple and retain renderer-dependent uncertainty in the working context when relevant. If a placeholder is later promoted or the user explicitly requests visual QA, continue with the production gate.

## 5. Render-gate production SVGs

Use an available renderer such as a browser, CairoSVG, Inkscape, resvg, or a bundled SVG workflow. Prefer the target runtime's renderer when compatibility matters, and retain the selected renderer in the working context.

Render one PNG preview at the most decision-relevant size, normally the target in-game size or delivery resolution. Add another size or 2× edge preview only to answer a specific unresolved question.

View the preview with vision and check:

- silhouette and detail remain readable at the intended size;
- strokes do not vanish or dominate;
- filters, glows, masks, and shadows are not clipped;
- transparency is intentional;
- gradients, blend modes, fonts, and text layout render correctly;
- related icons share canvas, padding, stroke, palette, and optical size;
- the target runtime supports any animation mechanism used.

If the preview passes, deliver it without forcing another iteration. If a material defect is visible, revise the SVG and repeat the render/view gate until that defect is resolved.

Keep the source SVG and at least one approved preview in the production package.

## Raster-to-SVG conversion

Do not blindly trace a textured raster. Reconstruct clean semantic shapes for icons, UI, decals, and logos. If tracing is used:

- simplify paths;
- remove tiny islands;
- normalize fills and strokes;
- verify holes and winding;
- for a production asset, compare the rendered SVG with the approved raster at the intended size.

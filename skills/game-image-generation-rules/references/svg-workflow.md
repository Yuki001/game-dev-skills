# SVG workflow

Use SVG when scalable geometry, editability, clean paths, exact layout, or compact reuse matters. Prefer raster generation for organic painterly assets unless vectorization is explicitly required.

## Workflow

```text
PLAN → ASK VALIDATION LEVEL → BUILD SVG → TEXT-ONLY VALIDATE & REVIEW
                                               ├─ prototype → STOP
                                               └─ formal → RENDER ONCE → VIEW
                                                                              ├─ pass → DELIVER
                                                                              └─ defect → REVISE → RENDER/VIEW
```

## 1. Plan

Decide whether SVG is appropriate. Before building, use `AskUserQuestion` to let the user choose the validation level:

- **Prototype**: complete Step 3, then stop without rendering or vision evaluation.
- **Formal**: complete Step 3, then require one successful render/view and vision-evaluation gate.

**Auto-mode exception:** if the agent is running in auto mode, skip `AskUserQuestion` and default the validation level to **Prototype**.

Do not infer this choice from terms such as temporary, placeholder, final, production, official, or shippable; the explicit user selection controls whether vision evaluation runs.

For batch SVG generation, ask once at the beginning and apply that selection to the entire batch. Do not ask again for each asset in the batch.

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

First, run `scripts/inspect_svg.py` for basic structural evidence:

- XML parses and the root element is `<svg>`;
- a valid positive-size `viewBox` or explicit dimensions exist;
- IDs are stable and references such as `<use>`, masks, filters, and clip paths resolve;
- graphic elements exist and common numeric geometry, path, and transform attributes have valid finite syntax;
- external resources, scripts, `foreignObject`, or `role="img"` without an accessible name are reported as warnings.

Use `--strict-svg` only when those warnings should fail the current asset contract. Otherwise, inspect the source to decide whether external images, fonts, scripts, naming, accessibility, and deliberately used SVG features are intentional and supported by the target runtime.

Then evaluate the SVG shapes only from the SVG code text against the intended asset. This is a subjective semantic check, not another parser check. Reconstruct the likely composition from element types, groups, path data, coordinates, transforms, draw order, fills, and strokes. Judge whether:

- all requested objects and meaningful parts are represented;
- the chosen primitives and paths plausibly describe the intended silhouettes;
- proportions, positions, orientation, spacing, and occupied bounds make sense within the `viewBox`;
- layering and draw order produce the intended foreground/background and occlusion;
- fills, strokes, gradients, and detail density fit the requested visual role;
- no obvious shape is missing, duplicated, disconnected, inverted, or placed outside the useful canvas;
- repeated assets or icon-set elements follow the expected shared geometry conventions.

Do not claim pixel-level visual certainty or target-runtime compatibility from the script or text alone. For prototype SVGs, this is the final subjective plausibility gate. For formal SVGs, it catches semantic mistakes before the render/view gate.

Fix failures from either the objective validation or the text-only shape review before continuing. Both checks are required for every SVG.

## 4. Stop prototype SVGs after Step 3

When objective code validation and the text-only shape review both pass, stop. Do not render, call vision, or create a PNG preview merely to validate a prototype SVG.

Keep prototype SVGs simple and retain renderer-dependent uncertainty in the working context when relevant. If the user later selects formal validation or explicitly requests visual QA, continue with the formal gate.

## 5. Render-gate formal SVGs

Use an available renderer such as a browser, CairoSVG, Inkscape, resvg, or a bundled SVG workflow. Prefer the target runtime's renderer when compatibility matters, and retain the selected renderer in the working context.

For one SVG, render one PNG preview at the most decision-relevant size, normally the target in-game size or delivery resolution. Add another size or 2× edge preview only to answer a specific unresolved question.

For a formal SVG batch, render the SVGs into a labeled atlas/contact sheet and perform one overall vision evaluation whenever every asset remains readable at its decision-relevant size. This preserves set-wide comparison while reducing repeated vision calls and token use. Use stable IDs, uniform cells, sufficient padding, and a background that makes transparency and edge defects visible. Split the batch into the fewest atlases needed when one atlas would make assets too small or exceed the vision input limits. The atlas does not replace the per-SVG objective validation and text-only shape review from Step 3.

View the preview or atlas with vision and check:

- silhouette and detail remain readable at the intended size;
- strokes do not vanish or dominate;
- filters, glows, masks, and shadows are not clipped;
- transparency is intentional;
- gradients, blend modes, fonts, and text layout render correctly;
- related icons share canvas, padding, stroke, palette, and optical size;
- the target runtime supports any animation mechanism used.

If the preview or atlas passes, deliver without forcing another iteration. If a material defect is visible, revise the affected SVGs and re-evaluate only those assets in a smaller atlas or individual preview. Re-evaluate the full atlas only when the changes could affect batch-wide cohesion.

Keep the source SVGs and the approved individual preview or atlas in the formal package.

## Raster-to-SVG conversion

Do not blindly trace a textured raster. Reconstruct clean semantic shapes for icons, UI, decals, and logos. If tracing is used:

- simplify paths;
- remove tiny islands;
- normalize fills and strokes;
- verify holes and winding;
- for a formal asset, compare the rendered SVG with the approved raster at the intended size.

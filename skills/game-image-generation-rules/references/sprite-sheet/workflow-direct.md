# Direct generation workflow

Use this workflow only when a complete video-generation plus frame-extraction route and a suitable motion-reference sheet are both unavailable. Prompt the selected image backend once for one complete sprite sheet, then use the shared sheet inspection and packaging pipeline.

## Backend request

Put the grid and frame contract before art direction:

```text
Create one strict 8×1 sprite sheet on a 2048×256 canvas.
LAYOUT: eight equal 256×256 cells, left-to-right order, no gutters, no merged cells, one full character per cell.
ACTION: run cycle. Cell 1 contact, 2 down, 3 passing, 4 up, 5 opposite contact, 6 down, 7 passing, 8 up.
CONSISTENCY: same character identity, costume, proportions, palette, side-view orthographic camera, scale, baseline, and light direction in every cell.
RENDERING: [project style].
OUTPUT: transparent outside the character, no labels, borders, guides, floor, camera movement, duplicate poses, or cropped limbs.
```

Derive the exact frame phases from the animation contract or `sprite-animation-presets.md`. If the backend cannot output the requested resolution, preserve the requested aspect ratio, grid, frame count, and order; deterministic post-processing will repack the accepted frames.

## Handoff

Return one generated sheet plus its planned rows, columns, cell size, frame order, timing, loop mode, and alpha/blend contract. Continue with sheet inspection, slicing, sequence evaluation, and packaging in `sprite-sheets.md`.

Direct generation has the weakest temporal control. Reject missing, duplicated, reordered, merged, crossed, or discontinuous phases rather than treating a successful image call as a usable animation. If it cannot pass the hard gates, report that video-generation and frame-extraction capabilities or a suitable motion reference are needed.

# Sprite sheets

## Animation plan

Define before generation:

- state/action and gameplay purpose;
- projection, facing direction, camera lock, and ground line;
- canonical character/object height;
- canvas/cell size and pivot;
- frame count or timing budget;
- phase list: anticipation, contact, recoil, settle, etc.;
- loop mode and endpoint relationship;
- palette, outline, lighting, and identity anchors;
- blend mode and alpha convention for VFX.

## Direct sheet workflow

1. Define the exact grid, frame order, action phases, shared camera, cell size, and pivot.
2. Prompt the image model to generate one strict review sheet with every cell assigned a named phase.
3. Inspect whole-sheet geometry, then slice and evaluate every cell.
4. Reject missing, duplicated, reordered, merged, or inconsistent phases.
5. Normalize shared canvas, scale, pivot, palette, alpha, and edge treatment.
6. Preview the sequence at intended timing.
7. Repack deterministically and write frame metadata.

Direct generation is a first-class path, not just ideation. However, the model's visible grid is not trusted as exact geometry until inspected. When it repeatedly fails identity or phase consistency, generate and approve a canonical frame, then create frames through controlled edits using that frame as the identity reference.

## Sheet prompt structure

Put the grid contract before art direction:

```text
Create one strict 8×1 sprite sheet on a 2048×256 canvas.
LAYOUT: eight equal 256×256 cells, left-to-right order, no gutters, no merged cells, one full character per cell.
ACTION: run cycle. Cell 1 contact, 2 down, 3 passing, 4 up, 5 opposite contact, 6 down, 7 passing, 8 up.
CONSISTENCY: same character identity, costume, proportions, palette, side-view orthographic camera, scale, baseline, and light direction in every cell.
RENDERING: [project style].
OUTPUT: transparent outside the character, no labels, borders, guides, floor, camera movement, duplicate poses, or cropped limbs.
```

If the generator cannot output exact resolution, request the same aspect/grid structure, then slice, normalize, and repack to the delivery geometry.

## Sheet geometry

Record:

```text
cell_width, cell_height
columns, rows
frame_count
padding, extrusion
pivot_x, pivot_y
frame order and duration
loop mode
trim policy
```

The sheet dimensions must match the grid plus declared padding. Use `scripts/inspect_asset.py SHEET --cols N --rows N` for basic divisibility checks.

Keep one shared canvas across frames. Never independently trim frames unless metadata restores a stable pivot.

## External frame sequences

Do not generate or extract video in this skill. When another dedicated skill/tool supplies an ordered frame sequence, treat it as imported source material. Apply the same canvas, pivot, alpha, consistency, timing, evaluation, and packaging checks described here.

## Vision evaluation

Inspect:

- contact-sheet consistency;
- animated playback at target speed;
- silhouette and ground contact per frame;
- pivot/scale drift;
- missing or repeated motion phases;
- limb/part topology;
- palette/light flicker;
- loop discontinuity;
- alpha halo and frame-edge clipping.

For gameplay, motion readability matters more than maximal smoothness. Strong anticipation and contact poses may justify uneven frame timing.

## Packaging

Deliver:

- ordered individual frames;
- packed sprite sheet/atlas;
- machine-readable frame map if the engine needs one;
- pivot and cell metadata;
- per-frame duration or FPS;
- loop mode;
- preview GIF/video/contact sheet;
- source clip or canonical reference when useful.

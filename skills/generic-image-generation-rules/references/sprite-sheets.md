# Sprite sheets

## Contents

- [Animation plan](#animation-plan)
- [Reference roles and subject lock](#reference-roles-and-subject-lock)
- [Direct sheet workflow](#direct-sheet-workflow)
- [Sheet prompt structure](#sheet-prompt-structure)
- [Sheet geometry](#sheet-geometry)
- [Bundled sprite scripts](#bundled-sprite-scripts)
- [Strip extraction fallback](#strip-extraction-fallback)
- [Frame normalization](#frame-normalization)
- [Directional animation sets](#directional-animation-sets)
- [Measurement-driven correction](#measurement-driven-correction)
- [Evaluation](#evaluation)
- [Packaging](#packaging)
- [Extension: Video generated animation frames](#extension-video-generated-animation-frames)

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

Read `sprite-animation-presents.md` when optional action names, starting frame/FPS values, or phase choreography would help. Its values are defaults, not requirements.

## Reference roles and subject lock

Assign each input reference a role:

- **appearance reference**: identity, costume, proportions, topology, palette, and material;
- **motion reference**: phase order, timing, contact, recoil, or loop handoff;
- **view reference**: camera direction and which surfaces or body parts are visible;
- **style reference**: rendering language only.

Do not let a motion or style reference silently replace the canonical subject. State the preserved identity anchors in every controlled frame or direction prompt. An approved strip may become the motion reference for another direction, but it does not override direction-specific camera and visibility.

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

The sheet dimensions must match the grid plus declared padding. Use `scripts/inspect_asset.py SHEET --cols N --rows M` for basic divisibility checks.

Keep one shared canvas across frames. Never independently trim frames unless metadata restores a stable pivot.

## Bundled sprite scripts

These helpers import Pillow only when executed. If Pillow is unavailable, they stop with the same environment-aware dependency hint used by the image-generation chroma-key helper.

- `scripts/sprite/inspect_sequence.py` measures ordered frames without modifying them: Alpha bounds, occupancy, edge contact, centroid/baseline range, color-distribution drift, and adjacent-frame motion delta over the visible-pixel union.
- `scripts/sprite/slice_strip.py` detects natural content runs, drops minor remote residue, splits touching runs with Alpha projection and DP, and optionally aligns frames by center, Alpha centroid, or source-relative baseline. Baseline alignment preserves vertical offsets such as a jump arc.
- `scripts/sprite/pack_animation.py` packs ordered frames into a uniform-grid PNG atlas and Aseprite-style JSON, GIF, and APNG. It uses one shared GIF palette, a configurable binary GIF Alpha threshold, and explicit loop metadata. It supports trim rectangles, padding, extrusion, pivots, FPS or per-frame durations. It is a single-animation packer, not a general multi-page bin packer.

Typical calls:

```text
python scripts/sprite/inspect_sequence.py frames/ --output sequence-report.json
python scripts/sprite/slice_strip.py strip.png frames/ --frames 8 --align baseline --cell-size 256x256 --manifest slice.json
python scripts/sprite/pack_animation.py frames/ --output-prefix walk --fps 12 --columns 4 --trim
```

`--output-prefix` writes the atlas, JSON, GIF, and APNG together. Select individual output flags when only some formats are needed. Treat the inspection JSON and inferred cuts as evidence to review, not proof that the motion phases are semantically correct.

The projection/DP and alignment workflow is a clean Python implementation of concepts adapted from PerfectPixel Studio. See `sprite-animation-presents.md` for the source note and MIT notice.

## Strip extraction fallback

When generated gutters are not exact, detect likely frame boundaries before forcing equal cuts:

1. compute the vertical Alpha projection `P[x]` by summing Alpha down each image column;
2. smooth the projection enough to ignore isolated pixels;
3. identify contiguous content runs, reject low-mass remote residue, and estimate whether a wide run contains multiple prominent pose peaks;
4. if gutters are fused or the natural count differs from the expected count, choose all cuts together inside the main content envelope with a global optimization that favors low Alpha at each cut and discourages implausibly uneven frame widths;
5. use equal expected cuts only as a fallback or regularizer;
6. inspect the extracted contact sheet and playback.

A forced division can produce the requested number of cells without proving that the generator produced the requested number of distinct motion phases. Reject duplicated, fused, reordered, or semantically empty frames after extraction.

## Frame normalization

Normalize the sequence as a set rather than trimming and scaling each frame independently:

- align horizontally from an alpha-weighted subject centroid or another stable subject anchor;
- estimate body extent with a robust alpha-mass interval so a weapon tip, particle, or outstretched limb does not set the scale alone;
- choose one shared scale and canvas for the sequence;
- align grounded actions to a common baseline or contact point;
- preserve intentional vertical displacement for jumps, knockback, flight, and similar motion;
- retain a stable pivot even when packed frames use trim rectangles;
- apply one palette, alpha policy, and edge treatment across all frames.

The exact estimator and tolerance are implementation choices. Verify the normalized result visually at target timing.

## Directional animation sets

For a conventional eight-direction character, an optional efficient plan is:

1. establish and approve the front/south animation strip;
2. generate south, east, north, south-east, and north-east with direction-specific view instructions;
3. use the approved front/south strip as a motion-phase reference for generated directions;
4. derive west, south-west, and north-west by horizontal mirroring only when the character, equipment, lighting, and action are mirror-safe;
5. re-evaluate every mirrored direction against identity, handedness, readable symbols, lighting, and attachment points.

Generate both sides when asymmetric hair, clothing, weapons, text, scars, lighting, or gameplay handedness makes mirroring incorrect. Rear and oblique views expose different features, so relax face-detail comparison while keeping body proportions, costume topology, palette, scale, ground line, and phase timing locked.

## Measurement-driven correction

Combine visual review with lightweight measurements. Convert each observed defect into one narrow correction:

| Evidence | Example correction |
|---|---|
| edge contact or clipped alpha | increase safe margin; keep all limbs and effects inside each cell |
| occupied-area outlier | restore the shared character scale without changing the action phase |
| palette or color-distribution drift | reuse the canonical costume palette and lighting |
| near-empty or faint frame | render the named phase as a complete readable pose |
| insufficient pose change | strengthen the missing contact, passing, apex, or recoil phase |
| baseline/contact drift | keep grounded feet on the declared ground line |
| extraction cut crosses alpha | restore clear gutters or simplify overlapping effects |

Keep the stable semantic brief and references unchanged while correcting the measured defect. Retain the best passing foundation when useful. If failures are global—wrong view, merged grid, identity replacement, or unusable alpha—change the prompt structure or production path instead of adding many local hints. No fixed retry count is implied.

## Evaluation

Use deterministic evidence before judging animation quality:

- expected frame count and order;
- dimensions, alpha mode, and cell divisibility;
- empty/faint frames and occupied-alpha bounds;
- edge contact and clipping;
- area/scale outliers;
- palette or color-distribution drift across frames and against the canonical reference;
- motion presence and distinct phases;
- baseline, pivot, and ground-contact consistency.

Then inspect:

- contact-sheet consistency;
- animated playback at target speed;
- silhouette and ground contact per frame;
- pivot/scale drift;
- missing or repeated motion phases;
- limb/part topology;
- palette/light flicker;
- loop discontinuity;
- alpha/additive compositing artifacts and frame-edge clipping.

Measurements are diagnostic evidence, not semantic proof. Calibrate tolerances to the asset style and resolution; do not import a fixed score or threshold blindly. Pixel-level comparison is less informative across view directions, deliberate deformation, or particle-heavy effects.

For gameplay, motion readability matters more than maximal smoothness. Strong anticipation and contact poses may justify uneven frame timing.

## Packaging

Deliver:

- ordered individual frames;
- packed sprite sheet/atlas;
- machine-readable frame map if the engine needs one;
- pivot and cell metadata;
- per-frame duration or FPS;
- loop mode;
- preview GIF, APNG, video, or contact sheet as appropriate;
- source clip or canonical reference when useful.

When the target pipeline supports it, include a machine-readable manifest with:

```text
animation name
ordered frame identifiers
source rect or trim rect per frame
cell or canvas size
pivot/origin per frame
duration per frame or FPS
loop mode
total duration
```

Common outputs include individual PNG frames, a packed PNG atlas, Aseprite-compatible JSON, GIF for convenient review, and APNG when the preview must retain full alpha behavior. The engine contract decides which outputs are required.

## Extension: Video generated animation frames

**NOTE:** THIS PART NEEDS A DEDICATED VIDEO GENERATION TOOL AVAILABLE.

When a dedicated Video Generation tool (skill/mcp/api) is available and motion-first generation suits the asset:

1. Prepare one canonical appearance reference, or multiple key-time references when the video backend supports them. Keep the subject scale, framing, camera, and background treatment compatible with later extraction.
2. Write a motion prompt that preserves the references and describes temporal behavior, particles, pacing, camera lock, and loop intent. Example: “A burning fireball churns continuously and emits sparks, with a fixed camera and stable centered silhouette.”
3. Hand the references and motion prompt to the Video Generation skill. Request a short source clip, typically 10–20 seconds, with no cuts or camera movement.
4. Hand the clip to a dedicated video-processing skill/tool. Sample an initial ordered sequence at a consistent interval derived from the usable duration and target frame count, then favor readable motion phases over blindly keeping every sample. Do not implement video extraction here.
5. If true-alpha frames are required and the video is opaque, route them through the background-removal policy in `backend-routing.md`. If the emissive additive path is selected, retain pure black, skip background removal, and record the intended blend mode. Inspect alpha or black neutrality, particles, glow, and temporal consistency as applicable.
6. Normalize canvas, pivot, scale, palette, and timing; reject unstable frames; then pack the approved sequence deterministically into the sprite sheet.

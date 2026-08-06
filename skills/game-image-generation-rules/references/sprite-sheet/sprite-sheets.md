# Sprite sheets

Use this file as the entry point for sprite-sheet and sprite-frame animation work. Select one generation workflow, then apply the shared inspection and packaging stages here.

## Contents

- [Animation contract](#animation-contract)
- [Workflow routing](#workflow-routing)
- [Backend result contracts](#backend-result-contracts)
- [Shared frame pipeline](#shared-frame-pipeline)
- [Evaluation](#evaluation)
- [Packaging](#packaging)

## Animation contract

Define before routing:

- state/action and gameplay purpose;
- projection, facing direction, camera lock, and ground line;
- canonical character/object height;
- canvas/cell size and pivot;
- frame count or timing budget;
- phase list: anticipation, contact, recoil, settle, etc.;
- loop mode and endpoint relationship;
- palette, outline, lighting, and identity anchors;
- blend mode and alpha convention for VFX.

Read `sprite-animation-presets.md` when optional action names, starting frame/FPS values, or phase choreography would help. Its values are defaults, not requirements.

## Workflow routing

Check capabilities and inputs in priority order. A route is usable only when all required callable capabilities and their handoff artifacts satisfy the workflow contract; an installed tool name alone is not enough.

| Priority | Enter when | Workflow | Backend result | Fallback |
|---:|---|---|---|---|
| 1 | Video generation can produce a usable clip and frame extraction can return ordered frames; one backend may provide both capabilities or two backends may be chained | [Video generation](workflow-video.md) | ordered frame images | reference generation only with a valid motion-reference sheet; otherwise direct generation |
| 2 | The complete video route is unavailable, unsuitable, or failed; a valid motion-reference sprite sheet is supplied or can be obtained | [Reference generation](workflow-reference.md) | one replacement sheet | change the replacement backend/implementation or report unsupported |
| 3 | A complete video route and a valid motion-reference sprite sheet are unavailable | [Direct generation](workflow-direct.md) | one generated sheet | report the unsupported continuity requirement or deliver only a passing result |

Exception: when the user explicitly supplies or designates a valid sprite sheet as the motion reference, use reference generation even if the complete video route is available.

Manually invoke [reference-sheet preprocessing](reference-sheet-preprocessing.md) only when the user explicitly requests normalization of a motion-reference sheet. It is an optional utility, not another generation route or a prerequisite for reference generation.

For the reference route, distinguish:

- **motion-reference sheet**: sprite sheet that controls phase order, timing, contact, recoil, and loop handoff;
- **appearance reference**: character setting image, canonical image, or text specification that controls identity, costume, proportions, topology, palette, and material.

A motion reference may be a sprite sheet or ordered poses. Motion-reference sprite sheets qualify for reference generation. Ordered poses may optionally guide the video workflow when the selected backend supports them; they do not qualify as input to reference generation.

An appearance reference alone does not provide temporal continuity. When the complete video route is unavailable and no motion reference was supplied, ask whether the user has one or wants one searched for; also inspect relevant project assets. If the user already requested or allowed external search, search without asking again. Use direct generation only when no suitable motion reference is available.

## Backend result contracts

### Sheet result

Reference and direct generation return one sheet plus the planned geometry:

```text
sheet_path
replacement mode when reference-generated
source-sheet metadata and target metadata match when reference-generated
source crop rectangle when single-animation extraction was used
columns, rows
frame_count and row-major order
frame or region rectangles when packing is irregular
cell size when fixed
frame durations or FPS
loop mode
alpha or blend-mode contract
```

A reference-generated sheet must preserve the selected source-sheet metadata contract. A directly generated sheet may miss exact pixel geometry, but it must still produce the requested number of distinct, ordered phases without merged cells or crossed cell boundaries.

### Frame-list result

Video generation and frame extraction stay in the backend layer. They are separate capabilities and may come from one combined backend or two chained backends. This skill receives their final handoff:

```text
ordered frame paths
frame durations or FPS
loop mode
canvas size
alpha or blend-mode contract
```

Frames must be in playback order and share a stable camera and canvas. Preserve source timestamps when sampling is uneven. Do not pass an existing frame list through `slice_strip.py`.

## Shared frame pipeline

Use the bundled scripts according to the backend result. Pixel normalization is optional and applies only to hard-edged pixel-art frame lists after their alpha or matte contract has been resolved:

| Workflow result | `slice_strip.py` | `normalize_pixel_sequence.py` | `inspect_sequence.py` | `pack_animation.py` |
|---|:---:|:---:|:---:|:---:|
| video frame list | — | pixel art only | yes | yes |
| reference-generated sheet | yes | — | yes | yes |
| directly generated sheet | yes | — | yes | yes |

```text
VIDEO:     appearance reference --> video generation --> source clip --> frame extraction --> ordered frames --> optional pixel normalization --> inspect_sequence.py --> vision review --> pack_animation.py
REFERENCE: reference backend --> sheet --> inspect_asset.py --> slice_strip.py --> frames --> inspect_sequence.py --> vision review --> pack_animation.py
DIRECT:    direct backend --> sheet --> inspect_asset.py --> slice_strip.py --> frames --> inspect_sequence.py --> vision review --> pack_animation.py
```

For both sheet-producing routes, `slice_strip.py` returns the single-frame image collection consumed by `inspect_sequence.py`.

For generated sheets:

1. Run `scripts/inspect_asset.py SHEET --cols C --rows R` to check size, alpha, borders, padding, and grid divisibility.
2. Run `scripts/sprite/slice_strip.py`. Use `--method equal` when the backend produced a known exact grid; use the default `projection-dp` when transparent gutters or generated boundaries are not exact. When source-cell coordinates encode root motion, use the exact grid with `--align none`; content-aware variable-width segmentation cannot recover discarded cell-space offsets.
3. For multi-row sheets, pass `--rows R --frames C`. Output is row-major and named `_r{row}_c{col}`.
4. Use one shared cell canvas and a suitable alignment mode. The default `none` preserves source-cell X/Y coordinates. `baseline` preserves relative vertical displacement but normalizes horizontal placement, so use it only for intentionally in-place animation.
5. Reject a sheet when extraction would cut through a subject, merge phases, invent missing phases, or hide a crossed cell boundary. Producing the expected file count does not prove the sheet is valid.

For video frames, preserve the backend's camera-space motion. Do not centroid-align or baseline-align the sequence merely to suppress visible movement; camera drift is a backend failure, while intentional subject displacement is part of the animation. For hard-edged pixel art, `normalize_pixel_sequence.py` applies one shared crop, scale, placement, and global palette to the complete sequence, so it preserves motion instead of recentering individual frames. Supply frames with usable alpha; remove a matte first when necessary.

Then run `scripts/sprite/inspect_sequence.py` on the ordered frames. It reports dimensions, occupied Alpha bounds, centroid/baseline drift, edge contact, color-distribution drift, and adjacent-frame motion delta. Treat these metrics as diagnostic evidence, not proof of identity or correct motion semantics.

Typical calls:

```text
python scripts/inspect_asset.py sheet.png --cols 4 --rows 2 --expect-transparent
python scripts/sprite/slice_strip.py sheet.png frames/ --rows 2 --frames 4 --method equal --align none --cell-size 256x256 --manifest slice.json
python scripts/sprite/normalize_pixel_sequence.py video-frames/ pixel-frames/ --size 64x64 --colors 4 --anchor bottom-center
python scripts/sprite/inspect_sequence.py frames/ --output sequence-report.json
python scripts/sprite/pack_animation.py frames/ --output-prefix hero --names run,jump --fps 12 --trim
python scripts/sprite/pack_animation.py video-frames/ --output-prefix walk --fps 12 --trim
```

`pack_animation.py` uses a sibling slice manifest or `_r{row}_c{col}` names to group sheet rows. Without row information it treats the inputs as one animation. Use `--normalize global` only when every animation must share one fixed canvas; the default `per-row` keeps animation rows compact.

## Evaluation

Apply deterministic evidence first:

- expected frame count and order;
- dimensions, alpha mode, and sheet/cell geometry;
- empty or faint frames and occupied-alpha bounds;
- edge contact and clipping;
- area/scale and palette outliers;
- baseline, pivot, and ground-contact consistency;
- meaningful adjacent motion and a plausible final-to-first transition for loops.

Then inspect a contact sheet and playback at target timing for:

- stable identity, costume, proportions, topology, palette, camera, and scale;
- readable anticipation, contact, passing/apex, recoil, and settle phases as applicable;
- missing, duplicated, reordered, or abruptly discontinuous poses;
- limb, weapon, attachment, particle, and secondary-motion continuity;
- loop discontinuity, palette flicker, alpha artifacts, and frame-edge clipping.

Gameplay readability matters more than maximal smoothness. Strong anticipation and contact poses may justify uneven timing. A visually attractive frame does not compensate for a broken sequence or failed hard gate.

Convert each observed defect into one narrow correction. Regenerate or change workflow when failures are global, such as identity replacement, wrong view, merged grid, unstable video camera, unusable alpha, or missing motion phases.

## Packaging

Deliver only accepted outputs:

- ordered individual frames;
- packed PNG sheet or atlas;
- machine-readable frame map when the engine needs one;
- pivot/origin and cell or trim metadata;
- per-frame duration or FPS;
- loop mode;
- GIF or APNG playback preview and optional contact sheet;
- source sheet, motion reference, or video-derived frame set when useful.

When the target pipeline supports it, include a manifest containing animation name, ordered frame identifiers, source/trim rects, canvas size, pivot, duration, loop mode, and total duration.

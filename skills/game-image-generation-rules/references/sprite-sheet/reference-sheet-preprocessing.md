# Reference-sheet preprocessing

Use this optional workflow only when the user explicitly requests preprocessing for a motion-reference sprite sheet whose spacing, cells, matte, or packing is unsuitable for full-sheet replacement. It is not an automatic prerequisite or entry gate for reference generation. Use a valid sheet directly when no preprocessing was requested.

Preprocessing is deterministic layout normalization, not subject replacement or animation generation. Preserve every recoverable source phase; do not repair a broken reference by inventing frames.

## Output contract

Return:

- one canonical motion-reference sheet with clearer frame and row separation;
- the original source metadata;
- canonical row, cell, frame-count, and playback-order metadata;
- a one-to-one mapping from every original frame rectangle to its canonical cell rectangle;
- pivot, ground-line, placement-offset, duration, FPS, and loop metadata when known; mark unavailable values as unknown.

## Analyze the source

Record the source canvas, alpha or matte contract, animation regions, frame rectangles, row-major order, gutters, pivots, ground lines, occupied bounds, and known timing before changing the layout. Use source-aware segmentation plus vision. Do not use raw connected-component counts for effects that cross gaps, or a forced slice count as proof of valid metadata.

Stop when missing, duplicated, merged, or ambiguous phases prevent a reliable one-to-one mapping. Report the defect instead of fabricating a canonical sheet.

## Slice to ordered frames

Resolve the alpha or matte contract, then extract complete animation regions and frames in source playback order. `slice_strip.py` may be used when its detected boundaries match the analyzed metadata; process animation regions separately when their frame counts differ.

- Preserve source frame identifiers and rectangles in the manifest.
- Use `--align none` unless an explicit shared pivot transformation is recorded.
- Do not independently trim, center, baseline-align, or scale frames in a way that removes intentional root motion, jump height, recoil, or effect displacement.
- Keep effect-only phases when they are valid source frames.

## Pack the canonical sheet

Pack all extracted frames into one generation-friendly sheet:

- keep one row or region per source animation, in the same order;
- preserve the exact frame count and playback order in every region;
- use a stable cell canvas, pivot, ground line, and subject scale within each animation;
- add consistent safe gutters between cells and clear separation between animation rows;
- keep every subject and effect inside its assigned cell;
- use transparent padding or one flat removable matte without labels, guides, or decorative content;
- record canonical cell rectangles and placement offsets in the mapping manifest.

Use `pack_animation.py` to create the canonical atlas and JSON. Set `--padding` deliberately larger than the delivery default so every normalized frame has clear transparent separation, record that value, and keep `--extrude 0` because extrusion is not blank padding. Leave `--trim` disabled, and select `--anchor` and `--normalize` to preserve the recorded pivot and motion offsets.

```text
python scripts/sprite/pack_animation.py frames/ --atlas canonical-reference.png --json canonical-reference.json --padding <padding> --extrude 0 --anchor <anchor> --normalize <per-row|global>
```

## Process

Run:

```text
source sheet --> metadata analysis --> slice_strip.py --> ordered frames + mapping
             --> pack_animation.py with large padding --> canonical atlas + mapping manifest
```

Do not run `inspect_image.py` or `inspect_sequence.py` in this preprocessing workflow. It ends after packing the canonical sheet and metadata mapping; the caller may then use those outputs manually.

# Reference generation workflow

Use this workflow when the user explicitly supplies or designates a valid motion-reference sprite sheet, or when the complete video route is unavailable, unsuitable, or failed and such a sheet exists or can be obtained. The backend receives the motion-reference sheet plus a replacement appearance reference or text specification and returns one replacement sheet.

Reference generation always executes exactly one of these two modes:

1. **Full-sheet replacement** — the default. Analyze the complete source-sheet metadata, then replace the subject across the complete sheet while preserving its layout and motion.
2. **Single-animation extraction** — use only when the user explicitly requests a specific action or animation. First crop that animation's complete source region, analyze the cropped sheet metadata, then perform sheet replacement on that cropped region.

Do not introduce another reference-generation mode. Single-animation extraction is not freeform animation generation: cropping selects the source sheet to replace, and the replacement must still preserve that sheet's complete frame structure.

## Entry gate

Enter this workflow only with a motion-reference sprite sheet that contains the complete frame layout to preserve. A single motion image, loose frame collection, video, skeleton sequence, or pose-only sequence is not a direct input because it does not provide the sheet-level layout contract this workflow replaces.

- Use single images only as appearance, view, or style references.
- Route video through the video workflow.
- Route skeleton or pose sequences through a pose-conditioned image or video workflow rather than treating them as sprite sheets.
- If a complete ordered raster-frame sequence is supplied, pack it deterministically into a motion-reference sheet and record its metadata before entering this workflow. This normalization does not create another reference mode.

If no valid motion-reference sheet exists or can be produced, do not use this workflow.

## Acquire and classify references

Obtain a motion reference in this order:

1. user-provided attachments;
2. relevant existing project assets;
3. ask whether the user can provide one or wants one searched for, unless search is already authorized;
4. external search when the user requested or allowed it.

Route to direct generation only when no suitable motion reference can be obtained.

Assign every reference one role:

- **motion-reference sheet**: sheet layout, frame order, pose relationships, contacts, displacement, recoil, and loop handoff;
- **appearance reference**: identity, costume, proportions, topology, palette, and material;
- **view reference**: camera direction and visible surfaces or body parts;
- **style reference**: rendering language only.

Do not let the motion or style reference replace the target subject. A text appearance description is acceptable when the selected backend can hold it consistently; otherwise first create one canonical appearance image.

## Analyze source metadata

Analyze the selected source sheet before requesting any replacement. For full-sheet replacement, the selected source is the complete motion-reference image. For single-animation extraction, locate and crop the explicitly requested animation first; the selected source is that complete cropped region.

Record the selected source's:

- canvas size, format, color mode, alpha or matte/background contract;
- animation regions or rows and their source rectangles;
- frame count per region, frame rectangles, and playback order;
- fixed-grid, variable-cell, gutter, padding, and packing geometry;
- camera, facing direction, ground line, pivot or root motion, and occupied bounds;
- known animation names, durations, FPS, and loop modes; mark unavailable values as unknown instead of inventing them.

For single-animation extraction, also record the crop rectangle in full-sheet coordinates and express the cropped frame rectangles relative to the cropped sheet. Do not infer a uniform grid when the source uses irregular packing. Do not generate until the metadata is reliable enough to detect missing, duplicated, reordered, merged, or displaced frames.

## Compatibility gate

For full-sheet replacement, confirm that every animation region has readable phase order, compatible views, and a sufficiently compatible subject topology. For single-animation extraction, apply the same check to the cropped action region. Preserve joint relationships, ground contacts, displacement, and phase timing rather than blindly copying the source silhouette when body proportions differ.

Reject references with missing/repeated phases, broken loops, merged cells, severe clipping, or a topology that cannot express the target action.

## Backend request

Send the complete selected source sheet and request one metadata-isomorphic replacement sheet. Do not summarize the reference into a new textual phase list or change its layout during generation. State the mode, transformation, and preservation boundary explicitly:

```text
MODE: [full-sheet replacement | single-animation extraction].
CHANGE: replace the motion-reference subject with [target appearance].
PRESERVE FROM MOTION REFERENCE: canvas and region layout, frame count, frame rectangles, frame order, every action phase, pose relationships, ground contacts, displacement, facing direction, camera, effects, and loop handoff.
PRESERVE FROM APPEARANCE REFERENCE: identity, costume topology, proportions, palette, materials, equipment, and rendering style.
OUTPUT: one replacement sheet matching the selected source metadata contract, with the required alpha/blend contract and no added labels, omitted frames, merged cells, or layout changes.
```

Prefer a backend that can use the motion and appearance references simultaneously and preserve whole-sheet structure. An implementation may process frames or regions internally when the backend cannot replace the selected sheet in one call, but it must reconstruct the same selected-sheet metadata contract; internal processing does not create another execution mode. Keep reference roles, frame order, geometry, and identity anchors stable across retries.

## Directional sets

An approved strip may become the motion reference for another direction, but it does not override direction-specific camera and visibility. Generate both sides when hair, clothing, weapons, text, scars, lighting, or gameplay handedness is asymmetric. Mirror only directions whose subject, equipment, lighting, and action are mirror-safe.

## Handoff and fallback

Before handoff, compare the replacement against the source frame rectangles and verify each region's frame count and the total with source-aware segmentation plus vision. Do not use raw connected-component counts for effects that cross gaps, or treat a forced slice count as proof. If a slice would be empty, fragmentary, merged, or invented to reach the expected count, reject and regenerate the sheet before slicing.

Return one replacement sheet, the analyzed source metadata, and the target metadata verification. For single-animation extraction, also return the full-sheet crop rectangle. Continue with sheet inspection, slicing, sequence evaluation, and packaging in `sprite-sheets.md`.

Reject changed canvas or region geometry and any missing, duplicated, reordered, merged, displaced, or inconsistent phase. When a suitable motion reference exists, do not fall back to direct generation because that abandons the supplied motion contract. Change the backend or internal replacement implementation; if none can preserve the contract, report the unsupported requirement and deliver no misleading substitute.

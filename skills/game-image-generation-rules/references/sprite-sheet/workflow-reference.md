# Reference generation workflow

Use this workflow when video generation is unavailable, unsuitable, or failed and a motion-reference sprite sheet exists or can be obtained. The backend receives the motion reference plus a replacement appearance reference or text specification and returns one generated sheet.

## Acquire and classify references

Obtain a motion reference in this order:

1. user-provided attachments;
2. relevant existing project assets;
3. ask whether the user can provide one or wants one searched for, unless search is already authorized;
4. external search when the user requested or allowed it.

Route to direct generation only when no suitable motion reference can be obtained.

Assign every reference one role:

- **motion reference**: grid, phase order, pose relationships, contacts, displacement, recoil, and loop handoff;
- **appearance reference**: identity, costume, proportions, topology, palette, and material;
- **view reference**: camera direction and visible surfaces or body parts;
- **style reference**: rendering language only.

Do not let the motion or style reference replace the target subject. A text appearance description is acceptable when the selected backend can hold it consistently; otherwise first create one canonical appearance image.

## Compatibility gate

Confirm that the reference has the requested action, readable phase order, compatible view, and a sufficiently compatible subject topology. Preserve joint relationships, ground contacts, displacement, and phase timing rather than blindly copying the source silhouette when body proportions differ.

Reject references with missing/repeated phases, broken loops, merged cells, severe clipping, or a topology that cannot express the target action.

## Backend request

Request one complete sheet. State the transformation and preservation boundary explicitly:

```text
CHANGE: replace the motion-reference subject with [target appearance].
PRESERVE FROM MOTION REFERENCE: grid, cell order, action phases, pose relationships, ground contacts, displacement, facing direction, camera, and loop handoff.
PRESERVE FROM APPEARANCE REFERENCE: identity, costume topology, proportions, palette, materials, equipment, and rendering style.
OUTPUT: one sheet with the planned rows, columns, frame order, alpha/blend contract, and no labels or merged cells.
```

Prefer a backend that can use the motion and appearance references simultaneously. Keep reference roles, frame order, and identity anchors stable across retries.

## Directional sets

An approved strip may become the motion reference for another direction, but it does not override direction-specific camera and visibility. Generate both sides when hair, clothing, weapons, text, scars, lighting, or gameplay handedness is asymmetric. Mirror only directions whose subject, equipment, lighting, and action are mirror-safe.

## Handoff and fallback

Return one generated sheet plus the planned geometry and timing metadata. Continue with sheet inspection, slicing, sequence evaluation, and packaging in `sprite-sheets.md`.

Reject missing, duplicated, reordered, merged, or inconsistent phases. If no suitable motion reference exists or the backend cannot preserve it after a materially revised attempt, use `workflow-direct.md`.

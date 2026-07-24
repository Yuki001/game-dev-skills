# Vision evaluation

Define evaluation before generation. Use observable criteria and evidence, not “looks good.”

## Evaluation layers

### 1. Hard gates

Typical gates:

- correct artifact type and format;
- exact dimensions/aspect ratio;
- correct subject/count/action;
- true alpha when required;
- no crop or frame-edge clipping;
- correct camera/projection;
- required identity/reference consistency;
- sheet/frame geometry valid;
- safety/IP/content constraints satisfied.

Any failed gate makes the asset or variant non-deliverable regardless of average score.

### 2. Weighted quality criteria

Choose only relevant criteria and make weights total 100:

| Criterion | Typical evidence |
|---|---|
| functional readability | recognizable at intended in-game size |
| silhouette/composition | clear outline, focal hierarchy, balanced occupied bounds |
| style adherence | matches declared shape, line, palette, and material language |
| technical cleanliness | no artifacts, halos, clipping, grid errors, or broken alpha |
| reference consistency | stable identity, costume, proportion, camera, and palette |
| game-set cohesion | matches accepted assets and import conventions |
| animation quality | stable pivot, meaningful phases, loop and timing quality |

Set a total threshold and any per-criterion minimum in the plan. A useful default is 80/100 total with no critical criterion below 3/5, but adjust for the task.

## Vision evaluation prompt

Provide the evaluator:

```text
ROLE: strict game-asset art/technical reviewer.
CONTEXT: intended use, target display size, references, and asset contract.
HARD GATES: explicit list.
WEIGHTED CRITERIA: names, weights, and anchors.
INSTRUCTIONS:
- Inspect the actual image, not the generation prompt's claims.
- Cite visible evidence and defect locations.
- Evaluate at target size and inspection zoom.
- Do not compensate a hard-gate failure with aesthetic quality.
- Return concise findings for the current working context: gate results, scores, defects, decision, and next action.
```

Recommended response:

```text
GATES: true alpha — FAIL; opaque white pixels fill all four corners.
SCORES: silhouette 4/5; blade and hilt separate clearly at 48 px.
DEFECTS: critical — opaque background at canvas border.
DECISION: edit.
NEXT: remove the background while preserving internal holes and crop.
```

Keep this assessment in context unless the user requests a persistent report.

## Score anchors

Use consistent anchors:

- **5**: production-ready; no meaningful defect for the intended use.
- **4**: strong; minor fix or acceptable small deviation.
- **3**: usable draft; visible issues require refinement.
- **2**: major mismatch or artifacts; substantial change needed.
- **1**: fails the criterion.

## Comparative review

When ranking variants for the same asset:

1. label images with temporary anonymous IDs;
2. reject hard-gate failures first;
3. compare the remaining variants side by side;
4. select the best foundation, not merely the most detailed image;
5. keep a brief reason in context for why the winner is easier to refine.

Use pairwise comparison if scores cluster tightly. Detail density should not beat functional readability.

## Reference and temporal drift

For each asset, variant, or frame compare:

- face/body/object proportions;
- silhouette landmarks;
- costume/part topology;
- palette swatches;
- camera angle and scale;
- light direction;
- pivot and ground contact.

For animation, view a contact sheet and the motion sequence. A single attractive frame can still belong to a broken animation.

## Iteration decision

- `accept`: all gates pass and thresholds met.
- `edit`: localized defect; composition and identity are sound.
- `regenerate`: global composition, pose, silhouette, or projection is wrong.
- `change pipeline`: repeated failure shows a backend capability mismatch.

After two rounds with the same major defect, revise the prompt structure, references, control method, or backend.

# Video generation workflow

Use this workflow first when video-generation and frame-extraction capabilities are both available. They may be exposed by one combined skill/tool or by separate backends chained through a source clip. This workflow resumes from the final frame-list result.

## Capability preconditions

Verify that video generation can:

- accept an appearance reference or a sufficiently constrained subject prompt;
- generate a short clip without cuts or camera movement;
- keep the complete subject inside a stable frame;
- return a clip that the selected frame-extraction capability can access.

Verify separately that frame extraction can:

- read the generated clip format or shared clip artifact;
- select or sample the usable action segment;
- return ordered image frames with source timing or explicit durations;
- satisfy or declare the required alpha, matte, or additive-blend contract.

If the task supplies only text, create a canonical appearance image with an available image backend when video generation needs an image reference. This preparatory still does not switch the task to direct sheet generation.

## Video-generation request

Give the video-generation backend:

- the canonical appearance reference and its identity anchors;
- action, facing direction, projection, ground line, and gameplay purpose;
- a short motion description with anticipation, contact/apex, recovery, and loop intent;
- fixed-camera, stable-scale, full-subject, and no-cut requirements;
- target frame count or timing budget;
- background and alpha/blend expectations for the extracted frames.

Prefer the shortest clip that contains one readable action cycle or one complete one-shot. Long clips increase identity, texture, lighting, and camera drift.

## Frame-extraction request

Hand the generated clip to the selected frame-extraction capability. Request the usable action segment, target frame count or timing budget, playback order, source timestamps when sampling is uneven, and the required image/compositing contract. Favor readable motion phases over blind uniform sampling.

## Required result

Require the backend layer to return:

```text
ordered frame paths
frame durations or FPS
loop mode
canvas size
alpha or blend-mode contract
```

The frame-extraction capability produces this result. Video generation does not need to expose frame extraction itself when a compatible second backend is available.

## Handoff and fallback

Pass the returned frames directly to the shared sequence inspection and packaging stages in `sprite-sheets.md`; do not run `slice_strip.py`.

Route failures to the responsible capability: rerun video generation for camera movement, subject replacement, incomplete action, topology flicker, or crossed framing; rerun frame extraction for wrong segment, ordering, sampling, timing, or output-format defects. If a materially revised video route still cannot satisfy the hard gates, fall back to `workflow-reference.md` when a motion-reference sheet can be obtained, otherwise use `workflow-direct.md`.

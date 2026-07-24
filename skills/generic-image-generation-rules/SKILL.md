---
name: generic-image-generation-rules
description: Plan, generate, inspect, vision-evaluate, refine, and package images and visual assets for game development through a backend-agnostic production loop. Use for PNG or SVG props, icons, characters, environments, tiles, UI, VFX, transparent cutouts, concept sheets, sprite sheets, or animation frames; especially when the task needs batch generation, native prompts or ComfyUI/Stable Diffusion Danbooru tags, reference consistency, background removal, format validation, or iterative quality scoring. This skill orchestrates available image, image-edit, vision, SVG, MCP, local, and host-native tools without requiring a specific generator.
---

# Generic Image Generation Rules

Treat image generation as an asset-production pipeline, not a single prompt. Keep the active brief, prompts, and evaluation evidence in the model context while the task runs.

## Core loop

Run:

```text
PLAN → GENERATE → NORMALIZE/INSPECT → EVALUATE
     → ACCEPT OR EDIT/REGENERATE → RE-EVALUATE → OUTPUT
```

Do not generate before defining the deliverable contract and evaluation criteria. Do not deliver an uninspected asset.

## 1. Plan the asset contract

Maintain a concise working plan in the model context. Do not create plan, manifest, or log files unless the user explicitly asks for persistent records.

Resolve:

- in-game purpose and viewing distance;
- asset family: icon, prop, character, portrait, environment, tile, UI, VFX, sheet, or animation;
- SVG versus raster, canvas size, aspect ratio, color space, alpha or blend-mode requirement, and engine constraints;
- camera/projection, silhouette, pose, scale, lighting, palette, material, and style invariants;
- references and the role of each reference;
- animation timing, loop behavior, frame count, pivot, cell size, and sheet layout when applicable;
- batch/iteration budget and the acceptance rubric.

Separate **hard gates** from **quality criteria**. Define both before generation. Read:

- `references/backend-routing.md` to select and preflight generators/editors;
- `references/prompting.md` to compile native prompts or Danbooru tags;
- `references/game-asset-patterns.md` for asset-specific brief and prompt patterns.

Ask only when a missing choice materially changes the deliverable. Otherwise record a reasonable assumption in the plan.

## 2. Route by artifact type

Choose the simplest production path that preserves the requested properties:

- **SVG**: construct or generate vector-native markup, then validate it through `references/svg-workflow.md`.
- **Raster PNG**: generate at or above delivery size, preserve a clean subject silhouette, then normalize and inspect.
- **Transparent or composited VFX raster**: use native alpha or a removable matte for normal transparency. For emissive-only VFX, black-background additive delivery may replace alpha extraction when the target engine/material supports it. Validate the selected path through `references/raster-and-alpha.md`.
- **Sprite sheet**: prompt the image model for a strict grid and explicit per-cell phases, then inspect the sheet and every cell. If direct generation cannot hold identity or grid geometry, fall back to canonical-reference plus controlled frame generation. Read `references/sprite-sheets.md`.
- **Video-derived frames**: delegate video generation and extraction to a dedicated video skill/tool. Accept its ordered frames as inputs here only when game-asset evaluation or packaging is still requested.

## 3. Compile prompts from one semantic source

Write one backend-neutral semantic prompt as the source of truth. Derive, do not independently invent:

1. a native-language prompt for instruction-following image models;
2. a positive Danbooru-style tag list for compatible SD/ComfyUI checkpoints;
3. a separate negative prompt only when that backend uses one;
4. edit instructions that state the transformation first and repeat preserved invariants.

Keep format, layout, identity, and content constraints distinct from style modifiers. Keep the current compiled prompts in context and pass them directly to the selected backend.

## 4. Generate batches

Preflight available capabilities: generate, edit, mask/inpaint, reference images, multi-reference, alpha, seed, batch, SVG, video, and output-size limits. Do not name or require a particular skill/tool unless it is actually available and chosen.

Distinguish two batch modes:

- **Direct asset batch**: each output is a different usable asset. Generate directly into the requested target directory with deterministic final filenames, then validate every asset independently.
- **Variant batch**: multiple attempts compete for one asset slot. Use a temporary or staging directory, compare them with short-lived labels, and place only accepted output in the target directory.

Keep prompts, relevant parameters, comparison reasons, and iteration state in the current model context. Avoid changing every variation axis at once. Use lower-cost draft settings only for variant exploration and reserve expensive/high-resolution calls for selected outputs when supported.

## 5. Normalize and inspect

Before aesthetic judging, apply deterministic checks:

- file opens and format matches the contract;
- exact dimensions/aspect ratio;
- the selected transparency/compositing path is valid: real alpha for alpha assets, or intentional pure black plus a declared blend mode for additive VFX;
- no clipped pixels, edge halos, accidental borders, or empty padding;
- grid/cell geometry is divisible and consistent;
- animation frames have stable canvas, pivot, scale, identity, and ordering;
- SVG passes objective structural checks and text-only shape review; production SVG additionally passes one render/view.

Run `scripts/inspect_asset.py` for PNG/SVG metadata, alpha evidence, and optional sheet-grid checks. Read `references/raster-and-alpha.md` for edge cleanup.

## 6. Evaluate with vision

Evaluate each generated asset or variant against the criteria written during planning, not against improvised taste. Read `references/evaluation.md`.

Skip vision for SVGs classified as placeholders by the SVG planning step. Render and evaluate them only when they become clearly production-bound.

For each raster asset, production SVG, or variant that requires vision evaluation:

1. apply hard gates first;
2. view at intended in-game size and at inspection zoom;
3. score each planned criterion with visible evidence;
4. list defects with location and severity;
5. compare competing variants under anonymous IDs when practical;
6. recommend `accept`, `edit`, `regenerate`, or `change pipeline`.

Do not accept a high average score when a hard gate fails. For references or animation, explicitly measure identity, palette, camera, proportion, and temporal drift.

## 7. Iterate deliberately

Choose the cheapest action that addresses the observed defect:

- use **edit/inpaint** for localized defects while the composition is sound;
- **regenerate** when silhouette, pose, projection, or composition is wrong;
- revise prompt compilation when the model repeatedly misreads the brief;
- change backend or artifact path when the current one lacks a required capability.

Re-evaluate every edited output. Stop when all hard gates pass and the plan's thresholds are met. If the same major defect survives two rounds, change the prompt structure, references, or pipeline rather than repeating near-identical calls.

## 8. Package game-ready outputs

Deliver only accepted files plus useful production metadata:

- deterministic filenames and version suffixes;
- source SVG plus rendered preview for production vector assets; placeholders may omit the preview;
- PNG with the correct color/alpha mode, or a documented additive blend contract, when raster;
- individual frames plus packed sheet and frame map when animated;
- pivot/origin, cell size, padding/extrusion, frame duration, and loop mode;
- contact sheet or preview for batches/animations.

Report assumptions, selected variant when applicable, evaluation result, post-processing applied, and any engine-import caveat.

## Bundled resources

- `references/backend-routing.md` — capability discovery and backend selection.
- `references/prompting.md` — semantic prompts, native prompts, Danbooru tag compilation, and edit prompts.
- `references/game-asset-patterns.md` — reusable patterns for common game asset families.
- `references/evaluation.md` — hard gates, weighted rubrics, comparison, and iteration decisions.
- `references/raster-and-alpha.md` — PNG, alpha, matte removal, additive VFX, edge cleanup, and delivery checks.
- `references/svg-workflow.md` — universal code/text shape checks and production render/view verification.
- `references/sprite-sheets.md` — direct sheet prompting, grid/frame consistency, and packaging.
- `scripts/inspect_asset.py` — inspect PNG/SVG metadata, alpha, and grid geometry.

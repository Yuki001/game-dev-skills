# Backend routing

Select a backend only after the asset contract exists. The skill is an orchestrator; generation may come from a host-native image tool, another installed skill, an MCP server, a local ComfyUI/Stable Diffusion workflow, SVG code, or a user-provided pipeline.

## Capability inventory

Probe or infer the smallest relevant set:

| Capability | Why it matters |
|---|---|
| text-to-image | initial raster assets or variants |
| image edit / image-to-image | preserve composition or identity during refinement |
| background removal | foreground segmentation/matting to alpha |
| mask / inpaint | local corrections and background-removal fallback |
| one or more references | character, style, palette, layout, or item consistency |
| native alpha output | direct transparent or partial-alpha PNG |
| deterministic seed | controlled variation and reproduction |
| batch generation | efficient exploration |
| exact dimensions | sheet cells, UI, engine constraints |
| vector/SVG output | editable geometric assets |
| vision input | evidence-based evaluation |
| video generation | generate a reference-guided continuous-motion source clip |
| frame extraction | decode a source clip and return selected ordered frames with timing |

Do not assume a capability from a tool name. Verify the callable interface or document the uncertainty.

## Routing rules

- Choose SVG/code-native construction for geometric icons, flat UI, logos, diagrams, scalable decals, and assets that require editable paths.
- Choose a modern instruction-following image model for complex composition, readable labels, reference edits, or semantic scene control.
- Choose SD/ComfyUI when the user needs local execution, checkpoint/LoRA/control-net workflows, repeatable seeds, or tag-oriented prompting.
- Choose image edit over regeneration when the current silhouette and composition already pass.
- Prefer native transparent or partial-alpha generation when the selected model can represent the required opacity structure; inspect the returned alpha rather than trusting the prompt.
- For background removal, prefer an available dedicated skill, MCP, or API; if none is available, fall back to a capable image-edit/inpaint model and inspect the resulting alpha and edges.
- For emissive-only VFX, choose black-background additive delivery instead of background removal when the target engine/material supports it; do not use this path for smoke, shadows, or pixels that must occlude or darken the scene.
- For sprite animation, use the routing table in `sprite-sheet/sprite-sheets.md`: prefer the video route when both video-generation and frame-extraction capabilities are available; otherwise use a motion-reference sheet plus the target appearance; use direct full-sheet generation only when neither route is available.
- Choose deterministic post-processing tools for resizing, alpha inspection, slicing, and packing. Do not ask a generative model to perform exact grid arithmetic.

## Preflight

Keep only relevant facts in the current working context:

```text
backend:
  route:
  tool/model:
  capability_providers:
  handoff_artifacts:
  capabilities_verified:
  limitations:
  prompt_dialect:
  generation_size:
  edit_support:
  alpha_support:
  blend_mode_or_alpha_contract:
  batch_or_seed_support:
  cost_or_latency_class:
```

Never place API keys, tokens, cookies, or private endpoint credentials in prompts, logs, or output files.

## Fallback ladder

Use a fallback only if it preserves the hard gates:

1. native required capability;
2. generation plus a separate deterministic/edit step;
3. alternative backend;
4. change artifact construction method;
5. report the unsupported requirement and deliver no misleading substitute.

Examples:

- Required alpha → native alpha-capable generation → dedicated removal/matting over a removable matte when needed → capable image edit/inpaint → alpha inspection.
- Emissive VFX with no alpha requirement → pure black background → additive material → in-engine composite inspection.
- Sprite animation → video generation + frame extraction → motion-reference sheet plus target appearance → direct full-sheet generation.
- Raster model fails exact geometry → construct SVG or composite generated parts deterministically.
- Video source selected → hand the generation result to an available frame-extraction capability, which may belong to the same or a different backend; then resume here from the ordered frame list.

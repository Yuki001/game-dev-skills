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
| native alpha output | direct transparent PNG |
| deterministic seed | controlled variation and reproduction |
| batch generation | efficient exploration |
| exact dimensions | sheet cells, UI, engine constraints |
| vector/SVG output | editable geometric assets |
| vision input | evidence-based evaluation |

Do not assume a capability from a tool name. Verify the callable interface or document the uncertainty.

## Routing rules

- Choose SVG/code-native construction for geometric icons, flat UI, logos, diagrams, scalable decals, and assets that require editable paths.
- Choose a modern instruction-following image model for complex composition, readable labels, reference edits, or semantic scene control.
- Choose SD/ComfyUI when the user needs local execution, checkpoint/LoRA/control-net workflows, repeatable seeds, or tag-oriented prompting.
- Choose image edit over regeneration when the current silhouette and composition already pass.
- For background removal, prefer an available skill, MCP, or API only for dedicated background removal; if none is available, fall back to mask/inpaint and inspect the resulting alpha and edges.
- Choose direct sheet generation when a model can follow strict grid and per-cell phase instructions.
- Choose frame-by-frame controlled edits when direct sheets cannot preserve identity, phase order, or cell geometry.
- Choose deterministic post-processing tools for resizing, alpha inspection, slicing, and packing. Do not ask a generative model to perform exact grid arithmetic.

## Preflight

Keep only relevant facts in the current working context:

```text
backend:
  route:
  tool/model:
  capabilities_verified:
  limitations:
  prompt_dialect:
  generation_size:
  edit_support:
  alpha_support:
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

- No native alpha → removable matte → background-removal edit → alpha inspection.
- Poor direct sheet generation → canonical reference → individual frames → deterministic pack.
- Raster model fails exact geometry → construct SVG or composite generated parts deterministically.
- Video source requested → hand off video generation/extraction to a dedicated skill, then resume here only for asset evaluation or packaging.

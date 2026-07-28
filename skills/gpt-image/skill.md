---
name: gpt-image
description: Execute image generation, editing, and chroma-key transparent-background workflows with GPT Image 2 / gpt-image-2 through the bundled scripts. Use when GPT Image is the selected backend and a supplied prompt or edit instruction must be executed for text-to-image generation, reference-image editing, multi-reference editing, masked inpainting, or chroma-key background removal. Treat the supplied prompt as authoritative; this skill does not search prompt galleries, choose art direction, or perform general prompt planning.
---

# GPT Image Executor

Execution-only runbook for GPT Image generation and editing. Use the packaged CLI; do not reimplement image API code.

## Responsibility boundary

- Accept the prompt or edit instruction produced by the user or an upstream workflow.
- Do not browse prompt examples, invent an art direction, compare creative concepts, or rewrite the prompt semantically.
- Apply only backend-required formatting and parameter mapping. If a required execution input is missing or contradictory, ask one concise question.
- Generate or edit images only through this skill's packaged CLI.
- Do not create a new SDK wrapper or ad-hoc generation script unless the user explicitly asks to modify this repository.

## Operating loop

1. **Classify operation**: `generate`, `edit`, `inpaint`, `multi-reference`, or chroma-key background removal.
2. **Preflight without mutation**: verify the CLI, Python 3.11+, required packages, input files, output destination, and credential availability.
3. **Map execution parameters**: pass the supplied prompt unchanged in meaning; select endpoint flags, size, quality, count, format, and output path from explicit requirements or conservative defaults.
4. **Execute via CLI**: call the packaged command directly.
5. **Report**: return output path(s), material flags or defaults, and actionable API errors.

## Requirements

- Python 3.11+ with `openai>=1.55`.
- Pillow for chroma-key background removal only.
- `OPENAI_API_KEY` for the default OpenAI endpoint. Calls may incur API charges.
- Do not reinstall dependencies, overwrite skill folders, create or modify `.env`, or write API keys unless the user explicitly requests setup.

## CLI

```bash
python "$SKILL_DIR/scripts/src/gpt_image_cli/cli.py" -p "PROMPT" [-f OUT] [-i REF...] [-m MASK] [options]
```

## Key and cost rules

- The CLI reads `OPENAI_API_KEY` from process env, then `.env`, then `~/.env`, without overriding an existing environment value.
- Set `OPENAI_BASE_URL` in the environment to use a compatible endpoint. The OpenAI API is the default.
- If the host has platform-managed image generation and that is the selected backend, use the host capability instead of this CLI.
- If `OPENAI_API_KEY` is unset, report it; do not write or print secrets.
- Respect a user's request to avoid local-key use. Do not work around their credential choice.

## Flags

| Flag | Values | Use |
|---|---|---|
| `-p, --prompt` | string | Required prompt or edit instruction |
| `-f, --file` | path | Output path; auto-named if omitted |
| `-i, --image` | repeatable path | Use edits endpoint; supports multiple references |
| `-m, --mask` | PNG path | Inpaint with alpha mask; requires `-i` |
| `--model` | default `gpt-image-2` | Image model |
| `--size` | `1k`, `2k`, `4k`, `portrait`, `landscape`, `square`, `wide`, `tall`, or literal | Canvas size |
| `--quality` | `low`, `medium`, `high`, `auto` | Cost and quality |
| `-n, --n` | integer | Number of images |
| `--background` | `auto`, `opaque` | Background behavior; use `opaque` for chroma-key removal |
| `--remove-background` | flag | After the API response, run the bundled chroma-key remover on every output and replace each keyed PNG/WebP with its alpha result |
| `--moderation` | `auto`, `low` | Generation moderation setting |
| `--input-fidelity` | `low`, `high` | Edit fidelity; dropped for `gpt-image-2`, which rejects it |
| `--format` | `png`, `jpeg`, `webp` | Output encoding |
| `--compression` | `0-100` | JPEG or WebP compression |
| `--user` | string | Optional end-user identifier |

Quality policy:

- `low`: cheap drafts, broad exploration, many variants.
- `medium`: normal exploration, style probing, balanced cost.
- `high`: final assets, Chinese text, posters, diagrams, UI, paper figures, dense labels.

Size policy:

- default or social square: `1k` / `1024x1024`
- poster, mobile, or beauty: `portrait`
- landscape, gameplay, or photo: `landscape`
- print or paper figure: `2k`
- widescreen hero: `4k`
- vertical story or banner: `tall`

Timeout policy:

- `1k`, `portrait`, `landscape`, or `square`: **180000 ms** (3 minutes)
- `2k`, `4k`, or multi-image batches (`-n > 1`): **360000 ms** (6 minutes)

## Endpoint routing

| Mode | Trigger | Endpoint |
|---|---|---|
| Text-to-image | no `-i` | `/v1/images/generations` |
| Reference edit | one or more `-i` | `/v1/images/edits` |
| Inpaint | `-i` + `-m` | `/v1/images/edits` with mask |

Surface enough of API errors for debugging. Exit codes are `0` for success, `1` for API error or refusal, and `2` for invalid arguments or a missing key.

## Transparent-background workflow

Use chroma-key removal for transparent assets. The only supported path is `--background opaque --remove-background`.

Default sequence:

1. Choose a key color unlikely to appear in the subject: default to `#00ff00`, use `#ff00ff` for green subjects, and avoid blue for blue subjects.
2. Append only the following execution constraints to the supplied prompt, replacing the key color when needed:

```text
Create the requested subject on a perfectly flat solid #00ff00 chroma-key background for background removal.
The background must be one uniform color with no shadows, gradients, texture, reflections, floor plane, or lighting variation.
Keep the subject fully separated from the background with crisp edges and generous padding.
Do not use #00ff00 anywhere in the subject.
No cast shadow, no contact shadow, no reflection, no watermark, and no text unless explicitly requested.
```

3. Generate a PNG with `--background opaque --remove-background`. The CLI flag does not modify the prompt or decide whether chroma-key removal is appropriate; it only applies the bundled post-processor after generation. Continue to use the normal skill judgment above to decide when to pass it.
4. The flag invokes the bundled helper with the system workflow's calibrated defaults, equivalent to:

```bash
python "$SKILL_DIR/scripts/remove_chroma_key.py" \
  --input generated.png \
  --out transparent.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

Use the helper command directly only when post-processing an image that already exists. For a new CLI generation, prefer `--remove-background` so generation and post-processing share one command. The flag supports batches and processes every returned image. It requires Pillow and a final `.png` or `.webp` output; it preserves the keyed source at the requested path if post-processing fails.

5. Verify an alpha channel exists, the corners are transparent, subject coverage is plausible, interior detail remains intact, and no obvious key-color fringe is present.
6. If a thin fringe remains, retry once with `--edge-contract 1`. Use `--edge-feather 0.25` only when the edge is visibly stair-stepped and the subject is not shiny or reflective.

Write the final output as `.png` or `.webp` to preserve alpha. Never overwrite an existing output unless explicitly requested; use `--force` only with authorization. If the matte removes subject details or the subject contains the key color, regenerate with a contrasting key color instead of increasing tolerance aggressively.

Chroma-key removal is unsuitable for hair, fur, feathers, smoke, glass, liquids, translucent materials, reflective objects, soft shadows, realistic product grounding, or subjects that conflict with every practical key color. If the chroma-key result fails validation or the subject is unsuitable, report the limitation instead of switching models or inventing another transparency path.

### `remove_chroma_key.py` options

| Option | Meaning |
|---|---|
| `--input PATH` | Required source image |
| `--out PATH` | Required `.png` or `.webp` alpha output |
| `--key-color HEX` | Exact key color; default `#00ff00` |
| `--auto-key none\|corners\|border` | Sample the key color instead; prefer `border` for generated images |
| `--tolerance 0..255` | Hard-key distance; default `12` |
| `--soft-matte` + `--transparent-threshold` / `--opaque-threshold` | Enable a smooth alpha ramp; defaults `12` / `96`, while this workflow uses `12` / `220` |
| `--despill`, `--spill-cleanup` | Equivalent flags that reduce key-color edge spill |
| `--edge-contract 0..16`, `--edge-feather 0..64` | Shrink or soften the alpha edge |
| `--force` | Overwrite an existing output |

## API reference

Read `references/openai-cookbook.md` only when API behavior, supported parameters, or model semantics are uncertain. Do not use it to expand or rewrite the supplied prompt.

## Verification

- Before calling the API, confirm endpoint mode, size, quality, output path, and required reference or mask files.
- For edits and inpainting, verify every `-i` path and any `-m` path exist.
- After the CLI call, report the paths printed by the CLI and surface stderr on failure.
- For transparent outputs, follow the alpha, corner, coverage, interior-detail, and fringe checks in the transparent-background workflow.

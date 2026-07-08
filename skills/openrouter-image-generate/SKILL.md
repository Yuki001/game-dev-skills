---
name: openrouter-image-generate
description: Generate images through OpenRouter's dedicated Image API. Use this skill whenever the user wants to create, render, generate, or save images with OpenRouter, including text-to-image, image-to-image/reference images, choosing OpenRouter image models, listing image models, setting resolution/aspect ratio/quality/output format, or passing provider-specific image options. Prefer the bundled Python script so API options are passed explicitly as command-line arguments instead of hand-written ad hoc curl requests.
---

# OpenRouter Image Generation

Use this skill to generate images with OpenRouter's dedicated Image API and save the returned base64 image bytes to files.

## Default workflow

1. Use the OpenRouter API key from the current environment first. If it is missing, rely on the bundled script's automatic lookup of the nearest project `.env` file containing `OPENROUTER_API_KEY`, unless the user explicitly provides another environment variable name or env file path.
2. Pick a model from the user's request. If no model is specified, use `bytedance-seed/seedream-4.5` as a practical default and mention that the user can override it.
3. Use the bundled script at `scripts/openrouter_image_generate.py` rather than constructing requests manually.
4. Save generated images to a user-visible output directory, defaulting to the current working directory if the user did not specify one.
5. Do not print API keys. Do not put API keys directly on the command line because shell history may capture them.

## Bundled script

Run from this skill directory or pass the script path directly:

```bash
python scripts/openrouter_image_generate.py generate \
  --prompt "a red panda astronaut floating in space, studio lighting" \
  --model "bytedance-seed/seedream-4.5" \
  --resolution 2K \
  --aspect-ratio 16:9 \
  --output-dir ./outputs
```

The script reads `OPENROUTER_API_KEY` from the current environment first. If it is not set, it automatically searches from the current working directory upward for the nearest `.env` file and reads `OPENROUTER_API_KEY=...` from there. Use `--api-key-env MY_OPENROUTER_KEY` if the key uses a different variable name, or `--env-file ./path/to/.env` to force a specific env file.

## Common generation options

Pass only the options the user asks for or that are
 clearly needed:

- `--prompt TEXT` is required for generation.
- `--model MODEL_ID` defaults to `bytedance-seed/seedream-4.5`.
- `--n 1..10` requests multiple images when supported by the endpoint.
- `--resolution 512|1K|2K|4K` sets the normalized resolution tier.
- `--aspect-ratio 1:1|16:9|9:16|4:3|3:4|...` sets the normalized ratio.
- `--size 2048x2048` or `--size 2K` is the shorthand alternative. Do not combine explicit pixel sizes with mismatched `--resolution` or `--aspect-ratio`.
- `--quality auto|low|medium|high` controls provider quality where supported.
- `--output-format png|jpeg|webp|svg` controls the saved file type when supported.
- `--background auto|transparent|opaque` sets background where supported.
- `--output-compression 0..100` applies to jpeg/webp where supported.
- `--seed INTEGER` requests deterministic generation where supported.
- `--reference PATH_OR_URL` can be passed multiple times for image-to-image/reference inputs. Local files are converted to data URLs.
- `--provider-options-json '{"black-forest-labs":{"steps":40,"guidance":3}}'` passes provider-specific options under `provider.options`.
- `--provider-options-file options.json` is safer for larger provider options.
- `--raw-json payload.json` can merge additional OpenRouter-compatible request fields into the payload.
- `--dry-run` prints the request payload without making a network call.

## Model discovery

List available image models:

```bash
python scripts/openrouter_image_generate.py models
```

Show endpoint/provider capabilities for one model:

```bash
python scripts/openrouter_image_generate.py endpoints --model bytedance-seed/seedream-4.5
```

Use discovery before passing unusual parameters. OpenRouter image models differ by provider, and unsupported parameters may be ignored or rejected.

## Output behavior

The script writes a single generated image as `<output-prefix>.<ext>` and multiple generated images as `<output-prefix>_001.<ext>`, `<output-prefix>_002.<ext>`, and so on. SVG outputs are decoded as text bytes and saved with `.svg`; raster outputs are decoded from base64 and saved with the requested or returned media type.

The script also writes a JSON metadata file by default with the request payload minus secrets, OpenRouter `usage`, created timestamp, and generated file paths. Use `--no-metadata` to skip it.

## Streaming

Use `--stream` only when the selected endpoint supports streaming. The script saves completed images from streaming responses and can optionally save partial previews with `--save-partials`.

## Safety and cost

Image generation can bill the user's OpenRouter account. Before running a real generation command, make sure the requested model, image count, and output options match the user's intent. Use `--dry-run` when uncertain.

## 40x troubleshooting notes

These are real failure modes observed while testing OpenRouter image generation:

- `400` with `n: must be exactly 1` means the model advertises or accepts an `n` parameter but that endpoint/provider only allows one image per request. Retry with `--n 1`, or choose a model whose `supported_parameters.n.max` is greater than 1.
- `400` with `Streaming is not supported with n > 1` means OpenRouter/OpenAI streaming can only be used for a single image. For multiple images, remove `--stream` or generate one image per streaming request.
- `400` with provider-specific size or resolution messages means the normalized options still need to satisfy the upstream provider's constraints. For example, Seedream 4.5 rejected 1K square output because the image size was below its minimum pixel count; increasing to `--resolution 2K` fixed the request.
- `429` from an upstream provider means the provider is rate-limiting or temporarily capacity-limited. This is not a script bug; retry later, use a lower-cost/lower-demand model, or switch providers.
- A model may accept `--n 2` but still return only one image. Trust the response length when naming files and metadata; if the user specifically needs multiple outputs, choose a model that has been observed returning multiple images, such as `recraft/recraft-v4.1-pro`.

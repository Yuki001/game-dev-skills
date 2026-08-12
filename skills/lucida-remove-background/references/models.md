# BGR Model Registry

Consult this reference only for alternate-model selection or local-checkpoint troubleshooting. Prefer `lucida` and `birefnet-hr` for the main workflow.

## Directly loaded models

| CLI model | Source | Input size | Choose it for |
| --- | --- | ---: | --- |
| `lucida` | `egeorcun/lucida` | 1024 | Default; transparency, camouflage, text, glow, illustration, and design |
| `rmbg-2.0` | `briaai/RMBG-2.0` | 1024 | Solid objects, product photos, and hair |
| `birefnet-hr` | `ZhengPeng7/BiRefNet_HR` | 2048 | High-resolution general segmentation when additional compute is acceptable |
| `inspyrenet` | `transparent-background` engine | Engine-managed | Complex scenes and thin or perforated structures |

The first use of a Hugging Face-backed model downloads and caches its weights. If loading fails with a gated-model or HTTP 401 error, accept the model license at `https://huggingface.co/<model-id>`, run `huggingface-cli login`, and retry.

`rmbg-2.0` is a gated model.

## Local checkpoint entries

These entries construct the `ZhengPeng7/BiRefNet_HR` architecture and then replace all weights with a local training checkpoint. Paths are relative to the current working directory.

| CLI model | Required checkpoint |
| --- | --- |
| `bgr-v1` | `data/checkpoints/epoch_1.pth` |
| `bgr-v2` | `data/checkpoints/epoch_2.pth` |
| `bgr-v3` | `data/checkpoints/epoch_3.pth` |
| `bgr-v4` | `data/checkpoints/epoch_4.pth` |
| `lucida-v5` | `data/checkpoints/epoch_5.pth` |
| `lucida-v6` | `data/checkpoints/epoch_6.pth` |
| `lucida-v7` | `data/checkpoints/epoch_7.pth` |
| `lucida-v8` | `data/checkpoints/epoch_8_v8bug.pth` |
| `lucida-v9` | `data/checkpoints/epoch_8_v9.pth` |
| `lucida-v10` | `data/checkpoints/epoch_9.pth` |
| `lucida-v11probe` | `data/checkpoints/epoch_10.pth` |
| `lucida-v11` | `data/checkpoints/epoch_11.pth` |
| `lucida-v12` | `data/checkpoints/epoch_12.pth` |
| `lucida-v13` | `data/checkpoints/epoch_13.pth` |
| `lucida-soup913` | `data/checkpoints/soup_9_13.pth` |
| `lucida-soup91113` | `data/checkpoints/soup_9_11_13.pth` |
| `lucida-soup` | `data/checkpoints/soup_11_12_13.pth` |

Do not select a local checkpoint entry merely because its version number is higher. Use it only when the user specifically requests it or a matching checkpoint has been supplied and its provenance is known.

## Registry variants

The registry also accepts a `+refine` suffix, such as `lucida+refine`. Prefer the CLI's explicit `--refine` flag for clarity:

```text
bgr remove "input.png" -o "output.png" --model lucida --refine
```

Official sources:

- <https://github.com/egeorcun/lucida>
- <https://huggingface.co/egeorcun/lucida>

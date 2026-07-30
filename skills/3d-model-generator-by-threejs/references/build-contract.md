# Build module contract

## Required export

Create a side-effect-free ESM module containing one named export:

```js
export async function buildModel(ctx) {
  const { THREE, builders, helpers, rng, logger } = ctx;
  const root = new THREE.Group();

  return {
    root,
    animations: [],
    metadata: {
      name: 'model-name',
      units: 'meters',
      upAxis: 'Y'
    }
  };
}
```

The function may also return a `THREE.Object3D` directly. Prefer the object form when animations or metadata are present.

## Context

| Field | Purpose |
|---|---|
| `apiVersion` | Runtime contract version. Currently `1`. |
| `THREE` | Pinned Three.js namespace for custom geometry and scene operations. |
| `builders` | High-level primitive and material constructors. |
| `helpers` | Placement, repetition, mirroring, orientation, and unit utilities. |
| `rng` | Seeded deterministic random-number generator. |
| `logger` | Runtime logger. |

## Result

| Field | Requirement |
|---|---|
| `root` | A `THREE.Object3D`, usually `Group` or `Scene`. |
| `animations` | Optional array of `THREE.AnimationClip`. |
| `metadata.name` | Optional asset name used as the default output basename. |
| `metadata.units` | `meters`, `centimeters`, or `millimeters`. Default: `meters`. |
| `metadata.upAxis` | `Y` or `Z`. Default: `Y`. |
| `metadata.seed` | Optional seed recorded for reproducibility. |

The pipeline wraps non-Scene roots in a `THREE.Scene`, updates world matrices, validates the result, and sends the normalized scene to each exporter.

## Determinism

- Use `ctx.rng.next()`, `float()`, `int()`, or `pick()`.
- Do not use `Math.random()`, time, environment state, or network data.
- Keep all dimensions and segment counts explicit or derived from stable inputs.

## Safety boundary

Generated modules must not:

- contain static or dynamic imports;
- access `process`, `require`, file APIs, child processes, sockets, or HTTP;
- use `fetch`, `XMLHttpRequest`, or `WebSocket`;
- invoke `eval` or `Function`;
- start timers or background work;
- write files or export models themselves.

The runtime performs a conservative source scan before import. Treat this scan as defense in depth, not a replacement for an OS or agent sandbox.

## Modeling conventions

- Use right-handed coordinates with Y up.
- Model near the origin and place the lowest intended contact surface on Y=0.
- Use radians for Three.js rotations. Use `helpers.deg(value)` for degree input.
- Name important groups and meshes.
- Prefer one shared geometry/material for repeated identical parts.
- Avoid negative scale for final printable geometry unless it is baked and normals are corrected.
- Do not add review-only cameras, grids, lights, or backgrounds to the returned asset root.

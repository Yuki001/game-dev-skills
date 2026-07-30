# Standalone preview rendering

Render an exported model to a PNG without starting a browser or WebGL server:

```text
node scripts/render-preview.mjs --model <task-dir>/model.glb --out <task-dir>/preview.png
```

The command reads GLB, glTF, OBJ, or STL and renders an orthographic `iso` view by default.

## Contact sheets

Pass comma-separated views to render a labeled contact sheet:

```text
node scripts/render-preview.mjs --model <task-dir>/model.glb --out <task-dir>/preview.png --views iso,front,back,left,right,top
```

Supported views are `iso`, `front`, `back`, `left`, `right`, and `top`.

## Image options

```text
--width 1200
--height 720
--background #091018
```

Width and height must be integers from 64 to 4096. Output must use a `.png` extension.

## Rendering scope

The renderer is deterministic and uses mesh triangles, transforms, material colors, vertex colors, opacity, and simple directional shading. It does not require browser automation or native graphics dependencies.

Use the interactive viewer when exact textures, physically based lighting, animation, transparency ordering, or shader behavior must be reviewed.

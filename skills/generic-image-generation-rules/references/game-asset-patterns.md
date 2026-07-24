# Game asset patterns

Use these as brief skeletons, not copy-paste style incantations.

## Inventory icon or isolated prop

Plan:

- final display size and source size;
- single dominant silhouette;
- orientation and occupied bounds;
- readable material separation;
- transparent output and shadow policy;
- icon border/frame delivered separately unless requested.

Prompt slots:

```text
[square canvas and source resolution]
[one named object + orientation]
[genre and functional history: pristine, worn, enchanted, improvised]
[shape language and material zones]
[light direction + value contrast]
[transparent isolation]
[small-size readability and crop constraints]
```

Evaluation emphasis: silhouette, crop, recognizability, edge quality, value separation.

## Character concept or reference sheet

Plan identity anchors: face shape, hair silhouette, body proportions, costume layers, palette swatches, signature equipment, and forbidden drift.

For a sheet, allocate regions before detail:

```text
front / side / back turnaround
expressions
equipment close-ups
palette
scale marker
short annotations only when exact text is supplied
```

Evaluation emphasis: identity across views, plausible topology, costume continuity, neutral camera, readable parts.

## Character sprite

Specify:

- projection: side, front, top-down, isometric, or 3/4;
- facing direction and ground line;
- exact cell and maximum occupied bounds;
- canonical height in pixels;
- pivot/foot contact;
- animation state and frame phases;
- palette and outline policy;
- no camera movement.

Generate a neutral canonical frame first. Use it as the identity reference for subsequent frames.

## Tile or tileset

Specify tile size, projection, seamless edges, neighbor rules, padding/extrusion, and material variants. Generate or construct tiles in a way that allows deterministic edge testing.

Evaluation emphasis:

- opposite borders match;
- no directional lighting discontinuity unless designed;
- scale and texel density remain constant;
- transitions/corners cover the intended adjacency rules;
- no objects cross a tile boundary accidentally.

## Environment or background

Plan playable/readable zones separately from atmosphere:

```text
camera/projection and horizon
foreground gameplay plane
midground navigation landmarks
background depth layers
value grouping and focal path
parallax layer requirements
lighting and weather
forbidden visual clutter behind gameplay
```

Evaluation emphasis: navigation readability, scale cues, depth separation, collision-relevant shapes, parallax seams.

## UI element

Prefer SVG or deterministic composition for exact geometry and text. Separate states such as normal, hover, pressed, disabled, selected, cooldown, and alert.

Evaluation emphasis: legibility at target DPI, consistent padding, state differentiation, contrast, nine-slice safety, and localization expansion.

## VFX sprite

Specify effect family, source/emitter, anticipation, peak, dissipation, frame count, blend mode, background used for review, and whether the delivered pixels are premultiplied.

Evaluation emphasis: temporal arc, stable center/pivot, no frame-edge clipping, usable alpha or clean additive composition, smooth energy decay, and visibility on both light and dark test backgrounds.

## Pixel art

Treat pixel art as a constrained production format:

- define native canvas and sprite bounds before generation;
- select a palette budget;
- prohibit antialiasing and subpixel transforms;
- use clusters and intentional single-pixel accents;
- scale previews with nearest-neighbor only;
- inspect at 1× and enlarged integer scale;
- normalize generated drafts manually or deterministically before acceptance.

“Pixel-art style” at 1024 px is not automatically production pixel art.

## Cohesion across an asset set

Create a style bible from accepted anchors:

- projection and camera;
- canonical object/character scale;
- outline width and color;
- shadow hue and light direction;
- palette roles;
- material shorthand;
- detail density at target size;
- transparent padding and pivot conventions.

Evaluate new assets against both their individual rubric and this set-level bible.

## Concrete prompt references

Adapt these slots to the project style bible and delivery contract.

### Side-view character canonical frame

Native:

```text
Create one game-ready 2D side-view character sprite on a 256×256 canvas.
SUBJECT: an original young adult desert courier, full body, facing right, neutral idle stance, both feet on the same ground line. Distinctive anchors: crescent hood silhouette, short sand-colored cloak, teal sash, compact leather satchel, dark ankle boots.
PROPORTIONS: stylized 5.5-head figure, hands and feet readable, no foreshortening.
RENDERING: clean hand-painted indie action-platformer sprite, firm dark-brown outer contour, two-step cel shading, limited sand/teal/umber palette.
CONSISTENCY: orthographic side camera, no perspective change, no wind, no motion pose.
OUTPUT: transparent background, 24 px safe padding, no cast shadow, no text, one character only.
```

Danbooru-style:

```text
game sprite, 1girl, full body, solo, side view, facing right, standing,
neutral pose, hood, short cloak, teal sash, satchel, ankle boots,
desert traveler, stylized proportions, clean lineart, cel shading,
limited palette, centered, transparent background
```

### Isometric building

```text
Create one game-ready isometric building asset on a 768×768 square canvas: a compact fantasy alchemist shop, strict 2:1 isometric projection, front-left and front-right walls visible, base aligned to an isometric diamond. Readable landmarks: crooked copper chimney, round green-glass window, herb bundles, small awning, reinforced wooden door. Hand-painted strategy-game rendering, chunky shapes, warm plaster / dark timber / oxidized copper palette, upper-left daylight, shadows falling consistently down-right. Isolated with true transparency; no ground plane beyond the building footprint, no people, sign text, border, or cropped roof.
```

### Seamless ground tile

```text
Create a seamless 128×128 top-down game texture tile of worn mossy flagstones. Orthographic camera, uniform texel density, broad readable stone clusters, narrow dark grout, restrained green moss in less than 20% of the area, diffuse overcast lighting with no directional cast shadows. All four edges must tile continuously; no unique central landmark, border, text, debris crossing only one edge, or perspective.
```

Generate multiple variants, then test exact edge continuity deterministically. A prompt cannot prove seamlessness.

### VFX impact sequence

```text
Create a 6-frame game VFX concept sequence for a compact arcane impact, arranged left-to-right on a strict 6×1 review sheet. Each cell represents: 1 anticipation spark, 2 contact flash, 3 expanding violet ring, 4 fragmented energy shards, 5 fading wisps, 6 nearly empty residual motes. Fixed emitter at cell center, no camera movement, consistent scale, high-contrast cyan core / violet edge, readable on dark and light backgrounds. Transparent outside the effect, no smoke backdrop, no text, no cell borders in the delivered frames.
```

Treat direct sheet generation as the normal first attempt. Slice and evaluate every cell; normalize pivots/alpha and repack only after the grid and phases pass.

### UI nine-slice panel

Prefer SVG or deterministic construction:

```text
Create a scalable fantasy inventory panel as clean SVG: 256×160 viewBox, symmetric 20 px corner ornaments, 12 px safe stretch regions along all four edges, dark indigo fill, muted brass outline, subtle inner highlight, no text and no embedded raster image. Keep corner geometry outside the stretch regions and ensure the center can expand without visible seams.
```

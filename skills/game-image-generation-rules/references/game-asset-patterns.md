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

Choose the sheet's purpose before allocating regions:

- use a **turnaround/reference sheet** for production continuity and neutral orthographic views;
- use an **expression sheet** for facial consistency across named emotions;
- use an **exploratory concept sheet** for alternatives, measurements, annotations, and unresolved design decisions.

Do not present exploratory sketches as a production turnaround. A production sheet needs compatible scale, ground line, camera, anatomy, costume topology, and equipment placement across views.

Use `game-gallery-patterns.md` when the deliverable is a multi-character roster or a board that mixes characters with environments, maps, or props.

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

## Static sprite collection

Use this pattern when one regular sheet contains multiple independent assets rather than sequential animation frames. Define:

- asset family, intended gameplay use, and required variety;
- rows, columns, cell size, gutters, and row-major asset order or identifiers;
- projection, facing convention, canonical scale, occupied bounds, and padding;
- shared palette, outline, shading, light direction, and alpha policy;
- forbidden duplicates and per-cell acceptance criteria at native display size.

Do not assign animation phases, duration, FPS, loop mode, or temporal-continuity requirements. Inspect the full collection for set-level cohesion, then slice and validate every cell as an independent asset. Reject missing, duplicated, merged, crossed, clipped, or stylistically drifting cells.

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

Use `game-hud-patterns.md` when the deliverable is a complete gameplay screen in which scene, camera, visible game state, and HUD must be composed together.

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

For a sprite sequence or directional set:

- build or select one shared palette across the whole set rather than quantizing each frame independently;
- merge near-colors consistently so a shade does not flicker between neighboring frames;
- select or infer one pixel-grid scale, then snap every frame to the same grid size and origin;
- compare identity and palette before quantization because aggressive reduction can hide source drift;
- use binary alpha only when the target pixel-art style requires a hard mask, not for soft VFX or deliberately translucent pixels.

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

### Official character turnaround sheet

```text
Create one landscape game-character reference sheet on a 1536×1024 canvas with a clean white background and an organized official-setting-material layout.
IDENTITY: [original character or supplied appearance reference], with fixed face shape, hair silhouette, body proportions, costume layers, palette, and signature equipment.
TURNAROUND: show full-body front, true orthographic side, and back views in neutral stance, at identical scale, camera height, and ground line. These must be three distinct views, not repeated three-quarter poses or mirrored approximations.
SUPPORTING REGIONS: a small row of named facial expressions, clothing and equipment close-ups, palette swatches, and a scale marker. Include a short setting note only when exact copy is supplied.
CONSISTENCY: preserve anatomy, costume seams, closures, accessories, material zones, colors, handedness, and equipment attachment points across every view.
OUTPUT: crisp readable layout, generous gutters, no scenic background, dynamic action pose, perspective distortion, cropped feet, duplicate views, or invented labels.
```

Evaluate view identity and costume topology before judging illustration polish.

### Character expression sheet

```text
Create one strict 4×4 facial-expression sheet for the same original game character. Use one identical head-and-shoulders crop, camera angle, scale, hairstyle, clothing neckline, palette, and light direction in all 16 cells. Expressions in row-major order: happy, sad, angry, surprised, shy, speechless, mischievous grin, contemplative, curious, proud, hurt, disdainful, confused, frightened, crying, and affectionate joy. Change only expression-related facial features and subtle head gesture. Use clean equal gutters and no merged cells, duplicate expressions, identity drift, costume changes, scenic backgrounds, or unreadable generated labels.
```

If labels are required, supply their exact text; otherwise identify expressions outside the generated image by row and column.

### Exploratory character concept sheet

```text
Create one portrait-oriented exploratory game-character concept sheet for an original elven archer. Place one large full-body hero sketch at center, then surround it with two side-view cloak variations, three small action-pose thumbnails, a bow and quiver construction study with supplied measurements, clothing-detail callouts, material swatches, and restrained forest-green / silver color tests. Use loose graphite construction lines with precise ink accents and light watercolor tests. Keep the character's face, proportions, costume motifs, and equipment language recognizable across studies, while clearly presenting alternatives as alternatives. The page should read as an art-director development sheet, not a final turnaround or unrelated sketch collage. Add annotations only when exact text is supplied.
```

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

### Static pixel-art vehicle collection

```text
Create one strict 10×10 static pixel-art sprite collection on a canvas sized for 100 equal cells.
CONTENTS: one distinct original retro vehicle per cell, including varied sedans, sports cars, utility vehicles, taxis, service vehicles, convertibles, and hot rods. Cells are independent assets, not animation frames.
LAYOUT: ten rows by ten columns, fixed row-major order, equal 64×64 native cells, one complete vehicle per cell, consistent occupied bounds, no gutters unless the contract supplies them, no merged or crossed cells.
CONSISTENCY: one 3/4 top-down orthographic projection, matching scale, outline policy, upper-left light direction, and shared palette logic across all vehicles.
RENDERING: crisp 16-bit-inspired pixel art, deliberate pixel clusters, no antialiasing or subpixel detail, approximately 16 colors or fewer per vehicle while preserving one coherent set-level palette.
OUTPUT: true transparent background outside each vehicle; no visible grid, labels, cast-shadow plates, duplicate vehicles, cropped silhouettes, or franchise logos.
```

Inspect the complete grid, then slice it into independent assets and validate every cell for dimensions, alpha, clipping, padding, projection, scale, palette, and recognizability at native size. A generated high-resolution pixel-art look still requires deterministic reduction, palette control, and nearest-neighbor handling before it qualifies as production pixel art.

### Isometric building

```text
Create one game-ready isometric building asset on a 768×768 square canvas: a compact fantasy alchemist shop, strict 2:1 isometric projection, front-left and front-right walls visible, base aligned to an isometric diamond. Readable landmarks: crooked copper chimney, round green-glass window, herb bundles, small awning, reinforced wooden door. Hand-painted strategy-game rendering, chunky shapes, warm plaster / dark timber / oxidized copper palette, upper-left daylight, shadows falling consistently down-right. Isolated with true transparency; no ground plane beyond the building footprint, no people, sign text, border, or cropped roof.
```

### Isometric environment cluster

```text
Create one square isometric environment cluster showing a compact two-block market district. Use precise 30° screen axes and one fixed orthographic camera. Include a corner cafe, small bookstore, bakery stall, fountain plaza, bicycle, planters, food cart, and a few scale-reference pedestrians. Keep building footprints, doors, paths, roof heights, and props readable as a strategy-game environment block. Use clean geometric forms, consistent upper-left ambient light, shadows falling down-right, restrained terracotta / cream / sage / dusty-blue palette, and controlled ambient occlusion. Present the cluster on one unobtrusive background or ground footprint with no perspective drift, floating pieces, illegible signs, cropped buildings, or conflicting light directions.
```

Treat this as one environment cluster. Generate isolated buildings separately when the engine needs individually placeable assets.

### Isometric grid map

```text
Create one square isometric fantasy-village map concept based on an explicit gameplay grid. Use fixed 3×3-meter world tiles, precise 30° screen axes, consistent elevation steps, and one orthographic camera. Include readable wooden houses, cobblestone paths, a central fountain, and one corner raised by a 2-meter grassy level connected with stairs. Preserve clear traversable routes, building footprints, tile boundaries, scale, texel density, upper-left sunlight, and down-right shadows. The result should read as a handcrafted strategy-game map, not a perspective illustration. Avoid hidden paths, impossible elevation joins, objects crossing intended boundaries, inconsistent building scale, and decorative clutter over playable areas.
```

The prompt defines the intended grid but cannot prove alignment, adjacency, or path validity. Verify those properties deterministically or rebuild the accepted concept in the level pipeline.

### Seamless ground tile

```text
Create a seamless 128×128 top-down game texture tile of worn mossy flagstones. Orthographic camera, uniform texel density, broad readable stone clusters, narrow dark grout, restrained green moss in less than 20% of the area, diffuse overcast lighting with no directional cast shadows. All four edges must tile continuously; no unique central landmark, border, text, debris crossing only one edge, or perspective.
```

Generate multiple variants, then test exact edge continuity deterministically. A prompt cannot prove seamlessness.

### Equirectangular panorama or skybox source

```text
Create one strict 2:1 equirectangular game-environment panorama at 4096×2048 for spherical viewing. Scene: a dense prehistoric jungle with a level horizon, layered fern-covered trees, a winding river, distant large-animal silhouettes, canopy birds, warm late-afternoon shafts, and light atmospheric haze. Compose in full 360° space: the left and right edges must wrap continuously in geometry, value, color, lighting, and object continuation. Keep major landmarks away from the seam and poles, preserve navigable depth cues around the horizon, and avoid visible edge breaks, duplicated seam objects, pinched zenith/nadir details, flat wallpaper perspective, text, borders, or camera-frame artifacts.
```

Inspect the panorama in an equirectangular viewer and test the horizontal wrap. A prompt cannot guarantee a seamless spherical projection.

### VFX impact sequence

```text
Create a 6-frame game VFX concept sequence for a compact arcane impact, arranged left-to-right on a strict 6×1 review sheet. Each cell represents: 1 anticipation spark, 2 contact flash, 3 expanding violet ring, 4 fragmented energy shards, 5 fading wisps, 6 nearly empty residual motes. Fixed emitter at cell center, no camera movement, consistent scale, high-contrast cyan core / violet edge, readable on dark and light backgrounds. Transparent outside the effect, no smoke backdrop, no text, no cell borders in the delivered frames.
```

Route this sequence through `sprite-sheet/sprite-sheets.md`. Prefer video-derived frames when video-generation and frame-extraction capabilities are both available, whether supplied by one backend or two; otherwise use a compatible motion-reference sheet, and use the direct sheet prompt above only as the final generation route. Evaluate every frame before normalizing and packing.

### UI nine-slice panel

Prefer SVG or deterministic construction:

```text
Create a scalable fantasy inventory panel as clean SVG: 256×160 viewBox, symmetric 20 px corner ornaments, 12 px safe stretch regions along all four edges, dark indigo fill, muted brass outline, subtle inner highlight, no text and no embedded raster image. Keep corner geometry outside the stretch regions and ensure the center can expand without visible seams.
```

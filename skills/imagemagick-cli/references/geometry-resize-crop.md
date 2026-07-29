# Geometry, resize, crop, and canvas

## Contents

- [Resize decision table](#resize-decision-table)
- [Resize operators](#resize-operators)
- [High-quality resizing](#high-quality-resizing)
- [Filter artifacts and expert controls](#filter-artifacts-and-expert-controls)
- [Orientation and read-time hints](#orientation-and-read-time-hints)
- [Density and physical dimensions](#density-and-physical-dimensions)
- [Crop, page, and repage](#crop-page-and-repage)
- [Trim and borders](#trim-and-borders)
- [Advanced trim and edge removal](#advanced-trim-and-edge-removal)
- [Extent, splice, chop, and shave](#extent-splice-chop-and-shave)
- [Tile and slice workflows](#tile-and-slice-workflows)
- [Thumbnail framing patterns](#thumbnail-framing-patterns)
- [Verification](#verification)

## Resize decision table

| Goal | Pattern |
|---|---|
| Fit within box | `-resize WxH` |
| Fit, shrink only | `-resize "WxH>"` |
| Fit, enlarge only | `-resize "WxH<"` |
| Fill and center-crop | `-resize "WxH^" -gravity center -extent WxH` |
| Force exact dimensions | `-resize "WxH!"` |
| Scale by percentage | `-resize 50%` |
| Limit total pixels | `-resize "2MP@"` |
| Thumbnail and discard ancillary data | `-thumbnail "WxH>" -strip` |
| Pixel-art nearest neighbor | `-filter point -resize "800%"` or `-sample` |
| Fast rough scaling | `-scale` |
| Replicate/drop rows and columns | `-sample` |

Typical photo:

```bash
magick input.jpg -auto-orient -resize '1600x1600>' -quality 88 output.jpg
```

Exact social tile:

```bash
magick input.jpg -auto-orient -resize '1200x630^' \
  -gravity center -extent 1200x630 output.jpg
```

Pad instead of crop:

```bash
magick input.png -resize '1200x630>' \
  -background '#111827' -gravity center -extent 1200x630 output.png
```

## Resize operators

`-resize` uses a resampling filter and is the general choice:

```bash
magick input.png -resize 640x480 output.png
```

`-thumbnail` is optimized for thumbnails and removes some profiles:

```bash
magick input.jpg -thumbnail '320x320>' -strip thumb.jpg
```

`-scale` uses pixel averaging/replication:

```bash
magick input.png -scale 25% preview.png
```

`-sample` selects/replicates rows and columns, useful for crisp pixel art:

```bash
magick sprite.png -sample '800%' sprite-large.png
```

`-adaptive-resize` preserves sharper details for small changes:

```bash
magick input.png -adaptive-resize 90% output.png
```

`-liquid-rescale` performs seam carving when supported:

```bash
magick input.jpg -liquid-rescale 800x600 output.jpg
```

It can distort salient objects; use only when content-aware resizing is explicitly desired.

## High-quality resizing

Filter selection:

```bash
magick input.png -filter Lanczos -resize 40% output.png
magick input.png -filter Mitchell -resize 40% output.png
magick pixel-art.png -filter point -resize '1000%' pixel-art-large.png
```

Inspect available filters:

```bash
magick -list filter
```

For critical photographic resizing, use a linear-light or sigmoidal workflow:

```bash
magick input.jpg -colorspace RGB -resize 25% -colorspace sRGB output.jpg
```

Sigmoidal method:

```bash
magick input.jpg -colorspace RGB +sigmoidal-contrast 11.6933 \
  -resize 25% -sigmoidal-contrast 11.6933 -colorspace sRGB output.jpg
```

Test against representative imagery. Strong ringing filters can create halos near hard edges; use `-clamp` for HDRI builds when negative lobes are undesirable.

Post-resize sharpening:

```bash
magick input.jpg -resize '1600x1600>' -unsharp 0x0.75+0.75+0.008 output.jpg
```

Do not apply a fixed unsharp recipe blindly to line art, text, or already sharpened images.

## Filter artifacts and expert controls

Common resize failures:

| Artifact | Typical cause | Response |
|---|---|---|
| blocking/pixelation | too little source resolution or nearest sampling | use a reconstruction filter; do not expect invented detail |
| ringing/halos | negative-lobe sharp filter near hard edges | choose Mitchell/RobidouxSoft, reduce lobes, or adjust filter blur |
| aliasing/moiré | insufficient low-pass filtering during reduction | use a wider filter/support or preblur slightly |
| excessive blur | overly soft filter or repeated resizes | resize once from the best source and tune final sharpening |

Inspect the actual filter and support:

```bash
magick input.png -filter Lanczos \
  -define filter:verbose=true -resize 40% null:
```

Expert controls include:

```text
filter:blur
filter:lobes
filter:support
filter:window
filter:window-support
filter:b
filter:c
filter:sigma
```

Example, slightly soften a ringing-prone Lanczos reduction:

```bash
magick input.png -filter Lanczos -define filter:blur=1.05 \
  -resize 40% output.png
```

Cubic filters can be selected by B/C coefficients:

```bash
magick input.png -filter Cubic \
  -define filter:b=0.333333 -define filter:c=0.333333 \
  -resize 40% output.png
```

The second form approximates Mitchell-Netravali. Distortions use cylindrical/EWA filters rather than the orthogonal resize support model, so a named filter can behave differently under `-distort`. Tune on representative edges, fine texture, and the target scale; do not select by file size alone.

## Orientation and read-time hints

Normalize camera orientation before geometric operations:

```bash
magick photo.jpg -auto-orient -resize '1600x1600>' output.jpg
```

JPEG decoder hint before input:

```bash
magick -define jpeg:size=1000x1000 photo.jpg \
  -auto-orient -thumbnail '500x500>' thumb.jpg
```

Read only a PDF page at the required density:

```bash
magick -density 300 'document.pdf[2]' -resize '1600x1600>' page-3.png
```

Read modifier:

```bash
magick 'input.jpg[800x600]' output.png
magick 'large.tif[1000x700+200+300]' region.png
```

Decoder support for read-time geometry varies; verify dimensions and pixels.

## Density and physical dimensions

`-density` sets read/write resolution metadata or controls vector/page rasterization:

```bash
magick -density 300 input.pdf page.png
magick input.png -units PixelsPerInch -density 300 tagged.png
```

`-resample` changes pixels so physical size remains consistent at a new density:

```bash
magick scan.tif -units PixelsPerInch -resample 300 output.tif
```

Compute inches:

```bash
magick identify -format '%[fx:w/resolution.x] x %[fx:h/resolution.y] in\n' scan.png
```

Resolution units may be undefined. State assumptions before converting physical dimensions.

## Crop, page, and repage

Basic crop:

```bash
magick input.png -crop 800x600+100+50 +repage output.png
```

Gravity-relative crop:

```bash
magick input.jpg -gravity center -crop 800x600+0+0 +repage output.jpg
magick input.jpg -gravity southeast -crop 800x600+20+20 +repage output.jpg
```

Percentage crop:

```bash
magick input.png -gravity center -crop '80%x80%+0+0' +repage output.png
```

Crop to aspect ratio dynamically:

```bash
magick input.jpg -gravity center \
  -crop '%[fx:min(w,h*16/9)]x%[fx:min(h,w*9/16)]+0+0' +repage \
  -resize 1280x720 output.jpg
```

Test dynamic geometry on both portrait and landscape inputs.

Virtual canvas/page offsets can survive crop:

```bash
magick identify -format '%[page]\n' cropped.png
magick cropped.png +repage normalized.png
```

Keep page offsets for animation/layer placement; remove them for ordinary standalone outputs or before geometry that should use a fresh origin.

Reset page without changing pixels:

```bash
magick input.png +repage output.png
```

Set a virtual canvas:

```bash
magick input.png -repage 1200x800+100+50 output.miff
magick input.png -set page 1200x800+100+50 output.miff
```

Negative crop offsets do not mean “measure from the right/bottom” in every form. Prefer gravity for edge-relative crops:

```bash
magick input.png -gravity southeast -crop 800x600+0+0 +repage output.png
```

Extract quadrants around a point by using four explicit geometries or calculated widths/heights. A crop that misses the virtual canvas can return a one-pixel “missed image”; treat unexpected `1x1` output as an error in automation.

## Trim and borders

Trim pixels matching the corner/background:

```bash
magick input.png -trim +repage output.png
```

Allow near matches:

```bash
magick input.png -fuzz 5% -trim +repage output.png
```

Specify trim background from the top-left pixel:

```bash
magick input.png -bordercolor '%[pixel:p{0,0}]' -border 1 \
  -fuzz 5% -trim +repage output.png
```

Add a border:

```bash
magick input.png -bordercolor white -border 20x20 output.png
```

Add a 3D frame:

```bash
magick input.jpg -mattecolor '#69717d' -frame 12x12+3+3 output.jpg
```

`-trim` can remove meaningful near-background content. Preview or use a conservative fuzz value.

## Advanced trim and edge removal

Trim only selected sides when supported by the installed version:

```bash
magick input.png -define trim:edges=north,east -trim +repage output.png
```

Require a minimum result size or a minimum percentage of background pixels:

```bash
magick scan.jpg -fuzz 8% \
  -define trim:percent-background=95% \
  -define trim:minSize=200x200 \
  -trim +repage output.png
```

These defines are version-sensitive; search `defines-index.md` and test a representative scan. For noisy/scanned borders, normalize or lightly blur a clone to derive a trim box, then crop the untouched original:

```bash
box=$(magick scan.jpg -colorspace Gray -blur 0x2 \
  -fuzz 8% -trim -format '%@' info:)
magick scan.jpg -crop "$box" +repage output.jpg
```

PowerShell:

```powershell
$box = & $magick "scan.jpg" -colorspace Gray -blur "0x2" `
  -fuzz "8%" -trim -format "%@" "info:"
& $magick "scan.jpg" -crop $box +repage "output.jpg"
```

Validate that the calculated box is nonempty and within the original dimensions before using it in an unattended batch.

## Extent, splice, chop, and shave

Canvas extent:

```bash
magick input.png -background none -gravity center -extent 1200x800 output.png
magick input.jpg -background white -gravity northwest -extent 1200x800 output.jpg
```

Crop with extent by using a smaller canvas:

```bash
magick input.jpg -gravity center -extent 800x600 output.jpg
```

Insert rows or columns:

```bash
magick input.png -background white -gravity north -splice 0x80 output.png
magick input.png -background none -gravity west -splice 120x0 output.png
```

Remove an internal strip:

```bash
magick input.png -gravity north -chop 0x40 output.png
```

Remove equal edges:

```bash
magick input.png -shave 10x20 output.png
```

Canvas versus pixels:

- `-extent` changes the viewport and may crop or pad.
- `-splice` inserts new pixels and moves existing content.
- `-chop` deletes a strip and closes the gap.
- `-shave` removes symmetric edges.
- `-border` expands with a color.

## Tile and slice workflows

Fixed tiles:

```bash
magick input.png -crop 256x256 +repage 'tile-%03d.png'
```

Grid by count:

```bash
magick input.png -crop '4x3@' +repage 'tile-%02d.png'
```

Horizontal strips:

```bash
magick input.png -crop '1x8@' +repage 'strip-%02d.png'
```

Sprite sheet from frames:

```bash
magick frame-*.png -background none -gravity center \
  -extent 128x128 -append sprite-column.png
magick frame-*.png -background none -gravity center \
  -extent 128x128 +append sprite-row.png
```

Montage grid:

```bash
magick montage frame-*.png -tile 8x -geometry 128x128+0+0 \
  -background none sprite-sheet.png
```

Avoid reading generated tiles back into the same glob on reruns; use a separate output directory.

Separate regularly spaced sprites by removing gutters before or after cropping. When cell size and gutter are known, explicit crop geometries are safer than trying to infer gaps from color. If inference is needed, build a threshold mask and use connected components; see `advanced-analysis.md`.

## Thumbnail framing patterns

Rounded corners:

```bash
magick input.jpg -thumbnail '400x300^' -gravity center -extent 400x300 \
  thumbnail.png
magick -size 400x300 xc:none -fill white \
  -draw 'roundrectangle 0,0 399,299 30,30' rounded-mask.png
magick thumbnail.png rounded-mask.png -alpha off \
  -compose CopyOpacity -composite rounded.png
```

Inspect the alpha and prefer an SVG mask for strict radii or nonuniform corners:

```bash
magick input.jpg rounded-mask.png -alpha off \
  -compose CopyOpacity -composite rounded.png
```

Polaroid-style card:

```bash
magick input.jpg -thumbnail '360x280^' -gravity center -extent 360x280 \
  -bordercolor white -border 18x18 -background white \
  -gravity south -splice 0x48 -fill '#222' -pointsize 22 \
  -annotate +0+14 'Caption' -background none -rotate -4 polaroid.png
```

Add shadows only after the final frame/rotation so the shadow follows the complete silhouette. Torn paper, page curls, glass badges, and complex edge frames are mask-and-lighting recipes; keep their masks as separate inspectable assets rather than burying all steps in one command.

## Verification

Dimensions:

```bash
magick identify -format '%f %wx%h page=%[page]\n' output.png
```

Expected batch count:

```bash
magick identify -format '%f\n' output/*.png
```

Visual contact sheet:

```bash
magick montage output/*.png -thumbnail 160x160 -label '%f' \
  -tile 5x -geometry +8+24 review.png
```

For a lossy resize, compare structure rather than demanding pixel equality. For deterministic lossless geometry, compare dimensions, alpha, page geometry, and representative pixels.

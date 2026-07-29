# Compositing, masks, and layers

## Contents

- [Core composition model](#core-composition-model)
- [Placement](#placement)
- [Common compose operators](#common-compose-operators)
- [Opacity and dissolve](#opacity-and-dissolve)
- [Alpha masks](#alpha-masks)
- [Background removal and chroma key](#background-removal-and-chroma-key)
- [Known-background and two-background recovery](#known-background-and-two-background-recovery)
- [Read and write masks](#read-and-write-masks)
- [Regions and hole filling](#regions-and-hole-filling)
- [Stacks and clones](#stacks-and-clones)
- [Append, flatten, mosaic, and merge](#append-flatten-mosaic-and-merge)
- [Shadow and watermark patterns](#shadow-and-watermark-patterns)
- [Debugging composites](#debugging-composites)

## Core composition model

With the general `magick` command, the first image is the destination/background and the second is the source/overlay:

```bash
magick background.png overlay.png -compose Over -composite result.png
```

The compatibility subcommand uses a different visual order:

```bash
magick composite -compose Over overlay.png background.png result.png
```

Prefer the general form in complex pipelines because it works naturally with stacks and clones.

Default over:

```bash
magick background.png overlay.png -composite result.png
```

Explicit form is clearer:

```bash
magick background.png overlay.png -compose Over -composite result.png
```

## Placement

Gravity:

```bash
magick background.png overlay.png -gravity center -compose over -composite result.png
magick background.png overlay.png -gravity southeast -geometry +24+24 \
  -compose over -composite result.png
```

Absolute geometry:

```bash
magick background.png overlay.png -geometry +120+80 -compose over -composite result.png
```

Resize only the overlay:

```bash
magick background.png \( overlay.png -resize 25% \) \
  -gravity southeast -geometry +24+24 -compose over -composite result.png
```

PowerShell:

```powershell
& $magick "background.png" "(" "overlay.png" -resize "25%" ")" `
  -gravity southeast -geometry "+24+24" -compose over -composite "result.png"
```

Layer page offsets:

```bash
magick overlay.png -repage +120+80 background.png +swap \
  -compose over -layers merge result.png
```

Use geometry/gravity for ordinary placement; use page offsets when building layer lists or animations.

## Common compose operators

List installed names:

```bash
magick -list compose
```

Porter-Duff:

| Operator | Typical use |
|---|---|
| `Over` | normal overlay |
| `DstOver` | place source behind destination |
| `Src` | replace within canvas |
| `Copy` | copy source |
| `DstIn` | keep destination where source alpha exists |
| `DstOut` | erase destination where source alpha exists |
| `SrcIn` | keep source where destination alpha exists |
| `SrcOut` | keep source outside destination alpha |
| `Atop` | overlay clipped to destination |
| `Xor` | keep non-overlap |
| `Clear` | clear affected destination |

Blend/math:

```bash
magick a.png b.png -compose Multiply -composite multiply.png
magick a.png b.png -compose Screen -composite screen.png
magick a.png b.png -compose Overlay -composite overlay.png
magick a.png b.png -compose SoftLight -composite soft-light.png
magick a.png b.png -compose Difference -composite difference.png
magick a.png b.png -compose Exclusion -composite exclusion.png
magick a.png b.png -compose Plus -composite plus.png
```

Channel/math operators are sensitive to alpha and `-channel` synchronization. For scientific image math, use explicit channels, colorspace, depth, and HDRI expectations.

## Opacity and dissolve

Set overlay opacity:

```bash
magick background.png \( overlay.png -alpha set -channel A -evaluate multiply 0.35 +channel \) \
  -compose over -composite result.png
```

Set alpha directly:

```bash
magick overlay.png -alpha set -channel A -evaluate set 35% +channel translucent.png
```

Dissolve compose arguments:

```bash
magick background.png overlay.png -compose dissolve -define compose:args=35 \
  -composite result.png
```

Exact `compose:args` interpretation differs by compose method; consult `defines-index.md` and the compose docs.

Crossfade two same-sized images:

```bash
magick first.png second.png -define compose:args=35,65 \
  -compose blend -composite crossfade.png
```

## Alpha masks

Mask image to alpha:

```bash
magick color.png mask.png -alpha off -compose CopyOpacity -composite result.png
```

Equivalent using copy alpha where available:

```bash
magick color.png mask.png -alpha off -compose CopyAlpha -composite result.png
```

Extract:

```bash
magick input.png -alpha extract mask.png
```

Invert mask polarity:

```bash
magick mask.png -negate inverted-mask.png
```

Clip content to a mask:

```bash
magick content.png mask.png -alpha off -compose DstIn -composite clipped.png
```

Punch a hole:

```bash
magick content.png mask.png -alpha off -compose DstOut -composite punched.png
```

Color through mask:

```bash
magick -size 1200x800 xc:'#e11d48' mask.png \
  -alpha off -compose CopyOpacity -composite colored-shape.png
```

Three-image legacy composite masks have historically surprising semantics. Prefer building explicit alpha first, then doing a normal two-image composite.

## Background removal and chroma key

Choose the mask-generation method from the evidence available:

| Input situation | Starting method | Main limitation |
|---|---|---|
| Uniform connected background | flood fill from a known outside point | enclosed background-colored holes remain |
| Uniform color everywhere | `-transparent` with a conservative `-fuzz` | matching foreground colors are also removed |
| Green/blue screen | color-distance mask, then clean and feather | spill and shadows need separate treatment |
| Exact clean background image | `ChangeMask` or a difference-derived mask | images must be pixel-aligned |
| Same subject on black and white | two-background recovery | subject and camera must not move |
| Arbitrary photographic background | externally supplied/segmented mask | ImageMagick has no semantic subject detector |

Remove only the background connected to the top-left corner:

```bash
magick input.png -alpha set -channel RGBA -fuzz 6% \
  -fill none -floodfill +0+0 white output.png
```

Add a one-pixel border first when no corner is guaranteed to be background:

```bash
magick input.png -bordercolor white -border 1 -alpha set -channel RGBA \
  -fuzz 6% -fill none -floodfill +0+0 white \
  -shave 1x1 output.png
```

Remove every pixel close to a known flat color:

```bash
magick input.png -alpha on -fuzz 8% -transparent white output.png
```

This is not equivalent to flood fill: it also removes matching colors inside the object.

Simple green-screen starting point:

```bash
magick input.png -alpha on -fuzz 18% -transparent '#00b140' keyed.png
```

For difficult keys, generate a grayscale mask in a perceptual or hue-based colorspace, inspect it, then clean it with morphology and feather only its edge:

```bash
magick input.png -colorspace HSV \
  -color-threshold 'hsv(70,20%,10%)-hsv(170,100%,100%)' \
  -colorspace Gray -negate \
  -morphology Close Disk:1 -blur 0x0.7 key-mask.png

magick input.png key-mask.png -alpha off \
  -compose CopyOpacity -composite keyed.png
```

Hue ranges can wrap, and green spill in foreground RGB remains after alpha extraction. Split a wrapped range into two masks and combine them; correct spill separately. Do not increase `-fuzz` until hair, shadows, and foreground colors disappear.

## Known-background and two-background recovery

When a clean copy of the exact background exists, `ChangeMask` makes pixels within the current fuzz distance transparent:

```bash
magick subject-on-background.png clean-background.png \
  -fuzz 3% -compose ChangeMask -composite cutout.png
```

This produces an on/off decision. A difference-derived mask gives direct control over threshold and feathering:

```bash
magick subject-on-background.png clean-background.png \
  -compose Difference -composite -colorspace Gray \
  -threshold 5% -blur 0x0.7 mask.png

magick subject-on-background.png mask.png -alpha off \
  -compose CopyOpacity -composite cutout.png
```

Save and inspect `mask.png`. Registration errors, compression noise, shadows, and foreground colors close to the background become mask errors. A soft mask preserves antialiased edges, but the RGB under those edges can still contain background color and create a fringe on a new background.

Two aligned renders of the same semitransparent subject on pure black and pure white contain enough information to recover both alpha and foreground color:

```bash
magick on-black.png on-white.png -alpha off \
  \( -clone 0,1 -compose Difference -composite -negate \) \
  \( -clone 0,2 +swap -compose Divide -composite \) \
  -delete 0,1 +swap -compose CopyOpacity -composite recovered.png
```

Assumptions:

- backgrounds are exactly black and white;
- dimensions and subject placement are identical;
- neither source has an active alpha channel;
- the black-background render is image 0.

For other known background pairs, recover alpha from their channel differences, then solve the foreground colors with `-fx` or external numeric code. Test black, white, and mid-gray preview backgrounds to expose color spill.

## Read and write masks

Write mask protects pixels from modification:

```bash
magick input.png -write-mask protect.png -blur 0x8 +write-mask output.png
```

Depending on mask polarity, white/black regions permit or block updates. Test with a small colored image before applying a complex mask.

Read mask controls which source pixels participate:

```bash
magick input.png -read-mask region.png -blur 0x8 +read-mask output.png
```

Pixel mask variants:

```bash
magick input.png -clip-mask mask.png -negate +clip-mask output.png
```

SVG/TIFF clip paths:

```bash
magick input.tif -clip-path '#1' -alpha transparent output.png
```

List profiles and clip paths with `identify -verbose`; names vary by file.

Neighbourhood operators read pixels outside a write-enabled region. Protecting the foreground with a write mask does not stop its colors leaking into a blurred background. For a clean background blur, make excluded pixels transparent before the blur, blur RGBA, then restore the foreground:

```bash
magick input.png background-mask.png -alpha off \
  -compose CopyOpacity -composite background-only.png
magick background-only.png -channel RGBA -blur 0x12 blurred-background.png
magick input.png foreground-mask.png -alpha off \
  -compose CopyOpacity -composite foreground.png
magick blurred-background.png foreground.png \
  -compose Over -composite output.png
```

The two masks must be complementary and correctly aligned. An explicit original/blurred blend is often easier to verify than relying on mask polarity.

## Regions and hole filling

Apply an operator to a rectangular region:

```bash
magick input.png -region 640x360+120+80 -blur 0x8 +region output.png
```

`-region` creates a region sub-image with a page offset. Operators that change geometry or virtual canvas can behave unexpectedly inside it. Prefer an explicit crop/process/composite stack for warps or size changes:

```bash
magick input.png \
  \( +clone -crop 640x360+120+80 +repage -blur 0x8 \) \
  -geometry +120+80 -compose Over -composite output.png
```

A quick fill for a transparent hole spreads nearby colors into it, then places that fill under the original:

```bash
magick image-with-hole.png \
  \( +clone -channel RGBA -blur 0x20 -alpha off \) \
  +swap -compose DstOver -composite filled.png
```

Blur radius must exceed the hole radius. This is suitable for smooth, low-detail backgrounds, not structured texture. For larger or textured removals, create a precise hole mask and use a dedicated inpainting/content-aware tool; keep ImageMagick for mask cleanup, compositing, and verification.

## Stacks and clones

Clone original, transform clone, composite:

```bash
magick input.png \
  \( +clone -blur 0x12 \) \
  -compose screen -composite output.png
```

Build a reflection:

```bash
magick input.png \
  \( +clone -flip -alpha set -channel A \
     -evaluate multiply 0.35 +channel \) \
  -append output.png
```

Blurred background with sharp fitted foreground:

```bash
magick input.jpg \
  \( +clone -resize '1200x630^' -gravity center -extent 1200x630 -blur 0x24 \) \
  \( +clone -resize '1200x630>' \) \
  -delete 0 -gravity center -compose over -composite output.jpg
```

Reuse original by index:

```bash
magick input.png \
  \( -clone 0 -resize 25% \) \
  \( -clone 0 -blur 0x10 \) \
  -delete 0 -compose over -composite output.png
```

Track list indexes carefully after `-delete`, `-insert`, and `-swap`.

## Append, flatten, mosaic, and merge

Horizontal and vertical:

```bash
magick left.png right.png +append row.png
magick top.png bottom.png -append column.png
```

Align different sizes:

```bash
magick left.png right.png -background none -gravity center +append row.png
```

Flatten onto fixed canvas/page:

```bash
magick layer-*.png -background white -flatten result.jpg
```

Mosaic expands to positive layer extents:

```bash
magick layer-*.miff -background none -mosaic result.png
```

Layer merge can expand and handle negative offsets:

```bash
magick layer-*.miff -background none -layers merge +repage result.png
```

Coalesce an animation/layer list:

```bash
magick animation.gif -coalesce coalesced.miff
```

Sequence composite:

```bash
magick background-frames.gif overlay-frames.gif \
  -compose over -layers composite result.gif
```

Verify list lengths and timing when compositing sequences.

## Shadow and watermark patterns

Shadow behind transparent object:

```bash
magick object.png \
  \( +clone -background black -shadow 60x8+12+12 \) \
  +swap -background none -layers merge +repage result.png
```

Text watermark:

```bash
magick input.jpg -gravity southeast -fill 'rgba(255,255,255,0.45)' \
  -stroke 'rgba(0,0,0,0.25)' -strokewidth 1 -pointsize 28 \
  -annotate +24+20 '© Example' output.jpg
```

Image watermark:

```bash
magick input.jpg \( logo.png -resize '180x180>' \
  -alpha set -channel A -evaluate multiply 0.55 +channel \) \
  -gravity southeast -geometry +24+24 -compose over -composite output.jpg
```

Tiled watermark:

```bash
magick input.jpg \( -size 300x180 -background none -fill '#ffffff40' \
  -gravity center -pointsize 30 label:'SAMPLE' -rotate -25 \) \
  -compose over -tile -composite output.jpg
```

Test tile syntax on the installed version; a full-size watermark canvas is often easier to reason about:

```bash
magick -size 1200x800 tile:watermark.png watermark-layer.png
```

## Debugging composites

1. Save/inspect each stack as a temporary PNG.
2. Print list state with `-identify` or `-write info:`.
3. Verify image order.
4. Verify overlay dimensions and page offsets.
5. Extract alpha channels and inspect them.
6. Reset `-channel` and `-compose` settings.
7. Use opaque test colors before debugging subtle transparency.

```bash
magick background.png overlay.png \
  -write mpr:debug +delete mpr:debug -verbose info:

magick overlay.png -alpha extract overlay-alpha.png
magick identify -format '%f %wx%h page=%[page] channels=%[channels]\n' \
  background.png overlay.png
```

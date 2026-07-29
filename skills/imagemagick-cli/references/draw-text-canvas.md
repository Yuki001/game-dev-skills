# Canvas creation, drawing, and text

## Contents

- [Solid and generated canvases](#solid-and-generated-canvases)
- [Gradients and patterns](#gradients-and-patterns)
- [Procedural and seamless canvases](#procedural-and-seamless-canvases)
- [Fonts](#fonts)
- [Label, caption, and annotate](#label-caption-and-annotate)
- [Pango, mixed styles, and form filling](#pango-mixed-styles-and-form-filling)
- [Gravity and text metrics](#gravity-and-text-metrics)
- [Draw primitives](#draw-primitives)
- [Reusable symbols and arrows](#reusable-symbols-and-arrows)
- [Paths, MVG, and SVG](#paths-mvg-and-svg)
- [Watermarks, outlines, and shadows](#watermarks-outlines-and-shadows)
- [Antialiasing and color](#antialiasing-and-color)

## Solid and generated canvases

```bash
magick -size 800x600 canvas:'#0f172a' canvas.png
magick -size 800x600 xc:none transparent.png
magick -size 800x600 xc:'rgba(15,23,42,0.8)' translucent.png
```

Create a same-sized canvas:

```bash
magick input.png -fill white -colorize 100 blank.png
magick input.png -alpha extract -negate mask.png
```

Pick a pixel as a color:

```bash
magick input.png -crop 1x1+40+30 +repage -scale 800x600 color-canvas.png
```

Noise/plasma:

```bash
magick -size 800x600 xc:gray +noise Random noise.png
magick -size 800x600 plasma:'#102a43-#d64545' plasma.png
```

Built-ins:

```bash
magick logo: logo.png
magick rose: rose.png
magick wizard: wizard.png
```

## Gradients and patterns

Linear:

```bash
magick -size 800x600 gradient:'#0f172a-#38bdf8' gradient.png
magick -size 800x600 -define gradient:angle=45 \
  gradient:'#0f172a-#38bdf8' diagonal.png
```

Radial:

```bash
magick -size 800x600 radial-gradient:'#ffffff-#1e293b' radial.png
```

Multi-stop with sparse colors:

```bash
magick -size 800x1 xc: \
  -sparse-color Barycentric '0,0 #ef4444 400,0 #22c55e 799,0 #3b82f6' \
  -resize 800x600 gradient.png
```

Pattern:

```bash
magick -size 800x600 pattern:checkerboard checker.png
magick -size 800x600 tile:texture.png tiled.png
```

List patterns:

```bash
magick -list format | grep -i pattern
```

Built-in pattern names vary less than fonts but should still be queried or tested when uncertain.

## Procedural and seamless canvases

Repeat a tile with an offset:

```bash
magick -size 1200x800 -tile-offset +40+20 tile:texture.png tiled.png
```

Mirror a source into a seam-reduced 2×2 tile:

```bash
magick texture.png \( +clone -flop \) +append \
  \( +clone -flip \) -append mirrored-tile.png
magick -size 1200x800 tile:mirrored-tile.png background.png
```

This hides value discontinuities at the outside edges but creates mirror symmetry. Random noise is naturally tileable when generated at the final tile size:

```bash
magick -size 256x256 xc:gray +noise Random \
  -blur 0x3 -auto-level noise-tile.png
```

Set `-seed` for reproducibility:

```bash
magick -seed 12345 -size 256x256 xc:gray +noise Random noise.png
```

Plasma is not guaranteed seamless. Generate it larger, use virtual-pixel tiling/mirroring during transforms, then shave unreliable edges or use an explicit seam-making algorithm. Verify every tile by rendering at least a 3×3 repetition:

```bash
magick -size 768x768 tile:tile.png tile-check.png
```

For hexagonal/diagonal tiling, first construct a rectangular repeat cell with clones and calculated offsets, then use `tile:`. Keep the cell on a transparent canvas and inspect page offsets before flattening.

## Fonts

List known fonts:

```bash
magick -list font
magick -list font | grep -E 'Font:|family:|glyphs:'
```

Use a configured font name:

```bash
magick -size 900x200 -background none -fill white \
  -font DejaVu-Sans -pointsize 72 -gravity center \
  label:'ImageMagick' label.png
```

Use an exact font file:

```bash
magick -size 900x200 -background none -fill white \
  -font '/path/to/Font.ttf' -pointsize 72 -gravity center \
  label:'ImageMagick' label.png
```

Font discovery depends on Fontconfig or Windows configuration. If a requested font is missing, locate a licensed font file or ask for one; do not silently substitute when layout is strict.

Complex scripts, emoji, and advanced shaping may require Pango:

```bash
magick -background none pango:'مرحبا بالعالم' output.png
```

Confirm the Pango delegate and fonts.

## Label, caption, and annotate

`label:` sizes to a line of text unless `-size` constrains it:

```bash
magick -background none -fill black -pointsize 42 \
  label:'Single line' label.png
```

`caption:` wraps within the requested width/height:

```bash
magick -size 720x -background white -fill '#111827' -pointsize 36 \
  caption:'A longer paragraph that wraps automatically.' caption.png
```

Append label below:

```bash
magick photo.jpg -background white -fill black -pointsize 30 \
  label:'Figure 1 — Sample' -gravity center -append labeled.jpg
```

Annotate on an image:

```bash
magick photo.jpg -gravity south -fill white -stroke black -strokewidth 2 \
  -pointsize 36 -annotate +0+24 'Sample caption' output.jpg
```

Rotate annotation:

```bash
magick photo.jpg -gravity center -fill '#ffffff80' -pointsize 64 \
  -annotate -25 'DRAFT' output.jpg
```

Read text from a file:

```bash
magick -size 900x -background white -fill black -pointsize 28 \
  caption:@caption.txt output.png
```

Security policy may disable indirect `@file` reads. For untrusted text, pass an argument safely through the shell and avoid interpreting it as MVG/format escapes.

Percent escapes can be expanded in labels:

```bash
magick input.jpg -set label '%f — %wx%h' -background white \
  -gravity center -append output.jpg
```

## Pango, mixed styles, and form filling

Use `pango:` when text needs shaping, bidirectional layout, wrapping, or mixed styles:

```bash
magick -size 800x -background none -fill black \
  -define pango:markup=true \
  pango:'<span font="Noto Sans 32">Normal <b>bold</b> <i>italic</i></span>' \
  text.png
```

Useful defines include `pango:align`, `pango:wrap`, `pango:ellipsize`, `pango:justify`, `pango:auto-dir`, `pango:language`, and `pango:single-paragraph`. Search `defines-index.md` for the installed grammar. Pango markup must be escaped as markup in addition to shell quoting.

For mixed fonts without Pango, render fragments independently and append them on a common baseline. Font ascent/descent differences make this more work than ordinary `+append`; measure each fragment and add transparent padding before assembly.

Fill a raster form with fixed-position annotations:

```bash
magick form.png -font DejaVu-Sans -pointsize 24 -fill black \
  -annotate +180+220 'Alice Example' \
  -annotate +180+280 '2026-07-29' \
  filled-form.png
```

For multiline fields, render a constrained `caption:` image and composite it into the field:

```bash
magick -size 520x140 -background none -fill black \
  -font DejaVu-Sans -pointsize 22 \
  caption:'Wrapped field contents' field.png
magick form.png field.png -geometry +180+340 \
  -compose Over -composite filled-form.png
```

Do not use a raster workflow when the output must remain an editable PDF form or selectable text.

## Gravity and text metrics

Common values:

```text
northwest north northeast
west      center east
southwest south southeast
```

Offset is interpreted from the gravity anchor:

```bash
magick input.png -gravity northeast -annotate +20+30 'Top right' output.png
```

Measure before rendering:

```bash
magick -font DejaVu-Sans -pointsize 42 -debug annotate \
  label:'Measure me' null:
```

Useful percent escapes:

```bash
magick -font DejaVu-Sans -pointsize 42 label:'Measure me' \
  -format '%w x %h\n' info:
```

Create a fixed box with padding:

```bash
magick -size 800x200 -background '#111827' -fill white \
  -font DejaVu-Sans -pointsize 52 -gravity center \
  caption:'Centered title' title.png
```

For exact typography, test the actual font/rendering stack and inspect bounds; different delegates can produce different metrics.

## Draw primitives

Base pattern:

```bash
magick -size 600x400 xc:white -fill '#38bdf8' -stroke '#0f172a' \
  -strokewidth 4 -draw 'rectangle 60,60 540,340' drawing.png
```

Primitives:

```bash
magick -size 600x400 xc:white -fill none -stroke black -strokewidth 4 \
  -draw 'line 40,40 560,360' line.png

magick -size 600x400 xc:white -fill '#f97316' -stroke black \
  -draw 'roundrectangle 80,60 520,340 30,30' rounded.png

magick -size 600x400 xc:white -fill '#22c55e' -stroke black \
  -draw 'circle 300,200 300,80' circle.png

magick -size 600x400 xc:white -fill '#8b5cf6' -stroke black \
  -draw 'ellipse 300,200 220,120 0,360' ellipse.png

magick -size 600x400 xc:white -fill '#eab308' -stroke black \
  -draw 'polygon 300,30 570,360 30,360' polygon.png

magick -size 600x400 xc:white -fill none -stroke '#ef4444' -strokewidth 5 \
  -draw 'bezier 30,330 180,20 420,380 570,70' bezier.png
```

Draw text:

```bash
magick -size 800x300 xc:none -fill white -stroke black -strokewidth 2 \
  -font DejaVu-Sans -pointsize 72 -gravity center \
  -draw "text 0,0 'Hello'" text.png
```

Draw an image:

```bash
magick -size 800x600 xc:white -draw "image over 100,80 320,240 'photo.jpg'" result.png
```

Prefer normal compositing for complex image placement; `-draw image` has quoting and sizing semantics that are less obvious.

Flood fill:

```bash
magick input.png -bordercolor black -border 1 \
  -fuzz 5% -fill none -draw 'matte 0,0 floodfill' \
  -shave 1x1 output.png
```

Review polarity and alpha behavior on the installed version.

## Reusable symbols and arrows

Build a symbol on a transparent canvas around a known origin, then rotate/scale the symbol rather than recomputing every point:

```bash
magick -size 240x80 xc:none -fill '#2563eb' -stroke '#1e3a8a' \
  -strokewidth 3 \
  -draw 'polygon 0,30 170,30 170,5 235,40 170,75 170,50 0,50' \
  arrow.png
magick arrow.png -background none -rotate 28 arrow-28.png
```

Composite between measured endpoints:

1. calculate `dx`, `dy`, length, and `atan2(dy,dx)` outside ImageMagick or with `-fx`;
2. resize the arrow to the calculated length;
3. rotate around its intended anchor;
4. composite at the start point.

For dimension lines, draw the line, end caps/arrowheads, and label as separate layers. This keeps stroke width and text readable when the line is rotated.

Symbol fonts are compact but font-dependent. Prefer explicit vector paths or SVG assets when the symbol must render identically across machines.

## Paths, MVG, and SVG

SVG path:

```bash
magick -size 600x400 xc:white -fill '#38bdf8' -stroke '#0f172a' \
  -draw "path 'M 60,300 C 180,20 420,380 540,100 Z'" path.png
```

MVG file:

```text
push graphic-context
viewbox 0 0 600 400
fill '#38bdf8'
stroke '#0f172a'
stroke-width 4
roundrectangle 60,60 540,340 30,30
pop graphic-context
```

Render:

```bash
magick -size 600x400 mvg:drawing.mvg drawing.png
```

Inline:

```bash
magick -size 600x400 xc:white -draw @drawing.mvg output.png
```

Policy can restrict indirect file reads. Treat MVG and SVG as active parsing formats; do not render untrusted content without a restrictive policy.

SVG rasterization:

```bash
magick -density 192 vector.svg -background none vector.png
```

## Watermarks, outlines, and shadows

Outlined text:

```bash
magick -size 900x240 xc:none -gravity center -font DejaVu-Sans \
  -pointsize 80 -fill white -stroke black -strokewidth 6 \
  -annotate 0 'Outlined' output.png
```

Soft shadow:

```bash
magick -background none -fill white -font DejaVu-Sans -pointsize 72 \
  label:'Shadow' \
  \( +clone -background black -shadow 70x6+8+8 \) \
  +swap -background none -layers merge +repage output.png
```

Text watermark:

```bash
magick input.jpg -gravity southeast -font DejaVu-Sans -pointsize 28 \
  -fill '#ffffff99' -stroke '#00000066' -strokewidth 1 \
  -annotate +24+20 '© Example' output.jpg
```

Emboss/bump watermark:

```bash
magick input.jpg watermark-mask.png \
  -compose SoftLight -composite output.jpg
```

For photographic watermarks, build and inspect the grayscale bump/alpha mask separately.

## Antialiasing and color

Drawing is antialiased by default:

```bash
magick -size 200x200 xc:white -antialias -draw 'circle 100,100 100,20' aa.png
magick -size 200x200 xc:white +antialias -draw 'circle 100,100 100,20' hard.png
```

For physically meaningful blending/drawing on high-quality assets, consider linear-light composition. For UI assets, matching the target renderer may be more important than mathematically linear blending.

Inspect output alpha:

```bash
magick output.png -alpha extract alpha.png
magick identify -format '%[channels] %[opaque]\n' output.png
```

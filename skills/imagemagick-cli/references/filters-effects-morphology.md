# Filters, effects, convolution, and morphology

## Contents

- [Blur and sharpen](#blur-and-sharpen)
- [Noise and cleanup](#noise-and-cleanup)
- [Edge detection](#edge-detection)
- [Hough lines and local thresholding](#hough-lines-and-local-thresholding)
- [Convolution](#convolution)
- [Morphology model](#morphology-model)
- [Morphology recipes](#morphology-recipes)
- [Hit-and-miss, thinning, and constrained morphology](#hit-and-miss-thinning-and-constrained-morphology)
- [Deskew and document cleanup](#deskew-and-document-cleanup)
- [Local contrast and photographic effects](#local-contrast-and-photographic-effects)
- [Shade and antialiasing workflows](#shade-and-antialiasing-workflows)
- [Shadows and shaped blur](#shadows-and-shaped-blur)
- [Quality and debugging](#quality-and-debugging)

## Blur and sharpen

Gaussian-style blur:

```bash
magick input.png -blur 0x4 output.png
magick input.png -gaussian-blur 0x4 output.png
```

The geometry is `radius x sigma`. Sigma controls blur strength; radius `0` lets ImageMagick choose a meaningful support size.

Blur RGB but retain alpha edges:

```bash
magick input.png -channel RGB -blur 0x4 +channel output.png
```

Blur RGBA together:

```bash
magick input.png -channel RGBA -blur 0x4 +channel output.png
```

These produce different colors near transparency. Premultiplication/hidden RGB can create halos; inspect on contrasting backgrounds.

Adaptive blur:

```bash
magick input.png -adaptive-blur 0x4 output.png
```

Motion/radial blur:

```bash
magick input.png -motion-blur 0x12+30 output.png
magick input.png -rotational-blur 12 output.png
```

Sharpen:

```bash
magick input.png -sharpen 0x1 output.png
magick input.png -adaptive-sharpen 0x1 output.png
magick input.png -unsharp 0x1+1+0.05 output.png
```

Unsharp geometry is commonly `radius x sigma + amount + threshold`. Tune at final display size.

## Noise and cleanup

Add noise:

```bash
magick input.png -attenuate 0.15 +noise Gaussian output.png
magick input.png -attenuate 0.10 +noise Poisson output.png
magick input.png -attenuate 0.20 +noise Random output.png
```

Reduce noise:

```bash
magick input.png -despeckle output.png
magick input.png -median 2 output.png
magick input.png -statistic Median 5x5 output.png
magick input.png -bilateral-blur 9x9+6+0.1 output.png
magick input.png -kuwahara 5 output.png
```

Salt-and-pepper cleanup:

```bash
magick input.png -statistic Median 3x3 output.png
```

Local statistics:

```bash
magick input.png -statistic Mean 7x7 local-mean.png
magick input.png -statistic StandardDeviation 7x7 local-contrast.png
```

Always compare detail retention at 100%; denoising can erase text and thin lines.

## Edge detection

Simple edge:

```bash
magick input.png -colorspace Gray -edge 1 edges.png
```

Canny:

```bash
magick input.png -colorspace Gray -canny 0x1+10%+30% edges.png
```

Morphological edge:

```bash
magick input.png -colorspace Gray -morphology EdgeIn Diamond edges-in.png
magick input.png -colorspace Gray -morphology EdgeOut Diamond edges-out.png
magick input.png -colorspace Gray -morphology Edge Diamond edges.png
```

Gradient magnitude:

```bash
magick input.png -colorspace Gray -morphology Convolve Sobel:0 \
  -auto-level edges.png
```

Direction-specific kernels:

```bash
magick input.png -colorspace Gray -morphology Convolve 'Sobel:90' edge-x.png
magick input.png -colorspace Gray -morphology Convolve 'Sobel:0' edge-y.png
```

Confirm kernel syntax with `magick -define morphology:showKernel=1 ...` and installed version.

## Hough lines and local thresholding

Hough line detection expects clean white lines on black. Generate a Canny edge map first:

```bash
magick input.png -colorspace Gray -canny 0x1+10%+30% edges.png
magick edges.png -background black -stroke red \
  -hough-lines 5x5+20 lines.mvg
```

The geometry is `neighbourhood-width x neighbourhood-height + peak-threshold`. MVG output preserves line coordinates and strength comments for downstream parsing. Render it over the source:

```bash
magick input.png lines.mvg -compose Over -composite lines-preview.png
```

Inspect the accumulator when duplicate or missing lines are hard to tune:

```bash
magick edges.png -define hough-lines:accumulator=true \
  -hough-lines 5x5+20 -delete 0 -contrast-stretch 0.1% accumulator.png
```

Local adaptive thresholding handles uneven illumination:

```bash
magick scan.png -colorspace Gray -lat 25x25+8% threshold.png
```

Smaller windows follow local illumination but amplify noise; larger windows are slower and behave more like a global threshold. Positive offset is typically less sensitive to small dark variations. Denoise lightly before `-lat` when paper texture becomes foreground.

## Convolution

Direct:

```bash
magick input.png -convolve '0,-1,0,-1,5,-1,0,-1,0' sharpen.png
```

Morphology form:

```bash
magick input.png -morphology Convolve \
  '3x3: 0,-1,0 -1,5,-1 0,-1,0' sharpen.png
```

Box blur:

```bash
magick input.png -morphology Convolve 'Square:2' output.png
```

Custom edge:

```bash
magick input.png -colorspace Gray -bias 50% \
  -convolve '-1,-1,-1,-1,8,-1,-1,-1,-1' edge.png
```

Zero-summing kernels need a bias or HDRI-aware workflow because negative values otherwise clamp.

Inspect generated kernel:

```bash
magick xc: -define morphology:showKernel=1 \
  -morphology Convolve 'Gaussian:0x2' null:
```

Normalize or scale:

```bash
magick input.png -define convolve:scale='1/9' \
  -convolve '1,1,1,1,1,1,1,1,1' output.png
```

Search `defines-index.md` for `convolve:` and `morphology:`.

## Morphology model

General form:

```text
-morphology method[:iterations] kernel[:arguments]
```

List methods/kernels:

```bash
magick -list morphology
```

Show kernel:

```bash
magick xc: -define morphology:showKernel=1 \
  -morphology Dilate Diamond:3 null:
```

Binary morphology normally treats white foreground on black background. Invert when the source uses black ink:

```bash
magick scan.png -colorspace Gray -threshold 50% -negate \
  -morphology Open Diamond -negate cleaned.png
```

Core methods:

| Method | Effect on white foreground |
|---|---|
| `Erode` | shrinks shapes |
| `Dilate` | expands shapes |
| `Open` | removes small foreground protrusions/components |
| `Close` | fills small gaps/holes and connects near shapes |
| `Smooth` | open then close style smoothing |
| `EdgeIn` | inner edge |
| `EdgeOut` | outer edge |
| `TopHat` | extracts small bright features |
| `BottomHat` | extracts small dark features |
| `HitAndMiss` | pattern matching |
| `Thinning` | skeleton-style reduction |
| `Thicken` | controlled growth |
| `Distance` | distance transform |
| `Voronoi` | nearest-seed partition |

## Morphology recipes

Thicken thin white lines:

```bash
magick lines.png -morphology Dilate Diamond:1 output.png
```

Remove isolated white specks:

```bash
magick mask.png -morphology Open Disk:1 output.png
```

Fill small gaps:

```bash
magick mask.png -morphology Close Disk:2 output.png
```

Outline:

```bash
magick mask.png -morphology Edge Diamond outline.png
```

Skeleton:

```bash
magick mask.png -morphology Thinning:-1 Skeleton skeleton.png
```

Distance transform:

```bash
magick mask.png -morphology Distance Euclidean:4 distance.png
```

Remove horizontal lines in documents:

```bash
magick scan.png -colorspace Gray -threshold 50% -negate \
  -morphology Open 'Rectangle:40x1' horizontal-lines.png
```

Extract vertical lines:

```bash
magick scan.png -colorspace Gray -threshold 50% -negate \
  -morphology Open 'Rectangle:1x40' vertical-lines.png
```

Combine to detect a grid:

```bash
magick horizontal-lines.png vertical-lines.png -compose Lighten -composite grid.png
```

Kernel naming and polarity are common failure points; inspect intermediate masks.

## Hit-and-miss, thinning, and constrained morphology

Hit-and-miss detects exact local binary patterns. Define foreground hits as `1`, background misses as `0`, and ignored cells as `-` in a user kernel:

```bash
magick mask.png -morphology HitAndMiss \
  '3x3: 0,0,0  -,1,-  1,1,1' matches.png
```

Rotate a kernel or use a built-in kernel list to detect multiple orientations. Always test mask polarity and render the kernel:

```bash
magick xc: -define morphology:showKernel=1 \
  -morphology HitAndMiss 'LineEnds' null:
```

Useful pattern kernels include `Peaks`, `Edges`, `Corners`, `Diagonals`, `LineEnds`, `LineJunctions`, `Ridges`, and `Skeleton` variants; availability and exact names depend on the build.

Thin to a one-pixel skeleton:

```bash
magick mask.png -morphology Thinning:-1 Skeleton skeleton.png
```

Prune short spurs by applying line-end kernels for a controlled number of iterations; unlimited pruning can erase genuine branches. Compare connected-component count and endpoints before/after.

Constrained dilation grows seeds only inside an allowed mask. One explicit form is to dilate, intersect with the constraint, and iterate:

```bash
magick seeds.png -morphology Dilate Diamond:1 \
  constraint.png -compose Darken -composite grown-1.png
```

Repeat until stable or for a fixed radius. In a white-foreground convention, `Darken` acts as intersection. Reverse the compose choice when polarity is reversed.

## Deskew and document cleanup

Deskew:

```bash
magick scan.png -background white -deskew 40% deskewed.png
```

Trim afterward:

```bash
magick scan.png -background white -deskew 40% -fuzz 5% -trim +repage output.png
```

Adaptive binarization:

```bash
magick scan.png -colorspace Gray -lat 25x25+10% output.png
```

Normalize and threshold:

```bash
magick scan.png -colorspace Gray -contrast-stretch 1%x1% \
  -threshold 60% output.png
```

Morphological background normalization:

```bash
magick scan.png -colorspace Gray \
  \( +clone -morphology Close Disk:20 \) \
  -compose DivideSrc -composite -auto-level normalized.png
```

Document cleanup is content-sensitive. Preserve a lossless intermediate and inspect faint strokes.

## Local contrast and photographic effects

CLAHE:

```bash
magick photo.jpg -clahe 25x25%+128+3 output.jpg
magick photo.jpg -virtual-pixel mirror -clahe 300x300+128+3! output.jpg
```

Vignette:

```bash
magick photo.jpg -background black -vignette 0x20+10%+10% output.jpg
```

Charcoal/oil:

```bash
magick photo.jpg -charcoal 1 output.jpg
magick photo.jpg -paint 4 output.jpg
```

Emboss:

```bash
magick input.png -colorspace Gray -emboss 0x2 -auto-level output.png
```

Sketch:

```bash
magick photo.jpg -colorspace Gray -sketch 0x20+120 output.png
```

Poster/solarize:

```bash
magick input.png -posterize 6 output.png
magick input.png -solarize 50% output.png
```

Spread:

```bash
magick input.png -virtual-pixel mirror -spread 8 output.png
```

Raise:

```bash
magick button.png -raise 8 raised.png
magick button.png +raise 8 sunken.png
```

## Shade and antialiasing workflows

`-shade` converts a height map into directional lighting:

```bash
magick height-map.png -shade 120x35 -auto-level shaded.png
```

The arguments are light azimuth and elevation. For a colored 3-D object, keep the height/lighting image separate and combine it with color using `Overlay`, `HardLight`, or `Multiply`:

```bash
magick height-map.png -shade 120x35 -auto-level lighting.png
magick color-layer.png lighting.png -compose Overlay -composite shaded-color.png
```

Blur the height map, not only the finished shading, to round hard edges. Mask the final lighting back to the original object alpha.

Drawing is antialiased by default; `+antialias` deliberately produces hard bitmap edges. Flood fill on an antialiased outline can leak through partially covered edge pixels. Safer patterns are:

- draw/fill at 2–4× resolution and downsample;
- close the boundary with morphology before filling;
- use `-fuzz` conservatively and add a temporary border;
- build the shape as an alpha mask and composite it instead of flood-filling the rendered edge.

When downsampling line art, choose a filter that does not ring into unwanted halos and inspect on both light and dark backgrounds.

## Shadows and shaped blur

Drop shadow:

```bash
magick object.png \
  \( +clone -background black -shadow 65x8+12+12 \) \
  +swap -background none -layers merge +repage output.png
```

Glow:

```bash
magick object.png \
  \( +clone -channel A -separate +channel -blur 0x12 \
     -fill '#38bdf8' -colorize 100 \) \
  -compose DstOver -composite output.png
```

Blur only masked area:

```bash
magick input.jpg blurred-mask.png -write-mask blurred-mask.png \
  -blur 0x12 +write-mask output.jpg
```

If mask semantics are uncertain, create `original`, `fully blurred`, then blend them explicitly:

```bash
magick input.jpg \( +clone -blur 0x12 \) mask.png \
  -compose over -composite output.jpg
```

For explicit blend, build alpha on the blurred clone first.

## Quality and debugging

```bash
magick identify -format '%wx%h %[colorspace] %[channels]\n' output.png
magick input.png output.png -compose difference -composite -auto-level diff.png
```

Kernel debug:

```bash
magick xc: -define morphology:showKernel=1 \
  -morphology Dilate 'Disk:5' null:
```

Channel debug:

```bash
magick output.png -separate 'channel-%d.png'
```

Use a checkerboard under transparent results to detect blur/composite halos:

```bash
magick -size 800x600 pattern:checkerboard output.png \
  -compose over -composite preview.png
```

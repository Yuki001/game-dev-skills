# Color, tone, channels, alpha, and quantization

## Contents

- [Color specification](#color-specification)
- [Colorspace conversion vs tagging](#colorspace-conversion-vs-tagging)
- [Grayscale](#grayscale)
- [Channels and alpha](#channels-and-alpha)
- [Level, gamma, contrast, and histograms](#level-gamma-contrast-and-histograms)
- [Tint, duotone, and lookup grading](#tint-duotone-and-lookup-grading)
- [Color replacement and thresholding](#color-replacement-and-thresholding)
- [CLUTs and color matrices](#cluts-and-color-matrices)
- [Color reduction](#color-reduction)
- [Dithering](#dithering)
- [Palette and transparency edge cases](#palette-and-transparency-edge-cases)
- [Color-management verification](#color-management-verification)

## Color specification

Equivalent green examples:

```text
lime
#0f0
#00ff00
rgb(0,255,0)
rgb(0%,100%,0%)
srgb(0,1,0)
```

Alpha-bearing forms:

```text
#ff000080
rgba(255,0,0,0.5)
srgba(1,0,0,0.5)
none
transparent
```

Use quotes around parentheses, `#`, spaces, or percent signs:

```bash
magick -size 400x200 xc:'rgba(20,40,80,0.6)' output.png
```

Query available names:

```bash
magick -list color
magick xc:rebeccapurple -format '%[pixel:p{0,0}]\n' info:
```

Do not rely on ambiguous gray names across standards; use numeric values for reproducibility.

## Colorspace conversion vs tagging

Convert pixel values:

```bash
magick input.jpg -colorspace RGB linear.miff
magick linear.miff -colorspace sRGB output.jpg
magick input.tif -colorspace Lab lab.tif
```

Tag/reinterpret without changing pixel values:

```bash
magick input.png -set colorspace sRGB tagged.png
```

`-set colorspace` is for correcting a missing/wrong interpretation or controlling later operations. It is not a normal conversion.

ICC transform:

```bash
magick input.tif -profile scanner.icc -profile sRGB.icc output.jpg
```

If the image already has an embedded source profile:

```bash
magick input.tif -profile sRGB.icc output.jpg
```

Confirm profiles before deciding which form is correct. Applying the wrong source profile changes color meaning.

Linear-light processing:

```bash
magick input.jpg -colorspace RGB -resize 50% -colorspace sRGB output.jpg
```

## Grayscale

Convert using colorspace:

```bash
magick input.jpg -colorspace Gray gray.jpg
```

Choose intensity formula:

```bash
magick input.jpg -grayscale Rec709Luminance gray-linear.png
magick input.jpg -grayscale Rec709Luma gray-luma.png
magick input.jpg -grayscale Rec601Luma gray-601.png
```

Desaturate perceptually:

```bash
magick input.jpg -modulate 100,0,100 gray.png
```

Extract a channel:

```bash
magick input.png -channel R -separate red.png
magick input.png -separate 'channel-%d.png'
```

Combine grayscale channel images:

```bash
magick red.png green.png blue.png -combine rgb.png
magick c.png m.png y.png k.png -set colorspace CMYK -combine cmyk.tif
```

Choose a method based on whether the result should represent encoded luma, linear luminance, a specific channel, or a simple artistic desaturation.

## Channels and alpha

Inspect:

```bash
magick identify -format '%[channels] opaque=%[opaque]\n' input.png
```

Activate alpha:

```bash
magick input.png -alpha set output.png
```

Extract alpha:

```bash
magick input.png -alpha extract alpha.png
```

Apply a grayscale mask as alpha:

```bash
magick color.png mask.png -alpha off -compose CopyOpacity -composite output.png
```

Remove transparency against a color:

```bash
magick input.png -background white -alpha remove -alpha off output.jpg
```

Turn alpha off without flattening:

```bash
magick input.png -alpha off output.png
```

This hides/ignores transparency and may retain RGB values under transparent pixels. Use `-alpha remove` to blend onto the background.

Operate on selected channels:

```bash
magick input.png -channel RGB -negate +channel output.png
magick input.png -channel A -threshold 50% +channel output.png
magick input.png -channel R -evaluate multiply 1.1 +channel output.png
```

Reset with `+channel`; a forgotten channel restriction silently changes later operators.

Copy channels:

```bash
magick base.png source.png -compose CopyRed -composite output.png
magick base.png alpha.png -compose CopyAlpha -composite output.png
```

Check installed compose names; aliases such as `CopyOpacity`/`CopyAlpha` may vary by version.

## Level, gamma, contrast, and histograms

Negate:

```bash
magick input.png -negate output.png
magick input.png -channel RGB -negate +channel output.png
```

Level black/white points:

```bash
magick input.jpg -level 5%,95% output.jpg
magick input.jpg -level 5%,95%,1.1 output.jpg
```

Gamma:

```bash
magick input.jpg -gamma 1.2 output.jpg
```

Brightness/contrast:

```bash
magick input.jpg -brightness-contrast 8x12 output.jpg
```

Sigmoidal contrast:

```bash
magick input.jpg -sigmoidal-contrast 6x50% output.jpg
magick input.jpg +sigmoidal-contrast 6x50% softened.jpg
```

Normalize/stretch:

```bash
magick input.jpg -auto-level output.jpg
magick input.jpg -normalize output.jpg
magick input.jpg -contrast-stretch 0.5%x0.5% output.jpg
magick input.jpg -linear-stretch 0.5%x0.5% output.jpg
```

Histogram equalization:

```bash
magick input.jpg -equalize output.jpg
magick input.jpg -clahe 25x25%+128+3 output.jpg
```

Local CLAHE can reveal noise and halos; tune tile size, bins, and clip limit on representative regions.

Modulate:

```bash
magick input.jpg -modulate 105,115,100 output.jpg
```

Arguments are brightness, saturation, hue percentages.

Histogram text:

```bash
magick input.png -depth 8 -format %c histogram:info:-
magick input.png -colorspace Gray histogram:histogram.png
```

Statistics:

```bash
magick input.png -format '%[mean] %[standard-deviation] %[min] %[max]\n' info:
magick input.png -channel RGB -separate -format '%[mean]\n' info:
```

## Tint, duotone, and lookup grading

Uniform tint:

```bash
magick input.jpg -fill '#2563eb' -colorize 18% tinted.jpg
```

Midtone-oriented tint:

```bash
magick input.jpg -colorspace Gray \
  +level-colors '#0f172a','#f8fafc' duotone.png
```

Three-color gradient map:

```bash
magick -size 1024x1 xc: -sparse-color Shepards \
  '0,0 #0f172a 512,0 #dc2626 1023,0 #f8fafc' grade-map.png
magick input.jpg -colorspace Gray grade-map.png -clut graded.png
```

For exact multistop grading, build the lookup image with explicit stop positions using `-sparse-color` or a saved gradient asset. Apply CLUTs only after deciding which intensity/colorspace indexes the table.

Hald CLUTs encode a 3-D RGB transform:

```bash
magick hald:8 identity.png
# Edit identity.png only with color operations that preserve its geometry.
magick input.jpg edited-hald.png -hald-clut graded.jpg
```

Cropping, resizing, lossy compression, or color-managing the Hald image changes the transform. Hald CLUTs do not model spatial effects, sharpening, or grain.

## Color replacement and thresholding

Exact replacement:

```bash
magick input.png -fill red -opaque blue output.png
```

Fuzzy replacement:

```bash
magick input.png -fuzz 8% -fill red -opaque blue output.png
```

Make a color transparent:

```bash
magick input.png -alpha on -fuzz 8% -transparent white output.png
```

Replace transparent pixels:

```bash
magick input.png -background white -alpha remove -alpha off output.png
```

Black/white threshold:

```bash
magick input.png -colorspace Gray -threshold 55% bilevel.png
magick input.png -colorspace Gray -lat 25x25+10% bilevel.png
magick input.png -colorspace Gray -auto-threshold OTSU bilevel.png
```

Color range:

```bash
magick input.jpg -color-threshold 'sRGB(160,110,0)-sRGB(205,155,45)' mask.png
```

HSV range:

```bash
magick input.jpg -colorspace HSV \
  -color-threshold 'hsv(35,25%,20%)-hsv(75,100%,100%)' \
  -colorspace sRGB mask.png
```

Hue wraps at the endpoint; a red range may need two ranges combined.

Fuzz distance:

```bash
magick input.png -fuzz 10% -fill none -draw 'matte 0,0 floodfill' output.png
```

Test transparent colors carefully because hidden RGB values can affect distance unless alpha/channel semantics are explicit.

## CLUTs and color matrices

Apply a color lookup table:

```bash
magick input.png gradient.png -clut output.png
```

Hald CLUT:

```bash
magick input.jpg hald-clut.png -hald-clut graded.jpg
```

Generate an identity Hald CLUT:

```bash
magick hald:8 identity-hald.png
```

Color matrix:

```bash
magick input.png -color-matrix \
  '0.393 0.769 0.189 0 0
   0.349 0.686 0.168 0 0
   0.272 0.534 0.131 0 0
   0     0     0     1 0
   0     0     0     0 1' sepia.png
```

Channel expressions:

```bash
magick input.png -channel-fx 'red=>blue; blue=>red' swapped.png
```

Verify option availability and exact grammar in `options-index.md`.

## Color reduction

Reduce to an adaptive palette:

```bash
magick input.png -colors 64 output.png
magick input.png +dither -colors 64 output.png
```

Choose quantization colorspace:

```bash
magick input.png -colorspace Lab -colors 32 -colorspace sRGB output.png
```

Use a predefined palette:

```bash
magick input.png +dither -remap palette.png output.png
magick input.png -dither FloydSteinberg -remap palette.png output.png
```

Extract palette:

```bash
magick input.png -colors 16 -unique-colors -scale 800% palette.png
magick input.png -unique-colors txt:-
```

Count colors:

```bash
magick identify -format '%k colors\n' input.png
```

`-colors` does not guarantee preservation of particular brand colors. Include them in a remap palette when exact palette membership matters.

## Dithering

Error diffusion:

```bash
magick input.png -colors 16 -dither FloydSteinberg output.png
magick input.png -colors 16 -dither Riemersma output.png
```

Ordered dither:

```bash
magick input.png -ordered-dither o8x8 output.png
magick input.png -ordered-dither h8x8a output.png
```

Monochrome:

```bash
magick input.png -colorspace Gray -threshold 50% hard.png
magick input.png -colorspace Gray -ordered-dither o8x8 dithered.png
```

Posterize:

```bash
magick input.png -posterize 4 output.png
magick input.png +dither -posterize 4 flat.png
```

List dither maps:

```bash
magick -list threshold
```

Choose based on the display/output medium. Error diffusion preserves tone but can speckle and changes sensitively with crops; ordered dithering is stable and pattern-like.

Custom ordered threshold maps can encode line screens, clustered dots, or symbol patterns. Inspect available maps:

```bash
magick -list threshold
```

For an animation or tiled texture, prefer a spatially stable ordered map; error diffusion changes when the crop origin or neighbouring pixels change.

## Palette and transparency edge cases

GIF has one fully transparent palette entry; it cannot store continuous alpha. Choose among:

- flatten against a known final background;
- threshold alpha for hard edges;
- dither transparency against a known/patterned background;
- keep PNG/WebP when the final background is unknown.

Flatten:

```bash
magick input.png -background white -alpha remove -alpha off \
  -colors 256 output.gif
```

Hard alpha:

```bash
magick input.png -channel A -threshold 50% +channel \
  -colors 255 output.gif
```

Reserve palette membership when brand colors must survive:

```bash
magick input.png -dither FloydSteinberg -remap required-palette.png output.png
```

Quantization across an animation can assign different palettes to different frames and create flicker. Build/remap to one global palette; see `animation-montage-compare.md`.

PNG8 can preserve palette alpha subject to coder support, but it is not interchangeable with full RGBA PNG. Verify type, palette size, and alpha:

```bash
magick identify -verbose output.png
```

## Color-management verification

```bash
magick identify -format '%[colorspace] depth=%z profiles=%[profiles]\n' output
magick output.png -format '%[pixel:p{0,0}] %[pixel:p{w/2,h/2}]\n' info:
```

For ICC transforms, render reference patches or compare with a color-managed viewer. Pixel equality across different profile encodings is not a valid color-equivalence test.

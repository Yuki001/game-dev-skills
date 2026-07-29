# Advanced analysis and low-level workflows

## Contents

- [Histograms and statistics](#histograms-and-statistics)
- [Pixel enumeration](#pixel-enumeration)
- [Connected components](#connected-components)
- [Convex hull and bounding geometry](#convex-hull-and-bounding-geometry)
- [Similarity and template location](#similarity-and-template-location)
- [Image classification heuristics](#image-classification-heuristics)
- [Kernels and distance transforms](#kernels-and-distance-transforms)
- [Fourier transforms](#fourier-transforms)
- [HDRI and numeric range](#hdri-and-numeric-range)
- [Raw streaming](#raw-streaming)
- [Registers, options, and calculated geometry](#registers-options-and-calculated-geometry)

## Histograms and statistics

Text histogram:

```bash
magick input.png -depth 8 -format %c histogram:info:-
```

Unique colors:

```bash
magick input.png -unique-colors txt:-
magick identify -format '%k\n' input.png
```

Global statistics:

```bash
magick input.png -format \
  'min=%[min] max=%[max] mean=%[mean] sd=%[standard-deviation] entropy=%[entropy]\n' \
  info:
```

Per-channel:

```bash
magick input.png -channel RGB -separate \
  -format 'scene=%s mean=%[mean] sd=%[standard-deviation]\n' info:
```

Moments/features:

```bash
magick identify -moments input.png
magick identify -features 1 input.png
```

Output syntax can change and be verbose; parse a machine-readable `-format` when possible.

## Pixel enumeration

Inspect all pixels:

```bash
magick input.png -depth 8 txt:-
```

One pixel:

```bash
magick input.png -format '%[pixel:p{20,30}]\n' info:
```

Region mean:

```bash
magick input.png -crop 100x80+20+30 +repage \
  -format '%[mean]\n' info:
```

Export channels:

```bash
magick input.png -depth 8 rgba:-
```

Pixel enumeration is huge; crop or stream for large images.

## Connected components

Label foreground components:

```bash
magick mask.png -connected-components 4 labels.png
```

Verbose table:

```bash
magick mask.png -define connected-components:verbose=true \
  -connected-components 8 null:
```

Filter by area:

```bash
magick mask.png -define connected-components:area-threshold=100 \
  -connected-components 8 cleaned.png
```

Keep selected IDs:

```bash
magick mask.png -define connected-components:keep='1,3,7' \
  -connected-components 8 output.png
```

Remove IDs:

```bash
magick mask.png -define connected-components:remove='0,2' \
  -connected-components 8 output.png
```

Use 4-connectivity when diagonal touch should not connect; use 8-connectivity when it should.

Typical segmentation pipeline:

```bash
magick input.jpg -colorspace Gray -threshold 60% -negate \
  -morphology Open Disk:1 \
  -define connected-components:verbose=true \
  -connected-components 8 labels.png
```

Inspect polarity: the background is usually the largest component and commonly ID 0, but do not hard-code assumptions without reading the table.

## Convex hull and bounding geometry

Convex hull from foreground:

```bash
magick mask.png -format '%[convex-hull]\n' info:
```

Draw:

```bash
magick mask.png -set option:hull '%[convex-hull]' \
  -fill none -stroke red -strokewidth 2 \
  -draw 'polygon %[hull]' hull.png
```

Minimum bounding box properties:

```bash
magick mask.png -format '%[minimum-bounding-box]\n' info:
```

Deskew by detected angle:

```bash
magick input.png -set option:angle '%[minimum-bounding-box:angle]' \
  -background white -rotate '%[angle]' output.png
```

Property names and availability are version-specific; verify with the installed `magick` help and a small mask.

Trim bounding box:

```bash
magick mask.png -format '%@' info:
```

Use `%@` or `-trim -format '%[page]'` to derive a content box without necessarily writing a cropped image.

## Similarity and template location

```bash
magick search.png template.png -metric NCC -subimage-search result.png
```

Locate extrema in a similarity map:

```bash
magick similarity-map.png -define identify:locate=maximum \
  -define identify:limit=10 -identify null:
```

Use a mask to exclude irrelevant template pixels if supported by the comparison form. Normalize scale, rotation, colorspace, and alpha before template matching.

Perceptual hashes:

```bash
magick identify -moments image.png
```

For bulk search, store features externally and use ImageMagick only for final verification/diffs.

## Image classification heuristics

ImageMagick can extract features for sorting, but it does not provide a semantic photo/cartoon/document classifier. Combine several recorded measurements and calibrate thresholds on known examples.

Basic type and palette:

```bash
magick identify -format \
  '%f|%[type]|%[colorspace]|colors=%k|mean=%[mean]|sd=%[standard-deviation]|entropy=%[entropy]\n' \
  input.png
```

Detect a nearly blank page by measuring standard deviation and foreground fraction after thresholding:

```bash
magick scan.png -colorspace Gray -threshold 95% -negate \
  -format 'foreground-mean=%[fx:mean]\n' info:
```

Average and predominant colors:

```bash
magick input.png -resize 1x1! -format '%[pixel:p{0,0}]\n' info:
magick input.png -colors 1 -unique-colors txt:-
```

Corner/background samples:

```bash
magick input.png -format \
  'nw=%[pixel:p{0,0}] ne=%[pixel:p{w-1,0}] sw=%[pixel:p{0,h-1}] se=%[pixel:p{w-1,h-1}]\n' \
  info:
```

Edge/detail proxy:

```bash
magick input.png -colorspace Gray -morphology Convolve Laplacian:0 \
  -format 'edge-mean=%[mean]\n' info:
```

Feature vector for texture:

```bash
magick identify -features 1 input.png
magick identify -moments input.png
```

Use these for candidate filtering—blank fax detection, line-art/photo separation, duplicate clustering, or fixed-camera change detection—then verify borderline cases visually. JPEG noise, scan borders, alpha, resizing, and colorspace can shift all thresholds.

## Kernels and distance transforms

Show built-in kernel:

```bash
magick xc: -define morphology:showKernel=1 \
  -morphology Dilate Disk:5 null:
```

Render a kernel:

```bash
magick xc: -kernel Disk:5 -morphology Convolve Disk:5 kernel.png
```

Distance:

```bash
magick mask.png -morphology Distance Euclidean:4 distance.miff
magick distance.miff -auto-level distance.png
```

Voronoi from seeds:

```bash
magick seeds.png -morphology Voronoi Euclidean:4 regions.png
```

Skeleton:

```bash
magick mask.png -morphology Thinning:-1 Skeleton skeleton.png
```

Kernel operations depend on quantum range and morphology polarity. Use MIFF or a high-depth format for intermediate numeric data.

## Fourier transforms

Check build:

```bash
magick -version
```

FFTW delegate/HDRI may be required for some workflows.

Forward transform:

```bash
magick input.png -colorspace Gray -fft +depth +adjoin 'fft-%d.miff'
```

The default pair is commonly magnitude/phase. Real/imaginary forms use defines/options documented by the installed version.

Inverse:

```bash
magick fft-0.miff fft-1.miff -ift reconstructed.png
```

Round-trip check:

```bash
magick compare -metric RMSE input.png reconstructed.png null:
```

Frequency spectrum visualization:

```bash
magick fft-0.miff -auto-level -evaluate log 1000 spectrum.png
```

Frequency-domain filtering:

1. Convert to an appropriate linear grayscale/float representation.
2. FFT into a two-image complex representation.
3. Generate a same-sized frequency mask.
4. Multiply complex components consistently.
5. IFT.
6. Normalize or clamp only with a defined numeric goal.

Fourier list ordering and representation are easy to corrupt. Preserve MIFF/HDRI intermediates and verify a no-op round trip before applying a filter.

## HDRI and numeric range

Inspect:

```bash
magick identify -version
```

Look for `HDRI` in Features.

HDRI builds preserve negative and out-of-range values in suitable in-memory/intermediate formats. Ordinary PNG/JPEG outputs clamp/quantize them.

High-depth intermediate:

```bash
magick input.exr -depth 32 output.miff
magick input.exr -evaluate multiply 2 output.exr
```

Clamp deliberately:

```bash
magick numeric.miff -clamp output.png
```

Quantum scaling:

```bash
magick input.png -format '%[quantum:range]\n' info:
```

Expressions may use normalized values or quantum-scaled statistics depending on escape/operator. Test with `xc:black`, `xc:gray50`, and `xc:white`.

Ultra HDR example:

```bash
magick -define uhdr:hdr-color-gamut=bt709 \
  -define uhdr:hdr-color-transfer=hlg \
  \( sdr.tif -depth 8 \) \( hdr.tif -depth 16 \) uhdr:output.jpg
```

Delegate support and metadata requirements vary; inspect the resulting format and properties.

## Raw streaming

Rows/regions without normal full-image output:

```bash
magick stream -map rgb -storage-type char input.jpg pixels.dat
magick stream -map i -storage-type double \
  -extract 100x100+30+40 input.tif gray.raw
```

Round trip:

```bash
magick -depth 8 -size 640x480 rgb:pixels.dat restored.png
```

Map examples:

```text
rgb rgba bgr bgra i cmyk
```

Storage types:

```text
char short integer long float double quantum
```

Record endianness and storage type. `stream` is useful for large raw extraction, not a substitute for all operations.

## Registers, options, and calculated geometry

Set a reusable option:

```bash
magick input.png -set option:target '%[fx:min(w,h)]' \
  -resize '%[target]x%[target]' output.png
```

Filename register:

```bash
magick input.tif -set filename:base '%[basename]' \
  'output/%[filename:base]-%03d.png'
```

In-memory image register:

```bash
magick input.png -write mpr:original \
  -resize 25% -write mpr:small +delete \
  mpr:original mpr:small +append output.png
```

Print registers:

```bash
magick input.png -set option:area '%[fx:w*h]' \
  -print 'area=%[area]\n' null:
```

Properties, artifacts, options, and registry entries have different lifetimes/scopes. Use `-set option:key value` for command-local calculated strings and `mpr:` for command-local images.

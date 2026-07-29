# Distortion, mapping, and pixel expressions

## Contents

- [Simple geometric warps](#simple-geometric-warps)
- [Affine and SRT](#affine-and-srt)
- [General distort](#general-distort)
- [Lens correction and calibration](#lens-correction-and-calibration)
- [Control-point perspective](#control-point-perspective)
- [Virtual pixels, interpolation, and viewport](#virtual-pixels-interpolation-and-viewport)
- [Displacement maps](#displacement-maps)
- [Absolute distortion maps](#absolute-distortion-maps)
- [Variable blur maps](#variable-blur-maps)
- [Evaluate and function](#evaluate-and-function)
- [FX expressions](#fx-expressions)
- [Sparse color and polynomial transforms](#sparse-color-and-polynomial-transforms)
- [Performance and verification](#performance-and-verification)

## Simple geometric warps

```bash
magick input.png -flip output.png
magick input.png -flop output.png
magick input.png -transpose output.png
magick input.png -transverse output.png
magick input.png -rotate 90 output.png
magick input.png -roll +120-40 output.png
magick input.png -shear 20x0 output.png
magick input.png -wave 20x120 output.png
magick input.png -swirl 90 output.png
magick input.png -implode 0.5 output.png
```

Control fill beyond source bounds:

```bash
magick input.png -background none -virtual-pixel transparent \
  -rotate 17 output.png
```

`-roll` wraps. `-rotate` expands according to background/alpha. `-shear` and distort operations can retain page offsets; use `+repage` when a fresh canvas is desired.

## Affine and SRT

Scale-rotate-translate:

```bash
magick input.png -virtual-pixel transparent +distort SRT '1.2 30' output.png
magick input.png -virtual-pixel transparent +distort SRT \
  '200,150 1.2 30 400,300' output.png
```

SRT argument forms can specify source center, scale, angle, and destination center. Use `-verbose` on a no-op or consult the option docs when composing dynamic forms.

Affine matrix:

```bash
magick input.png -virtual-pixel transparent \
  -affine '1,0.2,-0.1,1,30,20' -transform output.png
```

General affine distortion:

```bash
magick input.png -virtual-pixel transparent \
  +distort AffineProjection '1,0.2,-0.1,1,30,20' output.png
```

Control points:

```bash
magick input.png -virtual-pixel transparent +distort Affine \
  '0,0 20,30  400,0 430,10  0,300 10,340' output.png
```

`+distort` requests best-fit output; `-distort` normally retains the source viewport. This plus/minus distinction is intentional.

## General distort

Common methods:

```text
Affine
AffineProjection
ScaleRotateTranslate / SRT
Perspective
PerspectiveProjection
BilinearForward
BilinearReverse
Polynomial
Arc
Polar
DePolar
Barrel
BarrelInverse
Shepards
Resize
```

List/verify:

```bash
magick -list distort
```

Arc text/image:

```bash
magick label.png -virtual-pixel transparent -distort Arc 120 output.png
```

Polar:

```bash
magick input.png -virtual-pixel horizontal-tile -distort Polar 0 output.png
magick polar.png -virtual-pixel horizontal-tile -distort DePolar 0 restored.png
```

Barrel:

```bash
magick input.jpg -virtual-pixel black -distort Barrel \
  '0.0 0.0 -0.18 1.18' corrected.jpg
```

Lens coefficients are calibration-specific; do not invent them.

## Lens correction and calibration

Barrel/pincushion correction is a calibration problem, not a visual preset. Use known coefficients for the exact camera/lens/focal-length combination:

```bash
magick input.jpg -virtual-pixel black \
  -distort Barrel 'A B C D' corrected.jpg
```

`D` is commonly chosen so the polynomial is neutral at a reference radius:

```text
D = 1 - A - B - C
```

That convention does not guarantee that output scale or corners match the original. Decide whether the requirement is:

- preserve the center scale;
- preserve the original canvas;
- retain every corrected source pixel;
- crop away invalid edge pixels.

Use `-distort Barrel` with a fixed viewport when dimensions must stay fixed, or `+distort Barrel` to request a best-fit canvas:

```bash
magick input.jpg -virtual-pixel black \
  -define distort:viewport='%[fx:w]x%[fx:h]+0+0' \
  -distort Barrel '0.0 0.0 -0.18 1.18' corrected-fixed.jpg
```

Calibrate from straight lines or a checkerboard:

1. Photograph a planar grid at the intended focal length and focus distance.
2. Correct EXIF orientation before measuring points.
3. Fit coefficients with Hugin/lensfun or external least-squares tooling.
4. Test on held-out grid lines near the corners, not only the calibration image.
5. Store coefficients together with camera, lens, focal length, dimensions, and crop assumptions.

If control-point pairs are available instead of coefficients, use a least-squares `Perspective`, `Polynomial`, or `Shepards` fit and inspect residual error. Do not transfer coefficients between resized/cropped images without accounting for the changed optical center and normalization.

## Control-point perspective

Four corners:

```bash
magick input.png -virtual-pixel transparent +distort Perspective \
  '0,0 40,30
   800,0 760,70
   800,600 790,560
   0,600 20,590' output.png
```

Rectify a photographed page by mapping source page corners to a rectangle:

```bash
magick photo.jpg -virtual-pixel white +distort Perspective \
  '120,80 0,0
   1820,140 1700,0
   1760,2350 1700,2200
   160,2290 0,2200' \
  -crop 1700x2200+0+0 +repage rectified.png
```

Point order does not need to be clockwise, but each source coordinate must pair with the intended destination coordinate. Draw/annotate the detected points during debugging.

Use more than four pairs with methods that fit least squares:

```bash
magick input.png +distort Perspective \
  'sx1,sy1 dx1,dy1  sx2,sy2 dx2,dy2  ...' output.png
```

## Virtual pixels, interpolation, and viewport

Virtual pixel methods determine colors sampled outside the source:

```bash
magick -list virtual-pixel
```

Common:

```text
transparent background black white gray
edge mirror tile horizontal-tile vertical-tile
checker-tile random dither
```

```bash
magick input.png -background '#0f172a' -virtual-pixel background \
  +distort SRT 25 output.png
```

Interpolation:

```bash
magick input.png -interpolate nearest -distort SRT 17 output.png
magick input.png -interpolate bilinear -distort SRT 17 output.png
magick input.png -filter Lanczos -distort SRT 17 output.png
```

Distort often uses EWA resampling and `-filter`; some map operations use `-interpolate`. Set the control appropriate to the operator.

Viewport:

```bash
magick input.png -define distort:viewport=800x600+0+0 \
  -distort SRT 17 output.png
```

Scale output for supersampling:

```bash
magick input.png -define distort:scale=4 \
  -distort SRT 17 -resize 25% output.png
```

Search `defines-index.md` for `distort:`.

## Displacement maps

A displacement map encodes relative X/Y offsets, commonly with 50% gray as no displacement.

Horizontal wave map:

```bash
magick -size 800x600 gradient: -rotate 90 \
  -function sinusoid 8,0,0.5,0.5 wave-map.png
```

Apply:

```bash
magick input.png wave-map.png -compose Displace \
  -define compose:args='40x0' -composite output.png
```

Two-axis map can use red/green or two map images depending on the compose form:

```bash
magick input.png x-map.png y-map.png \
  -define compose:args='40x25' -compose Displace -composite output.png
```

Build a radial displacement:

```bash
magick -size 800x600 radial-gradient:black-white radial-map.png
magick input.png radial-map.png -compose Displace \
  -define compose:args='30x30' -composite output.png
```

Map semantics depend on channel depth, midpoint, alpha, and compose arguments. Save and inspect maps independently.

## Absolute distortion maps

`-fx` can sample coordinates from other images:

```bash
magick input.png \( -size 800x600 gradient: -rotate 90 \) \
  -fx 'u.p{v*w,j}' output.png
```

Two-map lookup:

```bash
magick input.png x-map.png y-map.png \
  -fx 'u[0].p{u[1]*w,u[2]*h}' output.png
```

Image indices:

- `u` or `u[0]` is the first image.
- `u[1]`, `u[2]` are later images.
- `p{x,y}` samples a pixel from the selected image.

Coordinate normalization and channel extraction must be explicit for robust maps.

Absolute maps are prone to one-pixel scaling mistakes because image coordinates run from `0` to `w-1` and `0` to `h-1`. Verify a no-op map with a pixel-check pattern before building an effect:

```bash
magick -size 256x256 pattern:gray50 \
  \( -size 256x256 gradient: -rotate 90 \) \
  \( -size 256x256 gradient: -flip \) \
  -compose Distort -define compose:args='' -composite no-op-check.png
```

## Variable blur maps

The `Blur` compose method uses a grayscale map to vary blur strength spatially. Black requests little/no blur and white requests the maximum:

```bash
magick input.png blur-map.png \
  -compose Blur -define compose:args='12' -composite output.png
```

Use red/green map channels for independently varying the two ellipse axes:

```bash
magick x-blur-map.png y-blur-map.png -background black \
  -channel RG -combine blur-map-rg.png
magick input.png blur-map-rg.png \
  -compose Blur -define compose:args='18x6' -composite output.png
```

Map and source must have the intended dimensions and page offsets. Save the map separately and test black, gray50, and white maps first. Blur mapping uses neighbourhood pixels, so select a suitable `-virtual-pixel` method and expect edge effects.

To vary blur angle as well as aspect ratio, encode magnitude/direction in the channels expected by the installed compose implementation; `compose:args` accepts forms such as `XxY+angle`. Exact channel semantics are version-sensitive, so build black/gray/white and primary-channel test maps before applying a complex map.

## Evaluate and function

Constant arithmetic:

```bash
magick input.png -evaluate multiply 1.1 output.png
magick input.png -evaluate add 0.05 output.png
magick input.png -evaluate pow 0.8 output.png
magick input.png -channel A -evaluate set 50% +channel output.png
```

Sequence evaluation:

```bash
magick a.png b.png -evaluate-sequence mean average.png
magick a.png b.png c.png -evaluate-sequence median median.png
magick a.png b.png -evaluate-sequence max max.png
```

Functions:

```bash
magick gradient.png -function polynomial '0,1' output.png
magick gradient.png -function sinusoid '3,0,0.5,0.5' waves.png
```

Prefer `-evaluate`, `-function`, `-level`, or `-color-matrix` over `-fx` when they express the operation; they are usually faster and clearer.

## FX expressions

Simple:

```bash
magick input.png -fx '1-u' negative.png
magick input.png -fx '(r+g+b)/3' gray.png
magick input.png -fx 'u^0.8' gamma-like.png
```

Coordinate gradient:

```bash
magick -size 800x600 xc: -fx 'i/w' x-gradient.png
magick -size 800x600 xc: -fx 'j/h' y-gradient.png
```

Radial:

```bash
magick -size 800x600 xc: \
  -fx '1-hypot(i-w/2,j-h/2)/hypot(w/2,h/2)' radial.png
```

Conditional mask:

```bash
magick input.png -fx 'intensity>0.6 ? 1 : 0' mask.png
```

Pixel access:

```bash
magick input.png -fx 'p{i-1,j}' shifted.png
magick input.png -virtual-pixel edge -fx '0.5*p{i-1,j}+0.5*p{i+1,j}' blur-x.png
```

Multiple images:

```bash
magick a.png b.png -fx '0.7*u+0.3*v' blend.png
magick a.png b.png -fx 'abs(u-v)' difference.png
```

FX is evaluated per pixel and can be slow. Use named variables and a small test crop for complex formulas:

```bash
magick input.png -fx 'dx=i-w/2; dy=j-h/2; r=hypot(dx,dy); r<100 ? u : 0' output.png
```

## Sparse color and polynomial transforms

Interpolate colors from points:

```bash
magick -size 800x600 xc: \
  -sparse-color Barycentric \
  '0,0 red 799,0 blue 0,599 green 799,599 white' gradient.png
```

Voronoi regions:

```bash
magick -size 800x600 xc: \
  -sparse-color Voronoi \
  '100,100 red 700,120 blue 400,520 green' regions.png
```

Shepard interpolation:

```bash
magick -size 800x600 xc: \
  -sparse-color Shepards \
  '100,100 red 700,120 blue 400,520 green' smooth.png
```

Polynomial distort maps and color functions are advanced; fit coefficients externally when possible and verify with known control points.

## Performance and verification

- Crop a small region while developing expressions.
- Prefer built-in operators to per-pixel `-fx`.
- Use `-monitor` for long operations.
- Set `-limit time`, memory, map, and disk for untrusted or large work.
- Save maps and control-point previews.
- Compare dimensions, virtual page, alpha, and edge coverage.

```bash
magick input.png -crop 400x400+0+0 +repage -fx '...' test.png
magick identify -format '%wx%h page=%[page]\n' output.png
magick input.png output.png -compose difference -composite -auto-level diff.png
```

# Photo, thumbnail, and constructed effects

## Contents

- [Digital photo preparation](#digital-photo-preparation)
- [Selective focus and anonymization](#selective-focus-and-anonymization)
- [Multiple exposures and textures](#multiple-exposures-and-textures)
- [Photo cutouts and green screen](#photo-cutouts-and-green-screen)
- [Sketch and outline effects](#sketch-and-outline-effects)
- [Vignette correction](#vignette-correction)
- [Thumbnail decoration](#thumbnail-decoration)
- [Constructed 3-D and lighting effects](#constructed-3-d-and-lighting-effects)
- [Verification](#verification)

This file covers the task-oriented examples spread across the Usage `photos`, `thumbnails`, `advanced`, `backgrounds`, and `transform` pages. Load the lower-level reference named in each section when changing the mask, geometry, compose method, or filter.

## Digital photo preparation

Inspect EXIF and normalize orientation before crop, perspective, or annotation:

```bash
magick identify -format '%[EXIF:DateTimeOriginal] %[orientation]\n' photo.jpg
magick photo.jpg -auto-orient oriented.jpg
```

Correct a small horizon error:

```bash
magick photo.jpg -background none -rotate -1.2 \
  -gravity center -crop '%[fx:w*cos(1.2*pi/180)-h*sin(1.2*pi/180)]x%[fx:h*cos(1.2*pi/180)-w*sin(1.2*pi/180)]+0+0' \
  +repage leveled.png
```

The calculated crop is conservative only for small angles and may need manual review. For documents, use `-deskew`; for horizons, measure the desired angle explicitly.

Brighten underexposed midtones without blindly clipping highlights:

```bash
magick photo.jpg -sigmoidal-contrast 5x45% -modulate 104,100,100 brightened.jpg
```

Inspect the histogram first. Exposure recovery cannot restore clipped shadows/highlights, and JPEG banding/noise can become more visible.

Reduce noise by spatial binning when a smaller output is acceptable:

```bash
magick photo.jpg -filter box -resize 50% binned.jpg
```

This averages neighbouring pixels and changes dimensions. Use a denoiser when full resolution must be retained.

## Selective focus and anonymization

Tilt-shift style selective focus uses a full-size grayscale mask: black keeps the sharp original; white overlays the blurred clone.

```bash
magick photo.jpg \
  \( +clone -blur 0x12 focus-mask.png -alpha off \
     -compose CopyOpacity -composite \) \
  -compose Over -composite tilt-shift.jpg
```

Make `focus-mask.png` smooth to avoid a visible transition. A perspective-shaped band usually looks more convincing than a simple horizontal gradient.

Blur or pixelate a known rectangular identity region:

```bash
magick photo.jpg -region 280x180+620+210 -blur 0x18 +region anonymized.jpg
magick photo.jpg -region 280x180+620+210 \
  -scale 10% -scale 1000% +region pixelated.jpg
```

For faces at arbitrary positions, use externally detected boxes/masks and apply the operation to each. ImageMagick does not detect faces on its own.

Irregular region:

```bash
magick photo.jpg \
  \( +clone -blur 0x18 irregular-mask.png -alpha off \
     -compose CopyOpacity -composite \) \
  -compose Over -composite anonymized.png
```

## Multiple exposures and textures

Double exposure with equal-size images:

```bash
magick first.jpg second.jpg -define compose:args=50,50 \
  -compose Blend -composite double-exposure.jpg
```

Align and normalize dimensions first. `Screen`, `Lighten`, or a mask-controlled `Over` blend can preserve highlights differently:

```bash
magick portrait.jpg texture.jpg -compose Screen -composite screened.jpg
```

Add texture while preserving most luminosity:

```bash
magick photo.jpg texture.jpg -compose SoftLight -composite textured.jpg
```

Control texture opacity before compositing:

```bash
magick photo.jpg \
  \( texture.jpg -alpha set -channel A -evaluate multiply 0.35 +channel \) \
  -compose SoftLight -composite textured.jpg
```

Resize/crop the texture to the photo canvas and inspect colorspace/alpha; a compose method alone does not align inputs.

Blurred overlap between side-by-side photos:

1. extend both photos into a common canvas with an overlap;
2. create opposing horizontal alpha gradients across the overlap;
3. apply each gradient as alpha;
4. composite and flatten.

Keep both masks as files while tuning the seam.

## Photo cutouts and green screen

Start with the decision table in `compose-mask-layers.md`. A quick chroma key:

```bash
magick green-screen.png -alpha on -fuzz 18% \
  -transparent '#00b140' keyed.png
```

Then inspect:

- alpha edge on black, white, and checkerboard;
- green/blue color spill in semitransparent foreground pixels;
- holes caused by foreground colors close to the key color;
- hair, motion blur, shadows, and compression blocks.

Use a separately generated mask for production work:

```bash
magick green-screen.png key-mask.png -alpha off \
  -compose CopyOpacity -composite keyed.png
```

Mask cleanup belongs in `filters-effects-morphology.md`; known/two-background recovery belongs in `compose-mask-layers.md`.

## Sketch and outline effects

Charcoal:

```bash
magick photo.jpg -colorspace Gray -charcoal 1 charcoal.png
```

Pencil-sketch style:

```bash
magick photo.jpg -colorspace Gray \
  \( +clone -negate -blur 0x8 \) \
  -compose ColorDodge -composite -auto-level pencil.png
```

Coloring-book outline:

```bash
magick photo.jpg -colorspace Gray -canny 0x1+10%+30% \
  -negate -threshold 70% outline.png
```

Real photos often need denoise/contrast normalization before edge extraction. Check thin features at the intended print size.

## Vignette correction

Lens vignetting should be corrected with a flat-field image captured using the same lens, aperture, focal length, focus, crop, and sensor pipeline:

```bash
magick flat-field.tif -colorspace Gray -blur 0x20 \
  -auto-level flat-normalized.miff
magick photo.tif flat-normalized.miff \
  -compose DivideSrc -composite -auto-level corrected.tif
```

Compose direction and normalization affect exposure. Test with a uniform target before batch use. A synthetic radial gradient can approximate correction, but it can amplify corner noise and cannot model decentering or dust.

## Thumbnail decoration

Core fit/pad/crop choices and rounded-corner/Polaroid examples are in `geometry-resize-crop.md`.

Soft edge:

```bash
magick thumbnail.png \( +clone -alpha extract -blur 0x8 \) \
  -alpha off -compose CopyOpacity -composite soft-edge.png
```

Drop shadow after all framing/rotation:

```bash
magick framed.png \
  \( +clone -background black -shadow 60x8+12+12 \) \
  +swap -background none -layers merge +repage shadowed.png
```

Badge overlay:

```bash
magick thumbnail.png badge.png -gravity northeast -geometry +12+12 \
  -compose Over -composite badged.png
```

For torn edges, page curls, glass bubbles, and edge-piece frames:

1. build an explicit silhouette/height mask;
2. apply texture or lighting to that mask;
3. copy the mask to alpha;
4. composite the result over the thumbnail;
5. add the final shadow.

This mask-first form is easier to debug and reuse than a single long stack.

## Constructed 3-D and lighting effects

The Usage `advanced` and `backgrounds` pages build bullets, reflections, jigsaw pieces, gel/aqua buttons, stars, and flares from the same primitives:

- a binary silhouette or text mask;
- a distance/blurred height map;
- `-shade`, emboss, or displaced gradients for lighting;
- color/texture applied with `Overlay`, `HardLight`, `Multiply`, or CLUT;
- alpha copied from the original silhouette;
- shadow/reflection merged as a separate layer.

Reflection with fading alpha:

```bash
magick object.png \
  \( +clone -flip \
     \( -size '%[fx:w]x%[fx:h]' gradient:'#808080cc-#80808000' \) \
     -compose DstIn -composite \) \
  -append reflection.png
```

If dynamic `-size` escapes are unsupported in the installed build, query dimensions first and pass a literal size.

Create a lit gel-like shape:

```bash
magick shape-mask.png -blur 0x4 -shade 120x35 -auto-level lighting.png
magick -size 600x300 xc:'#38bdf8' lighting.png \
  -compose Overlay -composite shape-mask.png \
  -alpha off -compose CopyOpacity -composite gel.png
```

Use a high-depth lossless intermediate for repeated lighting/composition. Elaborate effects are parameter-sensitive; save silhouette, height map, lighting, color layer, and alpha separately.

## Verification

```bash
magick identify -format '%f %wx%h %[colorspace] %[channels] %[opaque]\n' output.png
magick -size 1200x800 pattern:checkerboard output.png \
  -compose Over -composite transparency-preview.png
```

For photos, compare at 100% and at final display size. For masks/effects, also inspect the alpha alone:

```bash
magick output.png -alpha extract alpha.png
```

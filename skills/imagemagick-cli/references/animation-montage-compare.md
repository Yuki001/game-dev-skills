# Animation, montage, and image comparison

## Contents

- [Animation metadata](#animation-metadata)
- [Coalesce and disposal](#coalesce-and-disposal)
- [Create and edit animations](#create-and-edit-animations)
- [Merge and synchronize animations](#merge-and-synchronize-animations)
- [Optimize animations](#optimize-animations)
- [Video frames, shared palettes, and deinterlacing](#video-frames-shared-palettes-and-deinterlacing)
- [Montage and contact sheets](#montage-and-contact-sheets)
- [Comparison metrics](#comparison-metrics)
- [Difference images](#difference-images)
- [Subimage search and duplicate detection](#subimage-search-and-duplicate-detection)
- [Verification](#verification)

## Animation metadata

Inspect every frame:

```bash
magick identify -format \
  'scene=%s size=%wx%h page=%[page] delay=%T dispose=%D iterations=%[iterations]\n' \
  animation.gif
```

Key fields:

- delay is in ticks; GIF commonly uses 100 ticks/second.
- disposal controls how the canvas changes before the next frame.
- page geometry carries canvas size and frame offset.
- optimized GIF frames can be small deltas, not full canvases.
- loop/iterations metadata may be stored on the sequence.

Split raw stored frames:

```bash
magick animation.gif 'raw-%03d.png'
```

Split visual frames:

```bash
magick animation.gif -coalesce 'frame-%03d.png'
```

Use coalesced frames for editing what a viewer actually displays.

## Coalesce and disposal

Coalesce:

```bash
magick animation.gif -coalesce coalesced.miff
```

View frame differences:

```bash
magick animation.gif -coalesce -layers CompareAny 'changes-%03d.png'
```

Set disposal:

```bash
magick frame-*.png -set dispose background -delay 8 -loop 0 animation.gif
```

Common disposal values:

- `None`: leave previous frame.
- `Background`: clear frame region.
- `Previous`: restore prior canvas.

Incorrect disposal causes trails, holes, or missing content. Use a checkerboard background and a frame contact sheet to diagnose.

## Create and edit animations

Create GIF:

```bash
magick -delay 8 -loop 0 frame-*.png animation.gif
```

Per-frame filename order must be deterministic; zero-pad numeric names.

Resize:

```bash
magick animation.gif -coalesce -resize '640x640>' \
  -layers Optimize animation-small.gif
```

Crop:

```bash
magick animation.gif -coalesce -gravity center \
  -crop 640x360+0+0 +repage -layers Optimize animation-crop.gif
```

Annotate all frames:

```bash
magick animation.gif -coalesce -gravity southeast \
  -fill white -stroke black -strokewidth 1 -pointsize 20 \
  -annotate +12+10 '© Example' -layers Optimize output.gif
```

Reverse:

```bash
magick animation.gif -coalesce -reverse -layers Optimize reversed.gif
```

Patrol loop:

```bash
magick animation.gif -coalesce \
  \( -clone 0--1 \) \( -clone -2-1 -reverse \) \
  -delete 0--1 -set delay 8 -loop 0 -layers Optimize patrol.gif
```

Simpler with pre-split frames:

```bash
magick frame-*.png frame-*.png -reverse -delay 8 -loop 0 patrol.gif
```

Avoid duplicating endpoints if a pause is not intended.

Morph:

```bash
magick first.png second.png -morph 12 -delay 6 -loop 0 morph.gif
```

Normalize size/canvas before morphing.

Change speed:

```bash
magick animation.gif -coalesce -set delay 4 -layers Optimize faster.gif
```

Multiply existing delay with an expression:

```bash
magick animation.gif -coalesce -set delay '%[fx:t*2]' -layers Optimize slower.gif
```

Verify expression/property support; frame delay can have minimums and viewer-specific rounding.

## Merge and synchronize animations

Animations are timelines, not merely image lists. Coalesce both inputs before spatial composition:

```bash
magick left.gif -coalesce left.miff
magick right.gif -coalesce right.miff
magick left.miff right.miff +append -layers Optimize side-by-side.gif
```

The simple `+append` form pairs lists only when frame counts and timing are already compatible. For two frame lists with equal counts, use `-layers Composite`:

```bash
magick background.gif -coalesce background.miff
magick overlay.gif -coalesce overlay.miff
magick background.miff overlay.miff -gravity center \
  -compose Over -layers Composite -layers Optimize merged.gif
```

Before merging, decide:

- whether the shorter animation should stop, hold its last frame, or loop;
- whether delays share the same tick rate;
- whether timelines align by frame index or elapsed time;
- which loop/disposal metadata should survive.

For time-wise concatenation, normalize canvases, then append the scene lists:

```bash
magick first.gif -coalesce -background none -gravity center \
  -extent 800x600 first.miff
magick second.gif -coalesce -background none -gravity center \
  -extent 800x600 second.miff
magick first.miff second.miff -set dispose none -loop 0 \
  -layers Optimize serial.gif
```

Use MIFF intermediates to retain page, delay, alpha, and list data. Inspect the final delay/disposal inventory; a visually correct contact sheet cannot reveal timing errors.

## Optimize animations

Basic:

```bash
magick animation.gif -coalesce -layers Optimize optimized.gif
```

Frame optimization:

```bash
magick animation.gif -coalesce -layers OptimizeFrame optimized.gif
```

Remove duplicates:

```bash
magick animation.gif -coalesce -layers RemoveDups optimized.gif
```

Remove zero-delay update frames:

```bash
magick animation.gif -coalesce -layers RemoveZero optimized.gif
```

Color optimize:

```bash
magick animation.gif -coalesce -layers Optimize \
  -colors 256 optimized.gif
```

Quantization across frames can flicker if each frame receives a different palette. Build/remap to a shared palette where consistent color is important.

GIF transparency is binary. Semi-transparent edges need flattening against a known background or carefully dithered transparency.

Compare byte size:

```bash
magick identify -format '%b\n' animation.gif optimized.gif
```

Do not optimize before editing. Always coalesce → edit → optimize.

## Video frames, shared palettes, and deinterlacing

ImageMagick video decoding depends on an installed delegate and is less predictable than extracting frames with FFmpeg. Prefer:

1. decode/scale/select frame rate with FFmpeg or another video tool;
2. process the resulting numbered frames with ImageMagick;
3. assemble and optimize the animation.

Build one palette from representative coalesced frames, then remap every frame to it:

```bash
magick frame-*.png -append -colors 256 -unique-colors palette.png
magick frame-*.png -dither FloydSteinberg -remap palette.png \
  -delay 4 -loop 0 -layers Optimize animation.gif
```

A shared palette prevents independent per-frame palettes from changing colors and flickering. Error-diffusion dither can still shimmer as objects move. Ordered dithering is spatially stable and often compresses better:

```bash
magick frame-*.png -ordered-dither 'o8x8,8,8,4' +remap \
  -delay 4 -loop 0 -layers Optimize animation.gif
```

Check that the ordered-dither result stays within 256 colors before writing GIF. For a content-specific global palette, remap rather than relying on `+remap` alone.

For an interlaced still frame, select one field and expand it:

```bash
magick interlaced.png -sample 100%x50% -resize 100%x200% field-a.png
magick interlaced.png -define sample:offset=75 \
  -sample 100%x50% -resize 100%x200% field-b.png
```

`-sample` chooses rows; the second `-resize` interpolates the missing lines. Field order varies by source. This discards half the temporal samples and is not motion-adaptive deinterlacing; use a video tool for production footage.

## Montage and contact sheets

Basic:

```bash
magick montage image1.png image2.png image3.png \
  -geometry +8+8 montage.png
```

Fixed thumbnail cells:

```bash
magick montage *.jpg -thumbnail '240x180>' \
  -tile 4x -geometry 240x180+12+28 -background '#111827' contact.png
```

Labels:

```bash
magick montage *.jpg -thumbnail '240x180>' -set label '%f' \
  -font DejaVu-Sans -pointsize 18 -fill white \
  -tile 4x -geometry 240x180+12+32 -background '#111827' contact.png
```

Frame/shadow:

```bash
magick montage *.png -thumbnail '200x200>' -label '%f' \
  -frame 6 -shadow -tile 5x -geometry +12+32 contact.png
```

Exact grid:

```bash
magick montage frame-*.png -tile 8x4 \
  -geometry 128x128+0+0 -background none sprite.png
```

For a last row with blanks:

```bash
magick montage input-*.png null: null: \
  -tile 4x -geometry 200x200+8+8 contact.png
```

Use `null:` placeholders deliberately and verify their effect in the installed version.

Ashlar layout:

```bash
magick '*.png' -resize 320x320 -label '%f' ashlar:ashlar.png
```

Contact sheet for animation frames:

```bash
magick animation.gif -coalesce -thumbnail 200x200 \
  -set label 'frame %s, %T ticks' \
  -background white -fill black -gravity center \
  -append null:
```

Usually it is clearer to split frames, then call `magick montage`.

## Comparison metrics

Basic:

```bash
magick compare -metric RMSE reference.png candidate.png difference.png
```

Metrics include:

```text
AE MAE MEPP MSE RMSE PSNR NCC PAE PHASH SSIM DSSIM
```

List/confirm on current build:

```bash
magick compare -help
```

No diff output:

```bash
magick compare -metric RMSE reference.png candidate.png null:
```

Metric output normally goes to stderr:

```bash
metric=$(magick compare -metric RMSE reference.png candidate.png null: 2>&1)
```

PowerShell:

```powershell
$metric = (& $magick compare -metric RMSE "reference.png" "candidate.png" "null:" 2>&1)
$exitCode = $LASTEXITCODE
```

Compare exit code may be nonzero when images differ. Distinguish “difference found” from parser/read/write failure by examining metric output and stderr.

Channel comparison:

```bash
magick compare -channel RGB -metric RMSE a.png b.png null:
magick compare -channel A -metric AE a.png b.png null:
```

Fuzz:

```bash
magick compare -fuzz 1% -metric AE a.png b.png null:
```

Choose a metric aligned to the question:

- `AE`: count of pixels outside fuzz tolerance.
- `RMSE`/`MAE`: numeric pixel error.
- `PSNR`: signal-to-noise, higher is better.
- `SSIM`/`DSSIM`: structural similarity where supported.
- `PHASH`: perceptual signature distance.
- `NCC`: correlation/template matching.

Normalize dimensions, colorspace, alpha, depth, page offsets, and profiles before interpreting a metric.

## Difference images

Default highlighted diff:

```bash
magick compare a.png b.png diff.png
```

Custom colors:

```bash
magick compare -highlight-color '#ef4444' -lowlight-color '#111827' \
  a.png b.png diff.png
```

Absolute difference:

```bash
magick a.png b.png -compose difference -composite diff.png
```

Amplify:

```bash
magick a.png b.png -compose difference -composite \
  -auto-level diff-amplified.png
```

Threshold changed pixels:

```bash
magick a.png b.png -compose difference -composite \
  -colorspace Gray -threshold 2% changed-mask.png
```

Overlay changed areas:

```bash
magick a.png changed-mask.png -fill red -colorize 40% overlay.png
```

Build the overlay explicitly through alpha if only changed regions should be colored.

## Subimage search and duplicate detection

Find template:

```bash
magick search.png template.png -metric NCC -subimage-search result.png
```

Similarity form:

```bash
magick search.png template.png -similarity-threshold 0.95 \
  -metric NCC -subimage-search result.png
```

The output can contain a match image and similarity map. Inspect verbose output and output scenes.

Perceptual hashes:

```bash
magick identify -moments image.png
magick image.png -define identify:locate=maximum -metric NCC \
  template.png -compare info:
```

For large duplicate collections, compute stable features/hashes once and cluster externally; pairwise `compare` scales poorly.

## Verification

Animation:

```bash
magick identify -format '%s|%T|%D|%wx%h|%[page]\n' output.gif
```

Contact sheet:

```bash
magick output.gif -coalesce 'verify-%03d.png'
magick montage verify-*.png -thumbnail 160x160 -label '%f' \
  -tile 6x -geometry +8+24 verify-contact.png
```

Compare original and optimized visual frames:

```bash
magick original.gif -coalesce original.miff
magick optimized.gif -coalesce optimized.miff
magick compare -metric AE original.miff optimized.miff null:
```

For lossy palette changes, use an appropriate metric and inspect flicker visually.

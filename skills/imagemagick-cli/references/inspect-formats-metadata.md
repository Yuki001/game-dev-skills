# Inspection, formats, and metadata

## Contents

- [Fast and verbose inspection](#fast-and-verbose-inspection)
- [Percent escapes](#percent-escapes)
- [Profiles, properties, artifacts, and options](#profiles-properties-artifacts-and-options)
- [Format discovery and prefixes](#format-discovery-and-prefixes)
- [Multi-image reads and writes](#multi-image-reads-and-writes)
- [JPEG](#jpeg)
- [PNG](#png)
- [GIF and animations](#gif-and-animations)
- [TIFF and multi-page files](#tiff-and-multi-page-files)
- [WebP, AVIF, HEIC, and JPEG XL](#webp-avif-heic-and-jpeg-xl)
- [PDF, PostScript, and SVG](#pdf-postscript-and-svg)
- [NetPBM, BMP, ICO, PSD, DPX, and camera raw](#netpbm-bmp-ico-psd-dpx-and-camera-raw)
- [Raw pixels](#raw-pixels)
- [Delegates, encrypted images, and large streams](#delegates-encrypted-images-and-large-streams)
- [Metadata policies](#metadata-policies)

## Fast and verbose inspection

Basic:

```bash
magick identify input.png
magick identify input1.jpg input2.webp
```

Avoid full decoding when dimensions and header metadata suffice:

```bash
magick identify -ping input.jpg
magick identify -ping -format '%f %m %wx%h %b\n' *.jpg
```

Full detail:

```bash
magick identify -verbose input.tif
magick input.png -verbose info:
```

Scene/frame inventory:

```bash
magick identify -format '%s %m %wx%h page=%[page] delay=%T dispose=%D\n' animation.gif
magick identify -format '%s %wx%h\n' document.tif
```

Common automation record:

```bash
magick identify -format '%i|%s|%m|%w|%h|%z|%[colorspace]|%[channels]|%[orientation]|%b\n' input
```

Use a separator that cannot occur in filenames, or emit JSON-compatible strings with appropriate escaping in the calling shell.

## Percent escapes

Frequently used short forms:

| Escape | Meaning |
|---|---|
| `%f` | filename without directory |
| `%d` | directory |
| `%e` | extension |
| `%m` | format/magick |
| `%w`, `%h` | width, height |
| `%z` | depth |
| `%b` | file/blob size |
| `%n` | image count |
| `%p` | page/scene number |
| `%s` | scene number |
| `%T` | animation delay |
| `%D` | disposal |
| `%x`, `%y` | resolution |
| `%[page]` | virtual canvas geometry |
| `%[channels]` | channel layout |
| `%[colorspace]` | colorspace |
| `%[orientation]` | orientation |
| `%[pixel:p{x,y}]` | pixel value |

Calculated expressions:

```bash
magick input.png -format '%[fx:w*h]\n' info:
magick input.png -format '%[fx:w/h]\n' info:
magick xc: -format '%[fx:sin(pi/4)]\n' info:
```

Properties and wildcard listings:

```bash
magick input.jpg -format '%[EXIF:*]' info:
magick input.png -format '%[*]' info:
magick input.png -format '%[artifact:*]' info:
magick input.png -format '%[option:*]' info:
```

PowerShell uses the same percent escapes; unlike cmd batch files it does not require doubling `%`.

## Profiles, properties, artifacts, and options

Profiles are binary blocks such as ICC, EXIF, IPTC, and XMP. Properties are attached textual image attributes. Artifacts/options control operations and coders.

List profiles:

```bash
magick identify -verbose photo.jpg
magick photo.jpg -format '%[profiles]\n' info:
```

Extract or apply profiles:

```bash
magick photo.jpg profile:exif exif.bin
magick photo.jpg profile:icc display.icc
magick input.tif -profile source.icc -profile sRGB.icc output.jpg
```

Remove metadata:

```bash
magick input.jpg -strip output.jpg
magick input.jpg +profile exif +profile xmp output.jpg
magick input.jpg +comment output.jpg
```

`-strip` removes profiles and comments broadly; it may remove color-management data. Use selective removal when color fidelity matters.

Set and delete properties:

```bash
magick input.jpg -set comment 'Generated preview' output.jpg
magick input.jpg -set label '%f' labeled.miff
magick input.jpg -delete 0 null:
```

EXIF orientation:

```bash
magick identify -format '%[EXIF:Orientation]\n' photo.jpg
magick photo.jpg -auto-orient oriented.jpg
```

Run `-auto-orient` before crop placement. It updates pixels and normally resets the orientation tag.

## Format discovery and prefixes

```bash
magick identify -list format
magick identify -list mime
magick identify -list magic
```

Explicit input/output coders:

```bash
magick JPEG:input.bin PNG:output.bin
magick input.png PNG32:rgba.png
magick input.png PNG24:rgb.png
magick input.png PNG8:indexed.png
magick input.tif 'JPEG:frame-%03d.jpg'
```

Check that a format is writable and that a delegate is available. Installed support varies for HEIC, AVIF, JPEG XL, PDF/PS, RAW camera formats, video, and fonts.

## Multi-image reads and writes

Select scenes/pages in the filename:

```bash
magick 'document.tif[0]' first-page.png
magick 'animation.gif[2-7]' selected.miff
```

Write one file per scene with an explicit number:

```bash
magick document.tif 'page-%04d.png'
```

Set the starting scene:

```bash
magick document.tif -scene 1 'page-%04d.png'
```

Formats such as GIF, TIFF, PDF, MIFF, and WebP may adjoin multiple images into one file:

```bash
magick page-*.png -adjoin document.tif
magick page-*.png +adjoin 'page-%03d.tif'
```

Whether a coder supports adjoining is format/build dependent. Verify scene count after writing:

```bash
magick identify -format '%s %n %wx%h\n' output.tif
```

Use `-write` to emit an intermediate while continuing:

```bash
magick input.png -resize 50% -write preview.png -blur 0x2 final.png
```

Filename percent escapes and shell percent expansion are separate systems. Quote brackets/globs and double `%` in Windows batch files.

## JPEG

JPEG is lossy and does not store alpha.

```bash
magick input.png -background white -alpha remove -alpha off -quality 88 output.jpg
```

Control chroma subsampling:

```bash
magick input.png -sampling-factor 4:4:4 -quality 90 output.jpg
magick input.png -sampling-factor 4:2:0 -quality 85 output.jpg
```

Optimize decoding for thumbnails by placing the hint before the input:

```bash
magick -define jpeg:size=800x800 large.jpg -auto-orient -thumbnail '400x400>' thumb.jpg
```

Progressive/interlace:

```bash
magick input.jpg -interlace Plane -quality 88 progressive.jpg
```

Preserve or remove profiles deliberately:

```bash
magick input.jpg -auto-orient -resize '1600x1600>' -quality 88 output.jpg
magick input.jpg -auto-orient -resize '1600x1600>' -strip -quality 88 output-small.jpg
```

Do not judge JPEG quality by the numeric setting alone; encoder version, subsampling, colorspace, and image content matter.

## PNG

Choose a type explicitly when size or alpha behavior matters:

```bash
magick input.png PNG24:opaque-rgb.png
magick input.png PNG32:rgba.png
magick input.png -colors 256 PNG8:indexed.png
```

Compression controls trade time for size without changing pixels:

```bash
magick input.png -define png:compression-level=9 output.png
magick input.png -define png:compression-filter=5 \
  -define png:compression-strategy=1 output.png
```

Chunk controls:

```bash
magick input.png -define png:exclude-chunk='EXIF,iCCP,iTXt,tEXt,zTXt,date' output.png
magick input.png -define png:include-chunk='gAMA,sRGB' output.png
```

Prefer selective chunk handling to `-strip` when gamma/ICC behavior is important.

Binary transparency:

```bash
magick input.png -alpha extract mask.png
magick input.png -channel A -threshold 50% +channel binary-alpha.png
```

## GIF and animations

GIF supports indexed color and binary transparency; partial alpha is quantized.

Single image:

```bash
magick input.png -channel A -threshold 50% +channel -colors 256 output.gif
```

Animation information:

```bash
magick identify -format '%s delay=%T dispose=%D page=%[page]\n' animation.gif
```

Split frames:

```bash
magick animation.gif -coalesce 'frame-%03d.png'
```

Assemble:

```bash
magick -delay 8 -loop 0 frame-*.png -layers Optimize animation.gif
```

See `animation-montage-compare.md` before editing optimized frames.

## TIFF and multi-page files

Inspect pages:

```bash
magick identify multipage.tif
magick 'multipage.tif[0]' first.png
magick 'multipage.tif[0-4]' 'page-%02d.png'
```

Create multi-page TIFF:

```bash
magick page-*.png -compress LZW multipage.tif
magick page-*.png -compress Zip multipage.tif
magick page-*.jpg -compress JPEG -quality 90 multipage.tif
```

Control photometric/type deliberately for bilevel or grayscale documents:

```bash
magick scan.png -colorspace Gray -threshold 60% -type bilevel \
  -compress Group4 fax.tif
```

Check whether the intended TIFF compression is available and suitable for the bit depth.

## WebP, AVIF, HEIC, and JPEG XL

Confirm installed coders first:

```bash
magick identify -list format | grep -Ei 'WEBP|AVIF|HEIC|JXL'
```

WebP:

```bash
magick input.png -quality 82 output.webp
magick input.png -define webp:lossless=true output-lossless.webp
magick input.png -define webp:method=6 -quality 82 output.webp
```

AVIF/HEIC:

```bash
magick input.png -quality 55 output.avif
magick input.png -quality 70 output.heic
```

Options and quality interpretation depend on the installed delegate. Inspect output format, depth, colorspace, alpha, and profiles; do not assume parity across builds.

Animated WebP/AVIF support may differ. Verify scene count after writing:

```bash
magick identify -format '%n\n' output.webp | head -n 1
```

## PDF, PostScript, and SVG

ImageMagick rasterizes these inputs. Place density before input:

```bash
magick -density 300 'document.pdf[0]' -background white -alpha remove page.png
magick -density 192 icon.svg -background none icon.png
```

Downsample after a higher-density rasterization when antialiasing matters:

```bash
magick -density 600 diagram.svg -background white -alpha remove \
  -resize 25% -strip diagram.png
```

Write PDF:

```bash
magick page-*.png -units PixelsPerInch -density 300 output.pdf
```

This embeds raster pages; it does not recreate vector content or searchable text.

Common failures:

- `not authorized`: security policy denies the coder/delegate.
- delegate missing: Ghostscript, librsvg, or another delegate is unavailable.
- wrong dimensions: density was placed after the input or physical units were misunderstood.
- dark/transparent background: remove alpha against an explicit background for PDF/JPEG-like outputs.

Do not weaken system policy without explicit authority. Explain which capability is blocked.

## NetPBM, BMP, ICO, PSD, DPX, and camera raw

NetPBM formats are useful as simple interoperable streams:

```bash
magick input.png -depth 8 PPM:output.ppm
magick input.png -colorspace Gray -depth 16 PGM:output.pgm
magick input.png -alpha on -depth 8 PAM:output.pam
```

PBM is bilevel, PGM is grayscale, PPM is RGB, and PAM can carry richer channel layouts. Record depth and max value when another program consumes the result.

Windows icons normally contain several scenes:

```bash
magick input.png -define icon:auto-resize=256,128,64,48,32,16 favicon.ico
magick identify favicon.ico
```

BMP variants differ in header version, palette, bit fields, and alpha support. Set the intended subtype/format with `bmp:` defines and verify with the target application; “BMP” alone is not a compatibility guarantee.

PSD commonly exposes a composite preview plus layer scenes:

```bash
magick identify input.psd
magick input.psd 'psd-scene-%02d.png'
```

Scene 0 is often the flattened composite, but inspect names/counts rather than hard-coding it. ImageMagick is useful for raster layer extraction and simple PSD writing; it does not preserve every Photoshop feature.

DPX is high-depth motion-picture interchange. Preserve depth, colorspace, endian, orientation, and timecode-related properties deliberately:

```bash
magick identify -verbose frame.dpx
magick frame.dpx -depth 16 -colorspace RGB frame.tif
```

Camera raw formats normally require a delegate such as LibRaw/dcraw:

```bash
magick identify -list format | grep -Ei 'DNG|CR2|CR3|NEF|ARW|RAF'
magick input.dng -auto-orient -colorspace sRGB output.tif
```

Raw development choices—white balance, demosaic, exposure, highlight recovery, camera profile—can differ across delegates. Use a dedicated raw developer when those controls matter.

## Raw pixels

Raw formats have no header. Supply dimensions, depth, colorspace, and layout before input:

```bash
magick -size 1920x1080 -depth 8 rgb:frame.raw frame.png
magick -size 640x480 -depth 16 -endian LSB gray:scan.raw scan.tif
magick -size 512x512 -depth 8 rgba:frame.raw frame.png
```

Export:

```bash
magick input.png -depth 8 rgb:frame.raw
magick input.png -alpha on -depth 8 rgba:frame.raw
```

Use `magick stream` for regions or row-wise raw export from very large files:

```bash
magick stream -map rgb -storage-type char input.tif pixels.dat
magick stream -map i -storage-type double -extract 100x100+30+40 input.tif region.raw
```

Record byte order, channel order, storage type, depth, and dimensions alongside raw output.

## Delegates, encrypted images, and large streams

Inspect delegate mappings:

```bash
magick -list delegate
magick -debug coder input.pdf null:
```

Delegates may spawn Ghostscript, FFmpeg, browser/rendering engines, or raw decoders. A direct ImageMagick format conversion can therefore execute an external program and inherit its limits and security posture.

ImageMagick can encipher pixel data using a passphrase file:

```bash
magick input.png -encipher passphrase.txt encrypted.png
magick encrypted.png -decipher passphrase.txt restored.png
```

Keep the passphrase file private and out of logs. Verify a round trip with a lossless format; lossy re-encoding or pixel modification destroys reversibility. This is not a replacement for authenticated file encryption, because metadata/container details may remain visible and tampering may not be detected.

For long image sequences, use MIFF streams where possible:

```bash
producer | magick miff:- -resize 50% miff:- | consumer
```

For massive images, prefer read-time regions, `magick stream`, tiled processing with overlap for neighbourhood filters, or a large-image tool such as libvips. Tiling blur/convolution without halo overlap creates seams. The overlap must cover the operator support radius, and final tiles must discard that halo before assembly.

## Metadata policies

Choose one deliberately:

- **Preserve:** omit `-strip`; verify ICC/EXIF/XMP survival.
- **Privacy:** remove EXIF, XMP, comments, and thumbnails; decide whether to retain ICC.
- **Web-minimal:** keep only color-critical chunks/profile; normalize orientation into pixels.
- **Archival:** avoid lossy recompression; preserve depth, colorspace, profiles, page/frame metadata, and provenance.

Privacy-oriented example retaining ICC:

```bash
magick input.jpg -auto-orient +profile exif +profile xmp +comment output.jpg
```

Check exact profile names with `identify -verbose`; wildcard profile removal can be broader than intended.

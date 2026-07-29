# CLI foundations

## Contents

- [Discover the installation](#discover-the-installation)
- [Sequential evaluation](#sequential-evaluation)
- [Settings, operators, and stacks](#settings-operators-and-stacks)
- [Geometry grammar](#geometry-grammar)
- [Inputs and outputs](#inputs-and-outputs)
- [Specialist subcommands](#specialist-subcommands)
- [Image lists and temporary registers](#image-lists-and-temporary-registers)
- [Shell quoting](#shell-quoting)
- [ImageMagick 6 to 7](#imagemagick-6-to-7)
- [Debugging checklist](#debugging-checklist)

## Discover the installation

```bash
magick -version
magick -list configure
magick -list policy
magick identify -list format
magick -list font
magick -list color
magick -list compose
magick -list morphology
```

`-version` reports quantum depth, HDRI, features, and delegates. Format listings use mode flags such as `r--`, `-w-`, or `rw+`; do not infer write support merely from a familiar extension.

On Windows:

```powershell
$magick = & "$PSScriptRoot\..\scripts\resolve-imagemagick.ps1"
& $magick -version
```

On Linux/macOS:

```bash
MAGICK="$(./scripts/resolve-imagemagick.sh)"
"$MAGICK" -version
```

## Sequential evaluation

ImageMagick 7 reads and applies arguments in order. A robust mental model is:

```text
read settings → read image(s) → image settings/operators → sequence operators → write settings → output
```

Correct:

```bash
magick input.jpg -resize 800x600 output.jpg
magick -density 300 input.pdf -background white -alpha remove page.png
magick -size 640x480 -depth 8 rgb:frame.raw frame.png
```

Risky or wrong:

```bash
# -density is too late to control PDF rasterization
magick input.pdf -density 300 page.png

# raw pixels need size/depth before they are read
magick rgb:frame.raw -size 640x480 frame.png
```

Multiple inputs form an image list:

```bash
magick first.png second.png +append side-by-side.png
magick frame-*.png -delay 8 -loop 0 animation.gif
```

Use a quoted glob when ImageMagick should expand it; use an unquoted glob when the shell should expand it. Shell expansion is usually easier to reason about, but ImageMagick scene patterns support file specifications the shell does not.

## Settings, operators, and stacks

Settings persist until changed:

```bash
magick input.png -gravity southeast -background none \
  -splice 20x20 -extent 1200x800 output.png
```

Operators act on the current list:

```bash
magick input.png -auto-orient -trim +repage -resize '1200x1200>' output.png
```

Parentheses isolate a nested image list and make multi-image pipelines readable:

```bash
magick background.png \
  \( overlay.png -resize 30% -alpha set \) \
  -gravity southeast -geometry +20+20 -compose over -composite output.png
```

PowerShell:

```powershell
& $magick "background.png" `
  "(" "overlay.png" -resize "30%" -alpha set ")" `
  -gravity southeast -geometry "+20+20" -compose over -composite "output.png"
```

Frequent list operators:

```bash
-clone 0          # clone scene 0
+clone            # clone the current/last image
-duplicate 3      # add three more copies
-delete 0         # remove scene 0
-swap 0,1         # exchange two scenes
+swap             # swap the last two
-insert 0         # move current image to index 0
-reverse          # reverse list order
-append           # vertical append
+append           # horizontal append
-flatten          # composite list on a fixed canvas
-mosaic           # compose while expanding to positive extents
-layers merge     # merge layers and choose a new canvas
```

Reset a persistent setting where ambiguity matters:

```bash
magick input.png -channel RGB -auto-level +channel output.png
```

## Geometry grammar

Geometry is a compact mini-language:

```text
WIDTHxHEIGHT+X+Y
WIDTHxHEIGHT
xHEIGHT
WIDTHx
PERCENT%
PIXELCOUNT@
```

Resize modifiers:

| Modifier | Meaning |
|---|---|
| none | fit inside the box, preserve aspect ratio |
| `!` | force exact width and height |
| `>` | shrink only |
| `<` | enlarge only |
| `^` | fill the box; one dimension may exceed it |
| `%` | scale by percentage |
| `@` | limit total pixel area |

```bash
magick in.jpg -resize 800x600 out.jpg
magick in.jpg -resize '800x600>' out.jpg
magick in.jpg -resize '800x600^' -gravity center -extent 800x600 out.jpg
magick in.png -resize '64x64!' stretched.png
magick in.jpg -resize '2MP@' limited.jpg
magick in.png -resize 50% half.png
```

Offsets can be negative and are interpreted with `-gravity` for many placement operators:

```bash
magick in.png -gravity southeast -crop 400x300+25+25 +repage crop.png
```

An exclamation mark can also modify crop/extent semantics in some options; consult `options-index.md` rather than generalizing from resize.

## Inputs and outputs

Explicit format prefixes override extension or signature inference:

```bash
magick -size 640x480 -depth 8 rgb:frame.raw frame.png
magick input.dat PNG:output.bin
magick input.png PNG32:rgba.png
magick input.png PNG24:opaque.png
magick input.png PNG8:indexed.png
```

Scene selection and read-time cropping use filename suffixes:

```bash
magick 'document.pdf[0]' first-page.png
magick 'animation.gif[0-9]' selected.miff
magick 'large.tif[800x600+100+200]' region.png
```

Quote brackets to prevent shell glob interpretation.

Built-in and pseudo-images:

```bash
magick logo: logo.png
magick rose: rose.png
magick -size 640x480 xc:'#20242b' canvas.png
magick -size 640x480 gradient:'#111-#777' gradient.png
magick -size 640x480 radial-gradient:white-black radial.png
magick -size 256x256 pattern:checkerboard pattern.png
magick -size 600x100 -background none -fill white label:'Hello' label.png
magick -size 600x -background none -fill white caption:'Wrapped text' caption.png
```

Standard streams:

```bash
producer | magick png:- -resize 50% png:- | consumer
magick input.png miff:- | magick - -blur 0x2 output.png
magick input.png info:
magick input.png txt:-
```

Prefer MIFF between ImageMagick processes because it preserves image attributes and sequences. A raw `png:-` stream represents one PNG image, not an arbitrary in-memory list.

Use `null:` as a sink:

```bash
magick input.png -format '%w %h\n' info:
magick compare -metric RMSE a.png b.png null:
```

## Specialist subcommands

ImageMagick 7 keeps several specialist tools behind `magick`:

| Form | Purpose |
|---|---|
| `magick identify` | inspect image metadata/scenes |
| `magick mogrify` | apply one pipeline to files, destructive by default |
| `magick montage` | build labeled thumbnail grids |
| `magick compare` | metrics and difference images |
| `magick composite` | legacy/simple two-image composition |
| `magick stream` | export regions/channels without ordinary image output |
| `magick display` | X11 image viewer where available |
| `magick animate` | X11 animation viewer where available |
| `magick import` | X11 screen capture where available |
| `magick conjure` | run MSL scripts where enabled |

Prefer the general `magick input ... output` form for stacks and multi-stage pipelines. `display`, `animate`, and `import` require a graphical/X11 environment and are not portable Windows/macOS screenshot APIs. MSL/MVG/SVG are active parsing formats; do not run untrusted scripts.

Examples:

```bash
magick display input.png
magick animate animation.gif
magick import -window root screenshot.png
magick conjure workflow.msl
```

Confirm that the subcommand exists and that policy permits its coders/actions. In headless automation, write an output and inspect it rather than relying on a viewer.

## Image lists and temporary registers

Write an intermediate without ending the pipeline:

```bash
magick input.png -resize 1200x1200 -write preview.png -blur 0x2 final.png
```

`-write` keeps the image in the list. `+write` restores the image state after writing for option forms that support it; verify exact behavior when relying on it.

Named in-memory images avoid temporary files:

```bash
magick input.png -resize 25% -write mpr:small +delete \
  -size 1200x800 xc:white mpr:small \
  -gravity center -compose over -composite output.png
```

Use `mpr:` within one process only. It is not a filesystem cache and cannot be shared across separate commands.

Use `-respect-parentheses` when stack-local settings must be restored on exit:

```bash
magick -respect-parentheses base.png \
  \( overlay.png -gravity center -resize 25% \) \
  -gravity southeast -composite out.png
```

Prefer explicit settings even with this option; it makes copied snippets safer.

## Shell quoting

### Bash/zsh

- Escape stack parentheses as `\(` and `\)`.
- Quote geometry containing `<`, `>`, `!`, `^`, `%`, `*`, or brackets.
- Single-quote `-fx`, `-draw`, and percent-escape expressions unless shell variables are deliberately interpolated.
- Use `--` only for tools/options that document it; ImageMagick filename handling is richer than a conventional Unix parser.

```bash
magick 'input [final].png' -resize '800x800>' -format '%[pixel:p{0,0}]' info:
```

### PowerShell

- Invoke a resolved path with `&`.
- Quote literal `(` and `)` arguments.
- Single-quote percent escapes and `-fx` expressions when no PowerShell interpolation is desired.
- Pass arguments as an array for generated commands.

```powershell
$args = @(
  "input [final].png",
  "-resize", "800x800>",
  "-format", "%[pixel:p{0,0}]",
  "info:"
)
& $magick @args
```

### cmd.exe

- Use `^` for line continuation.
- Double `%` in `.bat`/`.cmd` files.
- Escape shell metacharacters separately from ImageMagick geometry.
- Prefer a response/script file or PowerShell for complex stacks.

## ImageMagick 6 to 7

Common rewrites:

```text
convert in.png -resize 50% out.png
→ magick in.png -resize 50% out.png

identify -verbose in.png
→ magick identify -verbose in.png

montage *.png -geometry +4+4 out.png
→ magick montage *.png -geometry +4+4 out.png

compare -metric RMSE a.png b.png diff.png
→ magick compare -metric RMSE a.png b.png diff.png
```

Important behavioral differences:

- IM7 has strict sequential parsing; place each operator after its input.
- IM7 uses `magick` and subcommands; do not invoke Windows `convert.exe`.
- IM7 uses a channel-aware pixel model and defaults can differ for alpha/channels.
- Several options were renamed, deprecated, or removed. Search `options-index.md` and confirm with the installed `magick` help.
- `magick` without a subcommand replaces most `convert` workflows, but specialist tools retain subcommand grammar.

Do not mechanically port a command that relies on old mask, alpha, channel, or colorspace behavior without a small test image.

## Debugging checklist

1. Reduce to one input and one output.
2. Print the exact executable with `magick -version`.
3. Inspect input with `identify -verbose`.
4. Confirm option order and shell quoting.
5. Confirm format read/write flags and delegates.
6. Confirm policy rights.
7. Add `-regard-warnings` if warnings matter.
8. Use `-debug coder`, `-debug cache`, `-debug configure`, or `-debug all` only after narrowing the issue.
9. Add `-define registry:temporary-path=...` or resource limits only with an explicit writable directory.
10. Verify the output with `identify`, not just its existence.

Useful diagnostics:

```bash
magick -debug configure input.png null:
magick -debug coder input.pdf null:
magick -limit memory 256MiB -limit map 512MiB -limit disk 2GiB input.tif null:
magick input.png -regard-warnings output.png
```

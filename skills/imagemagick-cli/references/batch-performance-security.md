# Batch processing, performance, and security

## Contents

- [Safe batch principles](#safe-batch-principles)
- [PowerShell patterns](#powershell-patterns)
- [Bash patterns](#bash-patterns)
- [cmd.exe and VBScript legacy patterns](#cmdexe-and-vbscript-legacy-patterns)
- [Mogrify](#mogrify)
- [Filename and output design](#filename-and-output-design)
- [Resource limits and pixel cache](#resource-limits-and-pixel-cache)
- [Concurrency](#concurrency)
- [Delegates, policy, and untrusted input](#delegates-policy-and-untrusted-input)
- [Temporary files and cleanup](#temporary-files-and-cleanup)
- [Failure handling and manifests](#failure-handling-and-manifests)

## Safe batch principles

1. Enumerate an exact input directory and allowed extensions.
2. Put outputs in a separate directory.
3. Exclude the output directory from future enumeration.
4. Preserve the relative directory structure when duplicate basenames are possible.
5. Use a distinct temporary output and atomically move it only after verification when replacing originals.
6. Capture exit code and stderr per file.
7. Continue or stop according to the user’s error policy.
8. Compare input/output counts and inspect a representative sample.
9. Avoid shell-generated command strings; pass argument arrays.
10. Limit resources for large or untrusted files.

Dry-run first by printing resolved input/output pairs. Do not create an accidental recursive conversion loop.

## PowerShell patterns

Resolve executable:

```powershell
$magick = (Get-Command magick -ErrorAction Stop).Source
```

Non-recursive conversion:

```powershell
$inputDir = (Resolve-Path -LiteralPath "E:\images").Path
$outputDir = "E:\images-output"
New-Item -ItemType Directory -Path $outputDir -Force | Out-Null

Get-ChildItem -LiteralPath $inputDir -File |
  Where-Object { $_.Extension -in ".jpg", ".jpeg", ".png" } |
  ForEach-Object {
    $output = Join-Path $outputDir ($_.BaseName + ".webp")
    & $magick $_.FullName -auto-orient -resize "1600x1600>" `
      -quality 82 $output
    if ($LASTEXITCODE -ne 0) {
      throw "ImageMagick failed for '$($_.FullName)'"
    }
  }
```

Recursive while preserving subdirectories:

```powershell
$inputDir = (Resolve-Path -LiteralPath "E:\images").Path
$outputDir = [IO.Path]::GetFullPath("E:\images-output")

Get-ChildItem -LiteralPath $inputDir -File -Recurse |
  Where-Object { $_.Extension -in ".jpg", ".jpeg", ".png" } |
  ForEach-Object {
    $relative = [IO.Path]::GetRelativePath($inputDir, $_.FullName)
    $relativeOut = [IO.Path]::ChangeExtension($relative, ".webp")
    $output = Join-Path $outputDir $relativeOut
    $parent = Split-Path -Parent $output
    New-Item -ItemType Directory -Path $parent -Force | Out-Null
    & $magick $_.FullName -auto-orient -resize "1600x1600>" `
      -quality 82 $output
    if ($LASTEXITCODE -ne 0) {
      Write-Error "Failed: $($_.FullName)"
    }
  }
```

Conditional by dimensions:

```powershell
Get-ChildItem -LiteralPath $inputDir -File | ForEach-Object {
  $dimensions = & $magick identify -ping -format "%w,%h" $_.FullName
  if ($LASTEXITCODE -ne 0) { return }
  $width, $height = $dimensions -split ","
  if ([int]$width -gt 2000 -or [int]$height -gt 2000) {
    & $magick $_.FullName -resize "2000x2000>" (Join-Path $outputDir $_.Name)
  }
}
```

Argument array:

```powershell
$args = @(
  $_.FullName,
  "-auto-orient",
  "-resize", "1600x1600>",
  "-quality", "82",
  $output
)
& $magick @args
```

Never interpolate untrusted paths into `Invoke-Expression`.

## Bash patterns

Null-delimited safe loop:

```bash
input_dir=/data/images
output_dir=/data/images-output
mkdir -p "$output_dir"

find "$input_dir" -maxdepth 1 -type f \
  \( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' \) -print0 |
while IFS= read -r -d '' input; do
  name=$(basename "$input")
  stem=${name%.*}
  output="$output_dir/$stem.webp"
  if ! magick "$input" -auto-orient -resize '1600x1600>' \
      -quality 82 "$output"; then
    printf 'failed: %s\n' "$input" >&2
  fi
done
```

Recursive structure:

```bash
find "$input_dir" -type f -print0 |
while IFS= read -r -d '' input; do
  case ${input##*.} in
    jpg|JPG|jpeg|JPEG|png|PNG) ;;
    *) continue ;;
  esac
  relative=${input#"$input_dir"/}
  output="$output_dir/${relative%.*}.webp"
  mkdir -p "$(dirname "$output")"
  magick "$input" -auto-orient -resize '1600x1600>' -quality 82 "$output"
done
```

Conditional:

```bash
dimensions=$(magick identify -ping -format '%w %h' "$input") || continue
read -r width height <<EOF
$dimensions
EOF
if [ "$width" -gt 2000 ] || [ "$height" -gt 2000 ]; then
  magick "$input" -resize '2000x2000>' "$output"
fi
```

Avoid `for f in $(find ...)`; it breaks whitespace and newlines.

## cmd.exe and VBScript legacy patterns

Prefer PowerShell for new Windows automation, but maintain existing batch files with correct quoting and doubled percent signs:

```bat
@echo off
if not exist "output" mkdir "output"
for %%F in ("input\*.png") do (
  magick "%%~fF" -resize "1600x1600>" "output\%%~nF.webp"
  if errorlevel 1 exit /b 1
)
```

At an interactive `cmd.exe` prompt, use `%F`; inside `.bat`/`.cmd`, use `%%F`. `%~fF`, `%~nF`, and `%~xF` expand full path, stem, and extension. ImageMagick percent escapes such as `%w` also need doubling in a batch file when cmd would interpret them.

Avoid delayed expansion when filenames can contain `!`. Do not build one command string from untrusted filenames; quote each expansion at the point of use.

VBScript can call ImageMagick through `WScript.Shell.Exec` when a legacy host requires it:

```vbscript
Function Q(s)
  Q = Chr(34) & Replace(s, Chr(34), Chr(34) & Chr(34)) & Chr(34)
End Function

Set shell = CreateObject("WScript.Shell")
cmd = "magick " & Q(inputPath) & " -resize " & Q("1600x1600>") & " " & Q(outputPath)
Set process = shell.Exec(cmd)
stderrText = process.StdErr.ReadAll
exitCode = process.ExitCode
If exitCode <> 0 Then WScript.Echo stderrText
```

`Exec` still receives a command line string, so robust quoting is essential and user-controlled option fragments must not be concatenated. Prefer passing only validated paths and fixed options. Capture stdout/stderr before interpreting the exit code.

## Mogrify

`mogrify` changes files in place by default:

```bash
magick mogrify -resize '1600x1600>' *.jpg
```

Safer output directory:

```bash
mkdir -p output
magick mogrify -path output -format webp \
  -auto-orient -resize '1600x1600>' -quality 82 *.jpg
```

Thumbnail batch:

```bash
mkdir -p thumbs
magick mogrify -path thumbs -format jpg \
  -define jpeg:size=640x640 -thumbnail '320x320>' \
  -strip -quality 85 *.jpg
```

Limitations:

- One option pipeline applies to every input.
- Complex list operations/compositing are often clearer in a shell loop.
- Filename collisions can occur when formats change.
- In-place failure can leave a partially rewritten file depending on coder/path behavior.

Use per-file `magick` commands when custom output names, logging, conditional logic, or transactional replacement matter.

## Filename and output design

Format conversion with same basenames can collide:

```text
folder/a.jpg
folder/a.png
→ output/a.webp
```

Resolve with extension suffixes or directory preservation:

```text
output/a-jpg.webp
output/a-png.webp
```

Scene numbers:

```bash
magick document.tif 'page-%04d.png'
```

Input filename in output names is not automatically sanitized:

```bash
magick input.tif -set filename:base '%[basename]' \
  'out/%[filename:base]-%03d.png'
```

Test percent escapes and output naming with a small sample. Shells and ImageMagick may each expand `%`, brackets, and globs.

Atomic replacement pattern:

1. Write `file.ext.im-tmp.ext` in the same filesystem.
2. Verify format, dimensions, and nonzero size.
3. Move original to a recoverable backup or replace only with explicit authorization.
4. Remove backup only after user-defined retention.

Do not use a temporary extension that changes coder selection unless an explicit format prefix is used.

## Resource limits and pixel cache

Command-level limits:

```bash
magick -limit memory 256MiB -limit map 512MiB \
  -limit disk 4GiB -limit time 120 \
  input.tif -resize '4000x4000>' output.jpg
```

Useful resources:

```text
width height area memory map disk file thread time throttle
```

Inspect:

```bash
magick -list resource
magick -list policy
```

The pixel cache may move from heap memory to mapped memory to disk. “Memory limit” alone is not a full safety bound; set area, map, disk, and time as appropriate.

Pixel-area guard:

```bash
magick -limit area 100MP input.png null:
```

Large dimensions can be dangerous even when a compressed input is small. Inspect header dimensions with `identify -ping`, but remember malformed files can still fail during decode.

Temporary path:

```bash
magick -define registry:temporary-path=/data/im-tmp input.tif output.png
```

Use an existing, private, writable directory with adequate space.

## Concurrency

ImageMagick may already use OpenMP threads:

```bash
magick -limit thread 4 input.png output.png
```

Running many multi-threaded processes can oversubscribe CPU and memory. Choose either:

- few processes with several threads each, or
- many processes with `-limit thread 1`.

Bash with bounded jobs:

```bash
find input -type f -name '*.png' -print0 |
  xargs -0 -n1 -P4 sh -c '
    input=$1
    output="output/$(basename "$input")"
    magick -limit thread 1 "$input" -resize "1600x1600>" "$output"
  ' sh
```

Ensure output names are collision-free and aggregate failures; `xargs -P` output can interleave.

PowerShell 7:

```powershell
$files | ForEach-Object -Parallel {
  & $using:magick -limit thread 1 $_.FullName -resize "1600x1600>" $output
} -ThrottleLimit 4
```

Construct `$output` inside the parallel block from immutable input/output roots.

## Delegates, policy, and untrusted input

ImageMagick may invoke delegates for PDF/PS, SVG, fonts, HEIF/AVIF, video, raw camera files, and more.

Inspect:

```bash
magick -version
magick -list configure
magick -list delegate
magick -list policy
```

Security policy can restrict:

- coder read/write rights,
- delegates,
- modules,
- paths,
- URL protocols,
- indirect reads,
- resource limits.

Do not bypass a policy error by weakening global policy unless the user explicitly owns and authorizes that environment change. Prefer an allowed format, trusted preprocessing tool, or administrator change.

Untrusted-input rules:

1. Allowlist formats and actual magic signatures.
2. Deny URL/protocol reads unless required.
3. Avoid MVG/MSL/SVG from untrusted sources.
4. Set width, height, area, time, memory, map, disk, and file limits.
5. Use a nonprivileged account and isolated temporary directory.
6. Keep ImageMagick and delegates patched.
7. Avoid expanding attacker-controlled strings into filenames, `-draw`, `-fx`, or `@file`.
8. Store outputs outside web-executable paths.

Explicit format allowlist example belongs in `policy.xml`, not in a per-command snippet:

```xml
<policy domain="module" rights="none" pattern="*" />
<policy domain="module" rights="read | write" pattern="{GIF,JPEG,PNG,WEBP}" />
```

Policy syntax and installation paths are version/platform specific; inspect `magick -list policy`, `magick -list configure`, and the configuration files installed with that ImageMagick build.

## Temporary files and cleanup

Prefer a task-scoped temporary directory:

PowerShell:

```powershell
$taskTemp = Join-Path ([IO.Path]::GetTempPath()) ("im-" + [guid]::NewGuid())
New-Item -ItemType Directory -Path $taskTemp | Out-Null
try {
  & $magick -define "registry:temporary-path=$taskTemp" "input.tif" "output.png"
  if ($LASTEXITCODE -ne 0) { throw "ImageMagick failed" }
}
finally {
  Remove-Item -LiteralPath $taskTemp -Recurse -Force -ErrorAction SilentlyContinue
}
```

Bash:

```bash
task_tmp=$(mktemp -d)
trap 'rm -rf -- "$task_tmp"' EXIT HUP INT TERM
magick -define "registry:temporary-path=$task_tmp" input.tif output.png
```

Validate the exact path before recursive cleanup. Do not use a broad environment variable as a deletion target.

## Failure handling and manifests

Capture:

```text
input path
output path
start/end time
exit code
stderr summary
input format/dimensions
output format/dimensions
command/version
```

PowerShell record:

```powershell
$stderr = & $magick @args 2>&1
$record = [pscustomobject]@{
  Input = $_.FullName
  Output = $output
  ExitCode = $LASTEXITCODE
  Message = ($stderr -join "`n")
}
```

Bash:

```bash
if message=$(magick "$input" -resize '1600x1600>' "$output" 2>&1); then
  printf 'ok\t%s\t%s\n' "$input" "$output"
else
  status=$?
  printf 'failed\t%s\t%s\t%s\n' "$status" "$input" "$message" >&2
fi
```

After the batch:

```bash
magick identify -format '%f|%m|%wx%h|%b\n' output/*
```

Compare counts only after accounting for multi-page inputs and filtered/skipped files.

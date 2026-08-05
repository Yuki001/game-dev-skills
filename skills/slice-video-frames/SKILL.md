---
name: slice-video-frames
description: Extract ordered still-image frames from local video files with FFmpeg, using a fixed FPS, an exact frame count, explicit timestamps, or every source frame; optionally remove a flat chroma-key background and emit timing metadata. Use for video-to-frame conversion, animation frame sampling, contact-sheet inputs, sprite animation source frames, dataset frames, thumbnail sequences, or any request to split MP4, WebM, MOV, MKV, AVI, or other FFmpeg-readable video into PNG, WebP, or JPEG images.
---

# Slice Video Frames

Use the bundled scripts for deterministic extraction and optional chroma-key cleanup. Do not add generation, sprite-sheet packing, motion evaluation, or engine-specific packaging to this skill.

## Workflow

1. Inspect the source clip and confirm the usable time range.
2. Choose one sampling mode:
   - `--fps RATE` for evenly timed playback frames;
   - `--count N` for exactly N representative frames across a range;
   - `--timestamps LIST` for hand-selected source times;
   - `--every-frame` for every decoded source frame.
3. Extract into a new output directory. Keep the default PNG format when quality or alpha matters.
4. Use `--remove-background` only for a deliberately flat, solid chroma-key background.
5. Verify frame count, ordering, dimensions, timing, and alpha before returning the output paths and manifest.

Require the user to choose a sampling mode when intent does not imply one. Avoid `--every-frame` for long clips unless the user explicitly needs all source frames.

## Extract frames

```bash
python "$SKILL_DIR/scripts/slice_video_frames.py" input.mp4 frames/ --fps 12
python "$SKILL_DIR/scripts/slice_video_frames.py" input.mp4 frames/ --count 8 --start 0.4 --end 1.6
python "$SKILL_DIR/scripts/slice_video_frames.py" input.mp4 frames/ --timestamps 0.10,0.28,0.55,0.92
python "$SKILL_DIR/scripts/slice_video_frames.py" input.webm frames/ --every-frame
```

`--start` and `--end` accept seconds or `HH:MM:SS.mmm`. They apply to `--fps`, `--count`, and `--every-frame`. Explicit timestamps are absolute source times and cannot be combined with a range.

For `--count`, the default `--count-position centers` samples the center of each equal temporal bin and avoids fragile end-of-file seeks. Use `--count-position endpoints` only when the first and last usable poses must be represented.

`--count` and `--timestamps` resolve requested sample times to the nearest distinct decoded source frames. The manifest records the actual source timestamp for every output and also preserves the requested list for explicit timestamp sampling.

The script stages all frames before writing outputs, refuses to replace existing frames or manifests unless `--force` is passed, and writes `frames.json` by default. The manifest contains the source path, sampling mode, source timestamps, per-frame durations when derivable, canvas size, ordered paths, and alpha contract. Use `--manifest NAME.json` to rename it or `--no-manifest` to omit it.

Output controls:

- `--format png|webp|jpg` selects the image encoding; default `png`.
- `--prefix NAME` changes the default `frame_0000` naming prefix.
- `--digits N` changes numeric zero padding.
- `--ffmpeg-bin` and `--ffprobe-bin` select non-default binaries.
- `--force` authorizes replacement of colliding output files only; it does not clear the directory.

## Remove a flat background

For a chroma-keyed source clip, remove the matte during extraction:

```bash
python "$SKILL_DIR/scripts/slice_video_frames.py" keyed.mp4 frames/ \
  --fps 12 \
  --remove-background \
  --auto-key border \
  --edge-contract 1
```

This mode requires Pillow and PNG or WebP output. It uses a soft alpha matte, border sampling, and despill by default. Use `--key-color '#00ff00' --auto-key none` when the key color is known and the border is unreliable. Use `--edge-feather 0.25` only for visibly stair-stepped edges.

To process an already extracted frame independently:

```bash
python "$SKILL_DIR/scripts/remove_chroma_key.py" \
  --input frame_0000.png \
  --out frame_0000_alpha.png \
  --auto-key border \
  --soft-matte \
  --transparent-threshold 12 \
  --opaque-threshold 220 \
  --despill
```

Chroma-key removal is unsuitable when the subject shares the key color or has hair, fur, smoke, glass, liquids, translucency, reflections, soft shadows, or fine semi-transparent edges. Report the limitation instead of widening thresholds until subject detail disappears.

## Verification

Check:

- the script exits successfully and the manifest frame count matches the files;
- filenames sort in playback order;
- source timestamps fall within the requested range and durations are plausible;
- every frame opens and has the same intended dimensions;
- no frame is empty, clipped, corrupted, or an unintended duplicate;
- keyed outputs have alpha, transparent corners, intact interior detail, and no obvious key-color fringe.

When sampling motion for review, inspect both a contact sheet and playback at the manifest timing. Uniform sampling guarantees timing coverage, not good semantic pose selection; use explicit timestamps when particular motion phases matter.

## Requirements

- Python 3.9+.
- `ffmpeg` and `ffprobe` on `PATH`, or pass their paths explicitly.
- Pillow only when removing a background.

Do not install dependencies or overwrite existing outputs without user authorization.

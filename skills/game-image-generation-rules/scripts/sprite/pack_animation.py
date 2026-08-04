#!/usr/bin/env python3
"""Pack ordered sprite frames into an atlas and animation preview formats.

Frames are grouped into animation rows automatically: a sibling slice manifest
(slice.json) is preferred, then `_r{row}_c{col}` filename tags, else a single
animation. Each row becomes one band in the shared atlas, one frameTag in the
JSON, and one GIF/APNG preview.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


def _die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _dependency_hint(package: str) -> str:
    return (
        "Activate the repo-selected environment first, then install it with "
        f"`uv pip install {package}`. If this repo uses a local virtualenv, start with "
        "`source .venv/bin/activate`; otherwise use this repo's configured shared fallback "
        "environment."
    )


def _load_pillow() -> Any:
    try:
        from PIL import Image
    except ImportError:
        _die(f"Pillow is required for sprite animation packing. {_dependency_hint('pillow')}")
    return Image


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


ROWCOL_RE = re.compile(r"_r(\d+)_c(\d+)(?=[_.])")


def group_paths_by_row(paths: list[Path], manifest: dict[str, Any] | None) -> list[list[Path]]:
    """Group frames into animation rows.

    Row info comes from a slice manifest (preferred) when supplied, else from
    `_r{row}_c{col}` filename patterns. No row info anywhere yields a single
    group (current single-animation behavior). A partial match is an error.
    Returns rows ordered by row index, each row ordered by column index.
    """
    by_name = {path.name: path for path in paths}

    manifest_groups: dict[int, list[tuple[int, Path]]] = {}
    manifest_hits = 0
    if manifest:
        for entry in manifest.get("frames", []):
            row = entry.get("row")
            column = entry.get("column")
            output = entry.get("output")
            if row is None or column is None or not output:
                continue
            name = Path(output).name
            if name in by_name:
                manifest_groups.setdefault(int(row), []).append((int(column), by_name[name]))
                manifest_hits += 1

    if manifest_groups and manifest_hits == len(paths):
        return [
            [path for _col, path in sorted(manifest_groups[row], key=lambda item: item[0])]
            for row in sorted(manifest_groups)
        ]

    name_groups: dict[int, list[tuple[int, Path]]] = {}
    matched = 0
    for path in paths:
        match = ROWCOL_RE.search(path.name)
        if match:
            row, column = int(match.group(1)), int(match.group(2))
            name_groups.setdefault(row, []).append((column, path))
            matched += 1

    if matched == 0:
        return [list(paths)]
    if matched != len(paths):
        raise ValueError(
            "mixed row-tagged and untagged frame names; either every frame uses "
            "_r{row}_c{col} naming (or a slice manifest) or none do"
        )
    return [
        [path for _col, path in sorted(name_groups[row], key=lambda item: item[0])]
        for row in sorted(name_groups)
    ]


def find_slice_manifest(inputs: Iterable[str]) -> dict[str, Any] | None:
    """Locate a slice manifest (slice.json) beside the input frames, if any."""
    for raw in inputs:
        path = Path(raw)
        directory = path if path.is_dir() else path.parent
        for candidate in (directory / "slice.json", directory / "slice_manifest.json"):
            if candidate.is_file():
                try:
                    data = json.loads(candidate.read_text(encoding="utf-8"))
                except (OSError, ValueError):
                    continue
                if isinstance(data, dict) and "frames" in data:
                    return data
    return None


def pixel_data(image: Any) -> Any:
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter is not None else image.getdata()


def collect_paths(inputs: Iterable[str], pattern: str) -> list[Path]:
    paths: list[Path] = []
    for raw in inputs:
        path = Path(raw)
        if path.is_dir():
            paths.extend(candidate for candidate in path.glob(pattern) if candidate.is_file())
        elif path.is_file():
            paths.append(path)
        else:
            raise ValueError(f"input does not exist: {path}")
    unique = {path.resolve(): path for path in paths}
    return sorted(unique.values(), key=natural_key)


def parse_pair(value: str) -> tuple[float, float]:
    try:
        first, second = value.split(",", 1)
        return float(first), float(second)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected X,Y") from exc


def parse_durations(value: str) -> list[int]:
    try:
        durations = [int(item.strip()) for item in value.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("durations must be comma-separated integers") from exc
    if not durations or any(duration < 1 for duration in durations):
        raise argparse.ArgumentTypeError("durations must be positive milliseconds")
    return durations


def ensure_writable(paths: Iterable[Path | None], force: bool) -> None:
    for path in paths:
        if path is None:
            continue
        if path.exists() and not force:
            raise ValueError(f"output exists (use --force): {path}")
        path.parent.mkdir(parents=True, exist_ok=True)


def resolve_outputs(args: argparse.Namespace) -> None:
    if args.output_prefix:
        prefix = args.output_prefix
        args.atlas = args.atlas or prefix.with_name(prefix.name + "_atlas").with_suffix(".png")
        args.json = args.json or prefix.with_suffix(".json")
        args.gif = args.gif or prefix.with_suffix(".gif")
        args.apng = args.apng or prefix.with_suffix(".apng")
    if not any((args.atlas, args.json, args.gif, args.apng)):
        raise ValueError("choose at least one output or provide --output-prefix")


def normalize_frames(frames: list[Any], anchor: str, Image: Any) -> list[Any]:
    width = max(frame.width for frame in frames)
    height = max(frame.height for frame in frames)
    normalized: list[Any] = []
    for frame in frames:
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        if anchor == "center":
            x = (width - frame.width) // 2
            y = (height - frame.height) // 2
        elif anchor == "bottom-center":
            x = (width - frame.width) // 2
            y = height - frame.height
        else:
            x = 0
            y = 0
        canvas.alpha_composite(frame, (x, y))
        normalized.append(canvas)
    return normalized


def normalize_rows(
    rows: list[list[Any]],
    anchor: str,
    mode: str,
    Image: Any,
) -> list[list[Any]]:
    """Normalize frame canvases per animation row.

    mode "per-row": each row is normalized to its own max width/height, so rows
    stay compact and one tall row does not inflate the others.
    mode "global": every frame across all rows shares one canvas (legacy behavior).
    """
    if mode == "global":
        flat = [frame for row in rows for frame in row]
        width = max(frame.width for frame in flat)
        height = max(frame.height for frame in flat)
        return [
            _normalize_to(frames, width, height, anchor, Image)
            for frames in rows
        ]
    return [
        _normalize_to(
            frames,
            max(frame.width for frame in frames),
            max(frame.height for frame in frames),
            anchor,
            Image,
        )
        for frames in rows
    ]


def _normalize_to(
    frames: list[Any],
    width: int,
    height: int,
    anchor: str,
    Image: Any,
) -> list[Any]:
    normalized: list[Any] = []
    for frame in frames:
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        if anchor == "center":
            x = (width - frame.width) // 2
            y = (height - frame.height) // 2
        elif anchor == "bottom-center":
            x = (width - frame.width) // 2
            y = height - frame.height
        else:
            x = 0
            y = 0
        canvas.alpha_composite(frame, (x, y))
        normalized.append(canvas)
    return normalized


def trim_frame(frame: Any, trim: bool, alpha_threshold: int, Image: Any) -> tuple[Any, list[int]]:
    if not trim:
        return frame, [0, 0, frame.width, frame.height]
    alpha = frame.getchannel("A")
    mask = alpha.point(lambda value: 255 if value >= alpha_threshold else 0)
    bbox = mask.getbbox()
    if bbox is None:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0)), [0, 0, 1, 1]
    left, top, right, bottom = bbox
    return frame.crop(bbox), [left, top, right - left, bottom - top]


def extrude_sprite(atlas: Any, sprite: Any, x: int, y: int, amount: int) -> None:
    if amount <= 0:
        return
    width, height = sprite.size
    top = sprite.crop((0, 0, width, 1))
    bottom = sprite.crop((0, height - 1, width, height))
    left = sprite.crop((0, 0, 1, height))
    right = sprite.crop((width - 1, 0, width, height))
    atlas.paste(top.resize((width, amount)), (x, y - amount))
    atlas.paste(bottom.resize((width, amount)), (x, y + height))
    atlas.paste(left.resize((amount, height)), (x - amount, y))
    atlas.paste(right.resize((amount, height)), (x + width, y))
    atlas.paste(
        sprite.crop((0, 0, 1, 1)).resize((amount, amount)),
        (x - amount, y - amount),
    )
    atlas.paste(
        sprite.crop((width - 1, 0, width, 1)).resize((amount, amount)),
        (x + width, y - amount),
    )
    atlas.paste(
        sprite.crop((0, height - 1, 1, height)).resize((amount, amount)),
        (x - amount, y + height),
    )
    atlas.paste(
        sprite.crop((width - 1, height - 1, width, height)).resize((amount, amount)),
        (x + width, y + height),
    )


def pack_atlas(
    rows: list[list[Any]],
    columns: int,
    padding: int,
    extrusion: int,
    trim: bool,
    alpha_threshold: int,
    Image: Any,
) -> tuple[Any, list[dict[str, Any]], list[tuple[int, int]]]:
    """Pack animation rows into one atlas, one horizontal band per row.

    rows: normalized frames grouped by animation row.
    Returns (atlas, records, row_ranges). records is the flat row-major frame
    records; row_ranges holds each row's (start, end) inclusive index into records.
    """
    # Trim each sprite and remember its source rect, preserving row structure.
    # Each entry: (sprite, source_rect, full_frame_size)
    trimmed_rows: list[list[tuple[Any, list[int], tuple[int, int]]]] = []
    for frames in rows:
        row_sprites: list[tuple[Any, list[int], tuple[int, int]]] = []
        for frame in frames:
            sprite, source_rect = trim_frame(frame, trim, alpha_threshold, Image)
            row_sprites.append((sprite, source_rect, (frame.width, frame.height)))
        trimmed_rows.append(row_sprites)

    # Per-row band heights; a row's sprites are laid out left-to-right.
    row_heights = [
        max(sprite.height for sprite, _, _ in row_sprites) + 2 * (padding + extrusion)
        for row_sprites in trimmed_rows
    ]
    row_widths = [
        sum(sprite.width + 2 * (padding + extrusion) for sprite, _, _ in row_sprites)
        for row_sprites in trimmed_rows
    ]
    atlas_width = max(row_widths) if row_widths else 1
    atlas_height = sum(row_heights) if row_heights else 1
    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))

    records: list[dict[str, Any]] = []
    row_ranges: list[tuple[int, int]] = []
    y = 0
    for row_sprites, band_height in zip(trimmed_rows, row_heights):
        x = 0
        start = len(records)
        for sprite, source_rect, full_size in row_sprites:
            px = x + padding + extrusion
            py = y + padding + extrusion
            atlas.alpha_composite(sprite, (px, py))
            extrude_sprite(atlas, sprite, px, py, extrusion)
            records.append(
                {
                    "frame": {"x": px, "y": py, "w": sprite.width, "h": sprite.height},
                    "rotated": False,
                    "trimmed": trim,
                    "spriteSourceSize": {
                        "x": source_rect[0],
                        "y": source_rect[1],
                        "w": source_rect[2],
                        "h": source_rect[3],
                    },
                    "sourceSize": {"w": full_size[0], "h": full_size[1]},
                }
            )
            x += sprite.width + 2 * (padding + extrusion)
        row_ranges.append((start, len(records) - 1))
        y += band_height
    return atlas, records, row_ranges


def build_gif_palette(
    frames: list[Any],
    alpha_threshold: int,
) -> list[tuple[int, int, int]]:
    buckets: dict[tuple[int, int, int], list[int]] = {}
    for frame in frames:
        for red, green, blue, alpha in pixel_data(frame):
            if alpha < alpha_threshold:
                continue
            key = (red >> 3, green >> 3, blue >> 3)
            bucket = buckets.setdefault(key, [0, 0, 0, 0])
            bucket[0] += 1
            bucket[1] += red
            bucket[2] += green
            bucket[3] += blue
    ordered = sorted(buckets.values(), key=lambda bucket: bucket[0], reverse=True)
    palette = [(0, 0, 0)]
    palette.extend(
        (
            bucket[1] // bucket[0],
            bucket[2] // bucket[0],
            bucket[3] // bucket[0],
        )
        for bucket in ordered[:255]
    )
    if len(palette) == 1:
        palette.append((0, 0, 0))
    return palette


def gif_frame(
    rgba: Any,
    palette: list[tuple[int, int, int]],
    alpha_threshold: int,
    cache: dict[tuple[int, int, int], int],
    Image: Any,
) -> Any:
    indices: list[int] = []
    for red, green, blue, alpha in pixel_data(rgba):
        if alpha < alpha_threshold:
            indices.append(0)
            continue
        key = (red >> 3, green >> 3, blue >> 3)
        palette_index = cache.get(key)
        if palette_index is None:
            palette_index = min(
                range(1, len(palette)),
                key=lambda index: (
                    (palette[index][0] - red) ** 2
                    + (palette[index][1] - green) ** 2
                    + (palette[index][2] - blue) ** 2
                ),
            )
            cache[key] = palette_index
        indices.append(palette_index)

    frame = Image.new("P", rgba.size, 0)
    flattened = [channel for color in palette for channel in color]
    flattened.extend([0] * (768 - len(flattened)))
    frame.putpalette(flattened)
    frame.putdata(indices)
    frame.info["transparency"] = 0
    frame.info["disposal"] = 2
    return frame


def write_preview(
    path: Path,
    frames: list[Any],
    durations: list[int],
    loop: bool,
    kind: str,
    alpha_threshold: int,
    Image: Any,
) -> None:
    if kind == "gif":
        palette = build_gif_palette(frames, alpha_threshold)
        cache: dict[tuple[int, int, int], int] = {}
        preview = [
            gif_frame(frame, palette, alpha_threshold, cache, Image)
            for frame in frames
        ]
        kwargs: dict[str, Any] = {
            "save_all": True,
            "append_images": preview[1:],
            "duration": [max(20, duration) for duration in durations],
            "disposal": 2,
            "transparency": 0,
        }
        if loop:
            kwargs["loop"] = 0
        preview[0].save(path, format="GIF", **kwargs)
    else:
        kwargs = {
            "save_all": True,
            "append_images": frames[1:],
            "duration": durations,
            "disposal": 1,
            "blend": 0,
        }
        kwargs["loop"] = 0 if loop else 1
        frames[0].save(path, format="PNG", **kwargs)


def build_manifest(
    args: argparse.Namespace,
    paths: list[Path],
    records: list[dict[str, Any]],
    atlas_size: tuple[int, int] | None,
    durations: list[int],
    row_ranges: list[tuple[int, int]],
    row_names: list[str],
) -> dict[str, Any]:
    frame_map: dict[str, Any] = {}
    for index, (path, record) in enumerate(zip(paths, records)):
        frame_map[path.name] = {
            **record,
            "duration": durations[index],
            "pivot": {"x": args.pivot[0], "y": args.pivot[1]},
        }
    frame_tags: list[dict[str, Any]] = []
    for row_index, ((start, end), tag_name) in enumerate(zip(row_ranges, row_names)):
        frame_tag: dict[str, Any] = {
            "name": tag_name,
            "from": start,
            "to": end,
            "direction": "forward",
        }
        if len(row_ranges) > 1:
            frame_tag["row"] = row_index
        if args.loop == "once":
            frame_tag["repeat"] = "1"
        frame_tags.append(frame_tag)
    return {
        "frames": frame_map,
        "meta": {
            "app": "game-image-generation-rules/scripts/sprite/pack_animation.py",
            "version": "1",
            "image": args.atlas.name if args.atlas else None,
            "format": "RGBA8888",
            "size": (
                {"w": atlas_size[0], "h": atlas_size[1]}
                if atlas_size is not None
                else None
            ),
            "scale": "1",
            "frameTags": frame_tags,
            "animation": {
                "fps": args.fps,
                "loop": args.loop == "loop",
                "totalDuration": sum(durations),
            },
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Pack sprite frames into a PNG atlas, GIF, APNG, and Aseprite-style JSON."
    )
    parser.add_argument("inputs", nargs="+", help="Frame files or directories.")
    parser.add_argument("--glob", default="*.png")
    parser.add_argument("--output-prefix", type=Path)
    parser.add_argument("--atlas", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--gif", type=Path)
    parser.add_argument("--apng", type=Path)
    parser.add_argument("--name", default="animation")
    parser.add_argument("--columns", type=int)
    parser.add_argument("--padding", type=int, default=1)
    parser.add_argument("--extrude", type=int, default=0)
    parser.add_argument("--trim", action="store_true")
    parser.add_argument("--alpha-threshold", type=int, default=1)
    parser.add_argument("--gif-alpha-threshold", type=int, default=128)
    parser.add_argument("--fps", type=float, default=10.0)
    parser.add_argument("--durations", type=parse_durations)
    parser.add_argument("--loop", choices=("loop", "once"), default="loop")
    parser.add_argument("--pivot", type=parse_pair, default=(0.5, 1.0))
    parser.add_argument("--anchor", choices=("center", "bottom-center", "top-left"), default="center")
    parser.add_argument(
        "--normalize",
        choices=("per-row", "global"),
        default="per-row",
        help=(
            "Canvas normalization across frames. per-row (default): each animation row "
            "is sized to its own max width/height so rows stay compact. global: every "
            "frame across all rows shares one canvas."
        ),
    )
    parser.add_argument(
        "--names",
        help=(
            "Comma-separated animation names, one per detected row (e.g. run,jump,dash). "
            "Falls back to {--name} for a single animation or {--name}_r{row} per row."
        ),
    )
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    Image = _load_pillow()
    try:
        resolve_outputs(args)
        if (
            not 1 <= args.alpha_threshold <= 255
            or not 1 <= args.gif_alpha_threshold <= 255
            or args.fps <= 0
            or args.padding < 0
            or args.extrude < 0
        ):
            raise ValueError(
                "alpha threshold and FPS must be positive; padding and extrusion cannot be negative"
            )
        ensure_writable((args.atlas, args.json), args.force)
        paths = collect_paths(args.inputs, args.glob)
        if not paths:
            raise ValueError("no input frames found")

        # Group frames into animation rows (manifest preferred, else _rN_cM names,
        # else a single animation). Rows are ordered; frames within a row ordered.
        slice_manifest = find_slice_manifest(args.inputs)
        row_groups = group_paths_by_row(paths, slice_manifest)
        row_count = len(row_groups)

        # Resolve per-row animation names.
        if args.names:
            row_names = [name.strip() for name in args.names.split(",")]
            if len(row_names) != row_count:
                raise ValueError(
                    f"--names provided {len(row_names)} names but {row_count} animation "
                    "row(s) were detected"
                )
        elif row_count == 1:
            row_names = [args.name]
        else:
            row_names = [f"{args.name}_r{index}" for index in range(row_count)]

        # Flat ordered frame list (row-major) for records/durations alignment.
        ordered_paths = [path for group in row_groups for path in group]

        # GIF/APNG are one-animation-per-file; multi-row needs derived per-row files.
        if row_count > 1 and (args.gif or args.apng) and not args.output_prefix:
            raise ValueError(
                "multiple animation rows detected; GIF/APNG are written per row, so use "
                "--output-prefix (derives one preview per row) instead of an explicit "
                "--gif/--apng file"
            )

        # Load frames preserving row structure.
        rows: list[list[Any]] = []
        for group in row_groups:
            row_frames: list[Any] = []
            for path in group:
                with Image.open(path) as source:
                    row_frames.append(source.convert("RGBA"))
            rows.append(row_frames)

        rows = normalize_rows(rows, args.anchor, args.normalize, Image)
        flat_frames = [frame for row in rows for frame in row]
        total_frames = len(flat_frames)

        if args.durations:
            if len(args.durations) == 1:
                durations = args.durations * total_frames
            elif len(args.durations) == total_frames:
                durations = args.durations
            else:
                raise ValueError(
                    "--durations must contain one value or one value per frame "
                    f"({total_frames} frames across {row_count} row(s))"
                )
        else:
            durations = [max(1, round(1000 / args.fps))] * total_frames

        # Split flat durations back per row for per-row previews.
        row_durations: list[list[int]] = []
        offset = 0
        for row in rows:
            row_durations.append(durations[offset : offset + len(row)])
            offset += len(row)

        atlas = None
        records: list[dict[str, Any]]
        row_ranges: list[tuple[int, int]]
        if args.atlas or args.json:
            atlas, records, row_ranges = pack_atlas(
                rows,
                args.columns,
                args.padding,
                args.extrude,
                args.trim,
                args.alpha_threshold,
                Image,
            )
            if args.atlas:
                atlas.save(args.atlas)
        else:
            records = [
                {
                    "frame": {"x": 0, "y": 0, "w": frame.width, "h": frame.height},
                    "rotated": False,
                    "trimmed": False,
                    "spriteSourceSize": {"x": 0, "y": 0, "w": frame.width, "h": frame.height},
                    "sourceSize": {"w": frame.width, "h": frame.height},
                }
                for frame in flat_frames
            ]
            row_ranges = []
            cursor = 0
            for row in rows:
                row_ranges.append((cursor, cursor + len(row) - 1))
                cursor += len(row)

        written_previews: list[Path] = []
        preview_paths: list[Path] = []
        for row_index, tag_name in enumerate(row_names):
            if args.gif:
                preview_paths.append(
                    args.gif
                    if row_count == 1
                    else args.output_prefix.with_name(
                        f"{args.output_prefix.name}_{tag_name}"
                    ).with_suffix(".gif")
                )
            if args.apng:
                preview_paths.append(
                    args.apng
                    if row_count == 1
                    else args.output_prefix.with_name(
                        f"{args.output_prefix.name}_{tag_name}"
                    ).with_suffix(".apng")
                )
        ensure_writable(preview_paths, args.force)

        preview_iter = iter(preview_paths)
        for row_frames, durations_for_row in zip(rows, row_durations):
            if args.gif:
                gif_path = next(preview_iter)
                write_preview(
                    gif_path, row_frames, durations_for_row, args.loop == "loop", "gif",
                    args.gif_alpha_threshold, Image
                )
                written_previews.append(gif_path)
            if args.apng:
                apng_path = next(preview_iter)
                write_preview(
                    apng_path, row_frames, durations_for_row, args.loop == "loop", "apng",
                    args.alpha_threshold, Image
                )
                written_previews.append(apng_path)

        if args.json:
            manifest = build_manifest(
                args,
                ordered_paths,
                records,
                atlas.size if atlas is not None else None,
                durations,
                row_ranges,
                row_names,
            )
            args.json.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    outputs = [path for path in (args.atlas, args.json) if path]
    outputs.extend(written_previews)
    for path in outputs:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

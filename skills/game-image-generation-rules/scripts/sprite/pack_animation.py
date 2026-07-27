#!/usr/bin/env python3
"""Pack ordered sprite frames into an atlas and animation preview formats."""

from __future__ import annotations

import argparse
import json
import math
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
    frames: list[Any],
    columns: int,
    padding: int,
    extrusion: int,
    trim: bool,
    alpha_threshold: int,
    Image: Any,
) -> tuple[Any, list[dict[str, Any]]]:
    packed: list[Any] = []
    source_rects: list[list[int]] = []
    for frame in frames:
        sprite, source_rect = trim_frame(frame, trim, alpha_threshold, Image)
        packed.append(sprite)
        source_rects.append(source_rect)

    slot_width = max(sprite.width for sprite in packed) + 2 * (padding + extrusion)
    slot_height = max(sprite.height for sprite in packed) + 2 * (padding + extrusion)
    rows = math.ceil(len(packed) / columns)
    atlas = Image.new(
        "RGBA",
        (slot_width * columns, slot_height * rows),
        (0, 0, 0, 0),
    )
    records: list[dict[str, Any]] = []
    for index, (sprite, source_rect) in enumerate(zip(packed, source_rects)):
        column = index % columns
        row = index // columns
        x = column * slot_width + padding + extrusion
        y = row * slot_height + padding + extrusion
        atlas.alpha_composite(sprite, (x, y))
        extrude_sprite(atlas, sprite, x, y, extrusion)
        records.append(
            {
                "frame": {"x": x, "y": y, "w": sprite.width, "h": sprite.height},
                "rotated": False,
                "trimmed": trim,
                "spriteSourceSize": {
                    "x": source_rect[0],
                    "y": source_rect[1],
                    "w": source_rect[2],
                    "h": source_rect[3],
                },
                "sourceSize": {"w": frames[index].width, "h": frames[index].height},
            }
        )
    return atlas, records


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
) -> dict[str, Any]:
    frame_map: dict[str, Any] = {}
    for index, (path, record) in enumerate(zip(paths, records)):
        frame_map[path.name] = {
            **record,
            "duration": durations[index],
            "pivot": {"x": args.pivot[0], "y": args.pivot[1]},
        }
    frame_tag: dict[str, Any] = {
        "name": args.name,
        "from": 0,
        "to": len(paths) - 1,
        "direction": "forward",
    }
    if args.loop == "once":
        frame_tag["repeat"] = "1"
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
            "frameTags": [frame_tag],
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
        paths = collect_paths(args.inputs, args.glob)
        if not paths:
            raise ValueError("no input frames found")
        columns = args.columns or math.ceil(math.sqrt(len(paths)))
        if columns < 1:
            raise ValueError("--columns must be positive")
        ensure_writable((args.atlas, args.json, args.gif, args.apng), args.force)

        frames: list[Any] = []
        for path in paths:
            with Image.open(path) as source:
                frames.append(source.convert("RGBA"))
        frames = normalize_frames(frames, args.anchor, Image)

        if args.durations:
            if len(args.durations) == 1:
                durations = args.durations * len(frames)
            elif len(args.durations) == len(frames):
                durations = args.durations
            else:
                raise ValueError("--durations must contain one value or one value per frame")
        else:
            durations = [max(1, round(1000 / args.fps))] * len(frames)

        atlas = None
        records: list[dict[str, Any]]
        if args.atlas or args.json:
            atlas, records = pack_atlas(
                frames,
                columns,
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
                for frame in frames
            ]

        if args.gif:
            write_preview(
                args.gif, frames, durations, args.loop == "loop", "gif",
                args.gif_alpha_threshold, Image
            )
        if args.apng:
            write_preview(
                args.apng, frames, durations, args.loop == "loop", "apng",
                args.alpha_threshold, Image
            )
        if args.json:
            manifest = build_manifest(
                args,
                paths,
                records,
                atlas.size if atlas is not None else None,
                durations,
            )
            args.json.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    outputs = [path for path in (args.atlas, args.json, args.gif, args.apng) if path]
    for path in outputs:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

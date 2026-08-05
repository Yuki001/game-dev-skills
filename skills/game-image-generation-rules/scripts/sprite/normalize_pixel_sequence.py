#!/usr/bin/env python3
"""Normalize transparent video-derived frames to one pixel-art canvas and palette."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ALPHA_THRESHOLD = 128
SAFE_MARGIN = 1


def _die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def _load_pillow() -> Any:
    try:
        from PIL import Image
    except ImportError:
        _die("Pillow is required. Activate the repo environment and install `pillow`.")
    return Image


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


def parse_size(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"(\d+)[xX](\d+)", value.strip())
    if not match:
        raise argparse.ArgumentTypeError("size must use WIDTHxHEIGHT, for example 64x64")
    size = (int(match.group(1)), int(match.group(2)))
    if size[0] < 3 or size[1] < 3:
        raise argparse.ArgumentTypeError("each target dimension must be at least 3 pixels")
    return size


def pixel_data(image: Any) -> Any:
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter is not None else image.getdata()


def alpha_bbox(rgba: Any) -> tuple[int, int, int, int] | None:
    mask = rgba.getchannel("A").point(
        lambda value: 255 if value >= ALPHA_THRESHOLD else 0
    )
    return mask.getbbox()


def union_bbox(
    boxes: list[tuple[int, int, int, int]],
) -> tuple[int, int, int, int]:
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def fit_size(source: tuple[int, int], target: tuple[int, int]) -> tuple[int, int]:
    available = (target[0] - SAFE_MARGIN * 2, target[1] - SAFE_MARGIN * 2)
    scale = min(available[0] / source[0], available[1] / source[1])
    return (
        max(1, min(available[0], round(source[0] * scale))),
        max(1, min(available[1], round(source[1] * scale))),
    )


def placement(
    content: tuple[int, int], target: tuple[int, int], anchor: str
) -> tuple[int, int]:
    x = (target[0] - content[0]) // 2
    if anchor == "bottom-center":
        return x, target[1] - SAFE_MARGIN - content[1]
    return x, (target[1] - content[1]) // 2


def build_global_palette(
    frames: list[Any], colors: int, Image: Any
) -> list[tuple[int, int, int]]:
    histogram: Counter[tuple[int, int, int]] = Counter()
    for frame in frames:
        histogram.update(
            (red, green, blue)
            for red, green, blue, alpha in pixel_data(frame)
            if alpha >= ALPHA_THRESHOLD
        )
    if not histogram:
        raise ValueError("no visible pixels remain after resizing")
    if len(histogram) <= colors:
        return [color for color, _count in histogram.most_common()]

    samples: list[tuple[int, int, int]] = []
    for color, count in histogram.items():
        samples.extend([color] * count)
    width = min(1024, len(samples))
    height = math.ceil(len(samples) / width)
    samples.extend([samples[-1]] * (width * height - len(samples)))
    sample_image = Image.new("RGB", (width, height))
    sample_image.putdata(samples)
    quantized = sample_image.quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.NONE,
    )
    raw_palette = quantized.getpalette() or []
    used = sorted(
        quantized.getcolors(maxcolors=colors) or [],
        key=lambda item: (-item[0], item[1]),
    )
    return [
        tuple(raw_palette[index * 3 : index * 3 + 3])
        for _count, index in used
    ]


def apply_palette(frame: Any, palette: list[tuple[int, int, int]], Image: Any) -> Any:
    output = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    converted = []
    for red, green, blue, alpha in pixel_data(frame):
        if alpha < ALPHA_THRESHOLD:
            converted.append((0, 0, 0, 0))
            continue
        source = (red, green, blue)
        color = min(
            palette,
            key=lambda candidate: sum(
                (candidate[channel] - source[channel]) ** 2 for channel in range(3)
            ),
        )
        converted.append((*color, 255))
    output.putdata(converted)
    return output


def normalize(args: argparse.Namespace, Image: Any) -> dict[str, Any]:
    input_dir = args.input_dir.resolve()
    output_dir = args.output_dir.resolve()
    if input_dir == output_dir:
        raise ValueError("input and output directories must differ")
    if not input_dir.is_dir():
        raise ValueError(f"input directory does not exist: {input_dir}")

    paths = sorted(input_dir.glob("*.png"), key=natural_key)
    if not paths:
        raise ValueError("no PNG frames found in the input directory")

    frames: list[Any] = []
    boxes: list[tuple[int, int, int, int]] = []
    sizes: set[tuple[int, int]] = set()
    opaque_paths: list[Path] = []
    for path in paths:
        with Image.open(path) as source:
            rgba = source.convert("RGBA")
        frames.append(rgba)
        sizes.add(rgba.size)
        alpha = rgba.getchannel("A")
        if alpha.getextrema() == (255, 255):
            opaque_paths.append(path)
        box = alpha_bbox(rgba)
        if box is None:
            raise ValueError(f"frame has no visible pixels at alpha >= {ALPHA_THRESHOLD}: {path}")
        boxes.append(box)

    if len(sizes) != 1:
        raise ValueError(f"source frame dimensions differ: {sorted(sizes)}")
    if opaque_paths:
        raise ValueError(
            "one or more frames are fully opaque; resolve native alpha or remove the "
            f"matte before pixel normalization: {opaque_paths[0]}"
        )

    shared_box = union_bbox(boxes)
    shared_size = (shared_box[2] - shared_box[0], shared_box[3] - shared_box[1])
    content_size = fit_size(shared_size, args.size)
    offset = placement(content_size, args.size, args.anchor)
    staged: list[Any] = []
    for frame in frames:
        cropped = frame.crop(shared_box).resize(content_size, Image.Resampling.NEAREST)
        canvas = Image.new("RGBA", args.size, (0, 0, 0, 0))
        canvas.alpha_composite(cropped, offset)
        staged.append(canvas)

    palette = build_global_palette(staged, args.colors, Image)
    normalized = [apply_palette(frame, palette, Image) for frame in staged]
    output_dir.mkdir(parents=True, exist_ok=True)
    expected_names = {path.name for path in paths}
    unexpected = sorted(
        path.name for path in output_dir.glob("*.png") if path.name not in expected_names
    )
    if unexpected:
        raise ValueError(
            "output directory contains stale PNG files not present in the input: "
            + ", ".join(unexpected)
        )

    frame_reports = []
    for path, frame in zip(paths, normalized):
        output_path = output_dir / path.name
        frame.save(output_path)
        frame_reports.append(
            {
                "source": str(path),
                "output": str(output_path),
                "bbox": list(alpha_bbox(frame) or (0, 0, 0, 0)),
            }
        )

    report = {
        "schema": "game-image-generation-rules.pixel-sequence-normalization/v1",
        "frame_count": len(paths),
        "source_size": list(next(iter(sizes))),
        "shared_source_bbox": list(shared_box),
        "target_size": list(args.size),
        "content_size": list(content_size),
        "anchor": args.anchor,
        "offset": list(offset),
        "safe_margin": SAFE_MARGIN,
        "alpha": f"binary at source threshold {ALPHA_THRESHOLD}",
        "color_budget": args.colors,
        "palette_rgb": [list(color) for color in palette],
        "frames": frame_reports,
    }
    report_path = output_dir / "normalize-report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Normalize transparent video-derived PNG frames with one shared crop, "
            "pixel canvas, anchor, and sequence-wide palette."
        )
    )
    parser.add_argument("input_dir", type=Path, help="Directory of ordered PNG frames.")
    parser.add_argument("output_dir", type=Path, help="Directory for normalized PNG frames.")
    parser.add_argument(
        "--size", required=True, type=parse_size, help="Native canvas WIDTHxHEIGHT."
    )
    parser.add_argument(
        "--colors", required=True, type=int, help="Opaque colors for the whole sequence."
    )
    parser.add_argument(
        "--anchor",
        choices=("bottom-center", "center"),
        default="bottom-center",
        help="Shared placement anchor. Default: bottom-center.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if not 1 <= args.colors <= 256:
        print("error: --colors must be between 1 and 256", file=sys.stderr)
        return 2
    Image = _load_pillow()
    try:
        report = normalize(args, Image)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"normalized {report['frame_count']} frames to "
        f"{report['target_size'][0]}x{report['target_size'][1]} with "
        f"{len(report['palette_rgb'])} shared colors"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

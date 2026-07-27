#!/usr/bin/env python3
"""Measure objective properties of an ordered sprite-frame sequence."""

from __future__ import annotations

import argparse
import json
import re
import statistics
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
        _die(
            f"Pillow is required for sprite sequence inspection. "
            f"{_dependency_hint('pillow')}"
        )
    return Image


def natural_key(path: Path) -> list[object]:
    return [
        int(part) if part.isdigit() else part.lower()
        for part in re.split(r"(\d+)", path.name)
    ]


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


def alpha_bbox(alpha: Any, threshold: int) -> tuple[int, int, int, int] | None:
    mask = alpha.point(lambda value: 255 if value >= threshold else 0)
    return mask.getbbox()


def pixel_data(image: Any) -> Any:
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter is not None else image.getdata()


def alpha_geometry(rgba: Any, threshold: int, edge_margin: int) -> dict[str, Any]:
    width, height = rgba.size
    alpha = rgba.getchannel("A")
    values = list(pixel_data(alpha))
    bbox = alpha_bbox(alpha, threshold)
    active = 0
    mass = 0
    weighted_x = 0
    weighted_y = 0
    for index, value in enumerate(values):
        if value >= threshold:
            active += 1
        if value:
            x = index % width
            y = index // width
            mass += value
            weighted_x += x * value
            weighted_y += y * value

    if bbox is None:
        centroid = None
        baseline = None
        edge_contact = {"left": False, "top": False, "right": False, "bottom": False}
        bbox_size = None
    else:
        left, top, right, bottom = bbox
        centroid = [
            round(weighted_x / mass, 4),
            round(weighted_y / mass, 4),
        ] if mass else None
        baseline = bottom - 1
        edge_contact = {
            "left": left <= edge_margin,
            "top": top <= edge_margin,
            "right": right >= width - edge_margin,
            "bottom": bottom >= height - edge_margin,
        }
        bbox_size = [right - left, bottom - top]

    return {
        "bbox": list(bbox) if bbox else None,
        "bbox_size": bbox_size,
        "alpha_pixels": active,
        "alpha_mass": mass,
        "occupied_ratio": round(active / (width * height), 6),
        "centroid": centroid,
        "baseline": baseline,
        "edge_contact": edge_contact,
    }


def color_histogram(rgba: Any, bins: int, sample_size: int) -> list[float]:
    image = rgba.copy()
    image.thumbnail((sample_size, sample_size))
    histogram = [0.0] * (bins * bins * bins)
    total = 0.0
    scale = bins / 256.0
    for red, green, blue, alpha in pixel_data(image):
        if alpha == 0:
            continue
        r_bin = min(bins - 1, int(red * scale))
        g_bin = min(bins - 1, int(green * scale))
        b_bin = min(bins - 1, int(blue * scale))
        weight = alpha / 255.0
        histogram[(r_bin * bins + g_bin) * bins + b_bin] += weight
        total += weight
    if total:
        histogram = [value / total for value in histogram]
    return histogram


def histogram_distance(first: list[float], second: list[float]) -> float:
    return round(sum(abs(a - b) for a, b in zip(first, second)) / 2.0, 6)


def normalized_frame(rgba: Any, size: tuple[int, int], Image: Any) -> Any:
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    x = (size[0] - rgba.width) // 2
    y = (size[1] - rgba.height) // 2
    canvas.alpha_composite(rgba, (x, y))
    return canvas


def motion_delta(
    first: Any,
    second: Any,
    sample_size: int,
    alpha_threshold: int,
    Image: Any,
) -> float:
    width = max(first.width, second.width)
    height = max(first.height, second.height)
    first = normalized_frame(first, (width, height), Image)
    second = normalized_frame(second, (width, height), Image)
    first.thumbnail((sample_size, sample_size))
    second.thumbnail((sample_size, sample_size))
    total = 0.0
    visible = 0
    for first_pixel, second_pixel in zip(pixel_data(first), pixel_data(second)):
        if (
            first_pixel[3] < alpha_threshold
            and second_pixel[3] < alpha_threshold
        ):
            continue
        total += sum(abs(a - b) for a, b in zip(first_pixel, second_pixel)) / (
            255.0 * 4.0
        )
        visible += 1
    return round(total / visible, 6) if visible else 0.0


def inspect_sequence(args: argparse.Namespace, Image: Any) -> dict[str, Any]:
    paths = collect_paths(args.inputs, args.glob)
    if not paths:
        raise ValueError("no input frames found")

    frames: list[Any] = []
    frame_reports: list[dict[str, Any]] = []
    histograms: list[list[float]] = []

    for index, path in enumerate(paths):
        with Image.open(path) as source:
            source_mode = source.mode
            rgba = source.convert("RGBA")
        frames.append(rgba)
        geometry = alpha_geometry(rgba, args.alpha_threshold, args.edge_margin)
        histogram = color_histogram(rgba, args.color_bins, args.sample_size)
        histograms.append(histogram)
        color_count = rgba.getcolors(maxcolors=args.max_color_count)
        frame_reports.append(
            {
                "index": index,
                "file": str(path),
                "size": list(rgba.size),
                "source_mode": source_mode,
                **geometry,
                "unique_colors": len(color_count) if color_count is not None else f">{args.max_color_count}",
            }
        )

    occupied = [report["occupied_ratio"] for report in frame_reports if report["alpha_pixels"]]
    median_occupied = statistics.median(occupied) if occupied else 0.0
    reference_histogram = histograms[0]
    previous = None
    for index, report in enumerate(frame_reports):
        report["occupied_vs_median"] = (
            round(report["occupied_ratio"] / median_occupied, 6)
            if median_occupied
            else None
        )
        report["color_drift_from_first"] = histogram_distance(
            reference_histogram, histograms[index]
        )
        if previous is None:
            report["motion_delta_from_previous"] = None
        else:
            report["motion_delta_from_previous"] = motion_delta(
                previous,
                frames[index],
                args.sample_size,
                args.alpha_threshold,
                Image,
            )
        previous = frames[index]

    sizes = {tuple(frame.size) for frame in frames}
    empty_frames = [report["index"] for report in frame_reports if not report["alpha_pixels"]]
    edge_frames = [
        report["index"]
        for report in frame_reports
        if any(report["edge_contact"].values())
    ]
    centroids = [report["centroid"] for report in frame_reports if report["centroid"]]
    baselines = [report["baseline"] for report in frame_reports if report["baseline"] is not None]
    centroid_range = None
    if centroids:
        centroid_range = {
            "x": round(max(value[0] for value in centroids) - min(value[0] for value in centroids), 4),
            "y": round(max(value[1] for value in centroids) - min(value[1] for value in centroids), 4),
        }

    return {
        "schema": "generic-image-generation-rules.sprite-sequence-inspection/v1",
        "frame_count": len(frames),
        "dimension_consistent": len(sizes) == 1,
        "sizes": [list(size) for size in sorted(sizes)],
        "median_occupied_ratio": round(median_occupied, 6),
        "empty_frames": empty_frames,
        "edge_contact_frames": edge_frames,
        "centroid_range": centroid_range,
        "baseline_range": (max(baselines) - min(baselines)) if baselines else None,
        "frames": frame_reports,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Measure alpha bounds, drift, edge contact, palette drift, and motion in sprite frames."
    )
    parser.add_argument("inputs", nargs="+", help="Frame files or directories.")
    parser.add_argument("--glob", default="*.png", help="Directory glob. Default: *.png")
    parser.add_argument("--output", type=Path, help="Write the JSON report to this path.")
    parser.add_argument("--alpha-threshold", type=int, default=1)
    parser.add_argument("--edge-margin", type=int, default=0)
    parser.add_argument("--color-bins", type=int, default=8, choices=range(2, 17))
    parser.add_argument("--sample-size", type=int, default=256)
    parser.add_argument("--max-color-count", type=int, default=4096)
    parser.add_argument("--compact", action="store_true", help="Emit compact JSON.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if (
        not 1 <= args.alpha_threshold <= 255
        or args.edge_margin < 0
        or args.sample_size < 1
        or args.max_color_count < 1
    ):
        print("error: invalid alpha threshold, margin, or sample limit", file=sys.stderr)
        return 2
    Image = _load_pillow()
    try:
        report = inspect_sequence(args, Image)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    payload = json.dumps(
        report,
        indent=None if args.compact else 2,
        ensure_ascii=False,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

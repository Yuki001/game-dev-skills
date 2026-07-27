#!/usr/bin/env python3
"""Split a horizontal sprite strip with alpha projection and DP, then align frames."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


SIZE_RE = re.compile(r"^(\d+)[xX×](\d+)$")


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
            f"Pillow is required for sprite strip slicing. "
            f"{_dependency_hint('pillow')}"
        )
    return Image


def parse_size(value: str) -> tuple[int, int]:
    match = SIZE_RE.match(value.strip())
    if not match:
        raise argparse.ArgumentTypeError("expected WIDTHxHEIGHT")
    width, height = int(match.group(1)), int(match.group(2))
    if width < 1 or height < 1:
        raise argparse.ArgumentTypeError("dimensions must be positive")
    return width, height


def pixel_data(image: Any) -> Any:
    getter = getattr(image, "get_flattened_data", None)
    return getter() if getter is not None else image.getdata()


def alpha_projection(rgba: Any) -> list[float]:
    width, height = rgba.size
    alpha = rgba.getchannel("A")
    values = list(pixel_data(alpha))
    projection = [0.0] * width
    for y in range(height):
        row = y * width
        for x in range(width):
            projection[x] += values[row + x]
    return projection


def smooth(values: list[float], radius: int) -> list[float]:
    if radius <= 0:
        return values[:]
    prefix = [0.0]
    for value in values:
        prefix.append(prefix[-1] + value)
    result: list[float] = []
    for index in range(len(values)):
        left = max(0, index - radius)
        right = min(len(values), index + radius + 1)
        result.append((prefix[right] - prefix[left]) / (right - left))
    return result


def content_runs(
    projection: list[float],
    epsilon: float,
    peak_minimum: float,
    minimum_width: int,
) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    index = 0
    while index < len(projection):
        if projection[index] <= epsilon:
            index += 1
            continue
        end = index
        peak = 0.0
        while end < len(projection) and projection[end] > epsilon:
            peak = max(peak, projection[end])
            end += 1
        if end - index >= minimum_width and peak >= peak_minimum:
            runs.append((index, end))
        index = end
    return runs


def run_mass(projection: list[float], span: tuple[int, int]) -> float:
    return sum(projection[span[0] : span[1]])


def drop_minor_runs(
    projection: list[float],
    runs: list[tuple[int, int]],
    fraction: float,
) -> list[tuple[int, int]]:
    if len(runs) <= 1:
        return runs
    maximum = max(run_mass(projection, run) for run in runs)
    threshold = maximum * fraction
    return [run for run in runs if run_mass(projection, run) >= threshold]


def median_run_width(runs: list[tuple[int, int]]) -> float:
    if not runs:
        return 0.0
    widths = sorted(end - start for start, end in runs)
    return float(widths[len(widths) // 2])


def pose_peaks(projection: list[float], start: int, end: int) -> list[int]:
    if end - start < 3:
        return [(start + end) // 2]
    run_maximum = max(projection[start:end], default=0.0)
    if run_maximum <= 0:
        return [(start + end) // 2]
    candidates = [
        x
        for x in range(start + 1, end - 1)
        if projection[x] >= projection[x - 1]
        and projection[x] > projection[x + 1]
        and projection[x] >= 0.45 * run_maximum
    ]
    if not candidates:
        return [(start + end) // 2]
    kept: list[int] = []
    for candidate in candidates:
        prominent = True
        for other in candidates:
            if other == candidate or projection[other] < projection[candidate]:
                continue
            low, high = sorted((candidate, other))
            valley = min(projection[low : high + 1])
            if valley > 0.62 * projection[candidate]:
                prominent = False
                break
        if prominent:
            kept.append(candidate)
    return kept or [candidates[0]]


def dp_cuts(
    projection: list[float],
    start: int,
    end: int,
    frame_count: int,
    width_weight: float,
    min_width_ratio: float,
) -> list[int] | None:
    if frame_count <= 1 or end - start < frame_count:
        return []
    ideal = (end - start) / frame_count
    minimum_width = max(2, int(ideal * min_width_ratio))
    cuts_needed = frame_count - 1
    previous: dict[int, tuple[float, list[int]]] = {start: (0.0, [])}
    for cut_index in range(1, cuts_needed + 1):
        current: dict[int, tuple[float, list[int]]] = {}
        first = start + cut_index * minimum_width
        last = end - (cuts_needed - cut_index + 1) * minimum_width
        for position in range(first, last + 1):
            best: tuple[float, list[int]] | None = None
            for prior, (prior_cost, path) in previous.items():
                segment_width = position - prior
                if segment_width < minimum_width:
                    continue
                width_error = segment_width - ideal
                cost = (
                    prior_cost
                    + projection[position]
                    + width_weight * width_error * width_error
                )
                if best is None or cost < best[0]:
                    best = (cost, path + [position])
            if best is not None:
                current[position] = best
        if not current:
            return None
        previous = current

    best_final: tuple[float, list[int]] | None = None
    for prior, (prior_cost, path) in previous.items():
        segment_width = end - prior
        if segment_width < minimum_width:
            continue
        width_error = segment_width - ideal
        cost = prior_cost + width_weight * width_error * width_error
        if best_final is None or cost < best_final[0]:
            best_final = (cost, path)
    return best_final[1] if best_final else None


def split_range(
    projection: list[float],
    start: int,
    end: int,
    frame_count: int,
    width_weight: float,
    min_width_ratio: float,
) -> list[tuple[int, int]]:
    if frame_count <= 1 or end - start < frame_count:
        return [(start, end)]
    cuts = dp_cuts(
        projection,
        start,
        end,
        frame_count,
        width_weight,
        min_width_ratio,
    )
    if cuts is None or len(cuts) != frame_count - 1:
        return [
            (
                start + (end - start) * index // frame_count,
                start + (end - start) * (index + 1) // frame_count,
            )
            for index in range(frame_count)
        ]
    boundaries = [start, *cuts, end]
    return [
        (boundaries[index], boundaries[index + 1])
        for index in range(frame_count)
    ]


def segment_strip(
    projection: list[float],
    expected: int,
    width_weight: float,
    min_width_ratio: float,
) -> tuple[list[tuple[int, int]], int]:
    width = len(projection)
    maximum = max(projection, default=0.0)
    if width == 0 or expected < 1 or maximum <= 0:
        return [], 0
    epsilon = 0.045 * maximum
    peak_minimum = 0.18 * maximum
    minimum_run = max(4, width // 100)
    runs = content_runs(projection, epsilon, peak_minimum, minimum_run)
    runs = drop_minor_runs(projection, runs, 0.20)
    if not runs:
        return [], 0

    median_width = median_run_width(runs)
    width_total = sum(end - start for start, end in runs)
    segments: list[tuple[int, int]] = []
    for start, end in runs:
        peak_count = len(pose_peaks(projection, start, end))
        if len(runs) > 1 and median_width > 0:
            maximum_by_width = max(1, int((end - start) / median_width + 0.5))
            peak_count = min(peak_count, maximum_by_width)
        if (
            peak_count == 1
            and len(runs) > 1
            and median_width > 0
            and end - start > median_width * 1.45
        ):
            peak_count = 2
        if peak_count <= 1:
            segments.append((start, end))
        else:
            segments.extend(
                split_range(
                    projection,
                    start,
                    end,
                    peak_count,
                    width_weight,
                    min_width_ratio,
                )
            )

    natural_count = len(segments)
    content_start = min(start for start, _ in runs)
    content_end = max(end for _, end in runs)
    if (
        len(segments) != expected
        and width_total / expected >= 16
        and (content_end - content_start) / expected >= 16
    ):
        segments = split_range(
            projection,
            content_start,
            content_end,
            expected,
            width_weight,
            min_width_ratio,
        )
    return segments, natural_count


def equal_boundaries(width: int, frame_count: int) -> list[int]:
    return [round(index * width / frame_count) for index in range(frame_count + 1)]


def alpha_bbox(rgba: Any, threshold: int) -> tuple[int, int, int, int] | None:
    alpha = rgba.getchannel("A")
    mask = alpha.point(lambda value: 255 if value > threshold else 0)
    return mask.getbbox()


def alpha_centroid(rgba: Any, threshold: int) -> tuple[float, float] | None:
    width, _ = rgba.size
    values = list(pixel_data(rgba.getchannel("A")))
    mass = sum(value for value in values if value > threshold)
    if not mass:
        return None
    x_total = 0
    y_total = 0
    for index, value in enumerate(values):
        if value > threshold:
            x_total += (index % width) * value
            y_total += (index // width) * value
    return x_total / mass, y_total / mass


def crop_content(frame: Any, threshold: int, Image: Any) -> tuple[Any, list[int] | None]:
    bbox = alpha_bbox(frame, threshold)
    if bbox is None:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0)), None
    content = frame.crop(bbox)
    alpha = content.getchannel("A").point(
        lambda value: value if value > threshold else 0
    )
    content.putalpha(alpha)
    return content, list(bbox)


def choose_canvas(
    contents: list[Any],
    requested: tuple[int, int] | None,
    padding: int,
    required_content_height: int | None = None,
) -> tuple[int, int]:
    needed_width = max(content.width for content in contents) + padding * 2
    needed_height = (
        required_content_height
        if required_content_height is not None
        else max(content.height for content in contents)
    ) + padding * 2
    if requested is None:
        return needed_width, needed_height
    if requested[0] < needed_width or requested[1] < needed_height:
        raise ValueError(
            f"requested canvas {requested[0]}x{requested[1]} is smaller than "
            f"required {needed_width}x{needed_height}"
        )
    return requested


def align_frames(
    frames: list[Any],
    mode: str,
    canvas_size: tuple[int, int] | None,
    padding: int,
    threshold: int,
    Image: Any,
) -> tuple[list[Any], list[dict[str, Any]]]:
    if mode == "none" and canvas_size is None and padding == 0:
        return frames, [
            {"source_bbox": list(alpha_bbox(frame, threshold)) if alpha_bbox(frame, threshold) else None,
             "paste": [0, 0],
             "output_size": list(frame.size)}
            for frame in frames
        ]

    cropped: list[Any] = []
    source_boxes: list[list[int] | None] = []
    for frame in frames:
        content, source_bbox = crop_content(frame, threshold, Image)
        cropped.append(content)
        source_boxes.append(source_bbox)
    common_baseline = max(
        (source_bbox[3] - 1 for source_bbox in source_boxes if source_bbox),
        default=0,
    )
    baseline_heights = [
        content.height
        + (
            common_baseline - (source_bbox[3] - 1)
            if source_bbox is not None
            else 0
        )
        for content, source_bbox in zip(cropped, source_boxes)
    ]
    canvas = choose_canvas(
        cropped,
        canvas_size,
        padding,
        max(baseline_heights) if mode == "baseline" else None,
    )

    outputs: list[Any] = []
    placements: list[dict[str, Any]] = []
    for content, source_bbox in zip(cropped, source_boxes):
        if mode == "none":
            x = padding
            y = padding
        elif mode == "center":
            x = (canvas[0] - content.width) // 2
            y = (canvas[1] - content.height) // 2
        else:
            centroid = alpha_centroid(content, threshold)
            center_x = centroid[0] if centroid else (content.width - 1) / 2
            x = round(canvas[0] / 2 - center_x)
            if mode == "baseline":
                baseline_offset = (
                    common_baseline - (source_bbox[3] - 1)
                    if source_bbox is not None
                    else 0
                )
                y = canvas[1] - padding - baseline_offset - content.height
            else:
                baseline_offset = None
                center_y = centroid[1] if centroid else (content.height - 1) / 2
                y = round(canvas[1] / 2 - center_y)
        if mode != "baseline":
            baseline_offset = None
        if x < 0 or y < 0 or x + content.width > canvas[0] or y + content.height > canvas[1]:
            raise ValueError(
                f"aligned content does not fit canvas {canvas[0]}x{canvas[1]}; "
                "increase --cell-size or padding"
            )
        output = Image.new("RGBA", canvas, (0, 0, 0, 0))
        output.alpha_composite(content, (x, y))
        outputs.append(output)
        placements.append(
            {
                "source_bbox": source_bbox,
                "paste": [x, y],
                "output_size": list(canvas),
                "source_baseline_offset": baseline_offset,
            }
        )
    return outputs, placements


def pack_strip(frames: list[Any], Image: Any) -> Any:
    cell_width = max(frame.width for frame in frames)
    cell_height = max(frame.height for frame in frames)
    strip = Image.new("RGBA", (cell_width * len(frames), cell_height), (0, 0, 0, 0))
    for index, frame in enumerate(frames):
        x = index * cell_width + (cell_width - frame.width) // 2
        y = (cell_height - frame.height) // 2
        strip.alpha_composite(frame, (x, y))
    return strip


def ensure_writable(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise ValueError(f"output exists (use --force): {path}")
    path.parent.mkdir(parents=True, exist_ok=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Split a horizontal sprite strip using alpha projection and DP."
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--method", choices=("projection-dp", "equal"), default="projection-dp")
    parser.add_argument("--alpha-threshold", type=int, default=10)
    parser.add_argument(
        "--smooth-radius",
        type=int,
        help="Projection smoothing radius. Default: adaptive from strip width.",
    )
    parser.add_argument("--width-weight", type=float, default=0.0015)
    parser.add_argument("--min-width-ratio", type=float, default=0.45)
    parser.add_argument("--align", choices=("none", "center", "centroid", "baseline"), default="baseline")
    parser.add_argument("--cell-size", type=parse_size)
    parser.add_argument("--padding", type=int, default=0)
    parser.add_argument("--prefix", default="frame")
    parser.add_argument("--sheet-output", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.frames < 1:
        print("error: --frames must be positive", file=sys.stderr)
        return 2
    if (
        not 1 <= args.alpha_threshold <= 255
        or (args.smooth_radius is not None and args.smooth_radius < 0)
        or args.padding < 0
        or args.width_weight < 0
        or not 0 < args.min_width_ratio <= 1
    ):
        print("error: invalid smoothing, padding, or DP parameter", file=sys.stderr)
        return 2

    Image = _load_pillow()
    try:
        with Image.open(args.input) as source:
            strip = source.convert("RGBA")
        if strip.width < args.frames:
            raise ValueError("strip width is smaller than the requested frame count")
        smoothing_radius = args.smooth_radius
        if smoothing_radius is None:
            smoothing_radius = max(3, strip.width // 220) // 2
        projection = smooth(alpha_projection(strip), smoothing_radius)
        if args.method == "equal":
            equal = equal_boundaries(strip.width, args.frames)
            spans = [
                (equal[index], equal[index + 1])
                for index in range(args.frames)
            ]
            natural_count = args.frames
        else:
            spans, natural_count = segment_strip(
                projection,
                args.frames,
                args.width_weight,
                args.min_width_ratio,
            )
        if not spans:
            raise ValueError("no usable sprite content was detected")
        raw_frames = [
            strip.crop((start, 0, end, strip.height))
            for start, end in spans
        ]
        frames, placements = align_frames(
            raw_frames,
            args.align,
            args.cell_size,
            args.padding,
            args.alpha_threshold,
            Image,
        )

        args.output_dir.mkdir(parents=True, exist_ok=True)
        digits = max(2, len(str(len(frames) - 1)))
        frame_paths = [
            args.output_dir / f"{args.prefix}_{index:0{digits}d}.png"
            for index in range(len(frames))
        ]
        for output in frame_paths:
            ensure_writable(output, args.force)
        if args.sheet_output:
            ensure_writable(args.sheet_output, args.force)
        if args.manifest:
            ensure_writable(args.manifest, args.force)

        for frame, output in zip(frames, frame_paths):
            frame.save(output)
        if args.sheet_output:
            pack_strip(frames, Image).save(args.sheet_output)

        contiguous = (
            spans[0][0] == 0
            and spans[-1][1] == strip.width
            and all(spans[index][1] == spans[index + 1][0] for index in range(len(spans) - 1))
        )
        boundaries = [spans[0][0], *(end for _, end in spans)] if contiguous else None
        manifest = {
            "schema": "generic-image-generation-rules.sprite-strip-slice/v2",
            "input": str(args.input),
            "input_size": list(strip.size),
            "method": args.method,
            "boundaries": boundaries,
            "spans": [list(span) for span in spans],
            "expected_frame_count": args.frames,
            "natural_frame_count": natural_count,
            "output_frame_count": len(frames),
            "alignment": args.align,
            "warnings": (
                []
                if natural_count == args.frames
                else [
                    f"detected {natural_count} natural poses; expected {args.frames}"
                ]
            ),
            "frames": [
                {
                    "index": index,
                    "source_rect": [
                        spans[index][0],
                        0,
                        spans[index][1] - spans[index][0],
                        strip.height,
                    ],
                    "output": str(frame_paths[index]),
                    **placements[index],
                }
                for index in range(len(frames))
            ],
        }
        if args.manifest:
            args.manifest.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        else:
            print(json.dumps(manifest, indent=2, ensure_ascii=False))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extract an ordered image sequence from a video with FFmpeg."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import statistics
import subprocess
import sys
import tempfile
from typing import Any, Iterable


def die(message: str, code: int = 2) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def parse_time(raw: str) -> float:
    value = raw.strip()
    try:
        if ":" not in value:
            seconds = float(value)
        else:
            parts = value.split(":")
            if len(parts) > 3:
                raise ValueError
            numbers = [float(part) for part in parts]
            seconds = 0.0
            for number in numbers:
                seconds = seconds * 60.0 + number
    except ValueError:
        die(f"invalid time value: {raw!r}; use seconds or HH:MM:SS.mmm")
    if not math.isfinite(seconds) or seconds < 0:
        die(f"time must be a finite non-negative value: {raw!r}")
    return seconds


def parse_rate(raw: str | None) -> float | None:
    if not raw or raw in {"0/0", "N/A"}:
        return None
    try:
        numerator, denominator = raw.split("/", 1)
        value = float(numerator) / float(denominator)
    except (ValueError, ZeroDivisionError):
        return None
    return value if math.isfinite(value) and value > 0 else None


def resolve_binary(value: str, label: str) -> str:
    candidate = Path(value)
    if candidate.parent != Path(".") or candidate.is_absolute():
        if not candidate.is_file():
            die(f"{label} binary not found: {candidate}")
        return str(candidate)
    resolved = shutil.which(value)
    if not resolved:
        die(f"{label} was not found on PATH; pass --{label}-bin PATH")
    return resolved


def run(command: list[str], label: str) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        die(f"could not run {label}: {exc}", 1)
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        die(f"{label} failed" + (f":\n{detail}" if detail else ""), 1)


def probe_video(ffprobe: str, source: Path) -> dict[str, Any]:
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,avg_frame_rate,r_frame_rate,duration,nb_frames:format=duration",
            "-of",
            "json",
            str(source),
        ],
        "ffprobe",
    )
    try:
        payload = json.loads(result.stdout)
        stream = payload["streams"][0]
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        die("ffprobe did not return a readable video stream", 1)

    duration_raw = stream.get("duration") or payload.get("format", {}).get("duration")
    try:
        duration = float(duration_raw) if duration_raw is not None else None
    except (TypeError, ValueError):
        duration = None
    if duration is not None and (not math.isfinite(duration) or duration <= 0):
        duration = None

    return {
        "width": int(stream["width"]),
        "height": int(stream["height"]),
        "duration": duration,
        "avg_fps": parse_rate(stream.get("avg_frame_rate")),
        "nominal_fps": parse_rate(stream.get("r_frame_rate")),
        "declared_frames": int(stream["nb_frames"])
        if str(stream.get("nb_frames", "")).isdigit()
        else None,
    }


def probe_frame_times(ffprobe: str, source: Path) -> list[tuple[float, float | None]]:
    result = run(
        [
            ffprobe,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "frame=best_effort_timestamp_time,pkt_duration_time",
            "-of",
            "json",
            str(source),
        ],
        "ffprobe frame timing",
    )
    try:
        frames = json.loads(result.stdout).get("frames", [])
    except json.JSONDecodeError:
        return []
    output: list[tuple[float, float | None]] = []
    for frame in frames:
        try:
            timestamp = float(frame["best_effort_timestamp_time"])
        except (KeyError, TypeError, ValueError):
            continue
        duration = None
        try:
            raw_duration = float(frame.get("pkt_duration_time"))
            if math.isfinite(raw_duration) and raw_duration > 0:
                duration = raw_duration
        except (TypeError, ValueError):
            pass
        if math.isfinite(timestamp):
            output.append((timestamp, duration))
    return output


def output_options(image_format: str) -> list[str]:
    if image_format == "png":
        return ["-pix_fmt", "rgba"]
    if image_format == "webp":
        return ["-lossless", "1"]
    return ["-q:v", "2"]


def sequence_command(
    ffmpeg: str,
    source: Path,
    pattern: Path,
    image_format: str,
    start: float,
    end: float,
    fps: float | None,
) -> list[str]:
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-i", str(source)]
    if start > 0:
        command += ["-ss", f"{start:.9f}"]
    command += ["-t", f"{end - start:.9f}", "-map", "0:v:0", "-an", "-sn", "-dn"]
    if fps is not None:
        command += ["-vf", f"fps={fps:.12g}:start_time=0"]
    else:
        command += ["-fps_mode", "passthrough"]
    command += ["-start_number", "0", *output_options(image_format), str(pattern)]
    return command


def extract_one(
    ffmpeg: str,
    source: Path,
    destination: Path,
    image_format: str,
    timestamp: float,
) -> None:
    run(
        [
            ffmpeg,
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-ss",
            f"{timestamp:.9f}",
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-an",
            "-sn",
            "-dn",
            *output_options(image_format),
            str(destination),
        ],
        f"ffmpeg extraction at {timestamp:.6f}s",
    )
    if not destination.is_file():
        die(f"no video frame exists at {timestamp:.6f}s", 1)


def evenly_counted_times(
    start: float,
    end: float,
    count: int,
    position: str,
    source_fps: float | None,
) -> list[float]:
    span = end - start
    if position == "centers":
        return [start + span * (index + 0.5) / count for index in range(count)]
    if count == 1:
        return [start]
    final_margin = min(1.0 / (source_fps or 30.0), span / (count * 2.0))
    last = max(start, end - final_margin)
    return [start + (last - start) * index / (count - 1) for index in range(count)]


def select_unique_source_times(
    available: list[float], targets: list[float], label: str
) -> list[float]:
    if len(available) < len(targets):
        die(
            f"{label} requests {len(targets)} distinct frames, but only "
            f"{len(available)} source frames are available in the selected range"
        )
    selected: list[float] = []
    previous_index = -1
    for target_index, target in enumerate(targets):
        first = previous_index + 1
        last = len(available) - (len(targets) - target_index)
        index = min(range(first, last + 1), key=lambda value: abs(available[value] - target))
        selected.append(available[index])
        previous_index = index
    return selected


def inferred_durations(timestamps: list[float], fallback: float | None = None) -> list[float | None]:
    if not timestamps:
        return []
    if len(timestamps) == 1:
        return [fallback]
    deltas = [timestamps[index + 1] - timestamps[index] for index in range(len(timestamps) - 1)]
    positive = [value for value in deltas if value > 0]
    last = statistics.median(positive) if positive else fallback
    return [*deltas, last]


def apply_background_removal(args: argparse.Namespace, source: Path, destination: Path) -> None:
    remover = Path(__file__).with_name("remove_chroma_key.py")
    command = [
        sys.executable,
        str(remover),
        "--input",
        str(source),
        "--out",
        str(destination),
        "--auto-key",
        args.auto_key,
        "--key-color",
        args.key_color,
        "--soft-matte",
        "--transparent-threshold",
        "12",
        "--opaque-threshold",
        "220",
        "--despill",
        "--edge-contract",
        str(args.edge_contract),
        "--edge-feather",
        str(args.edge_feather),
    ]
    run(command, f"background removal for {source.name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Extract ordered still frames from a video and write timing metadata."
    )
    parser.add_argument("input", type=Path, help="Source video file.")
    parser.add_argument("output_dir", type=Path, help="Directory for extracted frames.")
    sampling = parser.add_mutually_exclusive_group(required=True)
    sampling.add_argument("--fps", type=float, help="Extract at a fixed frames-per-second rate.")
    sampling.add_argument("--count", type=int, help="Extract exactly this many frames.")
    sampling.add_argument(
        "--timestamps",
        help="Comma-separated absolute source times in seconds or HH:MM:SS.mmm.",
    )
    sampling.add_argument("--every-frame", action="store_true", help="Extract every source frame.")
    parser.add_argument("--start", default="0", help="Range start in seconds or HH:MM:SS.mmm.")
    parser.add_argument("--end", help="Exclusive range end in seconds or HH:MM:SS.mmm.")
    parser.add_argument(
        "--count-position",
        choices=["centers", "endpoints"],
        default="centers",
        help="How --count places samples across the selected range.",
    )
    parser.add_argument("--format", choices=["png", "webp", "jpg"], default="png")
    parser.add_argument("--prefix", default="frame", help="Output filename prefix.")
    parser.add_argument("--digits", type=int, default=4, help="Frame-number zero padding.")
    parser.add_argument("--manifest", default="frames.json", help="Manifest filename.")
    parser.add_argument("--no-manifest", action="store_true", help="Do not write a manifest.")
    parser.add_argument("--force", action="store_true", help="Replace colliding outputs.")
    parser.add_argument("--ffmpeg-bin", default="ffmpeg", help="FFmpeg executable name or path.")
    parser.add_argument("--ffprobe-bin", default="ffprobe", help="FFprobe executable name or path.")
    parser.add_argument(
        "--remove-background",
        action="store_true",
        help="Convert a flat chroma-key background to alpha on every frame.",
    )
    parser.add_argument(
        "--auto-key",
        choices=["none", "corners", "border"],
        default="border",
        help="Background-key sampling mode.",
    )
    parser.add_argument("--key-color", default="#00ff00", help="Key color when auto-key is none.")
    parser.add_argument("--edge-contract", type=int, default=0, help="Contract alpha by 0-16 px.")
    parser.add_argument("--edge-feather", type=float, default=0.0, help="Blur alpha by 0-64 px.")
    return parser


def validate_args(args: argparse.Namespace) -> None:
    if not args.input.is_file():
        die(f"input video not found: {args.input}")
    if args.fps is not None and (not math.isfinite(args.fps) or args.fps <= 0):
        die("--fps must be a finite value greater than zero")
    if args.count is not None and args.count <= 0:
        die("--count must be greater than zero")
    if args.digits < 1 or args.digits > 12:
        die("--digits must be between 1 and 12")
    if not args.prefix or any(character in args.prefix for character in "\\/\0"):
        die("--prefix must be a non-empty filename component")
    if args.remove_background and args.format == "jpg":
        die("background removal requires PNG or WebP output")
    if not 0 <= args.edge_contract <= 16:
        die("--edge-contract must be between 0 and 16")
    if not 0 <= args.edge_feather <= 64:
        die("--edge-feather must be between 0 and 64")
    if Path(args.manifest).name != args.manifest:
        die("--manifest must be a filename inside the output directory")
    if args.timestamps and (args.start != "0" or args.end is not None):
        die("--timestamps cannot be combined with --start or --end")


def copy_outputs(
    staged: Iterable[Path], output_dir: Path, force: bool
) -> list[Path]:
    staged_list = list(staged)
    destinations = [output_dir / path.name for path in staged_list]
    collisions = [path for path in destinations if path.exists()]
    if collisions and not force:
        preview = ", ".join(str(path) for path in collisions[:3])
        die(f"output already exists: {preview}" + (" ..." if len(collisions) > 3 else ""))
    output_dir.mkdir(parents=True, exist_ok=True)
    for source, destination in zip(staged_list, destinations):
        shutil.copy2(source, destination)
    return destinations


def main() -> int:
    args = build_parser().parse_args()
    validate_args(args)
    ffmpeg = resolve_binary(args.ffmpeg_bin, "ffmpeg")
    ffprobe = resolve_binary(args.ffprobe_bin, "ffprobe")
    source = args.input.resolve()
    output_dir = args.output_dir.resolve()
    metadata = probe_video(ffprobe, source)

    start = parse_time(args.start)
    end = parse_time(args.end) if args.end else metadata["duration"]
    if args.timestamps:
        requested_timestamps = [
            parse_time(value) for value in args.timestamps.split(",") if value.strip()
        ]
        if not requested_timestamps:
            die("--timestamps must contain at least one time")
        if requested_timestamps != sorted(requested_timestamps) or len(
            requested_timestamps
        ) != len(set(requested_timestamps)):
            die("--timestamps must be unique and in playback order")
        if metadata["duration"] is not None and requested_timestamps[-1] >= metadata["duration"]:
            die(
                f"timestamp {requested_timestamps[-1]:.6f}s is outside the "
                f"{metadata['duration']:.6f}s clip"
            )
        mode = "timestamps"
        start, end = requested_timestamps[0], requested_timestamps[-1]
        timestamps: list[float] = []
    else:
        if end is None:
            die("could not determine video duration; pass --end")
        if start >= end:
            die("--start must be earlier than --end")
        if metadata["duration"] is not None and end > metadata["duration"] + 1e-6:
            die(f"--end exceeds the {metadata['duration']:.6f}s clip duration")
        requested_timestamps = []
        timestamps = []
        mode = "fps" if args.fps is not None else "count" if args.count is not None else "every-frame"

    with tempfile.TemporaryDirectory(prefix="slice-video-frames-") as temp_name:
        temp_dir = Path(temp_name)
        raw_dir = temp_dir / "raw"
        final_dir = temp_dir / "final"
        raw_dir.mkdir()
        final_dir.mkdir()
        pattern = raw_dir / f"{args.prefix}_%0{args.digits}d.{args.format}"

        if mode == "count":
            targets = evenly_counted_times(
                start,
                end,
                args.count,
                args.count_position,
                metadata["avg_fps"] or metadata["nominal_fps"],
            )
            available = [
                timestamp
                for timestamp, _duration in probe_frame_times(ffprobe, source)
                if start - 1e-9 <= timestamp < end - 1e-9
            ]
            timestamps = select_unique_source_times(available, targets, "--count")
            for index, timestamp in enumerate(timestamps):
                destination = raw_dir / f"{args.prefix}_{index:0{args.digits}d}.{args.format}"
                extract_one(ffmpeg, source, destination, args.format, timestamp)
        elif mode == "timestamps":
            available = [timestamp for timestamp, _duration in probe_frame_times(ffprobe, source)]
            timestamps = select_unique_source_times(
                available, requested_timestamps, "--timestamps"
            )
            for index, timestamp in enumerate(timestamps):
                destination = raw_dir / f"{args.prefix}_{index:0{args.digits}d}.{args.format}"
                extract_one(ffmpeg, source, destination, args.format, timestamp)
        else:
            run(
                sequence_command(
                    ffmpeg,
                    source,
                    pattern,
                    args.format,
                    start,
                    end,
                    args.fps if mode == "fps" else None,
                ),
                "ffmpeg frame extraction",
            )

        raw_frames = sorted(raw_dir.glob(f"{args.prefix}_*.{args.format}"))
        if not raw_frames:
            die("FFmpeg produced no frames for the requested range", 1)
        if mode == "count" and len(raw_frames) != args.count:
            die(f"expected {args.count} frames but FFmpeg produced {len(raw_frames)}", 1)
        if mode == "timestamps" and len(raw_frames) != len(timestamps):
            die(f"expected {len(timestamps)} frames but FFmpeg produced {len(raw_frames)}", 1)

        if mode == "fps":
            timestamps = [start + index / args.fps for index in range(len(raw_frames))]
            durations: list[float | None] = [1.0 / args.fps] * len(raw_frames)
        elif mode == "every-frame":
            probed = [
                (timestamp, duration)
                for timestamp, duration in probe_frame_times(ffprobe, source)
                if start - 1e-9 <= timestamp < end - 1e-9
            ]
            if len(probed) == len(raw_frames):
                timestamps = [item[0] for item in probed]
                durations = [item[1] for item in probed]
            else:
                source_fps = metadata["avg_fps"] or metadata["nominal_fps"]
                timestamps = [start + index / source_fps for index in range(len(raw_frames))] if source_fps else []
                durations = [1.0 / source_fps] * len(raw_frames) if source_fps else [None] * len(raw_frames)
        elif mode == "count":
            durations = [(end - start) / len(raw_frames)] * len(raw_frames)
        else:
            durations = inferred_durations(timestamps)

        if len(timestamps) != len(raw_frames):
            timestamps = [start + index for index in range(len(raw_frames))]
            durations = [None] * len(raw_frames)

        staged_frames: list[Path] = []
        if args.remove_background:
            for raw_frame in raw_frames:
                destination = final_dir / raw_frame.name
                apply_background_removal(args, raw_frame, destination)
                staged_frames.append(destination)
        else:
            staged_frames = raw_frames

        manifest_path = output_dir / args.manifest
        if not args.no_manifest and manifest_path.exists() and not args.force:
            die(f"manifest already exists: {manifest_path}")
        outputs = copy_outputs(staged_frames, output_dir, args.force)

        manifest = {
            "schema_version": 1,
            "source": str(source),
            "sampling": {
                "mode": mode,
                "start_seconds": start,
                "end_seconds": end,
                "requested_fps": args.fps,
                "requested_count": args.count,
                "count_position": args.count_position if mode == "count" else None,
                "requested_timestamps_seconds": requested_timestamps
                if mode == "timestamps"
                else None,
            },
            "source_video": {
                "duration_seconds": metadata["duration"],
                "width": metadata["width"],
                "height": metadata["height"],
                "average_fps": metadata["avg_fps"],
                "nominal_fps": metadata["nominal_fps"],
            },
            "output": {
                "format": args.format,
                "canvas_width": metadata["width"],
                "canvas_height": metadata["height"],
                "frame_count": len(outputs),
                "alpha_contract": "straight-alpha" if args.remove_background else "source-or-opaque",
            },
            "frames": [
                {
                    "index": index,
                    "path": output.name,
                    "timestamp_seconds": round(timestamps[index], 9),
                    "duration_seconds": round(durations[index], 9)
                    if durations[index] is not None
                    else None,
                }
                for index, output in enumerate(outputs)
            ],
        }
        if not args.no_manifest:
            output_dir.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            print(f"Wrote manifest: {manifest_path}")
        print(f"Wrote {len(outputs)} frame(s) to {output_dir}")
        for output in outputs:
            print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

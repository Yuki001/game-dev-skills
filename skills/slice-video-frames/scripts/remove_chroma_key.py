#!/usr/bin/env python3
"""Convert a flat chroma-key image background to straight alpha."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
from statistics import median
import sys
from typing import Tuple


Color = Tuple[int, int, int]
ALPHA_NOISE_FLOOR = 8


def die(message: str, code: int = 2) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def load_pillow():
    try:
        from PIL import Image, ImageFilter
    except ImportError:
        die("Pillow is required for chroma-key removal. Install the 'pillow' package.", 1)
    return Image, ImageFilter


def parse_key_color(raw: str) -> Color:
    match = re.fullmatch(r"#?([0-9a-fA-F]{6})", raw.strip())
    if not match:
        die("--key-color must be a hex RGB value such as #00ff00")
    value = match.group(1)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def clamp(value: float) -> int:
    return max(0, min(255, int(round(value))))


def channel_distance(first: Color, second: Color) -> int:
    return max(abs(first[index] - second[index]) for index in range(3))


def spill_channels(key: Color) -> list[int]:
    peak = max(key)
    if peak < 128:
        return []
    return [index for index, value in enumerate(key) if value >= peak - 16 and value >= 128]


def key_dominance(rgb: Color, key: Color) -> float:
    spill = spill_channels(key)
    if not spill:
        return 0.0
    channels = [float(value) for value in rgb]
    other = [index for index in range(3) if index not in spill]
    key_strength = min(channels[index] for index in spill)
    other_strength = max((channels[index] for index in other), default=0.0)
    return key_strength - other_strength


def dominance_alpha(rgb: Color, key: Color) -> int:
    spill = spill_channels(key)
    dominance = key_dominance(rgb, key)
    if not spill or dominance <= 0:
        return 255
    other = [index for index in range(3) if index not in spill]
    other_strength = max((float(rgb[index]) for index in other), default=0.0)
    denominator = max(1.0, float(max(key)) - other_strength)
    return clamp(255.0 * (1.0 - min(1.0, dominance / denominator)))


def soft_alpha(distance: int, transparent: float, opaque: float) -> int:
    if distance <= transparent:
        return 0
    if distance >= opaque:
        return 255
    ratio = (distance - transparent) / (opaque - transparent)
    smooth = ratio * ratio * (3.0 - 2.0 * ratio)
    return clamp(255.0 * smooth)


def cleanup_spill(rgb: Color, key: Color, alpha: int) -> Color:
    if alpha >= 252:
        return rgb
    spill = spill_channels(key)
    other = [index for index in range(3) if index not in spill]
    if not spill or not other:
        return rgb
    channels = [float(value) for value in rgb]
    cap = max(0.0, max(channels[index] for index in other) - 1.0)
    for index in spill:
        channels[index] = min(channels[index], cap)
    return clamp(channels[0]), clamp(channels[1]), clamp(channels[2])


def sample_key(image, mode: str) -> Color:
    width, height = image.size
    pixels = image.load()
    samples: list[Color] = []
    if mode == "corners":
        patch = max(1, min(width, height, 12))
        boxes = [
            (0, 0, patch, patch),
            (width - patch, 0, width, patch),
            (0, height - patch, patch, height),
            (width - patch, height - patch, width, height),
        ]
        for left, top, right, bottom in boxes:
            for y in range(top, bottom):
                for x in range(left, right):
                    samples.append(tuple(pixels[x, y][:3]))
    else:
        band = max(1, min(width, height, 6))
        step = max(1, min(width, height) // 256)
        for x in range(0, width, step):
            for y in range(band):
                samples.append(tuple(pixels[x, y][:3]))
                samples.append(tuple(pixels[x, height - 1 - y][:3]))
        for y in range(0, height, step):
            for x in range(band):
                samples.append(tuple(pixels[x, y][:3]))
                samples.append(tuple(pixels[width - 1 - x, y][:3]))
    if not samples:
        die("could not sample a key color from the image border", 1)
    return tuple(int(round(median(sample[index] for sample in samples))) for index in range(3))


def apply_matte(image, args: argparse.Namespace, key: Color) -> None:
    pixels = image.load()
    width, height = image.size
    for y in range(height):
        for x in range(width):
            red, green, blue, source_alpha = pixels[x, y]
            rgb = red, green, blue
            distance = channel_distance(rgb, key)
            key_like = distance <= 32 or key_dominance(rgb, key) >= 16.0
            if args.soft_matte and key_like:
                alpha = min(
                    soft_alpha(distance, args.transparent_threshold, args.opaque_threshold),
                    dominance_alpha(rgb, key),
                )
            else:
                alpha = 0 if distance <= args.tolerance else 255
            alpha = int(round(alpha * source_alpha / 255.0))
            if 0 < alpha <= ALPHA_NOISE_FLOOR:
                alpha = 0
            if alpha == 0:
                pixels[x, y] = 0, 0, 0, 0
            elif args.despill and key_like:
                red, green, blue = cleanup_spill(rgb, key, alpha)
                pixels[x, y] = red, green, blue, alpha
            else:
                pixels[x, y] = red, green, blue, alpha


def alpha_counts(image) -> tuple[int, int, int]:
    total = transparent = partial = 0
    for _red, _green, _blue, alpha in image.getdata():
        total += 1
        if alpha == 0:
            transparent += 1
        elif alpha < 255:
            partial += 1
    return total, transparent, partial


def validate(args: argparse.Namespace) -> None:
    source = Path(args.input)
    output = Path(args.out)
    if not source.is_file():
        die(f"input image not found: {source}")
    if output.suffix.lower() not in {".png", ".webp"}:
        die("--out must end in .png or .webp")
    if output.exists() and not args.force:
        die(f"output already exists: {output}; pass --force to replace it")
    if not 0 <= args.tolerance <= 255:
        die("--tolerance must be between 0 and 255")
    if not 0 <= args.transparent_threshold <= 255:
        die("--transparent-threshold must be between 0 and 255")
    if not 0 <= args.opaque_threshold <= 255:
        die("--opaque-threshold must be between 0 and 255")
    if args.soft_matte and args.transparent_threshold >= args.opaque_threshold:
        die("--transparent-threshold must be lower than --opaque-threshold")
    if not 0 <= args.edge_contract <= 16:
        die("--edge-contract must be between 0 and 16")
    if not 0 <= args.edge_feather <= 64:
        die("--edge-feather must be between 0 and 64")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Remove a solid chroma-key background and write straight alpha."
    )
    parser.add_argument("--input", required=True, help="Source image.")
    parser.add_argument("--out", required=True, help="Output PNG or WebP.")
    parser.add_argument("--key-color", default="#00ff00", help="Hex RGB key color.")
    parser.add_argument("--tolerance", type=int, default=12, help="Hard-key tolerance, 0-255.")
    parser.add_argument(
        "--auto-key",
        choices=["none", "corners", "border"],
        default="none",
        help="Sample the key from corners or the full border.",
    )
    parser.add_argument("--soft-matte", action="store_true", help="Use a smooth alpha ramp.")
    parser.add_argument("--transparent-threshold", type=float, default=12.0)
    parser.add_argument("--opaque-threshold", type=float, default=96.0)
    parser.add_argument("--despill", action="store_true", help="Reduce key-color edge spill.")
    parser.add_argument("--edge-contract", type=int, default=0, help="Contract alpha by 0-16 px.")
    parser.add_argument("--edge-feather", type=float, default=0.0, help="Blur alpha by 0-64 px.")
    parser.add_argument("--force", action="store_true", help="Replace an existing output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    validate(args)
    Image, ImageFilter = load_pillow()
    with Image.open(args.input) as source:
        image = source.convert("RGBA")
    key = sample_key(image, args.auto_key) if args.auto_key != "none" else parse_key_color(args.key_color)
    apply_matte(image, args, key)

    if args.edge_contract:
        alpha = image.getchannel("A")
        for _ in range(args.edge_contract):
            alpha = alpha.filter(ImageFilter.MinFilter(3))
        image.putalpha(alpha)
    if args.edge_feather:
        image.putalpha(image.getchannel("A").filter(ImageFilter.GaussianBlur(args.edge_feather)))

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, format="PNG" if output.suffix.lower() == ".png" else "WEBP")
    total, transparent, partial = alpha_counts(image)
    print(f"Wrote {output}")
    print(f"Key color: #{key[0]:02x}{key[1]:02x}{key[2]:02x}")
    print(f"Transparent pixels: {transparent}/{total}")
    print(f"Partially transparent pixels: {partial}/{total}")
    if transparent == 0:
        print("Warning: no pixels became fully transparent.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

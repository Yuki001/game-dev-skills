#!/usr/bin/env python3
"""Inspect PNG image metadata, alpha, padding, borders, and sheet geometry."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPES = {
    0: ("grayscale", 1),
    2: ("rgb", 3),
    3: ("indexed", 1),
    4: ("grayscale_alpha", 2),
    6: ("rgba", 4),
}
PNG_ALLOWED_BIT_DEPTHS = {
    0: {1, 2, 4, 8, 16},
    2: {8, 16},
    3: {1, 2, 4, 8},
    4: {8, 16},
    6: {8, 16},
}
SIZE_RE = re.compile(r"^\s*(\d+)\s*[xX×]\s*(\d+)\s*$")


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def _unfilter(raw: bytes, height: int, row_bytes: int, bpp: int) -> list[bytes]:
    expected_size = height * (row_bytes + 1)
    if len(raw) != expected_size:
        raise ValueError(
            f"PNG scanline data has {len(raw)} bytes; expected {expected_size}"
        )
    rows: list[bytes] = []
    offset = 0
    prior = bytearray(row_bytes)
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        source = raw[offset : offset + row_bytes]
        offset += row_bytes
        if len(source) != row_bytes:
            raise ValueError("truncated PNG scanline data")
        row = bytearray(row_bytes)
        for i, value in enumerate(source):
            left = row[i - bpp] if i >= bpp else 0
            up = prior[i]
            upper_left = prior[i - bpp] if i >= bpp else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                predictor = _paeth(left, up, upper_left)
            else:
                raise ValueError(f"unsupported PNG filter type {filter_type}")
            row[i] = (value + predictor) & 0xFF
        rows.append(bytes(row))
        prior = row
    return rows


def _sample_indices(row: bytes, width: int, bit_depth: int) -> list[int]:
    if bit_depth == 8:
        return list(row[:width])
    mask = (1 << bit_depth) - 1
    result: list[int] = []
    for byte in row:
        for shift in range(8 - bit_depth, -1, -bit_depth):
            result.append((byte >> shift) & mask)
            if len(result) == width:
                return result
    return result


def _alpha_values(
    rows: list[bytes],
    width: int,
    color_type: int,
    bit_depth: int,
    trns: bytes | None,
) -> list[list[int]] | None:
    if bit_depth != 8 and color_type != 3:
        return None
    output: list[list[int]] = []
    if color_type == 6:
        for row in rows:
            output.append([row[x * 4 + 3] for x in range(width)])
    elif color_type == 4:
        for row in rows:
            output.append([row[x * 2 + 1] for x in range(width)])
    elif color_type == 3 and trns is not None:
        palette_alpha = list(trns)
        for row in rows:
            indices = _sample_indices(row, width, bit_depth)
            output.append(
                [palette_alpha[i] if i < len(palette_alpha) else 255 for i in indices]
            )
    elif color_type == 0 and trns is not None and len(trns) >= 2:
        transparent = struct.unpack(">H", trns[:2])[0] & 0xFF
        for row in rows:
            output.append([0 if row[x] == transparent else 255 for x in range(width)])
    elif color_type == 2 and trns is not None and len(trns) >= 6:
        rgb16 = struct.unpack(">HHH", trns[:6])
        transparent = tuple(value & 0xFF for value in rgb16)
        for row in rows:
            output.append(
                [
                    0 if tuple(row[x * 3 : x * 3 + 3]) == transparent else 255
                    for x in range(width)
                ]
            )
    else:
        return None
    return output


def _read_png_chunks(data: bytes) -> tuple[dict[str, list[bytes]], list[str]]:
    chunks: dict[str, list[bytes]] = {}
    sequence: list[str] = []
    offset = len(PNG_SIGNATURE)
    saw_iend = False
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("truncated PNG chunk header")
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        name_bytes = data[offset + 4 : offset + 8]
        if not re.fullmatch(rb"[A-Za-z]{4}", name_bytes):
            raise ValueError("invalid PNG chunk type")
        name = name_bytes.decode("ascii")
        payload_start = offset + 8
        payload_end = payload_start + length
        chunk_end = payload_end + 4
        if chunk_end > len(data):
            raise ValueError(f"truncated PNG {name} chunk")
        payload = data[payload_start:payload_end]
        expected_crc = struct.unpack(">I", data[payload_end:chunk_end])[0]
        actual_crc = zlib.crc32(name_bytes + payload) & 0xFFFFFFFF
        if actual_crc != expected_crc:
            raise ValueError(f"PNG {name} chunk CRC mismatch")
        if saw_iend:
            raise ValueError("PNG contains data after IEND")
        chunks.setdefault(name, []).append(payload)
        sequence.append(name)
        offset = chunk_end
        if name == "IEND":
            saw_iend = True

    if not sequence or sequence[0] != "IHDR":
        raise ValueError("PNG must begin with IHDR")
    if len(chunks.get("IHDR", [])) != 1 or len(chunks["IHDR"][0]) != 13:
        raise ValueError("PNG must contain exactly one 13-byte IHDR chunk")
    if "IDAT" not in chunks:
        raise ValueError("PNG has no IDAT chunk")
    if len(chunks.get("IEND", [])) != 1 or chunks["IEND"][0]:
        raise ValueError("PNG must end with one empty IEND chunk")
    if sequence[-1] != "IEND":
        raise ValueError("PNG IEND chunk must be last")
    return chunks, sequence


def inspect_png(path: Path) -> dict:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid PNG signature")
    chunks, chunk_sequence = _read_png_chunks(data)
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", chunks["IHDR"][0]
    )
    if width < 1 or height < 1:
        raise ValueError("PNG dimensions must be positive")
    if color_type not in COLOR_TYPES:
        raise ValueError(f"unsupported PNG color type {color_type}")
    if bit_depth not in PNG_ALLOWED_BIT_DEPTHS[color_type]:
        raise ValueError(
            f"invalid PNG bit depth {bit_depth} for color type {color_type}"
        )
    if compression != 0 or filtering != 0 or interlace not in (0, 1):
        raise ValueError("unsupported or invalid PNG IHDR encoding fields")
    if color_type == 3 and "PLTE" not in chunks:
        raise ValueError("indexed PNG has no PLTE chunk")
    color_name, channels = COLOR_TYPES[color_type]
    trns = chunks.get("tRNS", [None])[0]
    has_alpha = color_type in (4, 6) or trns is not None
    decompressor = zlib.decompressobj()
    raw = decompressor.decompress(b"".join(chunks["IDAT"])) + decompressor.flush()
    if not decompressor.eof:
        raise ValueError("truncated PNG IDAT zlib stream")
    if decompressor.unused_data or decompressor.unconsumed_tail:
        raise ValueError("PNG IDAT contains trailing compressed data")
    result = {
        "path": str(path.resolve()),
        "format": "png",
        "width": width,
        "height": height,
        "bit_depth": bit_depth,
        "color_type": color_name,
        "has_alpha_channel": has_alpha,
        "interlaced": bool(interlace),
        "chunks": sorted(chunks),
        "chunk_sequence": chunk_sequence,
    }
    if interlace:
        result["alpha_analysis"] = {
            "available": False,
            "reason": "interlaced PNG alpha decoding is unavailable",
        }
        return result
    row_bytes = math.ceil(width * channels * bit_depth / 8)
    bpp = max(1, math.ceil(channels * bit_depth / 8))
    rows = _unfilter(raw, height, row_bytes, bpp)
    alpha = _alpha_values(rows, width, color_type, bit_depth, trns)
    if alpha is None:
        result["alpha_analysis"] = {
            "available": not has_alpha,
            "transparent_pixels": 0 if not has_alpha else None,
            "partial_alpha_pixels": 0 if not has_alpha else None,
            "opaque_pixels": width * height if not has_alpha else None,
            "reason": None if not has_alpha else "alpha decoding unavailable",
        }
        return result
    transparent = partial = opaque = 0
    xs: list[int] = []
    ys: list[int] = []
    border_transparent = 0
    border_total = 0
    for y, row in enumerate(alpha):
        for x, value in enumerate(row):
            if value == 0:
                transparent += 1
            elif value == 255:
                opaque += 1
                xs.append(x)
                ys.append(y)
            else:
                partial += 1
                xs.append(x)
                ys.append(y)
            if x in (0, width - 1) or y in (0, height - 1):
                border_total += 1
                border_transparent += int(value == 0)
    bbox = [min(xs), min(ys), max(xs) + 1, max(ys) + 1] if xs else None
    padding = None
    if bbox:
        left, top, right, bottom = bbox
        padding = {
            "left": left,
            "top": top,
            "right": width - right,
            "bottom": height - bottom,
        }
        padding["minimum"] = min(padding.values())
    result["alpha_analysis"] = {
        "available": True,
        "transparent_pixels": transparent,
        "partial_alpha_pixels": partial,
        "opaque_pixels": opaque,
        "transparent_fraction": transparent / (width * height),
        "nontransparent_bbox_xyxy": bbox,
        "transparent_padding": padding,
        "transparent_border_fraction": border_transparent / border_total,
    }
    return result


def _parse_size(value: str) -> tuple[int, int]:
    match = SIZE_RE.fullmatch(value)
    if not match:
        raise argparse.ArgumentTypeError("size must use WIDTHxHEIGHT, for example 512x512")
    width, height = (int(part) for part in match.groups())
    if width < 1 or height < 1:
        raise argparse.ArgumentTypeError("size dimensions must be positive")
    return width, height


def _parse_nonnegative_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be an integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("value must be non-negative")
    return number


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--expect-transparent", action="store_true")
    parser.add_argument("--expect-size", type=_parse_size, metavar="WIDTHxHEIGHT")
    parser.add_argument(
        "--expect-color-type",
        choices=sorted(name for name, _channels in COLOR_TYPES.values()),
    )
    parser.add_argument("--require-transparent-border", action="store_true")
    parser.add_argument("--require-partial-alpha", action="store_true")
    parser.add_argument("--min-padding", type=_parse_nonnegative_int, metavar="PIXELS")
    parser.add_argument("--cols", type=int)
    parser.add_argument("--rows", type=int)
    args = parser.parse_args()
    try:
        if args.image.suffix.lower() != ".png":
            raise ValueError("supported format: .png")
        result = inspect_png(args.image)
        failures: list[str] = []
        if args.expect_size and (result["width"], result["height"]) != args.expect_size:
            expected_width, expected_height = args.expect_size
            failures.append(
                f"expected {expected_width}x{expected_height}, "
                f"got {result['width']}x{result['height']}"
            )
        if args.expect_color_type and result.get("color_type") != args.expect_color_type:
            failures.append(
                f"expected color type {args.expect_color_type}, "
                f"got {result.get('color_type')}"
            )
        if args.expect_transparent:
            alpha = result.get("alpha_analysis", {})
            if not result.get("has_alpha_channel"):
                failures.append("asset has no alpha channel")
            elif not alpha.get("available"):
                failures.append("alpha pixels could not be verified")
            elif not alpha.get("transparent_pixels", 0):
                failures.append("asset contains no fully transparent pixels")
        if args.require_transparent_border:
            alpha = result.get("alpha_analysis", {})
            if not result.get("has_alpha_channel"):
                failures.append("asset has no alpha channel")
            elif not alpha.get("available"):
                failures.append("alpha pixels could not be verified")
            elif alpha.get("transparent_border_fraction") != 1.0:
                failures.append("not every border pixel is fully transparent")
        if args.require_partial_alpha:
            alpha = result.get("alpha_analysis", {})
            if not result.get("has_alpha_channel"):
                failures.append("asset has no alpha channel")
            elif not alpha.get("available"):
                failures.append("alpha pixels could not be verified")
            elif not alpha.get("partial_alpha_pixels", 0):
                failures.append("asset contains no partially transparent pixels")
        if args.min_padding is not None:
            alpha = result.get("alpha_analysis", {})
            padding = alpha.get("transparent_padding")
            if not result.get("has_alpha_channel"):
                failures.append("asset has no alpha channel")
            elif not alpha.get("available"):
                failures.append("alpha pixels could not be verified")
            elif padding is None:
                failures.append("asset contains no nontransparent pixels")
            else:
                result["padding_check"] = {
                    "required_minimum": args.min_padding,
                    "actual": padding,
                    "passed": padding["minimum"] >= args.min_padding,
                }
                if padding["minimum"] < args.min_padding:
                    failures.append(
                        f"minimum transparent padding is {padding['minimum']} px; "
                        f"expected at least {args.min_padding} px"
                    )
        if args.cols or args.rows:
            if not args.cols or not args.rows or args.cols < 1 or args.rows < 1:
                failures.append("--cols and --rows must both be positive")
            else:
                width, height = result["width"], result["height"]
                result["grid"] = {
                    "cols": args.cols,
                    "rows": args.rows,
                    "divisible": width % args.cols == 0 and height % args.rows == 0,
                    "cell_width": width // args.cols if width % args.cols == 0 else None,
                    "cell_height": height // args.rows if height % args.rows == 0 else None,
                }
                if not result["grid"]["divisible"]:
                    failures.append("image dimensions are not divisible by the requested grid")
        failures = list(dict.fromkeys(failures))
        result["checks_passed"] = not failures
        result["failures"] = failures
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not failures else 1
    except (OSError, ValueError, zlib.error) as exc:
        print(
            json.dumps(
                {"path": str(args.image), "error": str(exc)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())

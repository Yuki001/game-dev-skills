#!/usr/bin/env python3
"""Inspect PNG/SVG assets using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
import zlib
from pathlib import Path
from xml.etree import ElementTree

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_TYPES = {
    0: ("grayscale", 1),
    2: ("rgb", 3),
    3: ("indexed", 1),
    4: ("grayscale_alpha", 2),
    6: ("rgba", 4),
}
SVG_GRAPHIC_TAGS = {
    "circle",
    "ellipse",
    "image",
    "line",
    "path",
    "polygon",
    "polyline",
    "rect",
    "text",
    "use",
}
SVG_URL_REFERENCE_RE = re.compile(r"url\(\s*#([^) \t\r\n]+)\s*\)")
SVG_NONFINITE_RE = re.compile(
    r"(?:^|[\s,;(])(?:nan|[+-]?inf(?:inity)?)(?=$|[\s,;)])",
    re.IGNORECASE,
)
SVG_LENGTH_RE = re.compile(
    r"^\s*([+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"\s*(?:px|pt|pc|mm|cm|in)?\s*$"
)


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def _unfilter(raw: bytes, height: int, row_bytes: int, bpp: int) -> list[bytes]:
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


def inspect_png(path: Path) -> dict:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError("invalid PNG signature")
    chunks: dict[str, list[bytes]] = {}
    offset = len(PNG_SIGNATURE)
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        name = data[offset + 4 : offset + 8].decode("ascii")
        payload = data[offset + 8 : offset + 8 + length]
        chunks.setdefault(name, []).append(payload)
        offset += 12 + length
        if name == "IEND":
            break
    if "IHDR" not in chunks:
        raise ValueError("PNG has no IHDR chunk")
    width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(
        ">IIBBBBB", chunks["IHDR"][0]
    )
    if color_type not in COLOR_TYPES:
        raise ValueError(f"unsupported PNG color type {color_type}")
    color_name, channels = COLOR_TYPES[color_type]
    trns = chunks.get("tRNS", [None])[0]
    has_alpha = color_type in (4, 6) or trns is not None
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
    }
    if interlace or compression != 0 or filtering != 0 or "IDAT" not in chunks:
        result["alpha_analysis"] = {"available": False, "reason": "unsupported PNG encoding"}
        return result
    row_bytes = math.ceil(width * channels * bit_depth / 8)
    bpp = max(1, math.ceil(channels * bit_depth / 8))
    rows = _unfilter(zlib.decompress(b"".join(chunks["IDAT"])), height, row_bytes, bpp)
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
    result["alpha_analysis"] = {
        "available": True,
        "transparent_pixels": transparent,
        "partial_alpha_pixels": partial,
        "opaque_pixels": opaque,
        "transparent_fraction": transparent / (width * height),
        "nontransparent_bbox_xyxy": bbox,
        "transparent_border_fraction": border_transparent / border_total,
    }
    return result


def _positive_svg_length(value: str | None) -> bool:
    if not value:
        return False
    match = SVG_LENGTH_RE.fullmatch(value)
    if not match:
        return False
    number = float(match.group(1))
    return math.isfinite(number) and number > 0


def _valid_svg_view_box(value: str | None) -> bool:
    if not value:
        return False
    parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
    if len(parts) != 4:
        return False
    try:
        numbers = [float(part) for part in parts]
    except ValueError:
        return False
    return all(math.isfinite(number) for number in numbers) and numbers[2] > 0 and numbers[3] > 0


def inspect_svg(path: Path) -> dict:
    root = ElementTree.parse(path).getroot()
    if root.tag.split("}")[-1] != "svg":
        raise ValueError("root element is not <svg>")
    view_box = root.attrib.get("viewBox")
    width = root.attrib.get("width")
    height = root.attrib.get("height")
    ids: set[str] = set()
    duplicate_ids: set[str] = set()
    local_references: set[str] = set()
    external_references: list[str] = []
    nonfinite_attributes: list[str] = []
    graphic_element_count = 0
    script_count = 0
    foreign_object_count = 0

    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag in SVG_GRAPHIC_TAGS:
            graphic_element_count += 1
        elif tag == "script":
            script_count += 1
        elif tag == "foreignObject":
            foreign_object_count += 1

        element_id = element.attrib.get("id")
        if element_id:
            if element_id in ids:
                duplicate_ids.add(element_id)
            ids.add(element_id)

        for name, value in element.attrib.items():
            local_name = name.split("}")[-1]
            if local_name == "href":
                if value.startswith("#"):
                    local_references.add(value[1:])
                elif value:
                    external_references.append(value)
            local_references.update(SVG_URL_REFERENCE_RE.findall(value))
            if local_name in {"d", "points", "transform"} and SVG_NONFINITE_RE.search(value):
                nonfinite_attributes.append(f"{tag}.{local_name}")
            if local_name in {"aria-labelledby", "aria-describedby"}:
                local_references.update(value.split())
        if tag == "style" and element.text:
            local_references.update(SVG_URL_REFERENCE_RE.findall(element.text))

    structural_failures: list[str] = []
    warnings: list[str] = []
    view_box_valid = _valid_svg_view_box(view_box)
    explicit_dimensions_valid = _positive_svg_length(width) and _positive_svg_length(height)
    if view_box and not view_box_valid:
        structural_failures.append("viewBox must contain four finite numbers with positive width and height")
    elif not view_box and not explicit_dimensions_valid:
        structural_failures.append("SVG needs a valid positive-size viewBox or explicit width and height")
    if duplicate_ids:
        structural_failures.append(f"duplicate IDs: {', '.join(sorted(duplicate_ids))}")
    missing_references = sorted(reference for reference in local_references if reference not in ids)
    if missing_references:
        structural_failures.append(f"unresolved local references: {', '.join(missing_references)}")
    if nonfinite_attributes:
        structural_failures.append(
            f"non-finite numeric values in: {', '.join(sorted(set(nonfinite_attributes)))}"
        )
    if graphic_element_count == 0:
        structural_failures.append("SVG contains no graphic elements")
    if external_references:
        warnings.append("SVG contains external or embedded href resources; verify target-runtime support")
    if script_count:
        warnings.append("SVG contains <script>; verify that scripting is intentional and supported")
    if foreign_object_count:
        warnings.append("SVG contains <foreignObject>; verify target-runtime support")

    return {
        "path": str(path.resolve()),
        "format": "svg",
        "width": width,
        "height": height,
        "viewBox": view_box,
        "has_viewBox": bool(view_box),
        "viewBox_valid": view_box_valid,
        "explicit_dimensions_valid": explicit_dimensions_valid,
        "graphic_element_count": graphic_element_count,
        "id_count": len(ids),
        "duplicate_ids": sorted(duplicate_ids),
        "local_reference_count": len(local_references),
        "unresolved_local_references": missing_references,
        "external_reference_count": len(external_references),
        "external_references": external_references,
        "script_count": script_count,
        "foreign_object_count": foreign_object_count,
        "structural_failures": structural_failures,
        "warnings": warnings,
        "note": (
            "All SVGs require structural checks plus a text-only semantic shape review; "
            "production SVGs additionally require render/view."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("asset", type=Path)
    parser.add_argument("--expect-transparent", action="store_true")
    parser.add_argument("--cols", type=int)
    parser.add_argument("--rows", type=int)
    args = parser.parse_args()
    try:
        suffix = args.asset.suffix.lower()
        if suffix == ".png":
            result = inspect_png(args.asset)
        elif suffix == ".svg":
            result = inspect_svg(args.asset)
        else:
            raise ValueError("supported formats: .png, .svg")
        failures: list[str] = list(result.get("structural_failures", []))
        if args.expect_transparent:
            alpha = result.get("alpha_analysis", {})
            if not result.get("has_alpha_channel"):
                failures.append("asset has no alpha channel")
            elif not alpha.get("available"):
                failures.append("alpha pixels could not be verified")
            elif not alpha.get("transparent_pixels", 0):
                failures.append("asset contains no fully transparent pixels")
        if args.cols or args.rows:
            if result.get("format") != "png":
                failures.append("grid checks require PNG")
            elif not args.cols or not args.rows or args.cols < 1 or args.rows < 1:
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
        result["checks_passed"] = not failures
        result["failures"] = failures
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not failures else 1
    except (OSError, ValueError, ElementTree.ParseError, zlib.error) as exc:
        print(json.dumps({"path": str(args.asset), "error": str(exc)}, ensure_ascii=False, indent=2))
        return 2


if __name__ == "__main__":
    sys.exit(main())

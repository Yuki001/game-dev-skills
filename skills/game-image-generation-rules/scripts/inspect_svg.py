#!/usr/bin/env python3
"""Inspect SVG structure, references, numeric geometry, and compatibility warnings."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from xml.etree import ElementTree

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
SVG_NUMBER_PATTERN = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?"
SVG_NUMBER_RE = re.compile(rf"^{SVG_NUMBER_PATTERN}$")
SVG_LENGTH_RE_ANY_SIGN = re.compile(
    rf"^{SVG_NUMBER_PATTERN}(?:px|pt|pc|mm|cm|in|em|ex|ch|rem|vw|vh|vmin|vmax|%)?$"
)
SVG_PATH_TOKEN_RE = re.compile(rf"[AaCcHhLlMmQqSsTtVvZz]|{SVG_NUMBER_PATTERN}")
SVG_TRANSFORM_RE = re.compile(r"([A-Za-z]+)\s*\(([^()]*)\)")
SVG_NUMERIC_ATTRIBUTES = {
    "baseFrequency",
    "cx",
    "cy",
    "d",
    "dx",
    "dy",
    "fill-opacity",
    "filterRes",
    "height",
    "k1",
    "k2",
    "k3",
    "k4",
    "offset",
    "opacity",
    "pathLength",
    "points",
    "r",
    "rx",
    "ry",
    "stdDeviation",
    "stroke-dasharray",
    "stroke-dashoffset",
    "stroke-opacity",
    "stroke-width",
    "transform",
    "viewBox",
    "width",
    "x",
    "x1",
    "x2",
    "y",
    "y1",
    "y2",
}
SVG_LENGTH_RE = re.compile(
    r"^\s*([+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"\s*(?:px|pt|pc|mm|cm|in)?\s*$"
)


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


def _valid_svg_number_list(
    value: str,
    *,
    allow_lengths: bool = False,
    minimum_count: int = 1,
    even_count: bool = False,
) -> bool:
    parts = [part for part in re.split(r"[\s,]+", value.strip()) if part]
    if len(parts) < minimum_count or (even_count and len(parts) % 2):
        return False
    token_re = SVG_LENGTH_RE_ANY_SIGN if allow_lengths else SVG_NUMBER_RE
    return all(token_re.fullmatch(part) for part in parts)


def _valid_svg_path_data(value: str) -> bool:
    tokens: list[str] = []
    cursor = 0
    previous_was_number = False
    for match in SVG_PATH_TOKEN_RE.finditer(value):
        gap = value[cursor : match.start()]
        token = match.group(0)
        current_is_number = not token.isalpha()
        if gap and not re.fullmatch(r"[\s,]*", gap):
            return False
        if (
            not gap
            and previous_was_number
            and current_is_number
            and token[0] not in "+-"
        ):
            return False
        tokens.append(token)
        previous_was_number = current_is_number
        cursor = match.end()
    if value[cursor:].strip(" \t\r\n,") or not tokens or tokens[0] not in "Mm":
        return False

    arity = {
        "A": 7,
        "C": 6,
        "H": 1,
        "L": 2,
        "M": 2,
        "Q": 4,
        "S": 4,
        "T": 2,
        "V": 1,
        "Z": 0,
    }
    index = 0
    while index < len(tokens):
        command = tokens[index]
        if not command.isalpha():
            return False
        index += 1
        number_count = 0
        while index < len(tokens) and not tokens[index].isalpha():
            number_count += 1
            index += 1
        required = arity[command.upper()]
        if required == 0:
            if number_count:
                return False
        elif number_count < required or number_count % required:
            return False
    return True


def _valid_svg_transform_list(value: str) -> bool:
    arities = {
        "matrix": {6},
        "translate": {1, 2},
        "scale": {1, 2},
        "rotate": {1, 3},
        "skewX": {1},
        "skewY": {1},
    }
    cursor = 0
    matched = False
    for match in SVG_TRANSFORM_RE.finditer(value):
        if value[cursor : match.start()].strip(" \t\r\n,"):
            return False
        name, arguments = match.groups()
        parts = [part for part in re.split(r"[\s,]+", arguments.strip()) if part]
        if name not in arities or len(parts) not in arities[name]:
            return False
        if not parts or not all(SVG_NUMBER_RE.fullmatch(part) for part in parts):
            return False
        matched = True
        cursor = match.end()
    return matched and not value[cursor:].strip(" \t\r\n,")


def _valid_svg_numeric_attribute(name: str, value: str) -> bool:
    if SVG_NONFINITE_RE.search(value):
        return False
    if name == "viewBox":
        return _valid_svg_view_box(value)
    if name == "d":
        return _valid_svg_path_data(value)
    if name == "points":
        return _valid_svg_number_list(value, minimum_count=2, even_count=True)
    if name == "transform":
        if value.strip() == "none":
            return True
        return _valid_svg_transform_list(value)
    if name == "stroke-dasharray" and value.strip() == "none":
        return True
    if value.strip() in {"inherit", "initial", "unset"}:
        return True
    return _valid_svg_number_list(value, allow_lengths=True)


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
    invalid_numeric_attributes: list[str] = []
    graphic_element_count = 0
    script_count = 0
    foreign_object_count = 0
    title_count = 0
    desc_count = 0

    for element in root.iter():
        tag = element.tag.split("}")[-1]
        if tag in SVG_GRAPHIC_TAGS:
            graphic_element_count += 1
        elif tag == "script":
            script_count += 1
        elif tag == "foreignObject":
            foreign_object_count += 1
        elif tag == "title":
            title_count += 1
        elif tag == "desc":
            desc_count += 1

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
            if local_name in SVG_NUMERIC_ATTRIBUTES and not _valid_svg_numeric_attribute(
                local_name, value
            ):
                invalid_numeric_attributes.append(f"{tag}.{local_name}")
            if local_name in {"aria-labelledby", "aria-describedby"}:
                local_references.update(value.split())
        if tag == "style" and element.text:
            local_references.update(SVG_URL_REFERENCE_RE.findall(element.text))

    structural_failures: list[str] = []
    warnings: list[str] = []
    view_box_valid = _valid_svg_view_box(view_box)
    explicit_dimensions_valid = _positive_svg_length(width) and _positive_svg_length(height)
    if view_box and not view_box_valid:
        structural_failures.append(
            "viewBox must contain four finite numbers with positive width and height"
        )
    elif not view_box and not explicit_dimensions_valid:
        structural_failures.append(
            "SVG needs a valid positive-size viewBox or explicit width and height"
        )
    if duplicate_ids:
        structural_failures.append(f"duplicate IDs: {', '.join(sorted(duplicate_ids))}")
    missing_references = sorted(
        reference for reference in local_references if reference not in ids
    )
    if missing_references:
        structural_failures.append(
            f"unresolved local references: {', '.join(missing_references)}"
        )
    if invalid_numeric_attributes:
        structural_failures.append(
            "invalid or non-finite numeric geometry values in: "
            f"{', '.join(sorted(set(invalid_numeric_attributes)))}"
        )
    if graphic_element_count == 0:
        structural_failures.append("SVG contains no graphic elements")
    if external_references:
        warnings.append(
            "SVG contains external or embedded href resources; verify target-runtime support"
        )
    if script_count:
        warnings.append("SVG contains <script>; verify that scripting is intentional and supported")
    if foreign_object_count:
        warnings.append("SVG contains <foreignObject>; verify target-runtime support")
    root_titles = [child for child in root if child.tag.split("}")[-1] == "title"]
    has_root_title = any("".join(title.itertext()).strip() for title in root_titles)
    has_accessible_name = bool(
        root.attrib.get("aria-label")
        or root.attrib.get("aria-labelledby")
        or has_root_title
    )
    if root.attrib.get("role") == "img" and not has_accessible_name:
        warnings.append('SVG has role="img" but no title, aria-label, or aria-labelledby')

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
        "invalid_numeric_attributes": sorted(set(invalid_numeric_attributes)),
        "script_count": script_count,
        "foreign_object_count": foreign_object_count,
        "role": root.attrib.get("role"),
        "title_count": title_count,
        "desc_count": desc_count,
        "root_title_count": len(root_titles),
        "has_root_title": has_root_title,
        "has_accessible_name": has_accessible_name,
        "structural_failures": structural_failures,
        "warnings": warnings,
        "note": (
            "All SVGs require structural checks plus a text-only semantic shape review; "
            "formal SVGs additionally require render/view."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("svg", type=Path)
    parser.add_argument(
        "--strict-svg",
        action="store_true",
        help="promote SVG compatibility and accessibility warnings to failures",
    )
    args = parser.parse_args()
    try:
        if args.svg.suffix.lower() != ".svg":
            raise ValueError("supported format: .svg")
        result = inspect_svg(args.svg)
        failures: list[str] = list(result.get("structural_failures", []))
        if args.strict_svg:
            failures.extend(result.get("warnings", []))
        failures = list(dict.fromkeys(failures))
        result["checks_passed"] = not failures
        result["failures"] = failures
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not failures else 1
    except (OSError, ValueError, ElementTree.ParseError) as exc:
        print(
            json.dumps(
                {"path": str(args.svg), "error": str(exc)},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())

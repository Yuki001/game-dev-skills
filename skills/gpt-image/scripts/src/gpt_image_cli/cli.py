#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "openai>=1.55",
# ]
# ///
"""General-purpose CLI for OpenAI GPT Image models.

Mirrors the two official endpoints from the OpenAI cookbook using the official
`openai` Python SDK:

    client.images.generate(...)   — text → image          (no  -i)
    client.images.edit(...)       — text + image(s) → image (with -i; mask via -m)

Every documented parameter is exposed as a flag. Reads OPENAI_API_KEY from
process env, then .env, then ~/.env without overriding existing env. Writes the
returned PNG/JPEG/WebP bytes to disk and prints the output path(s) on stdout.

Exit codes: 0 success, 1 API error, 2 bad args.

Examples:
    # Basic generate, auto filename, 1K square
    gpt-image -p "a cat astronaut on the moon"

    # Named output, portrait 2K, high quality
    gpt-image -p "Chinese tea poster" -f poster.png --size 2k --quality high

    # Edit existing image (colorize, restyle, translate text, etc.)
    gpt-image -p "colorize this manga page" -i page.jpg -f colored.png

    # Multi-reference edit (outfit transfer, pet + brand, etc.)
    gpt-image -p "77 × KFC collab poster" -i cat.png -i kfc_logo.png -f collab.png

    # Alpha-channel inpaint (mask opaque = keep, transparent = regenerate)
    gpt-image -p "replace sky with aurora" -i photo.jpg -m sky_mask.png -f aurora.png

    # Grid of 4, opaque background, webp
    gpt-image -p "isometric chair, minimalist" -n 4 --background opaque --format webp

    # Generate on a flat chroma-key background, then remove it locally
    gpt-image -p "isolated product on a perfectly flat solid green background" \
        --background opaque --format png --remove-background

    # Run directly (no launcher needed)
    python "$SKILL_DIR/scripts/src/gpt_image_cli/cli.py" -p "a cat astronaut on the moon"
"""
from __future__ import annotations

import argparse
import base64
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from openai import APIError, OpenAI


def _parse_env_line(line: str) -> tuple[str, str] | None:
    """Parse a simple dotenv assignment without requiring python-dotenv."""
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if stripped.startswith("export "):
        stripped = stripped[len("export ") :].lstrip()
    if "=" not in stripped:
        return None

    key, value = stripped.split("=", 1)
    key = key.strip()
    value = value.strip()
    if not key:
        return None
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1]
    return key, value


def _load_env_file(path: Path) -> None:
    """Load unset environment variables from one dotenv-style file."""
    if not path.is_file():
        return
    try:
        lines = path.read_text(encoding="utf-8-sig").splitlines()
    except OSError as exc:
        print(f"error: could not read env file {path}: {exc}", file=sys.stderr)
        return

    for line in lines:
        parsed = _parse_env_line(line)
        if parsed:
            key, value = parsed
            os.environ.setdefault(key, value)


def _load_env_chain() -> None:
    """Resolve environment settings without overriding runtime-provided values.

    Order: process env → ./.env → ~/.env. Existing process env wins so
    hosted agents or explicit shell exports are not replaced by local files.
    """
    _load_env_file(Path.cwd() / ".env")
    _load_env_file(Path.home() / ".env")


SIZE_SHORTCUTS: dict[str, str] = {
    "1k": "1024x1024",
    "2k": "2048x2048",
    "4k": "3840x2160",
    "portrait": "1024x1536",
    "landscape": "1536x1024",
    "square": "1024x1024",
    "wide": "2048x1152",
    "tall": "2160x3840",
}

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "1024x1024"
DEFAULT_MODERATION = "low"


def slugify(text: str, max_len: int = 30) -> str:
    s = re.sub(r"[^\w\s-]", "", text.lower()).strip()
    s = re.sub(r"[-\s]+", "-", s)[:max_len]
    return s or "image"


def default_output_path(prompt: str, extension: str) -> Path:
    cwd = Path.cwd()
    target_dir = cwd / "fig" if (cwd / "fig").is_dir() else cwd
    stamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    return target_dir / f"{stamp}-{slugify(prompt)}.{extension}"


def resolve_size(value: str) -> str:
    return SIZE_SHORTCUTS.get(value.lower(), value)


def model_rejects_input_fidelity(model: str) -> bool:
    return model.strip().lower().startswith("gpt-image-2")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="gpt-image",
        description="Call OpenAI GPT Image models (generations or edits) via the official openai Python SDK.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("-p", "--prompt", required=True, help="Text prompt / edit instruction.")
    p.add_argument(
        "-f", "--file",
        help="Output path. Auto-generated as YYYY-MM-DD-HH-MM-SS-<slug>.<ext> if omitted "
             "(written to ./fig/ if that dir exists, else ./).",
    )
    p.add_argument(
        "-i", "--image", action="append", type=Path, default=None,
        help="Reference image path. Repeat flag for multi-reference edits. "
             "Presence of any -i switches endpoint to client.images.edit().",
    )
    p.add_argument(
        "-m", "--mask", type=Path, default=None,
        help="Alpha-channel PNG mask (opaque = preserved, transparent = regenerated). "
             "Edits endpoint only; requires -i.",
    )
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Model ID (default {DEFAULT_MODEL}).")
    p.add_argument(
        "--size", default=DEFAULT_SIZE,
        help="Image size. Accepts literals (1024x1024, 1536x1024, 2048x2048, 3840x2160, "
             "any 16px-multiple up to 3840 max edge, 3:1 ratio cap) or shortcuts "
             "(1k, 2k, 4k, portrait, landscape, square, wide, tall). Default 1024x1024.",
    )
    p.add_argument(
        "--quality", default="high", choices=["auto", "low", "medium", "high"],
        help="Rendering fidelity / budget knob (cost scales ~10× per step). Default high. "
             "Use low for cheap drafts, medium for normal exploration, high for final text-heavy or shipping-facing assets.",
    )
    p.add_argument("-n", "--n", type=int, default=1, help="Number of images to return. Default 1.")
    p.add_argument(
        "--background", default=None, choices=["auto", "opaque"],
        help="Background handling. Use `opaque` for chroma-key removal. Default API-side auto.",
    )
    p.add_argument(
        "--remove-background", action="store_true",
        help="After the API response, remove a flat chroma-key background with the bundled helper. "
             "Does not rewrite the prompt; request a uniform key-color background and use PNG or WebP.",
    )
    p.add_argument(
        "--moderation", default=DEFAULT_MODERATION, choices=["auto", "low"],
        help="Generations only. Default low. Use `auto` if you want the stricter API-side default.",
    )
    p.add_argument(
        "--input-fidelity", dest="input_fidelity", default=None, choices=["low", "high"],
        help="Edits only. gpt-image-2 rejects this parameter, so the CLI drops it locally before calling the API.",
    )
    p.add_argument(
        "--format", dest="output_format", default=None,
        choices=["png", "jpeg", "webp"],
        help="Output encoding. Default png.",
    )
    p.add_argument(
        "--compression", dest="output_compression", type=int, default=None,
        help="0-100 compression level for jpeg/webp. Ignored for png.",
    )
    p.add_argument(
        "--user", default=None,
        help="Optional end-user identifier forwarded to OpenAI for abuse tracking.",
    )
    return p.parse_args()


def _filter_none(d: dict[str, Any]) -> dict[str, Any]:
    """Drop keys whose value is None — SDK treats missing vs None differently."""
    return {k: v for k, v in d.items() if v is not None}


def call_generate(client: OpenAI, args: argparse.Namespace) -> Any:
    return client.images.generate(**_filter_none({
        "model": args.model,
        "prompt": args.prompt,
        "size": resolve_size(args.size),
        "quality": args.quality,
        "n": args.n,
        "background": args.background,
        "moderation": args.moderation,
        "output_format": args.output_format,
        "output_compression": args.output_compression,
        "user": args.user,
    }))


def call_edit(client: OpenAI, args: argparse.Namespace) -> Any:
    for p in args.image:
        if not p.is_file():
            print(f"error: --image not found: {p}", file=sys.stderr)
            sys.exit(2)
    if args.mask and not args.mask.is_file():
        print(f"error: --mask not found: {args.mask}", file=sys.stderr)
        sys.exit(2)

    input_fidelity = args.input_fidelity
    if input_fidelity and model_rejects_input_fidelity(args.model):
        print(
            "note: dropping --input-fidelity because gpt-image-2 rejects that parameter.",
            file=sys.stderr,
        )
        input_fidelity = None

    image_handles = [p.open("rb") for p in args.image]
    mask_handle = args.mask.open("rb") if args.mask else None
    try:
        return client.images.edit(**_filter_none({
            "model": args.model,
            "image": image_handles,
            "mask": mask_handle,
            "prompt": args.prompt,
            "size": resolve_size(args.size),
            "quality": args.quality,
            "n": args.n,
            "background": args.background,
            "input_fidelity": input_fidelity,
            "output_format": args.output_format,
            "output_compression": args.output_compression,
            "user": args.user,
        }))
    finally:
        for h in image_handles:
            h.close()
        if mask_handle:
            mask_handle.close()


def write_outputs(data: list[Any], out_path: Path, n: int) -> list[Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for i, item in enumerate(data):
        b64 = getattr(item, "b64_json", None)
        url = getattr(item, "url", None)
        if b64:
            raw = base64.b64decode(b64)
        elif url:
            with urllib.request.urlopen(url, timeout=300) as r:  # noqa: S310 — OpenAI-owned host
                raw = r.read()
        else:
            print(f"error: response item {i} has neither b64_json nor url", file=sys.stderr)
            sys.exit(1)

        if n == 1:
            target = out_path
        else:
            stem = out_path.with_suffix("")
            target = stem.parent / f"{stem.name}_{i}{out_path.suffix}"
        target.write_bytes(raw)
        written.append(target)
    return written


def remove_backgrounds(paths: list[Path]) -> bool:
    """Replace keyed PNG/WebP outputs with locally processed alpha images."""
    helper = Path(__file__).resolve().parents[2] / "remove_chroma_key.py"
    if not helper.is_file():
        print(f"error: background-removal helper not found: {helper}", file=sys.stderr)
        return False

    for path in paths:
        if path.suffix.lower() not in {".png", ".webp"}:
            print(
                f"error: --remove-background requires a .png or .webp output: {path}",
                file=sys.stderr,
            )
            return False

        with TemporaryDirectory(prefix="gpt-image-remove-background-") as temp_dir:
            processed = Path(temp_dir) / f"processed{path.suffix.lower()}"
            result = subprocess.run(
                [
                    sys.executable,
                    str(helper),
                    "--input",
                    str(path),
                    "--out",
                    str(processed),
                    "--auto-key",
                    "border",
                    "--soft-matte",
                    "--transparent-threshold",
                    "12",
                    "--opaque-threshold",
                    "220",
                    "--despill",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode != 0:
                if result.stdout:
                    print(result.stdout.rstrip(), file=sys.stderr)
                if result.stderr:
                    print(result.stderr.rstrip(), file=sys.stderr)
                print(
                    f"error: background removal failed for {path}; the keyed source was kept.",
                    file=sys.stderr,
                )
                return False

            if result.stderr:
                print(result.stderr.rstrip(), file=sys.stderr)
            path.write_bytes(processed.read_bytes())

    return True


def main() -> int:
    args = parse_args()

    _load_env_chain()
    if not os.environ.get("OPENAI_API_KEY"):
        print(
            "error: OPENAI_API_KEY not set. Add it to env / .env / ~/.env, or use your host agent's native image tool.",
            file=sys.stderr,
        )
        return 2

    if args.mask and not args.image:
        print("error: --mask requires --image (edits endpoint only)", file=sys.stderr)
        return 2

    ext = args.output_format or "png"
    out_path = Path(args.file).expanduser().resolve() if args.file else default_output_path(args.prompt, ext)

    if args.remove_background:
        if args.output_format == "jpeg" or out_path.suffix.lower() not in {".png", ".webp"}:
            print(
                "error: --remove-background requires PNG or WebP output so alpha is preserved.",
                file=sys.stderr,
            )
            return 2
        try:
            import PIL  # noqa: F401
        except ImportError:
            print(
                "error: --remove-background requires Pillow. Install it in the active Python environment.",
                file=sys.stderr,
            )
            return 2

    client = OpenAI()  # auto-reads OPENAI_API_KEY

    try:
        result = call_edit(client, args) if args.image else call_generate(client, args)
    except APIError as e:
        print(f"error: {type(e).__name__}: {e}", file=sys.stderr)
        return 1

    data = result.data or []
    if not data:
        print(f"error: no image data in response: {result}", file=sys.stderr)
        return 1

    written = write_outputs(data, out_path, args.n)
    if args.remove_background and not remove_backgrounds(written):
        return 1

    for p in written:
        print(p)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Generate images through OpenRouter's dedicated Image API."""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

API_BASE = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "bytedance-seed/seedream-4.5"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate images with OpenRouter's dedicated Image API."
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable containing the OpenRouter API key.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional .env file to read when the API key is not already in the environment. Defaults to the nearest .env found from the current directory upward.",
    )
    parser.add_argument(
        "--api-base",
        default=API_BASE,
        help="OpenRouter API base URL.",
    )

    def add_common_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument(
            "--api-key-env",
            default=argparse.SUPPRESS,
            help="Environment variable containing the OpenRouter API key.",
        )
        command_parser.add_argument(
            "--env-file",
            type=Path,
            default=argparse.SUPPRESS,
            help="Optional .env file to read when the API key is not already in the environment.",
        )
        command_parser.add_argument(
            "--api-base",
            default=argparse.SUPPRESS,
            help="OpenRouter API base URL.",
        )

    subparsers = parser.add_subparsers(dest="command", required=True)

    models = subparsers.add_parser("models", help="List available OpenRouter image models.")
    add_common_options(models)
    models.add_argument("--json", action="store_true", help="Print the raw JSON response.")

    endpoints = subparsers.add_parser(
        "endpoints", help="Show endpoint/provider capabilities for a model."
    )
    add_common_options(endpoints)
    endpoints.add_argument("--model", required=True, help="Image model ID.")
    endpoints.add_argument("--json", action="store_true", help="Print the raw JSON response.")

    generate = subparsers.add_parser("generate", help="Generate images from a prompt.")
    add_common_options(generate)
    generate.add_argument("--prompt", required=True, help="Text description of the desired image.")
    generate.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter image model ID.")
    generate.add_argument("--n", type=int, help="Number of images to generate, where supported.")
    generate.add_argument("--resolution", help="Resolution tier, e.g. 512, 1K, 2K, or 4K.")
    generate.add_argument("--aspect-ratio", help="Aspect ratio, e.g. 1:1, 16:9, or 9:16.")
    generate.add_argument("--size", help="Size shorthand, e.g. 2K or 2048x2048.")
    generate.add_argument(
        "--quality", choices=["auto", "low", "medium", "high"], help="Output quality."
    )
    generate.add_argument(
        "--output-format",
        choices=["png", "jpeg", "webp", "svg"],
        help="Requested output format.",
    )
    generate.add_argument(
        "--background",
        choices=["auto", "transparent", "opaque"],
        help="Background handling.",
    )
    generate.add_argument(
        "--output-compression", type=int, help="Compression 0-100 for jpeg/webp."
    )
    generate.add_argument("--seed", type=int, help="Seed for models that support it.")
    generate.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference image path, HTTP(S) URL, or data URL. Can be repeated.",
    )
    generate.add_argument(
        "--provider-options-json",
        help="JSON object placed under provider.options.",
    )
    generate.add_argument(
        "--provider-options-file",
        type=Path,
        help="File containing JSON object placed under provider.options.",
    )
    generate.add_argument(
        "--raw-json",
        type=Path,
        help="File containing additional request fields to merge into the payload.",
    )
    generate.add_argument("--stream", action="store_true", help="Use SSE streaming.")
    generate.add_argument(
        "--save-partials",
        action="store_true",
        help="Save streaming partial previews in addition to completed images.",
    )
    generate.add_argument(
        "--output-dir", type=Path, default=Path.cwd(), help="Directory for generated files."
    )
    generate.add_argument(
        "--output-prefix", default="openrouter_image", help="Generated file prefix."
    )
    generate.add_argument(
        "--metadata-file",
        type=Path,
        help="Metadata JSON path. Defaults to <output-dir>/<output-prefix>_metadata.json.",
    )
    generate.add_argument(
        "--no-metadata", action="store_true", help="Do not write metadata JSON."
    )
    generate.add_argument(
        "--dry-run", action="store_true", help="Print payload without making a request."
    )

    args = parser.parse_args()
    if not hasattr(args, "api_key_env"):
        args.api_key_env = "OPENROUTER_API_KEY"
    if not hasattr(args, "env_file"):
        args.env_file = None
    if not hasattr(args, "api_base"):
        args.api_base = API_BASE
    return args


def parse_env_line(line: str) -> tuple[str, str] | None:
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


def find_nearest_env_file(start: Path) -> Path | None:
    current = start.resolve()
    if current.is_file():
        current = current.parent
    for directory in (current, *current.parents):
        candidate = directory / ".env"
        if candidate.is_file():
            return candidate
    return None


def read_env_value(env_name: str, env_file: Path | None) -> str | None:
    path = env_file or find_nearest_env_file(Path.cwd())
    if not path:
        return None
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            parsed = parse_env_line(line)
            if parsed and parsed[0] == env_name:
                return parsed[1]
    except OSError as exc:
        raise SystemExit(f"Could not read env file {path}: {exc}") from exc
    return None


def get_api_key(env_name: str, env_file: Path | None, required: bool) -> str | None:
    return os.environ.get(env_name) or read_env_value(env_name, env_file) or (None if not required else missing_api_key(env_name, env_file))


def missing_api_key(env_name: str, env_file: Path | None) -> str:
    env_hint = f" or add {env_name}=... to {env_file}" if env_file else f" or add {env_name}=... to a project .env file"
    raise SystemExit(f"Missing API key. Set {env_name}{env_hint} before calling OpenRouter.")


def request_json(api_base: str, path: str, api_key: str | None = None) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(f"{api_base}{path}", headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def post_json(
    api_base: str, path: str, api_key: str, payload: dict[str, Any], stream: bool = False
) -> urllib.response.addinfourl:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        f"{api_base}{path}",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "text/event-stream" if stream else "application/json",
        },
        method="POST",
    )
    return urllib.request.urlopen(request, timeout=600)


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
    except OSError as exc:
        raise SystemExit(f"Could not read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected JSON object in {path}.")
    return value


def parse_json_object(value: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for {label}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"Expected JSON object for {label}.")
    return parsed


def local_image_to_data_url(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Reference image does not exist: {path}")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def build_reference(value: str) -> dict[str, Any]:
    if value.startswith(("http://", "https://", "data:")):
        url = value
    else:
        url = local_image_to_data_url(Path(value))
    return {"type": "image_url", "image_url": {"url": url}}


def add_if_present(payload: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        payload[key] = value


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": args.model, "prompt": args.prompt}

    add_if_present(payload, "n", args.n)
    add_if_present(payload, "resolution", args.resolution)
    add_if_present(payload, "aspect_ratio", args.aspect_ratio)
    add_if_present(payload, "size", args.size)
    add_if_present(payload, "quality", args.quality)
    add_if_present(payload, "output_format", args.output_format)
    add_if_present(payload, "background", args.background)
    add_if_present(payload, "output_compression", args.output_compression)
    add_if_present(payload, "seed", args.seed)

    if args.stream:
        payload["stream"] = True
    if args.reference:
        payload["input_references"] = [build_reference(ref) for ref in args.reference]

    provider_options: dict[str, Any] = {}
    if args.provider_options_file:
        provider_options.update(read_json_file(args.provider_options_file))
    if args.provider_options_json:
        provider_options.update(parse_json_object(args.provider_options_json, "provider options"))
    if provider_options:
        payload["provider"] = {"options": provider_options}

    if args.raw_json:
        payload.update(read_json_file(args.raw_json))

    return payload


def extension_for_image(image: dict[str, Any], requested_format: str | None) -> str:
    media_type = image.get("media_type")
    if media_type == "image/svg+xml":
        return "svg"
    if media_type and "/" in media_type:
        return media_type.split("/", 1)[1].replace("jpeg", "jpg")
    if requested_format:
        return "jpg" if requested_format == "jpeg" else requested_format
    return "png"


def save_image(
    image: dict[str, Any],
    output_dir: Path,
    prefix: str,
    index: int,
    requested_format: str | None,
    total_count: int | None = None,
) -> Path:
    b64_json = image.get("b64_json")
    if not isinstance(b64_json, str):
        raise SystemExit("OpenRouter response image is missing b64_json.")
    extension = extension_for_image(image, requested_format)
    path = output_dir / f"{prefix}.{extension}" if total_count == 1 else output_dir / f"{prefix}_{index:03d}.{extension}"
    path.write_bytes(base64.b64decode(b64_json))
    return path


def write_metadata(
    args: argparse.Namespace,
    payload: dict[str, Any],
    result: dict[str, Any],
    files: list[Path],
) -> None:
    if args.no_metadata:
        return
    metadata_path = args.metadata_file or args.output_dir / f"{args.output_prefix}_metadata.json"
    metadata = {
        "request": payload,
        "created": result.get("created"),
        "usage": result.get("usage"),
        "files": [str(path) for path in files],
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote metadata: {metadata_path}")


def print_models(result: dict[str, Any], raw_json: bool) -> None:
    if raw_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    for model in result.get("data", []):
        model_id = model.get("id", "<unknown>")
        name = model.get("name", "")
        params = ", ".join(sorted((model.get("supported_parameters") or {}).keys()))
        streaming = "streaming" if model.get("supports_streaming") else "buffered"
        print(f"{model_id}\t{name}\t{streaming}\t{params}")


def print_endpoints(result: dict[str, Any], raw_json: bool) -> None:
    if raw_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print(result.get("id", "<unknown model>"))
    for endpoint in result.get("endpoints", []):
        provider = endpoint.get("provider_name") or endpoint.get("provider_slug") or "<provider>"
        tag = endpoint.get("provider_tag") or "-"
        params = ", ".join(sorted((endpoint.get("supported_parameters") or {}).keys()))
        passthrough = ", ".join(endpoint.get("allowed_passthrough_parameters") or []) or "-"
        streaming = "yes" if endpoint.get("supports_streaming") else "no"
        print(f"- {provider} (tag: {tag}, streaming: {streaming})")
        print(f"  parameters: {params or '-'}")
        print(f"  passthrough: {passthrough}")
        for price in endpoint.get("pricing", []):
            billable = price.get("billable")
            unit = price.get("unit")
            cost = price.get("cost_usd")
            variant = f" ({price['variant']})" if price.get("variant") else ""
            print(f"  price: {cost} USD per {unit} {billable}{variant}")


def handle_buffered_response(
    args: argparse.Namespace, payload: dict[str, Any], response: urllib.response.addinfourl
) -> None:
    result = json.loads(response.read().decode("utf-8"))
    images = result.get("data", [])
    if not images:
        raise SystemExit(f"OpenRouter response did not include images: {json.dumps(result)[:500]}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    files = [
        save_image(image, args.output_dir, args.output_prefix, index, args.output_format, len(images))
        for index, image in enumerate(images, start=1)
    ]
    for path in files:
        print(f"Wrote image: {path}")
    if result.get("usage"):
        print(f"Usage: {json.dumps(result['usage'], ensure_ascii=False)}")
    write_metadata(args, payload, result, files)


def iter_sse_events(response: urllib.response.addinfourl):
    for raw_line in response:
        line = raw_line.decode("utf-8").strip()
        if not line or not line.startswith("data: "):
            continue
        data = line[6:]
        if data == "[DONE]":
            break
        yield json.loads(data)


def handle_streaming_response(
    args: argparse.Namespace, payload: dict[str, Any], response: urllib.response.addinfourl
) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    files: list[Path] = []
    result: dict[str, Any] = {"data": [], "created": None, "usage": None}
    partial_count = 0

    for event in iter_sse_events(response):
        event_type = event.get("type")
        print(f"Event: {event_type}")
        if event_type == "error":
            raise SystemExit(json.dumps(event.get("error", event), ensure_ascii=False))
        if event_type == "image_generation.partial_image" and args.save_partials:
            partial_count += 1
            partial = {"b64_json": event.get("b64_json"), "media_type": event.get("media_type")}
            files.append(
                save_image(
                    partial,
                    args.output_dir,
                    f"{args.output_prefix}_partial",
                    partial_count,
                    args.output_format,
                )
            )
        if event_type == "image_generation.completed":
            result["created"] = event.get("created") or int(time.time())
            result["usage"] = event.get("usage")
            image = {"b64_json": event.get("b64_json"), "media_type": event.get("media_type")}
            result["data"].append(image)
            files.append(save_image(image, args.output_dir, args.output_prefix, len(result["data"]), args.output_format))

    if not result["data"]:
        raise SystemExit("Streaming finished without a completed image.")
    if len(result["data"]) == 1:
        original_path = files[-1]
        extension = extension_for_image(result["data"][0], args.output_format)
        renamed_path = args.output_dir / f"{args.output_prefix}.{extension}"
        original_path.replace(renamed_path)
        files[-1] = renamed_path
    for path in files:
        print(f"Wrote image: {path}")
    if result.get("usage"):
        print(f"Usage: {json.dumps(result['usage'], ensure_ascii=False)}")
    write_metadata(args, payload, result, files)


def main() -> int:
    args = parse_args()

    try:
        if args.command == "models":
            api_key = get_api_key(args.api_key_env, args.env_file, required=False)
            print_models(request_json(args.api_base, "/images/models", api_key), args.json)
            return 0

        if args.command == "endpoints":
            api_key = get_api_key(args.api_key_env, args.env_file, required=False)
            model_path = urllib.parse.quote(args.model, safe="/")
            print_endpoints(
                request_json(args.api_base, f"/images/models/{model_path}/endpoints", api_key),
                args.json,
            )
            return 0

        if args.command == "generate":
            payload = build_payload(args)
            if args.dry_run:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
                return 0
            api_key = get_api_key(args.api_key_env, args.env_file, required=True)
            response = post_json(args.api_base, "/images", api_key, payload, stream=args.stream)
            if args.stream:
                handle_streaming_response(args, payload, response)
            else:
                handle_buffered_response(args, payload, response)
            return 0

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"OpenRouter HTTP {exc.code}: {body}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"OpenRouter request failed: {exc}", file=sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

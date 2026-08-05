#!/usr/bin/env python3
"""Generate videos through OpenRouter's asynchronous Video API."""

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
DEFAULT_MODEL = "bytedance/seedance-2.0"
TERMINAL_STATUSES = {"completed", "failed", "cancelled", "expired"}


class SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Do not forward an API key when a download redirects to another origin."""

    def redirect_request(self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str):
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is None:
            return None
        old_origin = urllib.parse.urlsplit(req.full_url)[:2]
        new_origin = urllib.parse.urlsplit(newurl)[:2]
        if old_origin != new_origin:
            redirected.remove_header("Authorization")
        return redirected


def open_url(request: urllib.request.Request, timeout: float):
    return urllib.request.build_opener(SafeRedirectHandler()).open(request, timeout=timeout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate videos with OpenRouter's asynchronous Video API."
    )
    parser.add_argument(
        "--api-key-env",
        default="OPENROUTER_API_KEY",
        help="Environment variable containing the OpenRouter API key.",
    )
    parser.add_argument(
        "--env-file",
        type=Path,
        help="Optional .env file. Defaults to the nearest .env found from the current directory upward.",
    )
    parser.add_argument("--api-base", default=API_BASE, help="OpenRouter API base URL.")

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
            help="Optional .env file to read for the API key.",
        )
        command_parser.add_argument(
            "--api-base", default=argparse.SUPPRESS, help="OpenRouter API base URL."
        )

    def add_output_options(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument(
            "--output-dir", type=Path, default=Path.cwd(), help="Directory for generated files."
        )
        command_parser.add_argument(
            "--output-prefix", default="openrouter_video", help="Generated file prefix."
        )
        command_parser.add_argument(
            "--metadata-file",
            type=Path,
            help="Metadata path. Defaults to <output-dir>/<output-prefix>_metadata.json.",
        )
        command_parser.add_argument(
            "--no-metadata", action="store_true", help="Do not write metadata JSON."
        )

    subparsers = parser.add_subparsers(dest="command", required=True)

    models = subparsers.add_parser("models", help="List available OpenRouter video models.")
    add_common_options(models)
    models.add_argument("--json", action="store_true", help="Print the raw JSON response.")

    status = subparsers.add_parser("status", help="Get a video job's current status.")
    add_common_options(status)
    status.add_argument("--job-id", required=True, help="OpenRouter video job ID.")
    status.add_argument("--json", action="store_true", help="Print the raw JSON response.")

    download = subparsers.add_parser("download", help="Download a completed video job.")
    add_common_options(download)
    add_output_options(download)
    download.add_argument("--job-id", required=True, help="OpenRouter video job ID.")
    download.add_argument("--index", type=int, help="Download only this zero-based output index.")

    generate = subparsers.add_parser("generate", help="Submit and optionally wait for a video.")
    add_common_options(generate)
    add_output_options(generate)
    generate.add_argument("--prompt", required=True, help="Text description of the desired video.")
    generate.add_argument("--model", default=DEFAULT_MODEL, help="OpenRouter video model ID.")
    generate.add_argument("--duration", type=int, help="Video duration in seconds.")
    generate.add_argument("--resolution", help="Resolution, e.g. 720p, 1080p, or 2K.")
    generate.add_argument("--aspect-ratio", help="Aspect ratio, e.g. 16:9 or 9:16.")
    generate.add_argument("--size", help="Exact dimensions in WIDTHxHEIGHT form.")
    generate.add_argument("--first-frame", help="First-frame image path, URL, or data URL.")
    generate.add_argument("--last-frame", help="Last-frame image path, URL, or data URL.")
    generate.add_argument(
        "--reference",
        action="append",
        default=[],
        help="Reference image path, URL, or data URL. Can be repeated.",
    )
    audio = generate.add_mutually_exclusive_group()
    audio.add_argument(
        "--generate-audio", dest="generate_audio", action="store_true", help="Generate audio."
    )
    audio.add_argument(
        "--no-generate-audio",
        dest="generate_audio",
        action="store_false",
        help="Do not generate audio.",
    )
    generate.set_defaults(generate_audio=None)
    generate.add_argument("--seed", type=int, help="Seed for providers that support it.")
    generate.add_argument("--callback-url", help="HTTPS webhook callback URL.")
    generate.add_argument(
        "--provider-options-json", help="JSON object placed under provider.options."
    )
    generate.add_argument(
        "--provider-options-file",
        type=Path,
        help="File containing a JSON object placed under provider.options.",
    )
    generate.add_argument(
        "--raw-json", type=Path, help="File containing additional request fields to merge."
    )
    generate.add_argument(
        "--poll-interval", type=float, default=30.0, help="Seconds between status checks."
    )
    generate.add_argument(
        "--timeout",
        type=float,
        default=1800.0,
        help="Maximum seconds to wait; use 0 for no local timeout.",
    )
    generate.add_argument(
        "--submit-only", action="store_true", help="Submit the job without polling or downloading."
    )
    generate.add_argument(
        "--no-download", action="store_true", help="Wait for completion without downloading."
    )
    generate.add_argument(
        "--dry-run", action="store_true", help="Print the request payload without submitting."
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


def missing_api_key(env_name: str, env_file: Path | None) -> str:
    env_hint = (
        f" or add {env_name}=... to {env_file}"
        if env_file
        else f" or add {env_name}=... to a project .env file"
    )
    raise SystemExit(f"Missing API key. Set {env_name}{env_hint} before calling OpenRouter.")


def get_api_key(env_name: str, env_file: Path | None, required: bool) -> str | None:
    return (
        os.environ.get(env_name)
        or read_env_value(env_name, env_file)
        or (None if not required else missing_api_key(env_name, env_file))
    )


def api_url(api_base: str, path: str) -> str:
    return f"{api_base.rstrip('/')}/{path.lstrip('/')}"


def read_json_response(response: Any) -> dict[str, Any]:
    value = json.loads(response.read().decode("utf-8"))
    if not isinstance(value, dict):
        raise SystemExit("OpenRouter returned JSON that was not an object.")
    return value


def get_json(url: str, api_key: str | None = None) -> dict[str, Any]:
    headers = {"Accept": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, headers=headers)
    with open_url(request, timeout=60) as response:
        return read_json_response(response)


def post_json(url: str, api_key: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    with open_url(request, timeout=120) as response:
        return read_json_response(response)


def read_json_file(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
    except OSError as exc:
        raise SystemExit(f"Could not read JSON file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit(f"Expected a JSON object in {path}.")
    return value


def parse_json_object(value: str, label: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON for {label}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SystemExit(f"Expected a JSON object for {label}.")
    return parsed


def local_image_to_data_url(path: Path) -> str:
    if not path.is_file():
        raise SystemExit(f"Image does not exist: {path}")
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def image_url(value: str) -> str:
    if value.startswith(("http://", "https://", "data:")):
        return value
    return local_image_to_data_url(Path(value))


def build_image(value: str, frame_type: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "type": "image_url",
        "image_url": {"url": image_url(value)},
    }
    if frame_type:
        result["frame_type"] = frame_type
    return result


def add_if_present(payload: dict[str, Any], key: str, value: Any) -> None:
    if value is not None:
        payload[key] = value


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.duration is not None and args.duration <= 0:
        raise SystemExit("--duration must be greater than zero.")
    if args.size and (args.resolution or args.aspect_ratio):
        raise SystemExit("--size cannot be combined with --resolution or --aspect-ratio.")
    if args.callback_url and urllib.parse.urlparse(args.callback_url).scheme != "https":
        raise SystemExit("--callback-url must use HTTPS.")
    if args.poll_interval <= 0:
        raise SystemExit("--poll-interval must be greater than zero.")
    if args.timeout < 0:
        raise SystemExit("--timeout cannot be negative.")

    payload: dict[str, Any] = {"model": args.model, "prompt": args.prompt}
    add_if_present(payload, "duration", args.duration)
    add_if_present(payload, "resolution", args.resolution)
    add_if_present(payload, "aspect_ratio", args.aspect_ratio)
    add_if_present(payload, "size", args.size)
    add_if_present(payload, "generate_audio", args.generate_audio)
    add_if_present(payload, "seed", args.seed)
    add_if_present(payload, "callback_url", args.callback_url)

    frames = []
    if args.first_frame:
        frames.append(build_image(args.first_frame, "first_frame"))
    if args.last_frame:
        frames.append(build_image(args.last_frame, "last_frame"))
    if frames:
        payload["frame_images"] = frames
    if args.reference:
        payload["input_references"] = [build_image(value) for value in args.reference]
    if frames and args.reference:
        print(
            "Warning: frame_images take precedence over input_references; references may be ignored.",
            file=sys.stderr,
        )

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


def job_url(api_base: str, job_id: str) -> str:
    encoded_id = urllib.parse.quote(job_id, safe="")
    return api_url(api_base, f"/videos/{encoded_id}")


def same_origin(first_url: str, second_url: str) -> bool:
    first = urllib.parse.urlsplit(first_url)
    second = urllib.parse.urlsplit(second_url)
    return (first.scheme.lower(), first.netloc.lower()) == (
        second.scheme.lower(),
        second.netloc.lower(),
    )


def get_job(api_base: str, api_key: str, job_id: str) -> dict[str, Any]:
    return get_json(job_url(api_base, job_id), api_key)


def print_models(result: dict[str, Any], raw_json: bool) -> None:
    if raw_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    for model in result.get("data", []):
        model_id = model.get("id", "<unknown>")
        name = model.get("name", "")
        resolutions = ",".join(model.get("supported_resolutions") or []) or "-"
        ratios = ",".join(model.get("supported_aspect_ratios") or []) or "-"
        sizes = ",".join(model.get("supported_sizes") or []) or "-"
        passthrough = ",".join(model.get("allowed_passthrough_parameters") or []) or "-"
        print(f"{model_id}\t{name}")
        print(f"  resolutions: {resolutions}")
        print(f"  aspect ratios: {ratios}")
        print(f"  sizes: {sizes}")
        print(f"  passthrough: {passthrough}")
        for sku, price in (model.get("pricing_skus") or {}).items():
            print(f"  price: {sku}={price}")


def print_job(result: dict[str, Any], raw_json: bool = False) -> None:
    if raw_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return
    print(f"Job: {result.get('id', '<unknown>')}")
    print(f"Status: {result.get('status', '<unknown>')}")
    if result.get("generation_id"):
        print(f"Generation: {result['generation_id']}")
    if result.get("error"):
        print(f"Error: {result['error']}")
    if result.get("usage"):
        print(f"Usage: {json.dumps(result['usage'], ensure_ascii=False)}")


def wait_for_job(
    api_base: str,
    api_key: str,
    job_id: str,
    initial: dict[str, Any],
    poll_interval: float,
    timeout: float,
) -> dict[str, Any]:
    result = initial
    started = time.monotonic()
    last_status = None
    while True:
        status = str(result.get("status", ""))
        if status != last_status:
            print(f"Status: {status or '<unknown>'}")
            last_status = status
        if status in TERMINAL_STATUSES:
            return result
        elapsed = time.monotonic() - started
        if timeout and elapsed >= timeout:
            raise TimeoutError(
                f"Timed out after {timeout:g} seconds. Job {job_id} is still remote; resume with status or download."
            )
        delay = poll_interval if not timeout else min(poll_interval, max(0.0, timeout - elapsed))
        time.sleep(delay)
        result = get_job(api_base, api_key, job_id)


def sanitized_for_metadata(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitized_for_metadata(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitized_for_metadata(item) for item in value]
    if isinstance(value, str) and value.startswith("data:") and ";base64," in value:
        header = value.split(",", 1)[0]
        return f"{header},<omitted>"
    return value


def write_metadata(
    args: argparse.Namespace,
    payload: dict[str, Any] | None,
    job: dict[str, Any],
    files: list[Path],
) -> None:
    if args.no_metadata:
        return
    args.output_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = args.metadata_file or args.output_dir / f"{args.output_prefix}_metadata.json"
    existing_request = None
    if payload is None and metadata_path.is_file():
        try:
            existing = json.loads(metadata_path.read_text(encoding="utf-8"))
            if isinstance(existing, dict):
                existing_request = existing.get("request")
        except (OSError, json.JSONDecodeError):
            pass
    metadata = {
        "request": sanitized_for_metadata(payload) if payload is not None else existing_request,
        "job": job,
        "files": [str(path) for path in files],
    }
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote metadata: {metadata_path}")


def extension_from_response(response: Any) -> str:
    media_type = response.headers.get_content_type().lower()
    extensions = {
        "video/mp4": "mp4",
        "video/webm": "webm",
        "video/quicktime": "mov",
        "video/x-matroska": "mkv",
    }
    return extensions.get(media_type, "mp4")


def download_one(url: str, path_without_suffix: Path, api_key: str | None) -> Path:
    headers = {"Accept": "video/*,application/octet-stream"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, headers=headers)
    with open_url(request, timeout=600) as response:
        path = path_without_suffix.with_suffix(f".{extension_from_response(response)}")
        with path.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
    return path


def download_job_outputs(
    args: argparse.Namespace,
    api_key: str,
    job: dict[str, Any],
) -> list[Path]:
    status = job.get("status")
    if status != "completed":
        error = f": {job['error']}" if job.get("error") else ""
        raise SystemExit(f"Job is {status or 'not completed'}{error}")
    urls = job.get("unsigned_urls") or []
    if not isinstance(urls, list):
        raise SystemExit("Job response contained invalid unsigned_urls.")

    selected: list[tuple[int, str, str | None]] = []
    if getattr(args, "index", None) is not None:
        if args.index < 0:
            raise SystemExit("--index cannot be negative.")
        if urls:
            if args.index >= len(urls):
                raise SystemExit(f"--index {args.index} is out of range for {len(urls)} output(s).")
            url = urls[args.index]
            download_key = api_key if same_origin(url, args.api_base) else None
            selected.append((args.index, url, download_key))
        else:
            direct = f"{job_url(args.api_base, str(job['id']))}/content?index={args.index}"
            selected.append((args.index, direct, api_key))
    elif urls:
        selected = [
            (index, url, api_key if same_origin(url, args.api_base) else None)
            for index, url in enumerate(urls)
        ]
    else:
        direct = f"{job_url(args.api_base, str(job['id']))}/content?index=0"
        selected.append((0, direct, api_key))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    multiple = len(selected) > 1
    files: list[Path] = []
    for index, url, download_key in selected:
        if not isinstance(url, str) or not url.startswith(("http://", "https://")):
            raise SystemExit(f"Invalid download URL for output {index}.")
        stem = f"{args.output_prefix}_{index + 1:03d}" if multiple else args.output_prefix
        path = download_one(url, args.output_dir / stem, download_key)
        files.append(path)
        print(f"Wrote video: {path}")
    return files


def main() -> int:
    args = parse_args()
    try:
        if args.command == "models":
            api_key = get_api_key(args.api_key_env, args.env_file, required=False)
            result = get_json(api_url(args.api_base, "/videos/models"), api_key)
            print_models(result, args.json)
            return 0

        if args.command == "status":
            api_key = get_api_key(args.api_key_env, args.env_file, required=True)
            print_job(get_job(args.api_base, api_key, args.job_id), args.json)
            return 0

        if args.command == "download":
            api_key = get_api_key(args.api_key_env, args.env_file, required=True)
            job = get_job(args.api_base, api_key, args.job_id)
            files = download_job_outputs(args, api_key, job)
            write_metadata(args, None, job, files)
            return 0

        if args.command == "generate":
            payload = build_payload(args)
            if args.dry_run:
                print(json.dumps(sanitized_for_metadata(payload), indent=2, ensure_ascii=False))
                return 0
            api_key = get_api_key(args.api_key_env, args.env_file, required=True)
            args.output_dir.mkdir(parents=True, exist_ok=True)
            job = post_json(api_url(args.api_base, "/videos"), api_key, payload)
            job_id = job.get("id")
            if not isinstance(job_id, str) or not job_id:
                raise SystemExit(f"Submit response did not include a job ID: {json.dumps(job)[:500]}")
            print(f"Job submitted: {job_id}")
            print(f"Polling URL: {job.get('polling_url') or job_url(args.api_base, job_id)}")
            write_metadata(args, payload, job, [])
            if args.submit_only:
                return 0
            job = wait_for_job(
                args.api_base,
                api_key,
                job_id,
                job,
                args.poll_interval,
                args.timeout,
            )
            print_job(job)
            if job.get("status") != "completed":
                write_metadata(args, payload, job, [])
                return 1
            files = [] if args.no_download else download_job_outputs(args, api_key, job)
            write_metadata(args, payload, job, files)
            return 0

    except TimeoutError as exc:
        print(str(exc), file=sys.stderr)
        return 2
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

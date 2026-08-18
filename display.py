from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path
import tempfile
import time

import requests

from render import render_file
from conference import load_conference


API_BASE = "https://dot.mindreset.tech"
API_KEY = os.environ.get("QUOTE_API_KEY", "")
DEVICE_ID = os.environ.get("QUOTE_DEVICE_ID", "")
TASK_KEY = os.environ.get("QUOTE_TASK_KEY", "")
PUSH_ENABLED = os.environ.get("QUOTE_PUSH_ENABLED", "false").lower() == "true"
UPDATE_INTERVAL = int(os.environ.get("UPDATE_INTERVAL", "10800"))
PREVIEW_PATH = os.environ.get("PREVIEW_PATH", "/tmp/conference-countdown.png")
CONFIG_PATH = os.environ.get("CONFERENCE_CONFIG_PATH", "conference.yml")
CONFIG_URL = os.environ.get("CONFERENCE_CONFIG_URL", "")


def current_config_path() -> Path:
    if not CONFIG_URL:
        return Path(CONFIG_PATH)

    response = requests.get(CONFIG_URL, timeout=15)
    response.raise_for_status()
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False, encoding="utf-8") as handle:
        handle.write(response.text)
        downloaded = Path(handle.name)
    try:
        load_conference(downloaded)
    except Exception:
        downloaded.unlink(missing_ok=True)
        raise
    return downloaded


def push_image(path: str | Path) -> None:
    if not API_KEY or not DEVICE_ID:
        raise RuntimeError("QUOTE_API_KEY and QUOTE_DEVICE_ID are required for device pushes")

    png = Path(path).read_bytes()
    payload = {
        "refreshNow": True,
        "image": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
        "border": 0,
        "ditherType": "NONE",
    }
    if TASK_KEY:
        payload["taskKey"] = TASK_KEY

    response = requests.post(
        f"{API_BASE}/api/authV2/open/device/{DEVICE_ID}/image",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json=payload,
        timeout=20,
    )
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = response.json().get("message", "")
        except ValueError:
            detail = response.text.strip()
        suffix = f": {detail}" if detail else ""
        raise RuntimeError(f"Image API failed with HTTP {response.status_code}{suffix}") from exc


def run_once() -> bool:
    config_path = current_config_path()
    try:
        output = render_file(config_path=config_path, output_path=PREVIEW_PATH)
    finally:
        if CONFIG_URL:
            config_path.unlink(missing_ok=True)
    size = output.stat().st_size
    if not PUSH_ENABLED:
        print(f"Preview updated; Quote push disabled ({size:,} bytes)")
        return True

    push_image(output)
    print(f"Display updated ({size:,} bytes)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a single conference deadline for Quote/0")
    parser.add_argument("--loop", action="store_true", help="refresh continuously")
    parser.add_argument("--interval", type=int, default=UPDATE_INTERVAL)
    args = parser.parse_args()

    if not args.loop:
        run_once()
        return

    print(f"Looping every {args.interval}s")
    while True:
        try:
            run_once()
        except Exception as exc:
            print(f"Update failed: {exc}", flush=True)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()

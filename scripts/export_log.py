#!/usr/bin/env python3
"""
Export the current session log from the running test-app and save it to
test-verifier/logs/.

Usage:
  python scripts/export_log.py                   # connects to localhost:5173
  python scripts/export_log.py --port 5173        # explicit Vite port
  python scripts/export_log.py --task house_task  # prefix output filename

Requirements:
  None — uses only the Python standard library.

The test-app must be running with `npm run dev`. The Vite dev server exposes a
/dev-log endpoint that the app updates on every flush (~250 ms after each action).
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

REPO_ROOT = Path(__file__).parent.parent
LOGS_DIR = REPO_ROOT / "test-verifier" / "logs"


def fetch_log(port: int) -> dict:
    url = f"http://localhost:{port}/dev-log"
    try:
        with urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except URLError as e:
        reason = getattr(e, "reason", e)
        if "Connection refused" in str(reason):
            print(f"\nCould not connect to {url}")
            print("Make sure the test-app is running:  npm run dev  (in test-app/)")
        elif "404" in str(e):
            print(f"\nNo log yet at {url}")
            print("Open the app in your browser and perform some actions first.")
        else:
            print(f"\nHTTP error: {e}")
        sys.exit(1)


def save_log(log: dict, task_prefix: str | None) -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{task_prefix}_{ts}" if task_prefix else f"log_{ts}"
    path = LOGS_DIR / f"{stem}.json"
    with open(path, "w") as f:
        json.dump(log, f, indent=2)
    return path


def main():
    parser = argparse.ArgumentParser(description="Export test-app session log to test-verifier/logs/")
    parser.add_argument("--port", type=int, default=5173, help="Vite dev server port (default 5173)")
    parser.add_argument("--task", type=str, default=None, help="Task name prefix for the output file")
    args = parser.parse_args()

    print(f"Fetching log from http://localhost:{args.port}/dev-log …")
    log = fetch_log(args.port)
    path = save_log(log, args.task)

    sem_count = len(log.get("semantic", []))
    raw_count = len(log.get("raw", []))
    print(f"\n✓ Log saved → {path}")
    print(f"  sessionId : {log.get('sessionId', '?')}")
    print(f"  semantic  : {sem_count} events")
    print(f"  raw       : {raw_count} events")


if __name__ == "__main__":
    main()

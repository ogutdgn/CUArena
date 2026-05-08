#!/usr/bin/env python3
"""
run_task.py — Export the current session log and (optionally) run a verifier task.

Usage:
  python scripts/run_task.py task_01                            # full pipeline (export + score)
  python scripts/run_task.py 1                                  # numeric prefix also works
  python scripts/run_task.py export-log                         # export only, no scoring
  python scripts/run_task.py export-log task_01                 # export only, prefix filename with task
  python scripts/run_task.py --host mock task_01                # docker-compose service-to-service

Loads task verifiers from delivery-1/task_NN/verifier.py (single source of truth).
Saves logs to scripts/logs/, scores to scripts/scores/.

Run with the verifier venv's python (it has pyyaml):
  ../.venv/Scripts/python scripts/run_task.py task_01
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

APP_ROOT     = Path(__file__).resolve().parent.parent       # apps/figma/
SCRIPTS_DIR  = Path(__file__).resolve().parent              # apps/figma/scripts/
DELIVERY_DIR = APP_ROOT / "delivery-1"
LOGS_DIR     = SCRIPTS_DIR / "logs"
SCORES_DIR   = SCRIPTS_DIR / "scores"

# Make `from verifier... import ...` work inside delivery-1/task_NN/verifier.py
sys.path.insert(0, str(APP_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def list_task_dirs() -> list[Path]:
    return sorted(p for p in DELIVERY_DIR.glob("task_*") if (p / "verifier.py").is_file())


def resolve_task(name: str) -> Path:
    """Accept full 'task_NN', short 'NN' / 'N'. Returns task dir under delivery-1/."""
    dirs = list_task_dirs()
    if not dirs:
        raise SystemExit(f"No task verifiers found in {DELIVERY_DIR}")

    if name.isdigit():
        target = f"task_{name.zfill(2)}"
    else:
        target = name

    for d in dirs:
        if d.name == target:
            return d

    listing = "\n  ".join(d.name for d in dirs)
    raise SystemExit(f"No task matching '{name}'. Available:\n  {listing}")


def load_task(task_dir: Path):
    verifier_py = task_dir / "verifier.py"
    spec = importlib.util.spec_from_file_location(f"delivery_{task_dir.name}", verifier_py)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load {verifier_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.task


def fetch_log(host: str, port: int) -> dict:
    url = f"http://{host}:{port}/dev-log"
    try:
        with urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        if "Connection refused" in reason or "10061" in reason:
            print(f"\nCould not connect to {url}", file=sys.stderr)
            print("Make sure the mock is running:  npm run dev  (in mock/)", file=sys.stderr)
        elif "404" in reason:
            print(f"\nNo log yet at {url}", file=sys.stderr)
            print("Open the app in your browser and perform some actions first.", file=sys.stderr)
        else:
            print(f"\nHTTP error: {e}", file=sys.stderr)
        sys.exit(1)


def save_log(log: dict, prefix: str) -> Path:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = LOGS_DIR / f"{prefix}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)
    return path


def print_log_details(log: dict, path: Path) -> None:
    sem = log.get("semantic", []) or []
    raw = log.get("raw", []) or []
    outcome = log.get("outcome", {}) or {}
    counts = (outcome.get("summary", {}) or {}).get("shapeCounts", {}) or {}

    print(f"\n✓ Log saved → {path}")
    print(f"  sessionId : {log.get('sessionId', '?')}")
    print(f"  raw       : {len(raw)} events")
    print(f"  semantic  : {len(sem)} events")
    if counts:
        joined = ", ".join(f"{k}={v}" for k, v in sorted(counts.items()))
        print(f"  shapes    : {joined}")
    if sem:
        head = sem[:8]
        tail = sem[-5:] if len(sem) > 13 else []
        print("  semantic head:")
        for ev in head:
            print(f"    • {_fmt_event(ev)}")
        if tail:
            print(f"    … (+{len(sem) - len(head) - len(tail)} more) …")
            for ev in tail:
                print(f"    • {_fmt_event(ev)}")


def _fmt_event(ev: dict) -> str:
    name = ev.get("name", "?")
    extra = {k: v for k, v in ev.items() if k not in ("name", "timestamp", "ts")}
    if extra:
        return f"{name}  {json.dumps(extra, default=str)[:80]}"
    return name


def score_log(task, log_path: Path):
    from verifier.loader import load_log
    from verifier.types import TaskResult

    log = load_log(str(log_path))
    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)
    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)
    return TaskResult(
        task_id=task.id,
        log_path=str(log_path),
        rubrics=rubric_results,
        base_score=base_score,
        efficiency=efficiency,
        final_score=final_score,
    )


def print_result(result) -> None:
    max_base = sum(r.max_score for r in result.rubrics)
    print(f"\nTask : {result.task_id}")
    print(f"Log  : {result.log_path}")
    print("─" * 56)
    for r in result.rubrics:
        pct = f"{r.score / r.max_score * 100:.0f}%" if r.max_score else "—"
        print(f"  {r.name:<16} {r.score:.4f} / {r.max_score:.1f}   ({pct})")
        for c in r.checks:
            mark = "✓" if c.passed else "✗"
            print(f"    {mark} {c.message}")
    print("─" * 56)
    print(f"  {'base_score':<16} {result.base_score:.4f} / {max_base:.1f}")
    print(f"  {'efficiency':<16} ×{result.efficiency.multiplier:.4f}  ({result.efficiency.message})")
    print(f"  {'FINAL':<16} {result.final_score:.4f} / {max_base:.1f}")
    print()


def save_result(result, task_dir: Path) -> Path:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SCORES_DIR / f"{task_dir.name}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(result), f, indent=2)
    return path


def cmd_full_pipeline(task_input: str, host: str, port: int) -> None:
    task_dir = resolve_task(task_input)
    if task_dir.name != task_input:
        print(f"Resolved '{task_input}' → {task_dir.name}")

    task = load_task(task_dir)

    print(f"Fetching log from http://{host}:{port}/dev-log …")
    log = fetch_log(host, port)
    log_path = save_log(log, task_dir.name)
    print_log_details(log, log_path)

    result = score_log(task, log_path)
    print_result(result)
    score_path = save_result(result, task_dir)
    print(f"Score saved → {score_path}")


def cmd_export_only(task_input: str | None, host: str, port: int) -> None:
    prefix = "log"
    if task_input:
        task_dir = resolve_task(task_input)
        if task_dir.name != task_input:
            print(f"Resolved '{task_input}' → {task_dir.name}")
        prefix = task_dir.name

    print(f"Fetching log from http://{host}:{port}/dev-log …")
    log = fetch_log(host, port)
    log_path = save_log(log, prefix)
    print_log_details(log, log_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the current session log and (optionally) run a verifier task.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/run_task.py task_01\n"
            "  python scripts/run_task.py 1\n"
            "  python scripts/run_task.py export-log\n"
            "  python scripts/run_task.py export-log task_01\n"
            "  python scripts/run_task.py --host mock task_01"
        ),
    )
    parser.add_argument("target", help="task name (e.g. 'task_01' or '1') or the literal 'export-log'")
    parser.add_argument("task", nargs="?", help="optional task name after 'export-log' (used as filename prefix)")
    parser.add_argument("--host", default="localhost", help="mock dev-server host (default localhost)")
    parser.add_argument("--port", type=int, default=5173, help="Vite dev server port (default 5173)")
    args = parser.parse_args()

    if args.target == "export-log":
        cmd_export_only(args.task, args.host, args.port)
    else:
        if args.task is not None:
            parser.error(f"Unexpected extra argument '{args.task}'. For export-only use: export-log [task]")
        cmd_full_pipeline(args.target, args.host, args.port)


if __name__ == "__main__":
    main()

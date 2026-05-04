#!/usr/bin/env python3
"""
run_task.py — Export the current session log and (optionally) run a verifier task.

Usage:
  python scripts/run_task.py task_01                            # full pipeline (export + score)
  python scripts/run_task.py task_01_house_task_comprehensive   # full name also works
  python scripts/run_task.py export-log                         # export only, no scoring
  python scripts/run_task.py export-log task_01                 # export only, prefix filename with task

Requires the verifier's dependencies (pyyaml). The simplest way is to invoke
this script with the verifier venv's python:
  test-verifier/.venv/Scripts/python scripts/run_task.py task_01
"""

import argparse
import dataclasses
import importlib
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from urllib.error import URLError

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_VERIFIER = REPO_ROOT / "test-verifier"
TASKS_DIR = TEST_VERIFIER / "tasks"
LOGS_DIR = TEST_VERIFIER / "logs"
SCORES_DIR = TEST_VERIFIER / "scores"

sys.path.insert(0, str(TEST_VERIFIER))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def list_task_modules() -> list[str]:
    return sorted(p.stem for p in TASKS_DIR.glob("*.py") if p.stem != "__init__")


def resolve_task(name: str) -> str:
    modules = list_task_modules()
    if not modules:
        raise SystemExit(f"No task files found in {TASKS_DIR}")

    if name in modules:
        return name

    prefix_matches = [m for m in modules if m.startswith(name + "_")]
    if len(prefix_matches) == 1:
        return prefix_matches[0]
    if len(prefix_matches) > 1:
        listing = "\n  ".join(prefix_matches)
        raise SystemExit(f"Ambiguous task name '{name}'. Matches:\n  {listing}")

    listing = "\n  ".join(modules)
    raise SystemExit(f"No task matching '{name}'. Available tasks:\n  {listing}")


def fetch_log(port: int) -> dict:
    url = f"http://localhost:{port}/dev-log"
    try:
        with urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        if "Connection refused" in reason or "10061" in reason:
            print(f"\nCould not connect to {url}", file=sys.stderr)
            print("Make sure the test-app is running:  npm run dev  (in test-app/)", file=sys.stderr)
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


def print_log_summary(log: dict, path: Path) -> None:
    sem = len(log.get("semantic", []))
    raw = len(log.get("raw", []))
    print(f"\n✓ Log saved → {path}")
    print(f"  sessionId : {log.get('sessionId', '?')}")
    print(f"  semantic  : {sem} events")
    print(f"  raw       : {raw} events")


def run_verifier(task_module: str, log_path: Path):
    try:
        import yaml  # noqa: F401
    except ImportError:
        venv_python = TEST_VERIFIER / ".venv" / "Scripts" / "python.exe"
        print("\nMissing dependency 'pyyaml' (needed by the verifier).", file=sys.stderr)
        print(f"Run this script with the verifier venv's python instead:", file=sys.stderr)
        print(f"  {venv_python} scripts/run_task.py ...", file=sys.stderr)
        sys.exit(1)

    from verifier.loader import load_log

    mod = importlib.import_module(f"tasks.{task_module}")
    task = mod.task
    log = load_log(str(log_path))

    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)
    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)

    from verifier.types import TaskResult
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


def save_result(result) -> Path:
    SCORES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = SCORES_DIR / f"{result.task_id}_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(result), f, indent=2)
    return path


def cmd_full_pipeline(task_input: str, port: int) -> None:
    task_module = resolve_task(task_input)
    if task_module != task_input:
        print(f"Resolved '{task_input}' → {task_module}")

    print(f"Fetching log from http://localhost:{port}/dev-log …")
    log = fetch_log(port)
    log_path = save_log(log, task_module)
    print_log_summary(log, log_path)

    result = run_verifier(task_module, log_path)
    print_result(result)
    score_path = save_result(result)
    print(f"Score saved → {score_path}")


def cmd_export_only(task_input: str | None, port: int) -> None:
    prefix = "log"
    if task_input:
        task_module = resolve_task(task_input)
        if task_module != task_input:
            print(f"Resolved '{task_input}' → {task_module}")
        prefix = task_module

    print(f"Fetching log from http://localhost:{port}/dev-log …")
    log = fetch_log(port)
    log_path = save_log(log, prefix)
    print_log_summary(log, log_path)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export the current session log and (optionally) run a verifier task.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scripts/run_task.py task_01\n"
            "  python scripts/run_task.py task_01_house_task_comprehensive\n"
            "  python scripts/run_task.py export-log\n"
            "  python scripts/run_task.py export-log task_01"
        ),
    )
    parser.add_argument("target", help="task name (e.g. 'task_01') or the literal 'export-log'")
    parser.add_argument("task", nargs="?", help="optional task name after 'export-log' (used as filename prefix)")
    parser.add_argument("--port", type=int, default=5173, help="Vite dev server port (default 5173)")
    args = parser.parse_args()

    if args.target == "export-log":
        cmd_export_only(args.task, args.port)
    else:
        if args.task is not None:
            parser.error(f"Unexpected extra argument '{args.task}'. For export-only use: export-log [task]")
        cmd_full_pipeline(args.target, args.port)


if __name__ == "__main__":
    main()

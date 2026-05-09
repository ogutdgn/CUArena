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
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

APP_ROOT     = Path(__file__).resolve().parent.parent       # apps/figma/
SCRIPTS_DIR  = Path(__file__).resolve().parent              # apps/figma/scripts/
DELIVERY_DIR = APP_ROOT / "delivery-1"
OUTPUT_ROOT  = Path(os.getenv("FIGMA_OUTPUT_DIR", str(SCRIPTS_DIR)))
LOGS_DIR     = OUTPUT_ROOT / "logs"
SCORES_DIR   = OUTPUT_ROOT / "scores"

# Make `from verifier... import ...` work inside delivery-1/task_NN/verifier.py
sys.path.insert(0, str(APP_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class MissingDevLogError(RuntimeError):
    """Raised when /dev-log exists but no session log has been posted yet."""

    def __init__(self, url: str, session_id: str | None = None):
        super().__init__(f"No log yet at {url}")
        self.url = url
        self.session_id = session_id


def _build_url(host: str, port: int, path: str, session_id: str | None = None) -> str:
    base = f"http://{host}:{port}{path}"
    if session_id:
        return f"{base}?{urlencode({'sessionId': session_id})}"
    return base


def fetch_log_status(host: str, port: int, session_id: str | None = None) -> dict | None:
    url = _build_url(host, port, "/dev-log/status", session_id=session_id)
    try:
        with urlopen(url, timeout=3) as r:
            return json.loads(r.read())
    except Exception:
        return None


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


def fetch_log(host: str, port: int, session_id: str | None = None) -> dict:
    url = _build_url(host, port, "/dev-log", session_id=session_id)
    try:
        with urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except HTTPError as e:
        if e.code == 404:
            raise MissingDevLogError(url, session_id=session_id) from e
        print(f"\nHTTP error: {e}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        reason = str(getattr(e, "reason", e))
        if "Connection refused" in reason or "10061" in reason:
            print(f"\nCould not connect to {url}", file=sys.stderr)
            print("Make sure the mock is running:  npm run dev  (in mock/)", file=sys.stderr)
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


def forced_zero_result(task, log_path: Path, reason: str):
    from verifier.types import CheckResult, EfficiencyResult, RubricResult, TaskResult

    rubric_results: list[RubricResult] = []
    for rubric in task.rubrics:
        checks = getattr(rubric, "checks", []) or []
        check_count = len(checks) if checks else 1
        check_results = [
            CheckResult(
                passed=False,
                score=0.0,
                max_score=1.0,
                message=reason,
            )
            for _ in range(check_count)
        ]
        max_score = float(getattr(rubric, "weight", 0.5))
        rubric_results.append(
            RubricResult(
                name=str(getattr(rubric, "name", "rubric")),
                score=0.0,
                max_score=max_score,
                checks=check_results,
            )
        )

    target_turns = int(getattr(task.efficiency, "target_turns", 0) or 0)
    lam = getattr(task.efficiency, "lambda_", None)
    lambda_used = float(lam if lam is not None else 0.0)
    efficiency = EfficiencyResult(
        multiplier=1.0,
        actual_turns=0,
        target_turns=target_turns,
        lambda_used=lambda_used,
        message="Forced zero result: no /dev-log payload was available.",
    )
    return TaskResult(
        task_id=task.id,
        log_path=str(log_path),
        rubrics=rubric_results,
        base_score=0.0,
        efficiency=efficiency,
        final_score=0.0,
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


def cmd_full_pipeline(task_input: str, host: str, port: int, session_id: str | None = None) -> None:
    task_dir = resolve_task(task_input)
    if task_dir.name != task_input:
        print(f"Resolved '{task_input}' → {task_dir.name}")

    task = load_task(task_dir)

    fetch_url = _build_url(host, port, "/dev-log", session_id=session_id)
    print(f"Fetching log from {fetch_url} …")
    try:
        log = fetch_log(host, port, session_id=session_id)
        log_path = save_log(log, task_dir.name)
        print_log_details(log, log_path)
        result = score_log(task, log_path)
    except MissingDevLogError as e:
        print(f"\nNo session log available at {e.url}.")
        status = fetch_log_status(host, port, session_id=session_id)
        if status:
            print(
                "Relay status:"
                f" hasLog={status.get('hasLog')}"
                f", postCount={status.get('postCount')}"
                f", sessionCount={status.get('sessionCount')}"
                f", selectedSessionId={status.get('selectedSessionId')}"
                f", lastSessionId={status.get('lastSessionId')}"
            )
            if session_id:
                print(f"Requested sessionId: {session_id}")
            if int(status.get("postCount") or 0) == 0:
                print(
                    "No browser log POST has reached this mock instance yet."
                    f" Open http://{host}:{port}, hard-refresh, interact once, wait 0.5s, then rerun."
                )
        print("Returning forced zero score for this run.")
        ts_ms = int(datetime.now().timestamp() * 1000)
        empty_log = {
            "schemaVersion": 1,
            "sessionId": "missing_dev_log",
            "exportedAt": ts_ms,
            "raw": [],
            "semantic": [],
            "outcome": {
                "schemaVersion": 1,
                "sessionId": "missing_dev_log",
                "capturedAt": ts_ms,
                "activePageId": "",
                "summary": {"semanticEventCount": 0, "shapeCounts": {}},
                "document": {"id": "document_missing_dev_log", "schemaVersion": 1, "pages": []},
            },
        }
        log_path = save_log(empty_log, f"{task_dir.name}_missing")
        print_log_details(empty_log, log_path)
        result = forced_zero_result(
            task,
            log_path,
            "No interaction log captured; rubric forced to 0.0.",
        )
    print_result(result)
    score_path = save_result(result, task_dir)
    print(f"Score saved → {score_path}")


def cmd_export_only(task_input: str | None, host: str, port: int, session_id: str | None = None) -> None:
    prefix = "log"
    if task_input:
        task_dir = resolve_task(task_input)
        if task_dir.name != task_input:
            print(f"Resolved '{task_input}' → {task_dir.name}")
        prefix = task_dir.name

    fetch_url = _build_url(host, port, "/dev-log", session_id=session_id)
    print(f"Fetching log from {fetch_url} …")
    log = fetch_log(host, port, session_id=session_id)
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
            "  python scripts/run_task.py --host mock task_01\n"
            "  python scripts/run_task.py --host mock --session-id <uuid> task_01"
        ),
    )
    parser.add_argument("target", help="task name (e.g. 'task_01' or '1') or the literal 'export-log'")
    parser.add_argument("task", nargs="?", help="optional task name after 'export-log' (used as filename prefix)")
    parser.add_argument("--host", default="localhost", help="mock dev-server host (default localhost)")
    parser.add_argument("--port", type=int, default=5173, help="Vite dev server port (default 5173)")
    parser.add_argument("--session-id", default=None, help="optional sessionId to fetch from /dev-log")
    args = parser.parse_args()

    if args.target == "export-log":
        cmd_export_only(args.task, args.host, args.port, session_id=args.session_id)
    else:
        if args.task is not None:
            parser.error(f"Unexpected extra argument '{args.task}'. For export-only use: export-log [task]")
        cmd_full_pipeline(args.target, args.host, args.port, session_id=args.session_id)


if __name__ == "__main__":
    main()

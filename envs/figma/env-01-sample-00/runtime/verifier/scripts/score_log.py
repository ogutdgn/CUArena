#!/usr/bin/env python3
"""
score_log.py — Score an existing log file against a delivery-1 task verifier.

Usage:
  python scripts/score_log.py --task 01            --log scripts/logs/<file>.json
  python scripts/score_log.py --task task_01       --log scripts/logs/<file>.json

Loads the verifier from delivery task_NN/verifier.py.
Saves the score to runtime/output/Competitor-logs-scores/task_XX/scores/<task>_<timestamp>.json and prints both
the log details and the score breakdown to stdout.

Run with the verifier venv's python (it has pyyaml):
  ../.venv/Scripts/python scripts/score_log.py --task 01 --log scripts/logs/<file>.json
"""

from __future__ import annotations

import argparse
import dataclasses
import importlib.util
import json
import os
import sys
from datetime import datetime
from pathlib import Path

APP_ROOT     = Path(__file__).resolve().parent.parent
SCRIPTS_DIR  = Path(__file__).resolve().parent
DELIVERY_DIR = Path(os.getenv("FIGMA_DELIVERY_DIR", str(APP_ROOT / "tasks")))
OUTPUT_ROOT  = Path(os.getenv("FIGMA_OUTPUT_DIR", str(APP_ROOT / "output")))
LOGS_DIR     = OUTPUT_ROOT / "logs"
SCORES_DIR   = OUTPUT_ROOT / "scores"

sys.path.insert(0, str(APP_ROOT))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def list_task_dirs() -> list[Path]:
    return sorted(p for p in DELIVERY_DIR.glob("task_*") if (p / "verifier.py").is_file())


def resolve_task(name: str) -> Path:
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


def print_log_details(log: dict, log_path: Path) -> None:
    sem = log.get("semantic", []) or []
    raw = log.get("raw", []) or []
    outcome = log.get("outcome", {}) or {}
    counts = (outcome.get("summary", {}) or {}).get("shapeCounts", {}) or {}

    print(f"\n✓ Log loaded ← {log_path}")
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


def main() -> None:
    parser = argparse.ArgumentParser(description="Score an existing log file against a delivery-1 task.")
    parser.add_argument("--task", required=True, help="task name (e.g. 'task_01' or '1')")
    parser.add_argument("--log",  required=True, help="path to log JSON file")
    args = parser.parse_args()

    task_dir = resolve_task(args.task)
    if task_dir.name != args.task:
        print(f"Resolved '{args.task}' → {task_dir.name}")

    task = load_task(task_dir)

    from verifier.loader import load_log
    from verifier.types import TaskResult

    log_path = Path(args.log)
    log = load_log(str(log_path))
    print_log_details(log, log_path)

    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)
    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)

    result = TaskResult(
        task_id=task.id,
        log_path=str(log_path),
        rubrics=rubric_results,
        base_score=base_score,
        efficiency=efficiency,
        final_score=final_score,
    )
    print_result(result)

    out_dir = OUTPUT_ROOT / "Competitor-logs-scores" / task_dir.name / "scores"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = out_dir / f"{task_dir.name}_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(dataclasses.asdict(result), f, indent=2)
    print(f"Score saved → {out_path}")


if __name__ == "__main__":
    main()

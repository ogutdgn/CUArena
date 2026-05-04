#!/usr/bin/env python3
"""
Verifier CLI.

Usage:
  python run.py --task house_task --log logs/house_sample.json
  python run.py --task 01          --log logs/house_sample.json   # numeric prefix
  python run.py --task task_01     --log logs/house_sample.json   # short prefix

When the task name resolves to task_NN_*, the result + a copy of the input log
+ a reward.txt are routed to delivery-1/task_NN/output/<timestamp>/ if that
folder structure exists. Otherwise output falls back to test-verifier/scores/.
"""

from __future__ import annotations

import argparse
import dataclasses
import glob
import importlib
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

from verifier.loader import load_log
from verifier.types import TaskResult

REPO_ROOT  = Path(__file__).resolve().parent.parent
TASKS_DIR  = Path(__file__).parent / "tasks"
SCORES_DIR = Path(__file__).parent / "scores"
DELIVERY_ROOT = REPO_ROOT / "delivery-1"


def resolve_task_name(arg: str) -> str:
    """Accept full module name, 'task_NN', or just 'NN' / 'N'.
    Returns the full module name (filename stem) of the matching verifier file."""
    if (TASKS_DIR / f"{arg}.py").exists():
        return arg
    if arg.isdigit():
        prefix = f"task_{arg.zfill(2)}_"
    elif arg.startswith("task_") and not arg.endswith("_"):
        prefix = arg + "_"
    else:
        prefix = arg
    matches = sorted(TASKS_DIR.glob(f"{prefix}*.py"))
    if matches:
        return matches[0].stem
    return arg   # fall through; importlib will raise a clear error


def task_number_from_name(task_name: str) -> str | None:
    m = re.match(r"task_(\d+)", task_name)
    return m.group(1) if m else None


def run_task(task_name: str, log_path: str) -> TaskResult:
    try:
        mod = importlib.import_module(f"tasks.{task_name}")
    except ModuleNotFoundError:
        print(f"Error: task '{task_name}' not found in tasks/.", file=sys.stderr)
        sys.exit(1)

    task = mod.task
    log = load_log(log_path)

    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)

    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)

    return TaskResult(
        task_id=task.id,
        log_path=log_path,
        rubrics=rubric_results,
        base_score=base_score,
        efficiency=efficiency,
        final_score=final_score,
    )


def save_result(result: TaskResult, task_name: str, log_path: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nn = task_number_from_name(task_name)
    if nn and (DELIVERY_ROOT / f"task_{nn}").exists():
        run_dir = DELIVERY_ROOT / f"task_{nn}" / "output" / timestamp
        run_dir.mkdir(parents=True, exist_ok=True)
        # Copy input log so the run is self-contained
        try:
            shutil.copy(log_path, run_dir / "log.json")
        except (FileNotFoundError, shutil.SameFileError):
            pass
        # Single-line reward (final score)
        (run_dir / "reward.txt").write_text(f"{result.final_score:.4f}\n")
        # Full result (rubric breakdown, efficiency, etc.)
        result_path = run_dir / "result.json"
        with open(result_path, "w") as f:
            json.dump(dataclasses.asdict(result), f, indent=2)
        return result_path

    SCORES_DIR.mkdir(exist_ok=True)
    out_path = SCORES_DIR / f"{result.task_id}_{timestamp}.json"
    with open(out_path, "w") as f:
        json.dump(dataclasses.asdict(result), f, indent=2)
    return out_path


def print_result(result: TaskResult) -> None:
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
    parser = argparse.ArgumentParser(description="Run a task verifier against a log file.")
    parser.add_argument("--task", required=True,
                        help="Task module name OR numeric prefix (01, 1, task_01)")
    parser.add_argument("--log",  required=True, help="Path to log JSON file")
    args = parser.parse_args()

    task_name = resolve_task_name(args.task)
    result = run_task(task_name, args.log)
    print_result(result)

    print(json.dumps(dataclasses.asdict(result), indent=2))

    out_path = save_result(result, task_name, args.log)
    print(f"\nResult saved → {out_path}")


if __name__ == "__main__":
    main()

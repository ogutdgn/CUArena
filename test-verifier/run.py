#!/usr/bin/env python3
"""
Verifier CLI.

Usage:
  python run.py --task house_task --log logs/house_sample.json
"""

import argparse
import dataclasses
import importlib
import json
import sys
from datetime import datetime
from pathlib import Path

from verifier.loader import load_log
from verifier.types import TaskResult

SCORES_DIR = Path(__file__).parent / "scores"


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


def save_result(result: TaskResult) -> Path:
    SCORES_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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
    parser.add_argument("--task", required=True, help="Task module name (e.g. house_task)")
    parser.add_argument("--log",  required=True, help="Path to log JSON file")
    args = parser.parse_args()

    result = run_task(args.task, args.log)
    print_result(result)

    print(json.dumps(dataclasses.asdict(result), indent=2))

    out_path = save_result(result)
    print(f"\nResult saved → {out_path}")


if __name__ == "__main__":
    main()

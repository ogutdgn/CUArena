"""Re-score every attempt's log.json using the (now-patched) verifiers.

For each attempt under cua-eval/runs/<run_id>/openrouter/task_*/attempt_*/:
  - Load the existing log.json
  - Find the matching delivery-1/task_*/verifier.py
  - Call runner.score_log() to get a fresh TaskResult
  - Write a new score.json (back up the old one to score.json.bak first)
  - Write a refreshed outcome.json with the new final_score

After all runs are rescored, regenerate merged_attempts.json via merge_runs.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/rescore_rollouts.py
"""
from __future__ import annotations

import dataclasses
import json
import shutil
import sys
import time
from pathlib import Path

APP_ROOT = Path(__file__).resolve().parents[2]
RUNS = APP_ROOT / "cua-eval" / "runs"
DELIVERY = APP_ROOT / "delivery-1"

EVAL_ROOT = APP_ROOT / "cua-eval"
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))
if str(EVAL_ROOT) not in sys.path:
    sys.path.insert(0, str(EVAL_ROOT))


def main() -> int:
    from runner.runner import load_task, score_log

    rescored = 0
    skipped = 0
    runs = [
        RUNS / "qwen35_parallel_10x_20260510_144617",
        RUNS / "qwen35_fillin_20260510_155010",
        RUNS / "qwen35_fillin2_20260510_163353",
        RUNS / "qwen35_fillin3_20260510_170851",
    ]

    # Cache loaded tasks by task_dir_name to avoid re-importing 50 times per run
    task_cache: dict[str, object] = {}

    def get_task(task_dir_name: str):
        if task_dir_name in task_cache:
            return task_cache[task_dir_name]
        task_dir = DELIVERY / task_dir_name
        if not (task_dir / "verifier.py").is_file():
            return None
        task = load_task(task_dir)
        task_cache[task_dir_name] = task
        return task

    for run in runs:
        if not run.is_dir():
            continue
        print(f"\n=== {run.name} ===")
        for outcome_path in sorted(run.rglob("outcome.json")):
            attempt_dir = outcome_path.parent
            log_path = attempt_dir / "log.json"
            score_path = attempt_dir / "score.json"
            task_run_dir = attempt_dir.parent.name  # e.g. task_27_neumorphic_button
            # Map run-dir name (task_NN_descriptive) to delivery dir name (task_NN)
            num_part = task_run_dir.split("_")[0] + "_" + task_run_dir.split("_")[1]  # "task_NN"
            # Handle house_task_comprehensive specially
            if task_run_dir.startswith("house_task"):
                delivery_dir_name = "task_01"  # house is task_01 in delivery
            else:
                delivery_dir_name = num_part

            task = get_task(delivery_dir_name)
            if task is None:
                # try the run-dir name verbatim
                task = get_task(task_run_dir)
            if task is None:
                skipped += 1
                continue

            if not log_path.is_file():
                skipped += 1
                continue

            # Skip errored attempts — they have no real log to rescore
            try:
                old_outcome = json.load(outcome_path.open())
            except Exception:
                skipped += 1
                continue
            if old_outcome.get("stop_reason") == "error":
                skipped += 1
                continue

            # Back up the old score.json once
            if score_path.is_file() and not score_path.with_suffix(".json.bak").is_file():
                shutil.copyfile(score_path, score_path.with_suffix(".json.bak"))
            if not outcome_path.with_suffix(".json.bak").is_file():
                shutil.copyfile(outcome_path, outcome_path.with_suffix(".json.bak"))

            try:
                result = score_log(task, log_path)
            except Exception as exc:
                print(f"  ! {task_run_dir}/{attempt_dir.name}: score failed: {exc}")
                skipped += 1
                continue

            # Write new score.json
            score_path.write_text(
                json.dumps(dataclasses.asdict(result), indent=2), encoding="utf-8"
            )

            # Update outcome.json's score block
            max_base = float(sum(r.max_score for r in result.rubrics))
            old_outcome["score"] = {
                "final": result.final_score,
                "base": result.base_score,
                "max": max_base,
                "efficiency": result.efficiency.multiplier,
                "passed": result.final_score >= old_outcome["score"].get("threshold", 0.7),
                "threshold": old_outcome["score"].get("threshold", 0.7),
            }
            old_outcome["rescored_at"] = int(time.time() * 1000)
            outcome_path.write_text(json.dumps(old_outcome, indent=2), encoding="utf-8")

            rescored += 1
            if rescored % 25 == 0:
                print(f"  rescored {rescored} attempts so far...")

    print(f"\n=== summary ===")
    print(f"  rescored: {rescored}")
    print(f"  skipped:  {skipped} (errored or missing log)")
    print(f"  task cache size: {len(task_cache)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Run a per-task qa_per_task module and summarize results."""
from __future__ import annotations
import argparse
import importlib
import re
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import score_task


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("task_num", help="e.g. 01 or 1")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    nn = args.task_num.zfill(2)

    # Find tasks/task_NN_*.py
    import glob
    matches = sorted(glob.glob(f"tasks/task_{nn}_*.py"))
    if not matches:
        print(f"no task module for {nn}", file=sys.stderr)
        sys.exit(1)
    task_mod_name = os.path.basename(matches[0])[:-3]
    task_mod = importlib.import_module(f"tasks.{task_mod_name}")
    task = task_mod.task

    qa_mod = importlib.import_module(f"qa_per_task.task_{nn}")

    print(f"\n=== Task {nn}: {task_mod_name} ===\n")

    n_bugs = 0
    print("PASS LOGS (expect score ≥ 0.85):")
    for label, log in qa_mod.PASS_LOGS:
        score, breakdown = score_task(task, log)
        flag = "OK" if score >= 0.85 else "BUG-LOW"
        if flag != "OK":
            n_bugs += 1
        print(f"  [{flag:<7}] {label:<28} → {score:.3f}")
        if args.verbose or flag != "OK":
            for name, sc, mx, checks in breakdown["rubrics"]:
                fails = [m for p, m in checks if not p]
                if fails:
                    print(f"      {name}: {sc:.2f}/{mx:.2f}, fails: {fails}")

    print("\nFAIL LOGS (expect specific checks to fail):")
    for entry in qa_mod.FAIL_LOGS:
        if len(entry) == 3:
            label, log, expected_fail_patterns = entry
        else:
            label, log = entry
            expected_fail_patterns = []
        score, breakdown = score_task(task, log)

        # Collect failed check messages
        failed_msgs = []
        for name, sc, mx, checks in breakdown["rubrics"]:
            for passed, msg in checks:
                if not passed:
                    failed_msgs.append(msg)

        # For each expected pattern, did we find a matching failure?
        unmatched = []
        for pat in expected_fail_patterns:
            if not any(re.search(pat, m) for m in failed_msgs):
                unmatched.append(pat)

        if unmatched:
            flag = "BUG-MISS"
            n_bugs += 1
        elif not failed_msgs:
            flag = "BUG-NONE"  # nothing failed at all
            n_bugs += 1
        else:
            flag = "OK"

        print(f"  [{flag:<8}] {label:<28} → {score:.3f}")
        if args.verbose or flag != "OK":
            print(f"      expected fails: {expected_fail_patterns}")
            print(f"      actual fails:   {failed_msgs}")
            if unmatched:
                print(f"      ✗ unmatched:    {unmatched}")

    print(f"\nResult: {n_bugs} bug(s)")
    return 0 if n_bugs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""Run ported per-task QA modules against apps/figma/delivery-1."""
from __future__ import annotations

import argparse
import importlib
import importlib.util
import re
import sys
from pathlib import Path

QA_DIR = Path(__file__).resolve().parent
SCRIPTS_ROOT = QA_DIR.parent
APP_ROOT = SCRIPTS_ROOT.parent
DELIVERY_DIR = APP_ROOT / "delivery-1"

sys.path.insert(0, str(SCRIPTS_ROOT))
sys.path.insert(0, str(APP_ROOT))

from qa_per_task._helpers import score_task  # noqa: E402


def load_task(nn: str):
    verifier_py = DELIVERY_DIR / f"task_{nn}" / "verifier.py"
    if not verifier_py.exists():
        raise FileNotFoundError(f"no delivery verifier for task_{nn}: {verifier_py}")
    spec = importlib.util.spec_from_file_location(f"delivery_task_{nn}_verifier", verifier_py)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod.task


def run_task_qa(nn: str, verbose: bool = False) -> int:
    task = load_task(nn)
    qa_mod = importlib.import_module(f"qa_per_task.task_{nn}")

    print(f"\n=== Task {nn}: delivery-1/task_{nn} ===\n")

    n_bugs = 0
    print("PASS LOGS (expect score >= 0.85):")
    for label, log in qa_mod.PASS_LOGS:
        score, breakdown = score_task(task, log)
        flag = "OK" if score >= 0.85 else "BUG-LOW"
        if flag != "OK":
            n_bugs += 1
        print(f"  [{flag:<7}] {label:<28} -> {score:.3f}")
        if verbose or flag != "OK":
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

        failed_msgs = []
        for _name, _sc, _mx, checks in breakdown["rubrics"]:
            for passed, msg in checks:
                if not passed:
                    failed_msgs.append(msg)

        unmatched = []
        for pat in expected_fail_patterns:
            if not any(re.search(pat, m) for m in failed_msgs):
                unmatched.append(pat)

        if unmatched:
            flag = "BUG-MISS"
            n_bugs += 1
        elif not failed_msgs:
            flag = "BUG-NONE"
            n_bugs += 1
        else:
            flag = "OK"

        print(f"  [{flag:<8}] {label:<28} -> {score:.3f}")
        if verbose or flag != "OK":
            print(f"      expected fails: {expected_fail_patterns}")
            print(f"      actual fails:   {failed_msgs}")
            if unmatched:
                print(f"      unmatched:      {unmatched}")

    print(f"\nResult: {n_bugs} bug(s)")
    return n_bugs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("task_num", help="e.g. 01, 1, or all")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    if args.task_num == "all":
        total_bugs = 0
        for task_dir in sorted(DELIVERY_DIR.glob("task_*")):
            nn = task_dir.name.split("_", 1)[1]
            total_bugs += run_task_qa(nn, args.verbose)
        return 0 if total_bugs == 0 else 1

    nn = args.task_num.zfill(2)
    return 0 if run_task_qa(nn, args.verbose) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

"""Live progress bar for an in-flight pass@k run. Polls the run
directory's outcome.json files and prints a single-line, repainting bar
with pass/fail counters, running pass@k, mean score, cost, and ETA.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/progress_bar.py RUN_DIR [--total 150] [--interval 5]

Example:
    .venv/bin/python cua-eval/runner/progress_bar.py \\
        cua-eval/runs/qwen35_resume_YYYYMMDD_HHMMSS

Press Ctrl-C to exit (the run keeps going).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path


BAR_WIDTH = 30


def _bar(done: int, total: int) -> str:
    if total <= 0:
        return "[" + "?" * BAR_WIDTH + "]"
    frac = min(1.0, done / total)
    filled = int(BAR_WIDTH * frac)
    return "[" + "█" * filled + "░" * (BAR_WIDTH - filled) + f"] {frac*100:5.1f}%"


def _fmt_eta(seconds: float) -> str:
    if seconds <= 0:
        return "0s"
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def snapshot(run_dir: Path) -> dict:
    outcomes = []
    for p in run_dir.rglob("outcome.json"):
        try:
            outcomes.append(json.load(p.open()))
        except Exception:
            pass
    n = len(outcomes)
    passed = sum(1 for o in outcomes if o["score"]["passed"])
    nonzero = sum(1 for o in outcomes if o["score"]["final"] > 0)
    cost = sum((o.get("cost_estimate") or {}).get("total_usd", 0) or 0 for o in outcomes)
    mean_score = (sum(o["score"]["final"] for o in outcomes) / n) if n else 0.0
    elapsed = (sum(o.get("elapsed_s", 0) or 0 for o in outcomes) / n) if n else 0.0
    tasks_seen = len({o["task_id"] for o in outcomes})
    return {
        "n": n,
        "passed": passed,
        "nonzero": nonzero,
        "cost": cost,
        "mean": mean_score,
        "avg_elapsed_per_attempt": elapsed,
        "tasks_seen": tasks_seen,
    }


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("run_dir", type=Path)
    p.add_argument("--total", type=int, default=None,
                   help="Total expected attempts (default: read from run config if present).")
    p.add_argument("--interval", type=float, default=5.0,
                   help="Refresh interval in seconds.")
    args = p.parse_args(argv[1:])

    if not args.run_dir.is_dir():
        print(f"ERROR: not a directory: {args.run_dir}", file=sys.stderr)
        return 2

    # Try to infer total from the run's config if present (passk.py doesn't
    # write one canonically, so fall back to user-supplied --total).
    total = args.total
    if total is None:
        # Look for a per-attempt meta.json to read the task list size + k from CLI argv
        metas = list(args.run_dir.rglob("meta.json"))
        if metas:
            try:
                m = json.load(metas[0].open())
                argv_str = " ".join(m.get("argv", []) or [])
                # Crude parse: find --k N and count --tasks args until next flag
                parts = argv_str.split()
                k = 1
                n_tasks = 0
                in_tasks = False
                for tok in parts:
                    if tok == "--k":
                        in_tasks = False
                    elif tok == "--tasks":
                        in_tasks = True
                        n_tasks = 0
                        continue
                    elif tok.startswith("--"):
                        in_tasks = False
                    if in_tasks and not tok.startswith("--"):
                        n_tasks += 1
                # Find k value
                if "--k" in parts:
                    k = int(parts[parts.index("--k") + 1])
                if n_tasks and k:
                    total = n_tasks * k
            except Exception:
                pass

    start_wall = time.time()
    start_done = None
    print(f"watching {args.run_dir} (refresh every {args.interval:.0f}s)")
    if total:
        print(f"total expected attempts: {total}")
    print()

    try:
        while True:
            s = snapshot(args.run_dir)
            n = s["n"]
            if start_done is None:
                start_done = n
            wall = time.time() - start_wall
            done_since_start = n - start_done
            rate = done_since_start / wall if wall > 0 else 0
            if total and rate > 0:
                eta_s = (total - n) / rate
                eta_str = _fmt_eta(eta_s)
            else:
                eta_str = "?"

            pass1 = (s["passed"] / n * 100) if n else 0.0
            nonzero_pct = (s["nonzero"] / n * 100) if n else 0.0

            line = (
                f"\r{_bar(n, total or n)}  "
                f"{n}/{total or '?':>3}  "
                f"pass@1={pass1:4.1f}%  "
                f"nonzero={nonzero_pct:4.1f}%  "
                f"mean={s['mean']:.3f}  "
                f"cost=${s['cost']:5.2f}  "
                f"ETA={eta_str:>8s}  "
                f"tasks={s['tasks_seen']:>2d}    "
            )
            sys.stdout.write(line)
            sys.stdout.flush()

            if total and n >= total:
                print()
                print("done.")
                return 0
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

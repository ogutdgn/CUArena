"""Merge per-attempt results from multiple pass@k run directories into a
combined headline + per-task table. Useful when a long run had to be
resumed (or split across parallel mocks) and you want a single set of
numbers.

Picks the latest attempt for any (provider, task_id, attempt_index)
duplicate across runs, so a partial-then-resumed attempt is replaced by
the resumed version.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/merge_runs.py \\
        cua-eval/runs/qwen35_full_v2_20260509_224235 \\
        cua-eval/runs/qwen35_resume_YYYYMMDD_HHMMSS

Writes a `merged_summary.md` and `merged_attempts.json` into the
working directory.
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_outcomes(run_dir: Path) -> list[dict[str, Any]]:
    """Load every outcome.json under a run directory. Annotates with
    source_run + attempt_dir mtime for dedup."""
    out: list[dict[str, Any]] = []
    for p in sorted(run_dir.rglob("outcome.json")):
        try:
            d = json.load(p.open())
        except Exception:
            continue
        d["_source_run"] = run_dir.name
        d["_attempt_dir"] = str(p.parent)
        d["_mtime"] = p.stat().st_mtime
        # Infer attempt index from path: openrouter/task_NN/attempt_K/
        try:
            attempt_idx = int(p.parent.name.replace("attempt_", ""))
        except ValueError:
            attempt_idx = 0
        d["_attempt_idx"] = attempt_idx
        out.append(d)
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    runs = [Path(p) for p in argv[1:]]
    for r in runs:
        if not r.is_dir():
            print(f"ERROR: not a directory: {r}", file=sys.stderr)
            return 2

    all_outcomes: list[dict[str, Any]] = []
    for r in runs:
        all_outcomes.extend(load_outcomes(r))

    # Dedup: (provider, task_id, attempt_idx) -> best of all candidates.
    # Preference order:
    #   1. Non-error attempts beat error attempts (rerunning to fill error gaps).
    #   2. Among non-errors, higher final_score wins (rerunning to improve).
    #   3. Tiebreak by latest mtime.
    def _is_error(o: dict[str, Any]) -> bool:
        return o.get("stop_reason") == "error"

    def _score(o: dict[str, Any]) -> float:
        return float((o.get("score") or {}).get("final") or 0.0)

    by_key: dict[tuple[str, str, int], dict[str, Any]] = {}
    for o in all_outcomes:
        key = (o.get("provider", "?"), o.get("task_id", "?"), o["_attempt_idx"])
        prev = by_key.get(key)
        if prev is None:
            by_key[key] = o
            continue
        prev_err, curr_err = _is_error(prev), _is_error(o)
        if prev_err and not curr_err:
            by_key[key] = o
        elif not prev_err and curr_err:
            pass  # keep prev
        elif _score(o) > _score(prev):
            by_key[key] = o
        elif _score(o) == _score(prev) and o["_mtime"] > prev["_mtime"]:
            by_key[key] = o
    merged = sorted(by_key.values(), key=lambda x: (x.get("task_id", ""), x["_attempt_idx"]))

    # Stats
    n = len(merged)
    if n == 0:
        print("no outcomes found in supplied runs")
        return 3

    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for o in merged:
        by_task[o.get("task_id", "?")].append(o)

    complete_tasks = [t for t, xs in by_task.items() if len(xs) >= 3]
    pass1 = sum(1 for o in merged if o["score"]["passed"]) / n * 100
    passk_count = sum(1 for t, xs in by_task.items() if any(x["score"]["passed"] for x in xs))
    passk = passk_count / len(by_task) * 100
    passk_complete_count = sum(1 for t in complete_tasks if any(x["score"]["passed"] for x in by_task[t]))
    passk_complete = passk_complete_count / len(complete_tasks) * 100 if complete_tasks else 0
    mean_score = sum(o["score"]["final"] for o in merged) / n
    cost = sum((o.get("cost_estimate") or {}).get("total_usd", 0) or 0 for o in merged)
    nonzero = sum(1 for o in merged if o["score"]["final"] > 0)
    high = sum(1 for o in merged if o["score"]["final"] >= 0.1)

    # Render summary
    lines = []
    lines.append("# Merged Run Summary")
    lines.append("")
    lines.append(f"- **Sources:** {', '.join(r.name for r in runs)}")
    lines.append(f"- **Total attempts merged:** {n}")
    lines.append(f"- **Tasks seen:** {len(by_task)} / 50")
    lines.append(f"- **Tasks with k=3 complete:** {len(complete_tasks)}")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| pass@1 | **{pass1:.1f}%** ({sum(1 for o in merged if o['score']['passed'])}/{n}) |")
    lines.append(f"| pass@3 (tasks ≥1 pass / all tasks seen) | **{passk:.1f}%** ({passk_count}/{len(by_task)}) |")
    lines.append(f"| pass@3 (only tasks with all 3 attempts) | **{passk_complete:.1f}%** ({passk_complete_count}/{len(complete_tasks)}) |")
    lines.append(f"| mean score | {mean_score:.3f} |")
    lines.append(f"| nonzero scores | {nonzero}/{n} ({nonzero * 100 / n:.0f}%) |")
    lines.append(f"| partial ≥0.1 | {high}/{n} ({high * 100 / n:.0f}%) |")
    lines.append(f"| total cost (est.) | ${cost:.2f} |")
    lines.append("")

    # Passing tasks
    passes = [(t, max((x for x in xs if x["score"]["passed"]),
                      key=lambda x: x["score"]["final"]))
              for t, xs in by_task.items() if any(x["score"]["passed"] for x in xs)]
    if passes:
        lines.append("## Passing tasks")
        lines.append("")
        lines.append("| Task | Best score | Turns | Attempts passing |")
        lines.append("|---|---|---|---|")
        for t, best in sorted(passes):
            n_pass = sum(1 for x in by_task[t] if x["score"]["passed"])
            n_total = len(by_task[t])
            lines.append(f"| `{t}` | {best['score']['final']:.3f} | {best['turns']} | {n_pass}/{n_total} |")
        lines.append("")

    # Top partial-credit tasks (best non-passing)
    best_partials = []
    for t, xs in by_task.items():
        if any(x["score"]["passed"] for x in xs):
            continue
        best_non = max(xs, key=lambda x: x["score"]["final"])
        if best_non["score"]["final"] > 0:
            best_partials.append((t, best_non))
    best_partials.sort(key=lambda kv: -kv[1]["score"]["final"])
    if best_partials:
        lines.append("## Top partial-credit (non-passing) tasks")
        lines.append("")
        lines.append("| Task | Best score | Turns |")
        lines.append("|---|---|---|")
        for t, best in best_partials[:15]:
            lines.append(f"| `{t}` | {best['score']['final']:.3f} | {best['turns']} |")
        lines.append("")

    # Full per-task table
    lines.append("## Per-task detail")
    lines.append("")
    lines.append("| Task | k | Best | Mean | Passed (k of n) |")
    lines.append("|---|---|---|---|---|")
    for t in sorted(by_task):
        xs = by_task[t]
        best = max(xs, key=lambda x: x["score"]["final"])
        mean = sum(x["score"]["final"] for x in xs) / len(xs)
        n_pass = sum(1 for x in xs if x["score"]["passed"])
        lines.append(f"| `{t}` | {len(xs)} | {best['score']['final']:.3f} | {mean:.3f} | {n_pass}/{len(xs)} |")

    summary_md = Path("merged_summary.md")
    summary_md.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {summary_md}")

    # Compact attempts JSON
    compact = []
    for o in merged:
        compact.append({
            "task_id": o.get("task_id"),
            "attempt": o["_attempt_idx"],
            "source_run": o.get("_source_run"),
            "passed": o["score"]["passed"],
            "score": o["score"]["final"],
            "base": o["score"]["base"],
            "max": o["score"]["max"],
            "turns": o["turns"],
            "stop_reason": o["stop_reason"],
            "cost_usd": (o.get("cost_estimate") or {}).get("total_usd", 0),
            "elapsed_s": o.get("elapsed_s"),
        })
    Path("merged_attempts.json").write_text(json.dumps(compact, indent=2), encoding="utf-8")
    print(f"wrote merged_attempts.json")

    # Print headline to stdout for quick view
    print("")
    print("=" * 60)
    print("HEADLINE")
    print("=" * 60)
    print(f"  attempts merged: {n}")
    print(f"  tasks seen:      {len(by_task)} / 50  ({len(complete_tasks)} with k=3 complete)")
    print(f"  pass@1:          {pass1:.1f}%")
    print(f"  pass@3 (all):    {passk:.1f}%  ({passk_count}/{len(by_task)} tasks)")
    print(f"  pass@3 (k=3):    {passk_complete:.1f}%  ({passk_complete_count}/{len(complete_tasks)} complete tasks)")
    print(f"  mean score:      {mean_score:.3f}")
    print(f"  cost (est):      ${cost:.2f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

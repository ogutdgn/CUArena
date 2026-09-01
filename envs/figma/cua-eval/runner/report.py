"""Aggregate per-attempt results into digestible run reports.

Writes:
  <run_root>/summary.csv   one row per attempt
  <run_root>/summary.md    headline pass@k + per-task table per provider
"""
from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean

from .runner import AttemptResult


def _pass_at_k(passes: list[bool], k: int) -> float:
    """pass@k = 1.0 if any of the k attempts passed (assuming we have exactly
    k attempts per task). With fewer attempts, scale by what we have."""
    if not passes:
        return 0.0
    used = passes[:k]
    return 1.0 if any(used) else 0.0


def write_reports(attempts: list[AttemptResult], run_root: Path,
                  *, threshold: float, k: int) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    _write_csv(attempts, run_root / "summary.csv")
    _write_md(attempts, run_root / "summary.md", threshold=threshold, k=k)


def _write_csv(attempts: list[AttemptResult], path: Path) -> None:
    cols = ["provider", "model", "task_id", "passed", "final_score",
            "base_score", "max_score", "efficiency", "turns", "elapsed_s",
            "stop_reason", "input_tokens", "output_tokens",
            "cost_input_usd", "cost_output_usd", "cost_total_usd", "error"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for a in attempts:
            ce = a.cost_estimate or {}
            w.writerow([
                a.provider, a.model, a.task_id,
                "yes" if a.passed else "no",
                f"{a.final_score:.4f}", f"{a.base_score:.4f}", f"{a.max_score:.2f}",
                f"{a.efficiency:.4f}", a.turns, f"{a.elapsed_s:.1f}", a.stop_reason,
                (a.usage or {}).get("input_tokens", ""),
                (a.usage or {}).get("output_tokens", ""),
                ce.get("input_usd", ""), ce.get("output_usd", ""), ce.get("total_usd", ""),
                (a.error or "").replace("\n", " ")[:200],
            ])


def _write_md(attempts: list[AttemptResult], path: Path,
              *, threshold: float, k: int) -> None:
    by_provider: dict[str, list[AttemptResult]] = defaultdict(list)
    for a in attempts:
        by_provider[a.provider].append(a)

    lines: list[str] = []
    lines.append("# CUA Benchmark — Run Summary")
    lines.append("")
    lines.append(f"- Pass threshold: `final_score >= {threshold}`")
    lines.append(f"- k (attempts per task): `{k}`")
    lines.append(f"- Total attempts: `{len(attempts)}`")
    lines.append("")

    lines.append("## Headline")
    lines.append("")
    lines.append("| Provider | Model | Tasks | pass@k | mean score | mean turns | mean s/turn | total in tok | total out tok | est. cost (USD) |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for provider, items in by_provider.items():
        per_task: dict[str, list[AttemptResult]] = defaultdict(list)
        for a in items:
            per_task[a.task_id].append(a)
        passes_per_task = [_pass_at_k([x.passed for x in v], k) for v in per_task.values()]
        passk = mean(passes_per_task) if passes_per_task else 0.0
        mean_score = mean(a.final_score for a in items) if items else 0.0
        mean_turns = mean(a.turns for a in items) if items else 0.0
        per_turn_samples = [a.elapsed_s / a.turns for a in items if a.turns]
        mean_s_per_turn = mean(per_turn_samples) if per_turn_samples else 0.0
        in_tok = sum((a.usage or {}).get("input_tokens", 0) for a in items)
        out_tok = sum((a.usage or {}).get("output_tokens", 0) for a in items)
        cost = sum((a.cost_estimate or {}).get("total_usd", 0.0) for a in items)
        model = items[0].model if items else "?"
        lines.append(f"| {provider} | `{model}` | {len(per_task)} | "
                     f"{passk:.2%} | {mean_score:.3f} | {mean_turns:.1f} | "
                     f"{mean_s_per_turn:.1f} | "
                     f"{in_tok:,} | {out_tok:,} | ${cost:.2f} |")
    lines.append("")

    for provider, items in by_provider.items():
        lines.append(f"## Per-task — {provider}")
        lines.append("")
        lines.append("| Task | Pass | Score | Base / Max | Eff× | Turns | Stop | Error |")
        lines.append("|---|---|---|---|---|---|---|---|")
        per_task: dict[str, list[AttemptResult]] = defaultdict(list)
        for a in items:
            per_task[a.task_id].append(a)
        for task_id in sorted(per_task.keys()):
            best = max(per_task[task_id], key=lambda r: r.final_score)
            mark = "✓" if any(a.passed for a in per_task[task_id]) else "✗"
            err = (best.error or "")[:60]
            lines.append(
                f"| {task_id} | {mark} | {best.final_score:.3f} | "
                f"{best.base_score:.2f} / {best.max_score:.2f} | "
                f"{best.efficiency:.2f} | {best.turns} | {best.stop_reason} | {err} |"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")

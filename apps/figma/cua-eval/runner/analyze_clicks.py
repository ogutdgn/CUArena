"""Postprocess one or more pass@k runs to characterize the model's
click distribution: total parsed clicks, off-viewport rate, top coords,
and consecutive-loop rate. Used to compare the effect of interventions
(e.g. baseline vs --coord-clamp + --loop-break).

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/analyze_clicks.py RUN_DIR [RUN_DIR ...]

Example:
    .venv/bin/python cua-eval/runner/analyze_clicks.py \\
        cua-eval/runs/diag_194718 \\
        cua-eval/runs/intervention_a_HHMMSS
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 800


def _coerce_xy(action: dict[str, Any]) -> tuple[int | None, int | None]:
    """Mirror of openrouter._coerce_xy (kept inline so this script has no
    import dependency on the runner package)."""
    def _to_int(v: Any) -> int | None:
        try:
            return int(v)
        except (TypeError, ValueError):
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return None

    x_raw = action.get("x")
    y_raw = action.get("y")

    if isinstance(x_raw, (list, tuple)) and len(x_raw) >= 2 and y_raw is None:
        return _to_int(x_raw[0]), _to_int(x_raw[1])
    if isinstance(x_raw, str) and y_raw is None:
        s = x_raw.strip().lstrip("[(").rstrip("])")
        if "," in s:
            parts = [p.strip() for p in s.split(",")]
            if len(parts) >= 2:
                xi = _to_int(parts[0])
                yi = _to_int(parts[1])
                if xi is not None and yi is not None:
                    return xi, yi

    coord = action.get("coordinate")
    if isinstance(coord, (list, tuple)) and len(coord) >= 2:
        return _to_int(coord[0]), _to_int(coord[1])

    return _to_int(x_raw), _to_int(y_raw)


def analyze_run(run_dir: Path) -> dict[str, Any]:
    total_actions = 0
    parsed_clicks: list[tuple[int, int]] = []
    off_viewport = 0
    loop_actions = 0
    coord_clamp_count = 0
    loop_break_count = 0
    prev_sig = None
    prev_run = 0
    per_task: list[dict[str, Any]] = []

    for tj_path in sorted(run_dir.rglob("trajectory.jsonl")):
        attempt_dir = tj_path.parent
        # task_id from outcome.json if present, else from path
        outcome_path = attempt_dir / "outcome.json"
        outcome = json.loads(outcome_path.read_text()) if outcome_path.is_file() else {}
        task_id = outcome.get("task_id") or attempt_dir.parent.name

        task_total = 0
        task_off = 0
        task_loops = 0
        task_clamps = 0
        task_breaks = 0
        local_prev_sig = None
        local_prev_run = 0
        for line in tj_path.open():
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            phase = d.get("phase")
            if phase == "intervention":
                kind = d.get("intervention")
                if kind == "coord_clamp":
                    task_clamps += 1
                elif kind == "loop_break":
                    task_breaks += 1
                continue
            if phase != "step":
                continue
            for a in d.get("actions", []):
                total_actions += 1
                task_total += 1
                t = a.get("type")
                if t in ("click", "double_click", "move"):
                    x, y = _coerce_xy(a)
                    if x is not None and y is not None:
                        parsed_clicks.append((x, y))
                        if not (0 <= x <= DISPLAY_WIDTH and 0 <= y <= DISPLAY_HEIGHT):
                            off_viewport += 1
                            task_off += 1
                # Loop signature: type + parsed coords (if any)
                if t in ("click", "double_click", "move"):
                    x, y = _coerce_xy(a)
                    sig = f"{t}:{x}:{y}"
                else:
                    sig = t or "?"
                if sig == prev_sig:
                    prev_run += 1
                    if prev_run >= 2:  # 3rd+ consecutive identical
                        loop_actions += 1
                else:
                    prev_sig = sig
                    prev_run = 0
                if sig == local_prev_sig:
                    local_prev_run += 1
                    if local_prev_run >= 2:
                        task_loops += 1
                else:
                    local_prev_sig = sig
                    local_prev_run = 0

        coord_clamp_count += task_clamps
        loop_break_count += task_breaks
        per_task.append({
            "task_id": task_id,
            "actions": task_total,
            "off_viewport": task_off,
            "off_vp_pct": (task_off * 100.0 / task_total) if task_total else 0.0,
            "loop_actions": task_loops,
            "loop_pct": (task_loops * 100.0 / task_total) if task_total else 0.0,
            "coord_clamp_count": task_clamps,
            "loop_break_count": task_breaks,
            "score": outcome.get("score", {}).get("final"),
            "passed": outcome.get("score", {}).get("passed"),
            "turns": outcome.get("turns"),
            "stop_reason": outcome.get("stop_reason"),
        })

    coord_counter = Counter(parsed_clicks)
    return {
        "run_dir": str(run_dir),
        "total_actions": total_actions,
        "parsed_clicks": len(parsed_clicks),
        "off_viewport_clicks": off_viewport,
        "off_viewport_pct": (off_viewport * 100.0 / len(parsed_clicks)) if parsed_clicks else 0.0,
        "consecutive_loop_actions": loop_actions,
        "loop_pct": (loop_actions * 100.0 / total_actions) if total_actions else 0.0,
        "coord_clamp_count": coord_clamp_count,
        "loop_break_count": loop_break_count,
        "top_5_click_coords": [
            {"coord": list(c), "count": n,
             "in_viewport": 0 <= c[0] <= DISPLAY_WIDTH and 0 <= c[1] <= DISPLAY_HEIGHT}
            for c, n in coord_counter.most_common(5)
        ],
        "unique_click_coords": len(coord_counter),
        "per_task": per_task,
    }


def print_report(stats: dict[str, Any]) -> None:
    print(f"=== {stats['run_dir']} ===")
    print(f"  total actions:           {stats['total_actions']}")
    print(f"  parsed clicks:           {stats['parsed_clicks']}")
    print(f"  off-viewport clicks:     {stats['off_viewport_clicks']} "
          f"({stats['off_viewport_pct']:.1f}%)")
    print(f"  consecutive-loop actions: {stats['consecutive_loop_actions']} "
          f"({stats['loop_pct']:.1f}%)")
    print(f"  unique click coords:     {stats['unique_click_coords']}")
    if stats.get("coord_clamp_count") or stats.get("loop_break_count"):
        print(f"  coord_clamp activations: {stats['coord_clamp_count']}")
        print(f"  loop_break activations:  {stats['loop_break_count']}")
    print(f"  top-5 click coords:")
    for item in stats["top_5_click_coords"]:
        marker = "in" if item["in_viewport"] else "OFF"
        print(f"    {tuple(item['coord'])} x{item['count']}  [{marker}]")
    print(f"  per-task:")
    for t in stats["per_task"]:
        score = t.get("score")
        passed = "✓" if t.get("passed") else "✗"
        score_str = f"{score:.3f}" if isinstance(score, (int, float)) else "?"
        print(f"    {passed} {t['task_id'][:25]:<25}  score={score_str}  "
              f"turns={t.get('turns','?'):>3}  off_vp={t['off_vp_pct']:>5.1f}%  "
              f"loops={t['loop_pct']:>5.1f}%  "
              f"clamps={t.get('coord_clamp_count',0)}  breaks={t.get('loop_break_count',0)}")


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    runs = [Path(p) for p in argv[1:]]
    for r in runs:
        if not r.is_dir():
            print(f"ERROR: not a directory: {r}", file=sys.stderr)
            return 2
    all_stats = [analyze_run(r) for r in runs]
    for s in all_stats:
        print_report(s)
        print()
    if len(all_stats) >= 2:
        print("=== DELTA: ", all_stats[0]["run_dir"], "→", all_stats[-1]["run_dir"], "===")
        a, b = all_stats[0], all_stats[-1]
        delta = lambda k, fmt=".1f": f"{a.get(k,0):>6{fmt}} → {b.get(k,0):>6{fmt}}  Δ={b.get(k,0)-a.get(k,0):+{fmt}}"
        print(f"  off-viewport %:  {delta('off_viewport_pct')}")
        print(f"  loop %:          {delta('loop_pct')}")
        print(f"  unique coords:   {delta('unique_click_coords','d')}")
        print(f"  total actions:   {delta('total_actions','d')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

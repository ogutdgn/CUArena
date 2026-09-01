"""Audit all 50 figma task verifiers against the merged rollout data and
representative log.jsons. Produces audit_data.json + VERIFIER_AUDIT.md.

For each task:
  - Statically introspect the verifier: rubric weights, critical indices,
    every check primitive used, whether a frame is mandated, all tolerance
    values that appear in geometry/alignment checks.
  - Aggregate the 3 attempts from merged_attempts.json: best score, mean,
    range, plateau flag, stop-reason distribution, per-rubric breakdown.
  - From one representative log.json: shape types that appeared in the
    outcome scene graph, and semantic event types the agent emitted.
  - Compute a verdict per task:
      "honest"        — score reflects model capability on what prompt asked
      "verifier-gap"  — verifier requires something not in prompt OR uses
                        brittle tolerance OR doesn't grant partial credit
      "mock-gap"      — verifier expects a shape type the mock never logged
      "model-gap"     — model never attempted the required tool/action

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/audit_verifiers.py
"""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

APP_ROOT = Path(__file__).resolve().parents[2]   # apps/figma/
DELIVERY = APP_ROOT / "delivery-1"
RUNS = APP_ROOT / "cua-eval" / "runs"

# Make `from verifier.* import *` work
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))


# ---------------------------------------------------------------- static load
def load_task_module(task_dir: Path) -> Any:
    """Import the task's verifier.py as a fresh module and return mod.task."""
    spec = importlib.util.spec_from_file_location(
        f"audit_{task_dir.name}", task_dir / "verifier.py"
    )
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.task


def introspect_check(check: Any) -> dict[str, Any]:
    """Extract class name + dataclass fields from a check instance."""
    cls = type(check).__name__
    try:
        params = dataclasses.asdict(check) if dataclasses.is_dataclass(check) else dict(vars(check))
    except Exception:
        try:
            params = {k: v for k, v in vars(check).items() if not k.startswith("_")}
        except Exception:
            params = {}
    return {"check": cls, "params": params}


def introspect_task(task_dir: Path) -> dict[str, Any]:
    task = load_task_module(task_dir)
    if task is None:
        return {"task_dir": task_dir.name, "error": "could not load"}

    rubrics_out = []
    for r in task.rubrics:
        checks = []
        for c in r.checks:
            checks.append(introspect_check(c))
        rubrics_out.append({
            "name": getattr(r, "name", type(r).__name__),
            "weight": float(getattr(r, "weight", 0.5)),
            "critical": list(getattr(r, "critical", []) or []),
            "checks": checks,
        })

    # Aggregate static properties of interest
    frame_required = False
    has_alignment_tol_under_15 = False
    tolerances: list[float] = []
    check_classes: Counter = Counter()
    for r in rubrics_out:
        for c in r["checks"]:
            check_classes[c["check"]] += 1
            p = c.get("params", {})
            if (c["check"] == "LayerInsideFrame"
                    or (c["check"] == "AllLayerBoundsInside" and p.get("outer_type") == "frame")):
                frame_required = True
            tol = p.get("tolerance")
            if isinstance(tol, (int, float)):
                tolerances.append(float(tol))
                if c["check"].startswith("Layers") and tol < 15:
                    has_alignment_tol_under_15 = True

    # Required shape types from ShapeCount/ShapeCountAtLeast
    required_shapes: Counter = Counter()
    for r in rubrics_out:
        for c in r["checks"]:
            if c["check"] in ("ShapeCount", "ShapeCountAtLeast"):
                lt = c["params"].get("layer_type")
                if lt:
                    required_shapes[lt] += 1

    target_turns = getattr(task.efficiency, "target_turns", None)
    return {
        "task_dir": task_dir.name,
        "task_id": task.id,
        "scope": getattr(task, "scope", "in_scope"),
        "description": (task.description or "").strip(),
        "rubrics": rubrics_out,
        "frame_required": frame_required,
        "brittle_alignment_tolerance": has_alignment_tol_under_15,
        "all_tolerances": tolerances,
        "check_class_counts": dict(check_classes),
        "required_shape_types": dict(required_shapes),
        "target_turns": target_turns,
    }


# ---------------------------------------------------------------- rollout data
def load_merged_outcomes(merged_path: Path) -> dict[str, list[dict[str, Any]]]:
    """Index merged_attempts.json by task_id."""
    data = json.load(merged_path.open())
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in data:
        by_task[a["task_id"]].append(a)
    return by_task


def aggregate_rollout(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    if not attempts:
        return {"best": None, "mean": None, "range": None, "n_pass": 0, "plateau": False,
                "stops": {}, "n_attempts": 0}
    scores = [float(a["score"]) for a in attempts]
    stops = dict(Counter(a["stop_reason"] for a in attempts))
    n_pass = sum(1 for a in attempts if a["passed"])
    rng = max(scores) - min(scores)
    return {
        "best": max(scores),
        "mean": sum(scores) / len(scores),
        "range": rng,
        "plateau": rng < 0.05 and min(scores) > 0,
        "n_pass": n_pass,
        "n_attempts": len(attempts),
        "stops": stops,
    }


def find_score_json(task_id: str, runs: list[Path]) -> Path | None:
    """Find a representative non-error score.json for the task (max score)."""
    candidates: list[tuple[float, Path]] = []
    for run in runs:
        # task_id is e.g. "task_27_neumorphic_button"; directory is "task_27"
        for sp in run.rglob("score.json"):
            try:
                d = json.load(sp.open())
            except Exception:
                continue
            if d.get("task_id") == task_id:
                candidates.append((float(d.get("final_score", 0)), sp))
    if not candidates:
        return None
    candidates.sort(key=lambda kv: -kv[0])
    return candidates[0][1]


def load_rubric_breakdown(score_json_path: Path | None) -> dict[str, Any] | None:
    if score_json_path is None or not score_json_path.is_file():
        return None
    try:
        d = json.load(score_json_path.open())
    except Exception:
        return None
    out = []
    for r in d.get("rubrics", []):
        out.append({
            "name": r.get("name"),
            "score": round(float(r.get("score", 0)), 4),
            "max_score": round(float(r.get("max_score", 0)), 4),
            "n_checks": len(r.get("checks", [])),
            "n_pass": sum(1 for c in r.get("checks", []) if c.get("passed")),
            "fail_messages": [c.get("message") for c in r.get("checks", []) if not c.get("passed")][:5],
        })
    return {
        "source": str(score_json_path),
        "final_score": float(d.get("final_score", 0)),
        "rubrics": out,
    }


def scan_logs_for_task(task_dir_name: str, runs: list[Path]) -> dict[str, Any]:
    """Inspect every log.json for this task across all runs. Return what shape
    types and semantic event types appeared. This tells us whether the mock
    is producing certain shape types at all."""
    shape_types: Counter = Counter()
    event_types: Counter = Counter()
    n_logs = 0
    for run in runs:
        # Directory name in run is just "task_NN" (the number prefix)
        # but task_id is "task_NN_descriptive" — we got task_dir_name from delivery_1 dir
        # which is just "task_NN" (no descriptor). The run dirs use "task_NN_descriptive".
        # So we search by prefix.
        for log_path in run.rglob("log.json"):
            attempt_dir = log_path.parent
            task_run_dir = attempt_dir.parent  # task_NN_descriptive
            # Match by num prefix from task_dir_name (e.g. "task_27" or "house_task_comprehensive")
            if not (task_run_dir.name == task_dir_name
                    or task_run_dir.name.startswith(task_dir_name + "_")):
                continue
            try:
                d = json.load(log_path.open())
            except Exception:
                continue
            n_logs += 1
            outcome = d.get("outcome", {}) or {}
            doc = outcome.get("document", {}) or {}
            for page in doc.get("pages", []) or []:
                for layer in _walk_layers(page.get("children", []) or []):
                    t = layer.get("type")
                    if t:
                        shape_types[t] += 1
            for ev in d.get("semantic", []) or []:
                name = ev.get("name") or ev.get("type")
                if name:
                    event_types[name] += 1
    return {
        "n_logs_seen": n_logs,
        "shape_types_in_outcomes": dict(shape_types),
        "semantic_event_types": dict(event_types.most_common(20)),
    }


def _walk_layers(nodes: list[dict[str, Any]]):
    for n in nodes:
        yield n
        kids = n.get("children")
        if isinstance(kids, list) and kids:
            yield from _walk_layers(kids)


# ---------------------------------------------------------------- verdict
def estimate_post_fix_score(task: dict[str, Any]) -> tuple[float, float, list[str]]:
    """Estimate (current_base, hypothetical_post_verifier_fix, notes).

    Conservative model:
      - Frame fix: for rubrics whose failed-check messages mention 'frame',
        assume one additional check passes.
      - Critical-halving fix: if a rubric's current score equals
        weight × (pass/total) × 0.5 (i.e. it was halved), assume we
        un-halve it.
      - All other failures (e.g. effect rubrics with 0/N pass) stay as
        residual model capability gaps and contribute zero lift.
    """
    breakdown = task.get("score_breakdown") or {}
    rubrics = breakdown.get("rubrics") or []
    if not rubrics:
        return 0.0, 0.0, []
    cur_total = 0.0
    fixed_total = 0.0
    notes: list[str] = []
    frame_required = task.get("frame_required", False)
    for r in rubrics:
        cur = r["score"]
        mx = r["max_score"]
        n_pass = r["n_pass"]
        n_check = r["n_checks"]
        cur_total += cur
        if n_check == 0:
            fixed_total += mx
            continue
        adjusted_pass = n_pass
        if frame_required:
            frame_fails = [m for m in (r.get("fail_messages") or [])
                           if "frame" in (m or "").lower()]
            if frame_fails:
                adjusted_pass = min(n_pass + 1, n_check)
                notes.append(f"frame-fix {r['name']}: +1 check")
        unhalved = mx * (adjusted_pass / n_check)
        if abs(cur - unhalved * 0.5) < 0.005 and adjusted_pass > 0:
            fixed_r = unhalved
            notes.append(f"unhalve {r['name']}: {cur:.3f}->{fixed_r:.3f}")
        elif adjusted_pass > n_pass:
            fixed_r = mx * (adjusted_pass / n_check)
        else:
            fixed_r = cur
        fixed_total += fixed_r
    return cur_total, fixed_total, notes


def compute_verdict(task: dict[str, Any]) -> tuple[str, list[str]]:
    """Return (verdict, reasoning_bullets). Verdict is one of:
       passing            — task already passes (best >= 0.7)
       verifier-primary   — fixing verifier would push past threshold
       model-primary      — verifier issues exist but model is the real blocker
       honest             — verifier looks fine; score reflects model
       mock-gap           — required shape type missing from mock logs
       model-gap          — agent never attempted required tool
    """
    reasons: list[str] = []
    rollout = task["rollout"]
    log_scan = task["log_scan"]
    best = rollout.get("best") or 0.0
    required = task.get("required_shape_types", {}) or {}
    observed = log_scan.get("shape_types_in_outcomes", {}) or {}

    # Hard zero — look for missing shape type signal
    if best == 0.0:
        missing_shapes = [s for s, n in required.items() if observed.get(s, 0) == 0]
        if missing_shapes:
            tool_events = log_scan.get("semantic_event_types", {})
            attempts_for_missing = [s for s in missing_shapes
                                    if any(s in k.lower() for k in tool_events.keys())]
            if attempts_for_missing:
                return "mock-gap", [
                    f"Required {missing_shapes} but only {attempts_for_missing} ever attempted",
                    "Agent attempted the tool but the mock didn't log the shape into outcome.document",
                ]
            return "model-gap", [
                f"Agent never created required shape type(s) {missing_shapes} in any log across {log_scan.get('n_logs_seen',0)} attempts",
            ]

    if best >= 0.7:
        return "passing", [f"Passing ({rollout.get('n_pass',0)}/{rollout.get('n_attempts',0)} attempts)"]

    # Compute post-fix estimate
    cur, fixed, notes = estimate_post_fix_score(task)
    lift = fixed - cur
    if fixed >= 0.7 and lift > 0.05:
        return "verifier-primary", [
            f"Current {cur:.3f}; post-verifier-fix estimate {fixed:.3f} → would pass (lift +{lift:.3f})",
            *notes[:3],
        ]
    if lift > 0.05:
        return "model-primary", [
            f"Verifier fix would lift {cur:.3f} → {fixed:.3f} (+{lift:.3f}), still below 0.7 threshold — model is the bigger gap",
            *notes[:3],
        ]
    return "honest", [
        f"No meaningful verifier-fixable lift ({cur:.3f} → {fixed:.3f}). Score reflects model capability.",
    ]


# ---------------------------------------------------------------- main
def main() -> int:
    print(f"app_root: {APP_ROOT}")

    # Discover task directories
    task_dirs = sorted(d for d in DELIVERY.iterdir()
                       if d.is_dir() and (d / "verifier.py").is_file())
    print(f"task dirs: {len(task_dirs)}")

    # Load merged outcomes
    merged_path = APP_ROOT / "merged_attempts.json"
    if not merged_path.is_file():
        print(f"ERROR: missing {merged_path}", file=sys.stderr)
        return 1
    by_task = load_merged_outcomes(merged_path)
    print(f"merged tasks: {len(by_task)}")

    runs = [
        RUNS / "qwen35_parallel_10x_20260510_144617",
        RUNS / "qwen35_fillin_20260510_155010",
        RUNS / "qwen35_fillin2_20260510_163353",
        RUNS / "qwen35_fillin3_20260510_170851",
    ]
    runs = [r for r in runs if r.is_dir()]
    print(f"runs: {len(runs)}")

    audit: list[dict[str, Any]] = []
    for td in task_dirs:
        rec = introspect_task(td)
        if "error" in rec:
            audit.append(rec)
            continue
        tid = rec["task_id"]
        rec["rollout"] = aggregate_rollout(by_task.get(tid, []))
        rec["score_breakdown"] = load_rubric_breakdown(find_score_json(tid, runs))
        rec["log_scan"] = scan_logs_for_task(td.name, runs)
        rec["verdict"], rec["verdict_reasons"] = compute_verdict(rec)
        audit.append(rec)

    out_path = APP_ROOT / "audit_data.json"
    out_path.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(f"wrote {out_path} ({out_path.stat().st_size:,} bytes)")

    # Summary
    print()
    print("=== verdict summary ===")
    v = Counter(t.get("verdict", "?") for t in audit)
    for k, n in v.most_common():
        print(f"  {k}: {n}")
    print()
    print("=== frame-required count ===")
    print(f"  {sum(1 for t in audit if t.get('frame_required'))} tasks")
    print("=== brittle alignment count ===")
    print(f"  {sum(1 for t in audit if t.get('brittle_alignment_tolerance'))} tasks")
    return 0


if __name__ == "__main__":
    sys.exit(main())

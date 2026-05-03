"""
QA harness for the verifier set.

For each task in tasks/, synthesizes:
  - PERFECT-LOG: shapes/events the task expects, in matching counts
  - EMPTY-LOG: no shapes, no events (should score ~0)

Then runs the verifier on both, prints a table flagging:
  - CRASH       — verifier raised an exception
  - TOO STRICT  — perfect log scored < 0.7
  - TOO LENIENT — empty log scored > 0.3
  - OK          — perfect ≥ 0.7 and empty ≤ 0.3

Usage:
    PYTHONPATH=. python qa_verifiers.py
"""

from __future__ import annotations
import importlib, os, sys, traceback
from dataclasses import is_dataclass

# Ensure framework imports resolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# ─────────────────────────────────────────────────
# Synthetic log construction
# ─────────────────────────────────────────────────

def collect_expected(task) -> dict:
    """Walk the task's rubric tree and pull out expected shape/event counts."""
    shapes = {}      # type -> max required count
    tools  = set()
    events = {}      # name -> max required count

    def add_count(d, key, n):
        d[key] = max(d.get(key, 0), n)

    # WeightedRubric wraps the actual rubric; .rubric.checks
    for w in task.rubrics:
        rubric = getattr(w, "rubric", w)
        for check in getattr(rubric, "checks", []):
            cname = type(check).__name__
            if cname == "ShapeCount":
                add_count(shapes, check.layer_type, check.equals)
            elif cname == "ShapeCountAtLeast":
                add_count(shapes, check.layer_type, check.minimum)
            elif cname == "ToolUsed":
                tools.add(check.tool_id)
            elif cname == "EventTypeCount":
                add_count(events, check.event_name, check.equals)
            elif cname == "EventTypeCountAtLeast":
                add_count(events, check.event_name, check.minimum)
            elif cname == "EventTypeUsed":
                add_count(events, check.event_name, 1)
            elif cname == "AlignToolUsed":
                add_count(events, "align_layers", 1)
    return shapes, tools, events


def synth_layer(t, idx, x_base=100, y_base=100):
    """A synthetic layer node matching an existing log's schema."""
    # Use a moderate, non-degenerate position so geometry checks pass when possible.
    x = x_base + idx * 120
    y = y_base
    w = 80
    h = 80
    base = {
        "id": f"{t}_{idx}",
        "type": t,
        "x": x, "y": y, "w": w, "h": h,
        "fills": [{"kind": "solid",
                   "color": {"r": 0.2 + idx*0.07, "g": 0.5, "b": 0.7, "a": 1.0},
                   "opacity": 1.0, "visible": True}],
        "strokes": [],
        "effects": [],
    }
    if t == "polygon":
        base["sides"] = 6 if idx >= 0 else 3
    if t == "star":
        base["points"] = 8
        base["innerRatio"] = 0.7
    return base


def perfect_log(task) -> dict:
    """Build a synthetic outcome.document + semantic events that match expectations."""
    shapes, tools, events = collect_expected(task)

    # Build layer nodes (also emit a frame to satisfy any LayerInsideFrame style checks)
    children = []
    idx = 0
    for stype, n in shapes.items():
        for i in range(n):
            children.append(synth_layer(stype, idx))
            idx += 1

    # If shapes are needed but no frame requested, still add a frame as parent
    needs_frame = "frame" in shapes or len(shapes) > 0
    if needs_frame:
        frame_node = {
            "id": "frame_0", "type": "frame",
            "x": 0, "y": 0, "w": 1280, "h": 832,
            "fills": [{"kind": "solid", "color": {"r": 0.95, "g": 0.95, "b": 0.95, "a": 1.0},
                       "opacity": 1.0, "visible": True}],
            "strokes": [], "effects": [],
            "children": children,
        }
        page_children = [frame_node]
    else:
        page_children = children

    document = {
        "pages": [{
            "id": "page_0",
            "children": page_children,
            "prototypeSettings": {"device": None, "backgroundColor": {"r": 0,"g": 0,"b": 0,"a": 1}},
            "prototypeFlows": [],
        }]
    }

    semantic = [{"name": "session_start", "timestamp": 0}]
    for tool in tools:
        semantic.append({"name": "tool_change", "before": "select", "after": tool, "timestamp": 1})
    for event_name, count in events.items():
        for i in range(count):
            semantic.append({"name": event_name, "timestamp": 100 + i})

    # outcome summary shapeCounts
    counts = {}
    for stype, n in shapes.items():
        counts[stype] = n

    return {
        "schemaVersion": 1,
        "sessionId": "qa_synthetic_perfect",
        "raw": [],
        "semantic": semantic,
        "outcome": {
            "summary": {"shapeCounts": counts},
            "document": document,
        }
    }


def empty_log() -> dict:
    return {
        "schemaVersion": 1,
        "sessionId": "qa_synthetic_empty",
        "raw": [],
        "semantic": [{"name": "session_start", "timestamp": 0}],
        "outcome": {
            "summary": {"shapeCounts": {}},
            "document": {"pages": [{"id": "p", "children": [],
                                     "prototypeSettings": {"device": None,
                                                            "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
                                     "prototypeFlows": []}]}
        }
    }


# ─────────────────────────────────────────────────
# Score one task
# ─────────────────────────────────────────────────

def score(task, log) -> float:
    rubric_results = [r.run(log) for r in task.rubrics]
    eff = task.efficiency.run(log)
    max_base = sum(r.max_score for r in rubric_results) or 1.0
    base = sum(r.score for r in rubric_results) / max_base
    return base * eff.multiplier


# ─────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────

if __name__ == "__main__":
    tasks = sorted(f[:-3] for f in os.listdir("tasks")
                   if f.endswith(".py") and f != "__init__.py")

    rows = []
    for tname in tasks:
        try:
            mod = importlib.import_module(f"tasks.{tname}")
            task = mod.task
            p_log = perfect_log(task)
            e_log = empty_log()
            p_score = score(task, p_log)
            e_score = score(task, e_log)

            if p_score >= 0.7 and e_score <= 0.3:
                flag = "OK"
            elif p_score < 0.7:
                flag = "STRICT"
            elif e_score > 0.3:
                flag = "LENIENT"
            else:
                flag = "?"
            rows.append((tname, p_score, e_score, flag, None))
        except Exception as ex:
            rows.append((tname, None, None, "CRASH", repr(ex)))

    print(f"{'Task':<40} {'Perfect':>7} {'Empty':>6}  Flag       Notes")
    print("-" * 110)
    for tname, p, e, flag, err in rows:
        if p is None:
            print(f"{tname:<40} {'-':>7} {'-':>6}  {flag:<10} {err[:55] if err else ''}")
        else:
            print(f"{tname:<40} {p:>7.3f} {e:>6.3f}  {flag:<10}")

    ok    = sum(1 for r in rows if r[3] == "OK")
    strict = sum(1 for r in rows if r[3] == "STRICT")
    lenient = sum(1 for r in rows if r[3] == "LENIENT")
    crash = sum(1 for r in rows if r[3] == "CRASH")
    print()
    print(f"Summary: {ok} OK  |  {strict} STRICT  |  {lenient} LENIENT  |  {crash} CRASH  |  total {len(rows)}")

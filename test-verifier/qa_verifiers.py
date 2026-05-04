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


def collect_layers_by_type(doc: dict) -> dict:
    """Index every layer in the doc by type."""
    out: dict = {}

    def walk(nodes):
        for n in nodes:
            out.setdefault(n["type"], []).append(n)
            if "children" in n:
                walk(n["children"])

    for page in doc.get("pages", []):
        walk(page.get("children", []))
    return out


def mutate_for_geometry(task, log) -> None:
    """
    After perfect_log() builds layers in a default row, mutate them in-place
    so the synthetic doc satisfies geometric primitives present in the task.

    Order: aspect-ratio (sets size) → position (concentric/stacked/grid/radial/centered)
           → rotation → cornerRadius → cross-type containment/overlap.
    """
    import math
    doc = log["outcome"]["document"]

    checks = []
    for w in task.rubrics:
        rubric = getattr(w, "rubric", w)
        for c in getattr(rubric, "checks", []):
            checks.append(c)

    by_type = collect_layers_by_type(doc)

    # Pass 1: aspect ratio (resize before positioning so stacking math uses final w/h)
    for c in checks:
        cname = type(c).__name__
        if cname == "LayerIsCircular":
            for l in by_type.get(c.layer_type, []):
                l["h"] = l["w"]
        elif cname == "LayerAspectRatioGreaterThan":
            for l in by_type.get(c.layer_type, []):
                if c.axis == "horizontal":
                    l["w"] = max(l["w"], int(l["h"] * (c.ratio + 0.5)))
                else:
                    l["h"] = max(l["h"], int(l["w"] * (c.ratio + 0.5)))
        elif cname == "LayersHaveAspectMix":
            layers = by_type.get(c.layer_type, [])
            scale = c.ratio + 0.5
            target_cx, target_cy = 500, 500
            # First N → horizontal; next M → vertical; all centered on (target_cx, target_cy)
            for l in layers[: c.horizontal_count]:
                l["w"] = max(l["w"], int(l["h"] * scale))
                l["x"] = target_cx - l["w"] / 2
                l["y"] = target_cy - l["h"] / 2
            for l in layers[c.horizontal_count : c.horizontal_count + c.vertical_count]:
                l["h"] = max(l["h"], int(l["w"] * scale))
                l["x"] = target_cx - l["w"] / 2
                l["y"] = target_cy - l["h"] / 2

    # Pass 2: positioning (later mutations win for the same layer_type)
    for c in checks:
        cname = type(c).__name__
        if cname == "LayersConcentric":
            for i, l in enumerate(by_type.get(c.layer_type, [])):
                size = max(40, 200 - i * 30)
                l["w"] = l["h"] = size
                l["x"] = 500 - size / 2
                l["y"] = 500 - size / 2
        elif cname == "LayersStacked":
            layers = by_type.get(c.layer_type, [])
            if c.axis == "y":
                cur = 100
                for l in layers:
                    l["x"] = 100
                    l["y"] = cur
                    cur += l["h"] + c.gap_px
            else:  # "x"
                cur = 100
                for l in layers:
                    l["y"] = 100
                    l["x"] = cur
                    cur += l["w"] + c.gap_px
        elif cname == "LayersInGrid":
            layers = by_type.get(c.layer_type, [])
            for i, l in enumerate(layers[: c.rows * c.cols]):
                row = i // c.cols
                col = i % c.cols
                l["x"] = 100 + col * 120
                l["y"] = 100 + row * 120
        elif cname == "RadialDistribution":
            layers = by_type.get(c.layer_type, [])
            for i, l in enumerate(layers[: c.n]):
                angle = (2 * math.pi * i) / c.n
                l["x"] = 500 + 200 * math.cos(angle) - l["w"] / 2
                l["y"] = 500 + 200 * math.sin(angle) - l["h"] / 2
        elif cname == "LayerCenteredInFrame":
            for parent in collect_layers_by_type(doc).get("frame", []):
                for child in parent.get("children", []):
                    if child.get("type") == c.layer_type:
                        child["x"] = parent["w"] / 2 - child["w"] / 2
                        child["y"] = parent["h"] / 2 - child["h"] / 2
                        break
                break

    # Pass 3: rotation (independent)
    for c in checks:
        if type(c).__name__ == "LayersEvenlyRotated":
            for i, l in enumerate(by_type.get(c.layer_type, [])):
                l["rotation"] = i * c.step_deg

    # Pass 4: corner radius
    for c in checks:
        if type(c).__name__ == "CornerRadiusAtLeast":
            for l in by_type.get(c.layer_type, []):
                l["cornerRadius"] = c.min_value

    # Pass 5: containment/overlap (cross-type cases not already implied by positioning)
    for c in checks:
        cname = type(c).__name__
        if cname == "LayerBoundsInside":
            if c.inner_type == c.outer_type:
                continue
            inners = by_type.get(c.inner_type, [])
            outers = by_type.get(c.outer_type, [])
            if inners and outers:
                outer = outers[0]
                inner = inners[0]
                inner["w"] = min(inner["w"], max(20, outer["w"] - 20))
                inner["h"] = min(inner["h"], max(20, outer["h"] - 20))
                inner["x"] = outer["x"] + 10
                inner["y"] = outer["y"] + 10
        elif cname == "LayersOverlap":
            a = by_type.get(c.type_a, [])
            b = by_type.get(c.type_b, [])
            if c.type_a == c.type_b:
                if len(a) >= 2:
                    a[1]["x"] = a[0]["x"] + 10
                    a[1]["y"] = a[0]["y"] + 10
            elif a and b and a[0] is not b[0]:
                b[0]["x"] = a[0]["x"] + 10
                b[0]["y"] = a[0]["y"] + 10
        elif cname == "LayerCenteredOnLayer":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            if a_layers and b_layers and a_layers[0] is not b_layers[0]:
                b = b_layers[0]
                a = a_layers[0]
                a["x"] = b["x"] + b["w"] / 2 - a["w"] / 2
                a["y"] = b["y"] + b["h"] / 2 - a["h"] / 2
        elif cname == "LayerOnTopOf":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            if c.type_a == c.type_b and len(a_layers) >= 2:
                # later-in-list = later in z-order; ensure overlap
                a_layers[1]["x"] = a_layers[0]["x"] + 10
                a_layers[1]["y"] = a_layers[0]["y"] + 10
            elif a_layers and b_layers and a_layers[0] is not b_layers[0]:
                b = b_layers[0]
                a = a_layers[0]
                a["x"] = b["x"] + 10
                a["y"] = b["y"] + 10
        elif cname == "LayerNextTo":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            if a_layers and b_layers and a_layers[0] is not b_layers[0]:
                b = b_layers[0]
                a = a_layers[0]
                if c.side == "above":
                    a["x"] = b["x"]; a["y"] = b["y"] - a["h"]
                elif c.side == "below":
                    a["x"] = b["x"]; a["y"] = b["y"] + b["h"]
                elif c.side == "left":
                    a["x"] = b["x"] - a["w"]; a["y"] = b["y"]
                elif c.side == "right":
                    a["x"] = b["x"] + b["w"]; a["y"] = b["y"]
        elif cname == "LayerWidthFraction":
            for parent in by_type.get(c.parent_type, []):
                children = parent.get("children", [])
                target_w = parent.get("w", 800) * (c.min_frac + c.max_frac) / 2
                for child in children:
                    if child.get("type") == c.inner_type:
                        child["w"] = target_w
                        break
        elif cname == "LayerHasNoFill":
            for l in by_type.get(c.layer_type, []):
                l["fills"] = []
                break
        elif cname == "SameColorAcrossTypes":
            ref_color = None
            for t in c.types:
                ls = by_type.get(t, [])
                if not ls:
                    continue
                fills = ls[0].get("fills", [])
                if ref_color is None and fills:
                    ref_color = fills[0].get("color")
                elif ref_color is not None:
                    if not fills:
                        ls[0]["fills"] = [{"kind": "solid", "color": ref_color, "opacity": 1.0, "visible": True}]
                    else:
                        fills[0]["color"] = ref_color
        elif cname == "LayersAlternatingColors":
            layers = by_type.get(c.layer_type, [])
            if c.sort_axis == "x":
                ordered = sorted(layers, key=lambda l: l["x"] + l["w"] / 2)
            else:
                ordered = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
            cycle_colors = [{"r": 0.2 + 0.3 * k, "g": 0.5, "b": 0.8 - 0.2 * k, "a": 1.0}
                            for k in range(c.n_colors)]
            for i, l in enumerate(ordered):
                target = cycle_colors[i % c.n_colors]
                fills = l.get("fills", [])
                if fills:
                    fills[0]["color"] = target
                else:
                    l["fills"] = [{"kind": "solid", "color": target, "opacity": 1.0, "visible": True}]
        elif cname == "OffsetGridLayout":
            layers = by_type.get(c.layer_type, [])
            for i, l in enumerate(layers[: c.rows * c.cols]):
                row = i // c.cols
                col = i % c.cols
                x_offset = (l["w"] / 2) if row % 2 else 0
                l["x"] = 100 + col * 120 + x_offset
                l["y"] = 100 + row * 100
        elif cname == "RadialDistributionExcludeCentral":
            import math
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= c.n + 1:
                core = layers[0]
                core["x"] = 500 - core["w"] / 2
                core["y"] = 500 - core["h"] / 2
                for i, l in enumerate(layers[1: c.n + 1]):
                    angle = (2 * math.pi * i) / c.n
                    l["x"] = 500 + 200 * math.cos(angle) - l["w"] / 2
                    l["y"] = 500 + 200 * math.sin(angle) - l["h"] / 2
        elif cname == "LinesOnDiagonal":
            rects = by_type.get(c.rect_type, [])
            lines = by_type.get(c.line_type, [])
            if rects and len(lines) >= 2:
                r = rects[0]
                # Lines store p1/p2 in local space, with their own x/y offset
                lines[0]["x"] = r["x"]; lines[0]["y"] = r["y"]
                lines[0]["w"] = r["w"]; lines[0]["h"] = r["h"]
                lines[0]["p1"] = {"x": 0, "y": 0}
                lines[0]["p2"] = {"x": r["w"], "y": r["h"]}
                lines[1]["x"] = r["x"]; lines[1]["y"] = r["y"]
                lines[1]["w"] = r["w"]; lines[1]["h"] = r["h"]
                lines[1]["p1"] = {"x": r["w"], "y": 0}
                lines[1]["p2"] = {"x": 0, "y": r["h"]}
        elif cname == "LayersHaveRotations":
            layers = by_type.get(c.layer_type, [])
            for i, l in enumerate(layers[: len(c.expected) * c.count_per]):
                l["rotation"] = c.expected[i // c.count_per]
        elif cname == "DistinctStrokeColors":
            i = 0
            for l in by_type.get("rectangle", []) + by_type.get("ellipse", []) + by_type.get("vector", []) + by_type.get("polygon", []) + by_type.get("line", []):
                if i >= c.minimum:
                    break
                color = {"r": 0.1 + 0.15 * i, "g": 0.3, "b": 0.6, "a": 1.0}
                l["strokes"] = [{"paint": {"kind": "solid", "color": color}, "weight": 2, "alignment": "center", "dash": None}]
                i += 1
        elif cname == "PageBackgroundColorEquals":
            pages = doc.get("pages", [])
            if c.page_index < len(pages):
                pages[c.page_index]["backgroundColor"] = dict(c.expected_rgb)


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

    log = {
        "schemaVersion": 1,
        "sessionId": "qa_synthetic_perfect",
        "raw": [],
        "semantic": semantic,
        "outcome": {
            "summary": {"shapeCounts": counts},
            "document": document,
        }
    }
    mutate_for_geometry(task, log)
    return log


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

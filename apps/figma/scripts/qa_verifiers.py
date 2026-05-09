"""
QA harness for the verifier set.

For each task in delivery-1/, synthesizes:
  - PERFECT-LOG: shapes/events the task expects, in matching counts
  - EMPTY-LOG: no shapes, no events (should score ~0)

Then runs the verifier on both, prints a table flagging:
  - CRASH       — verifier raised an exception
  - TOO STRICT  — perfect log scored < 0.7
  - TOO LENIENT — empty log scored > 0.3
  - OK          — perfect ≥ 0.7 and empty ≤ 0.3

Usage:
    ../.venv/Scripts/python scripts/qa_verifiers.py
"""

from __future__ import annotations
import importlib.util, os, sys, traceback
from dataclasses import is_dataclass
from pathlib import Path

APP_ROOT     = Path(__file__).resolve().parent.parent
DELIVERY_DIR = APP_ROOT / "delivery-1"

# Make `from verifier... import ...` work inside delivery-1/task_NN/verifier.py
sys.path.insert(0, str(APP_ROOT))


def load_task_from_dir(task_dir: Path):
    verifier_py = task_dir / "verifier.py"
    spec = importlib.util.spec_from_file_location(f"delivery_{task_dir.name}", verifier_py)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.task


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
    # Pick perceptually distinct colors per index so DistinctSolidColors works.
    palette = [
        (0.20, 0.50, 0.70),
        (0.95, 0.30, 0.30),
        (0.30, 0.85, 0.30),
        (0.95, 0.85, 0.20),
        (0.50, 0.30, 0.85),
        (0.20, 0.85, 0.85),
        (0.95, 0.50, 0.20),
        (1.00, 0.40, 0.85),
    ]
    r, g, b = palette[idx % len(palette)]
    base = {
        "id": f"{t}_{idx}",
        "type": t,
        "x": x, "y": y, "w": w, "h": h,
        "fills": [{"kind": "solid",
                   "color": {"r": r, "g": g, "b": b, "a": 1.0},
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
        if cname in ("LayerIsCircular", "LayerIsSquare",
                     "LayerAllCircular", "LayerAllSquare",
                     "AllLayersAreCircular"):
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
            # If LayersSameDimensions is also required for this type, keep all
            # layers the same size and just align centers — otherwise shrink
            # progressively to nest concentrically.
            same_size = any(
                type(c2).__name__ == "LayersSameDimensions" and c2.layer_type == c.layer_type
                for c2 in checks
            )
            for i, l in enumerate(by_type.get(c.layer_type, [])):
                if same_size:
                    size = 200
                else:
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
        elif cname == "LayersOnRing":
            layers = by_type.get(c.layer_type, [])
            radius = max(c.min_radius_px + 20, 150)
            for i, l in enumerate(layers[: c.n]):
                angle = (2 * math.pi * i) / c.n
                l["x"] = 500 + radius * math.cos(angle) - l["w"] / 2
                l["y"] = 500 + radius * math.sin(angle) - l["h"] / 2
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
        elif type(c).__name__ == "LayersHaveDistinctRotations":
            # Spread rotations evenly so we have at least `minimum` distinct values
            layers = by_type.get(c.layer_type, [])
            if layers:
                step = max(360 / max(len(layers), 1), c.tolerance_deg * 3)
                for i, l in enumerate(layers):
                    # Only set if rotation hasn't been claimed by LayersEvenlyRotated
                    if "rotation" not in l or l.get("rotation", 0) == 0:
                        l["rotation"] = (i * step) % 360

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
                layers = by_type.get(c.inner_type, [])
                if len(layers) >= 2:
                    outer = layers[0]
                    inner = layers[1]
                    inner["w"] = min(inner["w"], max(20, outer["w"] - 20))
                    inner["h"] = min(inner["h"], max(20, outer["h"] - 20))
                    inner["x"] = outer["x"] + 10
                    inner["y"] = outer["y"] + 10
                continue
            inners = by_type.get(c.inner_type, [])
            outers = by_type.get(c.outer_type, [])
            if inners and outers:
                outer = outers[0]
                inner = inners[0]
                # If the inner needs to remain circular/square, scale uniformly so
                # both dimensions fit within the outer (preserving w==h).
                needs_uniform = any(
                    type(c2).__name__ in ("LayerIsCircular", "LayerIsSquare",
                                          "LayerAllCircular", "LayerAllSquare")
                    and c2.layer_type == c.inner_type
                    for c2 in checks
                )
                if needs_uniform:
                    target = min(max(20, outer["w"] - 20), max(20, outer["h"] - 20))
                    inner["w"] = inner["h"] = target
                else:
                    inner["w"] = min(inner["w"], max(20, outer["w"] - 20))
                    inner["h"] = min(inner["h"], max(20, outer["h"] - 20))
                inner["x"] = outer["x"] + 10
                inner["y"] = outer["y"] + 10
        elif cname == "LayersOverlap":
            a = by_type.get(c.type_a, [])
            b = by_type.get(c.type_b, [])
            if c.type_a == c.type_b:
                if len(a) >= 2:
                    # Partial overlap (~30%): offset second by ~30% of width.
                    offset = max(25, int(a[0].get("w", 80) * 0.3))
                    a[1]["x"] = a[0]["x"] + offset
                    a[1]["y"] = a[0]["y"] + max(15, offset // 3)
            elif a and b and a[0] is not b[0]:
                # move first type_a to overlap the first type_b (zero offset → identical bbox)
                a[0]["x"] = b[0]["x"]
                a[0]["y"] = b[0]["y"]
        elif cname == "LayerEdgesAligned":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            if a_layers and b_layers and a_layers[0] is not b_layers[0]:
                a = a_layers[0]
                b = b_layers[0]
                if c.edge_b == "top":      target = b["y"]
                elif c.edge_b == "bottom": target = b["y"] + b["h"]
                elif c.edge_b == "left":   target = b["x"]
                elif c.edge_b == "right":  target = b["x"] + b["w"]
                elif c.edge_b == "center_x": target = b["x"] + b["w"] / 2
                elif c.edge_b == "center_y": target = b["y"] + b["h"] / 2
                else: continue
                if c.edge_a == "top":      a["y"] = target
                elif c.edge_a == "bottom": a["y"] = target - a["h"]
                elif c.edge_a == "left":   a["x"] = target
                elif c.edge_a == "right":  a["x"] = target - a["w"]
                elif c.edge_a == "center_x": a["x"] = target - a["w"] / 2
                elif c.edge_a == "center_y": a["y"] = target - a["h"] / 2
        elif cname == "LayerCenteredOnLayer":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            axis = getattr(c, "axis", "both")
            if c.type_a == c.type_b and len(a_layers) >= 2:
                largest = max(a_layers, key=lambda l: l["w"] * l["h"])
                smallest = min(a_layers, key=lambda l: l["w"] * l["h"])
                if largest is not smallest:
                    if axis in ("x", "both"):
                        smallest["x"] = largest["x"] + largest["w"] / 2 - smallest["w"] / 2
                    if axis in ("y", "both"):
                        smallest["y"] = largest["y"] + largest["h"] / 2 - smallest["h"] / 2
            elif a_layers and b_layers and a_layers[0] is not b_layers[0]:
                b = b_layers[0]
                a = a_layers[0]
                if axis in ("x", "both"):
                    a["x"] = b["x"] + b["w"] / 2 - a["w"] / 2
                if axis in ("y", "both"):
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
        elif cname == "AllLayerWidthFraction":
            # Scale h proportionally when (a) LayerIsCircular requires w==h for
            # this type, or (b) this type is a container in AllLayerBoundsInside
            # — otherwise containers shrink in h and inners can't fit.
            needs_circular = any(
                type(c2).__name__ == "LayerIsCircular" and c2.layer_type == c.inner_type
                for c2 in checks
            )
            is_container = any(
                type(c2).__name__ == "AllLayerBoundsInside" and c2.outer_type == c.inner_type
                for c2 in checks
            )
            needs_h_scale = needs_circular or is_container
            for parent in by_type.get(c.parent_type, []):
                target_w = parent.get("w", 800) * (c.min_frac + c.max_frac) / 2
                for child in parent.get("children", []):
                    if child.get("type") == c.inner_type:
                        if needs_h_scale and child["w"]:
                            scale = target_w / child["w"]
                            child["h"] = child["h"] * scale
                        child["w"] = target_w
        elif cname == "LayerSizeAtLeast":
            for l in by_type.get(c.layer_type, []):
                if l["w"] < c.min_w:
                    l["w"] = c.min_w
                if l["h"] < c.min_h:
                    l["h"] = c.min_h
        elif cname == "CrossTypeAreaRatioAtLeast":
            bigs = by_type.get(c.big_type, [])
            smalls = by_type.get(c.small_type, [])
            if bigs and smalls:
                big_area = max(l["w"] * l["h"] for l in bigs)
                # Scale every small layer down so its area is at most big_area / (min_ratio * 1.5)
                target_small_area = big_area / (c.min_ratio * 1.5)
                for s in smalls:
                    a = s["w"] * s["h"]
                    if a > target_small_area:
                        import math
                        scale = math.sqrt(target_small_area / a)
                        s["w"] = max(4, s["w"] * scale)
                        s["h"] = max(4, s["h"] * scale)
        elif cname == "LayerShortDimensionAtMost":
            for l in by_type.get(c.layer_type, []):
                if min(l["w"], l["h"]) > c.max_value:
                    if l["w"] > c.max_value: l["w"] = c.max_value
                    if l["h"] > c.max_value: l["h"] = c.max_value
        elif cname == "LayerSmallerThanLayer":
            larges = by_type.get(c.larger_type, [])
            smalls = by_type.get(c.smaller_type, [])
            if larges and smalls:
                anchor = max(larges, key=lambda l: l["w"] * l["h"])
                anchor_short = min(anchor["w"], anchor["h"])
                if anchor_short > 0:
                    target_short = anchor_short * c.max_frac * 0.7  # well within max_frac
                    for s in smalls:
                        if id(s) == id(anchor):
                            continue
                        if min(s["w"], s["h"]) > target_short:
                            scale = target_short / min(s["w"], s["h"])
                            s["w"] *= scale
                            s["h"] *= scale
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
        elif cname == "LayersAlternatingColorsByArea":
            layers = by_type.get(c.layer_type, [])
            ordered = sorted(layers, key=lambda l: l["w"] * l["h"], reverse=True)
            cycle_colors = [
                {"r": 0.20, "g": 0.50, "b": 0.80, "a": 1.0},
                {"r": 0.95, "g": 0.30, "b": 0.30, "a": 1.0},
                {"r": 0.30, "g": 0.85, "b": 0.30, "a": 1.0},
                {"r": 0.95, "g": 0.85, "b": 0.20, "a": 1.0},
            ]
            for i, l in enumerate(ordered):
                target = cycle_colors[i % c.n_colors]
                l["fills"] = [{"kind": "solid", "color": dict(target),
                               "opacity": 1.0, "visible": True}]
        elif cname == "LayersAlternatingColors":
            layers = by_type.get(c.layer_type, [])
            if c.sort_axis == "x":
                ordered = sorted(layers, key=lambda l: l["x"] + l["w"] / 2)
            elif c.sort_axis == "angle" and layers:
                # Sort by angle around the centroid (for radial layouts)
                cx_ = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
                cy_ = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
                ordered = sorted(layers, key=lambda l: math.atan2(
                    (l["y"] + l["h"] / 2) - cy_, (l["x"] + l["w"] / 2) - cx_))
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
        elif cname == "DistinctTypedSolidColors":
            # Assign visibly-distinct colors to each layer of layer_type so
            # the per-type distinct-color check passes for the synthetic perfect log.
            palette = [
                {"r": 0.95, "g": 0.20, "b": 0.20, "a": 1.0},  # red
                {"r": 0.06, "g": 0.72, "b": 0.50, "a": 1.0},  # green
                {"r": 0.10, "g": 0.40, "b": 0.85, "a": 1.0},  # blue
                {"r": 1.00, "g": 0.85, "b": 0.20, "a": 1.0},  # yellow
                {"r": 0.50, "g": 0.20, "b": 0.70, "a": 1.0},  # purple
                {"r": 1.00, "g": 0.50, "b": 0.10, "a": 1.0},  # orange
                {"r": 0.30, "g": 0.30, "b": 0.30, "a": 1.0},  # dark gray
                {"r": 0.85, "g": 0.85, "b": 0.85, "a": 1.0},  # light gray
                {"r": 0.85, "g": 0.30, "b": 0.65, "a": 1.0},  # pink
                {"r": 0.65, "g": 0.40, "b": 0.20, "a": 1.0},  # brown
                {"r": 0.10, "g": 0.10, "b": 0.10, "a": 1.0},  # near-black
                {"r": 0.95, "g": 0.95, "b": 0.20, "a": 1.0},  # neon yellow
                {"r": 0.20, "g": 0.85, "b": 0.85, "a": 1.0},  # cyan
                {"r": 0.95, "g": 0.50, "b": 0.30, "a": 1.0},  # coral
                {"r": 0.55, "g": 0.55, "b": 0.85, "a": 1.0},  # lavender
                {"r": 0.10, "g": 0.50, "b": 0.30, "a": 1.0},  # forest green
            ]
            # If a SolidColorEquals will overwrite layer[0] for this type, skip
            # palette entries that match the target color (otherwise both ellipses
            # end up the same color → distinct check fails).
            forbidden_colors = []
            for c2 in checks:
                if type(c2).__name__ == "SolidColorEquals" and c2.layer_type == c.layer_type:
                    forbidden_colors.append(dict(c2.expected_rgb))
                if type(c2).__name__ == "AllSolidColorEquals" and c2.layer_type == c.layer_type:
                    forbidden_colors.append(dict(c2.expected_rgb))
            def _color_collision(p):
                for f in forbidden_colors:
                    if (abs(p["r"] - f.get("r", 0)) < 0.20
                        and abs(p["g"] - f.get("g", 0)) < 0.20
                        and abs(p["b"] - f.get("b", 0)) < 0.20):
                        return True
                return False
            usable_palette = [p for p in palette if not _color_collision(p)]
            target_layers = by_type.get(c.layer_type, [])
            # If a SolidColorEquals will paint layer[0], leave it alone and only
            # paint layers[1..]; the SolidColorEquals color counts as one "distinct".
            has_scq = any(
                type(c2).__name__ == "SolidColorEquals" and c2.layer_type == c.layer_type
                for c2 in checks
            )
            if has_scq and target_layers:
                target_layers = target_layers[1:]
            for i, l in enumerate(target_layers[: c.minimum]):
                target = dict(usable_palette[i % len(usable_palette)])
                l["fills"] = [{"kind": "solid", "color": target,
                               "opacity": 1.0, "visible": True}]
        elif cname == "DistinctTypedStrokeColors":
            # Assign visibly-distinct stroke colors to each layer of layer_type
            # so per-type stroke distinct-color check passes for the perfect log.
            stroke_palette = [
                {"r": 0.10, "g": 0.40, "b": 0.85, "a": 1.0},  # blue
                {"r": 0.20, "g": 0.20, "b": 0.55, "a": 1.0},  # darker blue
                {"r": 0.40, "g": 0.65, "b": 0.95, "a": 1.0},  # lighter blue
                {"r": 0.95, "g": 0.20, "b": 0.20, "a": 1.0},  # red
                {"r": 0.06, "g": 0.72, "b": 0.50, "a": 1.0},  # green
                {"r": 1.00, "g": 0.85, "b": 0.20, "a": 1.0},  # yellow
            ]
            for i, l in enumerate(by_type.get(c.layer_type, [])[: c.minimum]):
                target = dict(stroke_palette[i % len(stroke_palette)])
                existing = (l.get("strokes") or [{}])[0]
                weight = existing.get("weight", 4)
                alignment = existing.get("alignment", "center")
                l["strokes"] = [{
                    "paint": {"kind": "solid", "color": target},
                    "weight": weight, "alignment": alignment,
                    "dash": None, "visible": True,
                }]

    # Pass 6: fills + frame size (run last so explicit colors override per-idx synth variation)
    for c in checks:
        cname = type(c).__name__
        if cname == "FrameSizeEquals":
            frames = by_type.get("frame", [])
            if frames:
                frames[0]["w"] = c.width
                frames[0]["h"] = c.height
        elif cname == "LayersHaveColorOrder":
            layers = by_type.get(c.layer_type, [])
            if c.sort_axis == "y":
                ordered = sorted(layers, key=lambda l: l["y"] + l["h"] / 2)
            elif c.sort_axis == "size":
                ordered = sorted(layers, key=lambda l: -(l["w"] * l["h"]))
            else:
                ordered = sorted(layers, key=lambda l: l["x"] + l["w"] / 2)
            for i, l in enumerate(ordered[: len(c.expected_rgbs)]):
                target = dict(c.expected_rgbs[i])
                target.setdefault("a", 1.0)
                l["fills"] = [{"kind": "solid", "color": target, "opacity": 1.0, "visible": True}]
        elif cname == "LayersAllSameColor":
            layers = by_type.get(c.layer_type, [])
            if layers:
                fills = layers[0].get("fills") or [{"kind": "solid",
                    "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0},
                    "opacity": 1.0, "visible": True}]
                ref = fills[0]["color"]
                for l in layers:
                    l["fills"] = [{"kind": "solid", "color": dict(ref), "opacity": 1.0, "visible": True}]
        elif cname == "SolidColorEquals":
            layers = by_type.get(c.layer_type, [])
            if layers:
                target = dict(c.expected_rgb)
                target.setdefault("a", 1.0)
                layers[0]["fills"] = [{"kind": "solid", "color": target, "opacity": 1.0, "visible": True}]
        elif cname == "AllSolidColorEquals":
            target = dict(c.expected_rgb)
            target.setdefault("a", 1.0)
            for l in by_type.get(c.layer_type, []):
                l["fills"] = [{"kind": "solid", "color": target, "opacity": 1.0, "visible": True}]
        elif cname == "CentermostLayerHasColor":
            layers = by_type.get(c.layer_type, [])
            if not layers:
                continue
            cx_ = sum(l["x"] + l["w"] / 2 for l in layers) / len(layers)
            cy_ = sum(l["y"] + l["h"] / 2 for l in layers) / len(layers)
            center = min(layers, key=lambda l: ((l["x"] + l["w"] / 2 - cx_) ** 2 + (l["y"] + l["h"] / 2 - cy_) ** 2))
            target = dict(c.expected_rgb)
            target.setdefault("a", 1.0)
            center["fills"] = [{"kind": "solid", "color": target, "opacity": 1.0, "visible": True}]

    # Pass 7: visual properties (strokes, effects, layer-level scalars)
    def _ensure_first(layers):
        return layers[0] if layers else None

    def _ensure_drop_shadow(layer):
        for e in layer.setdefault("effects", []):
            if e.get("kind") == "drop_shadow":
                return e
        e = {"kind": "drop_shadow", "x": 0, "y": 0, "blur": 4, "spread": 0,
             "color": {"r": 0, "g": 0, "b": 0, "a": 0.25}, "visible": True}
        layer["effects"].append(e)
        return e

    def _ensure_layer_blur(layer):
        for e in layer.setdefault("effects", []):
            if e.get("kind") == "layer_blur":
                return e
        e = {"kind": "layer_blur", "radius": 4, "visible": True}
        layer["effects"].append(e)
        return e

    def _ensure_stroke(layer):
        strokes = layer.setdefault("strokes", [])
        if not strokes:
            strokes.append({
                "paint": {"kind": "solid",
                          "color": {"r": 0, "g": 0, "b": 0, "a": 1.0}},
                "weight": 1, "alignment": "center", "dash": None, "visible": True,
            })
        return strokes[0]

    for c in checks:
        cname = type(c).__name__

        # Effects
        if cname == "DropShadowExists":
            for l in by_type.get(c.layer_type, []):
                _ensure_drop_shadow(l)
        elif cname == "DropShadowOffsetEquals":
            l = _ensure_first(by_type.get(c.layer_type, []))
            if l is not None:
                e = _ensure_drop_shadow(l)
                e["x"] = c.x
                e["y"] = c.y
        elif cname == "DropShadowBlurEquals":
            l = _ensure_first(by_type.get(c.layer_type, []))
            if l is not None:
                e = _ensure_drop_shadow(l)
                e["blur"] = c.blur
        elif cname == "DropShadowSpreadEquals":
            l = _ensure_first(by_type.get(c.layer_type, []))
            if l is not None:
                e = _ensure_drop_shadow(l)
                e["spread"] = c.spread
        elif cname == "EffectColorEquals":
            l = _ensure_first(by_type.get(c.layer_type, []))
            if l is not None:
                e = _ensure_drop_shadow(l)
                target = dict(c.expected_rgb)
                target.setdefault("a", 1.0)
                e["color"] = target
        elif cname == "EffectCount":
            for l in by_type.get(c.layer_type, []):
                effects = l.setdefault("effects", [])
                while len(effects) < c.equals:
                    # Use offset+visible drop shadows so PairedDropShadowsOpposite passes too
                    idx = len(effects)
                    sx, sy = (-6, -6) if idx % 2 == 0 else (6, 6)
                    effects.append({"kind": "drop_shadow", "x": sx, "y": sy, "blur": 6,
                                    "spread": 0, "color": {"r": 0, "g": 0, "b": 0, "a": 0.4},
                                    "visible": True})
                while len(effects) > c.equals:
                    effects.pop()
        elif cname == "DropShadowCountAtLeast":
            for l in by_type.get(c.layer_type, []):
                effects = l.setdefault("effects", [])
                visible_shadows = [e for e in effects
                                   if e.get("kind") == "drop_shadow"
                                   and e.get("visible", True) is not False
                                   and e.get("color", {}).get("a", 1.0) >= c.min_alpha]
                while len(visible_shadows) < c.minimum:
                    idx = len(visible_shadows)
                    sx, sy = (-6, -6) if idx % 2 == 0 else (6, 6)
                    new_e = {"kind": "drop_shadow", "x": sx, "y": sy, "blur": 6,
                             "spread": 0, "color": {"r": 0, "g": 0, "b": 0, "a": 0.4},
                             "visible": True}
                    effects.append(new_e)
                    visible_shadows.append(new_e)
        elif cname == "PairedDropShadowsOpposite":
            for l in by_type.get(c.layer_type, []):
                effects = l.setdefault("effects", [])
                # Strip any zero-offset shadows
                opposing_shadows = [e for e in effects
                                    if e.get("kind") == "drop_shadow"
                                    and e.get("visible", True) is not False
                                    and e.get("color", {}).get("a", 1.0) >= 0.05
                                    and (abs(e.get("x", 0)) >= c.min_offset or abs(e.get("y", 0)) >= c.min_offset)]
                # Need at least 2 with opposing offsets
                has_pair = False
                for i in range(len(opposing_shadows)):
                    for j in range(i + 1, len(opposing_shadows)):
                        a = opposing_shadows[i]
                        b = opposing_shadows[j]
                        if (a.get("x", 0) * b.get("x", 0) < 0) or (a.get("y", 0) * b.get("y", 0) < 0):
                            has_pair = True
                            break
                    if has_pair:
                        break
                if not has_pair:
                    # Force opposing offsets on first 2 visible shadows
                    visible_shadows = [e for e in effects
                                       if e.get("kind") == "drop_shadow"
                                       and e.get("visible", True) is not False]
                    while len(visible_shadows) < 2:
                        new_e = {"kind": "drop_shadow", "x": 0, "y": 0, "blur": 6,
                                 "spread": 0, "color": {"r": 0, "g": 0, "b": 0, "a": 0.4},
                                 "visible": True}
                        effects.append(new_e)
                        visible_shadows.append(new_e)
                    visible_shadows[0]["x"] = -6
                    visible_shadows[0]["y"] = -6
                    visible_shadows[0]["color"] = {"r": 1, "g": 1, "b": 1, "a": 0.6}
                    visible_shadows[1]["x"] = 6
                    visible_shadows[1]["y"] = 6
                    visible_shadows[1]["color"] = {"r": 0, "g": 0, "b": 0, "a": 0.4}
        elif cname == "LayerBlurExists":
            for l in by_type.get(c.layer_type, []):
                _ensure_layer_blur(l)
        elif cname == "AllLayerBlurExists":
            for l in by_type.get(c.layer_type, []):
                e = _ensure_layer_blur(l)
                if e.get("radius", 0) < c.min_radius:
                    e["radius"] = max(c.min_radius, 4)
                e["visible"] = True
        elif cname == "BlurRadiusEquals":
            l = _ensure_first(by_type.get(c.layer_type, []))
            if l is not None:
                e = _ensure_layer_blur(l)
                e["radius"] = c.radius

        # Strokes
        elif cname == "StrokeExists":
            for l in by_type.get(c.layer_type, []):
                _ensure_stroke(l)
        elif cname == "VisibleStrokeExists":
            for l in by_type.get(c.layer_type, []):
                strokes = l.setdefault("strokes", [])
                if not strokes:
                    strokes.append({
                        "paint": {"kind": "solid",
                                  "color": {"r": 0, "g": 0, "b": 0, "a": 1.0}},
                        "weight": max(c.min_weight + 0.5, 1),
                        "alignment": "center", "dash": None, "visible": True,
                    })
                else:
                    s = strokes[0]
                    s["visible"] = True
                    if s.get("weight", 0) < c.min_weight:
                        s["weight"] = max(c.min_weight + 0.5, 1)
                    paint = s.setdefault("paint", {"kind": "solid", "color": {"r":0,"g":0,"b":0,"a":1}})
                    color = paint.setdefault("color", {"r":0,"g":0,"b":0,"a":1})
                    if color.get("a", 1.0) < c.min_alpha:
                        color["a"] = max(c.min_alpha + 0.05, 1)
        elif cname == "AllLayerStrokeVisible":
            for l in by_type.get(c.layer_type, []):
                strokes = l.setdefault("strokes", [])
                # Ensure at least one visible stroke with sufficient alpha and weight
                if not strokes:
                    strokes.append({
                        "paint": {"kind": "solid",
                                  "color": {"r": 0, "g": 0, "b": 0, "a": 1.0}},
                        "weight": max(c.min_weight + 0.5, 1),
                        "alignment": "center", "dash": None, "visible": True,
                    })
                else:
                    s = strokes[0]
                    s["visible"] = True
                    s["weight"] = max(s.get("weight", 0), c.min_weight + 0.5)
                    paint = s.setdefault("paint", {"kind": "solid", "color": {"r":0,"g":0,"b":0,"a":1.0}})
                    color = paint.setdefault("color", {"r":0,"g":0,"b":0,"a":1.0})
                    if color.get("a", 1.0) < c.min_alpha:
                        color["a"] = max(color.get("a", 1.0), c.min_alpha + 0.05)
        elif cname == "StrokeWeightEquals":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                s["weight"] = c.weight
        elif cname == "StrokeColorEquals":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                target = dict(c.expected_rgb)
                target.setdefault("a", 1.0)
                s["paint"] = {"kind": "solid", "color": target}
        elif cname == "StrokeAlignmentIs":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                s["alignment"] = c.alignment
        elif cname == "StrokeIsDashed":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                s["dash"] = {"dash": 6, "gap": 4}
        elif cname == "AllStrokeExists":
            for l in by_type.get(c.layer_type, []):
                _ensure_stroke(l)
        elif cname == "AllStrokeColorEquals":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                target = dict(c.expected_rgb)
                target.setdefault("a", 1.0)
                s["paint"] = {"kind": "solid", "color": target}
        elif cname == "AllStrokeWeightAtMost":
            for l in by_type.get(c.layer_type, []):
                for s in l.get("strokes", []):
                    if s.get("weight", 0) > c.max_weight:
                        s["weight"] = c.max_weight
        elif cname == "AllStrokeWeightWithinTolerance":
            for l in by_type.get(c.layer_type, []):
                s = _ensure_stroke(l)
                s["weight"] = c.target_weight

        # Property checks
        elif cname == "OpacityEquals":
            for l in by_type.get(c.layer_type, []):
                l["opacity"] = c.opacity
        elif cname == "VisibilityIs":
            for l in by_type.get(c.layer_type, []):
                l["visible"] = c.visible
        elif cname == "CornerRadiusEquals":
            for l in by_type.get(c.layer_type, []):
                l["cornerRadius"] = c.radius
        elif cname == "IsFlippedH":
            for l in by_type.get(c.layer_type, []):
                l["scaleX"] = -1
        elif cname == "IsFlippedV":
            for l in by_type.get(c.layer_type, []):
                l["scaleY"] = -1
        elif cname == "ConstraintHorizontalEquals":
            for l in by_type.get(c.layer_type, []):
                l.setdefault("constraints", {})["horizontal"] = c.value
        elif cname == "ConstraintVerticalEquals":
            for l in by_type.get(c.layer_type, []):
                l.setdefault("constraints", {})["vertical"] = c.value
        elif cname == "LayerRotationEquals":
            for l in by_type.get(c.layer_type, []):
                l["rotation"] = c.degrees

        # Fill subtype
        elif cname == "FillTypeIs" and c.kind == "image":
            for l in by_type.get(c.layer_type, []):
                l["fills"] = [{"kind": "image", "src": "synthetic.jpg",
                               "fit": "cover", "rotation": 0,
                               "opacity": 1.0, "visible": True}]
        elif cname == "AllFillTypeIs" and c.kind == "image":
            for l in by_type.get(c.layer_type, []):
                l["fills"] = [{"kind": "image", "src": "synthetic.jpg",
                               "fit": "cover", "rotation": 0,
                               "opacity": 1.0, "visible": True}]
        elif cname == "ImageFillExists":
            for l in by_type.get(c.layer_type, []):
                l["fills"] = [{"kind": "image", "src": "synthetic.jpg",
                               "fit": "cover", "rotation": 0,
                               "opacity": 1.0, "visible": True}]
        elif cname == "FillOpacityEquals":
            for l in by_type.get(c.layer_type, []):
                fills = l.setdefault("fills", [{"kind": "solid",
                    "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0},
                    "opacity": 1.0, "visible": True}])
                if c.fill_index < len(fills):
                    fills[c.fill_index]["opacity"] = c.opacity
        elif cname == "FillCount":
            for l in by_type.get(c.layer_type, []):
                fills = l.setdefault("fills", [])
                base_color = (fills[0].get("color") if fills
                              else {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0})
                while len(fills) < c.equals:
                    fills.append({"kind": "solid", "color": dict(base_color),
                                  "opacity": 1.0, "visible": True})
                del fills[c.equals:]

        # Text checks
        elif cname == "TextContent":
            for l in by_type.get("text", []):
                l["content"] = c.expected
        elif cname == "TextContains":
            for l in by_type.get("text", []):
                if c.substring not in l.get("content", ""):
                    l["content"] = c.substring
        elif cname == "FontSizeEquals":
            for l in by_type.get("text", []):
                l["fontSize"] = c.size
        elif cname == "FontWeightEquals":
            for l in by_type.get("text", []):
                l["fontWeight"] = c.weight
        elif cname == "TextAlignEquals":
            for l in by_type.get("text", []):
                l["hAlign"] = c.align
        elif cname == "VerticalAlignEquals":
            for l in by_type.get("text", []):
                l["vAlign"] = c.align
        elif cname == "LineHeightEquals":
            for l in by_type.get("text", []):
                l["lineHeight"] = {"type": "pixels", "value": c.value}
        elif cname == "LetterSpacingEquals":
            for l in by_type.get("text", []):
                l["letterSpacing"] = {"type": "pixels", "value": c.value}

    # ── Final pass: fix positions after all sizing is settled.
    # Some checks (SmallerLayerInsideLarger, LayerCenteredOnLayer, LayerEdgesAligned)
    # depend on layer sizes, but earlier passes may resize layers via AllLayerWidthFraction.
    # Re-run these position fixes so the perfect log holds end-state.
    for c in checks:
        cname = type(c).__name__
        if cname == "SmallerLayerInsideLarger":
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= 2:
                outer = max(layers, key=lambda l: l["w"] * l["h"])
                area_ratio = max(
                    [c2.min_ratio for c2 in checks
                     if type(c2).__name__ == "LayerAreaRatioAtLeast"
                     and c2.layer_type == c.layer_type],
                    default=1.0,
                )
                # Detect alignment convention: if LayersConcentric is also required
                # for this type, center-align both axes (concentric squares/circles).
                # Otherwise default to door-on-body (bottom-aligned, x-centered).
                needs_concentric = any(
                    type(c2).__name__ == "LayersConcentric" and c2.layer_type == c.layer_type
                    for c2 in checks
                )
                # When multiple inners exist (e.g., 4 concentric squares), give each
                # progressively smaller scale so they truly nest.
                inners = [l for l in layers if l is not outer]
                # Sort largest-to-smallest by current area so the size order is stable.
                inners.sort(key=lambda l: -(l["w"] * l["h"]))
                import math
                base_scale = 1.0 / math.sqrt(area_ratio + 0.5)
                for i, inner in enumerate(inners):
                    if needs_concentric:
                        # progressively shrink: 0.7, 0.49, 0.34, ... of outer
                        scale = 0.7 ** (i + 1)
                    else:
                        scale = base_scale
                    inner["w"] = outer["w"] * scale
                    inner["h"] = outer["h"] * scale
                    if needs_concentric:
                        inner["x"] = outer["x"] + (outer["w"] - inner["w"]) / 2
                        inner["y"] = outer["y"] + (outer["h"] - inner["h"]) / 2
                    else:
                        inner["x"] = outer["x"] + (outer["w"] - inner["w"]) / 2
                        inner["y"] = outer["y"] + outer["h"] - inner["h"]
        elif cname == "SmallerLayerCenteredOnLargerEdge":
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= 2:
                largest = max(layers, key=lambda l: l["w"] * l["h"])
                smallest = min(layers, key=lambda l: l["w"] * l["h"])
                if largest is not smallest:
                    if c.edge == "bottom":
                        # smallest's bottom == largest's bottom; center_x aligned
                        smallest["x"] = largest["x"] + largest["w"] / 2 - smallest["w"] / 2
                        smallest["y"] = largest["y"] + largest["h"] - smallest["h"]
                    elif c.edge == "top":
                        smallest["x"] = largest["x"] + largest["w"] / 2 - smallest["w"] / 2
                        smallest["y"] = largest["y"]
                    elif c.edge == "left":
                        smallest["x"] = largest["x"]
                        smallest["y"] = largest["y"] + largest["h"] / 2 - smallest["h"] / 2
                    elif c.edge == "right":
                        smallest["x"] = largest["x"] + largest["w"] - smallest["w"]
                        smallest["y"] = largest["y"] + largest["h"] / 2 - smallest["h"] / 2
        elif cname == "PolygonSidesEquals":
            for l in by_type.get("polygon", []):
                l["sides"] = c.sides
        elif cname == "StarPointsEquals":
            for l in by_type.get("star", []):
                l["points"] = c.points
        elif cname == "LayerAspectRatioGreaterThan":
            # Re-apply after Pass 5 has resized w via LayerWidthFraction etc.
            for l in by_type.get(c.layer_type, []):
                if c.axis == "horizontal":
                    l["w"] = max(l["w"], int(l["h"] * (c.ratio + 0.5)))
                else:
                    l["h"] = max(l["h"], int(l["w"] * (c.ratio + 0.5)))
        elif cname == "LinesOnDiagonal":
            # Re-run after sizing changes so lines actually span the rect.
            rects = by_type.get(c.rect_type, [])
            lines = by_type.get(c.line_type, [])
            if rects and len(lines) >= 2:
                r = rects[0]
                lines[0]["x"] = r["x"]; lines[0]["y"] = r["y"]
                lines[0]["w"] = r["w"]; lines[0]["h"] = r["h"]
                lines[0]["p1"] = {"x": 0, "y": 0}
                lines[0]["p2"] = {"x": r["w"], "y": r["h"]}
                lines[1]["x"] = r["x"]; lines[1]["y"] = r["y"]
                lines[1]["w"] = r["w"]; lines[1]["h"] = r["h"]
                lines[1]["p1"] = {"x": r["w"], "y": 0}
                lines[1]["p2"] = {"x": 0, "y": r["h"]}
        elif cname == "LayerSizeEquals":
            for l in by_type.get(c.layer_type, []):
                if c.width is not None:
                    l["w"] = c.width
                if c.height is not None:
                    l["h"] = c.height
        elif cname == "LayersStacked":
            # Re-run after Pass 9 sizing so positions reflect final w/h.
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= 2:
                if c.axis == "x":
                    layers_sorted = sorted(layers, key=lambda l: l["x"])
                    cur = layers_sorted[0]["x"]
                    for l in layers_sorted:
                        l["x"] = cur
                        cur += l["w"] + c.gap_px
                else:
                    layers_sorted = sorted(layers, key=lambda l: l["y"])
                    cur = layers_sorted[0]["y"]
                    for l in layers_sorted:
                        l["y"] = cur
                        cur += l["h"] + c.gap_px
        elif cname == "LayersHaveConsistentGap":
            # Run in final pass so positions reflect final w/h after sizing.
            # If there's a frame, fit the row inside it to keep AllLayerBoundsInside happy.
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= 2:
                frames = by_type.get("frame", [])
                if frames:
                    frame = frames[0]
                    avail = frame["w"] - 40
                    total_w = sum(l["w"] for l in layers)
                    n = len(layers)
                    # leftover space split as gaps; clamp to a positive workable range
                    gap = max(c.min_gap + 4, min((avail - total_w) / max(1, n - 1), 40.0))
                    cur_x = frame["x"] + 20
                    base_y = frame["y"] + 100
                else:
                    gap = max(c.min_gap + 4, 20.0)
                    cur_x = 100
                    base_y = 100
                if c.axis == "x":
                    layers_sorted = sorted(layers, key=lambda l: l["x"])
                    cur = cur_x
                    for l in layers_sorted:
                        l["y"] = base_y
                        l["x"] = cur
                        cur += l["w"] + gap
                else:
                    layers_sorted = sorted(layers, key=lambda l: l["y"])
                    cur = base_y
                    for l in layers_sorted:
                        l["x"] = cur_x
                        l["y"] = cur
                        cur += l["h"] + gap
        elif cname == "LayersAtDistinctPositions":
            # Re-spread layers to ensure distinct centers (overrides LayersOverlap stacking).
            layers = by_type.get(c.layer_type, [])
            need = c.min_distinct
            if len(layers) >= need:
                # Lay out in a 2-column grid offset so we get up to N distinct positions
                # while still keeping bbox overlaps for any LayersOverlap check.
                step = max(c.tolerance * 2, 20.0)
                base_x = layers[0].get("x", 100)
                base_y = layers[0].get("y", 100)
                for i, l in enumerate(layers):
                    l["x"] = base_x + (i % 2) * step
                    l["y"] = base_y + (i // 2) * step
        elif cname == "LayersAligned":
            same_type = by_type.get(c.layer_type, [])
            if len(same_type) >= 2:
                if c.axis == "center_x":
                    cx = same_type[0]["x"] + same_type[0]["w"] / 2
                    for l in same_type[1:]:
                        l["x"] = cx - l["w"] / 2
                elif c.axis == "center_y":
                    cy = same_type[0]["y"] + same_type[0]["h"] / 2
                    for l in same_type[1:]:
                        l["y"] = cy - l["h"] / 2
                elif c.axis == "x":
                    target = same_type[0]["x"]
                    for l in same_type[1:]:
                        l["x"] = target
                elif c.axis == "y":
                    target = same_type[0]["y"]
                    for l in same_type[1:]:
                        l["y"] = target
        elif cname == "LayerEdgesAligned":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            if a_layers and b_layers and a_layers[0] is not b_layers[0]:
                a = a_layers[0]
                b = b_layers[0]
                if c.edge_b == "top":      target = b["y"]
                elif c.edge_b == "bottom": target = b["y"] + b["h"]
                elif c.edge_b == "left":   target = b["x"]
                elif c.edge_b == "right":  target = b["x"] + b["w"]
                elif c.edge_b == "center_x": target = b["x"] + b["w"] / 2
                elif c.edge_b == "center_y": target = b["y"] + b["h"] / 2
                else: continue
                if c.edge_a == "top":      a["y"] = target
                elif c.edge_a == "bottom": a["y"] = target - a["h"]
                elif c.edge_a == "left":   a["x"] = target
                elif c.edge_a == "right":  a["x"] = target - a["w"]
                elif c.edge_a == "center_x": a["x"] = target - a["w"] / 2
                elif c.edge_a == "center_y": a["y"] = target - a["h"] / 2
        elif cname == "LayerCenteredOnLayer":
            a_layers = by_type.get(c.type_a, [])
            b_layers = by_type.get(c.type_b, [])
            axis = getattr(c, "axis", "both")
            if c.type_a == c.type_b and len(a_layers) >= 2:
                # same-type: align the smallest layer's center on the largest's center
                largest = max(a_layers, key=lambda l: l["w"] * l["h"])
                smallest = min(a_layers, key=lambda l: l["w"] * l["h"])
                if largest is not smallest:
                    if axis in ("x", "both"):
                        smallest["x"] = largest["x"] + largest["w"] / 2 - smallest["w"] / 2
                    if axis in ("y", "both"):
                        smallest["y"] = largest["y"] + largest["h"] / 2 - smallest["h"] / 2
            elif a_layers and b_layers and a_layers[0] is not b_layers[0]:
                a = a_layers[0]
                b = b_layers[0]
                if axis in ("x", "both"):
                    a["x"] = b["x"] + b["w"] / 2 - a["w"] / 2
                if axis in ("y", "both"):
                    a["y"] = b["y"] + b["h"] / 2 - a["h"] / 2
        elif cname == "LayerCenteredInFrame":
            # Re-run after Pass 5 sizing so the centered layer reflects final w/h.
            for parent in by_type.get("frame", []):
                placed = False
                for child in parent.get("children", []):
                    if child.get("type") == c.layer_type:
                        child["x"] = parent["w"] / 2 - child["w"] / 2
                        child["y"] = parent["h"] / 2 - child["h"] / 2
                        placed = True
                        break
                if placed:
                    break
        elif cname == "LayersFlankLayer":
            # Skip here — handled in Pass 8.7 after SmallerLayerInsideLarger
            # has finalized the rectangle positions (this main-loop iteration
            # would see stale pivot positions).
            pass
        elif cname == "LayersBracketAllOnAxis":
            # Place brackets[0] above all inners, brackets[1] below all inners.
            brackets = by_type.get(c.bracket_type, [])
            inners = by_type.get(c.inner_type, [])
            if len(brackets) >= 2 and inners:
                if c.axis == "y":
                    inner_min = min(i["y"] for i in inners)
                    inner_max = max(i["y"] + i["h"] for i in inners)
                    brackets[0]["y"] = inner_min - brackets[0]["h"] - 4
                    brackets[1]["y"] = inner_max + 4
                else:
                    inner_min = min(i["x"] for i in inners)
                    inner_max = max(i["x"] + i["w"] for i in inners)
                    brackets[0]["x"] = inner_min - brackets[0]["w"] - 4
                    brackets[1]["x"] = inner_max + 4
        elif cname == "LayersOrderedByRotation":
            # Assign rotations and arrange so first rotation precedes second on axis.
            layers = by_type.get(c.layer_type, [])
            if len(layers) >= 2:
                halves = max(1, len(layers) // 2)
                for i, l in enumerate(layers):
                    l["rotation"] = c.rotation_first if i < halves else c.rotation_second
                sorted_layers = sorted(layers, key=lambda l: 0 if l.get("rotation") == c.rotation_first else 1)
                if c.axis == "y":
                    cur = sorted_layers[0]["y"]
                    for l in sorted_layers:
                        l["y"] = cur
                        cur += l["h"]
                else:
                    cur = sorted_layers[0]["x"]
                    for l in sorted_layers:
                        l["x"] = cur
                        cur += l["w"]

    # ── Pass 8.5: ensure all layers of types required by LayerGroupAllInSameFrame
    # are direct children of a single frame.
    for c in checks:
        if type(c).__name__ == "LayerGroupAllInSameFrame":
            frames = by_type.get("frame", [])
            target_layers = by_type.get(c.layer_type, [])
            if frames and target_layers:
                frame = frames[0]
                # Move every target_layer that isn't already a direct child of frame
                existing = set(id(x) for x in frame.get("children", []))
                # Walk the whole doc and remove from any other parent, then add to frame
                def _remove(nodes, ids):
                    for n in list(nodes):
                        if id(n) in ids:
                            nodes.remove(n)
                        elif "children" in n:
                            _remove(n["children"], ids)
                ids_to_move = set()
                for l in target_layers:
                    if id(l) not in existing:
                        ids_to_move.add(id(l))
                if ids_to_move:
                    for page in doc.get("pages", []):
                        _remove(page.get("children", []), ids_to_move)
                    for l in target_layers:
                        if id(l) in ids_to_move:
                            frame.setdefault("children", []).append(l)

    # ── Pass 8.7: line-endpoint primitives (LinesShareEndpoint / LineAngleEquals
    # / LineLengthEquals / PolygonCornersAligned) need explicit per-layer p1/p2.
    # Existing handlers set bbox + rotation; here we set local-space p1 to the bbox
    # center so all lines (already concentric) share an endpoint after transform,
    # and leave default p2 so the rotation property still drives visual angle.
    if any(type(c).__name__ == "LinesShareEndpoint" for c in checks):
        for line in by_type.get("line", []):
            line["p1"] = {"x": line["w"] / 2, "y": line["h"] / 2}
            # leave p2 unset → defaults to right-edge, rotation drives angle
            if "p2" in line:
                del line["p2"]

    # LinesRadialFromSharedEndpoint: each line's p1 sits at a single shared
    # world center; p2 fans out evenly around it at uniform length.
    for c in checks:
        if type(c).__name__ != "LinesRadialFromSharedEndpoint":
            continue
        lines = by_type.get("line", [])[: c.n]
        if not lines:
            continue
        center_x, center_y = 500.0, 500.0
        length = max(c.min_length_px + 40.0, 100.0)
        for i, line in enumerate(lines):
            angle = (2 * math.pi * i) / c.n
            tip_x = center_x + length * math.cos(angle)
            tip_y = center_y + length * math.sin(angle)
            line["x"] = 0.0
            line["y"] = 0.0
            line["w"] = max(line.get("w", 80) or 80, length + 10)
            line["h"] = max(line.get("h", 80) or 80, length + 10)
            line["rotation"] = 0
            line["p1"] = {"x": center_x, "y": center_y}
            line["p2"] = {"x": tip_x, "y": tip_y}

    # Re-run LayersFlankLayer after rectangles have been positioned by
    # SmallerLayerInsideLarger above. The first run in the main loop sees stale
    # rectangle positions because LayersFlankLayer is checked before
    # SmallerLayerInsideLarger in task definitions.
    for c in checks:
        if type(c).__name__ != "LayersFlankLayer":
            continue
        flankers = by_type.get(c.flanker_type, [])
        pivots = by_type.get(c.pivot_type, [])
        if len(flankers) < 2 or not pivots:
            continue
        flanker_must_fit_inside = any(
            type(c2).__name__ == "AllLayerBoundsInside"
            and c2.inner_type == c.flanker_type
            and c2.outer_type == c.pivot_type
            for c2 in checks
        )
        if not (flanker_must_fit_inside and len(pivots) >= 2):
            continue
        outer = max(pivots, key=lambda p: p["w"] * p["h"])
        inner = min(pivots, key=lambda p: p["w"] * p["h"])
        if c.axis == "x":
            gap_left = inner["x"] - outer["x"]
            gap_right = (outer["x"] + outer["w"]) - (inner["x"] + inner["w"])
            target_w = max(20, min(flankers[0]["w"], gap_left - 6, gap_right - 6))
            target_h = target_w
            for f in flankers[:2]:
                f["w"] = target_w
                f["h"] = target_h
                f["y"] = outer["y"] + outer["h"] / 2 - target_h / 2
            flankers[0]["x"] = outer["x"] + (gap_left - target_w) / 2
            flankers[1]["x"] = inner["x"] + inner["w"] + (gap_right - target_w) / 2
        else:
            gap_top = inner["y"] - outer["y"]
            gap_bot = (outer["y"] + outer["h"]) - (inner["y"] + inner["h"])
            target_h = max(20, min(flankers[0]["h"], gap_top - 6, gap_bot - 6))
            target_w = target_h
            for f in flankers[:2]:
                f["w"] = target_w
                f["h"] = target_h
                f["x"] = outer["x"] + outer["w"] / 2 - target_w / 2
            flankers[0]["y"] = outer["y"] + (gap_top - target_h) / 2
            flankers[1]["y"] = inner["y"] + inner["h"] + (gap_bot - target_h) / 2

    # PolygonCornersAligned: triangle (sides=3) has its bottom-2 vertices at
    # local y = 0.75*h (NOT h — there's a 0.25*h gap below them). To put those
    # vertices on the rect's top edge AND at the rect's top corners:
    #   layer.y = rect.top - 0.75 * poly.h
    #   layer.x = rect.x - 0.067 * poly.w  (with poly.w = 1.155 * rect.w)
    # so that bottom vertices land at rect.x and rect.x + rect.w.
    if any(type(c).__name__ == "PolygonCornersAligned" for c in checks):
        rects = by_type.get("rectangle", [])
        polys = by_type.get("polygon", [])
        if rects and polys:
            outer = max(rects, key=lambda l: l["w"] * l["h"])
            poly = polys[0]
            poly["w"] = outer["w"] / 0.866   # ≈ 1.1547 * rect.w
            poly["x"] = outer["x"] - poly["w"] * (0.5 - 0.5 * 0.866)  # ≈ rect.x - 0.067·poly.w
            poly["y"] = outer["y"] - poly["h"] * 0.75
            poly["rotation"] = 0
            poly["scaleX"] = 1
            poly["scaleY"] = 1

    # ── Pass 9: shift everything inside any frame if AllLayerBoundsInside is required.
    # After all sizing/positioning, layers may extend off-frame (e.g., polygon above
    # body has negative y). Shift the entire layer set so all layers fit inside frame.
    needs_frame_fit = any(
        type(c).__name__ in ("AllLayerBoundsInside",) and c.outer_type == "frame"
        for c in checks
    )
    if needs_frame_fit:
        frames = by_type.get("frame", [])
        if frames:
            frame = frames[0]
            # Collect all non-frame layers that should fit inside the frame
            inner_types = {c.inner_type for c in checks
                           if type(c).__name__ == "AllLayerBoundsInside"
                           and c.outer_type == "frame"}
            target_layers = []
            for t in inner_types:
                target_layers.extend(by_type.get(t, []))
            # Skip shift if any LayerEdgesAligned anchors a target type to the frame edge
            # (otherwise Pass 9 would push the anchored layer off the frame edge).
            anchored = any(
                type(c).__name__ == "LayerEdgesAligned"
                and c.type_a in inner_types and c.type_b == "frame"
                for c in checks
            )
            if target_layers and not anchored:
                min_x = min(l["x"] for l in target_layers)
                min_y = min(l["y"] for l in target_layers)
                max_x = max(l["x"] + l["w"] for l in target_layers)
                max_y = max(l["y"] + l["h"] for l in target_layers)
                shift_x = max(0, frame["x"] + 10 - min_x)
                shift_y = max(0, frame["y"] + 10 - min_y)
                if shift_x > 0 or shift_y > 0:
                    for l in target_layers:
                        l["x"] += shift_x
                        l["y"] += shift_y


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
    task_dirs = sorted(p for p in DELIVERY_DIR.glob("task_*") if (p / "verifier.py").is_file())

    rows = []
    for task_dir in task_dirs:
        tname = task_dir.name
        try:
            task = load_task_from_dir(task_dir)
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

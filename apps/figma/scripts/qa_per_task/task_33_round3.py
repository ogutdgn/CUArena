"""Round 3 edge cases — hunt for surviving false positives in task_33 (pie chart).

Each case is a wrong pie chart that the verifier should give < 0.95.
"""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                # scripts/
sys.path.insert(0, str(HERE.parent.parent))         # apps/figma/

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task,
    PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    BLACK, LIGHT_GRAY, DARK_GRAY, WARM_ORANGE, CREAM, DEEP_BLUE, TEAL,
    COBALT, MAGENTA, SAND, PALE_YELLOW, DEEP_PURPLE,
)
import importlib.util
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_33" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
W1 = (0.95, 0.4, 0.4)
W2 = (0.95, 0.85, 0.2)


def evt(ellipse=1, polygon=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.append(make_event("tool_change", before="ellipse", after="polygon"))
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pie(base=TEAL, w1=W1, w2=W2):
    cx, cy = 500, 500
    base_circle = L("ellipse", cx - 150, cy - 150, 300, 300, base)
    wedge_1 = L("polygon", cx - 30, cy - 150, 60, 300, w1, sides=3, rotation=30)
    wedge_2 = L("polygon", cx - 30, cy - 150, 60, 300, w2, sides=3, rotation=120)
    return [base_circle, wedge_1, wedge_2]


CASES = []
def add(label, log): CASES.append((label, log))


# ── K. Subtle deceptions ─────────────────────────────────────────────
def k1():
    """Wedges at same rotation (no different angles)."""
    layers = perfect_pie()
    layers[1]["rotation"] = 30
    layers[2]["rotation"] = 30
    return make_log(layers, evt())
add("K1: wedges at same rotation", k1())


def k2():
    """Wedges 1° apart (just under tol 10°)."""
    layers = perfect_pie()
    layers[1]["rotation"] = 30
    layers[2]["rotation"] = 35
    return make_log(layers, evt())
add("K2: wedges 5° apart (under tol)", k2())


def k3():
    """Base near-teal (within tol 0.25)."""
    NEAR_TEAL = (0.10, 0.55, 0.55)
    layers = perfect_pie(base=NEAR_TEAL)
    return make_log(layers, evt())
add("K3: near-teal base (within tol)", k3())


def k4():
    """Base completely behind wedges (z-order swapped)."""
    layers = perfect_pie()
    base = layers.pop(0)
    layers.append(base)
    return make_log(layers, evt())
add("K4: base drawn last (above wedges)", k4())


def k5():
    """Wedges below base in z-order but base on top."""
    layers = perfect_pie()
    # Move base to between wedges
    layers = [layers[1], layers[0], layers[2]]
    return make_log(layers, evt())
add("K5: base sandwiched between wedges", k5())


def k6():
    """Wedges huge and base is small — wedges become the dominant shape."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 480, 480, 40, 40, TEAL)  # tiny base
    layers[1]["w"] = 200
    layers[1]["h"] = 400
    layers[2]["w"] = 200
    layers[2]["h"] = 400
    return make_log(layers, evt())
add("K6: tiny base, huge wedges", k6())


def k7():
    """Wedges have cornerRadius (round-corner triangles)."""
    layers = perfect_pie()
    layers[1]["cornerRadius"] = 30
    layers[2]["cornerRadius"] = 30
    return make_log(layers, evt())
add("K7: wedges with corner radius", k7())


def k8():
    """Wedges visually overlap base only on the edge (not actually 'on top')."""
    layers = perfect_pie()
    layers[1]["x"] = 350  # offset so wedge sits beside base
    layers[2]["x"] = 700
    return make_log(layers, evt())
add("K8: wedges placed beside base (no overlap)", k8())


def k9():
    """Wedges rotated to be base-tangent (don't actually wedge)."""
    layers = perfect_pie()
    layers[1]["rotation"] = 90
    layers[2]["rotation"] = 90
    return make_log(layers, evt())
add("K9: wedges parallel rotation 90°", k9())


def k10():
    """Wedges very thin (5px) and base much larger."""
    layers = perfect_pie()
    layers[1]["w"] = 5
    layers[2]["w"] = 5
    return make_log(layers, evt())
add("K10: wedges 5px wide (almost lines)", k10())


# ── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Base alpha=0 (invisible)."""
    layers = perfect_pie()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return make_log(layers, evt())
add("L1: base alpha=0", l1())


def l2():
    """Base layer opacity=0."""
    layers = perfect_pie()
    layers[0]["opacity"] = 0.0
    return make_log(layers, evt())
add("L2: base layer opacity=0", l2())


def l3():
    """Base fill visible=False."""
    layers = perfect_pie()
    layers[0]["fills"][0]["visible"] = False
    return make_log(layers, evt())
add("L3: base fill visible=False", l3())


def l4():
    """Wedges all opacity=0.05 (barely visible)."""
    layers = perfect_pie()
    for l in layers[1:]:
        l["fills"][0]["opacity"] = 0.05
    return make_log(layers, evt())
add("L4: wedges opacity 0.05", l4())


def l5():
    """All shapes alpha=0 (entirely invisible structurally)."""
    layers = perfect_pie()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return make_log(layers, evt())
add("L5: all alpha=0", l5())


# ── M. Geometry tricks ───────────────────────────────────────────────
def m1():
    """Base 1×1 degenerate."""
    layers = perfect_pie()
    layers[0]["w"] = 1
    layers[0]["h"] = 1
    return make_log(layers, evt())
add("M1: base 1×1", m1())


def m2():
    """Wedges at 0×0 (invisible)."""
    layers = perfect_pie()
    layers[1]["w"] = 0
    layers[1]["h"] = 0
    layers[2]["w"] = 0
    layers[2]["h"] = 0
    return make_log(layers, evt())
add("M2: wedges 0×0", m2())


def m3():
    """Base squashed (oval, not circle)."""
    layers = perfect_pie()
    layers[0]["h"] = 50  # 300×50 stretched oval
    return make_log(layers, evt())
add("M3: base oval 300×50", m3())


def m4():
    """All wedges identical (no different angles)."""
    layers = perfect_pie()
    layers[1]["rotation"] = 30
    layers[2]["rotation"] = 30
    layers[1]["x"] = layers[2]["x"]  # also same position
    layers[1]["y"] = layers[2]["y"]
    return make_log(layers, evt())
add("M4: wedges identical (overlap)", m4())


def m5():
    """Wedges fully cover base (entire pie)."""
    layers = perfect_pie()
    layers[1]["x"] = 350
    layers[1]["y"] = 350
    layers[1]["w"] = 300
    layers[1]["h"] = 300
    layers[2]["x"] = 350
    layers[2]["y"] = 350
    layers[2]["w"] = 300
    layers[2]["h"] = 300
    return make_log(layers, evt())
add("M5: wedges = base size (cover all)", m5())


def m6():
    """Base is full canvas."""
    layers = perfect_pie()
    layers[0]["x"] = 0
    layers[0]["y"] = 0
    layers[0]["w"] = 1280
    layers[0]["h"] = 1280
    return make_log(layers, evt())
add("M6: base = full canvas", m6())


def m7():
    """Wedges have no fill (only stroke)."""
    layers = perfect_pie()
    for l in layers[1:]:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLUE, weight=2)]
    return make_log(layers, evt())
add("M7: wedges stroke-only", m7())


# ── N. Structural tricks ─────────────────────────────────────────────
def n1():
    """Base in frame, wedges outside."""
    layers = perfect_pie()
    frame = make_frame([layers[0]], w=1000, h=1000)
    return make_log([frame, *layers[1:]], evt())
add("N1: base in frame, wedges on page", n1())


def n2():
    """Each shape in its own frame."""
    layers = perfect_pie()
    frames = [make_frame([s], w=1000, h=1000) for s in layers]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())


def n3():
    """Pie inside component (not frame)."""
    layers = perfect_pie()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: pie inside component", n3())


def n4():
    """Pie deep nested in groups."""
    layers = perfect_pie()
    g3 = {"id": "g3", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    return make_log([g1], evt())
add("N4: pie 3-deep nested groups", n4())


# ── O. Wrong types ───────────────────────────────────────────────────
def o1():
    """Base is rectangle not ellipse."""
    layers = perfect_pie()
    layers[0] = L("rectangle", 350, 350, 300, 300, TEAL)
    return make_log(layers, evt(ellipse=0))
add("O1: base is rectangle", o1())


def o2():
    """Wedges are stars (not polygons)."""
    layers = perfect_pie()[:1]
    layers.append(make_layer("star", x=470, y=350, w=60, h=300, fill=W1, points=5, innerRatio=0.4))
    layers.append(make_layer("star", x=470, y=350, w=60, h=300, fill=W2, points=5, innerRatio=0.4))
    return make_log(layers, evt(polygon=0))
add("O2: wedges are stars", o2())


def o3():
    """Wedges are 4-sided polygons (squares)."""
    layers = perfect_pie()
    layers[1]["sides"] = 4
    layers[2]["sides"] = 4
    return make_log(layers, evt())
add("O3: wedges 4-sided (squares)", o3())


# ── Run ─────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)

for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

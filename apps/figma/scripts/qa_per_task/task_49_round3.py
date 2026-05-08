"""Round-3 novel-deception battery for task 49 (decorative ribbon).

30+ NEW edge cases not in the round-1 battery. Categories K (subtle),
L (visibility), M (geometry), N (structural), O (wrong types).
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_49" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
def evt(vector=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(vector): sem.append(make_event("create_vector"))
    sem.extend(extras)
    return sem


def perfect_ribbon(stroke_w=12, dashed=True, color=GOLD):
    dash = {"dash": 8, "gap": 4} if dashed else None
    return make_layer("vector", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=color, weight=stroke_w, dash=dash)])


def H(layers=None, evts=None):
    if layers is None: layers = [perfect_ribbon()]
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions (8) ───────────────────────────────────────
def k1():
    """Stroke weight 13.9 — just inside 12±2 tolerance."""
    layers = [perfect_ribbon(stroke_w=13.9)]
    return H(layers)
add("K1: stroke weight 13.9 (just within tol)", k1())

def k2():
    """Vector rotated 14° — inside 15° tolerance."""
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 14
    return H(layers)
add("K2: vector rotated 14° (within tol)", k2())

def k3():
    """Multiple strokes, only first is dashed (passes IsDashed because checks first)."""
    layers = [perfect_ribbon(dashed=True)]
    layers[0]["strokes"].append(make_stroke(rgb=BLACK, weight=12, dash=None))
    return H(layers)
add("K3: 2 strokes, first dashed second solid", k3())

def k4():
    """Multiple strokes, only first has weight=12."""
    layers = [perfect_ribbon(stroke_w=12)]
    layers[0]["strokes"].append(make_stroke(rgb=BLACK, weight=2,
                                              dash={"dash": 8, "gap": 4}))
    return H(layers)
add("K4: 2 strokes, mixed weights", k4())

def k5():
    """Vector w=51 — just over LayerSizeAtLeast 50 minimum."""
    layers = [perfect_ribbon()]; layers[0]["w"] = 51; layers[0]["h"] = 21
    return H(layers)
add("K5: vector 51×21 (just over min)", k5())

def k6():
    """Stroke alpha=0.55 — just over LayerVisible 0.5 threshold."""
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0.55
    return H(layers)
add("K6: stroke alpha=0.55 (over LayerVisible tol)", k6())

def k7():
    """Vector with cornerRadius (no effect on vector but adds noise)."""
    layers = [perfect_ribbon()]; layers[0]["cornerRadius"] = 50
    return H(layers)
add("K7: vector with cornerRadius=50", k7())

def k8():
    """Vector with no fill but solid stroke and a dashed marker stroke."""
    layers = [perfect_ribbon(dashed=True)]
    return H(layers)
add("K8: control (perfect dashed)", k8())


# ─── L. Visibility tricks (6) ───────────────────────────────────────
def l1():
    """Vector visible=False (whole layer hidden)."""
    layers = [perfect_ribbon()]; layers[0]["visible"] = False
    return H(layers)
add("L1: vector visible=False", l1())

def l2():
    """Vector layer opacity=0.3 (just under threshold)."""
    layers = [perfect_ribbon()]; layers[0]["opacity"] = 0.3
    return H(layers)
add("L2: vector opacity=0.3", l2())

def l3():
    """Stroke paint alpha=0.2 (under 0.5 threshold)."""
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0.2
    return H(layers)
add("L3: stroke alpha=0.2", l3())

def l4():
    """Stroke visible=False explicitly."""
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["visible"] = False
    return H(layers)
add("L4: stroke visible=False", l4())

def l5():
    """Stroke weight=0 (zero-width)."""
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["weight"] = 0
    return H(layers)
add("L5: stroke weight=0", l5())

def l6():
    """Empty strokes array."""
    layers = [perfect_ribbon()]
    layers[0]["strokes"] = []
    return H(layers)
add("L6: vector strokes=[]", l6())


# ─── M. Geometry tricks (8) ─────────────────────────────────────────
def m1():
    """Vector w=2000, h=2 (super wide thin)."""
    layers = [perfect_ribbon()]
    layers[0]["w"] = 2000; layers[0]["h"] = 2
    return H(layers)
add("M1: vector 2000×2 super thin", m1())

def m2():
    """Vector rotated 16° — just over 15° tolerance."""
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 16
    return H(layers)
add("M2: vector rotated 16° (just over tol)", m2())

def m3():
    """Vector scaleX=-1 (flipped horizontally)."""
    layers = [perfect_ribbon()]; layers[0]["scaleX"] = -1
    return H(layers)
add("M3: vector scaleX=-1", m3())

def m4():
    """Vector with no path data (degenerate vector)."""
    layers = [perfect_ribbon()]; layers[0]["path"] = ""
    return H(layers)
add("M4: vector empty path data", m4())

def m5():
    """Vector w=1600, h=1600 (huge square but still under cap)."""
    layers = [perfect_ribbon()]
    layers[0]["w"] = 1600; layers[0]["h"] = 1600
    return H(layers)
add("M5: vector 1600×1600 (over short-dim cap)", m5())

def m6():
    """Vector rotated 90° (S-curve becomes vertical)."""
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 90
    return H(layers)
add("M6: vector rotated 90°", m6())

def m7():
    """Vector at extreme position (should still pass with no position checks)."""
    layers = [perfect_ribbon()]; layers[0]["x"] = -10000; layers[0]["y"] = -10000
    return H(layers)
add("M7: vector at far negative coords", m7())

def m8():
    """Vector with negative dimensions."""
    layers = [perfect_ribbon()]; layers[0]["w"] = -100; layers[0]["h"] = -100
    return H(layers)
add("M8: vector negative dims", m8())


# ─── N. Hierarchy / structural tricks (4) ───────────────────────────
def n1():
    """Vector inside a deeply-nested component."""
    v = perfect_ribbon()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "children": [v]}
    inst = {"id": "i1", "type": "instance", "x": 0, "y": 0, "w": 1000, "h": 1000,
            "fills": [], "children": [component]}
    return make_log([inst], evt())
add("N1: vector inside instance>component", n1())

def n2():
    """Two vectors, one canonical and one tiny degenerate."""
    v1 = perfect_ribbon()
    v2 = make_layer("vector", x=100, y=100, w=1, h=1, fill=None,
                     strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})])
    return make_log([v1, v2], evt(vector=2))
add("N2: 2 vectors (one degenerate)", n2())

def n3():
    """Vector with 3 strokes (excessive, may break weight checks)."""
    v = perfect_ribbon()
    v["strokes"].append(make_stroke(rgb=NAVY, weight=4))
    v["strokes"].append(make_stroke(rgb=PINK, weight=2))
    return H([v])
add("N3: vector with 3 stacked strokes", n3())

def n4():
    """Vector inside group with vector deletion event after."""
    v = perfect_ribbon()
    grp = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
           "fills": [], "children": [v]}
    return make_log([grp], evt(extras=[make_event("delete"),
                                          make_event("create_vector")]))
add("N4: vector in group + delete events", n4())


# ─── O. Wrong types (5) ─────────────────────────────────────────────
def o1():
    """Line with dashed stroke instead of vector (line tool, not pen)."""
    line = make_layer("line", x=200, y=300, w=600, h=2, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})])
    return make_log([line], [make_event("session_start"),
                              make_event("tool_change", before="select", after="line"),
                              make_event("create_line")])
add("O1: line instead of vector", o1())

def o2():
    """Rectangle with same stroke setup."""
    rect = make_layer("rectangle", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})])
    return make_log([rect], [make_event("session_start"),
                              make_event("tool_change", before="select", after="rectangle"),
                              make_event("create_rectangle")])
add("O2: rectangle instead of vector", o2())

def o3():
    """Polygon (octagon) instead of vector with dashed stroke."""
    poly = make_layer("polygon", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})], sides=8)
    return make_log([poly], [make_event("session_start"),
                              make_event("tool_change", before="select", after="polygon"),
                              make_event("create_polygon")])
add("O3: polygon instead of vector", o3())

def o4():
    """Ellipse instead of vector."""
    ell = make_layer("ellipse", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})])
    return make_log([ell], [make_event("session_start"),
                              make_event("tool_change", before="select", after="ellipse"),
                              make_event("create_ellipse")])
add("O4: ellipse instead of vector", o4())

def o5():
    """Star instead of vector."""
    star = make_layer("star", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})],
                       points=5, innerRatio=0.4)
    return make_log([star], [make_event("session_start"),
                              make_event("tool_change", before="select", after="star"),
                              make_event("create_star")])
add("O5: star instead of vector", o5())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " ⚠ FP" if score >= 0.95 else ""
        if score >= 0.95: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\n{fp_count} cases scored ≥ 0.95")

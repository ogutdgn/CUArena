"""Round 3 edge cases — hunt for surviving false positives in task_36 (vintage frame)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, WHITE, BLACK, RED, NAVY, GOLD,
)
from tasks import task_36_polaroid as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(rectangle=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rectangle): sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_polaroid(rotation=5, color=WHITE, has_shadow=True):
    effects = [make_drop_shadow(y=8, blur=12)] if has_shadow else []
    outer = L("rectangle", 400, 400, 300, 340, color, rotation=rotation, effects=effects)
    inner = L("rectangle", 420, 440, 260, 260, LIGHT_GRAY, rotation=rotation)
    return [outer, inner]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_polaroid()
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ── K. Subtle deceptions ─────────────────────────────────────────────
def k1():
    """Inner is exactly the same size as outer."""
    layers = perfect_polaroid()
    layers[1] = L("rectangle", 400, 400, 300, 340, LIGHT_GRAY, rotation=5)
    return H(layers)
add("K1: inner = outer dimensions", k1())


def k2():
    """Inner just 5px smaller than outer (inside tol)."""
    layers = perfect_polaroid()
    layers[1] = L("rectangle", 402, 402, 296, 336, LIGHT_GRAY, rotation=5)
    return H(layers)
add("K2: inner 5px smaller (within tol)", k2())


def k3():
    """Inner 10px offset center (just outside tol 15)."""
    layers = perfect_polaroid()
    # inner center should be (550, 570) but here put it at (570, 590)
    layers[1] = L("rectangle", 440, 460, 260, 260, LIGHT_GRAY, rotation=5)
    return H(layers)
add("K3: inner 20px off-center", k3())


def k4():
    """Inner cornerRadius = 0.4 of size (max allowed)."""
    layers = perfect_polaroid()
    layers[1]["cornerRadius"] = 100  # 100/260 = 0.385 < 0.4
    return H(layers)
add("K4: inner cornerRadius near max (0.385)", k4())


def k5():
    """Inner cornerRadius = 0.5 of size (over max 0.4)."""
    layers = perfect_polaroid()
    layers[1]["cornerRadius"] = 130  # 130/260 = 0.5 > 0.4
    return H(layers)
add("K5: inner cornerRadius over max", k5())


def k6():
    """Inner is rectangle but 95% of outer (just under cap)."""
    layers = perfect_polaroid()
    # outer w=300, max 0.95 = 285. Set inner w=284 - within but barely
    layers[1] = L("rectangle", 408, 448, 284, 324, LIGHT_GRAY, rotation=5)
    return H(layers)
add("K6: inner 95% of outer (boundary)", k6())


def k7():
    """Inner mirrored (scaleX=-1) — flipped variant."""
    layers = perfect_polaroid()
    layers[1]["scaleX"] = -1
    return H(layers)
add("K7: inner mirrored", k7())


def k8():
    """Outer flipped vertically."""
    layers = perfect_polaroid()
    layers[0]["scaleY"] = -1
    return H(layers)
add("K8: outer flipped V", k8())


def k9():
    """Both invisible (opacity=0)."""
    layers = perfect_polaroid()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("K9: both opacity=0", k9())


def k10():
    """Both fill alpha=0."""
    layers = perfect_polaroid()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("K10: both alpha=0", k10())


# ── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Inner fill alpha=0."""
    layers = perfect_polaroid()
    layers[1]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: inner alpha=0", l1())


def l2():
    """Outer fill visible=False."""
    layers = perfect_polaroid()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L2: outer fill visible=False", l2())


def l3():
    """Inner layer.opacity=0."""
    layers = perfect_polaroid()
    layers[1]["opacity"] = 0.0
    return H(layers)
add("L3: inner layer opacity=0", l3())


def l4():
    """Outer fill opacity=0.05."""
    layers = perfect_polaroid()
    layers[0]["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L4: outer fill opacity 0.05", l4())


def l5():
    """Both visible=False."""
    layers = perfect_polaroid()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L5: both layer visible=False", l5())


# ── M. Geometry tricks ───────────────────────────────────────────────
def m1():
    """Inner 1×1 (degenerate)."""
    layers = perfect_polaroid()
    layers[1]["w"] = 1
    layers[1]["h"] = 1
    return H(layers)
add("M1: inner 1×1", m1())


def m2():
    """Both 0×0."""
    layers = perfect_polaroid()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("M2: both 0×0", m2())


def m3():
    """Outer is full canvas (no real frame composition)."""
    layers = perfect_polaroid()
    layers[0]["x"] = 0
    layers[0]["y"] = 0
    layers[0]["w"] = 1280
    layers[0]["h"] = 832
    return H(layers)
add("M3: outer = full canvas", m3())


def m4():
    """Inner only (no outer). Just 1 rect duplicated."""
    layers = [L("rectangle", 400, 400, 300, 340, WHITE, rotation=5,
                effects=[make_drop_shadow()])]
    return H(layers, evts=evt(rectangle=1))
add("M4: only outer rect (no inner)", m4())


def m5():
    """Outer huge corner radius (rectangle becomes circle)."""
    layers = perfect_polaroid()
    layers[0]["cornerRadius"] = 200  # >> 0.4 frac
    return H(layers)
add("M5: outer cornerRadius 200 (circle)", m5())


def m6():
    """Inner above outer (separate, vertical)."""
    layers = perfect_polaroid()
    layers[1]["y"] = 50  # above outer
    return H(layers)
add("M6: inner above outer", m6())


def m7():
    """Both rectangles overlap fully (same dimensions, but offset)."""
    layers = perfect_polaroid()
    layers[1]["w"] = 300
    layers[1]["h"] = 340
    layers[1]["x"] = 410
    layers[1]["y"] = 410
    return H(layers)
add("M7: 2 rects same size, offset", m7())


# ── N. Structural tricks ─────────────────────────────────────────────
def n1():
    """Outer in frame, inner outside frame."""
    layers = perfect_polaroid()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, layers[1]], evt())
add("N1: outer in frame, inner outside", n1())


def n2():
    """Each rect in own frame."""
    layers = perfect_polaroid()
    frames = [make_frame([s], w=1280, h=832) for s in layers]
    return make_log(frames, evt())
add("N2: each rect in own frame", n2())


def n3():
    """Polaroid in component."""
    layers = perfect_polaroid()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: polaroid in component", n3())


def n4():
    """Polaroid deep in nested groups."""
    layers = perfect_polaroid()
    g3 = {"id": "g3", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    return make_log([g1], evt())
add("N4: polaroid 3-deep in groups", n4())


# ── O. Wrong types ───────────────────────────────────────────────────
def o1():
    """Outer is ellipse not rectangle."""
    layers = perfect_polaroid()
    layers[0] = L("ellipse", 400, 400, 300, 340, WHITE, rotation=5,
                   effects=[make_drop_shadow(y=8, blur=12)])
    return H(layers, evts=evt(rectangle=1, extras=[make_event("create_ellipse")]))
add("O1: outer ellipse", o1())


def o2():
    """Outer is polygon."""
    layers = perfect_polaroid()
    layers[0] = L("polygon", 400, 400, 300, 340, WHITE, sides=4, rotation=5,
                   effects=[make_drop_shadow()])
    return H(layers, evts=evt(rectangle=1, extras=[make_event("create_polygon")]))
add("O2: outer polygon", o2())


def o3():
    """Both are stars."""
    layers = []
    for _ in range(2):
        layers.append(make_layer("star", x=400, y=400, w=300, h=300,
                                  fill=WHITE, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rectangle=0))
add("O3: both stars", o3())


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

"""Round 3 edge cases — hunt for surviving false positives in task_11.

Each case is a wrong nested-triangles design that the verifier should give < 1.0.
Anything scoring ≥ 0.95 is a likely surviving false positive.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    DARK_GRAY, LIGHT_GRAY, BLACK,
)
from tasks import task_11_pressed_button as t
T = t.task

COLOR_A = (0.10, 0.50, 0.90)
COLOR_B = (0.95, 0.85, 0.20)


def evt(poly=3, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="polygon"))
    for _ in range(poly):
        sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def Tri(x, y, w, h, fill, sides=3, **extra):
    return make_layer("polygon", x=x, y=y, w=w, h=h, fill=fill, sides=sides, **extra)


def perfect_design(cx=640, cy=400):
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    return [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """All rotated 1.5° (under tolerance)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 1.5
    return H(layers)
add("K1: all rotated 1.5° (under tol)", k1())

def k2():
    """3 same-color triangles."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    layers = [Tri(cx-s/2, cy-s/2, s, s, COLOR_A) for s in sizes]
    return H(layers)
add("K2: 3 same color (1 distinct)", k2())

def k3():
    """All sides=4 (squares not triangles)."""
    layers = perfect_design()
    for l in layers:
        l["sides"] = 4
    return H(layers)
add("K3: all sides=4 (squares)", k3())

def k4():
    """1 has sides=5 (pentagon)."""
    layers = perfect_design()
    layers[1]["sides"] = 5
    return H(layers)
add("K4: 1 has sides=5", k4())

def k5():
    """Z-order ascending: smallest first."""
    layers = perfect_design()
    layers.reverse()
    return H(layers)
add("K5: z-order ascending (smallest 1st)", k5())

def k6():
    """Sizes 400/399/398 (within tol — no real nesting)."""
    cx, cy = 640, 400
    sizes = [400, 399, 398]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("K6: sizes within 2px (no nesting)", k6())

def k7():
    """All rotated 30° (looks weird)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 30
    return H(layers)
add("K7: all rotated 30°", k7())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Outer alpha=0."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: outer alpha=0", l1())

def l2():
    """All opacity=0."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("L2: all opacity=0", l2())

def l3():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L3: all visible=False", l3())

def l4():
    """Inner fill.visible=False."""
    layers = perfect_design()
    layers[2]["fills"][0]["visible"] = False
    return H(layers)
add("L4: inner fill.visible=False", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All same size at same position (pile)."""
    cx, cy = 640, 400
    layers = [Tri(cx-100, cy-100, 200, 200, [COLOR_A, COLOR_B][i % 2]) for i in range(3)]
    return H(layers)
add("M1: 3 same-size piled", m1())

def m2():
    """Outer = full frame."""
    layers = perfect_design()
    layers[0] = Tri(0, 0, 1280, 832, COLOR_A)
    return H(layers)
add("M2: outer = full frame", m2())

def m3():
    """All 100×50 stretched (not equilateral)."""
    cx, cy = 640, 400
    layers = [Tri(cx-50, cy-25, 100, 50, [COLOR_A, COLOR_B, COLOR_A][i]) for i in range(3)]
    return H(layers)
add("M3: all 100×50 stretched", m3())

def m4():
    """Outer 1500×1500 (>frame)."""
    layers = perfect_design()
    layers[0] = Tri(0, 0, 1500, 1500, COLOR_A)
    return H(layers)
add("M4: outer 1500x1500 (>frame)", m4())

def m5():
    """Concentric within tol but inner not nested."""
    cx, cy = 640, 400
    layers = [Tri(cx-200, cy-200, 400, 400, COLOR_A),
              Tri(cx-300, cy-150, 280, 280, COLOR_B),  # off-x
              Tri(cx-80,  cy-80,  160, 160, COLOR_A)]
    return H(layers)
add("M5: middle off-center", m5())

def m6():
    """Triangles overlap but not concentric."""
    layers = [Tri(100, 100, 400, 400, COLOR_A),
              Tri(300, 100, 280, 280, COLOR_B),
              Tri(500, 200, 160, 160, COLOR_A)]
    return H(layers)
add("M6: cascading not concentric", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Each in own frame."""
    layers = perfect_design()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N1: each in own frame", n1())

def n2():
    """In component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1280, "h": 832,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("N2: in component", n2())

def n3():
    """No frame."""
    return H(in_frame=False)
add("N3: no frame", n3())

def n4():
    """1 outside frame, 2 inside."""
    layers = perfect_design()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, layers[2]], evt())
add("N4: 2 in frame, 1 outside", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """3 ellipses."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("ellipse", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_ellipse")]*3))
add("O1: 3 ellipses (not polygons)", o1())

def o2():
    """3 rectangles."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("rectangle", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_rectangle")]*3))
add("O2: 3 rectangles", o2())

def o3():
    """3 stars."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("star", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c,
                         points=5, innerRatio=0.4)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_star")]*3))
add("O3: 3 stars (not polygons)", o3())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " ⚠ FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

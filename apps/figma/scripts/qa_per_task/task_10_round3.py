"""Round 3 edge cases — hunt for surviving false positives in task_10.

Each case is a wrong concentric-squares design that the verifier should give < 1.0.
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
from tasks import task_10_apple_avatar as t
T = t.task

COLOR_A = (0.10, 0.50, 0.90)
COLOR_B = (0.95, 0.85, 0.20)


def evt(rect=4, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="rectangle"))
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def R(x, y, w, h, fill, **extra):
    return make_layer("rectangle", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design(cx=640, cy=400):
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    return [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]


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
    """Z-order reversed: outer in front."""
    layers = perfect_design()
    layers.reverse()  # smallest first now means largest last (top)
    return H(layers)
add("K2: z-order reversed (outer-on-top)", k2())

def k3():
    """All cornerRadius=30 (rounded but still squarish)."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 30
    return H(layers)
add("K3: all cornerRadius=30", k3())

def k4():
    """All within 7px of center (within tol)."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = []
    for i, (s, c) in enumerate(zip(sizes, colors)):
        layers.append(R(cx-s/2 + 5, cy-s/2 + 7, s, s, c))
    return H(layers)
add("K4: all 7px off-center (within tol)", k4())

def k5():
    """4 same color (1 distinct color)."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    layers = [R(cx-s/2, cy-s/2, s, s, COLOR_A) for s in sizes]
    return H(layers)
add("K5: 4 squares all same color", k5())

def k6():
    """Sizes 400/399/398/397 (within tol)."""
    cx, cy = 640, 400
    sizes = [400, 399, 398, 397]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("K6: sizes within 3px (decreasing tinily)", k6())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Outer fill alpha=0."""
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
    layers[3]["fills"][0]["visible"] = False
    return H(layers)
add("L4: inner fill.visible=False", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All same size at same position (pile)."""
    cx, cy = 640, 400
    layers = [R(cx-100, cy-100, 200, 200, [COLOR_A, COLOR_B][i % 2]) for i in range(4)]
    return H(layers)
add("M1: 4 same-size piled (no nesting)", m1())

def m2():
    """Outer = full frame."""
    layers = perfect_design()
    layers[0] = R(0, 0, 1280, 832, COLOR_A)
    return H(layers)
add("M2: outer = full frame", m2())

def m3():
    """All near-square (4×3 ratio, within 2px tolerance)."""
    cx, cy = 640, 400
    sizes = [(400, 398), (300, 298), (200, 198), (100, 98)]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("M3: 2px tall-vs-wide (within tol)", m3())

def m4():
    """Sizes 400/200/100/50 (more aggressive nesting)."""
    cx, cy = 640, 400
    sizes = [400, 200, 100, 50]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("M4: aggressive 2x nesting", m4())

def m5():
    """4 squares all 100×100 (no nesting at all)."""
    cx, cy = 640, 400
    layers = [R(cx-50, cy-50, 100, 100, [COLOR_A, COLOR_B][i % 2]) for i in range(4)]
    return H(layers)
add("M5: all same 100×100 (no nesting)", m5())

def m6():
    """Concentric but inner is bigger than outer."""
    cx, cy = 640, 400
    sizes = [100, 200, 300, 400]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("M6: smallest in front (sizes ascending)", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Each in own frame (split)."""
    layers = perfect_design()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N1: each square in own frame", n1())

def n2():
    """Squares in component."""
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
    """1 outside, 3 inside frame."""
    layers = perfect_design()
    frame = make_frame(layers[:3], w=1280, h=832)
    return make_log([frame, layers[3]], evt())
add("N4: 3 in frame, 1 outside", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """4 ellipses (not rects)."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [make_layer("ellipse", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_ellipse")]*4))
add("O1: 4 ellipses (not rects)", o1())

def o2():
    """4 polygons."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [make_layer("polygon", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c, sides=4)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_polygon")]*4))
add("O2: 4 polygons (4-sided diamonds)", o2())

def o3():
    """3 rectangles + 1 ellipse."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = []
    for i, (s, c) in enumerate(zip(sizes, colors)):
        if i == 3:
            layers.append(make_layer("ellipse", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c))
        else:
            layers.append(R(cx-s/2, cy-s/2, s, s, c))
    return H(layers, evts=evt(rect=3,
                              extras=[make_event("create_ellipse")]))
add("O3: 3 rects + 1 ellipse", o3())


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

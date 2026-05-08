"""Round 3 edge cases — hunt for surviving false positives in task_07.

Each case is a wrong mountain design that the verifier should give < 1.0.
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
from tasks import task_07_mountain_range as t
T = t.task

DGRAY = (0.30, 0.30, 0.30)
LGRAY = (0.60, 0.60, 0.60)


def evt(pen=True, vectors=2, set_fill=2, extras=()):
    sem = [make_event("session_start")]
    if pen:
        sem.append(make_event("tool_change", before="select", after="pen"))
    for _ in range(vectors):
        sem.append(make_event("create_vector"))
    for _ in range(set_fill):
        sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def V(x, y, w, h, fill, **extra):
    return make_layer("vector", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    far = V(100, 100, 500, 250, DGRAY)
    near = V(350, 200, 500, 200, LGRAY)
    return [far, near]


def H(layers=None, frame_w=1000, frame_h=400, frame_fill=(0.95, 0.95, 0.95),
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
    """Both vectors rotated 1.5° (under tolerance)."""
    layers = perfect_design()
    layers[0]["rotation"] = 1.5
    layers[1]["rotation"] = 1.5
    return H(layers)
add("K1: both rotated 1.5° (under tol)", k1())

def k2():
    """Two vectors of identical color (DGRAY repeats; tol=0.04 different)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(350, 200, 500, 200, (0.34, 0.30, 0.30))]
    return H(layers)
add("K2: two near-DGRAY shades (4% diff)", k2())

def k3():
    """Bright distinct colors (red and blue) — not gray at all."""
    layers = [V(100, 100, 500, 250, RED),
              V(350, 200, 500, 200, NAVY)]
    return H(layers)
add("K3: red + blue (NOT gray shades)", k3())

def k4():
    """Saturated colors but distinct (purple + cyan)."""
    layers = [V(100, 100, 500, 250, PURPLE),
              V(350, 200, 500, 200, CYAN)]
    return H(layers)
add("K4: purple + cyan", k4())

def k5():
    """Both vectors at the same exact position with stacked overlap (1 visible)."""
    layers = [V(200, 100, 400, 200, DGRAY),
              V(200, 100, 400, 200, DGRAY)]
    return H(layers)
add("K5: identical position+color (looks like 1)", k5())

def k6():
    """Vectors with corner radius (visually rounded, not natural pen path)."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 100
    layers[1]["cornerRadius"] = 100
    return H(layers)
add("K6: vectors with cornerRadius=100", k6())

def k7():
    """Z-order: near drawn behind far (looks weird)."""
    far = V(100, 100, 500, 250, DGRAY)
    near = V(350, 200, 500, 200, LGRAY)
    # children order: far comes after near = far drawn last = far in front
    return H([near, far])
add("K7: 'far' on top of 'near' (z-swap)", k7())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """1st vector fully transparent at fill alpha."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.05
    return H(layers)
add("L1: 1st fill alpha=0.05", l1())

def l2():
    """Both vectors layer-opacity=0.05."""
    layers = perfect_design()
    layers[0]["opacity"] = 0.05
    layers[1]["opacity"] = 0.05
    return H(layers)
add("L2: layer opacity=0.05 (essentially invisible)", l2())

def l3():
    """1st has fill.visible=False."""
    layers = perfect_design()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L3: 1st fill visible=False", l3())

def l4():
    """1st vector layer.visible=False."""
    layers = perfect_design()
    layers[0]["visible"] = False
    return H(layers)
add("L4: 1st layer.visible=False", l4())

def l5():
    """Both fills are gradients but with gray colors."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 0.3, "g": 0.3, "b": 0.3, "a": 1}},
            {"position": 1, "color": {"r": 0.6, "g": 0.6, "b": 0.6, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("L5: both gradient fills (gray-to-gray)", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Both vectors are tiny dots (1×1) but distinct colors."""
    layers = [V(500, 200, 1, 1, DGRAY),
              V(501, 201, 1, 1, LGRAY)]
    return H(layers)
add("M1: both 1×1 dots", m1())

def m2():
    """1 vector spans entire frame, 2nd is a tiny dot."""
    layers = [V(0, 0, 1000, 400, DGRAY),
              V(495, 195, 5, 5, LGRAY)]
    return H(layers)
add("M2: 1 huge + 1 tiny dot (overlap)", m2())

def m3():
    """Both vectors as horizontal flat strips."""
    layers = [V(0, 200, 1000, 5, DGRAY),
              V(0, 205, 1000, 5, LGRAY)]
    return H(layers)
add("M3: two flat horizontal strips (5px tall)", m3())

def m4():
    """Vector partially off-frame (50% inside, 50% outside)."""
    layers = [V(700, 100, 500, 250, DGRAY),
              V(800, 200, 500, 200, LGRAY)]
    return H(layers)
add("M4: 50% off-frame", m4())

def m5():
    """Both vectors pile at single point."""
    layers = [V(500, 200, 100, 100, DGRAY),
              V(500, 200, 100, 100, LGRAY)]
    return H(layers)
add("M5: pile at one point", m5())

def m6():
    """Frame size 1010x410 (within 10px tolerance)."""
    return H(frame_w=1010, frame_h=410)
add("M6: frame just-within-tol (1010x410)", m6())

def m7():
    """Frame size 1015x420 (just over tolerance)."""
    return H(frame_w=1015, frame_h=420)
add("M7: frame just-over-tol (1015x420)", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Each vector in its own frame (split)."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=500, h=400)
    f2 = make_frame([house[1]], w=500, h=400)
    return make_log([f1, f2], evt())
add("N1: each vector in own frame (split)", n1())

def n2():
    """Vectors in component, not frame."""
    house = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1000, "h": 400,
                 "fills": [], "strokes": [], "effects": [], "children": house}
    return make_log([component], evt())
add("N2: vectors in component (not frame)", n2())

def n3():
    """No frame at all — vectors directly on page."""
    return H(in_frame=False)
add("N3: vectors on page (no frame)", n3())

def n4():
    """3rd extra vector hidden inside group."""
    house = perfect_design()
    extra = V(100, 100, 50, 50, RED)
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": [extra]}
    frame = make_frame([*house, group], w=1000, h=400)
    return make_log([frame], evt(vectors=3))
add("N4: hidden 3rd vector in group", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """2 rectangles instead of vectors."""
    layers = [make_layer("rectangle", x=100, y=100, w=500, h=250, fill=DGRAY),
              make_layer("rectangle", x=350, y=200, w=500, h=200, fill=LGRAY)]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_rectangle"),
                                      make_event("create_rectangle")]))
add("O1: 2 rectangles (no vectors)", o1())

def o2():
    """2 ellipses (smooth curves) instead of vectors."""
    layers = [make_layer("ellipse", x=100, y=100, w=500, h=250, fill=DGRAY),
              make_layer("ellipse", x=350, y=200, w=500, h=200, fill=LGRAY)]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_ellipse"),
                                      make_event("create_ellipse")]))
add("O2: 2 ellipses (no vectors)", o2())

def o3():
    """1 vector + 1 polygon (mixed types)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              make_layer("polygon", x=350, y=200, w=500, h=200, fill=LGRAY, sides=3)]
    return H(layers, evts=evt(vectors=1,
                              extras=[make_event("create_polygon")]))
add("O3: 1 vector + 1 triangle polygon", o3())


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

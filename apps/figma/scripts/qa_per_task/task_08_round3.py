"""Round 3 edge cases — hunt for surviving false positives in task_08.

Each case is a wrong wave design that the verifier should give < 1.0.
Anything scoring ≥ 0.95 is a likely surviving false positive.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    DARK_GRAY, LIGHT_GRAY, BLACK, COBALT, DEEP_BLUE,
)
from tasks import task_08_water_waves as t
T = t.task

BLUE1 = (0.20, 0.40, 0.85)
BLUE2 = (0.10, 0.30, 0.65)
BLUE3 = (0.40, 0.60, 0.95)


def evt(pen=True, vectors=2, set_stroke=2, extras=()):
    sem = [make_event("session_start")]
    if pen:
        sem.append(make_event("tool_change", before="select", after="pen"))
    for _ in range(vectors):
        sem.append(make_event("create_vector"))
    for _ in range(set_stroke):
        sem.append(make_event("set_stroke_color"))
    sem.extend(extras)
    return sem


def W(x, y, w, h, stroke_rgb=BLUE1, stroke_w=4, fill=None, **extra):
    strokes = [make_stroke(rgb=stroke_rgb, weight=stroke_w)] if stroke_rgb else []
    return make_layer("vector", x=x, y=y, w=w, h=h, fill=fill,
                      strokes=strokes, **extra)


def perfect_design():
    w1 = W(100, 100, 800, 120, BLUE1, 4)
    w2 = W(100, 150, 800, 120, BLUE2, 4)
    return [w1, w2]


def H(layers=None, frame_w=1000, frame_h=300, frame_fill=(0.95, 0.95, 0.95),
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
    """Both rotated 1.5° (under tolerance)."""
    layers = perfect_design()
    layers[0]["rotation"] = 1.5
    layers[1]["rotation"] = 1.5
    return H(layers)
add("K1: both rotated 1.5° (under tol)", k1())

def k2():
    """Two near-identical blues (4% diff)."""
    layers = [W(100, 100, 800, 120, BLUE1, 4),
              W(100, 150, 800, 120, (0.24, 0.40, 0.85), 4)]
    return H(layers)
add("K2: 4% blue diff (within tol=0.05)", k2())

def k3():
    """Stroke 5.4px (within 1.5 tolerance of 4)."""
    layers = [W(100, 100, 800, 120, BLUE1, 5.4),
              W(100, 150, 800, 120, BLUE2, 5.4)]
    return H(layers)
add("K3: stroke 5.4px (just-within 1.5 tol)", k3())

def k4():
    """Both vectors with cornerRadius (visually rounded)."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 50
    layers[1]["cornerRadius"] = 50
    return H(layers)
add("K4: vectors with cornerRadius=50", k4())

def k5():
    """Strokes are not blues at all (red shades)."""
    layers = [W(100, 100, 800, 120, (0.85, 0.20, 0.20), 4),
              W(100, 150, 800, 120, (0.65, 0.10, 0.10), 4)]
    return H(layers)
add("K5: red strokes (NOT blue)", k5())

def k6():
    """Greens instead of blues."""
    layers = [W(100, 100, 800, 120, (0.20, 0.85, 0.40), 4),
              W(100, 150, 800, 120, (0.10, 0.65, 0.30), 4)]
    return H(layers)
add("K6: green strokes (NOT blue)", k6())

def k7():
    """Stroke 0px (invisible) on both — but distinct paint colors."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["weight"] = 0
    return H(layers)
add("K7: stroke 0px (invisible)", k7())

def k8():
    """1 wave with stroke, 1 with no strokes at all."""
    layers = perfect_design()
    layers[1]["strokes"] = []
    return H(layers)
add("K8: 1 wave missing strokes", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Stroke alpha=0 on both."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("L1: stroke alpha=0", l1())

def l2():
    """Both opacity=0.05 (essentially invisible)."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.05
    return H(layers)
add("L2: layer opacity=0.05", l2())

def l3():
    """Stroke visible=False on both."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["visible"] = False
    return H(layers)
add("L3: stroke visible=False", l3())

def l4():
    """Both layer visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L4: layer visible=False", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Both vectors are tiny."""
    layers = [W(495, 145, 10, 10, BLUE1, 4),
              W(498, 148, 10, 10, BLUE2, 4)]
    return H(layers)
add("M1: 10×10 vectors", m1())

def m2():
    """Both = full frame."""
    layers = [W(0, 0, 1000, 300, BLUE1, 4),
              W(0, 0, 1000, 300, BLUE2, 4)]
    return H(layers)
add("M2: both = full frame", m2())

def m3():
    """Stroke weight 5.4 (just inside tol)."""
    layers = [W(100, 100, 800, 120, BLUE1, 5.4),
              W(100, 150, 800, 120, BLUE2, 5.4)]
    return H(layers)
add("M3: stroke weight 5.4 (within tol)", m3())

def m4():
    """Stroke weight 5.6 (just over tol)."""
    layers = [W(100, 100, 800, 120, BLUE1, 5.6),
              W(100, 150, 800, 120, BLUE2, 5.6)]
    return H(layers)
add("M4: stroke weight 5.6 (over tol)", m4())

def m5():
    """Frame 1010x310 (within 10px tol)."""
    return H(frame_w=1010, frame_h=310)
add("M5: frame just-within-tol", m5())

def m6():
    """Frame 1015x315 (just over tol)."""
    return H(frame_w=1015, frame_h=315)
add("M6: frame just-over-tol", m6())

def m7():
    """Both at exact same pile position."""
    layers = [W(500, 150, 50, 50, BLUE1, 4),
              W(500, 150, 50, 50, BLUE2, 4)]
    return H(layers)
add("M7: pile at same point", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Each in own frame (split)."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=500, h=300)
    f2 = make_frame([house[1]], w=500, h=300)
    return make_log([f1, f2], evt())
add("N1: each in own frame", n1())

def n2():
    """Inside component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1000, "h": 300,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("N2: in component (no frame)", n2())

def n3():
    """No frame — vectors on page."""
    return H(in_frame=False)
add("N3: no frame", n3())

def n4():
    """Hidden 3rd vector in group."""
    layers = perfect_design()
    extra = W(100, 100, 50, 50, RED, 4)
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": [extra]}
    frame = make_frame([*layers, group], w=1000, h=300)
    return make_log([frame], evt(vectors=3))
add("N4: hidden 3rd vector in group", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """2 rectangles with strokes (not vectors)."""
    layers = [make_layer("rectangle", x=100, y=100, w=800, h=120, fill=None,
                         strokes=[make_stroke(rgb=BLUE1, weight=4)]),
              make_layer("rectangle", x=100, y=150, w=800, h=120, fill=None,
                         strokes=[make_stroke(rgb=BLUE2, weight=4)])]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_rectangle")]*2))
add("O1: 2 rectangles (not vectors)", o1())

def o2():
    """2 ellipses with strokes."""
    layers = [make_layer("ellipse", x=100, y=100, w=800, h=120, fill=None,
                         strokes=[make_stroke(rgb=BLUE1, weight=4)]),
              make_layer("ellipse", x=100, y=150, w=800, h=120, fill=None,
                         strokes=[make_stroke(rgb=BLUE2, weight=4)])]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_ellipse")]*2))
add("O2: 2 ellipses (not vectors)", o2())

def o3():
    """2 lines."""
    layers = [make_layer("line", x=100, y=150, w=800, h=2, fill=None,
                         strokes=[make_stroke(rgb=BLUE1, weight=4)]),
              make_layer("line", x=100, y=200, w=800, h=2, fill=None,
                         strokes=[make_stroke(rgb=BLUE2, weight=4)])]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_line")]*2))
add("O3: 2 lines (not vectors)", o3())


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

"""Round 3 edge cases — hunt for surviving false positives in task_09.

Each case is a wrong palette grid that the verifier should give < 1.0.
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
from tasks import task_09_brand_palette as t
T = t.task

COLORS_12 = [
    (0.95, 0.20, 0.20), (1.00, 0.60, 0.20), (1.00, 0.85, 0.20),
    (0.40, 0.85, 0.30), (0.10, 0.50, 0.90), (0.50, 0.20, 0.70),
    (0.85, 0.30, 0.65), (0.65, 0.40, 0.20), (0.20, 0.20, 0.20),
    (0.85, 0.85, 0.85), (0.30, 0.70, 0.70), (0.95, 0.50, 0.30),
]


def evt(rect=12, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="rectangle"))
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def R(x, y, w, h, fill, **extra):
    return make_layer("rectangle", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design(square_size=80, gap=40, x0=100, y0=100):
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(x0 + col * (square_size + gap), y0 + row * (square_size + gap),
                        square_size, square_size, COLORS_12[i]))
    return layers


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
    """All 12 squares rotated 1.5° (under tolerance)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 1.5
    return H(layers)
add("K1: all rotated 1.5° (under tol)", k1())

def k2():
    """11 squares + 1 ellipse-shaped (looks like circle, but type=rectangle with rounded)."""
    layers = perfect_design()
    layers[5]["cornerRadius"] = 40  # 50% — looks circular
    return H(layers)
add("K2: 1 rect with cornerRadius=40 (circular look)", k2())

def k3():
    """All 12 with cornerRadius=20 (rounded but still squarish)."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 20
    return H(layers)
add("K3: all cornerRadius=20", k3())

def k4():
    """11 distinct + 1 within tol of another (effectively 11 distinct)."""
    layers = perfect_design()
    layers[11]["fills"][0]["color"] = {"r": 0.97, "g": 0.22, "b": 0.22, "a": 1.0}  # near-red[0]
    return H(layers)
add("K4: 11 distinct, 12th near-tol of 1st", k4())

def k5():
    """All 12 actually 79×80 (within 2px tolerance — squarish)."""
    layers = perfect_design()
    for l in layers:
        l["w"] = 79
    return H(layers)
add("K5: all 79×80 (within tol)", k5())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Half the squares fill alpha=0."""
    layers = perfect_design()
    for l in layers[:6]:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: half with alpha=0", l1())

def l2():
    """All squares opacity=0.05 (essentially invisible)."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.05
    return H(layers)
add("L2: opacity=0.05 (invisible)", l2())

def l3():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L3: all visible=False", l3())

def l4():
    """All fills are gradients (look like fills, but each different)."""
    layers = perfect_design()
    for i, l in enumerate(layers):
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": COLORS_12[i][0], "g": COLORS_12[i][1], "b": COLORS_12[i][2], "a": 1}},
            {"position": 1, "color": {"r": COLORS_12[i][0]*0.5, "g": COLORS_12[i][1]*0.5, "b": COLORS_12[i][2]*0.5, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("L4: all gradients (12 distinct)", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All squares pile at one position (overlap into 1 visible)."""
    layers = [R(500, 400, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("M1: 12 piled at one point", m1())

def m2():
    """Grid is 4×3 but x-spacing varies wildly within each row."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        x_offset = col * (60 + (i * 13) % 50)  # irregular spacing
        layers.append(R(100 + x_offset, 100 + row * 120, 80, 80, COLORS_12[i]))
    return H(layers)
add("M2: 4x3 with irregular x-spacing", m2())

def m3():
    """3x4 transposed grid."""
    layers = []
    for i in range(12):
        row = i // 3
        col = i % 3
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80, COLORS_12[i]))
    return H(layers)
add("M3: 3x4 transposed (not 4x3)", m3())

def m4():
    """Some squares have wildly different heights."""
    layers = perfect_design()
    layers[0]["h"] = 200
    layers[6]["h"] = 200
    return H(layers)
add("M4: 2 squares with h=200 (not square)", m4())

def m5():
    """Frame is rotated 1.5° (under tol)."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 1.5
    return make_log([frame], evt())
add("M5: frame rotated 1.5° (under tol)", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Each square in own frame (no shared frame)."""
    layers = perfect_design()
    frames = [make_frame([l], w=120, h=120) for l in layers]
    return make_log(frames, evt())
add("N1: each square in own frame", n1())

def n2():
    """Squares split 6+6 across 2 frames."""
    layers = perfect_design()
    f1 = make_frame(layers[:6], w=640, h=832)
    f2 = make_frame(layers[6:], w=640, h=832)
    return make_log([f1, f2], evt())
add("N2: 6+6 across 2 frames", n2())

def n3():
    """Squares in component (not frame)."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1280, "h": 832,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("N3: in component (not frame)", n3())

def n4():
    """No frame at all."""
    return H(in_frame=False)
add("N4: no frame", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """12 ellipses with grid."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(make_layer("ellipse", x=100 + col * 120, y=100 + row * 120,
                                 w=80, h=80, fill=COLORS_12[i]))
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_ellipse")]*12))
add("O1: 12 ellipses (not rects)", o1())

def o2():
    """12 polygons with grid."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(make_layer("polygon", x=100 + col * 120, y=100 + row * 120,
                                 w=80, h=80, fill=COLORS_12[i], sides=4))
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_polygon")]*12))
add("O2: 12 4-sided polygons", o2())

def o3():
    """Mixed: 6 rectangles + 6 ellipses."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        if i < 6:
            layers.append(R(100 + col * 120, 100 + row * 120, 80, 80, COLORS_12[i]))
        else:
            layers.append(make_layer("ellipse", x=100 + col * 120, y=100 + row * 120,
                                     w=80, h=80, fill=COLORS_12[i]))
    return H(layers, evts=evt(rect=6,
                              extras=[make_event("create_ellipse")]*6))
add("O3: 6 rects + 6 ellipses", o3())


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

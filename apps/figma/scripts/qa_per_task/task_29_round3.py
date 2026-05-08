"""Round 3 novel-deception edge cases for task 29 (Polka dot grid).

Spec: Off-white frame + 4 same-color circles in 2x2 grid (Tidy up).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, WHITE, BLACK,
)
from tasks import task_29_polka_dot_grid as t
T = t.task

OFF_WHITE = (0.97, 0.95, 0.92)
DOT_BLUE  = (0.2, 0.4, 0.85)


def evt(ellipse=4, set_fill=1, align=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(align):    sem.append(make_event("align_layers", axis="center_x"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    dots = []
    size = 80
    gap = 40
    for i in range(4):
        row = i // 2
        col = i % 2
        x = 540 + col * (size + gap)
        y = 320 + row * (size + gap)
        dots.append(L("ellipse", x, y, size, size, DOT_BLUE))
    return dots


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=OFF_WHITE,
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ───────────────────────────────────────────
def k1():
    """Dots in 2x2 grid but rotated 4° (under tol)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("K1: dots rotated 4° (under tol)", k1())


def k2():
    """Just outside circular tol (4 each off): 76x84."""
    layers = []
    size_w = 76; size_h = 84
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, size_w, size_h, DOT_BLUE))
    return H(layers)
add("K2: dots 76x84 (just over circular tol)", k2())


def k3():
    """4 dots arranged as 1x4 (one row), not 2x2."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 200 + i*120, 400, 80, 80, DOT_BLUE))
    return H(layers)
add("K3: 1x4 row, not 2x2", k3())


def k4():
    """4 dots as a quincunx (4 corners + 1 center... wait, just 4 corners but offset)."""
    layers = []
    pts = [(540, 320), (660, 380), (540, 440), (660, 380)]
    for x, y in pts:
        layers.append(L("ellipse", x, y, 80, 80, DOT_BLUE))
    return H(layers)
add("K4: dots in irregular L+center", k4())


def k5():
    """Dots all in 1 row (y aligned, x irregular)."""
    layers = [
        L("ellipse", 200, 400, 80, 80, DOT_BLUE),
        L("ellipse", 380, 400, 80, 80, DOT_BLUE),
        L("ellipse", 600, 400, 80, 80, DOT_BLUE),
        L("ellipse", 900, 400, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("K5: dots in single row", k5())


def k6():
    """Dots flipped scaleY=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleY"] = -1
    return H(layers)
add("K6: dots scaleY=-1", k6())


def k7():
    """Frame-sized dots (huge)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", col*640, row*416, 640, 416, DOT_BLUE))
    return H(layers)
add("K7: dots = quarter-frame each", k7())


def k8():
    """Dots progressively smaller (40, 60, 80, 100)."""
    layers = []
    sizes = [40, 60, 80, 100]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("K8: progressively sized dots", k8())


def k9():
    """3 dots in row, 1 dot far below (T shape)."""
    layers = [
        L("ellipse", 400, 300, 80, 80, DOT_BLUE),
        L("ellipse", 600, 300, 80, 80, DOT_BLUE),
        L("ellipse", 800, 300, 80, 80, DOT_BLUE),
        L("ellipse", 600, 600, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("K9: T-shape arrangement (3+1)", k9())


def k10():
    """Frame is white instead of off-white (just at tolerance edge)."""
    layers = perfect_design()
    return H(layers, frame_fill=(1.0, 1.0, 1.0))
add("K10: frame pure white (over tol from off-white)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Dots opacity=0.2."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.2
    return H(layers)
add("L1: dots opacity=0.2", l1())


def l2():
    """Dots fill alpha=0.1."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.1
    return H(layers)
add("L2: dots fill alpha=0.1", l2())


def l3():
    """Dots fill.opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L3: dots fill opacity=0.05", l3())


def l4():
    """Half dots visible, half hidden."""
    layers = perfect_design()
    layers[0]["visible"] = False
    layers[2]["visible"] = False
    return H(layers)
add("L4: 2 of 4 dots visible=False", l4())


def l5():
    """All dots fill.visible=False."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L5: dots fill visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """4 dots in concentric layout."""
    layers = []
    sizes = [200, 150, 100, 50]
    for size in sizes:
        layers.append(L("ellipse", 600 - size/2, 400 - size/2, size, size, DOT_BLUE))
    return H(layers)
add("M1: 4 concentric circles", m1())


def m2():
    """4 dots arranged as a + sign."""
    layers = [
        L("ellipse", 600, 200, 80, 80, DOT_BLUE),  # top
        L("ellipse", 400, 400, 80, 80, DOT_BLUE),  # left
        L("ellipse", 800, 400, 80, 80, DOT_BLUE),  # right
        L("ellipse", 600, 600, 80, 80, DOT_BLUE),  # bottom
    ]
    return H(layers)
add("M2: + (plus) arrangement", m2())


def m3():
    """4 dots arranged as a diamond."""
    layers = [
        L("ellipse", 600, 200, 80, 80, DOT_BLUE),
        L("ellipse", 400, 400, 80, 80, DOT_BLUE),
        L("ellipse", 800, 400, 80, 80, DOT_BLUE),
        L("ellipse", 600, 600, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("M3: diamond arrangement (4 corners)", m3())


def m4():
    """Tiny dots: 5x5 — just over LayerSizeAtLeast min=20."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 5, 5, DOT_BLUE))
    return H(layers)
add("M4: 5x5 dots (under min size 20)", m4())


def m5():
    """Dots overlapping each other (size > gap)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*60, 320 + row*60, 100, 100, DOT_BLUE))
    return H(layers)
add("M5: dots overlapping (size 100, gap 60)", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Dots split: 2 in frame_a, 2 in frame_b."""
    dots = perfect_design()
    f1 = make_frame(dots[:2], w=640, h=832, fill=OFF_WHITE)
    f2 = make_frame(dots[2:], w=640, h=832, fill=OFF_WHITE)
    return make_log([f1, f2], evt())
add("N1: 2 dots in frame_a, 2 in frame_b", n1())


def n2():
    """Dots in frame > group > dots."""
    dots = perfect_design()
    group = {"id": "grp_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": dots}
    frame = make_frame([group], w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame], evt())
add("N2: frame > group > dots (not direct)", n2())


def n3():
    """Dots in component within frame."""
    dots = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": dots}
    frame = make_frame([component], w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame], evt())
add("N3: frame > component > dots", n3())


def n4():
    """3 dots in frame, 1 dot at page level."""
    dots = perfect_design()
    frame = make_frame(dots[:3], w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame, dots[3]], evt())
add("N4: 3 dots in frame, 1 on page", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """4 polygons (hexagons) instead of ellipses."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("polygon", 540 + col*120, 320 + row*120, 80, 80, DOT_BLUE, sides=6))
    return H(layers, evts=evt(ellipse=0) + [make_event("create_polygon")]*4)
add("O1: 4 hexagons instead of ellipses", o1())


def o2():
    """4 squares."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("rectangle", 540 + col*120, 320 + row*120, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=0) + [make_event("create_rectangle")]*4)
add("O2: 4 squares", o2())


def o3():
    """4 stars."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(make_layer("star", x=540 + col*120, y=320 + row*120, w=80, h=80, fill=DOT_BLUE,
                                 points=5, innerRatio=0.4))
    return H(layers, evts=evt(ellipse=0) + [make_event("create_star")]*4)
add("O3: 4 stars instead of dots", o3())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)

for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

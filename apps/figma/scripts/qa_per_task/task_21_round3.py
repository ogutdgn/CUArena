"""Round 3 — novel deception cases for task 21 (button stack)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, MAGENTA, CYAN, BLACK, WHITE, RED, GREEN, PURPLE,
    PINK, ORANGE, GOLD, YELLOW,
)
from tasks import task_21_button_stack as t
T = t.task

RECT_W, RECT_H, GAP = 200, 60, 16
START_X, START_Y = 540, 200


def evt(rect=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_stack():
    colors = [(0.95,0.30,0.30), (0.95,0.60,0.20), (0.40,0.85,0.40)]
    return [L("rectangle", START_X, START_Y + i*(RECT_H+GAP), RECT_W, RECT_H, c)
            for i, c in enumerate(colors)]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ──────────────────────────────────────────
def k1():
    """Gap = 24 (just over tol of 8 from 16 = 8..24)."""
    layers = []
    cy = START_Y
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", START_X, cy, RECT_W, RECT_H, c))
        cy += RECT_H + 25  # over tol
    return H(layers)
add("K1: gap=25 (just over tol)", k1())

def k2():
    """Rects rotated 1° (under tol)."""
    layers = perfect_stack()
    for l in layers: l["rotation"] = 1.5
    return H(layers)
add("K2: all rects rotated 1.5° (under tol)", k2())

def k3():
    """Rects almost-but-not-quite same size (3px diff, just at tol)."""
    layers = perfect_stack()
    layers[1]["w"] = 203; layers[1]["h"] = 63
    return H(layers)
add("K3: middle rect 203×63 (just at tol)", k3())

def k4():
    """Two colors are within tol of each other (tolerance 0.05)."""
    colors = [(0.95, 0.30, 0.30), (0.95, 0.32, 0.32), (0.40, 0.85, 0.40)]
    layers = []
    for i, c in enumerate(colors):
        layers.append(L("rectangle", START_X, START_Y + i*(RECT_H+GAP), RECT_W, RECT_H, c))
    return H(layers)
add("K4: 2 reds within color tol", k4())

def k5():
    """Rects 2px x-misaligned (under tol of 5)."""
    layers = perfect_stack()
    for i, l in enumerate(layers):
        l["x"] += i*2
    return H(layers)
add("K5: rects drift 2px x (under tol)", k5())

def k6():
    """Rects with cornerRadius=29 (just under 0.5 frac threshold)."""
    layers = perfect_stack()
    for l in layers: l["cornerRadius"] = 29
    return H(layers)
add("K6: cornerRadius=29 (just under pill threshold)", k6())

def k7():
    """Rects gap = -10 (overlapping)."""
    layers = []
    cy = START_Y
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", START_X, cy, RECT_W, RECT_H, c))
        cy += RECT_H - 10  # overlap by 10
    return H(layers)
add("K7: gap=-10 (overlapping)", k7())


# ─── L. Visibility tricks ──────────────────────────────────────────
def l1():
    """All fills alpha=0."""
    layers = perfect_stack()
    for l in layers: l["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: all alpha=0", l1())

def l2():
    """Middle rect opacity=0."""
    layers = perfect_stack()
    layers[1]["opacity"] = 0
    return H(layers)
add("L2: middle rect opacity=0", l2())

def l3():
    """Top rect visible=False."""
    layers = perfect_stack()
    layers[0]["visible"] = False
    return H(layers)
add("L3: top rect visible=False", l3())

def l4():
    """All fills opacity=0.05."""
    layers = perfect_stack()
    for l in layers: l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L4: all opacity=0.05", l4())

def l5():
    """All same color as frame (camouflaged)."""
    layers = perfect_stack()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1.0}
    return H(layers)
add("L5: all rects = frame color", l5())


# ─── M. Geometry tricks ────────────────────────────────────────────
def m1():
    """All rects 1×1."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", START_X, START_Y + i*17, 1, 1, c))
    return H(layers)
add("M1: all 1×1 degenerate", m1())

def m2():
    """All rects = full frame."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", 0, 0, 1280, 832, c))
    return H(layers)
add("M2: all rects = full frame", m2())

def m3():
    """All identical bbox."""
    layers = []
    for c in [RED, GREEN, PURPLE]:
        layers.append(L("rectangle", 500, 400, 200, 60, c))
    return H(layers)
add("M3: all identical bbox", m3())

def m4():
    """Rects on diagonal (not vertical stack)."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", 100 + i*150, 100 + i*150, RECT_W, RECT_H, c))
    return H(layers)
add("M4: rects on diagonal", m4())

def m5():
    """Stack vertical but rects very tall (h=400)."""
    layers = []
    cy = START_Y
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", START_X, cy, RECT_W, 400, c))
        cy += 416
    return H(layers)
add("M5: rects 400 tall (over h)", m5())

def m6():
    """Stack horizontal (axis swap)."""
    layers = []
    cx = 100
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("rectangle", cx, START_Y, RECT_W, RECT_H, c))
        cx += RECT_W + GAP
    return H(layers)
add("M6: rects stacked horizontally", m6())


# ─── N. Structural tricks ──────────────────────────────────────────
def n1():
    """Each rect in own frame."""
    layers = perfect_stack()
    f1 = make_frame([layers[0]], w=400, h=400)
    f2 = make_frame([layers[1]], w=400, h=400, x=400)
    f3 = make_frame([layers[2]], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("N1: 3 rects in 3 separate frames", n1())

def n2():
    """1 rect in component, 2 in frame."""
    layers = perfect_stack()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children":[layers[0]]}
    frame = make_frame(layers[1:], w=1280, h=832)
    return make_log([component, frame], evt())
add("N2: 1 rect in component, 2 in frame", n2())

def n3():
    """All rects in 5-deep nested groups inside frame."""
    layers = perfect_stack()
    g = layers
    for _ in range(5):
        g = [{"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=1280, h=832)
    return make_log([frame], evt())
add("N3: rects 5-deep nested groups", n3())

def n4():
    """Rects in section (with navy fill)."""
    layers = perfect_stack()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[{"kind":"solid","color":{"r":0.05,"g":0.10,"b":0.45,"a":1},"opacity":1,"visible":True}],
               "children":layers}
    return make_log([section], evt())
add("N4: rects in section (not frame)", n4())


# ─── O. Wrong shape types ─────────────────────────────────────────
def o1():
    """Replace rectangles with polygons (4-sided)."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("polygon", START_X, START_Y + i*(RECT_H+GAP), RECT_W, RECT_H, c, sides=4))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]*3))
add("O1: 3 polygons instead of rectangles", o1())

def o2():
    """Replace with ellipses."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(L("ellipse", START_X, START_Y + i*(RECT_H+GAP), RECT_W, RECT_H, c))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_ellipse")]*3))
add("O2: 3 ellipses instead of rectangles", o2())

def o3():
    """Mix: 2 rects + 1 ellipse."""
    layers = perfect_stack()
    layers[1] = L("ellipse", START_X, START_Y + (RECT_H+GAP), RECT_W, RECT_H, GREEN)
    return H(layers, evts=evt(rect=2, extras=[make_event("create_ellipse"),
                                              make_event("tool_change", before="rectangle", after="ellipse")]))
add("O3: 2 rects + 1 ellipse (middle swap)", o3())

def o4():
    """3 stars instead of rectangles."""
    layers = []
    for i, c in enumerate([RED, GREEN, PURPLE]):
        layers.append(make_layer("star", x=START_X, y=START_Y + i*(RECT_H+GAP),
                                 w=RECT_W, h=RECT_H, fill=c, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_star")]*3))
add("O4: 3 stars instead of rectangles", o4())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        if flag: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95): {fp_count}/{len(CASES)}")

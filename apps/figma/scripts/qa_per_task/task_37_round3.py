"""Round 3 — novel deception cases for task 37 (sticky note).

Each case is a wrong design that the verifier should give < 0.95.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, YELLOW, ORANGE, NAVY, WHITE, RED,
)
from tasks import task_37_sticky_note as t
T = t.task

YELLOW_NOTE = (1.0, 0.92, 0.6)
DARK_YELLOW = (0.85, 0.78, 0.5)
GRAY_LINE = (0.5, 0.5, 0.5)


def evt(rect=1, vector=1, line=3, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("tool_change", before="pen", after="line")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(line):    sem.append(make_event("create_line"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_note():
    rect = L("rectangle", 300, 300, 200, 200, YELLOW_NOTE,
             rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    fold = L("vector", 460, 300, 40, 40, DARK_YELLOW)
    lines = [L("line", 320, 350+i*30, 160, 2, None,
               strokes=[make_stroke(rgb=GRAY_LINE, weight=1)]) for i in range(3)]
    return [rect, fold, *lines]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_note()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions (rotation tolerance, sub-pixel, edge tricks) ───────
def k1():
    """Rotation 3.9° - just under tolerance."""
    layers = perfect_note()
    layers[0]["rotation"] = 3.9
    return H(layers)
add("K1: rotation 3.9° (within tol)", k1())

def k2():
    """Rotation 2.1° - just under tolerance."""
    layers = perfect_note()
    layers[0]["rotation"] = 2.1
    return H(layers)
add("K2: rotation 2.1° (within tol)", k2())

def k3():
    """Color near YELLOW boundary (0.91, 0.92, 0.6) - tight tol."""
    layers = perfect_note()
    layers[0]["fills"][0]["color"] = {"r":0.91, "g":0.92, "b":0.6, "a":1.0}
    return H(layers)
add("K3: yellow at 0.09 chan diff (boundary)", k3())

def k4():
    """Drop shadow with alpha 0 (invisible shadow)."""
    layers = perfect_note()
    layers[0]["effects"][0]["color"]["a"] = 0.0
    return H(layers)
add("K4: shadow alpha=0 (invisible)", k4())

def k5():
    """Drop shadow visible=False."""
    layers = perfect_note()
    layers[0]["effects"][0]["visible"] = False
    return H(layers)
add("K5: shadow visible=False", k5())

def k6():
    """Lines drawn with horizontal vectors instead of line type."""
    layers = perfect_note()[:2]
    for i in range(3):
        layers.append(L("vector", 320, 350+i*30, 160, 2, GRAY_LINE))
    return H(layers, evts=evt(line=0, vector=4))
add("K6: lines as vectors (no line type)", k6())

def k7():
    """3 'lines' but with rotation = 3° (matching rect, not horizontal)."""
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["rotation"] = 3
    return H(layers)
add("K7: lines rotated 3° (with rect)", k7())

def k8():
    """Shadow on different layer (line, not rectangle)."""
    layers = perfect_note()
    layers[0]["effects"] = []
    layers[2]["effects"] = [make_drop_shadow(y=4, blur=8)]
    return H(layers)
add("K8: shadow on line, not rectangle", k8())

def k9():
    """Rectangle is square but rotated heavily 89°."""
    layers = perfect_note()
    layers[0]["rotation"] = 89
    return H(layers)
add("K9: rectangle rotated 89° (near-vertical)", k9())

def k10():
    """Three lines, but one is way longer than the others."""
    layers = perfect_note()
    layers[2]["w"] = 800
    return H(layers)
add("K10: 1 line much wider than others", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Fold (vector) is alpha=0."""
    layers = perfect_note()
    layers[1]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: fold alpha=0", l1())

def l2():
    """Fold visible=False."""
    layers = perfect_note()
    layers[1]["visible"] = False
    return H(layers)
add("L2: fold visible=False", l2())

def l3():
    """Lines all have stroke color matching frame (invisible against bg)."""
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["strokes"][0]["paint"]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1.0}
    return H(layers)
add("L3: lines stroke = bg color", l3())

def l4():
    """Lines stroke weight 0 (effectively invisible)."""
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["strokes"][0]["weight"] = 0
    return H(layers)
add("L4: lines stroke weight 0", l4())

def l5():
    """Rectangle hidden (visible=False)."""
    layers = perfect_note()
    layers[0]["visible"] = False
    return H(layers)
add("L5: rectangle visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Rectangle is a 200x199 (off by 1 from square - within tol)."""
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 200, 199, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("M1: rect 200x199 (1px off square - within tol)", m1())

def m2():
    """Rectangle 100x300 - clearly not square."""
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 100, 300, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("M2: rect 100x300 (not square)", m2())

def m3():
    """3 lines but only 1 is 'horizontal' shape (others are squarish)."""
    layers = perfect_note()
    layers[3] = L("line", 320, 380, 30, 30, None,
                  strokes=[make_stroke(rgb=GRAY_LINE, weight=1)])
    layers[4] = L("line", 320, 410, 30, 30, None,
                  strokes=[make_stroke(rgb=GRAY_LINE, weight=1)])
    return H(layers)
add("M3: lines short (not horizontal-ratio)", m3())

def m4():
    """Fold huge - same size as rectangle."""
    layers = perfect_note()
    layers[1] = L("vector", 300, 300, 200, 200, DARK_YELLOW)
    return H(layers)
add("M4: fold size = rect size", m4())

def m5():
    """Rectangle 4000x4000 (very large, but square)."""
    layers = perfect_note()
    layers[0] = L("rectangle", 0, 0, 4000, 4000, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("M5: rect 4000x4000 (covers everything)", m5())


# ─── N. Structural / hierarchy tricks ────────────────────────────────
def n1():
    """Lines in a separate frame from rectangle."""
    rect = L("rectangle", 300, 300, 200, 200, YELLOW_NOTE,
             rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    fold = L("vector", 460, 300, 40, 40, DARK_YELLOW)
    lines = [L("line", 320, 350+i*30, 160, 2, None,
               strokes=[make_stroke(rgb=GRAY_LINE, weight=1)]) for i in range(3)]
    f1 = make_frame([rect, fold], w=1280, h=832)
    f2 = make_frame(lines, w=1280, h=832)
    return make_log([f1, f2], evt())
add("N1: lines in separate frame", n1())

def n2():
    """Each shape in its own 1-shape frame."""
    layers = perfect_note()
    frames = [make_frame([s], w=1280, h=832) for s in layers]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Rectangle, fold, lines all in component (not frame)."""
    layers = perfect_note()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: shapes in component, not frame", n3())

def n4():
    """Rectangle behind fold (z-order: rect above fold)."""
    layers = perfect_note()
    rect = layers.pop(0)
    layers.append(rect)
    return H(layers)
add("N4: rectangle on top z-order (occluding fold)", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Rectangle is actually a star with 4 points."""
    layers = perfect_note()
    layers[0] = make_layer("star", x=300, y=300, w=200, h=200,
                            fill=YELLOW_NOTE, rotation=3, points=4, innerRatio=0.6,
                            effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers, evts=evt(rect=0))
add("O1: rectangle replaced by star", o1())

def o2():
    """Fold is a polygon (3 sides) instead of vector."""
    layers = perfect_note()
    layers[1] = make_layer("polygon", x=460, y=300, w=40, h=40, fill=DARK_YELLOW, sides=3)
    return H(layers, evts=evt(vector=0))
add("O2: fold is polygon, not vector", o2())

def o3():
    """Lines replaced by 3 thin rectangles."""
    layers = perfect_note()[:2]
    for i in range(3):
        layers.append(L("rectangle", 320, 350+i*30, 160, 2, GRAY_LINE))
    return H(layers, evts=evt(rect=4, line=0))
add("O3: lines as thin rectangles", o3())


# ─── Run ────────────────────────────────────────────────────────────
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

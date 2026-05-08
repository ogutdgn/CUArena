"""Round 3 — novel deception cases for task 39 (wifi icon)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, RED, GREEN, YELLOW, ORANGE, WHITE,
)
from tasks import task_39_wifi_icon as t
T = t.task

NAVY_COLOR = (0.05, 0.10, 0.45)


def evt(vector=2, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_wifi():
    arc1 = L("vector", 300, 200, 200, 100, None,
             strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    arc2 = L("vector", 250, 170, 300, 130, None,
             strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    dot = L("ellipse", 390, 380, 20, 20, NAVY_COLOR)
    return [arc1, arc2, dot]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_wifi()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Dot rotated 4° (within tolerance)."""
    layers = perfect_wifi()
    layers[2]["rotation"] = 4
    return H(layers)
add("K1: dot rotated 4° (within tol)", k1())

def k2():
    """Stroke 4.5px (within 6±2 tol)."""
    layers = perfect_wifi()
    for arc in layers[:2]: arc["strokes"][0]["weight"] = 4.5
    return H(layers)
add("K2: stroke 4.5px (within tol)", k2())

def k3():
    """Stroke 8.5px (within tol)."""
    layers = perfect_wifi()
    for arc in layers[:2]: arc["strokes"][0]["weight"] = 8.5
    return H(layers)
add("K3: stroke 8.5px (within tol)", k3())

def k4():
    """Dot color near-navy (boundary)."""
    layers = perfect_wifi()
    layers[2]["fills"][0]["color"] = {"r":0.25, "g":0.30, "b":0.65, "a":1}
    return H(layers)
add("K4: dot near-navy (boundary)", k4())

def k5():
    """Stroke alpha=0.04 (just under min)."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["paint"]["color"]["a"] = 0.04
    return H(layers)
add("K5: arcs stroke alpha 0.04 (under min)", k5())

def k6():
    """Stroke weight 0.4 (under min weight)."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["weight"] = 0.4
    return H(layers)
add("K6: stroke weight 0.4 (under min)", k6())

def k7():
    """Dot is a polygon with 100 sides (looks like circle)."""
    layers = perfect_wifi()[:2]
    layers.append(make_layer("polygon", x=390, y=380, w=20, h=20,
                              fill=NAVY_COLOR, sides=100))
    return H(layers, evts=evt(ellipse=0))
add("K7: dot is 100-sided polygon", k7())

def k8():
    """Vectors with no strokes set."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"] = []
    return H(layers)
add("K8: arcs strokes empty array", k8())

def k9():
    """Arcs same size and overlapping but distinct y."""
    layers = perfect_wifi()
    layers[1] = L("vector", 300, 220, 200, 100, None,
                  strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    return H(layers)
add("K9: arcs same size, slightly offset", k9())

def k10():
    """Dot has 0px size after 0 width set."""
    layers = perfect_wifi()
    layers[2]["w"] = 0
    layers[2]["h"] = 0
    return H(layers)
add("K10: dot 0x0 (zero area)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Dot fill color alpha 0."""
    layers = perfect_wifi()
    layers[2]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: dot fill alpha=0", l1())

def l2():
    """Dot fill visible=False."""
    layers = perfect_wifi()
    layers[2]["fills"][0]["visible"] = False
    return H(layers)
add("L2: dot fill visible=False", l2())

def l3():
    """Arcs visible=False."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["visible"] = False
    return H(layers)
add("L3: arcs visible=False", l3())

def l4():
    """Arcs strokes visible=False."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["visible"] = False
    return H(layers)
add("L4: arcs stroke visible=False", l4())

def l5():
    """Arcs alpha=0 stroke."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("L5: arcs stroke alpha=0", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Dot covers entire frame."""
    layers = perfect_wifi()
    layers[2] = L("ellipse", 0, 0, 1280, 832, NAVY_COLOR)
    return H(layers)
add("M1: dot = full frame", m1())

def m2():
    """Arcs and dot at same y."""
    layers = perfect_wifi()
    layers[2]["y"] = 250  # at arc level
    return H(layers)
add("M2: dot at arcs level", m2())

def m3():
    """Arc1 = arc2 (perfectly overlapping)."""
    layers = perfect_wifi()
    layers[1] = L("vector", 300, 200, 200, 100, None,
                  strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    return H(layers)
add("M3: arcs identical", m3())

def m4():
    """Dot bigger than arcs."""
    layers = perfect_wifi()
    layers[2] = L("ellipse", 200, 380, 500, 500, NAVY_COLOR)
    return H(layers)
add("M4: dot bigger than arcs", m4())

def m5():
    """Arcs as 0-stroke (no visible)."""
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["weight"] = 0
    return H(layers)
add("M5: arcs stroke weight 0", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Arcs in separate frame from dot."""
    layers = perfect_wifi()
    f1 = make_frame(layers[:2], w=1280, h=832)
    f2 = make_frame([layers[2]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("N1: arcs in separate frame from dot", n1())

def n2():
    """All shapes in component."""
    layers = perfect_wifi()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N2: all in component", n2())

def n3():
    """Each in own frame."""
    layers = perfect_wifi()
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("N3: each in own frame", n3())

def n4():
    """Arcs in group, dot outside group."""
    layers = perfect_wifi()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers[:2]}
    frame = make_frame([group, layers[2]], w=1280, h=832)
    return make_log([frame], evt())
add("N4: arcs in group, dot outside", n4())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Arcs are rectangles."""
    layers = [
        L("rectangle", 300, 200, 200, 100, None,
          strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]),
        L("rectangle", 250, 170, 300, 130, None,
          strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]),
        L("ellipse", 390, 380, 20, 20, NAVY_COLOR)
    ]
    return H(layers, evts=evt(vector=0))
add("O1: arcs are rectangles", o1())

def o2():
    """Dot is a star."""
    layers = perfect_wifi()[:2]
    layers.append(make_layer("star", x=390, y=380, w=20, h=20,
                              fill=NAVY_COLOR, points=5, innerRatio=0.4))
    return H(layers, evts=evt(ellipse=0))
add("O2: dot is star", o2())

def o3():
    """Arcs and dot all same type (rectangle)."""
    layers = [
        L("rectangle", 300, 200, 200, 100, NAVY_COLOR),
        L("rectangle", 250, 170, 300, 130, NAVY_COLOR),
        L("rectangle", 390, 380, 20, 20, NAVY_COLOR)
    ]
    return H(layers, evts=evt(vector=0, ellipse=0))
add("O3: all 3 are rectangles", o3())


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

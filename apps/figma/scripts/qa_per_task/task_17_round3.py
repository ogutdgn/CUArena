"""Round 3 — novel deception cases for task 17 (hourglass)."""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                # scripts/
sys.path.insert(0, str(HERE.parent.parent))         # apps/figma/

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task,
    PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    BLACK, LIGHT_GRAY, DARK_GRAY, WARM_ORANGE, CREAM, DEEP_BLUE, TEAL,
    COBALT, MAGENTA, SAND, PALE_YELLOW, DEEP_PURPLE,
)
import importlib.util
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_17" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
CX = 500
TRI_FILL = (0.5, 0.4, 0.7)
CAP_FILL = (0.6, 0.5, 0.7)


def evt(rect=2, polygon=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("tool_change", before="polygon", after="rectangle")]
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_hourglass():
    p_top = L("polygon", CX-50, 240, 100, 100, TRI_FILL, sides=3, rotation=180)
    p_bot = L("polygon", CX-50, 340, 100, 100, TRI_FILL, sides=3, rotation=0)
    cap_top = L("rectangle", CX-100, 220, 200, 16, CAP_FILL)
    cap_bot = L("rectangle", CX-100, 444, 200, 16, CAP_FILL)
    return [p_top, p_bot, cap_top, cap_bot]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_hourglass()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ──────────────────────────────────────────
def k1():
    """Top tri rotation 178° (just under 3° tol)."""
    layers = perfect_hourglass()
    layers[0]["rotation"] = 178
    return H(layers)
add("K1: top tri rotation 178° (under tol)", k1())

def k2():
    """Both tris at rotation 178/2 — close to 180/0."""
    layers = perfect_hourglass()
    layers[0]["rotation"] = 178
    layers[1]["rotation"] = 2
    return H(layers)
add("K2: tris at 178/2° (under tol)", k2())

def k3():
    """Caps rotated 1° (just under 2° tol)."""
    layers = perfect_hourglass()
    layers[2]["rotation"] = 1
    layers[3]["rotation"] = 1
    return H(layers)
add("K3: caps rotated 1° (under tol)", k3())

def k4():
    """Tris meeting point-to-base (one is rotated 180 but other is rotated 60°)."""
    layers = perfect_hourglass()
    layers[1]["rotation"] = 60
    return H(layers)
add("K4: bottom tri rotated 60°", k4())

def k5():
    """Tri positions swapped (top tri = points up at top)."""
    layers = perfect_hourglass()
    layers[0]["rotation"] = 0     # pointing up at top (wrong)
    layers[1]["rotation"] = 180   # pointing down at bottom (wrong)
    return H(layers)
add("K5: tris point AWAY from each other (X shape)", k5())

def k6():
    """Caps with cornerRadius=200 (basically pills/circles)."""
    layers = perfect_hourglass()
    layers[2]["cornerRadius"] = 200
    layers[3]["cornerRadius"] = 200
    return H(layers)
add("K6: caps with extreme cornerRadius (pill-shaped)", k6())


# ─── L. Visibility tricks ──────────────────────────────────────────
def l1():
    """Caps fill alpha=0 (invisible)."""
    layers = perfect_hourglass()
    layers[2]["fills"][0]["color"]["a"] = 0.0
    layers[3]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: caps fill alpha=0", l1())

def l2():
    """Tris fill visible=False."""
    layers = perfect_hourglass()
    layers[0]["fills"][0]["visible"] = False
    layers[1]["fills"][0]["visible"] = False
    return H(layers)
add("L2: tris fill visible=False", l2())

def l3():
    """Tris layer opacity=0.1."""
    layers = perfect_hourglass()
    layers[0]["opacity"] = 0.1
    layers[1]["opacity"] = 0.1
    return H(layers)
add("L3: tris layer opacity=0.1", l3())

def l4():
    """Tri visible=False (layer level)."""
    layers = perfect_hourglass()
    layers[0]["visible"] = False
    return H(layers)
add("L4: top tri visible=False", l4())

def l5():
    """Tris fill opacity=0.05."""
    layers = perfect_hourglass()
    for i in (0, 1):
        layers[i]["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L5: tris fill opacity=0.05", l5())


# ─── M. Geometry tricks ────────────────────────────────────────────
def m1():
    """All shapes piled at same exact spot."""
    layers = []
    for s in perfect_hourglass():
        s["x"] = CX-50
        s["y"] = 300
        s["w"] = s["h"] = 100
        layers.append(s)
    return H(layers)
add("M1: all shapes piled at one point", m1())

def m2():
    """Tris are 1-pixel polygons (degenerate)."""
    layers = perfect_hourglass()
    for i in (0, 1):
        layers[i]["w"] = 1
        layers[i]["h"] = 1
    return H(layers)
add("M2: tris 1×1 degenerate", m2())

def m3():
    """Caps positioned far above/below frame (off-frame, far)."""
    layers = perfect_hourglass()
    layers[2]["y"] = -500
    layers[3]["y"] = 1500
    return H(layers)
add("M3: caps off-frame (top -500, bottom 1500)", m3())

def m4():
    """Tris half-out of frame (negative y)."""
    layers = perfect_hourglass()
    layers[0]["y"] = -50
    layers[1]["y"] = 50
    layers[2]["y"] = -100
    layers[3]["y"] = 200
    return H(layers)
add("M4: hourglass partially off-frame", m4())

def m5():
    """Caps 2000 wide (full width of huge frame)."""
    layers = perfect_hourglass()
    layers[2]["w"] = 2000
    layers[3]["w"] = 2000
    layers[2]["x"] = -360
    layers[3]["x"] = -360
    return H(layers)
add("M5: caps 2000 wide (overflow)", m5())

def m6():
    """Tris very wide (500 wide) and short (10 tall)."""
    layers = perfect_hourglass()
    layers[0]["w"] = 500
    layers[0]["h"] = 10
    layers[1]["w"] = 500
    layers[1]["h"] = 10
    return H(layers)
add("M6: tris squashed flat 500×10", m6())

def m7():
    """Cap rotated 90° (vertical cap line)."""
    layers = perfect_hourglass()
    layers[2]["rotation"] = 90
    return H(layers)
add("M7: top cap rotated 90° (vertical)", m7())


# ─── N. Structural tricks ──────────────────────────────────────────
def n1():
    """Tris in component, caps in frame."""
    tris = perfect_hourglass()[:2]
    caps = perfect_hourglass()[2:]
    component = {"id": "comp1", "type": "component", "x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children": tris}
    frame = make_frame(caps, w=1280, h=832)
    return make_log([component, frame], evt())
add("N1: tris in component, caps in frame", n1())

def n2():
    """Each shape in separate top-level frame."""
    layers = perfect_hourglass()
    frames = [make_frame([s], w=400, h=400) for s in layers]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Frame holds tris in inner group, caps as frame's siblings on page."""
    tris = perfect_hourglass()[:2]
    caps = perfect_hourglass()[2:]
    group = {"id":"group1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children":tris}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame, *caps], evt())
add("N3: tris in group inside frame, caps on page", n3())

def n4():
    """All shapes nested in a 5-deep group inside frame."""
    layers = perfect_hourglass()
    g5 = layers
    for _ in range(5):
        g5 = [{"id":f"g{_}","type":"group","x":0,"y":0,"w":0,"h":0,
               "fills":[],"strokes":[],"effects":[],"children":g5}]
    frame = make_frame(g5, w=1280, h=832)
    return make_log([frame], evt())
add("N4: hourglass nested in 5-deep groups", n4())


# ─── O. Wrong shape types ─────────────────────────────────────────
def o1():
    """Triangles replaced with stars (5-pointed)."""
    layers = perfect_hourglass()
    layers[0] = make_layer("star", x=CX-50, y=240, w=100, h=100, fill=TRI_FILL,
                           points=5, innerRatio=0.4, rotation=180)
    layers[1] = make_layer("star", x=CX-50, y=340, w=100, h=100, fill=TRI_FILL,
                           points=5, innerRatio=0.4, rotation=0)
    return H(layers, evts=evt(polygon=0))
add("O1: triangles replaced with stars", o1())

def o2():
    """Caps replaced with ellipses (oval caps)."""
    layers = perfect_hourglass()
    layers[2] = make_layer("ellipse", x=CX-100, y=220, w=200, h=16, fill=CAP_FILL)
    layers[3] = make_layer("ellipse", x=CX-100, y=444, w=200, h=16, fill=CAP_FILL)
    return H(layers, evts=evt(rect=0))
add("O2: caps replaced with ellipses", o2())

def o3():
    """Polygons with 5 sides (pentagons) instead of triangles."""
    layers = perfect_hourglass()
    layers[0]["sides"] = 5
    layers[1]["sides"] = 5
    return H(layers)
add("O3: polygons have 5 sides (pentagons)", o3())

def o4():
    """Triangles replaced with vectors (pen-drawn)."""
    layers = perfect_hourglass()
    layers[0] = make_layer("vector", x=CX-50, y=240, w=100, h=100, fill=TRI_FILL,
                           rotation=180)
    layers[1] = make_layer("vector", x=CX-50, y=340, w=100, h=100, fill=TRI_FILL,
                           rotation=0)
    return H(layers, evts=evt(polygon=0))
add("O4: triangles replaced with vectors", o4())


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
        if flag:
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95): {fp_count}/{len(CASES)}")

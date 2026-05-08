"""Round 3 — novel deception edge cases for task 43 (compass rose)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_43" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
DARK_GRAY = (0.30, 0.30, 0.30)


def evt(ellipse=2, polygon=4, set_fill=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon")]
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_compass():
    cx, cy = 640, 416
    sand = L("ellipse", cx-150, cy-150, 300, 300, SAND)
    n = L("polygon", cx-15, cy-100-50, 30, 100, RED, sides=3, rotation=0)
    e = L("polygon", cx+100-15, cy-50, 30, 100, GRAY, sides=3, rotation=90)
    s = L("polygon", cx-15, cy+100-50, 30, 100, GRAY, sides=3, rotation=180)
    w_ = L("polygon", cx-100-15, cy-50, 30, 100, DARK_GRAY, sides=3, rotation=270)
    center = L("ellipse", cx-15, cy-15, 30, 30, GOLD)
    return [sand, n, e, s, w_, center]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_compass()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """4 triangles all rotation=0 (no cardinals)."""
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["rotation"] = 0
    return H(layers)
add("K1: all triangles rotation=0", k1())

def k2():
    """4 triangles at 0°, 89°, 91°, 180° — close to cardinals but not 90° apart."""
    layers = perfect_compass()
    layers[1]["rotation"] = 0
    layers[2]["rotation"] = 89
    layers[3]["rotation"] = 91
    layers[4]["rotation"] = 180
    return H(layers)
add("K2: triangles 0/89/91/180", k2())

def k3():
    """All triangles same color (gray), no red N."""
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}
    return H(layers)
add("K3: all triangles gray (no red N)", k3())

def k4():
    """Sand circle scaleY=-1."""
    layers = perfect_compass()
    layers[0]["scaleY"] = -1
    return H(layers)
add("K4: sand mirrored vertically", k4())

def k5():
    """Center cornerRadius=15 (already round, doesn't matter)."""
    layers = perfect_compass()
    layers[5]["cornerRadius"] = 15
    return H(layers)
add("K5: center cornerRadius=15", k5())

def k6():
    """Triangles 91° apart (within tol but slightly off)."""
    layers = perfect_compass()
    layers[1]["rotation"] = 0
    layers[2]["rotation"] = 91
    layers[3]["rotation"] = 182
    layers[4]["rotation"] = 273
    return H(layers)
add("K6: triangles 91° apart (within tol)", k6())

def k7():
    """N triangle has 5 sides (pentagon, not triangle)."""
    layers = perfect_compass()
    layers[1]["sides"] = 5
    return H(layers)
add("K7: N triangle has 5 sides (pentagon)", k7())

def k8():
    """Center has cornerRadius=2 (still ellipse so doesn't matter)."""
    layers = perfect_compass()
    layers[5]["cornerRadius"] = 2
    return H(layers)
add("K8: center cornerRadius=2", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Sand circle alpha=0."""
    layers = perfect_compass()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: sand alpha=0", l1())

def l2():
    """Sand visible=False."""
    layers = perfect_compass()
    layers[0]["visible"] = False
    return H(layers)
add("L2: sand visible=False", l2())

def l3():
    """Center layer opacity=0."""
    layers = perfect_compass()
    layers[5]["opacity"] = 0
    return H(layers)
add("L3: center opacity=0", l3())

def l4():
    """All triangles fillOpacity=0.05."""
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L4: all triangles fillOpacity=0.05", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Center bigger than sand (role swap)."""
    layers = perfect_compass()
    layers[5] = L("ellipse", 100, 100, 500, 500, GOLD)
    return H(layers)
add("M1: center bigger than sand", m1())

def m2():
    """Sand same size as center (no contrast)."""
    layers = perfect_compass()
    layers[0] = L("ellipse", 600, 380, 30, 30, SAND)
    return H(layers)
add("M2: sand same size as center", m2())

def m3():
    """Triangles all at sand center (overlapping pile)."""
    layers = perfect_compass()
    cx, cy = 640, 416
    for i in range(1, 5):
        layers[i]["x"] = cx - 15
        layers[i]["y"] = cy - 50
    return H(layers)
add("M3: triangles piled at center", m3())

def m4():
    """Triangles at 4 corners (not radial)."""
    layers = perfect_compass()
    layers[1] = L("polygon", 100, 100, 30, 100, RED, sides=3, rotation=0)
    layers[2] = L("polygon", 1100, 100, 30, 100, GRAY, sides=3, rotation=90)
    layers[3] = L("polygon", 100, 700, 30, 100, GRAY, sides=3, rotation=180)
    layers[4] = L("polygon", 1100, 700, 30, 100, DARK_GRAY, sides=3, rotation=270)
    return H(layers)
add("M4: triangles at 4 corners", m4())

def m5():
    """Sand = full frame."""
    layers = perfect_compass()
    layers[0] = L("ellipse", 0, 0, 1280, 832, SAND)
    return H(layers)
add("M5: sand = full frame", m5())

def m6():
    """Frame 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("M6: frame 2000x2000", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Sand in 1 frame, triangles + center in another."""
    compass = perfect_compass()
    f1 = make_frame([compass[0]], w=1280, h=832)
    f2 = make_frame(compass[1:], w=600, h=600)
    return make_log([f1, f2], evt())
add("N1: sand and rest in different frames", n1())

def n2():
    """Each shape in its own frame."""
    compass = perfect_compass()
    frames = [make_frame([s], w=1280, h=832) for s in compass]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Compass inside a component (no frame)."""
    compass = perfect_compass()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": compass}
    return make_log([component], evt())
add("N3: compass inside component", n3())

def n4():
    """Compass on page 2."""
    compass = perfect_compass()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(compass, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("N4: compass on page 2", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """4 stars instead of 4 triangles."""
    layers = perfect_compass()[:1] + [perfect_compass()[5]]
    cx, cy = 640, 416
    for i, (x, y, rot) in enumerate([(cx-15, cy-130, 0), (cx+30, cy-15, 90),
                                       (cx-15, cy+30, 180), (cx-130, cy-15, 270)]):
        layers.insert(1 + i, make_layer("star", x=x, y=y, w=30, h=100,
                                         fill=RED if i == 0 else (GRAY if i < 3 else DARK_GRAY),
                                         points=3, rotation=rot))
    return H(layers, evts=evt(polygon=0, extras=[make_event("create_star")] * 4))
add("O1: 4 stars instead of 4 triangles", o1())

def o2():
    """Sand + center are rectangles, not ellipses."""
    layers = perfect_compass()
    layers[0] = L("rectangle", 490, 266, 300, 300, SAND)
    layers[5] = L("rectangle", 625, 401, 30, 30, GOLD)
    return H(layers, evts=evt(ellipse=0))
add("O2: sand + center are rectangles", o2())

def o3():
    """Compass rendered as text 'N E S W'."""
    layers = [L("ellipse", 490, 266, 300, 300, SAND)]
    text = make_layer("text", x=600, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "N E S W"
    layers.append(text)
    layers.append(L("ellipse", 625, 401, 30, 30, GOLD))
    return H(layers, evts=evt(polygon=0))
add("O3: compass as text", o3())


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
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

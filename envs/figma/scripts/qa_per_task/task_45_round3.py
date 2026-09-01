"""Round 3 — novel deception edge cases for task 45 (geometric emblem)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_45" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
YELLOW = (1.0, 0.85, 0.20)
NEAR_BLUE = (0.13, 0.22, 0.55)
NEAR_YELLOW = (0.95, 0.82, 0.25)


def evt(star=1, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("tool_change", before="star", after="ellipse")]
    for _ in range(star):    sem.append(make_event("create_star"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_emblem():
    star = make_layer("star", x=440, y=216, w=400, h=400, fill=DEEP_BLUE,
                      points=8, innerRatio=0.6)
    circle = L("ellipse", 540, 316, 200, 200, YELLOW)
    return [star, circle]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_emblem()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Star rotated 4° (under tol=2)."""
    layers = perfect_emblem()
    layers[0]["rotation"] = 4
    return H(layers)
add("K1: star rotation 4°", k1())

def k2():
    """Star with 7 points (off by 1)."""
    layers = perfect_emblem()
    layers[0]["points"] = 7
    return H(layers)
add("K2: star 7 points", k2())

def k3():
    """Star with 9 points (off by 1)."""
    layers = perfect_emblem()
    layers[0]["points"] = 9
    return H(layers)
add("K3: star 9 points", k3())

def k4():
    """Star color near-blue (within tol)."""
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"] = {"r": NEAR_BLUE[0], "g": NEAR_BLUE[1], "b": NEAR_BLUE[2], "a": 1.0}
    return H(layers)
add("K4: star near-blue (within tol)", k4())

def k5():
    """Circle near-yellow."""
    layers = perfect_emblem()
    layers[1]["fills"][0]["color"] = {"r": NEAR_YELLOW[0], "g": NEAR_YELLOW[1], "b": NEAR_YELLOW[2], "a": 1.0}
    return H(layers)
add("K5: circle near-yellow", k5())

def k6():
    """Star+circle reversed colors (star yellow, circle blue)."""
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"] = {"r": 1.0, "g": 0.85, "b": 0.20, "a": 1.0}
    layers[1]["fills"][0]["color"] = {"r": 0.10, "g": 0.20, "b": 0.60, "a": 1.0}
    return H(layers)
add("K6: star yellow, circle blue (swap)", k6())

def k7():
    """Star and circle slightly off-center (10px)."""
    layers = perfect_emblem()
    layers[1]["x"] += 10
    layers[1]["y"] += 10
    return H(layers)
add("K7: circle 10px off-center", k7())

def k8():
    """Circle drawn before star (under star in z-order)."""
    layers = perfect_emblem()
    return H([layers[1], layers[0]])
add("K8: circle below star (z-order swap)", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Star alpha=0."""
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: star alpha=0", l1())

def l2():
    """Circle visible=False."""
    layers = perfect_emblem()
    layers[1]["visible"] = False
    return H(layers)
add("L2: circle visible=False", l2())

def l3():
    """Star opacity=0."""
    layers = perfect_emblem()
    layers[0]["opacity"] = 0
    return H(layers)
add("L3: star opacity=0", l3())

def l4():
    """Circle fill visible=False."""
    layers = perfect_emblem()
    layers[1]["fills"][0]["visible"] = False
    return H(layers)
add("L4: circle fill visible=False", l4())

def l5():
    """Both fills opacity=0.05."""
    layers = perfect_emblem()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L5: both fillOpacity=0.05", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Circle bigger than star (role swap)."""
    layers = perfect_emblem()
    layers[1] = L("ellipse", 100, 100, 600, 600, YELLOW)
    return H(layers)
add("M1: circle bigger than star", m1())

def m2():
    """Star = full frame."""
    layers = perfect_emblem()
    layers[0]["x"] = 0
    layers[0]["y"] = 0
    layers[0]["w"] = 1280
    layers[0]["h"] = 832
    return H(layers)
add("M2: star = full frame", m2())

def m3():
    """Circle outside star."""
    layers = perfect_emblem()
    layers[1] = L("ellipse", 1000, 700, 80, 80, YELLOW)
    return H(layers)
add("M3: circle outside star", m3())

def m4():
    """Star and circle at same position+size (no contrast)."""
    layers = perfect_emblem()
    layers[1] = L("ellipse", 440, 216, 400, 400, YELLOW)
    return H(layers)
add("M4: circle = star size", m4())

def m5():
    """Frame 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("M5: frame 2000x2000", m5())

def m6():
    """Star tiny, circle stays."""
    layers = perfect_emblem()
    layers[0]["w"] = 30
    layers[0]["h"] = 30
    return H(layers)
add("M6: star 30×30 (tiny)", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Star in 1 frame, circle in another."""
    emblem = perfect_emblem()
    f1 = make_frame([emblem[0]], w=1280, h=832)
    f2 = make_frame([emblem[1]], w=400, h=400)
    return make_log([f1, f2], evt())
add("N1: star/circle in different frames", n1())

def n2():
    """Each shape in own frame."""
    emblem = perfect_emblem()
    frames = [make_frame([s], w=1280, h=832) for s in emblem]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Inside component."""
    emblem = perfect_emblem()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": emblem}
    return make_log([component], evt())
add("N3: in component", n3())

def n4():
    """Emblem on page 2."""
    emblem = perfect_emblem()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(emblem, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("N4: emblem on page 2", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Star is a polygon."""
    layers = perfect_emblem()
    layers[0] = make_layer("polygon", x=440, y=216, w=400, h=400, fill=DEEP_BLUE, sides=8)
    return H(layers, evts=evt(star=0, extras=[make_event("create_polygon")]))
add("O1: star is a polygon", o1())

def o2():
    """Circle is a rectangle."""
    layers = perfect_emblem()
    layers[1] = L("rectangle", 540, 316, 200, 200, YELLOW)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]))
add("O2: circle is a rectangle", o2())

def o3():
    """Star with 3 points (looks like triangle)."""
    layers = perfect_emblem()
    layers[0]["points"] = 3
    return H(layers)
add("O3: star with 3 points", o3())

def o4():
    """Both star and circle are text."""
    layers = [make_layer("text", x=440, y=216, w=400, h=400, fill=DEEP_BLUE),
              make_layer("text", x=540, y=316, w=200, h=200, fill=YELLOW)]
    layers[0]["content"] = "STAR"
    layers[1]["content"] = "CIRCLE"
    return H(layers, evts=[make_event("session_start"), make_event("create_text")])
add("O4: shapes are text", o4())


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

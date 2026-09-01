"""Round 3 — novel deception edge cases for task 42 (bell icon).

Each case is a wrong design that should score < 0.95. Anything ≥ 0.95 is a
likely surviving false positive.
"""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_42" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
RED_BADGE = (0.95, 0.20, 0.20)
DARK_GOLD1 = (0.95, 0.78, 0.10)
DARK_GOLD2 = (0.99, 0.82, 0.15)


def evt(vector=1, ellipse=2, set_fill=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bell():
    bell = L("vector", 540, 280, 200, 240, GOLD)
    clapper = L("ellipse", 620, 520, 40, 40, GOLD)
    badge = L("ellipse", 720, 280, 24, 24, RED_BADGE,
              strokes=[make_stroke(rgb=WHITE, weight=2)])
    return [bell, clapper, badge]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bell()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Bell rotated 4° (just under 5° tolerance)."""
    layers = perfect_bell()
    layers[0]["rotation"] = 4
    return H(layers)
add("K1: bell rotated 4° (under tol)", k1())

def k2():
    """Clapper rotated 4° (under tol). Doesn't matter visually but FAILS strict tol=2."""
    layers = perfect_bell()
    layers[1]["rotation"] = 4
    return H(layers)
add("K2: clapper rotated 4° (over tol=2)", k2())

def k3():
    """Bell stroke=3 (off-tol from 2)."""
    layers = perfect_bell()
    layers[2]["strokes"] = [make_stroke(rgb=WHITE, weight=3.5)]
    return H(layers)
add("K3: badge stroke 3.5px (over tol=1)", k3())

def k4():
    """Bell uses near-gold variant (within color tol)."""
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 200, 240, DARK_GOLD1)
    return H(layers)
add("K4: bell DARK_GOLD1 (within color tol)", k4())

def k5():
    """Badge has stroke but stroke alpha=0 (invisible)."""
    layers = perfect_bell()
    stroke = make_stroke(rgb=WHITE, weight=2)
    stroke["paint"]["color"]["a"] = 0
    layers[2]["strokes"] = [stroke]
    return H(layers)
add("K5: badge stroke color alpha=0", k5())

def k6():
    """Badge has stroke but visible=False."""
    layers = perfect_bell()
    stroke = make_stroke(rgb=WHITE, weight=2)
    stroke["visible"] = False
    layers[2]["strokes"] = [stroke]
    return H(layers)
add("K6: badge stroke visible=False", k6())

def k7():
    """Bell rotated 90° (drastically wrong but still in frame)."""
    layers = perfect_bell()
    layers[0]["rotation"] = 90
    return H(layers)
add("K7: bell rotated 90°", k7())

def k8():
    """Bell at far edge of frame, all squashed."""
    layers = perfect_bell()
    layers[0] = L("vector", 1100, 100, 50, 60, GOLD)  # tiny bell at right edge
    layers[1] = L("ellipse", 1110, 200, 20, 20, ORANGE)
    layers[2] = L("ellipse", 1120, 100, 12, 12, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("K8: bell at right edge, very small", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Bell fill alpha=0 (invisible)."""
    layers = perfect_bell()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: bell fill alpha=0", l1())

def l2():
    """Bell visible=False."""
    layers = perfect_bell()
    layers[0]["visible"] = False
    return H(layers)
add("L2: bell visible=False", l2())

def l3():
    """Bell layer opacity=0."""
    layers = perfect_bell()
    layers[0]["opacity"] = 0
    return H(layers)
add("L3: bell layer opacity=0", l3())

def l4():
    """Clapper visible=False."""
    layers = perfect_bell()
    layers[1]["visible"] = False
    return H(layers)
add("L4: clapper visible=False", l4())

def l5():
    """Badge fill visible=False."""
    layers = perfect_bell()
    layers[2]["fills"][0]["visible"] = False
    return H(layers)
add("L5: badge fill visible=False", l5())

def l6():
    """All 3 layers fillOpacity 0.05 (basically invisible)."""
    layers = perfect_bell()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L6: all fills opacity 0.05", l6())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Bell + clapper + badge all stacked at exact same point."""
    layers = [L("vector",  500, 400, 100, 100, GOLD),
              L("ellipse", 500, 400, 100, 100, ORANGE),
              L("ellipse", 500, 400, 100, 100, RED_BADGE,
                strokes=[make_stroke(rgb=WHITE, weight=2)])]
    return H(layers)
add("M1: all 3 layers piled at one point", m1())

def m2():
    """Bell huge with cornerRadius like a circle."""
    layers = perfect_bell()
    layers[0]["cornerRadius"] = 100
    return H(layers)
add("M2: bell cornerRadius=100", m2())

def m3():
    """Bell width = 2px (just over LayerSizeAtLeast min_w)."""
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 41, 41, GOLD)  # 41 just over 40
    return H(layers)
add("M3: bell 41×41 (just over min)", m3())

def m4():
    """Badge = full frame (occluding everything)."""
    layers = perfect_bell()
    layers[2] = L("ellipse", 0, 0, 1280, 832, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("M4: badge = full frame", m4())

def m5():
    """Both ellipses way larger than bell."""
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 100, 100, GOLD)  # smaller bell
    layers[1] = L("ellipse", 100, 600, 200, 200, ORANGE)  # huge clapper
    layers[2] = L("ellipse", 900, 100, 200, 200, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("M5: ellipses bigger than bell", m5())

def m6():
    """Frame at 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("M6: frame 2000x2000 (FrameSizeEquals fails)", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Bell in 1st frame; clapper+badge in 2nd frame."""
    bell = perfect_bell()
    f1 = make_frame([bell[0]], w=1280, h=832)
    f2 = make_frame(bell[1:], w=600, h=400)
    return make_log([f1, f2], evt())
add("N1: bell + ellipses in different frames", n1())

def n2():
    """Each shape in its own frame."""
    bell = perfect_bell()
    frames = [make_frame([s], w=1280, h=832) for s in bell]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Bell + clapper in frame, badge on page (siblings to frame)."""
    bell = perfect_bell()
    f = make_frame(bell[:2], w=1280, h=832)
    return make_log([f, bell[2]], evt())
add("N3: badge floating outside frame", n3())

def n4():
    """Components and instances instead of frame."""
    bell = perfect_bell()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": bell}
    return make_log([component], evt())
add("N4: bell inside component (no frame)", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Bell as a rectangle (not vector)."""
    layers = perfect_bell()
    layers[0] = L("rectangle", 540, 280, 200, 240, GOLD)
    return H(layers, evts=evt(vector=0))
add("O1: bell as rectangle (not vector)", o1())

def o2():
    """Clapper + badge are stars instead of ellipses."""
    layers = [perfect_bell()[0]]
    layers.append(make_layer("star", x=620, y=520, w=40, h=40, fill=GOLD, points=5, innerRatio=0.4))
    layers.append(make_layer("star", x=720, y=280, w=24, h=24, fill=RED_BADGE,
                             strokes=[make_stroke(rgb=WHITE, weight=2)], points=5, innerRatio=0.4))
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_star")]))
add("O2: clapper/badge are stars (no ellipse)", o2())

def o3():
    """Bell as polygon."""
    layers = perfect_bell()
    layers[0] = make_layer("polygon", x=540, y=280, w=200, h=240, fill=GOLD, sides=5)
    return H(layers, evts=evt(vector=0, extras=[make_event("create_polygon")]))
add("O3: bell as polygon (no vector)", o3())

def o4():
    """Bell, clapper, badge as text layers."""
    layers = [make_layer("text", x=540, y=280, w=200, h=240, fill=GOLD),
              make_layer("text", x=620, y=520, w=40, h=40, fill=ORANGE),
              make_layer("text", x=720, y=280, w=24, h=24, fill=RED_BADGE)]
    layers[0]["content"] = "bell"
    layers[1]["content"] = "."
    layers[2]["content"] = "1"
    return H(layers, evts=[make_event("session_start"), make_event("create_text")] * 3)
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

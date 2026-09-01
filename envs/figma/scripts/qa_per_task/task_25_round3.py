"""Round 3 novel deceptions for task 25 — 3 identical 160×40 buttons in row."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_25" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
BUTTON_COLOR = (0.20, 0.45, 0.85)


def evt(rect=3, set_fill=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_buttons(n=3, w=160, h=40, gap=12, color=BUTTON_COLOR, y=300, x0=200):
    layers = []
    for i in range(n):
        layers.append(L("rectangle", x0+i*(w+gap), y, w, h, color))
    return layers


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_buttons()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Buttons rotated 1.9° (under tol)."""
    layers = perfect_buttons()
    for l in layers:
        l["rotation"] = 1.9
    return H(layers)
add("K1: rotated 1.9°", k1())

def k2():
    """Buttons rotated 3° (over tol)."""
    layers = perfect_buttons()
    for l in layers:
        l["rotation"] = 3
    return H(layers)
add("K2: rotated 3° (over tol)", k2())

def k3():
    """y-baseline diff exactly 3px (at tol edge)."""
    layers = perfect_buttons()
    layers[1]["y"] += 3
    return H(layers)
add("K3: y diff 3px (at tol)", k3())

def k4():
    """Gap variance 7px (within 8 tol)."""
    layers = []
    cur = 200
    gaps = [12, 19]
    for i in range(3):
        layers.append(L("rectangle", cur, 300, 160, 40, BUTTON_COLOR))
        if i < 2:
            cur += 160 + gaps[i]
    return H(layers)
add("K4: gap +7px (within tol)", k4())

def k5():
    """Gap variance 9px (just over)."""
    layers = []
    cur = 200
    gaps = [12, 21]
    for i in range(3):
        layers.append(L("rectangle", cur, 300, 160, 40, BUTTON_COLOR))
        if i < 2:
            cur += 160 + gaps[i]
    return H(layers)
add("K5: gap +9px (just over tol)", k5())

def k6():
    """Buttons size 156×36 (within 4px tol)."""
    return H(perfect_buttons(w=156, h=36))
add("K6: 156×36 within tol", k6())

def k7():
    """Buttons size 165×46 (just over tol)."""
    return H(perfect_buttons(w=165, h=46))
add("K7: 165×46 just over tol", k7())

def k8():
    """3 buttons but distinct visually similar shades (within 0.05 tol)."""
    near = [(0.20,0.45,0.85),(0.20,0.46,0.85),(0.20,0.45,0.86)]
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200+i*172, 300, 160, 40, near[i]))
    return H(layers)
add("K8: near-same colors (within 0.05)", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    layers = perfect_buttons()
    layers[0]["visible"] = False
    return H(layers)
add("L1: 1 button visible=False", l1())

def l2():
    layers = perfect_buttons()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L2: 1 fill.visible=False", l2())

def l3():
    layers = perfect_buttons()
    for l in layers:
        l["opacity"] = 0.4
    return H(layers)
add("L3: opacity=0.4 on all", l3())

def l4():
    layers = perfect_buttons()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.4
    return H(layers)
add("L4: fill alpha=0.4 on all", l4())

def l5():
    layers = perfect_buttons()
    layers[2]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L5: 1 button alpha=0", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Buttons piled."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 600, 400, 160, 40, BUTTON_COLOR))
    return H(layers)
add("M1: buttons piled", m1())

def m2():
    """Buttons huge same size."""
    return H(perfect_buttons(w=400, h=100))
add("M2: 400×100 (huge but identical)", m2())

def m3():
    """Buttons = full frame each (3 stacked at 0,0)."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 0, 0, 1280, 832, BUTTON_COLOR))
    return H(layers)
add("M3: 3 buttons = full frame", m3())

def m4():
    """3 buttons in diagonal cascade."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200+i*172, 300+i*60, 160, 40, BUTTON_COLOR))
    return H(layers)
add("M4: diagonal cascade", m4())

def m5():
    """3 buttons all same color, but each has different opacity layer-level."""
    layers = perfect_buttons()
    for i, l in enumerate(layers):
        l["opacity"] = 1.0 - i*0.2  # 1.0, 0.8, 0.6
    return H(layers)
add("M5: opacity gradient on identical buttons", m5())

def m6():
    """3 buttons, only middle button is half-size."""
    layers = perfect_buttons()
    layers[1]["w"] = 80; layers[1]["h"] = 20
    return H(layers)
add("M6: 1 button half-size", m6())

def m7():
    """3 buttons + tiny extras (would be ignored by AllLayerBoundsInside if strict)."""
    layers = perfect_buttons()
    return H(layers)  # control again
add("M7: clean control", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    layers = perfect_buttons()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N1: in component", n1())

def n2():
    layers = perfect_buttons()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("N2: in instance", n2())

def n3():
    """Each button in its own frame."""
    layers = perfect_buttons()
    frames = [make_frame([l], w=300, h=200, x=i*350) for i, l in enumerate(layers)]
    return make_log(frames, evt())
add("N3: each button in own frame", n3())

def n4():
    """Buttons 4-deep nested."""
    layers = perfect_buttons()
    f4 = make_frame(layers, w=1280, h=832)
    f3 = make_frame([f4], w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("N4: 4-deep nested", n4())

def n5():
    """Buttons in section."""
    layers = perfect_buttons()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("N5: in section", n5())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    layers = []
    for i in range(3):
        layers.append(make_layer("ellipse", x=200+i*172, y=300, w=160, h=40,
                                  fill=BUTTON_COLOR))
    return H(layers, evts=evt(rect=0))
add("O1: 3 ellipses", o1())

def o2():
    layers = []
    for i in range(3):
        layers.append(make_layer("star", x=200+i*172, y=300, w=160, h=40,
                                  fill=BUTTON_COLOR, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0))
add("O2: 3 stars", o2())

def o3():
    layers = []
    for i in range(3):
        layers.append(make_layer("polygon", x=200+i*172, y=300, w=160, h=40,
                                  fill=BUTTON_COLOR, sides=4))
    return H(layers, evts=evt(rect=0))
add("O3: 3 polygons", o3())

def o4():
    """2 rectangles + 1 ellipse (mixed)."""
    layers = [L("rectangle", 200, 300, 160, 40, BUTTON_COLOR),
              L("rectangle", 372, 300, 160, 40, BUTTON_COLOR),
              make_layer("ellipse", x=544, y=300, w=160, h=40, fill=BUTTON_COLOR)]
    return H(layers, evts=evt(rect=2))
add("O4: 2 rects + 1 ellipse", o4())


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

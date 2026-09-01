"""Round 3 edge cases — task_05 (plus sign from 2 perpendicular red rectangles)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_05" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
BLUE_C = (0.2, 0.4, 0.85)


def evt(rect=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_plus(h_size=(200, 60), v_size=(60, 200), cx=500, cy=500):
    h = L("rectangle", cx-h_size[0]/2, cy-h_size[1]/2, h_size[0], h_size[1], RED)
    v = L("rectangle", cx-v_size[0]/2, cy-v_size[1]/2, v_size[0], v_size[1], RED)
    return [h, v]


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=False):
    if layers is None: layers = perfect_plus()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Centers off by 3px (within 4 tol)."""
    layers = perfect_plus()
    layers[1]["x"] += 3
    return H(layers)
add("K1: centers off 3px (within tol)", k1())

def k2():
    """Both rotated 1.9° (under 2 tol)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 1.9
    return H(layers)
add("K2: rotated 1.9°", k2())

def k3():
    """cornerRadius=18/60 = 0.30 (at boundary)."""
    layers = perfect_plus()
    for l in layers: l["cornerRadius"] = 17  # 17/60 = 0.283
    return H(layers)
add("K3: cornerRadius=17 (under 0.30 frac)", k3())

def k4():
    """Just-above-2 aspect (2.05)."""
    return H([L("rectangle", 400, 470, 123, 60, RED), L("rectangle", 470, 400, 60, 123, RED)])
add("K4: aspect 2.05 (just above)", k4())

def k5():
    """Both red but slightly off (within 0.20 tol)."""
    layers = perfect_plus()
    for l in layers: l["fills"][0]["color"] = {"r":0.85, "g":0.25, "b":0.25, "a":1}
    return H(layers)
add("K5: red shifted slightly (within tol)", k5())

def k6():
    """Plus where horizontal is slightly wider (same aspect mix passes)."""
    layers = perfect_plus(h_size=(220, 60), v_size=(60, 200))
    return H(layers)
add("K6: 220x60 + 60x200 (slightly off-symmetric)", k6())

def k7():
    """Plus where rectangles overlap a small offset (visible cross)."""
    layers = [L("rectangle", 410, 480, 200, 60, RED), L("rectangle", 480, 410, 60, 200, RED)]
    return H(layers)
add("K7: plus offset by ~10 (crossing visible)", k7())

def k8():
    """Plus where 1 rect rotated 1° (still cross-like)."""
    layers = perfect_plus()
    layers[0]["rotation"] = 1
    return H(layers)
add("K8: 1 rect rotated 1° (within tol)", k8())

def k9():
    """1 rectangle barely wider than tall (could be 'horizontal' barely)."""
    layers = [L("rectangle", 400, 480, 90, 50, RED), L("rectangle", 470, 410, 60, 200, RED)]
    return H(layers)
add("K9: horizontal aspect 1.8 (under 2)", k9())

def k10():
    """Plus where 2nd rectangle barely visible (1px overlap)."""
    layers = [L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 470, 530, 60, 200, RED)]
    return H(layers)
add("K10: 2nd rect outside (no cross)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    layers = perfect_plus()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: alpha=0", l1())

def l2():
    layers = perfect_plus()
    for l in layers: l["fills"][0]["visible"] = False
    return H(layers)
add("L2: fill.visible=False", l2())

def l3():
    layers = perfect_plus()
    for l in layers: l["opacity"] = 0.0
    return H(layers)
add("L3: layer.opacity=0", l3())

def l4():
    """1 invisible (alpha=0), 1 visible."""
    layers = perfect_plus()
    layers[1]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L4: 1 alpha=0, 1 visible", l4())

def l5():
    """Both image fills (no solid red)."""
    layers = perfect_plus()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("L5: both image fills", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Plus made of 2 squares 200x200 same position (overlapping)."""
    return H([L("rectangle", 400, 400, 200, 200, RED), L("rectangle", 400, 400, 200, 200, RED)])
add("M1: 2 200x200 stacked (no aspect mix)", m1())

def m2():
    """Plus with both at very different positions (not crossing)."""
    return H([L("rectangle", 100, 100, 200, 60, RED), L("rectangle", 700, 700, 60, 200, RED)])
add("M2: rects diagonal far apart", m2())

def m3():
    """Plus rotated 30° as a unit (each rect rotated 30°)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 30
    return H(layers)
add("M3: both rotated 30°", m3())

def m4():
    """Plus where rects very thin (1×200 each)."""
    return H([L("rectangle", 400, 499, 200, 1, RED), L("rectangle", 499, 400, 1, 200, RED)])
add("M4: 1px thin lines (rectangles)", m4())

def m5():
    """Plus where centers align by 1px."""
    layers = perfect_plus()
    layers[1]["x"] += 1
    return H(layers)
add("M5: 1px center offset (within tol)", m5())

def m6():
    """Plus where horizontal is reversed direction (negative w)."""
    layers = perfect_plus()
    layers[0]["w"] = -200
    layers[0]["x"] += 200
    return H(layers)
add("M6: horizontal w=-200", m6())

def m7():
    """Plus inside a frame that's rotated 90°."""
    layers = perfect_plus()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 90
    return make_log([frame], evt())
add("M7: frame rotated 90° (plus inside)", m7())

def m8():
    """Plus made of 2 stretched aspect rectangles 50:1."""
    return H([L("rectangle", 0, 499, 1000, 2, RED), L("rectangle", 499, 0, 2, 1000, RED)])
add("M8: 50:1 aspect rectangles", m8())


# ─── N. Hierarchy / structural tricks ────────────────────────────────
def n1():
    """Plus inside group inside frame."""
    layers = perfect_plus()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([g], w=900, h=900)
    return make_log([frame], evt())
add("N1: plus in group in frame", n1())

def n2():
    """Plus split: 1 rect in group, 1 outside."""
    layers = perfect_plus()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[layers[0]]}
    return make_log([g, layers[1]], evt())
add("N2: 1 rect in group, 1 outside", n2())

def n3():
    """Plus inside instance."""
    layers = perfect_plus()
    inst = {"id":"i1","type":"instance","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("N3: plus inside instance", n3())


# ─── O. Wrong shape types substituted ────────────────────────────────
def o1():
    """Plus made of 2 ellipses."""
    layers = [make_layer("ellipse", x=400, y=470, w=200, h=60, fill=RED),
              make_layer("ellipse", x=470, y=400, w=60, h=200, fill=RED)]
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 2)
    return H(layers, evts=sem)
add("O1: plus made of 2 ellipses", o1())

def o2():
    """Plus made of 2 polygons (4-sided)."""
    layers = [make_layer("polygon", x=400, y=470, w=200, h=60, fill=RED, sides=4),
              make_layer("polygon", x=470, y=400, w=60, h=200, fill=RED, sides=4)]
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    sem.extend([make_event("create_polygon")] * 2)
    return H(layers, evts=sem)
add("O2: plus made of 2 polygons", o2())

def o3():
    """Plus made of 2 stars (4-pointed)."""
    layers = [make_layer("star", x=400, y=470, w=200, h=60, fill=RED, points=4, innerRatio=0.5),
              make_layer("star", x=470, y=400, w=60, h=200, fill=RED, points=4, innerRatio=0.5)]
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 2)
    return H(layers, evts=sem)
add("O3: plus made of 2 stars", o3())

def o4():
    """Plus made of 2 lines."""
    layers = [make_layer("line", x=400, y=499, w=200, h=2, fill=None, strokes=[make_stroke(rgb=RED, weight=60)]),
              make_layer("line", x=499, y=400, w=2, h=200, fill=None, strokes=[make_stroke(rgb=RED, weight=60)])]
    for l in layers: l["fills"] = []
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.extend([make_event("create_line")] * 2)
    return H(layers, evts=sem)
add("O4: plus made of 2 lines (thick stroke)", o4())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95:
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95): {fp_count}")

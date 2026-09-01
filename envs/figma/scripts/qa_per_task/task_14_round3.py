"""Round 3 — novel-deception edge cases for task 14."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_14" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
BLACK = (0.0, 0.0, 0.0)


def evt(ellipse=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):
        sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_target():
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    colors = [RED, WHITE, RED, WHITE]
    layers = []
    for size, color in zip(sizes, colors):
        l = L("ellipse", cx-size/2, cy-size/2, size, size, color)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return layers


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_target()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Each ellipse w-h diff = 2.5 (just under tol=3)."""
    layers = perfect_target()
    for l in layers:
        l["w"] = l["w"]; l["h"] = l["w"] - 2.5
    return H(layers)
add("K1: w-h=2.5 (just under tol=3)", k1())

def k2():
    """Strokes 5px (4 + tol of 1)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=5)]
    return H(layers)
add("K2: strokes 5px (at tol edge)", k2())

def k3():
    """Strokes very dark gray (within color tol of black)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=(0.18, 0.18, 0.18), weight=4)]
    return H(layers)
add("K3: strokes 0.18 gray (within tol of black)", k3())

def k4():
    """Innermost color slightly off-white (very-light gray)."""
    layers = perfect_target()
    layers[3]["fills"][0]["color"] = {"r":0.85,"g":0.85,"b":0.85,"a":1}
    return H(layers)
add("K4: innermost light-gray (close to white)", k4())

def k5():
    """All same red (instead of alternating)."""
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    return H(layers)
add("K5: all red (no alternation)", k5())

def k6():
    """3 concentric + 1 offset by 3px (just over tol=2)."""
    layers = perfect_target()
    layers[3]["x"] += 3
    return H(layers)
add("K6: innermost off-center 3px", k6())

def k7():
    """Reverse z-order: smallest drawn first (innermost = first child)."""
    layers = perfect_target()[::-1]
    return H(layers)
add("K7: reverse z-order (smallest first)", k7())

def k8():
    """All strokes 0.5px (way too thin)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=0.5)]
    return H(layers)
add("K8: strokes 0.5px (way too thin)", k8())

def k9():
    """Sizes 240/200/160/120 (linear instead of halving)."""
    layers = perfect_target()
    cx, cy = 600, 416
    for i, size in enumerate([240, 200, 160, 120]):
        layers[i]["x"] = cx-size/2; layers[i]["y"] = cy-size/2
        layers[i]["w"] = size; layers[i]["h"] = size
    return H(layers)
add("K9: sizes 240/200/160/120 (linear shrink)", k9())

def k10():
    """All ellipses w=h=240 (no shrink — all same outermost size)."""
    layers = perfect_target()
    cx, cy = 600, 416
    for l in layers:
        l["x"] = cx-120; l["y"] = cy-120; l["w"] = 240; l["h"] = 240
    return H(layers)
add("K10: all same 240×240", k10())


# ─── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """All strokes visible=False."""
    layers = perfect_target()
    for l in layers:
        l["strokes"][0]["visible"] = False
    return H(layers)
add("L1: strokes visible=False", l1())

def l2():
    """All strokes alpha=0."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [{"paint":{"kind":"solid","color":{"r":0,"g":0,"b":0,"a":0.0}},
                         "weight":4,"alignment":"center","dash":None,"visible":True}]
    return H(layers)
add("L2: strokes alpha=0", l2())

def l3():
    """All fills visible=False."""
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L3: fills visible=False", l3())

def l4():
    """All ellipses opacity=0."""
    layers = perfect_target()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("L4: layer opacity=0", l4())

def l5():
    """All ellipses image fills."""
    layers = perfect_target()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("L5: image fills", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """1 ellipse 1×1 (innermost)."""
    layers = perfect_target()
    layers[3]["w"] = 1; layers[3]["h"] = 1
    return H(layers)
add("M1: innermost 1×1 degenerate", m1())

def m2():
    """All circles slightly elliptical (w=240, h=200)."""
    layers = perfect_target()
    for l in layers:
        l["h"] = l["w"] * 0.83  # 5/6 ratio — over tol=3
    return H(layers)
add("M2: ellipses w=1.2*h (not circles)", m2())

def m3():
    """All concentric but rotated to different angles."""
    layers = perfect_target()
    for i, l in enumerate(layers):
        l["rotation"] = i * 30
    return H(layers)
add("M3: concentric circles at varying rotations", m3())

def m4():
    """All ellipses huge (= full frame)."""
    layers = perfect_target()
    for l in layers:
        l["x"] = 0; l["y"] = 0; l["w"] = 1280; l["h"] = 832
    return H(layers)
add("M4: ellipses = full frame all stacked", m4())

def m5():
    """Ellipses concentric but smallest is 100x bigger than outermost."""
    layers = perfect_target()
    layers[3]["w"] = 1000; layers[3]["h"] = 1000
    layers[3]["x"] = 100; layers[3]["y"] = -100
    return H(layers)
add("M5: innermost MUCH bigger (1000×1000)", m5())

def m6():
    """Ellipses + 1 extra outside frame."""
    layers = perfect_target()
    extra = L("ellipse", 1300, 100, 60, 60, RED, strokes=[make_stroke(rgb=BLACK,weight=4)])
    layers.append(extra)
    return H(layers, evts=evt(ellipse=5))
add("M6: 5 ellipses (1 outside frame)", m6())

def m7():
    """Ellipses all flipped X — circles invariant to flip."""
    layers = perfect_target()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("M7: all ellipses flipped X", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Ellipses on page (no frame)."""
    return H(perfect_target(), in_frame=False)
add("N1: ellipses on page (no frame)", n1())

def n2():
    """Each ellipse in its own frame (split)."""
    layers = perfect_target()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N2: each ellipse in own frame", n2())

def n3():
    """Inside a Component instance."""
    layers = perfect_target()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: ellipses in component", n3())

def n4():
    """3 in frame, 1 outside as sibling."""
    layers = perfect_target()
    frame = make_frame(layers[:3], w=1280, h=832)
    return make_log([frame, layers[3]], evt())
add("N4: 3 in frame, 1 outside", n4())


# ─── O. Wrong types ──────────────────────────────────────────────────
def o1():
    """4 polygons (sides=8) instead of ellipses."""
    layers = []
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    colors = [RED, WHITE, RED, WHITE]
    for size, color in zip(sizes, colors):
        l = make_layer("polygon", x=cx-size/2, y=cy-size/2, w=size, h=size,
                       fill=color, sides=8)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_polygon")]*4))
add("O1: 4 polygons (sides=8) instead of ellipses", o1())

def o2():
    """4 rectangles instead."""
    layers = []
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    colors = [RED, WHITE, RED, WHITE]
    for size, color in zip(sizes, colors):
        l = make_layer("rectangle", x=cx-size/2, y=cy-size/2, w=size, h=size,
                       fill=color)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]*4))
add("O2: 4 rectangles (squares) instead of ellipses", o2())

def o3():
    """3 ellipses + 1 star."""
    layers = perfect_target()[:3]
    cx, cy = 600, 416
    star = make_layer("star", x=cx-30, y=cy-30, w=60, h=60, fill=WHITE,
                      points=5, innerRatio=0.4)
    star["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    layers.append(star)
    return H(layers, evts=evt(ellipse=3, extras=[make_event("create_star")]))
add("O3: 3 ellipses + 1 star", o3())


# ─── Run ─────────────────────────────────────────────────────────────
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

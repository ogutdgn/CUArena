"""Round 3 — novel-deception edge cases for task 12."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_12" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(rect=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_row(n=4, w=120, h=120, gap=20, y=300, x0=200):
    colors = [PINK, ORANGE, GREEN, BLUE]
    return [L("rectangle", x0+i*(w+gap), y, w, h, colors[i % len(colors)]) for i in range(n)]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_row()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """All rects rotated 1° (under-tol but accumulating skew)."""
    layers = perfect_row()
    for l in layers:
        l["rotation"] = 1
    return H(layers)
add("K1: all rects rotated 1° (under tol=2)", k1())

def k2():
    """Each rect rotated to a different angle (all under-tol)."""
    layers = perfect_row()
    for i, l in enumerate(layers):
        l["rotation"] = i * 0.5  # 0, 0.5, 1.0, 1.5
    return H(layers)
add("K2: rotations 0,0.5,1,1.5° (each under-tol)", k2())

def k3():
    """All rects with cornerRadius=48 (40% of 120) — just at edge."""
    layers = perfect_row()
    for l in layers:
        l["cornerRadius"] = 48  # 0.40 * 120 = exactly at threshold
    return H(layers)
add("K3: cornerRadius=48 (right at max_frac)", k3())

def k4():
    """All rects with cornerRadius=49 (over the 0.40 threshold)."""
    layers = perfect_row()
    for l in layers:
        l["cornerRadius"] = 49
    return H(layers)
add("K4: cornerRadius=49 (just over max)", k4())

def k5():
    """Inverse z-order: 4th rect drawn first (behind)."""
    layers = perfect_row()
    layers.reverse()
    return H(layers)
add("K5: rects in reverse z-order", k5())

def k6():
    """Rects at different y but slope <5px each (chains)."""
    layers = perfect_row()
    for i, l in enumerate(layers):
        l["y"] += i * 4  # 0, 4, 8, 12 — break tol=5
    return H(layers)
add("K6: y staircase +4 each (cumulative)", k6())

def k7():
    """All gaps just over variance_tolerance (1, 11, 11)."""
    layers = []
    xs = [200, 320 + 1, 440 + 1 + 11, 560 + 1 + 11 + 11]  # gaps: 0+1, 0+1+11, ...
    # Actually rebuild for explicit test: gaps of 1, 12, 12
    xs = [200, 320 + 1, 320 + 1 + 120 + 12, 320 + 1 + 120 + 12 + 120 + 12]
    for i in range(4):
        layers.append(L("rectangle", xs[i], 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("K7: gaps 1,12,12 (variance just over tol=10)", k7())

def k8():
    """Rects in column, but each at slightly different x (looks like a row from afar)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 600+(i%2)*5, 200+i*150, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("K8: vertical column with x-jitter", k8())

def k9():
    """Each rect has fillOpacity=0.49 (just under min_opacity=0.5)."""
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["opacity"] = 0.49
    return H(layers)
add("K9: fillOpacity=0.49 (just under min_opacity)", k9())

def k10():
    """Each rect cornerRadius=120 (= w & h) → full circle."""
    layers = perfect_row()
    for l in layers:
        l["cornerRadius"] = 120
    return H(layers)
add("K10: cornerRadius=120 (rects look as circles)", k10())


# ─── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Last rect alpha=0 (only 3 visible)."""
    layers = perfect_row()
    layers[3]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: 1 rect alpha=0 (3 visible)", l1())

def l2():
    """Last rect visible=False at layer level."""
    layers = perfect_row()
    layers[3]["visible"] = False
    return H(layers)
add("L2: 1 rect visible=False (3 visible)", l2())

def l3():
    """Last rect layer opacity=0.0."""
    layers = perfect_row()
    layers[3]["opacity"] = 0.0
    return H(layers)
add("L3: 1 rect opacity=0.0", l3())

def l4():
    """All rects fill.visible=False."""
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L4: all fills visible=False", l4())

def l5():
    """All rects have image fill (no solid)."""
    layers = perfect_row()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("L5: all image fills (no solid)", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All rects degenerate (1×1) at row positions."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300, 1, 1, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("M1: all 1×1 degenerate", m1())

def m2():
    """All rects 5×5 — pass count, alignment, but tiny."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300, 5, 5, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("M2: 5×5 rects (under min)", m2())

def m3():
    """All rects = full frame size, stacked at (0,0)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 0, 0, 1280, 832, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("M3: rects = full frame all stacked", m3())

def m4():
    """Each rect fills entire frame width (no row, no spacing)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 0, 200+i*60, 1280, 50, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("M4: stacked horizontal bands (full-width rows)", m4())

def m5():
    """Rects in row, but 1 way bigger (looks like banner card)."""
    layers = perfect_row()
    layers[1]["w"] = 600
    layers[1]["x"] = 320
    # shift rest
    layers[2]["x"] = 950
    layers[3]["x"] = 1090
    return H(layers)
add("M5: 1 rect 600 wide (rest 120)", m5())

def m6():
    """Rects in row but flipped horizontally."""
    layers = perfect_row()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("M6: all rects flipped X (mirror)", m6())

def m7():
    """All rects have w=120, h=120, but fills are gradient kinds."""
    layers = perfect_row()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("M7: all gradient fills", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Rects on page (no frame at all)."""
    layers = perfect_row()
    return make_log(layers, evt())
add("N1: rects on page, no frame", n1())

def n2():
    """4 rects, each in its own frame."""
    layers = perfect_row()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N2: each rect in own frame", n2())

def n3():
    """Rects inside a Component instance."""
    layers = perfect_row()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: rects in component (not frame)", n3())

def n4():
    """Rects split: 2 in frame, 2 outside frame as siblings."""
    layers = perfect_row()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, *layers[2:]], evt())
add("N4: 2 in frame, 2 outside", n4())


# ─── O. Wrong types ──────────────────────────────────────────────────
def o1():
    """4 polygons sides=4 (not rectangles, look square)."""
    layers = []
    for i in range(4):
        layers.append(make_layer("polygon", x=200+i*150, y=300, w=120, h=120,
                                  fill=[PINK,ORANGE,GREEN,BLUE][i], sides=4))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]*4))
add("O1: 4 polygons sides=4 (not rects)", o1())

def o2():
    """4 ellipses with same w=h (look circular cards but type wrong)."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 200+i*150, 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_ellipse")]*4))
add("O2: 4 ellipses (not rects)", o2())

def o3():
    """3 rectangles + 1 star at row (4 total but wrong type)."""
    layers = perfect_row(n=3)
    layers.append(make_layer("star", x=200+3*140, y=300, w=120, h=120,
                              fill=BLUE, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=3, extras=[make_event("create_star")]))
add("O3: 3 rects + 1 star (not 4 rects)", o3())


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

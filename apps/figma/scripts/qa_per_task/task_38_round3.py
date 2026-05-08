"""Round 3 — novel deception cases for task 38 (battery indicator)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_38" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GREEN_BAR  = (0.4, 0.85, 0.4)
YELLOW_BAR = (0.95, 0.85, 0.2)
RED_BAR    = (0.95, 0.3, 0.3)
GRAY_STROKE = (0.5, 0.5, 0.5)


def evt(rect=5, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_battery(body_radius=8):
    body = L("rectangle", 200, 300, 200, 80, WHITE,
             cornerRadius=body_radius,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    terminal = L("rectangle", 400, 325, 12, 30, GRAY_STROKE)
    bars = []
    for i, color in enumerate([GREEN_BAR, YELLOW_BAR, RED_BAR]):
        bars.append(L("rectangle", 220+i*45, 320, 40, 40, color))
    return [body, terminal, *bars]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_battery()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Body cornerRadius=4 (right at boundary - within tol)."""
    layers = perfect_battery(body_radius=4)
    return H(layers)
add("K1: body cornerRadius=4 (boundary)", k1())

def k2():
    """Body cornerRadius=3.5 (just under min)."""
    layers = perfect_battery(body_radius=3.5)
    return H(layers)
add("K2: body cornerRadius=3.5 (under min)", k2())

def k3():
    """Body rotated 1° (within tolerance)."""
    layers = perfect_battery()
    layers[0]["rotation"] = 1
    return H(layers)
add("K3: body rotated 1° (within tol)", k3())

def k4():
    """Body stroke alignment differs (inside vs center)."""
    layers = perfect_battery()
    layers[0]["strokes"][0]["alignment"] = "inside"
    return H(layers)
add("K4: stroke alignment=inside", k4())

def k5():
    """3 bars same green, but slightly different shades (within tol=0.1)."""
    layers = perfect_battery()
    layers[2]["fills"][0]["color"] = {"r":0.4, "g":0.85, "b":0.4, "a":1}
    layers[3]["fills"][0]["color"] = {"r":0.45, "g":0.88, "b":0.45, "a":1}
    layers[4]["fills"][0]["color"] = {"r":0.4, "g":0.82, "b":0.4, "a":1}
    return H(layers)
add("K5: 3 bars near-identical green (within tol)", k5())

def k6():
    """Stroke weight 0.6 (below requested 2 by 1.4 = within new tol 1.5)."""
    layers = perfect_battery()
    layers[0]["strokes"][0]["weight"] = 0.6
    return H(layers)
add("K6: stroke weight 0.6 (within tol)", k6())

def k7():
    """Stroke color slightly off (gray with red tint)."""
    layers = perfect_battery()
    layers[0]["strokes"][0]["paint"]["color"] = {"r":0.65, "g":0.5, "b":0.5, "a":1}
    return H(layers)
add("K7: stroke color near-gray with red tint", k7())

def k8():
    """Body cornerRadius=200 (basically circle)."""
    layers = perfect_battery()
    layers[0]["cornerRadius"] = 200
    return H(layers)
add("K8: body cornerRadius=200 (extreme)", k8())

def k9():
    """Stroke 0 weight + body cornerRadius=10."""
    layers = perfect_battery()
    layers[0]["strokes"][0]["weight"] = 0
    return H(layers)
add("K9: stroke weight=0", k9())

def k10():
    """Body very tilted (45°)."""
    layers = perfect_battery()
    layers[0]["rotation"] = 45
    return H(layers)
add("K10: body rotated 45°", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """All bars alpha=0."""
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: all bars alpha=0", l1())

def l2():
    """Body stroke color alpha=0 (invisible stroke)."""
    layers = perfect_battery()
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("L2: body stroke alpha=0", l2())

def l3():
    """Bars all visible=False."""
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["visible"] = False
    return H(layers)
add("L3: bars layer visible=False", l3())

def l4():
    """Terminal opacity=0."""
    layers = perfect_battery()
    layers[1]["opacity"] = 0
    return H(layers)
add("L4: terminal opacity=0", l4())

def l5():
    """Body fill alpha=0 + stroke gray (basically empty body)."""
    layers = perfect_battery()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L5: body fill alpha=0 (only stroke visible)", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Body wide-thin: 600x10 — thin body looks like line."""
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 600, 10, WHITE,
                  cornerRadius=4,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("M1: body 600x10 (thin like line)", m1())

def m2():
    """All 5 rects same size (no clear body)."""
    layers = []
    for i in range(5):
        layers.append(L("rectangle", 200+i*60, 300, 50, 50,
                        [WHITE, GRAY_STROKE, GREEN_BAR, YELLOW_BAR, RED_BAR][i],
                        cornerRadius=4,
                        strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)]))
    return H(layers)
add("M2: all 5 rects same size (no clear body)", m2())

def m3():
    """Bars in body but huge - covering body."""
    layers = perfect_battery()
    for i in range(3):
        layers[2+i] = L("rectangle", 210+i*5, 305, 200, 70,
                         [GREEN_BAR, YELLOW_BAR, RED_BAR][i])
    return H(layers)
add("M3: bars covering entire body", m3())

def m4():
    """Body smaller than bars (inverted size hierarchy)."""
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 30, 30, WHITE,
                  cornerRadius=4,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    for i in range(3):
        layers[2+i] = L("rectangle", 220+i*45, 300, 40, 40,
                         [GREEN_BAR, YELLOW_BAR, RED_BAR][i])
    return H(layers)
add("M4: body smaller than bars", m4())

def m5():
    """Body covers entire frame, stroke = transparent."""
    layers = perfect_battery()
    layers[0] = L("rectangle", 0, 0, 1280, 832, WHITE,
                  cornerRadius=8,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("M5: body = full frame", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Terminal in separate frame from body."""
    layers = perfect_battery()
    f1 = make_frame([layers[0], *layers[2:]], w=1280, h=832)
    f2 = make_frame([layers[1]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("N1: terminal in separate frame", n1())

def n2():
    """All shapes inside group, group inside frame."""
    layers = perfect_battery()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("N2: all in group inside frame", n2())

def n3():
    """Bars in component, body in frame."""
    layers = perfect_battery()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers[2:]}
    frame = make_frame([layers[0], layers[1], comp], w=1280, h=832)
    return make_log([frame], evt())
add("N3: bars in component", n3())

def n4():
    """Each rect in own 1-rect frame."""
    layers = perfect_battery()
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("N4: each rect in own frame", n4())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Body is ellipse instead of rectangle."""
    layers = perfect_battery()
    layers[0] = make_layer("ellipse", x=200, y=300, w=200, h=80,
                            fill=WHITE,
                            strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=4))
add("O1: body ellipse, not rect", o1())

def o2():
    """All 3 bars are stars."""
    layers = perfect_battery()[:2]
    for i, c in enumerate([GREEN_BAR, YELLOW_BAR, RED_BAR]):
        layers.append(make_layer("star", x=220+i*45, y=320, w=40, h=40,
                                  fill=c, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=2))
add("O2: bars are stars, not rects", o2())

def o3():
    """Terminal is line."""
    layers = perfect_battery()
    layers[1] = make_layer("line", x=400, y=325, w=12, h=30,
                            fill=None,
                            strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=4))
add("O3: terminal is line", o3())


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

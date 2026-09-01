"""Round 3 novel-deception edge cases for task 30 (Stripe wallpaper).

Spec: 6 vertical stripes alternating deep-blue/cream filling a 600x600 frame.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_30" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
DARK_BLUE = (0.10, 0.20, 0.55)
LIGHT_CREAM = (1.00, 0.95, 0.80)


def evt(rect=6, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    layers = []
    stripe_w = 100
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * stripe_w, 0, stripe_w, 600, color))
    return layers


def H(layers=None, frame_w=600, frame_h=600, frame_fill=WHITE,
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ───────────────────────────────────────────
def k1():
    """Stripes rotated 4° (under tolerance)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("K1: stripes rotated 4° (under tol)", k1())


def k2():
    """6 stripes but pattern is AABB-AB."""
    colors = [DARK_BLUE, DARK_BLUE, LIGHT_CREAM, LIGHT_CREAM, DARK_BLUE, LIGHT_CREAM]
    layers = []
    for i, c in enumerate(colors):
        layers.append(L("rectangle", i * 100, 0, 100, 600, c))
    return H(layers)
add("K2: AABB-AB pattern (broken alternation)", k2())


def k3():
    """All 6 stripes at exactly the same position (overlapping)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 0, 0, 600, 600, color))
    return H(layers)
add("K3: 6 stripes piled at same spot", k3())


def k4():
    """Stripes are 1px wide (degenerate)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 1, 600, color))
    return H(layers)
add("K4: stripes 1px wide", k4())


def k5():
    """6 stripes side-by-side but heights vary."""
    layers = []
    heights = [100, 200, 300, 400, 500, 600]
    for i, h in enumerate(heights):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 100, h, color))
    return H(layers)
add("K5: stripes ascending heights", k5())


def k6():
    """Stripes have aspect ratio 1.5 (just under min 2.0)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 100, 150, color))
    return H(layers)
add("K6: stripes aspect 1.5 (just under 2.0 min)", k6())


def k7():
    """Stripes very short (aspect 1:1 = squares)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 100, 100, color))
    return H(layers)
add("K7: stripes 100x100 (squares)", k7())


def k8():
    """Stripes mirrored scaleY=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleY"] = -1
    return H(layers)
add("K8: stripes scaleY=-1", k8())


def k9():
    """Stripes have height 400 (not full frame height)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 100, 100, 400, color))
    return H(layers)
add("K9: stripes only 400px tall", k9())


def k10():
    """Stripes alternating but with tiny gap > 8px (10px gap)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 110, 0, 100, 600, color))
    return H(layers, frame_w=660)
add("K10: stripes 10px gap (over tol)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """All stripes opacity=0."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("L1: stripes opacity=0", l1())


def l2():
    """Stripes fill alpha=0."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L2: stripes fill alpha=0", l2())


def l3():
    """Stripes fill.opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L3: stripes fill opacity=0.05", l3())


def l4():
    """Half stripes visible=False."""
    layers = perfect_design()
    for l in layers[::2]:
        l["visible"] = False
    return H(layers)
add("L4: 3 of 6 stripes visible=False", l4())


def l5():
    """All stripes fill visible=False."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L5: stripes fill visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Stripes outside frame entirely."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 1000 + i * 100, 1000, 100, 600, color))
    return H(layers)
add("M1: stripes off-frame", m1())


def m2():
    """Stripes diagonal layout."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, i * 100, 100, 100, color))
    return H(layers)
add("M2: stripes in diagonal", m2())


def m3():
    """6 horizontal stripes (wrong axis)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 0, i * 100, 600, 100, color))
    return H(layers)
add("M3: 6 horizontal stripes", m3())


def m4():
    """Stripes are 5px wide (under min 10)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 5, 0, 5, 600, color))
    return H(layers)
add("M4: stripes 5px wide (under min 10)", m4())


def m5():
    """Stripes overlapping by 50%."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 50, 0, 100, 600, color))
    return H(layers)
add("M5: stripes 50% overlap", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Stripes split: 3 in frame_a, 3 in frame_b."""
    stripes = perfect_design()
    f1 = make_frame(stripes[:3], w=300, h=600)
    f2 = make_frame(stripes[3:], w=300, h=600)
    return make_log([f1, f2], evt())
add("N1: 3 stripes in frame_a, 3 in frame_b", n1())


def n2():
    """Stripes inside group inside frame."""
    layers = perfect_design()
    group = {"id": "grp_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=600, h=600)
    return make_log([frame], evt())
add("N2: frame > group > stripes (not direct)", n2())


def n3():
    """Stripes in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 600, "h": 600, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: stripes in component (no frame)", n3())


def n4():
    """5 stripes in frame, 1 outside on page."""
    stripes = perfect_design()
    frame = make_frame(stripes[:5], w=600, h=600)
    return make_log([frame, stripes[5]], evt())
add("N4: 5 in frame, 1 on page", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """6 polygons (4-sided) stripes."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("polygon", i * 100, 0, 100, 600, color, sides=4))
    return H(layers, evts=evt(rect=0) + [make_event("create_polygon")]*6)
add("O1: 6 polygons instead of rects", o1())


def o2():
    """6 ellipses (vertical ovals)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("ellipse", i * 100, 0, 100, 600, color))
    return H(layers, evts=evt(rect=0) + [make_event("create_ellipse")]*6)
add("O2: 6 ellipses instead of rects", o2())


def o3():
    """6 vertical lines."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        line = make_layer("line", x=i * 100 + 50, y=0, w=0, h=600, fill=None,
                          strokes=[make_stroke(rgb=color, weight=80)])
        line["p1"] = {"x": 0, "y": 0}
        line["p2"] = {"x": 0, "y": 600}
        layers.append(line)
    return H(layers, evts=evt(rect=0) + [make_event("create_line")]*6)
add("O3: 6 vertical lines instead of rects", o3())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)

for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

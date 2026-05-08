"""Round 3 novel-deception edge cases for task 27 (Neumorphic button).

Spec: 200×200 light-gray rounded rectangle with two paired drop shadows.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow, make_layer_blur,
    score_task,
)
from tasks import task_27_neumorphic_button as t
T = t.task

LIGHT_GRAY = (0.88, 0.90, 0.93)
NEAR_WHITE = (0.97, 0.97, 0.97)


def evt(rect=1, set_fill=1, effects=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(effects):  sem.append(make_event("add_effect"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_button():
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY,
            cornerRadius=24,
            effects=[
                make_drop_shadow(x=-6, y=-6, blur=12, rgb=(1,1,1), alpha=0.6),
                make_drop_shadow(x=6, y=6, blur=12, rgb=(0,0,0), alpha=0.25),
            ])
    return [btn]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_button()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ───────────────────────────────────────────
def k1():
    """Both drop shadows on the same side (no contrast / paired effect)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=6, y=6, alpha=0.4),
                     make_drop_shadow(x=8, y=8, alpha=0.5)])
    return H([btn])
add("K1: 2 drop shadows on same side (no opposing pair)", k1())


def k2():
    """Both drop shadows are zero-offset (degenerate)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=0, y=0, blur=4, alpha=0.3),
                     make_drop_shadow(x=0, y=0, blur=8, alpha=0.4)])
    return H([btn])
add("K2: 2 zero-offset drop shadows", k2())


def k3():
    """1 visible drop shadow + 1 hidden (visible=False)."""
    e1 = make_drop_shadow(x=-6, y=-6, alpha=0.5)
    e2 = make_drop_shadow(x=6, y=6, alpha=0.5)
    e2["visible"] = False
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[e1, e2])
    return H([btn])
add("K3: 1 visible + 1 hidden drop shadow", k3())


def k4():
    """1 visible drop shadow + 1 alpha=0 drop shadow."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6, y=-6, alpha=0.5),
                     make_drop_shadow(x=6, y=6, alpha=0.0)])
    return H([btn])
add("K4: 1 alpha=0 drop shadow + 1 visible", k4())


def k5():
    """Effect kind 'inner_shadow' (which doesn't exist in our type system) — should fail DropShadowExists."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[{"kind": "inner_shadow", "x": -6, "y": -6, "blur": 6, "spread": 0,
                      "color": {"r":1,"g":1,"b":1,"a":0.6}, "visible": True},
                     {"kind": "inner_shadow", "x": 6, "y": 6, "blur": 6, "spread": 0,
                      "color": {"r":0,"g":0,"b":0,"a":0.25}, "visible": True}])
    return H([btn])
add("K5: inner_shadow effects (not drop_shadow)", k5())


def k6():
    """Rotated 4° (just under tolerance)."""
    btn = perfect_button()[0]
    btn["rotation"] = 4
    return H([btn])
add("K6: rotated 4° (under tol)", k6())


def k7():
    """cornerRadius equal to half (= circle)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=100,
            effects=[make_drop_shadow(x=-6, y=-6, alpha=0.5),
                     make_drop_shadow(x=6, y=6, alpha=0.5)])
    return H([btn])
add("K7: cornerRadius=100 in 200x200 (full circle)", k7())


def k8():
    """Tiny shadow offset (subpixel)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=0.5, y=0.5, alpha=0.3),
                     make_drop_shadow(x=-0.5, y=-0.5, alpha=0.3)])
    return H([btn])
add("K8: ±0.5px offset shadows (subpixel)", k8())


def k9():
    """Frame's color same as button (no contrast - white-on-white)."""
    btn = L("rectangle", 540, 316, 200, 200, NEAR_WHITE, cornerRadius=24,
            effects=[make_drop_shadow(x=-6, y=-6, alpha=0.5),
                     make_drop_shadow(x=6, y=6, alpha=0.5)])
    return H([btn], frame_fill=NEAR_WHITE)
add("K9: white button on white frame (camouflaged)", k9())


def k10():
    """Button = full frame size."""
    btn = L("rectangle", 0, 0, 1280, 832, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6, y=-6, alpha=0.5),
                     make_drop_shadow(x=6, y=6, alpha=0.5)])
    return H([btn])
add("K10: button covers entire frame", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Layer-level opacity=0.4 (just below threshold of 0.5)."""
    btn = perfect_button()[0]
    btn["opacity"] = 0.4
    return H([btn])
add("L1: layer opacity=0.4 (below 0.5 threshold)", l1())


def l2():
    """fill alpha=0.3 (just below threshold)."""
    btn = perfect_button()[0]
    btn["fills"][0]["color"]["a"] = 0.3
    return H([btn])
add("L2: fill alpha=0.3 (below threshold)", l2())


def l3():
    """fill.opacity=0.2 (just below threshold)."""
    btn = perfect_button()[0]
    btn["fills"][0]["opacity"] = 0.2
    return H([btn])
add("L3: fill opacity=0.2 (below threshold)", l3())


def l4():
    """layer.visible=False."""
    btn = perfect_button()[0]
    btn["visible"] = False
    return H([btn])
add("L4: layer visible=False", l4())


def l5():
    """fill.visible=False."""
    btn = perfect_button()[0]
    btn["fills"][0]["visible"] = False
    return H([btn])
add("L5: fill visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Just over tolerance: 211x211."""
    btn = L("rectangle", 540, 316, 211, 211, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6,alpha=0.5), make_drop_shadow(x=6,y=6,alpha=0.5)])
    return H([btn])
add("M1: 211x211 (just over tol)", m1())


def m2():
    """Skinny 200x100 (wrong aspect)."""
    btn = L("rectangle", 540, 316, 200, 100, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6,alpha=0.5), make_drop_shadow(x=6,y=6,alpha=0.5)])
    return H([btn])
add("M2: 200x100 (rect, not square)", m2())


def m3():
    """cornerRadius given as a 4-tuple list."""
    btn = perfect_button()[0]
    btn["cornerRadius"] = [24, 24, 24, 24]
    return H([btn])
add("M3: cornerRadius as 4-tuple", m3())


def m4():
    """cornerRadius mixed list (some sharp, some rounded)."""
    btn = perfect_button()[0]
    btn["cornerRadius"] = [24, 0, 24, 0]
    return H([btn])
add("M4: cornerRadius mixed list", m4())


def m5():
    """Frame rotated AND button rotated by same amount (visually upright)."""
    btn = perfect_button()[0]
    btn["rotation"] = 30
    layers = [btn]
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("M5: frame+btn both rotated 30°", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Button inside section (not frame)."""
    layers = perfect_button()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("N1: button in section, no frame", n1())


def n2():
    """Button inside group (no frame)."""
    layers = perfect_button()
    group = {"id": "grp_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("N2: button in group, no frame", n2())


def n3():
    """Frame contains a group, group contains button (button is grandchild)."""
    layers = perfect_button()
    group = {"id": "grp_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("N3: frame > group > button (not direct child)", n3())


def n4():
    """Frame contains component instance, component contains button."""
    layers = perfect_button()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 200, "h": 200, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    frame = make_frame([component], w=1280, h=832)
    return make_log([frame], evt())
add("N4: frame > component > button", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Polygon (4 sides = square) with shadows instead of rectangle."""
    poly = make_layer("polygon", x=540, y=316, w=200, h=200, fill=LIGHT_GRAY, sides=4,
                      effects=[make_drop_shadow(x=-6,y=-6,alpha=0.5), make_drop_shadow(x=6,y=6,alpha=0.5)])
    return H([poly], evts=evt(rect=0) + [make_event("create_polygon")])
add("O1: 4-sided polygon (square shape) instead of rect", o1())


def o2():
    """Star with shadows."""
    star = make_layer("star", x=540, y=316, w=200, h=200, fill=LIGHT_GRAY,
                      points=4, innerRatio=0.7,
                      effects=[make_drop_shadow(x=-6,y=-6,alpha=0.5), make_drop_shadow(x=6,y=6,alpha=0.5)])
    return H([star], evts=evt(rect=0) + [make_event("create_star")])
add("O2: 4-point star (square-ish) instead of rect", o2())


def o3():
    """Ellipse with shadows."""
    e = make_layer("ellipse", x=540, y=316, w=200, h=200, fill=LIGHT_GRAY,
                   effects=[make_drop_shadow(x=-6,y=-6,alpha=0.5), make_drop_shadow(x=6,y=6,alpha=0.5)])
    return H([e], evts=evt(rect=0) + [make_event("create_ellipse")])
add("O3: ellipse instead of rectangle", o3())


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

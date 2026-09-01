"""Round 3 novel-deception edge cases for task 31 (Sun rays).

Spec: Yellow center circle + 4 triangle rays at 90° intervals (radial sun).
"""
from __future__ import annotations
import sys
import math
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_31" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
YELLOW_SUN = (1.0, 0.9, 0.2)


def evt(ellipse=1, polygon=4, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    sem.append(make_event("tool_change", before="ellipse", after="polygon"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    cx, cy = 600, 400
    layers = []
    layers.append(L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN))
    radius = 200
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + radius * math.cos(angle_rad)
        ry = cy + radius * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return layers


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
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
    """Rays with 4 sides (squares not triangles)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["sides"] = 4
    return H(layers)
add("K1: rays sides=4 (squares not triangles)", k1())


def k2():
    """Rays with 5 sides (pentagons)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["sides"] = 5
    return H(layers)
add("K2: rays sides=5 (pentagons)", k2())


def k3():
    """Rays not rotated (all 0°)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["rotation"] = 0
    return H(layers)
add("K3: rays not rotated", k3())


def k4():
    """Rays rotated 91° step (just over 1° tolerance from 90°)."""
    layers = perfect_design()
    for i, ray in enumerate(layers[1:]):
        ray["rotation"] = i * 91.0
    return H(layers)
add("K4: rays at 91° steps", k4())


def k5():
    """Rays at 60°, 120°, 240°, 300° (3-way symmetric, but 4 of them)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [60, 120, 240, 300]
    for ang in angles:
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("K5: rays at 60/120/240/300° (not 90° step)", k5())


def k6():
    """Circle is yellow but very dim (distinct from spec)."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"] = {"r": 0.5, "g": 0.45, "b": 0.1, "a": 1}  # dark yellow
    return H(layers)
add("K6: circle dark yellow (under tol)", k6())


def k7():
    """Circle is oval (90x100)."""
    layers = perfect_design()
    layers[0]["w"] = 90; layers[0]["h"] = 100
    return H(layers)
add("K7: circle oval 90x100 (just over tol)", k7())


def k8():
    """4 rays at 0,0,90,180 — duplicate at 0°."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [0, 0, 90, 180]
    for ang in angles:
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = ang
        layers.append(ray)
    return H(layers)
add("K8: 2 rays at 0° (duplicate, missing 270°)", k8())


def k9():
    """4 rays all at the center (no radial)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        ray = L("polygon", cx-30, cy-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("K9: rays piled at center (no radial dist)", k9())


def k10():
    """Rays at varying radii from center: 100/150/200/250."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    radii = [100, 150, 200, 250]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + radii[i] * math.cos(angle_rad)
        ry = cy + radii[i] * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("K10: rays at varying radii (uneven)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Circle opacity=0."""
    layers = perfect_design()
    layers[0]["opacity"] = 0
    return H(layers)
add("L1: circle opacity=0", l1())


def l2():
    """Half rays opacity=0."""
    layers = perfect_design()
    for ray in layers[1::2]:
        ray["opacity"] = 0
    return H(layers)
add("L2: half rays opacity=0", l2())


def l3():
    """Circle fill alpha=0."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L3: circle alpha=0", l3())


def l4():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L4: design visible=False", l4())


def l5():
    """Rays fill visible=False."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["fills"][0]["visible"] = False
    return H(layers)
add("L5: rays fill visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Sun = full frame size."""
    layers = perfect_design()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    return H(layers)
add("M1: circle = full frame", m1())


def m2():
    """Rays = full frame size."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["w"] = ray["h"] = 1000
    return H(layers)
add("M2: rays = 1000x1000", m2())


def m3():
    """Rays clustered on one side (all in upper half)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [-45, -90, -135, -110]  # all upper
    for ang in angles:
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("M3: rays only in upper half", m3())


def m4():
    """Tiny circle 5x5."""
    layers = perfect_design()
    layers[0]["w"] = layers[0]["h"] = 5
    return H(layers)
add("M4: circle 5x5 (under min)", m4())


def m5():
    """Rays at 4 corners of frame, not radial around circle."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    pts = [(50, 50), (1100, 50), (50, 700), (1100, 700)]
    for x, y in pts:
        ray = L("polygon", x, y, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("M5: rays at frame corners", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Circle outside frame, rays inside frame."""
    layers = perfect_design()
    circle = layers.pop(0)
    frame = make_frame(layers, w=1280, h=832)
    return make_log([circle, frame], evt())
add("N1: circle outside frame, rays inside", n1())


def n2():
    """Rays in component, circle in frame."""
    layers = perfect_design()
    circle = layers[0]
    rays = layers[1:]
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": rays}
    frame = make_frame([circle, component], w=1280, h=832)
    return make_log([frame], evt())
add("N2: rays in component, circle in frame", n2())


def n3():
    """Design in section."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("N3: design in section, no frame", n3())


def n4():
    """Design in component (no frame)."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N4: design in component (no frame)", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Stars instead of triangle polygons."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = make_layer("star", x=rx-30, y=ry-30, w=60, h=60, fill=ORANGE,
                         points=3, innerRatio=0.4)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers, evts=evt(polygon=0) + [make_event("create_star")]*4)
add("O1: 4 stars instead of polygons", o1())


def o2():
    """Rectangles for rays."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("rectangle", rx-30, ry-30, 60, 60, ORANGE)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers, evts=evt(polygon=0) + [make_event("create_rectangle")]*4)
add("O2: 4 rectangles instead of polygons", o2())


def o3():
    """Polygon (5-sides) for circle."""
    cx, cy = 600, 400
    layers = [L("polygon", cx-50, cy-50, 100, 100, YELLOW_SUN, sides=5)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers, evts=evt(ellipse=0, polygon=5))
add("O3: pentagon for center (not circle)", o3())


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

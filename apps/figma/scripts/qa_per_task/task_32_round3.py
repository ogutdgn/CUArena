"""Round 3 edge cases — hunt for surviving false positives in task_32 (pinwheel).

Each case is a wrong pinwheel that the verifier should give < 0.95.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_32" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
C1 = (0.95, 0.4, 0.2)
C2 = (0.2, 0.4, 0.95)
DARK1 = (0.10, 0.10, 0.10)
DARK2 = (0.13, 0.13, 0.13)


def evt(polygon=4, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.append(make_event("tool_change", before="polygon", after="ellipse"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pinwheel(n=4, colors=(C1, C2), pivot_radius=20):
    cx, cy = 500, 500
    layers = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100, colors[i % len(colors)],
                        sides=3, rotation=math.degrees(angle)))
    layers.append(L("ellipse", cx - pivot_radius, cy - pivot_radius,
                    pivot_radius * 2, pivot_radius * 2, GRAY))
    return layers


def H(layers=None, evts=None):
    if layers is None: layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ── K. Subtle deceptions ─────────────────────────────────────────────
def k1():
    """4 triangles all same color but radially placed, alternation re-sorted by x."""
    layers = perfect_pinwheel(colors=(C1, C1))
    return H(layers)
add("K1: uniform color (alternation defeated)", k1())


def k2():
    """A,A,B,B color order — radially looks like A,B,A,B by x sort."""
    layers = perfect_pinwheel()
    cs = [C1, C1, C2, C2]
    for i, l in enumerate(layers[:4]):
        l["fills"][0]["color"] = {"r": cs[i][0], "g": cs[i][1], "b": cs[i][2], "a": 1.0}
    return H(layers)
add("K2: A,A,B,B but x-sort makes alternation pass", k2())


def k3():
    """Triangles rotated 4° (under tol 8) but radially valid."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["rotation"] = (l.get("rotation") or 0) + 4
    return H(layers)
add("K3: rotation +4° (under tol)", k3())


def k4():
    """All 4 triangles rotation=0, radially placed (no spin)."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["rotation"] = 0
    return H(layers)
add("K4: triangles radially placed but no rotation step", k4())


def k5():
    """Pivot ellipse very near edge, triangles look perfect from above."""
    layers = perfect_pinwheel()
    layers[-1]["x"] = 100
    layers[-1]["y"] = 100
    return H(layers)
add("K5: pivot ellipse far from triangle centroid", k5())


def k6():
    """Pivot ellipse very large (200×200) - not 'small'."""
    layers = perfect_pinwheel()
    layers[-1]["x"] = 400
    layers[-1]["y"] = 400
    layers[-1]["w"] = 200
    layers[-1]["h"] = 200
    return H(layers)
add("K6: pivot ellipse 200×200 (not 'small')", k6())


def k7():
    """4 triangles rotated 90 apart but identical in z-order: pivot drawn behind."""
    layers = perfect_pinwheel()
    pivot = layers.pop()
    layers.insert(0, pivot)
    return H(layers)
add("K7: pivot drawn before triangles (behind)", k7())


def k8():
    """Pivot above all (tomb-like, occludes blades)."""
    layers = perfect_pinwheel()
    layers[-1]["w"] = 200
    layers[-1]["h"] = 200
    layers[-1]["x"] = 400
    layers[-1]["y"] = 400
    return H(layers)
add("K8: pivot huge, occludes blades", k8())


def k9():
    """Triangles too small to count as blades - 5×5 pixels."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = l["h"] = 5
    return H(layers)
add("K9: blades 5×5 (degenerate)", k9())


def k10():
    """Pivot 1×1 degenerate."""
    layers = perfect_pinwheel()
    layers[-1]["w"] = 1
    layers[-1]["h"] = 1
    return H(layers)
add("K10: pivot ellipse 1×1", k10())


# ── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """All blade fills alpha=0 (invisible)."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: blade fills alpha=0", l1())


def l2():
    """All blade fills visible=False."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L2: blade fills visible=False", l2())


def l3():
    """All blade layer opacity=0."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["opacity"] = 0.0
    return H(layers)
add("L3: blade layer opacity=0", l3())


def l4():
    """Pivot ellipse alpha=0 (invisible center)."""
    layers = perfect_pinwheel()
    layers[-1]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L4: pivot fill alpha=0", l4())


def l5():
    """All blade fill opacity=0.05."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L5: blade fill opacity 0.05 (transparent)", l5())


# ── M. Geometry tricks ───────────────────────────────────────────────
def m1():
    """All triangles 1×1 — degenerate."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = l["h"] = 1
    return H(layers)
add("M1: blades 1×1 (visually invisible)", m1())


def m2():
    """4 triangles bigger than frame (overflow)."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = l["h"] = 800
    return H(layers)
add("M2: blades 800×800 (overflow frame)", m2())


def m3():
    """4 triangles all at same point (no spread)."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", 450, 450, 100, 100,
                        (C1, C2)[i % 2], sides=3, rotation=i * 90))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("M3: blades all stacked at same point", m3())


def m4():
    """Frame is full canvas, triangles tiny in corners."""
    cx, cy = 500, 500
    layers = []
    pos = [(50, 50), (1200, 50), (50, 1200), (1200, 1200)]
    for i, (x, y) in enumerate(pos):
        layers.append(L("polygon", x, y, 50, 50,
                        (C1, C2)[i % 2], sides=3, rotation=i * 90))
    layers.append(L("ellipse", cx - 20, cy - 20, 40, 40, GRAY))
    frame = make_frame(layers, w=1280, h=1280)
    return make_log([frame], evt())
add("M4: blades in corners (huge spread, not radial)", m4())


def m5():
    """Triangles + pivot all 0×0 — completely invisible."""
    layers = perfect_pinwheel()
    for l in layers:
        l["w"] = l["h"] = 0
    return H(layers)
add("M5: all shapes 0×0 (invisible structurally)", m5())


def m6():
    """Pivot is full frame (fake center)."""
    layers = perfect_pinwheel()
    layers[-1]["x"] = 0
    layers[-1]["y"] = 0
    layers[-1]["w"] = 900
    layers[-1]["h"] = 900
    return H(layers)
add("M6: pivot ellipse = full frame", m6())


def m7():
    """Triangle fills empty (no fill, no stroke = invisible)."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"] = []
        l["strokes"] = []
    return H(layers)
add("M7: blades have no fill no stroke", m7())


# ── N. Structural tricks ─────────────────────────────────────────────
def n1():
    """Triangles inside frame, pivot outside."""
    layers = perfect_pinwheel()
    pivot = layers.pop()
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame, pivot], evt())
add("N1: pivot outside frame, blades inside", n1())


def n2():
    """4 triangles split across 4 frames."""
    layers = perfect_pinwheel()
    frames = []
    for blade in layers[:4]:
        frames.append(make_frame([blade], w=900, h=900))
    frames.append(make_frame([layers[-1]], w=900, h=900))
    return make_log(frames, evt())
add("N2: each shape in its own frame", n2())


def n3():
    """Pinwheel inside component (not frame)."""
    layers = perfect_pinwheel()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 900, "h": 900, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: pinwheel inside component", n3())


def n4():
    """Triangles only on the page (no frame)."""
    layers = perfect_pinwheel()
    return make_log(layers, evt())
add("N4: pinwheel on page only (no frame)", n4())


# ── O. Wrong types ───────────────────────────────────────────────────
def o1():
    """Pivot is rectangle not ellipse."""
    layers = perfect_pinwheel()
    layers[-1] = L("rectangle", 480, 480, 40, 40, GRAY)
    return H(layers, evts=evt(ellipse=0))
add("O1: pivot rectangle", o1())


def o2():
    """4 stars instead of polygons."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 4
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(make_layer("star", x=rx, y=ry, w=100, h=100,
                                  fill=(C1, C2)[i % 2], points=5, innerRatio=0.4,
                                  rotation=math.degrees(angle)))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers, evts=evt(polygon=0))
add("O2: stars instead of polygons", o2())


def o3():
    """Polygon sides=4 (squares), not triangles."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["sides"] = 4
    return H(layers)
add("O3: polygons all 4 sides (not triangles)", o3())


# ── Run ─────────────────────────────────────────────────────────────
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

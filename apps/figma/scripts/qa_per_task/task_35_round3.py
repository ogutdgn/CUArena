"""Round 3 edge cases — hunt for surviving false positives in task_35 (honeycomb)."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, BLACK, WHITE, RED, GREEN, GOLD,
)
from tasks import task_35_honeycomb as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
YELLOW_HEX = (1.0, 0.85, 0.2)


def evt(polygon=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_honeycomb(n=4, side=80, fill=YELLOW_HEX, stroke=BLACK, sides=6, weight=1):
    layers = []
    for i in range(n):
        r, c = divmod(i, 2)
        x_offset = (side / 2) if r % 2 else 0
        layers.append(L("polygon", x=100 + c * side * 1.2 + x_offset,
                        y=100 + r * side, w=side, h=side, fill=fill,
                        strokes=[make_stroke(rgb=stroke, weight=weight)],
                        sides=sides))
    return layers


def H(layers=None, evts=None):
    if layers is None: layers = perfect_honeycomb()
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ── K. Subtle deceptions ─────────────────────────────────────────────
def k1():
    """3 hexagons + 1 pentagon (sneaky substitute)."""
    layers = perfect_honeycomb()
    layers[3]["sides"] = 5
    return H(layers)
add("K1: 3 hexagons + 1 pentagon", k1())


def k2():
    """All hexagons same color but with one side-property mismatch."""
    layers = perfect_honeycomb()
    layers[0]["sides"] = 7  # 1 heptagon
    return H(layers)
add("K2: 1 heptagon (7 sides)", k2())


def k3():
    """Hexagons with corner radius 30."""
    layers = perfect_honeycomb()
    for l in layers:
        l["cornerRadius"] = 30  # 30/80 = 0.375 > 0.1 max_frac
    return H(layers)
add("K3: hexagons cornerRadius 30 (rounded)", k3())


def k4():
    """Hexagons all rotated 6° (under tol 5)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["rotation"] = 6
    return H(layers)
add("K4: hexagons rotation 6° (just over tol)", k4())


def k5():
    """Hexagons mirrored (scaleX=-1)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("K5: hexagons mirrored", k5())


def k6():
    """Stroke 0.3px (basically invisible)."""
    return H(perfect_honeycomb(weight=0.3))
add("K6: stroke 0.3px", k6())


def k7():
    """Near-yellow color (within tol 0.20)."""
    NEAR = (0.95, 0.85, 0.30)
    return H(perfect_honeycomb(fill=NEAR))
add("K7: near-yellow fill", k7())


def k8():
    """Stroke is dark gray (near-black, within 0.20 tol)."""
    return H(perfect_honeycomb(stroke=(0.15, 0.15, 0.15)))
add("K8: dark gray stroke (near-black)", k8())


def k9():
    """Hexagons in row (not 2x2 honeycomb)."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=100 + i * 100, y=200, w=80, h=80,
                        fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("K9: 4 hexagons in row (not 2x2)", k9())


def k10():
    """Hexagons in regular grid (no offset)."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        layers.append(L("polygon", x=100 + c * 100, y=100 + r * 100,
                        w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("K10: 2x2 grid (no honeycomb offset)", k10())


# ── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Hexagons fill alpha=0."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: hexagons alpha=0", l1())


def l2():
    """Hexagons layer.opacity=0."""
    layers = perfect_honeycomb()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("L2: hexagons layer opacity=0", l2())


def l3():
    """Hexagons fill visible=False."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L3: hexagons fill visible=False", l3())


def l4():
    """Hexagons stroke alpha=0."""
    layers = perfect_honeycomb()
    for l in layers:
        l["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("L4: hexagons stroke alpha=0", l4())


def l5():
    """Hexagons fill opacity=0.05."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L5: hexagons fill opacity 0.05", l5())


# ── M. Geometry tricks ───────────────────────────────────────────────
def m1():
    """Hexagons 1×1 degenerate."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 1
        l["h"] = 1
    return H(layers)
add("M1: hexagons 1×1", m1())


def m2():
    """Hexagons 5×5 (just under min 15)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 5
        l["h"] = 5
    return H(layers)
add("M2: hexagons 5×5 (under min size)", m2())


def m3():
    """Hexagons 16×16 (just over min)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 16
        l["h"] = 16
    return H(layers)
add("M3: hexagons 16×16 (just over min)", m3())


def m4():
    """All 4 hexagons stacked at one point."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=300, y=300, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("M4: hexagons all stacked at one point", m4())


def m5():
    """Hexagons all 0×0."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("M5: all 0×0", m5())


def m6():
    """Hexagons different sizes (not honeycomb)."""
    sizes = [40, 60, 80, 100]
    layers = []
    for i, s in enumerate(sizes):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(L("polygon", x=100 + c * 100 + x_offset, y=100 + r * 80,
                        w=s, h=s, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("M6: hexagons varying sizes", m6())


def m7():
    """Hexagons squashed (200×30)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 200
        l["h"] = 30
    return H(layers)
add("M7: hexagons squashed", m7())


# ── N. Structural tricks ─────────────────────────────────────────────
def n1():
    """4 hexagons split: 2 in frame, 2 outside."""
    layers = perfect_honeycomb()
    frame = make_frame(layers[:2], w=800, h=800)
    return make_log([frame, *layers[2:]], evt())
add("N1: 2 hexagons in frame, 2 outside", n1())


def n2():
    """Each hexagon in own frame."""
    layers = perfect_honeycomb()
    frames = [make_frame([l], w=800, h=800) for l in layers]
    return make_log(frames, evt())
add("N2: each hex in own frame", n2())


def n3():
    """Hexagons inside component."""
    layers = perfect_honeycomb()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: hexagons in component", n3())


def n4():
    """Honeycomb deep in groups."""
    layers = perfect_honeycomb()
    g3 = {"id": "g3", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    return make_log([g2], evt())
add("N4: hexagons deep nested groups", n4())


# ── O. Wrong types ───────────────────────────────────────────────────
def o1():
    """4 stars instead of polygons."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(make_layer("star", x=100 + c * 100 + x_offset,
                                  y=100 + r * 80, w=80, h=80,
                                  fill=YELLOW_HEX, points=6, innerRatio=0.4))
    return H(layers, evts=evt(polygon=0))
add("O1: stars instead of polygons", o1())


def o2():
    """4 ellipses (round, not hex)."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(L("ellipse", x=100 + c * 100 + x_offset,
                        y=100 + r * 80, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)]))
    return H(layers, evts=evt(polygon=0))
add("O2: ellipses instead of hexagons", o2())


def o3():
    """4 rectangles instead of polygons."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(L("rectangle", x=100 + c * 100 + x_offset,
                        y=100 + r * 80, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)]))
    return H(layers, evts=evt(polygon=0))
add("O3: rectangles instead of hexagons", o3())


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

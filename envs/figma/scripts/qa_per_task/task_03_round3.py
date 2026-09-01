"""Round 3 edge cases — hunt for surviving false positives in task_03."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_03" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
PETAL_COLORS = [RED, ORANGE, GREEN, CYAN, NAVY, PURPLE, PINK, MAGENTA]


def evt(ellipse=9, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):
        sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_flower(radius=200, ellipse_w=60, center_w=60):
    cx, cy = 500, 500
    center = L("ellipse", cx-center_w/2, cy-center_w/2, center_w, center_w, YELLOW)
    petals = []
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + radius * math.cos(angle) - ellipse_w/2
        y = cy + radius * math.sin(angle) - ellipse_w/2
        c = PETAL_COLORS[i]
        petals.append(L("ellipse", x, y, ellipse_w, ellipse_w, c))
    return [center, *petals]


def H(layers=None, frame_w=1000, frame_h=1000, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_flower()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Petals slightly off-radial but within tol."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8 + 0.01  # slight offset
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("K1: petals offset 0.6° (within tol)", k1())

def k2():
    """Center yellow but very close to red boundary (color tol edge)."""
    layers = perfect_flower()
    layers[0]["fills"][0]["color"] = {"r":1.0, "g":0.7, "b":0.05, "a":1.0}
    return H(layers)
add("K2: center yellow-orange (within tol)", k2())

def k3():
    """All petals rotated 1.9° (under 2° tol)."""
    layers = perfect_flower()
    for p in layers[1:]: p["rotation"] = 1.9
    return H(layers)
add("K3: petals rotated 1.9° (under tol)", k3())

def k4():
    """Petals' colors all distinct but very similar (tol edge)."""
    layers = perfect_flower()
    base_colors = [(0.5,0.5,0.5), (0.55,0.5,0.5), (0.5,0.55,0.5), (0.5,0.5,0.55),
                    (0.55,0.55,0.5), (0.55,0.5,0.55), (0.5,0.55,0.55), (0.55,0.55,0.55)]
    for i, p in enumerate(layers[1:]):
        c = base_colors[i]
        p["fills"][0]["color"] = {"r":c[0], "g":c[1], "b":c[2], "a":1.0}
    return H(layers)
add("K4: petals near-gray but distinct", k4())

def k5():
    """Center 7px non-circular (just under 8 tolerance)."""
    layers = perfect_flower()
    layers[0]["w"] = 60
    layers[0]["h"] = 53  # diff = 7, under 8 tol
    return H(layers)
add("K5: center 60×53 (within 8 tol)", k5())

def k6():
    """Petals at radius 100 instead of 200 (still radial)."""
    return H(perfect_flower(radius=100))
add("K6: petals at radius=100", k6())

def k7():
    """Petals at radius 350 (still radial, just bigger)."""
    return H(perfect_flower(radius=350), frame_w=1000, frame_h=1000)
add("K7: petals at radius=350", k7())

def k8():
    """Center duplicated (2 yellow ellipses at center, looks like 1)."""
    layers = perfect_flower()
    layers.insert(1, L("ellipse", layers[0]["x"]-2, layers[0]["y"]-2, 60, 60, YELLOW))
    return H(layers, evts=evt(ellipse=10))
add("K8: 2 yellow centers stacked", k8())

def k9():
    """Petals rotated 0° but at slightly different sizes (within tol)."""
    layers = perfect_flower()
    sizes = [60, 62, 58, 61, 59, 60, 60, 60]
    for p, s in zip(layers[1:], sizes):
        p["w"] = p["h"] = s
    return H(layers)
add("K9: petals slightly different sizes", k9())

def k10():
    """8 petals all yellow + 1 yellow center (passes count, fails distinct)."""
    layers = perfect_flower()
    for p in layers[1:]:
        p["fills"][0]["color"] = {"r":1.0, "g":0.9, "b":0.2, "a":1.0}
    return H(layers)
add("K10: all 9 yellow", k10())


# ─── L. Color subtleties ─────────────────────────────────────────────
def l1():
    """All petals fill alpha=0 (invisible)."""
    layers = perfect_flower()
    for p in layers[1:]: p["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: petals alpha=0", l1())

def l2():
    """All petals fill.visible=False."""
    layers = perfect_flower()
    for p in layers[1:]: p["fills"][0]["visible"] = False
    return H(layers)
add("L2: petals fill.visible=False", l2())

def l3():
    """All petals layer.opacity=0."""
    layers = perfect_flower()
    for p in layers[1:]: p["opacity"] = 0.0
    return H(layers)
add("L3: petals layer.opacity=0", l3())

def l4():
    """Center invisible, petals visible (the visible parts look right)."""
    layers = perfect_flower()
    layers[0]["fills"] = []
    return H(layers)
add("L4: center has no fill", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Petals overlap center entirely (radius=0)."""
    layers = [perfect_flower()[0]]
    for c in PETAL_COLORS:
        layers.append(L("ellipse", 470, 470, 60, 60, c))
    return H(layers)
add("M1: petals concentric with center", m1())

def m2():
    """Center at frame edge."""
    layers = perfect_flower()
    layers[0]["x"] = 5
    layers[0]["y"] = 5
    return H(layers)
add("M2: center at frame corner", m2())

def m3():
    """Flower size = full frame."""
    return H([L("ellipse", 0, 0, 1000, 1000, c) for c in [YELLOW, *PETAL_COLORS]])
add("M3: 9 ellipses = full frame", m3())

def m4():
    """Petals at radius 0 (tightly packed at center)."""
    layers = [perfect_flower()[0]]
    cx, cy = 500, 500
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + 5 * math.cos(angle) - 30  # tiny radius
        y = cy + 5 * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("M4: petals radius ~5px", m4())

def m5():
    """All petals at same angle (clumped on one side)."""
    layers = [perfect_flower()[0]]
    cx, cy = 500, 500
    for i in range(8):
        x = cx + 200 - 30 + i*2  # all on right
        y = cy - 30 + i*2
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("M5: petals clumped on right side", m5())

def m6():
    """Frame rotated 90°."""
    layers = perfect_flower()
    frame = make_frame(layers, w=1000, h=1000)
    frame["rotation"] = 90
    return make_log([frame], evt())
add("M6: frame rotated 90°", m6())

def m7():
    """Petals all rotated by their angle (so they all face center)."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        l = L("ellipse", x, y, 60, 60, PETAL_COLORS[i])
        l["rotation"] = math.degrees(angle)
        layers.append(l)
    return H(layers)
add("M7: petals rotated by their angle", m7())

def m8():
    """All petals scaleX=-1."""
    layers = perfect_flower()
    for p in layers[1:]: p["scaleX"] = -1
    return H(layers)
add("M8: petals scaleX=-1", m8())


# ─── N. Hierarchy / structural tricks ────────────────────────────────
def n1():
    """Petals in group, center on page."""
    layers = perfect_flower()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers[1:]}
    frame = make_frame([layers[0], g], w=1000, h=1000)
    return make_log([frame], evt())
add("N1: petals in group, center sibling", n1())

def n2():
    """Ellipses split: center in frame_a, petals in frame_b."""
    layers = perfect_flower()
    f1 = make_frame([layers[0]], w=500, h=500)
    f2 = make_frame(layers[1:], w=1000, h=1000)
    return make_log([f1, f2], evt())
add("N2: center+petals in 2 different frames", n2())

def n3():
    """Each ellipse in own group inside frame."""
    layers = perfect_flower()
    groups = []
    for l in layers:
        g = {"id":f"g_{l['id']}","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[l]}
        groups.append(g)
    frame = make_frame(groups, w=1000, h=1000)
    return make_log([frame], evt())
add("N3: each ellipse in own group", n3())


# ─── O. Wrong shape types substituted ────────────────────────────────
def o1():
    """8 stars + 1 ellipse center."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(make_layer("star", x=x, y=y, w=60, h=60, fill=PETAL_COLORS[i], points=5, innerRatio=0.4))
    sem = evt(ellipse=1, extras=[make_event("tool_change", before="ellipse", after="star")] +
              [make_event("create_star") for _ in range(8)])
    return H(layers, evts=sem)
add("O1: 1 ellipse + 8 stars", o1())

def o2():
    """8 polygons + 1 ellipse center."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(make_layer("polygon", x=x, y=y, w=60, h=60, fill=PETAL_COLORS[i], sides=6))
    sem = evt(ellipse=1, extras=[make_event("tool_change", before="ellipse", after="polygon")] +
              [make_event("create_polygon") for _ in range(8)])
    return H(layers, evts=sem)
add("O2: 1 ellipse + 8 polygons", o2())

def o3():
    """All ellipses replaced by rectangles with cornerRadius."""
    layers = perfect_flower()
    new_layers = []
    for l in layers:
        new_l = make_layer("rectangle", x=l["x"], y=l["y"], w=l["w"], h=l["h"],
                           fill=tuple(l["fills"][0]["color"][k] for k in ("r","g","b")),
                           cornerRadius=l["w"]/2)
        new_layers.append(new_l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 9)
    return H(new_layers, evts=sem)
add("O3: rectangles+cornerRadius (no ellipses)", o3())


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

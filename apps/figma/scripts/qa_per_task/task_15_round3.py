"""Round 3 — novel-deception edge cases for task 15."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_15_cloud_union as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(ellipse=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):
        sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_cloud():
    layers = []
    sizes = [(180, 180), (220, 220), (200, 200), (160, 160)]
    xs = [400, 540, 680, 820]
    y = 300
    for (w, h), x in zip(sizes, xs):
        l = L("ellipse", x, y, w, h, WHITE)
        l["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=1)]
        layers.append(l)
    return layers


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_cloud()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Each ellipse rotated 1° (under tol=2)."""
    layers = perfect_cloud()
    for l in layers:
        l["rotation"] = 1
    return H(layers)
add("K1: ellipses rotated 1° (under tol)", k1())

def k2():
    """All ellipses share bottom edge but cross to make 2x2 grid (no overlap)."""
    layers = perfect_cloud()
    layers[0]["x"] = 100; layers[0]["y"] = 200
    layers[1]["x"] = 700; layers[1]["y"] = 200
    layers[2]["x"] = 100; layers[2]["y"] = 480  # different bottom
    layers[3]["x"] = 700; layers[3]["y"] = 480
    return H(layers)
add("K2: 2x2 grid (with bottom mismatch)", k2())

def k3():
    """Strokes 1.9px (just over tol=1)."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=1.9)]
    return H(layers)
add("K3: strokes 1.9px (within tol=1)", k3())

def k4():
    """White at #fff but with alpha=0.3."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.3
    return H(layers)
add("K4: alpha=0.3 (translucent)", k4())

def k5():
    """1 ellipse opacity=0.4 (just under min=0.5)."""
    layers = perfect_cloud()
    layers[0]["opacity"] = 0.4
    return H(layers)
add("K5: 1 ellipse opacity=0.4", k5())

def k6():
    """Reverse z-order."""
    layers = perfect_cloud()[::-1]
    return H(layers)
add("K6: reverse z-order", k6())

def k7():
    """Ellipses very tightly nested (concentric)."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] = 600; l["y"] = 400  # all stacked
    return H(layers)
add("K7: ellipses concentric/overlapping", k7())

def k8():
    """Cloud ellipses + 1 extra small dot in center."""
    layers = perfect_cloud()
    layers.append(L("ellipse", 600, 400, 30, 30, WHITE,
                     strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)]))
    return H(layers, evts=evt(ellipse=5))
add("K8: 5 ellipses (extra dot)", k8())

def k9():
    """Cloud ellipses with cornerRadius (no-op for ellipse)."""
    layers = perfect_cloud()
    for l in layers:
        l["cornerRadius"] = 100
    return H(layers)
add("K9: cornerRadius=100 (no-op for ellipse)", k9())

def k10():
    """1 ellipse rotated 90° (no visual change for circle)."""
    layers = perfect_cloud()
    layers[1]["rotation"] = 90
    return H(layers)
add("K10: 1 ellipse rotated 90°", k10())


# ─── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """All fills alpha=0."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: alpha=0 (all)", l1())

def l2():
    """All visible=False."""
    layers = perfect_cloud()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L2: layer visible=False", l2())

def l3():
    """All opacity=0."""
    layers = perfect_cloud()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("L3: layer opacity=0", l3())

def l4():
    """All fills.visible=False."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("L4: fill visible=False", l4())

def l5():
    """All ellipses image fills."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("L5: image fills", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All ellipses same size."""
    layers = perfect_cloud()
    for l in layers:
        l["w"] = 200; l["h"] = 200
    return H(layers)
add("M1: all 200×200 (uniform)", m1())

def m2():
    """Ellipses far apart (no overlap)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*350
    return H(layers)
add("M2: ellipses far apart", m2())

def m3():
    """All ellipses degenerate (1×1)."""
    layers = perfect_cloud()
    for l in layers:
        l["w"] = 1; l["h"] = 1
    return H(layers)
add("M3: all 1×1 degenerate", m3())

def m4():
    """All = full frame size."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] = 0; l["y"] = 0; l["w"] = 1280; l["h"] = 832
    return H(layers)
add("M4: ellipses = full frame", m4())

def m5():
    """Ellipses scattered to 4 corners."""
    layers = perfect_cloud()
    positions = [(100, 100), (1000, 100), (100, 700), (1000, 700)]
    for l, (x, y) in zip(layers, positions):
        l["x"] = x; l["y"] = y
    return H(layers)
add("M5: 4 corner positions", m5())

def m6():
    """All ellipses flipped X."""
    layers = perfect_cloud()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("M6: all flipped X", m6())

def m7():
    """Cloud rotated 90° as a group (vertical cloud)."""
    layers = perfect_cloud()
    for l in layers:
        l["x"], l["y"] = l["y"], l["x"]
    return H(layers)
add("M7: cloud arranged vertically", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """No frame."""
    return H(perfect_cloud(), in_frame=False)
add("N1: no frame", n1())

def n2():
    """Each in own frame."""
    layers = perfect_cloud()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N2: each in own frame", n2())

def n3():
    """In component."""
    layers = perfect_cloud()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: in component", n3())

def n4():
    """3 in frame, 1 outside."""
    layers = perfect_cloud()
    frame = make_frame(layers[:3], w=1280, h=832)
    return make_log([frame, layers[3]], evt())
add("N4: 3 in frame, 1 outside", n4())


# ─── O. Wrong types ──────────────────────────────────────────────────
def o1():
    """4 polygons (sides=10) instead of ellipses."""
    layers = []
    sizes = [180, 220, 200, 160]
    xs = [400, 540, 680, 820]
    for size, x in zip(sizes, xs):
        l = make_layer("polygon", x=x, y=300, w=size, h=size, fill=WHITE, sides=10,
                       strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_polygon")]*4))
add("O1: 4 polygons sides=10 (not ellipses)", o1())

def o2():
    """4 rectangles."""
    layers = []
    sizes = [180, 220, 200, 160]
    xs = [400, 540, 680, 820]
    for size, x in zip(sizes, xs):
        l = make_layer("rectangle", x=x, y=300, w=size, h=size, fill=WHITE,
                       strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]*4))
add("O2: 4 rectangles instead", o2())

def o3():
    """3 ellipses + 1 star."""
    layers = perfect_cloud()[:3]
    star = make_layer("star", x=820, y=300, w=160, h=160, fill=WHITE, points=8,
                      innerRatio=0.7,
                      strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
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

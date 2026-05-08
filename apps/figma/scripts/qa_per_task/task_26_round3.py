"""Round 3 novel deceptions for task 26 — 5 same-size squares brand-color row."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, WHITE, RED, GREEN, PURPLE, GOLD, CYAN, PINK,
)
from tasks import task_26_color_variable_card as t
T = t.task

BRAND_PRIMARY  = (0.20, 0.45, 0.85)
BRAND_RED      = (0.90, 0.15, 0.20)
BRAND_GREEN    = (0.15, 0.70, 0.40)
BRAND_YELLOW   = (1.00, 0.85, 0.10)
BRAND_PURPLE   = (0.55, 0.30, 0.80)


def evt(rect=5, set_fill=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_squares(n=5, w=80, h=80, gap=16, colors=None, y=400, x0=200):
    colors = colors or [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    layers = []
    for i in range(n):
        layers.append(L("rectangle", x0+i*(w+gap), y, w, h, colors[i % len(colors)]))
    return layers


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_squares()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Squares rotated 1.9°."""
    layers = perfect_squares()
    for l in layers:
        l["rotation"] = 1.9
    return H(layers)
add("K1: rotated 1.9° (under tol)", k1())

def k2():
    """Squares rotated 3°."""
    layers = perfect_squares()
    for l in layers:
        l["rotation"] = 3
    return H(layers)
add("K2: rotated 3° (over tol)", k2())

def k3():
    """Squares 80×84 (h diff 4 = at LayerIsSquare tol)."""
    return H(perfect_squares(w=80, h=84))
add("K3: 80×84 (at square tol)", k3())

def k4():
    """Squares 80×85 (just over square tol)."""
    return H(perfect_squares(w=80, h=85))
add("K4: 80×85 (over square tol)", k4())

def k5():
    """y diff 3px (at tol edge)."""
    layers = perfect_squares()
    layers[2]["y"] += 3
    return H(layers)
add("K5: y diff 3px (at tol)", k5())

def k6():
    """Gap variance 7px (within 8 tol)."""
    layers = []
    cur = 200
    gaps = [16, 16, 23, 16]  # one is 7px over
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", cur, 400, 80, 80, c))
        if i < 4:
            cur += 80 + gaps[i]
    return H(layers)
add("K6: gap +7px (within tol)", k6())

def k7():
    """5 squares with cornerRadius=32 (frac=0.4 at threshold)."""
    layers = perfect_squares()
    for l in layers:
        l["cornerRadius"] = 32
    return H(layers)
add("K7: cornerRadius frac 0.4 (boundary)", k7())

def k8():
    """5 squares with cornerRadius=40 (frac=0.5 over)."""
    layers = perfect_squares()
    for l in layers:
        l["cornerRadius"] = 40
    return H(layers)
add("K8: cornerRadius frac 0.5 (over)", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    layers = perfect_squares()
    layers[0]["visible"] = False
    return H(layers)
add("L1: 1 square visible=False", l1())

def l2():
    layers = perfect_squares()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L2: 1 fill.visible=False", l2())

def l3():
    layers = perfect_squares()
    for l in layers:
        l["opacity"] = 0.4
    return H(layers)
add("L3: opacity=0.4 on all", l3())

def l4():
    layers = perfect_squares()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L4: 1 alpha=0", l4())

def l5():
    """All fills opacity=0.4."""
    layers = perfect_squares()
    for l in layers:
        l["fills"][0]["opacity"] = 0.4
    return H(layers)
add("L5: all fillOpacity=0.4", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """All squares piled at center."""
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for c in colors:
        layers.append(L("rectangle", 600, 400, 80, 80, c))
    return H(layers)
add("M1: 5 piled at center", m1())

def m2():
    """5 squares filling entire frame."""
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for c in colors:
        layers.append(L("rectangle", 0, 0, 1280, 832, c))
    return H(layers)
add("M2: 5 = full frame each", m2())

def m3():
    """Squares with random vivid colors (still distinct)."""
    layers = perfect_squares(colors=[(1,0,0),(0,1,0),(0,0,1),(1,1,0),(1,0,1)])
    return H(layers)
add("M3: vivid colors (still distinct)", m3())

def m4():
    """5 squares but middle 1 is different size."""
    layers = perfect_squares()
    layers[2]["w"] = 120; layers[2]["h"] = 120
    return H(layers)
add("M4: 1 oversized middle square", m4())

def m5():
    """5 squares all sized 80×80 but one has different color twice."""
    layers = perfect_squares(colors=[BRAND_PRIMARY, BRAND_PRIMARY, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE])
    return H(layers)
add("M5: 4 distinct colors (1 duplicated)", m5())

def m6():
    """5 squares stacked diagonally."""
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for i, c in enumerate(colors):
        layers.append(L("rectangle", 200+i*96, 200+i*60, 80, 80, c))
    return H(layers)
add("M6: diagonal cascade", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    layers = perfect_squares()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N1: in component", n1())

def n2():
    layers = perfect_squares()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("N2: in instance", n2())

def n3():
    """Each square in its own frame."""
    layers = perfect_squares()
    frames = [make_frame([l], w=200, h=200, x=i*220) for i, l in enumerate(layers)]
    return make_log(frames, evt())
add("N3: each square in own frame", n3())

def n4():
    """4-deep nested."""
    layers = perfect_squares()
    f4 = make_frame(layers, w=1280, h=832)
    f3 = make_frame([f4], w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("N4: 4-deep nested", n4())

def n5():
    """In group in frame."""
    layers = perfect_squares()
    g = {"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("N5: in group in frame", n5())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for i, c in enumerate(colors):
        layers.append(make_layer("ellipse", x=200+i*96, y=400, w=80, h=80, fill=c))
    return H(layers, evts=evt(rect=0))
add("O1: 5 ellipses", o1())

def o2():
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for i, c in enumerate(colors):
        layers.append(make_layer("star", x=200+i*96, y=400, w=80, h=80,
                                  fill=c, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0))
add("O2: 5 stars", o2())

def o3():
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for i, c in enumerate(colors):
        layers.append(make_layer("polygon", x=200+i*96, y=400, w=80, h=80,
                                  fill=c, sides=4))
    return H(layers, evts=evt(rect=0))
add("O3: 5 polygons", o3())

def o4():
    """3 rects + 2 ellipses."""
    layers = []
    colors = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE]
    for i, c in enumerate(colors[:3]):
        layers.append(L("rectangle", 200+i*96, 400, 80, 80, c))
    for i, c in enumerate(colors[3:]):
        layers.append(make_layer("ellipse", x=200+(i+3)*96, y=400, w=80, h=80, fill=c))
    return H(layers, evts=evt(rect=3))
add("O4: 3 rects + 2 ellipses", o4())


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

"""Round 3 — novel deception cases for task 19 (padlock)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_19" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
BODY_X, BODY_Y, BODY_W, BODY_H = 540, 360, 200, 160
SHACKLE_X, SHACKLE_Y, SHACKLE_W, SHACKLE_H = 580, 240, 120, 130
KEY_X, KEY_Y, KEY_W, KEY_H = 625, 420, 30, 30


def evt(rect=1, vector=1, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_padlock():
    body = L("rectangle", BODY_X, BODY_Y, BODY_W, BODY_H, DARK_GRAY, cornerRadius=12)
    shackle = L("vector", SHACKLE_X, SHACKLE_Y, SHACKLE_W, SHACKLE_H, fill=None,
                strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    key = L("ellipse", KEY_X, KEY_Y, KEY_W, KEY_H, BLACK)
    return [body, shackle, key]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ──────────────────────────────────────────
def k1():
    """Body cornerRadius=8 (tolerance 4 means 12±4 = [8..16] passes; just at edge)."""
    layers = perfect_padlock()
    layers[0]["cornerRadius"] = 7  # 5 below 12
    return H(layers)
add("K1: body cornerRadius=7 (under tol)", k1())

def k2():
    """Shackle stroke 11 (under tol of 14±2 = [12..16])."""
    layers = perfect_padlock()
    layers[1]["strokes"][0]["weight"] = 11
    return H(layers)
add("K2: shackle stroke 11 (under tol)", k2())

def k3():
    """Body color = (0.55, 0.55, 0.55) — exactly at color tolerance edge."""
    layers = perfect_padlock()
    layers[0]["fills"][0]["color"] = {"r":0.56, "g":0.56, "b":0.56, "a":1.0}
    return H(layers)
add("K3: body color slightly outside dark gray tol", k3())

def k4():
    """Body cornerRadius=99 (basically circular)."""
    layers = perfect_padlock()
    layers[0]["cornerRadius"] = 99
    return H(layers)
add("K4: body cornerRadius=99 (circular)", k4())

def k5():
    """Keyhole 75% of body width (not 'small')."""
    layers = perfect_padlock()
    layers[2]["w"] = 80; layers[2]["h"] = 80
    layers[2]["x"] = 600; layers[2]["y"] = 400
    return H(layers)
add("K5: keyhole 80×80 (large)", k5())

def k6():
    """Shackle drawn BELOW body."""
    layers = perfect_padlock()
    layers[1]["y"] = BODY_Y + BODY_H  # below
    return H(layers)
add("K6: shackle below body", k6())


# ─── L. Visibility tricks ──────────────────────────────────────────
def l1():
    """Body fill alpha=0."""
    layers = perfect_padlock()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: body fill alpha=0", l1())

def l2():
    """Keyhole fill visible=False."""
    layers = perfect_padlock()
    layers[2]["fills"][0]["visible"] = False
    return H(layers)
add("L2: keyhole fill visible=False", l2())

def l3():
    """All layers opacity=0."""
    layers = perfect_padlock()
    for l in layers: l["opacity"] = 0
    return H(layers)
add("L3: all opacity=0", l3())

def l4():
    """Shackle stroke visible=False."""
    layers = perfect_padlock()
    layers[1]["strokes"][0]["visible"] = False
    return H(layers)
add("L4: shackle stroke visible=False", l4())

def l5():
    """Shackle stroke alpha=0.05 (rendering thresh 0.5)."""
    layers = perfect_padlock()
    layers[1]["strokes"][0]["paint"]["color"]["a"] = 0.05
    return H(layers)
add("L5: shackle stroke alpha=0.05", l5())


# ─── M. Geometry tricks ────────────────────────────────────────────
def m1():
    """Body fully covers frame, keyhole at center."""
    layers = perfect_padlock()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    layers[2]["x"] = 625; layers[2]["y"] = 401
    return H(layers)
add("M1: body = full frame", m1())

def m2():
    """All shapes at same point (1px each)."""
    layers = perfect_padlock()
    for l in layers:
        l["x"] = 600; l["y"] = 400; l["w"] = 1; l["h"] = 1
    return H(layers)
add("M2: all 1×1 piled", m2())

def m3():
    """Shackle has rotation 180 (upside down U)."""
    layers = perfect_padlock()
    layers[1]["rotation"] = 180
    return H(layers)
add("M3: shackle rotated 180°", m3())

def m4():
    """Keyhole far away from body, even though geometrically overlap."""
    layers = perfect_padlock()
    layers[2]["x"] = BODY_X - 200; layers[2]["y"] = BODY_Y - 200
    return H(layers)
add("M4: keyhole 200px from body", m4())

def m5():
    """Body 50px wide, ratio test"""
    layers = perfect_padlock()
    layers[0]["w"] = 50
    layers[2]["x"] = BODY_X + 5; layers[2]["y"] = BODY_Y + 50
    layers[2]["w"] = 20; layers[2]["h"] = 20
    return H(layers)
add("M5: body 50 wide", m5())

def m6():
    """Body, shackle, keyhole all at frame top-left."""
    layers = perfect_padlock()
    for l in layers:
        l["x"] = 0; l["y"] = 0
    return H(layers)
add("M6: all at top-left corner", m6())


# ─── N. Structural tricks ──────────────────────────────────────────
def n1():
    """Body in component, others in frame."""
    body = perfect_padlock()[0]
    others = perfect_padlock()[1:]
    component = {"id":"comp1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children":[body]}
    frame = make_frame(others, w=1280, h=832)
    return make_log([component, frame], evt())
add("N1: body in component, rest in frame", n1())

def n2():
    """Each in own frame."""
    layers = perfect_padlock()
    f1 = make_frame([layers[0]], w=400, h=400)
    f2 = make_frame([layers[1]], w=400, h=400, x=400)
    f3 = make_frame([layers[2]], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("N2: 3 shapes in 3 separate frames", n2())

def n3():
    """All 3 in nested 4-deep groups."""
    layers = perfect_padlock()
    g = layers
    for _ in range(4):
        g = [{"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=1280, h=832)
    return make_log([frame], evt())
add("N3: 4-deep nested groups", n3())

def n4():
    """3 padlocks stacked"""
    layers = perfect_padlock() * 3  # 9 layers total
    return H(layers, evts=evt(rect=3, vector=3, ellipse=3))
add("N4: 3 padlocks in same frame", n4())


# ─── O. Wrong shape types ─────────────────────────────────────────
def o1():
    """Body = polygon (4-sided)."""
    layers = perfect_padlock()
    layers[0] = L("polygon", BODY_X, BODY_Y, BODY_W, BODY_H, DARK_GRAY, sides=4)
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]))
add("O1: body as polygon", o1())

def o2():
    """Shackle = ellipse instead of vector."""
    layers = perfect_padlock()
    layers[1] = L("ellipse", SHACKLE_X, SHACKLE_Y, SHACKLE_W, SHACKLE_H, DARK_GRAY)
    return H(layers, evts=evt(vector=0, ellipse=2))
add("O2: shackle is ellipse", o2())

def o3():
    """Keyhole = rectangle."""
    layers = perfect_padlock()
    layers[2] = L("rectangle", KEY_X, KEY_Y, KEY_W, KEY_H, BLACK)
    return H(layers, evts=evt(rect=2, ellipse=0))
add("O3: keyhole is rectangle", o3())

def o4():
    """Body=star, shackle=star, keyhole=star (everything's a star)."""
    layers = []
    for x, y, w, h, fill in [(BODY_X,BODY_Y,BODY_W,BODY_H,DARK_GRAY),
                              (SHACKLE_X,SHACKLE_Y,SHACKLE_W,SHACKLE_H,DARK_GRAY),
                              (KEY_X,KEY_Y,KEY_W,KEY_H,BLACK)]:
        layers.append(make_layer("star", x=x, y=y, w=w, h=h, fill=fill,
                                 points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0, vector=0, ellipse=0,
                              extras=[make_event("create_star")]*3))
add("O4: 3 stars instead of padlock", o4())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        if flag: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95): {fp_count}/{len(CASES)}")

"""Round 3 — novel deception cases for task 40 (toggle switch)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_drop_shadow, make_stroke,
    score_task, GREEN, WHITE, NAVY, RED, ORANGE, YELLOW, BLACK,
)
from tasks import task_40_toggle_switch as t
T = t.task

GREEN_RGB = (0.20, 0.78, 0.35)
WHITE_RGB = (1.0, 1.0, 1.0)


def evt(rect=1, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_toggle():
    pill = L("rectangle", 400, 300, 80, 40, GREEN_RGB, cornerRadius=999)
    thumb = L("ellipse", 442, 305, 30, 30, WHITE_RGB,
              effects=[make_drop_shadow(y=2, blur=4)])
    return [pill, thumb]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_toggle()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Pill rotated 1.5° (within tol)."""
    layers = perfect_toggle()
    layers[0]["rotation"] = 1.5
    return H(layers)
add("K1: pill rotated 1.5° (within tol)", k1())

def k2():
    """Thumb at exact left edge, NOT right."""
    layers = perfect_toggle()
    layers[1] = L("ellipse", 405, 305, 30, 30, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("K2: thumb at left edge", k2())

def k3():
    """Thumb at center of pill."""
    layers = perfect_toggle()
    layers[1] = L("ellipse", 425, 305, 30, 30, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("K3: thumb in middle", k3())

def k4():
    """Pill green near boundary tolerance."""
    layers = perfect_toggle()
    layers[0]["fills"][0]["color"] = {"r":0.05, "g":0.62, "b":0.20, "a":1}  # darker green
    return H(layers)
add("K4: pill near-green boundary", k4())

def k5():
    """Pill cornerRadius=15 (just at min boundary)."""
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = 15
    return H(layers)
add("K5: pill cornerRadius=15 (boundary)", k5())

def k6():
    """Pill cornerRadius=14 (just under min)."""
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = 14
    return H(layers)
add("K6: pill cornerRadius=14 (under min)", k6())

def k7():
    """Drop shadow alpha=0.04 (just under min)."""
    layers = perfect_toggle()
    layers[1]["effects"][0]["color"]["a"] = 0.04
    return H(layers)
add("K7: shadow alpha=0.04 (under min)", k7())

def k8():
    """Thumb cornerRadius=15 (looks like rounded square not circle)."""
    layers = perfect_toggle()
    # but Layer is still ellipse — should pass
    layers[1]["cornerRadius"] = 15
    return H(layers)
add("K8: thumb cornerRadius=15 (cosmetic)", k8())

def k9():
    """Thumb 4x4 (very small)."""
    layers = perfect_toggle()
    layers[1] = L("ellipse", 470, 313, 4, 4, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("K9: thumb 4x4 (under min)", k9())

def k10():
    """Pill corner radius=999 but as a 4-tuple."""
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = [999, 999, 999, 999]  # all corners
    return H(layers)
add("K10: pill cornerRadius as 4-tuple", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Thumb fill alpha=0."""
    layers = perfect_toggle()
    layers[1]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: thumb fill alpha=0", l1())

def l2():
    """Thumb visible=False."""
    layers = perfect_toggle()
    layers[1]["visible"] = False
    return H(layers)
add("L2: thumb visible=False", l2())

def l3():
    """Pill fill visible=False."""
    layers = perfect_toggle()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L3: pill fill visible=False", l3())

def l4():
    """Drop shadow visible=False."""
    layers = perfect_toggle()
    layers[1]["effects"][0]["visible"] = False
    return H(layers)
add("L4: shadow visible=False", l4())

def l5():
    """Drop shadow blur=0 (effectively no shadow)."""
    layers = perfect_toggle()
    layers[1]["effects"][0]["blur"] = 0
    layers[1]["effects"][0]["x"] = 0
    layers[1]["effects"][0]["y"] = 0
    return H(layers)
add("L5: drop shadow blur=0 offset=0,0 (no shadow)", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Thumb same size as pill."""
    layers = perfect_toggle()
    layers[1] = L("ellipse", 400, 300, 80, 40, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("M1: thumb same size as pill", m1())

def m2():
    """Thumb wider than pill."""
    layers = perfect_toggle()
    layers[1] = L("ellipse", 350, 305, 200, 200, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("M2: thumb 200x200 wider than pill", m2())

def m3():
    """Pill very thin (cornerRadius=999 but 80x4 - looks like line)."""
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 4, GREEN_RGB, cornerRadius=999)
    return H(layers)
add("M3: pill 80x4 (thin)", m3())

def m4():
    """Pill perfectly square (no aspect ratio > 1.2)."""
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 80, GREEN_RGB, cornerRadius=999)
    return H(layers)
add("M4: pill 80x80 (square)", m4())

def m5():
    """Both shapes at same position with same size."""
    layers = [L("rectangle", 400, 300, 80, 40, GREEN_RGB, cornerRadius=999),
              L("ellipse", 400, 300, 80, 40, WHITE_RGB,
                effects=[make_drop_shadow(y=2, blur=4)])]
    return H(layers)
add("M5: pill and thumb same bbox", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Pill in frame, thumb outside frame on page."""
    layers = perfect_toggle()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, layers[1]], evt())
add("N1: thumb outside frame", n1())

def n2():
    """Pill and thumb in different frames."""
    layers = perfect_toggle()
    f1 = make_frame([layers[0]], w=1280, h=832)
    f2 = make_frame([layers[1]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("N2: pill/thumb in different frames", n2())

def n3():
    """All in component."""
    layers = perfect_toggle()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N3: all in component", n3())

def n4():
    """Each in own frame."""
    layers = perfect_toggle()
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("N4: each in own frame", n4())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Pill is actually a polygon (hexagon)."""
    layers = perfect_toggle()
    layers[0] = make_layer("polygon", x=400, y=300, w=80, h=40,
                            fill=GREEN_RGB, sides=6, cornerRadius=999)
    return H(layers, evts=evt(rect=0))
add("O1: pill is hexagon", o1())

def o2():
    """Thumb is a star."""
    layers = perfect_toggle()
    layers[1] = make_layer("star", x=442, y=305, w=30, h=30,
                            fill=WHITE_RGB, points=5, innerRatio=0.4,
                            effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers, evts=evt(ellipse=0))
add("O2: thumb is star", o2())

def o3():
    """Both shapes are vectors."""
    layers = [L("vector", 400, 300, 80, 40, GREEN_RGB, cornerRadius=999),
              L("vector", 442, 305, 30, 30, WHITE_RGB,
                effects=[make_drop_shadow(y=2, blur=4)])]
    return H(layers, evts=evt(rect=0, ellipse=0))
add("O3: both are vectors", o3())


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

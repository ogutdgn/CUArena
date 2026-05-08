"""Round 3 — novel deception cases for task 41 (search bar)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, RED, GREEN, YELLOW, ORANGE, WHITE, BLACK,
)
from tasks import task_41_search_bar as t
T = t.task

LIGHT_GRAY = (0.95, 0.95, 0.95)
GRAY_STROKE = (0.5, 0.5, 0.5)


def evt(rect=1, ellipse=3, line=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("tool_change", before="ellipse", after="line")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(line):    sem.append(make_event("create_line"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_search():
    bar = L("rectangle", 200, 300, 320, 48, LIGHT_GRAY, cornerRadius=24)
    glass = L("ellipse", 215, 312, 24, 24, None,
              strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    handle = L("line", 232, 332, 12, 12, None,
               strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    dot1 = L("ellipse", 270, 320, 8, 8, None,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    dot2 = L("ellipse", 285, 320, 8, 8, None,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return [bar, glass, handle, dot1, dot2]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_search()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Bar 308x48 (12px under)."""
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 308, 48, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("K1: bar 308x48 (within tol)", k1())

def k2():
    """Bar cornerRadius=20 (boundary)."""
    layers = perfect_search()
    layers[0]["cornerRadius"] = 20
    return H(layers)
add("K2: bar cornerRadius=20 (boundary)", k2())

def k3():
    """Bar cornerRadius=18 (just under min)."""
    layers = perfect_search()
    layers[0]["cornerRadius"] = 18
    return H(layers)
add("K3: bar cornerRadius=18 (under)", k3())

def k4():
    """Bar rotated 1.5° (within tol)."""
    layers = perfect_search()
    layers[0]["rotation"] = 1.5
    return H(layers)
add("K4: bar rotated 1.5° (within tol)", k4())

def k5():
    """Bar light gray (0.85 channel) — boundary."""
    layers = perfect_search()
    layers[0]["fills"][0]["color"] = {"r":0.85, "g":0.85, "b":0.85, "a":1}
    return H(layers)
add("K5: bar fills 0.85 gray (boundary)", k5())

def k6():
    """Magnifier stroke alpha=0.05 (just at min)."""
    layers = perfect_search()
    for arc in layers[1:]:
        arc["strokes"][0]["paint"]["color"]["a"] = 0.05
    return H(layers)
add("K6: stroke alpha=0.05 (at min)", k6())

def k7():
    """Stroke weight 1.05 (just at min)."""
    layers = perfect_search()
    for arc in layers[1:]:
        arc["strokes"][0]["weight"] = 1.05
    return H(layers)
add("K7: stroke weight 1.05 (at boundary)", k7())

def k8():
    """Bar very wide (full frame width-ish)."""
    layers = perfect_search()
    layers[0] = L("rectangle", 0, 300, 1280, 48, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("K8: bar = frame width", k8())

def k9():
    """1 dot + 1 magnifier (only 2 ellipses)."""
    layers = perfect_search()[:4]  # bar + glass + handle + 1 dot
    return H(layers, evts=evt(ellipse=2))
add("K9: only 2 ellipses (1 dot)", k9())

def k10():
    """Magnifier strokeAlignment=outside (visual offset)."""
    layers = perfect_search()
    for arc in layers[1:]:
        arc["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("K10: stroke alignment=outside", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Bar fill alpha=0."""
    layers = perfect_search()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: bar fill alpha=0", l1())

def l2():
    """Bar layer visible=False."""
    layers = perfect_search()
    layers[0]["visible"] = False
    return H(layers)
add("L2: bar visible=False", l2())

def l3():
    """All ellipses stroke alpha=0."""
    layers = perfect_search()
    for arc in layers[1:]:
        if arc["type"] == "ellipse":
            arc["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("L3: all ellipse strokes alpha=0", l3())

def l4():
    """Line stroke weight 0."""
    layers = perfect_search()
    layers[2]["strokes"][0]["weight"] = 0
    return H(layers)
add("L4: line stroke weight 0", l4())

def l5():
    """Bar fill opacity 0.1 (very transparent)."""
    layers = perfect_search()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("L5: bar fill opacity=0.1", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Magnifier same as bar (both 320x48)."""
    layers = perfect_search()
    layers[1] = L("ellipse", 200, 300, 320, 48, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("M1: magnifier 320x48 (same as bar)", m1())

def m2():
    """Bar inside magnifier (reversed sizes)."""
    layers = perfect_search()
    layers[0] = L("rectangle", 215, 312, 30, 24, LIGHT_GRAY, cornerRadius=12)
    layers[1] = L("ellipse", 100, 200, 500, 300, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("M2: magnifier larger than bar", m2())

def m3():
    """Dots all 200x200 (bigger than bar)."""
    layers = perfect_search()
    layers[3] = L("ellipse", 100, 100, 200, 200, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    layers[4] = L("ellipse", 100, 400, 200, 200, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("M3: dots 200x200 (huge)", m3())

def m4():
    """Bar 800x32 (very wide)."""
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 800, 32, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("M4: bar 800x32", m4())

def m5():
    """All shapes piled at one point."""
    layers = perfect_search()
    for l in layers:
        l["x"] = 500; l["y"] = 400; l["w"] = 50; l["h"] = 50
    return H(layers)
add("M5: all piled at one point", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Bar in frame, icons outside frame."""
    layers = perfect_search()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("N1: icons outside frame", n1())

def n2():
    """Each shape in own frame."""
    layers = perfect_search()
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("N2: each in own frame", n2())

def n3():
    """All in component."""
    layers = perfect_search()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N3: all in component", n3())

def n4():
    """Icons in group, bar outside."""
    layers = perfect_search()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers[1:]}
    frame = make_frame([layers[0], group], w=1280, h=832)
    return make_log([frame], evt())
add("N4: icons in group, bar outside", n4())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Bar is ellipse."""
    layers = perfect_search()
    layers[0] = L("ellipse", 200, 300, 320, 48, LIGHT_GRAY)
    return H(layers, evts=evt(rect=0, ellipse=4))
add("O1: bar is ellipse", o1())

def o2():
    """Magnifier is rectangle."""
    layers = perfect_search()
    layers[1] = L("rectangle", 215, 312, 24, 24, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=2, ellipse=2))
add("O2: magnifier is rectangle", o2())

def o3():
    """Line is vector (pen)."""
    layers = perfect_search()
    layers[2] = L("vector", 232, 332, 12, 12, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(line=0))
add("O3: line is vector (pen)", o3())


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

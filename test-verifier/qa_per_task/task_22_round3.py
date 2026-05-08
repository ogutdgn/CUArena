"""Round 3 novel deceptions for task 22 — 30 cases probing the gaps not covered
by the 100-case extended battery. Anything ≥0.95 that should fail is a strict FP."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE,
)
from tasks import task_22_tag_pills as t
T = t.task

PASTEL_PINK   = (0.95, 0.70, 0.75)
PASTEL_GREEN  = (0.70, 0.95, 0.75)
PASTEL_BLUE   = (0.70, 0.80, 0.95)
PASTEL_YELLOW = (0.95, 0.95, 0.70)


def evt(rect=4, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pills(n=4, w=120, h=40, gap=8, radius=999, colors=None, y=300, x0=100):
    colors = colors or [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW]
    layers = []
    for i in range(n):
        layers.append(L("rectangle", x0 + i * (w + gap), y, w, h,
                        colors[i % len(colors)], cornerRadius=radius))
    return layers


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_pills()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Pills rotated 1.5° (under 2° tolerance)."""
    layers = perfect_pills()
    for l in layers:
        l["rotation"] = 1.5
    return H(layers)
add("K1: pills rotated 1.5° (under tol)", k1())

def k2():
    """Pills rotated 4° (above 2° tolerance, should fail)."""
    layers = perfect_pills()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("K2: pills rotated 4° (above tol)", k2())

def k3():
    """One pill rotated 3° in opposite direction."""
    layers = perfect_pills()
    layers[1]["rotation"] = -3
    return H(layers)
add("K3: 1 pill rotated -3°", k3())

def k4():
    """Pill aspect ratio just at threshold (60×40 = 1.5:1)."""
    layers = perfect_pills(w=60, h=40)
    return H(layers)
add("K4: pills 60×40 (aspect = 1.5)", k4())

def k5():
    """Pill aspect just below threshold (55×40 = 1.375:1)."""
    layers = perfect_pills(w=55, h=40)
    return H(layers)
add("K5: pills 55×40 (aspect just under)", k5())

def k6():
    """Pills too small (39×19, just under 40×20 minimum)."""
    layers = perfect_pills(w=39, h=19)
    return H(layers)
add("K6: pills 39×19 (just under min size)", k6())

def k7():
    """Stack tolerance test — 4px gap on one pair (within ±4)."""
    layers = []
    cur = 100
    gaps = [8, 12, 8]  # 12 = 4 over target 8
    for i in range(4):
        layers.append(L("rectangle", cur, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
        if i < 3:
            cur += 120 + gaps[i]
    return H(layers)
add("K7: gap variance 4px (at tol edge)", k7())

def k8():
    """Stack tolerance test — 5px gap on one pair (just over)."""
    layers = []
    cur = 100
    gaps = [8, 13, 8]  # 13 = 5 over target 8
    for i in range(4):
        layers.append(L("rectangle", cur, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
        if i < 3:
            cur += 120 + gaps[i]
    return H(layers)
add("K8: gap variance 5px (just over tol)", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """One pill fill.visible=False."""
    layers = perfect_pills()
    layers[1]["fills"][0]["visible"] = False
    return H(layers)
add("L1: 1 pill fill.visible=False", l1())

def l2():
    """One pill layer.visible=False."""
    layers = perfect_pills()
    layers[2]["visible"] = False
    return H(layers)
add("L2: 1 pill layer.visible=False", l2())

def l3():
    """All pills layer.opacity=0.3 (below threshold 0.5)."""
    layers = perfect_pills()
    for l in layers:
        l["opacity"] = 0.3
    return H(layers)
add("L3: all pills opacity=0.3", l3())

def l4():
    """All pills fill.color.a = 0.3 (below threshold)."""
    layers = perfect_pills()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.3
    return H(layers)
add("L4: all pills fill alpha=0.3", l4())

def l5():
    """One pill alpha=0, others fine — fails 'every pill visible'."""
    layers = perfect_pills()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L5: 1 pill alpha=0, rest visible", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Pills overlap in a pile at one point."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 600, 400, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("M1: pills all stacked at same position", m1())

def m2():
    """Pills span entire frame width (giant pills)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 0 + i * 320, 400, 320, 80,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("M2: pills span full frame (320×80 each)", m2())

def m3():
    """Pills equal frame size each."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 0, 0, 1280, 832,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("M3: each pill = full frame", m3())

def m4():
    """Pills offset diagonally (still uniform spacing)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100 + i*128, 100 + i*60, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("M4: pills in diagonal stair pattern", m4())

def m5():
    """3 pills on page + 1 inside hidden frame."""
    layers = perfect_pills()
    hidden = make_frame([layers[3]], w=200, h=100, x=2000, y=2000)
    return make_log([*layers[:3], hidden], evt())
add("M5: 1 pill inside far-away frame", m5())

def m6():
    """Pills with random colors (not pastel — vivid red, etc.)."""
    layers = perfect_pills(colors=[(1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                                     (0.0, 0.0, 1.0), (1.0, 1.0, 0.0)])
    return H(layers)
add("M6: pills with vivid (non-pastel) colors", m6())

def m7():
    """Pills heights mismatch by exactly 3px (at tolerance)."""
    layers = perfect_pills()
    layers[1]["h"] = 43  # +3 from 40
    return H(layers)
add("M7: heights diff 3px (at tol edge)", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Pills inside a component instance (not frame)."""
    layers = perfect_pills()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N1: pills inside component", n1())

def n2():
    """Pills inside an instance node (parent_type=instance)."""
    layers = perfect_pills()
    instance = {"id": "inst_1", "type": "instance", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([instance], evt())
add("N2: pills inside instance", n2())

def n3():
    """Each pill in its own frame."""
    layers = perfect_pills()
    frames = [make_frame([l], w=200, h=80, x=i*220) for i, l in enumerate(layers)]
    return make_log(frames, evt())
add("N3: each pill in own frame", n3())

def n4():
    """Pills nested 4-deep."""
    layers = perfect_pills()
    f4 = make_frame(layers, w=1280, h=832)
    f3 = make_frame([f4], w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("N4: pills nested 4-deep", n4())

def n5():
    """Pills inside a 'frame' that's actually a section node."""
    layers = perfect_pills()
    section = {"id": "sec", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("N5: pills in section", n5())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """4 ellipses (not rectangles) with stretched aspect."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 100 + i*128, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i]))
    return H(layers, evts=evt(rect=0))
add("O1: 4 ellipses (no rectangles)", o1())

def o2():
    """Pill substitution: 4 stars in row."""
    layers = []
    for i in range(4):
        layers.append(make_layer("star", x=100+i*128, y=300, w=120, h=40,
                                  fill=[PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                                  points=5, innerRatio=0.4, cornerRadius=999))
    return H(layers, evts=evt(rect=0))
add("O2: 4 stars (no rectangles)", o2())

def o3():
    """4 polygons claiming to be rectangles."""
    layers = []
    for i in range(4):
        layers.append(make_layer("polygon", x=100+i*128, y=300, w=120, h=40,
                                  fill=[PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                                  sides=4, cornerRadius=999))
    return H(layers, evts=evt(rect=0))
add("O3: 4 polygons (no rectangles)", o3())

def o4():
    """3 rectangles + 1 ellipse (mixed type)."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 100+i*128, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE][i],
                        cornerRadius=999))
    layers.append(L("ellipse", 484, 300, 120, 40, PASTEL_YELLOW))
    return H(layers, evts=evt(rect=3))
add("O4: 3 rectangles + 1 ellipse", o4())

def o5():
    """Text labeled 'pills' instead of actual rectangles."""
    layers = [make_layer("text", x=100, y=300, w=400, h=40, fill=NAVY)]
    layers[0]["content"] = "tag pills"
    return make_log(layers, [make_event("session_start"),
                              make_event("create_text")])
add("O5: text saying 'tag pills'", o5())


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

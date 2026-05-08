"""Round 3 edge cases — hunt for surviving false positives in task_01.

Each case is a wrong house design that the verifier should give < 1.0.
Anything scoring ≥ 0.95 is a likely surviving false positive.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_01_house_task_comprehensive as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
DARK1 = (0.10, 0.10, 0.10)
DARK2 = (0.13, 0.13, 0.13)
DARK3 = (0.16, 0.16, 0.16)
DARK4 = (0.19, 0.19, 0.19)


def evt(rect=2, ellipse=2, polygon=1, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_house():
    body = L("rectangle", 440, 300, 400, 400, PINK)
    door = L("rectangle", 600, 560, 80, 140, ORANGE)
    win_l = L("ellipse", 500, 400, 60, 60, WHITE)
    win_r = L("ellipse", 720, 400, 60, 60, YELLOW)
    roof = L("polygon", 400, 180, 480, 120, NAVY, sides=3)
    return [body, door, win_l, win_r, roof]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_house()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Body is the size of the entire frame (house = frame, no real composition)."""
    layers = [L("rectangle", 0, 0, 1280, 832, PINK),
              L("rectangle", 600, 692, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 0, -120, 1280, 120, NAVY, sides=3)]
    return H(layers)
add("K1: body = full frame (house = frame)", k1())

def k2():
    """All shapes 1280x832 stacked (no real composition)."""
    layers = [L("rectangle", 0, 0, 1280, 832, PINK),
              L("rectangle", 0, 0, 1280, 832, ORANGE),
              L("ellipse", 0, 0, 1280, 832, WHITE),
              L("ellipse", 0, 0, 1280, 832, YELLOW),
              L("polygon", 0, 0, 1280, 832, NAVY, sides=3)]
    return H(layers)
add("K2: all 5 shapes = full frame", k2())

def k3():
    """Body rotated by 4° (just under tolerance)."""
    layers = perfect_house()
    layers[0]["rotation"] = 4
    return H(layers)
add("K3: body rotated 4° (under tol)", k3())

def k4():
    """Door rotated 30° (within rectangle's own rotation, but visually wrong)."""
    layers = perfect_house()
    layers[1]["rotation"] = 30
    return H(layers)
add("K4: door rotated 30°", k4())

def k5():
    """Roof rotated 4° (just under tolerance)."""
    layers = perfect_house()
    layers[4]["rotation"] = 4
    return H(layers)
add("K5: roof rotated 4° (under tol)", k5())

def k6():
    """Body has cornerRadius=200 (basically a circle pretending to be body)."""
    layers = perfect_house()
    layers[0]["cornerRadius"] = 200
    return H(layers)
add("K6: body cornerRadius=200 (circular body)", k6())

def k7():
    """Door has cornerRadius=70 (round door = no door)."""
    layers = perfect_house()
    layers[1]["cornerRadius"] = 70
    return H(layers)
add("K7: door fully rounded (looks like circle)", k7())

def k8():
    """Roof rendered behind body (z-order)."""
    layers = perfect_house()
    # Move roof to front of list = below in z-order (drawn first)
    roof = layers.pop(4)
    layers.insert(0, roof)
    return H(layers)
add("K8: roof under body (z-order swapped)", k8())

def k9():
    """Door rendered above roof in z-order."""
    layers = perfect_house()
    door = layers.pop(1)
    layers.append(door)
    return H(layers)
add("K9: door above roof (z-order)", k9())

def k10():
    """Windows behind body (occluded)."""
    layers = perfect_house()
    body = layers.pop(0)
    layers.append(body)
    return H(layers)
add("K10: body in front of everything", k10())


# ─── L. Color subtleties ─────────────────────────────────────────────
def l1():
    """4 distinct dark colors (technically distinct, but all near-black)."""
    layers = [L("rectangle", 440, 300, 400, 400, DARK1),
              L("rectangle", 600, 560, 80, 140, DARK2),
              L("ellipse", 500, 400, 60, 60, DARK3),
              L("ellipse", 720, 400, 60, 60, DARK4),
              L("polygon", 400, 180, 480, 120, DARK1, sides=3)]
    return H(layers, frame_fill=(0.05, 0.05, 0.05))
add("L1: 4 distinct dark colors (all near-black)", l1())

def l2():
    """Body fill alpha=0 (invisible)."""
    layers = perfect_house()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L2: body fill alpha=0", l2())

def l3():
    """Body fill visible=False."""
    layers = perfect_house()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L3: body fill visible=False", l3())

def l4():
    """Body opacity (layer-level) = 0."""
    layers = perfect_house()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("L4: body layer opacity=0", l4())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Body very thin but tall — passes width fraction at 0.04 lower bound."""
    layers = perfect_house()
    layers[0] = L("rectangle", 600, 100, 60, 600, PINK)  # 60 = 4.7% of 1280
    layers[1] = L("rectangle", 615, 580, 30, 120, ORANGE)
    layers[2] = L("ellipse", 605, 250, 50, 50, WHITE)
    layers[3] = L("ellipse", 605, 350, 50, 50, YELLOW)
    layers[4] = L("polygon", 580, 30, 100, 70, NAVY, sides=3)
    return H(layers)
add("M1: super-thin body (just inside width frac)", m1())

def m2():
    """3 polygons: 2 squares + 1 triangle (PolygonSidesEquals checks any?)."""
    layers = perfect_house()
    layers[4] = L("polygon", 400, 180, 480, 120, NAVY, sides=3)  # triangle
    extra1 = L("polygon", 100, 100, 50, 50, BLUE, sides=4)       # square
    extra2 = L("polygon", 1000, 100, 50, 50, GREEN, sides=5)     # pentagon
    layers.extend([extra1, extra2])
    return H(layers, evts=evt(polygon=3))
add("M2: 3 polygons total (1 triangle, 2 not)", m2())

def m3():
    """3 small triangles instead of 1 big roof."""
    layers = perfect_house()[:4]
    for i in range(3):
        layers.append(L("polygon", 440 + i*140, 240, 130, 60, NAVY, sides=3))
    return H(layers, evts=evt(polygon=3))
add("M3: 3 small roofs (instead of 1 big)", m3())

def m4():
    """Roof very wide AND very tall — goes off-screen above frame."""
    layers = perfect_house()
    layers[4] = L("polygon", 100, -500, 1000, 800, NAVY, sides=3)
    return H(layers)
add("M4: roof huge, goes way off-screen", m4())

def m5():
    """Door overlaps roof (extends above body's top)."""
    layers = perfect_house()
    layers[1] = L("rectangle", 600, 200, 80, 250, ORANGE)
    return H(layers)
add("M5: door extends up into roof area", m5())

def m6():
    """Frame size 2000x2000 — way too big but FrameSizeEquals(1280x832) fails."""
    return H(frame_w=2000, frame_h=2000)
add("M6: frame 2000x2000 (fails FrameSizeEquals)", m6())

def m7():
    """Body is invisible (no fill, no stroke), but exists structurally."""
    layers = perfect_house()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("M7: body invisible (no fill, no stroke)", m7())

def m8():
    """Windows concentric (one inside the other, looks like 1 ring)."""
    layers = perfect_house()
    layers[2] = L("ellipse", 580, 380, 100, 100, WHITE)
    layers[3] = L("ellipse", 600, 400, 60, 60, YELLOW)
    return H(layers)
add("M8: windows concentric (ring effect)", m8())

def m9():
    """Door is wider than body but shorter (squat)."""
    layers = perfect_house()
    layers[1] = L("rectangle", 200, 660, 880, 40, ORANGE)
    return H(layers)
add("M9: door 880x40 (wider than body)", m9())

def m10():
    """All shapes at exact same position (overlapping pile)."""
    layers = [L("rectangle", 500, 400, 100, 100, PINK),
              L("rectangle", 500, 400, 100, 100, ORANGE),
              L("ellipse", 500, 400, 100, 100, WHITE),
              L("ellipse", 500, 400, 100, 100, YELLOW),
              L("polygon", 500, 400, 100, 100, NAVY, sides=3)]
    return H(layers)
add("M10: all shapes piled at one point", m10())


# ─── N. Hierarchy / structural tricks ────────────────────────────────
def n1():
    """Body inside frame, others as siblings to frame on the page."""
    body = L("rectangle", 440, 300, 400, 400, PINK)
    others = [L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    frame = make_frame([body], w=1280, h=832)
    return make_log([frame, *others], evt())
add("N1: only body inside frame, others outside", n1())

def n2():
    """Roof in a SEPARATE frame from body."""
    house = perfect_house()
    f1 = make_frame(house[:4], w=1280, h=832)
    f2 = make_frame([house[4]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("N2: roof in different frame from body", n2())

def n3():
    """Each shape in its own 1-shape frame."""
    house = perfect_house()
    frames = [make_frame([s], w=1280, h=832) for s in house]
    return make_log(frames, evt())
add("N3: each shape in its own frame", n3())

def n4():
    """House inside a Component instance (not a frame)."""
    house = perfect_house()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": house}
    return make_log([component], evt())
add("N4: house inside component (not frame)", n4())


# ─── O. Wrong shape types substituted ────────────────────────────────
def o1():
    """Door as a star (5-point star)."""
    layers = perfect_house()
    layers[1] = make_layer("star", x=600, y=560, w=80, h=140,
                           fill=ORANGE, points=5, innerRatio=0.4)
    return H(layers, evts=evt(rect=1))
add("O1: door is a star", o1())

def o2():
    """Roof as ellipse (no polygon)."""
    layers = perfect_house()[:4]
    layers.append(L("ellipse", 400, 180, 480, 120, NAVY))
    return H(layers, evts=evt(ellipse=3, polygon=0))
add("O2: roof is ellipse, no polygon", o2())

def o3():
    """Two polygons claiming to be roof, both with 3 sides."""
    layers = perfect_house()
    layers[4] = L("polygon", 200, 180, 240, 120, NAVY, sides=3)
    layers.append(L("polygon", 840, 180, 240, 120, NAVY, sides=3))
    return H(layers, evts=evt(polygon=2))
add("O3: 2 triangles instead of 1 roof", o3())


# ─── Run ────────────────────────────────────────────────────────────
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

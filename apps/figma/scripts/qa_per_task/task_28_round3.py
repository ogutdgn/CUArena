"""Round 3 novel-deception edge cases for task 28 (X-cross photo placeholder).

Spec: Large rectangle (placeholder) + 2 diagonal lines crossing through it.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, BLACK, LIGHT_GRAY, WHITE,
)
from tasks import task_28_edited_photo as t
T = t.task


def evt(rect=1, line=2, set_fill=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    sem.append(make_event("tool_change", before="rectangle", after="line"))
    for _ in range(line):     sem.append(make_event("create_line"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def make_line(x, y, w, h, p1, p2, fill=BLACK, **extra):
    line = make_layer("line", x=x, y=y, w=w, h=h, fill=None, **extra)
    line["fills"] = []
    line["strokes"] = [make_stroke(rgb=fill, weight=2)]
    line["p1"] = {"x": p1[0], "y": p1[1]}
    line["p2"] = {"x": p2[0], "y": p2[1]}
    return line


def perfect_design():
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return [rect, line1, line2]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ───────────────────────────────────────────
def k1():
    """Lines exactly on rect edges (not corners)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    # Top edge to right edge midpoint
    line1 = make_line(400, 200, 480, 320, (240, 0), (480, 160))
    # Top edge to left edge midpoint
    line2 = make_line(400, 200, 480, 320, (240, 0), (0, 160))
    return H([rect, line1, line2])
add("K1: lines from edge midpoints (not corners)", k1())


def k2():
    """Lines correct corners but rect rotated 45° (corners no longer aligned)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    rect["rotation"] = 45
    # Lines based on un-rotated corner positions
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([rect, line1, line2])
add("K2: rect rotated, lines on un-rotated corners", k2())


def k3():
    """Both lines = TL→BR (no opposing X)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (5, 5), (475, 315))
    return H([rect, line1, line2])
add("K3: both lines TL→BR (no opposing pair)", k3())


def k4():
    """Lines drawn outside rect bounds (offset)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    # Lines that connect frame's corners, not rect's
    line1 = make_line(0, 0, 1280, 832, (0, 0), (1280, 832))
    line2 = make_line(0, 0, 1280, 832, (1280, 0), (0, 832))
    return H([rect, line1, line2])
add("K4: X spanning frame, not rect", k4())


def k5():
    """Lines off corners by 13px (just over 12px tol)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (13, 13), (467, 307))
    line2 = make_line(400, 200, 480, 320, (467, 13), (13, 307))
    return H([rect, line1, line2])
add("K5: lines 13px off corners (just over tol)", k5())


def k6():
    """Lines flipped scaleX=-1 — they still go corner to corner spatially."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line1["scaleX"] = -1
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    line2["scaleX"] = -1
    return H([rect, line1, line2])
add("K6: lines flipped scaleX=-1", k6())


def k7():
    """Rect at 200x150 (not 'large')."""
    rect = L("rectangle", 540, 340, 80, 80, LIGHT_GRAY)  # too small
    line1 = make_line(540, 340, 80, 80, (0, 0), (80, 80))
    line2 = make_line(540, 340, 80, 80, (80, 0), (0, 80))
    return H([rect, line1, line2])
add("K7: tiny 80x80 rect (not large)", k7())


def k8():
    """Rect rotated 4° (under tolerance)."""
    layers = perfect_design()
    layers[0]["rotation"] = 4
    return H(layers)
add("K8: rect rotated 4° (under tol)", k8())


def k9():
    """Lines have 0.4-alpha (just below visible threshold)."""
    layers = perfect_design()
    for line in layers[1:]:
        line["strokes"][0]["paint"]["color"]["a"] = 0.4
    return H(layers)
add("K9: line strokes alpha=0.4 (under threshold of 0.5? actually ok)", k9())


def k10():
    """Lines stroke weight=0 (no visible stroke even though stroke object exists)."""
    layers = perfect_design()
    for line in layers[1:]:
        line["strokes"][0]["weight"] = 0
    return H(layers)
add("K10: lines stroke weight=0", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Rect layer-level opacity=0."""
    layers = perfect_design()
    layers[0]["opacity"] = 0
    return H(layers)
add("L1: rect opacity=0", l1())


def l2():
    """Rect fill alpha=0."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L2: rect fill alpha=0", l2())


def l3():
    """Rect visible=False."""
    layers = perfect_design()
    layers[0]["visible"] = False
    return H(layers)
add("L3: rect visible=False", l3())


def l4():
    """Lines visible=False (all)."""
    layers = perfect_design()
    for line in layers[1:]:
        line["visible"] = False
        line["strokes"][0]["visible"] = False
    return H(layers)
add("L4: lines visible=False", l4())


def l5():
    """Lines have alpha=0 strokes."""
    layers = perfect_design()
    for line in layers[1:]:
        line["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("L5: lines stroke alpha=0", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Rect = full frame."""
    rect = L("rectangle", 0, 0, 1280, 832, LIGHT_GRAY)
    line1 = make_line(0, 0, 1280, 832, (0, 0), (1280, 832))
    line2 = make_line(0, 0, 1280, 832, (1280, 0), (0, 832))
    return H([rect, line1, line2])
add("M1: rect = full frame", m1())


def m2():
    """Rect 30x30 (degenerate small)."""
    rect = L("rectangle", 600, 400, 30, 30, LIGHT_GRAY)
    line1 = make_line(600, 400, 30, 30, (0, 0), (30, 30))
    line2 = make_line(600, 400, 30, 30, (30, 0), (0, 30))
    return H([rect, line1, line2])
add("M2: rect 30x30 (under min size)", m2())


def m3():
    """Two rects, 2 lines on smaller."""
    rect_big = L("rectangle", 100, 100, 800, 600, LIGHT_GRAY)
    rect_small = L("rectangle", 1000, 600, 40, 40, LIGHT_GRAY)
    line1 = make_line(1000, 600, 40, 40, (0, 0), (40, 40))
    line2 = make_line(1000, 600, 40, 40, (40, 0), (0, 40))
    return H([rect_big, rect_small, line1, line2], evts=evt(rect=2))
add("M3: 2 rects, lines on small one", m3())


def m4():
    """Rect with 0 width."""
    rect = L("rectangle", 600, 400, 0, 320, LIGHT_GRAY)
    line1 = make_line(600, 400, 0, 320, (0, 0), (0, 320))
    line2 = make_line(600, 400, 0, 320, (0, 0), (0, 320))
    return H([rect, line1, line2])
add("M4: rect 0 width", m4())


def m5():
    """Rect width = frame width, but offset off-frame."""
    rect = L("rectangle", 1500, 200, 600, 400, LIGHT_GRAY)
    line1 = make_line(1500, 200, 600, 400, (0, 0), (600, 400))
    line2 = make_line(1500, 200, 600, 400, (600, 0), (0, 400))
    return H([rect, line1, line2])
add("M5: rect off-frame to right", m5())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Rect outside frame, lines inside frame."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    frame = make_frame([line1, line2], w=1280, h=832)
    return make_log([rect, frame], evt())
add("N1: rect outside frame, lines inside", n1())


def n2():
    """Lines outside frame, rect inside."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    frame = make_frame([rect], w=1280, h=832)
    return make_log([frame, line1, line2], evt())
add("N2: lines outside frame, rect inside", n2())


def n3():
    """Design wrapped in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: design in component (no frame)", n3())


def n4():
    """Design in section (no frame)."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("N4: design in section (no frame)", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Polygon (rect-like) instead of rectangle."""
    poly = make_layer("polygon", x=400, y=200, w=480, h=320, fill=LIGHT_GRAY, sides=4)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([poly, line1, line2], evts=evt(rect=0) + [make_event("create_polygon")])
add("O1: 4-sided polygon instead of rect", o1())


def o2():
    """Vectors instead of lines."""
    rect = perfect_design()[0]
    v1 = make_layer("vector", x=400, y=200, w=480, h=320, fill=BLACK)
    v2 = make_layer("vector", x=400, y=200, w=480, h=320, fill=BLACK)
    return H([rect, v1, v2], evts=evt(line=0) + [make_event("create_vector"),
                                                  make_event("create_vector")])
add("O2: vectors instead of lines", o2())


def o3():
    """Ellipse instead of rectangle."""
    e = make_layer("ellipse", x=400, y=200, w=480, h=320, fill=LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([e, line1, line2], evts=evt(rect=0) + [make_event("create_ellipse")])
add("O3: ellipse instead of rect", o3())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)

for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

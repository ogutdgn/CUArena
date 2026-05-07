"""Task 01 — house inside MacBook Air frame.

Prompt: 2 rectangles (body + door) + 2 ellipses (windows) + 1 polygon (roof)
inside a 1280×832 frame. Distinct colors. Windows aligned + same-size +
symmetric. Roof bottom touches body top. Door inside body.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event,
    RED, WHITE, BLACK, YELLOW, NAVY, GREEN, PINK, ORANGE,
)


def _events_for(rect=2, ellipse=2, polygon=1, set_fill=4):
    """Standard event stream for a house creation."""
    sem = [make_event("session_start")]
    for tool in ("rectangle", "ellipse", "polygon"):
        sem.append(make_event("tool_change", before="select", after=tool))
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    return sem


def perfect():
    """A textbook valid house: 2 rect, 2 ellipse, 1 polygon, frame 1280×832,
    windows aligned + symmetric + same size, roof bottom on body top, distinct fills."""
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=PINK)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=500, y=400, w=60,  h=60,  fill=WHITE)
    win_r = make_layer("ellipse",  x=720, y=400, w=60,  h=60,  fill=WHITE)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832)
    # Windows: distinct from body fill — let's use yellow for win_l so DistinctSolidColors≥4
    win_l["fills"][0]["color"] = {"r": YELLOW[0], "g": YELLOW[1], "b": YELLOW[2], "a": 1.0}
    return make_log([frame], _events_for())


def perfect_alt_layout():
    """Same shapes but a smaller, shifted layout."""
    body = make_layer("rectangle", x=200, y=150, w=300, h=300, fill=PINK)
    door = make_layer("rectangle", x=320, y=350, w=60,  h=100, fill=GREEN)
    win_l = make_layer("ellipse",  x=240, y=220, w=40,  h=40,  fill=WHITE)
    win_r = make_layer("ellipse",  x=420, y=220, w=40,  h=40,  fill=YELLOW)
    roof = make_layer("polygon",   x=170, y=80,  w=360, h=70,  fill=NAVY, sides=3)
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832)
    return make_log([frame], _events_for())


def perfect_more_events():
    """Valid + extra align/move events that shouldn't change the score."""
    log = perfect()
    log["semantic"].extend([
        make_event("align_layers", axis="center_x"),
        make_event("move_layer"),
        make_event("set_fill_color"),  # 5th set_fill — still meets ≥4
    ])
    return log


# ─── FAIL logs (each targets a specific weakness) ───

def fail_three_rectangles():
    """3 rectangles instead of 2 — expects ShapeCount(rect, 2) to fail."""
    log = perfect()
    extra = make_layer("rectangle", x=900, y=600, w=50, h=50, fill=RED)
    log["outcome"]["document"]["pages"][0]["children"][0]["children"].append(extra)
    log["semantic"].append(make_event("create_rectangle"))
    return log


def fail_one_ellipse():
    """Only 1 ellipse instead of 2 — expects ShapeCount(ellipse, 2) to fail."""
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=PINK)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=500, y=400, w=60,  h=60,  fill=WHITE)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)
    frame = make_frame([body, door, win_l, roof], w=1280, h=832)
    return make_log([frame], _events_for(ellipse=1))


def fail_all_same_color():
    """All 5 shapes same gray — expects DistinctSolidColors≥4 to fail."""
    GRAY = (0.5, 0.5, 0.5)
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=GRAY)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=GRAY)
    win_l = make_layer("ellipse",  x=500, y=400, w=60,  h=60,  fill=GRAY)
    win_r = make_layer("ellipse",  x=720, y=400, w=60,  h=60,  fill=GRAY)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=GRAY, sides=3)
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832, fill=GRAY)
    return make_log([frame], _events_for())


def fail_windows_misaligned():
    """Right window y differs by 100px — expects LayersAligned(ellipse, center_y) to fail."""
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=PINK)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=500, y=400, w=60,  h=60,  fill=WHITE)
    win_r = make_layer("ellipse",  x=720, y=500, w=60,  h=60,  fill=YELLOW)  # 100px lower
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832)
    return make_log([frame], _events_for())


def fail_windows_not_symmetric():
    """Both windows on the left of door — expects LayersSymmetricX(ellipse) to fail."""
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=PINK)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=480, y=400, w=60,  h=60,  fill=WHITE)
    win_r = make_layer("ellipse",  x=540, y=400, w=60,  h=60,  fill=YELLOW)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832)
    return make_log([frame], _events_for())


def fail_no_frame():
    """All shapes loose on the page (no frame) — expects LayerInsideFrame + FrameSizeEquals + ChildCountAtLeast to fail."""
    body = make_layer("rectangle", x=440, y=300, w=400, h=400, fill=PINK)
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=500, y=400, w=60,  h=60,  fill=WHITE)
    win_r = make_layer("ellipse",  x=720, y=400, w=60,  h=60,  fill=YELLOW)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)
    return make_log([body, door, win_l, win_r, roof], _events_for())


def fail_roof_floats():
    """Roof bottom not touching body top — gap of 50px."""
    body = make_layer("rectangle", x=440, y=400, w=400, h=300, fill=PINK)  # body shifted down
    door = make_layer("rectangle", x=600, y=560, w=80,  h=140, fill=ORANGE)
    win_l = make_layer("ellipse",  x=500, y=460, w=60,  h=60,  fill=WHITE)
    win_r = make_layer("ellipse",  x=720, y=460, w=60,  h=60,  fill=YELLOW)
    roof = make_layer("polygon",   x=400, y=180, w=480, h=120, fill=NAVY, sides=3)  # roof bottom at y=300
    frame = make_frame([body, door, win_l, win_r, roof], w=1280, h=832)
    return make_log([frame], _events_for())


def fail_no_set_fill_events():
    """Shapes correct but no set_fill_color events — expects EventTypeCountAtLeast(set_fill_color, 4) to fail."""
    log = perfect()
    log["semantic"] = [e for e in log["semantic"] if e.get("name") != "set_fill_color"]
    return log


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_alt_layout", perfect_alt_layout()),
    ("perfect_more_events", perfect_more_events()),
]

FAIL_LOGS = [
    # (label, log, expected-broken-checks)
    ("3_rectangles",          fail_three_rectangles(),     ["rectangle.*expected 2.*got 3"]),
    ("1_ellipse",             fail_one_ellipse(),          ["ellipse.*expected 2.*got 1"]),
    ("all_same_color",        fail_all_same_color(),       ["distinct solid colors.*≥4"]),
    ("windows_misaligned",    fail_windows_misaligned(),   ["ellipse aligned on center_y"]),
    ("windows_not_symmetric", fail_windows_not_symmetric(), ["flanked by ellipse on both sides"]),
    ("no_frame",              fail_no_frame(),             ["No frame at 1280", "direct child of a frame", "≥5 children"]),
    ("roof_floats",           fail_roof_floats(),          ["polygon.bottom.*rectangle.top"]),
    ("no_set_fill_events",    fail_no_set_fill_events(),   ["set_fill_color.*≥"]),
]

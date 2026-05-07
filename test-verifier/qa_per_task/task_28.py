"""Task 28 — Photo placeholder rectangle with 2 diagonal lines forming an X."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, make_stroke


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("tool_change", before="rectangle", after="line"),
        make_event("create_rectangle"),
        make_event("create_line"),
        make_event("create_line"),
    ]


def _x_photo(rect_w=400, rect_h=300, fill=(0.85,0.85,0.85)):
    rect = make_layer("rectangle", x=200, y=200, w=rect_w, h=rect_h, fill=fill)
    line1 = make_layer("line", x=200, y=200, w=rect_w, h=rect_h, fill=None,
                       p1={"x":0,"y":0}, p2={"x":rect_w,"y":rect_h},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    line2 = make_layer("line", x=200, y=200, w=rect_w, h=rect_h, fill=None,
                       p1={"x":rect_w,"y":0}, p2={"x":0,"y":rect_h},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    return make_log([rect, line1, line2], _events())


def perfect():        return _x_photo()
def perfect_smaller(): return _x_photo(rect_w=200, rect_h=160)
def perfect_taller():  return _x_photo(rect_w=300, rect_h=400)


def fail_one_line():
    rect = make_layer("rectangle", x=200, y=200, w=400, h=300, fill=(0.85,0.85,0.85))
    line1 = make_layer("line", x=200, y=200, w=400, h=300, fill=None,
                       p1={"x":0,"y":0}, p2={"x":400,"y":300},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    sem = [make_event("session_start"),
           make_event("create_rectangle"),
           make_event("create_line")]
    return make_log([rect, line1], sem)


def fail_lines_not_diagonal():
    rect = make_layer("rectangle", x=200, y=200, w=400, h=300, fill=(0.85,0.85,0.85))
    line1 = make_layer("line", x=200, y=300, w=400, h=4, fill=None,
                       p1={"x":0,"y":0}, p2={"x":400,"y":0},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    line2 = make_layer("line", x=300, y=200, w=4, h=300, fill=None,
                       p1={"x":0,"y":0}, p2={"x":0,"y":300},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    return make_log([rect, line1, line2], _events())


def fail_no_rect():
    line1 = make_layer("line", x=200, y=200, w=400, h=300, fill=None,
                       p1={"x":0,"y":0}, p2={"x":400,"y":300},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    line2 = make_layer("line", x=200, y=200, w=400, h=300, fill=None,
                       p1={"x":400,"y":0}, p2={"x":0,"y":300},
                       strokes=[make_stroke(rgb=(0,0,0), weight=2)])
    sem = [make_event("session_start"),
           make_event("create_line"),
           make_event("create_line")]
    return make_log([line1, line2], sem)


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_taller",  perfect_taller()),
]
FAIL_LOGS = [
    ("one_line",            fail_one_line(),            ["expected 2, got 1"]),
    ("lines_not_diagonal",  fail_lines_not_diagonal(),  ["lines"]),
    ("no_rect",             fail_no_rect(),             ["expected 1, got 0"]),
]

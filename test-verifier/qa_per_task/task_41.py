"""Task 41 — 320×48 rounded light-gray bar + magnifier (stroked circle + line) + dots."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
)


LIGHT_GRAY_BAR = (0.95, 0.95, 0.95)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("tool_change", before="ellipse", after="line"),
           make_event("create_rectangle"),
           make_event("create_ellipse"),
           make_event("create_ellipse"),
           make_event("create_ellipse"),
           make_event("create_line")]
    return sem


def _bar(bar_w=320, bar_h=48, radius=24, fill=LIGHT_GRAY_BAR):
    bar = make_layer("rectangle", x=200, y=300, w=bar_w, h=bar_h, fill=fill,
                     cornerRadius=radius)
    glass = make_layer("ellipse", x=210, y=312, w=24, h=24, fill=None,
                       strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    handle = make_layer("line", x=232, y=334, w=10, h=10, fill=None,
                        strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    dot1 = make_layer("ellipse", x=270, y=320, w=8, h=8, fill=None,
                      strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    dot2 = make_layer("ellipse", x=290, y=320, w=8, h=8, fill=None,
                      strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    frame = make_frame([bar, glass, handle, dot1, dot2], w=1280, h=832)
    return make_log([frame], _events())


def perfect():        return _bar()
def perfect_smaller_radius(): return _bar(radius=20)
def perfect_other_color():
    return _bar(fill=(0.92, 0.92, 0.95))


def fail_wrong_bar_size(): return _bar(bar_w=200, bar_h=80)
def fail_no_radius():      return _bar(radius=0)
def fail_dark_bar():       return _bar(fill=(0.2, 0.2, 0.2))
def fail_no_glass_stroke():
    bar = make_layer("rectangle", x=200, y=300, w=320, h=48, fill=LIGHT_GRAY_BAR,
                     cornerRadius=24)
    glass = make_layer("ellipse", x=210, y=312, w=24, h=24, fill=None)
    handle = make_layer("line", x=232, y=334, w=10, h=10, fill=None,
                        strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    dot1 = make_layer("ellipse", x=270, y=320, w=8, h=8, fill=None)
    dot2 = make_layer("ellipse", x=290, y=320, w=8, h=8, fill=None)
    frame = make_frame([bar, glass, handle, dot1, dot2], w=1280, h=832)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",                perfect()),
    ("perfect_smaller_radius", perfect_smaller_radius()),
    ("perfect_other_color",    perfect_other_color()),
]
FAIL_LOGS = [
    ("wrong_bar_size",   fail_wrong_bar_size(),   ["w=200 ≠ 320"]),
    ("no_radius",        fail_no_radius(),        ["cornerRadius"]),
    ("dark_bar",         fail_dark_bar(),         ["No rectangle with solid"]),
    ("no_glass_stroke",  fail_no_glass_stroke(),  ["no visible stroke"]),
]

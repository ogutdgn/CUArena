"""Task 16 — Speech bubble: rounded rect + triangle tail, both light gray with 2px dark-gray stroke."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, LIGHT_GRAY, DARK_GRAY,
)


def _events():
    return [make_event("session_start"),
            make_event("tool_change", before="select", after="rectangle"),
            make_event("tool_change", before="rectangle", after="polygon"),
            make_event("create_rectangle"),
            make_event("create_polygon")]


def _bubble(rect_color=LIGHT_GRAY, poly_color=LIGHT_GRAY, stroke_color=DARK_GRAY,
            radius=16, stroke_w=2, overlap=True):
    rect = make_layer("rectangle", x=300, y=200, w=240, h=120, fill=rect_color,
                      strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)],
                      cornerRadius=radius)
    poly_x = 320 if overlap else 100
    poly = make_layer("polygon", x=poly_x, y=300, w=60, h=60, fill=poly_color,
                     strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)],
                     sides=3)
    return make_log([rect, poly], _events())


def perfect():        return _bubble()
def perfect_smaller(): return _bubble(radius=12, stroke_w=2)
def perfect_higher_radius(): return _bubble(radius=40)


def fail_rect_not_overlapping_tail(): return _bubble(overlap=False)
def fail_no_corner_radius():           return _bubble(radius=0)
def fail_wrong_color():                 return _bubble(rect_color=(0.95,0.3,0.3),
                                                       poly_color=(0.95,0.3,0.3))
def fail_no_stroke():
    rect = make_layer("rectangle", x=300, y=200, w=240, h=120, fill=LIGHT_GRAY,
                      cornerRadius=16)
    poly = make_layer("polygon", x=320, y=300, w=60, h=60, fill=LIGHT_GRAY, sides=3)
    return make_log([rect, poly], _events())


PASS_LOGS = [
    ("perfect",                 perfect()),
    ("perfect_smaller",         perfect_smaller()),
    ("perfect_higher_radius",   perfect_higher_radius()),
]
FAIL_LOGS = [
    ("rect_not_overlapping_tail", fail_rect_not_overlapping_tail(), ["overlap"]),
    ("no_corner_radius",          fail_no_corner_radius(),          ["cornerRadius"]),
    ("wrong_color",               fail_wrong_color(),               ["color mismatch"]),
    ("no_stroke",                 fail_no_stroke(),                 ["No rectangle with a stroke"]),
]

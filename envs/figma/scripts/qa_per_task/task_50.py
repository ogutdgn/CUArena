"""Task 50 — 1 large square + 1 5-point star centered on top, contrasting fills."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("tool_change", before="rectangle", after="star"),
        make_event("create_rectangle"),
        make_event("create_star"),
    ]


def _cover(rect_color=(0.3, 0.3, 0.5), star_color=(0.95, 0.85, 0.2),
           points=5, square_size=300, star_size=160):
    cx, cy = 500, 500
    square = make_layer("rectangle", x=cx-square_size/2, y=cy-square_size/2,
                        w=square_size, h=square_size, fill=rect_color)
    star = make_layer("star", x=cx-star_size/2, y=cy-star_size/2,
                     w=star_size, h=star_size, fill=star_color,
                     points=points, innerRatio=0.4)
    return make_log([square, star], _events())


def perfect():        return _cover()
def perfect_smaller(): return _cover(square_size=240, star_size=120)
def perfect_other_palette(): return _cover(rect_color=(0.85,0.3,0.3), star_color=(1,1,1))


def fail_3_point_star():       return _cover(points=3)
def fail_same_color():
    """Square and star same color — DistinctSolidColors≥2 fails."""
    return _cover(rect_color=(0.95,0.85,0.2), star_color=(0.95,0.85,0.2))


PASS_LOGS = [
    ("perfect",                perfect()),
    ("perfect_smaller",        perfect_smaller()),
    ("perfect_other_palette",  perfect_other_palette()),
]
FAIL_LOGS = [
    ("3_point_star",         fail_3_point_star(),         ["expected 5, got 3"]),
    ("same_color",           fail_same_color(),           ["≥2"]),
]

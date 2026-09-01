"""Task 47 — 8-point warm-orange star + smaller centered cream circle."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, WARM_ORANGE, CREAM


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="star"),
        make_event("tool_change", before="star", after="ellipse"),
        make_event("create_star"),
        make_event("create_ellipse"),
    ]


def _badge(star_color=WARM_ORANGE, ellipse_color=CREAM, points=8,
           star_size=240, circle_size=80):
    cx, cy = 500, 500
    star = make_layer("star", x=cx-star_size/2, y=cy-star_size/2,
                      w=star_size, h=star_size, fill=star_color,
                      points=points, innerRatio=0.5)
    circle = make_layer("ellipse", x=cx-circle_size/2, y=cy-circle_size/2,
                         w=circle_size, h=circle_size, fill=ellipse_color)
    return make_log([star, circle], _events())


def perfect():        return _badge()
def perfect_smaller(): return _badge(star_size=180, circle_size=60)
def perfect_other_orange(): return _badge(star_color=(0.95, 0.55, 0.15))


def fail_5_points():           return _badge(points=5)
def fail_wrong_star_color():   return _badge(star_color=(0.3,0.5,0.95))
def fail_wrong_circle_color(): return _badge(ellipse_color=(0.3,0.5,0.95))
def fail_circle_too_big():
    cx, cy = 500, 500
    star = make_layer("star", x=cx-120, y=cy-120, w=240, h=240, fill=WARM_ORANGE,
                      points=8, innerRatio=0.5)
    circle = make_layer("ellipse", x=cx-150, y=cy-150, w=300, h=300, fill=CREAM)
    return make_log([star, circle], _events())


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_smaller",    perfect_smaller()),
    ("perfect_other_orange",perfect_other_orange()),
]
FAIL_LOGS = [
    ("5_points",            fail_5_points(),            ["expected 8, got 5"]),
    ("wrong_star_color",    fail_wrong_star_color(),    ["No star with solid"]),
    ("wrong_circle_color",  fail_wrong_circle_color(),  ["No ellipse with solid"]),
    ("circle_too_big",      fail_circle_too_big(),      ["fits inside any star"]),
]

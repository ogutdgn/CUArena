"""Task 45 — Deep-blue 8-point star + smaller yellow circle centered on top."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, DEEP_BLUE, YELLOW,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="star"),
        make_event("tool_change", before="star", after="ellipse"),
        make_event("create_star"),
        make_event("create_ellipse"),
    ]


def _wrap(layers):
    return make_log([make_frame(layers, w=1280, h=832)], _events())


def _emblem(star_color=DEEP_BLUE, ellipse_color=YELLOW, star_points=8,
            star_size=400, ellipse_size=200):
    cx, cy = 640, 416
    star = make_layer("star", x=cx-star_size/2, y=cy-star_size/2,
                      w=star_size, h=star_size, fill=star_color,
                      points=star_points, innerRatio=0.4)
    circle = make_layer("ellipse", x=cx-ellipse_size/2, y=cy-ellipse_size/2,
                         w=ellipse_size, h=ellipse_size, fill=ellipse_color)
    return _wrap([star, circle])


def perfect():        return _emblem()
def perfect_smaller():return _emblem(star_size=320, ellipse_size=160)
def perfect_larger(): return _emblem(star_size=560, ellipse_size=200)


def fail_5_point_star():    return _emblem(star_points=5)
def fail_wrong_star_color(): return _emblem(star_color=(0.95,0.3,0.3))
def fail_wrong_ellipse_color(): return _emblem(ellipse_color=(0.3,0.5,0.95))
def fail_circle_not_centered():
    cx, cy = 640, 416
    star = make_layer("star", x=cx-200, y=cy-200, w=400, h=400, fill=DEEP_BLUE,
                      points=8, innerRatio=0.4)
    circle = make_layer("ellipse", x=200, y=200, w=80, h=80, fill=YELLOW)  # off-center
    return _wrap([star, circle])


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("5_point_star",            fail_5_point_star(),            ["expected 8, got 5"]),
    ("wrong_star_color",        fail_wrong_star_color(),        ["color mismatch"]),
    ("wrong_ellipse_color",     fail_wrong_ellipse_color(),     ["color mismatch"]),
    ("circle_not_centered",     fail_circle_not_centered(),     ["No ellipse fits inside any star"]),
]

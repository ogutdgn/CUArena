"""Task 14 — 4 concentric ellipses alternating red/white, 4px black stroke each."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, RED, WHITE, BLACK,
)


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(n):
        sem.append(make_event("create_ellipse"))
    return sem


def _target(sizes, colors, stroke_color=BLACK, stroke_w=4, with_stroke=True):
    cx, cy = 600, 416
    layers = []
    for sz, c in zip(sizes, colors):
        l = make_layer("ellipse", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz, fill=c)
        if with_stroke:
            l["strokes"] = [make_stroke(rgb=stroke_color, weight=stroke_w)]
        layers.append(l)
    frame = make_frame(layers, w=1280, h=832, fill=(0.95, 0.95, 0.95))
    return make_log([frame], _events(n=len(sizes)))


def perfect():        return _target([240,180,120,60], [RED, WHITE, RED, WHITE])
def perfect_smaller(): return _target([200,150,100,50], [RED, WHITE, RED, WHITE])
def perfect_thicker_stroke(): return _target([240,180,120,60], [RED, WHITE, RED, WHITE], stroke_w=5)


def fail_3_circles():           return _target([240,180,120], [RED, WHITE, RED])
def fail_no_strokes():          return _target([240,180,120,60], [RED, WHITE, RED, WHITE], with_stroke=False)
def fail_all_red():             return _target([240,180,120,60], [RED, RED, RED, RED])
def fail_color_order_reversed(): return _target([240,180,120,60], [WHITE, RED, WHITE, RED])
def fail_wrong_stroke_color():   return _target([240,180,120,60], [RED, WHITE, RED, WHITE],
                                                  stroke_color=(0.7, 0.7, 0.7))


PASS_LOGS = [
    ("perfect",                perfect()),
    ("perfect_smaller",        perfect_smaller()),
    ("perfect_thicker_stroke", perfect_thicker_stroke()),
]
FAIL_LOGS = [
    ("3_circles",                fail_3_circles(),                ["expected 4, got 3"]),
    ("no_strokes",               fail_no_strokes(),               ["no stroke"]),
    ("all_red",                  fail_all_red(),                  ["color mismatch"]),
    ("color_order_reversed",     fail_color_order_reversed(),     ["color mismatch"]),
    ("wrong_stroke_color",       fail_wrong_stroke_color(),       ["stroke color off"]),
]

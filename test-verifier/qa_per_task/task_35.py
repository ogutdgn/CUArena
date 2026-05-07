"""Task 35 — 2×2 honeycomb of 4 yellow hexagons with 1px black strokes."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, BLACK,
)


YELLOW_HEX = (1.0, 0.85, 0.2)


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(n):
        sem.append(make_event("create_polygon"))
    return sem


def _honey(n=4, side=80, fill=YELLOW_HEX, stroke=BLACK, sides=6):
    layers = []
    for i in range(n):
        r, c = divmod(i, 2)
        x_offset = (side / 2) if r % 2 else 0
        layers.append(make_layer("polygon", x=100+c*side*1.2 + x_offset,
                                  y=100+r*side, w=side, h=side, fill=fill,
                                  strokes=[make_stroke(rgb=stroke, weight=1)],
                                  sides=sides))
    return make_log(layers, _events(n))


def perfect():        return _honey()
def perfect_smaller(): return _honey(side=60)
def perfect_larger():  return _honey(side=120)


def fail_3_hexagons():    return _honey(n=3)
def fail_pentagons():     return _honey(sides=5)
def fail_no_stroke():
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(make_layer("polygon", x=100+c*100 + x_offset, y=100+r*80,
                                  w=80, h=80, fill=YELLOW_HEX, sides=6))
    return make_log(layers, _events())
def fail_wrong_color():   return _honey(fill=(0.3,0.3,0.7))
def fail_in_a_row():
    layers = []
    for i in range(4):
        layers.append(make_layer("polygon", x=100+i*120, y=200, w=80, h=80, fill=YELLOW_HEX,
                                  strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("3_hexagons",   fail_3_hexagons(),   ["expected 4, got 3"]),
    ("pentagons",    fail_pentagons(),    ["expected 6, got 5"]),
    ("no_stroke",    fail_no_stroke(),    ["No polygon with a stroke"]),
    ("wrong_color",  fail_wrong_color(),  ["color mismatch"]),
    ("in_a_row",     fail_in_a_row(),     ["row clusters"]),
]

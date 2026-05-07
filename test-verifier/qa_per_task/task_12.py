"""Task 12 — 4 same-size rectangles in horizontal row, sharing y baseline."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _row(n=4, w=120, h=120, gap=20, y=200):
    layers = []
    for i in range(n):
        layers.append(make_layer("rectangle", x=100+i*(w+gap), y=y,
                                  w=w, h=h, fill=(0.5+0.1*i, 0.5, 0.7)))
    return make_log(layers, _events(n))


def perfect():        return _row()
def perfect_smaller(): return _row(w=80, h=80, gap=10)
def perfect_larger():  return _row(w=180, h=180, gap=30)


def fail_3_rects():       return _row(n=3)
def fail_misaligned_y():
    layers = [
        make_layer("rectangle", x=100, y=200, w=120, h=120, fill=(0.5,0.5,0.7)),
        make_layer("rectangle", x=240, y=300, w=120, h=120, fill=(0.6,0.5,0.7)),
        make_layer("rectangle", x=380, y=200, w=120, h=120, fill=(0.7,0.5,0.7)),
        make_layer("rectangle", x=520, y=300, w=120, h=120, fill=(0.8,0.5,0.7)),
    ]
    return make_log(layers, _events())
def fail_different_sizes():
    layers = []
    for i in range(4):
        layers.append(make_layer("rectangle", x=100+i*170, y=200, w=80+i*40, h=120,
                                  fill=(0.5+0.1*i, 0.5, 0.7)))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("3_rects",          fail_3_rects(),          ["expected 4, got 3"]),
    ("misaligned_y",     fail_misaligned_y(),     ["aligned on center_y"]),
    ("different_sizes",  fail_different_sizes(),  ["≠ 80×120"]),
]

"""Task 09 — 12 same-size colored squares in a 4x3 grid via Tidy up."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n=12):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _grid(n=12, rows=3, cols=4, side=80, gap=20):
    layers = []
    palette = [(0.95, 0.3, 0.3), (0.95, 0.6, 0.2), (0.95, 0.9, 0.2),
               (0.4, 0.85, 0.4), (0.2, 0.7, 0.85), (0.2, 0.4, 0.95),
               (0.55, 0.3, 0.95), (0.95, 0.3, 0.7), (0.45, 0.85, 0.85),
               (0.85, 0.45, 0.65), (0.65, 0.85, 0.45), (0.85, 0.85, 0.55)]
    for i in range(n):
        r, c = divmod(i, cols)
        layers.append(make_layer("rectangle", x=100+c*(side+gap), y=100+r*(side+gap),
                                  w=side, h=side, fill=palette[i % 12]))
    frame = make_frame(layers, w=900, h=600)
    return make_log([frame], _events(n))


def perfect():        return _grid()
def perfect_smaller(): return _grid(side=50, gap=10)
def perfect_larger():  return _grid(side=100, gap=24)


def fail_11_squares():    return _grid(n=11)
def fail_in_a_row():
    palette = [(0.95, 0.3, 0.3), (0.95, 0.6, 0.2), (0.95, 0.9, 0.2),
               (0.4, 0.85, 0.4), (0.2, 0.7, 0.85), (0.2, 0.4, 0.95),
               (0.55, 0.3, 0.95), (0.95, 0.3, 0.7), (0.45, 0.85, 0.85),
               (0.85, 0.45, 0.65), (0.65, 0.85, 0.45), (0.85, 0.85, 0.55)]
    layers = [make_layer("rectangle", x=50+i*70, y=200, w=60, h=60, fill=palette[i])
              for i in range(12)]
    frame = make_frame(layers, w=900, h=600)
    return make_log([frame], _events())


def fail_only_3_distinct_colors():
    palette = [(1.0, 0.0, 0.0)]*4 + [(0.0, 1.0, 0.0)]*4 + [(0.0, 0.0, 1.0)]*4
    layers = []
    for i in range(12):
        r, c = divmod(i, 4)
        layers.append(make_layer("rectangle", x=100+c*100, y=100+r*100,
                                  w=80, h=80, fill=palette[i]))
    frame = make_frame(layers, w=900, h=600)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]

FAIL_LOGS = [
    ("11_squares",              fail_11_squares(),              ["expected 12, got 11"]),
    ("in_a_row",                fail_in_a_row(),                ["row clusters"]),
    ("only_3_distinct_colors",  fail_only_3_distinct_colors(),  ["≥12"]),
]

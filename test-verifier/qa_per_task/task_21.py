"""Task 21 — 3 same-size rectangles stacked vertically (16px gap), distinct colors."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events(n=3):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _stack(n=3, w=200, h=60, gap=16, colors=None):
    colors = colors or [(0.95,0.3,0.3),(0.95,0.6,0.2),(0.4,0.85,0.4)]
    layers = []
    for i in range(n):
        layers.append(make_layer("rectangle", x=400, y=100+i*(h+gap), w=w, h=h,
                                  fill=colors[i % len(colors)]))
    return make_log(layers, _events(n))


def perfect():        return _stack()
def perfect_smaller(): return _stack(w=120, h=40, gap=12)
def perfect_larger():  return _stack(w=320, h=80, gap=20)


def fail_2_rects():     return _stack(n=2)
def fail_no_gap():      return _stack(gap=0)
def fail_same_colors(): return _stack(colors=[(0.5,0.5,0.5)]*3)
def fail_different_widths():
    layers = []
    for i in range(3):
        layers.append(make_layer("rectangle", x=400, y=100+i*76, w=200+i*100, h=60,
                                  fill=(0.5+0.1*i, 0.5, 0.5)))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("2_rects",            fail_2_rects(),            ["expected 3, got 2"]),
    ("no_gap",             fail_no_gap(),             ["stacked"]),
    ("same_colors",        fail_same_colors(),        ["≥3"]),
    ("different_widths",   fail_different_widths(),   ["≠ 200×60"]),
]

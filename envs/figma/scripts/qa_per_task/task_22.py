"""Task 22 — 4 same-size rounded pill rectangles in horizontal row, distinct pastel fills."""
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


def _pills(n=4, w=120, h=40, gap=8, radius=999, colors=None):
    colors = colors or [(0.95,0.7,0.7),(0.7,0.95,0.7),(0.7,0.7,0.95),(0.95,0.95,0.7)]
    layers = []
    for i in range(n):
        layers.append(make_layer("rectangle", x=100+i*(w+gap), y=300, w=w, h=h,
                                  fill=colors[i % len(colors)], cornerRadius=radius))
    return make_log(layers, _events(n))


def perfect():       return _pills()
def perfect_smaller(): return _pills(w=80, h=32)
def perfect_uniform_w(): return _pills(w=140, gap=12)


def fail_3_pills():     return _pills(n=3)
def fail_no_radius():   return _pills(radius=0)
def fail_same_color():  return _pills(colors=[(0.95,0.7,0.7)]*4)
def fail_huge_gap():    return _pills(gap=80)


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_uniform_w",perfect_uniform_w()),
]
FAIL_LOGS = [
    ("3_pills",     fail_3_pills(),     ["expected 4, got 3"]),
    ("no_radius",   fail_no_radius(),   ["cornerRadius"]),
    ("same_color",  fail_same_color(),  ["≥4"]),
    ("huge_gap",    fail_huge_gap(),    ["stacked"]),
]

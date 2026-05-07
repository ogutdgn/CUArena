"""Task 26 — 5 same-size squares in row, brand colors."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events(n=5):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _palette(n=5, side=80, gap=12, colors=None):
    colors = colors or [(0.95,0.3,0.3),(0.95,0.6,0.2),(0.95,0.9,0.2),(0.4,0.85,0.4),(0.2,0.4,0.95)]
    layers = []
    for i in range(n):
        layers.append(make_layer("rectangle", x=100+i*(side+gap), y=300, w=side, h=side,
                                  fill=colors[i % len(colors)]))
    return make_log(layers, _events(n))


def perfect():        return _palette()
def perfect_smaller(): return _palette(side=60, gap=8)
def perfect_larger():  return _palette(side=120, gap=20)


def fail_4_squares():     return _palette(n=4)
def fail_same_color():    return _palette(colors=[(0.5,0.5,0.5)]*5)
def fail_different_sizes():
    layers = []
    for i in range(5):
        size = 60 + i*20
        layers.append(make_layer("rectangle", x=100+i*120, y=300, w=size, h=size,
                                  fill=(0.95-i*0.1, 0.3, 0.3)))
    return make_log(layers, _events())
def fail_misaligned_y():
    layers = []
    for i in range(5):
        layers.append(make_layer("rectangle", x=100+i*92, y=300+i*30, w=80, h=80,
                                  fill=(0.95-i*0.1, 0.3, 0.3)))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("4_squares",        fail_4_squares(),        ["expected 5, got 4"]),
    ("same_color",       fail_same_color(),       ["≥5"]),
    ("different_sizes",  fail_different_sizes(),  ["≠ 60×60"]),
    ("misaligned_y",     fail_misaligned_y(),     ["aligned on center_y"]),
]

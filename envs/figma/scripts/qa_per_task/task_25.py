"""Task 25 — 3 identical 160×40 rectangles in horizontal row, all same color."""
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


PURPLE = (0.55, 0.3, 0.95)


def _row(n=3, w=160, h=40, gap=12, colors=None):
    colors = colors or [PURPLE]*n
    layers = []
    for i in range(n):
        layers.append(make_layer("rectangle", x=100+i*(w+gap), y=300,
                                  w=w, h=h, fill=colors[i % len(colors)]))
    return make_log(layers, _events(n))


def perfect():        return _row()
def perfect_other_color(): return _row(colors=[(0.2,0.6,0.9)]*3)
def perfect_more_gap():    return _row(gap=18)


def fail_2_rects():     return _row(n=2)
def fail_different_colors(): return _row(colors=[PURPLE,(0.95,0.3,0.3),(0.4,0.85,0.4)])
def fail_different_sizes():
    # Prompt: "3 identical rectangles (same size, same color)". Adversarial: mixed sizes,
    # not specific dimensions (prompt doesn't pin a size — humans can pick any size).
    layers = [
        make_layer("rectangle", x=100, y=300, w=160, h=40, fill=PURPLE),
        make_layer("rectangle", x=272, y=300, w= 80, h=40, fill=PURPLE),
        make_layer("rectangle", x=372, y=300, w=160, h=80, fill=PURPLE),
    ]
    return make_log(layers, _events())
def fail_misaligned_y():
    layers = [
        make_layer("rectangle", x=100, y=300, w=160, h=40, fill=PURPLE),
        make_layer("rectangle", x=272, y=400, w=160, h=40, fill=PURPLE),
        make_layer("rectangle", x=444, y=300, w=160, h=40, fill=PURPLE),
    ]
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_other_color",perfect_other_color()),
    ("perfect_more_gap",   perfect_more_gap()),
]
FAIL_LOGS = [
    ("2_rects",          fail_2_rects(),          ["expected 3, got 2"]),
    ("different_colors", fail_different_colors(), ["differs from"]),
    ("different_sizes",  fail_different_sizes(),  ["≠"]),  # LayersSameDimensions fires
    ("misaligned_y",     fail_misaligned_y(),     ["aligned on center_y"]),
]

"""Task 10 — 4 nested squares with shared center, alternating two colors."""
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


def _nested(sizes, colors):
    cx, cy = 500, 500
    layers = []
    for sz, c in zip(sizes, colors):
        layers.append(make_layer("rectangle", x=cx-sz/2, y=cy-sz/2,
                                  w=sz, h=sz, fill=c))
    return make_log(layers, _events(n=len(sizes)))


C1 = (0.0, 0.0, 0.0)
C2 = (1.0, 1.0, 1.0)


def perfect():           return _nested([240, 180, 120, 60], [C1, C2, C1, C2])
def perfect_diff_palette():return _nested([240, 180, 120, 60], [(0.8,0.2,0.2),(0.95,0.95,0.95),(0.8,0.2,0.2),(0.95,0.95,0.95)])
def perfect_smaller():   return _nested([200, 150, 100, 50], [C1, C2, C1, C2])


def fail_3_squares():    return _nested([240, 180, 120], [C1, C2, C1])
def fail_not_concentric():
    cx, cy = 500, 500
    layers = []
    sizes = [240, 180, 120, 60]
    colors = [C1, C2, C1, C2]
    for i, (sz, c) in enumerate(zip(sizes, colors)):
        layers.append(make_layer("rectangle", x=cx-sz/2 + i*50, y=cy-sz/2,
                                  w=sz, h=sz, fill=c))
    return make_log(layers, _events())
def fail_not_nested():
    """4 same-size squares all at center — they overlap perfectly but no nesting."""
    cx, cy = 500, 500
    sz = 100
    layers = [make_layer("rectangle", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz, fill=c)
              for c in [C1, C2, C1, C2]]
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",             perfect()),
    ("perfect_diff_palette",perfect_diff_palette()),
    ("perfect_smaller",     perfect_smaller()),
]

FAIL_LOGS = [
    ("3_squares",         fail_3_squares(),         ["expected 4, got 3"]),
    ("not_concentric",    fail_not_concentric(),    ["concentric"]),
]

"""Task 11 — 3 nested triangles concentric, alternating two colors."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n=3):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(n):
        sem.append(make_event("create_polygon"))
    return sem


def _nested(sizes, colors, frame_w=1280, frame_h=832):
    cx, cy = 640, 416
    layers = []
    for sz, c in zip(sizes, colors):
        layers.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                  fill=c, sides=3))
    frame = make_frame(layers, w=frame_w, h=frame_h)
    return make_log([frame], _events(n=len(sizes)))


C1 = (0.95, 0.3, 0.3)
C2 = (1.0, 1.0, 1.0)


def perfect():
    return _nested([400, 280, 160], [C1, C2, C1])


def perfect_smaller():
    return _nested([300, 200, 100], [C1, C2, C1])


def perfect_other_palette():
    return _nested([400, 280, 160], [(0.2, 0.4, 0.85), (1.0, 1.0, 1.0), (0.2, 0.4, 0.85)])


def fail_2_triangles():
    return _nested([400, 280], [C1, C2])


def fail_not_concentric():
    cx, cy = 640, 416
    sizes, colors = [400, 280, 160], [C1, C2, C1]
    layers = []
    for i, (sz, c) in enumerate(zip(sizes, colors)):
        layers.append(make_layer("polygon", x=cx-sz/2 + i*100, y=cy-sz/2,
                                  w=sz, h=sz, fill=c, sides=3))
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",                perfect()),
    ("perfect_smaller",        perfect_smaller()),
    ("perfect_other_palette",  perfect_other_palette()),
]
FAIL_LOGS = [
    ("2_triangles",     fail_2_triangles(),     ["expected 3, got 2"]),
    ("not_concentric",  fail_not_concentric(),  ["concentric"]),
]

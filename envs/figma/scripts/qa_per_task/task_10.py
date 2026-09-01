"""Task 10 — 4 nested squares with shared center, alternating two colors."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _nested(sizes, colors, frame_w=1280, frame_h=832):
    cx, cy = 640, 416
    layers = []
    for sz, c in zip(sizes, colors):
        layers.append(make_layer("rectangle", x=cx-sz/2, y=cy-sz/2,
                                  w=sz, h=sz, fill=c))
    frame = make_frame(layers, w=frame_w, h=frame_h)
    return make_log([frame], _events(n=len(sizes)))


C1 = (0.0, 0.0, 0.0)
C2 = (1.0, 1.0, 1.0)


def perfect():
    """4 nested with strong area-ratio decrease."""
    return _nested([400, 280, 160, 60], [C1, C2, C1, C2])


def perfect_diff_palette():
    return _nested([400, 280, 160, 60],
                   [(0.8, 0.2, 0.2), (0.95, 0.95, 0.95), (0.8, 0.2, 0.2), (0.95, 0.95, 0.95)])


def perfect_smaller():
    return _nested([300, 200, 120, 50], [C1, C2, C1, C2])


def fail_3_squares():
    return _nested([400, 280, 160], [C1, C2, C1])


def fail_not_concentric():
    cx, cy = 640, 416
    layers = []
    sizes = [400, 280, 160, 60]
    colors = [C1, C2, C1, C2]
    for i, (sz, c) in enumerate(zip(sizes, colors)):
        layers.append(make_layer("rectangle", x=cx-sz/2 + i*100, y=cy-sz/2,
                                  w=sz, h=sz, fill=c))
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], _events())


def fail_not_nested():
    """4 same-size squares all at center — overlap perfectly but no nesting."""
    cx, cy = 640, 416
    sz = 100
    layers = [make_layer("rectangle", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz, fill=c)
              for c in [C1, C2, C1, C2]]
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], _events())


def fail_non_alternating_colors():
    """4 nested squares, but colors don't alternate by area: [A, A, B, B]
    instead of [A, B, A, B]."""
    return _nested([400, 280, 160, 60], [C1, C1, C2, C2])


PASS_LOGS = [
    ("perfect",             perfect()),
    ("perfect_diff_palette",perfect_diff_palette()),
    ("perfect_smaller",     perfect_smaller()),
]

FAIL_LOGS = [
    ("3_squares",                 fail_3_squares(),                 ["expected 4, got 3"]),
    ("not_concentric",            fail_not_concentric(),            ["concentric"]),
    ("not_nested",                fail_not_nested(),                ["not strictly smaller"]),
    ("non_alternating_colors",    fail_non_alternating_colors(),    ["alternating"]),
]

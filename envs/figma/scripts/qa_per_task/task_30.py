"""Task 30 — 6 vertical stripes alternating deep-blue/cream filling a frame."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


DEEP_BLUE = (0.10, 0.20, 0.55)
CREAM     = (1.00, 0.95, 0.80)


def _events(n=6):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _stripes(colors=None, w=100, h=600, frame_w=600, frame_h=600):
    colors = colors or [DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE, CREAM]
    layers = []
    for i, c in enumerate(colors):
        layers.append(make_layer("rectangle", x=i*w, y=0, w=w, h=h, fill=c))
    frame = make_frame(layers, w=frame_w, h=frame_h)
    return make_log([frame], _events(n=len(colors)))


def perfect():        return _stripes()
# perfect_smaller / perfect_larger keep the 600×600 frame intact while varying stripe geometry.
def perfect_smaller(): return _stripes(w=60, h=400)
def perfect_larger():  return _stripes(w=100, h=600)  # bound to 600×600 frame


def fail_5_stripes():        return _stripes(colors=[DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE])
def fail_color_order_random():
    return _stripes(colors=[CREAM, DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE])
def fail_3_colors():
    return _stripes(colors=[DEEP_BLUE, CREAM, (0.95, 0.3, 0.3),
                            DEEP_BLUE, CREAM, (0.95, 0.3, 0.3)])
def fail_horizontal_stripes():
    layers = []
    for i, c in enumerate([DEEP_BLUE, CREAM, DEEP_BLUE, CREAM, DEEP_BLUE, CREAM]):
        layers.append(make_layer("rectangle", x=0, y=i*100, w=600, h=100, fill=c))
    frame = make_frame(layers, w=600, h=600)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("5_stripes",            fail_5_stripes(),            ["expected 6, got 5"]),
    ("color_order_random",   fail_color_order_random(),   ["color mismatch"]),
    ("3_colors",             fail_3_colors(),             ["color mismatch"]),
    ("horizontal_stripes",   fail_horizontal_stripes(),   ["ratio=0.17 < 2.0"]),
]

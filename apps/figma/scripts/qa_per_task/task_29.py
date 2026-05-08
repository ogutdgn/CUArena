"""Task 29 — Off-white frame + 4 same-color circles in 2×2 grid via Tidy up."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n_e=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(n_e):
        sem.append(make_event("create_ellipse"))
    sem.append(make_event("align_layers", axis="center_x"))
    return sem


OFF_WHITE = (0.97, 0.95, 0.92)
BRAND     = (0.95, 0.3, 0.5)


def _grid(side=60, gap=40, color=BRAND, frame_fill=OFF_WHITE, n=4):
    layers = []
    for i in range(n):
        r, c = divmod(i, 2)
        layers.append(make_layer("ellipse", x=100+c*(side+gap), y=100+r*(side+gap),
                                  w=side, h=side, fill=color))
    frame = make_frame(layers, w=400, h=400, fill=frame_fill)
    return make_log([frame], _events(n_e=n))


def perfect():        return _grid()
def perfect_smaller(): return _grid(side=40, gap=30)
def perfect_larger():  return _grid(side=80, gap=60)


def fail_3_circles():        return _grid(n=3)
def fail_different_colors():
    colors = [BRAND, (0.3,0.5,0.95), (0.4,0.85,0.4), (0.95,0.6,0.2)]
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        layers.append(make_layer("ellipse", x=100+c*100, y=100+r*100, w=60, h=60,
                                  fill=colors[i]))
    frame = make_frame(layers, w=400, h=400, fill=OFF_WHITE)
    return make_log([frame], _events())
def fail_in_a_row():
    layers = []
    for i in range(4):
        layers.append(make_layer("ellipse", x=100+i*100, y=200, w=60, h=60, fill=BRAND))
    frame = make_frame(layers, w=600, h=400, fill=OFF_WHITE)
    return make_log([frame], _events())
def fail_wrong_frame_color(): return _grid(frame_fill=(0.2, 0.2, 0.2))
def fail_no_align_event():
    log = perfect()
    log["semantic"] = [e for e in log["semantic"] if e.get("name") != "align_layers"]
    return log


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("3_circles",            fail_3_circles(),            ["expected 4, got 3"]),
    ("different_colors",     fail_different_colors(),     ["differs from"]),
    ("in_a_row",             fail_in_a_row(),             ["row clusters"]),
    ("wrong_frame_color",    fail_wrong_frame_color(),    ["No frame with solid"]),
    ("no_align_event",       fail_no_align_event(),       ["align"]),
]

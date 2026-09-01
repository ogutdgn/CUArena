"""Task 20 — Dark navy frame + 2 overlapping blurred circles (distinct fills)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_layer_blur,
    NAVY, MAGENTA, CYAN,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="frame"),
        make_event("tool_change", before="frame", after="ellipse"),
        make_event("create_ellipse"),
        make_event("create_ellipse"),
    ]


def _glow(c1=MAGENTA, c2=CYAN, blur=80, frame_color=NAVY, overlap=True):
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=c1,
                    effects=[make_layer_blur(radius=blur)])
    e2x = 360 if overlap else 700
    e2 = make_layer("ellipse", x=e2x, y=320, w=200, h=200, fill=c2,
                    effects=[make_layer_blur(radius=blur)])
    frame = make_frame([e1, e2], w=900, h=900, fill=frame_color)
    return make_log([frame], _events())


def perfect():        return _glow()
def perfect_diff_colors(): return _glow(c1=(1.0,0.3,0.3), c2=(0.3,0.3,1.0))
def perfect_smaller_blur(): return _glow(blur=40)


def fail_no_blur():
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA)
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN)
    frame = make_frame([e1, e2], w=900, h=900, fill=NAVY)
    return make_log([frame], _events())
def fail_not_overlapping(): return _glow(overlap=False)
def fail_same_color():      return _glow(c1=MAGENTA, c2=MAGENTA)
def fail_wrong_frame_color(): return _glow(frame_color=(0.95, 0.95, 0.95))


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_diff_colors",perfect_diff_colors()),
    ("perfect_smaller_blur", perfect_smaller_blur()),
    ("perfect_no_blur",    fail_no_blur()),
]
FAIL_LOGS = [
    ("not_overlapping",    fail_not_overlapping(),    ["overlap"]),
    ("same_color",         fail_same_color(),         ["≥2"]),
    ("wrong_frame_color",  fail_wrong_frame_color(),  ["No frame with solid"]),
]

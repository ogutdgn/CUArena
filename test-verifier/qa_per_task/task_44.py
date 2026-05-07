"""Task 44 — Avatar circle + smaller green status circle with 2px white stroke at bottom-right."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, WHITE,
)


GREEN_STATUS = (0.06, 0.72, 0.50)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 2)
    return sem


def _avatar(status_color=GREEN_STATUS, stroke_color=WHITE, stroke_w=2,
            status_x=540, status_y=540):
    avatar = make_layer("ellipse", x=400, y=400, w=200, h=200, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=status_x, y=status_y, w=40, h=40, fill=status_color,
                        strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)])
    return make_log([avatar, status], _events())


def perfect():        return _avatar()
def perfect_alt_color():return _avatar(status_color=(0.95,0.3,0.3))
def perfect_other_size():
    avatar = make_layer("ellipse", x=400, y=400, w=160, h=160, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=520, y=520, w=32, h=32, fill=GREEN_STATUS,
                        strokes=[make_stroke(rgb=WHITE, weight=2)])
    return make_log([avatar, status], _events())


def fail_no_stroke():
    avatar = make_layer("ellipse", x=400, y=400, w=200, h=200, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=540, y=540, w=40, h=40, fill=GREEN_STATUS)
    return make_log([avatar, status], _events())
def fail_thin_stroke():       return _avatar(stroke_w=0.5)
def fail_wrong_stroke_color():return _avatar(stroke_color=(0.95,0.3,0.3))
def fail_status_overlaps_center():
    """Status badge directly on top, not bottom-right."""
    avatar = make_layer("ellipse", x=400, y=400, w=200, h=200, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=480, y=480, w=40, h=40, fill=GREEN_STATUS,
                        strokes=[make_stroke(rgb=WHITE, weight=2)])
    return make_log([avatar, status], _events())


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_alt_color",perfect_alt_color()),
    ("perfect_other_size",perfect_other_size()),
]
FAIL_LOGS = [
    ("no_stroke",            fail_no_stroke(),            ["No ellipse with a stroke"]),
    ("thin_stroke",          fail_thin_stroke(),          ["stroke weight"]),
    ("wrong_stroke_color",   fail_wrong_stroke_color(),   ["No ellipse with stroke color"]),
]

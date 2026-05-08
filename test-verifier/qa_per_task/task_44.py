"""Task 44 — Avatar circle + smaller green status circle with 2px white stroke at bottom-right."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, WHITE,
)


GREEN_STATUS = (0.06, 0.72, 0.50)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 2)
    return sem


def _wrap(layers):
    return make_log([make_frame(layers, w=1280, h=832)], _events())


def _avatar(status_color=GREEN_STATUS, stroke_color=WHITE, stroke_w=2,
            status_x=740, status_y=480):
    avatar = make_layer("ellipse", x=480, y=216, w=320, h=320, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=status_x, y=status_y, w=80, h=80, fill=status_color,
                        strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)])
    return _wrap([avatar, status])


def perfect():        return _avatar()
def perfect_alt_color():return _avatar(status_color=(0.95,0.3,0.3))
def perfect_other_size():
    avatar = make_layer("ellipse", x=520, y=256, w=240, h=240, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=700, y=440, w=60, h=60, fill=GREEN_STATUS,
                        strokes=[make_stroke(rgb=WHITE, weight=2)])
    return _wrap([avatar, status])


def fail_no_stroke():
    avatar = make_layer("ellipse", x=480, y=216, w=320, h=320, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=740, y=480, w=80, h=80, fill=GREEN_STATUS)
    return _wrap([avatar, status])
def fail_thin_stroke():       return _avatar(stroke_w=0.5)
def fail_wrong_stroke_color():return _avatar(stroke_color=(0.95,0.3,0.3))
def fail_status_overlaps_center():
    """Status badge directly on top, not bottom-right."""
    avatar = make_layer("ellipse", x=480, y=216, w=320, h=320, fill=(0.85,0.7,0.6))
    status = make_layer("ellipse", x=600, y=336, w=80, h=80, fill=GREEN_STATUS,
                        strokes=[make_stroke(rgb=WHITE, weight=2)])
    return _wrap([avatar, status])


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

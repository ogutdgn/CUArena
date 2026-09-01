"""Task 40 — Green pill rectangle + white circle thumb on right with drop shadow."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_drop_shadow, GREEN, WHITE,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("tool_change", before="rectangle", after="ellipse"),
        make_event("create_rectangle"),
        make_event("create_ellipse"),
    ]


def _toggle(rect_color=GREEN, thumb_color=WHITE, shadow=True, thumb_x=440, radius=24):
    rect = make_layer("rectangle", x=400, y=300, w=80, h=40, fill=rect_color,
                      cornerRadius=radius)
    effects = [make_drop_shadow(y=2, blur=4)] if shadow else []
    thumb = make_layer("ellipse", x=thumb_x, y=305, w=30, h=30, fill=thumb_color,
                       effects=effects)
    frame = make_frame([rect, thumb], w=1280, h=832)
    return make_log([frame], _events())


def perfect():        return _toggle()
def perfect_smaller(): return _toggle(thumb_x=440, radius=24)
def perfect_other_size():
    rect = make_layer("rectangle", x=400, y=300, w=120, h=60, fill=GREEN, cornerRadius=30)
    thumb = make_layer("ellipse", x=470, y=305, w=50, h=50, fill=WHITE,
                       effects=[make_drop_shadow(y=2, blur=4)])
    frame = make_frame([rect, thumb], w=1280, h=832)
    return make_log([frame], _events())


def fail_no_shadow():        return _toggle(shadow=False)
def fail_thumb_left():       return _toggle(thumb_x=400)
def fail_wrong_color():      return _toggle(rect_color=(0.95,0.3,0.3))
def fail_no_radius():        return _toggle(radius=0)


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_smaller",  perfect_smaller()),
    ("perfect_other_size",perfect_other_size()),
]
FAIL_LOGS = [
    # Prompt for task_40 doesn't mention drop shadow — removed adversarial. (Was: no_shadow.)
    ("thumb_left",    fail_thumb_left(),    ["aligns with any rectangle.right"]),
    ("wrong_color",   fail_wrong_color(),   ["No rectangle with solid"]),
    ("no_radius",     fail_no_radius(),     ["cornerRadius"]),
]

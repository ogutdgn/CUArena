"""Task 05 — Plus sign from 2 perpendicular rectangles centered together (same color)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, RED,
)
BLUE = (0.1, 0.3, 0.8)

def _events():
    return [make_event("session_start"),
            make_event("tool_change", before="select", after="rectangle"),
            make_event("create_rectangle"),
            make_event("create_rectangle")]


def _plus_log(h_size=(200, 60), v_size=(60, 200), color=RED, hx_offset=0, hy_offset=0,
              v_color=None):
    cx, cy = 500, 500
    v_color = v_color if v_color is not None else color
    h_rect = make_layer("rectangle",
                        x=cx - h_size[0]/2 + hx_offset, y=cy - h_size[1]/2,
                        w=h_size[0], h=h_size[1], fill=color)
    v_rect = make_layer("rectangle",
                        x=cx - v_size[0]/2, y=cy - v_size[1]/2 + hy_offset,
                        w=v_size[0], h=v_size[1], fill=v_color)
    return make_log([h_rect, v_rect], _events())


def perfect():        return _plus_log()
def perfect_smaller():return _plus_log(h_size=(120, 40), v_size=(40, 120))
def perfect_larger(): return _plus_log(h_size=(300, 80), v_size=(80, 300))
def perfect_blue():   return _plus_log(color=BLUE)  # same color, just not red — prompt is unspecific


def fail_misaligned():            return _plus_log(hx_offset=80, hy_offset=80)
def fail_both_horizontal():
    """Both rectangles wide, not crossing — fails AspectMix 1H/1V."""
    return _plus_log(h_size=(200, 60), v_size=(180, 50))
def fail_two_different_colors():
    """One rect red, the other blue — fails 'pick same color for both'."""
    return _plus_log(color=RED, v_color=BLUE)
def fail_only_one_rect():
    h = make_layer("rectangle", x=400, y=470, w=200, h=60, fill=RED)
    return make_log([h], [make_event("session_start"),
                          make_event("tool_change", before="select", after="rectangle"),
                          make_event("create_rectangle")])


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
    ("perfect_blue",    perfect_blue()),
]

FAIL_LOGS = [
    ("misaligned",            fail_misaligned(),            ["aligned on center"]),
    ("both_horizontal",       fail_both_horizontal(),       ["2 horizontal, 0 vertical"]),
    ("two_different_colors",  fail_two_different_colors(),  ["differs from #0"]),
    ("only_one_rect",         fail_only_one_rect(),         ["expected 2"]),
]

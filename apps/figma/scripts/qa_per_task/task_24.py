"""Task 24 — Outer frame + white rounded rectangle centered with drop shadow + AlignToolUsed."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_drop_shadow, WHITE,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("create_rectangle"),
        make_event("align_layers", axis="center_x"),
        make_event("align_layers", axis="center_y"),
    ]


def _modal(w=480, h=320, radius=16, color=WHITE, shadow=True):
    effects = [make_drop_shadow(y=8, blur=16)] if shadow else []
    modal = make_layer("rectangle", x=720-w/2, y=450-h/2, w=w, h=h, fill=color,
                       cornerRadius=radius, effects=effects)
    frame = make_frame([modal], w=1440, h=900)
    return make_log([frame], _events())


def perfect():        return _modal()
def perfect_smaller(): return _modal(w=360, h=240)
def perfect_taller():  return _modal(w=400, h=400)


def fail_no_shadow():       return _modal(shadow=False)
def fail_not_white():       return _modal(color=(0.5, 0.5, 0.5))
def fail_no_radius():       return _modal(radius=0)
def fail_off_center():
    modal = make_layer("rectangle", x=100, y=100, w=480, h=320, fill=WHITE,
                       cornerRadius=16, effects=[make_drop_shadow(y=8, blur=16)])
    frame = make_frame([modal], w=1440, h=900)
    return make_log([frame], _events())
def fail_no_align_event():
    log = _modal()
    log["semantic"] = [e for e in log["semantic"] if e.get("name") != "align_layers"]
    return log


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_taller",  perfect_taller()),
]
FAIL_LOGS = [
    ("no_shadow",       fail_no_shadow(),       ["drop shadow"]),
    ("not_white",       fail_not_white(),       ["color mismatch"]),
    ("no_radius",       fail_no_radius(),       ["cornerRadius"]),
    ("off_center",      fail_off_center(),      ["centered"]),
    ("no_align_event",  fail_no_align_event(),  ["align"]),
]

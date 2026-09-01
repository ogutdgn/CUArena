"""Task 23 — Frame + dark-gray sidebar (left, stretch vertical) with constraints."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event, DARK_GRAY


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="frame"),
        make_event("tool_change", before="frame", after="rectangle"),
        make_event("create_rectangle"),
    ]


def _sidebar(width=240, h_constraint="left", v_constraint="stretch", color=DARK_GRAY):
    sb = make_layer("rectangle", x=0, y=0, w=width, h=900, fill=color,
                    constraints={"horizontal": h_constraint, "vertical": v_constraint})
    frame = make_frame([sb], w=1440, h=900)
    return make_log([frame], _events())


def perfect():        return _sidebar()
def perfect_narrower(): return _sidebar(width=160)
def perfect_wider():    return _sidebar(width=320)


def fail_wrong_h_constraint(): return _sidebar(h_constraint="right")
def fail_wrong_v_constraint(): return _sidebar(v_constraint="top")
def fail_too_wide():           return _sidebar(width=600)
def fail_wrong_color():        return _sidebar(color=(1.0,1.0,1.0))


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_narrower", perfect_narrower()),
    ("perfect_wider",    perfect_wider()),
]
FAIL_LOGS = [
    ("wrong_h_constraint", fail_wrong_h_constraint(), ["wrong horizontal constraint"]),
    ("wrong_v_constraint", fail_wrong_v_constraint(), ["wrong vertical constraint"]),
    ("too_wide",           fail_too_wide(),           ["width fraction"]),
    ("wrong_color",        fail_wrong_color(),        ["No rectangle with solid"]),
]

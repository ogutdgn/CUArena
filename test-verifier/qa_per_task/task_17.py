"""Task 17 — Hourglass: 2 triangles (point-to-point) + 2 rectangle caps top and bottom."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("tool_change", before="polygon", after="rectangle")]
    sem.extend([make_event("create_polygon")] * 2)
    sem.extend([make_event("create_rectangle")] * 2)
    return sem


def _hourglass(angles=(0, 180)):
    cx = 500
    p_top = make_layer("polygon", x=cx-50, y=200, w=100, h=100, fill=(0.5,0.4,0.7),
                       sides=3, rotation=angles[0])
    p_bot = make_layer("polygon", x=cx-50, y=300, w=100, h=100, fill=(0.5,0.4,0.7),
                       sides=3, rotation=angles[1])
    cap_top = make_layer("rectangle", x=cx-100, y=180, w=200, h=20, fill=(0.6,0.5,0.7))
    cap_bot = make_layer("rectangle", x=cx-100, y=400, w=200, h=20, fill=(0.6,0.5,0.7))
    return make_log([p_top, p_bot, cap_top, cap_bot], _events())


def perfect():       return _hourglass()
def perfect_alt():
    log = _hourglass()
    for c in log["outcome"]["document"]["pages"][0]["children"]:
        c["x"] -= 100
    return log
def perfect_smaller():
    cx = 500
    p_top = make_layer("polygon", x=cx-30, y=240, w=60, h=60, fill=(0.5,0.4,0.7),
                       sides=3, rotation=0)
    p_bot = make_layer("polygon", x=cx-30, y=300, w=60, h=60, fill=(0.5,0.4,0.7),
                       sides=3, rotation=180)
    cap_top = make_layer("rectangle", x=cx-50, y=220, w=100, h=20, fill=(0.6,0.5,0.7))
    cap_bot = make_layer("rectangle", x=cx-50, y=360, w=100, h=20, fill=(0.6,0.5,0.7))
    return make_log([p_top, p_bot, cap_top, cap_bot], _events())


def fail_one_triangle():
    cx = 500
    p_top = make_layer("polygon", x=cx-50, y=200, w=100, h=100, fill=(0.5,0.4,0.7),
                       sides=3, rotation=0)
    cap_top = make_layer("rectangle", x=cx-100, y=180, w=200, h=20, fill=(0.6,0.5,0.7))
    cap_bot = make_layer("rectangle", x=cx-100, y=400, w=200, h=20, fill=(0.6,0.5,0.7))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("tool_change", before="polygon", after="rectangle"),
           make_event("create_polygon"),
           make_event("create_rectangle"),
           make_event("create_rectangle")]
    return make_log([p_top, cap_top, cap_bot], sem)
def fail_both_pointing_up():        return _hourglass(angles=(0, 0))
def fail_no_caps():
    cx = 500
    p_top = make_layer("polygon", x=cx-50, y=200, w=100, h=100, fill=(0.5,0.4,0.7),
                       sides=3, rotation=0)
    p_bot = make_layer("polygon", x=cx-50, y=300, w=100, h=100, fill=(0.5,0.4,0.7),
                       sides=3, rotation=180)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("create_polygon"),
           make_event("create_polygon")]
    return make_log([p_top, p_bot], sem)


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_alt",     perfect_alt()),
    ("perfect_smaller", perfect_smaller()),
]
FAIL_LOGS = [
    ("one_triangle",        fail_one_triangle(),        ["expected 2, got 1"]),
    ("both_pointing_up",    fail_both_pointing_up(),    ["Need 1 polygon at 180"]),
    ("no_caps",             fail_no_caps(),             ["expected 2, got 0"]),
]

"""Task 13 — 4 lines (2 vertical 0°, 2 horizontal 90°) forming a # hashtag."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, make_stroke


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(n):
        sem.append(make_event("create_line"))
    return sem


def _line(x, y, w, h, rotation):
    return make_layer("line", x=x, y=y, w=w, h=h, fill=None,
                      strokes=[make_stroke(rgb=(1,1,1), weight=2)],
                      rotation=rotation)


def perfect():
    """2 vertical lines + 2 horizontal lines crossing."""
    layers = [
        _line(400, 200, 4, 200, 0),
        _line(500, 200, 4, 200, 0),
        _line(350, 270, 200, 4, 90),
        _line(350, 330, 200, 4, 90),
    ]
    return make_log(layers, _events())


def perfect_smaller():
    layers = [
        _line(400, 250, 4, 100, 0),
        _line(450, 250, 4, 100, 0),
        _line(380, 280, 100, 4, 90),
        _line(380, 320, 100, 4, 90),
    ]
    return make_log(layers, _events())


def perfect_larger():
    layers = [
        _line(400, 100, 4, 400, 0),
        _line(550, 100, 4, 400, 0),
        _line(300, 200, 400, 4, 90),
        _line(300, 350, 400, 4, 90),
    ]
    return make_log(layers, _events())


def fail_3_lines():
    layers = [
        _line(400, 200, 4, 200, 0),
        _line(500, 200, 4, 200, 0),
        _line(350, 270, 200, 4, 90),
    ]
    return make_log(layers, _events(n=3))


def fail_all_same_rotation():
    layers = [_line(100+i*100, 200, 4, 200, 0) for i in range(4)]
    return make_log(layers, _events())


def fail_diagonal_lines():
    layers = [_line(100+i*100, 200, 4, 200, 45*(i+1)) for i in range(4)]
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("3_lines",            fail_3_lines(),            ["expected 4, got 3"]),
    ("all_same_rotation",  fail_all_same_rotation(),  ["Need 2 line at 90"]),
    ("diagonal_lines",     fail_diagonal_lines(),     ["Need 2 line at"]),
]

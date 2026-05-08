"""Task 13 — 4 lines (2 vertical 0°, 2 horizontal 90°) forming a # hashtag."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event, make_stroke


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(n):
        sem.append(make_event("create_line"))
    return sem


def _line(x, y, w, h, rotation):
    layer = make_layer("line", x=x, y=y, w=w, h=h, fill=(0.05, 0.05, 0.05),
                       strokes=[make_stroke(rgb=(0.05, 0.05, 0.05), weight=2)],
                       rotation=rotation)
    return layer


def _wrap(layers, n=4):
    frame = make_frame(layers, w=1280, h=832, fill=(0.95, 0.95, 0.95))
    return make_log([frame], _events(n))


def perfect():
    """2 horizontal + 2 vertical lines crossing (rotation distinguishes)."""
    layers = [
        _line(300, 270, 300, 4, 0),    # horizontal
        _line(300, 400, 300, 4, 0),    # horizontal
        _line(300, 200, 300, 4, 90),   # vertical
        _line(420, 200, 300, 4, 90),   # vertical
    ]
    return _wrap(layers)


def perfect_smaller():
    layers = [
        _line(380, 280, 200, 4, 0),
        _line(380, 320, 200, 4, 0),
        _line(380, 250, 200, 4, 90),
        _line(440, 250, 200, 4, 90),
    ]
    return _wrap(layers)


def perfect_larger():
    layers = [
        _line(200, 270, 500, 4, 0),
        _line(200, 500, 500, 4, 0),
        _line(200, 200, 500, 4, 90),
        _line(380, 200, 500, 4, 90),
    ]
    return _wrap(layers)


def fail_3_lines():
    layers = [
        _line(300, 270, 300, 4, 0),
        _line(300, 400, 300, 4, 0),
        _line(300, 200, 300, 4, 90),
    ]
    return _wrap(layers, n=3)


def fail_all_same_rotation():
    layers = [_line(100+i*150, 200, 300, 4, 0) for i in range(4)]
    return _wrap(layers)


def fail_diagonal_lines():
    layers = [_line(100+i*100, 200, 300, 4, 45*(i+1)) for i in range(4)]
    return _wrap(layers)


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

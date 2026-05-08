"""Task 33 — Teal base circle + 2 colored wedge triangles layered on top."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, TEAL


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="ellipse"),
        make_event("tool_change", before="ellipse", after="polygon"),
        make_event("create_ellipse"),
        make_event("create_polygon"),
        make_event("create_polygon"),
    ]


def _pie(base=TEAL, w1=(0.95,0.4,0.4), w2=(0.95,0.85,0.2), n_wedges=2):
    cx, cy = 500, 500
    base_circle = make_layer("ellipse", x=cx-150, y=cy-150, w=300, h=300, fill=base)
    layers = [base_circle]
    if n_wedges >= 1:
        layers.append(make_layer("polygon", x=cx-30, y=cy-150, w=60, h=300, fill=w1,
                                  sides=3, rotation=30))
    if n_wedges >= 2:
        layers.append(make_layer("polygon", x=cx-30, y=cy-150, w=60, h=300, fill=w2,
                                  sides=3, rotation=120))
    return make_log(layers, _events())


def perfect():        return _pie()
def perfect_other_wedges(): return _pie(w1=(0.55,0.3,0.95), w2=(0.95,0.6,0.2))
def perfect_smaller():
    cx, cy = 500, 500
    base_circle = make_layer("ellipse", x=cx-100, y=cy-100, w=200, h=200, fill=TEAL)
    w1 = make_layer("polygon", x=cx-20, y=cy-100, w=40, h=200, fill=(0.95,0.4,0.4),
                     sides=3, rotation=30)
    w2 = make_layer("polygon", x=cx-20, y=cy-100, w=40, h=200, fill=(0.95,0.85,0.2),
                     sides=3, rotation=120)
    return make_log([base_circle, w1, w2], _events())


def fail_no_base():
    cx, cy = 500, 500
    w1 = make_layer("polygon", x=cx-30, y=cy-150, w=60, h=300, fill=(0.95,0.4,0.4),
                     sides=3, rotation=30)
    w2 = make_layer("polygon", x=cx-30, y=cy-150, w=60, h=300, fill=(0.95,0.85,0.2),
                     sides=3, rotation=120)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("create_polygon"),
           make_event("create_polygon")]
    return make_log([w1, w2], sem)
def fail_wrong_base_color(): return _pie(base=(0.5,0.5,0.5))
def fail_no_wedges():
    cx, cy = 500, 500
    base_circle = make_layer("ellipse", x=cx-150, y=cy-150, w=300, h=300, fill=TEAL)
    sem = [make_event("session_start"),
           make_event("create_ellipse")]
    return make_log([base_circle], sem)


PASS_LOGS = [
    ("perfect",              perfect()),
    ("perfect_other_wedges", perfect_other_wedges()),
    ("perfect_smaller",      perfect_smaller()),
]
FAIL_LOGS = [
    ("no_base",            fail_no_base(),            ["expected 1, got 0"]),
    ("wrong_base_color",   fail_wrong_base_color(),   ["No ellipse with solid"]),
    ("no_wedges",          fail_no_wedges(),          ["expected 2, got 0"]),
]

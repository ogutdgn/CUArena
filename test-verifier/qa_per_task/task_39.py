"""Task 39 — 2 pen-tool arcs (6px navy stroke) + small navy filled circle below."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, NAVY,
)


def _events(n_arcs=2):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(n_arcs):
        sem.append(make_event("create_vector"))
    sem.append(make_event("create_ellipse"))
    return sem


def _wifi(n_arcs=2, stroke_w=6, stroke_color=NAVY, dot_color=NAVY):
    arcs = []
    for i in range(n_arcs):
        arcs.append(make_layer("vector", x=300-50*i, y=200-30*i,
                                w=200+100*i, h=100+50*i, fill=None,
                                strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)]))
    dot = make_layer("ellipse", x=400, y=380, w=20, h=20, fill=dot_color)
    return make_log([*arcs, dot], _events(n_arcs))


def perfect():        return _wifi()
def perfect_thicker(): return _wifi(stroke_w=8)
def perfect_more_arcs():return _wifi(n_arcs=3)


def fail_one_arc():        return _wifi(n_arcs=1)
def fail_thin_stroke():    return _wifi(stroke_w=1)
def fail_wrong_color():    return _wifi(stroke_color=(0.95,0.3,0.3))


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_thicker",  perfect_thicker()),
    ("perfect_more_arcs",perfect_more_arcs()),
]
FAIL_LOGS = [
    ("one_arc",         fail_one_arc(),         ["≥2"]),
    ("thin_stroke",     fail_thin_stroke(),     ["stroke weight"]),
    ("wrong_color",     fail_wrong_color(),     ["No vector with stroke color"]),
]

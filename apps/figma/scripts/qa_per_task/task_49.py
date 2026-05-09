"""Task 49 — 1 pen-tool S-curve with bezier handles + 12px dashed stroke (ribbon)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, make_stroke


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="pen"),
        make_event("create_vector"),
    ]


def _curved_network():
    """An S-curve has 3 anchors with bezier handles on the middle segments."""
    return {
        "vertices": [],
        "segments": [
            {"handleFrom": {"x": 0.20, "y": -0.40},
             "handleTo":   {"x": 0.40, "y":  0.40}},
            {"handleFrom": {"x": 0.60, "y": -0.40},
             "handleTo":   {"x": 0.80, "y":  0.40}},
        ],
        "closed": False,
    }


def _ribbon(stroke_w=12, dashed=True, color=(0.85, 0.65, 0.13), with_curves=True):
    dash = {"dash": 8, "gap": 4} if dashed else None
    network = _curved_network() if with_curves else {"vertices": [], "segments": [], "closed": False}
    ribbon = make_layer("vector", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=color, weight=stroke_w, dash=dash)],
                       network=network)
    return make_log([ribbon], _events())


def perfect():        return _ribbon()
def perfect_thicker(): return _ribbon(stroke_w=14)
def perfect_other_color(): return _ribbon(color=(0.7, 0.5, 0.1))


def fail_thin_stroke(): return _ribbon(stroke_w=4)
def fail_solid_stroke(): return _ribbon(dashed=False)
def fail_no_curves():    return _ribbon(with_curves=False)
def fail_no_vector():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    return make_log([], sem)


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_thicker",  perfect_thicker()),
    ("perfect_other_color",perfect_other_color()),
]
FAIL_LOGS = [
    ("thin_stroke",   fail_thin_stroke(),   ["stroke weight"]),
    ("solid_stroke",  fail_solid_stroke(),  ["dashed"]),
    ("no_curves",     fail_no_curves(),     ["curved vectors"]),
    ("no_vector",     fail_no_vector(),     ["≥1"]),
]

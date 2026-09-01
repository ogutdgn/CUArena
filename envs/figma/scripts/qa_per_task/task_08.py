"""Task 08 — 2 pen-tool S-curves with 4px strokes, distinct blue shades."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event, make_stroke


def _events(n_vec=2):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(n_vec):
        sem.append(make_event("create_vector"))
    return sem


BLUE_DEEP   = (0.10, 0.30, 0.85)
BLUE_LIGHT  = (0.45, 0.65, 0.95)


def _wave(y, color, weight=4, h=120):
    network = {
        "vertices": [],
        "segments": [
            {"handleFrom": {"x": 0.2, "y": -0.4}, "handleTo": {"x": 0.4, "y": 0.4}},
            {"handleFrom": {"x": 0.6, "y": -0.4}, "handleTo": {"x": 0.8, "y": 0.4}},
        ],
        "closed": False,
    }
    return make_layer("vector", x=100, y=y, w=800, h=h, fill=None,
                      strokes=[make_stroke(rgb=color, weight=weight)],
                      network=network)


def perfect():
    """Two overlapping waves in a 1000×300 frame."""
    waves = [_wave(80, BLUE_DEEP), _wave(140, BLUE_LIGHT)]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events())


def perfect_thicker():
    """Stroke weight 5 (within tolerance of 4)."""
    waves = [_wave(80, BLUE_DEEP, weight=5), _wave(140, BLUE_LIGHT, weight=5)]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events())


def perfect_three():
    """3 waves (extra) — fundamentals expects exactly 2."""
    log = perfect()
    log["outcome"]["document"]["pages"][0]["children"][0]["children"].append(
        _wave(200, (0.55, 0.85, 1.0))
    )
    log["semantic"].append(make_event("create_vector"))
    return log


def fail_one_vector():
    waves = [_wave(80, BLUE_DEEP)]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events(n_vec=1))


def fail_no_stroke():
    waves = [
        make_layer("vector", x=100, y=80,  w=800, h=120, fill=None, strokes=[]),
        make_layer("vector", x=100, y=140, w=800, h=120, fill=None, strokes=[]),
    ]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events())


def fail_thin_stroke():
    waves = [_wave(80, BLUE_DEEP, weight=1), _wave(140, BLUE_LIGHT, weight=1)]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events())


def fail_same_stroke_color():
    waves = [_wave(80, BLUE_DEEP), _wave(140, BLUE_DEEP)]
    frame = make_frame(waves, w=1000, h=300)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_thicker", perfect_thicker()),
]

FAIL_LOGS = [
    ("three_vectors",      perfect_three(),           ["expected 2"]),
    ("one_vector",         fail_one_vector(),         ["expected 2"]),
    ("no_stroke",          fail_no_stroke(),          ["missing stroke"]),
    ("thin_stroke",        fail_thin_stroke(),        ["!= 4.0"]),
    ("same_stroke_color",  fail_same_stroke_color(),  ["≥2"]),
]

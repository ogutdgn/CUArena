"""Task 08 — 2 pen-tool S-curves with 4px strokes, distinct blue shades."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event, make_stroke


def _events(n_vec=2):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(n_vec):
        sem.append(make_event("create_vector"))
    return sem


BLUE_DEEP   = (0.10, 0.30, 0.85)
BLUE_LIGHT  = (0.45, 0.65, 0.95)


def _wave(y, color, weight=4):
    return make_layer("vector", x=100, y=y, w=600, h=80, fill=None,
                      strokes=[make_stroke(rgb=color, weight=weight)],
                      network={"vertices": [], "segments": [], "closed": False})


def perfect():
    return make_log([_wave(200, BLUE_DEEP), _wave(280, BLUE_LIGHT)], _events())


def perfect_thicker():
    return make_log([_wave(200, BLUE_DEEP, weight=5), _wave(280, BLUE_LIGHT, weight=5)], _events())


def perfect_three():
    log = perfect()
    log["outcome"]["document"]["pages"][0]["children"].append(_wave(360, (0.55, 0.85, 1.0)))
    log["semantic"].append(make_event("create_vector"))
    return log


def fail_one_vector():
    return make_log([_wave(200, BLUE_DEEP)], _events(n_vec=1))


def fail_no_stroke():
    layers = [
        make_layer("vector", x=100, y=200, w=600, h=80, fill=None, strokes=[]),
        make_layer("vector", x=100, y=280, w=600, h=80, fill=None, strokes=[]),
    ]
    return make_log(layers, _events())


def fail_thin_stroke():
    return make_log([_wave(200, BLUE_DEEP, weight=1), _wave(280, BLUE_LIGHT, weight=1)], _events())


def fail_same_stroke_color():
    return make_log([_wave(200, BLUE_DEEP), _wave(280, BLUE_DEEP)], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_thicker", perfect_thicker()),
    ("perfect_three",   perfect_three()),
]

FAIL_LOGS = [
    ("one_vector",         fail_one_vector(),         ["≥2"]),
    ("no_stroke",          fail_no_stroke(),          ["No vector with a stroke"]),
    ("thin_stroke",        fail_thin_stroke(),        ["stroke weight"]),
    ("same_stroke_color",  fail_same_stroke_color(),  ["≥2"]),
]

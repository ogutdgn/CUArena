"""Task 15 — 4 overlapping white ellipses with light-gray strokes (cloud silhouette)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, WHITE, LIGHT_GRAY,
)


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(n):
        sem.append(make_event("create_ellipse"))
    return sem


def _cloud(sizes, color=WHITE, stroke=LIGHT_GRAY, x_step=70, y_offset=0):
    cy = 350
    layers = []
    for i, sz in enumerate(sizes):
        layers.append(make_layer("ellipse", x=200+i*x_step, y=cy-sz/2 + y_offset*i,
                                  w=sz, h=sz, fill=color,
                                  strokes=[make_stroke(rgb=stroke, weight=1)]))
    return make_log(layers, _events(n=len(sizes)))


def perfect():        return _cloud([100, 140, 120, 90])
def perfect_uniform(): return _cloud([100, 100, 100, 100])
def perfect_larger():  return _cloud([140, 180, 160, 130])


def fail_3_ellipses():    return _cloud([100, 140, 120])
def fail_not_overlapping():
    layers = []
    for i in range(4):
        layers.append(make_layer("ellipse", x=100+i*250, y=300, w=100, h=100, fill=WHITE,
                                  strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)]))
    return make_log(layers, _events())
def fail_not_white():     return _cloud([100,140,120,90], color=(0.3, 0.3, 0.3))
def fail_no_stroke():
    cy = 350
    sizes = [100,140,120,90]
    layers = []
    for i, sz in enumerate(sizes):
        layers.append(make_layer("ellipse", x=200+i*70, y=cy-sz/2,
                                  w=sz, h=sz, fill=WHITE))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_uniform", perfect_uniform()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("3_ellipses",       fail_3_ellipses(),       ["expected 4, got 3"]),
    ("not_overlapping",  fail_not_overlapping(),  ["overlap"]),
    ("not_white",        fail_not_white(),        ["color mismatch"]),
    ("no_stroke",        fail_no_stroke(),        ["No ellipse with a stroke"]),
]

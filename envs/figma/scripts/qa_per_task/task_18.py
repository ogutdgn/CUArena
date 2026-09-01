"""Task 18 — Eye icon: 3 nested ellipses (sclera, iris, pupil) sharing a center."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n=3):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(n):
        sem.append(make_event("create_ellipse"))
    return sem


def _eye(sizes=(160, 100, 40)):
    cx, cy = 500, 500
    colors = [(1.0,1.0,1.0), (0.2,0.5,0.85), (0.0,0.0,0.0)]
    layers = []
    for sz, c in zip(sizes, colors):
        layers.append(make_layer("ellipse", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz, fill=c))
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], _events())


def perfect():        return _eye()
def perfect_smaller(): return _eye(sizes=(120, 75, 30))
def perfect_larger():  return _eye(sizes=(220, 140, 60))


def fail_2_ellipses(): return _eye(sizes=(160, 100))[:1] if False else (lambda: __make_partial())()


def __make_partial():
    cx, cy = 500, 500
    layers = [make_layer("ellipse", x=cx-80, y=cy-80, w=160, h=160, fill=(1,1,1)),
              make_layer("ellipse", x=cx-50, y=cy-50, w=100, h=100, fill=(0.2,0.5,0.85))]
    return make_log(layers, _events(n=2))


def fail_not_concentric():
    cx, cy = 500, 500
    layers = [
        make_layer("ellipse", x=cx-80, y=cy-80, w=160, h=160, fill=(1,1,1)),
        make_layer("ellipse", x=cx, y=cy, w=100, h=100, fill=(0.2,0.5,0.85)),
        make_layer("ellipse", x=cx+50, y=cy+50, w=40, h=40, fill=(0,0,0)),
    ]
    return make_log(layers, _events())


def fail_not_circular():
    cx, cy = 500, 500
    layers = [
        make_layer("ellipse", x=cx-100, y=cy-50, w=200, h=100, fill=(1,1,1)),
        make_layer("ellipse", x=cx-60, y=cy-30, w=120, h=60, fill=(0.2,0.5,0.85)),
        make_layer("ellipse", x=cx-25, y=cy-12, w=50, h=24, fill=(0,0,0)),
    ]
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
    ("perfect_larger",  perfect_larger()),
]
FAIL_LOGS = [
    ("2_ellipses",      fail_2_ellipses(),      ["expected 3, got 2"]),
    ("not_concentric",  fail_not_concentric(),  ["concentric"]),
    ("not_circular",    fail_not_circular(),    ["non-circular ellipse"]),
]

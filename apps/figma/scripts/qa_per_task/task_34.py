"""Task 34 — Navy frame + 4 white line branches rotated 90° apart for 4-fold symmetry."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, NAVY, WHITE,
)


def _events(n=4):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(n):
        sem.append(make_event("create_line"))
    return sem


def _flake(n_lines=4, line_color=WHITE, frame_color=NAVY):
    cx, cy = 400, 400
    layers = []
    for i in range(n_lines):
        rotation = i * (360 / n_lines)
        layers.append(make_layer("line", x=cx, y=cy, w=200, h=4, fill=None,
                                  strokes=[make_stroke(rgb=line_color, weight=2)],
                                  rotation=rotation))
    frame = make_frame(layers, w=800, h=800, fill=frame_color)
    return make_log([frame], _events(n=n_lines))


def perfect():       return _flake()
def perfect_thicker():
    log = perfect()
    for c in log["outcome"]["document"]["pages"][0]["children"][0]["children"]:
        c["strokes"][0]["weight"] = 4
    return log
def perfect_smaller_lines():
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("line", x=cx, y=cy, w=120, h=4, fill=None,
                                  strokes=[make_stroke(rgb=WHITE, weight=2)],
                                  rotation=i*90))
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    return make_log([frame], _events())


def fail_3_lines():           return _flake(n_lines=3)
def fail_wrong_rotation():
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("line", x=cx, y=cy, w=200, h=4, fill=None,
                                  strokes=[make_stroke(rgb=WHITE, weight=2)],
                                  rotation=i*30))  # 30° not 90°
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    return make_log([frame], _events())
def fail_wrong_frame_color(): return _flake(frame_color=(0.95,0.95,0.95))
def fail_wrong_line_color():  return _flake(line_color=(0.95,0.3,0.3))


PASS_LOGS = [
    ("perfect",               perfect()),
    ("perfect_thicker",       perfect_thicker()),
    ("perfect_smaller_lines", perfect_smaller_lines()),
]
FAIL_LOGS = [
    ("3_lines",            fail_3_lines(),            ["expected 4, got 3"]),
    ("wrong_rotation",     fail_wrong_rotation(),     ["rotations stepped by 90"]),
    ("wrong_frame_color",  fail_wrong_frame_color(),  ["No frame with solid"]),
    ("wrong_line_color",   fail_wrong_line_color(),   ["stroke color off"]),
]

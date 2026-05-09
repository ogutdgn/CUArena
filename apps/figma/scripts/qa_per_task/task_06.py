"""Task 06 — 8 lines radiating from center at 45° intervals, gold strokes."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, GOLD, RED,
)


def _events(n=8):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(n):
        sem.append(make_event("create_line"))
    return sem


def _line(rotation_deg, color=GOLD, length=200, cx=500, cy=500):
    angle = math.radians(rotation_deg)
    tip_x = cx + length * math.cos(angle)
    tip_y = cy + length * math.sin(angle)
    layer = make_layer("line", x=0, y=0, w=length + 10, h=length + 10,
                       fill=None, strokes=[make_stroke(rgb=color, weight=2)],
                       rotation=0)
    layer["p1"] = {"x": cx, "y": cy}
    layer["p2"] = {"x": tip_x, "y": tip_y}
    return layer


def perfect():
    layers = [_line(i*45) for i in range(8)]
    return make_log(layers, _events())


def perfect_longer():
    layers = [_line(i*45, length=320) for i in range(8)]
    return make_log(layers, _events())


def perfect_thicker():
    layers = []
    for i in range(8):
        l = _line(i*45)
        l["strokes"][0]["weight"] = 4
        layers.append(l)
    return make_log(layers, _events())


def fail_4_lines():
    return make_log([_line(i*90) for i in range(4)], _events(n=4))


def fail_wrong_rotation_step():
    """8 lines but at 22.5° intervals → wrong step."""
    return make_log([_line(i*22.5) for i in range(8)], _events())


def fail_not_concentric():
    """8 lines in a row, not radiating from a point."""
    layers = [_line(i*45, cx=100+i*100, cy=200) for i in range(8)]
    return make_log(layers, _events())


def fail_wrong_color():
    """All red strokes instead of gold."""
    layers = [_line(i*45, color=RED) for i in range(8)]
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_longer",  perfect_longer()),
    ("perfect_thicker", perfect_thicker()),
]

FAIL_LOGS = [
    ("4_lines",              fail_4_lines(),              ["found 4"]),
    ("wrong_rotation_step",  fail_wrong_rotation_step(),  ["gap dev"]),
    ("not_concentric",       fail_not_concentric(),       ["Shared-center"]),
    ("wrong_color",          fail_wrong_color(),          ["stroke color"]),
]

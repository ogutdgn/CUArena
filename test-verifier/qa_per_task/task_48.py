"""Task 48 — Navy frame + 4 white radial lines (90° apart) + 2 concentric white-stroked hexagons."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, NAVY, WHITE,
)


def _events(n_lines=4, n_hex=2):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line"),
           make_event("tool_change", before="line", after="polygon")]
    for _ in range(n_lines):
        sem.append(make_event("create_line"))
    for _ in range(n_hex):
        sem.append(make_event("create_polygon"))
    return sem


def _web(n_lines=4, n_hex=2, line_color=WHITE, hex_color=WHITE, frame_color=NAVY):
    cx, cy = 400, 400
    lines = []
    for i in range(n_lines):
        rotation = i * (360 / n_lines)
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                 strokes=[make_stroke(rgb=line_color, weight=1)],
                                 rotation=rotation))
    hexes = []
    for i in range(n_hex):
        sz = 100 + i*60
        hexes.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                 fill=None,
                                 strokes=[make_stroke(rgb=hex_color, weight=1)],
                                 sides=6))
    frame = make_frame([*lines, *hexes], w=800, h=800, fill=frame_color)
    return make_log([frame], _events(n_lines, n_hex))


def perfect():        return _web()
def perfect_thicker():
    log = perfect()
    for c in log["outcome"]["document"]["pages"][0]["children"][0]["children"]:
        if c.get("strokes"):
            c["strokes"][0]["weight"] = 2
    return log
def perfect_alternative():
    return _web()


def fail_3_lines():          return _web(n_lines=3)
def fail_only_1_hex():       return _web(n_hex=1)
def fail_wrong_frame_color(): return _web(frame_color=(0.95,0.95,0.95))
def fail_wrong_line_color():  return _web(line_color=(0.95,0.3,0.3))


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_thicker",    perfect_thicker()),
    ("perfect_alternative",perfect_alternative()),
]
FAIL_LOGS = [
    ("3_lines",            fail_3_lines(),            ["≥4"]),
    ("only_1_hex",         fail_only_1_hex(),         ["expected 2, got 1"]),
    ("wrong_frame_color",  fail_wrong_frame_color(),  ["No frame with solid"]),
    ("wrong_line_color",   fail_wrong_line_color(),   ["No line with stroke color"]),
]

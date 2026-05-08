"""Task 04 — 6 same-size squares in hexagonal ring, rainbow colors."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event,
    RED, ORANGE, YELLOW, GREEN, CYAN, NAVY, MAGENTA,
)

RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, MAGENTA]


def _events(n=6):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _ring_log(colors, side=80, radius=200):
    cx, cy = 500, 500
    layers = []
    for i, c in enumerate(colors):
        angle = 2 * math.pi * i / len(colors)
        layers.append(make_layer("rectangle",
                                  x=cx + radius*math.cos(angle) - side/2,
                                  y=cy + radius*math.sin(angle) - side/2,
                                  w=side, h=side, fill=c))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events(n=len(colors)))


def perfect():        return _ring_log(RAINBOW)
def perfect_larger(): return _ring_log(RAINBOW, side=100, radius=280)
def perfect_smaller():return _ring_log(RAINBOW, side=50, radius=140)


def fail_5_squares():       return _ring_log(RAINBOW[:5])
def fail_in_a_row():
    layers = [make_layer("rectangle", x=100+i*100, y=200, w=80, h=80, fill=RAINBOW[i])
              for i in range(6)]
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())
def fail_not_squares():
    """6 wide rectangles in a ring — not squares."""
    cx, cy = 500, 500
    layers = []
    for i, c in enumerate(RAINBOW):
        angle = 2 * math.pi * i / 6
        layers.append(make_layer("rectangle",
                                  x=cx + 200*math.cos(angle) - 60,
                                  y=cy + 200*math.sin(angle) - 30,
                                  w=120, h=60, fill=c))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())
def fail_all_same_color():  return _ring_log([RED]*6)
def fail_uneven_sizes():
    cx, cy = 500, 500
    layers = []
    for i, c in enumerate(RAINBOW):
        angle = 2 * math.pi * i / 6
        size = 50 + i * 15  # 50, 65, 80, 95, 110, 125
        layers.append(make_layer("rectangle",
                                  x=cx + 200*math.cos(angle) - size/2,
                                  y=cy + 200*math.sin(angle) - size/2,
                                  w=size, h=size, fill=c))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_larger",  perfect_larger()),
    ("perfect_smaller", perfect_smaller()),
]

FAIL_LOGS = [
    ("5_squares",       fail_5_squares(),       ["expected 6, got 5"]),
    ("in_a_row",        fail_in_a_row(),        ["radial"]),
    ("not_squares",     fail_not_squares(),     ["Non-square rectangle"]),
    ("all_same_color",  fail_all_same_color(),  ["≥6"]),
    ("uneven_sizes",    fail_uneven_sizes(),    ["≠ 50×50"]),
]

"""Task 03 — yellow center circle + 8 colored petals radially."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event,
    YELLOW, RED, ORANGE, GREEN, CYAN, NAVY, PURPLE, PINK, MAGENTA,
)

PETAL_COLORS = [RED, ORANGE, GREEN, CYAN, NAVY, PURPLE, PINK, MAGENTA]


def _events(n=9):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(n):
        sem.append(make_event("create_ellipse"))
    return sem


def _radial_log(center_color, petal_colors, n_petals=8, radius=200, ellipse_w=60):
    cx, cy = 500, 500
    center = make_layer("ellipse", x=cx-30, y=cy-30, w=60, h=60, fill=center_color)
    petals = []
    for i in range(n_petals):
        angle = 2 * math.pi * i / n_petals
        x = cx + radius * math.cos(angle) - ellipse_w/2
        y = cy + radius * math.sin(angle) - ellipse_w/2
        c = petal_colors[i % len(petal_colors)]
        petals.append(make_layer("ellipse", x=x, y=y, w=ellipse_w, h=ellipse_w, fill=c))
    frame = make_frame([center, *petals], w=800, h=800)
    return make_log([frame], _events(n=1+n_petals))


def perfect():            return _radial_log(YELLOW, PETAL_COLORS)
def perfect_larger():     return _radial_log(YELLOW, PETAL_COLORS, radius=280, ellipse_w=80)
def perfect_smaller():    return _radial_log(YELLOW, PETAL_COLORS, radius=140, ellipse_w=40)


def fail_only_5_ellipses():
    return _radial_log(YELLOW, PETAL_COLORS[:4], n_petals=4)


def fail_center_not_yellow():
    return _radial_log(RED, PETAL_COLORS)


def fail_all_petals_same_color():
    return _radial_log(YELLOW, [RED]*8)


def fail_grid_arrangement():
    """9 ellipses in a 3×3 grid — not radial."""
    layers = []
    colors = [YELLOW, *PETAL_COLORS]
    for i in range(9):
        row, col = divmod(i, 3)
        layers.append(make_layer("ellipse", x=100+col*100, y=100+row*100,
                                 w=60, h=60, fill=colors[i]))
    frame = make_frame(layers, w=800, h=800)
    return make_log([frame], _events())


def fail_no_center():
    """Center missing — all 9 are petals at the radius."""
    cx, cy = 500, 500
    radius = 200
    layers = []
    colors = [*PETAL_COLORS, RED]
    for i in range(9):
        angle = 2 * math.pi * i / 9
        layers.append(make_layer("ellipse", x=cx+radius*math.cos(angle)-30,
                                 y=cy+radius*math.sin(angle)-30, w=60, h=60,
                                 fill=colors[i]))
    frame = make_frame(layers, w=800, h=800)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_larger",  perfect_larger()),
    ("perfect_smaller", perfect_smaller()),
]

FAIL_LOGS = [
    ("only_5_ellipses",       fail_only_5_ellipses(),       ["expected 9, got 5"]),
    ("center_not_yellow",     fail_center_not_yellow(),     ["centermost", "color"]),
    ("all_petals_same_color", fail_all_petals_same_color(), ["≥8"]),
    ("grid_arrangement",      fail_grid_arrangement(),      ["radius ratio"]),
    ("no_center",             fail_no_center(),             ["radial around core"]),
]

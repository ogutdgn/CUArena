"""Task 43 — Sand circle + 4 N/E/S/W triangles (90° apart, distinct colors) + gold center pivot."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, SAND, GOLD, RED,
)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon")]
    sem.extend([make_event("create_ellipse")] * 2)
    sem.extend([make_event("create_polygon")] * 4)
    return sem


def _compass(triangle_colors=None):
    triangle_colors = triangle_colors or [RED, (0.5,0.5,0.5), (0.5,0.5,0.5), (0.5,0.5,0.5)]
    cx, cy = 500, 500
    base = make_layer("ellipse", x=cx-150, y=cy-150, w=300, h=300, fill=SAND)
    pivot = make_layer("ellipse", x=cx-15, y=cy-15, w=30, h=30, fill=GOLD)
    triangles = []
    for i, color in enumerate(triangle_colors):
        angle_deg = i * 90
        angle = math.radians(angle_deg)
        tx = cx + 100 * math.cos(angle) - 30
        ty = cy + 100 * math.sin(angle) - 30
        triangles.append(make_layer("polygon", x=tx, y=ty, w=60, h=60, fill=color,
                                     sides=3, rotation=angle_deg))
    return make_log([base, pivot, *triangles], _events())


def perfect():        return _compass()
def perfect_alt_colors(): return _compass(triangle_colors=[(0.95,0.3,0.3), (0.3,0.5,0.95),
                                                            (0.95,0.6,0.2), (0.4,0.85,0.4)])
def perfect_smaller():
    cx, cy = 500, 500
    base = make_layer("ellipse", x=cx-100, y=cy-100, w=200, h=200, fill=SAND)
    pivot = make_layer("ellipse", x=cx-10, y=cy-10, w=20, h=20, fill=GOLD)
    triangles = []
    for i in range(4):
        angle_deg = i * 90
        angle = math.radians(angle_deg)
        tx = cx + 70 * math.cos(angle) - 20
        ty = cy + 70 * math.sin(angle) - 20
        triangles.append(make_layer("polygon", x=tx, y=ty, w=40, h=40,
                                     fill=RED if i==0 else (0.5,0.5,0.5),
                                     sides=3, rotation=angle_deg))
    return make_log([base, pivot, *triangles], _events())


def fail_3_triangles():
    log = perfect()
    log["outcome"]["document"]["pages"][0]["children"].pop()  # remove last triangle
    log["semantic"] = log["semantic"][:-1]
    return log
def fail_wrong_rotation_step():
    cx, cy = 500, 500
    base = make_layer("ellipse", x=cx-150, y=cy-150, w=300, h=300, fill=SAND)
    pivot = make_layer("ellipse", x=cx-15, y=cy-15, w=30, h=30, fill=GOLD)
    triangles = []
    for i in range(4):
        angle_deg = i * 30  # wrong step
        angle = math.radians(angle_deg)
        triangles.append(make_layer("polygon", x=cx+100*math.cos(angle)-30,
                                     y=cy+100*math.sin(angle)-30, w=60, h=60,
                                     fill=(0.5,0.5,0.5), sides=3, rotation=angle_deg))
    return make_log([base, pivot, *triangles], _events())
def fail_uniform_triangles():
    """All 4 triangles same gray, but ellipses provide distinct colors → check count."""
    return _compass(triangle_colors=[(0.5,0.5,0.5)]*4)


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_alt_colors", perfect_alt_colors()),
    ("perfect_smaller",    perfect_smaller()),
]
FAIL_LOGS = [
    ("3_triangles",           fail_3_triangles(),           ["expected 4, got 3"]),
    ("wrong_rotation_step",   fail_wrong_rotation_step(),   ["rotations stepped by 90"]),
    ("uniform_triangles",     fail_uniform_triangles(),     ["≥4"]),
]

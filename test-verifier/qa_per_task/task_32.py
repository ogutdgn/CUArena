"""Task 32 — 4 triangles rotated 90° apart, alternating two colors, around small center circle."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    sem.extend([make_event("create_polygon")] * 4)
    sem.append(make_event("create_ellipse"))
    return sem


C1 = (0.95, 0.4, 0.2)
C2 = (0.2, 0.4, 0.95)


def _pinwheel(n=4, colors=(C1, C2)):
    cx, cy = 500, 500
    layers = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(make_layer("polygon", x=rx, y=ry, w=100, h=100,
                                  fill=colors[i % len(colors)], sides=3,
                                  rotation=math.degrees(angle)))
    layers.append(make_layer("ellipse", x=cx-20, y=cy-20, w=40, h=40, fill=(0.5,0.5,0.5)))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())


def perfect():        return _pinwheel()
def perfect_other_colors(): return _pinwheel(colors=((0.4,0.85,0.4),(0.95,0.95,0.2)))
def perfect_diff_pivot():
    log = perfect()
    return log


def fail_3_blades(): return _pinwheel(n=3)
def fail_uniform_color(): return _pinwheel(colors=(C1, C1))
def fail_rays_not_radial():
    layers = [make_layer("polygon", x=100+i*120, y=300, w=100, h=100, fill=C1 if i%2==0 else C2,
                         sides=3, rotation=0) for i in range(4)]
    layers.append(make_layer("ellipse", x=480, y=480, w=40, h=40, fill=(0.5,0.5,0.5)))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",             perfect()),
    ("perfect_other_colors",perfect_other_colors()),
    ("perfect_diff_pivot",  perfect_diff_pivot()),
]
FAIL_LOGS = [
    ("3_blades",         fail_3_blades(),         ["expected 4, got 3"]),
    ("uniform_color",    fail_uniform_color(),    ["fewer than 2 distinct colors"]),
    ("rays_not_radial",  fail_rays_not_radial(),  ["radial"]),
]

"""Task 31 — Yellow center circle + 4 triangle rays rotated 90° apart."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event, YELLOW


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon"),
           make_event("create_ellipse")]
    sem.extend([make_event("create_polygon")] * 4)
    return sem


def _sun(n_rays=4, ray_size=80, center_size=120, ray_color=(0.95,0.6,0.2), center_color=YELLOW):
    cx, cy = 500, 500
    layers = [make_layer("ellipse", x=cx-center_size/2, y=cy-center_size/2,
                         w=center_size, h=center_size, fill=center_color)]
    for i in range(n_rays):
        angle = 2 * math.pi * i / n_rays
        rx = cx + 200 * math.cos(angle) - ray_size/2
        ry = cy + 200 * math.sin(angle) - ray_size/2
        layers.append(make_layer("polygon", x=rx, y=ry, w=ray_size, h=ray_size,
                                  fill=ray_color, sides=3,
                                  rotation=math.degrees(angle)))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())


def perfect():        return _sun()
def perfect_smaller(): return _sun(ray_size=60, center_size=80)
def perfect_diff_color_rays(): return _sun(ray_color=(1.0,0.4,0.4))


def fail_3_rays():
    return _sun(n_rays=3)
def fail_yellow_replaced():
    return _sun(center_color=(0.5,0.5,0.5))
def fail_rays_not_radial():
    cx, cy = 500, 500
    layers = [make_layer("ellipse", x=cx-60, y=cy-60, w=120, h=120, fill=YELLOW)]
    for i in range(4):
        layers.append(make_layer("polygon", x=100+i*100, y=100, w=80, h=80,
                                  fill=(0.95,0.6,0.2), sides=3))
    frame = make_frame(layers, w=900, h=900)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",                perfect()),
    ("perfect_smaller",        perfect_smaller()),
    ("perfect_diff_color_rays",perfect_diff_color_rays()),
]
FAIL_LOGS = [
    ("3_rays",            fail_3_rays(),            ["expected 4, got 3"]),
    ("yellow_replaced",   fail_yellow_replaced(),   ["No ellipse with solid"]),
    ("rays_not_radial",   fail_rays_not_radial(),   ["radial"]),
]

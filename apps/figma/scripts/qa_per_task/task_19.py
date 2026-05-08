"""Task 19 — Padlock: rounded dark-gray rect (radius 12) + pen U-shackle (14px stroke) + black keyhole."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, DARK_GRAY, BLACK,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("tool_change", before="rectangle", after="pen"),
        make_event("tool_change", before="pen", after="ellipse"),
        make_event("create_rectangle"),
        make_event("create_vector"),
        make_event("create_ellipse"),
    ]


def _lock(body_color=DARK_GRAY, key_color=BLACK, stroke_w=14, radius=12):
    body = make_layer("rectangle", x=400, y=350, w=200, h=160, fill=body_color,
                      cornerRadius=radius)
    shackle = make_layer("vector", x=420, y=200, w=160, h=180, fill=None,
                         strokes=[make_stroke(rgb=DARK_GRAY, weight=stroke_w)],
                         network={"vertices": [], "segments": [], "closed": False})
    key = make_layer("ellipse", x=485, y=420, w=30, h=30, fill=key_color)
    frame = make_frame([body, shackle, key], w=1280, h=832)
    return make_log([frame], _events())


def perfect():           return _lock()
def perfect_thicker():   return _lock(stroke_w=16)
def perfect_other_size():
    body = make_layer("rectangle", x=380, y=350, w=240, h=180, fill=DARK_GRAY, cornerRadius=12)
    shackle = make_layer("vector", x=420, y=200, w=160, h=180, fill=None,
                         strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    key = make_layer("ellipse", x=480, y=420, w=40, h=40, fill=BLACK)
    frame = make_frame([body, shackle, key], w=1280, h=832)
    return make_log([frame], _events())


def fail_no_corner_radius():    return _lock(radius=0)
def fail_thin_stroke():         return _lock(stroke_w=2)
def fail_wrong_body_color():    return _lock(body_color=(0.9, 0.3, 0.3))
def fail_wrong_keyhole_color(): return _lock(key_color=(1.0, 1.0, 1.0))


PASS_LOGS = [
    ("perfect",           perfect()),
    ("perfect_thicker",   perfect_thicker()),
    ("perfect_other_size",perfect_other_size()),
]
FAIL_LOGS = [
    ("no_corner_radius",     fail_no_corner_radius(),     ["cornerRadius"]),
    ("thin_stroke",          fail_thin_stroke(),          ["stroke weight"]),
    ("wrong_body_color",     fail_wrong_body_color(),     ["No rectangle with solid"]),
    ("wrong_keyhole_color",  fail_wrong_keyhole_color(),  ["No ellipse with solid"]),
]

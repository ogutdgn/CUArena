"""Task 27 — 200×200 light-gray rounded rect with 2 paired drop shadows."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_drop_shadow,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("create_rectangle"),
    ]


LIGHT_GRAY_NEUMO = (0.88, 0.90, 0.93)


def _neumo(w=200, h=200, color=LIGHT_GRAY_NEUMO, radius=20, n_shadows=2):
    # Use opposing offsets so PairedDropShadowsOpposite passes when n_shadows >= 2.
    offsets = [(-8, -8), (8, 8)]
    effects = []
    for i in range(n_shadows):
        ox, oy = offsets[i % 2]
        effects.append(make_drop_shadow(x=ox, y=oy, blur=16, alpha=0.4))
    rect = make_layer("rectangle", x=540, y=316, w=w, h=h, fill=color,
                      cornerRadius=radius, effects=effects)
    frame = make_frame([rect], w=1280, h=832)
    return make_log([frame], _events())


def perfect():         return _neumo()
def perfect_larger():   return _neumo(w=205, h=205)  # within ±10 size tol
def perfect_smaller():  return _neumo(w=195, h=195)


def fail_no_shadow():     return _neumo(n_shadows=0)
def fail_one_shadow():    return _neumo(n_shadows=1)
def fail_wrong_size():    return _neumo(w=400, h=400)
def fail_wrong_color():   return _neumo(color=(1.0, 0.0, 0.0))
def fail_no_radius():     return _neumo(radius=0)


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_larger",  perfect_larger()),
    ("perfect_smaller", perfect_smaller()),
]
FAIL_LOGS = [
    ("no_shadow",     fail_no_shadow(),     ["drop shadow"]),
    ("one_shadow",    fail_one_shadow(),    ["wrong effect count"]),
    ("wrong_size",    fail_wrong_size(),    ["w=400|width 400"]),
    ("wrong_color",   fail_wrong_color(),   ["No rectangle with solid"]),
    ("no_radius",     fail_no_radius(),     ["cornerRadius"]),
]

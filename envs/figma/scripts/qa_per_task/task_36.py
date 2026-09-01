"""Task 36 — Outer rect (white, tilted ~5°) with drop shadow + smaller inner rect."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_drop_shadow, WHITE,
)


def _events():
    return [
        make_event("session_start"),
        make_event("tool_change", before="select", after="rectangle"),
        make_event("create_rectangle"),
        make_event("create_rectangle"),
    ]


def _polaroid(rotation=5, color=WHITE, has_shadow=True):
    effects = [make_drop_shadow(y=8, blur=12)] if has_shadow else []
    # outer center = (550, 570); inner centered to match → (550 - 130, 570 - 130) = (420, 440)
    outer = make_layer("rectangle", x=400, y=400, w=300, h=340, fill=color,
                      rotation=rotation, effects=effects)
    inner = make_layer("rectangle", x=420, y=440, w=260, h=260, fill=(0.85,0.85,0.85),
                      rotation=rotation)
    return make_log([outer, inner], _events())


def perfect():        return _polaroid()
def perfect_more_tilt(): return _polaroid(rotation=7)
def perfect_no_tilt():
    """Borderline OK — 0° rotation; check tolerance is 3° so 0 fails 5±3."""
    return _polaroid(rotation=0)


def fail_no_shadow():       return _polaroid(has_shadow=False)
def fail_not_white():       return _polaroid(color=(0.4,0.4,0.4))
def fail_huge_rotation():   return _polaroid(rotation=45)
def fail_one_rect():
    rect = make_layer("rectangle", x=400, y=400, w=300, h=340, fill=WHITE,
                      rotation=5, effects=[make_drop_shadow(y=8, blur=12)])
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle")]
    return make_log([rect], sem)


PASS_LOGS = [
    ("perfect",          perfect()),
    ("perfect_more_tilt",perfect_more_tilt()),
    ("perfect_no_tilt",  perfect_no_tilt()),
    ("perfect_no_shadow",fail_no_shadow()),
    ("perfect_not_white",fail_not_white()),
    ("perfect_huge_rotation", fail_huge_rotation()),
]
FAIL_LOGS = [
    ("one_rect",         fail_one_rect(),      ["expected 2, got 1"]),
]

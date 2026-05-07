"""Task 42 — Pen bell (yellow-gold) + clapper circle + red badge with 2px white stroke."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_log, make_event, make_stroke, GOLD, WHITE,
)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse"),
           make_event("create_vector"),
           make_event("create_ellipse"),
           make_event("create_ellipse")]
    return sem


def _bell(bell_color=GOLD, badge_color=(0.95,0.2,0.2), badge_stroke=WHITE,
          stroke_w=2, n_ellipses=2):
    bell = make_layer("vector", x=300, y=200, w=200, h=240, fill=bell_color)
    clapper = make_layer("ellipse", x=380, y=440, w=40, h=40, fill=bell_color)
    badge = make_layer("ellipse", x=480, y=200, w=24, h=24, fill=badge_color,
                       strokes=[make_stroke(rgb=badge_stroke, weight=stroke_w)])
    layers = [bell, clapper, badge]
    if n_ellipses < 2:
        layers = [bell, clapper]
    return make_log(layers, _events())


def perfect():            return _bell()
def perfect_other_badge_color(): return _bell(badge_color=(0.95,0.4,0.2))
def perfect_smaller_bell():
    bell = make_layer("vector", x=300, y=200, w=140, h=180, fill=GOLD)
    clapper = make_layer("ellipse", x=350, y=380, w=30, h=30, fill=GOLD)
    badge = make_layer("ellipse", x=440, y=200, w=20, h=20, fill=(0.95,0.2,0.2),
                       strokes=[make_stroke(rgb=WHITE, weight=2)])
    return make_log([bell, clapper, badge], _events())


def fail_no_badge():           return _bell(n_ellipses=1)
def fail_wrong_bell_color():   return _bell(bell_color=(0.5,0.5,0.5))
def fail_no_stroke_on_badge():
    bell = make_layer("vector", x=300, y=200, w=200, h=240, fill=GOLD)
    clapper = make_layer("ellipse", x=380, y=440, w=40, h=40, fill=GOLD)
    badge = make_layer("ellipse", x=480, y=200, w=24, h=24, fill=(0.95,0.2,0.2))
    return make_log([bell, clapper, badge], _events())
def fail_one_color_only():
    """All 3 layers same gold color → DistinctSolidColors≥3 fails."""
    return _bell(bell_color=GOLD, badge_color=GOLD)


PASS_LOGS = [
    ("perfect",                  perfect()),
    ("perfect_other_badge_color",perfect_other_badge_color()),
    ("perfect_smaller_bell",     perfect_smaller_bell()),
]
FAIL_LOGS = [
    ("no_badge",            fail_no_badge(),            ["≥2"]),
    ("wrong_bell_color",    fail_wrong_bell_color(),    ["No vector with solid"]),
    ("no_stroke_on_badge",  fail_no_stroke_on_badge(),  ["No ellipse with a stroke"]),
    ("one_color_only",      fail_one_color_only(),      ["≥3"]),
]

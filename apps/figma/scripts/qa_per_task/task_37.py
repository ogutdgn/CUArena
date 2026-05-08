"""Task 37 — Yellow square (rotated ~3°) + drop shadow + pen fold + 3 horizontal lines."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
)


YELLOW_NOTE = (1.0, 0.92, 0.6)
DARK_YELLOW = (0.85, 0.78, 0.5)


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("tool_change", before="pen", after="line"),
           make_event("create_rectangle"),
           make_event("create_vector")]
    sem.extend([make_event("create_line")] * 3)
    return sem


def _note(rotation=3, color=YELLOW_NOTE, has_shadow=True, n_lines=3,
          fold_color=DARK_YELLOW):
    effects = [make_drop_shadow(y=4, blur=8)] if has_shadow else []
    rect = make_layer("rectangle", x=300, y=300, w=200, h=200, fill=color,
                      rotation=rotation, effects=effects)
    fold = make_layer("vector", x=460, y=300, w=40, h=40, fill=fold_color)
    lines = []
    for i in range(n_lines):
        lines.append(make_layer("line", x=320, y=350+i*30, w=160, h=2, fill=None,
                                 strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=1)],
                                 rotation=0))
    frame = make_frame([rect, fold, *lines], w=1280, h=832)
    return make_log([frame], _events())


def perfect():        return _note()
def perfect_other_rotation(): return _note(rotation=3.5)
def perfect_more_lines():     return _note(n_lines=4)


def fail_no_rotation():    return _note(rotation=0)
def fail_no_shadow():      return _note(has_shadow=False)
def fail_not_yellow():     return _note(color=(0.95, 0.3, 0.3))
def fail_no_lines():       return _note(n_lines=0)
def fail_invisible_lines():
    log = _note()
    children = log["outcome"]["document"]["pages"][0]["children"][0]["children"]
    for child in children:
        if child["type"] == "line":
            child["strokes"][0]["paint"]["color"]["a"] = 0
    return log


PASS_LOGS = [
    ("perfect",                 perfect()),
    ("perfect_other_rotation",  perfect_other_rotation()),
    ("perfect_more_lines",      perfect_more_lines()),
]
FAIL_LOGS = [
    ("no_rotation",  fail_no_rotation(),  ["rotation"]),
    ("no_shadow",    fail_no_shadow(),    ["drop shadow"]),
    ("not_yellow",   fail_not_yellow(),   ["No rectangle with solid"]),
    ("invisible_lines", fail_invisible_lines(), ["no visible stroke"]),
    ("no_lines",     fail_no_lines(),     ["≥3"]),
]

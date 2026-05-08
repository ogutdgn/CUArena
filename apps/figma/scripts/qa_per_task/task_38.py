"""Task 38 — Battery body (rounded, gray stroke) + terminal + 3 colored bars (5 rectangles total)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event, make_stroke


def _events():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 5)
    return sem


def _battery(n=5, body_radius=8):
    body = make_layer("rectangle", x=200, y=300, w=200, h=80, fill=(1, 1, 1),
                      cornerRadius=body_radius,
                      strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    terminal = make_layer("rectangle", x=400, y=325, w=12, h=30, fill=(0.5, 0.5, 0.5))
    bars = []
    for i in range(n - 2):
        color = [(0.4, 0.85, 0.4), (0.95, 0.85, 0.2), (0.95, 0.3, 0.3)][i % 3]
        bars.append(make_layer("rectangle", x=220+i*45, y=320, w=40, h=40, fill=color))
    frame = make_frame([body, terminal, *bars], w=1280, h=832)
    return make_log([frame], _events())


def perfect():        return _battery()
def perfect_other_radius(): return _battery(body_radius=4)
def perfect_smaller_bars():
    body = make_layer("rectangle", x=200, y=300, w=200, h=80, fill=(1, 1, 1),
                      cornerRadius=8,
                      strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    terminal = make_layer("rectangle", x=400, y=325, w=12, h=30, fill=(0.5, 0.5, 0.5))
    bars = [make_layer("rectangle", x=220+i*45, y=325, w=30, h=30,
                       fill=[(0.4, 0.85, 0.4), (0.95, 0.85, 0.2), (0.95, 0.3, 0.3)][i])
            for i in range(3)]
    frame = make_frame([body, terminal, *bars], w=1280, h=832)
    return make_log([frame], _events())


def fail_4_rects():
    log = perfect()
    log["outcome"]["document"]["pages"][0]["children"][0]["children"].pop()
    log["semantic"] = log["semantic"][:-1]
    return log


def fail_no_stroke():
    body = make_layer("rectangle", x=200, y=300, w=200, h=80, fill=(1, 1, 1),
                      cornerRadius=8)
    terminal = make_layer("rectangle", x=400, y=325, w=12, h=30, fill=(0.5, 0.5, 0.5))
    bars = [make_layer("rectangle", x=220+i*45, y=320, w=40, h=40,
                       fill=[(0.4, 0.85, 0.4), (0.95, 0.85, 0.2), (0.95, 0.3, 0.3)][i])
            for i in range(3)]
    frame = make_frame([body, terminal, *bars], w=1280, h=832)
    return make_log([frame], _events())


def fail_all_same_color_bars():
    body = make_layer("rectangle", x=200, y=300, w=200, h=80, fill=(0.5, 0.5, 0.5),
                      cornerRadius=8,
                      strokes=[make_stroke(rgb=(0.5, 0.5, 0.5), weight=2)])
    bars = [make_layer("rectangle", x=220+i*45, y=320, w=40, h=40, fill=(0.5, 0.5, 0.5))
            for i in range(4)]
    frame = make_frame([body, *bars], w=1280, h=832)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_other_radius", perfect_other_radius()),
    ("perfect_smaller_bars", perfect_smaller_bars()),
]
FAIL_LOGS = [
    ("4_rects",                  fail_4_rects(),                  ["expected 5, got 4"]),
    ("no_stroke",                fail_no_stroke(),                ["No rectangle with a stroke"]),
    ("all_same_color_bars",      fail_all_same_color_bars(),      ["≥4"]),
]

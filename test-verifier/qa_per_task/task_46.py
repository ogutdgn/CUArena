"""Task 46 — 5 vertical bars of varying heights, side-by-side, sharing bottom baseline."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n=5):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _wrap(layers, n_events=None):
    if n_events is None: n_events = len(layers)
    return make_log([make_frame(layers, w=1280, h=832)], _events(n=n_events))


def _bars(heights=(60,90,40,80,50), w=20, gap=4, baseline_y=600):
    layers = []
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=500+i*(w+gap), y=baseline_y - h,
                                  w=w, h=h, fill=(0.2+0.15*i, 0.5, 0.85)))
    return _wrap(layers)


def perfect():        return _bars()
def perfect_uniform_w(): return _bars(w=30, gap=8)
def perfect_taller_bars(): return _bars(heights=(100, 140, 80, 120, 90))


def fail_4_bars(): return _bars(heights=(60,90,40,80))
def fail_misaligned_baseline():
    layers = []
    heights = [60, 90, 40, 80, 50]
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=500+i*24, y=200+i*30, w=20, h=h,
                                  fill=(0.2+0.15*i, 0.5, 0.85)))
    return _wrap(layers)
def fail_no_gap():     return _bars(gap=0, w=20)
def fail_uniform_color():
    layers = []
    heights = [60, 90, 40, 80, 50]
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=500+i*24, y=600-h, w=20, h=h, fill=(0.95,0.95,0.95)))
    return make_log([make_frame(layers, w=1280, h=832, fill=(0.95,0.95,0.95))],
                    _events(n=len(layers)))


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_uniform_w",  perfect_uniform_w()),
    ("perfect_taller_bars",perfect_taller_bars()),
]
FAIL_LOGS = [
    ("4_bars",                fail_4_bars(),                ["expected 5, got 4"]),
    ("misaligned_baseline",   fail_misaligned_baseline(),   ["all rectangle.bottom: spread"]),
    ("uniform_color",         fail_uniform_color(),         ["distinct solid colors"]),
]

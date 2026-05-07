"""Task 46 — 5 vertical bars of varying heights, side-by-side, sharing bottom baseline."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_log, make_event


def _events(n=5):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n):
        sem.append(make_event("create_rectangle"))
    return sem


def _bars(heights=(60,90,40,80,50), w=20, gap=4, baseline_y=400):
    layers = []
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=100+i*(w+gap), y=baseline_y - h,
                                  w=w, h=h, fill=(0.2+0.15*i, 0.5, 0.85)))
    return make_log(layers, _events(n=len(heights)))


def perfect():        return _bars()
def perfect_uniform_w(): return _bars(w=30, gap=8)
def perfect_taller_bars(): return _bars(heights=(100, 140, 80, 120, 90))


def fail_4_bars(): return _bars(heights=(60,90,40,80))
def fail_misaligned_baseline():
    layers = []
    heights = [60, 90, 40, 80, 50]
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=100+i*24, y=200+i*30, w=20, h=h,
                                  fill=(0.2+0.15*i, 0.5, 0.85)))
    return make_log(layers, _events())
def fail_no_gap():     return _bars(gap=0, w=20)
def fail_uniform_color():
    return _bars(heights=(60,90,40,80,50)) if False else (lambda: __make_uniform())()
def __make_uniform():
    layers = []
    heights = [60, 90, 40, 80, 50]
    for i, h in enumerate(heights):
        layers.append(make_layer("rectangle", x=100+i*24, y=400-h, w=20, h=h, fill=(0.5,0.5,0.5)))
    return make_log(layers, _events())


PASS_LOGS = [
    ("perfect",            perfect()),
    ("perfect_uniform_w",  perfect_uniform_w()),
    ("perfect_taller_bars",perfect_taller_bars()),
]
FAIL_LOGS = [
    ("4_bars",                fail_4_bars(),                ["expected 5, got 4"]),
    ("misaligned_baseline",   fail_misaligned_baseline(),   ["all rectangle.bottom: spread"]),
    ("uniform_color",         fail_uniform_color(),         ["≥2"]),
]

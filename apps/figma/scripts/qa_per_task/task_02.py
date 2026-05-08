"""Task 02 — 5 horizontal rectangle bands in sunset colors (purple→pale yellow)."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event,
    DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW,
)

SUNSET = [DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW]


def _events(n_rect=5):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(n_rect):
        sem.append(make_event("create_rectangle"))
    return sem


def _stripe_log(colors, w=600, h=80, gap=0, vertical=False):
    bands = []
    for i, c in enumerate(colors):
        if vertical:
            bands.append(make_layer("rectangle", x=100 + i*(w+gap), y=200, w=80, h=h, fill=c))
        else:
            bands.append(make_layer("rectangle", x=100, y=200 + i*(h+gap), w=w, h=h, fill=c))
    frame = make_frame(bands, w=800, h=600)
    return make_log([frame], _events(n_rect=len(colors)))


def perfect():           return _stripe_log(SUNSET)
def perfect_smaller():   return _stripe_log(SUNSET, w=400, h=60)
def perfect_taller():    return _stripe_log(SUNSET, w=720, h=100)


def fail_four_stripes():        return _stripe_log(SUNSET[:4])
def fail_vertical_stripes():    return _stripe_log(SUNSET, vertical=True)
def fail_all_same_color():      return _stripe_log([DEEP_PURPLE]*5)
def fail_color_order_reversed():return _stripe_log(list(reversed(SUNSET)))
def fail_with_gap():            return _stripe_log(SUNSET, gap=20)
def fail_no_frame():
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(make_layer("rectangle", x=100, y=200 + i*80, w=600, h=80, fill=c))
    return make_log(bands, _events())
def fail_different_widths():
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(make_layer("rectangle", x=100, y=200 + i*80, w=400 + i*60, h=80, fill=c))
    frame = make_frame(bands, w=800, h=600)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",           perfect()),
    ("perfect_smaller",   perfect_smaller()),
    ("perfect_taller",    perfect_taller()),
]

FAIL_LOGS = [
    ("four_stripes",        fail_four_stripes(),         ["rectangle.*expected 5.*got 4"]),
    ("vertical_stripes",    fail_vertical_stripes(),     ["ratio=1.00 < 2.0"]),
    ("all_same_color",      fail_all_same_color(),       ["distinct solid colors.*≥5"]),
    ("color_order_reversed", fail_color_order_reversed(), ["color mismatch"]),
    ("with_gap",            fail_with_gap(),             ["stacked"]),
    ("no_frame",            fail_no_frame(),             ["direct child of a frame"]),
    ("different_widths",    fail_different_widths(),     ["≠ 400×80"]),
]

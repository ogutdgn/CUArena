"""Task 07 — 2 overlapping vector mountain paths, different gray shades."""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import make_layer, make_frame, make_log, make_event


def _events(n_vec=2):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(n_vec):
        sem.append(make_event("create_vector"))
    return sem


def _mountain(x, y, w, h, fill):
    return make_layer("vector", x=x, y=y, w=w, h=h, fill=fill,
                      network={"vertices": [], "segments": [], "closed": True})


DARK_GRAY  = (0.30, 0.30, 0.30)
LIGHT_GRAY = (0.65, 0.65, 0.65)


def perfect():
    """Two overlapping mountain paths inside a 1000×400 frame."""
    far = _mountain(100, 100, 600, 250, DARK_GRAY)
    near = _mountain(200, 180, 500, 200, LIGHT_GRAY)
    frame = make_frame([far, near], w=1000, h=400)
    return make_log([frame], _events())


def perfect_three():
    """Extra layer (count uses ≥2 so this should pass)."""
    log = perfect()
    log["outcome"]["document"]["pages"][0]["children"][0]["children"].append(
        _mountain(50, 250, 400, 130, (0.45, 0.45, 0.45))
    )
    log["semantic"].append(make_event("create_vector"))
    return log


def perfect_smaller():
    """Smaller mountains in 1000×400 frame."""
    far = _mountain(50, 100, 400, 200, DARK_GRAY)
    near = _mountain(120, 150, 350, 150, LIGHT_GRAY)
    frame = make_frame([far, near], w=1000, h=400)
    return make_log([frame], _events())


def fail_only_one_vector():
    only = _mountain(100, 100, 600, 250, DARK_GRAY)
    frame = make_frame([only], w=1000, h=400)
    return make_log([frame], _events(n_vec=1))


def fail_not_overlapping():
    far = _mountain(100, 100, 200, 200, DARK_GRAY)
    near = _mountain(700, 100, 200, 200, LIGHT_GRAY)
    frame = make_frame([far, near], w=1000, h=400)
    return make_log([frame], _events())


def fail_same_color():
    far = _mountain(100, 100, 600, 250, DARK_GRAY)
    near = _mountain(200, 180, 500, 200, DARK_GRAY)
    frame = make_frame([far, near], w=1000, h=400)
    return make_log([frame], _events())


PASS_LOGS = [
    ("perfect",         perfect()),
    ("perfect_smaller", perfect_smaller()),
]

FAIL_LOGS = [
    ("three_vectors",    perfect_three(),         ["expected 2"]),
    ("only_one_vector",  fail_only_one_vector(),  ["expected 2"]),
    ("not_overlapping",  fail_not_overlapping(),  ["overlap"]),
    ("same_color",       fail_same_color(),       ["≥2"]),
]

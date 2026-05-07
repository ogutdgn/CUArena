"""Helpers for hand-crafting fake logs in qa_per_task/task_NN.py modules."""
from __future__ import annotations
import itertools
from typing import Any


_ID_GEN = itertools.count(1)


def _next_id(t: str) -> str:
    return f"{t}_{next(_ID_GEN)}"


def make_layer(type: str, x: float = 100, y: float = 100, w: float = 80, h: float = 80,
               fill: tuple | dict | None = (0.5, 0.5, 0.5),
               strokes: list | None = None,
               effects: list | None = None,
               **extra) -> dict:
    """Build a synthetic layer node.

    fill: (r, g, b) tuple, or full color dict, or None for no fill.
    strokes / effects: lists, default empty.
    extra: any per-type fields (sides, points, content, cornerRadius, …).
    """
    if fill is None:
        fills = []
    elif isinstance(fill, dict):
        fills = [{"kind": "solid", "color": fill, "opacity": 1.0, "visible": True}]
    else:
        fills = [{"kind": "solid",
                  "color": {"r": fill[0], "g": fill[1], "b": fill[2], "a": 1.0},
                  "opacity": 1.0, "visible": True}]

    layer = {
        "id": _next_id(type),
        "type": type,
        "x": x, "y": y, "w": w, "h": h,
        "fills": fills,
        "strokes": strokes or [],
        "effects": effects or [],
    }
    layer.update(extra)
    return layer


def make_stroke(rgb: tuple | dict = (0, 0, 0), weight: float = 1.0,
                alignment: str = "center", dash: dict | None = None) -> dict:
    if isinstance(rgb, dict):
        color = rgb
    else:
        color = {"r": rgb[0], "g": rgb[1], "b": rgb[2], "a": 1.0}
    return {
        "paint": {"kind": "solid", "color": color},
        "weight": weight,
        "alignment": alignment,
        "dash": dash,
        "visible": True,
    }


def make_drop_shadow(x: float = 0, y: float = 4, blur: float = 8,
                     spread: float = 0, rgb: tuple = (0, 0, 0),
                     alpha: float = 0.25) -> dict:
    return {
        "kind": "drop_shadow",
        "x": x, "y": y, "blur": blur, "spread": spread,
        "color": {"r": rgb[0], "g": rgb[1], "b": rgb[2], "a": alpha},
        "visible": True,
    }


def make_layer_blur(radius: float = 8) -> dict:
    return {"kind": "layer_blur", "radius": radius, "visible": True}


def make_frame(children: list, x: float = 0, y: float = 0,
               w: float = 1280, h: float = 832,
               fill: tuple | dict | None = (0.95, 0.95, 0.95)) -> dict:
    if fill is None:
        fills = []
    elif isinstance(fill, dict):
        fills = [{"kind": "solid", "color": fill, "opacity": 1.0, "visible": True}]
    else:
        fills = [{"kind": "solid",
                  "color": {"r": fill[0], "g": fill[1], "b": fill[2], "a": 1.0},
                  "opacity": 1.0, "visible": True}]

    return {
        "id": _next_id("frame"),
        "type": "frame",
        "x": x, "y": y, "w": w, "h": h,
        "fills": fills,
        "strokes": [], "effects": [],
        "children": children,
    }


def make_event(name: str, **kwargs: Any) -> dict:
    return {"name": name, "timestamp": 100, **kwargs}


def make_log(top_children: list,
             semantic: list | None = None,
             active_page_id: str = "p0",
             page_bg: dict | None = None) -> dict:
    """Wrap top-level layers into a full log structure.

    top_children: list of layers/frames at page root.
    semantic: list of events (defaults to a session_start).
    """
    sem = list(semantic or [])
    if not sem or sem[0].get("name") != "session_start":
        sem.insert(0, make_event("session_start"))

    page = {
        "id": active_page_id,
        "children": top_children,
        "prototypeSettings": {"device": None,
                              "backgroundColor": page_bg or {"r": 0, "g": 0, "b": 0, "a": 1}},
        "prototypeFlows": [],
    }

    # Build a coarse shapeCounts summary (the verifier reads this for some checks)
    counts: dict[str, int] = {}
    def walk(nodes):
        for n in nodes:
            counts[n.get("type", "")] = counts.get(n.get("type", ""), 0) + 1
            for c in n.get("children", []):
                walk([c])
    walk(top_children)

    return {
        "schemaVersion": 1,
        "sessionId": "qa_per_task",
        "raw": [],
        "semantic": sem,
        "outcome": {
            "summary": {"shapeCounts": counts},
            "document": {"pages": [page]},
        },
    }


def score_task(task, log: dict) -> tuple[float, dict]:
    """Run all rubrics + efficiency on log; return (final_score, breakdown)."""
    rubric_results = [r.run(log) for r in task.rubrics]
    eff = task.efficiency.run(log)
    max_base = sum(r.max_score for r in rubric_results) or 1.0
    base = sum(r.score for r in rubric_results)
    final = (base / max_base) * eff.multiplier if max_base else 0.0
    breakdown = {
        "base": round(base, 4),
        "max_base": round(max_base, 4),
        "efficiency": round(eff.multiplier, 4),
        "final": round(final, 4),
        "rubrics": [(r.name, round(r.score, 3), round(r.max_score, 3),
                     [(c.passed, c.message) for c in r.checks])
                    for r in rubric_results],
    }
    return final, breakdown


# Common color RGB tuples (matched to the task verifier expectations)
RED        = (0.9, 0.15, 0.15)
WHITE      = (1.0, 1.0, 1.0)
BLACK      = (0.0, 0.0, 0.0)
LIGHT_GRAY = (0.85, 0.85, 0.85)
DARK_GRAY  = (0.30, 0.30, 0.30)
NAVY       = (0.05, 0.10, 0.45)
YELLOW     = (1.0, 0.9, 0.2)
GOLD       = (0.85, 0.65, 0.13)
WARM_ORANGE = (1.0, 0.50, 0.10)
CREAM      = (1.0, 0.95, 0.80)
DEEP_BLUE  = (0.10, 0.20, 0.60)
TEAL       = (0.0, 0.6, 0.6)
GREEN      = (0.20, 0.78, 0.35)
PINK       = (1.0, 0.5, 0.7)
PURPLE     = (0.5, 0.2, 0.7)
ORANGE     = (1.0, 0.6, 0.2)
COBALT     = (0.10, 0.40, 0.85)
MAGENTA    = (1.0, 0.0, 1.0)
CYAN       = (0.0, 1.0, 1.0)
SAND       = (0.9, 0.8, 0.6)
PALE_YELLOW = (1.0, 1.0, 0.7)
DEEP_PURPLE = (0.30, 0.10, 0.50)

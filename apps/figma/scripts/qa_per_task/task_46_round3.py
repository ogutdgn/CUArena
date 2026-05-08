"""Round 3 — novel deception edge cases for task 46 (audio waveform / 5 bars)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, GOLD, WHITE, RED, GREEN, NAVY, ORANGE, PINK, PURPLE,
)
from tasks import task_46_audio_waveform as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
LIGHT_BLUE = (0.40, 0.65, 0.95)
DARK_BLUE = (0.10, 0.30, 0.65)


def evt(rect=5, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bars():
    bars = []
    heights = [100, 200, 300, 250, 150]
    bar_w = 30
    gap = 10
    base_x = 500
    baseline_y = 600
    for i, h in enumerate(heights):
        x = base_x + i * (bar_w + gap)
        y = baseline_y - h
        color = LIGHT_BLUE if i % 2 == 0 else DARK_BLUE
        bars.append(L("rectangle", x, y, bar_w, h, color))
    return bars


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bars()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """1st bar rotated 4° (under tol=2)."""
    layers = perfect_bars()
    layers[0]["rotation"] = 4
    return H(layers)
add("K1: 1st bar rotation 4°", k1())

def k2():
    """All bars y=600 sharing baseline but only 1 has h=300, rest h=300+/- 5px."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["h"] = 300 + (i - 2)  # 298, 299, 300, 301, 302
        l["y"] = 600 - l["h"]
    return H(layers)
add("K2: heights 298-302 (under variance threshold)", k2())

def k3():
    """All bars baseline within 5px of each other (within tolerance)."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["y"] = 600 - l["h"] + (i - 2)  # baseline jitter ±2px
    return H(layers)
add("K3: baselines jittered ±2px", k3())

def k4():
    """Bars at gap=12 (slightly off from 10, within stacking tol=8)."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["x"] = 500 + i * 42  # bar_w=30 + gap=12
    return H(layers)
add("K4: gap=12 (within stacking tol)", k4())

def k5():
    """Bars rotation 1° (under tol=2)."""
    layers = perfect_bars()
    for l in layers: l["rotation"] = 1
    return H(layers)
add("K5: all bars 1° rotation", k5())

def k6():
    """4 bars near baseline, 1 bar above (skipped)."""
    layers = perfect_bars()
    layers[2]["y"] = 100  # 3rd bar floats up
    return H(layers)
add("K6: 1 bar floating (not on baseline)", k6())

def k7():
    """Bars touch each other (gap=0)."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["x"] = 500 + i * 30  # gap=0
    return H(layers)
add("K7: bars touching (gap=0)", k7())

def k8():
    """Bars cornerRadius=2 (subtle rounded)."""
    layers = perfect_bars()
    for l in layers: l["cornerRadius"] = 2
    return H(layers)
add("K8: bars cornerRadius 2", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """1st bar fill alpha=0."""
    layers = perfect_bars()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: 1st bar alpha=0", l1())

def l2():
    """All bars visible=False."""
    layers = perfect_bars()
    for l in layers: l["visible"] = False
    return H(layers)
add("L2: all bars visible=False", l2())

def l3():
    """All bars opacity=0."""
    layers = perfect_bars()
    for l in layers: l["opacity"] = 0
    return H(layers)
add("L3: all bars opacity=0", l3())

def l4():
    """All bars fillOpacity=0.05."""
    layers = perfect_bars()
    for l in layers: l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L4: all bars fillOpacity=0.05", l4())

def l5():
    """3 of 5 bars invisible (fills empty)."""
    layers = perfect_bars()
    for i in [0, 2, 4]: layers[i]["fills"] = []
    return H(layers)
add("L5: 3 bars no fill", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Bars all same exact rect (overlapping pile)."""
    layers = perfect_bars()
    for l in layers:
        l["x"] = 500
        l["y"] = 300
        l["w"] = 30
        l["h"] = 300
    return H(layers)
add("M1: all bars piled at one point", m1())

def m2():
    """Frame 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("M2: frame 2000x2000", m2())

def m3():
    """Bars are wider than tall (horizontal, not vertical)."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["w"] = 200
        l["h"] = 30
        l["x"] = 100
        l["y"] = 100 + i * 40
    return H(layers)
add("M3: bars horizontal not vertical", m3())

def m4():
    """Bars are stacked vertically (all same x)."""
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["x"] = 500
        l["y"] = 100 + i * 100
    return H(layers)
add("M4: bars stacked vertically", m4())

def m5():
    """Bars share TOP edge instead of BOTTOM."""
    layers = perfect_bars()
    for l in layers: l["y"] = 200
    return H(layers)
add("M5: bars share top edge", m5())

def m6():
    """First bar = full frame."""
    layers = perfect_bars()
    layers[0] = L("rectangle", 0, 0, 1280, 832, LIGHT_BLUE)
    return H(layers)
add("M6: 1st bar = full frame", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Bars split across 2 frames (3 + 2)."""
    bars = perfect_bars()
    f1 = make_frame(bars[:3], w=640, h=832)
    f2 = make_frame(bars[3:], w=640, h=832)
    return make_log([f1, f2], evt())
add("N1: 3+2 bars in 2 frames", n1())

def n2():
    """Each bar in its own frame."""
    bars = perfect_bars()
    frames = [make_frame([s], w=1280, h=832) for s in bars]
    return make_log(frames, evt())
add("N2: each bar in own frame", n2())

def n3():
    """Bars on page (no frame)."""
    return make_log(perfect_bars(), evt())
add("N3: bars on page (no frame)", n3())

def n4():
    """Bars on page 2."""
    bars = perfect_bars()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(bars, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("N4: bars on page 2", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Bars are ellipses (not rectangles)."""
    layers = []
    heights = [100, 200, 300, 250, 150]
    for i, h in enumerate(heights):
        layers.append(make_layer("ellipse", x=500 + i * 40, y=600 - h, w=30, h=h, fill=LIGHT_BLUE))
    return H(layers, evts=[make_event("session_start"),
                            make_event("tool_change", before="select", after="ellipse")] +
                          [make_event("create_ellipse")] * 5)
add("O1: bars are ellipses", o1())

def o2():
    """Bars are polygons (rectangles)."""
    layers = []
    heights = [100, 200, 300, 250, 150]
    for i, h in enumerate(heights):
        layers.append(make_layer("polygon", x=500 + i * 40, y=600 - h, w=30, h=h, fill=LIGHT_BLUE, sides=4))
    return H(layers, evts=[make_event("session_start"),
                            make_event("tool_change", before="select", after="polygon")] +
                          [make_event("create_polygon")] * 5)
add("O2: bars are 4-sided polygons", o2())

def o3():
    """Bars are lines (vertical line type)."""
    layers = []
    heights = [100, 200, 300, 250, 150]
    for i, h in enumerate(heights):
        line = make_layer("line", x=500 + i * 40, y=600 - h, w=2, h=h, fill=None)
        layers.append(line)
    return H(layers, evts=[make_event("session_start"),
                            make_event("tool_change", before="select", after="line")] +
                          [make_event("create_line")] * 5)
add("O3: bars are lines", o3())

def o4():
    """Bars are vector shapes."""
    layers = []
    heights = [100, 200, 300, 250, 150]
    for i, h in enumerate(heights):
        layers.append(make_layer("vector", x=500 + i * 40, y=600 - h, w=30, h=h, fill=LIGHT_BLUE))
    return H(layers, evts=[make_event("session_start"),
                            make_event("tool_change", before="select", after="pen")] +
                          [make_event("create_vector")] * 5)
add("O4: bars are vectors", o4())


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
    print("─" * 130)
    for i, (label, log) in enumerate(CASES, 1):
        try:
            score, b = score_task(T, log)
            breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
            eff = b["efficiency"]
            flag = " ⚠ FP" if score >= 0.95 else ""
            print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
        except Exception as e:
            print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

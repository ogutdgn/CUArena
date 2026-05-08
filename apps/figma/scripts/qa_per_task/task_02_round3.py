"""Round 3 edge cases — hunt for surviving false positives in task_02."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW,
    PURPLE, GREEN, RED, NAVY, WHITE, BLACK, GOLD, CYAN,
)
from tasks import task_02_sunset_gradient as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
SUNSET = [DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW]


def evt(rect=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bands():
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200, 100 + i*80, 600, 80, c))
    return bands


def H(layers=None, frame_w=1000, frame_h=600, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bands()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Bands sized just above min_h (20px tall)."""
    bands = [L("rectangle", 200, 100+i*20, 200, 20, SUNSET[i]) for i in range(5)]
    return H(bands, frame_w=400, frame_h=200)
add("K1: bands at min height (20px)", k1())

def k2():
    """All sunset colors but second band's R/G is just inside tolerance."""
    bands = perfect_bands()
    bands[1]["fills"][0]["color"] = {"r":0.9, "g":0.4, "b":0.65, "a":1.0}  # close-ish to pink
    return H(bands)
add("K2: pink slightly off (within tol)", k2())

def k3():
    """Bands rotated 1.9° each (just under tolerance)."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 1.9
    return H(bands)
add("K3: bands rotated 1.9° (under 2° tol)", k3())

def k4():
    """All bands cornerRadius=24 (30% of height) — at boundary."""
    bands = perfect_bands()
    for b in bands: b["cornerRadius"] = 23  # 23/80 = 0.28 < 0.30
    return H(bands)
add("K4: corner radius 23/80 (just under 0.30 frac)", k4())

def k5():
    """Bands stacked but in z-order reversed (1st in list = last visually)."""
    bands = perfect_bands()
    bands.reverse()
    return H(bands)
add("K5: bands z-order reversed", k5())

def k6():
    """Bands with 3px stack tolerance (just-under)."""
    bands = []
    cur = 100
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200, cur, 600, 80, c))
        cur += 80 + 3
    return H(bands)
add("K6: 3px gaps (under 4px tol)", k6())

def k7():
    """Bands stacked, but one band is wider (by 3px = within same-dim tol)."""
    bands = perfect_bands()
    bands[2]["w"] = 603
    return H(bands)
add("K7: 1 band 3px wider (within tol)", k7())

def k8():
    """4 sunset bands plus 1 sunset-colored band that's slightly different green."""
    bands = perfect_bands()
    bands[2]["fills"][0]["color"] = {"r":0.0, "g":1.0, "b":0.5, "a":1.0}  # green not orange
    return H(bands)
add("K8: 3rd band is green, not orange", k8())

def k9():
    """Bands present but with 6 of them (1 extra hidden behind)."""
    bands = perfect_bands()
    # add an extra band at same y as 3rd, hidden underneath
    bands.append(L("rectangle", 200, 260, 600, 80, GREEN))  # same y as 3rd
    return H(bands, evts=evt(rect=6))
add("K9: 6 bands (1 hidden)", k9())

def k10():
    """All bands have visible=False on the layer."""
    bands = perfect_bands()
    for b in bands: b["visible"] = False
    return H(bands)
add("K10: all bands layer.visible=False", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """All bands fill alpha=0 (totally invisible)."""
    bands = perfect_bands()
    for b in bands: b["fills"][0]["color"]["a"] = 0.0
    return H(bands)
add("L1: all fill alpha=0", l1())

def l2():
    """All bands fill.visible=False."""
    bands = perfect_bands()
    for b in bands: b["fills"][0]["visible"] = False
    return H(bands)
add("L2: all fill visible=False", l2())

def l3():
    """All bands layer.opacity=0."""
    bands = perfect_bands()
    for b in bands: b["opacity"] = 0.0
    return H(bands)
add("L3: all layer opacity=0", l3())

def l4():
    """All bands have only image fill (no visible solid color)."""
    bands = perfect_bands()
    for b in bands:
        b["fills"] = [{"kind": "image", "src": "blank.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(bands)
add("L4: all bands image fill (no visible color)", l4())

def l5():
    """All bands fill.opacity=0.05 (near-invisible)."""
    bands = perfect_bands()
    for b in bands: b["fills"][0]["opacity"] = 0.05
    return H(bands)
add("L5: all bands fill opacity=0.05", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Bands stacked but 1st band 2x normal width (asymmetric)."""
    bands = perfect_bands()
    bands[0]["w"] = 1200
    bands[0]["x"] = 0
    return H(bands)
add("M1: 1st band 2x width", m1())

def m2():
    """Bands' colors = sunset, but all overlapping at same y."""
    return H([L("rectangle", 200, 200, 600, 80, c) for c in SUNSET])
add("M2: all bands at same y (overlapping)", m2())

def m3():
    """Bands stacked but tiny 1px gap (within stack tol)."""
    bands = []
    cur = 100
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200, cur, 600, 80, c))
        cur += 80 + 1
    return H(bands)
add("M3: bands 1px gap (just inside tol)", m3())

def m4():
    """5 bands but 4 are normal and 1 is 2x height (proportions broken)."""
    bands = perfect_bands()
    bands[2]["h"] = 200  # 200 vs 80 = wildly different
    bands[3]["y"] = bands[2]["y"] + 200
    bands[4]["y"] = bands[2]["y"] + 280
    return H(bands)
add("M4: 1 band 2.5x height", m4())

def m5():
    """Bands stacked but 1 band has a flipped scaleY (still horizontal looking)."""
    bands = perfect_bands()
    bands[2]["scaleY"] = -1
    return H(bands)
add("M5: 1 band scaleY=-1", m5())

def m6():
    """All bands with negative widths (flipped via dimension)."""
    bands = []
    for i, c in enumerate(SUNSET):
        b = L("rectangle", 800, 100+i*80, 600, 80, c)
        b["w"] = -600  # negative
        bands.append(b)
    return H(bands)
add("M6: bands with negative w (flipped)", m6())

def m7():
    """Bands have scaleX=-1 (mirrored)."""
    bands = perfect_bands()
    for b in bands: b["scaleX"] = -1
    return H(bands)
add("M7: all bands scaleX=-1", m7())

def m8():
    """Frame is rotated 90°, bands inside still valid orientation but visually wrong."""
    bands = perfect_bands()
    frame = make_frame(bands, w=1000, h=600)
    frame["rotation"] = 90
    return make_log([frame], evt())
add("M8: frame rotated 90°", m8())


# ─── N. Hierarchy / structural tricks ────────────────────────────────
def n1():
    """Bands inside group inside frame (group as wrapper)."""
    bands = perfect_bands()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": bands}
    frame = make_frame([g], w=1000, h=600)
    return make_log([frame], evt())
add("N1: bands buried in group", n1())

def n2():
    """Bands as siblings of frame (some in, some out)."""
    bands = perfect_bands()
    frame = make_frame(bands[:3], w=1000, h=600)
    return make_log([frame, *bands[3:]], evt())
add("N2: 3 in frame, 2 outside", n2())

def n3():
    """Bands inside instance/component."""
    bands = perfect_bands()
    inst = {"id": "i1", "type": "instance", "x": 0, "y": 0,
            "w": 1000, "h": 600, "fills": [], "strokes": [], "effects": [],
            "children": bands}
    return make_log([inst], evt())
add("N3: bands inside instance (no frame)", n3())


# ─── O. Wrong shape types substituted ────────────────────────────────
def o1():
    """Bands replaced by polygons (4-sided)."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(make_layer("polygon", x=200, y=100+i*80, w=600, h=80, fill=c, sides=4))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    sem.extend([make_event("create_polygon")] * 5)
    return H(bands, evts=sem)
add("O1: 5 polygons instead of rectangles", o1())

def o2():
    """3 rectangles + 2 ellipses passing for bands."""
    bands = perfect_bands()[:3]
    bands.append(make_layer("ellipse", x=200, y=340, w=600, h=80, fill=YELLOW))
    bands.append(make_layer("ellipse", x=200, y=420, w=600, h=80, fill=PALE_YELLOW))
    sem = evt(rect=3, extras=[make_event("tool_change", before="rectangle", after="ellipse"),
                                make_event("create_ellipse"), make_event("create_ellipse")])
    return H(bands, evts=sem)
add("O2: 3 rect + 2 ellipses (mixed types)", o2())

def o3():
    """All bands are stars (5-pointed)."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(make_layer("star", x=200, y=100+i*80, w=600, h=80, fill=c, points=5, innerRatio=0.4))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 5)
    return H(bands, evts=sem)
add("O3: bands as stars", o3())

def o4():
    """All bands are lines (no fill, just stroke)."""
    bands = []
    for i, c in enumerate(SUNSET):
        b = make_layer("line", x=200, y=100+i*80, w=600, h=2, fill=None)
        b["fills"] = []
        b["strokes"] = [make_stroke(rgb=c, weight=80)]
        bands.append(b)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.extend([make_event("create_line")] * 5)
    return H(bands, evts=sem)
add("O4: bands as lines", o4())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95:
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95): {fp_count}")

"""Round-3 novel-deception battery for task 47 (sunburst badge).

30+ NEW edge cases not in the round-1 battery. Hunts for surviving false
positives via subtle deception (K), visibility tricks (L), geometry tricks
(M), structural tricks (N), and wrong-type substitutions (O).
"""
from __future__ import annotations
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))                # scripts/
sys.path.insert(0, str(HERE.parent.parent))         # apps/figma/

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task,
    PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    BLACK, LIGHT_GRAY, DARK_GRAY, WARM_ORANGE, CREAM, DEEP_BLUE, TEAL,
    COBALT, MAGENTA, SAND, PALE_YELLOW, DEEP_PURPLE,
)
import importlib.util
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_47" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
def evt(star=1, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("tool_change", before="star", after="ellipse")]
    for _ in range(star):    sem.append(make_event("create_star"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_badge():
    star = L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)
    circle = L("ellipse", 460, 460, 80, 80, CREAM)
    return [star, circle]


def H(layers=None, evts=None, in_frame=False):
    if layers is None: layers = perfect_badge()
    if in_frame:
        frame = make_frame(layers, w=1280, h=832, fill=(0.95, 0.95, 0.95))
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions (8) ───────────────────────────────────────
def k1():
    """Star rotated by 1.5° — under default 2° tolerance."""
    layers = perfect_badge()
    layers[0]["rotation"] = 1.5
    return H(layers)
add("K1: star rotated 1.5° (under tol)", k1())

def k2():
    """Circle at exact star bottom-right edge — passes BoundsInside."""
    layers = perfect_badge()
    layers[1]["x"] = 380 + 240 - 80
    layers[1]["y"] = 380 + 240 - 80
    return H(layers)
add("K2: circle at star's bottom-right corner", k2())

def k3():
    """Star with 7 points — close to 8 but wrong."""
    layers = perfect_badge()
    layers[0]["points"] = 7
    return H(layers)
add("K3: star has 7 points", k3())

def k4():
    """Star points=8 but as a string '8' — type confusion."""
    layers = perfect_badge()
    layers[0]["points"] = "8"
    return H(layers)
add("K4: star points='8' (string)", k4())

def k5():
    """Circle at exactly 70% of star — borderline LayerSmallerThanLayer."""
    layers = perfect_badge()
    cx, cy = 500, 500
    sz = 240 * 0.71  # just over threshold
    layers[1]["x"] = cx - sz/2
    layers[1]["y"] = cy - sz/2
    layers[1]["w"] = sz
    layers[1]["h"] = sz
    return H(layers)
add("K5: circle 71% of star (over LayerSmaller threshold)", k5())

def k6():
    """Circle behind star (z-order swap)."""
    star, circle = perfect_badge()
    return H([circle, star])  # circle first = under
add("K6: circle behind star (z-order swap)", k6())

def k7():
    """Star with innerRatio extreme = 0.85 (almost circular)."""
    layers = perfect_badge()
    layers[0]["innerRatio"] = 0.85  # within 0.5±0.3 = passes barely
    return H(layers)
add("K7: star innerRatio=0.85 (almost circle)", k7())

def k8():
    """Star with innerRatio=0.0 (super spiky)."""
    layers = perfect_badge()
    layers[0]["innerRatio"] = 0.0
    return H(layers)
add("K8: star innerRatio=0.0 (extreme spike)", k8())


# ─── L. Visibility tricks (6) ───────────────────────────────────────
def l1():
    """Star fill alpha=0.3 — under 0.5 LayerVisible threshold."""
    layers = perfect_badge()
    layers[0]["fills"][0]["color"]["a"] = 0.3
    return H(layers)
add("L1: star fill alpha=0.3", l1())

def l2():
    """Circle fill alpha=0.4."""
    layers = perfect_badge()
    layers[1]["fills"][0]["color"]["a"] = 0.4
    return H(layers)
add("L2: circle fill alpha=0.4", l2())

def l3():
    """Star opacity=0.4 (layer-level)."""
    layers = perfect_badge()
    layers[0]["opacity"] = 0.4
    return H(layers)
add("L3: star layer opacity=0.4", l3())

def l4():
    """Circle visible=False (layer-level)."""
    layers = perfect_badge()
    layers[1]["visible"] = False
    return H(layers)
add("L4: circle visible=False", l4())

def l5():
    """Both shapes fill opacity 0.45 (just under LayerVisible)."""
    layers = perfect_badge()
    layers[0]["fills"][0]["opacity"] = 0.45
    layers[1]["fills"][0]["opacity"] = 0.45
    return H(layers)
add("L5: both shapes fill opacity 0.45", l5())

def l6():
    """Star fill is image with cream color overlay (image fills bypass solid checks)."""
    layers = perfect_badge()
    layers[0]["fills"] = [{"kind": "image", "src": "warm-orange.jpg",
                           "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("L6: star image fill (cream-orange image)", l6())


# ─── M. Geometry tricks (8) ─────────────────────────────────────────
def m1():
    """Star and circle at exact same x,y,w,h (degenerate overlap)."""
    layers = [L("star", 400, 400, 200, 200, WARM_ORANGE, points=8, innerRatio=0.5),
              L("ellipse", 400, 400, 200, 200, CREAM)]  # same size as star
    return H(layers)
add("M1: star and circle exact same bounds", m1())

def m2():
    """Star w=200, h=20 (squashed flat)."""
    layers = perfect_badge()
    layers[0]["w"] = 200
    layers[0]["h"] = 20  # super flat
    return H(layers)
add("M2: star 200×20 squashed flat", m2())

def m3():
    """Star w=20, h=200 (squashed thin)."""
    layers = perfect_badge()
    layers[0]["w"] = 20
    layers[0]["h"] = 200
    return H(layers)
add("M3: star 20×200 squashed thin", m3())

def m4():
    """Circle has w=80, h=20 (oval not circle, but min < 15 fails LayerSizeAtLeast)."""
    layers = perfect_badge()
    layers[1]["w"] = 80; layers[1]["h"] = 20  # not circular
    return H(layers)
add("M4: circle 80x20 (not round, min<size)", m4())

def m5():
    """Star at exact center of circle (circle larger and contains star)."""
    layers = [L("star", 480, 480, 80, 80, WARM_ORANGE, points=8, innerRatio=0.5),
              L("ellipse", 400, 400, 240, 240, CREAM)]  # circle bigger than star
    return H(layers)
add("M5: roles swapped (small star, big circle)", m5())

def m6():
    """Circle at corner of star but outside it (passes Centered if tol high)."""
    layers = perfect_badge()
    layers[1]["x"] = 380 - 100
    layers[1]["y"] = 380 - 100  # above-left of star
    return H(layers)
add("M6: circle outside star top-left", m6())

def m7():
    """Star that's 30×30 (just over the 40 minimum) — borderline tiny."""
    layers = perfect_badge()
    layers[0]["w"] = 30; layers[0]["h"] = 30
    layers[1]["x"] = 380; layers[1]["y"] = 380
    layers[1]["w"] = 10; layers[1]["h"] = 10
    return H(layers)
add("M7: star 30×30 (under 40 LayerSizeAtLeast)", m7())

def m8():
    """Circle's centroid matches star's, but with negative w/h (degenerate)."""
    layers = perfect_badge()
    layers[1]["w"] = 0
    layers[1]["h"] = 0
    return H(layers)
add("M8: circle 0×0 (degenerate)", m8())


# ─── N. Structural / hierarchy tricks (4) ───────────────────────────
def n1():
    """Star inside frame, circle outside (page-level)."""
    star, circle = perfect_badge()
    frame = make_frame([star], w=1280, h=832)
    return make_log([frame, circle], evt())
add("N1: star in frame, circle on page", n1())

def n2():
    """Both inside a Component (not a frame)."""
    layers = perfect_badge()
    component = {"id": "comp1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "strokes": [],
                 "effects": [], "children": layers}
    return make_log([component], evt())
add("N2: badge in component", n2())

def n3():
    """Circle is direct child of star (nested in children)."""
    star, circle = perfect_badge()
    star["children"] = [circle]
    return make_log([star], evt())
add("N3: circle is child of star", n3())

def n4():
    """Two stars, one with 8 points, one with 5 points, both visible."""
    s1 = L("star", 200, 200, 200, 200, WARM_ORANGE, points=8, innerRatio=0.5)
    s2 = L("star", 600, 600, 200, 200, WARM_ORANGE, points=5, innerRatio=0.4)
    circle = L("ellipse", 280, 280, 60, 60, CREAM)
    return make_log([s1, s2, circle], evt(star=2))
add("N4: 2 stars (8pt + 5pt), one circle", n4())


# ─── O. Wrong-type substitutions (5) ────────────────────────────────
def o1():
    """Polygon with 8 sides instead of star (octagonal lookalike)."""
    octa = make_layer("polygon", x=380, y=380, w=240, h=240,
                      fill=WARM_ORANGE, sides=8)
    circle = L("ellipse", 460, 460, 80, 80, CREAM)
    return make_log([octa, circle], evt(star=0,
                                          extras=[make_event("create_polygon")]))
add("O1: polygon-8 instead of star", o1())

def o2():
    """Rectangle with rounded corners instead of star."""
    rect = make_layer("rectangle", x=380, y=380, w=240, h=240,
                     fill=WARM_ORANGE, cornerRadius=120)
    circle = L("ellipse", 460, 460, 80, 80, CREAM)
    return make_log([rect, circle], evt(star=0,
                                          extras=[make_event("create_rectangle")]))
add("O2: rounded rectangle instead of star", o2())

def o3():
    """Star but circle replaced with rectangle of same size."""
    star = L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)
    rect = make_layer("rectangle", x=460, y=460, w=80, h=80, fill=CREAM)
    return make_log([star, rect], evt(ellipse=0,
                                       extras=[make_event("create_rectangle")]))
add("O3: rectangle instead of circle", o3())

def o4():
    """Circle is a polygon-32 (visually round but typed as polygon)."""
    star = L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)
    poly = make_layer("polygon", x=460, y=460, w=80, h=80, fill=CREAM, sides=32)
    return make_log([star, poly], evt(ellipse=0,
                                       extras=[make_event("create_polygon")]))
add("O4: polygon-32 instead of ellipse", o4())

def o5():
    """Vector path traced as star outline (star tool not used)."""
    vec = make_layer("vector", x=380, y=380, w=240, h=240, fill=WARM_ORANGE)
    circle = L("ellipse", 460, 460, 80, 80, CREAM)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse"),
           make_event("create_vector"),
           make_event("create_ellipse")]
    return make_log([vec, circle], sem)
add("O5: vector pen-traced star + circle", o5())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " ⚠ FP" if score >= 0.95 else ""
        if score >= 0.95: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\n{fp_count} cases scored ≥ 0.95")

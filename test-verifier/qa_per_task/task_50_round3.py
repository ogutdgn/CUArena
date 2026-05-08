"""Round-3 novel-deception battery for task 50 (album cover).

30+ NEW edge cases not in the round-1 battery. Categories K (subtle),
L (visibility), M (geometry), N (structural), O (wrong types).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN, PINK,
    ORANGE, BLACK,
)
from tasks import task_50_album_cover as t
T = t.task


def evt(rect=1, star=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="star")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(star): sem.append(make_event("create_star"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_cover():
    cx, cy = 500, 500
    sq = L("rectangle", cx-150, cy-150, 300, 300, NAVY)
    star = L("star", cx-80, cy-80, 160, 160, YELLOW,
              points=5, innerRatio=0.4,
              strokes=[make_stroke(rgb=WHITE, weight=4)])
    return [sq, star]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_cover()
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions (8) ───────────────────────────────────────
def k1():
    """Star rotated 9° — under 10° tolerance."""
    layers = perfect_cover()
    layers[1]["rotation"] = 9
    return H(layers)
add("K1: star rotated 9° (under tol)", k1())

def k2():
    """Square rotated 1.5° — under 2° tolerance."""
    layers = perfect_cover()
    layers[0]["rotation"] = 1.5
    return H(layers)
add("K2: square rotated 1.5° (under tol)", k2())

def k3():
    """Star at exactly 84% of square (just under 85% max_frac)."""
    layers = perfect_cover()
    cx, cy = 500, 500
    sz = 300 * 0.84  # 252
    layers[1]["x"] = cx - sz/2
    layers[1]["y"] = cy - sz/2
    layers[1]["w"] = sz
    layers[1]["h"] = sz
    return H(layers)
add("K3: star 84% of square (just under cap)", k3())

def k4():
    """Square w=302, h=298 — within 10px LayerIsSquare tolerance but not square."""
    layers = perfect_cover()
    layers[0]["w"] = 302; layers[0]["h"] = 298
    return H(layers)
add("K4: rectangle 302×298 (just within IsSquare tol)", k4())

def k5():
    """Star w=200, h=170 — w!=h (oval-star)."""
    layers = perfect_cover()
    layers[1]["w"] = 200; layers[1]["h"] = 170
    return H(layers)
add("K5: star 200×170 stretched", k5())

def k6():
    """Star behind square (z-order swap)."""
    sq, star = perfect_cover()
    return H([star, sq])  # star first = under
add("K6: star behind square (z-order)", k6())

def k7():
    """Stroke weight 4.9 — within 4±1 tolerance."""
    layers = perfect_cover()
    layers[1]["strokes"][0]["weight"] = 4.9
    return H(layers)
add("K7: stroke weight 4.9 (within tol)", k7())

def k8():
    """Star innerRatio=0.7 — within 0.4±0.3 boundary."""
    layers = perfect_cover()
    layers[1]["innerRatio"] = 0.7
    return H(layers)
add("K8: star innerRatio=0.7 (boundary)", k8())


# ─── L. Visibility tricks (6) ───────────────────────────────────────
def l1():
    """Square fill alpha=0.3 — under LayerVisible threshold."""
    layers = perfect_cover()
    layers[0]["fills"][0]["color"]["a"] = 0.3
    return H(layers)
add("L1: square fill alpha=0.3", l1())

def l2():
    """Star fill alpha=0.4."""
    layers = perfect_cover()
    layers[1]["fills"][0]["color"]["a"] = 0.4
    return H(layers)
add("L2: star fill alpha=0.4", l2())

def l3():
    """Star opacity=0 (layer)."""
    layers = perfect_cover()
    layers[1]["opacity"] = 0
    return H(layers)
add("L3: star opacity=0", l3())

def l4():
    """Square visible=False."""
    layers = perfect_cover()
    layers[0]["visible"] = False
    return H(layers)
add("L4: square visible=False", l4())

def l5():
    """Star stroke alpha=0 (invisible white)."""
    layers = perfect_cover()
    layers[1]["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("L5: star stroke alpha=0", l5())

def l6():
    """Both fills opacity=0.45 (just below 0.5 visibility)."""
    layers = perfect_cover()
    layers[0]["fills"][0]["opacity"] = 0.45
    layers[1]["fills"][0]["opacity"] = 0.45
    return H(layers)
add("L6: both fills opacity=0.45", l6())


# ─── M. Geometry tricks (8) ─────────────────────────────────────────
def m1():
    """Square and star at same exact bounds (degenerate)."""
    layers = [L("rectangle", 400, 400, 200, 200, NAVY),
              L("star", 400, 400, 200, 200, YELLOW, points=5, innerRatio=0.4,
                 strokes=[make_stroke(rgb=WHITE, weight=4)])]
    return H(layers)
add("M1: square and star same bounds", m1())

def m2():
    """Star is bigger than square (87% just over 85% max_frac)."""
    layers = perfect_cover()
    cx, cy = 500, 500
    sz = 300 * 0.87  # 261
    layers[1]["x"] = cx - sz/2; layers[1]["y"] = cy - sz/2
    layers[1]["w"] = sz; layers[1]["h"] = sz
    return H(layers)
add("M2: star 87% of square (over cap)", m2())

def m3():
    """Square w=400, h=200 (rectangle, not square — outside 10px tol)."""
    layers = perfect_cover()
    layers[0]["w"] = 400; layers[0]["h"] = 200
    return H(layers)
add("M3: rect 400×200 not square", m3())

def m4():
    """Star at corner of square (still inside but off-center)."""
    layers = perfect_cover()
    layers[1]["x"] = 350; layers[1]["y"] = 350  # near top-left corner
    return H(layers)
add("M4: star at square corner", m4())

def m5():
    """Star outside square (fully detached)."""
    layers = perfect_cover()
    layers[1]["x"] = 1000; layers[1]["y"] = 1000
    return H(layers)
add("M5: star fully outside square", m5())

def m6():
    """Square 30×30 (under min size of 40)."""
    layers = perfect_cover()
    layers[0]["w"] = 30; layers[0]["h"] = 30
    layers[1]["w"] = 20; layers[1]["h"] = 20
    layers[1]["x"] = 505; layers[1]["y"] = 505  # adjust center
    return H(layers)
add("M6: square 30×30 (under LayerSizeAtLeast)", m6())

def m7():
    """Star 15×15 (under min 20)."""
    layers = perfect_cover()
    layers[1]["w"] = 15; layers[1]["h"] = 15
    return H(layers)
add("M7: star 15×15 (under min)", m7())

def m8():
    """Both shapes at huge size (3000×3000)."""
    layers = perfect_cover()
    layers[0]["w"] = 3000; layers[0]["h"] = 3000
    layers[1]["w"] = 1500; layers[1]["h"] = 1500
    return H(layers)
add("M8: both shapes 3000×3000 (over cap)", m8())


# ─── N. Hierarchy / structural tricks (4) ───────────────────────────
def n1():
    """Star is child of square (nested in children)."""
    sq, star = perfect_cover()
    sq["children"] = [star]
    return make_log([sq], evt())
add("N1: star is child of square", n1())

def n2():
    """Both inside instance>component."""
    layers = perfect_cover()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "children": layers}
    return make_log([component], evt())
add("N2: cover in component", n2())

def n3():
    """Star floats above square but in different layer order (square last)."""
    sq, star = perfect_cover()
    return H([star, sq])  # square last = on top in z-order
add("N3: square in front of star (z-order swap)", n3())

def n4():
    """Cover inside section inside frame."""
    layers = perfect_cover()
    sec = {"id": "sec1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
           "fills": [], "children": layers}
    frame = make_frame([sec], w=1280, h=832)
    return make_log([frame], evt())
add("N4: cover in section in frame", n4())


# ─── O. Wrong types (5) ─────────────────────────────────────────────
def o1():
    """Polygon-4 (square) instead of rectangle."""
    poly = make_layer("polygon", x=350, y=350, w=300, h=300, fill=NAVY, sides=4)
    sq, star = perfect_cover()
    return make_log([poly, star], evt(rect=0,
                                       extras=[make_event("create_polygon")]))
add("O1: polygon-4 instead of rectangle", o1())

def o2():
    """Polygon-5 instead of star (visually similar pentagon-not-star)."""
    sq, star = perfect_cover()
    poly = make_layer("polygon", x=420, y=420, w=160, h=160, fill=YELLOW,
                       sides=5, strokes=[make_stroke(rgb=WHITE, weight=4)])
    return make_log([sq, poly], evt(star=0,
                                      extras=[make_event("create_polygon")]))
add("O2: polygon-5 instead of star", o2())

def o3():
    """Ellipse instead of square."""
    sq, star = perfect_cover()
    ell = make_layer("ellipse", x=350, y=350, w=300, h=300, fill=NAVY)
    return make_log([ell, star], evt(rect=0,
                                       extras=[make_event("create_ellipse")]))
add("O3: ellipse instead of square", o3())

def o4():
    """Rectangle with cornerRadius=150 (round) instead of square."""
    sq, star = perfect_cover()
    sq["cornerRadius"] = 150
    return H([sq, star])
add("O4: rectangle cornerRadius=150 (round)", o4())

def o5():
    """Vector instead of star."""
    sq, _ = perfect_cover()
    vec = make_layer("vector", x=420, y=420, w=160, h=160, fill=YELLOW,
                       strokes=[make_stroke(rgb=WHITE, weight=4)])
    return make_log([sq, vec], evt(star=0,
                                     extras=[make_event("create_vector")]))
add("O5: vector instead of star", o5())


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

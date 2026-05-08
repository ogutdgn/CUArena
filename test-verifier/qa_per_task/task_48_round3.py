"""Round-3 novel-deception battery for task 48 (spiderweb).

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
from tasks import task_48_spiderweb as t
T = t.task


def evt(n_lines=4, n_hex=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line"),
           make_event("tool_change", before="line", after="polygon")]
    for _ in range(n_lines): sem.append(make_event("create_line"))
    for _ in range(n_hex):   sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def perfect_web():
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    hexes = []
    for i in range(2):
        sz = 100 + i * 60
        hexes.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    return make_frame([*lines, *hexes], w=800, h=800, fill=NAVY)


def H(frame=None, evts=None):
    if frame is None: frame = perfect_web()
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions (8) ───────────────────────────────────────
def k1():
    """Lines rotated by 1.5° from canonical 90° steps (under 10° tol)."""
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["rotation"] = i * 90 + 1.5  # 1.5°, 91.5°, 181.5°, 271.5°
    return H(f)
add("K1: lines 91.5° step (within tol)", k1())

def k2():
    """Lines at 360° instead of 0° (modulo trick)."""
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["rotation"] = i * 90 + 360
    return H(f)
add("K2: lines all at +360° offset", k2())

def k3():
    """Hexagons concentric but inner is just barely smaller (1.31x ratio)."""
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    cx, cy = 400, 400
    polys[0]["x"] = cx - 100; polys[0]["y"] = cy - 100
    polys[0]["w"] = 200; polys[0]["h"] = 200
    polys[1]["x"] = cx - 88; polys[1]["y"] = cy - 88
    polys[1]["w"] = 175; polys[1]["h"] = 175  # ratio = 200²/175² = 1.31
    return H(f)
add("K3: hexagons just over 1.3x ratio", k3())

def k4():
    """Frame fill alpha=0.55 — just above 0.5 LayerVisible threshold."""
    f = perfect_web()
    f["fills"][0]["color"]["a"] = 0.55
    return H(f)
add("K4: frame alpha=0.55 (just over LayerVisible tol)", k4())

def k5():
    """Star sneak in (a 6-pointed star looks hex-like)."""
    f = perfect_web()
    f["children"].append(make_layer("star", x=300, y=300, w=200, h=200,
                                     fill=None, strokes=[make_stroke(rgb=WHITE, weight=1)],
                                     points=6, innerRatio=0.5))
    return H(f, evts=evt(extras=[make_event("create_star")]))
add("K5: extra hex-like 6-point star", k5())

def k6():
    """Hexagons concentric exactly the same size (ratio=1)."""
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    cx, cy = 400, 400
    for p in polys:
        p["x"] = cx - 100; p["y"] = cy - 100
        p["w"] = 200; p["h"] = 200
    return H(f)
add("K6: hexagons same size (ratio=1)", k6())

def k7():
    """Frame stretched horizontally (1600×400 not square)."""
    f = perfect_web()
    f["w"] = 1600; f["h"] = 400
    return H(f)
add("K7: frame 1600×400 stretched", k7())

def k8():
    """Lines all at same y, with varied rotation but same starting point."""
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["x"] = 200 + i * 30  # different x positions, so not radial
        l["y"] = 400
        l["rotation"] = i * 90
    return H(f)
add("K8: lines spread out, not from center", k8())


# ─── L. Visibility tricks (6) ───────────────────────────────────────
def l1():
    """All lines visible=False."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["visible"] = False
    return H(f)
add("L1: all lines visible=False", l1())

def l2():
    """All polygons opacity=0."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["opacity"] = 0
    return H(f)
add("L2: all polygons opacity=0", l2())

def l3():
    """Frame fill visible=False."""
    f = perfect_web()
    f["fills"][0]["visible"] = False
    return H(f)
add("L3: frame fill visible=False", l3())

def l4():
    """Lines stroke alpha=0 (invisible white strokes)."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"][0]["paint"]["color"]["a"] = 0
    return H(f)
add("L4: lines stroke alpha=0", l4())

def l5():
    """Polygons stroke weight=0 (zero-width strokes)."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon":
            c["strokes"][0]["weight"] = 0
    return H(f)
add("L5: polygons stroke weight 0", l5())

def l6():
    """Frame is image fill (looks navy but image)."""
    f = perfect_web()
    f["fills"] = [{"kind": "image", "src": "navy.jpg", "fit": "cover",
                  "opacity": 1, "visible": True}]
    return H(f)
add("L6: frame image fill (not solid)", l6())


# ─── M. Geometry tricks (8) ─────────────────────────────────────────
def m1():
    """Lines all at same rotation but different x — not radial."""
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["x"] = 100 + i * 100
        l["rotation"] = 0
    return H(f)
add("M1: 4 horizontal lines (no rotation)", m1())

def m2():
    """Hexagons concentric but huge (overflows frame)."""
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    polys[0]["x"] = -200; polys[0]["y"] = -200
    polys[0]["w"] = 1200; polys[0]["h"] = 1200
    polys[1]["x"] = -100; polys[1]["y"] = -100
    polys[1]["w"] = 1000; polys[1]["h"] = 1000
    return H(f)
add("M2: hexagons overflow frame", m2())

def m3():
    """Lines as zero-width: w=0 (degenerate)."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["w"] = 0
    return H(f)
add("M3: lines w=0", m3())

def m4():
    """Hexagons concentric but rotated 60° (hex symmetry — visually same)."""
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    for p in polys: p["rotation"] = 60
    return H(f)
add("M4: hexagons rotated 60° (hex symmetric)", m4())

def m5():
    """Lines in non-radial layout (4 in a square)."""
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    layout = [(200, 200, 0), (600, 200, 90), (200, 600, 180), (600, 600, 270)]
    for l, (x, y, rot) in zip(lines, layout):
        l["x"] = x; l["y"] = y; l["rotation"] = rot
    return H(f)
add("M5: lines in 4 corners", m5())

def m6():
    """Hexagons stacked vertically (not concentric)."""
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    polys[0]["x"] = 350; polys[0]["y"] = 200
    polys[1]["x"] = 350; polys[1]["y"] = 500
    return H(f)
add("M6: hexagons stacked vertically", m6())

def m7():
    """Polygon with sides=6 but rendered as solid (not stroked)."""
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon":
            c["fills"] = [{"kind": "solid", "color": {"r": 1, "g": 1, "b": 1, "a": 1},
                          "opacity": 1, "visible": True}]
    return H(f)
add("M7: hexagons have white solid fill (not stroked)", m7())

def m8():
    """Frame at scale 0 (degenerate — w=0, h=0)."""
    f = perfect_web()
    f["w"] = 0; f["h"] = 0
    return H(f)
add("M8: frame 0×0", m8())


# ─── N. Hierarchy / structural tricks (4) ───────────────────────────
def n1():
    """Lines in frame, polygons in a sibling group at same level."""
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    grp = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
           "fills": [], "children": polys}
    f = make_frame([*lines, grp], w=800, h=800, fill=NAVY)
    return make_log([f], evt())
add("N1: polygons in group inside frame (not direct)", n1())

def n2():
    """Each line in its own 1-line frame."""
    cx, cy = 400, 400
    line_frames = []
    for i in range(4):
        l = make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                       strokes=[make_stroke(rgb=WHITE, weight=1)],
                       rotation=i * 90)
        line_frames.append(make_frame([l], w=800, h=800, fill=NAVY))
    return make_log(line_frames, evt())
add("N2: each line in its own frame", n2())

def n3():
    """Frame with no children (empty)."""
    f = make_frame([], w=800, h=800, fill=NAVY)
    return make_log([f], evt(n_lines=0, n_hex=0))
add("N3: empty navy frame", n3())

def n4():
    """Lines + polygons inside a Component, no frame."""
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "children": [*lines, *polys]}
    return make_log([component], evt())
add("N4: web in component (no navy frame)", n4())


# ─── O. Wrong types (5) ─────────────────────────────────────────────
def o1():
    """Rectangles instead of lines."""
    cx, cy = 400, 400
    rects = []
    for i in range(4):
        rects.append(make_layer("rectangle", x=cx, y=cy, w=200, h=2, fill=WHITE,
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    f = make_frame([*rects, *polys], w=800, h=800, fill=NAVY)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(4): sem.append(make_event("create_rectangle"))
    sem.append(make_event("create_polygon"))
    sem.append(make_event("create_polygon"))
    return make_log([f], sem)
add("O1: rectangles substituting lines", o1())

def o2():
    """Ellipses instead of polygons."""
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    ells = []
    for i in range(2):
        sz = 100 + i * 60
        ells.append(make_layer("ellipse", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)]))
    f = make_frame([*lines, *ells], w=800, h=800, fill=NAVY)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line"),
           make_event("tool_change", before="line", after="ellipse")]
    for _ in range(4): sem.append(make_event("create_line"))
    for _ in range(2): sem.append(make_event("create_ellipse"))
    return make_log([f], sem)
add("O2: ellipses substituting hexagons", o2())

def o3():
    """Vectors (pen-drawn) instead of lines."""
    cx, cy = 400, 400
    vecs = []
    for i in range(4):
        vecs.append(make_layer("vector", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    f = make_frame([*vecs, *polys], w=800, h=800, fill=NAVY)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="polygon")]
    for _ in range(4): sem.append(make_event("create_vector"))
    for _ in range(2): sem.append(make_event("create_polygon"))
    return make_log([f], sem)
add("O3: vectors substituting lines (pen used)", o3())

def o4():
    """Polygons with sides=6 but not stroked - only filled."""
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=WHITE,  # filled white, no stroke
                                strokes=[],
                                sides=6))
    f = make_frame([*lines, *polys], w=800, h=800, fill=NAVY)
    return make_log([f], evt())
add("O4: hexagons solid white fill (no stroke)", o4())

def o5():
    """Frame with rectangle as background (rectangle, not navy frame)."""
    cx, cy = 400, 400
    bg_rect = make_layer("rectangle", x=0, y=0, w=800, h=800, fill=NAVY)
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    f = make_frame([bg_rect, *lines, *polys], w=800, h=800, fill=None)
    f["fills"] = []  # no fill on the frame itself
    return make_log([f], evt(extras=[make_event("create_rectangle")]))
add("O5: rectangle background instead of navy frame fill", o5())


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

"""100 edge cases for task 10 — runs all and prints a sorted score table.

Task 10 = 4 nested squares of decreasing size, shared center, alternating two colors.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_10" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
COLOR_A = (0.10, 0.50, 0.90)  # blue
COLOR_B = (0.95, 0.85, 0.20)  # yellow
COLOR_C = (0.95, 0.20, 0.20)  # red (extra)


def evt(rect=4, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="rectangle"))
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def R(x, y, w, h, fill, **extra):
    return make_layer("rectangle", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design(cx=640, cy=400):
    """4 concentric squares, decreasing size, alternating A/B/A/B."""
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    return [R(cx - s/2, cy - s/2, s, s, c) for s, c in zip(sizes, colors)]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    return H(perfect_design()[:3], evts=evt(rect=3))
add("A1: only 3 squares", case_a1())

def case_a2():
    return H(perfect_design()[:2], evts=evt(rect=2))
add("A2: only 2 squares", case_a2())

def case_a3():
    return H(perfect_design()[:1], evts=evt(rect=1))
add("A3: only 1 square", case_a3())

def case_a4():
    """5 nested squares."""
    sizes = [500, 400, 300, 200, 100]
    cx, cy = 640, 400
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B, COLOR_A]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(rect=5))
add("A4: 5 nested squares", case_a4())

def case_a5():
    """0 rectangles."""
    return H([], evts=evt(rect=0))
add("A5: 0 squares", case_a5())

def case_a6():
    """8 nested squares."""
    sizes = [400, 350, 300, 250, 200, 150, 100, 50]
    cx, cy = 640, 400
    colors = [COLOR_A, COLOR_B] * 4
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(rect=8))
add("A6: 8 nested squares (2x extras)", case_a6())

def case_a7():
    """4 nested + 1 extra outside."""
    layers = perfect_design()
    layers.append(R(50, 50, 80, 80, COLOR_C))
    return H(layers, evts=evt(rect=5))
add("A7: 4 nested + 1 outside", case_a7())

def case_a8():
    """4 ellipses (not rects)."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [make_layer("ellipse", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_ellipse")]*4))
add("A8: 4 ellipses (not rects)", case_a8())

def case_a9():
    """4 same size (not nested)."""
    layers = [R(640-50, 400-50, 100, 100, COLOR_A) for _ in range(4)]
    return H(layers)
add("A9: 4 same-size at same spot", case_a9())

def case_a10():
    """Perfect (control)."""
    return H()
add("A10: 4 nested perfect (control)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    """All same color (not alternating)."""
    layers = []
    cx, cy = 640, 400
    for s in [400, 300, 200, 100]:
        layers.append(R(cx-s/2, cy-s/2, s, s, COLOR_A))
    return H(layers)
add("B11: all same color", case_b11())

def case_b12():
    """4 different colors (not alternating 2)."""
    layers = []
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_C, (0.5, 0.5, 0.5)]
    for s, c in zip(sizes, colors):
        layers.append(R(cx-s/2, cy-s/2, s, s, c))
    return H(layers)
add("B12: 4 different colors (no alternation)", case_b12())

def case_b13():
    """All image fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: all image fills", case_b13())

def case_b14():
    """All gradient fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1}},
            {"position": 1, "color": {"r": 0.8, "g": 0.8, "b": 0.8, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("B14: all gradient fills", case_b14())

def case_b15():
    """Stacked 2 fills each."""
    layers = perfect_design()
    for l in layers:
        l["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover",
                           "opacity": 0.5, "visible": True})
    return H(layers)
add("B15: stacked 2 fills each", case_b15())

def case_b16():
    """Stroke-only, no fill."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("B16: stroke-only, no fill", case_b16())

def case_b17():
    """All near-identical (within tolerance)."""
    layers = []
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    near_a = (0.10, 0.50, 0.90)
    near_b = (0.13, 0.50, 0.90)  # near A, within 0.05 tol
    colors = [near_a, near_b, near_a, near_b]
    for s, c in zip(sizes, colors):
        layers.append(R(cx-s/2, cy-s/2, s, s, c))
    return H(layers)
add("B17: all near-identical (within tol)", case_b17())

def case_b18():
    """Fill alpha=0 on outer."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: outer alpha=0", case_b18())

def case_b19():
    """All fill opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: all fill opacity=0.05", case_b19())

def case_b20():
    """Layer opacity=0.05 on innermost."""
    layers = perfect_design()
    layers[3]["opacity"] = 0.05
    return H(layers)
add("B20: innermost opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    """All same size (not decreasing)."""
    cx, cy = 640, 400
    layers = [R(cx-100, cy-100, 200, 200, [COLOR_A, COLOR_B][i % 2]) for i in range(4)]
    return H(layers)
add("C21: all same size", case_c21())

def case_c22():
    """Increasing size (not decreasing)."""
    cx, cy = 640, 400
    sizes = [100, 200, 300, 400]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C22: increasing size (last is biggest)", case_c22())

def case_c23():
    """Sizes near-equal (within tolerance)."""
    cx, cy = 640, 400
    sizes = [202, 200, 198, 196]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C23: sizes within 6px tol", case_c23())

def case_c24():
    """Tiny squares 5x5."""
    cx, cy = 640, 400
    sizes = [20, 15, 10, 5]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C24: tiny <20px squares", case_c24())

def case_c25():
    """Huge outer (way bigger than frame)."""
    cx, cy = 640, 400
    sizes = [1500, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C25: outer 1500x1500 (>frame)", case_c25())

def case_c26():
    """Very rectangular (not square)."""
    cx, cy = 640, 400
    sizes = [(400, 200), (300, 150), (200, 100), (100, 50)]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("C26: 2:1 rectangles (not square)", case_c26())

def case_c27():
    """Tall rectangles."""
    cx, cy = 640, 400
    sizes = [(200, 400), (150, 300), (100, 200), (50, 100)]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("C27: 1:2 (tall) rectangles", case_c27())

def case_c28():
    """Sizes 80% nested (each 80% of prev)."""
    cx, cy = 640, 400
    sizes = [400, 320, 256, 205]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C28: sizes 80% step (gentle)", case_c28())

def case_c29():
    """Outer 50% of frame."""
    cx, cy = 640, 400
    sizes = [600, 450, 300, 150]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C29: outer 600 (50% frame)", case_c29())

def case_c30():
    """Innermost 1×1 degenerate."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 1]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C30: innermost 1×1 degenerate", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    """All offset to one corner (not centered)."""
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(100, 100, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D31: all top-left corner (not concentric)", case_d31())

def case_d32():
    """Each shifted by 50px."""
    cx, cy = 640, 400
    layers = []
    sizes = [400, 300, 200, 100]
    for i, s in enumerate(sizes):
        layers.append(R(cx-s/2 + i*50, cy-s/2 + i*30, s, s,
                        [COLOR_A, COLOR_B][i % 2]))
    return H(layers)
add("D32: each shifted (not concentric)", case_d32())

def case_d33():
    """Random positions."""
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    positions = [(100, 100), (500, 200), (300, 500), (700, 100)]
    layers = [R(x, y, s, s, c) for (x, y), s, c in zip(positions, sizes, colors)]
    return H(layers)
add("D33: random positions", case_d33())

def case_d34():
    """All in horizontal row."""
    layers = []
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    x = 100
    for s, c in zip(sizes, colors):
        layers.append(R(x, 200, s, s, c))
        x += s + 20
    return H(layers, frame_w=2000, frame_h=900)
add("D34: horizontal row", case_d34())

def case_d35():
    """All shifted off frame."""
    cx, cy = 1500, 1000
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D35: shifted off-frame", case_d35())

def case_d36():
    """Concentric, but offset to one side."""
    cx, cy = 200, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D36: concentric but off-center", case_d36())

def case_d37():
    """Nested but each within tol of center."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = []
    for i, (s, c) in enumerate(zip(sizes, colors)):
        layers.append(R(cx-s/2 + (i-1)*1, cy-s/2 + i*1, s, s, c))
    return H(layers)
add("D37: concentric within 3px tol", case_d37())

def case_d38():
    """4 nested at different centers."""
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(100+i*50, 100+i*50, s, s, c) for i, (s, c) in enumerate(zip(sizes, colors))]
    return H(layers)
add("D38: cascading offsets", case_d38())

def case_d39():
    """Concentric but inner outside outer's bounds."""
    cx, cy = 640, 400
    layers = [R(cx-200, cy-200, 400, 400, COLOR_A),
              R(cx-300, cy-300, 200, 200, COLOR_B),  # offset way out
              R(cx-100, cy-100, 200, 200, COLOR_A),
              R(cx-50,  cy-50,  100, 100, COLOR_B)]
    return H(layers)
add("D39: 1 inner outside outer", case_d39())

def case_d40():
    """Centered but extreme far edge."""
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    cx, cy = 30, 30
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D40: concentric at corner (off-frame)", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    """All rotated 45°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E41: all rotated 45°", case_e41())

def case_e42():
    """1 rotated 30° (others 0)."""
    layers = perfect_design()
    layers[1]["rotation"] = 30
    return H(layers)
add("E42: 1 rotated 30°", case_e42())

def case_e43():
    """All rotated 4° (under tol)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E43: all rotated 4° (under tol)", case_e43())

def case_e44():
    """All flipped horizontally."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: all scaleX=-1", case_e44())

def case_e45():
    """All cornerRadius=50% (rounded)."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = l["w"] / 2
    return H(layers)
add("E45: all 50% cornerRadius (circles)", case_e45())

def case_e46():
    """Outer with cornerRadius."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 100
    return H(layers)
add("E46: outer cornerRadius=100", case_e46())

def case_e47():
    """All have stroke."""
    layers = perfect_design()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E47: all stroked", case_e47())

def case_e48():
    """All have drop shadow."""
    layers = perfect_design()
    for l in layers:
        l["effects"] = [make_drop_shadow()]
    return H(layers)
add("E48: all drop-shadowed", case_e48())

def case_e49():
    """All rotated 90°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E49: all rotated 90°", case_e49())

def case_e50():
    """All rotated 180°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("E50: all rotated 180°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    """Inner is bigger than outer (size order wrong)."""
    cx, cy = 640, 400
    sizes = [200, 300, 100, 400]  # mixed
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F51: sizes shuffled", case_f51())

def case_f52():
    """4 squares but each differently sized rect."""
    cx, cy = 640, 400
    sizes = [(400, 200), (300, 250), (200, 300), (100, 400)]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("F52: rectangle aspect varies", case_f52())

def case_f53():
    """4 perfectly stacked at same position."""
    cx, cy = 640, 400
    layers = [R(cx-100, cy-100, 200, 200, [COLOR_A, COLOR_B][i % 2]) for i in range(4)]
    return H(layers)
add("F53: 4 same size+pos (overlapping pile)", case_f53())

def case_f54():
    """4 nested but ratio inverted (last bigger)."""
    cx, cy = 640, 400
    sizes = [50, 100, 200, 400]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F54: smallest-to-largest order", case_f54())

def case_f55():
    """Sizes 3-2-1 ratio (not nested at all)."""
    cx, cy = 640, 400
    sizes = [300, 290, 280, 270]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F55: barely-decreasing sizes", case_f55())

def case_f56():
    """Each square's inside touches adjacent square."""
    cx, cy = 640, 400
    layers = []
    s = 400
    for i in range(4):
        layers.append(R(cx-s/2 + 10*i, cy-s/2 + 10*i, s-20*i, s-20*i,
                        [COLOR_A, COLOR_B][i % 2]))
    return H(layers)
add("F56: nested with 10px ring spacing", case_f56())

def case_f57():
    """Inner is far smaller than outer (huge gap)."""
    cx, cy = 640, 400
    sizes = [400, 50, 30, 10]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F57: huge size gaps", case_f57())

def case_f58():
    """Perfect (control)."""
    return H()
add("F58: perfect (control)", case_f58())

def case_f59():
    """4 same-color all (no alternation)."""
    cx, cy = 640, 400
    layers = [R(cx-200, cy-200, 400, 400, COLOR_A),
              R(cx-150, cy-150, 300, 300, COLOR_A),
              R(cx-100, cy-100, 200, 200, COLOR_A),
              R(cx-50,  cy-50,  100, 100, COLOR_A)]
    return H(layers)
add("F59: 4 same color (1 distinct)", case_f59())

def case_f60():
    """3-color rotation (not 2-color)."""
    cx, cy = 640, 400
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_C, COLOR_A]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F60: 3 colors (not strict 2)", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Nested frames."""
    inner = make_frame(perfect_design(), w=900, h=700)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """No frame."""
    return H(in_frame=False)
add("G63: no frame", case_g63())

def case_g64():
    """Frame too small."""
    return H(frame_w=300, frame_h=300)
add("G64: frame 300x300 (too small)", case_g64())

def case_g65():
    """Frame has stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G65: frame stroked", case_g65())

def case_g66():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G67: frame image fill", case_g67())

def case_g68():
    """Big frame (2000x2000)."""
    return H(frame_w=2000, frame_h=2000)
add("G68: frame 2000x2000", case_g68())

def case_g69():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_design(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames", case_g69())

def case_g70():
    """Frame at edge of canvas."""
    layers = perfect_design()
    frame = make_frame(layers, x=2000, y=2000, w=1280, h=832)
    return make_log([frame], evt())
add("G70: frame at (2000,2000)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    """No tool change."""
    sem = [make_event("session_start")]
    for _ in range(4): sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H71: no tool_change", case_h71())

def case_h72():
    """Tool=ellipse but rects exist."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(4): sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H72: tool=ellipse but rects", case_h72())

def case_h73():
    """0 create_rectangle events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    return H(evts=sem)
add("H73: 0 create_rectangle events", case_h73())

def case_h74():
    """3 create_rectangle events (not 4)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(3): sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H74: 3 create_rectangle (not 4)", case_h74())

def case_h75():
    """100 undo events."""
    return H(evts=evt(extras=[make_event("undo")]*100))
add("H75: 100 undo events", case_h75())

def case_h76():
    """Used align_layers."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H76: used align_layers", case_h76())

def case_h77():
    """Created and deleted extras."""
    extras = [make_event("create_rectangle"), make_event("delete")] * 3
    return H(evts=evt(extras=extras))
add("H77: 3 create+delete pairs", case_h77())

def case_h78():
    """Many session_end events."""
    return H(evts=evt(extras=[make_event("session_end")]*5))
add("H78: 5x session_end", case_h78())

def case_h79():
    """Created via duplicate (no separate create events but 4 rects)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("duplicate"), make_event("duplicate"), make_event("duplicate")]
    return H(evts=sem)
add("H79: 1 create + 3 duplicate", case_h79())

def case_h80():
    """50 set_fill events."""
    return H(evts=evt(extras=[make_event("set_fill_color")]*50))
add("H80: 50 set_fill events", case_h80())


# ─── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_design()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group in frame", case_i81())

def case_i82():
    """Each in own frame."""
    layers = perfect_design()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I82: each in own frame", case_i82())

def case_i83():
    """In section."""
    layers = perfect_design()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    """1 in frame, 3 on page."""
    layers = perfect_design()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I84: 1 in frame, 3 on page", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    """Page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    p1 = {"id": "p1", "children": [],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    p2 = {"id": "p2", "children": [frame],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I86: design on page 2", case_i86())

def case_i87():
    """In component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1280, "h": 832,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I87: in component (not frame)", case_i87())

def case_i88():
    """3-deep group nesting."""
    layers = perfect_design()
    g3 = {"id":"g3", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id":"g2", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id":"g1", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    frame = make_frame([g1], w=1280, h=832)
    return make_log([frame], evt())
add("I88: 3-deep groups in frame", case_i88())

def case_i89():
    """4 frames, 1 each."""
    layers = perfect_design()
    frames = [make_frame([l], w=600, h=600) for l in layers]
    return make_log(frames, evt())
add("I89: 4 frames split", case_i89())

def case_i90():
    """Empty frame + squares as siblings."""
    layers = perfect_design()
    frame = make_frame([], w=1280, h=832)
    return make_log([frame, *layers], evt())
add("I90: empty frame + sibling squares", case_i90())


# ─── J. Bizarre / hard ──────────────────────────────────────────────
def case_j91():
    """Opacity=0 on all."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("J91: opacity=0 (invisible)", case_j91())

def case_j92():
    """visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J92: visible=False", case_j92())

def case_j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", case_j93())

def case_j94():
    return H([])
add("J94: frame, no squares", case_j94())

def case_j95():
    """Text only."""
    text = make_layer("text", x=400, y=400, w=200, h=40, fill=BLACK)
    text["content"] = "nested"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'nested' only", case_j95())

def case_j96():
    """4 stars."""
    cx, cy = 640, 400
    layers = []
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    for s, c in zip(sizes, colors):
        layers.append(make_layer("star", x=cx-s/2, y=cy-s/2, w=s, h=s,
                                 fill=c, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_star")]*4))
add("J96: 4 stars (not rects)", case_j96())

def case_j97():
    """Negative coords concentric."""
    cx, cy = -200, -200
    sizes = [400, 300, 200, 100]
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [R(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("J97: concentric at negative coords", case_j97())

def case_j98():
    """All scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J98: all mirrored", case_j98())

def case_j99():
    """Outer = entire frame."""
    cx, cy = 640, 400
    layers = [R(0, 0, 1280, 832, COLOR_A),
              R(cx-150, cy-150, 300, 300, COLOR_B),
              R(cx-100, cy-100, 200, 200, COLOR_A),
              R(cx-50,  cy-50,  100, 100, COLOR_B)]
    return H(layers)
add("J99: outer = full frame", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
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

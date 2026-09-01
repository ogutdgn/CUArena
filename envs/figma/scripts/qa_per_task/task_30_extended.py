"""100 edge cases for task 30 (Stripe wallpaper) — runs all and prints a sorted score table.

Spec: 6 vertical stripes alternating deep-blue/cream filling a 600x600 frame.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_30" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
DARK_BLUE = (0.10, 0.20, 0.55)
LIGHT_CREAM = (1.00, 0.95, 0.80)


def evt(rect=6, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    """6 vertical stripes alternating blue/cream filling a 600-wide frame."""
    layers = []
    stripe_w = 100  # 600/6
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * stripe_w, 0, stripe_w, 600, color))
    return layers


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=600, frame_h=600, frame_fill=WHITE, evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# A. Counts
def case_a1():
    """5 stripes."""
    layers = perfect_design()[:5]
    return H(layers, evts=evt(rect=5))
add("A1: 5 stripes", case_a1())


def case_a2():
    """7 stripes."""
    layers = perfect_design()
    layers.append(L("rectangle", 600, 0, 100, 600, DARK_BLUE))
    return H(layers, frame_w=700, evts=evt(rect=7))
add("A2: 7 stripes", case_a2())


def case_a3():
    """3 stripes."""
    layers = []
    for i in range(3):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 200, 0, 200, 600, color))
    return H(layers, evts=evt(rect=3))
add("A3: 3 stripes", case_a3())


def case_a4():
    """0 stripes (empty frame)."""
    return H([], evts=evt(rect=0))
add("A4: 0 stripes (empty)", case_a4())


def case_a5():
    """12 stripes."""
    layers = []
    stripe_w = 50
    for i in range(12):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * stripe_w, 0, stripe_w, 600, color))
    return H(layers, evts=evt(rect=12))
add("A5: 12 stripes (doubled)", case_a5())


def case_a6():
    """6 stripes + extra circle."""
    layers = perfect_design()
    layers.append(L("ellipse", 300, 300, 80, 80, DARK_BLUE))
    return H(layers, evts=evt() + [make_event("create_ellipse")])
add("A6: 6 stripes + ellipse", case_a6())


def case_a7():
    """6 stripes but 1 missing - 5 in place + 1 elsewhere."""
    layers = perfect_design()[:5]
    layers.append(L("rectangle", 200, 700, 100, 600, DARK_BLUE))  # outside frame
    return H(layers, evts=evt())
add("A7: 5 stripes + 1 stray rect", case_a7())


def case_a8():
    """Off-by-one: 6 plus 1 stripe at edge."""
    layers = perfect_design()
    layers.append(L("rectangle", 0, 600, 600, 50, DARK_BLUE))  # extra horizontal stripe
    return H(layers, evts=evt(rect=7))
add("A8: 6 vertical + 1 horizontal", case_a8())


def case_a9():
    """6 polygons instead of rectangles."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("polygon", i * 100, 0, 100, 600, color, sides=4))
    return H(layers, evts=evt(rect=0) + [make_event("create_polygon")]*6)
add("A9: 6 polygons (4-sided)", case_a9())


def case_a10():
    """Perfect (control)."""
    return H()
add("A10: perfect 6 stripes (control)", case_a10())


# B. Colors / fills
def case_b11():
    """Image fills on stripes."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "stripe.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B11: stripes have image fill", case_b11())


def case_b12():
    """Gradient fills on stripes."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B12: stripes gradient fill", case_b12())


def case_b13():
    """All stripes empty fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B13: stripes no fills", case_b13())


def case_b14():
    """Stroke-only stripes."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=DARK_BLUE, weight=2)]
    return H(layers)
add("B14: stripes stroke-only", case_b14())


def case_b15():
    """All stripes same color (no alternating)."""
    layers = []
    for i in range(6):
        layers.append(L("rectangle", i * 100, 0, 100, 600, DARK_BLUE))
    return H(layers)
add("B15: all 6 stripes blue (no alternating)", case_b15())


def case_b16():
    """3 alternating colors (R-G-B-R-G-B)."""
    colors = [(1,0,0), (0,1,0), (0,0,1), (1,0,0), (0,1,0), (0,0,1)]
    layers = []
    for i, c in enumerate(colors):
        layers.append(L("rectangle", i * 100, 0, 100, 600, c))
    return H(layers)
add("B16: 3 alternating colors RGB", case_b16())


def case_b17():
    """Stripes random colors (no pattern)."""
    colors = [(1,0,0), (0,1,0), (1,1,0), (0,0,1), (1,0,1), (0,1,1)]
    layers = []
    for i, c in enumerate(colors):
        layers.append(L("rectangle", i * 100, 0, 100, 600, c))
    return H(layers)
add("B17: 6 random colors (no alternating)", case_b17())


def case_b18():
    """All stripes alpha=0."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: stripes alpha=0", case_b18())


def case_b19():
    """All stripes opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: stripes opacity=0.05", case_b19())


def case_b20():
    """Stacked fills on stripes."""
    layers = perfect_design()
    for l in layers:
        l["fills"].extend([
            {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
            {"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":0,"b":0,"a":1}}], "opacity":0.3, "visible":True}])
    return H(layers)
add("B20: stripes stacked fills", case_b20())


# C. Sizing
def case_c21():
    """Stripes too narrow (10px wide)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 10, 600, color))
    return H(layers)
add("C21: stripes 10px wide (don't fill)", case_c21())


def case_c22():
    """Stripes too short (50 tall)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 200, 100, 50, color))
    return H(layers)
add("C22: stripes 50px tall (not vertical)", case_c22())


def case_c23():
    """Wide stripes (100 wide, but only 100 tall - aspect 1:1)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 250, 100, 100, color))
    return H(layers)
add("C23: stripes 100x100 (square, not vertical)", case_c23())


def case_c24():
    """Different widths: 50, 100, 150, 50, 100, 150."""
    layers = []
    widths = [50, 100, 150, 50, 100, 150]
    x = 0
    for i, w in enumerate(widths):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", x, 0, w, 600, color))
        x += w
    return H(layers)
add("C24: stripes varying widths", case_c24())


def case_c25():
    """All same width (within tol)."""
    layers = []
    widths = [98, 100, 102, 98, 100, 102]
    x = 0
    for i, w in enumerate(widths):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", x, 0, w, 600, color))
        x += w
    return H(layers)
add("C25: stripes 98/100/102 (within tol)", case_c25())


def case_c26():
    """Tiny stripes (1px wide)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 1, 0, 1, 600, color))
    return H(layers)
add("C26: stripes 1px wide (degenerate)", case_c26())


def case_c27():
    """Stripes wider than tall (horizontal aspect)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 0, i * 100, 600, 100, color))
    return H(layers)
add("C27: 6 horizontal stripes (not vertical)", case_c27())


def case_c28():
    """Different heights but consistent widths."""
    layers = []
    heights = [400, 500, 600, 400, 500, 600]
    for i, h in enumerate(heights):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 100, h, color))
    return H(layers)
add("C28: stripes varying heights", case_c28())


def case_c29():
    """6 stripes but partial fill (only fill bottom half)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 300, 100, 300, color))
    return H(layers)
add("C29: stripes only fill bottom half", case_c29())


def case_c30():
    """Stripes wider than 600 (overflow)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 200, 0, 200, 600, color))
    return H(layers)
add("C30: stripes 200x600 (overflow frame)", case_c30())


# D. Position
def case_d31():
    """Stripes with gaps between (gap=20)."""
    layers = []
    stripe_w = 80
    gap = 20
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * (stripe_w + gap), 0, stripe_w, 600, color))
    return H(layers, frame_w=600+5*gap)
add("D31: stripes with 20px gaps", case_d31())


def case_d32():
    """All stripes overlap (stacked at same position)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 0, 0, 600, 600, color))
    return H(layers)
add("D32: 6 stripes piled at same point", case_d32())


def case_d33():
    """Stripes shifted off-frame."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 800 + i * 100, 0, 100, 600, color))
    return H(layers)
add("D33: stripes off-frame (x=800)", case_d33())


def case_d34():
    """Stripes vertically misaligned (different y)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, i * 50, 100, 600, color))
    return H(layers)
add("D34: stripes y-misaligned (stair step)", case_d34())


def case_d35():
    """Stripes have different x's not adjacent."""
    layers = []
    xs = [0, 200, 400, 100, 300, 500]  # non-monotonic
    for i, x in enumerate(xs):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", x, 0, 100, 600, color))
    return H(layers)
add("D35: stripes scrambled x-positions", case_d35())


def case_d36():
    """Stripes with negative coords."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", -300 + i * 100, 0, 100, 600, color))
    return H(layers)
add("D36: stripes at negative x", case_d36())


def case_d37():
    """Stripes diagonal arrangement."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, i * 100, 100, 100, color))
    return H(layers)
add("D37: stripes diagonal layout", case_d37())


def case_d38():
    """Stripes far apart (gap > stripe width)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 300, 0, 100, 600, color))
    return H(layers, frame_w=2000)
add("D38: stripes spaced 300px apart", case_d38())


def case_d39():
    """Stripes squashed: only filling middle of frame."""
    layers = []
    stripe_w = 50
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", 150 + i * stripe_w, 200, stripe_w, 200, color))
    return H(layers)
add("D39: stripes only in middle (50x200 each)", case_d39())


def case_d40():
    """Stripes 8px gap (within tol)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 108, 0, 100, 600, color))
    return H(layers, frame_w=648)
add("D40: stripes with 8px gap (within tol)", case_d40())


# E. Per-shape variants
def case_e41():
    """Stripes rotated 90°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E41: stripes rotated 90°", case_e41())


def case_e42():
    """Stripes rotated 4° (under tol)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E42: stripes rotated 4° (under tol)", case_e42())


def case_e43():
    """Stripes flipped scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E43: stripes scaleX=-1", case_e43())


def case_e44():
    """Stripes have shadows."""
    layers = perfect_design()
    for l in layers:
        l["effects"] = [make_drop_shadow(x=2, y=2)]
    return H(layers)
add("E44: stripes with drop shadows", case_e44())


def case_e45():
    """Stripes have strokes."""
    layers = perfect_design()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E45: stripes with strokes", case_e45())


def case_e46():
    """Stripes have cornerRadius."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 20
    return H(layers)
add("E46: stripes cornerRadius=20", case_e46())


def case_e47():
    """Stripes rotated 45°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E47: stripes rotated 45°", case_e47())


def case_e48():
    """Stripes layer.opacity=0.3."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.3
    return H(layers)
add("E48: stripes opacity=0.3", case_e48())


def case_e49():
    """Stripes mixed rotations: 0, 45, 0, 45, 0, 45."""
    layers = perfect_design()
    for i, l in enumerate(layers):
        if i % 2 == 1:
            l["rotation"] = 45
    return H(layers)
add("E49: mixed rotations", case_e49())


def case_e50():
    """Stripes blur."""
    layers = perfect_design()
    for l in layers:
        l["effects"] = [{"kind": "layer_blur", "radius": 8, "visible": True}]
    return H(layers)
add("E50: stripes blurred", case_e50())


# F. Pattern variants
def case_f51():
    """Pattern reversed: cream-blue-cream-blue."""
    layers = []
    for i in range(6):
        color = LIGHT_CREAM if i % 2 == 0 else DARK_BLUE
        layers.append(L("rectangle", i * 100, 0, 100, 600, color))
    return H(layers)
add("F51: reversed pattern (cream-blue)", case_f51())


def case_f52():
    """All blue then all cream (blocks)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i < 3 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, 100, 600, color))
    return H(layers)
add("F52: 3 blue + 3 cream blocks", case_f52())


def case_f53():
    """Wrong colors (red and green)."""
    layers = []
    for i in range(6):
        color = (1, 0, 0) if i % 2 == 0 else (0, 1, 0)
        layers.append(L("rectangle", i * 100, 0, 100, 600, color))
    return H(layers)
add("F53: red-green stripes (wrong colors)", case_f53())


def case_f54():
    """Slightly off colors (within tol of expected)."""
    layers = []
    for i in range(6):
        if i % 2 == 0:
            color = (0.15, 0.25, 0.50)  # off blue
        else:
            color = (0.95, 0.92, 0.78)  # off cream
        layers.append(L("rectangle", i * 100, 0, 100, 600, color))
    return H(layers)
add("F54: stripes slightly off-color (within tol)", case_f54())


def case_f55():
    """4 colors AABBCCDD pattern."""
    layers = []
    colors = [DARK_BLUE, DARK_BLUE, LIGHT_CREAM, LIGHT_CREAM, RED, RED]
    for i, c in enumerate(colors):
        layers.append(L("rectangle", i * 100, 0, 100, 600, c))
    return H(layers)
add("F55: AA-BB-CC pattern (3 colors x 2)", case_f55())


def case_f56():
    """Same dimensions but 1 stripe is wider."""
    layers = []
    widths = [100, 100, 100, 100, 100, 100]
    widths[3] = 200
    x = 0
    for i, w in enumerate(widths):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", x, 0, w, 600, color))
        x += w
    return H(layers, frame_w=700)
add("F56: 1 wider stripe (200), rest 100", case_f56())


def case_f57():
    """Stripes overlap each other."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 80, 0, 100, 600, color))
    return H(layers, frame_w=520)
add("F57: stripes overlapping (80 step, 100 wide)", case_f57())


def case_f58():
    """Stripes touch but slightly off-aligned y."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, i * 5, 100, 600, color))
    return H(layers)
add("F58: stripes 5px y-offset each (within tol)", case_f58())


def case_f59():
    """6 stripes but some are tiny (1x600)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        w = 1 if i % 2 == 1 else 199  # alternate 199 / 1
        layers.append(L("rectangle", sum(199 if j % 2 == 0 else 1 for j in range(i)), 0, w, 600, color))
    return H(layers)
add("F59: alternating wide/thin stripes", case_f59())


def case_f60():
    """4 stripes at left, 2 at right (gap)."""
    layers = []
    xs = [0, 100, 200, 300, 700, 800]
    for i, x in enumerate(xs):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", x, 0, 100, 600, color))
    return H(layers, frame_w=900)
add("F60: 4 stripes left + 2 stripes right (gap)", case_f60())


# G. Frame variants
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=600, h=600)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers = perfect_design()
    inner = make_frame(layers, w=400, h=400)
    outer = make_frame([inner], w=600, h=600)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """Frame stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=600, h=600)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G63: frame stroke", case_g63())


def case_g64():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=600, h=600, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G64: frame image fill", case_g64())


def case_g65():
    """Frame much smaller."""
    layers = perfect_design()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G65: frame 200x200 (smaller than design)", case_g65())


def case_g66():
    """Frame much larger."""
    layers = perfect_design()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G66: frame 2000x2000 (huge)", case_g66())


def case_g67():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=600, h=600)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())


def case_g68():
    """No frame, stripes on page."""
    return H(in_frame=False)
add("G68: no frame, stripes on page", case_g68())


def case_g69():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=600, h=600)
    f2 = make_frame(perfect_design(), w=600, h=600)
    return make_log([f1, f2], evt())
add("G69: 2 frames, design in 2nd", case_g69())


def case_g70():
    """Frame size 600x800 (taller)."""
    return H(frame_h=800)
add("G70: frame 600x800 (taller)", case_g70())


# H. Tools / events
def case_h71():
    """50 move events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())


def case_h72():
    """50 undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())


def case_h73():
    """No tool changes."""
    sem = [make_event("session_start")]
    for _ in range(6): sem.append(make_event("create_rectangle"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H73: no tool_change", case_h73())


def case_h74():
    """Used pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(6): sem.append(make_event("create_rectangle"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H74: pen tool used", case_h74())


def case_h75():
    """Star tool used (then deleted)."""
    extras = [make_event("tool_change", before="rectangle", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: star tool used then deleted", case_h75())


def case_h76():
    """Many session_end events."""
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: 5 session_end", case_h76())


def case_h77():
    """20 set_fill_color events."""
    return H(evts=evt(set_fill=20))
add("H77: 20 fill events", case_h77())


def case_h78():
    """3 create_rectangle events instead of 6."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(3): sem.append(make_event("create_rectangle"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H78: only 3 create_rectangle", case_h78())


def case_h79():
    """Distribute_layers used."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute used", case_h79())


def case_h80():
    """Align_layers used (Tidy up)."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H80: align used", case_h80())


# I. Hierarchy / structure
def case_i81():
    """Stripes in group inside frame."""
    layers = perfect_design()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=600, h=600)
    return make_log([frame], evt())
add("I81: stripes in group in frame", case_i81())


def case_i82():
    """Stripes split across 2 frames."""
    stripes = perfect_design()
    f1 = make_frame(stripes[:3], w=300, h=600)
    f2 = make_frame(stripes[3:], w=300, h=600)
    return make_log([f1, f2], evt())
add("I82: stripes split across 2 frames", case_i82())


def case_i83():
    """Stripes in section."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 600, "h": 600,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: stripes in section", case_i83())


def case_i84():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=620, h=620)
    f1 = make_frame([f2], w=640, h=640)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())


def case_i85():
    """Stripes on page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=600, h=600)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: stripes on page 2", case_i85())


def case_i86():
    """Stripes in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 600, "h": 600, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: stripes in component", case_i86())


def case_i87():
    """5 stripes in frame, 1 on page."""
    stripes = perfect_design()
    frame = make_frame(stripes[:5], w=600, h=600)
    return make_log([frame, stripes[5]], evt())
add("I87: 5 stripes in frame, 1 on page", case_i87())


def case_i88():
    """6 frames each with 1 stripe."""
    stripes = perfect_design()
    frames = [make_frame([s], w=100, h=600) for s in stripes]
    return make_log(frames, evt())
add("I88: 6 stripes each in own frame", case_i88())


# J. Bizarre
def case_j89():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())


def case_j90():
    """Frame only."""
    return H([])
add("J90: frame only", case_j90())


def case_j91():
    """Text 'stripes'."""
    text = make_layer("text", x=200, y=300, w=200, h=50, fill=DARK_BLUE)
    text["content"] = "stripes"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'stripes'", case_j91())


def case_j92():
    """1 wide stripe colored as a gradient (single rect)."""
    rect = L("rectangle", 0, 0, 600, 600, fill=None)
    rect["fills"] = [{"kind": "gradient", "stops":[
        {"position":0,"color":{"r":0.1,"g":0.2,"b":0.55,"a":1}},
        {"position":1,"color":{"r":1,"g":0.95,"b":0.8,"a":1}}], "opacity":1, "visible":True}]
    return H([rect], evts=evt(rect=1))
add("J92: 1 gradient rect (no stripes)", case_j92())


def case_j93():
    """6 stripes but as polygons (4-sided)."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("polygon", i * 100, 0, 100, 600, color, sides=4))
    return H(layers, evts=evt(rect=0) + [make_event("create_polygon")]*6)
add("J93: 6 polygons (4-sided) stripes", case_j93())


def case_j94():
    """Layer opacity=0 on all."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("J94: stripes opacity=0", case_j94())


def case_j95():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J95: stripes visible=False", case_j95())


def case_j96():
    """Stripes mirrored scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J96: stripes scaleX=-1", case_j96())


def case_j97():
    """Negative w."""
    layers = []
    for i in range(6):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 100, 0, -100, 600, color))
    return H(layers)
add("J97: negative w stripes", case_j97())


def case_j98():
    """Stripe at every position (16 total)."""
    layers = []
    for i in range(16):
        color = DARK_BLUE if i % 2 == 0 else LIGHT_CREAM
        layers.append(L("rectangle", i * 50, 0, 50, 600, color))
    return H(layers, frame_w=800, evts=evt(rect=16))
add("J98: 16 thin stripes", case_j98())


def case_j99():
    """Stripes color = same as frame fill."""
    layers = []
    for i in range(6):
        color = WHITE if i % 2 == 0 else WHITE  # all white
        layers.append(L("rectangle", i * 100, 0, 100, 600, color))
    return H(layers)
add("J99: all white stripes (camouflaged)", case_j99())


def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect 6 stripes (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

"""100 edge cases for task 28 (Edited photo X-cross) — runs all and prints a sorted score table.

Spec: Large rectangle (placeholder) + 2 diagonal lines crossing through it (X-shape).
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_28" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(rect=1, line=2, set_fill=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    sem.append(make_event("tool_change", before="rectangle", after="line"))
    for _ in range(line):     sem.append(make_event("create_line"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def make_line(x, y, w, h, p1, p2, fill=BLACK, **extra):
    """Create a line with p1, p2 in local coords."""
    line = make_layer("line", x=x, y=y, w=w, h=h, fill=None, **extra)
    line["fills"] = []
    line["strokes"] = [make_stroke(rgb=fill, weight=2)]
    line["p1"] = {"x": p1[0], "y": p1[1]}
    line["p2"] = {"x": p2[0], "y": p2[1]}
    return line


def perfect_design():
    """1 placeholder rect + 2 X-cross lines."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))    # TL→BR
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))    # TR→BL
    return [rect, line1, line2]


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95), evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# A. Counts
def case_a1():
    """3 rectangles."""
    layers = perfect_design()
    layers.append(L("rectangle", 100, 100, 80, 80, BLUE))
    layers.append(L("rectangle", 1000, 100, 80, 80, RED))
    return H(layers, evts=evt(rect=3))
add("A1: 3 rectangles", case_a1())


def case_a2():
    """0 rectangles."""
    layers = [
        make_line(400, 200, 480, 320, (0, 0), (480, 320)),
        make_line(400, 200, 480, 320, (480, 0), (0, 320)),
    ]
    return H(layers, evts=evt(rect=0))
add("A2: 0 rectangles, 2 lines floating", case_a2())


def case_a3():
    """3 lines (one extra)."""
    layers = perfect_design()
    layers.append(make_line(400, 250, 480, 0, (0, 0), (480, 0)))
    return H(layers, evts=evt(line=3))
add("A3: 3 lines (one extra)", case_a3())


def case_a4():
    """1 line only."""
    layers = perfect_design()[:2]
    return H(layers, evts=evt(line=1))
add("A4: only 1 diagonal line", case_a4())


def case_a5():
    """0 lines."""
    return H([perfect_design()[0]], evts=evt(line=0))
add("A5: rectangle, no lines", case_a5())


def case_a6():
    """4 lines (X plus + sign)."""
    layers = perfect_design()
    layers.append(make_line(400, 360, 480, 0, (0, 0), (480, 0)))    # horizontal
    layers.append(make_line(640, 200, 0, 320, (0, 0), (0, 320)))    # vertical
    return H(layers, evts=evt(line=4))
add("A6: X + plus = 4 lines", case_a6())


def case_a7():
    """2 rectangles same color, 2 lines."""
    layers = perfect_design()
    layers.insert(1, L("rectangle", 100, 100, 100, 100, LIGHT_GRAY))
    return H(layers, evts=evt(rect=2))
add("A7: 2 rectangles same color", case_a7())


def case_a8():
    """1 rect, 2 lines, plus 1 ellipse."""
    layers = perfect_design()
    layers.append(L("ellipse", 100, 600, 80, 80, LIGHT_GRAY))
    return H(layers, evts=evt() + [make_event("create_ellipse")])
add("A8: design + extra ellipse", case_a8())


def case_a9():
    """5 lines, no rect."""
    layers = []
    for i in range(5):
        layers.append(make_line(400 + i*10, 200 + i*10, 100, 100, (0, 0), (100, 100)))
    return H(layers, evts=evt(rect=0, line=5))
add("A9: 5 lines, no rect", case_a9())


def case_a10():
    """Perfect (control)."""
    return H()
add("A10: perfect design (control)", case_a10())


# B. Colors / fills
def case_b11():
    """Rectangle has image fill."""
    rect = L("rectangle", 400, 200, 480, 320, fill=None)
    rect["fills"] = [{"kind": "image", "src": "photo.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    layers = [rect, perfect_design()[1], perfect_design()[2]]
    return H(layers)
add("B11: rect has image fill (not solid)", case_b11())


def case_b12():
    """Rectangle has gradient fill."""
    rect = L("rectangle", 400, 200, 480, 320, fill=None)
    rect["fills"] = [{"kind": "gradient", "stops":[
        {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    layers = [rect, perfect_design()[1], perfect_design()[2]]
    return H(layers)
add("B12: rect has gradient fill", case_b12())


def case_b13():
    """Rectangle has empty fills."""
    rect = L("rectangle", 400, 200, 480, 320, fill=None)
    rect["fills"] = []
    layers = [rect, perfect_design()[1], perfect_design()[2]]
    return H(layers)
add("B13: rect has empty fills", case_b13())


def case_b14():
    """Rectangle stroke-only no fill."""
    rect = L("rectangle", 400, 200, 480, 320, fill=None,
             strokes=[make_stroke(rgb=BLACK, weight=4)])
    layers = [rect, perfect_design()[1], perfect_design()[2]]
    return H(layers)
add("B14: rect stroke-only", case_b14())


def case_b15():
    """Lines + rect all white (invisible against white frame)."""
    rect = L("rectangle", 400, 200, 480, 320, WHITE)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320), fill=WHITE)
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320), fill=WHITE)
    return H([rect, line1, line2], frame_fill=WHITE)
add("B15: all white (no contrast)", case_b15())


def case_b16():
    """Rectangle near-tolerance off-color."""
    rect = L("rectangle", 400, 200, 480, 320, (0.6, 0.7, 0.4))
    layers = [rect, perfect_design()[1], perfect_design()[2]]
    return H(layers)
add("B16: rect olive color (any solid passes)", case_b16())


def case_b17():
    """Lines have 0-alpha strokes (invisible)."""
    rect = perfect_design()[0]
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line1["strokes"] = [{"paint":{"kind":"solid","color":{"r":0,"g":0,"b":0,"a":0}},"weight":2,"alignment":"center","dash":None,"visible":True}]
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    line2["strokes"] = [{"paint":{"kind":"solid","color":{"r":0,"g":0,"b":0,"a":0}},"weight":2,"alignment":"center","dash":None,"visible":True}]
    return H([rect, line1, line2])
add("B17: lines have alpha=0 strokes", case_b17())


def case_b18():
    """Rect fill alpha=0."""
    rect = perfect_design()[0]
    rect["fills"][0]["color"]["a"] = 0.0
    return H([rect, perfect_design()[1], perfect_design()[2]])
add("B18: rect fill alpha=0", case_b18())


def case_b19():
    """Rect fill opacity=0.05."""
    rect = perfect_design()[0]
    rect["fills"][0]["opacity"] = 0.05
    return H([rect, perfect_design()[1], perfect_design()[2]])
add("B19: rect fill opacity=0.05", case_b19())


def case_b20():
    """Rect has stacked fills."""
    rect = perfect_design()[0]
    rect["fills"].extend([
        {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
        {"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":0,"b":0,"a":1}}], "opacity":0.3, "visible":True}])
    return H([rect, perfect_design()[1], perfect_design()[2]])
add("B20: rect has stacked fills", case_b20())


# C. Sizing
def case_c21():
    """Rectangle tiny 20x20."""
    rect = L("rectangle", 400, 200, 20, 20, LIGHT_GRAY)
    line1 = make_line(400, 200, 20, 20, (0, 0), (20, 20))
    line2 = make_line(400, 200, 20, 20, (20, 0), (0, 20))
    return H([rect, line1, line2])
add("C21: tiny 20x20 rect with 20-px lines", case_c21())


def case_c22():
    """Rectangle huge 1100x700."""
    rect = L("rectangle", 50, 50, 1100, 700, LIGHT_GRAY)
    line1 = make_line(50, 50, 1100, 700, (0, 0), (1100, 700))
    line2 = make_line(50, 50, 1100, 700, (1100, 0), (0, 700))
    return H([rect, line1, line2])
add("C22: huge 1100x700 rect", case_c22())


def case_c23():
    """Skinny 40x500."""
    rect = L("rectangle", 600, 200, 40, 500, LIGHT_GRAY)
    line1 = make_line(600, 200, 40, 500, (0, 0), (40, 500))
    line2 = make_line(600, 200, 40, 500, (40, 0), (0, 500))
    return H([rect, line1, line2])
add("C23: skinny 40x500", case_c23())


def case_c24():
    """Wide 800x40."""
    rect = L("rectangle", 200, 400, 800, 40, LIGHT_GRAY)
    line1 = make_line(200, 400, 800, 40, (0, 0), (800, 40))
    line2 = make_line(200, 400, 800, 40, (800, 0), (0, 40))
    return H([rect, line1, line2])
add("C24: wide 800x40", case_c24())


def case_c25():
    """1x1 degenerate rect."""
    rect = L("rectangle", 600, 400, 1, 1, LIGHT_GRAY)
    line1 = make_line(600, 400, 1, 1, (0, 0), (1, 1))
    line2 = make_line(600, 400, 1, 1, (1, 0), (0, 1))
    return H([rect, line1, line2])
add("C25: 1x1 degenerate rect", case_c25())


def case_c26():
    """Lines wrong length: lines don't span rect."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    # lines that span only half the rect
    line1 = make_line(400, 200, 240, 160, (0, 0), (240, 160))
    line2 = make_line(640, 200, 240, 160, (0, 0), (0, 0))
    return H([rect, line1, line2])
add("C26: lines too short for rect", case_c26())


def case_c27():
    """Lines way longer than rect."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(0, 0, 1280, 832, (0, 0), (1280, 832))
    line2 = make_line(0, 0, 1280, 832, (1280, 0), (0, 832))
    return H([rect, line1, line2])
add("C27: lines span entire frame", case_c27())


def case_c28():
    """Lines drawn outside the rect."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(0, 600, 200, 200, (0, 0), (200, 200))
    line2 = make_line(900, 100, 200, 200, (0, 0), (0, 0))
    return H([rect, line1, line2])
add("C28: lines outside rect bounds", case_c28())


def case_c29():
    """Rect just at 100x100, lines at corners."""
    rect = L("rectangle", 600, 400, 100, 100, LIGHT_GRAY)
    line1 = make_line(600, 400, 100, 100, (0, 0), (100, 100))
    line2 = make_line(600, 400, 100, 100, (100, 0), (0, 100))
    return H([rect, line1, line2])
add("C29: 100x100 rect (small)", case_c29())


def case_c30():
    """Lines as single point (degenerate)."""
    rect = perfect_design()[0]
    line1 = make_line(400, 200, 0, 0, (0, 0), (0, 0))
    line2 = make_line(880, 520, 0, 0, (0, 0), (0, 0))
    return H([rect, line1, line2])
add("C30: lines are points (zero-length)", case_c30())


# D. Position
def case_d31():
    """Rect at frame edge."""
    rect = L("rectangle", 0, 0, 400, 300, LIGHT_GRAY)
    line1 = make_line(0, 0, 400, 300, (0, 0), (400, 300))
    line2 = make_line(0, 0, 400, 300, (400, 0), (0, 300))
    return H([rect, line1, line2])
add("D31: rect at top-left corner", case_d31())


def case_d32():
    """Rect off-frame to the right."""
    rect = L("rectangle", 1500, 200, 400, 300, LIGHT_GRAY)
    line1 = make_line(1500, 200, 400, 300, (0, 0), (400, 300))
    line2 = make_line(1500, 200, 400, 300, (400, 0), (0, 300))
    return H([rect, line1, line2])
add("D32: rect off-frame right", case_d32())


def case_d33():
    """Negative coords."""
    rect = L("rectangle", -200, -200, 400, 300, LIGHT_GRAY)
    line1 = make_line(-200, -200, 400, 300, (0, 0), (400, 300))
    line2 = make_line(-200, -200, 400, 300, (400, 0), (0, 300))
    return H([rect, line1, line2])
add("D33: negative coords", case_d33())


def case_d34():
    """Lines at wrong position (away from rect)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(0, 600, 200, 200, (0, 0), (200, 200))
    line2 = make_line(900, 100, 200, 200, (0, 0), (200, 200))
    return H([rect, line1, line2])
add("D34: lines disconnected from rect", case_d34())


def case_d35():
    """Lines cross at rect center but don't reach corners."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(520, 280, 240, 160, (0, 0), (240, 160))
    line2 = make_line(520, 280, 240, 160, (240, 0), (0, 160))
    return H([rect, line1, line2])
add("D35: lines half-length crossing in center", case_d35())


def case_d36():
    """Lines parallel (no X)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 250, 480, 320, (0, 0), (480, 320))  # parallel
    return H([rect, line1, line2])
add("D36: 2 parallel diagonal lines", case_d36())


def case_d37():
    """2 horizontal lines through middle."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 320, 480, 0, (0, 0), (480, 0))
    line2 = make_line(400, 400, 480, 0, (0, 0), (480, 0))
    return H([rect, line1, line2])
add("D37: 2 horizontal lines (parallel)", case_d37())


def case_d38():
    """One horizontal one vertical (+ sign, not X)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 360, 480, 0, (0, 0), (480, 0))
    line2 = make_line(640, 200, 0, 320, (0, 0), (0, 320))
    return H([rect, line1, line2])
add("D38: + cross instead of X", case_d38())


def case_d39():
    """Slightly off corners (within tol)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (5, 5), (475, 315))
    line2 = make_line(400, 200, 480, 320, (475, 5), (5, 315))
    return H([rect, line1, line2])
add("D39: lines slightly inside corners (within 12px tol)", case_d39())


def case_d40():
    """Lines off corners by 30px (over tol)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (30, 30), (450, 290))
    line2 = make_line(400, 200, 480, 320, (450, 30), (30, 290))
    return H([rect, line1, line2])
add("D40: lines off corners by 30px (over tol)", case_d40())


# E. Per-shape variants (rotations)
def case_e41():
    """Rect rotated 45°."""
    layers = perfect_design()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: rect rotated 45°", case_e41())


def case_e42():
    """Rect rotated 4° (under tol)."""
    layers = perfect_design()
    layers[0]["rotation"] = 4
    return H(layers)
add("E42: rect rotated 4° (under tol)", case_e42())


def case_e43():
    """Rect rotated 90°."""
    layers = perfect_design()
    layers[0]["rotation"] = 90
    return H(layers)
add("E43: rect rotated 90°", case_e43())


def case_e44():
    """Rect flipped horizontally."""
    layers = perfect_design()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: rect scaleX=-1", case_e44())


def case_e45():
    """Rect with corner radius (rounded photo)."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 24
    return H(layers)
add("E45: rect with cornerRadius=24", case_e45())


def case_e46():
    """Lines rotated."""
    layers = perfect_design()
    layers[1]["rotation"] = 45
    layers[2]["rotation"] = 45
    return H(layers)
add("E46: lines rotated 45°", case_e46())


def case_e47():
    """Lines flipped."""
    layers = perfect_design()
    layers[1]["scaleY"] = -1
    layers[2]["scaleY"] = -1
    return H(layers)
add("E47: lines flipped V", case_e47())


def case_e48():
    """Rect with cornerRadius=200 (full circle)."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 200
    return H(layers)
add("E48: rect cornerRadius=200 (huge)", case_e48())


def case_e49():
    """Lines with thick strokes."""
    layers = perfect_design()
    layers[1]["strokes"][0]["weight"] = 30
    layers[2]["strokes"][0]["weight"] = 30
    return H(layers)
add("E49: lines weight=30 (very thick)", case_e49())


def case_e50():
    """Lines with dashed strokes."""
    layers = perfect_design()
    layers[1]["strokes"][0]["dash"] = {"dash": 6, "gap": 4}
    layers[2]["strokes"][0]["dash"] = {"dash": 6, "gap": 4}
    return H(layers)
add("E50: lines dashed", case_e50())


# F. Subcomponent variants
def case_f51():
    """Lines very different sizes."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 100, 100, (0, 0), (100, 100))   # short
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))   # full
    return H([rect, line1, line2])
add("F51: lines different sizes", case_f51())


def case_f52():
    """Lines stacked exactly on top of each other."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    return H([rect, line1, line2])
add("F52: 2 identical (stacked) diagonals", case_f52())


def case_f53():
    """Lines but not corner to corner (touching middle of edges)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (240, 0), (240, 320))   # vertical center
    line2 = make_line(400, 200, 480, 320, (0, 160), (480, 160))   # horizontal center
    return H([rect, line1, line2])
add("F53: lines through edge midpoints (+ sign)", case_f53())


def case_f54():
    """Both lines TL→BR (no opposing diagonal)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (5, 5), (475, 315))
    return H([rect, line1, line2])
add("F54: both lines TL→BR (no X)", case_f54())


def case_f55():
    """Lines connect to wrong corners — just one corner each."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (240, 160))
    line2 = make_line(400, 200, 480, 320, (480, 0), (240, 160))
    return H([rect, line1, line2])
add("F55: lines from corners to center", case_f55())


def case_f56():
    """Lines drawn but outside frame."""
    rect = perfect_design()[0]
    line1 = make_line(2000, 2000, 480, 320, (0, 0), (480, 320))
    line2 = make_line(2000, 2000, 480, 320, (480, 0), (0, 320))
    return H([rect, line1, line2])
add("F56: lines outside frame", case_f56())


def case_f57():
    """Lines with empty p1/p2."""
    rect = perfect_design()[0]
    line1 = make_layer("line", x=400, y=200, w=480, h=320, fill=None, strokes=[make_stroke()])
    line2 = make_layer("line", x=400, y=200, w=480, h=320, fill=None, strokes=[make_stroke()])
    return H([rect, line1, line2])
add("F57: lines with no p1/p2", case_f57())


def case_f58():
    """Lines with mismatched x,y vs rect."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(0, 0, 480, 320, (0, 0), (480, 320))      # at origin instead of rect's
    line2 = make_line(0, 0, 480, 320, (480, 0), (0, 320))
    return H([rect, line1, line2])
add("F58: lines at (0,0) origin, not rect", case_f58())


def case_f59():
    """Lines on different rect (frame's bounds)."""
    rect = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(0, 0, 1280, 832, (0, 0), (1280, 832))
    line2 = make_line(0, 0, 1280, 832, (1280, 0), (0, 832))
    return H([rect, line1, line2])
add("F59: X across frame, not rect", case_f59())


def case_f60():
    """Lines with no strokes (invisible)."""
    rect = perfect_design()[0]
    line1 = make_layer("line", x=400, y=200, w=480, h=320, fill=None, strokes=[])
    line1["p1"] = {"x": 0, "y": 0}; line1["p2"] = {"x": 480, "y": 320}
    line2 = make_layer("line", x=400, y=200, w=480, h=320, fill=None, strokes=[])
    line2["p1"] = {"x": 480, "y": 0}; line2["p2"] = {"x": 0, "y": 320}
    return H([rect, line1, line2])
add("F60: lines with empty strokes", case_f60())


# G. Frame variants
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers = perfect_design()
    inner = make_frame(layers, w=1000, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_design(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, design in 2nd", case_g63())


def case_g64():
    """Frame with stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())


def case_g65():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())


def case_g66():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())


def case_g67():
    """Frame much smaller."""
    layers = perfect_design()
    frame = make_frame(layers, w=200, h=150)
    return make_log([frame], evt())
add("G67: frame 200x150 (smaller than design)", case_g67())


def case_g68():
    """No frame, design on page."""
    return H(in_frame=False)
add("G68: no frame, design on page", case_g68())


def case_g69():
    """Frame with gradient fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":1,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G69: frame has gradient fill", case_g69())


def case_g70():
    """Frame with image fill at 0 alpha."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=(1, 1, 1))
    return make_log([frame], evt())
add("G70: frame default white fill (perfect)", case_g70())


# H. Tools / events
def case_h71():
    """Many move events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())


def case_h72():
    """Many undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())


def case_h73():
    """No tool changes."""
    sem = [make_event("session_start"),
           make_event("create_rectangle"),
           make_event("create_line"),
           make_event("create_line"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H73: no tool_change events", case_h73())


def case_h74():
    """Wrong tool used: pen instead of line."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("create_line"), make_event("create_line"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H74: pen tool used instead of line", case_h74())


def case_h75():
    """Star tool used (then deleted)."""
    extras = [make_event("tool_change", before="line", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: star tool used then deleted", case_h75())


def case_h76():
    """Many session_end events."""
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H76: many session_end events", case_h76())


def case_h77():
    """20 set_fill_color events."""
    return H(evts=evt(set_fill=20))
add("H77: 20 set_fill_color events", case_h77())


def case_h78():
    """Wrong line count: only 1 create_line."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="line"),
           make_event("create_line"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H78: only 1 create_line in events", case_h78())


def case_h79():
    """3 create_rectangle events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("create_rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="line"),
           make_event("create_line"), make_event("create_line"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H79: 3 create_rectangle events (extra)", case_h79())


def case_h80():
    """Distribute_layers used."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: 1 distribute event", case_h80())


# I. Hierarchy / structure
def case_i81():
    """Design in group inside frame."""
    layers = perfect_design()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: design in group in frame", case_i81())


def case_i82():
    """Design split across 2 frames."""
    rect = perfect_design()[0]
    lines = perfect_design()[1:]
    f1 = make_frame([rect], w=640, h=832)
    f2 = make_frame(lines, w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: rect and lines in different frames", case_i82())


def case_i83():
    """Design in section."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: design in section", case_i83())


def case_i84():
    """Design on page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I84: design on page 2", case_i84())


def case_i85():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    """Design in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: design in component", case_i86())


def case_i87():
    """Lines on page, rect in frame."""
    rect = perfect_design()[0]
    lines = perfect_design()[1:]
    f1 = make_frame([rect], w=1280, h=832)
    return make_log([f1, *lines], evt())
add("I87: rect in frame, lines on page", case_i87())


def case_i88():
    """Multiple frames each containing a rect."""
    rect1 = L("rectangle", 200, 200, 200, 200, LIGHT_GRAY)
    rect2 = L("rectangle", 400, 200, 480, 320, LIGHT_GRAY)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    f1 = make_frame([rect1], w=640, h=832)
    f2 = make_frame([rect2, line1, line2], w=640, h=832)
    return make_log([f1, f2], evt(rect=2))
add("I88: 2 rects in 2 frames", case_i88())


# J. Bizarre
def case_j89():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())


def case_j90():
    """Frame only."""
    return H([])
add("J90: frame only, no shapes", case_j90())


def case_j91():
    """Text 'X' (looks like X)."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "XXX"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'XXX' on page", case_j91())


def case_j92():
    """Rect rotated 180°."""
    layers = perfect_design()
    layers[0]["rotation"] = 180
    return H(layers)
add("J92: rect rotated 180°", case_j92())


def case_j93():
    """Lines on diagonals but rect is missing."""
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([line1, line2], evts=evt(rect=0))
add("J93: lines only, no rect", case_j93())


def case_j94():
    """Polygon (triangle) instead of rectangle."""
    poly = make_layer("polygon", x=400, y=200, w=480, h=320, fill=LIGHT_GRAY, sides=3)
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([poly, line1, line2], evts=evt(rect=0) + [make_event("create_polygon")])
add("J94: polygon instead of rect", case_j94())


def case_j95():
    """Layer-level opacity=0 on rect."""
    layers = perfect_design()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("J95: rect opacity=0", case_j95())


def case_j96():
    """Visible=False on rect."""
    layers = perfect_design()
    layers[0]["visible"] = False
    return H(layers)
add("J96: rect visible=False", case_j96())


def case_j97():
    """Rect = full frame."""
    rect = L("rectangle", 0, 0, 1280, 832, LIGHT_GRAY)
    line1 = make_line(0, 0, 1280, 832, (0, 0), (1280, 832))
    line2 = make_line(0, 0, 1280, 832, (1280, 0), (0, 832))
    return H([rect, line1, line2])
add("J97: rect = full frame", case_j97())


def case_j98():
    """Lines flipped (with scaleY=-1)."""
    layers = perfect_design()
    layers[1]["scaleY"] = -1
    layers[2]["scaleX"] = -1
    return H(layers)
add("J98: lines mirrored", case_j98())


def case_j99():
    """Rect color matches frame fill (camouflaged)."""
    rect = L("rectangle", 400, 200, 480, 320, (0.95, 0.95, 0.95))
    line1 = make_line(400, 200, 480, 320, (0, 0), (480, 320))
    line2 = make_line(400, 200, 480, 320, (480, 0), (0, 320))
    return H([rect, line1, line2])
add("J99: rect matches frame fill", case_j99())


def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect design (control)", case_j100())


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

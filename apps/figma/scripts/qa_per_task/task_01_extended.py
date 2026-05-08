"""96 edge cases for task 01 — runs all and prints a sorted score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_01" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
# ─── Helpers ────────────────────────────────────────────────────────
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(rect=2, ellipse=2, polygon=1, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_house():
    body = L("rectangle", 440, 300, 400, 400, PINK)
    door = L("rectangle", 600, 560, 80, 140, ORANGE)
    win_l = L("ellipse", 500, 400, 60, 60, WHITE)
    win_r = L("ellipse", 720, 400, 60, 60, YELLOW)
    roof = L("polygon", 400, 180, 480, 120, NAVY, sides=3)
    return [body, door, win_l, win_r, roof]


# ─── Case factories ─────────────────────────────────────────────────
CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95), evts=None, in_frame=True):
    """Wrap layers in a 1280×832 frame (or page directly) and a default event log."""
    if layers is None: layers = perfect_house()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    else:
        return make_log(layers, evts or evt())


# A. Count permutations
def case_a1():
    layers = perfect_house()
    layers.append(L("ellipse", 800, 400, 60, 60, GREEN))  # 3rd window
    return H(layers, evts=evt(ellipse=3))
add("A1: 3 windows (extra ellipse)", case_a1())

def case_a2():
    layers = [L("rectangle", 440, 300, 400, 400, PINK),
              L("rectangle", 600, 560, 80, 140, ORANGE),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers, evts=evt(ellipse=0))
add("A2: 0 windows", case_a2())

def case_a3():
    layers = perfect_house()
    layers.insert(2, L("rectangle", 480, 600, 60, 100, PURPLE))  # 2nd door
    return H(layers, evts=evt(rect=3))
add("A3: 2 doors", case_a3())

def case_a4():
    layers = [L("rectangle", 440, 300, 400, 400, PINK),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers, evts=evt(rect=1))
add("A4: 0 doors", case_a4())

def case_a5():
    layers = perfect_house()
    layers.append(L("polygon", 410, 180, 460, 120, GREEN, sides=3))  # 2nd roof
    return H(layers, evts=evt(polygon=2))
add("A5: 2 roofs stacked", case_a5())

def case_a6():
    layers = [L("rectangle", 440, 300, 400, 400, PINK),
              L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW)]
    return H(layers, evts=evt(polygon=0))
add("A6: 0 roofs", case_a6())

def case_a7():
    body = L("rectangle", 440, 300, 400, 400, PINK)
    door = L("rectangle", 600, 560, 80, 140, ORANGE)
    roof = L("polygon", 400, 180, 480, 120, NAVY, sides=3)
    wins = [L("ellipse", 460+i*80, 400, 50, 50, [WHITE,YELLOW,GREEN,CYAN,RED][i]) for i in range(5)]
    return H([body, door, *wins, roof], evts=evt(ellipse=5))
add("A7: 5 windows along body", case_a7())

def case_a8():
    return H([L("rectangle", 440, 300, 400, 400, PINK),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)],
             evts=evt(rect=1, ellipse=0))
add("A8: body+roof only (no door, no windows)", case_a8())

def case_a9():
    layers = perfect_house()
    for i in range(5):
        layers.append(L("ellipse", 100+i*80, 720, 30, 30, [GOLD,GREEN,CYAN,PURPLE,ORANGE][i]))
    return H(layers, evts=evt(ellipse=7))
add("A9: house + 5 decorative ellipses", case_a9())

def case_a10():
    return H([L("rectangle", 440, 300, 400, 400, PINK)],
             evts=evt(rect=1, ellipse=0, polygon=0))
add("A10: just a body rectangle", case_a10())

# B. Colors
def case_b11():
    layers = [L("rectangle", 440, 300, 400, 400, BLUE),
              L("rectangle", 600, 560, 80, 140, BLUE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, BLUE, sides=3)]
    return H(layers)
add("B11: body+door+roof same blue, windows distinct (3 distinct)", case_b11())

def case_b12():
    return H()  # default perfect with 4 distinct = pass
add("B12: 4 distinct fills (perfect)", case_b12())

def case_b13():
    body = L("rectangle", 440, 300, 400, 400, fill=None)
    body["fills"] = [{"kind": "image", "src": "house.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    layers = [body, L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers)
add("B13: body has image fill (not solid)", case_b13())

def case_b14():
    body = L("rectangle", 440, 300, 400, 400, fill=None,
             strokes=[make_stroke(rgb=PINK, weight=4)])
    layers = [body, L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers)
add("B14: body stroke only, no fill", case_b14())

def case_b15():
    body = L("rectangle", 440, 300, 400, 400, fill=None)
    body["fills"] = []
    layers = [body, L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers)
add("B15: body fills array empty", case_b15())

def case_b16():
    layers = [L("rectangle", 440, 300, 400, 400, WHITE),
              L("rectangle", 600, 560, 80, 140, WHITE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, WHITE),
              L("polygon", 400, 180, 480, 120, WHITE, sides=3)]
    return H(layers, frame_fill=WHITE)
add("B16: all white (no contrast)", case_b16())

def case_b17():
    base = (0.5, 0.5, 0.5)
    layers = [L("rectangle", 440, 300, 400, 400, (0.50, 0.50, 0.50)),
              L("rectangle", 600, 560, 80, 140, (0.51, 0.51, 0.51)),
              L("ellipse", 500, 400, 60, 60, (0.52, 0.50, 0.50)),
              L("ellipse", 720, 400, 60, 60, (0.50, 0.52, 0.50)),
              L("polygon", 400, 180, 480, 120, (0.50, 0.50, 0.52), sides=3)]
    return H(layers)
add("B17: all near-gray (within color tolerance)", case_b17())

def case_b18():
    body = L("rectangle", 440, 300, 400, 400, fill=None)
    body["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":0,"b":0,"a":1}},
        {"position": 1, "color": {"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    layers = [body, L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers)
add("B18: body has gradient (not solid)", case_b18())

def case_b19():
    layers = perfect_house()
    layers[4]["fills"][0]["opacity"] = 0.1  # roof super transparent
    return H(layers)
add("B19: roof transparent (fillOpacity=0.1)", case_b19())

def case_b20():
    body = L("rectangle", 440, 300, 400, 400, PINK)
    body["fills"].extend([
        {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
        {"kind": "solid", "color": {"r":0,"g":0,"b":0,"a":1}, "opacity":0.3, "visible":True}])
    layers = [body, L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 500, 400, 60, 60, WHITE),
              L("ellipse", 720, 400, 60, 60, YELLOW),
              L("polygon", 400, 180, 480, 120, NAVY, sides=3)]
    return H(layers)
add("B20: body has 3 stacked fills (first solid)", case_b20())

# C. Sizing
def case_c21():
    layers = [L("rectangle", 0, 0, 1500, 1000, PINK),
              L("rectangle", 700, 800, 80, 140, ORANGE),
              L("ellipse", 600, 600, 60, 60, WHITE),
              L("ellipse", 820, 600, 60, 60, YELLOW),
              L("polygon", 0, -100, 1500, 200, NAVY, sides=3)]
    return H(layers)
add("C21: body too big (overflows frame)", case_c21())

def case_c22():
    layers = [L("rectangle", 340, 300, 600, 400, PINK),
              L("rectangle", 600, 560, 80, 140, ORANGE),
              L("ellipse", 480, 400, 60, 60, WHITE),
              L("ellipse", 800, 400, 60, 60, YELLOW),
              L("polygon", 300, 180, 680, 120, NAVY, sides=3)]
    return H(layers)
add("C22: body 50% of frame width", case_c22())

def case_c23():
    layers = perfect_house()
    layers[1] = L("rectangle", 340, 200, 600, 600, ORANGE)  # door bigger than body
    return H(layers)
add("C23: door bigger than body", case_c23())

def case_c24():
    layers = perfect_house()
    layers[2] = L("ellipse", 200, 200, 700, 700, WHITE)
    layers[3] = L("ellipse", 500, 500, 700, 700, YELLOW)
    return H(layers, evts=evt())
add("C24: windows bigger than body", case_c24())

def case_c25():
    layers = perfect_house()
    layers[0] = L("rectangle", 600, 100, 10, 800, PINK)  # 10×800 body
    return H(layers)
add("C25: body 10×800 skinny vertical", case_c25())

def case_c26():
    layers = perfect_house()
    layers[0] = L("rectangle", 100, 400, 800, 10, PINK)
    return H(layers)
add("C26: body 800×10 skinny horizontal", case_c26())

def case_c27():
    layers = perfect_house()
    layers[4] = L("polygon", 100, 100, 1200, 200, NAVY, sides=3)
    return H(layers)
add("C27: roof 3× body width", case_c27())

def case_c28():
    layers = perfect_house()
    layers[4] = L("polygon", 600, 280, 20, 20, NAVY, sides=3)
    return H(layers)
add("C28: roof 20×20 (tiny)", case_c28())

def case_c29():
    layers = perfect_house()
    layers[2] = L("ellipse", 500, 400, 5, 5, WHITE)
    layers[3] = L("ellipse", 720, 400, 5, 5, YELLOW)
    return H(layers)
add("C29: windows 5×5 (tiny)", case_c29())

def case_c30():
    layers = perfect_house()
    layers[2] = L("ellipse", 350, 250, 300, 300, WHITE)
    layers[3] = L("ellipse", 650, 250, 300, 300, YELLOW)
    return H(layers)
add("C30: windows 300×300 (huge)", case_c30())

# D. Position
def case_d31():
    layers = perfect_house()
    layers[1] = L("rectangle", 600, 300, 80, 140, ORANGE)  # door at top of body
    return H(layers)
add("D31: door at top of body", case_d31())

def case_d32():
    layers = perfect_house()
    layers[2] = L("ellipse", 500, 800, 60, 60, WHITE)
    layers[3] = L("ellipse", 720, 800, 60, 60, YELLOW)
    return H(layers)
add("D32: windows below body, not on it", case_d32())

def case_d33():
    layers = perfect_house()
    layers[2] = L("ellipse", 600, 580, 60, 60, WHITE)  # window on door
    layers[3] = L("ellipse", 620, 600, 60, 60, YELLOW)
    return H(layers)
add("D33: windows on door (overlapping it)", case_d33())

def case_d34():
    layers = perfect_house()
    layers[2] = L("ellipse", 500, 100, 60, 60, WHITE)
    layers[3] = L("ellipse", 720, 100, 60, 60, YELLOW)
    return H(layers)
add("D34: windows above the roof", case_d34())

def case_d35():
    layers = perfect_house()
    layers[1] = L("rectangle", 440, 560, 80, 140, ORANGE)  # door at body's left edge
    return H(layers)
add("D35: door at body's far-left edge", case_d35())

def case_d36():
    layers = perfect_house()
    for l in layers:
        l["x"] -= 400; l["y"] -= 250
    return H(layers)
add("D36: house shifted to top-left corner of frame", case_d36())

def case_d37():
    return H()  # default perfect
add("D37: house centered (perfect)", case_d37())

def case_d38():
    layers = perfect_house()
    for l in layers:
        l["x"] += 600
    return H(layers)
add("D38: house extends past frame's right edge", case_d38())

def case_d39():
    layers = perfect_house()
    layers[4] = L("polygon", 200, 180, 480, 120, NAVY, sides=3)  # roof shifted left
    return H(layers)
add("D39: roof not centered horizontally on body", case_d39())

def case_d40():
    layers = perfect_house()
    layers[4] = L("polygon", 700, 180, 480, 120, NAVY, sides=3)  # roof 200px right of body center
    return H(layers)
add("D40: roof 200px off-center from body", case_d40())

# E. Roof variants
def case_e41():
    layers = perfect_house()
    layers[4] = L("polygon", 440, 350, 400, 200, NAVY, sides=3)  # roof inside body
    return H(layers)
add("E41: roof entirely inside body", case_e41())

def case_e42():
    layers = perfect_house()
    layers[4]["rotation"] = 45
    return H(layers)
add("E42: roof rotated 45°", case_e42())

def case_e43():
    layers = perfect_house()
    layers[4]["rotation"] = 180
    return H(layers)
add("E43: roof rotated 180° (upside down)", case_e43())

def case_e44():
    layers = perfect_house()
    layers[4] = L("polygon", 400, 180, 480, 120, NAVY, sides=4)
    return H(layers)
add("E44: roof has 4 sides (square polygon)", case_e44())

def case_e45():
    layers = perfect_house()
    layers[4] = L("polygon", 400, 180, 480, 120, NAVY, sides=6)
    return H(layers)
add("E45: roof has 6 sides (hexagon)", case_e45())

def case_e46():
    layers = perfect_house()
    layers[4] = L("polygon", 400, 175, 480, 120, NAVY, sides=3)  # bottom 5px above
    return H(layers)
add("E46: roof bottom 5px above body (within tolerance)", case_e46())

def case_e47():
    layers = perfect_house()
    layers[4] = L("polygon", 400, 130, 480, 120, NAVY, sides=3)  # bottom 50px above
    return H(layers)
add("E47: roof bottom 50px above body (clearly floating)", case_e47())

def case_e48():
    layers = perfect_house()
    layers[4] = L("polygon", 400, 200, 480, 120, NAVY, sides=3)  # bottom 20px below body top
    return H(layers)
add("E48: roof bottom 20px below body top (overlap)", case_e48())

def case_e49():
    layers = perfect_house()
    layers[4] = L("polygon", 440, 180, 400, 120, NAVY, sides=3)  # exact body width
    return H(layers)
add("E49: roof same width as body (no overhang)", case_e49())

def case_e50():
    layers = perfect_house()
    layers[4] = L("polygon", 100, 180, 1080, 120, NAVY, sides=3)
    return H(layers)
add("E50: roof much wider than body (huge overhang)", case_e50())

# F. Window variants
def case_f51():
    layers = perfect_house()
    layers[2] = L("ellipse", 460, 400, 200, 60, WHITE)
    layers[3] = L("ellipse", 680, 400, 200, 60, YELLOW)
    return H(layers)
add("F51: windows squashed (200×60, not circular)", case_f51())

def case_f52():
    layers = perfect_house()
    layers[3] = L("ellipse", 720, 400, 80, 80, YELLOW)  # different size
    return H(layers)
add("F52: windows different sizes (60 vs 80)", case_f52())

def case_f53():
    layers = perfect_house()
    layers[2] = L("ellipse", 540, 400, 60, 60, WHITE)
    layers[3] = L("ellipse", 600, 400, 60, 60, YELLOW)  # touching
    return H(layers)
add("F53: windows touching each other", case_f53())

def case_f54():
    layers = perfect_house()
    layers[2] = L("ellipse", 540, 400, 60, 60, WHITE)
    layers[3] = L("ellipse", 570, 400, 60, 60, YELLOW)  # overlap
    return H(layers)
add("F54: windows overlapping each other", case_f54())

def case_f55():
    layers = perfect_house()
    layers[2] = L("ellipse", 600, 400, 60, 60, WHITE)
    layers[3] = L("ellipse", 600, 480, 60, 60, YELLOW)  # stacked above door
    return H(layers)
add("F55: windows stacked vertically above door", case_f55())

def case_f56():
    layers = perfect_house()
    layers[2] = L("ellipse", 480, 400, 60, 60, WHITE)
    layers[3] = L("ellipse", 540, 400, 60, 60, YELLOW)  # both left of door
    return H(layers)
add("F56: both windows on left of door", case_f56())

def case_f57():
    layers = perfect_house()
    layers[2] = L("ellipse", 410, 400, 60, 60, WHITE)  # half outside body
    layers[3] = L("ellipse", 810, 400, 60, 60, YELLOW)
    return H(layers)
add("F57: windows half outside body", case_f57())

def case_f58():
    layers = perfect_house()
    layers[2]["fills"] = []
    layers[2]["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    layers[3]["fills"] = []
    layers[3]["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("F58: windows stroke-only (no fill)", case_f58())

def case_f59():
    layers = perfect_house()
    layers[2] = L("rectangle", 500, 400, 60, 60, WHITE)  # 1 window is rect
    return H(layers, evts=evt(rect=3, ellipse=1))
add("F59: 1 window is a rectangle, 1 ellipse", case_f59())

def case_f60():
    layers = perfect_house()
    layers[2] = L("ellipse", 540, 400, 60, 60, WHITE)  # touching door's left
    layers[3] = L("ellipse", 680, 400, 60, 60, YELLOW)  # touching door's right
    return H(layers)
add("F60: windows touching door's edges", case_f60())

# G. Frame variants
def case_g61():
    layers = perfect_house()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_house()
    inner = make_frame(layers, w=1000, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: frame inside another frame (nested)", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_house(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, house in 2nd", case_g63())

def case_g64():
    layers = perfect_house()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_house()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_house()
    for l in layers:
        l["x"] += 100; l["y"] += 50
    return H(layers)
add("G66: house close to frame edge", case_g66())

def case_g67():
    layers = perfect_house()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated to (500,300)", case_g67())

def case_g68():
    layers = perfect_house()
    frame = make_frame(layers, w=1279, h=831)  # within ±10 tolerance
    return make_log([frame], evt())
add("G68: frame 1279×831 (within tolerance)", case_g68())

# H. Tools / events
def case_h69():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 move_layer events", case_h69())

def case_h70():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H70: 50 undo events", case_h70())

def case_h71():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H71: used align_layers", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H72: used distribute_layers", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")] * 2)
    sem.extend([make_event("create_ellipse")] * 2)
    sem.append(make_event("create_polygon"))
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H73: pen tool used (no create_vector emitted)", case_h73())

def case_h74():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 2)
    sem.extend([make_event("create_ellipse")] * 2)
    sem.append(make_event("create_polygon"))
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H74: 0 tool_change events (keyboard shortcuts)", case_h74())

def case_h75():
    extras = [make_event("tool_change", before="polygon", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted a star", case_h75())

def case_h76():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("create_polygon"),
           make_event("tool_change", before="polygon", after="ellipse"),
           make_event("create_ellipse"), make_event("create_ellipse"),
           make_event("tool_change", before="ellipse", after="rectangle"),
           make_event("create_rectangle"), make_event("create_rectangle")]
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H76: shapes created in reverse order", case_h76())

def case_h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", case_h77())

def case_h78():
    return H(evts=evt(set_fill=10))  # 10 set_fill events
add("H78: 10 set_fill_color events", case_h78())

# I. Structure / hierarchy
def case_i79():
    layers = perfect_house()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: shapes inside group inside frame", case_i79())

def case_i80():
    f1 = make_frame(perfect_house()[:3], w=640, h=832)  # body, door, win_l
    f2 = make_frame(perfect_house()[3:], w=640, h=832)  # win_r, roof
    return make_log([f1, f2], evt())
add("I80: shapes split across 2 frames", case_i80())

def case_i81():
    layers = perfect_house()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I81: shapes inside section (not frame)", case_i81())

def case_i82():
    layers = perfect_house()
    frame = make_frame(layers[:3], w=1280, h=832)
    return make_log([frame, *layers[3:]], evt())
add("I82: 3 in frame, 2 on page", case_i82())

def case_i83():
    layers = perfect_house()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I83: 3-deep nested frames", case_i83())

def case_i84():
    layers = perfect_house()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I84: only body in frame, others on page", case_i84())

def case_i85():
    layers = perfect_house()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: house on page 2 (multi-page doc)", case_i85())

# J. Bizarre / hard
def case_j86():
    layers = perfect_house()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J86: body mirrored (scaleX=-1)", case_j86())

def case_j87():
    layers = perfect_house()
    layers[0]["rotation"] = 180
    return H(layers)
add("J87: body rotated 180°", case_j87())

def case_j88():
    layers = perfect_house()
    layers.insert(1, L("rectangle", 440, 300, 400, 400, GREEN))  # 2nd identical body
    return H(layers, evts=evt(rect=3))
add("J88: 2 identical bodies stacked", case_j88())

def case_j89():
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())

def case_j90():
    return H([])  # frame, no shapes
add("J90: frame only, no shapes", case_j90())

def case_j91():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "house"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text layer 'house'", case_j91())

def case_j92():
    layers = perfect_house()
    layers[0] = make_layer("star", x=440, y=300, w=400, h=400, fill=PINK, points=5, innerRatio=0.4)
    return H(layers, evts=evt(rect=1))
add("J92: body is a star (not rectangle)", case_j92())

def case_j93():
    layers = perfect_house()
    layers[4] = make_layer("star", x=400, y=180, w=480, h=120, fill=NAVY, points=5, innerRatio=0.4)
    return H(layers, evts=evt(polygon=0))
add("J93: roof is a star (not polygon)", case_j93())

def case_j94():
    layers = perfect_house()
    layers[2] = L("ellipse", 500, 400, 1, 1, WHITE)
    layers[3] = L("ellipse", 720, 400, 1, 1, YELLOW)
    return H(layers)
add("J94: windows are 1×1 (degenerate)", case_j94())

def case_j95():
    layers = perfect_house()
    for l in layers:
        l["y"] -= 1000  # negative y
    return H(layers)
add("J95: house with negative-y coords", case_j95())

def case_j96():
    layers = perfect_house()
    return H(layers)
add("J96: perfect house (control)", case_j96())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

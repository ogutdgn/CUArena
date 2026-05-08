"""100 edge cases for task 03 — runs all and prints a sorted score table."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, YELLOW, RED, ORANGE, GREEN, CYAN, NAVY, PURPLE, PINK, MAGENTA,
    WHITE, BLACK, GOLD,
)
from tasks import task_03_glowing_orb as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
PETAL_COLORS = [RED, ORANGE, GREEN, CYAN, NAVY, PURPLE, PINK, MAGENTA]


def evt(ellipse=9, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):
        sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_flower(radius=200, ellipse_w=60, center_w=60):
    cx, cy = 500, 500
    center = L("ellipse", cx-center_w/2, cy-center_w/2, center_w, center_w, YELLOW)
    petals = []
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + radius * math.cos(angle) - ellipse_w/2
        y = cy + radius * math.sin(angle) - ellipse_w/2
        c = PETAL_COLORS[i]
        petals.append(L("ellipse", x, y, ellipse_w, ellipse_w, c))
    return [center, *petals]


def H(layers=None, frame_w=1000, frame_h=1000, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_flower()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ────────────────────────────────────────────────────────
def case_a1():
    layers = perfect_flower()
    layers.append(L("ellipse", 200, 200, 50, 50, GOLD))
    return H(layers, evts=evt(ellipse=10))
add("A1: 10 ellipses (extra)", case_a1())

def case_a2():
    return H(perfect_flower()[:8], evts=evt(ellipse=8))
add("A2: 8 ellipses (missing 1)", case_a2())

def case_a3():
    return H([perfect_flower()[0]], evts=evt(ellipse=1))
add("A3: 1 ellipse (center only)", case_a3())

def case_a4():
    return H(perfect_flower()[1:], evts=evt(ellipse=8))
add("A4: 8 petals only (no center)", case_a4())

def case_a5():
    layers = perfect_flower()
    layers.extend(perfect_flower())  # double
    return H(layers, evts=evt(ellipse=18))
add("A5: 18 ellipses (doubled)", case_a5())

def case_a6():
    return H([], evts=evt(ellipse=0))
add("A6: empty", case_a6())

def case_a7():
    layers = perfect_flower()[:5]  # center + 4 petals
    return H(layers, evts=evt(ellipse=5))
add("A7: 5 ellipses (center + 4)", case_a7())

def case_a8():
    layers = perfect_flower()
    # add 5 random ellipses outside the radial
    for i in range(5):
        layers.append(L("ellipse", 50+i*30, 50, 30, 30, GREEN))
    return H(layers, evts=evt(ellipse=14))
add("A8: 14 ellipses (random extras)", case_a8())

def case_a9():
    # 9 ellipses but use the wrong type for half
    layers = perfect_flower()[:4]
    for i in range(5):
        layers.append(make_layer("rectangle", x=400+i*50, y=400, w=40, h=40, fill=PURPLE))
    sem = evt(ellipse=4, extras=[make_event("tool_change", before="ellipse", after="rectangle"),
                                  *[make_event("create_rectangle") for _ in range(5)]])
    return H(layers, evts=sem)
add("A9: 4 ellipses + 5 rectangles", case_a9())

def case_a10():
    return H(perfect_flower()[:7], evts=evt(ellipse=7))
add("A10: 7 ellipses (center + 6)", case_a10())


# ─── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    layers = perfect_flower()
    layers[0]["fills"][0]["color"] = {"r":1,"g":0,"b":0,"a":1}  # center red, not yellow
    return H(layers)
add("B11: center is red, not yellow", case_b11())

def case_b12():
    layers = perfect_flower()
    for p in layers[1:]:
        p["fills"][0]["color"] = {"r":1,"g":0,"b":0,"a":1}  # all petals same red
    return H(layers)
add("B12: all 8 petals same red color", case_b12())

def case_b13():
    layers = perfect_flower()
    layers[0]["fills"] = [{"kind": "image", "src": "yellow.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: center has image fill", case_b13())

def case_b14():
    layers = perfect_flower()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B14: all image fills", case_b14())

def case_b15():
    layers = perfect_flower()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("B15: stroke-only ellipses", case_b15())

def case_b16():
    """All same yellow."""
    layers = perfect_flower()
    for p in layers:
        p["fills"][0]["color"] = {"r":1,"g":0.9,"b":0.2,"a":1}
    return H(layers)
add("B16: all yellow (no contrast)", case_b16())

def case_b17():
    """All near-gray (within color tolerance)."""
    layers = perfect_flower()
    for i, p in enumerate(layers):
        p["fills"][0]["color"] = {"r":0.5+i*0.005,"g":0.5,"b":0.5,"a":1}
    return H(layers)
add("B17: all near-gray (within tol)", case_b17())

def case_b18():
    """Center has gradient fill."""
    layers = perfect_flower()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":0.9,"b":0.2,"a":1}},
        {"position": 1, "color": {"r":0.5,"g":0.5,"b":0.0,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B18: center gradient fill", case_b18())

def case_b19():
    """All ellipses have alpha=0 (invisible)."""
    layers = perfect_flower()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: all alpha=0", case_b19())

def case_b20():
    """Center has stacked fills (1st yellow, then image)."""
    layers = perfect_flower()
    layers[0]["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(layers)
add("B20: center has stacked fills", case_b20())


# ─── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """Center HUGE (covers entire frame)."""
    layers = perfect_flower()
    layers[0] = L("ellipse", 100, 100, 800, 800, YELLOW)
    return H(layers)
add("C21: huge center 800x800", case_c21())

def case_c22():
    """Center tiny 5×5."""
    layers = perfect_flower()
    layers[0] = L("ellipse", 497, 497, 5, 5, YELLOW)
    return H(layers)
add("C22: center 5x5 tiny", case_c22())

def case_c23():
    """Petals huge (200×200)."""
    layers = perfect_flower(ellipse_w=200)
    return H(layers)
add("C23: petals 200x200 large", case_c23())

def case_c24():
    """Petals tiny (5×5)."""
    layers = perfect_flower(ellipse_w=5)
    return H(layers)
add("C24: petals 5x5 tiny", case_c24())

def case_c25():
    """Petals stretched (200×60)."""
    layers = perfect_flower()
    for p in layers[1:]:
        p["w"] = 200
        p["h"] = 60
    return H(layers)
add("C25: petals 200x60 stretched", case_c25())

def case_c26():
    """Petals are actually full circles 60x60 (pass)."""
    return H(perfect_flower())
add("C26: petals 60x60 (perfect)", case_c26())

def case_c27():
    """Center 1×1 degenerate."""
    layers = perfect_flower()
    layers[0] = L("ellipse", 499, 499, 1, 1, YELLOW)
    return H(layers)
add("C27: center 1x1", case_c27())

def case_c28():
    """Petals different sizes."""
    layers = perfect_flower()
    sizes = [40, 60, 80, 100, 120, 50, 70, 90]
    for p, s in zip(layers[1:], sizes):
        p["w"] = p["h"] = s
    return H(layers)
add("C28: petals different sizes", case_c28())

def case_c29():
    """Center same size as petals (60x60) — design pattern check."""
    return H(perfect_flower(center_w=60))
add("C29: center 60x60 (same as petals)", case_c29())

def case_c30():
    """Petals all huge (overlapping each other)."""
    return H(perfect_flower(radius=100, ellipse_w=200))
add("C30: petals 200×200 overlapping", case_c30())


# ─── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Petals shifted off-center (not radial)."""
    layers = [perfect_flower()[0]]  # keep center
    for i in range(8):
        layers.append(L("ellipse", 100+i*100, 100, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("D31: petals in a row (linear)", case_d31())

def case_d32():
    """Petals in 3×3 grid (one is center)."""
    layers = []
    colors = [YELLOW, *PETAL_COLORS]
    for i in range(9):
        row, col = divmod(i, 3)
        layers.append(L("ellipse", 100+col*100, 100+row*100, 60, 60, colors[i]))
    return H(layers)
add("D32: 3x3 grid arrangement", case_d32())

def case_d33():
    """Center off-center, petals around it."""
    layers = perfect_flower()
    layers[0]["x"] = 100  # center moved to corner
    layers[0]["y"] = 100
    return H(layers)
add("D33: center at corner", case_d33())

def case_d34():
    """All 9 ellipses at same position."""
    return H([L("ellipse", 500, 500, 60, 60, c) for c in [YELLOW, *PETAL_COLORS]])
add("D34: 9 ellipses piled at one point", case_d34())

def case_d35():
    """Petals at correct radial angles but variable radius."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    radii = [100, 150, 200, 250, 300, 200, 150, 100]
    for i in range(8):
        angle = 2 * math.pi * i / 8
        r = radii[i]
        x = cx + r * math.cos(angle) - 30
        y = cy + r * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers, frame_w=1000, frame_h=1000)
add("D35: petals different radii", case_d35())

def case_d36():
    """7 petals at 8 angle positions (1 missing) but spread radially."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        if i == 4: continue  # skip
        angle = 2 * math.pi * i / 8
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers, evts=evt(ellipse=8))
add("D36: 7 petals + center (1 angle missing)", case_d36())

def case_d37():
    """Petals on top half only (4 angles, 2x each)."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(4):
        for j in range(2):
            angle = math.pi + (math.pi * i / 4) + j * 0.05
            x = cx + 200 * math.cos(angle) - 30
            y = cy + 200 * math.sin(angle) - 30
            layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i*2+j]))
    return H(layers)
add("D37: petals in top half only", case_d37())

def case_d38():
    """Perfect (control)."""
    return H()
add("D38: perfect (control)", case_d38())

def case_d39():
    """Center off-center (within frame but not at petals' center)."""
    layers = perfect_flower()
    layers[0]["x"] += 100  # center shifted right
    return H(layers)
add("D39: center off-center by 100px", case_d39())

def case_d40():
    """Petals rotated 45° around the center (still radial)."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8 + math.pi/8  # offset by 22.5°
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("D40: petals offset 22.5°", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────────
def case_e41():
    """Center rotated 90°."""
    layers = perfect_flower()
    layers[0]["rotation"] = 90
    return H(layers)
add("E41: center rotated 90°", case_e41())

def case_e42():
    """All petals rotated 45°."""
    layers = perfect_flower()
    for p in layers[1:]: p["rotation"] = 45
    return H(layers)
add("E42: all petals rotated 45°", case_e42())

def case_e43():
    """Center as ellipse with weird aspect 60×30."""
    layers = perfect_flower()
    layers[0]["w"] = 60
    layers[0]["h"] = 30
    return H(layers)
add("E43: center 60×30 (oval)", case_e43())

def case_e44():
    """Petals are stars."""
    cx, cy = 500, 500
    layers = [L("ellipse", cx-30, cy-30, 60, 60, YELLOW)]
    for i in range(8):
        angle = 2 * math.pi * i / 8
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(make_layer("star", x=x, y=y, w=60, h=60, fill=PETAL_COLORS[i], points=5, innerRatio=0.4))
    sem = evt(ellipse=1, extras=[make_event("tool_change", before="ellipse", after="star"),
                                   *[make_event("create_star") for _ in range(8)]])
    return H(layers, evts=sem)
add("E44: 1 ellipse center + 8 star petals", case_e44())

def case_e45():
    """All ellipses rotated 360° (≡ 0)."""
    layers = perfect_flower()
    for l in layers: l["rotation"] = 360
    return H(layers)
add("E45: all rotated 360°", case_e45())

def case_e46():
    """1 petal scaleX=-1."""
    layers = perfect_flower()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E46: 1 petal scaleX=-1", case_e46())

def case_e47():
    """All ellipses cornerRadius=20 (still circular but with extra rounding)."""
    layers = perfect_flower()
    for l in layers: l["cornerRadius"] = 20
    return H(layers)
add("E47: all cornerRadius=20", case_e47())

def case_e48():
    """1 petal scaleY=-1."""
    layers = perfect_flower()
    layers[3]["scaleY"] = -1
    return H(layers)
add("E48: 1 petal scaleY=-1", case_e48())

def case_e49():
    """Center rotated 4° (under tol)."""
    layers = perfect_flower()
    layers[0]["rotation"] = 4
    return H(layers)
add("E49: center rotated 4° (tolerance edge)", case_e49())

def case_e50():
    """Petals are very tall (60×200) like real petals, not circles."""
    layers = perfect_flower()
    for p in layers[1:]:
        p["h"] = 200
    return H(layers)
add("E50: petals 60×200 (tall)", case_e50())


# ─── F. Subcomponent variants ─────────────────────────────────────────
def case_f51():
    """Petals all touching center (no gap)."""
    return H(perfect_flower(radius=30))
add("F51: petals touching center", case_f51())

def case_f52():
    """Petals overlapping each other."""
    return H(perfect_flower(radius=80, ellipse_w=80))
add("F52: petals overlapping each other", case_f52())

def case_f53():
    """Petals very far from center."""
    return H(perfect_flower(radius=400), frame_w=1500, frame_h=1500)
add("F53: petals very far from center", case_f53())

def case_f54():
    """Center is way bigger than petals (1:5)."""
    layers = perfect_flower()
    layers[0]["w"] = layers[0]["h"] = 300
    layers[0]["x"] = 350
    layers[0]["y"] = 350
    return H(layers)
add("F54: center 300x300 (way bigger)", case_f54())

def case_f55():
    """All petals same exact color and position."""
    return H([perfect_flower()[0]] + [L("ellipse", 700, 500, 60, 60, RED) for _ in range(8)])
add("F55: 8 petals all at same point and color", case_f55())

def case_f56():
    """7 petals + 1 weird shape (rectangle)."""
    layers = perfect_flower()
    layers[1] = make_layer("rectangle", x=layers[1]["x"], y=layers[1]["y"], w=60, h=60, fill=RED)
    sem = evt(ellipse=8, extras=[make_event("tool_change", before="ellipse", after="rectangle"),
                                   make_event("create_rectangle")])
    return H(layers, evts=sem)
add("F56: 1 petal is a rectangle", case_f56())

def case_f57():
    """8 ellipses radially but no center (9th is at the radius too)."""
    cx, cy = 500, 500
    layers = []
    colors = [*PETAL_COLORS, YELLOW]
    for i in range(9):
        angle = 2 * math.pi * i / 9
        x = cx + 200 * math.cos(angle) - 30
        y = cy + 200 * math.sin(angle) - 30
        layers.append(L("ellipse", x, y, 60, 60, colors[i]))
    return H(layers)
add("F57: 9 petals on circle (no center)", case_f57())

def case_f58():
    """Petals stroke-only (no fill)."""
    layers = perfect_flower()
    for p in layers[1:]:
        p["fills"] = []
        p["strokes"] = [make_stroke(rgb=PETAL_COLORS[layers[1:].index(p)], weight=4)]
    return H(layers)
add("F58: petals stroke-only", case_f58())

def case_f59():
    """Petals all overlap center (radius=0)."""
    layers = [perfect_flower()[0]]
    for i in range(8):
        layers.append(L("ellipse", 470, 470, 60, 60, PETAL_COLORS[i]))
    return H(layers)
add("F59: all petals = center position", case_f59())

def case_f60():
    """Petals with cornerRadius (still circular)."""
    layers = perfect_flower()
    for p in layers[1:]: p["cornerRadius"] = 30
    return H(layers)
add("F60: petals cornerRadius=30", case_f60())


# ─── G. Frame variants ────────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_flower()
    frame = make_frame(layers, w=1000, h=1000)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Flower in nested frame."""
    layers = perfect_flower()
    inner = make_frame(layers, w=900, h=900)
    outer = make_frame([inner], w=1100, h=1100)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """2 frames, flower in 2nd."""
    f1 = make_frame([], w=500, h=500)
    f2 = make_frame(perfect_flower(), w=1000, h=1000)
    return make_log([f1, f2], evt())
add("G63: 2 frames, flower in 2nd", case_g63())

def case_g64():
    """Frame has stroke."""
    layers = perfect_flower()
    frame = make_frame(layers, w=1000, h=1000)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    """Frame with image fill."""
    layers = perfect_flower()
    frame = make_frame(layers, w=1000, h=1000, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    """Frame translated to (1000,1000)."""
    layers = perfect_flower()
    frame = make_frame(layers, x=1000, y=1000, w=1000, h=1000)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    """Tiny frame 200x200, flower bursts out."""
    return H(frame_w=200, frame_h=200)
add("G67: tiny 200x200 frame", case_g67())

def case_g68():
    """Frame 3000x3000 huge."""
    return H(frame_w=3000, frame_h=3000)
add("G68: 3000x3000 frame", case_g68())

def case_g69():
    """Flower entirely off-frame (negative coords)."""
    layers = perfect_flower()
    for l in layers:
        l["x"] -= 1500
        l["y"] -= 1500
    return H(layers)
add("G69: flower off-frame (negative)", case_g69())

def case_g70():
    """Frame perfectly fitting flower."""
    return H(frame_w=400, frame_h=400)
add("G70: 400x400 frame (matches flower)", case_g70())


# ─── H. Tools / events ────────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())

def case_h73():
    """No tool_change events."""
    sem = [make_event("session_start")]
    sem.extend([make_event("create_ellipse")] * 9)
    return H(evts=sem)
add("H73: no tool_change events", case_h73())

def case_h74():
    """Wrong tool (rectangle)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_ellipse")] * 9)
    return H(evts=sem)
add("H74: rectangle tool used (no ellipse)", case_h74())

def case_h75():
    """Pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_ellipse")] * 9)
    return H(evts=sem)
add("H75: pen tool only", case_h75())

def case_h76():
    """9 creates + 5 deletes."""
    sem = evt()
    sem.extend([make_event("delete") for _ in range(5)])
    return H(evts=sem)
add("H76: 9 creates + 5 deletes", case_h76())

def case_h77():
    """0 create_ellipse."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    return H(evts=sem)
add("H77: 0 create_ellipse events", case_h77())

def case_h78():
    """Used align_layers."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H78: align_layers used", case_h78())

def case_h79():
    """Used distribute_layers."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute_layers used", case_h79())

def case_h80():
    """Many session_end events."""
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H80: 5 session_end events", case_h80())


# ─── I. Hierarchy ─────────────────────────────────────────────────────
def case_i81():
    """Flower in group inside frame."""
    layers = perfect_flower()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([g], w=1000, h=1000)
    return make_log([frame], evt())
add("I81: flower in group in frame", case_i81())

def case_i82():
    """Flower split: center + 3 in 1 frame, 5 in another."""
    flower = perfect_flower()
    f1 = make_frame(flower[:4], w=500, h=1000)
    f2 = make_frame(flower[4:], w=500, h=1000)
    return make_log([f1, f2], evt())
add("I82: flower split across 2 frames", case_i82())

def case_i83():
    """Flower in section."""
    layers = perfect_flower()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: flower in section", case_i83())

def case_i84():
    """Flower on page (no frame)."""
    return H(in_frame=False)
add("I84: flower on page (no frame)", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_flower()
    f3 = make_frame(layers, w=900, h=900)
    f2 = make_frame([f3], w=1000, h=1000)
    f1 = make_frame([f2], w=1100, h=1100)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    """Flower on page 2."""
    layers = perfect_flower()
    frame = make_frame(layers, w=1000, h=1000)
    p1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    p2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[p1,p2]}}}
add("I86: flower on page 2", case_i86())

def case_i87():
    """Each ellipse in its own frame."""
    layers = perfect_flower()
    frames = [make_frame([l], w=200, h=200) for l in layers]
    return make_log(frames, evt())
add("I87: each ellipse in own frame", case_i87())

def case_i88():
    """Flower inside component."""
    layers = perfect_flower()
    comp = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
            "w": 1000, "h": 1000, "fills": [], "strokes": [], "effects": [],
            "children": layers}
    return make_log([comp], evt())
add("I88: flower inside component", case_i88())

def case_i89():
    """Center in frame, petals outside on page."""
    layers = perfect_flower()
    frame = make_frame([layers[0]], w=1000, h=1000)
    return make_log([frame, *layers[1:]], evt())
add("I89: center in frame, petals on page", case_i89())

def case_i90():
    """Flower in nested groups in frame."""
    layers = perfect_flower()
    g1 = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    g2 = {"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g1]}
    frame = make_frame([g2], w=1000, h=1000)
    return make_log([frame], evt())
add("I90: flower in nested groups in frame", case_i90())


# ─── J. Bizarre / hard ────────────────────────────────────────────────
def case_j91():
    """All ellipses scaleX=-1."""
    layers = perfect_flower()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J91: all scaleX=-1", case_j91())

def case_j92():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J92: empty document", case_j92())

def case_j93():
    """Text 'flower' instead of shapes."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=YELLOW)
    text["content"] = "yellow flower"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J93: text 'flower'", case_j93())

def case_j94():
    """All ellipses mirrored 180°."""
    layers = perfect_flower()
    for l in layers: l["rotation"] = 180
    return H(layers)
add("J94: all rotated 180°", case_j94())

def case_j95():
    """1×1 degenerate ellipses."""
    return H([L("ellipse", 500+i*2, 500, 1, 1, c) for i, c in enumerate([YELLOW, *PETAL_COLORS])])
add("J95: all 1x1 ellipses", case_j95())

def case_j96():
    """All ellipses are full frame."""
    return H([L("ellipse", 0, 0, 1000, 1000, c) for c in [YELLOW, *PETAL_COLORS]])
add("J96: all ellipses = full frame", case_j96())

def case_j97():
    """Rectangle imitating ellipse (using rectangle type)."""
    layers = []
    for c in [YELLOW, *PETAL_COLORS]:
        layers.append(make_layer("rectangle", x=400, y=400, w=60, h=60, fill=c, cornerRadius=30))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 9)
    return H(layers, evts=sem)
add("J97: 9 rectangles with cornerRadius (no ellipses)", case_j97())

def case_j98():
    """All petals same yellow color (looks like one big yellow blob)."""
    layers = perfect_flower()
    for p in layers: p["fills"][0]["color"] = {"r":1,"g":0.9,"b":0.2,"a":1}
    return H(layers)
add("J98: all 9 yellow", case_j98())

def case_j99():
    """All ellipses at same position with different rotations."""
    cx, cy = 500, 500
    layers = []
    for i, c in enumerate([YELLOW, *PETAL_COLORS]):
        l = L("ellipse", cx-30, cy-30, 60, 60, c)
        l["rotation"] = i * 40
        layers.append(l)
    return H(layers)
add("J99: ellipses concentric with different rotations", case_j99())

def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95 and not label.startswith("J100"):
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95, not J100): {fp_count}")

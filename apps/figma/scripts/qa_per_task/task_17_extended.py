"""100 edge cases for task 17 — Hourglass: 2 triangles point-to-point + 2 cap rectangles.

Each case is a wrong/edge-case design that should score < 1.0.
Anything scoring ≥ 0.95 is flagged as a candidate strict false-positive.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_17" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
# ─── Helpers ────────────────────────────────────────────────────────
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
TRI_FILL = (0.5, 0.4, 0.7)
CAP_FILL = (0.6, 0.5, 0.7)
CX = 500


def evt(rect=2, polygon=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("tool_change", before="polygon", after="rectangle")]
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_hourglass():
    """Top triangle (rotated 180° = pointing down), bottom triangle (rotated 0° = pointing up).
    Cap rectangles at top and bottom."""
    p_top = L("polygon", CX-50, 240, 100, 100, TRI_FILL, sides=3, rotation=180)
    p_bot = L("polygon", CX-50, 340, 100, 100, TRI_FILL, sides=3, rotation=0)
    cap_top = L("rectangle", CX-100, 220, 200, 16, CAP_FILL)
    cap_bot = L("rectangle", CX-100, 444, 200, 16, CAP_FILL)
    return [p_top, p_bot, cap_top, cap_bot]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832, in_frame=True):
    if layers is None: layers = perfect_hourglass()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():  # 3 polygons (extra triangle)
    layers = perfect_hourglass()
    layers.append(L("polygon", CX-30, 500, 60, 60, GREEN, sides=3, rotation=0))
    return H(layers, evts=evt(polygon=3))
add("A1: 3 triangles (extra polygon)", case_a1())

def case_a2():  # 1 polygon
    layers = [perfect_hourglass()[0]] + perfect_hourglass()[2:]
    return H(layers, evts=evt(polygon=1))
add("A2: 1 triangle only", case_a2())

def case_a3():  # 4 rectangles instead of 2
    layers = perfect_hourglass()
    layers.append(L("rectangle", CX-100, 480, 200, 16, CAP_FILL))
    layers.append(L("rectangle", CX-100, 200, 200, 16, CAP_FILL))
    return H(layers, evts=evt(rect=4))
add("A3: 4 cap rectangles", case_a3())

def case_a4():  # 0 rectangles
    layers = perfect_hourglass()[:2]
    return H(layers, evts=evt(rect=0))
add("A4: 0 cap rectangles", case_a4())

def case_a5():  # 0 polygons (just the caps)
    layers = perfect_hourglass()[2:]
    return H(layers, evts=evt(polygon=0))
add("A5: 0 triangles", case_a5())

def case_a6():  # double everything
    layers = perfect_hourglass()
    layers.extend([
        L("polygon", 700, 240, 60, 60, GREEN, sides=3, rotation=180),
        L("polygon", 700, 340, 60, 60, GREEN, sides=3, rotation=0),
    ])
    return H(layers, evts=evt(polygon=4))
add("A6: 4 triangles (doubled)", case_a6())

def case_a7():  # off by 1 cap
    layers = perfect_hourglass()[:3]
    return H(layers, evts=evt(rect=1))
add("A7: 1 cap rectangle", case_a7())

def case_a8():  # 0 of everything
    return H([], evts=[make_event("session_start")])
add("A8: empty design", case_a8())

def case_a9():  # 5 polygons stacked
    layers = []
    for i in range(5):
        rot = 180 if i % 2 == 0 else 0
        layers.append(L("polygon", CX-30, 200+i*80, 60, 60, TRI_FILL, sides=3, rotation=rot))
    layers.append(L("rectangle", CX-100, 180, 200, 16, CAP_FILL))
    layers.append(L("rectangle", CX-100, 600, 200, 16, CAP_FILL))
    return H(layers, evts=evt(polygon=5))
add("A9: 5 triangles", case_a9())

def case_a10():  # 1 polygon + 1 rect (off by 1 each)
    layers = [perfect_hourglass()[0], perfect_hourglass()[2]]
    return H(layers, evts=evt(polygon=1, rect=1))
add("A10: 1 triangle + 1 cap", case_a10())


# ─── B. Colors / fills ─────────────────────────────────────────────
def case_b11():  # all white (no contrast)
    layers = []
    for shape in perfect_hourglass():
        shape["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
        layers.append(shape)
    return H(layers)
add("B11: all white (no contrast)", case_b11())

def case_b12():  # all distinct fills (control)
    return H()
add("B12: standard fills (control)", case_b12())

def case_b13():  # triangle has image fill
    layers = perfect_hourglass()
    layers[0]["fills"] = [{"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return H(layers)
add("B13: triangle has image fill", case_b13())

def case_b14():  # rectangle has gradient
    layers = perfect_hourglass()
    layers[2]["fills"] = [{"kind": "gradient", "stops":[
        {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1,"visible":True}]
    return H(layers)
add("B14: cap has gradient fill", case_b14())

def case_b15():  # triangles have empty fills
    layers = perfect_hourglass()
    layers[0]["fills"] = []
    layers[1]["fills"] = []
    return H(layers)
add("B15: triangles have empty fills", case_b15())

def case_b16():  # alpha=0
    layers = perfect_hourglass()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: top triangle alpha=0", case_b16())

def case_b17():  # fillOpacity=0.05
    layers = perfect_hourglass()
    for shape in layers:
        shape["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B17: all fills near-transparent (opacity=0.05)", case_b17())

def case_b18():  # layer.opacity=0
    layers = perfect_hourglass()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("B18: top triangle opacity=0", case_b18())

def case_b19():  # fill.visible=False
    layers = perfect_hourglass()
    for shape in layers:
        shape["fills"][0]["visible"] = False
    return H(layers)
add("B19: all fills visible=False", case_b19())

def case_b20():  # stacked-fills (first solid, rest gradient)
    layers = perfect_hourglass()
    layers[0]["fills"].append({"kind":"image","src":"x","fit":"cover","opacity":0.5,"visible":True})
    layers[0]["fills"].append({"kind":"solid","color":{"r":0,"g":0,"b":0,"a":1},"opacity":0.3,"visible":True})
    return H(layers)
add("B20: top triangle has 3 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():  # tiny (degenerate)
    layers = perfect_hourglass()
    for shape in layers:
        shape["w"] = shape["h"] = 1
    return H(layers)
add("C21: 1×1 degenerate sizes", case_c21())

def case_c22():  # huge (overflow)
    layers = perfect_hourglass()
    for shape in layers:
        shape["w"] *= 10
        shape["h"] *= 10
    return H(layers)
add("C22: 10× sizes (overflow)", case_c22())

def case_c23():  # extreme aspect
    layers = perfect_hourglass()
    layers[0]["w"] = 500
    layers[0]["h"] = 10
    return H(layers)
add("C23: top triangle 500×10 (extreme aspect)", case_c23())

def case_c24():  # caps as wide as a quarter of their original
    layers = perfect_hourglass()
    layers[2]["w"] = 30
    layers[3]["w"] = 30
    return H(layers)
add("C24: caps 30 wide (much narrower than tris)", case_c24())

def case_c25():  # caps very tall (square instead of horizontal)
    layers = perfect_hourglass()
    layers[2]["h"] = 200
    layers[3]["h"] = 200
    return H(layers)
add("C25: caps 200 tall (square shape)", case_c25())

def case_c26():  # one tri tiny, one normal
    layers = perfect_hourglass()
    layers[0]["w"] = layers[0]["h"] = 5
    return H(layers)
add("C26: top triangle 5×5", case_c26())

def case_c27():  # one cap super wide, one normal
    layers = perfect_hourglass()
    layers[2]["w"] = 1000
    return H(layers)
add("C27: top cap 1000 wide", case_c27())

def case_c28():  # tris squashed flat
    layers = perfect_hourglass()
    layers[0]["h"] = 5
    layers[1]["h"] = 5
    return H(layers)
add("C28: triangles squashed flat", case_c28())

def case_c29():  # tris too narrow
    layers = perfect_hourglass()
    layers[0]["w"] = 5
    layers[1]["w"] = 5
    return H(layers)
add("C29: triangles 5 wide", case_c29())

def case_c30():  # caps wider than rest
    layers = perfect_hourglass()
    layers[2]["w"] = 800
    layers[3]["w"] = 800
    return H(layers)
add("C30: caps 800 wide (full width)", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():  # tris not aligned on x
    layers = perfect_hourglass()
    layers[0]["x"] = 200
    layers[1]["x"] = 700
    return H(layers)
add("D31: triangles not aligned on x (200 vs 700)", case_d31())

def case_d32():  # caps not aligned on x
    layers = perfect_hourglass()
    layers[2]["x"] = 100
    layers[3]["x"] = 600
    return H(layers)
add("D32: caps not aligned on x", case_d32())

def case_d33():  # all elements off-frame to right
    layers = perfect_hourglass()
    for shape in layers:
        shape["x"] += 1500
    return H(layers)
add("D33: hourglass shifted off-frame right", case_d33())

def case_d34():  # all elements at negative coords
    layers = perfect_hourglass()
    for shape in layers:
        shape["x"] -= 800
        shape["y"] -= 600
    return H(layers)
add("D34: negative coords (off-frame top-left)", case_d34())

def case_d35():  # tris in wrong order (top tri below bot tri)
    layers = perfect_hourglass()
    layers[0]["y"] = 340
    layers[1]["y"] = 240
    return H(layers)
add("D35: top triangle below bottom triangle", case_d35())

def case_d36():  # caps both at top
    layers = perfect_hourglass()
    layers[3]["y"] = 220
    return H(layers)
add("D36: both caps at top", case_d36())

def case_d37():  # caps both at bottom
    layers = perfect_hourglass()
    layers[2]["y"] = 444
    return H(layers)
add("D37: both caps at bottom", case_d37())

def case_d38():  # cx misaligned (cap rectangles not centered with triangles)
    layers = perfect_hourglass()
    layers[2]["x"] = CX - 100 + 80  # cap shifted right
    return H(layers)
add("D38: top cap shifted right of triangle center", case_d38())

def case_d39():  # tris very far apart
    layers = perfect_hourglass()
    layers[0]["y"] = 100
    layers[1]["y"] = 600
    return H(layers)
add("D39: triangles very far apart", case_d39())

def case_d40():  # tris overlapping (top below where bot starts)
    layers = perfect_hourglass()
    layers[0]["y"] = 280
    layers[1]["y"] = 280
    return H(layers)
add("D40: triangles fully overlapping", case_d40())


# ─── E. Per-shape variants (rotation/sides) ─────────────────────────
def case_e41():  # both tris pointing up
    layers = perfect_hourglass()
    layers[0]["rotation"] = 0
    layers[1]["rotation"] = 0
    return H(layers)
add("E41: both triangles pointing up (0°)", case_e41())

def case_e42():  # both tris pointing down
    layers = perfect_hourglass()
    layers[0]["rotation"] = 180
    layers[1]["rotation"] = 180
    return H(layers)
add("E42: both triangles pointing down (180°)", case_e42())

def case_e43():  # 4 sides instead of 3
    layers = perfect_hourglass()
    layers[0]["sides"] = 4
    layers[1]["sides"] = 4
    return H(layers)
add("E43: polygons have 4 sides (squares)", case_e43())

def case_e44():  # 6 sides
    layers = perfect_hourglass()
    layers[0]["sides"] = 6
    layers[1]["sides"] = 6
    return H(layers)
add("E44: polygons have 6 sides (hexagons)", case_e44())

def case_e45():  # tris rotated 90°
    layers = perfect_hourglass()
    layers[0]["rotation"] = 90
    layers[1]["rotation"] = 270
    return H(layers)
add("E45: triangles rotated 90/270", case_e45())

def case_e46():  # tris rotated 4° (under tol)
    layers = perfect_hourglass()
    layers[0]["rotation"] = 184
    layers[1]["rotation"] = 4
    return H(layers)
add("E46: triangles rotated 4° (under tol)", case_e46())

def case_e47():  # tris flipped scaleY=-1
    layers = perfect_hourglass()
    layers[0]["scaleY"] = -1
    layers[1]["scaleY"] = -1
    return H(layers)
add("E47: triangles flipped (scaleY=-1)", case_e47())

def case_e48():  # caps rotated 45°
    layers = perfect_hourglass()
    layers[2]["rotation"] = 45
    layers[3]["rotation"] = 45
    return H(layers)
add("E48: caps rotated 45°", case_e48())

def case_e49():  # one tri at 90 not 180
    layers = perfect_hourglass()
    layers[0]["rotation"] = 90
    return H(layers)
add("E49: one triangle at 90° (not 0/180)", case_e49())

def case_e50():  # caps as polygon (sides=4)
    layers = perfect_hourglass()
    # Replace cap rectangles with 4-sided polygons (squares)
    layers[2] = L("polygon", CX-100, 220, 200, 16, CAP_FILL, sides=4)
    layers[3] = L("polygon", CX-100, 444, 200, 16, CAP_FILL, sides=4)
    return H(layers, evts=evt(polygon=4, rect=0))
add("E50: caps replaced with polygon sides=4", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────────────
def case_f51():  # caps as different sizes
    layers = perfect_hourglass()
    layers[2]["w"] = 200
    layers[3]["w"] = 100
    return H(layers)
add("F51: caps different widths", case_f51())

def case_f52():  # caps stacked horizontally beside tris (not above/below)
    layers = perfect_hourglass()
    layers[2]["x"] = 100
    layers[2]["y"] = 290
    layers[3]["x"] = 800
    layers[3]["y"] = 290
    return H(layers)
add("F52: caps to the side of triangles", case_f52())

def case_f53():  # tris squeezed together (touching)
    layers = perfect_hourglass()
    layers[1]["y"] = 340
    return H(layers)
add("F53: triangles touching at center (control-like)", case_f53())

def case_f54():  # cap touching tri (no gap)
    layers = perfect_hourglass()
    layers[2]["y"] = 240   # touching top tri's top
    return H(layers)
add("F54: top cap touching triangle directly", case_f54())

def case_f55():  # cap inside triangle (overlap)
    layers = perfect_hourglass()
    layers[2]["x"] = CX - 50
    layers[2]["y"] = 280
    layers[2]["w"] = 100
    return H(layers)
add("F55: top cap overlaps top triangle", case_f55())

def case_f56():  # tris stacked horizontally (not vertically)
    layers = perfect_hourglass()
    layers[0]["x"] = CX-150
    layers[0]["y"] = 290
    layers[1]["x"] = CX+50
    layers[1]["y"] = 290
    return H(layers)
add("F56: triangles stacked horizontally", case_f56())

def case_f57():  # tris not point-to-point (gap of 100px between)
    layers = perfect_hourglass()
    layers[1]["y"] = 460  # large gap
    return H(layers)
add("F57: triangles separated by 100px gap", case_f57())

def case_f58():  # caps stroke-only (no fill)
    layers = perfect_hourglass()
    for i in (2, 3):
        layers[i]["fills"] = []
        layers[i]["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("F58: caps stroke-only", case_f58())

def case_f59():  # cap on top of tri (z-order)
    layers = perfect_hourglass()
    cap = layers.pop(2)
    layers.append(cap)
    return H(layers)
add("F59: top cap moved to last in z-order", case_f59())

def case_f60():  # caps very far away from tris (vertically)
    layers = perfect_hourglass()
    layers[2]["y"] = 50
    layers[3]["y"] = 700
    return H(layers)
add("F60: caps far from triangles", case_f60())


# ─── G. Frame variants ─────────────────────────────────────────────
def case_g61():  # frame rotated
    layers = perfect_hourglass()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():  # nested frames
    layers = perfect_hourglass()
    inner = make_frame(layers, w=900, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():  # 2 frames, hourglass in 2nd
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_hourglass(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, hourglass in 2nd", case_g63())

def case_g64():  # frame with stroke
    layers = perfect_hourglass()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():  # frame image fill
    layers = perfect_hourglass()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():  # tiny frame
    layers = perfect_hourglass()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G66: 200×200 tiny frame", case_g66())

def case_g67():  # frame translated
    layers = perfect_hourglass()
    frame = make_frame(layers, x=400, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():  # 4 deep nested frames
    layers = perfect_hourglass()
    f4 = make_frame(layers, w=1000, h=600)
    f3 = make_frame([f4], w=1100, h=700)
    f2 = make_frame([f3], w=1200, h=800)
    f1 = make_frame([f2], w=1300, h=900)
    return make_log([f1], evt())
add("G68: 4-deep nested frames", case_g68())


# ─── H. Tools / events ─────────────────────────────────────────────
def case_h69():  # 50 move events
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 move_layer events", case_h69())

def case_h70():  # missing tool_change (rectangle missing)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("create_polygon"), make_event("create_polygon"),
           make_event("create_rectangle"), make_event("create_rectangle")]
    return H(evts=sem)
add("H70: rectangle tool never changed to", case_h70())

def case_h71():  # missing polygon tool change
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_polygon"), make_event("create_polygon"),
           make_event("create_rectangle"), make_event("create_rectangle")]
    return H(evts=sem)
add("H71: polygon tool never changed to", case_h71())

def case_h72():  # extra align tool used
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H72: extra align_layers used (acceptable)", case_h72())

def case_h73():  # extra tool_change to pen + create_vector then delete
    extras = [make_event("tool_change", before="rectangle", after="pen"),
              make_event("create_vector"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H73: pen tool used + delete", case_h73())

def case_h74():  # 0 events
    return H(evts=[make_event("session_start")])
add("H74: just session_start (no events)", case_h74())

def case_h75():  # extra deletions
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H75: 20 delete events", case_h75())

def case_h76():  # only create events, no tool_change at all
    sem = [make_event("session_start"),
           make_event("create_polygon"), make_event("create_polygon"),
           make_event("create_rectangle"), make_event("create_rectangle")]
    return H(evts=sem)
add("H76: 0 tool_change events (keyboard shortcuts)", case_h76())

def case_h77():  # double session_end
    sem = evt() + [make_event("session_end"), make_event("session_end")]
    return H(evts=sem)
add("H77: 2 session_end events", case_h77())

def case_h78():  # 5 polygons created (more than 2)
    sem = evt(polygon=5)
    return H(evts=sem)
add("H78: 5 create_polygon events but only 2 polygons exist", case_h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i79():  # all in group inside frame
    layers = perfect_hourglass()
    group = {"id":"group_1", "type":"group", "x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: hourglass in group inside frame", case_i79())

def case_i80():  # split across 2 frames
    layers = perfect_hourglass()
    f1 = make_frame(layers[:2], w=640, h=832)
    f2 = make_frame(layers[2:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I80: hourglass split across 2 frames", case_i80())

def case_i81():  # in section
    layers = perfect_hourglass()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I81: hourglass in section", case_i81())

def case_i82():  # 2 in frame, 2 on page
    layers = perfect_hourglass()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, *layers[2:]], evt())
add("I82: 2 shapes in frame, 2 on page", case_i82())

def case_i83():  # 3-deep nested
    layers = perfect_hourglass()
    f3 = make_frame(layers, w=1000, h=600)
    f2 = make_frame([f3], w=1100, h=700)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I83: 3-deep nested frames", case_i83())

def case_i84():  # only triangles in frame
    layers = perfect_hourglass()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, *layers[2:]], evt())
add("I84: only triangles in frame", case_i84())

def case_i85():  # hourglass on page 2
    layers = perfect_hourglass()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: hourglass on page 2", case_i85())

def case_i86():  # hourglass in component
    layers = perfect_hourglass()
    component = {"id":"comp1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I86: hourglass in component", case_i86())

def case_i87():  # not in any frame
    layers = perfect_hourglass()
    return make_log(layers, evt())
add("I87: hourglass directly on page (no frame)", case_i87())

def case_i88():  # each shape in own frame
    layers = perfect_hourglass()
    frames = [make_frame([s], w=400, h=400) for s in layers]
    return make_log(frames, evt())
add("I88: each shape in own frame", case_i88())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j89():  # all flipped horizontally
    layers = perfect_hourglass()
    for shape in layers:
        shape["scaleX"] = -1
    return H(layers)
add("J89: all shapes scaleX=-1", case_j89())

def case_j90():  # all rotated 180
    layers = perfect_hourglass()
    for shape in layers:
        shape["rotation"] = (shape.get("rotation",0) + 180) % 360
    return H(layers)
add("J90: all shapes +180° rotation", case_j90())

def case_j91():  # 1×1 degenerate
    layers = perfect_hourglass()
    for shape in layers:
        shape["w"] = shape["h"] = 1
    return H(layers)
add("J91: all 1×1 sizes", case_j91())

def case_j92():  # negative coords
    layers = perfect_hourglass()
    for shape in layers:
        shape["x"] -= 1500
        shape["y"] -= 1500
    return H(layers)
add("J92: negative coords (offscreen)", case_j92())

def case_j93():  # all overlapping pile
    layers = []
    for shape in perfect_hourglass():
        shape["x"] = 500
        shape["y"] = 400
        shape["w"] = shape["h"] = 80
        layers.append(shape)
    return H(layers)
add("J93: all shapes piled at one point", case_j93())

def case_j94():  # all shapes = full frame
    layers = []
    for shape in perfect_hourglass():
        shape["x"] = 0; shape["y"] = 0
        shape["w"] = 1280; shape["h"] = 832
        layers.append(shape)
    return H(layers)
add("J94: all shapes = full frame", case_j94())

def case_j95():  # text spelling 'hourglass'
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "hourglass"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: just a text 'hourglass'", case_j95())

def case_j96():  # tris become stars
    layers = perfect_hourglass()
    layers[0] = make_layer("star", x=CX-50, y=240, w=100, h=100, fill=TRI_FILL,
                           points=5, innerRatio=0.4, rotation=180)
    layers[1] = make_layer("star", x=CX-50, y=340, w=100, h=100, fill=TRI_FILL,
                           points=5, innerRatio=0.4, rotation=0)
    return H(layers, evts=evt(polygon=0))
add("J96: triangles replaced with stars", case_j96())

def case_j97():  # caps are ellipses
    layers = perfect_hourglass()
    layers[2] = make_layer("ellipse", x=CX-100, y=220, w=200, h=16, fill=CAP_FILL)
    layers[3] = make_layer("ellipse", x=CX-100, y=444, w=200, h=16, fill=CAP_FILL)
    return H(layers, evts=evt(rect=0))
add("J97: caps replaced with ellipses", case_j97())

def case_j98():  # perfect (control)
    return H()
add("J98: perfect hourglass (control)", case_j98())

def case_j99():  # perfect smaller (control 2): scaled around CX,300 keeping point-to-point
    p_top = L("polygon", CX-30, 270, 60, 60, TRI_FILL, sides=3, rotation=180)
    p_bot = L("polygon", CX-30, 330, 60, 60, TRI_FILL, sides=3, rotation=0)
    cap_top = L("rectangle", CX-60, 254, 120, 16, CAP_FILL)
    cap_bot = L("rectangle", CX-60, 394, 120, 16, CAP_FILL)
    return H([p_top, p_bot, cap_top, cap_bot])
add("J99: smaller hourglass (control variant)", case_j99())

def case_j100():  # perfect larger (control 3): scaled keeping point-to-point
    p_top = L("polygon", CX-70, 200, 140, 140, TRI_FILL, sides=3, rotation=180)
    p_bot = L("polygon", CX-70, 340, 140, 140, TRI_FILL, sides=3, rotation=0)
    cap_top = L("rectangle", CX-140, 184, 280, 16, CAP_FILL)
    cap_bot = L("rectangle", CX-140, 484, 280, 16, CAP_FILL)
    return H([p_top, p_bot, cap_top, cap_bot])
add("J100: larger hourglass (control variant)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        is_control = "control" in label.lower()
        flag = " * FP" if score >= 0.95 and not is_control else ""
        if flag:
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95 non-control): {fp_count}/{len(CASES)}")

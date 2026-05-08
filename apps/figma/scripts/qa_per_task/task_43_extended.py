"""100 edge cases for task 43 (compass rose) — runs all and prints a sorted score table.

Task 43 prompt: sand-colored circle + 4 thin triangles pointing N/E/S/W from
center (90° apart) + 1 small gold center pivot circle. N triangle is red;
E/S/W are gray.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_43" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
DARK_GRAY = (0.30, 0.30, 0.30)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(ellipse=2, polygon=4, set_fill=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("tool_change", before="ellipse", after="polygon")]
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_compass():
    """Sand circle 300×300 at center, 4 thin triangles arranged radially, gold center 30×30."""
    cx, cy = 640, 416
    sand = L("ellipse", cx-150, cy-150, 300, 300, SAND)
    # 4 triangles arranged at radius 100 from center, centers at N/E/S/W cardinals.
    # Each is 30 wide × 100 tall. We want each layer's center at radius 100 from (cx, cy).
    # → top-left x = center_x - 15, top-left y = center_y - 50
    n = L("polygon", cx-15, cy-100-50, 30, 100, RED,       sides=3, rotation=0)    # center (cx, cy-100)
    e = L("polygon", cx+100-15, cy-50, 30, 100, GRAY,      sides=3, rotation=90)   # center (cx+100, cy)
    s = L("polygon", cx-15, cy+100-50, 30, 100, GRAY,      sides=3, rotation=180)  # center (cx, cy+100)
    w_ = L("polygon", cx-100-15, cy-50, 30, 100, DARK_GRAY, sides=3, rotation=270)  # center (cx-100, cy)
    center = L("ellipse", cx-15, cy-15, 30, 30, GOLD)
    return [sand, n, e, s, w_, center]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_compass()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_compass()
    layers.append(L("ellipse", 100, 100, 30, 30, NAVY))
    return H(layers, evts=evt(ellipse=3))
add("A1: 3 ellipses (extra)", case_a1())

def case_a2():
    layers = perfect_compass()
    layers.append(L("polygon", 100, 100, 30, 30, NAVY, sides=3))
    return H(layers, evts=evt(polygon=5))
add("A2: 5 polygons (extra triangle)", case_a2())

def case_a3():
    layers = perfect_compass()[:5]  # missing center
    return H(layers, evts=evt(ellipse=1))
add("A3: 1 ellipse (no center)", case_a3())

def case_a4():
    layers = perfect_compass()[:4]  # 3 triangles only
    return H(layers, evts=evt(polygon=3, ellipse=1))
add("A4: 3 triangles only", case_a4())

def case_a5():
    layers = perfect_compass()[:1]  # just sand
    return H(layers, evts=evt(polygon=0))
add("A5: just sand circle", case_a5())

def case_a6():
    return H([], evts=evt(ellipse=0, polygon=0))
add("A6: empty doc", case_a6())

def case_a7():
    layers = perfect_compass()[1:5]  # 4 triangles only
    return H(layers, evts=evt(ellipse=0))
add("A7: 4 triangles only (no circles)", case_a7())

def case_a8():
    layers = perfect_compass()
    layers.append(L("polygon", 100, 100, 30, 30, NAVY, sides=3))
    layers.append(L("polygon", 200, 100, 30, 30, NAVY, sides=3))
    return H(layers, evts=evt(polygon=6))
add("A8: 6 polygons", case_a8())

def case_a9():
    layers = perfect_compass()
    layers.append(L("polygon", 100, 100, 30, 30, NAVY, sides=4))  # square
    return H(layers, evts=evt(polygon=5))
add("A9: extra square polygon", case_a9())

def case_a10():
    layers = perfect_compass()[:5]
    layers[0] = L("ellipse", 490, 266, 300, 300, GOLD)  # sand→gold
    return H(layers, evts=evt(ellipse=1))
add("A10: 1 ellipse (sand replaced gold)", case_a10())


# ─── B. Colors ───────────────────────────────────────────────────────
def case_b11():
    layers = perfect_compass()
    layers[0]["fills"] = [{"kind": "image", "src": "sand.jpg", "fit": "cover",
                           "opacity": 1, "visible": True}]
    return H(layers)
add("B11: sand circle has image fill", case_b11())

def case_b12():
    layers = perfect_compass()
    for l in layers:
        l["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}  # all gray
    return H(layers)
add("B12: all 6 layers gray (no distinct)", case_b12())

def case_b13():
    layers = perfect_compass()
    for l in layers[1:5]:
        l["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}  # all 4 triangles gray
    return H(layers)
add("B13: all 4 triangles gray (no red N)", case_b13())

def case_b14():
    layers = perfect_compass()
    layers[0]["fills"] = []  # sand no fill
    return H(layers)
add("B14: sand circle no fill", case_b14())

def case_b15():
    layers = perfect_compass()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=SAND, weight=4)]
    return H(layers)
add("B15: sand circle stroke-only", case_b15())

def case_b16():
    layers = perfect_compass()
    layers[5]["fills"][0]["color"] = {"r": 0.95, "g": 0.78, "b": 0.10, "a": 1.0}  # near-gold
    return H(layers)
add("B16: center near-gold (within tol)", case_b16())

def case_b17():
    layers = perfect_compass()
    layers[1]["fills"][0]["opacity"] = 0.1  # N triangle transparent
    return H(layers)
add("B17: N triangle opacity 0.1", case_b17())

def case_b18():
    layers = perfect_compass()
    layers[0]["fills"][0]["color"]["a"] = 0  # sand alpha=0
    return H(layers)
add("B18: sand alpha=0", case_b18())

def case_b19():
    layers = perfect_compass()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 0.8, "b": 0.6, "a": 1}},
        {"position": 1, "color": {"r": 0.5, "g": 0.4, "b": 0.3, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B19: sand gradient", case_b19())

def case_b20():
    layers = perfect_compass()
    # All triangles distinct colors (4 different) but 2 of 4 nearly same
    layers[1] = L("polygon", 625, 286, 30, 100, RED, sides=3, rotation=0)
    layers[2] = L("polygon", 670, 401, 30, 100, (0.51, 0.51, 0.51), sides=3, rotation=90)
    layers[3] = L("polygon", 625, 446, 30, 100, (0.50, 0.50, 0.50), sides=3, rotation=180)
    layers[4] = L("polygon", 510, 401, 30, 100, (0.50, 0.50, 0.50), sides=3, rotation=270)
    return H(layers)
add("B20: 3 grays nearly identical", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_compass()
    layers[0] = L("ellipse", 0, 0, 1280, 832, SAND)  # sand = full frame
    return H(layers)
add("C21: sand = full frame", case_c21())

def case_c22():
    layers = perfect_compass()
    layers[0] = L("ellipse", 600, 400, 5, 5, SAND)  # tiny sand
    return H(layers)
add("C22: sand 5×5 (tiny)", case_c22())

def case_c23():
    layers = perfect_compass()
    layers[5] = L("ellipse", 625, 401, 1, 1, GOLD)  # 1×1 center
    return H(layers)
add("C23: center 1×1", case_c23())

def case_c24():
    layers = perfect_compass()
    layers[5] = L("ellipse", 490, 266, 300, 300, GOLD)  # center same size as sand
    return H(layers)
add("C24: center = sand size (no contrast)", case_c24())

def case_c25():
    layers = perfect_compass()
    layers[1]["w"] = 200  # N very wide
    return H(layers)
add("C25: N triangle 200 wide (squashed)", case_c25())

def case_c26():
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["w"] = 200
    return H(layers)
add("C26: all triangles 200 wide", case_c26())

def case_c27():
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["h"] = 5
    return H(layers)
add("C27: all triangles 5 tall (degenerate)", case_c27())

def case_c28():
    layers = perfect_compass()
    layers[0] = L("ellipse", 400, 200, 600, 200, SAND)  # sand oval
    return H(layers)
add("C28: sand oval 600×200", case_c28())

def case_c29():
    layers = perfect_compass()
    layers[5] = L("ellipse", 625, 401, 30, 60, GOLD)  # center oval
    return H(layers)
add("C29: center oval 30×60", case_c29())

def case_c30():
    layers = perfect_compass()
    layers[1] = L("polygon", 100, 100, 600, 100, RED, sides=3, rotation=0)
    return H(layers)
add("C30: N triangle huge 600×100", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_compass()
    for l in layers: l["x"] -= 600  # shift left
    return H(layers)
add("D31: shifted left out of frame", case_d31())

def case_d32():
    layers = perfect_compass()
    for l in layers: l["y"] -= 500
    return H(layers)
add("D32: shifted up", case_d32())

def case_d33():
    layers = perfect_compass()
    layers[5]["x"] = 0
    layers[5]["y"] = 0
    return H(layers)
add("D33: center at (0,0)", case_d33())

def case_d34():
    return H()
add("D34: perfect (control)", case_d34())

def case_d35():
    layers = perfect_compass()
    layers[1]["x"] = 0
    layers[1]["y"] = 0  # N triangle far away
    return H(layers)
add("D35: N triangle at corner", case_d35())

def case_d36():
    layers = perfect_compass()
    # All triangles at sand center (overlapping)
    for i in range(1, 5):
        layers[i]["x"] = 625
        layers[i]["y"] = 401
    return H(layers)
add("D36: all triangles piled at center", case_d36())

def case_d37():
    layers = perfect_compass()
    # Triangles at corners
    layers[1] = L("polygon", 100, 100, 30, 100, RED, sides=3, rotation=0)
    layers[2] = L("polygon", 1100, 100, 30, 100, GRAY, sides=3, rotation=0)
    layers[3] = L("polygon", 100, 700, 30, 100, GRAY, sides=3, rotation=0)
    layers[4] = L("polygon", 1100, 700, 30, 100, DARK_GRAY, sides=3, rotation=0)
    return H(layers)
add("D37: triangles at 4 corners (none rotated)", case_d37())

def case_d38():
    layers = perfect_compass()
    # All overlap sand but no clear cardinal direction
    for i in range(1, 5):
        layers[i]["x"] = 540 + i*30
        layers[i]["y"] = 350
    return H(layers)
add("D38: triangles in a row, no cardinals", case_d38())

def case_d39():
    layers = perfect_compass()
    layers[5]["x"] = 100
    layers[5]["y"] = 700
    return H(layers)
add("D39: gold center off-center", case_d39())

def case_d40():
    layers = perfect_compass()
    for l in layers: l["x"] += 100
    return H(layers)
add("D40: shifted slightly right", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_compass()
    layers[1]["sides"] = 4  # N square
    return H(layers)
add("E41: N triangle has 4 sides", case_e41())

def case_e42():
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["sides"] = 4
    return H(layers)
add("E42: all 4 polygons have 4 sides", case_e42())

def case_e43():
    layers = perfect_compass()
    layers[0]["rotation"] = 45  # sand rotated
    return H(layers)
add("E43: sand rotated 45°", case_e43())

def case_e44():
    layers = perfect_compass()
    for i in range(1, 5):
        layers[i]["rotation"] = 0  # all 0° (no cardinal directions)
    return H(layers)
add("E44: all triangles rotation=0 (no cardinals)", case_e44())

def case_e45():
    layers = perfect_compass()
    # Step 60° instead of 90°
    layers[1]["rotation"] = 0
    layers[2]["rotation"] = 60
    layers[3]["rotation"] = 120
    layers[4]["rotation"] = 180
    return H(layers)
add("E45: triangles at 60° steps (5 directions implied)", case_e45())

def case_e46():
    layers = perfect_compass()
    layers[1]["rotation"] = 4  # 4° (under 10° tol)
    return H(layers)
add("E46: N triangle 4° (under tol)", case_e46())

def case_e47():
    layers = perfect_compass()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E47: N triangle scaleX=-1", case_e47())

def case_e48():
    layers = perfect_compass()
    layers[0]["scaleY"] = -1  # sand mirrored
    return H(layers)
add("E48: sand mirrored", case_e48())

def case_e49():
    layers = perfect_compass()
    # 3 of 4 triangles same size, 1 different
    layers[2] = L("polygon", 670, 401, 60, 200, GRAY, sides=3, rotation=90)
    return H(layers)
add("E49: E triangle bigger (60×200)", case_e49())

def case_e50():
    layers = perfect_compass()
    # Triangles fully aligned but N is a star
    layers[1] = make_layer("star", x=625, y=286, w=30, h=100, fill=RED, points=5)
    return H(layers, evts=evt(polygon=3, extras=[make_event("create_star")]))
add("E50: N triangle is a star", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    layers = perfect_compass()
    # Sand and center at different positions
    layers[5]["x"] = 100
    layers[5]["y"] = 100
    return H(layers)
add("F51: center far from sand", case_f51())

def case_f52():
    layers = perfect_compass()
    # Center BIGGER than sand
    layers[5] = L("ellipse", 100, 100, 500, 500, GOLD)
    return H(layers)
add("F52: center bigger than sand", case_f52())

def case_f53():
    layers = perfect_compass()
    # Sand wider than tall (oval)
    layers[0] = L("ellipse", 200, 366, 800, 100, SAND)
    return H(layers)
add("F53: sand 800×100 oval", case_f53())

def case_f54():
    layers = perfect_compass()
    # Triangles all same color
    for i in range(1, 5):
        layers[i]["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}
    return H(layers)
add("F54: all 4 triangles same gray", case_f54())

def case_f55():
    layers = perfect_compass()
    # 2 triangles overlap each other
    layers[2]["x"] = layers[1]["x"]  # E at N's x
    layers[2]["rotation"] = 0
    return H(layers)
add("F55: E triangle at N's position", case_f55())

def case_f56():
    layers = perfect_compass()
    # Center fully outside sand
    layers[5]["x"] = 1100
    layers[5]["y"] = 700
    return H(layers)
add("F56: gold center outside sand", case_f56())

def case_f57():
    layers = perfect_compass()
    # Sand is ALSO gold
    layers[0]["fills"][0]["color"] = {"r": 0.85, "g": 0.65, "b": 0.13, "a": 1.0}
    return H(layers)
add("F57: sand is gold (same as center)", case_f57())

def case_f58():
    layers = perfect_compass()
    layers[1]["fills"][0]["opacity"] = 0  # N invisible
    return H(layers)
add("F58: N triangle fillOpacity=0", case_f58())

def case_f59():
    layers = perfect_compass()
    # Triangles at very large w (overlap each other)
    for i in range(1, 5):
        layers[i] = L("polygon", 100, 100, 1000, 200, [RED, GRAY, GRAY, DARK_GRAY][i-1],
                      sides=3, rotation=(i-1)*90)
    return H(layers)
add("F59: triangles huge (overlap each other)", case_f59())

def case_f60():
    layers = perfect_compass()
    # Triangles same dimensions but rotated incorrectly (all 45°)
    for i in range(1, 5):
        layers[i]["rotation"] = 45
    return H(layers)
add("F60: triangles all rotated 45°", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_compass()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    inner = make_frame(perfect_compass(), w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    return H(frame_w=2000, frame_h=2000)
add("G63: frame 2000x2000", case_g63())

def case_g64():
    layers = perfect_compass()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_compass()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_compass(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G66: 2 frames, compass in 2nd", case_g66())

def case_g67():
    layers = perfect_compass()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H(frame_w=200, frame_h=200)
add("G68: frame 200x200 (too small)", case_g68())

def case_g69():
    layers = perfect_compass()
    return make_log(layers, evt())
add("G69: no frame, on page", case_g69())

def case_g70():
    return H(frame_w=1290, frame_h=842)
add("G70: frame 1290x842 (within tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    return H(evts=[make_event("session_start")])
add("H71: no events", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("create_ellipse"),
           make_event("create_polygon")]
    return H(evts=sem)
add("H72: events but no tool_change", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H73: rectangle tool used", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H74: only ellipse tool, no polygon", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H75: 50 undo events", case_h75())

def case_h76():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H76: many deletes", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    sem.extend([make_event("create_polygon")] * 4)
    return H(evts=sem)
add("H77: only polygon used", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("create_rectangle"), make_event("delete")]))
add("H78: rect created+deleted", case_h78())

def case_h79():
    return H(evts=evt(set_fill=20))
add("H79: 20 set_fill events", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("session_end")] * 5))
add("H80: many session_end events", case_h80())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i81():
    layers = perfect_compass()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group inside frame", case_i81())

def case_i82():
    compass = perfect_compass()
    f1 = make_frame(compass[:3], w=640, h=832)
    f2 = make_frame(compass[3:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_compass()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: inside section", case_i83())

def case_i84():
    layers = perfect_compass()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    compass = perfect_compass()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(compass, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: compass on page 2", case_i85())

def case_i86():
    compass = perfect_compass()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": compass}
    return make_log([component], evt())
add("I86: inside component", case_i86())

def case_i87():
    compass = perfect_compass()
    return make_log(compass, evt())
add("I87: on page (no frame)", case_i87())

def case_i88():
    compass = perfect_compass()
    frame = make_frame([compass[0]], w=1280, h=832)
    return make_log([frame, *compass[1:]], evt())
add("I88: only sand in frame, others on page", case_i88())

def case_i89():
    compass = perfect_compass()
    inner = make_frame([compass[0]], w=300, h=300)
    outer = make_frame([inner, *compass[1:]], w=1280, h=832)
    return make_log([outer], evt())
add("I89: sand in inner frame, others in outer", case_i89())

def case_i90():
    return H(frame_fill=(0, 0, 0))
add("I90: black frame fill", case_i90())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j91():
    layers = perfect_compass()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J91: sand mirrored", case_j91())

def case_j92():
    layers = perfect_compass()
    text = make_layer("text", x=100, y=100, w=200, h=50, fill=NAVY)
    text["content"] = "compass"
    return H(layers + [text])
add("J92: compass + text 'compass'", case_j92())

def case_j93():
    layers = [L("ellipse", 0, 0, 1280, 832, SAND),
              L("polygon", 0, 0, 1280, 832, RED, sides=3, rotation=0),
              L("polygon", 0, 0, 1280, 832, GRAY, sides=3, rotation=90),
              L("polygon", 0, 0, 1280, 832, GRAY, sides=3, rotation=180),
              L("polygon", 0, 0, 1280, 832, DARK_GRAY, sides=3, rotation=270),
              L("ellipse", 0, 0, 1280, 832, GOLD)]
    return H(layers)
add("J93: all shapes = full frame", case_j93())

def case_j94():
    layers = perfect_compass()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("J94: sand invisible", case_j94())

def case_j95():
    layers = perfect_compass()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("J95: sand alpha=0", case_j95())

def case_j96():
    layers = perfect_compass()
    layers[5]["visible"] = False  # center hidden
    return H(layers)
add("J96: center visible=False", case_j96())

def case_j97():
    layers = perfect_compass()
    layers[1]["opacity"] = 0  # N opacity 0
    return H(layers)
add("J97: N triangle opacity=0", case_j97())

def case_j98():
    layers = perfect_compass()
    for l in layers: l["y"] -= 1000
    return H(layers)
add("J98: shifted up off-screen", case_j98())

def case_j99():
    layers = perfect_compass()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J99: all shapes 0×0", case_j99())

def case_j100():
    return H()  # control
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
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

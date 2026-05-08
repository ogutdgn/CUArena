"""100 edge cases for task 33 (pie chart) — runs all and prints a sorted score table."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    MAGENTA, TEAL, COBALT,
)
from tasks import task_33_pie_chart as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
W1 = (0.95, 0.4, 0.4)
W2 = (0.95, 0.85, 0.2)


def evt(ellipse=1, polygon=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.append(make_event("tool_change", before="ellipse", after="polygon"))
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pie(base=TEAL, w1=W1, w2=W2):
    """Teal base circle + 2 wedge triangles layered on top."""
    cx, cy = 500, 500
    base_circle = L("ellipse", cx - 150, cy - 150, 300, 300, base)
    wedge_1 = L("polygon", cx - 30, cy - 150, 60, 300, w1, sides=3, rotation=30)
    wedge_2 = L("polygon", cx - 30, cy - 150, 60, 300, w2, sides=3, rotation=120)
    return [base_circle, wedge_1, wedge_2]


CASES = []


def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, in_frame=False, frame_w=1000, frame_h=1000,
      frame_fill=(0.95, 0.95, 0.95)):
    if layers is None: layers = perfect_pie()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ── A. Counts ───────────────────────────────────────────────────────
def case_a1():
    layers = perfect_pie()
    layers.append(L("ellipse", 100, 100, 80, 80, RED))
    return H(layers, evts=evt(ellipse=2))
add("A1: 2 ellipses (extra)", case_a1())


def case_a2():
    layers = perfect_pie()[1:]  # no base
    return H(layers, evts=evt(ellipse=0))
add("A2: 0 ellipses (no base)", case_a2())


def case_a3():
    layers = perfect_pie()
    layers.append(L("polygon", 200, 200, 60, 60, PURPLE, sides=3))
    return H(layers, evts=evt(polygon=3))
add("A3: 3 polygons (extra wedge)", case_a3())


def case_a4():
    layers = perfect_pie()[:1]  # only base
    return H(layers, evts=evt(polygon=0))
add("A4: 0 wedges (only base)", case_a4())


def case_a5():
    layers = perfect_pie()
    layers.append(L("polygon", 200, 200, 60, 200, GREEN, sides=3))
    layers.append(L("polygon", 800, 200, 60, 200, BLUE, sides=3))
    return H(layers, evts=evt(polygon=4))
add("A5: 4 wedges", case_a5())


def case_a6():
    layers = perfect_pie()[:2]  # 1 base + 1 wedge
    return H(layers, evts=evt(polygon=1))
add("A6: 1 wedge only", case_a6())


def case_a7():
    layers = perfect_pie() + perfect_pie()  # 2 pies
    return H(layers, evts=evt(ellipse=2, polygon=4))
add("A7: 2 complete pies", case_a7())


def case_a8():
    return H([], evts=evt(ellipse=0, polygon=0))
add("A8: empty", case_a8())


def case_a9():
    layers = perfect_pie()
    layers.extend([L("ellipse", 100+i*60, 700, 30, 30, GREEN) for i in range(3)])
    return H(layers, evts=evt(ellipse=4))
add("A9: 4 ellipses (extras)", case_a9())


def case_a10():
    layers = perfect_pie() + [L("rectangle", 100, 100, 80, 80, RED)]
    return H(layers)
add("A10: pie + extra rectangle", case_a10())


# ── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    """Base color is gray, not teal."""
    layers = perfect_pie(base=GRAY)
    return H(layers)
add("B11: base GRAY (not teal)", case_b11())


def case_b12():
    """Both wedges same color (red)."""
    layers = perfect_pie(w1=RED, w2=RED)
    return H(layers)
add("B12: both wedges same color", case_b12())


def case_b13():
    """Base has image fill."""
    layers = perfect_pie()
    layers[0]["fills"] = [{"kind": "image", "src": "pie.jpg", "fit": "cover",
                           "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: base has image fill", case_b13())


def case_b14():
    """Base stroke only (no fill)."""
    layers = perfect_pie()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=TEAL, weight=4)]
    return H(layers)
add("B14: base stroke only", case_b14())


def case_b15():
    """Base fills array empty."""
    layers = perfect_pie()
    layers[0]["fills"] = []
    return H(layers)
add("B15: base fills empty", case_b15())


def case_b16():
    """All 3 white (no contrast with white frame)."""
    layers = perfect_pie(base=WHITE, w1=WHITE, w2=WHITE)
    return H(layers)
add("B16: all white", case_b16())


def case_b17():
    """Near-teal but slightly off."""
    NEAR_TEAL = (0.05, 0.6, 0.6)
    layers = perfect_pie(base=NEAR_TEAL)
    return H(layers)
add("B17: base near-teal (within tol)", case_b17())


def case_b18():
    """Base has gradient fill."""
    layers = perfect_pie()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 0, "g": 0.6, "b": 0.6, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0.4, "b": 0.4, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B18: base gradient fill", case_b18())


def case_b19():
    """Base fill opacity=0.1."""
    layers = perfect_pie()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: base fill opacity 0.1", case_b19())


def case_b20():
    """Base has 3 stacked fills."""
    layers = perfect_pie()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True}])
    return H(layers)
add("B20: base 3 stacked fills", case_b20())


# ── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """Base circle huge."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 0, 0, 1000, 1000, TEAL)
    return H(layers)
add("C21: base 1000×1000", case_c21())


def case_c22():
    """Base circle very small."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 480, 480, 40, 40, TEAL)
    return H(layers)
add("C22: base 40×40", case_c22())


def case_c23():
    """Base squashed (not circular)."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 200, 470, 600, 60, TEAL)
    return H(layers)
add("C23: base 600×60 (squashed oval)", case_c23())


def case_c24():
    """Wedges huge (bigger than base)."""
    layers = perfect_pie()
    layers[1]["w"] = 600
    layers[1]["h"] = 800
    layers[2]["w"] = 600
    layers[2]["h"] = 800
    return H(layers)
add("C24: wedges 600×800 (bigger than base)", case_c24())


def case_c25():
    """Wedges very thin."""
    layers = perfect_pie()
    layers[1]["w"] = 5
    layers[2]["w"] = 5
    return H(layers)
add("C25: wedges 5px wide", case_c25())


def case_c26():
    """Wedges all same size (looks normal)."""
    return H()
add("C26: perfect pie (control)", case_c26())


def case_c27():
    """Base 1×1 degenerate."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 499, 499, 1, 1, TEAL)
    return H(layers)
add("C27: base 1×1 degenerate", case_c27())


def case_c28():
    """Wedges 1×1 degenerate."""
    layers = perfect_pie()
    layers[1] = L("polygon", 499, 499, 1, 1, W1, sides=3)
    layers[2] = L("polygon", 499, 499, 1, 1, W2, sides=3)
    return H(layers)
add("C28: wedges 1×1 degenerate", case_c28())


def case_c29():
    """Wedge 1 huge, wedge 2 normal."""
    layers = perfect_pie()
    layers[1]["w"] = 800
    layers[1]["h"] = 800
    return H(layers)
add("C29: 1 huge wedge", case_c29())


def case_c30():
    """Base diameter 5px."""
    layers = perfect_pie()
    layers[0] = L("ellipse", 497, 497, 5, 5, TEAL)
    return H(layers)
add("C30: base 5×5 (tiny)", case_c30())


# ── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Base in corner."""
    layers = perfect_pie()
    layers[0]["x"] = 50
    layers[0]["y"] = 50
    return H(layers)
add("D31: base in top-left corner", case_d31())


def case_d32():
    """Wedges far from base."""
    layers = perfect_pie()
    layers[1]["x"] = 50
    layers[1]["y"] = 50
    layers[2]["x"] = 900
    layers[2]["y"] = 900
    return H(layers)
add("D32: wedges far from base", case_d32())


def case_d33():
    """Base off-canvas (negative coords)."""
    layers = perfect_pie()
    layers[0]["x"] = -200
    layers[0]["y"] = -200
    return H(layers)
add("D33: base off-canvas", case_d33())


def case_d34():
    """Wedges far apart (no overlap with base)."""
    layers = perfect_pie()
    layers[1]["x"] = 50
    layers[2]["x"] = 1000
    return H(layers)
add("D34: wedges far from base", case_d34())


def case_d35():
    """Base and wedges all centered (control)."""
    return H()
add("D35: perfect centered pie", case_d35())


def case_d36():
    """Wedges aligned but rotated 0°."""
    layers = perfect_pie()
    layers[1]["rotation"] = 0
    layers[2]["rotation"] = 0
    return H(layers)
add("D36: wedges rotation=0 (parallel)", case_d36())


def case_d37():
    """Wedges below base, not on top."""
    layers = perfect_pie()
    layers[1]["y"] = 1000
    layers[2]["y"] = 1100
    return H(layers)
add("D37: wedges below base", case_d37())


def case_d38():
    """Wedges above base (no overlap)."""
    layers = perfect_pie()
    layers[1]["y"] = -200
    layers[2]["y"] = -200
    return H(layers)
add("D38: wedges above base", case_d38())


def case_d39():
    """Wedges far right of base."""
    layers = perfect_pie()
    layers[1]["x"] = 1200
    layers[2]["x"] = 1300
    return H(layers)
add("D39: wedges far right", case_d39())


def case_d40():
    """Wedges shifted globally."""
    layers = perfect_pie()
    for l in layers:
        l["x"] += 300
        l["y"] += 200
    return H(layers)
add("D40: pie shifted globally", case_d40())


# ── E. Per-shape variants ───────────────────────────────────────────
def case_e41():
    """Wedges are 4-sided polygons (squares not triangles)."""
    layers = perfect_pie()
    layers[1]["sides"] = 4
    layers[2]["sides"] = 4
    return H(layers)
add("E41: wedges 4-sided", case_e41())


def case_e42():
    """Wedges are 6-sided hexagons."""
    layers = perfect_pie()
    layers[1]["sides"] = 6
    layers[2]["sides"] = 6
    return H(layers)
add("E42: wedges hexagons", case_e42())


def case_e43():
    """1 wedge triangle, 1 hexagon."""
    layers = perfect_pie()
    layers[2]["sides"] = 6
    return H(layers)
add("E43: 1 triangle + 1 hexagon wedge", case_e43())


def case_e44():
    """Base is rotated 45°."""
    layers = perfect_pie()
    layers[0]["rotation"] = 45
    return H(layers)
add("E44: base rotated 45°", case_e44())


def case_e45():
    """Wedges all rotated 45° (parallel)."""
    layers = perfect_pie()
    layers[1]["rotation"] = 45
    layers[2]["rotation"] = 45
    return H(layers)
add("E45: wedges parallel rotation 45°", case_e45())


def case_e46():
    """Base mirrored."""
    layers = perfect_pie()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E46: base mirrored", case_e46())


def case_e47():
    """Wedge 1 mirrored."""
    layers = perfect_pie()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E47: wedge mirrored", case_e47())


def case_e48():
    """Base is square-ish (300×305, just outside circle tol of 3)."""
    layers = perfect_pie()
    layers[0]["h"] = 305
    return H(layers)
add("E48: base 300×305 (slightly oval)", case_e48())


def case_e49():
    """Base is ellipse 300×400 (clearly oval)."""
    layers = perfect_pie()
    layers[0]["h"] = 400
    return H(layers)
add("E49: base 300×400 (oval)", case_e49())


def case_e50():
    """Wedges have cornerRadius (round corners)."""
    layers = perfect_pie()
    layers[1]["cornerRadius"] = 30
    layers[2]["cornerRadius"] = 30
    return H(layers)
add("E50: wedges with corner radius", case_e50())


# ── F. Subcomponent variants ────────────────────────────────────────
def case_f51():
    """Both wedges same exact rotation."""
    layers = perfect_pie()
    layers[1]["rotation"] = 60
    layers[2]["rotation"] = 60
    return H(layers)
add("F51: wedges same rotation 60°", case_f51())


def case_f52():
    """Base under wedges (z-order swapped, base drawn last)."""
    layers = perfect_pie()
    base = layers.pop(0)
    layers.append(base)
    return H(layers)
add("F52: base drawn last (on top of wedges)", case_f52())


def case_f53():
    """All 3 same color (teal)."""
    layers = perfect_pie(base=TEAL, w1=TEAL, w2=TEAL)
    return H(layers)
add("F53: all 3 teal (no contrast)", case_f53())


def case_f54():
    """Wedges have 5 colors stacked fills."""
    layers = perfect_pie()
    for l in layers[1:]:
        l["fills"] = [
            {"kind": "solid", "color": {"r": 0.95, "g": 0.4, "b": 0.4, "a": 1}, "opacity": 1, "visible": True},
            {"kind": "solid", "color": {"r": 0.95, "g": 0.85, "b": 0.2, "a": 1}, "opacity": 0.5, "visible": True},
            {"kind": "solid", "color": {"r": 0, "g": 0.6, "b": 0.6, "a": 1}, "opacity": 0.5, "visible": True},
        ]
    return H(layers)
add("F54: wedges with 3 stacked fills", case_f54())


def case_f55():
    """Wedge 1 is white, wedge 2 is white."""
    layers = perfect_pie(w1=WHITE, w2=WHITE)
    return H(layers)
add("F55: wedges both white", case_f55())


def case_f56():
    """Wedges have transparent fills (opacity 0.05)."""
    layers = perfect_pie()
    for l in layers[1:]:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("F56: wedges 0.05 opacity", case_f56())


def case_f57():
    """3 distinct teal-like colors (technically distinct but all teal-like)."""
    NEAR_TEAL_1 = (0.05, 0.6, 0.6)
    NEAR_TEAL_2 = (0.0, 0.55, 0.6)
    NEAR_TEAL_3 = (0.0, 0.6, 0.55)
    layers = perfect_pie(base=NEAR_TEAL_1, w1=NEAR_TEAL_2, w2=NEAR_TEAL_3)
    return H(layers)
add("F57: 3 near-teal colors (no contrast)", case_f57())


def case_f58():
    """Wedges concentric on base (no rotation differentiation)."""
    layers = perfect_pie()
    layers[1]["x"] = 470
    layers[1]["y"] = 470
    layers[1]["w"] = 60
    layers[1]["h"] = 60
    layers[1]["rotation"] = 0
    layers[2]["x"] = 470
    layers[2]["y"] = 470
    layers[2]["w"] = 60
    layers[2]["h"] = 60
    layers[2]["rotation"] = 0
    return H(layers)
add("F58: wedges concentric small", case_f58())


def case_f59():
    """Wedges share same color (only 2 distinct, not 3)."""
    layers = perfect_pie(w1=W1, w2=W1)
    return H(layers)
add("F59: 2 distinct colors (teal + 1 wedge color)", case_f59())


def case_f60():
    """Single solid white wedges (look invisible on white frame)."""
    layers = perfect_pie(base=TEAL, w1=WHITE, w2=WHITE)
    return H(layers)
add("F60: white wedges (no contrast)", case_f60())


# ── G. Frame variants ───────────────────────────────────────────────
def case_g61():
    layers = perfect_pie()
    return H(layers, in_frame=True)
add("G61: pie in frame (control)", case_g61())


def case_g62():
    layers = perfect_pie()
    frame = make_frame(layers, w=1000, h=1000)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G62: frame rotated 45°", case_g62())


def case_g63():
    """Pie split across 2 frames."""
    layers = perfect_pie()
    f1 = make_frame([layers[0]], w=1000, h=1000)
    f2 = make_frame(layers[1:], w=1000, h=1000)
    return make_log([f1, f2], evt())
add("G63: pie split across 2 frames", case_g63())


def case_g64():
    layers = perfect_pie()
    inner = make_frame(layers, w=800, h=800)
    outer = make_frame([inner], w=1200, h=1200)
    return make_log([outer], evt())
add("G64: nested frames", case_g64())


def case_g65():
    """No frame at all."""
    return make_log(perfect_pie(), evt())
add("G65: no frame (page only)", case_g65())


def case_g66():
    layers = perfect_pie()
    frame = make_frame(layers, w=1000, h=1000)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return make_log([frame], evt())
add("G66: frame image fill", case_g66())


def case_g67():
    layers = perfect_pie()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G67: frame too small for pie", case_g67())


def case_g68():
    """Pie in 2nd of 3 frames."""
    f1 = make_frame([], w=1000, h=1000)
    f2 = make_frame(perfect_pie(), w=1000, h=1000)
    f3 = make_frame([], w=1000, h=1000)
    return make_log([f1, f2, f3], evt())
add("G68: 3 frames, pie in middle", case_g68())


def case_g69():
    layers = perfect_pie()
    frame = make_frame(layers, x=500, y=300, w=1000, h=1000)
    return make_log([frame], evt())
add("G69: frame translated", case_g69())


def case_g70():
    """Frame too small."""
    layers = perfect_pie()
    frame = make_frame(layers, w=100, h=100)
    return make_log([frame], evt())
add("G70: tiny frame 100×100", case_g70())


# ── H. Tools / events ───────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())


def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(40)]))
add("H72: 40 undo events", case_h72())


def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_ellipse"),
           make_event("create_polygon"),
           make_event("create_polygon")]
    return H(evts=sem)
add("H73: only rectangle tool_change (wrong)", case_h73())


def case_h74():
    sem = [make_event("session_start"),
           make_event("create_ellipse"),
           make_event("create_polygon"),
           make_event("create_polygon")]
    return H(evts=sem)
add("H74: 0 tool_change events (keyboard)", case_h74())


def case_h75():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted a star", case_h75())


def case_h76():
    return H(evts=evt(polygon=8))  # too many polygon events
add("H76: 8 create_polygon events", case_h76())


def case_h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", case_h77())


def case_h78():
    return H(evts=evt(polygon=0, ellipse=0))
add("H78: no create events at all", case_h78())


def case_h79():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: used align tool", case_h79())


def case_h80():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: used distribute tool", case_h80())


# ── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_pie()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("I81: pie inside group", case_i81())


def case_i82():
    layers = perfect_pie()
    f1 = make_frame(layers[:1], w=1000, h=1000)
    f2 = make_frame(layers[1:], w=1000, h=1000)
    return make_log([f1, f2], evt())
add("I82: pie split across 2 frames", case_i82())


def case_i83():
    layers = perfect_pie()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: pie inside section", case_i83())


def case_i84():
    layers = perfect_pie()
    frame = make_frame([layers[0]], w=1000, h=1000)
    return make_log([frame, *layers[1:]], evt())
add("I84: base in frame, wedges on page", case_i84())


def case_i85():
    layers = perfect_pie()
    f3 = make_frame(layers, w=1000, h=1000)
    f2 = make_frame([f3], w=1000, h=1000)
    f1 = make_frame([f2], w=1000, h=1000)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    layers = perfect_pie()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: pie inside component", case_i86())


def case_i87():
    layers = perfect_pie()
    frame = make_frame(layers, w=1000, h=1000)
    page1 = {"id": "p1", "children": [],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    page2 = {"id": "p2", "children": [frame],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I87: pie on page 2 (multi-page)", case_i87())


def case_i88():
    """Each shape in own frame."""
    layers = perfect_pie()
    frames = [make_frame([s], w=1000, h=1000) for s in layers]
    return make_log(frames, evt())
add("I88: each shape in its own frame", case_i88())


def case_i89():
    """Pie deep inside group inside frame inside group."""
    layers = perfect_pie()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([g], w=1000, h=1000)
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [frame]}
    return make_log([g2], evt())
add("I89: pie deep in group/frame/group", case_i89())


def case_i90():
    layers = perfect_pie()
    return make_log(layers, evt())
add("I90: pie page-only (no frame)", case_i90())


# ── J. Bizarre ──────────────────────────────────────────────────────
def case_j91():
    layers = perfect_pie()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J91: base mirrored", case_j91())


def case_j92():
    layers = perfect_pie()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("J92: all rotated 180°", case_j92())


def case_j93():
    """All shapes overlapping."""
    layers = perfect_pie()
    layers[1]["x"] = 350
    layers[1]["y"] = 350
    layers[1]["w"] = 300
    layers[1]["h"] = 300
    layers[2]["x"] = 350
    layers[2]["y"] = 350
    layers[2]["w"] = 300
    layers[2]["h"] = 300
    return H(layers)
add("J93: wedges = base size", case_j93())


def case_j94():
    return make_log([], [make_event("session_start")])
add("J94: empty document", case_j94())


def case_j95():
    return make_log([{"id": "f1", "type": "frame", "x": 0, "y": 0, "w": 1000, "h": 1000,
                       "fills": [], "strokes": [], "effects": [], "children": []}],
                     [make_event("session_start")])
add("J95: empty frame", case_j95())


def case_j96():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=BLUE)
    text["content"] = "pie chart"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J96: text 'pie chart'", case_j96())


def case_j97():
    """Wedges as stars (not polygons)."""
    layers = perfect_pie()[:1]
    layers.append(make_layer("star", x=470, y=350, w=60, h=300, fill=W1, points=5, innerRatio=0.4))
    layers.append(make_layer("star", x=470, y=350, w=60, h=300, fill=W2, points=5, innerRatio=0.4))
    return H(layers, evts=evt(polygon=0))
add("J97: wedges as stars", case_j97())


def case_j98():
    """All 0×0 (no shape)."""
    layers = perfect_pie()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J98: all 0×0", case_j98())


def case_j99():
    """Negative coords."""
    layers = perfect_pie()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 1000
    return H(layers)
add("J99: negative coords", case_j99())


def case_j100():
    """Perfect control."""
    return H()
add("J100: perfect pie (control)", case_j100())


# ── Run ─────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

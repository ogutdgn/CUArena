"""100 edge cases for task 35 (honeycomb) — runs all and prints a sorted score table."""
from __future__ import annotations
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, BLACK, WHITE, RED, GREEN, ORANGE, PURPLE, GOLD,
)
BLUE = (0.2, 0.4, 0.85)
from tasks import task_35_honeycomb as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
YELLOW_HEX = (1.0, 0.85, 0.2)


def evt(polygon=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_honeycomb(n=4, side=80, fill=YELLOW_HEX, stroke=BLACK, sides=6, weight=1):
    """4 yellow hexagons in 2×2 offset honeycomb tiling."""
    layers = []
    for i in range(n):
        r, c = divmod(i, 2)
        x_offset = (side / 2) if r % 2 else 0
        layers.append(L("polygon", x=100 + c * side * 1.2 + x_offset,
                        y=100 + r * side, w=side, h=side, fill=fill,
                        strokes=[make_stroke(rgb=stroke, weight=weight)],
                        sides=sides))
    return layers


CASES = []


def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, in_frame=False):
    if layers is None: layers = perfect_honeycomb()
    if in_frame:
        frame = make_frame(layers, w=800, h=800)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ── A. Counts ───────────────────────────────────────────────────────
def case_a1(): return H(perfect_honeycomb(n=5), evts=evt(polygon=5))
add("A1: 5 hexagons (extra)", case_a1())


def case_a2(): return H(perfect_honeycomb(n=3), evts=evt(polygon=3))
add("A2: 3 hexagons", case_a2())


def case_a3(): return H(perfect_honeycomb(n=8), evts=evt(polygon=8))
add("A3: 8 hexagons (doubled)", case_a3())


def case_a4(): return H(perfect_honeycomb(n=2), evts=evt(polygon=2))
add("A4: 2 hexagons", case_a4())


def case_a5(): return H([], evts=evt(polygon=0))
add("A5: 0 hexagons", case_a5())


def case_a6(): return H(perfect_honeycomb(n=1), evts=evt(polygon=1))
add("A6: 1 hexagon", case_a6())


def case_a7():
    layers = perfect_honeycomb()
    layers.append(L("rectangle", 50, 50, 50, 50, RED))
    return H(layers)
add("A7: 4 hexagons + extra rect", case_a7())


def case_a8():
    layers = perfect_honeycomb()
    layers.append(L("ellipse", 600, 600, 50, 50, BLUE))
    return H(layers)
add("A8: 4 hexagons + extra ellipse", case_a8())


def case_a9():
    """Many extra polygons (not hexagons)."""
    layers = perfect_honeycomb()
    layers.extend([L("polygon", 500 + i * 60, 50, 30, 30, RED, sides=5) for i in range(4)])
    return H(layers, evts=evt(polygon=8))
add("A9: 4 hexagons + 4 pentagons", case_a9())


def case_a10(): return H(perfect_honeycomb(n=16), evts=evt(polygon=16))
add("A10: 16 hexagons (4x more)", case_a10())


# ── B. Colors / fills ────────────────────────────────────────────────
def case_b11(): return H(perfect_honeycomb(fill=RED))
add("B11: RED hexagons (not yellow)", case_b11())


def case_b12(): return H(perfect_honeycomb(stroke=WHITE))
add("B12: WHITE strokes (not black)", case_b12())


def case_b13():
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "honey.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: hexagons image fill", case_b13())


def case_b14():
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B14: hexagons no fill", case_b14())


def case_b15():
    layers = perfect_honeycomb()
    for l in layers:
        l["strokes"] = []
    return H(layers)
add("B15: hexagons no stroke", case_b15())


def case_b16(): return H(perfect_honeycomb(fill=WHITE, stroke=WHITE))
add("B16: white on white (no contrast)", case_b16())


def case_b17():
    NEAR_YELLOW = (0.95, 0.85, 0.25)
    return H(perfect_honeycomb(fill=NEAR_YELLOW))
add("B17: near-yellow (within tol)", case_b17())


def case_b18():
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 1, "g": 0.8, "b": 0.2, "a": 1}},
            {"position": 1, "color": {"r": 1, "g": 0.6, "b": 0.0, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("B18: hexagons gradient fill", case_b18())


def case_b19():
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: hexagons fill opacity 0.1", case_b19())


def case_b20():
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"].extend([
            {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
            {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True}])
    return H(layers)
add("B20: hexagons stacked fills", case_b20())


# ── C. Sizing ────────────────────────────────────────────────────────
def case_c21(): return H(perfect_honeycomb(side=200))
add("C21: hexagons 200×200 (large)", case_c21())


def case_c22(): return H(perfect_honeycomb(side=10))
add("C22: hexagons 10×10 (tiny)", case_c22())


def case_c23():
    layers = perfect_honeycomb()
    layers[0]["w"] = 200
    layers[0]["h"] = 200
    return H(layers)
add("C23: 1 hexagon huge, 3 normal", case_c23())


def case_c24():
    """Hexagons mixed sizes."""
    sizes = [40, 80, 100, 120]
    layers = []
    for i, s in enumerate(sizes):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(L("polygon", x=100 + c * 100 + x_offset, y=100 + r * 100,
                        w=s, h=s, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("C24: hexagons varying sizes", case_c24())


def case_c25():
    """Hexagons squashed (200×60)."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 200
        l["h"] = 60
    return H(layers)
add("C25: hexagons 200×60 (squashed)", case_c25())


def case_c26():
    """Hexagons 1×1 degenerate."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 1
        l["h"] = 1
    return H(layers)
add("C26: hexagons 1×1", case_c26())


def case_c27(): return H(perfect_honeycomb(side=82))
add("C27: hexagons 82×82 (within tol)", case_c27())


def case_c28(): return H(perfect_honeycomb(side=85))
add("C28: hexagons 85×85 (slightly off tol)", case_c28())


def case_c29(): return H(perfect_honeycomb(weight=10))
add("C29: hexagons 10px stroke", case_c29())


def case_c30(): return H(perfect_honeycomb(weight=0))
add("C30: hexagons 0px stroke (invisible)", case_c30())


# ── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Hexagons in a row (not 2x2)."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=100 + i * 120, y=200, w=80, h=80,
                        fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D31: hexagons in a row", case_d31())


def case_d32():
    """Hexagons stacked vertically."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=200, y=100 + i * 100, w=80, h=80,
                        fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D32: hexagons in column", case_d32())


def case_d33():
    """Hexagons in regular 2x2 grid (no offset)."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        layers.append(L("polygon", x=100 + c * 100, y=100 + r * 100,
                        w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D33: regular grid (no honeycomb offset)", case_d33())


def case_d34(): return H(perfect_honeycomb())
add("D34: perfect 2x2 honeycomb (control)", case_d34())


def case_d35():
    """Hexagons piled at one point."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=200, y=200, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D35: hexagons all at same point", case_d35())


def case_d36():
    """Hexagons at corners."""
    pos = [(50, 50), (1000, 50), (50, 1000), (1000, 1000)]
    layers = []
    for x, y in pos:
        layers.append(L("polygon", x=x, y=y, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D36: hexagons in 4 corners", case_d36())


def case_d37():
    """Hexagons offset in wrong direction."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        y_offset = 40 if c % 2 else 0  # offset y by column
        layers.append(L("polygon", x=100 + c * 100, y=100 + r * 100 + y_offset,
                        w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D37: y-offset honeycomb (wrong direction)", case_d37())


def case_d38():
    """Hexagons in 4x1 row with offset."""
    layers = []
    for i in range(4):
        x_offset = 40 if i % 2 else 0
        layers.append(L("polygon", x=100 + i * 80, y=200 + x_offset,
                        w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("D38: 4x1 row (zigzag)", case_d38())


def case_d39():
    """Hexagons shifted globally."""
    layers = perfect_honeycomb()
    for l in layers:
        l["x"] += 500
        l["y"] += 300
    return H(layers)
add("D39: honeycomb shifted globally", case_d39())


def case_d40():
    """Hexagons at negative coords."""
    layers = perfect_honeycomb()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 1000
    return H(layers)
add("D40: hexagons at negative coords", case_d40())


# ── E. Per-shape variants ───────────────────────────────────────────
def case_e41(): return H(perfect_honeycomb(sides=5))  # pentagons
add("E41: pentagons (5 sides)", case_e41())


def case_e42(): return H(perfect_honeycomb(sides=4))  # squares
add("E42: 4-sided (squares)", case_e42())


def case_e43(): return H(perfect_honeycomb(sides=3))  # triangles
add("E43: triangles (3 sides)", case_e43())


def case_e44(): return H(perfect_honeycomb(sides=8))  # octagons
add("E44: octagons (8 sides)", case_e44())


def case_e45():
    """Hexagons all rotated 30°."""
    layers = perfect_honeycomb()
    for l in layers:
        l["rotation"] = 30
    return H(layers)
add("E45: hexagons rotated 30°", case_e45())


def case_e46():
    """Hexagons mirrored."""
    layers = perfect_honeycomb()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E46: hexagons mirrored", case_e46())


def case_e47():
    """Hexagons with cornerRadius."""
    layers = perfect_honeycomb()
    for l in layers:
        l["cornerRadius"] = 10
    return H(layers)
add("E47: hexagons with corner radius", case_e47())


def case_e48():
    """1 hexagon, 3 pentagons."""
    layers = perfect_honeycomb()
    for l in layers[1:]:
        l["sides"] = 5
    return H(layers)
add("E48: 1 hex + 3 pentagons (mixed)", case_e48())


def case_e49():
    """Hexagons 5×5 degenerate."""
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 5
        l["h"] = 5
    return H(layers)
add("E49: hexagons 5×5", case_e49())


def case_e50():
    """Hexagons rotated 60° each (random)."""
    layers = perfect_honeycomb()
    for i, l in enumerate(layers):
        l["rotation"] = i * 60
    return H(layers)
add("E50: hexagons random rotations", case_e50())


# ── F. Subcomponent variants ────────────────────────────────────────
def case_f51():
    """4 hexagons but 2 are pentagons/triangles."""
    layers = perfect_honeycomb()
    layers[0]["sides"] = 5
    layers[1]["sides"] = 3
    return H(layers)
add("F51: mixed polygon types", case_f51())


def case_f52():
    """Hexagons stroke missing on 2."""
    layers = perfect_honeycomb()
    layers[0]["strokes"] = []
    layers[2]["strokes"] = []
    return H(layers)
add("F52: 2 hexagons no stroke", case_f52())


def case_f53():
    """Hexagons different colors."""
    layers = perfect_honeycomb()
    colors = [YELLOW_HEX, RED, GREEN, BLUE]
    for l, c in zip(layers, colors):
        l["fills"][0]["color"] = {"r": c[0], "g": c[1], "b": c[2], "a": 1.0}
    return H(layers)
add("F53: 4 hexagons different colors", case_f53())


def case_f54():
    """Hexagons stacked fills."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"].append({"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True})
    return H(layers)
add("F54: hexagons 2 stacked fills", case_f54())


def case_f55():
    """Strokes dashed."""
    layers = perfect_honeycomb()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=1, dash={"dash": 4, "gap": 2})]
    return H(layers)
add("F55: strokes dashed", case_f55())


def case_f56():
    """Strokes 0.1px (basically invisible)."""
    return H(perfect_honeycomb(weight=0.1))
add("F56: strokes 0.1px (invisible)", case_f56())


def case_f57():
    """Hexagons opacity 0.5."""
    layers = perfect_honeycomb()
    for l in layers:
        l["opacity"] = 0.5
    return H(layers)
add("F57: hexagons opacity 0.5", case_f57())


def case_f58():
    """Hexagons fill alpha=0."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("F58: hexagons alpha=0", case_f58())


def case_f59():
    """Hexagons fill visible=False."""
    layers = perfect_honeycomb()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("F59: hexagons fill visible=False", case_f59())


def case_f60():
    """Hexagons all at single position (overlapping)."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=200, y=200, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("F60: hexagons all overlapping", case_f60())


# ── G. Frame variants ───────────────────────────────────────────────
def case_g61(): return H(in_frame=True)
add("G61: honeycomb in frame", case_g61())


def case_g62():
    layers = perfect_honeycomb()
    frame = make_frame(layers, w=800, h=800)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G62: frame rotated 45°", case_g62())


def case_g63():
    layers = perfect_honeycomb()
    f1 = make_frame(layers[:2], w=800, h=800)
    f2 = make_frame(layers[2:], w=800, h=800)
    return make_log([f1, f2], evt())
add("G63: hexagons split across 2 frames", case_g63())


def case_g64():
    layers = perfect_honeycomb()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=800, h=800)
    return make_log([outer], evt())
add("G64: nested frames", case_g64())


def case_g65():
    layers = perfect_honeycomb()
    return make_log(layers, evt())
add("G65: no frame", case_g65())


def case_g66():
    layers = perfect_honeycomb()
    frame = make_frame(layers, w=800, h=800, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return make_log([frame], evt())
add("G66: frame image fill", case_g66())


def case_g67():
    layers = perfect_honeycomb()
    frame = make_frame(layers, w=800, h=800)
    frame["strokes"] = [make_stroke(rgb=BLUE, weight=4)]
    return make_log([frame], evt())
add("G67: frame with stroke", case_g67())


def case_g68():
    f1 = make_frame([], w=800, h=800)
    f2 = make_frame(perfect_honeycomb(), w=800, h=800)
    return make_log([f1, f2], evt())
add("G68: 2 frames, honeycomb in 2nd", case_g68())


def case_g69():
    layers = perfect_honeycomb()
    frame = make_frame(layers, x=300, y=200, w=800, h=800)
    return make_log([frame], evt())
add("G69: frame translated", case_g69())


def case_g70():
    layers = perfect_honeycomb()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G70: frame too small", case_g70())


# ── H. Tools / events ───────────────────────────────────────────────
def case_h71(): return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())


def case_h72(): return H(evts=evt(extras=[make_event("undo") for _ in range(40)]))
add("H72: 40 undo events", case_h72())


def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_polygon")] * 4)
    return H(evts=sem)
add("H73: rectangle tool used (wrong)", case_h73())


def case_h74():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_polygon")] * 4)
    return H(evts=sem)
add("H74: 0 tool_change events", case_h74())


def case_h75():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted star", case_h75())


def case_h76(): return H(evts=evt(polygon=8))
add("H76: 8 create_polygon", case_h76())


def case_h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", case_h77())


def case_h78(): return H(evts=evt(polygon=0))
add("H78: 0 create_polygon", case_h78())


def case_h79(): return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: used align tool", case_h79())


def case_h80(): return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: used distribute tool", case_h80())


# ── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_honeycomb()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("I81: hexagons in group", case_i81())


def case_i82():
    layers = perfect_honeycomb()
    f1 = make_frame(layers[:2], w=800, h=800)
    f2 = make_frame(layers[2:], w=800, h=800)
    return make_log([f1, f2], evt())
add("I82: hexagons split frames", case_i82())


def case_i83():
    layers = perfect_honeycomb()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 800, "h": 800,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: hexagons in section", case_i83())


def case_i84():
    layers = perfect_honeycomb()
    frame = make_frame(layers[:2], w=800, h=800)
    return make_log([frame, *layers[2:]], evt())
add("I84: 2 hexagons in frame, 2 on page", case_i84())


def case_i85():
    layers = perfect_honeycomb()
    f3 = make_frame(layers, w=800, h=800)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=800, h=800)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    layers = perfect_honeycomb()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: hexagons in component", case_i86())


def case_i87():
    layers = perfect_honeycomb()
    page1 = {"id": "p1", "children": [],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    page2 = {"id": "p2", "children": layers,
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I87: hexagons on page 2", case_i87())


def case_i88():
    layers = perfect_honeycomb()
    frames = [make_frame([s], w=800, h=800) for s in layers]
    return make_log(frames, evt())
add("I88: each hexagon in own frame", case_i88())


def case_i89():
    layers = perfect_honeycomb()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g]}
    return make_log([g2], evt())
add("I89: hexagons in nested groups", case_i89())


def case_i90():
    """Hexagons inside frame inside group."""
    layers = perfect_honeycomb()
    frame = make_frame(layers, w=800, h=800)
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": [frame]}
    return make_log([g], evt())
add("I90: frame in group", case_i90())


# ── J. Bizarre ──────────────────────────────────────────────────────
def case_j91(): return H([])
add("J91: empty layers", case_j91())


def case_j92():
    layers = perfect_honeycomb()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J92: all 0×0", case_j92())


def case_j93():
    """Text 'honeycomb'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=BLUE)
    text["content"] = "honeycomb"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J93: text 'honeycomb'", case_j93())


def case_j94():
    """4 stars instead of polygons."""
    layers = []
    for i in range(4):
        r, c = divmod(i, 2)
        x_offset = 40 if r % 2 else 0
        layers.append(make_layer("star", x=100 + c * 100 + x_offset,
                                  y=100 + r * 80, w=80, h=80,
                                  fill=YELLOW_HEX, points=6, innerRatio=0.4))
    return H(layers, evts=evt(polygon=0))
add("J94: stars instead of hexagons", case_j94())


def case_j95():
    """All shapes overlap completely."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", x=200, y=200, w=80, h=80, fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers)
add("J95: all hexagons same position", case_j95())


def case_j96():
    """Hexagons at very different rotations."""
    layers = perfect_honeycomb()
    layers[0]["rotation"] = 0
    layers[1]["rotation"] = 23
    layers[2]["rotation"] = 47
    layers[3]["rotation"] = 71
    return H(layers)
add("J96: hexagons random rotations", case_j96())


def case_j97():
    """Frame is gigantic, hexagons tiny."""
    layers = perfect_honeycomb(side=20)
    frame = make_frame(layers, w=10000, h=10000)
    return make_log([frame], evt())
add("J97: huge frame, tiny hexagons", case_j97())


def case_j98():
    """3x1 row instead of 2x2."""
    layers = []
    for i in range(3):
        layers.append(L("polygon", x=100 + i * 100, y=200, w=80, h=80,
                        fill=YELLOW_HEX,
                        strokes=[make_stroke(rgb=BLACK, weight=1)], sides=6))
    return H(layers, evts=evt(polygon=3))
add("J98: 3x1 row", case_j98())


def case_j99():
    """Hexagons at negative coords."""
    layers = perfect_honeycomb()
    for l in layers:
        l["x"] -= 5000
        l["y"] -= 5000
    return H(layers)
add("J99: hexagons negative coords", case_j99())


def case_j100(): return H()
add("J100: perfect honeycomb (control)", case_j100())


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

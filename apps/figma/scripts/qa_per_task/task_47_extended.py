"""100 edge cases for task 47 — sunburst stamp badge.

Prompt: 8-point warm-orange star + smaller centered cream circle on top.

Runs all and prints a sorted score table. Anything ≥ 0.95 that should fail = strict FP.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_47" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
# ─── Helpers ────────────────────────────────────────────────────────


def evt(star=1, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("tool_change", before="star", after="ellipse")]
    for _ in range(star):    sem.append(make_event("create_star"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_badge(cx=500, cy=500, star_size=240, circle_size=80,
                  star_color=WARM_ORANGE, circle_color=CREAM, points=8):
    star = L("star", cx-star_size/2, cy-star_size/2, star_size, star_size,
             star_color, points=points, innerRatio=0.5)
    circle = L("ellipse", cx-circle_size/2, cy-circle_size/2,
               circle_size, circle_size, circle_color)
    return [star, circle]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, in_frame=False):
    if layers is None: layers = perfect_badge()
    if in_frame:
        frame = make_frame(layers, w=1280, h=832, fill=(0.95, 0.95, 0.95))
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ────────────────────────────────────────────────
def case_a1():
    layers = perfect_badge()
    layers.append(L("star", 100, 100, 100, 100, WARM_ORANGE, points=8, innerRatio=0.5))
    return H(layers, evts=evt(star=2))
add("A1: 2 stars (extra)", case_a1())

def case_a2():
    layers = perfect_badge()
    layers.append(L("ellipse", 100, 100, 60, 60, CREAM))
    return H(layers, evts=evt(ellipse=2))
add("A2: 2 ellipses (extra)", case_a2())

def case_a3():
    return H([L("ellipse", 460, 460, 80, 80, CREAM)], evts=evt(star=0, ellipse=1))
add("A3: only ellipse, no star", case_a3())

def case_a4():
    return H([L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)],
             evts=evt(star=1, ellipse=0))
add("A4: only star, no ellipse", case_a4())

def case_a5():
    return H([], evts=evt(star=0, ellipse=0))
add("A5: empty document", case_a5())

def case_a6():
    layers = perfect_badge()
    for i in range(2):
        layers.append(L("star", 100+i*100, 100, 50, 50, WARM_ORANGE, points=8, innerRatio=0.5))
    return H(layers, evts=evt(star=3))
add("A6: 3 stars total", case_a6())

def case_a7():
    layers = perfect_badge()
    for i in range(2):
        layers.append(L("ellipse", 100+i*100, 100, 30, 30, CREAM))
    return H(layers, evts=evt(ellipse=3))
add("A7: 3 ellipses total", case_a7())

def case_a8():
    layers = perfect_badge()
    layers.append(L("rectangle", 100, 100, 50, 50, GREEN))
    return H(layers, evts=evt(extras=[make_event("create_rectangle")]))
add("A8: extra rectangle (decorative)", case_a8())

def case_a9():
    layers = perfect_badge()
    layers.append(L("polygon", 100, 100, 50, 50, GREEN, sides=3))
    return H(layers, evts=evt(extras=[make_event("create_polygon")]))
add("A9: extra polygon", case_a9())

def case_a10():
    return H()  # control: perfect
add("A10: perfect (control)", case_a10())


# ─── B. Colors / fills (10) ────────────────────────────────────────
def case_b11():
    layers = perfect_badge()
    layers[0]["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B11: star image fill (not solid)", case_b11())

def case_b12():
    layers = perfect_badge()
    layers[1]["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B12: circle image fill", case_b12())

def case_b13():
    layers = perfect_badge()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 0.5, "b": 0.1, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0, "b": 0, "a": 1}}], "opacity": 1, "visible": True}]
    return H(layers)
add("B13: star has gradient fill", case_b13())

def case_b14():
    layers = perfect_badge()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=WARM_ORANGE, weight=4)]
    return H(layers)
add("B14: star stroke-only (no fill)", case_b14())

def case_b15():
    layers = perfect_badge()
    layers[1]["fills"] = []
    return H(layers)
add("B15: circle empty fills", case_b15())

def case_b16():
    layers = perfect_badge()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B16: star fill opacity=0.1", case_b16())

def case_b17():
    layers = perfect_badge()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B17: star fill alpha=0 (invisible)", case_b17())

def case_b18():
    layers = perfect_badge()
    layers[1]["opacity"] = 0.0
    return H(layers)
add("B18: circle layer opacity=0", case_b18())

def case_b19():
    layers = perfect_badge()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("B19: star fill visible=False", case_b19())

def case_b20():
    layers = perfect_badge()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.5, "visible": True},
    ])
    return H(layers)
add("B20: star has 3 stacked fills (first solid)", case_b20())


# ─── C. Sizing (10) ────────────────────────────────────────────────
def case_c21():
    layers = perfect_badge(star_size=20, circle_size=10)
    return H(layers)
add("C21: star 20×20 tiny", case_c21())

def case_c22():
    layers = perfect_badge(star_size=2000, circle_size=600)
    return H(layers)
add("C22: huge star 2000×2000", case_c22())

def case_c23():
    layers = perfect_badge()
    layers[0]["w"] = 240
    layers[0]["h"] = 60
    return H(layers)
add("C23: star 240×60 squashed", case_c23())

def case_c24():
    layers = perfect_badge()
    layers[1]["w"] = 200
    layers[1]["h"] = 30
    return H(layers)
add("C24: circle 200×30 oval", case_c24())

def case_c25():
    layers = perfect_badge(circle_size=400)  # bigger than star (240)
    return H(layers)
add("C25: circle larger than star", case_c25())

def case_c26():
    layers = perfect_badge(star_size=80, circle_size=80)
    return H(layers)
add("C26: circle equal to star", case_c26())

def case_c27():
    layers = perfect_badge(circle_size=235)  # circle nearly same as star
    return H(layers)
add("C27: circle nearly same size as star", case_c27())

def case_c28():
    layers = perfect_badge(circle_size=1)  # 1×1 circle
    return H(layers)
add("C28: circle 1×1 degenerate", case_c28())

def case_c29():
    layers = perfect_badge(star_size=1)  # 1×1 star
    return H(layers)
add("C29: star 1×1 degenerate", case_c29())

def case_c30():
    layers = perfect_badge(circle_size=78)  # just inside (32% of star)
    return H(layers)
add("C30: circle 78px (just inside)", case_c30())


# ─── D. Position (10) ──────────────────────────────────────────────
def case_d31():
    layers = perfect_badge()
    layers[1]["x"] += 200; layers[1]["y"] += 200
    return H(layers)
add("D31: circle 200px off-center", case_d31())

def case_d32():
    layers = perfect_badge()
    layers[1]["x"] -= 500; layers[1]["y"] -= 500
    return H(layers)
add("D32: circle far above-left of star", case_d32())

def case_d33():
    layers = perfect_badge()
    layers[1]["x"] = layers[0]["x"] - 50; layers[1]["y"] = layers[0]["y"] - 50
    return H(layers)
add("D33: circle outside star top-left", case_d33())

def case_d34():
    layers = perfect_badge()
    layers[1]["x"] = layers[0]["x"]; layers[1]["y"] = layers[0]["y"]
    return H(layers)
add("D34: circle at star top-left corner", case_d34())

def case_d35():
    layers = perfect_badge()
    layers[1]["x"] += 80; layers[1]["y"] = layers[1]["y"]  # circle off-center x only
    return H(layers)
add("D35: circle offset x but matching y", case_d35())

def case_d36():
    layers = perfect_badge()
    layers[1]["y"] += 80
    return H(layers)
add("D36: circle offset y but matching x", case_d36())

def case_d37():
    layers = perfect_badge()
    cx, cy = 500, 500
    layers[1]["x"] = cx + 120 - 40
    layers[1]["y"] = cy + 120 - 40  # circle at lower-right corner, on edge
    return H(layers)
add("D37: circle on star edge", case_d37())

def case_d38():
    layers = perfect_badge()
    for l in layers: l["x"] += 2000
    return H(layers)
add("D38: badge way off-canvas right", case_d38())

def case_d39():
    layers = perfect_badge()
    for l in layers: l["x"] -= 2000
    return H(layers)
add("D39: badge way off-canvas left", case_d39())

def case_d40():
    layers = perfect_badge()
    layers[1]["x"] = layers[0]["x"] + layers[0]["w"]  # circle outside star, right
    return H(layers)
add("D40: circle entirely outside star", case_d40())


# ─── E. Per-shape variants (10) ────────────────────────────────────
def case_e41():
    return H(perfect_badge(points=4))
add("E41: star has 4 points", case_e41())

def case_e42():
    return H(perfect_badge(points=5))
add("E42: star has 5 points", case_e42())

def case_e43():
    return H(perfect_badge(points=6))
add("E43: star has 6 points", case_e43())

def case_e44():
    return H(perfect_badge(points=12))
add("E44: star has 12 points", case_e44())

def case_e45():
    layers = perfect_badge()
    layers[0]["rotation"] = 45
    return H(layers)
add("E45: star rotated 45°", case_e45())

def case_e46():
    layers = perfect_badge()
    layers[0]["rotation"] = 22.5  # half star angle
    return H(layers)
add("E46: star rotated 22.5°", case_e46())

def case_e47():
    layers = perfect_badge()
    layers[0]["rotation"] = 4
    return H(layers)
add("E47: star rotated 4° (subtle)", case_e47())

def case_e48():
    layers = perfect_badge()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E48: star mirrored (scaleX=-1)", case_e48())

def case_e49():
    layers = perfect_badge()
    layers[0]["innerRatio"] = 0.05  # super spiky
    return H(layers)
add("E49: star super spiky (innerRatio=0.05)", case_e49())

def case_e50():
    layers = perfect_badge()
    layers[0]["innerRatio"] = 0.95  # almost circular
    return H(layers)
add("E50: star almost circular (innerRatio=0.95)", case_e50())


# ─── F. Subcomponent (circle) variants (10) ─────────────────────────
def case_f51():
    layers = perfect_badge()
    layers[1]["w"] = 80; layers[1]["h"] = 60  # not circular
    return H(layers)
add("F51: circle is 80×60 oval", case_f51())

def case_f52():
    layers = perfect_badge()
    layers[1]["rotation"] = 45  # ellipse rotated
    return H(layers)
add("F52: circle rotated 45°", case_f52())

def case_f53():
    layers = perfect_badge()
    layers[1]["scaleX"] = -1
    return H(layers)
add("F53: circle scaleX=-1", case_f53())

def case_f54():
    layers = perfect_badge()
    layers[1]["fills"] = []
    layers[1]["strokes"] = [make_stroke(rgb=CREAM, weight=4)]
    return H(layers)
add("F54: circle stroke-only no fill", case_f54())

def case_f55():
    layers = perfect_badge()
    layers[1]["w"] = 100; layers[1]["h"] = 100
    layers[1]["x"] = layers[0]["x"] + layers[0]["w"]/2 - 50
    layers[1]["y"] = layers[0]["y"] + layers[0]["h"]/2 - 50
    return H(layers)
add("F55: circle 100x100 (slightly off-center? still centered)", case_f55())

def case_f56():
    layers = perfect_badge()
    layers[1]["cornerRadius"] = 0  # ellipse with cornerRadius (no effect, but)
    return H(layers)
add("F56: circle cornerRadius=0 (no-op)", case_f56())

def case_f57():
    layers = perfect_badge(circle_size=300)  # circle bigger than star
    layers[1]["x"] = 350; layers[1]["y"] = 350
    return H(layers)
add("F57: circle 300x300 way larger than star", case_f57())

def case_f58():
    layers = perfect_badge()
    layers[1]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("F58: circle invisible (alpha=0)", case_f58())

def case_f59():
    layers = perfect_badge()
    layers[1]["visible"] = False
    return H(layers)
add("F59: circle visible=False", case_f59())

def case_f60():
    layers = perfect_badge()
    layers[1]["opacity"] = 0.05
    return H(layers)
add("F60: circle opacity=0.05", case_f60())


# ─── G. Frame variants (10) ─────────────────────────────────────────
def case_g61():
    return H(in_frame=True)
add("G61: in 1280×832 frame", case_g61())

def case_g62():
    layers = perfect_badge()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G62: frame rotated 45°", case_g62())

def case_g63():
    layers = perfect_badge()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G63: nested frames", case_g63())

def case_g64():
    f1 = make_frame([], w=600, h=600)
    f2 = make_frame(perfect_badge(), w=600, h=600)
    return make_log([f1, f2], evt())
add("G64: 2 frames, badge in 2nd", case_g64())

def case_g65():
    layers = perfect_badge()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G65: frame has stroke", case_g65())

def case_g66():
    layers = perfect_badge()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G66: frame has image fill", case_g66())

def case_g67():
    layers = perfect_badge()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    layers = perfect_badge()
    frame = make_frame(layers, w=1, h=1)  # tiny frame
    return make_log([frame], evt())
add("G68: 1×1 frame", case_g68())

def case_g69():
    return H(in_frame=True)
add("G69: in frame (control)", case_g69())

def case_g70():
    layers = perfect_badge()
    layers[0]["w"] = 1500; layers[0]["h"] = 1000
    return H(layers, in_frame=True)
add("G70: star larger than frame", case_g70())


# ─── H. Tools / events (10) ─────────────────────────────────────────
def case_h71():
    extras = [make_event("undo") for _ in range(40)]
    return H(evts=evt(extras=extras))
add("H71: 40 undo events", case_h71())

def case_h72():
    extras = [make_event("delete") for _ in range(20)]
    return H(evts=evt(extras=extras))
add("H72: 20 delete events", case_h72())

def case_h73():
    extras = [make_event("align_layers", axis="center_y"),
              make_event("align_layers", axis="center_x")]
    return H(evts=evt(extras=extras))
add("H73: align_layers (used)", case_h73())

def case_h74():
    sem = [make_event("session_start")]  # no tool change
    sem.append(make_event("create_star"))
    sem.append(make_event("create_ellipse"))
    return H(evts=sem)
add("H74: 0 tool_change events", case_h74())

def case_h75():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.append(make_event("create_rectangle"))
    sem.append(make_event("create_ellipse"))
    layers = perfect_badge()
    return H(layers, evts=sem)
add("H75: created rect not star (tool mismatch)", case_h75())

def case_h76():
    extras = [make_event("create_star"), make_event("create_star"),
              make_event("delete"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H76: extra create+delete cycles", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse"),
           make_event("tool_change", before="ellipse", after="star"),
           make_event("create_star")]  # reverse order
    return H(evts=sem)
add("H77: ellipse before star creation", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("set_fill_color")] * 10))
add("H78: 10 set_fill_color events", case_h78())

def case_h79():
    return H(evts=evt(star=3, ellipse=3))
add("H79: 3 create_star + 3 create_ellipse events but only 1+1 layers", case_h79())

def case_h80():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("create_star"),
           make_event("session_end")]
    return H(evts=sem)
add("H80: missing ellipse tool/event", case_h80())


# ─── I. Hierarchy (10) ──────────────────────────────────────────────
def case_i81():
    layers = perfect_badge()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("I81: badge inside group", case_i81())

def case_i82():
    star, circle = perfect_badge()
    f1 = make_frame([star], w=600, h=600)
    f2 = make_frame([circle], w=600, h=600)
    return make_log([f1, f2], evt())
add("I82: star + circle in different frames", case_i82())

def case_i83():
    layers = perfect_badge()
    sec = {"id": "sec1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
           "fills": [], "children": layers}
    return make_log([sec], evt())
add("I83: badge in section", case_i83())

def case_i84():
    layers = perfect_badge()
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    layers = perfect_badge()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    page2 = {"id": "p2", "children": layers, "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: badge on page 2", case_i85())

def case_i86():
    layers = perfect_badge()
    component = {"id": "comp1", "type": "component", "x": 0, "y": 0, "w": 1000, "h": 1000,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I86: badge inside component", case_i86())

def case_i87():
    star, circle = perfect_badge()
    group_inner = {"id": "g_inner", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                   "fills": [], "children": [circle]}
    group_outer = {"id": "g_outer", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                   "fills": [], "children": [star, group_inner]}
    return make_log([group_outer], evt())
add("I87: nested groups", case_i87())

def case_i88():
    layers = perfect_badge()
    return make_log(layers, evt())
add("I88: bare on page (no frame)", case_i88())

def case_i89():
    layers = perfect_badge()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("I89: in frame (canonical)", case_i89())

def case_i90():
    star, circle = perfect_badge()
    return make_log([star, circle], evt())
add("I90: bare layers (control)", case_i90())


# ─── J. Bizarre (10) ────────────────────────────────────────────────
def case_j91():
    layers = perfect_badge()
    layers[0]["rotation"] = 180
    return H(layers)
add("J91: star rotated 180°", case_j91())

def case_j92():
    layers = perfect_badge()
    layers[0]["x"] = -1000; layers[0]["y"] = -1000
    layers[1]["x"] = -1000 + 80; layers[1]["y"] = -1000 + 80
    return H(layers)
add("J92: badge with negative coords", case_j92())

def case_j93():
    layers = perfect_badge()
    layers[0]["w"] = 1; layers[0]["h"] = 1  # star 1×1
    layers[1]["w"] = 1; layers[1]["h"] = 1
    return H(layers)
add("J93: both shapes 1×1 piled", case_j93())

def case_j94():
    layers = [L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)] * 1
    layers.append(L("ellipse", 460, 460, 80, 80, CREAM))
    layers.append(L("ellipse", 460, 460, 80, 80, CREAM))  # duplicate identical
    return H(layers, evts=evt(ellipse=2))
add("J94: 2 identical ellipses stacked", case_j94())

def case_j95():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "sunburst"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'sunburst' instead of shapes", case_j95())

def case_j96():
    layers = perfect_badge()
    layers[0]["scaleY"] = -1  # vertically flipped
    return H(layers)
add("J96: star scaleY=-1", case_j96())

def case_j97():
    star, circle = perfect_badge()
    star["x"] = 500; star["y"] = 500
    circle["x"] = 500; circle["y"] = 500
    return H([star, circle])
add("J97: same x,y top-left (not centered, but matching origins)", case_j97())

def case_j98():
    layers = perfect_badge(star_color=(0.95, 0.55, 0.15))  # near-but-different orange
    return H(layers)
add("J98: star near-warm-orange (within color tol)", case_j98())

def case_j99():
    layers = [L("star", 380, 380, 240, 240, WARM_ORANGE, points=8, innerRatio=0.5)]  # no ellipse
    layers.append(L("rectangle", 460, 460, 80, 80, CREAM))  # rectangle instead of ellipse
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]))
add("J99: rectangle instead of circle", case_j99())

def case_j100():
    return H()  # control: perfect
add("J100: perfect badge (control)", case_j100())


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

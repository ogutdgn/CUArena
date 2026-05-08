"""100 edge cases for task 42 (bell icon) — runs all and prints a sorted score table.

Task 42 prompt: pen-drawn bell silhouette (yellow-gold) + small clapper circle below
+ red badge circle in upper-right with 2px white stroke.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, GOLD, WHITE, RED, NAVY, GREEN, ORANGE, PINK, PURPLE,
)
from tasks import task_42_bell_icon as t
T = t.task

# ─── Helpers ────────────────────────────────────────────────────────
GRAY = (0.5, 0.5, 0.5)
RED_BADGE = (0.95, 0.20, 0.20)
DARK_GRAY = (0.30, 0.30, 0.30)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(vector=1, ellipse=2, set_fill=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bell():
    bell = L("vector", 540, 280, 200, 240, GOLD)
    clapper = L("ellipse", 620, 520, 40, 40, GOLD)
    badge = L("ellipse", 720, 280, 24, 24, RED_BADGE,
              strokes=[make_stroke(rgb=WHITE, weight=2)])
    return [bell, clapper, badge]


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bell()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_bell()
    layers.append(L("vector", 100, 100, 80, 80, GOLD))
    return H(layers, evts=evt(vector=2))
add("A1: 2 vectors (extra bell)", case_a1())

def case_a2():
    layers = perfect_bell()
    layers.append(L("ellipse", 100, 700, 30, 30, PINK))
    return H(layers, evts=evt(ellipse=3))
add("A2: 3 ellipses (extra dot)", case_a2())

def case_a3():
    layers = [perfect_bell()[0], perfect_bell()[2]]  # bell + badge only
    return H(layers, evts=evt(ellipse=1))
add("A3: 1 ellipse (missing clapper)", case_a3())

def case_a4():
    return H([], evts=evt(vector=0, ellipse=0))
add("A4: empty doc", case_a4())

def case_a5():
    layers = perfect_bell()[1:]  # no vector
    return H(layers, evts=evt(vector=0))
add("A5: no vector (bell missing)", case_a5())

def case_a6():
    layers = [perfect_bell()[0]]  # only bell
    return H(layers, evts=evt(ellipse=0))
add("A6: only bell vector", case_a6())

def case_a7():
    layers = perfect_bell()
    for i in range(3):
        layers.append(L("ellipse", 100 + i*60, 700, 20, 20, GREEN))
    return H(layers, evts=evt(ellipse=5))
add("A7: 5 ellipses (3 extra)", case_a7())

def case_a8():
    layers = perfect_bell() + [L("vector", 1000, 100, 60, 60, NAVY),
                                L("vector", 1100, 100, 60, 60, ORANGE)]
    return H(layers, evts=evt(vector=3))
add("A8: 3 vectors total", case_a8())

def case_a9():
    layers = perfect_bell()
    layers[0]["type"] = "rectangle"  # bell is now a rect
    return H(layers, evts=evt(vector=0))
add("A9: bell is a rectangle, no vector", case_a9())

def case_a10():
    layers = perfect_bell()
    layers.append(L("ellipse", 700, 600, 30, 30, GOLD))  # extra ellipse same color
    return H(layers, evts=evt(ellipse=3))
add("A10: 3 ellipses (extra clapper-like)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    layers = perfect_bell()
    layers[0]["fills"] = [{"kind": "image", "src": "bell.jpg", "fit": "cover",
                           "opacity": 1, "visible": True}]
    return H(layers)
add("B11: bell has image fill (not solid)", case_b11())

def case_b12():
    layers = perfect_bell()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 0.8, "b": 0.1, "a": 1}},
        {"position": 1, "color": {"r": 0.5, "g": 0.4, "b": 0.05, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B12: bell gradient fill", case_b12())

def case_b13():
    layers = perfect_bell()
    layers[0]["fills"] = []  # bell no fill
    layers[0]["strokes"] = [make_stroke(rgb=GOLD, weight=4)]
    return H(layers)
add("B13: bell stroke-only", case_b13())

def case_b14():
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 200, 240, GRAY)  # bell gray, not gold
    return H(layers)
add("B14: bell gray (wrong color)", case_b14())

def case_b15():
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 200, 240, GOLD)
    layers[1] = L("ellipse", 620, 520, 40, 40, GOLD)
    layers[2] = L("ellipse", 720, 280, 24, 24, GOLD,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("B15: all 3 layers same gold (no distinct)", case_b15())

def case_b16():
    layers = perfect_bell()
    layers[2]["strokes"] = []  # no stroke on badge
    return H(layers)
add("B16: badge has no stroke", case_b16())

def case_b17():
    layers = perfect_bell()
    layers[2]["strokes"] = [make_stroke(rgb=(0, 0, 0), weight=2)]  # black stroke
    return H(layers)
add("B17: badge stroke is black", case_b17())

def case_b18():
    layers = perfect_bell()
    layers[2]["strokes"] = [make_stroke(rgb=WHITE, weight=10)]  # very thick
    return H(layers)
add("B18: badge stroke 10px (off-tol from 2)", case_b18())

def case_b19():
    layers = perfect_bell()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: bell fill opacity 0.1 (transparent)", case_b19())

def case_b20():
    layers = perfect_bell()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "bell.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True}])
    return H(layers)
add("B20: bell stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_bell()
    layers[0] = L("vector", 0, 0, 1280, 832, GOLD)  # bell = full frame
    return H(layers)
add("C21: bell = full frame", case_c21())

def case_c22():
    layers = perfect_bell()
    layers[0] = L("vector", 540, 280, 5, 5, GOLD)  # bell tiny
    return H(layers)
add("C22: bell 5×5 (tiny)", case_c22())

def case_c23():
    layers = perfect_bell()
    layers[1] = L("ellipse", 620, 520, 1, 1, GOLD)  # 1×1 clapper
    return H(layers)
add("C23: clapper 1×1 (degenerate)", case_c23())

def case_c24():
    layers = perfect_bell()
    layers[2] = L("ellipse", 720, 280, 1, 1, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C24: badge 1×1 (degenerate)", case_c24())

def case_c25():
    layers = perfect_bell()
    layers[1] = L("ellipse", 600, 500, 200, 60, GOLD)  # squashed clapper
    return H(layers)
add("C25: clapper squashed 200×60", case_c25())

def case_c26():
    layers = perfect_bell()
    layers[2] = L("ellipse", 720, 280, 200, 60, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C26: badge squashed 200×60", case_c26())

def case_c27():
    layers = perfect_bell()
    layers[2] = L("ellipse", 720, 280, 24, 60, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C27: badge tall ellipse 24×60", case_c27())

def case_c28():
    layers = perfect_bell()
    layers[1] = L("ellipse", 600, 500, 60, 24, GOLD)  # clapper wide ellipse
    return H(layers)
add("C28: clapper wide ellipse 60×24", case_c28())

def case_c29():
    layers = perfect_bell()
    layers[0] = L("vector", 100, 100, 1080, 600, GOLD)  # bell huge
    return H(layers)
add("C29: bell huge 1080×600", case_c29())

def case_c30():
    layers = perfect_bell()
    layers[1] = L("ellipse", 620, 520, 39, 39, GOLD)  # within tol of circular
    layers[2] = L("ellipse", 720, 280, 25, 25, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C30: clapper/badge within tol (39 vs 39, 25 vs 25)", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_bell()
    for l in layers: l["x"] -= 500
    return H(layers)
add("D31: shifted left out of frame", case_d31())

def case_d32():
    layers = perfect_bell()
    for l in layers: l["x"] += 600
    return H(layers)
add("D32: shifted right out of frame", case_d32())

def case_d33():
    layers = perfect_bell()
    for l in layers: l["y"] -= 400
    return H(layers)
add("D33: shifted up out of frame", case_d33())

def case_d34():
    layers = perfect_bell()
    layers[1]["x"] = 1100  # clapper far right of bell
    layers[1]["y"] = 100
    return H(layers)
add("D34: clapper top-right of frame (not below bell)", case_d34())

def case_d35():
    layers = perfect_bell()
    layers[2]["x"] = 100  # badge bottom-left
    layers[2]["y"] = 700
    return H(layers)
add("D35: badge bottom-left (not upper-right)", case_d35())

def case_d36():
    return H()  # default perfect
add("D36: perfect (control)", case_d36())

def case_d37():
    layers = perfect_bell()
    layers[1] = L("ellipse", 620, 200, 40, 40, GOLD)  # clapper above bell
    return H(layers)
add("D37: clapper above bell", case_d37())

def case_d38():
    layers = perfect_bell()
    for l in layers: l["x"] += 100
    return H(layers)
add("D38: shifted slightly", case_d38())

def case_d39():
    layers = perfect_bell()
    layers[2]["x"] = 540
    layers[2]["y"] = 280  # badge ON bell upper-left
    return H(layers)
add("D39: badge on bell (not upper-right)", case_d39())

def case_d40():
    layers = perfect_bell()
    layers[1]["x"] = 0
    layers[1]["y"] = 0  # clapper far away
    return H(layers)
add("D40: clapper at corner (0,0)", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_bell()
    layers[0]["rotation"] = 90
    return H(layers)
add("E41: bell rotated 90°", case_e41())

def case_e42():
    layers = perfect_bell()
    layers[0]["rotation"] = 180
    return H(layers)
add("E42: bell rotated 180°", case_e42())

def case_e43():
    layers = perfect_bell()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E43: clapper flipped scaleX=-1", case_e43())

def case_e44():
    layers = perfect_bell()
    layers[2]["scaleY"] = -1
    return H(layers)
add("E44: badge flipped scaleY=-1", case_e44())

def case_e45():
    layers = perfect_bell()
    layers[0]["rotation"] = 4  # under tol
    return H(layers)
add("E45: bell rotated 4° (under tol)", case_e45())

def case_e46():
    layers = perfect_bell()
    layers[2] = L("rectangle", 720, 280, 24, 24, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers, evts=evt(ellipse=1))
add("E46: badge is rectangle (not ellipse)", case_e46())

def case_e47():
    layers = perfect_bell()
    layers[1] = L("rectangle", 620, 520, 40, 40, GOLD)  # clapper rect
    return H(layers, evts=evt(ellipse=1))
add("E47: clapper is a rectangle", case_e47())

def case_e48():
    layers = perfect_bell()
    layers[0]["sides"] = 3  # vector with sides? Just an attribute
    return H(layers)
add("E48: bell has sides=3 attr", case_e48())

def case_e49():
    layers = perfect_bell()
    layers[2]["cornerRadius"] = 12  # max round (already round)
    return H(layers)
add("E49: badge cornerRadius 12 (it's an ellipse)", case_e49())

def case_e50():
    layers = perfect_bell()
    layers[1]["rotation"] = 90  # 90 doesn't visually matter for circle but checks
    return H(layers)
add("E50: clapper rotated 90°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    layers = perfect_bell()
    # clapper and badge same position
    layers[1]["x"] = 720
    layers[1]["y"] = 280
    return H(layers)
add("F51: clapper at badge position (overlap)", case_f51())

def case_f52():
    layers = perfect_bell()
    # both ellipses identical size at same place
    layers[1] = L("ellipse", 600, 500, 100, 100, GOLD)
    layers[2] = L("ellipse", 600, 500, 100, 100, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F52: both ellipses identical", case_f52())

def case_f53():
    layers = perfect_bell()
    # badge HUGE (covers bell)
    layers[2] = L("ellipse", 540, 280, 200, 200, RED_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F53: badge huge 200×200", case_f53())

def case_f54():
    layers = perfect_bell()
    # clapper bigger than bell
    layers[1] = L("ellipse", 540, 280, 240, 240, GOLD)
    return H(layers)
add("F54: clapper bigger than bell", case_f54())

def case_f55():
    layers = perfect_bell()
    # bell, clapper, badge identical color and stacked
    layers[1]["fills"] = layers[0]["fills"]
    layers[2]["fills"] = layers[0]["fills"]
    return H(layers)
add("F55: all same color stacked", case_f55())

def case_f56():
    layers = perfect_bell()
    # extra giant transparent overlay above bell
    overlay = L("vector", 0, 0, 1280, 832, RED_BADGE)
    overlay["fills"][0]["opacity"] = 0.05
    layers.insert(0, overlay)
    return H(layers, evts=evt(vector=2))
add("F56: extra transparent vector overlay", case_f56())

def case_f57():
    layers = perfect_bell()
    # badge identical to clapper
    layers[2] = L("ellipse", 620, 520, 40, 40, GOLD)
    return H(layers)
add("F57: badge identical to clapper, gold", case_f57())

def case_f58():
    layers = perfect_bell()
    # clapper and badge same color
    layers[1]["fills"][0]["color"] = {"r": 0.95, "g": 0.20, "b": 0.20, "a": 1.0}
    return H(layers)
add("F58: clapper red (matches badge)", case_f58())

def case_f59():
    layers = perfect_bell()
    layers[2]["strokes"] = [make_stroke(rgb=WHITE, weight=2, alignment="inside")]
    return H(layers)
add("F59: badge stroke alignment inside", case_f59())

def case_f60():
    layers = perfect_bell()
    layers[2]["strokes"] = [make_stroke(rgb=WHITE, weight=2, dash={"dash": 4, "gap": 2})]
    return H(layers)
add("F60: badge stroke dashed", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_bell()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    inner = make_frame(perfect_bell(), w=600, h=500)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    layers = perfect_bell()
    return H(layers, frame_w=2000, frame_h=2000)
add("G63: frame 2000x2000", case_g63())

def case_g64():
    layers = perfect_bell()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0, 0, 0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_bell()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_bell(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G66: 2 frames, bell in 2nd", case_g66())

def case_g67():
    layers = perfect_bell()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H(frame_w=200, frame_h=200)  # frame too small
add("G68: frame 200x200 (too small)", case_g68())

def case_g69():
    layers = perfect_bell()
    return make_log(layers, evt())  # no frame
add("G69: no frame, bell on page", case_g69())

def case_g70():
    layers = perfect_bell()
    return H(layers, frame_w=1290, frame_h=842)  # within tol
add("G70: frame 1290x842 (within tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    return H(evts=[make_event("session_start")])  # no tool changes
add("H71: no events at all", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("create_vector"),
           make_event("create_ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H72: events but no tool_change (no pen used)", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_vector"),
           make_event("create_ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H73: rectangle tool used (not pen)", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector"),
           make_event("create_vector"),
           make_event("create_vector")]
    return H(evts=sem, frame_w=1280, frame_h=832)
add("H74: only pen used (no ellipse)", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H75: 50 undo events", case_h75())

def case_h76():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H76: many deletes", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse"),
           make_event("create_ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H77: only ellipse tool, no pen", case_h77())

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
    layers = perfect_bell()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: bell in group inside frame", case_i81())

def case_i82():
    bell = perfect_bell()
    f1 = make_frame([bell[0]], w=640, h=832)
    f2 = make_frame(bell[1:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: bell split across 2 frames", case_i82())

def case_i83():
    layers = perfect_bell()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: bell inside section (not frame)", case_i83())

def case_i84():
    layers = perfect_bell()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    bell = perfect_bell()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(bell, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: bell on page 2", case_i85())

def case_i86():
    bell = perfect_bell()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": bell}
    return make_log([component], evt())
add("I86: bell inside component (not frame)", case_i86())

def case_i87():
    bell = perfect_bell()
    return make_log(bell, evt())  # all on page directly
add("I87: bell on page (no frame)", case_i87())

def case_i88():
    bell = perfect_bell()
    frame = make_frame([bell[0]], w=1280, h=832)
    return make_log([frame, *bell[1:]], evt())
add("I88: bell vector in frame, ellipses on page", case_i88())

def case_i89():
    bell = perfect_bell()
    inner = make_frame([bell[0]], w=300, h=300)
    outer = make_frame([inner, *bell[1:]], w=1280, h=832)
    return make_log([outer], evt())
add("I89: bell in inner frame, ellipses in outer frame", case_i89())

def case_i90():
    bell = perfect_bell()
    return H(bell, frame_fill=(0, 0, 0))
add("I90: black frame", case_i90())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j91():
    bell = perfect_bell()
    bell[0]["scaleX"] = -1
    return H(bell)
add("J91: bell mirrored scaleX=-1", case_j91())

def case_j92():
    bell = perfect_bell()
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "bell"
    return H(bell + [text])
add("J92: bell + text 'bell'", case_j92())

def case_j93():
    layers = [L("vector", 0, 0, 1280, 832, GOLD),
              L("ellipse", 0, 0, 1280, 832, GOLD),
              L("ellipse", 0, 0, 1280, 832, RED_BADGE,
                strokes=[make_stroke(rgb=WHITE, weight=2)])]
    return H(layers)
add("J93: all shapes = full frame", case_j93())

def case_j94():
    layers = perfect_bell()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("J94: bell invisible (no fill, no stroke)", case_j94())

def case_j95():
    layers = perfect_bell()
    layers[0]["fills"][0]["color"]["a"] = 0.0  # alpha 0
    return H(layers)
add("J95: bell fill alpha=0", case_j95())

def case_j96():
    layers = perfect_bell()
    layers[0]["visible"] = False
    return H(layers)
add("J96: bell visible=False", case_j96())

def case_j97():
    layers = perfect_bell()
    layers[0]["opacity"] = 0
    return H(layers)
add("J97: bell layer opacity=0", case_j97())

def case_j98():
    layers = perfect_bell()
    for l in layers: l["y"] -= 1000
    return H(layers)
add("J98: bell at y=-1000 (off-screen)", case_j98())

def case_j99():
    layers = perfect_bell()
    layers[1] = L("ellipse", 620, 520, 0, 0, GOLD)
    return H(layers)
add("J99: clapper 0×0 (degenerate)", case_j99())

def case_j100():
    layers = perfect_bell()
    return H(layers)  # control: pure perfect
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

"""100 edge cases for task 45 (geometric emblem) — runs all and prints a sorted score table.

Task 45 prompt: 8-point deep-blue star (Star tool) + smaller circle on top with
yellow fill, both centered together.
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_45" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
YELLOW = (1.0, 0.85, 0.20)


def evt(star=1, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("tool_change", before="star", after="ellipse")]
    for _ in range(star):    sem.append(make_event("create_star"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_emblem():
    star = make_layer("star", x=440, y=216, w=400, h=400, fill=DEEP_BLUE,
                      points=8, innerRatio=0.6)
    circle = L("ellipse", 540, 316, 200, 200, YELLOW)  # smaller, centered on star
    return [star, circle]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_emblem()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_emblem()
    layers.append(make_layer("star", x=100, y=100, w=80, h=80, fill=NAVY, points=8))
    return H(layers, evts=evt(star=2))
add("A1: 2 stars", case_a1())

def case_a2():
    layers = perfect_emblem()
    layers.append(L("ellipse", 100, 100, 30, 30, NAVY))
    return H(layers, evts=evt(ellipse=2))
add("A2: 2 ellipses", case_a2())

def case_a3():
    layers = [perfect_emblem()[0]]  # only star
    return H(layers, evts=evt(ellipse=0))
add("A3: only star", case_a3())

def case_a4():
    layers = [perfect_emblem()[1]]  # only ellipse
    return H(layers, evts=evt(star=0))
add("A4: only ellipse", case_a4())

def case_a5():
    return H([], evts=evt(star=0, ellipse=0))
add("A5: empty", case_a5())

def case_a6():
    layers = perfect_emblem()
    layers.extend([L("ellipse", 100, 100, 30, 30, NAVY) for _ in range(3)])
    return H(layers, evts=evt(ellipse=4))
add("A6: 4 ellipses (3 extra)", case_a6())

def case_a7():
    layers = perfect_emblem()
    layers.extend([make_layer("star", x=100+i*100, y=100, w=50, h=50, fill=NAVY, points=8)
                   for i in range(3)])
    return H(layers, evts=evt(star=4))
add("A7: 4 stars", case_a7())

def case_a8():
    layers = perfect_emblem()
    layers.append(L("rectangle", 100, 100, 30, 30, NAVY))
    return H(layers, evts=evt(extras=[make_event("create_rectangle")]))
add("A8: emblem + extra rect", case_a8())

def case_a9():
    layers = perfect_emblem()
    layers.append(make_layer("polygon", x=100, y=100, w=30, h=30, fill=NAVY, sides=5))
    return H(layers, evts=evt(extras=[make_event("create_polygon")]))
add("A9: emblem + polygon", case_a9())

def case_a10():
    layers = perfect_emblem() + perfect_emblem()  # 2 stars 2 ellipses
    return H(layers, evts=evt(star=2, ellipse=2))
add("A10: 2 emblems (2 stars + 2 ellipses)", case_a10())


# ─── B. Colors ──────────────────────────────────────────────────────
def case_b11():
    layers = perfect_emblem()
    layers[0]["fills"] = [{"kind": "image", "src": "star.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return H(layers)
add("B11: star image fill", case_b11())

def case_b12():
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}  # gray star
    return H(layers)
add("B12: star gray (not deep blue)", case_b12())

def case_b13():
    layers = perfect_emblem()
    layers[1]["fills"][0]["color"] = {"r": 0.10, "g": 0.20, "b": 0.60, "a": 1.0}  # circle blue (same as star)
    return H(layers)
add("B13: circle deep blue (same as star)", case_b13())

def case_b14():
    layers = perfect_emblem()
    layers[1]["fills"][0]["color"] = {"r": 0.95, "g": 0.20, "b": 0.20, "a": 1.0}  # red circle
    return H(layers)
add("B14: circle red (not yellow)", case_b14())

def case_b15():
    layers = perfect_emblem()
    layers[0]["fills"] = []
    return H(layers)
add("B15: star no fill", case_b15())

def case_b16():
    layers = perfect_emblem()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B16: star fill opacity 0.1", case_b16())

def case_b17():
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("B17: star alpha=0", case_b17())

def case_b18():
    layers = perfect_emblem()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 0, "g": 0, "b": 1, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0, "b": 0.3, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B18: star gradient", case_b18())

def case_b19():
    layers = perfect_emblem()
    layers[1]["fills"] = []
    return H(layers)
add("B19: circle no fill", case_b19())

def case_b20():
    layers = perfect_emblem()
    layers[0]["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(layers)
add("B20: star stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_emblem()
    layers[0]["w"] = 1280
    layers[0]["h"] = 832
    layers[0]["x"] = 0
    layers[0]["y"] = 0
    return H(layers)
add("C21: star = full frame", case_c21())

def case_c22():
    layers = perfect_emblem()
    layers[0]["w"] = 5
    layers[0]["h"] = 5
    return H(layers)
add("C22: star 5×5", case_c22())

def case_c23():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 540, 316, 1, 1, YELLOW)
    return H(layers)
add("C23: circle 1×1", case_c23())

def case_c24():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 100, 100, 600, 100, YELLOW)  # squashed
    return H(layers)
add("C24: circle 600×100 oval", case_c24())

def case_c25():
    layers = perfect_emblem()
    layers[0]["w"] = 200
    layers[0]["h"] = 600  # tall star
    return H(layers)
add("C25: star tall 200×600", case_c25())

def case_c26():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 100, 100, 600, 600, YELLOW)  # circle bigger than star
    return H(layers)
add("C26: circle bigger than star", case_c26())

def case_c27():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 440, 216, 400, 400, YELLOW)  # circle = star size
    return H(layers)
add("C27: circle = star size", case_c27())

def case_c28():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 540, 316, 8, 8, YELLOW)  # tiny circle
    return H(layers)
add("C28: circle 8×8 (tiny)", case_c28())

def case_c29():
    layers = perfect_emblem()
    layers[0]["w"] = 1080
    layers[0]["h"] = 600
    return H(layers)
add("C29: star huge", case_c29())

def case_c30():
    layers = perfect_emblem()
    layers[1] = L("ellipse", 540, 316, 200, 60, YELLOW)  # oval
    return H(layers)
add("C30: circle 200×60 oval", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_emblem()
    layers[1]["x"] = 100
    layers[1]["y"] = 100  # circle far from star
    return H(layers)
add("D31: circle far from star", case_d31())

def case_d32():
    layers = perfect_emblem()
    for l in layers: l["x"] -= 600
    return H(layers)
add("D32: shifted left", case_d32())

def case_d33():
    layers = perfect_emblem()
    for l in layers: l["y"] -= 400
    return H(layers)
add("D33: shifted up", case_d33())

def case_d34():
    return H()
add("D34: perfect (control)", case_d34())

def case_d35():
    layers = perfect_emblem()
    # circle at edge of star
    layers[1]["x"] = 700
    layers[1]["y"] = 316
    return H(layers)
add("D35: circle at right edge of star", case_d35())

def case_d36():
    layers = perfect_emblem()
    layers[1]["x"] = 540  # left-aligned
    return H(layers)
add("D36: circle at top-left of star", case_d36())

def case_d37():
    layers = perfect_emblem()
    layers[1]["x"] = 1100
    layers[1]["y"] = 700
    return H(layers)
add("D37: circle at far corner", case_d37())

def case_d38():
    layers = perfect_emblem()
    for l in layers: l["x"] += 200
    return H(layers)
add("D38: shifted right slightly", case_d38())

def case_d39():
    layers = perfect_emblem()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 500
    return H(layers)
add("D39: shifted off-frame", case_d39())

def case_d40():
    # Both on top of each other — same position
    layers = perfect_emblem()
    layers[1]["x"] = 440
    layers[1]["y"] = 216
    return H(layers)
add("D40: circle at star top-left", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_emblem()
    layers[0]["points"] = 5  # 5-point star
    return H(layers)
add("E41: 5-point star", case_e41())

def case_e42():
    layers = perfect_emblem()
    layers[0]["points"] = 16
    return H(layers)
add("E42: 16-point star", case_e42())

def case_e43():
    layers = perfect_emblem()
    layers[0]["rotation"] = 45
    return H(layers)
add("E43: star rotated 45°", case_e43())

def case_e44():
    layers = perfect_emblem()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: star mirrored", case_e44())

def case_e45():
    layers = perfect_emblem()
    layers[1]["rotation"] = 45  # circle rotated
    return H(layers)
add("E45: circle rotated 45° (no visual effect)", case_e45())

def case_e46():
    layers = perfect_emblem()
    layers[0]["points"] = 0  # degenerate star
    return H(layers)
add("E46: star points=0", case_e46())

def case_e47():
    layers = perfect_emblem()
    layers[1]["cornerRadius"] = 50
    return H(layers)
add("E47: circle cornerRadius=50", case_e47())

def case_e48():
    layers = perfect_emblem()
    layers[0]["innerRatio"] = 0.99  # almost a circle
    return H(layers)
add("E48: star innerRatio 0.99 (looks circular)", case_e48())

def case_e49():
    layers = perfect_emblem()
    layers[0]["innerRatio"] = 0.05  # very pointy
    return H(layers)
add("E49: star innerRatio 0.05 (pointy)", case_e49())

def case_e50():
    layers = perfect_emblem()
    layers[1]["scaleY"] = -1
    return H(layers)
add("E50: circle flipped vertically", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    layers = perfect_emblem()
    # Both same color (yellow)
    layers[0]["fills"][0]["color"] = {"r": 1.0, "g": 0.85, "b": 0.20, "a": 1.0}
    return H(layers)
add("F51: star yellow (same as circle)", case_f51())

def case_f52():
    # Order swapped (ellipse drawn first, star drawn last → on top)
    layers = perfect_emblem()
    layers = [layers[1], layers[0]]
    return H(layers)
add("F52: star drawn after circle (on top)", case_f52())

def case_f53():
    layers = perfect_emblem()
    layers[1] = L("rectangle", 540, 316, 200, 200, YELLOW)  # circle is rect
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]))
add("F53: circle is a rectangle", case_f53())

def case_f54():
    layers = perfect_emblem()
    # Circle below star (z-order)
    layers = [layers[1], layers[0]]
    return H(layers)
add("F54: circle drawn first (below star)", case_f54())

def case_f55():
    layers = perfect_emblem()
    # Star is a polygon (5-sided)
    layers[0] = make_layer("polygon", x=440, y=216, w=400, h=400, fill=DEEP_BLUE, sides=5)
    return H(layers, evts=evt(star=0, extras=[make_event("create_polygon")]))
add("F55: star is a polygon", case_f55())

def case_f56():
    layers = perfect_emblem()
    # Star's inner area larger than circle
    layers[0] = make_layer("star", x=440, y=216, w=400, h=400, fill=DEEP_BLUE, points=8, innerRatio=0.95)
    return H(layers)
add("F56: star innerRatio 0.95 (no real spikes)", case_f56())

def case_f57():
    layers = perfect_emblem()
    # Circle slightly below center
    layers[1] = L("ellipse", 540, 350, 200, 200, YELLOW)
    return H(layers)
add("F57: circle slightly below star center", case_f57())

def case_f58():
    layers = perfect_emblem()
    # Circle has stroke
    layers[1]["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return H(layers)
add("F58: circle has stroke", case_f58())

def case_f59():
    layers = perfect_emblem()
    # Star has stroke
    layers[0]["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return H(layers)
add("F59: star has stroke", case_f59())

def case_f60():
    layers = perfect_emblem()
    # Circle has cornerRadius (no effect on ellipse)
    layers[1]["cornerRadius"] = 0
    return H(layers)
add("F60: circle cornerRadius=0", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_emblem()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated", case_g61())

def case_g62():
    inner = make_frame(perfect_emblem(), w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    return H(frame_w=2000, frame_h=2000)
add("G63: frame 2000x2000", case_g63())

def case_g64():
    layers = perfect_emblem()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    layers = perfect_emblem()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_emblem(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G66: 2 frames, emblem in 2nd", case_g66())

def case_g67():
    layers = perfect_emblem()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H(frame_w=200, frame_h=200)
add("G68: frame 200x200", case_g68())

def case_g69():
    return make_log(perfect_emblem(), evt())
add("G69: no frame", case_g69())

def case_g70():
    return H(frame_w=1290, frame_h=842)
add("G70: frame 1290x842 (within tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    return H(evts=[make_event("session_start")])
add("H71: no events", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("create_star"), make_event("create_ellipse")]
    return H(evts=sem)
add("H72: events but no tool_change", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_star"), make_event("create_ellipse")]
    return H(evts=sem)
add("H73: rectangle tool used", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H74: only ellipse, no star", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H75: 50 undos", case_h75())

def case_h76():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H76: many deletes", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("create_star")]
    return H(evts=sem)
add("H77: only star, no ellipse", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("create_rectangle"), make_event("delete")]))
add("H78: rect + delete", case_h78())

def case_h79():
    return H(evts=evt(set_fill=20))
add("H79: 20 set_fills", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("session_end")] * 5))
add("H80: many session_end", case_h80())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i81():
    layers = perfect_emblem()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group", case_i81())

def case_i82():
    emblem = perfect_emblem()
    f1 = make_frame([emblem[0]], w=640, h=832)
    f2 = make_frame([emblem[1]], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_emblem()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    layers = perfect_emblem()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested", case_i84())

def case_i85():
    emblem = perfect_emblem()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(emblem, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: emblem on page 2", case_i85())

def case_i86():
    emblem = perfect_emblem()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": emblem}
    return make_log([component], evt())
add("I86: in component", case_i86())

def case_i87():
    return make_log(perfect_emblem(), evt())
add("I87: on page (no frame)", case_i87())

def case_i88():
    emblem = perfect_emblem()
    f = make_frame([emblem[0]], w=1280, h=832)
    return make_log([f, emblem[1]], evt())
add("I88: star in frame, circle on page", case_i88())

def case_i89():
    emblem = perfect_emblem()
    inner = make_frame([emblem[0]], w=600, h=600)
    outer = make_frame([inner, emblem[1]], w=1280, h=832)
    return make_log([outer], evt())
add("I89: star in inner, circle in outer", case_i89())

def case_i90():
    return H(frame_fill=(0, 0, 0))
add("I90: black frame", case_i90())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j91():
    layers = perfect_emblem()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J91: star mirrored", case_j91())

def case_j92():
    layers = perfect_emblem()
    text = make_layer("text", x=100, y=100, w=200, h=50, fill=NAVY)
    text["content"] = "emblem"
    return H(layers + [text])
add("J92: emblem + text", case_j92())

def case_j93():
    layers = [make_layer("star", x=0, y=0, w=1280, h=832, fill=DEEP_BLUE, points=8),
              L("ellipse", 0, 0, 1280, 832, YELLOW)]
    return H(layers)
add("J93: both = full frame", case_j93())

def case_j94():
    layers = perfect_emblem()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("J94: star invisible", case_j94())

def case_j95():
    layers = perfect_emblem()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("J95: star alpha=0", case_j95())

def case_j96():
    layers = perfect_emblem()
    layers[1]["visible"] = False
    return H(layers)
add("J96: circle visible=False", case_j96())

def case_j97():
    layers = perfect_emblem()
    layers[0]["opacity"] = 0
    return H(layers)
add("J97: star opacity=0", case_j97())

def case_j98():
    layers = perfect_emblem()
    for l in layers: l["y"] -= 1000
    return H(layers)
add("J98: shifted up off-screen", case_j98())

def case_j99():
    layers = perfect_emblem()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J99: 0×0", case_j99())

def case_j100():
    return H()
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

"""100 edge cases for task 37 (sticky note) — runs all and prints score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_37" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
YELLOW_NOTE = (1.0, 0.92, 0.6)
DARK_YELLOW = (0.85, 0.78, 0.5)
GRAY_LINE = (0.5, 0.5, 0.5)
LIGHT_GRAY = (0.8, 0.8, 0.8)


def evt(rect=1, vector=1, line=3, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("tool_change", before="pen", after="line")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(line):    sem.append(make_event("create_line"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_note():
    rect = L("rectangle", 300, 300, 200, 200, YELLOW_NOTE,
             rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    fold = L("vector", 460, 300, 40, 40, DARK_YELLOW)
    lines = [L("line", 320, 350+i*30, 160, 2, None,
               strokes=[make_stroke(rgb=GRAY_LINE, weight=1)]) for i in range(3)]
    return [rect, fold, *lines]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_note()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10 cases) ────────────────────────────────────────────
def a1():
    layers = perfect_note()
    layers.append(L("rectangle", 600, 300, 200, 200, YELLOW_NOTE,
                    rotation=3, effects=[make_drop_shadow(y=4, blur=8)]))
    return H(layers, evts=evt(rect=2))
add("A1: 2 sticky note bodies", a1())

def a2():
    layers = [L("vector", 460, 300, 40, 40, DARK_YELLOW)]
    layers.extend([L("line", 320, 350+i*30, 160, 2, None,
                     strokes=[make_stroke(rgb=GRAY_LINE, weight=1)]) for i in range(3)])
    return H(layers, evts=evt(rect=0))
add("A2: 0 rectangles (no body)", a2())

def a3():
    layers = perfect_note()
    layers.pop(1)  # drop fold
    return H(layers, evts=evt(vector=0))
add("A3: 0 vectors (no fold)", a3())

def a4():
    layers = perfect_note()
    for _ in range(3): layers.pop()  # drop all lines
    return H(layers, evts=evt(line=0))
add("A4: 0 lines", a4())

def a5():
    layers = perfect_note()
    layers.pop()  # drop one line: 2 left
    return H(layers, evts=evt(line=2))
add("A5: only 2 lines (off-by-one)", a5())

def a6():
    layers = perfect_note()
    layers.pop(); layers.pop()  # drop two lines
    return H(layers, evts=evt(line=1))
add("A6: only 1 line", a6())

def a7():
    layers = perfect_note()
    for i in range(5):
        layers.append(L("line", 320, 470+i*15, 160, 2, None,
                        strokes=[make_stroke(rgb=GRAY_LINE, weight=1)]))
    return H(layers, evts=evt(line=8))
add("A7: 8 lines (extras)", a7())

def a8():
    layers = perfect_note()
    layers.append(L("vector", 320, 460, 30, 30, DARK_YELLOW))
    layers.append(L("vector", 380, 460, 30, 30, DARK_YELLOW))
    return H(layers, evts=evt(vector=3))
add("A8: 3 vectors (extra folds)", a8())

def a9():
    return H([])
add("A9: empty document", a9())

def a10():
    rect = L("rectangle", 300, 300, 200, 200, YELLOW_NOTE,
             rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H([rect], evts=evt(vector=0, line=0))
add("A10: just the rectangle (no fold, no lines)", a10())


# ─── B. Colors / fills (10 cases) ────────────────────────────────────
def b11():
    layers = perfect_note()
    layers[0]["fills"] = [{"kind": "image", "src": "note.jpg", "fit": "cover",
                           "opacity": 1.0, "visible": True}]
    return H(layers)
add("B11: rectangle has image fill", b11())

def b12():
    layers = perfect_note()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":0.92,"b":0.6,"a":1}},
        {"position": 1, "color": {"r":0.8,"g":0.7,"b":0.4,"a":1}}],
        "opacity":1, "visible":True}]
    return H(layers)
add("B12: rectangle has gradient fill", b12())

def b13():
    layers = perfect_note()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=YELLOW_NOTE, weight=2)]
    return H(layers)
add("B13: rectangle stroke only, no fill", b13())

def b14():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 200, 200, RED,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("B14: red square (not yellow)", b14())

def b15():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 200, 200, NAVY,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("B15: navy square (not yellow)", b15())

def b16():
    layers = perfect_note()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: rectangle fill alpha=0 (invisible)", b16())

def b17():
    layers = perfect_note()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B17: rectangle fill opacity=0.1 (transparent)", b17())

def b18():
    layers = perfect_note()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("B18: rectangle fill visible=False", b18())

def b19():
    layers = perfect_note()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("B19: rectangle layer opacity=0", b19())

def b20():
    layers = perfect_note()
    # near-yellow but at edge of tolerance
    layers[0]["fills"][0]["color"] = {"r":0.9, "g":0.85, "b":0.55, "a":1.0}
    return H(layers)
add("B20: near-yellow (just inside tol)", b20())


# ─── C. Sizing (10 cases) ────────────────────────────────────────────
def c21():
    layers = perfect_note()
    layers[0] = L("rectangle", 0, 0, 1280, 832, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C21: rectangle = full frame", c21())

def c22():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 5, 5, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C22: rectangle 5x5 (tiny)", c22())

def c23():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 800, 20, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C23: rectangle 800x20 (very thin)", c23())

def c24():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 20, 800, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C24: rectangle 20x800 (very tall)", c24())

def c25():
    layers = perfect_note()
    layers[1] = L("vector", 460, 300, 600, 600, DARK_YELLOW)
    return H(layers)
add("C25: fold huge", c25())

def c26():
    layers = perfect_note()
    layers[1] = L("vector", 460, 300, 1, 1, DARK_YELLOW)
    return H(layers)
add("C26: fold 1x1 (degenerate)", c26())

def c27():
    layers = perfect_note()
    for i in range(3):
        layers[2+i] = L("line", 320, 350+i*30, 1, 1, None,
                        strokes=[make_stroke(rgb=GRAY_LINE, weight=1)])
    return H(layers)
add("C27: lines 1x1 (degenerate)", c27())

def c28():
    layers = perfect_note()
    for i in range(3):
        layers[2+i] = L("line", 320, 350+i*30, 1500, 2, None,
                        strokes=[make_stroke(rgb=GRAY_LINE, weight=1)])
    return H(layers)
add("C28: lines 1500px wide (huge)", c28())

def c29():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 199, 50, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C29: rectangle 199x50 (squashed)", c29())

def c30():
    layers = perfect_note()
    layers[0] = L("rectangle", 300, 300, 50, 199, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers)
add("C30: rectangle 50x199 (tall)", c30())


# ─── D. Position (10 cases) ──────────────────────────────────────────
def d31():
    layers = perfect_note()
    for l in layers:
        l["x"] -= 500; l["y"] -= 350
    return H(layers)
add("D31: note shifted off-frame top-left", d31())

def d32():
    layers = perfect_note()
    for l in layers:
        l["x"] += 1500
    return H(layers)
add("D32: note shifted off-frame right", d32())

def d33():
    layers = perfect_note()
    for l in layers:
        l["y"] -= 1000
    return H(layers)
add("D33: note negative y", d33())

def d34():
    layers = perfect_note()
    layers[1]["x"] = -500; layers[1]["y"] = -500
    return H(layers)
add("D34: fold off-frame", d34())

def d35():
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["x"] = -500
    return H(layers)
add("D35: lines off-frame", d35())

def d36():
    layers = perfect_note()
    layers[1] = L("vector", 0, 0, 40, 40, DARK_YELLOW)  # fold far from rect
    return H(layers)
add("D36: fold not on rectangle", d36())

def d37():
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["x"] = 0
        layers[2+i]["y"] = 100 + i*20
    return H(layers)
add("D37: lines not on rectangle", d37())

def d38():
    layers = perfect_note()
    return H(layers)  # default perfect, control
add("D38: perfect (control)", d38())

def d39():
    layers = perfect_note()
    layers[1] = L("vector", 280, 280, 40, 40, DARK_YELLOW)  # fold on top-LEFT
    return H(layers)
add("D39: fold at top-left (not top-right)", d39())

def d40():
    layers = perfect_note()
    layers[0]["x"] = 1100; layers[0]["y"] = 750
    layers[1]["x"] = 1140; layers[1]["y"] = 750
    return H(layers)
add("D40: rect+fold at far edge", d40())


# ─── E. Rotation / shape variants (10 cases) ─────────────────────────
def e41():
    layers = perfect_note()
    layers[0]["rotation"] = 0
    return H(layers)
add("E41: rotation 0° (no tilt)", e41())

def e42():
    layers = perfect_note()
    layers[0]["rotation"] = 45
    return H(layers)
add("E42: rotation 45°", e42())

def e43():
    layers = perfect_note()
    layers[0]["rotation"] = 90
    return H(layers)
add("E43: rotation 90°", e43())

def e44():
    layers = perfect_note()
    layers[0]["rotation"] = 180
    return H(layers)
add("E44: rotation 180°", e44())

def e45():
    layers = perfect_note()
    layers[0]["rotation"] = -3
    return H(layers)
add("E45: rotation -3° (negative)", e45())

def e46():
    layers = perfect_note()
    layers[0]["rotation"] = 4
    return H(layers)
add("E46: rotation 4° (close to expected)", e46())

def e47():
    layers = perfect_note()
    layers[0]["rotation"] = 30
    return H(layers)
add("E47: rotation 30°", e47())

def e48():
    layers = perfect_note()
    layers[0] = make_layer("star", x=300, y=300, w=200, h=200, fill=YELLOW_NOTE,
                            rotation=3, points=5, innerRatio=0.4,
                            effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers, evts=evt(rect=0))
add("E48: rectangle replaced by star", e48())

def e49():
    layers = perfect_note()
    layers[0] = L("ellipse", 300, 300, 200, 200, YELLOW_NOTE,
                  rotation=3, effects=[make_drop_shadow(y=4, blur=8)])
    return H(layers, evts=evt(rect=0))
add("E49: rectangle replaced by ellipse", e49())

def e50():
    layers = perfect_note()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E50: rectangle flipped (scaleX=-1)", e50())


# ─── F. Subcomponent / line variants (10 cases) ──────────────────────
def f51():
    # all 3 lines at exact same y (overlapping)
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["y"] = 350
    return H(layers)
add("F51: lines all at same y (overlapping)", f51())

def f52():
    # lines vertical instead of horizontal
    layers = perfect_note()
    for i in range(3):
        layers[2+i] = L("line", 320+i*30, 350, 2, 100, None,
                        strokes=[make_stroke(rgb=GRAY_LINE, weight=1)])
    return H(layers)
add("F52: lines vertical (not horizontal)", f52())

def f53():
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["fills"] = []
        layers[2+i]["strokes"] = []  # no stroke
    return H(layers)
add("F53: lines with no stroke at all", f53())

def f54():
    layers = perfect_note()
    layers[1]["fills"][0]["color"] = {"r":0.05, "g":0.10, "b":0.45, "a":1}  # navy fold
    return H(layers)
add("F54: fold is navy (not darker yellow)", f54())

def f55():
    layers = perfect_note()
    layers[1]["fills"][0]["color"] = {"r":0.95, "g":0.92, "b":0.8, "a":1}  # too pale
    return H(layers)
add("F55: fold pale-yellow (not darker)", f55())

def f56():
    layers = perfect_note()
    layers[1]["effects"] = []
    layers[1]["fills"] = []
    return H(layers)
add("F56: fold has no fill (invisible)", f56())

def f57():
    layers = perfect_note()
    layers[0]["effects"] = []
    return H(layers)
add("F57: no drop shadow on rectangle", f57())

def f58():
    # extra: 4th line as rectangle (wrong type)
    layers = perfect_note()
    layers.append(L("rectangle", 320, 470, 160, 2, GRAY_LINE))
    return H(layers, evts=evt(rect=2))
add("F58: 4th 'line' is actually rectangle", f58())

def f59():
    # lines all rotated
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["rotation"] = 45
    return H(layers)
add("F59: lines rotated 45°", f59())

def f60():
    # lines way outside rectangle bounds
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["x"] = 800 + i*30
        layers[2+i]["y"] = 100
    return H(layers)
add("F60: lines far from rectangle", f60())


# ─── G. Frame variants (10 cases) ────────────────────────────────────
def g61():
    layers = perfect_note()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", g61())

def g62():
    layers = perfect_note()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", g62())

def g63():
    layers = perfect_note()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("G63: frame with stroke", g63())

def g64():
    layers = perfect_note()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G64: frame image fill", g64())

def g65():
    layers = perfect_note()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G65: frame translated", g65())

def g66():
    return H(frame_w=2000, frame_h=1500)
add("G66: frame oversized 2000x1500", g66())

def g67():
    return H(frame_w=200, frame_h=200)
add("G67: frame undersized 200x200", g67())

def g68():
    return H()  # default perfect
add("G68: default frame (control)", g68())

def g69():
    layers = perfect_note()
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(layers, w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames, note in 2nd", g69())

def g70():
    return H(in_frame=False)
add("G70: shapes on page (no frame)", g70())


# ─── H. Tools / events (10 cases) ────────────────────────────────────
def h71():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H71: 20 undo events", h71())

def h72():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H72: used align_layers", h72())

def h73():
    sem = [make_event("session_start"),
           make_event("create_rectangle"),
           make_event("create_vector"),
           make_event("create_line"), make_event("create_line"), make_event("create_line")]
    return H(evts=sem)
add("H73: 0 tool_change events", h73())

def h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="line"),
           make_event("create_line"), make_event("create_line"), make_event("create_line")]
    return H(evts=sem)
add("H74: no pen tool used", h74())

def h75():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("create_rectangle"),
           make_event("create_vector"),
           make_event("create_line"), make_event("create_line"), make_event("create_line")]
    return H(evts=sem)
add("H75: no line tool tool_change (used keyboard)", h75())

def h76():
    return H(evts=evt(extras=[make_event("create_star"),
                              make_event("delete")]))
add("H76: create+delete star (extras)", h76())

def h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", h77())

def h78():
    return H(evts=evt(set_fill=10))
add("H78: 10 set_fill events", h78())

def h79():
    return H(evts=evt(rect=2, line=5))
add("H79: 2 create_rectangle (extra)", h79())

def h80():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H80: 50 move events", h80())


# ─── I. Hierarchy (10 cases) ─────────────────────────────────────────
def i81():
    layers = perfect_note()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: shapes in group inside frame", i81())

def i82():
    layers = perfect_note()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: shapes split across 2 frames", i82())

def i83():
    layers = perfect_note()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: shapes in section (not frame)", i83())

def i84():
    layers = perfect_note()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I84: shapes in component (not frame)", i84())

def i85():
    layers = perfect_note()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", i85())

def i86():
    layers = perfect_note()
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    frame = make_frame(layers, w=1280, h=832)
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: note on page 2", i86())

def i87():
    layers = perfect_note()
    frame = make_frame(layers[:1], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: rect in frame, fold/lines on page", i87())

def i88():
    # All layers on a page directly without a parent frame
    layers = perfect_note()
    return make_log(layers, evt())
add("I88: shapes top-level on page (no frame)", i88())

def i89():
    layers = perfect_note()
    inner_frame = make_frame(layers, w=400, h=400)
    big_frame = make_frame([inner_frame], w=1280, h=832)
    return make_log([big_frame], evt())
add("I89: small inner frame in big frame", i89())

def i90():
    layers = perfect_note()
    layers[0]["children"] = [layers[1]]  # fold inside rect (impossible but allowed)
    return make_log([layers[0], *layers[2:]], evt())
add("I90: fold nested inside rectangle", i90())


# ─── J. Bizarre / Hard (10 cases) ────────────────────────────────────
def j91():
    layers = perfect_note()
    layers[0]["rotation"] = 180
    return H(layers)
add("J91: rectangle rotated 180°", j91())

def j92():
    layers = perfect_note()
    # rectangle, fold and lines at one point
    for l in layers: l["x"] = 500; l["y"] = 400; l["w"] = 100; l["h"] = 100
    return H(layers)
add("J92: all shapes piled at one point", j92())

def j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document, just session_start", j93())

def j94():
    layers = [L("text", 400, 400, 200, 50, NAVY)]
    layers[0]["content"] = "yellow sticky note"
    return make_log(layers, [make_event("session_start"), make_event("create_text")])
add("J94: text 'yellow sticky note'", j94())

def j95():
    layers = perfect_note()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J95: rectangle mirrored (scaleX=-1)", j95())

def j96():
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["w"] = 1
        layers[2+i]["h"] = 1
    return H(layers)
add("J96: lines all 1x1 (degenerate)", j96())

def j97():
    layers = perfect_note()
    layers.append(L("rectangle", 400, 400, 50, 50, ORANGE))
    return H(layers, evts=evt(rect=2))
add("J97: 2 rectangles (extra body)", j97())

def j98():
    # all lines at same x as rectangle but with y outside rectangle range
    layers = perfect_note()
    for i in range(3):
        layers[2+i]["y"] = 100  # above the rect
    return H(layers)
add("J98: lines above rectangle", j98())

def j99():
    layers = perfect_note()
    # rectangle covers fold and lines (z-order: rect on top)
    rect = layers.pop(0)
    layers.append(rect)
    return H(layers)
add("J99: rectangle on top z-order", j99())

def j100():
    layers = perfect_note()  # control
    return H(layers)
add("J100: perfect (control)", j100())


# ─── Run ────────────────────────────────────────────────────────────
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

"""100 edge cases for task 41 (search bar) — runs all and prints score table."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, RED, GREEN, YELLOW, ORANGE, WHITE, BLACK, PURPLE, PINK, GOLD, CYAN,
)
from tasks import task_41_search_bar as t
T = t.task

LIGHT_GRAY = (0.95, 0.95, 0.95)
GRAY_STROKE = (0.5, 0.5, 0.5)


def evt(rect=1, ellipse=3, line=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("tool_change", before="ellipse", after="line")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(line):    sem.append(make_event("create_line"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_search():
    bar = L("rectangle", 200, 300, 320, 48, LIGHT_GRAY, cornerRadius=24)
    glass = L("ellipse", 215, 312, 24, 24, None,
              strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    handle = L("line", 232, 332, 12, 12, None,
               strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    dot1 = L("ellipse", 270, 320, 8, 8, None,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    dot2 = L("ellipse", 285, 320, 8, 8, None,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return [bar, glass, handle, dot1, dot2]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_search()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ──────────────────────────────────────────────────
def a1():
    layers = perfect_search()[:1]
    return H(layers, evts=evt(ellipse=0, line=0))
add("A1: only bar", a1())

def a2():
    layers = perfect_search()[:2]
    return H(layers, evts=evt(ellipse=1, line=0))
add("A2: bar + glass only", a2())

def a3():
    layers = perfect_search()[:3]
    return H(layers, evts=evt(ellipse=1))
add("A3: bar + glass + handle", a3())

def a4():
    layers = perfect_search()[:4]
    return H(layers, evts=evt(ellipse=2))
add("A4: missing 2nd dot", a4())

def a5():
    layers = perfect_search()
    layers.append(L("ellipse", 320, 320, 8, 8, None,
                    strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)]))
    return H(layers, evts=evt(ellipse=4))
add("A5: 3 dots + glass = 4 ellipses", a5())

def a6():
    layers = perfect_search()
    layers.append(L("rectangle", 600, 100, 50, 50, GOLD))
    return H(layers, evts=evt(rect=2))
add("A6: 2 rectangles", a6())

def a7():
    layers = perfect_search()
    layers.append(L("line", 100, 700, 50, 5, None,
                    strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)]))
    return H(layers, evts=evt(line=2))
add("A7: 2 lines (extra)", a7())

def a8():
    return H()  # control
add("A8: perfect (control)", a8())

def a9():
    return H([], evts=evt(rect=0, ellipse=0, line=0))
add("A9: empty doc", a9())

def a10():
    layers = perfect_search()
    return H(layers)
add("A10: perfect 2 (control)", a10())


# ─── B. Colors (10) ──────────────────────────────────────────────────
def b11():
    layers = perfect_search()
    layers[0]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B11: bar image fill", b11())

def b12():
    layers = perfect_search()
    layers[0]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B12: bar gradient", b12())

def b13():
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 320, 48, BLACK, cornerRadius=24)
    return H(layers)
add("B13: bar is black", b13())

def b14():
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 320, 48, RED, cornerRadius=24)
    return H(layers)
add("B14: bar is red", b14())

def b15():
    layers = perfect_search()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("B15: bar fill alpha=0", b15())

def b16():
    layers = perfect_search()
    layers[0]["opacity"] = 0
    return H(layers)
add("B16: bar layer opacity=0", b16())

def b17():
    layers = perfect_search()
    layers[1]["strokes"][0]["paint"]["color"] = {"r":1.0, "g":0.95, "b":0.95, "a":1}
    return H(layers)
add("B17: glass stroke near-white (invisible)", b17())

def b18():
    layers = perfect_search()
    layers[1]["strokes"] = []
    return H(layers)
add("B18: glass no stroke", b18())

def b19():
    layers = perfect_search()
    layers[1]["fills"] = [{"kind":"solid","color":{"r":0.5,"g":0.5,"b":0.5,"a":1},"opacity":1,"visible":True}]
    return H(layers)
add("B19: glass has fill (should be hollow)", b19())

def b20():
    return H()  # control
add("B20: perfect (control)", b20())


# ─── C. Sizing (10) ──────────────────────────────────────────────────
def c21():
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 200, 48, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("C21: bar 200 wide (not 320)", c21())

def c22():
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 320, 80, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("C22: bar 320x80 (twice as tall)", c22())

def c23():
    layers = perfect_search()
    layers[0] = L("rectangle", 200, 300, 1280, 48, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("C23: bar 1280x48 (full width)", c23())

def c24():
    layers = perfect_search()
    layers[1] = L("ellipse", 215, 312, 200, 200, None,  # huge magnifier
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C24: magnifier 200x200 (huge)", c24())

def c25():
    layers = perfect_search()
    layers[1] = L("ellipse", 215, 312, 1, 1, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C25: magnifier 1x1", c25())

def c26():
    layers = perfect_search()
    layers[3] = L("ellipse", 270, 320, 1, 1, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    layers[4] = L("ellipse", 285, 320, 1, 1, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C26: dots 1x1", c26())

def c27():
    layers = perfect_search()
    layers[2] = L("line", 232, 332, 1, 1, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C27: line 1x1", c27())

def c28():
    layers = perfect_search()
    layers[1] = L("ellipse", 215, 312, 100, 30, None,  # squashed magnifier
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C28: magnifier 100x30 oval", c28())

def c29():
    return H()  # control
add("C29: perfect (control)", c29())

def c30():
    layers = perfect_search()
    layers[0] = L("rectangle", 0, 0, 1280, 832, LIGHT_GRAY, cornerRadius=24)
    return H(layers)
add("C30: bar = full frame", c30())


# ─── D. Position (10) ────────────────────────────────────────────────
def d31():
    layers = perfect_search()
    for l in layers: l["x"] -= 500
    return H(layers)
add("D31: shifted off-left", d31())

def d32():
    layers = perfect_search()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D32: shifted off-right", d32())

def d33():
    layers = perfect_search()
    for l in layers: l["y"] -= 500
    return H(layers)
add("D33: negative y", d33())

def d34():
    layers = perfect_search()
    layers[1] = L("ellipse", 100, 100, 24, 24, None,  # magnifier far away
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("D34: magnifier far from bar", d34())

def d35():
    layers = perfect_search()
    for i in range(2):
        layers[3+i] = L("ellipse", 100+i*15, 100, 8, 8, None,  # dots far away
                        strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("D35: dots far from bar", d35())

def d36():
    layers = perfect_search()
    layers[2] = L("line", 100, 100, 12, 12, None,  # line far away
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("D36: line far from bar", d36())

def d37():
    return H()
add("D37: perfect (control)", d37())

def d38():
    # bar at top, all icons below
    layers = perfect_search()
    for l in layers[1:]:
        l["y"] += 200
    return H(layers)
add("D38: icons below bar", d38())

def d39():
    # all at one point
    layers = perfect_search()
    for l in layers: l["x"] = 500; l["y"] = 400
    return H(layers)
add("D39: all at one point", d39())

def d40():
    return H()  # control
add("D40: perfect (control)", d40())


# ─── E. Rotation / shape variants (10) ───────────────────────────────
def e41():
    layers = perfect_search()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: bar rotated 45°", e41())

def e42():
    layers = perfect_search()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: bar rotated 90°", e42())

def e43():
    layers = perfect_search()
    layers[1]["rotation"] = 45
    return H(layers)
add("E43: magnifier rotated 45°", e43())

def e44():
    layers = perfect_search()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: bar mirrored", e44())

def e45():
    layers = perfect_search()
    layers[0]["cornerRadius"] = 0
    return H(layers)
add("E45: bar cornerRadius=0", e45())

def e46():
    layers = perfect_search()
    layers[0]["cornerRadius"] = 4
    return H(layers)
add("E46: bar cornerRadius=4 (low)", e46())

def e47():
    # bar is ellipse
    layers = perfect_search()
    layers[0] = L("ellipse", 200, 300, 320, 48, LIGHT_GRAY)
    return H(layers, evts=evt(rect=0, ellipse=4))
add("E47: bar is ellipse", e47())

def e48():
    # magnifier is rectangle
    layers = perfect_search()
    layers[1] = L("rectangle", 215, 312, 24, 24, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=2, ellipse=2))
add("E48: magnifier is rectangle", e48())

def e49():
    # line is rectangle
    layers = perfect_search()
    layers[2] = L("rectangle", 232, 332, 12, 2, GRAY_STROKE)
    return H(layers, evts=evt(rect=2, line=0))
add("E49: line is rectangle", e49())

def e50():
    return H()  # control
add("E50: perfect (control)", e50())


# ─── F. Subcomponent variants (10) ───────────────────────────────────
def f51():
    # magnifier oval not circle
    layers = perfect_search()
    layers[1] = L("ellipse", 215, 312, 50, 24, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("F51: magnifier oval (not circle)", f51())

def f52():
    layers = perfect_search()
    layers[1]["strokes"][0]["weight"] = 0
    return H(layers)
add("F52: magnifier stroke weight 0", f52())

def f53():
    # very thick stroke
    layers = perfect_search()
    layers[1]["strokes"][0]["weight"] = 20
    return H(layers)
add("F53: magnifier stroke 20px (thick)", f53())

def f54():
    # line filled instead of stroked
    layers = perfect_search()
    layers[2] = L("line", 232, 332, 12, 12, GRAY_STROKE)
    return H(layers)
add("F54: line filled (no stroke)", f54())

def f55():
    layers = perfect_search()
    for arc in layers[1:]:
        arc["strokes"] = []
    return H(layers)
add("F55: no strokes anywhere on icons", f55())

def f56():
    layers = perfect_search()
    # magnifier and dots all same gray (very small distinction)
    return H(layers)
add("F56: perfect colors (control 3)", f56())

def f57():
    # dots are squares (rectangles)
    layers = perfect_search()
    layers[3] = L("rectangle", 270, 320, 8, 8, GRAY_STROKE)
    layers[4] = L("rectangle", 285, 320, 8, 8, GRAY_STROKE)
    return H(layers, evts=evt(rect=3, ellipse=1))
add("F57: dots are rectangles", f57())

def f58():
    layers = perfect_search()
    # magnifier and line at same position (overlapping)
    layers[2]["x"] = 215
    layers[2]["y"] = 312
    return H(layers)
add("F58: line on magnifier (overlap)", f58())

def f59():
    # line very long (extends well beyond bar)
    layers = perfect_search()
    layers[2] = L("line", 232, 332, 1500, 12, None,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("F59: line 1500px wide", f59())

def f60():
    return H()  # control
add("F60: perfect (control)", f60())


# ─── G. Frame variants (10) ──────────────────────────────────────────
def g61():
    layers = perfect_search()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", g61())

def g62():
    layers = perfect_search()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", g62())

def g63():
    layers = perfect_search()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G63: frame image fill", g63())

def g64():
    layers = perfect_search()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("G64: frame with stroke", g64())

def g65():
    return H(frame_w=2000, frame_h=1500)
add("G65: frame oversized", g65())

def g66():
    return H(frame_w=200, frame_h=200)
add("G66: frame undersized", g66())

def g67():
    layers = perfect_search()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    return H()  # control
add("G68: default (control)", g68())

def g69():
    layers = perfect_search()
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(layers, w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames, search in 2nd", g69())

def g70():
    return H(in_frame=False)
add("G70: shapes on page (no frame)", g70())


# ─── H. Tools / events (10) ──────────────────────────────────────────
def h71():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H71: 20 undo events", h71())

def h72():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H72: align_layers used", h72())

def h73():
    sem = [make_event("session_start"),
           make_event("create_rectangle"),
           make_event("create_ellipse"), make_event("create_ellipse"),
           make_event("create_ellipse"), make_event("create_line")]
    return H(evts=sem)
add("H73: 0 tool_change events", h73())

def h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle")]
    return H(evts=sem)
add("H74: only rectangle tool used", h74())

def h75():
    return H(evts=evt(rect=10))
add("H75: 10 create_rect events", h75())

def h76():
    return H(evts=evt(extras=[make_event("create_star"), make_event("delete")]))
add("H76: create+delete star", h76())

def h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end", h77())

def h78():
    return H(evts=evt(set_fill=10))
add("H78: 10 set_fill", h78())

def h79():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H79: 50 move events", h79())

def h80():
    return H()  # control
add("H80: default events", h80())


# ─── I. Hierarchy (10) ───────────────────────────────────────────────
def i81():
    layers = perfect_search()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: shapes in group inside frame", i81())

def i82():
    layers = perfect_search()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: shapes split across 2 frames", i82())

def i83():
    layers = perfect_search()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: shapes in section (not frame)", i83())

def i84():
    layers = perfect_search()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I84: shapes in component", i84())

def i85():
    layers = perfect_search()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", i85())

def i86():
    layers = perfect_search()
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    frame = make_frame(layers, w=1280, h=832)
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: search on page 2", i86())

def i87():
    layers = perfect_search()
    frame = make_frame(layers[:1], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: bar in frame, others on page", i87())

def i88():
    layers = perfect_search()
    return make_log(layers, evt())
add("I88: shapes top-level (no frame)", i88())

def i89():
    layers = perfect_search()
    inner = make_frame(layers, w=400, h=400)
    big = make_frame([inner], w=1280, h=832)
    return make_log([big], evt())
add("I89: small inner frame in big", i89())

def i90():
    return H()  # control
add("I90: perfect (control)", i90())


# ─── J. Bizarre (10) ─────────────────────────────────────────────────
def j91():
    layers = perfect_search()
    layers[0]["rotation"] = 180
    return H(layers)
add("J91: bar rotated 180°", j91())

def j92():
    # all 5 shapes piled
    layers = []
    for t in ["rectangle", "ellipse", "line", "ellipse", "ellipse"]:
        layers.append(L(t, 500, 400, 50, 50, GRAY_STROKE,
                        strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)] if t != "rectangle" else []))
    return H(layers)
add("J92: 5 shapes piled at one point", j92())

def j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", j93())

def j94():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "Search"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J94: text 'Search'", j94())

def j95():
    layers = perfect_search()
    for arc in layers[1:]:
        arc["scaleX"] = -1
    return H(layers)
add("J95: icons mirrored", j95())

def j96():
    layers = perfect_search()
    layers[0]["w"] = 1; layers[0]["h"] = 1
    return H(layers)
add("J96: bar 1x1", j96())

def j97():
    # bar is a line type
    layers = perfect_search()
    layers[0] = L("line", 200, 300, 320, 48, LIGHT_GRAY,
                  strokes=[make_stroke(rgb=LIGHT_GRAY, weight=48)])
    return H(layers, evts=evt(rect=0, line=2))
add("J97: bar is a line", j97())

def j98():
    # all icons inside bar
    layers = perfect_search()
    return H(layers)  # default already
add("J98: perfect 4 (control)", j98())

def j99():
    # bar at far edge
    layers = perfect_search()
    for l in layers:
        l["x"] += 800
    return H(layers)
add("J99: search at right edge", j99())

def j100():
    return H()  # control
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

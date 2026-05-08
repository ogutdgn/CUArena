"""100 edge cases for task 21 — Button stack: 3 same-size rectangles, vertical, 16px gap, distinct colors."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, MAGENTA, CYAN, BLACK, WHITE, RED, GREEN, PURPLE,
    PINK, ORANGE, GOLD, YELLOW,
)
from tasks import task_21_button_stack as t
T = t.task

# Default rectangle sizes/colors
RECT_W, RECT_H, GAP = 200, 60, 16
START_X, START_Y = 540, 200


def evt(rect=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_stack(n=3, w=RECT_W, h=RECT_H, gap=GAP, colors=None):
    colors = colors or [(0.95,0.30,0.30), (0.95,0.60,0.20), (0.40,0.85,0.40)]
    layers = []
    for i in range(n):
        layers.append(L("rectangle", START_X, START_Y + i*(h+gap), w, h, colors[i % len(colors)]))
    return layers


def H(layers=None, evts=None):
    if layers is None: layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    return H(perfect_stack(n=4), evts=evt(rect=4))
add("A1: 4 rectangles", case_a1())

def case_a2():
    return H(perfect_stack(n=2), evts=evt(rect=2))
add("A2: 2 rectangles", case_a2())

def case_a3():
    return H(perfect_stack(n=1), evts=evt(rect=1))
add("A3: 1 rectangle", case_a3())

def case_a4():
    return H([], evts=[make_event("session_start")])
add("A4: empty", case_a4())

def case_a5():
    return H(perfect_stack(n=6), evts=evt(rect=6))
add("A5: 6 rectangles", case_a5())

def case_a6():
    layers = perfect_stack()
    layers.append(L("ellipse", 100, 100, 60, 60, GREEN))
    return H(layers, evts=evt(extras=[make_event("create_ellipse"),
                                       make_event("tool_change", before="rectangle", after="ellipse")]))
add("A6: 3 rects + 1 ellipse (extra)", case_a6())

def case_a7():
    layers = perfect_stack()
    layers.append(L("polygon", 100, 100, 60, 60, GREEN, sides=5))
    return H(layers, evts=evt(extras=[make_event("create_polygon"),
                                       make_event("tool_change", before="rectangle", after="polygon")]))
add("A7: 3 rects + 1 polygon", case_a7())

def case_a8():
    layers = perfect_stack(n=3) + perfect_stack(n=3)  # 6 same
    return H(layers, evts=evt(rect=6))
add("A8: 6 rectangles (doubled stack)", case_a8())

def case_a9():
    layers = perfect_stack(n=2) + [L("rectangle", 100, 800, 30, 30, BLACK)]
    return H(layers, evts=evt(rect=3))
add("A9: 2 stack + 1 small rect", case_a9())

def case_a10():
    layers = perfect_stack()
    for _ in range(3):
        layers.append(L("rectangle", 100, 700, 50, 50, GREEN))
    return H(layers, evts=evt(rect=6))
add("A10: 3 stacked + 3 random", case_a10())


# ─── B. Colors / fills ─────────────────────────────────────────────
def case_b11():
    return H()  # control
add("B11: standard stack (control)", case_b11())

def case_b12():
    return H(perfect_stack(colors=[(0.5,0.5,0.5)]*3))
add("B12: all 3 same gray (no contrast)", case_b12())

def case_b13():
    layers = perfect_stack()
    layers[0]["fills"] = [{"kind":"image","src":"x","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: rect 1 image fill", case_b13())

def case_b14():
    layers = perfect_stack()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1,"visible":True}]
    return H(layers)
add("B14: all gradient fills", case_b14())

def case_b15():
    layers = perfect_stack()
    for l in layers: l["fills"] = []
    return H(layers)
add("B15: all empty fills", case_b15())

def case_b16():
    layers = perfect_stack()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: all alpha=0", case_b16())

def case_b17():
    layers = perfect_stack()
    for l in layers: l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B17: all opacity=0.05", case_b17())

def case_b18():
    layers = perfect_stack()
    for l in layers: l["opacity"] = 0
    return H(layers)
add("B18: all layer opacity=0", case_b18())

def case_b19():
    layers = perfect_stack()
    for l in layers: l["fills"][0]["visible"] = False
    return H(layers)
add("B19: all fills visible=False", case_b19())

def case_b20():
    layers = perfect_stack()
    layers[0]["fills"].append({"kind":"image","src":"x","fit":"cover","opacity":0.5,"visible":True})
    return H(layers)
add("B20: rect 1 has 2 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    return H(perfect_stack(w=1, h=1, gap=16))
add("C21: 1×1 degenerate", case_c21())

def case_c22():
    return H(perfect_stack(w=2000, h=300, gap=16))
add("C22: huge sizes", case_c22())

def case_c23():
    # Different sizes
    layers = []
    for i, h in enumerate([60, 90, 120]):
        layers.append(L("rectangle", START_X, START_Y + i*(h+16), RECT_W, h, GREEN))
    return H(layers)
add("C23: different heights", case_c23())

def case_c24():
    # Different widths
    layers = []
    cy = START_Y
    for i, w in enumerate([100, 200, 300]):
        layers.append(L("rectangle", START_X, cy, w, 60, GREEN))
        cy += 76
    return H(layers)
add("C24: different widths", case_c24())

def case_c25():
    # Tall and skinny
    layers = perfect_stack(w=20, h=200, gap=16)
    return H(layers)
add("C25: 20×200 tall skinny", case_c25())

def case_c26():
    # Square (60×60)
    return H(perfect_stack(w=60, h=60, gap=16))
add("C26: 60×60 square", case_c26())

def case_c27():
    # Very wide (1000)
    return H(perfect_stack(w=1000, h=60, gap=16))
add("C27: 1000×60 wide", case_c27())

def case_c28():
    # Mix of sizes
    layers = [
        L("rectangle", START_X, 100, 200, 60, RED),
        L("rectangle", START_X, 200, 100, 60, GREEN),
        L("rectangle", START_X, 300, 50, 60, PURPLE),
    ]
    return H(layers)
add("C28: 3 rects with progressive widths", case_c28())

def case_c29():
    # one rect 1×1 (degenerate among normal)
    layers = perfect_stack()
    layers[1]["w"] = 1; layers[1]["h"] = 1
    return H(layers)
add("C29: middle rect 1×1", case_c29())

def case_c30():
    # All same size but tiny
    return H(perfect_stack(w=5, h=5, gap=16))
add("C30: 5×5 tiny", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    # Rects not aligned x
    layers = perfect_stack()
    layers[0]["x"] = 100
    layers[1]["x"] = 500
    layers[2]["x"] = 800
    return H(layers)
add("D31: rects diff x positions", case_d31())

def case_d32():
    # Rects same x but no consistent gap
    layers = perfect_stack()
    layers[0]["y"] = 100
    layers[1]["y"] = 250  # gap 90
    layers[2]["y"] = 600  # gap 290
    return H(layers)
add("D32: inconsistent gaps", case_d32())

def case_d33():
    # All 3 rectangles overlap (no gap)
    layers = perfect_stack(gap=-30)  # negative gap
    return H(layers)
add("D33: overlapping (negative gap)", case_d33())

def case_d34():
    # All on top of each other
    layers = perfect_stack()
    for l in layers: l["x"] = 500; l["y"] = 400
    return H(layers)
add("D34: all 3 rects identical position", case_d34())

def case_d35():
    # Rects horizontally arranged (not vertical)
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 100 + i*240, 400, RECT_W, RECT_H, [(0.95,0.3,0.3),(0.95,0.6,0.2),(0.4,0.85,0.4)][i]))
    return H(layers)
add("D35: rects horizontal (not vertical)", case_d35())

def case_d36():
    # Rects diagonal
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 100 + i*100, 100 + i*100, RECT_W, RECT_H, [(0.95,0.3,0.3),(0.95,0.6,0.2),(0.4,0.85,0.4)][i]))
    return H(layers)
add("D36: rects on diagonal", case_d36())

def case_d37():
    # Rects vertical but different gaps (some 16, some 50)
    layers = []
    cy = START_Y
    gaps = [16, 50]
    for i in range(3):
        layers.append(L("rectangle", START_X, cy, RECT_W, RECT_H, GREEN))
        cy += RECT_H + gaps[i % 2]
    return H(layers)
add("D37: alternating gaps 16/50", case_d37())

def case_d38():
    # Rects stacked but x slightly off (5 px)
    layers = perfect_stack()
    for i, l in enumerate(layers):
        l["x"] += i*15  # progressive drift
    return H(layers)
add("D38: x drifts progressively", case_d38())

def case_d39():
    # 3 rects off-frame
    layers = perfect_stack()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D39: stack off-frame right", case_d39())

def case_d40():
    # negative coords
    layers = perfect_stack()
    for l in layers: l["x"] -= 800; l["y"] -= 600
    return H(layers)
add("D40: negative coords", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────
def case_e41():
    layers = perfect_stack()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: rect 1 rotated 45°", case_e41())

def case_e42():
    layers = perfect_stack()
    for l in layers: l["rotation"] = 30
    return H(layers)
add("E42: all rotated 30°", case_e42())

def case_e43():
    layers = perfect_stack()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E43: rect 1 flipped", case_e43())

def case_e44():
    layers = perfect_stack()
    for l in layers: l["scaleY"] = -1
    return H(layers)
add("E44: all rects flipped vertically", case_e44())

def case_e45():
    # Rects with cornerRadius
    layers = perfect_stack()
    for l in layers: l["cornerRadius"] = 10
    return H(layers)
add("E45: all with cornerRadius=10", case_e45())

def case_e46():
    # Rects with extreme cornerRadius
    layers = perfect_stack()
    for l in layers: l["cornerRadius"] = 30
    return H(layers)
add("E46: cornerRadius=30 (pill-like)", case_e46())

def case_e47():
    # Rects with stroke
    layers = perfect_stack()
    for l in layers: l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E47: all with stroke", case_e47())

def case_e48():
    # Rects with effects
    layers = perfect_stack()
    from qa_per_task._helpers import make_drop_shadow
    for l in layers: l["effects"] = [make_drop_shadow()]
    return H(layers)
add("E48: all with drop shadow", case_e48())

def case_e49():
    # Rect at gap=0 (touching)
    return H(perfect_stack(gap=0))
add("E49: gap=0 (touching)", case_e49())

def case_e50():
    # gap=24 (just outside tolerance 8 from 16 = 8..24)
    return H(perfect_stack(gap=25))
add("E50: gap=25 (over tol)", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────────────
def case_f51():
    # 3 rects same color (not distinct)
    return H(perfect_stack(colors=[(0.5,0.5,0.5)]*3))
add("F51: all same color", case_f51())

def case_f52():
    # 2 same color, 1 different
    return H(perfect_stack(colors=[(0.5,0.5,0.5),(0.5,0.5,0.5),(0.9,0.3,0.3)]))
add("F52: 2 same + 1 different", case_f52())

def case_f53():
    # near-identical colors (within tolerance)
    return H(perfect_stack(colors=[(0.50,0.50,0.50),(0.51,0.51,0.51),(0.52,0.52,0.52)]))
add("F53: 3 near-identical grays", case_f53())

def case_f54():
    # 3 stacked vertical but rects are squashed (5px tall)
    return H(perfect_stack(h=5, gap=16))
add("F54: rects 5px tall", case_f54())

def case_f55():
    # Rects with varying heights
    layers = []
    cy = START_Y
    for i, (w, h) in enumerate([(200, 60), (220, 60), (240, 60)]):
        layers.append(L("rectangle", START_X, cy, w, h, GREEN))
        cy += h + 16
    return H(layers)
add("F55: rects with progressive widths", case_f55())

def case_f56():
    # Rects with completely random positions
    layers = [
        L("rectangle", 100, 100, 200, 60, RED),
        L("rectangle", 600, 400, 200, 60, GREEN),
        L("rectangle", 1100, 700, 200, 60, BLUE if False else NAVY),
    ]
    return H(layers)
add("F56: rects scattered", case_f56())

def case_f57():
    # Rects near touching (gap = 4, under tolerance)
    return H(perfect_stack(gap=4))
add("F57: gap=4 (under tol)", case_f57())

def case_f58():
    # rects stroke-only (no fill)
    layers = perfect_stack()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("F58: stroke-only rects", case_f58())

def case_f59():
    # All same exact bbox
    layers = perfect_stack()
    for l in layers:
        l["x"] = 500; l["y"] = 400; l["w"] = 200; l["h"] = 60
    return H(layers)
add("F59: all 3 identical bbox", case_f59())

def case_f60():
    # Rects at random rotations
    layers = perfect_stack()
    for i, l in enumerate(layers):
        l["rotation"] = i * 45
    return H(layers)
add("F60: rects rotated 0/45/90", case_f60())


# ─── G. Frame variants ─────────────────────────────────────────────
def case_g61():
    layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("G61: frame rotated 30°", case_g61())

def case_g62():
    layers = perfect_stack()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_stack(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, stack in 2nd", case_g63())

def case_g64():
    layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    layers = perfect_stack()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G66: tiny frame", case_g66())

def case_g67():
    layers = perfect_stack()
    frame = make_frame(layers, x=400, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    layers = perfect_stack()
    f3 = make_frame(layers, w=1000, h=600)
    f2 = make_frame([f3], w=1100, h=700)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("G68: 3-deep nested frames", case_g68())


# ─── H. Tools / events ─────────────────────────────────────────────
def case_h69():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 moves", case_h69())

def case_h70():
    sem = [make_event("session_start"),
           make_event("create_rectangle"), make_event("create_rectangle"), make_event("create_rectangle")]
    return H(evts=sem)
add("H70: 0 tool_change", case_h70())

def case_h71():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H71: align used (acceptable)", case_h71())

def case_h72():
    extras = [make_event("tool_change", before="rectangle", after="pen"),
              make_event("create_vector"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H72: pen + delete", case_h72())

def case_h73():
    return H(evts=[make_event("session_start")])
add("H73: 0 events", case_h73())

def case_h74():
    return H(evts=evt(rect=10))
add("H74: 10 create_rectangle (extras)", case_h74())

def case_h75():
    return H(evts=evt(rect=1))
add("H75: 1 create_rectangle (off by 2)", case_h75())

def case_h76():
    sem = evt() + [make_event("session_end")]*3
    return H(evts=sem)
add("H76: 3 session_end", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),  # wrong tool
           make_event("create_rectangle")]*3
    return H(evts=sem)
add("H77: ellipse tool changed but rectangles created", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("delete") for _ in range(30)]))
add("H78: 30 deletes", case_h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i79():
    layers = perfect_stack()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: stack in group inside frame", case_i79())

def case_i80():
    layers = perfect_stack()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832, x=640)
    return make_log([f1, f2], evt())
add("I80: stack split across 2 frames", case_i80())

def case_i81():
    layers = perfect_stack()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I81: stack in section", case_i81())

def case_i82():
    layers = perfect_stack()
    return make_log(layers, evt())
add("I82: stack on page (no frame)", case_i82())

def case_i83():
    layers = perfect_stack()
    f3 = make_frame(layers, w=1000, h=600)
    f2 = make_frame([f3], w=1100, h=700)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I83: 3-deep nested", case_i83())

def case_i84():
    layers = perfect_stack()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children":layers}
    return make_log([component], evt())
add("I84: stack in component", case_i84())

def case_i85():
    layers = perfect_stack()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: stack on page 2", case_i85())

def case_i86():
    layers = perfect_stack()
    g = layers
    for _ in range(3):
        g = [{"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=1280, h=832)
    return make_log([frame], evt())
add("I86: 3-deep nested groups", case_i86())

def case_i87():
    layers = perfect_stack()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: 1 in frame, 2 on page", case_i87())

def case_i88():
    layers = perfect_stack()
    f1 = make_frame([layers[0]], w=400, h=400)
    f2 = make_frame([layers[1]], w=400, h=400, x=400)
    f3 = make_frame([layers[2]], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("I88: 3 rects in 3 separate frames", case_i88())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j89():
    layers = perfect_stack()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J89: all flipped horizontally", case_j89())

def case_j90():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "stack"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J90: just text 'stack'", case_j90())

def case_j91():
    # 3 polygons (sides=4) instead of rectangles
    layers = []
    for i, c in enumerate([(0.95,0.3,0.3),(0.95,0.6,0.2),(0.4,0.85,0.4)]):
        layers.append(L("polygon", START_X, START_Y + i*(60+16), 200, 60, c, sides=4))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]*3))
add("J91: polygons (4-sided) instead of rectangles", case_j91())

def case_j92():
    # 3 ellipses
    layers = []
    for i, c in enumerate([(0.95,0.3,0.3),(0.95,0.6,0.2),(0.4,0.85,0.4)]):
        layers.append(L("ellipse", START_X, START_Y + i*(60+16), 200, 60, c))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_ellipse")]*3))
add("J92: ellipses instead of rectangles", case_j92())

def case_j93():
    layers = perfect_stack()
    # all = full frame
    for l in layers:
        l["x"] = 0; l["y"] = 0; l["w"] = 1280; l["h"] = 832
    return H(layers)
add("J93: all rects = full frame", case_j93())

def case_j94():
    # all 1×1
    return H(perfect_stack(w=1, h=1, gap=16))
add("J94: all 1×1", case_j94())

def case_j95():
    # 3 rects very close to each other (gap 0) but sizes inconsistent
    layers = perfect_stack(gap=0)
    layers[1]["w"] = 100
    return H(layers)
add("J95: gap=0, middle rect narrower", case_j95())

def case_j96():
    # Stacks vertically but reversed order
    layers = perfect_stack()
    layers[0]["y"], layers[2]["y"] = layers[2]["y"], layers[0]["y"]
    return H(layers)
add("J96: rects in reversed y-order", case_j96())

def case_j97():
    # Stack but with one in a different x
    layers = perfect_stack()
    layers[1]["x"] = START_X + 200
    return H(layers)
add("J97: middle rect shifted right", case_j97())

def case_j98():
    return H()  # control
add("J98: standard stack (control)", case_j98())

def case_j99():
    return H(perfect_stack(w=120, h=40, gap=12))
add("J99: smaller stack (control variant)", case_j99())

def case_j100():
    return H(perfect_stack(w=320, h=80, gap=20))
add("J100: larger stack (control variant)", case_j100())


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
        if flag: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95 non-control): {fp_count}/{len(CASES)}")

"""100 edge cases for task 18 — Eye icon: 3 nested ellipses (sclera, iris, pupil) sharing center.

Each case is a wrong/edge-case design that should score < 1.0.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    BLACK, DARK_GRAY, COBALT,
)
from tasks import task_18_donut as t
T = t.task

CX = 500
CY = 500
WHITE_FILL = (1.0, 1.0, 1.0)
IRIS_FILL  = (0.2, 0.5, 0.85)
PUPIL_FILL = (0.0, 0.0, 0.0)


def evt(ellipse=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_eye(sizes=(160, 100, 40)):
    """3 concentric circles: sclera, iris, pupil (largest first)."""
    fills = [WHITE_FILL, IRIS_FILL, PUPIL_FILL]
    layers = []
    for sz, c in zip(sizes, fills):
        layers.append(L("ellipse", CX-sz/2, CY-sz/2, sz, sz, c))
    return layers


def H(layers=None, evts=None):
    if layers is None: layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_eye() + [L("ellipse", CX-10, CY-10, 20, 20, GREEN)]
    return H(layers, evts=evt(ellipse=4))
add("A1: 4 ellipses (extra)", case_a1())

def case_a2():
    return H(perfect_eye()[:2], evts=evt(ellipse=2))
add("A2: 2 ellipses (missing pupil)", case_a2())

def case_a3():
    return H(perfect_eye()[:1], evts=evt(ellipse=1))
add("A3: 1 ellipse only (sclera only)", case_a3())

def case_a4():
    return H([], evts=[make_event("session_start")])
add("A4: empty design", case_a4())

def case_a5():
    layers = perfect_eye()*2  # 6 ellipses
    return H(layers, evts=evt(ellipse=6))
add("A5: 6 ellipses (doubled)", case_a5())

def case_a6():
    return H(perfect_eye()[:0] + [L("ellipse", CX-80, CY-80, 160, 160, WHITE_FILL)],
             evts=evt(ellipse=1))
add("A6: just 1 ellipse (sclera)", case_a6())

def case_a7():
    layers = perfect_eye()
    layers.extend([L("ellipse", CX+200, CY, 30, 30, RED) for _ in range(3)])
    return H(layers, evts=evt(ellipse=6))
add("A7: 3 main + 3 extra ellipses", case_a7())

def case_a8():
    layers = perfect_eye() + [L("rectangle", CX-40, CY-40, 80, 80, GREEN)]
    return H(layers, evts=evt(extras=[make_event("create_rectangle"),
                                      make_event("tool_change", before="ellipse", after="rectangle")]))
add("A8: 3 ellipses + 1 rectangle (extra)", case_a8())

def case_a9():
    return H(perfect_eye()[:2] + [L("polygon", CX-15, CY-15, 30, 30, BLACK, sides=3)],
             evts=evt(ellipse=2,
                      extras=[make_event("create_polygon"),
                              make_event("tool_change", before="ellipse", after="polygon")]))
add("A9: 2 ellipses + 1 polygon (pupil as triangle)", case_a9())

def case_a10():
    layers = [perfect_eye()[1], perfect_eye()[2]]  # iris + pupil only
    return H(layers, evts=evt(ellipse=2))
add("A10: iris + pupil (no sclera)", case_a10())


# ─── B. Colors / fills ─────────────────────────────────────────────
def case_b11():
    # 3 distinct ellipse colors (control)
    return H()
add("B11: standard fills (control)", case_b11())

def case_b12():
    # all 3 same color (no contrast)
    layers = [L("ellipse", CX-80, CY-80, 160, 160, GREEN),
              L("ellipse", CX-50, CY-50, 100, 100, GREEN),
              L("ellipse", CX-20, CY-20, 40, 40, GREEN)]
    return H(layers)
add("B12: all 3 ellipses same color", case_b12())

def case_b13():
    layers = perfect_eye()
    layers[0]["fills"] = [{"kind":"image","src":"x","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: sclera has image fill", case_b13())

def case_b14():
    layers = perfect_eye()
    layers[1]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1,"visible":True}]
    return H(layers)
add("B14: iris has gradient fill", case_b14())

def case_b15():
    layers = perfect_eye()
    for l in layers: l["fills"] = []
    return H(layers)
add("B15: all ellipses empty fills", case_b15())

def case_b16():
    layers = perfect_eye()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: all alpha=0", case_b16())

def case_b17():
    layers = perfect_eye()
    for l in layers: l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B17: all fills opacity=0.05", case_b17())

def case_b18():
    layers = perfect_eye()
    for l in layers: l["opacity"] = 0.0
    return H(layers)
add("B18: all layer opacity=0", case_b18())

def case_b19():
    layers = perfect_eye()
    for l in layers: l["fills"][0]["visible"] = False
    return H(layers)
add("B19: all fills visible=False", case_b19())

def case_b20():
    layers = perfect_eye()
    layers[0]["fills"].append({"kind":"image","src":"x","fit":"cover","opacity":0.5,"visible":True})
    return H(layers)
add("B20: sclera has 2 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    return H(perfect_eye(sizes=(1, 1, 1)))
add("C21: all 1×1 degenerate", case_c21())

def case_c22():
    return H(perfect_eye(sizes=(1500, 1000, 400)))
add("C22: huge sizes (overflow)", case_c22())

def case_c23():
    layers = [L("ellipse", CX-80, CY-40, 160, 80, WHITE_FILL),  # squashed sclera
              L("ellipse", CX-50, CY-25, 100, 50, IRIS_FILL),
              L("ellipse", CX-20, CY-10, 40, 20, PUPIL_FILL)]
    return H(layers)
add("C23: all ellipses squashed (h=w/2)", case_c23())

def case_c24():
    layers = perfect_eye()
    layers[0]["w"] = 200; layers[0]["h"] = 100  # sclera squashed
    return H(layers)
add("C24: only sclera squashed (200×100)", case_c24())

def case_c25():
    return H(perfect_eye(sizes=(60, 70, 50)))  # roughly equal sizes
add("C25: similar sized ellipses", case_c25())

def case_c26():
    return H(perfect_eye(sizes=(40, 100, 160)))  # reverse size order
add("C26: reversed size order", case_c26())

def case_c27():
    return H(perfect_eye(sizes=(160, 5, 40)))
add("C27: iris very thin (5×5)", case_c27())

def case_c28():
    return H(perfect_eye(sizes=(160, 100, 100)))  # iris and pupil same size
add("C28: iris and pupil same size", case_c28())

def case_c29():
    return H(perfect_eye(sizes=(50, 100, 40)))  # iris larger than sclera
add("C29: iris > sclera", case_c29())

def case_c30():
    return H(perfect_eye(sizes=(160, 100, 95)))  # pupil almost as big as iris
add("C30: pupil 95% of iris", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_eye()
    layers[1]["x"] = CX + 60  # iris offset
    return H(layers)
add("D31: iris offset to right", case_d31())

def case_d32():
    layers = perfect_eye()
    layers[2]["x"] = CX + 80; layers[2]["y"] = CY + 80
    return H(layers)
add("D32: pupil offset diagonally", case_d32())

def case_d33():
    layers = perfect_eye()
    for l in layers:
        l["x"] += 1500  # off-frame
    return H(layers)
add("D33: eye off-frame right", case_d33())

def case_d34():
    layers = perfect_eye()
    for l in layers:
        l["x"] -= 800; l["y"] -= 600
    return H(layers)
add("D34: negative coords", case_d34())

def case_d35():
    layers = perfect_eye()
    layers[1]["x"] = layers[0]["x"] - 30  # iris at left edge of sclera
    return H(layers)
add("D35: iris at left edge of sclera", case_d35())

def case_d36():
    layers = perfect_eye()
    layers[2]["x"] = CX  # pupil at right side of sclera
    return H(layers)
add("D36: pupil offset right", case_d36())

def case_d37():
    # all 3 ellipses non-concentric, stacked horizontally
    layers = [L("ellipse", 100, 400, 160, 160, WHITE_FILL),
              L("ellipse", 400, 400, 100, 100, IRIS_FILL),
              L("ellipse", 700, 400, 40, 40, PUPIL_FILL)]
    return H(layers)
add("D37: ellipses stacked horizontally (not nested)", case_d37())

def case_d38():
    # pupil outside iris (sclera contains pupil but iris doesn't)
    layers = perfect_eye()
    layers[2]["x"] = CX + 50; layers[2]["y"] = CY - 20
    return H(layers)
add("D38: pupil outside iris (still in sclera)", case_d38())

def case_d39():
    # iris partially outside sclera
    layers = perfect_eye()
    layers[1]["x"] = layers[0]["x"] + 50
    return H(layers)
add("D39: iris partially outside sclera", case_d39())

def case_d40():
    # pupil completely outside sclera
    layers = perfect_eye()
    layers[2]["x"] = CX + 200
    return H(layers)
add("D40: pupil outside sclera", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────
def case_e41():
    layers = perfect_eye()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: sclera rotated 45° (still circular)", case_e41())

def case_e42():
    layers = perfect_eye()
    for l in layers: l["rotation"] = 30
    return H(layers)
add("E42: all rotated 30°", case_e42())

def case_e43():
    layers = perfect_eye()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E43: sclera flipped", case_e43())

def case_e44():
    layers = perfect_eye()
    layers[1]["scaleY"] = -1
    return H(layers)
add("E44: iris vertically flipped", case_e44())

def case_e45():
    layers = perfect_eye()
    layers[1]["w"] = 200; layers[1]["h"] = 50
    layers[1]["x"] = CX - 100; layers[1]["y"] = CY - 25
    return H(layers)
add("E45: iris elongated (200×50)", case_e45())

def case_e46():
    layers = perfect_eye()
    layers[2]["w"] = 5; layers[2]["h"] = 5
    layers[2]["x"] = CX - 2.5; layers[2]["y"] = CY - 2.5
    return H(layers)
add("E46: pupil 5×5 (tiny)", case_e46())

def case_e47():
    layers = perfect_eye()
    # sclera and pupil have same exact center coords as concentric, but iris off
    layers[1]["x"] = CX - 50 + 2.5  # 2.5px off
    return H(layers)
add("E47: iris 2.5px off-center (under tol)", case_e47())

def case_e48():
    # ellipses with cornerRadius (not applicable but just to test)
    layers = perfect_eye()
    layers[0]["cornerRadius"] = 80
    return H(layers)
add("E48: sclera with cornerRadius (no effect on ellipse)", case_e48())

def case_e49():
    # 3 squares pretending to be circles
    layers = [L("rectangle", CX-80, CY-80, 160, 160, WHITE_FILL),
              L("rectangle", CX-50, CY-50, 100, 100, IRIS_FILL),
              L("rectangle", CX-20, CY-20, 40, 40, PUPIL_FILL)]
    return H(layers, evts=evt(ellipse=0,
                              extras=[make_event("create_rectangle")]*3))
add("E49: rectangles instead of ellipses", case_e49())

def case_e50():
    # 3 stars instead of ellipses
    layers = []
    for sz, fill in [(160, WHITE_FILL), (100, IRIS_FILL), (40, PUPIL_FILL)]:
        layers.append(make_layer("star", x=CX-sz/2, y=CY-sz/2, w=sz, h=sz, fill=fill,
                                 points=5, innerRatio=0.4))
    return H(layers, evts=evt(ellipse=0,
                              extras=[make_event("create_star")]*3))
add("E50: stars instead of ellipses", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────────────
def case_f51():
    # all 3 same-size, concentric (circles overlap perfectly)
    return H(perfect_eye(sizes=(100, 100, 100)))
add("F51: all 3 same-size (overlap perfectly)", case_f51())

def case_f52():
    # only 2 concentric, 3rd off
    layers = perfect_eye()
    layers[2]["x"] = CX + 100
    return H(layers)
add("F52: pupil far off-center", case_f52())

def case_f53():
    # all 3 stroke-only no fill
    layers = perfect_eye()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("F53: all stroke-only no fill", case_f53())

def case_f54():
    # all 3 squashed
    return H(perfect_eye(sizes=(160, 100, 40)))  # control... use properly squashed
add("F54: standard sizes (control variant)", case_f54())

def case_f55():
    # ellipses with massive corner radius (no-op for ellipse but adds property)
    layers = perfect_eye()
    for l in layers:
        l["cornerRadius"] = 100
    return H(layers)
add("F55: all ellipses with cornerRadius (no-op)", case_f55())

def case_f56():
    # all 3 with same fill but different alpha
    layers = perfect_eye()
    for i, l in enumerate(layers):
        l["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1.0 - i*0.3}
    return H(layers)
add("F56: same gray, different alpha", case_f56())

def case_f57():
    # iris larger than sclera (visual swap)
    return H(perfect_eye(sizes=(50, 200, 30)))
add("F57: iris (200) larger than sclera (50)", case_f57())

def case_f58():
    # pupil very large
    return H(perfect_eye(sizes=(200, 100, 90)))
add("F58: pupil 90% of iris", case_f58())

def case_f59():
    # all 3 outside the frame
    layers = perfect_eye()
    for l in layers: l["x"] += 2000
    return H(layers)
add("F59: all ellipses way off frame", case_f59())

def case_f60():
    # ellipses each in different sub-frame
    e1, e2, e3 = perfect_eye()
    f1 = make_frame([e1], w=400, h=400)
    f2 = make_frame([e2], w=400, h=400, x=400)
    f3 = make_frame([e3], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("F60: ellipses in 3 separate frames", case_f60())


# ─── G. Frame variants ─────────────────────────────────────────────
def case_g61():
    layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("G61: frame rotated 30°", case_g61())

def case_g62():
    layers = perfect_eye()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_eye(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, eye in 2nd", case_g63())

def case_g64():
    layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_eye()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G66: 200×200 tiny frame (eye doesn't fit)", case_g66())

def case_g67():
    layers = perfect_eye()
    frame = make_frame(layers, x=400, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    layers = perfect_eye()
    f3 = make_frame(layers, w=1000, h=600)
    f2 = make_frame([f3], w=1100, h=700)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("G68: 3-deep nested frames", case_g68())


# ─── H. Tools / events ─────────────────────────────────────────────
def case_h69():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 move_layer events", case_h69())

def case_h70():
    sem = [make_event("session_start"),
           make_event("create_ellipse"), make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H70: 0 tool_change events", case_h70())

def case_h71():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x"),
                              make_event("align_layers", axis="center_y")]))
add("H71: align layers used (acceptable)", case_h71())

def case_h72():
    extras = [make_event("tool_change", before="ellipse", after="pen"),
              make_event("create_vector"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H72: pen used + delete", case_h72())

def case_h73():
    return H(evts=[make_event("session_start")])
add("H73: 0 events (just session_start)", case_h73())

def case_h74():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H74: 20 deletes", case_h74())

def case_h75():
    return H(evts=evt(ellipse=10))
add("H75: 10 create_ellipse events", case_h75())

def case_h76():
    return H(evts=evt(ellipse=1))  # only 1 create_ellipse
add("H76: only 1 create_ellipse event", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_ellipse"), make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H77: rectangle tool changed but ellipses created", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H78: 50 undos", case_h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i79():
    layers = perfect_eye()
    group = {"id":"group1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: ellipses inside group inside frame", case_i79())

def case_i80():
    layers = perfect_eye()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I80: ellipses in section", case_i80())

def case_i81():
    layers = perfect_eye()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832, x=640)
    return make_log([f1, f2], evt())
add("I81: split sclera/iris+pupil across frames", case_i81())

def case_i82():
    layers = perfect_eye()
    return make_log(layers, evt())
add("I82: ellipses on page (no frame)", case_i82())

def case_i83():
    layers = perfect_eye()
    component = {"id":"comp1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children":layers}
    return make_log([component], evt())
add("I83: ellipses in component (not frame)", case_i83())

def case_i84():
    layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I84: eye on page 2", case_i84())

def case_i85():
    layers = perfect_eye()
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    layers = perfect_eye()
    g = layers
    for _ in range(3):
        g = [{"id":f"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=1280, h=832)
    return make_log([frame], evt())
add("I86: 3-deep nested groups", case_i86())

def case_i87():
    layers = perfect_eye()
    frame = make_frame(layers[:1], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only sclera in frame, others on page", case_i87())

def case_i88():
    e1, e2, e3 = perfect_eye()
    f1 = make_frame([e1], w=400, h=400)
    f2 = make_frame([e2], w=400, h=400, x=400)
    f3 = make_frame([e3], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("I88: 3 ellipses in 3 separate frames", case_i88())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j89():
    layers = perfect_eye()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J89: all flipped scaleX=-1", case_j89())

def case_j90():
    layers = perfect_eye()
    for l in layers:
        l["x"] = CX; l["y"] = CY  # all at same position
        l["w"] = 80; l["h"] = 80
    return H(layers)
add("J90: all at same point, same size", case_j90())

def case_j91():
    layers = perfect_eye()
    for l in layers:
        l["w"] = 1280; l["h"] = 832; l["x"] = 0; l["y"] = 0
    return H(layers)
add("J91: all = full frame", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "eye"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: just text 'eye'", case_j92())

def case_j93():
    # Same y, different x — 3 ellipses side-by-side
    layers = [L("ellipse", 200, CY-80, 160, 160, WHITE_FILL),
              L("ellipse", 500, CY-50, 100, 100, IRIS_FILL),
              L("ellipse", 800, CY-20, 40, 40, PUPIL_FILL)]
    return H(layers)
add("J93: 3 ellipses side-by-side", case_j93())

def case_j94():
    # 3 ellipses, but iris and pupil same color as background
    layers = perfect_eye()
    layers[1]["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1.0}  # frame color
    layers[2]["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1.0}
    return H(layers)
add("J94: iris+pupil = frame color (invisible)", case_j94())

def case_j95():
    # 3 vector ellipse-like shapes
    layers = []
    for sz in [160, 100, 40]:
        layers.append(make_layer("vector", x=CX-sz/2, y=CY-sz/2, w=sz, h=sz, fill=WHITE_FILL))
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_vector")]*3))
add("J95: 3 vectors instead of ellipses", case_j95())

def case_j96():
    # 3 ellipses at very different y positions
    layers = [L("ellipse", CX-80, 100, 160, 160, WHITE_FILL),
              L("ellipse", CX-50, 400, 100, 100, IRIS_FILL),
              L("ellipse", CX-20, 700, 40, 40, PUPIL_FILL)]
    return H(layers)
add("J96: 3 ellipses stacked vertically", case_j96())

def case_j97():
    # 3 ellipses but 2 are way smaller (1px) and 1 is normal sclera
    layers = [L("ellipse", CX-80, CY-80, 160, 160, WHITE_FILL),
              L("ellipse", CX, CY, 1, 1, IRIS_FILL),
              L("ellipse", CX+1, CY+1, 1, 1, PUPIL_FILL)]
    return H(layers)
add("J97: 1 normal ellipse + 2 tiny degenerate", case_j97())

def case_j98():
    # control: perfect
    return H()
add("J98: perfect eye (control)", case_j98())

def case_j99():
    # control: smaller eye
    return H(perfect_eye(sizes=(120, 75, 30)))
add("J99: smaller eye (control variant)", case_j99())

def case_j100():
    # control: larger eye
    return H(perfect_eye(sizes=(220, 140, 60)))
add("J100: larger eye (control variant)", case_j100())


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

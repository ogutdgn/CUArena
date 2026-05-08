"""100 edge cases for task 19 — Padlock: rect body + pen U-shackle + ellipse keyhole."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    BLACK, DARK_GRAY,
)
from tasks import task_19_padlock as t
T = t.task

# Body, key, shackle helpers
BODY_X, BODY_Y, BODY_W, BODY_H = 540, 360, 200, 160
SHACKLE_X, SHACKLE_Y, SHACKLE_W, SHACKLE_H = 580, 240, 120, 130
KEY_X, KEY_Y, KEY_W, KEY_H = 625, 420, 30, 30


def evt(rect=1, vector=1, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_padlock():
    """Rounded rectangle body, pen U-shackle, black keyhole circle."""
    body = L("rectangle", BODY_X, BODY_Y, BODY_W, BODY_H, DARK_GRAY, cornerRadius=12)
    shackle = L("vector", SHACKLE_X, SHACKLE_Y, SHACKLE_W, SHACKLE_H, fill=None,
                strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    key = L("ellipse", KEY_X, KEY_Y, KEY_W, KEY_H, BLACK)
    return [body, shackle, key]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_padlock()
    layers.append(L("rectangle", 100, 100, 50, 50, GREEN, cornerRadius=12))
    return H(layers, evts=evt(rect=2))
add("A1: 2 rectangles (extra)", case_a1())

def case_a2():
    layers = perfect_padlock()
    layers.append(L("vector", 200, 200, 60, 60, fill=None,
                    strokes=[make_stroke(rgb=GREEN, weight=14)]))
    return H(layers, evts=evt(vector=2))
add("A2: 2 vectors (extra)", case_a2())

def case_a3():
    layers = perfect_padlock()
    layers.append(L("ellipse", 300, 300, 30, 30, BLACK))
    return H(layers, evts=evt(ellipse=2))
add("A3: 2 ellipses (extra keyhole)", case_a3())

def case_a4():
    return H([perfect_padlock()[0], perfect_padlock()[1]], evts=evt(ellipse=0))
add("A4: no keyhole", case_a4())

def case_a5():
    return H([perfect_padlock()[0], perfect_padlock()[2]], evts=evt(vector=0))
add("A5: no shackle", case_a5())

def case_a6():
    return H([perfect_padlock()[1], perfect_padlock()[2]], evts=evt(rect=0))
add("A6: no body", case_a6())

def case_a7():
    return H([], evts=[make_event("session_start")])
add("A7: empty design", case_a7())

def case_a8():
    layers = perfect_padlock() * 2
    return H(layers, evts=evt(rect=2, vector=2, ellipse=2))
add("A8: doubled (2 of each)", case_a8())

def case_a9():
    layers = perfect_padlock()
    layers.extend([L("rectangle", 100, 100, 50, 50, GREEN) for _ in range(5)])
    return H(layers, evts=evt(rect=6))
add("A9: 6 rectangles total (5 extras)", case_a9())

def case_a10():
    layers = perfect_padlock()
    layers.append(L("polygon", 200, 200, 60, 60, RED, sides=5))
    return H(layers, evts=evt(extras=[make_event("create_polygon"),
                                      make_event("tool_change", before="ellipse", after="polygon")]))
add("A10: padlock + extra polygon", case_a10())


# ─── B. Colors / fills ─────────────────────────────────────────────
def case_b11():
    return H()  # control
add("B11: standard padlock (control)", case_b11())

def case_b12():
    layers = perfect_padlock()
    layers[0]["fills"][0]["color"] = {"r":1.0,"g":0.0,"b":0.0,"a":1.0}  # red body
    return H(layers)
add("B12: red body (not gray)", case_b12())

def case_b13():
    layers = perfect_padlock()
    layers[2]["fills"][0]["color"] = {"r":1.0,"g":1.0,"b":1.0,"a":1.0}  # white keyhole
    return H(layers)
add("B13: white keyhole (not black)", case_b13())

def case_b14():
    layers = perfect_padlock()
    layers[0]["fills"] = [{"kind":"image","src":"x","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B14: body image fill", case_b14())

def case_b15():
    layers = perfect_padlock()
    layers[0]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":0.3,"g":0.3,"b":0.3,"a":1}},
        {"position":1,"color":{"r":0.6,"g":0.6,"b":0.6,"a":1}}], "opacity":1,"visible":True}]
    return H(layers)
add("B15: body gradient fill", case_b15())

def case_b16():
    layers = perfect_padlock()
    layers[0]["fills"] = []
    return H(layers)
add("B16: body empty fills", case_b16())

def case_b17():
    layers = perfect_padlock()
    for l in layers:
        if l.get("fills"):
            l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B17: all fills alpha=0", case_b17())

def case_b18():
    layers = perfect_padlock()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("B18: body layer opacity=0", case_b18())

def case_b19():
    layers = perfect_padlock()
    for l in layers:
        if l.get("fills"):
            l["fills"][0]["visible"] = False
    return H(layers)
add("B19: all fills visible=False", case_b19())

def case_b20():
    layers = perfect_padlock()
    layers[0]["fills"].append({"kind":"image","src":"x","fit":"cover","opacity":0.5,"visible":True})
    return H(layers)
add("B20: body has 2 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_padlock()
    for l in layers:
        l["w"] = 1; l["h"] = 1
    return H(layers)
add("C21: all 1×1 degenerate", case_c21())

def case_c22():
    layers = perfect_padlock()
    layers[0]["w"] = 2000; layers[0]["h"] = 1500
    return H(layers)
add("C22: body huge (overflow)", case_c22())

def case_c23():
    layers = perfect_padlock()
    layers[2]["w"] = 200; layers[2]["h"] = 200  # huge keyhole (bigger than 'small')
    return H(layers)
add("C23: keyhole 200×200 (large)", case_c23())

def case_c24():
    layers = perfect_padlock()
    layers[2]["w"] = 5; layers[2]["h"] = 5
    return H(layers)
add("C24: keyhole 5×5 (tiny)", case_c24())

def case_c25():
    layers = perfect_padlock()
    layers[1]["w"] = 5; layers[1]["h"] = 5
    return H(layers)
add("C25: shackle 5×5", case_c25())

def case_c26():
    layers = perfect_padlock()
    layers[0]["w"] = 5  # body very thin
    return H(layers)
add("C26: body 5 wide", case_c26())

def case_c27():
    layers = perfect_padlock()
    layers[0]["h"] = 5  # body super flat
    return H(layers)
add("C27: body 5 tall", case_c27())

def case_c28():
    layers = perfect_padlock()
    layers[2]["w"] = 80; layers[2]["h"] = 30  # keyhole oval (not circle)
    return H(layers)
add("C28: keyhole 80×30 (oval, not circle)", case_c28())

def case_c29():
    layers = perfect_padlock()
    layers[1]["w"] = 1000; layers[1]["h"] = 1000  # shackle huge
    return H(layers)
add("C29: shackle 1000×1000", case_c29())

def case_c30():
    layers = perfect_padlock()
    layers[2]["w"] = 100; layers[2]["h"] = 100  # keyhole bigger than body
    layers[2]["x"] = 590; layers[2]["y"] = 390
    return H(layers)
add("C30: keyhole nearly as big as body", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_padlock()
    layers[2]["x"] = BODY_X - 200
    layers[2]["y"] = BODY_Y - 200
    return H(layers)
add("D31: keyhole far from body (top-left)", case_d31())

def case_d32():
    layers = perfect_padlock()
    layers[1]["x"] = 100; layers[1]["y"] = 100
    return H(layers)
add("D32: shackle in top-left corner", case_d32())

def case_d33():
    layers = perfect_padlock()
    layers[1]["y"] = BODY_Y + BODY_H + 50  # shackle below body
    return H(layers)
add("D33: shackle below body (not above)", case_d33())

def case_d34():
    layers = perfect_padlock()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D34: padlock off-frame right", case_d34())

def case_d35():
    layers = perfect_padlock()
    for l in layers: l["x"] -= 800; l["y"] -= 600
    return H(layers)
add("D35: negative coords", case_d35())

def case_d36():
    layers = perfect_padlock()
    layers[2]["x"] = BODY_X + BODY_W + 50  # keyhole outside body right
    return H(layers)
add("D36: keyhole right of body", case_d36())

def case_d37():
    layers = perfect_padlock()
    layers[0]["x"] = BODY_X + 300  # body shifted right
    return H(layers)
add("D37: body shifted right", case_d37())

def case_d38():
    layers = perfect_padlock()
    layers[1]["x"] = SHACKLE_X + 300  # shackle far right of body
    return H(layers)
add("D38: shackle 300px right of body", case_d38())

def case_d39():
    layers = perfect_padlock()
    layers[2]["x"] = BODY_X - 50; layers[2]["y"] = BODY_Y - 50  # keyhole at body's TL corner outside
    return H(layers)
add("D39: keyhole outside body's top-left", case_d39())

def case_d40():
    layers = perfect_padlock()
    layers[1]["y"] = BODY_Y + BODY_H/2  # shackle inside body (overlap)
    return H(layers)
add("D40: shackle inside body (overlap)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────
def case_e41():
    layers = perfect_padlock()
    layers[0]["cornerRadius"] = 0  # no corner radius
    return H(layers)
add("E41: body cornerRadius=0", case_e41())

def case_e42():
    layers = perfect_padlock()
    layers[0]["cornerRadius"] = 80  # body fully rounded (oval)
    return H(layers)
add("E42: body cornerRadius=80 (extreme)", case_e42())

def case_e43():
    layers = perfect_padlock()
    layers[0]["rotation"] = 45
    return H(layers)
add("E43: body rotated 45°", case_e43())

def case_e44():
    layers = perfect_padlock()
    layers[1]["strokes"] = []  # no stroke on shackle
    return H(layers)
add("E44: shackle no stroke", case_e44())

def case_e45():
    layers = perfect_padlock()
    layers[1]["strokes"][0]["weight"] = 1  # tiny stroke
    return H(layers)
add("E45: shackle stroke 1px", case_e45())

def case_e46():
    layers = perfect_padlock()
    layers[1]["strokes"][0]["weight"] = 50  # huge stroke
    return H(layers)
add("E46: shackle stroke 50px", case_e46())

def case_e47():
    layers = perfect_padlock()
    layers[2]["w"] = 30; layers[2]["h"] = 60  # keyhole tall oval
    return H(layers)
add("E47: keyhole 30×60 (tall oval)", case_e47())

def case_e48():
    layers = perfect_padlock()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E48: body flipped", case_e48())

def case_e49():
    layers = perfect_padlock()
    layers[2]["scaleY"] = -1
    return H(layers)
add("E49: keyhole flipped vertically", case_e49())

def case_e50():
    layers = perfect_padlock()
    layers[0]["cornerRadius"] = 4  # small radius (under tol of 4 for radius=12)
    return H(layers)
add("E50: body cornerRadius=4 (under tol)", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────────────
def case_f51():
    layers = perfect_padlock()
    # Replace shackle vector with an open vector (no shape)
    layers[1]["strokes"] = []
    layers[1]["fills"] = []
    return H(layers)
add("F51: shackle has no fill or stroke", case_f51())

def case_f52():
    layers = perfect_padlock()
    layers[1]["strokes"][0]["paint"]["color"] = {"r":1,"g":0,"b":0,"a":1}  # red shackle
    return H(layers)
add("F52: shackle stroke red", case_f52())

def case_f53():
    layers = perfect_padlock()
    layers[1]["strokes"][0]["weight"] = 14
    layers[1]["strokes"][0]["dash"] = {"dash":6,"gap":4}  # dashed
    return H(layers)
add("F53: shackle dashed", case_f53())

def case_f54():
    layers = perfect_padlock()
    # Shackle with very low alpha
    layers[1]["strokes"][0]["paint"]["color"]["a"] = 0.05
    return H(layers)
add("F54: shackle stroke alpha=0.05", case_f54())

def case_f55():
    layers = perfect_padlock()
    # Body without rounded corner
    del layers[0]["cornerRadius"]
    return H(layers)
add("F55: body no cornerRadius attribute", case_f55())

def case_f56():
    layers = perfect_padlock()
    # Replace ellipse with a small square as keyhole
    layers[2] = L("rectangle", KEY_X, KEY_Y, KEY_W, KEY_H, BLACK, cornerRadius=2)
    return H(layers, evts=evt(rect=2, ellipse=0))
add("F56: keyhole as rectangle", case_f56())

def case_f57():
    layers = perfect_padlock()
    # Keyhole offset 50px right
    layers[2]["x"] = KEY_X + 70
    return H(layers)
add("F57: keyhole 70px right of body center", case_f57())

def case_f58():
    layers = perfect_padlock()
    # Body width 30 (very narrow)
    layers[0]["w"] = 30
    return H(layers)
add("F58: body 30 wide (narrow)", case_f58())

def case_f59():
    layers = perfect_padlock()
    # Shackle stroke is 14 but no actual vector
    layers[1] = L("vector", SHACKLE_X, SHACKLE_Y, 0, 0, fill=None,
                  strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    return H(layers)
add("F59: shackle 0×0", case_f59())

def case_f60():
    layers = perfect_padlock()
    # 3 stacked keyholes
    layers.extend([L("ellipse", KEY_X+i*40, KEY_Y, 30, 30, BLACK) for i in range(1, 3)])
    return H(layers, evts=evt(ellipse=3))
add("F60: 3 keyholes side-by-side", case_f60())


# ─── G. Frame variants ─────────────────────────────────────────────
def case_g61():
    layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("G61: frame rotated 30°", case_g61())

def case_g62():
    layers = perfect_padlock()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_padlock(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, padlock in 2nd", case_g63())

def case_g64():
    layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    layers = perfect_padlock()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G66: tiny frame 200×200", case_g66())

def case_g67():
    layers = perfect_padlock()
    frame = make_frame(layers, x=400, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    layers = perfect_padlock()
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("G68: 3-deep nested frames", case_g68())


# ─── H. Tools / events ─────────────────────────────────────────────
def case_h69():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 move_layer events", case_h69())

def case_h70():
    sem = [make_event("session_start"),
           make_event("create_rectangle"), make_event("create_vector"), make_event("create_ellipse")]
    return H(evts=sem)
add("H70: 0 tool_change events (keyboard)", case_h70())

def case_h71():
    sem = evt()
    sem.append(make_event("align_layers", axis="center_x"))
    return H(evts=sem)
add("H71: align used (acceptable)", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H72: 20 deletes", case_h72())

def case_h73():
    return H(evts=[make_event("session_start")])
add("H73: 0 events", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"), make_event("create_vector"), make_event("create_ellipse")]
    return H(evts=sem)
add("H74: only rectangle tool_change (no pen, no ellipse)", case_h74())

def case_h75():
    sem = evt()
    sem.append(make_event("session_end")); sem.append(make_event("session_end"))
    return H(evts=sem)
add("H75: double session_end", case_h75())

def case_h76():
    return H(evts=evt(rect=5, vector=5, ellipse=5))
add("H76: 5 of each create event", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),  # skip pen
           make_event("create_rectangle"), make_event("create_vector"), make_event("create_ellipse")]
    return H(evts=sem)
add("H77: skip pen tool change", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H78: 50 undos", case_h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i79():
    layers = perfect_padlock()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: padlock in group inside frame", case_i79())

def case_i80():
    layers = perfect_padlock()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832, x=640)
    return make_log([f1, f2], evt())
add("I80: padlock split across 2 frames", case_i80())

def case_i81():
    layers = perfect_padlock()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I81: padlock in section", case_i81())

def case_i82():
    layers = perfect_padlock()
    return make_log(layers, evt())
add("I82: padlock on page (no frame)", case_i82())

def case_i83():
    layers = perfect_padlock()
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I83: 3-deep nested frames", case_i83())

def case_i84():
    layers = perfect_padlock()
    component = {"id":"comp1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[], "children":layers}
    return make_log([component], evt())
add("I84: padlock in component", case_i84())

def case_i85():
    layers = perfect_padlock()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: padlock on page 2", case_i85())

def case_i86():
    layers = perfect_padlock()
    g = layers
    for _ in range(3):
        g = [{"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=1280, h=832)
    return make_log([frame], evt())
add("I86: 3-deep nested groups", case_i86())

def case_i87():
    layers = perfect_padlock()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only body in frame, others on page", case_i87())

def case_i88():
    layers = perfect_padlock()
    f1 = make_frame([layers[0]], w=400, h=400)
    f2 = make_frame([layers[1]], w=400, h=400, x=400)
    f3 = make_frame([layers[2]], w=400, h=400, x=800)
    return make_log([f1, f2, f3], evt())
add("I88: 3 shapes in 3 separate frames", case_i88())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j89():
    layers = perfect_padlock()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J89: all flipped scaleX=-1", case_j89())

def case_j90():
    layers = perfect_padlock()
    for l in layers:
        l["x"] = 500; l["y"] = 400
        l["w"] = 80; l["h"] = 80
    return H(layers)
add("J90: all piled at one spot", case_j90())

def case_j91():
    layers = perfect_padlock()
    for l in layers:
        l["x"] = 0; l["y"] = 0; l["w"] = 1280; l["h"] = 832
    return H(layers)
add("J91: all = full frame", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "padlock"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: just text 'padlock'", case_j92())

def case_j93():
    # Body+keyhole but no shackle (incomplete lock)
    return H([perfect_padlock()[0], perfect_padlock()[2]],
             evts=evt(vector=0))
add("J93: padlock without shackle", case_j93())

def case_j94():
    layers = perfect_padlock()
    # Body has rotation but cornerRadius=12
    layers[0]["rotation"] = 90
    return H(layers)
add("J94: body rotated 90°", case_j94())

def case_j95():
    layers = perfect_padlock()
    # Shackle is now a star (5 points)
    layers[1] = make_layer("star", x=SHACKLE_X, y=SHACKLE_Y, w=SHACKLE_W, h=SHACKLE_H,
                           fill=DARK_GRAY, points=5, innerRatio=0.4)
    return H(layers, evts=evt(vector=0, extras=[make_event("create_star")]))
add("J95: shackle replaced with star", case_j95())

def case_j96():
    layers = perfect_padlock()
    # Use polygon as body
    layers[0] = L("polygon", BODY_X, BODY_Y, BODY_W, BODY_H, DARK_GRAY, sides=4)
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]))
add("J96: body is polygon (4-sided)", case_j96())

def case_j97():
    layers = perfect_padlock()
    # Body fully covers frame
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    return H(layers)
add("J97: body = frame size", case_j97())

def case_j98():
    return H()  # control
add("J98: perfect padlock (control)", case_j98())

def case_j99():
    # smaller padlock
    body = L("rectangle", 580, 400, 120, 100, DARK_GRAY, cornerRadius=12)
    shackle = L("vector", 600, 320, 80, 90, fill=None,
                strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    key = L("ellipse", 625, 440, 20, 20, BLACK)
    return H([body, shackle, key])
add("J99: smaller padlock (control variant)", case_j99())

def case_j100():
    # larger padlock
    body = L("rectangle", 440, 280, 320, 240, DARK_GRAY, cornerRadius=12)
    shackle = L("vector", 500, 120, 200, 170, fill=None,
                strokes=[make_stroke(rgb=DARK_GRAY, weight=14)])
    key = L("ellipse", 580, 380, 40, 40, BLACK)
    return H([body, shackle, key])
add("J100: larger padlock (control variant)", case_j100())


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

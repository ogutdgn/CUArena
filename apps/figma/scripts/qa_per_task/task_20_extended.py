"""100 edge cases for task 20 — Glow blob: navy frame + 2 overlapping blurred circles."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_layer_blur, make_drop_shadow,
    score_task, NAVY, MAGENTA, CYAN, PINK, ORANGE, WHITE, YELLOW, GREEN, RED,
    PURPLE, GOLD, BLACK, COBALT,
)
from tasks import task_20_glow_blob as t
T = t.task

C1_X, C1_Y, C1_R = 250, 250, 200
C2_X, C2_Y, C2_R = 310, 270, 200


def evt(ellipse=2, frame_set=True, extras=()):
    sem = [make_event("session_start")]
    if frame_set:
        sem.append(make_event("tool_change", before="select", after="frame"))
        sem.append(make_event("tool_change", before="frame", after="ellipse"))
    else:
        sem.append(make_event("tool_change", before="select", after="ellipse"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_glow(c1=MAGENTA, c2=CYAN, blur=80, frame_color=NAVY, overlap=True, blur2=None):
    blur2 = blur2 or blur
    e1 = make_layer("ellipse", x=C1_X, y=C1_Y, w=C1_R, h=C1_R, fill=c1,
                    effects=[make_layer_blur(radius=blur)])
    e2x = C2_X if overlap else 700
    e2 = make_layer("ellipse", x=e2x, y=C2_Y, w=C2_R, h=C2_R, fill=c2,
                    effects=[make_layer_blur(radius=blur2)])
    return [e1, e2], frame_color


def H(layers_and_frame_color=None, frame_w=900, frame_h=900, evts=None):
    if layers_and_frame_color is None:
        layers, frame_color = perfect_glow()
    else:
        layers, frame_color = layers_and_frame_color
    frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_color)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers, fc = perfect_glow()
    layers.append(make_layer("ellipse", x=600, y=300, w=100, h=100, fill=GREEN,
                             effects=[make_layer_blur(radius=80)]))
    return H((layers, fc), evts=evt(ellipse=3))
add("A1: 3 ellipses (extra)", case_a1())

def case_a2():
    layers, fc = perfect_glow()
    return H(([layers[0]], fc), evts=evt(ellipse=1))
add("A2: 1 ellipse (missing one)", case_a2())

def case_a3():
    return H(([], NAVY), evts=evt(ellipse=0))
add("A3: 0 ellipses", case_a3())

def case_a4():
    layers, fc = perfect_glow()
    return H((layers + layers, fc), evts=evt(ellipse=4))
add("A4: 4 ellipses (doubled)", case_a4())

def case_a5():
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA)  # no blur
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN)
    return H(([e1, e2], NAVY))
add("A5: 2 ellipses no blur", case_a5())

def case_a6():
    layers, fc = perfect_glow()
    layers.append(make_layer("rectangle", x=100, y=100, w=50, h=50, fill=GREEN))
    return H((layers, fc), evts=evt(ellipse=2,
                                   extras=[make_event("create_rectangle"),
                                           make_event("tool_change", before="ellipse", after="rectangle")]))
add("A6: 2 ellipses + 1 rectangle (extra)", case_a6())

def case_a7():
    # 6 ellipses (5 extra)
    layers, fc = perfect_glow()
    for i in range(4):
        layers.append(make_layer("ellipse", x=100+i*60, y=600, w=50, h=50, fill=GREEN,
                                 effects=[make_layer_blur(radius=80)]))
    return H((layers, fc), evts=evt(ellipse=6))
add("A7: 6 ellipses", case_a7())

def case_a8():
    return H(([], NAVY), evts=[make_event("session_start")])
add("A8: empty", case_a8())

def case_a9():
    layers, fc = perfect_glow()
    layers.append(make_layer("polygon", x=100, y=100, w=50, h=50, fill=GREEN, sides=5))
    return H((layers, fc), evts=evt(extras=[make_event("create_polygon"),
                                            make_event("tool_change", before="ellipse", after="polygon")]))
add("A9: 2 ellipses + 1 polygon", case_a9())

def case_a10():
    # 2 frames each with 1 ellipse — "split design"
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    f1 = make_frame([e1], w=600, h=600, fill=NAVY)
    f2 = make_frame([e2], w=600, h=600, fill=NAVY)
    return make_log([f1, f2], evt())
add("A10: each ellipse in own frame", case_a10())


# ─── B. Colors / fills ─────────────────────────────────────────────
def case_b11():
    return H()
add("B11: standard glow (control)", case_b11())

def case_b12():
    # both same color
    return H((perfect_glow(c1=MAGENTA, c2=MAGENTA)[0], NAVY))
add("B12: both ellipses magenta (same color)", case_b12())

def case_b13():
    # frame light gray, not navy
    return H((perfect_glow()[0], (0.95, 0.95, 0.95)))
add("B13: frame is light gray (not navy)", case_b13())

def case_b14():
    # ellipse 1 image fill
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=None,
                    effects=[make_layer_blur(radius=80)])
    e1["fills"] = [{"kind":"image","src":"x","fit":"cover","opacity":1,"visible":True}]
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("B14: e1 image fill", case_b14())

def case_b15():
    # both gradient
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=None,
                    effects=[make_layer_blur(radius=80)])
    e1["fills"] = [{"kind":"gradient","stops":[{"position":0,"color":{"r":1,"g":0,"b":1,"a":1}},
                                                 {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],
                    "opacity":1,"visible":True}]
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=None,
                    effects=[make_layer_blur(radius=80)])
    e2["fills"] = e1["fills"][:]
    return H(([e1, e2], NAVY))
add("B15: both ellipses gradient", case_b15())

def case_b16():
    # ellipses fills empty
    layers, fc = perfect_glow()
    layers[0]["fills"] = []
    layers[1]["fills"] = []
    return H((layers, fc))
add("B16: both ellipses empty fills", case_b16())

def case_b17():
    # ellipses alpha=0
    layers, fc = perfect_glow()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H((layers, fc))
add("B17: both fills alpha=0", case_b17())

def case_b18():
    # layer opacity=0
    layers, fc = perfect_glow()
    for l in layers: l["opacity"] = 0
    return H((layers, fc))
add("B18: all layer opacity=0", case_b18())

def case_b19():
    # all visible=False
    layers, fc = perfect_glow()
    for l in layers: l["fills"][0]["visible"] = False
    return H((layers, fc))
add("B19: all fills visible=False", case_b19())

def case_b20():
    # ellipse stacked fills
    layers, fc = perfect_glow()
    layers[0]["fills"].append({"kind":"image","src":"x","fit":"cover","opacity":0.5,"visible":True})
    return H((layers, fc))
add("B20: e1 has 2 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers, fc = perfect_glow()
    for l in layers: l["w"] = 1; l["h"] = 1
    return H((layers, fc))
add("C21: 1×1 degenerate", case_c21())

def case_c22():
    layers, fc = perfect_glow()
    for l in layers: l["w"] = 5000; l["h"] = 5000
    return H((layers, fc))
add("C22: 5000×5000 huge", case_c22())

def case_c23():
    # squashed ellipses
    e1 = make_layer("ellipse", x=300, y=300, w=400, h=50, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=320, y=320, w=400, h=50, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("C23: ellipses 400×50 (squashed)", case_c23())

def case_c24():
    # Different sizes (very different)
    layers, fc = perfect_glow()
    layers[1]["w"] = 50; layers[1]["h"] = 50
    return H((layers, fc))
add("C24: e2 is 50×50 (much smaller)", case_c24())

def case_c25():
    # both very tall
    e1 = make_layer("ellipse", x=300, y=100, w=80, h=400, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=350, y=120, w=80, h=400, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("C25: ellipses 80×400 (vertical)", case_c25())

def case_c26():
    # both tiny
    layers, fc = perfect_glow()
    for l in layers: l["w"] = 5; l["h"] = 5
    return H((layers, fc))
add("C26: 5×5 tiny", case_c26())

def case_c27():
    # frame too small
    return H(perfect_glow(), frame_w=100, frame_h=100)
add("C27: frame 100×100 (tiny)", case_c27())

def case_c28():
    # frame too big
    return H(perfect_glow(), frame_w=3000, frame_h=3000)
add("C28: frame 3000×3000 (huge)", case_c28())

def case_c29():
    # frame square aspect 1:1
    return H(perfect_glow(), frame_w=400, frame_h=400)
add("C29: frame 400×400", case_c29())

def case_c30():
    # ellipses bigger than frame
    layers, fc = perfect_glow()
    for l in layers: l["w"] = 1500; l["h"] = 1500
    return H((layers, fc))
add("C30: ellipses 1500×1500 (bigger than frame)", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    # e1 way off frame
    layers, fc = perfect_glow()
    layers[0]["x"] = 2000
    return H((layers, fc))
add("D31: e1 at x=2000 (off-frame)", case_d31())

def case_d32():
    # e2 way off
    layers, fc = perfect_glow()
    layers[1]["x"] = -500
    return H((layers, fc))
add("D32: e2 at negative x", case_d32())

def case_d33():
    # both at frame top-left
    layers, fc = perfect_glow()
    for l in layers: l["x"] = 0; l["y"] = 0
    return H((layers, fc))
add("D33: both at TL corner", case_d33())

def case_d34():
    # ellipses very far apart (no overlap)
    layers, fc = perfect_glow()
    layers[0]["x"] = 50
    layers[1]["x"] = 700
    return H((layers, fc))
add("D34: ellipses far apart (no overlap)", case_d34())

def case_d35():
    # ellipses identical position (perfect overlap)
    layers, fc = perfect_glow()
    layers[1]["x"] = layers[0]["x"]
    layers[1]["y"] = layers[0]["y"]
    return H((layers, fc))
add("D35: identical position (perfect overlap)", case_d35())

def case_d36():
    # ellipses just barely touching (no real overlap)
    e1 = make_layer("ellipse", x=200, y=200, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=400, y=200, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("D36: ellipses just touching (edge-to-edge)", case_d36())

def case_d37():
    # tiny overlap (1px)
    e1 = make_layer("ellipse", x=200, y=200, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=399, y=200, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("D37: 1px overlap", case_d37())

def case_d38():
    # 90% overlap
    layers, fc = perfect_glow()
    layers[1]["x"] = layers[0]["x"] + 20
    return H((layers, fc))
add("D38: 90% overlap (almost identical)", case_d38())

def case_d39():
    # ellipses outside frame
    layers, fc = perfect_glow()
    for l in layers: l["x"] += 1500; l["y"] += 1500
    return H((layers, fc))
add("D39: ellipses way off frame", case_d39())

def case_d40():
    # ellipses exactly at frame edges
    layers, fc = perfect_glow()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[1]["x"] = 700; layers[1]["y"] = 700
    return H((layers, fc))
add("D40: ellipses at frame corners", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────
def case_e41():
    # rotation 45 (still circle)
    layers, fc = perfect_glow()
    layers[0]["rotation"] = 45
    return H((layers, fc))
add("E41: e1 rotated 45°", case_e41())

def case_e42():
    # blur radius 0 (no blur)
    layers, fc = perfect_glow(blur=0)
    return H((layers, fc))
add("E42: blur radius 0", case_e42())

def case_e43():
    # blur radius 200 (excessive)
    layers, fc = perfect_glow(blur=200)
    return H((layers, fc))
add("E43: blur radius 200", case_e43())

def case_e44():
    # only one has blur
    layers = []
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN)  # no blur
    return H(([e1, e2], NAVY))
add("E44: only e1 has blur", case_e44())

def case_e45():
    # blur is drop shadow not layer_blur
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_drop_shadow(x=0, y=0, blur=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_drop_shadow(x=0, y=0, blur=80)])
    return H(([e1, e2], NAVY))
add("E45: drop shadow instead of layer blur", case_e45())

def case_e46():
    # ellipses flipped
    layers, fc = perfect_glow()
    for l in layers: l["scaleX"] = -1
    return H((layers, fc))
add("E46: ellipses flipped", case_e46())

def case_e47():
    # ellipses with stroke
    layers, fc = perfect_glow()
    for l in layers:
        l["strokes"] = [{"paint":{"kind":"solid","color":{"r":1,"g":1,"b":0,"a":1}},
                         "weight":4,"alignment":"center","dash":None,"visible":True}]
    return H((layers, fc))
add("E47: ellipses with stroke", case_e47())

def case_e48():
    # 2 ellipses with cornerRadius
    layers, fc = perfect_glow()
    for l in layers: l["cornerRadius"] = 40
    return H((layers, fc))
add("E48: ellipses with cornerRadius (no-op)", case_e48())

def case_e49():
    # blur radius = 1 (under tolerance)
    layers, fc = perfect_glow(blur=1)
    return H((layers, fc))
add("E49: blur radius 1 (very low)", case_e49())

def case_e50():
    # blur 100 (within tolerance 80±20)
    layers, fc = perfect_glow(blur=100)
    return H((layers, fc))
add("E50: blur radius 100 (within tol)", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────────────
def case_f51():
    # diff shapes for ellipses
    e1 = make_layer("rectangle", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("rectangle", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY), evts=evt(ellipse=0,
                                        extras=[make_event("create_rectangle")]*2))
add("F51: rectangles instead of ellipses", case_f51())

def case_f52():
    # one ellipse, one polygon
    layers, fc = perfect_glow()
    layers[1] = make_layer("polygon", x=360, y=320, w=200, h=200, fill=CYAN,
                           effects=[make_layer_blur(radius=80)], sides=6)
    return H((layers, fc), evts=evt(ellipse=1, extras=[make_event("create_polygon"),
                                                        make_event("tool_change", before="ellipse", after="polygon")]))
add("F52: 1 ellipse + 1 polygon", case_f52())

def case_f53():
    # ellipses are oval (not circle)
    layers, fc = perfect_glow()
    layers[0]["w"] = 300; layers[0]["h"] = 100
    layers[1]["w"] = 300; layers[1]["h"] = 100
    return H((layers, fc))
add("F53: ellipses 300×100 (oval)", case_f53())

def case_f54():
    # blur is image filter not layer_blur
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[{"kind":"background_blur","radius":80,"visible":True}])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[{"kind":"background_blur","radius":80,"visible":True}])
    return H(([e1, e2], NAVY))
add("F54: background blur instead of layer blur", case_f54())

def case_f55():
    # layer_blur invisible
    layers, fc = perfect_glow()
    for l in layers:
        l["effects"][0]["visible"] = False
    return H((layers, fc))
add("F55: layer_blur visible=False", case_f55())

def case_f56():
    # 2 ellipses, only 1 has blur, but it's a dark color (looks intentionally hidden)
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=NAVY)  # navy on navy
    return H(([e1, e2], NAVY))
add("F56: e2 = navy (camouflaged) no blur", case_f56())

def case_f57():
    # 2 same colored ellipses
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("F57: both ellipses MAGENTA (same)", case_f57())

def case_f58():
    # 2 ellipses with blur radius 5
    layers, fc = perfect_glow(blur=5)
    return H((layers, fc))
add("F58: blur radius 5 (barely blurred)", case_f58())

def case_f59():
    # ellipses with hugely different blurs
    layers, fc = perfect_glow(blur=10, blur2=200)
    return H((layers, fc))
add("F59: blurs 10 and 200 (very different)", case_f59())

def case_f60():
    # one circle, one square (and blur), at same location
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("rectangle", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY), evts=evt(ellipse=1,
                                        extras=[make_event("create_rectangle"),
                                                make_event("tool_change", before="ellipse", after="rectangle")]))
add("F60: 1 ellipse + 1 rect (overlapping)", case_f60())


# ─── G. Frame variants ─────────────────────────────────────────────
def case_g61():
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=fc)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    # nested frames
    layers, fc = perfect_glow()
    inner = make_frame(layers, w=600, h=600, fill=fc)
    outer = make_frame([inner], w=900, h=900, fill=NAVY)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    # 2 frames, glow in 2nd
    f1 = make_frame([], w=900, h=900, fill=NAVY)
    layers, fc = perfect_glow()
    f2 = make_frame(layers, w=900, h=900, fill=fc)
    return make_log([f1, f2], evt())
add("G63: 2 frames, glow in 2nd", case_g63())

def case_g64():
    # frame with stroke
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=fc)
    frame["strokes"] = [{"paint":{"kind":"solid","color":{"r":1,"g":1,"b":1,"a":1}},
                         "weight":4,"alignment":"center","dash":None,"visible":True}]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    # frame image fill (not navy)
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=None)
    frame["fills"] = [{"kind":"image","src":"navy.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    # frame transparent
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=None)
    return make_log([frame], evt())
add("G66: frame no fill", case_g66())

def case_g67():
    # frame translated
    layers, fc = perfect_glow()
    frame = make_frame(layers, x=400, y=300, w=900, h=900, fill=fc)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    # Frame is not navy — light gray
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=(0.95, 0.95, 0.95))
    return make_log([frame], evt())
add("G68: frame light gray (not navy)", case_g68())


# ─── H. Tools / events ─────────────────────────────────────────────
def case_h69():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H69: 50 move events", case_h69())

def case_h70():
    return H(evts=[make_event("session_start"),
                   make_event("create_ellipse"), make_event("create_ellipse")])
add("H70: 0 tool_change events (no frame tool)", case_h70())

def case_h71():
    # frame tool used but no ellipse tool
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H71: only frame tool changed (no ellipse tool)", case_h71())

def case_h72():
    # ellipse tool used but no frame tool
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H72: only ellipse tool changed (no frame tool)", case_h72())

def case_h73():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H73: align used (acceptable)", case_h73())

def case_h74():
    return H(evts=evt(extras=[make_event("delete") for _ in range(30)]))
add("H74: 30 deletes", case_h74())

def case_h75():
    return H(evts=evt(ellipse=10))
add("H75: 10 create_ellipse events", case_h75())

def case_h76():
    return H(evts=evt(ellipse=1))
add("H76: 1 create_ellipse event (off by 1)", case_h76())

def case_h77():
    sem = evt() + [make_event("session_end"), make_event("session_end")]
    return H(evts=sem)
add("H77: 2 session_end events", case_h77())

def case_h78():
    return H(evts=[make_event("session_start")])
add("H78: 0 events", case_h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i79():
    # ellipses on page (no frame at all)
    layers, fc = perfect_glow()
    return make_log(layers, evt())
add("I79: ellipses on page (no frame)", case_i79())

def case_i80():
    # group inside frame
    layers, fc = perfect_glow()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[], "children":layers}
    frame = make_frame([group], w=900, h=900, fill=fc)
    return make_log([frame], evt())
add("I80: group inside frame", case_i80())

def case_i81():
    # ellipses split across 2 frames
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    f1 = make_frame([e1], w=600, h=600, fill=NAVY)
    f2 = make_frame([e2], w=600, h=600, fill=NAVY, x=600)
    return make_log([f1, f2], evt())
add("I81: ellipses in 2 frames", case_i81())

def case_i82():
    # ellipses in section
    layers, fc = perfect_glow()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":900,"h":900,
               "fills":[{"kind":"solid","color":{"r":fc[0],"g":fc[1],"b":fc[2],"a":1},"opacity":1,"visible":True}],
               "children":layers}
    return make_log([section], evt())
add("I82: ellipses in section (not frame)", case_i82())

def case_i83():
    # ellipses in component
    layers, fc = perfect_glow()
    component = {"id":"comp1","type":"component","x":0,"y":0,"w":900,"h":900,
                 "fills":[],"strokes":[],"effects":[], "children":layers}
    return make_log([component], evt())
add("I83: ellipses in component", case_i83())

def case_i84():
    # glow on page 2
    layers, fc = perfect_glow()
    frame = make_frame(layers, w=900, h=900, fill=fc)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I84: glow on page 2", case_i84())

def case_i85():
    # 3-deep nested frames
    layers, fc = perfect_glow()
    f3 = make_frame(layers, w=600, h=600, fill=fc)
    f2 = make_frame([f3], w=700, h=700, fill=fc)
    f1 = make_frame([f2], w=900, h=900, fill=fc)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    # 3-deep nested groups
    layers, fc = perfect_glow()
    g = layers
    for _ in range(3):
        g = [{"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
              "fills":[],"strokes":[],"effects":[],"children":g}]
    frame = make_frame(g, w=900, h=900, fill=fc)
    return make_log([frame], evt())
add("I86: 3-deep nested groups", case_i86())

def case_i87():
    # only e1 in frame, e2 on page
    layers, fc = perfect_glow()
    frame = make_frame([layers[0]], w=900, h=900, fill=fc)
    return make_log([frame, layers[1]], evt())
add("I87: 1 ellipse in frame, 1 on page", case_i87())

def case_i88():
    # 2 ellipses in 2 separate frames (same as I81 different)
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    f1 = make_frame([e1], w=400, h=400, fill=NAVY)
    f2 = make_frame([e2], w=400, h=400, fill=NAVY, x=500)
    return make_log([f1, f2], evt())
add("I88: ellipses in 2 separate frames", case_i88())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j89():
    # text spelling 'glow'
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "glow"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J89: text 'glow'", case_j89())

def case_j90():
    # both ellipses fully cover frame
    e1 = make_layer("ellipse", x=0, y=0, w=900, h=900, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=0, y=0, w=900, h=900, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("J90: ellipses = full frame", case_j90())

def case_j91():
    # both flipped scaleY=-1
    layers, fc = perfect_glow()
    for l in layers: l["scaleY"] = -1
    return H((layers, fc))
add("J91: ellipses flipped vertically", case_j91())

def case_j92():
    # blur radius -10 (negative, invalid)
    layers, fc = perfect_glow(blur=-10)
    return H((layers, fc))
add("J92: blur radius -10", case_j92())

def case_j93():
    # ellipses are stars
    e1 = make_layer("star", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    points=5, innerRatio=0.4, effects=[make_layer_blur(radius=80)])
    e2 = make_layer("star", x=360, y=320, w=200, h=200, fill=CYAN,
                    points=5, innerRatio=0.4, effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY), evts=evt(ellipse=0, extras=[make_event("create_star")]*2))
add("J93: stars instead of ellipses", case_j93())

def case_j94():
    # ellipses hugely overlapping (e2 inside e1)
    layers, fc = perfect_glow()
    layers[1]["x"] = layers[0]["x"] + 30
    layers[1]["y"] = layers[0]["y"] + 30
    layers[1]["w"] = 30; layers[1]["h"] = 30
    return H((layers, fc))
add("J94: e2 30×30 inside e1", case_j94())

def case_j95():
    # 2 ellipses but only 1 has fill (other transparent)
    layers, fc = perfect_glow()
    layers[1]["fills"] = []
    return H((layers, fc))
add("J95: e2 has no fill", case_j95())

def case_j96():
    # both ellipses at frame center, exact same size
    e1 = make_layer("ellipse", x=350, y=350, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=350, y=350, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("J96: 2 ellipses same exact bbox", case_j96())

def case_j97():
    # blur radius is 1000 (extreme)
    layers, fc = perfect_glow(blur=1000)
    return H((layers, fc))
add("J97: blur radius 1000", case_j97())

def case_j98():
    return H()  # control
add("J98: standard glow (control)", case_j98())

def case_j99():
    # smaller variant
    e1 = make_layer("ellipse", x=350, y=350, w=120, h=120, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=400, y=370, w=120, h=120, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("J99: smaller glow (control variant)", case_j99())

def case_j100():
    # larger variant
    e1 = make_layer("ellipse", x=200, y=200, w=300, h=300, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=300, y=250, w=300, h=300, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H(([e1, e2], NAVY))
add("J100: larger glow (control variant)", case_j100())


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

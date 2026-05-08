"""100 edge cases for task 16 (speech bubble: rounded rect + triangle tail, light-gray fill)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_16_speech_bubble as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
LIGHT_GRAY = (0.85, 0.85, 0.85)
DARK_GRAY = (0.30, 0.30, 0.30)


def evt(rect=1, polygon=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.append(make_event("tool_change", before="rectangle", after="polygon"))
    for _ in range(polygon):
        sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bubble():
    """Rounded rectangle bubble + triangle tail at bottom-left, both light-gray."""
    bubble = L("rectangle", 400, 250, 480, 240, LIGHT_GRAY, cornerRadius=16)
    bubble["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    tail = make_layer("polygon", x=420, y=470, w=80, h=80, fill=LIGHT_GRAY, sides=3)
    tail["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    return [bubble, tail]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bubble()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────
def case_a1():
    layers = perfect_bubble()
    extra = L("rectangle", 100, 100, 200, 100, LIGHT_GRAY, cornerRadius=16)
    extra["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    layers.insert(0, extra)
    return H(layers, evts=evt(rect=2, polygon=1))
add("A1: 2 rects + 1 polygon", case_a1())

def case_a2():
    """0 rectangles + 1 polygon."""
    layers = perfect_bubble()[1:]
    return H(layers, evts=evt(rect=0, polygon=1))
add("A2: 0 rects + 1 polygon", case_a2())

def case_a3():
    """1 rect + 0 polygons."""
    layers = perfect_bubble()[:1]
    return H(layers, evts=evt(rect=1, polygon=0))
add("A3: 1 rect + 0 polygons", case_a3())

def case_a4():
    """2 polygons (extra tail)."""
    layers = perfect_bubble()
    extra = make_layer("polygon", x=850, y=470, w=80, h=80, fill=LIGHT_GRAY, sides=3)
    extra["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    layers.append(extra)
    return H(layers, evts=evt(rect=1, polygon=2))
add("A4: 1 rect + 2 polygons", case_a4())

def case_a5():
    return H([], evts=evt(rect=0, polygon=0))
add("A5: 0 layers", case_a5())

def case_a6():
    """Doubled bubble."""
    layers = perfect_bubble()*2
    return H(layers, evts=evt(rect=2, polygon=2))
add("A6: 2 bubbles + 2 tails", case_a6())

def case_a7():
    """1 rect + 1 polygon + extra ellipse."""
    layers = perfect_bubble()
    layers.append(L("ellipse", 200, 200, 80, 80, LIGHT_GRAY))
    return H(layers, evts=evt(rect=1, polygon=1, extras=[make_event("create_ellipse")]))
add("A7: rect + polygon + ellipse", case_a7())

def case_a8():
    """Just 1 rectangle (no tail at all)."""
    layers = [perfect_bubble()[0]]
    return H(layers, evts=evt(rect=1, polygon=0))
add("A8: 1 rect only (no tail)", case_a8())

def case_a9():
    return H(perfect_bubble(), evts=evt(rect=1, polygon=1))
add("A9: control perfect", case_a9())

def case_a10():
    """3 rects 1 polygon."""
    layers = perfect_bubble()
    layers.insert(0, L("rectangle", 50, 50, 80, 80, LIGHT_GRAY, cornerRadius=8,
                        strokes=[make_stroke(rgb=DARK_GRAY, weight=2)]))
    layers.insert(0, L("rectangle", 200, 50, 80, 80, LIGHT_GRAY, cornerRadius=8,
                        strokes=[make_stroke(rgb=DARK_GRAY, weight=2)]))
    return H(layers, evts=evt(rect=3, polygon=1))
add("A10: 3 rects + 1 polygon", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────
def case_b11():
    """Rect white, polygon light-gray (mismatched)."""
    layers = perfect_bubble()
    layers[0]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    return H(layers)
add("B11: rect white, polygon LIGHT_GRAY", case_b11())

def case_b12():
    """Both image fills."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B12: image fills", case_b12())

def case_b13():
    """Rect blue, polygon light-gray."""
    layers = perfect_bubble()
    layers[0]["fills"][0]["color"] = {"r":0.2,"g":0.4,"b":0.85,"a":1}
    return H(layers)
add("B13: rect blue", case_b13())

def case_b14():
    """Both gradient fills."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":1,"b":1,"a":1}},
            {"position":1,"color":{"r":0.5,"g":0.5,"b":0.5,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B14: gradient fills", case_b14())

def case_b15():
    """No fills."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B15: no fills", case_b15())

def case_b16():
    """Both pure black."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"][0]["color"] = {"r":0,"g":0,"b":0,"a":1}
    return H(layers)
add("B16: both black", case_b16())

def case_b17():
    """Rect = polygon different shades of gray."""
    layers = perfect_bubble()
    layers[0]["fills"][0]["color"] = {"r":0.85,"g":0.85,"b":0.85,"a":1}
    layers[1]["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1}
    return H(layers)
add("B17: rect light gray, polygon medium gray", case_b17())

def case_b18():
    """Stroke missing on polygon."""
    layers = perfect_bubble()
    layers[1]["strokes"] = []
    return H(layers)
add("B18: polygon missing stroke", case_b18())

def case_b19():
    """alpha=0 fills."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: alpha=0", case_b19())

def case_b20():
    """fill opacity=0.05."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B20: fill opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────
def case_c21():
    """Bubble too small (50×50)."""
    layers = perfect_bubble()
    layers[0]["w"] = 50; layers[0]["h"] = 50
    return H(layers)
add("C21: bubble 50×50", case_c21())

def case_c22():
    """Bubble huge (1200×800)."""
    layers = perfect_bubble()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1200; layers[0]["h"] = 800
    return H(layers)
add("C22: bubble 1200×800", case_c22())

def case_c23():
    """Bubble 0×0."""
    layers = perfect_bubble()
    layers[0]["w"] = 0; layers[0]["h"] = 0
    return H(layers)
add("C23: bubble degenerate 0×0", case_c23())

def case_c24():
    """Tail huge (200×200)."""
    layers = perfect_bubble()
    layers[1]["w"] = 200; layers[1]["h"] = 200
    return H(layers)
add("C24: tail 200×200", case_c24())

def case_c25():
    """Tail tiny (5×5)."""
    layers = perfect_bubble()
    layers[1]["w"] = 5; layers[1]["h"] = 5
    return H(layers)
add("C25: tail 5×5", case_c25())

def case_c26():
    """Both tiny."""
    layers = perfect_bubble()
    for l in layers:
        l["w"] = 5; l["h"] = 5
    return H(layers)
add("C26: both 5×5", case_c26())

def case_c27():
    """Bubble = tail size (similar)."""
    layers = perfect_bubble()
    layers[0]["w"] = 80; layers[0]["h"] = 80
    return H(layers)
add("C27: bubble same size as tail", case_c27())

def case_c28():
    """Bubble super-thin (480×10)."""
    layers = perfect_bubble()
    layers[0]["h"] = 10
    return H(layers)
add("C28: bubble 480×10 thin", case_c28())

def case_c29():
    """Bubble super-tall (50×500)."""
    layers = perfect_bubble()
    layers[0]["w"] = 50; layers[0]["h"] = 500
    return H(layers)
add("C29: bubble 50×500 tall", case_c29())

def case_c30():
    """Tail wider than bubble."""
    layers = perfect_bubble()
    layers[1]["w"] = 600
    return H(layers)
add("C30: tail wider than bubble", case_c30())


# ─── D. Position ────────────────────────────────────────────
def case_d31():
    """Tail far away from bubble (no overlap)."""
    layers = perfect_bubble()
    layers[1]["x"] = 1100; layers[1]["y"] = 100
    return H(layers)
add("D31: tail far from bubble", case_d31())

def case_d32():
    """Off-frame top-left."""
    layers = perfect_bubble()
    for l in layers:
        l["x"] -= 600; l["y"] -= 400
    return H(layers)
add("D32: off-frame top-left", case_d32())

def case_d33():
    """Negative y."""
    layers = perfect_bubble()
    for l in layers:
        l["y"] -= 1000
    return H(layers)
add("D33: at negative y", case_d33())

def case_d34():
    """Tail above bubble."""
    layers = perfect_bubble()
    layers[1]["y"] = 100
    return H(layers)
add("D34: tail above bubble", case_d34())

def case_d35():
    """Tail centered on bubble (overlapping middle)."""
    layers = perfect_bubble()
    layers[1]["x"] = 600; layers[1]["y"] = 350
    return H(layers)
add("D35: tail in middle of bubble", case_d35())

def case_d36():
    """Bubble + tail at frame edge."""
    layers = perfect_bubble()
    layers[0]["x"] = 1200
    layers[1]["x"] = 1230
    return H(layers)
add("D36: at frame edge", case_d36())

def case_d37():
    """Tail at top-left of bubble (correct per prompt)."""
    layers = perfect_bubble()
    layers[1]["x"] = 380; layers[1]["y"] = 220  # top-left adjacent
    return H(layers)
add("D37: tail at top-left of bubble", case_d37())

def case_d38():
    """Tail at bottom-right (alternative position)."""
    layers = perfect_bubble()
    layers[1]["x"] = 800; layers[1]["y"] = 470
    return H(layers)
add("D38: tail at bottom-right", case_d38())

def case_d39():
    """Tail far below bubble."""
    layers = perfect_bubble()
    layers[1]["y"] = 700
    return H(layers)
add("D39: tail far below bubble", case_d39())

def case_d40():
    return H(perfect_bubble())
add("D40: control", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────
def case_e41():
    """Bubble cornerRadius=0 (sharp corners — not 'rounded')."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 0
    return H(layers)
add("E41: bubble cornerRadius=0", case_e41())

def case_e42():
    """Bubble cornerRadius=2 (barely rounded)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 2
    return H(layers)
add("E42: bubble cornerRadius=2 (barely)", case_e42())

def case_e43():
    """Polygon sides=4 (not triangle)."""
    layers = perfect_bubble()
    layers[1]["sides"] = 4
    return H(layers)
add("E43: tail sides=4 (square)", case_e43())

def case_e44():
    """Polygon sides=6 (hexagon)."""
    layers = perfect_bubble()
    layers[1]["sides"] = 6
    return H(layers)
add("E44: tail sides=6 (hexagon)", case_e44())

def case_e45():
    """Bubble rotated 45°."""
    layers = perfect_bubble()
    layers[0]["rotation"] = 45
    return H(layers)
add("E45: bubble rotated 45°", case_e45())

def case_e46():
    """Bubble flipped X."""
    layers = perfect_bubble()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E46: bubble flipped X", case_e46())

def case_e47():
    """Tail rotated 90°."""
    layers = perfect_bubble()
    layers[1]["rotation"] = 90
    return H(layers)
add("E47: tail rotated 90°", case_e47())

def case_e48():
    """Tail flipped Y."""
    layers = perfect_bubble()
    layers[1]["scaleY"] = -1
    return H(layers)
add("E48: tail flipped Y", case_e48())

def case_e49():
    """Bubble cornerRadius=10 (less than min=8 implied)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 4
    return H(layers)
add("E49: bubble cornerRadius=4", case_e49())

def case_e50():
    """Bubble cornerRadius=200 (extreme)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 200
    return H(layers)
add("E50: bubble cornerRadius=200 (very rounded)", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────
def case_f51():
    """Both no strokes."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"] = []
    return H(layers)
add("F51: no strokes", case_f51())

def case_f52():
    """Strokes 8px (over expected 2)."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=8)]
    return H(layers)
add("F52: strokes 8px", case_f52())

def case_f53():
    """Strokes 0.5px."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=0.5)]
    return H(layers)
add("F53: strokes 0.5px", case_f53())

def case_f54():
    """Strokes wrong color (red)."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=RED, weight=2)]
    return H(layers)
add("F54: red strokes", case_f54())

def case_f55():
    """Stroke alignment outside."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("F55: alignment=outside", case_f55())

def case_f56():
    """Dashed strokes."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"][0]["dash"] = {"dash": 4, "gap": 4}
    return H(layers)
add("F56: dashed strokes", case_f56())

def case_f57():
    """Bubble at 45°, tail too."""
    layers = perfect_bubble()
    layers[0]["rotation"] = 45
    layers[1]["rotation"] = 45
    return H(layers)
add("F57: both rotated 45°", case_f57())

def case_f58():
    """Tail far above bubble."""
    layers = perfect_bubble()
    layers[1]["y"] = 50
    return H(layers)
add("F58: tail far above bubble", case_f58())

def case_f59():
    """Bubble corner radius matches half bubble height (extreme)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 120  # half of 240 = full pill
    return H(layers)
add("F59: bubble cornerRadius=120 (full pill)", case_f59())

def case_f60():
    """Tail color #fff (white not gray)."""
    layers = perfect_bubble()
    layers[1]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    return H(layers)
add("F60: tail white (not light_gray)", case_f60())


# ─── G. Frame variants ─────────────────────────────────────
def case_g61():
    layers = perfect_bubble()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_bubble()
    inner = make_frame(layers, w=900, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_bubble(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, bubble in 2nd", case_g63())

def case_g64():
    layers = perfect_bubble()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_bubble()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_bubble()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_bubble()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G67: frame 2000×2000", case_g67())

def case_g68():
    layers = perfect_bubble()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G68: frame 200×200 (too small)", case_g68())

def case_g69():
    return H(perfect_bubble(), in_frame=False)
add("G69: bubble on page (no frame)", case_g69())

def case_g70():
    return H(perfect_bubble(), frame_w=1279, frame_h=831)
add("G70: frame 1279×831 (within tol)", case_g70())


# ─── H. Tools / events ─────────────────────────────────────
def case_h71():
    extras = [make_event("move_layer") for _ in range(50)]
    return H(evts=evt(extras=extras))
add("H71: 50 move events", case_h71())

def case_h72():
    extras = [make_event("undo") for _ in range(50)]
    return H(evts=evt(extras=extras))
add("H72: 50 undo events", case_h72())

def case_h73():
    extras = [make_event("align_layers", axis="center_y")]
    return H(evts=evt(extras=extras))
add("H73: align used", case_h73())

def case_h74():
    """Used ellipse tool instead of polygon."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H74: ellipse tool used (not polygon)", case_h74())

def case_h75():
    """0 tool_change events."""
    sem = [make_event("session_start"),
           make_event("create_rectangle"),
           make_event("create_polygon")]
    return H(evts=sem)
add("H75: 0 tool_change events", case_h75())

def case_h76():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: many session_end", case_h76())

def case_h77():
    extras = [make_event("create_polygon"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H77: created+deleted polygon", case_h77())

def case_h78():
    """Excessive create events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 5)
    sem.append(make_event("tool_change", before="rectangle", after="polygon"))
    sem.extend([make_event("create_polygon")] * 5)
    return H(evts=sem)
add("H78: 5 create_rect + 5 create_poly", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("create_rectangle"),
           make_event("tool_change", before="rectangle", after="polygon"),
           make_event("create_polygon"),
           make_event("create_polygon")]
    return H(evts=sem)
add("H79: 2 create_rect + 2 create_poly", case_h79())

def case_h80():
    extras = [make_event("create_ellipse"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H80: created+deleted ellipse", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────
def case_i81():
    layers = perfect_bubble()
    group = {"id":"group_1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group in frame", case_i81())

def case_i82():
    layers = perfect_bubble()
    f1 = make_frame([layers[0]], w=600, h=832)
    f2 = make_frame([layers[1]], w=600, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_bubble()
    section = {"id":"sec_1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    layers = perfect_bubble()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested", case_i84())

def case_i85():
    layers = perfect_bubble()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: bubble on page 2", case_i85())

def case_i86():
    layers = perfect_bubble()
    f1 = make_frame([layers[0]], w=1280, h=832)
    return make_log([f1, layers[1]], evt())
add("I86: rect in frame, polygon outside", case_i86())

def case_i87():
    """Bubble in component."""
    layers = perfect_bubble()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I87: in component", case_i87())


# ─── J. Bizarre ────────────────────────────────────────────
def case_j88():
    """Bubble is ellipse instead of rect."""
    layers = perfect_bubble()
    layers[0] = make_layer("ellipse", x=400, y=250, w=480, h=240, fill=LIGHT_GRAY,
                            strokes=[make_stroke(rgb=DARK_GRAY, weight=2)])
    return H(layers, evts=evt(rect=0, polygon=1, extras=[make_event("create_ellipse")]))
add("J88: bubble = ellipse, not rect", case_j88())

def case_j89():
    """Tail is ellipse instead of polygon."""
    layers = perfect_bubble()
    layers[1] = make_layer("ellipse", x=420, y=470, w=80, h=80, fill=LIGHT_GRAY,
                            strokes=[make_stroke(rgb=DARK_GRAY, weight=2)])
    return H(layers, evts=evt(rect=1, polygon=0, extras=[make_event("create_ellipse")]))
add("J89: tail = ellipse, not polygon", case_j89())

def case_j90():
    return make_log([], [make_event("session_start")])
add("J90: empty document", case_j90())

def case_j91():
    return H([])
add("J91: frame only", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=LIGHT_GRAY)
    text["content"] = "speech bubble"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text 'speech bubble'", case_j92())

def case_j93():
    """Both 1×1 degenerate."""
    layers = perfect_bubble()
    for l in layers:
        l["w"] = 1; l["h"] = 1
    return H(layers)
add("J93: both 1×1", case_j93())

def case_j94():
    """Both flipped."""
    layers = perfect_bubble()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J94: both flipped X", case_j94())

def case_j95():
    """Negative coordinates."""
    layers = perfect_bubble()
    for l in layers:
        l["x"] -= 1500
    return H(layers)
add("J95: at negative x", case_j95())

def case_j96():
    return H(perfect_bubble())
add("J96: control perfect", case_j96())

def case_j97():
    """Bubble HUGE = full frame."""
    layers = perfect_bubble()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    return H(layers)
add("J97: bubble = full frame", case_j97())

def case_j98():
    """Both light gray but no overlap."""
    layers = perfect_bubble()
    layers[1]["x"] = 1100; layers[1]["y"] = 50
    return H(layers)
add("J98: tail far away (no overlap)", case_j98())

def case_j99():
    """Bubble cornerRadius=480 (half size)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 480
    return H(layers)
add("J99: bubble cornerRadius=480 (extreme)", case_j99())

def case_j100():
    return H(perfect_bubble())
add("J100: control perfect", case_j100())


# Run all
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

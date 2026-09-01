"""100 edge cases for task 39 (wifi icon) — runs all and prints score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_39" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
NAVY_COLOR = (0.05, 0.10, 0.45)


def evt(vector=2, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("tool_change", before="pen", after="ellipse")]
    for _ in range(vector):  sem.append(make_event("create_vector"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_wifi():
    arc1 = L("vector", 300, 200, 200, 100, None,
             strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    arc2 = L("vector", 250, 170, 300, 130, None,
             strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    dot = L("ellipse", 390, 380, 20, 20, NAVY_COLOR)
    return [arc1, arc2, dot]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_wifi()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ──────────────────────────────────────────────────
def a1():
    layers = perfect_wifi()
    layers = layers[1:]  # drop arc1
    return H(layers, evts=evt(vector=1))
add("A1: 1 vector (off-by-one)", a1())

def a2():
    layers = [L("ellipse", 390, 380, 20, 20, NAVY_COLOR)]
    return H(layers, evts=evt(vector=0))
add("A2: 0 vectors (no arcs)", a2())

def a3():
    layers = perfect_wifi()[:2]
    return H(layers, evts=evt(ellipse=0))
add("A3: 0 ellipses (no dot)", a3())

def a4():
    layers = perfect_wifi()
    layers.append(L("ellipse", 350, 350, 30, 30, RED))
    return H(layers, evts=evt(ellipse=2))
add("A4: 2 ellipses (extra dot)", a4())

def a5():
    layers = perfect_wifi()
    for i in range(3):
        layers.insert(0, L("vector", 280-30*i, 150-20*i, 250+50*i, 100+30*i, None,
                           strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]))
    return H(layers, evts=evt(vector=5))
add("A5: 5 vectors (extras)", a5())

def a6():
    return H([], evts=evt(vector=0, ellipse=0))
add("A6: empty document", a6())

def a7():
    layers = [L("ellipse", 390, 380, 20, 20, NAVY_COLOR)]
    layers.append(L("ellipse", 360, 350, 30, 30, NAVY_COLOR))
    layers.append(L("ellipse", 330, 320, 40, 40, NAVY_COLOR))
    return H(layers, evts=evt(vector=0, ellipse=3))
add("A7: 3 ellipses (no vectors at all)", a7())

def a8():
    layers = perfect_wifi()
    layers.append(L("rectangle", 100, 100, 50, 50, GREEN))
    return H(layers)
add("A8: 1 extra rectangle", a8())

def a9():
    layers = perfect_wifi()[:1]
    layers.append(L("ellipse", 390, 380, 20, 20, NAVY_COLOR))
    return H(layers, evts=evt(vector=1))
add("A9: 1 vector + 1 dot only", a9())

def a10():
    return H()  # control
add("A10: perfect (control)", a10())


# ─── B. Colors (10) ──────────────────────────────────────────────────
def b11():
    layers = perfect_wifi()
    layers[2]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B11: dot has image fill", b11())

def b12():
    layers = perfect_wifi()
    layers[2]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":0.05,"g":0.10,"b":0.45,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":0,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B12: dot has gradient", b12())

def b13():
    layers = perfect_wifi()
    layers[2]["fills"] = []
    return H(layers)
add("B13: dot has no fill", b13())

def b14():
    layers = perfect_wifi()
    layers[2]["fills"][0]["color"] = {"r":1.0, "g":0, "b":0, "a":1}  # red dot
    return H(layers)
add("B14: dot is red (not navy)", b14())

def b15():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["paint"]["color"] = {"r":1, "g":0, "b":0, "a":1}
    return H(layers)
add("B15: arcs stroke is red", b15())

def b16():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["weight"] = 1
    return H(layers)
add("B16: arcs stroke 1px (thin)", b16())

def b17():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["weight"] = 12
    return H(layers)
add("B17: arcs stroke 12px (thick)", b17())

def b18():
    layers = perfect_wifi()
    layers[2]["fills"][0]["color"]["a"] = 0  # alpha 0
    return H(layers)
add("B18: dot alpha=0", b18())

def b19():
    layers = perfect_wifi()
    layers[2]["fills"][0]["opacity"] = 0.1  # transparent
    return H(layers)
add("B19: dot opacity 0.1", b19())

def b20():
    layers = perfect_wifi()
    layers[2]["opacity"] = 0
    return H(layers)
add("B20: dot layer opacity 0", b20())


# ─── C. Sizing (10) ──────────────────────────────────────────────────
def c21():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 380, 1, 1, NAVY_COLOR)
    return H(layers)
add("C21: dot 1x1 (degenerate)", c21())

def c22():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 100, 380, 800, 100, NAVY_COLOR)
    return H(layers)
add("C22: dot huge oval (800x100)", c22())

def c23():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["w"] = 1; arc["h"] = 1
    return H(layers)
add("C23: arcs 1x1 (degenerate)", c23())

def c24():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["w"] = 1500; arc["h"] = 800
    return H(layers)
add("C24: arcs 1500x800 (huge)", c24())

def c25():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 380, 200, 200, NAVY_COLOR)  # huge dot
    return H(layers)
add("C25: dot 200x200", c25())

def c26():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 380, 5, 5, NAVY_COLOR)
    return H(layers)
add("C26: dot 5x5 (tiny)", c26())

def c27():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 380, 100, 30, NAVY_COLOR)  # squashed oval
    return H(layers)
add("C27: dot squashed (100x30 oval)", c27())

def c28():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["w"] = 50; arc["h"] = 25
    return H(layers)
add("C28: arcs 50x25 (small)", c28())

def c29():
    return H()  # default control
add("C29: default (control)", c29())

def c30():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 380, 30, 20, NAVY_COLOR)  # slightly oval
    return H(layers)
add("C30: dot 30x20 (slight oval)", c30())


# ─── D. Position (10) ────────────────────────────────────────────────
def d31():
    layers = perfect_wifi()
    for l in layers: l["x"] -= 500
    return H(layers)
add("D31: shifted off-left", d31())

def d32():
    layers = perfect_wifi()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D32: shifted off-right", d32())

def d33():
    layers = perfect_wifi()
    for l in layers: l["y"] -= 400
    return H(layers)
add("D33: negative y", d33())

def d34():
    # dot ABOVE arcs (wrong)
    layers = perfect_wifi()
    layers[2] = L("ellipse", 390, 100, 20, 20, NAVY_COLOR)
    return H(layers)
add("D34: dot above arcs", d34())

def d35():
    layers = perfect_wifi()
    layers[2] = L("ellipse", 100, 380, 20, 20, NAVY_COLOR)  # far left
    return H(layers)
add("D35: dot far from arc center", d35())

def d36():
    # arc1 above arc2 (reversed concentric)
    layers = perfect_wifi()
    layers[0]["y"] = 100
    layers[1]["y"] = 250
    return H(layers)
add("D36: arc1 above arc2 (reversed)", d36())

def d37():
    layers = perfect_wifi()
    layers[0] = L("vector", 100, 100, 200, 100, None,
                  strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    return H(layers)
add("D37: arc1 in corner", d37())

def d38():
    return H()  # control
add("D38: perfect (control)", d38())

def d39():
    layers = perfect_wifi()
    # arcs and dot stacked
    layers[2] = L("ellipse", 305, 220, 20, 20, NAVY_COLOR)
    return H(layers)
add("D39: dot inside arc area", d39())

def d40():
    layers = perfect_wifi()
    for l in layers:
        l["x"] = 0; l["y"] = 0
    return H(layers)
add("D40: all at origin", d40())


# ─── E. Rotation / shape variants (10) ───────────────────────────────
def e41():
    layers = perfect_wifi()
    layers[2]["rotation"] = 45
    return H(layers)
add("E41: dot rotated 45° (oval-shape)", e41())

def e42():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["rotation"] = 45
    return H(layers)
add("E42: arcs rotated 45°", e42())

def e43():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["rotation"] = 180
    return H(layers)
add("E43: arcs rotated 180°", e43())

def e44():
    layers = perfect_wifi()
    layers[2]["scaleX"] = -1
    return H(layers)
add("E44: dot flipped scaleX=-1", e44())

def e45():
    # dot is a square (rectangle)
    layers = perfect_wifi()[:2]
    layers.append(L("rectangle", 390, 380, 20, 20, NAVY_COLOR))
    return H(layers, evts=evt(ellipse=0))
add("E45: dot is rectangle", e45())

def e46():
    # dot is a star
    layers = perfect_wifi()[:2]
    layers.append(make_layer("star", x=390, y=380, w=20, h=20, fill=NAVY_COLOR,
                              points=5, innerRatio=0.4))
    return H(layers, evts=evt(ellipse=0))
add("E46: dot is star", e46())

def e47():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["scaleY"] = -1
    return H(layers)
add("E47: arcs flipped vertically", e47())

def e48():
    # arcs are polygons not vectors
    layers = perfect_wifi()
    layers[0] = make_layer("polygon", x=300, y=200, w=200, h=100, fill=NAVY_COLOR, sides=3)
    layers[1] = make_layer("polygon", x=250, y=170, w=300, h=130, fill=NAVY_COLOR, sides=3)
    return H(layers, evts=evt(vector=0))
add("E48: arcs are polygons", e48())

def e49():
    # arcs are ellipses (filled circles)
    layers = perfect_wifi()
    layers[0] = L("ellipse", 300, 200, 200, 100, NAVY_COLOR)
    layers[1] = L("ellipse", 250, 170, 300, 130, NAVY_COLOR)
    return H(layers, evts=evt(vector=0, ellipse=3))
add("E49: arcs are ellipses (filled)", e49())

def e50():
    return H()  # control
add("E50: perfect (control)", e50())


# ─── F. Subcomponent variants (10) ───────────────────────────────────
def f51():
    layers = perfect_wifi()
    # arcs same size = not concentric
    layers[1] = L("vector", 300, 200, 200, 100, None,
                  strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)])
    return H(layers)
add("F51: arcs same size (not concentric)", f51())

def f52():
    # arcs filled instead of stroked
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["fills"] = [{"kind":"solid","color":{"r":0.05,"g":0.10,"b":0.45,"a":1},"opacity":1,"visible":True}]
        arc["strokes"] = []
    return H(layers)
add("F52: arcs filled (no stroke)", f52())

def f53():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"] = []  # no stroke at all
    return H(layers)
add("F53: arcs no stroke", f53())

def f54():
    # Dot has stroke instead of fill
    layers = perfect_wifi()
    layers[2]["fills"] = []
    layers[2]["strokes"] = [make_stroke(rgb=NAVY_COLOR, weight=2)]
    return H(layers)
add("F54: dot stroke-only", f54())

def f55():
    # arcs partially transparent stroke
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("F55: arcs stroke alpha=0", f55())

def f56():
    # arcs visible=False
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["visible"] = False
    return H(layers)
add("F56: arcs visible=False", f56())

def f57():
    # arcs at frame edge
    layers = perfect_wifi()
    layers[0]["x"] = -100
    return H(layers)
add("F57: arc1 partially off-frame", f57())

def f58():
    # arcs and dot in line (no concentric)
    layers = perfect_wifi()
    layers[0]["y"] = 200
    layers[1]["y"] = 200
    return H(layers)
add("F58: arcs at same y (not concentric)", f58())

def f59():
    # arcs widely separated
    layers = perfect_wifi()
    layers[0]["x"] = 100
    layers[1]["x"] = 700
    return H(layers)
add("F59: arcs widely separated x", f59())

def f60():
    return H()  # control
add("F60: perfect (control)", f60())


# ─── G. Frame variants (10) ──────────────────────────────────────────
def g61():
    layers = perfect_wifi()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", g61())

def g62():
    layers = perfect_wifi()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", g62())

def g63():
    layers = perfect_wifi()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G63: frame image fill", g63())

def g64():
    layers = perfect_wifi()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("G64: frame with stroke", g64())

def g65():
    return H(frame_w=2000, frame_h=1500)
add("G65: frame oversized", g65())

def g66():
    return H(frame_w=200, frame_h=200)
add("G66: frame undersized 200x200", g66())

def g67():
    layers = perfect_wifi()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    return H()  # control
add("G68: default frame (control)", g68())

def g69():
    layers = perfect_wifi()
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(layers, w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames, wifi in 2nd", g69())

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
           make_event("create_vector"), make_event("create_vector"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H73: 0 tool_change events", h73())

def h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_vector"), make_event("create_vector"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H74: tool change to rectangle (no pen/ellipse)", h74())

def h75():
    return H(evts=evt(vector=10))
add("H75: 10 create_vector events", h75())

def h76():
    return H(evts=evt(extras=[make_event("create_star"), make_event("delete")]))
add("H76: create+delete a star", h76())

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
add("H80: default events (control)", h80())


# ─── I. Hierarchy (10) ───────────────────────────────────────────────
def i81():
    layers = perfect_wifi()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: shapes in group inside frame", i81())

def i82():
    layers = perfect_wifi()
    f1 = make_frame(layers[:2], w=640, h=832)
    f2 = make_frame(layers[2:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: shapes split across 2 frames", i82())

def i83():
    layers = perfect_wifi()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: shapes in section (not frame)", i83())

def i84():
    layers = perfect_wifi()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I84: shapes in component (not frame)", i84())

def i85():
    layers = perfect_wifi()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", i85())

def i86():
    layers = perfect_wifi()
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    frame = make_frame(layers, w=1280, h=832)
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: wifi on page 2", i86())

def i87():
    layers = perfect_wifi()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, *layers[2:]], evt())
add("I87: arcs in frame, dot on page", i87())

def i88():
    layers = perfect_wifi()
    return make_log(layers, evt())
add("I88: shapes top-level", i88())

def i89():
    layers = perfect_wifi()
    inner_frame = make_frame(layers, w=400, h=400)
    big_frame = make_frame([inner_frame], w=1280, h=832)
    return make_log([big_frame], evt())
add("I89: small inner frame in big frame", i89())

def i90():
    return H()  # control
add("I90: perfect (control)", i90())


# ─── J. Bizarre (10) ─────────────────────────────────────────────────
def j91():
    layers = perfect_wifi()
    layers[2]["rotation"] = 180
    return H(layers)
add("J91: dot rotated 180° (no visual change)", j91())

def j92():
    # all 3 shapes piled at one point
    layers = [L("vector", 500, 400, 100, 100, None,
                strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]),
              L("vector", 500, 400, 100, 100, None,
                strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]),
              L("ellipse", 500, 400, 100, 100, NAVY_COLOR)]
    return H(layers)
add("J92: all 3 piled at one point", j92())

def j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", j93())

def j94():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY_COLOR)
    text["content"] = "wifi"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J94: text 'wifi'", j94())

def j95():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["scaleX"] = -1
    return H(layers)
add("J95: arcs flipped scaleX=-1", j95())

def j96():
    layers = perfect_wifi()
    for arc in layers[:2]:
        arc["w"] = 1; arc["h"] = 1
    return H(layers)
add("J96: arcs 1x1 (degenerate)", j96())

def j97():
    layers = perfect_wifi()
    # add a 3rd pen-vector but as decoration
    layers.append(L("vector", 100, 700, 50, 50, None,
                    strokes=[make_stroke(rgb=NAVY_COLOR, weight=6)]))
    return H(layers, evts=evt(vector=3))
add("J97: 3rd vector (decoration)", j97())

def j98():
    # arcs at exactly same position (overlapping)
    layers = perfect_wifi()
    layers[1]["x"] = layers[0]["x"]
    layers[1]["y"] = layers[0]["y"]
    layers[1]["w"] = layers[0]["w"]
    layers[1]["h"] = layers[0]["h"]
    return H(layers)
add("J98: arcs at exact same position", j98())

def j99():
    # dot above arcs in z-order
    layers = perfect_wifi()
    dot = layers.pop(2)
    layers.insert(0, dot)  # dot drawn first = back
    return H(layers)
add("J99: dot behind arcs (z-order)", j99())

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

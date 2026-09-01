"""100 edge cases for task 15 (4 overlapping white ellipses forming cloud)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_15" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(ellipse=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):
        sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    layer = make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)
    return layer


def perfect_cloud():
    """4 overlapping white ellipses — varying sizes, sharing y baseline,
    overlapping like a cloud silhouette."""
    layers = []
    sizes = [(180, 180), (220, 220), (200, 200), (160, 160)]  # varying sizes
    xs = [400, 540, 680, 820]  # overlapping
    y = 300
    for i, ((w, h), x) in enumerate(zip(sizes, xs)):
        l = L("ellipse", x, y, w, h, WHITE)
        l["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=1)]
        layers.append(l)
    return layers


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_cloud()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────
def case_a1():
    layers = perfect_cloud()
    layers.append(L("ellipse", 950, 300, 150, 150, WHITE,
                     strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)]))
    return H(layers, evts=evt(ellipse=5))
add("A1: 5 ellipses (extra)", case_a1())

def case_a2():  return H(perfect_cloud()[:3], evts=evt(ellipse=3))
add("A2: 3 ellipses (missing)", case_a2())

def case_a3():  return H(perfect_cloud()[:2], evts=evt(ellipse=2))
add("A3: 2 ellipses", case_a3())

def case_a4():  return H(perfect_cloud()[:1], evts=evt(ellipse=1))
add("A4: 1 ellipse", case_a4())

def case_a5():  return H([], evts=evt(ellipse=0))
add("A5: 0 ellipses", case_a5())

def case_a6():  return H(perfect_cloud()*2, evts=evt(ellipse=8))
add("A6: 8 ellipses (doubled)", case_a6())

def case_a7():
    layers = perfect_cloud()
    layers.append(L("rectangle", 400, 480, 400, 50, WHITE))  # base rect
    return H(layers, evts=evt(ellipse=4, extras=[make_event("create_rectangle")]))
add("A7: 4 ellipses + extra rect", case_a7())

def case_a8():
    """6 ellipses (busier cloud)."""
    layers = perfect_cloud()
    for i in range(2):
        layers.append(L("ellipse", 380+i*80, 280, 100, 100, WHITE,
                         strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)]))
    return H(layers, evts=evt(ellipse=6))
add("A8: 6 ellipses (more puffs)", case_a8())

def case_a9():  return H(perfect_cloud(), evts=evt(ellipse=4))
add("A9: 4 ellipses (control)", case_a9())

def case_a10():
    return H(perfect_cloud() + [
        make_layer("polygon", x=600, y=400, w=80, h=80, fill=WHITE, sides=3)
    ], evts=evt(ellipse=4, extras=[make_event("create_polygon")]))
add("A10: 4 ellipses + polygon", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────
def case_b11():
    """All gray instead of white."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1}
    return H(layers)
add("B11: all gray", case_b11())

def case_b12():
    """All blue."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.2,"g":0.4,"b":0.85,"a":1}
    return H(layers)
add("B12: all blue", case_b12())

def case_b13():
    """All image fills."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: image fills", case_b13())

def case_b14():
    """Gradient fills."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":1,"b":1,"a":1}},
            {"position":1,"color":{"r":0.8,"g":0.8,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B14: gradient fills", case_b14())

def case_b15():
    """No fills."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B15: no fills", case_b15())

def case_b16():
    """Each different color."""
    layers = perfect_cloud()
    for l, c in zip(layers, [PINK, ORANGE, GREEN, BLUE]):
        l["fills"][0]["color"] = {"r":c[0],"g":c[1],"b":c[2],"a":1}
    return H(layers)
add("B16: 4 different colors", case_b16())

def case_b17():
    """Almost-white but slightly off (within tol)."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1}
    return H(layers)
add("B17: near-white (within tol)", case_b17())

def case_b18():
    """White-ish but more like beige."""
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.85,"g":0.80,"b":0.70,"a":1}
    return H(layers)
add("B18: cream/beige fills", case_b18())

def case_b19():
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: alpha=0 invisible", case_b19())

def case_b20():
    layers = perfect_cloud()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B20: opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────
def case_c21():
    """All ellipses tiny (5×5)."""
    layers = []
    for i, x in enumerate([400, 540, 680, 820]):
        l = L("ellipse", x, 300, 5, 5, WHITE, strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers)
add("C21: tiny 5×5 ellipses", case_c21())

def case_c22():
    """All ellipses huge (1000×1000)."""
    layers = []
    for i, x in enumerate([0, 100, 200, 300]):
        l = L("ellipse", x, 0, 1000, 1000, WHITE, strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers)
add("C22: huge ellipses (overflow)", case_c22())

def case_c23():
    """All same size (no variation)."""
    layers = perfect_cloud()
    for l in layers:
        l["w"] = 200; l["h"] = 200
    return H(layers)
add("C23: all 200×200 (uniform)", case_c23())

def case_c24():
    """Long thin ellipses."""
    layers = []
    for i, x in enumerate([400, 540, 680, 820]):
        l = L("ellipse", x, 350, 200, 30, WHITE, strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers)
add("C24: 200×30 thin ellipses", case_c24())

def case_c25():
    """1 ellipse 0×0 (degenerate)."""
    layers = perfect_cloud()
    layers[0]["w"] = 0; layers[0]["h"] = 0
    return H(layers)
add("C25: 1 ellipse 0×0", case_c25())

def case_c26():
    """1 ellipse super huge (frame size)."""
    layers = perfect_cloud()
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("C26: 1 ellipse = full frame", case_c26())

def case_c27():
    """Sizes 300/250/200/150 (varied, decreasing)."""
    layers = perfect_cloud()
    for i, (size, l) in enumerate(zip([300, 250, 200, 150], layers)):
        l["w"] = size; l["h"] = size
    return H(layers)
add("C27: sizes 300/250/200/150 (decreasing)", case_c27())

def case_c28():
    """All circular (w=h)."""
    layers = perfect_cloud()
    for l in layers:
        l["h"] = l["w"]
    return H(layers)
add("C28: all circular", case_c28())

def case_c29():
    """All wide ovals (w=2h)."""
    layers = perfect_cloud()
    for l in layers:
        l["w"] = 200; l["h"] = 100
    return H(layers)
add("C29: all wide ovals", case_c29())

def case_c30():
    """All vertical ovals (h=2w)."""
    layers = perfect_cloud()
    for l in layers:
        l["w"] = 100; l["h"] = 200
    return H(layers)
add("C30: all tall ovals", case_c30())


# ─── D. Position ────────────────────────────────────────────
def case_d31():
    """Ellipses far apart (no overlap)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*250
    return H(layers)
add("D31: ellipses far apart (no overlap)", case_d31())

def case_d32():
    """Ellipses scattered all around frame (random)."""
    layers = perfect_cloud()
    positions = [(100, 100), (1000, 100), (100, 700), (1000, 700)]
    for l, (x, y) in zip(layers, positions):
        l["x"] = x; l["y"] = y
    return H(layers)
add("D32: ellipses at 4 corners", case_d32())

def case_d33():
    """Ellipses in vertical column (overlapping)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 600
        l["y"] = 100 + i*120
    return H(layers)
add("D33: ellipses in vertical column", case_d33())

def case_d34():
    """All at exact same position (pile)."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] = 600; l["y"] = 400
    return H(layers)
add("D34: all at same point", case_d34())

def case_d35():
    """Overlap but ellipses much higher than others (no shared baseline)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["y"] = 100 + i*100  # different y for each
    return H(layers)
add("D35: y staircase", case_d35())

def case_d36():
    """Ellipses off-frame top-left."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] -= 600; l["y"] -= 400
    return H(layers)
add("D36: ellipses off-frame", case_d36())

def case_d37():
    """At negative y."""
    layers = perfect_cloud()
    for l in layers:
        l["y"] -= 1000
    return H(layers)
add("D37: at negative y", case_d37())

def case_d38():
    """All at center pile (overlapping)."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] = 600; l["y"] = 400
    return H(layers)
add("D38: all centered pile", case_d38())

def case_d39():
    """Ellipses share y baseline (correct) but spread far horizontally."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*350
    return H(layers)
add("D39: spread horizontally, no overlap", case_d39())

def case_d40():
    return H(perfect_cloud())
add("D40: cloud (control)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────
def case_e41():
    """All rotated 45°."""
    layers = perfect_cloud()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E41: all rotated 45°", case_e41())

def case_e42():
    """Each rotated differently."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["rotation"] = i * 30
    return H(layers)
add("E42: varying rotations", case_e42())

def case_e43():
    """All flipped X."""
    layers = perfect_cloud()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E43: all flipped X", case_e43())

def case_e44():
    """1 flipped Y."""
    layers = perfect_cloud()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E44: 1 flipped Y", case_e44())

def case_e45():
    """All cornerRadius=200 (no-op for ellipse)."""
    layers = perfect_cloud()
    for l in layers:
        l["cornerRadius"] = 200
    return H(layers)
add("E45: cornerRadius=200 (no-op for ellipse)", case_e45())

def case_e46():
    """All under-tol rotated 4°."""
    layers = perfect_cloud()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E46: all rotated 4°", case_e46())

def case_e47():
    """All have stroke 5px (over expected 1)."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=5)]
    return H(layers)
add("E47: all strokes 5px", case_e47())

def case_e48():
    """No strokes at all."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"] = []
    return H(layers)
add("E48: no strokes", case_e48())

def case_e49():
    """Stroke is dark instead of light gray."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=(0.1,0.1,0.1), weight=1)]
    return H(layers)
add("E49: dark gray strokes", case_e49())

def case_e50():
    """Dashed strokes."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"][0]["dash"] = {"dash": 4, "gap": 4}
    return H(layers)
add("E50: dashed strokes", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────
def case_f51():
    """Ellipses arranged in horizontal line, but no overlap."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*500
    return H(layers)
add("F51: spread far, no overlap", case_f51())

def case_f52():
    """Non-overlapping but close (touching)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*200  # exactly touching
        l["w"] = 200; l["h"] = 200
    return H(layers)
add("F52: touching not overlapping", case_f52())

def case_f53():
    """Heavy overlap (almost concentric)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 600 + i*5  # very close
    return H(layers)
add("F53: heavy overlap", case_f53())

def case_f54():
    """One ellipse far above (cloud + stray)."""
    layers = perfect_cloud()
    layers[3]["y"] = 50  # one floating up
    return H(layers)
add("F54: 1 ellipse floating up", case_f54())

def case_f55():
    """All ellipses at top of frame."""
    layers = perfect_cloud()
    for l in layers:
        l["y"] = 50
    return H(layers)
add("F55: all at top of frame", case_f55())

def case_f56():
    """All at bottom of frame."""
    layers = perfect_cloud()
    for l in layers:
        l["y"] = 700
    return H(layers)
add("F56: all at bottom", case_f56())

def case_f57():
    """All same size but offset diagonally."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 400+i*50; l["y"] = 200+i*50
    return H(layers)
add("F57: diagonal arrangement", case_f57())

def case_f58():
    """Tight cloud (small)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 500 + i*30; l["y"] = 300
        l["w"] = 80; l["h"] = 80
    return H(layers)
add("F58: tight small cloud", case_f58())

def case_f59():
    """Wide cloud (long)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        l["x"] = 100 + i*200
        l["w"] = 300; l["h"] = 200
    return H(layers)
add("F59: wide long cloud", case_f59())

def case_f60():
    """Cloud with strokes 1.5px (within tol)."""
    layers = perfect_cloud()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=1.5)]
    return H(layers)
add("F60: strokes 1.5px (within tol)", case_f60())


# ─── G. Frame variants ─────────────────────────────────────
def case_g61():
    layers = perfect_cloud()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_cloud()
    inner = make_frame(layers, w=900, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_cloud(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, cloud in 2nd", case_g63())

def case_g64():
    layers = perfect_cloud()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_cloud()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_cloud()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_cloud()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G67: frame 2000x2000", case_g67())

def case_g68():
    layers = perfect_cloud()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G68: frame 200x200 (too small)", case_g68())

def case_g69():
    return H(perfect_cloud(), in_frame=False)
add("G69: cloud on page (no frame)", case_g69())

def case_g70():
    return H(perfect_cloud(), frame_w=1279, frame_h=831)
add("G70: frame 1279x831 (within tol)", case_g70())


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
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 4)
    return H(evts=sem)
add("H74: rectangle tool used", case_h74())

def case_h75():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_ellipse")] * 4)
    return H(evts=sem)
add("H75: 0 tool_change events", case_h75())

def case_h76():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: many session_end events", case_h76())

def case_h77():
    extras = [make_event("create_ellipse"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H77: created+deleted ellipse", case_h77())

def case_h78():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 8)
    return H(evts=sem)
add("H78: 8 create_ellipse events", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 2)
    return H(evts=sem)
add("H79: 2 create_ellipse events", case_h79())

def case_h80():
    extras = [make_event("create_polygon"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H80: created+deleted polygon", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────
def case_i81():
    layers = perfect_cloud()
    group = {"id":"group_1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group in frame", case_i81())

def case_i82():
    layers = perfect_cloud()
    f1 = make_frame(layers[:2], w=600, h=832)
    f2 = make_frame(layers[2:], w=600, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_cloud()
    section = {"id":"sec_1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    layers = perfect_cloud()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested", case_i84())

def case_i85():
    layers = perfect_cloud()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: cloud on page 2", case_i85())

def case_i86():
    layers = perfect_cloud()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I86: each in own frame", case_i86())

def case_i87():
    layers = perfect_cloud()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only 1 in frame", case_i87())


# ─── J. Bizarre ────────────────────────────────────────────
def case_j88():
    """1 ellipse → rectangle (still white)."""
    layers = perfect_cloud()
    layers[0] = make_layer("rectangle", x=400, y=300, w=200, h=200, fill=WHITE,
                            strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
    return H(layers, evts=evt(ellipse=3, extras=[make_event("create_rectangle")]))
add("J88: 1 ellipse→rect (3 ellipses)", case_j88())

def case_j89():
    """All 4 are stars (still overlapping, still white)."""
    layers = []
    for i, x in enumerate([400, 540, 680, 820]):
        l = make_layer("star", x=x, y=300, w=200, h=200, fill=WHITE,
                       points=8, innerRatio=0.7,
                       strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_star")]*4))
add("J89: 4 stars instead of ellipses", case_j89())

def case_j90():
    return make_log([], [make_event("session_start")])
add("J90: empty document", case_j90())

def case_j91():
    return H([])
add("J91: frame only", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=WHITE)
    text["content"] = "cloud"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text 'cloud'", case_j92())

def case_j93():
    """All 1×1."""
    layers = []
    for x in [400, 540, 680, 820]:
        l = L("ellipse", x, 300, 1, 1, WHITE, strokes=[make_stroke(rgb=LIGHT_GRAY, weight=1)])
        layers.append(l)
    return H(layers)
add("J93: all 1×1 degenerate", case_j93())

def case_j94():
    """Cloud with 4 different white shades."""
    layers = perfect_cloud()
    layers[0]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}  # pure white
    layers[1]["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1}  # off-white
    layers[2]["fills"][0]["color"] = {"r":0.92,"g":0.92,"b":0.92,"a":1}  # very pale gray
    layers[3]["fills"][0]["color"] = {"r":0.90,"g":0.90,"b":0.90,"a":1}  # pale gray (out of tol)
    return H(layers)
add("J94: 4 different white shades", case_j94())

def case_j95():
    """1 ellipse colored differently."""
    layers = perfect_cloud()
    layers[2]["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.9,"a":1}  # blue tint
    return H(layers)
add("J95: 1 ellipse blue-tinted", case_j95())

def case_j96():
    return H(perfect_cloud())
add("J96: control perfect", case_j96())

def case_j97():
    """All ellipses overlapping at perfect location, cloud is 'compact'."""
    layers = perfect_cloud()
    for l in layers:
        l["x"] = 600
    return H(layers)
add("J97: all ellipses at same x (overlapping)", case_j97())

def case_j98():
    """3 cloud + 1 stretched."""
    layers = perfect_cloud()
    layers[0]["w"] = 800; layers[0]["h"] = 50
    return H(layers)
add("J98: 1 ellipse super wide-thin", case_j98())

def case_j99():
    """Cloud rotated 90° (vertical cloud)."""
    layers = perfect_cloud()
    for i, l in enumerate(layers):
        # swap x and y to rotate
        l["x"], l["y"] = l["y"], l["x"]
    return H(layers)
add("J99: cloud arranged vertically", case_j99())

def case_j100():
    return H(perfect_cloud())
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

"""100 edge cases for task 14 (4 concentric red/white circles with black strokes)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_14" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
BLACK = (0.0, 0.0, 0.0)


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


def perfect_target():
    """4 concentric circles, decreasing diameters, R/W/R/W from outermost to center,
    each with 4px black stroke."""
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    colors = [RED, WHITE, RED, WHITE]
    layers = []
    for size, color in zip(sizes, colors):
        l = L("ellipse", cx - size/2, cy - size/2, size, size, color)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return layers


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_target()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────
def case_a1():  return H(perfect_target() + [L("ellipse", 600, 416, 30, 30, RED, strokes=[make_stroke(rgb=BLACK,weight=4)])], evts=evt(ellipse=5))
add("A1: 5 circles (extra)", case_a1())

def case_a2():  return H(perfect_target()[:3], evts=evt(ellipse=3))
add("A2: 3 circles (missing)", case_a2())

def case_a3():  return H(perfect_target()[:2], evts=evt(ellipse=2))
add("A3: 2 circles only", case_a3())

def case_a4():  return H(perfect_target()[:1], evts=evt(ellipse=1))
add("A4: 1 circle only", case_a4())

def case_a5():  return H([], evts=evt(ellipse=0))
add("A5: 0 circles", case_a5())

def case_a6():  return H(perfect_target()*2, evts=evt(ellipse=8))
add("A6: 8 circles (doubled)", case_a6())

def case_a7():
    layers = perfect_target()
    layers.append(L("rectangle", 580, 400, 40, 40, RED))
    return H(layers, evts=evt(ellipse=4, extras=[make_event("create_rectangle")]))
add("A7: 4 circles + extra rect", case_a7())

def case_a8():
    """6 ellipses, last 2 are tiny."""
    layers = perfect_target()
    layers.append(L("ellipse", 600, 416, 20, 20, RED, strokes=[make_stroke(rgb=BLACK,weight=4)]))
    layers.append(L("ellipse", 600, 416, 10, 10, WHITE, strokes=[make_stroke(rgb=BLACK,weight=4)]))
    return H(layers, evts=evt(ellipse=6))
add("A8: 6 circles", case_a8())

def case_a9():  return H(perfect_target(), evts=evt(ellipse=4))
add("A9: 4 circles (control)", case_a9())

def case_a10():
    layers = perfect_target()
    layers[3]["w"] = layers[3]["h"] = 0
    return H(layers, evts=evt(ellipse=4))
add("A10: 4 circles, innermost is 0×0", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────
def case_b11():
    """All white circles."""
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    return H(layers)
add("B11: all white", case_b11())

def case_b12():
    """All red circles."""
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    return H(layers)
add("B12: all red", case_b12())

def case_b13():
    """Image fills."""
    layers = perfect_target()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: image fills", case_b13())

def case_b14():
    """Gradient fills."""
    layers = perfect_target()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B14: gradient fills", case_b14())

def case_b15():
    """No fills."""
    layers = perfect_target()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B15: no fills", case_b15())

def case_b16():
    """Reversed colors W/R/W/R."""
    layers = perfect_target()
    layers[0]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    layers[1]["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    layers[2]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    layers[3]["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    return H(layers)
add("B16: W/R/W/R (reversed)", case_b16())

def case_b17():
    """All blue."""
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.2,"g":0.4,"b":0.85,"a":1}
    return H(layers)
add("B17: all blue (wrong color)", case_b17())

def case_b18():
    """4 colors R/G/B/Y."""
    layers = perfect_target()
    layers[0]["fills"][0]["color"] = {"r":1,"g":0,"b":0,"a":1}
    layers[1]["fills"][0]["color"] = {"r":0,"g":1,"b":0,"a":1}
    layers[2]["fills"][0]["color"] = {"r":0,"g":0,"b":1,"a":1}
    layers[3]["fills"][0]["color"] = {"r":1,"g":1,"b":0,"a":1}
    return H(layers)
add("B18: R/G/B/Y (wrong colors)", case_b18())

def case_b19():
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0  # alpha=0
    return H(layers)
add("B19: alpha=0 (invisible)", case_b19())

def case_b20():
    layers = perfect_target()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B20: opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────
def case_c21():
    """All circles same size (no nesting)."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx-100, cy-100, 200, 200, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C21: all 4 circles same size", case_c21())

def case_c22():
    """Circles colored opposite: outermost=WHITE, then R/W/R."""
    layers = perfect_target()
    # Swap colors: outermost was RED, make it WHITE
    layers[0]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    layers[1]["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    layers[2]["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    layers[3]["fills"][0]["color"] = {"r":0.9,"g":0.15,"b":0.15,"a":1}
    return H(layers)
add("C22: W/R/W/R (reverse colors)", case_c22())

def case_c23():
    """All circles tiny (5×5)."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx-2, cy-2, 5, 5, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C23: all 5×5 (tiny)", case_c23())

def case_c24():
    """All circles huge (1000×1000)."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx-500, cy-500, 1000, 1000, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C24: all 1000×1000 (huge)", case_c24())

def case_c25():
    """Circles too thin: w=200 h=20 (oval not circle)."""
    layers = []
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    for size, color in zip(sizes, [RED,WHITE,RED,WHITE]):
        l = L("ellipse", cx-size/2, cy-10, size, 20, color)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C25: ellipses 200×20 (oval not circle)", case_c25())

def case_c26():
    """Circles tall: w=20 h=200 (vertical oval)."""
    layers = []
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    for size, color in zip(sizes, [RED,WHITE,RED,WHITE]):
        l = L("ellipse", cx-10, cy-size/2, 20, size, color)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C26: ellipses 20×200 (vertical oval)", case_c26())

def case_c27():
    """All circles 240 (same large size)."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx-120, cy-120, 240, 240, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("C27: all 240 size (no nesting)", case_c27())

def case_c28():
    """Smallest circle = 0×0."""
    layers = perfect_target()
    layers[3]["w"] = 0; layers[3]["h"] = 0
    return H(layers)
add("C28: innermost = 0×0 (degenerate)", case_c28())

def case_c29():
    """Same size but slightly different (within tol)."""
    layers = perfect_target()
    sizes = [240, 178, 122, 60]  # close but not exact
    cx, cy = 600, 416
    for i, (size, l) in enumerate(zip(sizes, layers)):
        l["x"] = cx-size/2; l["y"] = cy-size/2; l["w"] = size; l["h"] = size
    return H(layers)
add("C29: sizes 240/178/122/60 (slight variation)", case_c29())

def case_c30():
    """Sizes equal pairs: 240/240/120/120."""
    layers = perfect_target()
    sizes = [240, 240, 120, 120]
    cx, cy = 600, 416
    for i, (size, l) in enumerate(zip(sizes, layers)):
        l["x"] = cx-size/2; l["y"] = cy-size/2; l["w"] = size; l["h"] = size
    return H(layers)
add("C30: sizes 240/240/120/120 (pairs)", case_c30())


# ─── D. Position ────────────────────────────────────────────
def case_d31():
    """Circles concentric but offset to top-left of frame."""
    layers = perfect_target()
    for l in layers:
        l["x"] -= 400; l["y"] -= 350
    return H(layers)
add("D31: target shifted off-frame", case_d31())

def case_d32():
    """Slight offset in centers (each off by 1)."""
    layers = perfect_target()
    for i, l in enumerate(layers):
        l["x"] += i*0.5; l["y"] += i*0.5
    return H(layers)
add("D32: centers off by 0/0.5/1/1.5 (within tol)", case_d32())

def case_d33():
    """Centers off by 5px each (just over tol=2)."""
    layers = perfect_target()
    for i, l in enumerate(layers):
        l["x"] += i*5; l["y"] += i*5
    return H(layers)
add("D33: centers off by 5px steps", case_d33())

def case_d34():
    """Circles in a row (not concentric)."""
    layers = perfect_target()
    for i, l in enumerate(layers):
        l["x"] = 200 + i*150
        l["y"] = 300
    return H(layers)
add("D34: circles in a row (not concentric)", case_d34())

def case_d35():
    """Centers split: 2 inner left, 2 outer right."""
    layers = perfect_target()
    layers[2]["x"] -= 100
    layers[3]["x"] -= 100
    return H(layers)
add("D35: inner pair shifted left", case_d35())

def case_d36():
    """All circles at frame corner."""
    layers = perfect_target()
    for l in layers:
        l["x"] = 0; l["y"] = 0
    return H(layers)
add("D36: all at (0,0) corner", case_d36())

def case_d37():
    layers = perfect_target()
    for l in layers:
        l["y"] -= 1000  # negative y
    return H(layers)
add("D37: at negative y", case_d37())

def case_d38():
    """All circles at (1500, 1500) — past frame."""
    layers = perfect_target()
    for l in layers:
        l["x"] = 1500; l["y"] = 1500
    return H(layers)
add("D38: at (1500,1500) past frame", case_d38())

def case_d39():
    """Each circle at slightly different center but all overlap."""
    layers = perfect_target()
    for i, l in enumerate(layers):
        l["x"] += (i-1)*30; l["y"] += (i-1)*30
    return H(layers)
add("D39: progressive offset (no concentric)", case_d39())

def case_d40():
    return H(perfect_target())  # control
add("D40: target centered (control)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────
def case_e41():
    """Outermost rotated 45°."""
    layers = perfect_target()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: outermost rotated 45°", case_e41())

def case_e42():
    """All rotated 45°."""
    layers = perfect_target()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E42: all rotated 45°", case_e42())

def case_e43():
    """1 mirrored."""
    layers = perfect_target()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E43: outermost mirrored X", case_e43())

def case_e44():
    """All mirrored."""
    layers = perfect_target()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: all mirrored", case_e44())

def case_e45():
    """All have cornerRadius=120 (full circle)."""
    layers = perfect_target()
    for l in layers:
        l["cornerRadius"] = 200
    return H(layers)
add("E45: cornerRadius=200 (no-op for ellipse)", case_e45())

def case_e46():
    """All have rotation=4° (under tol)."""
    layers = perfect_target()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E46: rotation=4° (under tol=2) breaks", case_e46())

def case_e47():
    """1 ellipse rotated 90° (no visual change for circle)."""
    layers = perfect_target()
    layers[2]["rotation"] = 90
    return H(layers)
add("E47: 1 rotated 90° (circle invariant)", case_e47())

def case_e48():
    """1 missing stroke."""
    layers = perfect_target()
    layers[1]["strokes"] = []
    return H(layers)
add("E48: 1 ellipse no stroke", case_e48())

def case_e49():
    """1 stroke wrong color (red instead of black)."""
    layers = perfect_target()
    layers[1]["strokes"] = [make_stroke(rgb=RED, weight=4)]
    return H(layers)
add("E49: 1 stroke RED", case_e49())

def case_e50():
    """1 stroke wrong weight (10px instead of 4)."""
    layers = perfect_target()
    layers[1]["strokes"] = [make_stroke(rgb=BLACK, weight=10)]
    return H(layers)
add("E50: 1 stroke 10px", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────
def case_f51():
    """Strokes 0.5px (under tol)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=0.5)]
    return H(layers)
add("F51: stroke weight 0.5px", case_f51())

def case_f52():
    """All strokes 8px (over expected 4)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=8)]
    return H(layers)
add("F52: all strokes 8px", case_f52())

def case_f53():
    """Stroke alignment outside."""
    layers = perfect_target()
    for l in layers:
        l["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("F53: stroke alignment=outside", case_f53())

def case_f54():
    """Strokes dashed."""
    layers = perfect_target()
    for l in layers:
        l["strokes"][0]["dash"] = {"dash": 4, "gap": 4}
    return H(layers)
add("F54: dashed strokes", case_f54())

def case_f55():
    """All strokes gray (not black)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=GRAY, weight=4)]
    return H(layers)
add("F55: gray strokes", case_f55())

def case_f56():
    """All strokes white (invisible on white bg)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=(1,1,1), weight=4)]
    return H(layers)
add("F56: all strokes white", case_f56())

def case_f57():
    """No strokes at all."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = []
    return H(layers)
add("F57: no strokes", case_f57())

def case_f58():
    """Strokes 4.5px (within tol)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4.5)]
    return H(layers)
add("F58: strokes 4.5px (within tol)", case_f58())

def case_f59():
    """Stroke color is dark gray (within tol of black)."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=(0.1,0.1,0.1), weight=4)]
    return H(layers)
add("F59: dark gray strokes (within tol)", case_f59())

def case_f60():
    """4 colors RED/WHITE/RED/PINK (last is wrong)."""
    layers = perfect_target()
    layers[3]["fills"][0]["color"] = {"r":1,"g":0.5,"b":0.7,"a":1}
    return H(layers)
add("F60: innermost is PINK", case_f60())


# ─── G. Frame variants ─────────────────────────────────────
def case_g61():
    layers = perfect_target()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_target()
    inner = make_frame(layers, w=900, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_target(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, target in 2nd", case_g63())

def case_g64():
    layers = perfect_target()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_target()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_target()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_target()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G67: frame 2000×2000", case_g67())

def case_g68():
    layers = perfect_target()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G68: frame 200×200 (too small)", case_g68())

def case_g69():
    return H(perfect_target(), in_frame=False)
add("G69: target on page (no frame)", case_g69())

def case_g70():
    return H(perfect_target(), frame_w=1279, frame_h=831)
add("G70: frame 1279×831 (within tol)", case_g70())


# ─── H. Tools / events ─────────────────────────────────────
def case_h71():
    extras = [make_event("move_layer") for _ in range(50)]
    return H(evts=evt(extras=extras))
add("H71: 50 move_layer events", case_h71())

def case_h72():
    extras = [make_event("undo") for _ in range(50)]
    return H(evts=evt(extras=extras))
add("H72: 50 undo events", case_h72())

def case_h73():
    extras = [make_event("align_layers", axis="center_y"),
              make_event("align_layers", axis="center_x")]
    return H(evts=evt(extras=extras))
add("H73: align tools used", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 4)
    return H(evts=sem)
add("H74: rectangle tool used (no ellipse)", case_h74())

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
add("H79: 2 create_ellipse events (too few)", case_h79())

def case_h80():
    extras = [make_event("create_polygon"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H80: created+deleted polygon", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────
def case_i81():
    layers = perfect_target()
    group = {"id":"group_1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group in frame", case_i81())

def case_i82():
    layers = perfect_target()
    f1 = make_frame(layers[:2], w=600, h=832)
    f2 = make_frame(layers[2:], w=600, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_target()
    section = {"id":"sec_1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: in section (not frame)", case_i83())

def case_i84():
    layers = perfect_target()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested", case_i84())

def case_i85():
    layers = perfect_target()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: target on page 2", case_i85())

def case_i86():
    layers = perfect_target()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I86: each circle in own frame", case_i86())

def case_i87():
    layers = perfect_target()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only outermost in frame", case_i87())


# ─── J. Bizarre ────────────────────────────────────────────
def case_j88():
    """Outermost is a square (rectangle)."""
    layers = perfect_target()
    layers[0] = make_layer("rectangle", x=480, y=296, w=240, h=240, fill=RED,
                            strokes=[make_stroke(rgb=BLACK, weight=4)])
    return H(layers, evts=evt(ellipse=3, extras=[make_event("create_rectangle")]))
add("J88: outermost is rectangle", case_j88())

def case_j89():
    """All circles are stars."""
    layers = []
    cx, cy = 600, 416
    sizes = [240, 180, 120, 60]
    colors = [RED, WHITE, RED, WHITE]
    for size, color in zip(sizes, colors):
        l = make_layer("star", x=cx-size/2, y=cy-size/2, w=size, h=size, fill=color,
                       points=5, innerRatio=0.4)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_star")]*4))
add("J89: all 4 are stars (not ellipses)", case_j89())

def case_j90():
    return make_log([], [make_event("session_start")])
add("J90: empty document", case_j90())

def case_j91():
    return H([])
add("J91: frame only", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "target"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text 'target'", case_j92())

def case_j93():
    """All circles 1×1 piled."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx, cy, 1, 1, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("J93: all 1×1 piled", case_j93())

def case_j94():
    """Rotated 180 (no visual change for circle)."""
    layers = perfect_target()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("J94: all rotated 180° (invariant for circle)", case_j94())

def case_j95():
    """Inner-most is PINK."""
    layers = perfect_target()
    layers[3]["fills"][0]["color"] = {"r":1,"g":0.4,"b":0.7,"a":1}
    return H(layers)
add("J95: innermost PINK (not WHITE)", case_j95())

def case_j96():
    return H(perfect_target())
add("J96: control perfect", case_j96())

def case_j97():
    """Outer is BLACK (matches stroke), wrong color."""
    layers = perfect_target()
    layers[0]["fills"][0]["color"] = {"r":0,"g":0,"b":0,"a":1}
    return H(layers)
add("J97: outermost BLACK", case_j97())

def case_j98():
    """All ellipses with no stroke + extra rect with stroke."""
    layers = perfect_target()
    for l in layers:
        l["strokes"] = []
    layers.append(L("rectangle", 100, 100, 50, 50, BLACK,
                     strokes=[make_stroke(rgb=BLACK, weight=4)]))
    return H(layers, evts=evt(ellipse=4, extras=[make_event("create_rectangle")]))
add("J98: ellipses no stroke + rect has stroke", case_j98())

def case_j99():
    """4 circles concentric but tiny (10px each, all = 10px)."""
    layers = []
    cx, cy = 600, 416
    for c in [RED, WHITE, RED, WHITE]:
        l = L("ellipse", cx-5, cy-5, 10, 10, c)
        l["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
        layers.append(l)
    return H(layers)
add("J99: 4 tiny 10×10 stacked", case_j99())

def case_j100():
    return H(perfect_target())
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

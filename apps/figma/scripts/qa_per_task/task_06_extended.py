"""100 edge cases for task 06 — 8 lines from center at 45° intervals, gold strokes."""
from __future__ import annotations
import sys
import math
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_06" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
BLUE = (0.2, 0.4, 0.85)
GRAY = (0.5, 0.5, 0.5)


def evt(line=8, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(line):
        sem.append(make_event("create_line"))
    sem.extend(extras)
    return sem


def line(rot, color=GOLD, length=200, cx=500, cy=500, weight=2):
    return make_layer("line", x=cx, y=cy, w=length, h=2,
                      fill=None, strokes=[make_stroke(rgb=color, weight=weight)],
                      rotation=rot)


def perfect_burst(n=8, step=45, length=200, color=GOLD, cx=500, cy=500, weight=2):
    return [line(i*step, color=color, length=length, cx=cx, cy=cy, weight=weight) for i in range(n)]


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=False):
    if layers is None: layers = perfect_burst()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ────────────────────────────────────────────────────────
def case_a1():
    layers = perfect_burst() + [line(202.5)]
    return H(layers, evts=evt(line=9))
add("A1: 9 lines (extra)", case_a1())

def case_a2():
    return H(perfect_burst(n=7, step=45), evts=evt(line=7))
add("A2: 7 lines (missing 1)", case_a2())

def case_a3():
    return H(perfect_burst(n=4, step=90), evts=evt(line=4))
add("A3: 4 lines at 90° (insufficient)", case_a3())

def case_a4():
    return H(perfect_burst(n=16, step=22.5), evts=evt(line=16))
add("A4: 16 lines at 22.5° (doubled density)", case_a4())

def case_a5():
    return H([], evts=evt(line=0))
add("A5: empty", case_a5())

def case_a6():
    return H([line(0)], evts=evt(line=1))
add("A6: 1 line only", case_a6())

def case_a7():
    layers = perfect_burst() * 2
    return H(layers, evts=evt(line=16))
add("A7: 16 lines (doubled identical)", case_a7())

def case_a8():
    layers = perfect_burst()
    layers.append(make_layer("rectangle", x=200, y=200, w=100, h=100, fill=GOLD))
    return H(layers, evts=evt(line=8, extras=[make_event("create_rectangle")]))
add("A8: 8 lines + rectangle extra", case_a8())

def case_a9():
    layers = perfect_burst(n=10, step=36)  # 10 lines at 36° not 45°
    return H(layers, evts=evt(line=10))
add("A9: 10 lines at 36°", case_a9())

def case_a10():
    layers = perfect_burst(n=6, step=60)
    return H(layers, evts=evt(line=6))
add("A10: 6 lines at 60°", case_a10())


# ─── B. Colors / fills (strokes for lines) ───────────────────────────
def case_b11():
    """All red strokes."""
    return H(perfect_burst(color=RED))
add("B11: all red strokes (not gold)", case_b11())

def case_b12():
    """All blue strokes."""
    return H(perfect_burst(color=BLUE))
add("B12: all blue strokes", case_b12())

def case_b13():
    """1 red, 7 gold."""
    layers = perfect_burst()
    layers[0]["strokes"][0]["paint"]["color"] = {"r":1, "g":0, "b":0, "a":1}
    return H(layers)
add("B13: 1 red + 7 gold", case_b13())

def case_b14():
    """All white strokes."""
    return H(perfect_burst(color=WHITE))
add("B14: all white strokes", case_b14())

def case_b15():
    """No strokes (lines have no stroke)."""
    layers = perfect_burst()
    for l in layers: l["strokes"] = []
    return H(layers)
add("B15: no strokes", case_b15())

def case_b16():
    """Stroke alpha=0 (invisible)."""
    layers = perfect_burst()
    for l in layers: l["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("B16: stroke alpha=0", case_b16())

def case_b17():
    """All gold but slightly different shades."""
    layers = perfect_burst()
    for i, l in enumerate(layers):
        l["strokes"][0]["paint"]["color"] = {"r":0.85+i*0.005, "g":0.65, "b":0.13, "a":1}
    return H(layers)
add("B17: 8 distinct gold shades", case_b17())

def case_b18():
    """Gold gradient stroke."""
    layers = perfect_burst()
    for l in layers:
        l["strokes"][0]["paint"] = {"kind": "gradient", "stops": [
            {"position": 0, "color": {"r":1, "g":1, "b":0, "a":1}},
            {"position": 1, "color": {"r":0.5, "g":0.4, "b":0, "a":1}}]}
    return H(layers)
add("B18: gradient strokes", case_b18())

def case_b19():
    """Stroke weight=0."""
    layers = perfect_burst(weight=0)
    return H(layers)
add("B19: stroke weight=0", case_b19())

def case_b20():
    """Stroke visible=False."""
    layers = perfect_burst()
    for l in layers: l["strokes"][0]["visible"] = False
    return H(layers)
add("B20: stroke visible=False", case_b20())


# ─── C. Sizing / length ───────────────────────────────────────────────
def case_c21():
    """All 1px length."""
    return H(perfect_burst(length=1))
add("C21: lines length=1", case_c21())

def case_c22():
    """Different lengths (50-400)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, length=50+i*50))
    return H(layers)
add("C22: lines length 50-400 varying", case_c22())

def case_c23():
    """All 5000 length (massive)."""
    return H(perfect_burst(length=5000))
add("C23: lines length=5000", case_c23())

def case_c24():
    """All 0 length."""
    return H(perfect_burst(length=0))
add("C24: lines length=0", case_c24())

def case_c25():
    """All same long lines (300)."""
    return H(perfect_burst(length=300))
add("C25: lines length=300", case_c25())

def case_c26():
    """Lines have non-zero h (rectangle-like, but type=line)."""
    layers = perfect_burst()
    for l in layers: l["h"] = 100
    return H(layers)
add("C26: lines h=100 (thick rectangles?)", case_c26())

def case_c27():
    """Stroke weight=20 (very thick)."""
    return H(perfect_burst(weight=20))
add("C27: stroke weight=20", case_c27())

def case_c28():
    """Lines with weights 1, 2, 3, ..., 8 (varying)."""
    layers = perfect_burst()
    for i, l in enumerate(layers): l["strokes"][0]["weight"] = i + 1
    return H(layers)
add("C28: stroke weights 1-8", case_c28())

def case_c29():
    """Lines pointing in 8 directions but length 1px each (essentially dots)."""
    return H(perfect_burst(length=1))
add("C29: same as c21", case_c29())

def case_c30():
    """Lines at different lengths (1, 100, 200, ...)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, length=2**(i+3)))  # 8, 16, 32, 64, ..., 1024
    return H(layers)
add("C30: lines length geometric (8 to 1024)", case_c30())


# ─── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Lines not concentric (each at different center)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=100+i*100, cy=300))
    return H(layers)
add("D31: lines not concentric (8 in row)", case_d31())

def case_d32():
    """Lines all at far point (5000,5000)."""
    return H(perfect_burst(cx=5000, cy=5000))
add("D32: burst at (5000,5000)", case_d32())

def case_d33():
    """Lines drawn from (0,0)."""
    return H(perfect_burst(cx=0, cy=0))
add("D33: burst at origin (0,0)", case_d33())

def case_d34():
    """Lines slightly off-center."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=500+(i%3)*5, cy=500+(i%3)*5))
    return H(layers)
add("D34: lines slightly off-center (within tol)", case_d34())

def case_d35():
    """Lines drawn from page corners."""
    layers = []
    centers = [(100,100), (900,100), (100,900), (900,900)] * 2
    for i, (cx, cy) in enumerate(centers):
        layers.append(line(i*45, cx=cx, cy=cy))
    return H(layers)
add("D35: lines from 4 corners", case_d35())

def case_d36():
    """Lines at exact same point but different angles (concentric)."""
    return H(perfect_burst())
add("D36: perfect burst (control)", case_d36())

def case_d37():
    """Lines drawn very far from each other (not concentric)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=100+i*200, cy=500))
    return H(layers)
add("D37: lines spaced 200px apart (non-concentric)", case_d37())

def case_d38():
    """Lines off-center by 12px (over 10 tol)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=500+(i%2)*15, cy=500))
    return H(layers)
add("D38: lines ±15px (over tol)", case_d38())

def case_d39():
    """Lines stacked at same point."""
    return H([line(0) for _ in range(8)])
add("D39: 8 lines all rotation=0 stacked", case_d39())

def case_d40():
    """Lines on diagonal of frame (not from center)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=100+i*100, cy=100+i*100))
    return H(layers)
add("D40: lines on diagonal not from center", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────────
def case_e41():
    """Step is 22.5° (16 angles, 8 lines but wrong step)."""
    return H([line(i*22.5) for i in range(8)])
add("E41: lines at 22.5° step", case_e41())

def case_e42():
    """Step is 60°."""
    return H([line(i*60) for i in range(8)])
add("E42: lines at 60° step", case_e42())

def case_e43():
    """Lines 4 at 0° and 4 at 90°."""
    layers = [line(0) for _ in range(4)] + [line(90) for _ in range(4)]
    return H(layers)
add("E43: 4 at 0° + 4 at 90°", case_e43())

def case_e44():
    """All scaleX=-1."""
    layers = perfect_burst()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("E44: all scaleX=-1", case_e44())

def case_e45():
    """Lines step 44° (instead of 45°)."""
    return H([line(i*44) for i in range(8)])
add("E45: lines at 44° step", case_e45())

def case_e46():
    """Lines step 46° (just over 45°)."""
    return H([line(i*46) for i in range(8)])
add("E46: lines at 46° step", case_e46())

def case_e47():
    """All same rotation (0°)."""
    return H([line(0) for _ in range(8)])
add("E47: all lines rot=0°", case_e47())

def case_e48():
    """Step is 45.5° (just inside 8° tolerance for evenly rotated)."""
    return H([line(i*45.5) for i in range(8)])
add("E48: lines at 45.5° step", case_e48())

def case_e49():
    """Lines all same start point but with different scaleX."""
    layers = [line(i*45) for i in range(8)]
    layers[3]["scaleX"] = -1
    return H(layers)
add("E49: 1 line scaleX=-1", case_e49())

def case_e50():
    """Lines reversed: 0, -45, -90... (= 0, 315, 270...)."""
    layers = [line(-i*45) for i in range(8)]
    return H(layers)
add("E50: lines reversed direction (still 8 angles)", case_e50())


# ─── F. Subcomponent variants ─────────────────────────────────────────
def case_f51():
    """8 vectors instead of lines."""
    layers = []
    for i in range(8):
        l = make_layer("vector", x=500, y=500, w=200, h=2, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=2)], rotation=i*45)
        layers.append(l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_vector")] * 8)
    return H(layers, evts=sem)
add("F51: 8 vectors instead of lines", case_f51())

def case_f52():
    """8 thin rectangles (not lines)."""
    layers = []
    for i in range(8):
        l = make_layer("rectangle", x=500, y=499, w=200, h=2, fill=GOLD, rotation=i*45)
        layers.append(l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 8)
    return H(layers, evts=sem)
add("F52: 8 thin rectangles (not lines)", case_f52())

def case_f53():
    """Mix of 4 lines + 4 rectangles."""
    layers = [line(i*45) for i in range(4)]
    for i in range(4):
        layers.append(make_layer("rectangle", x=500, y=499, w=200, h=2, fill=GOLD, rotation=180+i*45))
    sem = evt(line=4, extras=[make_event("tool_change", before="line", after="rectangle"),
                                *[make_event("create_rectangle") for _ in range(4)]])
    return H(layers, evts=sem)
add("F53: 4 lines + 4 rectangles", case_f53())

def case_f54():
    """Lines without rotation property (all flat horizontal)."""
    layers = []
    for i in range(8):
        l = line(0)  # all 0°
        layers.append(l)
    return H(layers)
add("F54: all 8 lines rotation=0°", case_f54())

def case_f55():
    """Lines have visible=False on layer."""
    layers = perfect_burst()
    for l in layers: l["visible"] = False
    return H(layers)
add("F55: all lines layer.visible=False", case_f55())

def case_f56():
    """Burst rotated (whole burst rotated 30° as 1 unit)."""
    layers = perfect_burst()
    for l in layers: l["rotation"] += 30
    return H(layers)
add("F56: burst rotated 30° (still 45° step)", case_f56())

def case_f57():
    """Lines + extra strokes."""
    layers = perfect_burst()
    for l in layers:
        l["strokes"].append(make_stroke(rgb=RED, weight=2))
    return H(layers)
add("F57: lines with 2 strokes each", case_f57())

def case_f58():
    """Lines with weights 0.1 (tiny)."""
    return H(perfect_burst(weight=0.1))
add("F58: stroke weight=0.1", case_f58())

def case_f59():
    """Burst with 8 lines, 1 of which is dashed."""
    layers = perfect_burst()
    layers[0]["strokes"][0]["dash"] = {"dash":4, "gap":4}
    return H(layers)
add("F59: 1 dashed line", case_f59())

def case_f60():
    """Lines in a frame."""
    return H(in_frame=True)
add("F60: lines inside frame", case_f60())


# ─── G. Frame variants ────────────────────────────────────────────────
def case_g61():
    """Frame rotated 45° with burst inside."""
    layers = perfect_burst()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Burst in nested frames."""
    layers = perfect_burst()
    inner = make_frame(layers, w=900, h=900)
    outer = make_frame([inner], w=1100, h=1100)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """Burst split across 2 frames."""
    layers = perfect_burst()
    f1 = make_frame(layers[:4], w=500, h=500)
    f2 = make_frame(layers[4:], w=500, h=500)
    return make_log([f1, f2], evt())
add("G63: burst split across 2 frames", case_g63())

def case_g64():
    """Frame stroke."""
    layers = perfect_burst()
    frame = make_frame(layers, w=900, h=900)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    """Frame image fill."""
    layers = perfect_burst()
    frame = make_frame(layers, w=900, h=900, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    """Frame translated to (1000, 1000)."""
    layers = perfect_burst()
    frame = make_frame(layers, x=1000, y=1000, w=900, h=900)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    """Tiny frame 200x200."""
    return H(in_frame=True, frame_w=200, frame_h=200)
add("G67: tiny frame 200x200", case_g67())

def case_g68():
    """Huge frame 3000x3000."""
    return H(in_frame=True, frame_w=3000, frame_h=3000)
add("G68: 3000x3000 frame", case_g68())

def case_g69():
    """Lines off-frame (negative coords)."""
    layers = perfect_burst(cx=-500, cy=-500)
    return H(layers)
add("G69: burst at negative coords", case_g69())

def case_g70():
    """Burst exactly fits frame."""
    return H(in_frame=True, frame_w=400, frame_h=400)
add("G70: 400x400 frame fits burst", case_g70())


# ─── H. Tools / events ────────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())

def case_h73():
    """No tool_change."""
    sem = [make_event("session_start")]
    sem.extend([make_event("create_line")] * 8)
    return H(evts=sem)
add("H73: no tool_change", case_h73())

def case_h74():
    """Wrong tool (rectangle)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_line")] * 8)
    return H(evts=sem)
add("H74: rectangle tool", case_h74())

def case_h75():
    """Pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_line")] * 8)
    return H(evts=sem)
add("H75: pen tool", case_h75())

def case_h76():
    """8 creates + 5 deletes."""
    sem = evt()
    sem.extend([make_event("delete") for _ in range(5)])
    return H(evts=sem)
add("H76: 8 + 5 deletes", case_h76())

def case_h77():
    """0 creates."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    return H(evts=sem)
add("H77: 0 create_line", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H78: align_layers used", case_h78())

def case_h79():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute_layers", case_h79())

def case_h80():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H80: many session_end", case_h80())


# ─── I. Hierarchy ─────────────────────────────────────────────────────
def case_i81():
    """Burst in group."""
    layers = perfect_burst()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([g], evt())
add("I81: burst in group", case_i81())

def case_i82():
    """Burst split: 4 in 1 frame, 4 in another."""
    layers = perfect_burst()
    f1 = make_frame(layers[:4], w=500, h=500)
    f2 = make_frame(layers[4:], w=500, h=500)
    return make_log([f1, f2], evt())
add("I82: burst split across 2 frames", case_i82())

def case_i83():
    """Burst in section."""
    layers = perfect_burst()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":900,"h":900,"fills":[],"children":layers}
    return make_log([section], evt())
add("I83: burst in section", case_i83())

def case_i84():
    """Burst on page."""
    return H(in_frame=False)
add("I84: burst on page (no frame)", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_burst()
    f3 = make_frame(layers, w=900, h=900)
    f2 = make_frame([f3], w=950, h=950)
    f1 = make_frame([f2], w=1000, h=1000)
    return make_log([f1], evt())
add("I85: 3-deep nested", case_i85())

def case_i86():
    """Burst on page 2."""
    layers = perfect_burst()
    p1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    p2 = {"id":"p2","children":layers,"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[p1,p2]}}}
add("I86: burst on page 2", case_i86())

def case_i87():
    """Each line in own frame."""
    layers = perfect_burst()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I87: each line in own frame", case_i87())

def case_i88():
    """Burst inside component."""
    layers = perfect_burst()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I88: burst in component", case_i88())

def case_i89():
    """Half in frame, half on page."""
    layers = perfect_burst()
    frame = make_frame(layers[:4], w=900, h=900)
    return make_log([frame, *layers[4:]], evt())
add("I89: 4 in frame, 4 outside", case_i89())

def case_i90():
    """In nested groups."""
    layers = perfect_burst()
    g1 = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    g2 = {"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g1]}
    return make_log([g2], evt())
add("I90: burst in nested groups", case_i90())


# ─── J. Bizarre ───────────────────────────────────────────────────────
def case_j91():
    """All lines scaleX=-1."""
    layers = perfect_burst()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J91: all scaleX=-1", case_j91())

def case_j92():
    """Empty doc."""
    return make_log([], [make_event("session_start")])
add("J92: empty document", case_j92())

def case_j93():
    """Text 'burst'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=GOLD)
    text["content"] = "asterisk burst"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J93: text 'burst'", case_j93())

def case_j94():
    """8 stars (4-pointed) instead of lines."""
    layers = []
    cx, cy = 500, 500
    for i in range(8):
        a = math.radians(i*45)
        layers.append(make_layer("star", x=cx+200*math.cos(a)-30, y=cy+200*math.sin(a)-30,
                                  w=60, h=60, fill=GOLD, points=4, innerRatio=0.5))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 8)
    return H(layers, evts=sem)
add("J94: 8 stars (no lines)", case_j94())

def case_j95():
    """Lines in 8 directions but length 0 (zero-length)."""
    return H(perfect_burst(length=0))
add("J95: 8 zero-length lines", case_j95())

def case_j96():
    """Lines + frame rotated 90°."""
    layers = perfect_burst()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 90
    return make_log([frame], evt())
add("J96: frame rotated 90°", case_j96())

def case_j97():
    """All 8 lines at exact same rotation."""
    return H([line(45) for _ in range(8)])
add("J97: 8 lines all rotation=45°", case_j97())

def case_j98():
    """Lines at 8 angles but spread across frame (not concentric)."""
    layers = []
    for i in range(8):
        a = math.radians(i*45)
        cx = 500 + 200 * math.cos(a)
        cy = 500 + 200 * math.sin(a)
        layers.append(line(i*45, cx=cx, cy=cy))
    return H(layers)
add("J98: lines at 8 angles spread on circle", case_j98())

def case_j99():
    """Lines all rotated 45° + something."""
    return H([line(45 + i*45) for i in range(8)])
add("J99: lines starting at 45° (still 45° step)", case_j99())

def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95 and not label.startswith("J100"):
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95, not J100): {fp_count}")

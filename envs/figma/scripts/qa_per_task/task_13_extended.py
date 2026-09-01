"""100 edge cases for task 13 (4 lines forming a hashtag)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_13" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(line=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(line):
        sem.append(make_event("create_line"))
    sem.extend(extras)
    return sem


def line_layer(x, y, length=200, rotation=0, fill=NAVY, **extra):
    """Build a line layer at (x,y) with given length and rotation."""
    layer = make_layer("line", x=x, y=y, w=length, h=4, fill=fill, **extra)
    layer["rotation"] = rotation
    layer["p1"] = {"x": 0, "y": 0}
    layer["p2"] = {"x": length, "y": 0}
    layer["strokes"] = [make_stroke(rgb=fill, weight=4)]
    return layer


def perfect_hashtag():
    """2 horizontal lines (rotation=0) + 2 vertical lines (rotation=90), forming a #.

    All lines stored with the same bbox shape (w=300, h=4 — visually horizontal).
    Rotation property differentiates: 0 → horizontal, 90 → vertical (rotates around center).
    """
    # Horizontal lines: long layer in x, rotation=0
    h1 = make_layer("line", x=300, y=270, w=300, h=4, fill=NAVY)
    h1["rotation"] = 0
    h1["p1"] = {"x": 0, "y": 0}; h1["p2"] = {"x": 300, "y": 0}
    h2 = make_layer("line", x=300, y=400, w=300, h=4, fill=NAVY)
    h2["rotation"] = 0
    h2["p1"] = {"x": 0, "y": 0}; h2["p2"] = {"x": 300, "y": 0}
    # Vertical lines: same long bbox, rotation=90 puts them upright when rendered
    v1 = make_layer("line", x=300, y=200, w=300, h=4, fill=NAVY)
    v1["rotation"] = 90
    v1["p1"] = {"x": 0, "y": 0}; v1["p2"] = {"x": 300, "y": 0}
    v2 = make_layer("line", x=420, y=200, w=300, h=4, fill=NAVY)
    v2["rotation"] = 90
    v2["p1"] = {"x": 0, "y": 0}; v2["p2"] = {"x": 300, "y": 0}
    return [h1, h2, v1, v2]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_hashtag()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────
def case_a1():
    layers = perfect_hashtag()
    extra = make_layer("line", x=300, y=350, w=400, h=4, fill=PINK)
    extra["rotation"] = 0; extra["p1"]={"x":0,"y":0}; extra["p2"]={"x":400,"y":0}
    layers.append(extra)
    return H(layers, evts=evt(line=5))
add("A1: 5 lines (extra horizontal)", case_a1())

def case_a2():
    return H(perfect_hashtag()[:3], evts=evt(line=3))
add("A2: 3 lines (1 missing)", case_a2())

def case_a3():
    return H(perfect_hashtag()[:2], evts=evt(line=2))
add("A3: 2 lines (only verticals)", case_a3())

def case_a4():
    return H(perfect_hashtag()[2:], evts=evt(line=2))
add("A4: 2 lines (only horizontals)", case_a4())

def case_a5():
    return H(perfect_hashtag() * 2, evts=evt(line=8))
add("A5: 8 lines (doubled set)", case_a5())

def case_a6():
    return H([], evts=evt(line=0))
add("A6: 0 lines", case_a6())

def case_a7():
    layers = perfect_hashtag()
    layers.append(make_layer("rectangle", x=400, y=300, w=200, h=200, fill=PINK))
    return H(layers, evts=evt(line=4, extras=[make_event("create_rectangle")]))
add("A7: 4 lines + 1 rectangle", case_a7())

def case_a8():
    layers = perfect_hashtag()[:1]  # only 1 vertical
    return H(layers, evts=evt(line=1))
add("A8: 1 line only", case_a8())

def case_a9():
    layers = perfect_hashtag()
    # add 2 more horizontal
    extras = [make_layer("line", x=340, y=300, w=300, h=4, fill=NAVY) for _ in range(2)]
    for e in extras: e["rotation"]=0; e["p1"]={"x":0,"y":0}; e["p2"]={"x":300,"y":0}
    return H(layers + extras, evts=evt(line=6))
add("A9: 6 lines", case_a9())

def case_a10():
    return H(perfect_hashtag(), evts=evt(line=4))
add("A10: 4 lines (control)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────
def case_b11():
    layers = perfect_hashtag()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
        l["fills"] = []
    return H(layers)
add("B11: stroke-only (no fill)", case_b11())

def case_b12():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0  # alpha=0
    return H(layers)
add("B12: fills alpha=0 (invisible)", case_b12())

def case_b13():
    layers = perfect_hashtag()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B13: layer opacity=0", case_b13())

def case_b14():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("B14: fills visible=False", case_b14())

def case_b15():
    layers = perfect_hashtag()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=(1,1,1), weight=1, dash={"dash":4,"gap":2})]
    return H(layers)
add("B15: dashed strokes", case_b15())

def case_b16():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"] = []
        l["strokes"] = []
    return H(layers)
add("B16: no fills, no strokes (invisible)", case_b16())

def case_b17():
    layers = perfect_hashtag()
    layers[0]["fills"][0]["color"] = {"r":1,"g":0,"b":0,"a":1}
    layers[1]["fills"][0]["color"] = {"r":0,"g":1,"b":0,"a":1}
    layers[2]["fills"][0]["color"] = {"r":0,"g":0,"b":1,"a":1}
    layers[3]["fills"][0]["color"] = {"r":1,"g":1,"b":0,"a":1}
    return H(layers)
add("B17: 4 different colors", case_b17())

def case_b18():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B18: image fills", case_b18())

def case_b19():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fills opacity=0.05", case_b19())

def case_b20():
    layers = perfect_hashtag()
    for l in layers:
        l["fills"].extend([
            {"kind":"image","src":"x.jpg","fit":"cover","opacity":0.5,"visible":True},
            {"kind":"solid","color":{"r":0,"g":0,"b":0,"a":1},"opacity":0.3,"visible":True}])
    return H(layers)
add("B20: stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────
def case_c21():
    layers = perfect_hashtag()
    layers[0]["h"] = 5  # very short vertical
    return H(layers)
add("C21: 1 vertical only 5px tall", case_c21())

def case_c22():
    layers = perfect_hashtag()
    layers[2]["w"] = 5
    return H(layers)
add("C22: 1 horizontal only 5px wide", case_c22())

def case_c23():
    layers = perfect_hashtag()
    layers[0]["h"] = 1500  # massive vertical
    return H(layers)
add("C23: 1 vertical 1500px tall (off-frame)", case_c23())

def case_c24():
    layers = perfect_hashtag()
    layers[2]["w"] = 1500
    return H(layers)
add("C24: 1 horizontal 1500px wide (off-frame)", case_c24())

def case_c25():
    layers = perfect_hashtag()
    for l in layers:
        if l["w"] > l["h"]:
            l["w"] = 1
        else:
            l["h"] = 1
    return H(layers)
add("C25: all lines 1px length", case_c25())

def case_c26():
    layers = perfect_hashtag()
    layers[0]["h"] = 80  # 80px vertical (matches 100 length-min if any)
    layers[1]["h"] = 80
    layers[2]["w"] = 80
    layers[3]["w"] = 80
    return H(layers)
add("C26: all lines 80px (smaller)", case_c26())

def case_c27():
    layers = perfect_hashtag()
    layers[2]["w"] = 100  # 1 horizontal half-length
    return H(layers)
add("C27: 1 horizontal half-length", case_c27())

def case_c28():
    # h1 doesn't span both verticals
    layers = perfect_hashtag()
    layers[2]["x"] = 200
    layers[2]["w"] = 100  # only spans left of v1
    return H(layers)
add("C28: 1 horizontal too short to cross both verticals", case_c28())

def case_c29():
    layers = perfect_hashtag()
    layers[0]["w"] = 50  # 50px wide vertical (not a line)
    layers[0]["h"] = 50
    return H(layers)
add("C29: 1 vertical = 50×50 square (not line-like)", case_c29())

def case_c30():
    layers = perfect_hashtag()
    layers[2]["h"] = 50  # thick horizontal — looks like rect
    return H(layers)
add("C30: 1 horizontal h=50 (very thick)", case_c30())


# ─── D. Position ────────────────────────────────────────────
def case_d31():
    layers = perfect_hashtag()
    # Both verticals to far left, horizontals far right
    layers[0]["x"] = 100; layers[1]["x"] = 200
    layers[2]["x"] = 700; layers[3]["x"] = 700
    return H(layers)
add("D31: vertical/horizontal sets apart (no overlap)", case_d31())

def case_d32():
    layers = perfect_hashtag()
    # Move all lines way off frame
    for l in layers:
        l["x"] -= 600; l["y"] -= 400
    return H(layers)
add("D32: lines off-frame top-left", case_d32())

def case_d33():
    layers = perfect_hashtag()
    for l in layers:
        l["y"] -= 1500  # negative y
    return H(layers)
add("D33: lines at negative y", case_d33())

def case_d34():
    # Verticals don't cross horizontals
    layers = perfect_hashtag()
    layers[0]["y"] = 100; layers[0]["h"] = 50  # vertical too short
    layers[1]["y"] = 100; layers[1]["h"] = 50
    return H(layers)
add("D34: verticals don't cross horizontals", case_d34())

def case_d35():
    layers = perfect_hashtag()
    # 2 verticals at same x — overlap (layers 2,3 are verticals)
    layers[3]["x"] = layers[2]["x"]
    return H(layers)
add("D35: 2 verticals at same x (overlap)", case_d35())

def case_d36():
    layers = perfect_hashtag()
    # 2 horizontals at same y — overlap (layers 0,1 are horizontals)
    layers[1]["y"] = layers[0]["y"]
    return H(layers)
add("D36: 2 horizontals at same y (overlap)", case_d36())

def case_d37():
    layers = perfect_hashtag()
    # All 4 lines at center pile
    for l in layers:
        l["x"] = 600; l["y"] = 400
    return H(layers)
add("D37: all 4 lines piled at center", case_d37())

def case_d38():
    layers = perfect_hashtag()
    # Small offsets but still functional hashtag
    layers[0]["x"] += 5; layers[1]["x"] += 5
    layers[2]["y"] += 5; layers[3]["y"] += 5
    return H(layers)
add("D38: small offsets (still hashtag-like)", case_d38())

def case_d39():
    layers = perfect_hashtag()
    # Verticals on either side of frame, horizontals at top + bottom — square
    layers[0] = make_layer("line", x=100, y=100, w=4, h=600, fill=NAVY)
    layers[0]["rotation"] = 90
    layers[1] = make_layer("line", x=900, y=100, w=4, h=600, fill=NAVY)
    layers[1]["rotation"] = 90
    layers[2] = make_layer("line", x=100, y=100, w=800, h=4, fill=NAVY)
    layers[2]["rotation"] = 0
    layers[3] = make_layer("line", x=100, y=700, w=800, h=4, fill=NAVY)
    layers[3]["rotation"] = 0
    return H(layers)
add("D39: rectangle outline (4 lines, but no inner crossings)", case_d39())

def case_d40():
    return H(perfect_hashtag())  # control
add("D40: perfect # (control)", case_d40())


# ─── E. Per-shape variants (rotation) ──────────────────────────
def case_e41():
    layers = perfect_hashtag()
    layers[0]["rotation"] = 45  # 1 vertical at 45°
    return H(layers)
add("E41: 1 vertical rotated 45° (diagonal)", case_e41())

def case_e42():
    layers = perfect_hashtag()
    for l in layers:
        l["rotation"] = 0  # all horizontal
    return H(layers)
add("E42: all 4 lines horizontal", case_e42())

def case_e43():
    layers = perfect_hashtag()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E43: all 4 lines vertical", case_e43())

def case_e44():
    layers = perfect_hashtag()
    layers[0]["rotation"] = 45
    layers[1]["rotation"] = 135
    layers[2]["rotation"] = 45
    layers[3]["rotation"] = 135
    return H(layers)
add("E44: lines at 45/135 (diagonal X)", case_e44())

def case_e45():
    layers = perfect_hashtag()
    layers[0]["rotation"] = 80  # 80° (10° off vertical)
    layers[1]["rotation"] = 100
    return H(layers)
add("E45: verticals at 80 and 100° (off by 10°)", case_e45())

def case_e46():
    layers = perfect_hashtag()
    layers[0]["rotation"] = 7  # under 8° tolerance
    layers[1]["rotation"] = 7
    return H(layers)
add("E46: verticals at 7° (under tol but bad)", case_e46())

def case_e47():
    layers = perfect_hashtag()
    layers[2]["rotation"] = 5
    layers[3]["rotation"] = -5
    return H(layers)
add("E47: horizontals at +5°/-5° (under tol)", case_e47())

def case_e48():
    layers = perfect_hashtag()
    layers[0]["rotation"] = 270  # 270 = -90 (same as 90 in line context? depends)
    layers[1]["rotation"] = 270
    return H(layers)
add("E48: verticals at 270°", case_e48())

def case_e49():
    layers = perfect_hashtag()
    # 3 horizontal, 1 vertical (change one vertical to horizontal)
    layers[2]["rotation"] = 0  # was 90 vertical → now horizontal
    return H(layers)
add("E49: 3H+1V rotations", case_e49())

def case_e50():
    layers = perfect_hashtag()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E50: all lines flipped X", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────
def case_f51():
    """Lines too short — don't form crossings."""
    layers = perfect_hashtag()
    layers[2]["w"] = 80  # h1 too short
    layers[3]["w"] = 80
    layers[2]["x"] = 410; layers[3]["x"] = 410
    return H(layers)
add("F51: horizontals too short to cross both verticals", case_f51())

def case_f52():
    """Verticals very close (overlapping or near-flush)."""
    layers = perfect_hashtag()
    layers[3]["x"] = layers[2]["x"] + 10  # verticals 10px apart
    return H(layers)
add("F52: verticals only 10px apart", case_f52())

def case_f53():
    """Horizontals very close."""
    layers = perfect_hashtag()
    layers[1]["y"] = layers[0]["y"] + 10  # horizontals 10px apart
    return H(layers)
add("F53: horizontals only 10px apart", case_f53())

def case_f54():
    """Asymmetric # — gap between horizontals different from gap between verticals."""
    layers = perfect_hashtag()
    layers[1]["y"] = layers[0]["y"] + 200  # huge gap between horizontals
    return H(layers)
add("F54: horizontals 200px apart, verticals 120 apart", case_f54())

def case_f55():
    """Two verticals far apart, two horizontals close together."""
    layers = perfect_hashtag()
    layers[3]["x"] = layers[2]["x"] + 600  # verticals 600px apart
    return H(layers)
add("F55: verticals 600px apart", case_f55())

def case_f56():
    """All 4 lines stacked vertically."""
    layers = []
    for i in range(4):
        l = make_layer("line", x=400, y=200+i*50, w=200, h=4, fill=NAVY)
        l["rotation"] = 0
        l["p1"]={"x":0,"y":0}; l["p2"]={"x":200,"y":0}
        layers.append(l)
    return H(layers)
add("F56: 4 horizontal lines stacked (no verticals)", case_f56())

def case_f57():
    """Bowtie pattern — 2 lines crossing at center, 2 outside."""
    layers = perfect_hashtag()
    layers[0]["rotation"] = 45
    layers[1]["rotation"] = -45
    return H(layers)
add("F57: 2 diagonals + 2 horizontals", case_f57())

def case_f58():
    layers = perfect_hashtag()
    # mixed rotations: 2 at 60, 2 at 30
    layers[0]["rotation"] = 60
    layers[1]["rotation"] = 60
    layers[2]["rotation"] = 30
    layers[3]["rotation"] = 30
    return H(layers)
add("F58: rotations 60/60/30/30 (not perpendicular)", case_f58())

def case_f59():
    """Lines fanned out — radial pattern."""
    layers = perfect_hashtag()
    angles = [0, 45, 90, 135]
    for i, l in enumerate(layers):
        l["rotation"] = angles[i]
    return H(layers)
add("F59: lines at 0/45/90/135 (radial)", case_f59())

def case_f60():
    layers = perfect_hashtag()
    layers[2]["x"] = layers[2]["x"] - 200  # shift so it doesn't cross verticals
    return H(layers)
add("F60: 1 horizontal far left of verticals", case_f60())


# ─── G. Frame variants ─────────────────────────────────────
def case_g61():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_hashtag()
    inner = make_frame(layers, w=900, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_hashtag(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, # in 2nd", case_g63())

def case_g64():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_hashtag()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G67: frame 2000×2000 (huge)", case_g67())

def case_g68():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=200, h=200)  # too small
    return make_log([frame], evt())
add("G68: frame too small (200×200)", case_g68())

def case_g69():
    return H(perfect_hashtag(), in_frame=False)
add("G69: lines on page (no frame)", case_g69())

def case_g70():
    return H(perfect_hashtag(), frame_w=1279, frame_h=831)
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
              make_event("distribute_layers", axis="x")]
    return H(evts=evt(extras=extras))
add("H73: align + distribute used", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 4)
    return H(evts=sem)
add("H74: rectangle tool used (no line tool_change)", case_h74())

def case_h75():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_line")] * 4)
    return H(evts=sem)
add("H75: 0 tool_change events", case_h75())

def case_h76():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: many session_end events", case_h76())

def case_h77():
    extras = [make_event("create_line"), make_event("delete")]  # 1 extra create+delete
    return H(evts=evt(extras=extras))
add("H77: created+deleted extra line", case_h77())

def case_h78():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.extend([make_event("create_line")] * 8)  # too many
    return H(evts=sem)
add("H78: 8 create_line events", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.extend([make_event("create_line")] * 2)  # too few
    return H(evts=sem)
add("H79: 2 create_line events (count too low)", case_h79())

def case_h80():
    extras = [make_event("create_polygon"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H80: created+deleted polygon", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────
def case_i81():
    layers = perfect_hashtag()
    group = {"id":"group_1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: lines in group in frame", case_i81())

def case_i82():
    layers = perfect_hashtag()
    f1 = make_frame(layers[:2], w=600, h=832)
    f2 = make_frame(layers[2:], w=600, h=832)
    return make_log([f1, f2], evt())
add("I82: lines split across 2 frames", case_i82())

def case_i83():
    layers = perfect_hashtag()
    section = {"id":"sec_1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: lines in section (not frame)", case_i83())

def case_i84():
    layers = perfect_hashtag()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    layers = perfect_hashtag()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: # on page 2", case_i85())

def case_i86():
    layers = perfect_hashtag()
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("I86: each line in own frame", case_i86())

def case_i87():
    layers = perfect_hashtag()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only 1 line in frame", case_i87())


# ─── J. Bizarre ────────────────────────────────────────────
def case_j88():
    layers = perfect_hashtag()
    # Replace 1 line with a rectangle
    layers[0] = make_layer("rectangle", x=400, y=200, w=4, h=300, fill=NAVY)
    return H(layers, evts=evt(line=3, extras=[make_event("create_rectangle")]))
add("J88: 1 rect (vertical) + 3 lines", case_j88())

def case_j89():
    layers = perfect_hashtag()
    # 2 thin rectangles (vertical) + 2 lines (horizontal)
    layers[0] = make_layer("rectangle", x=400, y=200, w=4, h=300, fill=NAVY)
    layers[1] = make_layer("rectangle", x=520, y=200, w=4, h=300, fill=NAVY)
    return H(layers, evts=evt(line=2, extras=[make_event("create_rectangle"),
                                               make_event("create_rectangle")]))
add("J89: 2 thin rects + 2 lines (looks like #)", case_j89())

def case_j90():
    return make_log([], [make_event("session_start")])
add("J90: empty document", case_j90())

def case_j91():
    return H([])
add("J91: frame only, no shapes", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "#"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text layer '#'", case_j92())

def case_j93():
    layers = perfect_hashtag()
    # All 4 lines with rotation=0 making them horizontal
    for l in layers:
        l["rotation"] = 0; l["w"] = 300; l["h"] = 4
        l["p1"]={"x":0,"y":0}; l["p2"]={"x":300,"y":0}
    return H(layers)
add("J93: all 4 lines = horizontal at same angle", case_j93())

def case_j94():
    layers = perfect_hashtag()
    # All lines = degenerate (1×1)
    for l in layers:
        l["w"] = 1; l["h"] = 1
        l["p1"]={"x":0,"y":0}; l["p2"]={"x":0,"y":0}
    return H(layers)
add("J94: all lines 1×1 degenerate", case_j94())

def case_j95():
    layers = perfect_hashtag()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J95: all lines mirrored", case_j95())

def case_j96():
    return H(perfect_hashtag())
add("J96: control perfect", case_j96())

def case_j97():
    layers = perfect_hashtag()
    # Rotate all by 30° (whole hashtag tilted)
    for l in layers:
        l["rotation"] = (l["rotation"] + 30) % 180
    return H(layers)
add("J97: hashtag tilted by 30°", case_j97())

def case_j98():
    layers = perfect_hashtag()
    layers.append(make_layer("ellipse", x=400, y=400, w=200, h=200, fill=PINK))
    return H(layers, evts=evt(line=4, extras=[make_event("create_ellipse")]))
add("J98: hashtag + extra ellipse", case_j98())

def case_j99():
    # Just 4 lines but as Bezier vectors
    layers = []
    for i in range(4):
        v = make_layer("vector", x=400+i*50, y=200, w=4, h=300, fill=NAVY)
        v["rotation"] = 0
        layers.append(v)
    return H(layers, evts=evt(line=0, extras=[make_event("create_vector")]*4))
add("J99: 4 vectors instead of lines", case_j99())

def case_j100():
    return H(perfect_hashtag())
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

"""100 edge cases for task 12 (4 same-size rectangles in horizontal row with consistent spacing)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_12" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(rect=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_row(n=4, w=120, h=120, gap=20, y=300, x0=200):
    """4 same-size rectangles in horizontal row, evenly spaced."""
    colors = [PINK, ORANGE, GREEN, BLUE]
    return [L("rectangle", x0+i*(w+gap), y, w, h, colors[i % len(colors)]) for i in range(n)]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_row()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ──────────────────────────────────────────────
def case_a1():  return H(perfect_row(n=5), evts=evt(rect=5))
add("A1: 5 rectangles (extra)", case_a1())

def case_a2():  return H(perfect_row(n=3), evts=evt(rect=3))
add("A2: 3 rectangles (missing)", case_a2())

def case_a3():  return H(perfect_row(n=2), evts=evt(rect=2))
add("A3: 2 rectangles (halved)", case_a3())

def case_a4():  return H(perfect_row(n=8), evts=evt(rect=8))
add("A4: 8 rectangles (doubled)", case_a4())

def case_a5():  return H([], evts=evt(rect=0))
add("A5: 0 rectangles", case_a5())

def case_a6():
    layers = perfect_row()
    layers.append(L("ellipse", 800, 320, 120, 120, BLUE))  # extra ellipse
    return H(layers, evts=evt(rect=4, extras=[make_event("create_ellipse")]))
add("A6: 4 rects + extra ellipse", case_a6())

def case_a7():  return H(perfect_row(n=1), evts=evt(rect=1))
add("A7: 1 rectangle only", case_a7())

def case_a8():
    layers = perfect_row()
    for i, c in enumerate([(0.4,0.4,0.4)]*3):
        layers.append(L("rectangle", 200+i*140, 600, 80, 80, c))
    return H(layers, evts=evt(rect=7))
add("A8: 4 row rects + 3 stray rects", case_a8())

def case_a9():
    return H([L("rectangle", 200, 300, 120, 120, PINK)] * 4, evts=evt(rect=4))
add("A9: 4 identical rects (same id ref) at same spot", case_a9())

def case_a10():
    layers = perfect_row(n=4)
    return H(layers + [L("polygon", 1100, 500, 80, 80, NAVY, sides=3)], evts=evt(rect=4, extras=[make_event("create_polygon")]))
add("A10: 4 rects + extra polygon", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────
def case_b11():
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1.0}
    return H(layers)
add("B11: all same gray (uniform)", case_b11())

def case_b12():
    layers = perfect_row()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B12: all image fill", case_b12())

def case_b13():
    layers = perfect_row()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B13: all gradient fill", case_b13())

def case_b14():
    layers = perfect_row()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("B14: stroke-only (no fill)", case_b14())

def case_b15():
    layers = perfect_row()
    layers[0]["fills"] = []
    return H(layers)
add("B15: 1 rect has empty fills array", case_b15())

def case_b16():
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: all fills alpha=0 (invisible)", case_b16())

def case_b17():
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B17: all fills opacity=0.05", case_b17())

def case_b18():
    layers = perfect_row()
    for l in layers:
        l["fills"][0]["visible"] = False
    return H(layers)
add("B18: all fills visible=False", case_b18())

def case_b19():
    layers = perfect_row()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B19: all layer opacity=0", case_b19())

def case_b20():
    layers = perfect_row()
    for l in layers:
        l["fills"].extend([
            {"kind":"image","src":"x.jpg","fit":"cover","opacity":0.5,"visible":True},
            {"kind":"solid","color":{"r":0,"g":0,"b":0,"a":1},"opacity":0.3,"visible":True}])
    return H(layers)
add("B20: stacked fills (solid + image + solid)", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────
def case_c21():  return H(perfect_row(w=400, h=400, gap=20, x0=50))
add("C21: rects too big (400×400)", case_c21())

def case_c22():  return H(perfect_row(w=8, h=8, gap=5))
add("C22: rects tiny (8×8)", case_c22())

def case_c23():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100+i*(100+15), 300, 80+i*30, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("C23: increasing widths (different sizes)", case_c23())

def case_c24():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100+i*150, 300, 120, 60+i*40, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("C24: increasing heights (different sizes)", case_c24())

def case_c25():
    layers = perfect_row()
    layers[1]["w"] = 240  # one rect twice as wide
    layers[1]["x"] = 320
    return H(layers)
add("C25: 1 rect twice as wide", case_c25())

def case_c26():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*(40+5), 300, 40, 600, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("C26: ultra-thin tall (40×600)", case_c26())

def case_c27():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100+i*(280+15), 300, 280, 30, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("C27: ultra-wide thin (280×30)", case_c27())

def case_c28():
    layers = perfect_row(w=122, h=120)  # +2 in width — within tol=3
    return H(layers)
add("C28: w=122 just inside tolerance", case_c28())

def case_c29():
    layers = perfect_row(w=125, h=120)  # +5 in width — outside tol=3
    return H(layers)
add("C29: w=125 outside tolerance", case_c29())

def case_c30():
    layers = perfect_row()
    layers[0]["w"] = 1; layers[0]["h"] = 1  # 1×1 degenerate
    return H(layers)
add("C30: 1 rect is 1×1 degenerate", case_c30())


# ─── D. Position ────────────────────────────────────────────
def case_d31():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300+i*40, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D31: y staircase (not aligned)", case_d31())

def case_d32():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300+(i*5), 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D32: y drift +5 each (just outside tol=5)", case_d32())

def case_d33():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300+(i*2), 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D33: y drift +2 each (within tol=5)", case_d33())

def case_d34():
    layers = []
    xs = [200, 350, 700, 850]  # uneven spacing
    for i in range(4):
        layers.append(L("rectangle", xs[i], 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D34: uneven horizontal spacing", case_d34())

def case_d35():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200, 300+i*150, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D35: stacked vertically (column)", case_d35())

def case_d36():
    layers = perfect_row()
    for l in layers:
        l["x"] -= 300; l["y"] -= 250  # off-frame top-left
    return H(layers)
add("D36: row off-frame top-left", case_d36())

def case_d37():
    layers = perfect_row()
    for l in layers:
        l["x"] += 1500
    return H(layers)
add("D37: row entirely past right of frame", case_d37())

def case_d38():
    layers = []
    xs = [200, 200, 200, 200]  # all same x
    for i in range(4):
        layers.append(L("rectangle", xs[i], 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("D38: all 4 rects at same x (overlapping pile)", case_d38())

def case_d39():
    layers = []
    # First 2 spaced 20px gap, last 2 spaced 100px gap
    layers.append(L("rectangle", 100, 300, 120, 120, PINK))
    layers.append(L("rectangle", 240, 300, 120, 120, ORANGE))
    layers.append(L("rectangle", 460, 300, 120, 120, GREEN))
    layers.append(L("rectangle", 680, 300, 120, 120, BLUE))
    return H(layers)
add("D39: gaps 20,100,100 (varying spacing)", case_d39())

def case_d40():
    return H(perfect_row())  # control: perfect
add("D40: perfect row (control)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────
def case_e41():
    layers = perfect_row()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1 rect rotated 45°", case_e41())

def case_e42():
    layers = perfect_row()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E42: all rects rotated 45°", case_e42())

def case_e43():
    layers = perfect_row()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E43: 1 rect mirrored (scaleX=-1)", case_e43())

def case_e44():
    layers = perfect_row()
    layers[2]["scaleY"] = -1
    return H(layers)
add("E44: 1 rect flipped Y", case_e44())

def case_e45():
    layers = perfect_row()
    for l in layers:
        l["cornerRadius"] = 200  # rect-as-pill
    return H(layers)
add("E45: cornerRadius=200 (rect = pill)", case_e45())

def case_e46():
    layers = perfect_row()
    for l in layers:
        l["rotation"] = 4  # 4° rotation, near edge
    return H(layers)
add("E46: all rects rotated 4° (under-tol)", case_e46())

def case_e47():
    layers = perfect_row()
    layers[3]["rotation"] = 90
    return H(layers)
add("E47: 1 rect rotated 90°", case_e47())

def case_e48():
    layers = perfect_row()
    layers[2]["rotation"] = 180
    return H(layers)
add("E48: 1 rect rotated 180°", case_e48())

def case_e49():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i],
                        rotation=10*i))
    return H(layers)
add("E49: rotations 0,10,20,30 (varying)", case_e49())

def case_e50():
    layers = perfect_row()
    for l in layers:
        l["cornerRadius"] = 60  # half of 120 = circle
    return H(layers)
add("E50: cornerRadius=60 (circle)", case_e50())


# ─── F. Subcomponent variants ──────────────────────────────
def case_f51():
    layers = perfect_row(gap=0)  # touching
    return H(layers)
add("F51: rects touching (gap=0)", case_f51())

def case_f52():
    layers = perfect_row(gap=-30)  # overlapping
    return H(layers)
add("F52: rects overlapping (gap=-30)", case_f52())

def case_f53():
    layers = perfect_row(gap=200)  # huge gap
    return H(layers)
add("F53: huge gaps (200)", case_f53())

def case_f54():
    layers = perfect_row()
    layers[1]["x"] += 5  # one slightly off
    return H(layers)
add("F54: 1 rect x off by 5", case_f54())

def case_f55():
    layers = perfect_row()
    # First two then big gap
    layers[2]["x"] = 700
    layers[3]["x"] = 850
    return H(layers)
add("F55: 2 close, then 2 far apart", case_f55())

def case_f56():
    layers = perfect_row(w=80, h=200)  # tall rectangles
    return H(layers)
add("F56: tall rects (80×200)", case_f56())

def case_f57():
    layers = perfect_row(w=200, h=80)  # wide rectangles
    return H(layers)
add("F57: wide rects (200×80)", case_f57())

def case_f58():
    layers = perfect_row(w=120, h=120, gap=20, y=500)
    return H(layers)
add("F58: row near bottom (y=500)", case_f58())

def case_f59():
    layers = perfect_row(w=120, h=120, gap=20, y=10)
    return H(layers)
add("F59: row near top (y=10)", case_f59())

def case_f60():
    layers = perfect_row()
    # alternating up/down +/- 3
    for i, l in enumerate(layers):
        l["y"] += (3 if i % 2 else -3)
    return H(layers)
add("F60: alternating ±3 y (within tol=5)", case_f60())


# ─── G. Frame variants ─────────────────────────────────────
def case_g61():
    layers = perfect_row()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    layers = perfect_row()
    inner = make_frame(layers, w=1000, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_row(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, row in 2nd", case_g63())

def case_g64():
    layers = perfect_row()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    layers = perfect_row()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    layers = perfect_row()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_row()
    frame = make_frame(layers, w=2000, h=1500)
    return make_log([frame], evt())
add("G67: frame too big (2000×1500)", case_g67())

def case_g68():
    layers = perfect_row()
    frame = make_frame(layers, w=400, h=200)  # too small to fit
    return make_log([frame], evt())
add("G68: frame too small (400×200)", case_g68())

def case_g69():
    return H(perfect_row(), in_frame=False)  # no frame, on page
add("G69: rects on page (no frame)", case_g69())

def case_g70():
    layers = perfect_row()
    return H(layers, frame_w=1279, frame_h=832)  # within tol
add("G70: frame 1279×832 (within tol)", case_g70())


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
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse"), make_event("create_ellipse"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H74: ellipse tool used (no rectangle tool_change)", case_h74())

def case_h75():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 4)
    return H(evts=sem)
add("H75: 0 tool_change events (keyboard shortcut)", case_h75())

def case_h76():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: many session_end events", case_h76())

def case_h77():
    extras = [make_event("delete") for _ in range(3)]
    return H(evts=evt(extras=extras))
add("H77: 3 delete events", case_h77())

def case_h78():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 8)  # too many creates
    return H(evts=sem)
add("H78: 8 create_rectangle events", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 2)  # too few creates
    return H(evts=sem)
add("H79: 2 create_rectangle events (count too low)", case_h79())

def case_h80():
    extras = [make_event("create_ellipse"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H80: created+deleted an ellipse", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────
def case_i81():
    layers = perfect_row()
    group = {"id":"group_1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: rects in group in frame", case_i81())

def case_i82():
    layers = perfect_row()
    f1 = make_frame(layers[:2], w=600, h=832)
    f2 = make_frame(layers[2:], w=600, h=832)
    return make_log([f1, f2], evt())
add("I82: rects split across 2 frames", case_i82())

def case_i83():
    layers = perfect_row()
    section = {"id":"sec_1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: rects in section (not frame)", case_i83())

def case_i84():
    layers = perfect_row()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    layers = perfect_row()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: row on page 2", case_i85())

def case_i86():
    layers = perfect_row()
    # each in its own frame
    frames = [make_frame([l], w=1280, h=832) for l in layers]
    return make_log(frames, evt())
add("I86: each rect in its own frame", case_i86())

def case_i87():
    layers = perfect_row()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: only first rect in frame", case_i87())


# ─── J. Bizarre ────────────────────────────────────────────
def case_j88():
    layers = perfect_row()
    layers[0] = make_layer("star", x=200, y=300, w=120, h=120, fill=PINK, points=5, innerRatio=0.4)
    return H(layers, evts=evt(rect=3, extras=[make_event("create_star")]))
add("J88: 1 rect → star (3 rects total)", case_j88())

def case_j89():
    layers = perfect_row()
    layers[2] = make_layer("ellipse", x=500, y=300, w=120, h=120, fill=GREEN)
    return H(layers, evts=evt(rect=3, extras=[make_event("create_ellipse")]))
add("J89: 1 rect → ellipse (3 rects total)", case_j89())

def case_j90():
    return make_log([], [make_event("session_start")])
add("J90: empty document", case_j90())

def case_j91():
    return H([])
add("J91: frame only, no shapes", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "rectangles"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text layer 'rectangles'", case_j92())

def case_j93():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 0, 0, 1280, 832, [PINK,ORANGE,GREEN,BLUE][i]))
    return H(layers)
add("J93: 4 rects = full frame size, all stacked", case_j93())

def case_j94():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200+i*150, 300, 120, 120, [PINK,ORANGE,GREEN,BLUE][i],
                        scaleX=-1))
    return H(layers)
add("J94: all rects mirrored", case_j94())

def case_j95():
    layers = perfect_row()
    for l in layers:
        l["y"] -= 1500  # negative y outside frame
    return H(layers)
add("J95: row at negative y", case_j95())

def case_j96():
    return H(perfect_row())
add("J96: control perfect", case_j96())

def case_j97():
    layers = []
    # 4 rects at perfect row, but as polygons sides=4 (visually rectangle)
    for i in range(4):
        layers.append(make_layer("polygon", x=200+i*150, y=300, w=120, h=120,
                                  fill=[PINK,ORANGE,GREEN,BLUE][i], sides=4))
    return H(layers, evts=evt(rect=0, extras=[make_event("create_polygon")]*4))
add("J97: 4 polygons sides=4 (not rectangles)", case_j97())

def case_j98():
    # rows in 2 stacked rows of 2 (instead of 1 row of 4)
    layers = []
    for r in range(2):
        for c in range(2):
            layers.append(L("rectangle", 200+c*150, 200+r*150, 120, 120,
                            [PINK,ORANGE,GREEN,BLUE][r*2+c]))
    return H(layers)
add("J98: 2x2 grid (not row)", case_j98())

def case_j99():
    layers = perfect_row()
    layers[3]["fills"][0]["color"] = layers[2]["fills"][0]["color"]  # 2 same
    return H(layers)
add("J99: rects 3+4 same color (legit)", case_j99())

def case_j100():
    layers = perfect_row()
    return H(layers)
add("J100: control perfect (duplicate)", case_j100())


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

"""100 edge cases for task 48 — spiderweb pattern.

Prompt: Navy frame + 4 white radial lines (90° apart) + 2 concentric stroked hexagons.
"""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_48" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
def evt(n_lines=4, n_hex=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line"),
           make_event("tool_change", before="line", after="polygon")]
    for _ in range(n_lines): sem.append(make_event("create_line"))
    for _ in range(n_hex):   sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_web(cx=400, cy=400, line_w=200, line_color=WHITE,
                hex_color=WHITE, frame_color=NAVY,
                n_lines=4, n_hex=2):
    lines = []
    for i in range(n_lines):
        rotation = i * (360 / max(1, n_lines))
        lines.append(make_layer("line", x=cx, y=cy, w=line_w, h=2, fill=None,
                                strokes=[make_stroke(rgb=line_color, weight=1)],
                                rotation=rotation))
    hexes = []
    for i in range(n_hex):
        sz = 100 + i * 60
        hexes.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=hex_color, weight=1)],
                                sides=6))
    frame = make_frame([*lines, *hexes], w=800, h=800, fill=frame_color)
    return frame


CASES = []
def add(label, log): CASES.append((label, log))


def H(frame=None, evts=None):
    if frame is None: frame = perfect_web()
    return make_log([frame], evts or evt())


# ─── A. Counts (10) ─────────────────────────────────────────────────
def case_a1():
    return H(perfect_web(n_lines=3))
add("A1: 3 lines (missing)", case_a1())

def case_a2():
    return H(perfect_web(n_lines=5))
add("A2: 5 lines (extra)", case_a2())

def case_a3():
    return H(perfect_web(n_hex=1))
add("A3: 1 hexagon", case_a3())

def case_a4():
    return H(perfect_web(n_hex=3))
add("A4: 3 hexagons", case_a4())

def case_a5():
    return H(perfect_web(n_lines=0, n_hex=2))
add("A5: no lines, 2 hexagons", case_a5())

def case_a6():
    return H(perfect_web(n_lines=4, n_hex=0))
add("A6: 4 lines, no hexagons", case_a6())

def case_a7():
    f = perfect_web(n_lines=8)
    return H(f)
add("A7: 8 lines (radial extras)", case_a7())

def case_a8():
    f = perfect_web(n_lines=4, n_hex=4)
    return H(f)
add("A8: 4 hexagons (extra)", case_a8())

def case_a9():
    f = perfect_web()
    f["children"].append(make_layer("ellipse", 350, 350, 100, 100, WHITE,
                                    strokes=[make_stroke(rgb=WHITE, weight=1)]))
    return H(f)
add("A9: extra decorative ellipse", case_a9())

def case_a10():
    return H()
add("A10: perfect (control)", case_a10())


# ─── B. Colors / fills (10) ─────────────────────────────────────────
def case_b11():
    f = perfect_web(frame_color=WHITE)  # white frame, not navy
    return H(f)
add("B11: white frame (wrong color)", case_b11())

def case_b12():
    f = perfect_web(frame_color=BLACK)
    return H(f)
add("B12: black frame", case_b12())

def case_b13():
    f = perfect_web(line_color=NAVY)  # lines navy, invisible against navy frame
    return H(f)
add("B13: lines navy (invisible against frame)", case_b13())

def case_b14():
    f = perfect_web(hex_color=NAVY)
    return H(f)
add("B14: hexagons navy strokes", case_b14())

def case_b15():
    f = perfect_web()
    # set polygon fills to solid navy (not no-fill)
    for c in f["children"]:
        if c["type"] == "polygon":
            c["fills"] = [{"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1},
                          "opacity": 1.0, "visible": True}]
    return H(f)
add("B15: hexagons have solid fill (not no-fill)", case_b15())

def case_b16():
    f = perfect_web()
    f["fills"] = []  # no frame fill
    return H(f)
add("B16: frame has empty fills", case_b16())

def case_b17():
    f = perfect_web()
    f["fills"] = [{"kind": "image", "src": "navy.jpg", "fit": "cover",
                  "opacity": 1.0, "visible": True}]
    return H(f)
add("B17: frame has image fill (not solid)", case_b17())

def case_b18():
    f = perfect_web()
    f["fills"][0]["opacity"] = 0.1  # frame transparent
    return H(f)
add("B18: frame fill opacity=0.1", case_b18())

def case_b19():
    f = perfect_web()
    f["fills"][0]["color"]["a"] = 0.0  # frame alpha=0
    return H(f)
add("B19: frame alpha=0", case_b19())

def case_b20():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"][0]["paint"]["color"] = {"r": 0.6, "g": 0.6, "b": 0.6, "a": 1}
    return H(f)
add("B20: lines mid-gray (not white)", case_b20())


# ─── C. Sizing (10) ─────────────────────────────────────────────────
def case_c21():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["w"] = 5  # super short lines
    return H(f)
add("C21: lines 5px short", case_c21())

def case_c22():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["w"] = 2000  # huge lines
    return H(f)
add("C22: lines 2000px", case_c22())

def case_c23():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["w"] = 5; c["h"] = 5
    return H(f)
add("C23: polygons 5×5 tiny", case_c23())

def case_c24():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["w"] = 800; c["h"] = 800
    return H(f)
add("C24: polygons same size as frame", case_c24())

def case_c25():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["w"] = 600; c["h"] = 100
    return H(f)
add("C25: polygons 600×100 squashed", case_c25())

def case_c26():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if len(polys) >= 2:
        polys[0]["w"] = polys[0]["h"] = 100
        polys[1]["w"] = polys[1]["h"] = 105  # nearly identical sizes
    return H(f)
add("C26: hexagons nearly identical sizes", case_c26())

def case_c27():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["h"] = 100  # thick lines (not lines)
    return H(f)
add("C27: lines 100px thick", case_c27())

def case_c28():
    f = perfect_web()
    f["w"] = 50; f["h"] = 50  # tiny frame
    return H(f)
add("C28: frame 50×50 tiny", case_c28())

def case_c29():
    f = perfect_web()
    f["w"] = 5000; f["h"] = 5000
    return H(f)
add("C29: frame 5000×5000 huge", case_c29())

def case_c30():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["w"] = 1; c["h"] = 1
    return H(f)
add("C30: polygons 1×1 degenerate", case_c30())


# ─── D. Position (10) ───────────────────────────────────────────────
def case_d31():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if len(polys) >= 2:
        polys[1]["x"] += 200  # 2nd hex offset from concentric
    return H(f)
add("D31: hexagons not concentric", case_d31())

def case_d32():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["x"] += 100
    return H(f)
add("D32: lines shifted +100 (off-center)", case_d32())

def case_d33():
    f = perfect_web()
    for c in f["children"]: c["x"] += 1000  # all way off-frame
    return H(f)
add("D33: all children shifted +1000", case_d33())

def case_d34():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if len(polys) >= 2:
        polys[0]["x"] = 100; polys[0]["y"] = 100  # corner
        polys[1]["x"] = 600; polys[1]["y"] = 600  # opposite corner
    return H(f)
add("D34: hexagons in opposite corners", case_d34())

def case_d35():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["x"] = 100 + i * 50
        l["y"] = 100 + i * 50
    return H(f)
add("D35: lines in row, not radiating", case_d35())

def case_d36():
    f = perfect_web()
    for c in f["children"]: c["y"] -= 800  # all above frame
    return H(f)
add("D36: all children above frame", case_d36())

def case_d37():
    return H(perfect_web(cx=100, cy=100))
add("D37: web origin at (100,100)", case_d37())

def case_d38():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if len(polys) >= 2:
        polys[1]["x"] = polys[0]["x"] + 5  # 5px off concentric
    return H(f)
add("D38: hexagons 5px off concentric (within tol)", case_d38())

def case_d39():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if len(polys) >= 2:
        polys[1]["x"] = polys[0]["x"] + 50  # 50px off concentric (out)
    return H(f)
add("D39: hexagons 50px off concentric", case_d39())

def case_d40():
    f = perfect_web()
    for c in f["children"]: c["x"] = 0; c["y"] = 0  # all piled at origin
    return H(f)
add("D40: all children at (0,0) piled", case_d40())


# ─── E. Per-shape variants (10) ─────────────────────────────────────
def case_e41():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["sides"] = 5  # pentagons
    return H(f)
add("E41: hexagons → 5 sides", case_e41())

def case_e42():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["sides"] = 8
    return H(f)
add("E42: hexagons → 8 sides (octagon)", case_e42())

def case_e43():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["sides"] = 3  # triangles
    return H(f)
add("E43: hexagons → 3 sides (triangle)", case_e43())

def case_e44():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for l in lines:
        l["rotation"] = 0  # all at 0° (not radial)
    return H(f)
add("E44: lines all at 0° (not radial)", case_e44())

def case_e45():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["rotation"] = i * 45  # 45° spacing not 90°
    return H(f)
add("E45: lines 45° apart (not 90°)", case_e45())

def case_e46():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for i, l in enumerate(lines):
        l["rotation"] = i * 91  # nearly 90° but off
    return H(f)
add("E46: lines 91° apart", case_e46())

def case_e47():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    for p in polys:
        p["rotation"] = 30  # rotated hexagons
    return H(f)
add("E47: hexagons rotated 30°", case_e47())

def case_e48():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for l in lines:
        l["scaleX"] = -1  # flipped
    return H(f)
add("E48: lines scaleX=-1", case_e48())

def case_e49():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    for p in polys:
        p["scaleX"] = -1
    return H(f)
add("E49: polygons scaleX=-1", case_e49())

def case_e50():
    f = perfect_web()
    lines = [c for c in f["children"] if c["type"] == "line"]
    for l in lines:
        l["rotation"] = 45  # all rotated 45° same
    return H(f)
add("E50: all lines rotated 45° (same)", case_e50())


# ─── F. Stroke variants (10) ────────────────────────────────────────
def case_f51():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["strokes"] = []  # no stroke on lines
    return H(f)
add("F51: lines have no stroke", case_f51())

def case_f52():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon": c["strokes"] = []
    return H(f)
add("F52: polygons have no stroke", case_f52())

def case_f53():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line": c["strokes"][0]["weight"] = 30
    return H(f)
add("F53: lines stroke 30px (very thick)", case_f53())

def case_f54():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon":
            c["strokes"][0]["paint"]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1}
    return H(f)
add("F54: polygons gray strokes", case_f54())

def case_f55():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "polygon":
            c["strokes"][0]["dash"] = {"dash": 6, "gap": 3}  # dashed
    return H(f)
add("F55: hexagons dashed strokes", case_f55())

def case_f56():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"][0]["alignment"] = "outside"
    return H(f)
add("F56: lines stroke alignment outside", case_f56())

def case_f57():
    f = perfect_web()
    # multiple strokes on lines
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"].append(make_stroke(rgb=BLACK, weight=2))
    return H(f)
add("F57: lines have 2 strokes (overlay)", case_f57())

def case_f58():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"][0]["visible"] = False  # invisible stroke
    return H(f)
add("F58: lines stroke visible=False", case_f58())

def case_f59():
    f = perfect_web()
    for c in f["children"]:
        if c["type"] == "line":
            c["strokes"][0]["weight"] = 0
    return H(f)
add("F59: lines stroke weight 0", case_f59())

def case_f60():
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    if polys:
        polys[0]["strokes"] = []  # only first polygon no stroke
    return H(f)
add("F60: 1 of 2 polygons has no stroke", case_f60())


# ─── G. Frame variants (10) ─────────────────────────────────────────
def case_g61():
    f = perfect_web()
    f["rotation"] = 30
    return H(f)
add("G61: frame rotated 30°", case_g61())

def case_g62():
    f = perfect_web()
    inner = make_frame(f["children"], w=800, h=800, fill=NAVY)
    outer = make_frame([inner], w=1280, h=832, fill=BLACK)
    return make_log([outer], evt())
add("G62: nested navy frame inside frame", case_g62())

def case_g63():
    f1 = make_frame([], w=800, h=800, fill=NAVY)
    f2 = perfect_web()
    return make_log([f1, f2], evt())
add("G63: 2 frames, web in 2nd", case_g63())

def case_g64():
    f = perfect_web()
    f["scaleX"] = -1
    return H(f)
add("G64: frame scaleX=-1", case_g64())

def case_g65():
    f = perfect_web()
    f["x"] = 500; f["y"] = 300
    return H(f)
add("G65: frame translated", case_g65())

def case_g66():
    f = perfect_web()
    f["fills"][0]["color"]["a"] = 0.5
    return H(f)
add("G66: frame fill alpha=0.5", case_g66())

def case_g67():
    f = perfect_web()
    f["strokes"] = [make_stroke(rgb=WHITE, weight=2)]
    return H(f)
add("G67: frame has white stroke too", case_g67())

def case_g68():
    f = perfect_web()
    f["effects"] = [make_drop_shadow(blur=12, alpha=0.4)]
    return H(f)
add("G68: frame has drop shadow", case_g68())

def case_g69():
    return H()  # control
add("G69: perfect (control)", case_g69())

def case_g70():
    f = perfect_web()
    f["w"] = 100; f["h"] = 100  # tiny frame
    return H(f)
add("G70: frame 100×100 tiny", case_g70())


# ─── H. Tools / events (10) ─────────────────────────────────────────
def case_h71():
    extras = [make_event("undo") for _ in range(30)]
    return H(evts=evt(extras=extras))
add("H71: 30 undo events", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.append(make_event("create_line"))  # 1 line only
    sem.append(make_event("create_polygon"))  # but no polygon tool change
    return H(evts=sem)
add("H72: only 1 create_line event", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(4): sem.append(make_event("create_line"))
    sem.append(make_event("create_polygon"))
    sem.append(make_event("create_polygon"))
    return H(evts=sem)
add("H73: rectangle tool used (no line tool)", case_h73())

def case_h74():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H74: 20 delete events", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")] * 5))
add("H75: 5 align events", case_h75())

def case_h76():
    sem = [make_event("session_start")]
    # only 2 lines
    sem.append(make_event("create_line"))
    sem.append(make_event("create_line"))
    sem.append(make_event("create_polygon"))
    sem.append(make_event("create_polygon"))
    return H(evts=sem)
add("H76: 0 tool_change events", case_h76())

def case_h77():
    return H(evts=evt(n_lines=10))
add("H77: 10 create_line events but only 4 lines", case_h77())

def case_h78():
    extras = [make_event("rotate") for _ in range(8)]
    return H(evts=evt(extras=extras))
add("H78: 8 rotate events", case_h78())

def case_h79():
    extras = [make_event("duplicate") for _ in range(5)]
    return H(evts=evt(extras=extras))
add("H79: 5 duplicate events (web making)", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("session_end")]))
add("H80: session_end included", case_h80())


# ─── I. Hierarchy (10) ──────────────────────────────────────────────
def case_i81():
    f = perfect_web()
    grp = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
           "fills": [], "strokes": [], "effects": [], "children": f["children"]}
    f["children"] = [grp]
    return H(f)
add("I81: web contents in a group", case_i81())

def case_i82():
    # No frame at all — lines and polygons on page
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    return make_log([*lines, *polys], evt())
add("I82: no frame, web on page", case_i82())

def case_i83():
    f = perfect_web()
    sec = {"id": "sec1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
           "fills": [], "children": [f]}
    return make_log([sec], evt())
add("I83: web frame in section", case_i83())

def case_i84():
    f3 = perfect_web()
    f2 = make_frame([f3], w=1000, h=1000)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I84: web in 3-deep frame nest", case_i84())

def case_i85():
    f = perfect_web()
    p1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    p2 = {"id": "p2", "children": [f], "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I85: web on page 2", case_i85())

def case_i86():
    f = perfect_web()
    component = {"id": "comp1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "children": [f]}
    return make_log([component], evt())
add("I86: web frame in component", case_i86())

def case_i87():
    # Lines in one frame, polygons in another
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    f1 = make_frame(lines, w=800, h=800, fill=NAVY)
    f2 = make_frame(polys, w=800, h=800, fill=NAVY)
    return make_log([f1, f2], evt())
add("I87: lines and polys in different frames", case_i87())

def case_i88():
    # Lines in frame, polygons on page outside frame
    f = perfect_web()
    polys = [c for c in f["children"] if c["type"] == "polygon"]
    f["children"] = [c for c in f["children"] if c["type"] != "polygon"]
    return make_log([f, *polys], evt())
add("I88: polygons outside frame", case_i88())

def case_i89():
    return H()
add("I89: web in frame (canonical)", case_i89())

def case_i90():
    f = perfect_web()
    grp_lines = {"id": "g_lines", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                 "fills": [], "children": [c for c in f["children"] if c["type"] == "line"]}
    grp_polys = {"id": "g_polys", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                 "fills": [], "children": [c for c in f["children"] if c["type"] == "polygon"]}
    f["children"] = [grp_lines, grp_polys]
    return H(f)
add("I90: lines and polys in separate groups", case_i90())


# ─── J. Bizarre (10) ────────────────────────────────────────────────
def case_j91():
    f = perfect_web()
    for c in f["children"]: c["rotation"] = 180
    return H(f)
add("J91: all children rotated 180°", case_j91())

def case_j92():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=WHITE)
    text["content"] = "spiderweb"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J92: text 'spiderweb'", case_j92())

def case_j93():
    f = perfect_web()
    for c in f["children"]:
        c["w"] = 1; c["h"] = 1
    return H(f)
add("J93: all children 1×1", case_j93())

def case_j94():
    f = perfect_web(line_color=NAVY, hex_color=NAVY)  # all stroke colors navy = invisible
    return H(f)
add("J94: all strokes navy (invisible vs frame)", case_j94())

def case_j95():
    f = perfect_web()
    for c in f["children"]:
        c["x"] -= 1000; c["y"] -= 1000
    return H(f)
add("J95: all children at negative coords", case_j95())

def case_j96():
    # 4 Lines all stacked on top of each other (same rotation, same x/y)
    cx, cy = 400, 400
    lines = []
    for _ in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=0))  # ALL same rotation
    polys = []
    for i in range(2):
        sz = 100 + i * 60
        polys.append(make_layer("polygon", x=cx-sz/2, y=cy-sz/2, w=sz, h=sz,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))
    f = make_frame([*lines, *polys], w=800, h=800, fill=NAVY)
    return make_log([f], evt())
add("J96: 4 lines all rotation 0 (degenerate radial)", case_j96())

def case_j97():
    # 2 hexagons piled at exact same place (overlapping)
    cx, cy = 400, 400
    lines = []
    for i in range(4):
        lines.append(make_layer("line", x=cx, y=cy, w=200, h=2, fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                rotation=i * 90))
    polys = []
    for i in range(2):
        polys.append(make_layer("polygon", x=300, y=300, w=200, h=200,
                                fill=None,
                                strokes=[make_stroke(rgb=WHITE, weight=1)],
                                sides=6))  # both same size
    f = make_frame([*lines, *polys], w=800, h=800, fill=NAVY)
    return make_log([f], evt())
add("J97: 2 hexagons identical (no concentric variety)", case_j97())

def case_j98():
    # All children visible=False
    f = perfect_web()
    for c in f["children"]:
        c["visible"] = False
    return H(f)
add("J98: all children visible=False", case_j98())

def case_j99():
    # Way more lines (128) and only 1 hex
    f = perfect_web(n_lines=128, n_hex=1)
    return H(f, evts=evt(n_lines=128, n_hex=1))
add("J99: 128 lines, 1 hex", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " ⚠ FP" if score >= 0.95 else ""
        if score >= 0.95: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\n{fp_count} cases scored ≥ 0.95")

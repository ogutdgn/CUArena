"""100 edge cases for task 36 (vintage frame) — runs all and prints a sorted score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_36" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
LIGHT_GRAY = (0.85, 0.85, 0.85)


def evt(rectangle=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rectangle): sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_polaroid(rotation=5, color=WHITE, has_shadow=True):
    """Outer rect + smaller inner rect, both centered, with drop shadow."""
    effects = [make_drop_shadow(y=8, blur=12)] if has_shadow else []
    # outer center = (550, 570), inner center = (550, 570) → concentric
    outer = L("rectangle", 400, 400, 300, 340, color, rotation=rotation, effects=effects)
    inner = L("rectangle", 420, 440, 260, 260, LIGHT_GRAY, rotation=rotation)
    return [outer, inner]


CASES = []


def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None):
    if layers is None: layers = perfect_polaroid()
    return make_log(layers, evts or evt())


# ── A. Counts ───────────────────────────────────────────────────────
def case_a1():
    layers = perfect_polaroid()
    layers.append(L("rectangle", 350, 350, 100, 100, RED))
    return H(layers, evts=evt(rectangle=3))
add("A1: 3 rectangles", case_a1())


def case_a2():
    layers = perfect_polaroid()[:1]
    return H(layers, evts=evt(rectangle=1))
add("A2: 1 rectangle", case_a2())


def case_a3():
    return H([], evts=evt(rectangle=0))
add("A3: 0 rectangles", case_a3())


def case_a4():
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100 + i * 60, 100, 50, 50, WHITE,
                        effects=[make_drop_shadow()]))
    return H(layers, evts=evt(rectangle=4))
add("A4: 4 rectangles", case_a4())


def case_a5():
    layers = perfect_polaroid()
    layers.append(L("ellipse", 300, 300, 50, 50, RED))
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]))
add("A5: 2 rect + 1 ellipse", case_a5())


def case_a6():
    layers = perfect_polaroid()
    layers.extend([L("rectangle", 50 + i * 60, 50, 50, 50, GREEN,
                     effects=[make_drop_shadow()]) for i in range(3)])
    return H(layers, evts=evt(rectangle=5))
add("A6: 5 rectangles", case_a6())


def case_a7():
    """Just 2 unrelated rectangles."""
    layers = [L("rectangle", 50, 50, 100, 100, RED, effects=[make_drop_shadow()]),
              L("rectangle", 700, 700, 100, 100, BLUE, effects=[make_drop_shadow()])]
    return H(layers)
add("A7: 2 rects, no inner-outer relation", case_a7())


def case_a8():
    """Inner inside outer, no shadow."""
    return H(perfect_polaroid(has_shadow=False))
add("A8: no drop shadow", case_a8())


def case_a9():
    layers = perfect_polaroid()
    layers.append(L("rectangle", 0, 0, 100, 100, ORANGE,
                    effects=[make_drop_shadow()]))
    return H(layers, evts=evt(rectangle=3))
add("A9: 3rd rect outside", case_a9())


def case_a10():
    layers = perfect_polaroid() * 2  # 4 rectangles total
    return H(layers, evts=evt(rectangle=4))
add("A10: 4 rectangles (2x perfect)", case_a10())


# ── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    layers = perfect_polaroid(color=BLACK)
    return H(layers)
add("B11: outer BLACK (not white)", case_b11())


def case_b12():
    layers = perfect_polaroid(color=GRAY)
    return H(layers)
add("B12: outer GRAY", case_b12())


def case_b13():
    layers = perfect_polaroid()
    layers[0]["fills"] = [{"kind": "image", "src": "frame.jpg", "fit": "cover",
                           "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: outer image fill", case_b13())


def case_b14():
    layers = perfect_polaroid()
    layers[0]["fills"] = []
    return H(layers)
add("B14: outer no fill", case_b14())


def case_b15():
    layers = perfect_polaroid()
    layers[0]["fills"] = []
    layers[1]["fills"] = []
    return H(layers)
add("B15: both no fill", case_b15())


def case_b16():
    layers = perfect_polaroid(color=WHITE)
    layers[1]["fills"][0]["color"] = {"r": 1, "g": 1, "b": 1, "a": 1}
    return H(layers)
add("B16: both white (no contrast)", case_b16())


def case_b17():
    NEAR_WHITE = (0.95, 0.95, 0.95)
    layers = perfect_polaroid(color=NEAR_WHITE)
    return H(layers)
add("B17: near-white outer (within tol)", case_b17())


def case_b18():
    layers = perfect_polaroid()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 1, "b": 1, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0, "b": 0, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B18: outer gradient fill", case_b18())


def case_b19():
    layers = perfect_polaroid()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: outer fill opacity 0.1", case_b19())


def case_b20():
    layers = perfect_polaroid()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True}])
    return H(layers)
add("B20: outer 3 stacked fills", case_b20())


# ── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """Outer huge."""
    layers = perfect_polaroid()
    layers[0]["w"] = 1500
    layers[0]["h"] = 1500
    return H(layers)
add("C21: outer 1500×1500", case_c21())


def case_c22():
    """Outer tiny."""
    layers = perfect_polaroid()
    layers[0]["w"] = 50
    layers[0]["h"] = 50
    return H(layers)
add("C22: outer 50×50", case_c22())


def case_c23():
    """Inner huge (bigger than outer)."""
    layers = perfect_polaroid()
    layers[1]["w"] = 600
    layers[1]["h"] = 600
    return H(layers)
add("C23: inner bigger than outer", case_c23())


def case_c24():
    """Both rectangles same size."""
    layers = perfect_polaroid()
    layers[1]["w"] = 300
    layers[1]["h"] = 340
    return H(layers)
add("C24: both rectangles same size", case_c24())


def case_c25():
    """Outer 1×1 degenerate."""
    layers = perfect_polaroid()
    layers[0]["w"] = 1
    layers[0]["h"] = 1
    return H(layers)
add("C25: outer 1×1", case_c25())


def case_c26():
    """Outer thin tall (10×1000)."""
    layers = perfect_polaroid()
    layers[0]["w"] = 10
    layers[0]["h"] = 1000
    return H(layers)
add("C26: outer 10×1000", case_c26())


def case_c27():
    """Inner same size as outer."""
    layers = perfect_polaroid()
    layers[1] = L("rectangle", 400, 400, 300, 340, LIGHT_GRAY, rotation=5)
    return H(layers)
add("C27: inner = outer dimensions", case_c27())


def case_c28():
    """Outer 0×0."""
    layers = perfect_polaroid()
    layers[0]["w"] = 0
    layers[0]["h"] = 0
    return H(layers)
add("C28: outer 0×0", case_c28())


def case_c29():
    """Both 1×1."""
    layers = perfect_polaroid()
    for l in layers:
        l["w"] = 1
        l["h"] = 1
    return H(layers)
add("C29: both 1×1", case_c29())


def case_c30():
    """Inner just 5px smaller than outer."""
    layers = perfect_polaroid()
    layers[1]["w"] = 295
    layers[1]["h"] = 335
    return H(layers)
add("C30: inner 5px smaller (within tol)", case_c30())


# ── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Inner outside outer (separate)."""
    layers = perfect_polaroid()
    layers[1]["x"] = 0
    layers[1]["y"] = 0
    return H(layers)
add("D31: inner at (0,0), outside outer", case_d31())


def case_d32():
    """Inner half-outside outer."""
    layers = perfect_polaroid()
    layers[1]["x"] = 700
    layers[1]["y"] = 700
    return H(layers)
add("D32: inner half-outside outer", case_d32())


def case_d33():
    """Both at same position."""
    layers = perfect_polaroid()
    layers[1]["x"] = 400
    layers[1]["y"] = 400
    return H(layers)
add("D33: inner at outer's corner", case_d33())


def case_d34():
    """Inner offset from outer center."""
    layers = perfect_polaroid()
    layers[1]["x"] = 410
    layers[1]["y"] = 410
    return H(layers)
add("D34: inner top-left of outer", case_d34())


def case_d35():
    """Both at top-left of canvas."""
    layers = perfect_polaroid()
    for l in layers:
        l["x"] -= 400
        l["y"] -= 400
    return H(layers)
add("D35: both at canvas top-left", case_d35())


def case_d36(): return H()
add("D36: control polaroid", case_d36())


def case_d37():
    """Inner negative coords."""
    layers = perfect_polaroid()
    layers[1]["x"] = -200
    layers[1]["y"] = -200
    return H(layers)
add("D37: inner negative coords", case_d37())


def case_d38():
    """Both at extreme positive coords."""
    layers = perfect_polaroid()
    for l in layers:
        l["x"] = 5000
        l["y"] = 5000
    return H(layers)
add("D38: both at extreme coords", case_d38())


def case_d39():
    """Outer at top, inner at bottom (separated)."""
    layers = perfect_polaroid()
    layers[0]["y"] = 0
    layers[1]["y"] = 1000
    return H(layers)
add("D39: rectangles separated vertically", case_d39())


def case_d40():
    """Outer flipped scaleX=-1."""
    layers = perfect_polaroid()
    layers[0]["scaleX"] = -1
    return H(layers)
add("D40: outer mirrored", case_d40())


# ── E. Per-shape variants ───────────────────────────────────────────
def case_e41():
    """Outer rotated 45° (way more than 5±3)."""
    layers = perfect_polaroid(rotation=45)
    return H(layers)
add("E41: outer rotated 45°", case_e41())


def case_e42():
    """Outer rotated 90°."""
    layers = perfect_polaroid(rotation=90)
    return H(layers)
add("E42: outer rotated 90°", case_e42())


def case_e43():
    """Outer rotated -10° (negative, outside tol)."""
    layers = perfect_polaroid(rotation=-10)
    return H(layers)
add("E43: outer rotation -10°", case_e43())


def case_e44():
    """Outer rotated 0° (no tilt - within tol of 5±3?)."""
    layers = perfect_polaroid(rotation=0)
    return H(layers)
add("E44: outer rotation 0° (no tilt)", case_e44())


def case_e45():
    """Outer with cornerRadius."""
    layers = perfect_polaroid()
    layers[0]["cornerRadius"] = 50
    return H(layers)
add("E45: outer with cornerRadius 50", case_e45())


def case_e46():
    """Inner with cornerRadius (high)."""
    layers = perfect_polaroid()
    layers[1]["cornerRadius"] = 100
    return H(layers)
add("E46: inner with cornerRadius 100", case_e46())


def case_e47():
    """Outer is ellipse (not rectangle)."""
    layers = perfect_polaroid()
    layers[0] = L("ellipse", 400, 400, 300, 340, WHITE,
                   rotation=5, effects=[make_drop_shadow(y=8, blur=12)])
    return H(layers, evts=evt(rectangle=1, extras=[make_event("create_ellipse")]))
add("E47: outer is ellipse", case_e47())


def case_e48():
    """Inner is polygon."""
    layers = perfect_polaroid()
    layers[1] = L("polygon", 420, 420, 260, 260, LIGHT_GRAY, sides=4, rotation=5)
    return H(layers, evts=evt(rectangle=1, extras=[make_event("create_polygon")]))
add("E48: inner is polygon", case_e48())


def case_e49():
    """Outer mirrored."""
    layers = perfect_polaroid()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E49: outer mirrored", case_e49())


def case_e50():
    """Both mirrored."""
    layers = perfect_polaroid()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E50: both mirrored", case_e50())


# ── F. Subcomponent variants ────────────────────────────────────────
def case_f51():
    """No drop shadow."""
    return H(perfect_polaroid(has_shadow=False))
add("F51: no drop shadow", case_f51())


def case_f52():
    """Drop shadow on inner instead of outer."""
    layers = perfect_polaroid(has_shadow=False)
    layers[1]["effects"] = [make_drop_shadow(y=8, blur=12)]
    return H(layers)
add("F52: shadow on inner only", case_f52())


def case_f53():
    """Outer fill alpha=0 (invisible)."""
    layers = perfect_polaroid()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("F53: outer fill alpha=0", case_f53())


def case_f54():
    """Outer opacity=0.1."""
    layers = perfect_polaroid()
    layers[0]["opacity"] = 0.1
    return H(layers)
add("F54: outer layer opacity 0.1", case_f54())


def case_f55():
    """Inner outside drawn first, outer second."""
    layers = perfect_polaroid()
    return H(layers[::-1])  # reverse order
add("F55: inner drawn after outer", case_f55())


def case_f56():
    """Inner same color as outer."""
    layers = perfect_polaroid()
    layers[1]["fills"][0]["color"] = {"r": 1, "g": 1, "b": 1, "a": 1}
    return H(layers)
add("F56: inner color = outer (white)", case_f56())


def case_f57():
    """Outer with stroke instead of fill."""
    layers = perfect_polaroid()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("F57: outer stroke only", case_f57())


def case_f58():
    """Both rectangles overlap fully (same position)."""
    layers = perfect_polaroid()
    layers[1]["x"] = 400
    layers[1]["y"] = 400
    layers[1]["w"] = 300
    layers[1]["h"] = 340
    return H(layers)
add("F58: both rectangles identical", case_f58())


def case_f59():
    """Inner rotated differently from outer."""
    layers = perfect_polaroid()
    layers[1]["rotation"] = 45
    return H(layers)
add("F59: inner rotated 45° (outer 5°)", case_f59())


def case_f60():
    """Multiple drop shadows on outer."""
    layers = perfect_polaroid()
    layers[0]["effects"] = [
        make_drop_shadow(y=8, blur=12),
        make_drop_shadow(y=-8, blur=12),
        make_drop_shadow(x=12, blur=20),
    ]
    return H(layers)
add("F60: 3 drop shadows on outer", case_f60())


# ── G. Frame variants ───────────────────────────────────────────────
def case_g61():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("G61: polaroid in frame", case_g61())


def case_g62():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G62: frame rotated", case_g62())


def case_g63():
    layers = perfect_polaroid()
    f1 = make_frame([layers[0]], w=1280, h=832)
    f2 = make_frame([layers[1]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames split", case_g63())


def case_g64():
    layers = perfect_polaroid()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G64: nested frames", case_g64())


def case_g65():
    return H()  # no frame
add("G65: no frame (page)", case_g65())


def case_g66():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return make_log([frame], evt())
add("G66: frame image fill", case_g66())


def case_g67():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return make_log([frame], evt())
add("G67: frame with stroke", case_g67())


def case_g68():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_polaroid(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G68: 2 frames, polaroid in 2nd", case_g68())


def case_g69():
    layers = perfect_polaroid()
    frame = make_frame(layers, x=300, y=200, w=1280, h=832)
    return make_log([frame], evt())
add("G69: frame translated", case_g69())


def case_g70():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G70: frame too small", case_g70())


# ── H. Tools / events ───────────────────────────────────────────────
def case_h71(): return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())


def case_h72(): return H(evts=evt(extras=[make_event("undo") for _ in range(40)]))
add("H72: 40 undo events", case_h72())


def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_rectangle")] * 2)
    return H(evts=sem)
add("H73: ellipse tool used (wrong)", case_h73())


def case_h74():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 2)
    return H(evts=sem)
add("H74: 0 tool_change", case_h74())


def case_h75():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted star", case_h75())


def case_h76(): return H(evts=evt(rectangle=8))
add("H76: 8 create_rectangle events", case_h76())


def case_h77():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H77: many session_end events", case_h77())


def case_h78(): return H(evts=evt(rectangle=0))
add("H78: 0 create events", case_h78())


def case_h79(): return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: used align tool", case_h79())


def case_h80(): return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: used distribute tool", case_h80())


# ── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_polaroid()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("I81: polaroid in group", case_i81())


def case_i82():
    layers = perfect_polaroid()
    f1 = make_frame([layers[0]], w=1280, h=832)
    f2 = make_frame([layers[1]], w=1280, h=832)
    return make_log([f1, f2], evt())
add("I82: rects split frames", case_i82())


def case_i83():
    layers = perfect_polaroid()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: polaroid in section", case_i83())


def case_i84():
    layers = perfect_polaroid()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, layers[1]], evt())
add("I84: 1 in frame, 1 on page", case_i84())


def case_i85():
    layers = perfect_polaroid()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    layers = perfect_polaroid()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: polaroid in component", case_i86())


def case_i87():
    layers = perfect_polaroid()
    page1 = {"id": "p1", "children": [],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    page2 = {"id": "p2", "children": layers,
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I87: polaroid on page 2", case_i87())


def case_i88():
    layers = perfect_polaroid()
    frames = [make_frame([s], w=1280, h=832) for s in layers]
    return make_log(frames, evt())
add("I88: each rect in own frame", case_i88())


def case_i89():
    layers = perfect_polaroid()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g]}
    return make_log([g2], evt())
add("I89: polaroid deep in groups", case_i89())


def case_i90():
    layers = perfect_polaroid()
    frame = make_frame(layers, w=1280, h=832)
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": [frame]}
    return make_log([g], evt())
add("I90: frame in group", case_i90())


# ── J. Bizarre ──────────────────────────────────────────────────────
def case_j91(): return H([])
add("J91: empty", case_j91())


def case_j92():
    layers = perfect_polaroid()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J92: 0×0 rectangles", case_j92())


def case_j93():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=BLACK)
    text["content"] = "polaroid"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J93: text 'polaroid'", case_j93())


def case_j94():
    """2 stars instead of rectangles."""
    layers = []
    for i in range(2):
        layers.append(make_layer("star", x=400, y=400, w=300, h=300,
                                  fill=WHITE, points=5, innerRatio=0.4,
                                  effects=[make_drop_shadow()]))
    return H(layers, evts=evt(rectangle=0))
add("J94: stars instead of rectangles", case_j94())


def case_j95():
    """Both rectangles same exact rectangle."""
    layers = perfect_polaroid()
    layers[1] = layers[0].copy()
    layers[1]["id"] = "rect_b"
    return H(layers)
add("J95: 2 identical overlapping rects", case_j95())


def case_j96():
    """Outer flipped, inner mirrored."""
    layers = perfect_polaroid()
    layers[0]["scaleY"] = -1
    layers[1]["scaleX"] = -1
    return H(layers)
add("J96: outer flipped V, inner flipped H", case_j96())


def case_j97():
    """Inner is text."""
    layers = perfect_polaroid()[:1]
    text = make_layer("text", x=420, y=420, w=260, h=260, fill=BLACK)
    text["content"] = "photo"
    layers.append(text)
    return H(layers, evts=evt(rectangle=1, extras=[make_event("create_text")]))
add("J97: outer rect + inner text", case_j97())


def case_j98():
    layers = perfect_polaroid()
    for l in layers:
        l["x"] -= 5000
        l["y"] -= 5000
    return H(layers)
add("J98: at extreme negative coords", case_j98())


def case_j99():
    layers = perfect_polaroid()
    for l in layers:
        l["rotation"] = 360
    return H(layers)
add("J99: rotation=360°", case_j99())


def case_j100(): return H()
add("J100: perfect polaroid (control)", case_j100())


# ── Run ─────────────────────────────────────────────────────────────
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

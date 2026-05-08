"""100 edge cases for task 27 (Neumorphic button) — runs all and prints a sorted score table.

Spec: 200×200 light-gray rounded rectangle with two paired drop shadows.
"""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_27_neumorphic_button as t
T = t.task

# ─── Helpers ────────────────────────────────────────────────────────
LIGHT_GRAY = (0.88, 0.90, 0.93)
DARK_GRAY  = (0.30, 0.30, 0.30)
GRAY       = (0.5, 0.5, 0.5)
BLUE       = (0.2, 0.4, 0.85)


def evt(rect=1, set_fill=1, effects=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(effects):  sem.append(make_event("add_effect"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_button():
    """Single 200x200 light-gray rounded rect with 2 drop shadows."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY,
            cornerRadius=24,
            effects=[
                make_drop_shadow(x=-6, y=-6, blur=12, rgb=(1,1,1), alpha=0.6),
                make_drop_shadow(x=6, y=6, blur=12, rgb=(0,0,0), alpha=0.25),
            ])
    return [btn]


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95), evts=None, in_frame=True):
    if layers is None: layers = perfect_button()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# A. Counts
def case_a1():
    """Two buttons (extra rectangle)."""
    layers = perfect_button()
    layers.append(L("rectangle", 200, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
                    effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)]))
    return H(layers, evts=evt(rect=2))
add("A1: 2 buttons (extra rect)", case_a1())


def case_a2():
    """Zero rectangles (empty design)."""
    return H([], evts=evt(rect=0, effects=0))
add("A2: 0 buttons (empty)", case_a2())


def case_a3():
    """3 stacked rectangles."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 540+i*50, 316+i*50, 200, 200, LIGHT_GRAY, cornerRadius=24,
                        effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)]))
    return H(layers, evts=evt(rect=3))
add("A3: 3 stacked rects", case_a3())


def case_a4():
    """Half: 1 rect but no effects."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24, effects=[])
    return H([btn], evts=evt(effects=0))
add("A4: 1 rect, no shadows at all", case_a4())


def case_a5():
    """Five rectangles (way too many)."""
    layers = []
    for i in range(5):
        layers.append(L("rectangle", 100+i*200, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
                        effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)]))
    return H(layers, evts=evt(rect=5))
add("A5: 5 rects in a row", case_a5())


def case_a6():
    """1 rect + an extra ellipse."""
    layers = perfect_button()
    layers.append(L("ellipse", 100, 100, 80, 80, LIGHT_GRAY))
    return H(layers, evts=evt() + [make_event("create_ellipse")])
add("A6: 1 rect + extra ellipse", case_a6())


def case_a7():
    """Off-by-one: 4 effects instead of 2."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=-3,y=-3),
                     make_drop_shadow(x=3,y=3), make_drop_shadow(x=6,y=6)])
    return H([btn], evts=evt(effects=4))
add("A7: 4 drop shadows (too many)", case_a7())


def case_a8():
    """1 rect + 1 polygon (extra shape)."""
    layers = perfect_button()
    layers.append(L("polygon", 100, 100, 80, 80, LIGHT_GRAY, sides=6))
    return H(layers, evts=evt() + [make_event("create_polygon")])
add("A8: 1 rect + extra polygon", case_a8())


def case_a9():
    """0 rectangles, 1 ellipse (substituted)."""
    btn = L("ellipse", 540, 316, 200, 200, LIGHT_GRAY,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn], evts=evt(rect=0) + [make_event("create_ellipse")])
add("A9: ellipse instead of rectangle", case_a9())


def case_a10():
    """Perfect (control)."""
    return H()
add("A10: perfect button (control)", case_a10())


# B. Colors / fills
def case_b11():
    """Image fill instead of solid."""
    btn = perfect_button()[0]
    btn["fills"] = [{"kind": "image", "src": "btn.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H([btn])
add("B11: image fill (not solid)", case_b11())


def case_b12():
    """Gradient fill."""
    btn = perfect_button()[0]
    btn["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":1,"b":1,"a":1}},
        {"position": 1, "color": {"r":0.5,"g":0.5,"b":0.5,"a":1}}], "opacity":1, "visible":True}]
    return H([btn])
add("B12: gradient fill", case_b12())


def case_b13():
    """Empty fills array."""
    btn = perfect_button()[0]
    btn["fills"] = []
    return H([btn])
add("B13: no fills (empty array)", case_b13())


def case_b14():
    """Stroke-only, no fill."""
    btn = perfect_button()[0]
    btn["fills"] = []
    btn["strokes"] = [make_stroke(rgb=LIGHT_GRAY, weight=4)]
    return H([btn])
add("B14: stroke-only (no fill)", case_b14())


def case_b15():
    """Way wrong color (hot pink)."""
    btn = L("rectangle", 540, 316, 200, 200, (1.0, 0.0, 0.5), cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("B15: hot pink fill (wrong color)", case_b15())


def case_b16():
    """Near tolerance edge (slight off)."""
    btn = L("rectangle", 540, 316, 200, 200, (0.75, 0.78, 0.81), cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("B16: medium gray (close to tolerance)", case_b16())


def case_b17():
    """Pure black (very wrong)."""
    btn = L("rectangle", 540, 316, 200, 200, (0,0,0), cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("B17: pure black", case_b17())


def case_b18():
    """fill alpha=0.0 (fully transparent)."""
    btn = perfect_button()[0]
    btn["fills"][0]["color"]["a"] = 0.0
    return H([btn])
add("B18: fill alpha=0", case_b18())


def case_b19():
    """fill opacity=0.05 (nearly invisible)."""
    btn = perfect_button()[0]
    btn["fills"][0]["opacity"] = 0.05
    return H([btn])
add("B19: fill opacity=0.05", case_b19())


def case_b20():
    """Stacked fills (solid + image + gradient)."""
    btn = perfect_button()[0]
    btn["fills"].extend([
        {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
        {"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":0,"b":0,"a":1}}], "opacity":0.3, "visible":True}])
    return H([btn])
add("B20: stacked fills (solid first)", case_b20())


# C. Sizing
def case_c21():
    """Tiny 20x20 rectangle."""
    btn = L("rectangle", 540, 316, 20, 20, LIGHT_GRAY, cornerRadius=4,
            effects=[make_drop_shadow(x=-2,y=-2), make_drop_shadow(x=2,y=2)])
    return H([btn])
add("C21: 20x20 (tiny)", case_c21())


def case_c22():
    """Huge 800x800."""
    btn = L("rectangle", 200, 100, 800, 800, LIGHT_GRAY, cornerRadius=80,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C22: 800x800 (huge)", case_c22())


def case_c23():
    """Skinny 40x500."""
    btn = L("rectangle", 540, 316, 40, 500, LIGHT_GRAY, cornerRadius=10,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C23: 40x500 (skinny vertical)", case_c23())


def case_c24():
    """Wide 800x40."""
    btn = L("rectangle", 200, 316, 800, 40, LIGHT_GRAY, cornerRadius=10,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C24: 800x40 (wide horizontal)", case_c24())


def case_c25():
    """Just inside tolerance: 209x209."""
    btn = L("rectangle", 540, 316, 209, 209, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C25: 209x209 (just inside tol)", case_c25())


def case_c26():
    """Just outside tolerance: 220x220."""
    btn = L("rectangle", 540, 316, 220, 220, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C26: 220x220 (just outside tol)", case_c26())


def case_c27():
    """Half size 100x100."""
    btn = L("rectangle", 540, 316, 100, 100, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C27: 100x100 (half size)", case_c27())


def case_c28():
    """Double size 400x400."""
    btn = L("rectangle", 440, 216, 400, 400, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C28: 400x400 (double)", case_c28())


def case_c29():
    """1x1 degenerate."""
    btn = L("rectangle", 540, 316, 1, 1, LIGHT_GRAY, cornerRadius=0,
            effects=[make_drop_shadow(x=-1,y=-1), make_drop_shadow(x=1,y=1)])
    return H([btn])
add("C29: 1x1 degenerate", case_c29())


def case_c30():
    """Wrong aspect 200x100 (rectangle, not square)."""
    btn = L("rectangle", 540, 316, 200, 100, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("C30: 200x100 (rect, not square)", case_c30())


# D. Position
def case_d31():
    """Far top-left corner."""
    btn = L("rectangle", 0, 0, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D31: button at (0,0)", case_d31())


def case_d32():
    """Far bottom-right past frame."""
    btn = L("rectangle", 1100, 700, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D32: extends past frame edge", case_d32())


def case_d33():
    """Negative coords."""
    btn = L("rectangle", -100, -100, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D33: negative coords", case_d33())


def case_d34():
    """Centered (perfect)."""
    return H()
add("D34: centered (perfect)", case_d34())


def case_d35():
    """At frame edge."""
    btn = L("rectangle", 1080, 632, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D35: button right-aligned to frame edge", case_d35())


def case_d36():
    """Far off-frame to the right."""
    btn = L("rectangle", 2000, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D36: button at x=2000 (way off frame)", case_d36())


def case_d37():
    """Slightly off-center (acceptable)."""
    btn = L("rectangle", 600, 350, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D37: slight off-center", case_d37())


def case_d38():
    """Way off-center."""
    btn = L("rectangle", 100, 100, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D38: button in top-left quadrant", case_d38())


def case_d39():
    """y far below visible area."""
    btn = L("rectangle", 540, 5000, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D39: y=5000 (off-frame down)", case_d39())


def case_d40():
    """y far above frame."""
    btn = L("rectangle", 540, -2000, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("D40: y=-2000 (off-frame up)", case_d40())


# E. Per-shape variants (rotation, corner radius extremes)
def case_e41():
    """No corner radius (sharp corners)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=0,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("E41: cornerRadius=0 (sharp)", case_e41())


def case_e42():
    """Minimal radius=2."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=2,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("E42: cornerRadius=2 (almost sharp)", case_e42())


def case_e43():
    """Just under 16: cornerRadius=15."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=15,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("E43: cornerRadius=15 (just under min)", case_e43())


def case_e44():
    """Big radius: cornerRadius=80."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=80,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("E44: cornerRadius=80 (very rounded)", case_e44())


def case_e45():
    """Maxed out: cornerRadius=100 (becomes circle)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=100,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("E45: cornerRadius=100 (full pill/circle)", case_e45())


def case_e46():
    """Rotated 45°."""
    btn = perfect_button()[0]
    btn["rotation"] = 45
    return H([btn])
add("E46: rotated 45°", case_e46())


def case_e47():
    """Rotated 4° (under tol)."""
    btn = perfect_button()[0]
    btn["rotation"] = 4
    return H([btn])
add("E47: rotated 4° (under tol)", case_e47())


def case_e48():
    """Rotated 180°."""
    btn = perfect_button()[0]
    btn["rotation"] = 180
    return H([btn])
add("E48: rotated 180°", case_e48())


def case_e49():
    """Flipped horizontally."""
    btn = perfect_button()[0]
    btn["scaleX"] = -1
    return H([btn])
add("E49: scaleX=-1 (flipped H)", case_e49())


def case_e50():
    """Flipped vertically."""
    btn = perfect_button()[0]
    btn["scaleY"] = -1
    return H([btn])
add("E50: scaleY=-1 (flipped V)", case_e50())


# F. Effect / shadow variants
def case_f51():
    """Single drop shadow."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=6,y=6)])
    return H([btn], evts=evt(effects=1))
add("F51: only 1 drop shadow", case_f51())


def case_f52():
    """No shadow at all."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24, effects=[])
    return H([btn], evts=evt(effects=0))
add("F52: no effects", case_f52())


def case_f53():
    """Layer blur instead of drop shadow."""
    from qa_per_task._helpers import make_layer_blur
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_layer_blur(radius=8), make_layer_blur(radius=4)])
    return H([btn], evts=evt(effects=2))
add("F53: 2 layer blurs (not drop shadow)", case_f53())


def case_f54():
    """Mixed: 1 drop shadow + 1 layer blur."""
    from qa_per_task._helpers import make_layer_blur
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=6,y=6), make_layer_blur(radius=8)])
    return H([btn], evts=evt(effects=2))
add("F54: 1 drop shadow + 1 layer blur", case_f54())


def case_f55():
    """3 drop shadows (extra)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6),
                     make_drop_shadow(x=0,y=10)])
    return H([btn], evts=evt(effects=3))
add("F55: 3 drop shadows", case_f55())


def case_f56():
    """Drop shadow with alpha=0 (invisible)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6,alpha=0), make_drop_shadow(x=6,y=6,alpha=0)])
    return H([btn])
add("F56: 2 drop shadows alpha=0", case_f56())


def case_f57():
    """Drop shadow with visible=False."""
    e1 = make_drop_shadow(x=-6,y=-6); e1["visible"] = False
    e2 = make_drop_shadow(x=6,y=6); e2["visible"] = False
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[e1, e2])
    return H([btn])
add("F57: 2 drop shadows visible=False", case_f57())


def case_f58():
    """Both shadows on the same side (no contrast)."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=6,y=6), make_drop_shadow(x=8,y=8)])
    return H([btn])
add("F58: 2 drop shadows on same side", case_f58())


def case_f59():
    """Tiny blur, no offset."""
    btn = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=0,y=0,blur=0), make_drop_shadow(x=0,y=0,blur=0)])
    return H([btn])
add("F59: 2 zero-offset zero-blur shadows", case_f59())


def case_f60():
    """Effects on the wrong shape: 2 ellipses with 2 shadows each, but no rect."""
    layers = [L("ellipse", 540, 316, 200, 200, LIGHT_GRAY,
                effects=[make_drop_shadow(), make_drop_shadow()])]
    return H(layers, evts=evt(rect=0) + [make_event("create_ellipse")])
add("F60: shadow on ellipse, no rect", case_f60())


# G. Frame variants
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_button()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers = perfect_button()
    inner = make_frame(layers, w=1000, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """2 frames, button in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_button(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, btn in 2nd", case_g63())


def case_g64():
    """Frame stroke."""
    layers = perfect_button()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())


def case_g65():
    """Frame image fill."""
    layers = perfect_button()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())


def case_g66():
    """Frame much smaller than button."""
    layers = perfect_button()
    frame = make_frame(layers, w=100, h=100)
    return make_log([frame], evt())
add("G66: frame 100x100 (smaller than btn)", case_g66())


def case_g67():
    """Frame translated."""
    layers = perfect_button()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated to (500,300)", case_g67())


def case_g68():
    """No frame, button on page directly."""
    return H(in_frame=False)
add("G68: no frame, btn on page", case_g68())


def case_g69():
    """Frame much bigger."""
    layers = perfect_button()
    frame = make_frame(layers, w=3000, h=2000)
    return make_log([frame], evt())
add("G69: frame 3000x2000 (huge)", case_g69())


def case_g70():
    """Frame with image fill instead of solid."""
    layers = perfect_button()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":1,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G70: frame has gradient fill", case_g70())


# H. Tools / events
def case_h71():
    """50 move events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())


def case_h72():
    """50 undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())


def case_h73():
    """No tool changes (only create)."""
    sem = [make_event("session_start")]
    sem.append(make_event("create_rectangle"))
    sem.append(make_event("set_fill_color"))
    sem.append(make_event("add_effect"))
    sem.append(make_event("add_effect"))
    return H(evts=sem)
add("H73: no tool_change events", case_h73())


def case_h74():
    """Used pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_rectangle")]
    sem.append(make_event("add_effect"))
    sem.append(make_event("add_effect"))
    return H(evts=sem)
add("H74: pen tool used (not rectangle)", case_h74())


def case_h75():
    """Star tool used in middle."""
    extras = [make_event("tool_change", before="rectangle", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: star tool used (then deleted)", case_h75())


def case_h76():
    """Many duplicate session_ends."""
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H76: many session_end events", case_h76())


def case_h77():
    """Way too many fill events."""
    return H(evts=evt(set_fill=20))
add("H77: 20 set_fill_color events", case_h77())


def case_h78():
    """Wrong tool used (line)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line"),
           make_event("create_rectangle")]
    sem.extend([make_event("add_effect"), make_event("add_effect")])
    return H(evts=sem)
add("H78: line tool used", case_h78())


def case_h79():
    """Add 30 align events."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x") for _ in range(30)]))
add("H79: 30 align events", case_h79())


def case_h80():
    """Distribute_layers used."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: 1 distribute event", case_h80())


# I. Hierarchy / structure
def case_i81():
    """Button inside group inside frame."""
    layers = perfect_button()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: button in group in frame", case_i81())


def case_i82():
    """Button in section."""
    layers = perfect_button()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I82: button in section", case_i82())


def case_i83():
    """3-deep nested frames."""
    layers = perfect_button()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I83: 3-deep nested frames", case_i83())


def case_i84():
    """Button on page 2."""
    layers = perfect_button()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I84: button on page 2", case_i84())


def case_i85():
    """Button inside component."""
    layers = perfect_button()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I85: button inside component", case_i85())


def case_i86():
    """Two frames with one button each."""
    btn1 = perfect_button()[0]
    btn2 = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
             effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    f1 = make_frame([btn1], w=1280, h=832)
    f2 = make_frame([btn2], w=1280, h=832)
    return make_log([f1, f2], evt(rect=2))
add("I86: 2 frames, each with own button (2 rects total)", case_i86())


def case_i87():
    """Button outside any container (page directly)."""
    return H(in_frame=False)
add("I87: button on page (no container)", case_i87())


def case_i88():
    """Group at page top level."""
    layers = perfect_button()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([group], evt())
add("I88: button in group at page level", case_i88())


# J. Bizarre
def case_j89():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())


def case_j90():
    """Frame only, no shapes."""
    return H([])
add("J90: frame only, no shapes", case_j90())


def case_j91():
    """Text layer 'button'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "neumorphic button"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text layer 'neumorphic button'", case_j91())


def case_j92():
    """Star instead of rectangle (with 2 shadows)."""
    star = make_layer("star", x=540, y=316, w=200, h=200, fill=LIGHT_GRAY,
                      points=5, innerRatio=0.4,
                      effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([star], evts=evt(rect=0) + [make_event("create_star")])
add("J92: star instead of rect", case_j92())


def case_j93():
    """Polygon instead of rectangle."""
    poly = make_layer("polygon", x=540, y=316, w=200, h=200, fill=LIGHT_GRAY,
                      sides=4,
                      effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([poly], evts=evt(rect=0) + [make_event("create_polygon")])
add("J93: polygon (square) instead of rect", case_j93())


def case_j94():
    """Two rectangles, identical."""
    btn1 = perfect_button()[0]
    btn2 = L("rectangle", 540, 316, 200, 200, LIGHT_GRAY, cornerRadius=24,
             effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn1, btn2], evts=evt(rect=2))
add("J94: 2 identical rects stacked", case_j94())


def case_j95():
    """Negative size 200x-200 (degenerate)."""
    btn = L("rectangle", 540, 316, 200, -200, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("J95: negative h (h=-200)", case_j95())


def case_j96():
    """Layer-level opacity=0.0."""
    btn = perfect_button()[0]
    btn["opacity"] = 0.0
    return H([btn])
add("J96: layer opacity=0", case_j96())


def case_j97():
    """visible=False."""
    btn = perfect_button()[0]
    btn["visible"] = False
    return H([btn])
add("J97: layer visible=False", case_j97())


def case_j98():
    """Button = full frame size."""
    btn = L("rectangle", 0, 0, 1280, 832, LIGHT_GRAY, cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("J98: button = full frame", case_j98())


def case_j99():
    """Same color as frame fill (camouflage)."""
    btn = L("rectangle", 540, 316, 200, 200, (0.95, 0.95, 0.95), cornerRadius=24,
            effects=[make_drop_shadow(x=-6,y=-6), make_drop_shadow(x=6,y=6)])
    return H([btn])
add("J99: btn matches frame fill", case_j99())


def case_j100():
    """Perfect button (control)."""
    return H()
add("J100: perfect button (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

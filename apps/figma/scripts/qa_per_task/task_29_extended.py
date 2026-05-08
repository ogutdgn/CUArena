"""100 edge cases for task 29 (Polka dot grid) — runs all and prints a sorted score table.

Spec: Off-white frame + 4 same-color circles in 2x2 grid (Tidy up).
"""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    LIGHT_GRAY,
)
from tasks import task_29_polka_dot_grid as t
T = t.task

OFF_WHITE = (0.97, 0.95, 0.92)
DOT_BLUE  = (0.2, 0.4, 0.85)


def evt(ellipse=4, set_fill=1, align=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(align):    sem.append(make_event("align_layers", axis="center_x"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    """4 same-color circles in 2x2 grid."""
    dots = []
    size = 80
    gap = 40
    for i in range(4):
        row = i // 2
        col = i % 2
        x = 540 + col * (size + gap)
        y = 320 + row * (size + gap)
        dots.append(L("ellipse", x, y, size, size, DOT_BLUE))
    return dots


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=OFF_WHITE, evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# A. Counts
def case_a1():
    """3 circles."""
    layers = perfect_design()[:3]
    return H(layers, evts=evt(ellipse=3))
add("A1: 3 circles", case_a1())


def case_a2():
    """5 circles."""
    layers = perfect_design()
    layers.append(L("ellipse", 540, 600, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=5))
add("A2: 5 circles", case_a2())


def case_a3():
    """0 circles."""
    return H([], evts=evt(ellipse=0))
add("A3: 0 circles", case_a3())


def case_a4():
    """8 circles."""
    layers = []
    for i in range(8):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 200 + row*120, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=8))
add("A4: 8 circles in 2x4 grid", case_a4())


def case_a5():
    """4 circles + extra rectangle."""
    layers = perfect_design()
    layers.append(L("rectangle", 100, 100, 80, 80, DOT_BLUE))
    return H(layers, evts=evt() + [make_event("create_rectangle")])
add("A5: 4 circles + extra rect", case_a5())


def case_a6():
    """4 circles + 2 polygons."""
    layers = perfect_design()
    layers.append(L("polygon", 100, 100, 80, 80, DOT_BLUE, sides=6))
    layers.append(L("polygon", 1000, 100, 80, 80, DOT_BLUE, sides=6))
    return H(layers, evts=evt() + [make_event("create_polygon"), make_event("create_polygon")])
add("A6: 4 circles + 2 polygons", case_a6())


def case_a7():
    """Off-by-one: 3 circles + 1 ellipse 'mistake'."""
    layers = perfect_design()[:3]
    layers.append(L("ellipse", 800, 800, 80, 80, DOT_BLUE))  # at wrong location
    return H(layers, evts=evt(ellipse=4))
add("A7: 3 dots + 1 stray ellipse", case_a7())


def case_a8():
    """Doubled: 8 circles in 4x2."""
    layers = []
    for i in range(8):
        row = i // 4
        col = i % 4
        layers.append(L("ellipse", 200 + col*120, 300 + row*120, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=8))
add("A8: 4x2 grid (doubled)", case_a8())


def case_a9():
    """Halved: only 2 circles."""
    layers = perfect_design()[:2]
    return H(layers, evts=evt(ellipse=2))
add("A9: 2 circles only", case_a9())


def case_a10():
    """Perfect (control)."""
    return H()
add("A10: perfect 2x2 grid (control)", case_a10())


# B. Colors / fills
def case_b11():
    """Image fill on circles."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "dot.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B11: circles have image fill", case_b11())


def case_b12():
    """Gradient fill on circles."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B12: circles have gradient", case_b12())


def case_b13():
    """Empty fills on circles."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B13: circles no fills", case_b13())


def case_b14():
    """Stroke-only circles."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=DOT_BLUE, weight=4)]
    return H(layers)
add("B14: stroke-only circles", case_b14())


def case_b15():
    """4 different colors (allowed by spec)."""
    layers = []
    colors = [RED, GREEN, NAVY, YELLOW]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 80, 80, colors[i]))
    return H(layers)
add("B15: 4 different colors (acceptable)", case_b15())


def case_b16():
    """Frame is wrong color (not off-white)."""
    return H(frame_fill=PINK)
add("B16: frame is pink", case_b16())


def case_b17():
    """Frame has gradient fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":1,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("B17: frame has gradient", case_b17())


def case_b18():
    """Circles fill alpha=0."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: circles fill alpha=0", case_b18())


def case_b19():
    """Circles fill opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: circles fill opacity=0.05", case_b19())


def case_b20():
    """Stacked fills on circles."""
    layers = perfect_design()
    for l in layers:
        l["fills"].extend([
            {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
            {"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":0,"b":0,"a":1}}], "opacity":0.3, "visible":True}])
    return H(layers)
add("B20: circles have stacked fills", case_b20())


# C. Sizing
def case_c21():
    """Circles tiny 5x5."""
    layers = perfect_design()
    for l in layers:
        l["w"] = l["h"] = 5
    return H(layers)
add("C21: 5x5 dots (tiny)", case_c21())


def case_c22():
    """Circles huge 400x400."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 100 + col*450, 50 + row*450, 400, 400, DOT_BLUE))
    return H(layers)
add("C22: 400x400 dots (huge)", case_c22())


def case_c23():
    """Circles different sizes (varying)."""
    layers = []
    sizes = [60, 90, 60, 90]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("C23: 4 dots different sizes (60/90)", case_c23())


def case_c24():
    """Circles non-circular (oval)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 100, 60, DOT_BLUE))
    return H(layers)
add("C24: ovals (100x60, not circular)", case_c24())


def case_c25():
    """Circles 1x1 (degenerate)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 1, 1, DOT_BLUE))
    return H(layers)
add("C25: 1x1 dots (degenerate)", case_c25())


def case_c26():
    """3 small dots and 1 huge dot."""
    layers = []
    sizes = [40, 40, 40, 200]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("C26: 3 small + 1 large dot", case_c26())


def case_c27():
    """Circles overlapping (size > gap)."""
    layers = []
    size = 200
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*100, 320 + row*100, size, size, DOT_BLUE))
    return H(layers)
add("C27: 200x200 dots overlapping", case_c27())


def case_c28():
    """Circles too far apart (huge gap)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 100 + col*1000, 100 + row*600, 80, 80, DOT_BLUE))
    return H(layers)
add("C28: dots widely scattered", case_c28())


def case_c29():
    """Within tolerance (sizes 78, 80, 80, 82)."""
    layers = []
    sizes = [78, 80, 80, 82]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("C29: dots 78/80/80/82 (within tol)", case_c29())


def case_c30():
    """Just outside tolerance: sizes 70, 80, 80, 90."""
    layers = []
    sizes = [70, 80, 80, 90]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("C30: dots 70/80/80/90 (outside tol)", case_c30())


# D. Position
def case_d31():
    """Dots in a row (1x4)."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 200 + i*150, 400, 80, 80, DOT_BLUE))
    return H(layers)
add("D31: 1x4 row instead of 2x2", case_d31())


def case_d32():
    """Dots in 4x1 column."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 600, 100 + i*150, 80, 80, DOT_BLUE))
    return H(layers)
add("D32: 4x1 column", case_d32())


def case_d33():
    """Dots stacked in pile (all at one point)."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 600, 400, 80, 80, DOT_BLUE))
    return H(layers)
add("D33: 4 dots piled at same point", case_d33())


def case_d34():
    """Dots in 2x2 grid but offset by 6px (within tol)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120 + (6 if i==0 else 0), 320 + row*120, 80, 80, DOT_BLUE))
    return H(layers)
add("D34: 2x2 grid 6px offset (within tol)", case_d34())


def case_d35():
    """Dots in 2x2 grid offset by 30px (outside tol)."""
    layers = []
    offsets = [(0,0),(30,0),(0,30),(30,30)]
    for i in range(4):
        row = i // 2
        col = i % 2
        ox, oy = offsets[i]
        layers.append(L("ellipse", 540 + col*120 + ox, 320 + row*120 + oy, 80, 80, DOT_BLUE))
    return H(layers)
add("D35: 2x2 grid 30px offsets (outside tol)", case_d35())


def case_d36():
    """Dots positioned diagonally (TL, TR, BL, BR... but at corners)."""
    layers = []
    pts = [(50,50), (1100,50), (50,650), (1100,650)]
    for x, y in pts:
        layers.append(L("ellipse", x, y, 80, 80, DOT_BLUE))
    return H(layers)
add("D36: dots at frame corners", case_d36())


def case_d37():
    """Dots in 3x2 (extra dot)."""
    layers = []
    for i in range(6):
        row = i // 3
        col = i % 3
        layers.append(L("ellipse", 300 + col*120, 320 + row*120, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=6))
add("D37: 3x2 grid (6 dots)", case_d37())


def case_d38():
    """All dots overlap each other."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 540 + i*5, 320 + i*5, 80, 80, DOT_BLUE))
    return H(layers)
add("D38: dots heavily overlapping", case_d38())


def case_d39():
    """Dots in concentric layout."""
    layers = []
    sizes = [200, 150, 100, 50]
    for size in sizes:
        layers.append(L("ellipse", 600 - size/2, 400 - size/2, size, size, DOT_BLUE))
    return H(layers)
add("D39: 4 concentric circles", case_d39())


def case_d40():
    """Dots off-frame entirely."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 1500 + col*120, 1000 + row*120, 80, 80, DOT_BLUE))
    return H(layers)
add("D40: dots off-frame", case_d40())


# E. Per-shape variants
def case_e41():
    """Dots rotated 30°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 30
    return H(layers)
add("E41: dots rotated 30°", case_e41())


def case_e42():
    """Dots flipped scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E42: dots scaleX=-1", case_e42())


def case_e43():
    """Dots near-circular: 80x82 (within 3 tol)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 80, 82, DOT_BLUE))
    return H(layers)
add("E43: dots 80x82 (within circular tol)", case_e43())


def case_e44():
    """Dots 80x90 (outside circular tol)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 80, 90, DOT_BLUE))
    return H(layers)
add("E44: dots 80x90 (outside circular tol)", case_e44())


def case_e45():
    """Dots stretched 80x40."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*60, 80, 40, DOT_BLUE))
    return H(layers)
add("E45: dots squashed 80x40", case_e45())


def case_e46():
    """Dots have shadows."""
    layers = perfect_design()
    for l in layers:
        l["effects"] = [make_drop_shadow(x=2, y=2)]
    return H(layers)
add("E46: dots with drop shadows (decorations)", case_e46())


def case_e47():
    """Half dots have layer-blur."""
    layers = perfect_design()
    for l in layers[:2]:
        l["effects"] = [{"kind": "layer_blur", "radius": 4, "visible": True}]
    return H(layers)
add("E47: half dots blurred", case_e47())


def case_e48():
    """Dots have strokes too."""
    layers = perfect_design()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=NAVY, weight=2)]
    return H(layers)
add("E48: dots have strokes (decoration)", case_e48())


def case_e49():
    """Dots in cornerRadius (rectangle disguise)."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 40
    return H(layers)
add("E49: dots have cornerRadius=40 (no effect on ellipse)", case_e49())


def case_e50():
    """Dots layer.opacity=0.3."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.3
    return H(layers)
add("E50: dots opacity=0.3", case_e50())


# F. Subcomponent variants
def case_f51():
    """3 dots same color, 1 different."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"] = {"r": 1, "g": 0, "b": 0, "a": 1}  # red
    return H(layers)
add("F51: 3 blue dots + 1 red", case_f51())


def case_f52():
    """All dots have different sizes increasing."""
    layers = []
    sizes = [40, 60, 80, 100]
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, sizes[i], sizes[i], DOT_BLUE))
    return H(layers)
add("F52: dots increasing size 40/60/80/100", case_f52())


def case_f53():
    """Dots arranged in L shape."""
    layers = [
        L("ellipse", 200, 200, 80, 80, DOT_BLUE),
        L("ellipse", 200, 320, 80, 80, DOT_BLUE),
        L("ellipse", 200, 440, 80, 80, DOT_BLUE),
        L("ellipse", 320, 440, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("F53: dots in L-shape (3+1)", case_f53())


def case_f54():
    """Dots in zig-zag pattern."""
    layers = [
        L("ellipse", 200, 200, 80, 80, DOT_BLUE),
        L("ellipse", 320, 350, 80, 80, DOT_BLUE),
        L("ellipse", 440, 200, 80, 80, DOT_BLUE),
        L("ellipse", 560, 350, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("F54: zig-zag dots", case_f54())


def case_f55():
    """Dots clustered (all near each other)."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 600 + (i%2)*40, 400 + (i//2)*40, 80, 80, DOT_BLUE))
    return H(layers)
add("F55: 4 dots tightly clustered", case_f55())


def case_f56():
    """Dots in triangular layout."""
    layers = [
        L("ellipse", 600, 200, 80, 80, DOT_BLUE),
        L("ellipse", 540, 320, 80, 80, DOT_BLUE),
        L("ellipse", 660, 320, 80, 80, DOT_BLUE),
        L("ellipse", 600, 440, 80, 80, DOT_BLUE),
    ]
    return H(layers)
add("F56: dots in diamond/triangle", case_f56())


def case_f57():
    """Dots in wide grid (gap > size)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 200 + col*400, 200 + row*400, 80, 80, DOT_BLUE))
    return H(layers)
add("F57: dots widely spaced 2x2", case_f57())


def case_f58():
    """Dots touching (no gap)."""
    layers = []
    size = 80
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 540 + col*size, 320 + row*size, size, size, DOT_BLUE))
    return H(layers)
add("F58: dots touching with no gap", case_f58())


def case_f59():
    """Dots with progressive opacity."""
    layers = perfect_design()
    for i, l in enumerate(layers):
        l["fills"][0]["opacity"] = 0.25 + i*0.25
    return H(layers)
add("F59: dots opacity 0.25/0.5/0.75/1.0", case_f59())


def case_f60():
    """4 dots all same color (perfect except slight variation)."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        # small color variation within tolerance
        c = (DOT_BLUE[0]+i*0.005, DOT_BLUE[1], DOT_BLUE[2])
        layers.append(L("ellipse", 540 + col*120, 320 + row*120, 80, 80, c))
    return H(layers)
add("F60: dots tiny color variations (within tol)", case_f60())


# G. Frame variants
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=OFF_WHITE)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers = perfect_design()
    inner = make_frame(layers, w=1000, h=600, fill=OFF_WHITE)
    outer = make_frame([inner], w=1280, h=832, fill=OFF_WHITE)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """2 frames, dots in 2nd."""
    f1 = make_frame([], w=1280, h=832, fill=OFF_WHITE)
    f2 = make_frame(perfect_design(), w=1280, h=832, fill=OFF_WHITE)
    return make_log([f1, f2], evt())
add("G63: 2 frames, dots in 2nd", case_g63())


def case_g64():
    """Frame stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=OFF_WHITE)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())


def case_g65():
    """Frame image fill (not off-white)."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())


def case_g66():
    """Frame too small."""
    layers = perfect_design()
    frame = make_frame(layers, w=400, h=300, fill=OFF_WHITE)
    return make_log([frame], evt())
add("G66: frame 400x300 (too small)", case_g66())


def case_g67():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())


def case_g68():
    """No frame (dots on page)."""
    return H(in_frame=False)
add("G68: no frame, dots on page", case_g68())


def case_g69():
    """Frame with no fill at all."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    return make_log([frame], evt())
add("G69: frame with no fill", case_g69())


def case_g70():
    """Frame fill near tolerance (off-white-ish)."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=(0.93, 0.91, 0.88))
    return make_log([frame], evt())
add("G70: frame near-off-white (within tol)", case_g70())


# H. Tools / events
def case_h71():
    """50 move events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())


def case_h72():
    """50 undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())


def case_h73():
    """No align_layers events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(4): sem.append(make_event("create_ellipse"))
    sem.append(make_event("set_fill_color"))
    return H(evts=sem)
add("H73: no align_layers (Tidy up not used)", case_h73())


def case_h74():
    """No tool changes."""
    sem = [make_event("session_start")]
    for _ in range(4): sem.append(make_event("create_ellipse"))
    sem.append(make_event("set_fill_color"))
    sem.append(make_event("align_layers"))
    return H(evts=sem)
add("H74: no tool_change", case_h74())


def case_h75():
    """Wrong tool: rectangle instead of ellipse."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(4): sem.append(make_event("create_ellipse"))
    sem.append(make_event("align_layers"))
    return H(evts=sem)
add("H75: rectangle tool used", case_h75())


def case_h76():
    """Star tool used."""
    extras = [make_event("tool_change", before="ellipse", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H76: star tool used then deleted", case_h76())


def case_h77():
    """Many session_end events."""
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H77: 5 session_end", case_h77())


def case_h78():
    """20 set_fill_color events."""
    return H(evts=evt(set_fill=20))
add("H78: 20 fill events", case_h78())


def case_h79():
    """Used distribute_layers."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute used", case_h79())


def case_h80():
    """3 align_layers events."""
    return H(evts=evt(align=3))
add("H80: 3 align events", case_h80())


# I. Hierarchy / structure
def case_i81():
    """Dots in group inside frame."""
    layers = perfect_design()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame], evt())
add("I81: dots in group in frame", case_i81())


def case_i82():
    """Dots split across 2 frames."""
    dots = perfect_design()
    f1 = make_frame(dots[:2], w=640, h=832, fill=OFF_WHITE)
    f2 = make_frame(dots[2:], w=640, h=832, fill=OFF_WHITE)
    return make_log([f1, f2], evt())
add("I82: dots split across 2 frames", case_i82())


def case_i83():
    """3 dots in frame, 1 on page."""
    dots = perfect_design()
    frame = make_frame(dots[:3], w=1280, h=832, fill=OFF_WHITE)
    return make_log([frame, dots[3]], evt())
add("I83: 3 dots in frame, 1 on page", case_i83())


def case_i84():
    """3-deep nested frames."""
    dots = perfect_design()
    f3 = make_frame(dots, w=1280, h=832, fill=OFF_WHITE)
    f2 = make_frame([f3], w=1300, h=850, fill=OFF_WHITE)
    f1 = make_frame([f2], w=1320, h=870, fill=OFF_WHITE)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())


def case_i85():
    """Dots on page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=OFF_WHITE)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: dots on page 2", case_i85())


def case_i86():
    """Dots in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: dots in component (no frame)", case_i86())


def case_i87():
    """Dots in section."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I87: dots in section", case_i87())


def case_i88():
    """4 frames each with one dot."""
    dots = perfect_design()
    frames = [make_frame([d], w=400, h=400, fill=OFF_WHITE) for d in dots]
    return make_log(frames, evt())
add("I88: 4 dots each in own frame", case_i88())


# J. Bizarre
def case_j89():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())


def case_j90():
    """Frame only."""
    return H([])
add("J90: empty frame", case_j90())


def case_j91():
    """Text 'dots'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "dots"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'dots'", case_j91())


def case_j92():
    """4 polygons (hexagons) instead of ellipses."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("polygon", 540 + col*120, 320 + row*120, 80, 80, DOT_BLUE, sides=6))
    return H(layers, evts=evt(ellipse=0) + [make_event("create_polygon")]*4)
add("J92: 4 hexagons instead of ellipses", case_j92())


def case_j93():
    """4 squares."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("rectangle", 540 + col*120, 320 + row*120, 80, 80, DOT_BLUE))
    return H(layers, evts=evt(ellipse=0) + [make_event("create_rectangle")]*4)
add("J93: 4 squares", case_j93())


def case_j94():
    """Layer.opacity=0 on all dots."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("J94: dots opacity=0", case_j94())


def case_j95():
    """Visible=False on all dots."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J95: dots visible=False", case_j95())


def case_j96():
    """Dots = full frame."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", 0, 0, 1280, 832, DOT_BLUE))
    return H(layers)
add("J96: 4 dots = full frame each", case_j96())


def case_j97():
    """Negative coords."""
    layers = []
    for i in range(4):
        row = i // 2
        col = i % 2
        layers.append(L("ellipse", -200 + col*120, -200 + row*120, 80, 80, DOT_BLUE))
    return H(layers)
add("J97: dots at negative coords", case_j97())


def case_j98():
    """Mirror dots scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J98: dots scaleX=-1", case_j98())


def case_j99():
    """Dots at exact same point (overlapping pile)."""
    layers = []
    for _ in range(4):
        layers.append(L("ellipse", 600, 400, 80, 80, DOT_BLUE))
    return H(layers)
add("J99: 4 identical dots stacked", case_j99())


def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect 2x2 grid (control)", case_j100())


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

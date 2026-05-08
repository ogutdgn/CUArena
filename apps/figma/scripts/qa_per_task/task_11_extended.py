"""100 edge cases for task 11 — runs all and prints a sorted score table.

Task 11 = 3 triangles of decreasing size, centered together, alternating two colors.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    DARK_GRAY, LIGHT_GRAY, BLACK,
)
from tasks import task_11_pressed_button as t
T = t.task

COLOR_A = (0.10, 0.50, 0.90)
COLOR_B = (0.95, 0.85, 0.20)
COLOR_C = (0.95, 0.20, 0.20)


def evt(poly=3, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="polygon"))
    for _ in range(poly):
        sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def Tri(x, y, w, h, fill, sides=3, **extra):
    return make_layer("polygon", x=x, y=y, w=w, h=h, fill=fill, sides=sides, **extra)


def perfect_design(cx=640, cy=400):
    """3 triangles, decreasing size, alternating colors."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    return [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    return H(perfect_design()[:2], evts=evt(poly=2))
add("A1: only 2 triangles", case_a1())

def case_a2():
    return H([], evts=evt(poly=0))
add("A2: 0 triangles", case_a2())

def case_a3():
    """4 triangles."""
    sizes = [400, 320, 240, 160]
    cx, cy = 640, 400
    colors = [COLOR_A, COLOR_B, COLOR_A, COLOR_B]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=4))
add("A3: 4 triangles", case_a3())

def case_a4():
    """1 triangle."""
    return H(perfect_design()[:1], evts=evt(poly=1))
add("A4: 1 triangle", case_a4())

def case_a5():
    """6 triangles."""
    sizes = [400, 350, 300, 250, 200, 150]
    cx, cy = 640, 400
    colors = [COLOR_A, COLOR_B] * 3
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=6))
add("A5: 6 triangles", case_a5())

def case_a6():
    """3 triangles + 1 extra at corner."""
    layers = perfect_design()
    layers.append(Tri(50, 50, 80, 80, COLOR_C))
    return H(layers, evts=evt(poly=4))
add("A6: 3 nested + 1 extra", case_a6())

def case_a7():
    """3 polygons, none triangles (all 4-sided)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c, sides=4) for s, c in zip(sizes, colors)]
    return H(layers)
add("A7: 3 polygons sides=4 (squares)", case_a7())

def case_a8():
    """3 ellipses (not polygons)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("ellipse", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_ellipse")]*3))
add("A8: 3 ellipses (not polygons)", case_a8())

def case_a9():
    """3 rectangles."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("rectangle", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_rectangle")]*3))
add("A9: 3 rectangles (not polygons)", case_a9())

def case_a10():
    return H()
add("A10: 3 nested perfect (control)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    """All same color."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    layers = [Tri(cx-s/2, cy-s/2, s, s, COLOR_A) for s in sizes]
    return H(layers)
add("B11: all same color", case_b11())

def case_b12():
    """3 different colors (not alternating 2)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_C]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("B12: 3 different colors", case_b12())

def case_b13():
    """All image fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: all image fills", case_b13())

def case_b14():
    """All gradient."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1}},
            {"position": 1, "color": {"r": 0.8, "g": 0.8, "b": 0.8, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("B14: all gradient", case_b14())

def case_b15():
    """Stacked fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover",
                           "opacity": 0.5, "visible": True})
    return H(layers)
add("B15: stacked 2 fills each", case_b15())

def case_b16():
    """Stroke-only."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("B16: stroke-only", case_b16())

def case_b17():
    """Near-identical colors (within tol)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    layers = [Tri(cx-s/2, cy-s/2, s, s, (0.10, 0.50, 0.90)) for s in sizes]
    layers[1]["fills"][0]["color"]["g"] = 0.52  # tiny diff
    return H(layers)
add("B17: near-identical (within tol)", case_b17())

def case_b18():
    """Outer alpha=0."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: outer alpha=0", case_b18())

def case_b19():
    """All opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: all fill opacity=0.05", case_b19())

def case_b20():
    """Layer.opacity=0.05."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.05
    return H(layers)
add("B20: layer opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    """All same size."""
    cx, cy = 640, 400
    layers = [Tri(cx-100, cy-100, 200, 200, [COLOR_A, COLOR_B][i % 2])
              for i in range(3)]
    return H(layers)
add("C21: all same size", case_c21())

def case_c22():
    """Increasing size."""
    cx, cy = 640, 400
    sizes = [160, 280, 400]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C22: increasing size", case_c22())

def case_c23():
    """Tiny <20px triangles."""
    cx, cy = 640, 400
    sizes = [20, 15, 10]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C23: tiny <20px triangles", case_c23())

def case_c24():
    """Outer 1500x1500 (>frame)."""
    cx, cy = 640, 400
    sizes = [1500, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C24: outer 1500 (>frame)", case_c24())

def case_c25():
    """2:1 aspect ratio (not equilateral)."""
    cx, cy = 640, 400
    sizes = [(400, 200), (280, 140), (160, 80)]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("C25: 2:1 stretched triangles", case_c25())

def case_c26():
    """Mostly equal sizes (within tol)."""
    cx, cy = 640, 400
    sizes = [302, 300, 298]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C26: sizes within 4px (no real nesting)", case_c26())

def case_c27():
    """Innermost 1×1."""
    cx, cy = 640, 400
    sizes = [400, 280, 1]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C27: innermost 1×1", case_c27())

def case_c28():
    """All very narrow (1px wide tall lines)."""
    cx, cy = 640, 400
    sizes = [(2, 400), (2, 280), (2, 160)]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("C28: 2px-wide vertical lines", case_c28())

def case_c29():
    """Outer = full frame."""
    layers = perfect_design()
    layers[0] = Tri(0, 0, 1280, 832, COLOR_A)
    return H(layers)
add("C29: outer = full frame", case_c29())

def case_c30():
    """Sizes 90% step (gentle)."""
    cx, cy = 640, 400
    sizes = [400, 360, 324]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("C30: 90% step nesting (gentle)", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    """All in corner (not concentric)."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(50, 50, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D31: all top-left corner", case_d31())

def case_d32():
    """Scattered across canvas."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    positions = [(50, 50), (700, 200), (200, 600)]
    layers = [Tri(x, y, s, s, c) for (x, y), s, c in zip(positions, sizes, colors)]
    return H(layers)
add("D32: scattered positions", case_d32())

def case_d33():
    """In horizontal row."""
    cx = 100
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = []
    for s, c in zip(sizes, colors):
        layers.append(Tri(cx, 200, s, s, c))
        cx += s + 10
    return H(layers, frame_w=1500, frame_h=900)
add("D33: triangles in row", case_d33())

def case_d34():
    """All shifted off-frame."""
    cx, cy = 1500, 900
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D34: all off-frame", case_d34())

def case_d35():
    """Concentric within tolerance (5px)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = []
    for i, (s, c) in enumerate(zip(sizes, colors)):
        layers.append(Tri(cx-s/2 + (i-1)*2, cy-s/2 + i*2, s, s, c))
    return H(layers)
add("D35: concentric within 5px tol", case_d35())

def case_d36():
    """3 in vertical column."""
    cx = 640
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    cy = 50
    layers = []
    for s, c in zip(sizes, colors):
        layers.append(Tri(cx-s/2, cy, s, s, c))
        cy += s + 10
    return H(layers, frame_w=1280, frame_h=2000)
add("D36: triangles in column", case_d36())

def case_d37():
    """Inner outside outer's bounds."""
    cx, cy = 640, 400
    layers = [Tri(cx-200, cy-200, 400, 400, COLOR_A),
              Tri(cx-300, cy-300, 280, 280, COLOR_B),  # off-center
              Tri(cx-80,  cy-80,  160, 160, COLOR_A)]
    return H(layers)
add("D37: middle off-center (outside outer)", case_d37())

def case_d38():
    """Cascade with fixed offset."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(100+i*100, 100+i*100, s, s, c)
              for i, (s, c) in enumerate(zip(sizes, colors))]
    return H(layers)
add("D38: cascading positions", case_d38())

def case_d39():
    """Outer in center, others at edges."""
    cx, cy = 640, 400
    layers = [Tri(cx-200, cy-200, 400, 400, COLOR_A),
              Tri(50, 50, 280, 280, COLOR_B),
              Tri(900, 600, 160, 160, COLOR_A)]
    return H(layers)
add("D39: outer center, others corners", case_d39())

def case_d40():
    """All at negative coords."""
    cx, cy = -200, -200
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("D40: concentric at negative coords", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E41: all rotated 45°", case_e41())

def case_e42():
    layers = perfect_design()
    layers[1]["rotation"] = 30
    return H(layers)
add("E42: 1 rotated 30°", case_e42())

def case_e43():
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E43: all rotated 4° (under tol)", case_e43())

def case_e44():
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: all scaleX=-1", case_e44())

def case_e45():
    """Triangles have 5 sides each (pentagons)."""
    layers = perfect_design()
    for l in layers:
        l["sides"] = 5
    return H(layers)
add("E45: sides=5 (pentagons)", case_e45())

def case_e46():
    """1 triangle has sides=4."""
    layers = perfect_design()
    layers[1]["sides"] = 4
    return H(layers)
add("E46: 1 has sides=4 (square)", case_e46())

def case_e47():
    """All have stroke."""
    layers = perfect_design()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E47: all stroked", case_e47())

def case_e48():
    """All flipped vertically."""
    layers = perfect_design()
    for l in layers:
        l["scaleY"] = -1
    return H(layers)
add("E48: all scaleY=-1", case_e48())

def case_e49():
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E49: all rotated 90°", case_e49())

def case_e50():
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("E50: all rotated 180°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    """Sizes shuffled."""
    cx, cy = 640, 400
    sizes = [280, 400, 160]  # mid, big, small
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F51: sizes shuffled", case_f51())

def case_f52():
    """3 triangles of vastly different aspect."""
    cx, cy = 640, 400
    sizes = [(400, 100), (280, 280), (50, 200)]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("F52: mixed aspects", case_f52())

def case_f53():
    """Concentric but each touching outside (huge offset)."""
    cx, cy = 640, 400
    layers = [Tri(cx-200, cy-200, 400, 400, COLOR_A),
              Tri(cx-100, cy-100, 280, 280, COLOR_B),
              Tri(cx, cy, 160, 160, COLOR_A)]
    return H(layers)
add("F53: lower-right cascade", case_f53())

def case_f54():
    """Smallest-to-largest order in z-list."""
    cx, cy = 640, 400
    sizes = [160, 280, 400]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("F54: z-order ascending (smallest 1st)", case_f54())

def case_f55():
    """Triangles overlap each other but not concentrically."""
    cx, cy = 640, 400
    layers = [Tri(cx-200, cy-200, 400, 400, COLOR_A),
              Tri(cx-100, cy-200, 280, 280, COLOR_B),  # overlap right
              Tri(cx-50,  cy-100, 160, 160, COLOR_A)]
    return H(layers)
add("F55: overlapping but not concentric", case_f55())

def case_f56():
    """3 same-color triangles (1 distinct)."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    layers = [Tri(cx-s/2, cy-s/2, s, s, COLOR_A) for s in sizes]
    return H(layers)
add("F56: all same color", case_f56())

def case_f57():
    """Triangles touch but don't nest (each next to the other)."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    cx = 100
    layers = []
    for s, c in zip(sizes, colors):
        layers.append(Tri(cx, 200, s, s, c))
        cx += s
    return H(layers, frame_w=1500, frame_h=900)
add("F57: triangles next to each other", case_f57())

def case_f58():
    """Triangles arranged in vertical stack."""
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    cy = 50
    layers = []
    for s, c in zip(sizes, colors):
        layers.append(Tri(640-s/2, cy, s, s, c))
        cy += s
    return H(layers, frame_w=1280, frame_h=2000)
add("F58: vertical stack", case_f58())

def case_f59():
    """Each triangle progressively offset right."""
    cy = 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = []
    for i, (s, c) in enumerate(zip(sizes, colors)):
        layers.append(Tri(100 + i*200, cy-s/2, s, s, c))
    return H(layers, frame_w=1500, frame_h=900)
add("F59: triangles diagonally offset", case_f59())

def case_f60():
    """Perfect (control)."""
    return H()
add("F60: perfect (control)", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    inner = make_frame(perfect_design(), w=900, h=700)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    return H(in_frame=False)
add("G63: no frame", case_g63())

def case_g64():
    return H(frame_w=300, frame_h=300)
add("G64: frame 300x300", case_g64())

def case_g65():
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G65: frame stroked", case_g65())

def case_g66():
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G67: frame image fill", case_g67())

def case_g68():
    return H(frame_w=2000, frame_h=2000)
add("G68: frame 2000x2000", case_g68())

def case_g69():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_design(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames", case_g69())

def case_g70():
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 1
    return make_log([frame], evt())
add("G70: frame rotated 1° (under tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    sem = [make_event("session_start")]
    for _ in range(3): sem.append(make_event("create_polygon"))
    return H(evts=sem)
add("H71: no tool_change", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(3): sem.append(make_event("create_polygon"))
    return H(evts=sem)
add("H72: tool=rectangle but polygons", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    return H(evts=sem)
add("H73: 0 create_polygon events", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(2): sem.append(make_event("create_polygon"))
    return H(evts=sem)
add("H74: 2 create_polygon (not 3)", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("undo")]*100))
add("H75: 100 undo events", case_h75())

def case_h76():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H76: used align_layers", case_h76())

def case_h77():
    extras = [make_event("create_polygon"), make_event("delete")] * 3
    return H(evts=evt(extras=extras))
add("H77: 3 create+delete pairs", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("session_end")]*5))
add("H78: 5x session_end", case_h78())

def case_h79():
    """Created via duplicate."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon"),
           make_event("create_polygon"),
           make_event("duplicate"), make_event("duplicate")]
    return H(evts=sem)
add("H79: 1 create + 2 duplicate", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("set_fill_color")]*50))
add("H80: 50 set_fill events", case_h80())


# ─── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_design()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group in frame", case_i81())

def case_i82():
    layers = perfect_design()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I82: each in own frame", case_i82())

def case_i83():
    layers = perfect_design()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    layers = perfect_design()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I84: 1 in frame, 2 on page", case_i84())

def case_i85():
    layers = perfect_design()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    p1 = {"id": "p1", "children": [],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    p2 = {"id": "p2", "children": [frame],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I86: design on page 2", case_i86())

def case_i87():
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1280, "h": 832,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I87: in component", case_i87())

def case_i88():
    layers = perfect_design()
    g3 = {"id":"g3", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id":"g2", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id":"g1", "type":"group", "x":0, "y":0, "w":0, "h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    frame = make_frame([g1], w=1280, h=832)
    return make_log([frame], evt())
add("I88: 3-deep groups in frame", case_i88())

def case_i89():
    layers = perfect_design()
    frames = [make_frame([l], w=600, h=600) for l in layers]
    return make_log(frames, evt())
add("I89: each in own frame (split)", case_i89())

def case_i90():
    layers = perfect_design()
    frame = make_frame([], w=1280, h=832)
    return make_log([frame, *layers], evt())
add("I90: empty frame + sibling polygons", case_i90())


# ─── J. Bizarre / hard ──────────────────────────────────────────────
def case_j91():
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("J91: opacity=0", case_j91())

def case_j92():
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J92: visible=False", case_j92())

def case_j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", case_j93())

def case_j94():
    return H([])
add("J94: frame, no polygons", case_j94())

def case_j95():
    text = make_layer("text", x=400, y=400, w=200, h=40, fill=BLACK)
    text["content"] = "triangles"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'triangles' only", case_j95())

def case_j96():
    """3 stars."""
    cx, cy = 640, 400
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [make_layer("star", x=cx-s/2, y=cy-s/2, w=s, h=s, fill=c,
                         points=5, innerRatio=0.4)
              for s, c in zip(sizes, colors)]
    return H(layers, evts=evt(poly=0,
                              extras=[make_event("create_star")]*3))
add("J96: 3 stars (not polygons)", case_j96())

def case_j97():
    cx, cy = -200, -200
    sizes = [400, 280, 160]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-s/2, cy-s/2, s, s, c) for s, c in zip(sizes, colors)]
    return H(layers)
add("J97: at negative coords", case_j97())

def case_j98():
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J98: all mirrored (scaleX=-1)", case_j98())

def case_j99():
    """Polygons with sides=3 but stretched into lines."""
    cx, cy = 640, 400
    sizes = [(400, 1), (280, 1), (160, 1)]
    colors = [COLOR_A, COLOR_B, COLOR_A]
    layers = [Tri(cx-w/2, cy-h/2, w, h, c) for (w, h), c in zip(sizes, colors)]
    return H(layers)
add("J99: 1px-tall (degenerate)", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
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

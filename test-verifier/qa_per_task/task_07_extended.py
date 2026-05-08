"""100 edge cases for task 07 — runs all and prints a sorted score table.

Task 07 = two pen-tool mountain paths, distinct gray shades, layered (overlapping).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    DARK_GRAY, LIGHT_GRAY, BLACK,
)
from tasks import task_07_mountain_range as t
T = t.task

# ─── Helpers ────────────────────────────────────────────────────────
DGRAY = (0.30, 0.30, 0.30)   # dark gray
LGRAY = (0.60, 0.60, 0.60)   # lighter gray
MID_GRAY = (0.45, 0.45, 0.45)
NEAR_DGRAY1 = (0.31, 0.31, 0.31)  # within tolerance of DGRAY
NEAR_DGRAY2 = (0.32, 0.30, 0.30)


def evt(pen=True, vectors=2, set_fill=2, extras=()):
    sem = [make_event("session_start")]
    if pen:
        sem.append(make_event("tool_change", before="select", after="pen"))
    for _ in range(vectors):
        sem.append(make_event("create_vector"))
    for _ in range(set_fill):
        sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def V(x, y, w, h, fill, **extra):
    """Vector helper."""
    return make_layer("vector", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    far = V(100, 100, 500, 250, DGRAY)
    near = V(350, 200, 500, 200, LGRAY)  # overlaps far
    return [far, near]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1000, frame_h=400, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    """Only 1 mountain path."""
    return H([V(100, 100, 500, 250, DGRAY)], evts=evt(vectors=1, set_fill=1))
add("A1: only 1 vector (missing 2nd)", case_a1())

def case_a2():
    """3 mountain paths."""
    layers = perfect_design()
    layers.append(V(150, 250, 400, 150, MID_GRAY))
    return H(layers, evts=evt(vectors=3, set_fill=3))
add("A2: 3 vectors (extra)", case_a2())

def case_a3():
    """4 mountain paths."""
    layers = [V(50+i*50, 100+i*30, 400, 200, (0.3+i*0.1, 0.3+i*0.1, 0.3+i*0.1)) for i in range(4)]
    return H(layers, evts=evt(vectors=4, set_fill=4))
add("A3: 4 vectors", case_a3())

def case_a4():
    """0 vectors (empty)."""
    return H([], evts=evt(vectors=0, set_fill=0))
add("A4: 0 vectors (empty design)", case_a4())

def case_a5():
    """5 layered mountains."""
    layers = []
    for i in range(5):
        layers.append(V(50+i*30, 100+i*20, 500, 200, (0.2+i*0.1, 0.2+i*0.1, 0.2+i*0.1)))
    return H(layers, evts=evt(vectors=5, set_fill=5))
add("A5: 5 vectors layered", case_a5())

def case_a6():
    """2 vectors but 2nd doesn't overlap (separate)."""
    layers = [V(50, 100, 300, 200, DGRAY),
              V(700, 100, 200, 200, LGRAY)]
    return H(layers)
add("A6: 2 vectors but no overlap", case_a6())

def case_a7():
    """1 vector + 1 rectangle (rectangle isn't pen path)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              make_layer("rectangle", x=300, y=200, w=400, h=180, fill=LGRAY)]
    return H(layers, evts=evt(vectors=1, set_fill=2,
                              extras=[make_event("tool_change", before="pen", after="rectangle"),
                                      make_event("create_rectangle")]))
add("A7: 1 vector + 1 rectangle", case_a7())

def case_a8():
    """2 vectors + 2 rectangles + 2 ellipses (extras)."""
    layers = perfect_design()
    layers.append(make_layer("rectangle", x=10, y=10, w=80, h=20, fill=PINK))
    layers.append(make_layer("ellipse", x=900, y=10, w=80, h=80, fill=YELLOW))
    return H(layers, evts=evt(extras=[make_event("create_rectangle"),
                                      make_event("create_ellipse")]))
add("A8: 2 vectors + decorations (rect+ellipse)", case_a8())

def case_a9():
    """6 vectors very layered."""
    layers = []
    for i in range(6):
        layers.append(V(50+i*40, 100+i*20, 450, 200, (0.2+i*0.08, 0.2+i*0.08, 0.2+i*0.08)))
    return H(layers, evts=evt(vectors=6, set_fill=6))
add("A9: 6 vectors heavily layered", case_a9())

def case_a10():
    """Exactly 2 vectors (control / perfect)."""
    return H()
add("A10: 2 vectors perfect (control)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    """Both vectors same dark gray (not distinct)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(350, 200, 500, 200, DGRAY)]
    return H(layers)
add("B11: both vectors same gray", case_b11())

def case_b12():
    """Image fill on first vector."""
    layers = perfect_design()
    layers[0]["fills"] = [{"kind": "image", "src": "mountain.jpg", "fit": "cover",
                           "opacity": 1.0, "visible": True}]
    return H(layers)
add("B12: 1st vector image fill", case_b12())

def case_b13():
    """Both image fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "mountain.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: both image fills", case_b13())

def case_b14():
    """Stroke only on both (no fill)."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=DGRAY, weight=2)]
    return H(layers)
add("B14: stroke-only (no fill)", case_b14())

def case_b15():
    """Empty fills array."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B15: fills array empty", case_b15())

def case_b16():
    """Gradient fill."""
    layers = perfect_design()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 0.3, "g": 0.3, "b": 0.3, "a": 1}},
        {"position": 1, "color": {"r": 0.6, "g": 0.6, "b": 0.6, "a": 1}}],
        "opacity": 1.0, "visible": True}]
    return H(layers)
add("B16: 1st vector gradient fill", case_b16())

def case_b17():
    """Two near-identical grays (within tolerance)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(350, 200, 500, 200, NEAR_DGRAY1)]
    return H(layers)
add("B17: near-identical grays (within tol)", case_b17())

def case_b18():
    """Fill alpha=0 on first vector (invisible)."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: 1st vector fill alpha=0", case_b18())

def case_b19():
    """Fill opacity=0.1 (super transparent)."""
    layers = perfect_design()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: 1st vector opacity=0.1", case_b19())

def case_b20():
    """Stacked fills (first solid, rest gradient/image)."""
    layers = perfect_design()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 1, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True},
    ])
    return H(layers)
add("B20: 1st vector has 3 stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    """Both vectors massive (way bigger than frame)."""
    layers = [V(0, 0, 1500, 800, DGRAY),
              V(100, 100, 1400, 700, LGRAY)]
    return H(layers)
add("C21: both vectors way too big", case_c21())

def case_c22():
    """Both 1×1 degenerate."""
    layers = [V(100, 100, 1, 1, DGRAY),
              V(101, 101, 1, 1, LGRAY)]
    return H(layers)
add("C22: both vectors 1×1 degenerate", case_c22())

def case_c23():
    """1st vector tiny, 2nd huge."""
    layers = [V(100, 100, 5, 5, DGRAY),
              V(0, 0, 1000, 400, LGRAY)]
    return H(layers)
add("C23: tiny + huge mountain", case_c23())

def case_c24():
    """Extreme aspect ratio (very wide thin)."""
    layers = [V(0, 195, 1000, 10, DGRAY),
              V(0, 198, 1000, 5, LGRAY)]
    return H(layers)
add("C24: extreme thin horizontal lines", case_c24())

def case_c25():
    """Extreme aspect ratio (very tall thin)."""
    layers = [V(495, 0, 10, 400, DGRAY),
              V(498, 0, 5, 400, LGRAY)]
    return H(layers)
add("C25: extreme thin vertical lines", case_c25())

def case_c26():
    """Both vectors negative size? (resilience)."""
    layers = [V(100, 100, 0, 0, DGRAY),
              V(120, 120, 0, 0, LGRAY)]
    return H(layers)
add("C26: both vectors zero-size", case_c26())

def case_c27():
    """Vectors 50% of frame (reasonable)."""
    layers = [V(100, 100, 500, 200, DGRAY),
              V(400, 200, 500, 150, LGRAY)]
    return H(layers)
add("C27: 50% frame size (reasonable)", case_c27())

def case_c28():
    """1st 90% width, 2nd 10% width."""
    layers = [V(50, 100, 900, 250, DGRAY),
              V(450, 250, 100, 100, LGRAY)]
    return H(layers)
add("C28: 90% + 10% width vectors", case_c28())

def case_c29():
    """Just-inside-tolerance very small (10×10)."""
    layers = [V(100, 100, 10, 10, DGRAY),
              V(105, 105, 10, 10, LGRAY)]
    return H(layers)
add("C29: 10×10 vectors (just visible)", case_c29())

def case_c30():
    """Both vectors are entire frame."""
    layers = [V(0, 0, 1000, 400, DGRAY),
              V(0, 0, 1000, 400, LGRAY)]
    return H(layers)
add("C30: both = full frame", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    """Both off-frame to the right."""
    layers = [V(1500, 100, 500, 250, DGRAY),
              V(1700, 200, 500, 200, LGRAY)]
    return H(layers)
add("D31: both off-frame right", case_d31())

def case_d32():
    """Both off-frame above."""
    layers = [V(100, -500, 500, 250, DGRAY),
              V(300, -400, 500, 200, LGRAY)]
    return H(layers)
add("D32: both off-frame above", case_d32())

def case_d33():
    """1st in-frame, 2nd outside."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(2000, 100, 500, 200, LGRAY)]
    return H(layers)
add("D33: 2nd vector outside frame", case_d33())

def case_d34():
    """Both shifted negative (top-left off)."""
    layers = [V(-300, -200, 500, 250, DGRAY),
              V(-100, -100, 500, 200, LGRAY)]
    return H(layers)
add("D34: both shifted top-left off-frame", case_d34())

def case_d35():
    """Tucked in upper-left corner."""
    layers = [V(0, 0, 200, 100, DGRAY),
              V(50, 50, 200, 100, LGRAY)]
    return H(layers)
add("D35: tucked upper-left corner", case_d35())

def case_d36():
    """Vertically stacked, no horizontal overlap."""
    layers = [V(100, 50, 500, 100, DGRAY),
              V(100, 250, 500, 100, LGRAY)]
    return H(layers)
add("D36: stacked vertically (overlap may pass)", case_d36())

def case_d37():
    """Side by side, separated."""
    layers = [V(50, 100, 200, 250, DGRAY),
              V(700, 100, 200, 250, LGRAY)]
    return H(layers)
add("D37: side by side, no overlap", case_d37())

def case_d38():
    """Just barely overlapping (1px)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(599, 100, 500, 200, LGRAY)]
    return H(layers)
add("D38: just-touching at right edge", case_d38())

def case_d39():
    """Far apart corners."""
    layers = [V(0, 0, 100, 100, DGRAY),
              V(900, 300, 100, 100, LGRAY)]
    return H(layers)
add("D39: opposite corners (no overlap)", case_d39())

def case_d40():
    """Both in dead-center, perfectly stacked."""
    layers = [V(400, 150, 200, 100, DGRAY),
              V(400, 150, 200, 100, LGRAY)]
    return H(layers)
add("D40: identical bbox (full overlap)", case_d40())


# ─── E. Per-shape variants (vector orientation/rotation) ────────────
def case_e41():
    """1st vector rotated 45°."""
    layers = perfect_design()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1st vector rotated 45°", case_e41())

def case_e42():
    """2nd vector rotated 90°."""
    layers = perfect_design()
    layers[1]["rotation"] = 90
    return H(layers)
add("E42: 2nd vector rotated 90°", case_e42())

def case_e43():
    """Both rotated 180° (upside down)."""
    layers = perfect_design()
    layers[0]["rotation"] = 180
    layers[1]["rotation"] = 180
    return H(layers)
add("E43: both rotated 180°", case_e43())

def case_e44():
    """Both flipped horizontally (scaleX=-1)."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: both flipped horizontally", case_e44())

def case_e45():
    """1st vector mirrored vertically."""
    layers = perfect_design()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E45: 1st flipped vertically", case_e45())

def case_e46():
    """1st rotated 4° (under tol)."""
    layers = perfect_design()
    layers[0]["rotation"] = 4
    return H(layers)
add("E46: 1st rotated 4° (under tol)", case_e46())

def case_e47():
    """Random rotations on both."""
    layers = perfect_design()
    layers[0]["rotation"] = 30
    layers[1]["rotation"] = -30
    return H(layers)
add("E47: rotated +30°/-30°", case_e47())

def case_e48():
    """Vector with stroke instead (still a vector type)."""
    layers = perfect_design()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=DGRAY, weight=4)]
    return H(layers)
add("E48: 1st has stroke, no fill", case_e48())

def case_e49():
    """Identical vectors (clone)."""
    layers = [V(100, 100, 500, 250, DGRAY),
              V(100, 100, 500, 250, DGRAY)]
    return H(layers)
add("E49: identical clones (same color)", case_e49())

def case_e50():
    """1st vector points dictionary missing (degenerate)."""
    layers = perfect_design()
    layers[0]["w"] = 0
    layers[0]["h"] = 0
    return H(layers)
add("E50: 1st vector w=h=0", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    """Mountain in front bigger than mountain in back (wrong layering visual)."""
    layers = [V(300, 100, 200, 100, DGRAY),
              V(50, 80, 800, 300, LGRAY)]  # near is huge
    return H(layers)
add("F51: 'near' larger than 'far'", case_f51())

def case_f52():
    """Both same exact dimensions, slightly offset."""
    layers = [V(100, 100, 400, 200, DGRAY),
              V(120, 120, 400, 200, LGRAY)]
    return H(layers)
add("F52: identical dimensions, slight offset", case_f52())

def case_f53():
    """Mountains stacked vertically (not horizontally layered)."""
    layers = [V(100, 50, 600, 150, DGRAY),
              V(100, 200, 600, 150, LGRAY)]
    return H(layers)
add("F53: mountains stacked vertically", case_f53())

def case_f54():
    """Squashed flat mountains."""
    layers = [V(100, 350, 700, 30, DGRAY),
              V(150, 360, 700, 30, LGRAY)]
    return H(layers)
add("F54: squashed flat 30px tall", case_f54())

def case_f55():
    """Inverted (peaks point down) — checked via shape orientation."""
    layers = perfect_design()
    layers[0]["scaleY"] = -1
    layers[1]["scaleY"] = -1
    return H(layers)
add("F55: both inverted (scaleY=-1)", case_f55())

def case_f56():
    """1 mountain wraps the other (concentric)."""
    layers = [V(50, 50, 800, 350, DGRAY),
              V(300, 200, 200, 100, LGRAY)]
    return H(layers)
add("F56: small mountain inside big one", case_f56())

def case_f57():
    """Both at edge, touching corners."""
    layers = [V(50, 50, 200, 100, DGRAY),
              V(248, 148, 200, 100, LGRAY)]
    return H(layers)
add("F57: edge-corner touching", case_f57())

def case_f58():
    """Mountains overlap each other entirely."""
    layers = [V(200, 100, 400, 200, DGRAY),
              V(210, 110, 380, 180, LGRAY)]
    return H(layers)
add("F58: 2nd nested inside 1st", case_f58())

def case_f59():
    """Two small disjoint mountains."""
    layers = [V(100, 100, 100, 100, DGRAY),
              V(800, 200, 100, 100, LGRAY)]
    return H(layers)
add("F59: two disjoint small mountains", case_f59())

def case_f60():
    """Mountains touch at single point only."""
    layers = [V(100, 100, 300, 200, DGRAY),
              V(400, 300, 300, 200, LGRAY)]
    return H(layers)
add("F60: touch at corner only", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=400)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Frame within frame (nested)."""
    inner = make_frame(perfect_design(), w=900, h=350)
    outer = make_frame([inner], w=1000, h=400)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=1000, h=400)
    f2 = make_frame(perfect_design(), w=1000, h=400)
    return make_log([f1, f2], evt())
add("G63: 2 frames, design in 2nd", case_g63())

def case_g64():
    """Frame with stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=400)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    """Frame has image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=400, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())

def case_g66():
    """Frame way too big."""
    return H(frame_w=2000, frame_h=2000)
add("G66: frame 2000x2000", case_g66())

def case_g67():
    """Frame way too small (smaller than mountains)."""
    return H(frame_w=200, frame_h=100)
add("G67: frame 200x100 (smaller than vectors)", case_g67())

def case_g68():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1000, h=400)
    return make_log([frame], evt())
add("G68: frame translated", case_g68())

def case_g69():
    """No frame at all (vectors on page)."""
    return H(in_frame=False)
add("G69: no frame, vectors on page", case_g69())

def case_g70():
    """Frame near edge of canvas."""
    layers = perfect_design()
    frame = make_frame(layers, x=2000, y=2000, w=1000, h=400)
    return make_log([frame], evt())
add("G70: frame at (2000,2000)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    """Pen tool not used at all (vectors created via different mechanism)."""
    sem = [make_event("session_start"),
           make_event("create_vector"),
           make_event("create_vector"),
           make_event("set_fill_color"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H71: no tool_change to pen", case_h71())

def case_h72():
    """Used rectangle tool but vectors exist."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_vector"),
           make_event("create_vector"),
           make_event("set_fill_color"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H72: tool=rectangle but vectors created", case_h72())

def case_h73():
    """Pen used but only 1 create_vector emitted."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector"),
           make_event("set_fill_color"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H73: pen tool but only 1 create_vector", case_h73())

def case_h74():
    """Pen used but 0 create_vector events (deleted maybe)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("set_fill_color"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H74: pen tool but 0 create_vector events", case_h74())

def case_h75():
    """Many extras: undo/redo/move."""
    extras = [make_event("undo") for _ in range(20)] + \
             [make_event("redo") for _ in range(20)] + \
             [make_event("move_layer") for _ in range(20)]
    return H(evts=evt(extras=extras))
add("H75: many undo/redo/move", case_h75())

def case_h76():
    """Used align_layers."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H76: used align_layers", case_h76())

def case_h77():
    """Created and deleted a star."""
    extras = [make_event("tool_change", before="pen", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H77: created+deleted star", case_h77())

def case_h78():
    """Many duplicate session_end events."""
    extras = [make_event("session_end")] * 5
    return H(evts=evt(extras=extras))
add("H78: 5x session_end", case_h78())

def case_h79():
    """Pen tool used multiple times."""
    extras = [make_event("tool_change", before="pen", after="select"),
              make_event("tool_change", before="select", after="pen"),
              make_event("tool_change", before="pen", after="rectangle"),
              make_event("tool_change", before="rectangle", after="pen")]
    return H(evts=evt(extras=extras))
add("H79: pen toggled many times", case_h79())

def case_h80():
    """0 set_fill_color events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector"),
           make_event("create_vector")]
    return H(evts=sem)
add("H80: 0 set_fill_color events", case_h80())


# ─── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    """Vectors inside a group inside frame."""
    layers = perfect_design()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1000, h=400)
    return make_log([frame], evt())
add("I81: vectors in group in frame", case_i81())

def case_i82():
    """Each vector in its own frame."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=500, h=400)
    f2 = make_frame([house[1]], w=500, h=400)
    return make_log([f1, f2], evt())
add("I82: each vector in own frame", case_i82())

def case_i83():
    """Vectors inside a section."""
    layers = perfect_design()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 400,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: vectors in section (no frame)", case_i83())

def case_i84():
    """One vector inside frame, other on page."""
    layers = perfect_design()
    frame = make_frame([layers[0]], w=1000, h=400)
    return make_log([frame, layers[1]], evt())
add("I84: 1 vector in frame, 1 on page", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1000, h=400)
    f2 = make_frame([f3], w=1100, h=450)
    f1 = make_frame([f2], w=1200, h=500)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    """Vectors on page 2 (not 1)."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=400)
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
    """Vectors as children of a component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1000, "h": 400,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I87: vectors in component", case_i87())

def case_i88():
    """Vectors deeply nested via groups."""
    layers = perfect_design()
    g3 = {"id": "g3", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    frame = make_frame([g1], w=1000, h=400)
    return make_log([frame], evt())
add("I88: 3-deep group nesting", case_i88())

def case_i89():
    """Multiple frames, 1 vector each."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=1000, h=400)
    f2 = make_frame([house[1]], w=1000, h=400)
    f3 = make_frame([], w=1000, h=400)
    return make_log([f1, f2, f3], evt())
add("I89: 3 frames, 1 each (split)", case_i89())

def case_i90():
    """Vectors as siblings to frame on page."""
    layers = perfect_design()
    frame = make_frame([], w=1000, h=400)
    return make_log([frame, *layers], evt())
add("I90: empty frame + vectors as siblings", case_i90())


# ─── J. Bizarre / hard ──────────────────────────────────────────────
def case_j91():
    """Both vectors with 0 opacity (invisible)."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("J91: opacity=0 (invisible)", case_j91())

def case_j92():
    """Both visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J92: visible=False on layer", case_j92())

def case_j93():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J93: empty document", case_j93())

def case_j94():
    """Frame only, no vectors."""
    return H([])
add("J94: frame, no vectors", case_j94())

def case_j95():
    """Text label saying 'mountain' (no actual vector)."""
    text = make_layer("text", x=400, y=200, w=200, h=40, fill=DGRAY)
    text["content"] = "mountain"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'mountain' only", case_j95())

def case_j96():
    """Triangles (polygon, sides=3) instead of vectors."""
    layers = [make_layer("polygon", x=100, y=100, w=500, h=250, fill=DGRAY, sides=3),
              make_layer("polygon", x=300, y=200, w=500, h=200, fill=LGRAY, sides=3)]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_polygon"), make_event("create_polygon")]))
add("J96: 2 polygons (triangles) — no vectors", case_j96())

def case_j97():
    """Negative coordinates."""
    layers = [V(-300, -100, 500, 250, DGRAY),
              V(-100, -50, 500, 200, LGRAY)]
    return H(layers)
add("J97: negative coords", case_j97())

def case_j98():
    """Both vectors at exact same position+size."""
    layers = [V(200, 100, 400, 200, DGRAY),
              V(200, 100, 400, 200, LGRAY)]
    return H(layers)
add("J98: identical position+size", case_j98())

def case_j99():
    """1st vector huge, 2nd a tiny dot."""
    layers = [V(0, 0, 1000, 400, DGRAY),
              V(500, 200, 2, 2, LGRAY)]
    return H(layers)
add("J99: huge + 2x2 dot", case_j99())

def case_j100():
    """Perfect (control)."""
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

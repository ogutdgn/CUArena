"""100 edge cases for task 08 — runs all and prints a sorted score table.

Task 08 = two pen-tool S-curve waves with bezier handles, distinct blue 4px strokes.
Frame 1000x300.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
    DARK_GRAY, LIGHT_GRAY, BLACK, COBALT, DEEP_BLUE,
)
from tasks import task_08_water_waves as t
T = t.task

# Blue shades
BLUE1 = (0.20, 0.40, 0.85)   # primary blue
BLUE2 = (0.10, 0.30, 0.65)   # darker blue
BLUE3 = (0.40, 0.60, 0.95)   # lighter
NEAR_BLUE = (0.21, 0.40, 0.85)  # within tol of BLUE1


def evt(pen=True, vectors=2, set_stroke=2, extras=()):
    sem = [make_event("session_start")]
    if pen:
        sem.append(make_event("tool_change", before="select", after="pen"))
    for _ in range(vectors):
        sem.append(make_event("create_vector"))
    for _ in range(set_stroke):
        sem.append(make_event("set_stroke_color"))
    sem.extend(extras)
    return sem


def W(x, y, w, h, stroke_rgb=BLUE1, stroke_w=4, fill=None, **extra):
    """Wave helper: vector with stroke (and optional fill)."""
    strokes = [make_stroke(rgb=stroke_rgb, weight=stroke_w)] if stroke_rgb else []
    return make_layer("vector", x=x, y=y, w=w, h=h, fill=fill,
                      strokes=strokes, **extra)


def perfect_design():
    w1 = W(100, 100, 800, 120, BLUE1, 4)
    w2 = W(100, 150, 800, 120, BLUE2, 4)
    return [w1, w2]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1000, frame_h=300, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    return H([W(100, 150, 800, 100, BLUE1, 4)], evts=evt(vectors=1, set_stroke=1))
add("A1: only 1 wave", case_a1())

def case_a2():
    return H([], evts=evt(vectors=0, set_stroke=0))
add("A2: 0 waves", case_a2())

def case_a3():
    layers = perfect_design() + [W(100, 250, 800, 80, BLUE3, 4)]
    return H(layers, evts=evt(vectors=3, set_stroke=3))
add("A3: 3 waves", case_a3())

def case_a4():
    layers = [W(100, 50+i*50, 800, 40, (0.1+i*0.1, 0.3, 0.7), 4) for i in range(5)]
    return H(layers, evts=evt(vectors=5, set_stroke=5))
add("A4: 5 waves", case_a4())

def case_a5():
    """1 wave + 1 rectangle."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              make_layer("rectangle", x=100, y=200, w=800, h=80, fill=BLUE2)]
    return H(layers, evts=evt(vectors=1, set_stroke=2,
                              extras=[make_event("create_rectangle")]))
add("A5: 1 wave + 1 rectangle", case_a5())

def case_a6():
    """2 waves + 5 decorations."""
    layers = perfect_design()
    for i in range(5):
        layers.append(make_layer("ellipse", x=100+i*150, y=20, w=20, h=20, fill=YELLOW))
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]*5))
add("A6: 2 waves + 5 ellipse decorations", case_a6())

def case_a7():
    """6 waves heavily layered."""
    layers = []
    for i in range(6):
        layers.append(W(100, 50+i*30, 800, 100, (0.1+i*0.1, 0.3, 0.7), 4))
    return H(layers, evts=evt(vectors=6, set_stroke=6))
add("A7: 6 waves layered", case_a7())

def case_a8():
    """Just a stroke-less line (no stroke means no wave to render)."""
    layers = [W(100, 100, 800, 80, None, 0),
              W(100, 200, 800, 80, None, 0)]
    return H(layers)
add("A8: 2 vectors but no strokes", case_a8())

def case_a9():
    """0 vectors but 2 fills present (rectangles)."""
    layers = [make_layer("rectangle", x=100, y=100, w=800, h=80, fill=BLUE1),
              make_layer("rectangle", x=100, y=200, w=800, h=80, fill=BLUE2)]
    return H(layers, evts=evt(vectors=0, set_stroke=0,
                              extras=[make_event("create_rectangle")]*2))
add("A9: 2 rectangles (no vectors)", case_a9())

def case_a10():
    """Perfect (control)."""
    return H()
add("A10: 2 waves perfect (control)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    """Both same blue."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 200, 800, 80, BLUE1, 4)]
    return H(layers)
add("B11: both same blue", case_b11())

def case_b12():
    """Both near-identical (within tol)."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 200, 800, 80, NEAR_BLUE, 4)]
    return H(layers)
add("B12: near-identical blues (within tol)", case_b12())

def case_b13():
    """Both red strokes (not blue)."""
    layers = [W(100, 100, 800, 80, RED, 4),
              W(100, 200, 800, 80, (0.6, 0.1, 0.1), 4)]
    return H(layers)
add("B13: both red strokes", case_b13())

def case_b14():
    """Strokes have weight 1 (not 4)."""
    layers = [W(100, 100, 800, 80, BLUE1, 1),
              W(100, 200, 800, 80, BLUE2, 1)]
    return H(layers)
add("B14: stroke weight 1px", case_b14())

def case_b15():
    """Strokes have weight 12 (way bigger than 4)."""
    layers = [W(100, 100, 800, 80, BLUE1, 12),
              W(100, 200, 800, 80, BLUE2, 12)]
    return H(layers)
add("B15: stroke weight 12px", case_b15())

def case_b16():
    """Filled instead of stroked."""
    layers = [W(100, 100, 800, 80, None, 0, fill=BLUE1),
              W(100, 200, 800, 80, None, 0, fill=BLUE2)]
    return H(layers)
add("B16: solid fill instead of stroke", case_b16())

def case_b17():
    """One has stroke, other has fill."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 200, 800, 80, None, 0, fill=BLUE2)]
    return H(layers)
add("B17: 1 stroke + 1 fill", case_b17())

def case_b18():
    """Stroke is a gradient (not solid)."""
    layers = perfect_design()
    layers[0]["strokes"][0]["paint"] = {"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 0.2, "g": 0.4, "b": 0.85, "a": 1}},
        {"position": 1, "color": {"r": 0.1, "g": 0.3, "b": 0.65, "a": 1}}]}
    return H(layers)
add("B18: 1 stroke is gradient paint", case_b18())

def case_b19():
    """Stroke alpha=0 (invisible)."""
    layers = perfect_design()
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("B19: 1 stroke alpha=0", case_b19())

def case_b20():
    """Layer opacity=0 on both."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B20: opacity=0 on both", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    """Both waves tiny."""
    layers = [W(500, 100, 5, 5, BLUE1, 4),
              W(500, 200, 5, 5, BLUE2, 4)]
    return H(layers)
add("C21: tiny 5×5 waves", case_c21())

def case_c22():
    """Both waves 1×1."""
    layers = [W(500, 100, 1, 1, BLUE1, 4),
              W(500, 200, 1, 1, BLUE2, 4)]
    return H(layers)
add("C22: 1×1 waves", case_c22())

def case_c23():
    """Both waves huge (way past frame)."""
    layers = [W(0, 0, 2000, 800, BLUE1, 4),
              W(0, 0, 2000, 800, BLUE2, 4)]
    return H(layers)
add("C23: massive waves (>frame)", case_c23())

def case_c24():
    """Both extreme tall+thin."""
    layers = [W(495, 0, 10, 300, BLUE1, 4),
              W(498, 0, 10, 300, BLUE2, 4)]
    return H(layers)
add("C24: tall+thin (10×300)", case_c24())

def case_c25():
    """Stroke weight 4.4 (within tolerance 1.5)."""
    layers = [W(100, 100, 800, 80, BLUE1, 4.4),
              W(100, 200, 800, 80, BLUE2, 4.4)]
    return H(layers)
add("C25: stroke 4.4px (within tol)", case_c25())

def case_c26():
    """Stroke weight 6 (outside tolerance)."""
    layers = [W(100, 100, 800, 80, BLUE1, 6),
              W(100, 200, 800, 80, BLUE2, 6)]
    return H(layers)
add("C26: stroke 6px (outside tol)", case_c26())

def case_c27():
    """Wave 90% width."""
    layers = [W(50, 100, 900, 80, BLUE1, 4),
              W(50, 200, 900, 80, BLUE2, 4)]
    return H(layers)
add("C27: 90% width waves", case_c27())

def case_c28():
    """Wave 5% width."""
    layers = [W(450, 100, 50, 80, BLUE1, 4),
              W(450, 200, 50, 80, BLUE2, 4)]
    return H(layers)
add("C28: 5% width waves", case_c28())

def case_c29():
    """Both = full frame."""
    layers = [W(0, 0, 1000, 300, BLUE1, 4),
              W(0, 0, 1000, 300, BLUE2, 4)]
    return H(layers)
add("C29: both = full frame", case_c29())

def case_c30():
    """0×0 size."""
    layers = [W(500, 100, 0, 0, BLUE1, 4),
              W(500, 200, 0, 0, BLUE2, 4)]
    return H(layers)
add("C30: 0×0 sized", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    """Both off-frame right."""
    layers = [W(1500, 100, 800, 80, BLUE1, 4),
              W(1500, 200, 800, 80, BLUE2, 4)]
    return H(layers)
add("D31: both off-frame right", case_d31())

def case_d32():
    """Both above frame."""
    layers = [W(100, -200, 800, 80, BLUE1, 4),
              W(100, -100, 800, 80, BLUE2, 4)]
    return H(layers)
add("D32: both above frame", case_d32())

def case_d33():
    """1st in, 2nd outside frame."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(2000, 200, 800, 80, BLUE2, 4)]
    return H(layers)
add("D33: 2nd outside frame", case_d33())

def case_d34():
    """Negative coords."""
    layers = [W(-300, -100, 800, 80, BLUE1, 4),
              W(-100, 50, 800, 80, BLUE2, 4)]
    return H(layers)
add("D34: negative coords", case_d34())

def case_d35():
    """Tucked in corner."""
    layers = [W(0, 0, 200, 50, BLUE1, 4),
              W(50, 50, 200, 50, BLUE2, 4)]
    return H(layers)
add("D35: tucked corner", case_d35())

def case_d36():
    """Both stacked horizontally side-by-side (no vertical layering)."""
    layers = [W(50, 100, 400, 80, BLUE1, 4),
              W(550, 100, 400, 80, BLUE2, 4)]
    return H(layers)
add("D36: side-by-side (no layered)", case_d36())

def case_d37():
    """Centered vertically (waves overlap)."""
    layers = [W(100, 110, 800, 80, BLUE1, 4),
              W(100, 110, 800, 80, BLUE2, 4)]
    return H(layers)
add("D37: identical bbox stacked", case_d37())

def case_d38():
    """Far apart corners."""
    layers = [W(0, 0, 100, 50, BLUE1, 4),
              W(900, 250, 100, 50, BLUE2, 4)]
    return H(layers)
add("D38: opposite corners", case_d38())

def case_d39():
    """Just barely overlapping."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 175, 800, 80, BLUE2, 4)]
    return H(layers)
add("D39: just-barely-overlapping (5px)", case_d39())

def case_d40():
    """Off-frame to left."""
    layers = [W(-500, 100, 800, 80, BLUE1, 4),
              W(-500, 200, 800, 80, BLUE2, 4)]
    return H(layers)
add("D40: both off-frame left", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    """1st rotated 45°."""
    layers = perfect_design()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1st rotated 45°", case_e41())

def case_e42():
    """Both rotated 90°."""
    layers = perfect_design()
    layers[0]["rotation"] = 90
    layers[1]["rotation"] = 90
    return H(layers)
add("E42: both rotated 90°", case_e42())

def case_e43():
    """Both flipped horizontally."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E43: both scaleX=-1", case_e43())

def case_e44():
    """Both flipped vertically."""
    layers = perfect_design()
    for l in layers:
        l["scaleY"] = -1
    return H(layers)
add("E44: both scaleY=-1", case_e44())

def case_e45():
    """1st rotated 4° (under tolerance)."""
    layers = perfect_design()
    layers[0]["rotation"] = 4
    return H(layers)
add("E45: 1st rotated 4° (under tol)", case_e45())

def case_e46():
    """Both rotated 180°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("E46: both rotated 180°", case_e46())

def case_e47():
    """1st has dashed stroke."""
    layers = perfect_design()
    layers[0]["strokes"][0]["dash"] = {"dash": 6, "gap": 4}
    return H(layers)
add("E47: 1st has dashed stroke", case_e47())

def case_e48():
    """Stroke alignment 'inside'."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["alignment"] = "inside"
    return H(layers)
add("E48: stroke alignment=inside", case_e48())

def case_e49():
    """Both stroke alignment 'outside'."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("E49: stroke alignment=outside", case_e49())

def case_e50():
    """1st no stroke, 2nd ok."""
    layers = perfect_design()
    layers[0]["strokes"] = []
    return H(layers)
add("E50: 1st missing stroke", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    """Stroke 0px (invisible)."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["weight"] = 0
    return H(layers)
add("F51: stroke 0px", case_f51())

def case_f52():
    """1 wave with stroke, 1 with no stroke (just fill)."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 200, 800, 80, None, 0, fill=BLUE2)]
    return H(layers)
add("F52: 1 stroke + 1 fill (mixed)", case_f52())

def case_f53():
    """Stroke visible=False on both."""
    layers = perfect_design()
    for l in layers:
        l["strokes"][0]["visible"] = False
    return H(layers)
add("F53: strokes visible=False", case_f53())

def case_f54():
    """1 wave squished flat (1px tall)."""
    layers = perfect_design()
    layers[0]["h"] = 1
    return H(layers)
add("F54: 1 wave 1px tall", case_f54())

def case_f55():
    """Both waves 1px tall."""
    layers = perfect_design()
    layers[0]["h"] = 1
    layers[1]["h"] = 1
    return H(layers)
add("F55: both 1px tall (flat lines)", case_f55())

def case_f56():
    """1 inside 2 (concentric)."""
    layers = [W(100, 100, 800, 200, BLUE1, 4),
              W(200, 150, 600, 100, BLUE2, 4)]
    return H(layers)
add("F56: 1 nested in other", case_f56())

def case_f57():
    """Edge-touching only."""
    layers = [W(100, 100, 400, 80, BLUE1, 4),
              W(500, 100, 400, 80, BLUE2, 4)]
    return H(layers)
add("F57: side-by-side touching", case_f57())

def case_f58():
    """Both stroke=4 on a 1×1 vector (degenerate)."""
    layers = [W(500, 100, 1, 1, BLUE1, 4),
              W(500, 200, 1, 1, BLUE2, 4)]
    return H(layers)
add("F58: stroke 4 on 1×1 (no shape)", case_f58())

def case_f59():
    """Two distinct blues but BOTH same exact stroke weight."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 200, 800, 80, BLUE2, 4)]
    return H(layers)
add("F59: same stroke weight (control)", case_f59())

def case_f60():
    """1 has fill+stroke, 2 has just stroke."""
    layers = [W(100, 100, 800, 80, BLUE1, 4, fill=BLUE3),
              W(100, 200, 800, 80, BLUE2, 4)]
    return H(layers)
add("F60: 1 stroke+fill, 1 stroke", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=300)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Frame nested in frame."""
    inner = make_frame(perfect_design(), w=900, h=250)
    outer = make_frame([inner], w=1000, h=300)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """2 frames."""
    f1 = make_frame([], w=1000, h=300)
    f2 = make_frame(perfect_design(), w=1000, h=300)
    return make_log([f1, f2], evt())
add("G63: 2 frames, design in 2nd", case_g63())

def case_g64():
    """Frame has stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=300)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=300, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    return H(frame_w=2000, frame_h=600)
add("G66: frame 2000x600", case_g66())

def case_g67():
    return H(frame_w=400, frame_h=100)
add("G67: frame 400x100", case_g67())

def case_g68():
    """Frame 1010x310 (within tol)."""
    return H(frame_w=1010, frame_h=310)
add("G68: frame 1010x310 (within tol)", case_g68())

def case_g69():
    """No frame."""
    return H(in_frame=False)
add("G69: vectors on page (no frame)", case_g69())

def case_g70():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1000, h=300)
    return make_log([frame], evt())
add("G70: frame translated", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    """No pen tool used."""
    sem = [make_event("session_start"),
           make_event("create_vector"),
           make_event("create_vector"),
           make_event("set_stroke_color"),
           make_event("set_stroke_color")]
    return H(evts=sem)
add("H71: no tool_change to pen", case_h71())

def case_h72():
    """Tool=rectangle."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_vector"),
           make_event("create_vector"),
           make_event("set_stroke_color"),
           make_event("set_stroke_color")]
    return H(evts=sem)
add("H72: tool=rectangle but vectors", case_h72())

def case_h73():
    """0 create_vector events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    return H(evts=sem)
add("H73: 0 create_vector events", case_h73())

def case_h74():
    """Only 1 create_vector event."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector")]
    return H(evts=sem)
add("H74: 1 create_vector event", case_h74())

def case_h75():
    """100 undo events."""
    extras = [make_event("undo")] * 100
    return H(evts=evt(extras=extras))
add("H75: 100 undo events", case_h75())

def case_h76():
    """Used align tool."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H76: used align_layers", case_h76())

def case_h77():
    """Created a star."""
    extras = [make_event("tool_change", before="pen", after="star"),
              make_event("create_star")]
    return H(evts=evt(extras=extras))
add("H77: created a star (extra)", case_h77())

def case_h78():
    """Many duplicate session_end."""
    return H(evts=evt(extras=[make_event("session_end")]*5))
add("H78: 5x session_end", case_h78())

def case_h79():
    """Pen tool used many times."""
    extras = [make_event("tool_change", before="pen", after="select"),
              make_event("tool_change", before="select", after="pen"),
              make_event("tool_change", before="pen", after="rectangle"),
              make_event("tool_change", before="rectangle", after="pen")]
    return H(evts=evt(extras=extras))
add("H79: pen toggled many times", case_h79())

def case_h80():
    """0 set_stroke events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector"),
           make_event("create_vector")]
    return H(evts=sem)
add("H80: 0 set_stroke events", case_h80())


# ─── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_design()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1000, h=300)
    return make_log([frame], evt())
add("I81: vectors in group in frame", case_i81())

def case_i82():
    """Each in own frame."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=500, h=300)
    f2 = make_frame([house[1]], w=500, h=300)
    return make_log([f1, f2], evt())
add("I82: each in own frame", case_i82())

def case_i83():
    """Section instead of frame."""
    layers = perfect_design()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 300,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: vectors in section", case_i83())

def case_i84():
    """1 in frame, 1 on page."""
    layers = perfect_design()
    frame = make_frame([layers[0]], w=1000, h=300)
    return make_log([frame, layers[1]], evt())
add("I84: 1 in frame, 1 on page", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1000, h=300)
    f2 = make_frame([f3], w=1100, h=350)
    f1 = make_frame([f2], w=1200, h=400)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    """Page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1000, h=300)
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
    """Vectors in component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1000, "h": 300,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I87: vectors in component", case_i87())

def case_i88():
    """Deep group nesting."""
    layers = perfect_design()
    g3 = {"id": "g3", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id": "g1", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    frame = make_frame([g1], w=1000, h=300)
    return make_log([frame], evt())
add("I88: 3-deep group nesting", case_i88())

def case_i89():
    """3 frames split."""
    house = perfect_design()
    f1 = make_frame([house[0]], w=1000, h=300)
    f2 = make_frame([house[1]], w=1000, h=300)
    f3 = make_frame([], w=1000, h=300)
    return make_log([f1, f2, f3], evt())
add("I89: 3 frames split", case_i89())

def case_i90():
    """Empty frame + vectors as siblings."""
    layers = perfect_design()
    frame = make_frame([], w=1000, h=300)
    return make_log([frame, *layers], evt())
add("I90: empty frame + sibling vectors", case_i90())


# ─── J. Bizarre / hard ──────────────────────────────────────────────
def case_j91():
    """Both opacity=0."""
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
    return make_log([], [make_event("session_start")])
add("J93: empty document", case_j93())

def case_j94():
    return H([])
add("J94: frame, no vectors", case_j94())

def case_j95():
    """Text label 'wave'."""
    text = make_layer("text", x=400, y=200, w=200, h=40, fill=BLUE1)
    text["content"] = "wave"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'wave' only", case_j95())

def case_j96():
    """Replace vectors with rectangles."""
    layers = [make_layer("rectangle", x=100, y=100, w=800, h=80, fill=BLUE1,
                         strokes=[make_stroke(rgb=BLUE1, weight=4)]),
              make_layer("rectangle", x=100, y=200, w=800, h=80, fill=BLUE2,
                         strokes=[make_stroke(rgb=BLUE2, weight=4)])]
    return H(layers, evts=evt(vectors=0,
                              extras=[make_event("create_rectangle")]*2))
add("J96: 2 rectangles with strokes", case_j96())

def case_j97():
    """Negative coords."""
    layers = [W(-300, -100, 800, 80, BLUE1, 4),
              W(-100, -50, 800, 80, BLUE2, 4)]
    return H(layers)
add("J97: negative coords", case_j97())

def case_j98():
    """Identical bbox."""
    layers = [W(100, 100, 800, 80, BLUE1, 4),
              W(100, 100, 800, 80, BLUE2, 4)]
    return H(layers)
add("J98: identical position+size", case_j98())

def case_j99():
    """Huge wave + 2x2 dot."""
    layers = [W(0, 0, 1000, 300, BLUE1, 4),
              W(500, 200, 2, 2, BLUE2, 4)]
    return H(layers)
add("J99: huge + 2x2 dot", case_j99())

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

"""100 edge cases for task 05 — plus sign from 2 perpendicular red rectangles."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, RED, ORANGE, YELLOW, GREEN, CYAN, NAVY, MAGENTA, PINK, PURPLE,
    WHITE, BLACK, GOLD,
)
from tasks import task_05_red_heart_union as t
T = t.task

BLUE = (0.2, 0.4, 0.85)
GRAY = (0.5, 0.5, 0.5)


def evt(rect=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_plus(h_size=(200, 60), v_size=(60, 200), cx=500, cy=500):
    h = L("rectangle", cx-h_size[0]/2, cy-h_size[1]/2, h_size[0], h_size[1], RED)
    v = L("rectangle", cx-v_size[0]/2, cy-v_size[1]/2, v_size[0], v_size[1], RED)
    return [h, v]


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=False):
    """Default in_frame=False for task 05 (prompt doesn't require frame)."""
    if layers is None: layers = perfect_plus()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ────────────────────────────────────────────────────────
def case_a1():
    layers = perfect_plus()
    layers.append(L("rectangle", 200, 200, 60, 60, RED))
    return H(layers, evts=evt(rect=3))
add("A1: 3 rectangles (extra)", case_a1())

def case_a2():
    return H([perfect_plus()[0]], evts=evt(rect=1))
add("A2: 1 rectangle (horizontal only)", case_a2())

def case_a3():
    return H([perfect_plus()[1]], evts=evt(rect=1))
add("A3: 1 rectangle (vertical only)", case_a3())

def case_a4():
    return H([], evts=evt(rect=0))
add("A4: 0 rectangles", case_a4())

def case_a5():
    layers = perfect_plus() + perfect_plus()
    return H(layers, evts=evt(rect=4))
add("A5: 4 rectangles (doubled)", case_a5())

def case_a6():
    layers = perfect_plus()
    for i in range(8):
        layers.append(L("rectangle", 100+i*30, 100, 20, 20, RED))
    return H(layers, evts=evt(rect=10))
add("A6: 10 rectangles (8 extras)", case_a6())

def case_a7():
    layers = perfect_plus()
    layers.append(make_layer("ellipse", x=400, y=400, w=80, h=80, fill=RED))
    return H(layers, evts=evt(rect=2, extras=[make_event("create_ellipse")]))
add("A7: 2 rects + 1 ellipse extra", case_a7())

def case_a8():
    """5 rectangles all same color forming a complex shape."""
    return H([
        L("rectangle", 400, 470, 200, 60, RED),
        L("rectangle", 470, 400, 60, 200, RED),
        L("rectangle", 100, 100, 80, 80, RED),
        L("rectangle", 700, 100, 80, 80, RED),
        L("rectangle", 100, 700, 80, 80, RED),
    ], evts=evt(rect=5))
add("A8: 2 plus + 3 corner squares (5 total)", case_a8())

def case_a9():
    """2 horizontals (no vertical)."""
    return H([
        L("rectangle", 400, 470, 200, 60, RED),
        L("rectangle", 400, 350, 200, 60, RED),
    ])
add("A9: 2 horizontals (no vertical)", case_a9())

def case_a10():
    """2 verticals (no horizontal)."""
    return H([
        L("rectangle", 470, 400, 60, 200, RED),
        L("rectangle", 350, 400, 60, 200, RED),
    ])
add("A10: 2 verticals (no horizontal)", case_a10())


# ─── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    """Both blue (not red)."""
    layers = perfect_plus()
    for l in layers: l["fills"][0]["color"] = {"r":0.2, "g":0.4, "b":0.85, "a":1}
    return H(layers)
add("B11: both blue", case_b11())

def case_b12():
    """1 red, 1 blue (mixed)."""
    layers = perfect_plus()
    layers[1]["fills"][0]["color"] = {"r":0.2, "g":0.4, "b":0.85, "a":1}
    return H(layers)
add("B12: 1 red + 1 blue", case_b12())

def case_b13():
    """1 image fill."""
    layers = perfect_plus()
    layers[0]["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: 1 image fill", case_b13())

def case_b14():
    """All image fills."""
    layers = perfect_plus()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B14: all image fills", case_b14())

def case_b15():
    """Stroke-only (no fill)."""
    layers = perfect_plus()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=RED, weight=4)]
    return H(layers)
add("B15: stroke-only", case_b15())

def case_b16():
    """Empty fills."""
    layers = perfect_plus()
    for l in layers: l["fills"] = []
    return H(layers)
add("B16: empty fills arrays", case_b16())

def case_b17():
    """Both white."""
    layers = perfect_plus()
    for l in layers: l["fills"][0]["color"] = {"r":1, "g":1, "b":1, "a":1}
    return H(layers)
add("B17: both white", case_b17())

def case_b18():
    """1 gradient."""
    layers = perfect_plus()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":0,"b":0,"a":1}},
        {"position": 1, "color": {"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B18: 1 gradient fill", case_b18())

def case_b19():
    """Both alpha=0."""
    layers = perfect_plus()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: alpha=0", case_b19())

def case_b20():
    """Stacked fills."""
    layers = perfect_plus()
    for l in layers:
        l["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(layers)
add("B20: stacked fills", case_b20())


# ─── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """Both rectangles 200x200 (squares, no aspect)."""
    return H([L("rectangle", 400, 400, 200, 200, RED), L("rectangle", 400, 400, 200, 200, RED)])
add("C21: 2 squares 200x200", case_c21())

def case_c22():
    """Both 1x1 degenerate."""
    return H([L("rectangle", 500, 500, 1, 1, RED), L("rectangle", 500, 500, 1, 1, RED)])
add("C22: both 1x1", case_c22())

def case_c23():
    """Both rectangles same size 200x60 (both horizontal)."""
    return H([L("rectangle", 400, 460, 200, 60, RED), L("rectangle", 400, 480, 200, 60, RED)])
add("C23: both 200x60 (both horizontal)", case_c23())

def case_c24():
    """Both 60x200 (both vertical)."""
    return H([L("rectangle", 470, 400, 60, 200, RED), L("rectangle", 460, 400, 60, 200, RED)])
add("C24: both 60x200 (both vertical)", case_c24())

def case_c25():
    """One huge, one tiny."""
    return H([L("rectangle", 100, 100, 800, 50, RED), L("rectangle", 460, 400, 50, 100, RED)])
add("C25: 1 huge horizontal + 1 small vertical", case_c25())

def case_c26():
    """Aspect ratio 1.99 (just under 2)."""
    return H([L("rectangle", 400, 470, 119, 60, RED), L("rectangle", 470, 410, 60, 120, RED)])
add("C26: aspect 1.99 (under threshold)", case_c26())

def case_c27():
    """Aspect ratio 3.0 (well above threshold)."""
    return H([L("rectangle", 400, 470, 300, 60, RED), L("rectangle", 470, 350, 60, 300, RED)])
add("C27: aspect 5.0 (well above)", case_c27())

def case_c28():
    """Both 100x100 squares but differently positioned."""
    return H([L("rectangle", 400, 400, 100, 100, RED), L("rectangle", 500, 500, 100, 100, RED)])
add("C28: 2 squares positioned to look like + ", case_c28())

def case_c29():
    """Both rotated 90° (perpendicular)."""
    layers = [L("rectangle", 400, 470, 200, 60, RED),
              L("rectangle", 470, 400, 60, 200, RED)]
    return H(layers)
add("C29: perfect plus (control)", case_c29())

def case_c30():
    """Tiny tiny crosses."""
    return H([L("rectangle", 490, 495, 20, 10, RED), L("rectangle", 495, 490, 10, 20, RED)])
add("C30: tiny plus 10x20", case_c30())


# ─── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Misaligned (offset 50px)."""
    return H([L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 520, 350, 60, 200, RED)])
add("D31: rectangles offset (not centered)", case_d31())

def case_d32():
    """Both at left."""
    return H([L("rectangle", 100, 470, 200, 60, RED), L("rectangle", 170, 350, 60, 200, RED)])
add("D32: both shifted left", case_d32())

def case_d33():
    """1 at left, 1 at right (separate)."""
    return H([L("rectangle", 100, 460, 200, 60, RED), L("rectangle", 700, 360, 60, 200, RED)])
add("D33: 2 rects separated", case_d33())

def case_d34():
    """Centered but not crossing (diagonal)."""
    return H([L("rectangle", 100, 100, 200, 60, RED), L("rectangle", 700, 700, 60, 200, RED)])
add("D34: 2 rects diagonal apart", case_d34())

def case_d35():
    """Stacked on top of each other (same y)."""
    return H([L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 470, 350, 60, 200, RED)])
add("D35: perfect plus (control 2)", case_d35())

def case_d36():
    """Off-center but parallel (touching)."""
    return H([L("rectangle", 400, 480, 200, 60, RED), L("rectangle", 460, 400, 60, 200, RED)])
add("D36: off-center but valid plus", case_d36())

def case_d37():
    """Plus moved to corner."""
    return H([L("rectangle", 50, 100, 200, 60, RED), L("rectangle", 120, 50, 60, 200, RED)])
add("D37: plus in corner", case_d37())

def case_d38():
    """Both at exact center, same size (perfect plus shape from 2 squares)."""
    return H([L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 470, 400, 60, 200, RED)])
add("D38: perfect (control 3)", case_d38())

def case_d39():
    """Plus at far edge."""
    layers = perfect_plus(cx=2000, cy=2000)
    return H(layers)
add("D39: plus at (2000,2000) (far)", case_d39())

def case_d40():
    """Centers off by 4px (within tolerance)."""
    return H([L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 472, 400, 60, 200, RED)])
add("D40: centers off 2px (within tol)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────────
def case_e41():
    """Both rotated 45° (no longer cross)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 45
    return H(layers)
add("E41: both rotated 45°", case_e41())

def case_e42():
    """Horizontal rotated 90° (now vertical, both vertical)."""
    layers = perfect_plus()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: horizontal rotated 90° (becomes vertical)", case_e42())

def case_e43():
    """Vertical rotated 90° (now horizontal, both horizontal)."""
    layers = perfect_plus()
    layers[1]["rotation"] = 90
    return H(layers)
add("E43: vertical rotated 90° (becomes horizontal)", case_e43())

def case_e44():
    """Both scaleX=-1."""
    layers = perfect_plus()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("E44: both scaleX=-1", case_e44())

def case_e45():
    """Both rotated 4° (just over 2 tol)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 4
    return H(layers)
add("E45: both rotated 4°", case_e45())

def case_e46():
    """Both cornerRadius=30 (rounded plus)."""
    layers = perfect_plus()
    for l in layers: l["cornerRadius"] = 30
    return H(layers)
add("E46: both cornerRadius=30", case_e46())

def case_e47():
    """Both rotated 1° (within tol)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 1
    return H(layers)
add("E47: both rotated 1° (within tol)", case_e47())

def case_e48():
    """Both scaleY=-1."""
    layers = perfect_plus()
    for l in layers: l["scaleY"] = -1
    return H(layers)
add("E48: both scaleY=-1", case_e48())

def case_e49():
    """Both rotated 360° (≡ 0)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 360
    return H(layers)
add("E49: both rotated 360°", case_e49())

def case_e50():
    """Both rotated 180° (still a plus)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 180
    return H(layers)
add("E50: both rotated 180° (still plus)", case_e50())


# ─── F. Subcomponent variants ─────────────────────────────────────────
def case_f51():
    """1 rectangle + 1 ellipse forming plus shape."""
    layers = [L("rectangle", 400, 470, 200, 60, RED),
              make_layer("ellipse", x=470, y=400, w=60, h=200, fill=RED)]
    sem = evt(rect=1, extras=[make_event("tool_change", before="rectangle", after="ellipse"),
                                make_event("create_ellipse")])
    return H(layers, evts=sem)
add("F51: 1 rect + 1 ellipse plus", case_f51())

def case_f52():
    """Both rectangles same wide horizontal (no plus)."""
    return H([L("rectangle", 400, 460, 200, 80, RED), L("rectangle", 400, 480, 200, 80, RED)])
add("F52: 2 wide rects stacked", case_f52())

def case_f53():
    """Plus has 0px horizontal width (degenerate)."""
    return H([L("rectangle", 500, 500, 0, 60, RED), L("rectangle", 470, 400, 60, 200, RED)])
add("F53: horizontal rect width=0", case_f53())

def case_f54():
    """Plus with extra 3 horizontals (asterisk-like)."""
    layers = perfect_plus()
    layers.append(L("rectangle", 400, 480, 200, 50, RED))
    return H(layers, evts=evt(rect=3))
add("F54: 3 horizontals + 1 vertical", case_f54())

def case_f55():
    """Plus with very tiny vertical (1×200)."""
    return H([L("rectangle", 400, 470, 200, 60, RED), L("rectangle", 499, 400, 1, 200, RED)])
add("F55: vertical width=1", case_f55())

def case_f56():
    """Both as long thin lines."""
    return H([L("rectangle", 400, 499, 200, 1, RED), L("rectangle", 499, 400, 1, 200, RED)])
add("F56: 2 lines (1px wide)", case_f56())

def case_f57():
    """Plus + 2 more rectangles forming X (extras)."""
    layers = perfect_plus()
    layers.append(L("rectangle", 400, 400, 200, 30, RED, rotation=45))
    layers.append(L("rectangle", 400, 400, 200, 30, RED, rotation=-45))
    return H(layers, evts=evt(rect=4))
add("F57: plus + 2 diagonals", case_f57())

def case_f58():
    """Plus with stroke-only horizontal."""
    layers = perfect_plus()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=RED, weight=4)]
    return H(layers)
add("F58: 1 stroke-only horizontal", case_f58())

def case_f59():
    """Plus but rectangles touching but not centered."""
    return H([L("rectangle", 400, 200, 200, 60, RED), L("rectangle", 470, 260, 60, 200, RED)])
add("F59: T-shape (touching but not centered)", case_f59())

def case_f60():
    """Plus but with strange aspect ratios (3:1 each)."""
    return H([L("rectangle", 400, 470, 200, 67, RED), L("rectangle", 467, 400, 67, 200, RED)])
add("F60: aspect 3:1 each", case_f60())


# ─── G. Frame variants (although task doesn't require frame) ──────────
def case_g61():
    """Plus inside a frame."""
    return H(in_frame=True)
add("G61: plus inside a frame", case_g61())

def case_g62():
    """Plus inside nested frames."""
    layers = perfect_plus()
    inner = make_frame(layers, w=900, h=900)
    outer = make_frame([inner], w=1000, h=1000)
    return make_log([outer], evt())
add("G62: plus in nested frames", case_g62())

def case_g63():
    """2 frames, plus split: 1 in each."""
    layers = perfect_plus()
    f1 = make_frame([layers[0]], w=500, h=500)
    f2 = make_frame([layers[1]], w=500, h=500)
    return make_log([f1, f2], evt())
add("G63: plus split across 2 frames", case_g63())

def case_g64():
    """Frame rotated 45° (with plus inside)."""
    layers = perfect_plus()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G64: frame rotated 45°", case_g64())

def case_g65():
    """Plus inside group inside frame."""
    layers = perfect_plus()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([g], w=900, h=900)
    return make_log([frame], evt())
add("G65: plus in group in frame", case_g65())

def case_g66():
    """Plus on page (no frame)."""
    return H(in_frame=False)
add("G66: plus on page (no frame, default)", case_g66())

def case_g67():
    """Plus inside section."""
    layers = perfect_plus()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":900,"h":900,"fills":[],"children":layers}
    return make_log([section], evt())
add("G67: plus in section", case_g67())

def case_g68():
    """Plus inside component."""
    layers = perfect_plus()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("G68: plus in component", case_g68())

def case_g69():
    """Plus with negative coords (off-frame)."""
    layers = perfect_plus(cx=-500, cy=-500)
    return H(layers)
add("G69: plus at negative coords", case_g69())

def case_g70():
    """Plus on page 2."""
    layers = perfect_plus()
    p1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    p2 = {"id":"p2","children":layers,"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[p1,p2]}}}
add("G70: plus on page 2", case_g70())


# ─── H. Tools / events ────────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())

def case_h73():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 2)
    return H(evts=sem)
add("H73: no tool_change", case_h73())

def case_h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_rectangle")] * 2)
    return H(evts=sem)
add("H74: ellipse tool", case_h74())

def case_h75():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")] * 2)
    return H(evts=sem)
add("H75: pen tool", case_h75())

def case_h76():
    sem = evt()
    sem.extend([make_event("delete") for _ in range(3)])
    return H(evts=sem)
add("H76: 2 creates + 3 deletes", case_h76())

def case_h77():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    return H(evts=sem)
add("H77: 0 create_rectangle", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x"),
                                make_event("align_layers", axis="center_y")]))
add("H78: 2 align events used", case_h78())

def case_h79():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute_layers used", case_h79())

def case_h80():
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H80: 5 session_end", case_h80())


# ─── I. Hierarchy ─────────────────────────────────────────────────────
def case_i81():
    """In group on page (no frame)."""
    layers = perfect_plus()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([g], evt())
add("I81: plus in group (no frame)", case_i81())

def case_i82():
    """Each rect in own frame."""
    layers = perfect_plus()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("I82: each rect in own frame", case_i82())

def case_i83():
    """Section."""
    layers = perfect_plus()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":900,"h":900,"fills":[],"children":layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    """Both in nested groups."""
    layers = perfect_plus()
    g1 = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    g2 = {"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g1]}
    return make_log([g2], evt())
add("I84: in nested groups", case_i84())

def case_i85():
    """Plus inside component."""
    layers = perfect_plus()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I85: plus in component", case_i85())

def case_i86():
    """3-deep nested groups."""
    layers = perfect_plus()
    g3 = {"id":"g3","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    g2 = {"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g3]}
    g1 = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g2]}
    return make_log([g1], evt())
add("I86: 3-deep nested groups", case_i86())

def case_i87():
    """Plus on page 2."""
    layers = perfect_plus()
    p1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    p2 = {"id":"p2","children":layers,"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[p1,p2]}}}
add("I87: plus on page 2", case_i87())

def case_i88():
    """Plus rotated 45° (nested in group)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 45
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([g], evt())
add("I88: rotated plus in group", case_i88())

def case_i89():
    """Page with text 'plus'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=RED)
    text["content"] = "plus"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("I89: text 'plus' (no shapes)", case_i89())

def case_i90():
    """Plus inside instance."""
    layers = perfect_plus()
    inst = {"id":"i1","type":"instance","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("I90: plus in instance", case_i90())


# ─── J. Bizarre ───────────────────────────────────────────────────────
def case_j91():
    """Both scaleX=-1."""
    layers = perfect_plus()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J91: both scaleX=-1", case_j91())

def case_j92():
    """Empty doc."""
    return make_log([], [make_event("session_start")])
add("J92: empty document", case_j92())

def case_j93():
    """Plus with stars."""
    layers = [make_layer("star", x=400, y=470, w=200, h=60, fill=RED, points=4),
              make_layer("star", x=470, y=400, w=60, h=200, fill=RED, points=4)]
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 2)
    return H(layers, evts=sem)
add("J93: 2 stars (no rectangles)", case_j93())

def case_j94():
    """Both rectangles same size 60x60 (looks like 1 square)."""
    return H([L("rectangle", 470, 470, 60, 60, RED), L("rectangle", 470, 470, 60, 60, RED)])
add("J94: 2 squares 60x60 stacked", case_j94())

def case_j95():
    """Plus with 200x200 squares (no aspect)."""
    return H([L("rectangle", 400, 470, 200, 200, RED), L("rectangle", 470, 400, 200, 200, RED)])
add("J95: 2 200x200 squares (no aspect mix)", case_j95())

def case_j96():
    """Plus with horizontal 200x60 and vertical 60x200, stacked at exact same point."""
    return H(perfect_plus())
add("J96: perfect plus (control)", case_j96())

def case_j97():
    """1 horizontal but bizarre size 1×200 (still vertical aspect)."""
    return H([L("rectangle", 200, 200, 100, 100, RED), L("rectangle", 1, 1, 1, 200, RED)])
add("J97: 1 square + 1 vertical line", case_j97())

def case_j98():
    """Plus rotated 45° (still cross visually)."""
    layers = perfect_plus()
    for l in layers: l["rotation"] = 45
    return H(layers)
add("J98: plus rotated 45°", case_j98())

def case_j99():
    """Plus made of 2 stars rotated 90°."""
    layers = perfect_plus()
    layers[0]["rotation"] = 30
    layers[1]["rotation"] = 30
    return H(layers)
add("J99: both rotated 30°", case_j99())

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

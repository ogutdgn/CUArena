"""100 edge cases for task 26 — 5 same-size squares in horizontal row, each
filled a different brand color."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_26" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
# Brand palette: 1 primary + 4 supports
BRAND_PRIMARY  = (0.20, 0.45, 0.85)
BRAND_RED      = (0.90, 0.15, 0.20)
BRAND_GREEN    = (0.15, 0.70, 0.40)
BRAND_YELLOW   = (1.00, 0.85, 0.10)
BRAND_PURPLE   = (0.55, 0.30, 0.80)


def evt(rect=5, set_fill=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_squares(n=5, w=80, h=80, gap=16, colors=None, y=400, x0=200):
    colors = colors or [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE,
                          PINK, CYAN, GOLD, NAVY]
    layers = []
    for i in range(n):
        layers.append(L("rectangle", x0+i*(w+gap), y, w, h, colors[i % len(colors)]))
    return layers


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_squares()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def a1(): return H(perfect_squares(n=6), evts=evt(rect=6))
add("A1: 6 squares", a1())

def a2(): return H(perfect_squares(n=4), evts=evt(rect=4))
add("A2: 4 squares", a2())

def a3(): return H(perfect_squares(n=10), evts=evt(rect=10))
add("A3: 10 squares (doubled)", a3())

def a4(): return H(perfect_squares(n=2), evts=evt(rect=2))
add("A4: 2 squares", a4())

def a5(): return H(perfect_squares(n=0), evts=evt(rect=0, set_fill=0))
add("A5: 0 squares", a5())

def a6(): return H(perfect_squares(n=1), evts=evt(rect=1))
add("A6: 1 square", a6())

def a7():
    layers = perfect_squares() + [L("ellipse", 1000, 400, 80, 80, RED)]
    return H(layers, evts=evt(rect=5))
add("A7: 5 squares + 1 ellipse", a7())

def a8():
    """5 squares but mixed types (4 rects + 1 ellipse)."""
    layers = perfect_squares(n=4) + [
        make_layer("ellipse", x=584, y=400, w=80, h=80, fill=BRAND_PURPLE)
    ]
    return H(layers, evts=evt(rect=4))
add("A8: 4 rects + 1 ellipse", a8())

def a9():
    """5 squares + 5 random rects."""
    layers = perfect_squares()
    for i in range(5):
        layers.append(L("rectangle", 100+i*40, 100, 40, 40, RED))
    return H(layers, evts=evt(rect=10))
add("A9: 5 squares + 5 small rects", a9())

def a10(): return H(perfect_squares(), evts=evt(rect=0))
add("A10: 5 squares but 0 create events", a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def b11():
    """All same color."""
    return H(perfect_squares(colors=[BRAND_PRIMARY]*5))
add("B11: all 5 same primary blue", b11())

def b12():
    return H()
add("B12: 5 distinct colors (control)", b12())

def b13():
    layers = perfect_squares()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: image fills", b13())

def b14():
    layers = perfect_squares()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
            {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],
            "opacity":1,"visible":True}]
    return H(layers)
add("B14: gradient fills", b14())

def b15():
    layers = perfect_squares()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BRAND_PRIMARY, weight=2)]
    return H(layers)
add("B15: stroke-only", b15())

def b16():
    layers = perfect_squares()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B16: empty fills", b16())

def b17():
    """5 near-identical colors (within 0.05 tol)."""
    near = [(0.20,0.45,0.85),(0.21,0.45,0.85),(0.20,0.46,0.85),
            (0.20,0.45,0.86),(0.21,0.46,0.86)]
    return H(perfect_squares(colors=near))
add("B17: 5 near-identical colors", b17())

def b18():
    layers = perfect_squares()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: alpha=0 on all", b18())

def b19():
    layers = perfect_squares()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fillOpacity=0.05 on all", b19())

def b20():
    layers = perfect_squares()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B20: layer.opacity=0 on all", b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def c21(): return H(perfect_squares(w=200, h=200))
add("C21: huge squares 200×200", c21())

def c22(): return H(perfect_squares(w=10, h=10))
add("C22: tiny 10×10", c22())

def c23():
    """Each square different size."""
    layers = []
    cur = 200
    for i, w in enumerate([60, 80, 100, 120, 140]):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", cur, 400, w, w, c))
        cur += w + 16
    return H(layers)
add("C23: 5 squares all different sizes", c23())

def c24():
    """Squares not square (rectangles 80×40)."""
    return H(perfect_squares(w=80, h=40))
add("C24: 80×40 (rectangle, not square)", c24())

def c25(): return H(perfect_squares(w=1, h=1))
add("C25: 1×1 (degenerate)", c25())

def c26():
    """Squares 78×82 (within 2px tol)."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 200+i*96, 400, 78, 82, c))
    return H(layers)
add("C26: 78×82 within tol", c26())

def c27():
    """Squares 80×80 with one being 100×100."""
    layers = perfect_squares()
    layers[2]["w"] = 100; layers[2]["h"] = 100
    return H(layers)
add("C27: 1 oversized square", c27())

def c28():
    """All squares 30×30 (small)."""
    return H(perfect_squares(w=30, h=30))
add("C28: 30×30 small", c28())

def c29():
    """All squares 200×200 + bigger gap."""
    return H(perfect_squares(w=200, h=200, gap=30))
add("C29: 200×200 squares", c29())

def c30():
    """Squares are tall rects 40×120."""
    return H(perfect_squares(w=40, h=120))
add("C30: 40×120 (tall, not square)", c30())


# ─── D. Position ────────────────────────────────────────────────────
def d31():
    """Vertical column of squares."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 200, 100+i*100, 80, 80, c))
    return H(layers)
add("D31: vertical column", d31())

def d32():
    """3x2 grid (5 cells)."""
    coords = [(200,200),(300,200),(400,200),(200,300),(300,300)]
    layers = []
    for i, (x,y) in enumerate(coords):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", x, y, 80, 80, c))
    return H(layers)
add("D32: 3x2 grid", d32())

def d33():
    layers = perfect_squares()
    for i, l in enumerate(layers):
        l["y"] += [0, 50, -30, 100, -60][i]
    return H(layers)
add("D33: random y baselines", d33())

def d34():
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 600, 400, 80, 80, c))
    return H(layers)
add("D34: all overlapping at one point", d34())

def d35():
    layers = perfect_squares()
    for l in layers:
        l["x"] += 1500
    return H(layers)
add("D35: off-frame right", d35())

def d36():
    import random; random.seed(3)
    layers = perfect_squares()
    for l in layers:
        l["x"] = random.randint(0, 1100)
        l["y"] = random.randint(0, 700)
    return H(layers)
add("D36: random scatter", d36())

def d37():
    layers = perfect_squares()
    layers[1]["y"] += 2  # within 3 tol
    return H(layers)
add("D37: 2px y diff (within tol)", d37())

def d38():
    layers = perfect_squares()
    layers[1]["y"] += 5
    return H(layers)
add("D38: 5px y diff (over tol)", d38())

def d39():
    return H(perfect_squares(gap=0))
add("D39: gap=0", d39())

def d40():
    return H(perfect_squares(gap=300))
add("D40: gap=300", d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def e41():
    layers = perfect_squares()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1 square rotated 45°", e41())

def e42():
    layers = perfect_squares()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E42: all rotated 90°", e42())

def e43():
    layers = perfect_squares()
    for l in layers:
        l["rotation"] = 1.5
    return H(layers)
add("E43: all rotated 1.5° (under tol)", e43())

def e44():
    layers = perfect_squares()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: all scaleX=-1", e44())

def e45():
    layers = perfect_squares()
    layers[2]["scaleY"] = -1
    return H(layers)
add("E45: 1 square scaleY=-1", e45())

def e46():
    """All squares with cornerRadius=999 (circles)."""
    layers = perfect_squares()
    for l in layers:
        l["cornerRadius"] = 999
    return H(layers)
add("E46: cornerRadius=999 (circular)", e46())

def e47():
    """All ellipses."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(make_layer("ellipse", x=200+i*96, y=400, w=80, h=80, fill=c))
    return H(layers, evts=evt(rect=0))
add("E47: 5 ellipses", e47())

def e48():
    """All polygons (4-sided squares)."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(make_layer("polygon", x=200+i*96, y=400, w=80, h=80, fill=c, sides=4))
    return H(layers, evts=evt(rect=0))
add("E48: 5 polygons", e48())

def e49():
    """All squares with cornerRadius=20 (rounded)."""
    layers = perfect_squares()
    for l in layers:
        l["cornerRadius"] = 20
    return H(layers)
add("E49: cornerRadius=20", e49())

def e50():
    """Each square has different rotation."""
    layers = perfect_squares()
    for i, l in enumerate(layers):
        l["rotation"] = i*15
    return H(layers)
add("E50: rotations 0,15,30,45,60", e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def f51():
    layers = perfect_squares()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=NAVY, weight=2)]
    return H(layers)
add("F51: squares w/ stroke", f51())

def f52():
    layers = perfect_squares()
    for l in layers:
        l["effects"] = [{"kind":"drop_shadow","x":0,"y":2,"blur":4,"spread":0,
                          "color":{"r":0,"g":0,"b":0,"a":0.25},"visible":True}]
    return H(layers)
add("F52: w/ shadow", f52())

def f53():
    """1 square different size."""
    layers = perfect_squares()
    layers[2]["w"] = 60; layers[2]["h"] = 60
    return H(layers)
add("F53: 1 square 60×60", f53())

def f54():
    """5 squares overlapping."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 200+i*40, 400, 80, 80, c))
    return H(layers)
add("F54: 5 overlapping squares", f54())

def f55():
    layers = perfect_squares()
    for l in layers:
        l["x"] -= 500
    return H(layers)
add("F55: off-frame left", f55())

def f56():
    """4 in row + 1 stacked."""
    layers = []
    for i in range(4):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW][i]
        layers.append(L("rectangle", 200+i*96, 400, 80, 80, c))
    layers.append(L("rectangle", 200, 500, 80, 80, BRAND_PURPLE))
    return H(layers)
add("F56: 4 in row + 1 below", f56())

def f57():
    """5 squares in arc."""
    import math
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        ang = math.radians(-60 + i*30)
        x = 600 + 200*math.cos(ang) - 40
        y = 600 + 200*math.sin(ang) - 40
        layers.append(L("rectangle", x, y, 80, 80, c))
    return H(layers)
add("F57: 5 squares in arc", f57())

def f58():
    return H(perfect_squares(y=0))
add("F58: y=0 (frame top)", f58())

def f59():
    """Gap variance within tol."""
    layers = []
    cur = 200
    gaps = [16, 14, 18, 16]
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", cur, 400, 80, 80, c))
        if i < 4:
            cur += 80 + gaps[i]
    return H(layers)
add("F59: gap variance within tol", f59())

def f60():
    """Big gap on last pair."""
    layers = []
    cur = 200
    gaps = [16, 16, 16, 80]
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", cur, 400, 80, 80, c))
        if i < 4:
            cur += 80 + gaps[i]
    return H(layers)
add("F60: 80px gap on last pair", f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def g61(): return H()
add("G61: perfect frame", g61())

def g62(): return H(frame_w=800, frame_h=600)
add("G62: frame 800×600", g62())

def g63(): return H(in_frame=False)
add("G63: squares on page", g63())

def g64():
    layers = perfect_squares()
    f1 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([], w=600, h=400, x=1300)
    return make_log([f1, f2], evt())
add("G64: 2 frames", g64())

def g65():
    layers = perfect_squares()
    inner = make_frame(layers, w=800, h=400)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G65: nested frame", g65())

def g66():
    layers = perfect_squares()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G66: frame rotated", g66())

def g67():
    layers = perfect_squares()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    layers = perfect_squares()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G68: frame stroked", g68())


# ─── H. Tools / events ──────────────────────────────────────────────
def h69(): return H(evts=evt(extras=[make_event("undo")]*20))
add("H69: 20 undos", h69())

def h70(): return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H70: align event", h70())

def h71():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")]*5)
    sem.extend([make_event("set_fill_color")]*5)
    return H(evts=sem)
add("H71: 0 tool_change", h71())

def h72():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")]*5)
    sem.extend([make_event("set_fill_color")]*5)
    return H(evts=sem)
add("H72: pen tool", h72())

def h73(): return H(evts=evt(rect=8))
add("H73: rect=8", h73())

def h74(): return H(evts=evt(extras=[make_event("move_layer")]*40))
add("H74: 40 moves", h74())

def h75(): return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H75: distribute event", h75())

def h76():
    extras = [make_event("create_rectangle"), make_event("delete")]*3
    return H(evts=evt(extras=extras))
add("H76: 3 created+deleted", h76())

def h77(): return H(evts=evt() + [make_event("session_end")]*5)
add("H77: 5 session_end", h77())

def h78(): return H(evts=evt(set_fill=50))
add("H78: 50 set_fill", h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def i79():
    layers = perfect_squares()
    g = {"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("I79: in group in frame", i79())

def i80():
    layers = perfect_squares()
    f1 = make_frame(layers[:3], w=640, h=832)
    f2 = make_frame(layers[3:], w=640, h=832, x=700)
    return make_log([f1, f2], evt())
add("I80: split across 2 frames", i80())

def i81():
    layers = perfect_squares()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("I81: in section", i81())

def i82():
    layers = perfect_squares()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I82: 3-deep nested", i82())

def i83():
    layers = perfect_squares()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I83: on page 2", i83())

def i84():
    layers = perfect_squares()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I84: in component", i84())

def i85():
    layers = perfect_squares()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("I85: in instance", i85())


# ─── J. Bizarre ──────────────────────────────────────────────────────
def j86():
    layers = perfect_squares()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J86: all scaleX=-1", j86())

def j87():
    layers = perfect_squares()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("J87: all rotated 180°", j87())

def j88():
    """5 squares piled at one position."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 600, 400, 80, 80, c))
    return H(layers)
add("J88: 5 squares piled", j88())

def j89():
    return make_log([], [make_event("session_start")])
add("J89: empty doc", j89())

def j90(): return H([])
add("J90: frame only", j90())

def j91():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "color row"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'color row'", j91())

def j92():
    """5 stars."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(make_layer("star", x=200+i*96, y=400, w=80, h=80,
                                  fill=c, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0))
add("J92: 5 stars", j92())

def j93():
    layers = perfect_squares()
    for l in layers:
        l["y"] -= 1500
    return H(layers)
add("J93: negative y", j93())

def j94():
    """All 5 = full frame size."""
    layers = []
    for i in range(5):
        c = [BRAND_PRIMARY, BRAND_RED, BRAND_GREEN, BRAND_YELLOW, BRAND_PURPLE][i]
        layers.append(L("rectangle", 0, 0, 1280, 832, c))
    return H(layers)
add("J94: 5 full-frame", j94())

def j95(): return H(perfect_squares(w=1, h=1))
add("J95: 1×1 squares", j95())

def j96(): return H()
add("J96: perfect (control)", j96())


# ─── Run ────────────────────────────────────────────────────────────
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

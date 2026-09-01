"""100 edge cases for task 25 — 3 identical 160×40 rectangles in horizontal row,
all same color, consistent spacing, shared y-baseline."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_25" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
BUTTON_COLOR = (0.20, 0.45, 0.85)   # primary blue


def evt(rect=3, set_fill=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_buttons(n=3, w=160, h=40, gap=12, color=BUTTON_COLOR, y=300, x0=200):
    layers = []
    for i in range(n):
        layers.append(L("rectangle", x0 + i*(w+gap), y, w, h, color))
    return layers


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_buttons()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def a1(): return H(perfect_buttons(n=4), evts=evt(rect=4))
add("A1: 4 buttons (extra)", a1())

def a2(): return H(perfect_buttons(n=2), evts=evt(rect=2))
add("A2: 2 buttons (missing)", a2())

def a3(): return H(perfect_buttons(n=6), evts=evt(rect=6))
add("A3: 6 buttons (doubled)", a3())

def a4(): return H(perfect_buttons(n=1), evts=evt(rect=1))
add("A4: 1 button", a4())

def a5(): return H(perfect_buttons(n=0), evts=evt(rect=0, set_fill=0))
add("A5: 0 buttons", a5())

def a6():
    layers = perfect_buttons(n=2) + [L("ellipse", 600, 300, 160, 40, BUTTON_COLOR)]
    return H(layers, evts=evt(rect=2))
add("A6: 2 rects + 1 ellipse", a6())

def a7():
    """3 buttons + 5 random extras."""
    layers = perfect_buttons()
    for i in range(5):
        layers.append(L("rectangle", 700+i*30, 600, 30, 30, RED))
    return H(layers, evts=evt(rect=8))
add("A7: 3 buttons + 5 small extras", a7())

def a8():
    """3 rectangles all stacked at same point (no row)."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 600, 400, 160, 40, BUTTON_COLOR))
    return H(layers, evts=evt(rect=3))
add("A8: 3 buttons stacked at same point", a8())

def a9(): return H(perfect_buttons(n=10), evts=evt(rect=10))
add("A9: 10 buttons (way too many)", a9())

def a10(): return H(perfect_buttons(n=3), evts=evt(rect=0))
add("A10: 3 buttons but 0 create events", a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def b11():
    layers = []
    for i, c in enumerate([RED, GREEN, NAVY]):
        layers.append(L("rectangle", 200+i*172, 300, 160, 40, c))
    return H(layers)
add("B11: 3 buttons all distinct colors", b11())

def b12(): return H()
add("B12: perfect 3 same buttons (control)", b12())

def b13():
    layers = perfect_buttons()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B13: all image fills", b13())

def b14():
    layers = perfect_buttons()
    for l in layers:
        l["fills"] = [{"kind":"gradient","stops":[
            {"position":0,"color":{"r":0.2,"g":0.4,"b":0.8,"a":1}},
            {"position":1,"color":{"r":0.5,"g":0.6,"b":0.9,"a":1}}],
            "opacity":1,"visible":True}]
    return H(layers)
add("B14: all gradient fills", b14())

def b15():
    layers = perfect_buttons()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BUTTON_COLOR, weight=2)]
    return H(layers)
add("B15: stroke-only", b15())

def b16():
    layers = perfect_buttons()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B16: empty fills", b16())

def b17():
    """Near-identical colors (within 0.05 tol)."""
    near = [(0.20, 0.45, 0.85), (0.21, 0.45, 0.85), (0.20, 0.46, 0.85)]
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200+i*172, 300, 160, 40, near[i]))
    return H(layers)
add("B17: 3 near-identical colors", b17())

def b18():
    layers = perfect_buttons()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: alpha=0 on all", b18())

def b19():
    layers = perfect_buttons()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fillOpacity=0.05 on all", b19())

def b20():
    layers = perfect_buttons()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B20: layer.opacity=0 on all", b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def c21(): return H(perfect_buttons(w=400, h=100))
add("C21: huge buttons 400×100", c21())

def c22(): return H(perfect_buttons(w=10, h=4))
add("C22: tiny buttons 10×4", c22())

def c23():
    """3 buttons all different sizes."""
    layers = []
    for i, (w,h) in enumerate([(80,40),(160,40),(240,40)]):
        layers.append(L("rectangle", 200+i*250, 300, w, h, BUTTON_COLOR))
    return H(layers)
add("C23: 3 different widths", c23())

def c24(): return H(perfect_buttons(w=160, h=40))
add("C24: perfect 160×40 (control)", c24())

def c25(): return H(perfect_buttons(w=1, h=1))
add("C25: 1×1 buttons (degenerate)", c25())

def c26():
    """Buttons 158×38 (within 4px tol of 160×40)."""
    return H(perfect_buttons(w=158, h=38))
add("C26: 158×38 (within tol)", c26())

def c27():
    """Buttons 200×50 (outside tol)."""
    return H(perfect_buttons(w=200, h=50))
add("C27: 200×50 (over tol)", c27())

def c28():
    """Buttons square 40×40."""
    return H(perfect_buttons(w=40, h=40))
add("C28: 40×40 (square)", c28())

def c29():
    """3 buttons same size but different positions making a triangle."""
    layers = [
        L("rectangle", 200, 200, 160, 40, BUTTON_COLOR),
        L("rectangle", 400, 400, 160, 40, BUTTON_COLOR),
        L("rectangle", 600, 600, 160, 40, BUTTON_COLOR),
    ]
    return H(layers)
add("C29: 3 buttons in diagonal", c29())

def c30():
    """Tall buttons 40×200 (vertical)."""
    return H(perfect_buttons(w=40, h=200))
add("C30: 40×200 (tall)", c30())


# ─── D. Position ────────────────────────────────────────────────────
def d31():
    """Vertical column."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200, 100+i*60, 160, 40, BUTTON_COLOR))
    return H(layers)
add("D31: vertical column", d31())

def d32():
    """2x2 grid (only 3 cells filled)."""
    coords = [(200,200),(400,200),(200,400)]
    layers = [L("rectangle", x, y, 160, 40, BUTTON_COLOR) for x,y in coords]
    return H(layers)
add("D32: 2x2 grid (3 cells)", d32())

def d33():
    """Random y-baselines."""
    layers = perfect_buttons()
    layers[1]["y"] += 50
    layers[2]["y"] -= 50
    return H(layers)
add("D33: random y baselines", d33())

def d34():
    """Buttons all overlapping at center."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 600, 400, 160, 40, BUTTON_COLOR))
    return H(layers)
add("D34: all 3 at same x,y", d34())

def d35():
    layers = perfect_buttons()
    for l in layers:
        l["x"] += 1500
    return H(layers)
add("D35: buttons off-frame right", d35())

def d36():
    """Random scatter."""
    import random; random.seed(1)
    layers = perfect_buttons()
    for l in layers:
        l["x"] = random.randint(0, 1000)
        l["y"] = random.randint(0, 700)
    return H(layers)
add("D36: random scatter", d36())

def d37():
    """y-baseline diff 2px (within 3 tol)."""
    layers = perfect_buttons()
    layers[1]["y"] += 2
    return H(layers)
add("D37: 2px y diff (within tol)", d37())

def d38():
    """y-baseline diff 5px (over tol)."""
    layers = perfect_buttons()
    layers[1]["y"] += 5
    return H(layers)
add("D38: 5px y diff (over tol)", d38())

def d39():
    """Touching gap=0."""
    return H(perfect_buttons(gap=0))
add("D39: gap=0", d39())

def d40():
    """Huge gap 200px."""
    return H(perfect_buttons(gap=200))
add("D40: gap=200", d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def e41():
    layers = perfect_buttons()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1 button rotated 45°", e41())

def e42():
    layers = perfect_buttons()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E42: all rotated 90°", e42())

def e43():
    layers = perfect_buttons()
    for l in layers:
        l["rotation"] = 1.5
    return H(layers)
add("E43: all rotated 1.5° (under tol)", e43())

def e44():
    layers = perfect_buttons()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: 1 button scaleX=-1", e44())

def e45():
    layers = perfect_buttons()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E45: 1 button scaleY=-1", e45())

def e46():
    """All buttons with cornerRadius=999 (full pill)."""
    layers = perfect_buttons()
    for l in layers:
        l["cornerRadius"] = 999
    return H(layers)
add("E46: all cornerRadius=999", e46())

def e47():
    """All ellipses (wrong type)."""
    layers = []
    for i in range(3):
        layers.append(make_layer("ellipse", x=200+i*172, y=300, w=160, h=40,
                                  fill=BUTTON_COLOR))
    return H(layers, evts=evt(rect=0))
add("E47: 3 ellipses", e47())

def e48():
    """Mix of types."""
    layers = [L("rectangle", 200, 300, 160, 40, BUTTON_COLOR),
              make_layer("ellipse", x=372, y=300, w=160, h=40, fill=BUTTON_COLOR),
              make_layer("polygon", x=544, y=300, w=160, h=40, fill=BUTTON_COLOR, sides=4)]
    return H(layers, evts=evt(rect=1))
add("E48: 1 rect + 1 ellipse + 1 polygon", e48())

def e49():
    """Buttons with cornerRadius=20 (rounded but still rect-shaped)."""
    layers = perfect_buttons()
    for l in layers:
        l["cornerRadius"] = 20
    return H(layers)
add("E49: cornerRadius=20 (rounded)", e49())

def e50():
    layers = perfect_buttons()
    layers[0]["scaleX"] = -1
    layers[1]["scaleY"] = -1
    layers[2]["rotation"] = 30
    return H(layers)
add("E50: each button has different gimmick", e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def f51():
    """Buttons with stroke."""
    layers = perfect_buttons()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=NAVY, weight=2)]
    return H(layers)
add("F51: buttons w/ stroke", f51())

def f52():
    """Buttons with drop shadow."""
    layers = perfect_buttons()
    for l in layers:
        l["effects"] = [{"kind":"drop_shadow","x":0,"y":2,"blur":4,"spread":0,
                          "color":{"r":0,"g":0,"b":0,"a":0.25},"visible":True}]
    return H(layers)
add("F52: buttons w/ shadow", f52())

def f53():
    """Each button different size but same color."""
    layers = []
    cur = 200
    for i, w in enumerate([100, 160, 220]):
        layers.append(L("rectangle", cur, 300, w, 40, BUTTON_COLOR))
        cur += w + 12
    return H(layers)
add("F53: different widths same color", f53())

def f54():
    """3 buttons partially overlapping."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200+i*100, 300, 160, 40, BUTTON_COLOR))
    return H(layers)
add("F54: 3 buttons overlapping", f54())

def f55():
    """3 buttons off-frame to the left."""
    layers = perfect_buttons()
    for l in layers:
        l["x"] -= 500
    return H(layers)
add("F55: buttons off-frame left", f55())

def f56():
    """2 buttons in row + 1 button stacked."""
    layers = [
        L("rectangle", 200, 300, 160, 40, BUTTON_COLOR),
        L("rectangle", 372, 300, 160, 40, BUTTON_COLOR),
        L("rectangle", 200, 400, 160, 40, BUTTON_COLOR),
    ]
    return H(layers)
add("F56: 2 in row + 1 stacked", f56())

def f57():
    """3 buttons in radial arc."""
    import math
    layers = []
    cx, cy, r = 600, 600, 200
    for i in range(3):
        ang = math.radians(-30 + i*30)
        x = cx + r*math.cos(ang) - 80
        y = cy + r*math.sin(ang) - 20
        layers.append(L("rectangle", x, y, 160, 40, BUTTON_COLOR))
    return H(layers)
add("F57: 3 buttons radial arc", f57())

def f58():
    """Buttons at frame top."""
    return H(perfect_buttons(y=0))
add("F58: buttons at y=0", f58())

def f59():
    """Subtle gap variation (within tol)."""
    layers = []
    cur = 200
    gaps = [12, 10, 14]  # variance ≤4 within 12 tol
    for i in range(3):
        layers.append(L("rectangle", cur, 300, 160, 40, BUTTON_COLOR))
        if i < 2:
            cur += 160 + gaps[i]
    return H(layers)
add("F59: gap variance within tol", f59())

def f60():
    """Gap variance over tol."""
    layers = []
    cur = 200
    gaps = [12, 50]
    for i in range(3):
        layers.append(L("rectangle", cur, 300, 160, 40, BUTTON_COLOR))
        if i < 2:
            cur += 160 + gaps[i]
    return H(layers)
add("F60: 50px gap on last pair", f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def g61(): return H()
add("G61: perfect frame", g61())

def g62(): return H(frame_w=800, frame_h=600)
add("G62: frame 800×600", g62())

def g63(): return H(in_frame=False)
add("G63: buttons on page", g63())

def g64():
    """2 frames, buttons in 1st."""
    layers = perfect_buttons()
    f1 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([], w=600, h=400, x=1300)
    return make_log([f1, f2], evt())
add("G64: 2 frames", g64())

def g65():
    """Nested frame."""
    layers = perfect_buttons()
    inner = make_frame(layers, w=800, h=400)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G65: nested frame", g65())

def g66():
    """Frame rotated 45°."""
    layers = perfect_buttons()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G66: frame rotated", g66())

def g67():
    layers = perfect_buttons()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    layers = perfect_buttons()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G68: frame stroked", g68())


# ─── H. Tools / events ──────────────────────────────────────────────
def h69(): return H(evts=evt(extras=[make_event("undo")]*20))
add("H69: 20 undos", h69())

def h70(): return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H70: 1 align event", h70())

def h71():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")]*3)
    sem.extend([make_event("set_fill_color")]*3)
    return H(evts=sem)
add("H71: no tool_change events", h71())

def h72():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")]*3)
    sem.extend([make_event("set_fill_color")]*3)
    return H(evts=sem)
add("H72: pen tool used", h72())

def h73(): return H(evts=evt(rect=7))
add("H73: create_rectangle=7", h73())

def h74(): return H(evts=evt(extras=[make_event("move_layer")]*40))
add("H74: 40 move events", h74())

def h75(): return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H75: distribute event", h75())

def h76():
    extras = [make_event("create_rectangle"), make_event("delete")]*3
    return H(evts=evt(extras=extras))
add("H76: 3 created+deleted extras", h76())

def h77(): return H(evts=evt() + [make_event("session_end")]*5)
add("H77: 5 session_end", h77())

def h78(): return H(evts=evt(set_fill=50))
add("H78: 50 set_fill events", h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def i79():
    layers = perfect_buttons()
    g = {"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("I79: buttons in group in frame", i79())

def i80():
    layers = perfect_buttons()
    f1 = make_frame(layers[:1], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832, x=700)
    return make_log([f1, f2], evt())
add("I80: buttons split across 2 frames", i80())

def i81():
    layers = perfect_buttons()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("I81: buttons in section", i81())

def i82():
    layers = perfect_buttons()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I82: 3-deep nested", i82())

def i83():
    layers = perfect_buttons()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I83: buttons on page 2", i83())

def i84():
    layers = perfect_buttons()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I84: buttons in component", i84())

def i85():
    layers = perfect_buttons()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("I85: buttons in instance", i85())


# ─── J. Bizarre ──────────────────────────────────────────────────────
def j86():
    layers = perfect_buttons()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J86: all scaleX=-1", j86())

def j87():
    layers = perfect_buttons()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("J87: all rotated 180°", j87())

def j88():
    """Buttons piled at one point."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 600, 400, 160, 40, BUTTON_COLOR))
    return H(layers)
add("J88: piled buttons", j88())

def j89():
    return make_log([], [make_event("session_start")])
add("J89: empty doc", j89())

def j90(): return H([])
add("J90: frame only", j90())

def j91():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "buttons"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'buttons'", j91())

def j92():
    layers = []
    for i in range(3):
        layers.append(make_layer("star", x=200+i*172, y=300, w=160, h=40,
                                  fill=BUTTON_COLOR, points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0))
add("J92: 3 stars", j92())

def j93():
    layers = perfect_buttons()
    for l in layers:
        l["y"] -= 1500
    return H(layers)
add("J93: negative y", j93())

def j94():
    """All 3 = full frame size."""
    layers = []
    for _ in range(3):
        layers.append(L("rectangle", 0, 0, 1280, 832, BUTTON_COLOR))
    return H(layers)
add("J94: 3 full-frame buttons", j94())

def j95():
    return H(perfect_buttons(w=1, h=1))
add("J95: 1×1 buttons", j95())

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

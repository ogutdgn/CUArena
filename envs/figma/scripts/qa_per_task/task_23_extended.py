"""100 edge cases for task 23 — outer frame + 1 dark-gray sidebar rectangle on
left edge, constraints horizontal=left, vertical=stretch."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_23" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
DARK_GRAY = (0.30, 0.30, 0.30)
NEAR_DARK_GRAY = (0.32, 0.32, 0.32)
LIGHT_GRAY = (0.85, 0.85, 0.85)
MID_GRAY  = (0.50, 0.50, 0.50)


def evt(rect=1, set_fill=1, frame=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("tool_change", before="frame", after="rectangle")]
    for _ in range(frame): sem.append(make_event("create_frame"))
    for _ in range(rect):  sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_sidebar(frame_w=1280, frame_h=832, sidebar_w=None,
                    sidebar_color=DARK_GRAY, h_constraint="left",
                    v_constraint="stretch"):
    if sidebar_w is None:
        sidebar_w = int(frame_w * 0.17)
    sidebar = L("rectangle", 0, 0, sidebar_w, frame_h, sidebar_color)
    sidebar["constraints"] = {"horizontal": h_constraint, "vertical": v_constraint}
    return [sidebar]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_sidebar(frame_w, frame_h)
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def a1():
    layers = perfect_sidebar() + [L("rectangle", 600, 100, 100, 100, RED,
                                     constraints={"horizontal":"left","vertical":"stretch"})]
    return H(layers, evts=evt(rect=2))
add("A1: 2 sidebars (extra rect)", a1())

def a2():
    """0 rectangles — frame only."""
    return H([], evts=evt(rect=0, set_fill=0))
add("A2: 0 sidebars", a2())

def a3():
    """3 rectangles all dark gray."""
    layers = []
    for i in range(3):
        r = L("rectangle", i*100, 0, 100, 832, DARK_GRAY)
        r["constraints"] = {"horizontal":"left","vertical":"stretch"}
        layers.append(r)
    return H(layers, evts=evt(rect=3))
add("A3: 3 dark-gray sidebars", a3())

def a4():
    """Sidebar + 4 extra distractor rects."""
    layers = perfect_sidebar()
    BLUE_FAKE = (0.2, 0.4, 0.85)
    for i in range(4):
        r = L("rectangle", 400+i*100, 100, 80, 80, [PINK, GREEN, BLUE_FAKE, YELLOW][i])
        layers.append(r)
    return H(layers, evts=evt(rect=5))
add("A4: sidebar + 4 extras", a4())

def a5():
    """0 frames, just sidebar on page."""
    return H(perfect_sidebar(), in_frame=False, evts=evt(rect=1, frame=0))
add("A5: sidebar on page (no frame)", a5())

def a6():
    """2 frames, sidebar in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_sidebar(), w=1280, h=832, x=1300)
    return make_log([f1, f2], evt(frame=2))
add("A6: 2 frames, sidebar in 2nd", a6())

def a7():
    """3 sidebars all distinct colors."""
    layers = []
    for i, c in enumerate([DARK_GRAY, MID_GRAY, LIGHT_GRAY]):
        r = L("rectangle", i*220, 0, 218, 832, c)
        r["constraints"] = {"horizontal":"left","vertical":"stretch"}
        layers.append(r)
    return H(layers, evts=evt(rect=3))
add("A7: 3 sidebar variants", a7())

def a8():
    """Just a sidebar with no events tracking it."""
    return H(perfect_sidebar(), evts=[make_event("session_start")])
add("A8: sidebar but 0 events", a8())

def a9():
    """5 frames nested with sidebar in deepest."""
    layers = perfect_sidebar()
    f5 = make_frame(layers, w=1280, h=832)
    f4 = make_frame([f5], w=1280, h=832)
    f3 = make_frame([f4], w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt(frame=5))
add("A9: sidebar 5-deep nested", a9())

def a10():
    """Way too many sidebars (10)."""
    layers = []
    for i in range(10):
        r = L("rectangle", i*100, 0, 100, 832, DARK_GRAY)
        r["constraints"] = {"horizontal":"left","vertical":"stretch"}
        layers.append(r)
    return H(layers, evts=evt(rect=10))
add("A10: 10 sidebars", a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def b11():
    """Light gray (not dark)."""
    return H(perfect_sidebar(sidebar_color=LIGHT_GRAY))
add("B11: sidebar light gray", b11())

def b12():
    """White sidebar."""
    return H(perfect_sidebar(sidebar_color=WHITE))
add("B12: white sidebar", b12())

def b13():
    """Image fill (not solid)."""
    layers = perfect_sidebar()
    layers[0]["fills"] = [{"kind": "image", "src": "tex.jpg",
                            "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: image fill on sidebar", b13())

def b14():
    """Gradient fill."""
    layers = perfect_sidebar()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":0.3,"g":0.3,"b":0.3,"a":1}},
        {"position": 1, "color": {"r":0.0,"g":0.0,"b":0.0,"a":1}}],
        "opacity":1, "visible":True}]
    return H(layers)
add("B14: gradient fill", b14())

def b15():
    """Stroke-only, no fill."""
    layers = perfect_sidebar()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=4)]
    return H(layers)
add("B15: stroke-only", b15())

def b16():
    """Empty fills array."""
    layers = perfect_sidebar()
    layers[0]["fills"] = []
    return H(layers)
add("B16: empty fills", b16())

def b17():
    """Near-dark-gray (within 0.20 tol)."""
    return H(perfect_sidebar(sidebar_color=NEAR_DARK_GRAY))
add("B17: near-dark-gray (within tol)", b17())

def b18():
    """Sidebar fill alpha=0."""
    layers = perfect_sidebar()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: sidebar alpha=0", b18())

def b19():
    """fillOpacity=0.05."""
    layers = perfect_sidebar()
    layers[0]["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fillOpacity=0.05", b19())

def b20():
    """layer.opacity=0."""
    layers = perfect_sidebar()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("B20: layer.opacity=0", b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def c21():
    """Sidebar very wide (60% of frame)."""
    return H(perfect_sidebar(sidebar_w=768))
add("C21: sidebar 60% of frame", c21())

def c22():
    """Sidebar very narrow (3% — well below 8%)."""
    return H(perfect_sidebar(sidebar_w=38))
add("C22: sidebar 3% of frame", c22())

def c23():
    """Sidebar at exactly 8% (lower bound)."""
    return H(perfect_sidebar(sidebar_w=102))
add("C23: sidebar 8% of frame (at min)", c23())

def c24():
    """Sidebar at exactly 30% (upper bound)."""
    return H(perfect_sidebar(sidebar_w=384))
add("C24: sidebar 30% of frame (at max)", c24())

def c25():
    """Sidebar 1×1 (degenerate)."""
    layers = [L("rectangle", 0, 0, 1, 1, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("C25: sidebar 1×1 (degenerate)", c25())

def c26():
    """Sidebar h=100 (not full height)."""
    layers = [L("rectangle", 0, 0, 200, 100, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("C26: sidebar h=100 (short)", c26())

def c27():
    """Sidebar 217 wide (= ~17%, perfect)."""
    return H(perfect_sidebar(sidebar_w=217))
add("C27: sidebar 217px (~17%)", c27())

def c28():
    """Sidebar w=1, h=832."""
    layers = [L("rectangle", 0, 0, 1, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("C28: sidebar 1×832 (line)", c28())

def c29():
    """Sidebar = full frame size (1280×832)."""
    layers = [L("rectangle", 0, 0, 1280, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("C29: sidebar = entire frame", c29())

def c30():
    """Sidebar inverted (wider than tall — landscape strip)."""
    layers = [L("rectangle", 0, 0, 1280, 100, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("C30: sidebar 1280×100 (landscape)", c30())


# ─── D. Position ────────────────────────────────────────────────────
def d31():
    """Sidebar on right edge."""
    layers = [L("rectangle", 1080, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"right","vertical":"stretch"}
    return H(layers)
add("D31: sidebar on right edge (right constraint)", d31())

def d32():
    """Sidebar in center horizontally."""
    layers = [L("rectangle", 540, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"center","vertical":"stretch"}
    return H(layers)
add("D32: sidebar center", d32())

def d33():
    """Sidebar at top (not full height)."""
    layers = [L("rectangle", 0, 0, 200, 200, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"top"}
    return H(layers)
add("D33: sidebar top (vertical=top, not stretch)", d33())

def d34():
    """Sidebar at bottom only."""
    layers = [L("rectangle", 0, 632, 200, 200, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"bottom"}
    return H(layers)
add("D34: sidebar bottom (vertical=bottom)", d34())

def d35():
    """Sidebar offset by 50px from left edge."""
    layers = [L("rectangle", 50, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("D35: sidebar offset 50px from left", d35())

def d36():
    """Sidebar entirely outside frame."""
    layers = [L("rectangle", 1500, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("D36: sidebar outside frame", d36())

def d37():
    """Sidebar with no constraints set."""
    layers = [L("rectangle", 0, 0, 200, 832, DARK_GRAY)]
    return H(layers)
add("D37: sidebar w/o constraints", d37())

def d38():
    """Sidebar with scale constraint (proportional)."""
    layers = [L("rectangle", 0, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"scale","vertical":"scale"}
    return H(layers)
add("D38: sidebar scale/scale constraints", d38())

def d39():
    """Sidebar with horizontal=stretch (filling full width)."""
    layers = [L("rectangle", 0, 0, 1280, 100, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"stretch","vertical":"top"}
    return H(layers)
add("D39: horizontal=stretch (full-width banner)", d39())

def d40():
    """Sidebar with center/center constraints."""
    layers = [L("rectangle", 540, 366, 200, 100, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"center","vertical":"center"}
    return H(layers)
add("D40: center/center constraints", d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def e41():
    """Sidebar rotated 45°."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: sidebar rotated 45°", e41())

def e42():
    """Sidebar rotated 90°."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: sidebar rotated 90°", e42())

def e43():
    """Sidebar rotated 1°."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 1
    return H(layers)
add("E43: sidebar rotated 1°", e43())

def e44():
    """Sidebar mirrored (scaleX=-1)."""
    layers = perfect_sidebar()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: sidebar scaleX=-1", e44())

def e45():
    """Sidebar mirrored (scaleY=-1)."""
    layers = perfect_sidebar()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E45: sidebar scaleY=-1", e45())

def e46():
    """Sidebar with cornerRadius=99."""
    layers = perfect_sidebar()
    layers[0]["cornerRadius"] = 99
    return H(layers)
add("E46: sidebar cornerRadius=99", e46())

def e47():
    """Sidebar with cornerRadius=999 (looks like a pill)."""
    layers = perfect_sidebar()
    layers[0]["cornerRadius"] = 999
    return H(layers)
add("E47: sidebar cornerRadius=999 (pill)", e47())

def e48():
    """Sidebar as ellipse not rectangle."""
    s = make_layer("ellipse", x=0, y=0, w=200, h=832, fill=DARK_GRAY)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("E48: sidebar is ellipse", e48())

def e49():
    """Sidebar as polygon (rectangle-shaped polygon, sides=4)."""
    s = make_layer("polygon", x=0, y=0, w=200, h=832, fill=DARK_GRAY, sides=4)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("E49: sidebar is polygon", e49())

def e50():
    """Sidebar as line (vertical line)."""
    s = make_layer("line", x=0, y=0, w=2, h=832, fill=DARK_GRAY)
    s["p1"] = {"x":0,"y":0}; s["p2"] = {"x":0,"y":832}
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("E50: sidebar is line", e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def f51():
    """Sidebar with stroke."""
    layers = perfect_sidebar()
    layers[0]["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("F51: sidebar w/ stroke", f51())

def f52():
    """Sidebar with drop shadow."""
    layers = perfect_sidebar()
    layers[0]["effects"] = [{"kind":"drop_shadow","x":4,"y":4,"blur":8,"spread":0,
                              "color":{"r":0,"g":0,"b":0,"a":0.25},"visible":True}]
    return H(layers)
add("F52: sidebar w/ drop shadow", f52())

def f53():
    """Sidebar with layer blur."""
    layers = perfect_sidebar()
    layers[0]["effects"] = [{"kind":"layer_blur","radius":8,"visible":True}]
    return H(layers)
add("F53: sidebar w/ layer blur", f53())

def f54():
    """Sidebar inside a group."""
    layers = perfect_sidebar()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":200,"h":832,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("F54: sidebar inside group inside frame", f54())

def f55():
    """Sidebar at frame edge but slightly outside (overhanging)."""
    layers = [L("rectangle", -50, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("F55: sidebar 50px past left edge", f55())

def f56():
    """Sidebar with both vertical and horizontal stretch."""
    layers = [L("rectangle", 0, 0, 1280, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"stretch","vertical":"stretch"}
    return H(layers)
add("F56: sidebar stretch on both axes", f56())

def f57():
    """Sidebar made of many tiny rects stacked (20 rects)."""
    layers = []
    for i in range(20):
        r = L("rectangle", 0, i*42, 200, 41, DARK_GRAY)
        r["constraints"] = {"horizontal":"left","vertical":"stretch"}
        layers.append(r)
    return H(layers, evts=evt(rect=20))
add("F57: 20 tiny rect strips (faux sidebar)", f57())

def f58():
    """Sidebar partially visible (50% h)."""
    layers = [L("rectangle", 0, 200, 200, 432, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("F58: sidebar half-height starting at y=200", f58())

def f59():
    """Sidebar with top constraint instead of stretch."""
    layers = [L("rectangle", 0, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"top"}
    return H(layers)
add("F59: vertical=top (not stretch)", f59())

def f60():
    """Sidebar with horizontal=center, vertical=stretch."""
    layers = [L("rectangle", 540, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"center","vertical":"stretch"}
    return H(layers)
add("F60: horizontal=center, v=stretch", f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def g61():
    """Default 1280×832 frame (control)."""
    return H()
add("G61: perfect frame 1280×832", g61())

def g62():
    """Tiny frame 200×200."""
    return H(perfect_sidebar(200, 200), frame_w=200, frame_h=200)
add("G62: frame 200×200", g62())

def g63():
    """Frame translated to (500, 300)."""
    layers = perfect_sidebar()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G63: frame translated", g63())

def g64():
    """Frame rotated 45°."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G64: frame rotated 45°", g64())

def g65():
    """Frame with stroke."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G65: frame stroked", g65())

def g66():
    """Frame with image fill."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover",
                        "opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G66: frame image fill", g66())

def g67():
    """Frame at non-standard size 800×600."""
    return H(perfect_sidebar(800, 600), frame_w=800, frame_h=600)
add("G67: frame 800×600", g67())

def g68():
    """Multiple frames, sidebar in 1st."""
    layers = perfect_sidebar()
    f1 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([], w=1280, h=832, x=1300)
    return make_log([f1, f2], evt(frame=2))
add("G68: 2 frames, sidebar in 1st", g68())


# ─── H. Tools / events ──────────────────────────────────────────────
def h69():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H69: 20 undo events", h69())

def h70():
    """No frame tool used."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H70: no frame tool used", h70())

def h71():
    """No rectangle tool used."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("create_frame"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H71: no rectangle tool used", h71())

def h72():
    """Pen tool used (wrong)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_rectangle"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H72: pen tool", h72())

def h73():
    """create_rectangle count = 5."""
    return H(evts=evt(rect=5))
add("H73: create_rectangle=5", h73())

def h74():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(40)]))
add("H74: 40 move_layer events", h74())

def h75():
    """5 align events."""
    return H(evts=evt(extras=[make_event("align_layers", axis="left") for _ in range(5)]))
add("H75: 5 align events", h75())

def h76():
    """create+delete extra rects."""
    extras = [make_event("create_rectangle"), make_event("delete")]*3
    return H(evts=evt(extras=extras))
add("H76: 3 created+deleted extra rects", h76())

def h77():
    """Many session_end events."""
    return H(evts=evt() + [make_event("session_end")]*5)
add("H77: 5 session_end events", h77())

def h78():
    """50 set_fill_color events."""
    return H(evts=evt(set_fill=50))
add("H78: 50 set_fill events", h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def i79():
    """Sidebar inside group inside frame."""
    layers = perfect_sidebar()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":200,"h":832,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("I79: sidebar in group in frame", i79())

def i80():
    """Sidebar in section."""
    layers = perfect_sidebar()
    section = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I80: sidebar in section", i80())

def i81():
    """Sidebar on page (no frame)."""
    return H(perfect_sidebar(), in_frame=False, evts=evt(rect=1, frame=0))
add("I81: sidebar on page (no frame)", i81())

def i82():
    """Sidebar in 3-deep nested frames."""
    layers = perfect_sidebar()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt(frame=3))
add("I82: sidebar 3-deep nested", i82())

def i83():
    """Sidebar on page 2."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I83: sidebar on page 2", i83())

def i84():
    """Sidebar inside component."""
    layers = perfect_sidebar()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I84: sidebar in component", i84())

def i85():
    """Sidebar inside instance."""
    layers = perfect_sidebar()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("I85: sidebar in instance", i85())


# ─── J. Bizarre ──────────────────────────────────────────────────────
def j86():
    """Sidebar with negative coords."""
    layers = [L("rectangle", -200, -100, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("J86: sidebar negative coords", j86())

def j87():
    """Sidebar rotated 180°."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 180
    return H(layers)
add("J87: sidebar rotated 180°", j87())

def j88():
    """Sidebar duplicated 5x at same position."""
    layers = []
    for _ in range(5):
        r = L("rectangle", 0, 0, 200, 832, DARK_GRAY)
        r["constraints"] = {"horizontal":"left","vertical":"stretch"}
        layers.append(r)
    return H(layers, evts=evt(rect=5))
add("J88: 5 sidebars piled at same pos", j88())

def j89():
    return make_log([], [make_event("session_start")])
add("J89: empty document", j89())

def j90():
    return H([])
add("J90: frame only, no sidebar", j90())

def j91():
    text = make_layer("text", x=0, y=0, w=200, h=832, fill=NAVY)
    text["content"] = "sidebar"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text saying 'sidebar'", j91())

def j92():
    """Star instead of rectangle."""
    s = make_layer("star", x=0, y=0, w=200, h=832, fill=DARK_GRAY,
                    points=5, innerRatio=0.4)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("J92: sidebar is a star", j92())

def j93():
    """Sidebar in vector layer."""
    s = make_layer("vector", x=0, y=0, w=200, h=832, fill=DARK_GRAY)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("J93: sidebar is vector", j93())

def j94():
    """Sidebar at far-out position."""
    layers = [L("rectangle", 5000, 5000, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("J94: sidebar at (5000,5000)", j94())

def j95():
    """Sidebar 1×1 (degenerate)."""
    layers = [L("rectangle", 0, 0, 1, 1, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("J95: sidebar 1×1", j95())

def j96():
    return H()
add("J96: perfect sidebar (control)", j96())


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

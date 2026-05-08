"""100 edge cases for task 22 — 4 same-size pill rectangles (radius 999) in a
horizontal row, distinct pastel fills, shared y-baseline."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_22_tag_pills as t
T = t.task

# ─── Helpers ────────────────────────────────────────────────────────
PASTEL_PINK   = (0.95, 0.70, 0.75)
PASTEL_GREEN  = (0.70, 0.95, 0.75)
PASTEL_BLUE   = (0.70, 0.80, 0.95)
PASTEL_YELLOW = (0.95, 0.95, 0.70)
PASTEL_PEACH  = (0.99, 0.85, 0.70)
PASTEL_LILAC  = (0.85, 0.75, 0.95)


def evt(rect=4, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):     sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pills(n=4, w=120, h=40, gap=8, radius=999, colors=None, y=300):
    colors = colors or [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW,
                        PASTEL_PEACH, PASTEL_LILAC]
    layers = []
    for i in range(n):
        layers.append(L("rectangle", 100 + i * (w + gap), y, w, h,
                        colors[i % len(colors)], cornerRadius=radius))
    return layers


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_pills()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def a1():  return H(perfect_pills(n=5), evts=evt(rect=5))
add("A1: 5 pills (extra)", a1())

def a2():  return H(perfect_pills(n=3), evts=evt(rect=3))
add("A2: 3 pills (missing)", a2())

def a3():  return H(perfect_pills(n=8), evts=evt(rect=8))
add("A3: 8 pills (doubled)", a3())

def a4():  return H(perfect_pills(n=2), evts=evt(rect=2))
add("A4: 2 pills (halved)", a4())

def a5():  return H(perfect_pills(n=0), evts=evt(rect=0, set_fill=0))
add("A5: 0 pills", a5())

def a6():
    layers = perfect_pills()
    layers[0]["type"] = "ellipse"  # 1 ellipse + 3 rects
    return H(layers, evts=evt(rect=3))
add("A6: 3 rects + 1 ellipse", a6())

def a7():
    layers = perfect_pills() + [L("ellipse", 700, 300, 40, 40, PASTEL_LILAC)]
    return H(layers, evts=evt(rect=4))
add("A7: 4 pills + extra ellipse", a7())

def a8():  return H(perfect_pills(n=1), evts=evt(rect=1))
add("A8: 1 pill", a8())

def a9():  return H(perfect_pills(n=4) + perfect_pills(n=4, y=400), evts=evt(rect=8))
add("A9: 2 rows of 4 pills (8 total)", a9())

def a10(): return H(perfect_pills(n=6), evts=evt(rect=6))
add("A10: 6 pills (off-by-2)", a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def b11():
    layers = perfect_pills(colors=[PASTEL_PINK]*4)
    return H(layers)
add("B11: all 4 same pastel pink", b11())

def b12():
    return H(perfect_pills())
add("B12: 4 distinct pastels (perfect)", b12())

def b13():
    layers = perfect_pills()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "tag.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: all image fills", b13())

def b14():
    layers = perfect_pills()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r":1,"g":0,"b":0,"a":1}},
            {"position": 1, "color": {"r":0,"g":0,"b":1,"a":1}}],
            "opacity":1, "visible":True}]
    return H(layers)
add("B14: all gradient fills", b14())

def b15():
    layers = perfect_pills()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("B15: stroke-only, no fill", b15())

def b16():
    layers = perfect_pills()
    for l in layers:
        l["fills"] = []
    return H(layers)
add("B16: empty fills array", b16())

def b17():
    base = (0.85, 0.85, 0.85)
    near = [(0.85, 0.85, 0.85), (0.86, 0.85, 0.85),
            (0.85, 0.86, 0.85), (0.85, 0.85, 0.86)]
    return H(perfect_pills(colors=near))
add("B17: near-identical colors (within tol)", b17())

def b18():
    layers = perfect_pills()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: alpha=0 (invisible) on all", b18())

def b19():
    layers = perfect_pills()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fillOpacity=0.05 on all", b19())

def b20():
    layers = perfect_pills()
    # First fill solid distinct, but layer.opacity=0 (invisible)
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("B20: layer.opacity=0 on all", b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def c21():
    layers = perfect_pills(w=400, h=40)
    return H(layers, frame_w=2000)
add("C21: pills 400×40 (huge)", c21())

def c22():
    layers = perfect_pills(w=10, h=4)
    return H(layers)
add("C22: pills 10×4 (tiny)", c22())

def c23():
    """Same w but different h on one — fails LayersSameDimensions."""
    layers = perfect_pills()
    layers[0]["h"] = 80
    return H(layers)
add("C23: 1st pill double-height (different size)", c23())

def c24():
    """Each pill different size."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100 + i*150, 300, 80 + i*30, 30 + i*10,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("C24: 4 pills all different sizes", c24())

def c25():
    """1×1 degenerate."""
    layers = perfect_pills(w=1, h=1)
    return H(layers)
add("C25: pills 1×1 (degenerate)", c25())

def c26():
    """Tall narrow — w and h reversed — pill becomes a vertical capsule."""
    layers = perfect_pills(w=40, h=120)
    return H(layers)
add("C26: pills 40×120 (vertical pills)", c26())

def c27():
    """Just-inside size variation (within 3px tolerance)."""
    layers = perfect_pills()
    layers[1]["w"] = 122  # +2 from 120
    layers[2]["h"] = 38   # -2 from 40
    return H(layers)
add("C27: pills size within tol", c27())

def c28():
    """Just-outside size variation (4px > 3px tol)."""
    layers = perfect_pills()
    layers[1]["w"] = 124
    layers[2]["h"] = 36
    return H(layers)
add("C28: pills size outside tol", c28())

def c29():
    """Pills same size but extreme aspect (10:1)."""
    layers = perfect_pills(w=400, h=20)
    return H(layers)
add("C29: pills very wide flat (400×20)", c29())

def c30():
    """Pills same size but square (40×40) — not really pills anymore."""
    layers = perfect_pills(w=40, h=40, radius=999)
    return H(layers)
add("C30: pills 40×40 (square pills look like circles)", c30())


# ─── D. Position ────────────────────────────────────────────────────
def d31():
    """Pills in a vertical column instead of horizontal row."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200, 100 + i*60, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("D31: pills vertical column (not row)", d31())

def d32():
    """Pills in a 2x2 grid."""
    layers = []
    for i in range(4):
        col = i % 2; row = i // 2
        layers.append(L("rectangle", 200 + col*150, 200 + row*60, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("D32: pills in 2x2 grid", d32())

def d33():
    """Different y-baselines (not aligned)."""
    layers = perfect_pills()
    layers[1]["y"] = 350  # 50px below baseline
    layers[2]["y"] = 250  # 50px above
    return H(layers)
add("D33: pills with random y-baselines", d33())

def d34():
    """All overlapping at same x."""
    layers = perfect_pills()
    for l in layers:
        l["x"] = 200
    return H(layers)
add("D34: pills overlapping at same x (no row)", d34())

def d35():
    """Off-frame to the right."""
    layers = perfect_pills()
    for l in layers:
        l["x"] += 1500
    return H(layers, frame_w=1280)
add("D35: pills off the frame's right", d35())

def d36():
    """Random scatter."""
    import random
    random.seed(2)
    layers = perfect_pills()
    for l in layers:
        l["x"] = random.randint(0, 1100)
        l["y"] = random.randint(0, 700)
    return H(layers)
add("D36: pills randomly scattered", d36())

def d37():
    """Y baseline within tolerance (≤5px diff)."""
    layers = perfect_pills()
    layers[1]["y"] += 4  # within 5px tolerance
    return H(layers)
add("D37: pills with 4px y diff (within tol)", d37())

def d38():
    """Y baseline outside tolerance (10px diff)."""
    layers = perfect_pills()
    layers[1]["y"] += 10
    return H(layers)
add("D38: pills with 10px y diff (outside tol)", d38())

def d39():
    """No gap (touching)."""
    layers = perfect_pills(gap=0)
    return H(layers)
add("D39: pills touching (gap=0)", d39())

def d40():
    """Huge gap (200px)."""
    layers = perfect_pills(gap=200)
    return H(layers)
add("D40: pills with huge 200px gap", d40())


# ─── E. Pill (per-shape) variants ───────────────────────────────────
def e41():
    """No rounding — squares, not pills."""
    layers = perfect_pills(radius=0)
    return H(layers)
add("E41: cornerRadius=0 (sharp rectangles)", e41())

def e42():
    """Below required radius (12 < 24 min)."""
    layers = perfect_pills(radius=12)
    return H(layers)
add("E42: cornerRadius=12 (below 24)", e42())

def e43():
    """At threshold of acceptance (24)."""
    layers = perfect_pills(radius=24)
    return H(layers)
add("E43: cornerRadius=24 (at threshold)", e43())

def e44():
    """Just inside (23 < 24, fails)."""
    layers = perfect_pills(radius=23)
    return H(layers)
add("E44: cornerRadius=23 (just under)", e44())

def e45():
    """One pill rotated 45°."""
    layers = perfect_pills()
    layers[0]["rotation"] = 45
    return H(layers)
add("E45: 1st pill rotated 45°", e45())

def e46():
    """All pills rotated 90° (vertical pills)."""
    layers = perfect_pills()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E46: all pills rotated 90°", e46())

def e47():
    """Pills mirrored (scaleX=-1)."""
    layers = perfect_pills()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E47: pills scaleX=-1 (mirrored)", e47())

def e48():
    """Ellipses with cornerRadius (wrong type)."""
    layers = []
    for i in range(4):
        layers.append(L("ellipse", 100 + i*128, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i]))
    return H(layers, evts=evt(rect=0))
add("E48: 4 ellipses (no rectangles)", e48())

def e49():
    """One pill flipped vertically (scaleY=-1)."""
    layers = perfect_pills()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E49: 1st pill scaleY=-1", e49())

def e50():
    """All pills with extreme cornerRadius (way bigger than h)."""
    layers = perfect_pills(radius=99999)
    return H(layers)
add("E50: cornerRadius=99999 (extreme)", e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def f51():
    """Pills with different widths."""
    layers = []
    widths = [100, 120, 140, 160]
    for i in range(4):
        layers.append(L("rectangle", 100 + sum(widths[:i]) + i*8, 300,
                        widths[i], 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("F51: pills different widths", f51())

def f52():
    """Pills different heights."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100 + i*128, 300, 120, 30 + i*10,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("F52: pills different heights", f52())

def f53():
    """Pills overlapping each other (negative gap)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 100 + i*60, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("F53: pills overlapping each other", f53())

def f54():
    """Pills stacked vertically with shared x (column)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", 200, 100 + i*48, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("F54: pills vertical stack (column)", f54())

def f55():
    """Pills edge-touching at frame border (off-edge)."""
    layers = []
    for i in range(4):
        layers.append(L("rectangle", -50 + i*128, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
    return H(layers)
add("F55: pills extending off frame's left", f55())

def f56():
    """3 pills stacked + 1 pill in row — mixed."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 200, 100 + i*48, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE][i],
                        cornerRadius=999))
    layers.append(L("rectangle", 600, 200, 120, 40, PASTEL_YELLOW, cornerRadius=999))
    return H(layers)
add("F56: 3 pills stacked + 1 pill in row (mixed)", f56())

def f57():
    """Pills in arc (fan)."""
    import math
    layers = []
    cx, cy, r = 600, 600, 200
    for i in range(4):
        ang = math.radians(-90 + i * 30)
        x = cx + r*math.cos(ang) - 60
        y = cy + r*math.sin(ang) - 20
        layers.append(L("rectangle", x, y, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999, rotation=i*30))
    return H(layers)
add("F57: pills in radial arc", f57())

def f58():
    """Pills at edge of frame (top-aligned to top)."""
    layers = perfect_pills(y=0)
    return H(layers)
add("F58: pills at frame top (y=0)", f58())

def f59():
    """Pills with subtle gap variation (within tolerance, 8±5)."""
    layers = []
    gaps = [4, 8, 12, 6]
    cur_x = 100
    for i in range(4):
        layers.append(L("rectangle", cur_x, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
        cur_x += 120 + gaps[i]
    return H(layers)
add("F59: pills with gap variance (within tol)", f59())

def f60():
    """Pills with gap variance outside tolerance (8 vs 30)."""
    layers = []
    gaps = [8, 8, 30]
    cur_x = 100
    for i in range(4):
        layers.append(L("rectangle", cur_x, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                        cornerRadius=999))
        if i < 3:
            cur_x += 120 + gaps[i]
    return H(layers)
add("F60: pills with 30px gap on last pair", f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def g61():
    """Frame 1280×832 default — sanity."""
    return H()
add("G61: perfect frame 1280×832", g61())

def g62():
    """Frame 800×600."""
    return H(frame_w=800, frame_h=600)
add("G62: frame 800×600", g62())

def g63():
    """No frame, pills directly on page."""
    return H(in_frame=False)
add("G63: pills on page (no frame)", g63())

def g64():
    """Two frames, pills only in 1st."""
    layers = perfect_pills()
    f1 = make_frame(layers, w=640, h=600)
    f2 = make_frame([], x=700, w=640, h=600)
    return make_log([f1, f2], evt())
add("G64: 2 frames, pills only in 1st", g64())

def g65():
    """Pills inside nested frames."""
    layers = perfect_pills()
    inner = make_frame(layers, w=800, h=400)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G65: pills nested 2-deep", g65())

def g66():
    """Frame rotated 45°."""
    layers = perfect_pills()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G66: frame rotated 45°", g66())

def g67():
    """Frame translated to (500, 300)."""
    layers = perfect_pills()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    """Frame with stroke."""
    layers = perfect_pills()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G68: frame has stroke", g68())


# ─── H. Tools / events ──────────────────────────────────────────────
def h69():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H69: 20 undo events", h69())

def h70():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H70: used align tool", h70())

def h71():
    """No tool_change at all."""
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 4)
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H71: 0 tool_change events", h71())

def h72():
    """Pen tool used (wrong tool)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")] * 4)
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H72: pen tool used (no rectangle tool)", h72())

def h73():
    """create_rectangle count off."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 7)  # 7 instead of 4
    sem.extend([make_event("set_fill_color")] * 4)
    return H(evts=sem)
add("H73: create_rectangle=7 (off)", h73())

def h74():
    """Lots of move_layer events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(40)]))
add("H74: 40 move_layer events", h74())

def h75():
    return H(evts=evt(extras=[make_event("delete"), make_event("undo")]))
add("H75: delete+undo (extra activity)", h75())

def h76():
    """Created and deleted some pills."""
    extras = [make_event("create_rectangle"), make_event("delete")]*2
    return H(evts=evt(extras=extras))
add("H76: 2 created+deleted pills", h76())

def h77():
    """Many session_end events."""
    sem = evt() + [make_event("session_end")]*5
    return H(evts=sem)
add("H77: 5 session_end events", h77())

def h78():
    """50 set_fill_color events (over-doing it)."""
    return H(evts=evt(set_fill=50))
add("H78: 50 set_fill events", h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def i79():
    layers = perfect_pills()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I79: pills in group inside frame", i79())

def i80():
    layers = perfect_pills()
    f1 = make_frame(layers[:2], w=640, h=832)
    f2 = make_frame(layers[2:], w=640, h=832, x=700)
    return make_log([f1, f2], evt())
add("I80: pills split across 2 frames", i80())

def i81():
    layers = perfect_pills()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I81: pills in section (not frame)", i81())

def i82():
    """3 pills in frame, 1 on page."""
    layers = perfect_pills()
    frame = make_frame(layers[:3], w=1280, h=832)
    return make_log([frame, layers[3]], evt())
add("I82: 3 pills in frame, 1 on page", i82())

def i83():
    """3-deep nesting."""
    layers = perfect_pills()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I83: pills 3-deep nested", i83())

def i84():
    """Pills on page (no frame)."""
    return H(in_frame=False)
add("I84: pills directly on page", i84())

def i85():
    """Pills on page 2 (multi-page)."""
    layers = perfect_pills()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: pills on page 2", i85())


# ─── J. Bizarre ──────────────────────────────────────────────────────
def j86():
    layers = perfect_pills()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J86: all pills scaleX=-1", j86())

def j87():
    layers = perfect_pills()
    for l in layers:
        l["rotation"] = 180
    return H(layers)
add("J87: all pills rotated 180°", j87())

def j88():
    layers = perfect_pills() + perfect_pills(y=300)  # 8 identical
    return H(layers, evts=evt(rect=8))
add("J88: 4 pills + 4 identical duplicates stacked", j88())

def j89():
    return make_log([], [make_event("session_start")])
add("J89: empty document", j89())

def j90():
    return H([])
add("J90: frame only, no shapes", j90())

def j91():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "tag pills"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text layer 'tag pills'", j91())

def j92():
    """4 stars instead of rectangles."""
    layers = []
    for i in range(4):
        layers.append(make_layer("star", x=100+i*128, y=300, w=120, h=40,
                                  fill=[PASTEL_PINK, PASTEL_GREEN, PASTEL_BLUE, PASTEL_YELLOW][i],
                                  points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0))
add("J92: 4 stars (no rectangles)", j92())

def j93():
    """Mix of rectangles and stars (2+2)."""
    layers = []
    for i in range(2):
        layers.append(L("rectangle", 100+i*128, 300, 120, 40,
                        [PASTEL_PINK, PASTEL_GREEN][i], cornerRadius=999))
    for i in range(2):
        layers.append(make_layer("star", x=400+i*128, y=300, w=120, h=40,
                                  fill=[PASTEL_BLUE, PASTEL_YELLOW][i],
                                  points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=2))
add("J93: 2 rectangles + 2 stars", j93())

def j94():
    """Negative coordinates."""
    layers = perfect_pills()
    for l in layers:
        l["y"] -= 1500
    return H(layers)
add("J94: pills at negative-y", j94())

def j95():
    """All pills 1×1 (degenerate)."""
    layers = perfect_pills(w=1, h=1)
    return H(layers)
add("J95: all pills 1×1 (degenerate)", j95())

def j96():
    return H(perfect_pills())
add("J96: perfect pill row (control)", j96())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " FP" if score >= 0.95 and i not in (12, 92, 96) else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

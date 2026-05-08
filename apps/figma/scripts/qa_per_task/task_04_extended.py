"""100 edge cases for task 04 — 6 same-size squares in a hexagonal ring with rainbow colors."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, RED, ORANGE, YELLOW, GREEN, CYAN, NAVY, MAGENTA, PINK, PURPLE,
    WHITE, BLACK, GOLD,
)
from tasks import task_04_color_wheel as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, MAGENTA]


def evt(rect=6, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_ring(side=80, radius=200, n=6):
    cx, cy = 500, 500
    layers = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        layers.append(L("rectangle",
                        cx + radius*math.cos(angle) - side/2,
                        cy + radius*math.sin(angle) - side/2,
                        side, side, RAINBOW[i % 6]))
    return layers


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_ring()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ────────────────────────────────────────────────────────
def case_a1():
    layers = perfect_ring(n=7)
    return H(layers, evts=evt(rect=7))
add("A1: 7 squares (extra)", case_a1())

def case_a2():
    layers = perfect_ring(n=5)
    return H(layers, evts=evt(rect=5))
add("A2: 5 squares (missing 1)", case_a2())

def case_a3():
    return H(perfect_ring(n=4), evts=evt(rect=4))
add("A3: 4 squares", case_a3())

def case_a4():
    return H(perfect_ring(n=3), evts=evt(rect=3))
add("A4: 3 squares", case_a4())

def case_a5():
    return H(perfect_ring(n=8), evts=evt(rect=8))
add("A5: 8 squares", case_a5())

def case_a6():
    return H(perfect_ring(n=12), evts=evt(rect=12))
add("A6: 12 squares (doubled)", case_a6())

def case_a7():
    return H([], evts=evt(rect=0))
add("A7: 0 squares (empty frame)", case_a7())

def case_a8():
    return H([perfect_ring()[0]], evts=evt(rect=1))
add("A8: 1 square", case_a8())

def case_a9():
    layers = perfect_ring()
    # add an ellipse extra
    layers.append(make_layer("ellipse", x=500, y=500, w=50, h=50, fill=GREEN))
    return H(layers, evts=evt(rect=6, extras=[make_event("create_ellipse")]))
add("A9: 6 squares + 1 ellipse extra", case_a9())

def case_a10():
    # 6 squares but add 5 more rectangles outside the ring
    layers = perfect_ring()
    for i in range(5):
        layers.append(L("rectangle", 50+i*30, 50, 20, 20, BLACK))
    return H(layers, evts=evt(rect=11))
add("A10: 11 rectangles (5 extras)", case_a10())


# ─── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    """All same red."""
    cx, cy = 500, 500
    return H([L("rectangle", cx+200*math.cos(2*math.pi*i/6)-40, cy+200*math.sin(2*math.pi*i/6)-40, 80, 80, RED) for i in range(6)])
add("B11: all 6 same red", case_b11())

def case_b12():
    """6 distinct but all near-gray."""
    layers = perfect_ring()
    grays = [(0.4,0.4,0.4),(0.45,0.45,0.45),(0.5,0.5,0.5),(0.55,0.55,0.55),(0.6,0.6,0.6),(0.65,0.65,0.65)]
    for l, c in zip(layers, grays):
        l["fills"][0]["color"] = {"r":c[0], "g":c[1], "b":c[2], "a":1.0}
    return H(layers)
add("B12: 6 near-grays (distinct but bland)", case_b12())

def case_b13():
    """1 image fill on a rectangle."""
    layers = perfect_ring()
    layers[0]["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: 1 image fill", case_b13())

def case_b14():
    """All image fills."""
    layers = perfect_ring()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B14: all image fills", case_b14())

def case_b15():
    """Stroke-only squares."""
    layers = perfect_ring()
    for i, l in enumerate(layers):
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=RAINBOW[i], weight=4)]
    return H(layers)
add("B15: stroke-only squares", case_b15())

def case_b16():
    """Empty fills."""
    layers = perfect_ring()
    for l in layers: l["fills"] = []
    return H(layers)
add("B16: empty fills arrays", case_b16())

def case_b17():
    """All white squares."""
    layers = perfect_ring()
    for l in layers: l["fills"][0]["color"] = {"r":1, "g":1, "b":1, "a":1}
    return H(layers, frame_fill=WHITE)
add("B17: all white (no contrast)", case_b17())

def case_b18():
    """Gradient fills."""
    layers = perfect_ring()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r":1,"g":0,"b":0,"a":1}},
            {"position": 1, "color": {"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B18: all gradient fills", case_b18())

def case_b19():
    """All squares fill alpha=0."""
    layers = perfect_ring()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: alpha=0 (invisible)", case_b19())

def case_b20():
    """Stacked fills (1 solid + image)."""
    layers = perfect_ring()
    for l in layers:
        l["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(layers)
add("B20: stacked fills", case_b20())


# ─── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """All squares 200x200."""
    return H(perfect_ring(side=200))
add("C21: squares 200x200", case_c21())

def case_c22():
    """All squares 5x5."""
    return H(perfect_ring(side=5))
add("C22: squares 5x5 tiny", case_c22())

def case_c23():
    """Different sizes (uneven)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * i / 6
        size = 50 + i * 15
        layers.append(L("rectangle",
                        cx + 200*math.cos(angle) - size/2,
                        cy + 200*math.sin(angle) - size/2,
                        size, size, RAINBOW[i]))
    return H(layers)
add("C23: 6 squares, uneven sizes", case_c23())

def case_c24():
    """All wide rectangles (160x60), not squares."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * i / 6
        layers.append(L("rectangle",
                        cx + 200*math.cos(angle) - 80,
                        cy + 200*math.sin(angle) - 30,
                        160, 60, RAINBOW[i]))
    return H(layers)
add("C24: wide rectangles (not squares)", case_c24())

def case_c25():
    """All tall rectangles (60x160)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * i / 6
        layers.append(L("rectangle",
                        cx + 200*math.cos(angle) - 30,
                        cy + 200*math.sin(angle) - 80,
                        60, 160, RAINBOW[i]))
    return H(layers)
add("C25: tall rectangles (not squares)", case_c25())

def case_c26():
    """Squares 1x1 degenerate."""
    return H(perfect_ring(side=1))
add("C26: squares 1x1 (degenerate)", case_c26())

def case_c27():
    """Squares with same size at 84 (within 3 tol of 80)."""
    return H(perfect_ring(side=84))
add("C27: squares 84x84 (within tol)", case_c27())

def case_c28():
    """5 squares same, 1 different."""
    layers = perfect_ring()
    layers[2] = L("rectangle", layers[2]["x"]-10, layers[2]["y"]-10, 100, 100, YELLOW)
    return H(layers)
add("C28: 5 same + 1 bigger", case_c28())

def case_c29():
    """All squares barely-off (h=82, w=80, within tol 3)."""
    layers = perfect_ring()
    for l in layers: l["h"] = 82
    return H(layers)
add("C29: rectangles 80x82 (within tol)", case_c29())

def case_c30():
    """All squares 50x50."""
    return H(perfect_ring(side=50))
add("C30: squares 50x50", case_c30())


# ─── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """All in a row (linear)."""
    return H([L("rectangle", 100+i*120, 400, 80, 80, RAINBOW[i]) for i in range(6)])
add("D31: 6 squares in a row", case_d31())

def case_d32():
    """3x2 grid."""
    return H([L("rectangle", 200+col*200, 200+row*200, 80, 80, RAINBOW[row*3+col]) for row in range(2) for col in range(3)])
add("D32: 3x2 grid", case_d32())

def case_d33():
    """All at same position (overlapping pile)."""
    return H([L("rectangle", 500, 500, 80, 80, RAINBOW[i]) for i in range(6)])
add("D33: all 6 piled at one point", case_d33())

def case_d34():
    """Hexagonal ring but offset center."""
    return H(perfect_ring(radius=100))
add("D34: ring radius=100 (smaller)", case_d34())

def case_d35():
    """Ring radius=400 (larger)."""
    return H(perfect_ring(radius=400), frame_w=1200, frame_h=1200)
add("D35: ring radius=400", case_d35())

def case_d36():
    """3 squares at angle 0, 3 at angle 180 (clumped)."""
    layers = []
    for i in range(3):
        layers.append(L("rectangle", 700, 470+i*30, 80, 80, RAINBOW[i]))
    for i in range(3):
        layers.append(L("rectangle", 220, 470+i*30, 80, 80, RAINBOW[3+i]))
    return H(layers)
add("D36: 3 left + 3 right (no ring)", case_d36())

def case_d37():
    """6 squares but not at exactly hex angles (5 close, 1 way off)."""
    cx, cy = 500, 500
    layers = []
    angles_deg = [0, 60, 120, 180, 240, 280]  # last angle 280° not 300°
    for i, ang in enumerate(angles_deg):
        a = math.radians(ang)
        layers.append(L("rectangle",
                        cx + 200*math.cos(a) - 40,
                        cy + 200*math.sin(a) - 40,
                        80, 80, RAINBOW[i]))
    return H(layers)
add("D37: 5 at hex angles + 1 way off", case_d37())

def case_d38():
    """6 squares centered in frame instead of in ring."""
    return H([L("rectangle", 460+i*5, 460, 80, 80, RAINBOW[i]) for i in range(6)])
add("D38: 6 squares stacked at center", case_d38())

def case_d39():
    """Perfect ring (control)."""
    return H()
add("D39: perfect (control)", case_d39())

def case_d40():
    """Ring shifted (off-center)."""
    layers = perfect_ring()
    for l in layers:
        l["x"] += 200
    return H(layers)
add("D40: ring shifted right by 200", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────────
def case_e41():
    """All squares rotated 45°."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 45
    return H(layers)
add("E41: all squares rotated 45°", case_e41())

def case_e42():
    """1 square rotated 90°."""
    layers = perfect_ring()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: 1 square rotated 90°", case_e42())

def case_e43():
    """All rotated 180°."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 180
    return H(layers)
add("E43: all rotated 180°", case_e43())

def case_e44():
    """1 scaleX=-1."""
    layers = perfect_ring()
    layers[2]["scaleX"] = -1
    return H(layers)
add("E44: 1 square scaleX=-1", case_e44())

def case_e45():
    """All scaleX=-1."""
    layers = perfect_ring()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("E45: all squares scaleX=-1", case_e45())

def case_e46():
    """All rotated 4° (under 5° tol).
    LayerRotationEquals tolerance defaulted to 2 by us, so 4° should fail."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 4
    return H(layers)
add("E46: all rotated 4° (above strict tol)", case_e46())

def case_e47():
    """All squares cornerRadius=40 (rounded)."""
    layers = perfect_ring()
    for l in layers: l["cornerRadius"] = 40
    return H(layers)
add("E47: all cornerRadius=40", case_e47())

def case_e48():
    """All scaleY=-1."""
    layers = perfect_ring()
    for l in layers: l["scaleY"] = -1
    return H(layers)
add("E48: all scaleY=-1", case_e48())

def case_e49():
    """All rotated 1° (within tol)."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 1
    return H(layers)
add("E49: all rotated 1° (tolerance edge)", case_e49())

def case_e50():
    """Rotation 360° (= 0)."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 360
    return H(layers)
add("E50: rotated 360°", case_e50())


# ─── F. Subcomponent variants ─────────────────────────────────────────
def case_f51():
    """4 squares + 2 stars in a ring."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 6
        layers.append(L("rectangle", cx+200*math.cos(angle)-40, cy+200*math.sin(angle)-40, 80, 80, RAINBOW[i]))
    for i in range(4, 6):
        angle = 2 * math.pi * i / 6
        layers.append(make_layer("star", x=cx+200*math.cos(angle)-40, y=cy+200*math.sin(angle)-40,
                                  w=80, h=80, fill=RAINBOW[i], points=5, innerRatio=0.4))
    sem = evt(rect=4, extras=[make_event("tool_change", before="rectangle", after="star"),
                                make_event("create_star"), make_event("create_star")])
    return H(layers, evts=sem)
add("F51: 4 squares + 2 stars in ring", case_f51())

def case_f52():
    """All squares at the center of frame, rotated to look like fan."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        l = L("rectangle", cx-40, cy-40, 80, 80, RAINBOW[i])
        l["rotation"] = i * 30
        layers.append(l)
    return H(layers)
add("F52: squares stacked at center, fan rotated", case_f52())

def case_f53():
    """Squares with cornerRadius (rounded)."""
    layers = perfect_ring()
    for l in layers: l["cornerRadius"] = 30
    return H(layers)
add("F53: squares cornerRadius=30", case_f53())

def case_f54():
    """6 squares but in a vertical stack."""
    return H([L("rectangle", 500, 100+i*100, 80, 80, RAINBOW[i]) for i in range(6)])
add("F54: 6 squares vertical stack", case_f54())

def case_f55():
    """Perfect ring + extras outside."""
    layers = perfect_ring()
    for i in range(3):
        layers.append(L("rectangle", 50+i*30, 50, 20, 20, BLACK))
    return H(layers, evts=evt(rect=9))
add("F55: ring + 3 extras outside", case_f55())

def case_f56():
    """6 squares in pentagon (5 angles)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * (i % 5) / 5
        layers.append(L("rectangle", cx+200*math.cos(angle)-40, cy+200*math.sin(angle)-40, 80, 80, RAINBOW[i]))
    return H(layers)
add("F56: 6 squares in pentagon (1 doubled)", case_f56())

def case_f57():
    """Squares stroke-only no fill."""
    layers = perfect_ring()
    for i, l in enumerate(layers):
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=RAINBOW[i], weight=4)]
    return H(layers)
add("F57: stroke-only squares", case_f57())

def case_f58():
    """6 squares all touching each other (no gaps)."""
    return H([L("rectangle", 100+i*80, 400, 80, 80, RAINBOW[i]) for i in range(6)])
add("F58: 6 squares in a row touching", case_f58())

def case_f59():
    """6 squares overlapping each other."""
    return H([L("rectangle", 200+i*60, 400, 80, 80, RAINBOW[i]) for i in range(6)])
add("F59: 6 squares overlapping in a row", case_f59())

def case_f60():
    """Squares but in a circle (radial) but with NaN-ish gap (3 angles, 2 squares each)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * (i // 2) / 3
        layers.append(L("rectangle", cx+200*math.cos(angle)+10*(i%2)-40, cy+200*math.sin(angle)+10*(i%2)-40, 80, 80, RAINBOW[i]))
    return H(layers)
add("F60: 3 angles, 2 squares each", case_f60())


# ─── G. Frame variants ────────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_ring()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Squares in nested frames."""
    layers = perfect_ring()
    inner = make_frame(layers, w=800, h=800)
    outer = make_frame([inner], w=1000, h=1000)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """2 frames, ring in 2nd."""
    f1 = make_frame([], w=400, h=400)
    f2 = make_frame(perfect_ring(), w=900, h=900)
    return make_log([f1, f2], evt())
add("G63: 2 frames, ring in 2nd", case_g63())

def case_g64():
    """Frame with stroke."""
    layers = perfect_ring()
    frame = make_frame(layers, w=900, h=900)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    """Frame image fill."""
    layers = perfect_ring()
    frame = make_frame(layers, w=900, h=900, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    """Frame translated."""
    layers = perfect_ring()
    frame = make_frame(layers, x=500, y=500, w=900, h=900)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    """Tiny 200x200 frame."""
    return H(frame_w=200, frame_h=200)
add("G67: tiny frame 200x200", case_g67())

def case_g68():
    """Huge frame 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("G68: huge frame", case_g68())

def case_g69():
    """Ring off-frame."""
    layers = perfect_ring()
    for l in layers: l["x"] -= 1500; l["y"] -= 1500
    return H(layers)
add("G69: ring off-frame (negative)", case_g69())

def case_g70():
    """Frame perfectly fits ring."""
    return H(frame_w=400, frame_h=400)
add("G70: 400x400 frame fits ring", case_g70())


# ─── H. Tools / events ────────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())

def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())

def case_h73():
    """No tool_change."""
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 6)
    return H(evts=sem)
add("H73: no tool_change events", case_h73())

def case_h74():
    """Wrong tool ellipse."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_rectangle")] * 6)
    return H(evts=sem)
add("H74: ellipse tool used", case_h74())

def case_h75():
    """Pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")] * 6)
    return H(evts=sem)
add("H75: pen tool only", case_h75())

def case_h76():
    """6 creates + 4 deletes."""
    sem = evt()
    sem.extend([make_event("delete") for _ in range(4)])
    return H(evts=sem)
add("H76: 6 creates + 4 deletes", case_h76())

def case_h77():
    """0 creates."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    return H(evts=sem)
add("H77: 0 create_rectangle events", case_h77())

def case_h78():
    """Used align."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H78: align_layers used", case_h78())

def case_h79():
    """Used distribute."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: distribute_layers used", case_h79())

def case_h80():
    """Many session_end."""
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H80: many session_end", case_h80())


# ─── I. Hierarchy ─────────────────────────────────────────────────────
def case_i81():
    """Squares in group in frame."""
    layers = perfect_ring()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([g], w=900, h=900)
    return make_log([frame], evt())
add("I81: squares in group in frame", case_i81())

def case_i82():
    """Split: 3 in 1 frame, 3 in another."""
    layers = perfect_ring()
    f1 = make_frame(layers[:3], w=500, h=900)
    f2 = make_frame(layers[3:], w=500, h=900)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    """In section."""
    layers = perfect_ring()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":900,"h":900,"fills":[],"children":layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    """On page no frame."""
    return H(in_frame=False)
add("I84: on page (no frame)", case_i84())

def case_i85():
    """3-deep nested frames."""
    layers = perfect_ring()
    f3 = make_frame(layers, w=800, h=800)
    f2 = make_frame([f3], w=900, h=900)
    f1 = make_frame([f2], w=1000, h=1000)
    return make_log([f1], evt())
add("I85: 3-deep nested", case_i85())

def case_i86():
    """Page 2."""
    layers = perfect_ring()
    frame = make_frame(layers, w=900, h=900)
    p1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    p2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[p1,p2]}}}
add("I86: ring on page 2", case_i86())

def case_i87():
    """Each square in its own frame."""
    layers = perfect_ring()
    frames = [make_frame([l], w=200, h=200) for l in layers]
    return make_log(frames, evt())
add("I87: each square in own frame", case_i87())

def case_i88():
    """In component."""
    layers = perfect_ring()
    comp = {"id":"c1","type":"component","x":0,"y":0,"w":900,"h":900,"fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I88: in component", case_i88())

def case_i89():
    """3 in frame, 3 outside on page."""
    layers = perfect_ring()
    frame = make_frame(layers[:3], w=900, h=900)
    return make_log([frame, *layers[3:]], evt())
add("I89: 3 in, 3 out", case_i89())

def case_i90():
    """In nested groups in frame."""
    layers = perfect_ring()
    g1 = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    g2 = {"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[g1]}
    frame = make_frame([g2], w=900, h=900)
    return make_log([frame], evt())
add("I90: in nested groups in frame", case_i90())


# ─── J. Bizarre ───────────────────────────────────────────────────────
def case_j91():
    """All scaleX=-1."""
    layers = perfect_ring()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("J91: all scaleX=-1", case_j91())

def case_j92():
    """Empty doc."""
    return make_log([], [make_event("session_start")])
add("J92: empty document", case_j92())

def case_j93():
    """Text 'rainbow'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=RED)
    text["content"] = "rainbow ring"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J93: text 'rainbow'", case_j93())

def case_j94():
    """All squares = full frame."""
    return H([L("rectangle", 0, 0, 900, 900, RAINBOW[i]) for i in range(6)])
add("J94: all squares = full frame", case_j94())

def case_j95():
    """All 1x1 degenerate."""
    cx, cy = 500, 500
    return H([L("rectangle", cx+200*math.cos(2*math.pi*i/6)-0.5, cy+200*math.sin(2*math.pi*i/6)-0.5, 1, 1, RAINBOW[i]) for i in range(6)])
add("J95: all 1x1 squares", case_j95())

def case_j96():
    """Squares are stars (pretending to be squares with rotation)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        angle = 2 * math.pi * i / 6
        layers.append(make_layer("star", x=cx+200*math.cos(angle)-40, y=cy+200*math.sin(angle)-40,
                                  w=80, h=80, fill=RAINBOW[i], points=4))
    sem = [make_event("session_start"), make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 6)
    return H(layers, evts=sem)
add("J96: 6 stars instead of squares", case_j96())

def case_j97():
    """Negative coords."""
    layers = perfect_ring()
    for l in layers: l["x"] -= 1000; l["y"] -= 1000
    return H(layers)
add("J97: ring at negative coords", case_j97())

def case_j98():
    """Squares all rotated 30° (looks like diamond)."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 30
    return H(layers)
add("J98: all rotated 30° (diamonds)", case_j98())

def case_j99():
    """All overlapping at center, fan rotated."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        l = L("rectangle", cx-40, cy-40, 80, 80, RAINBOW[i])
        l["rotation"] = i * 30
        layers.append(l)
    return H(layers)
add("J99: all squares at center, fan-rotated", case_j99())

def case_j100():
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

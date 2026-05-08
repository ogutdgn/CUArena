"""100 edge cases for task 50 — album cover (square + centered 5-point star).

Prompt: 1 large square + 1 5-point star centered on top, contrasting fills,
4px white stroke around the star.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN, PINK,
    ORANGE, BLACK, WARM_ORANGE, CREAM,
)
from tasks import task_50_album_cover as t
T = t.task


def evt(rect=1, star=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="star")]
    for _ in range(rect):  sem.append(make_event("create_rectangle"))
    for _ in range(star):  sem.append(make_event("create_star"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_cover(rect_color=NAVY, star_color=YELLOW,
                   points=5, stroke_color=WHITE, stroke_w=4,
                   square_size=300, star_size=160):
    cx, cy = 500, 500
    square = L("rectangle", cx-square_size/2, cy-square_size/2,
               square_size, square_size, rect_color)
    star = L("star", cx-star_size/2, cy-star_size/2,
              star_size, star_size, star_color,
              points=points, innerRatio=0.4,
              strokes=[make_stroke(rgb=stroke_color, weight=stroke_w)])
    return [square, star]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None):
    if layers is None: layers = perfect_cover()
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ─────────────────────────────────────────────────
def case_a1():
    layers = perfect_cover()
    layers.append(L("rectangle", 100, 100, 50, 50, RED))
    return H(layers, evts=evt(rect=2))
add("A1: 2 rectangles", case_a1())

def case_a2():
    layers = perfect_cover()
    layers.append(L("star", 100, 100, 50, 50, RED, points=5, innerRatio=0.4,
                    strokes=[make_stroke(rgb=WHITE, weight=4)]))
    return H(layers, evts=evt(star=2))
add("A2: 2 stars", case_a2())

def case_a3():
    layers = [perfect_cover()[1]]  # only star
    return H(layers, evts=evt(rect=0))
add("A3: only star, no square", case_a3())

def case_a4():
    layers = [perfect_cover()[0]]  # only square
    return H(layers, evts=evt(star=0))
add("A4: only square, no star", case_a4())

def case_a5():
    return H([])
add("A5: empty document", case_a5())

def case_a6():
    layers = perfect_cover()
    layers.append(L("ellipse", 100, 100, 50, 50, GREEN))
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]))
add("A6: extra ellipse decoration", case_a6())

def case_a7():
    layers = perfect_cover()
    for i in range(3):
        layers.append(L("rectangle", 100+i*60, 100, 50, 50, RED))
    return H(layers, evts=evt(rect=4))
add("A7: 4 rectangles total", case_a7())

def case_a8():
    layers = perfect_cover()
    for i in range(2):
        layers.append(L("star", 100+i*60, 100, 50, 50, RED, points=5,
                       innerRatio=0.4, strokes=[make_stroke(rgb=WHITE, weight=4)]))
    return H(layers, evts=evt(star=3))
add("A8: 3 stars total", case_a8())

def case_a9():
    return H()
add("A9: perfect (control)", case_a9())

def case_a10():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=YELLOW)
    text["content"] = "album"
    layers = perfect_cover()
    layers.append(text)
    return H(layers, evts=evt(extras=[make_event("create_text")]))
add("A10: cover + text", case_a10())


# ─── B. Colors / fills (10) ─────────────────────────────────────────
def case_b11():
    layers = perfect_cover(rect_color=YELLOW, star_color=YELLOW)
    return H(layers)
add("B11: square and star same color", case_b11())

def case_b12():
    layers = perfect_cover(rect_color=NAVY, star_color=NAVY)
    return H(layers)
add("B12: square and star both navy", case_b12())

def case_b13():
    layers = perfect_cover()
    layers[0]["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover",
                          "opacity": 1, "visible": True}]
    return H(layers)
add("B13: square has image fill", case_b13())

def case_b14():
    layers = perfect_cover()
    layers[1]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 1, "b": 0, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0, "b": 1, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B14: star has gradient fill", case_b14())

def case_b15():
    layers = perfect_cover()
    layers[0]["fills"] = []
    return H(layers)
add("B15: square has empty fills", case_b15())

def case_b16():
    layers = perfect_cover()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B16: square fill opacity 0.1", case_b16())

def case_b17():
    layers = perfect_cover()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("B17: square alpha=0", case_b17())

def case_b18():
    layers = perfect_cover()
    layers[1]["opacity"] = 0
    return H(layers)
add("B18: star layer opacity=0", case_b18())

def case_b19():
    layers = perfect_cover()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("B19: square fill visible=False", case_b19())

def case_b20():
    layers = perfect_cover()
    layers[0]["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover",
                                "opacity": 0.5, "visible": True})
    return H(layers)
add("B20: square has 2 stacked fills", case_b20())


# ─── C. Sizing (10) ─────────────────────────────────────────────────
def case_c21():
    layers = perfect_cover()
    layers[0]["w"] = 5; layers[0]["h"] = 5  # tiny square
    return H(layers)
add("C21: square 5×5 tiny", case_c21())

def case_c22():
    layers = perfect_cover()
    layers[0]["w"] = 600; layers[0]["h"] = 50  # squashed square (rectangle)
    return H(layers)
add("C22: square 600×50 squashed", case_c22())

def case_c23():
    layers = perfect_cover()
    layers[0]["w"] = 50; layers[0]["h"] = 600  # tall thin
    return H(layers)
add("C23: square 50×600 thin tall", case_c23())

def case_c24():
    layers = perfect_cover()
    layers[1]["w"] = 5; layers[1]["h"] = 5
    return H(layers)
add("C24: star 5×5 tiny", case_c24())

def case_c25():
    layers = perfect_cover(square_size=80, star_size=160)  # star bigger than square
    return H(layers)
add("C25: star bigger than square", case_c25())

def case_c26():
    layers = perfect_cover()
    layers[0]["w"] = 5000; layers[0]["h"] = 5000  # huge square
    return H(layers)
add("C26: square 5000×5000", case_c26())

def case_c27():
    layers = perfect_cover()
    layers[1]["w"] = 4000; layers[1]["h"] = 4000  # huge star
    return H(layers)
add("C27: star 4000×4000", case_c27())

def case_c28():
    layers = perfect_cover()
    layers[0]["w"] = 0; layers[0]["h"] = 0
    return H(layers)
add("C28: square 0×0", case_c28())

def case_c29():
    layers = perfect_cover()
    layers[1]["w"] = 1; layers[1]["h"] = 1
    return H(layers)
add("C29: star 1×1", case_c29())

def case_c30():
    layers = perfect_cover(square_size=500, star_size=295)  # star nearly as big as square
    return H(layers)
add("C30: star 295/500 (≈0.59)", case_c30())


# ─── D. Position (10) ───────────────────────────────────────────────
def case_d31():
    layers = perfect_cover()
    layers[1]["x"] += 200
    return H(layers)
add("D31: star shifted right", case_d31())

def case_d32():
    layers = perfect_cover()
    layers[1]["y"] -= 200
    return H(layers)
add("D32: star shifted up", case_d32())

def case_d33():
    layers = perfect_cover()
    layers[1]["x"] -= 500; layers[1]["y"] -= 500
    return H(layers)
add("D33: star far away", case_d33())

def case_d34():
    layers = perfect_cover()
    layers[1]["x"] = layers[0]["x"] + layers[0]["w"] - 50
    return H(layers)
add("D34: star at square's right edge", case_d34())

def case_d35():
    layers = perfect_cover()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("D35: square at origin (star elsewhere)", case_d35())

def case_d36():
    layers = perfect_cover()
    layers[1]["x"] = layers[0]["x"]; layers[1]["y"] = layers[0]["y"]
    return H(layers)
add("D36: star at square top-left corner", case_d36())

def case_d37():
    layers = perfect_cover()
    layers[1]["x"] = 1500; layers[1]["y"] = 1500  # outside square
    return H(layers)
add("D37: star way far from square", case_d37())

def case_d38():
    return H()
add("D38: perfect centered", case_d38())

def case_d39():
    layers = perfect_cover()
    layers[1]["x"] += 6  # 6px off (within 10px tol)
    return H(layers)
add("D39: star 6px off-center (tol)", case_d39())

def case_d40():
    layers = perfect_cover()
    layers[1]["x"] += 15  # 15px off (over 10px tol)
    return H(layers)
add("D40: star 15px off-center", case_d40())


# ─── E. Star variants (10) ──────────────────────────────────────────
def case_e41():
    return H(perfect_cover(points=3))
add("E41: 3-point star", case_e41())

def case_e42():
    return H(perfect_cover(points=4))
add("E42: 4-point star", case_e42())

def case_e43():
    return H(perfect_cover(points=8))
add("E43: 8-point star", case_e43())

def case_e44():
    layers = perfect_cover()
    layers[1]["rotation"] = 45
    return H(layers)
add("E44: star rotated 45°", case_e44())

def case_e45():
    layers = perfect_cover()
    layers[1]["rotation"] = 36  # one-tenth turn (star symmetry)
    return H(layers)
add("E45: star rotated 36°", case_e45())

def case_e46():
    layers = perfect_cover()
    layers[1]["scaleX"] = -1
    return H(layers)
add("E46: star scaleX=-1", case_e46())

def case_e47():
    layers = perfect_cover()
    layers[1]["innerRatio"] = 0.05
    return H(layers)
add("E47: star super spiky (innerRatio=0.05)", case_e47())

def case_e48():
    layers = perfect_cover()
    layers[1]["innerRatio"] = 0.95
    return H(layers)
add("E48: star almost circle (innerRatio=0.95)", case_e48())

def case_e49():
    layers = perfect_cover()
    layers[0]["rotation"] = 45  # square diamond
    return H(layers)
add("E49: square rotated 45° (diamond)", case_e49())

def case_e50():
    layers = perfect_cover()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E50: square scaleX=-1", case_e50())


# ─── F. Stroke variants (10) ────────────────────────────────────────
def case_f51():
    layers = perfect_cover(stroke_w=1)
    return H(layers)
add("F51: stroke 1px (too thin)", case_f51())

def case_f52():
    layers = perfect_cover(stroke_w=20)
    return H(layers)
add("F52: stroke 20px (thick)", case_f52())

def case_f53():
    layers = perfect_cover(stroke_color=BLACK)
    return H(layers)
add("F53: black stroke (not white)", case_f53())

def case_f54():
    layers = perfect_cover(stroke_color=RED)
    return H(layers)
add("F54: red stroke", case_f54())

def case_f55():
    layers = perfect_cover()
    layers[1]["strokes"] = []
    return H(layers)
add("F55: star has no stroke", case_f55())

def case_f56():
    layers = perfect_cover()
    layers[1]["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("F56: stroke alignment outside", case_f56())

def case_f57():
    layers = perfect_cover()
    layers[1]["strokes"][0]["dash"] = {"dash": 4, "gap": 4}
    return H(layers)
add("F57: dashed star stroke", case_f57())

def case_f58():
    layers = perfect_cover()
    layers[1]["strokes"][0]["paint"]["color"]["a"] = 0
    return H(layers)
add("F58: stroke alpha=0", case_f58())

def case_f59():
    layers = perfect_cover()
    layers[1]["strokes"].append(make_stroke(rgb=BLACK, weight=2))
    return H(layers)
add("F59: 2 strokes (white + black)", case_f59())

def case_f60():
    layers = perfect_cover()
    layers[0]["strokes"] = [make_stroke(rgb=WHITE, weight=4)]  # square has stroke too
    return H(layers)
add("F60: square also has white stroke", case_f60())


# ─── G. Frame variants (10) ─────────────────────────────────────────
def case_g61():
    layers = perfect_cover()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("G61: cover in 1280×832 frame", case_g61())

def case_g62():
    layers = perfect_cover()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("G62: frame rotated 30°", case_g62())

def case_g63():
    layers = perfect_cover()
    inner = make_frame(layers, w=400, h=400)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G63: nested frames", case_g63())

def case_g64():
    f1 = make_frame([], w=400, h=400)
    f2 = make_frame(perfect_cover(), w=400, h=400)
    return make_log([f1, f2], evt())
add("G64: 2 frames, cover in 2nd", case_g64())

def case_g65():
    layers = perfect_cover()
    frame = make_frame(layers, w=1280, h=832)
    frame["scaleX"] = -1
    return make_log([frame], evt())
add("G65: frame scaleX=-1", case_g65())

def case_g66():
    return H()
add("G66: bare on page", case_g66())

def case_g67():
    layers = perfect_cover()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H()
add("G68: bare control", case_g68())

def case_g69():
    layers = perfect_cover()
    frame = make_frame(layers, w=400, h=400)
    return make_log([frame], evt())
add("G69: cover in tight frame", case_g69())

def case_g70():
    layers = perfect_cover(square_size=2000, star_size=1000)  # doesn't fit any frame
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("G70: cover too big for frame", case_g70())


# ─── H. Tools / events (10) ─────────────────────────────────────────
def case_h71():
    extras = [make_event("undo") for _ in range(20)]
    return H(evts=evt(extras=extras))
add("H71: 20 undo events", case_h71())

def case_h72():
    extras = [make_event("delete") for _ in range(10)]
    return H(evts=evt(extras=extras))
add("H72: 10 delete events", case_h72())

def case_h73():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x"),
                               make_event("align_layers", axis="center_y")]))
add("H73: align used", case_h73())

def case_h74():
    sem = [make_event("session_start")]
    sem.append(make_event("create_rectangle"))
    sem.append(make_event("create_star"))
    return H(evts=sem)
add("H74: 0 tool_change events", case_h74())

def case_h75():
    return H(evts=evt(rect=10, star=10))
add("H75: 10 rect + 10 star events", case_h75())

def case_h76():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.append(make_event("create_rectangle"))
    sem.append(make_event("create_star"))
    return H(evts=sem)
add("H76: ellipse tool used (extra)", case_h76())

def case_h77():
    return H(evts=evt(extras=[make_event("session_end")]))
add("H77: session_end included", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("rotate") for _ in range(5)]))
add("H78: 5 rotate events", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star"),
           make_event("create_star"),
           make_event("tool_change", before="star", after="rectangle"),
           make_event("create_rectangle")]
    return H(evts=sem)
add("H79: star created before rectangle", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("set_fill_color")] * 8))
add("H80: 8 set_fill_color events", case_h80())


# ─── I. Hierarchy (10) ──────────────────────────────────────────────
def case_i81():
    layers = perfect_cover()
    grp = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
           "fills": [], "children": layers}
    return make_log([grp], evt())
add("I81: cover in group", case_i81())

def case_i82():
    sq, star = perfect_cover()
    f1 = make_frame([sq], w=400, h=400)
    f2 = make_frame([star], w=400, h=400)
    return make_log([f1, f2], evt())
add("I82: square and star in different frames", case_i82())

def case_i83():
    layers = perfect_cover()
    sec = {"id": "sec1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
           "fills": [], "children": layers}
    return make_log([sec], evt())
add("I83: cover in section", case_i83())

def case_i84():
    layers = perfect_cover()
    f3 = make_frame(layers, w=400, h=400)
    f2 = make_frame([f3], w=600, h=600)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    layers = perfect_cover()
    p1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    p2 = {"id": "p2", "children": layers, "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I85: cover on page 2", case_i85())

def case_i86():
    layers = perfect_cover()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "children": layers}
    return make_log([component], evt())
add("I86: cover in component", case_i86())

def case_i87():
    sq, star = perfect_cover()
    star_grp = {"id": "g_star", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                "fills": [], "children": [star]}
    return make_log([sq, star_grp], evt())
add("I87: star in group, square outside", case_i87())

def case_i88():
    return H()
add("I88: bare (canonical control)", case_i88())

def case_i89():
    layers = perfect_cover()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("I89: in canonical frame", case_i89())

def case_i90():
    sq, star = perfect_cover()
    star["children"] = []  # vector star has no children
    return H([sq, star])
add("I90: bare layers (control)", case_i90())


# ─── J. Bizarre (10) ────────────────────────────────────────────────
def case_j91():
    layers = perfect_cover()
    layers[1]["rotation"] = 180
    return H(layers)
add("J91: star rotated 180°", case_j91())

def case_j92():
    layers = perfect_cover()
    for l in layers: l["x"] -= 1000; l["y"] -= 1000
    return H(layers)
add("J92: cover at far negative", case_j92())

def case_j93():
    layers = perfect_cover()
    layers[0]["w"] = 1; layers[0]["h"] = 1
    layers[1]["w"] = 1; layers[1]["h"] = 1
    return H(layers)
add("J93: square+star both 1×1 at same point", case_j93())

def case_j94():
    sq, star = perfect_cover()
    sq["children"] = [star]  # star nested inside square
    return make_log([sq], evt())
add("J94: star is child of square", case_j94())

def case_j95():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=YELLOW)
    text["content"] = "album cover"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'album cover'", case_j95())

def case_j96():
    layers = perfect_cover()
    layers[1]["scaleY"] = -1
    return H(layers)
add("J96: star scaleY=-1", case_j96())

def case_j97():
    # Square smaller than star
    layers = [L("rectangle", 460, 460, 80, 80, NAVY),
              L("star", 380, 380, 240, 240, YELLOW, points=5, innerRatio=0.4,
                strokes=[make_stroke(rgb=WHITE, weight=4)])]
    return H(layers)
add("J97: roles swapped (small square, big star)", case_j97())

def case_j98():
    # Use a polygon-5 instead of star (similar visually)
    layers = [perfect_cover()[0],
              L("polygon", 420, 420, 160, 160, YELLOW, sides=5)]
    return H(layers, evts=evt(star=0, extras=[make_event("create_polygon")]))
add("J98: polygon-5 instead of star", case_j98())

def case_j99():
    # Ellipse instead of star
    layers = [perfect_cover()[0],
              L("ellipse", 420, 420, 160, 160, YELLOW)]
    return H(layers, evts=evt(star=0, extras=[make_event("create_ellipse")]))
add("J99: ellipse instead of star", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " ⚠ FP" if score >= 0.95 else ""
        if score >= 0.95: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\n{fp_count} cases scored ≥ 0.95")

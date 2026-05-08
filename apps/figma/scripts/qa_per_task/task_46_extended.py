"""100 edge cases for task 46 (audio waveform / 5 vertical bars).

Task 46 prompt: 5 thin vertical rectangles of varying heights, side-by-side
with consistent gap, all sharing a common bottom baseline (like a histogram).
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, GOLD, WHITE, RED, GREEN, NAVY, ORANGE, PINK, PURPLE,
)
from tasks import task_46_audio_waveform as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
LIGHT_BLUE = (0.40, 0.65, 0.95)
DARK_BLUE = (0.10, 0.30, 0.65)


def evt(rect=5, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bars():
    """5 thin vertical rectangles, side-by-side, sharing bottom baseline at y=600.
    Heights vary: 100, 200, 300, 250, 150."""
    bars = []
    heights = [100, 200, 300, 250, 150]
    bar_w = 30
    gap = 10
    base_x = 500
    baseline_y = 600
    for i, h in enumerate(heights):
        x = base_x + i * (bar_w + gap)
        y = baseline_y - h
        color = LIGHT_BLUE if i % 2 == 0 else DARK_BLUE
        bars.append(L("rectangle", x, y, bar_w, h, color))
    return bars


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bars()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_bars()[:4]  # 4 bars
    return H(layers, evts=evt(rect=4))
add("A1: 4 bars", case_a1())

def case_a2():
    layers = perfect_bars() + [L("rectangle", 700, 500, 30, 100, GRAY)]  # 6 bars
    return H(layers, evts=evt(rect=6))
add("A2: 6 bars", case_a2())

def case_a3():
    return H([], evts=evt(rect=0))
add("A3: empty", case_a3())

def case_a4():
    layers = perfect_bars()[:1]  # 1 bar
    return H(layers, evts=evt(rect=1))
add("A4: 1 bar", case_a4())

def case_a5():
    layers = perfect_bars()
    layers.extend([L("ellipse", 100, 100, 30, 30, NAVY)])
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]))
add("A5: 5 bars + 1 ellipse", case_a5())

def case_a6():
    layers = perfect_bars()
    layers.extend([L("rectangle", 100, 100, 30, 30, GRAY) for _ in range(3)])
    return H(layers, evts=evt(rect=8))
add("A6: 8 rects (3 extra not bars)", case_a6())

def case_a7():
    layers = perfect_bars() * 2  # 10 bars
    return H(layers, evts=evt(rect=10))
add("A7: 10 bars", case_a7())

def case_a8():
    layers = perfect_bars()[:3]
    return H(layers, evts=evt(rect=3))
add("A8: 3 bars", case_a8())

def case_a9():
    layers = perfect_bars()[:2]
    return H(layers, evts=evt(rect=2))
add("A9: 2 bars", case_a9())

def case_a10():
    layers = perfect_bars()
    layers.extend(perfect_bars()[:5])  # 10 bars total
    return H(layers, evts=evt(rect=10))
add("A10: 10 bars (2 sets)", case_a10())


# ─── B. Colors ──────────────────────────────────────────────────────
def case_b11():
    layers = perfect_bars()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return H(layers)
add("B11: all bars image fill", case_b11())

def case_b12():
    layers = perfect_bars()
    for l in layers:
        l["fills"][0]["color"] = {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1.0}  # all gray
    return H(layers)
add("B12: all bars same gray (no contrast)", case_b12())

def case_b13():
    layers = perfect_bars()
    for l in layers: l["fills"] = []
    return H(layers)
add("B13: all bars no fill", case_b13())

def case_b14():
    layers = perfect_bars()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 0, "g": 0, "b": 1, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 0, "b": 0.3, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B14: 1st bar gradient", case_b14())

def case_b15():
    layers = perfect_bars()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0  # all alpha=0
    return H(layers)
add("B15: all bars alpha=0", case_b15())

def case_b16():
    layers = perfect_bars()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B16: all bars opacity 0.05", case_b16())

def case_b17():
    layers = perfect_bars()
    layers[0]["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(layers)
add("B17: 1st bar stacked fills", case_b17())

def case_b18():
    layers = perfect_bars()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("B18: all bars visible=False", case_b18())

def case_b19():
    layers = perfect_bars()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("B19: all bars layer opacity=0", case_b19())

def case_b20():
    layers = perfect_bars()
    # Mix of distinct colors
    colors = [RED, GREEN, NAVY, ORANGE, PURPLE]
    for l, c in zip(layers, colors):
        l["fills"][0]["color"] = {"r": c[0], "g": c[1], "b": c[2], "a": 1.0}
    return H(layers)
add("B20: 5 distinct rainbow", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_bars()
    layers[0] = L("rectangle", 0, 0, 1280, 832, LIGHT_BLUE)  # 1st bar = full frame
    return H(layers)
add("C21: 1st bar = full frame", case_c21())

def case_c22():
    layers = perfect_bars()
    for l in layers:
        l["w"] = 5
        l["h"] = 5
    return H(layers)
add("C22: all bars 5×5", case_c22())

def case_c23():
    layers = perfect_bars()
    for l in layers:
        l["w"] = 1
    return H(layers)
add("C23: all bars 1px wide", case_c23())

def case_c24():
    layers = perfect_bars()
    for l in layers:
        l["h"] = 1
    return H(layers)
add("C24: all bars 1px tall", case_c24())

def case_c25():
    layers = perfect_bars()
    # All same height (no varying)
    for l in layers:
        l["h"] = 200
        l["y"] = 400
    return H(layers)
add("C25: all bars 200 tall (no variation)", case_c25())

def case_c26():
    layers = perfect_bars()
    for i, l in enumerate(layers):
        l["w"] = 200  # all very wide
    return H(layers)
add("C26: all bars 200 wide", case_c26())

def case_c27():
    layers = perfect_bars()
    # 4 normal + 1 huge
    layers[2] = L("rectangle", 600, 100, 30, 1000, LIGHT_BLUE)
    return H(layers)
add("C27: 1 bar 1000 tall (huge)", case_c27())

def case_c28():
    layers = perfect_bars()
    # All 1×800 — height varies but very thin
    for i, l in enumerate(layers):
        l["w"] = 1
        l["h"] = 100 + i * 50
        l["y"] = 600 - l["h"]
    return H(layers)
add("C28: all bars 1px wide, varying heights", case_c28())

def case_c29():
    layers = perfect_bars()
    layers[2] = L("rectangle", 600, 600, 30, 1, LIGHT_BLUE)  # 1 bar degenerate height
    return H(layers)
add("C29: 1 bar 1px tall (degenerate)", case_c29())

def case_c30():
    layers = perfect_bars()
    for i in range(5):
        layers[i]["h"] = 100 + i  # varying within tol
    return H(layers)
add("C30: heights vary by 1px each (within tol)", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_bars()
    for l in layers: l["x"] -= 600  # shift left out of frame
    return H(layers)
add("D31: shifted left out of frame", case_d31())

def case_d32():
    layers = perfect_bars()
    for l in layers: l["y"] -= 500
    return H(layers)
add("D32: shifted up", case_d32())

def case_d33():
    layers = perfect_bars()
    # Bars not sharing baseline (different y_bottom)
    for i, l in enumerate(layers):
        l["y"] = 100 + i * 100
    return H(layers)
add("D33: bars at different baselines", case_d33())

def case_d34():
    return H()
add("D34: perfect (control)", case_d34())

def case_d35():
    layers = perfect_bars()
    # Bars stacked vertically (not side-by-side)
    for i, l in enumerate(layers):
        l["x"] = 500
        l["y"] = 100 + i * 100
    return H(layers)
add("D35: bars stacked vertically", case_d35())

def case_d36():
    layers = perfect_bars()
    # Bars overlapping each other
    for l in layers: l["x"] = 500
    return H(layers)
add("D36: all bars at same x (piled)", case_d36())

def case_d37():
    layers = perfect_bars()
    # Bars with random gaps
    base_x = 500
    for i, l in enumerate(layers):
        l["x"] = base_x + i * 100  # gap 70 (instead of 10)
    return H(layers)
add("D37: bars with 70px gap", case_d37())

def case_d38():
    layers = perfect_bars()
    # Bars touching (no gap)
    base_x = 500
    for i, l in enumerate(layers):
        l["x"] = base_x + i * 30  # gap = 0
    return H(layers)
add("D38: bars touching (no gap)", case_d38())

def case_d39():
    for l in (layers := perfect_bars()): l["x"] += 100
    return H(layers)
add("D39: shifted right slightly", case_d39())

def case_d40():
    # Bars at far corners
    layers = perfect_bars()
    layers[0]["x"] = 50
    layers[4]["x"] = 1200
    return H(layers)
add("D40: 1st and 5th at edges", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_bars()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: 1st bar rotated 45°", case_e41())

def case_e42():
    layers = perfect_bars()
    for l in layers: l["rotation"] = 90
    return H(layers)
add("E42: all bars rotated 90° (horizontal)", case_e42())

def case_e43():
    layers = perfect_bars()
    layers[2]["scaleX"] = -1
    return H(layers)
add("E43: 3rd bar mirrored", case_e43())

def case_e44():
    layers = perfect_bars()
    for l in layers: l["scaleY"] = -1
    return H(layers)
add("E44: all bars flipped vertically", case_e44())

def case_e45():
    layers = perfect_bars()
    for l in layers: l["cornerRadius"] = 15
    return H(layers)
add("E45: all bars rounded corners", case_e45())

def case_e46():
    layers = perfect_bars()
    layers[0]["cornerRadius"] = 25  # 1st rounded
    return H(layers)
add("E46: 1st bar rounded", case_e46())

def case_e47():
    layers = perfect_bars()
    layers[0]["rotation"] = 4  # under tol
    return H(layers)
add("E47: 1st bar 4° rotation (under tol)", case_e47())

def case_e48():
    layers = perfect_bars()
    layers[0] = make_layer("ellipse", x=500, y=400, w=30, h=200, fill=LIGHT_BLUE)
    return H(layers, evts=evt(rect=4, extras=[make_event("create_ellipse")]))
add("E48: 1st bar is ellipse", case_e48())

def case_e49():
    layers = perfect_bars()
    layers[0]["w"] = 200
    layers[0]["h"] = 30  # horizontal not vertical
    return H(layers)
add("E49: 1st bar horizontal (200×30)", case_e49())

def case_e50():
    layers = perfect_bars()
    for l in layers:
        l["rotation"] = 30  # all tilted
    return H(layers)
add("E50: all bars rotated 30°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    layers = perfect_bars()
    # All same height (boring)
    for l in layers:
        l["h"] = 200
        l["y"] = 400
    return H(layers)
add("F51: all bars same height 200", case_f51())

def case_f52():
    layers = perfect_bars()
    # Bars not sharing baseline; instead share TOP edge
    for l in layers:
        l["y"] = 200
    return H(layers)
add("F52: bars share top edge (not bottom)", case_f52())

def case_f53():
    layers = perfect_bars()
    # All bars have stroke
    for l in layers:
        l["strokes"] = [make_stroke(rgb=NAVY, weight=2)]
    return H(layers)
add("F53: all bars have stroke", case_f53())

def case_f54():
    layers = perfect_bars()
    # 1st 3 bars at one level, last 2 at different
    for i, l in enumerate(layers):
        if i >= 3:
            l["y"] = 200
            l["h"] = 100
    return H(layers)
add("F54: 3 bars at baseline, 2 floating", case_f54())

def case_f55():
    layers = perfect_bars()
    # Last bar absurdly tall
    layers[4] = L("rectangle", 700, 0, 30, 600, DARK_BLUE)
    return H(layers)
add("F55: last bar 600 tall (extends to top)", case_f55())

def case_f56():
    layers = perfect_bars()
    # Bars touch each other at edges (no gap)
    base_x = 500
    for i, l in enumerate(layers):
        l["x"] = base_x + i * 30
    return H(layers)
add("F56: bars touching edges", case_f56())

def case_f57():
    layers = perfect_bars()
    # Reversed order (heights decreasing)
    heights = [300, 250, 200, 150, 100]
    for i, l in enumerate(layers):
        l["h"] = heights[i]
        l["y"] = 600 - heights[i]
    return H(layers)
add("F57: heights decreasing", case_f57())

def case_f58():
    layers = perfect_bars()
    # All bars 5px wide (very thin)
    for l in layers: l["w"] = 5
    return H(layers)
add("F58: all bars 5px wide", case_f58())

def case_f59():
    layers = perfect_bars()
    # Bars w=80 (twice as wide)
    for l in layers: l["w"] = 80
    return H(layers)
add("F59: all bars 80 wide", case_f59())

def case_f60():
    layers = perfect_bars()
    # All bars same exact rect (overlapping pile)
    for l in layers:
        l["x"] = 500
        l["y"] = 300
        l["w"] = 30
        l["h"] = 300
    return H(layers)
add("F60: all bars overlapping pile", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_bars()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    inner = make_frame(perfect_bars(), w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    return H(frame_w=2000, frame_h=2000)
add("G63: frame 2000x2000", case_g63())

def case_g64():
    layers = perfect_bars()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    layers = perfect_bars()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_bars(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G66: 2 frames, bars in 2nd", case_g66())

def case_g67():
    layers = perfect_bars()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H(frame_w=200, frame_h=200)
add("G68: frame 200x200", case_g68())

def case_g69():
    return make_log(perfect_bars(), evt())
add("G69: no frame", case_g69())

def case_g70():
    return H(frame_w=1290, frame_h=842)
add("G70: frame 1290x842", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    return H(evts=[make_event("session_start")])
add("H71: no events", case_h71())

def case_h72():
    sem = [make_event("session_start")] + [make_event("create_rectangle")] * 5
    return H(evts=sem)
add("H72: events but no tool_change", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_rectangle")] * 5
    return H(evts=sem)
add("H73: ellipse tool used (not rectangle)", case_h73())

def case_h74():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H74: 50 undos", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H75: many deletes", case_h75())

def case_h76():
    return H(evts=evt(rect=10))  # 10 create events
add("H76: 10 create_rectangle events", case_h76())

def case_h77():
    return H(evts=evt(rect=2))  # only 2 events
add("H77: 2 create events", case_h77())

def case_h78():
    return H(evts=evt(extras=[make_event("create_ellipse")]))
add("H78: extra create_ellipse event", case_h78())

def case_h79():
    return H(evts=evt(set_fill=20))
add("H79: 20 set_fills", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("session_end")] * 5))
add("H80: many session_end", case_h80())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i81():
    layers = perfect_bars()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group", case_i81())

def case_i82():
    bars = perfect_bars()
    f1 = make_frame(bars[:3], w=640, h=832)
    f2 = make_frame(bars[3:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_bars()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: in section", case_i83())

def case_i84():
    layers = perfect_bars()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested", case_i84())

def case_i85():
    bars = perfect_bars()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(bars, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: bars on page 2", case_i85())

def case_i86():
    bars = perfect_bars()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": bars}
    return make_log([component], evt())
add("I86: in component", case_i86())

def case_i87():
    return make_log(perfect_bars(), evt())
add("I87: on page (no frame)", case_i87())

def case_i88():
    bars = perfect_bars()
    f = make_frame(bars[:3], w=1280, h=832)
    return make_log([f, *bars[3:]], evt())
add("I88: 3 in frame, 2 on page", case_i88())

def case_i89():
    bars = perfect_bars()
    inner = make_frame(bars[:2], w=600, h=600)
    outer = make_frame([inner, *bars[2:]], w=1280, h=832)
    return make_log([outer], evt())
add("I89: 2 in inner, 3 in outer", case_i89())

def case_i90():
    return H(frame_fill=(0, 0, 0))
add("I90: black frame", case_i90())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j91():
    layers = perfect_bars()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J91: 1st bar mirrored", case_j91())

def case_j92():
    layers = perfect_bars()
    text = make_layer("text", x=100, y=100, w=200, h=50, fill=NAVY)
    text["content"] = "histogram"
    return H(layers + [text])
add("J92: bars + text", case_j92())

def case_j93():
    layers = [L("rectangle", 0, 0, 1280, 832, LIGHT_BLUE)] * 5
    return H(layers)
add("J93: all bars = full frame", case_j93())

def case_j94():
    layers = perfect_bars()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("J94: 1st bar invisible", case_j94())

def case_j95():
    layers = perfect_bars()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0
    return H(layers)
add("J95: all bars alpha=0", case_j95())

def case_j96():
    layers = perfect_bars()
    layers[0]["visible"] = False
    return H(layers)
add("J96: 1st bar visible=False", case_j96())

def case_j97():
    layers = perfect_bars()
    for l in layers: l["opacity"] = 0
    return H(layers)
add("J97: all bars opacity=0", case_j97())

def case_j98():
    layers = perfect_bars()
    for l in layers: l["y"] -= 1000
    return H(layers)
add("J98: shifted up off-screen", case_j98())

def case_j99():
    layers = perfect_bars()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers)
add("J99: all 0×0", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
if __name__ == "__main__":
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

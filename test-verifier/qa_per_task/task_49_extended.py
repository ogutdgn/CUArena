"""100 edge cases for task 49 — decorative ribbon (pen-tool S-curve).

Prompt: 1 pen-tool S-curve with thick (12px) dashed stroke as ribbon.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN, PINK,
    ORANGE, BLACK, WARM_ORANGE, CREAM,
)
from tasks import task_49_decorative_ribbon as t
T = t.task


def evt(vector=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    for _ in range(vector): sem.append(make_event("create_vector"))
    sem.extend(extras)
    return sem


def L(t_, x, y, w, h, fill, **extra):
    return make_layer(t_, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_ribbon(stroke_w=12, dashed=True, color=GOLD):
    dash = {"dash": 8, "gap": 4} if dashed else None
    ribbon = make_layer("vector", x=200, y=300, w=600, h=200, fill=None,
                       strokes=[make_stroke(rgb=color, weight=stroke_w, dash=dash)])
    return ribbon


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None):
    if layers is None: layers = [perfect_ribbon()]
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ─────────────────────────────────────────────────
def case_a1():
    return H([])  # no vector
add("A1: no vector", case_a1())

def case_a2():
    return H([perfect_ribbon(), perfect_ribbon()], evts=evt(vector=2))
add("A2: 2 vectors", case_a2())

def case_a3():
    return H([perfect_ribbon() for _ in range(5)], evts=evt(vector=5))
add("A3: 5 vectors", case_a3())

def case_a4():
    layers = [perfect_ribbon(),
              L("rectangle", 100, 100, 50, 50, RED)]
    return H(layers, evts=evt(extras=[make_event("create_rectangle")]))
add("A4: vector + decorative rectangle", case_a4())

def case_a5():
    layers = [perfect_ribbon(),
              L("ellipse", 100, 100, 50, 50, RED)]
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]))
add("A5: vector + decorative ellipse", case_a5())

def case_a6():
    layers = [perfect_ribbon()]
    for i in range(10):
        layers.append(L("rectangle", 100+i*40, 100, 30, 30, [RED, GREEN, BLUE := (0,0,1)][i % 2]))
    return H(layers)
add("A6: vector + 10 decorative rectangles", case_a6())

def case_a7():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "ribbon"
    return H([perfect_ribbon(), text], evts=evt(extras=[make_event("create_text")]))
add("A7: vector + text", case_a7())

def case_a8():
    return H()  # control: perfect
add("A8: perfect (control)", case_a8())

def case_a9():
    return H([perfect_ribbon(), perfect_ribbon(), perfect_ribbon()], evts=evt(vector=3))
add("A9: 3 vectors", case_a9())

def case_a10():
    layers = [L("vector", 200, 300, 600, 200, fill=GOLD)]  # vector with no stroke
    return H(layers)
add("A10: vector but no stroke at all", case_a10())


# ─── B. Stroke / fill variants (10) ─────────────────────────────────
def case_b11():
    layers = [perfect_ribbon(stroke_w=12, dashed=False)]  # solid stroke
    return H(layers)
add("B11: solid stroke (not dashed)", case_b11())

def case_b12():
    layers = [perfect_ribbon(stroke_w=4)]  # thin stroke
    return H(layers)
add("B12: 4px stroke (too thin)", case_b12())

def case_b13():
    layers = [perfect_ribbon(stroke_w=2)]  # very thin
    return H(layers)
add("B13: 2px stroke", case_b13())

def case_b14():
    layers = [perfect_ribbon(stroke_w=50)]  # super thick
    return H(layers)
add("B14: 50px stroke", case_b14())

def case_b15():
    layers = [perfect_ribbon(stroke_w=14)]  # 14 within 12±2
    return H(layers)
add("B15: 14px stroke (within tol)", case_b15())

def case_b16():
    layers = [perfect_ribbon(stroke_w=10)]
    return H(layers)
add("B16: 10px stroke (within tol)", case_b16())

def case_b17():
    layers = [perfect_ribbon()]
    layers[0]["fills"] = [{"kind": "solid", "color": {"r": 1, "g": 0, "b": 0, "a": 1},
                          "opacity": 1, "visible": True}]
    return H(layers)
add("B17: vector also has solid fill", case_b17())

def case_b18():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0  # invisible stroke
    return H(layers)
add("B18: stroke alpha=0", case_b18())

def case_b19():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["visible"] = False
    return H(layers)
add("B19: stroke visible=False", case_b19())

def case_b20():
    # Multiple strokes, only 2nd dashed
    layers = [perfect_ribbon(dashed=False)]
    layers[0]["strokes"].append(make_stroke(rgb=NAVY, weight=8,
                                              dash={"dash": 6, "gap": 3}))
    return H(layers)
add("B20: 2 strokes, only 2nd dashed", case_b20())


# ─── C. Sizing (10) ─────────────────────────────────────────────────
def case_c21():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 1; layers[0]["h"] = 1
    return H(layers)
add("C21: vector 1×1 degenerate", case_c21())

def case_c22():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 5000; layers[0]["h"] = 5000
    return H(layers)
add("C22: vector 5000×5000", case_c22())

def case_c23():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 50; layers[0]["h"] = 5  # very short
    return H(layers)
add("C23: vector 50×5 short", case_c23())

def case_c24():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 5; layers[0]["h"] = 50
    return H(layers)
add("C24: vector 5×50 thin tall", case_c24())

def case_c25():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 1000; layers[0]["h"] = 1000  # square
    return H(layers)
add("C25: vector 1000×1000 square", case_c25())

def case_c26():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 600; layers[0]["h"] = 200  # canonical
    return H(layers)
add("C26: vector 600×200 (control)", case_c26())

def case_c27():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 200; layers[0]["h"] = 600  # vertical
    return H(layers)
add("C27: vector 200×600 vertical", case_c27())

def case_c28():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 0; layers[0]["h"] = 0
    return H(layers)
add("C28: vector 0×0", case_c28())

def case_c29():
    layers = [perfect_ribbon()]
    layers[0]["w"] = -100; layers[0]["h"] = -100  # negative dims
    return H(layers)
add("C29: vector negative dims", case_c29())

def case_c30():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 100; layers[0]["h"] = 100
    return H(layers)
add("C30: vector 100×100", case_c30())


# ─── D. Position (10) ───────────────────────────────────────────────
def case_d31():
    layers = [perfect_ribbon()]; layers[0]["x"] = -1000; layers[0]["y"] = -1000
    return H(layers)
add("D31: vector at (-1000,-1000)", case_d31())

def case_d32():
    layers = [perfect_ribbon()]; layers[0]["x"] = 5000; layers[0]["y"] = 5000
    return H(layers)
add("D32: vector at (5000,5000)", case_d32())

def case_d33():
    layers = [perfect_ribbon()]; layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("D33: vector at origin", case_d33())

def case_d34():
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 45
    return H(layers)
add("D34: vector rotated 45°", case_d34())

def case_d35():
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 180
    return H(layers)
add("D35: vector rotated 180°", case_d35())

def case_d36():
    layers = [perfect_ribbon()]; layers[0]["scaleX"] = -1
    return H(layers)
add("D36: vector scaleX=-1", case_d36())

def case_d37():
    layers = [perfect_ribbon()]; layers[0]["scaleY"] = -1
    return H(layers)
add("D37: vector scaleY=-1", case_d37())

def case_d38():
    return H()
add("D38: vector at canonical position", case_d38())

def case_d39():
    layers = [perfect_ribbon()]; layers[0]["x"] = 100; layers[0]["y"] = 100
    return H(layers)
add("D39: vector top-left of canvas", case_d39())

def case_d40():
    layers = [perfect_ribbon()]; layers[0]["rotation"] = 90
    return H(layers)
add("D40: vector rotated 90°", case_d40())


# ─── E. Stroke styling (10) ─────────────────────────────────────────
def case_e41():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["dash"] = {"dash": 100, "gap": 1}  # nearly solid
    return H(layers)
add("E41: dash=100, gap=1 (nearly solid)", case_e41())

def case_e42():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["dash"] = {"dash": 1, "gap": 100}  # nearly invisible
    return H(layers)
add("E42: dash=1, gap=100", case_e42())

def case_e43():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["alignment"] = "inside"
    return H(layers)
add("E43: stroke inside alignment", case_e43())

def case_e44():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["alignment"] = "outside"
    return H(layers)
add("E44: stroke outside alignment", case_e44())

def case_e45():
    layers = [perfect_ribbon(color=PINK)]
    return H(layers)
add("E45: pink stroke", case_e45())

def case_e46():
    layers = [perfect_ribbon(color=BLACK)]
    return H(layers)
add("E46: black stroke", case_e46())

def case_e47():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["dash"] = None  # no dash
    return H(layers)
add("E47: dash=None (solid)", case_e47())

def case_e48():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["weight"] = 11.5  # within tol
    return H(layers)
add("E48: weight 11.5 (within tol)", case_e48())

def case_e49():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["paint"]["kind"] = "image"
    layers[0]["strokes"][0]["paint"]["src"] = "tex.jpg"
    return H(layers)
add("E49: image stroke paint", case_e49())

def case_e50():
    layers = [perfect_ribbon()]
    layers[0]["strokes"] = []  # no strokes at all
    return H(layers)
add("E50: vector has no strokes", case_e50())


# ─── F. Visibility (10) ─────────────────────────────────────────────
def case_f51():
    layers = [perfect_ribbon()]; layers[0]["visible"] = False
    return H(layers)
add("F51: vector visible=False", case_f51())

def case_f52():
    layers = [perfect_ribbon()]; layers[0]["opacity"] = 0
    return H(layers)
add("F52: vector opacity=0", case_f52())

def case_f53():
    layers = [perfect_ribbon()]; layers[0]["opacity"] = 0.05
    return H(layers)
add("F53: vector opacity=0.05", case_f53())

def case_f54():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["weight"] = 0
    return H(layers)
add("F54: stroke weight 0", case_f54())

def case_f55():
    layers = [perfect_ribbon()]
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0.05
    return H(layers)
add("F55: stroke alpha=0.05", case_f55())

def case_f56():
    layers = [perfect_ribbon()]; layers[0]["opacity"] = 0.5
    return H(layers)
add("F56: vector opacity=0.5", case_f56())

def case_f57():
    layers = [perfect_ribbon()]
    layers[0]["effects"] = [make_drop_shadow(blur=10)]
    return H(layers)
add("F57: vector with drop shadow", case_f57())

def case_f58():
    layers = [perfect_ribbon()]
    layers[0]["effects"] = [{"kind": "layer_blur", "radius": 8, "visible": True}]
    return H(layers)
add("F58: vector with layer blur", case_f58())

def case_f59():
    layers = [perfect_ribbon()]
    layers[0]["opacity"] = 0.95
    return H(layers)
add("F59: vector opacity=0.95 (within tol)", case_f59())

def case_f60():
    return H()
add("F60: control (perfect)", case_f60())


# ─── G. Frame variants (10) ─────────────────────────────────────────
def case_g61():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("G61: ribbon in 1280×832 frame", case_g61())

def case_g62():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("G62: frame rotated 30°", case_g62())

def case_g63():
    layers = [perfect_ribbon()]
    inner = make_frame(layers, w=800, h=400)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G63: nested frames", case_g63())

def case_g64():
    f1 = make_frame([], w=400, h=400)
    f2 = make_frame([perfect_ribbon()], w=400, h=400)
    return make_log([f1, f2], evt())
add("G64: 2 frames, ribbon in 2nd", case_g64())

def case_g65():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, w=1280, h=832)
    frame["scaleX"] = -1
    return make_log([frame], evt())
add("G65: frame scaleX=-1", case_g65())

def case_g66():
    return H()  # bare on page
add("G66: bare on page", case_g66())

def case_g67():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, w=1, h=1)
    return make_log([frame], evt())
add("G68: 1×1 frame", case_g68())

def case_g69():
    return H()
add("G69: bare (control)", case_g69())

def case_g70():
    layers = [perfect_ribbon()]
    layers[0]["w"] = 2000  # bigger than frame
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("G70: vector wider than frame", case_g70())


# ─── H. Tools / events (10) ─────────────────────────────────────────
def case_h71():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.append(make_event("create_vector"))
    return H(evts=sem)
add("H71: rectangle tool used (no pen)", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    sem.append(make_event("create_vector"))
    return H(evts=sem)
add("H72: line tool used (no pen)", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_vector")]
    sem.append(make_event("undo"))
    sem.append(make_event("create_vector"))
    return H(evts=sem)
add("H73: undo + redo create", case_h73())

def case_h74():
    sem = [make_event("session_start")]  # no tool_change
    sem.append(make_event("create_vector"))
    return H(evts=sem)
add("H74: 0 tool_change events", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("delete") for _ in range(10)]))
add("H75: 10 delete events", case_h75())

def case_h76():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H76: align_layers used", case_h76())

def case_h77():
    return H(evts=evt(vector=10))
add("H77: 10 create_vector events", case_h77())

def case_h78():
    sem = evt()
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H78: session_end included", case_h78())

def case_h79():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    return H(evts=sem)  # pen but no create
add("H79: pen tool but no create", case_h79())

def case_h80():
    return H(evts=evt(extras=[make_event("rotate") for _ in range(5)]))
add("H80: 5 rotate events", case_h80())


# ─── I. Hierarchy (10) ──────────────────────────────────────────────
def case_i81():
    layers = [perfect_ribbon()]
    grp = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
           "fills": [], "children": layers}
    return make_log([grp], evt())
add("I81: vector in group", case_i81())

def case_i82():
    layers = [perfect_ribbon()]
    sec = {"id": "sec1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 1000,
           "fills": [], "children": layers}
    return make_log([sec], evt())
add("I82: vector in section", case_i82())

def case_i83():
    layers = [perfect_ribbon()]
    f3 = make_frame(layers, w=600, h=600)
    f2 = make_frame([f3], w=800, h=800)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt())
add("I83: 3-deep nested frames", case_i83())

def case_i84():
    layers = [perfect_ribbon()]
    p1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    p2 = {"id": "p2", "children": layers, "prototypeSettings": {"device": None,
          "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I84: vector on page 2", case_i84())

def case_i85():
    layers = [perfect_ribbon()]
    component = {"id": "c1", "type": "component", "x": 0, "y": 0,
                 "w": 1000, "h": 1000, "fills": [], "children": layers}
    return make_log([component], evt())
add("I85: vector in component", case_i85())

def case_i86():
    layers = [perfect_ribbon(), perfect_ribbon()]
    f1 = make_frame([layers[0]], w=800, h=400)
    f2 = make_frame([layers[1]], w=800, h=400)
    return make_log([f1, f2], evt(vector=2))
add("I86: 2 vectors in different frames", case_i86())

def case_i87():
    layers = [perfect_ribbon()]
    grp_inner = {"id": "g_inner", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                 "fills": [], "children": layers}
    grp_outer = {"id": "g_outer", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
                 "fills": [], "children": [grp_inner]}
    return make_log([grp_outer], evt())
add("I87: vector in nested groups", case_i87())

def case_i88():
    return H()  # bare control
add("I88: vector on page (canonical)", case_i88())

def case_i89():
    layers = [perfect_ribbon()]
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evt())
add("I89: vector in canonical frame", case_i89())

def case_i90():
    layers = [perfect_ribbon()]
    return make_log(layers, evt())
add("I90: bare on page", case_i90())


# ─── J. Bizarre (10) ────────────────────────────────────────────────
def case_j91():
    layers = [perfect_ribbon()]
    layers[0]["points"] = 5  # vector with star-like data (irrelevant)
    return H(layers)
add("J91: vector with extra 'points' attr", case_j91())

def case_j92():
    layers = [perfect_ribbon()]
    layers[0]["sides"] = 6
    return H(layers)
add("J92: vector with 'sides' attr", case_j92())

def case_j93():
    # Path data abusive - just an empty path
    layers = [perfect_ribbon()]
    layers[0]["path"] = ""
    return H(layers)
add("J93: vector empty path", case_j93())

def case_j94():
    layers = [perfect_ribbon()]
    layers[0]["fills"] = [{"kind": "image", "src": "ribbon.jpg",
                           "fit": "cover", "opacity": 1, "visible": True}]
    return H(layers)
add("J94: vector image fill instead of stroke", case_j94())

def case_j95():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=GOLD)
    text["content"] = "ribbon"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'ribbon' instead of vector", case_j95())

def case_j96():
    layers = [perfect_ribbon(stroke_w=12)]
    layers[0]["strokes"][0]["dash"] = {"dash": 0, "gap": 0}  # zero-length dash
    return H(layers)
add("J96: dash 0,0", case_j96())

def case_j97():
    layers = [perfect_ribbon(dashed=True)]
    layers[0]["strokes"][0]["dash"] = {"dash": 0.001, "gap": 0.001}
    return H(layers)
add("J97: dash=0.001 (effectively solid)", case_j97())

def case_j98():
    # Replace vector with a long thin rectangle (not pen-tool)
    rect = L("rectangle", 200, 300, 600, 12, GOLD)
    return make_log([rect], [make_event("session_start"),
                              make_event("tool_change", before="select", after="rectangle"),
                              make_event("create_rectangle")])
add("J98: rectangle instead of vector", case_j98())

def case_j99():
    # Line instead of vector
    line = make_layer("line", x=200, y=300, w=600, h=2, fill=None,
                       strokes=[make_stroke(rgb=GOLD, weight=12,
                                            dash={"dash": 8, "gap": 4})])
    return make_log([line], [make_event("session_start"),
                              make_event("tool_change", before="select", after="line"),
                              make_event("create_line")])
add("J99: line instead of vector", case_j99())

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

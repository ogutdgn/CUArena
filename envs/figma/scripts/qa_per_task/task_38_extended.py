"""100 edge cases for task 38 (battery indicator) — runs all and prints score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_38" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GREEN_BAR  = (0.4, 0.85, 0.4)
YELLOW_BAR = (0.95, 0.85, 0.2)
RED_BAR    = (0.95, 0.3, 0.3)
GRAY_STROKE = (0.5, 0.5, 0.5)


def evt(rect=5, set_fill=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_battery(body_radius=8):
    body = L("rectangle", 200, 300, 200, 80, WHITE,
             cornerRadius=body_radius,
             strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    terminal = L("rectangle", 400, 325, 12, 30, GRAY_STROKE)
    bars = []
    for i, color in enumerate([GREEN_BAR, YELLOW_BAR, RED_BAR]):
        bars.append(L("rectangle", 220+i*45, 320, 40, 40, color))
    return [body, terminal, *bars]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_battery()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ──────────────────────────────────────────────────
def a1():
    layers = perfect_battery()
    layers.pop()  # 4 rects
    return H(layers, evts=evt(rect=4))
add("A1: 4 rectangles (off-by-1)", a1())

def a2():
    layers = perfect_battery()
    layers.pop(); layers.pop()  # 3 rects
    return H(layers, evts=evt(rect=3))
add("A2: 3 rectangles (no last bar)", a2())

def a3():
    return H([], evts=evt(rect=0))
add("A3: 0 rectangles (empty)", a3())

def a4():
    layers = perfect_battery()
    layers.append(L("rectangle", 460, 320, 40, 40, ORANGE))
    return H(layers, evts=evt(rect=6))
add("A4: 6 rectangles (extra bar)", a4())

def a5():
    layers = perfect_battery()
    layers.append(L("rectangle", 460, 320, 40, 40, ORANGE))
    layers.append(L("rectangle", 510, 320, 40, 40, PURPLE))
    return H(layers, evts=evt(rect=7))
add("A5: 7 rectangles (2 extra bars)", a5())

def a6():
    layers = perfect_battery()
    layers = layers[:1]
    return H(layers, evts=evt(rect=1))
add("A6: only body (no terminal, no bars)", a6())

def a7():
    layers = perfect_battery()
    return H(layers + [L("ellipse", 600, 300, 50, 50, RED_BAR)], evts=evt())
add("A7: extra ellipse (5 rects + 1 ellipse)", a7())

def a8():
    layers = perfect_battery()[:2]
    layers.extend([L("rectangle", 220+i*45, 320, 40, 40, GREEN_BAR) for i in range(3)])
    return H(layers, evts=evt())
add("A8: bars all green (3 same color)", a8())

def a9():
    return H(perfect_battery() + [L("rectangle", 600, 300, 100, 60, NAVY)], evts=evt(rect=6))
add("A9: 6 rectangles (extra ungrouped)", a9())

def a10():
    return H()  # control
add("A10: perfect (control)", a10())


# ─── B. Colors (10) ──────────────────────────────────────────────────
def b11():
    layers = perfect_battery()
    layers[0]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B11: body has image fill", b11())

def b12():
    layers = perfect_battery()
    layers[0]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":1,"g":0,"b":0,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":1,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B12: body has gradient fill", b12())

def b13():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1}
    return H(layers)
add("B13: all 3 bars same gray", b13())

def b14():
    layers = perfect_battery()
    layers[0]["strokes"] = []
    return H(layers)
add("B14: body has no stroke", b14())

def b15():
    layers = perfect_battery()
    for i, c in enumerate([(0.95,0.95,0.95), (0.96,0.96,0.96), (0.97,0.97,0.97)]):
        layers[2+i]["fills"][0]["color"] = {"r":c[0],"g":c[1],"b":c[2],"a":1}
    return H(layers)
add("B15: bars near-identical near-white", b15())

def b16():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B16: bars alpha=0 (invisible)", b16())

def b17():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B17: bars opacity 0.1", b17())

def b18():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["opacity"] = 0.0
    return H(layers)
add("B18: bars layer opacity 0", b18())

def b19():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["visible"] = False
    return H(layers)
add("B19: bars fill visible=False", b19())

def b20():
    layers = perfect_battery()
    layers[0]["fills"] = []  # body no fill (acceptable per prompt)
    return H(layers)
add("B20: body has no fill (acceptable)", b20())


# ─── C. Sizing (10) ──────────────────────────────────────────────────
def c21():
    layers = perfect_battery()
    layers[0] = L("rectangle", 0, 0, 1280, 832, WHITE,
                  cornerRadius=8,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C21: body = full frame", c21())

def c22():
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 5, 5, WHITE,
                  cornerRadius=2,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C22: body 5x5 (tiny)", c22())

def c23():
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 800, 5, WHITE,
                  cornerRadius=2,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C23: body 800x5 (very thin)", c23())

def c24():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i] = L("rectangle", 220+i*5, 320, 1, 1,
                        [GREEN_BAR, YELLOW_BAR, RED_BAR][i])
    return H(layers)
add("C24: bars 1x1 (degenerate)", c24())

def c25():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i] = L("rectangle", 220+i*150, 320, 200, 200,
                        [GREEN_BAR, YELLOW_BAR, RED_BAR][i])
    return H(layers)
add("C25: bars huge (200x200)", c25())

def c26():
    layers = perfect_battery()
    layers[1] = L("rectangle", 400, 325, 1, 1, GRAY_STROKE)  # tiny terminal
    return H(layers)
add("C26: terminal 1x1", c26())

def c27():
    layers = perfect_battery()
    layers[1] = L("rectangle", 400, 325, 200, 200, GRAY_STROKE)  # huge terminal
    return H(layers)
add("C27: terminal 200x200 (huge)", c27())

def c28():
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 30, 30, WHITE,
                  cornerRadius=2,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C28: body 30x30 (square)", c28())

def c29():
    layers = perfect_battery()
    layers[0] = L("rectangle", 200, 300, 1000, 80, WHITE,
                  cornerRadius=8,
                  strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers)
add("C29: body 1000x80 (very wide)", c29())

def c30():
    layers = perfect_battery()
    return H(layers)  # control
add("C30: perfect sizes (control)", c30())


# ─── D. Position (10) ────────────────────────────────────────────────
def d31():
    layers = perfect_battery()
    for l in layers: l["x"] -= 500
    return H(layers)
add("D31: shifted off-left", d31())

def d32():
    layers = perfect_battery()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D32: shifted off-right", d32())

def d33():
    layers = perfect_battery()
    for l in layers: l["y"] -= 500
    return H(layers)
add("D33: negative y", d33())

def d34():
    layers = perfect_battery()
    layers[1] = L("rectangle", 100, 325, 12, 30, GRAY_STROKE)  # terminal far left
    return H(layers)
add("D34: terminal far left of body", d34())

def d35():
    layers = perfect_battery()
    layers[1] = L("rectangle", 200, 100, 12, 30, GRAY_STROKE)  # terminal above
    return H(layers)
add("D35: terminal above body", d35())

def d36():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["x"] = 600  # bars stacked at one x
    return H(layers)
add("D36: bars all same x (overlapping)", d36())

def d37():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["y"] = 100  # bars above body
    return H(layers)
add("D37: bars above body", d37())

def d38():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["y"] = 800  # bars below body
    return H(layers)
add("D38: bars below body", d38())

def d39():
    layers = perfect_battery()
    layers[0]["x"] = 1100; layers[0]["y"] = 700
    return H(layers)
add("D39: body at far edge", d39())

def d40():
    return H()  # control
add("D40: perfect (control)", d40())


# ─── E. Rotation / shape variants (10) ───────────────────────────────
def e41():
    layers = perfect_battery()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: body rotated 45°", e41())

def e42():
    layers = perfect_battery()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: body rotated 90°", e42())

def e43():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["rotation"] = 45
    return H(layers)
add("E43: bars rotated 45°", e43())

def e44():
    layers = perfect_battery()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("E44: all flipped scaleX=-1", e44())

def e45():
    layers = perfect_battery()
    layers[0]["cornerRadius"] = 0
    return H(layers)
add("E45: body cornerRadius=0", e45())

def e46():
    layers = perfect_battery()
    layers[0]["cornerRadius"] = 100
    return H(layers)
add("E46: body cornerRadius=100", e46())

def e47():
    layers = perfect_battery()
    layers[0] = make_layer("ellipse", x=200, y=300, w=200, h=80,
                            fill=WHITE, strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=4))
add("E47: body is ellipse", e47())

def e48():
    layers = perfect_battery()
    layers[0] = make_layer("polygon", x=200, y=300, w=200, h=80,
                            fill=WHITE, sides=6,
                            strokes=[make_stroke(rgb=GRAY_STROKE, weight=2)])
    return H(layers, evts=evt(rect=4))
add("E48: body is polygon", e48())

def e49():
    layers = perfect_battery()
    layers[0]["rotation"] = 3
    return H(layers)
add("E49: body rotated 3° (slight)", e49())

def e50():
    layers = perfect_battery()
    return H(layers)  # control
add("E50: perfect (control)", e50())


# ─── F. Subcomponent variants (10) ───────────────────────────────────
def f51():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"][0]["color"] = {"r":1.0, "g":0, "b":0, "a":1}  # all red
    return H(layers)
add("F51: bars all red (1 distinct)", f51())

def f52():
    layers = perfect_battery()
    layers[2]["fills"][0]["color"] = {"r":0.4,"g":0.85,"b":0.4,"a":1}
    layers[3]["fills"][0]["color"] = {"r":0.41,"g":0.85,"b":0.41,"a":1}
    layers[4]["fills"][0]["color"] = {"r":0.42,"g":0.85,"b":0.42,"a":1}
    return H(layers)
add("F52: bars 3 near-identical greens (within tol)", f52())

def f53():
    layers = perfect_battery()
    layers[1]["fills"] = []
    return H(layers)
add("F53: terminal has no fill", f53())

def f54():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["fills"] = []
    return H(layers)
add("F54: bars no fill", f54())

def f55():
    layers = perfect_battery()
    layers[0]["strokes"] = [make_stroke(rgb=(1,0,0), weight=2)]  # red stroke
    return H(layers)
add("F55: body stroke is red (not gray)", f55())

def f56():
    layers = perfect_battery()
    layers[0]["strokes"] = [make_stroke(rgb=GRAY_STROKE, weight=0)]
    return H(layers)
add("F56: body stroke weight 0", f56())

def f57():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["x"] = 220
        layers[2+i]["y"] = 320 + i*15  # stacked vertically
    return H(layers)
add("F57: bars stacked vertically", f57())

def f58():
    layers = perfect_battery()
    for i in range(3):
        # bars way outside body bbox
        layers[2+i]["x"] = 800 + i*20
        layers[2+i]["y"] = 600
    return H(layers)
add("F58: bars outside body", f58())

def f59():
    layers = perfect_battery()
    layers[0]["fills"][0]["color"] = {"r":0.5,"g":0.5,"b":0.5,"a":1}
    return H(layers)
add("F59: body filled gray (not transparent)", f59())

def f60():
    layers = perfect_battery()
    return H(layers)  # control
add("F60: perfect (control)", f60())


# ─── G. Frame variants (10) ──────────────────────────────────────────
def g61():
    layers = perfect_battery()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", g61())

def g62():
    layers = perfect_battery()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", g62())

def g63():
    layers = perfect_battery()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G63: frame image fill", g63())

def g64():
    layers = perfect_battery()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("G64: frame with stroke", g64())

def g65():
    return H(frame_w=2000, frame_h=1500)
add("G65: frame oversized 2000x1500", g65())

def g66():
    return H(frame_w=200, frame_h=200)
add("G66: frame undersized 200x200", g66())

def g67():
    layers = perfect_battery()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    return H()  # default control
add("G68: default frame (control)", g68())

def g69():
    layers = perfect_battery()
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(layers, w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames, battery in 2nd", g69())

def g70():
    return H(in_frame=False)
add("G70: shapes on page (no frame)", g70())


# ─── H. Tools / events (10) ──────────────────────────────────────────
def h71():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H71: 20 undo events", h71())

def h72():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H72: used align_layers", h72())

def h73():
    sem = [make_event("session_start"),
           make_event("create_rectangle"), make_event("create_rectangle"),
           make_event("create_rectangle"), make_event("create_rectangle"),
           make_event("create_rectangle")]
    return H(evts=sem)
add("H73: 0 tool_change events", h73())

def h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_rectangle")]
    return H(evts=sem)
add("H74: tool change to ellipse only", h74())

def h75():
    return H(evts=evt(rect=10))
add("H75: 10 create_rectangle events", h75())

def h76():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H76: created+deleted a star", h76())

def h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", h77())

def h78():
    return H(evts=evt(set_fill=10))
add("H78: 10 set_fill events", h78())

def h79():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H79: 50 move events", h79())

def h80():
    return H()  # control
add("H80: default events (control)", h80())


# ─── I. Hierarchy (10) ───────────────────────────────────────────────
def i81():
    layers = perfect_battery()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: shapes in group inside frame", i81())

def i82():
    layers = perfect_battery()
    f1 = make_frame(layers[:2], w=640, h=832)
    f2 = make_frame(layers[2:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: shapes split across 2 frames", i82())

def i83():
    layers = perfect_battery()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: shapes in section (not frame)", i83())

def i84():
    layers = perfect_battery()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I84: shapes in component (not frame)", i84())

def i85():
    layers = perfect_battery()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", i85())

def i86():
    layers = perfect_battery()
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    frame = make_frame(layers, w=1280, h=832)
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: battery on page 2", i86())

def i87():
    layers = perfect_battery()
    frame = make_frame(layers[:1], w=1280, h=832)
    return make_log([frame, *layers[1:]], evt())
add("I87: body in frame, others on page", i87())

def i88():
    layers = perfect_battery()
    return make_log(layers, evt())
add("I88: shapes on page (no frame)", i88())

def i89():
    layers = perfect_battery()
    inner_frame = make_frame(layers, w=400, h=400)
    big_frame = make_frame([inner_frame], w=1280, h=832)
    return make_log([big_frame], evt())
add("I89: small inner frame in big frame", i89())

def i90():
    return H()  # control
add("I90: perfect (control)", i90())


# ─── J. Bizarre (10) ─────────────────────────────────────────────────
def j91():
    layers = perfect_battery()
    layers[0]["rotation"] = 180
    return H(layers)
add("J91: body rotated 180°", j91())

def j92():
    layers = []
    for i in range(5):
        layers.append(L("rectangle", 500, 400, 100, 100, [GREEN_BAR,YELLOW_BAR,RED_BAR,WHITE,GRAY_STROKE][i]))
    return H(layers)
add("J92: all 5 rects piled at one point", j92())

def j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", j93())

def j94():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "battery indicator"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J94: text 'battery indicator'", j94())

def j95():
    layers = perfect_battery()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J95: body mirrored", j95())

def j96():
    layers = perfect_battery()
    for i in range(3):
        layers[2+i]["w"] = 1; layers[2+i]["h"] = 1
    return H(layers)
add("J96: bars 1x1 (degenerate)", j96())

def j97():
    # body=red instead of gray-stroke neutral
    layers = perfect_battery()
    layers[0]["fills"][0]["color"] = {"r":1,"g":0,"b":0,"a":1}
    return H(layers)
add("J97: body red filled", j97())

def j98():
    # only 5 rects but no terminal-on-right relationship
    layers = perfect_battery()
    layers[1] = L("rectangle", 600, 600, 12, 30, GRAY_STROKE)
    return H(layers)
add("J98: terminal far away from body", j98())

def j99():
    # extra terminal
    layers = perfect_battery()
    layers.append(L("rectangle", 50, 325, 12, 30, GRAY_STROKE))
    return H(layers, evts=evt(rect=6))
add("J99: 2 terminals (2 small rects)", j99())

def j100():
    return H()  # control
add("J100: perfect (control)", j100())


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

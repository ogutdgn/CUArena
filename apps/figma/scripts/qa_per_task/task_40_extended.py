"""100 edge cases for task 40 (toggle switch) — runs all and prints score table."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_drop_shadow,
    score_task, GREEN, WHITE, NAVY, RED, ORANGE, YELLOW, PURPLE, PINK, GOLD, CYAN, BLACK,
    make_stroke,
)
from tasks import task_40_toggle_switch as t
T = t.task

GREEN_RGB = (0.20, 0.78, 0.35)
WHITE_RGB = (1.0, 1.0, 1.0)


def evt(rect=1, ellipse=1, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("tool_change", before="rectangle", after="ellipse")]
    for _ in range(rect):    sem.append(make_event("create_rectangle"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill):sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_toggle():
    pill = L("rectangle", 400, 300, 80, 40, GREEN_RGB, cornerRadius=999)
    thumb = L("ellipse", 442, 305, 30, 30, WHITE_RGB,
              effects=[make_drop_shadow(y=2, blur=4)])
    return [pill, thumb]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_toggle()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts (10) ──────────────────────────────────────────────────
def a1():
    return H([L("rectangle", 400, 300, 80, 40, GREEN_RGB, cornerRadius=999)],
             evts=evt(ellipse=0))
add("A1: only pill (no thumb)", a1())

def a2():
    return H([L("ellipse", 442, 305, 30, 30, WHITE_RGB,
                effects=[make_drop_shadow(y=2, blur=4)])], evts=evt(rect=0))
add("A2: only thumb (no pill)", a2())

def a3():
    layers = perfect_toggle()
    layers.append(L("rectangle", 600, 300, 80, 40, GREEN_RGB, cornerRadius=999))
    return H(layers, evts=evt(rect=2))
add("A3: 2 pills (extra)", a3())

def a4():
    layers = perfect_toggle()
    layers.append(L("ellipse", 442, 350, 30, 30, WHITE_RGB,
                    effects=[make_drop_shadow(y=2, blur=4)]))
    return H(layers, evts=evt(ellipse=2))
add("A4: 2 thumbs", a4())

def a5():
    return H([], evts=evt(rect=0, ellipse=0))
add("A5: empty document", a5())

def a6():
    layers = perfect_toggle()
    for i in range(3):
        layers.append(L("rectangle", 100+i*100, 100, 50, 50, GOLD))
    return H(layers, evts=evt(rect=4))
add("A6: 4 rectangles (decoration)", a6())

def a7():
    layers = perfect_toggle()
    layers.append(L("polygon", 100, 100, 50, 50, ORANGE, sides=3))
    return H(layers)
add("A7: with polygon decoration", a7())

def a8():
    return H()  # control
add("A8: perfect (control)", a8())

def a9():
    layers = perfect_toggle()
    layers.append(L("text", 100, 100, 100, 30, NAVY))
    layers[-1]["content"] = "ON"
    return H(layers)
add("A9: with text label", a9())

def a10():
    layers = perfect_toggle()
    return H(layers)  # control 2
add("A10: perfect 2 (control)", a10())


# ─── B. Colors (10) ──────────────────────────────────────────────────
def b11():
    layers = perfect_toggle()
    layers[0]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("B11: pill image fill", b11())

def b12():
    layers = perfect_toggle()
    layers[0]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":0.2,"g":0.78,"b":0.35,"a":1}},
        {"position":1,"color":{"r":0,"g":0,"b":0,"a":1}}],"opacity":1,"visible":True}]
    return H(layers)
add("B12: pill gradient", b12())

def b13():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 40, RED, cornerRadius=999)  # red pill
    return H(layers)
add("B13: red pill (not green)", b13())

def b14():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 305, 30, 30, BLACK,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("B14: black thumb", b14())

def b15():
    layers = perfect_toggle()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("B15: pill alpha=0", b15())

def b16():
    layers = perfect_toggle()
    layers[1]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("B16: thumb alpha=0", b16())

def b17():
    layers = perfect_toggle()
    layers[0]["opacity"] = 0
    return H(layers)
add("B17: pill layer opacity=0", b17())

def b18():
    layers = perfect_toggle()
    layers[1]["opacity"] = 0
    return H(layers)
add("B18: thumb layer opacity=0", b18())

def b19():
    layers = perfect_toggle()
    layers[0]["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: pill fill opacity 0.1", b19())

def b20():
    layers = perfect_toggle()
    return H(layers)  # control
add("B20: perfect colors (control)", b20())


# ─── C. Sizing (10) ──────────────────────────────────────────────────
def c21():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 0, 0, 1280, 832, GREEN_RGB, cornerRadius=999)
    return H(layers)
add("C21: pill = full frame", c21())

def c22():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 5, 5, GREEN_RGB, cornerRadius=4)
    return H(layers)
add("C22: pill 5x5 (tiny)", c22())

def c23():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 305, 1, 1, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("C23: thumb 1x1", c23())

def c24():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 100, 305, 200, 200, WHITE_RGB,  # huge thumb
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("C24: thumb 200x200 (huge)", c24())

def c25():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 800, 40, GREEN_RGB, cornerRadius=999)
    return H(layers)
add("C25: pill 800x40 (very wide)", c25())

def c26():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 410, 295, 50, 60, WHITE_RGB,  # oval thumb
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("C26: thumb 50x60 (oval, not circle)", c26())

def c27():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 40, 80, GREEN_RGB, cornerRadius=999)
    return H(layers)
add("C27: pill 40x80 (vertical)", c27())

def c28():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 305, 100, 100, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("C28: thumb 100x100 (bigger than pill)", c28())

def c29():
    layers = perfect_toggle()
    return H(layers)
add("C29: perfect sizes (control)", c29())

def c30():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 80, GREEN_RGB, cornerRadius=999)
    layers[1] = L("ellipse", 422, 305, 60, 60, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("C30: pill 80x80 + thumb 60x60 (both square)", c30())


# ─── D. Position (10) ────────────────────────────────────────────────
def d31():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 405, 305, 30, 30, WHITE_RGB,  # thumb on LEFT
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("D31: thumb on left side of pill", d31())

def d32():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 425, 305, 30, 30, WHITE_RGB,  # thumb in middle
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("D32: thumb in middle of pill", d32())

def d33():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 100, 100, 30, 30, WHITE_RGB,  # thumb far away
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("D33: thumb far from pill", d33())

def d34():
    layers = perfect_toggle()
    for l in layers: l["x"] -= 500
    return H(layers)
add("D34: shifted off-left", d34())

def d35():
    layers = perfect_toggle()
    for l in layers: l["x"] += 1500
    return H(layers)
add("D35: shifted off-right", d35())

def d36():
    layers = perfect_toggle()
    for l in layers: l["y"] -= 500
    return H(layers)
add("D36: negative y", d36())

def d37():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 100, 30, 30, WHITE_RGB,  # thumb above pill
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("D37: thumb above pill", d37())

def d38():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 500, 30, 30, WHITE_RGB,  # thumb below pill
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("D38: thumb below pill", d38())

def d39():
    return H()  # control
add("D39: perfect (control)", d39())

def d40():
    layers = perfect_toggle()
    return H(layers)  # control 2
add("D40: perfect 2 (control)", d40())


# ─── E. Rotation / shape variants (10) ───────────────────────────────
def e41():
    layers = perfect_toggle()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: pill rotated 45°", e41())

def e42():
    layers = perfect_toggle()
    layers[0]["rotation"] = 90
    return H(layers)
add("E42: pill rotated 90°", e42())

def e43():
    layers = perfect_toggle()
    layers[1]["rotation"] = 45
    return H(layers)
add("E43: thumb rotated 45°", e43())

def e44():
    layers = perfect_toggle()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E44: pill flipped scaleX=-1", e44())

def e45():
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = 0  # square pill
    return H(layers)
add("E45: pill cornerRadius=0", e45())

def e46():
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = 4
    return H(layers)
add("E46: pill cornerRadius=4 (low)", e46())

def e47():
    # pill is ellipse
    layers = perfect_toggle()
    layers[0] = L("ellipse", 400, 300, 80, 40, GREEN_RGB)
    return H(layers, evts=evt(rect=0, ellipse=2))
add("E47: pill is ellipse", e47())

def e48():
    # thumb is rectangle
    layers = perfect_toggle()
    layers[1] = L("rectangle", 442, 305, 30, 30, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers, evts=evt(rect=2, ellipse=0))
add("E48: thumb is rectangle", e48())

def e49():
    layers = perfect_toggle()
    layers[1]["scaleY"] = -1
    return H(layers)
add("E49: thumb flipped scaleY=-1", e49())

def e50():
    return H()  # control
add("E50: perfect (control)", e50())


# ─── F. Subcomponent variants (10) ───────────────────────────────────
def f51():
    layers = perfect_toggle()
    layers[1]["effects"] = []
    return H(layers)
add("F51: thumb no shadow", f51())

def f52():
    layers = perfect_toggle()
    layers[1]["effects"][0]["color"]["a"] = 0
    return H(layers)
add("F52: thumb shadow alpha=0", f52())

def f53():
    layers = perfect_toggle()
    layers[1]["effects"][0]["visible"] = False
    return H(layers)
add("F53: thumb shadow visible=False", f53())

def f54():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 410, 305, 60, 30, WHITE_RGB,  # squashed
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("F54: thumb squashed (not circular)", f54())

def f55():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 40, fill=None, cornerRadius=999,
                  strokes=[make_stroke(rgb=GREEN_RGB, weight=2)])
    return H(layers)
add("F55: pill stroke-only", f55())

def f56():
    layers = perfect_toggle()
    layers[0] = L("rectangle", 400, 300, 80, 40, GREEN_RGB, cornerRadius=10)
    return H(layers)
add("F56: pill cornerRadius=10 (less rounded)", f56())

def f57():
    # thumb x at left edge
    layers = perfect_toggle()
    layers[1] = L("ellipse", 405, 305, 30, 30, WHITE_RGB,
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("F57: thumb at left edge of pill", f57())

def f58():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 308, 30, 30, GREEN_RGB,  # green thumb
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("F58: thumb green (matches pill)", f58())

def f59():
    layers = perfect_toggle()
    layers[1]["fills"] = []  # no thumb fill
    return H(layers)
add("F59: thumb no fill", f59())

def f60():
    return H()  # control
add("F60: perfect (control)", f60())


# ─── G. Frame variants (10) ──────────────────────────────────────────
def g61():
    layers = perfect_toggle()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", g61())

def g62():
    layers = perfect_toggle()
    inner = make_frame(layers, w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", g62())

def g63():
    layers = perfect_toggle()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G63: frame image fill", g63())

def g64():
    layers = perfect_toggle()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("G64: frame with stroke", g64())

def g65():
    return H(frame_w=2000, frame_h=1500)
add("G65: frame oversized", g65())

def g66():
    return H(frame_w=200, frame_h=200)
add("G66: frame undersized", g66())

def g67():
    layers = perfect_toggle()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", g67())

def g68():
    return H()  # control
add("G68: default frame (control)", g68())

def g69():
    layers = perfect_toggle()
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(layers, w=1280, h=832)
    return make_log([f1, f2], evt())
add("G69: 2 frames, toggle in 2nd", g69())

def g70():
    return H(in_frame=False)
add("G70: shapes on page (no frame)", g70())


# ─── H. Tools / events (10) ──────────────────────────────────────────
def h71():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H71: 20 undo events", h71())

def h72():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H72: align_layers used", h72())

def h73():
    sem = [make_event("session_start"),
           make_event("create_rectangle"), make_event("create_ellipse")]
    return H(evts=sem)
add("H73: 0 tool_change events", h73())

def h74():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle")]
    return H(evts=sem)
add("H74: only rect tool", h74())

def h75():
    return H(evts=evt(rect=10))
add("H75: 10 create_rectangle", h75())

def h76():
    return H(evts=evt(extras=[make_event("create_star"), make_event("delete")]))
add("H76: create+delete star", h76())

def h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end", h77())

def h78():
    return H(evts=evt(set_fill=10))
add("H78: 10 set_fill", h78())

def h79():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H79: 50 move events", h79())

def h80():
    return H()  # control
add("H80: default events", h80())


# ─── I. Hierarchy (10) ───────────────────────────────────────────────
def i81():
    layers = perfect_toggle()
    group = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,
             "fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: shapes in group inside frame", i81())

def i82():
    layers = perfect_toggle()
    f1 = make_frame([layers[0]], w=640, h=832)
    f2 = make_frame([layers[1]], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: pill/thumb in different frames", i82())

def i83():
    layers = perfect_toggle()
    section = {"id":"s1","type":"section","x":0,"y":0,"w":1280,"h":832,
               "fills":[],"children":layers}
    return make_log([section], evt())
add("I83: shapes in section (not frame)", i83())

def i84():
    layers = perfect_toggle()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("I84: shapes in component", i84())

def i85():
    layers = perfect_toggle()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", i85())

def i86():
    layers = perfect_toggle()
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    frame = make_frame(layers, w=1280, h=832)
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: toggle on page 2", i86())

def i87():
    layers = perfect_toggle()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, layers[1]], evt())
add("I87: pill in frame, thumb on page", i87())

def i88():
    layers = perfect_toggle()
    return make_log(layers, evt())
add("I88: shapes top-level", i88())

def i89():
    layers = perfect_toggle()
    inner = make_frame(layers, w=400, h=400)
    big = make_frame([inner], w=1280, h=832)
    return make_log([big], evt())
add("I89: small inner frame in big", i89())

def i90():
    return H()  # control
add("I90: perfect (control)", i90())


# ─── J. Bizarre (10) ─────────────────────────────────────────────────
def j91():
    layers = perfect_toggle()
    layers[0]["rotation"] = 180
    return H(layers)
add("J91: pill rotated 180°", j91())

def j92():
    layers = perfect_toggle()
    for l in layers:
        l["x"] = 500; l["y"] = 400
        l["w"] = 100; l["h"] = 100
    return H(layers)
add("J92: pill+thumb piled at one point", j92())

def j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", j93())

def j94():
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=NAVY)
    text["content"] = "toggle ON"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J94: text 'toggle ON'", j94())

def j95():
    layers = perfect_toggle()
    layers[1]["scaleX"] = -1
    return H(layers)
add("J95: thumb mirrored", j95())

def j96():
    layers = perfect_toggle()
    layers[0]["w"] = 1; layers[0]["h"] = 1
    return H(layers)
add("J96: pill 1x1", j96())

def j97():
    layers = perfect_toggle()
    layers[1] = L("ellipse", 442, 305, 30, 30, GREEN_RGB,  # green thumb
                  effects=[make_drop_shadow(y=2, blur=4)])
    return H(layers)
add("J97: thumb same color as pill", j97())

def j98():
    layers = perfect_toggle()
    # thumb behind pill (z-order)
    layers.reverse()
    return H(layers)
add("J98: pill on top z-order (occludes thumb)", j98())

def j99():
    layers = perfect_toggle()
    layers[0]["cornerRadius"] = 100  # large but not full
    return H(layers)
add("J99: pill cornerRadius=100", j99())

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

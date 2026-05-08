"""100 edge cases for task 24 — outer frame + 1 centered white rounded rectangle
with drop shadow, centered via align tool."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_24_centered_modal as t
T = t.task

NEAR_WHITE = (0.95, 0.95, 0.95)


def evt(rect=1, set_fill=1, frame=1, align=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("tool_change", before="frame", after="rectangle")]
    for _ in range(frame): sem.append(make_event("create_frame"))
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(align): sem.append(make_event("align_layers", axis="center_x"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_modal(frame_w=1280, frame_h=832, modal_w=400, modal_h=240,
                  modal_color=WHITE, radius=16, shadow=True):
    cx = frame_w / 2 - modal_w / 2
    cy = frame_h / 2 - modal_h / 2
    modal = L("rectangle", cx, cy, modal_w, modal_h, modal_color,
              cornerRadius=radius)
    if shadow:
        modal["effects"] = [make_drop_shadow(x=0, y=4, blur=8, spread=0,
                                              rgb=(0,0,0), alpha=0.25)]
    return [modal]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_modal()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def a1():
    layers = perfect_modal() + [L("rectangle", 100, 100, 100, 100, RED, cornerRadius=16)]
    return H(layers, evts=evt(rect=2))
add("A1: 2 modals (extra rect)", a1())

def a2():
    return H([], evts=evt(rect=0, set_fill=0))
add("A2: 0 modals", a2())

def a3():
    """3 modals overlapping in center."""
    layers = []
    for i in range(3):
        m = L("rectangle", 440 + i*5, 296 + i*5, 400, 240, WHITE, cornerRadius=16)
        m["effects"] = [make_drop_shadow()]
        layers.append(m)
    return H(layers, evts=evt(rect=3))
add("A3: 3 stacked modals", a3())

def a4():
    layers = perfect_modal() + [
        L("rectangle", 100, 100, 80, 80, RED, cornerRadius=16),
        L("rectangle", 1100, 100, 80, 80, GREEN, cornerRadius=16),
        L("rectangle", 100, 700, 80, 80, NAVY, cornerRadius=16),
    ]
    return H(layers, evts=evt(rect=4))
add("A4: modal + 3 corner rects", a4())

def a5():
    return H(perfect_modal(), in_frame=False, evts=evt(rect=1, frame=0))
add("A5: modal on page (no frame)", a5())

def a6():
    """Modal + a hidden frame."""
    layers = perfect_modal()
    f1 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([], w=600, h=400, x=2000)
    return make_log([f1, f2], evt(frame=2))
add("A6: 2 frames, modal in 1st", a6())

def a7():
    """3 modals as a checkerboard."""
    layers = []
    for i, (x,y) in enumerate([(200,300),(640,300),(440,500)]):
        m = L("rectangle", x, y, 200, 100, WHITE, cornerRadius=16)
        m["effects"] = [make_drop_shadow()]
        layers.append(m)
    return H(layers, evts=evt(rect=3))
add("A7: 3 small modals at different spots", a7())

def a8():
    return H(evts=evt(rect=2))  # event count off
add("A8: events claim 2 rects but doc has 1", a8())

def a9():
    """Modal duplicated at same position 5x."""
    layers = []
    for _ in range(5):
        m = L("rectangle", 440, 296, 400, 240, WHITE, cornerRadius=16)
        m["effects"] = [make_drop_shadow()]
        layers.append(m)
    return H(layers, evts=evt(rect=5))
add("A9: 5 identical modals piled", a9())

def a10():
    return H(perfect_modal(), evts=evt(rect=0))
add("A10: 1 modal but 0 create events", a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def b11():
    return H(perfect_modal(modal_color=NAVY))
add("B11: navy modal (not white)", b11())

def b12():
    return H(perfect_modal(modal_color=RED))
add("B12: red modal", b12())

def b13():
    layers = perfect_modal()
    layers[0]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover",
                            "opacity":1,"visible":True}]
    return H(layers)
add("B13: image fill", b13())

def b14():
    layers = perfect_modal()
    layers[0]["fills"] = [{"kind":"gradient","stops":[
        {"position":0,"color":{"r":1,"g":1,"b":1,"a":1}},
        {"position":1,"color":{"r":0.8,"g":0.8,"b":0.8,"a":1}}],
        "opacity":1,"visible":True}]
    return H(layers)
add("B14: gradient fill", b14())

def b15():
    layers = perfect_modal()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=WHITE, weight=2)]
    return H(layers)
add("B15: stroke-only", b15())

def b16():
    layers = perfect_modal()
    layers[0]["fills"] = []
    return H(layers)
add("B16: empty fills", b16())

def b17():
    return H(perfect_modal(modal_color=NEAR_WHITE))
add("B17: near-white (within tol)", b17())

def b18():
    layers = perfect_modal()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: alpha=0 (invisible)", b18())

def b19():
    layers = perfect_modal()
    layers[0]["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: fillOpacity=0.05", b19())

def b20():
    layers = perfect_modal()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("B20: layer.opacity=0", b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def c21():
    return H(perfect_modal(modal_w=1200, modal_h=800))
add("C21: huge modal (1200×800)", c21())

def c22():
    return H(perfect_modal(modal_w=20, modal_h=12))
add("C22: tiny modal (20×12)", c22())

def c23():
    """Modal = entire frame size."""
    return H(perfect_modal(modal_w=1280, modal_h=832))
add("C23: modal = entire frame", c23())

def c24():
    """Modal 1×1 (degenerate)."""
    return H(perfect_modal(modal_w=1, modal_h=1))
add("C24: modal 1×1", c24())

def c25():
    """Modal with extreme aspect (long flat)."""
    return H(perfect_modal(modal_w=800, modal_h=20))
add("C25: modal 800×20 (super flat)", c25())

def c26():
    """Modal 20×800 (super tall)."""
    return H(perfect_modal(modal_w=20, modal_h=800))
add("C26: modal 20×800 (super tall)", c26())

def c27():
    """Modal at 100x60 small but valid."""
    return H(perfect_modal(modal_w=100, modal_h=60))
add("C27: small valid modal 100×60", c27())

def c28():
    """Modal 401×241 (just inside tolerance of 400×240)."""
    return H(perfect_modal(modal_w=401, modal_h=241))
add("C28: modal 401×241 (within tol)", c28())

def c29():
    """Modal 600×400."""
    return H(perfect_modal(modal_w=600, modal_h=400))
add("C29: modal 600×400", c29())

def c30():
    """Modal 800×500 (large but valid)."""
    return H(perfect_modal(modal_w=800, modal_h=500))
add("C30: modal 800×500", c30())


# ─── D. Position ────────────────────────────────────────────────────
def d31():
    """Modal at top-left."""
    layers = perfect_modal()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("D31: modal at top-left (0,0)", d31())

def d32():
    """Modal at top-right."""
    layers = perfect_modal()
    layers[0]["x"] = 880; layers[0]["y"] = 0
    return H(layers)
add("D32: modal at top-right", d32())

def d33():
    """Modal at bottom-left."""
    layers = perfect_modal()
    layers[0]["x"] = 0; layers[0]["y"] = 592
    return H(layers)
add("D33: modal at bottom-left", d33())

def d34():
    """Modal at bottom-right."""
    layers = perfect_modal()
    layers[0]["x"] = 880; layers[0]["y"] = 592
    return H(layers)
add("D34: modal at bottom-right", d34())

def d35():
    """Modal centered horizontally but not vertically."""
    layers = perfect_modal()
    layers[0]["y"] = 50  # at top
    return H(layers)
add("D35: modal h-centered, top", d35())

def d36():
    """Modal centered vertically but offset horizontally."""
    layers = perfect_modal()
    layers[0]["x"] = 100  # at left
    return H(layers)
add("D36: modal v-centered, left", d36())

def d37():
    """Modal off-frame entirely."""
    layers = perfect_modal()
    layers[0]["x"] = 1500; layers[0]["y"] = 1500
    return H(layers)
add("D37: modal off-frame", d37())

def d38():
    """Modal centered exactly (control)."""
    return H()
add("D38: modal centered (perfect)", d38())

def d39():
    """Modal centered + 5px x offset (within tol)."""
    layers = perfect_modal()
    layers[0]["x"] = layers[0]["x"] + 5
    return H(layers)
add("D39: modal centered + 5px (within tol)", d39())

def d40():
    """Modal centered + 30px (outside 12px tol)."""
    layers = perfect_modal()
    layers[0]["x"] = layers[0]["x"] + 30
    return H(layers)
add("D40: modal centered + 30px (outside tol)", d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def e41():
    """No corner radius."""
    layers = perfect_modal(radius=0)
    return H(layers)
add("E41: cornerRadius=0", e41())

def e42():
    """Below threshold (5 < 8)."""
    layers = perfect_modal(radius=5)
    return H(layers)
add("E42: cornerRadius=5 (below 8)", e42())

def e43():
    """At threshold (8)."""
    layers = perfect_modal(radius=8)
    return H(layers)
add("E43: cornerRadius=8 (at threshold)", e43())

def e44():
    """Below threshold (7)."""
    layers = perfect_modal(radius=7)
    return H(layers)
add("E44: cornerRadius=7 (just under)", e44())

def e45():
    """Modal rotated 45°."""
    layers = perfect_modal()
    layers[0]["rotation"] = 45
    return H(layers)
add("E45: rotated 45°", e45())

def e46():
    """Modal mirrored."""
    layers = perfect_modal()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E46: scaleX=-1", e46())

def e47():
    """Modal scaleY=-1."""
    layers = perfect_modal()
    layers[0]["scaleY"] = -1
    return H(layers)
add("E47: scaleY=-1", e47())

def e48():
    """Modal as ellipse."""
    s = make_layer("ellipse", x=440, y=296, w=400, h=240, fill=WHITE)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("E48: modal is ellipse", e48())

def e49():
    """Modal rotated 1° (under tol)."""
    layers = perfect_modal()
    layers[0]["rotation"] = 1
    return H(layers)
add("E49: rotated 1° (under tol)", e49())

def e50():
    """Modal cornerRadius=999 (full pill)."""
    layers = perfect_modal(radius=999)
    return H(layers)
add("E50: cornerRadius=999 (full pill)", e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def f51():
    """No drop shadow."""
    return H(perfect_modal(shadow=False))
add("F51: no drop shadow", f51())

def f52():
    """Layer blur instead of drop shadow."""
    layers = perfect_modal(shadow=False)
    layers[0]["effects"] = [{"kind":"layer_blur","radius":8,"visible":True}]
    return H(layers)
add("F52: blur instead of shadow", f52())

def f53():
    """Drop shadow with alpha=0 (invisible)."""
    layers = perfect_modal(shadow=False)
    layers[0]["effects"] = [make_drop_shadow(alpha=0.0)]
    return H(layers)
add("F53: drop shadow alpha=0", f53())

def f54():
    """Multi-effect: shadow + blur."""
    layers = perfect_modal()
    layers[0]["effects"].append({"kind":"layer_blur","radius":4,"visible":True})
    return H(layers)
add("F54: shadow + blur", f54())

def f55():
    """Drop shadow visible=False."""
    layers = perfect_modal()
    layers[0]["effects"][0]["visible"] = False
    return H(layers)
add("F55: shadow visible=False", f55())

def f56():
    """Modal with stroke as well."""
    layers = perfect_modal()
    layers[0]["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return H(layers)
add("F56: modal w/ stroke", f56())

def f57():
    """Modal with 5 drop shadows (extreme)."""
    layers = perfect_modal(shadow=False)
    layers[0]["effects"] = [make_drop_shadow(y=i*4, blur=8) for i in range(5)]
    return H(layers)
add("F57: 5 drop shadows", f57())

def f58():
    """Modal in a group inside frame."""
    layers = perfect_modal()
    g = {"id":"g","type":"group","x":0,"y":0,"w":0,"h":0,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("F58: modal in group in frame", f58())

def f59():
    """Modal partially off frame's right."""
    layers = perfect_modal()
    layers[0]["x"] = 1100
    return H(layers)
add("F59: modal partially off right", f59())

def f60():
    """Modal at exact edge-touching position (overlapping frame edges)."""
    layers = perfect_modal(modal_w=1280, modal_h=832)
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("F60: modal exactly = frame size", f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def g61():
    return H()
add("G61: perfect frame 1280×832", g61())

def g62():
    return H(perfect_modal(frame_w=400, frame_h=300, modal_w=200, modal_h=150),
             frame_w=400, frame_h=300)
add("G62: small frame 400×300", g62())

def g63():
    """Frame translated."""
    layers = perfect_modal()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G63: frame translated", g63())

def g64():
    """Frame rotated 45°."""
    layers = perfect_modal()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G64: frame rotated", g64())

def g65():
    """Frame stroked."""
    layers = perfect_modal()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=2)]
    return make_log([frame], evt())
add("G65: frame stroked", g65())

def g66():
    """Frame with image fill."""
    layers = perfect_modal()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind":"image","src":"bg.jpg","fit":"cover","opacity":1,"visible":True}]
    return make_log([frame], evt())
add("G66: frame image fill", g66())

def g67():
    """Frame 800×600."""
    return H(perfect_modal(frame_w=800, frame_h=600), frame_w=800, frame_h=600)
add("G67: frame 800×600", g67())

def g68():
    """Multiple frames, modal in 1st."""
    layers = perfect_modal()
    f1 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([], w=1280, h=832, x=1300)
    return make_log([f1, f2], evt(frame=2))
add("G68: 2 frames, modal in 1st", g68())


# ─── H. Tools / events ──────────────────────────────────────────────
def h69():
    return H(evts=evt(extras=[make_event("undo") for _ in range(20)]))
add("H69: 20 undos", h69())

def h70():
    """No align tool used."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("set_fill_color")]
    return H(evts=sem)
add("H70: no align tool", h70())

def h71():
    """No frame tool used."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("align_layers"),
           make_event("align_layers")]
    return H(evts=sem)
add("H71: no frame tool", h71())

def h72():
    """Pen tool."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen"),
           make_event("create_rectangle"),
           make_event("align_layers")]
    return H(evts=sem)
add("H72: pen tool", h72())

def h73():
    """create_rectangle=5."""
    return H(evts=evt(rect=5))
add("H73: create_rectangle=5", h73())

def h74():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(40)]))
add("H74: 40 moves", h74())

def h75():
    """20 align events."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y") for _ in range(20)]))
add("H75: 20 align events", h75())

def h76():
    """Created+deleted extra modals."""
    extras = [make_event("create_rectangle"), make_event("delete")]*3
    return H(evts=evt(extras=extras))
add("H76: 3 created+deleted", h76())

def h77():
    return H(evts=evt() + [make_event("session_end")]*5)
add("H77: 5 session_end", h77())

def h78():
    return H(evts=evt(set_fill=50))
add("H78: 50 set_fill events", h78())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def i79():
    layers = perfect_modal()
    g = {"id":"g","type":"group","x":0,"y":0,"w":400,"h":240,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("I79: modal in group in frame", i79())

def i80():
    layers = perfect_modal()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("I80: modal in section", i80())

def i81():
    return H(perfect_modal(), in_frame=False, evts=evt(rect=1, frame=0))
add("I81: modal on page (no frame)", i81())

def i82():
    layers = perfect_modal()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt(frame=3))
add("I82: modal 3-deep nested", i82())

def i83():
    layers = perfect_modal()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],
             "prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},
             "prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I83: modal on page 2", i83())

def i84():
    layers = perfect_modal()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("I84: modal in component", i84())

def i85():
    layers = perfect_modal()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("I85: modal in instance", i85())


# ─── J. Bizarre ──────────────────────────────────────────────────────
def j86():
    """Modal with negative coords."""
    layers = perfect_modal()
    layers[0]["x"] = -200; layers[0]["y"] = -100
    return H(layers)
add("J86: negative coords", j86())

def j87():
    """Modal rotated 180°."""
    layers = perfect_modal()
    layers[0]["rotation"] = 180
    return H(layers)
add("J87: rotated 180°", j87())

def j88():
    """Modal duplicated 5x at exact center."""
    layers = []
    for _ in range(5):
        m = L("rectangle", 440, 296, 400, 240, WHITE, cornerRadius=16)
        m["effects"] = [make_drop_shadow()]
        layers.append(m)
    return H(layers, evts=evt(rect=5))
add("J88: 5 modals piled at center", j88())

def j89():
    return make_log([], [make_event("session_start")])
add("J89: empty document", j89())

def j90():
    return H([])
add("J90: frame only", j90())

def j91():
    text = make_layer("text", x=440, y=300, w=400, h=240, fill=NAVY)
    text["content"] = "modal"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'modal'", j91())

def j92():
    """Modal is a star."""
    s = make_layer("star", x=440, y=296, w=400, h=240, fill=WHITE,
                    points=5, innerRatio=0.4, cornerRadius=16)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("J92: modal is star", j92())

def j93():
    """Modal is polygon 4 sides."""
    s = make_layer("polygon", x=440, y=296, w=400, h=240, fill=WHITE,
                    sides=4, cornerRadius=16)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("J93: modal is polygon", j93())

def j94():
    """Modal at exact center but no shadow, no radius."""
    layers = perfect_modal(radius=0, shadow=False)
    return H(layers)
add("J94: centered but bare", j94())

def j95():
    """Modal 1×1 at center."""
    layers = [L("rectangle", 640-0.5, 416-0.5, 1, 1, WHITE, cornerRadius=16)]
    layers[0]["effects"] = [make_drop_shadow()]
    return H(layers)
add("J95: modal 1×1 at center", j95())

def j96():
    return H()
add("J96: perfect modal (control)", j96())


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

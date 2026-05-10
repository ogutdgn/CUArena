"""100 edge cases for task 44 (avatar + status badge) — runs all and prints a sorted score table.

Task 44 prompt: 1 large avatar circle + 1 smaller status badge (green, with 2px white stroke)
overlapping the bottom-right of the avatar.
"""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_44" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
GREEN_BADGE = (0.06, 0.72, 0.50)


def evt(ellipse=2, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_avatar():
    avatar = L("ellipse", 480, 216, 320, 320, GRAY)  # large center circle
    badge = L("ellipse", 740, 476, 80, 80, GREEN_BADGE,
              strokes=[make_stroke(rgb=WHITE, weight=2)])  # small bottom-right
    return [avatar, badge]


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_avatar()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    layers = perfect_avatar() + [L("ellipse", 100, 100, 30, 30, NAVY)]
    return H(layers, evts=evt(ellipse=3))
add("A1: 3 ellipses (extra)", case_a1())

def case_a2():
    layers = [perfect_avatar()[0]]  # no badge
    return H(layers, evts=evt(ellipse=1))
add("A2: 1 ellipse (no badge)", case_a2())

def case_a3():
    return H([], evts=evt(ellipse=0))
add("A3: empty", case_a3())

def case_a4():
    layers = perfect_avatar() + perfect_avatar()  # 4 ellipses
    return H(layers, evts=evt(ellipse=4))
add("A4: 4 ellipses (2 avatars + 2 badges)", case_a4())

def case_a5():
    layers = perfect_avatar() + [L("rectangle", 100, 100, 30, 30, NAVY)]
    return H(layers, evts=evt(ellipse=2, extras=[make_event("create_rectangle")]))
add("A5: 2 ellipses + 1 rect", case_a5())

def case_a6():
    layers = [perfect_avatar()[1]]  # only badge
    return H(layers, evts=evt(ellipse=1))
add("A6: 1 ellipse (only badge)", case_a6())

def case_a7():
    layers = perfect_avatar()
    for i in range(5):
        layers.append(L("ellipse", 100+i*40, 700, 30, 30, [GREEN, RED, NAVY, ORANGE, GRAY][i]))
    return H(layers, evts=evt(ellipse=7))
add("A7: 7 ellipses", case_a7())

def case_a8():
    layers = perfect_avatar()
    layers.append(L("ellipse", 100, 100, 30, 30, GREEN_BADGE,
                    strokes=[make_stroke(rgb=WHITE, weight=2)]))
    return H(layers, evts=evt(ellipse=3))
add("A8: 3 ellipses (extra badge-like)", case_a8())

def case_a9():
    layers = [perfect_avatar()[0], perfect_avatar()[0]]  # 2 same avatars
    return H(layers, evts=evt(ellipse=2))
add("A9: 2 avatars (no badge)", case_a9())

def case_a10():
    layers = [perfect_avatar()[1], perfect_avatar()[1]]  # 2 badges
    return H(layers, evts=evt(ellipse=2))
add("A10: 2 badges (no avatar)", case_a10())


# ─── B. Colors ──────────────────────────────────────────────────────
def case_b11():
    layers = perfect_avatar()
    layers[0]["fills"] = [{"kind": "image", "src": "av.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return H(layers)
add("B11: avatar image fill", case_b11())

def case_b12():
    layers = perfect_avatar()
    layers[1]["fills"][0]["color"] = {"r": 0.95, "g": 0.20, "b": 0.20, "a": 1.0}  # red badge
    return H(layers)
add("B12: badge red (not green)", case_b12())

def case_b13():
    layers = perfect_avatar()
    layers[0]["fills"][0]["color"] = {"r": 0.06, "g": 0.72, "b": 0.50, "a": 1.0}  # avatar green too
    return H(layers)
add("B13: avatar green (same as badge, no contrast)", case_b13())

def case_b14():
    layers = perfect_avatar()
    layers[1]["strokes"] = []  # no stroke
    return H(layers)
add("B14: badge has no stroke", case_b14())

def case_b15():
    layers = perfect_avatar()
    layers[1]["strokes"] = [make_stroke(rgb=(0, 0, 0), weight=2)]  # black stroke
    return H(layers)
add("B15: badge black stroke", case_b15())

def case_b16():
    layers = perfect_avatar()
    layers[1]["strokes"] = [make_stroke(rgb=WHITE, weight=10)]  # very thick
    return H(layers)
add("B16: badge stroke 10px", case_b16())

def case_b17():
    layers = perfect_avatar()
    layers[0]["fills"][0]["opacity"] = 0.1  # avatar transparent
    return H(layers)
add("B17: avatar opacity 0.1", case_b17())

def case_b18():
    layers = perfect_avatar()
    layers[0]["fills"] = []
    return H(layers)
add("B18: avatar no fill", case_b18())

def case_b19():
    layers = perfect_avatar()
    layers[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r": 1, "g": 0, "b": 0, "a": 1}},
        {"position": 1, "color": {"r": 0, "g": 1, "b": 0, "a": 1}}],
        "opacity": 1, "visible": True}]
    return H(layers)
add("B19: avatar gradient", case_b19())

def case_b20():
    layers = perfect_avatar()
    layers[0]["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True}])
    return H(layers)
add("B20: avatar stacked fills", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 0, 0, 1280, 832, GRAY)  # avatar = full frame
    return H(layers)
add("C21: avatar = full frame", case_c21())

def case_c22():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 600, 400, 5, 5, GRAY)  # tiny avatar
    return H(layers)
add("C22: avatar 5×5", case_c22())

def case_c23():
    layers = perfect_avatar()
    layers[1] = L("ellipse", 740, 476, 1, 1, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C23: badge 1×1", case_c23())

def case_c24():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 480, 300, 600, 200, GRAY)  # squashed avatar
    return H(layers)
add("C24: avatar squashed 600×200", case_c24())

def case_c25():
    layers = perfect_avatar()
    layers[1] = L("ellipse", 740, 476, 200, 60, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C25: badge oval 200×60", case_c25())

def case_c26():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 480, 216, 100, 100, GRAY)
    layers[1] = L("ellipse", 480, 216, 320, 320, GREEN_BADGE,  # badge larger than avatar
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C26: badge bigger than avatar", case_c26())

def case_c27():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 480, 216, 320, 320, GRAY)
    layers[1] = L("ellipse", 480, 216, 320, 320, GREEN_BADGE,  # both same size
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C27: avatar and badge same size", case_c27())

def case_c28():
    layers = perfect_avatar()
    layers[1] = L("ellipse", 740, 476, 4, 4, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("C28: badge 4×4 (degenerate)", case_c28())

def case_c29():
    layers = perfect_avatar()
    layers[0] = L("ellipse", 100, 100, 1080, 600, GRAY)  # avatar huge
    return H(layers)
add("C29: avatar 1080×600 (huge)", case_c29())

def case_c30():
    layers = perfect_avatar()
    # Avatar same size as badge
    layers[0] = L("ellipse", 480, 216, 80, 80, GRAY)
    return H(layers)
add("C30: avatar = badge size 80x80", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    layers = perfect_avatar()
    layers[1]["x"] = 100
    layers[1]["y"] = 100  # badge top-left
    return H(layers)
add("D31: badge at top-left of frame (not on avatar)", case_d31())

def case_d32():
    layers = perfect_avatar()
    layers[1]["x"] = 480
    layers[1]["y"] = 216  # badge at avatar's top-left
    return H(layers)
add("D32: badge at top-left of avatar", case_d32())

def case_d33():
    layers = perfect_avatar()
    # Badge no longer overlaps avatar
    layers[1]["x"] = 1100
    layers[1]["y"] = 700
    return H(layers)
add("D33: badge far from avatar", case_d33())

def case_d34():
    return H()  # control
add("D34: perfect (control)", case_d34())

def case_d35():
    layers = perfect_avatar()
    # Badge centered ON avatar (not at edge)
    layers[1]["x"] = 600
    layers[1]["y"] = 336
    return H(layers)
add("D35: badge centered on avatar", case_d35())

def case_d36():
    layers = perfect_avatar()
    # Badge top-right of avatar
    layers[1]["x"] = 740
    layers[1]["y"] = 216
    return H(layers)
add("D36: badge at top-right of avatar", case_d36())

def case_d37():
    layers = perfect_avatar()
    for l in layers: l["x"] += 200
    return H(layers)
add("D37: shifted right", case_d37())

def case_d38():
    layers = perfect_avatar()
    layers[1]["x"] = 480
    layers[1]["y"] = 476  # badge bottom-left
    return H(layers)
add("D38: badge at bottom-left of avatar", case_d38())

def case_d39():
    layers = perfect_avatar()
    for l in layers:
        l["x"] -= 600
        l["y"] -= 400
    return H(layers)
add("D39: shifted off-frame upper-left", case_d39())

def case_d40():
    layers = perfect_avatar()
    # Badge off frame entirely
    layers[1]["x"] = 1300
    layers[1]["y"] = 200
    return H(layers)
add("D40: badge outside frame (right)", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    layers = perfect_avatar()
    layers[0]["rotation"] = 45
    return H(layers)
add("E41: avatar rotated 45°", case_e41())

def case_e42():
    layers = perfect_avatar()
    layers[1]["rotation"] = 90
    return H(layers)
add("E42: badge rotated 90°", case_e42())

def case_e43():
    layers = perfect_avatar()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E43: avatar mirrored", case_e43())

def case_e44():
    layers = perfect_avatar()
    layers[1] = L("rectangle", 740, 476, 80, 80, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers, evts=evt(ellipse=1))
add("E44: badge is a rectangle", case_e44())

def case_e45():
    layers = perfect_avatar()
    layers[0] = L("rectangle", 480, 216, 320, 320, GRAY)  # avatar is rect
    return H(layers, evts=evt(ellipse=1))
add("E45: avatar is a rectangle", case_e45())

def case_e46():
    layers = perfect_avatar()
    layers[0]["cornerRadius"] = 160
    return H(layers)
add("E46: avatar cornerRadius 160 (no effect on ellipse)", case_e46())

def case_e47():
    layers = perfect_avatar()
    layers[1]["cornerRadius"] = 0
    return H(layers)
add("E47: badge cornerRadius 0", case_e47())

def case_e48():
    layers = perfect_avatar()
    layers[0]["rotation"] = 4  # under tol
    return H(layers)
add("E48: avatar rotation 4° (under tol)", case_e48())

def case_e49():
    layers = perfect_avatar()
    layers[1]["scaleY"] = -1
    return H(layers)
add("E49: badge scaleY=-1", case_e49())

def case_e50():
    layers = perfect_avatar()
    layers[1]["rotation"] = 180
    return H(layers)
add("E50: badge rotated 180°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    layers = perfect_avatar()
    # Both ellipses identical
    layers[1] = L("ellipse", 480, 216, 320, 320, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F51: both ellipses same position+size", case_f51())

def case_f52():
    layers = perfect_avatar()
    # Badge much bigger than avatar (role swap)
    layers[1] = L("ellipse", 100, 100, 600, 600, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F52: badge huge, avatar small", case_f52())

def case_f53():
    layers = perfect_avatar()
    # Badge stroke is green (matches fill)
    layers[1]["strokes"] = [make_stroke(rgb=GREEN_BADGE, weight=2)]
    return H(layers)
add("F53: badge stroke green (no contrast)", case_f53())

def case_f54():
    layers = perfect_avatar()
    # Both ellipses same color
    layers[1]["fills"][0]["color"] = layers[0]["fills"][0]["color"]
    return H(layers)
add("F54: avatar+badge same color", case_f54())

def case_f55():
    layers = perfect_avatar()
    # Badge above avatar in y but offset
    layers[1] = L("ellipse", 740, 100, 80, 80, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F55: badge top-right (no overlap)", case_f55())

def case_f56():
    layers = perfect_avatar()
    # Badge has dashed stroke
    layers[1]["strokes"] = [make_stroke(rgb=WHITE, weight=2, dash={"dash": 4, "gap": 2})]
    return H(layers)
add("F56: badge dashed stroke", case_f56())

def case_f57():
    layers = perfect_avatar()
    # Both layers black
    for l in layers:
        l["fills"][0]["color"] = {"r": 0, "g": 0, "b": 0, "a": 1.0}
    return H(layers)
add("F57: both ellipses black", case_f57())

def case_f58():
    layers = perfect_avatar()
    # Badge stroke has 0 weight (invisible)
    layers[1]["strokes"] = [make_stroke(rgb=WHITE, weight=0)]
    return H(layers)
add("F58: badge stroke weight 0", case_f58())

def case_f59():
    layers = perfect_avatar()
    # Avatar has stroke
    layers[0]["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return H(layers)
add("F59: avatar has stroke", case_f59())

def case_f60():
    layers = perfect_avatar()
    # Avatar = badge size, badge is now bigger
    layers[0] = L("ellipse", 600, 400, 80, 80, GRAY)
    layers[1] = L("ellipse", 480, 216, 320, 320, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("F60: avatar tiny, badge huge (role swap)", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    layers = perfect_avatar()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    inner = make_frame(perfect_avatar(), w=600, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    return H(frame_w=2000, frame_h=2000)
add("G63: frame 2000x2000", case_g63())

def case_g64():
    layers = perfect_avatar()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G64: frame stroke", case_g64())

def case_g65():
    layers = perfect_avatar()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_avatar(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G66: 2 frames, avatar in 2nd", case_g66())

def case_g67():
    layers = perfect_avatar()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())

def case_g68():
    return H(frame_w=200, frame_h=200)
add("G68: frame 200x200", case_g68())

def case_g69():
    return make_log(perfect_avatar(), evt())
add("G69: no frame", case_g69())

def case_g70():
    return H(frame_w=1290, frame_h=842)
add("G70: frame 1290x842 (within tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    return H(evts=[make_event("session_start")])
add("H71: no events", case_h71())

def case_h72():
    sem = [make_event("session_start"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H72: events but no tool_change", case_h72())

def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_ellipse"), make_event("create_ellipse")]
    return H(evts=sem)
add("H73: rectangle tool used", case_h73())

def case_h74():
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H74: 50 undo events", case_h74())

def case_h75():
    return H(evts=evt(extras=[make_event("delete") for _ in range(20)]))
add("H75: many deletes", case_h75())

def case_h76():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse"),
           make_event("create_ellipse")]
    return H(evts=sem)
add("H76: only 1 create_ellipse event", case_h76())

def case_h77():
    return H(evts=evt(extras=[make_event("create_rectangle"), make_event("delete")]))
add("H77: rect created+deleted", case_h77())

def case_h78():
    return H(evts=evt(set_fill=20))
add("H78: 20 set_fill events", case_h78())

def case_h79():
    return H(evts=evt(extras=[make_event("session_end")] * 5))
add("H79: many session_end events", case_h79())

def case_h80():
    sem = [make_event("session_start")] + [make_event("create_ellipse")] * 5
    return H(evts=sem)
add("H80: 5 create_ellipse events", case_h80())


# ─── I. Hierarchy ───────────────────────────────────────────────────
def case_i81():
    layers = perfect_avatar()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: in group inside frame", case_i81())

def case_i82():
    avatar = perfect_avatar()
    f1 = make_frame([avatar[0]], w=640, h=832)
    f2 = make_frame([avatar[1]], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: split across 2 frames", case_i82())

def case_i83():
    layers = perfect_avatar()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0,
               "w": 1280, "h": 832, "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: inside section", case_i83())

def case_i84():
    layers = perfect_avatar()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())

def case_i85():
    avatar = perfect_avatar()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(avatar, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I85: avatar on page 2", case_i85())

def case_i86():
    avatar = perfect_avatar()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": avatar}
    return make_log([component], evt())
add("I86: inside component", case_i86())

def case_i87():
    return make_log(perfect_avatar(), evt())
add("I87: on page (no frame)", case_i87())

def case_i88():
    avatar = perfect_avatar()
    f = make_frame([avatar[0]], w=1280, h=832)
    return make_log([f, avatar[1]], evt())
add("I88: avatar in frame, badge on page", case_i88())

def case_i89():
    avatar = perfect_avatar()
    inner = make_frame([avatar[0]], w=600, h=600)
    outer = make_frame([inner, avatar[1]], w=1280, h=832)
    return make_log([outer], evt())
add("I89: avatar in inner, badge in outer frame", case_i89())

def case_i90():
    return H(frame_fill=(0, 0, 0))
add("I90: black frame", case_i90())


# ─── J. Bizarre ─────────────────────────────────────────────────────
def case_j91():
    layers = perfect_avatar()
    layers[0]["scaleX"] = -1
    return H(layers)
add("J91: avatar mirrored", case_j91())

def case_j92():
    layers = perfect_avatar()
    text = make_layer("text", x=100, y=100, w=200, h=50, fill=NAVY)
    text["content"] = "avatar"
    return H(layers + [text])
add("J92: avatar + text 'avatar'", case_j92())

def case_j93():
    layers = [L("ellipse", 0, 0, 1280, 832, GRAY),
              L("ellipse", 0, 0, 1280, 832, GREEN_BADGE,
                strokes=[make_stroke(rgb=WHITE, weight=2)])]
    return H(layers)
add("J93: both ellipses = full frame", case_j93())

def case_j94():
    layers = perfect_avatar()
    layers[0]["fills"] = []
    layers[0]["strokes"] = []
    return H(layers)
add("J94: avatar invisible", case_j94())

def case_j95():
    layers = perfect_avatar()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("J95: avatar alpha=0", case_j95())

def case_j96():
    layers = perfect_avatar()
    layers[1]["visible"] = False
    return H(layers)
add("J96: badge visible=False", case_j96())

def case_j97():
    layers = perfect_avatar()
    layers[0]["opacity"] = 0
    return H(layers)
add("J97: avatar opacity=0", case_j97())

def case_j98():
    layers = perfect_avatar()
    for l in layers: l["y"] -= 1000
    return H(layers)
add("J98: shifted up off-screen", case_j98())

def case_j99():
    layers = perfect_avatar()
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

"""Round 3 — novel deception edge cases for task 44 (avatar + status badge)."""
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
NEAR_GREEN = (0.10, 0.70, 0.55)


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
    avatar = L("ellipse", 480, 216, 320, 320, GRAY)
    badge = L("ellipse", 740, 476, 80, 80, GREEN_BADGE,
              strokes=[make_stroke(rgb=WHITE, weight=2)])
    return [avatar, badge]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_avatar()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Avatar rotated 4° (under tol=2)."""
    layers = perfect_avatar()
    layers[0]["rotation"] = 4
    return H(layers)
add("K1: avatar rotation 4°", k1())

def k2():
    """Badge stroke 3.5px (off-tol from 2)."""
    layers = perfect_avatar()
    layers[1]["strokes"] = [make_stroke(rgb=WHITE, weight=3.5)]
    return H(layers)
add("K2: badge stroke 3.5px", k2())

def k3():
    """Badge near-green (within tol)."""
    layers = perfect_avatar()
    layers[1]["fills"][0]["color"] = {"r": NEAR_GREEN[0], "g": NEAR_GREEN[1], "b": NEAR_GREEN[2], "a": 1.0}
    return H(layers)
add("K3: badge near-green (within tol)", k3())

def k4():
    """Avatar+badge same shade (no contrast)."""
    layers = perfect_avatar()
    layers[0]["fills"][0]["color"] = {"r": 0.06, "g": 0.72, "b": 0.50, "a": 1.0}
    return H(layers)
add("K4: avatar same green as badge", k4())

def k5():
    """Badge stroke alpha=0."""
    layers = perfect_avatar()
    stroke = make_stroke(rgb=WHITE, weight=2)
    stroke["paint"]["color"]["a"] = 0
    layers[1]["strokes"] = [stroke]
    return H(layers)
add("K5: badge stroke alpha=0", k5())

def k6():
    """Badge stroke visible=False."""
    layers = perfect_avatar()
    stroke = make_stroke(rgb=WHITE, weight=2)
    stroke["visible"] = False
    layers[1]["strokes"] = [stroke]
    return H(layers)
add("K6: badge stroke visible=False", k6())

def k7():
    """Badge cornerRadius=20 (already round, redundant)."""
    layers = perfect_avatar()
    layers[1]["cornerRadius"] = 20
    return H(layers)
add("K7: badge cornerRadius=20", k7())

def k8():
    """Badge stroke weight=0."""
    layers = perfect_avatar()
    layers[1]["strokes"] = [make_stroke(rgb=WHITE, weight=0)]
    return H(layers)
add("K8: badge stroke weight=0", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Avatar fill alpha=0."""
    layers = perfect_avatar()
    layers[0]["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: avatar alpha=0", l1())

def l2():
    """Avatar visible=False."""
    layers = perfect_avatar()
    layers[0]["visible"] = False
    return H(layers)
add("L2: avatar visible=False", l2())

def l3():
    """Avatar layer opacity=0."""
    layers = perfect_avatar()
    layers[0]["opacity"] = 0
    return H(layers)
add("L3: avatar opacity=0", l3())

def l4():
    """Badge fill visible=False."""
    layers = perfect_avatar()
    layers[1]["fills"][0]["visible"] = False
    return H(layers)
add("L4: badge fill visible=False", l4())

def l5():
    """Both layers fill opacity=0.05."""
    layers = perfect_avatar()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("L5: both fillOpacity=0.05", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Both ellipses identical (overlap perfectly)."""
    layers = perfect_avatar()
    layers[1] = L("ellipse", 480, 216, 320, 320, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("M1: both ellipses identical", m1())

def m2():
    """Badge bigger than avatar (role swap)."""
    layers = perfect_avatar()
    layers[1] = L("ellipse", 100, 100, 600, 600, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    layers[0] = L("ellipse", 600, 400, 80, 80, GRAY)
    return H(layers)
add("M2: badge bigger than avatar", m2())

def m3():
    """Avatar = full frame."""
    layers = perfect_avatar()
    layers[0] = L("ellipse", 0, 0, 1280, 832, GRAY)
    return H(layers)
add("M3: avatar = full frame", m3())

def m4():
    """Frame 2000x2000."""
    return H(frame_w=2000, frame_h=2000)
add("M4: frame 2000x2000", m4())

def m5():
    """Badge at top-left corner (NOT bottom-right)."""
    layers = perfect_avatar()
    layers[1]["x"] = 100
    layers[1]["y"] = 100
    return H(layers)
add("M5: badge at top-left corner", m5())

def m6():
    """Avatar tiny (40x40), badge huge (300x300)."""
    layers = perfect_avatar()
    layers[0] = L("ellipse", 600, 400, 40, 40, GRAY)
    layers[1] = L("ellipse", 100, 100, 300, 300, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers)
add("M6: avatar tiny, badge huge", m6())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Avatar in 1 frame, badge in another."""
    avatar = perfect_avatar()
    f1 = make_frame([avatar[0]], w=1280, h=832)
    f2 = make_frame([avatar[1]], w=400, h=400)
    return make_log([f1, f2], evt())
add("N1: avatar/badge in different frames", n1())

def n2():
    """Each shape in own frame."""
    avatar = perfect_avatar()
    frames = [make_frame([s], w=1280, h=832) for s in avatar]
    return make_log(frames, evt())
add("N2: each shape in own frame", n2())

def n3():
    """Avatar inside component (no frame)."""
    avatar = perfect_avatar()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": avatar}
    return make_log([component], evt())
add("N3: inside component", n3())

def n4():
    """Both ellipses on page 2."""
    avatar = perfect_avatar()
    page1 = {"id": "p1", "children": [], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    frame = make_frame(avatar, w=1280, h=832)
    page2 = {"id": "p2", "children": [frame], "prototypeSettings": {"device": None,
             "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}}, "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("N4: avatar on page 2", n4())


# ─── O. Wrong types substituted ──────────────────────────────────────
def o1():
    """Avatar and badge are rectangles."""
    layers = perfect_avatar()
    layers[0] = L("rectangle", 480, 216, 320, 320, GRAY)
    layers[1] = L("rectangle", 740, 476, 80, 80, GREEN_BADGE,
                  strokes=[make_stroke(rgb=WHITE, weight=2)])
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")] * 2))
add("O1: rectangles instead of ellipses", o1())

def o2():
    """Avatar = star."""
    layers = [make_layer("star", x=480, y=216, w=320, h=320, fill=GRAY, points=5),
              perfect_avatar()[1]]
    return H(layers, evts=evt(ellipse=1, extras=[make_event("create_star")]))
add("O2: avatar is a star", o2())

def o3():
    """Badge = polygon (triangle)."""
    layers = [perfect_avatar()[0],
              make_layer("polygon", x=740, y=476, w=80, h=80, fill=GREEN_BADGE,
                         strokes=[make_stroke(rgb=WHITE, weight=2)], sides=3)]
    return H(layers, evts=evt(ellipse=1, extras=[make_event("create_polygon")]))
add("O3: badge is a polygon", o3())

def o4():
    """Avatar+badge as text."""
    layers = [make_layer("text", x=480, y=216, w=320, h=320, fill=GRAY),
              make_layer("text", x=740, y=476, w=80, h=80, fill=GREEN_BADGE)]
    layers[0]["content"] = "AV"
    layers[1]["content"] = "."
    return H(layers, evts=[make_event("session_start"), make_event("create_text")])
add("O4: shapes are text", o4())


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

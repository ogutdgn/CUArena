"""Round 3 novel deceptions for task 23 — frame + dark-gray sidebar with
constraints horizontal=left, vertical=stretch."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, NAVY, WHITE, RED, GREEN, PURPLE,
)
from tasks import task_23_stretchy_sidebar as t
T = t.task

DARK_GRAY = (0.30, 0.30, 0.30)


def evt(rect=1, set_fill=1, frame=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("tool_change", before="frame", after="rectangle")]
    for _ in range(frame): sem.append(make_event("create_frame"))
    for _ in range(rect):  sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_sidebar(frame_w=1280, frame_h=832, sidebar_w=None,
                    sidebar_color=DARK_GRAY):
    if sidebar_w is None:
        sidebar_w = int(frame_w * 0.17)
    sidebar = L("rectangle", 0, 0, sidebar_w, frame_h, sidebar_color)
    sidebar["constraints"] = {"horizontal": "left", "vertical": "stretch"}
    return [sidebar]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_sidebar(frame_w, frame_h)
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Sidebar at 7px from left (just outside 8px tolerance)."""
    layers = [L("rectangle", 7, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("K1: sidebar 7px from left edge", k1())

def k2():
    """Sidebar at 9px from left (just outside)."""
    layers = [L("rectangle", 9, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("K2: sidebar 9px from left edge (just out)", k2())

def k3():
    """Sidebar rotated 1.9° (just under tolerance)."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 1.9
    return H(layers)
add("K3: rotated 1.9° (under tol)", k3())

def k4():
    """Sidebar rotated 2.5° (just over tolerance)."""
    layers = perfect_sidebar()
    layers[0]["rotation"] = 2.5
    return H(layers)
add("K4: rotated 2.5° (over tol)", k4())

def k5():
    """Sidebar with cornerRadius=60 on 200-wide (frac=0.3 at threshold)."""
    layers = perfect_sidebar()
    layers[0]["cornerRadius"] = 60  # 60/200 = 0.3
    return H(layers)
add("K5: cornerRadius=60 (frac at 0.3)", k5())

def k6():
    """Sidebar with cornerRadius=70 (frac=0.35, over)."""
    layers = perfect_sidebar()
    layers[0]["cornerRadius"] = 70
    return H(layers)
add("K6: cornerRadius=70 (frac=0.35)", k6())

def k7():
    """Width frac at exactly 8% (lower boundary)."""
    return H(perfect_sidebar(sidebar_w=102))
add("K7: sidebar at 8% (boundary)", k7())

def k8():
    """Width frac at exactly 30% (upper boundary)."""
    return H(perfect_sidebar(sidebar_w=384))
add("K8: sidebar at 30% (boundary)", k8())

def k9():
    """Width frac just under 8% (95px)."""
    return H(perfect_sidebar(sidebar_w=95))
add("K9: sidebar just under 8%", k9())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Sidebar visible=False on layer."""
    layers = perfect_sidebar()
    layers[0]["visible"] = False
    return H(layers)
add("L1: layer.visible=False", l1())

def l2():
    """Sidebar fill visible=False."""
    layers = perfect_sidebar()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L2: fill.visible=False", l2())

def l3():
    """Sidebar opacity=0.4 (under threshold 0.5)."""
    layers = perfect_sidebar()
    layers[0]["opacity"] = 0.4
    return H(layers)
add("L3: opacity=0.4 (under threshold)", l3())

def l4():
    """Sidebar fill alpha=0.4."""
    layers = perfect_sidebar()
    layers[0]["fills"][0]["color"]["a"] = 0.4
    return H(layers)
add("L4: fill alpha=0.4", l4())

def l5():
    """Sidebar fill opacity=0.4."""
    layers = perfect_sidebar()
    layers[0]["fills"][0]["opacity"] = 0.4
    return H(layers)
add("L5: fill opacity=0.4", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Sidebar in middle of frame (constraint=left but x=600 anyway)."""
    layers = [L("rectangle", 600, 0, 200, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("M1: sidebar at x=600 despite constraint=left", m1())

def m2():
    """Sidebar overlapping frame's right edge."""
    layers = [L("rectangle", 1100, 0, 300, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("M2: sidebar overlapping right edge", m2())

def m3():
    """Sidebar covers entire frame (1280×832)."""
    layers = [L("rectangle", 0, 0, 1280, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("M3: sidebar = entire frame", m3())

def m4():
    """Sidebar w=1500 (wider than frame)."""
    layers = [L("rectangle", 0, 0, 1500, 832, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("M4: sidebar 1500px wide", m4())

def m5():
    """Sidebar h=400 (half frame height) — still tall but not stretched."""
    layers = [L("rectangle", 0, 200, 200, 400, DARK_GRAY)]
    layers[0]["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H(layers)
add("M5: sidebar h=400 (half height)", m5())

def m6():
    """Sidebar with random vivid color."""
    layers = perfect_sidebar(sidebar_color=(1.0, 0.0, 0.5))
    return H(layers)
add("M6: sidebar magenta (not gray)", m6())

def m7():
    """Sidebar with cornerRadius matching width (full pill)."""
    layers = perfect_sidebar()
    layers[0]["cornerRadius"] = 200
    return H(layers)
add("M7: sidebar full pill (cornerRadius=w)", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Sidebar inside instance (variant of frame)."""
    layers = perfect_sidebar()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("N1: sidebar in instance (no real frame)", n1())

def n2():
    """Sidebar inside section (no frame)."""
    layers = perfect_sidebar()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("N2: sidebar in section (no real frame)", n2())

def n3():
    """Sidebar in group at page level (no frame)."""
    layers = perfect_sidebar()
    g = {"id":"g","type":"group","x":0,"y":0,"w":200,"h":832,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([g], evt())
add("N3: sidebar in group on page", n3())

def n4():
    """Sidebar in frame, frame nested in group."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832)
    g = {"id":"g","type":"group","x":0,"y":0,"w":1280,"h":832,
         "fills":[],"strokes":[],"effects":[],"children":[frame]}
    return make_log([g], evt())
add("N4: frame in group", n4())

def n5():
    """Sidebar in 'frame' but frame has rotation!=0."""
    layers = perfect_sidebar()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 30
    return make_log([frame], evt())
add("N5: frame rotated 30°", n5())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Sidebar is an ellipse."""
    s = make_layer("ellipse", x=0, y=0, w=200, h=832, fill=DARK_GRAY)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("O1: sidebar is ellipse", o1())

def o2():
    """Sidebar is polygon."""
    s = make_layer("polygon", x=0, y=0, w=200, h=832, fill=DARK_GRAY, sides=4)
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("O2: sidebar is polygon", o2())

def o3():
    """Sidebar is line, no width."""
    s = make_layer("line", x=0, y=0, w=2, h=832, fill=DARK_GRAY)
    s["p1"] = {"x":0,"y":0}; s["p2"] = {"x":0,"y":832}
    s["constraints"] = {"horizontal":"left","vertical":"stretch"}
    return H([s], evts=evt(rect=0))
add("O3: sidebar is line", o3())

def o4():
    """Sidebar is text 'sidebar'."""
    s = make_layer("text", x=0, y=0, w=200, h=832, fill=DARK_GRAY)
    s["content"] = "sidebar"
    return make_log([make_frame([s], w=1280, h=832)],
                     [make_event("session_start"), make_event("create_text")])
add("O4: sidebar is text", o4())


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

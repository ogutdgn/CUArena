"""Round 3 — novel-deception edge cases for task 16."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_16_speech_bubble as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
LIGHT_GRAY = (0.85, 0.85, 0.85)
DARK_GRAY = (0.30, 0.30, 0.30)


def evt(rect=1, polygon=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.append(make_event("tool_change", before="rectangle", after="polygon"))
    for _ in range(polygon):
        sem.append(make_event("create_polygon"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bubble():
    bubble = L("rectangle", 400, 250, 480, 240, LIGHT_GRAY, cornerRadius=16)
    bubble["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    tail = make_layer("polygon", x=420, y=470, w=80, h=80, fill=LIGHT_GRAY, sides=3)
    tail["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    return [bubble, tail]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bubble()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Bubble cornerRadius=8 (just at min)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 8
    return H(layers)
add("K1: cornerRadius=8 (at min)", k1())

def k2():
    """Bubble cornerRadius=7 (just under min)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 7
    return H(layers)
add("K2: cornerRadius=7 (just under min)", k2())

def k3():
    """Bubble rotation=2° (at tol edge)."""
    layers = perfect_bubble()
    layers[0]["rotation"] = 2
    return H(layers)
add("K3: bubble rotation=2° (at tol)", k3())

def k4():
    """Strokes 3px (at tol edge for 2±1)."""
    layers = perfect_bubble()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=3)]
    return H(layers)
add("K4: strokes 3px (at tol edge)", k4())

def k5():
    """Color #aaa (within tol of LIGHT_GRAY=#d9d9d9)."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"][0]["color"] = {"r":0.7,"g":0.7,"b":0.7,"a":1}  # within 0.20 tol
    return H(layers)
add("K5: 0.7 gray (within color tol)", k5())

def k6():
    """Tail polygon area = 1/3.5 of bubble (just over min_ratio=3)."""
    layers = perfect_bubble()
    # bubble = 480x240 = 115200; tail must be < 115200/3 = 38400
    layers[1]["w"] = 200; layers[1]["h"] = 192  # = 38400
    return H(layers)
add("K6: tail = bubble/3 (at ratio threshold)", k6())

def k7():
    """Reverse z-order (tail drawn first)."""
    layers = perfect_bubble()[::-1]
    return H(layers)
add("K7: reverse z-order", k7())

def k8():
    """Bubble cornerRadius=120 (= half-h, full pill on short axis)."""
    layers = perfect_bubble()
    layers[0]["cornerRadius"] = 120
    return H(layers)
add("K8: cornerRadius=120 (full pill on h-axis)", k8())

def k9():
    """Tail rotation=3° (over tol)."""
    layers = perfect_bubble()
    layers[1]["rotation"] = 3
    return H(layers)
add("K9: tail rotation=3°", k9())

def k10():
    """Bubble & tail share same x,y (overlap fully)."""
    layers = perfect_bubble()
    layers[1]["x"] = 400; layers[1]["y"] = 250
    return H(layers)
add("K10: bubble & tail at same position", k10())


# ─── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Bubble alpha=0."""
    layers = perfect_bubble()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: bubble alpha=0", l1())

def l2():
    """Bubble visible=False."""
    layers = perfect_bubble()
    layers[0]["visible"] = False
    return H(layers)
add("L2: bubble visible=False", l2())

def l3():
    """Bubble opacity=0."""
    layers = perfect_bubble()
    layers[0]["opacity"] = 0.0
    return H(layers)
add("L3: bubble opacity=0", l3())

def l4():
    """Tail invisible."""
    layers = perfect_bubble()
    layers[1]["visible"] = False
    return H(layers)
add("L4: tail visible=False", l4())

def l5():
    """Both with image fills."""
    layers = perfect_bubble()
    for l in layers:
        l["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("L5: both image fills", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Both 1×1 (degenerate)."""
    layers = perfect_bubble()
    for l in layers:
        l["w"] = 1; l["h"] = 1
    return H(layers)
add("M1: both 1×1", m1())

def m2():
    """Bubble = full frame."""
    layers = perfect_bubble()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    return H(layers)
add("M2: bubble = full frame", m2())

def m3():
    """Tail at frame top (no overlap with bubble)."""
    layers = perfect_bubble()
    layers[1]["x"] = 50; layers[1]["y"] = 50
    return H(layers)
add("M3: tail at top-left frame corner", m3())

def m4():
    """Tail = bubble size (same large)."""
    layers = perfect_bubble()
    layers[1]["w"] = 480; layers[1]["h"] = 240
    return H(layers)
add("M4: tail same size as bubble", m4())

def m5():
    """Tail covers bubble."""
    layers = perfect_bubble()
    layers[1]["x"] = 380; layers[1]["y"] = 230
    layers[1]["w"] = 520; layers[1]["h"] = 280
    return H(layers)
add("M5: tail fully covers bubble", m5())

def m6():
    """Both flipped."""
    layers = perfect_bubble()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("M6: both flipped", m6())

def m7():
    """Bubble + 3 polygons (extras)."""
    layers = perfect_bubble()
    for i in range(2):
        extra = make_layer("polygon", x=900+i*60, y=470, w=40, h=40,
                           fill=LIGHT_GRAY, sides=3)
        extra["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
        layers.append(extra)
    return H(layers, evts=evt(rect=1, polygon=3))
add("M7: 1 rect + 3 polygons", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """No frame."""
    return H(perfect_bubble(), in_frame=False)
add("N1: no frame", n1())

def n2():
    """Each in own frame."""
    layers = perfect_bubble()
    f1 = make_frame([layers[0]], w=400, h=400)
    f2 = make_frame([layers[1]], w=400, h=400)
    return make_log([f1, f2], evt())
add("N2: each in own frame", n2())

def n3():
    """In component."""
    layers = perfect_bubble()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: in component", n3())

def n4():
    """Bubble in frame, tail outside."""
    layers = perfect_bubble()
    frame = make_frame([layers[0]], w=1280, h=832)
    return make_log([frame, layers[1]], evt())
add("N4: bubble in frame, tail outside", n4())


# ─── O. Wrong types ──────────────────────────────────────────────────
def o1():
    """Bubble as polygon (sides=4)."""
    layers = perfect_bubble()
    layers[0] = make_layer("polygon", x=400, y=250, w=480, h=240, fill=LIGHT_GRAY,
                            sides=4)
    layers[0]["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    return H(layers, evts=evt(rect=0, polygon=2))
add("O1: bubble as polygon (no rectangle)", o1())

def o2():
    """Tail as ellipse."""
    layers = perfect_bubble()
    layers[1] = make_layer("ellipse", x=420, y=470, w=80, h=80, fill=LIGHT_GRAY)
    layers[1]["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    return H(layers, evts=evt(rect=1, polygon=0, extras=[make_event("create_ellipse")]))
add("O2: tail as ellipse (no polygon)", o2())

def o3():
    """Tail as star."""
    layers = perfect_bubble()
    layers[1] = make_layer("star", x=420, y=470, w=80, h=80, fill=LIGHT_GRAY,
                            points=5, innerRatio=0.4)
    layers[1]["strokes"] = [make_stroke(rgb=DARK_GRAY, weight=2)]
    return H(layers, evts=evt(rect=1, polygon=0, extras=[make_event("create_star")]))
add("O3: tail as star (no polygon)", o3())


# ─── Run ─────────────────────────────────────────────────────────────
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

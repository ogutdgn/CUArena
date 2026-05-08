"""Round 3 — novel-deception edge cases for task 13."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, PINK, ORANGE, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN,
)
from tasks import task_13_night_sky as t
T = t.task

GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(line=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(line):
        sem.append(make_event("create_line"))
    sem.extend(extras)
    return sem


def perfect_hashtag():
    h1 = make_layer("line", x=300, y=270, w=300, h=4, fill=NAVY)
    h1["rotation"] = 0; h1["p1"] = {"x":0,"y":0}; h1["p2"] = {"x":300,"y":0}
    h2 = make_layer("line", x=300, y=400, w=300, h=4, fill=NAVY)
    h2["rotation"] = 0; h2["p1"] = {"x":0,"y":0}; h2["p2"] = {"x":300,"y":0}
    v1 = make_layer("line", x=300, y=200, w=300, h=4, fill=NAVY)
    v1["rotation"] = 90; v1["p1"] = {"x":0,"y":0}; v1["p2"] = {"x":300,"y":0}
    v2 = make_layer("line", x=420, y=200, w=300, h=4, fill=NAVY)
    v2["rotation"] = 90; v2["p1"] = {"x":0,"y":0}; v2["p2"] = {"x":300,"y":0}
    return [h1, h2, v1, v2]


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_hashtag()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Each line rotated by 4° (under tol=5°)."""
    layers = perfect_hashtag()
    for l in layers:
        l["rotation"] += 4
    return H(layers)
add("K1: all lines rotated +4° (under tol=5)", k1())

def k2():
    """Lines at 5°, 5°, 95°, 95° (just over tol)."""
    layers = perfect_hashtag()
    layers[0]["rotation"] = 5; layers[1]["rotation"] = 5
    layers[2]["rotation"] = 95; layers[3]["rotation"] = 95
    return H(layers)
add("K2: rotations 5/5/95/95 (just over tol=5)", k2())

def k3():
    """All 4 lines at rotation=45° (diagonal X pattern, NOT #)."""
    layers = perfect_hashtag()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("K3: all rotations=45 (diagonal pile)", k3())

def k4():
    """1 line at rotation=180 (= 0 visually but breaks LayersHaveRotations)."""
    layers = perfect_hashtag()
    layers[0]["rotation"] = 180
    return H(layers)
add("K4: 1 line rotation=180", k4())

def k5():
    """Lines stacked at 45°+135° = X pattern (not #)."""
    layers = perfect_hashtag()
    layers[0]["rotation"] = 45; layers[1]["rotation"] = 45
    layers[2]["rotation"] = 135; layers[3]["rotation"] = 135
    return H(layers)
add("K5: 45/135 X pattern (not #)", k5())

def k6():
    """All lines fillOpacity=0.49 (just under min)."""
    layers = perfect_hashtag()
    for l in layers:
        l["fills"][0]["opacity"] = 0.49
    return H(layers)
add("K6: fillOpacity=0.49 (under min_opacity)", k6())

def k7():
    """Reverse z-order (no functional change for non-overlapping lines)."""
    layers = perfect_hashtag()[::-1]
    return H(layers)
add("K7: reverse z-order", k7())

def k8():
    """Lines all stacked at one center."""
    layers = perfect_hashtag()
    for l in layers:
        l["x"] = 600; l["y"] = 400
    return H(layers)
add("K8: all 4 lines at same point", k8())

def k9():
    """Tiny lines (15px each — just under min_w=20)."""
    layers = perfect_hashtag()
    for l in layers:
        l["w"] = 15; l["h"] = 4 if l["rotation"] == 0 else 15
    return H(layers)
add("K9: lines 15px (under min_w=20)", k9())

def k10():
    """All lines extending way past frame bounds."""
    layers = perfect_hashtag()
    for l in layers:
        l["x"] -= 800; l["w"] = 2000
    return H(layers)
add("K10: lines extend far past frame", k10())


# ─── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """All lines have alpha=0 fills + no strokes."""
    layers = perfect_hashtag()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
        l["strokes"] = []
    return H(layers)
add("L1: alpha=0 + no strokes", l1())

def l2():
    """All lines visible=False."""
    layers = perfect_hashtag()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("L2: layer visible=False", l2())

def l3():
    """All lines opacity=0."""
    layers = perfect_hashtag()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("L3: layer opacity=0", l3())

def l4():
    """All lines: fills empty AND strokes opacity=0.05."""
    layers = perfect_hashtag()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
        # opacity not directly on stroke object in our schema; use weight=0.5 instead
    # Actually we'd need stroke alpha. Use color alpha=0 for now
    for l in layers:
        l["strokes"] = [{"paint":{"kind":"solid","color":{"r":0,"g":0,"b":0,"a":0.0}},
                         "weight":2,"alignment":"center","dash":None,"visible":True}]
    return H(layers)
add("L4: fills empty + strokes alpha=0", l4())

def l5():
    """1 line with image fill, 3 normal."""
    layers = perfect_hashtag()
    layers[0]["fills"] = [{"kind":"image","src":"x.jpg","fit":"cover","opacity":1,"visible":True}]
    return H(layers)
add("L5: 1 line image fill", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Lines sized as 1×1 dots."""
    layers = perfect_hashtag()
    for l in layers:
        l["w"] = 1; l["h"] = 1
    return H(layers)
add("M1: lines = 1×1 (dots)", m1())

def m2():
    """All lines = full frame size (banners)."""
    layers = perfect_hashtag()
    for l in layers:
        l["x"] = 0; l["y"] = 0; l["w"] = 1280; l["h"] = 832
    return H(layers)
add("M2: lines = full frame", m2())

def m3():
    """Lines as 2x2 grid pattern (4 lines all parallel)."""
    layers = perfect_hashtag()
    # Make all rotation=0 (horizontal) but at 4 different positions
    for l in layers:
        l["rotation"] = 0
    layers[0]["x"] = 200; layers[0]["y"] = 200
    layers[1]["x"] = 200; layers[1]["y"] = 350
    layers[2]["x"] = 200; layers[2]["y"] = 500
    layers[3]["x"] = 200; layers[3]["y"] = 650
    return H(layers)
add("M3: 4 horizontals stacked (no #)", m3())

def m4():
    """3 lines piled, 1 line apart."""
    layers = perfect_hashtag()
    layers[0]["x"] = layers[1]["x"] = layers[2]["x"] = 500
    layers[0]["y"] = layers[1]["y"] = layers[2]["y"] = 400
    return H(layers)
add("M4: 3 lines piled + 1 apart", m4())

def m5():
    """All 4 lines at 45° (diagonal)."""
    layers = perfect_hashtag()
    for l in layers:
        l["rotation"] = 45
    layers[1]["x"] = 600
    return H(layers)
add("M5: all lines at 45°", m5())

def m6():
    """Mirror flip on horizontal."""
    layers = perfect_hashtag()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("M6: all lines flipped X", m6())

def m7():
    """Lines super thick (h=50) — look like rectangles."""
    layers = perfect_hashtag()
    for l in layers:
        l["h"] = 50
    return H(layers)
add("M7: all lines h=50 (looks like rect)", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Lines on page (no frame)."""
    layers = perfect_hashtag()
    return make_log(layers, evt())
add("N1: lines on page (no frame)", n1())

def n2():
    """Each line in its own frame."""
    layers = perfect_hashtag()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N2: each line in own frame", n2())

def n3():
    """Lines inside a Component instance."""
    layers = perfect_hashtag()
    component = {"id":"comp_1","type":"component","x":0,"y":0,"w":1280,"h":832,
                 "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([component], evt())
add("N3: lines in component", n3())

def n4():
    """Lines split: 2 in frame, 2 outside frame as siblings."""
    layers = perfect_hashtag()
    frame = make_frame(layers[:2], w=1280, h=832)
    return make_log([frame, *layers[2:]], evt())
add("N4: 2 in frame, 2 outside", n4())


# ─── O. Wrong types ──────────────────────────────────────────────────
def o1():
    """4 thin rectangles instead of lines."""
    layers = []
    for i in range(2):
        layers.append(make_layer("rectangle", x=300, y=270+i*130, w=300, h=4, fill=NAVY))
    for i in range(2):
        layers.append(make_layer("rectangle", x=300+i*120, y=200, w=4, h=300, fill=NAVY))
    return H(layers, evts=evt(line=0, extras=[make_event("create_rectangle")]*4))
add("O1: 4 thin rectangles instead of lines", o1())

def o2():
    """4 vectors (paths) instead of lines."""
    layers = []
    for i in range(4):
        v = make_layer("vector", x=300+i*30, y=200+i*60, w=300, h=4, fill=NAVY)
        layers.append(v)
    return H(layers, evts=evt(line=0, extras=[make_event("create_vector")]*4))
add("O2: 4 vectors instead of lines", o2())

def o3():
    """3 lines + 1 arrow."""
    layers = perfect_hashtag()[:3]
    arrow = make_layer("arrow", x=420, y=200, w=300, h=4, fill=NAVY)
    arrow["rotation"] = 90
    arrow["p1"] = {"x":0,"y":0}; arrow["p2"] = {"x":300,"y":0}
    layers.append(arrow)
    return H(layers, evts=evt(line=3, extras=[make_event("create_arrow")]))
add("O3: 3 lines + 1 arrow", o3())


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

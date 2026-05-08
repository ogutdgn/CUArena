"""Round 3 edge cases — task_06 (8 lines from center at 45° intervals, gold)."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, GOLD, RED, ORANGE, YELLOW, GREEN, NAVY,
    BLACK, WHITE,
)
from tasks import task_06_gold_star_exclude as t
T = t.task


def evt(line_n=8, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(line_n):
        sem.append(make_event("create_line"))
    sem.extend(extras)
    return sem


def line(rot, color=GOLD, length=200, cx=500, cy=500, weight=2):
    return make_layer("line", x=cx, y=cy, w=length, h=2,
                      fill=None, strokes=[make_stroke(rgb=color, weight=weight)],
                      rotation=rot)


def perfect_burst(n=8, step=45, length=200, color=GOLD, cx=500, cy=500, weight=2):
    return [line(i*step, color=color, length=length, cx=cx, cy=cy, weight=weight) for i in range(n)]


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=False):
    if layers is None: layers = perfect_burst()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Step 47.9° (just inside 8° tol)."""
    return H([line(i*47.9) for i in range(8)])
add("K1: step 47.9° (within tol)", k1())

def k2():
    """All gold but 1 line stroke alpha=0.4 (just under 0.5 tol)."""
    layers = perfect_burst()
    layers[0]["strokes"][0]["paint"]["color"]["a"] = 0.4
    return H(layers)
add("K2: 1 stroke alpha=0.4 (under tol)", k2())

def k3():
    """Lines off-center by 9px (within 10 tol)."""
    layers = []
    for i in range(8):
        layers.append(line(i*45, cx=500+(i%2)*9, cy=500))
    return H(layers)
add("K3: lines ±9px off-center (within tol)", k3())

def k4():
    """Lines at angles 0, 45, 90, ..., 315 — but each line scaleX=-1 (mirrored)."""
    layers = perfect_burst()
    for l in layers: l["scaleX"] = -1
    return H(layers)
add("K4: all scaleX=-1 (still 45° step)", k4())

def k5():
    """8 lines but only 4 distinct angles (each duplicated)."""
    return H([line(i*45) for i in [0,0,90,90,180,180,270,270]])
add("K5: 4 angles duplicated (still 8 lines)", k5())

def k6():
    """All gold but slightly varied within tol."""
    layers = perfect_burst()
    for i, l in enumerate(layers):
        l["strokes"][0]["paint"]["color"] = {"r":0.85+i*0.005, "g":0.65, "b":0.13, "a":1.0}
    return H(layers)
add("K6: slightly-varying gold within tol", k6())

def k7():
    """Lines at very small radii (length=5)."""
    return H(perfect_burst(length=5))
add("K7: very short lines (length=5)", k7())

def k8():
    """Lines at length=10000 (massive)."""
    return H(perfect_burst(length=10000))
add("K8: very long lines (10000)", k8())

def k9():
    """Lines all rotation=0 but weight=20."""
    layers = perfect_burst(weight=20)
    return H(layers)
add("K9: stroke weight=20 (very thick)", k9())

def k10():
    """Lines with stroke weight 0.5 (just at min)."""
    layers = perfect_burst(weight=0.5)
    return H(layers)
add("K10: stroke weight=0.5 (at min)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """All stroke alpha=0."""
    layers = perfect_burst()
    for l in layers: l["strokes"][0]["paint"]["color"]["a"] = 0.0
    return H(layers)
add("L1: stroke alpha=0", l1())

def l2():
    """All stroke visible=False."""
    layers = perfect_burst()
    for l in layers: l["strokes"][0]["visible"] = False
    return H(layers)
add("L2: stroke visible=False", l2())

def l3():
    """All stroke weight=0."""
    layers = perfect_burst(weight=0)
    return H(layers)
add("L3: stroke weight=0", l3())

def l4():
    """All layer opacity=0."""
    layers = perfect_burst()
    for l in layers: l["opacity"] = 0.0
    return H(layers)
add("L4: layer opacity=0", l4())

def l5():
    """All layer visible=False."""
    layers = perfect_burst()
    for l in layers: l["visible"] = False
    return H(layers)
add("L5: layer visible=False", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Lines length=0."""
    return H(perfect_burst(length=0))
add("M1: length=0 (zero-length)", m1())

def m2():
    """Lines all at same angle (fan, no burst)."""
    return H([line(0) for _ in range(8)])
add("M2: all rot=0", m2())

def m3():
    """Lines at angles 0, 45, 90, 135 only (4 distinct, but 8 layers)."""
    angles = [0, 45, 90, 135]
    return H([line(angles[i % 4]) for i in range(8)])
add("M3: 4 distinct angles, 2 each", m3())

def m4():
    """Lines spread across page (cx, cy varies)."""
    layers = []
    for i in range(8):
        a = math.radians(i*45)
        layers.append(line(i*45, cx=500+200*math.cos(a), cy=500+200*math.sin(a)))
    return H(layers)
add("M4: lines on circle (not concentric)", m4())

def m5():
    """Frame rotated 45°, burst inside."""
    layers = perfect_burst()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("M5: frame rotated 45°", m5())

def m6():
    """Burst with negative w (flipped lines)."""
    layers = perfect_burst()
    for l in layers: l["w"] = -200
    return H(layers)
add("M6: lines w=-200", m6())

def m7():
    """Lines all stacked at center, no rotations."""
    return H([line(0, cx=500, cy=500) for _ in range(8)])
add("M7: 8 lines at center, all rot=0", m7())

def m8():
    """1 line missing, 1 doubled (8 total)."""
    layers = [line(i*45) for i in range(8) if i != 3] + [line(0)]
    return H(layers)
add("M8: 7 distinct angles + 1 doubled", m8())


# ─── N. Hierarchy ────────────────────────────────────────────────────
def n1():
    """Burst in group inside frame."""
    layers = perfect_burst()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([g], w=900, h=900)
    return make_log([frame], evt())
add("N1: burst in group in frame", n1())

def n2():
    """Burst split across 2 frames (4 each)."""
    layers = perfect_burst()
    f1 = make_frame(layers[:4], w=900, h=900)
    f2 = make_frame(layers[4:], w=900, h=900)
    return make_log([f1, f2], evt())
add("N2: burst split across 2 frames", n2())

def n3():
    """Each line in own frame."""
    layers = perfect_burst()
    frames = [make_frame([l], w=400, h=400) for l in layers]
    return make_log(frames, evt())
add("N3: each line in own frame", n3())


# ─── O. Wrong shape types substituted ────────────────────────────────
def o1():
    """8 thin rectangles (not lines)."""
    layers = []
    for i in range(8):
        l = make_layer("rectangle", x=500, y=499, w=200, h=2, fill=GOLD, rotation=i*45)
        layers.append(l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_rectangle")] * 8)
    return H(layers, evts=sem)
add("O1: 8 rectangles (not lines)", o1())

def o2():
    """8 vectors."""
    layers = []
    for i in range(8):
        l = make_layer("vector", x=500, y=500, w=200, h=2, fill=None,
                        strokes=[make_stroke(rgb=GOLD, weight=2)], rotation=i*45)
        layers.append(l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_vector")] * 8)
    return H(layers, evts=sem)
add("O2: 8 vectors (not lines)", o2())

def o3():
    """8 ellipses (long thin)."""
    layers = []
    for i in range(8):
        l = make_layer("ellipse", x=500, y=499, w=200, h=4, fill=GOLD, rotation=i*45)
        layers.append(l)
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 8)
    return H(layers, evts=sem)
add("O3: 8 thin ellipses (not lines)", o3())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95:
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95): {fp_count}")

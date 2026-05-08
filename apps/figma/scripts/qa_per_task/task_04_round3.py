"""Round 3 edge cases — task_04 (6 same-size squares in hex ring rainbow)."""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke,
    score_task, RED, ORANGE, YELLOW, GREEN, CYAN, NAVY, MAGENTA,
    BLACK, WHITE,
)
from tasks import task_04_color_wheel as t
T = t.task

RAINBOW = [RED, ORANGE, YELLOW, GREEN, CYAN, MAGENTA]


def evt(rect=6, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_ring(side=80, radius=200, n=6):
    cx, cy = 500, 500
    return [L("rectangle", cx + radius*math.cos(2*math.pi*i/n) - side/2,
              cy + radius*math.sin(2*math.pi*i/n) - side/2, side, side, RAINBOW[i % 6])
            for i in range(n)]


def H(layers=None, frame_w=900, frame_h=900, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_ring()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """All squares 80x82 (within 3 tol)."""
    return H([L("rectangle", l["x"], l["y"], 80, 82, l["fills"][0]["color"]) for l in perfect_ring()])
add("K1: 80x82 (within 3 tol)", k1())

def k2():
    """All squares rotated 1.9° (under 2 tol)."""
    layers = perfect_ring()
    for l in layers: l["rotation"] = 1.9
    return H(layers)
add("K2: all rotated 1.9°", k2())

def k3():
    """5 squares at hex angles + 1 at 65° (close to 60°)."""
    cx, cy = 500, 500
    layers = []
    angles_deg = [0, 60, 120, 180, 240, 305]  # last 305° vs ideal 300°
    for i, ang in enumerate(angles_deg):
        a = math.radians(ang)
        layers.append(L("rectangle", cx+200*math.cos(a)-40, cy+200*math.sin(a)-40, 80, 80, RAINBOW[i]))
    return H(layers)
add("K3: 5 hex + 1 5° off", k3())

def k4():
    """Squares cornerRadius=23 (just under 0.30 frac)."""
    layers = perfect_ring()
    for l in layers: l["cornerRadius"] = 23  # 23/80 = 0.288
    return H(layers)
add("K4: cornerRadius=23 (just under 0.30)", k4())

def k5():
    """6 distinct rainbow but 1 fill is gradient (passes color order if first stop is solid-ish)."""
    layers = perfect_ring()
    layers[0]["fills"] = [{"kind": "solid", "color":{"r":1,"g":0,"b":0,"a":0.5}, "opacity":0.5, "visible":True}]
    return H(layers)
add("K5: 1st square fill alpha=0.5 (within tol)", k5())

def k6():
    """Squares at hex angles but radius varies slightly."""
    cx, cy = 500, 500
    radii = [200, 200, 200, 220, 200, 200]  # 1 outlier (within radius_tolerance_frac=0.25)
    layers = []
    for i, r in enumerate(radii):
        a = 2*math.pi*i/6
        layers.append(L("rectangle", cx+r*math.cos(a)-40, cy+r*math.sin(a)-40, 80, 80, RAINBOW[i]))
    return H(layers)
add("K6: 5 at r=200 + 1 at r=220", k6())

def k7():
    """6 squares but at duplicated angle pattern (3 angles, 2 each)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2 * math.pi * (i // 2) / 3 + (0.1 if i % 2 else 0)  # 3 angles, 2 each
        layers.append(L("rectangle", cx+200*math.cos(a)-40, cy+200*math.sin(a)-40, 80, 80, RAINBOW[i]))
    return H(layers)
add("K7: 3 angles, 2 squares each (clumped)", k7())

def k8():
    """6 distinct colors but 5 are similar pinks + 1 outlier."""
    layers = perfect_ring()
    pinks = [{"r":1,"g":0.5+i*0.05,"b":0.7,"a":1} for i in range(5)]
    pinks.append({"r":0.0,"g":0.0,"b":0.0,"a":1})
    for l, c in zip(layers, pinks): l["fills"][0]["color"] = c
    return H(layers)
add("K8: 5 pinks + 1 black (technically distinct)", k8())

def k9():
    """Squares stacked at exact center (radial fail)."""
    return H([L("rectangle", 460, 460, 80, 80, RAINBOW[i]) for i in range(6)])
add("K9: 6 squares stacked at center (zero radius)", k9())

def k10():
    """Squares 78x82 (within tol but not perfect square)."""
    layers = perfect_ring(side=80)
    for l in layers: l["w"] = 78; l["h"] = 82
    return H(layers)
add("K10: 78x82 (close-square, within tol)", k10())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    layers = perfect_ring()
    for l in layers: l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: alpha=0", l1())

def l2():
    layers = perfect_ring()
    for l in layers: l["fills"][0]["visible"] = False
    return H(layers)
add("L2: fill.visible=False", l2())

def l3():
    layers = perfect_ring()
    for l in layers: l["opacity"] = 0.0
    return H(layers)
add("L3: layer.opacity=0", l3())

def l4():
    layers = perfect_ring()
    for l in layers: l["visible"] = False
    return H(layers)
add("L4: layer.visible=False", l4())

def l5():
    layers = perfect_ring()
    for i, l in enumerate(layers):
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("L5: all image fills (no solid colors)", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Squares overlap in the ring."""
    return H(perfect_ring(side=200, radius=80))
add("M1: squares overlapping", m1())

def m2():
    """All squares = full frame."""
    return H([L("rectangle", 0, 0, 900, 900, RAINBOW[i]) for i in range(6)])
add("M2: all = full frame", m2())

def m3():
    """6 squares but 1 is huge (200x200)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2*math.pi*i/6
        size = 200 if i == 0 else 80
        layers.append(L("rectangle", cx+200*math.cos(a)-size/2, cy+200*math.sin(a)-size/2, size, size, RAINBOW[i]))
    return H(layers)
add("M3: 1 huge + 5 normal", m3())

def m4():
    """Frame rotated 90°, squares inside."""
    layers = perfect_ring()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 90
    return make_log([frame], evt())
add("M4: frame rotated 90°", m4())

def m5():
    """Squares at radius=15 (almost concentric)."""
    return H(perfect_ring(side=80, radius=15))
add("M5: radius=15 (near-concentric)", m5())

def m6():
    """Squares each scaleY=-1 individually."""
    layers = perfect_ring()
    for l in layers: l["scaleY"] = -1
    return H(layers)
add("M6: all scaleY=-1", m6())

def m7():
    """Squares with negative w (flipped)."""
    layers = perfect_ring()
    for l in layers: l["w"] = -80
    return H(layers)
add("M7: negative w", m7())

def m8():
    """Each square rotated by its own angle."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2*math.pi*i/6
        l = L("rectangle", cx+200*math.cos(a)-40, cy+200*math.sin(a)-40, 80, 80, RAINBOW[i])
        l["rotation"] = math.degrees(a)
        layers.append(l)
    return H(layers)
add("M8: each square rotated by its angle", m8())


# ─── N. Hierarchy ────────────────────────────────────────────────────
def n1():
    """Squares in group inside frame."""
    layers = perfect_ring()
    g = {"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":layers}
    frame = make_frame([g], w=900, h=900)
    return make_log([frame], evt())
add("N1: in group in frame", n1())

def n2():
    """3 squares in frame_a, 3 in frame_b."""
    layers = perfect_ring()
    f1 = make_frame(layers[:3], w=900, h=900)
    f2 = make_frame(layers[3:], w=900, h=900)
    return make_log([f1, f2], evt())
add("N2: split across 2 frames", n2())

def n3():
    """Each square in own group inside frame."""
    layers = perfect_ring()
    groups = []
    for l in layers:
        g = {"id":f"g_{l['id']}","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":[l]}
        groups.append(g)
    frame = make_frame(groups, w=900, h=900)
    return make_log([frame], evt())
add("N3: each in own group", n3())


# ─── O. Wrong shape types ────────────────────────────────────────────
def o1():
    """All ellipses (with same dimensions, in ring)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2*math.pi*i/6
        layers.append(make_layer("ellipse", x=cx+200*math.cos(a)-40, y=cy+200*math.sin(a)-40,
                                  w=80, h=80, fill=RAINBOW[i]))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_ellipse")] * 6)
    return H(layers, evts=sem)
add("O1: 6 ellipses instead of squares", o1())

def o2():
    """All polygons (squares = 4 sides)."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2*math.pi*i/6
        layers.append(make_layer("polygon", x=cx+200*math.cos(a)-40, y=cy+200*math.sin(a)-40,
                                  w=80, h=80, fill=RAINBOW[i], sides=4))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    sem.extend([make_event("create_polygon")] * 6)
    return H(layers, evts=sem)
add("O2: 6 polygons (4-sided) instead of squares", o2())

def o3():
    """All stars."""
    cx, cy = 500, 500
    layers = []
    for i in range(6):
        a = 2*math.pi*i/6
        layers.append(make_layer("star", x=cx+200*math.cos(a)-40, y=cy+200*math.sin(a)-40,
                                  w=80, h=80, fill=RAINBOW[i], points=4))
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="star")]
    sem.extend([make_event("create_star")] * 6)
    return H(layers, evts=sem)
add("O3: 6 stars instead of squares", o3())


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

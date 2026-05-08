"""Round 3 — novel deception cases for task 20 (glow blob)."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_layer_blur, make_drop_shadow,
    score_task, NAVY, MAGENTA, CYAN, BLACK, WHITE, RED, GREEN, COBALT,
)
from tasks import task_20_glow_blob as t
T = t.task


def evt(ellipse=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("tool_change", before="frame", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_glow():
    e1 = make_layer("ellipse", x=250, y=250, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=310, y=270, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return [e1, e2]


def H(layers=None, frame_color=NAVY, frame_w=900, frame_h=900, evts=None):
    if layers is None: layers = perfect_glow()
    frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_color)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ──────────────────────────────────────────
def k1():
    """Frame nearly navy (but slightly off)."""
    return H(frame_color=(0.20, 0.20, 0.50))   # purple-ish navy
add("K1: frame purple-navy (drift)", k1())

def k2():
    """Blur radius 49 (just under tol of 80-30=50)."""
    layers = perfect_glow()
    for l in layers: l["effects"][0]["radius"] = 49
    return H(layers)
add("K2: blur 49 (just under tol)", k2())

def k3():
    """Ellipses 0px overlap (just touching)."""
    e1 = make_layer("ellipse", x=200, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=400, y=300, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("K3: ellipses touching (0px overlap)", k3())

def k4():
    """Frame slightly off-navy color (channel +0.31 deviation)."""
    return H(frame_color=(0.36, 0.10, 0.45))   # too red
add("K4: frame red-shifted (over tol)", k4())

def k5():
    """Ellipses nearly circular (w-h diff = 5px, tol = 3)."""
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=205, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=200, h=205, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("K5: ellipses 200×205 (ovals, over tol)", k5())

def k6():
    """1 ellipse circular, 1 oval."""
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=360, y=320, w=300, h=100, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("K6: 1 circle + 1 oval", k6())


# ─── L. Visibility tricks ──────────────────────────────────────────
def l1():
    """Both ellipses fill alpha=0."""
    layers = perfect_glow()
    for l in layers: l["fills"][0]["color"]["a"] = 0
    return H(layers)
add("L1: both alpha=0", l1())

def l2():
    """One ellipse opacity=0, the other normal."""
    layers = perfect_glow()
    layers[0]["opacity"] = 0
    return H(layers)
add("L2: e1 opacity=0", l2())

def l3():
    """Frame fill alpha=0 (frame invisible)."""
    return H(frame_color={"r":0.05, "g":0.10, "b":0.45, "a":0.0})
add("L3: frame fill alpha=0", l3())

def l4():
    """Both layer_blur effects invisible."""
    layers = perfect_glow()
    for l in layers:
        l["effects"][0]["visible"] = False
    return H(layers)
add("L4: both blurs visible=False", l4())

def l5():
    """Both blur radius=0 (no actual blur)."""
    layers = perfect_glow()
    for l in layers: l["effects"][0]["radius"] = 0
    return H(layers)
add("L5: both blur radius=0", l5())


# ─── M. Geometry tricks ────────────────────────────────────────────
def m1():
    """Both ellipses 1×1 at center."""
    e1 = make_layer("ellipse", x=400, y=400, w=1, h=1, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=400, y=400, w=1, h=1, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M1: 1×1 ellipses (degenerate)", m1())

def m2():
    """Both = full frame size 900×900."""
    e1 = make_layer("ellipse", x=0, y=0, w=900, h=900, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=0, y=0, w=900, h=900, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M2: ellipses = full frame", m2())

def m3():
    """Ellipses positioned so one entirely inside the other."""
    e1 = make_layer("ellipse", x=100, y=100, w=400, h=400, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=200, y=200, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M3: e2 entirely inside e1", m3())

def m4():
    """Ellipses way off frame."""
    e1 = make_layer("ellipse", x=2000, y=2000, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=2050, y=2050, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M4: ellipses at (2000,2000)", m4())

def m5():
    """Ellipses are massive and one is rotated 45°."""
    e1 = make_layer("ellipse", x=100, y=100, w=600, h=600, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)], rotation=45)
    e2 = make_layer("ellipse", x=200, y=200, w=600, h=600, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M5: e1 rotated 45° (huge)", m5())

def m6():
    """Both ellipses scaled to exactly frame size (centered)."""
    e1 = make_layer("ellipse", x=100, y=100, w=700, h=700, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("ellipse", x=100, y=100, w=700, h=700, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2])
add("M6: e1 and e2 at exact same bbox", m6())


# ─── N. Structural tricks ──────────────────────────────────────────
def n1():
    """Ellipses outside any frame."""
    layers = perfect_glow()
    return make_log(layers, evt())
add("N1: ellipses on page (no frame)", n1())

def n2():
    """Ellipses in 2 separate frames."""
    layers = perfect_glow()
    f1 = make_frame([layers[0]], w=400, h=400, fill=NAVY)
    f2 = make_frame([layers[1]], w=400, h=400, fill=NAVY, x=400)
    return make_log([f1, f2], evt())
add("N2: ellipses in 2 separate frames", n2())

def n3():
    """Ellipses in section with navy fill (not frame)."""
    layers = perfect_glow()
    section = {"id":"sec1","type":"section","x":0,"y":0,"w":900,"h":900,
               "fills":[{"kind":"solid","color":{"r":0.05,"g":0.10,"b":0.45,"a":1},"opacity":1,"visible":True}],
               "children":layers}
    return make_log([section], evt())
add("N3: ellipses in navy section (not frame)", n3())

def n4():
    """Component containing the design."""
    layers = perfect_glow()
    component = {"id":"c1","type":"component","x":0,"y":0,"w":900,"h":900,
                 "fills":[{"kind":"solid","color":{"r":0.05,"g":0.10,"b":0.45,"a":1},"opacity":1,"visible":True}],
                 "strokes":[],"effects":[], "children":layers}
    return make_log([component], evt())
add("N4: glow inside component", n4())


# ─── O. Wrong shape types ─────────────────────────────────────────
def o1():
    """Replace ellipses with rectangles."""
    e1 = make_layer("rectangle", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("rectangle", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2], evts=evt(ellipse=0,
                                extras=[make_event("create_rectangle")]*2))
add("O1: rectangles instead of ellipses", o1())

def o2():
    """Replace ellipses with polygons (hexagons)."""
    e1 = make_layer("polygon", x=300, y=300, w=200, h=200, fill=MAGENTA, sides=6,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("polygon", x=360, y=320, w=200, h=200, fill=CYAN, sides=6,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2], evts=evt(ellipse=0,
                                extras=[make_event("create_polygon")]*2))
add("O2: hexagons instead of ellipses", o2())

def o3():
    """Mix: 1 ellipse + 1 rectangle (overlap)."""
    e1 = make_layer("ellipse", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("rectangle", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2], evts=evt(ellipse=1,
                                extras=[make_event("create_rectangle"),
                                        make_event("tool_change", before="ellipse", after="rectangle")]))
add("O3: 1 ellipse + 1 rect (mixed)", o3())

def o4():
    """Replace ellipses with vectors (custom blob shapes)."""
    e1 = make_layer("vector", x=300, y=300, w=200, h=200, fill=MAGENTA,
                    effects=[make_layer_blur(radius=80)])
    e2 = make_layer("vector", x=360, y=320, w=200, h=200, fill=CYAN,
                    effects=[make_layer_blur(radius=80)])
    return H([e1, e2], evts=evt(ellipse=0,
                                extras=[make_event("create_vector")]*2))
add("O4: vectors instead of ellipses", o4())


# ─── Run ────────────────────────────────────────────────────────────
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        if flag: fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nstrict FPs (≥0.95): {fp_count}/{len(CASES)}")

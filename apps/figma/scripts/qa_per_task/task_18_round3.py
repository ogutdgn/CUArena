"""Round 3 — novel deception cases for task 18 (eye icon)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_18" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
CX, CY = 500, 500
WHITE_FILL = (1.0, 1.0, 1.0)
IRIS_FILL  = (0.2, 0.5, 0.85)
PUPIL_FILL = (0.0, 0.0, 0.0)


def evt(ellipse=3, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_eye(sizes=(160, 100, 40)):
    fills = [WHITE_FILL, IRIS_FILL, PUPIL_FILL]
    return [L("ellipse", CX-sz/2, CY-sz/2, sz, sz, c) for sz, c in zip(sizes, fills)]


def H(layers=None, evts=None):
    if layers is None: layers = perfect_eye()
    frame = make_frame(layers, w=1280, h=832)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ──────────────────────────────────────────
def k1():
    """Iris 1.5px off-center (just under tolerance)."""
    layers = perfect_eye()
    layers[1]["x"] = CX - 50 + 1.5
    return H(layers)
add("K1: iris 1.5px off-center (under tol)", k1())

def k2():
    """All 3 ellipses w=h=80 with same color (no nesting visible)."""
    layers = []
    for sz in [80, 80, 80]:
        layers.append(L("ellipse", CX-sz/2, CY-sz/2, sz, sz, IRIS_FILL))
    return H(layers)
add("K2: all 3 same-size single color (visual blob)", k2())

def k3():
    """Sclera/iris/pupil in size order (160/100/40), but colors uniformly white."""
    layers = perfect_eye()
    for l in layers:
        l["fills"][0]["color"] = {"r":1,"g":1,"b":1,"a":1}
    return H(layers)
add("K3: all white (no contrast at all)", k3())

def k4():
    """Iris is 1.4× pupil (smaller than 1.5× area ratio)."""
    # area ratio: 100²/85² = 1.38, just under 1.5
    layers = perfect_eye(sizes=(160, 100, 85))
    return H(layers)
add("K4: iris/pupil area ratio 1.38 (under 1.5)", k4())

def k5():
    """All 3 ellipses concentric, but ellipses are 1px ovals."""
    layers = [L("ellipse", CX-1, CY-0.5, 2, 1, WHITE_FILL),
              L("ellipse", CX-0.5, CY-0.25, 1, 0.5, IRIS_FILL),
              L("ellipse", CX-0.25, CY-0.125, 0.5, 0.25, PUPIL_FILL)]
    return H(layers)
add("K5: all 3 sub-pixel degenerate", k5())

def k6():
    """3 ellipses nested but circle aspect not exact (w/h drift just under tol)."""
    layers = [L("ellipse", CX-80, CY-78, 160, 156, WHITE_FILL),
              L("ellipse", CX-50, CY-49, 100, 98, IRIS_FILL),
              L("ellipse", CX-20, CY-19, 40, 38, PUPIL_FILL)]
    return H(layers)
add("K6: ellipses not perfectly circular (under tol)", k6())


# ─── L. Visibility tricks ──────────────────────────────────────────
def l1():
    """Iris fill alpha=0."""
    layers = perfect_eye()
    layers[1]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("L1: iris alpha=0", l1())

def l2():
    """Pupil fill visible=False."""
    layers = perfect_eye()
    layers[2]["fills"][0]["visible"] = False
    return H(layers)
add("L2: pupil fill visible=False", l2())

def l3():
    """Sclera layer opacity=0.05."""
    layers = perfect_eye()
    layers[0]["opacity"] = 0.05
    return H(layers)
add("L3: sclera layer opacity=0.05", l3())

def l4():
    """All 3 fills opacity=0.1."""
    layers = perfect_eye()
    for l in layers: l["fills"][0]["opacity"] = 0.1
    return H(layers)
add("L4: all fills opacity=0.1", l4())

def l5():
    """Sclera color = frame color (camouflaged)."""
    layers = perfect_eye()
    layers[0]["fills"][0]["color"] = {"r":0.95,"g":0.95,"b":0.95,"a":1.0}
    return H(layers)
add("L5: sclera matches frame color", l5())


# ─── M. Geometry tricks ────────────────────────────────────────────
def m1():
    """Iris and pupil flipped (iris at center, pupil mid-size)."""
    layers = [L("ellipse", CX-80, CY-80, 160, 160, WHITE_FILL),
              L("ellipse", CX-20, CY-20, 40, 40, IRIS_FILL),  # smallest = iris color
              L("ellipse", CX-50, CY-50, 100, 100, PUPIL_FILL)]
    return H(layers)
add("M1: pupil at iris size, iris at pupil size (color-swap)", m1())

def m2():
    """3 ellipses concentric in 1280×832 frame but each is 800×800 (overflow)."""
    layers = [L("ellipse", CX-400, CY-400, 800, 800, WHITE_FILL),
              L("ellipse", CX-300, CY-300, 600, 600, IRIS_FILL),
              L("ellipse", CX-200, CY-200, 400, 400, PUPIL_FILL)]
    return H(layers)
add("M2: ellipses overflow frame", m2())

def m3():
    """3 ellipses on diagonal (each one offset by 50px from previous)."""
    layers = [L("ellipse", 200, 200, 160, 160, WHITE_FILL),
              L("ellipse", 250, 250, 100, 100, IRIS_FILL),
              L("ellipse", 300, 300, 40, 40, PUPIL_FILL)]
    return H(layers)
add("M3: ellipses on diagonal (not concentric)", m3())

def m4():
    """3 ellipses at exactly sclera dimension (overlapping perfectly)."""
    layers = [L("ellipse", CX-80, CY-80, 160, 160, WHITE_FILL),
              L("ellipse", CX-80, CY-80, 160, 160, IRIS_FILL),
              L("ellipse", CX-80, CY-80, 160, 160, PUPIL_FILL)]
    return H(layers)
add("M4: 3 ellipses identical, 'on top' = pupil only visible", m4())

def m5():
    """Sclera tiny (10px), pupil huge (200px)."""
    layers = [L("ellipse", CX-5, CY-5, 10, 10, WHITE_FILL),
              L("ellipse", CX-50, CY-50, 100, 100, IRIS_FILL),
              L("ellipse", CX-100, CY-100, 200, 200, PUPIL_FILL)]
    return H(layers)
add("M5: sclera 10px, pupil 200px (inverted)", m5())

def m6():
    """All 3 share center but pupil is HUGE, iris medium, sclera tiny."""
    layers = [L("ellipse", CX-20, CY-20, 40, 40, WHITE_FILL),
              L("ellipse", CX-50, CY-50, 100, 100, IRIS_FILL),
              L("ellipse", CX-80, CY-80, 160, 160, PUPIL_FILL)]
    return H(layers)
add("M6: sizes inverted (sclera smallest)", m6())


# ─── N. Structural tricks ──────────────────────────────────────────
def n1():
    """3 ellipses in 3 separate components (no frame)."""
    layers = perfect_eye()
    components = []
    for l in layers:
        c = {"id":f"comp_{l['id']}","type":"component","x":0,"y":0,"w":1280,"h":832,
             "fills":[],"strokes":[],"effects":[], "children":[l]}
        components.append(c)
    return make_log(components, evt())
add("N1: 3 ellipses in 3 components", n1())

def n2():
    """3 nested groups → all in 1 frame."""
    layers = perfect_eye()
    g3 = [layers[2]]
    g2 = [{"id":"g2","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":g3 + [layers[1]]}]
    g1 = [{"id":"g1","type":"group","x":0,"y":0,"w":0,"h":0,"fills":[],"strokes":[],"effects":[],"children":g2 + [layers[0]]}]
    frame = make_frame(g1, w=1280, h=832)
    return make_log([frame], evt())
add("N2: ellipses nested in groups inside frame", n2())

def n3():
    """Ellipses on page (not frame)."""
    return make_log(perfect_eye(), evt())
add("N3: ellipses directly on page", n3())

def n4():
    """3 ellipses in section-section-frame."""
    layers = perfect_eye()
    inner = make_frame(layers, w=600, h=600)
    sec1 = {"id":"s1","type":"section","x":0,"y":0,"w":700,"h":700,"fills":[],"children":[inner]}
    sec2 = {"id":"s2","type":"section","x":0,"y":0,"w":800,"h":800,"fills":[],"children":[sec1]}
    return make_log([sec2], evt())
add("N4: ellipses inside section/section/frame", n4())


# ─── O. Wrong shape types ─────────────────────────────────────────
def o1():
    """Ellipses replaced with squares."""
    layers = []
    for sz, c in zip([160, 100, 40], [WHITE_FILL, IRIS_FILL, PUPIL_FILL]):
        layers.append(L("rectangle", CX-sz/2, CY-sz/2, sz, sz, c))
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_rectangle")]*3))
add("O1: rectangles instead of ellipses", o1())

def o2():
    """Ellipses replaced with hexagons."""
    layers = []
    for sz, c in zip([160, 100, 40], [WHITE_FILL, IRIS_FILL, PUPIL_FILL]):
        layers.append(L("polygon", CX-sz/2, CY-sz/2, sz, sz, c, sides=6))
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_polygon")]*3))
add("O2: hexagons instead of ellipses", o2())

def o3():
    """Mixed: 1 ellipse + 1 rectangle + 1 polygon."""
    e = L("ellipse", CX-80, CY-80, 160, 160, WHITE_FILL)
    r = L("rectangle", CX-50, CY-50, 100, 100, IRIS_FILL)
    p = L("polygon", CX-20, CY-20, 40, 40, PUPIL_FILL, sides=6)
    return H([e, r, p], evts=evt(ellipse=1, extras=[make_event("create_rectangle"),
                                                    make_event("create_polygon")]))
add("O3: 1 ellipse + 1 rect + 1 polygon", o3())

def o4():
    """3 ellipses, but they're vector ellipses."""
    layers = []
    for sz in [160, 100, 40]:
        layers.append(make_layer("vector", x=CX-sz/2, y=CY-sz/2, w=sz, h=sz, fill=WHITE_FILL))
    return H(layers, evts=evt(ellipse=0, extras=[make_event("create_vector")]*3))
add("O4: 3 vectors instead of ellipses", o4())


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

"""Round 3 edge cases — hunt for surviving false positives in task_34 (snowflake)."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_34" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)


def evt(line=4, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="line")]
    for _ in range(line): sem.append(make_event("create_line"))
    sem.extend(extras)
    return sem


def L(tt, x, y, w, h, fill, **extra):
    return make_layer(tt, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_snowflake(n_lines=4, line_color=WHITE, frame_color=NAVY, line_w=2):
    cx, cy = 400, 400
    layers = []
    for i in range(n_lines):
        rotation = i * (360 / n_lines)
        layers.append(L("line", cx, cy, 200, 4, fill=None,
                        strokes=[make_stroke(rgb=line_color, weight=line_w)],
                        rotation=rotation))
    return layers, frame_color


def H(layers=None, evts=None, frame_w=800, frame_h=800, frame_fill=NAVY):
    if layers is None:
        layers, frame_fill = perfect_snowflake()
    frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
    return make_log([frame], evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ── K. Subtle deceptions ─────────────────────────────────────────────
def k1():
    """Lines all rotation=0 but at different positions = visually 4 parallel."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx + i * 50, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=0))
    return H(layers, frame_fill=NAVY)
add("K1: 4 parallel lines (no rotation)", k1())


def k2():
    """Lines stepped 8° apart (just under tol 10)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 8))  # 0,8,16,24 - bunched
    return H(layers, frame_fill=NAVY)
add("K2: stepped 8° (under tol)", k2())


def k3():
    """Lines stepped 88° (just under 90°)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 88))  # 0,88,176,264
    return H(layers, frame_fill=NAVY)
add("K3: stepped 88° (just under tol)", k3())


def k4():
    """Lines diagonally placed (rotation 45,135,225,315)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=45 + i * 90))
    return H(layers, frame_fill=NAVY)
add("K4: lines diagonal (X pattern, valid)", k4())


def k5():
    """Lines at 0,180,90,270 but NOT concentric — different positions."""
    layers = []
    pos = [(200, 200), (200, 200), (600, 600), (600, 600)]
    rots = [0, 90, 180, 270]
    for (x, y), r in zip(pos, rots):
        layers.append(L("line", x, y, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=r))
    return H(layers, frame_fill=NAVY)
add("K5: lines stepped 90° but not concentric", k5())


def k6():
    """Lines varying lengths (50, 100, 150, 200)."""
    cx, cy = 400, 400
    layers = []
    lens = [50, 100, 150, 200]
    for i, ln in enumerate(lens):
        layers.append(L("line", cx, cy, ln, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("K6: lines varying lengths", k6())


def k7():
    """Frame is white rectangle (not navy frame)."""
    layers, _ = perfect_snowflake()
    rect = L("rectangle", 0, 0, 800, 800, NAVY)
    layers_with_rect = [rect, *layers]
    return make_log(layers_with_rect, evt())
add("K7: navy rectangle instead of frame", k7())


def k8():
    """Lines all rotation=0 (all horizontal)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=0))
    return H(layers, frame_fill=NAVY)
add("K8: all 4 lines parallel (rotation 0)", k8())


def k9():
    """Lines step 90° but absolute rotations 4° off pure 0,90,180,270."""
    cx, cy = 400, 400
    layers = []
    rotations = [4, 94, 184, 274]  # within tol 10°
    for i, r in enumerate(rotations):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=r))
    return H(layers, frame_fill=NAVY)
add("K9: rotations all +4° (within tol)", k9())


def k10():
    """Lines varying stroke weights (1, 5, 10, 20)."""
    cx, cy = 400, 400
    weights = [1, 5, 10, 20]
    layers = []
    for i, w in enumerate(weights):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=w)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("K10: lines varying weights (no consistent thickness)", k10())


# ── L. Visibility tricks ─────────────────────────────────────────────
def l1():
    """Lines stroke alpha=0."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        s = make_stroke(rgb=WHITE, weight=2)
        s["paint"]["color"]["a"] = 0.0
        layers.append(L("line", cx, cy, 200, 4, None, strokes=[s], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("L1: lines stroke alpha=0", l1())


def l2():
    """Lines stroke visible=False."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        s = make_stroke(rgb=WHITE, weight=2)
        s["visible"] = False
        layers.append(L("line", cx, cy, 200, 4, None, strokes=[s], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("L2: lines stroke visible=False", l2())


def l3():
    """Lines layer.opacity=0."""
    layers, _ = perfect_snowflake()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers, frame_fill=NAVY)
add("L3: lines layer opacity=0", l3())


def l4():
    """Frame fill alpha=0."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["fills"][0]["color"]["a"] = 0.0
    return make_log([frame], evt())
add("L4: frame alpha=0", l4())


def l5():
    """Lines stroke weight 0.1 (essentially invisible)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=0.1)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("L5: lines stroke weight 0.1 (invisible)", l5())


# ── M. Geometry tricks ───────────────────────────────────────────────
def m1():
    """Lines 1×1 degenerate."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 1, 1, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("M1: lines 1×1", m1())


def m2():
    """Lines all 0×0."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 0, 0, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("M2: lines 0×0", m2())


def m3():
    """Lines pile on top of each other (overlap)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=0))
    return H(layers, frame_fill=NAVY)
add("M3: lines all rotation=0 (parallel pile)", m3())


def m4():
    """Lines outside frame bounds."""
    cx, cy = 1500, 1500
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("M4: lines outside frame", m4())


def m5():
    """Frame is 0×0."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=0, h=0, fill=NAVY)
    return make_log([frame], evt())
add("M5: frame 0×0", m5())


def m6():
    """Lines are not centered on frame center."""
    layers = []
    for i in range(4):
        layers.append(L("line", 100, 100, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("M6: lines all in top-left corner", m6())


def m7():
    """Lines are huge, frame is small (lines way outside)."""
    cx, cy = 100, 100
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 5000, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_w=200, frame_h=200, frame_fill=NAVY)
add("M7: huge lines, tiny frame", m7())


# ── N. Structural tricks ─────────────────────────────────────────────
def n1():
    """No frame at all."""
    layers, _ = perfect_snowflake()
    return make_log(layers, evt())
add("N1: snowflake without frame", n1())


def n2():
    """Each line in own frame."""
    layers, _ = perfect_snowflake()
    frames = [make_frame([s], w=800, h=800, fill=NAVY) for s in layers]
    return make_log(frames, evt())
add("N2: each line in own frame", n2())


def n3():
    """Snowflake inside component."""
    layers, _ = perfect_snowflake()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("N3: snowflake inside component (no frame)", n3())


def n4():
    """Lines split: 2 in frame, 2 on page."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers[:2], w=800, h=800, fill=NAVY)
    return make_log([frame, *layers[2:]], evt())
add("N4: 2 lines in frame, 2 on page", n4())


# ── O. Wrong types ───────────────────────────────────────────────────
def o1():
    """Vectors instead of lines."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("vector", x=cx, y=cy, w=200, h=4, fill=None,
                                  strokes=[make_stroke(rgb=WHITE, weight=2)],
                                  rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("O1: vectors instead of lines", o1())


def o2():
    """Rectangles instead of lines."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("rectangle", cx, cy, 200, 4, WHITE, rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("O2: rectangles instead of lines", o2())


def o3():
    """4 stars instead of lines."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("star", x=cx, y=cy, w=200, h=4, fill=WHITE,
                                  points=5, innerRatio=0.4, rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("O3: stars instead of lines", o3())


# ── Run ─────────────────────────────────────────────────────────────
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

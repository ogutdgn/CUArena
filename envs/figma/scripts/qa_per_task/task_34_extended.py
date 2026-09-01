"""100 edge cases for task 34 (snowflake) — runs all and prints a sorted score table."""
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
    """Navy frame + 4 white line branches rotated 90° each."""
    cx, cy = 400, 400
    layers = []
    for i in range(n_lines):
        rotation = i * (360 / n_lines)
        layers.append(L("line", cx, cy, 200, 4, fill=None,
                        strokes=[make_stroke(rgb=line_color, weight=line_w)],
                        rotation=rotation))
    return layers, frame_color


CASES = []


def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=800, frame_h=800, frame_fill=NAVY,
      in_frame=True):
    if layers is None:
        layers, frame_fill = perfect_snowflake()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ── A. Counts ───────────────────────────────────────────────────────
def case_a1():
    layers, c = perfect_snowflake(n_lines=5)
    return H(layers, frame_fill=c, evts=evt(line=5))
add("A1: 5 lines (extra)", case_a1())


def case_a2():
    layers, c = perfect_snowflake(n_lines=3)
    return H(layers, frame_fill=c, evts=evt(line=3))
add("A2: 3 lines (missing one)", case_a2())


def case_a3():
    layers, c = perfect_snowflake(n_lines=2)
    return H(layers, frame_fill=c, evts=evt(line=2))
add("A3: 2 lines", case_a3())


def case_a4():
    layers, c = perfect_snowflake(n_lines=8)
    return H(layers, frame_fill=c, evts=evt(line=8))
add("A4: 8 lines (doubled)", case_a4())


def case_a5():
    return H([], frame_fill=NAVY, evts=evt(line=0))
add("A5: 0 lines (empty frame)", case_a5())


def case_a6():
    layers, c = perfect_snowflake(n_lines=4)
    layers.append(L("line", 100, 100, 100, 4, None, strokes=[make_stroke(rgb=WHITE, weight=2)]))
    return H(layers, frame_fill=c, evts=evt(line=5))
add("A6: 4 radial + 1 stray", case_a6())


def case_a7():
    layers, c = perfect_snowflake(n_lines=1)
    return H(layers, frame_fill=c, evts=evt(line=1))
add("A7: 1 line only", case_a7())


def case_a8():
    layers, c = perfect_snowflake()
    layers.append(L("rectangle", 100, 100, 50, 50, RED))
    return H(layers, frame_fill=c)
add("A8: 4 lines + 1 rectangle", case_a8())


def case_a9():
    """4 lines but 4 of them are all unrelated extras."""
    cx, cy = 100, 100
    layers = [L("line", cx + i * 50, cy, 30, 4, None, strokes=[make_stroke(rgb=WHITE, weight=2)]) for i in range(4)]
    return H(layers, frame_fill=NAVY)
add("A9: 4 lines but in row (not radial)", case_a9())


def case_a10():
    layers, c = perfect_snowflake()
    layers.extend([L("ellipse", 50+i*100, 700, 30, 30, GOLD) for i in range(4)])
    return H(layers, frame_fill=c)
add("A10: snowflake + 4 ellipse decoration", case_a10())


# ── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    """Frame is white not navy."""
    layers, _ = perfect_snowflake()
    return H(layers, frame_fill=WHITE)
add("B11: frame WHITE (not navy)", case_b11())


def case_b12():
    """Lines are red not white."""
    layers, c = perfect_snowflake(line_color=RED)
    return H(layers, frame_fill=c)
add("B12: lines RED (not white)", case_b12())


def case_b13():
    """Frame has image fill."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=None)
    frame["fills"] = [{"kind": "image", "src": "snow.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return make_log([frame], evt())
add("B13: frame image fill", case_b13())


def case_b14():
    """Frame stroke only."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=None)
    frame["strokes"] = [make_stroke(rgb=NAVY, weight=4)]
    return make_log([frame], evt())
add("B14: frame stroke only", case_b14())


def case_b15():
    """Lines stroke=None (no stroke)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, fill=None,
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("B15: lines have no stroke", case_b15())


def case_b16():
    """All lines black on navy (low contrast)."""
    layers, c = perfect_snowflake(line_color=BLACK)
    return H(layers, frame_fill=c)
add("B16: lines BLACK on navy", case_b16())


def case_b17():
    """Lines near-white but slightly off."""
    NEAR_WHITE = (0.95, 0.95, 0.95)
    layers, c = perfect_snowflake(line_color=NEAR_WHITE)
    return H(layers, frame_fill=c)
add("B17: near-white lines (within tol)", case_b17())


def case_b18():
    """Frame near-navy but slightly off."""
    NEAR_NAVY = (0.10, 0.15, 0.50)
    layers, _ = perfect_snowflake()
    return H(layers, frame_fill=NEAR_NAVY)
add("B18: near-navy frame (within tol)", case_b18())


def case_b19():
    """Frame fill opacity 0.1."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["fills"][0]["opacity"] = 0.1
    return make_log([frame], evt())
add("B19: frame opacity 0.1", case_b19())


def case_b20():
    """Frame has stacked fills."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["fills"].extend([
        {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
        {"kind": "solid", "color": {"r": 1, "g": 1, "b": 1, "a": 1}, "opacity": 0.3, "visible": True}])
    return make_log([frame], evt())
add("B20: frame stacked fills", case_b20())


# ── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """Lines very long."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 1000, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("C21: lines 1000px long", case_c21())


def case_c22():
    """Lines very short."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 5, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("C22: lines 5px long", case_c22())


def case_c23():
    """Frame 100×100 (tiny)."""
    layers, c = perfect_snowflake()
    return H(layers, frame_w=100, frame_h=100, frame_fill=c)
add("C23: frame 100×100", case_c23())


def case_c24():
    """Frame 5000×5000 (huge)."""
    layers, c = perfect_snowflake()
    return H(layers, frame_w=5000, frame_h=5000, frame_fill=c)
add("C24: frame 5000×5000", case_c24())


def case_c25():
    """Lines varying lengths."""
    cx, cy = 400, 400
    layers = []
    lens = [50, 100, 200, 400]
    for i, ln in enumerate(lens):
        layers.append(L("line", cx, cy, ln, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("C25: lines varying lengths", case_c25())


def case_c26():
    """Lines very thick (100px stroke)."""
    layers, c = perfect_snowflake(line_w=100)
    return H(layers, frame_fill=c)
add("C26: lines 100px stroke weight", case_c26())


def case_c27():
    """Lines 1×1 degenerate."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 1, 1, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("C27: lines 1×1 degenerate", case_c27())


def case_c28():
    """Frame 1×1 degenerate."""
    layers, c = perfect_snowflake()
    return H(layers, frame_w=1, frame_h=1, frame_fill=c)
add("C28: frame 1×1 degenerate", case_c28())


def case_c29():
    """Lines stroke 0px (no visual)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=0)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("C29: lines stroke=0 (invisible)", case_c29())


def case_c30():
    """Frame too narrow to fit lines."""
    layers, c = perfect_snowflake()
    return H(layers, frame_w=10, frame_h=800, frame_fill=c)
add("C30: frame 10×800 (lines overflow)", case_c30())


# ── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Lines all at corner of frame."""
    layers = []
    for i in range(4):
        layers.append(L("line", 50, 50, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D31: lines all in corner", case_d31())


def case_d32():
    """Lines spread across frame."""
    layers = []
    pos = [(100, 100), (700, 100), (100, 700), (700, 700)]
    for i, (x, y) in enumerate(pos):
        layers.append(L("line", x, y, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D32: lines in 4 corners", case_d32())


def case_d33():
    """Lines off-frame."""
    layers = []
    for i in range(4):
        layers.append(L("line", 1000, 1000, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D33: lines off-frame", case_d33())


def case_d34():
    """Lines centered (perfect)."""
    return H()
add("D34: control (centered)", case_d34())


def case_d35():
    """Lines shifted globally."""
    layers, c = perfect_snowflake()
    for l in layers:
        l["x"] += 100
        l["y"] += 100
    return H(layers, frame_fill=c)
add("D35: lines shifted +100", case_d35())


def case_d36():
    """Lines all stacked at one point (no spread)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D36: lines all from center (control-like)", case_d36())


def case_d37():
    """Lines on edge of frame."""
    cx, cy = 0, 0  # top-left corner
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D37: lines at top-left corner", case_d37())


def case_d38():
    """Lines at negative coords."""
    layers, c = perfect_snowflake()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 1000
    return H(layers, frame_fill=c)
add("D38: lines at negative coords", case_d38())


def case_d39():
    """Lines spread in 2x2 grid."""
    pos = [(200, 200), (600, 200), (200, 600), (600, 600)]
    layers = []
    for i, (x, y) in enumerate(pos):
        layers.append(L("line", x, y, 100, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D39: lines in 2x2 grid pattern", case_d39())


def case_d40():
    """Lines at exact same point."""
    layers = []
    for i in range(4):
        layers.append(L("line", 400, 400, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("D40: 4 lines at same point", case_d40())


# ── E. Per-shape variants ───────────────────────────────────────────
def case_e41():
    """Lines all rotation=0 (no spin)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=0))
    return H(layers, frame_fill=NAVY)
add("E41: lines all rotation=0", case_e41())


def case_e42():
    """Lines stepped by 30° (not 90°)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 30))
    return H(layers, frame_fill=NAVY)
add("E42: lines stepped 30° (not 90°)", case_e42())


def case_e43():
    """Lines stepped by 45° (not 90°)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 45))
    return H(layers, frame_fill=NAVY)
add("E43: lines stepped 45° (not 90°)", case_e43())


def case_e44():
    """Lines rotation +5° (within tol 10)."""
    layers, c = perfect_snowflake()
    for l in layers:
        l["rotation"] = (l.get("rotation", 0) + 5) % 360
    return H(layers, frame_fill=c)
add("E44: lines rotation +5° (within tol)", case_e44())


def case_e45():
    """Lines rotation +15° (outside tol 10)."""
    layers, c = perfect_snowflake()
    for l in layers:
        l["rotation"] = (l.get("rotation", 0) + 15) % 360
    return H(layers, frame_fill=c)
add("E45: lines rotation +15° (outside tol)", case_e45())


def case_e46():
    """Lines mirrored (scaleX=-1)."""
    layers, c = perfect_snowflake()
    for l in layers:
        l["scaleX"] = -1
    return H(layers, frame_fill=c)
add("E46: lines mirrored", case_e46())


def case_e47():
    """Lines = vectors."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("vector", x=cx, y=cy, w=200, h=4, fill=None,
                                  strokes=[make_stroke(rgb=WHITE, weight=2)],
                                  rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("E47: vectors not lines", case_e47())


def case_e48():
    """Lines but as rectangles."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("rectangle", cx, cy, 200, 4, WHITE,
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("E48: rectangles instead of lines", case_e48())


def case_e49():
    """Lines all rotation=180 (flipped)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=180))
    return H(layers, frame_fill=NAVY)
add("E49: lines all rotation=180", case_e49())


def case_e50():
    """Lines rotation step 60° (3-fold not 4-fold)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 60))
    return H(layers, frame_fill=NAVY)
add("E50: lines stepped 60° (not 90°)", case_e50())


# ── F. Subcomponent variants ────────────────────────────────────────
def case_f51():
    """3 lines + 1 rectangle posing as line."""
    cx, cy = 400, 400
    layers = []
    for i in range(3):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    layers.append(L("rectangle", cx, cy, 200, 4, WHITE, rotation=270))
    return H(layers, frame_fill=NAVY, evts=evt(line=3))
add("F51: 3 lines + 1 rect posing as line", case_f51())


def case_f52():
    """All 4 lines exact same line (overlapping)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=0))
    return H(layers, frame_fill=NAVY)
add("F52: 4 identical overlapping lines", case_f52())


def case_f53():
    """Lines have stroke colors mixed."""
    cx, cy = 400, 400
    colors = [WHITE, RED, GREEN, BLUE]
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=colors[i], weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F53: lines have 4 different stroke colors", case_f53())


def case_f54():
    """Lines have multiple strokes (not single)."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[
                            make_stroke(rgb=WHITE, weight=2),
                            make_stroke(rgb=RED, weight=4),
                        ], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F54: lines with 2 stacked strokes", case_f54())


def case_f55():
    """Lines have dashed strokes."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        s = make_stroke(rgb=WHITE, weight=2, dash={"dash": 6, "gap": 4})
        layers.append(L("line", cx, cy, 200, 4, None, strokes=[s], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F55: lines dashed strokes", case_f55())


def case_f56():
    """Frame has stroke."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["strokes"] = [make_stroke(rgb=WHITE, weight=4)]
    return make_log([frame], evt())
add("F56: frame with white stroke", case_f56())


def case_f57():
    """Frame has effects (drop shadow)."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["effects"] = [make_drop_shadow(blur=10)]
    return make_log([frame], evt())
add("F57: frame with drop shadow", case_f57())


def case_f58():
    """Lines with effects."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        effects=[make_drop_shadow(blur=4)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F58: lines with drop shadow", case_f58())


def case_f59():
    """Lines have transparent strokes."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        s = make_stroke(rgb=WHITE, weight=2)
        s["paint"]["color"]["a"] = 0.0
        layers.append(L("line", cx, cy, 200, 4, None, strokes=[s], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F59: lines stroke alpha=0", case_f59())


def case_f60():
    """Lines have visible=False."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        s = make_stroke(rgb=WHITE, weight=2)
        s["visible"] = False
        layers.append(L("line", cx, cy, 200, 4, None, strokes=[s], rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("F60: lines stroke visible=False", case_f60())


# ── G. Frame variants ───────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers, _ = perfect_snowflake()
    inner = make_frame(layers, w=600, h=600, fill=NAVY)
    outer = make_frame([inner], w=800, h=800, fill=NAVY)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """No frame."""
    layers, _ = perfect_snowflake()
    return make_log(layers, evt())
add("G63: snowflake without frame", case_g63())


def case_g64():
    """Multiple frames."""
    layers, _ = perfect_snowflake()
    f1 = make_frame([], w=800, h=800, fill=NAVY)
    f2 = make_frame(layers, w=800, h=800, fill=NAVY)
    return make_log([f1, f2], evt())
add("G64: 2 frames, snowflake in 2nd", case_g64())


def case_g65():
    """Frame with white fill."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=WHITE)
    return make_log([frame], evt())
add("G65: frame WHITE fill", case_g65())


def case_g66():
    """Frame translated."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, x=300, y=200, w=800, h=800, fill=NAVY)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())


def case_g67():
    """Frame split: 2 lines in each."""
    layers, _ = perfect_snowflake()
    f1 = make_frame(layers[:2], w=800, h=800, fill=NAVY)
    f2 = make_frame(layers[2:], w=800, h=800, fill=NAVY)
    return make_log([f1, f2], evt())
add("G67: lines split across 2 frames", case_g67())


def case_g68():
    """Frame is rectangle layer (not actual frame type)."""
    layers, _ = perfect_snowflake()
    rect = L("rectangle", 0, 0, 800, 800, NAVY)
    return make_log([rect, *layers], evt())
add("G68: navy rectangle instead of frame", case_g68())


def case_g69():
    """Frame inside group."""
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": [frame]}
    return make_log([group], evt())
add("G69: frame inside group", case_g69())


def case_g70():
    """Frame is huge, lines tiny in corner."""
    layers, _ = perfect_snowflake()
    return H(layers, frame_w=5000, frame_h=5000, frame_fill=NAVY)
add("G70: frame 5000×5000 (lines tiny)", case_g70())


# ── H. Tools / events ───────────────────────────────────────────────
def case_h71():
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())


def case_h72():
    return H(evts=evt(extras=[make_event("undo") for _ in range(40)]))
add("H72: 40 undo events", case_h72())


def case_h73():
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    sem.extend([make_event("create_line")] * 4)
    return H(evts=sem)
add("H73: tool_change to rectangle", case_h73())


def case_h74():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_line")] * 4)
    return H(evts=sem)
add("H74: 0 tool_change events", case_h74())


def case_h75():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted a star", case_h75())


def case_h76():
    return H(evts=evt(line=8))
add("H76: 8 create_line events", case_h76())


def case_h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", case_h77())


def case_h78():
    return H(evts=evt(line=0))
add("H78: 0 create_line events", case_h78())


def case_h79():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: used align tool", case_h79())


def case_h80():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: used distribute tool", case_h80())


# ── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers, _ = perfect_snowflake()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=800, h=800, fill=NAVY)
    return make_log([frame], evt())
add("I81: lines inside group inside frame", case_i81())


def case_i82():
    layers, _ = perfect_snowflake()
    f1 = make_frame(layers[:2], w=800, h=800, fill=NAVY)
    f2 = make_frame(layers[2:], w=800, h=800, fill=NAVY)
    return make_log([f1, f2], evt())
add("I82: lines split across 2 frames", case_i82())


def case_i83():
    layers, _ = perfect_snowflake()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 800, "h": 800,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: lines inside section", case_i83())


def case_i84():
    layers, _ = perfect_snowflake()
    frame = make_frame(layers[:2], w=800, h=800, fill=NAVY)
    return make_log([frame, *layers[2:]], evt())
add("I84: 2 lines in frame, 2 on page", case_i84())


def case_i85():
    layers, _ = perfect_snowflake()
    f3 = make_frame(layers, w=800, h=800, fill=NAVY)
    f2 = make_frame([f3], w=800, h=800, fill=NAVY)
    f1 = make_frame([f2], w=800, h=800, fill=NAVY)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    layers, _ = perfect_snowflake()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 800, "h": 800, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: lines inside component", case_i86())


def case_i87():
    layers, _ = perfect_snowflake()
    frame = make_frame(layers, w=800, h=800, fill=NAVY)
    page1 = {"id": "p1", "children": [],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    page2 = {"id": "p2", "children": [frame],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I87: snowflake on page 2", case_i87())


def case_i88():
    """Each line in own frame."""
    layers, _ = perfect_snowflake()
    frames = [make_frame([s], w=800, h=800, fill=NAVY) for s in layers]
    return make_log(frames, evt())
add("I88: each line in own frame", case_i88())


def case_i89():
    """Section instead of frame."""
    layers, _ = perfect_snowflake()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 800, "h": 800,
               "fills": [{"kind": "solid",
                          "color": {"r": NAVY[0], "g": NAVY[1], "b": NAVY[2], "a": 1.0},
                          "opacity": 1.0, "visible": True}],
               "children": layers}
    return make_log([section], evt())
add("I89: section instead of frame", case_i89())


def case_i90():
    """Lines deep in groups inside frame."""
    layers, _ = perfect_snowflake()
    g = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
         "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g]}
    frame = make_frame([g2], w=800, h=800, fill=NAVY)
    return make_log([frame], evt())
add("I90: lines deep in groups", case_i90())


# ── J. Bizarre ──────────────────────────────────────────────────────
def case_j91():
    layers, _ = perfect_snowflake()
    for l in layers:
        l["scaleX"] = -1
    return H(layers, frame_fill=NAVY)
add("J91: lines mirrored", case_j91())


def case_j92():
    """All shapes 0×0."""
    layers, _ = perfect_snowflake()
    for l in layers:
        l["w"] = 0
        l["h"] = 0
    return H(layers, frame_fill=NAVY)
add("J92: all 0×0", case_j92())


def case_j93():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J93: empty doc", case_j93())


def case_j94():
    """Frame only, no lines."""
    return H([], frame_fill=NAVY, evts=evt(line=0))
add("J94: empty frame", case_j94())


def case_j95():
    """Text 'snowflake'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=WHITE)
    text["content"] = "snowflake"
    frame = make_frame([text], w=800, h=800, fill=NAVY)
    return make_log([frame], [make_event("session_start"), make_event("create_text")])
add("J95: text 'snowflake'", case_j95())


def case_j96():
    """Lines stepped 90° but rotated globally 35°."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90 + 35))
    return H(layers, frame_fill=NAVY)
add("J96: lines stepped 90° + offset 35°", case_j96())


def case_j97():
    """Star points instead of lines."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(make_layer("star", x=cx, y=cy, w=200, h=4, fill=WHITE,
                                  points=5, innerRatio=0.4, rotation=i * 90))
    return H(layers, frame_fill=NAVY, evts=evt(line=0))
add("J97: stars instead of lines", case_j97())


def case_j98():
    """Lines at exactly 90° but with negative width."""
    cx, cy = 400, 400
    layers = []
    for i in range(4):
        layers.append(L("line", cx, cy, -200, -4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=i * 90))
    return H(layers, frame_fill=NAVY)
add("J98: lines negative dimensions", case_j98())


def case_j99():
    """Lines at random rotations (0, 13, 47, 89)."""
    cx, cy = 400, 400
    rotations = [0, 13, 47, 89]
    layers = []
    for i, r in enumerate(rotations):
        layers.append(L("line", cx, cy, 200, 4, None,
                        strokes=[make_stroke(rgb=WHITE, weight=2)],
                        rotation=r))
    return H(layers, frame_fill=NAVY)
add("J99: lines random rotations", case_j99())


def case_j100():
    """Perfect control."""
    return H()
add("J100: perfect snowflake (control)", case_j100())


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

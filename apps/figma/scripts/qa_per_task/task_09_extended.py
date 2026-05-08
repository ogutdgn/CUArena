"""100 edge cases for task 09 — runs all and prints a sorted score table.

Task 09 = 12 same-size squares in a 4x3 grid, each filled a different color.
"""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_09" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
# 12 distinct colors for the perfect grid
COLORS_12 = [
    (0.95, 0.20, 0.20),  # red
    (1.00, 0.60, 0.20),  # orange
    (1.00, 0.85, 0.20),  # yellow
    (0.40, 0.85, 0.30),  # green
    (0.10, 0.50, 0.90),  # blue
    (0.50, 0.20, 0.70),  # purple
    (0.85, 0.30, 0.65),  # pink
    (0.65, 0.40, 0.20),  # brown
    (0.20, 0.20, 0.20),  # near-black
    (0.85, 0.85, 0.85),  # near-white
    (0.30, 0.70, 0.70),  # teal
    (0.95, 0.50, 0.30),  # coral
]


def evt(rect=12, tool_changes=1, extras=()):
    sem = [make_event("session_start")]
    for _ in range(tool_changes):
        sem.append(make_event("tool_change", before="select", after="rectangle"))
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def R(x, y, w, h, fill, **extra):
    return make_layer("rectangle", x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design(square_size=80, gap=40, x0=100, y0=100):
    """4×3 grid of 12 same-size colored squares."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(x0 + col * (square_size + gap), y0 + row * (square_size + gap),
                        square_size, square_size, COLORS_12[i]))
    return layers


CASES = []
def add(label, log): CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ─── A. Counts ──────────────────────────────────────────────────────
def case_a1():
    return H(perfect_design()[:11], evts=evt(rect=11))
add("A1: 11 squares (1 missing)", case_a1())

def case_a2():
    return H(perfect_design()[:6], evts=evt(rect=6))
add("A2: 6 squares (half)", case_a2())

def case_a3():
    layers = perfect_design()
    layers.append(R(800, 600, 80, 80, (0.5, 0.0, 0.5)))
    return H(layers, evts=evt(rect=13))
add("A3: 13 squares (extra)", case_a3())

def case_a4():
    """24 squares (4x6 grid)."""
    layers = []
    for i in range(24):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 50 + row * 80, 60, 60,
                        COLORS_12[i % 12]))
    return H(layers, evts=evt(rect=24))
add("A4: 24 squares (4x6)", case_a4())

def case_a5():
    """0 rectangles."""
    return H([], evts=evt(rect=0))
add("A5: 0 squares", case_a5())

def case_a6():
    """12 ellipses instead of rectangles."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(make_layer("ellipse", x=100 + col * 120, y=100 + row * 120,
                                 w=80, h=80, fill=COLORS_12[i]))
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_ellipse")]*12))
add("A6: 12 ellipses (no rects)", case_a6())

def case_a7():
    """1 huge square (degenerate)."""
    return H([R(100, 100, 800, 800, COLORS_12[0])], evts=evt(rect=1))
add("A7: 1 huge square", case_a7())

def case_a8():
    """12 squares + 5 ellipse decorations."""
    layers = perfect_design()
    for i in range(5):
        layers.append(make_layer("ellipse", x=10+i*30, y=10, w=20, h=20, fill=YELLOW))
    return H(layers, evts=evt(extras=[make_event("create_ellipse")]*5))
add("A8: 12 + 5 ellipse decorations", case_a8())

def case_a9():
    """12 squares but each extracted from groups."""
    layers = perfect_design()
    return H(layers)
add("A9: 12 squares (control)", case_a9())

def case_a10():
    """50 squares (way too many)."""
    layers = []
    for i in range(50):
        row = i // 10
        col = i % 10
        layers.append(R(50 + col * 90, 50 + row * 90, 60, 60,
                        (i*0.02 % 1.0, 0.5, 0.5)))
    return H(layers, evts=evt(rect=50))
add("A10: 50 squares (way too many)", case_a10())


# ─── B. Colors / fills ──────────────────────────────────────────────
def case_b11():
    """All 12 same red."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80, RED))
    return H(layers)
add("B11: all 12 same red", case_b11())

def case_b12():
    """Only 6 distinct colors (each used twice)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80,
                        COLORS_12[i // 2]))
    return H(layers)
add("B12: 6 distinct colors (each×2)", case_b12())

def case_b13():
    """Only 11 distinct (2 are same)."""
    colors = list(COLORS_12)
    colors[11] = colors[0]  # 12th = 1st
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80, colors[i]))
    return H(layers)
add("B13: 11 distinct (1 dup)", case_b13())

def case_b14():
    """All 12 image fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B14: all image fills", case_b14())

def case_b15():
    """6 solid + 6 image fills."""
    layers = perfect_design()
    for l in layers[6:]:
        l["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B15: 6 solid + 6 image fills", case_b15())

def case_b16():
    """All gradient fills."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 0.5, "g": 0.5, "b": 0.5, "a": 1}},
            {"position": 1, "color": {"r": 0.8, "g": 0.8, "b": 0.8, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("B16: all gradient fills", case_b16())

def case_b17():
    """All 12 stroke-only (no fill)."""
    layers = perfect_design()
    for l in layers:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("B17: stroke-only, no fill", case_b17())

def case_b18():
    """Stacked fills (each has 2 fills)."""
    layers = perfect_design()
    for l in layers:
        l["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover",
                           "opacity": 0.5, "visible": True})
    return H(layers)
add("B18: stacked 2 fills each", case_b18())

def case_b19():
    """Fill alpha=0 on all."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B19: fill alpha=0 on all", case_b19())

def case_b20():
    """Fill opacity=0.05 on all."""
    layers = perfect_design()
    for l in layers:
        l["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B20: fill opacity=0.05", case_b20())


# ─── C. Sizing ──────────────────────────────────────────────────────
def case_c21():
    """All squares 200×200 (huge)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(50 + col * 250, 50 + row * 250, 200, 200, COLORS_12[i]))
    return H(layers, frame_w=1280, frame_h=832)
add("C21: 200×200 squares", case_c21())

def case_c22():
    """All squares 5×5 (tiny)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 30, 100 + row * 30, 5, 5, COLORS_12[i]))
    return H(layers)
add("C22: 5×5 tiny squares", case_c22())

def case_c23():
    """Sizes vary — 3 different sizes."""
    layers = []
    sizes = [60, 80, 100]
    for i in range(12):
        row = i // 4
        col = i % 4
        s = sizes[i % 3]
        layers.append(R(100 + col * 130, 100 + row * 130, s, s, COLORS_12[i]))
    return H(layers)
add("C23: varying sizes (60/80/100)", case_c23())

def case_c24():
    """Rectangular (not square) shapes — 80×40."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 100 + row * 80, 80, 40, COLORS_12[i]))
    return H(layers)
add("C24: 80×40 rectangles (not square)", case_c24())

def case_c25():
    """Rectangular 40×80 (tall, not square)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 80, 100 + row * 120, 40, 80, COLORS_12[i]))
    return H(layers)
add("C25: 40×80 (tall rects)", case_c25())

def case_c26():
    """1 outlier size — 11 normal, 1 huge."""
    layers = perfect_design()
    layers[5]["w"] = 200
    layers[5]["h"] = 200
    return H(layers)
add("C26: 1 outlier huge size", case_c26())

def case_c27():
    """Shape too big (each = full frame)."""
    layers = []
    for i in range(12):
        layers.append(R(0, 0, 1280, 832, COLORS_12[i]))
    return H(layers)
add("C27: each=full frame", case_c27())

def case_c28():
    """Squares 1×1 degenerate."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 50, 100 + row * 50, 1, 1, COLORS_12[i]))
    return H(layers)
add("C28: 1×1 degenerate", case_c28())

def case_c29():
    """Sizes within tolerance (78-82)."""
    layers = []
    sizes = [78, 80, 81, 79, 82, 80, 80, 80, 80, 80, 80, 81]
    for i in range(12):
        row = i // 4
        col = i % 4
        s = sizes[i]
        layers.append(R(100 + col * 120, 100 + row * 120, s, s, COLORS_12[i]))
    return H(layers)
add("C29: sizes 78-82 (within tol)", case_c29())

def case_c30():
    """Sizes 60+ but 6 of them 100."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        s = 100 if i < 6 else 60
        layers.append(R(100 + col * 120, 100 + row * 120, s, s, COLORS_12[i]))
    return H(layers)
add("C30: 6×100 + 6×60", case_c30())


# ─── D. Position ────────────────────────────────────────────────────
def case_d31():
    """Random positions (not grid)."""
    import random
    random.seed(42)
    layers = []
    for i in range(12):
        layers.append(R(random.randint(50, 1000), random.randint(50, 600), 80, 80,
                        COLORS_12[i]))
    return H(layers)
add("D31: random positions (not grid)", case_d31())

def case_d32():
    """All in single row (12x1, not 4x3)."""
    layers = [R(50 + i*100, 200, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("D32: 12x1 single row", case_d32())

def case_d33():
    """All in single column (1x12)."""
    layers = [R(200, 50 + i*60, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("D33: 1x12 single column", case_d33())

def case_d34():
    """3x4 grid (transposed)."""
    layers = []
    for i in range(12):
        row = i // 3
        col = i % 3
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80, COLORS_12[i]))
    return H(layers)
add("D34: 3x4 transposed", case_d34())

def case_d35():
    """Stacked at one point."""
    layers = [R(500, 400, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("D35: 12 piled at one point", case_d35())

def case_d36():
    """4x3 grid but offset (not aligned to grid)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        x_jitter = (i % 2) * 10
        y_jitter = (i // 4) * 5
        layers.append(R(100 + col * 120 + x_jitter, 100 + row * 120 + y_jitter,
                        80, 80, COLORS_12[i]))
    return H(layers)
add("D36: 4x3 grid with jitter", case_d36())

def case_d37():
    """All squares off-frame to right."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(1500 + col * 120, 100 + row * 120, 80, 80, COLORS_12[i]))
    return H(layers)
add("D37: grid off-frame right", case_d37())

def case_d38():
    """Squares spread across whole canvas (huge gaps)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 300, 50 + row * 200, 80, 80, COLORS_12[i]))
    return H(layers, frame_w=1500, frame_h=900)
add("D38: huge gaps in grid", case_d38())

def case_d39():
    """Compact grid (touching)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 80, 100 + row * 80, 80, 80, COLORS_12[i]))
    return H(layers)
add("D39: compact grid (touching)", case_d39())

def case_d40():
    """3-4-5 staggered triangle layout."""
    layers = []
    positions = [(100, 100), (200, 100), (300, 100),
                 (100, 220), (200, 220), (300, 220), (400, 220),
                 (100, 340), (200, 340), (300, 340), (400, 340), (500, 340)]
    for i, (x, y) in enumerate(positions):
        layers.append(R(x, y, 80, 80, COLORS_12[i]))
    return H(layers)
add("D40: triangular layout (3-4-5)", case_d40())


# ─── E. Per-shape variants ──────────────────────────────────────────
def case_e41():
    """All squares rotated 45°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 45
    return H(layers)
add("E41: all rotated 45°", case_e41())

def case_e42():
    """1 rotated 30°."""
    layers = perfect_design()
    layers[5]["rotation"] = 30
    return H(layers)
add("E42: 1 rotated 30°", case_e42())

def case_e43():
    """All rotated 4° (under tol)."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 4
    return H(layers)
add("E43: all rotated 4° (under tol)", case_e43())

def case_e44():
    """All flipped horizontally."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("E44: all scaleX=-1", case_e44())

def case_e45():
    """All have rounded corners."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 40  # 50% rounded
    return H(layers)
add("E45: cornerRadius=40 (looks circular)", case_e45())

def case_e46():
    """All have cornerRadius=20."""
    layers = perfect_design()
    for l in layers:
        l["cornerRadius"] = 20
    return H(layers)
add("E46: cornerRadius=20 (rounded squares)", case_e46())

def case_e47():
    """All have stroke."""
    layers = perfect_design()
    for l in layers:
        l["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E47: all with stroke (decorative)", case_e47())

def case_e48():
    """Squares have drop shadows."""
    layers = perfect_design()
    for l in layers:
        l["effects"] = [make_drop_shadow(x=2, y=2, blur=4)]
    return H(layers)
add("E48: all with drop shadow", case_e48())

def case_e49():
    """1 in different rotation."""
    layers = perfect_design()
    layers[5]["rotation"] = 180
    return H(layers)
add("E49: 1 rotated 180°", case_e49())

def case_e50():
    """All rotated 90°."""
    layers = perfect_design()
    for l in layers:
        l["rotation"] = 90
    return H(layers)
add("E50: all rotated 90°", case_e50())


# ─── F. Subcomponent variants ───────────────────────────────────────
def case_f51():
    """Mix of squares and rectangles."""
    layers = perfect_design()
    for i in [0, 5, 11]:
        layers[i]["w"] = 120  # not square
    return H(layers)
add("F51: 3 are non-square rects", case_f51())

def case_f52():
    """First 6 are 80×80, next 6 are 100×100."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        s = 80 if i < 6 else 100
        layers.append(R(100 + col * 130, 100 + row * 130, s, s, COLORS_12[i]))
    return H(layers)
add("F52: half 80, half 100 size", case_f52())

def case_f53():
    """Squares overlap each other."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 60, 100 + row * 60, 80, 80, COLORS_12[i]))
    return H(layers)
add("F53: overlapping squares", case_f53())

def case_f54():
    """Squares with gaps (compactly arranged)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 90, 100 + row * 90, 80, 80, COLORS_12[i]))
    return H(layers)
add("F54: small gaps (10px)", case_f54())

def case_f55():
    """Squares with HUGE gaps."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 200, 100 + row * 200, 80, 80, COLORS_12[i]))
    return H(layers, frame_w=1280, frame_h=832)
add("F55: huge gaps (120px)", case_f55())

def case_f56():
    """All squares concentric (same center)."""
    layers = [R(600 - i*5, 400 - i*5, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("F56: 12 concentric (overlapping)", case_f56())

def case_f57():
    """Squares form a diagonal line."""
    layers = [R(100 + i*60, 100 + i*40, 80, 80, COLORS_12[i]) for i in range(12)]
    return H(layers)
add("F57: diagonal line layout", case_f57())

def case_f58():
    """6 squares + 6 squares stacked on each."""
    layers = []
    for i in range(6):
        x = 100 + (i % 3) * 120
        y = 100 + (i // 3) * 120
        layers.append(R(x, y, 80, 80, COLORS_12[i]))
        layers.append(R(x + 10, y + 10, 80, 80, COLORS_12[i+6]))
    return H(layers)
add("F58: 6 stacked pairs", case_f58())

def case_f59():
    """Squares 'in 4x4 grid' but only 12 (4 missing)."""
    layers = []
    for i in range(16):
        if i in [3, 7, 11, 15]:  # skip last column
            continue
        row = i // 4
        col = i % 4
        layers.append(R(100 + col * 120, 100 + row * 120, 80, 80,
                        COLORS_12[len(layers) - 1] if layers else COLORS_12[0]))
    return H(layers)
add("F59: 4x4 grid with 4 missing", case_f59())

def case_f60():
    """Hex pattern (offset every other row)."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        x_offset = 60 if row % 2 else 0
        layers.append(R(100 + col * 120 + x_offset, 100 + row * 120,
                        80, 80, COLORS_12[i]))
    return H(layers)
add("F60: offset (hex) pattern", case_f60())


# ─── G. Frame variants ──────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Nested frames."""
    inner = make_frame(perfect_design(), w=1000, h=700)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())

def case_g63():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_design(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G63: 2 frames, design in 2nd", case_g63())

def case_g64():
    """Frame with stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1, "visible": True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    """No frame (squares on page)."""
    return H(in_frame=False)
add("G66: no frame, squares on page", case_g66())

def case_g67():
    """Frame much smaller than design."""
    return H(frame_w=400, frame_h=300)
add("G67: frame 400x300 (too small)", case_g67())

def case_g68():
    """Frame much larger than design."""
    return H(frame_w=2500, frame_h=2000)
add("G68: frame 2500x2000 (huge)", case_g68())

def case_g69():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G69: frame translated (500,300)", case_g69())

def case_g70():
    """Frame rotated 1° (under tol)."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 1
    return make_log([frame], evt())
add("G70: frame rotated 1° (under tol)", case_g70())


# ─── H. Tools / events ──────────────────────────────────────────────
def case_h71():
    """No tool change (used keyboard shortcuts)."""
    sem = [make_event("session_start")]
    for _ in range(12):
        sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H71: no tool_change to rectangle", case_h71())

def case_h72():
    """Tool=ellipse but rects exist."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(12):
        sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H72: tool=ellipse but rects", case_h72())

def case_h73():
    """0 create_rectangle events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    return H(evts=sem)
add("H73: 0 create_rectangle events", case_h73())

def case_h74():
    """6 create_rectangle events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(6):
        sem.append(make_event("create_rectangle"))
    return H(evts=sem)
add("H74: 6 create_rectangle events", case_h74())

def case_h75():
    """100 undo events."""
    return H(evts=evt(extras=[make_event("undo")]*100))
add("H75: 100 undo events", case_h75())

def case_h76():
    """Used align_layers (Tidy up)."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_y")]))
add("H76: used align_layers", case_h76())

def case_h77():
    """Created and deleted extras."""
    extras = [make_event("create_rectangle"), make_event("delete")] * 5
    return H(evts=evt(extras=extras))
add("H77: 5 create+delete extras", case_h77())

def case_h78():
    """Many session_end events."""
    return H(evts=evt(extras=[make_event("session_end")]*5))
add("H78: 5x session_end", case_h78())

def case_h79():
    """Used distribute_layers."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H79: used distribute_layers", case_h79())

def case_h80():
    """Massive 200 fill events."""
    return H(evts=evt(extras=[make_event("set_fill_color")]*200))
add("H80: 200 set_fill events", case_h80())


# ─── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    """Squares in group inside frame."""
    layers = perfect_design()
    group = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: squares in group in frame", case_i81())

def case_i82():
    """Squares split across 2 frames."""
    layers = perfect_design()
    f1 = make_frame(layers[:6], w=640, h=832)
    f2 = make_frame(layers[6:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: 6+6 across 2 frames", case_i82())

def case_i83():
    """Squares in section."""
    layers = perfect_design()
    section = {"id": "s1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: in section (no frame)", case_i83())

def case_i84():
    """Each square in own frame."""
    layers = perfect_design()
    frames = [make_frame([l], w=120, h=120) for l in layers]
    return make_log(frames, evt())
add("I84: each square in own frame", case_i84())

def case_i85():
    """Page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    p1 = {"id": "p1", "children": [],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    p2 = {"id": "p2", "children": [frame],
          "prototypeSettings": {"device": None, "backgroundColor": {"r":0,"g":0,"b":0,"a":1}},
          "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [p1, p2]}}}
add("I85: design on page 2", case_i85())

def case_i86():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I86: 3-deep nested frames", case_i86())

def case_i87():
    """Squares in component."""
    layers = perfect_design()
    component = {"id": "c1", "type": "component", "x": 0, "y": 0, "w": 1280, "h": 832,
                 "fills": [], "strokes": [], "effects": [], "children": layers}
    return make_log([component], evt())
add("I87: in component (not frame)", case_i87())

def case_i88():
    """Half in frame, half on page."""
    layers = perfect_design()
    frame = make_frame(layers[:6], w=1280, h=832)
    return make_log([frame, *layers[6:]], evt())
add("I88: 6 in frame, 6 on page", case_i88())

def case_i89():
    """Empty frame + squares as siblings."""
    layers = perfect_design()
    frame = make_frame([], w=1280, h=832)
    return make_log([frame, *layers], evt())
add("I89: empty frame + sibling squares", case_i89())

def case_i90():
    """Deep group nesting."""
    layers = perfect_design()
    g3 = {"id": "g3", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": layers}
    g2 = {"id": "g2", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g3]}
    g1 = {"id": "g1", "type": "group", "x":0,"y":0,"w":0,"h":0,
          "fills": [], "strokes": [], "effects": [], "children": [g2]}
    frame = make_frame([g1], w=1280, h=832)
    return make_log([frame], evt())
add("I90: 3-deep groups in frame", case_i90())


# ─── J. Bizarre / hard ──────────────────────────────────────────────
def case_j91():
    """All squares opacity=0."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0.0
    return H(layers)
add("J91: opacity=0 (invisible)", case_j91())

def case_j92():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J92: visible=False", case_j92())

def case_j93():
    return make_log([], [make_event("session_start")])
add("J93: empty document", case_j93())

def case_j94():
    return H([])
add("J94: frame, no squares", case_j94())

def case_j95():
    """Text 'palette' only."""
    text = make_layer("text", x=400, y=400, w=200, h=40, fill=BLACK)
    text["content"] = "palette"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J95: text 'palette' only", case_j95())

def case_j96():
    """12 stars instead of squares."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(make_layer("star", x=100 + col * 120, y=100 + row * 120,
                                 w=80, h=80, fill=COLORS_12[i],
                                 points=5, innerRatio=0.4))
    return H(layers, evts=evt(rect=0,
                              extras=[make_event("create_star")]*12))
add("J96: 12 stars (not squares)", case_j96())

def case_j97():
    """Negative coords."""
    layers = []
    for i in range(12):
        row = i // 4
        col = i % 4
        layers.append(R(-200 + col * 120, -100 + row * 120, 80, 80, COLORS_12[i]))
    return H(layers)
add("J97: negative coords", case_j97())

def case_j98():
    """All squares mirrored (scaleX=-1)."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J98: all mirrored (scaleX=-1)", case_j98())

def case_j99():
    """1 huge square covering all others."""
    layers = perfect_design()
    layers.append(R(0, 0, 1280, 832, BLACK))
    return H(layers, evts=evt(rect=13))
add("J99: extra full-frame square overlapping", case_j99())

def case_j100():
    return H()
add("J100: perfect (control)", case_j100())


# ─── Run ────────────────────────────────────────────────────────────
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

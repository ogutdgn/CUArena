"""100 edge cases for task 32 (pinwheel) — runs all and prints a sorted score table."""
from __future__ import annotations
import sys
import math
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_32" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
BLUE = (0.2, 0.4, 0.85)
C1 = (0.95, 0.4, 0.2)
C2 = (0.2, 0.4, 0.95)


def evt(polygon=4, ellipse=1, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="polygon")]
    for _ in range(polygon): sem.append(make_event("create_polygon"))
    sem.append(make_event("tool_change", before="polygon", after="ellipse"))
    for _ in range(ellipse): sem.append(make_event("create_ellipse"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_pinwheel(n=4, colors=(C1, C2), pivot_radius=20):
    """4 triangles arranged radially around a small center circle, alternating two colors."""
    cx, cy = 500, 500
    layers = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100, colors[i % len(colors)],
                        sides=3, rotation=math.degrees(angle)))
    layers.append(L("ellipse", cx - pivot_radius, cy - pivot_radius,
                    pivot_radius * 2, pivot_radius * 2, GRAY))
    return layers


CASES = []


def add(label, log): CASES.append((label, log))


def H(layers=None, evts=None, frame_w=900, frame_h=900,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_pinwheel()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# ── A. Counts ───────────────────────────────────────────────────────
def case_a1():
    layers = perfect_pinwheel(n=5)
    return H(layers, evts=evt(polygon=5))
add("A1: 5 triangles (extra polygon)", case_a1())


def case_a2():
    layers = perfect_pinwheel(n=3)
    return H(layers, evts=evt(polygon=3))
add("A2: 3 triangles (missing one)", case_a2())


def case_a3():
    layers = perfect_pinwheel()
    layers.append(L("ellipse", 600, 200, 40, 40, RED))
    return H(layers, evts=evt(ellipse=2))
add("A3: 2 ellipses (extra circle)", case_a3())


def case_a4():
    layers = [l for l in perfect_pinwheel() if l["type"] != "ellipse"]
    return H(layers, evts=evt(ellipse=0))
add("A4: 0 ellipses (no center pivot)", case_a4())


def case_a5():
    layers = perfect_pinwheel(n=8)
    return H(layers, evts=evt(polygon=8))
add("A5: 8 triangles (doubled)", case_a5())


def case_a6():
    layers = perfect_pinwheel(n=2)
    return H(layers, evts=evt(polygon=2))
add("A6: 2 triangles (halved)", case_a6())


def case_a7():
    layers = perfect_pinwheel(n=4)
    layers.append(L("polygon", 100, 100, 50, 50, GREEN, sides=3))
    return H(layers, evts=evt(polygon=5))
add("A7: 5 triangles (4 radial + 1 stray)", case_a7())


def case_a8():
    layers = []
    for i in range(4):
        layers.append(L("polygon", 100 + i * 100, 200, 80, 80, C1, sides=3))
    return H(layers, evts=evt(polygon=4, ellipse=0))
add("A8: 4 triangles, no center circle", case_a8())


def case_a9():
    layers = perfect_pinwheel()
    return H(layers + [L("ellipse", 100, 100, 30, 30, RED),
                       L("ellipse", 800, 800, 30, 30, GREEN)],
             evts=evt(ellipse=3))
add("A9: 3 ellipses (extras as decoration)", case_a9())


def case_a10():
    layers = [L("ellipse", 480, 480, 40, 40, GRAY)]
    return H(layers, evts=evt(polygon=0))
add("A10: only ellipse, no triangles", case_a10())


# ── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    layers = perfect_pinwheel(colors=(C1, C1))  # uniform
    return H(layers)
add("B11: all 4 triangles same color", case_b11())


def case_b12():
    layers = perfect_pinwheel(colors=(C1, C1, C1, C1))
    return H(layers)
add("B12: uniform color (4 distinct slots)", case_b12())


def case_b13():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"] = [{"kind": "image", "src": "blade.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return H(layers)
add("B13: triangles all image fill", case_b13())


def case_b14():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"] = []
        l["strokes"] = [make_stroke(rgb=BLUE, weight=4)]
    return H(layers)
add("B14: triangles stroke only (no fill)", case_b14())


def case_b15():
    layers = perfect_pinwheel()
    layers[0]["fills"] = []
    layers[2]["fills"] = []
    return H(layers)
add("B15: 2 triangles have empty fills", case_b15())


def case_b16():
    layers = perfect_pinwheel(colors=(WHITE, WHITE))
    return H(layers, frame_fill=WHITE)
add("B16: white triangles on white frame (no contrast)", case_b16())


def case_b17():
    near1 = (0.50, 0.50, 0.50)
    near2 = (0.51, 0.51, 0.51)
    layers = perfect_pinwheel(colors=(near1, near2))
    return H(layers)
add("B17: near-identical 'two' colors (within tol)", case_b17())


def case_b18():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"] = [{"kind": "gradient", "stops": [
            {"position": 0, "color": {"r": 1, "g": 0, "b": 0, "a": 1}},
            {"position": 1, "color": {"r": 0, "g": 0, "b": 1, "a": 1}}],
            "opacity": 1, "visible": True}]
    return H(layers)
add("B18: triangles all gradient fills", case_b18())


def case_b19():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"][0]["opacity"] = 0.1
    return H(layers)
add("B19: triangles fill opacity=0.1 (transparent)", case_b19())


def case_b20():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["fills"].extend([
            {"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True},
            {"kind": "solid", "color": {"r": 0, "g": 0, "b": 0, "a": 1}, "opacity": 0.3, "visible": True}])
    return H(layers)
add("B20: triangles have 3 stacked fills", case_b20())


# ── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    layers = perfect_pinwheel()
    for i, l in enumerate(layers[:4]):
        if i == 0:
            l["w"] = 300
            l["h"] = 300
    return H(layers)
add("C21: 1 triangle 3× larger than others", case_c21())


def case_c22():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = 5
        l["h"] = 5
    return H(layers)
add("C22: tiny 5×5 triangles", case_c22())


def case_c23():
    layers = perfect_pinwheel()
    layers[-1]["w"] = layers[-1]["h"] = 400
    layers[-1]["x"] = 300
    layers[-1]["y"] = 300
    return H(layers)
add("C23: pivot ellipse 400×400 (huge, not 'small')", case_c23())


def case_c24():
    layers = perfect_pinwheel()
    for i, l in enumerate(layers[:4]):
        l["w"] = 60 + i * 40  # 60, 100, 140, 180
    return H(layers)
add("C24: triangles all different widths", case_c24())


def case_c25():
    layers = perfect_pinwheel()
    layers[0]["w"] = 200
    layers[0]["h"] = 5
    return H(layers)
add("C25: 1 triangle extreme aspect 200×5", case_c25())


def case_c26():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = 800
        l["h"] = 800
    return H(layers)
add("C26: triangles bigger than frame", case_c26())


def case_c27():
    layers = perfect_pinwheel()
    for i, l in enumerate(layers[:4]):
        l["w"] = 99 + (i % 2) * 2  # 99, 101, 99, 101 — within tol 3
    return H(layers)
add("C27: triangles within 3px tol of each other", case_c27())


def case_c28():
    layers = perfect_pinwheel()
    layers[0]["w"] = 110  # 10px outside tol from 100
    return H(layers)
add("C28: 1 triangle 10px wider (outside tol 3)", case_c28())


def case_c29():
    layers = perfect_pinwheel()
    layers[-1]["w"] = layers[-1]["h"] = 1
    return H(layers)
add("C29: pivot ellipse 1×1 (degenerate)", case_c29())


def case_c30():
    layers = perfect_pinwheel(pivot_radius=80)
    return H(layers)
add("C30: pivot ellipse 160×160 (huge but plausible)", case_c30())


# ── D. Position ──────────────────────────────────────────────────────
def case_d31():
    layers = perfect_pinwheel()
    layers[-1]["x"] = 100
    layers[-1]["y"] = 100
    return H(layers)
add("D31: pivot off-center (top-left)", case_d31())


def case_d32():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["x"] -= 200
    return H(layers)
add("D32: triangles shifted globally left 200px", case_d32())


def case_d33():
    layers = perfect_pinwheel()
    for l in layers:
        l["x"] += 600  # off-frame to the right
    return H(layers)
add("D33: pinwheel off-frame right", case_d33())


def case_d34():
    """Triangles aligned in a row, not radial."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", 100 + i * 120, 400, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=0))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("D34: triangles in a horizontal row (not radial)", case_d34())


def case_d35():
    """Triangles stacked vertically."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", 400, 100 + i * 120, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=i * 90))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("D35: triangles stacked vertically", case_d35())


def case_d36():
    """Triangles in a 2x2 grid (not radial)."""
    layers = []
    pos = [(200, 200), (600, 200), (200, 600), (600, 600)]
    for i, (x, y) in enumerate(pos):
        layers.append(L("polygon", x, y, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=i * 90))
    layers.append(L("ellipse", 430, 430, 40, 40, GRAY))
    return H(layers)
add("D36: triangles in 2x2 grid (corner pattern)", case_d36())


def case_d37():
    """Pivot far from radial center."""
    layers = perfect_pinwheel()
    layers[-1]["x"] = 50
    layers[-1]["y"] = 50
    return H(layers)
add("D37: pivot in extreme corner", case_d37())


def case_d38():
    """Pinwheel at exact perfect position (control)."""
    return H()
add("D38: perfect pinwheel control", case_d38())


def case_d39():
    """Two triangles stacked at same angle, two off."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = (i * 0.1) * math.pi  # very close angles, not 90 apart
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=math.degrees(angle)))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("D39: triangles bunched at small angles", case_d39())


def case_d40():
    """3 triangles at 120° apart (n=3 layout) but 4 of them."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 3  # 120° step but 4 → wraps
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=math.degrees(angle)))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("D40: triangles at 120° steps (overlap)", case_d40())


# ── E. Per-shape variants ───────────────────────────────────────────
def case_e41():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["sides"] = 4  # squares
    return H(layers)
add("E41: polygons all 4-sided (squares)", case_e41())


def case_e42():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["sides"] = 6
    return H(layers)
add("E42: polygons all hexagons (6 sides)", case_e42())


def case_e43():
    layers = perfect_pinwheel()
    layers[0]["sides"] = 5  # one pentagon, others triangle
    return H(layers)
add("E43: 1 pentagon, 3 triangles (mixed)", case_e43())


def case_e44():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["rotation"] = 0  # all same rotation, not stepped
    return H(layers)
add("E44: triangles all rotation=0 (no spin)", case_e44())


def case_e45():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["rotation"] = (l.get("rotation") or 0) + 4  # 4° offset (under tol 8)
    return H(layers)
add("E45: triangles rotation +4° (within tol 8)", case_e45())


def case_e46():
    layers = perfect_pinwheel()
    layers[0]["scaleX"] = -1
    return H(layers)
add("E46: 1 triangle mirrored (scaleX=-1)", case_e46())


def case_e47():
    layers = perfect_pinwheel()
    layers[-1] = L("rectangle", 480, 480, 40, 40, GRAY)
    return H(layers, evts=evt(ellipse=0))
add("E47: pivot is rectangle, not ellipse", case_e47())


def case_e48():
    layers = perfect_pinwheel()
    layers[-1]["w"] = 100
    layers[-1]["h"] = 30  # squashed (not circular)
    layers[-1]["x"] = 450
    layers[-1]["y"] = 485
    return H(layers)
add("E48: pivot ellipse squashed (not circular)", case_e48())


def case_e49():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["sides"] = 3
        l["rotation"] = 180  # all upside down
    return H(layers)
add("E49: triangles all rotated 180° (no spin)", case_e49())


def case_e50():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["scaleX"] = -1
    return H(layers)
add("E50: all triangles mirrored", case_e50())


# ── F. Subcomponent variants ────────────────────────────────────────
def case_f51():
    """Pivot ellipse not at center of triangles."""
    layers = perfect_pinwheel()
    # move pivot to (100, 100) far from triangle centroid
    layers[-1]["x"] = 50
    layers[-1]["y"] = 50
    return H(layers)
add("F51: pivot ellipse outside triangle centroid", case_f51())


def case_f52():
    """3 triangles in radial + 1 stray."""
    layers = perfect_pinwheel(n=3)
    layers.insert(0, L("polygon", 100, 100, 80, 80, C1, sides=3))
    return H(layers, evts=evt(polygon=4))
add("F52: 3 radial + 1 stray triangle", case_f52())


def case_f53():
    """All 4 triangles same color but 4 distinct shapes."""
    layers = perfect_pinwheel(colors=(C1, C1, C1, C1))
    return H(layers)
add("F53: 4 triangles uniform color", case_f53())


def case_f54():
    """Triangles overlap in 1 spot (no spread)."""
    layers = []
    for i in range(4):
        layers.append(L("polygon", 450, 450, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=i * 90))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("F54: 4 triangles piled at one point", case_f54())


def case_f55():
    """Triangles on the wrong side of a 90° step."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 4
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        # wrong rotation per blade
        layers.append(L("polygon", rx, ry, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3,
                        rotation=math.degrees(angle) + 45))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("F55: triangles offset rotation by 45°", case_f55())


def case_f56():
    """Triangles at extreme distance (radius too big)."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 4
        rx = cx + 1000 * math.cos(angle) - 50  # off-frame
        ry = cy + 1000 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3,
                        rotation=math.degrees(angle)))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("F56: triangles at extreme radius (off-frame)", case_f56())


def case_f57():
    """Triangles all touch but not radial (X pattern)."""
    cx, cy = 500, 500
    layers = []
    pos = [(cx-50, cy-150), (cx+50, cy-50), (cx-150, cy+50), (cx-50, cy+150)]
    for i, (x, y) in enumerate(pos):
        layers.append(L("polygon", x, y, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=i * 90))
    layers.append(L("ellipse", cx-20, cy-20, 40, 40, GRAY))
    return H(layers)
add("F57: triangles in X pattern (not regular radial)", case_f57())


def case_f58():
    """3 colors instead of 2 — alternating fails."""
    layers = perfect_pinwheel()
    colors = [C1, C2, GREEN, GOLD]
    for i, l in enumerate(layers[:4]):
        l["fills"][0]["color"] = {"r": colors[i][0], "g": colors[i][1], "b": colors[i][2], "a": 1.0}
    return H(layers)
add("F58: 4 distinct colors (not 2 alternating)", case_f58())


def case_f59():
    """Two triangles same color in a row (not alternating)."""
    layers = perfect_pinwheel()
    # set explicitly: A, A, B, B
    cs = [C1, C1, C2, C2]
    for i, l in enumerate(layers[:4]):
        l["fills"][0]["color"] = {"r": cs[i][0], "g": cs[i][1], "b": cs[i][2], "a": 1.0}
    return H(layers)
add("F59: A,A,B,B colors (not alternating)", case_f59())


def case_f60():
    """Triangles aligned but rotated all 0."""
    cx, cy = 500, 500
    layers = []
    for i in range(4):
        angle = 2 * math.pi * i / 4
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(L("polygon", rx, ry, 100, 100,
                        C1 if i % 2 == 0 else C2, sides=3, rotation=0))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers)
add("F60: radially placed but no rotation step", case_f60())


# ── G. Frame variants ───────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Frame inside frame."""
    layers = perfect_pinwheel()
    inner = make_frame(layers, w=800, h=800)
    outer = make_frame([inner], w=900, h=900)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """Pinwheel split across 2 frames."""
    layers = perfect_pinwheel()
    f1 = make_frame(layers[:2], w=900, h=900)
    f2 = make_frame(layers[2:], w=900, h=900)
    return make_log([f1, f2], evt())
add("G63: pinwheel split across 2 frames", case_g63())


def case_g64():
    """Frame with stroke."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900)
    frame["strokes"] = [make_stroke(rgb=BLUE, weight=4)]
    return make_log([frame], evt())
add("G64: frame with stroke", case_g64())


def case_g65():
    """Frame with image fill."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover",
                       "opacity": 1.0, "visible": True}]
    return make_log([frame], evt())
add("G65: frame has image fill", case_g65())


def case_g66():
    """Frame too small."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=200, h=200)
    return make_log([frame], evt())
add("G66: frame 200×200 (smaller than pinwheel)", case_g66())


def case_g67():
    """Frame translated."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, x=200, y=300, w=900, h=900)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())


def case_g68():
    """No frame at all (page-level)."""
    layers = perfect_pinwheel()
    return make_log(layers, evt())
add("G68: pinwheel on page (no frame)", case_g68())


def case_g69():
    """3 frames, pinwheel in 2nd."""
    f1 = make_frame([], w=900, h=900)
    f2 = make_frame(perfect_pinwheel(), w=900, h=900)
    f3 = make_frame([], w=900, h=900)
    return make_log([f1, f2, f3], evt())
add("G69: 3 frames, pinwheel in middle", case_g69())


def case_g70():
    """Frame is not actually wrapping pinwheel (siblings)."""
    layers = perfect_pinwheel()
    frame = make_frame([], w=900, h=900)
    return make_log([frame, *layers], evt())
add("G70: pinwheel siblings to empty frame", case_g70())


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
    sem.extend([make_event("create_polygon")] * 4)
    sem.append(make_event("create_ellipse"))
    return H(evts=sem)
add("H73: tool_change to rectangle (not polygon)", case_h73())


def case_h74():
    sem = [make_event("session_start")]
    sem.extend([make_event("create_polygon")] * 4)
    sem.append(make_event("create_ellipse"))
    return H(evts=sem)
add("H74: 0 tool_change events (keyboard)", case_h74())


def case_h75():
    extras = [make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: created+deleted a star", case_h75())


def case_h76():
    return H(evts=evt(polygon=8))  # too many polygon events
add("H76: 8 create_polygon events", case_h76())


def case_h77():
    sem = evt()
    sem.append(make_event("session_end"))
    sem.append(make_event("session_end"))
    return H(evts=sem)
add("H77: many session_end events", case_h77())


def case_h78():
    return H(evts=evt(polygon=0, ellipse=0))
add("H78: no create events at all", case_h78())


def case_h79():
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: used align tool", case_h79())


def case_h80():
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H80: used distribute tool", case_h80())


# ── I. Hierarchy ────────────────────────────────────────────────────
def case_i81():
    layers = perfect_pinwheel()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=900, h=900)
    return make_log([frame], evt())
add("I81: pinwheel inside group inside frame", case_i81())


def case_i82():
    layers = perfect_pinwheel()
    f1 = make_frame(layers[:2], w=900, h=900)
    f2 = make_frame(layers[2:], w=900, h=900)
    return make_log([f1, f2], evt())
add("I82: pinwheel split across 2 frames", case_i82())


def case_i83():
    layers = perfect_pinwheel()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 900, "h": 900,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: pinwheel inside section (not frame)", case_i83())


def case_i84():
    layers = perfect_pinwheel()
    frame = make_frame(layers[:3], w=900, h=900)
    return make_log([frame, *layers[3:]], evt())
add("I84: 3 in frame, 2 on page", case_i84())


def case_i85():
    layers = perfect_pinwheel()
    f3 = make_frame(layers, w=900, h=900)
    f2 = make_frame([f3], w=900, h=900)
    f1 = make_frame([f2], w=900, h=900)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())


def case_i86():
    layers = perfect_pinwheel()
    frame = make_frame([layers[-1]], w=900, h=900)  # only ellipse in frame
    return make_log([frame, *layers[:-1]], evt())
add("I86: only pivot in frame, triangles outside", case_i86())


def case_i87():
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900)
    page1 = {"id": "p1", "children": [],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    page2 = {"id": "p2", "children": [frame],
             "prototypeSettings": {"device": None, "backgroundColor": {"r": 0, "g": 0, "b": 0, "a": 1}},
             "prototypeFlows": []}
    return {"schemaVersion": 1, "sessionId": "qa", "raw": [], "semantic": evt(),
            "outcome": {"summary": {"shapeCounts": {}}, "document": {"pages": [page1, page2]}}}
add("I87: pinwheel on page 2 (multi-page)", case_i87())


def case_i88():
    layers = perfect_pinwheel()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 900, "h": 900, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I88: pinwheel inside component (not frame)", case_i88())


def case_i89():
    """4 separate single-shape frames."""
    layers = perfect_pinwheel()
    frames = [make_frame([s], w=900, h=900) for s in layers]
    return make_log(frames, evt())
add("I89: each shape in its own frame", case_i89())


def case_i90():
    """Pinwheel inside frame inside group."""
    layers = perfect_pinwheel()
    frame = make_frame(layers, w=900, h=900)
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": [frame]}
    return make_log([group], evt())
add("I90: frame inside group (top-level)", case_i90())


# ── J. Bizarre ──────────────────────────────────────────────────────
def case_j91():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["scaleX"] = -1
    return H(layers)
add("J91: all triangles mirrored (scaleX=-1)", case_j91())


def case_j92():
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["rotation"] = 180
    return H(layers)
add("J92: all triangles rotated 180°", case_j92())


def case_j93():
    """5 identical triangles stacked at center."""
    layers = []
    for i in range(5):
        layers.append(L("polygon", 450, 450, 100, 100,
                        C1, sides=3, rotation=0))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers, evts=evt(polygon=5))
add("J93: 5 identical stacked triangles", case_j93())


def case_j94():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J94: empty document", case_j94())


def case_j95():
    return H([])  # frame, no shapes
add("J95: frame only, no shapes", case_j95())


def case_j96():
    """Text layer 'pinwheel'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=BLUE)
    text["content"] = "pinwheel"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J96: text 'pinwheel'", case_j96())


def case_j97():
    """4 stars instead of 4 triangles."""
    layers = []
    cx, cy = 500, 500
    for i in range(4):
        angle = 2 * math.pi * i / 4
        rx = cx + 150 * math.cos(angle) - 50
        ry = cy + 150 * math.sin(angle) - 50
        layers.append(make_layer("star", x=rx, y=ry, w=100, h=100,
                                  fill=C1 if i % 2 == 0 else C2,
                                  points=5, innerRatio=0.4, rotation=math.degrees(angle)))
    layers.append(L("ellipse", 480, 480, 40, 40, GRAY))
    return H(layers, evts=evt(polygon=0))
add("J97: pinwheel made of stars (no polygons)", case_j97())


def case_j98():
    """All triangles 1×1 (degenerate)."""
    layers = perfect_pinwheel()
    for l in layers[:4]:
        l["w"] = l["h"] = 1
    return H(layers)
add("J98: all triangles 1×1", case_j98())


def case_j99():
    """All shapes at negative coords."""
    layers = perfect_pinwheel()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 1000
    return H(layers)
add("J99: all shapes at negative coords", case_j99())


def case_j100():
    """Perfect pinwheel control."""
    return H()
add("J100: perfect pinwheel (control)", case_j100())


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

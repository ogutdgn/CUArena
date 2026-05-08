"""100 edge cases for task 31 (Sun rays) — runs all and prints a sorted score table.

Spec: Yellow center circle + 4 triangle rays evenly rotated 90° apart (radial sun).
"""
from __future__ import annotations
import sys, math
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, WHITE, YELLOW, GREEN, RED, PURPLE, GOLD, CYAN, BLACK,
    LIGHT_GRAY, ORANGE,
)
from tasks import task_31_sun_rays as t
T = t.task

YELLOW_SUN = (1.0, 0.9, 0.2)


def evt(ellipse=1, polygon=4, set_fill=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    for _ in range(ellipse):  sem.append(make_event("create_ellipse"))
    sem.append(make_event("tool_change", before="ellipse", after="polygon"))
    for _ in range(polygon):  sem.append(make_event("create_polygon"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_design():
    """Yellow circle in center + 4 triangle rays radially distributed."""
    cx, cy = 600, 400
    layers = []
    # Center yellow circle
    layers.append(L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN))
    # 4 triangle rays at 0°, 90°, 180°, 270°
    radius = 200
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + radius * math.cos(angle_rad)
        ry = cy + radius * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return layers


CASES = []


def add(label, log):
    CASES.append((label, log))


def H(layers=None, frame_w=1280, frame_h=832, frame_fill=(0.95, 0.95, 0.95), evts=None, in_frame=True):
    if layers is None: layers = perfect_design()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


# A. Counts
def case_a1():
    """2 circles."""
    layers = perfect_design()
    layers.insert(1, L("ellipse", 700, 500, 100, 100, YELLOW_SUN))
    return H(layers, evts=evt(ellipse=2))
add("A1: 2 circles + 4 rays", case_a1())


def case_a2():
    """0 circles."""
    layers = perfect_design()[1:]
    return H(layers, evts=evt(ellipse=0))
add("A2: 0 circles, 4 rays only", case_a2())


def case_a3():
    """5 rays."""
    layers = perfect_design()
    cx, cy = 600, 400
    angle_rad = 4 * 2*math.pi / 5
    rx = cx + 200 * math.cos(angle_rad)
    ry = cy + 200 * math.sin(angle_rad)
    extra_ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
    layers.append(extra_ray)
    return H(layers, evts=evt(polygon=5))
add("A3: 1 circle + 5 rays", case_a3())


def case_a4():
    """3 rays."""
    layers = perfect_design()[:4]
    return H(layers, evts=evt(polygon=3))
add("A4: 1 circle + 3 rays", case_a4())


def case_a5():
    """0 rays."""
    layers = [perfect_design()[0]]
    return H(layers, evts=evt(polygon=0))
add("A5: 1 circle, 0 rays", case_a5())


def case_a6():
    """8 rays."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(8):
        angle_rad = i * math.pi / 4
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 45.0
        layers.append(ray)
    return H(layers, evts=evt(polygon=8))
add("A6: 1 circle + 8 rays (doubled)", case_a6())


def case_a7():
    """4 rays + extra rectangle."""
    layers = perfect_design()
    layers.append(L("rectangle", 100, 100, 80, 80, RED))
    return H(layers, evts=evt() + [make_event("create_rectangle")])
add("A7: design + extra rectangle", case_a7())


def case_a8():
    """1 circle + 4 rays + 2 stars (extras)."""
    layers = perfect_design()
    layers.append(make_layer("star", x=100, y=100, w=80, h=80, fill=GREEN, points=5, innerRatio=0.4))
    layers.append(make_layer("star", x=1100, y=100, w=80, h=80, fill=PURPLE, points=5, innerRatio=0.4))
    return H(layers, evts=evt() + [make_event("create_star")]*2)
add("A8: design + 2 stars", case_a8())


def case_a9():
    """4 circles, 0 polygons (substituted)."""
    layers = []
    cx, cy = 600, 400
    layers.append(L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN))
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        layers.append(L("ellipse", rx-30, ry-30, 60, 60, ORANGE))
    return H(layers, evts=evt(ellipse=5, polygon=0))
add("A9: 5 ellipses (rays substituted)", case_a9())


def case_a10():
    """Perfect (control)."""
    return H()
add("A10: perfect sun (control)", case_a10())


# B. Colors / fills
def case_b11():
    """Circle has image fill."""
    layers = perfect_design()
    layers[0]["fills"] = [{"kind": "image", "src": "sun.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(layers)
add("B11: circle image fill", case_b11())


def case_b12():
    """Rays have gradient fills."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["fills"] = [{"kind": "gradient", "stops":[
            {"position":0,"color":{"r":1,"g":0.5,"b":0,"a":1}},
            {"position":1,"color":{"r":1,"g":1,"b":0,"a":1}}], "opacity":1, "visible":True}]
    return H(layers)
add("B12: rays gradient fill", case_b12())


def case_b13():
    """Circle empty fills."""
    layers = perfect_design()
    layers[0]["fills"] = []
    return H(layers)
add("B13: circle empty fills", case_b13())


def case_b14():
    """Stroke-only circle."""
    layers = perfect_design()
    layers[0]["fills"] = []
    layers[0]["strokes"] = [make_stroke(rgb=YELLOW_SUN, weight=4)]
    return H(layers)
add("B14: circle stroke-only", case_b14())


def case_b15():
    """Circle is red (not yellow)."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"] = {"r": 1, "g": 0, "b": 0, "a": 1}
    return H(layers)
add("B15: circle red instead of yellow", case_b15())


def case_b16():
    """Circle is near tolerance: very orange."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"] = {"r": 1, "g": 0.6, "b": 0.1, "a": 1}
    return H(layers)
add("B16: circle dark orange (within tol?)", case_b16())


def case_b17():
    """Circle is white."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"] = {"r": 1, "g": 1, "b": 1, "a": 1}
    return H(layers)
add("B17: circle white", case_b17())


def case_b18():
    """Circle alpha=0."""
    layers = perfect_design()
    layers[0]["fills"][0]["color"]["a"] = 0.0
    return H(layers)
add("B18: circle alpha=0", case_b18())


def case_b19():
    """Rays opacity=0.05."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["fills"][0]["opacity"] = 0.05
    return H(layers)
add("B19: rays opacity=0.05", case_b19())


def case_b20():
    """Stacked fills on circle."""
    layers = perfect_design()
    layers[0]["fills"].extend([
        {"kind": "image", "src":"x.jpg", "fit":"cover", "opacity":0.5, "visible":True},
        {"kind": "gradient", "stops":[{"position":0,"color":{"r":1,"g":0,"b":0,"a":1}}], "opacity":0.3, "visible":True}])
    return H(layers)
add("B20: circle stacked fills", case_b20())


# C. Sizing
def case_c21():
    """Tiny circle 5x5."""
    layers = perfect_design()
    layers[0]["x"] = 597; layers[0]["y"] = 397
    layers[0]["w"] = 6; layers[0]["h"] = 6
    return H(layers)
add("C21: circle 6x6 (tiny)", case_c21())


def case_c22():
    """Huge circle 800x800."""
    layers = perfect_design()
    layers[0]["x"] = 200; layers[0]["y"] = 0
    layers[0]["w"] = 800; layers[0]["h"] = 800
    return H(layers)
add("C22: circle 800x800 (huge)", case_c22())


def case_c23():
    """Tiny rays 5x5."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["w"] = ray["h"] = 5
    return H(layers)
add("C23: rays 5x5 (tiny)", case_c23())


def case_c24():
    """Huge rays 300x300."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["w"] = ray["h"] = 300
    return H(layers)
add("C24: rays 300x300 (huge)", case_c24())


def case_c25():
    """Different ray sizes (40, 60, 80, 100)."""
    layers = perfect_design()
    sizes = [40, 60, 80, 100]
    for i, ray in enumerate(layers[1:]):
        ray["w"] = ray["h"] = sizes[i]
    return H(layers)
add("C25: rays varying sizes", case_c25())


def case_c26():
    """Circle is oval (100x60)."""
    layers = perfect_design()
    layers[0]["w"] = 100; layers[0]["h"] = 60
    return H(layers)
add("C26: circle is 100x60 oval", case_c26())


def case_c27():
    """Rays are stretched 100x40."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["w"] = 100; ray["h"] = 40
    return H(layers)
add("C27: rays 100x40 (oblong)", case_c27())


def case_c28():
    """1x1 degenerate circle."""
    layers = perfect_design()
    layers[0]["w"] = layers[0]["h"] = 1
    return H(layers)
add("C28: circle 1x1 (degenerate)", case_c28())


def case_c29():
    """Same dimensions tolerance: 60, 62, 60, 62 (within 4 tol)."""
    layers = perfect_design()
    sizes = [60, 62, 60, 62]
    for i, ray in enumerate(layers[1:]):
        ray["w"] = ray["h"] = sizes[i]
    return H(layers)
add("C29: rays 60/62 (within tol)", case_c29())


def case_c30():
    """Rays at full frame dimensions."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["w"] = ray["h"] = 1000
    return H(layers)
add("C30: rays 1000x1000 (full frame)", case_c30())


# D. Position
def case_d31():
    """Circle and rays at top-left corner."""
    cx, cy = 100, 100
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 100 * math.cos(angle_rad)
        ry = cy + 100 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("D31: design at top-left", case_d31())


def case_d32():
    """Off-frame to the right."""
    layers = perfect_design()
    for l in layers:
        l["x"] += 1000
    return H(layers)
add("D32: design off-frame right", case_d32())


def case_d33():
    """Circle off-center, rays around mismatched origin."""
    layers = perfect_design()
    layers[0]["x"] = 200; layers[0]["y"] = 200
    return H(layers)
add("D33: circle off-center, rays around 600,400", case_d33())


def case_d34():
    """Rays at all 4 different distances from center."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    radii = [100, 150, 200, 250]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + radii[i] * math.cos(angle_rad)
        ry = cy + radii[i] * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("D34: rays at varying distances", case_d34())


def case_d35():
    """Rays only on top (3 at top, 1 at bottom)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [0, math.pi/8, -math.pi/8, math.pi]  # 3 near top, 1 bottom
    for i, ang in enumerate(angles):
        rx = cx + 200 * math.cos(ang)
        ry = cy + 200 * math.sin(ang)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("D35: rays clustered (not 90° apart)", case_d35())


def case_d36():
    """Rays at 12,3,6,9 o'clock but center is at frame corner."""
    cx, cy = 0, 0
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("D36: design centered at (0,0)", case_d36())


def case_d37():
    """Circle and rays piled at one point."""
    layers = []
    layers.append(L("ellipse", 600, 400, 100, 100, YELLOW_SUN))
    for i in range(4):
        ray = L("polygon", 600, 400, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("D37: design piled at one point", case_d37())


def case_d38():
    """Rays in a line (not radial)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        ray = L("polygon", cx-150 + i*100, cy-200, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("D38: rays in horizontal row above circle", case_d38())


def case_d39():
    """Center circle inside frame, rays outside frame."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    far_radius = 1500
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + far_radius * math.cos(angle_rad)
        ry = cy + far_radius * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("D39: rays at huge radius (off-frame)", case_d39())


def case_d40():
    """Negative coords."""
    layers = perfect_design()
    for l in layers:
        l["x"] -= 1000
        l["y"] -= 1000
    return H(layers)
add("D40: design at negative coords", case_d40())


# E. Per-shape variants
def case_e41():
    """Rays with sides=4 (squares not triangles)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["sides"] = 4
    return H(layers)
add("E41: rays are squares (sides=4)", case_e41())


def case_e42():
    """Rays with sides=6 (hexagons)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["sides"] = 6
    return H(layers)
add("E42: rays are hexagons (sides=6)", case_e42())


def case_e43():
    """Rays not rotated (all 0°)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["rotation"] = 0
    return H(layers)
add("E43: rays not rotated (all at 0°)", case_e43())


def case_e44():
    """Rays rotated 45° step (instead of 90°)."""
    layers = perfect_design()
    for i, ray in enumerate(layers[1:]):
        ray["rotation"] = i * 45.0
    return H(layers)
add("E44: rays at 45° steps", case_e44())


def case_e45():
    """Rays rotated by 4° each (just under tolerance)."""
    layers = perfect_design()
    for i, ray in enumerate(layers[1:]):
        ray["rotation"] = i * 90.0 + 4
    return H(layers)
add("E45: rays rotated 90°+4° (under tol)", case_e45())


def case_e46():
    """Circle rotated 90°."""
    layers = perfect_design()
    layers[0]["rotation"] = 90
    return H(layers)
add("E46: circle rotated 90°", case_e46())


def case_e47():
    """Rays mirrored scaleX=-1."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["scaleX"] = -1
    return H(layers)
add("E47: rays scaleX=-1", case_e47())


def case_e48():
    """Circle has cornerRadius."""
    layers = perfect_design()
    layers[0]["cornerRadius"] = 50
    return H(layers)
add("E48: circle cornerRadius=50 (no effect)", case_e48())


def case_e49():
    """Rays have shadows."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["effects"] = [make_drop_shadow(x=2, y=2)]
    return H(layers)
add("E49: rays have shadows", case_e49())


def case_e50():
    """Rays have strokes (decorations)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["strokes"] = [make_stroke(rgb=BLACK, weight=2)]
    return H(layers)
add("E50: rays have strokes", case_e50())


# F. Subcomponent variants
def case_f51():
    """Rays at irregular angles (10°, 100°, 200°, 290°)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [10, 100, 200, 290]
    for ang in angles:
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("F51: rays at 10/100/200/290°", case_f51())


def case_f52():
    """Rays cluster in 3 quadrants (3 close + 1 far)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [0, 30, 60, 180]
    for ang in angles:
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        layers.append(ray)
    return H(layers)
add("F52: 3 rays clustered at top, 1 at bottom", case_f52())


def case_f53():
    """All rays the same color (good case)."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["fills"][0]["color"] = {"r": 1, "g": 0.5, "b": 0, "a": 1}
    return H(layers)
add("F53: rays uniform orange (good)", case_f53())


def case_f54():
    """All rays different colors."""
    colors = [RED, GREEN, BLACK, PURPLE]
    layers = perfect_design()
    for i, ray in enumerate(layers[1:]):
        c = colors[i]
        ray["fills"][0]["color"] = {"r": c[0], "g": c[1], "b": c[2], "a": 1}
    return H(layers)
add("F54: rays 4 different colors", case_f54())


def case_f55():
    """Rays rotated incorrectly: 90, 90, 90, 90."""
    layers = perfect_design()
    for ray in layers[1:]:
        ray["rotation"] = 90
    return H(layers)
add("F55: rays all rotated 90° (no progression)", case_f55())


def case_f56():
    """Circle replaces rays (all are circles)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("ellipse", rx-30, ry-30, 60, 60, ORANGE)
        layers.append(ray)
    return H(layers, evts=evt(ellipse=5, polygon=0))
add("F56: 5 ellipses (all circles)", case_f56())


def case_f57():
    """Rays inside the circle (overlapping)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-100, cy-100, 200, 200, YELLOW_SUN)]
    for i in range(4):
        ray = L("polygon", cx-30, cy-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("F57: rays inside circle", case_f57())


def case_f58():
    """Rays touching circle edge (radius=size)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 80 * math.cos(angle_rad)  # close
        ry = cy + 80 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("F58: rays touching circle edge", case_f58())


def case_f59():
    """Rays angled 0, 89, 180, 271 (within 1° of 90 step)."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    angles = [0, 89, 180, 271]
    for i, ang in enumerate(angles):
        rad = math.radians(ang)
        rx = cx + 200 * math.cos(rad)
        ry = cy + 200 * math.sin(rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = ang
        layers.append(ray)
    return H(layers)
add("F59: rays at 0/89/180/271° (within tol)", case_f59())


def case_f60():
    """All rays at exactly the same angle as one of them — i.e., overlapping rays."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        # all at angle 0°
        rx = cx + 200
        ry = cy
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = 0
        layers.append(ray)
    return H(layers)
add("F60: all 4 rays at same angle (overlapping)", case_f60())


# G. Frame variants
def case_g61():
    """Frame rotated 45°."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())


def case_g62():
    """Nested frames."""
    layers = perfect_design()
    inner = make_frame(layers, w=1000, h=600)
    outer = make_frame([inner], w=1280, h=832)
    return make_log([outer], evt())
add("G62: nested frames", case_g62())


def case_g63():
    """Frame stroke."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    frame["strokes"] = [make_stroke(rgb=(0,0,0), weight=4)]
    return make_log([frame], evt())
add("G63: frame stroke", case_g63())


def case_g64():
    """Frame image fill."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832, fill=None)
    frame["fills"] = [{"kind": "image", "src":"bg.jpg", "fit":"cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G64: frame image fill", case_g64())


def case_g65():
    """Frame much smaller than design."""
    layers = perfect_design()
    frame = make_frame(layers, w=300, h=300)
    return make_log([frame], evt())
add("G65: frame 300x300", case_g65())


def case_g66():
    """No frame, design on page."""
    return H(in_frame=False)
add("G66: no frame", case_g66())


def case_g67():
    """Frame translated."""
    layers = perfect_design()
    frame = make_frame(layers, x=500, y=300, w=1280, h=832)
    return make_log([frame], evt())
add("G67: frame translated", case_g67())


def case_g68():
    """2 frames, design in 2nd."""
    f1 = make_frame([], w=1280, h=832)
    f2 = make_frame(perfect_design(), w=1280, h=832)
    return make_log([f1, f2], evt())
add("G68: 2 frames, design in 2nd", case_g68())


def case_g69():
    """Frame size 2000x2000 (huge)."""
    layers = perfect_design()
    frame = make_frame(layers, w=2000, h=2000)
    return make_log([frame], evt())
add("G69: frame 2000x2000", case_g69())


def case_g70():
    """Frame tiny 100x100."""
    layers = perfect_design()
    frame = make_frame(layers, w=100, h=100)
    return make_log([frame], evt())
add("G70: frame 100x100 (smaller than design)", case_g70())


# H. Tools / events
def case_h71():
    """50 move events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move events", case_h71())


def case_h72():
    """50 undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())


def case_h73():
    """No tool changes."""
    sem = [make_event("session_start")]
    sem.append(make_event("create_ellipse"))
    for _ in range(4): sem.append(make_event("create_polygon"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H73: no tool_change", case_h73())


def case_h74():
    """Wrong tool: pen."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.append(make_event("create_ellipse"))
    for _ in range(4): sem.append(make_event("create_polygon"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H74: pen tool used", case_h74())


def case_h75():
    """Star tool used."""
    extras = [make_event("tool_change", before="polygon", after="star"),
              make_event("create_star"), make_event("delete")]
    return H(evts=evt(extras=extras))
add("H75: star tool used then deleted", case_h75())


def case_h76():
    """Many session_end events."""
    sem = evt()
    sem.extend([make_event("session_end")] * 5)
    return H(evts=sem)
add("H76: 5 session_end", case_h76())


def case_h77():
    """20 set_fill_color events."""
    return H(evts=evt(set_fill=20))
add("H77: 20 fill events", case_h77())


def case_h78():
    """Distribute events used."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="x")]))
add("H78: distribute events", case_h78())


def case_h79():
    """Align events used."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H79: align events", case_h79())


def case_h80():
    """Only ellipse tool used (no polygon tool change)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.append(make_event("create_ellipse"))
    for _ in range(4): sem.append(make_event("create_polygon"))
    sem.extend([make_event("set_fill_color")] * 2)
    return H(evts=sem)
add("H80: only ellipse tool changed (no polygon)", case_h80())


# I. Hierarchy / structure
def case_i81():
    """Design in group inside frame."""
    layers = perfect_design()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": layers}
    frame = make_frame([group], w=1280, h=832)
    return make_log([frame], evt())
add("I81: design in group in frame", case_i81())


def case_i82():
    """Design split across 2 frames."""
    layers = perfect_design()
    f1 = make_frame([layers[0]], w=640, h=832)
    f2 = make_frame(layers[1:], w=640, h=832)
    return make_log([f1, f2], evt())
add("I82: circle in frame_a, rays in frame_b", case_i82())


def case_i83():
    """Design in section."""
    layers = perfect_design()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1280, "h": 832,
               "fills": [], "children": layers}
    return make_log([section], evt())
add("I83: design in section", case_i83())


def case_i84():
    """3-deep nested frames."""
    layers = perfect_design()
    f3 = make_frame(layers, w=1280, h=832)
    f2 = make_frame([f3], w=1300, h=850)
    f1 = make_frame([f2], w=1320, h=870)
    return make_log([f1], evt())
add("I84: 3-deep nested frames", case_i84())


def case_i85():
    """Design on page 2."""
    layers = perfect_design()
    frame = make_frame(layers, w=1280, h=832)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I85: design on page 2", case_i85())


def case_i86():
    """Design in component."""
    layers = perfect_design()
    component = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
                 "w": 1280, "h": 832, "fills": [], "strokes": [], "effects": [],
                 "children": layers}
    return make_log([component], evt())
add("I86: design in component", case_i86())


def case_i87():
    """Circle on page, rays in frame."""
    layers = perfect_design()
    frame = make_frame(layers[1:], w=1280, h=832)
    return make_log([frame, layers[0]], evt())
add("I87: circle on page, rays in frame", case_i87())


def case_i88():
    """Each shape in own frame."""
    layers = perfect_design()
    frames = [make_frame([s], w=640, h=832) for s in layers]
    return make_log(frames, evt())
add("I88: each shape in own frame", case_i88())


# J. Bizarre
def case_j89():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J89: empty document", case_j89())


def case_j90():
    """Frame only."""
    return H([])
add("J90: frame only", case_j90())


def case_j91():
    """Text 'sun'."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=YELLOW_SUN)
    text["content"] = "sun"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J91: text 'sun'", case_j91())


def case_j92():
    """Polygon (5-sides) instead of circle."""
    cx, cy = 600, 400
    layers = [L("polygon", cx-50, cy-50, 100, 100, YELLOW_SUN, sides=5)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = L("polygon", rx-30, ry-30, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers, evts=evt(ellipse=0, polygon=5) + [make_event("create_polygon")])
add("J92: pentagon as center (not circle)", case_j92())


def case_j93():
    """Rays as stars."""
    cx, cy = 600, 400
    layers = [L("ellipse", cx-50, cy-50, 100, 100, YELLOW_SUN)]
    for i in range(4):
        angle_rad = i * math.pi / 2
        rx = cx + 200 * math.cos(angle_rad)
        ry = cy + 200 * math.sin(angle_rad)
        ray = make_layer("star", x=rx-30, y=ry-30, w=60, h=60, fill=ORANGE,
                         points=4, innerRatio=0.4)
        layers.append(ray)
    return H(layers, evts=evt(polygon=0) + [make_event("create_star")]*4)
add("J93: rays are stars not polygons", case_j93())


def case_j94():
    """Layer.opacity=0 on all."""
    layers = perfect_design()
    for l in layers:
        l["opacity"] = 0
    return H(layers)
add("J94: design opacity=0", case_j94())


def case_j95():
    """All visible=False."""
    layers = perfect_design()
    for l in layers:
        l["visible"] = False
    return H(layers)
add("J95: design visible=False", case_j95())


def case_j96():
    """Sun = full frame."""
    layers = perfect_design()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    layers[0]["w"] = 1280; layers[0]["h"] = 832
    return H(layers)
add("J96: sun = full frame", case_j96())


def case_j97():
    """Mirror everything scaleX=-1."""
    layers = perfect_design()
    for l in layers:
        l["scaleX"] = -1
    return H(layers)
add("J97: design scaleX=-1", case_j97())


def case_j98():
    """All shapes at exact same point."""
    layers = []
    layers.append(L("ellipse", 600, 400, 100, 100, YELLOW_SUN))
    for i in range(4):
        ray = L("polygon", 600, 400, 60, 60, ORANGE, sides=3)
        ray["rotation"] = i * 90.0
        layers.append(ray)
    return H(layers)
add("J98: all shapes at center (overlapping)", case_j98())


def case_j99():
    """Rays sorted differently in z-order (rays before circle)."""
    layers = perfect_design()
    circle = layers.pop(0)
    layers.append(circle)
    return H(layers)
add("J99: circle drawn above all rays", case_j99())


def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect sun (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = " * FP" if score >= 0.95 else ""
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")

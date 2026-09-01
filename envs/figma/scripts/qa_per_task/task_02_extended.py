"""100 edge cases for task 02 — runs all and prints a sorted score table."""
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
_VERIFIER = HERE.parent.parent / "delivery-1" / "task_02" / "verifier.py"
_spec = importlib.util.spec_from_file_location("_v", _VERIFIER)
_v = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_v)
T = _v.task
GRAY = (0.5, 0.5, 0.5)
SUNSET = [DEEP_PURPLE, PINK, ORANGE, YELLOW, PALE_YELLOW]


def evt(rect=5, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    for _ in range(rect):
        sem.append(make_event("create_rectangle"))
    sem.extend(extras)
    return sem


def L(t, x, y, w, h, fill, **extra):
    return make_layer(t, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_bands():
    """5 horizontal sunset bands, top→bottom, flush stacked."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200, 100 + i*80, 600, 80, c))
    return bands


def H(layers=None, frame_w=1000, frame_h=600, frame_fill=(0.95, 0.95, 0.95),
      evts=None, in_frame=True):
    if layers is None: layers = perfect_bands()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── A. Counts ────────────────────────────────────────────────────────
def case_a1():
    bands = perfect_bands()
    bands.append(L("rectangle", 200, 500, 600, 80, GREEN))  # 6th band
    return H(bands, evts=evt(rect=6))
add("A1: 6 bands (extra)", case_a1())

def case_a2():
    return H(perfect_bands()[:4], evts=evt(rect=4))
add("A2: 4 bands (missing 1)", case_a2())

def case_a3():
    return H(perfect_bands()[:3], evts=evt(rect=3))
add("A3: 3 bands (missing 2)", case_a3())

def case_a4():
    bands = perfect_bands() + [L("rectangle", 200, 500, 600, 80, GREEN),
                                L("rectangle", 200, 580, 600, 80, RED)]
    return H(bands, evts=evt(rect=7))
add("A4: 7 bands", case_a4())

def case_a5():
    return H([], evts=evt(rect=0))
add("A5: 0 bands (empty frame)", case_a5())

def case_a6():
    bands = perfect_bands()
    bands.append(L("rectangle", 200, 100, 600, 80, DEEP_PURPLE))  # duplicate first
    return H(bands, evts=evt(rect=6))
add("A6: 6 bands (duplicate first)", case_a6())

def case_a7():
    bands = perfect_bands() * 2  # 10 bands
    return H(bands, evts=evt(rect=10))
add("A7: 10 bands (doubled)", case_a7())

def case_a8():
    return H([perfect_bands()[0]], evts=evt(rect=1))
add("A8: 1 band only", case_a8())

def case_a9():
    bands = perfect_bands()
    # add 4 ellipses (extras of different type)
    for i in range(4):
        bands.append(make_layer("ellipse", x=100+i*80, y=520, w=50, h=50, fill=GREEN))
    sem = evt(rect=5, extras=[make_event("create_ellipse") for _ in range(4)])
    return H(bands, evts=sem)
add("A9: 5 bands + 4 ellipses extras", case_a9())

def case_a10():
    bands = perfect_bands()[:5]
    # add 1 extra polygon
    bands.append(make_layer("polygon", x=200, y=520, w=100, h=80, fill=GREEN, sides=3))
    return H(bands, evts=evt(rect=5,
             extras=[make_event("tool_change", before="rectangle", after="polygon"),
                     make_event("create_polygon")]))
add("A10: 5 bands + extra polygon", case_a10())


# ─── B. Colors / fills ────────────────────────────────────────────────
def case_b11():
    """All bands solid, but all the same purple."""
    return H([L("rectangle", 200, 100+i*80, 600, 80, DEEP_PURPLE) for i in range(5)])
add("B11: all 5 same purple", case_b11())

def case_b12():
    """Reversed sunset color order."""
    return H([L("rectangle", 200, 100+i*80, 600, 80, list(reversed(SUNSET))[i]) for i in range(5)])
add("B12: reversed color order", case_b12())

def case_b13():
    """Image fill on first band."""
    bands = perfect_bands()
    bands[0]["fills"] = [{"kind": "image", "src": "purple.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(bands)
add("B13: 1st band image fill", case_b13())

def case_b14():
    """All bands have image fills (no solid)."""
    bands = perfect_bands()
    for b in bands:
        b["fills"] = [{"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 1.0, "visible": True}]
    return H(bands)
add("B14: all image fills", case_b14())

def case_b15():
    """All bands stroke-only, no fill."""
    bands = []
    for i, c in enumerate(SUNSET):
        b = L("rectangle", 200, 100+i*80, 600, 80, fill=None)
        b["fills"] = []
        b["strokes"] = [make_stroke(rgb=c, weight=4)]
        bands.append(b)
    return H(bands)
add("B15: stroke-only bands", case_b15())

def case_b16():
    """Bands have empty fills array."""
    bands = perfect_bands()
    for b in bands:
        b["fills"] = []
    return H(bands)
add("B16: empty fills arrays", case_b16())

def case_b17():
    """All near-gray (within color tolerance — distinct will fail)."""
    return H([L("rectangle", 200, 100+i*80, 600, 80, (0.5+i*0.005, 0.5, 0.5)) for i in range(5)])
add("B17: all near-gray", case_b17())

def case_b18():
    """First band is gradient (not solid)."""
    bands = perfect_bands()
    bands[0]["fills"] = [{"kind": "gradient", "stops": [
        {"position": 0, "color": {"r":1,"g":0,"b":0,"a":1}},
        {"position": 1, "color": {"r":0,"g":0,"b":1,"a":1}}], "opacity":1, "visible":True}]
    return H(bands)
add("B18: 1st band gradient", case_b18())

def case_b19():
    """All bands have transparent fills (fillOpacity=0.05)."""
    bands = perfect_bands()
    for b in bands:
        b["fills"][0]["opacity"] = 0.05
    return H(bands)
add("B19: all bands opacity=0.05", case_b19())

def case_b20():
    """Bands have stacked fills (1st solid sunset, 2nd image fill)."""
    bands = perfect_bands()
    for b in bands:
        b["fills"].append({"kind": "image", "src": "x.jpg", "fit": "cover", "opacity": 0.5, "visible": True})
    return H(bands)
add("B20: stacked fills", case_b20())


# ─── C. Sizing ────────────────────────────────────────────────────────
def case_c21():
    """All bands too tall (square aspect)."""
    return H([L("rectangle", 200, 50+i*200, 200, 200, SUNSET[i]) for i in range(5)])
add("C21: all bands square (1:1)", case_c21())

def case_c22():
    """Bands have wildly different widths."""
    widths = [200, 800, 400, 600, 300]
    return H([L("rectangle", 200, 100+i*80, widths[i], 80, SUNSET[i]) for i in range(5)])
add("C22: bands wildly different widths", case_c22())

def case_c23():
    """Bands have wildly different heights."""
    heights = [40, 120, 60, 100, 80]
    bands = []
    y = 100
    for i, h in enumerate(heights):
        bands.append(L("rectangle", 200, y, 600, h, SUNSET[i]))
        y += h
    return H(bands)
add("C23: bands different heights", case_c23())

def case_c24():
    """All bands tiny (10×5)."""
    return H([L("rectangle", 200, 100+i*5, 10, 5, SUNSET[i]) for i in range(5)])
add("C24: all tiny bands", case_c24())

def case_c25():
    """Bands wider than frame."""
    return H([L("rectangle", -100, 100+i*80, 1500, 80, SUNSET[i]) for i in range(5)])
add("C25: bands wider than frame", case_c25())

def case_c26():
    """Bands very narrow but tall (vertical aspect)."""
    return H([L("rectangle", 100+i*80, 100, 80, 400, SUNSET[i]) for i in range(5)])
add("C26: bands narrow vertical 80×400", case_c26())

def case_c27():
    """Just-inside aspect ratio (2.001:1)."""
    return H([L("rectangle", 200, 100+i*80, 161, 80, SUNSET[i]) for i in range(5)])
add("C27: bands just-inside aspect (161/80)", case_c27())

def case_c28():
    """Just-outside aspect ratio (1.99:1)."""
    return H([L("rectangle", 200, 100+i*80, 159, 80, SUNSET[i]) for i in range(5)])
add("C28: bands just-outside aspect (159/80)", case_c28())

def case_c29():
    """Same width but heights differ slightly (within tol)."""
    heights = [80, 81, 79, 82, 78]
    bands = []
    y = 100
    for i, h in enumerate(heights):
        bands.append(L("rectangle", 200, y, 600, h, SUNSET[i]))
        y += h
    return H(bands)
add("C29: heights ±2px (within tol)", case_c29())

def case_c30():
    """Bands first big, rest tiny."""
    bands = [L("rectangle", 200, 100, 600, 200, SUNSET[0])]
    for i in range(1, 5):
        bands.append(L("rectangle", 200, 300+i*10, 600, 10, SUNSET[i]))
    return H(bands)
add("C30: 1 huge + 4 tiny bands", case_c30())


# ─── D. Position ──────────────────────────────────────────────────────
def case_d31():
    """Bands stacked but not centered (different x positions)."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 100 + i*30, 100+i*80, 600, 80, c))
    return H(bands)
add("D31: bands not aligned (drifting x)", case_d31())

def case_d32():
    """Bands shifted off-frame (negative x)."""
    return H([L("rectangle", -200, 100+i*80, 600, 80, SUNSET[i]) for i in range(5)])
add("D32: bands at x=-200 (off-frame left)", case_d32())

def case_d33():
    """Bands stacked vertically — but reversed Y order."""
    return H([L("rectangle", 200, 500-i*80, 600, 80, SUNSET[i]) for i in range(5)])
add("D33: bands stacked top→bottom but Y reversed", case_d33())

def case_d34():
    """Bands with 50px gaps."""
    return H([L("rectangle", 200, 100+i*130, 600, 80, SUNSET[i]) for i in range(5)])
add("D34: 50px gaps between bands", case_d34())

def case_d35():
    """Bands with -10px overlap."""
    return H([L("rectangle", 200, 100+i*70, 600, 80, SUNSET[i]) for i in range(5)])
add("D35: bands -10px overlap", case_d35())

def case_d36():
    """Bands are stacked diagonally."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 100+i*100, 100+i*80, 600, 80, c))
    return H(bands)
add("D36: bands stacked diagonally", case_d36())

def case_d37():
    """Bands stacked horizontally (axis swap)."""
    return H([L("rectangle", 100+i*150, 200, 150, 200, SUNSET[i]) for i in range(5)])
add("D37: bands stacked horizontally (vertical aspect)", case_d37())

def case_d38():
    """Bands at exact same y (all overlapping)."""
    return H([L("rectangle", 200, 200, 600, 80, SUNSET[i]) for i in range(5)])
add("D38: bands all at same y (piled)", case_d38())

def case_d39():
    """Bands aligned but with 8px tolerance gap (within tol)."""
    return H([L("rectangle", 200, 100+i*88, 600, 80, SUNSET[i]) for i in range(5)])
add("D39: bands +8px stacking gap (within tol)", case_d39())

def case_d40():
    """Bands shift centers slightly (4px x drift, within tol)."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200+(i%2)*4, 100+i*80, 600, 80, c))
    return H(bands)
add("D40: bands ±4px x-drift (within tol)", case_d40())


# ─── E. Per-shape variants ─────────────────────────────────────────────
def case_e41():
    """First band rotated 5°."""
    bands = perfect_bands()
    bands[0]["rotation"] = 5
    return H(bands)
add("E41: 1st band rotated 5°", case_e41())

def case_e42():
    """All bands rotated 5°."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 5
    return H(bands)
add("E42: all rotated 5°", case_e42())

def case_e43():
    """All bands rotated 90° (now vertical)."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 90
    return H(bands)
add("E43: all rotated 90° (becomes vertical)", case_e43())

def case_e44():
    """All bands rotated 45°."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 45
    return H(bands)
add("E44: all rotated 45°", case_e44())

def case_e45():
    """All bands rotated 180°."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 180
    return H(bands)
add("E45: all rotated 180°", case_e45())

def case_e46():
    """1st band scaleX=-1."""
    bands = perfect_bands()
    bands[0]["scaleX"] = -1
    return H(bands)
add("E46: 1st band scaleX=-1", case_e46())

def case_e47():
    """All bands have cornerRadius=40 (very rounded)."""
    bands = perfect_bands()
    for b in bands: b["cornerRadius"] = 40
    return H(bands)
add("E47: all bands cornerRadius=40", case_e47())

def case_e48():
    """1 band scaleY=-1."""
    bands = perfect_bands()
    bands[2]["scaleY"] = -1
    return H(bands)
add("E48: 3rd band scaleY=-1", case_e48())

def case_e49():
    """1st band rotated 4° (under 5° tolerance)."""
    bands = perfect_bands()
    bands[0]["rotation"] = 4
    return H(bands)
add("E49: 1st band rotated 4° (under tol)", case_e49())

def case_e50():
    """All bands rotated 1° (within tol but each)."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 1
    return H(bands)
add("E50: all rotated 1°", case_e50())


# ─── F. Subcomponent variants ─────────────────────────────────────────
def case_f51():
    """Bands present plus 5 stripes-as-ellipses."""
    bands = perfect_bands()
    for i in range(5):
        bands.append(make_layer("ellipse", x=100, y=520+i*30, w=600, h=20, fill=SUNSET[i]))
    sem = evt(rect=5, extras=[make_event("tool_change", before="rectangle", after="ellipse"),
                                *[make_event("create_ellipse") for _ in range(5)]])
    return H(bands, evts=sem)
add("F51: 5 bands + 5 ellipse stripes", case_f51())

def case_f52():
    """Squashed bands (different aspect)."""
    return H([L("rectangle", 200, 100+i*40, 200, 40, SUNSET[i]) for i in range(5)])
add("F52: small squashed bands", case_f52())

def case_f53():
    """Stretched bands (huge wide)."""
    return H([L("rectangle", 0, 100+i*100, 1280, 100, SUNSET[i]) for i in range(5)],
             frame_w=1280, frame_h=700)
add("F53: stretched bands (full frame width)", case_f53())

def case_f54():
    """Bands centered but jittered y positions (intermixed)."""
    return H([L("rectangle", 200, 200+(i*80 % 200), 600, 80, SUNSET[i]) for i in range(5)])
add("F54: bands jittered y positions", case_f54())

def case_f55():
    """Bands horizontal but each with 100px gap and shifted x."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", 200+i*5, 100+i*180, 600, 80, c))
    return H(bands)
add("F55: bands big gaps + drifting x", case_f55())

def case_f56():
    """Bands stacked but in wrong vertical order (color order mismatch)."""
    cols = [PINK, DEEP_PURPLE, ORANGE, YELLOW, PALE_YELLOW]  # purple+pink swapped
    return H([L("rectangle", 200, 100+i*80, 600, 80, cols[i]) for i in range(5)])
add("F56: purple/pink swapped", case_f56())

def case_f57():
    """All bands flush, but 2 bands have overlap by 30px."""
    return H([L("rectangle", 200, 100+i*60, 600, 80, SUNSET[i]) for i in range(5)])
add("F57: bands -20px overlap each", case_f57())

def case_f58():
    """Bands with no fill on 1 band (but stroke present)."""
    bands = perfect_bands()
    bands[2]["fills"] = []
    bands[2]["strokes"] = [make_stroke(rgb=ORANGE, weight=2)]
    return H(bands)
add("F58: 1 band stroke-only", case_f58())

def case_f59():
    """All bands at zero width."""
    return H([L("rectangle", 200, 100+i*80, 0, 80, SUNSET[i]) for i in range(5)])
add("F59: bands 0 width", case_f59())

def case_f60():
    """Bands with normal sizes but stroke-only first band."""
    bands = perfect_bands()
    bands[0]["fills"] = []
    bands[0]["strokes"] = [make_stroke(rgb=DEEP_PURPLE, weight=4)]
    return H(bands)
add("F60: 1st band stroke-only", case_f60())


# ─── G. Frame variants ────────────────────────────────────────────────
def case_g61():
    """Frame rotated 45°."""
    bands = perfect_bands()
    frame = make_frame(bands, w=1000, h=600)
    frame["rotation"] = 45
    return make_log([frame], evt())
add("G61: frame rotated 45°", case_g61())

def case_g62():
    """Bands in nested frame inside outer frame."""
    bands = perfect_bands()
    inner = make_frame(bands, w=900, h=500)
    outer = make_frame([inner], w=1280, h=800)
    return make_log([outer], evt())
add("G62: bands in nested frames", case_g62())

def case_g63():
    """2 frames, bands in 2nd."""
    f1 = make_frame([], w=500, h=400)
    f2 = make_frame(perfect_bands(), w=1000, h=600)
    return make_log([f1, f2], evt())
add("G63: 2 frames, bands in 2nd", case_g63())

def case_g64():
    """Frame has stroke."""
    bands = perfect_bands()
    frame = make_frame(bands, w=1000, h=600)
    frame["strokes"] = [make_stroke(rgb=BLACK, weight=4)]
    return make_log([frame], evt())
add("G64: frame has stroke", case_g64())

def case_g65():
    """Frame has image fill."""
    bands = perfect_bands()
    frame = make_frame(bands, w=1000, h=600, fill=None)
    frame["fills"] = [{"kind": "image", "src": "bg.jpg", "fit": "cover", "opacity":1, "visible":True}]
    return make_log([frame], evt())
add("G65: frame image fill", case_g65())

def case_g66():
    """Frame translated to (500,300)."""
    bands = perfect_bands()
    frame = make_frame(bands, x=500, y=300, w=1000, h=600)
    return make_log([frame], evt())
add("G66: frame translated", case_g66())

def case_g67():
    """Frame way too small (200×200 cropping bands)."""
    return H(frame_w=200, frame_h=200)
add("G67: tiny 200x200 frame", case_g67())

def case_g68():
    """Frame way too big (4000×3000)."""
    return H(frame_w=4000, frame_h=3000)
add("G68: huge frame", case_g68())

def case_g69():
    """Frame with 1280x832 (default-house-frame size)."""
    return H(frame_w=1280, frame_h=832)
add("G69: frame 1280×832", case_g69())

def case_g70():
    """Frame 100% bands width (no margin)."""
    return H(frame_w=600, frame_h=400, in_frame=True)
add("G70: frame matches bands' width exactly", case_g70())


# ─── H. Tools / events ────────────────────────────────────────────────
def case_h71():
    """50 move_layer events."""
    return H(evts=evt(extras=[make_event("move_layer") for _ in range(50)]))
add("H71: 50 move_layer events", case_h71())

def case_h72():
    """50 undo events."""
    return H(evts=evt(extras=[make_event("undo") for _ in range(50)]))
add("H72: 50 undo events", case_h72())

def case_h73():
    """No tool_change events (keyboard shortcuts only)."""
    sem = [make_event("session_start")]
    sem.extend([make_event("create_rectangle")] * 5)
    return H(evts=sem)
add("H73: no tool_change events", case_h73())

def case_h74():
    """Tool=ellipse (wrong tool used)."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="ellipse")]
    sem.extend([make_event("create_rectangle")] * 5)
    return H(evts=sem)
add("H74: ellipse tool selected (no rectangle tool)", case_h74())

def case_h75():
    """Pen tool used."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="pen")]
    sem.extend([make_event("create_rectangle")] * 5)
    return H(evts=sem)
add("H75: pen tool only (no rectangle tool)", case_h75())

def case_h76():
    """5 create_rectangles + 3 deletes."""
    sem = evt()
    sem.extend([make_event("delete") for _ in range(3)])
    return H(evts=sem)
add("H76: 5 create + 3 delete events", case_h76())

def case_h77():
    """0 create_rectangle events."""
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle")]
    return H(evts=sem)
add("H77: 0 create_rectangle events", case_h77())

def case_h78():
    """100 set_fill_color events."""
    return H(evts=evt(extras=[make_event("set_fill_color") for _ in range(100)]))
add("H78: 100 set_fill_color events", case_h78())

def case_h79():
    """Distribute_layers used."""
    return H(evts=evt(extras=[make_event("distribute_layers", axis="y")]))
add("H79: distribute_layers used", case_h79())

def case_h80():
    """Align_layers used."""
    return H(evts=evt(extras=[make_event("align_layers", axis="center_x")]))
add("H80: align_layers used", case_h80())


# ─── I. Hierarchy ──────────────────────────────────────────────────────
def case_i81():
    """Bands inside a group inside frame."""
    bands = perfect_bands()
    group = {"id": "group_1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
             "fills": [], "strokes": [], "effects": [], "children": bands}
    frame = make_frame([group], w=1000, h=600)
    return make_log([frame], evt())
add("I81: bands in group in frame", case_i81())

def case_i82():
    """Bands split across 2 frames."""
    bands = perfect_bands()
    f1 = make_frame(bands[:2], w=500, h=600)
    f2 = make_frame(bands[2:], w=500, h=600)
    return make_log([f1, f2], evt())
add("I82: bands split 2-and-3 across 2 frames", case_i82())

def case_i83():
    """Bands inside section (not frame)."""
    bands = perfect_bands()
    section = {"id": "sec_1", "type": "section", "x": 0, "y": 0, "w": 1000, "h": 600,
               "fills": [], "children": bands}
    return make_log([section], evt())
add("I83: bands in section (not frame)", case_i83())

def case_i84():
    """Bands directly on page (no frame)."""
    return H(in_frame=False)
add("I84: bands on page (no frame)", case_i84())

def case_i85():
    """3-deep nested frames containing bands."""
    bands = perfect_bands()
    f3 = make_frame(bands, w=900, h=500)
    f2 = make_frame([f3], w=1000, h=600)
    f1 = make_frame([f2], w=1100, h=700)
    return make_log([f1], evt())
add("I85: 3-deep nested frames", case_i85())

def case_i86():
    """Bands on page 2 of multi-page doc."""
    bands = perfect_bands()
    frame = make_frame(bands, w=1000, h=600)
    page1 = {"id":"p1","children":[],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    page2 = {"id":"p2","children":[frame],"prototypeSettings":{"device":None,"backgroundColor":{"r":0,"g":0,"b":0,"a":1}},"prototypeFlows":[]}
    return {"schemaVersion":1,"sessionId":"qa","raw":[],"semantic":evt(),
            "outcome":{"summary":{"shapeCounts":{}},"document":{"pages":[page1,page2]}}}
add("I86: bands on page 2", case_i86())

def case_i87():
    """Each band in its own frame."""
    bands = perfect_bands()
    frames = [make_frame([b], w=600, h=80) for b in bands]
    return make_log(frames, evt())
add("I87: each band in own frame", case_i87())

def case_i88():
    """Bands inside component."""
    bands = perfect_bands()
    comp = {"id": "comp_1", "type": "component", "x": 0, "y": 0,
            "w": 1000, "h": 600, "fills": [], "strokes": [], "effects": [],
            "children": bands}
    return make_log([comp], evt())
add("I88: bands inside component", case_i88())

def case_i89():
    """Bands inside 2 nested groups inside a frame."""
    bands = perfect_bands()
    g1 = {"id": "g1", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": bands}
    g2 = {"id": "g2", "type": "group", "x": 0, "y": 0, "w": 0, "h": 0,
          "fills": [], "strokes": [], "effects": [], "children": [g1]}
    frame = make_frame([g2], w=1000, h=600)
    return make_log([frame], evt())
add("I89: bands in nested groups in frame", case_i89())

def case_i90():
    """1 band inside frame, 4 outside on page."""
    bands = perfect_bands()
    frame = make_frame([bands[0]], w=1000, h=600)
    return make_log([frame, *bands[1:]], evt())
add("I90: only 1st band in frame", case_i90())


# ─── J. Bizarre / hard ────────────────────────────────────────────────
def case_j91():
    """Mirrored (scaleX=-1) on all bands."""
    bands = perfect_bands()
    for b in bands: b["scaleX"] = -1
    return H(bands)
add("J91: all bands scaleX=-1", case_j91())

def case_j92():
    """Empty document."""
    return make_log([], [make_event("session_start")])
add("J92: empty document", case_j92())

def case_j93():
    """All bands at same point."""
    return H([L("rectangle", 500, 300, 100, 100, SUNSET[i]) for i in range(5)])
add("J93: all bands piled at one point", case_j93())

def case_j94():
    """All bands = full frame."""
    return H([L("rectangle", 0, 0, 1000, 600, SUNSET[i]) for i in range(5)])
add("J94: all bands = full frame", case_j94())

def case_j95():
    """Bands with negative coords."""
    bands = []
    for i, c in enumerate(SUNSET):
        bands.append(L("rectangle", -100, -300+i*80, 600, 80, c))
    return H(bands)
add("J95: bands with negative coords", case_j95())

def case_j96():
    """Text 'sunset' instead of rectangles."""
    text = make_layer("text", x=400, y=400, w=200, h=50, fill=DEEP_PURPLE)
    text["content"] = "sunset gradient"
    return make_log([text], [make_event("session_start"), make_event("create_text")])
add("J96: text 'sunset' (no shapes)", case_j96())

def case_j97():
    """5 bands but 4 are stars (1 rectangle)."""
    bands = [perfect_bands()[0]]
    for i in range(1, 5):
        bands.append(make_layer("star", x=200, y=100+i*80, w=600, h=80, fill=SUNSET[i], points=5, innerRatio=0.4))
    return H(bands, evts=evt(rect=1, extras=[make_event("create_star") for _ in range(4)]))
add("J97: 4 stars + 1 rectangle", case_j97())

def case_j98():
    """1×1 degenerate bands."""
    return H([L("rectangle", 500, 300+i, 1, 1, SUNSET[i]) for i in range(5)])
add("J98: bands 1×1 degenerate", case_j98())

def case_j99():
    """All bands' rotation set to 360 (full rotation = same as 0)."""
    bands = perfect_bands()
    for b in bands: b["rotation"] = 360
    return H(bands)
add("J99: rotation=360° (≡ 0)", case_j99())

def case_j100():
    """Perfect (control)."""
    return H()
add("J100: perfect (control)", case_j100())


# Run all
print(f"\n{'#':>3} {'Case':<60} {'Score':>6}  Rubric breakdown")
print("─" * 130)
fp_count = 0
for i, (label, log) in enumerate(CASES, 1):
    try:
        score, b = score_task(T, log)
        breakdown = "  ".join(f"{name[:4]}={r:.2f}" for name, r, _, _ in b["rubrics"])
        eff = b["efficiency"]
        flag = ""
        if score >= 0.95 and not label.startswith("J100"):
            flag = " FP"
            fp_count += 1
        print(f"{i:>3} {label:<60} {score:>6.3f}  {breakdown}  eff={eff:.2f}{flag}")
    except Exception as e:
        print(f"{i:>3} {label:<60} CRASH: {repr(e)[:60]}")
print(f"\nStrict FPs (≥0.95, not J100): {fp_count}")

"""Round 3 novel deceptions for task 24 — centered white rounded modal w/ shadow."""
from __future__ import annotations
import sys
sys.path.insert(0, "/Users/rashidalblwi/figma-mock/test-verifier")

from qa_per_task._helpers import (
    make_layer, make_frame, make_log, make_event, make_stroke, make_drop_shadow,
    score_task, NAVY, WHITE, RED, GREEN, PURPLE,
)
from tasks import task_24_centered_modal as t
T = t.task


def evt(rect=1, set_fill=1, frame=1, align=2, extras=()):
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="frame"),
           make_event("tool_change", before="frame", after="rectangle")]
    for _ in range(frame): sem.append(make_event("create_frame"))
    for _ in range(rect): sem.append(make_event("create_rectangle"))
    for _ in range(set_fill): sem.append(make_event("set_fill_color"))
    for _ in range(align): sem.append(make_event("align_layers", axis="center_x"))
    sem.extend(extras)
    return sem


def L(typ, x, y, w, h, fill, **extra):
    return make_layer(typ, x=x, y=y, w=w, h=h, fill=fill, **extra)


def perfect_modal(frame_w=1280, frame_h=832, modal_w=400, modal_h=240,
                  modal_color=WHITE, radius=16, shadow=True):
    cx = frame_w / 2 - modal_w / 2
    cy = frame_h / 2 - modal_h / 2
    modal = L("rectangle", cx, cy, modal_w, modal_h, modal_color,
              cornerRadius=radius)
    if shadow:
        modal["effects"] = [make_drop_shadow(x=0, y=4, blur=8, spread=0,
                                              rgb=(0,0,0), alpha=0.25)]
    return [modal]


def H(layers=None, evts=None, frame_w=1280, frame_h=832,
      frame_fill=(0.95, 0.95, 0.95), in_frame=True):
    if layers is None: layers = perfect_modal()
    if in_frame:
        frame = make_frame(layers, w=frame_w, h=frame_h, fill=frame_fill)
        return make_log([frame], evts or evt())
    return make_log(layers, evts or evt())


CASES = []
def add(label, log): CASES.append((label, log))


# ─── K. Subtle deceptions ────────────────────────────────────────────
def k1():
    """Modal off-center by 11px (within 12 tol)."""
    layers = perfect_modal()
    layers[0]["x"] += 11
    return H(layers)
add("K1: 11px off-center (within tol)", k1())

def k2():
    """Modal off-center by 13px (just over)."""
    layers = perfect_modal()
    layers[0]["x"] += 13
    return H(layers)
add("K2: 13px off-center (just over)", k2())

def k3():
    """Modal rotated 1.9°."""
    layers = perfect_modal()
    layers[0]["rotation"] = 1.9
    return H(layers)
add("K3: rotated 1.9° (under tol)", k3())

def k4():
    """Drop shadow alpha=0.04 (just under threshold 0.05)."""
    layers = perfect_modal(shadow=False)
    layers[0]["effects"] = [make_drop_shadow(alpha=0.04)]
    return H(layers)
add("K4: shadow alpha=0.04 (under threshold)", k4())

def k5():
    """Modal cornerRadius=320 (frac=0.8 — looks like full pill)."""
    layers = perfect_modal()
    layers[0]["cornerRadius"] = 320  # frac of 400 = 0.8
    return H(layers)
add("K5: cornerRadius frac 0.8 (extreme)", k5())

def k6():
    """Modal width frac at exactly 10% (lower boundary)."""
    return H(perfect_modal(modal_w=128, modal_h=80))
add("K6: width frac 10% (boundary)", k6())

def k7():
    """Modal width frac just under 10%."""
    return H(perfect_modal(modal_w=120, modal_h=80))
add("K7: width frac just under 10%", k7())

def k8():
    """Modal width frac at exactly 85% (upper boundary)."""
    return H(perfect_modal(modal_w=1088, modal_h=600))
add("K8: width frac 85% (boundary)", k8())


# ─── L. Visibility tricks ────────────────────────────────────────────
def l1():
    """Modal layer.visible=False."""
    layers = perfect_modal()
    layers[0]["visible"] = False
    return H(layers)
add("L1: layer.visible=False", l1())

def l2():
    """Modal fill.visible=False."""
    layers = perfect_modal()
    layers[0]["fills"][0]["visible"] = False
    return H(layers)
add("L2: fill.visible=False", l2())

def l3():
    """Modal opacity=0.4."""
    layers = perfect_modal()
    layers[0]["opacity"] = 0.4
    return H(layers)
add("L3: opacity=0.4 (under tol)", l3())

def l4():
    """Modal fill alpha=0.4."""
    layers = perfect_modal()
    layers[0]["fills"][0]["color"]["a"] = 0.4
    return H(layers)
add("L4: fill alpha=0.4", l4())

def l5():
    """Drop shadow color alpha=0 (subtle hide)."""
    layers = perfect_modal(shadow=False)
    layers[0]["effects"] = [make_drop_shadow(alpha=0.0)]
    return H(layers)
add("L5: shadow alpha=0", l5())


# ─── M. Geometry tricks ──────────────────────────────────────────────
def m1():
    """Modal positioned not via align tool — manual coords."""
    layers = perfect_modal()
    sem = [make_event("session_start"),
           make_event("tool_change", before="select", after="rectangle"),
           make_event("create_rectangle"),
           make_event("set_fill_color"),
           make_event("move_layer"), make_event("move_layer")]
    return H(layers, evts=sem)
add("M1: modal centered without align tool", m1())

def m2():
    """Modal at (0,0) but cornerRadius and white — not centered."""
    layers = perfect_modal()
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("M2: modal at (0,0)", m2())

def m3():
    """Modal centered visually but extends past frame."""
    layers = perfect_modal(modal_w=1500, modal_h=1000)
    return H(layers)
add("M3: modal larger than frame, centered", m3())

def m4():
    """Modal scaled up to fill frame."""
    layers = perfect_modal(modal_w=1280, modal_h=832)
    layers[0]["x"] = 0; layers[0]["y"] = 0
    return H(layers)
add("M4: modal = frame size", m4())

def m5():
    """3 modals at different positions."""
    layers = []
    for x in [200, 540, 880]:
        m = L("rectangle", x, 296, 200, 240, WHITE, cornerRadius=16)
        m["effects"] = [make_drop_shadow()]
        layers.append(m)
    return H(layers, evts=evt(rect=3))
add("M5: 3 modals (only 1 should exist)", m5())

def m6():
    """Modal centered but cornerRadius=0."""
    layers = perfect_modal(radius=0)
    return H(layers)
add("M6: centered but no rounding", m6())

def m7():
    """Modal centered but no shadow."""
    layers = perfect_modal(shadow=False)
    return H(layers)
add("M7: centered but no shadow", m7())


# ─── N. Structural tricks ────────────────────────────────────────────
def n1():
    """Modal in component (no real frame)."""
    layers = perfect_modal()
    comp = {"id":"c","type":"component","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([comp], evt())
add("N1: modal in component", n1())

def n2():
    """Modal in section."""
    layers = perfect_modal()
    sec = {"id":"s","type":"section","x":0,"y":0,"w":1280,"h":832,
           "fills":[],"children":layers}
    return make_log([sec], evt())
add("N2: modal in section", n2())

def n3():
    """Modal in instance."""
    layers = perfect_modal()
    inst = {"id":"i","type":"instance","x":0,"y":0,"w":1280,"h":832,
            "fills":[],"strokes":[],"effects":[],"children":layers}
    return make_log([inst], evt())
add("N3: modal in instance", n3())

def n4():
    """Modal in 4-deep nested frames."""
    layers = perfect_modal()
    f4 = make_frame(layers, w=1280, h=832)
    f3 = make_frame([f4], w=1280, h=832)
    f2 = make_frame([f3], w=1280, h=832)
    f1 = make_frame([f2], w=1280, h=832)
    return make_log([f1], evt(frame=4))
add("N4: modal 4-deep nested", n4())

def n5():
    """Modal inside group inside frame."""
    layers = perfect_modal()
    g = {"id":"g","type":"group","x":0,"y":0,"w":400,"h":240,
         "fills":[],"strokes":[],"effects":[],"children":layers}
    return H([g])
add("N5: modal in group in frame", n5())


# ─── O. Wrong types ─────────────────────────────────────────────────
def o1():
    """Modal is ellipse."""
    s = make_layer("ellipse", x=440, y=296, w=400, h=240, fill=WHITE)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("O1: modal is ellipse", o1())

def o2():
    """Modal is star."""
    s = make_layer("star", x=440, y=296, w=400, h=240, fill=WHITE,
                    points=5, innerRatio=0.4, cornerRadius=16)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("O2: modal is star", o2())

def o3():
    """Modal is polygon."""
    s = make_layer("polygon", x=440, y=296, w=400, h=240, fill=WHITE,
                    sides=4, cornerRadius=16)
    s["effects"] = [make_drop_shadow()]
    return H([s], evts=evt(rect=0))
add("O3: modal is polygon", o3())

def o4():
    """Modal is text."""
    text = make_layer("text", x=440, y=296, w=400, h=240, fill=NAVY)
    text["content"] = "centered modal"
    return H([text], evts=[make_event("session_start"),
                            make_event("create_text"),
                            make_event("align_layers")])
add("O4: modal is text", o4())


# ─── Run ────────────────────────────────────────────────────────────
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

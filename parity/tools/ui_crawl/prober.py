"""Press / observe / classify / restore, zone-aware, foreground-safe (DESIGN section 6.1-6.6).

Pure, unit-tested: classify(), Snapshot, zone_point().
Live: probe() drives injected input only (never InvokePattern/ExecuteMso on an unclassified
control -- that deadlocks Word's UI thread, per the ExecuteMso precedent in this repo).
"""
import time
from dataclasses import dataclass, field

import win32gui, win32process
from pywinauto import mouse
from pywinauto.keyboard import send_keys

import config, ids, uia

# Window classes pinned from the live tree/probes.
DIALOG_CLASSES = {"NUIDialog", "#32770", "bosa_sdm_msword", "bosa_sdm_Mso96"}
POPUP_CLASSES = {"NetUIHWND", "Net UI Tool Window", "MsoCommandBarPopup", "NetUITWPopupWindow"}
_MIN_POPUP_AREA = 10_000        # tooltip exclusion (DESIGN section 6.1)


@dataclass
class Snapshot:
    windows: list          # [(class, title)] of PID-owned dialog-class top-levels
    popups: list           # [hwnd] of PID-owned popup-class top-levels (flyouts)
    panes_open: int        # count of docked task panes
    doc_hash: str
    toggle_state: object   # control toggle/selection state (None if not stateful)
    fingerprint: dict
    popup_els: list = field(default_factory=list)   # [(hwnd, class, title, rect)] for capture


def _is_dialog_class(cls):
    return cls in DIALOG_CLASSES or "Dialog" in cls


def classify(before, after):
    new_wins = [w for w in after.windows if w not in before.windows]
    if any(_is_dialog_class(w[0]) for w in new_wins):
        return "dialog"
    if [p for p in after.popups if p not in before.popups]:
        return "popup"
    if after.panes_open > before.panes_open:
        return "pane"
    if (before.toggle_state is not None and after.toggle_state is not None
            and after.toggle_state != before.toggle_state):
        return "toggles"
    if after.doc_hash != before.doc_hash:
        return "feature"
    return "unresolved"


def zone_point(rect, zone, split_children):
    """Absolute click point for a control zone. Prefers exposed split-child rects; else
    orientation-aware fallback; zone None -> geometric center."""
    l, t, r, b = rect
    if split_children:
        child = split_children[0] if zone == "primary" else split_children[-1]
        cl, ct, cr, cb = child
        return ((cl + cr) // 2, (ct + cb) // 2)
    if zone is None:
        return ((l + r) // 2, (t + b) // 2)
    w, h = r - l, b - t
    if h > 0.9 * w:                     # vertical split: primary=top third, flyout=bottom third
        y = t + h // 6 if zone == "primary" else t + 5 * h // 6
        return ((l + r) // 2, y)
    x = l + 3 * w // 8 if zone == "primary" else l + 7 * w // 8   # horizontal split
    return (x, (t + b) // 2)


# ---- live snapshot helpers ----

def _pid_toplevels(pid):
    out = []

    def cb(hwnd, _):
        try:
            if not win32gui.IsWindowVisible(hwnd):
                return True
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid != pid:
                return True
            cls = win32gui.GetClassName(hwnd)
            title = win32gui.GetWindowText(hwnd)
            l, t, r, b = win32gui.GetWindowRect(hwnd)
            out.append((hwnd, cls, title, (l, t, r, b), (r - l) * (b - t)))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(cb, None)
    return out


def _is_nag(title):
    import re
    return any(re.search(sig, title or "") for sig in config.NAG_SIGNATURES)


# Task-pane host window classes (docked panes). Seeded from Office; the exact class is
# confirmed/extended in T12 by dumping child-window classes when the Styles pane opens.
PANE_CLASSES = {"MsoWorkPane", "NetUIHWND"}


def _count_task_panes(session):
    """Fast win32 child-window scan for docked task panes (right-docked, tall). Avoids an
    expensive UIA descendants() walk in the observe hot loop. None of the 5 T9 archetypes
    opens a pane; this path is exercised/tuned in T12 (Styles / Clipboard / Navigation)."""
    main = session._hwnd()
    found = []

    def cb(h, _):
        try:
            cls = win32gui.GetClassName(h)
            l, t, r, b = win32gui.GetWindowRect(h)
            if "WorkPane" in cls and (b - t) > 300:      # docked, tall
                found.append(h)
        except Exception:
            pass
        return True

    try:
        win32gui.EnumChildWindows(main, cb, None)
    except Exception:
        pass
    return len(found)


def _read_toggle_state(control_el):
    try:
        return ("toggle", control_el.get_toggle_state())
    except Exception:
        pass
    try:
        return ("selection", int(bool(control_el.is_selected())))
    except Exception:
        pass
    try:
        raw = control_el.element_info.element     # SelectionItem is how Office toggles expose state
        if raw.GetCurrentPropertyValue(30096):    # IsSelectionItemPatternAvailable
            return ("selection-raw", int(bool(raw.GetCurrentPropertyValue(30079))))  # IsSelected
    except Exception:
        pass
    return None


def _snapshot(session, win, control_el, main_hwnd, count_panes=True):
    tops = _pid_toplevels(session.pid)
    windows, popups, popup_els = [], [], []
    for hwnd, cls, title, rect, area in tops:
        if hwnd == main_hwnd:
            continue
        if _is_nag(title):
            continue
        if _is_dialog_class(cls):
            windows.append((cls, title))
        elif cls in POPUP_CLASSES and area > _MIN_POPUP_AREA:
            popups.append(hwnd)
            popup_els.append((hwnd, cls, title, rect))
    ts = _read_toggle_state(control_el) if control_el is not None else None
    # COM calls raise 'application is busy' while a modal dialog is up -- but the dialog is
    # already detected above (win32), so a sentinel doc_hash is harmless (dialog wins classify).
    try:
        dh = session.doc_hash()
    except Exception:
        dh = "<com-busy>"
    try:
        fp = session.app_fingerprint()
    except Exception:
        fp = {}
    return Snapshot(windows=windows, popups=popups,
                    panes_open=_count_task_panes(session) if count_panes else 0,
                    doc_hash=dh, toggle_state=ts, fingerprint=fp, popup_els=popup_els)


def _ensure_ribbon_foreground(session):
    """Force the MAIN Word window foreground (for clicking a ribbon control -- no surface open)."""
    uia._force_foreground(session._hwnd())


def _ensure_word_foreground(session):
    """Refocus a Word window ONLY if the console/another process stole foreground. Does NOT
    steal focus from an already-Word-foreground surface (e.g. a modal dialog) -- forcing the
    main window while a modal dialog is up sends the ESC to the disabled main window instead."""
    fg = win32gui.GetForegroundWindow()
    try:
        _, fpid = win32process.GetWindowThreadProcessId(fg)
    except Exception:
        fpid = None
    if fpid != session.pid:
        uia._force_foreground(session._hwnd())


def _observe(session, win, control_el, main_hwnd, before):
    """Adaptive: wait 1.5s baseline, extend to 5s while windows are still appearing;
    return once the surface set is stable across two reads."""
    last, stable, t0 = None, 0, time.time()
    while time.time() - t0 < 5.0:
        time.sleep(0.25)
        snap = _snapshot(session, win, control_el, main_hwnd)
        shape = (len(snap.windows), len(snap.popups), snap.panes_open,
                 snap.doc_hash, snap.toggle_state)
        if last is not None and shape == last:
            stable += 1
            if stable >= 2 and time.time() - t0 >= 1.5:
                return snap
        else:
            stable = 0
        last = shape
        result = snap
    return result


def _ref_for(cls, control_id, after, before):
    seg = control_id.split(".")[-1]
    if cls == "dialog":
        new = [w for w in after.windows if w not in before.windows]
        title = new[0][1] if new and new[0][1] else seg
        return ids.surface_id("dialogs", title)
    if cls == "popup":
        return ids.surface_id("dropdowns", seg)
    if cls == "pane":
        return ids.surface_id("panes", seg)
    return None


def _clear_surfaces(session, win, control_el, main_hwnd, tries=4):
    """ESC away any open dialog/popup; do NOT force main foreground (that ESCs the disabled
    main window while a modal dialog is up). Returns the final snapshot."""
    after = _snapshot(session, win, control_el, main_hwnd)
    for _ in range(tries):
        if not after.windows and not after.popups:
            break
        _ensure_word_foreground(session)
        send_keys("{ESC}")
        time.sleep(0.4)
        after = _snapshot(session, win, control_el, main_hwnd)
    return after


def _restore(session, win, cls, point, before, control_el, main_hwnd):
    """Symmetric restore (section 6.6). Keystrokes only re-focus if the console stole foreground."""
    ok = False
    try:
        if cls in ("dialog", "popup"):
            _clear_surfaces(session, win, control_el, main_hwnd)
        elif cls == "toggles":
            _ensure_ribbon_foreground(session)
            mouse.click(coords=point)        # re-press to restore
            time.sleep(0.3)
        elif cls == "pane":
            _ensure_ribbon_foreground(session)
            mouse.click(coords=point)        # re-press opener (Esc does not close docked panes)
            time.sleep(0.3)
        elif cls == "feature":
            _ensure_word_foreground(session)
            send_keys("^z")
            time.sleep(0.3)
        after = _snapshot(session, win, control_el, main_hwnd)
        ok = (not after.windows and not after.popups
              and after.panes_open <= before.panes_open
              and after.doc_hash == before.doc_hash)
    except Exception:
        ok = False
    return ok


def probe(session, win, journal, control_el, control_id, zone=None, split_children=None):
    # 1. boundary FIRST -- never pressed (section 6.3)
    b = config.boundary_for(control_id)
    if b:
        journal.append({"t": "boundary", "from": control_id, "kind": b.get("kind", "feature"),
                        "policy": b["policy"], "decision": b["decision"]})
        return {"class": "boundary", "ref": None, "boundary": b,
                "probe_mode": "boundary-declared", "popup_els": []}

    # 2. anti-livelock quarantine (section 6.2)
    if journal.press_attempts(control_id) >= 2 and journal.press_outcome(control_id) is None:
        journal.append({"t": "ambiguous", "control": control_id,
                        "reason": "quarantine: >=2 press-attempts without outcome"})
        return {"class": "unresolved", "ref": None, "boundary": None,
                "probe_mode": "pressed-observed", "popup_els": []}

    main_hwnd = session._hwnd()
    # defensive: a prior failed restore must not pollute this probe's baseline
    before = _snapshot(session, win, control_el, main_hwnd)
    if before.windows or before.popups:
        before = _clear_surfaces(session, win, control_el, main_hwnd)
    rect = control_el.element_info.rectangle
    point = zone_point((rect.left, rect.top, rect.right, rect.bottom), zone, split_children)

    # 3. journal press-attempted BEFORE injection (section 6.2)
    journal.append({"t": "press-attempted", "control": control_id, "zone": zone, "point": list(point)})
    _ensure_ribbon_foreground(session)
    mouse.click(coords=point)                       # injected input only (section 6.1)

    after = _observe(session, win, control_el, main_hwnd, before)
    cls = classify(before, after)

    ref = _ref_for(cls, control_id, after, before) if cls in ("dialog", "popup", "pane") else None
    if cls in ("dialog", "popup", "pane"):
        journal.append({"t": "surface-discovered", "surface": ref, "entry": control_id})
    journal.append({"t": "press-outcome", "control": control_id, "kind": cls, "ref": ref})

    reset_ok = _restore(session, win, cls, point, before, control_el, main_hwnd)
    journal.append({"t": "reset-verified", "control": control_id, "ok": reset_ok})
    if cls == "unresolved" or not reset_ok:
        journal.append({"t": "ambiguous", "control": control_id,
                        "reason": f"class={cls} reset_ok={reset_ok}"})

    return {"class": cls, "ref": ref, "boundary": None,
            "probe_mode": "pressed-observed", "popup_els": after.popup_els,
            "dialog_windows": [w for w in after.windows if w not in before.windows]}

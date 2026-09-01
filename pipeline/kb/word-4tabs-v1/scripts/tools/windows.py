"""windows — the win32 truth layer: what opened on a press, dialog vs flyout, panes.

toolbox/win32.md: a top-level window either exists or it doesn't — the most truthful signal.
Detect what a press opened via before/after window-set deltas (PID-filtered, per-action
baseline); classify by window class. Classes pinned for Word 16 (verified against the live
dump): frame=OpusApp, document child=_WwG.
"""
import sys
from pathlib import Path

import win32gui
import win32process

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts

# Pinned window classes (toolbox/win32.md, Word 16).
DIALOG_CLASSES = {"NUIDialog", "#32770", "bosa_sdm_msword", "bosa_sdm_Mso96"}
FLYOUT_CLASSES = {"NetUIHWND", "Net UI Tool Window", "MsoCommandBarPopup", "NetUITWPopupWindow"}
FRAME_CLASS = "OpusApp"
DOC_CHILD_CLASS = "_WwG"
MIN_POPUP_AREA = 10_000     # exclude tiny tooltip/screentip popups


def toplevels(pid):
    """Visible top-level windows owned by pid: list of (hwnd, class, title, rect)."""
    out = []

    def cb(h, _):
        try:
            _, wp = win32process.GetWindowThreadProcessId(h)
            if wp == pid and win32gui.IsWindowVisible(h):
                out.append((h, win32gui.GetClassName(h),
                            win32gui.GetWindowText(h), win32gui.GetWindowRect(h)))
        except Exception:
            pass
        return True

    win32gui.EnumWindows(cb, None)
    return out


def _area(rect):
    l, t, r, b = rect
    return max(0, r - l) * max(0, b - t)


def classify_window(cls, title, rect):
    """dialog | flyout | other, by class (with 'Dialog' substring + area filter for flyouts)."""
    if cls in DIALOG_CLASSES or "Dialog" in cls:
        return "dialog"
    if cls in FLYOUT_CLASSES:
        return "flyout" if _area(rect) >= MIN_POPUP_AREA else "tooltip"
    return "other"


def new_windows(pid, before):
    """Top-level windows present now but not in the `before` set. `before` = set of hwnds."""
    return [w for w in toplevels(pid) if w[0] not in before]


def snapshot_hwnds(pid):
    return {w[0] for w in toplevels(pid)}


def find_child_class(hwnd, target_class):
    """First descendant window of target_class under hwnd (EnumChildWindows recurses fully)."""
    hit = []

    def cb(c, _):
        try:
            if win32gui.GetClassName(c) == target_class:
                hit.append(c)
        except Exception:
            pass
        return True

    try:
        win32gui.EnumChildWindows(hwnd, cb, None)
    except Exception:
        pass
    return hit[0] if hit else None


def is_task_pane_window(hwnd):
    """A FLOATING task pane (e.g. the Styles pane) is a top-level window that a class check reads
    as a dialog. Distinguish it: task panes carry a 'Close pane' button; dialogs carry OK/Cancel.
    (toolbox/win32.md: floating panes need the Close-pane probe.)"""
    try:
        from pywinauto import Desktop
        w = Desktop(backend="uia").window(handle=hwnd)
        return w.child_window(title="Close pane", control_type="Button").exists(timeout=0.6)
    except Exception:
        return False


def count_docked_panes(frame_hwnd, screen_w):
    """A docked side pane insets the document child (_WwG) — left>50 or right<screen_w-60."""
    doc = find_child_class(frame_hwnd, DOC_CHILD_CLASS)
    if not doc:
        return 0, None
    l, t, r, b = win32gui.GetWindowRect(doc)
    inset = (l > 50) or (r < screen_w - 60)
    return (1 if inset else 0), (l, t, r, b)

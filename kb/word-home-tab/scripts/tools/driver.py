"""driver — activate surfaces and press controls with real, foreground input.

toolbox/input.md law: injected input goes to the FOREGROUND window, so force foreground
before every press; use REAL mouse clicks (flyouts ignore synthetic input and API activation
of an unclassified control can deadlock the UI thread); split buttons have two zones.
"""
import sys
import time
from pathlib import Path

import win32gui
from pywinauto import mouse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
from session import force_foreground
import uia_attach as ua


def ensure_frame_foreground(frame_hwnd):
    """Force the main frame foreground — use only when about to click the command surface.
    While a modal dialog is up use ensure_no_foreign_foreground instead (see input.md)."""
    force_foreground(frame_hwnd)
    time.sleep(0.05)


def ensure_no_foreign_foreground(pid):
    """Refocus ONLY if another process stole foreground (dialog up): forcing the main frame
    would send ESC to the disabled frame instead of the dialog."""
    import win32process
    fg = win32gui.GetForegroundWindow()
    try:
        _, wp = win32process.GetWindowThreadProcessId(fg)
    except Exception:
        wp = None
    return wp == pid


def _center(rect):
    l, t, r, b = rect
    return (l + r) // 2, (t + b) // 2


def click_rect(rect, settle=0.15):
    x, y = _center(rect)
    mouse.click(coords=(x, y))
    time.sleep(settle)
    return (x, y)


def click_point(x, y, settle=0.15):
    mouse.click(coords=(int(x), int(y)))
    time.sleep(settle)
    return (int(x), int(y))


def move_park(x, y):
    """Park the cursor (e.g. on a popup's top border) and settle before hovering — the first
    hover of a sequence intermittently misses without this."""
    mouse.move(coords=(int(x), int(y)))
    time.sleep(0.35)


def split_zone_rects(split_el):
    """A SplitButton exposes a primary Button and a '*_Dropdown' MenuItem as children with their
    own rects — prefer those over guessing a fraction of the parent (toolbox/uia.md)."""
    primary = dropdown = None
    try:
        for k in split_el.children():
            ei = k.element_info
            r = ei.rectangle
            rect = (r.left, r.top, r.right, r.bottom)
            aid = (ei.automation_id or "")
            if aid.endswith("_Dropdown") or ei.control_type == "MenuItem":
                dropdown = rect
            elif ei.control_type == "Button":
                primary = rect
    except Exception:
        pass
    return primary, dropdown


def zone_point(rect, zone="primary", orientation="horizontal"):
    """Fallback zone point by fraction of the parent rect when child zones aren't available."""
    l, t, r, b = rect
    if zone == "dropdown":
        if orientation == "horizontal":
            return (l + int((r - l) * 0.82), (t + b) // 2)
        return ((l + r) // 2, t + int((b - t) * 0.75))
    return (l + int((r - l) * 0.30), (t + b) // 2)


def send_keys(keys):
    """Keyboard injection to the foreground window (e.g. ESC to close a flyout)."""
    from pywinauto import keyboard
    keyboard.send_keys(keys)
    time.sleep(0.1)


def press_escape(n=1):
    for _ in range(n):
        send_keys("{ESC}")
        time.sleep(0.15)

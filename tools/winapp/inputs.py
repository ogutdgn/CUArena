import time
import pywintypes
import win32gui
from pywinauto import mouse
from pywinauto.keyboard import send_keys


def _try_set_foreground(hwnd: int) -> None:
    # Windows' anti-focus-stealing heuristic can refuse a focus handoff two
    # ways: silently (GetForegroundWindow still doesn't match afterwards --
    # the case this function originally handled) or by raising
    # pywintypes.error "No error message is available" from
    # SetForegroundWindow itself (observed live: another window had focus
    # when a probe's ensure_foreground ran a few hundred ms after launch).
    # Both are the same refusal; swallow the raise so the existing
    # post-call GetForegroundWindow check drives the ALT-nudge/raise
    # fallback below instead of an uncaught exception aborting the probe.
    try:
        win32gui.SetForegroundWindow(hwnd)
    except pywintypes.error:
        pass


def ensure_foreground(hwnd: int) -> None:
    if win32gui.GetForegroundWindow() != hwnd:
        _try_set_foreground(hwnd)
        time.sleep(0.2)
    if win32gui.GetForegroundWindow() != hwnd:
        # Windows can refuse a focus handoff outright (anti-focus-stealing
        # heuristic). A synthetic ALT keypress before retrying
        # SetForegroundWindow is a well-known, generic Windows technique to
        # work around this -- not app-specific, so it belongs here rather
        # than in a caller.
        send_keys("%")
        _try_set_foreground(hwnd)
        time.sleep(0.2)
    if win32gui.GetForegroundWindow() != hwnd:
        raise RuntimeError(f"could not bring hwnd {hwnd} to foreground; clicks would drop silently")


def _center(rect):
    l, t, r, b = rect
    return ((l + r) // 2, (t + b) // 2)


def click_rect(rect) -> None:
    mouse.click(button="left", coords=_center(rect))


def hover_rect(rect) -> None:
    mouse.move(coords=_center(rect))


def press(keys: str) -> None:
    send_keys(keys, pause=0.05)

import time
import win32gui
from pywinauto import mouse
from pywinauto.keyboard import send_keys


def ensure_foreground(hwnd: int) -> None:
    if win32gui.GetForegroundWindow() != hwnd:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    if win32gui.GetForegroundWindow() != hwnd:
        # Windows can refuse a focus handoff outright (anti-focus-stealing
        # heuristic). A synthetic ALT keypress before retrying
        # SetForegroundWindow is a well-known, generic Windows technique to
        # work around this -- not app-specific, so it belongs here rather
        # than in a caller.
        send_keys("%")
        win32gui.SetForegroundWindow(hwnd)
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

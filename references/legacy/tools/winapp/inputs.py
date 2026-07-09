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


def type_text(text: str) -> None:
    # with_spaces=True: send_keys treats a bare space as a no-op key-name
    # separator by default, which silently drops spaces from literal text.
    # with_newlines=True similarly makes embedded "\n" send {ENTER} instead
    # of being dropped. Braces/other send_keys metacharacters in `text` are
    # NOT escaped here -- type_text is for literal prose entry, not for
    # driving key chords (that's press()); callers who need to type
    # characters that collide with send_keys syntax should escape before
    # calling.
    send_keys(text, pause=0.02, with_spaces=True, with_newlines=True)


def scroll(coords, wheel_dist: int) -> None:
    mouse.scroll(coords=coords, wheel_dist=wheel_dist)

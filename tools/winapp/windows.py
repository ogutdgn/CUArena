import time
from dataclasses import dataclass
import win32gui

@dataclass(frozen=True)
class WinInfo:
    hwnd: int
    title: str
    cls: str

def top_windows() -> list[WinInfo]:
    out: list[WinInfo] = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            out.append(WinInfo(hwnd, win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd)))
        return True
    win32gui.EnumWindows(cb, None)
    return out

def wait_new_window(before: list[WinInfo], timeout: float = 2.5, poll: float = 0.3) -> WinInfo | None:
    seen = {w.hwnd for w in before}
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:           # poll — one-shot detection is racy (spec reference lesson)
        for w in top_windows():
            if w.hwnd not in seen:
                return w
        time.sleep(poll)
    return None

def classify(cls: str, dialog_classes: list[str], flyout_classes: list[str]) -> str:
    if cls in dialog_classes:
        return "dialog"
    if cls in flyout_classes:
        return "flyout"
    return "unknown"

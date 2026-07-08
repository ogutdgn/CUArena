import time
import win32con, win32gui, win32process
import subprocess
from tools.models import JournalEvent

def _window_alive(hwnd: int) -> bool:
    return bool(win32gui.IsWindow(hwnd)) and bool(win32gui.IsWindowVisible(hwnd))

def _kill_by_hwnd_pid(hwnd: int) -> None:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)

def close_app(session, journal) -> None:
    hwnd = session.hwnd
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    deadline = time.monotonic() + 3.0
    alive = _window_alive(hwnd)
    while time.monotonic() < deadline and alive:
        time.sleep(0.3)
        alive = _window_alive(hwnd)
    if alive:
        _kill_by_hwnd_pid(hwnd)
        journal.append(JournalEvent(actor="teardown", action="close", target=session.config.name, outcome="killed"))
    else:
        journal.append(JournalEvent(actor="teardown", action="close", target=session.config.name, outcome="closed"))

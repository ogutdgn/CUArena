import re
import time
import win32con, win32gui, win32process
import subprocess
from tools.models import JournalEvent
from tools.winapp.uia import ElemInfo, UIASession
from tools.winapp.windows import top_windows
from tools.winapp import inputs

DESTRUCTIVE_RES = [r"(?i)^save$", r"(?i)^send\b", r"(?i)^delete\b",
                   r"(?i)buy|purchase", r"(?i)^share\b", r"(?i)^print\b"]
DISCARD_RES = [r"(?i)don'?t save", r"(?i)^no$"]

def _window_alive(hwnd: int) -> bool:
    return bool(win32gui.IsWindow(hwnd)) and bool(win32gui.IsWindowVisible(hwnd))

def _kill_by_hwnd_pid(hwnd: int) -> None:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)

def find_discard_target(elements: list[ElemInfo], extra_res: list[str]) -> ElemInfo | None:
    for pat in DISCARD_RES + list(extra_res):
        for e in elements:
            if e.name.strip() and re.search(pat, e.name):
                return e
    return None

def _try_discard_dialog(before_close: list, cfg, journal) -> bool:
    # a confirmation dialog is a NEW window (vs pre-close snapshot) of a dialog class
    for w in top_windows():
        if w.hwnd in {b.hwnd for b in before_close}:
            continue
        try:
            popup = UIASession.attach_by_handle(w.hwnd)
            els = [k for k in popup.children(depth=4) if k.name.strip()]
        except Exception:
            continue
        target = find_discard_target(els, cfg.discard_label_res)
        if target is not None:
            inputs.ensure_foreground(w.hwnd)
            inputs.click_rect(target.rect)
            journal.append(JournalEvent(actor="teardown", action="close", target=w.title or w.cls,
                                        outcome="discarded", data={"button": target.name}))
            return True
    return False

def close_app(session, journal) -> None:
    hwnd = session.hwnd
    before_close = top_windows()
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    deadline = time.monotonic() + 3.0
    alive = _window_alive(hwnd)
    while time.monotonic() < deadline and alive:
        time.sleep(0.3)
        alive = _window_alive(hwnd)
    if alive:
        if _try_discard_dialog(before_close, session.config, journal):
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

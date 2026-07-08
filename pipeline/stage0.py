import json, re, shutil, subprocess, time
from dataclasses import dataclass
from pathlib import Path
import win32api
from pipeline.config import AppConfig
from tools.journal import Journal
from tools.models import JournalEvent
from tools.winapp.uia import UIASession
from tools.winapp.windows import top_windows, wait_new_window
from tools.winapp import inputs

class VersionDriftError(RuntimeError):
    pass

def file_version(exe_path: str) -> str:
    path = shutil.which(exe_path) or exe_path
    info = win32api.GetFileVersionInfo(path, "\\")
    ms, ls = info["FileVersionMS"], info["FileVersionLS"]
    return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"

def assert_version(kb_app_json: Path, session_version: str) -> None:
    if not Path(kb_app_json).exists():
        return
    prior = json.loads(Path(kb_app_json).read_text(encoding="utf-8"))["version"]
    if prior != session_version:
        raise VersionDriftError(f"KB was built on {prior}, app is now {session_version} — refusing to mix")

@dataclass
class AppSession:
    config: AppConfig
    ui: UIASession
    hwnd: int
    pid: int
    version: str

def launch(cfg: AppConfig, journal: Journal) -> AppSession:
    before = top_windows()
    proc = subprocess.Popen([cfg.exe])
    win = wait_new_window(before, timeout=15.0)
    if win is None:
        journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name, outcome="failed: no window"))
        raise RuntimeError(f"{cfg.name}: no window appeared")
    time.sleep(1.0)
    # Some app builds (observed: Windows 11 modern Notepad) restore a
    # leftover window from a prior unsaved session alongside the freshly
    # launched one; both satisfy the same locale-tolerant window_title_re, so
    # a broad desktop-wide UIA lookup by that pattern can be ambiguous
    # (ElementAmbiguousError). wait_new_window already identified the one
    # hwnd we actually launched -- re-read its current title (the title seen
    # during the new-window race can be a mid-render transient) and, if it
    # differs from any other window matching window_title_re, attach on that
    # exact literal string instead of the broad pattern. Falls back to the
    # configured pattern when titles aren't unique enough to help (e.g. two
    # windows share literally the same title), which is app-agnostic --
    # driven only by cfg + window data launch() already has.
    snapshot = top_windows()
    current = next((w for w in snapshot if w.hwnd == win.hwnd), win)
    others = [w for w in snapshot
              if w.hwnd != win.hwnd and re.match(cfg.window_title_re, w.title or "")]
    target_re = cfg.window_title_re
    if current.title and not any(w.title == current.title for w in others):
        target_re = re.escape(current.title)
    ui = UIASession.attach(target_re)
    for pattern in cfg.boundaries.dismiss_title_res:      # dismiss nags BEFORE anything else
        for w in top_windows():
            if re.match(pattern, w.title or ""):
                inputs.ensure_foreground(w.hwnd)
                inputs.press("{ESC}")
                journal.append(JournalEvent(actor="stage0", action="boundary", target=w.title, outcome="dismissed"))
    version = file_version(cfg.exe)
    journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name,
                                outcome="ok", data={"version": version, "pid": proc.pid}))
    return AppSession(config=cfg, ui=ui, hwnd=ui._win.handle, pid=proc.pid, version=version)

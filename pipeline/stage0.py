import json, re, shutil, subprocess, time
from dataclasses import dataclass
from pathlib import Path
import win32api
from pipeline.config import AppConfig
from tools.journal import Journal
from tools.models import JournalEvent
from tools.winapp.uia import UIASession
from tools.winapp.windows import top_windows, wait_new_window, window_process_path
from tools.winapp import inputs

class VersionDriftError(RuntimeError):
    pass

def build_argv(cfg: AppConfig) -> list[str]:
    """Pure helper: [cfg.exe] + cfg.launch_args, with any "{fixture}" placeholder
    replaced by the absolute path of cfg.fixture (resolved relative to the
    current working directory, i.e. the repo root when invoked normally).
    Raises ValueError if "{fixture}" is used but cfg.fixture is None or the
    resolved file does not exist."""
    argv = [cfg.exe]
    for arg in cfg.launch_args:
        if "{fixture}" in arg:
            if not cfg.fixture:
                raise ValueError(
                    f"{cfg.name}: launch_args uses \"{{fixture}}\" but no fixture is configured")
            fixture_path = Path(cfg.fixture).resolve()
            if not fixture_path.exists():
                raise ValueError(f"{cfg.name}: fixture not found: {fixture_path}")
            arg = arg.replace("{fixture}", str(fixture_path))
        argv.append(arg)
    return argv

def file_version(exe_path: str) -> str:
    path = shutil.which(exe_path) or exe_path
    info = win32api.GetFileVersionInfo(path, "\\")
    ms, ls = info["FileVersionMS"], info["FileVersionLS"]
    return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"

def assert_version(kb_app_json: Path, session_version: str, kb_version_json: Path | None = None) -> None:
    # version.json is written after every successful launch (agent-independent),
    # so it is checked first; app.json only exists after a full agent run, so it
    # is the fallback for KBs produced before version.json existed. No prior
    # record of either -> first run, nothing to drift from.
    if kb_version_json is not None and Path(kb_version_json).exists():
        prior = json.loads(Path(kb_version_json).read_text(encoding="utf-8"))["version"]
    elif Path(kb_app_json).exists():
        prior = json.loads(Path(kb_app_json).read_text(encoding="utf-8"))["version"]
    else:
        return
    if prior != session_version:
        raise VersionDriftError(f"KB was built on {prior}, app is now {session_version} — refusing to mix")

def resolve_session_version(hwnd: int, exe: str, journal) -> str:
    # A store-app's launcher stub (cfg.exe) is not the running binary; the
    # attached window's owning process is. Prefer it; fall back loudly.
    try:
        return file_version(window_process_path(hwnd))
    except Exception:
        if journal is not None:
            journal.append(JournalEvent(actor="stage0", action="version", target=exe,
                                        outcome="version-fallback"))
        return file_version(exe)

@dataclass
class AppSession:
    config: AppConfig
    ui: UIASession
    hwnd: int
    pid: int
    version: str

def launch(cfg: AppConfig, journal: Journal) -> AppSession:
    before = top_windows()
    proc = subprocess.Popen(build_argv(cfg))
    win = wait_new_window(before, timeout=15.0)
    if win is None:
        journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name, outcome="failed: no window"))
        raise RuntimeError(f"{cfg.name}: no window appeared")
    time.sleep(1.0)
    # Some app builds (observed on Win11 store-app rewrites) restore a
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
    # Never rebind attach to a foreign window: the exact-title shortcut is only
    # safe when that title still identifies our launched window as belonging to
    # this app (i.e. it also satisfies the configured pattern). If it doesn't,
    # fall back to the configured regex rather than attaching on an untrusted
    # literal string.
    if (current.title and not any(w.title == current.title for w in others)
            and re.match(cfg.window_title_re, current.title)):
        target_re = re.escape(current.title)
    ui = UIASession.attach(target_re)
    for pattern in cfg.boundaries.dismiss_title_res:      # dismiss nags BEFORE anything else
        for w in top_windows():
            if re.match(pattern, w.title or ""):
                inputs.ensure_foreground(w.hwnd)
                inputs.press("{ESC}")
                deadline = time.monotonic() + 1.5
                while time.monotonic() < deadline and any(w2.hwnd == w.hwnd for w2 in top_windows()):
                    time.sleep(0.3)
                still_present = any(w2.hwnd == w.hwnd for w2 in top_windows())
                if still_present:
                    journal.append(JournalEvent(actor="stage0", action="boundary", target=w.title,
                                                outcome="failed: still-present"))
                else:
                    journal.append(JournalEvent(actor="stage0", action="boundary", target=w.title,
                                                outcome="dismissed"))
    version = resolve_session_version(ui._win.handle, cfg.exe, journal)
    journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name,
                                outcome="ok", data={"version": version, "pid": proc.pid}))
    return AppSession(config=cfg, ui=ui, hwnd=ui._win.handle, pid=proc.pid, version=version)

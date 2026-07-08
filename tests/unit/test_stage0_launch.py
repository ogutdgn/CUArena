"""Unit tests for pipeline.stage0.launch() boundary-dismissal honesty (FIX 3)
and the exact-title rebind guard (FIX 4). All OS-facing calls are mocked so
these run without a real window."""
from pathlib import Path

import pytest

from pipeline import stage0
from pipeline.config import AppConfig, Boundaries
from tools.journal import Journal
from tools.winapp.windows import WinInfo


def _cfg(window_title_re="Notepad", dismiss_title_res=()):
    return AppConfig(name="notepad", exe="notepad.exe", window_title_re=window_title_re,
                      boundaries=Boundaries(dismiss_title_res=list(dismiss_title_res)))


class FakeProc:
    pid = 1234


@pytest.fixture(autouse=True)
def _patch_common(monkeypatch):
    monkeypatch.setattr(stage0.subprocess, "Popen", lambda args: FakeProc())
    monkeypatch.setattr(stage0.time, "sleep", lambda s: None)
    monkeypatch.setattr(stage0, "file_version", lambda exe: "1.2.3")


def _finalize_ui_attach(monkeypatch, hwnd=999):
    class FakeWin:
        handle = hwnd
    def attach(cls, title_re):
        inst = cls.__new__(cls)
        inst._win = FakeWin()
        return inst
    monkeypatch.setattr(stage0.UIASession, "attach", classmethod(attach))


def test_dismissal_journals_dismissed_when_window_gone(tmp_path, monkeypatch):
    _finalize_ui_attach(monkeypatch)
    win = WinInfo(hwnd=1, title="Notepad", cls="Notepad")
    nag = WinInfo(hwnd=2, title="Nag", cls="#32770")

    calls = {"n": 0}
    def fake_top_windows():
        calls["n"] += 1
        if calls["n"] <= 3:
            return [win, nag]     # present through wait_new_window + snapshot + pre-ESC poll
        return [win]              # gone after ESC
    monkeypatch.setattr(stage0, "top_windows", fake_top_windows)
    monkeypatch.setattr(stage0, "wait_new_window", lambda before, timeout=15.0: win)
    monkeypatch.setattr(stage0.inputs, "ensure_foreground", lambda hwnd: None)
    monkeypatch.setattr(stage0.inputs, "press", lambda keys: None)

    cfg = _cfg(dismiss_title_res=["Nag"])
    journal = Journal(tmp_path / "journal.jsonl", run_id="t")
    stage0.launch(cfg, journal)

    events = Journal.read_all(tmp_path / "journal.jsonl")
    boundary_events = [e for e in events if e.action == "boundary"]
    assert len(boundary_events) == 1
    assert boundary_events[0].outcome == "dismissed"


def test_dismissal_journals_failed_when_window_still_present(tmp_path, monkeypatch):
    _finalize_ui_attach(monkeypatch)
    win = WinInfo(hwnd=1, title="Notepad", cls="Notepad")
    nag = WinInfo(hwnd=2, title="Nag", cls="#32770")

    # Nag window never disappears, no matter how many times we poll.
    monkeypatch.setattr(stage0, "top_windows", lambda: [win, nag])
    monkeypatch.setattr(stage0, "wait_new_window", lambda before, timeout=15.0: win)
    monkeypatch.setattr(stage0.inputs, "ensure_foreground", lambda hwnd: None)
    monkeypatch.setattr(stage0.inputs, "press", lambda keys: None)

    cfg = _cfg(dismiss_title_res=["Nag"])
    journal = Journal(tmp_path / "journal.jsonl", run_id="t")
    # Should not raise -- failed dismissal is journaled, not fatal.
    stage0.launch(cfg, journal)

    events = Journal.read_all(tmp_path / "journal.jsonl")
    boundary_events = [e for e in events if e.action == "boundary"]
    assert len(boundary_events) == 1
    assert boundary_events[0].outcome == "failed: still-present"


def test_attach_guard_uses_exact_title_when_it_matches_pattern(tmp_path, monkeypatch):
    captured = {}
    def attach(cls, title_re):
        captured["title_re"] = title_re
        inst = cls.__new__(cls)
        class FakeWin:
            handle = 999
        inst._win = FakeWin()
        return inst
    monkeypatch.setattr(stage0.UIASession, "attach", classmethod(attach))

    win = WinInfo(hwnd=1, title="Notepad - untitled", cls="Notepad")
    monkeypatch.setattr(stage0, "top_windows", lambda: [win])
    monkeypatch.setattr(stage0, "wait_new_window", lambda before, timeout=15.0: win)

    cfg = _cfg(window_title_re="Notepad.*")
    journal = Journal(tmp_path / "journal.jsonl", run_id="t")
    stage0.launch(cfg, journal)

    import re
    assert captured["title_re"] == re.escape("Notepad - untitled")


def test_attach_guard_falls_back_when_exact_title_does_not_match_pattern(tmp_path, monkeypatch):
    captured = {}
    def attach(cls, title_re):
        captured["title_re"] = title_re
        inst = cls.__new__(cls)
        class FakeWin:
            handle = 999
        inst._win = FakeWin()
        return inst
    monkeypatch.setattr(stage0.UIASession, "attach", classmethod(attach))

    # current.title diverges from the configured pattern entirely (e.g. a
    # foreign/unrelated window somehow ended up as "current") -- must NOT
    # attach on that literal title; must fall back to the configured regex.
    win = WinInfo(hwnd=1, title="Some Other App", cls="Notepad")
    monkeypatch.setattr(stage0, "top_windows", lambda: [win])
    monkeypatch.setattr(stage0, "wait_new_window", lambda before, timeout=15.0: win)

    cfg = _cfg(window_title_re="Notepad.*")
    journal = Journal(tmp_path / "journal.jsonl", run_id="t")
    stage0.launch(cfg, journal)

    assert captured["title_re"] == "Notepad.*"

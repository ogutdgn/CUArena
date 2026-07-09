from dataclasses import dataclass
from pathlib import Path
from PIL import Image

from pipeline.config import AppConfig, Boundaries
from pipeline.stage1_surface import scan_surface
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.winapp.uia import ElemInfo

WIN = ElemInfo("Window", "Notepad", (0, 0, 800, 600), "")


class FakeUI:
    def __init__(self, children):
        self._children = children

    def info(self):
        return WIN

    def children(self, depth=1):
        return self._children


@dataclass
class FakeSession:
    config: AppConfig
    ui: FakeUI
    hwnd: int = 1


def _config(exclude_labels=()):
    return AppConfig(name="notepad", exe="notepad.exe", window_title_re="Notepad",
                      boundaries=Boundaries(exclude_labels=list(exclude_labels)))


def _patch_capture(monkeypatch):
    monkeypatch.setattr("pipeline.stage1_surface.capture.grab_window",
                         lambda hwnd: (Image.new("RGB", (2, 2)), "print-window"))


def test_scan_surface_journals_skipped_excluded(tmp_path: Path, monkeypatch):
    _patch_capture(monkeypatch)
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("MenuItem", "Ads", (40, 0, 80, 20), "")]
    session = FakeSession(config=_config(exclude_labels=("Ads",)), ui=FakeUI(kids))
    journal_path = tmp_path / "journal.jsonl"
    journal = Journal(journal_path, run_id="t")
    writer = KBWriter(tmp_path, "notepad")

    paths = scan_surface(session, writer, journal)

    import json
    data = json.loads(paths[0].read_text(encoding="utf-8"))
    assert [e["label"] for e in data["children"]] == ["File"]   # excluded element absent

    events = Journal.read_all(journal_path)
    skip_events = [e for e in events if e.outcome == "skipped-excluded"]
    assert len(skip_events) == 1
    assert skip_events[0].data["count"] == 1
    assert skip_events[0].data["labels"] == ["Ads"]


def test_scan_surface_uses_grab_window_and_journals_capture_method(tmp_path: Path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        "pipeline.stage1_surface.capture.grab_window",
        lambda hwnd: (calls.append(hwnd), (Image.new("RGB", (2, 2)), "foreground-fallback"))[1],
    )
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), "")]
    session = FakeSession(config=_config(), ui=FakeUI(kids), hwnd=42)
    journal_path = tmp_path / "journal.jsonl"
    journal = Journal(journal_path, run_id="t")
    writer = KBWriter(tmp_path, "notepad")

    scan_surface(session, writer, journal)

    assert calls == [42]  # captured the window itself, not a screen region
    events = Journal.read_all(journal_path)
    scan_event = next(e for e in events if e.outcome == "ok")
    assert scan_event.data["capture_method"] == "foreground-fallback"


def test_scan_surface_no_excluded_labels_no_skip_event(tmp_path: Path, monkeypatch):
    _patch_capture(monkeypatch)
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), "")]
    session = FakeSession(config=_config(), ui=FakeUI(kids))
    journal_path = tmp_path / "journal.jsonl"
    journal = Journal(journal_path, run_id="t")
    writer = KBWriter(tmp_path, "notepad")

    scan_surface(session, writer, journal)

    events = Journal.read_all(journal_path)
    assert not [e for e in events if e.outcome == "skipped-excluded"]

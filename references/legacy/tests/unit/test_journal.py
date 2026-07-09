from pathlib import Path
from tools.journal import Journal
from tools.models import JournalEvent

def test_append_stamps_and_persists(tmp_path: Path):
    p = tmp_path / "journal.jsonl"
    j = Journal(p, run_id="run-001")
    e = j.append(JournalEvent(actor="stage0", action="launch", target="notepad", outcome="ok"))
    assert e.ts and e.run_id == "run-001"
    j.append(JournalEvent(actor="stage1.surface", action="scan-container", target="ui:main-window"))
    events = Journal.read_all(p)
    assert [ev.action for ev in events] == ["launch", "scan-container"]

def test_append_is_append_only(tmp_path: Path):
    p = tmp_path / "journal.jsonl"
    Journal(p, run_id="a").append(JournalEvent(actor="x", action="one"))
    Journal(p, run_id="b").append(JournalEvent(actor="x", action="two"))  # reopening never truncates
    assert [e.run_id for e in Journal.read_all(p)] == ["a", "b"]

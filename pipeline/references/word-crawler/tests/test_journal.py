import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from journal import Journal
from frontier import Frontier


def test_quarantine_and_frontier(tmp_path):
    j = Journal(tmp_path / "j.jsonl")
    j.append({"t": "press-attempted", "control": "ribbon.home.font.bold"})
    assert j.press_attempts("ribbon.home.font.bold") == 1
    assert j.press_outcome("ribbon.home.font.bold") is None
    j.append({"t": "press-outcome", "control": "ribbon.home.font.bold", "kind": "toggles"})
    assert j.press_outcome("ribbon.home.font.bold")["kind"] == "toggles"

    j.append({"t": "surface-discovered", "surface": "dialogs/font", "entry": "ribbon.home.font.launcher"})
    f = Frontier.from_journal(j)
    assert f.pending() == ["dialogs/font"] and not f.is_done()
    j.append({"t": "surface-captured", "surface": "dialogs/font", "payload": {}})
    assert Frontier.from_journal(j).is_done()


def test_replay_is_idempotent(tmp_path):
    p = tmp_path / "j.jsonl"
    j = Journal(p); j.append({"t": "boundary", "from": "ribbon.file"})
    j2 = Journal(p)
    assert j2.records()[-1]["t"] == "boundary"
    assert j2.records()[-1]["schema_version"] == 1

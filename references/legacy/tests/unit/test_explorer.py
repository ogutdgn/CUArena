import json
from pathlib import Path
from unittest.mock import patch
from pipeline.explorer import (
    SURVEY_MISSION, ITEM_MISSION, run_explorer, run_survey, run_item, replay_route,
)
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent


def test_survey_mission_contains_load_bearing_rules():
    for phrase in ("record_route", "write_worklist", "DONE"):
        assert phrase in SURVEY_MISSION

def test_item_mission_contains_load_bearing_rules():
    for phrase in ("VERIFY", "do NOT write", "write_container", "unexplored",
                   "probe", "Never", "DONE", "note_progress"):
        assert phrase in ITEM_MISSION


# --- run_survey --------------------------------------------------------

def test_run_survey_reads_back_worklist_written_by_agent(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    kb_app_root = tmp_path / "x"

    def fake_agent(briefing, tools, max_turns):
        worklist_path = kb_app_root / "scripts" / "worklist.json"
        worklist_path.parent.mkdir(parents=True, exist_ok=True)
        worklist_path.write_text(json.dumps(
            [{"surface": "Home tab", "how": "click Home"}]), encoding="utf-8")
        return "DONE wrote 1 item"

    with patch("pipeline.explorer.run_explorer_agent", side_effect=fake_agent):
        worklist = run_survey(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                              kb_app_root=kb_app_root, cfg=None, verbose=False)
    assert worklist == [{"surface": "Home tab", "how": "click Home"}]
    ev = Journal.read_all(j.path)[-1]
    assert ev.actor == "explorer" and ev.action == "survey" and ev.outcome == "done"

def test_run_survey_returns_none_when_agent_writes_no_worklist(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="DONE but forgot"):
        worklist = run_survey(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                              kb_app_root=tmp_path / "x", cfg=None, verbose=False)
    assert worklist is None
    ev = Journal.read_all(j.path)[-1]
    assert "failed" in ev.outcome


# --- run_item ------------------------------------------------------------

def test_run_item_ok_when_agent_writes_container(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")

    def fake_agent(briefing, tools, max_turns):
        assert "Home tab" in briefing and "click Home" in briefing
        j.append(JournalEvent(actor="explorer.write_container", action="write_container",
                              target="ui:tab-home", outcome="ok"))
        return "DONE wrote ui:tab-home"

    with patch("pipeline.explorer.run_explorer_agent", side_effect=fake_agent):
        outcome = run_item(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                           kb_app_root=tmp_path / "x", cfg=None,
                           item={"surface": "Home tab", "how": "click Home"},
                           index=1, total=1, verbose=False)
    assert outcome == "ok"
    ev = Journal.read_all(j.path)[-1]
    assert ev.actor == "explorer" and ev.action == "item" and ev.target == "Home tab"
    assert ev.outcome == "ok" and ev.data["container"] == "ui:tab-home"

def test_run_item_failed_when_agent_never_writes_container(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")

    def fake_agent(briefing, tools, max_turns):
        j.append(JournalEvent(actor="explorer.note", action="note", outcome="progress",
                              data={"text": "could not verify the tab switched"}))
        return "DONE could not verify"

    with patch("pipeline.explorer.run_explorer_agent", side_effect=fake_agent):
        outcome = run_item(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                           kb_app_root=tmp_path / "x", cfg=None,
                           item={"surface": "Weird tab", "how": "click Weird"},
                           index=2, total=5, verbose=False)
    assert outcome == "failed"
    ev = Journal.read_all(j.path)[-1]
    assert ev.outcome == "failed"

def test_run_item_only_looks_at_events_from_its_own_run(tmp_path: Path):
    # A write_container ok event from an EARLIER item must not leak into a
    # later item's outcome -- only journal events appended during this
    # item's own run_explorer_agent call should count.
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    j.append(JournalEvent(actor="explorer.write_container", action="write_container",
                          target="ui:tab-earlier", outcome="ok"))

    with patch("pipeline.explorer.run_explorer_agent", return_value="DONE nothing written"):
        outcome = run_item(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                           kb_app_root=tmp_path / "x", cfg=None,
                           item={"surface": "Later tab", "how": "click Later"},
                           index=1, total=1, verbose=False)
    assert outcome == "failed"


# --- run_explorer: full orchestration -----------------------------------

def test_run_explorer_orchestrates_survey_then_items(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    kb_app_root = tmp_path / "x"
    writer = KBWriter(tmp_path, "x")
    calls = []

    def fake_agent(briefing, tools, max_turns):
        calls.append(briefing)
        if briefing.startswith("You are surveying"):
            worklist_path = kb_app_root / "scripts" / "worklist.json"
            worklist_path.parent.mkdir(parents=True, exist_ok=True)
            worklist_path.write_text(json.dumps([
                {"surface": "Home tab", "how": "click Home"},
                {"surface": "Insert tab", "how": "click Insert"},
            ]), encoding="utf-8")
            return "DONE wrote 2 items"
        # item run: Home succeeds, Insert doesn't
        if "Home tab" in briefing:
            j.append(JournalEvent(actor="explorer.write_container", action="write_container",
                                  target="ui:tab-home", outcome="ok"))
            return "DONE wrote ui:tab-home"
        return "DONE could not verify Insert"

    with patch("pipeline.explorer.run_explorer_agent", side_effect=fake_agent):
        summary = run_explorer(session=None, writer=writer, journal=j,
                               kb_app_root=kb_app_root, cfg=None, verbose=False)

    assert len(calls) == 3  # 1 survey + 2 items
    assert "DONE" in summary and "1/2" in summary and "Insert tab" in summary

    events = Journal.read_all(j.path)
    item_events = [e for e in events if e.actor == "explorer" and e.action == "item"]
    assert len(item_events) == 2
    assert item_events[0].target == "Home tab" and item_events[0].outcome == "ok"
    assert item_events[1].target == "Insert tab" and item_events[1].outcome == "failed"

    mission_events = [e for e in events if e.actor == "explorer" and e.action == "mission"]
    assert mission_events[-1].outcome == "done"
    assert mission_events[-1].data["done"] == ["Home tab"]
    assert mission_events[-1].data["failed"] == ["Insert tab"]

def test_run_explorer_fails_fast_when_survey_produces_no_worklist(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="DONE but forgot worklist"):
        summary = run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                               kb_app_root=tmp_path / "x", cfg=None, verbose=False)
    assert "FAILED" in summary
    ev = Journal.read_all(j.path)[-1]
    assert ev.action == "mission" and "failed" in ev.outcome

def test_run_explorer_verbose_prints_progress(tmp_path: Path, capsys):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    kb_app_root = tmp_path / "x"

    def fake_agent(briefing, tools, max_turns):
        if briefing.startswith("You are surveying"):
            worklist_path = kb_app_root / "scripts" / "worklist.json"
            worklist_path.parent.mkdir(parents=True, exist_ok=True)
            worklist_path.write_text(json.dumps(
                [{"surface": "Home tab", "how": "click Home"}]), encoding="utf-8")
            return "DONE"
        return "DONE nothing written"

    with patch("pipeline.explorer.run_explorer_agent", side_effect=fake_agent):
        run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                     kb_app_root=kb_app_root, cfg=None, verbose=True)
    out = capsys.readouterr().out
    assert "[explorer] survey ->" in out
    assert "[explorer] item 1/1 Home tab -> failed" in out
    assert "[explorer] DONE" in out


# --- replay_route (unchanged) -----------------------------------------

class FakeElem:
    def __init__(self, name, rect=(0, 0, 10, 10)):
        self.name = name
        self.rect = rect

class FakeUI:
    def __init__(self, elements):
        self._elements = elements
    def children(self, depth=1):
        return self._elements

class FakeSession:
    def __init__(self, elements, hwnd=1):
        self.ui = FakeUI(elements)
        self.hwnd = hwnd

def test_replay_route_clicks_matching_step(tmp_path):
    session = FakeSession([FakeElem("New Blank Document"), FakeElem("Other")])
    route_path = tmp_path / "route.json"
    route_path.write_text('[{"click_label_re": "(?i)new blank"}]', encoding="utf-8")
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.inputs") as fake_inputs, patch("pipeline.explorer.time.sleep"):
        replay_route(session, route_path, j)
    fake_inputs.ensure_foreground.assert_called_once_with(1)
    fake_inputs.click_rect.assert_called_once_with((0, 0, 10, 10))
    ev = Journal.read_all(j.path)[-1]
    assert ev.actor == "ready" and ev.action == "replay" and ev.outcome == "ok"

def test_replay_route_missing_element_raises_and_journals_failed(tmp_path):
    session = FakeSession([FakeElem("Other")])
    route_path = tmp_path / "route.json"
    route_path.write_text('[{"click_label_re": "(?i)new blank"}]', encoding="utf-8")
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.inputs"), patch("pipeline.explorer.time.sleep"):
        try:
            replay_route(session, route_path, j)
            assert False, "expected RuntimeError"
        except RuntimeError:
            pass
    ev = Journal.read_all(j.path)[-1]
    assert "failed: route-step" in ev.outcome

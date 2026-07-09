from pathlib import Path
from unittest.mock import patch
from pipeline.explorer import B1_MISSION, run_explorer, replay_route
from tools.journal import Journal
from tools.kb_writer import KBWriter

def test_mission_contains_load_bearing_rules():
    for phrase in ("record_route", "write_container", "unexplored", "probe",
                   "Never", "DONE"):
        assert phrase in B1_MISSION

def test_run_explorer_journals_done(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="DONE covered main window"):
        out = run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                           kb_app_root=tmp_path / "x", cfg=None)
    assert out.startswith("DONE")
    ev = Journal.read_all(tmp_path / "j.jsonl")[-1]
    assert ev.actor == "explorer" and ev.outcome == "done"

def test_run_explorer_journals_failure(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="I could not finish"):
        run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                     kb_app_root=tmp_path / "x", cfg=None)
    assert "failed" in Journal.read_all(tmp_path / "j.jsonl")[-1].outcome


# --- replay_route -----------------------------------------------------------

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

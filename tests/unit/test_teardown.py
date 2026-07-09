from unittest.mock import patch
from pipeline.teardown import close_app
from tools.journal import Journal
from tools.models import JournalEvent

class FakeSession:
    hwnd = 1234
    class config: name = "x"; discard_label_res = []

def test_close_app_journals_closed_when_window_gone(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.teardown.win32gui.PostMessage"), \
         patch("pipeline.teardown._window_alive", side_effect=[True, False]):
        close_app(FakeSession(), j)
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "closed"

def test_close_app_falls_back_to_kill(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.teardown.win32gui.PostMessage"), \
         patch("pipeline.teardown._window_alive", return_value=True), \
         patch("pipeline.teardown._kill_by_hwnd_pid") as kill:
        close_app(FakeSession(), j)
    kill.assert_called_once()
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "killed"

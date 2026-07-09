import subprocess
import time

import pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.teardown import close_app, _window_alive
from tools.journal import Journal

pytestmark = pytest.mark.smoke

def test_stage0_launches_notepad(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        assert s.version and s.pid > 0
        assert Journal.read_all(tmp_path / "journal.jsonl")[-1].outcome == "ok"
        close_app(s, j)
        assert not _window_alive(s.hwnd)
        assert Journal.read_all(tmp_path / "journal.jsonl")[-1].outcome in ("closed", "killed")
    finally:
        # Modern Notepad can host its real window under a broker/child
        # process distinct from the Popen pid, and close_app's WM_CLOSE/kill
        # can leave sibling restored-session windows running, which then
        # poisons later smoke tests with ambiguous title matches.
        # Unconditional belt-and-suspenders cleanup by image name, same
        # pattern as tests/smoke/test_uia_smoke.py,
        # tests/smoke/test_windows_smoke.py, tests/smoke/test_inputs_smoke.py.
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True)

import subprocess
import time

import pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from tools.journal import Journal

pytestmark = pytest.mark.smoke

def test_stage0_launches_notepad(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        assert s.version and s.pid > 0
        assert Journal.read_all(tmp_path / "journal.jsonl")[-1].outcome == "ok"
    finally:
        import win32gui, win32con
        win32gui.PostMessage(s.hwnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.5)
        # Modern Notepad can host its real window under a broker/child
        # process distinct from the Popen pid, and a lone WM_CLOSE can leave
        # the window -- or sibling restored-session windows -- running, which
        # then poisons later smoke tests with ambiguous title matches.
        # Unconditional belt-and-suspenders cleanup by image name, same
        # pattern as tests/smoke/test_uia_smoke.py,
        # tests/smoke/test_windows_smoke.py, tests/smoke/test_inputs_smoke.py.
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True)

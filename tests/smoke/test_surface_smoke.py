import json, subprocess, time, pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.stage1_surface import scan_surface
from tools.journal import Journal
from tools.kb_writer import KBWriter

pytestmark = pytest.mark.smoke

# Locale note (evidence from Task 10 / stage0 smoke): this machine runs a
# Turkish Windows locale, so Win11 Notepad's menu bar renders localized
# labels ("Dosya" instead of "File") -- automation_id stays "File" underneath,
# but build_surface's UIElement has no auto_id field to assert on (by design;
# Task 11 is a mechanical uia-source scan, not a locale-mapping stage). The
# honest adaptation is to assert against the label the scan actually
# captured, tolerating either the English or the localized Turkish string,
# rather than inventing an auto_id assertion the interface doesn't support.
FILE_MENU_LABELS = ("File", "Dosya")

def test_surface_scan_on_notepad(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "notepad" / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        paths = scan_surface(s, KBWriter(tmp_path, "notepad"), j)
        data = json.loads(paths[0].read_text(encoding="utf-8"))
        labels = [e["label"] for e in data["children"]]
        assert any(any(f in l for f in FILE_MENU_LABELS) for l in labels), labels
        assert (tmp_path / "notepad" / data["screenshot"]).exists()
    finally:
        import win32gui, win32con
        win32gui.PostMessage(s.hwnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(0.5)
        # Modern Notepad can host its real window under a broker/child
        # process distinct from the Popen pid, and a lone WM_CLOSE can leave
        # the window -- or sibling restored-session windows -- running, which
        # then poisons later smoke tests with ambiguous title matches.
        # Unconditional belt-and-suspenders cleanup by image name, same
        # pattern as tests/smoke/test_stage0_smoke.py.
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True)

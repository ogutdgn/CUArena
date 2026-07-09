import pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.prober import probe_element
from pipeline.stage1_surface import scan_surface
from pipeline.teardown import close_app
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import UIContainer
import json

pytestmark = pytest.mark.smoke

def test_probe_notepad_file_menu(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "j.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        paths = scan_surface(s, KBWriter(tmp_path, "notepad"), j)
        c = UIContainer.model_validate_json(paths[0].read_text(encoding="utf-8"))
        file_item = next(e for e in c.children if (e.id or "").endswith("/file") or e.label in ("File", "Dosya"))
        r = probe_element(s, file_item, j)
        assert r.kind in ("expands-inline", "opens-flyout"), r.kind
        assert len(r.expanded) >= 3          # New / Open / Save ... appeared
        assert r.restored
    finally:
        close_app(s, j)

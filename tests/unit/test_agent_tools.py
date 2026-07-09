import json, pytest
from pathlib import Path
from unittest.mock import patch
from pipeline.agent_tools import (ToolContext, read_screen_impl, click_impl, press_impl,
                                  write_container_impl, write_script_impl, run_script_impl)
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.winapp.uia import ElemInfo

class FakeUI:
    def children(self, depth=1):
        return [ElemInfo("Button", "Bold", (0, 0, 10, 10), ""),
                ElemInfo("Button", "Save", (10, 0, 20, 10), "")]
class FakeSession:
    ui = FakeUI(); hwnd = 1
class FakeCfg:
    destructive_label_res = []; discard_label_res = []

def ctx(tmp_path):
    return ToolContext(session=FakeSession(), writer=KBWriter(tmp_path, "x"),
                       journal=Journal(tmp_path / "j.jsonl", run_id="t"),
                       kb_app_root=tmp_path / "x", cfg=FakeCfg())

def test_read_screen_lists_elements_with_refs(tmp_path):
    out = json.loads(read_screen_impl(ctx(tmp_path)))
    assert out[0]["label"] == "Bold" and out[0]["ref"] == "bold-0"

def test_click_blocks_destructive(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"):
        assert click_impl(c, "Save").startswith("blocked")
    assert Journal.read_all(c.journal.path)[-1].outcome == "blocked"

def test_press_blocks_save_chord(tmp_path):
    assert press_impl(ctx(tmp_path), "^s").startswith("blocked")

def test_write_container_rejects_bad_json(tmp_path):
    out = write_container_impl(ctx(tmp_path), '{"id": "nope"}')
    assert out.startswith("rejected")

def test_write_script_confines_to_scripts_dir(tmp_path):
    c = ctx(tmp_path)
    p = write_script_impl(c, "extract/scan.py", "print('hi')")
    assert Path(p).is_relative_to(tmp_path / "x" / "scripts")
    with pytest.raises(ValueError):
        write_script_impl(c, "../evil.py", "boom")

def test_run_script_captures_output(tmp_path):
    c = ctx(tmp_path)
    write_script_impl(c, "extract/hello.py", "print('hello-from-script')")
    out = run_script_impl(c, "extract/hello.py")
    assert "hello-from-script" in out and "exit 0" in out

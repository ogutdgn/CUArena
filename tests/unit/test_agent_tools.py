import base64, io, json, pytest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from pipeline.agent_tools import (ToolContext, read_screen_impl, click_impl, press_impl,
                                  screenshot_impl, write_container_impl, write_script_impl,
                                  run_script_impl)
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.winapp.uia import ElemInfo

class FakeUI:
    def __init__(self, children=None):
        self._children = children if children is not None else [
            ElemInfo("Button", "Bold", (0, 0, 10, 10), ""),
            ElemInfo("Button", "Save", (10, 0, 20, 10), "")]
    def children(self, depth=1):
        return self._children
class FakeSession:
    def __init__(self, ui=None, hwnd=1):
        self.ui = ui or FakeUI()
        self.hwnd = hwnd
class FakeCfg:
    destructive_label_res = []; discard_label_res = []

def ctx(tmp_path, session=None):
    return ToolContext(session=session or FakeSession(), writer=KBWriter(tmp_path, "x"),
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


# --- FIX 4: act-verify in click_impl ----------------------------------------

class MutableUI:
    """Fake UI whose children() reflects a click by swapping in `after`."""
    def __init__(self, before, after):
        self._elements = before
        self._before, self._after = before, after
    def children(self, depth=1):
        return self._elements
    def apply_click(self):
        self._elements = self._after

def test_click_reports_new_elements_after_click(tmp_path):
    before = [ElemInfo("Button", "Home", (0, 0, 10, 10), "")]
    after = [ElemInfo("Button", "Home", (0, 0, 10, 10), ""),
             ElemInfo("Button", "Bold", (10, 0, 20, 10), ""),
             ElemInfo("Button", "Italic", (20, 0, 30, 10), "")]
    ui = MutableUI(before, after)
    session = FakeSession(ui=ui)
    c = ctx(tmp_path, session=session)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.time.sleep", side_effect=lambda _: ui.apply_click()), \
         patch("pipeline.agent_tools.top_windows", return_value=[]):
        out = click_impl(c, "Home")
    assert "clicked 'Home'" in out
    assert "+2 new elements" in out
    assert "Bold" in out and "Italic" in out

def test_click_reports_gone_elements_after_click(tmp_path):
    before = [ElemInfo("Button", "Home", (0, 0, 10, 10), ""),
              ElemInfo("Button", "Bold", (10, 0, 20, 10), "")]
    after = [ElemInfo("Button", "Home", (0, 0, 10, 10), "")]
    ui = MutableUI(before, after)
    session = FakeSession(ui=ui)
    c = ctx(tmp_path, session=session)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.time.sleep", side_effect=lambda _: ui.apply_click()), \
         patch("pipeline.agent_tools.top_windows", return_value=[]):
        out = click_impl(c, "Home")
    assert "-1 gone" in out

def test_click_reports_no_visible_change(tmp_path):
    same = [ElemInfo("Button", "Home", (0, 0, 10, 10), "")]
    ui = MutableUI(same, same)
    session = FakeSession(ui=ui)
    c = ctx(tmp_path, session=session)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.time.sleep"), \
         patch("pipeline.agent_tools.top_windows", return_value=[]):
        out = click_impl(c, "Home")
    assert "no visible change" in out


# --- FIX 5: honesty guardrail in write_container_impl -----------------------

def test_write_container_rejects_empty_tab(tmp_path):
    out = write_container_impl(ctx(tmp_path),
                                json.dumps({"id": "ui:tab-home", "kind": "tab",
                                            "label": "Home", "children": []}))
    assert out.startswith("rejected: empty tab container")
    ev = Journal.read_all((tmp_path / "j.jsonl"))[-1]
    assert ev.outcome == "rejected-empty"

def test_write_container_rejects_empty_menu_dialog_dropdown_pane(tmp_path):
    for kind in ("menu", "dialog", "dropdown", "pane"):
        out = write_container_impl(ctx(tmp_path),
                                    json.dumps({"id": f"ui:{kind}-x", "kind": kind,
                                                "label": "X", "children": []}))
        assert out.startswith("rejected: empty"), kind

def test_write_container_allows_empty_window_or_section(tmp_path):
    for kind in ("window", "section"):
        out = write_container_impl(ctx(tmp_path),
                                    json.dumps({"id": f"ui:{kind}-x", "kind": kind,
                                                "label": "X", "children": []}))
        assert not out.startswith("rejected"), kind

def test_write_container_allows_nonempty_tab(tmp_path):
    out = write_container_impl(ctx(tmp_path), json.dumps({
        "id": "ui:tab-home", "kind": "tab", "label": "Home",
        "children": [{"control_type": "button", "label": "Bold",
                      "icon": {"description": "none"}, "source": "uia",
                      "unexplored": True}]}))
    assert not out.startswith("rejected")


# --- FIX 2/3: screenshot uses grab_window and returns the image -------------

def test_screenshot_impl_uses_grab_window_and_returns_path_and_image(tmp_path):
    c = ctx(tmp_path)
    fake_img = Image.new("RGB", (4, 4), (10, 20, 30))
    with patch("pipeline.agent_tools.capture.grab_window",
               return_value=(fake_img, "print-window")) as fake_grab:
        rel_path, b64_png = screenshot_impl(c, "home-tab")
    fake_grab.assert_called_once_with(1)  # FakeSession.hwnd
    assert rel_path.endswith(".png")
    assert isinstance(b64_png, str) and len(b64_png) > 0

def test_screenshot_impl_downscales_wide_images_for_the_agent_but_not_on_disk(tmp_path):
    c = ctx(tmp_path)
    wide_img = Image.new("RGB", (2000, 1000), (5, 5, 5))
    with patch("pipeline.agent_tools.capture.grab_window",
               return_value=(wide_img, "print-window")):
        rel_path, b64_png = screenshot_impl(c, "wide")
    # Full-resolution PNG still lands on disk (writer.save_screenshot, as before).
    saved = Image.open(tmp_path / "x" / rel_path)
    assert saved.size[0] == 2000
    # But the image handed back to the agent is downscaled to keep tokens sane.
    thumb = Image.open(io.BytesIO(base64.b64decode(b64_png)))
    assert thumb.size[0] <= 1280

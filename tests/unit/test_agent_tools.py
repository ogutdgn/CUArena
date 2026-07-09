import base64, io, json, pytest
from pathlib import Path
from unittest.mock import patch
from PIL import Image
from pipeline.agent_tools import (
    ToolContext, downscale_for_agent, look_impl, inspect_impl, click_impl,
    type_text_impl, press_impl, scroll_impl, bring_forward_impl, probe_impl,
    write_container_impl, write_worklist_impl, note_progress_impl,
    write_script_impl, run_script_impl,
)
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.winapp.uia import ElemInfo

SMALL_IMG = Image.new("RGB", (4, 4), (10, 20, 30))


class FakeUI:
    def __init__(self, children=None, rect=(0, 0, 200, 100), name="Fake Window"):
        self._children = children if children is not None else [
            ElemInfo("Button", "Bold", (0, 0, 10, 10), ""),
            ElemInfo("Button", "Save", (10, 0, 20, 10), "")]
        self._rect = rect
        self._name = name

    def children(self, depth=1):
        return self._children

    def info(self):
        return ElemInfo("Window", self._name, self._rect, "")


class FakeSession:
    def __init__(self, ui=None, hwnd=1):
        self.ui = ui or FakeUI()
        self.hwnd = hwnd


class FakeCfg:
    destructive_label_res = []
    discard_label_res = []


def ctx(tmp_path, session=None):
    return ToolContext(session=session or FakeSession(), writer=KBWriter(tmp_path, "x"),
                       journal=Journal(tmp_path / "j.jsonl", run_id="t"),
                       kb_app_root=tmp_path / "x", cfg=FakeCfg())


def _patch_grab_window(return_value=None):
    return patch("pipeline.agent_tools.capture.grab_window",
                return_value=return_value or (SMALL_IMG, "print-window"))


# --- downscale_for_agent (pure helper) --------------------------------------

def test_downscale_leaves_narrow_image_untouched():
    img = Image.new("RGB", (300, 200))
    out = downscale_for_agent(img, max_width=1280)
    assert out.size == (300, 200)

def test_downscale_bounds_wide_image_preserving_aspect():
    img = Image.new("RGB", (2560, 1440))
    out = downscale_for_agent(img, max_width=1280)
    assert out.width == 1280
    assert out.height == pytest.approx(720, abs=2)

def test_downscale_returns_a_copy_not_the_original():
    img = Image.new("RGB", (100, 100))
    out = downscale_for_agent(img, max_width=1280)
    assert out is not img


# --- look() ------------------------------------------------------------

def test_look_returns_text_and_image(tmp_path):
    c = ctx(tmp_path)
    with _patch_grab_window():
        text, b64_png = look_impl(c)
    assert "Fake Window" in text and "200x100" in text
    assert isinstance(b64_png, str) and len(b64_png) > 0
    Image.open(io.BytesIO(base64.b64decode(b64_png)))  # decodes cleanly

def test_look_journals_ok(tmp_path):
    c = ctx(tmp_path)
    with _patch_grab_window():
        look_impl(c)
    ev = Journal.read_all(c.journal.path)[-1]
    assert ev.actor == "explorer.look" and ev.outcome == "ok"


# --- inspect() -----------------------------------------------------------

def test_inspect_lists_elements_with_refs(tmp_path):
    out = json.loads(inspect_impl(ctx(tmp_path)))
    assert out[0]["label"] == "Bold" and out[0]["ref"] == "bold-0"


# --- click(): label/ref path -------------------------------------------

def test_click_blocks_destructive_label(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"):
        text, img = click_impl(c, "Save")
    assert text.startswith("blocked") and img is None
    assert Journal.read_all(c.journal.path)[-1].outcome == "blocked"

def test_click_not_found_label(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"):
        text, img = click_impl(c, "Nonexistent")
    assert text.startswith("not found") and img is None

def test_click_success_returns_summary_and_image(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.time.sleep"), \
         patch("pipeline.agent_tools.top_windows", return_value=[]), \
         _patch_grab_window():
        text, b64_png = click_impl(c, "Bold")
    assert "clicked 'Bold'" in text
    assert isinstance(b64_png, str) and len(b64_png) > 0
    ev = Journal.read_all(c.journal.path)[-1]
    assert ev.outcome == "ok" and ev.data["capture_method"] == "print-window"


# --- click(): coordinate path with hit-test safety ----------------------

class FakeHit:
    def __init__(self, name):
        self.name = name

def test_click_coords_blocks_when_hit_test_matches_destructive(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.element_at", return_value=FakeHit("Save")):
        text, img = click_impl(c, "50,50")
    assert text.startswith("blocked") and img is None

def test_click_coords_succeeds_and_uses_absolute_coords(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.element_at", return_value=FakeHit("Canvas")), \
         patch("pipeline.agent_tools.time.sleep"), \
         patch("pipeline.agent_tools.top_windows", return_value=[]), \
         _patch_grab_window():
        text, b64_png = click_impl(c, "50,60")
    assert "clicked 'Canvas'" in text
    # FakeUI rect origin is (0,0) so relative == absolute here.
    fake_inputs.click_rect.assert_called_once_with((50, 60, 50, 60))
    assert b64_png is not None

def test_click_coords_relative_to_window_origin(tmp_path):
    ui = FakeUI(rect=(500, 200, 700, 400))
    session = FakeSession(ui=ui)
    c = ctx(tmp_path, session=session)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.element_at", return_value=FakeHit("Canvas")) as fake_hit, \
         patch("pipeline.agent_tools.time.sleep"), \
         patch("pipeline.agent_tools.top_windows", return_value=[]), \
         _patch_grab_window():
        click_impl(c, "10,20")
    fake_hit.assert_called_once_with(510, 220)
    fake_inputs.click_rect.assert_called_once_with((510, 220, 510, 220))

def test_click_coords_no_name_falls_back_to_raw_target_label(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.element_at", return_value=FakeHit("")), \
         patch("pipeline.agent_tools.time.sleep"), \
         patch("pipeline.agent_tools.top_windows", return_value=[]), \
         _patch_grab_window():
        text, _ = click_impl(c, "5,5")
    assert "clicked '5,5'" in text


# --- type_text() ---------------------------------------------------------

def test_type_text_settles_and_returns_image(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.time.sleep") as fake_sleep, \
         _patch_grab_window():
        text, b64_png = type_text_impl(c, "hello world")
    fake_inputs.type_text.assert_called_once_with("hello world")
    fake_sleep.assert_called_once()
    assert "typed 11 chars" in text
    assert b64_png is not None
    ev = Journal.read_all(c.journal.path)[-1]
    assert ev.actor == "explorer.type_text" and ev.outcome == "ok"


# --- press() -------------------------------------------------------------

def test_press_blocks_save_chord(tmp_path):
    text, img = press_impl(ctx(tmp_path), "^s")
    assert text.startswith("blocked") and img is None

def test_press_blocks_print_chord(tmp_path):
    text, img = press_impl(ctx(tmp_path), "^p")
    assert text.startswith("blocked") and img is None

def test_press_blocks_altf4(tmp_path):
    text, img = press_impl(ctx(tmp_path), "%{F4}")
    assert text.startswith("blocked") and img is None

def test_press_success_returns_image(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"), \
         patch("pipeline.agent_tools.time.sleep"), \
         _patch_grab_window():
        text, b64_png = press_impl(c, "{TAB}")
    assert "pressed '{TAB}'" in text
    assert b64_png is not None


# --- scroll() ------------------------------------------------------------

def test_scroll_up_positive_wheel_dist(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.time.sleep"), \
         _patch_grab_window():
        text, b64_png = scroll_impl(c, "up", amount=3)
    fake_inputs.scroll.assert_called_once_with((100, 50), 3)
    assert "scrolled up x3" in text
    assert b64_png is not None

def test_scroll_down_negative_wheel_dist(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.time.sleep"), \
         _patch_grab_window():
        scroll_impl(c, "down", amount=5)
    fake_inputs.scroll.assert_called_once_with((100, 50), -5)

def test_scroll_invalid_direction_rejected(tmp_path):
    c = ctx(tmp_path)
    text, img = scroll_impl(c, "sideways")
    assert text.startswith("invalid direction") and img is None

def test_scroll_uses_window_center(tmp_path):
    ui = FakeUI(rect=(0, 0, 300, 200))
    session = FakeSession(ui=ui)
    c = ctx(tmp_path, session=session)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.time.sleep"), \
         _patch_grab_window():
        scroll_impl(c, "up")
    fake_inputs.scroll.assert_called_once_with((150, 100), 3)


# --- bring_forward() -------------------------------------------------------

def test_bring_forward_ensures_foreground_and_returns_image(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs") as fake_inputs, \
         patch("pipeline.agent_tools.time.sleep"), \
         _patch_grab_window():
        text, b64_png = bring_forward_impl(c)
    fake_inputs.ensure_foreground.assert_called_once_with(1)
    assert text == "brought to foreground"
    assert b64_png is not None


# --- probe() ---------------------------------------------------------------

def test_probe_blocks_destructive(tmp_path):
    c = ctx(tmp_path)
    text, img = probe_impl(c, "Save")
    assert text.startswith("blocked") and img is None

def test_probe_not_found(tmp_path):
    c = ctx(tmp_path)
    text, img = probe_impl(c, "Nope")
    assert text.startswith("not found") and img is None

def test_probe_success_returns_image(tmp_path):
    c = ctx(tmp_path)
    fake_result = type("R", (), {"kind": "no-effect", "expanded": [], "restored": True})()
    with patch("pipeline.agent_tools.probe_element", return_value=fake_result), \
         _patch_grab_window():
        text, b64_png = probe_impl(c, "Bold")
    out = json.loads(text)
    assert out["kind"] == "no-effect"
    assert b64_png is not None


# --- write_container: empty-container guard (kept from salvage) ------------

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

def test_write_container_rejects_bad_json(tmp_path):
    out = write_container_impl(ctx(tmp_path), '{"id": "nope"}')
    assert out.startswith("rejected")


# --- write_worklist() --------------------------------------------------

def test_write_worklist_writes_valid_items(tmp_path):
    c = ctx(tmp_path)
    items = [{"surface": "Home tab", "how": "click the Home tab"},
             {"surface": "File menu", "how": "click File in the menu bar"}]
    out = write_worklist_impl(c, json.dumps(items))
    path = Path(out)
    assert path.name == "worklist.json"
    saved = json.loads(path.read_text(encoding="utf-8"))
    assert saved == items
    ev = Journal.read_all(c.journal.path)[-1]
    assert ev.actor == "explorer.write_worklist" and ev.outcome == "ok"
    assert ev.data["items"] == 2

def test_write_worklist_rejects_bad_json(tmp_path):
    out = write_worklist_impl(ctx(tmp_path), "{not json")
    assert out.startswith("rejected")

def test_write_worklist_rejects_empty_list(tmp_path):
    out = write_worklist_impl(ctx(tmp_path), "[]")
    assert out.startswith("rejected")

def test_write_worklist_rejects_non_list(tmp_path):
    out = write_worklist_impl(ctx(tmp_path), json.dumps({"surface": "x", "how": "y"}))
    assert out.startswith("rejected")

def test_write_worklist_rejects_missing_fields(tmp_path):
    out = write_worklist_impl(ctx(tmp_path), json.dumps([{"surface": "Home"}]))
    assert out.startswith("rejected")

def test_write_worklist_rejects_blank_fields(tmp_path):
    out = write_worklist_impl(ctx(tmp_path), json.dumps([{"surface": "  ", "how": "x"}]))
    assert out.startswith("rejected")


# --- note_progress() -----------------------------------------------------

def test_note_progress_journals_and_returns_noted(tmp_path):
    c = ctx(tmp_path)
    out = note_progress_impl(c, "skipping the ribbon overflow menu, couldn't verify it opened")
    assert out == "noted"
    ev = Journal.read_all(c.journal.path)[-1]
    assert ev.actor == "explorer.note" and ev.outcome == "progress"
    assert "ribbon overflow" in ev.data["text"]


# --- scripting (unchanged semantics) ----------------------------------

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

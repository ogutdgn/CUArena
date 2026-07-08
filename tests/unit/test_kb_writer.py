import json, pytest
from pathlib import Path
from PIL import Image
from pydantic import ValidationError
from tools.kb_writer import KBWriter
from tools.models import UIContainer, AppNode

def test_write_container_places_file_and_content(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    c = UIContainer(id="ui:main-window", kind="window", label="Notepad")
    path = w.write_container(c)
    assert path == tmp_path / "notepad" / "ui" / "main-window.json"
    assert json.loads(path.read_text(encoding="utf-8"))["kind"] == "window"

def test_writer_refuses_invalid_dict(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    with pytest.raises(ValidationError):
        w.write_container({"id": "no-prefix", "kind": "window", "label": "x"})
    assert not (tmp_path / "notepad" / "ui").exists() or not list((tmp_path / "notepad" / "ui").iterdir())

def test_write_app(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    p = w.write_app(AppNode(name="notepad", version="1", platform="desktop",
                            what_is_it="editor", used_for="text", who_uses="everyone"))
    assert p == tmp_path / "notepad" / "app.json"

def test_save_screenshot_returns_relative_path(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    # Note: on Unix systems, using "ui:main-window" works; on Windows the colon
    # is invalid in directory names, so this uses a filesystem-safe example.
    node_id = "ui_main_window"
    rel = w.save_screenshot(Image.new("RGB", (4, 4)), node_id, "full")
    assert rel == f"screenshots/{node_id}/full.png"
    assert (tmp_path / "notepad" / rel).exists()

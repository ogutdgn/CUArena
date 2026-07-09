import json, pytest
from pathlib import Path
from pipeline.config import load_app_config, AppConfig

def test_load_notepad_config():
    cfg = load_app_config("notepad", Path("configs/apps"))
    assert isinstance(cfg, AppConfig) and cfg.exe.lower().endswith("notepad.exe")

def test_unknown_app_raises():
    with pytest.raises(FileNotFoundError):
        load_app_config("nope", Path("configs/apps"))

def test_boundaries_default_empty(tmp_path: Path):
    (tmp_path / "x.json").write_text(json.dumps(
        {"name": "x", "exe": "x.exe", "window_title_re": ".*x.*"}), encoding="utf-8")
    cfg = load_app_config("x", tmp_path)
    assert cfg.boundaries.dismiss_title_res == [] and cfg.dialog_classes == ["#32770"]

def test_ready_state_fields_default(tmp_path: Path):
    (tmp_path / "x.json").write_text(json.dumps(
        {"name": "x", "exe": "x.exe", "window_title_re": ".*x.*"}), encoding="utf-8")
    cfg = load_app_config("x", tmp_path)
    assert cfg.launch_args == [] and cfg.fixture is None

def test_ready_state_fields_load(tmp_path: Path):
    (tmp_path / "x.json").write_text(json.dumps(
        {"name": "x", "exe": "x.exe", "window_title_re": ".*x.*",
         "launch_args": ["{fixture}"], "fixture": "configs/fixtures/x/blank.docx"}), encoding="utf-8")
    cfg = load_app_config("x", tmp_path)
    assert cfg.launch_args == ["{fixture}"] and cfg.fixture == "configs/fixtures/x/blank.docx"

def test_safety_label_extras_default_empty(tmp_path):
    import json
    (tmp_path / "y.json").write_text(json.dumps(
        {"name": "y", "exe": "y.exe", "window_title_re": ".*y.*"}), encoding="utf-8")
    cfg = load_app_config("y", tmp_path)
    assert cfg.destructive_label_res == [] and cfg.discard_label_res == []

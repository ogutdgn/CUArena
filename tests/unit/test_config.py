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

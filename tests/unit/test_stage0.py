import json, pytest
from pathlib import Path
from pipeline.config import AppConfig
from pipeline.stage0 import assert_version, VersionDriftError, build_argv

def _app_json(tmp_path: Path, version: str) -> Path:
    p = tmp_path / "app.json"
    p.write_text(json.dumps({"name": "x", "version": version, "platform": "desktop",
                             "what_is_it": "a", "used_for": "b", "who_uses": "c",
                             "layout_regions": [], "feature_inventory": []}), encoding="utf-8")
    return p

def _version_json(tmp_path: Path, version: str) -> Path:
    p = tmp_path / "version.json"
    p.write_text(json.dumps({"version": version}), encoding="utf-8")
    return p

def test_assert_version_passes_on_match(tmp_path):
    assert_version(_app_json(tmp_path, "1.2.3"), "1.2.3")   # no raise

def test_assert_version_fails_loudly_on_drift(tmp_path):
    with pytest.raises(VersionDriftError):
        assert_version(_app_json(tmp_path, "1.2.3"), "9.9.9")

def test_assert_version_ok_when_no_prior_kb(tmp_path):
    assert_version(tmp_path / "missing.json", "1.2.3")      # first run: nothing to drift from

def test_assert_version_first_run_no_raise_with_version_json_param(tmp_path):
    # No prior record of either file -> no raise, even when the version.json
    # path is passed explicitly (agent-independent KB, brand new).
    assert_version(tmp_path / "app.json", "1.2.3", kb_version_json=tmp_path / "version.json")

def test_assert_version_match_passes_via_version_json(tmp_path):
    assert_version(tmp_path / "missing-app.json", "1.2.3",
                    kb_version_json=_version_json(tmp_path, "1.2.3"))   # no raise

def test_assert_version_drift_detected_via_version_json_without_app_json(tmp_path):
    # --no-agent-only KB: version.json exists, app.json never has (agent never ran).
    with pytest.raises(VersionDriftError):
        assert_version(tmp_path / "missing-app.json", "9.9.9",
                        kb_version_json=_version_json(tmp_path, "1.2.3"))

def test_assert_version_prefers_version_json_over_app_json(tmp_path):
    # If both exist and disagree, version.json (the agent-independent record) wins.
    app_json = _app_json(tmp_path, "1.2.3")
    version_json = _version_json(tmp_path, "1.2.3")
    assert_version(app_json, "1.2.3", kb_version_json=version_json)   # no raise: matches version.json

def test_build_argv_no_args_unchanged():
    cfg = AppConfig(name="x", exe="notepad.exe", window_title_re=".*")
    assert build_argv(cfg) == ["notepad.exe"]

def test_build_argv_fixture_substitution_produces_absolute_existing_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fixture_dir = tmp_path / "configs" / "fixtures" / "word"
    fixture_dir.mkdir(parents=True)
    fixture_path = fixture_dir / "blank.docx"
    fixture_path.write_bytes(b"fake docx")
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*",
                     launch_args=["{fixture}"], fixture="configs/fixtures/word/blank.docx")
    argv = build_argv(cfg)
    assert len(argv) == 2 and argv[0] == "WINWORD.EXE"
    resolved = Path(argv[1])
    assert resolved.is_absolute() and resolved.exists() and resolved == fixture_path.resolve()

def test_build_argv_missing_fixture_placeholder_without_fixture_raises():
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*", launch_args=["{fixture}"])
    with pytest.raises(ValueError):
        build_argv(cfg)

def test_build_argv_fixture_placeholder_with_nonexistent_file_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*",
                     launch_args=["{fixture}"], fixture="configs/fixtures/word/missing.docx")
    with pytest.raises(ValueError):
        build_argv(cfg)

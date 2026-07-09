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
    assert resolved.is_absolute() and resolved.exists()

def test_build_argv_fixture_is_copied_to_scratch_not_original_path(tmp_path, monkeypatch):
    # Root cause (found building the Task 4 live discard smoke test): this
    # repo lives under a OneDrive-synced folder, and modern Word enables
    # AutoSave purely by local path recognition for any file under such a
    # folder. With AutoSave on, edits are persisted continuously and the
    # canonical fixture gets silently corrupted, AND the close-time Save
    # dialog is suppressed (nothing pending to ask about) -- exactly the
    # dialog Task 4's discard logic needs to exercise. build_argv must never
    # hand the original fixture path to the app; it must copy it to a
    # scratch location outside the repo (tempfile.gettempdir()) and
    # substitute that.
    monkeypatch.chdir(tmp_path)
    fixture_dir = tmp_path / "configs" / "fixtures" / "word"
    fixture_dir.mkdir(parents=True)
    fixture_path = fixture_dir / "blank.docx"
    fixture_path.write_bytes(b"fake docx contents")
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*",
                     launch_args=["{fixture}"], fixture="configs/fixtures/word/blank.docx")

    argv = build_argv(cfg)
    resolved = Path(argv[1])

    assert resolved != fixture_path.resolve(), "must not open the original fixture path"
    import tempfile
    assert Path(tempfile.gettempdir()) in resolved.parents
    assert resolved.read_bytes() == fixture_path.read_bytes()

def test_build_argv_fixture_scratch_copies_are_distinct_across_calls(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    fixture_dir = tmp_path / "configs" / "fixtures" / "word"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "blank.docx").write_bytes(b"fake docx contents")
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*",
                     launch_args=["{fixture}"], fixture="configs/fixtures/word/blank.docx")

    first = Path(build_argv(cfg)[1])
    second = Path(build_argv(cfg)[1])
    assert first != second

def test_build_argv_journals_scratch_copy(tmp_path, monkeypatch):
    from tools.journal import Journal
    monkeypatch.chdir(tmp_path)
    fixture_dir = tmp_path / "configs" / "fixtures" / "word"
    fixture_dir.mkdir(parents=True)
    (fixture_dir / "blank.docx").write_bytes(b"fake docx contents")
    cfg = AppConfig(name="word", exe="WINWORD.EXE", window_title_re=".*",
                     launch_args=["{fixture}"], fixture="configs/fixtures/word/blank.docx")
    j = Journal(tmp_path / "j.jsonl", run_id="t")

    argv = build_argv(cfg, journal=j)
    scratch = argv[1]
    events = Journal.read_all(tmp_path / "j.jsonl")
    assert events[-1].actor == "stage0" and events[-1].action == "fixture"
    assert events[-1].outcome == "ok" and events[-1].data.get("scratch") == scratch

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

from unittest.mock import patch
from pipeline.stage0 import resolve_session_version

def test_version_prefers_window_process(tmp_path):
    with patch("pipeline.stage0.window_process_path", return_value="C:\\real\\app.exe"), \
         patch("pipeline.stage0.file_version", return_value="11.1.0.0") as fv:
        v = resolve_session_version(1234, "stub.exe", journal=None)
    assert v == "11.1.0.0"
    fv.assert_called_once_with("C:\\real\\app.exe")

def test_version_falls_back_to_exe(tmp_path):
    from tools.journal import Journal
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.stage0.window_process_path", side_effect=OSError("denied")), \
         patch("pipeline.stage0.file_version", return_value="1.0") :
        v = resolve_session_version(1234, "stub.exe", journal=j)
    assert v == "1.0"
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "version-fallback"

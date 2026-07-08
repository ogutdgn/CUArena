import json, pytest
from pathlib import Path
from pipeline.stage0 import assert_version, VersionDriftError

def _app_json(tmp_path: Path, version: str) -> Path:
    p = tmp_path / "app.json"
    p.write_text(json.dumps({"name": "x", "version": version, "platform": "desktop",
                             "what_is_it": "a", "used_for": "b", "who_uses": "c",
                             "layout_regions": [], "feature_inventory": []}), encoding="utf-8")
    return p

def test_assert_version_passes_on_match(tmp_path):
    assert_version(_app_json(tmp_path, "1.2.3"), "1.2.3")   # no raise

def test_assert_version_fails_loudly_on_drift(tmp_path):
    with pytest.raises(VersionDriftError):
        assert_version(_app_json(tmp_path, "1.2.3"), "9.9.9")

def test_assert_version_ok_when_no_prior_kb(tmp_path):
    assert_version(tmp_path / "missing.json", "1.2.3")      # first run: nothing to drift from

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from journal import Journal
from emit import emit


def _mini(tmp_path):
    j = Journal(tmp_path / "j.jsonl")
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.bold", "label": "Bold", "type": "toggle",
                          "idMso": "Bold", "action": {"kind": "toggles"},
                          "capture": {"status": "complete", "probe_mode": "pattern-inferred",
                                      "schema_version": 1}}})
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.fontdialog", "label": "Font Settings",
                          "type": "launcher",
                          "action": {"kind": "opens-dialog", "ref": "dialogs/font"},
                          "capture": {"status": "complete", "probe_mode": "pressed-observed",
                                      "schema_version": 1}}})
    j.append({"t": "surface-discovered", "surface": "dialogs/font", "entry": "ribbon.home.font.fontdialog"})
    j.append({"t": "surface-captured", "surface": "dialogs/font",
              "payload": {"id": "dialogs/font", "title": "Font", "modal": True,
                          "schema_version": 1, "tabs": [], "buttons": []}})
    j.append({"t": "boundary", "from": "ribbon.file", "kind": "opens-backstage",
              "policy": "excluded", "decision": "D4"})
    return j


def test_entry_points_and_closure(tmp_path):
    out = tmp_path / "out"
    rep = emit(_mini(tmp_path), out, tmp_path)
    assert rep["dangling"] == []
    font = json.loads((out / "dialogs" / "font.json").read_text(encoding="utf-8"))
    assert font["entry_points"] == ["ribbon.home.font.fontdialog"]
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert any(e["from"] == "ribbon.file" and e["decision"] == "D4" for e in cov["boundaries"])
    assert (out / "manifest.json").exists()


def test_dangling_and_orphans(tmp_path):
    out = tmp_path / "out"; (out / "dialogs").mkdir(parents=True)
    (out / "dialogs" / "stale.json").write_text("{}", encoding="utf-8")
    j = _mini(tmp_path)
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.ghost", "label": "Ghost", "type": "menu",
                          "action": {"kind": "opens-menu", "ref": "dropdowns/ghost"},
                          "capture": {"status": "complete", "probe_mode": "pressed-observed",
                                      "schema_version": 1}}})
    rep = emit(j, out, tmp_path)
    assert "dropdowns/ghost" in rep["dangling"]
    assert any(str(p).endswith("stale.json") for p in rep["orphans_deleted"])

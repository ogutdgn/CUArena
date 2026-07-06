import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import schemas

GOOD = {"id": "ribbon.home.font.bold", "label": "Bold", "type": "toggle",
        "action": {"kind": "toggles"}, "idMso": "Bold",
        "capture": {"status": "complete", "probe_mode": "pattern-inferred", "schema_version": 1}}


def test_good_control():
    assert schemas.validate_control(GOOD) == []


def test_ref_xor_boundary():
    bad = dict(GOOD, action={"kind": "opens-dialog"})
    assert any("ref XOR boundary" in e for e in schemas.validate_control(bad))
    bad2 = dict(GOOD, action={"kind": "opens-dialog", "ref": "dialogs/font",
                              "boundary": {"policy": "excluded", "decision": "D4"}})
    assert any("ref XOR boundary" in e for e in schemas.validate_control(bad2))


def test_popup_items_need_ids():
    pop = {"id": "dropdowns/x", "schema_version": 1, "sections": [
        {"kind": "menu-items", "items": [{"label": "no id", "action": {"kind": "feature"}}]}]}
    assert any("item id" in e for e in schemas.validate_popup(pop))

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


def test_bad_section_kind():
    pop = {"id": "dropdowns/x", "schema_version": 1, "sections": [
        {"kind": "gallery-filters", "items": []}]}
    assert any("bad section kind" in e for e in schemas.validate_popup(pop))


def test_color_grid_ok_and_missing_rgb():
    good = {"id": "dropdowns/fontcolor", "schema_version": 1, "sections": [
        {"kind": "color-grid", "title": "Theme Colors", "items": [
            {"id": "t0-r0", "rgb": "#FFFFFF", "themeSlot": 0, "tint": 0,
             "action": {"kind": "feature"}}]}]}
    assert schemas.validate_popup(good) == []
    bad = {"id": "dropdowns/fontcolor", "schema_version": 1, "sections": [
        {"kind": "color-grid", "items": [{"id": "t0", "action": {"kind": "feature"}}]}]}
    assert any("no rgb/bounds" in e for e in schemas.validate_popup(bad))


def test_split_requires_zones():
    bad = {"id": "ribbon.home.x.y", "type": "split", "label": "Y",
           "action": {"kind": "feature"},
           "capture": {"status": "complete", "probe_mode": "pressed-observed", "schema_version": 1}}
    assert any("split missing primary/flyout" in e for e in schemas.validate_control(bad))
    # boundary-declared split is exempt (never zone-probed)
    boundary_split = dict(bad, action={"kind": "feature",
                                       "boundary": {"policy": "excluded", "decision": "D8"}})
    assert schemas.validate_control(boundary_split) == []
    # a real split with both zones is valid
    ok = {"id": "ribbon.home.x.y", "type": "split", "label": "Y",
          "primary": {"action": {"kind": "feature"}},
          "flyout": {"action": {"kind": "opens-dropdown", "ref": "dropdowns/z"}},
          "capture": {"status": "complete", "probe_mode": "pressed-observed", "schema_version": 1}}
    assert schemas.validate_control(ok) == []

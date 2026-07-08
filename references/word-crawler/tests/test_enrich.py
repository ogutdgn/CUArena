import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import enrich


TABLE = {("selectmenu", "select all"): "Selects the entire document.",
         ("bordersselectiongallery", "view gridlines"): "Toggles table gridlines."}


def test_norm_strips_ellipsis_and_case():
    assert enrich._norm("Select All") == "select all"
    assert enrich._norm("Line Spacing Options...") == "line spacing options"
    assert enrich._norm("Selection Pane…") == "selection pane"
    assert enrich._norm("Sentence case.") == "sentence case"      # gallery-tile trailing period


def test_apply_only_to_leaves():
    doc = {"id": "dropdowns/selectmenu", "sections": [{"kind": "menu-items", "items": [
        {"id": "select-all", "label": "Select All", "action": {"kind": "feature"}},
        # an item that OPENS a surface must NOT receive a leaf description even if named in the table
        {"id": "selection-pane", "label": "Selection Pane...",
         "action": {"kind": "opens-pane", "ref": "panes/selection-pane"}},
    ]}]}
    n = enrich.apply_to_popup("dropdowns/selectmenu", doc, TABLE)
    assert n == 1
    items = doc["sections"][0]["items"]
    assert items[0]["description"] == "Selects the entire document."
    assert "description" not in items[1]


def test_apply_skips_non_dropdowns():
    doc = {"id": "dialogs/font", "sections": []}
    assert enrich.apply_to_popup("dialogs/font", doc, TABLE) == 0


def test_load_missing_fixture_is_empty(tmp_path):
    assert enrich.load_descriptions(tmp_path / "nope.json") == {}

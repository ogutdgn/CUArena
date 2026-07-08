"""Pure-logic tests for capture.py helpers (no live Word)."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import capture


def test_popup_action_ascii_and_unicode_ellipsis():
    a, disc = capture._popup_action("Paste Special...")
    assert disc and a == {"kind": "opens-dialog", "ref": "dialogs/paste-special"}
    a, disc = capture._popup_action("Line Spacing Options…")   # Unicode ellipsis (was typed feature)
    assert disc and a == {"kind": "opens-dialog", "ref": "dialogs/line-spacing-options"}
    a, disc = capture._popup_action("Select All")
    assert not disc and a == {"kind": "feature"}


def test_button_action_scopes_child_dialog_by_parent():
    # Sort's and Borders&Shading's identically-named 'Options...' must not alias to one id.
    a, _ = capture._button_action("Options...", "sort")
    assert a["ref"] == "dialogs/sort-options"
    a, _ = capture._button_action("Options...", "borders-and-shading")
    assert a["ref"] == "dialogs/borders-and-shading-options"
    a, role = capture._button_action("OK", "sort")
    assert a == {"kind": "feature"} and role == "default"
    a, role = capture._button_action("Cancel", "sort")
    assert a == {"kind": "feature"} and role == "cancel"
    a, _ = capture._button_action("Text Effects…", "font")     # Unicode ellipsis on buttons too
    assert a["ref"] == "dialogs/font-text-effects"


def test_merge_orphan_headers_reattaches_split_gallery():
    # font.json: 'Theme Fonts' header emptied, its 2 fonts split into untitled 1-item sections.
    sections = [
        {"kind": "gallery", "title": "Theme Fonts", "items": []},
        {"kind": "gallery", "items": [{"id": "aptos-display"}]},
        {"kind": "gallery", "items": [{"id": "aptos"}]},
        {"kind": "gallery", "title": "All Fonts", "items": [{"id": "agency-fb"}]},
    ]
    out = capture._merge_orphan_headers(sections)
    assert len(out) == 2
    assert out[0]["title"] == "Theme Fonts"
    assert [i["id"] for i in out[0]["items"]] == ["aptos-display", "aptos"]
    assert out[1]["title"] == "All Fonts"                       # titled+nonempty: untouched
    assert "_absorb" not in out[0]


def test_merge_orphan_headers_leaves_normal_sections_alone():
    sections = [
        {"kind": "gallery", "title": "Styles", "items": [{"id": "a"}]},
        {"kind": "gallery", "items": [{"id": "b"}]},            # untitled after a NON-empty titled
        {"kind": "menu-items", "items": [{"id": "c"}]},
    ]
    out = capture._merge_orphan_headers(list(sections))
    assert len(out) == 3                                        # nothing absorbed


def test_drop_occluded_bounds():
    # a footer checkbox painted over the last two clipped list rows -> those rows lose their bounds
    controls = [
        {"id": "normal", "type": "listitem", "bounds": {"x": 0, "y": 10, "w": 200, "h": 20}},
        {"id": "subtitle", "type": "listitem", "bounds": {"x": 0, "y": 158, "w": 200, "h": 20}},
        {"id": "show-preview", "type": "checkbox", "bounds": {"x": 0, "y": 158, "w": 200, "h": 18}},
        {"id": "scrolled-in", "type": "listitem", "scrolled": True},   # no bounds -> untouched
    ]
    capture._drop_occluded_bounds(controls)
    assert "bounds" in controls[0]                       # clear row keeps its bounds
    assert "bounds" not in controls[1] and controls[1]["occluded"] is True   # occluded row cleared
    assert "occluded" not in controls[2]                 # the footer control itself is untouched
    assert "bounds" not in controls[3]                   # scrolled row: no crash, still no bounds


def test_gallery_ellipsis_item_opens_dialog():
    a, disc = capture._popup_action("Line Spacing Options…")
    assert disc and a == {"kind": "opens-dialog", "ref": "dialogs/line-spacing-options"}


def test_cascade_window_separates_submenu_from_tooltip(monkeypatch):
    # popup occupies x=[100,400]; a submenu cascades to the right (l>=376), a ScreenTip appears
    # over/below the hovered item (l well inside the popup).
    popup = (100, 200, 400, 700)
    rects = {
        11: (390, 210, 560, 430),   # real submenu: left edge past popup right, tall  -> accepted
        22: (150, 260, 300, 285),   # ScreenTip over the item: inside popup, short    -> rejected
        33: (380, 240, 384, 400),   # a 4px-wide sliver at the edge                    -> rejected (w<24)
    }
    monkeypatch.setattr(capture.win32gui, "GetWindowRect", lambda h: rects[h])
    assert capture._cascade_window({22, 33, 11}, popup) == 11
    assert capture._cascade_window({22}, popup) is None          # tooltip only -> no submenu
    assert capture._cascade_window({33}, popup) is None          # sliver only  -> no submenu
    assert capture._cascade_window(set(), popup) is None


def test_dedup_fields_keeps_outer_of_nested_same_name():
    combo = {"name": "Style Name:", "type": "combo",
             "bounds": {"x": 10, "y": 10, "w": 200, "h": 24}}
    inner = {"name": "Style Name:", "type": "text",
             "bounds": {"x": 12, "y": 12, "w": 180, "h": 20}}   # nested inside the combo
    other = {"name": "Reapply", "type": "checkbox",
             "bounds": {"x": 10, "y": 40, "w": 90, "h": 18}}
    assert capture._dedup_fields([combo, inner, other]) == [combo, other]
    assert capture._dedup_fields([inner, combo, other]) == [combo, other]   # order-independent
    # same name, DISJOINT rects: two real fields, keep both
    twin = {"name": "Style Name:", "type": "text",
            "bounds": {"x": 300, "y": 10, "w": 100, "h": 20}}
    assert capture._dedup_fields([combo, twin]) == [combo, twin]
    # unnamed fields never collapse
    anon1 = {"name": "", "type": "text", "bounds": {"x": 0, "y": 0, "w": 500, "h": 500}}
    anon2 = {"name": "", "type": "text", "bounds": {"x": 1, "y": 1, "w": 10, "h": 10}}
    assert capture._dedup_fields([anon1, anon2]) == [anon1, anon2]

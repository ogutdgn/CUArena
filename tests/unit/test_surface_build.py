from tools.winapp.uia import ElemInfo
from pipeline.stage1_surface import build_surface

WIN = ElemInfo("Window", "Notepad", (0, 0, 800, 600), "")

def test_build_surface_marks_everything_unexplored():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("MenuItem", "Edit", (40, 0, 80, 20), "")]
    c = build_surface(WIN, kids, app="notepad")
    assert c.id == "ui:main-window" and c.kind == "window"
    assert [e.label for e in c.children] == ["File", "Edit"]
    assert all(e.unexplored and e.triggers is None and e.opens is None for e in c.children)
    assert all(e.source == "uia" for e in c.children)

def test_unnamed_elements_are_skipped_not_invented():
    kids = [ElemInfo("Button", "", (0, 0, 10, 10), ""), ElemInfo("MenuItem", "File", (0, 0, 40, 20), "")]
    c = build_surface(WIN, kids, app="notepad")
    assert [e.label for e in c.children] == ["File"]

def test_excluded_labels_are_filtered_out():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("MenuItem", "Edit", (40, 0, 80, 20), ""),
            ElemInfo("MenuItem", "Ads", (80, 0, 120, 20), "")]
    c = build_surface(WIN, kids, app="notepad", exclude_labels=("Ads",))
    assert [e.label for e in c.children] == ["File", "Edit"]

def test_no_exclude_labels_keeps_default_behavior():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), "")]
    c = build_surface(WIN, kids, app="notepad")
    assert [e.label for e in c.children] == ["File"]

def test_build_surface_assigns_unique_element_ids():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("Button", "Close", (0, 0, 10, 10), ""),
            ElemInfo("Button", "Close", (10, 0, 20, 10), "")]
    c = build_surface(WIN, kids, app="notepad")
    ids = [e.id for e in c.children]
    assert ids == ["el:main-window/file", "el:main-window/close", "el:main-window/close-1"]
    assert len(set(ids)) == len(ids)

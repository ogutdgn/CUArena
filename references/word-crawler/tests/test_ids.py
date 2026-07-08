import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import ids, pytest


def test_slugify_and_cap():
    assert ids.slugify("Format Painter") == "format-painter"
    assert ids.slugify("Text Effects...") == "text-effects"
    assert len(ids.slugify("A" * 100)) == 64
    assert ids.slugify("A" * 100) == "a" * 64


def test_control_segment_prefers_idmso():
    assert ids.control_segment("Bold", "Bold (Ctrl+B)") == "bold"
    assert ids.control_segment("", "Format Painter") == "format-painter"


def test_grammar():
    assert ids.surface_id("dropdowns", "Numbering Library") == "dropdowns/numbering-library"
    assert ids.node_id("ribbon", "home", "paragraph", "numbering") == "ribbon.home.paragraph.numbering"
    assert ids.node_id("ribbon", "home", "paragraph", "numbering", zone="flyout").endswith(".flyout")
    with pytest.raises(ValueError):
        ids.node_id("ribbon", "home", "paragraph", "x", zone="left-half")
    assert ids.sub_addr("dropdowns/numbering-library", "decimal-1") == "dropdowns/numbering-library#decimal-1"


def test_predicates():
    assert ids.is_surface_ref("dialogs/font")
    assert ids.is_node_id("ribbon.home.font.bold")
    assert ids.is_sub_addr("dialogs/font#field:size")
    assert not ids.is_surface_ref("ribbon.home.font.bold")

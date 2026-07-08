import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import textutil


def test_strip_control_chars():
    assert textutil.sanitize_label("Number Format: \x01.a.") == "Number Format: .a."
    assert textutil.sanitize_label("a\x00b\x1fc") == "a b c"


def test_collapse_whitespace():
    assert textutil.sanitize_label("  Font   color \n ") == "Font color"


def test_drop_state_suffix():
    assert textutil.sanitize_label(
        "Select All Text With Similar Formatting (No Data)"
    ) == "Select All Text With Similar Formatting"


def test_empty_and_none():
    assert textutil.sanitize_label(None) == ""
    assert textutil.sanitize_label("") == ""


def test_is_chrome():
    assert textutil.is_chrome("Gallery Filters")
    assert textutil.is_chrome("  ")
    assert textutil.is_chrome("")
    assert not textutil.is_chrome("Theme Colors")


def test_is_chrome_scrollbar_parts():
    # Owner-drawn popups leak their scrollbar's part buttons as fake menu-items.
    for n in ("Line up", "Line down", "Page up", "Page down",
              "Column left", "Column right"):
        assert textutil.is_chrome(n), n
    # A real command that merely starts with a scrollbar word must survive.
    assert not textutil.is_chrome("Line Numbers")
    assert not textutil.is_chrome("Page Color")

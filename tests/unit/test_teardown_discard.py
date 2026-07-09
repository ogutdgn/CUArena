from pipeline.teardown import find_discard_target
from tools.winapp.uia import ElemInfo

def E(name): return ElemInfo("Button", name, (0, 0, 10, 10), "")

def test_finds_dont_save_variants():
    els = [E("Save"), E("Don't Save"), E("Cancel")]
    assert find_discard_target(els, []).name == "Don't Save"

def test_finds_localized_via_config_extras():
    els = [E("Kaydet"), E("Kaydetme"), E("İptal")]
    assert find_discard_target(els, [r"(?i)kaydetme"]).name == "Kaydetme"

def test_never_returns_save_or_cancel():
    els = [E("Save"), E("Cancel")]
    assert find_discard_target(els, []) is None

from tools.ids import slug, element_id

def test_slug_folds_and_collapses():
    assert slug("Font Color…") == "font-color"
    assert slug("  Büyük  Harf ") == "buyuk-harf"          # ascii-fold non-English letters
    assert slug("A" * 100) == "a" * 60

def test_element_id_shape_and_ordinals():
    assert element_id("ui:main-window", "Bold", 0) == "el:main-window/bold"
    assert element_id("ui:tab-home", "Bold", 2) == "el:tab-home/bold-2"

def test_slug_folds_dotless_i():
    assert slug("Yardım") == "yardim"
    assert slug("Sağ Tıkla") == "sag-tikla"
    assert slug("İçindekiler") == "icindekiler"

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from PIL import Image
import shots


def test_rel_bounds():
    assert shots.rel_bounds((110, 220, 136, 244), (100, 200, 900, 300)) == {"x": 10, "y": 20, "w": 26, "h": 24}


def test_quality_gate(tmp_path):
    blank = tmp_path / "blank.png"
    Image.new("RGB", (26, 24), "white").save(blank)
    assert not shots.quality_ok(blank)              # all one color
    tiny = tmp_path / "tiny.png"
    Image.new("RGB", (3, 3), "black").save(tiny)
    assert not shots.quality_ok(tiny)               # side < 4px
    ok = tmp_path / "ok.png"
    img = Image.new("RGB", (26, 24), "white")
    for x in range(8, 18):
        for y in range(6, 18):
            img.putpixel((x, y), (30, 30, 30))
    img.save(ok)
    assert shots.quality_ok(ok)                     # two colors, big enough

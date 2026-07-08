from PIL import Image
from tools.winapp.capture import crop, pixel

def test_crop_uses_window_origin():
    img = Image.new("RGB", (100, 100), (0, 0, 0))
    img.paste((255, 0, 0), (10, 10, 20, 20))
    c = crop(img, rect_abs=(510, 210, 520, 220), origin_rect=(500, 200, 600, 300))
    assert c.size == (10, 10) and pixel(c, 5, 5) == (255, 0, 0)

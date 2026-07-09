from unittest.mock import patch
from PIL import Image
from tools.winapp.capture import _is_blank, crop, grab_window, pixel

def test_crop_uses_window_origin():
    img = Image.new("RGB", (100, 100), (0, 0, 0))
    img.paste((255, 0, 0), (10, 10, 20, 20))
    c = crop(img, rect_abs=(510, 210, 520, 220), origin_rect=(500, 200, 600, 300))
    assert c.size == (10, 10) and pixel(c, 5, 5) == (255, 0, 0)

def test_is_blank_detects_uniform_image():
    assert _is_blank(Image.new("RGB", (10, 10), (0, 0, 0)))

def test_is_blank_false_for_varied_image():
    img = Image.new("RGB", (10, 10), (0, 0, 0))
    img.paste((255, 0, 0), (0, 0, 5, 5))
    assert not _is_blank(img)

def test_grab_window_uses_print_window_result_when_not_blank():
    varied = Image.new("RGB", (10, 10), (0, 0, 0))
    varied.paste((255, 0, 0), (0, 0, 5, 5))
    with patch("tools.winapp.capture._print_window", return_value=varied):
        img, method = grab_window(123)
    assert method == "print-window"
    assert img is varied

def test_grab_window_falls_back_when_print_window_blank():
    blank = Image.new("RGB", (10, 10), (0, 0, 0))
    fallback = Image.new("RGB", (10, 10), (1, 2, 3))
    with patch("tools.winapp.capture._print_window", return_value=blank), \
         patch("tools.winapp.capture.win32gui.GetWindowRect", return_value=(0, 0, 10, 10)), \
         patch("tools.winapp.capture.grab_region", return_value=fallback) as fake_grab, \
         patch("tools.winapp.inputs.ensure_foreground") as fake_fg:
        img, method = grab_window(123)
    fake_fg.assert_called_once_with(123)
    fake_grab.assert_called_once_with((0, 0, 10, 10))
    assert method == "foreground-fallback"
    assert img is fallback

def test_grab_window_falls_back_when_print_window_raises():
    fallback = Image.new("RGB", (10, 10), (1, 2, 3))
    with patch("tools.winapp.capture._print_window", side_effect=OSError("boom")), \
         patch("tools.winapp.capture.win32gui.GetWindowRect", return_value=(0, 0, 10, 10)), \
         patch("tools.winapp.capture.grab_region", return_value=fallback), \
         patch("tools.winapp.inputs.ensure_foreground"):
        img, method = grab_window(123)
    assert method == "foreground-fallback"
    assert img is fallback

def test_grab_window_falls_back_when_print_window_returns_none():
    fallback = Image.new("RGB", (10, 10), (1, 2, 3))
    with patch("tools.winapp.capture._print_window", return_value=None), \
         patch("tools.winapp.capture.win32gui.GetWindowRect", return_value=(0, 0, 10, 10)), \
         patch("tools.winapp.capture.grab_region", return_value=fallback), \
         patch("tools.winapp.inputs.ensure_foreground"):
        img, method = grab_window(123)
    assert method == "foreground-fallback"
    assert img is fallback

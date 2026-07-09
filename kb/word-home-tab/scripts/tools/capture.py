"""capture — window-true surface shots, icon crops, and quality gating.

toolbox/screenshot.md law: grab by screen rect (multi-monitor aware); ONE screenshot per
surface, then crop icons out of that image (never re-grab the screen for a sub-rect — the
surface may have moved/closed); record geometry RELATIVE to the surface; gate crop quality
(reject <4px and single-color crops).
"""
import sys
from pathlib import Path

import win32gui
from PIL import Image, ImageGrab

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts


def grab_rect(rect) -> Image.Image:
    """Grab exactly this screen rect (left,top,right,bottom), multi-monitor aware."""
    return ImageGrab.grab(bbox=tuple(rect), all_screens=True)


def grab_window(hwnd) -> tuple:
    """Window-true grab: the exact window rect, not a guessed region. Returns (img, rect)."""
    rect = win32gui.GetWindowRect(hwnd)
    return grab_rect(rect), rect


def rel_bounds(control_rect, surface_rect):
    l, t, r, b = control_rect
    sl, st, _, _ = surface_rect
    return (l - sl, t - st, r - sl, b - st)


def crop_from(surface_img: Image.Image, control_rect, surface_rect) -> Image.Image:
    """Crop a control out of the surface image using surface-relative coordinates."""
    box = rel_bounds(control_rect, surface_rect)
    # clamp to image
    l, t, r, b = box
    l = max(0, l); t = max(0, t)
    r = min(surface_img.width, r); b = min(surface_img.height, b)
    return surface_img.crop((l, t, r, b))


def quality_ok(img: Image.Image) -> bool:
    """Reject crops that are too small or a single flat color (the crop missed its target)."""
    im = img.convert("RGB")
    if im.width < 4 or im.height < 4:
        return False
    colors = im.getcolors(maxcolors=4096)
    if colors and len(colors) == 1:
        return False
    return True


def sample_rgb(img: Image.Image, x, y) -> str:
    im = img.convert("RGB")
    x = max(0, min(im.width - 1, int(x)))
    y = max(0, min(im.height - 1, int(y)))
    r, g, b = im.getpixel((x, y))
    return f"#{r:02X}{g:02X}{b:02X}"

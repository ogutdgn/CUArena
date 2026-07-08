from PIL import Image, ImageGrab


def grab(rect, out):
    ImageGrab.grab(bbox=rect, all_screens=True).save(out)


def crop_from(surface_png, rect_in_surface, out):
    Image.open(surface_png).crop(rect_in_surface).save(out)


def rel_bounds(control_rect, surface_rect):
    l, t, r, b = control_rect
    sl, st, _, _ = surface_rect
    return {"x": l - sl, "y": t - st, "w": r - l, "h": b - t}


def sample_rgb(png, x, y):
    """Return '#RRGGBB' at pixel (x, y) in the image, clamped to bounds. Used to read
    owner-drawn color swatches (no reliable UIA color property exists)."""
    img = Image.open(png).convert("RGB")
    x = max(0, min(img.width - 1, int(x)))
    y = max(0, min(img.height - 1, int(y)))
    r, g, b = img.getpixel((x, y))
    return f"#{r:02X}{g:02X}{b:02X}"


def quality_ok(png):
    img = Image.open(png).convert("RGB")
    if img.width < 4 or img.height < 4:
        return False
    colors = img.getcolors(maxcolors=4096)
    if colors and len(colors) == 1:
        return False
    return True

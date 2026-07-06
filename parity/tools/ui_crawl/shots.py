from PIL import Image, ImageGrab


def grab(rect, out):
    ImageGrab.grab(bbox=rect, all_screens=True).save(out)


def crop_from(surface_png, rect_in_surface, out):
    Image.open(surface_png).crop(rect_in_surface).save(out)


def rel_bounds(control_rect, surface_rect):
    l, t, r, b = control_rect
    sl, st, _, _ = surface_rect
    return {"x": l - sl, "y": t - st, "w": r - l, "h": b - t}


def quality_ok(png):
    img = Image.open(png).convert("RGB")
    if img.width < 4 or img.height < 4:
        return False
    colors = img.getcolors(maxcolors=4096)
    if colors and len(colors) == 1:
        return False
    return True

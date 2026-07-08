from PIL import Image, ImageGrab

def grab_region(rect) -> Image.Image:
    return ImageGrab.grab(bbox=rect)

def crop(img: Image.Image, rect_abs, origin_rect) -> Image.Image:
    ol, ot = origin_rect[0], origin_rect[1]
    l, t, r, b = rect_abs
    return img.crop((l - ol, t - ot, r - ol, b - ot))

def pixel(img: Image.Image, x: int, y: int) -> tuple[int, int, int]:
    return img.convert("RGB").getpixel((x, y))

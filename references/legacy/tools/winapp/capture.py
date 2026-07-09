from ctypes import windll
from PIL import Image, ImageGrab
import win32con
import win32gui
import win32ui

# PW_RENDERFULLCONTENT: not exposed by pywin32's win32con, so the literal
# value from the Win32 SDK (winuser.h) is used directly. Required (over
# flag 0/PW_CLIENTONLY or 1) for modern (WinUI/UWP/DirectComposition-backed)
# windows -- without it PrintWindow silently returns a black/blank bitmap
# for such windows even though it reports success (return value 1).
PW_RENDERFULLCONTENT = 2

def grab_region(rect) -> Image.Image:
    return ImageGrab.grab(bbox=rect)

def crop(img: Image.Image, rect_abs, origin_rect) -> Image.Image:
    ol, ot = origin_rect[0], origin_rect[1]
    l, t, r, b = rect_abs
    return img.crop((l - ol, t - ot, r - ol, b - ot))

def pixel(img: Image.Image, x: int, y: int) -> tuple[int, int, int]:
    return img.convert("RGB").getpixel((x, y))

def _is_blank(img: Image.Image) -> bool:
    # A PrintWindow call that "succeeds" (returns nonzero) but rendered
    # nothing produces a bitmap that is a single flat color -- extrema's
    # (min, max) per channel collapse to equal values. Any real screen
    # content has variation in at least one channel.
    extrema = img.convert("RGB").getextrema()
    return all(lo == hi for lo, hi in extrema)

def _print_window(hwnd: int) -> Image.Image | None:
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = right - left, bottom - top
    if width <= 0 or height <= 0:
        return None

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    try:
        result = windll.user32.PrintWindow(hwnd, save_dc.GetSafeHdc(), PW_RENDERFULLCONTENT)
        if not result:
            return None
        bmp_info = bitmap.GetInfo()
        bmp_bits = bitmap.GetBitmapBits(True)
        img = Image.frombuffer(
            "RGB", (bmp_info["bmWidth"], bmp_info["bmHeight"]), bmp_bits,
            "raw", "BGRX", 0, 1,
        )
        return img
    finally:
        win32gui.DeleteObject(bitmap.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwnd_dc)

def grab_window(hwnd: int) -> tuple[Image.Image, str]:
    """Capture the window's own surface via PrintWindow, regardless of
    z-order/foreground state. Falls back to a foreground+region grab if
    PrintWindow fails or renders a blank image (observed with some legacy
    GDI apps). Returns (image, method) where method is "print-window" or
    "foreground-fallback" so callers/journals can record which path fired.
    """
    try:
        img = _print_window(hwnd)
    except Exception:
        img = None

    if img is not None and not _is_blank(img):
        return img, "print-window"

    from tools.winapp import inputs

    inputs.ensure_foreground(hwnd)
    rect = win32gui.GetWindowRect(hwnd)
    return grab_region(rect), "foreground-fallback"

import subprocess
import time

import pytest

from tools.winapp.uia import UIASession
from tools.winapp.capture import _is_blank, grab_region, grab_window
from tools.winapp.windows import top_windows, wait_new_window

pytestmark = pytest.mark.smoke


def test_grab_notepad_window():
    proc = subprocess.Popen(["notepad.exe"])
    time.sleep(1.5)
    try:
        rect = UIASession.attach(".*(Notepad|Not Defteri).*").window_rect()
        img = grab_region(rect)
        assert img.size[0] > 50 and img.size[1] > 50
    finally:
        proc.kill()
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True,
        )


def test_grab_window_of_live_notepad_is_non_blank_and_sized_per_rect():
    # Attach by hwnd (via wait_new_window) rather than title regex: on this
    # machine Notepad's UIA-visible title can transiently match more than
    # one top-level element (session-restore/second window), which makes
    # title_re attachment ambiguous. hwnd attachment sidesteps that, same
    # pattern already used in tests/smoke/test_inputs_smoke.py.
    before = top_windows()
    proc = subprocess.Popen(["notepad.exe"])
    try:
        new_win = wait_new_window(before, timeout=5.0)
        assert new_win is not None
        session = UIASession.attach_by_handle(new_win.hwnd)
        rect = session.window_rect()
        expected_w, expected_h = rect[2] - rect[0], rect[3] - rect[1]

        img, method = grab_window(session._win.handle)

        assert method in ("print-window", "foreground-fallback")
        assert not _is_blank(img)
        # Allow a small tolerance: DPI/border rounding can differ by a few px
        # between GetWindowRect (used for the fallback) and the bitmap
        # PrintWindow actually renders.
        assert abs(img.size[0] - expected_w) <= 10
        assert abs(img.size[1] - expected_h) <= 10
    finally:
        proc.kill()
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True,
        )

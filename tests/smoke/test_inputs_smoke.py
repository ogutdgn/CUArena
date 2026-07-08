import subprocess
import time

import pytest

from tools.winapp.uia import UIASession
from tools.winapp.windows import top_windows, wait_new_window
from tools.winapp import inputs

pytestmark = pytest.mark.smoke


def test_click_file_menu_opens_menu():
    before = top_windows()
    proc = subprocess.Popen(["notepad.exe"])
    try:
        assert wait_new_window(before, timeout=5.0)
        # NOTE on locale: this machine's Notepad title is a localized
        # session-restored string with no "Notepad" substring at all
        # (observed in tests/smoke/test_uia_smoke.py: e.g. "Not Defteri").
        # Match either the English or Turkish app name, per Task 5/6 precedent.
        s = UIASession.attach(".*(Notepad|Not Defteri).*")
        inputs.ensure_foreground(s._win.handle)

        # NOTE on depth: Win11 Notepad nests the menu bar at depth 4, not the
        # brief's depth=3/2 -- see tests/smoke/test_uia_smoke.py for the
        # empirically dumped tree (window->Pane->Pane->MenuBar->MenuItem).
        kids = s.children(depth=4)

        # NOTE on locale: menu item `name` is localized (observed "Dosya",
        # not "File"); `auto_id` is UIA's locale-invariant identifier and was
        # observed to be the literal "File" on that same MenuItem. Match on
        # auto_id, falling back to a name startswith check for portability
        # on an English-locale machine where auto_id might be absent.
        file_item = next(
            (k for k in kids if k.auto_id == "File"),
            None,
        ) or next(k for k in kids if k.name.startswith("File"))

        pre = len(s.children(depth=4))
        inputs.click_rect(file_item.rect)
        time.sleep(0.5)
        post = len(s.children(depth=4))
        assert post > pre, "clicking File should expand a menu (more elements visible)"
        inputs.press("{ESC}")
    finally:
        # Modern Notepad can host its real window under a broker/child
        # process distinct from the Popen pid, so proc.kill() alone may
        # leave a window running. Belt-and-suspenders cleanup by image name
        # (same pattern as tests/smoke/test_uia_smoke.py and
        # tests/smoke/test_windows_smoke.py).
        proc.kill()
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True)

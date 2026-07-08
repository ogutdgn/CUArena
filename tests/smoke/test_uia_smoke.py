import re
import subprocess
import time

import pytest
from pywinauto import Desktop

from tools.winapp.uia import UIASession

pytestmark = pytest.mark.smoke


def _find_notepad_title(timeout=10.0):
    """Poll the UIA desktop for a top-level window of class 'Notepad' and
    return its current title text.

    Modern (Windows 11) Notepad restores whatever tabs/session were open at
    last exit, so the window title is unpredictable -- on this machine it is
    a leftover session title with no English "Notepad" substring at all
    (observed: "*Parity Pipeline .. Core Finding and, Not Defteri", where
    "Not Defteri" is Notepad's own localized app name, not the document).
    Matching on class_name (stable, not locale- or session-dependent) is the
    reliable way to find the window; we then hand its literal title back to
    UIASession.attach(title_re=...) so the wrapper is exercised exactly per
    its documented contract (title_re, not class_name).
    """
    deadline = time.time() + timeout
    while time.time() < deadline:
        for w in Desktop(backend="uia").windows():
            try:
                if w.element_info.class_name == "Notepad":
                    return w.window_text()
            except Exception:
                continue
        time.sleep(0.25)
    raise TimeoutError("no top-level window with class_name 'Notepad' appeared")


@pytest.fixture()
def notepad():
    proc = subprocess.Popen(["notepad.exe"])
    time.sleep(1.5)
    try:
        yield proc
    finally:
        # Modern Notepad can host its real window under a broker/child
        # process distinct from the Popen pid, so proc.kill() alone may
        # leave a window running. Belt-and-suspenders cleanup by image name.
        proc.kill()
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True,
        )


def test_attach_and_read_children(notepad):
    title = _find_notepad_title()
    s = UIASession.attach(re.escape(title))

    # NOTE on depth: modern Notepad nests the menu bar deeper than classic
    # Notepad. Empirically dumping the tree on this machine showed:
    #   window(0) -> Pane(1) -> Pane(2) -> MenuBar(3) -> MenuItem "Dosya"(4)
    # depth=2 and depth=3 both come back with 0 menu items; depth=4 is the
    # first depth that reaches the MenuBar's children. Raised from the
    # brief's depth=2 for this reason (code is fine; the tree is just
    # deeper on this Notepad build).
    kids = s.children(depth=4)

    # NOTE on locale: this machine's Notepad UI renders in a localized
    # language (menu item name observed as "Dosya", not "File"), even though
    # the OS UI culture reports en-US -- apparently inherited from the
    # WindowsNotepad AppX package's own resource resolution. The `name`
    # field is therefore not a reliable cross-machine assertion target.
    # `automation_id` is UIA's locale-invariant identifier and was observed
    # to be the literal string "File" on the same MenuItem whose `name` was
    # "Dosya", so we assert on auto_id (still a genuine "did we really find
    # the File menu" check, just not language-dependent).
    auto_ids = [k.auto_id for k in kids if k.auto_id]
    names = [k.name for k in kids if k.name]
    assert "File" in auto_ids, (
        f"expected a File menu (auto_id) among: {auto_ids[:20]}; "
        f"names seen: {names[:20]}"
    )
    assert all(hasattr(k, "control_type") and hasattr(k, "rect") for k in kids)

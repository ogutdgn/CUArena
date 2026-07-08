import re
import subprocess, time, pytest
from pywinauto import Desktop
from tools.winapp.uia import UIASession
from tools.winapp.hit_test import element_at

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

def test_element_at_center_of_notepad():
    proc = subprocess.Popen(["notepad.exe"]); time.sleep(1.5)
    try:
        title = _find_notepad_title()
        l, t, r, b = UIASession.attach(re.escape(title)).window_rect()
        e = element_at((l + r) // 2, (t + b) // 2)
        assert e.control_type  # something real is there (document/edit area)
    finally:
        proc.kill()
        subprocess.run(
            ["taskkill", "/IM", "notepad.exe", "/F"],
            capture_output=True,
        )

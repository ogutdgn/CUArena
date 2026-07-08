import subprocess
import time

import pytest

from tools.winapp.uia import UIASession
from tools.winapp.capture import grab_region

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

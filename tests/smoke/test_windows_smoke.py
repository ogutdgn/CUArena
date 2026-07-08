import subprocess, time, pytest
import win32process
from tools.winapp.windows import top_windows, wait_new_window

pytestmark = pytest.mark.smoke


def test_new_window_detected_on_launch():
    before = top_windows()
    proc = subprocess.Popen(["notepad.exe"])
    try:
        w = wait_new_window(before, timeout=5.0)
        assert w is not None

        # Prefer a pid check (locale-proof): does the new hwnd belong to the
        # process we launched? On this machine (Windows 11, non-English
        # locale) it does NOT -- modern Notepad's visible window is owned by
        # a broker/child process distinct from the Popen pid (observed:
        # proc.pid=35168 vs owning pid=25648, reproduced across runs). Fall
        # back to a title check that accepts either the English or the
        # localized Windows 11 Notepad title ("Notepad" / "Not Defteri",
        # observed literal title: "Not Defteri") so the test stays honest
        # about what it's actually verifying on both kinds of machines.
        _, owner_pid = win32process.GetWindowThreadProcessId(w.hwnd)
        title = w.title or ""
        assert owner_pid == proc.pid or "Notepad" in title or "Not Defteri" in title, (
            f"new window {w!r} matched neither proc.pid={proc.pid} "
            f"(owner_pid={owner_pid}) nor a known Notepad title"
        )
    finally:
        proc.kill()
        subprocess.run(["taskkill", "/IM", "notepad.exe", "/F"], capture_output=True)

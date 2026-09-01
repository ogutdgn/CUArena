"""Debug: open two flyouts (font-color dropdown, line-spacing menu) and compare enumeration via
(a) UIA tree walk and (b) ElementFromPoint hit-testing, to fix the 0-items bug."""
import sys, time
from pathlib import Path
from ctypes.wintypes import POINT

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import uia_attach as ua
import driver as drv
import windows as wins
import enumerator as en
import run_step2 as r2
import run_step5_enter as r5


def tree_walk(hwnd):
    from pywinauto import Desktop
    w = Desktop(backend="uia").window(handle=hwnd)
    out = []
    try:
        for el in w.descendants():
            ct = el.element_info.control_type
            nm = (el.element_info.name or "").strip()
            if ct in ("MenuItem", "ListItem", "Button", "CheckBox", "RadioButton"):
                out.append((ct, nm))
    except Exception as e:
        out.append(("ERR", str(e)))
    return out


def efp(iuia, hwnd):
    l, t, r, b = wins.win32gui.GetWindowRect(hwnd) if hasattr(wins, "win32gui") else (0,0,0,0)
    import win32gui
    l, t, r, b = win32gui.GetWindowRect(hwnd)
    hits, err = [], None
    y = t + 4
    while y < b - 3:
        x = l + 5
        while x < r - 5:
            try:
                el = iuia.ElementFromPoint(POINT(x, y))
                hits.append((el.CurrentControlType, (el.CurrentName or "").strip()))
            except Exception as e:
                err = str(e)
            x += 12
        y += 10
    from collections import Counter
    c = Counter((ct, nm) for ct, nm in hits)
    return len(hits), err, c.most_common(12)


def main():
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build="16.0.20131")
    try:
        sess.doc.Content.InsertAfter("Hello world sample text.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame); time.sleep(0.4)
        pts = r5.build_open_points(win)
        iuia = ua.get_iuia()
        for surf in ("ui:font-color-dropdown", "ui:line-spacing-menu"):
            pt = pts.get(surf)
            if not pt:
                # line-spacing opener is a plain menuitem -> from ribbon bounds
                ribbon = r5.load_container("ui:ribbon-home")
                _, bounds = r5.opener_bounds(ribbon, surf)
                pt = r5._center(bounds)
            before = wins.snapshot_hwnds(sess.pid)
            drv.ensure_frame_foreground(sess.frame)
            drv.click_point(*pt)
            hwnd = None
            for _ in range(12):
                time.sleep(0.2)
                neww = [w for w in wins.new_windows(sess.pid, before) if wins._area(w[3]) >= 4000]
                if neww:
                    hwnd = max(neww, key=lambda w: wins._area(w[3]))[0]; break
            print(f"\n=== {surf} hwnd={hwnd} ===")
            if hwnd:
                tw = tree_walk(hwnd)
                print("  TREE WALK items:", len(tw), tw[:14])
                n, err, common_hits = efp(iuia, hwnd)
                print("  EFP hits:", n, "err:", err)
                print("  EFP top:", common_hits)
            drv.press_escape(2); time.sleep(0.3)
            sess.select_paragraph(1)
    finally:
        sess.close()


if __name__ == "__main__":
    main()

"""R2.8 screenshot-series pass — the gallery crawl captured the full TILE DATA (UIA returns
all list items un-virtualized) but only ONE frame, so a 105-style flyout's visual evidence
showed the first screenful only. This reopens each large gallery flyout and captures a
SCROLL SERIES (surface-1..N.png in scroll order, same group), stopping when the frame stops
changing (pixel hash). Data is untouched — only `screenshots` / `scrolled_to_end` are rewritten.
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import win32api
import win32gui
from pywinauto import mouse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import windows as wins
import capture as cap
import run_step2 as r2
import run_step3_contextual as r3c
import run_step5_enter as s5
import repair_galleries as rg

KB = common.APP_KB
# (host, live element id, family, flyout surface id) — the galleries whose tile count exceeds
# one viewport (worth a series). Small flyouts (<= ~20 tiles) stay single-frame.
BIG = [
    ("ui:ribbon-table-design", "el:ribbon-table-design-table-styles-gallery", "table",
     "ui:ribbon-table-design-table-styles-flyout"),
    ("ui:ribbon-picture-format", "el:ribbon-picture-format-picture-styles-gallery", "picture",
     "ui:ribbon-picture-format-picture-styles-flyout"),
    ("ui:ribbon-graphics-format", "el:ribbon-graphics-format-graphics-styles-gallery",
     "svg-graphic", "ui:ribbon-graphics-format-graphics-styles-flyout"),
    ("ui:ribbon-shape-format", "el:ribbon-shape-format-shape-styles-gallery", "shape",
     "ui:ribbon-shape-format-shape-styles-flyout"),
    ("ui:ribbon-smart-art-design", "el:ribbon-smart-art-design-smart-art-layout-gallery",
     "smartart", "ui:ribbon-smart-art-design-smart-art-layout-flyout"),
    ("ui:ribbon-equation", "el:ribbon-equation-equation-symbols-insert-gallery", "equation",
     "ui:ribbon-equation-equation-symbols-flyout"),
]
MAX_SEG = 12


def phash(rect):
    img = cap.grab_rect(rect)
    return hashlib.md5(img.tobytes()).hexdigest()


def capture_series(writer, jrnl, surf_id, hwnd):
    """Scroll-capture the open flyout into surface-1..N.png; stop when the frame repeats."""
    rect = win32gui.GetWindowRect(hwnd)
    cx, cy = (rect[0] + rect[2]) // 2, (rect[1] + rect[3]) // 2
    shots, hashes = [], set()
    for i in range(MAX_SEG):
        if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
            break
        h = phash(rect)
        if h in hashes:
            break                       # frame stopped changing -> reached the end
        hashes.add(h)
        shots.append(writer.save_screenshot(cap.grab_rect(rect), surf_id,
                                            f"surface-{len(shots) + 1}"))
        mouse.scroll(coords=(cx, cy), wheel_dist=-4)
        time.sleep(0.4)
    ui = writer.load_ui()
    c = ui.containers.get(surf_id)
    if c and shots:
        c.screenshot = shots[0]
        c.screenshots = shots
        c.scrolled_to_end = True
        writer.write_ui(ui)
    jrnl.append(common.journal_event(actor="reshoot.r2_8", action="screenshot-series",
                target=surf_id, outcome=f"{len(shots)} segments"))
    return len(shots)


def main():
    run_id = common.make_run_id() + "-reshoot-series"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    screen_w = win32api.GetSystemMetrics(0)
    results = []
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = s5.DepthWalker(sess, win, writer, jrnl, screen_w)
        probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}
        cur = None
        for host, el_id, fam, surf_id in BIG:
            if fam != cur:
                try:
                    sess.doc.Paragraphs(1).Range.Select()
                except Exception:
                    pass
                for _ in range(12):
                    drv.send_keys("^z")
                    time.sleep(0.2)
                    fp = sess.object_fingerprint()
                    if all(fp.get(k, 0) in (0, -1) for k in ("tables", "inline_shapes", "shapes")):
                        break
                sess.select_paragraph(1)
                probes[fam][0]()
                time.sleep(0.8)
                probes[fam][1]()
                time.sleep(1.0)
                cur = fam
            else:
                probes[fam][1]()
                time.sleep(0.5)
            tab_title = rg.tab_title_of(writer, host)
            ok = False
            for _ in range(3):
                try:
                    en.select_tab(win, tab_title)
                    time.sleep(0.4)
                    ok = True
                    break
                except Exception:
                    r3c._force_close_nonframe(sess, set())
                    drv.press_escape(2)
                    walker.close_all()
                    drv.ensure_frame_foreground(sess.frame)
                    time.sleep(0.5)
                    from session import frame_hwnd as _fh
                    fh = _fh(sess.pid)
                    if fh:
                        sess.frame = fh
                    win = ua.attach(sess.frame)
                    walker.win = win
            if not ok:
                results.append((surf_id, "TAB-FAIL"))
                continue
            el, props = rg.find_gallery_control(win, host, el_id)
            if el is None:
                results.append((surf_id, "NOT-FOUND"))
                continue
            drv.ensure_frame_foreground(sess.frame)
            before = wins.snapshot_hwnds(sess.pid)
            rg.press_expand(el, props)
            new = walker.observe_new(before, floor=2500)
            if not new:
                results.append((surf_id, "NO-FLYOUT"))
                continue
            n = capture_series(writer, jrnl, surf_id, new[0])
            drv.press_escape(2)
            time.sleep(0.3)
            results.append((surf_id, f"{n} segments"))
    finally:
        try:
            sess.close()
        except Exception:
            pass
    print("\n==== RESHOOT RESULTS ====")
    for surf, status in results:
        print(f"  {status:14} {surf.replace('ui:ribbon-', '')}")


if __name__ == "__main__":
    main()

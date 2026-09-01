"""Step 1 proof runner: exercise enumerator + driver + capture against the live app. (4tabs)

Scope = Home + Insert + Design + Layout. Produces:
  * tools/dumps/<tab>_enum.json — every control with name/id(idMso)/type/bounds/tooltip/
    keytip/shortcut per tab (all four universe tabs).
  * screenshots/tool-check/*.png — the four capture types (whole surface, single icon,
    dialog, dropdown/flyout) so a human (and I) can confirm each shows the intended target.
Capture targets are DESIGN/LAYOUT-tab controls — the new ground this run must prove tools
on (Home+Insert were proven by the v2 run on this same build; re-enumerated here anyway).
Journaled throughout; the session is opened cold and torn down.
"""
import json
import sys
import time
from pathlib import Path

import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word-4tabs-v1/scripts
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import capture as cap
import windows as wins

DUMP_DIR = Path(__file__).resolve().parent / "dumps"
TABS = ("Home", "Insert", "Design", "Layout")


def _rect_by_id(groups, idmso):
    for g in groups:
        for c in g["controls"]:
            if c["automation_id"] == idmso:
                return tuple(c["rect"])
    return None


def _dismiss_window(hwnd, pid, jrnl, label):
    """Close a dialog by its Cancel/Close button first, ESC as fallback; verify it vanished."""
    try:
        from pywinauto import Desktop
        dlg = Desktop(backend="uia").window(handle=hwnd)
        for btn in ("Cancel", "Close"):
            try:
                b = dlg.child_window(title=btn, control_type="Button")
                if b.exists(timeout=1):
                    b.click_input()
                    time.sleep(0.4)
                    break
            except Exception:
                continue
    except Exception:
        pass
    for _ in range(4):
        if not (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd)):
            jrnl.append(common.journal_event(actor="stage1.toolcheck", action="dismiss",
                        target=label, outcome="closed", data={}))
            return True
        drv.press_escape(1)
        time.sleep(0.3)
    gone = not (win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd))
    jrnl.append(common.journal_event(actor="stage1.toolcheck", action="dismiss",
                target=label, outcome="closed" if gone else "STUCK", data={}))
    return gone


def _open_capture_close(sess, jrnl, writer, idmso, groups, kind, shot_name):
    """Press a control that opens a surface, capture that surface window-true, close it."""
    rect = _rect_by_id(groups, idmso)
    if not rect:
        jrnl.append(common.journal_event(actor="stage1.toolcheck", action="locate",
                    target=idmso, outcome="NOT-FOUND", data={}))
        return None
    drv.ensure_frame_foreground(sess.frame)
    before = wins.snapshot_hwnds(sess.pid)
    drv.click_rect(rect)
    neww = []
    for _ in range(14):
        time.sleep(0.25)
        neww = wins.new_windows(sess.pid, before)
        neww = [w for w in neww if wins._area(w[3]) >= (wins.MIN_POPUP_AREA if kind == "flyout" else 1)]
        if neww:
            break
    if not neww:
        jrnl.append(common.journal_event(actor="stage1.toolcheck", action="open",
                    target=idmso, outcome=f"NO-{kind}-appeared", data={}))
        drv.press_escape(2)
        return None
    h, cls, title, r = max(neww, key=lambda w: wins._area(w[3]))
    got_kind = wins.classify_window(cls, title, r)
    img = cap.grab_rect(r)
    rel = writer.save_screenshot(img, "tool:check", shot_name)
    jrnl.append(common.journal_event(actor="stage1.toolcheck", action="capture-surface",
                target=idmso, outcome="ok",
                data={"expected": kind, "classified": got_kind, "class": cls,
                      "title": title, "rect": list(r), "path": rel,
                      "size": [img.width, img.height]}))
    _dismiss_window(h, sess.pid, jrnl, idmso)
    return {"idmso": idmso, "kind": got_kind, "class": cls, "path": rel,
            "size": [img.width, img.height]}


def main():
    DUMP_DIR.mkdir(parents=True, exist_ok=True)
    run_id = common.make_run_id() + "-step1"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    pinned = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(actor="stage1.toolcheck", action="launch",
                target="Word", outcome="attempting", data={}))
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage1.toolcheck", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"build": sess.build}))
    summary = {}
    try:
        # give the doc some text so text-gated controls (Drop Cap, hyphenation…) enable
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)

        # --- 1) ENUMERATE all four universe tabs ---
        for tab in TABS:
            enum = en.enumerate_tab(win, tab)
            (DUMP_DIR / f"{tab.lower()}_enum.json").write_text(
                json.dumps(enum, indent=2, ensure_ascii=False), encoding="utf-8")
            jrnl.append(common.journal_event(actor="stage1.toolcheck", action="enumerate-tab",
                        target=tab, outcome="ok",
                        data={"groups": [g["group"] for g in enum["groups"]],
                              "control_count": enum["control_count"]}))
            summary[f"enum_{tab.lower()}"] = {
                "groups": len(enum["groups"]), "controls": enum["control_count"],
                "group_names": [g["group"] for g in enum["groups"]]}
        design_enum = json.loads((DUMP_DIR / "design_enum.json").read_text(encoding="utf-8"))
        layout_enum = json.loads((DUMP_DIR / "layout_enum.json").read_text(encoding="utf-8"))

        # --- 2) WHOLE-SURFACE capture with Design active ---
        en.select_tab(win, "Design")
        drv.ensure_frame_foreground(sess.frame)
        time.sleep(0.4)
        frame_img, frame_rect = cap.grab_window(sess.frame)
        frame_rel = writer.save_screenshot(frame_img, "tool:check", "frame-design")
        ribbon_img = frame_img.crop((0, 0, frame_img.width, 200))
        writer.save_screenshot(ribbon_img, "tool:check", "ribbon-design")
        jrnl.append(common.journal_event(actor="stage1.toolcheck", action="capture-surface",
                    target="frame(design)", outcome="ok",
                    data={"path": frame_rel, "rect": list(frame_rect),
                          "size": [frame_img.width, frame_img.height]}))

        # --- 3) SINGLE ICON crops from the frame surface (quality-gated) ---
        icon_checks = []
        for idmso, nm in [("ThemesGallery", "themes"), ("WatermarkGallery", "watermark"),
                          ("PageBorderAndShadingDialog", "page-borders")]:
            rect = _rect_by_id(design_enum["groups"], idmso)
            if not rect:
                icon_checks.append({"idmso": idmso, "found": False})
                continue
            crop = cap.crop_from(frame_img, rect, frame_rect)
            ok = cap.quality_ok(crop)
            rel = writer.save_screenshot(crop, "tool:check", f"icon-{nm}")
            icon_checks.append({"idmso": idmso, "found": True, "quality_ok": ok,
                                "path": rel, "size": [crop.width, crop.height]})
        jrnl.append(common.journal_event(actor="stage1.toolcheck", action="capture-icons",
                    target="ribbon-design", outcome="ok", data={"icons": icon_checks}))
        summary["icons"] = icon_checks

        # --- 4) DIALOG capture (Layout > Page Setup dialog — local, Cancel-safe) ---
        en.select_tab(win, "Layout")
        time.sleep(0.4)
        dlg = _open_capture_close(sess, jrnl, writer, "PageSetupDialog",
                                  layout_enum["groups"], "dialog", "dialog-page-setup")
        summary["dialog"] = dlg

        # --- 5) DROPDOWN/FLYOUT capture (Layout > Margins gallery flyout) ---
        win = ua.attach(sess.frame)   # re-attach after dialog
        time.sleep(0.3)
        en.select_tab(win, "Layout")
        enum2 = en.enumerate_tab(win, "Layout")
        fly = _open_capture_close(sess, jrnl, writer, "PageMarginsGallery",
                                  enum2["groups"], "flyout", "dropdown-margins")
        summary["dropdown"] = fly

        print(json.dumps(summary, indent=2, ensure_ascii=False))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage1.toolcheck", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()

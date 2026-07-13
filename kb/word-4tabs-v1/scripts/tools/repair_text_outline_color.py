"""Last gap: the Text Outline color picker (subfeature:wordart-text-outline, reached from
Chart/SmartArt Format tabs) was an empty stub — the split-button's dropdown zone wasn't
resolved. Crawl it once live (swatch grid), reference the sibling tab's stub to it (seen-set:
same owner, same palette surface). Also persists the artistic-effects boundary fix.
"""
import json
import sys
import time
from pathlib import Path

import win32api
import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import windows as wins
import capture as cap
import depth_capture as dc
import run_step3_contextual as r3c
import run_step5_enter as s5
import repair_galleries as rg

KB = common.APP_KB
OWNER = "subfeature:wordart-text-outline"
CHART_SURF = "ui:ribbon-chart-format-text-outline-color-dropdown"
SMART_SURF = "ui:ribbon-smart-art-format-text-outline-color-dropdown"


def find_split(win, want_substr):
    for el in win.descendants():
        try:
            p = ua.read_props(el)
        except Exception:
            continue
        aid = (p.automation_id or "").lower()
        if "textoutline" in aid or ("outline" in aid and "text" in (p.name or "").lower()):
            return el, p
    return None, None


def main():
    run_id = common.make_run_id() + "-fix-textoutline"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    screen_w = win32api.GetSystemMetrics(0)
    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    result = "?"
    try:
        sess.doc.Content.InsertAfter("The quick brown fox.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = s5.DepthWalker(sess, win, writer, jrnl, screen_w)
        probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}
        # stage a chart
        probes["chart"][0](); time.sleep(0.8)
        probes["chart"][1](); time.sleep(1.0)
        for _ in range(3):
            try:
                en.select_tab(win, rg.tab_title_of(writer, "ui:ribbon-chart-format"))
                time.sleep(0.4); break
            except Exception:
                drv.press_escape(2); walker.close_all(); time.sleep(0.5)
                win = ua.attach(sess.frame); walker.win = win
        el, p = find_split(win, "textoutline")
        if el is None:
            result = "SPLIT-NOT-FOUND"
        else:
            zone = drv.zone_point(p.rect, "dropdown")
            drv.ensure_frame_foreground(sess.frame)
            before = wins.snapshot_hwnds(sess.pid)
            drv.click_point(*zone)
            new = walker.observe_new(before, floor=1500)
            if not new:
                result = "NO-FLYOUT"
            else:
                hwnd = new[0]
                data = dc.enumerate_flyout(walker.iuia, hwnd)
                img = cap.grab_rect(win32gui.GetWindowRect(hwnd))
                shot = writer.save_screenshot(img, CHART_SURF, "surface")
                children = []
                if data.get("swatches"):
                    children.append({"control_type": "swatch-grid", "label": "Color swatches",
                        "icon": {"description": "owner-drawn theme/standard color grid", "image": shot},
                        "source": "pixel", "triggers": OWNER,
                        "state_notes": f"{len(data['swatches'])} color cells (endpoint: applies the outline color)"})
                for it in data.get("items", []):
                    lab = it["label"]
                    is_ell = lab.rstrip().endswith(("...", "…")) and any(c.isalpha() for c in lab)
                    if is_ell:
                        children.append(walker.mk(it, OWNER, "opens", "ui:options-deep-option-boundary",
                            "opens the More Colors dialog (boundary)", source="hit-test"))
                    else:
                        children.append(walker.mk(it, OWNER,
                            "unexplored" if not it.get("enabled", True) else "triggers", OWNER,
                            "color command (endpoint)", source="hit-test"))
                cont = {"id": CHART_SURF, "kind": "dropdown", "label": "Text Outline color picker",
                        "screenshot": shot, "children": children, "child_containers": [],
                        "explored": True,
                        "purpose": f"the Text Outline color picker of {OWNER} — theme/standard "
                                   f"swatches (endpoints) + More Colors (boundary)"}
                walker.save(cont)
                drv.press_escape(2)
                # reference the smartart sibling stub to this surface (same owner, same palette)
                ui = writer.load_ui()
                if SMART_SURF in ui.containers:
                    for oc in ui.containers.values():
                        for ch in oc.children:
                            if ch.opens == SMART_SURF:
                                ch.opens = CHART_SURF
                                ch.state_notes = ((ch.state_notes + "; ") if ch.state_notes else "") + \
                                    "seen-set: same Text Outline color picker as Chart Format (shared owner/palette)"
                    del ui.containers[SMART_SURF]
                    writer.write_ui(ui)
                result = f"CRAWLED n={len(children)} + smartart referenced"
    finally:
        try:
            sess.close()
        except Exception:
            pass
    print("RESULT:", result)


if __name__ == "__main__":
    main()

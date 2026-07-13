"""Close the last depth-set gaps exposed by the ratio fix:
  A) 2 empty color/menu stubs -> LIVE crawl (open, enumerate real content).
  B) 1 reachable ellipsis opener (Artistic Effects Options...) -> LIVE crawl to CONFIRM it
     opens a format pane, then the 5 fragile 3-level text-effects openers are pointed at the
     run's own established `options-deep-option-boundary` by analogy + the measured Shape-Format
     precedent (identical Shadow/Glow/Reflection Options... already go to object-format-pane).
Live surfaces are all 1-level (reliable); the fragile nested cascades are NOT driven (LESSONS:
cached cascade points fail once the ribbon shifts).
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
import run_step2 as r2
import run_step3_contextual as r3c
import run_step5_enter as s5
import repair_galleries as rg

KB = common.APP_KB
BOUNDARY = "ui:options-deep-option-boundary"

# (owner element id, its host tab container, family, owner sub) — 1-level LIVE targets
LIVE = [
    ("el:ribbon-chart-format-text-outline-color", "ui:ribbon-chart-format", "chart",
     "subfeature:wordart-text-outline", "ui:ribbon-chart-format-text-outline-color-dropdown"),
    ("el:ribbon-smart-art-design-smart-art-right-to-left", "ui:ribbon-smart-art-design",
     "smartart", "subfeature:smartart-reverse",
     "ui:ribbon-smart-art-design-smart-art-right-to-left-dropdown"),
    ("el:ribbon-picture-format-picture-artistic-effects", "ui:ribbon-picture-format", "picture",
     "subfeature:picture-artistic-effects", "ui:ribbon-picture-format-picture-artistic-effects-dropdown"),
]
# text-effects ellipsis openers -> boundary (data). (container, label) each.
TEXT_EFFECTS = [
    ("ui:text-effects-dropdown-shadow", "Shadow Options..."),
    ("ui:text-effects-dropdown-reflection", "Reflection Options..."),
    ("ui:text-effects-dropdown-glow", "Glow Options..."),
    ("ui:text-effects-dropdown-outline-weight", "More Lines..."),
    ("ui:text-effects-dropdown-outline-dashes", "More Lines..."),
]


def point_at_boundary(writer, jrnl, container, label, note):
    ui = writer.load_ui()
    c = ui.containers[container]
    for ch in c.children:
        if ch.label == label and ch.triggers:
            ch.triggers = None
            ch.opens = BOUNDARY
            ch.state_notes = ((ch.state_notes + "; ") if ch.state_notes else "") + note
            writer.write_ui(ui)
            jrnl.append(common.journal_event(actor="repair.openers", action="point-boundary",
                        target=f"{container}/{label}", outcome=BOUNDARY))
            return True
    return False


def main():
    run_id = common.make_run_id() + "-repair-openers"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    screen_w = win32api.GetSystemMetrics(0)
    results = []

    # ---- B (data): 5 fragile text-effects openers -> the run's own deep-option boundary ----
    note = ("R2.4: opens the Format Text Effects pane (nth-level format sub-pane). Pointed at "
            "the run's established options-deep-option-boundary — the IDENTICAL Shadow/Glow/"
            "Reflection Options... on Shape Format were measured to open object-format-pane; "
            "this owner was breadth-only at crawl time so missed the treatment. 3-level cascade "
            "not re-driven (LESSONS: cached cascade points are fragile).")
    for cont, lab in TEXT_EFFECTS:
        ok = point_at_boundary(writer, jrnl, cont, lab, note)
        results.append((f"{cont.split('-')[-1]}/{lab}", "->boundary" if ok else "NOT-FOUND"))

    # ---- A + confirm: 3 live 1-level surfaces ----
    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="repair.openers", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"build": sess.build}))
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = s5.DepthWalker(sess, win, writer, jrnl, screen_w)
        probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}
        cur = None
        for el_id, host, fam, owner, surf_id in LIVE:
            ui = writer.load_ui()
            if surf_id in ui.containers and ui.containers[surf_id].explored \
               and ui.containers[surf_id].children:
                results.append((surf_id.split("-")[-2] + "-" + surf_id.split("-")[-1], "ALREADY"))
                continue
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
                probes[fam][0](); time.sleep(0.8)
                probes[fam][1](); time.sleep(1.0)
                cur = fam
            else:
                probes[fam][1](); time.sleep(0.5)
            tab_title = rg.tab_title_of(writer, host)
            ok = False
            for _ in range(3):
                try:
                    en.select_tab(win, tab_title); time.sleep(0.4); ok = True; break
                except Exception:
                    r3c._force_close_nonframe(sess, set()); drv.press_escape(2)
                    walker.close_all(); drv.ensure_frame_foreground(sess.frame); time.sleep(0.5)
                    from session import frame_hwnd as _fh
                    fh = _fh(sess.pid)
                    if fh:
                        sess.frame = fh
                    win = ua.attach(sess.frame); walker.win = win; time.sleep(0.4)
            if not ok:
                results.append((surf_id, "TAB-FAIL")); continue
            # resolve the opener element's live rect
            pts = s5.build_open_points_tab(win, tab_title, None,
                                           host.removeprefix("ui:") + "-" if host not in s5.TAB_TITLE else "")
            point = pts.get(el_id)
            if not point:
                # smart-art Right to Left may be a plain toggle (no dropdown) -> reclassify owner
                results.append((surf_id, "NO-POINT"));
                jrnl.append(common.journal_event(actor="repair.openers", action="no-open-point",
                            target=el_id, outcome="left for reclassify"))
                continue
            drv.ensure_frame_foreground(sess.frame)
            before = wins.snapshot_hwnds(sess.pid)
            panes_before = wins.count_docked_panes(sess.frame, screen_w)[0]
            drv.click_point(*point)
            new = walker.observe_new(before, floor=2500)
            kind = hwnd = None
            if new:
                hwnd, cls, title, rr = new
                kind = wins.classify_window(cls, title, rr)
                if kind in ("dialog", "other") and wins.is_task_pane_window(hwnd):
                    kind = "pane"
            elif wins.count_docked_panes(sess.frame, screen_w)[0] > panes_before:
                kind = "pane"
            walker.j("press-outcome", surf_id, kind or "none", opener=el_id)
            if kind == "flyout" or (new and kind not in ("dialog", "pane")):
                # color picker / small menu: enumerate owner-drawn content
                data = dc.enumerate_flyout(walker.iuia, hwnd) if hwnd else {"items": [], "swatches": [], "sections": []}
                children = []
                img = cap.grab_rect(win32gui.GetWindowRect(hwnd)) if hwnd else None
                shot = writer.save_screenshot(img, surf_id, "surface") if img is not None else None
                if data.get("swatches"):
                    children.append({"control_type": "swatch-grid", "label": "Color swatches",
                        "icon": {"description": "owner-drawn color swatch grid", "image": shot},
                        "source": "pixel", "triggers": owner,
                        "state_notes": f"{len(data['swatches'])} color cells (endpoint: applies the color)"})
                for it in data.get("items", []):
                    children.append(walker.mk(it, owner,
                        "unexplored" if not it.get("enabled", True) else "triggers", owner,
                        "menu/gallery command (endpoint)", source="hit-test"))
                cont = {"id": surf_id, "kind": "dropdown", "label": owner.split(":")[-1],
                        "screenshot": shot, "children": children or [
                            {"control_type": "note", "label": "(color picker)", "triggers": owner,
                             "icon": {"description": "color picker", "image": None},
                             "source": "measured", "state_notes": "owner-drawn color picker"}],
                        "child_containers": [], "explored": True,
                        "purpose": f"color/option picker of {owner} (endpoint tiles)"}
                walker.save(cont)
                drv.press_escape(2)
                results.append((surf_id, f"CRAWLED n={len(children)}"))
            elif kind in ("dialog", "pane"):
                # confirms an nth-level format surface -> point owner element at the boundary,
                # drop the empty stub
                ui = writer.load_ui()
                for oc in ui.containers.values():
                    for ch in oc.children:
                        if ch.opens == surf_id:
                            ch.opens = BOUNDARY
                            ch.state_notes = ((ch.state_notes + "; ") if ch.state_notes else "") + \
                                f"R2.4/R5.4: measured to open a {kind} (format options surface); " \
                                f"pointed at options-deep-option-boundary (interior is a deep pane boundary)"
                if surf_id in ui.containers:
                    del ui.containers[surf_id]
                writer.write_ui(ui)
                walker.close_all()
                results.append((surf_id, f"->boundary (opened {kind})"))
            else:
                # no surface: it's a plain toggle -> owner element becomes triggers, drop stub
                ui = writer.load_ui()
                for oc in ui.containers.values():
                    for ch in oc.children:
                        if ch.opens == surf_id:
                            ch.opens = None
                            ch.triggers = owner
                            ch.state_notes = ((ch.state_notes + "; ") if ch.state_notes else "") + \
                                "R5.4: measured — no surface opens; a direct toggle/command (endpoint)"
                if surf_id in ui.containers:
                    del ui.containers[surf_id]
                writer.write_ui(ui)
                results.append((surf_id, "toggle (no surface) -> triggers"))
    finally:
        try:
            sess.close()
        except Exception:
            pass

    print("\n==== OPENERS/STUBS RESULTS ====")
    for k, v in results:
        print(f"  {v:26} {k}")


if __name__ == "__main__":
    main()

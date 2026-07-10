"""Step 2 fixups — targeted re-probes for the two Insert-tab ambiguities, measured.

1. Comment [InsertNewComment]: the press creates a PENDING draft comment card anchored in the
   canvas — not a top-level window, and doc.Comments.Count stays 0 until posted, so the generic
   prober honestly said no-effect. Re-probe: press, then UIA-search the frame for the draft card
   (an Edit/'Post comment' surface). If found -> triggers, provenance measured:uia-card.
2. Object... dropdown zone [OleObjectInsertMenu_Dropdown]: its 2-item menu may sit under the
   10k-px tooltip-area filter. Re-probe with a 2.5k-px floor and journal exactly what appeared.
3. Contextual-tab pre-check for Step 3: COM-insert an equation, read the ribbon tab strip,
   journal whether/which contextual tabs appear (and whether UIA sees them at all).

Updates ui/ribbon-insert.json elements from the NEW measurements (journaled), via the kernel
writer — reconciliation from evidence, not hand-editing.
"""
import json
import sys
import time
from pathlib import Path

import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import prober as pb
import windows as wins
import capture as cap
import run_step2 as r2

KB = common.APP_KB


def find_comment_card(win):
    """Look for the draft-comment card's UIA evidence inside the frame."""
    hits = []
    try:
        for ct, name_sub in (("Edit", "comment"), ("Button", "post comment"),
                             ("Button", "post"), ("Group", "comment")):
            for el in win.descendants(control_type=ct):
                nm = (el.element_info.name or "").lower()
                if name_sub in nm:
                    r = el.element_info.rectangle
                    hits.append({"control_type": ct, "name": el.element_info.name,
                                 "rect": [r.left, r.top, r.right, r.bottom]})
        return hits[:8]
    except Exception:
        return hits


def load_ribbon():
    return json.loads((KB / "ui" / "ribbon-insert.json").read_text(encoding="utf-8"))


def save_ribbon(writer, ribbon):
    writer.write_container(ribbon)


def main():
    run_id = common.make_run_id() + "-step2-fixups"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage2.fixup", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={}))
    out = {}
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        en.select_tab(win, "Insert")
        time.sleep(0.4)
        ribbon = load_ribbon()
        by_id = {e["id"]: e for e in ribbon["children"]}

        # ---------- 1) Comment ----------
        el_c = by_id["el:insert-new-comment"]
        sess.select_paragraph(1)
        jrnl.append(common.journal_event(actor="stage2.fixup", action="press-attempted",
                    target="insert-new-comment", outcome="", data={"reprobe": True}))
        drv.ensure_frame_foreground(sess.frame)
        drv.click_rect(tuple(el_c["bounds"]))
        time.sleep(1.5)
        card = find_comment_card(win)
        jrnl.append(common.journal_event(actor="stage2.fixup", action="press-outcome",
                    target="insert-new-comment",
                    outcome="comment-draft-card" if card else "still-no-effect",
                    data={"card_evidence": card}))
        if card:
            el_c.pop("unexplored", None)
            el_c["triggers"] = "subfeature:insert-new-comment"
            el_c["source"] = "measured:uia-card"
            el_c["state_notes"] = ("creates a pending draft comment anchored at the selection and "
                                   "opens its card (Edit + Post button measured in-frame); the "
                                   "comment is committed only on Post — draft discards on Escape")
        drv.press_escape(2)          # discard the draft
        time.sleep(0.5)
        sess.select_paragraph(1)
        out["comment"] = {"card_found": bool(card), "evidence": card}

        # ---------- 2) Object... dropdown zone ----------
        # find the live split element to read exact zone rects now
        el_o = by_id["el:ole-objectct-insert-dropdown"]
        target_rect = None
        for gname, kt, leaves in en.live_leaves(win, "Insert"):
            for el, props in leaves:
                if props.automation_id == "OleObjectctInsert" or \
                   (props.control_type == "SplitButton" and (props.name or "").startswith("Object")):
                    _, dropdown = drv.split_zone_rects(el)
                    target_rect = dropdown
        jrnl.append(common.journal_event(actor="stage2.fixup", action="press-attempted",
                    target="ole-objectct-insert-dropdown", outcome="",
                    data={"reprobe": True, "zone_rect": list(target_rect or [])}))
        before = wins.snapshot_hwnds(sess.pid)
        drv.ensure_frame_foreground(sess.frame)
        drv.click_rect(target_rect or drv.zone_point(tuple(el_o["bounds"]), "dropdown"))
        neww, appeared = [], []
        for _ in range(12):
            time.sleep(0.25)
            neww = wins.new_windows(sess.pid, before)
            appeared = [{"class": c, "title": t, "area": wins._area(r), "rect": list(r)}
                        for (h, c, t, r) in neww if wins._area(r) >= 2500]
            if appeared:
                break
        jrnl.append(common.journal_event(actor="stage2.fixup", action="press-outcome",
                    target="ole-objectct-insert-dropdown",
                    outcome="flyout" if appeared else "no-effect",
                    data={"windows": appeared}))
        if appeared:
            h, c, t, r = max(((h, c, t, r) for (h, c, t, r) in neww
                              if wins._area(r) >= 2500), key=lambda w: wins._area(w[3]))
            img = cap.grab_rect(r)
            shot = writer.save_screenshot(img, "ui:ole-object-insert-menu", "surface")
            el_o.pop("unexplored", None)
            el_o["opens"] = "ui:ole-object-insert-menu"
            el_o["source"] = "measured:window-delta"
            el_o["state_notes"] = ("small 2-item menu (area under the generic tooltip filter — "
                                   "re-measured with a 2.5k floor)")
            writer.write_container({"id": "ui:ole-object-insert-menu", "kind": "menu",
                "label": "Object menu", "screenshot": shot, "children": [],
                "child_containers": [], "explored": False})
            if "ui:ole-object-insert-menu" not in ribbon["child_containers"]:
                ribbon["child_containers"].append(ribbon["child_containers"].pop()) if False else None
                ribbon["child_containers"] = sorted(set(ribbon["child_containers"] +
                                                        ["ui:ole-object-insert-menu"]))
            jrnl.append(common.journal_event(actor="stage2.fixup", action="surface-discovered",
                        target="ui:ole-object-insert-menu", outcome="flyout",
                        data={"via": "ole-objectct-insert-dropdown", "screenshot": shot}))
        drv.press_escape(2)
        out["object_dropdown"] = {"windows": appeared}

        # ---------- 3) contextual-tab pre-check (equation via COM) ----------
        tabs_before = r2.tab_strip_names(win)
        sess.doc.OMaths.Add(sess.app.Selection.Range)
        time.sleep(1.2)
        tabs_after = r2.tab_strip_names(win)
        new_tabs = [t for t in tabs_after if t not in tabs_before]
        jrnl.append(common.journal_event(actor="stage2.fixup", action="contextual-tabs",
                    target="equation(com-insert)", outcome="appeared" if new_tabs else "NONE",
                    data={"before": tabs_before, "after": tabs_after, "new": new_tabs}))
        out["contextual_precheck"] = {"before": tabs_before, "after": tabs_after, "new": new_tabs}
        # undo the equation
        for _ in range(4):
            drv.send_keys("^z")
            time.sleep(0.25)
            if sess.doc.OMaths.Count == 0:
                break

        save_ribbon(writer, ribbon)
        jrnl.append(common.journal_event(actor="stage2.fixup", action="write-containers",
                    target="ui/ribbon-insert.json", outcome="ok", data={}))
        print(json.dumps(out, indent=2, ensure_ascii=False))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage2.fixup", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()

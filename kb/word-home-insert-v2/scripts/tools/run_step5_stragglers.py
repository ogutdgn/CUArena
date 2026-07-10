"""Step 5 straggler fixup — re-drive the P0-P2 stubs the main depth pass could not open.

The main pass computes a split-button's dropdown-zone point ONCE per tab; for the shared
color-picker / crop split buttons that point goes stale between targets (the ribbon shifts as
the object selection changes), so the click lands on the primary zone and no flyout opens
('no-surface-appeared'). This fixup re-drives each remaining P0-P2 stub the way step 3 did and
proves works: activate the family object, RE-ENUMERATE the live split element at click time,
click its exact dropdown-child rect, and capture the owner-drawn flyout via hit-test.

Only stubs still reachable-and-explored:false from a P0-P2 node are targeted; each is matched
to the live control by its opener element id. Runs headless-serial like the main pass.
"""
import json
import sys
import time
from pathlib import Path

import win32api
import win32gui

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
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
import run_step5_enter as r5

KB = common.APP_KB


def p0p2_stubs():
    """Remaining explored:false containers reachable from a P0-P2 node, with the family + the
    opener element id that opens each (from the container's entry element)."""
    ui = json.loads((KB / "ui.json").read_text(encoding="utf-8"))["containers"]
    pri = json.loads((KB / "priority.json").read_text(encoding="utf-8"))
    p0p2 = set(pri["layers"]["P0"] + pri["layers"]["P1"] + pri["layers"]["P2"])
    ffiles = [json.loads(p.read_text(encoding="utf-8"))
              for p in sorted((KB / "features").glob("*.json"))]
    subs = {s["id"]: s for ff in ffiles for s in ff["subfeatures"]}
    el_opens = {e["id"]: e["opens"] for c in ui.values() for e in c.get("children", [])
                if e.get("id") and e.get("opens")}
    opener_of = {v: k for k, v in el_opens.items()}   # container -> opener element id

    def starts(n):
        st = set()
        if n.get("opens"):
            st.add(n["opens"])
        for tp in n.get("trigger_paths", []):
            leaf = tp["path"][-1] if tp.get("path") else None
            if leaf in el_opens:
                st.add(el_opens[leaf])
        return st

    def reach(ids):
        seen, stk = set(), list(ids)
        while stk:
            c = stk.pop()
            if c in seen:
                continue
            seen.add(c)
            cc = ui.get(c)
            if not cc:
                continue
            for e in cc.get("children", []):
                if e.get("opens"):
                    stk.append(e["opens"])
            stk += cc.get("child_containers", [])
        return seen

    stubs = {}
    for sid in [i for i in p0p2 if i.startswith("subfeature:")]:
        s = subs.get(sid)
        if not s:
            continue
        for c in reach(starts(s)):
            if ui.get(c, {}).get("explored", True) is False:
                stubs[c] = opener_of.get(c)
    return stubs, ui


FAMILY_OF = [("table", "table"), ("picture-format", "picture"), ("graphics", "svg-graphic"),
             ("shape-format", "shape"), ("smart-art", "smartart"), ("chart", "chart"),
             ("equation", "equation"), ("header", "header")]


def family_of_container(cid):
    for key, fam in FAMILY_OF:
        if key in cid:
            return fam
    return None


def main():
    stubs, ui = p0p2_stubs()
    run_id = common.make_run_id() + "-step5-stragglers"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    # group targets by family; plain (no family) handled with just the tab
    by_family = {}
    for cid, opener in stubs.items():
        if not opener:
            continue
        fam = family_of_container(cid)
        by_family.setdefault(fam, []).append((cid, opener))
    jrnl.append(common.journal_event(actor="stage5.straggler", action="run-begin",
                target="stragglers", outcome="start",
                data={"count": len(stubs), "by_family": {k: len(v) for k, v in by_family.items()}}))
    print(json.dumps({"remaining_stubs": len(stubs),
                      "by_family": {str(k): len(v) for k, v in by_family.items()}}, indent=2))

    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    walker = None
    done = []
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            sess.doc.Paragraphs(1).Range.Copy()
        except Exception:
            pass
        win = ua.attach(sess.frame)
        time.sleep(0.4)
        walker = r5.DepthWalker(sess, win, writer, jrnl, screen_w)
        probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                  in r3c.object_probes(sess, png, svg)}

        for fam, targets in by_family.items():
            # establish the family object + tab
            tab_title = None
            if fam is not None and fam in probes:
                try:
                    sess.doc.Paragraphs(1).Range.Select()
                except Exception:
                    pass
                for _ in range(10):
                    drv.send_keys("^z"); time.sleep(0.2)
                    of = sess.object_fingerprint()
                    if of.get("tables", 0) in (0, -1) and of.get("inline_shapes", 0) in (0, -1) \
                       and of.get("shapes", 0) in (0, -1):
                        break
                sess.select_paragraph(1)
                ins, sel = probes[fam]
                try:
                    ins(); time.sleep(0.6); sel(); time.sleep(1.0)
                except Exception as e:
                    jrnl.append(common.journal_event(actor="stage5.straggler",
                                action="context-setup", target=str(fam), outcome=f"error: {e}"))
                    continue
                win = ua.attach(sess.frame); walker.win = win
            # for each target, activate the right tab & re-drive the opener live
            for cid, opener in targets:
                # the hosting ribbon container = the one whose children include the opener
                host = next((hcid for hcid, hc in ui.items()
                             if any(e.get("id") == opener for e in hc.get("children", []))), None)
                tab = r5.TAB_TITLE.get(host)
                if tab is None and host:
                    tab = (ui[host].get("label") or "").replace(" (contextual tab)", "")
                if fam is not None and fam in probes:
                    try:
                        probes[fam][1](); time.sleep(0.4)
                    except Exception:
                        pass
                try:
                    en.select_tab(win, tab); time.sleep(0.4)
                except Exception as e:
                    jrnl.append(common.journal_event(actor="stage5.straggler", action="enter",
                                target=cid, outcome=f"tab-activate-failed: {e}"))
                    continue
                # RE-ENUMERATE the live split element and click its exact dropdown child rect
                drv.ensure_frame_foreground(sess.frame)
                base_open = opener.removesuffix("-dropdown")
                clicked = None
                for gname, kt, leaves in en.live_leaves(win, tab):
                    for el, props in leaves:
                        pref = host.removeprefix("ui:") + "-"
                        slug = (pref + r2.slugify(props.automation_id, props.name))[:100]
                        if f"el:{slug}" != base_open:
                            continue
                        primary, dropdown = drv.split_zone_rects(el)
                        if props.control_type == "ComboBox":
                            dropdown = en.combo_open_rect(el)
                        clicked = dropdown or drv.zone_point(props.rect, "dropdown")
                        break
                    if clicked:
                        break
                if not clicked:
                    jrnl.append(common.journal_event(actor="stage5.straggler", action="enter",
                                target=cid, outcome="opener-not-found-live", data={"opener": opener}))
                    continue
                before = wins.snapshot_hwnds(sess.pid)
                jrnl.append(common.journal_event(actor="stage5.straggler", action="press-attempted",
                            target=cid, outcome="", data={"opener": opener}))
                drv.click_target(clicked)
                new = walker.observe_new(before, floor=2500)
                if not new:
                    # owner-drawn color flyouts can render just under the floor briefly; retry lower
                    time.sleep(0.4)
                    new = walker.observe_new(before, floor=1500)
                if not new:
                    jrnl.append(common.journal_event(actor="stage5.straggler", action="enter",
                                target=cid, outcome="no-surface-appeared", data={"opener": opener}))
                    drv.press_escape(2)
                    continue
                hwnd, clsn, title, rr = new
                kind = wins.classify_window(clsn, title, rr)
                owner_node = None  # depth mk() falls back to the container's own id via triggers
                try:
                    if kind in ("flyout", "tooltip"):
                        walker.explore_flyout(hwnd, cid, cid, lambda: None, recurse=True)
                        drv.press_escape(2)
                    elif kind == "dialog":
                        walker.explore_dialog(hwnd, cid, cid, recurse=True)
                        walker.close_window(hwnd)
                    else:
                        walker.explore_flyout(hwnd, cid, cid, lambda: None, recurse=True)
                        drv.press_escape(2)
                    done.append(cid)
                except Exception as e:
                    jrnl.append(common.journal_event(actor="stage5.straggler", action="enter",
                                target=cid, outcome=f"error: {type(e).__name__}: {e}"))
                    walker.close_all()
                walker.close_all()
        print(json.dumps({"re_driven_explored": done}, indent=2))
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage5.straggler", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={"done": done}))


if __name__ == "__main__":
    main()

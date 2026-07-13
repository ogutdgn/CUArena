"""R2.5 repair — the 19 contextual in-ribbon galleries the crawl closed as endpoints
(11 wrong `triggers`) or left `unexplored` (8).

Root cause (journaled): run_step2 carried the R2.5 in-ribbon-gallery branch, the contextual
crawl path did not — the exact class the kernel's new R2.5 check now flags. This tool:

  * stages each object family (COM), activates its contextual tab,
  * finds the LIVE gallery control, presses its EXPAND zone (R2.5 three-zone rule),
  * enumerates the full flyout: tiles via UIA ListItems with an R2.8 scroll loop
    (wheel + re-enumerate until nothing new) + screenshot SERIES per segment,
  * presses the bottom commands; openers ("New Table Style…") descend into their dialogs
    via DepthWalker.explore_dialog (R5.4),
  * rewrites the ribbon element (triggers/unexplored -> opens), fills the owner
    sub-feature's behavior_record.options from the tiles (R6.3 evidence = this journal),
  * wires the pure-duplicate galleries by seen-set REFERENCE to the surface crawled once.

Resumable: an element that already carries `opens` is skipped.
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

sys.path.insert(0, str(common.REPO_ROOT))
from kernel.models import BehaviorRecord, BehaviorOption, FeatureFile

KB = common.APP_KB
MAX_SCROLL_ROUNDS = 40

# ---- worklist -------------------------------------------------------------------------
# (host container, element id, family, owner sub, new surface id)  — crawled LIVE, once per
# unique gallery type; duplicates below wire by reference.
CRAWL = [
    ("ui:ribbon-table-design", "el:ribbon-table-design-table-styles-gallery",
     "table", "subfeature:table-styles", "ui:ribbon-table-design-table-styles-flyout"),
    ("ui:ribbon-picture-format", "el:ribbon-picture-format-picture-styles-gallery",
     "picture", "subfeature:picture-style-gallery", "ui:ribbon-picture-format-picture-styles-flyout"),
    ("ui:ribbon-graphics-format", "el:ribbon-graphics-format-graphics-styles-gallery",
     "svg-graphic", "subfeature:graphics-style-gallery", "ui:ribbon-graphics-format-graphics-styles-flyout"),
    ("ui:ribbon-shape-format", "el:ribbon-shape-format-shape-styles-gallery",
     "shape", "subfeature:shape-style-gallery", "ui:ribbon-shape-format-shape-styles-flyout"),
    ("ui:ribbon-shape-format", "el:ribbon-shape-format-text-styles-gallery",
     "textbox", "subfeature:wordart-text-style-gallery", "ui:ribbon-shape-format-text-styles-flyout"),
    ("ui:ribbon-shape-format", "el:ribbon-shape-format-text-direction-gallery",
     "textbox", "subfeature:shape-text-direction", "ui:ribbon-shape-format-text-direction-flyout"),
    ("ui:ribbon-smart-art-design", "el:ribbon-smart-art-design-smart-art-layout-gallery",
     "smartart", "subfeature:smartart-layout", "ui:ribbon-smart-art-design-smart-art-layout-flyout"),
    ("ui:ribbon-smart-art-design", "el:ribbon-smart-art-design-smart-art-styles-gallery",
     "smartart", "subfeature:smartart-style", "ui:ribbon-smart-art-design-smart-art-styles-flyout"),
    ("ui:ribbon-smart-art-format", "el:ribbon-smart-art-format-shape-change-shape-gallery",
     "smartart", "subfeature:smartart-shape-edit", "ui:ribbon-smart-art-format-shape-change-shape-flyout"),
    ("ui:ribbon-chart-design", "el:ribbon-chart-design-chart-styles-gallery",
     "chart", "subfeature:chart-style", "ui:ribbon-chart-design-chart-styles-flyout"),
    ("ui:ribbon-equation", "el:ribbon-equation-equation-symbols-insert-gallery",
     "equation", "subfeature:equation-symbols", "ui:ribbon-equation-equation-symbols-flyout"),
]
# (host, element id, opens target = surface owned elsewhere, note-source)
REFERENCE = [
    ("ui:ribbon-shape-format", "el:ribbon-shape-format-shapes-insert-gallery",
     "ui:shapes-insert-dropdown", "Insert tab"),
    ("ui:ribbon-chart-format", "el:ribbon-chart-format-shapes-insert-gallery",
     "ui:shapes-insert-dropdown", "Insert tab"),
    ("ui:ribbon-chart-format", "el:ribbon-chart-format-object-rotate-gallery",
     "ui:object-rotate-dropdown", "Layout tab"),
    ("ui:ribbon-smart-art-format", "el:ribbon-smart-art-format-shape-styles-gallery",
     "ui:ribbon-shape-format-shape-styles-flyout", "Shape Format tab"),
    ("ui:ribbon-chart-format", "el:ribbon-chart-format-shape-styles-gallery",
     "ui:ribbon-shape-format-shape-styles-flyout", "Shape Format tab"),
    ("ui:ribbon-smart-art-format", "el:ribbon-smart-art-format-text-styles-gallery",
     "ui:ribbon-shape-format-text-styles-flyout", "Shape Format tab"),
    ("ui:ribbon-chart-format", "el:ribbon-chart-format-text-styles-gallery",
     "ui:ribbon-shape-format-text-styles-flyout", "Shape Format tab"),
]

_SCROLL_PARTS = {"line up", "line down", "page up", "page down", "position",
                 "vertical", "horizontal"}


def press_expand(el, props):
    """Press the gallery's expand zone. gallery_expand_rect gives a 4-tuple RECT; if absent,
    zone_point gives a 2-tuple POINT — dispatch to the matching click primitive."""
    exp = r2.gallery_expand_rect(el)
    if exp:
        drv.click_rect(tuple(exp))
        return ("rect", exp)
    pt = drv.zone_point(props.rect, "dropdown")
    drv.click_point(*pt)
    return ("point", pt)


def tab_title_of(writer, host):
    if host in s5.TAB_TITLE:
        return s5.TAB_TITLE[host]
    cont = writer.load_ui().containers.get(host)
    label = cont.label if cont else host
    return label.replace(" (contextual tab)", "")


def find_gallery_control(win, host, el_id):
    """Locate the live in-ribbon gallery control whose slug matches the stored element id."""
    want = el_id.removeprefix("el:" + host.removeprefix("ui:") + "-")
    for el in win.descendants():
        try:
            props = ua.read_props(el)
        except Exception:
            continue
        aid = props.automation_id or ""
        if "gallery" not in aid.lower():
            continue
        slug = r2.slugify(aid, props.name)
        if slug == want or want.endswith(slug) or slug.endswith(want):
            return el, props
    return None, None


def enum_tiles(popup):
    """Tile inventory of the open flyout: named ListItems (NetUI galleries expose them)."""
    tiles = {}
    try:
        for li in popup.descendants(control_type="ListItem"):
            nm = (li.element_info.name or "").strip()
            if not nm:
                continue
            r = li.element_info.rectangle
            tiles.setdefault(nm, (r.left, r.top, r.right, r.bottom))
    except Exception:
        pass
    return tiles


def enter_gallery_flyout(walker, hwnd, surf_id, owner, label, reopen, jrnl, writer):
    """Gallery-specialized flyout enterer: tiles (R2.8 scroll loop + screenshot series) +
    bottom commands (openers descend into dialogs per R5.4)."""
    popup = ua.attach(hwnd)
    time.sleep(0.3)
    rect = win32gui.GetWindowRect(hwnd)
    shots = [writer.save_screenshot(cap.grab_rect(rect), surf_id, "surface-1")]
    tiles = enum_tiles(popup)
    first_seen = dict(tiles)          # bounds valid only for the first (unscrolled) segment

    # R2.8: scroll the tile area until nothing new appears; one screenshot per segment
    scrollable = any((d.element_info.name or "").strip().lower() in _SCROLL_PARTS
                     for d in popup.descendants(control_type="Button"))
    capped = False
    if scrollable:
        from pywinauto import mouse
        cx = (rect[0] + rect[2]) // 2
        cy = (rect[1] + rect[3]) // 2
        stale = 0
        for i in range(MAX_SCROLL_ROUNDS):
            before_n = len(tiles)
            mouse.scroll(coords=(cx, cy), wheel_dist=-4)
            time.sleep(0.35)
            if not win32gui.IsWindow(hwnd) or not win32gui.IsWindowVisible(hwnd):
                break
            tiles.update(enum_tiles(popup))
            if len(tiles) > before_n:
                stale = 0
                shots.append(writer.save_screenshot(cap.grab_rect(rect), surf_id,
                                                    f"surface-{len(shots) + 1}"))
            else:
                stale += 1
                if stale >= 2:
                    break
        capped = (i + 1 >= MAX_SCROLL_ROUNDS)
    jrnl.append(common.journal_event(actor="repair.r2_5", action="scroll-enumerate",
                target=surf_id, outcome="capped" if capped else "exhausted (R2.8)",
                data={"tiles": len(tiles), "segments": len(shots),
                      "scrollable": scrollable}))

    children = []
    for nm, b in tiles.items():
        el = {"control_type": "listitem", "label": nm,
              "icon": {"description": f"'{nm}' preview tile", "image": None},
              "source": "uia", "triggers": owner,
              "state_notes": "gallery tile — applies the named item (endpoint)"}
        if nm in first_seen:
            el["bounds"] = list(first_seen[nm])
        else:
            el["state_notes"] += "; scrolled: true (bounds omitted — post-scroll)"
        children.append(el)

    # bottom commands: real MenuItems on the popup + hit-test fallback
    cmds = {}
    try:
        for mi in popup.descendants(control_type="MenuItem"):
            nm = (mi.element_info.name or "").strip()
            if nm and nm not in tiles:
                r = mi.element_info.rectangle
                cmds[nm] = {"label": nm, "control_type": "menuitem",
                            "bounds": [r.left, r.top, r.right, r.bottom],
                            "enabled": mi.is_enabled()}
    except Exception:
        pass
    if not cmds:
        try:
            data = dc.enumerate_flyout(walker.iuia, hwnd)
            for it in data["items"]:
                if it["label"] not in tiles:
                    cmds[it["label"]] = it
        except Exception:
            pass

    child_conts = []
    for nm, it in cmds.items():
        if not it.get("enabled", True):
            children.append(walker.mk(it, owner, "unexplored",
                                      note="disabled in this document state",
                                      source="hit-test"))
            continue
        if not s5._is_opener_label(nm):
            children.append(walker.mk(it, owner, "triggers", owner,
                                      "gallery menu command (endpoint)", source="uia"))
            continue
        # opener: press, expect a dialog, descend (R5.4)
        if not win32gui.IsWindowVisible(hwnd):
            hwnd = reopen()
            if not hwnd:
                children.append(walker.mk(it, owner, "unexplored",
                                          note="flyout could not be reopened for this opener",
                                          source="uia"))
                continue
        before = wins.snapshot_hwnds(walker.sess.pid)
        walker.j("press-attempted", f"{surf_id}/{nm}", "")
        drv.click_rect(tuple(it["bounds"]))
        new = walker.observe_new(before)
        if not new:
            children.append(walker.mk(it, owner, "unexplored",
                                      note="opener press produced no surface (R2.4: not an "
                                           "endpoint — press failed, journaled)", source="uia"))
            walker.j("press-outcome", f"{surf_id}/{nm}", "no-window")
            continue
        h2, cls2, t2, rr = new
        kind2 = wins.classify_window(cls2, t2, rr)
        known = walker.resolve_known(t2) if kind2 == "dialog" else None
        sub = known or s5.sub_id_for(surf_id, nm)
        walker.j("press-outcome", f"{surf_id}/{nm}", kind2, title=t2, sub_id=sub)
        if kind2 == "dialog":
            if not (known and known in walker.explored):
                walker.explore_dialog(h2, sub, owner, recurse=True, depth=1)
            walker.close_window(h2)
        else:
            walker.explore_flyout(h2, sub, owner, reopen=lambda: None, recurse=True, depth=1)
            drv.press_escape(2)
        children.append(walker.mk(it, owner, "opens", sub,
                                  f"opens a {kind2} (measured)", source="uia"))
        if sub not in child_conts:
            child_conts.append(sub)
        time.sleep(0.3)

    cont = {"id": surf_id, "kind": "dropdown", "label": label,
            "screenshot": shots[0], "screenshots": shots,
            "scrolled_to_end": (not capped),
            "children": children, "child_containers": child_conts, "explored": True,
            "purpose": f"full gallery flyout of {owner} — tiles apply items (variations); "
                       f"bottom commands descended per the depth-endpoint rule "
                       f"(R2.5 repair 2026-07-13)"}
    walker.save(cont)
    walker.j("surface-captured", surf_id, "explored",
             children=len(children), tiles=len(tiles), segments=len(shots))
    return cont, sorted(tiles)


def rewrite_element(writer, jrnl, host, el_id, surf_id, note):
    ui = writer.load_ui()
    cont = ui.containers[host]
    for ch in cont.children:
        if ch.id == el_id:
            ch.triggers = None
            ch.unexplored = False
            ch.opens = surf_id
            ch.control_type = "gallery"
            ch.state_notes = ((ch.state_notes + "; ") if ch.state_notes else "") + note
            break
    else:
        raise RuntimeError(f"{el_id} not found in {host}")
    writer.write_ui(ui)
    jrnl.append(common.journal_event(actor="repair.r2_5", action="element-rewritten",
                target=el_id, outcome=f"opens={surf_id}", data={"note": note}))


def fill_behavior_options(writer, jrnl, owner, surf_id, jref):
    """R6.3: the gallery's options = its tiles (variations). Sourced from ui.json's recorded
    flyout (single source of truth) so it is robust to crawl-time variable state."""
    ui = writer.load_ui()
    cont = ui.containers.get(surf_id)
    if not cont:
        return 0
    tile_names = [ch.label for ch in cont.children if ch.control_type == "listitem"]
    for f in sorted((KB / "features").glob("*.json")):
        ff = FeatureFile.model_validate_json(f.read_text(encoding="utf-8"))
        for s in ff.subfeatures:
            if s.id != owner:
                continue
            br = s.behavior_record or BehaviorRecord()
            br.options = [BehaviorOption(
                name=nm, found="gallery tile — applies this named style/item to the "
                               "selected object (variation of the capability)",
                evidence=[jref]) for nm in tile_names]
            br.pending = [p for p in br.pending if "gallery" not in p.lower()]
            if jref not in br.evidence:
                br.evidence.append(jref)
            s.behavior_record = br
            writer.write_feature_file(ff)
            jrnl.append(common.journal_event(actor="repair.r2_5", action="behavior-options",
                        target=owner, outcome=f"{len(tile_names)} options", data={"file": f.name}))
            return len(tile_names)
    return 0


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    run_id = common.make_run_id() + "-repair-galleries"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    jref = f"journal:{run_id}"
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))

    ui = writer.load_ui()
    def already_fixed(host, el_id):
        for ch in ui.containers[host].children:
            if ch.id == el_id:
                return bool(ch.opens)
        return False

    crawl = [t for t in CRAWL if not already_fixed(t[0], t[1])]
    if only:
        crawl = [t for t in crawl if only in t[1]]
    if not crawl:
        print("crawl worklist empty (all fixed) — doing reference wiring only")
    order = {"table": 0, "picture": 1, "svg-graphic": 2, "shape": 3, "textbox": 4,
             "smartart": 5, "chart": 6, "equation": 7}
    crawl.sort(key=lambda t: order.get(t[2], 99))

    png, svg = r3c.make_probe_png(), r3c.make_probe_svg()
    fixture = common.fresh_scratch_fixture()
    results = []
    if crawl:
        sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
        jrnl.append(common.journal_event(actor="repair.r2_5", action="launch",
                    target=f"pid={sess.pid}", outcome="ok",
                    data={"crawl": [t[1] for t in crawl], "build": sess.build,
                          "reason": "R2.5 repair: contextual crawl path lacked the "
                                    "in-ribbon-gallery branch (kernel R2.5 check findings)"}))
        try:
            sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
            sess.select_paragraph(1)
            win = ua.attach(sess.frame)
            time.sleep(0.4)
            walker = s5.DepthWalker(sess, win, writer, jrnl, screen_w)
            probes = {name: (ins, sel) for name, ins, sel, fp, cond, ownr
                      in r3c.object_probes(sess, png, svg)}
            cur_family = None
            for host, el_id, fam, owner, surf_id in crawl:
                # ---- family staging ----
                if fam != cur_family:
                    try:
                        sess.doc.Paragraphs(1).Range.Select()
                    except Exception:
                        pass
                    for _ in range(12):
                        drv.send_keys("^z")
                        time.sleep(0.25)
                        fp = sess.object_fingerprint()
                        if fp.get("tables", 0) in (0, -1) and \
                           fp.get("inline_shapes", 0) in (0, -1) and \
                           fp.get("shapes", 0) in (0, -1):
                            break
                    sess.select_paragraph(1)
                    ins, sel = probes[fam]
                    ins(); time.sleep(0.8)
                    sel(); time.sleep(1.0)
                    cur_family = fam
                    walker.j("context-setup", fam, "ok")
                else:
                    probes[fam][1]()
                    time.sleep(0.5)
                # ---- activate tab (with the stale-wrapper retry from step5) ----
                tab_title = tab_title_of(writer, host)
                activated = False
                for attempt in range(3):
                    try:
                        en.select_tab(win, tab_title)
                        time.sleep(0.4)
                        activated = True
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
                        time.sleep(0.4)
                if not activated:
                    walker.j("enter", surf_id, "tab-activate-failed")
                    results.append((el_id, "TAB-FAIL"))
                    continue
                # ---- live gallery + expand press ----
                el, props = find_gallery_control(win, host, el_id)
                if el is None:
                    walker.j("enter", surf_id, "gallery-not-found", element=el_id)
                    results.append((el_id, "NOT-FOUND"))
                    continue
                label = (props.name or el_id) + " (full gallery)"

                def reopen(tab_title=tab_title, fam=fam, host=host, el_id=el_id):
                    walker.close_all()
                    try:
                        probes[fam][1]()
                        time.sleep(0.4)
                        en.select_tab(win, tab_title)
                        time.sleep(0.4)
                    except Exception:
                        return None
                    el2, p2 = find_gallery_control(win, host, el_id)
                    if el2 is None:
                        return None
                    drv.ensure_frame_foreground(walker.sess.frame)
                    before = wins.snapshot_hwnds(walker.sess.pid)
                    press_expand(el2, p2)
                    new = walker.observe_new(before, floor=2500)
                    return new[0] if new else None

                walker.j("press-attempted", surf_id, "R2.5 expand-zone", element=el_id)
                drv.ensure_frame_foreground(sess.frame)
                before = wins.snapshot_hwnds(sess.pid)
                press_expand(el, props)
                new = walker.observe_new(before, floor=2500)
                if not new:
                    walker.j("press-outcome", surf_id, "no-flyout (honest: left unfixed)")
                    results.append((el_id, "NO-FLYOUT"))
                    continue
                hwnd = new[0]
                cont, tile_names = enter_gallery_flyout(walker, hwnd, surf_id, owner,
                                                        label, reopen, jrnl, writer)
                drv.press_escape(2)
                time.sleep(0.3)
                rewrite_element(writer, jrnl, host, el_id, surf_id,
                                "R2.5 repair 2026-07-13: in-ribbon gallery, expand zone "
                                "measured, full flyout explored")
                n_opt = fill_behavior_options(writer, jrnl, owner, surf_id, jref)
                results.append((el_id, f"OK tiles={len(tile_names)} opts={n_opt} "
                                       f"children={len(cont['children'])}"))
        finally:
            try:
                sess.close()
            except Exception:
                pass

    # ---- reference wiring (seen-set: shared surfaces, no re-crawl) ----
    ui = writer.load_ui()
    for host, el_id, target, src in REFERENCE:
        if target not in ui.containers:
            jrnl.append(common.journal_event(actor="repair.r2_5", action="reference-skip",
                        target=el_id, outcome=f"target {target} missing"))
            results.append((el_id, f"REF-SKIP ({target} missing)"))
            continue
        if already_fixed(host, el_id):
            results.append((el_id, "REF-ALREADY"))
            continue
        rewrite_element(writer, jrnl, host, el_id, target,
                        f"R2.5 repair 2026-07-13: shared gallery surface — same flyout as "
                        f"{src} (seen-set reference, not re-crawled)")
        results.append((el_id, f"REF->{target}"))
        ui = writer.load_ui()

    print("\n==== REPAIR RESULTS ====")
    for el_id, status in results:
        print(f"  {status:34} {el_id}")


if __name__ == "__main__":
    main()

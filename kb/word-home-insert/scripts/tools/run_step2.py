"""Step 2 — APP SKEL crawl: press-observe-classify every control on one universe tab.

Usage: python run_step2.py Home | python run_step2.py Insert

Scope = the HOME + INSERT tabs (this run's universe). Produces, via the kernel writers:
  * ui/main-window.json     — the frame: tab strip (Home/Insert -> their ribbon containers;
                              other tabs unexplored), File tab + QAT essentials (never-press).
  * ui/ribbon-<tab>.json    — the tab face: every measured control with exactly-one marker.
  * ui/<surface>.json       — one STUB container (explored:false) per opened dialog/flyout/pane.
  * screenshots/…           — window-true surface shots + per-control icon crops.
  * step2_coverage_<tab>.json + journal (press-attempted/press-outcome/reset-verified per zone).
Insert-tab additions vs the Home-tab run:
  * object_fingerprint deltas classify object-inserting presses (table/equation/comment/breaks);
  * the ribbon TAB STRIP is snapshotted around every press — a press that makes contextual tabs
    appear is journaled (measured contextual-trigger evidence for Step 3);
  * the crawl tab is re-selected after every probe (a contextual tab can steal activation).
Boundary groups: Home = Adobe Acrobat / Voice / Editor / Add-ins; Insert = eSignature.
"""
import json
import re
import sys
import time
from pathlib import Path

import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word-home-insert/scripts
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import prober as pb
import capture as cap
import windows as wins

# --- scope / boundaries ------------------------------------------------------
BOUNDARY_GROUPS = {
    "Home": {"Adobe Acrobat", "Voice", "Editor", "Add-ins"},
    "Insert": {"eSignature"},
}
BOUNDARY_REASON = {
    "Adobe Acrobat": "third-party COM add-in (config exclude_labels); not native Word",
    "Voice": "AI/cloud Dictate — turns on microphone / network",
    "Editor": "cloud proofing pane — network/AI (config exclude_labels)",
    "Add-ins": "Office add-in store flyout — external content",
    "eSignature": "SharePoint Syntex cloud e-signature service — network/account-gated",
}
# list-like flyouts get kind 'menu'; gallery-like get 'dropdown' (naming only; both are containers)
MENU_FLYOUTS = {"ChangeCaseGallery", "LineSpacingGallery", "BordersSelectionGallery",
                "UnderlineGallery", "SelectMenu", "MultilevelListGallery",
                "SelectMenuExcel_Dropdown", "PasteMenu_Dropdown", "DictationMenu_Dropdown",
                "FlyoutAnchorInsertPictures", "InsertLinkGallery", "OleObjectctInsert",
                "SignatureLineInsert", "Insert3DModelDefault", "HeaderFooterPageNumberInsert"}
# Real features whose effect is not fingerprintable via doc/format/object/window state.
KNOWN_NOEFFECT_FEATURES = {
    "Copy": "copies the selection to the Office clipboard",
    "FormatPainter": "copies formatting to reapply with the next click (arms a mode)",
    "ShadingColorPicker": "applies the last-used paragraph shading (fill) color to the selection",
}
_TYPE_WORDS = re.compile(r"-(dialog|gallery|picker|menu|pane|dropdown|classic|word)$")


def surface_id(stem, kind, ck):
    while _TYPE_WORDS.search(stem):
        stem = _TYPE_WORDS.sub("", stem)
    suffix = {"dialog": "dialog", "pane": "pane"}.get(kind, ck)   # ck in {menu, dropdown}
    return f"ui:{stem}-{suffix}"


def slugify(idmso, name):
    base = idmso or name or "control"
    base = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", base)      # camelCase -> camel-Case
    base = base.replace("_", "-").replace(" ", "-").replace("…", "").replace(".", "")
    base = re.sub(r"[^A-Za-z0-9-]+", "-", base)
    base = re.sub(r"-+", "-", base).strip("-").lower()
    base = re.sub(r"-word$", "", base)
    return base or "control"


def container_kind(measured_kind, base_id):
    if measured_kind == "dialog":
        return "dialog"
    if measured_kind == "pane":
        return "pane"
    return "menu" if base_id in MENU_FLYOUTS else "dropdown"


def tab_strip_names(win):
    """Current ribbon TabItem labels — contextual tabs appear/disappear here.
    CONTEXTUAL TabItems are NOT direct strip children: they nest inside a Group named
    '<family> Tools' (e.g. Group 'Table Tools' > TabItems 'Table Design','Table Layout'),
    so walk the strip's whole subtree (measured live, kb/word-home-insert debug)."""
    try:
        strip = win.child_window(title="Ribbon Tabs", control_type="Tab")
        return [t.element_info.name for t in strip.descendants(control_type="TabItem")]
    except Exception:
        return []


def contextual_tab_groups(win):
    """{tab label -> owning contextual Group name} for nested contextual TabItems."""
    out = {}
    try:
        strip = win.child_window(title="Ribbon Tabs", control_type="Tab")
        for g in strip.children():
            if g.element_info.control_type != "Group":
                continue
            for t in g.descendants(control_type="TabItem"):
                out[t.element_info.name] = g.element_info.name
    except Exception:
        pass
    return out


def make_icon(frame_img, frame_rect, rect, writer, ribbon_id, node_slug, label):
    crop = cap.crop_from(frame_img, rect, frame_rect)
    image = None
    if cap.quality_ok(crop):
        image = writer.save_screenshot(crop, ribbon_id, f"icon-{node_slug}")
    return {"description": f"{label} control (see icon crop)", "image": image}


def _surface_screenshot(sess, kind, detail, writer, slug):
    try:
        if kind in ("dialog", "flyout") and detail.get("rect"):
            img = cap.grab_rect(detail["rect"])
        else:  # pane / other: grab the frame (pane is docked inside)
            img, _ = cap.grab_window(sess.frame)
        return writer.save_screenshot(img, f"ui:{slug}", "surface"), [img.width, img.height]
    except Exception:
        return None, None


def probe_one(ctx, el, props, click_rect, node_slug, label, tooltip, shortcut, keytip,
              override_surface_id=None, surface_stem=None):
    """Press one control-zone, classify, build a UIElement dict, stub any opened surface."""
    sess, jrnl, writer = ctx["sess"], ctx["jrnl"], ctx["writer"]
    surface_stem = surface_stem or node_slug
    sess.select_paragraph(1)
    baseline = pb.snapshot(sess, ctx["screen_w"])
    tabs_before = tab_strip_names(ctx["win"])
    jrnl.append(common.journal_event(actor="stage2.probe", action="press-attempted",
                target=node_slug, outcome="", data={"rect": list(click_rect), "label": label,
                                                    "tab": ctx["tab"]}))
    drv.ensure_frame_foreground(sess.frame)
    pt = drv.click_rect(click_rect)
    neww = pb.observe(sess, baseline["hwnds"])
    sess.select_paragraph(1)
    after = pb.snapshot(sess, ctx["screen_w"])
    kind, detail = pb.classify(baseline, after, neww)
    tabs_after = tab_strip_names(ctx["win"])
    ctx_tabs = [t for t in tabs_after if t not in tabs_before]
    if ctx_tabs:
        detail["contextual_tabs_appeared"] = ctx_tabs
        jrnl.append(common.journal_event(actor="stage2.probe", action="contextual-tabs",
                    target=node_slug, outcome="appeared", data={"tabs": ctx_tabs}))

    # a floating task pane reads as a dialog by class — reclassify by its 'Close pane' button
    if kind == "dialog" and detail.get("hwnd") and wins.is_task_pane_window(detail["hwnd"]):
        kind = "pane"
        detail["floating"] = True

    icon = make_icon(ctx["frame_img"], ctx["frame_rect"], tuple(props.rect), writer,
                     ctx["ribbon_id"], node_slug, label)
    elem = {"id": f"el:{node_slug}", "control_type": props.control_type.lower(),
            "label": label, "icon": icon, "tooltip": tooltip or None,
            "shortcut": shortcut or None,
            "location": f"ui:main-window > {ctx['ribbon_id']}",
            "bounds": list(props.rect), "source": "measured",
            "state_notes": (f"keytip {keytip}" if keytip else None)}

    if kind in ("dialog", "flyout", "pane"):
        ck = container_kind(kind, props.automation_id)
        surf_id = override_surface_id or surface_id(surface_stem, kind, ck)
        elem["opens"] = surf_id
        elem["source"] = "measured:window-delta" if kind != "pane" else "measured:pane-inset"
        shot, size = _surface_screenshot(sess, kind, detail, writer, surf_id.removeprefix("ui:"))
        if surf_id not in ctx["seen_surfaces"]:
            ctx["stub_containers"][surf_id] = {
                "id": surf_id, "kind": ck, "label": detail.get("title") or label,
                "screenshot": shot, "children": [], "child_containers": [],
                "explored": False,
            }
            ctx["seen_surfaces"].add(surf_id)
            jrnl.append(common.journal_event(actor="stage2.probe", action="surface-discovered",
                        target=surf_id, outcome=kind,
                        data={"via": node_slug, "class": detail.get("class"),
                              "title": detail.get("title"), "screenshot": shot, "size": size}))
        elif shot and not ctx["stub_containers"].get(surf_id, {}).get("screenshot"):
            ctx["stub_containers"][surf_id]["screenshot"] = shot
    elif kind == "feature":
        elem["triggers"] = f"subfeature:{node_slug}"
        elem["source"] = "measured:state-delta"
        notes = f"state changed: {detail.get('state_changed')}"
        if ctx_tabs:
            notes += f"; contextual tabs appeared: {ctx_tabs}"
        elem["state_notes"] = notes + (f"; keytip {keytip}" if keytip else "")
    elif kind == "no-effect" and props.automation_id in KNOWN_NOEFFECT_FEATURES:
        elem["triggers"] = f"subfeature:{node_slug}"
        elem["source"] = "idmso"
        elem["state_notes"] = (f"feature by idMso '{props.automation_id}': "
                               f"{KNOWN_NOEFFECT_FEATURES[props.automation_id]}; "
                               f"effect not fingerprintable (clipboard/mode)")
    else:  # no-effect
        elem["unexplored"] = True
        elem["state_notes"] = "pressed: no observable effect (see journal)"

    reset_ok, notes = pb.restore(sess, kind, detail, pt, baseline, ctx["screen_w"])
    # a press may have activated a contextual tab or otherwise stolen ribbon activation —
    # put the crawl tab back before the next control (stored rects assume its geometry)
    try:
        en.select_tab(ctx["win"], ctx["tab"])
    except Exception:
        pass
    jrnl.append(common.journal_event(actor="stage2.probe", action="press-outcome",
                target=node_slug, outcome=kind,
                data={"detail": {k: v for k, v in detail.items() if k != "hwnd"},
                      "marker": ("opens:" + elem.get("opens", "")) if elem.get("opens")
                      else ("triggers:" + elem.get("triggers", "")) if elem.get("triggers")
                      else "unexplored"}))
    jrnl.append(common.journal_event(actor="stage2.probe", action="reset-verified",
                target=node_slug, outcome="ok" if reset_ok else "MISMATCH", data={"notes": notes}))
    return elem, reset_ok, kind


def boundary_element(ctx, props, label, tooltip, shortcut, group):
    node_slug = slugify(props.automation_id, label)
    icon = make_icon(ctx["frame_img"], ctx["frame_rect"], tuple(props.rect), ctx["writer"],
                     ctx["ribbon_id"], node_slug, label)
    ctx["jrnl"].append(common.journal_event(actor="stage2.boundary", action="boundary",
                target=node_slug, outcome="skipped",
                data={"group": group, "reason": BOUNDARY_REASON.get(group, "boundary")}))
    return {"id": f"el:{node_slug}", "control_type": props.control_type.lower(), "label": label,
            "icon": icon, "tooltip": tooltip or None, "shortcut": shortcut or None,
            "location": f"ui:main-window > {ctx['ribbon_id']}", "bounds": list(props.rect),
            "source": "uia", "unexplored": True,
            "state_notes": f"boundary (not pressed): {BOUNDARY_REASON.get(group, '')}"}


def build_main_window(win, writer, frame_img, frame_rect):
    """The frame: tab strip (Home+Insert in scope; others unexplored), File + QAT chrome."""
    children = []
    IN_SCOPE = {"Home": "ui:ribbon-home", "Insert": "ui:ribbon-insert"}
    try:
        strip = win.child_window(title="Ribbon Tabs", control_type="Tab")
        for t in strip.children():
            ei = t.element_info
            if ei.control_type != "TabItem":
                continue
            r = ei.rectangle
            rect = (r.left, r.top, r.right, r.bottom)
            label = ei.name
            slug = slugify(ei.automation_id, label)
            icon = {"description": f"{label} ribbon tab", "image": None}
            el = {"id": f"el:tab-{slug}", "control_type": "tab", "label": label, "icon": icon,
                  "tooltip": None, "location": "ui:main-window",
                  "bounds": list(rect), "source": "uia"}
            if label in IN_SCOPE:
                el["opens"] = IN_SCOPE[label]
                el["state_notes"] = "in-scope universe tab"
            else:
                el["unexplored"] = True
                el["state_notes"] = "other ribbon tab — out of scope this run (name only)"
            children.append(el)
    except Exception:
        pass
    try:
        ft = win.child_window(auto_id="FileTabButton")
        if ft.exists(timeout=1):
            r = ft.element_info.rectangle
            children.append({"id": "el:file-tab", "control_type": "button", "label": "File",
                             "icon": {"description": "File tab (opens Backstage)", "image": None},
                             "tooltip": None, "location": "ui:main-window",
                             "bounds": [r.left, r.top, r.right, r.bottom], "source": "uia",
                             "unexplored": True,
                             "state_notes": "boundary: opens Backstage (out of scope)"})
    except Exception:
        pass
    try:
        qat = win.child_window(title="Quick Access Toolbar", control_type="ToolBar")
        for b in qat.children():
            ei = b.element_info
            if ei.control_type not in ("Button", "SplitButton"):
                continue
            r = ei.rectangle
            slug = slugify(ei.automation_id, ei.name)
            children.append({"id": f"el:qat-{slug}", "control_type": ei.control_type.lower(),
                             "label": ei.name,
                             "icon": {"description": f"{ei.name} (Quick Access Toolbar)",
                                      "image": None},
                             "tooltip": None, "location": "ui:main-window",
                             "bounds": [r.left, r.top, r.right, r.bottom], "source": "uia",
                             "unexplored": True,
                             "state_notes": "persistent chrome — out of scope; never pressed "
                                            "(Save/AutoSave are never-press by law)"})
    except Exception:
        pass
    return {"id": "ui:main-window", "kind": "window", "label": "Word main window (frame)",
            "screenshot": None, "children": children,
            "child_containers": ["ui:ribbon-home", "ui:ribbon-insert"]}


def main():
    tab = sys.argv[1] if len(sys.argv) > 1 else "Home"
    assert tab in ("Home", "Insert"), "tab must be Home or Insert"
    ribbon_id = f"ui:ribbon-{tab.lower()}"
    run_id = common.make_run_id() + f"-step2-{tab.lower()}"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((common.APP_KB / "version.json").read_text(encoding="utf-8"))
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(actor="stage2", action="run-begin", target="run_step2",
                outcome="start", data={"run_id": run_id, "tab": tab}))
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage2", action="launch", target=f"pid={sess.pid}",
                outcome="ok", data={"build": sess.build}))
    coverage = {"measured": [], "boundary": [], "no_effect": [], "reset_mismatch": [],
                "contextual_tabs": {}}
    try:
        # a real, RICHLY-FORMATTED selection so formatting features produce a measurable delta,
        # text so text-gated Insert controls (Drop Cap) enable, and an armed clipboard for Paste.
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            f = sess.app.Selection.Font
            f.Bold = True; f.Italic = True; f.Underline = True
            f.Size = 14; f.Color = 255            # red
            sess.app.Selection.ParagraphFormat.LeftIndent = 36
            sess.doc.Paragraphs(1).Range.Copy()   # arm clipboard
        except Exception:
            pass
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        en.select_tab(win, tab)
        time.sleep(0.3)

        # window-true frame shot (source for icon crops) + ribbon band
        drv.ensure_frame_foreground(sess.frame)
        time.sleep(0.3)
        frame_img, frame_rect = cap.grab_window(sess.frame)
        ribbon_shot = writer.save_screenshot(frame_img.crop((0, 0, frame_img.width, 200)),
                                             ribbon_id, "surface")

        ctx = {"sess": sess, "jrnl": jrnl, "writer": writer, "win": win, "tab": tab,
               "ribbon_id": ribbon_id, "screen_w": screen_w,
               "frame_img": frame_img, "frame_rect": frame_rect,
               "seen_surfaces": set(), "stub_containers": {}}

        groups = en.live_leaves(win, tab)
        children = []

        for gname, gkeytip, leaves in groups:
            if gname in BOUNDARY_GROUPS[tab]:
                for el, props in leaves:
                    label = props.name or props.automation_id
                    children.append(boundary_element(ctx, props, label, props.tooltip,
                                                     props.accelerator_key, gname))
                    coverage["boundary"].append(f"{gname}:{label}")
                continue
            for el, props in leaves:
                label = props.name or props.automation_id or "?"
                ct = props.control_type
                base_slug = slugify(props.automation_id, label)
                if not props.is_enabled:
                    # journal honestly; a disabled control cannot be pressed
                    icon = make_icon(frame_img, frame_rect, tuple(props.rect), writer,
                                     ribbon_id, base_slug, label)
                    children.append({"id": f"el:{base_slug}", "control_type": ct.lower(),
                        "label": label, "icon": icon, "tooltip": props.tooltip or None,
                        "shortcut": props.accelerator_key or None,
                        "location": f"ui:main-window > {ribbon_id}",
                        "bounds": list(props.rect), "source": "uia", "unexplored": True,
                        "state_notes": "disabled in the fixture state — not pressable (journaled)"})
                    jrnl.append(common.journal_event(actor="stage2.probe", action="press-skipped",
                                target=base_slug, outcome="disabled", data={"label": label}))
                    coverage["measured"].append(f"{base_slug}[disabled]")
                    continue
                if ct == "SplitButton":
                    primary, dropdown = drv.split_zone_rects(el)
                    elem, ok, kind = probe_one(ctx, el, props,
                        primary or drv.zone_point(props.rect, "primary"),
                        base_slug, label, props.tooltip, props.accelerator_key, props.access_key)
                    children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                    if kind == "no-effect":
                        coverage["no_effect"].append(base_slug)
                    d_slug = base_slug + "-dropdown"
                    elem2, ok2, kind2 = probe_one(ctx, el, props,
                        dropdown or drv.zone_point(props.rect, "dropdown"),
                        d_slug, f"{label} (dropdown)", props.tooltip, None, props.access_key,
                        surface_stem=base_slug)
                    children.append(elem2)
                    coverage["measured"].append(f"{d_slug}[{kind2}]")
                    if not ok2:
                        coverage["reset_mismatch"].append(d_slug)
                elif ct == "ComboBox":
                    open_rect = en.combo_open_rect(el) or drv.zone_point(props.rect, "dropdown")
                    elem, ok, kind = probe_one(ctx, el, props, open_rect, base_slug, label,
                        props.tooltip, props.accelerator_key, props.access_key)
                    children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                elif gname == "Styles" and ct == "Button" and label == "Styles":
                    elem, ok, kind = probe_one(ctx, el, props, tuple(props.rect),
                        "styles-more", "Quick Styles More", props.tooltip, None, props.access_key,
                        override_surface_id="ui:styles-gallery")
                    children.append(elem)
                    coverage["measured"].append(f"styles-more[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append("styles-more")
                elif props.automation_id == "QuickStylesGallery":
                    icon = make_icon(frame_img, frame_rect, tuple(props.rect), writer,
                                     ribbon_id, "quick-styles", label)
                    children.append({"id": "el:quick-styles-gallery", "control_type": "gallery",
                        "label": "Quick Styles gallery", "icon": icon,
                        "tooltip": props.tooltip or None,
                        "location": f"ui:main-window > {ribbon_id}", "bounds": list(props.rect),
                        "source": "uia", "opens": "ui:styles-gallery",
                        "state_notes": "inline QuickStyles strip; expansion surface measured via "
                                       "the group's More button"})
                    if "ui:styles-gallery" not in ctx["seen_surfaces"]:
                        ctx["stub_containers"]["ui:styles-gallery"] = {"id": "ui:styles-gallery",
                            "kind": "dropdown", "label": "Quick Styles gallery", "screenshot": None,
                            "children": [], "child_containers": [], "explored": False}
                        ctx["seen_surfaces"].add("ui:styles-gallery")
                    coverage["measured"].append("quick-styles-gallery[gallery]")
                else:
                    elem, ok, kind = probe_one(ctx, el, props, tuple(props.rect), base_slug,
                        label, props.tooltip, props.accelerator_key, props.access_key)
                    children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                    if kind == "no-effect":
                        coverage["no_effect"].append(base_slug)

        # collect contextual-tab evidence from this run's journal into coverage
        # (probe_one journals each; summarize from stub side-channel)
        ribbon = {"id": ribbon_id, "kind": "tab", "label": f"{tab} tab",
                  "screenshot": ribbon_shot, "children": children,
                  "child_containers": sorted(ctx["seen_surfaces"])}
        main_window = build_main_window(win, writer, frame_img, frame_rect)
        writer.write_container(main_window)
        writer.write_container(ribbon)
        for sid, c in ctx["stub_containers"].items():
            writer.write_container(c)
        jrnl.append(common.journal_event(actor="stage2", action="write-containers", target="ui/*",
                    outcome="ok", data={"ribbon_children": len(children),
                                        "stubs": sorted(ctx["stub_containers"].keys()),
                                        "main_window_children": len(main_window["children"])}))

        note = {
            "scope": f"{tab} tab of the Home+Insert universe",
            "boundary_groups": {g: BOUNDARY_REASON[g] for g in BOUNDARY_GROUPS[tab]},
            "counts": {"controls": len(children),
                       "measured": len(coverage["measured"]),
                       "boundary_controls": len(coverage["boundary"]),
                       "opened_surfaces_stubbed": len(ctx["stub_containers"]),
                       "no_effect": len(coverage["no_effect"]),
                       "reset_mismatch": len(coverage["reset_mismatch"])},
            "no_effect_controls": coverage["no_effect"],
            "reset_mismatch_controls": coverage["reset_mismatch"],
            "measured_controls": coverage["measured"],
            "stub_surfaces": sorted(ctx["stub_containers"].keys()),
        }
        (common.APP_KB / f"step2_coverage_{tab.lower()}.json").write_text(
            json.dumps(note, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(note["counts"], indent=2))
        print("reset_mismatch:", coverage["reset_mismatch"])
        print("no_effect:", coverage["no_effect"])
    finally:
        sess.close()
        jrnl.append(common.journal_event(actor="stage2", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed", data={}))


if __name__ == "__main__":
    main()

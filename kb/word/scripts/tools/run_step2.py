"""Step 2 — APP SKEL crawl: press-observe-classify every Home-tab control, measured.

Scope = the Home tab as the whole app. Produces, via the kernel writers:
  * ui/main-window.json   — the frame: tab strip (Home -> ribbon-home; other tabs unexplored),
                            File tab + QAT essentials (unexplored, out-of-scope/never-press).
  * ui/ribbon-home.json   — the Home tab face: every measured control with exactly-one marker.
  * ui/<surface>.json     — one STUB container (explored:false) per opened dialog/flyout/pane.
  * screenshots/…         — window-true surface shots + per-control icon crops.
  * coverage note + journal (press-attempted / press-outcome / reset-verified per control).
Add-in / AI groups are boundaries (journaled, control marked unexplored, never pressed).
"""
import json
import re
import sys
import time
from pathlib import Path

import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # kb/word/scripts
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import prober as pb
import capture as cap
import windows as wins

# --- scope / boundaries ------------------------------------------------------
CORE_GROUPS = {"Clipboard", "Font", "Paragraph", "Styles", "Editing"}
BOUNDARY_GROUPS = {"Adobe Acrobat", "Voice", "Editor", "Add-ins"}
BOUNDARY_REASON = {
    "Adobe Acrobat": "third-party COM add-in (config exclude_labels); not native Word",
    "Voice": "AI/cloud Dictate — turns on microphone / network (reference D8)",
    "Editor": "cloud proofing pane — network/AI (config exclude_labels)",
    "Add-ins": "Office add-in store flyout — external content (reference D8)",
}
MENU_FLYOUTS = {"ChangeCaseGallery", "LineSpacingGallery", "BordersSelectionGallery",
                "UnderlineGallery", "SelectMenu", "MultilevelListGallery",
                "SelectMenuExcel_Dropdown", "PasteMenu_Dropdown", "DictationMenu_Dropdown"}
# Real features whose effect is not fingerprintable via doc/format/window state (clipboard, or an
# armed mode). Measured as 'no-effect'; marked triggers with idMso provenance, not a state delta.
KNOWN_NOEFFECT_FEATURES = {
    "Copy": "copies the selection to the Office clipboard",
    "FormatPainter": "copies formatting to reapply with the next click (arms a mode)",
    "ShadingColorPicker": "applies the last-used paragraph shading (fill) color to the selection",
}
# surface-type words baked into idMso slugs — stripped so ui: ids don't double the type suffix
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
    base = re.sub(r"-+", "-", base).strip("-").lower()
    base = re.sub(r"-word$", "", base)
    return base or "control"


def container_kind(measured_kind, base_id):
    if measured_kind == "dialog":
        return "dialog"
    if measured_kind == "pane":
        return "pane"
    return "menu" if base_id in MENU_FLYOUTS else "dropdown"


def make_icon(frame_img, frame_rect, rect, writer, node_slug, label):
    crop = cap.crop_from(frame_img, rect, frame_rect)
    image = None
    if cap.quality_ok(crop):
        image = writer.save_screenshot(crop, f"ui:ribbon-home", f"icon-{node_slug}")
    return {"description": f"{label} control (see icon crop)", "image": image}


def _surface_screenshot(sess, kind, detail, writer, slug):
    """Grab a window-true shot of the opened surface (frame for panes) and return rel path."""
    try:
        if kind in ("dialog", "flyout") and detail.get("rect"):
            img = cap.grab_rect(detail["rect"])
        else:  # pane / other: grab the frame (pane is docked inside)
            img, _ = cap.grab_window(sess.frame)
        return writer.save_screenshot(img, f"ui:{slug}", "surface"), [img.width, img.height]
    except Exception:
        return None, None


def probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
              el, props, click_rect, node_slug, label, tooltip, shortcut, keytip,
              seen_surfaces, stub_containers, override_surface_id=None, surface_stem=None):
    """Press one control-zone, classify, build a UIElement dict, stub any opened surface."""
    surface_stem = surface_stem or node_slug
    sess.select_paragraph(1)
    baseline = pb.snapshot(sess, screen_w)
    jrnl.append(common.journal_event(actor="stage2.probe", action="press-attempted",
                target=node_slug, outcome="", data={"rect": list(click_rect), "label": label}))
    drv.ensure_frame_foreground(sess.frame)
    pt = drv.click_rect(click_rect)
    neww = pb.observe(sess, baseline["hwnds"])
    sess.select_paragraph(1)
    after = pb.snapshot(sess, screen_w)
    kind, detail = pb.classify(baseline, after, neww)

    # a floating task pane (Styles pane) reads as a dialog by class — reclassify by its 'Close
    # pane' button so its marker and reset are correct.
    if kind == "dialog" and detail.get("hwnd") and wins.is_task_pane_window(detail["hwnd"]):
        kind = "pane"
        detail["floating"] = True

    icon = make_icon(frame_img, frame_rect, tuple(props.rect), writer, node_slug, label)
    elem = {"id": f"el:{node_slug}", "control_type": props.control_type.lower(),
            "label": label, "icon": icon, "tooltip": tooltip or None,
            "shortcut": shortcut or None,
            "location": "ui:main-window > ui:ribbon-home",
            "bounds": list(props.rect), "source": "measured",
            "state_notes": (f"keytip {keytip}" if keytip else None)}

    if kind in ("dialog", "flyout", "pane"):
        ck = container_kind(kind, props.automation_id)
        surf_id = override_surface_id or surface_id(surface_stem, kind, ck)
        elem["opens"] = surf_id
        elem["source"] = "measured:window-delta" if kind != "pane" else "measured:pane-inset"
        shot, size = _surface_screenshot(sess, kind, detail, writer, surf_id.removeprefix("ui:"))
        if surf_id not in seen_surfaces:
            stub_containers[surf_id] = {
                "id": surf_id, "kind": ck, "label": detail.get("title") or label,
                "screenshot": shot, "children": [], "child_containers": [],
                "explored": False,
            }
            seen_surfaces.add(surf_id)
            jrnl.append(common.journal_event(actor="stage2.probe", action="surface-discovered",
                        target=surf_id, outcome=kind,
                        data={"via": node_slug, "class": detail.get("class"),
                              "title": detail.get("title"), "screenshot": shot, "size": size}))
        elif shot and not stub_containers.get(surf_id, {}).get("screenshot"):
            stub_containers[surf_id]["screenshot"] = shot   # fill a previously-empty stub shot
    elif kind == "feature":
        elem["triggers"] = f"subfeature:{node_slug}"
        elem["source"] = "measured:state-delta"
        elem["state_notes"] = f"state changed: {detail.get('state_changed')}" + \
                              (f"; keytip {keytip}" if keytip else "")
    elif kind == "no-effect" and props.automation_id in KNOWN_NOEFFECT_FEATURES:
        # a real feature whose effect is un-fingerprintable (clipboard / armed mode). Marker is
        # triggers, but provenance is the app's own command id (idMso), not a state measurement.
        elem["triggers"] = f"subfeature:{node_slug}"
        elem["source"] = "idmso"
        elem["state_notes"] = (f"feature by idMso '{props.automation_id}': "
                               f"{KNOWN_NOEFFECT_FEATURES[props.automation_id]}; "
                               f"effect not fingerprintable (clipboard/mode)")
    else:  # no-effect
        elem["unexplored"] = True
        elem["state_notes"] = "pressed: no observable effect (see journal)"

    reset_ok, notes = pb.restore(sess, kind, detail, pt, baseline, screen_w)
    jrnl.append(common.journal_event(actor="stage2.probe", action="press-outcome",
                target=node_slug, outcome=kind,
                data={"detail": detail, "marker": ("opens:" + elem.get("opens", "")) if elem.get("opens")
                      else ("triggers:" + elem.get("triggers", "")) if elem.get("triggers") else "unexplored"}))
    jrnl.append(common.journal_event(actor="stage2.probe", action="reset-verified",
                target=node_slug, outcome="ok" if reset_ok else "MISMATCH", data={"notes": notes}))
    return elem, reset_ok, kind


def boundary_element(frame_img, frame_rect, writer, props, label, tooltip, shortcut, group, jrnl):
    node_slug = slugify(props.automation_id, label)
    icon = make_icon(frame_img, frame_rect, tuple(props.rect), writer, node_slug, label)
    jrnl.append(common.journal_event(actor="stage2.boundary", action="boundary",
                target=node_slug, outcome="skipped",
                data={"group": group, "reason": BOUNDARY_REASON.get(group, "boundary")}))
    return {"id": f"el:{node_slug}", "control_type": props.control_type.lower(), "label": label,
            "icon": icon, "tooltip": tooltip or None, "shortcut": shortcut or None,
            "location": "ui:main-window > ui:ribbon-home", "bounds": list(props.rect),
            "source": "uia", "unexplored": True,
            "state_notes": f"boundary (not pressed): {BOUNDARY_REASON.get(group,'')}"}


def build_main_window(win, writer, frame_img, frame_rect):
    """The frame: tab strip (Home -> ribbon-home; other tabs unexplored) + File + QAT essentials."""
    children = []
    # tab strip
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
            if label == "Home":
                el["opens"] = "ui:ribbon-home"
                el["state_notes"] = "the in-scope universe"
            else:
                el["unexplored"] = True
                el["state_notes"] = "other ribbon tab — out of scope this run (name only)"
            children.append(el)
    except Exception:
        pass
    # File tab (backstage) — boundary
    try:
        ft = win.child_window(auto_id="FileTabButton")
        if ft.exists(timeout=1):
            r = ft.element_info.rectangle
            children.append({"id": "el:file-tab", "control_type": "button", "label": "File",
                             "icon": {"description": "File tab (opens Backstage)", "image": None},
                             "tooltip": None, "location": "ui:main-window",
                             "bounds": [r.left, r.top, r.right, r.bottom], "source": "uia",
                             "unexplored": True, "state_notes": "boundary: opens Backstage (out of scope)"})
    except Exception:
        pass
    # QAT essentials — never press Save; list as unexplored chrome
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
                             "icon": {"description": f"{ei.name} (Quick Access Toolbar)", "image": None},
                             "tooltip": None, "location": "ui:main-window",
                             "bounds": [r.left, r.top, r.right, r.bottom], "source": "uia",
                             "unexplored": True,
                             "state_notes": "persistent chrome — out of Home-tab scope; never pressed"})
    except Exception:
        pass
    return {"id": "ui:main-window", "kind": "window", "label": "Word main window (frame)",
            "screenshot": None, "children": children, "child_containers": ["ui:ribbon-home"]}


def main():
    run_id = common.make_run_id() + "-step2"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    fixture = common.fresh_scratch_fixture()
    jrnl.append(common.journal_event(actor="stage2", action="run-begin", target="run_step2",
                outcome="start", data={"run_id": run_id}))
    sess = WordSession.start(fixture, expected_build="16.0.20131")
    jrnl.append(common.journal_event(actor="stage2", action="launch", target=f"pid={sess.pid}",
                outcome="ok", data={"build": sess.build}))
    coverage = {"measured": [], "boundary": [], "no_effect": [], "reset_mismatch": []}
    try:
        # prepare a real, RICHLY-FORMATTED selection so formatting features (Bold toggle off,
        # Clear Formatting, etc.) produce a measurable delta — and arm the clipboard for Paste.
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        try:
            f = sess.app.Selection.Font
            f.Bold = True; f.Italic = True; f.Underline = True
            f.Size = 14; f.Color = 255            # red
            sess.app.Selection.ParagraphFormat.LeftIndent = 36   # 0.5in so Decrease Indent registers
            sess.doc.Paragraphs(1).Range.Copy()   # arm clipboard
        except Exception:
            pass
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)

        # window-true frame shot (source for icon crops) + ribbon band
        drv.ensure_frame_foreground(sess.frame)
        time.sleep(0.3)
        frame_img, frame_rect = cap.grab_window(sess.frame)
        ribbon_shot = writer.save_screenshot(frame_img.crop((0, 0, frame_img.width, 200)),
                                             "ui:ribbon-home", "surface")

        groups = en.live_leaves(win, "Home")
        home_children = []
        seen_surfaces = set()
        stub_containers = {}

        for gname, gkeytip, leaves in groups:
            if gname in BOUNDARY_GROUPS:
                for el, props in leaves:
                    label = props.name or props.automation_id
                    home_children.append(boundary_element(frame_img, frame_rect, writer, props,
                                         label, props.tooltip, props.accelerator_key, gname, jrnl))
                    coverage["boundary"].append(f"{gname}:{label}")
                continue
            for el, props in leaves:
                label = props.name or props.automation_id or "?"
                ct = props.control_type
                base_slug = slugify(props.automation_id, label)
                # decide the zones to press
                if ct == "SplitButton":
                    primary, dropdown = drv.split_zone_rects(el)
                    # PRIMARY zone
                    elem, ok, kind = probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
                        el, props, primary or drv.zone_point(props.rect, "primary"),
                        base_slug, label, props.tooltip, props.accelerator_key, props.access_key,
                        seen_surfaces, stub_containers)
                    home_children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                    if kind == "no-effect":
                        coverage["no_effect"].append(base_slug)
                    # DROPDOWN zone -> its own element/surface
                    d_slug = base_slug + "-dropdown"
                    elem2, ok2, kind2 = probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
                        el, props, dropdown or drv.zone_point(props.rect, "dropdown"),
                        d_slug, f"{label} (dropdown)", props.tooltip, None, props.access_key,
                        seen_surfaces, stub_containers, surface_stem=base_slug)
                    home_children.append(elem2)
                    coverage["measured"].append(f"{d_slug}[{kind2}]")
                    if not ok2:
                        coverage["reset_mismatch"].append(d_slug)
                elif ct == "ComboBox":
                    open_rect = en.combo_open_rect(el) or drv.zone_point(props.rect, "dropdown")
                    elem, ok, kind = probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
                        el, props, open_rect, base_slug, label, props.tooltip,
                        props.accelerator_key, props.access_key, seen_surfaces, stub_containers)
                    home_children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                elif gname == "Styles" and ct == "Button" and label == "Styles":
                    # the QuickStyles 'More' button — opens the SAME expanded gallery as the
                    # inline strip; measure it and route to the shared ui:styles-gallery surface.
                    elem, ok, kind = probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
                        el, props, tuple(props.rect), "styles-more", "Quick Styles More",
                        props.tooltip, None, props.access_key, seen_surfaces, stub_containers,
                        override_surface_id="ui:styles-gallery")
                    home_children.append(elem)
                    coverage["measured"].append(f"styles-more[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append("styles-more")
                elif props.automation_id == "QuickStylesGallery":
                    # do NOT press the inline gallery (a center press applies a style); its surface
                    # is measured via the group's 'Styles' more-button below.
                    icon = make_icon(frame_img, frame_rect, tuple(props.rect), writer, "quick-styles", label)
                    home_children.append({"id": "el:quick-styles-gallery", "control_type": "gallery",
                        "label": "Quick Styles gallery", "icon": icon, "tooltip": props.tooltip or None,
                        "location": "ui:main-window > ui:ribbon-home", "bounds": list(props.rect),
                        "source": "uia", "opens": "ui:styles-gallery",
                        "state_notes": "inline QuickStyles strip; expansion surface measured via More (Alt+H+L)"})
                    if "ui:styles-gallery" not in seen_surfaces:
                        stub_containers["ui:styles-gallery"] = {"id": "ui:styles-gallery",
                            "kind": "dropdown", "label": "Quick Styles gallery", "screenshot": None,
                            "children": [], "child_containers": [], "explored": False}
                        seen_surfaces.add("ui:styles-gallery")
                    coverage["measured"].append("quick-styles-gallery[gallery]")
                else:
                    elem, ok, kind = probe_one(sess, jrnl, writer, frame_img, frame_rect, screen_w,
                        el, props, tuple(props.rect), base_slug, label, props.tooltip,
                        props.accelerator_key, props.access_key, seen_surfaces, stub_containers)
                    home_children.append(elem)
                    coverage["measured"].append(f"{base_slug}[{kind}]")
                    if not ok:
                        coverage["reset_mismatch"].append(base_slug)
                    if kind == "no-effect":
                        coverage["no_effect"].append(base_slug)

        # --- assemble + write containers via kernel writers ---
        ribbon_home = {"id": "ui:ribbon-home", "kind": "tab", "label": "Home tab",
                       "screenshot": ribbon_shot, "children": home_children,
                       "child_containers": sorted(seen_surfaces)}
        main_window = build_main_window(win, writer, frame_img, frame_rect)

        writer.write_container(main_window)
        writer.write_container(ribbon_home)
        for sid, c in stub_containers.items():
            writer.write_container(c)

        jrnl.append(common.journal_event(actor="stage2", action="write-containers", target="ui/*",
                    outcome="ok", data={"ribbon_home_children": len(home_children),
                                        "stubs": sorted(stub_containers.keys()),
                                        "main_window_children": len(main_window["children"])}))

        # coverage note
        note = {
            "scope": "Home tab as the whole app",
            "core_groups_measured": sorted(CORE_GROUPS),
            "boundary_groups": {g: BOUNDARY_REASON[g] for g in BOUNDARY_GROUPS},
            "counts": {"home_controls": len(home_children),
                       "measured": len(coverage["measured"]),
                       "boundary_controls": len(coverage["boundary"]),
                       "opened_surfaces_stubbed": len(stub_containers),
                       "no_effect": len(coverage["no_effect"]),
                       "reset_mismatch": len(coverage["reset_mismatch"])},
            "no_effect_controls": coverage["no_effect"],
            "reset_mismatch_controls": coverage["reset_mismatch"],
            "measured_controls": coverage["measured"],
            "stub_surfaces": sorted(stub_containers.keys()),
            "out_of_scope_unexplored": ["other ribbon tabs (Insert..Acrobat)", "File/Backstage",
                                        "status bar", "window chrome buttons"],
        }
        (common.APP_KB / "step2_coverage.json").write_text(
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

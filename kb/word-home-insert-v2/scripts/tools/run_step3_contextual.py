"""Step 3 — contextual surfaces, FULL LOOP (v2): discover, then PRESS every control.

The v1 failure this fixes (playbook/LESSONS.md, 03-features.md par.3): contextual tabs were
captured as faces with every control `unexplored` — dead ends invisible to priority and depth.
v2 runs the same press-observe-classify crawl on each contextual tab that Step 2 ran on
Home/Insert, WITH the summoning object present and selected:

  for each object family (table, picture, svg-graphic, shape, textbox, wordart, smartart,
                          chart, equation, header):
    COM-insert the object + select inside it (state setup only; UI is never driven via COM)
    read the ribbon tab-strip delta -> the appeared tabs are measured contextual surfaces
    for each new tab (deduped by family+label across probes):
      activate it, enumerate its face, then press-observe-classify EVERY enabled control:
        * new dialog/flyout/pane windows -> opens + stub container (explored:false)
        * doc/format/object/app OR family-fingerprint delta -> triggers (feature)
        * contextual-mode tabs appearing on a press (Background Removal) -> feature (mode)
        * nothing observable -> unexplored, journaled honestly
      reset per control: close surfaces / Ctrl+Z to the with-object baseline, RE-SELECT the
      object (the selection IS the trigger condition), re-activate the tab; if the object was
      destroyed, re-insert it (journaled incident)
    then undo everything, verify strip+doc back to the plain-doc baseline

Family fingerprints (COM, read-only) catch effects invisible to the generic snapshot: table
style options (Header Row / Banded Rows), shape fill/line/size, chart type/title/legend,
SmartArt layout/color, equation text, header/footer story text + flags.

Chart guard: presses that spawn an EXCEL process (Edit Data) are measured as opening the
external chart-data editor: journaled, the new excel pid killed, element -> opens
ui:chart-data-editor (stub, external boundary).

Usage: python run_step3_contextual.py [family ...]   (default: all families)
Resume-safe: a contextual tab already explored:true with children in ui.json is skipped.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import psutil
import win32api

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import common
from session import WordSession
import uia_attach as ua
import enumerator as en
import driver as drv
import prober as pb
import capture as cap
import windows as wins
import run_step2 as r2

KB = common.APP_KB


def slug_tab(label, family=None):
    """Container slug for a contextual tab. GENERIC labels ('Format', 'Design') collide across
    families — SmartArt Tools/Format and Chart Tools/Format are DIFFERENT surfaces — so a
    generic label gets its family prefixed (measured collision, v1 run)."""
    if family and label.lower() in ("format", "design"):
        fam = family.removesuffix(" Tools").strip()
        return "ribbon-" + r2.slugify("", f"{fam} {label}")
    return "ribbon-" + r2.slugify("", label)


def make_probe_png():
    from PIL import Image
    p = Path(common.SCRATCH_DIR) / "probe-image.png"
    img = Image.new("RGB", (120, 80))
    for x in range(120):
        for y in range(80):
            img.putpixel((x, y), (x * 2 % 256, y * 3 % 256, 120))
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    return p


def make_probe_svg():
    """A local SVG file — inserting it yields a Graphic object (Graphics Format tab) with NO
    network involved (v2 improvement over v1's 'Icons = network boundary' blanket skip)."""
    p = Path(common.SCRATCH_DIR) / "probe-icon.svg"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text('<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96">'
                 '<circle cx="48" cy="48" r="40" fill="#4472C4"/>'
                 '<rect x="30" y="30" width="36" height="36" fill="#ED7D31"/></svg>',
                 encoding="utf-8")
    return p


# --- family fingerprints (read-only COM; every getter guarded) -----------------------------
def _g(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def fp_table(sess):
    d = sess.doc
    if _g(lambda: d.Tables.Count, 0) == 0:
        return {"absent": True}
    t = d.Tables(1)
    return {"style": _g(lambda: str(t.Style.NameLocal)),
            "rows": _g(lambda: t.Rows.Count), "cols": _g(lambda: t.Columns.Count),
            "heading": _g(lambda: bool(t.ApplyStyleHeadingRows)),
            "lastrow": _g(lambda: bool(t.ApplyStyleLastRow)),
            "firstcol": _g(lambda: bool(t.ApplyStyleFirstColumn)),
            "lastcol": _g(lambda: bool(t.ApplyStyleLastColumn)),
            "rowbands": _g(lambda: bool(t.ApplyStyleRowBands)),
            "colbands": _g(lambda: bool(t.ApplyStyleColumnBands)),
            "shade": _g(lambda: int(t.Cell(1, 1).Shading.BackgroundPatternColor)),
            "borders": _g(lambda: int(t.Borders.Enable)),
            "autofit": _g(lambda: bool(t.AllowAutoFit)),
            "w1": _g(lambda: round(float(t.Columns(1).Width), 1)),
            "align": _g(lambda: int(t.Rows.Alignment)),
            "cellvalign": _g(lambda: int(t.Cell(1, 1).VerticalAlignment)),
            "dir": _g(lambda: int(t.TableDirection))}


def _fp_shapeish(sh):
    return {"w": _g(lambda: round(float(sh.Width), 1)),
            "h": _g(lambda: round(float(sh.Height), 1)),
            "rot": _g(lambda: round(float(sh.Rotation), 1)),
            "fill": _g(lambda: int(sh.Fill.ForeColor.RGB)),
            "fillvis": _g(lambda: int(sh.Fill.Visible)),
            "line": _g(lambda: int(sh.Line.ForeColor.RGB)),
            "linew": _g(lambda: round(float(sh.Line.Weight), 2)),
            "linevis": _g(lambda: int(sh.Line.Visible)),
            "shadow": _g(lambda: int(sh.Shadow.Visible)),
            "type": _g(lambda: int(sh.Type))}


def fp_inlineshape(sess):
    d = sess.doc
    if _g(lambda: d.InlineShapes.Count, 0) == 0:
        return {"absent": True}
    sh = d.InlineShapes(1)
    out = {"w": _g(lambda: round(float(sh.Width), 1)),
           "h": _g(lambda: round(float(sh.Height), 1)),
           "type": _g(lambda: int(sh.Type)),
           "bright": _g(lambda: round(float(sh.PictureFormat.Brightness), 3)),
           "contrast": _g(lambda: round(float(sh.PictureFormat.Contrast), 3)),
           "crop_l": _g(lambda: round(float(sh.PictureFormat.CropLeft), 1)),
           "border_rgb": _g(lambda: int(sh.Borders.OutsideColor)),
           "line_vis": _g(lambda: int(sh.Line.Visible)),
           "line_rgb": _g(lambda: int(sh.Line.ForeColor.RGB))}
    return out


def fp_shape(sess):
    d = sess.doc
    if _g(lambda: d.Shapes.Count, 0) == 0:
        return {"absent": True}
    return _fp_shapeish(d.Shapes(1))


def fp_chart(sess):
    d = sess.doc
    if _g(lambda: d.InlineShapes.Count, 0) == 0:
        return {"absent": True}
    sh = d.InlineShapes(1)
    ch = _g(lambda: sh.Chart)
    if ch is None:
        return {"absent": True}
    return {"type": _g(lambda: int(ch.ChartType)),
            "has_title": _g(lambda: bool(ch.HasTitle)),
            "has_legend": _g(lambda: bool(ch.HasLegend)),
            "style": _g(lambda: int(ch.ChartStyle)),
            "w": _g(lambda: round(float(sh.Width), 1)),
            "h": _g(lambda: round(float(sh.Height), 1))}


def fp_smartart(sess):
    d = sess.doc
    if _g(lambda: d.InlineShapes.Count, 0) == 0:
        return {"absent": True}
    sa = _g(lambda: d.InlineShapes(1).SmartArt)
    if sa is None:
        return {"absent": True}
    return {"layout": _g(lambda: str(sa.Layout.Name)),
            "color": _g(lambda: str(sa.Color.Name)),
            "quick": _g(lambda: str(sa.QuickStyle.Name)),
            "nodes": _g(lambda: int(sa.AllNodes.Count)),
            "reverse": _g(lambda: bool(sa.Reverse))}


def fp_equation(sess):
    d = sess.doc
    n = _g(lambda: d.OMaths.Count, 0)
    if not n:
        return {"absent": True}
    return {"count": n,
            "text": _g(lambda: str(d.OMaths(1).Range.Text)),
            "just": _g(lambda: int(d.OMaths(1).Justification)),
            "builtup": _g(lambda: bool(d.OMaths(1).Type))}


def fp_header(sess):
    d = sess.doc
    import hashlib
    def _h(fn):
        v = _g(fn, "")
        return hashlib.sha1(str(v).encode("utf-8", "replace")).hexdigest()[:10]
    s1 = _g(lambda: d.Sections(1))
    if s1 is None:
        return {"absent": True}
    return {"hdr": _h(lambda: s1.Headers(1).Range.Text),
            "ftr": _h(lambda: s1.Footers(1).Range.Text),
            "diff_first": _g(lambda: bool(s1.PageSetup.DifferentFirstPageHeaderFooter)),
            "odd_even": _g(lambda: bool(s1.PageSetup.OddAndEvenPagesHeaderFooter)),
            "hdr_dist": _g(lambda: round(float(s1.PageSetup.HeaderDistance), 1)),
            "fields": _g(lambda: int(d.Fields.Count)),
            "pagenums": _g(lambda: int(s1.Headers(1).PageNumbers.Count))}


# --- object probes: insert / reselect / fingerprint per family -----------------------------
def object_probes(sess, png_path, svg_path):
    app, doc = sess.app, sess.doc

    def ins_table():
        t = doc.Tables.Add(doc.Paragraphs(1).Range, 3, 3)
        return True

    def sel_table():
        t = doc.Tables(1)
        # select a 2-cell range so cell-merge/split style controls enable (representative state)
        doc.Range(t.Cell(1, 1).Range.Start, t.Cell(1, 2).Range.End).Select()
        return True

    def ins_picture():
        doc.InlineShapes.AddPicture(str(png_path), False, True, doc.Paragraphs(1).Range)
        return True

    def sel_inlineshape():
        doc.InlineShapes(1).Select()
        return True

    def ins_svg():
        doc.InlineShapes.AddPicture(str(svg_path), False, True, doc.Paragraphs(1).Range)
        return True

    def ins_shape():
        doc.Shapes.AddShape(1, 100, 100, 120, 80)
        return True

    def sel_shape():
        doc.Shapes(1).Select()
        return True

    def ins_textbox():
        doc.Shapes.AddTextbox(1, 100, 220, 160, 60)
        return True

    def ins_wordart():
        doc.Shapes.AddTextEffect(0, "Probe", "Arial", 24, False, False, 100, 320)
        return True

    def ins_smartart():
        layout = app.SmartArtLayouts.Item(1)
        doc.InlineShapes.AddSmartArt(layout, doc.Paragraphs(1).Range)
        return True

    def ins_chart():
        sh = doc.InlineShapes.AddChart2(-1, 51, doc.Paragraphs(1).Range)
        try:
            sh.Chart.ChartData.Workbook.Close(False)
        except Exception:
            pass
        return True

    def ins_equation():
        doc.OMaths.Add(app.Selection.Range)
        return True

    def sel_equation():
        doc.OMaths(1).Range.Select()
        return True

    def ins_header():
        return True     # nothing to insert — entering the story IS the trigger

    def sel_header():
        doc.Sections(1).Headers(1).Range.Select()
        return True

    return [
        ("table", ins_table, sel_table, fp_table,
         "selection is inside a table", "subfeature:table-insert"),
        ("picture", ins_picture, sel_inlineshape, fp_inlineshape,
         "an inline picture is selected", "subfeature:insert-pictures"),
        ("svg-graphic", ins_svg, sel_inlineshape, fp_inlineshape,
         "an SVG/icon graphic is selected", "subfeature:icon-insert-from-file"),
        ("shape", ins_shape, sel_shape, fp_shape,
         "a drawn shape is selected", "subfeature:shapes-insert"),
        ("textbox", ins_textbox, sel_shape, fp_shape,
         "a text box is selected", "subfeature:text-box-insert"),
        # NOTE: no 'wordart' probe. In Word 16 the ribbon Insert > WordArt gallery creates a
        # MODERN text-effect shape whose contextual surface is Shape Format (already captured
        # via the shape/textbox probes). The deprecated standalone 'WordArt' tab is only
        # summoned by the legacy COM AddTextEffect path / old documents — NOT reachable from
        # the Home+Insert universe's UI — and its 'Edit Text…' modal destabilised the COM
        # instance under automation. Decision journaled in main(); word-art-insert keeps its
        # measured contextual edge to Shape Format.
        ("smartart", ins_smartart, sel_inlineshape, fp_smartart,
         "a SmartArt graphic is selected", "subfeature:smart-art-insert"),
        ("chart", ins_chart, sel_inlineshape, fp_chart,
         "an embedded chart is selected", "subfeature:chart-insert"),
        ("equation", ins_equation, sel_equation, fp_equation,
         "the cursor is inside an equation (math zone)", "subfeature:equation-insert"),
        ("header", ins_header, sel_header, fp_header,
         "header/footer editing mode is active (cursor in header or footer)",
         "subfeature:header-insert"),
    ]


# --- the contextual press loop --------------------------------------------------------------
def _excel_pids():
    return {p.pid for p in psutil.process_iter(["name"])
            if (p.info["name"] or "").lower() == "excel.exe"}


MIN_REAL_WINDOW_AREA = 2500     # px²: a selected floating object shows a ~28x28 'Layout
                                # Options' chip of DIALOG class with a churning hwnd — it is
                                # chrome, not a surface (measured: shape-format MISMATCH chain)
# Legacy modal openers that destabilise the COM instance under automation — documented as
# honest boundaries (a node with a measured face + a journaled 'not pressed' reason), never
# pressed. Defense-in-depth so no single control can crash the whole run.
FRAGILE_OPENER_SUBSTR = ("edit text", "ink equation")


def _is_fragile(label):
    l = (label or "").lower()
    return any(s in l for s in FRAGILE_OPENER_SUBSTR)


def _stable_hwnds(pid):
    """Top-level hwnds excluding sub-floor chrome (the Layout Options chip et al.)."""
    return {h for (h, c, t, r) in wins.toplevels(pid)
            if wins._area(r) >= MIN_REAL_WINDOW_AREA}


def _force_close_nonframe(sess, keep_hwnds):
    """win32-ONLY teardown of any non-frame top-level window (no COM — the point is to unblock
    a COM that a modal is holding busy). Used to recover after a control opened a surface that
    blocked COM (e.g. an OS file dialog). Then wait for COM to answer again."""
    import win32con
    for (h, c, t, r) in wins.toplevels(sess.pid):
        if h == sess.frame or h in keep_hwnds:
            continue
        try:
            win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
        except Exception:
            pass
    drv.press_escape(3)     # keyboard-level (win32), not COM
    # poll until COM answers (doc_hash returns a real hash, not the <com-busy> sentinel)
    for _ in range(20):
        if sess.doc_hash() != "<com-busy>":
            return True
        time.sleep(0.3)
    return False


def probe_contextual_control(ctx, props, click_rect, node_slug, label, dropdown_zone=False):
    """Press one control on an active contextual tab; classify with the family fingerprint
    added to the generic snapshot; reset back to the with-object baseline."""
    sess, jrnl, writer = ctx["sess"], ctx["jrnl"], ctx["writer"]
    cid, tab_label = ctx["cid"], ctx["tab_label"]
    if _is_fragile(label):
        jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="boundary",
                    target=node_slug, outcome="fragile-opener-not-pressed",
                    data={"label": label, "reason": "legacy modal known to destabilise the "
                          "COM instance under automation — face documented, interior deferred"}))
        icon = r2.make_icon(ctx["frame_img"], ctx["frame_rect"], tuple(props.rect),
                            writer, cid, node_slug, label)
        el = {"id": f"el:{node_slug}", "control_type": props.control_type.lower(),
              "label": label, "icon": icon, "tooltip": props.tooltip or None,
              "shortcut": props.accelerator_key or None,
              "location": f"ui:main-window > {cid}", "bounds": list(props.rect),
              "source": "uia", "unexplored": True,
              "state_notes": "boundary: legacy modal not pressed (would destabilise COM)"}
        return el, True, "boundary"
    ctx["reselect"]()
    baseline = pb.snapshot(sess, ctx["screen_w"])
    baseline["family"] = ctx["fingerprint"](sess)
    tabs_before = r2.tab_strip_names(ctx["win"])
    excel_before = _excel_pids() if ctx["family"] == "chart" else set()
    jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="press-attempted",
                target=node_slug, outcome="",
                data={"rect": list(click_rect), "label": label, "tab": tab_label}))
    drv.ensure_frame_foreground(sess.frame)
    pt = drv.click_target(click_rect)
    neww = pb.observe(sess, baseline["hwnds"])
    # drop sub-floor chrome windows (Layout Options chip reads as a 28x28 'dialog')
    neww = [w for w in neww if wins._area(w[3]) >= MIN_REAL_WINDOW_AREA]
    after = pb.snapshot(sess, ctx["screen_w"])
    after["family"] = ctx["fingerprint"](sess)
    kind, detail = pb.classify(baseline, after, neww)

    # family-fingerprint delta: catches style-option/object effects the generic sig misses
    if kind == "no-effect" and baseline["family"] != after["family"]:
        diff = {k: (baseline["family"].get(k), after["family"].get(k))
                for k in after["family"] if baseline["family"].get(k) != after["family"].get(k)}
        kind, detail = "feature", {"state_changed": [f"ctxobj:{k}" for k in diff],
                                   "family_diff": {k: list(v) for k, v in diff.items()}}
    # dropdown-zone small-menu rescue (v1 fixup lesson)
    if kind == "no-effect" and dropdown_zone:
        rescue = r2._small_flyout_recheck(neww)
        if rescue:
            kind, detail = "flyout", rescue
            jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="surface-retyped",
                        target=node_slug, outcome="flyout(small-floor)", data=rescue))
    # a press may summon a DEEPER contextual mode (Remove Background) — measured via strip
    tabs_after = r2.tab_strip_names(ctx["win"])
    mode_tabs = [t for t in tabs_after if t not in tabs_before]
    if mode_tabs and kind == "no-effect":
        kind = "feature"
        detail = {"state_changed": [f"contextual-mode:{t}" for t in mode_tabs],
                  "mode_tabs": mode_tabs}
    elif mode_tabs:
        detail["contextual_tabs_appeared"] = mode_tabs
    if mode_tabs:
        jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="contextual-tabs",
                    target=node_slug, outcome="appeared", data={"tabs": mode_tabs}))

    # chart-family external editor guard (Edit Data spawns EXCEL — another process, invisible
    # to our PID-filtered window delta)
    if ctx["family"] == "chart":
        excel_new = _excel_pids() - excel_before
        if excel_new:
            kind, detail = "external", {"process": "excel.exe", "pids": sorted(excel_new)}
            jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="boundary",
                        target=node_slug, outcome="external-editor",
                        data={"reason": "opens the embedded chart-data editor in a separate "
                              "EXCEL process — external app boundary", "pids": sorted(excel_new)}))
            for pid in excel_new:
                subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            time.sleep(0.8)

    # floating task pane reads as dialog by class
    if kind == "dialog" and detail.get("hwnd") and wins.is_task_pane_window(detail["hwnd"]):
        kind = "pane"
        detail["floating"] = True

    icon = r2.make_icon(ctx["frame_img"], ctx["frame_rect"], tuple(props.rect), writer,
                        cid, node_slug, label)
    elem = {"id": f"el:{node_slug}", "control_type": props.control_type.lower(),
            "label": label, "icon": icon, "tooltip": props.tooltip or None,
            "shortcut": props.accelerator_key or None,
            "location": f"ui:main-window > {cid}",
            "bounds": list(props.rect), "source": "measured",
            "state_notes": (f"keytip {props.access_key}" if props.access_key else None)}

    if kind in ("dialog", "flyout", "pane"):
        ck = r2.container_kind(kind, props.automation_id)
        surf_id = r2.surface_id(node_slug, kind, ck)
        elem["opens"] = surf_id
        elem["source"] = "measured:window-delta" if kind != "pane" else "measured:pane-inset"
        shot, size = r2._surface_screenshot(sess, kind, detail, writer,
                                            surf_id.removeprefix("ui:"))
        if surf_id not in ctx["seen_surfaces"]:
            ctx["stub_containers"][surf_id] = {
                "id": surf_id, "kind": ck, "label": detail.get("title") or label,
                "purpose": (props.tooltip or None), "screenshot": shot,
                "children": [], "child_containers": [], "explored": False}
            ctx["seen_surfaces"].add(surf_id)
            jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="surface-discovered",
                        target=surf_id, outcome=kind,
                        data={"via": node_slug, "class": detail.get("class"),
                              "title": detail.get("title"), "screenshot": shot, "size": size}))
    elif kind == "feature":
        elem["triggers"] = f"subfeature:{node_slug}"
        elem["source"] = "measured:state-delta"
        notes = f"state changed: {detail.get('state_changed')}"
        if detail.get("mode_tabs"):
            notes = (f"enters a contextual editing MODE (tabs: {detail['mode_tabs']}) — "
                     f"exits via Escape/Keep/Discard")
        elem["state_notes"] = notes + (f"; keytip {props.access_key}" if props.access_key else "")
    elif kind == "external":
        surf_id = "ui:chart-data-editor"
        elem["opens"] = surf_id
        elem["source"] = "measured:process-delta"
        elem["state_notes"] = ("opens the chart's linked worksheet in a separate Excel "
                               "process (external editor boundary)")
        if surf_id not in ctx["seen_surfaces"]:
            ctx["stub_containers"][surf_id] = {
                "id": surf_id, "kind": "window",
                "label": "Chart data editor (embedded Excel workbook)",
                "purpose": "external Excel process editing the chart's source data — "
                           "boundary: another application's UI, not enumerated",
                "screenshot": None, "children": [], "child_containers": [],
                "explored": False}
            ctx["seen_surfaces"].add(surf_id)
    else:   # no-effect
        elem["unexplored"] = True
        elem["state_notes"] = "pressed: no observable effect (see journal)"

    # ---- reset to the with-object baseline ----
    notes = []
    if kind in ("dialog", "flyout"):
        pb._close_window(sess, detail.get("hwnd"), notes)
    elif kind == "pane":
        if detail.get("floating") and detail.get("hwnd"):
            pb._close_pane_window(sess, detail["hwnd"], notes)
        pb._close_panes(sess, notes)
    elif kind == "feature":
        if detail.get("mode_tabs"):
            # exit the mode: ESC, then look for a Discard/Close button if the tab persists
            drv.press_escape(2)
            time.sleep(0.5)
            if any(t in r2.tab_strip_names(ctx["win"]) for t in detail["mode_tabs"]):
                try:
                    w = ua.attach(sess.frame)
                    for bname in ("Discard All Changes", "Close Header and Footer", "Close"):
                        try:
                            b = w.child_window(title=bname, control_type="Button")
                            if b.exists(timeout=0.8):
                                b.click_input()
                                time.sleep(0.5)
                                notes.append(f"mode-exit via {bname}")
                                break
                        except Exception:
                            continue
                except Exception:
                    pass
            notes.append("mode-exited")
        drv.ensure_frame_foreground(sess.frame)
        for _ in range(8):
            drv.send_keys("^z")
            time.sleep(0.3)
            if (sess.doc_hash() == ctx["base_doc_hash"]
                    and ctx["fingerprint"](sess) == ctx["base_family"]
                    and sess.object_fingerprint() == ctx["base_objects"]):
                break
        notes.append("ctrl+z")
    elif kind == "no-effect":
        drv.press_escape(1)
        notes.append("esc(no-effect)")

    # the object may have been destroyed/left — verify and repair
    fam_now = ctx["fingerprint"](sess)
    if fam_now.get("absent") or sess.object_fingerprint() != ctx["base_objects"]:
        for _ in range(6):
            drv.send_keys("^z")
            time.sleep(0.3)
            fam_now = ctx["fingerprint"](sess)
            if not fam_now.get("absent") and sess.object_fingerprint() == ctx["base_objects"]:
                break
        if fam_now.get("absent"):
            jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="ambiguous",
                        target=node_slug,
                        outcome="object destroyed by press; re-inserting",
                        data={"family": ctx["family"]}))
            try:
                ctx["reinsert"]()
                time.sleep(0.8)
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="error",
                            target=node_slug, outcome=f"re-insert failed: {e}", data={}))
    # restore the contextual selection + tab
    try:
        ctx["reselect"]()
    except Exception:
        pass
    drv.ensure_frame_foreground(sess.frame)
    time.sleep(0.3)
    try:
        en.select_tab(ctx["win"], tab_label)
        time.sleep(0.3)
    except Exception:
        pass

    reset_ok = (sess.doc_hash() == ctx["base_doc_hash"]
                and ctx["fingerprint"](sess) == ctx["base_family"]
                and _stable_hwnds(sess.pid) == ctx["base_stable_hwnds"])
    jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="press-outcome",
                target=node_slug, outcome=kind,
                data={"detail": {k: v for k, v in detail.items() if k != "hwnd"},
                      "marker": ("opens:" + elem.get("opens", "")) if elem.get("opens")
                      else ("triggers:" + elem.get("triggers", "")) if elem.get("triggers")
                      else "unexplored"}))
    jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="reset-verified",
                target=node_slug, outcome="ok" if reset_ok else "MISMATCH",
                data={"notes": notes}))
    return elem, reset_ok, kind


def crawl_contextual_tab(sess, win, writer, jrnl, tab_label, condition, via, family,
                         fingerprint, reselect, reinsert, screen_w, seen_surfaces):
    """Activate one contextual tab and press-observe-classify every enabled control on it."""
    cid = f"ui:{slug_tab(tab_label, family)}"
    en.select_tab(win, tab_label)
    time.sleep(0.6)
    drv.ensure_frame_foreground(sess.frame)
    time.sleep(0.2)
    frame_img, frame_rect = cap.grab_window(sess.frame)
    shot = writer.save_screenshot(frame_img.crop((0, 0, frame_img.width, 200)), cid, "surface")

    ctx = {"sess": sess, "jrnl": jrnl, "writer": writer, "win": win, "cid": cid,
           "tab_label": tab_label, "family": family, "fingerprint": fingerprint,
           "reselect": reselect, "reinsert": reinsert, "screen_w": screen_w,
           "frame_img": frame_img, "frame_rect": frame_rect,
           "seen_surfaces": seen_surfaces, "stub_containers": {},
           "base_doc_hash": sess.doc_hash(), "base_family": fingerprint(sess),
           "base_objects": sess.object_fingerprint(),
           "base_stable_hwnds": _stable_hwnds(sess.pid)}

    children, counts = [], {"measured": 0, "opens": 0, "feature": 0, "no_effect": 0,
                            "disabled": 0, "mismatch": 0}
    groups_meta = []
    prefix = cid.removeprefix("ui:") + "-"
    for gname, gkeytip, leaves in en.live_leaves(win, tab_label):
        groups_meta.append(gname)
        for el, props in leaves:
            label = props.name or props.automation_id or "?"
            ct = props.control_type
            slug = (prefix + r2.slugify(props.automation_id, label))[:100]
            if not props.is_enabled:
                icon = r2.make_icon(frame_img, frame_rect, tuple(props.rect), writer, cid,
                                    slug, label)
                children.append({"id": f"el:{slug}", "control_type": ct.lower(), "label": label,
                    "icon": icon, "tooltip": props.tooltip or None,
                    "shortcut": props.accelerator_key or None,
                    "location": f"ui:main-window > {cid}", "bounds": list(props.rect),
                    "source": "uia", "unexplored": True,
                    "state_notes": f"disabled in this context (group '{gname}') — journaled"})
                jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="press-skipped",
                            target=slug, outcome="disabled", data={"label": label, "tab": tab_label}))
                counts["disabled"] += 1
                continue
            # build the (click_rect, slug, label, dropdown_zone) presses for this control
            presses = []
            if ct == "SplitButton":
                primary, dropdown = drv.split_zone_rects(el)
                presses.append((primary or drv.zone_point(props.rect, "primary"),
                                slug, label, False))
                presses.append((dropdown or drv.zone_point(props.rect, "dropdown"),
                                slug + "-dropdown", f"{label} (dropdown)", True))
            elif ct == "ComboBox":
                open_rect = en.combo_open_rect(el) or drv.zone_point(props.rect, "dropdown")
                presses.append((open_rect, slug, label, True))
            else:
                presses.append((tuple(props.rect), slug, label, False))

            for click_rect, pslug, plabel, dz in presses:
                try:
                    e, ok, k = probe_contextual_control(ctx, props, click_rect, pslug,
                                                        plabel, dropdown_zone=dz)
                except Exception as ex:
                    # a control blocked COM (e.g. an OS file dialog); recover win32-only and
                    # record it honestly as an unexplored boundary, then continue the tab
                    jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="ambiguous",
                                target=pslug, outcome=f"exception: {type(ex).__name__}",
                                data={"label": plabel, "error": str(ex)[:160]}))
                    recovered = _force_close_nonframe(ctx["sess"], set())
                    try:
                        ctx["reselect"]()
                        en.select_tab(ctx["win"], tab_label)
                    except Exception:
                        pass
                    icon = r2.make_icon(frame_img, frame_rect, tuple(props.rect), writer,
                                        cid, pslug, plabel)
                    e = {"id": f"el:{pslug}", "control_type": props.control_type.lower(),
                         "label": plabel, "icon": icon, "tooltip": props.tooltip or None,
                         "shortcut": props.accelerator_key or None,
                         "location": f"ui:main-window > {cid}", "bounds": list(props.rect),
                         "source": "measured", "unexplored": True,
                         "state_notes": ("opened a surface that blocked COM (likely an OS "
                                         "file/print dialog); recovered win32-only and left "
                                         f"unexplored{'' if recovered else ' (COM slow to free)'}")}
                    ok, k = True, "boundary"
                e["state_notes"] = ((e.get("state_notes") or "") +
                                    f"; group '{gname}'").strip("; ")
                children.append(e)
                counts["measured"] += 1
                counts["mismatch"] += (0 if ok else 1)
                if e.get("opens"):
                    counts["opens"] += 1
                elif e.get("triggers"):
                    counts["feature"] += 1
                elif e.get("unexplored"):
                    counts["no_effect"] += 1

    cont = {"id": cid, "kind": "tab", "label": f"{tab_label} (contextual tab)",
            "screenshot": shot, "children": children,
            "child_containers": sorted(ctx["stub_containers"].keys()),
            "explored": True,
            "trigger_condition": condition,
            "purpose": (f"contextual ribbon tab" +
                        (f" of the '{family}' family" if family else "") +
                        f"; exists only while: {condition}. "
                        f"Groups: {', '.join(groups_meta)}. Appeared on the '{via}' probe.")}
    writer.upsert_container(cont)
    for sid, c in ctx["stub_containers"].items():
        if sid not in {k for k in writer.load_ui().containers} or sid in ctx["stub_containers"]:
            existing = writer.load_ui().containers.get(sid)
            if existing is None:
                writer.upsert_container(c)
    jrnl.append(common.journal_event(actor="stage3.ctxprobe", action="surface-captured",
                target=cid, outcome="ok",
                data={"tab": tab_label, "controls": len(children), "groups": groups_meta,
                      "condition": condition, "via": via, "screenshot": shot,
                      "counts": counts}))
    return cid, counts


def main():
    only = set(a.lower() for a in sys.argv[1:])
    run_id = common.make_run_id() + "-step3-contextual"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    screen_w = win32api.GetSystemMetrics(0)
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    png, svg = make_probe_png(), make_probe_svg()

    jrnl.append(common.journal_event(actor="stage3.contextual", action="boundary",
                target="3d-models", outcome="skipped",
                data={"reason": "3D model library streams from network — boundary; its "
                      "contextual tab cannot be summoned offline"}))
    jrnl.append(common.journal_event(actor="stage3.contextual", action="decision",
                target="screenshot", outcome="skipped",
                data={"reasoning": "Screenshot inserts a picture — its contextual surface is "
                      "the Picture Format tab, covered by the picture probe"}))
    jrnl.append(common.journal_event(actor="stage3.contextual", action="decision",
                target="wordart-legacy-tab", outcome="out-of-universe",
                data={"reasoning": "Insert > WordArt in Word 16 creates a modern text-effect "
                      "shape -> Shape Format tab (measured, captured via shape/textbox). The "
                      "deprecated standalone 'WordArt' contextual tab is summoned only by the "
                      "legacy COM AddTextEffect path / old docs, not by this universe's UI, and "
                      "its Edit Text modal crashed the COM instance; excluded. word-art-insert "
                      "-> ui:ribbon-shape-format is its contextual edge."}))

    excel_before = _excel_pids()
    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage3.contextual", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={"run_id": run_id}))
    results = {}
    # dedupe tabs across probes and RUNS (resume-safe): (family,label) -> cid
    seen_tabs = {}
    ui_now = writer.load_ui().containers
    seen_surfaces = set(ui_now.keys())
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        base_tabs = r2.tab_strip_names(win)
        base_objects = sess.object_fingerprint()
        base_hash = sess.doc_hash()

        for name, ins, sel, fp, condition, owner in object_probes(sess, png, svg):
            if only and name not in only:
                continue
            jrnl.append(common.journal_event(actor="stage3.contextual", action="press-attempted",
                        target=name, outcome="", data={"method": "com-insert+select",
                                                       "condition": condition}))
            try:
                ins()
                time.sleep(0.6)
                sel()
                drv.ensure_frame_foreground(sess.frame)
                time.sleep(1.2)
                tabs_now = r2.tab_strip_names(win)
                new_tabs = [t for t in tabs_now if t not in base_tabs]
                families = r2.contextual_tab_groups(win)
                jrnl.append(common.journal_event(actor="stage3.contextual",
                            action="press-outcome", target=name,
                            outcome="contextual-tabs" if new_tabs else "none",
                            data={"new_tabs": new_tabs, "families": families}))
                entry = {"new_tabs": new_tabs, "containers": [], "counts": {}}
                for t in new_tabs:
                    tkey = (families.get(t), t)
                    cid_expect = f"ui:{slug_tab(t, families.get(t))}"
                    if tkey in seen_tabs:
                        cid = seen_tabs[tkey]
                        cont = writer.load_ui().containers.get(cid)
                        if cont and condition not in (cont.trigger_condition or ""):
                            cont.trigger_condition += f" | {condition}"
                            cont.purpose = (cont.purpose or "") + \
                                f" Also appears when: {condition} ('{name}' probe)."
                            writer.upsert_container(cont)
                        jrnl.append(common.journal_event(actor="stage3.contextual",
                                    action="surface-discovered", target=cid,
                                    outcome="seen-again (condition merged)", data={"via": name}))
                        entry["containers"].append(cid)
                        continue
                    existing = writer.load_ui().containers.get(cid_expect)
                    if existing is not None and existing.explored and existing.children:
                        seen_tabs[tkey] = cid_expect
                        entry["containers"].append(cid_expect)
                        if condition not in (existing.trigger_condition or ""):
                            existing.trigger_condition = ((existing.trigger_condition or "")
                                                          + f" | {condition}").strip(" |")
                            existing.purpose = (existing.purpose or "") + \
                                f" Also appears when: {condition} ('{name}' probe)."
                            writer.upsert_container(existing)
                        jrnl.append(common.journal_event(actor="stage3.contextual",
                                    action="decision", target=cid_expect,
                                    outcome="resume-skip",
                                    data={"reasoning": "tab already crawled in a previous "
                                          "step-3 run (explored:true with children); "
                                          "condition merged"}))
                        continue
                    cid, counts = crawl_contextual_tab(
                        sess, win, writer, jrnl, t, condition, name, families.get(t),
                        fp, sel, ins, screen_w, seen_surfaces)
                    seen_tabs[tkey] = cid
                    entry["containers"].append(cid)
                    entry["counts"][t] = counts
                results[name] = entry
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage3.contextual",
                            action="press-outcome", target=name,
                            outcome=f"error: {e}", data={}))
                results[name] = {"error": str(e)}
            # ---- restore: leave the object story, undo until plain-doc baseline ----
            try:
                sess.doc.Paragraphs(1).Range.Select()
            except Exception:
                pass
            drv.ensure_frame_foreground(sess.frame)
            for _ in range(14):
                drv.send_keys("^z")
                time.sleep(0.3)
                if (sess.object_fingerprint() == base_objects
                        and sess.doc_hash() == base_hash):
                    break
            sess.select_paragraph(1)
            time.sleep(0.4)
            tabs_check = r2.tab_strip_names(win)
            reset_ok = (tabs_check == base_tabs
                        and sess.object_fingerprint() == base_objects)
            jrnl.append(common.journal_event(actor="stage3.contextual", action="reset-verified",
                        target=name, outcome="ok" if reset_ok else "MISMATCH",
                        data={"tabs_now": tabs_check}))
            results.setdefault(name, {})["reset_ok"] = reset_ok

        # register contextual containers on the main window
        ui = writer.load_ui()
        mw = ui.containers.get("ui:main-window")
        if mw:
            add = [cid for cid in seen_tabs.values() if cid not in mw.child_containers]
            mw.child_containers = sorted(set(list(mw.child_containers) + add))
            writer.upsert_container(mw)
        jrnl.append(common.journal_event(actor="stage3.contextual", action="write-containers",
                    target="ui.json", outcome="ok",
                    data={"contextual_containers": sorted(seen_tabs.values())}))
        print(json.dumps({"results": {k: {kk: vv for kk, vv in v.items() if kk != "counts"}
                                      for k, v in results.items()},
                          "contextual_tabs": {f"{k[0]}/{k[1]}": v
                                              for k, v in seen_tabs.items()}},
                         indent=2, ensure_ascii=False))
    finally:
        sess.close()
        excel_new = _excel_pids() - excel_before
        for pid in excel_new:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        jrnl.append(common.journal_event(actor="stage3.contextual", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed",
                    data={"excel_killed": sorted(excel_new)}))


if __name__ == "__main__":
    main()

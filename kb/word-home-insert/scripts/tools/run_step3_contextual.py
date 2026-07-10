"""Step 3 — contextual surface discovery: measure which ribbon tabs exist only in context.

Method (per toolbox/win32.md lesson: contextual tabs are SELECTION-dependent):
  for each universe object family: insert the object via COM (state setup, per toolbox/com.md),
  SELECT INSIDE the object, read the ribbon tab strip delta -> the appeared tabs are measured
  contextual surfaces. For each newly seen tab: activate it, enumerate its face exhaustively
  (surface layer: every control with type/label/icon/tooltip/keytip — marked unexplored, faces
  are not pressed in this pass), screenshot the ribbon band, and write a ui:ribbon-<slug>
  container with trigger_condition. Then undo, verify the strip and doc return to baseline.

Skipped probes are journaled boundaries: Icons / 3D Models (content requires network downloads).
Screenshot-insert produces a picture -> covered by the picture probe. UI is read via UIA; COM
only establishes state — we never map UI through the API.
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
import capture as cap
import run_step2 as r2

KB = common.APP_KB


def slug_tab(label, family=None):
    """Container slug for a contextual tab. GENERIC labels ('Format', 'Design') collide across
    families — SmartArt Tools/Format and Chart Tools/Format are DIFFERENT surfaces — so a generic
    label gets its family prefixed (measured collision, this run)."""
    if family and label.lower() in ("format", "design"):
        fam = family.removesuffix(" Tools").strip()
        return "ribbon-" + r2.slugify("", f"{fam} {label}")
    return "ribbon-" + r2.slugify("", label)


def make_probe_png():
    """A small local PNG so the picture probe never touches the network."""
    from PIL import Image
    p = Path(common.SCRATCH_DIR) / "probe-image.png"
    img = Image.new("RGB", (120, 80))
    for x in range(120):
        for y in range(80):
            img.putpixel((x, y), (x * 2 % 256, y * 3 % 256, 120))
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    return p


def object_probes(sess, png_path):
    """(name, insert_and_select_fn, trigger_condition, owner_subfeature). Each fn returns True
    if the object was inserted AND the selection is inside/on it."""
    app, doc = sess.app, sess.doc

    def table():
        t = doc.Tables.Add(doc.Paragraphs(1).Range, 3, 3)
        t.Cell(1, 1).Range.Select()
        return True

    def picture():
        sh = doc.InlineShapes.AddPicture(str(png_path), False, True,
                                         doc.Paragraphs(1).Range)
        sh.Select()
        return True

    def shape():
        s = doc.Shapes.AddShape(1, 100, 100, 120, 80)   # msoShapeRectangle
        s.Select()
        return True

    def textbox():
        s = doc.Shapes.AddTextbox(1, 100, 220, 160, 60)  # msoTextOrientationHorizontal
        s.Select()
        return True

    def wordart():
        s = doc.Shapes.AddTextEffect(0, "Probe", "Arial", 24, False, False, 100, 320)
        s.Select()
        return True

    def smartart():
        layout = app.SmartArtLayouts.Item(1)
        sh = doc.InlineShapes.AddSmartArt(layout, doc.Paragraphs(1).Range)
        sh.Select()
        return True

    def chart():
        sh = doc.InlineShapes.AddChart2(-1, 51, doc.Paragraphs(1).Range)  # clustered column
        try:      # close the embedded data-editor workbook so only Word remains
            sh.Chart.ChartData.Workbook.Close(False)
        except Exception:
            pass
        sh.Select()
        return True

    def equation():
        om = doc.OMaths.Add(doc.Paragraphs(1).Range)
        doc.OMaths(1).Range.Select()
        return True

    def header():
        doc.Sections(1).Headers(1).Range.Select()   # selecting the header story enters
        return True                                  # header/footer editing mode

    return [
        ("table", table, "selection is inside a table", "subfeature:table-insert"),
        ("picture", picture, "an inline picture is selected", "subfeature:insert-pictures"),
        ("shape", shape, "a drawn shape is selected", "subfeature:shapes-insert"),
        ("textbox", textbox, "a text box is selected", "subfeature:text-box-insert"),
        ("wordart", wordart, "a WordArt object is selected", "subfeature:word-art-insert"),
        ("smartart", smartart, "a SmartArt graphic is selected", "subfeature:smart-art-insert"),
        ("chart", chart, "an embedded chart is selected", "subfeature:chart-insert"),
        ("equation", equation, "the cursor is inside an equation (math zone)",
         "subfeature:equation-insert"),
        ("header", header, "header/footer editing mode is active (cursor in header or footer)",
         "subfeature:header-insert"),
    ]


def enumerate_contextual_tab(sess, win, writer, jrnl, tab_label, condition, via, family=None):
    """Activate + exhaustively enumerate one contextual tab face (surface layer)."""
    cid = f"ui:{slug_tab(tab_label, family)}"
    en.select_tab(win, tab_label)
    time.sleep(0.5)
    drv.ensure_frame_foreground(sess.frame)
    time.sleep(0.2)
    frame_img, frame_rect = cap.grab_window(sess.frame)
    shot = writer.save_screenshot(frame_img.crop((0, 0, frame_img.width, 200)),
                                  cid, "surface")
    children = []
    groups_meta = []
    for gname, gkeytip, leaves in en.live_leaves(win, tab_label):
        groups_meta.append(gname)
        for el, props in leaves:
            label = props.name or props.automation_id or "?"
            slug = r2.slugify(props.automation_id, label)
            icon = r2.make_icon(frame_img, frame_rect, tuple(props.rect), writer, cid,
                                slug, label)
            children.append({
                "id": f"el:{cid.removeprefix('ui:')}-{slug}"[:120],
                "control_type": props.control_type.lower(), "label": label, "icon": icon,
                "tooltip": props.tooltip or None, "shortcut": props.accelerator_key or None,
                "location": f"ui:main-window > {cid}", "bounds": list(props.rect),
                "source": "uia", "unexplored": True,
                "state_notes": (f"group '{gname}'" + (f"; keytip {props.access_key}"
                                                      if props.access_key else "") +
                                "; face documented, not pressed (contextual surface layer)")})
    cont = {"id": cid, "kind": "tab", "label": f"{tab_label} (contextual tab)",
            "screenshot": shot, "children": children, "child_containers": [],
            "explored": True,
            "trigger_condition": condition,
            "purpose": (f"contextual ribbon tab" +
                        (f" of the '{family}' family" if family else "") +
                        f"; exists only while: {condition}. "
                        f"Groups: {', '.join(groups_meta)}. Appeared on the '{via}' probe.")}
    writer.write_container(cont)
    jrnl.append(common.journal_event(actor="stage3.contextual", action="surface-captured",
                target=cid, outcome="ok",
                data={"tab": tab_label, "controls": len(children), "groups": groups_meta,
                      "condition": condition, "via": via, "screenshot": shot}))
    return cid, len(children), groups_meta


def main():
    run_id = common.make_run_id() + "-step3-contextual"
    jrnl = common.get_journal(run_id)
    writer = common.get_writer()
    pinned = json.loads((KB / "version.json").read_text(encoding="utf-8"))
    png = make_probe_png()

    # journal deliberate skips (network-gated content)
    for target, why in (("icons", "Icons library streams from Office CDN — network boundary"),
                        ("3d-models", "3D model library streams from network — boundary"),
                        ("screenshot", "inserts a picture; contextual surface covered by the "
                                       "picture probe")):
        jrnl.append(common.journal_event(actor="stage3.contextual", action="boundary",
                    target=target, outcome="skipped", data={"reason": why}))

    import psutil
    excel_before = {p.pid for p in psutil.process_iter(["name"])
                    if (p.info["name"] or "").lower() == "excel.exe"}

    fixture = common.fresh_scratch_fixture()
    sess = WordSession.start(fixture, expected_build=pinned["build_prefix_pinned"])
    jrnl.append(common.journal_event(actor="stage3.contextual", action="launch",
                target=f"pid={sess.pid}", outcome="ok", data={}))
    results = {}
    seen_tabs = {}     # tab label -> container id (dedupe across probes)
    try:
        sess.doc.Content.InsertAfter("The quick brown fox jumps over the lazy dog.")
        sess.select_paragraph(1)
        win = ua.attach(sess.frame)
        time.sleep(0.5)
        base_tabs = r2.tab_strip_names(win)
        base_objects = sess.object_fingerprint()
        base_hash = sess.doc_hash()

        for name, fn, condition, owner in object_probes(sess, png):
            jrnl.append(common.journal_event(actor="stage3.contextual", action="press-attempted",
                        target=name, outcome="", data={"method": "com-insert+select",
                                                       "condition": condition}))
            try:
                fn()
                drv.ensure_frame_foreground(sess.frame)
                time.sleep(1.2)
                tabs_now = r2.tab_strip_names(win)
                new_tabs = [t for t in tabs_now if t not in base_tabs]
                families = r2.contextual_tab_groups(win)
                jrnl.append(common.journal_event(actor="stage3.contextual", action="press-outcome",
                            target=name, outcome="contextual-tabs" if new_tabs else "none",
                            data={"new_tabs": new_tabs, "families": families}))
                entry = {"new_tabs": new_tabs, "containers": [],
                         "families": {t: families.get(t) for t in new_tabs}}
                for t in new_tabs:
                    tkey = (families.get(t), t)   # family+label — generic labels collide
                    if tkey in seen_tabs:   # seen via an earlier probe — merge the condition
                        cid = seen_tabs[tkey]
                        p = KB / "ui" / (cid.removeprefix("ui:") + ".json")
                        cont = json.loads(p.read_text(encoding="utf-8"))
                        if condition not in (cont.get("trigger_condition") or ""):
                            cont["trigger_condition"] += f" | {condition}"
                            cont["purpose"] += f" Also appears when: {condition} ('{name}' probe)."
                            writer.write_container(cont)
                        jrnl.append(common.journal_event(actor="stage3.contextual",
                                    action="surface-discovered", target=cid,
                                    outcome="seen-again (condition merged)",
                                    data={"via": name}))
                        entry["containers"].append(cid)
                        continue
                    cid, n, groups = enumerate_contextual_tab(sess, win, writer, jrnl,
                                                              t, condition, name,
                                                              family=families.get(t))
                    seen_tabs[tkey] = cid
                    entry["containers"].append(cid)
                results[name] = entry
            except Exception as e:
                jrnl.append(common.journal_event(actor="stage3.contextual", action="press-outcome",
                            target=name, outcome=f"error: {e}", data={}))
                results[name] = {"error": str(e)}
            # ---- restore: leave the object story, undo until baseline ----
            try:
                sess.doc.Paragraphs(1).Range.Select()    # exits header story / deselects object
            except Exception:
                pass
            drv.ensure_frame_foreground(sess.frame)
            for _ in range(10):
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
        mw_path = KB / "ui" / "main-window.json"
        mw = json.loads(mw_path.read_text(encoding="utf-8"))
        add = [cid for cid in seen_tabs.values() if cid not in mw["child_containers"]]
        mw["child_containers"] = sorted(set(mw["child_containers"] + add))
        writer.write_container(mw)
        jrnl.append(common.journal_event(actor="stage3.contextual", action="write-containers",
                    target="ui/main-window.json", outcome="ok",
                    data={"contextual_containers": sorted(seen_tabs.values())}))
        print(json.dumps({"results": results,
                          "contextual_tabs": {f"{k[0]}/{k[1]}": v
                                              for k, v in seen_tabs.items()}},
                         indent=2, ensure_ascii=False))
    finally:
        sess.close()
        # kill only NEW excel pids our chart probe may have spawned
        excel_new = {p.pid for p in psutil.process_iter(["name"])
                     if (p.info["name"] or "").lower() == "excel.exe"} - excel_before
        for pid in excel_new:
            import subprocess
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
        jrnl.append(common.journal_event(actor="stage3.contextual", action="teardown",
                    target=f"pid={sess.pid}", outcome="closed",
                    data={"excel_killed": sorted(excel_new)}))


if __name__ == "__main__":
    main()

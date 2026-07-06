import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import config
from launcher import WordSession


def _compact_walk(el, fh, depth=0, max_depth=14, budget=None):
    """Compact one-line-per-node UIA dump: depth | control_type | name | aid | rect."""
    if budget is not None:
        budget[0] -= 1
        if budget[0] < 0:
            return
    try:
        ei = el.element_info
        r = ei.rectangle
        fh.write(f"{depth:2d} {'  ' * depth}ct={ei.control_type!r} "
                 f"name={ (ei.name or '')[:60]!r} aid={ei.automation_id or ''!r} "
                 f"rect=({r.left},{r.top},{r.right},{r.bottom})\n")
    except Exception as e:
        fh.write(f"{depth:2d} {'  ' * depth}<props error: {e}>\n")
        return
    if depth >= max_depth:
        return
    try:
        kids = el.children()
    except Exception:
        kids = []
    for k in kids:
        _compact_walk(k, fh, depth + 1, max_depth, budget)


def dump_tree():
    from pywinauto import Desktop
    s = WordSession.start(config.FIXTURES / "p0-blank.docx")
    rd = config.new_run_dir()
    try:
        win = Desktop(backend="uia").window(process=s.pid, top_level_only=True)
        win.dump_tree(depth=5, filename=str(rd / "tree-top.txt"))       # find the ribbon pane
        with open(rd / "tree-compact.txt", "w", encoding="utf-8") as fh:
            _compact_walk(win.wrapper_object(), fh, budget=[60000])
        print(f"stage-1 dump: {rd/'tree-top.txt'}")
        print(f"compact dump: {rd/'tree-compact.txt'}")
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


def enumerate_home():
    import json, uia, exposure
    s = WordSession.start(config.FIXTURES / "p0-text.docx")
    rd = config.new_run_dir()
    try:
        win = uia.attach(s)
        print("foreground after attach:", s.assert_foreground())
        dump = uia.enumerate_tab(win, "Home")
        out = rd / "home-enum.json"
        out.write_text(json.dumps(dump, indent=1, ensure_ascii=False), encoding="utf-8")
        exp = exposure.dump([out], rd / "exposure-map.json")
        per = {g["name"]: len(g["controls"]) for g in dump["groups"]}
        total = sum(per.values())
        print(f"groups={len(dump['groups'])} total={total} per-group={per}")
        # AutomationId==idMso spot-check
        bold = next((c for g in dump["groups"] for c in g["controls"] if c["name"] == "Bold"), None)
        print("Bold:", None if bold is None else
              {"aid": bold["automation_id"], "type": bold["control_type"],
               "patterns": bold["patterns"], "keytip": bold["access_key"],
               "shortcut": bold["accelerator_key"]})
        print("exposure flags:", exp["flags"])
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


def _split_child_rects(el):
    out = []
    for c in el.children():
        r = c.element_info.rectangle
        out.append((r.left, r.top, r.right, r.bottom))
    return out


def probe_archetypes():
    import uia, prober
    from journal import Journal
    s = WordSession.start(config.FIXTURES / "p0-text.docx")
    rd = config.new_run_dir()
    j = Journal(rd / "journal.jsonl")
    try:
        win = uia.attach(s)
        s.select_paragraph(1)
        armed = s.copy_fixture_text()
        j.append({"t": "clipboard-armed", "text": armed[:32]})
        j.append({"t": "state-established", "para": 1})

        groups = {g.element_info.name: g for g in uia._real_groups(win, "Home")}

        def find(group, aid=None, name=None, ct=None):
            for d in groups[group].descendants():
                ei = d.element_info
                if aid and ei.automation_id == aid:
                    return d
                if name and ei.name == name and (ct is None or ei.control_type == ct):
                    return d
            return None

        results = {}
        bold = find("Font", aid="Bold")
        results["Bold"] = prober.probe(s, win, j, bold, "ribbon.home.font.bold")

        fd = find("Font", aid="FontDialog")
        results["FontDialog"] = prober.probe(s, win, j, fd, "ribbon.home.font.fontdialog")

        num = find("Paragraph", aid="NumberingGalleryWord", ct="SplitButton")
        results["Numbering.flyout"] = prober.probe(
            s, win, j, num, "ribbon.home.paragraph.numberinggalleryword",
            zone="flyout", split_children=_split_child_rects(num))

        paste = find("Clipboard", name="Paste", ct="SplitButton")
        results["Paste.flyout"] = prober.probe(
            s, win, j, paste, "ribbon.home.clipboard.paste",
            zone="flyout", split_children=_split_child_rects(paste))

        # re-arm clipboard + place caret at DOC END so paste INSERTS (a real doc-hash delta);
        # pasting the clipboard back over its own source selection is a no-op -> unresolved.
        s.select_paragraph(1)
        s.copy_fixture_text()
        j.append({"t": "clipboard-armed", "text": "rearm"})
        end = s.doc.Content.End
        s.doc.Range(end - 1, end - 1).Select()
        results["Paste.primary"] = prober.probe(
            s, win, j, paste, "ribbon.home.clipboard.paste",
            zone="primary", split_children=_split_child_rects(paste))

        dictate = find("Voice", name="Dictate", ct="SplitButton")
        results["Dictate"] = prober.probe(s, win, j, dictate, "ribbon.home.voice.dictate")

        print("=== archetype outcomes ===")
        for k, v in results.items():
            print(f"  {k:18s} class={v['class']:11s} ref={v.get('ref')} mode={v['probe_mode']}")
        print("=== journal (reset-verified / ambiguous) ===")
        for r in j.records():
            if r["t"] in ("reset-verified", "ambiguous", "boundary", "surface-discovered"):
                print("  ", {kk: vv for kk, vv in r.items()
                             if kk not in ("ts", "seq", "schema_version")})
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


def _build_split(props, tab, gseg, primary_pr, flyout_pr, icon, bounds):
    import ids, build, schemas
    seg = ids.control_segment(props["automation_id"], props["name"])
    cid = ids.node_id("ribbon", tab, gseg, seg)

    def zone_action(pr):
        cls = pr["class"]
        if cls in ("unresolved", "feature"):
            return {"kind": "feature"}
        kind = build.KIND_MAP.get(cls, "feature")
        a = {"kind": kind}
        if kind.startswith("opens-") and pr.get("ref"):
            a["ref"] = pr["ref"]
        return a

    c = {"id": cid, "label": props["name"], "type": "split",
         "primary": {"action": zone_action(primary_pr)},
         "flyout": {"action": zone_action(flyout_pr)},
         "tooltip": props.get("help_text", ""), "keytip": props.get("access_key", ""),
         "idMso": props["automation_id"] or None,
         "capture": {"status": "complete", "probe_mode": "pressed-observed", "schema_version": 1}}
    if props.get("accelerator_key"):
        c["shortcut"] = props["accelerator_key"]
    if icon:
        c["icon"] = icon
    if bounds:
        c["bounds"] = bounds
    errs = schemas.validate_control(c)
    if errs:
        raise ValueError(f"invalid split {cid}: {errs}")
    return c


def _norm_result(pr):
    """Map an unresolved probe to a best-effort feature (the ambiguous journal record keeps
    the honest signal); pass other classes through for build.build_control."""
    if pr["class"] == "unresolved":
        return {"class": "feature", "ref": None, "boundary": None, "probe_mode": pr["probe_mode"]}
    return pr


def full_run(out_root, resume_dir=None):
    import time, json, win32gui, win32process
    import uia, prober, build, capture, shots, ids, schemas
    from journal import Journal
    from emit import emit
    from pywinauto import mouse
    from pywinauto.keyboard import send_keys

    run_dir = pathlib.Path(resume_dir) if resume_dir else config.new_run_dir()
    journal = Journal(run_dir / "journal.jsonl")
    done_controls = {r["control"]["id"] for r in journal.records() if r["t"] == "control-captured"}
    done_surfaces = {r["surface"] for r in journal.records() if r["t"] == "surface-captured"}

    s = WordSession.start(config.FIXTURES / "p0-text.docx")
    t0 = time.time()
    counts = {"controls": 0, "pressed": 0, "boundaries": 0, "surfaces": 0,
              "unresolved": 0, "ambiguous_notfound": 0}
    try:
        win = uia.attach(s)
        main = s._hwnd()
        prober.close_docked_panes(s, win)      # clean pane baseline (Word persists pane state)
        s.select_paragraph(1)
        armed = s.copy_fixture_text()
        if not resume_dir:
            journal.append({"t": "clipboard-armed", "text": armed[:24]})
            journal.append({"t": "state-established", "para": 1})

        lower = win.child_window(**uia.LOCATORS["lower_ribbon"])
        lr = lower.element_info.rectangle
        ribbon_rect = (lr.left, lr.top, lr.right, lr.bottom)
        ribbon_png = "screenshot__ribbon__home.png"
        shots.grab(ribbon_rect, run_dir / ribbon_png)
        dump = uia.enumerate_tab(win, "Home")

        def tops():
            a = []
            win32gui.EnumWindows(lambda h, x: (x.append(h) if win32gui.IsWindowVisible(h) else None) or True, a)
            return set(a)

        def new_win(before):
            for h in tops() - before:
                try:
                    _, wp = win32process.GetWindowThreadProcessId(h)
                    if wp == s.pid and h != main:
                        return h
                except Exception:
                    pass
            return None

        def safe_esc():
            fg = win32gui.GetForegroundWindow()
            _, fp = win32process.GetWindowThreadProcessId(fg)
            if fp != s.pid:
                uia._force_foreground(s._hwnd())
            send_keys("{ESC}"); time.sleep(0.35); send_keys("{ESC}"); time.sleep(0.25)

        def re_find(group_name, aid, name):
            for g in uia._real_groups(win, "Home"):
                if g.element_info.name != group_name:
                    continue
                for d in g.descendants():
                    ei = d.element_info
                    if aid and ei.automation_id == aid:
                        return d
                    if (not aid) and name and ei.name == name:
                        return d
            return None

        def icon_and_bounds(cid, rect):
            rb = shots.rel_bounds(rect, ribbon_rect)
            iname = "icon__" + cid + ".png"
            ok = False
            try:
                shots.crop_from(run_dir / ribbon_png,
                                (rb["x"], rb["y"], rb["x"] + rb["w"], rb["y"] + rb["h"]),
                                run_dir / iname)
                ok = shots.quality_ok(run_dir / iname)
            except Exception:
                ok = False
            return (iname if ok else None), {"in": ribbon_png, **rb}

        def reopen_capture(ref, cls, point):
            if not ref or ref in done_surfaces:
                return
            before = tops()
            uia._force_foreground(s._hwnd())
            mouse.click(coords=point)
            time.sleep(0.9)
            h = new_win(before)
            if not h:
                safe_esc()
                return
            try:
                if cls == "dialog":
                    capture.capture_dialog(s, journal, run_dir, ref, h)
                elif cls == "pane":
                    pass
                else:
                    capture.capture_popup(s, journal, run_dir, ref, win32gui.GetWindowRect(h))
                done_surfaces.add(ref)
                counts["surfaces"] += 1
            except Exception as e:
                journal.append({"t": "ambiguous", "control": ref, "reason": f"capture failed: {e}"})
            safe_esc()

        for group in dump["groups"]:
            gseg = ids.slugify(group["name"])
            for props in group["controls"]:
                seg = ids.control_segment(props["automation_id"], props["name"])
                cid = ids.node_id("ribbon", "home", gseg, seg)
                if cid in done_controls:
                    continue
                counts["controls"] += 1
                ct = props["control_type"]
                rect = tuple(props["rect"])
                icon, bounds = icon_and_bounds(cid, rect)

                b = config.boundary_for(cid)
                if b:
                    ctrl = build.build_control(props, "home", gseg,
                        {"class": "boundary", "ref": None, "boundary": b,
                         "probe_mode": "boundary-declared"}, icon, bounds)
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
                    counts["boundaries"] += 1
                    done_controls.add(cid)
                    continue

                if gseg == "clipboard":
                    s.select_paragraph(1)
                    s.copy_fixture_text()
                    if seg == "paste":
                        end = s.doc.Content.End
                        s.doc.Range(end - 1, end - 1).Select()

                el = re_find(group["name"], props["automation_id"], props["name"])
                if el is None:
                    journal.append({"t": "ambiguous", "control": cid, "reason": "element not found live"})
                    counts["ambiguous_notfound"] += 1
                    done_controls.add(cid)
                    continue

                if ct == "SplitButton":
                    kids = [(c.element_info.rectangle.left, c.element_info.rectangle.top,
                             c.element_info.rectangle.right, c.element_info.rectangle.bottom)
                            for c in el.children()]
                    pp = prober.probe(s, win, journal, el, cid, zone="primary", split_children=kids)
                    if pp["class"] == "feature":
                        s.select_paragraph(1)
                    el = re_find(group["name"], props["automation_id"], props["name"]) or el
                    pf = prober.probe(s, win, journal, el, cid, zone="flyout", split_children=kids)
                    ctrl = _build_split(props, "home", gseg, pp, pf, icon, bounds)
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
                    if pf["class"] == "popup" and pf.get("ref"):
                        reopen_capture(pf["ref"], "popup", prober.zone_point(rect, "flyout", kids))
                elif ct == "ComboBox":
                    kids = [(c.element_info.rectangle.left, c.element_info.rectangle.top,
                             c.element_info.rectangle.right, c.element_info.rectangle.bottom)
                            for c in el.children()]
                    pr = prober.probe(s, win, journal, el, cid, zone="flyout", split_children=kids)
                    ctrl = build.build_control(props, "home", gseg, _norm_result(pr), icon, bounds)
                    if pr["class"] == "unresolved":
                        ctrl["capture"]["status"] = "unresolved"; counts["unresolved"] += 1
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
                    if pr["class"] == "popup" and pr.get("ref"):
                        reopen_capture(pr["ref"], "popup", prober.zone_point(rect, "flyout", kids))
                else:
                    pr = prober.probe(s, win, journal, el, cid)
                    if pr["class"] == "feature":
                        s.select_paragraph(1)
                    ctrl = build.build_control(props, "home", gseg, _norm_result(pr), icon, bounds)
                    if pr["class"] == "unresolved":
                        ctrl["capture"]["status"] = "unresolved"; counts["unresolved"] += 1
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
                    if pr["class"] in ("dialog", "popup", "pane") and pr.get("ref"):
                        reopen_capture(pr["ref"], pr["class"], prober.zone_point(rect, None, None))
                counts["pressed"] += 1
                done_controls.add(cid)
                # a pane opened by this control (esp. the floating Styles pane, which _WwG
                # detection misses) must not persist -- it would suppress ribbon enumeration
                prober.close_docked_panes(s, win)

        secs = time.time() - t0
        stats = {"build": s.app.Build, "date": time.strftime("%Y-%m-%d"),
                 "throughput": {"secs": round(secs, 1), "controls": counts["controls"],
                                "secs_per_control": round(secs / max(counts["controls"], 1), 2)}}
        (run_dir / "stats.json").write_text(json.dumps({**counts, **stats}, indent=1), encoding="utf-8")
        rep = emit(journal, out_root, run_dir, stats)
        print("counts:", counts)
        print("emit:", {k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()
                        if k in ("written", "dangling", "orphans_deleted", "assets_copied",
                                 "missing_assets", "schema_errors", "unused_boundary_config")})
        print("secs_per_control:", stats["throughput"]["secs_per_control"], "total_secs:", round(secs, 1))
        print(f"RUN_DIR={run_dir}")
        return run_dir, rep
    finally:
        s.close()


def _tops():
    import win32gui
    a = []
    win32gui.EnumWindows(lambda h, x: (x.append(h) if win32gui.IsWindowVisible(h) else None) or True, a)
    return set(a)


def _new_win(pid, before, main):
    import win32gui, win32process
    for h in _tops() - before:
        try:
            _, wp = win32process.GetWindowThreadProcessId(h)
            if wp == pid and h != main:
                return h
        except Exception:
            pass
    return None


def capture_demo():
    import time, win32gui, win32process, uia, capture, schemas
    from journal import Journal
    from pywinauto import mouse
    from pywinauto.keyboard import send_keys
    s = WordSession.start(config.FIXTURES / "p0-text.docx")
    rd = config.new_run_dir()
    j = Journal(rd / "journal.jsonl")

    def esc():
        fg = win32gui.GetForegroundWindow()
        _, fp = win32process.GetWindowThreadProcessId(fg)
        if fp != s.pid:
            uia._force_foreground(s._hwnd())
        send_keys("{ESC}"); time.sleep(0.4); send_keys("{ESC}"); time.sleep(0.3)

    try:
        win = uia.attach(s)
        main = s._hwnd()
        s.select_paragraph(1)
        groups = {g.element_info.name: g for g in uia._real_groups(win, "Home")}

        def find(group, aid=None, name=None):
            for d in groups[group].descendants():
                ei = d.element_info
                if aid and ei.automation_id == aid:
                    return d
                if name and ei.name == name:
                    return d

        def flyout_pt(el):
            r = el.children()[-1].element_info.rectangle
            return ((r.left + r.right) // 2, (r.top + r.bottom) // 2)

        def center(el):
            r = el.element_info.rectangle
            return ((r.left + r.right) // 2, (r.top + r.bottom) // 2)

        def open_at(pt):
            before = _tops()
            uia._force_foreground(s._hwnd())
            mouse.click(coords=pt)
            time.sleep(1.0)
            return _new_win(s.pid, before, main)

        h = open_at(flyout_pt(find("Paragraph", aid="NumberingGalleryWord")))
        pop = capture.capture_popup(s, j, rd, "dropdowns/numbering-library", win32gui.GetWindowRect(h))
        nitems = sum(len(sec["items"]) for sec in pop["sections"])
        print(f"numbering popup: sections={len(pop['sections'])} items={nitems} "
              f"validate={schemas.validate_popup(pop)}")
        esc()

        h = open_at(center(find("Font", aid="FontDialog")))
        dlg = capture.capture_dialog(s, j, rd, "dialogs/font", h)
        nfields = sum(len(sec["fields"]) for t in dlg["tabs"] for sec in t["sections"])
        names = sorted({f["name"] for t in dlg["tabs"] for sec in t["sections"]
                        for f in sec["fields"] if f["name"]})
        print(f"font dialog: tabs={[t['name'] for t in dlg['tabs']]} fields={nfields} "
              f"buttons={[b['name'] for b in dlg['buttons']]} validate={schemas.validate_dialog(dlg)}")
        print(f"  field names: {names}")
        esc()

        qs = find("Styles", aid="QuickStylesGallery")
        moreb = [c for c in qs.children() if c.element_info.control_type == "Button"]
        if moreb:
            h = open_at(center(moreb[-1]))
            if h:
                sg = capture.capture_popup(s, j, rd, "dropdowns/styles-gallery", win32gui.GetWindowRect(h))
                print(f"styles gallery: items={sum(len(sec['items']) for sec in sg['sections'])} "
                      f"dynamic={sg.get('dynamic')} validate={schemas.validate_popup(sg)}")
                esc()
        print(f"RUN_DIR={rd}")
    finally:
        s.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump-tree", action="store_true")
    ap.add_argument("--enumerate-home", action="store_true")
    ap.add_argument("--probe-archetypes", action="store_true")
    ap.add_argument("--capture-demo", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--resume", metavar="RUN_DIR")
    ap.add_argument("--emit-repo", action="store_true", help="emit to parity/oracle/ui-structure")
    ap.add_argument("--emit-from", metavar="RUN_DIR", help="re-emit an existing journal (to repo)")
    a = ap.parse_args()
    if a.dump_tree:
        dump_tree()
    if a.enumerate_home:
        enumerate_home()
    if a.probe_archetypes:
        probe_archetypes()
    if a.capture_demo:
        capture_demo()
    if a.full or a.resume:
        out = config.OUTPUT_ROOT if a.emit_repo else (config.new_run_dir() / "emitted")
        rd = a.resume or None
        # when resuming, emit into the same scratch out-root next to the run
        full_run(out, resume_dir=rd)
    if a.emit_from:
        import pathlib as _pl
        from journal import Journal
        from emit import emit as _emit
        rdir = _pl.Path(a.emit_from)
        j = Journal(rdir / "journal.jsonl")
        rep = _emit(j, config.OUTPUT_ROOT if a.emit_repo else (rdir / "emitted"), rdir)
        print("re-emit:", {k: (len(v) if isinstance(v, list) else v) for k, v in rep.items()
                           if k in ("written", "dangling", "orphans_deleted", "missing_assets",
                                    "schema_errors", "unused_boundary_config")})

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


def _build_split(props, tab, gseg, primary_pr, flyout_pr, icon, bounds, primary_aid=""):
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
         "idMso": props["automation_id"] or primary_aid or None,
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
            try:
                if cls == "pane":
                    # docked panes (Clipboard) live in the frame; floating panes (Styles) are a new
                    # top-level MsoCommandBar window (B5)
                    h = new_win(before)
                    capture.capture_pane(s, journal, run_dir, ref, win, pane_hwnd=h)
                    done_surfaces.add(ref)
                    counts["surfaces"] += 1
                    prober.close_docked_panes(s, win)
                    return
                h = new_win(before)
                if not h:
                    safe_esc()
                    return
                if cls == "dialog":
                    # full-depth: recurse into child dialogs (DEPTH.md), sharing done_surfaces as the
                    # dedup 'seen' set so a dialog reached again is referenced, not re-drained
                    _drain_dialog(s, journal, run_dir, ref, h, done_surfaces, counts)
                    _close_dialogs(s)      # robustly unwind the whole modal chain
                    done_surfaces.add(ref)
                    return
                else:
                    prect = win32gui.GetWindowRect(h)
                    payload = capture.capture_popup(s, journal, run_dir, ref, prect)
                    counts["surfaces"] += 1
                    done_surfaces.add(ref)
                    # full-depth: drain dialog-opening popup items (Define New Bullet…, Paste
                    # Special…, More Colors…) — re-open the popup per item, click it, drain the dialog
                    _drain_popup(s, journal, run_dir, ref, point, prect, payload, done_surfaces, counts, win)
                    _close_dialogs(s)
                    return
                done_surfaces.add(ref)
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
                    # boundary double-entry (DESIGN section 4.8): the coverage edge and the node
                    # boundary block both derive from this single journal 'boundary' record.
                    journal.append({"t": "boundary", "from": cid, "kind": b.get("kind", "feature"),
                                    "policy": b["policy"], "decision": b["decision"]})
                    ctrl = build.build_control(props, "home", gseg,
                        {"class": "boundary", "ref": None, "boundary": b,
                         "probe_mode": "boundary-declared"}, icon, bounds)
                    # boundary SplitButtons (e.g. Dictate) have an empty wrapper AutomationId; recover
                    # idMso from the primary child so the engine bridge isn't null (#8).
                    if ct == "SplitButton" and not ctrl.get("idMso"):
                        bel = re_find(group["name"], props["automation_id"], props["name"])
                        kids = bel.children() if bel else []
                        if kids and kids[0].element_info.automation_id:
                            ctrl["idMso"] = kids[0].element_info.automation_id
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
                    children = el.children()
                    kids = [(c.element_info.rectangle.left, c.element_info.rectangle.top,
                             c.element_info.rectangle.right, c.element_info.rectangle.bottom)
                            for c in children]
                    primary_aid = children[0].element_info.automation_id if children else ""
                    pp = prober.probe(s, win, journal, el, cid, zone="primary", split_children=kids)
                    if pp["class"] == "feature":
                        s.select_paragraph(1)
                    el = re_find(group["name"], props["automation_id"], props["name"]) or el
                    pf = prober.probe(s, win, journal, el, cid, zone="flyout", split_children=kids)
                    ctrl = _build_split(props, "home", gseg, pp, pf, icon, bounds, primary_aid)
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
                    if pf["class"] == "popup" and pf.get("ref"):
                        reopen_capture(pf["ref"], "popup", prober.zone_point(rect, "flyout", kids))
                    if pp["class"] == "pane" and pp.get("ref"):     # split PRIMARY opens a pane (Find -> Nav pane)
                        reopen_capture(pp["ref"], "pane", prober.zone_point(rect, "primary", kids))
                elif props.get("is_gallery"):
                    # in-ribbon gallery: press the More chevron (last Button child) to open the full
                    # gallery popup; the strip itself applies-on-click (feature) with a moreRef.
                    moreb = [c for c in el.children() if c.element_info.control_type == "Button"]
                    ref = ids.surface_id("dropdowns", seg)
                    ctrl = build.build_control(props, "home", gseg,
                        {"class": "feature", "ref": None, "boundary": None,
                         "probe_mode": "pressed-observed"}, icon, bounds)
                    ctrl["moreRef"] = ref
                    if moreb:
                        r = moreb[-1].element_info.rectangle
                        journal.append({"t": "surface-discovered", "surface": ref, "entry": cid})
                        reopen_capture(ref, "popup", ((r.left + r.right) // 2, (r.top + r.bottom) // 2))
                    journal.append({"t": "control-captured", "tab": "home", "group": gseg,
                                    "group_label": group["name"], "control": ctrl})
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


def _tops_pid(pid):
    import win32gui, win32process
    a = set()

    def cb(h, _):
        try:
            if win32gui.IsWindowVisible(h):
                _, wp = win32process.GetWindowThreadProcessId(h)
                if wp == pid:
                    a.add(h)
        except Exception:
            pass
        return True

    win32gui.EnumWindows(cb, None)
    return a


def _child_dialog(s, before, exclude=None):
    """The new top-level that is a real dialog window. A flyout/popup must never be taken for the
    child: a DISABLED '...' item leaves its popup open and that popup itself got captured as a
    garbage 'dialog' (Set Numbering Value). We reject only flyout/popup CLASSES (blacklist) rather
    than whitelisting dialog classes — Word dialogs come in many classes (Apply Styles and the
    Insert Pictures chooser are top-level but not NUIDialog/#32770), and a whitelist silently
    dropped them. Disabled openers are already skipped upstream, so the leftover-flyout case can't
    arise; this is the second line of defence."""
    import win32gui
    import prober
    skip = {s._hwnd()} | (exclude or set())
    for h in sorted(_tops_pid(s.pid) - before):
        if h in skip:
            continue
        try:
            if win32gui.GetClassName(h) not in prober.POPUP_CLASSES:
                return h
        except Exception:
            pass
    return None


def _window_boundary(s, journal, child, entry, ref=None):
    """True (and journaled) if the child window is a config'd WINDOW boundary — a web-hosted
    chooser (Insert Pictures) whose body UIA cannot enumerate. Matched on the window's win32 text
    OR UIA name; the configured titles ('insert pictures'/'picture bullet') are specific enough that
    no class guard is needed (and the chooser is not a plain NUIDialog anyway). `ref` is the opener's
    discovered surface id: recording it lets the emitter resolve the ref OUT of the frontier
    (boundary-resolved, not uncaptured), keeping the 'frontier empty' gate attainable."""
    import win32gui
    from pywinauto import Desktop
    names = []
    try:
        names.append(win32gui.GetWindowText(child) or "")
    except Exception:
        pass
    try:
        names.append(Desktop(backend="uia").window(handle=child).element_info.name or "")
    except Exception:
        pass
    for nm in names:
        hit = config.BOUNDARY_WINDOW_TITLES.get(nm.strip().casefold())
        if hit:
            rec = {"t": "boundary", "from": entry, "kind": hit["kind"],
                   "policy": hit["policy"], "decision": hit["decision"]}
            if ref:
                rec["ref"] = ref
            journal.append(rec)
            return True
    return False


def _wait_child_dialog(s, before, exclude=None, timeout=2.5):
    """Poll for the child dialog instead of a single fixed sleep — a late-appearing child (Go To)
    is missed by one-shot detection, and re-clicking a DIALOG button to retry risks toggling state,
    so waiting is the safe retry for the dialog-button path."""
    import time
    deadline = time.time() + timeout
    while True:
        c = _child_dialog(s, before, exclude)
        if c or time.time() > deadline:
            return c
        time.sleep(0.3)


def _find_button_rect(dlg, dialog_hwnd, name):
    """The button's rectangle, searching ACROSS tabs. capture_dialog leaves a multi-tab dialog on its
    LAST tab, but an opener (Borders & Shading's 'Options...' is on the Borders tab, not the last
    Shading tab) may live on an earlier tab — so on a miss, activate each TabItem and retry."""
    import time
    from pywinauto import Desktop
    try:
        return dlg.child_window(title=name, control_type="Button").element_info.rectangle
    except Exception:
        pass
    try:
        tabs = Desktop(backend="uia").window(handle=dialog_hwnd).descendants(control_type="TabItem")
    except Exception:
        tabs = []
    for ti in tabs:
        try:
            ti.click_input()
            time.sleep(0.3)
            return dlg.child_window(title=name, control_type="Button").element_info.rectangle
        except Exception:
            continue
    return None


def _drain_dialog(s, journal, run_dir, surface_id, dialog_hwnd, seen, counts, depth=0, max_depth=8):
    """Depth-first: capture the dialog, then for each child-dialog opener button, click it, recurse
    into the child, and ESC back (DEPTH.md §2-3). `seen` dedups by surface id (breaks cycles / avoids
    re-traversal). Feature/toggle buttons open nothing -> leaves, no recursion."""
    import time
    import capture, ids, uia
    from pywinauto import Desktop, mouse
    from pywinauto.keyboard import send_keys
    import win32gui, win32process
    seen.add(surface_id)
    payload = capture.capture_dialog(s, journal, run_dir, surface_id, dialog_hwnd)
    counts["surfaces"] += 1
    if depth >= max_depth:
        return payload
    dlg = Desktop(backend="uia").window(handle=dialog_hwnd)
    is_word_options = (payload.get("title") or "").strip().casefold() == "word options"
    for b in payload.get("buttons", []):
        if b.get("action", {}).get("kind") != "opens-dialog":
            continue
        ref = b["action"].get("ref")
        if not ref or ref in seen:
            continue
        if b.get("enabled") is False:   # disabled '...' button: pressing captures garbage (cluster 7)
            journal.append({"t": "ambiguous", "control": ref,
                            "reason": "not drained: button disabled in this dialog state"})
            continue
        if is_word_options:
            # Word Options is the app-global settings window, not a Home surface. Its sub-dialogs
            # (File Locations, Web Options, Settings, Font Substitution) are generic Office, outside
            # Home scope — record as boundaries (D8) like the backstage, never drained.
            seen.add(ref)
            journal.append({"t": "boundary",
                            "from": ids.sub_addr(surface_id, "btn:" + ids.slugify(b["name"])),
                            "kind": "word-options-subdialog", "policy": "excluded",
                            "decision": "D8", "ref": ref})
            continue
        seen.add(ref)
        r = _find_button_rect(dlg, dialog_hwnd, b["name"])   # searches across tabs — an opener like
        if r is None:                                        # 'Options...' is not always on the tab
            journal.append({"t": "ambiguous", "control": ref,     # capture_dialog left active
                            "reason": "opens-dialog: button not found on any tab"})
            continue
        before = _tops_pid(s.pid)
        uia._force_foreground(dialog_hwnd)
        mouse.click(coords=((r.left + r.right) // 2, (r.top + r.bottom) // 2))
        time.sleep(0.6)
        child = _wait_child_dialog(s, before, exclude={dialog_hwnd})
        if child:
            entry = ids.sub_addr(surface_id, "btn:" + ids.slugify(b["name"]))
            if _window_boundary(s, journal, child, entry, ref=ref):
                _dismiss(s, child)      # boundary: recorded, never drained
            else:
                _drain_dialog(s, journal, run_dir, ref, child, seen, counts, depth + 1, max_depth)
                _dismiss(s, child)      # close EXACTLY the child (parent stays open, chain unwinds)
        else:
            journal.append({"t": "ambiguous", "control": ref,
                            "reason": "opens-dialog: no child dialog after wait"})
    return payload


def _dismiss(s, hwnd):
    """Close a single dialog WITHOUT applying: click its Cancel/Close button (some Office dialogs
    like Format Text Effects ignore ESC — they only close via their Close button), else fall back to
    ESC. Clicking Cancel/Close never commits changes."""
    import time
    import win32gui
    import uia
    from pywinauto import Desktop, mouse
    from pywinauto.keyboard import send_keys
    try:
        dlg = Desktop(backend="uia").window(handle=hwnd)
        for nm in ("Cancel", "Close"):
            try:
                r = dlg.child_window(title=nm, control_type="Button").element_info.rectangle
            except Exception:
                continue
            uia._force_foreground(hwnd)
            mouse.click(coords=((r.left + r.right) // 2, (r.top + r.bottom) // 2))
            time.sleep(0.4)
            if not win32gui.IsWindowVisible(hwnd):
                return True
    except Exception:
        pass
    for _ in range(4):
        if not win32gui.IsWindowVisible(hwnd):
            return True
        if win32gui.GetForegroundWindow() != hwnd:
            try:
                uia._force_foreground(hwnd)
            except Exception:
                pass
        send_keys("{ESC}")
        time.sleep(0.35)
    return not win32gui.IsWindowVisible(hwnd)


def _drain_popup(s, journal, run_dir, popup_id, point, popup_rect, payload, seen, counts, win=None):
    """Popup items that open a DIALOG (Paste Special…, Define New Bullet…, More Colors…): a popup
    item-click dismisses the popup, so for each dialog-item we re-open the popup (click its flyout
    `point`), click the item at its captured bounds, then drain+close the dialog. (DEPTH.md §3.)"""
    import time
    import capture
    import ids
    import prober
    import uia
    import win32gui
    from pywinauto import mouse
    from pywinauto.keyboard import send_keys

    def _items(kind):
        return [(it["action"]["ref"], it["bounds"], it["id"])
                for sec in payload.get("sections", []) for it in sec.get("items", [])
                if it.get("action", {}).get("kind") == kind
                and it["action"].get("ref") and it["action"]["ref"] not in seen
                and it.get("enabled") is not False]

    # DISABLED openers are never pressed (pressing one leaves the popup open and the popup itself
    # got captured as a garbage 'dialog' — Set Numbering Value). Their ref stays in the frontier:
    # discovered, but unreachable in this document state.
    for sec in payload.get("sections", []):
        for it in sec.get("items", []):
            if it.get("enabled") is False and it.get("action", {}).get("ref"):
                journal.append({"t": "ambiguous", "control": it["action"]["ref"],
                                "reason": "not drained: item disabled in this document state"})

    send_keys("{ESC}")                                  # close the popup left open by capture
    time.sleep(0.3)

    # (a) items that open a DIALOG: re-open popup, click item, drain the dialog
    for dref, b, itid in _items("opens-dialog"):
        if dref in seen:
            continue
        seen.add(dref)
        ix = popup_rect[0] + b["x"] + b["w"] // 2
        iy = popup_rect[1] + b["y"] + b["h"] // 2
        child = None
        for _attempt in range(2):       # one retry: Go To's child window intermittently missed
            _close_dialogs(s)
            before = _tops_pid(s.pid)
            uia._force_foreground(s._hwnd())
            mouse.click(coords=point)
            time.sleep(0.7)
            mouse.click(coords=(ix, iy))
            time.sleep(0.6)
            child = _wait_child_dialog(s, before)
            if child or (win is not None and prober._has_close_pane(win)):
                break                   # got the dialog, or a PANE opened (not a flake)
        if child:
            if _window_boundary(s, journal, child, ids.sub_addr(popup_id, itid), ref=dref):
                _dismiss(s, child)      # boundary (web-hosted chooser): recorded, never drained
            else:
                _drain_dialog(s, journal, run_dir, dref, child, seen, counts)
        elif win is not None and prober._has_close_pane(win):
            # the '...' item opened a PANE, not a dialog (e.g. Selection Pane…). Capture it as a pane
            # AND emit a `surface-retyped` so the emitter repoints the item's action (opens-dialog ->
            # opens-pane), drops the phantom dialog ref from the frontier, and gives the pane its
            # entry_point. (Static "..." => dialog heuristic corrected by what pressing actually did.)
            pref = "panes/" + dref.split("/")[-1]
            journal.append({"t": "surface-retyped", "surface": popup_id, "item": itid,
                            "old_ref": dref, "kind": "opens-pane", "ref": pref})
            if pref not in seen:
                seen.add(pref)
                try:
                    capture.capture_pane(s, journal, run_dir, pref, win)
                    counts["surfaces"] += 1
                except Exception as e:
                    journal.append({"t": "ambiguous", "control": pref, "reason": f"pane: {e}"})
            prober.close_docked_panes(s, win)
        else:
            journal.append({"t": "ambiguous", "control": dref,
                            "reason": "opens-dialog: no child dialog after retry"})
        _close_dialogs(s)

    # (b) SUBMENU items: open the popup ONCE and hover each item in turn (hovering the next auto-
    # closes the previous submenu) — far cheaper than re-opening per item. Capture with
    # detect_submenus=False (one level; deeper submenus are rare and would explode the cost).
    subs = _items("submenu")
    if subs:
        _close_dialogs(s)
        send_keys("{ESC}")
        time.sleep(0.3)
        uia._force_foreground(s._hwnd())
        mouse.click(coords=point)                       # open the parent popup once
        time.sleep(0.7)
        parkx = popup_rect[0] + (popup_rect[2] - popup_rect[0]) // 2
        parky = popup_rect[1] + 2                        # top border of the parent popup (no item)
        mouse.move(coords=(parkx, parky))               # settle before the first hover (mirror capture)
        time.sleep(0.35)
        prev_sub = None
        reopen_needed = False
        for sref, b, _itid in subs:
            if sref in seen:
                continue
            seen.add(sref)
            ix = popup_rect[0] + b["x"] + b["w"] // 2
            iy = popup_rect[1] + b["y"] + b["h"] // 2
            if reopen_needed:            # draining a submenu dialog last iteration closed the parent
                _close_dialogs(s)
                send_keys("{ESC}")
                time.sleep(0.3)
                uia._force_foreground(s._hwnd())
                mouse.click(coords=point)
                time.sleep(0.7)
                mouse.move(coords=(parkx, parky))
                time.sleep(0.35)
                prev_sub = None
                reopen_needed = False
            # Collapse any previously-open submenu FIRST: park on the parent popup's top border and
            # wait for the prior child window to close. Otherwise its flyout is still on screen and we
            # capture the STALE neighbour's content (Reflection/Number-Styles were getting Shadow's).
            if prev_sub is not None:
                mouse.move(coords=(parkx, parky))
                for _ in range(10):
                    if not win32gui.IsWindowVisible(prev_sub):
                        break
                    time.sleep(0.1)
            before = _tops_pid(s.pid)                    # recompute per item (never a stale global base)
            mouse.move(coords=(ix, iy))                 # hover (never click a submenu item)
            time.sleep(0.6)
            # the RIGHT-cascading window is the submenu; a ScreenTip over the item is rejected (same
            # position test _hover_submenus used to flag it), so we never capture a tooltip's content
            sub = capture._cascade_window(_tops_pid(s.pid) - before, popup_rect)
            if sub is None:                              # gradient / list-level flyouts render late
                time.sleep(0.4)
                sub = capture._cascade_window(_tops_pid(s.pid) - before, popup_rect)
            # Office RECYCLES the small pool of cascade-submenu HWNDs, so a genuinely-new item's flyout
            # can land on the SAME handle as the previous one — the collapse-wait above already ensured
            # the prior flyout was hidden, so any cascade window here is THIS item's. (The old
            # `sub != prev_sub` guard rejected the reused handle and dropped real submenus.)
            if sub is None:
                journal.append({"t": "ambiguous", "control": sref,
                                "reason": "submenu: no new window on hover"})
                continue
            sr = win32gui.GetWindowRect(sub)
            prev_sub = sub
            try:
                sub_payload = capture.capture_popup(s, journal, run_dir, sref, sr,
                                                    detect_submenus=False)
                counts["surfaces"] += 1
            except Exception as e:
                sub_payload = None
                journal.append({"t": "ambiguous", "control": sref, "reason": f"submenu: {e}"})
            # Drain ONE opens-dialog item WHILE the submenu is open and correctly positioned (Shadow →
            # 'Shadow Options…'). Re-opening the submenu afterwards proved unreliable, so click it now;
            # the click closes the submenu + parent, so flag a re-open for the next submenu item.
            for sec in (sub_payload or {}).get("sections", []):
                hit = False
                for it in sec.get("items", []):
                    a = it.get("action", {})
                    if not (a.get("kind") == "opens-dialog" and a.get("ref")
                            and a["ref"] not in seen and it.get("enabled") is not False):
                        continue
                    dref, db, ditid = a["ref"], it["bounds"], it.get("id", "")
                    seen.add(dref)
                    dcx = sr[0] + db["x"] + db["w"] // 2
                    dcy = sr[1] + db["y"] + db["h"] // 2
                    # Move INTO the submenu (its left edge, on the item's row) FIRST — a straight
                    # diagonal from the parent item to the dialog item crosses the parent↔submenu gap
                    # and collapses the cascade. Stepping along the submenu keeps it open, then click.
                    mouse.move(coords=(sr[0] + 10, dcy))
                    time.sleep(0.25)
                    dbefore = _tops_pid(s.pid)
                    mouse.click(coords=(dcx, dcy))
                    time.sleep(0.7)
                    child = _wait_child_dialog(s, dbefore)
                    if child:
                        _drain_dialog(s, journal, run_dir, dref, child, seen, counts)
                        _dismiss(s, child)
                    elif win is not None and prober._has_close_pane(win):
                        # 'Shadow/Glow/Reflection Options…' opens a docked Format-Shape TASK PANE, not
                        # a modal dialog (no top-level window appears — instrumented new=[]). Same as
                        # Selection Pane: capture it as a pane and retype the item opens-dialog→opens-pane.
                        pref = "panes/" + dref.split("/")[-1]
                        journal.append({"t": "surface-retyped", "surface": sref, "item": ditid,
                                        "old_ref": dref, "kind": "opens-pane", "ref": pref})
                        if pref not in seen:
                            seen.add(pref)
                            try:
                                capture.capture_pane(s, journal, run_dir, pref, win)
                                counts["surfaces"] += 1
                            except Exception as e:
                                journal.append({"t": "ambiguous", "control": pref, "reason": f"pane: {e}"})
                        prober.close_docked_panes(s, win)
                    else:
                        journal.append({"t": "ambiguous", "control": dref,
                                        "reason": "submenu-dialog: no child dialog and no pane"})
                    reopen_needed = True
                    hit = True
                    break
                if hit:
                    break
        send_keys("{ESC}")
        time.sleep(0.3)


def _close_dialogs(s, tries=12):
    """Close every PID top-level dialog except the frame (robust modal-chain teardown after a drain).
    Dismisses the topmost first via its Cancel/Close button (ESC is unreliable for some Office
    dialogs), unwinding the stack; a stuck modal would otherwise block every later ribbon control."""
    import win32gui
    main = s._hwnd()
    for _ in range(tries):
        extra = [h for h in _tops_pid(s.pid) if h != main and win32gui.IsWindowVisible(h)]
        if not extra:
            return True
        if not _dismiss(s, extra[-1]):
            return False
    return False


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

import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from journal import Journal
from emit import emit


def _mini(tmp_path):
    j = Journal(tmp_path / "j.jsonl")
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.bold", "label": "Bold", "type": "toggle",
                          "idMso": "Bold", "action": {"kind": "toggles"},
                          "capture": {"status": "complete", "probe_mode": "pattern-inferred",
                                      "schema_version": 1}}})
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.fontdialog", "label": "Font Settings",
                          "type": "launcher",
                          "action": {"kind": "opens-dialog", "ref": "dialogs/font"},
                          "capture": {"status": "complete", "probe_mode": "pressed-observed",
                                      "schema_version": 1}}})
    j.append({"t": "surface-discovered", "surface": "dialogs/font", "entry": "ribbon.home.font.fontdialog"})
    j.append({"t": "surface-captured", "surface": "dialogs/font",
              "payload": {"id": "dialogs/font", "title": "Font", "modal": True,
                          "schema_version": 1, "tabs": [], "buttons": []}})
    j.append({"t": "boundary", "from": "ribbon.file", "kind": "opens-backstage",
              "policy": "excluded", "decision": "D4"})
    return j


def test_entry_points_and_closure(tmp_path):
    out = tmp_path / "out"
    rep = emit(_mini(tmp_path), out, tmp_path)
    assert rep["dangling"] == []
    font = json.loads((out / "dialogs" / "font.json").read_text(encoding="utf-8"))
    assert font["entry_points"] == ["ribbon.home.font.fontdialog"]
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert any(e["from"] == "ribbon.file" and e["decision"] == "D4" for e in cov["boundaries"])
    man = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    # E4 regression: a boundary journal record must reach coverage AND the manifest count,
    # and a USED boundary must NOT appear in unused_boundary_config.
    assert man["coverage"]["boundaries"] == 1
    assert "ribbon.file" not in man["coverage"]["unused_boundary_config"]


def test_surface_retyped_reconciliation(tmp_path):
    """A '...' popup item is statically classified opens-dialog, but pressing it opened a PANE.
    A surface-retyped record must: repoint the item action, give the pane its entry_point, and
    drain the phantom dialog ref out of the frontier (no dangling)."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    # popup with a "Selection Pane..." item statically typed opens-dialog -> dialogs/selection-pane
    j.append({"t": "control-captured", "tab": "home", "group": "editing",
              "control": {"id": "ribbon.home.editing.selectmenu", "label": "Select", "type": "menu",
                          "action": {"kind": "opens-menu", "ref": "dropdowns/selectmenu"},
                          "capture": {"status": "complete", "probe_mode": "pressed-observed",
                                      "schema_version": 1}}})
    j.append({"t": "surface-discovered", "surface": "dropdowns/selectmenu",
              "entry": "ribbon.home.editing.selectmenu"})
    j.append({"t": "surface-discovered", "surface": "dialogs/selection-pane",
              "entry": "dropdowns/selectmenu#selection-pane"})
    j.append({"t": "surface-captured", "surface": "dropdowns/selectmenu",
              "payload": {"id": "dropdowns/selectmenu", "schema_version": 1,
                          "sections": [{"kind": "menu-items", "items": [
                              {"id": "selection-pane", "label": "Selection Pane...",
                               "action": {"kind": "opens-dialog", "ref": "dialogs/selection-pane"},
                               "bounds": {"x": 2, "y": 2, "w": 300, "h": 28}}]}]}})
    # pressing it revealed a PANE, captured at panes/selection-pane, + the retype record
    j.append({"t": "surface-captured", "surface": "panes/selection-pane",
              "payload": {"id": "panes/selection-pane", "schema_version": 1, "docked": True,
                          "sections": [{"kind": "controls", "items": []}]}})
    j.append({"t": "surface-retyped", "surface": "dropdowns/selectmenu", "item": "selection-pane",
              "old_ref": "dialogs/selection-pane", "kind": "opens-pane",
              "ref": "panes/selection-pane"})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []                                    # phantom dialog ref resolved
    sel = json.loads((out / "dropdowns" / "selectmenu.json").read_text(encoding="utf-8"))
    it = sel["sections"][0]["items"][0]
    assert it["action"] == {"kind": "opens-pane", "ref": "panes/selection-pane"}   # repointed
    pane = json.loads((out / "panes" / "selection-pane.json").read_text(encoding="utf-8"))
    assert pane["entry_points"] == ["dropdowns/selectmenu#selection-pane"]           # backfilled
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert "dialogs/selection-pane" not in cov["frontier"]          # phantom drained from frontier


def _dlg_payload(sid, title, fields, buttons=("OK", "Cancel")):
    return {"id": sid, "title": title, "modal": True, "schema_version": 1,
            "tabs": [{"name": title, "screenshot": "x.png",
                      "sections": [{"title": "", "fields": [
                          {"name": f, "type": "text", "bounds": {"x": 0, "y": 0, "w": 1, "h": 1}}
                          for f in fields]}],
                      "buttons": []}],
            "buttons": [{"name": b, "action": {"kind": "feature"}} for b in buttons]}


def test_structural_dialog_dedup_merges_same_dialog(tmp_path):
    """The same physical dialog captured under two ids (Line Spacing Options… vs the Paragraph
    launcher) merges to the id matching the dialog's own TITLE; refs and entry_points follow."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    j.append({"t": "surface-discovered", "surface": "dialogs/paragraph",
              "entry": "ribbon.home.paragraph.launcher"})
    j.append({"t": "surface-captured", "surface": "dialogs/paragraph",
              "payload": _dlg_payload("dialogs/paragraph", "Paragraph", ["Alignment:", "Left:"])})
    # the popup item that captured the SAME dialog under its item-derived id
    j.append({"t": "surface-captured", "surface": "dropdowns/linespacinggallery",
              "payload": {"id": "dropdowns/linespacinggallery", "schema_version": 1,
                          "sections": [{"kind": "menu-items", "items": [
                              {"id": "line-spacing-options", "label": "Line Spacing Options…",
                               "action": {"kind": "opens-dialog",
                                          "ref": "dialogs/line-spacing-options"},
                               "bounds": {"x": 1, "y": 1, "w": 10, "h": 10}}]}]}})
    j.append({"t": "surface-discovered", "surface": "dialogs/line-spacing-options",
              "entry": "dropdowns/linespacinggallery#line-spacing-options"})
    j.append({"t": "surface-captured", "surface": "dialogs/line-spacing-options",
              "payload": _dlg_payload("dialogs/line-spacing-options", "Paragraph",
                                      ["Alignment:", "Left:"])})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert not (out / "dialogs" / "line-spacing-options.json").exists()      # duplicate not emitted
    para = json.loads((out / "dialogs" / "paragraph.json").read_text(encoding="utf-8"))
    assert set(para["entry_points"]) == {"ribbon.home.paragraph.launcher",
                                         "dropdowns/linespacinggallery#line-spacing-options"}
    pop = json.loads((out / "dropdowns" / "linespacinggallery.json").read_text(encoding="utf-8"))
    assert pop["sections"][0]["items"][0]["action"]["ref"] == "dialogs/paragraph"  # ref rewritten
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert "dialogs/line-spacing-options" not in cov["frontier"]


def test_structural_dialog_dedup_distinguishes_different_dialogs(tmp_path):
    """Same title but different FIELDS = different dialogs — never merged (scoped Options dialogs)."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    for sid, fields in (("dialogs/sort-options", ["Separator:", "Case sensitive"]),
                        ("dialogs/borders-and-shading-options", ["Top:", "Measure from:"])):
        j.append({"t": "surface-discovered", "surface": sid, "entry": "ribbon.home.font.fontdialog"})
        j.append({"t": "surface-captured", "surface": sid,
                  "payload": _dlg_payload(sid, "Options", fields)})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert (out / "dialogs" / "sort-options.json").exists()
    assert (out / "dialogs" / "borders-and-shading-options.json").exists()


def test_dedup_rewrites_child_entry_points(tmp_path):
    """Review defect A: both Paragraph captures drain their 'Tabs...' child under scoped ids; the
    dedup must rewrite the child's entry sub-addrs to the KEEPER parent — never a back-link into a
    deleted duplicate — and the entry-closure check must stay clean."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    # the popup whose item is one of the two entry routes (its stem must be a known surface for
    # the new entry-closure check — in a real run it is always captured before its items drain)
    j.append({"t": "surface-discovered", "surface": "dropdowns/linespacinggallery",
              "entry": "ribbon.home.paragraph.linespacing"})
    tabs_btn = lambda parent: {"name": "Tabs...", "action": {
        "kind": "opens-dialog", "ref": f"dialogs/{parent}-tabs"}}
    for parent, entry in (("paragraph", "ribbon.home.paragraph.launcher"),
                          ("line-spacing-options",
                           "dropdowns/linespacinggallery#line-spacing-options")):
        j.append({"t": "surface-discovered", "surface": f"dialogs/{parent}", "entry": entry})
        pl = _dlg_payload(f"dialogs/{parent}", "Paragraph", ["Alignment:", "Left:"])
        pl["buttons"].append(tabs_btn(parent))
        j.append({"t": "surface-captured", "surface": f"dialogs/{parent}", "payload": pl})
        j.append({"t": "surface-discovered", "surface": f"dialogs/{parent}-tabs",
                  "entry": f"dialogs/{parent}#btn:tabs"})
        j.append({"t": "surface-captured", "surface": f"dialogs/{parent}-tabs",
                  "payload": _dlg_payload(f"dialogs/{parent}-tabs", "Tabs",
                                          ["Tab stop position:", "Default tab stops:"])})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert not (out / "dialogs" / "line-spacing-options.json").exists()
    assert not (out / "dialogs" / "paragraph-tabs.json").exists()      # merged into the other twin
    child = json.loads((out / "dialogs" / "line-spacing-options-tabs.json")
                       .read_text(encoding="utf-8"))
    # the stale 'dialogs/line-spacing-options#btn:tabs' back-link must have been rewritten to the
    # keeper parent (and thus collapsed with its twin)
    assert child["entry_points"] == ["dialogs/paragraph#btn:tabs"]
    para = json.loads((out / "dialogs" / "paragraph.json").read_text(encoding="utf-8"))
    tabs_refs = [b["action"]["ref"] for b in para["buttons"] if b["name"] == "Tabs..."]
    assert tabs_refs == ["dialogs/line-spacing-options-tabs"]          # ref follows the child keeper


def test_screenshot_dedup_merges_fieldless_dialog(tmp_path):
    """Two captures of the same 0-field 'Format Text Effects' panel (empty title, identical
    screenshot) reached from Font and from More Underlines must merge by screenshot hash."""
    out = tmp_path / "out"
    (tmp_path / "dialogs__te-a.png").write_bytes(b"IDENTICAL-TEXT-EFFECTS-PIXELS")
    (tmp_path / "dialogs__te-b.png").write_bytes(b"IDENTICAL-TEXT-EFFECTS-PIXELS")  # byte-identical
    j = _mini(tmp_path)
    def te(sid, shot):
        return {"id": sid, "title": "", "modal": True, "schema_version": 1,
                "tabs": [{"name": "Main", "screenshot": shot, "sections": [], "buttons": []}],
                "buttons": [{"name": "Text Fill", "action": {"kind": "feature"}},
                            {"name": "OK", "action": {"kind": "feature"}, "role": "default"}]}
    # both discovered from the same Font 'Text Effects...' button (the real crawl's entry for both)
    for sid, shot in (("dialogs/font-text-effects", "dialogs__te-a.png"),
                      ("dialogs/more-underlines-text-effects", "dialogs__te-b.png")):
        j.append({"t": "surface-discovered", "surface": sid, "entry": "dialogs/font#btn:text-effects"})
        j.append({"t": "surface-captured", "surface": sid, "payload": te(sid, shot)})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert not (out / "dialogs" / "more-underlines-text-effects.json").exists()   # merged away
    keep = json.loads((out / "dialogs" / "font-text-effects.json").read_text(encoding="utf-8"))
    assert keep["entry_points"] == ["dialogs/font#btn:text-effects"]              # de-duped to one


def test_fieldless_dialogs_with_different_screenshots_stay_split(tmp_path):
    """Two different 0-field alerts (same empty structure, DIFFERENT screenshot) must NOT merge."""
    out = tmp_path / "out"
    (tmp_path / "dialogs__al-a.png").write_bytes(b"ALERT-ONE-PIXELS")
    (tmp_path / "dialogs__al-b.png").write_bytes(b"ALERT-TWO-DIFFERENT-PIXELS")
    j = _mini(tmp_path)
    def al(sid, shot):
        return {"id": sid, "title": "Microsoft Word", "modal": True, "schema_version": 1,
                "tabs": [{"name": "Microsoft Word", "screenshot": shot, "sections": [], "buttons": []}],
                "buttons": [{"name": "OK", "action": {"kind": "feature"}, "role": "default"}]}
    for sid, shot in (("dialogs/alert-a", "dialogs__al-a.png"), ("dialogs/alert-b", "dialogs__al-b.png")):
        j.append({"t": "surface-discovered", "surface": sid, "entry": "ribbon.home.font.fontdialog"})
        j.append({"t": "surface-captured", "surface": sid, "payload": al(sid, shot)})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert (out / "dialogs" / "alert-a.json").exists() and (out / "dialogs" / "alert-b.json").exists()


def test_alert_dialogs_never_merge(tmp_path):
    """Review defect C: two DIFFERENT alert boxes (same title, OK button, zero fields) are
    indistinguishable by the signature — they must both be emitted, never merged."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    for sid in ("dialogs/alert-a", "dialogs/alert-b"):
        j.append({"t": "surface-discovered", "surface": sid, "entry": "ribbon.home.font.fontdialog"})
        j.append({"t": "surface-captured", "surface": sid,
                  "payload": _dlg_payload(sid, "Microsoft Word", [], buttons=("OK",))})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    assert (out / "dialogs" / "alert-a.json").exists()
    assert (out / "dialogs" / "alert-b.json").exists()


def test_disabled_state_resolves_frontier(tmp_path):
    """A discovered ref left un-drained because Word disabled the opener leaves the frontier and is
    documented under coverage.disabled_state — not silently dropped, not a dangling ref."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    j.append({"t": "surface-discovered", "surface": "dialogs/set-numbering-value"})
    j.append({"t": "ambiguous", "control": "dialogs/set-numbering-value",
              "reason": "not drained: item disabled in this document state"})
    # an ordinary ambiguous (a flake) must NOT be treated as disabled-resolved
    j.append({"t": "surface-discovered", "surface": "dialogs/flaky"})
    j.append({"t": "ambiguous", "control": "dialogs/flaky",
              "reason": "opens-dialog: no child dialog after wait"})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert "dialogs/set-numbering-value" not in cov["frontier"]
    assert [d["ref"] for d in cov["disabled_state"]] == ["dialogs/set-numbering-value"]
    assert "dialogs/flaky" in cov["frontier"]                    # genuine miss stays in frontier


def test_window_boundary_ref_resolves_frontier(tmp_path):
    """Review defect B: a window-boundary (Insert Pictures chooser) carries the opener's discovered
    ref — the ref must leave the frontier (boundary-resolved) and not count as dangling."""
    out = tmp_path / "out"
    j = _mini(tmp_path)
    j.append({"t": "surface-discovered", "surface": "dialogs/define-new-bullet-picture",
              "entry": "dialogs/define-new-bullet#btn:picture"})
    j.append({"t": "boundary", "from": "dialogs/define-new-bullet#btn:picture",
              "kind": "web-hosted-chooser", "policy": "excluded", "decision": "D8",
              "ref": "dialogs/define-new-bullet-picture"})
    rep = emit(j, out, tmp_path)
    assert rep["dangling"] == []
    cov = json.loads((out / "coverage.json").read_text(encoding="utf-8"))
    assert "dialogs/define-new-bullet-picture" not in cov["frontier"]
    assert any(b.get("ref") == "dialogs/define-new-bullet-picture" for b in cov["boundaries"])


def test_dangling_and_orphans(tmp_path):
    out = tmp_path / "out"; (out / "dialogs").mkdir(parents=True)
    (out / "dialogs" / "stale.json").write_text("{}", encoding="utf-8")
    j = _mini(tmp_path)
    j.append({"t": "control-captured", "tab": "home", "group": "font",
              "control": {"id": "ribbon.home.font.ghost", "label": "Ghost", "type": "menu",
                          "action": {"kind": "opens-menu", "ref": "dropdowns/ghost"},
                          "capture": {"status": "complete", "probe_mode": "pressed-observed",
                                      "schema_version": 1}}})
    rep = emit(j, out, tmp_path)
    assert "dropdowns/ghost" in rep["dangling"]
    assert any(str(p).endswith("stale.json") for p in rep["orphans_deleted"])

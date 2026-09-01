"""Reconciling emitter (DESIGN section 5.5, 4.8). Regenerates the full output set from the
journal, copies referenced PNGs, writes hash manifests + coverage + manifest, validates every
file, checks reference closure, and deletes orphaned files under the managed dirs.

Asset convention (T12 writes PNGs into run_dir with these basenames; emit copies + rewrites):
  icon__<control-id>.png     -> out_root/icons/<base>       (rewritten "icons/<base>")
  screenshot__<...>.png / any other .png -> out_root/screenshots/<base> ("screenshots/<base>")
"""
import json, hashlib, shutil, time, pathlib
import config, ids, schemas, enrich

MANAGED_DIRS = ["ribbon", "dropdowns", "dialogs", "panes", "canvas", "icons", "screenshots"]


def _sha_size(path):
    b = pathlib.Path(path).read_bytes()
    return {"sha256": hashlib.sha256(b).hexdigest(), "size": len(b)}


def _collect_surface_refs(doc):
    out = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("ref", "moreRef") and isinstance(v, str) and ids.is_surface_ref(v):
                    out.append(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(doc)
    return out


def _process_assets(doc, run_dir, out_root, copied, missing):
    def rewrite(parent, key):
        val = parent.get(key)
        if not isinstance(val, str) or not val.endswith(".png"):
            return
        base = pathlib.Path(val).name
        destdir = "icons" if base.startswith("icon__") else "screenshots"
        rel = f"{destdir}/{base}"
        src = run_dir / base
        if src.exists():
            dst = out_root / destdir / base
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dst)
            copied[rel] = _sha_size(dst)
        else:
            missing.append(rel)
        parent[key] = rel

    def walk(o):
        if isinstance(o, dict):
            for k in list(o.keys()):
                if k in ("icon", "screenshot", "preview"):
                    rewrite(o, k)
                elif k == "bounds" and isinstance(o[k], dict) and "in" in o[k]:
                    rewrite(o[k], "in")
                else:
                    walk(o[k])
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(doc)


def emit(journal, out_root, run_dir, stats=None, descriptions=None):
    out_root = pathlib.Path(out_root)
    run_dir = pathlib.Path(run_dir)
    recs = journal.records()
    descriptions = enrich.load_descriptions() if descriptions is None else descriptions

    groups_by_tab = {}      # tab -> {group_seg: {"label": str, "controls": []}}
    surfaces = {}           # surface_id -> payload
    discovered = []         # [(surface, entry)]
    boundaries = []
    disabled_state = []     # discovered refs left un-drained because Word disabled the opener
    retypes = []            # press-time corrections of a statically-misclassified item
    for r in recs:
        t = r["t"]
        if t == "control-captured":
            g = groups_by_tab.setdefault(r["tab"], {}).setdefault(
                r["group"], {"label": r.get("group_label", r["group"]), "controls": []})
            g["controls"].append(r["control"])
        elif t == "surface-captured":
            surfaces[r["surface"]] = r["payload"]
        elif t == "surface-discovered":
            discovered.append((r["surface"], r.get("entry")))
        elif t == "surface-retyped":
            retypes.append(r)
        elif t == "boundary":
            boundaries.append(r)
        elif t == "ambiguous" and str(r.get("reason", "")).startswith("not drained:") \
                and "disabled" in str(r.get("reason", "")):
            disabled_state.append({"ref": r["control"], "reason": r["reason"]})

    # Press-time retype reconciliation. A popup item is statically classified from its label
    # (e.g. a trailing "..." => opens-dialog), but pressing it can reveal a different truth — the
    # "Selection Pane..." item opens a docked PANE, not a dialog. When the driver discovers that at
    # press time it emits a `surface-retyped` record; here we (a) supersede the stale
    # (old_ref, entry) discovery with the true (ref, entry) so the phantom leaves the frontier and
    # the real surface gets its entry_point, and (b) rewrite the owning item's action so the emitted
    # ref/kind match what pressing actually did. Generalizes to any static-vs-pressed mismatch.
    for rt in retypes:
        entry = ids.sub_addr(rt["surface"], rt["item"])
        discovered = [(s, e) for (s, e) in discovered
                      if not (s == rt["old_ref"] and e == entry)]
        discovered.append((rt["ref"], entry))
        pl = surfaces.get(rt["surface"])
        if pl:
            for sec in pl.get("sections", []):
                for it in sec.get("items", []):
                    if it.get("id") == rt["item"]:
                        it["action"] = {"kind": rt["kind"], "ref": rt["ref"]}

    # Structural dialog dedup. The SAME physical dialog can be captured under several ids: the Find
    # split's Advanced Find / Replace / Go To items each capture the full 3-tab Find and Replace
    # dialog; 'Line Spacing Options…' captures the Paragraph dialog already captured from its
    # launcher; parent-scoped child-dialog ids (sort-options vs borders-and-shading-options) may
    # capture a genuinely-shared dialog twice. Merge by structural signature (title + per-tab field
    # names + button names): the id matching the dialog's own title wins (else first
    # lexicographically), every ref/discovery is rewritten, duplicates are not emitted.
    def _shot_sig(pl):
        """Byte-hash of every tab screenshot (still a run_dir basename at this point). Two captures
        of the SAME physical dialog render identical pixels; two different 0-field alerts show
        different text => different hashes => never merge."""
        hs = []
        for t in pl.get("tabs", []):
            sn = t.get("screenshot")
            if not sn:
                return None
            try:
                hs.append(hashlib.sha256((run_dir / pathlib.Path(sn).name).read_bytes()).hexdigest())
            except Exception:
                return None
        return tuple(hs) or None

    def _dlg_sig(pl):
        title = (pl.get("title") or "").strip().casefold()
        tabs = tuple((t.get("name", ""),
                      tuple(sorted(f.get("name", "") for sec in t.get("sections", [])
                                   for f in sec.get("fields", []))))
                     for t in pl.get("tabs", []))
        # Field-RICH dialogs identify structurally (title + per-tab field names + buttons) — robust
        # for dynamic dialogs whose screenshots differ across openings (Find and Replace's caret).
        if sum(len(fnames) for _, fnames in tabs) >= 2 and title:
            btns = tuple(sorted(b.get("name", "") for b in pl.get("buttons", [])))
            return ("struct", title, tabs, btns)
        # Field-POOR dialogs (Format Text Effects panel: empty title, 0 fields, only expander
        # buttons) can't be told apart structurally, and static Text is not captured as a field so
        # two DIFFERENT alerts would share a structural sig (review defect C). Fall back to the
        # SCREENSHOT: identical pixels ⇒ same dialog reached from two parents (Text Effects via Font
        # and via More Underlines); different alerts differ visually and stay separate.
        s = _shot_sig(pl)
        return ("visual", s) if s else None

    by_sig, alias = {}, {}
    for sid in sorted(s for s in surfaces if s.startswith("dialogs/")):
        sig = _dlg_sig(surfaces[sid])
        if sig is None:
            continue
        canonical = "dialogs/" + ids.slugify(surfaces[sid].get("title", ""))
        if sig not in by_sig:
            by_sig[sig] = sid
        elif sid == canonical and by_sig[sig] != canonical:
            alias[by_sig[sig]] = sid          # the title-matching id supersedes the earlier keeper
            by_sig[sig] = sid
        else:
            alias[sid] = by_sig[sig]
    for k in list(alias):                     # collapse chains (dup -> old keeper -> title keeper)
        while alias[k] in alias:
            alias[k] = alias[alias[k]]
    if alias:
        for dup in alias:
            surfaces.pop(dup, None)

        def _rewrite_entry(e):
            # entries are sub-addrs whose STEM is a surface id ("dialogs/<parent>#btn:tabs") — a
            # child discovered from a merged-away duplicate must back-link to the KEEPER, or its
            # emitted entry_points point into a surface that no longer exists (review defect A).
            if isinstance(e, str) and "#" in e:
                stem, local = e.split("#", 1)
                if stem in alias:
                    return f"{alias[stem]}#{local}"
            return e

        discovered = [(alias.get(sn, sn), _rewrite_entry(e)) for (sn, e) in discovered]
        for b in boundaries:
            b["from"] = _rewrite_entry(b.get("from"))

        def _rewrite_refs(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k in ("ref", "moreRef") and isinstance(v, str) and v in alias:
                        o[k] = alias[v]
                    else:
                        _rewrite_refs(v)
            elif isinstance(o, list):
                for x in o:
                    _rewrite_refs(x)
        for pl in surfaces.values():
            _rewrite_refs(pl)
        for groups in groups_by_tab.values():
            _rewrite_refs(groups)

    # entry_points = exact inverse of surface-discovered (generated, never hand-maintained)
    entry_points = {}
    for surf, entry in discovered:
        entry_points.setdefault(surf, [])
        if entry and entry not in entry_points[surf]:
            entry_points[surf].append(entry)

    files = {}              # relpath -> doc dict
    total_controls = 0
    for tab, groups in groups_by_tab.items():
        gl = []
        for seg, g in groups.items():
            total_controls += len(g["controls"])
            gl.append({"id": f"ribbon.{tab}.{seg}", "label": g["label"], "controls": g["controls"]})
        files[f"ribbon/{tab}.json"] = {
            "id": f"ribbon/{tab}", "tabLabel": tab.capitalize(), "schema_version": 1,
            "contextual": None, "groups": gl,
            "capture": {"status": "complete", "probe_mode": "pressed-observed", "schema_version": 1}}

    for surf, payload in surfaces.items():
        doc = dict(payload)
        doc["entry_points"] = entry_points.get(surf, [])
        enrich.apply_to_popup(surf, doc, descriptions)   # stamp feature-leaf descriptions (step 4)
        files[surf + ".json"] = doc

    emitted_surfaces = set(surfaces) | {f"ribbon/{t}" for t in groups_by_tab}
    discovered_surfaces = {s for s, _ in discovered}
    # a WINDOW boundary (Insert Pictures chooser) resolves its discovered ref: the surface is
    # deliberately not captured, so it must leave the frontier (else the 'frontier empty' completion
    # gate is unattainable) — coverage.boundaries documents it instead (review defect B).
    boundary_refs = {b["ref"] for b in boundaries if b.get("ref")}
    # a DISABLED opener (Set Numbering Value with no active list; a Text Effects button on a
    # bullet-glyph Font sub-dialog) is un-pressable in this state, so its ref is discovered but can
    # never be captured. It leaves the frontier — recorded under `disabled_state` so the surface is
    # documented as state-gated, not silently dropped, and the 'frontier empty' gate stays honest.
    disabled_refs = {d["ref"] for d in disabled_state} - set(surfaces)
    frontier = sorted(discovered_surfaces - set(surfaces) - boundary_refs - disabled_refs)

    files["coverage.json"] = {
        "schema_version": 1,
        "boundaries": [{k: b.get(k) for k in ("from", "kind", "policy", "decision", "ref")
                        if b.get(k) is not None}
                       for b in boundaries],
        "disabled_state": [d for d in disabled_state if d["ref"] in disabled_refs],
        "frontier": frontier, "blocked": []}

    # reference closure: every surface ref resolves to an emitted, discovered, or boundary surface
    known = emitted_surfaces | discovered_surfaces | boundary_refs
    dangling = sorted({ref for doc in files.values()
                       for ref in _collect_surface_refs(doc) if ref not in known})
    # entry_points closure too: an entry sub-addr's STEM must be a known surface — the dedup once
    # shipped back-links into deleted duplicates precisely because only ref/moreRef were checked.
    for doc in files.values():
        for e in doc.get("entry_points", []):
            if isinstance(e, str) and "#" in e and ids.is_surface_ref(e.split("#", 1)[0]) \
                    and e.split("#", 1)[0] not in known:
                dangling.append(e)
    dangling = sorted(set(dangling))

    # unused boundary config (config entries with no journal boundary record)
    used = {b["from"] for b in boundaries}
    unused = [k for k in config.BOUNDARIES if k not in used]
    unused += [p for p in config.BOUNDARY_PREFIXES if not any(f.startswith(p) for f in used)]

    # asset copy + rewrite (mutates the docs in-place)
    copied, missing = {}, []
    for doc in files.values():
        _process_assets(doc, run_dir, out_root, copied, missing)
    if copied:
        files["icons.json"] = {k: v for k, v in copied.items() if k.startswith("icons/")}
        files["screenshots.json"] = {k: v for k, v in copied.items() if k.startswith("screenshots/")}

    files["manifest.json"] = {
        "schema_version": 1, "build": (stats or {}).get("build", config.BUILD_PREFIX),
        "date": (stats or {}).get("date", time.strftime("%Y-%m-%d")),
        "env": {"resolution": "1920x1080", "dpi": 100, "theme": "light",
                "locale": "en-US", "view": "print"},
        "coverage": {"controls": total_controls, "surfaces_captured": len(surfaces),
                     "boundaries": len(boundaries), "frontier": len(frontier),
                     "unused_boundary_config": unused},
        "throughput": (stats or {}).get("throughput")}

    # validate
    schema_errors = {}
    for rel, doc in files.items():
        if rel.startswith("ribbon/"):
            e = schemas.validate_tab_file(doc)
        elif rel.startswith("dropdowns/"):
            e = schemas.validate_popup(doc)
        elif rel.startswith("dialogs/"):
            e = schemas.validate_dialog(doc)
        else:
            e = []
        if e:
            schema_errors[rel] = e

    # write everything (UTF-8, no BOM, indent=1)
    written = []
    for rel, doc in files.items():
        p = out_root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
        written.append(rel)

    # orphan sweep across managed dirs (keep just-written files + copied assets)
    keep = set(written) | set(copied)
    orphans_deleted = []
    for d in MANAGED_DIRS:
        base = out_root / d
        if not base.exists():
            continue
        for f in base.rglob("*"):
            if f.is_file():
                rel = f.relative_to(out_root).as_posix()
                if rel not in keep:
                    f.unlink()
                    orphans_deleted.append(f)

    return {"written": written, "orphans_deleted": orphans_deleted, "dangling": dangling,
            "entry_points_built": entry_points, "assets_copied": sorted(copied),
            "missing_assets": missing, "schema_errors": schema_errors,
            "unused_boundary_config": unused}

"""Reconciling emitter (DESIGN section 5.5, 4.8). Regenerates the full output set from the
journal, copies referenced PNGs, writes hash manifests + coverage + manifest, validates every
file, checks reference closure, and deletes orphaned files under the managed dirs.

Asset convention (T12 writes PNGs into run_dir with these basenames; emit copies + rewrites):
  icon__<control-id>.png     -> out_root/icons/<base>       (rewritten "icons/<base>")
  screenshot__<...>.png / any other .png -> out_root/screenshots/<base> ("screenshots/<base>")
"""
import json, hashlib, shutil, time, pathlib
import config, ids, schemas

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


def emit(journal, out_root, run_dir, stats=None):
    out_root = pathlib.Path(out_root)
    run_dir = pathlib.Path(run_dir)
    recs = journal.records()

    groups_by_tab = {}      # tab -> {group_seg: {"label": str, "controls": []}}
    surfaces = {}           # surface_id -> payload
    discovered = []         # [(surface, entry)]
    boundaries = []
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
        elif t == "boundary":
            boundaries.append(r)

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
        files[surf + ".json"] = doc

    emitted_surfaces = set(surfaces) | {f"ribbon/{t}" for t in groups_by_tab}
    discovered_surfaces = {s for s, _ in discovered}
    frontier = sorted(discovered_surfaces - set(surfaces))

    files["coverage.json"] = {
        "schema_version": 1,
        "boundaries": [{"from": b["from"], "kind": b.get("kind"),
                        "policy": b.get("policy"), "decision": b.get("decision")}
                       for b in boundaries],
        "frontier": frontier, "blocked": []}

    # reference closure: every surface ref resolves to an emitted or discovered surface
    known = emitted_surfaces | discovered_surfaces
    dangling = sorted({ref for doc in files.values()
                       for ref in _collect_surface_refs(doc) if ref not in known})

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

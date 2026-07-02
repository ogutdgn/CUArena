#!/usr/bin/env python3
"""structure_verify.py — the STRUCTURE parity axis.

Diffs the clone's rendered ribbon (captured live by parity/flow/structure-probe.js) against
the authoritative real-Word inventory (parity/oracle/word_ribbon_inventory.json — Microsoft's
official idMso workbook enriched with GetLabelMso labels from the locked build).

Per mapped tab (parity/oracle/structure_scope.json) each top-level Word control is classified:
  matched        — clone has a control with the same (normalized) label, compatible type
  label-differs  — matched fuzzily but the visible label text differs from Word's
  type-mismatch  — matched by label but the control kind is incompatible (e.g. Word gallery vs clone button)
  missing        — no clone counterpart (THE gap list)
  extra          — clone-only controls with no Word counterpart on that tab

Usage:
  python parity/engines/structure_verify.py                 # verify (uses cached probe capture)
  python parity/engines/structure_verify.py --capture       # re-run the Electron probe first
  python parity/engines/structure_verify.py --report-only   # never exit 1 on gaps (measurement mode)

Outputs parity/results/STRUCTURE_LEDGER.md + structure.json.
Exit: 0 ok / 1 missing-controls found (unless --report-only) / 2 harness failure.
"""
import json
import os
import re
import subprocess
import sys

# Windows consoles default to cp1252 — same guard as review_differ.py.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))          # repo root
PAR = os.path.join(ROOT, "parity")
INVENTORY = os.path.join(PAR, "oracle", "word_ribbon_inventory.json")
SCOPE = os.path.join(PAR, "oracle", "structure_scope.json")
PROBE = os.path.join(PAR, "flow", "structure-probe.js")
ACTUAL = os.path.join(PAR, "flow", "structure-actual.json")
RESULTS = os.path.join(PAR, "results")
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")

# Word control type -> acceptable clone ribbon-data types.
COMPAT = {
    "button": {"button", "split", "toggle", "dropdown"},
    "toggleButton": {"toggle", "button", "split"},
    "checkBox": {"checkbox", "toggle"},
    "menu": {"dropdown", "split"},
    "gallery": {"dropdown", "gallery", "split", "combo"},
    "splitButton": {"split", "dropdown", "button"},
    "dropDown": {"dropdown", "combo"},
    "comboBox": {"combo", "dropdown"},
    "control": {"combo", "spinner", "dropdown"},
    "button (dialogBoxLauncher)": {"launcher", "button"},
}
# Workbook rows that are structure, not controls.
NON_CONTROL_TYPES = {"tab", "group", "tabSet", "contextMenu", "labelControl", "task",
                     "category", "taskFormGroup", None}


def norm(s):
    s = (s or "").lower().replace("&", " ").replace("‑", "-")
    s = re.sub(r"[.…:]+\s*$", "", s.strip())
    return re.sub(r"\s+", " ", s)


def tokens(s):
    return set(norm(s).split())


def load_word_side(inv, tab_map, excluded):
    """{clone_tab: [ {idMso, label, type, group} ]} — top-level controls per mapped Word tab."""
    out = {ct: [] for ct in tab_map.values()}
    seen = set()
    for c in inv["controls"]:
        tab = c.get("tab")
        if tab not in tab_map or c.get("parent") or c["type"] in NON_CONTROL_TYPES:
            continue
        if c["idMso"] in excluded:
            continue
        # *MenuAnchor ids are the ribbon-collapse menu variants of a whole group (the same
        # controls re-parented under one anchor when the window narrows) — not real features.
        if c["idMso"].endswith("MenuAnchor"):
            continue
        key = (tab, c["idMso"])
        if key in seen:
            continue
        seen.add(key)
        out[tab_map[tab]].append({
            "idMso": c["idMso"],
            "label": c.get("label") or "",
            "type": c["type"],
            "group": c.get("group"),
        })
    return out


def load_clone_side(actual, wanted_tabs):
    """{clone_tab: [ {cmd, label, type, items} ]} from the live probe capture (launchers included)."""
    out = {}
    for t in (actual.get("mainTabs") or []) + (actual.get("contextualTabs") or []):
        if t["id"] not in wanted_tabs:
            continue
        ctrls = []
        for g in t.get("groups") or []:
            for c in g.get("controls") or []:
                ctrls.append({"cmd": c.get("cmd"), "label": c.get("label") or "",
                              "type": c.get("type") or "button", "items": c.get("items")})
            if g.get("launcher"):
                ln = g["launcher"]
                ctrls.append({"cmd": ln.get("cmd"), "label": ln.get("label") or "", "type": "launcher", "items": None})
        out[t["id"]] = ctrls
    return out


# Word control types whose CHILDREN we compare against the clone's declared items[] (D2.1).
MENUISH_TYPES = {"menu", "splitButton", "gallery"}

# Clone items[] entries that are gallery SECTION HEADERS / picker chrome, not clickable
# commands — the workbook never lists these as controls, so they'd read as fake "extra".
# (Same class as flow_verify's CATEGORY_ITEMS.)
CATEGORY_HEADERS = {
    "underline styles", "color swatches", "theme colors", "standard colors", "recent colors",
    "bullet library", "numbering library", "document bullets", "list library", "current list",
    "recently used bullets", "recently used numbers", "recently used number formats",
    "gradient", "more gradients",
}


def load_word_children(inv, tab_map, excluded):
    """{(clone_tab, parent_idMso): [ {idMso,label,type} ]} — every inventory row nested under a
    parent control on a mapped tab. Direct + secondary nesting are FLATTENED (presence check);
    children under *MenuAnchor collapse-variants are skipped like their parents."""
    out = {}
    seen = set()
    for c in inv["controls"]:
        tab, parent = c.get("tab"), c.get("parent")
        if not parent or tab not in tab_map or c["type"] in NON_CONTROL_TYPES:
            continue
        if c["idMso"] in excluded or parent.endswith("MenuAnchor"):
            continue
        key = (tab, parent, c["idMso"])
        if key in seen:
            continue
        seen.add(key)
        out.setdefault((tab_map[tab], parent), []).append({
            "idMso": c["idMso"], "label": c.get("label") or "", "type": c["type"],
        })
    return out


def expected_children(childmap, top_ids, tab, parent):
    """Expected EXPANDED-menu content for a menu-ish control. The workbook flattens ALL
    placements under a parent, including the collapsed-ribbon state where whole-group members
    (Cut/Copy under PasteMenu) fold into the primary split — so: drop children that also sit
    TOP-LEVEL on the same tab (collapse duplicates); drop a child named like the parent (the
    split's own primary action / self-named gallery) but DESCEND into it, inlining its children
    (the paste-options gallery IS the menu's content)."""
    out = []
    for c in childmap.get((tab, parent["idMso"]), []):
        if c["idMso"] in top_ids:
            continue
        if norm(c["label"]) and norm(c["label"]) == norm(parent["label"]):
            out.extend(x for x in childmap.get((tab, c["idMso"]), []) if x["idMso"] not in top_ids)
            continue
        out.append(c)
    return out


def match_items(word_children, clone_items):
    """Diff a menu's Word children (labeled controls) vs the clone's declared item strings."""
    res = {"matched": 0, "missing": [], "extra": [], "skipped_unlabeled": 0}
    citems = [(i, s) for i, s in enumerate(clone_items or [])
              if norm(s) and norm(s) not in CATEGORY_HEADERS]
    avail = [i for i, _ in citems]
    bylabel = {i: s for i, s in citems}

    def take(ci):
        avail.remove(ci)

    for w in word_children:
        wn, wt = norm(w["label"]), tokens(w["label"])
        if not wn:
            res["skipped_unlabeled"] += 1
            continue
        hit = next((ci for ci in avail if norm(bylabel[ci]) == wn), None)
        if hit is None and len(wn) >= 4:
            def fuzz(ci):
                cn, ct = norm(bylabel[ci]), tokens(bylabel[ci])
                return len(cn) >= 4 and (wt <= ct or ct <= wt or wn in cn or cn in wn)
            hit = next((ci for ci in avail if fuzz(ci)), None)
        if hit is not None:
            take(hit)
            res["matched"] += 1
        else:
            res["missing"].append({"idMso": w["idMso"], "label": w["label"], "type": w["type"]})
    res["extra"] = [bylabel[ci] for ci in avail]
    return res


def match_tab(word, clone, pinned):
    """1:1 match Word controls to clone controls: pinned (human-triaged) first, then exact
    normalized label, then token-subset / substring containment."""
    res = {"matched": [], "label_differs": [], "type_mismatch": [], "missing": [], "extra": []}
    # Stable-sort so type 'menu' matches LAST: when Word has both a concrete control and its
    # ribbon-collapse menu variant under the same label (Paste splitButton vs PasteMenu), the
    # concrete one must claim the clone control first.
    word = sorted(word, key=lambda w: w["type"] == "menu")
    cavail = list(range(len(clone)))

    def take(ci):
        cavail.remove(ci)
        return clone[ci]

    def bucket_of(w, c, fuzzy):
        if c["type"] not in COMPAT.get(w["type"], set()):
            return "type_mismatch"
        return "label_differs" if (fuzzy and norm(c["label"]) != norm(w["label"])) else "matched"

    # pass 0: pinned matches (clone cmd -> idMso), from structure_scope.json triage
    unmatched_word = []
    for w in word:
        hit = next((ci for ci in cavail
                    if clone[ci].get("cmd") and pinned.get(clone[ci]["cmd"]) == w["idMso"]), None)
        if hit is not None:
            c = take(hit)
            res[bucket_of(w, c, fuzzy=True)].append({"word": w, "clone": c, "pinned": True})
        else:
            unmatched_word.append(w)
    # pass 1: exact normalized label
    word, unmatched_word = unmatched_word, []
    for w in word:
        wn = norm(w["label"])
        hit = next((ci for ci in cavail if wn and norm(clone[ci]["label"]) == wn), None)
        if hit is not None:
            c = take(hit)
            res[bucket_of(w, c, fuzzy=False)].append({"word": w, "clone": c})
        else:
            unmatched_word.append(w)
    # pass 2: token-subset either way, or substring containment (>=4 chars)
    still = []
    for w in unmatched_word:
        wn, wt = norm(w["label"]), tokens(w["label"])
        hit = None
        if len(wn) >= 4:
            def fuzz(ci):
                cn, ct = norm(clone[ci]["label"]), tokens(clone[ci]["label"])
                if len(cn) < 4 or not ct:
                    return False
                return wt <= ct or ct <= wt or wn in cn or cn in wn
            hit = next((ci for ci in cavail if fuzz(ci)), None)
        if hit is not None:
            c = take(hit)
            res[bucket_of(w, c, fuzzy=True)].append({"word": w, "clone": c})
        else:
            still.append(w)
    res["missing"] = still
    res["extra"] = [clone[ci] for ci in cavail]
    return res


def capture():
    cmd = [ELECTRON, "--user-data-dir=C:/tmp/wc-structure-profile", "--disable-http-cache", ".",
           f"--probe-out={ACTUAL}", f"--shot-evalfile={PROBE}"]
    subprocess.run(cmd, cwd=ROOT, timeout=180, capture_output=True)


def write_ledger(per_tab, meta):
    os.makedirs(RESULTS, exist_ok=True)
    tot = {k: sum(len(v[k]) for v in per_tab.values())
           for k in ("matched", "label_differs", "type_mismatch", "missing", "extra")}
    tot["items_matched"] = sum(m["matched"] for v in per_tab.values() for m in v.get("menus", []))
    tot["items_missing"] = sum(len(m["missing"]) for v in per_tab.values() for m in v.get("menus", []))
    tot["items_extra"] = sum(len(m["extra"]) for v in per_tab.values() for m in v.get("menus", []))
    tot["items_skipped"] = sum(m["skipped_unlabeled"] for v in per_tab.values() for m in v.get("menus", []))
    md = ["# Structure Ledger — clone ribbon vs. real Word (official idMso inventory)\n",
          "Auto-generated by `parity/engines/structure_verify.py`. Word side = Microsoft's",
          "control-identifier workbook (M365 Current Channel) + GetLabelMso labels from the locked",
          "build. Clone side = the LIVE rendered ribbon (structure-probe.js), contextual tabs included.\n",
          f"**Totals:** matched {tot['matched']} · label-differs {tot['label_differs']} · "
          f"type-mismatch {tot['type_mismatch']} · **missing {tot['missing']}** · extra {tot['extra']}\n",
          f"**Menu items (D2.1):** matched {tot['items_matched']} · **missing {tot['items_missing']}** · "
          f"extra {tot['items_extra']} · unlabeled-skipped {tot['items_skipped']}\n",
          "| Tab | matched | label≠ | type≠ | missing | extra | item-miss |",
          "|---|---|---|---|---|---|---|"]
    for tab, r in per_tab.items():
        imiss = sum(len(m["missing"]) for m in r.get("menus", []))
        md.append(f"| {tab} | {len(r['matched'])} | {len(r['label_differs'])} | "
                  f"{len(r['type_mismatch'])} | **{len(r['missing'])}** | {len(r['extra'])} | **{imiss}** |")
    for tab, r in per_tab.items():
        if not (r["missing"] or r["extra"] or r["label_differs"] or r["type_mismatch"]):
            continue
        md.append(f"\n## {tab}\n")
        if r["missing"]:
            md.append("**Missing in clone** (Word has these; the clone tab does not):\n")
            for w in r["missing"]:
                md.append(f"- `{w['idMso']}` — **{w['label'] or '(no label)'}** ({w['type']}, {w['group'] or '?'})")
        if r["type_mismatch"]:
            md.append("\n**Type mismatch** (present but the wrong kind of control):\n")
            for p in r["type_mismatch"]:
                md.append(f"- `{p['word']['idMso']}` {p['word']['label']}: Word {p['word']['type']} "
                          f"vs clone `{p['clone']['cmd']}` {p['clone']['type']}")
        if r["label_differs"]:
            md.append("\n**Label differs** (matched, but the visible text ≠ Word's):\n")
            for p in r["label_differs"]:
                md.append(f"- `{p['word']['idMso']}`: Word \"{p['word']['label']}\" vs clone "
                          f"\"{p['clone']['label']}\" (`{p['clone']['cmd']}`)")
        if r["extra"]:
            md.append("\n**Extra in clone** (no top-level Word counterpart on this tab — may be "
                      "misplaced, renamed beyond fuzz, or genuinely clone-only):\n")
            for c in r["extra"]:
                md.append(f"- `{c['cmd']}` \"{c['label']}\" ({c['type']})")
        gaps = [m for m in r.get("menus", []) if m["missing"] or m["extra"]]
        if gaps:
            md.append("\n**Menu items (Word children vs clone declared items):**\n")
            for m in gaps:
                md.append(f"- `{m['parent']}` \"{m['wordLabel']}\" (clone `{m['cloneCmd']}`): "
                          f"{m['matched']}/{m['wordChildCount']} matched"
                          + (f", skipped-unlabeled {m['skipped_unlabeled']}" if m["skipped_unlabeled"] else ""))
                for w in m["missing"]:
                    md.append(f"  - MISSING item: `{w['idMso']}` — {w['label']} ({w['type']})")
                for s in m["extra"]:
                    md.append(f"  - extra clone item: \"{s}\"")
    if meta.get("unmapped_todo"):
        md.append("\n## Not yet mapped (TODO tab sets)\n")
        for ts in meta["unmapped_todo"]:
            md.append(f"- {ts}")
    with open(os.path.join(RESULTS, "STRUCTURE_LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(RESULTS, "structure.json"), "w", encoding="utf-8") as f:
        json.dump({"totals": tot, "per_tab": per_tab, "meta": meta}, f, indent=1)
    return tot


def main():
    args = sys.argv[1:]
    if "--capture" in args or not os.path.exists(ACTUAL):
        capture()
    try:
        inv = json.load(open(INVENTORY, encoding="utf-8"))
        scope = json.load(open(SCOPE, encoding="utf-8"))
        actual = json.load(open(ACTUAL, encoding="utf-8"))
    except Exception as e:
        print(f"structure_verify: harness failure: {e}")
        return 2
    if not actual.get("ready"):
        print("structure_verify: probe reported app not ready")
        return 2

    excluded = set(scope.get("excluded_idmso", {}))
    word_side = load_word_side(inv, scope["tab_map"], excluded)
    word_children = load_word_children(inv, scope["tab_map"], excluded)
    clone_side = load_clone_side(actual, set(scope["tab_map"].values()))
    pinned = scope.get("pinned_matches", {})
    per_tab = {}
    for tab in scope["tab_map"].values():
        if tab in per_tab:
            continue
        per_tab[tab] = match_tab(word_side.get(tab, []), clone_side.get(tab, []), pinned)
        if tab not in clone_side:
            per_tab[tab]["note"] = "clone tab NOT CAPTURED by the probe"
        # D2.1 — menu-item level: diff Word children vs the clone's declared items[] for
        # every present pair whose Word control is menu-ish.
        menus = []
        top_ids = {w["idMso"] for w in word_side.get(tab, [])}
        for p in per_tab[tab]["matched"] + per_tab[tab]["label_differs"] + per_tab[tab]["type_mismatch"]:
            w = p["word"]
            if w["type"] not in MENUISH_TYPES:
                continue
            kids = expected_children(word_children, top_ids, tab, w)
            if not kids:
                continue
            m = match_items(kids, p["clone"].get("items"))
            m["parent"] = w["idMso"]
            m["wordLabel"] = w["label"]
            m["cloneCmd"] = p["clone"].get("cmd")
            m["wordChildCount"] = len(kids)
            menus.append(m)
        per_tab[tab]["menus"] = menus
    tot = write_ledger(per_tab, {"unmapped_todo": scope.get("unmapped_word_tabsets_todo", []),
                                 "probe_errors": actual.get("errors", [])})
    print(f"STRUCTURE: matched {tot['matched']} / label≠ {tot['label_differs']} / type≠ "
          f"{tot['type_mismatch']} / MISSING {tot['missing']} / extra {tot['extra']}")
    print(f"MENU ITEMS: matched {tot['items_matched']} / MISSING {tot['items_missing']} / "
          f"extra {tot['items_extra']} / unlabeled-skipped {tot['items_skipped']}")
    print(f"ledger: parity/results/STRUCTURE_LEDGER.md")
    if (tot["missing"] or tot["items_missing"]) and "--report-only" not in args:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

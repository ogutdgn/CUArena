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
    """{clone_tab: [ {cmd, label, type} ]} from the live probe capture (launchers included)."""
    out = {}
    for t in (actual.get("mainTabs") or []) + (actual.get("contextualTabs") or []):
        if t["id"] not in wanted_tabs:
            continue
        ctrls = []
        for g in t.get("groups") or []:
            for c in g.get("controls") or []:
                ctrls.append({"cmd": c.get("cmd"), "label": c.get("label") or "", "type": c.get("type") or "button"})
            if g.get("launcher"):
                ln = g["launcher"]
                ctrls.append({"cmd": ln.get("cmd"), "label": ln.get("label") or "", "type": "launcher"})
        out[t["id"]] = ctrls
    return out


def match_tab(word, clone, pinned):
    """1:1 match Word controls to clone controls: pinned (human-triaged) first, then exact
    normalized label, then token-subset / substring containment."""
    res = {"matched": [], "label_differs": [], "type_mismatch": [], "missing": [], "extra": []}
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
    md = ["# Structure Ledger — clone ribbon vs. real Word (official idMso inventory)\n",
          "Auto-generated by `parity/engines/structure_verify.py`. Word side = Microsoft's",
          "control-identifier workbook (M365 Current Channel) + GetLabelMso labels from the locked",
          "build. Clone side = the LIVE rendered ribbon (structure-probe.js), contextual tabs included.\n",
          f"**Totals:** matched {tot['matched']} · label-differs {tot['label_differs']} · "
          f"type-mismatch {tot['type_mismatch']} · **missing {tot['missing']}** · extra {tot['extra']}\n",
          "| Tab | matched | label≠ | type≠ | missing | extra |",
          "|---|---|---|---|---|---|"]
    for tab, r in per_tab.items():
        md.append(f"| {tab} | {len(r['matched'])} | {len(r['label_differs'])} | "
                  f"{len(r['type_mismatch'])} | **{len(r['missing'])}** | {len(r['extra'])} |")
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

    word_side = load_word_side(inv, scope["tab_map"], set(scope.get("excluded_idmso", {})))
    clone_side = load_clone_side(actual, set(scope["tab_map"].values()))
    pinned = scope.get("pinned_matches", {})
    per_tab = {}
    for tab in scope["tab_map"].values():
        if tab in per_tab:
            continue
        per_tab[tab] = match_tab(word_side.get(tab, []), clone_side.get(tab, []), pinned)
        if tab not in clone_side:
            per_tab[tab]["note"] = "clone tab NOT CAPTURED by the probe"
    tot = write_ledger(per_tab, {"unmapped_todo": scope.get("unmapped_word_tabsets_todo", []),
                                 "probe_errors": actual.get("errors", [])})
    print(f"STRUCTURE: matched {tot['matched']} / label≠ {tot['label_differs']} / type≠ "
          f"{tot['type_mismatch']} / MISSING {tot['missing']} / extra {tot['extra']}")
    print(f"ledger: parity/results/STRUCTURE_LEDGER.md")
    if tot["missing"] and "--report-only" not in args:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

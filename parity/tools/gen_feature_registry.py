#!/usr/bin/env python3
"""gen_feature_registry.py — build the 111-locked-feature registry that keys the multi-axis
feature ledger (rubric: verdicts reported per locked feature, 111 rows).

Sources:
  docs/SCOPE_LOCKED.md                 — the locked feature list (name, tier, per-tab sections)
  parity/flow/structure-actual.json    — the clone's rendered controls (label -> cmd, per tab)
  parity/results/structure.json        — the structure pairs (cmd -> idMso)
  parity/tasks.json                    — OOXML tasks (task.feature -> feature name)
  parity/oracle/feature_registry_pins.json (optional) — human-triaged {feature: [cmds]} pins

Output: parity/oracle/feature_registry.json
  {features: [{name, tab, tier, cmds[], idMso[], ooxmlTasks[]}], unmatched: [names]}
Auto-matching is label-based (exact -> token-subset); unmatched features are LISTED, never
guessed — pin them in feature_registry_pins.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAR = os.path.join(ROOT, "parity")
SCOPE_MD = os.path.join(ROOT, "docs", "SCOPE_LOCKED.md")
ACTUAL = os.path.join(PAR, "flow", "structure-actual.json")
STRUCTURE = os.path.join(PAR, "results", "structure.json")
TASKS = os.path.join(PAR, "tasks.json")
PINS = os.path.join(PAR, "oracle", "feature_registry_pins.json")
OUT = os.path.join(PAR, "oracle", "feature_registry.json")

TAB_IDS = {"Home": "home", "Insert": "insert", "Design": "design", "Layout": "layout",
           "References": "references", "Mailings": "mailings", "Review": "review", "View": "view"}


def norm(s):
    s = (s or "").lower().replace("&", " ").replace("¶", "")
    s = re.sub(r"\(.*?\)", " ", s)           # "Font (face)" -> "font"
    s = re.sub(r"[.…:]+\s*$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def tokens(s):
    return set(norm(s).split())


def parse_scope():
    feats = []
    tab = None
    for line in open(SCOPE_MD, encoding="utf-8").read().splitlines():
        m = re.match(r"^### (\w+)", line)
        if m:
            tab = m.group(1)
            continue
        if line.startswith("## Deferred"):
            break
        m = re.match(r"^\| \*\*(.+?)\*\* \| (T\d) \|", line)
        if m and tab in TAB_IDS:
            feats.append({"name": m.group(1), "tab": TAB_IDS[tab], "tier": m.group(2)})
    return feats


def main():
    feats = parse_scope()
    actual = json.load(open(ACTUAL, encoding="utf-8"))
    structure = json.load(open(STRUCTURE, encoding="utf-8"))
    tasks = json.load(open(TASKS, encoding="utf-8"))
    tasks = tasks["tasks"] if isinstance(tasks, dict) and "tasks" in tasks else tasks
    pins = json.load(open(PINS, encoding="utf-8")) if os.path.exists(PINS) else {}

    # clone controls per tab: label -> cmd
    controls = {}
    for t in (actual.get("mainTabs") or []) + (actual.get("contextualTabs") or []):
        for g in t.get("groups") or []:
            for c in (g.get("controls") or []) + ([g["launcher"]] if g.get("launcher") else []):
                if c and c.get("cmd"):
                    controls.setdefault(t["id"], []).append({"label": c.get("label") or "", "cmd": c["cmd"]})
    # cmd -> idMso from the structure pairs
    cmd2mso = {}
    for r in structure["per_tab"].values():
        for bucket in ("matched", "label_differs", "type_mismatch"):
            for p in r.get(bucket, []):
                if p["clone"].get("cmd"):
                    cmd2mso.setdefault(p["clone"]["cmd"], p["word"]["idMso"])
    # task -> feature linking: exact > prefix ("Font dialog: All caps" -> "Font dialog (…)")
    # > token-subset (longest feature wins, so "Font Color" beats "Font" for color variants);
    # tab-restricted when the task declares one.
    def link_task(t, feats):
        tf, tt = norm(t.get("feature", "")), tokens(t.get("feature", ""))
        ttab = TAB_IDS.get(t.get("tab", ""), None)
        best, score = None, 0
        for f in feats:
            if ttab and f["tab"] != ttab:
                continue
            fn, ft = norm(f["name"]), tokens(f["name"])
            if not fn:
                continue
            s = 0
            if tf == fn:
                s = 1000
            elif tf.startswith(fn + ":") or tf.startswith(fn + " "):
                s = 500 + len(ft)
            elif ft and ft <= tt:
                s = 100 + len(ft)
            if s > score:
                best, score = f, s
        return best

    feat2tasks = {}
    for t in tasks:
        f = link_task(t, feats)
        if f:
            feat2tasks.setdefault(f["name"], []).append(t["id"])

    out, unmatched = [], []
    for f in feats:
        cmds = list(pins.get(f["name"], []))
        if not cmds:
            fn, ft = norm(f["name"]), tokens(f["name"])
            cands = controls.get(f["tab"], [])
            hit = next((c for c in cands if norm(c["label"]) == fn), None)
            if hit is None and len(fn) >= 3:
                hit = next((c for c in cands if tokens(c["label"]) and
                            (ft <= tokens(c["label"]) or tokens(c["label"]) <= ft)), None)
            if hit:
                cmds = [hit["cmd"]]
        if not cmds:
            unmatched.append(f["name"])
        out.append({**f, "cmds": cmds,
                    "idMso": sorted({cmd2mso[c] for c in cmds if c in cmd2mso}),
                    "ooxmlTasks": feat2tasks.get(f["name"], [])})

    json.dump({"features": out, "unmatched": unmatched},
              open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"wrote {len(out)} features -> {os.path.relpath(OUT, ROOT)}")
    print(f"auto-matched cmds: {sum(1 for f in out if f['cmds'])} / unmatched: {len(unmatched)}")
    if unmatched:
        print("UNMATCHED (pin in feature_registry_pins.json):")
        for n in unmatched:
            print(f"  - {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

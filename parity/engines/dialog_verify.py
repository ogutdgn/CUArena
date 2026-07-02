#!/usr/bin/env python3
"""dialog_verify.py — the dialog-field parity check (rubric D2.2).

Diffs each Word dialog's UIA field/tab dump (parity/oracle/dialogs/<key>.json, from
dump_dialog_uia.ps1) against the clone's rendered dialog fields (dialog-fields-probe.js).
Per dialog: fields matched / missing (Word has, clone lacks) / extra; tabs matched / missing.

SCOPE (rubric D2.2): only dialogs of the 111 locked features. Word dumps are captured one at a
time (Word closed each run) and cached under parity/oracle/dialogs/.

Usage:
  python parity/engines/dialog_verify.py --capture-clone   # re-run the clone probe
  python parity/engines/dialog_verify.py --report-only
Outputs parity/results/DIALOG_LEDGER.md + dialog.json.
"""
import glob
import json
import os
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAR = os.path.join(ROOT, "parity")
WORD_DIR = os.path.join(PAR, "oracle", "dialogs")
PROBE = os.path.join(PAR, "flow", "dialog-fields-probe.js")
ACTUAL = os.path.join(PAR, "flow", "dialog-fields-actual.json")
RESULTS = os.path.join(PAR, "results")
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")

# Word UIA control names that are dialog chrome, not feature fields.
CHROME = {"ok", "cancel", "close", "help", "apply", "minimize", "maximize", "system",
          "default", "set as default", "text effects", "", "word"}


def norm(s):
    s = (s or "").lower().replace("&", " ")
    s = re.sub(r"[.…:]+\s*$", "", s.strip())
    return re.sub(r"\s+", " ", s).strip()


def tokens(s):
    return set(norm(s).split())


def diff_fields(word_fields, clone_fields):
    wf = [f for f in word_fields if norm(f["name"]) and norm(f["name"]) not in CHROME]
    cf = [f for f in clone_fields if norm(f["name"]) and norm(f["name"]) not in CHROME]
    cav = list(range(len(cf)))
    matched, missing = [], []

    def hit(wn, wt):
        for ci in cav:
            cn, ct = norm(cf[ci]["name"]), tokens(cf[ci]["name"])
            if cn == wn or (len(wn) >= 4 and (wn in cn or cn in wn or (wt and (wt <= ct or ct <= wt)))):
                return ci
        return None

    for w in wf:
        wn, wt = norm(w["name"]), tokens(w["name"])
        h = hit(wn, wt)
        if h is not None:
            cav.remove(h)
            matched.append(w["name"])
        else:
            missing.append(w)
    extra = [cf[ci]["name"] for ci in cav]
    return matched, missing, extra


def main():
    args = sys.argv[1:]
    if "--capture-clone" in args or not os.path.exists(ACTUAL):
        subprocess.run([ELECTRON, "--user-data-dir=C:/tmp/wc-dialog-profile", "--disable-http-cache",
                        ".", f"--probe-out={ACTUAL}", f"--shot-evalfile={PROBE}"],
                       cwd=ROOT, timeout=240, capture_output=True)
    try:
        clone = json.load(open(ACTUAL, encoding="utf-8"))
    except Exception as e:
        print(f"dialog_verify: harness failure: {e}")
        return 2
    if not clone.get("ready"):
        print("dialog_verify: clone probe not ready")
        return 2

    word = {}
    for p in glob.glob(os.path.join(WORD_DIR, "*.json")):
        d = json.load(open(p, encoding="utf-8-sig"))
        word[d.get("key") or os.path.splitext(os.path.basename(p))[0]] = d

    rows = []
    for key, cd in clone.get("dialogs", {}).items():
        wd = word.get(key)
        row = {"key": key, "cloneFound": cd.get("found"), "wordFound": bool(wd)}
        if not wd:
            row["status"] = "no-word-dump"
        elif not cd.get("found"):
            row["status"] = "clone-dialog-missing"
            row["wordFields"] = len(wd.get("fields", []))
        else:
            m, miss, extra = diff_fields(wd.get("fields", []), cd.get("fields", []))
            tw = {norm(t) for t in wd.get("tabs", [])}
            tc = {norm(t) for t in cd.get("tabs", [])}
            row.update({"status": "compared", "matched": len(m), "missing": miss, "extra": extra,
                        "tabsMissing": sorted(tw - tc), "tabsMatched": sorted(tw & tc)})
        rows.append(row)

    os.makedirs(RESULTS, exist_ok=True)
    total_missing = sum(len(r.get("missing", [])) for r in rows)
    md = ["# Dialog Ledger — clone dialog fields vs Word UIA dump (D2.2)\n",
          "Word side = UIA field/tab dump (dump_dialog_uia.ps1); clone side = rendered dialog DOM",
          "(dialog-fields-probe.js). Scope = locked-feature dialogs.\n",
          f"**Dialogs compared: {sum(1 for r in rows if r['status']=='compared')}** · "
          f"**fields missing in clone: {total_missing}**\n",
          "| Dialog | Status | fields matched | missing | extra | tabs missing |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        if r["status"] == "compared":
            md.append(f"| {r['key']} | compared | {r['matched']} | **{len(r['missing'])}** | "
                      f"{len(r['extra'])} | {', '.join(r['tabsMissing']) or '—'} |")
        else:
            md.append(f"| {r['key']} | {r['status']} | — | — | — | — |")
    for r in rows:
        if r.get("missing"):
            md.append(f"\n## {r['key']} — missing fields (Word has, clone lacks)\n")
            for w in r["missing"]:
                md.append(f"- {w['name']} ({w['type']})")
    with open(os.path.join(RESULTS, "DIALOG_LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    with open(os.path.join(RESULTS, "dialog.json"), "w", encoding="utf-8") as f:
        json.dump({"rows": rows}, f, indent=1)

    comp = sum(1 for r in rows if r["status"] == "compared")
    print(f"DIALOG: compared {comp} dialogs / fields missing {total_missing} / "
          f"no-word-dump {sum(1 for r in rows if r['status']=='no-word-dump')}")
    print("ledger: parity/results/DIALOG_LEDGER.md")
    if total_missing and "--report-only" not in args:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

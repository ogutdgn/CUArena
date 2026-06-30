#!/usr/bin/env python3
"""Parity task runner — orchestrates clone capture + real-Word capture + diff + ledger.

Conventions (per task id):
  clone probe   : parity/probes/<id>-pilot-probe.js   -> writes parity/fixtures/wc-<id>.docx
  real-Word COM : parity/ground-truth/realword_<id>.ps1 -> writes parity/fixtures/rw-<id>.docx
  diff          : engines/ooxml_diff.py(rw, wc)

Usage (run from clone repo root):
  python parity/engines/run.py                # diff existing fixtures -> LEDGER  (no capture)
  python parity/engines/run.py --only bold
  python parity/engines/run.py --capture      # also (re)capture both sides first  (needs Electron + Word closed)
"""
import os, sys, json, argparse, subprocess

ENGINES = os.path.dirname(os.path.abspath(__file__))
PARITY = os.path.dirname(ENGINES)
ROOT = os.path.dirname(PARITY)
sys.path.insert(0, ENGINES)
import ooxml_diff
import ledger

FIX = os.path.join(PARITY, "fixtures")
RESULTS = os.path.join(PARITY, "results")
PROBES = os.path.join(PARITY, "probes")
GT = os.path.join(PARITY, "ground-truth")
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")


def capture_clone(tid):
    probe = os.path.join(PROBES, f"{tid}-pilot-probe.js")
    cmd = [ELECTRON, "--user-data-dir=C:/tmp/wc-probe-profile", "--disable-http-cache", ".",
           f"--probe-out={os.path.join(RESULTS, tid + '-probe.json')}", f"--shot-evalfile={probe}"]
    subprocess.run(cmd, cwd=ROOT, timeout=180, capture_output=True)


def capture_realword(tid, method):
    if method != "com":
        print(f"  [!] {tid}: realword_method='{method}' -> needs manual vsto UI capture; skipping auto-capture.")
        return
    ps1 = os.path.join(GT, f"realword_{tid}.ps1")
    out = os.path.join(FIX, f"rw-{tid}.docx")
    subprocess.run(["powershell", "-NonInteractive", "-File", ps1, "-Out", out], timeout=120, capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default=os.path.join(PARITY, "tasks.json"))
    ap.add_argument("--only", default=None, help="run a single task id")
    ap.add_argument("--capture", action="store_true", help="(re)capture both sides before diffing")
    a = ap.parse_args()

    tasks = json.load(open(a.tasks, encoding="utf-8"))["tasks"]
    if a.only:
        tasks = [t for t in tasks if t["id"] == a.only]
    os.makedirs(RESULTS, exist_ok=True)

    results = []
    for t in tasks:
        tid = t["id"]
        print(f"== task: {tid} ({t.get('feature')}) ==")
        if a.capture:
            print("  capturing clone..."); capture_clone(tid)
            print("  capturing real Word..."); capture_realword(tid, t.get("realword_method", "com"))
        rw = os.path.join(FIX, f"rw-{tid}.docx")
        wc = os.path.join(FIX, f"wc-{tid}.docx")
        if not (os.path.exists(rw) and os.path.exists(wc)):
            print(f"  [!] missing fixtures (rw={os.path.exists(rw)}, wc={os.path.exists(wc)}) — run with --capture")
            continue
        d = ooxml_diff.diff(rw, wc, tid)
        d["id"] = tid
        d.update({k: t.get(k) for k in ("control_id", "feature", "tab", "usage_tier", "note")})
        json.dump(d, open(os.path.join(RESULTS, f"{tid}.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        results.append(d)
        print(f"  -> {d['verdict']}  match={d['counts']['match']} missing={d['counts']['missing']} extra={d['counts']['extra']}")

    path = ledger.write_ledger(results, RESULTS)
    seeds = ledger.write_spec_seeds(results, RESULTS)
    print(f"\nLedger written: {path}  ({len(results)} tasks)")
    print(f"Spec seeds written: {seeds}  (-> /speckit-specify input)")


if __name__ == "__main__":
    main()

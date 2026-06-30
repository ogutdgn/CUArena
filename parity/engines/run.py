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

try:  # the Windows console defaults to cp1252 and crashes on non-ASCII print()
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

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

# v2 baseline subtraction: each side's empty-doc baseline, subtracted from every task
# so blank-document boilerplate cancels and only the feature delta remains.
BASELINE_ID = "blank"
RW_BASELINE = os.path.join(FIX, f"rw-{BASELINE_ID}.docx")
WC_BASELINE = os.path.join(FIX, f"wc-{BASELINE_ID}.docx")


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


def capture_baseline():
    """Capture the empty-doc baseline for both sides (clone probe + real-Word COM)."""
    print("== baseline: capturing empty-doc baselines (clone + real Word) ==")
    capture_clone(BASELINE_ID)
    capture_realword(BASELINE_ID, "com")
    print(f"  -> wc-baseline={os.path.exists(WC_BASELINE)}  rw-baseline={os.path.exists(RW_BASELINE)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default=os.path.join(PARITY, "tasks.json"))
    ap.add_argument("--only", default=None, help="run a single task id")
    ap.add_argument("--capture", action="store_true", help="(re)capture both sides before diffing")
    ap.add_argument("--capture-baseline", action="store_true", help="(re)capture ONLY the empty-doc baselines")
    ap.add_argument("--no-baseline", action="store_true", help="diff full docs without baseline subtraction (v1 behavior)")
    a = ap.parse_args()

    tasks = json.load(open(a.tasks, encoding="utf-8"))["tasks"]
    if a.only:
        tasks = [t for t in tasks if t["id"] == a.only]
    os.makedirs(RESULTS, exist_ok=True)

    # v2 baseline subtraction: capture the empty-doc baselines once, then subtract them.
    if a.capture or a.capture_baseline:
        capture_baseline()
    if a.capture_baseline and not a.capture:
        return
    use_baseline = not a.no_baseline and os.path.exists(RW_BASELINE) and os.path.exists(WC_BASELINE)
    if a.no_baseline:
        print("  [i] --no-baseline: diffing full docs (v1).")
    elif not use_baseline:
        print(f"  [!] no baseline fixtures (rw={os.path.exists(RW_BASELINE)}, wc={os.path.exists(WC_BASELINE)}) "
              "— diffing full docs; run with --capture-baseline for clean deltas.")
    else:
        # The two empty-doc baselines come from different engines; if they DIVERGE, every task's
        # delta is net of that blank-doc gap (not pure feature parity) — so surface it loudly.
        bvb = ooxml_diff.diff(RW_BASELINE, WC_BASELINE)
        div = bvb["missing_nodes"] + bvb["extra_nodes"]
        if div:
            print(f"  [!!] BASELINE DIVERGENCE: clone vs Word empty-doc baselines differ in {len(div)} signature(s) "
                  "— task deltas are NET of this blank-doc gap, not pure feature parity:")
            for s in div:
                print(f"        {s}")
            print("       -> fix the clone's blank export, or record these as a separate blank-doc finding.")
        else:
            print("  [i] baselines equivalent — clean delta subtraction.")

    results = []
    for t in tasks:
        tid = t["id"]
        if tid == BASELINE_ID:
            continue   # the baseline is subtracted from tasks, never diffed against itself
        print(f"== task: {tid} ({t.get('feature')}) ==")
        if a.capture:
            print("  capturing clone..."); capture_clone(tid)
            print("  capturing real Word..."); capture_realword(tid, t.get("realword_method", "com"))
        rw = os.path.join(FIX, f"rw-{tid}.docx")
        wc = os.path.join(FIX, f"wc-{tid}.docx")
        if not (os.path.exists(rw) and os.path.exists(wc)):
            print(f"  [!] missing fixtures (rw={os.path.exists(rw)}, wc={os.path.exists(wc)}) — run with --capture")
            continue
        d = ooxml_diff.diff(rw, wc, tid,
                            real_baseline=RW_BASELINE if use_baseline else None,
                            clone_baseline=WC_BASELINE if use_baseline else None)
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

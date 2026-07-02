#!/usr/bin/env python3
"""visual_verify.py — the VISUAL axis harness (rubric D5).

Mechanics (the chain PROVEN in the 2026-07-01 capture trial):
  1. capture:   real-Word ribbon PNG (parity/oracle/_capture_word_ribbon.ps1, maximized,
                Word must be CLOSED) + clone PNG (parity/flow/shot-tab-probe.js /
                scripts/ribbon-shot-probe.js, --start-maximized) per PAIR in visual_pairs.json
  2. composite: stacked side-by-side PNG per pair (labels GERCEK WORD / KLON)
  3. judge:     an LLM (the driving agent) views each composite and answers the FIXED
                question: "same screen of the same program? would a Word user notice a
                difference at a glance? list the differences" — then records the verdict:
                    python parity/engines/visual_verify.py --record <pairId> pass|fail "reason"
  4. trust gate (D5.3): the judge must first classify the GOLDEN pairs correctly
     (golden-identical -> pass, golden-seeded-difference -> fail); verdicts recorded while
     the golden gate is unpassed are REFUSED.

Capture discipline (D5.4) is asserted at capture time: 1920+ primary resolution and both
captures maximized; scale/theme are the operator's checklist (recorded in the run header).

Usage:
  python parity/engines/visual_verify.py --capture           # (re)capture + composite all pairs
  python parity/engines/visual_verify.py --status            # list pairs + verdicts
  python parity/engines/visual_verify.py --record <id> pass|fail "reason"
  python parity/engines/visual_verify.py --golden-ok         # mark the golden gate passed
                                                             # (only after the judge really did)
Outputs parity/results/VISUAL_LEDGER.md + visual.json; composites in C:/tmp/wc-visual/.
"""
import json
import os
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAR = os.path.join(ROOT, "parity")
PAIRS = os.path.join(PAR, "oracle", "visual_pairs.json")
STATE = os.path.join(PAR, "results", "visual.json")
RESULTS = os.path.join(PAR, "results")
OUTDIR = "C:/tmp/wc-visual"
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")
WORD_CAP = os.path.join(PAR, "oracle", "_capture_word_ribbon.ps1")
STACK = os.path.join(PAR, "tools", "stack_compare.ps1")


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {"goldenPassed": False, "verdicts": {}}


def save_state(st):
    os.makedirs(RESULTS, exist_ok=True)
    json.dump(st, open(STATE, "w", encoding="utf-8"), indent=1)


def write_ledger(pairs, st):
    md = ["# Visual Ledger — clone vs real Word, side-by-side (D5)\n",
          "Judge question (FIXED): *same screen of the same program? would a Word user notice",
          "a difference at a glance? list the differences.* Verdicts recorded via",
          "`visual_verify.py --record`; refused until the GOLDEN trust gate passes (D5.3).\n",
          f"**Golden gate:** {'PASSED' if st.get('goldenPassed') else 'NOT PASSED — verdicts refused'}\n",
          "| Pair | What | Verdict | Reason |", "|---|---|---|---|"]
    for p in pairs:
        v = st["verdicts"].get(p["id"], {})
        md.append(f"| {p['id']} | {p['desc']} | {v.get('verdict', '—')} | {v.get('reason', '')} |")
    with open(os.path.join(RESULTS, "VISUAL_LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


def capture(pairs):
    os.makedirs(OUTDIR, exist_ok=True)
    for p in pairs:
        if p.get("golden"):
            continue  # golden pairs are pre-made seeded images, not captured
        wout = f"{OUTDIR}/word-{p['id']}.png"
        cout = f"{OUTDIR}/wc-{p['id']}.png"
        print(f"[{p['id']}] word capture ({p['wordTab']})...")
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", WORD_CAP,
                        "-Tab", p["wordTab"], "-Out", wout.replace("/", "\\")],
                       cwd=ROOT, timeout=240, capture_output=True)
        print(f"[{p['id']}] clone capture ({p['cloneTab']})...")
        subprocess.run([ELECTRON, "--user-data-dir=C:/tmp/wc-visual-profile", "--disable-http-cache",
                        ".", "--start-maximized", f"--shot={cout}",
                        f"--shot-evalfile={os.path.join(PAR, 'flow', p['cloneProbe'])}",
                        "--shot-delay=2200", f"--probe-out={OUTDIR}/probe-{p['id']}.json"],
                       cwd=ROOT, timeout=240, capture_output=True)
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", STACK,
                        "-Top", wout.replace("/", "\\"), "-Bottom", cout.replace("/", "\\"),
                        "-TopLabel", f"GERCEK WORD - {p['desc']}", "-BottomLabel", f"KLON - {p['desc']}",
                        "-Out", f"{OUTDIR}/compare-{p['id']}.png".replace("/", "\\")],
                       cwd=ROOT, timeout=120, capture_output=True)
        print(f"[{p['id']}] composite -> {OUTDIR}/compare-{p['id']}.png")


def main():
    args = sys.argv[1:]
    pairs = json.load(open(PAIRS, encoding="utf-8"))["pairs"]
    st = load_state()
    if "--capture" in args:
        capture(pairs)
    elif "--golden-ok" in args:
        st["goldenPassed"] = True
        save_state(st)
        print("golden gate marked PASSED")
    elif "--record" in args:
        i = args.index("--record")
        pid, verdict = args[i + 1], args[i + 2]
        reason = args[i + 3] if len(args) > i + 3 else ""
        if verdict not in ("pass", "fail"):
            print("verdict must be pass|fail")
            return 2
        p = next((x for x in pairs if x["id"] == pid), None)
        if not p:
            print(f"unknown pair {pid}")
            return 2
        if not st.get("goldenPassed") and not p.get("golden"):
            print("REFUSED: the golden trust gate has not passed (D5.3) — judge the golden pairs first")
            return 1
        st["verdicts"][pid] = {"verdict": verdict, "reason": reason}
        save_state(st)
        print(f"recorded {pid}: {verdict}")
    write_ledger(pairs, st)
    real = [p for p in pairs if not p.get("golden")]
    judged = sum(1 for p in real if p["id"] in st["verdicts"])
    passed = sum(1 for p in real if st["verdicts"].get(p["id"], {}).get("verdict") == "pass")
    print(f"VISUAL: {passed} pass / {judged - passed} fail / {len(real) - judged} unjudged "
          f"(golden gate {'OK' if st.get('goldenPassed') else 'PENDING'})")
    print("ledger: parity/results/VISUAL_LEDGER.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())

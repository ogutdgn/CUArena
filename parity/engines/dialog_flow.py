#!/usr/bin/env python3
"""Dialog flow verifier — the FLOW axis of the deep T0/T1 dialog enumeration.

For each T0/T1 dialog it checks, at runtime (dialog-flow-probe.js), (a) the dialog OPENS, (b) which of
Word's fields are PRESENT in the clone dialog, flagging Word-has-but-clone-lacks fields, and (c) an OK/
apply control exists. A flow gap = the dialog doesn't open, OK is missing, or a Word field is absent.
This RUNTIME-CONFIRMS the field-presence claims the code-trace investigation recorded as IDENTIFIED_GAPS.

Field presence is keyword matching against the labels/placeholders the probe collected (case-insensitive
substring). EXPECTED lists every field WORD's dialog exposes; `clone_lacks=True` marks the ones the
investigation already traced as absent (so a regression that ADDS them flips the expectation, and a
regression that DROPS a present field is caught).

Usage (repo root):
  python parity/engines/dialog_flow.py               # analyze existing dialog-flow-actual.json + selfcheck
  python parity/engines/dialog_flow.py --capture     # run the clone probe first (needs the built app)
  python parity/engines/dialog_flow.py --selfcheck   # golden + self-consistency only (exit 1 on failure)
"""
import os, sys, json, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ENGINES = os.path.dirname(os.path.abspath(__file__))
PARITY = os.path.dirname(ENGINES)
ROOT = os.path.dirname(PARITY)
FLOWDIR = os.path.join(PARITY, "flow")
PROBE = os.path.join(FLOWDIR, "dialog-flow-probe.js")
ACTUAL = os.path.join(FLOWDIR, "dialog-flow-actual.json")
RESULTS = os.path.join(PARITY, "results")
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")

# Per dialog: (field_key, [keywords], clone_lacks). clone_lacks=True => the investigation traced it absent
# (Word has it, the clone dialog omits it) — a known flow gap; False => expected present in the clone.
EXPECTED = {
    "font": [
        ("style", ["style", "bold", "italic", "regular"], False),
        ("size", ["size"], False),
        ("font-color", ["font color", "color"], False),
        ("underline-style", ["underline"], False),
        ("underline-color", ["underline color"], True),
        ("strikethrough", ["strikethrough"], False),
        ("double-strikethrough", ["double strikethrough", "double strike"], True),
        ("superscript", ["superscript"], False),
        ("subscript", ["subscript"], False),
        ("small-caps", ["small caps"], False),
        ("all-caps", ["all caps"], False),
        ("hidden", ["hidden"], True),
        ("scale", ["scale"], False),
        ("spacing", ["spacing"], False),
        ("position", ["position"], False),
        ("ligatures", ["ligatures"], True),
        ("kerning", ["kerning"], True),
    ],
    "paragraph": [
        ("alignment", ["alignment"], False),
        ("indent-left", ["indent left", "left"], False),
        ("indent-right", ["indent right", "right"], False),
        ("special", ["special"], False),
        ("spacing-before", ["before"], False),
        ("spacing-after", ["after"], False),
        ("line-spacing", ["line spacing"], False),
        ("widow-orphan", ["widow"], True),
        ("keep-with-next", ["keep with next"], True),
        ("keep-lines", ["keep lines"], True),
        ("page-break-before", ["page break before"], True),
    ],
    "find-replace": [
        ("find", ["find"], False),
        ("replace", ["replace"], False),
        ("match-case", ["match case"], False),
        ("whole-word", ["whole word"], False),
        ("wildcards", ["wildcard"], False),
        ("special", ["special"], False),
        ("format", ["format"], False),
    ],
    "insert-table": [
        ("rows", ["rows"], False),
        ("columns", ["columns", "cols"], False),
    ],
    "insert-hyperlink": [
        ("text", ["text to display", "text"], False),
        ("address", ["address", "url"], False),
    ],
    "page-margins": [
        ("top", ["top"], True),      # clone has ONE uniform 'Margin (inches)' field, not independent sides
        ("bottom", ["bottom"], True),
        ("left", ["left"], True),
        ("right", ["right"], True),
    ],
}


def _has(keywords, labels_lc):
    return any(any(k in lab for lab in labels_lc) for k in keywords)


def analyze_dialog(dialog_id, rec):
    """Classify one dialog's flow. Pure function (golden-testable)."""
    expected = EXPECTED.get(dialog_id, [])
    snap = (rec or {}).get("snapshot") or {}
    # button text is part of the field surface too (Find/Replace exposes Special/Format as buttons)
    labels_lc = [str(s).lower() for s in (snap.get("labels", []) + snap.get("buttons", []))]
    opened = bool((rec or {}).get("opened"))
    ok_present = bool(snap.get("ok_present"))
    fields = []
    for key, keywords, clone_lacks in expected:
        present = _has(keywords, labels_lc) if opened else False
        # a gap = Word-has-clone-lacks confirmed absent, OR a field expected-present that is missing
        if clone_lacks:
            status = "gap-missing-field" if not present else "unexpectedly-present"
        else:
            status = "present" if present else "gap-missing-field"
        fields.append({"field": key, "present": present, "word_has": True,
                       "expected_in_clone": not clone_lacks, "status": status})
    missing = [f["field"] for f in fields if f["status"] == "gap-missing-field"]
    hard = (not opened) or (opened and not ok_present and dialog_id != "page-margins")
    return {
        "dialog": dialog_id, "opened": opened, "ok_present": ok_present,
        "verdict": "flow-gap" if (hard or missing) else "flow-pass",
        "fields": fields, "missing_fields": missing,
        "field_count": len(fields), "present_count": sum(1 for f in fields if f["present"]),
    }


def analyze(actual_json):
    by_id = {d.get("id"): d for d in actual_json.get("dialogs", [])}
    return [analyze_dialog(did, by_id.get(did)) for did in EXPECTED]


# ------------------------------------------------------------------ regression-lock
def golden_cases():
    # (name, dialog_id, rec, expected_verdict, expected_missing_subset)
    font_full = {"opened": True, "snapshot": {"ok_present": True, "labels": [
        "Style", "Size", "Font color", "Underline", "Strikethrough", "Superscript", "Subscript",
        "Small caps", "All caps", "Scale", "Spacing", "Position"]}}
    return [
        ("font_clone_known_gaps", "font", font_full, "flow-gap",
         ["underline-color", "double-strikethrough", "hidden", "ligatures", "kerning"]),
        ("dialog_did_not_open", "insert-table", {"opened": False}, "flow-gap", ["rows", "columns"]),
        ("ok_missing", "insert-hyperlink", {"opened": True, "snapshot": {"ok_present": False, "labels": ["Text to display", "Address"]}}, "flow-gap", []),
        ("find_all_present", "find-replace", {"opened": True, "snapshot": {"ok_present": True, "labels": [
            "Find in document", "Replace with", "Match case", "Whole words only", "Use wildcards", "Special", "Format"]}}, "flow-pass", []),
    ]


def run_golden():
    out = []
    for name, did, rec, exp_v, exp_missing in golden_cases():
        r = analyze_dialog(did, rec)
        ok = (r["verdict"] == exp_v) and all(m in r["missing_fields"] for m in exp_missing)
        out.append({"name": name, "exp": exp_v, "got": r["verdict"], "ok": ok, "missing": r["missing_fields"]})
    return out


def self_consistency(a, b):
    ka = {d["dialog"]: (d["verdict"], tuple(sorted(d["missing_fields"]))) for d in analyze(a)}
    kb = {d["dialog"]: (d["verdict"], tuple(sorted(d["missing_fields"]))) for d in analyze(b)}
    return [k for k in (set(ka) | set(kb)) if ka.get(k) != kb.get(k)]


def capture():
    os.makedirs(FLOWDIR, exist_ok=True)
    cmd = [ELECTRON, "--user-data-dir=C:/tmp/wc-dialogflow-profile", "--disable-http-cache", ".",
           f"--probe-out={ACTUAL}", f"--shot-evalfile={PROBE}"]
    subprocess.run(cmd, cwd=ROOT, timeout=180, capture_output=True)


def write_ledger(results):
    os.makedirs(RESULTS, exist_ok=True)
    npass = sum(1 for r in results if r["verdict"] == "flow-pass")
    md = ["# Dialog Flow Ledger — clone dialog fields vs. Word's dialog (runtime)\n",
          "Auto-generated by `parity/engines/dialog_flow.py`. Opens each T0/T1 dialog at runtime and checks "
          "which of Word's fields are present. **flow-gap** = dialog won't open / OK missing / a Word field "
          "is absent. `missing fields` are Word-has-clone-lacks (runtime-confirmed code-trace gaps).\n",
          f"**Dialogs:** {len(results)} · **flow-pass:** {npass} · **flow-gap:** {len(results) - npass}\n",
          "| Dialog | opens | OK | fields present | missing (Word-has-clone-lacks) | verdict |",
          "|---|---|---|---|---|---|"]
    for r in results:
        v = "✅ pass" if r["verdict"] == "flow-pass" else "🟠 gap"
        miss = ", ".join(r["missing_fields"]) or "—"
        md.append(f"| `{r['dialog']}` | {'yes' if r['opened'] else 'NO'} | {'yes' if r['ok_present'] else 'no'} "
                  f"| {r['present_count']}/{r['field_count']} | {miss} | {v} |")
    with open(os.path.join(RESULTS, "DIALOG_FLOW_LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    json.dump(results, open(os.path.join(RESULTS, "dialog_flow_ledger.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return os.path.join(RESULTS, "DIALOG_FLOW_LEDGER.md")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    golden = run_golden()
    gpass = sum(1 for g in golden if g["ok"])
    print(f"GOLDEN (dialog-flow logic): {gpass}/{len(golden)} pass")
    for g in golden:
        if not g["ok"]:
            print(f"  [X] {g['name']}: exp {g['exp']} got {g['got']} missing={g['missing']}")

    diffs = []
    if a.capture:
        print("capturing dialog flow (clone)..."); capture()
        first = json.load(open(ACTUAL, encoding="utf-8"))
        capture()
        second = json.load(open(ACTUAL, encoding="utf-8"))
        diffs = self_consistency(first, second)
        print(f"SELF-CONSISTENCY: {'OK (deterministic)' if not diffs else 'NON-DETERMINISTIC on ' + ', '.join(diffs)}")
        json.dump(first, open(ACTUAL, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    if a.selfcheck:
        ok = (gpass == len(golden)) and not diffs
        print("DIALOG-FLOW SELF-CHECK:", "PASS" if ok else "FAIL")
        return 0 if ok else 1

    if not os.path.exists(ACTUAL):
        print(f"[!] no {ACTUAL} — run with --capture (needs the built app)"); return 1
    results = analyze(json.load(open(ACTUAL, encoding="utf-8")))
    path = write_ledger(results)
    npass = sum(1 for r in results if r["verdict"] == "flow-pass")
    print(f"Dialog-flow ledger written: {path}  ({npass}/{len(results)} flow-pass)")
    return 0 if gpass == len(golden) else 1


if __name__ == "__main__":
    sys.exit(main())

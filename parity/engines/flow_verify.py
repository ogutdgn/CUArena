#!/usr/bin/env python3
"""Flow verifier — the SECOND parity axis (interaction flow, not OOXML).

For each control it checks what the clone DOM actually does on click (from flow-probe.js's
live introspection) against the ribbon-data spec (control `type` + `items[]`): does it open the
right thing (toggle/button -> apply, combo -> combo, split/dropdown -> flyout), is the launcher
DEAD (nothing opens), and are the declared menu items present. Type-mismatch / dead-launcher /
missing-control are HARD flow gaps; declared-vs-actual item differences are reported informationally
(ribbon-data items[] are often category labels, so item matching is fuzzy by design).

Usage (from repo root):
  python parity/engines/flow_verify.py                 # analyze existing flow-actual.json + self-check
  python parity/engines/flow_verify.py --capture       # run the clone probe first (needs the built app)
  python parity/engines/flow_verify.py --selfcheck     # golden + self-consistency only (exit 1 on failure)
"""
import os, sys, json, re, subprocess

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ENGINES = os.path.dirname(os.path.abspath(__file__))
PARITY = os.path.dirname(ENGINES)
ROOT = os.path.dirname(PARITY)
FLOWDIR = os.path.join(PARITY, "flow")
PROBE = os.path.join(FLOWDIR, "flow-probe.js")
ACTUAL = os.path.join(FLOWDIR, "flow-actual.json")
RESULTS = os.path.join(PARITY, "results")
ELECTRON = os.path.join(ROOT, "node_modules", "electron", "dist", "electron.exe")

# declared ribbon-data `type` -> the actual DOM interaction we expect on click
EXPECT_KIND = {"toggle": "apply", "button": "apply", "combo": "combo", "split": "flyout", "dropdown": "flyout"}
# declared item labels that are CATEGORIES / galleries (rendered as swatch/preview grids, not
# .fi-label text items) -> not text-matchable, skip in the item-presence check.
CATEGORY_ITEMS = {"underline styles", "color swatches", "standard colors", "theme colors", "recent colors",
                  "bullet library", "numbering library", "document bullets", "list library",
                  "recently used bullets", "recently used numbers", "recently used number formats"}
DEAD_KINDS = {"nothing", "error", "missing-control", None}


def _norm(s):
    return re.sub(r"[.…\s]+$", "", str(s).strip().lower())


def analyze_control(rec):
    """Classify one control's flow into a verdict + flags. Pure function (golden-testable)."""
    dtype = rec.get("type")
    kind = rec.get("kind")
    expected = EXPECT_KIND.get(dtype)
    flags = []
    if not rec.get("found"):
        flags.append("control-missing-from-ribbon")
    elif rec.get("rendered") is False:
        flags.append("not-rendered-in-dom")
    if kind in DEAD_KINDS:
        flags.append("dead-launcher")
    elif expected and kind != expected:
        flags.append(f"type-mismatch (declared {dtype} -> actual {kind}, expected {expected})")
    # declared item presence (fuzzy / informational): a swatch menu carries the rest visually
    declared = rec.get("items") or []
    actual = [_norm(x) for x in (rec.get("actual_items") or [])]
    has_swatches = bool(rec.get("swatch_count"))
    missing = []
    for di in declared:
        nd = _norm(di)
        if nd in CATEGORY_ITEMS:
            continue
        present = any(nd in a or a in nd for a in actual)
        if not present and not has_swatches:
            missing.append(di)
    hard = [f for f in flags if "dead-launcher" in f or "type-mismatch" in f or "missing-from-ribbon" in f or "not-rendered" in f]
    return {
        "id": rec.get("id"), "type": dtype, "kind": kind,
        "verdict": "flow-gap" if hard else "flow-pass",
        "flags": flags,
        "declared_items": declared, "actual_items": rec.get("actual_items") or [],
        "actual_item_count": rec.get("actual_item_count", 0), "swatch_count": rec.get("swatch_count", 0),
        "possibly_missing_items": missing,
    }


def analyze(actual_json):
    return [analyze_control(c) for c in actual_json.get("controls", [])]


# ------------------------------------------------------------------ regression-lock
def golden_cases():
    # (name, record, expected_verdict, expected_flag_substring_or_None)
    return [
        ("toggle_applies", {"id": "t", "found": True, "rendered": True, "type": "toggle", "kind": "apply"}, "flow-pass", None),
        ("combo_combo", {"id": "c", "found": True, "rendered": True, "type": "combo", "kind": "combo"}, "flow-pass", None),
        ("split_opens", {"id": "s", "found": True, "rendered": True, "type": "split", "kind": "flyout",
                          "actual_items": ["Single", "Double"], "actual_item_count": 2}, "flow-pass", None),
        ("dead_dropdown", {"id": "d", "found": True, "rendered": True, "type": "dropdown", "kind": "nothing"}, "flow-gap", "dead-launcher"),
        ("type_mismatch", {"id": "m", "found": True, "rendered": True, "type": "toggle", "kind": "flyout"}, "flow-gap", "type-mismatch"),
        ("missing_control", {"id": "x", "found": False}, "flow-gap", "missing-from-ribbon"),
        ("missing_item", {"id": "i", "found": True, "rendered": True, "type": "split", "kind": "flyout",
                           "items": ["Define New Bullet"], "actual_items": ["Change List Level"], "swatch_count": 0}, "flow-pass", None),
    ]


def run_golden():
    out = []
    for name, rec, exp_v, exp_flag in golden_cases():
        r = analyze_control(rec)
        ok = (r["verdict"] == exp_v) and (exp_flag is None or any(exp_flag in f for f in r["flags"]))
        # missing_item case: verify the informational missing list is populated (not a hard gap)
        if name == "missing_item":
            ok = ok and (r["possibly_missing_items"] == ["Define New Bullet"]) and (r["verdict"] == "flow-pass")
        out.append({"name": name, "exp": exp_v, "got": r["verdict"], "ok": ok, "flags": r["flags"]})
    return out


def self_consistency(a, b):
    """Two probe runs must analyze to the same per-control (verdict, kind, flags)."""
    ka = {c["id"]: (c["verdict"], c["kind"], tuple(sorted(c["flags"]))) for c in analyze(a)}
    kb = {c["id"]: (c["verdict"], c["kind"], tuple(sorted(c["flags"]))) for c in analyze(b)}
    diffs = [k for k in (set(ka) | set(kb)) if ka.get(k) != kb.get(k)]
    return diffs


def capture():
    os.makedirs(FLOWDIR, exist_ok=True)
    cmd = [ELECTRON, "--user-data-dir=C:/tmp/wc-flow-profile", "--disable-http-cache", ".",
           f"--probe-out={ACTUAL}", f"--shot-evalfile={PROBE}"]
    subprocess.run(cmd, cwd=ROOT, timeout=180, capture_output=True)


def write_ledger(results, src):
    os.makedirs(RESULTS, exist_ok=True)
    npass = sum(1 for r in results if r["verdict"] == "flow-pass")
    md = ["# Flow Ledger — clone interaction flow vs. ribbon-data spec\n",
          "Auto-generated by `parity/engines/flow_verify.py`. Checks what each control OPENS on click "
          "(clone DOM) against the ribbon-data `type`/`items[]`. **flow-gap** = type mismatch / dead launcher / "
          "missing control (a real flow defect). `possibly missing items` is informational (ribbon-data items[] "
          "are often category labels; swatch menus carry items visually).\n",
          f"**Controls:** {len(results)} · **flow-pass:** {npass} · **flow-gap:** {len(results) - npass}\n",
          "| Control | type | opens | verdict | flags / notes |", "|---|---|---|---|---|"]
    for r in results:
        note = "; ".join(r["flags"]) or (f"items: {r['actual_item_count']} + {r['swatch_count']} swatches" +
                                         (f"; possibly missing: {', '.join(r['possibly_missing_items'])}" if r["possibly_missing_items"] else ""))
        v = "✅ pass" if r["verdict"] == "flow-pass" else "🟠 gap"
        md.append(f"| `{r['id']}` | {r['type']} | {r['kind']} | {v} | {note} |")
    with open(os.path.join(RESULTS, "FLOW_LEDGER.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    json.dump(results, open(os.path.join(RESULTS, "flow_ledger.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    return os.path.join(RESULTS, "FLOW_LEDGER.md")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", action="store_true")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args()

    # regression-lock: golden logic
    golden = run_golden()
    gpass = sum(1 for g in golden if g["ok"])
    print(f"GOLDEN (flow logic): {gpass}/{len(golden)} pass")
    for g in golden:
        if not g["ok"]:
            print(f"  ❌ {g['name']}: exp {g['exp']} got {g['got']} flags={g['flags']}")

    if a.capture:
        print("capturing flow (clone)..."); capture()
        # self-consistency: capture a second time and compare
        import shutil
        first = json.load(open(ACTUAL, encoding="utf-8"))
        capture()
        second = json.load(open(ACTUAL, encoding="utf-8"))
        diffs = self_consistency(first, second)
        print(f"SELF-CONSISTENCY: {'OK (deterministic)' if not diffs else 'NON-DETERMINISTIC on ' + ', '.join(diffs)}")
        json.dump(first, open(ACTUAL, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    else:
        diffs = []

    if a.selfcheck:
        ok = (gpass == len(golden)) and not diffs
        print("FLOW SELF-CHECK:", "✅ PASS" if ok else "❌ FAIL")
        return 0 if ok else 1

    if not os.path.exists(ACTUAL):
        print(f"[!] no {ACTUAL} — run with --capture (needs the built app)"); return 1
    results = analyze(json.load(open(ACTUAL, encoding="utf-8")))
    path = write_ledger(results, ACTUAL)
    npass = sum(1 for r in results if r["verdict"] == "flow-pass")
    print(f"Flow ledger written: {path}  ({npass}/{len(results)} flow-pass)")
    return 0 if gpass == len(golden) else 1


if __name__ == "__main__":
    sys.exit(main())

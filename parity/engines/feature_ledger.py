#!/usr/bin/env python3
"""feature_ledger.py — THE multi-axis report card: 111 locked features × the rubric's axes.

Columns (rubric v2): OOXML · STRUCT · STATE · SCORE(card) · VISUAL · BEHAV(ior).
A feature is DONE only when every column passes; an unmeasured axis shows "—" and the feature
can NOT be called done (the no-silent-caps / not-measured-is-not-green rule).

Inputs (each optional — absent axis = "—"):
  parity/oracle/feature_registry.json   (gen_feature_registry.py)
  parity/results/structure.json         STRUCTURE axis (+ menus)
  parity/results/state.json             STATE axis
  parity/results/scorecard.json         SCORECARD axis
  parity/results/ledger.json            OOXML axis (run.py)

Output: parity/results/FEATURE_LEDGER.md + feature_ledger.json
Usage: python parity/engines/feature_ledger.py [--report-only]
Exit: 0 / 1 if any measured column has gaps (unless --report-only) / 2 harness failure.
"""
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PAR = os.path.join(ROOT, "parity")
RESULTS = os.path.join(PAR, "results")
REGISTRY = os.path.join(PAR, "oracle", "feature_registry.json")

COLS = ["OOXML", "STRUCT", "STATE", "SCORE", "VISUAL", "BEHAV"]


def load(path):
    try:
        return json.load(open(path, encoding="utf-8"))
    except Exception:
        return None


def main():
    args = sys.argv[1:]
    reg = load(REGISTRY)
    if not reg:
        print("feature_ledger: missing feature_registry.json (run gen_feature_registry.py)")
        return 2
    structure = load(os.path.join(RESULTS, "structure.json"))
    state = load(os.path.join(RESULTS, "state.json"))
    scorecard = load(os.path.join(RESULTS, "scorecard.json"))
    ooxml = load(os.path.join(RESULTS, "ledger.json"))
    visual = load(os.path.join(RESULTS, "visual.json"))
    vpairs = load(os.path.join(PAR, "oracle", "visual_pairs.json"))
    behavior = load(os.path.join(RESULTS, "behavior.json"))

    # ---- index the axis results by clone cmd / task id ----
    pair_bucket, menu_missing = {}, {}
    if structure:
        for tab, r in structure["per_tab"].items():
            for bucket in ("matched", "label_differs", "type_mismatch"):
                for p in r.get(bucket, []):
                    if p["clone"].get("cmd"):
                        pair_bucket[(tab, p["clone"]["cmd"])] = bucket
            for p in r.get("extra", []):   # clone-only controls Word doesn't have = a STRUCT gap
                cmd = p.get("cmd") or (p.get("clone") or {}).get("cmd")
                if cmd:
                    pair_bucket[(tab, cmd)] = "extra"
            for m in r.get("menus", []):
                if m.get("cloneCmd"):
                    menu_missing[(tab, m["cloneCmd"])] = len(m["missing"])
    state_bad = {}
    if state:
        for r in state.get("mismatches", []):
            state_bad.setdefault(r["cmd"], []).append(r["diff"])
    # VISUAL: pair verdicts rolled up per feature (pair config carries `feature`)
    vis_feat = {}
    if visual and vpairs:
        for pr in vpairs.get("pairs", []):
            fk = pr.get("feature")
            if not fk or pr.get("golden"):
                continue
            v = (visual.get("verdicts") or {}).get(pr["id"], {}).get("verdict")
            if v:
                vis_feat.setdefault(fk, []).append(v)
    # BEHAVIOR: card verdicts rolled up per feature (cards carry `feature`). SAMPLED (D6.4).
    beh_feat = {}
    if behavior:
        for c in behavior.get("cards", []):
            fk = c.get("feature")
            if fk:
                beh_feat.setdefault(fk, []).append(c.get("verdict"))
    score_verdict = {}
    if scorecard:
        for r in scorecard.get("controls", []):
            if r.get("cmd"):
                v = r.get("verdict")
                cur = score_verdict.get(r["cmd"])
                rank = {"dead": 3, "triage": 2, "pass": 1, "skip": 0}
                if cur is None or rank.get(v, 0) > rank.get(cur, 0):
                    score_verdict[r["cmd"]] = v
    task_verdict = {}
    if ooxml:
        rows = ooxml.get("tasks", ooxml) if isinstance(ooxml, dict) else ooxml
        if isinstance(rows, dict):
            for tid, r in rows.items():
                task_verdict[tid] = (r or {}).get("verdict")
        elif isinstance(rows, list):
            for r in rows:
                if isinstance(r, dict) and r.get("id"):
                    task_verdict[r["id"]] = r.get("verdict")

    # ---- per-feature verdicts ----
    rows = []
    for f in reg["features"]:
        row = {"name": f["name"], "tab": f["tab"], "tier": f["tier"], "cols": {}}
        # OOXML
        tv = [task_verdict.get(t) for t in f["ooxmlTasks"] if t in task_verdict]
        if not tv:
            row["cols"]["OOXML"] = "—"
        elif all(v in ("semantic-pass", "pass-with-note") for v in tv):
            _nn = sum(1 for v in tv if v == "pass-with-note")
            row["cols"]["OOXML"] = f"pass({len(tv)})" + (f"+{_nn}note" if _nn else "")
        else:
            row["cols"]["OOXML"] = f"GAP({sum(1 for v in tv if v not in ('semantic-pass','pass-with-note'))}/{len(tv)})"
        # STRUCT (control bucket + its menus' missing items)
        if not structure or not f["cmds"]:
            row["cols"]["STRUCT"] = "—"
        else:
            buckets = [pair_bucket.get((f["tab"], c)) for c in f["cmds"]]
            miss = sum(menu_missing.get((f["tab"], c), 0) for c in f["cmds"])
            if miss:
                row["cols"]["STRUCT"] = f"GAP(items:{miss})"
            elif "type_mismatch" in buckets:
                row["cols"]["STRUCT"] = "GAP(type)"
            elif "extra" in buckets:
                row["cols"]["STRUCT"] = "GAP(extra)"
            elif any(b is None for b in buckets):
                row["cols"]["STRUCT"] = "MISSING?"
            elif "label_differs" in buckets:
                row["cols"]["STRUCT"] = "warn(label)"
            else:
                row["cols"]["STRUCT"] = "pass"
        # STATE
        if not state or not f["cmds"]:
            row["cols"]["STATE"] = "—"
        else:
            bad = sum(len(state_bad.get(c, [])) for c in f["cmds"])
            row["cols"]["STATE"] = f"GAP({bad})" if bad else "pass"
        # SCORECARD
        if not scorecard or not f["cmds"]:
            row["cols"]["SCORE"] = "—"
        else:
            vs = [score_verdict.get(c) for c in f["cmds"] if score_verdict.get(c)]
            if not vs:
                row["cols"]["SCORE"] = "—"
            elif "dead" in vs:
                row["cols"]["SCORE"] = "DEAD"
            elif "triage" in vs:
                row["cols"]["SCORE"] = "triage"
            else:
                row["cols"]["SCORE"] = "pass"
        # VISUAL / BEHAVIOR — rolled up where pairs/cards exist; SAMPLED per D6.4
        vv = vis_feat.get(f["name"], [])
        if not vv:
            row["cols"]["VISUAL"] = "—"
        elif "fail" in vv:
            row["cols"]["VISUAL"] = f"GAP({sum(1 for x in vv if x == 'fail')}/{len(vv)})"
        else:
            row["cols"]["VISUAL"] = f"pass({len(vv)} sampled)"
        bv = beh_feat.get(f["name"], [])
        if not bv:
            row["cols"]["BEHAV"] = "—"
        elif "fail" in bv:
            row["cols"]["BEHAV"] = f"GAP({sum(1 for x in bv if x == 'fail')}/{len(bv)})"
        elif "pending" in bv:
            row["cols"]["BEHAV"] = f"pending({sum(1 for x in bv if x == 'pending')}/{len(bv)})"
        else:
            row["cols"]["BEHAV"] = f"pass({len(bv)} sampled)"
        rows.append(row)

    def is_pass(v):
        return v.startswith("pass")

    def is_gap(v):
        return v.startswith("GAP") or v in ("DEAD", "MISSING?")

    done = [r for r in rows if all(is_pass(r["cols"][c]) for c in COLS)]
    col_stats = {c: {"pass": sum(1 for r in rows if is_pass(r["cols"][c])),
                     "gap": sum(1 for r in rows if is_gap(r["cols"][c])),
                     "warn": sum(1 for r in rows if r["cols"][c].startswith(("warn", "triage"))),
                     "unmeasured": sum(1 for r in rows if r["cols"][c] == "—")}
                 for c in COLS}

    os.makedirs(RESULTS, exist_ok=True)
    md = ["# Feature Ledger — 111 locked features × the rubric axes\n",
          "Auto-generated by `parity/engines/feature_ledger.py`. **DONE requires every column",
          "green; an unmeasured axis (—) blocks done** (not-measured ≠ no-gaps).\n",
          f"**FULLY VERIFIED (all axes pass): {len(done)} / {len(rows)}**\n",
          "| Axis | pass | gap | warn/triage | unmeasured |", "|---|---|---|---|---|"]
    for c in COLS:
        s = col_stats[c]
        md.append(f"| {c} | {s['pass']} | **{s['gap']}** | {s['warn']} | {s['unmeasured']} |")
    md += ["\n| Feature | Tab | Tier | " + " | ".join(COLS) + " |",
           "|---|---|---|" + "---|" * len(COLS)]
    for r in rows:
        md.append(f"| {r['name']} | {r['tab']} | {r['tier']} | "
                  + " | ".join(r["cols"][c] for c in COLS) + " |")
    with open(os.path.join(RESULTS, "FEATURE_LEDGER.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    with open(os.path.join(RESULTS, "feature_ledger.json"), "w", encoding="utf-8") as fh:
        json.dump({"done": len(done), "col_stats": col_stats, "rows": rows}, fh, indent=1)

    print(f"FEATURE LEDGER: fully-verified {len(done)}/{len(rows)}")
    for c in COLS:
        s = col_stats[c]
        print(f"  {c:7s} pass {s['pass']:3d} / gap {s['gap']:3d} / warn {s['warn']:3d} / unmeasured {s['unmeasured']:3d}")
    print("ledger: parity/results/FEATURE_LEDGER.md")
    any_gap = any(col_stats[c]["gap"] for c in COLS)
    if any_gap and "--report-only" not in args:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

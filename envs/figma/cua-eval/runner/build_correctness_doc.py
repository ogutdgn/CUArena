"""Build VERIFIER_CORRECTNESS_AUDIT.md from audit_correctness.json.

This audit asks ONLY: does each verifier check what its own prompt asks
for? Model performance is NOT considered.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/build_correctness_doc.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}


def main() -> int:
    p = Path("audit_correctness.json")
    if not p.is_file():
        print("ERROR: run audit_correctness.py first")
        return 1
    audit = json.load(p.open())

    n = len(audit)
    clean = [t for t in audit if t["n_issues"] == 0]
    issue_types: Counter = Counter()
    severities: Counter = Counter()
    for t in audit:
        for i in t["issues"]:
            issue_types[i["type"]] += 1
            severities[i["severity"]] += 1

    today = datetime.now().strftime("%B %d, %Y")

    out: list[str] = []
    out.append("# Verifier Correctness Audit — does each verifier check what its prompt asks for?")
    out.append("")
    out.append(f"_Generated {today}. This audit ignores model performance entirely. The only")
    out.append("question is: **does each task's verifier accurately enforce what its own")
    out.append("`prompt.md` asks for**?_")
    out.append("")
    out.append("For each task, we parse the prompt's `## Thorough description` section")
    out.append("(the contract the harness sends to the model in default prompt-mode) and")
    out.append("cross-reference it against the verifier's checks. Mismatches are flagged")
    out.append("by category:")
    out.append("")
    out.append("| Issue type | Meaning | Severity |")
    out.append("|---|---|---|")
    out.append("| `FRAME-OVERSPEC` | Verifier requires `LayerInsideFrame` / `AllLayerBoundsInside(outer=frame)` but the prompt's thorough description never mentions a Figma frame. | high |")
    out.append("| `FRAME-UNDERSPEC` | Prompt explicitly asks for a frame but verifier has no frame containment check. | low |")
    out.append("| `BRITTLE-ALIGN-TOLERANCE` | Verifier uses an alignment tolerance below 15 px. Tight relative to typical drag-create variance. | medium |")
    out.append("| `EFFECT-OVERSPEC` | Verifier requires drop-shadow / blur effect but prompt doesn't mention effects. | medium |")
    out.append("| `SIZE-OVERSPEC` | Verifier requires exact W×H but the prompt only gives a qualitative size. | medium |")
    out.append("| `COLOR-OVERSPEC` | Verifier requires a specific RGB but the prompt mentions no color. | medium |")
    out.append("| `SHAPE-CHECK-MISSING` | Prompt names a quantity of shapes but verifier has no ShapeCount check for that type. | medium |")
    out.append("| `CORNER-RADIUS-OVERSPEC` | Verifier REQUIRES rounded corners (`CornerRadiusAtLeast(min_value > 0)`) but prompt doesn't mention 'rounded'. | medium |")
    out.append("")
    out.append("Notes on what we **don't** flag:")
    out.append("- `CornerRadiusFractionAtMost` (a 'don't be too round / accidentally became a pill' sanity check) is")
    out.append("  legitimate and not counted as over-spec.")
    out.append("- Tool-use is a recipe hint, not a contract. Verifiers should check outputs, not which tool")
    out.append("  produced them. Tool-mismatch is not a correctness gap.")
    out.append("- Critical-halving rules in the rubric framework are a tuning issue, not a correctness gap.")
    out.append("")

    out.append("## Headline")
    out.append("")
    out.append("| Metric | Value |")
    out.append("|---|---|")
    out.append(f"| Tasks audited | **{n}/50** |")
    out.append(f"| **CLEAN** (no detected issues) | **{len(clean)}** |")
    out.append(f"| With ≥ 1 issue | {n - len(clean)} |")
    out.append(f"| High-severity issues total | {severities.get('high', 0)} |")
    out.append(f"| Medium-severity issues total | {severities.get('medium', 0)} |")
    out.append("")
    out.append("**Issue-type counts:**")
    out.append("")
    out.append("| Issue type | Count | % of tasks |")
    out.append("|---|---|---|")
    for it, cnt in issue_types.most_common():
        out.append(f"| `{it}` | {cnt} | {cnt*100/n:.0f}% |")
    out.append("")

    # Cross-tabulate: how many have frame+align together?
    fr = set(t["task_id"] for t in audit
             if any(i["type"] == "FRAME-OVERSPEC" for i in t["issues"]))
    al = set(t["task_id"] for t in audit
             if any(i["type"] == "BRITTLE-ALIGN-TOLERANCE" for i in t["issues"]))
    out.append("**Cross-tabulation of the two biggest issues:**")
    out.append("")
    out.append("| | brittle-align | clean align |")
    out.append("|---|---|---|")
    out.append(f"| frame-overspec | {len(fr & al)} | {len(fr - al)} |")
    out.append(f"| clean frame | {len(al - fr)} | {n - len(fr | al)} |")
    out.append("")

    # Clean tasks
    out.append(f"## CLEAN tasks ({len(clean)})")
    out.append("")
    out.append("Verifiers that match their prompt cleanly — no detected over-spec or brittleness:")
    out.append("")
    for t in sorted(clean, key=lambda x: x["task_id"]):
        out.append(f"- `{t['task_id']}`")
    out.append("")

    # Per-issue task lists
    out.append("## Per-issue inventories")
    out.append("")
    for it in ["FRAME-OVERSPEC", "BRITTLE-ALIGN-TOLERANCE", "FRAME-UNDERSPEC",
               "EFFECT-OVERSPEC", "SIZE-OVERSPEC", "COLOR-OVERSPEC",
               "SHAPE-CHECK-MISSING", "CORNER-RADIUS-OVERSPEC"]:
        affected = [t for t in audit if any(i["type"] == it for i in t["issues"])]
        if not affected:
            continue
        out.append(f"### `{it}` ({len(affected)} tasks)")
        out.append("")
        for t in sorted(affected, key=lambda x: x["task_id"]):
            details = next((i["detail"] for i in t["issues"] if i["type"] == it), "")
            # Compact: just task id + short reason
            out.append(f"- `{t['task_id']}` — {details[:120]}")
        out.append("")

    # Full per-task table
    out.append("## Full per-task table")
    out.append("")
    out.append("| Task | # Issues | Severity max | Types |")
    out.append("|---|---|---|---|")
    rank_audit = sorted(
        audit,
        key=lambda t: (
            -max((SEVERITY_RANK.get(i["severity"], 0) for i in t["issues"]), default=0),
            -t["n_issues"],
            t["task_id"],
        ),
    )
    for t in rank_audit:
        if t["n_issues"] == 0:
            sev = "—"
            types_str = "—"
        else:
            sev = max((i["severity"] for i in t["issues"]),
                      key=lambda s: SEVERITY_RANK.get(s, 0))
            types_str = ", ".join(sorted(set(i["type"] for i in t["issues"])))
        out.append(f"| `{t['task_id']}` | {t['n_issues']} | {sev} | {types_str} |")
    out.append("")

    # Recommended actions
    out.append("## Recommended actions (verifier-side only)")
    out.append("")
    out.append("In priority order by tasks-affected × severity:")
    out.append("")
    out.append("### 1. Audit and remove unstated frame mandates (27 tasks)")
    out.append("")
    out.append("Review every verifier flagged FRAME-OVERSPEC. For each:")
    out.append("- Re-read the prompt's thorough description.")
    out.append("- If the prompt doesn't mention a Figma frame as a design element, remove")
    out.append("  `LayerInsideFrame(...)` and replace `AllLayerBoundsInside(outer_type=\"frame\", ...)` with")
    out.append("  either no containment check or a permissive equivalent.")
    out.append("- If the prompt does mention a frame implicitly (e.g. 'in a 200×200 canvas')")
    out.append("  but not as a Figma frame primitive, decide whether the verifier should be")
    out.append("  flexible about page-level vs frame-level containment.")
    out.append("")
    out.append("### 2. Calibrate sub-15 px alignment tolerances (24 tasks)")
    out.append("")
    out.append("Find every `Layers*` check with `tolerance < 15` and increase to 25–35 px,")
    out.append("unless the prompt explicitly says 'pixel-perfect' or 'exactly centered'.")
    out.append("Combined with the critical-halving rule in")
    out.append("`apps/figma/verifier/rubrics/_base.py:36`, a single sub-15 px miss collapses")
    out.append("the entire alignment rubric to 50% × (pass_count / total).")
    out.append("")
    out.append("### 3. Audit the 3 EFFECT-OVERSPEC tasks")
    out.append("")
    out.append("Tasks where the verifier checks for drop shadows the prompt never requested:")
    for t in audit:
        for i in t["issues"]:
            if i["type"] == "EFFECT-OVERSPEC":
                out.append(f"- `{t['task_id']}`")
                break
    out.append("")
    out.append("Decide: is the shadow check intentional (\"bonus credit\") or a mistake? If")
    out.append("intentional, document it. If a mistake, remove the EffectRubric.")
    out.append("")
    out.append("### 4. Resolve narrow size/color over-specifications")
    out.append("")
    out.append("- `SIZE-OVERSPEC` (2 tasks): verifier asks for exact pixel dimensions the")
    out.append("  prompt never gave. Remove the LayerSizeEquals or replace with a permissive")
    out.append("  size range.")
    out.append("- `COLOR-OVERSPEC` (1 task): verifier asks for a specific RGB the prompt")
    out.append("  doesn't name. Replace with LayersAllSameColor or a fill-type check.")
    out.append("")
    out.append("---")
    out.append("")
    out.append("Per [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md), this audit only reports;")
    out.append("it does not patch `delivery-1/task_NN/verifier.py` files. Authorize specific")
    out.append("patches as a follow-up if you want them applied.")
    out.append("")

    doc_path = Path("VERIFIER_CORRECTNESS_AUDIT.md")
    doc_path.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {doc_path} ({doc_path.stat().st_size:,} bytes, {len(out)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

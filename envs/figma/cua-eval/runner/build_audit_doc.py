"""Build VERIFIER_AUDIT.md from audit_data.json.

Run after audit_verifiers.py.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/build_audit_doc.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


def fmt_score(x: float | None) -> str:
    if x is None:
        return "—"
    return f"{x:.3f}"


def main() -> int:
    audit_path = Path("audit_data.json")
    if not audit_path.is_file():
        print("ERROR: run audit_verifiers.py first", file=__import__("sys").stderr)
        return 1
    audit = json.load(audit_path.open())

    n_tasks = len(audit)
    verdicts = Counter(t.get("verdict", "?") for t in audit)
    n_frame = sum(1 for t in audit if t.get("frame_required"))
    n_brittle = sum(1 for t in audit if t.get("brittle_alignment_tolerance"))
    n_plateau = sum(1 for t in audit if t.get("rollout", {}).get("plateau"))
    n_pass = sum(1 for t in audit if (t.get("rollout", {}).get("n_pass") or 0) > 0)

    # Categorize tasks by verdict for the per-task sections
    by_verdict: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for t in audit:
        by_verdict[t.get("verdict", "?")].append(t)
    for k in by_verdict:
        by_verdict[k].sort(key=lambda x: -(x.get("rollout", {}).get("best") or 0))

    today = datetime.now().strftime("%B %d, %Y")

    lines: list[str] = []
    lines.append("# Verifier Audit — figma-50 vs. Qwen3.5-27B rollouts")
    lines.append("")
    lines.append(f"_Generated {today} from `audit_data.json` ({audit_path.stat().st_size:,} bytes)._")
    lines.append("")
    lines.append("This audit cross-references all 50 task verifiers in `delivery-1/` against the")
    lines.append("merged 150-attempt rollout (parent + 3 fill-ins). For each task it inspects:")
    lines.append("- the verifier's rubrics, weights, critical checks, and tolerance values (statically)")
    lines.append("- the 3 rollout attempts' scores, plateau pattern, stop reasons, and per-rubric breakdown")
    lines.append("- the actual scene-graph + semantic events from a representative log.json")
    lines.append("")
    lines.append("Each task gets a single-word verdict that distinguishes verifier issues from model issues:")
    lines.append("")
    lines.append("| Verdict | Meaning |")
    lines.append("|---|---|")
    lines.append("| `passing` | Task already passes (best ≥ 0.7) |")
    lines.append("| `verifier-primary` | **Verifier IS the bottleneck.** Estimated post-verifier-fix score ≥ 0.7. Fixing the verifier would unlock this task. |")
    lines.append("| `model-primary` | Verifier has issues but model is the bigger blocker. Verifier fix lifts the score but still < 0.7. |")
    lines.append("| `honest` | No verifier-fixable lift available. Low score reflects model capability. |")
    lines.append("| `mock-gap` | Hard zero: agent attempted the required tool but the mock didn't log the shape. |")
    lines.append("| `model-gap` | Hard zero: agent never attempted the required tool. |")
    lines.append("")
    lines.append("Verdicts use a `compute_verdict()` heuristic that simulates removing the two")
    lines.append("biggest verifier brittleness sources (frame-mandate + critical-halving) and re-scores.")
    lines.append("Tasks where the simulated score crosses 0.7 are `verifier-primary`. Tasks where the")
    lines.append("lift is real but doesn't reach 0.7 are `model-primary` — the verifier compounds the")
    lines.append("gap, but the model can't fully close it either way.")
    lines.append("")

    # Headline
    lines.append("## Headline")
    lines.append("")
    lines.append(f"| Metric | Value |")
    lines.append(f"|---|---|")
    lines.append(f"| Tasks audited | **{n_tasks}/50** |")
    lines.append(f"| Tasks passing (≥0.7) | {n_pass} |")
    lines.append(f"| Plateau tasks (range < 0.05 across 3 attempts) | **{n_plateau}** ({n_plateau*100//n_tasks}%) |")
    lines.append(f"| Verifiers requiring a frame | **{n_frame}** ({n_frame*100//n_tasks}%) |")
    lines.append(f"| Verifiers with alignment tolerance < 15 px | **{n_brittle}** ({n_brittle*100//n_tasks}%) |")
    lines.append("")
    lines.append(f"**Verdict distribution:**")
    lines.append("")
    for v, n in verdicts.most_common():
        lines.append(f"- `{v}`: **{n}** tasks")
    lines.append("")

    # Aggregate gap categories
    lines.append("## Aggregate gap categories")
    lines.append("")

    lines.append("### Gap 1 — Frame mandated by verifier but not by prompt")
    lines.append("")
    lines.append(f"**{n_frame}/{n_tasks} verifiers** include either `LayerInsideFrame(...)` or")
    lines.append("`AllLayerBoundsInside(outer_type=\"frame\")`. The model rarely creates an explicit")
    lines.append("frame element (it draws shapes directly on the canvas), so this check fails on")
    lines.append("nearly every attempt. The cost is ~10% of the rubric weight per affected task.")
    lines.append("")
    lines.append("Tasks where the verifier IS the primary blocker (verdict=`verifier-primary`):")
    lines.append("")
    frame_gap_tasks = [t for t in audit if t.get("verdict") in ("verifier-primary", "model-primary") and t.get("frame_required")]
    for t in frame_gap_tasks[:20]:
        lines.append(f"- `{t['task_id']}` (best={t['rollout']['best']:.3f})")
    if len(frame_gap_tasks) > 20:
        lines.append(f"- _...and {len(frame_gap_tasks)-20} more_")
    lines.append("")

    lines.append("### Gap 2 — Brittle alignment tolerances (< 15 px)")
    lines.append("")
    lines.append(f"**{n_brittle}/{n_tasks} verifiers** use a sub-15px alignment tolerance.")
    lines.append("Typical agent drag-creation lands ±20-30px off perfect alignment. Combined with")
    lines.append("the critical-halving rule in `verifier/rubrics/_base.py:36`, a single off-center")
    lines.append("rectangle collapses the entire alignment rubric to 50% × (pass_count/total).")
    lines.append("")
    lines.append("Verbatim from `verifier/rubrics/_base.py:36`:")
    lines.append("```python")
    lines.append('if any(i < len(results) and not results[i].passed for i in self.critical):')
    lines.append('    score *= 0.5')
    lines.append("```")
    lines.append("")

    lines.append("### Gap 3 — All-or-nothing effect rubrics")
    lines.append("")
    lines.append("Effect-heavy tasks like task_27 (`EffectRubric`: 4 checks for drop-shadow")
    lines.append("count + opposing offsets) score 0/0.2 every time because the model never opens")
    lines.append("the effects panel. With no partial credit for \"shadow exists,\" the rubric is")
    lines.append("an information-free hard zero.")
    lines.append("")

    lines.append("### Gap 4 — Hard zeros from missing shape types")
    lines.append("")
    lines.append("Tasks scoring exactly 0.000 across all 3 attempts where the verifier requires")
    lines.append("a shape type the mock never logged or the agent never attempted:")
    lines.append("")
    zero_tasks = [t for t in audit if (t.get("rollout", {}).get("best") or 0) == 0]
    for t in zero_tasks:
        observed = list((t.get("log_scan", {}).get("shape_types_in_outcomes") or {}).keys())
        required = list((t.get("required_shape_types") or {}).keys())
        missing = [r for r in required if r not in observed]
        lines.append(f"- `{t['task_id']}` — verdict=`{t['verdict']}`, required: {required}, missing: {missing}")
    lines.append("")

    lines.append("### Gap 5 — Plateau scores reveal deterministic failure modes")
    lines.append("")
    lines.append(f"**{n_plateau}/{n_tasks} tasks scored within 0.05 across all 3 attempts.** This")
    lines.append("means k=3 retries are not unlocking variance — the model lands on the same")
    lines.append("partial solution every time, and the verifier locks that solution at a fixed")
    lines.append("sub-threshold score. k>3 retries would NOT improve these tasks.")
    lines.append("")

    # Per-task tables, organized by verdict
    lines.append("## Per-task verdicts")
    lines.append("")
    lines.append("All 50 tasks, grouped by verdict and sorted by best score.")
    lines.append("")

    for verdict_label, header in [
        ("verifier-primary", "🔧 Verifier-primary tasks ({}) — fixing the verifier would push past 0.7"),
        ("model-primary", "🤖 Model-primary tasks ({}) — verifier issues exist but model is the bigger blocker"),
        ("honest", "= Honest scoring tasks ({}) — no verifier-fixable lift, score reflects model"),
        ("passing", "✓ Passing tasks ({})"),
        ("model-gap", "0️⃣ Hard zero (model-gap) ({}) — agent never tried required tool"),
        ("mock-gap", "🪵 Hard zero (mock-gap) ({}) — mock didn't log the shape type"),
    ]:
        tasks = by_verdict.get(verdict_label, [])
        if not tasks:
            continue
        lines.append(f"### {header.format(len(tasks))}")
        lines.append("")
        lines.append("| Task | Best | Mean | Plateau | Frame req | Brittle align | Top reason |")
        lines.append("|---|---|---|---|---|---|---|")
        for t in tasks:
            rollout = t.get("rollout", {})
            best = fmt_score(rollout.get("best"))
            mean = fmt_score(rollout.get("mean"))
            plateau = "yes" if rollout.get("plateau") else "—"
            frame = "yes" if t.get("frame_required") else "—"
            brittle = "yes" if t.get("brittle_alignment_tolerance") else "—"
            reason = (t.get("verdict_reasons") or ["—"])[0]
            reason = reason.replace("|", "\\|")
            if len(reason) > 80:
                reason = reason[:77] + "..."
            lines.append(f"| `{t['task_id']}` | {best} | {mean} | {plateau} | {frame} | {brittle} | {reason} |")
        lines.append("")

    # Detailed plateau analysis
    lines.append("## Plateau math (top 10)")
    lines.append("")
    lines.append("Tasks where all 3 attempts produced near-identical scores. The plateau score")
    lines.append("equals the sum of rubric × weight × (pass_count/total) [× 0.5 if any critical")
    lines.append("check fails in that rubric]:")
    lines.append("")
    plats = [t for t in audit if t.get("rollout", {}).get("plateau") and (t.get("rollout", {}).get("best") or 0) > 0]
    plats.sort(key=lambda t: -(t.get("rollout", {}).get("best") or 0))
    for t in plats[:10]:
        rollout = t.get("rollout", {})
        breakdown = t.get("score_breakdown") or {}
        rubrics = breakdown.get("rubrics") or []
        lines.append(f"### `{t['task_id']}` — plateau at {rollout['best']:.3f} × 3 attempts")
        lines.append("")
        if rubrics:
            for r in rubrics:
                lines.append(f"- **{r['name']}**: {r['score']:.3f}/{r['max_score']:.3f} "
                             f"({r['n_pass']}/{r['n_checks']} checks pass)")
                for msg in (r.get("fail_messages") or [])[:2]:
                    short = (msg or "").strip().replace("\n", " ")[:140]
                    lines.append(f"  - fail: `{short}`")
        if t.get("verdict_reasons"):
            lines.append(f"- _verdict_: **{t['verdict']}** — {'; '.join(t['verdict_reasons'])}")
        lines.append("")

    # Ranked fix candidates
    lines.append("## Top fix candidates")
    lines.append("")
    lines.append("Ranked by estimated score lift × number of tasks affected. Patches are")
    lines.append("scoped to verifier or mock files only (no agent-side changes).")
    lines.append("")
    lines.append("### #1 — Remove or relax frame mandate (38 tasks affected)")
    lines.append("")
    lines.append("Audit which tasks' prompts actually require a frame. For those that don't,")
    lines.append("replace `AllLayerBoundsInside(outer_type=\"frame\")` and `LayerInsideFrame(...)`")
    lines.append("with optional checks (e.g. score 0 if not present but don't halve the rubric)")
    lines.append("or remove entirely.")
    lines.append("")
    lines.append(f"_Estimated lift_: ~0.10 per task on best score × {n_frame} tasks affected.")
    lines.append("")
    lines.append("### #2 — Raise sub-15px alignment tolerances (24 tasks affected)")
    lines.append("")
    lines.append("Increase `LayersAligned(..., tolerance=...)` and `LayersConcentric(...)` from")
    lines.append("12-15 px to 25-30 px on non-prompt-critical alignment. Keep strict tolerances")
    lines.append("only when the prompt explicitly says \"perfectly centered\" or equivalent.")
    lines.append("")
    lines.append(f"_Estimated lift_: ~0.05-0.15 per task × {n_brittle} tasks affected.")
    lines.append("")
    lines.append("### #3 — Add effect partial credit (task_27 + others)")
    lines.append("")
    lines.append("In `EffectRubric` for tasks like task_27, replace the 4 all-or-nothing checks")
    lines.append("with graded credit: 0.025 for \"any drop shadow exists,\" 0.025 for \"≥ 2 shadows,\"")
    lines.append("0.025 for \"shadows oppose,\" 0.025 for \"shadows pair on offset.\" That way the")
    lines.append("rubric can score 0.025-0.100 instead of locked at 0.0.")
    lines.append("")
    lines.append("### #4 — Resolve hard-zero shape-type gaps (3 tasks)")
    lines.append("")
    lines.append("For the 3 tasks scoring exact 0.0 across all attempts:")
    for t in zero_tasks:
        lines.append(f"- `{t['task_id']}` — verdict=`{t['verdict']}`")
    lines.append("")
    lines.append("Action depends on verdict:")
    lines.append("- `model-gap` → real CUA capability gap; no harness change needed")
    lines.append("- `mock-gap` → fix mock to log the missing shape type; expect score lift")
    lines.append("")

    lines.append("## Methodology notes")
    lines.append("")
    lines.append("- Verifier introspection uses Python's standard `dataclasses.asdict` on each")
    lines.append("  check instance. Each check's class name + parameter dict is captured.")
    lines.append("- `frame_required` is True iff any check is `LayerInsideFrame` or")
    lines.append("  `AllLayerBoundsInside(outer_type=\"frame\")`.")
    lines.append("- `brittle_alignment_tolerance` is True iff any `Layers*` check has tolerance < 15.")
    lines.append("- Rollout aggregation reads `merged_attempts.json` (the cross-run dedup).")
    lines.append("- Log scan walks `outcome.document.pages[].children` recursively across all 4 runs.")
    lines.append("- Verdict heuristic in `audit_verifiers.py:compute_verdict()`.")
    lines.append("")
    lines.append("Per [apps/figma/CLAUDE.md](apps/figma/CLAUDE.md), this audit does **not** modify any")
    lines.append("`delivery-1/task_NN/verifier.py` or `prompt.md` files. Authorize specific patches")
    lines.append("via follow-up if you want them applied.")
    lines.append("")

    out = Path("VERIFIER_AUDIT.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out} ({out.stat().st_size:,} bytes, {len(lines)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

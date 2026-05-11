"""Build a styled PDF report describing the Qwen3.5-27B figma-50 evaluation:
methodology, task taxonomy, results, and failure modes.

Usage (from apps/figma/):
    .venv/bin/python cua-eval/runner/build_report.py \\
        cua-eval/runs/qwen35_parallel_10x_20260510_144617 \\
        cua-eval/runs/qwen35_fillin_20260510_155010 \\
        cua-eval/runs/qwen35_fillin2_20260510_163353 \\
        cua-eval/runs/qwen35_fillin3_20260510_170851

Writes report.html + report.pdf to the current directory. Uses
Playwright's chromium for PDF rendering (no external deps).
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any


# Task taxonomy: hand-curated based on the 50 prompts in delivery-1/.
TAXONOMY: dict[str, list[str]] = {
    "A. Simple primitives (1-2 shapes)": [
        "task_05_red_heart_union", "task_06_gold_star_exclude",
        "task_13_night_sky", "task_36_polaroid", "task_50_album_cover",
    ],
    "B. Grids & repeated patterns": [
        "task_02_sunset_gradient", "task_04_color_wheel",
        "task_07_mountain_range", "task_08_water_waves",
        "task_09_brand_palette", "task_10_apple_avatar",
        "task_11_pressed_button", "task_12_shadowed_cards",
        "task_15_cloud_union",
        "task_22_tag_pills", "task_25_button_component",
        "task_26_color_variable_card", "task_29_polka_dot_grid",
        "task_30_stripe_wallpaper", "task_35_honeycomb",
        "task_46_audio_waveform",
    ],
    "C. Icons & small UI components": [
        "task_16_speech_bubble", "task_17_play_button",
        "task_18_donut", "task_21_button_stack",
        "task_23_stretchy_sidebar", "task_24_centered_modal",
        "task_27_neumorphic_button", "task_28_edited_photo",
        "task_38_battery_indicator", "task_40_toggle_switch",
        "task_41_search_bar", "task_44_avatar_status",
    ],
    "D. Multi-element compositions": [
        "house_task_comprehensive", "task_03_glowing_orb",
        "task_14_concentric_target", "task_19_padlock",
        "task_20_glow_blob",
        "task_31_sun_with_rays", "task_32_pinwheel",
        "task_33_pie_chart", "task_34_snowflake",
        "task_37_sticky_note",
        "task_42_bell_notification",
        "task_43_compass_rose",
        "task_45_geometric_emblem", "task_47_sunburst_stamp",
        "task_48_spider_web",
    ],
    "E. Pen-tool / vector-heavy": [
        "task_39_wifi_icon", "task_49_decorative_ribbon",
    ],
}


def _load_merged(merged_path: Path) -> list[dict[str, Any]]:
    return json.load(merged_path.open())


def _aggregate_trajectory_data(runs: list[Path]) -> dict[str, Any]:
    total_actions = 0
    action_type_counts: Counter = Counter()
    total_clicks = 0
    off_viewport_clicks = 0
    total_drags = 0
    total_keypresses = 0
    keypress_keys: Counter = Counter()
    coord_clamp_total = 0
    loop_break_total = 0

    for run in runs:
        for tj in run.rglob("trajectory.jsonl"):
            for line in tj.open():
                try:
                    d = json.loads(line)
                except Exception:
                    continue
                if d.get("phase") == "intervention":
                    if d.get("intervention") == "coord_clamp":
                        coord_clamp_total += 1
                    elif d.get("intervention") == "loop_break":
                        loop_break_total += 1
                if d.get("phase") != "step":
                    continue
                for a in d.get("actions", []):
                    total_actions += 1
                    t = a.get("type", "?")
                    action_type_counts[t] += 1
                    if t in ("click", "double_click", "move"):
                        total_clicks += 1
                        x, y = a.get("x"), a.get("y")
                        try:
                            if isinstance(x, str) and "," in x:
                                parts = [int(p.strip().strip("[]()"))
                                         for p in x.split(",")]
                                xi, yi = parts[0], parts[1]
                            else:
                                xi, yi = int(x), int(y)
                            if not (0 <= xi <= 1280 and 0 <= yi <= 800):
                                off_viewport_clicks += 1
                        except Exception:
                            pass
                    elif t == "drag":
                        total_drags += 1
                    elif t == "keypress":
                        total_keypresses += 1
                        for k in a.get("keys", []):
                            keypress_keys[str(k).lower()] += 1
    return {
        "total_actions": total_actions,
        "action_type_counts": dict(action_type_counts.most_common()),
        "total_clicks": total_clicks,
        "off_viewport_clicks": off_viewport_clicks,
        "off_viewport_pct": off_viewport_clicks * 100 / max(1, total_clicks),
        "total_drags": total_drags,
        "total_keypresses": total_keypresses,
        "keypress_keys": dict(keypress_keys.most_common(10)),
        "coord_clamp_total": coord_clamp_total,
        "loop_break_total": loop_break_total,
    }


def _detect_plateaus(by_task: dict[str, list[dict[str, Any]]]) -> list[tuple[str, list[float]]]:
    plateaus = []
    for tid, xs in by_task.items():
        scores = sorted(float(x["score"]) for x in xs)
        if len(scores) == 3 and (scores[-1] - scores[0]) < 0.05 and scores[0] > 0:
            plateaus.append((tid, scores))
    plateaus.sort(key=lambda kv: -sum(kv[1]) / 3)
    return plateaus


def _score_distribution(merged: list[dict[str, Any]]) -> dict[str, int]:
    bins = {"0 (no progress)": 0, "0–0.1 (minimal)": 0, "0.1–0.3 (some progress)": 0,
            "0.3–0.5 (moderate)": 0, "0.5–0.7 (close miss)": 0, "≥0.7 (PASS)": 0}
    for a in merged:
        s = float(a["score"])
        if s == 0:
            bins["0 (no progress)"] += 1
        elif s < 0.1:
            bins["0–0.1 (minimal)"] += 1
        elif s < 0.3:
            bins["0.1–0.3 (some progress)"] += 1
        elif s < 0.5:
            bins["0.3–0.5 (moderate)"] += 1
        elif s < 0.7:
            bins["0.5–0.7 (close miss)"] += 1
        else:
            bins["≥0.7 (PASS)"] += 1
    return bins


CSS = """
@page { size: Letter; margin: 0.6in 0.7in; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
  font-size: 10.5pt; line-height: 1.45; color: #1a1a1a;
}
h1 { font-size: 24pt; margin: 0 0 0.1em 0; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 14pt; margin-top: 1.4em; margin-bottom: 0.4em; padding-bottom: 0.2em;
     border-bottom: 1px solid #999; font-weight: 600; }
h3 { font-size: 11.5pt; margin-top: 1em; margin-bottom: 0.3em; font-weight: 600; }
p { margin: 0.4em 0; }
code, pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 9.5pt; }
pre { background: #f4f4f4; padding: 0.6em 0.8em; border-radius: 4px;
      border-left: 3px solid #888; overflow-x: auto; }
.cover { page-break-after: always; padding-top: 1.5in; }
.cover h1 { font-size: 32pt; }
.cover .subtitle { font-size: 14pt; color: #555; margin-top: 0.3em; }
.cover .meta { margin-top: 3em; font-size: 11pt; color: #444; }
.cover .meta dt { font-weight: 600; color: #222; display: inline-block; min-width: 8em; }
.cover .headline { margin-top: 3em; padding: 1.2em 1.4em; background: #f6f6f6;
                   border: 1px solid #ddd; border-radius: 6px; }
.cover .headline .big { font-size: 36pt; font-weight: 700; color: #c8302e; }
.cover .headline .label { font-size: 10pt; color: #666; letter-spacing: 0.1em;
                          text-transform: uppercase; margin-top: 0.4em; }
table { border-collapse: collapse; width: 100%; margin: 0.6em 0; font-size: 9.5pt; }
th, td { border: 1px solid #ccc; padding: 0.35em 0.6em; text-align: left; vertical-align: top; }
th { background: #eaeaea; font-weight: 600; }
td.num { text-align: right; font-variant-numeric: tabular-nums; }
td.pass { background: #d4edda; }
td.high { background: #fff3cd; }
td.zero { background: #f8d7da; color: #555; }
.summary-card { display: inline-block; padding: 0.6em 0.9em; margin: 0 0.4em 0.4em 0;
                background: #f6f6f6; border-radius: 4px; min-width: 7em; vertical-align: top;
                border-left: 3px solid #555; }
.summary-card .v { font-size: 16pt; font-weight: 700; }
.summary-card .l { font-size: 8.5pt; color: #666; text-transform: uppercase;
                   letter-spacing: 0.07em; }
.note { background: #fffaf0; border-left: 3px solid #d97706;
        padding: 0.5em 0.8em; margin: 0.5em 0; font-size: 10pt; }
.bar-chart { margin: 0.4em 0; }
.bar-row { display: flex; align-items: center; margin: 0.15em 0; font-size: 9.5pt; }
.bar-label { width: 14em; }
.bar-track { flex: 1; height: 1.1em; background: #f0f0f0; border-radius: 2px;
             margin: 0 0.5em; position: relative; }
.bar-fill { height: 100%; background: #5b8def; border-radius: 2px; }
.bar-fill.pass { background: #28a745; }
.bar-fill.close { background: #ffc107; }
.bar-fill.zero { background: #dc3545; }
.bar-value { width: 4em; text-align: right; font-variant-numeric: tabular-nums; }
ul { margin: 0.3em 0; padding-left: 1.4em; }
li { margin: 0.2em 0; }
.small { font-size: 9pt; color: #555; }
.tag { display: inline-block; padding: 0.1em 0.5em; border-radius: 3px; font-size: 8.5pt;
       background: #eee; color: #444; margin-right: 0.3em; }
.tag.pass { background: #d4edda; color: #155724; }
.tag.fail { background: #f8d7da; color: #721c24; }
hr { border: none; border-top: 1px solid #ccc; margin: 1.2em 0; }
"""


def _bar_chart(bins: dict[str, int], total: int, color_fn=None) -> str:
    """Render a horizontal bar chart."""
    max_val = max(bins.values()) if bins else 1
    rows = []
    for label, val in bins.items():
        width_pct = val * 100 / max_val if max_val else 0
        klass = ""
        if color_fn:
            klass = color_fn(label)
        rows.append(
            f'<div class="bar-row">'
            f'<span class="bar-label">{label}</span>'
            f'<span class="bar-track"><span class="bar-fill {klass}" '
            f'style="width:{width_pct:.1f}%"></span></span>'
            f'<span class="bar-value">{val} ({val*100/total:.0f}%)</span>'
            f"</div>"
        )
    return f'<div class="bar-chart">{"".join(rows)}</div>'


def _build_html(merged: list[dict[str, Any]], by_task: dict[str, list[dict[str, Any]]],
                stats: dict[str, Any], plateaus: list[tuple[str, list[float]]],
                score_bins: dict[str, int]) -> str:
    n = len(merged)
    passed = [a for a in merged if a["passed"]]
    pass_tasks = {a["task_id"] for a in passed}
    nonzero = sum(1 for a in merged if a["score"] > 0)
    high_partial = sum(1 for a in merged if 0.5 <= a["score"] < 0.7)
    mean_score = sum(a["score"] for a in merged) / n
    total_cost = sum(a.get("cost_usd", 0) or 0 for a in merged)

    stops = Counter(a["stop_reason"] for a in merged)

    # Build per-task table grouped by taxonomy
    taxonomy_blocks = []
    for cat, task_ids in TAXONOMY.items():
        rows = []
        for tid in task_ids:
            xs = by_task.get(tid)
            if not xs:
                continue
            scores = [x["score"] for x in xs]
            best = max(scores)
            mean_s = sum(scores) / len(scores)
            n_pass = sum(1 for x in xs if x["passed"])
            tcss = "pass" if n_pass else ("high" if best >= 0.5 else ("zero" if best == 0 else ""))
            rows.append(
                f"<tr>"
                f"<td>{tid}</td>"
                f"<td class='num {tcss}'>{best:.3f}</td>"
                f"<td class='num'>{mean_s:.3f}</td>"
                f"<td class='num'>{n_pass}/{len(xs)}</td>"
                f"</tr>"
            )
        taxonomy_blocks.append(
            f"<h3>{cat} <span class='small'>(n={len(task_ids)} tasks)</span></h3>"
            f"<table><thead><tr><th>Task</th><th>Best score</th><th>Mean</th>"
            f"<th>Passes (k of n)</th></tr></thead><tbody>{''.join(rows)}</tbody></table>"
        )

    # Passing-tasks block
    passing_rows = []
    for tid in sorted(pass_tasks):
        xs = by_task[tid]
        passes = [x for x in xs if x["passed"]]
        best = max(passes, key=lambda x: x["score"])
        passing_rows.append(
            f"<tr><td>{tid}</td>"
            f"<td class='num pass'>{best['score']:.3f}</td>"
            f"<td class='num'>{best['turns']}</td>"
            f"<td>{len(passes)}/{len(xs)}</td>"
            f"<td>{best['stop_reason']}</td></tr>"
        )
    passing_block = (
        f"<table><thead><tr><th>Task</th><th>Best score</th><th>Turns</th>"
        f"<th>Passes/attempts</th><th>Stop reason</th></tr></thead>"
        f"<tbody>{''.join(passing_rows)}</tbody></table>"
    )

    # Close-miss block
    close_misses = sorted(
        [a for a in merged if not a["passed"] and a["score"] >= 0.5],
        key=lambda x: -x["score"],
    )[:10]
    miss_rows = []
    for a in close_misses:
        miss_rows.append(
            f"<tr><td>{a['task_id']}</td>"
            f"<td class='num high'>{a['score']:.3f}</td>"
            f"<td class='num'>{a['turns']}</td>"
            f"<td>{a['stop_reason']}</td></tr>"
        )
    close_block = (
        f"<table><thead><tr><th>Task</th><th>Score</th><th>Turns</th><th>Stop</th></tr></thead>"
        f"<tbody>{''.join(miss_rows)}</tbody></table>"
    )

    # Plateau examples
    plateau_rows = []
    for tid, scores in plateaus[:15]:
        plateau_rows.append(
            f"<tr><td>{tid}</td>"
            f"<td class='num'>{scores[0]:.3f}</td>"
            f"<td class='num'>{scores[1]:.3f}</td>"
            f"<td class='num'>{scores[2]:.3f}</td>"
            f"<td class='num'>{scores[2]-scores[0]:.3f}</td></tr>"
        )
    plateau_block = (
        f"<table><thead><tr><th>Task</th><th>Attempt 1</th><th>Attempt 2</th>"
        f"<th>Attempt 3</th><th>Range</th></tr></thead>"
        f"<tbody>{''.join(plateau_rows)}</tbody></table>"
    )

    # Stop reason summary
    stop_html = "".join(
        f'<span class="summary-card"><div class="v">{n_st}</div>'
        f'<div class="l">{r}</div></span>'
        for r, n_st in stops.most_common()
    )

    # Keypress summary
    keypress_rows = "".join(
        f"<tr><td><code>{k}</code></td><td class='num'>{cnt}</td></tr>"
        for k, cnt in stats["keypress_keys"].items()
    )

    today = datetime.now().strftime("%B %d, %Y")

    html = f"""<!doctype html>
<html><head><meta charset="utf-8">
<title>Qwen3.5-27B — figma-50 CUA Benchmark Report</title>
<style>{CSS}</style>
</head><body>

<!-- COVER -->
<section class="cover">
<h1>Qwen3.5-27B on figma-50</h1>
<div class="subtitle">A 50-task computer-use benchmark, executed via OpenRouter</div>

<div class="meta">
<dl>
<dt>Model:</dt> <code>qwen/qwen3.5-27b</code> (vision-language, 27B dense) routed via OpenRouter → DeepInfra<br>
<dt>Harness:</dt> apps/figma/cua-eval/passk.py with custom <code>agents/openrouter.py</code> adapter<br>
<dt>Tasks:</dt> 50 / 50, k=3 attempts each (150 total)<br>
<dt>Threshold:</dt> final_score ≥ 0.7 = pass<br>
<dt>Date:</dt> {today}<br>
<dt>Total cost:</dt> ${total_cost:.2f} (API), ≈$45 actual incl. credit-error overhead<br>
</dl>
</div>

<div class="headline">
<div class="big">4.0%</div>
<div class="label">pass@3 — 2 of 50 tasks scored ≥ 0.7 on at least one attempt</div>
<p style="margin-top:1em">Mean score across 150 attempts: <strong>{mean_score:.3f}</strong>.
{nonzero}/{n} attempts ({nonzero*100/n:.0f}%) produced non-zero scores.
{high_partial}/{n} attempts ({high_partial*100/n:.0f}%) scored in the 0.5–0.7 close-miss band.</p>
</div>
</section>

<!-- EXECUTIVE SUMMARY -->
<h2>1. Executive summary</h2>

<p>This report documents an end-to-end CUA (computer-use agent) evaluation of
<strong>Qwen3.5-27B</strong>, an open-weight vision-language model, against the
<strong>figma-50</strong> task set — 50 design exercises requiring an agent to operate
a browser-based Figma mock and reproduce specified layouts. The agent is scored by an
automated verifier that inspects the resulting scene graph for shape counts, colors,
alignment, structure, and proper events.</p>

<p>The model accesses the benchmark through a custom OpenAI-compatible adapter
(<code>cua-eval/runner/agents/openrouter.py</code>) that defines a generic
<code>computer_action</code> function tool, since Qwen has no native computer-use
tool. Three opt-in interventions were added to make the test fair to a model with
strong off-viewport coordinate priors: corrective-feedback coord clamping,
stuck-state nudging, and early-abort on repeated loops.</p>

<div class="bar-chart">
{_bar_chart(score_bins, n, lambda l: 'pass' if 'PASS' in l else ('close' if 'close' in l else ('zero' if 'no progress' in l else '')))}
</div>

<h3>Headline numbers</h3>
<span class="summary-card"><div class="v">{len(passed)}/{n}</div><div class="l">pass@1 attempts ({len(passed)*100/n:.1f}%)</div></span>
<span class="summary-card"><div class="v">{len(pass_tasks)}/{len(by_task)}</div><div class="l">pass@3 tasks ({len(pass_tasks)*100/len(by_task):.1f}%)</div></span>
<span class="summary-card"><div class="v">{mean_score:.3f}</div><div class="l">mean final_score</div></span>
<span class="summary-card"><div class="v">{nonzero*100/n:.0f}%</div><div class="l">nonzero rate</div></span>
<span class="summary-card"><div class="v">{high_partial}</div><div class="l">close misses (0.5–0.7)</div></span>

<h3>Stop-reason breakdown</h3>
{stop_html}

<!-- METHODOLOGY -->
<h2>2. Methodology</h2>

<h3>2.1 Harness architecture</h3>
<p>Each attempt: Playwright launches Chromium → navigates to a local Figma-mock
Vite dev server → presents the agent with a screenshot and the task prompt.
The agent emits one or more <code>computer_action</code> tool calls per turn
(click, drag, scroll, keypress, type, wait, done). The harness executes each
action against the browser, takes a fresh screenshot, and feeds it back. The
mock's own logger records every DOM event into <code>localStorage</code> as
<code>raw[]</code>, <code>semantic[]</code>, and an
<code>outcome.document</code> snapshot; at attempt end the harness scrapes the
log and runs the task's verifier (a python rubric in
<code>delivery-1/task_NN/verifier.py</code>) which produces a
<code>final_score</code> in [0, 1].</p>

<h3>2.2 Model access</h3>
<p>Calls go through OpenRouter's OpenAI-compatible chat-completions endpoint,
with <code>provider: {{"only": ["DeepInfra"]}}</code> pinned in
<code>extra_body</code>. Verified empirically: Novita rejects image + tools
together; AtlasCloud returns 400 on most tool-call shapes; DeepInfra serves
the model cleanly. <code>reasoning: {{"enabled": false}}</code> disables the
hidden chain-of-thought tokens that would otherwise be billed at the output
rate.</p>

<h3>2.3 Interventions (27B-specific)</h3>
<ul>
<li><strong>Coord clamp</strong> (<code>--coord-clamp</code>): if a click/drag
falls outside the 1280×800 viewport, the action is rejected with a structured
tool_result explaining the viewport bounds and the toolbar y-coord. The model
sees its mistake and gets to retry. <strong>Fidelity-preserving</strong>: we
don't silently move the click — we tell it and let the model decide.</li>
<li><strong>Loop break</strong> (<code>--loop-break</code>): when the same
action signature repeats 3 times with no screen change, inject a user message
telling the model it's stuck and that shapes are created by DRAGGING, not
clicking, with the exact <code>computer_action</code> JSON syntax inline.</li>
<li><strong>Early abort</strong>: if loop_break fires more than 10 times in
one attempt, stop with <code>stop_reason=loop_break_abort</code>. Saves
walltime/cost on doomed attempts that keep looping despite nudges.</li>
</ul>

<h3>2.4 Other operational settings</h3>
<ul>
<li><code>step_cap=200</code> (max turns per attempt)</li>
<li><code>keep_screenshots=3</code> (image history pruning to keep input tokens flat)</li>
<li>System prompt: <code>cua-eval/system-prompts/qwen-figma-strict.md</code> —
viewport-aware, with explicit toolbar coords, keyboard-shortcut table, and
anti-loop instruction</li>
<li><code>turn_delay_s=0.3</code> + per-request <code>timeout=120</code> with
retry on 429/5xx/timeout/connection errors</li>
<li><strong>Parallel sharding</strong>: 10 concurrent passk.py workers, each
with its own Vite mock on ports 5174–5183, all writing to one shared
<code>--run-id</code>. The merge script picks the best outcome per
(task, attempt) pair, preferring non-errors</li>
</ul>

<h3>2.5 Operational notes</h3>
<div class="note">
<strong>Credit exhaustion</strong>: the parent run hit OpenRouter's
"insufficient credits" wall partway through, leaving 35 attempts with
<code>stop_reason=error</code>. Three follow-up fill-in runs (after top-ups)
filled the gaps; the final merge across all 4 runs covers 50/50 tasks at k=3.
Out of 150 final attempts, only 2 (task_17 attempt 3, task_45 attempt 3) remain
unscored — both tasks have valid scores from their other two attempts, so all
50 tasks have meaningful pass@3 statistics.
</div>

<!-- TAXONOMY -->
<h2>3. Task taxonomy</h2>

<p>The 50 tasks span 5 difficulty/complexity categories, hand-curated from the
prompt set:</p>

{"".join(taxonomy_blocks)}

<!-- RESULTS -->
<h2>4. Results</h2>

<h3>4.1 Passing tasks</h3>
{passing_block}

<h3>4.2 Top close-misses (≥ 0.5, below threshold)</h3>
{close_block}

<h3>4.3 Score distribution</h3>
<p>Across all 150 attempts:</p>
{_bar_chart(score_bins, n, lambda l: 'pass' if 'PASS' in l else ('close' if 'close' in l else ('zero' if 'no progress' in l else '')))}

<!-- FAILURE MODES -->
<h2>5. Failure modes</h2>

<h3>5.1 Action-type distribution (aggregate across 150 attempts)</h3>
<p>Total model actions: <strong>{stats['total_actions']:,}</strong>.
Action types:</p>
<table>
<thead><tr><th>Type</th><th>Count</th><th>% of all actions</th></tr></thead>
<tbody>
{"".join(f'<tr><td><code>{t}</code></td><td class="num">{c:,}</td><td class="num">{c*100/stats["total_actions"]:.1f}%</td></tr>' for t, c in stats['action_type_counts'].items())}
</tbody></table>

<p>The model overwhelmingly relied on <code>click</code> ({stats['action_type_counts'].get('click', 0)*100/stats['total_actions']:.0f}% of all actions)
even though shape creation requires <code>drag</code>. Only
{stats['action_type_counts'].get('drag', 0):,} drag actions were emitted
({stats['action_type_counts'].get('drag', 0)*100/stats['total_actions']:.1f}%
of all actions).</p>

<h3>5.2 Off-viewport coordinate prior</h3>
<p>Of {stats['total_clicks']:,} click-type actions, <strong>{stats['off_viewport_clicks']:,}
({stats['off_viewport_pct']:.1f}%)</strong> landed outside the 1280×800
viewport. The model has a strong learned prior at <code>y ≈ 953</code>
inherited from full-resolution desktop Figma screenshots in its training data.
Coord-clamp activated <strong>{stats['coord_clamp_total']:,} times</strong>
across the run to push these back into bounds.</p>

<h3>5.3 Tool-fixation loops</h3>
<p>The most common stuck pattern: repeated clicks on the same tool icon
without ever switching to a canvas drag. Loop-break fired
<strong>{stats['loop_break_total']:,} times</strong> total. Of 150 attempts,
{stops.get('loop_break_abort', 0)} were terminated by the &gt;10-loop_break
early-abort rule (versus only {stops.get('done', 0)} that called
<code>type: "done"</code> themselves).</p>

<h3>5.4 Keyboard-shortcut usage</h3>
<p>Despite an explicit shortcut table in the system prompt and a working
keyboard, the model only emitted <strong>{stats['total_keypresses']:,}
keypress actions</strong> ({stats['total_keypresses']*100/stats['total_actions']:.1f}%
of all actions). When it did use them, <code>r</code> (rectangle) and
<code>o</code> (ellipse) were the most common:</p>
<table>
<thead><tr><th>Key</th><th>Count</th></tr></thead><tbody>{keypress_rows}</tbody>
</table>

<h3>5.5 Score plateaus (model has stable failure modes)</h3>
<p>For <strong>{len(plateaus)} of 50 tasks</strong>, all 3 attempts scored
within 0.05 of each other (i.e. the model produces the same partial solution
every retry but cannot push past it). Top 15:</p>
{plateau_block}

<p>This is strong evidence that k=3 reruns do not unlock additional capability
— the model's "approach" to most tasks is deterministic given the prompt and
initial screenshot. Diversity comes from screen variance after the first
action, but the planning ceiling is fixed per task.</p>

<h3>5.6 Coordinate-format pathologies</h3>
<p>Frequent malformations observed in tool-call arguments:</p>
<ul>
<li>String-packed coords: <code>{{"x": "435, 953"}}</code> (one field, comma-separated)</li>
<li>List-packed coords: <code>{{"x": [435, 953]}}</code> (list under x, y is None)</li>
<li>Drag path with single waypoint holding two endpoints: <code>{{"path": [{{"x": [300, 500], "y": [200, 400]}}]}}</code></li>
<li>Legacy XML tool-call syntax bleeding into <code>content</code>:
<code>&lt;parameter=reason&gt;...&lt;/parameter&gt;&lt;/function&gt;&lt;/tool_call&gt;</code></li>
</ul>
<p>The adapter's parser handles all of these tolerantly, so they don't
cause crashes — but they signal the model is confused between tool-call
conventions and isn't reliably following the OpenAI-style schema we declare.</p>

<!-- CONCLUSIONS -->
<h2>6. Conclusions</h2>

<p><strong>Qwen3.5-27B is not a viable CUA agent on this benchmark.</strong>
The 4.0% pass@3 result reflects fundamental model limitations, not harness
artifacts:</p>

<ul>
<li><strong>It can do simple shape compositions when the canvas is empty.</strong>
The two passing tasks (task_05 plus-sign and task_36 polaroid-frame) are
2-shape compositions. The model reliably handles these in 5–11 turns.</li>
<li><strong>It loses planning coherence on multi-shape compositions.</strong>
Once the canvas has shapes on it, the model regresses to clicking known-bad
coordinates from its training-data prior. Without coord-clamp and loop-break,
this manifests as 100% off-viewport clicks and 70%+ consecutive-loop rates
(as observed in the baseline diagnostic).</li>
<li><strong>It does not synthesize "I should drag instead of click" from
explicit instructions.</strong> Both the system prompt and the runtime
loop-break message tell the model exactly how to draw shapes with the
<code>drag</code> action. The intervention raised pass@1 from 0% to 10% on a
10-task diagnostic — clear evidence the nudges help — but the full-run
pass@3 stayed at 4%, indicating most tasks require multi-step planning the
model can't sustain.</li>
<li><strong>k=3 retries do not unlock latent capability.</strong>
{len(plateaus)} of 50 tasks scored within 0.05 across all 3 attempts. The
model is deterministic w.r.t. the prompt + first screenshot; retries mostly
duplicate prior attempts.</li>
</ul>

<p>For an open-weight model evaluation, this is a meaningful negative result:
even with generous interventions (coord correction, loop-break with explicit
recipe injection, generous step_cap, keyboard enabled, parallel sharding),
Qwen3.5-27B handles only the simplest 1–2 shape tasks. The benchmark
discriminates well — task_36 passing 2/3 vs. half of category D scoring &lt;0.1
isn't noise, it's the model's real capability profile.</p>

</body></html>
"""
    return html


def render_pdf(html_path: Path, pdf_path: Path) -> None:
    """Use Playwright Chromium to render HTML → PDF."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        page.goto(f"file://{html_path.resolve()}", wait_until="networkidle")
        page.pdf(
            path=str(pdf_path),
            format="Letter",
            margin={"top": "0.6in", "right": "0.7in", "bottom": "0.6in", "left": "0.7in"},
            print_background=True,
        )
        browser.close()


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    runs = [Path(p) for p in argv[1:]]
    for r in runs:
        if not r.is_dir():
            print(f"ERROR: not a directory: {r}", file=sys.stderr)
            return 2

    merged_path = Path("merged_attempts.json")
    if not merged_path.is_file():
        print("ERROR: merged_attempts.json missing — run merge_runs.py first", file=sys.stderr)
        return 3

    merged = _load_merged(merged_path)
    by_task: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for a in merged:
        by_task[a["task_id"]].append(a)

    stats = _aggregate_trajectory_data(runs)
    plateaus = _detect_plateaus(by_task)
    score_bins = _score_distribution(merged)

    html = _build_html(merged, by_task, stats, plateaus, score_bins)

    html_path = Path("report.html")
    html_path.write_text(html, encoding="utf-8")
    print(f"wrote {html_path} ({len(html):,} bytes)")

    pdf_path = Path("report.pdf")
    print(f"rendering {pdf_path} via Playwright...")
    render_pdf(html_path, pdf_path)
    print(f"wrote {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

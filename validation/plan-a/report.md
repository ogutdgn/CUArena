# Plan A validation report — foundations, desktop tools, skeleton pass

**Plan:** `docs/superpowers/plans/2026-07-08-p1-plan-a-foundations-skeleton.md`
**Status:** COMPLETE (pending final whole-branch review + merge)
**Executed:** 2026-07-08, branch `plan-a` (base `0ae595b`, head `a57729d`)
**Spec at time of execution:** as of commit `0ae595b`

## Questions and verdicts

| # | Question | Verdict | Evidence |
|---|---|---|---|
| A1 | Can our tools read and drive real Windows apps? | **ANSWERED-YES** | 7 smoke tests pass individually AND in one combined invocation (7/7 in 13.2s): UIA tree read, window detection, real clicks opening menus, ESC closing them, capture, hit-test, launch. See `results/notepad/` |
| A2 | Does the schema fit reality? | **ANSWERED-YES** (1 amendment) | Real Notepad surface (37 elements) and Word surface (22 elements) both validated through the models with the exactly-one-marker rule; one reality fix required: colons in node ids are invalid in Windows paths → writer sanitizes (commit `d14f308`) |
| A3 | Does ONE general codebase drive two different apps with only config differences? | **ANSWERED-YES** | Same pipeline ran Notepad (full) and Word (scoped); grep check clean — zero app names in `pipeline/` or `tools/` (comment cleanup `a57729d`); app data only in `configs/apps/*.json` |
| A4 | Can the skeleton agent produce a sensible identity + feature inventory? | **ANSWERED-YES** | Live agent run produced 8 coherent features for Notepad (incl. modern realities: tab management, AI writing tools, rich-text formatting), every `trigger_path` grounded at `ui:main-window`; output schema-validated. Required one fix: hermetic agent options (`e0f564c`) |
| A5 | Is the discipline real in practice? | **ANSWERED-YES** (1 gap noted) | Journal captures every action with outcomes (`results/*/journal.jsonl`); version pinned (`10.0.26100.8521` recorded in app.json, asserted on re-runs, drift raises VersionDriftError — unit-tested); boundaries config loads and dismissals are journaled — though no live nag window existed to exercise dismissal end-to-end (see findings) |

## Acceptance runs

| Run | Command | Result | Snapshot |
|---|---|---|---|
| Notepad, no agent | `python -m pipeline.run notepad --no-agent` | exit 0; ui/main-window.json (37 elements) + screenshot + journal | `results/notepad/` |
| Notepad, with agent | `python -m pipeline.run notepad` | exit 0 (first attempt, post-fix); app.json with 8 features | `results/notepad/app.json` |
| Word, scoped surface | `python -m pipeline.run word --no-agent --max-containers 10` | exit 0 first try; ribbon-level surface (22 elements) + screenshot + journal | `results/word-surface/` |
| Combined smoke suite | `python -m pytest -m smoke` | 7 passed in 13.21s (single invocation — earlier hang was pre-fix window pollution, resolved) | — |

## Findings

| Finding | Action | Link |
|---|---|---|
| Colons in node ids (`ui:main-window`) are invalid in Windows directory names — the spec's `screenshots/<node-id>/` layout breaks on real filesystems | General fix: KB writer sanitizes `:` → `-` in screenshot paths | commit `d14f308` |
| OS locale changes BOTH window titles ("Not Defteri") and UI labels ("Dosya") — configs and tests must never assume English; **KB labels will be captured in the OS locale** (design consideration for Plan B: label language policy) | Title regex made locale-tolerant (config data); tests assert via locale-invariant automation ids | commit `5b61306` |
| Win11 store-app UIA trees nest far deeper than classic apps (menu items at depth 4, not 2) | General knob: `DEFAULT_SCAN_DEPTH = 5`, evidence-based | commit `bb21099` |
| Modern apps launch under broker processes (Popen pid unreliable) and can restore leftover windows with matching titles | Detection by hwnd-set-difference (never pid); launch() disambiguates via exact current title | commit `d038697` |
| Ambient Claude Code settings/CLAUDE.md leaked into the one-shot skeleton-agent SDK call, causing a failed run | Hermetic agent: `ClaudeAgentOptions(setting_sources=[], tools=[])` — agent sees ONLY its briefing | commit `e0f564c` |
| Deferred (tracked for later plans): handle-based UIA attach (two identically-titled windows edge case); boundary dismissal never exercised against a live nag window; DPI/multi-monitor coordinate alignment unverified | Noted in progress ledger; revisit in Plan B/C | — |

## Test suite state at acceptance

- Unit suite: **28 passed, 8 deselected, 0.38s** (`python -m pytest` — no GUI needed)
- Smoke suite: **7 passed, 13.21s** (`python -m pytest -m smoke` — single invocation)
- Live agent test: exercised via acceptance run (b) rather than the `agent_live` marker

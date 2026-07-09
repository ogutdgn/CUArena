# Plan A validation report — foundations, desktop tools, skeleton pass

**Plan:** `docs/superpowers/plans/2026-07-08-p1-plan-a-foundations-skeleton.md`
**Status:** COMPLETE — final whole-branch review passed (READY TO MERGE) after one fix wave (`83e1029`)
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

### Addendum: ready-state Word workspace run

| Run | Command | Result | Snapshot |
|---|---|---|---|
| Word, ready-state workspace, with agent | `python -m pipeline.run word --max-containers 10` | exit 0; ui/main-window.json now 73 workspace elements (window label `blank - Word`, ribbon tabs Home/Insert/Design/Layout/References/Mailings/Review/View/Help/Acrobat, ribbon command groups Clipboard/Font/Paragraph/Styles/Editing/Voice/Add-ins — zero template-gallery content); app.json with 25 features, all grounded at `ui:main-window` | `results/word-workspace/` |

`word.json` now sets `launch_args: ["{fixture}"]` and `fixture: configs/fixtures/word/blank.docx` (a real `.docx` generated once via Word COM), so `pipeline.stage0.build_argv` launches Word directly on that document instead of on no args. `configs/fixtures/word/blank.docx` is the fixture, committed as a small binary. No nag/dialog window was observed on this fixture-launch (journal shows no boundary events); `word.json`'s existing `dismiss_title_res` patterns (`.*What's New.*`, `.*Sign in.*`) were left unchanged.

Diagnostic evidence (live UIA-tree depth walk against the attached ready-state window) found ribbon tab names first appear at depth=8 (66 named nodes; depth=7 has 42 named nodes and zero ribbon hits) and ribbon command groups (Clipboard/Font/Paragraph/...) appear at depth=9. `DEFAULT_SCAN_DEPTH` in `pipeline/stage1_surface.py` was raised from 5 to 9 (first-appear depth + one level of margin, matching the original depth=3→5 margin policy) — a general, evidence-based knob, not Word-specific logic.

## Findings

| Finding | Action | Link |
|---|---|---|
| Colons in node ids (`ui:main-window`) are invalid in Windows directory names — the spec's `screenshots/<node-id>/` layout breaks on real filesystems | General fix: KB writer sanitizes `:` → `-` in screenshot paths | commit `d14f308` |
| OS locale changes BOTH window titles ("Not Defteri") and UI labels ("Dosya") — configs and tests must never assume English; **KB labels will be captured in the OS locale** (design consideration for Plan B: label language policy) | Title regex made locale-tolerant (config data); tests assert via locale-invariant automation ids | commit `5b61306` |
| Win11 store-app UIA trees nest far deeper than classic apps (menu items at depth 4, not 2) | General knob: `DEFAULT_SCAN_DEPTH = 5`, evidence-based | commit `bb21099` |
| Modern apps launch under broker processes (Popen pid unreliable) and can restore leftover windows with matching titles | Detection by hwnd-set-difference (never pid); launch() disambiguates via exact current title | commit `d038697` |
| Ambient Claude Code settings/CLAUDE.md leaked into the one-shot skeleton-agent SDK call, causing a failed run | Hermetic agent: `ClaudeAgentOptions(setting_sources=[], tools=[])` — agent sees ONLY its briefing | commit `e0f564c` |
| Deferred (tracked for later plans): handle-based UIA attach (two identically-titled windows edge case); boundary dismissal never exercised against a live nag window; DPI/multi-monitor coordinate alignment unverified | Noted in progress ledger; revisit in Plan B/C | — |
| Version pin currently reads the launcher stub binary (`shutil.which(cfg.exe)`), recorded `10.0.26100.8521` — that's the OS launcher stub's version, not the store-app Notepad 11.x actually running; store-app version pinning needs a better source (e.g. the attached window's process) | Deferred to Plan B: resolve version from the attached window's process (e.g. `pid`/`hwnd` -> process image path), not the launch-time `which` result | — |
| Apps that launch into a start screen/launcher were scanned in the wrong state (Word acceptance run scanned the template gallery because `WINWORD.EXE` with no args opens there, not the workspace) | Ready-state added: config `launch_args` + `fixture` opens the workspace directly (`build_argv` substitutes `{fixture}` with the fixture's absolute path); agent-driven ready-state discovery (auto-detecting how to reach a workspace without a hand-configured fixture) deferred to Plan B | `5dd8dc1`, `b981726` |

## Test suite state at acceptance

- Unit suite: **28 passed, 8 deselected, 0.38s** (`python -m pytest` — no GUI needed)
- Smoke suite: **7 passed, 13.21s** (`python -m pytest -m smoke` — single invocation)
- Live agent test: exercised via acceptance run (b) rather than the `agent_live` marker
- After the final-review fix wave (`83e1029`: agent-independent version pin, exclude_labels implemented, honest dismissal journaling, attach-rebind guard): **40 passed, 8 deselected**
- After the ready-state addendum (`launch_args`/`fixture` config fields, `build_argv` helper): **46 passed, 8 deselected**; notepad smoke test re-run alone still passes unchanged (no `launch_args` configured for notepad)

## Final-review findings fixed post-acceptance (commit `83e1029`)

| Finding | Fix |
|---|---|
| Version pinning only worked for agent runs (`app.json`-based) — `--no-agent` KBs never detected drift | `kb/<app>/version.json` written after every successful launch; checked first by `assert_version` |
| `boundaries.exclude_labels` was declared + documented but never read (dead config) | Implemented: surface scan filters excluded labels and journals `skipped-excluded` |
| Boundary dismissal journaled `dismissed` without verifying the window closed | Re-polls after ESC; journals `dismissed` only if the hwnd is gone, else `failed: still-present` |
| `launch()` could rebind the UIA attach target to an unrelated new window (e.g. a toast) | Exact-title rebind now also requires the title to match `window_title_re` |
| Version pin reads the launcher stub binary, not the store-app actually running | Documented; deferred to Plan B (resolve from the attached window's process) |

Residual Plan B ledger items from the re-review: bounded grace-poll for slow-closing nags; give `version.json` a model if it grows fields.

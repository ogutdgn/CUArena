# Figma Mock — Agent Guide

This is the **figma** app within `cua-bench`. It pairs a Figma-Design mock UI (`mock/`) with a verifier (`verifier/`) so we can score CUA agent runs against task rubrics.

For repo-level overview (the three-app monorepo, cross-app conventions, skills) see [../../CLAUDE.md](../../CLAUDE.md) and [../../overview/](../../overview/).

---

## Sub-projects

| Sub-project | Language | Purpose |
|---|---|---|
| `mock/` | TypeScript + React + Vite | Figma mock — the environment CUA agents interact with |
| `verifier/` | Python | Verifier framework — scores agent runs against task rubrics |

---

## How the two projects connect

```
CUA agent interacts with mock
        ↓
mock produces a log: figma-mock-log-<sessionId>.json
  └── raw[]      — every DOM input event
  └── semantic[] — every meaningful operation (create, move, fill, ...)
  └── outcome{}  — full document snapshot + shapeCounts at session end
        ↓
verifier reads that log and scores it
  └── checks outcome.document  → did the right shapes end up on canvas?
  └── checks semantic[]        → how many turns did it take?
  └── produces final_score = base_score × efficiency_multiplier
```

**The log format is the contract between the two projects.** Any change to the outcome.document schema or semantic event fields in `mock/` must be reflected in the verifier check primitives.

---

## Feature → Check relationship

Every feature implemented in `mock/` has a corresponding check primitive in `verifier/`. When a feature ships in `mock/`, the verifier can check for its outcome:

| mock feature | verifier check |
|---|---|
| Rectangle, ellipse, polygon... | `ShapeCount`, `ShapeCountAtLeast` |
| Polygon sides, star points | `PolygonSidesEquals`, `StarPointsEquals` |
| Fill color | `SolidColorEquals`, `FillTypeIs` |
| Stroke | `StrokeExists`, `StrokeWeightEquals` |
| Drop shadow / layer blur | `DropShadowExists`, `LayerBlurExists` |
| Opacity | `OpacityEquals` |
| Corner radius | `CornerRadiusEquals` |
| Layer alignment | `LayersAligned`, `LayersSymmetricX` |
| Frame nesting | `LayerInsideFrame`, `LayerContains` |
| Z-order | `ZOrderIsFirst`, `ZOrderIsLast` |
| Text content | `TextContent`, `FontSizeEquals` |
| Image fill | `ImageFillExists` |
| Multiple pages | `PageCount`, `LayerOnPage` |

When a new feature is checked off in `app-docs/feature-checklist.md`:
1. Check if any `planned` tasks in `app-docs/verifier-doc/tasks.csv` now become `in_scope`.
2. Check if new check primitives are needed in `verifier/checks/`.

---

## Document map (this app)

```
apps/figma/
├── CLAUDE.md (this file)         agent guide for this app
├── AGENTS.md                     mirror of CLAUDE.md (Codex/other tooling)
├── README.md                     top-level intro for the app
├── requirements.txt              Python deps (pyyaml — needed by verifier/config.py)
├── .venv/                        Python venv (gitignored) — used by scripts/
├── app-docs/                     ALL documentation lives here
│   ├── feature-checklist.md     ← customer feature list; tick [x] as features ship
│   ├── execution-map.md         ← wave-by-wave plan + session log (update every session)
│   ├── mock_improvement_steps.md ← bug fixes + UI improvements + feature updates (single numbering, status-tracked)
│   ├── mock-doc/                 mock-side technical docs
│   │   ├── architecture.md      ← mock tech overview (stack, ops, state, folder layout)
│   │   └── logging-documentation.md ← full log schema reference (raw/semantic/outcome fields)
│   ├── verifier-doc/             verifier-side technical docs
│   │   ├── verifier-documentation.md ← verifier design: scoring model, check catalog, rubrics
│   │   ├── verifier-writer.md   ← instructions for AI agents writing per-task verifier.py scripts
│   │   ├── tasks.csv            ← 50-task scope/status table (planned / in_scope / shipped)
│   │   ├── task-qa.md           ← delivery-1 achievability audit and task QA checks
│   │   └── task-qa-actions.md   ← follow-up tracker for task QA / verifier QA actions
│   ├── scripts-doc/              scripts/ usage docs
│   │   ├── README.md            ← full flow diagram + step-by-step usage
│   │   └── best-practices.md    ← export-approach trade-offs + migration notes
│   └── helper/                   reference corpus for Figma feature specs
├── mock/                         the React Figma mock (TypeScript + Vite)
├── verifier/                     the Python framework (checks, rubrics, types) — library only
├── delivery-1/                   single source of truth for tasks: per-task prompt.md + verifier.py
├── scripts/                      CLI entry-points (run_task.py, score_log.py, qa_verifiers.py, qa_per_task/) + logs/scores output
└── cua-eval/                     50-task CSV + builder guide
```

**app-docs/helper/** — reference corpus for Figma feature specs (read via `app-docs/helper/00-overview.md §7a`).
Do not read `app-docs/helper/` blind — go through the overview first.

---

## Session workflow (mandatory — figma-app development)

Both `app-docs/feature-checklist.md` and `app-docs/execution-map.md` must be refreshed every session.

**At session start:** discuss which features will be tackled, then update `execution-map.md` to reflect the plan.

**At session end:**
- Tick newly-shipped items in `feature-checklist.md`.
- In `execution-map.md`:
  - Add a dated entry at the **top** of the Session log with what shipped.
  - In session-log entries, describe what shipped directly — do not label by Wave number.
  - **Delete** completed items from the lower plan. Do not annotate as "Done" — the session log is the record.
  - **Renumber waves from Wave 1** after deletions.
- If a new feature shipped, check whether any `planned` task in `app-docs/verifier-doc/tasks.csv` is now `in_scope` and whether new check primitives are needed.

---

## Documentation update protocol

When changing the figma app, update documentation by change type before finishing the task:

### Universal pre-finish gate

Before marking any bug fix, feature update, or UI improvement as done, explicitly check:

1. **Logger impact:** Did the change add, remove, rename, or reinterpret any user action, semantic event, raw target, or outcome field?
   - If yes, update `app-docs/mock-doc/logging-documentation.md`.
   - If no, record "Logger impact: none" in the relevant `app-docs/mock_improvement_steps.md` item when the item is non-trivial.
2. **Verifier impact:** Can the verifier framework check the new/changed behavior from `outcome.document` or `semantic[]`?
   - If a new checker/helper/rubric is needed, add it under `verifier/` and document it in `app-docs/verifier-doc/verifier-documentation.md` / `verifier-writer.md`.
   - If shared checker primitives change, run `scripts/qa_verifier_framework.py` in addition to the delivery verifier smoke test.
   - Do not modify `delivery-1/task_NN/prompt.md` or `delivery-1/task_NN/verifier.py` unless the user explicitly scopes task ownership into this branch.
3. **Task QA impact:** If scoring assumptions or task achievability changed, update `app-docs/verifier-doc/task-qa.md` and `app-docs/verifier-doc/task-qa-actions.md`.
4. **Architecture impact:** If the change creates or changes a durable engine/UI invariant, update `app-docs/mock-doc/architecture.md`.

This gate applies even for UI work. A UI-only change can still affect raw targets, semantic events, outcome reachability, or verifier guidance.

### Bug fix

- Add or update the bug entry in `app-docs/mock_improvement_steps.md`.
- If the fix changes engine architecture, coordinate-space rules, scene-graph invariants, tools, overlays, or UI systems, update `app-docs/mock-doc/architecture.md`.
- Audit logger impact. If semantic events, outcome shape, raw capture, or event meaning changes, update `app-docs/mock-doc/logging-documentation.md`.
- Run verifier QA when the change can affect final document state, event names, or scoring. If task QA status changes, update `app-docs/verifier-doc/task-qa.md` and record follow-up status in `app-docs/verifier-doc/task-qa-actions.md`.

### Feature update

- Check or update `app-docs/feature-checklist.md`.
- Add or update the feature entry in `app-docs/mock_improvement_steps.md`.
- Update `app-docs/mock-doc/architecture.md` for new app systems or durable behavior.
- Update `app-docs/mock-doc/logging-documentation.md` for any new or changed semantic/outcome contract.
- Check `app-docs/verifier-doc/tasks.csv` for tasks that should move from `planned` to `in_scope`, and update verifier docs if new check primitives are needed.

### UI improvement

- Track the item in `app-docs/mock_improvement_steps.md`.
- Update architecture docs only if the UI change creates a reusable pattern, panel state, overlay system, or other durable app behavior.
- Logger docs usually do not change unless the UI creates, removes, or renames a semantic action.

### Logger change

- Update `app-docs/mock-doc/logging-documentation.md`.
- Check verifier compatibility and update `app-docs/verifier-doc/verifier-documentation.md` if checks or scoring assumptions change.
- Mention logger impact in the relevant `app-docs/mock_improvement_steps.md` item.

### Verifier or task QA change

- Update `app-docs/verifier-doc/verifier-documentation.md` when the framework or check catalog changes.
- Update `app-docs/verifier-doc/verifier-writer.md` when authoring rules change.
- Update `app-docs/verifier-doc/task-qa.md` for audit findings and `app-docs/verifier-doc/task-qa-actions.md` for follow-up status.
- Run `scripts/qa_verifier_framework.py` for shared checker/helper changes and `scripts/qa_verifiers.py` to confirm all `delivery-1/` task verifiers still smoke-test cleanly.
- Run `scripts/qa_per_task/_runner.py <NN>` after changing a task verifier and `scripts/qa_per_task/_runner.py all` before broad delivery/verifier hardening commits.

Keep `app-docs/helper/` unchanged unless the user explicitly asks to refresh the helper corpus. Never read it blind; start from `app-docs/helper/00-overview.md`.

---

## Working on `mock/`

Code lives in `mock/`. Architecture: `app-docs/mock-doc/architecture.md`.

Reference material for Figma feature specs:
- `app-docs/helper/00-overview.md` — start here (§7a has agent workflows)
- `app-docs/helper/01-ui-schema-extraction.md` — UI regions, state matrix, color picker
- `app-docs/helper/02-feature-research.md` — ~250 feature specs across 34 categories

---

## Working on `verifier/`

`verifier/` is now a flat Python **library** — checks, rubrics, types, loader, config.
It has no `__init__.py` (PEP 420 namespace package) and no CLI of its own; entry-points live in `scripts/`.

To write a new task verifier: read `app-docs/verifier-doc/verifier-writer.md` — it has the full check catalog and rules.
Tasks live as `delivery-1/task_NN/verifier.py` (single source of truth) and `import` from this package
via `from verifier.checks.* import ...`.

---

## scripts/ — CLI entry-points + log/score output

The `scripts/` folder is the only place a human developer runs Python from. It also stores
the runtime artifacts (logs, scores) so the `verifier/` package and `delivery-1/` task
definitions stay clean.

```
scripts/
├── run_task.py             ← fetch current session log + score against delivery-1 task (full pipeline)
├── score_log.py            ← score an existing log file against a delivery-1 task (offline)
├── qa_verifiers.py         ← smoke-test all 50 verifiers against synthetic perfect/empty logs
├── qa_verifier_framework.py← smoke-test shared checker primitives
├── qa_per_task/            ← per-task delivery hardening stress batteries
├── generate_delivery_1.py  ← (legacy) regenerate the delivery-1 package
├── logs/                   ← saved logs from run_task.py / export-log
└── scores/                 ← saved scores from run_task.py / score_log.py
```

Usage docs for `scripts/` live in [`app-docs/scripts-doc/README.md`](app-docs/scripts-doc/README.md);
export-approach trade-offs in [`app-docs/scripts-doc/best-practices.md`](app-docs/scripts-doc/best-practices.md).

### How log export works

The `mock` (in dev mode) POSTs the full log to the Vite dev server at `POST /dev-log`
on every flush (~250 ms). `run_task.py` retrieves it with a plain HTTP GET — no Chrome
flags, no Playwright, no external dependencies.

```bash
# 1. Start the app (from apps/figma/mock/)
cd mock && npm run dev

# 2. Do stuff in the browser at http://localhost:5173

# 3. Run a task verifier end-to-end (from apps/figma/)
.venv/Scripts/python scripts/run_task.py task_01
# → saves log to scripts/logs/<task>_<timestamp>.json
# → saves score to scripts/scores/<task>_<timestamp>.json
# → prints log details + score breakdown to stdout

# Re-score a saved log
.venv/Scripts/python scripts/score_log.py --task 01 --log scripts/logs/<file>.json

# Smoke-test every verifier
.venv/Scripts/python scripts/qa_verifiers.py

# Smoke-test shared verifier checker primitives
.venv/Scripts/python scripts/qa_verifier_framework.py
```

### For automated CUA / Docker

The Vite relay is dev-only and not the right approach for automated runs. When a CUA agent
controls the browser via Playwright, the test harness already has CDP access and should
read sessionStorage directly via `page.evaluate()`. See `app-docs/scripts-doc/best-practices.md` for
the full comparison and migration steps.

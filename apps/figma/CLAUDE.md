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
1. Check if any `planned` tasks in `verifier/task-docs/tasks.csv` now become `in_scope`.
2. Check if new check primitives are needed in `verifier/verifier/checks/`.

---

## Document map (this app)

```
apps/figma/
├── CLAUDE.md (this file)         agent guide for this app
├── AGENTS.md                     mirror of CLAUDE.md (Codex/other tooling)
├── app-docs/
│   ├── feature-checklist.md     ← customer feature list; tick [x] as features ship
│   ├── execution-map.md         ← wave-by-wave plan + session log (update every session)
│   ├── architecture.md          ← mock tech overview (stack, ops, state, folder layout)
│   └── logging-documentation.md ← full log schema reference (raw/semantic/outcome fields)
├── verifier-docs/
│   ├── verifier-documentation.md ← verifier design: scoring model, check catalog, rubrics
│   └── verifier-writer.md        ← instructions for AI agents writing tasks/<id>.py scripts
├── helper/                       reference corpus for Figma feature specs
├── mock/                         the React Figma mock
├── verifier/                     the Python verifier framework
├── scripts/                      log export tooling (run_task.py)
├── cua-eval/                     50-task CSV + builder guide
└── delivery-1/                   per-task delivery package (50 prompt+verifier folders)
```

**helper/** — reference corpus for Figma feature specs (read via `helper/00-overview.md §7a`).
Do not read `helper/` blind — go through the overview first.

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
- If a new feature shipped, check whether any `planned` task in `verifier/task-docs/tasks.csv` is now `in_scope` and whether new check primitives are needed.

---

## Working on `mock/`

Code lives in `mock/`. Architecture: `app-docs/architecture.md`.

Reference material for Figma feature specs:
- `helper/00-overview.md` — start here (§7a has agent workflows)
- `helper/01-ui-schema-extraction.md` — UI regions, state matrix, color picker
- `helper/02-feature-research.md` — ~250 feature specs across 34 categories

---

## Working on `verifier/`

Code lives in `verifier/`. Setup and usage: `verifier/README.md`.

To write a new task verifier script: read `verifier-docs/verifier-writer.md` — it has the full check catalog and rules.

Run a verifier (from `apps/figma/verifier/`):
```bash
.venv/bin/python run.py --task house_task --log logs/house_sample.json
```

---

## scripts/ — log export tooling

The `scripts/` folder bridges `mock/` and `verifier/` for the **human developer** workflow.

```
scripts/
├── run_task.py        ← fetches the current session log, saves it, runs the matching task verifier
├── generate_delivery_1.py
├── requirements.txt
├── README.md          ← full flow diagram + step-by-step usage
└── best-practices.md  ← three export approaches, trade-offs, migration guide
```

### How log export works

The `mock` (in dev mode) POSTs the full log to the Vite dev server at `POST /dev-log`
on every flush (~250 ms). `run_task.py` retrieves it with a plain HTTP GET — no Chrome
flags, no Playwright, no external dependencies.

```bash
# 1. Start the app (from apps/figma/mock/)
cd mock && npm run dev

# 2. Do stuff in the browser at http://localhost:5173

# 3. Run a task verifier end-to-end (from apps/figma/)
verifier/.venv/Scripts/python scripts/run_task.py task_01
# → saves log to verifier/logs/<task>_<timestamp>.json
# → routes score into delivery-1/task_NN/output/<timestamp>/
```

### For automated CUA / Docker

The Vite relay is dev-only and not the right approach for automated runs. When a CUA agent
controls the browser via Playwright, the test harness already has CDP access and should
read sessionStorage directly via `page.evaluate()`. See `scripts/best-practices.md` for
the full comparison and migration steps.

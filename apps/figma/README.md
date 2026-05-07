# Figma Mock — CUA Evaluation System

A pixel-accurate mock of **Figma Design** paired with a **CUA verifier framework**. Together they form the evaluation environment for Computer Use Agent testing: the agent interacts with the mock app, and the verifier scores the outcome.

## Two sub-projects

| Sub-project | Language | Purpose |
|---|---|---|
| [`mock/`](mock/) | TypeScript + React (Vite) | The Figma mock — what the CUA sees and interacts with |
| [`verifier/`](verifier/) | Python | Verifier framework — reads logs, runs rubrics, produces scores |

They are connected by a single log file the app exports after each session. See **How they connect** below.

---

## Run the app

```bash
cd mock
npm install
npm run dev        # local dev server
npm run typecheck  # tsc -b --noEmit
npm run build      # production build
```

Export a log after interacting (dev mode only — browser console):
```javascript
__exportLog()   // downloads figma-mock-log-<sessionId>.json
```

---

## Run the verifier

```bash
# One-time setup (from apps/figma/)
python3 -m venv .venv
.venv/Scripts/pip install -r requirements.txt   # .venv/bin/pip on Unix

# Score an existing log against any of the 50 delivery-1 tasks
.venv/Scripts/python scripts/score_log.py --task 01 --log scripts/logs/house_sample.json

# Or full pipeline: live log + score (requires mock running on :5173)
.venv/Scripts/python scripts/run_task.py task_01
```

Score is auto-saved to `scripts/scores/<task>_<timestamp>.json`.

---

## How they connect

```
CUA agent interacts with mock
        ↓
mock exports: figma-mock-log-<sessionId>.json
  { raw[], semantic[], outcome{} }
        ↓
scripts/run_task.py loads delivery-1/task_NN/verifier.py + log
  checks outcome.document → did the right shapes end up on canvas?
  checks semantic[]       → how many turns did it take?
        ↓
scripts/scores/<task>_<timestamp>.json
```

---

## Documentation

All docs now live under [`app-docs/`](app-docs/):

```
apps/figma/app-docs/
├── feature-checklist.md      ← customer feature list; tick [x] as features ship
├── execution-map.md          ← session log (top) + pending waves (bottom)
├── bugs-found.md             ← running list of bugs surfaced by audits
├── mock-doc/
│   ├── architecture.md       ← mock stack, ops, state buckets, folder layout
│   └── logging-documentation.md  ← full log schema (raw/semantic/outcome fields)
├── verifier-doc/
│   ├── verifier-documentation.md  ← scoring model, check catalog, rubrics, CLI
│   ├── verifier-writer.md         ← instructions for writing per-task verifier.py scripts
│   └── tasks.csv                  ← 50-task scope/status table
├── scripts-doc/
│   ├── README.md             ← scripts/ flow diagram + step-by-step usage
│   └── best-practices.md     ← export-approach trade-offs + migration notes
└── helper/                   ← Figma feature spec corpus (read 00-overview.md first)
```

Agent instructions (session workflow, reference map, feature↔check relationship): [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md). Repo-root context: [`../../CLAUDE.md`](../../CLAUDE.md), [`../../overview/`](../../overview/).

---

## Reference material (Figma feature specs)

[`app-docs/helper/`](app-docs/helper/) holds the documentation corpus. Three entry points cover almost every task:

- [`app-docs/helper/00-overview.md`](app-docs/helper/00-overview.md) — project scope, principles, agent workflows (§7a)
- [`app-docs/helper/01-ui-schema-extraction.md`](app-docs/helper/01-ui-schema-extraction.md) — UI regions, state matrix, color picker
- [`app-docs/helper/02-feature-research.md`](app-docs/helper/02-feature-research.md) — ~250 feature specs across 34 categories

Do not read `app-docs/helper/figma_docs/` or `app-docs/helper/analysis/` directly — navigate through the entry points above.

---

## Project structure (this app)

```
apps/figma/
├── CLAUDE.md                 # Agent guide for this app
├── AGENTS.md                 # Mirror of CLAUDE.md (Codex / other tooling)
├── README.md                 # This file
├── requirements.txt          # Python deps (pyyaml — verifier/config.py needs it)
├── .venv/                    # Python venv (gitignored)
├── app-docs/                 # ALL documentation (feature lists + mock-doc/ + verifier-doc/ + scripts-doc/ + helper/)
├── mock/                     # The figma mock (Vite + React + TS)
├── verifier/                 # The verifier framework — Python library only (checks, rubrics, types)
├── delivery-1/               # 50-task source of truth (prompt.md + verifier.py per task)
├── scripts/                  # CLI entry-points (run_task / score_log / qa_verifiers) + logs/scores output
└── cua-eval/                 # 50-task CSV + builder guide
```

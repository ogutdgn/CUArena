# Figma Mock — CUA Evaluation System

A pixel-accurate mock of **Figma Design** paired with a **CUA verifier framework**. Together they form the evaluation environment for Computer Use Agent testing: the agent interacts with the mock app, and the verifier scores the outcome.

## Two sub-projects

| Sub-project | Language | Purpose |
|---|---|---|
| [`test-app/`](test-app/) | TypeScript + React (Vite) | The Figma mock — what the CUA sees and interacts with |
| [`test-verifier/`](test-verifier/) | Python | Verifier framework — reads logs, runs rubrics, produces scores |

They are connected by a single log file the app exports after each session. See **How they connect** below.

---

## Run the app

```bash
cd test-app
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
cd test-verifier
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python run.py --task house_task --log logs/house_sample.json
```

Score is auto-saved to `test-verifier/scores/<task_id>_<timestamp>.json`.

---

## How they connect

```
CUA agent interacts with test-app
        ↓
test-app exports: figma-mock-log-<sessionId>.json
  { raw[], semantic[], outcome{} }
        ↓
test-verifier reads the log
  checks outcome.document → did the right shapes end up on canvas?
  checks semantic[]       → how many turns did it take?
        ↓
scores/<task_id>_<timestamp>.json
```

---

## Documentation

```
project-documents/
├── app-docs/
│   ├── feature-checklist.md      ← customer feature list; tick [x] as features ship
│   ├── execution-map.md          ← session log (top) + pending waves (bottom)
│   ├── architecture.md           ← test-app stack, ops, state buckets, folder layout
│   └── logging-documentation.md  ← full log schema (raw/semantic/outcome fields)
└── verifier-docs/
    ├── verifier-documentation.md  ← scoring model, check catalog, rubrics, CLI
    └── verifier-writer.md         ← instructions for writing task/<id>.py verifier scripts
```

AI agent instructions (session workflow, reference map, feature↔check relationship): [`CLAUDE.md`](CLAUDE.md) / [`AGENTS.md`](AGENTS.md)

---

## Reference material (Figma feature specs)

[`helper/`](helper/) holds the documentation corpus. Three entry points cover almost every task:

- [`helper/00-overview.md`](helper/00-overview.md) — project scope, principles, agent workflows (§7a)
- [`helper/01-ui-schema-extraction.md`](helper/01-ui-schema-extraction.md) — UI regions, state matrix, color picker
- [`helper/02-feature-research.md`](helper/02-feature-research.md) — ~250 feature specs across 34 categories

Do not read `helper/figma_docs/` or `helper/analysis/` directly — navigate through the entry points above.

---

## Project structure

```
.
├── CLAUDE.md                 # AI agent instructions
├── AGENTS.md                 # Same — for non-Claude AI agents
├── README.md                 # This file
├── project-documents/        # All documentation
│   ├── app-docs/             # test-app docs
│   └── verifier-docs/        # test-verifier docs
├── test-app/                 # Figma mock (Vite + React + TS)
├── test-verifier/            # Verifier framework (Python)
└── helper/                   # Figma feature spec corpus + analysis
```

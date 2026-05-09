# scripts/

CLI entry-points for the figma-mock CUA evaluation system. The verifier framework
lives at `../verifier/` (library only); task definitions live at `../delivery-1/`
(single source of truth, one folder per task). This folder also stores runtime
artifacts (`logs/`, `scores/`).

Related docs:

- `best-practices.md` preserves export/logging approaches and trade-offs for future harness work.
- `../mock-doc/logging-documentation.md` defines the log contract that these scripts consume.
- `../verifier-doc/verifier-documentation.md` defines the scoring framework used after a log is collected.

---

## Log flow: mock → score

```
mock (browser)
  │
  │  Every ~250 ms (on any action):
  │  logger/persist.ts flushes three streams to sessionStorage
  │    • _raw_      — every DOM input event
  │    • _semantic_ — every meaningful operation (create, move, fill …)
  │    • _outcome_  — full document snapshot + shape counts
  │
  │  In DEV mode only:
  │  persist.ts also POSTs the combined log to
  │  the Vite dev server at POST /dev-log
  │
  ▼
Vite dev server (:5173)
  │  devLogRelayPlugin (vite.config.ts) stores the latest payload in memory
  │  GET /dev-log returns it as JSON
  │
  ▼
scripts/run_task.py <task>
  │  GET http://localhost:5173/dev-log
  │  Writes the log to scripts/logs/<task>_<timestamp>.json
  │  Loads delivery-1/<task>/verifier.py and runs its rubrics
  │  Writes score to scripts/scores/<task>_<timestamp>.json
  │  Prints log details + score breakdown to stdout
```

---

## Usage

All commands run from `apps/figma/`. Use the venv's python (it has `pyyaml`):
`.venv/Scripts/python` (Windows) or `.venv/bin/python` (Unix).

### 1. Start the mock

```bash
cd mock
npm run dev
```

### 2. Open the app at http://localhost:5173 and perform actions

The log updates automatically — no extra steps needed.

### 3. Export and score (full pipeline)

```bash
# Numeric prefix or full task_NN name
.venv/Scripts/python scripts/run_task.py task_01
.venv/Scripts/python scripts/run_task.py 1

# Just export the log, no scoring
.venv/Scripts/python scripts/run_task.py export-log
.venv/Scripts/python scripts/run_task.py export-log task_01

# Docker / compose service-to-service fetch
docker compose run --rm verifier python3 scripts/run_task.py --host mock task_01
```

The log lands in `scripts/logs/<task>_<timestamp>.json` and the score in
`scripts/scores/<task>_<timestamp>.json`.

### Re-score an existing log file

```bash
.venv/Scripts/python scripts/score_log.py --task 01 --log scripts/logs/<file>.json
```

### Smoke-test all 50 verifiers

```bash
.venv/Scripts/python scripts/qa_verifiers.py
```

### Smoke-test verifier framework primitives

```bash
.venv/Scripts/python scripts/qa_verifier_framework.py
```

Use this when adding or changing shared checker primitives under `verifier/checks/`.
It covers framework capabilities that may not be exercised by the current
`delivery-1/` task set.

### Run per-task hardening QA

```bash
.venv/Scripts/python scripts/qa_per_task/_runner.py 01
.venv/Scripts/python scripts/qa_per_task/_runner.py all
```

`qa_per_task/` contains the delivery-1 hardening stress batteries ported from the
old `test-verifier/qa_per_task` layout. The runner loads canonical tasks from
`delivery-1/task_NN/verifier.py`; it does not use or require the old root
`test-verifier/tasks/` package.

---

## Files

| File | Purpose |
|---|---|
| `run_task.py` | Full pipeline: fetch live log via `GET /dev-log`, save it, score it against `delivery-1/<task>/verifier.py`, save and print result. Subcommand `export-log` exports without scoring. |
| `score_log.py` | Score an existing saved log file against a `delivery-1/` task verifier. |
| `qa_verifiers.py` | Smoke-test every `delivery-1/task_NN/verifier.py` against synthetic perfect/empty logs and flag CRASH / TOO STRICT / TOO LENIENT. |
| `qa_verifier_framework.py` | Smoke-test shared checker primitives that support newer mock features but may not be referenced by `delivery-1/` yet. |
| `qa_per_task/_runner.py` | Run targeted or full delivery-1 stress batteries from `qa_per_task/task_NN.py` against the canonical `delivery-1/task_NN/verifier.py` files. |
| `generate_delivery_1.py` | (Legacy) regenerator for `delivery-1/` package. |
| `logs/` | Saved logs from `run_task.py` / `export-log`. |
| `scores/` | Saved scores from `run_task.py` / `score_log.py`. |
| `best-practices.md` | Export-approach trade-offs and migration notes for automated CUA setups. |

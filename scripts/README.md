# scripts/

Helper scripts for the figma-mock CUA evaluation system.

---

## Log flow: test-app → test-verifier

```
test-app (browser)
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
  │  Writes the log to test-verifier/logs/<task>_<timestamp>.json
  │  Imports the matching tasks/<task>.py module and runs its rubrics
  │  Writes score to test-verifier/scores/<task>_<timestamp>.json
  │  Prints result to stdout
```

---

## Usage

### 1. Start the test-app

```bash
cd test-app
npm run dev
```

### 2. Open the app and do stuff

Navigate to `http://localhost:5173` in any browser. Perform whatever actions the
task requires. The log is updated automatically — no extra steps needed.

### 3. Export and score in one command

```bash
# Full pipeline: fetch the log, save it, run the matching task verifier, print score
test-verifier/.venv/Scripts/python scripts/run_task.py task_01

# Full module name also works
test-verifier/.venv/Scripts/python scripts/run_task.py task_01_house_task_comprehensive

# Just export the log, no scoring
test-verifier/.venv/Scripts/python scripts/run_task.py export-log
test-verifier/.venv/Scripts/python scripts/run_task.py export-log task_01
```

The log lands in `test-verifier/logs/<resolved-task>_<timestamp>.json` and the
score in `test-verifier/scores/<resolved-task>_<timestamp>.json`.

> Use the verifier venv's python (`test-verifier/.venv/Scripts/python` on
> Windows, `test-verifier/.venv/bin/python` on Unix). The script imports the
> verifier package directly and needs `pyyaml` available.

### Manually running just the verifier

```bash
cd test-verifier
.venv/Scripts/python run.py --task task_01_house_task_comprehensive --log logs/<file>.json
```

---

## Files

| File | Purpose |
|---|---|
| `run_task.py` | Fetches the current log, saves it, and runs the matching task verifier. Subcommand `export-log` exports without scoring. |
| `requirements.txt` | No extra deps for the script itself; relies on the verifier venv for `pyyaml`. |
| `best-practices.md` | Architecture trade-offs and migration notes |

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
scripts/export_log.py
  │  GET http://localhost:5173/dev-log
  │  Writes the log to test-verifier/logs/<task>_<timestamp>.json
  │
  ▼
test-verifier/run.py --task <name> --log logs/<file>.json
  │  Runs rubric checks against the log
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

### 3. Export the log

```bash
# From the repo root:
python3 scripts/export_log.py --task house_task

# Or from inside scripts/:
python3 export_log.py --task house_task
```

The log lands in `test-verifier/logs/house_task_<timestamp>.json`.

### 4. Run the verifier

```bash
cd test-verifier
.venv/bin/python run.py --task house_task --log logs/house_task_<timestamp>.json
```

---

## Files

| File | Purpose |
|---|---|
| `export_log.py` | Fetches the current log from the Vite relay and saves it to `test-verifier/logs/` |
| `requirements.txt` | No external deps — `export_log.py` uses only the Python standard library |
| `best-practices.md` | Architecture trade-offs and migration notes |

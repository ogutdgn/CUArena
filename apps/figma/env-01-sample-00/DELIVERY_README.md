# Env 01 - 11 Sample delivery

## 1) Run the env / Docker images

```bash
cd env-01-sample-00
MOCK_PORT=5173 docker compose up -d --build
```

Open:

- `http://localhost:5173/`
- If task has a fixture, you can use:
  - `http://localhost:5173/?task=task_51`
  - or (recommended for reproducible scoring): `http://localhost:5173/?task=task_51`

Stop:

```bash
docker compose down
```

## 2) Test tasks / verifiers

After doing an attempt on canvas, run:

```bash
docker compose run --rm verifier python3 scripts/run_task.py --host mock task_51
```

If you have run multiple instances of the canvas & want to test a specific session:

```bash
docker compose run --rm verifier python3 scripts/run_task.py --host mock task_51  --session-id <SESSION_ID>
```

Score an existing log file:

```bash
docker compose run --rm verifier python3 scripts/score_log.py --task task_51 --log runtime/output/by-task/task_51/logs/<log_file>.json
```

## 3) Review logs

All outputs are outside containers in `runtime/output/`:

- Raw mock relay logs (all sessions):
  - `runtime/output/mock-devlog/<sessionId>.json`
- Per-task verifier logs:
  - `runtime/output/by-task/task_XX/logs/*.json`
- Per-task scores:
  - `runtime/output/by-task/task_XX/scores/*.json`
- Per-task copy of raw session payload:
  - `runtime/output/by-task/task_XX/mock-devlog/<sessionId>.json`

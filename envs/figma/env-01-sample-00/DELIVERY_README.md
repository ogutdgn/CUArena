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
docker compose run --rm verifier python3 scripts/run_task.py --host figma-env task_51
```

If you have run multiple instances of the canvas & want to test a specific session:

```bash
docker compose run --rm verifier python3 scripts/run_task.py --host figma-env task_51 --session-id <SESSION_ID>
```

Score an existing log file:

```bash
docker compose run --rm verifier python3 scripts/score_log.py --task task_51 --log runtime/output/Competitor-logs-scores/task_51/runs/<run_id>/log.json
```

## 3) Review logs

All outputs are outside containers in `runtime/output/`:

- Environment session logs:
  - `runtime/output/environment-devlog/<sessionId>.json`
- Competitor rollouts + scores:
  - `runtime/output/Competitor-logs-scores/task_XX/runs/<run_id>/`
  - Each run folder has `trajectory`, `screenshots`, `log.json`, `end_state.json`, `score.json`, etc.
- Re-scored verifier outputs:
  - `runtime/output/Competitor-logs-scores/task_XX/scores/*.json`

## 4) Sonnet rollout overview

See:

- `runtime/output/Competitor-logs-scores/README.md`

It includes:

- how Sonnet runs were executed
- per-task original score vs re-score
- verifier deltas (if any)

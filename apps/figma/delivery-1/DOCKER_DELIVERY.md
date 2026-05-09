# Docker Delivery Guide (Customer Handoff)

If you want a runtime-only handoff (no repo checkout), use:

- [RUNTIME_ONLY_DELIVERY.md](RUNTIME_ONLY_DELIVERY.md)

That path ships prebuilt images + host commands only.

This environment can be shipped as a Dockerized package with:

- `mock/` (web UI)
- `verifier/` + `scripts/` (Python scoring)
- `delivery-1/` (50 tasks: prompt + verifier copies)

## 1) What to deliver

Send the `apps/figma/` snapshot containing at least:

- `docker-compose.yml`
- `docker/`
- `mock/`
- `verifier/`
- `scripts/`
- `delivery-1/`
- `requirements.txt`

Or generate a clean handoff archive:

```bash
./scripts/package_delivery.sh
```

## 2) Start the environment

From `apps/figma/`:

```bash
docker compose up -d --build mock
```

Open: `http://localhost:5173`

## 3) Run a task and score it

After the agent/human performs actions in the app:

```bash
# Fetch /dev-log from mock container and score task 01
docker compose run --rm verifier python3 scripts/run_task.py --host mock task_01
```

Outputs are persisted to host:

- `scripts/logs/*.json`
- `scripts/scores/*.json`

## 4) Score an existing log directly

```bash
docker compose run --rm verifier \
  python3 scripts/score_log.py --task 01 --log scripts/logs/<your-log>.json
```

For `task_NN_*`, verifier output is also routed to:

- `delivery-1/task_NN/output/<timestamp>/{log.json,reward.txt,result.json}`

## 5) Verify all 50 task verifiers quickly

```bash
docker compose run --rm verifier python3 scripts/qa_verifiers.py
```

## 6) Recommendation for fast RL / CI rollouts

For high-throughput automated runs, keep Docker for environment reproducibility but avoid `/dev-log` polling as the primary extraction path. Prefer reading session storage from the browser harness (`page.evaluate`) and passing the reconstructed log directly to the verifier.

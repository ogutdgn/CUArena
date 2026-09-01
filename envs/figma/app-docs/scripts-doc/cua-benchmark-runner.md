# CUA Benchmark Runner (OpenAI + Anthropic)

This runner executes delivery tasks in the mock app with CUA providers, then
captures logs and verifier scores automatically.

Script:

- `apps/figma/scripts/cua_benchmark_runner.py`

## Why this runner

- Session-safe scoring: logs are fetched by explicit `sessionId`.
- Minimal cores by default: `--max-parallel 1`.
- Unified output for both providers.

## Prerequisites

From `apps/figma/`:

1. Start mock:

```bash
docker compose up -d --build mock
```

2. Python deps:

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
```

3. API keys:

```bash
export OPENAI_API_KEY=...
export ANTHROPIC_API_KEY=...
```

## Quick run (single core)

```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers openai,anthropic \
  --tasks 01,02 \
  --max-parallel 1
```

## Config-file run

Edit `scripts/cua_benchmark.config.example.json`, then:

```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --config scripts/cua_benchmark.config.example.json \
  --max-parallel 1
```

## Output artifacts

Each run writes to:

- `scripts/cua_runs/<timestamp>/leaderboard.json`
- `scripts/cua_runs/<timestamp>/leaderboard.csv`

Per episode:

- `.../<provider>/task_NN/<timestamp>/actions.jsonl`
- `.../<provider>/task_NN/<timestamp>/log.json`
- `.../<provider>/task_NN/<timestamp>/score.json`
- `.../<provider>/task_NN/<timestamp>/summary.json`

## Notes for scale

- Keep `--max-parallel 1` inside each runner process to minimize cores.
- Scale out by running one runner process per container.
- Each container should point at its own mock instance.
- If a provider/tool schema changes, update provider adapter logic in
  `cua_benchmark_runner.py`.


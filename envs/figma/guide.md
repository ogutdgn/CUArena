# Claude CUA Smoke Test Guide

## Purpose
Run staged Claude CUA rollouts on `task_01`, capture full artifacts, and score with built-in verifiers.

## What gets captured per rollout
Each episode folder contains:
- `prompt.md` (task prompt used)
- `actions.jsonl` (executed tool actions)
- `claude_messages.jsonl` (turn-by-turn Claude request/response traces; image payloads redacted in trace logs)
- `screens/start.png` (initial state)
- `screens/turn_XXX_action_YY.png` (per-action screenshots)
- `screens/final.png` (end-state screenshot)
- `status.json` (dev-log relay status)
- `log.json` (session-scoped app log)
- `score.json` (verifier result)
- `summary.json` (stop reason, turns, steps, reward)
- `trace_meta.json` (episode stop metadata)

## Rate-limit mitigation
The runner truncates Anthropic screenshot history before each API call:
- keeps only the latest 3 image blocks
- replaces older image blocks with: `"screenshot omitted"`

This reduces input token pressure during long sessions.

## Prerequisites
From `apps/figma/`:

1. Start mock app:
```bash
docker compose up -d --build mock
```

2. Ensure Python venv exists and has deps:
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
```

3. API key setup (`apps/figma/.env` supported):
```bash
claude_api_key=... 
```
Accepted key names:
- `ANTHROPIC_API_KEY`
- `CLAUDE_API_KEY`
- `claude_api_key`

## Stage runs

### Stage 1: one-turn smoke (`max-steps=1`)
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 1 \
  --max-parallel 1 \
  --output-dir scripts/cua_runs/stage1_turn1
```

### Stage 2: one session, 10-step cap
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 10 \
  --max-parallel 1 \
  --output-dir scripts/cua_runs/stage2_turn10
```

### Stage 3: one session, 50-step cap
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 50 \
  --max-parallel 1 \
  --output-dir scripts/cua_runs/stage3_turn50
```

## How to verify stopping behavior
Read each episode `summary.json`:
- `stopped_by_model=true` means Claude returned no `tool_use` and stopped naturally.
- `hit_max_steps=true` means run terminated by the configured cap.
- `stop_reason` mirrors Anthropic API stop reason when available.

## k-runs per task
For repeated evaluation:
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01-10 \
  --runs-per-task 3 \
  --max-steps 50 \
  --max-parallel 1 \
  --output-dir scripts/cua_runs/tasks01_10_k3
```

Aggregate outputs:
- `leaderboard.csv`
- `aggregate_summary.json` (per-task and overall reward summary)

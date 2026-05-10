# Claude RL Smoke Plan (Task 01, staged)

## Goal
Run a controlled Claude CUA smoke evaluation with reproducible artifacts and verifier reward output.

## Stage 0: Runner/Trace Setup
### Changes to implement in `scripts/cua_benchmark_runner.py`
1. Environment loading
- Auto-load `apps/figma/.env` if present.
- Resolve Anthropic key from:
  - `ANTHROPIC_API_KEY` (primary)
  - `CLAUDE_API_KEY`, `claude_api_key` (fallback aliases)

2. Full trace capture per rollout session
- Create per-episode trace folder (example):
  - `scripts/cua_runs/<run_id>/anthropic/task_01/<episode_id>/traces/`
- Store:
  - `actions.jsonl` (tool actions executed)
  - `claude_messages.jsonl` (request/response envelope per turn)
  - `screens/turn_XXX.png` (post-action screenshots)
  - `screens/final.png` (end-state screenshot)
  - `log.json` (mock /dev-log payload)
  - `score.json` (verifier output)
  - `summary.json` (session metadata)

3. Stop semantics tracking
- Track and save:
  - `turns`
  - `steps`
  - `last_stop_reason` (Anthropic response)
  - `stopped_by_model` (true if no `tool_use` in final assistant turn)
  - `hit_max_steps` (true if loop exited due to configured cap)

4. Multi-run support per task
- Add CLI arg: `--runs-per-task K` (default `1`).
- Queue episodes as `(provider, task, run_index)`.
- Print and persist aggregate summary:
  - per task: count, success count, mean reward
  - overall: mean reward across all successful episodes

### Acceptance criteria
- Single episode produces complete trace set.
- `summary.json` includes explicit stop cause fields.
- Leaderboard includes run index and is stable across repeated runs.

---

## Stage 1: One-turn Claude API call (Task 01)
Run with a one-action cap to validate key auth + basic loop path.

Command:
```bash
cd apps/figma
docker compose up -d --build mock
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 1 \
  --max-parallel 1
```

Expected:
- One episode folder with full traces.
- `hit_max_steps=true` is acceptable at this stage.

---

## Stage 2: One session, 10-turn max (Task 01)
Command:
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 10 \
  --max-parallel 1
```

Expected:
- Full trace bundle.
- Valid `log.json` + `score.json`.
- Either model stop or max-step stop is explicitly recorded.

---

## Stage 3: One session, 50-turn max (Task 01)
Command:
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01 \
  --runs-per-task 1 \
  --max-steps 50 \
  --max-parallel 1
```

Expected:
- Higher completion chance than Stage 2.
- End-state screenshot and reward captured.

---

## Stage 4: Verify Claude stop behavior
Check `summary.json` and `claude_messages.jsonl`:
- `stopped_by_model=true` when final response has no `tool_use`.
- `hit_max_steps=true` only when run terminated by cap.
- `last_stop_reason` matches Anthropic response field.

Pass condition:
- Stop mode is unambiguous in summary for all 3 stages.

---

## Optional Extension (after smoke)
Run first 10 tasks with k repeats:
```bash
.venv/bin/python scripts/cua_benchmark_runner.py \
  --providers anthropic \
  --tasks 01-10 \
  --runs-per-task 3 \
  --max-steps 50 \
  --max-parallel 1
```
This yields per-task reward distribution and overall average for quick RL-style baselining.

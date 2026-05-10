# Agent Handoff (2026-05-09)

## Scope
This repo state is for `apps/figma/` under:
- Mock app: `apps/figma/mock/`
- Verifier framework: `apps/figma/verifier/`
- Delivery tasks: `apps/figma/delivery-1/task_01..task_50`
- Runtime scripts: `apps/figma/scripts/`

## Current Branch / Git State
- Repo: `CUA/env_01_canvas`
- Branch: `codex/cua-benchmark-runner`
- HEAD: `5ca4a9d` (`mock: preserve session and logs across refresh`)
- Local uncommitted change currently exists in:
  - `apps/figma/scripts/cua_benchmark_runner.py` (partial WIP trace-capture edits)
- Untracked local secret file:
  - `apps/figma/.env` (contains `claude_api_key`)

## What Was Completed Recently
1. Session-safe logging and scoring pipeline
- `/dev-log` keyed by `sessionId` (supports deterministic retrieval).
- `run_task.py` supports `--session-id`.
- Missing `/dev-log` now returns forced zero score instead of hard failing.

2. Dockerized delivery flow
- `docker-compose.yml` with `mock` + `verifier` services.
- Delivery docs and packaging scripts are in place.

3. Refresh resilience in mock app
- Refresh no longer wipes persisted session/log state.
- Session continuity and startup log restore were added.

4. Automated benchmark runner scaffold
- `scripts/cua_benchmark_runner.py` supports OpenAI + Anthropic episodes.
- Produces per-episode artifacts (`actions`, `log`, `score`, `summary`) and leaderboard.

## Current Infra Snapshot
- App docs: `apps/figma/README.md`
- Runner docs: `apps/figma/app-docs/scripts-doc/cua-benchmark-runner.md`
- Docker handoff: `apps/figma/delivery-1/DOCKER_DELIVERY.md`

## Past Action/Score Artifacts (Observed)
Existing historical logs/scores indicate many runs with no captured `/dev-log` payload and forced-zero behavior:
- Logs dir: `apps/figma/scripts/logs/`
- Scores dir: `apps/figma/scripts/scores/`
- Pattern seen:
  - `task_01_missing_*.json` log exports
  - `task_01_*.json` score files with zero rubrics due to missing relay payload

Interpretation:
- Verifier plumbing is working (it produces deterministic output).
- Operationally, runs were often launched without a posted mock session log reaching the same mock instance.

## Near-Term Goals
1. Upgrade Claude rollout trace capture:
- Save turn-by-turn screenshots.
- Save Claude response traces (including tool-use blocks and any textual/thinking blocks returned).
- Save final screenshot + verifier reward per rollout.
- Keep all traces grouped per run/session.

2. Add repeatable mini-RL test mode:
- `k` runs per task.
- Aggregate summary: mean/std reward per task and overall.

3. Execute staged Claude smoke tests:
- 1-turn task_01
- 10-turn max task_01
- 50-turn max task_01
- Confirm stop semantics (model stop vs max-turn cutoff).

## Handoff Notes for Next Agent
- Preserve `.env` secrecy; never print key values.
- Use `--max-parallel 1` for deterministic smoke tests.
- Prefer session-scoped log retrieval (`/dev-log?sessionId=...`) always.
- Finish/validate WIP changes in `cua_benchmark_runner.py` before broad rollout.

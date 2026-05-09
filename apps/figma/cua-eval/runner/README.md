# CUA pass@k harness

A Playwright-driven harness that runs OpenAI `computer-use-preview` and
Anthropic Claude `computer_20250124` agents against the figma mock,
scrapes the session log, scores it via the existing `verifier/` package,
and aggregates pass@k.

## Setup

```bash
# 1. Drop API keys (file is gitignored):
#      apps/figma/cua-eval/.env
#    Required:  OPENAI_API_KEY=...   and/or   ANTHROPIC_API_KEY=...
#    Start from:
#      cp apps/figma/cua-eval/.env.example apps/figma/cua-eval/.env

# 2. Install Python deps + a Chromium for Playwright:
cd apps/figma
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m playwright install chromium

# 3. Start the mock (separate terminal, from apps/figma/mock/):
npm run dev      # serves http://localhost:5173
```

## Run

```bash
# All from apps/figma/

# Single task
.venv/bin/python cua-eval/runner/passk.py --tasks 05

# Smoke test — 3 short tasks, k=1
.venv/bin/python cua-eval/runner/passk.py --providers anthropic --smoke

# Full sweep, k=1, threshold 0.7 (defaults)
.venv/bin/python cua-eval/runner/passk.py --providers anthropic openai

# Pick specific tasks and bump k
.venv/bin/python cua-eval/runner/passk.py --tasks 01 05 12 --k 3

# Use Opus 4.7 (more expensive, stronger)
.venv/bin/python cua-eval/runner/passk.py --providers anthropic \
    --anthropic-model claude-opus-4-7

# Watch the browser
.venv/bin/python cua-eval/runner/passk.py --smoke --headed

# Persist every attempt into SQLite (default path shown explicitly)
.venv/bin/python cua-eval/runner/passk.py --smoke \
    --trace-db cua-eval/runs/trace_store.sqlite3

# Optional: also embed PNG bytes in DB BLOBs (larger DB files)
.venv/bin/python cua-eval/runner/passk.py --smoke \
    --trace-db-store-screenshot-bytes

# Hosted backend (team-shared): Postgres metadata + S3 artifacts
.venv/bin/python cua-eval/runner/passk.py --smoke \
    --trace-backend postgres-s3 \
    --trace-postgres-dsn "$CUA_TRACE_POSTGRES_DSN" \
    --trace-s3-bucket "$CUA_TRACE_S3_BUCKET" \
    --trace-s3-prefix "figma/rollouts"

# Enable the harness (system prompt that describes the UI)
.venv/bin/python cua-eval/runner/passk.py --tasks 05 --harness

# Send the entire prompt.md including step-by-step solution (oracle baseline)
.venv/bin/python cua-eval/runner/passk.py --tasks 05 --prompt-mode full
```

`--run-id` is optional; it just renames the directory under `cua-eval/runs/`
(default: timestamp). A useful idiom for parallel batches:

```bash
RUN_ID=parallel_$(date +%Y%m%d_%H%M%S)
.venv/bin/python cua-eval/runner/passk.py --tasks 02 --run-id "$RUN_ID" ...
```

DB flags:

- `--trace-backend {sqlite,postgres-s3}`: trace backend type (default `sqlite`)
- `--trace-db <path>`: backend=sqlite path (default: `cua-eval/runs/trace_store.sqlite3`)
- `--no-trace-db`: disable DB writes and keep filesystem-only artifacts
- `--trace-db-store-screenshot-bytes`: backend=sqlite only, store screenshot PNG bytes as BLOBs
- `--trace-postgres-dsn`: backend=postgres-s3 DSN
- `--trace-s3-bucket`: backend=postgres-s3 artifact bucket
- `--trace-s3-prefix`: backend=postgres-s3 artifact prefix (default `cua-traces`)
- `--trace-aws-region`: backend=postgres-s3 AWS region (optional)
- `--trace-s3-endpoint-url`: backend=postgres-s3 custom S3 endpoint (optional, for MinIO/R2)

Env equivalents:

- `CUA_TRACE_BACKEND`
- `CUA_TRACE_DB`
- `CUA_TRACE_POSTGRES_DSN`
- `CUA_TRACE_S3_BUCKET`
- `CUA_TRACE_S3_PREFIX`
- `CUA_TRACE_AWS_REGION`
- `CUA_TRACE_S3_ENDPOINT_URL`

## Parallel runs

Each `passk.py` invocation drives a single Playwright browser against a single
mock instance, so parallelism is achieved by running **multiple mock servers
on distinct ports** and pointing one runner at each.

```bash
# Terminal 1 — mock on :5173
cd apps/figma/mock && npm run dev

# Terminal 2 — mock on :5174 (Vite auto-bumps the port if 5173 is taken)
cd apps/figma/mock && npm run dev

# Terminal 3 — runner against :5173
cd apps/figma
.venv/bin/python cua-eval/runner/passk.py --tasks 02 \
    --mock-url http://localhost:5173 --run-id "task02_$(date +%H%M%S)" --headed

# Terminal 4 — runner against :5174 (different task, same time)
cd apps/figma
.venv/bin/python cua-eval/runner/passk.py --tasks 05 \
    --mock-url http://localhost:5174 --run-id "task05_$(date +%H%M%S)" --headed
```

Rules:

- Each runner **must** point at its own dev-server port. Two runners sharing a
  mock will collide on session-log state and produce wrong scores.
- Distinct `--run-id`s keep `cua-eval/runs/` tidy when batches finish out of
  order.
- API rate limits still apply per-key — running 4 anthropic agents in parallel
  hits TPM caps faster than running them serially. Use `--turn-delay-s` /
  `--keep-screenshots` to pace.

## Prompt modes (`--prompt-mode`)

Each `delivery-1/task_NN/prompt.md` has several sections including a
**Step-by-step** numbered solution. The default mode strips everything but
the Thorough description so the model isn't given an oracle.

| Mode | What the model sees |
|---|---|
| `bare` | Simplified prompt body only (one-liner intent). |
| `description` *(default)* | Thorough description body only — for fair eval. |
| `full` | The entire `prompt.md` verbatim, including the step-by-step. |

## Harness (`--harness`)

By default the model receives **no** system prompt — only the task prompt
and screenshots. Pass `--harness` to add a one-paragraph system prompt
that describes the mock's left/right panels and viewport size.

### Customizing the harness

The harness text lives in `DEFAULT_SYSTEM_PROMPT` in each agent module:

- `cua-eval/runner/agents/anthropic.py` — Claude harness (uses `{w}` and `{h}` placeholders for viewport)
- `cua-eval/runner/agents/openai.py` — OpenAI harness (plain string, viewport already interpolated)

To plug in your own harness, either edit those constants or extend
`passk.py` to load a file (e.g. `--harness-file path/to/system.txt`)
and pass that string in place of the default.

## Output

Per-attempt artifacts are written **incrementally** so a killed run is still
inspectable. The `meta.json`, `prompt.txt`, and `system_prompt.txt` land
before the browser even launches. `trajectory.jsonl` and screenshots are
appended turn-by-turn. `log.json` and `score.json` land after scoring.

```
apps/figma/cua-eval/runs/<run_id>/
├── attempts.json                       all per-attempt results, machine-readable
├── summary.csv                         one row per attempt (incl. cost + elapsed)
├── summary.md                          headline pass@k + per-task per-provider table
└── <provider>/task_NN/attempt_K/
    ├── meta.json                       inputs + endpoint signature (see below)
    ├── outcome.json                    final summary (started/ended, cost, score, error)
    ├── prompt.txt                      EXACT user-message text the model received
    ├── system_prompt.txt               harness system prompt (empty if no --harness)
    ├── trajectory.jsonl                one JSON line per turn — actions, text, usage, screenshot
    ├── trajectory.json                 finalized trajectory (written at end)
    ├── screenshots/
    │   ├── initial.png                 viewport before turn 0
    │   └── turn_NN.png                 viewport after turn NN's actions
    ├── log.json                        the figma-mock session log
    └── score.json                      verifier output (rubrics, base, eff, final)
```

`meta.json` captures everything needed to reproduce the request:

```json
{
  "task_id": "task_05_plus_sign",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5",
  "endpoint": {
    "provider": "anthropic",
    "endpoint": "messages.create",
    "tool": {"type": "computer_20250124", "name": "computer",
             "display_width_px": 1280, "display_height_px": 800,
             "display_number": 1},
    "beta_headers": ["computer-use-2025-01-24"],
    "max_tokens": 4096,
    "keep_screenshots": 3,
    "turn_delay_s": 0.0,
    "max_retries": 5
  },
  "prompt_mode": "description", "prompt_chars": 412,
  "harness": false, "system_prompt_chars": 0,
  "step_cap": 60,
  "mock_url": "http://localhost:5173", "headless": true,
  "viewport": {"width": 1280, "height": 800, "device_scale_factor": 1},
  "pass_threshold": 0.7,
  "started_at_iso": "2026-05-08T20:21:37+00:00",
  "harness_git": {"git_sha": "554a7c1", "git_branch": "claude/...", "git_dirty": false},
  "sdk_versions": {"python": "3.11.x", "anthropic": "0.x.y", "openai": "1.x.y", "playwright": "1.x"},
  "argv": ["passk.py", "--tasks", "05", "--headed"]
}
```

`outcome.json` captures the post-run summary (cost, elapsed, score, error).

A `trajectory.jsonl` line looks like:

```json
{
  "turn": 3,
  "phase": "step",
  "elapsed_s": 14.7,
  "text": "I'll click the Rectangle tool now.",
  "actions": [{"action": "left_click", "coordinate": [42, 180]}],
  "usage_delta": {"input_tokens": 2843, "output_tokens": 187},
  "usage_total": {"input_tokens": 9821, "output_tokens": 612},
  "screenshot": "screenshots/turn_03.png"
}
```

## Trace persistence

When trace persistence is enabled, each run writes:

- `runs`: run config + summary
- `attempts`: one row per provider/task/attempt with score + usage + prompt/system prompt
- artifact records for screenshots, logs, trajectories, etc.

Two modes:

- `sqlite`: all metadata/artifacts in one local sqlite file
- `postgres-s3`: metadata in Postgres, artifact files uploaded to S3 and referenced by URI

Quick queries:

```bash
# Inspect latest runs
sqlite3 cua-eval/runs/trace_store.sqlite3 \
  "select run_id,status,attempt_count,pass_count from runs order by created_at_ms desc limit 10;"

# Best score per task/provider for a run
sqlite3 cua-eval/runs/trace_store.sqlite3 "
select provider, task_id, max(final_score) as best
from attempts
where run_id = 'YOUR_RUN_ID'
group by provider, task_id
order by provider, task_id;"

# Pull one attempt log JSON
sqlite3 cua-eval/runs/trace_store.sqlite3 "
select log_json
from attempts
where run_id='YOUR_RUN_ID' and provider='anthropic' and task_id='05' and attempt_index=1;"

# List screenshots for one attempt
sqlite3 cua-eval/runs/trace_store.sqlite3 "
select ordinal, filename, path, width, height, byte_size
from screenshots
where attempt_id = (
  select id from attempts
  where run_id='YOUR_RUN_ID' and provider='anthropic' and task_id='05' and attempt_index=1
);"
```

Postgres + S3 query examples:

```bash
psql "$CUA_TRACE_POSTGRES_DSN" -c "
select run_id,status,attempt_count,pass_count,created_at
from runs
order by created_at desc
limit 10;"

psql "$CUA_TRACE_POSTGRES_DSN" -c "
select provider, task_id, max(final_score) as best
from attempts
where run_id = 'YOUR_RUN_ID'
group by provider, task_id
order by provider, task_id;"

psql "$CUA_TRACE_POSTGRES_DSN" -c "
select artifact_kind, filename, storage_uri, byte_size
from artifacts
where attempt_id = (
  select id from attempts
  where run_id='YOUR_RUN_ID' and provider='anthropic' and task_id='05' and attempt_index=1
);"
```

## Bedrock-friendly deployment notes

For Bedrock-oriented infra, prefer:

- Postgres on RDS/Aurora
- S3 for artifacts
- IAM role auth for S3 (no static keys)
- short-lived DB credentials (Secrets Manager / IAM auth proxy)

## Pass criterion

An attempt **passes** if `final_score >= --threshold` (default `0.7`).
A task **passes at k** if at least one of its `k` attempts passed.

## Rate limits

Computer-use loops re-send every prior screenshot on every turn, so input
tokens grow each turn and you'll hit per-minute caps quickly. Two knobs:

- **`--keep-screenshots N`** *(default 3)* — Anthropic only. Replaces older
  images in the conversation with a small text stub. The model still sees
  the most recent N screens, which is what it actually needs.
- **`--turn-delay-s X`** *(default 0)* — wait X seconds between turns.
  Helpful when you've got a low TPM ceiling (e.g. fresh API account).

`429` and 5xx errors are retried automatically up to `--max-retries 5`
times, honoring the `retry-after` header when the API sends one.

If you keep blowing through the cap, drop `--keep-screenshots` to 1 or 2
and add a small `--turn-delay-s 2`.

## Cost estimates (rough, ~60-turn cap)

| Model | Per attempt avg | Worst case |
|---|---|---|
| `claude-sonnet-4-5` | $0.30–0.80 | ~$2.50 |
| `claude-opus-4-7`   | $1.50–4.00 | ~$12 |
| `computer-use-preview` | $0.30–0.70 | ~$2.00 |

## Design notes

- **Browser**: Playwright Chromium at 1280×800, `device_scale_factor=1`, so
  model-emitted coordinates map 1:1 to page coordinates.
- **Log capture**: at end of attempt, scrape the three sessionStorage keys
  written by `mock/src/logger/persist.ts` and reconstruct the same payload
  the Vite `/dev-log` relay would have POSTed. No mock changes needed.
- **Scoring**: in-process via `verifier/loader.py` and the matching
  `delivery-1/task_NN/verifier.py` module — same code path as
  `scripts/run_task.py`.
- **Smoke set**: tasks 05, 10, 12 (Plus-sign, Concentric squares, Card row)
  — short, mouse-only, end-to-end checkable in <15 turns.

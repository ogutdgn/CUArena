# `passk.py` — Flag Reference

Run from `apps/figma/`:

```bash
python3 cua-eval/runner/passk.py [flags]
```

`python3 cua-eval/runner/passk.py --help` prints the same info; this doc
groups flags by purpose with the *why* alongside.

---

## What runs

| Flag | Default | Purpose |
|---|---|---|
| `--providers anthropic [openai openrouter ...]` | `anthropic` | Which provider(s) to run. Each picks its own agent loop and model. |
| `--anthropic-model NAME` | `claude-sonnet-4-5` (env: `ANTHROPIC_MODEL`) | Anthropic model id. The harness picks the right computer-use tool/beta automatically per model. Use `claude-opus-4-7` for stronger but ~5× pricier runs. |
| `--openai-model NAME` | `computer-use-preview` (env: `OPENAI_MODEL`) | OpenAI model id. |
| `--openrouter-model NAME` | `qwen/qwen3.5-27b` (env: `OPENROUTER_MODEL`) | OpenRouter slug for any vision-language model that supports OpenAI-compatible function calling. Provider routing is pinned to DeepInfra (the only upstream that serves Qwen3.5-27B with image+tools). Set `OPENROUTER_API_KEY` first. |
| `--tasks 01 02 ...` | all 50 | Task ids to run, with or without leading zeros (`5` and `05` both work). |
| `--smoke` | off | Shortcut: run only `05 10 12` — three short, mouse-only tasks for cheap end-to-end validation. Overrides `--tasks`. |
| `--k N` | `1` | Attempts per task. pass@k = 1.0 if any of the k attempts cleared `--threshold`. |
| `--threshold X` | `0.7` | `final_score` threshold to count an attempt as passed. |
| `--step-cap N` | `0` (unlimited) | Hard cap on model turns per attempt. `0` (default) lets the model run until it emits a final message or errors out. Set to e.g. `60` to cut runaway loops short — attempts that hit the cap end with `stop_reason=step_cap`. |

---

## What the model sees

| Flag | Default | Purpose |
|---|---|---|
| `--prompt-mode {bare,description,full}` | `description` | Which slice of `delivery-1/task_NN/prompt.md` reaches the model. `bare` = simplified one-liner only. `description` = the Thorough description (recommended for fair eval). `full` = the entire `prompt.md` *including the step-by-step solution* (oracle baseline). |
| `--system-prompt SPEC` | `none` | Picks a system prompt. Three forms: <br>• `none` — no system prompt at all.<br>• `NAME` — resolves to `cua-eval/system-prompts/<NAME>.md`. Currently bundled: `mouse-only`, `figma-mock`, `click-only`.<br>• `PATH` — any `.md` / `.txt` file path is loaded verbatim. |
| `--block-keyboard` | off | Hard environment handicap. Intercepts the model's `type` / `key` / `keypress` actions at the executor and tells the model they were BLOCKED — useful when the mock truly doesn't accept keyboard input. Orthogonal to `--system-prompt`; pair with `mouse-only` or `click-only` for "keyboard is unplugged" experiments. |
| `--coord-clamp` | off | **(openrouter only)** Reject off-viewport coordinates with a corrective `tool_result` instead of letting Playwright click outside the canvas. Useful for models with frozen-coord priors (e.g. Qwen3.5-27B clicks at y=953 from full-resolution Figma training data). Fidelity-preserving: we don't silently move the click; we tell the model and let it retry. |
| `--loop-break` | off | **(openrouter only)** After 3 consecutive identical actions with no screen change, inject a "STUCK — try different" user message before the next request. Helps models break out of off-target click attractors. Pair with `--coord-clamp` for models that loop on off-viewport coords. |

Add a new system prompt by dropping a `.md` file into
`cua-eval/system-prompts/` — `--help` picks it up automatically.

The exact prompt that reached the model is captured per-attempt at
`<run_dir>/<provider>/task_NN/attempt_K/{prompt.txt,system_prompt.txt}`.

---

## Browser + mock

| Flag | Default | Purpose |
|---|---|---|
| `--mock-url URL` | `http://localhost:5173` | Where the figma mock is served. Each parallel runner needs its own port. |
| `--headed` | off (headless) | Show the Chromium window. Useful for watching a smoke run; required if you want to see the agent operate. |

---

## Rate limit / cost control

Computer-use loops re-send every prior screenshot on every turn, so input
tokens grow per turn. These knobs keep things sane:

| Flag | Default | Purpose |
|---|---|---|
| `--keep-screenshots N` | `3` | **(Anthropic + OpenRouter.)** In the conversation history, replace all but the last N screenshots with a small text stub. Keeps per-request input tokens flat instead of growing each turn. Drop to `1`–`2` if you keep hitting TPM caps; raise if the model needs longer visual memory. (OpenAI's adapter uses `previous_response_id` server-side, so the flag is a no-op there.) |
| `--turn-delay-s X` | `0` | Sleep X seconds between model turns. A hard ceiling of `60/X` requests/min on this process. Use `2`–`5` on low-tier API keys. |
| `--max-retries N` | `5` | On 429 / 5xx, retry up to N times with exponential backoff. Honors the `retry-after` header when the API sends one. |

---

## Run output / IDs

| Flag | Default | Purpose |
|---|---|---|
| `--run-id NAME` | timestamp `YYYYMMDD_HHMMSS` | Names the directory under `cua-eval/runs/`. Set to a shared value across multiple parallel terminals to merge their attempts under one run dir. |

---

## Trace database

The harness can write per-turn traces into a database alongside the
filesystem artifacts. Off-the-filesystem-only is the default; pass
`--no-trace-db` to skip the database entirely.

| Flag | Default | Purpose |
|---|---|---|
| `--trace-backend {sqlite,s3,postgres-s3}` | `sqlite` (env: `CUA_TRACE_BACKEND`) | Which trace backend. `sqlite` is local DB, `s3` uploads artifacts only, `postgres-s3` writes structured rows to Postgres and artifacts to S3. |
| `--trace-db PATH` | `cua-eval/runs/trace_store.sqlite3` (env: `CUA_TRACE_DB`) | SQLite file path (backend=sqlite only). |
| `--no-trace-db` | off | Disable DB ingestion entirely. Filesystem artifacts under `runs/<id>/...` still land normally. |
| `--trace-db-store-screenshot-bytes` | off | (sqlite only) Embed screenshot PNGs as BLOBs in the DB instead of just paths. |
| `--trace-postgres-dsn DSN` | env: `CUA_TRACE_POSTGRES_DSN` | postgres-s3 only: Postgres connection string. |
| `--trace-s3-bucket NAME` | env: `CUA_TRACE_S3_BUCKET` | s3/postgres-s3: S3 bucket for logs, screenshots, and end-state artifacts. |
| `--trace-s3-prefix PREFIX` | `cua-traces` (env: `CUA_TRACE_S3_PREFIX`) | s3/postgres-s3: key prefix inside the bucket. |
| `--trace-aws-region REGION` | env: `CUA_TRACE_AWS_REGION` | s3/postgres-s3: AWS region. |
| `--trace-s3-endpoint-url URL` | env: `CUA_TRACE_S3_ENDPOINT_URL` | s3/postgres-s3: custom endpoint (for MinIO, R2, etc.). |

---

## Common recipes

```bash
# Quickest sanity check (~$1, ~3 minutes)
python3 cua-eval/runner/passk.py --smoke --headed

# Single task, watching the browser
python3 cua-eval/runner/passk.py --tasks 05 --headed

# Fair eval on all 50 tasks, k=3, Sonnet
python3 cua-eval/runner/passk.py --k 3

# Mouse-only environment (the click-only system prompt + executor handicap)
python3 cua-eval/runner/passk.py --tasks 05 \
    --system-prompt click-only --block-keyboard

# Headline numbers on Opus
python3 cua-eval/runner/passk.py --anthropic-model claude-opus-4-7 \
    --keep-screenshots 2 --turn-delay-s 2

# Both providers, k=1, full sweep
python3 cua-eval/runner/passk.py --providers anthropic openai

# Qwen3.5-27B via OpenRouter, mouse-only
python3 cua-eval/runner/passk.py --providers openrouter \
    --openrouter-model qwen/qwen3.5-27b \
    --system-prompt figma-mock --block-keyboard --k 3

# Qwen3.5-27B with off-viewport-coord correction + loop-break (use with strict prompt)
python3 cua-eval/runner/passk.py --providers openrouter \
    --openrouter-model qwen/qwen3.5-27b \
    --system-prompt qwen-figma-strict --block-keyboard \
    --coord-clamp --loop-break --k 1

# Oracle baseline (model gets the step-by-step solution in the prompt)
python3 cua-eval/runner/passk.py --tasks 01 --prompt-mode full

# Parallel batch (different terminal each, shared run-id)
RUN_ID=batch_$(date +%H%M%S)
# T1: cd apps/figma/mock && npm run dev -- --port 5173
# T2: python3 cua-eval/runner/passk.py --tasks 01 02 03 --mock-url http://localhost:5173 --run-id "$RUN_ID"
# T3: cd apps/figma/mock && npm run dev -- --port 5174
# T4: python3 cua-eval/runner/passk.py --tasks 04 05 06 --mock-url http://localhost:5174 --run-id "$RUN_ID"
```

---

## Banner cheatsheet

When `passk.py` starts a run, it prints a banner like this:

```
Run id    : 20260509_141331
Run dir   : /.../cua-eval/runs/20260509_141331
Providers : anthropic
Tasks     : 1 (05)
k         : 1
Threshold : final_score >= 0.7
Mock URL  : http://localhost:5173
System    : cua-eval/system-prompts/click-only.md (2149 chars)  [keyboard allowed]
Prompt    : description
Trace DB  : sqlite /.../cua-eval/runs/trace_store.sqlite3
```

Glance at it before walking away — if `Tasks`, `Mock URL`, `System`, or
`Run id` look wrong (e.g. all 50 tasks instead of 1, default port instead
of `:5174`), Ctrl-C and re-issue. Most "the harness ignored my flags"
issues come from a multi-line paste breaking shell line continuation.

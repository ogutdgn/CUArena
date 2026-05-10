"""Pass@k orchestrator CLI.

Runs each task k times for each enabled provider, scores via the existing
verifier, writes per-attempt artifacts, and emits an aggregated summary.

Usage (run from apps/figma/):
  python cua-eval/runner/passk.py --providers anthropic --smoke
  python cua-eval/runner/passk.py --providers anthropic openai --k 1
  python cua-eval/runner/passk.py --tasks 01 02 03 --k 3

The `cua-eval` directory has a hyphen, so this script must be invoked by
path, not via `python -m`. The script-mode fallback below makes the
`runner.*` imports resolve in either invocation style.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Allow running both as a module and as a script.
HERE = Path(__file__).resolve()
APP_ROOT = HERE.parents[2]                        # apps/figma/
EVAL_ROOT = HERE.parent.parent                    # apps/figma/cua-eval/
RUNS_DIR = EVAL_ROOT / "runs"

if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))
if str(HERE.parent.parent.parent.parent.parent) not in sys.path:
    # Repo root, so `apps.figma...` import works if invoked as a module.
    sys.path.insert(0, str(HERE.parent.parent.parent.parent.parent))

try:
    from .runner import AttemptResult, list_task_dirs, run_attempt
    from . import report as report_mod
    from .trace_db import TraceStore, create_trace_store
except ImportError:
    # Script-style invocation (`python passk.py ...`) — promote the parent
    # package onto sys.path and re-import absolutely.
    sys.path.insert(0, str(HERE.parent.parent))
    from runner.runner import AttemptResult, list_task_dirs, run_attempt        # type: ignore
    from runner import report as report_mod                                     # type: ignore
    from runner.trace_db import TraceStore, create_trace_store                  # type: ignore


SMOKE_TASKS = ["05", "10", "12"]   # short, easy tasks for cheap end-to-end check
SYSTEM_PROMPTS_DIR = EVAL_ROOT / "system-prompts"


def _list_prompt_names() -> list[str]:
    if not SYSTEM_PROMPTS_DIR.is_dir():
        return []
    return sorted(p.stem for p in SYSTEM_PROMPTS_DIR.glob("*.md"))


def resolve_system_prompt(spec: str) -> tuple[str | None, str]:
    """Resolve ``--system-prompt`` to (text, label).

    - ``none`` → (None, "none")
    - contains '/' or '\\' or ends with .md/.txt → treated as a path
    - otherwise → cua-eval/system-prompts/<spec>.md
    """
    if spec == "none":
        return None, "none"
    p = Path(spec)
    looks_like_path = ("/" in spec or "\\" in spec
                       or spec.endswith(".md") or spec.endswith(".txt"))
    if not looks_like_path:
        p = SYSTEM_PROMPTS_DIR / f"{spec}.md"
    if not p.is_file():
        avail = ", ".join(_list_prompt_names()) or "(none)"
        raise SystemExit(
            f"--system-prompt: cannot find {spec!r} (looked at {p}). "
            f"Available NAMEs in cua-eval/system-prompts/: {avail}"
        )
    return p.read_text(encoding="utf-8"), str(p.relative_to(EVAL_ROOT.parent))


def load_dotenv() -> None:
    env_file = EVAL_ROOT / ".env"
    if not env_file.is_file():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if k and v and k not in os.environ:
            os.environ[k] = v


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Pass@k CUA benchmark runner")
    p.add_argument("--providers", nargs="+", default=["anthropic"],
                   choices=["anthropic", "openai"],
                   help="Which providers to run.")
    p.add_argument("--tasks", nargs="*", default=None,
                   help="Task IDs (e.g. 01 02 03). Defaults to all 50.")
    p.add_argument("--smoke", action="store_true",
                   help=f"Run only the smoke set ({', '.join(SMOKE_TASKS)}).")
    p.add_argument("--k", type=int, default=1, help="Attempts per task (default 1).")
    p.add_argument("--threshold", type=float, default=0.7,
                   help="final_score threshold to count as a pass (default 0.7).")
    p.add_argument("--step-cap", type=int, default=60,
                   help="Max model turns per attempt (default 60).")
    p.add_argument("--mock-url", default="http://localhost:5173",
                   help="URL of the running figma mock.")
    p.add_argument("--anthropic-model", default=os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5"))
    p.add_argument("--openai-model", default=os.environ.get("OPENAI_MODEL", "computer-use-preview"))
    p.add_argument("--prompt-mode", choices=["bare", "description", "full"], default="description",
                   help="What to send the model. Default: 'description' (Thorough description only). "
                        "'bare'=Simplified prompt only. 'full'=entire prompt.md including step-by-step solution.")
    p.add_argument("--system-prompt", default="none",
                   help="Pick a system prompt. Default 'none' (no system prompt). "
                        "Either a NAME (resolved to cua-eval/system-prompts/<NAME>.md), "
                        "an explicit PATH to a .md/.txt file, or 'none'. "
                        f"Available NAMEs: {', '.join(_list_prompt_names())}.")
    p.add_argument("--block-keyboard", action="store_true",
                   help="Make the executor refuse keyboard actions (type/key/keypress) "
                        "and tell the model they were blocked. Default: keyboard works. "
                        "Orthogonal to --system-prompt — pair with mouse-only/click-only "
                        "for a hard mouse-only environment.")
    p.add_argument("--keep-screenshots", type=int, default=3,
                   help="(anthropic) keep only the last N screenshots in conversation "
                        "history; older ones are replaced with a text stub. Default 3. "
                        "Lower = cheaper + less likely to hit input TPM, but less context.")
    p.add_argument("--turn-delay-s", type=float, default=0.0,
                   help="Seconds to sleep between model turns. Default 0. "
                        "Use 2-5s if you keep hitting rate limits.")
    p.add_argument("--max-retries", type=int, default=5,
                   help="On 429 / 5xx, retry up to N times with exponential backoff "
                        "(or the API's retry-after header). Default 5.")
    p.add_argument("--headed", action="store_true", help="Show the browser window.")
    p.add_argument("--run-id", default=None, help="Override the run id (default: timestamp).")
    p.add_argument(
        "--trace-backend",
        default=os.environ.get("CUA_TRACE_BACKEND", "sqlite"),
        choices=["sqlite", "postgres-s3"],
        help="Trace backend type (default: sqlite).",
    )
    p.add_argument(
        "--trace-db",
        default=os.environ.get("CUA_TRACE_DB", str(EVAL_ROOT / "runs" / "trace_store.sqlite3")),
        help="SQLite path for trace backend=sqlite (default: cua-eval/runs/trace_store.sqlite3).",
    )
    p.add_argument(
        "--no-trace-db",
        action="store_true",
        help="Disable DB ingestion and keep filesystem-only artifacts.",
    )
    p.add_argument(
        "--trace-db-store-screenshot-bytes",
        action="store_true",
        help="backend=sqlite only: store screenshot PNG bytes in DB BLOBs.",
    )
    p.add_argument(
        "--trace-postgres-dsn",
        default=os.environ.get("CUA_TRACE_POSTGRES_DSN"),
        help="backend=postgres-s3: postgres DSN",
    )
    p.add_argument(
        "--trace-s3-bucket",
        default=os.environ.get("CUA_TRACE_S3_BUCKET"),
        help="backend=postgres-s3: S3 bucket for artifacts",
    )
    p.add_argument(
        "--trace-s3-prefix",
        default=os.environ.get("CUA_TRACE_S3_PREFIX", "cua-traces"),
        help="backend=postgres-s3: S3 prefix",
    )
    p.add_argument(
        "--trace-aws-region",
        default=os.environ.get("CUA_TRACE_AWS_REGION"),
        help="backend=postgres-s3: AWS region (optional)",
    )
    p.add_argument(
        "--trace-s3-endpoint-url",
        default=os.environ.get("CUA_TRACE_S3_ENDPOINT_URL"),
        help="backend=postgres-s3: custom S3 endpoint URL (optional)",
    )
    return p.parse_args()


def resolve_provider_runner(
    provider: str,
    *,
    anthropic_model: str,
    openai_model: str,
    keep_screenshots: int,
    common_kwargs: dict[str, Any],
    system_prompt: str | None,
    block_keyboard: bool,
) -> tuple[Any, dict[str, Any], str | None]:
    """The system prompt has already been resolved to a string (or None);
    just pick the right agent runner and pass everything through. The
    ``allow_keyboard`` flag passed into the agent is the inverse of
    --block-keyboard."""
    if provider == "anthropic":
        try:
            if __package__:
                from .agents.anthropic import run_anthropic_agent
            else:
                from runner.agents.anthropic import run_anthropic_agent  # type: ignore
        except ImportError as exc:
            raise RuntimeError("anthropic provider unavailable. Install deps from requirements.txt") from exc
        return (
            run_anthropic_agent,
            {
                "model": anthropic_model,
                "keep_screenshots": keep_screenshots,
                "allow_keyboard": not block_keyboard,
                **common_kwargs,
            },
            system_prompt,
        )
    if provider == "openai":
        try:
            if __package__:
                from .agents.openai import run_openai_agent
            else:
                from runner.agents.openai import run_openai_agent       # type: ignore
        except ImportError as exc:
            raise RuntimeError("openai provider unavailable. Install deps from requirements.txt") from exc
        return (
            run_openai_agent,
            {
                "model": openai_model,
                "allow_keyboard": not block_keyboard,
                **common_kwargs,
            },
            system_prompt,
        )
    raise RuntimeError(f"Unknown provider: {provider}")


def resolve_task_list(args: argparse.Namespace) -> list[str]:
    if args.smoke:
        return SMOKE_TASKS[:]
    if args.tasks:
        return [t.zfill(2) for t in args.tasks]
    return [d.name.removeprefix("task_") for d in list_task_dirs()]


def attempt_label(provider: str, task_id: str, k_idx: int) -> str:
    return f"[{provider} task_{task_id} attempt_{k_idx + 1}]"


def main() -> int:
    args = parse_args()
    load_dotenv()

    tasks = resolve_task_list(args)
    run_id = args.run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = RUNS_DIR / run_id
    run_root.mkdir(parents=True, exist_ok=True)
    trace_db: TraceStore | None = None
    if not args.no_trace_db:
        trace_db = create_trace_store(
            backend=args.trace_backend,
            sqlite_path=Path(args.trace_db),
            sqlite_store_screenshot_bytes=args.trace_db_store_screenshot_bytes,
            postgres_dsn=args.trace_postgres_dsn,
            s3_bucket=args.trace_s3_bucket,
            s3_prefix=args.trace_s3_prefix,
            aws_region=args.trace_aws_region,
            s3_endpoint_url=args.trace_s3_endpoint_url,
        )
        trace_db.upsert_run(
            run_id=run_id,
            run_root=run_root,
            config={
                "providers": args.providers,
                "tasks": tasks,
                "k": args.k,
                "threshold": args.threshold,
                "step_cap": args.step_cap,
                "mock_url": args.mock_url,
                "prompt_mode": args.prompt_mode,
                "system_prompt": args.system_prompt,
                "block_keyboard": bool(args.block_keyboard),
                "headed": bool(args.headed),
                "run_id": run_id,
                "trace_backend": args.trace_backend,
                "trace_db": args.trace_db,
                "trace_s3_bucket": args.trace_s3_bucket,
                "trace_s3_prefix": args.trace_s3_prefix,
            },
        )

    print(f"Run id    : {run_id}")
    print(f"Run dir   : {run_root}")
    print(f"Providers : {', '.join(args.providers)}")
    print(f"Tasks     : {len(tasks)} ({', '.join(tasks) if len(tasks) <= 12 else tasks[0] + '...' + tasks[-1]})")
    print(f"k         : {args.k}")
    print(f"Threshold : final_score >= {args.threshold}")
    print(f"Mock URL  : {args.mock_url}")
    sys_prompt_text, sys_prompt_label = resolve_system_prompt(args.system_prompt)
    kb_state = "blocked" if args.block_keyboard else "allowed"
    if sys_prompt_text is None:
        print(f"System    : none  [keyboard {kb_state}]")
    else:
        print(f"System    : {sys_prompt_label} ({len(sys_prompt_text)} chars)  [keyboard {kb_state}]")
    print(f"Prompt    : {args.prompt_mode}"
          + ("  (⚠ includes step-by-step solution)" if args.prompt_mode == "full" else ""))
    if trace_db:
        if args.trace_backend == "sqlite":
            print(f"Trace DB  : sqlite {Path(args.trace_db)}"
                  + ("  (with screenshot blobs)" if args.trace_db_store_screenshot_bytes else ""))
        else:
            print(f"Trace DB  : postgres+s3 (bucket={args.trace_s3_bucket}, prefix={args.trace_s3_prefix})")
    else:
        print("Trace DB  : disabled (--no-trace-db)")
    print()

    all_attempts: list[AttemptResult] = []
    t0 = time.time()
    summary_json = run_root / "attempts.json"

    try:
        common_kwargs = {
            "step_cap": args.step_cap,
            "turn_delay_s": args.turn_delay_s,
            "max_retries": args.max_retries,
        }
        for provider in args.providers:
            agent_runner, agent_kwargs, sys_prompt = resolve_provider_runner(
                provider,
                anthropic_model=args.anthropic_model,
                openai_model=args.openai_model,
                keep_screenshots=args.keep_screenshots,
                common_kwargs=common_kwargs,
                system_prompt=sys_prompt_text,
                block_keyboard=args.block_keyboard,
            )

            for task_id in tasks:
                for k_idx in range(args.k):
                    label = attempt_label(provider, task_id, k_idx)
                    attempt_dir = run_root / provider / f"task_{task_id}" / f"attempt_{k_idx + 1}"
                    t_a = time.time()
                    print(f"{label} starting...", flush=True)
                    try:
                        res = run_attempt(
                            task_id=task_id,
                            provider=provider,
                            agent_runner=agent_runner,
                            agent_kwargs=agent_kwargs,
                            out_dir=attempt_dir,
                            mock_url=args.mock_url,
                            headless=not args.headed,
                            pass_threshold=args.threshold,
                            progress_prefix=label,
                            prompt_mode=args.prompt_mode,
                            system_prompt=sys_prompt,
                        )
                    except Exception as exc:
                        print(f"{label} CRASH: {exc}", flush=True)
                        continue
                    all_attempts.append(res)
                    if trace_db is not None:
                        trace_db.ingest_attempt(
                            run_id=run_id,
                            provider=provider,
                            task_id=task_id,
                            attempt_index=k_idx + 1,
                            attempt_dir=attempt_dir,
                            result=res,
                        )
                    dt = time.time() - t_a
                    pass_mark = "✓ pass" if res.passed else "✗ fail"
                    err = f"  err={res.error}" if res.error else ""
                    print(f"{label} {pass_mark}  score={res.final_score:.3f}/{res.max_score:.1f}  "
                          f"turns={res.turns}  stop={res.stop_reason}  {dt:.1f}s{err}", flush=True)

        summary_json.write_text(
            json.dumps([dataclasses.asdict(a) for a in all_attempts], indent=2),
            encoding="utf-8")

        report_mod.write_reports(all_attempts, run_root, threshold=args.threshold, k=args.k)
        if trace_db is not None:
            trace_db.finalize_run(
                run_id=run_id,
                attempts=all_attempts,
                extra={
                    "threshold": args.threshold,
                    "k": args.k,
                    "run_root": str(run_root.resolve()),
                    "summary_csv": str((run_root / "summary.csv").resolve()),
                    "summary_md": str((run_root / "summary.md").resolve()),
                    "attempts_json": str(summary_json.resolve()),
                },
            )

        print()
        print(f"Run complete in {time.time() - t0:.1f}s")
        print(f"Attempts JSON : {summary_json}")
        print(f"Summary MD    : {run_root / 'summary.md'}")
        print(f"Summary CSV   : {run_root / 'summary.csv'}")
        return 0
    finally:
        if trace_db is not None:
            trace_db.close()


if __name__ == "__main__":
    sys.exit(main())

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
    from .agents.anthropic import run_anthropic_agent, DEFAULT_SYSTEM_PROMPT as ANTH_SYS
    from .agents.openai import run_openai_agent, DEFAULT_SYSTEM_PROMPT as OAI_SYS
    from . import report as report_mod
except ImportError:
    # Script-style invocation (`python passk.py ...`) — promote the parent
    # package onto sys.path and re-import absolutely.
    sys.path.insert(0, str(HERE.parent.parent))
    from runner.runner import AttemptResult, list_task_dirs, run_attempt        # type: ignore
    from runner.agents.anthropic import run_anthropic_agent, DEFAULT_SYSTEM_PROMPT as ANTH_SYS  # type: ignore
    from runner.agents.openai import run_openai_agent, DEFAULT_SYSTEM_PROMPT as OAI_SYS         # type: ignore
    from runner import report as report_mod                                     # type: ignore


SMOKE_TASKS = ["05", "10", "12"]   # short, easy tasks for cheap end-to-end check


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
    p.add_argument("--harness", action="store_true",
                   help="Enable a system prompt that describes the mock's UI. "
                        "Default: OFF (model sees only the task prompt and screenshots).")
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
    return p.parse_args()


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

    print(f"Run id    : {run_id}")
    print(f"Run dir   : {run_root}")
    print(f"Providers : {', '.join(args.providers)}")
    print(f"Tasks     : {len(tasks)} ({', '.join(tasks) if len(tasks) <= 12 else tasks[0] + '...' + tasks[-1]})")
    print(f"k         : {args.k}")
    print(f"Threshold : final_score >= {args.threshold}")
    print(f"Mock URL  : {args.mock_url}")
    print(f"Harness   : {'on' if args.harness else 'off'}")
    print(f"Prompt    : {args.prompt_mode}"
          + ("  (⚠ includes step-by-step solution)" if args.prompt_mode == "full" else ""))
    print()

    # Build the harness system prompt per provider. ``None`` = no harness.
    harness_enabled = args.harness

    all_attempts: list[AttemptResult] = []
    t0 = time.time()

    common_kwargs = {
        "step_cap": args.step_cap,
        "turn_delay_s": args.turn_delay_s,
        "max_retries": args.max_retries,
    }
    for provider in args.providers:
        if provider == "anthropic":
            agent_runner = run_anthropic_agent
            agent_kwargs = {
                "model": args.anthropic_model,
                "keep_screenshots": args.keep_screenshots,
                **common_kwargs,
            }
            sys_prompt = (ANTH_SYS.format(w=1280, h=800) if harness_enabled else None)
        else:
            agent_runner = run_openai_agent
            agent_kwargs = {"model": args.openai_model, **common_kwargs}
            sys_prompt = (OAI_SYS if harness_enabled else None)

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
                        harness=harness_enabled,
                        system_prompt=sys_prompt,
                    )
                except Exception as exc:
                    print(f"{label} CRASH: {exc}", flush=True)
                    continue
                all_attempts.append(res)
                dt = time.time() - t_a
                pass_mark = "✓ pass" if res.passed else "✗ fail"
                err = f"  err={res.error}" if res.error else ""
                print(f"{label} {pass_mark}  score={res.final_score:.3f}/{res.max_score:.1f}  "
                      f"turns={res.turns}  stop={res.stop_reason}  {dt:.1f}s{err}", flush=True)

    summary_json = run_root / "attempts.json"
    summary_json.write_text(
        json.dumps([dataclasses.asdict(a) for a in all_attempts], indent=2),
        encoding="utf-8")

    report_mod.write_reports(all_attempts, run_root, threshold=args.threshold, k=args.k)

    print()
    print(f"Run complete in {time.time() - t0:.1f}s")
    print(f"Attempts JSON : {summary_json}")
    print(f"Summary MD    : {run_root / 'summary.md'}")
    print(f"Summary CSV   : {run_root / 'summary.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

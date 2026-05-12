"""Single-attempt orchestration: spin browser, run agent, scrape log, score."""
from __future__ import annotations

import dataclasses
import importlib.util
import json
import sys
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

APP_ROOT = Path(__file__).resolve().parents[2]      # apps/figma/
DELIVERY_DIR = APP_ROOT / "delivery-1"

# Make `from verifier.* import *` work for delivery-1 task modules.
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

from .agents.base import AgentResult        # noqa: E402
from .browser import DISPLAY_HEIGHT, DISPLAY_WIDTH, launch_browser   # noqa: E402
from .env import (                          # noqa: E402
    estimate_cost_usd,
    harness_git_info,
    python_argv,
    sdk_versions,
)


@dataclass
class AttemptResult:
    task_id: str
    provider: str
    model: str
    final_score: float
    base_score: float
    max_score: float
    efficiency: float
    passed: bool
    turns: int
    stop_reason: str
    error: str | None
    log_path: str
    score_path: str
    trajectory_path: str
    usage: dict[str, Any] = field(default_factory=dict)
    cost_estimate: dict[str, Any] = field(default_factory=dict)
    elapsed_s: float = 0.0


def list_task_dirs() -> list[Path]:
    return sorted(p for p in DELIVERY_DIR.glob("task_*") if (p / "verifier.py").is_file())


def resolve_task(name: str) -> Path:
    dirs = list_task_dirs()
    target = f"task_{name.zfill(2)}" if name.isdigit() else name
    for d in dirs:
        if d.name == target:
            return d
    raise SystemExit(f"No task matching '{name}'")


def load_task(task_dir: Path):
    verifier_py = task_dir / "verifier.py"
    spec = importlib.util.spec_from_file_location(f"delivery_{task_dir.name}", verifier_py)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Cannot load {verifier_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.task


PROMPT_MODES = ("bare", "description", "full")


def read_prompt(task_dir: Path) -> str:
    """Whole prompt.md verbatim. Kept for back-compat / ``full`` mode."""
    prompt_md = task_dir / "prompt.md"
    return prompt_md.read_text(encoding="utf-8") if prompt_md.is_file() else ""


def _split_sections(md: str) -> tuple[str, dict[str, str]]:
    """Return (h1_title_line, {section_name_lower: body}). Sections are split
    on ``## `` headers. ``h1_title_line`` is the first ``# ...`` line, if any."""
    lines = md.splitlines()
    title = ""
    sections: dict[str, str] = {}
    current_name: str | None = None
    current_body: list[str] = []

    def _flush() -> None:
        if current_name is not None:
            sections[current_name.strip().lower()] = "\n".join(current_body).strip()

    for line in lines:
        if line.startswith("# ") and not title:
            title = line.strip()
            continue
        if line.startswith("## "):
            _flush()
            current_name = line[3:].strip()
            current_body = []
            continue
        if current_name is not None:
            current_body.append(line)
    _flush()
    return title, sections


def build_task_prompt(task_dir: Path, mode: str) -> str:
    """Render the task prompt the model will see, per ``mode``.

    - ``bare``        Simplified prompt body only (no title, no headers)
    - ``description`` Thorough description body only (no title, no headers) — DEFAULT
    - ``full``        the entire prompt.md verbatim
    """
    if mode not in PROMPT_MODES:
        raise SystemExit(f"Unknown --prompt-mode {mode!r}; choose from {PROMPT_MODES}")
    md = read_prompt(task_dir)
    if not md:
        return ""

    if mode == "full":
        return md.strip()

    _title, sections = _split_sections(md)
    if mode == "bare":
        body = sections.get("simplified prompt", "")
        # The simplified prompt is conventionally a markdown blockquote.
        # Strip the leading "> " so the model sees plain text.
        lines = [l[2:] if l.startswith("> ") else l.lstrip("> ") if l.startswith(">") else l
                 for l in body.splitlines()]
        return "\n".join(lines).strip()
    # description
    return sections.get("thorough description", "").strip()


def score_log(task, log_path: Path):
    from verifier.loader import load_log
    from verifier.types import TaskResult

    log = load_log(str(log_path))
    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)
    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)
    return TaskResult(
        task_id=task.id,
        log_path=str(log_path),
        rubrics=rubric_results,
        base_score=base_score,
        efficiency=efficiency,
        final_score=final_score,
    )


def _zero_result(task, log_path: Path, reason: str):
    from verifier.types import CheckResult, EfficiencyResult, RubricResult, TaskResult
    rubric_results = []
    for rubric in task.rubrics:
        checks = getattr(rubric, "checks", []) or []
        n = len(checks) if checks else 1
        rubric_results.append(RubricResult(
            name=str(getattr(rubric, "name", "rubric")),
            score=0.0,
            max_score=float(getattr(rubric, "weight", 0.5)),
            checks=[CheckResult(passed=False, score=0.0, max_score=1.0, message=reason) for _ in range(n)],
        ))
    target_turns = int(getattr(task.efficiency, "target_turns", 0) or 0)
    lam = getattr(task.efficiency, "lambda_", 0.0) or 0.0
    eff = EfficiencyResult(multiplier=1.0, actual_turns=0, target_turns=target_turns,
                           lambda_used=float(lam), message=reason)
    return TaskResult(task_id=task.id, log_path=str(log_path),
                      rubrics=rubric_results, base_score=0.0,
                      efficiency=eff, final_score=0.0)


AgentRunner = Callable[..., AgentResult]


def run_attempt(
    *,
    task_id: str,
    provider: str,
    agent_runner: AgentRunner,
    agent_kwargs: dict[str, Any],
    out_dir: Path,
    mock_url: str,
    headless: bool,
    pass_threshold: float,
    progress_prefix: str = "",
    prompt_mode: str = "full",
    system_prompt: str | None = None,
) -> AttemptResult:
    task_dir = resolve_task(task_id)
    task = load_task(task_dir)
    prompt = build_task_prompt(task_dir, prompt_mode)

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "screenshots").mkdir(exist_ok=True)
    log_path = out_dir / "log.json"
    score_path = out_dir / "score.json"
    trajectory_path = out_dir / "trajectory.json"
    meta_path = out_dir / "meta.json"
    outcome_path = out_dir / "outcome.json"
    end_state_path = out_dir / "end_state.json"
    prompt_path = out_dir / "prompt.txt"
    system_prompt_path = out_dir / "system_prompt.txt"

    # Materialize what the model is about to be shown — eagerly, so a
    # killed run still preserves the inputs.
    prompt_path.write_text(prompt, encoding="utf-8")
    # ``system_prompt`` is whatever passk.py resolved from --system-prompt.
    effective_system = system_prompt
    system_prompt_path.write_text(effective_system or "", encoding="utf-8")

    # Pull static endpoint metadata from the matching agent module so the
    # log records the exact request shape (tool type/version, beta header,
    # max_tokens, viewport, etc.) without duplicating constants.
    if provider == "anthropic":
        from .agents.anthropic import describe_endpoint as _describe
    elif provider == "openai":
        from .agents.openai import describe_endpoint as _describe
    elif provider == "openrouter":
        from .agents.openrouter import describe_endpoint as _describe
    else:
        _describe = lambda *_a, **_kw: {}                       # noqa: E731
    endpoint_meta = _describe(**{
        k: v for k, v in agent_kwargs.items()
        if k in ("model", "max_tokens", "keep_screenshots",
                 "turn_delay_s", "max_retries",
                 "coord_clamp", "loop_break")
    })

    started_at = int(time.time() * 1000)
    started_iso = datetime.fromtimestamp(started_at / 1000, tz=timezone.utc).isoformat()
    meta = {
        "task_id": task.id,
        "task_dir": str(task_dir),
        "provider": provider,
        "model": agent_kwargs.get("model", "?"),
        "endpoint": endpoint_meta,
        "prompt_mode": prompt_mode,
        "prompt_chars": len(prompt),
        "system_prompt_chars": len(effective_system or ""),
        "block_keyboard": not bool(agent_kwargs.get("allow_keyboard", True)),
        "step_cap": agent_kwargs.get("step_cap", None),
        "mock_url": mock_url,
        "headless": headless,
        "viewport": {
            "width": DISPLAY_WIDTH,
            "height": DISPLAY_HEIGHT,
            "device_scale_factor": 1,
        },
        "pass_threshold": pass_threshold,
        "started_at": started_at,
        "started_at_iso": started_iso,
        "harness_git": harness_git_info(),
        "sdk_versions": sdk_versions(),
        "argv": python_argv(),
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    error: str | None = None
    agent_res: AgentResult | None = None
    log_payload: dict | None = None

    full_agent_kwargs = dict(agent_kwargs)
    full_agent_kwargs["system_prompt"] = effective_system
    full_agent_kwargs["attempt_dir"] = out_dir

    fixture_dict = None
    if hasattr(task, "fixture") and task.fixture is not None:
        from dataclasses import asdict as _fixture_asdict
        fixture_dict = _fixture_asdict(task.fixture)

    try:
        with launch_browser(mock_url, headless=headless) as session:
            if fixture_dict is not None:
                if not session.load_fixture(fixture_dict):
                    error = "fixture injection failed"
            agent_res = agent_runner(session, prompt, progress_prefix=progress_prefix, **full_agent_kwargs)
            try:
                log_payload = session.scrape_log()
            except Exception as exc:
                error = f"log scrape failed: {exc}"
    except Exception as exc:
        error = f"browser/agent failure: {exc}"

    if log_payload is not None:
        log_path.write_text(json.dumps(log_payload, indent=2), encoding="utf-8")
        end_state_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "sessionId": log_payload.get("sessionId", ""),
                    "exportedAt": log_payload.get("exportedAt", int(time.time() * 1000)),
                    "outcome": log_payload.get("outcome", {}),
                    "raw_event_count": len(log_payload.get("raw", []) or []),
                    "semantic_event_count": len(log_payload.get("semantic", []) or []),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        try:
            result = score_log(task, log_path)
        except Exception as score_exc:
            # Verifier requires outcome.summary / .document — when an agent
            # does nothing useful the mock's log can be incomplete. Fall
            # back to a zero-scored attempt instead of crashing the run.
            score_err = f"score failed: {score_exc}"
            error = score_err if not error else f"{error}; {score_err}"
            result = _zero_result(task, log_path, reason=str(score_exc))
    else:
        fallback_ts = int(time.time() * 1000)
        log_path.write_text(json.dumps({
            "schemaVersion": 1, "sessionId": "unavailable",
            "exportedAt": fallback_ts,
            "raw": [], "semantic": [], "outcome": {},
        }, indent=2), encoding="utf-8")
        end_state_path.write_text(
            json.dumps(
                {
                    "schemaVersion": 1,
                    "sessionId": "unavailable",
                    "exportedAt": fallback_ts,
                    "outcome": {},
                    "raw_event_count": 0,
                    "semantic_event_count": 0,
                    "status": "no_log",
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        result = _zero_result(task, log_path, reason=error or "no log")

    score_path.write_text(json.dumps(dataclasses.asdict(result), indent=2), encoding="utf-8")

    if agent_res is not None:
        trajectory_path.write_text(json.dumps({
            "provider": agent_res.provider,
            "model": agent_res.model,
            "turns": agent_res.turns,
            "finished": agent_res.finished,
            "stop_reason": agent_res.stop_reason,
            "error": agent_res.error,
            "usage": agent_res.usage,
            "trajectory": [asdict(s) for s in agent_res.trajectory],
        }, indent=2), encoding="utf-8")
    else:
        trajectory_path.write_text(json.dumps({"error": error or "agent did not run"}, indent=2),
                                   encoding="utf-8")

    max_base = float(sum(r.max_score for r in result.rubrics))

    # Final outcome blob — written after scoring so a researcher reading
    # the attempt dir later has end-to-end metadata without parsing
    # multiple files.
    ended_at = int(time.time() * 1000)
    usage = (agent_res.usage if agent_res else {}) or {}
    cost = estimate_cost_usd(
        meta["model"],
        usage.get("input_tokens", 0) or 0,
        usage.get("output_tokens", 0) or 0,
    )
    outcome_blob = {
        "task_id": task.id,
        "provider": provider,
        "model": meta["model"],
        "started_at": started_at,
        "ended_at": ended_at,
        "ended_at_iso": datetime.fromtimestamp(ended_at / 1000, tz=timezone.utc).isoformat(),
        "elapsed_s": round((ended_at - started_at) / 1000, 2),
        "turns": (agent_res.turns if agent_res else 0),
        "stop_reason": (agent_res.stop_reason if agent_res else "error"),
        "finished": (agent_res.finished if agent_res else False),
        "error": (error or (agent_res.error if agent_res else None)),
        "usage": usage,
        "cost_estimate": cost,
        "score": {
            "final": result.final_score,
            "base": result.base_score,
            "max": max_base,
            "efficiency": result.efficiency.multiplier,
            "passed": result.final_score >= pass_threshold,
            "threshold": pass_threshold,
        },
        "log_session_id": (log_payload or {}).get("sessionId") if log_payload else None,
    }
    outcome_path.write_text(json.dumps(outcome_blob, indent=2), encoding="utf-8")

    return AttemptResult(
        task_id=task.id,
        provider=provider,
        model=(agent_res.model if agent_res else agent_kwargs.get("model", "?")),
        final_score=result.final_score,
        base_score=result.base_score,
        max_score=max_base,
        efficiency=result.efficiency.multiplier,
        passed=result.final_score >= pass_threshold,
        turns=(agent_res.turns if agent_res else 0),
        stop_reason=(agent_res.stop_reason if agent_res else "error"),
        error=(error or (agent_res.error if agent_res else None)),
        log_path=str(log_path),
        score_path=str(score_path),
        trajectory_path=str(trajectory_path),
        usage=usage,
        cost_estimate=cost,
        elapsed_s=outcome_blob["elapsed_s"],
    )

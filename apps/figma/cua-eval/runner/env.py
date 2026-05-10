"""Capture environment + harness metadata so a researcher reading the
logs later can reconstruct how a run was produced."""
from __future__ import annotations

import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

# Pricing table for cost estimates ($ per million tokens, input / output).
# Update when public pricing changes; values are best-effort and meant for
# rough budgeting, not billing.
PRICES_USD_PER_MTOK: dict[str, tuple[float, float]] = {
    # Anthropic
    "claude-sonnet-4-5": (3.0, 15.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-opus-4-5":   (15.0, 75.0),
    "claude-opus-4-6":   (15.0, 75.0),
    "claude-opus-4-7":   (15.0, 75.0),
    "claude-haiku-4-5":  (1.0, 5.0),
    # OpenAI
    "computer-use-preview": (3.0, 12.0),
    # OpenRouter (Qwen via DeepInfra)
    "qwen/qwen3.5-27b": (0.195, 1.56),
}


def _sdk_version(pkg: str) -> str:
    try:
        return version(pkg)
    except PackageNotFoundError:
        return "not-installed"


def sdk_versions() -> dict[str, str]:
    return {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "anthropic": _sdk_version("anthropic"),
        "openai": _sdk_version("openai"),
        "playwright": _sdk_version("playwright"),
    }


def harness_git_info() -> dict[str, str | None]:
    """Best-effort: harness git SHA + branch + dirty flag. Looks at the
    repo containing this file. Returns Nones when run outside a git tree."""
    repo_root = Path(__file__).resolve().parents[4]   # repo root from cua-eval/runner/

    def _git(*args: str) -> str | None:
        try:
            out = subprocess.run(
                ["git", "-C", str(repo_root), *args],
                check=True, capture_output=True, text=True, timeout=2,
            ).stdout.strip()
            return out or None
        except Exception:
            return None

    sha = _git("rev-parse", "HEAD")
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    status = _git("status", "--porcelain")
    return {
        "git_sha": sha,
        "git_branch": branch,
        "git_dirty": bool(status) if status is not None else None,
    }


def estimate_cost_usd(model: str, input_tokens: int, output_tokens: int) -> dict[str, float | str]:
    rates = PRICES_USD_PER_MTOK.get(model)
    if rates is None:
        return {"input_usd": 0.0, "output_usd": 0.0, "total_usd": 0.0,
                "note": f"no public pricing entry for {model!r}; cost is 0"}
    in_rate, out_rate = rates
    in_usd = input_tokens / 1_000_000 * in_rate
    out_usd = output_tokens / 1_000_000 * out_rate
    return {
        "input_usd": round(in_usd, 6),
        "output_usd": round(out_usd, 6),
        "total_usd": round(in_usd + out_usd, 6),
        "input_rate_per_mtok_usd": in_rate,
        "output_rate_per_mtok_usd": out_rate,
    }


def python_argv() -> list[str]:
    return list(sys.argv)

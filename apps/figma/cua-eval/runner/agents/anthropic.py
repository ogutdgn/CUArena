"""Claude computer-use agent loop.

Uses the Messages API + `computer_20250124` tool. Each turn:
  1. Send the running message history to the model.
  2. For each `tool_use` block whose name == "computer", execute the action
     against the browser and append a `tool_result` content block with the
     fresh screenshot.
  3. Stop when the model returns no `tool_use` (final message) or the step
     cap is hit.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from anthropic import Anthropic

from ..browser import DISPLAY_HEIGHT, DISPLAY_WIDTH, BrowserSession
from .base import AgentResult, AgentTrajectoryStep


# Anthropic's computer-use tool/beta pairs as documented at
# https://platform.claude.com/docs/en/agents-and-tools/tool-use/computer-use-tool
#
# The newer ``computer_20251124`` / ``computer-use-2025-11-24`` pair is for
# Claude Opus 4.7 / 4.6 / 4.5 and Sonnet 4.6, and adds the ``zoom`` action.
# The older ``computer_20250124`` / ``computer-use-2025-01-24`` pair is for
# Sonnet 4.5, Haiku 4.5, Opus 4.1, Sonnet 4, Opus 4, and Sonnet 3.7.
NEW_TOOL = ("computer_20251124", "computer-use-2025-11-24")
OLD_TOOL = ("computer_20250124", "computer-use-2025-01-24")

# Substring → tool pair. First match wins; ordering matters because
# "claude-opus-4-1" is a substring of nothing else, but "opus-4-" matches
# 4.5/4.6/4.7 too, so we list 4-1 before the broader prefix.
_MODEL_TOOL_TABLE: list[tuple[str, tuple[str, str]]] = [
    # Opus 4.1 still uses the old tool — match it before the broader opus-4 rule.
    ("claude-opus-4-1", OLD_TOOL),
    # New tool: Opus 4.5 / 4.6 / 4.7 and Sonnet 4.6.
    ("claude-opus-4-5", NEW_TOOL),
    ("claude-opus-4-6", NEW_TOOL),
    ("claude-opus-4-7", NEW_TOOL),
    ("claude-sonnet-4-6", NEW_TOOL),
    # Old tool: everyone else with computer-use support.
    ("claude-sonnet-4-5", OLD_TOOL),
    ("claude-haiku-4-5", OLD_TOOL),
    ("claude-sonnet-4", OLD_TOOL),         # plain "sonnet 4"
    ("claude-opus-4", OLD_TOOL),           # plain "opus 4"
    ("claude-3-7-sonnet", OLD_TOOL),
]


def _tool_version_for_model(model: str) -> tuple[str, str]:
    """Return the (tool_type, beta_header) for ``model``, per Anthropic's
    docs. Falls back to the older pair for unknown models — the API will
    return a clear 400 if that's wrong."""
    m = model.lower()
    for needle, pair in _MODEL_TOOL_TABLE:
        if m.startswith(needle):
            return pair
    return OLD_TOOL


def describe_endpoint(model: str, *, max_tokens: int = 4096,
                      keep_screenshots: int = 3, turn_delay_s: float = 0.0,
                      max_retries: int = 5) -> dict[str, Any]:
    """Static metadata about how this agent calls the API. Captured into
    meta.json so a researcher reading the logs later knows exactly what
    request shape produced the trajectory."""
    tool_type, beta = _tool_version_for_model(model)
    return {
        "provider": "anthropic",
        "model": model,
        "endpoint": "messages.create",
        "tool": {
            "type": tool_type,
            "name": "computer",
            "display_width_px": DISPLAY_WIDTH,
            "display_height_px": DISPLAY_HEIGHT,
            "display_number": 1,
        },
        "beta_headers": [beta],
        "max_tokens": max_tokens,
        "keep_screenshots": keep_screenshots,
        "turn_delay_s": turn_delay_s,
        "max_retries": max_retries,
    }


# Always sent. Hard environment constraint — the figma mock does NOT
# accept keyboard input through computer-use; only mouse actions actually
# affect the canvas. Without this note the model burns turns trying to
# type names, use shortcuts, etc.
MOUSE_ONLY_NOTE = """ENVIRONMENT CONSTRAINT — MOUSE ONLY:
The browser this agent controls does NOT accept keyboard input. Pretend the keyboard is unplugged.

Use ONLY these mouse actions:
- screenshot, mouse_move, cursor_position
- left_click, right_click, middle_click, double_click, triple_click
- left_click_drag, left_mouse_down, left_mouse_up
- scroll, wait

Do NOT use the `type`, `key`, or `hold_key` actions — they have NO effect in this environment.
If a task seems to require typing, a keyboard shortcut, or pressing Enter/Escape, find a mouse-only path (click the matching UI button or menu item instead). Modifier-clicks are allowed via the `text` parameter on left_click/scroll (e.g. shift, ctrl, alt, super).
"""


# Optional UI-explainer prompt — only sent when --harness is on. Layered
# on top of MOUSE_ONLY_NOTE.
DEFAULT_SYSTEM_PROMPT = """You are an autonomous computer-use agent operating a Figma design mock in a browser.

You will be given a task. Use the computer tool to complete the task by clicking and dragging in the canvas. The viewport is {w}x{h}.

Guidelines:
- Take a screenshot first to see the UI.
- The left panel has shape tools (rectangle, ellipse, polygon, etc.). Click a tool, then drag on the canvas to create a shape.
- The right panel shows properties of the selected layer (fill, stroke, position, size, corner radius, etc.).
- Work efficiently — fewer turns means a higher score multiplier.
- When you believe the task is complete, stop calling the computer tool and reply with a short summary.
"""


def _action_to_text(action: dict[str, Any]) -> str:
    a = action.get("action", "?")
    extras = {k: v for k, v in action.items() if k != "action"}
    return f"{a} {extras}" if extras else a


def _execute(session: BrowserSession, action: dict[str, Any]) -> dict[str, Any]:
    """Execute one Anthropic computer action. Returns a tool_result content
    list (always with a screenshot)."""
    name = action.get("action")
    coord = action.get("coordinate") or [0, 0]
    x, y = int(coord[0]), int(coord[1])

    try:
        if name == "screenshot":
            pass
        elif name == "left_click":
            session.click(x, y, "left")
        elif name == "right_click":
            session.click(x, y, "right")
        elif name == "middle_click":
            session.click(x, y, "middle")
        elif name == "double_click":
            session.double_click(x, y)
        elif name == "triple_click":
            session.click(x, y, "left", click_count=3)
        elif name == "mouse_move":
            session.move(x, y)
        elif name == "left_click_drag":
            start = action.get("start_coordinate") or coord
            session.drag([(int(start[0]), int(start[1])), (x, y)])
        elif name == "left_mouse_down":
            session.page.mouse.move(x, y)
            session.page.mouse.down()
        elif name == "left_mouse_up":
            session.page.mouse.move(x, y)
            session.page.mouse.up()
        elif name in ("type", "key", "hold_key"):
            # Hard environment constraint — keyboard input is disabled in
            # this harness. Don't actually press; return a text message in
            # the tool_result so the model gets explicit feedback that
            # this action did nothing and stops repeating it.
            attempted = action.get("text", "")
            session.wait(50)
            shot = session.screenshot_b64()
            return [
                {"type": "text",
                 "text": (f"BLOCKED: keyboard action '{name}' is disabled in this environment. "
                          f"Attempted text/keys: {attempted!r}. Use mouse-only actions instead "
                          f"(left_click, left_click_drag, scroll, etc.). The screen is unchanged.")},
                {"type": "image",
                 "source": {"type": "base64", "media_type": "image/png", "data": shot}},
            ]
        elif name == "scroll":
            direction = action.get("scroll_direction", "down")
            amount = int(action.get("scroll_amount", 3)) * 100
            dx, dy = 0, 0
            if direction == "down": dy = amount
            elif direction == "up": dy = -amount
            elif direction == "right": dx = amount
            elif direction == "left": dx = -amount
            session.scroll(x, y, dx, dy)
        elif name == "wait":
            session.wait(int(float(action.get("duration", 1)) * 1000))
        elif name == "cursor_position":
            pass
        else:
            return [{"type": "text", "text": f"Unknown action: {name}"}]

        # Small settle before screenshot.
        session.wait(150)
        shot = session.screenshot_b64()
        return [{
            "type": "image",
            "source": {"type": "base64", "media_type": "image/png", "data": shot},
        }]
    except Exception as exc:
        return [{"type": "text", "text": f"Action error: {exc}"}]


_KEY_MAP = {
    "ctrl": "Control", "control": "Control",
    "cmd": "Meta", "command": "Meta", "meta": "Meta", "super": "Meta",
    "alt": "Alt", "option": "Alt",
    "shift": "Shift",
    "return": "Enter", "enter": "Enter",
    "escape": "Escape", "esc": "Escape",
    "backspace": "Backspace", "delete": "Delete", "tab": "Tab",
    "space": "Space",
    "up": "ArrowUp", "down": "ArrowDown", "left": "ArrowLeft", "right": "ArrowRight",
}


def _normalize_keys(keys: str) -> str:
    parts = keys.replace(" ", "").split("+")
    out = []
    for p in parts:
        out.append(_KEY_MAP.get(p.lower(), p if len(p) == 1 else p.capitalize()))
    return "+".join(out)


def _save_screenshot(attempt_dir: Path | None, name: str, b64_png: str) -> str | None:
    if attempt_dir is None:
        return None
    shots_dir = attempt_dir / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)
    p = shots_dir / name
    p.write_bytes(base64.standard_b64decode(b64_png))
    return str(p.relative_to(attempt_dir))


def _append_trajectory_jsonl(attempt_dir: Path | None, entry: dict[str, Any]) -> None:
    if attempt_dir is None:
        return
    with (attempt_dir / "trajectory.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


_OMITTED_IMAGE_TEXT = "[screenshot omitted to stay under input token limits]"


def _trim_history_images(messages: list[dict[str, Any]], keep_last: int) -> int:
    """Walk messages newest→oldest, keep the last ``keep_last`` images,
    replace older image blocks with a small text stub. Mutates in place.
    Returns the number of images that were trimmed."""
    if keep_last < 0:
        return 0
    seen = 0
    trimmed = 0

    def _maybe_replace(block: dict[str, Any]) -> dict[str, Any]:
        nonlocal seen, trimmed
        if isinstance(block, dict) and block.get("type") == "image":
            seen += 1
            if seen > keep_last:
                trimmed += 1
                return {"type": "text", "text": _OMITTED_IMAGE_TEXT}
        return block

    for msg in reversed(messages):
        content = msg.get("content")
        if not isinstance(content, list):
            continue
        for i, block in enumerate(content):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                inner = block.get("content")
                if isinstance(inner, list):
                    for j, c in enumerate(inner):
                        inner[j] = _maybe_replace(c)
            else:
                content[i] = _maybe_replace(block)
    return trimmed


def _retry_after_seconds(exc: Exception, default: float) -> float:
    """Best-effort extraction of a retry hint from an Anthropic SDK error.
    Falls back to ``default`` if no header is present."""
    resp = getattr(exc, "response", None)
    headers = getattr(resp, "headers", None) if resp is not None else None
    if headers is not None:
        for name in ("retry-after", "Retry-After",
                     "anthropic-ratelimit-input-tokens-reset"):
            try:
                val = headers.get(name)
            except Exception:
                val = None
            if not val:
                continue
            try:
                # Some headers return seconds, some return absolute timestamps —
                # only treat short integers as seconds.
                v = float(val)
                if 0 < v < 600:
                    return v
            except ValueError:
                pass
    return default


def run_anthropic_agent(
    session: BrowserSession,
    task_prompt: str,
    *,
    model: str = "claude-sonnet-4-5",
    step_cap: int = 60,
    max_tokens: int = 4096,
    progress_prefix: str = "",
    system_prompt: str | None = None,
    attempt_dir: Path | None = None,
    keep_screenshots: int = 3,
    turn_delay_s: float = 0.0,
    max_retries: int = 5,
) -> AgentResult:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return AgentResult(provider="anthropic", model=model, turns=0,
                           finished=False, stop_reason="error",
                           error="ANTHROPIC_API_KEY not set")

    client = Anthropic(api_key=api_key)
    tool_type, beta_header = _tool_version_for_model(model)
    tools = [{
        "type": tool_type,
        "name": "computer",
        "display_width_px": DISPLAY_WIDTH,
        "display_height_px": DISPLAY_HEIGHT,
        "display_number": 1,
    }]
    # ``system_prompt is None`` means "no harness" — the API call simply
    # omits the ``system`` parameter. Callers that want the default harness
    # should pass ``DEFAULT_SYSTEM_PROMPT.format(w=..., h=...)``.
    effective_system = system_prompt

    initial_screenshot = session.screenshot_b64()
    _save_screenshot(attempt_dir, "initial.png", initial_screenshot)
    t_start = time.time()
    _append_trajectory_jsonl(attempt_dir, {
        "turn": -1,
        "phase": "start",
        "elapsed_s": 0.0,
        "task_prompt": task_prompt,
        "system_prompt": effective_system,
        "model": model,
        "screenshot": "screenshots/initial.png",
    })

    messages: list[dict[str, Any]] = [{
        "role": "user",
        "content": [
            {"type": "text", "text": f"Task:\n\n{task_prompt}\n\nHere is the current screen:"},
            {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": initial_screenshot}},
        ],
    }]

    trajectory: list[AgentTrajectoryStep] = []
    usage_total = {"input_tokens": 0, "output_tokens": 0}
    stop_reason = "step_cap"

    for turn in range(step_cap):
        if turn > 0 and turn_delay_s > 0:
            time.sleep(turn_delay_s)

        # Trim old screenshots before sending. Most of the input tokens in a
        # computer-use loop are images; keeping only the last few gives the
        # model the recent context it needs while staying under TPM caps.
        n_trimmed = _trim_history_images(messages, keep_last=keep_screenshots)
        if n_trimmed and turn == 1:
            print(f"{progress_prefix}  trimming history to last {keep_screenshots} screenshots", flush=True)

        api_kwargs: dict[str, Any] = dict(
            model=model,
            max_tokens=max_tokens,
            tools=tools,
            messages=messages,
            extra_headers={"anthropic-beta": beta_header},
        )
        if effective_system:
            api_kwargs["system"] = effective_system

        # Retry with exponential backoff on rate limits / 5xx.
        resp = None
        last_exc: Exception | None = None
        for attempt_idx in range(max_retries + 1):
            try:
                resp = client.messages.create(**api_kwargs)
                break
            except Exception as exc:
                last_exc = exc
                msg = str(exc)
                low = msg.lower()
                is_429 = "429" in msg or "rate_limit" in low
                is_overloaded = "overloaded" in low or "529" in msg
                is_5xx = any(code in msg for code in ("500", "502", "503", "504"))
                if not (is_429 or is_overloaded or is_5xx) or attempt_idx == max_retries:
                    break
                wait = _retry_after_seconds(exc, default=min(60.0, 5.0 * (2 ** attempt_idx)))
                kind = "429 rate-limit" if is_429 else ("529 overloaded" if is_overloaded else "5xx")
                # Show the first ~200 chars of the actual error so 429s
                # (your TPM cap, slow down) can be told apart from 529s
                # (Anthropic overloaded, just wait).
                snippet = msg.replace("\n", " ")[:200]
                print(f"{progress_prefix}  {kind} on turn {turn} "
                      f"(attempt {attempt_idx + 1}/{max_retries + 1}); sleeping {wait:.1f}s :: {snippet}",
                      flush=True)
                time.sleep(wait)

        if resp is None:
            err_str = str(last_exc) if last_exc else "unknown api error"
            print(f"{progress_prefix}  api error on turn {turn}: {err_str}", flush=True)
            _append_trajectory_jsonl(attempt_dir, {
                "turn": turn, "phase": "error", "stop_reason": "error",
                "elapsed_s": round(time.time() - t_start, 2),
                "error": err_str, "usage_total": dict(usage_total),
            })
            return AgentResult(provider="anthropic", model=model, turns=turn,
                               finished=False, stop_reason="error",
                               error=err_str, trajectory=trajectory, usage=usage_total)

        usage_delta = {"input_tokens": 0, "output_tokens": 0}
        u = getattr(resp, "usage", None)
        if u is not None:
            usage_delta["input_tokens"] = getattr(u, "input_tokens", 0) or 0
            usage_delta["output_tokens"] = getattr(u, "output_tokens", 0) or 0
            usage_total["input_tokens"] += usage_delta["input_tokens"]
            usage_total["output_tokens"] += usage_delta["output_tokens"]

        assistant_blocks = [b.model_dump() if hasattr(b, "model_dump") else dict(b)
                            for b in resp.content]
        messages.append({"role": "assistant", "content": assistant_blocks})

        tool_uses = [b for b in assistant_blocks if b.get("type") == "tool_use"]
        text_blocks = [b.get("text", "") for b in assistant_blocks if b.get("type") == "text"]

        if text_blocks:
            head = " | ".join(t.strip().replace("\n", " ") for t in text_blocks if t.strip())
            if head:
                print(f"{progress_prefix}  t{turn:02d} say: {head[:120]}", flush=True)

        if not tool_uses:
            stop_reason = "done"
            if text_blocks:
                trajectory.append(AgentTrajectoryStep(turn=turn, action={"action": "final"}, text="\n".join(text_blocks)))
            print(f"{progress_prefix}  t{turn:02d} done (no tool_use)", flush=True)
            _append_trajectory_jsonl(attempt_dir, {
                "turn": turn,
                "phase": "final",
                "elapsed_s": round(time.time() - t_start, 2),
                "stop_reason": "done",
                "text": "\n".join(text_blocks),
                "actions": [],
                "usage_delta": usage_delta,
                "usage_total": dict(usage_total),
                "screenshot": None,
            })
            break

        tool_results = []
        actions_this_turn: list[dict[str, Any]] = []
        latest_shot_b64: str | None = None
        for tu in tool_uses:
            action = tu.get("input") or {}
            actions_this_turn.append(action)
            trajectory.append(AgentTrajectoryStep(
                turn=turn, action=action, text=_action_to_text(action)))
            print(f"{progress_prefix}  t{turn:02d} act: {_action_to_text(action)[:120]}", flush=True)
            content = _execute(session, action)
            for c in content:
                if isinstance(c, dict) and c.get("type") == "image":
                    latest_shot_b64 = c.get("source", {}).get("data")
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tu.get("id"),
                "content": content,
            })
        messages.append({"role": "user", "content": tool_results})

        shot_path: str | None = None
        if latest_shot_b64 is not None:
            shot_path = _save_screenshot(attempt_dir, f"turn_{turn:02d}.png", latest_shot_b64)

        _append_trajectory_jsonl(attempt_dir, {
            "turn": turn,
            "phase": "step",
            "elapsed_s": round(time.time() - t_start, 2),
            "text": "\n".join(text_blocks),
            "actions": actions_this_turn,
            "usage_delta": usage_delta,
            "usage_total": dict(usage_total),
            "screenshot": shot_path,
        })

    return AgentResult(
        provider="anthropic",
        model=model,
        turns=len(trajectory),
        finished=stop_reason == "done",
        stop_reason=stop_reason,
        trajectory=trajectory,
        usage=usage_total,
    )

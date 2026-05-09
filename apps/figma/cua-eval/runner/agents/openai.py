"""OpenAI computer-use-preview agent loop (Responses API).

Each turn the model returns one or more output items. We execute every
`computer_call`, take a screenshot, and reply with a `computer_call_output`
chained via `previous_response_id`. Stop when the response has no
`computer_call` items.
"""
from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from ..browser import DISPLAY_HEIGHT, DISPLAY_WIDTH, BrowserSession
from .base import AgentResult, AgentTrajectoryStep


def describe_endpoint(model: str, *, turn_delay_s: float = 0.0,
                      max_retries: int = 5) -> dict[str, Any]:
    """Static metadata about how this agent calls the API. Captured into
    meta.json so a researcher reading the logs later knows exactly what
    request shape produced the trajectory."""
    return {
        "provider": "openai",
        "model": model,
        "endpoint": "responses.create",
        "tool": {
            "type": "computer_use_preview",
            "display_width": DISPLAY_WIDTH,
            "display_height": DISPLAY_HEIGHT,
            "environment": "browser",
        },
        "truncation": "auto",
        "context_carry": "previous_response_id",
        "turn_delay_s": turn_delay_s,
        "max_retries": max_retries,
    }


# Always sent. Hard environment constraint — see anthropic.py for context.
MOUSE_ONLY_NOTE = """ENVIRONMENT CONSTRAINT — MOUSE ONLY:
The browser this agent controls does NOT accept keyboard input. Pretend the keyboard is unplugged.

Use ONLY these mouse actions:
- screenshot, move
- click (left/right/middle), double_click
- drag, scroll, wait

Do NOT use the `type` or `keypress` actions — they have NO effect in this environment.
If a task seems to require typing, a keyboard shortcut, or pressing Enter/Escape, find a mouse-only path (click the matching UI button or menu item instead).
"""


# Optional UI-explainer prompt — only sent when --harness is on.
DEFAULT_SYSTEM_PROMPT = (
    "You are an autonomous computer-use agent operating a Figma design mock in a browser. "
    "Use the computer tool to complete the task by clicking and dragging in the canvas. "
    f"Viewport is {DISPLAY_WIDTH}x{DISPLAY_HEIGHT}. "
    "The left panel has shape tools; the right panel shows properties of the selected layer. "
    "Work efficiently — fewer turns yields a higher score multiplier. "
    "When the task is complete, stop calling the tool and reply with a short summary."
)


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


_KEY_MAP = {
    "CTRL": "Control", "CONTROL": "Control",
    "CMD": "Meta", "COMMAND": "Meta", "META": "Meta",
    "ALT": "Alt", "OPTION": "Alt",
    "SHIFT": "Shift",
    "RETURN": "Enter", "ENTER": "Enter",
    "ESC": "Escape", "ESCAPE": "Escape",
    "BACKSPACE": "Backspace", "DELETE": "Delete", "TAB": "Tab",
    "SPACE": "Space",
    "UP": "ArrowUp", "DOWN": "ArrowDown", "LEFT": "ArrowLeft", "RIGHT": "ArrowRight",
}


def _normalize_key(k: str) -> str:
    return _KEY_MAP.get(k.upper(), k if len(k) == 1 else k.capitalize())


KEYBOARD_ACTIONS = ("type", "keypress")


def _execute(session: BrowserSession, action: dict[str, Any]) -> bool:
    """Execute one OpenAI computer action. Returns ``True`` if the action
    was a blocked keyboard action (no-op'd), ``False`` otherwise. The
    caller uses the flag to attach a feedback message to the next input."""
    t = action.get("type")
    if t in KEYBOARD_ACTIONS:
        # Hard environment constraint — don't actually press anything.
        return True
    if t == "click":
        session.click(int(action["x"]), int(action["y"]),
                      button=action.get("button", "left"))
    elif t == "double_click":
        session.double_click(int(action["x"]), int(action["y"]))
    elif t == "move":
        session.move(int(action["x"]), int(action["y"]))
    elif t == "drag":
        path = [(int(p["x"]), int(p["y"])) for p in action.get("path", [])]
        session.drag(path)
    elif t == "scroll":
        session.scroll(int(action["x"]), int(action["y"]),
                       int(action.get("scroll_x", 0)),
                       int(action.get("scroll_y", 0)))
    elif t == "wait":
        session.wait(int(action.get("ms", 1000)))
    elif t == "screenshot":
        pass
    # else: unknown — ignored
    return False


def run_openai_agent(
    session: BrowserSession,
    task_prompt: str,
    *,
    model: str = "computer-use-preview",
    step_cap: int = 60,
    progress_prefix: str = "",
    system_prompt: str | None = None,
    attempt_dir: Path | None = None,
    turn_delay_s: float = 0.0,
    max_retries: int = 5,
) -> AgentResult:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return AgentResult(provider="openai", model=model, turns=0,
                           finished=False, stop_reason="error",
                           error="OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)
    tools = [{
        "type": "computer_use_preview",
        "display_width": DISPLAY_WIDTH,
        "display_height": DISPLAY_HEIGHT,
        "environment": "browser",
    }]

    initial_shot = session.screenshot_b64()
    _save_screenshot(attempt_dir, "initial.png", initial_shot)
    t_start = time.time()
    _append_trajectory_jsonl(attempt_dir, {
        "turn": -1,
        "phase": "start",
        "elapsed_s": 0.0,
        "task_prompt": task_prompt,
        "system_prompt": system_prompt,
        "model": model,
        "screenshot": "screenshots/initial.png",
    })

    # The Responses API doesn't take a separate `system` field; the harness
    # prompt rides as a prelude on the first user message when present.
    prelude = (system_prompt + "\n\n") if system_prompt else ""
    initial_input = [{
        "role": "user",
        "content": [
            {"type": "input_text",
             "text": f"{prelude}Task:\n\n{task_prompt}\n\nHere is the current screen:"},
            {"type": "input_image",
             "image_url": f"data:image/png;base64,{initial_shot}"},
        ],
    }]

    trajectory: list[AgentTrajectoryStep] = []
    usage_total = {"input_tokens": 0, "output_tokens": 0}
    stop_reason = "step_cap"
    previous_response_id: str | None = None
    next_input: list[dict[str, Any]] | None = initial_input

    try:
        for turn in range(step_cap):
            if turn > 0 and turn_delay_s > 0:
                time.sleep(turn_delay_s)

            kwargs: dict[str, Any] = {
                "model": model,
                "tools": tools,
                "truncation": "auto",
            }
            if previous_response_id:
                kwargs["previous_response_id"] = previous_response_id
            if next_input is not None:
                kwargs["input"] = next_input

            resp = None
            last_exc: Exception | None = None
            for attempt_idx in range(max_retries + 1):
                try:
                    resp = client.responses.create(**kwargs)
                    break
                except Exception as exc:
                    last_exc = exc
                    msg = str(exc)
                    is_rate = "429" in msg or "rate_limit" in msg.lower()
                    is_5xx = any(c in msg for c in ("500", "502", "503", "504"))
                    if not (is_rate or is_5xx) or attempt_idx == max_retries:
                        break
                    wait = min(60.0, 5.0 * (2 ** attempt_idx))
                    print(f"{progress_prefix}  rate-limit / transient on turn {turn} "
                          f"(attempt {attempt_idx + 1}/{max_retries + 1}); sleeping {wait:.1f}s",
                          flush=True)
                    time.sleep(wait)
            if resp is None:
                raise last_exc if last_exc else RuntimeError("openai api: no response")
            previous_response_id = resp.id

            usage_delta = {"input_tokens": 0, "output_tokens": 0}
            u = getattr(resp, "usage", None)
            if u is not None:
                usage_delta["input_tokens"] = getattr(u, "input_tokens", 0) or 0
                usage_delta["output_tokens"] = getattr(u, "output_tokens", 0) or 0
                usage_total["input_tokens"] += usage_delta["input_tokens"]
                usage_total["output_tokens"] += usage_delta["output_tokens"]

            output_items = [
                item.model_dump() if hasattr(item, "model_dump") else dict(item)
                for item in resp.output
            ]

            calls = [it for it in output_items if it.get("type") == "computer_call"]
            text_chunks = []
            for it in output_items:
                if it.get("type") == "message":
                    for c in it.get("content", []):
                        if c.get("type") == "output_text":
                            text_chunks.append(c.get("text", ""))

            if text_chunks:
                head = " | ".join(t.strip().replace("\n", " ") for t in text_chunks if t.strip())
                if head:
                    print(f"{progress_prefix}  t{turn:02d} say: {head[:120]}", flush=True)

            if not calls:
                stop_reason = "done"
                if text_chunks:
                    trajectory.append(AgentTrajectoryStep(
                        turn=turn, action={"type": "final"}, text="\n".join(text_chunks)))
                print(f"{progress_prefix}  t{turn:02d} done (no computer_call)", flush=True)
                _append_trajectory_jsonl(attempt_dir, {
                    "turn": turn, "phase": "final",
                    "elapsed_s": round(time.time() - t_start, 2),
                    "stop_reason": "done",
                    "text": "\n".join(text_chunks),
                    "actions": [],
                    "usage_delta": usage_delta,
                    "usage_total": dict(usage_total),
                    "screenshot": None,
                })
                break

            next_input = []
            actions_this_turn: list[dict[str, Any]] = []
            latest_shot: str | None = None
            blocked_attempts: list[dict[str, Any]] = []
            for call in calls:
                action = call.get("action") or {}
                actions_this_turn.append(action)
                trajectory.append(AgentTrajectoryStep(
                    turn=turn, action=action, text=action.get("type", "?")))
                extras = {k: v for k, v in action.items() if k != "type"}
                desc = f"{action.get('type','?')} {extras}" if extras else action.get("type", "?")
                blocked = _execute(session, action)
                if blocked:
                    blocked_attempts.append(action)
                    print(f"{progress_prefix}  t{turn:02d} BLOCKED: {desc[:120]}", flush=True)
                else:
                    print(f"{progress_prefix}  t{turn:02d} act: {desc[:120]}", flush=True)
                session.wait(150)
                shot = session.screenshot_b64()
                latest_shot = shot
                acknowledged = call.get("pending_safety_checks") or []
                next_input.append({
                    "type": "computer_call_output",
                    "call_id": call.get("call_id"),
                    "acknowledged_safety_checks": acknowledged,
                    "output": {
                        "type": "computer_screenshot",
                        "image_url": f"data:image/png;base64,{shot}",
                    },
                })

            if blocked_attempts:
                # The Responses API doesn't surface text via computer_call_output,
                # so attach a separate user message item right after it.
                detail = "; ".join(
                    f"{a.get('type')}={a.get('text') or a.get('keys')}"
                    for a in blocked_attempts
                )
                next_input.append({
                    "role": "user",
                    "content": [{
                        "type": "input_text",
                        "text": (
                            f"BLOCKED: keyboard actions were intercepted and did NOT execute "
                            f"({detail}). The keyboard is disabled in this environment — use "
                            f"only mouse actions (click, double_click, drag, scroll). "
                            f"The screen is unchanged."),
                    }],
                })

            shot_path = _save_screenshot(attempt_dir, f"turn_{turn:02d}.png", latest_shot) if latest_shot else None
            _append_trajectory_jsonl(attempt_dir, {
                "turn": turn, "phase": "step",
                "elapsed_s": round(time.time() - t_start, 2),
                "text": "\n".join(text_chunks),
                "actions": actions_this_turn,
                "usage_delta": usage_delta,
                "usage_total": dict(usage_total),
                "screenshot": shot_path,
            })
    except Exception as exc:
        _append_trajectory_jsonl(attempt_dir, {
            "phase": "error", "stop_reason": "error",
            "elapsed_s": round(time.time() - t_start, 2),
            "error": str(exc), "usage_total": dict(usage_total),
        })
        return AgentResult(provider="openai", model=model, turns=len(trajectory),
                           finished=False, stop_reason="error",
                           error=str(exc), trajectory=trajectory, usage=usage_total)

    return AgentResult(
        provider="openai",
        model=model,
        turns=len(trajectory),
        finished=stop_reason == "done",
        stop_reason=stop_reason,
        trajectory=trajectory,
        usage=usage_total,
    )

"""OpenRouter (chat-completions) computer-use agent loop.

Used for any OpenAI-compatible vision-language model that supports
function calling, accessed through OpenRouter. The model has no native
computer-use tool, so we define a single ``computer_action`` function
and dispatch the model's tool calls against the BrowserSession.

Provider routing notes (verified against ``qwen/qwen3.5-27b``, 2026-05-09):
- Novita rejects ``image_url`` content blocks alongside ``tools``.
- AtlasCloud returns 400 on most tool-call shapes.
- DeepInfra serves vision+tools+function-calling cleanly.

We pin ``provider={"only":["DeepInfra"]}`` so routing is deterministic and
costs/throughput are predictable. ``reasoning={"enabled": False}`` cuts
the hidden chain-of-thought tokens that OpenRouter would otherwise charge
at the output rate.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import time
from pathlib import Path
from typing import Any

from openai import OpenAI

from ..browser import DISPLAY_HEIGHT, DISPLAY_WIDTH, BrowserSession
from .base import AgentResult, AgentTrajectoryStep


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_PROVIDER_PIN = "DeepInfra"


COMPUTER_ACTION_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "computer_action",
        "description": (
            "Perform exactly one action on the browser viewport. Coordinates are "
            f"in pixels within the {DISPLAY_WIDTH}x{DISPLAY_HEIGHT} viewport, "
            "(0,0) at the top-left. Call this once per turn. Use type='done' "
            "when the task is finished."
        ),
        "parameters": {
            "type": "object",
            "required": ["type"],
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["click", "double_click", "move", "drag",
                             "scroll", "type", "keypress", "wait", "done"],
                    "description": (
                        "click/double_click/move/drag: mouse actions. "
                        "scroll: wheel at (x,y) by (scroll_x,scroll_y). "
                        "type: type text. keypress: press a key chord. "
                        "wait: pause ms. done: task complete."
                    ),
                },
                "x": {"type": "integer", "description": "Pixel X."},
                "y": {"type": "integer", "description": "Pixel Y."},
                "button": {"type": "string", "enum": ["left", "right", "middle"]},
                "path": {
                    "type": "array",
                    "items": {"type": "object", "properties": {
                        "x": {"type": "integer"}, "y": {"type": "integer"},
                    }, "required": ["x", "y"]},
                    "description": "drag only: list of {x,y} waypoints from start to end.",
                },
                "scroll_x": {"type": "integer"},
                "scroll_y": {"type": "integer"},
                "text": {"type": "string", "description": "type only: text to type."},
                "keys": {
                    "type": "array", "items": {"type": "string"},
                    "description": "keypress only: e.g. ['Control','a'] for Ctrl+A.",
                },
                "ms": {"type": "integer", "description": "wait only: milliseconds to sleep."},
                "reason": {"type": "string", "description": "Optional one-line rationale."},
            },
        },
    },
}


def describe_endpoint(model: str, *, keep_screenshots: int = 3,
                      turn_delay_s: float = 0.0,
                      max_retries: int = 5,
                      coord_clamp: bool = False,
                      loop_break: bool = False) -> dict[str, Any]:
    """Static metadata recorded into ``meta.json`` so a researcher reading
    the logs later knows exactly what request shape produced the trajectory."""
    return {
        "provider": "openrouter",
        "model": model,
        "endpoint": "chat.completions.create",
        "base_url": OPENROUTER_BASE_URL,
        "tool": {
            "name": COMPUTER_ACTION_TOOL["function"]["name"],
            "type": "function",
            "display_width": DISPLAY_WIDTH,
            "display_height": DISPLAY_HEIGHT,
        },
        "tool_choice": "auto",
        "provider_pin": os.environ.get("OPENROUTER_PROVIDER_PIN", DEFAULT_PROVIDER_PIN),
        "reasoning_enabled": False,
        "context_carry": "client_side_messages",
        "keep_screenshots": keep_screenshots,
        "turn_delay_s": turn_delay_s,
        "max_retries": max_retries,
        "coord_clamp": coord_clamp,
        "loop_break": loop_break,
    }


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


def _coerce_xy(action: dict[str, Any]) -> tuple[int, int]:
    """Extract (x, y) coordinates from a tool-call payload, tolerating the
    common ways smaller models emit them:
      {"x": 100, "y": 200}                    — canonical
      {"x": [100, 200]}                        — packed list under x
      {"x": "[100, 200]"}                      — packed list, JSON-encoded
      {"coordinate": [100, 200]}               — Anthropic-style
      {"position": {"x": 100, "y": 200}}       — nested
    Returns (0, 0) if no coords can be extracted.
    """
    def _to_int(v: Any, default: int = 0) -> int:
        try:
            return int(v)
        except (TypeError, ValueError):
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return default

    x_raw = action.get("x")
    y_raw = action.get("y")

    # Packed list under x: [x, y]
    if isinstance(x_raw, (list, tuple)) and len(x_raw) >= 2 and y_raw is None:
        return _to_int(x_raw[0]), _to_int(x_raw[1])
    if isinstance(x_raw, str) and y_raw is None:
        s = x_raw.strip().lstrip("[(").rstrip("])")
        if "," in s:
            parts = [p.strip() for p in s.split(",")]
            if len(parts) >= 2:
                xi = _to_int(parts[0], default=-1)
                yi = _to_int(parts[1], default=-1)
                if xi >= 0 and yi >= 0:
                    return xi, yi

    # Anthropic-style coordinate: [x, y]
    coord = action.get("coordinate")
    if isinstance(coord, (list, tuple)) and len(coord) >= 2:
        return _to_int(coord[0]), _to_int(coord[1])

    # Nested position
    pos = action.get("position")
    if isinstance(pos, dict):
        return _to_int(pos.get("x")), _to_int(pos.get("y"))

    return _to_int(x_raw), _to_int(y_raw)


def _coerce_path(action: dict[str, Any]) -> list[tuple[int, int]]:
    """Drag path tolerant of:
      [{"x":300,"y":200},{"x":500,"y":400}]              — canonical
      [[300,200],[500,400]]                              — pair-of-pairs
      [{"x":[300,500],"y":[200,400]}]                    — packed start/end (Qwen quirk)
      [{"x":"[300,500]","y":"[200,400]"}]                — packed + JSON-string
    """
    raw = action.get("path") or action.get("waypoints") or []
    if not isinstance(raw, list):
        return []

    def _to_int(v: Any) -> int | None:
        try:
            return int(v)
        except (TypeError, ValueError):
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return None

    def _maybe_unpack(v: Any) -> list[int]:
        if isinstance(v, (list, tuple)):
            ints = [_to_int(x) for x in v]
            return [x for x in ints if x is not None]
        if isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
            except Exception:
                return []
            if isinstance(parsed, (list, tuple)):
                ints = [_to_int(x) for x in parsed]
                return [x for x in ints if x is not None]
        i = _to_int(v)
        return [i] if i is not None else []

    out: list[tuple[int, int]] = []
    for p in raw:
        if isinstance(p, dict) and ("x" in p or "y" in p):
            xs = _maybe_unpack(p.get("x"))
            ys = _maybe_unpack(p.get("y"))
            n = min(len(xs), len(ys))
            if n == 0:
                continue
            for i in range(n):
                out.append((xs[i], ys[i]))
        elif isinstance(p, (list, tuple)) and len(p) >= 2:
            xi, yi = _to_int(p[0]), _to_int(p[1])
            if xi is not None and yi is not None:
                out.append((xi, yi))
    return out


def _execute(session: BrowserSession, action: dict[str, Any], *,
             allow_keyboard: bool = False) -> tuple[bool, bool]:
    """Run one computer_action against the browser.

    Returns ``(blocked, done)``:
      - ``blocked`` is True when a keyboard action was intercepted.
      - ``done`` is True when the model called ``type='done'``.

    Raises on truly malformed input so the caller can log + recover.
    """
    t = action.get("type")
    if t == "done":
        return False, True
    if t in KEYBOARD_ACTIONS and not allow_keyboard:
        return True, False
    if t == "click":
        x, y = _coerce_xy(action)
        session.click(x, y, button=action.get("button", "left"))
    elif t == "double_click":
        x, y = _coerce_xy(action)
        session.double_click(x, y)
    elif t == "move":
        x, y = _coerce_xy(action)
        session.move(x, y)
    elif t == "drag":
        path = _coerce_path(action)
        if len(path) < 2:
            # Some models emit drag with start_xy + end_xy instead of a path.
            x, y = _coerce_xy(action)
            sx = int(action.get("start_x", x))
            sy = int(action.get("start_y", y))
            if (sx, sy) != (x, y):
                path = [(sx, sy), (x, y)]
        if len(path) >= 2:
            session.drag(path)
    elif t == "scroll":
        x, y = _coerce_xy(action)
        try:
            dx = int(action.get("scroll_x", 0))
            dy = int(action.get("scroll_y", 0))
        except (TypeError, ValueError):
            dx, dy = 0, 0
        session.scroll(x, y, dx, dy)
    elif t == "type":
        session.type_text(str(action.get("text", "")))
    elif t == "keypress":
        keys = action.get("keys", []) or []
        chord = "+".join(_normalize_key(k) for k in keys)
        if chord:
            session.key(chord)
    elif t == "wait":
        try:
            ms = int(action.get("ms", 1000))
        except (TypeError, ValueError):
            ms = 1000
        session.wait(ms)
    # else: unknown — ignored (logged at the call site)
    return False, False


_OMITTED_IMAGE_TEXT = "[screenshot omitted to stay under input token limits]"


def _trim_history_images(messages: list[dict[str, Any]], keep_last: int) -> int:
    """Walk messages newest→oldest, keep the last ``keep_last`` images,
    replace older ``image_url`` blocks with a small text stub. Mutates in
    place. Returns the number of images that were trimmed."""
    if keep_last < 0:
        return 0
    seen = 0
    trimmed = 0

    def _maybe_replace(block: dict[str, Any]) -> dict[str, Any]:
        nonlocal seen, trimmed
        if isinstance(block, dict) and block.get("type") == "image_url":
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
            if isinstance(block, dict):
                content[i] = _maybe_replace(block)
    return trimmed


def _retry_after_seconds(exc: Exception, default: float) -> float:
    """Best-effort retry hint extraction from an OpenAI SDK error response."""
    resp = getattr(exc, "response", None)
    headers = getattr(resp, "headers", None) if resp is not None else None
    if headers is not None:
        for name in ("retry-after", "Retry-After"):
            try:
                val = headers.get(name)
            except Exception:
                val = None
            if not val:
                continue
            try:
                v = float(val)
                if 0 < v < 600:
                    return v
            except ValueError:
                pass
    return default


def _parse_tool_arguments(raw: str | dict | None) -> dict[str, Any]:
    """Tool call arguments come back as a JSON-encoded string; some
    upstreams already return a dict. Be permissive."""
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except Exception:
        return {"_raw": str(raw)}


_COORD_ACTION_TYPES = ("click", "double_click", "move", "drag", "scroll")


def _coords_in_viewport(action: dict[str, Any]) -> tuple[bool, tuple[int, int] | None]:
    """For coord-bearing actions, return (in_viewport, parsed_xy).
    For non-coord actions (type/keypress/wait/done), returns (True, None).
    """
    t = action.get("type")
    if t not in _COORD_ACTION_TYPES:
        return True, None
    if t == "drag":
        path = _coerce_path(action)
        if not path:
            return True, None  # malformed; let _execute handle it
        for x, y in path:
            if not (0 <= x <= DISPLAY_WIDTH and 0 <= y <= DISPLAY_HEIGHT):
                return False, (x, y)
        return True, path[0]
    x, y = _coerce_xy(action)
    in_vp = 0 <= x <= DISPLAY_WIDTH and 0 <= y <= DISPLAY_HEIGHT
    return in_vp, (x, y)


def _action_signature(action: dict[str, Any]) -> str:
    """Stable signature for loop detection. Coord actions use parsed coords;
    text/keypress include their payload."""
    t = action.get("type", "?")
    if t in _COORD_ACTION_TYPES:
        if t == "drag":
            path = _coerce_path(action)
            return f"drag:{path}"
        x, y = _coerce_xy(action)
        return f"{t}:{x}:{y}"
    if t == "type":
        return f"type:{action.get('text','')!r}"
    if t == "keypress":
        return f"keypress:{action.get('keys',[])!r}"
    return t


def run_openrouter_agent(
    session: BrowserSession,
    task_prompt: str,
    *,
    model: str = "qwen/qwen3.5-27b",
    step_cap: int = 60,
    max_tokens: int = 1024,
    progress_prefix: str = "",
    system_prompt: str | None = None,
    attempt_dir: Path | None = None,
    keep_screenshots: int = 3,
    turn_delay_s: float = 0.0,
    max_retries: int = 5,
    allow_keyboard: bool = False,
    coord_clamp: bool = False,
    loop_break: bool = False,
) -> AgentResult:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return AgentResult(provider="openrouter", model=model, turns=0,
                           finished=False, stop_reason="error",
                           error="OPENROUTER_API_KEY not set")

    client = OpenAI(api_key=api_key, base_url=OPENROUTER_BASE_URL)

    initial_shot = session.screenshot_b64()
    _save_screenshot(attempt_dir, "initial.png", initial_shot)
    t_start = time.time()
    _append_trajectory_jsonl(attempt_dir, {
        "turn": -1, "phase": "start", "elapsed_s": 0.0,
        "task_prompt": task_prompt,
        "system_prompt": system_prompt,
        "model": model,
        "screenshot": "screenshots/initial.png",
    })

    messages: list[dict[str, Any]] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({
        "role": "user",
        "content": [
            {"type": "text",
             "text": f"Task:\n\n{task_prompt}\n\nHere is the current screen:"},
            {"type": "image_url",
             "image_url": {"url": f"data:image/png;base64,{initial_shot}"}},
        ],
    })

    trajectory: list[AgentTrajectoryStep] = []
    usage_total = {"input_tokens": 0, "output_tokens": 0}
    stop_reason = "step_cap"

    # 27B-specific intervention state.
    initial_shot_hash = hashlib.md5(base64.standard_b64decode(initial_shot)).hexdigest()
    recent_action_sigs: list[str] = []     # used by loop_break
    recent_shot_hashes: list[str] = [initial_shot_hash]
    coord_clamp_count = 0
    loop_break_count = 0
    LOOP_BREAK_ABORT_THRESHOLD = 10        # abort attempt after this many loop_break activations

    # OpenRouter passes provider routing + reasoning controls via
    # ``extra_body`` on the OpenAI SDK. ``reasoning.enabled=False`` actually
    # disables reasoning (vs. ``exclude=True`` which still emits & charges).
    # OPENROUTER_PROVIDER_PIN env var: "auto" (or empty) = let OpenRouter
    # pick; otherwise pin to that provider (e.g. "DeepInfra").
    pin = os.environ.get("OPENROUTER_PROVIDER_PIN", DEFAULT_PROVIDER_PIN)
    extra_body: dict[str, Any] = {"reasoning": {"enabled": False}}
    if pin and pin.lower() != "auto":
        extra_body["provider"] = {"only": [pin]}

    try:
        for turn in range(step_cap):
            if turn > 0 and turn_delay_s > 0:
                time.sleep(turn_delay_s)

            # Loop-break: if the last 3 actions are identical AND the screen
            # hasn't changed across them, inject a "stuck" nudge before the
            # next request. Only fires when explicitly enabled.
            if (loop_break and len(recent_action_sigs) >= 3
                    and recent_action_sigs[-1] == recent_action_sigs[-2] == recent_action_sigs[-3]
                    and len(set(recent_shot_hashes[-3:])) == 1):
                stuck_sig = recent_action_sigs[-1]
                print(f"{progress_prefix}  t{turn:02d} LOOP_BREAK: stuck on {stuck_sig}", flush=True)
                # The most common failure mode we've observed is the model
                # clicking on the canvas trying to "place" a shape rather
                # than dragging to create one. The nudge tells it exactly
                # how to draw and what shortcut keys exist.
                stuck_was_click = stuck_sig.startswith("click:") or stuck_sig.startswith("double_click:")
                draw_hint = (
                    "SHAPES ARE CREATED BY DRAGGING, NOT CLICKING.\n"
                    "To draw a shape:\n"
                    "  1. Select the tool with a keypress: "
                    '{\"type\":\"keypress\",\"keys\":[\"r\"]} for rectangle, '
                    '\"o\" for ellipse, \"f\" for frame, \"t\" for text, \"l\" for line.\n'
                    "  2. DRAG on the canvas (NOT click): "
                    '{\"type\":\"drag\",\"path\":[{\"x\":300,\"y\":200},{\"x\":500,\"y\":400}]}\n'
                    "Clicking on empty canvas does nothing. If you've been clicking, "
                    "switch to drag for the next action.\n"
                ) if stuck_was_click else (
                    "Try a DIFFERENT action type entirely — your current one isn't producing a change.\n"
                )
                messages.append({
                    "role": "user",
                    "content": (
                        f"STUCK: you've performed the same action ({stuck_sig}) 3 times "
                        f"and the screen has NOT CHANGED.\n"
                        f"{draw_hint}"
                        f"DO NOT repeat the same coordinates or action. "
                        f"Look at the screenshot more carefully before your next move."
                    ),
                })
                _append_trajectory_jsonl(attempt_dir, {
                    "turn": turn, "phase": "intervention",
                    "intervention": "loop_break",
                    "stuck_signature": stuck_sig,
                })
                loop_break_count += 1
                # Reset so we don't fire again on the next turn if model still loops.
                recent_action_sigs = recent_action_sigs[-1:]

                # Early-abort: if the model has been nudged this many times
                # without recovering, further turns are unlikely to help and
                # just burn cost. Stop the attempt with a distinct reason
                # so the writeup can distinguish "model gave up" from "ran out
                # of turns" from "model kept looping despite interventions".
                if loop_break_count > LOOP_BREAK_ABORT_THRESHOLD:
                    print(f"{progress_prefix}  t{turn:02d} ABORT: "
                          f"{loop_break_count} loop_breaks > {LOOP_BREAK_ABORT_THRESHOLD} threshold", flush=True)
                    stop_reason = "loop_break_abort"
                    _append_trajectory_jsonl(attempt_dir, {
                        "turn": turn, "phase": "final",
                        "elapsed_s": round(time.time() - t_start, 2),
                        "stop_reason": "loop_break_abort",
                        "loop_break_count": loop_break_count,
                        "usage_total": dict(usage_total),
                    })
                    break

            n_trimmed = _trim_history_images(messages, keep_last=keep_screenshots)
            if n_trimmed and turn == 1:
                print(f"{progress_prefix}  trimming history to last {keep_screenshots} screenshots", flush=True)

            resp = None
            last_exc: Exception | None = None
            for attempt_idx in range(max_retries + 1):
                try:
                    # Per-request timeout prevents a hung socket from
                    # silently freezing a multi-hour run (which happened
                    # on Gate 3 v2 after ~1h). 120s is generous; typical
                    # Qwen3.5-27B responses come back in 1-5s.
                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        tools=[COMPUTER_ACTION_TOOL],
                        tool_choice="auto",
                        max_tokens=max_tokens,
                        temperature=0.0,
                        extra_body=extra_body,
                        timeout=120,
                    )
                    break
                except Exception as exc:
                    last_exc = exc
                    msg = str(exc)
                    low = msg.lower()
                    is_429 = "429" in msg or "rate_limit" in low
                    is_5xx = any(c in msg for c in ("500", "502", "503", "504"))
                    # Also retry on timeouts and transient connection errors —
                    # without this, a hung socket kills the run silently.
                    is_timeout = ("timeout" in low or "timed out" in low
                                  or "APITimeoutError" in msg
                                  or "ReadTimeout" in msg or "ConnectTimeout" in msg)
                    is_conn = ("connection" in low and ("reset" in low or "aborted" in low
                                                         or "refused" in low or "closed" in low))
                    if not (is_429 or is_5xx or is_timeout or is_conn) or attempt_idx == max_retries:
                        break
                    wait = _retry_after_seconds(exc, default=min(60.0, 5.0 * (2 ** attempt_idx)))
                    kind = ("429 rate-limit" if is_429
                            else "5xx" if is_5xx
                            else "timeout" if is_timeout
                            else "conn-error")
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
                return AgentResult(provider="openrouter", model=model, turns=turn,
                                   finished=False, stop_reason="error",
                                   error=err_str, trajectory=trajectory, usage=usage_total)

            usage_delta = {"input_tokens": 0, "output_tokens": 0}
            u = getattr(resp, "usage", None)
            if u is not None:
                usage_delta["input_tokens"] = getattr(u, "prompt_tokens", 0) or 0
                usage_delta["output_tokens"] = getattr(u, "completion_tokens", 0) or 0
                usage_total["input_tokens"] += usage_delta["input_tokens"]
                usage_total["output_tokens"] += usage_delta["output_tokens"]

            choice = resp.choices[0]
            message = choice.message
            assistant_msg: dict[str, Any] = {
                "role": "assistant",
                "content": message.content or "",
            }
            tool_calls_raw = getattr(message, "tool_calls", None) or []
            if tool_calls_raw:
                assistant_msg["tool_calls"] = [
                    {"id": tc.id, "type": "function",
                     "function": {"name": tc.function.name,
                                  "arguments": tc.function.arguments}}
                    for tc in tool_calls_raw
                ]
            messages.append(assistant_msg)

            content_text = (message.content or "").strip()
            if content_text:
                head = content_text.replace("\n", " ")[:120]
                print(f"{progress_prefix}  t{turn:02d} say: {head}", flush=True)

            if not tool_calls_raw:
                stop_reason = "done"
                if content_text:
                    trajectory.append(AgentTrajectoryStep(
                        turn=turn, action={"type": "final"}, text=content_text))
                print(f"{progress_prefix}  t{turn:02d} done (no tool_calls)", flush=True)
                _append_trajectory_jsonl(attempt_dir, {
                    "turn": turn, "phase": "final",
                    "elapsed_s": round(time.time() - t_start, 2),
                    "stop_reason": "done",
                    "text": content_text,
                    "actions": [],
                    "usage_delta": usage_delta,
                    "usage_total": dict(usage_total),
                    "screenshot": None,
                })
                break

            actions_this_turn: list[dict[str, Any]] = []
            latest_shot: str | None = None
            blocked_attempts: list[dict[str, Any]] = []
            done_called = False
            for tc in tool_calls_raw:
                action = _parse_tool_arguments(tc.function.arguments)
                actions_this_turn.append(action)
                trajectory.append(AgentTrajectoryStep(
                    turn=turn, action=action, text=action.get("type", "?")))
                extras = {k: v for k, v in action.items() if k != "type"}
                desc = f"{action.get('type','?')} {extras}" if extras else action.get("type", "?")

                if tc.function.name != "computer_action":
                    print(f"{progress_prefix}  t{turn:02d} UNKNOWN_TOOL: {tc.function.name}", flush=True)
                    messages.append({
                        "role": "tool", "tool_call_id": tc.id,
                        "content": f"unknown tool {tc.function.name!r}; only computer_action is available",
                    })
                    continue

                # Coord-clamp: if enabled, reject actions whose parsed coords
                # fall outside the viewport before they reach Playwright.
                # The model gets a corrective tool_result and a chance to retry.
                if coord_clamp:
                    in_vp, parsed_xy = _coords_in_viewport(action)
                    if not in_vp and parsed_xy is not None:
                        x, y = parsed_xy
                        coord_clamp_count += 1
                        print(f"{progress_prefix}  t{turn:02d} CLAMP_REJECT: ({x}, {y})", flush=True)
                        messages.append({
                            "role": "tool", "tool_call_id": tc.id,
                            "content": (
                                f"REJECTED: your action at ({x}, {y}) is OFF VIEWPORT. "
                                f"The viewport is {DISPLAY_WIDTH}×{DISPLAY_HEIGHT}; valid x∈[0,{DISPLAY_WIDTH}], y∈[0,{DISPLAY_HEIGHT}]. "
                                f"The bottom toolbar is at y≈763. The screen is unchanged. "
                                f"Provide corrected integer coordinates within the viewport."
                            ),
                        })
                        _append_trajectory_jsonl(attempt_dir, {
                            "turn": turn, "phase": "intervention",
                            "intervention": "coord_clamp", "rejected_xy": [x, y],
                        })
                        # Track signature so loop_break can still fire on
                        # repeated rejected actions.
                        recent_action_sigs.append(_action_signature(action))
                        if len(recent_action_sigs) > 5:
                            recent_action_sigs.pop(0)
                        continue

                try:
                    blocked, done = _execute(session, action, allow_keyboard=allow_keyboard)
                except Exception as exec_exc:
                    err = f"{type(exec_exc).__name__}: {exec_exc}"
                    print(f"{progress_prefix}  t{turn:02d} ACTION_ERROR: {desc[:80]} :: {err[:120]}", flush=True)
                    messages.append({
                        "role": "tool", "tool_call_id": tc.id,
                        "content": (
                            f"ACTION_ERROR: {err}. The screen is unchanged. "
                            "Provide a corrected action with separate integer x and y "
                            "fields, e.g. {\"type\":\"click\",\"x\":100,\"y\":200}."),
                    })
                    continue

                if done:
                    done_called = True
                    print(f"{progress_prefix}  t{turn:02d} done (computer_action type=done)", flush=True)
                    messages.append({
                        "role": "tool", "tool_call_id": tc.id,
                        "content": "task marked complete",
                    })
                    continue
                if blocked:
                    blocked_attempts.append(action)
                    print(f"{progress_prefix}  t{turn:02d} BLOCKED: {desc[:120]}", flush=True)
                    messages.append({
                        "role": "tool", "tool_call_id": tc.id,
                        "content": (
                            f"BLOCKED: keyboard action '{action.get('type')}' is disabled "
                            "in this environment. The screen is unchanged. Use mouse-only "
                            "actions (click, double_click, drag, scroll)."),
                    })
                    continue

                print(f"{progress_prefix}  t{turn:02d} act: {desc[:120]}", flush=True)
                session.wait(150)
                shot = session.screenshot_b64()
                latest_shot = shot
                # Tool-result message: brief text confirmation. The new
                # screenshot rides on a follow-up user message so the model
                # can attach attention to it directly.
                messages.append({
                    "role": "tool", "tool_call_id": tc.id,
                    "content": f"executed {action.get('type')}",
                })

                # Track for loop_break: action signature + post-action screenshot hash.
                if loop_break:
                    recent_action_sigs.append(_action_signature(action))
                    if len(recent_action_sigs) > 5:
                        recent_action_sigs.pop(0)
                    shot_hash = hashlib.md5(base64.standard_b64decode(shot)).hexdigest()
                    recent_shot_hashes.append(shot_hash)
                    if len(recent_shot_hashes) > 5:
                        recent_shot_hashes.pop(0)

            if done_called:
                stop_reason = "done"
                shot_path = (_save_screenshot(attempt_dir, f"turn_{turn:02d}.png", latest_shot)
                             if latest_shot else None)
                _append_trajectory_jsonl(attempt_dir, {
                    "turn": turn, "phase": "final",
                    "elapsed_s": round(time.time() - t_start, 2),
                    "stop_reason": "done",
                    "text": content_text,
                    "actions": actions_this_turn,
                    "usage_delta": usage_delta,
                    "usage_total": dict(usage_total),
                    "screenshot": shot_path,
                })
                break

            # Append a single user message with the latest screenshot so the
            # model can react. If everything was blocked, no fresh shot —
            # send a text-only nudge.
            if latest_shot is not None:
                messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": "Updated screen after the action(s) above:"},
                        {"type": "image_url",
                         "image_url": {"url": f"data:image/png;base64,{latest_shot}"}},
                    ],
                })
            elif blocked_attempts:
                messages.append({
                    "role": "user",
                    "content": "Continue with mouse-only actions.",
                })

            shot_path = (_save_screenshot(attempt_dir, f"turn_{turn:02d}.png", latest_shot)
                         if latest_shot else None)
            _append_trajectory_jsonl(attempt_dir, {
                "turn": turn, "phase": "step",
                "elapsed_s": round(time.time() - t_start, 2),
                "text": content_text,
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
        return AgentResult(provider="openrouter", model=model, turns=len(trajectory),
                           finished=False, stop_reason="error",
                           error=str(exc), trajectory=trajectory, usage=usage_total)

    if coord_clamp or loop_break:
        usage_total["coord_clamp_count"] = coord_clamp_count
        usage_total["loop_break_count"] = loop_break_count

    return AgentResult(
        provider="openrouter",
        model=model,
        turns=len(trajectory),
        finished=stop_reason == "done",
        stop_reason=stop_reason,
        trajectory=trajectory,
        usage=usage_total,
    )

#!/usr/bin/env python3
"""
cua_benchmark_runner.py

Run Figma mock tasks with CUA providers (OpenAI + Anthropic), capture session-
scoped logs, and score every episode automatically.

Design goals:
- Minimal local CPU usage by default (single worker / one browser context).
- Deterministic log attribution via explicit session IDs.
- Provider adapters isolated behind a common interface.

Example:
  python3 scripts/cua_benchmark_runner.py \
    --providers openai,anthropic \
    --tasks 01,02 \
    --openai-model computer-use-preview \
    --anthropic-model claude-sonnet-4-5 \
    --max-parallel 1
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import dataclasses
import importlib.util
import json
import os
import re
import sys
import time
import traceback
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

APP_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
DELIVERY_DIR = APP_ROOT / "delivery-1"

sys.path.insert(0, str(APP_ROOT))


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _http_json(
    method: str,
    url: str,
    payload: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float = 90.0,
) -> dict[str, Any]:
    req_headers = {"Content-Type": "application/json"}
    if headers:
        req_headers.update(headers)
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url=url, data=data, headers=req_headers, method=method.upper())
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            if not body:
                return {}
            return json.loads(body)
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode("utf-8")
        except Exception:
            err_body = "<no-body>"
        raise RuntimeError(f"HTTP {e.code} {url}: {err_body}") from e


def _parse_tasks(raw: str) -> list[str]:
    out: list[str] = []
    for chunk in [s.strip() for s in raw.split(",") if s.strip()]:
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            if not a.isdigit() or not b.isdigit():
                raise ValueError(f"Invalid task range: {chunk}")
            for i in range(int(a), int(b) + 1):
                out.append(f"{i:02d}")
        else:
            if chunk.isdigit():
                out.append(f"{int(chunk):02d}")
            else:
                m = re.match(r"^task_(\d+)$", chunk)
                if not m:
                    raise ValueError(f"Invalid task id: {chunk}")
                out.append(f"{int(m.group(1)):02d}")
    # preserve order, drop dups
    seen: set[str] = set()
    uniq: list[str] = []
    for t in out:
        if t not in seen:
            uniq.append(t)
            seen.add(t)
    return uniq


def _resolve_task_dir(task_id_2d: str) -> Path:
    p = DELIVERY_DIR / f"task_{task_id_2d}"
    if not (p / "prompt.md").is_file() or not (p / "verifier.py").is_file():
        raise FileNotFoundError(f"Task folder missing prompt/verifier: {p}")
    return p


def _read_task_prompt(task_dir: Path) -> str:
    # Use full prompt file. Provider-specific instructions can be prepended.
    return (task_dir / "prompt.md").read_text(encoding="utf-8")


def _load_task_object(task_dir: Path):
    verifier_py = task_dir / "verifier.py"
    spec = importlib.util.spec_from_file_location(f"delivery_{task_dir.name}", verifier_py)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load verifier: {verifier_py}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    return mod.task


def _score_log(task_dir: Path, log_path: Path) -> dict[str, Any]:
    # Mirrors scripts/score_log.py semantics while returning a dict for automation.
    from verifier.loader import load_log
    from verifier.types import TaskResult

    task = _load_task_object(task_dir)
    log = load_log(str(log_path))
    rubric_results = [r.run(log) for r in task.rubrics]
    efficiency = task.efficiency.run(log)
    base_score = round(sum(r.score for r in rubric_results), 4)
    final_score = round(base_score * efficiency.multiplier, 4)
    result = TaskResult(
        task_id=task.id,
        log_path=str(log_path),
        rubrics=rubric_results,
        base_score=base_score,
        efficiency=efficiency,
        final_score=final_score,
    )
    return dataclasses.asdict(result)


def _keymap(k: str) -> str:
    # Playwright key names
    m = {
        "ctrl": "Control",
        "control": "Control",
        "cmd": "Meta",
        "command": "Meta",
        "alt": "Alt",
        "shift": "Shift",
        "enter": "Enter",
        "esc": "Escape",
        "space": "Space",
        "tab": "Tab",
        "up": "ArrowUp",
        "down": "ArrowDown",
        "left": "ArrowLeft",
        "right": "ArrowRight",
        "backspace": "Backspace",
        "delete": "Delete",
    }
    lk = k.strip().lower()
    return m.get(lk, k)


@dataclasses.dataclass
class RunnerConfig:
    app_url: str
    task_ids: list[str]
    providers: list[str]
    openai_model: str
    anthropic_model: str
    max_steps: int
    max_parallel: int
    headless: bool
    step_delay_ms: int
    nav_timeout_ms: int
    output_dir: Path
    openai_api_key_env: str
    anthropic_api_key_env: str
    anthropic_tool_version: str
    anthropic_beta: str
    openai_tool_type: str
    width: int
    height: int


@dataclasses.dataclass
class EpisodeResult:
    provider: str
    model: str
    task: str
    status: str
    started_at: str
    finished_at: str
    duration_sec: float
    session_id: str | None
    steps: int
    final_score: float | None
    base_score: float | None
    efficiency_multiplier: float | None
    run_dir: str
    error: str | None


class BrowserHarness:
    def __init__(self, app_url: str, width: int, height: int, headless: bool, step_delay_ms: int, nav_timeout_ms: int):
        self.app_url = app_url
        self.width = width
        self.height = height
        self.headless = headless
        self.step_delay_ms = step_delay_ms
        self.nav_timeout_ms = nav_timeout_ms
        self._pw = None
        self._browser = None
        self._context = None
        self._page = None

    async def __aenter__(self):
        try:
            from playwright.async_api import async_playwright
        except Exception as e:
            raise RuntimeError(
                "playwright is required. Install with:\n"
                "  pip install playwright\n"
                "  playwright install chromium"
            ) from e
        self._pw = await async_playwright().start()
        self._browser = await self._pw.chromium.launch(headless=self.headless)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if self._context is not None:
                await self._context.close()
            if self._browser is not None:
                await self._browser.close()
            if self._pw is not None:
                await self._pw.stop()
        finally:
            self._context = None
            self._browser = None
            self._pw = None

    async def reset(self) -> None:
        if self._browser is None:
            raise RuntimeError("Browser not started")
        if self._context is not None:
            await self._context.close()
        self._context = await self._browser.new_context(viewport={"width": self.width, "height": self.height})
        self._page = await self._context.new_page()
        await self._page.goto(self.app_url, wait_until="domcontentloaded", timeout=self.nav_timeout_ms)
        await self._page.wait_for_timeout(350)

    async def screenshot_b64(self) -> str:
        if self._page is None:
            raise RuntimeError("No active page")
        png = await self._page.screenshot(type="png")
        return base64.b64encode(png).decode("utf-8")

    async def execute_openai_actions(self, actions: list[dict[str, Any]]) -> None:
        for action in actions:
            await self._execute_openai_action(action)
            if self.step_delay_ms > 0:
                await self._page.wait_for_timeout(self.step_delay_ms)  # type: ignore[union-attr]

    async def _with_modifiers(self, keys: list[str], coro):
        if self._page is None:
            raise RuntimeError("No active page")
        for k in keys:
            await self._page.keyboard.down(_keymap(k))
        try:
            return await coro()
        finally:
            for k in reversed(keys):
                await self._page.keyboard.up(_keymap(k))

    async def _execute_openai_action(self, action: dict[str, Any]) -> None:
        if self._page is None:
            raise RuntimeError("No active page")
        t = str(action.get("type", "")).lower()
        if t == "screenshot":
            return
        if t == "wait":
            await self._page.wait_for_timeout(1000)
            return
        if t == "move":
            await self._page.mouse.move(float(action["x"]), float(action["y"]))
            return
        if t == "click":
            x = float(action["x"])
            y = float(action["y"])
            btn = str(action.get("button", "left"))
            keys = [str(k) for k in action.get("keys", [])]

            async def _do():
                await self._page.mouse.click(x, y, button=btn)

            await self._with_modifiers(keys, _do)
            return
        if t == "double_click":
            await self._page.mouse.dblclick(float(action["x"]), float(action["y"]))
            return
        if t == "scroll":
            x = float(action.get("x", self.width // 2))
            y = float(action.get("y", self.height // 2))
            scroll_x = float(action.get("scroll_x", 0))
            scroll_y = float(action.get("scroll_y", 0))
            keys = [str(k) for k in action.get("keys", [])]

            async def _do():
                await self._page.mouse.move(x, y)
                await self._page.evaluate(
                    "(dx, dy) => window.scrollBy({left: dx, top: dy, behavior: 'auto'})",
                    scroll_x,
                    scroll_y,
                )

            await self._with_modifiers(keys, _do)
            return
        if t == "type":
            await self._page.keyboard.type(str(action.get("text", "")))
            return
        if t == "keypress":
            keys = [str(k) for k in action.get("keys", [])]
            if not keys:
                return
            if len(keys) == 1:
                await self._page.keyboard.press(_keymap(keys[0]))
                return
            for k in keys:
                await self._page.keyboard.down(_keymap(k))
            for k in reversed(keys):
                await self._page.keyboard.up(_keymap(k))
            return
        if t == "drag":
            path = action.get("path", [])
            if not path or len(path) < 2:
                return
            p0 = path[0]
            await self._page.mouse.move(float(p0["x"]), float(p0["y"]))
            await self._page.mouse.down()
            for p in path[1:]:
                await self._page.mouse.move(float(p["x"]), float(p["y"]))
            await self._page.mouse.up()
            return
        raise RuntimeError(f"Unsupported OpenAI action: {action}")

    async def execute_anthropic_action(self, action: dict[str, Any]) -> None:
        if self._page is None:
            raise RuntimeError("No active page")
        t = str(action.get("action", "")).lower()
        if t == "screenshot":
            return
        if t == "wait":
            await self._page.wait_for_timeout(1000)
            return
        if t in ("left_click", "right_click", "middle_click", "double_click", "triple_click", "mouse_move"):
            coord = action.get("coordinate") or [self.width // 2, self.height // 2]
            x, y = float(coord[0]), float(coord[1])
            if t == "mouse_move":
                await self._page.mouse.move(x, y)
            elif t == "double_click":
                await self._page.mouse.dblclick(x, y)
            elif t == "triple_click":
                await self._page.mouse.click(x, y, click_count=3)
            else:
                btn = "left"
                if t == "right_click":
                    btn = "right"
                elif t == "middle_click":
                    btn = "middle"
                await self._page.mouse.click(x, y, button=btn)
            return
        if t == "left_click_drag":
            start = action.get("start_coordinate") or action.get("coordinate")
            end = action.get("end_coordinate")
            if not start or not end:
                return
            sx, sy = float(start[0]), float(start[1])
            ex, ey = float(end[0]), float(end[1])
            await self._page.mouse.move(sx, sy)
            await self._page.mouse.down()
            await self._page.mouse.move(ex, ey)
            await self._page.mouse.up()
            return
        if t == "left_mouse_down":
            await self._page.mouse.down(button="left")
            return
        if t == "left_mouse_up":
            await self._page.mouse.up(button="left")
            return
        if t == "type":
            await self._page.keyboard.type(str(action.get("text", "")))
            return
        if t == "key":
            combo = str(action.get("text", "")).strip()
            if not combo:
                return
            parts = [_keymap(p) for p in re.split(r"[+]", combo) if p.strip()]
            if not parts:
                return
            if len(parts) == 1:
                await self._page.keyboard.press(parts[0])
                return
            for p in parts:
                await self._page.keyboard.down(p)
            for p in reversed(parts):
                await self._page.keyboard.up(p)
            return
        if t == "scroll":
            coord = action.get("coordinate") or [self.width // 2, self.height // 2]
            x, y = float(coord[0]), float(coord[1])
            direction = str(action.get("scroll_direction", "down")).lower()
            amount = int(action.get("scroll_amount", 3))
            amount_px = max(1, amount) * 220
            dx, dy = 0, amount_px
            if direction == "up":
                dy = -amount_px
            elif direction == "left":
                dx, dy = -amount_px, 0
            elif direction == "right":
                dx, dy = amount_px, 0
            await self._page.mouse.move(x, y)
            await self._page.evaluate(
                "(sx, sy) => window.scrollBy({left: sx, top: sy, behavior: 'auto'})",
                dx,
                dy,
            )
            return
        raise RuntimeError(f"Unsupported Anthropic action: {action}")


class OpenAIComputerAgent:
    def __init__(self, api_key: str, model: str, tool_type: str, width: int, height: int, max_steps: int):
        self.api_key = api_key
        self.model = model
        self.tool_type = tool_type
        self.width = width
        self.height = height
        self.max_steps = max_steps

    def _tool_def(self) -> dict[str, Any]:
        if self.tool_type == "computer_use_preview":
            return {
                "type": "computer_use_preview",
                "display_width": self.width,
                "display_height": self.height,
                "environment": "browser",
            }
        return {"type": "computer"}

    def _headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.api_key}"}

    async def run_episode(self, harness: BrowserHarness, task_prompt: str, trace_file: Path) -> int:
        steps = 0
        screenshot0 = await harness.screenshot_b64()
        req: dict[str, Any] = {
            "model": self.model,
            "tools": [self._tool_def()],
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are controlling a Figma mock in the browser.\n"
                                "Finish the user task exactly.\n"
                                "Prefer minimal, efficient actions.\n\n"
                                f"TASK:\n{task_prompt}"
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{screenshot0}",
                            "detail": "original",
                        },
                    ],
                }
            ],
            "truncation": "auto",
        }
        if self.tool_type == "computer_use_preview":
            req["reasoning"] = {"summary": "concise"}

        resp = _http_json("POST", "https://api.openai.com/v1/responses", payload=req, headers=self._headers(), timeout=120.0)

        while steps < self.max_steps:
            outputs = resp.get("output", []) or []
            computer_call = next((o for o in outputs if o.get("type") == "computer_call"), None)
            if not computer_call:
                break
            call_id = computer_call.get("call_id")
            if not call_id:
                raise RuntimeError("OpenAI computer_call missing call_id")

            actions = computer_call.get("actions")
            if not isinstance(actions, list):
                # Backward compat with legacy single action.
                single = computer_call.get("action")
                actions = [single] if isinstance(single, dict) else []
            actions = [a for a in actions if isinstance(a, dict)]
            if not actions:
                # No executable action, break to avoid dead-loop.
                break

            await harness.execute_openai_actions(actions)
            steps += len(actions)
            trace_file.parent.mkdir(parents=True, exist_ok=True)
            with open(trace_file, "a", encoding="utf-8") as tf:
                for a in actions:
                    tf.write(json.dumps({"ts": _utc_now(), "provider": "openai", "action": a}) + "\n")

            screenshot_b64 = await harness.screenshot_b64()
            follow = {
                "model": self.model,
                "tools": [self._tool_def()],
                "previous_response_id": resp["id"],
                "input": [
                    {
                        "type": "computer_call_output",
                        "call_id": call_id,
                        "output": {
                            "type": "computer_screenshot",
                            "image_url": f"data:image/png;base64,{screenshot_b64}",
                            "detail": "original",
                        },
                    }
                ],
                "truncation": "auto",
            }
            resp = _http_json("POST", "https://api.openai.com/v1/responses", payload=follow, headers=self._headers(), timeout=120.0)

        return steps


class AnthropicComputerAgent:
    def __init__(
        self,
        api_key: str,
        model: str,
        tool_version: str,
        beta_flag: str,
        width: int,
        height: int,
        max_steps: int,
    ):
        self.api_key = api_key
        self.model = model
        self.tool_version = tool_version
        self.beta_flag = beta_flag
        self.width = width
        self.height = height
        self.max_steps = max_steps

    def _headers(self) -> dict[str, str]:
        return {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "anthropic-beta": self.beta_flag,
        }

    def _tool_def(self) -> dict[str, Any]:
        return {
            "type": f"computer_{self.tool_version}",
            "name": "computer",
            "display_width_px": self.width,
            "display_height_px": self.height,
        }

    async def run_episode(self, harness: BrowserHarness, task_prompt: str, trace_file: Path) -> int:
        steps = 0
        messages: list[dict[str, Any]] = [
            {
                "role": "user",
                "content": (
                    "You are controlling a Figma mock in a browser. "
                    "Complete the task exactly and efficiently.\n\n"
                    f"TASK:\n{task_prompt}"
                ),
            }
        ]

        while steps < self.max_steps:
            req = {
                "model": self.model,
                "max_tokens": 4096,
                "messages": messages,
                "tools": [self._tool_def()],
            }
            resp = _http_json(
                "POST",
                "https://api.anthropic.com/v1/messages",
                payload=req,
                headers=self._headers(),
                timeout=120.0,
            )
            content = resp.get("content", []) or []
            messages.append({"role": "assistant", "content": content})

            tool_uses = [b for b in content if isinstance(b, dict) and b.get("type") == "tool_use"]
            if not tool_uses:
                break

            tool_results: list[dict[str, Any]] = []
            trace_file.parent.mkdir(parents=True, exist_ok=True)

            for block in tool_uses:
                inp = block.get("input", {}) or {}
                if not isinstance(inp, dict):
                    inp = {}
                await harness.execute_anthropic_action(inp)
                steps += 1
                with open(trace_file, "a", encoding="utf-8") as tf:
                    tf.write(json.dumps({"ts": _utc_now(), "provider": "anthropic", "action": inp}) + "\n")

                shot = await harness.screenshot_b64()
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block["id"],
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": shot,
                                },
                            }
                        ],
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        return steps


async def _run_one_episode(
    cfg: RunnerConfig,
    provider: str,
    task_id_2d: str,
    run_root: Path,
) -> EpisodeResult:
    started = time.time()
    started_at = _utc_now()
    task_dir = _resolve_task_dir(task_id_2d)
    task_prompt = _read_task_prompt(task_dir)

    ep_dir = run_root / provider / f"task_{task_id_2d}" / datetime.now().strftime("%Y%m%d_%H%M%S")
    ep_dir.mkdir(parents=True, exist_ok=True)
    (ep_dir / "prompt.md").write_text(task_prompt, encoding="utf-8")

    model = cfg.openai_model if provider == "openai" else cfg.anthropic_model
    session_id: str | None = None
    steps = 0
    final_score = None
    base_score = None
    eff = None
    err = None
    status = "ok"
    trace_file = ep_dir / "actions.jsonl"

    try:
        async with BrowserHarness(
            app_url=cfg.app_url,
            width=cfg.width,
            height=cfg.height,
            headless=cfg.headless,
            step_delay_ms=cfg.step_delay_ms,
            nav_timeout_ms=cfg.nav_timeout_ms,
        ) as harness:
            await harness.reset()

            if provider == "openai":
                api_key = os.getenv(cfg.openai_api_key_env, "").strip()
                if not api_key:
                    raise RuntimeError(f"Missing env var {cfg.openai_api_key_env}")
                agent = OpenAIComputerAgent(
                    api_key=api_key,
                    model=cfg.openai_model,
                    tool_type=cfg.openai_tool_type,
                    width=cfg.width,
                    height=cfg.height,
                    max_steps=cfg.max_steps,
                )
                steps = await agent.run_episode(harness, task_prompt, trace_file)
            elif provider == "anthropic":
                api_key = os.getenv(cfg.anthropic_api_key_env, "").strip()
                if not api_key:
                    raise RuntimeError(f"Missing env var {cfg.anthropic_api_key_env}")
                agent = AnthropicComputerAgent(
                    api_key=api_key,
                    model=cfg.anthropic_model,
                    tool_version=cfg.anthropic_tool_version,
                    beta_flag=cfg.anthropic_beta,
                    width=cfg.width,
                    height=cfg.height,
                    max_steps=cfg.max_steps,
                )
                steps = await agent.run_episode(harness, task_prompt, trace_file)
            else:
                raise RuntimeError(f"Unsupported provider: {provider}")

        # Wait for persist flush (~250ms in app); add margin.
        await asyncio.sleep(0.65)

        status_url = f"{cfg.app_url.rstrip('/')}/dev-log/status"
        s = _http_json("GET", status_url, timeout=20.0)
        session_id = s.get("lastSessionId")
        if not session_id:
            raise RuntimeError(f"No session id from {status_url}: {s}")
        (ep_dir / "status.json").write_text(json.dumps(s, indent=2), encoding="utf-8")

        log_url = f"{cfg.app_url.rstrip('/')}/dev-log?{urllib.parse.urlencode({'sessionId': session_id})}"
        log_obj = _http_json("GET", log_url, timeout=20.0)
        log_path = ep_dir / "log.json"
        log_path.write_text(json.dumps(log_obj, indent=2), encoding="utf-8")

        result = _score_log(task_dir, log_path)
        (ep_dir / "score.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
        final_score = float(result.get("final_score", 0.0))
        base_score = float(result.get("base_score", 0.0))
        eff_obj = result.get("efficiency", {}) or {}
        eff = float(eff_obj.get("multiplier", 1.0))
    except Exception as e:
        status = "error"
        err = f"{e}\n{traceback.format_exc(limit=2)}"
        (ep_dir / "error.txt").write_text(err, encoding="utf-8")

    finished_at = _utc_now()
    duration = round(time.time() - started, 3)
    summary = EpisodeResult(
        provider=provider,
        model=model,
        task=f"task_{task_id_2d}",
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=duration,
        session_id=session_id,
        steps=steps,
        final_score=final_score,
        base_score=base_score,
        efficiency_multiplier=eff,
        run_dir=str(ep_dir),
        error=err,
    )
    (ep_dir / "summary.json").write_text(json.dumps(dataclasses.asdict(summary), indent=2), encoding="utf-8")
    return summary


async def _worker_loop(name: str, cfg: RunnerConfig, q: asyncio.Queue, run_root: Path, summaries: list[EpisodeResult]):
    while True:
        item = await q.get()
        if item is None:
            q.task_done()
            return
        provider, task_id_2d = item
        print(f"[{name}] start provider={provider} task=task_{task_id_2d}")
        res = await _run_one_episode(cfg, provider, task_id_2d, run_root)
        summaries.append(res)
        print(
            f"[{name}] done provider={provider} task=task_{task_id_2d} "
            f"status={res.status} score={res.final_score} session={res.session_id}"
        )
        q.task_done()


def _load_config(args: argparse.Namespace) -> RunnerConfig:
    if args.config:
        cfg_obj = json.loads(Path(args.config).read_text(encoding="utf-8"))
        app_url = cfg_obj.get("app_url", args.app_url)
        providers = cfg_obj.get("providers", args.providers.split(","))
        tasks_raw = cfg_obj.get("tasks", args.tasks)
        if isinstance(tasks_raw, list):
            task_ids = _parse_tasks(",".join(str(x) for x in tasks_raw))
        else:
            task_ids = _parse_tasks(str(tasks_raw))
    else:
        app_url = args.app_url
        providers = [p.strip() for p in args.providers.split(",") if p.strip()]
        task_ids = _parse_tasks(args.tasks)

    out_dir = Path(args.output_dir).expanduser()
    return RunnerConfig(
        app_url=app_url,
        task_ids=task_ids,
        providers=[str(p).strip().lower() for p in providers],
        openai_model=args.openai_model,
        anthropic_model=args.anthropic_model,
        max_steps=args.max_steps,
        max_parallel=max(1, args.max_parallel),
        headless=not args.show_browser,
        step_delay_ms=args.step_delay_ms,
        nav_timeout_ms=args.nav_timeout_ms,
        output_dir=out_dir,
        openai_api_key_env=args.openai_api_key_env,
        anthropic_api_key_env=args.anthropic_api_key_env,
        anthropic_tool_version=args.anthropic_tool_version,
        anthropic_beta=args.anthropic_beta,
        openai_tool_type=args.openai_tool_type,
        width=args.width,
        height=args.height,
    )


def _write_leaderboard(run_root: Path, summaries: list[EpisodeResult]) -> None:
    out_json = run_root / "leaderboard.json"
    out_csv = run_root / "leaderboard.csv"

    rows = [dataclasses.asdict(s) for s in summaries]
    out_json.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    headers = [
        "provider",
        "model",
        "task",
        "status",
        "final_score",
        "base_score",
        "efficiency_multiplier",
        "steps",
        "duration_sec",
        "session_id",
        "run_dir",
        "error",
    ]
    lines = [",".join(headers)]
    for r in rows:
        vals: list[str] = []
        for h in headers:
            v = r.get(h)
            s = "" if v is None else str(v)
            s = s.replace('"', '""')
            vals.append(f"\"{s}\"")
        lines.append(",".join(vals))
    out_csv.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def _amain(args: argparse.Namespace) -> int:
    cfg = _load_config(args)
    for p in cfg.providers:
        if p not in ("openai", "anthropic"):
            raise SystemExit(f"Unsupported provider '{p}'. Use openai,anthropic")
    if not cfg.task_ids:
        raise SystemExit("No tasks selected")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_root = cfg.output_dir / stamp
    run_root.mkdir(parents=True, exist_ok=True)
    (run_root / "config.json").write_text(json.dumps(dataclasses.asdict(cfg), indent=2, default=str), encoding="utf-8")

    queue: asyncio.Queue = asyncio.Queue()
    for provider in cfg.providers:
        for task_id in cfg.task_ids:
            queue.put_nowait((provider, task_id))
    for _ in range(cfg.max_parallel):
        queue.put_nowait(None)

    summaries: list[EpisodeResult] = []
    workers = [
        asyncio.create_task(_worker_loop(f"w{i+1}", cfg, queue, run_root, summaries))
        for i in range(cfg.max_parallel)
    ]
    await queue.join()
    for w in workers:
        await w

    _write_leaderboard(run_root, summaries)
    print(f"\nRun complete. Artifacts: {run_root}")
    ok = [s for s in summaries if s.status == "ok"]
    if ok:
        mean_score = sum(float(s.final_score or 0.0) for s in ok) / len(ok)
        print(f"Successful episodes: {len(ok)}/{len(summaries)} | mean final_score={mean_score:.4f}")
    else:
        print(f"Successful episodes: 0/{len(summaries)}")
    return 0


def main() -> None:
    p = argparse.ArgumentParser(description="Run CUA providers on Figma tasks and score automatically.")
    p.add_argument("--config", default="", help="optional JSON config file")
    p.add_argument("--app-url", default="http://127.0.0.1:5173", help="Figma mock URL")
    p.add_argument("--providers", default="openai,anthropic", help="comma-separated: openai,anthropic")
    p.add_argument("--tasks", default="01", help="comma/range, e.g. 01,02,10-12")
    p.add_argument("--max-steps", type=int, default=80, help="max tool-action turns per episode")
    p.add_argument("--max-parallel", type=int, default=1, help="concurrent episodes (default 1 to minimize cores)")
    p.add_argument("--show-browser", action="store_true", help="run headed browser instead of headless")
    p.add_argument("--step-delay-ms", type=int, default=120, help="delay after each executed action")
    p.add_argument("--nav-timeout-ms", type=int, default=30000, help="page navigation timeout")
    p.add_argument("--width", type=int, default=1280, help="browser viewport width")
    p.add_argument("--height", type=int, default=800, help="browser viewport height")
    p.add_argument("--output-dir", default=str(SCRIPTS_DIR / "cua_runs"), help="artifact root")

    p.add_argument("--openai-model", default="computer-use-preview", help="OpenAI computer-use model")
    p.add_argument("--openai-tool-type", default="computer_use_preview", help="OpenAI tool type: computer_use_preview or computer")
    p.add_argument("--openai-api-key-env", default="OPENAI_API_KEY", help="env var for OpenAI API key")

    p.add_argument("--anthropic-model", default="claude-sonnet-4-5", help="Anthropic model name")
    p.add_argument("--anthropic-tool-version", default="20250124", help="Anthropic computer tool version")
    p.add_argument("--anthropic-beta", default="computer-use-2025-01-24", help="Anthropic beta header value")
    p.add_argument("--anthropic-api-key-env", default="ANTHROPIC_API_KEY", help="env var for Anthropic API key")

    args = p.parse_args()
    rc = asyncio.run(_amain(args))
    raise SystemExit(rc)


if __name__ == "__main__":
    main()


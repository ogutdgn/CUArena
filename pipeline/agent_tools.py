import base64, io, json, re, subprocess, sys, time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from pydantic import ValidationError
from pipeline.prober import probe_element
from pipeline.teardown import DESTRUCTIVE_RES
from tools.ids import slug
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent, UIContainer, UIElement
from tools.winapp import capture, inputs
from tools.winapp.hit_test import element_at
from tools.winapp.windows import top_windows

# Container kinds that only make sense as a labeled grouping of contents --
# writing one with zero children is (almost) always a symptom of a switch
# that silently failed (wrong surface still on screen, click landed on
# nothing, etc.), not a legitimately empty surface. "window"/"section" are
# excluded: a window can legitimately have no top-level named children of
# its own (everything lives in child containers), and "section" is a
# free-form grouping the agent may create for a genuinely sparse area.
EMPTY_REJECT_KINDS = {"tab", "menu", "dialog", "dropdown", "pane"}

MAX_SCREENSHOT_WIDTH = 1280

SETTLE_SECONDS = 0.8

REPO_ROOT = Path(__file__).resolve().parent.parent

# Keys that either persist data (save/print) or close the window — refused
# outright since the explorer must never trigger them, by design or by typo.
DESTRUCTIVE_KEY_RES = [r"\^s", r"\^p", r"%\{f4\}"]

_COORD_RE = re.compile(r"^\s*(-?\d+)\s*,\s*(-?\d+)\s*$")


@dataclass
class ToolContext:
    session: Any
    writer: KBWriter
    journal: Journal
    kb_app_root: Path
    cfg: Any


# --- shared helpers -----------------------------------------------------

def _named_elements(ctx: ToolContext):
    return [e for e in ctx.session.ui.children(depth=1) if e.name.strip()]

def _refs(elements) -> list[str]:
    counts: dict[str, int] = {}
    out = []
    for e in elements:
        s = slug(e.name)
        n = counts.get(s, 0)
        out.append(f"{s}-{n}")
        counts[s] = n + 1
    return out

def _resolve(ctx: ToolContext, ref_or_label: str):
    elements = _named_elements(ctx)
    refs = _refs(elements)
    for r, e in zip(refs, elements):
        if r == ref_or_label:
            return e
    for e in elements:
        if e.name.lower() == ref_or_label.lower():
            return e
    return None

def _is_destructive(label: str, cfg) -> bool:
    return any(re.search(pat, label) for pat in DESTRUCTIVE_RES + list(cfg.destructive_label_res))

def _diff_summary(before_names: list[str], after_names: list[str]) -> str:
    before_set, after_set = set(before_names), set(after_names)
    added = [n for n in after_names if n not in before_set]
    removed = [n for n in before_names if n not in after_set]
    if not added and not removed:
        return "no visible change"
    parts = []
    if added:
        sample = ", ".join(added[:5])
        parts.append(f"+{len(added)} new elements (sample: {sample})")
    if removed:
        parts.append(f"-{len(removed)} gone")
    return "; ".join(parts)

def downscale_for_agent(img, max_width: int = MAX_SCREENSHOT_WIDTH):
    """Pure helper: takes a PIL image, returns a copy bounded to max_width
    (PIL .thumbnail preserves aspect ratio and is a no-op if already
    narrower). Kept separate from screenshot encoding so it is trivially
    unit-testable without any capture/IO involved.
    """
    thumb = img.copy()
    if thumb.width > max_width:
        ratio = max_width / thumb.width
        thumb.thumbnail((max_width, max(1, int(thumb.height * ratio))))
    return thumb

def _encode_png_b64(img) -> str:
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("ascii")

def _window_image_b64(ctx: ToolContext):
    """Grab the target window itself (tools.winapp.capture.grab_window,
    not whatever happens to be foreground), downscale for the agent, and
    return (capture_method, base64_png). Used by every ACTION tool's
    post-action "see the result" step.
    """
    img, method = capture.grab_window(ctx.session.hwnd)
    thumb = downscale_for_agent(img)
    return method, _encode_png_b64(thumb)

def _settle(ctx: ToolContext) -> None:
    time.sleep(SETTLE_SECONDS)


# --- perception -----------------------------------------------------------

def look_impl(ctx: ToolContext):
    """Pure perception: current window-true screenshot plus a short text
    description (title/size). Does not act, does not journal a mutation --
    just look at what's on screen right now.
    """
    info = ctx.session.ui.info()
    method, b64_png = _window_image_b64(ctx)
    l, t, r, b = info.rect
    text = f"window '{info.name}' size {r - l}x{b - t} (capture: {method})"
    ctx.journal.append(JournalEvent(actor="explorer.look", action="look", target=info.name,
                                    outcome="ok", data={"capture_method": method}))
    return text, b64_png

def inspect_impl(ctx: ToolContext) -> str:
    """UIA precision listing -- the on-demand instrument for reading exact
    element refs/labels/bounds, not the primary sense (that's look()).
    """
    elements = _named_elements(ctx)
    refs = _refs(elements)
    out = [{"ref": r, "label": e.name, "control_type": e.control_type, "bounds": list(e.rect)}
           for r, e in zip(refs, elements)]
    ctx.journal.append(JournalEvent(actor="explorer.inspect", action="inspect",
                                    outcome="ok", data={"count": len(out)}))
    return json.dumps(out)


# --- action tools (act -> settle -> see) -----------------------------------

def _click_target_label(ctx: ToolContext, target: str):
    """Resolve what a click target refers to for the safety check, before
    any input is sent. Returns (label_for_safety_check, click_fn) where
    click_fn() performs the actual click once safety has cleared, or
    (None, None) if the target could not be resolved at all.
    """
    m = _COORD_RE.match(target)
    if m:
        x_rel, y_rel = int(m.group(1)), int(m.group(2))
        win_rect = ctx.session.ui.info().rect
        x_abs, y_abs = win_rect[0] + x_rel, win_rect[1] + y_rel
        hit = element_at(x_abs, y_abs)
        label = hit.name if hit is not None and hit.name.strip() else target

        # click_rect expects a rect and clicks its center; a single point's
        # "center" is itself, so pass a zero-area rect at the point.
        def do_click():
            inputs.ensure_foreground(ctx.session.hwnd)
            inputs.click_rect((x_abs, y_abs, x_abs, y_abs))
        return label, do_click

    elem = _resolve(ctx, target)
    if elem is None:
        return None, None
    label = elem.name

    def do_click():
        inputs.ensure_foreground(ctx.session.hwnd)
        inputs.click_rect(elem.rect)
    return label, do_click

def click_impl(ctx: ToolContext, target: str):
    label, do_click = _click_target_label(ctx, target)
    if label is None:
        ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=target,
                                        outcome="failed: not-found"))
        return f"not found: {target}", None
    if _is_destructive(label, ctx.cfg):
        ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=label,
                                        outcome="blocked"))
        return "blocked: destructive", None

    before_names = [e.name for e in _named_elements(ctx)]
    do_click()
    _settle(ctx)
    after_names = [e.name for e in _named_elements(ctx)]
    diff = _diff_summary(before_names, after_names)
    windows = [w.title or w.cls for w in top_windows()]
    method, b64_png = _window_image_b64(ctx)
    ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=label,
                                    outcome="ok", data={"diff": diff, "capture_method": method}))
    return f"clicked '{label}'; {diff}; windows now: {windows}", b64_png

def type_text_impl(ctx: ToolContext, text: str):
    inputs.ensure_foreground(ctx.session.hwnd)
    inputs.type_text(text)
    _settle(ctx)
    method, b64_png = _window_image_b64(ctx)
    ctx.journal.append(JournalEvent(actor="explorer.type_text", action="type_text",
                                    target=text[:120], outcome="ok",
                                    data={"capture_method": method}))
    return f"typed {len(text)} chars", b64_png

def press_impl(ctx: ToolContext, keys: str):
    if any(re.search(pat, keys, re.IGNORECASE) for pat in DESTRUCTIVE_KEY_RES):
        ctx.journal.append(JournalEvent(actor="explorer.press", action="press", target=keys,
                                        outcome="blocked"))
        return "blocked: destructive keys", None
    inputs.ensure_foreground(ctx.session.hwnd)
    inputs.press(keys)
    _settle(ctx)
    method, b64_png = _window_image_b64(ctx)
    ctx.journal.append(JournalEvent(actor="explorer.press", action="press", target=keys,
                                    outcome="ok", data={"capture_method": method}))
    return f"pressed '{keys}'", b64_png

_VALID_DIRECTIONS = {"up": 1, "down": -1}

def scroll_impl(ctx: ToolContext, direction: str, amount: int = 3):
    d = direction.strip().lower()
    if d not in _VALID_DIRECTIONS:
        return f"invalid direction: {direction} (use up|down)", None
    win_rect = ctx.session.ui.info().rect
    l, t, r, b = win_rect
    center = ((l + r) // 2, (t + b) // 2)
    inputs.ensure_foreground(ctx.session.hwnd)
    inputs.scroll(center, _VALID_DIRECTIONS[d] * amount)
    _settle(ctx)
    method, b64_png = _window_image_b64(ctx)
    ctx.journal.append(JournalEvent(actor="explorer.scroll", action="scroll", target=d,
                                    outcome="ok", data={"amount": amount, "capture_method": method}))
    return f"scrolled {d} x{amount}", b64_png

def bring_forward_impl(ctx: ToolContext):
    inputs.ensure_foreground(ctx.session.hwnd)
    _settle(ctx)
    method, b64_png = _window_image_b64(ctx)
    ctx.journal.append(JournalEvent(actor="explorer.bring_forward", action="bring_forward",
                                    outcome="ok", data={"capture_method": method}))
    return "brought to foreground", b64_png

def probe_impl(ctx: ToolContext, target: str):
    label, _ = _click_target_label(ctx, target)
    if label is None:
        return f"not found: {target}", None
    if _is_destructive(label, ctx.cfg):
        ctx.journal.append(JournalEvent(actor="explorer.probe", action="probe", target=label,
                                        outcome="blocked"))
        return "blocked: destructive", None
    elem = _resolve(ctx, target)
    if elem is None:
        return f"not found: {target}", None
    ui_elem = UIElement(control_type=elem.control_type.lower(), label=label,
                        icon={"description": "not captured"}, bounds=elem.rect,
                        source="uia", unexplored=True)
    result = probe_element(ctx.session, ui_elem, ctx.journal)
    out = {"kind": result.kind, "expanded": [e.name for e in result.expanded],
           "restored": result.restored}
    method, b64_png = _window_image_b64(ctx)
    return json.dumps(out), b64_png


# --- knowledge-base writes ---------------------------------------------

def write_container_impl(ctx: ToolContext, container_json: str) -> str:
    try:
        container = UIContainer.model_validate_json(container_json)
    except ValidationError as exc:
        ctx.journal.append(JournalEvent(actor="explorer.write_container", action="write_container",
                                        outcome="rejected", data={"error": str(exc)[:500]}))
        return f"rejected: {exc}"
    if container.kind in EMPTY_REJECT_KINDS and not container.children:
        ctx.journal.append(JournalEvent(actor="explorer.write_container", action="write_container",
                                        target=container.id, outcome="rejected-empty",
                                        data={"kind": container.kind}))
        return (f"rejected: empty {container.kind} container — read and include its contents, "
                f"or do not write it")
    path = ctx.writer.write_container(container)
    ctx.journal.append(JournalEvent(actor="explorer.write_container", action="write_container",
                                    target=container.id, outcome="ok"))
    return str(path)

def record_route_impl(ctx: ToolContext, steps_json: str) -> str:
    try:
        steps = json.loads(steps_json)
    except json.JSONDecodeError as exc:
        ctx.journal.append(JournalEvent(actor="explorer.record_route", action="record_route",
                                        outcome="rejected", data={"error": str(exc)}))
        return f"rejected: {exc}"
    path = ctx.kb_app_root / "scripts" / "drive" / "ready_route.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(steps, indent=2), encoding="utf-8")
    ctx.journal.append(JournalEvent(actor="explorer.record_route", action="record_route",
                                    outcome="ok", data={"steps": len(steps)}))
    return str(path)

def write_worklist_impl(ctx: ToolContext, items_json: str) -> str:
    """Validate a list of {"surface": <name>, "how": <one line>} items and
    persist them under kb/<app>/scripts/worklist.json. This is the agent's
    OWN plan for phase 2's deterministic per-item loop -- code iterates it,
    it does not invent it.
    """
    try:
        items = json.loads(items_json)
    except json.JSONDecodeError as exc:
        ctx.journal.append(JournalEvent(actor="explorer.write_worklist", action="write_worklist",
                                        outcome="rejected", data={"error": str(exc)}))
        return f"rejected: {exc}"
    if not isinstance(items, list) or not items:
        ctx.journal.append(JournalEvent(actor="explorer.write_worklist", action="write_worklist",
                                        outcome="rejected", data={"error": "empty or not a list"}))
        return "rejected: worklist must be a non-empty list"
    for i, item in enumerate(items):
        if (not isinstance(item, dict) or
                not isinstance(item.get("surface"), str) or not item["surface"].strip() or
                not isinstance(item.get("how"), str) or not item["how"].strip()):
            ctx.journal.append(JournalEvent(actor="explorer.write_worklist", action="write_worklist",
                                            outcome="rejected",
                                            data={"error": f"item {i} missing surface/how"}))
            return f"rejected: item {i} must have non-empty 'surface' and 'how' strings"
    path = ctx.kb_app_root / "scripts" / "worklist.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(items, indent=2), encoding="utf-8")
    ctx.journal.append(JournalEvent(actor="explorer.write_worklist", action="write_worklist",
                                    outcome="ok", data={"items": len(items)}))
    return str(path)

def note_progress_impl(ctx: ToolContext, text: str) -> str:
    """Live progress narration hook: no side effect beyond a journal entry
    the agent can use to explain itself mid-mission (e.g. why it is
    skipping a surface, or what it is about to try next).
    """
    ctx.journal.append(JournalEvent(actor="explorer.note", action="note", outcome="progress",
                                    data={"text": text}))
    return "noted"


# --- scripting ---------------------------------------------------------

def _scripts_root(ctx: ToolContext) -> Path:
    return ctx.kb_app_root / "scripts"

def _confine(root: Path, relpath: str) -> Path:
    target = (root / relpath).resolve()
    root_resolved = root.resolve()
    if root_resolved not in target.parents and target != root_resolved:
        raise ValueError(f"path escapes scripts dir: {relpath}")
    return target

def write_script_impl(ctx: ToolContext, relpath: str, content: str) -> str:
    root = _scripts_root(ctx)
    path = _confine(root, relpath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    ctx.journal.append(JournalEvent(actor="explorer.write_script", action="write_script",
                                    target=relpath, outcome="ok"))
    return str(path)

def run_script_impl(ctx: ToolContext, relpath: str) -> str:
    path = _confine(_scripts_root(ctx), relpath)
    proc = subprocess.run([sys.executable, str(path)], capture_output=True, timeout=120,
                          cwd=REPO_ROOT, text=True)
    combined = (proc.stdout or "") + (proc.stderr or "")
    out = f"exit {proc.returncode}\n{combined[-2000:]}"
    ctx.journal.append(JournalEvent(actor="explorer.run_script", action="run_script",
                                    target=relpath, outcome=f"exit-{proc.returncode}"))
    return out


# --- SDK wiring -------------------------------------------------------------
# SDK imports live only here: the impls above stay SDK-free and unit-testable
# with fakes. Verified against the installed claude-agent-sdk 0.2.113 by
# reading claude_agent_sdk/__init__.py's create_sdk_mcp_server call_tool
# handler (lines ~478-485) and the in-process query bridge in
# claude_agent_sdk/_internal/query.py (lines ~652-659): a content item
# {"type": "image", "data": <base64 str>, "mimeType": <str>} round-trips
# through mcp.types.ImageContent(type="image", data=..., mimeType=...) and
# back out to the identical dict shape -- both keys required, no defaults.
# @tool(name, description, input_schema) wraps an async handler taking a
# single args dict and returning {"content": [...]}; create_sdk_mcp_server
# (name, tools=[...]) builds an in-process McpSdkServerConfig;
# ClaudeAgentOptions.mcp_servers takes {server_name: config} and
# allowed_tools is a flat list of tool names -- we use the fully-qualified
# "mcp__<server>__<tool>" form to avoid collisions with any other server the
# host process might add.

def _text_content(sync_fn):
    def build(args):
        result = sync_fn(args)
        return {"content": [{"type": "text", "text": result}]}
    return build

def _text_and_image_content(sync_fn):
    # Every ACTION tool returns (text_summary, base64_png_or_None) instead of
    # plain text: the tool result includes BOTH a text block (short summary,
    # for the agent's own bookkeeping/journal reasoning) and -- when the
    # action actually ran (b64_png is not None; blocked/not-found short
    # circuits skip the capture) -- an image block so the agent can SEE the
    # result of each step, per the mandate ("agent should drive and see the
    # result of each step so it can verify itself, step-by-step").
    def build(args):
        text, b64_png = sync_fn(args)
        content = [{"type": "text", "text": text}]
        if b64_png is not None:
            content.append({"type": "image", "data": b64_png, "mimeType": "image/png"})
        return {"content": content}
    return build

_TOOL_SPECS = [
    ("look", "See the current window-true screenshot and title/size (pure perception)", {},
     lambda ctx: (lambda args: look_impl(ctx)), _text_and_image_content),
    ("inspect", "UIA precision listing of live named elements with refs/labels/bounds", {},
     lambda ctx: (lambda args: inspect_impl(ctx)), _text_content),
    ("click", "Click an element by ref/label, or by 'x,y' coords relative to the window",
     {"target": str},
     lambda ctx: (lambda args: click_impl(ctx, args["target"])), _text_and_image_content),
    ("type_text", "Type literal text into the focused control", {"text": str},
     lambda ctx: (lambda args: type_text_impl(ctx, args["text"])), _text_and_image_content),
    ("press", "Send a key chord to the focused window", {"keys": str},
     lambda ctx: (lambda args: press_impl(ctx, args["keys"])), _text_and_image_content),
    ("scroll", "Scroll the window with the mouse wheel", {"direction": str, "amount": int},
     lambda ctx: (lambda args: scroll_impl(ctx, args["direction"], args.get("amount", 3))),
     _text_and_image_content),
    ("bring_forward", "Ensure the target window is in the foreground", {},
     lambda ctx: (lambda args: bring_forward_impl(ctx)), _text_and_image_content),
    ("probe", "Press an element and observe/restore the effect", {"target": str},
     lambda ctx: (lambda args: probe_impl(ctx, args["target"])), _text_and_image_content),
    ("write_container", "Write a UIContainer JSON node to the KB", {"container_json": str},
     lambda ctx: (lambda args: write_container_impl(ctx, args["container_json"])), _text_content),
    ("record_route", "Record the steps to reach the ready workspace", {"steps_json": str},
     lambda ctx: (lambda args: record_route_impl(ctx, args["steps_json"])), _text_content),
    ("write_worklist", "Write the survey worklist ([{surface, how}, ...]) to the KB",
     {"items_json": str},
     lambda ctx: (lambda args: write_worklist_impl(ctx, args["items_json"])), _text_content),
    ("note_progress", "Narrate progress/reasoning into the journal", {"text": str},
     lambda ctx: (lambda args: note_progress_impl(ctx, args["text"])), _text_content),
    ("write_script", "Write a helper script under kb/<app>/scripts/", {"relpath": str, "content": str},
     lambda ctx: (lambda args: write_script_impl(ctx, args["relpath"], args["content"])), _text_content),
    ("run_script", "Run a previously written helper script", {"relpath": str},
     lambda ctx: (lambda args: run_script_impl(ctx, args["relpath"])), _text_content),
]

def make_explorer_tools(ctx: ToolContext) -> list:
    from claude_agent_sdk import tool

    made = []
    for name, description, schema, bind, content_builder in _TOOL_SPECS:
        sync_fn = bind(ctx)
        build_content = content_builder(sync_fn)

        async def handler(args, _build=build_content):
            return _build(args)

        made.append(tool(name, description, schema)(handler))
    return made

def run_explorer_agent(briefing: str, tools: list, max_turns: int = 60) -> str:
    import anyio
    from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query

    server = create_sdk_mcp_server(name="ui", tools=tools)
    allowed = [f"mcp__ui__{t.name}" for t in tools]
    # Hermetic: no ambient settings/CLAUDE.md, only the in-process "ui" server
    # and its tools are reachable, bounded by max_turns.
    #
    # allowed_tools alone is NOT a restriction: per claude-agent-sdk 0.2.113's
    # README ("Using Tools" section), allowed_tools is a permission allowlist
    # only -- listed tools are auto-approved, unlisted tools fall through to
    # permission_mode/can_use_tool, but the built-in toolset (Read/Write/Edit/
    # Bash/Glob/Grep/...) stays in Claude's toolset regardless. Confirmed by
    # reading _internal/transport/subprocess_cli.py:_build_command: allowed_tools
    # only ever emits --allowedTools, a separate flag from --tools.
    #
    # The actual base-set restriction is ClaudeAgentOptions.tools (see
    # types.py: "Specify the base set of available built-in tools ... []
    # (empty list) -- Disable all built-in tools"). subprocess_cli.py maps
    # tools=[] to `--tools ""`, which is a different CLI flag from
    # --allowedTools/--disallowedTools and from the same source: MCP servers
    # are wired independently via --mcp-config, so tools=[] strips the
    # built-ins without touching our in-process "ui" MCP server or its
    # mcp__ui__* tools. query() and ClaudeSDKClient both route through the
    # same SubprocessCLITransport._build_command, so this applies to query()
    # too (no ClaudeSDKClient needed).
    #
    # disallowed_tools is added as defense-in-depth: it is the CLI's harder
    # guarantee ("removed from the model's context and cannot be used, even
    # if they would otherwise be allowed" per types.py), covering us in case
    # tools=[] behaves unexpectedly on some CLI version, and it's what the
    # SDK's own README recommends for blocking specific tools.
    BUILTIN_TOOLS = ["Task", "Bash", "Glob", "Grep", "Read", "Edit", "Write",
                     "NotebookEdit", "WebFetch", "WebSearch", "TodoWrite",
                     "SlashCommand", "ExitPlanMode", "BashOutput", "KillShell"]
    options = ClaudeAgentOptions(setting_sources=[], mcp_servers={"ui": server},
                                 allowed_tools=allowed, tools=[],
                                 disallowed_tools=BUILTIN_TOOLS, max_turns=max_turns)

    async def _go() -> str:
        chunks: list[str] = []
        async for message in query(prompt=briefing, options=options):
            for block in getattr(message, "content", []) or []:
                text = getattr(block, "text", None)
                if text:
                    chunks.append(text)
        return "".join(chunks)
    return anyio.run(_go)

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

REPO_ROOT = Path(__file__).resolve().parent.parent

# Keys that either persist data (save/print) or close the window — refused
# outright since the explorer must never trigger them, by design or by typo.
DESTRUCTIVE_KEY_RES = [r"\^s", r"\^p", r"%\{f4\}"]

@dataclass
class ToolContext:
    session: Any
    writer: KBWriter
    journal: Journal
    kb_app_root: Path
    cfg: Any

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

def read_screen_impl(ctx: ToolContext) -> str:
    elements = _named_elements(ctx)
    refs = _refs(elements)
    out = [{"ref": r, "label": e.name, "control_type": e.control_type, "bounds": list(e.rect)}
           for r, e in zip(refs, elements)]
    ctx.journal.append(JournalEvent(actor="explorer.read_screen", action="read_screen",
                                    outcome="ok", data={"count": len(out)}))
    return json.dumps(out)

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

def click_impl(ctx: ToolContext, ref_or_label: str) -> str:
    elem = _resolve(ctx, ref_or_label)
    label = elem.name if elem is not None else ref_or_label
    if _is_destructive(label, ctx.cfg):
        ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=label,
                                        outcome="blocked"))
        return "blocked: destructive"
    if elem is None:
        ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=label,
                                        outcome="failed: not-found"))
        return f"not found: {ref_or_label}"
    before_names = [e.name for e in _named_elements(ctx)]
    inputs.ensure_foreground(ctx.session.hwnd)
    inputs.click_rect(elem.rect)
    time.sleep(0.8)
    after_names = [e.name for e in _named_elements(ctx)]
    diff = _diff_summary(before_names, after_names)
    windows = [w.title or w.cls for w in top_windows()]
    ctx.journal.append(JournalEvent(actor="explorer.click", action="click", target=label,
                                    outcome="ok", data={"diff": diff}))
    return f"clicked '{label}'; {diff}; windows now: {windows}"

def press_impl(ctx: ToolContext, keys: str) -> str:
    if any(re.search(pat, keys, re.IGNORECASE) for pat in DESTRUCTIVE_KEY_RES):
        ctx.journal.append(JournalEvent(actor="explorer.press", action="press", target=keys,
                                        outcome="blocked"))
        return "blocked: destructive keys"
    inputs.press(keys)
    ctx.journal.append(JournalEvent(actor="explorer.press", action="press", target=keys,
                                    outcome="ok"))
    return f"pressed '{keys}'"

def probe_impl(ctx: ToolContext, ref_or_label: str) -> str:
    elem = _resolve(ctx, ref_or_label)
    label = elem.name if elem is not None else ref_or_label
    if elem is None:
        return f"not found: {ref_or_label}"
    if _is_destructive(label, ctx.cfg):
        ctx.journal.append(JournalEvent(actor="explorer.probe", action="probe", target=label,
                                        outcome="blocked"))
        return "blocked: destructive"
    ui_elem = UIElement(control_type=elem.control_type.lower(), label=label,
                        icon={"description": "not captured"}, bounds=elem.rect,
                        source="uia", unexplored=True)
    result = probe_element(ctx.session, ui_elem, ctx.journal)
    out = {"kind": result.kind, "expanded": [e.name for e in result.expanded],
           "restored": result.restored}
    return json.dumps(out)

def screenshot_impl(ctx: ToolContext, name: str) -> tuple[str, str]:
    """Capture the target window itself (not whatever happens to be in the
    foreground -- see tools.winapp.capture.grab_window) and return both the
    KB-relative saved path and a base64-encoded PNG for the caller to hand
    back to the agent as an image content block (FIX 3: the agent couldn't
    see any of its own screenshots before this).
    """
    img, method = capture.grab_window(ctx.session.hwnd)
    rel = ctx.writer.save_screenshot(img, "ui:screen", name)
    ctx.journal.append(JournalEvent(actor="explorer.screenshot", action="screenshot", target=name,
                                    outcome="ok", data={"capture_method": method}))
    thumb = img.copy()
    if thumb.width > MAX_SCREENSHOT_WIDTH:
        ratio = MAX_SCREENSHOT_WIDTH / thumb.width
        thumb.thumbnail((MAX_SCREENSHOT_WIDTH, max(1, int(thumb.height * ratio))))
    buf = io.BytesIO()
    thumb.convert("RGB").save(buf, format="PNG")
    b64_png = base64.b64encode(buf.getvalue()).decode("ascii")
    return rel, b64_png

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
# introspection (inspect.signature on tool/create_sdk_mcp_server/
# ClaudeAgentOptions): @tool(name, description, input_schema) wraps an async
# handler taking a single args dict and returning {"content": [...]};
# create_sdk_mcp_server(name, tools=[...]) builds an in-process McpSdkServerConfig;
# ClaudeAgentOptions.mcp_servers takes {server_name: config} and allowed_tools
# is a flat list of tool names using the SDK's own "mcp__<server>__<tool>"
# naming convention (confirmed against create_sdk_mcp_server's docstring
# example: mcp_servers={"calc": calculator}, allowed_tools=["add", "multiply"]
# is the SHORT form; the CLI-facing convention documented elsewhere in the SDK
# for restricting by server-qualified name is "mcp__<server>__<tool>" — both
# forms are accepted by allowed_tools, we use the fully-qualified form here
# to avoid collisions with any other server the host process might add).

def _text_content(ctx: ToolContext, sync_fn):
    def build(args):
        result = sync_fn(args)
        return {"content": [{"type": "text", "text": result}]}
    return build

def _screenshot_content(ctx: ToolContext, sync_fn):
    # screenshot_impl returns (rel_path, base64_png) instead of plain text:
    # the tool result includes BOTH a text block (the saved path, for the
    # agent's own bookkeeping/journal reasoning) and an image block (so the
    # agent can actually SEE what it captured -- FIX 3). Per the installed
    # claude-agent-sdk 0.2.113 (verified by reading create_sdk_mcp_server's
    # call_tool wrapper in claude_agent_sdk/__init__.py): a content item
    # with {"type": "image", "data": <base64 str>, "mimeType": <str>} is
    # parsed into mcp.types.ImageContent(type="image", data=item["data"],
    # mimeType=item["mimeType"]) -- both keys are required, no defaults.
    def build(args):
        rel_path, b64_png = sync_fn(args)
        return {"content": [
            {"type": "text", "text": rel_path},
            {"type": "image", "data": b64_png, "mimeType": "image/png"},
        ]}
    return build

_TOOL_SPECS = [
    ("read_screen", "List live named UI elements on screen with refs", {},
     lambda ctx: (lambda args: read_screen_impl(ctx)), _text_content),
    ("click", "Click an element by ref or label", {"ref_or_label": str},
     lambda ctx: (lambda args: click_impl(ctx, args["ref_or_label"])), _text_content),
    ("press", "Send a key chord to the focused window", {"keys": str},
     lambda ctx: (lambda args: press_impl(ctx, args["keys"])), _text_content),
    ("probe", "Press an element and observe/restore the effect", {"ref_or_label": str},
     lambda ctx: (lambda args: probe_impl(ctx, args["ref_or_label"])), _text_content),
    ("screenshot", "Grab a screenshot of the app window and see the image", {"name": str},
     lambda ctx: (lambda args: screenshot_impl(ctx, args["name"])), _screenshot_content),
    ("write_container", "Write a UIContainer JSON node to the KB", {"container_json": str},
     lambda ctx: (lambda args: write_container_impl(ctx, args["container_json"])), _text_content),
    ("record_route", "Record the steps to reach the ready workspace", {"steps_json": str},
     lambda ctx: (lambda args: record_route_impl(ctx, args["steps_json"])), _text_content),
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
        build_content = content_builder(ctx, sync_fn)

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

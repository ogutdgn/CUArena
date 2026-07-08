import json
from typing import Protocol
from pydantic import ValidationError
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import AppNode, JournalEvent, UIContainer

class AgentRunner(Protocol):
    def run(self, briefing: str) -> str: ...

EXAMPLE = {"name": "example-editor", "version": "2.1", "platform": "desktop",
           "what_is_it": "a rich text editor", "used_for": "writing formatted documents",
           "who_uses": "office workers and students",
           "layout_regions": ["ui:main-window"],
           "feature_inventory": [{"id": "feature:text-formatting", "name": "Text Formatting",
                                  "one_liner": "bold/italic/font controls for selected text",
                                  "trigger_path": ["ui:main-window"]}]}

def briefing_for(app_name: str, version: str, surface: UIContainer) -> str:
    return (
        f"You are the skeleton inspector for the app '{app_name}' (version {version}).\n"
        "Below is the mechanically scanned surface layer (ground truth — do not invent elements).\n\n"
        f"SURFACE:\n{surface.model_dump_json(indent=2)}\n\n"
        "Produce ONLY a JSON object with fields: name, version, platform, what_is_it, used_for, "
        "who_uses, layout_regions (container ids), feature_inventory (list of "
        "{id: 'feature:<slug>', name, one_liner, trigger_path: [container/element ids]}).\n"
        "Group the surface elements into user-recognizable features. Every feature MUST have a "
        "trigger_path that starts at a listed layout region. Use only ids that appear in SURFACE.\n\n"
        f"EXAMPLE OF A CORRECT ANSWER:\n{json.dumps(EXAMPLE, indent=2)}\n"
    )

def run_skeleton_agent(runner: AgentRunner, app_name: str, version: str, surface: UIContainer,
                       writer: KBWriter, journal: Journal) -> AppNode:
    raw = runner.run(briefing_for(app_name, version, surface))
    try:
        node = AppNode.model_validate_json(raw)
    except ValidationError:
        journal.append(JournalEvent(actor="stage1.agent", action="skeleton", target=app_name,
                                    outcome="failed: invalid-agent-output", data={"raw": raw[:500]}))
        raise
    writer.write_app(node)
    journal.append(JournalEvent(actor="stage1.agent", action="skeleton", target=app_name,
                                outcome="ok", data={"features": len(node.feature_inventory)}))
    return node

class SdkRunner:
    """Real runner: one-shot Claude Agent SDK query, returns the final text."""
    def run(self, briefing: str) -> str:
        import anyio
        from claude_agent_sdk import ClaudeAgentOptions, query

        # Hermetic options: the agent must reason over ONLY the briefing text.
        # setting_sources=[] stops the CLI from loading ~/.claude/settings.json,
        # .claude/settings.json/.local.json, or any CLAUDE.md (CLAUDE.md needs
        # "project" in setting_sources, which we deliberately omit) — otherwise
        # this machine's ambient config leaks into the one-shot query. tools=[]
        # disables every built-in tool since this call only reasons over text
        # and never needs to act.
        options = ClaudeAgentOptions(setting_sources=[], tools=[])

        async def _go() -> str:
            chunks: list[str] = []
            async for message in query(prompt=briefing, options=options):
                for block in getattr(message, "content", []) or []:
                    text = getattr(block, "text", None)
                    if text:
                        chunks.append(text)
            text = "".join(chunks)
            start, end = text.find("{"), text.rfind("}")
            return text[start:end + 1] if start != -1 else text
        return anyio.run(_go)

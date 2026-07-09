import json, re, time
from pathlib import Path
from pipeline.agent_tools import ToolContext, make_explorer_tools, run_explorer_agent
from pipeline.stage1_surface import DEFAULT_SCAN_DEPTH
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent
from tools.winapp import inputs

# Generic, app-agnostic briefing: the agent decides what to explore and how;
# code only supplies tools, safety floors, and journaling.
B1_MISSION = """\
You are exploring a desktop application to document its trigger surface.

READY STATE
Before documenting anything, determine whether the app is already in its
main working state (a workspace ready for input) or is showing a launcher /
start screen (template picker, splash, recent-files list, etc.). If it is a
launcher, find the minimal sequence of clicks that reaches the workspace and
record that sequence with record_route so future runs can skip the launcher
automatically. If the app is already ready, call record_route with an empty
list. Keep the recorded route minimal -- only what is required to reach the
workspace.

SKELETON MISSION
Outline this app's trigger surface. Document the main window and each
top-level navigation container (tabs, menus): use probe to measure what each
element does, write one container per surface via write_container (ids
`ui:<kind>-<slug>`, elements with exactly one marker -- opens only for
measured outcomes, unexplored otherwise), screenshot each surface. Cover
every top-level tab and menu before finishing.

VERIFY BEFORE YOU WRITE
After switching to any surface (clicking a tab/menu/etc.), you MUST verify
the switch actually happened before documenting it: check the click result's
diff summary ("+N new elements" / "-M gone") and/or take a screenshot (the
screenshot tool now returns the image itself, so look at it) BEFORE calling
write_container for that surface. If a click reports "no visible change",
the surface did not switch -- do not write it. Journal that outcome mentally
(it is already recorded automatically) and either retry the click once or
move on to the next surface. Never call write_container for a container you
have not confirmed is actually showing on screen, and never write a
container with zero children just to mark it "covered" -- the tool will
reject empty tab/menu/dialog/dropdown/pane containers outright, and even if
it didn't, an empty container is worse than no container: it looks like
documented coverage while recording nothing.

RULES
- Never perform destructive actions (save, print, close) -- the tools will
  refuse them anyway, but do not attempt to work around a refusal.
- If a save-confirmation dialog appears, discard it (do not save).
- Every tool call is journaled automatically; you do not need to log
  anything yourself.
- You may write and run helper scripts under scripts/ for repetitive
  mechanics (e.g. iterating over many similar elements).

FINISH CONTRACT
When you are done, reply starting with the single word DONE followed by a
one-paragraph coverage summary naming what you documented and what you
deliberately left unexplored.
"""

def run_explorer(session, writer: KBWriter, journal: Journal, kb_app_root: Path,
                  cfg, max_turns: int = 60) -> str:
    ctx = ToolContext(session=session, writer=writer, journal=journal,
                      kb_app_root=kb_app_root, cfg=cfg)
    tools = make_explorer_tools(ctx)
    reply = run_explorer_agent(B1_MISSION, tools, max_turns)
    outcome = "done" if reply.strip().startswith("DONE") else "failed: no-done"
    journal.append(JournalEvent(actor="explorer", action="mission", outcome=outcome,
                                data={"reply": reply[:2000]}))
    return reply

def replay_route(session, route_path: Path, journal: Journal) -> None:
    steps = json.loads(Path(route_path).read_text(encoding="utf-8"))
    for step in steps:
        pattern = step["click_label_re"]
        elements = session.ui.children(depth=DEFAULT_SCAN_DEPTH)
        match = next((e for e in elements if re.search(pattern, e.name, re.IGNORECASE)), None)
        if match is None:
            journal.append(JournalEvent(actor="ready", action="replay", target=pattern,
                                        outcome="failed: route-step"))
            raise RuntimeError(f"ready-route step not found: {pattern}")
        inputs.ensure_foreground(session.hwnd)
        inputs.click_rect(match.rect)
        time.sleep(0.8)
        journal.append(JournalEvent(actor="ready", action="replay", target=match.name,
                                    outcome="ok"))

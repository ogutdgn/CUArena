import json, re, time
from pathlib import Path
from pipeline.agent_tools import ToolContext, make_explorer_tools, run_explorer_agent
from pipeline.stage1_surface import DEFAULT_SCAN_DEPTH
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent
from tools.winapp import inputs

# Generic, app-agnostic briefings: the agent decides what to explore and how;
# code only supplies tools, safety floors, journaling, and the phase-2 loop
# that iterates the agent's OWN worklist. Split into two missions (survey,
# then one focused run per worklist item) instead of one long open-ended
# mission: a single agent run covering an entire app's trigger surface tends
# to lose track of what it already verified by the time it is 20+ tools deep,
# whereas each phase-2 run only has to hold one surface in its head, and it
# always starts from the freshly-verified images the SDK just gave it.

SURVEY_MISSION = """\
You are surveying a desktop application to plan how to document its trigger
surface. This is a SHORT reconnaissance pass -- you are not documenting
anything yet, just looking around and making a plan.

READY STATE
Call look() first to see what's on screen. Determine whether the app is
already in its main working state (a workspace ready for input) or is
showing a launcher / start screen (template picker, splash, recent-files
list, etc.). If it is a launcher, find the minimal sequence of clicks that
reaches the workspace and record that sequence with record_route so future
runs can skip the launcher automatically. If the app is already ready, call
record_route with an empty list. Keep the recorded route minimal -- only
what is required to reach the workspace.

WORKLIST
Once you are at the ready workspace, use look() and inspect() to identify
the app's top-level navigable surfaces (tabs, menus, panes, dialogs reached
from the main window -- whatever this app actually has). For each one, write
a short one-line note on how to reach it from the ready workspace. Then call
write_worklist with a JSON list of {"surface": "<name>", "how": "<one line>"}
items, one per surface. Do not visit or document the surfaces yet -- that
happens later, one at a time. Aim for the smallest list that still covers
every top-level tab/menu you can see; do not invent surfaces you have not
actually seen on screen.

RULES
- Never perform destructive actions (save, print, close) -- the tools will
  refuse them anyway, but do not attempt to work around a refusal.
- If a save-confirmation dialog appears, discard it (do not save).
- Every tool call is journaled automatically; you do not need to log
  anything yourself.

FINISH CONTRACT
When you are done, reply starting with the single word DONE followed by a
one-sentence summary of the worklist you wrote.
"""

ITEM_MISSION = """\
Document ONE surface: {surface}. Reach it: {how}.

VERIFY YOU ARE LOOKING AT IT
Every action tool (click, type_text, press, scroll, bring_forward) already
returns a screenshot image of the window after it settles -- look at that
image (and/or call look() again) before you decide the surface is showing.
If a click reports "no visible change" or the image does not show the
surface you expected, the surface did not switch -- do NOT write it. Retry
once, or call note_progress explaining why you could not reach it and finish.

READ AND WRITE
Once you have verified the surface is on screen, use inspect() to read its
contents (and probe() where you need to measure what an element does), then
write it via write_container: one container for this surface, id
`ui:<kind>-<slug>`, elements with exactly one marker (opens/triggers only for
measured outcomes, unexplored otherwise). A screenshot is saved alongside the
container automatically as part of the action tools you already called --
you do not need a separate screenshot step.

Never call write_container with zero children just to mark this surface
"covered" -- the tool rejects empty tab/menu/dialog/dropdown/pane containers
outright, and even if it didn't, an empty container is worse than no
container: it looks like documented coverage while recording nothing. If you
cannot verify the surface, do NOT write it -- call note_progress explaining
why, then finish.

RULES
- Never perform destructive actions (save, print, close) -- the tools will
  refuse them anyway, but do not attempt to work around a refusal.
- If a save-confirmation dialog appears, discard it (do not save).
- Every tool call is journaled automatically; you do not need to log
  anything yourself.

FINISH CONTRACT
When you are done, reply starting with the single word DONE followed by a
one-sentence outcome (what you wrote, or why you did not).
"""


def _read_worklist(kb_app_root: Path) -> list[dict] | None:
    path = kb_app_root / "scripts" / "worklist.json"
    if not path.exists():
        return None
    try:
        items = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if not isinstance(items, list) or not items:
        return None
    return items


def _item_outcome(new_events: list[JournalEvent]) -> tuple[str, dict]:
    """Inspect the journal events produced during one item's focused run and
    decide ok/failed the same way a human reviewer would: did the agent
    actually write a (non-empty) container for this surface?
    """
    for ev in reversed(new_events):
        if ev.actor == "explorer.write_container" and ev.outcome == "ok":
            return "ok", {"container": ev.target}
    return "failed", {}


def run_survey(session, writer: KBWriter, journal: Journal, kb_app_root: Path, cfg,
               max_turns: int = 20, verbose: bool = True) -> list[dict] | None:
    ctx = ToolContext(session=session, writer=writer, journal=journal,
                      kb_app_root=kb_app_root, cfg=cfg)
    tools = make_explorer_tools(ctx)
    reply = run_explorer_agent(SURVEY_MISSION, tools, max_turns)
    worklist = _read_worklist(kb_app_root)
    outcome = "done" if worklist is not None else "failed: no-worklist"
    journal.append(JournalEvent(actor="explorer", action="survey", outcome=outcome,
                                data={"reply": reply[:2000], "items": len(worklist or [])}))
    if verbose:
        n = len(worklist) if worklist is not None else 0
        print(f"[explorer] survey -> {outcome} ({n} items)")
    return worklist


def run_item(session, writer: KBWriter, journal: Journal, kb_app_root: Path, cfg,
             item: dict, index: int, total: int,
             max_turns: int = 15, verbose: bool = True) -> str:
    ctx = ToolContext(session=session, writer=writer, journal=journal,
                      kb_app_root=kb_app_root, cfg=cfg)
    tools = make_explorer_tools(ctx)
    briefing = ITEM_MISSION.format(surface=item["surface"], how=item["how"])

    before_path = journal.path
    before_count = len(Journal.read_all(before_path))
    reply = run_explorer_agent(briefing, tools, max_turns)
    all_events = Journal.read_all(before_path)
    new_events = all_events[before_count:]
    outcome, data = _item_outcome(new_events)
    data["reply"] = reply[:1000]
    journal.append(JournalEvent(actor="explorer", action="item", target=item["surface"],
                                outcome=outcome, data=data))
    if verbose:
        detail = f" ({data['container']})" if "container" in data else ""
        print(f"[explorer] item {index}/{total} {item['surface']} -> {outcome}{detail}")
    return outcome


def run_explorer(session, writer: KBWriter, journal: Journal, kb_app_root: Path,
                  cfg, survey_max_turns: int = 20, item_max_turns: int = 15,
                  verbose: bool = True) -> str:
    """Orchestrates all three phases: survey (writes a worklist), the
    deterministic per-item work loop over that worklist (one focused agent
    run per surface), then a coverage summary. Code drives the loop; the
    agent drives each individual surface.
    """
    worklist = run_survey(session, writer, journal, kb_app_root, cfg,
                          max_turns=survey_max_turns, verbose=verbose)
    if not worklist:
        journal.append(JournalEvent(actor="explorer", action="mission",
                                    outcome="failed: no-worklist"))
        summary = "FAILED: survey did not produce a worklist"
        if verbose:
            print(f"[explorer] {summary}")
        return summary

    done, failed = [], []
    total = len(worklist)
    for i, item in enumerate(worklist, start=1):
        outcome = run_item(session, writer, journal, kb_app_root, cfg, item, i, total,
                           max_turns=item_max_turns, verbose=verbose)
        (done if outcome == "ok" else failed).append(item["surface"])

    journal.append(JournalEvent(actor="explorer", action="mission", outcome="done",
                                data={"done": done, "failed": failed, "total": total}))
    summary = (f"DONE: {len(done)}/{total} surfaces documented"
              f"{'; failed: ' + ', '.join(failed) if failed else ''}")
    if verbose:
        print(f"[explorer] {summary}")
    return summary


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

import json, pytest
from pathlib import Path
from pydantic import ValidationError
from pipeline.stage1_agent import briefing_for, run_skeleton_agent
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import Icon, UIContainer, UIElement

SURFACE = UIContainer(id="ui:main-window", kind="window", label="Notepad", children=[
    UIElement(control_type="menu-item", label="File", icon=Icon(description="none"),
              source="uia", unexplored=True)])

GOOD = json.dumps({"name": "notepad", "version": "1.0", "platform": "desktop",
                   "what_is_it": "a plain-text editor", "used_for": "editing text files",
                   "who_uses": "everyone",
                   "layout_regions": ["ui:main-window"],
                   "feature_inventory": [{"id": "feature:file-management", "name": "File Management",
                                          "one_liner": "open and save files",
                                          "trigger_path": ["ui:main-window"]}]})

class FakeRunner:
    def __init__(self, reply): self.reply = reply
    def run(self, briefing: str) -> str: return self.reply

def test_briefing_contains_surface_and_schema():
    b = briefing_for("notepad", "1.0", SURFACE)
    assert "File" in b and "feature_inventory" in b and "trigger_path" in b

def test_agent_output_written_as_app_json(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    node = run_skeleton_agent(FakeRunner(GOOD), "notepad", "1.0", SURFACE, KBWriter(tmp_path, "notepad"), j)
    assert node.feature_inventory[0].id == "feature:file-management"
    assert (tmp_path / "notepad" / "app.json").exists()

def test_invalid_agent_output_raises_and_journals(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with pytest.raises(ValidationError):
        run_skeleton_agent(FakeRunner('{"name": "notepad"}'), "notepad", "1.0", SURFACE,
                           KBWriter(tmp_path, "notepad"), j)
    assert "invalid-agent-output" in Journal.read_all(tmp_path / "j.jsonl")[-1].outcome

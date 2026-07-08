import pytest
from pathlib import Path
from pipeline.stage1_agent import SdkRunner, run_skeleton_agent
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import Icon, UIContainer, UIElement

pytestmark = pytest.mark.agent_live

def test_live_skeleton_on_fake_surface(tmp_path: Path):
    surface = UIContainer(id="ui:main-window", kind="window", label="Notepad", children=[
        UIElement(control_type="menu-item", label=n, icon=Icon(description="none"),
                  source="uia", unexplored=True) for n in ["File", "Edit", "Format", "View", "Help"]])
    node = run_skeleton_agent(SdkRunner(), "notepad", "1.0", surface,
                              KBWriter(tmp_path, "notepad"), Journal(tmp_path / "j.jsonl", run_id="live"))
    assert len(node.feature_inventory) >= 2

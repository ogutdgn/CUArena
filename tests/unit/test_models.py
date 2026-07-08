import pytest
from pydantic import ValidationError
from tools.models import Icon, UIElement, UIContainer, AppNode, FeatureStub

def el(**over):
    base = dict(control_type="button", label="Bold",
                icon=Icon(description="bold letter B", image=None),
                source="uia", triggers="subfeature:bold")
    base.update(over)
    return UIElement(**base)

def test_element_with_one_marker_is_valid():
    assert el().triggers == "subfeature:bold"

def test_element_with_no_marker_is_rejected():
    with pytest.raises(ValidationError):
        el(triggers=None)

def test_element_with_two_markers_is_rejected():
    with pytest.raises(ValidationError):
        el(opens="ui:font-dialog")  # triggers also set -> two markers

def test_unexplored_counts_as_the_one_marker():
    e = el(triggers=None, unexplored=True)
    assert e.unexplored is True

def test_missing_label_is_rejected():
    with pytest.raises(ValidationError):
        UIElement(control_type="button", icon=Icon(description="x"), source="uia", unexplored=True)

def test_container_requires_ui_prefix():
    with pytest.raises(ValidationError):
        UIContainer(id="main", kind="window", label="Main")
    c = UIContainer(id="ui:main-window", kind="window", label="Main")
    assert c.children == [] and c.child_containers == []

def test_app_node_roundtrip():
    app = AppNode(name="notepad", version="11.2409", platform="desktop",
                  what_is_it="a text editor", used_for="editing plain text",
                  who_uses="everyone",
                  layout_regions=["ui:main-window"],
                  feature_inventory=[FeatureStub(id="feature:file-management", name="File Management",
                                                 one_liner="open/save text files",
                                                 trigger_path=["ui:main-window", "ui:menu-file"])])
    assert AppNode.model_validate_json(app.model_dump_json()).name == "notepad"

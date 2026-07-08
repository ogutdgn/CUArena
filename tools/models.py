from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

class Icon(BaseModel):
    description: str
    image: Optional[str] = None          # relative path to cropped image; null = control has no icon

class UIElement(BaseModel):
    id: Optional[str] = None
    control_type: str                    # behavioral kind: button, toggle-button, dropdown, menu-item, ...
    label: str
    icon: Icon
    tooltip: Optional[str] = None
    shortcut: Optional[str] = None       # display string only; registry is source of truth (Plan B)
    location: Optional[str] = None       # "ui:parent > ui:child" chain
    bounds: Optional[tuple[int, int, int, int]] = None  # left, top, right, bottom (screen px)
    state_notes: Optional[str] = None
    source: str                          # provenance: uia | hit-test | object-model | pixel | vision | docs | tooltip
    triggers: Optional[str] = None       # node id, e.g. "subfeature:bold"
    opens: Optional[str] = None          # container id, e.g. "ui:font-dialog"
    unexplored: bool = False

    @model_validator(mode="after")
    def exactly_one_marker(self):
        n = sum([self.triggers is not None, self.opens is not None, self.unexplored])
        if n != 1:
            raise ValueError(f"element '{self.label}' must carry exactly one of triggers/opens/unexplored, got {n}")
        return self

class UIContainer(BaseModel):
    id: str = Field(pattern=r"^ui:[a-z0-9][a-z0-9-]*$")
    kind: Literal["window", "dialog", "dropdown", "pane", "menu", "tab", "section"]
    label: str
    screenshot: Optional[str] = None
    children: list[UIElement] = []
    child_containers: list[str] = []     # ids of nested containers (each its own file)

class FeatureStub(BaseModel):
    id: str = Field(pattern=r"^feature:[a-z0-9][a-z0-9-]*$")
    name: str
    one_liner: str
    trigger_path: list[str]              # container/element id chain from the skeleton

class AppNode(BaseModel):
    name: str
    version: str
    platform: Literal["desktop", "web"]
    what_is_it: str
    used_for: str
    who_uses: str
    layout_regions: list[str] = []       # top-level container ids
    feature_inventory: list[FeatureStub] = []

class JournalEvent(BaseModel):
    ts: str = ""                         # filled by Journal.append
    run_id: str = ""                     # filled by Journal.append
    actor: str                           # e.g. "stage0", "stage1.surface", "stage1.agent"
    action: str                          # e.g. "launch", "scan-container", "press", "boundary", "error"
    target: str = ""                     # element/container/app the action addressed
    outcome: str = ""                    # e.g. "ok", "dialog-opened", "skipped", "failed: <why>"
    data: dict = {}

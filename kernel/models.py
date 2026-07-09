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
    purpose: Optional[str] = None        # what this surface is for (design: stubs record purpose)
    screenshot: Optional[str] = None
    children: list[UIElement] = []
    child_containers: list[str] = []     # ids of nested containers (each its own file)
    explored: bool = True                # False = STUB: exists + measured-open, interior deferred
                                         # (design/knowledge-base-design.md, playbook step 2)

class FeatureStub(BaseModel):
    id: str = Field(pattern=r"^feature:[a-z0-9][a-z0-9-]*$")
    name: str
    one_liner: str
    trigger_path: list[str]              # container/element id chain from the skeleton


# --- the 3-level knowledge tree (design/knowledge-base-design.md: feature / subfeature nodes) ---

class Connection(BaseModel):
    """An affects/uses edge in the SOURCE node's connections[]. Drives priority (Step 4)."""
    target: str                          # node id (feature:/subfeature:) or container id
    kind: Literal["affects", "uses"]
    why: str                             # the evidence for the edge
    source: Literal["measured", "observed", "co-location", "shared-target",
                    "dependency", "contextual", "inference"]


class TriggerPath(BaseModel):
    """A path into the skeleton that fires this node — mouse id-chain or keyboard shortcut."""
    path: list[str] = []                 # e.g. ["ui:main-window", "ui:ribbon-home", "el:bold"]
    kind: Literal["mouse", "keyboard"] = "mouse"
    shortcut: Optional[str] = None       # e.g. "Ctrl+B" or keytip "Alt, H, 1"


def _valid_audience(v: str) -> str:
    ok = v in ("everyone", "most", "niche") or v.startswith("role-specific:")
    if not ok:
        raise ValueError(f"audience_breadth '{v}' must be everyone|most|niche|role-specific:<role>")
    return v


class FeatureNode(BaseModel):
    id: str = Field(pattern=r"^feature:[a-z0-9][a-z0-9-]*$")
    node_type: Literal["feature"] = "feature"
    name: str
    what_it_does: str                    # the function — a real description, not a name
    affects: str                         # the state/target it changes
    audience_breadth: str
    behavior: Optional[str] = None       # depth: how it works (options, states, defaults, edges)
    trigger_paths: list[TriggerPath] = []
    shortcut: Optional[str] = None       # display string; registry is source of truth
    location: Optional[str] = None       # ui container id where it lives
    screenshot: Optional[str] = None
    screenshots: list[str] = []          # depth: icon crop + surface shots (visual evidence)
    subfeatures: list[str] = []          # child subfeature ids
    connections: list[Connection] = []
    boundary: bool = False               # a Home-tab group we deliberately did not press
    explored: bool = False               # depth flag (Step 5 flips for P0-P2)
    source: str = "measured"

    @model_validator(mode="after")
    def _aud(self):
        _valid_audience(self.audience_breadth)
        return self


class SubFeatureNode(BaseModel):
    id: str = Field(pattern=r"^subfeature:[a-z0-9][a-z0-9-]*$")
    node_type: Literal["subfeature"] = "subfeature"
    name: str
    parent: Optional[str] = None         # feature id
    what_it_does: str
    affects: str
    audience_breadth: str
    behavior: Optional[str] = None       # depth: how it works (options, states, defaults, edges)
    trigger_paths: list[TriggerPath] = []
    shortcut: Optional[str] = None
    opens: Optional[str] = None          # container id if the control opens a surface (Step 2)
    location: Optional[str] = None
    screenshot: Optional[str] = None
    screenshots: list[str] = []          # depth: icon crop + surface shots (visual evidence)
    connections: list[Connection] = []
    boundary: bool = False
    explored: bool = False               # Step 5 flips for P0-P2 after full depth
    source: str = "measured"

    @model_validator(mode="after")
    def _aud(self):
        _valid_audience(self.audience_breadth)
        return self

class AppNode(BaseModel):
    name: str
    version: str
    platform: Literal["desktop", "web"]
    what_is_it: str
    used_for: str
    who_uses: str
    layout_regions: list[str] = []       # top-level container ids
    feature_inventory: list[FeatureStub] = []

class ShortcutBinding(BaseModel):
    context: str                         # WHEN this binding is active
    effect: str                          # how it acts
    triggers: Optional[str] = None       # node id
    opens: Optional[str] = None          # container id
    source: list[str] = []               # provenance: tooltip | uia-accelerator | keytip | docs

    @model_validator(mode="after")
    def exactly_one_action(self):
        n = sum([self.triggers is not None, self.opens is not None])
        if n != 1:
            raise ValueError(f"shortcut binding must carry exactly one of triggers/opens, got {n}")
        return self


class ShortcutEntry(BaseModel):
    keys: str                            # e.g. "Ctrl+B"
    bindings: list[ShortcutBinding]      # context-scoped; a context-dependent key holds several


class JournalEvent(BaseModel):
    ts: str = ""                         # filled by Journal.append
    run_id: str = ""                     # filled by Journal.append
    actor: str                           # e.g. "stage0", "stage1.surface", "stage1.agent"
    action: str                          # e.g. "launch", "scan-container", "press", "boundary", "error"
    target: str = ""                     # element/container/app the action addressed
    outcome: str = ""                    # e.g. "ok", "dialog-opened", "skipped", "failed: <why>"
    data: dict = {}

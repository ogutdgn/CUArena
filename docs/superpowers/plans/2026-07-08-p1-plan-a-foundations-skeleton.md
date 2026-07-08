# P1 Plan A: Foundations + Desktop Tools + Skeleton Pass — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A runnable `python -m pipeline.run <app> --stages 0,1` that launches a Windows desktop app, maps its skeleton surface layer, and writes a valid, schema-enforced partial KB (`kb/<app>/`) — validated on Notepad (full surface) and MS Word (scoped surface).

**Architecture:** Bottom-up per the spec (`docs/superpowers/specs/2026-07-07-knowledge-base-pipeline-design.md`): data models + journal + schema-enforcing writers first (everything depends on them), then the desktop half of the tool catalog as thin wrappers (UIA read, window detection, real input, capture/pixels, hit-testing), then Stage 0 (launch/pin/boundaries) and Stage 1 (mechanical surface scan + one LLM skeleton agent for identity/feature inventory). Deterministic parts are plain Python; only the skeleton agent uses the Claude Agent SDK.

**Tech Stack:** Python 3.11+, pydantic v2 (models/validation), pywinauto + pywin32 (UIA, win32), Pillow (capture/pixels), claude-agent-sdk (skeleton agent), pytest.

## Global Constraints

- **Generality:** no app-specific logic in `pipeline/` or `tools/` — app specifics live only in `configs/apps/<app>.json` (data) and `kb/<app>/` (output). A change that fixes one test app but breaks another is a pipeline bug.
- **Exactly-one marker:** every interactive element record carries exactly one of `triggers` / `opens` / `unexplored: true` (spec: "The UI tree").
- **Mandatory fields:** `control_type`, `label`, `icon` on every ui_element (icon `image` may be `null` when a control genuinely has none; `description` still required).
- **All KB writes go through the schema-enforcing writer** (spec: tool catalog, "KB writers"); writers refuse invalid records.
- **Journal everything:** every inspector action and outcome appends to `kb/<app>/journal.jsonl` (spec: "Inspection discipline").
- **Version pinning:** Stage 0 records app version; asserted on later runs; mismatch = loud failure (exit, journaled).
- **Test pyramid:** default `pytest` run needs no GUI and finishes in seconds; real-app tests are marked `smoke` (Notepad, seconds) and are excluded by default; Word runs are scoped (`--max-containers`), full builds are milestones only.
- **Python 3.11+; line length/style: match existing code; no new deps beyond:** pydantic>=2, pywinauto, pywin32, Pillow, claude-agent-sdk, pytest.

## File Structure

```
pyproject.toml                    # project metadata, deps, pytest config
tools/__init__.py
tools/models.py                   # pydantic models: Icon, UIElement, UIContainer, AppNode, FeatureStub, JournalEvent
tools/journal.py                  # append-only JSONL journal
tools/kb_writer.py                # schema-enforcing KB writers + screenshot saver
tools/winapp/__init__.py
tools/winapp/uia.py               # UIA session: attach, list children (pywinauto backend="uia")
tools/winapp/windows.py           # top-level window listing, wait-for-new-window, dialog-vs-flyout classify
tools/winapp/inputs.py            # real mouse/keyboard + foreground enforcement
tools/winapp/capture.py           # screenshots, crops, pixel sampling (Pillow)
tools/winapp/hit_test.py          # element-at-point (owner-drawn UI)
pipeline/__init__.py
pipeline/config.py                # per-app run config + boundaries loader (configs/apps/*.json)
pipeline/stage0.py                # launch, version pin, journal run-start
pipeline/stage1_surface.py        # mechanical surface-layer scan -> containers/elements/screenshots
pipeline/stage1_agent.py          # skeleton agent briefing + runner (mockable), writes app.json
pipeline/run.py                   # CLI entry
configs/apps/notepad.json         # test-app config (data, not code)
configs/apps/word.json            # test-app config (data, not code)
tests/unit/...                    # no GUI needed
tests/smoke/...                   # real Notepad/Word, marked "smoke"
```

Node/edge JSON *file* formats are exactly the pydantic models' `model_dump_json()` — the models ARE the schemas for this plan (feature/subfeature deep rubric models arrive in Plan B; Plan A needs only AppNode + FeatureStub + UI tree + journal).

---

### Task 1: Project scaffolding + core data models

**Files:**
- Create: `pyproject.toml`, `tools/__init__.py`, `tools/models.py`
- Test: `tests/unit/test_models.py`

**Interfaces:**
- Produces: `Icon(description: str, image: str | None)`, `UIElement`, `UIContainer`, `AppNode`, `FeatureStub`, `JournalEvent` (all pydantic v2 `BaseModel`). `UIElement` enforces the exactly-one-marker rule at construction. Later tasks import from `tools.models`.

- [ ] **Step 1: Write pyproject.toml**

```toml
[project]
name = "app-pipeline"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = ["pydantic>=2", "pywinauto", "pywin32; sys_platform == 'win32'", "Pillow", "claude-agent-sdk"]

[project.optional-dependencies]
dev = ["pytest"]

[tool.pytest.ini_options]
addopts = "-m 'not smoke and not agent_live'"
markers = [
  "smoke: needs a real GUI app (Notepad/Word); run explicitly with -m smoke",
  "agent_live: makes a real LLM API call; run explicitly",
]
testpaths = ["tests"]
```

- [ ] **Step 2: Write the failing tests**

```python
# tests/unit/test_models.py
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
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.models'`

- [ ] **Step 4: Write the models**

```python
# tools/models.py
from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

class Icon(BaseModel):
    description: str
    image: Optional[str] = None          # relative path to cropped image; null = control has no icon

class UIElement(BaseModel):
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
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_models.py -v`
Expected: PASS (7 tests)

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml tools/__init__.py tools/models.py tests/unit/test_models.py
git commit -m "feat: project scaffolding and core KB data models with exactly-one-marker rule"
```

---

### Task 2: Append-only journal

**Files:**
- Create: `tools/journal.py`
- Test: `tests/unit/test_journal.py`

**Interfaces:**
- Consumes: `tools.models.JournalEvent`
- Produces: `Journal(path: Path, run_id: str)` with `.append(event: JournalEvent) -> JournalEvent` (stamps `ts` UTC-ISO + `run_id`, appends one JSON line, flushes) and `Journal.read_all(path: Path) -> list[JournalEvent]`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_journal.py
from pathlib import Path
from tools.journal import Journal
from tools.models import JournalEvent

def test_append_stamps_and_persists(tmp_path: Path):
    p = tmp_path / "journal.jsonl"
    j = Journal(p, run_id="run-001")
    e = j.append(JournalEvent(actor="stage0", action="launch", target="notepad", outcome="ok"))
    assert e.ts and e.run_id == "run-001"
    j.append(JournalEvent(actor="stage1.surface", action="scan-container", target="ui:main-window"))
    events = Journal.read_all(p)
    assert [ev.action for ev in events] == ["launch", "scan-container"]

def test_append_is_append_only(tmp_path: Path):
    p = tmp_path / "journal.jsonl"
    Journal(p, run_id="a").append(JournalEvent(actor="x", action="one"))
    Journal(p, run_id="b").append(JournalEvent(actor="x", action="two"))  # reopening never truncates
    assert [e.run_id for e in Journal.read_all(p)] == ["a", "b"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_journal.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.journal'`

- [ ] **Step 3: Implement**

```python
# tools/journal.py
from datetime import datetime, timezone
from pathlib import Path
from tools.models import JournalEvent

class Journal:
    def __init__(self, path: Path, run_id: str):
        self.path = Path(path)
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append(self, event: JournalEvent) -> JournalEvent:
        event.ts = datetime.now(timezone.utc).isoformat()
        event.run_id = self.run_id
        with self.path.open("a", encoding="utf-8") as f:
            f.write(event.model_dump_json() + "\n")
        return event

    @staticmethod
    def read_all(path: Path) -> list[JournalEvent]:
        p = Path(path)
        if not p.exists():
            return []
        return [JournalEvent.model_validate_json(line)
                for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_journal.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/journal.py tests/unit/test_journal.py
git commit -m "feat: append-only JSONL journal"
```

---

### Task 3: Schema-enforcing KB writer

**Files:**
- Create: `tools/kb_writer.py`
- Test: `tests/unit/test_kb_writer.py`

**Interfaces:**
- Consumes: `tools.models` (`UIContainer`, `AppNode`), `PIL.Image.Image`
- Produces: `KBWriter(kb_root: Path, app: str)` with:
  - `.write_container(c: UIContainer) -> Path` → `kb/<app>/ui/<id-without-prefix>.json`
  - `.write_app(a: AppNode) -> Path` → `kb/<app>/app.json`
  - `.save_screenshot(img, node_id: str, name: str) -> str` → saves PNG under `kb/<app>/screenshots/<node_id>/<name>.png`, returns the KB-relative path
  - All writers re-validate via `model_validate` and raise `pydantic.ValidationError` on bad input; they never write a partial file.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_kb_writer.py
import json, pytest
from pathlib import Path
from PIL import Image
from pydantic import ValidationError
from tools.kb_writer import KBWriter
from tools.models import UIContainer, AppNode

def test_write_container_places_file_and_content(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    c = UIContainer(id="ui:main-window", kind="window", label="Notepad")
    path = w.write_container(c)
    assert path == tmp_path / "notepad" / "ui" / "main-window.json"
    assert json.loads(path.read_text(encoding="utf-8"))["kind"] == "window"

def test_writer_refuses_invalid_dict(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    with pytest.raises(ValidationError):
        w.write_container({"id": "no-prefix", "kind": "window", "label": "x"})
    assert not (tmp_path / "notepad" / "ui").exists() or not list((tmp_path / "notepad" / "ui").iterdir())

def test_write_app(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    p = w.write_app(AppNode(name="notepad", version="1", platform="desktop",
                            what_is_it="editor", used_for="text", who_uses="everyone"))
    assert p == tmp_path / "notepad" / "app.json"

def test_save_screenshot_returns_relative_path(tmp_path: Path):
    w = KBWriter(tmp_path, "notepad")
    rel = w.save_screenshot(Image.new("RGB", (4, 4)), "ui:main-window", "full")
    assert rel == "screenshots/ui:main-window/full.png"
    assert (tmp_path / "notepad" / rel).exists()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_kb_writer.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.kb_writer'`

- [ ] **Step 3: Implement**

```python
# tools/kb_writer.py
from pathlib import Path
from PIL import Image
from tools.models import UIContainer, AppNode

class KBWriter:
    def __init__(self, kb_root: Path, app: str):
        self.root = Path(kb_root) / app

    def _write_json(self, model, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(model.model_dump_json(indent=2), encoding="utf-8")
        return path

    def write_container(self, c) -> Path:
        c = UIContainer.model_validate(c)                      # refuse bad input BEFORE touching disk
        return self._write_json(c, self.root / "ui" / (c.id.removeprefix("ui:") + ".json"))

    def write_app(self, a) -> Path:
        a = AppNode.model_validate(a)
        return self._write_json(a, self.root / "app.json")

    def save_screenshot(self, img: Image.Image, node_id: str, name: str) -> str:
        rel = f"screenshots/{node_id}/{name}.png"
        out = self.root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out)
        return rel
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_kb_writer.py -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add tools/kb_writer.py tests/unit/test_kb_writer.py
git commit -m "feat: schema-enforcing KB writers with screenshot saver"
```

---

### Task 4: Per-app run config + boundaries loader

**Files:**
- Create: `pipeline/__init__.py`, `pipeline/config.py`, `configs/apps/notepad.json`, `configs/apps/word.json`
- Test: `tests/unit/test_config.py`

**Interfaces:**
- Produces: `AppConfig` (pydantic) with `name, exe, window_title_re, dialog_classes: list[str], flyout_classes: list[str], boundaries: Boundaries`; `Boundaries(dismiss_title_res: list[str], exclude_labels: list[str])`; `load_app_config(name: str, configs_dir: Path) -> AppConfig`. This is DATA — the only place app names appear.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_config.py
import json, pytest
from pathlib import Path
from pipeline.config import load_app_config, AppConfig

def test_load_notepad_config():
    cfg = load_app_config("notepad", Path("configs/apps"))
    assert isinstance(cfg, AppConfig) and cfg.exe.lower().endswith("notepad.exe")

def test_unknown_app_raises():
    with pytest.raises(FileNotFoundError):
        load_app_config("nope", Path("configs/apps"))

def test_boundaries_default_empty(tmp_path: Path):
    (tmp_path / "x.json").write_text(json.dumps(
        {"name": "x", "exe": "x.exe", "window_title_re": ".*x.*"}), encoding="utf-8")
    cfg = load_app_config("x", tmp_path)
    assert cfg.boundaries.dismiss_title_res == [] and cfg.dialog_classes == ["#32770"]
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/test_config.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'pipeline.config'`

- [ ] **Step 3: Implement + write the two app configs**

```python
# pipeline/config.py
from pathlib import Path
from pydantic import BaseModel

class Boundaries(BaseModel):
    dismiss_title_res: list[str] = []    # nag windows to close before inspecting
    exclude_labels: list[str] = []       # areas deliberately out of scope (journaled as skips)

class AppConfig(BaseModel):
    name: str
    exe: str                             # path or bare exe resolvable on PATH
    window_title_re: str
    dialog_classes: list[str] = ["#32770"]           # classic Win32 dialog class
    flyout_classes: list[str] = ["Net UI Tool Window", "MsoCommandBarPopup"]
    boundaries: Boundaries = Boundaries()

def load_app_config(name: str, configs_dir: Path) -> AppConfig:
    p = Path(configs_dir) / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"no app config: {p}")
    return AppConfig.model_validate_json(p.read_text(encoding="utf-8"))
```

```json
// configs/apps/notepad.json
{
  "name": "notepad",
  "exe": "notepad.exe",
  "window_title_re": ".*Notepad.*",
  "boundaries": { "dismiss_title_res": [], "exclude_labels": [] }
}
```

```json
// configs/apps/word.json
{
  "name": "word",
  "exe": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
  "window_title_re": ".*Word.*",
  "boundaries": {
    "dismiss_title_res": [".*What's New.*", ".*Sign in.*"],
    "exclude_labels": ["File", "Editor", "Adobe Acrobat"]
  }
}
```

(JSON files contain no `//` comments — shown here for the plan only. Strip them when creating the files.)

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/test_config.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add pipeline/__init__.py pipeline/config.py configs/apps/notepad.json configs/apps/word.json tests/unit/test_config.py
git commit -m "feat: per-app run config with boundaries (data, not code)"
```

---

### Task 5: UIA read wrapper

**Files:**
- Create: `tools/winapp/__init__.py`, `tools/winapp/uia.py`
- Test: `tests/smoke/test_uia_smoke.py`

**Interfaces:**
- Produces: `ElemInfo(control_type: str, name: str, rect: tuple[int,int,int,int], auto_id: str)` (plain dataclass) and `UIASession` with:
  - `UIASession.attach(title_re: str) -> UIASession` (pywinauto `Desktop(backend="uia")`)
  - `.window_rect() -> tuple`, `.info() -> ElemInfo`
  - `.children(depth: int = 1) -> list[ElemInfo]` — immediate child elements of the main window
  - `.children_of(rect_or_elem) -> list[ElemInfo]`
- Consumed by: Task 9 (hit test uses same `ElemInfo`), Task 11 (surface scan).

- [ ] **Step 1: Write the smoke test (this layer is inherently GUI-bound; unit-testing a wrapper this thin against fakes tests nothing real)**

```python
# tests/smoke/test_uia_smoke.py
import subprocess, time, pytest
from tools.winapp.uia import UIASession

pytestmark = pytest.mark.smoke

@pytest.fixture()
def notepad():
    proc = subprocess.Popen(["notepad.exe"])
    time.sleep(1.5)
    yield proc
    proc.kill()

def test_attach_and_read_children(notepad):
    s = UIASession.attach(".*Notepad.*")
    kids = s.children(depth=2)
    names = [k.name for k in kids if k.name]
    assert any("File" in n for n in names), f"expected a File menu among: {names[:20]}"
    assert all(hasattr(k, "control_type") and hasattr(k, "rect") for k in kids)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/smoke/test_uia_smoke.py -m smoke -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tools.winapp.uia'`

- [ ] **Step 3: Implement**

```python
# tools/winapp/uia.py
from dataclasses import dataclass
from pywinauto import Desktop

@dataclass
class ElemInfo:
    control_type: str
    name: str
    rect: tuple[int, int, int, int]
    auto_id: str

def _info(w) -> ElemInfo:
    r = w.rectangle()
    return ElemInfo(control_type=w.element_info.control_type or "unknown",
                    name=w.element_info.name or "",
                    rect=(r.left, r.top, r.right, r.bottom),
                    auto_id=w.element_info.automation_id or "")

class UIASession:
    def __init__(self, window):
        self._win = window

    @classmethod
    def attach(cls, title_re: str) -> "UIASession":
        win = Desktop(backend="uia").window(title_re=title_re)
        win.wait("exists ready", timeout=10)
        return cls(win)

    def info(self) -> ElemInfo:
        return _info(self._win)

    def window_rect(self):
        return self.info().rect

    def children(self, depth: int = 1) -> list[ElemInfo]:
        out, frontier = [], [(self._win, 0)]
        while frontier:
            node, d = frontier.pop(0)
            for ch in node.children():
                out.append(_info(ch))
                if d + 1 < depth:
                    frontier.append((ch, d + 1))
        return out
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest tests/smoke/test_uia_smoke.py -m smoke -v`
Expected: PASS. Also run `python -m pytest` — must still pass in seconds (smoke excluded by default).

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/__init__.py tools/winapp/uia.py tests/smoke/test_uia_smoke.py
git commit -m "feat: UIA read wrapper with Notepad smoke test"
```

---

### Task 6: Window detection (did something open? dialog or flyout?)

**Files:**
- Create: `tools/winapp/windows.py`
- Test: `tests/unit/test_windows_classify.py`, `tests/smoke/test_windows_smoke.py`

**Interfaces:**
- Produces: `WinInfo(hwnd: int, title: str, cls: str)`; `top_windows() -> list[WinInfo]` (visible only); `wait_new_window(before: list[WinInfo], timeout=2.5, poll=0.3) -> WinInfo | None`; `classify(cls: str, dialog_classes: list[str], flyout_classes: list[str]) -> str` returning `"dialog" | "flyout" | "unknown"`.
- Consumed by: Stage 1 surface scan journaling; Plan B probing.

- [ ] **Step 1: Write the failing unit test (classification is pure logic)**

```python
# tests/unit/test_windows_classify.py
from tools.winapp.windows import classify

def test_classify():
    assert classify("#32770", ["#32770"], ["Net UI Tool Window"]) == "dialog"
    assert classify("Net UI Tool Window", ["#32770"], ["Net UI Tool Window"]) == "flyout"
    assert classify("SomethingElse", ["#32770"], []) == "unknown"
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/unit/test_windows_classify.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# tools/winapp/windows.py
import time
from dataclasses import dataclass
import win32gui

@dataclass(frozen=True)
class WinInfo:
    hwnd: int
    title: str
    cls: str

def top_windows() -> list[WinInfo]:
    out: list[WinInfo] = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            out.append(WinInfo(hwnd, win32gui.GetWindowText(hwnd), win32gui.GetClassName(hwnd)))
        return True
    win32gui.EnumWindows(cb, None)
    return out

def wait_new_window(before: list[WinInfo], timeout: float = 2.5, poll: float = 0.3) -> WinInfo | None:
    seen = {w.hwnd for w in before}
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:           # poll — one-shot detection is racy (spec reference lesson)
        for w in top_windows():
            if w.hwnd not in seen:
                return w
        time.sleep(poll)
    return None

def classify(cls: str, dialog_classes: list[str], flyout_classes: list[str]) -> str:
    if cls in dialog_classes:
        return "dialog"
    if cls in flyout_classes:
        return "flyout"
    return "unknown"
```

- [ ] **Step 4: Write + run the smoke test**

```python
# tests/smoke/test_windows_smoke.py
import subprocess, time, pytest
from tools.winapp.windows import top_windows, wait_new_window

pytestmark = pytest.mark.smoke

def test_new_window_detected_on_launch():
    before = top_windows()
    proc = subprocess.Popen(["notepad.exe"])
    try:
        w = wait_new_window(before, timeout=5.0)
        assert w is not None and "Notepad" in (w.title or "")
    finally:
        proc.kill()
```

Run: `python -m pytest tests/unit/test_windows_classify.py -v && python -m pytest tests/smoke/test_windows_smoke.py -m smoke -v`
Expected: PASS both

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/windows.py tests/unit/test_windows_classify.py tests/smoke/test_windows_smoke.py
git commit -m "feat: window detection with polling and dialog/flyout classification"
```

---

### Task 7: Real input + foreground enforcement

**Files:**
- Create: `tools/winapp/inputs.py`
- Test: `tests/smoke/test_inputs_smoke.py`

**Interfaces:**
- Produces: `ensure_foreground(hwnd: int) -> None`; `click_rect(rect) -> None` (clicks center); `hover_rect(rect) -> None`; `press(keys: str) -> None` (pywinauto `send_keys` syntax, e.g. `"{ESC}"`, `"^b"`).
- Rule encoded: every click/hover first asserts the target window is foreground — silent-drop clicks are the reference crawler's hardest-won lesson.

- [ ] **Step 1: Write the smoke test**

```python
# tests/smoke/test_inputs_smoke.py
import subprocess, time, pytest
from tools.winapp.uia import UIASession
from tools.winapp.windows import top_windows, wait_new_window
from tools.winapp import inputs

pytestmark = pytest.mark.smoke

def test_click_file_menu_opens_menu():
    before = top_windows()
    proc = subprocess.Popen(["notepad.exe"])
    try:
        assert wait_new_window(before, timeout=5.0)
        s = UIASession.attach(".*Notepad.*")
        inputs.ensure_foreground(s._win.handle)
        file_item = next(k for k in s.children(depth=3) if k.name.startswith("File"))
        pre = len(s.children(depth=3))
        inputs.click_rect(file_item.rect)
        time.sleep(0.5)
        post = len(s.children(depth=3))
        assert post > pre, "clicking File should expand a menu (more elements visible)"
        inputs.press("{ESC}")
    finally:
        proc.kill()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/smoke/test_inputs_smoke.py -m smoke -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# tools/winapp/inputs.py
import time
import win32gui
from pywinauto import mouse
from pywinauto.keyboard import send_keys

def ensure_foreground(hwnd: int) -> None:
    if win32gui.GetForegroundWindow() != hwnd:
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2)
    if win32gui.GetForegroundWindow() != hwnd:
        raise RuntimeError(f"could not bring hwnd {hwnd} to foreground; clicks would drop silently")

def _center(rect):
    l, t, r, b = rect
    return ((l + r) // 2, (t + b) // 2)

def click_rect(rect) -> None:
    mouse.click(button="left", coords=_center(rect))

def hover_rect(rect) -> None:
    mouse.move(coords=_center(rect))

def press(keys: str) -> None:
    send_keys(keys, pause=0.05)
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest tests/smoke/test_inputs_smoke.py -m smoke -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/inputs.py tests/smoke/test_inputs_smoke.py
git commit -m "feat: real input injection with foreground enforcement"
```

---

### Task 8: Capture + pixel sampling

**Files:**
- Create: `tools/winapp/capture.py`
- Test: `tests/unit/test_capture.py` (pixel logic on synthetic images), `tests/smoke/test_capture_smoke.py`

**Interfaces:**
- Produces: `grab_region(rect) -> PIL.Image` (`ImageGrab.grab(bbox=rect)`); `crop(img, rect_abs, origin_rect) -> PIL.Image` (element crop out of a window grab); `pixel(img, x: int, y: int) -> tuple[int,int,int]`.

- [ ] **Step 1: Write the failing unit test**

```python
# tests/unit/test_capture.py
from PIL import Image
from tools.winapp.capture import crop, pixel

def test_crop_uses_window_origin():
    img = Image.new("RGB", (100, 100), (0, 0, 0))
    img.paste((255, 0, 0), (10, 10, 20, 20))
    c = crop(img, rect_abs=(510, 210, 520, 220), origin_rect=(500, 200, 600, 300))
    assert c.size == (10, 10) and pixel(c, 5, 5) == (255, 0, 0)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/unit/test_capture.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# tools/winapp/capture.py
from PIL import Image, ImageGrab

def grab_region(rect) -> Image.Image:
    return ImageGrab.grab(bbox=rect)

def crop(img: Image.Image, rect_abs, origin_rect) -> Image.Image:
    ol, ot = origin_rect[0], origin_rect[1]
    l, t, r, b = rect_abs
    return img.crop((l - ol, t - ot, r - ol, b - ot))

def pixel(img: Image.Image, x: int, y: int) -> tuple[int, int, int]:
    return img.convert("RGB").getpixel((x, y))
```

- [ ] **Step 4: Write + run the smoke test, then run all**

```python
# tests/smoke/test_capture_smoke.py
import subprocess, time, pytest
from tools.winapp.uia import UIASession
from tools.winapp.capture import grab_region

pytestmark = pytest.mark.smoke

def test_grab_notepad_window():
    proc = subprocess.Popen(["notepad.exe"]); time.sleep(1.5)
    try:
        rect = UIASession.attach(".*Notepad.*").window_rect()
        img = grab_region(rect)
        assert img.size[0] > 50 and img.size[1] > 50
    finally:
        proc.kill()
```

Run: `python -m pytest tests/unit/test_capture.py -v && python -m pytest tests/smoke/test_capture_smoke.py -m smoke -v`
Expected: PASS both

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/capture.py tests/unit/test_capture.py tests/smoke/test_capture_smoke.py
git commit -m "feat: screen capture, element crop, pixel sampling"
```

---

### Task 9: Hit-testing (element at point)

**Files:**
- Create: `tools/winapp/hit_test.py`
- Test: `tests/smoke/test_hit_test_smoke.py`

**Interfaces:**
- Produces: `element_at(x: int, y: int) -> ElemInfo` (reuses `tools.winapp.uia.ElemInfo`; pywinauto `Desktop(backend="uia").from_point`). For owner-drawn UI invisible in the tree (spec: tool catalog).

- [ ] **Step 1: Write the smoke test**

```python
# tests/smoke/test_hit_test_smoke.py
import subprocess, time, pytest
from tools.winapp.uia import UIASession
from tools.winapp.hit_test import element_at

pytestmark = pytest.mark.smoke

def test_element_at_center_of_notepad():
    proc = subprocess.Popen(["notepad.exe"]); time.sleep(1.5)
    try:
        l, t, r, b = UIASession.attach(".*Notepad.*").window_rect()
        e = element_at((l + r) // 2, (t + b) // 2)
        assert e.control_type  # something real is there (document/edit area)
    finally:
        proc.kill()
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/smoke/test_hit_test_smoke.py -m smoke -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# tools/winapp/hit_test.py
from pywinauto import Desktop
from tools.winapp.uia import ElemInfo, _info

def element_at(x: int, y: int) -> ElemInfo:
    return _info(Desktop(backend="uia").from_point(x, y))
```

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest tests/smoke/test_hit_test_smoke.py -m smoke -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/hit_test.py tests/smoke/test_hit_test_smoke.py
git commit -m "feat: element-at-point hit testing for owner-drawn UI"
```

---

### Task 10: Stage 0 — launch, version pin, boundaries, run journal

**Files:**
- Create: `pipeline/stage0.py`
- Test: `tests/unit/test_stage0.py`, `tests/smoke/test_stage0_smoke.py`

**Interfaces:**
- Consumes: `AppConfig` (Task 4), `Journal` (Task 2), `top_windows/wait_new_window` (Task 6), `UIASession` (Task 5)
- Produces: `AppSession(config: AppConfig, ui: UIASession, hwnd: int, pid: int, version: str)`; `launch(cfg: AppConfig, journal: Journal) -> AppSession`; `file_version(exe_path: str) -> str`; `assert_version(kb_app_json: Path, session_version: str) -> None` — raises `VersionDriftError` on mismatch (loud failure, spec: inspection discipline); dismisses `boundaries.dismiss_title_res` windows via `press("{ESC}")` and journals each as `action="boundary"`.

- [ ] **Step 1: Write the failing unit tests (version logic; no GUI)**

```python
# tests/unit/test_stage0.py
import json, pytest
from pathlib import Path
from pipeline.stage0 import assert_version, VersionDriftError

def _app_json(tmp_path: Path, version: str) -> Path:
    p = tmp_path / "app.json"
    p.write_text(json.dumps({"name": "x", "version": version, "platform": "desktop",
                             "what_is_it": "a", "used_for": "b", "who_uses": "c",
                             "layout_regions": [], "feature_inventory": []}), encoding="utf-8")
    return p

def test_assert_version_passes_on_match(tmp_path):
    assert_version(_app_json(tmp_path, "1.2.3"), "1.2.3")   # no raise

def test_assert_version_fails_loudly_on_drift(tmp_path):
    with pytest.raises(VersionDriftError):
        assert_version(_app_json(tmp_path, "1.2.3"), "9.9.9")

def test_assert_version_ok_when_no_prior_kb(tmp_path):
    assert_version(tmp_path / "missing.json", "1.2.3")      # first run: nothing to drift from
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/unit/test_stage0.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# pipeline/stage0.py
import json, shutil, subprocess, time
from dataclasses import dataclass
from pathlib import Path
import win32api
from pipeline.config import AppConfig
from tools.journal import Journal
from tools.models import JournalEvent
from tools.winapp.uia import UIASession
from tools.winapp.windows import top_windows, wait_new_window
from tools.winapp import inputs

class VersionDriftError(RuntimeError):
    pass

def file_version(exe_path: str) -> str:
    path = shutil.which(exe_path) or exe_path
    info = win32api.GetFileVersionInfo(path, "\\")
    ms, ls = info["FileVersionMS"], info["FileVersionLS"]
    return f"{ms >> 16}.{ms & 0xFFFF}.{ls >> 16}.{ls & 0xFFFF}"

def assert_version(kb_app_json: Path, session_version: str) -> None:
    if not Path(kb_app_json).exists():
        return
    prior = json.loads(Path(kb_app_json).read_text(encoding="utf-8"))["version"]
    if prior != session_version:
        raise VersionDriftError(f"KB was built on {prior}, app is now {session_version} — refusing to mix")

@dataclass
class AppSession:
    config: AppConfig
    ui: UIASession
    hwnd: int
    pid: int
    version: str

def launch(cfg: AppConfig, journal: Journal) -> AppSession:
    before = top_windows()
    proc = subprocess.Popen([cfg.exe])
    win = wait_new_window(before, timeout=15.0)
    if win is None:
        journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name, outcome="failed: no window"))
        raise RuntimeError(f"{cfg.name}: no window appeared")
    time.sleep(1.0)
    ui = UIASession.attach(cfg.window_title_re)
    for pattern in cfg.boundaries.dismiss_title_res:      # dismiss nags BEFORE anything else
        for w in top_windows():
            import re
            if re.match(pattern, w.title or ""):
                inputs.ensure_foreground(w.hwnd)
                inputs.press("{ESC}")
                journal.append(JournalEvent(actor="stage0", action="boundary", target=w.title, outcome="dismissed"))
    version = file_version(cfg.exe)
    journal.append(JournalEvent(actor="stage0", action="launch", target=cfg.name,
                                outcome="ok", data={"version": version, "pid": proc.pid}))
    return AppSession(config=cfg, ui=ui, hwnd=ui._win.handle, pid=proc.pid, version=version)
```

- [ ] **Step 4: Write + run the smoke test, then run all unit tests**

```python
# tests/smoke/test_stage0_smoke.py
import pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from tools.journal import Journal

pytestmark = pytest.mark.smoke

def test_stage0_launches_notepad(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        assert s.version and s.pid > 0
        assert Journal.read_all(tmp_path / "journal.jsonl")[-1].outcome == "ok"
    finally:
        import win32gui, win32con
        win32gui.PostMessage(s.hwnd, win32con.WM_CLOSE, 0, 0)
```

Run: `python -m pytest tests/unit/test_stage0.py -v && python -m pytest tests/smoke/test_stage0_smoke.py -m smoke -v`
Expected: PASS both

- [ ] **Step 5: Commit**

```bash
git add pipeline/stage0.py tests/unit/test_stage0.py tests/smoke/test_stage0_smoke.py
git commit -m "feat: stage 0 launch with version pinning, boundaries, journaling"
```

---

### Task 11: Stage 1a — mechanical surface scan

**Files:**
- Create: `pipeline/stage1_surface.py`
- Test: `tests/unit/test_surface_build.py` (pure assembly logic on fake ElemInfo lists), `tests/smoke/test_surface_smoke.py`

**Interfaces:**
- Consumes: `AppSession` (Task 10), `UIASession.children` (Task 5), `capture` (Task 8), `KBWriter` (Task 3), `Journal` (Task 2)
- Produces:
  - `build_surface(window_info: ElemInfo, children: list[ElemInfo], app: str) -> UIContainer` — pure: converts ElemInfos to a `ui:main-window` container whose `children` are `UIElement`s, every one marked `unexplored=True` (breadth pass never claims triggers it hasn't measured), `source="uia"`, icons `Icon(description="not captured", image=None)` at this stage, labels from `name` (elements with empty names are **skipped and reported**, not invented).
  - `scan_surface(session: AppSession, writer: KBWriter, journal: Journal, max_containers: int = 50) -> list[Path]` — grabs the window screenshot, builds + writes the container, journals `scan-container` per container. `max_containers` is the scope cap that keeps Word runs minutes-long.

- [ ] **Step 1: Write the failing unit test**

```python
# tests/unit/test_surface_build.py
from tools.winapp.uia import ElemInfo
from pipeline.stage1_surface import build_surface

WIN = ElemInfo("Window", "Notepad", (0, 0, 800, 600), "")

def test_build_surface_marks_everything_unexplored():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("MenuItem", "Edit", (40, 0, 80, 20), "")]
    c = build_surface(WIN, kids, app="notepad")
    assert c.id == "ui:main-window" and c.kind == "window"
    assert [e.label for e in c.children] == ["File", "Edit"]
    assert all(e.unexplored and e.triggers is None and e.opens is None for e in c.children)
    assert all(e.source == "uia" for e in c.children)

def test_unnamed_elements_are_skipped_not_invented():
    kids = [ElemInfo("Button", "", (0, 0, 10, 10), ""), ElemInfo("MenuItem", "File", (0, 0, 40, 20), "")]
    c = build_surface(WIN, kids, app="notepad")
    assert [e.label for e in c.children] == ["File"]
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/unit/test_surface_build.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# pipeline/stage1_surface.py
from pathlib import Path
from tools.models import Icon, JournalEvent, UIContainer, UIElement
from tools.kb_writer import KBWriter
from tools.journal import Journal
from tools.winapp.uia import ElemInfo
from tools.winapp import capture

def build_surface(window_info: ElemInfo, children: list[ElemInfo], app: str) -> UIContainer:
    elements = [
        UIElement(control_type=k.control_type.lower(), label=k.name,
                  icon=Icon(description="not captured", image=None),
                  bounds=k.rect, source="uia", unexplored=True)
        for k in children if k.name.strip()
    ]
    return UIContainer(id="ui:main-window", kind="window", label=window_info.name or app,
                       children=elements)

def scan_surface(session, writer: KBWriter, journal: Journal, max_containers: int = 50) -> list[Path]:
    win_info = session.ui.info()
    container = build_surface(win_info, session.ui.children(depth=3), app=session.config.name)
    img = capture.grab_region(win_info.rect)
    container.screenshot = writer.save_screenshot(img, container.id, "full")
    path = writer.write_container(container)
    journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                outcome="ok", data={"elements": len(container.children)}))
    skipped = [k.name for k in session.ui.children(depth=3) if not k.name.strip()]
    if skipped:
        journal.append(JournalEvent(actor="stage1.surface", action="scan-container", target=container.id,
                                    outcome="skipped-unnamed", data={"count": len(skipped)}))
    return [path]
```

- [ ] **Step 4: Write + run the smoke test, then run all**

```python
# tests/smoke/test_surface_smoke.py
import json, pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.stage1_surface import scan_surface
from tools.journal import Journal
from tools.kb_writer import KBWriter

pytestmark = pytest.mark.smoke

def test_surface_scan_on_notepad(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "notepad" / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        paths = scan_surface(s, KBWriter(tmp_path, "notepad"), j)
        data = json.loads(paths[0].read_text(encoding="utf-8"))
        labels = [e["label"] for e in data["children"]]
        assert any("File" in l for l in labels), labels
        assert (tmp_path / "notepad" / data["screenshot"]).exists()
    finally:
        import win32gui, win32con
        win32gui.PostMessage(s.hwnd, win32con.WM_CLOSE, 0, 0)
```

Run: `python -m pytest tests/unit/test_surface_build.py -v && python -m pytest tests/smoke/test_surface_smoke.py -m smoke -v`
Expected: PASS both

- [ ] **Step 5: Commit**

```bash
git add pipeline/stage1_surface.py tests/unit/test_surface_build.py tests/smoke/test_surface_smoke.py
git commit -m "feat: stage 1 mechanical surface scan writing UI containers + screenshots"
```

---

### Task 12: Stage 1b — skeleton agent (identity + feature inventory)

**Files:**
- Create: `pipeline/stage1_agent.py`
- Test: `tests/unit/test_stage1_agent.py` (FakeRunner), `tests/smoke/test_stage1_agent_live.py` (marked `agent_live`)

**Interfaces:**
- Consumes: `UIContainer` (surface scan output), `AppNode/FeatureStub` models, `KBWriter`
- Produces:
  - `AgentRunner` protocol: `run(briefing: str) -> str` (returns raw JSON text). Real impl `SdkRunner` uses `claude_agent_sdk.query()`; tests use `FakeRunner`.
  - `briefing_for(app_name: str, version: str, surface: UIContainer) -> str` — the full agent instruction: identity questions + "group these surface elements into feature stubs with trigger paths" + the exact output JSON schema + one filled example.
  - `run_skeleton_agent(runner: AgentRunner, app_name: str, version: str, surface: UIContainer, writer: KBWriter, journal: Journal) -> AppNode` — parses/validates agent output as `AppNode` (pydantic = enforcement; a bad response raises and is journaled `outcome="failed: invalid-agent-output"`), then `writer.write_app(...)`.

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/unit/test_stage1_agent.py
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
```

- [ ] **Step 2: Run to verify they fail**

Run: `python -m pytest tests/unit/test_stage1_agent.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# pipeline/stage1_agent.py
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
        from claude_agent_sdk import query

        async def _go() -> str:
            chunks: list[str] = []
            async for message in query(prompt=briefing):
                for block in getattr(message, "content", []) or []:
                    text = getattr(block, "text", None)
                    if text:
                        chunks.append(text)
            text = "".join(chunks)
            start, end = text.find("{"), text.rfind("}")
            return text[start:end + 1] if start != -1 else text
        return anyio.run(_go)
```

- [ ] **Step 4: Run unit tests; add the live smoke (optional, needs API key)**

```python
# tests/smoke/test_stage1_agent_live.py
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
```

Run: `python -m pytest tests/unit/test_stage1_agent.py -v`
Expected: PASS (3 tests). Live test only via `python -m pytest -m agent_live -v` with `ANTHROPIC_API_KEY` set.

- [ ] **Step 5: Commit**

```bash
git add pipeline/stage1_agent.py tests/unit/test_stage1_agent.py tests/smoke/test_stage1_agent_live.py
git commit -m "feat: skeleton agent briefing + validated AppNode output (SDK + fake runners)"
```

---

### Task 13: CLI + acceptance runs on Notepad and Word

**Files:**
- Create: `pipeline/run.py`
- Test: `tests/unit/test_cli.py`

**Interfaces:**
- Consumes: everything above.
- Produces: `python -m pipeline.run <app> [--stages 0,1] [--kb-root kb] [--configs configs/apps] [--no-agent] [--max-containers N]`. `--no-agent` stops after the surface scan (no API cost). Exit code 0 on success; non-zero + journaled error otherwise. `main(argv) -> int` for testability.

- [ ] **Step 1: Write the failing unit test (arg parsing only; run wiring is covered by smoke/acceptance)**

```python
# tests/unit/test_cli.py
from pipeline.run import parse_args

def test_defaults():
    a = parse_args(["notepad"])
    assert a.app == "notepad" and a.stages == "0,1" and not a.no_agent

def test_flags():
    a = parse_args(["word", "--no-agent", "--max-containers", "5"])
    assert a.no_agent and a.max_containers == 5
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest tests/unit/test_cli.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Implement**

```python
# pipeline/run.py
import argparse, sys, uuid
from pathlib import Path
from pipeline.config import load_app_config
from pipeline import stage0, stage1_surface
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import JournalEvent

def parse_args(argv):
    p = argparse.ArgumentParser(prog="pipeline.run")
    p.add_argument("app")
    p.add_argument("--stages", default="0,1")
    p.add_argument("--kb-root", default="kb")
    p.add_argument("--configs", default="configs/apps")
    p.add_argument("--no-agent", action="store_true")
    p.add_argument("--max-containers", type=int, default=50)
    return p.parse_args(argv)

def main(argv=None) -> int:
    a = parse_args(argv if argv is not None else sys.argv[1:])
    cfg = load_app_config(a.app, Path(a.configs))
    journal = Journal(Path(a.kb_root) / a.app / "journal.jsonl", run_id=uuid.uuid4().hex[:8])
    writer = KBWriter(Path(a.kb_root), a.app)
    try:
        session = stage0.launch(cfg, journal)
        stage0.assert_version(Path(a.kb_root) / a.app / "app.json", session.version)
        if "1" in a.stages.split(","):
            surface_paths = stage1_surface.scan_surface(session, writer, journal,
                                                        max_containers=a.max_containers)
            if not a.no_agent:
                from pipeline.stage1_agent import SdkRunner, run_skeleton_agent
                from tools.models import UIContainer
                import json as _json
                surface = UIContainer.model_validate_json(surface_paths[0].read_text(encoding="utf-8"))
                run_skeleton_agent(SdkRunner(), cfg.name, session.version, surface, writer, journal)
        return 0
    except Exception as exc:  # journal, then loud failure
        journal.append(JournalEvent(actor="run", action="error", target=a.app, outcome=f"failed: {exc}"))
        raise

if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run unit tests, then the two acceptance runs**

Run: `python -m pytest tests/unit/test_cli.py -v` → PASS
Then (manual acceptance, minutes each):

```bash
python -m pipeline.run notepad
# Expect: kb/notepad/{app.json, ui/main-window.json, screenshots/..., journal.jsonl}
# app.json has >=2 features, every feature's trigger_path starts at ui:main-window

python -m pipeline.run word --no-agent --max-containers 10
# Expect: kb/word/ui/main-window.json with ribbon-tab-level elements, screenshot, journal; exits 0
```

Verify: open both `journal.jsonl` files — every action present, no silent steps. Full `pytest` still green in seconds.

- [ ] **Step 5: Commit**

```bash
git add pipeline/run.py tests/unit/test_cli.py
git commit -m "feat: pipeline CLI with stage selection, agent toggle, scope caps"
```

---

## Acceptance criteria for Plan A (definition of done)

1. `python -m pytest` — all unit tests pass in seconds, no GUI needed.
2. `python -m pytest -m smoke` — all smoke tests pass on a Windows machine with Notepad.
3. `python -m pipeline.run notepad` produces a valid `kb/notepad/` (app.json + UI container + screenshot + journal) with ≥2 sensible features.
4. `python -m pipeline.run word --no-agent --max-containers 10` produces a scoped `kb/word/` surface in minutes.
5. Zero app-specific logic outside `configs/apps/` and `kb/` (grep check: "notepad"/"word" appear only in configs, kb, tests, and docs).

## Explicitly deferred to Plan B/C

- Feature/subfeature deep rubric models, `affects/uses` edges, shortcut registry files, `graph.json`
- Breadth fan-out (Stage 2), assembly + completeness check + priority mechanics (Stage 3)
- Depth pass (Stage 4), finalize/recompute (Stage 5), docs harvest (Stage 1b of the spec)
- Web backend (browser automation), object-model (COM) tool, icon cropping into `Icon.image`
- Container drill-down below the surface layer (menus/dialogs interiors)

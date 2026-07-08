# P1 Plan B1: Interactive Skeleton — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** The pipeline stops being a passive observer: it presses things and records what happens. Deliverables: element ids everywhere; a snapshot-diff prober (press → observe → classify → restore); an exhaustive surface sweep (every ribbon tab's face, every menu opened and captured, `opens` markers measured not assumed); agent-driven ready-state discovery that records replayable routes; and the Plan A debt bundle (true version pinning, teardown, honest dismissal timing).

**Architecture:** Deterministic code drives everything mechanical (sweeping tabs, probing, diffing); one new agent capability (the driving agent with custom UI tools via the Claude Agent SDK's in-process MCP server) is introduced for ready-state discovery only — Plan B2's breadth inspectors will reuse that harness. Everything discovered by interaction is classified from *measured state deltas* (window-set diffs + UIA child diffs), never from metadata guesses.

**Tech Stack:** unchanged — Python 3.13, pydantic v2, pywinauto/pywin32, Pillow, claude-agent-sdk, pytest.

## Global Constraints

- **Generality:** no app-specific logic in `pipeline/` or `tools/`; app data only in `configs/apps/*.json`, fixtures, tests. A fix that helps one test app but breaks another is a pipeline bug.
- **Exactly-one marker** per element (`triggers`/`opens`/`unexplored`) — unchanged, enforced by models.
- **Measured, not assumed:** an `opens` marker may ONLY be written from an observed probe outcome (a window/flyout/expansion that actually appeared). Unprobed elements stay `unexplored`.
- **Journal everything:** every probe, sweep step, dismissal, route replay — with honest outcomes (`ambiguous` and `failed:` are valid outcomes; silence is not).
- **Restore after probe:** every probe must leave the app in the state it found it (ESC/close + verify window set restored) or journal `failed: unrestored` loudly.
- **Runs write only inside `kb/<app>/`** — discovered ready-routes are recorded to `kb/<app>/scripts/drive/`, never to `configs/` (promotion to config is a manual, reviewed step).
- **Driving agents are hermetic:** `setting_sources=[]`, and ONLY our custom UI tools exposed; max-turns capped.
- **Test pyramid unchanged:** default `pytest` needs no GUI; smoke files run ONE AT A TIME; Word runs scoped via knobs; probing smoke uses Notepad.
- Commit messages end with "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>".

## File Structure

```
tools/ids.py                      # slug + element/container id generation
tools/models.py                   # MODIFY: UIElement.id field
tools/winapp/windows.py           # MODIFY: window_process_path(hwnd)
pipeline/config.py                # MODIFY: flyout_classes default [] (data moves to word.json)
pipeline/stage0.py                # MODIFY: version from attached window; ESC grace poll; ready-route replay
pipeline/teardown.py              # close the launched app at run end (journaled)
pipeline/prober.py                # press-observe-classify-restore
pipeline/stage1_sweep.py          # exhaustive tab sweep + menu capture, updates markers
pipeline/agent_harness.py         # SDK in-process MCP server with UI tools + driving-agent runner
pipeline/ready_state.py           # discovery briefing, route recording (kb/<app>/scripts/drive/), replay
pipeline/run.py                   # MODIFY: sweep in stage 1, teardown, --max-tabs/--no-sweep knobs
configs/apps/word.json            # MODIFY: flyout classes move here (data)
tests/unit/...  tests/smoke/...   # per module
```

---

### Task 1: Element ids

**Files:**
- Create: `tools/ids.py`
- Modify: `tools/models.py` (UIElement gains `id: Optional[str] = None`), `pipeline/stage1_surface.py` (scan populates ids)
- Test: `tests/unit/test_ids.py`, extend `tests/unit/test_surface_build.py`

**Interfaces:**
- Produces: `slug(text: str) -> str` (lowercase, ascii-fold, non-alnum → `-`, collapse, trim, max 60); `element_id(container_id: str, label: str, ordinal: int) -> str` → `"el:<container-sans-prefix>/<slug>"` with `-<ordinal>` suffix appended only when ordinal > 0. `build_surface` assigns ids with per-slug ordinals (duplicate labels get `-1`, `-2`, …).

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_ids.py
from tools.ids import slug, element_id

def test_slug_folds_and_collapses():
    assert slug("Font Color…") == "font-color"
    assert slug("  Büyük  Harf ") == "buyuk-harf"          # ascii-fold non-English letters
    assert slug("A" * 100) == "a" * 60

def test_element_id_shape_and_ordinals():
    assert element_id("ui:main-window", "Bold", 0) == "el:main-window/bold"
    assert element_id("ui:tab-home", "Bold", 2) == "el:tab-home/bold-2"
```

```python
# append to tests/unit/test_surface_build.py
def test_build_surface_assigns_unique_element_ids():
    kids = [ElemInfo("MenuItem", "File", (0, 0, 40, 20), ""),
            ElemInfo("Button", "Close", (0, 0, 10, 10), ""),
            ElemInfo("Button", "Close", (10, 0, 20, 10), "")]
    c = build_surface(WIN, kids, app="notepad")
    ids = [e.id for e in c.children]
    assert ids == ["el:main-window/file", "el:main-window/close", "el:main-window/close-1"]
    assert len(set(ids)) == len(ids)
```

- [ ] **Step 2: Run to verify failure**

Run: `python -m pytest tests/unit/test_ids.py tests/unit/test_surface_build.py -v`
Expected: FAIL — `No module named 'tools.ids'`

- [ ] **Step 3: Implement**

```python
# tools/ids.py
import re, unicodedata

def slug(text: str) -> str:
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    t = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")
    return t[:60].strip("-") or "unnamed"

def element_id(container_id: str, label: str, ordinal: int) -> str:
    base = f"el:{container_id.removeprefix('ui:')}/{slug(label)}"
    return f"{base}-{ordinal}" if ordinal else base
```

In `tools/models.py` add to `UIElement`: `id: Optional[str] = None` (after `control_type`).
In `pipeline/stage1_surface.py::build_surface`, assign ids while building:

```python
    counts: dict[str, int] = {}
    elements = []
    for k in children:
        if not k.name.strip() or k.name in exclude_labels:
            continue
        s = slug(k.name)
        elements.append(UIElement(
            id=element_id("ui:main-window", k.name, counts.get(s, 0)),
            control_type=k.control_type.lower(), label=k.name,
            icon=Icon(description="not captured", image=None),
            bounds=k.rect, source="uia", unexplored=True))
        counts[s] = counts.get(s, 0) + 1
```

(Import `slug, element_id` from `tools.ids`. Note: the container id is passed as a literal here; Task 4's sweep reuses the same pattern with its own container ids — extract a small helper `assign_ids(container_id, infos, exclude_labels) -> list[UIElement]` in `stage1_surface.py` and have both call it.)

- [ ] **Step 4: Run to verify pass**

Run: `python -m pytest tests/unit/ -v`
Expected: all pass (existing tests unaffected — `id` is optional with default None)

- [ ] **Step 5: Commit**

```bash
git add tools/ids.py tools/models.py pipeline/stage1_surface.py tests/unit/test_ids.py tests/unit/test_surface_build.py
git commit -m "feat: element ids (el:<container>/<slug>) assigned during surface scan"
```

---

### Task 2: Plan A debt bundle — true version pin, teardown, dismissal grace, flyout classes to config

**Files:**
- Modify: `tools/winapp/windows.py`, `pipeline/stage0.py`, `pipeline/config.py`, `configs/apps/word.json`, `pipeline/run.py`
- Create: `pipeline/teardown.py`
- Test: `tests/unit/test_stage0.py` (extend), `tests/unit/test_teardown.py`, `tests/smoke/test_stage0_smoke.py` (extend)

**Interfaces:**
- Produces: `windows.window_process_path(hwnd) -> str` (image path of the hwnd's owning process, via `win32process.GetWindowThreadProcessId` + `OpenProcess` + `GetModuleFileNameEx`); `stage0.launch` now sets `AppSession.version = file_version(window_process_path(hwnd))` with fallback to `file_version(cfg.exe)` journaled as `outcome="version-fallback"` if the process query fails; ESC dismissal re-checks with a bounded grace poll (up to 1.5s, 0.3s steps) before journaling `failed: still-present`; `teardown.close_app(session, journal) -> None` (WM_CLOSE, wait up to 3s, then taskkill by the window pid, journal actual outcome); `pipeline/config.py` `flyout_classes: list[str] = []` (Office strings move to `configs/apps/word.json`).

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_teardown.py
from unittest.mock import patch
from pipeline.teardown import close_app
from tools.journal import Journal
from tools.models import JournalEvent

class FakeSession:
    hwnd = 1234
    class config: name = "x"

def test_close_app_journals_closed_when_window_gone(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.teardown.win32gui.PostMessage"), \
         patch("pipeline.teardown._window_alive", side_effect=[True, False]):
        close_app(FakeSession(), j)
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "closed"

def test_close_app_falls_back_to_kill(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.teardown.win32gui.PostMessage"), \
         patch("pipeline.teardown._window_alive", return_value=True), \
         patch("pipeline.teardown._kill_by_hwnd_pid") as kill:
        close_app(FakeSession(), j)
    kill.assert_called_once()
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "killed"
```

```python
# append to tests/unit/test_stage0.py
from unittest.mock import patch
from pipeline.stage0 import resolve_session_version

def test_version_prefers_window_process(tmp_path):
    with patch("pipeline.stage0.window_process_path", return_value="C:\\real\\app.exe"), \
         patch("pipeline.stage0.file_version", return_value="11.1.0.0") as fv:
        v = resolve_session_version(1234, "stub.exe", journal=None)
    assert v == "11.1.0.0"
    fv.assert_called_once_with("C:\\real\\app.exe")

def test_version_falls_back_to_exe(tmp_path):
    from tools.journal import Journal
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.stage0.window_process_path", side_effect=OSError("denied")), \
         patch("pipeline.stage0.file_version", return_value="1.0") :
        v = resolve_session_version(1234, "stub.exe", journal=j)
    assert v == "1.0"
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "version-fallback"
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/unit/test_teardown.py tests/unit/test_stage0.py -v` → FAIL (missing module/function)

- [ ] **Step 3: Implement**

```python
# tools/winapp/windows.py — append
import win32api, win32con, win32process

def window_process_path(hwnd: int) -> str:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
    try:
        return win32process.GetModuleFileNameEx(h, 0)
    finally:
        win32api.CloseHandle(h)
```

```python
# pipeline/teardown.py
import time
import win32con, win32gui, win32process
import subprocess
from tools.models import JournalEvent

def _window_alive(hwnd: int) -> bool:
    return bool(win32gui.IsWindow(hwnd)) and bool(win32gui.IsWindowVisible(hwnd))

def _kill_by_hwnd_pid(hwnd: int) -> None:
    _, pid = win32process.GetWindowThreadProcessId(hwnd)
    subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)

def close_app(session, journal) -> None:
    hwnd = session.hwnd
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    deadline = time.monotonic() + 3.0
    while time.monotonic() < deadline and _window_alive(hwnd):
        time.sleep(0.3)
    if _window_alive(hwnd):
        _kill_by_hwnd_pid(hwnd)
        journal.append(JournalEvent(actor="teardown", action="close", target=session.config.name, outcome="killed"))
    else:
        journal.append(JournalEvent(actor="teardown", action="close", target=session.config.name, outcome="closed"))
```

In `pipeline/stage0.py`:

```python
from tools.winapp.windows import top_windows, wait_new_window, window_process_path

def resolve_session_version(hwnd: int, exe: str, journal) -> str:
    # A store-app's launcher stub (cfg.exe) is not the running binary; the
    # attached window's owning process is. Prefer it; fall back loudly.
    try:
        return file_version(window_process_path(hwnd))
    except Exception:
        if journal is not None:
            journal.append(JournalEvent(actor="stage0", action="version", target=exe,
                                        outcome="version-fallback"))
        return file_version(exe)
```

In `launch()`: replace `version = file_version(cfg.exe)` with `version = resolve_session_version(ui._win.handle, cfg.exe, journal)`. In the dismissal loop, replace the immediate still-present check with a grace poll:

```python
                deadline = time.monotonic() + 1.5
                while time.monotonic() < deadline and any(w2.hwnd == w.hwnd for w2 in top_windows()):
                    time.sleep(0.3)
                still_present = any(w2.hwnd == w.hwnd for w2 in top_windows())
```

In `pipeline/config.py`: `flyout_classes: list[str] = []`. In `configs/apps/word.json` add `"flyout_classes": ["Net UI Tool Window", "MsoCommandBarPopup"]`. In `pipeline/run.py::main`, wrap the post-launch work in `try/finally` with `teardown.close_app(session, journal)` in the finally block (after the version.json write; a `--keep-open` flag skips it).

- [ ] **Step 4: Run to verify pass** — `python -m pytest -v` all green; then `python -m pytest tests/smoke/test_stage0_smoke.py -m smoke -v` (extend it to assert no Notepad window remains after `close_app` — reuse `_window_alive`).

- [ ] **Step 5: Commit**

```bash
git add tools/winapp/windows.py pipeline/teardown.py pipeline/stage0.py pipeline/config.py configs/apps/word.json pipeline/run.py tests/
git commit -m "feat: window-process version pinning, journaled teardown, dismissal grace poll, flyout classes to config"
```

---

### Task 3: The prober — press, observe, classify, restore

**Files:**
- Create: `pipeline/prober.py`
- Test: `tests/unit/test_prober_classify.py`, `tests/smoke/test_prober_smoke.py`

**Interfaces:**
- Produces: `ProbeObservation(new_window, child_delta, before_windows, after_windows)` (dataclass); pure `classify_probe(obs, dialog_classes, flyout_classes) -> str` returning one of `"opens-dialog" | "opens-flyout" | "expands-inline" | "no-effect"`; and `probe_element(session, elem: UIElement, journal) -> ProbeResult(kind: str, new_window: WinInfo | None, expanded: list[ElemInfo], restored: bool)` which: snapshots windows + child count → `ensure_foreground` → `click_rect(elem.bounds)` → waits (`wait_new_window`, timeout 2.5) → rescans → classifies → captures expansion/new-window children (via a fresh `UIASession` scan of the new window for dialogs, or the session tree diff for inline expansion) → restores (ESC once for flyout/inline; WM_CLOSE then ESC for dialogs; verify window set == before, else `restored=False`) → journals `action="probe"` with the outcome. Skips disabled/zero-area elements (journal `outcome="skipped-disabled"`). Consumed by Task 4 (menu capture) and all of Plan B2.

- [ ] **Step 1: Write the failing unit tests (pure classification)**

```python
# tests/unit/test_prober_classify.py
from pipeline.prober import ProbeObservation, classify_probe
from tools.winapp.windows import WinInfo

W = lambda h, t, c: WinInfo(h, t, c)
BASE = [W(1, "Main", "AppClass")]

def obs(new=None, delta=0):
    after = BASE + ([new] if new else [])
    return ProbeObservation(new_window=new, child_delta=delta,
                            before_windows=BASE, after_windows=after)

def test_dialog_class_wins():
    assert classify_probe(obs(new=W(2, "Save As", "#32770")), ["#32770"], []) == "opens-dialog"

def test_flyout_class():
    assert classify_probe(obs(new=W(2, "", "Net UI Tool Window")), ["#32770"], ["Net UI Tool Window"]) == "opens-flyout"

def test_unknown_new_window_is_dialog_by_default():
    assert classify_probe(obs(new=W(2, "Popup", "Weird")), ["#32770"], []) == "opens-dialog"

def test_inline_expansion():
    assert classify_probe(obs(new=None, delta=12), ["#32770"], []) == "expands-inline"

def test_no_effect():
    assert classify_probe(obs(new=None, delta=0), ["#32770"], []) == "no-effect"
```

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement**

```python
# pipeline/prober.py
import time
from dataclasses import dataclass, field
from tools.models import JournalEvent, UIElement
from tools.winapp.uia import ElemInfo, UIASession
from tools.winapp.windows import WinInfo, top_windows, wait_new_window, classify
from tools.winapp import inputs

EXPANSION_THRESHOLD = 3   # named children appearing in-tree = a menu/dropdown expanded

@dataclass
class ProbeObservation:
    new_window: WinInfo | None
    child_delta: int
    before_windows: list[WinInfo]
    after_windows: list[WinInfo]

@dataclass
class ProbeResult:
    kind: str
    new_window: WinInfo | None = None
    expanded: list[ElemInfo] = field(default_factory=list)
    restored: bool = True

def classify_probe(obs: ProbeObservation, dialog_classes, flyout_classes) -> str:
    if obs.new_window is not None:
        k = classify(obs.new_window.cls, dialog_classes, flyout_classes)
        return "opens-flyout" if k == "flyout" else "opens-dialog"
    if obs.child_delta >= EXPANSION_THRESHOLD:
        return "expands-inline"
    return "no-effect"

def _named_children(session, depth):
    return [k for k in session.ui.children(depth=depth) if k.name.strip()]

def probe_element(session, elem: UIElement, journal, scan_depth: int = 9) -> ProbeResult:
    from pipeline.stage1_surface import DEFAULT_SCAN_DEPTH
    scan_depth = scan_depth or DEFAULT_SCAN_DEPTH
    if elem.bounds is None or (elem.bounds[2] - elem.bounds[0]) <= 0:
        journal.append(JournalEvent(actor="prober", action="probe", target=elem.id or elem.label,
                                    outcome="skipped-disabled"))
        return ProbeResult(kind="skipped")
    before_w = top_windows()
    before_c = _named_children(session, scan_depth)
    inputs.ensure_foreground(session.hwnd)
    inputs.click_rect(elem.bounds)
    new_win = wait_new_window(before_w, timeout=2.5)
    time.sleep(0.3)
    after_c = _named_children(session, scan_depth)
    obs = ProbeObservation(new_window=new_win, child_delta=len(after_c) - len(before_c),
                           before_windows=before_w, after_windows=top_windows())
    kind = classify_probe(obs, session.config.dialog_classes, session.config.flyout_classes)
    result = ProbeResult(kind=kind, new_window=new_win)
    if kind == "expands-inline":
        before_keys = {(k.name, k.rect) for k in before_c}
        result.expanded = [k for k in after_c if (k.name, k.rect) not in before_keys]
    elif kind in ("opens-dialog", "opens-flyout") and new_win is not None:
        try:
            import re
            popup = UIASession.attach(re.escape(new_win.title)) if new_win.title else None
            result.expanded = [k for k in popup.children(depth=4) if k.name.strip()] if popup else []
        except Exception:
            result.expanded = []
    # restore
    if kind in ("opens-dialog", "opens-flyout", "expands-inline"):
        inputs.press("{ESC}")
        time.sleep(0.3)
        if new_win is not None and any(w.hwnd == new_win.hwnd for w in top_windows()):
            import win32con, win32gui
            win32gui.PostMessage(new_win.hwnd, win32con.WM_CLOSE, 0, 0)
            time.sleep(0.4)
        result.restored = {w.hwnd for w in top_windows()} == {w.hwnd for w in before_w}
    journal.append(JournalEvent(actor="prober", action="probe", target=elem.id or elem.label,
                                outcome=kind if result.restored else f"{kind}; failed: unrestored",
                                data={"expanded": len(result.expanded)}))
    return result
```

- [ ] **Step 4: Write + run the smoke test**

```python
# tests/smoke/test_prober_smoke.py
import pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.prober import probe_element
from pipeline.stage1_surface import scan_surface
from pipeline.teardown import close_app
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.models import UIContainer
import json

pytestmark = pytest.mark.smoke

def test_probe_notepad_file_menu(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "j.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        paths = scan_surface(s, KBWriter(tmp_path, "notepad"), j)
        c = UIContainer.model_validate_json(paths[0].read_text(encoding="utf-8"))
        file_item = next(e for e in c.children if (e.id or "").endswith("/file") or e.label in ("File", "Dosya"))
        r = probe_element(s, file_item, j)
        assert r.kind in ("expands-inline", "opens-flyout"), r.kind
        assert len(r.expanded) >= 3          # New / Open / Save ... appeared
        assert r.restored
    finally:
        close_app(s, j)
```

Run: `python -m pytest tests/unit/test_prober_classify.py -v` then `python -m pytest tests/smoke/test_prober_smoke.py -m smoke -v`
Expected: PASS both. (If the File menu id differs on this machine's locale, match by the established auto_id/label-pair pattern from sibling smoke tests — adapt the TEST selection only, with evidence.)

- [ ] **Step 5: Commit**

```bash
git add pipeline/prober.py tests/unit/test_prober_classify.py tests/smoke/test_prober_smoke.py
git commit -m "feat: snapshot-diff prober - press, observe, classify, restore"
```

---

### Task 4: Exhaustive surface sweep — every tab face, every menu, measured markers

**Files:**
- Create: `pipeline/stage1_sweep.py`
- Test: `tests/unit/test_sweep_build.py`, `tests/smoke/test_sweep_smoke.py`

**Interfaces:**
- Produces: `sweep(session, writer, journal, max_tabs: int | None = None) -> list[Path]`:
  1. Reads the main container (already scanned). **Tab sweep:** for each element whose `control_type` is `"tabitem"` (general UIA type; cap at `max_tabs` if set — journal the cap), click it, rescan, diff against the pre-click named-children set, build `UIContainer(id=f"ui:tab-{slug(label)}", kind="tab", children=assign_ids(...diff...), screenshot=writer.save_screenshot(...))`, write it, and set the tab element's marker in the main container to `opens="ui:tab-<slug>"`.
  2. **Menu capture:** for each element with `control_type` in `("menuitem", "menu item")` in the main container, `probe_element`; when the result is `expands-inline`/`opens-flyout` with expanded elements, build `UIContainer(id=f"ui:menu-{slug(label)}", kind="menu", children=assign_ids(expanded))`, write, and set the element's marker to `opens=...`.
  3. Rewrite the main container file with the updated markers (elements that opened something are no longer `unexplored`; everything unprobed stays `unexplored`).
  Pure part for unit tests: `face_diff(before: list[ElemInfo], after: list[ElemInfo]) -> list[ElemInfo]` (named elements present after but not before, keyed by (name, rect)).
- Consumes: `probe_element` (Task 3), `assign_ids` (Task 1), `slug`, `KBWriter`, `capture`.

- [ ] **Step 1: Write the failing unit test**

```python
# tests/unit/test_sweep_build.py
from pipeline.stage1_sweep import face_diff
from tools.winapp.uia import ElemInfo

def test_face_diff_returns_only_new_named_elements():
    before = [ElemInfo("Button", "Bold", (0, 0, 1, 1), ""), ElemInfo("Pane", "", (0, 0, 9, 9), "")]
    after = before + [ElemInfo("Button", "Margins", (5, 0, 6, 1), ""), ElemInfo("Pane", "", (1, 1, 2, 2), "")]
    diff = face_diff(before, after)
    assert [d.name for d in diff] == ["Margins"]
```

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement**

```python
# pipeline/stage1_sweep.py
import time
from pathlib import Path
from tools.ids import slug
from tools.models import JournalEvent, UIContainer
from tools.winapp import capture
from tools.winapp.uia import ElemInfo
from tools.journal import Journal
from tools.kb_writer import KBWriter
from pipeline.prober import probe_element
from pipeline.stage1_surface import DEFAULT_SCAN_DEPTH, assign_ids
from tools.winapp import inputs

def face_diff(before: list[ElemInfo], after: list[ElemInfo]) -> list[ElemInfo]:
    seen = {(k.name, k.rect) for k in before if k.name.strip()}
    return [k for k in after if k.name.strip() and (k.name, k.rect) not in seen]

def _named(session):
    return [k for k in session.ui.children(depth=DEFAULT_SCAN_DEPTH) if k.name.strip()]

def sweep(session, writer: KBWriter, journal: Journal, max_tabs: int | None = None) -> list[Path]:
    main_path = writer.root / "ui" / "main-window.json"
    main = UIContainer.model_validate_json(main_path.read_text(encoding="utf-8"))
    written: list[Path] = []
    exclude = tuple(session.config.boundaries.exclude_labels)

    tabs = [e for e in main.children if e.control_type == "tabitem" and e.label not in exclude]
    if max_tabs is not None and len(tabs) > max_tabs:
        journal.append(JournalEvent(actor="stage1.sweep", action="cap", target="tabs",
                                    outcome="capped", data={"total": len(tabs), "kept": max_tabs}))
        tabs = tabs[:max_tabs]
    for tab in tabs:
        pre = _named(session)
        inputs.ensure_foreground(session.hwnd)
        inputs.click_rect(tab.bounds)
        time.sleep(0.6)
        post = _named(session)
        cid = f"ui:tab-{slug(tab.label)}"
        face = face_diff(pre, post)
        container = UIContainer(id=cid, kind="tab", label=tab.label,
                                children=assign_ids(cid, face, exclude))
        img = capture.grab_region(session.ui.window_rect())
        container.screenshot = writer.save_screenshot(img, cid, "face")
        written.append(writer.write_container(container))
        tab.opens, tab.unexplored = cid, False
        journal.append(JournalEvent(actor="stage1.sweep", action="sweep-tab", target=cid,
                                    outcome="ok", data={"elements": len(container.children)}))

    menus = [e for e in main.children if e.control_type in ("menuitem", "menu item")
             and e.label not in exclude]
    for m in menus:
        r = probe_element(session, m, journal)
        if r.kind in ("expands-inline", "opens-flyout") and r.expanded:
            cid = f"ui:menu-{slug(m.label)}"
            container = UIContainer(id=cid, kind="menu", label=m.label,
                                    children=assign_ids(cid, r.expanded, exclude))
            written.append(writer.write_container(container))
            m.opens, m.unexplored = cid, False

    writer.write_container(main)          # markers updated: measured opens, honest unexplored
    return written
```

(`assign_ids(container_id, infos, exclude_labels)` is the helper extracted in Task 1. Note `tab.opens/tab.unexplored` mutation relies on pydantic model mutability — default in v2; if the models are configured frozen anywhere, rebuild the element instead.)

- [ ] **Step 4: Write + run the smoke test**

```python
# tests/smoke/test_sweep_smoke.py
import json, pytest
from pathlib import Path
from pipeline.config import load_app_config
from pipeline.stage0 import launch
from pipeline.stage1_surface import scan_surface
from pipeline.stage1_sweep import sweep
from pipeline.teardown import close_app
from tools.journal import Journal
from tools.kb_writer import KBWriter

pytestmark = pytest.mark.smoke

def test_sweep_captures_notepad_menus(tmp_path: Path):
    cfg = load_app_config("notepad", Path("configs/apps"))
    j = Journal(tmp_path / "notepad" / "journal.jsonl", run_id="smoke")
    s = launch(cfg, j)
    try:
        w = KBWriter(tmp_path, "notepad")
        scan_surface(s, w, j)
        written = sweep(s, w, j)
        names = [p.name for p in written]
        assert any(n.startswith("menu-") for n in names), names   # File/Edit/View captured
        main = json.loads((tmp_path / "notepad" / "ui" / "main-window.json").read_text(encoding="utf-8"))
        opened = [e for e in main["children"] if e.get("opens")]
        assert opened, "menu elements should now carry measured opens markers"
        menu_file = json.loads(written[0].read_text(encoding="utf-8"))
        assert len(menu_file["children"]) >= 3
    finally:
        close_app(s, j)
```

Run: `python -m pytest tests/unit/test_sweep_build.py -v` then `python -m pytest tests/smoke/test_sweep_smoke.py -m smoke -v`
Expected: PASS. Then a scoped Word sanity (manual, not a test): `python -m pipeline.run word --no-agent --max-tabs 2` after Task 6 wires it — deferred to Task 6's acceptance.

- [ ] **Step 5: Commit**

```bash
git add pipeline/stage1_sweep.py tests/unit/test_sweep_build.py tests/smoke/test_sweep_smoke.py
git commit -m "feat: exhaustive surface sweep - tab faces and menus with measured opens markers"
```

---

### Task 5: Driving-agent harness — custom UI tools over the Agent SDK

**Files:**
- Create: `pipeline/agent_harness.py`
- Test: `tests/unit/test_agent_harness.py`

**Interfaces:**
- Produces: `make_ui_tools(session, writer, journal) -> list` — SDK custom tools (in-process MCP, `claude_agent_sdk.tool` + `create_sdk_mcp_server`), each a thin wrapper over existing capabilities, all journaled:
  - `ui_snapshot()` → JSON list of the main container's current named elements (id/label/control_type/bounds) — re-scanned live
  - `ui_click(element_label: str)` → clicks the first element whose label or id matches; returns what changed (`new window: <title/class>` / `expanded N elements` / `no visible change`) — implemented via `probe_element` WITHOUT restore (the agent is navigating, not probing)
  - `ui_press(keys: str)` → `inputs.press`
  - `ui_windows()` → current top-level windows (title/class)
  - `record_route(steps_json: str)` → validates and writes `kb/<app>/scripts/drive/ready_route.json`; returns the saved path
- `run_driving_agent(briefing: str, tools, max_turns: int = 15) -> str` — hermetic (`setting_sources=[]`), ONLY these tools allowed, returns final text. VERIFY the exact SDK API for custom tools against the installed claude-agent-sdk (0.2.113: `tool` decorator, `create_sdk_mcp_server`, `ClaudeAgentOptions(mcp_servers=..., allowed_tools=..., max_turns=...)`) — adapt mechanically if names differ, record evidence in the report.
- Unit tests use the tool functions directly with a fake session (no SDK call, no GUI): `ui_snapshot` returns the fake elements; `record_route` writes the file and rejects malformed steps.

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/unit/test_agent_harness.py
import json, pytest
from pathlib import Path
from pipeline.agent_harness import snapshot_impl, record_route_impl
from tools.journal import Journal
from tools.winapp.uia import ElemInfo

class FakeUI:
    def children(self, depth=1):
        return [ElemInfo("Button", "Blank document", (0, 0, 10, 10), "")]
class FakeSession:
    ui = FakeUI(); hwnd = 1
    class config:
        name = "x"
        class boundaries: exclude_labels = []

def test_snapshot_impl_lists_named_elements(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    out = json.loads(snapshot_impl(FakeSession(), j))
    assert out[0]["label"] == "Blank document" and "bounds" in out[0]

def test_record_route_impl_writes_and_validates(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    p = record_route_impl(tmp_path / "x", '[{"click_label_re": "Blank document"}]', j)
    assert json.loads(Path(p).read_text(encoding="utf-8"))[0]["click_label_re"]
    with pytest.raises(ValueError):
        record_route_impl(tmp_path / "x", '[{"bogus": 1}]', j)
```

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement**

```python
# pipeline/agent_harness.py
import json
from pathlib import Path
from tools.models import JournalEvent
from tools.winapp.uia import ElemInfo

def snapshot_impl(session, journal) -> str:
    els = [k for k in session.ui.children(depth=9) if k.name.strip()]
    journal.append(JournalEvent(actor="agent.ui", action="snapshot", outcome="ok",
                                data={"elements": len(els)}))
    return json.dumps([{"label": k.name, "control_type": k.control_type, "bounds": k.rect}
                       for k in els])

def record_route_impl(kb_app_root: Path, steps_json: str, journal) -> str:
    steps = json.loads(steps_json)
    if not isinstance(steps, list) or not all(
            isinstance(s, dict) and "click_label_re" in s for s in steps):
        raise ValueError("route steps must be a list of {click_label_re: ...}")
    out = Path(kb_app_root) / "scripts" / "drive" / "ready_route.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(steps, indent=2), encoding="utf-8")
    journal.append(JournalEvent(actor="agent.ui", action="record-route", target=str(out), outcome="ok"))
    return str(out)

def make_ui_tools(session, kb_app_root: Path, journal):
    from claude_agent_sdk import tool

    @tool("ui_snapshot", "List the app's currently visible named UI elements", {})
    async def ui_snapshot(args):
        return {"content": [{"type": "text", "text": snapshot_impl(session, journal)}]}

    @tool("ui_click", "Click the element whose label matches", {"element_label": str})
    async def ui_click(args):
        from tools.winapp import inputs
        els = [k for k in session.ui.children(depth=9) if k.name.strip()]
        target = next((k for k in els if args["element_label"].lower() in k.name.lower()), None)
        if target is None:
            return {"content": [{"type": "text", "text": "no element matched"}]}
        inputs.ensure_foreground(session.hwnd); inputs.click_rect(target.rect)
        import time; time.sleep(0.8)
        journal.append(JournalEvent(actor="agent.ui", action="click", target=target.name, outcome="ok"))
        return {"content": [{"type": "text", "text": f"clicked '{target.name}'"}]}

    @tool("ui_press", "Press keys (pywinauto send_keys syntax)", {"keys": str})
    async def ui_press(args):
        from tools.winapp import inputs
        inputs.press(args["keys"])
        journal.append(JournalEvent(actor="agent.ui", action="press", target=args["keys"], outcome="ok"))
        return {"content": [{"type": "text", "text": "pressed"}]}

    @tool("record_route", "Record the ready-state route as JSON steps", {"steps_json": str})
    async def record_route(args):
        return {"content": [{"type": "text", "text": record_route_impl(kb_app_root, args["steps_json"], journal)}]}

    return [ui_snapshot, ui_click, ui_press, record_route]

def run_driving_agent(briefing: str, sdk_tools, max_turns: int = 15) -> str:
    import anyio
    from claude_agent_sdk import ClaudeAgentOptions, create_sdk_mcp_server, query

    server = create_sdk_mcp_server(name="ui", tools=sdk_tools)
    options = ClaudeAgentOptions(
        setting_sources=[], mcp_servers={"ui": server},
        allowed_tools=[f"mcp__ui__{t.name if hasattr(t, 'name') else ''}" for t in sdk_tools] or None,
        max_turns=max_turns)

    async def _go() -> str:
        chunks = []
        async for message in query(prompt=briefing, options=options):
            for block in getattr(message, "content", []) or []:
                text = getattr(block, "text", None)
                if text:
                    chunks.append(text)
        return "".join(chunks)
    return anyio.run(_go)
```

(The SDK-facing parts — `tool` decorator return shape, `allowed_tools` naming (`mcp__<server>__<tool>`), `create_sdk_mcp_server` — must be verified against the installed SDK by inspection, as Task 12 of Plan A did; adapt mechanically and record evidence. The `_impl` functions are the tested logic and must stay SDK-free.)

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/unit/test_agent_harness.py -v` and full suite green.

- [ ] **Step 5: Commit**

```bash
git add pipeline/agent_harness.py tests/unit/test_agent_harness.py
git commit -m "feat: driving-agent harness - hermetic SDK agent with custom UI tools"
```

---

### Task 6: Ready-state discovery, recording, and replay

**Files:**
- Create: `pipeline/ready_state.py`
- Modify: `pipeline/stage0.py` (replay recorded route after attach), `pipeline/run.py` (`--discover-ready` flag)
- Test: `tests/unit/test_ready_state.py`; live validation in Task 7's acceptance

**Interfaces:**
- Produces:
  - `READY_DEFINITION` (str): the general briefing text: *"The ready state is where a user creates or edits the app's primary artifact. NOT ready: template galleries, welcome/launcher screens, sign-in prompts, recent-file lists. Ready: the main working canvas plus primary command surfaces (ribbon/toolbars/menus) are visible. Use ui_snapshot to look, ui_click/ui_press to act. When you reach the ready state, verify with a final ui_snapshot, then call record_route with the minimal steps you took (as [{'click_label_re': ...}]), and reply DONE. If already ready, record an empty route []. Never click destructive-looking controls (Save, Send, Delete, Buy)."*
  - `discover_ready(session, kb_app_root, journal) -> Path | None` — runs the driving agent with Task 5's tools + this briefing; returns the recorded route path (None + journaled failure if the agent didn't record).
  - `replay_route(session, route_path, journal) -> None` — for each step, find element by `click_label_re` against a live snapshot, click, wait; journal each step; raise RuntimeError (journaled `failed: route-step`) if a step's element is missing (loud — the route is stale, rediscovery needed).
  - In `stage0.launch`: after attach + boundary dismissal, if `kb/<app>/scripts/drive/ready_route.json` exists → `replay_route`. In `run.py`: `--discover-ready` runs `discover_ready` after launch (once), then continues the normal stages.
- Unit tests: `replay_route` with a fake session (steps click matching elements; missing element raises + journals); `discover_ready` with a monkeypatched `run_driving_agent` that calls `record_route_impl` (no SDK, no GUI).

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/unit/test_ready_state.py
import json, pytest
from pathlib import Path
from unittest.mock import patch
from pipeline.ready_state import replay_route, discover_ready
from tools.journal import Journal
from tools.winapp.uia import ElemInfo

class FakeUI:
    def children(self, depth=1):
        return [ElemInfo("Button", "Blank document", (0, 0, 10, 10), "")]
class FakeSession:
    ui = FakeUI(); hwnd = 1
    class config: name = "x"

def _route(tmp_path, steps):
    p = tmp_path / "ready_route.json"
    p.write_text(json.dumps(steps), encoding="utf-8")
    return p

def test_replay_clicks_matching_step(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.ready_state.inputs") as fake_inputs:
        replay_route(FakeSession(), _route(tmp_path, [{"click_label_re": "Blank"}]), j)
    fake_inputs.click_rect.assert_called_once()
    assert Journal.read_all(tmp_path / "j.jsonl")[-1].outcome == "ok"

def test_replay_missing_element_fails_loudly(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.ready_state.inputs"), pytest.raises(RuntimeError):
        replay_route(FakeSession(), _route(tmp_path, [{"click_label_re": "No Such"}]), j)
    assert "failed: route-step" in Journal.read_all(tmp_path / "j.jsonl")[-1].outcome

def test_discover_ready_returns_recorded_path(tmp_path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    def fake_agent(briefing, tools, max_turns=15):
        from pipeline.agent_harness import record_route_impl
        record_route_impl(tmp_path / "kb-x", "[]", j)
        return "DONE"
    with patch("pipeline.ready_state.run_driving_agent", side_effect=fake_agent):
        p = discover_ready(FakeSession(), tmp_path / "kb-x", j)
    assert p is not None and Path(p).exists()
```

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement**

```python
# pipeline/ready_state.py
import json, re, time
from pathlib import Path
from tools.models import JournalEvent
from tools.winapp import inputs
from pipeline.agent_harness import make_ui_tools, run_driving_agent

READY_DEFINITION = (
    "You are bringing a desktop application into its READY STATE for inspection.\n"
    "READY = where a user creates or edits the app's primary artifact. NOT ready: template "
    "galleries, welcome/launcher screens, sign-in prompts, recent-file lists. Ready: the main "
    "working canvas plus primary command surfaces (ribbon/toolbars/menus) are visible.\n"
    "Use ui_snapshot to look, ui_click/ui_press to act. When you reach the ready state, verify "
    "with a final ui_snapshot, then call record_route with the MINIMAL steps you took, as "
    "[{\"click_label_re\": \"...\"}], and reply DONE. If the app is already ready, record [].\n"
    "Never click destructive-looking controls (Save, Send, Delete, Buy, Purchase, Share)."
)

def replay_route(session, route_path: Path, journal) -> None:
    steps = json.loads(Path(route_path).read_text(encoding="utf-8"))
    for step in steps:
        pat = step["click_label_re"]
        els = [k for k in session.ui.children(depth=9) if k.name.strip()]
        target = next((k for k in els if re.search(pat, k.name, re.IGNORECASE)), None)
        if target is None:
            journal.append(JournalEvent(actor="ready", action="replay", target=pat,
                                        outcome="failed: route-step"))
            raise RuntimeError(f"ready route step matched nothing: {pat} (route is stale)")
        inputs.ensure_foreground(session.hwnd)
        inputs.click_rect(target.rect)
        time.sleep(0.8)
        journal.append(JournalEvent(actor="ready", action="replay", target=pat, outcome="ok"))

def discover_ready(session, kb_app_root: Path, journal) -> Path | None:
    tools = make_ui_tools(session, kb_app_root, journal)
    run_driving_agent(READY_DEFINITION, tools)
    route = Path(kb_app_root) / "scripts" / "drive" / "ready_route.json"
    if route.exists():
        journal.append(JournalEvent(actor="ready", action="discover", target=str(route), outcome="ok"))
        return route
    journal.append(JournalEvent(actor="ready", action="discover", outcome="failed: no route recorded"))
    return None
```

Wire-up: in `stage0.launch`, after the dismissal loop, add — route replay (path passed in from run.py as an optional argument `ready_route: Path | None = None`, keeping stage0 free of kb-layout knowledge): if `ready_route` is not None and exists → `replay_route(session-under-construction...)`. Simplest correct wiring: perform the replay in `run.py` right after `launch()` returns (session exists there), before `scan_surface`. In `run.py`: add `--discover-ready` flag → call `discover_ready(session, Path(a.kb_root)/a.app, journal)`; on every run, if `kb/<app>/scripts/drive/ready_route.json` exists → `replay_route(...)` before stage 1.

- [ ] **Step 4: Run to verify pass** — `python -m pytest tests/unit/test_ready_state.py -v`; full suite green.

- [ ] **Step 5: Commit**

```bash
git add pipeline/ready_state.py pipeline/stage0.py pipeline/run.py tests/unit/test_ready_state.py
git commit -m "feat: ready-state discovery agent, recorded routes, deterministic replay"
```

---

### Task 7: CLI knobs + B1 acceptance

**Files:**
- Modify: `pipeline/run.py` (`--max-tabs`, `--no-sweep`, `--keep-open`, sweep wired into stage 1)
- Test: extend `tests/unit/test_cli.py`

**Interfaces:**
- `main()` stage 1 order: `scan_surface` → (unless `--no-sweep`) `sweep(session, writer, journal, max_tabs=a.max_tabs)` → optional agent. Teardown in `finally` (Task 2), skipped by `--keep-open`.

- [ ] **Step 1: Extend CLI unit tests**

```python
# append to tests/unit/test_cli.py
def test_b1_flags():
    a = parse_args(["word", "--max-tabs", "3", "--no-sweep", "--keep-open", "--discover-ready"])
    assert a.max_tabs == 3 and a.no_sweep and a.keep_open and a.discover_ready

def test_b1_defaults():
    a = parse_args(["notepad"])
    assert a.max_tabs is None and not a.no_sweep and not a.keep_open and not a.discover_ready
```

- [ ] **Step 2: Run to verify failure**, **Step 3: implement flags + wiring** (argparse additions: `--max-tabs` type=int default None; `--no-sweep`, `--keep-open`, `--discover-ready` store_true; wiring per Task 2/4/6 interface notes), **Step 4: full unit suite green.**

- [ ] **Step 5: Acceptance runs (real, in order; close each app between runs):**

```bash
# a) Notepad full: scan + sweep + agent
python -m pipeline.run notepad
# Expect: kb/notepad/ui/ has main-window.json + menu-*.json containers;
#         main-window elements for menus carry measured opens markers; app.json present.

# b) Word interactive skeleton, scoped then full:
python -m pipeline.run word --no-agent --max-tabs 2       # minutes; sanity
python -m pipeline.run word --no-agent                    # full sweep: every ribbon tab face
# Expect: kb/word/ui/tab-*.json for every ribbon tab (~10), each with elements + ids +
#         screenshot; main-window tab elements carry opens=ui:tab-<slug>.

# c) Ready-state discovery (the agent finds the way in without the fixture):
#    temporarily rename configs/apps/word.json's launch_args/fixture out of the way
#    (use a copied config app name, e.g. configs/apps/word-bare.json with no args),
python -m pipeline.run word-bare --discover-ready --no-agent --max-tabs 1
# Expect: agent clicks through the Start screen; kb/word-bare/scripts/drive/ready_route.json
#         exists; a SECOND run (no --discover-ready) replays the route deterministically and
#         reaches the workspace (journal shows ready/replay ok events).
```

- [ ] **Step 6: Validation report + commit**

Create `validation/plan-b1/report.md` (same format as plan-a: questions/verdicts/evidence): B1 questions — *Can the pipeline press and honestly classify what happened? (prober outcomes journaled, restore verified)*; *Is the surface layer now exhaustive? (every Word ribbon tab face captured; Notepad menus captured; markers measured)*; *Can an agent discover the ready state and does the recorded route replay deterministically?*; *Did generality hold? (grep; Notepad + Word same code)*. Snapshot `kb/word/ui/` and `kb/notepad/ui/` into `validation/plan-b1/results/`. Commit:

```bash
git add pipeline/run.py tests/unit/test_cli.py validation/plan-b1/
git commit -m "feat: B1 CLI knobs, acceptance evidence, validation report"
```

---

## Acceptance criteria for Plan B1 (definition of done)

1. `python -m pytest` green in seconds (no GUI); every smoke file passes run alone; the combined `-m smoke` suite passes.
2. **Prober honesty:** every probe journaled with a measured outcome; `opens` markers exist ONLY where a probe observed something; restore verified or loudly journaled.
3. **Exhaustive surface:** `kb/word/ui/` contains one `tab-*.json` per ribbon tab, each with element ids and a screenshot; `kb/notepad/ui/` contains `menu-*.json` containers; main-window markers updated accordingly.
4. **Ready state:** discovery run records a route; replay run reaches the workspace with zero agent calls.
5. **Plan A debt closed:** version pinned from the attached window's process; runs tear down their app; dismissal journaling has a grace poll; no Office strings in `pipeline/` code.
6. Generality grep clean; `validation/plan-b1/report.md` filled with verdicts + evidence. **The plan is not done without its report.**

## Explicitly deferred to Plan B2

- Feature/sub-feature node models and the per-feature breadth inspectors (sub-features, connections, audience)
- Contextual/special-surface discovery via state-changing probes (insert a table → new tabs)
- Assembly (`graph.json`), the three-state completeness check as a gate, priority signals/ranking/layers, usage research agent
- Label-language policy decision (locale finding from Plan A)
- Icon image capture into `Icon.image`

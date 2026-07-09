# P1 Plan B1 (rev 2): The Explorer Agent — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **REVISION NOTE (rev 2, 2026-07-08, user decision):** rev 1 put exploration *strategy* into
> deterministic pipeline code (a hardcoded `sweep()` loop). That was a design drift: per the spec,
> inspectors are **agents holding tools** — strategy belongs to the agent, and hardcoded strategy
> is what made the pipeline feel app-specific and brittle (every app quirk became a code patch).
> Rev 2 deletes the sweep and centers the plan on an **explorer agent**. Permanent code is limited
> to three layers: **hands** (tools), **guarantees** (journal, schema-enforced writes, safety
> floor), and **per-app memory** (routes/scripts the agent itself records into `kb/<app>/`).
> Tasks 1–3 of rev 1 were executed, reviewed, and stand unchanged — they built hands, not strategy.

**Goal:** `python -m pipeline.run <app>` launches the app and hands control to an **explorer agent** that drives it — reaches the workspace, outlines the full trigger surface (tab faces, menus) with *measured* `opens` markers, handles interruptions (save dialogs: always discard, never Save), records its ready-route and any helper scripts it writes into `kb/<app>/`, and journals every step. Validated on Notepad and Word with the same code and different agent behavior.

**Architecture:** The agent is in charge of *what to do*; code is in charge of *what its hands do*, *what counts as valid knowledge*, and *what is forbidden*. The agent gets a small tool belt over the existing proven tool layer (read screen, click, press, probe, screenshot, write KB, record route, write/run helper scripts). Clicks pass through a code-enforced destructive-action blocklist. Teardown handles save-confirmation dialogs deterministically (discard) because no agent is present at teardown time.

**Tech Stack:** unchanged — Python 3.13, pydantic v2, pywinauto/pywin32, Pillow, claude-agent-sdk, pytest.

## Global Constraints

- **Strategy is never hardcoded.** No pipeline code may encode exploration order or app-navigation logic (no "loop over tabs" in `pipeline/`). The agent decides; tools act; the journal records.
- **Safety floor is code, not instructions:** the click tool refuses elements whose label matches the destructive blocklist (code defaults + per-app config extras); `^s`/`^p` key chords are refused by the press tool. The briefing ALSO says "never Save" — but the tool would refuse anyway.
- **Measured, not assumed:** `opens` markers only from observed outcomes (the probe tool). Unprobed elements stay `unexplored`.
- **Agent-written scripts** live ONLY under `kb/<app>/scripts/`, run via subprocess with a timeout, output captured and journaled. They are per-app memory, never pipeline code.
- **Every agent tool call is journaled** by the tool itself (actor `explorer.<tool>`); hermetic agent (`setting_sources=[]`, only our tools, `max_turns` capped).
- Exactly-one marker; runs write only inside `kb/<app>/`; no app-specific logic in `pipeline/`/`tools/` (app data in configs); default `pytest` GUI-free and fast; smoke files one at a time; commits end with "Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>".

## Completed under rev 1 (stand unchanged — accounting only)

- **Task 1 — element ids** (`c84e9f5` incl. Turkish dotless-ı fix): `tools/ids.py`, `UIElement.id`, `assign_ids` helper.
- **Task 2 — Plan A debt bundle** (`28aac5a`): version pinned from the attached window's process; journaled teardown (`pipeline/teardown.py`); dismissal grace poll; flyout classes moved to config data.
- **Task 3 — the prober** (`ae7d241` + `57dc04d`): `probe_element` press-observe-classify-restore, proven live; `attach_by_handle` with popup-tree race fix; notepad popup class as config data.

## File Structure (rev 2 remaining work)

```
pipeline/config.py           # MODIFY: destructive_label_res / discard_label_res config extras
pipeline/teardown.py         # MODIFY: discard save-confirmation dialogs before force-kill
pipeline/agent_tools.py      # explorer tool belt: SDK-free impls + SDK wiring
pipeline/explorer.py         # mission briefing (B1 skeleton mission) + run_explorer()
pipeline/run.py              # MODIFY: stage 1 = base scan + explorer agent; --max-turns knob
tests/unit/test_teardown_discard.py
tests/unit/test_agent_tools.py
tests/unit/test_explorer.py
validation/plan-b1/report.md
```

---

### Task 4: Safety floor + teardown discard handling

**Files:**
- Modify: `pipeline/config.py`, `pipeline/teardown.py`, `configs/apps/word.json`, `configs/apps/notepad.json`
- Test: `tests/unit/test_teardown_discard.py`, extend `tests/unit/test_config.py`

**Interfaces:**
- `pipeline/config.py`: `AppConfig` gains `destructive_label_res: list[str] = []` and `discard_label_res: list[str] = []` (per-app/locale EXTRAS; the general defaults live in code).
- `pipeline/agent_tools.py` will consume (Task 5): `DESTRUCTIVE_RES` (code defaults, module constant in `pipeline/teardown.py` for now to avoid a forward file): `[r"(?i)^save$", r"(?i)^send\b", r"(?i)^delete\b", r"(?i)buy|purchase", r"(?i)^share\b", r"(?i)^print\b"]`; `DISCARD_RES = [r"(?i)don'?t save", r"(?i)^no$"]`.
- `teardown.close_app(session, journal)` gains a discard step: after WM_CLOSE + poll, if the window survives OR a new dialog-class window appeared, scan that dialog's elements (attach_by_handle → children) for a label matching `DISCARD_RES + cfg.discard_label_res`, click it (real click), journal `outcome="discarded"`, re-poll; only then fall back to taskkill (`outcome="killed"`).
- Pure helper for tests: `find_discard_target(elements: list[ElemInfo], extra_res: list[str]) -> ElemInfo | None`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_teardown_discard.py
from pipeline.teardown import find_discard_target
from tools.winapp.uia import ElemInfo

def E(name): return ElemInfo("Button", name, (0, 0, 10, 10), "")

def test_finds_dont_save_variants():
    els = [E("Save"), E("Don't Save"), E("Cancel")]
    assert find_discard_target(els, []).name == "Don't Save"

def test_finds_localized_via_config_extras():
    els = [E("Kaydet"), E("Kaydetme"), E("İptal")]
    assert find_discard_target(els, [r"(?i)kaydetme"]).name == "Kaydetme"

def test_never_returns_save_or_cancel():
    els = [E("Save"), E("Cancel")]
    assert find_discard_target(els, []) is None
```

```python
# append to tests/unit/test_config.py
def test_safety_label_extras_default_empty(tmp_path):
    import json
    (tmp_path / "y.json").write_text(json.dumps(
        {"name": "y", "exe": "y.exe", "window_title_re": ".*y.*"}), encoding="utf-8")
    cfg = load_app_config("y", tmp_path)
    assert cfg.destructive_label_res == [] and cfg.discard_label_res == []
```

- [ ] **Step 2: Run to verify failure** — `python -m pytest tests/unit/test_teardown_discard.py tests/unit/test_config.py -v` → FAIL (missing symbol/fields).

- [ ] **Step 3: Implement**

`pipeline/config.py`: add the two fields to `AppConfig` (defaults `[]`).

`pipeline/teardown.py` additions:

```python
import re
from tools.winapp.uia import ElemInfo, UIASession
from tools.winapp.windows import top_windows
from tools.winapp import inputs

DESTRUCTIVE_RES = [r"(?i)^save$", r"(?i)^send\b", r"(?i)^delete\b",
                   r"(?i)buy|purchase", r"(?i)^share\b", r"(?i)^print\b"]
DISCARD_RES = [r"(?i)don'?t save", r"(?i)^no$"]

def find_discard_target(elements: list[ElemInfo], extra_res: list[str]) -> ElemInfo | None:
    for pat in DISCARD_RES + list(extra_res):
        for e in elements:
            if e.name.strip() and re.search(pat, e.name):
                return e
    return None

def _try_discard_dialog(before_close: list, cfg, journal) -> bool:
    # a confirmation dialog is a NEW window (vs pre-close snapshot) of a dialog class
    for w in top_windows():
        if w.hwnd in {b.hwnd for b in before_close}:
            continue
        try:
            popup = UIASession.attach_by_handle(w.hwnd)
            els = [k for k in popup.children(depth=4) if k.name.strip()]
        except Exception:
            continue
        target = find_discard_target(els, cfg.discard_label_res)
        if target is not None:
            inputs.ensure_foreground(w.hwnd)
            inputs.click_rect(target.rect)
            journal.append(JournalEvent(actor="teardown", action="close", target=w.title or w.cls,
                                        outcome="discarded", data={"button": target.name}))
            return True
    return False
```

In `close_app`: snapshot `before_close = top_windows()` BEFORE PostMessage; after the existing 3s poll, if still alive: `if _try_discard_dialog(before_close, session.config, journal):` re-poll up to 3s more; only then `_kill_by_hwnd_pid` + journal `killed` as today. Keep existing outcomes intact (`closed` when the first poll succeeds).

Config data: to `configs/apps/word.json` add `"discard_label_res": ["(?i)kaydetme"]` (locale safety net) — notepad needs none (Win11 Notepad keeps sessions without prompting), leave its extras absent (defaults apply).

- [ ] **Step 4: Run to verify pass** — targeted tests + full `python -m pytest`; then `python -m pytest tests/smoke/test_stage0_smoke.py -m smoke -v` once (teardown path with no dialog must still work: `closed`).

- [ ] **Step 5: Commit**

```bash
git add pipeline/config.py pipeline/teardown.py configs/apps/word.json tests/
git commit -m "feat: destructive/discard safety labels; teardown discards save dialogs before kill"
```

---

### Task 5: The explorer tool belt

**Files:**
- Create: `pipeline/agent_tools.py`
- Test: `tests/unit/test_agent_tools.py`

**Interfaces:**
All `_impl` functions are SDK-free and unit-testable with fakes; each journals with actor `explorer.<tool>`. `ToolContext` (dataclass) carries `session, writer, journal, kb_app_root, cfg`.

- `read_screen_impl(ctx) -> str` — JSON list of live named elements: `{ref, label, control_type, bounds}` where `ref` is `"<slug>-<n>"` (stable within one call; the agent uses refs in subsequent calls; every call re-scans and re-numbers).
- `click_impl(ctx, ref_or_label) -> str` — resolves the element from a fresh scan (by ref from the LAST read_screen's numbering — implemented by re-deriving the same ordering — or by case-insensitive label match); **refuses** if the label matches `DESTRUCTIVE_RES + cfg.destructive_label_res` → returns `"blocked: destructive"` and journals `outcome="blocked"`; otherwise clicks, waits 0.8s, reports `"clicked '<label>'; windows now: [...]"`.
- `press_impl(ctx, keys) -> str` — refuses `^s`, `^p`, `%{F4}` (journaled block); else presses.
- `probe_impl(ctx, ref_or_label) -> str` — runs `probe_element`, returns JSON `{kind, expanded: [labels...], restored}`.
- `screenshot_impl(ctx, name) -> str` — window grab via `capture.grab_region`, saved through `writer.save_screenshot(img, "ui:screen", name)`, returns rel path.
- `write_container_impl(ctx, container_json) -> str` — `UIContainer.model_validate_json` then `writer.write_container`; ValidationError message returned as `"rejected: <why>"` (the agent retries with fixed JSON).
- `record_route_impl(ctx, steps_json) -> str` — as in rev 1 (steps `[{click_label_re}]` → `kb/<app>/scripts/drive/ready_route.json`).
- `write_script_impl(ctx, relpath, content) -> str` — writes ONLY under `kb/<app>/scripts/` (reject `..` or absolute paths), returns saved path.
- `run_script_impl(ctx, relpath) -> str` — `subprocess.run([sys.executable, path], timeout=120, capture_output=True, cwd=repo_root)`; returns exit code + last 2000 chars of output; journaled.
- SDK wiring: `make_explorer_tools(ctx) -> list` (thin `@tool` wrappers over the impls) and `run_explorer_agent(briefing, tools, max_turns=60) -> str` (hermetic; in-process MCP server; `allowed_tools` restricted; verify exact SDK API against installed claude-agent-sdk 0.2.113 as done in Plan A Task 12 — adapt mechanically, record evidence).

- [ ] **Step 1: Write the failing unit tests**

```python
# tests/unit/test_agent_tools.py
import json, pytest
from pathlib import Path
from unittest.mock import patch
from pipeline.agent_tools import (ToolContext, read_screen_impl, click_impl, press_impl,
                                  write_container_impl, write_script_impl, run_script_impl)
from tools.journal import Journal
from tools.kb_writer import KBWriter
from tools.winapp.uia import ElemInfo

class FakeUI:
    def children(self, depth=1):
        return [ElemInfo("Button", "Bold", (0, 0, 10, 10), ""),
                ElemInfo("Button", "Save", (10, 0, 20, 10), "")]
class FakeSession:
    ui = FakeUI(); hwnd = 1
class FakeCfg:
    destructive_label_res = []; discard_label_res = []

def ctx(tmp_path):
    return ToolContext(session=FakeSession(), writer=KBWriter(tmp_path, "x"),
                       journal=Journal(tmp_path / "j.jsonl", run_id="t"),
                       kb_app_root=tmp_path / "x", cfg=FakeCfg())

def test_read_screen_lists_elements_with_refs(tmp_path):
    out = json.loads(read_screen_impl(ctx(tmp_path)))
    assert out[0]["label"] == "Bold" and out[0]["ref"] == "bold-0"

def test_click_blocks_destructive(tmp_path):
    c = ctx(tmp_path)
    with patch("pipeline.agent_tools.inputs"):
        assert click_impl(c, "Save").startswith("blocked")
    assert Journal.read_all(c.journal.path)[-1].outcome == "blocked"

def test_press_blocks_save_chord(tmp_path):
    assert press_impl(ctx(tmp_path), "^s").startswith("blocked")

def test_write_container_rejects_bad_json(tmp_path):
    out = write_container_impl(ctx(tmp_path), '{"id": "nope"}')
    assert out.startswith("rejected")

def test_write_script_confines_to_scripts_dir(tmp_path):
    c = ctx(tmp_path)
    p = write_script_impl(c, "extract/scan.py", "print('hi')")
    assert Path(p).is_relative_to(tmp_path / "x" / "scripts")
    with pytest.raises(ValueError):
        write_script_impl(c, "../evil.py", "boom")

def test_run_script_captures_output(tmp_path):
    c = ctx(tmp_path)
    write_script_impl(c, "extract/hello.py", "print('hello-from-script')")
    out = run_script_impl(c, "extract/hello.py")
    assert "hello-from-script" in out and "exit 0" in out
```

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement** (`pipeline/agent_tools.py`; impls per the interface block — keep each under ~20 lines, reuse `tools.ids.slug` for refs, `pipeline.teardown.DESTRUCTIVE_RES` for the blocklist, `pipeline.prober.probe_element` for probing; SDK wiring at the bottom mirroring Plan A's verified `SdkRunner` pattern with `create_sdk_mcp_server` + `ClaudeAgentOptions(setting_sources=[], mcp_servers=..., allowed_tools=..., max_turns=...)`).

- [ ] **Step 4: Run to verify pass** — targeted + full suite green.

- [ ] **Step 5: Commit**

```bash
git add pipeline/agent_tools.py tests/unit/test_agent_tools.py
git commit -m "feat: explorer tool belt - journaled, safety-floored tools with SDK wiring"
```

---

### Task 6: The explorer mission + stage 1 integration

**Files:**
- Create: `pipeline/explorer.py`
- Modify: `pipeline/run.py`
- Test: `tests/unit/test_explorer.py`, extend `tests/unit/test_cli.py`

**Interfaces:**
- `B1_MISSION` (str): the briefing. Contents (generic, no app names): (1) the ready-state definition from rev 1 (workspace vs launcher; record the minimal route via record_route; empty route if already ready); (2) the skeleton mission: *"Outline this app's trigger surface. Document the main window and each top-level navigation container (tabs, menus): use probe to measure what each element does, write one container per surface via write_container (ids `ui:<kind>-<slug>`, elements with exactly one marker — opens only for measured outcomes, unexplored otherwise), screenshot each surface. Cover every top-level tab and menu before finishing."*; (3) rules: never destructive (tools will refuse anyway), discard save-confirmation dialogs, journal is automatic, you may write/run helper scripts under scripts/ for repetitive mechanics; (4) finish contract: reply `DONE` + a one-paragraph coverage summary naming what was documented and what was deliberately left unexplored.
- `run_explorer(session, writer, journal, kb_app_root, cfg, max_turns=60) -> str` — builds `ToolContext`, `make_explorer_tools`, `run_explorer_agent(B1_MISSION, ...)`; journals `actor="explorer", action="mission", outcome="done"|"failed: <why>"` with the agent's final summary in data.
- `pipeline/run.py`: stage 1 becomes `scan_surface` (cheap mechanical baseline, unchanged) then — unless `--no-agent` — `run_explorer(...)` (replacing the old `run_skeleton_agent` call; the feature-inventory skeleton agent moves to Plan B2 where features are the mission). New knob `--max-turns` (default 60). `--discover-ready` is subsumed (ready-state is part of the mission) — remove the flag.
- Unit tests: mission text contains the load-bearing phrases; `run_explorer` with a patched `run_explorer_agent` that exercises a fake tool round (write a container via the impl, then return "DONE ...") → journal shows mission done; CLI flags updated.

- [ ] **Step 1: Write the failing tests**

```python
# tests/unit/test_explorer.py
from pathlib import Path
from unittest.mock import patch
from pipeline.explorer import B1_MISSION, run_explorer
from tools.journal import Journal
from tools.kb_writer import KBWriter

def test_mission_contains_load_bearing_rules():
    for phrase in ("record_route", "write_container", "unexplored", "probe",
                   "Never", "DONE"):
        assert phrase in B1_MISSION

def test_run_explorer_journals_done(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="DONE covered main window"):
        out = run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                           kb_app_root=tmp_path / "x", cfg=None)
    assert out.startswith("DONE")
    ev = Journal.read_all(tmp_path / "j.jsonl")[-1]
    assert ev.actor == "explorer" and ev.outcome == "done"

def test_run_explorer_journals_failure(tmp_path: Path):
    j = Journal(tmp_path / "j.jsonl", run_id="t")
    with patch("pipeline.explorer.run_explorer_agent", return_value="I could not finish"):
        run_explorer(session=None, writer=KBWriter(tmp_path, "x"), journal=j,
                     kb_app_root=tmp_path / "x", cfg=None)
    assert "failed" in Journal.read_all(tmp_path / "j.jsonl")[-1].outcome
```

```python
# adjust tests/unit/test_cli.py: replace the --discover-ready assertions with --max-turns
def test_b1_flags():
    a = parse_args(["word", "--max-tabs", "3", "--no-sweep", "--keep-open", "--max-turns", "40"])
    assert a.max_turns == 40 and a.keep_open
```

(Also remove `--no-sweep`/`--max-tabs` if they only served the deleted sweep — check `run.py`: rev 1 Task 4 never landed, so those flags never existed; drop them from this test accordingly. Keep the test minimal against the REAL current flags: `--keep-open`, `--max-turns`, `--no-agent`, `--max-containers`.)

- [ ] **Step 2: Run to verify failure** — module missing.

- [ ] **Step 3: Implement** `pipeline/explorer.py` (mission string per the interface block; `run_explorer` ~15 lines) and the `run.py` wiring (`--max-turns`, explorer call in stage 1, remove the old `run_skeleton_agent` import/call — Plan B2 reintroduces feature extraction on top of explorer output).

- [ ] **Step 4: Run to verify pass** — full suite green.

- [ ] **Step 5: Commit**

```bash
git add pipeline/explorer.py pipeline/run.py tests/unit/test_explorer.py tests/unit/test_cli.py
git commit -m "feat: explorer mission and stage-1 integration - agent drives, code serves"
```

---

### Task 7: Live acceptance + validation report

No new production code — this task RUNS the explorer for real and reports honestly.

- [ ] **Step 1: Notepad run** — `python -m pipeline.run notepad --max-turns 40`
  Expect: exit 0; `kb/notepad/ui/` contains main-window plus agent-written containers for the menus (File/Edit/View — localized labels fine); measured `opens` markers on probed elements; journal shows every tool call; teardown clean.

- [ ] **Step 2: Word run** — `python -m pipeline.run word --max-turns 80`
  Expect: exit 0; containers for ribbon tab faces the agent explored; screenshots; if a save dialog appeared: journal shows the discard (teardown or agent path); ready route recorded only if Word wasn't already in the workspace (fixture makes it ready — that's fine, route `[]` or absent).

- [ ] **Step 3: Ready-state discovery proof** — copy `configs/apps/word.json` to `configs/apps/word-bare.json` with `launch_args`/`fixture` removed; `python -m pipeline.run word-bare --max-turns 60`
  Expect: the agent recognizes the Start screen, reaches the workspace itself, records `kb/word-bare/scripts/drive/ready_route.json`; a second run replays the route (journal `ready/replay` events) — note: replay wiring exists in `run.py` from rev 1 interfaces? If NOT yet wired (rev 1 Task 6 never landed), wire the minimal replay in `run.py` as part of this step: if `kb/<app>/scripts/drive/ready_route.json` exists, replay it after launch (reuse `record_route` steps: find by `click_label_re`, click, journal) — ~15 lines + a unit test, committed with this task.

- [ ] **Step 4: Suite + generality** — full `python -m pytest` green; each smoke file alone green; grep: no app names in `pipeline/`/`tools/`.

- [ ] **Step 5: Validation report** — create `validation/plan-b1/report.md` (plan-a format):
  Questions → verdicts with evidence: B1-Q1 *Can an agent explore a real app end-to-end with only our tools?* B1-Q2 *Are markers measured (opens only via probe) and is everything journaled?* B1-Q3 *Does the safety floor hold (blocked clicks in journal; no Save ever clicked; save dialogs discarded)?* B1-Q4 *Does ready-state discovery + replay work without hand-written config?* B1-Q5 *Generality: same code, Notepad + Word?* Snapshot `kb/notepad/` and `kb/word/` (+`word-bare` route) into `validation/plan-b1/results/`. Record the token/turn cost of each run (from journal timestamps + turn counts) — B2 needs the cost baseline.

- [ ] **Step 6: Commit**

```bash
git add validation/plan-b1/ pipeline/run.py tests/
git commit -m "docs: B1 acceptance evidence and validation report"
```

---

## Acceptance criteria for Plan B1 rev 2 (definition of done)

1. Default `pytest` green in seconds; every smoke file green alone.
2. **The explorer works:** on both test apps, the agent produced multi-container skeletons (tab faces / menus) with measured `opens` markers, using only the tool belt — zero strategy code in the pipeline.
3. **Safety floor proven:** destructive clicks blocked at the tool layer (journal evidence); save-confirmation dialogs discarded, never saved.
4. **Ready-state:** agent-discovered route recorded and replayed on a bare config (no hand-written fixture needed).
5. **Honest bookkeeping:** every tool call journaled; unexplored stays unexplored; cost baseline recorded.
6. `validation/plan-b1/report.md` filled — **the plan is not done without its report.**

## Explicitly deferred to Plan B2

- Feature/sub-feature node models; the feature-extraction mission (breadth: sub-features, connections, audience) on top of B1's skeleton
- Contextual-surface discovery via state-changing probes (insert table → new tabs)
- Assembly (`graph.json`), completeness gate, priority signals/ranking/layers, usage research
- Label-language policy; icon image capture

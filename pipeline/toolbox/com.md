# com — the app's own object model (Office COM as the worked example)

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

If the app exposes an automation object model (Office COM, or any scripting API), use it for
three things ONLY: (1) launching an **isolated instance** you fully own, (2) establishing a
**deterministic starting state** (fixture document, selection, clipboard), and (3) reading
**state fingerprints** that prove what a press changed. Do NOT use it to drive the UI you're
trying to map — you'd be measuring the API, not the UI.

## How to use

**Isolated instance + PID ownership** (`crawler/launcher.py::WordSession.start`):

```python
pre = {p.pid for p in psutil.process_iter(['name']) if p.info['name'].lower() == 'winword.exe'}
app = win32com.client.DispatchEx("Word.Application")   # DispatchEx = NEW instance, never attach
# poll until exactly ONE new pid appears in the process set — that pid is yours
assert len(new_pids) == 1
```

**Version lock** — assert the build every launch so silent auto-updates fail loudly instead of
silently changing ground truth:

```python
assert app.Build.startswith(BUILD_PREFIX), f"build drift: {app.Build}"
```

**State fingerprints** (`crawler/launcher.py`):

```python
def doc_hash(self):     # text-only content hash
    return hashlib.sha256(self.doc.Content.Text.encode("utf-8", "replace")).hexdigest()

def format_sig(self):   # selection FORMATTING fingerprint — bold/italic/size/font/color/indent…
    f, p = self.app.Selection.Font, self.app.Selection.ParagraphFormat
    ...
```

`classify` uses both: a text delta OR a formatting delta after a press = the control is a
`feature` (see `win32.md`).

**Deterministic teardown** (`crawler/launcher.py::close`): each step independent —
`doc.Close(SaveChanges=0)` → `app.Quit()` → `taskkill /PID <yours> /F`. The taskkill is the
guaranteed PID-safe cleanup; never kill by process name (you'd murder the user's own instance).

**Fixture anchoring** — open a known document, select a known paragraph, arm the clipboard once
before crawling clipboard-dependent controls (`crawler/launcher.py::select_paragraph`,
`::copy_fixture_text`, `crawler/run_p0.py` "clipboard-armed").

## Known traps

- **COM calls raise "application is busy" while a modal dialog is up.** Snapshot code must
  tolerate this: catch the exception and return a sentinel (`"<com-busy>"`) — harmless because
  the dialog was already detected via win32 and dialog outranks state-delta in classification
  (`crawler/prober.py::_snapshot`).
- **Never fire the API's command-execution path (`ExecuteMso` / UIA `Invoke`) on an
  unclassified control** — it can deadlock the app's UI thread. Physical input only for
  probing (`crawler/prober.py` module docstring).
- **A stuck modal makes even `doc.Close()` report busy** — that's why teardown ends with a
  PID-targeted taskkill instead of trusting the polite path
  (`crawler/launcher.py::close` comment).
- **Add-ins pollute the UI.** Disconnect COM add-ins at launch — and expect leftovers anyway:
  Word's Acrobat add-in still injected its ribbon group after disconnect, which had to be
  declared a crawl boundary instead (`crawler/launcher.py::_disconnect_addins`,
  `crawler/config.py` BOUNDARY_PREFIXES comment).
- **A text-only content hash misses formatting-only changes.** Grow Font / indent / color
  change nothing in `Content.Text`; without the separate formatting signature those controls
  classify as `unresolved` (`crawler/launcher.py::format_sig` docstring).

## Lessons learned

- 2026-07-09 — **Own your instance by PID, derived from a process-set delta around launch.**
  `DispatchEx` + before/after process sets gives you exactly one pid that is yours to kill;
  everything PID-filtered downstream (windows, teardown) inherits this safety.
  (learned from `crawler/launcher.py::WordSession.start`)
- 2026-07-09 — **Pin the app version as an executable assertion, not documentation.** The dev
  machine auto-updated mid-project; the prefix assert turned "silently different ground truth"
  into a loud launch failure.
  (learned from `crawler/launcher.py::start` + `crawler/config.py::BUILD_PREFIX` comment)
- 2026-07-09 — **The object model is your truth oracle for "did the press do something?"**
  Window deltas catch surfaces; the content hash + formatting signature catch feature presses
  that open nothing. You need both halves. (An app-settings fingerprint — view/zoom/options —
  is also captured per snapshot, but classification consults only the hash and format
  signature; the settings-delta check exists as design intent, not implemented code.)
  (learned from `crawler/prober.py::classify` lines 73-77,
  `crawler/launcher.py::doc_hash`/`::format_sig`; design intent: source project
  `docs/DESIGN.md` §4.2/§6.6)
- 2026-07-09 — **Restore state through the same channel you observe it.** After a `feature`
  press the crawler sends Ctrl+Z and then verifies `doc_hash` returned to the baseline — the
  fingerprint doubles as the reset check.
  (learned from `crawler/prober.py::_restore`)
- 2026-07-09 — **The format fingerprint must reach OUTSIDE Font/ParagraphFormat, or highlight /
  shading / borders classify as false `no-effect`.** Highlight lives on `Selection.Range.
  HighlightColorIndex`, shading on `ParagraphFormat.Shading.BackgroundPatternColor`, borders on
  `Range.Borders(i).LineStyle` (i = -1..-4). Applying a highlight/border via the ribbon changed
  none of the classic Font/Paragraph props, so those primary-applies measured as no-effect until
  the sig was widened. Also: **pre-format the probe selection** (bold/italic/size/color/indent)
  so *removal* features (Clear Formatting, Decrease Indent from 0) produce a delta too.
  (learned from kb/word/scripts/session.py::format_sig + run_step2 pre-format)
- 2026-07-09 — **Ctrl+Z, not re-press, is the universal formatting reset.** Re-pressing a
  *toggle* (Bold) undoes it, but re-pressing a *non-toggle apply* (Font Color = red) applies red
  again — silently leaving the selection formatted and poisoning every later `format_sig`
  baseline. Undo any doc/format change with Ctrl+Z (loop until doc_hash AND format_sig match
  baseline); reserve re-press for view toggles like Show All that Ctrl+Z can't undo.
  (learned from kb/word/scripts/tools/prober.py::restore)
- 2026-07-10 — **One control that opens a COM-blocking modal must not kill the whole crawl —
  catch, recover win32-only, continue.** A contextual press that opens an OS file dialog (the
  Header&Footer tab's 'Pictures…') or an ink/modal editor makes EVERY later COM call raise
  `RPC_E_SERVERCALL_RETRYLATER` (-2147417846, "application is busy"); an uncaught exception then
  aborts the entire tab. Wrap each control's probe in try/except: on failure close every
  non-frame top-level window with win32 `PostMessage(WM_CLOSE)` + keyboard ESC (NO COM — COM is
  the thing that's blocked), then **poll `doc_hash()` until it stops returning the `<com-busy>`
  sentinel** before continuing, and record the control as an honest unexplored boundary. This
  turned a fatal crawl-killer into a single journaled skip. (learned from kb/word-home-insert-v2
  step3: `_force_close_nonframe` + per-control except in crawl_contextual_tab)

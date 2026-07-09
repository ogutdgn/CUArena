# win32 — window enumeration, class identification, press-classification evidence

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

The Win32 window layer is the most truthful signal source you have: a top-level window either
exists or it doesn't. Use it to (a) find the app's real frame window, (b) detect what a press
opened via **before/after window-set deltas**, (c) tell dialogs from flyouts by **window
class**, and (d) manage geometry (primary monitor, maximize). When UIA and Win32 disagree,
trust Win32.

## How to use

**Snapshot the process's visible top-level windows** (this is the primitive everything builds on):

```python
def _pid_toplevels(pid):
    out = []
    def cb(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            _, wpid = win32process.GetWindowThreadProcessId(hwnd)
            if wpid == pid:
                out.append((hwnd, win32gui.GetClassName(hwnd),
                            win32gui.GetWindowText(hwnd), win32gui.GetWindowRect(hwnd)))
        return True
    win32gui.EnumWindows(cb, None)
    return out
```

**Press-observe-classify by delta:** snapshot → inject the click → snapshot again → the
difference is what YOU opened (PID-filtered, so other apps can't pollute it). Classify by
class-set membership, with an explicit precedence order
(`crawler/prober.py::classify`, `::_snapshot`):

1. new **dialog-class** window → `dialog`
2. toggle-state changed → `toggles` (must beat popup — see traps)
3. new **popup-class** window → `popup`
4. docked-pane count grew → `pane`
5. document/formatting state changed (via COM, see `com.md`) → `feature`
6. else `unresolved`

**Window classes are knowable — pin them from live probes.** For Word 16:
dialogs = `{NUIDialog, #32770, bosa_sdm_msword, bosa_sdm_Mso96}` (+ substring "Dialog");
flyouts = `{NetUIHWND, Net UI Tool Window, MsoCommandBarPopup, NetUITWPopupWindow}`
(`crawler/prober.py` head); frame = `OpusApp` (`crawler/uia.py::_frame_hwnd`);
document child window = `_WwG` (`crawler/prober.py::_count_task_panes`).

**Find the frame explicitly by class** — an app can own several top-level windows at startup and
its API's "active window handle" is not always the one hosting the command surface
(`crawler/uia.py::_frame_hwnd`).

**Detect docked side panes by child-window geometry:** a docked pane pushes the document child
window (`_WwG`) inward, so `left > 50 or right < screen_w - 60` means a pane is open — fast and
deterministic where class-based heuristics flapped (`crawler/prober.py::_count_task_panes`).
Floating panes don't inset the document; detect those by a "Close pane" button inside the frame
rect via UIA (`crawler/prober.py::_has_close_pane`).

**Adaptive observation:** after a click, poll snapshots until the surface set is stable across
two reads (min 1.5s, max 5s) — some windows appear late (`crawler/prober.py::_observe`).

## Known traps

- **Whitelisting dialog classes silently drops real dialogs.** Word's Apply Styles window and
  the Insert Pictures chooser are top-level but NOT in the pinned dialog-class set. The fix that
  survived: **blacklist the flyout/popup classes** and accept any other new top-level as the
  child dialog — pair it with an enabled-check upstream so a leftover flyout can't be mistaken
  for a dialog (`crawler/run_p0.py::_child_dialog` docstring).
- **A toggle-state change must outrank a coincident popup window.** Transient tooltip /
  live-preview windows of popup class intermittently appear during observation; checking popup
  first misclassified real toggles (align-center, subscript) as dropdown-openers
  (`crawler/prober.py::classify` comment).
- **Tooltips are top-level popup-class windows too.** Exclude tiny ones by area
  (`_MIN_POPUP_AREA = 10_000`) and, for cascade submenus, by POSITION: a real submenu's left
  edge sits at/after the parent popup's right edge; a ScreenTip renders over the hovered item
  (`crawler/prober.py`, `crawler/capture.py::_cascade_window`).
- **The OS recycles flyout HWNDs from a small pool.** Hovering the next submenu item may reuse
  the PREVIOUS flyout's handle — an `hwnd != prev_hwnd` "is it new?" guard wrongly rejects real
  flyouts. Wait for the previous one to become invisible, then accept any cascade window
  (`crawler/run_p0.py::_drain_popup` comment).
- **Win32 window text and UIA Name can disagree on the same window** (Word's picture chooser:
  win32 says "Insert Pictures", UIA says "Picture Bullet"). Match boundary/title rules against
  BOTH (`crawler/run_p0.py::_window_boundary`).
- **Teaching callouts / nag windows pollute deltas.** Filter known nag titles by regex before
  classifying (`crawler/prober.py::_is_nag`, `crawler/config.py::NAG_SIGNATURES`).
- **The app may open on a secondary monitor** (breaks pinned-coordinate assumptions). Restore +
  `SetWindowPos` to (0,0) before maximizing, then assert the window is on the primary monitor
  (`crawler/launcher.py::_move_to_primary`, `::_assert_primary_monitor`).

## Lessons learned

- 2026-07-09 — **"A new window appeared" is only meaningful with PID + visibility + class
  filters and a per-action baseline.** Recompute the `before` set immediately before every
  press/hover; a stale global baseline hides windows that opened in between.
  (learned from `crawler/prober.py::_snapshot`, `crawler/run_p0.py::_drain_popup`)
- 2026-07-09 — **Panes are not top-level windows** — window-set deltas are blind to them. You
  need a second signal: document-area inset geometry for docked panes, a "Close pane" button
  probe for floating ones. Budget for a "pane rescue" reclassification after the fact.
  (learned from `crawler/prober.py::_count_task_panes`, `::_has_close_pane`, `::probe`)
- 2026-07-09 — **Classify from evidence precedence, not from the first signal you find.** The
  exact order dialog → toggle → popup → pane → state-delta was reached by fixing real
  misclassification bugs; keep it as a pure, unit-testable function over two snapshots.
  (learned from `crawler/prober.py::classify` + `crawler/tests/test_prober_pure.py`)
- 2026-07-09 — **Record window class/title/area diagnostics into the journal on every popup
  outcome** — when a transient window causes a misclassification weeks later, the journal
  answers it without a repro hunt.
  (learned from `crawler/prober.py::probe` "popup_windows" diagnostic)
- 2026-07-09 — **Some presses legitimately open nothing top-level** (they open a pane, or are
  state-gated). Instrument the failure path: log the classes of whatever DID appear
  (`new=[...]`) — an empty list is itself a strong clue (pane or no-op), a non-empty list names
  the unexpected window.
  (learned from `crawler/run_p0.py::_drain_popup` submenu-dialog instrumentation + run journals
  `run-20260707-*`: `"submenu-dialog: no child dialog; new=[]"`)
- 2026-07-09 — **Confirmed live (kb/word): a committed STATE delta must be checked BEFORE the
  flyout branch, not just before the toggle branch.** Pressing **Justify** (a plain Button, not
  a UIA toggle) fl\-classified as `flyout` because a transient live-preview NetUI window of flyout
  class flickered during observation and my precedence checked flyout before the format delta. The
  alignment change (`format_sig`) is the truth. Order that survived: **dialog → state-delta
  (doc/format/app) → flyout → pane → other**. Live-preview never *commits* formatting, so a real
  flyout-opener (color picker, Change Case) shows no state delta and still falls through to
  `flyout` correctly. (learned from kb/word/scripts/tools/prober.py::classify, run-042323)
- 2026-07-09 — **Floating task panes read as a dialog by window class.** Word's **Styles** pane
  opens *floating* (a top-level window), so document-inset pane detection misses it and the class
  check calls it a dialog — then dialog-dismissal (Cancel/ESC) can't close it and it stays stuck.
  Distinguish it by probing for a **'Close pane' button** on the window (task panes have one;
  dialogs have OK/Cancel); close it through that button, not ESC.
  (learned from kb/word/scripts/tools/windows.py::is_task_pane_window + prober `_close_pane_window`)

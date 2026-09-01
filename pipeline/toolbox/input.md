# input — real mouse/keyboard injection

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

Physical input injection (`pywinauto.mouse` / `pywinauto.keyboard.send_keys`) is the ONLY safe
way to press unclassified controls and to work with flyouts. Flyout menus live and die by real
focus and real cursor position: they close on focus loss, submenus open only on hover, and
owner-drawn flyout items expose no UIA elements to invoke at all (items are reachable only via
`ElementFromPoint` — see `pixel.md`); synchronous API activation on an unclassified control can
deadlock the app's UI thread rather than fail politely. All injected input goes to the
FOREGROUND window, which makes the whole crawl inherently serial on one desktop.

## How to use

**Force foreground before every click — with the AttachThreadInput dance** (attach your
thread's input queue to the current foreground window's thread before calling
`SetForegroundWindow`; a bare call is refused when your process isn't foreground):

```python
def _force_foreground(hwnd):
    if win32gui.GetForegroundWindow() == hwnd:
        return
    t1, _ = win32process.GetWindowThreadProcessId(win32gui.GetForegroundWindow())
    t2 = win32api.GetCurrentThreadId()
    ctypes.windll.user32.AttachThreadInput(t1, t2, True)
    try:    win32gui.SetForegroundWindow(hwnd)
    finally: ctypes.windll.user32.AttachThreadInput(t1, t2, False)
```

(`crawler/uia.py::_force_foreground`)

**Two foreground policies, not one** (`crawler/prober.py::_ensure_ribbon_foreground` /
`::_ensure_word_foreground`): force the MAIN frame only when you're about to click the command
surface; while a modal dialog is up, refocus **only if another process stole foreground** —
forcing the main window sends your ESC to the disabled frame instead of the dialog.

**Click zones:** for split buttons, click the child-zone rects UIA exposes (primary Button vs
`*_Dropdown` MenuItem); fall back to orientation-aware fractions of the parent rect
(`crawler/prober.py::zone_point`).

**Submenus: hover, never click** — clicking a submenu-owning item fires terminal items instead.
Park the cursor on the parent popup's top border and settle (~0.35s) before the FIRST hover,
hover each candidate, and wait out the previous flyout before the next
(`crawler/capture.py::_hover_submenus`, `crawler/run_p0.py::_drain_popup`).

**Close dialogs by their Cancel/Close BUTTON first, ESC only as fallback** — and never a
committing button (`crawler/run_p0.py::_dismiss`).

**Scroll long lists with real wheel input** at the list's center
(`mouse.scroll(coords=..., wheel_dist=-3)`) and re-enumerate until nothing new appears
(`crawler/capture.py::capture_pane`).

## Known traps

- **ESC does not close every dialog.** Word's Format Text Effects panel ignores ESC entirely —
  only its Close button works. A dismiss helper must click Cancel/Close first and treat ESC as
  the fallback, then verify the window actually vanished (`crawler/run_p0.py::_dismiss`).
- **ESC does not close docked panes either** — every task pane has a "Close pane" header button
  (note: named "Close pane", not "Close"); click that (`crawler/prober.py::close_docked_panes`,
  `::_restore` comment).
- **The first hover of a sequence intermittently misses** unless you park-and-settle on a
  neutral point first (`crawler/capture.py::_hover_submenus` comment).
- **Slow flyouts render late.** If no window appeared after the normal dwell (~0.55s), wait
  ~0.4s more and re-check before concluding "no submenu"
  (`crawler/capture.py::_hover_submenus`).
- **Hover dwell long enough for a flyout is long enough for a ScreenTip** — a tooltip window
  will appear and pass a naive "new window ⇒ submenu" test. Disambiguate by position
  (see `win32.md`; `crawler/capture.py::_cascade_window`).
- **Clicking an item inside a cascade submenu is fragile.** Moving diagonally from the parent
  item to the submenu item can cross the gap and collapse the cascade, so the click lands on
  nothing; stepping onto the submenu's near edge first (same row) keeps it alive. Even then,
  some submenu items open a PANE or nothing top-level — instrument what appeared
  (`crawler/run_p0.py::_drain_popup` comments; run journals `run-20260707-*` `new=[]`).
- **Anything that changes foreground mid-crawl corrupts the run** — a user touching the mouse,
  a console window popping up. The crawl must own the desktop while it runs; refocus defensively
  before each press (`crawler/prober.py::_ensure_word_foreground`).

## Lessons learned

- 2026-07-09 — **Never activate a control through the accessibility/automation API when you
  don't know what it is** (UIA `Invoke`, Office `ExecuteMso`): it can deadlock the app's UI
  thread. Injected clicks at screen coordinates are the only probe-safe activation.
  (learned from `crawler/prober.py` module docstring)
- 2026-07-09 — **Restore is action-specific:** dialogs/popups → an ESC loop with foreground
  re-checks (`_clear_surfaces`); toggles → re-press the same point; panes → their "Close pane"
  button; document features → Ctrl+Z. A single generic reset leaves state behind and poisons
  every subsequent probe. (The stronger Cancel/Close-button-first dismissal lives on the drain
  path — `crawler/run_p0.py::_dismiss` — because some dialogs ignore ESC.)
  (learned from `crawler/prober.py::_restore`/`::_clear_surfaces`)
- 2026-07-09 — **Popup items that open dialogs need a re-open per item** — clicking an item
  dismisses the whole popup, so each `…` item costs: reopen popup → click item → drain dialog →
  dismiss. Retry once on a missed child; some children just appear late (poll, don't re-click a
  dialog button — re-clicking can toggle state).
  (learned from `crawler/run_p0.py::_drain_popup`, `::_wait_child_dialog`)
- 2026-07-09 — **Serial by construction.** One physical input stream + foreground semantics
  means two drivers on one desktop collide. Parallelize read-only analysis, never the driving.
  (learned from `docs/DEPTH.md` §5 of the source project)
- 2026-07-09 — **Transitive descent has two regimes: modal stacks descend in place, flyouts
  need route replay.** Pressing a '…' opener inside a DIALOG leaves the parent open under the
  child — recurse, close the child, continue with the next opener, no reopening. Pressing an
  item inside a FLYOUT kills the flyout — each opener item costs: click → explore what opened
  → close → replay the ribbon-zone click to reopen the flyout for the next sibling. Budget
  accordingly: a gallery menu with 4 cascades + 2 dialog openers ≈ 7 open/close cycles.
  (learned from kb/word-home-insert step5 DepthWalker: 60 surfaces entered transitively)
- 2026-07-09 — **Cascade submenus are discoverable by hover-probe with the position rule.**
  Menu items WITHOUT '…' may still own cascades (Word's Gradient, Underline Color, Top of
  Page…). Park-settle on the parent's top border, hover the item ~0.65s, and accept a new
  window only if its left edge sits at/after the parent's right edge (tooltips render OVER the
  item). Items named '… from Office.com' open network galleries — journal a boundary, don't
  descend. (learned from kb/word-home-insert step5: 10 cascades measured this way)
- 2026-07-09 — **Deduplicate shared dialogs by normalized TITLE at discovery time.** 'More
  Underlines…' opens the Font dialog; 'Line Spacing Options…' opens the Paragraph dialog; Find
  dropdown's 'Advanced Find…' and Replace open the same Find and Replace dialog. Keeping a
  normalized-title → container-id map and resolving each newly opened dialog against it before
  assigning a fresh id turns re-crawls into references (the seen-set the design demands).
  (learned from kb/word-home-insert step5 DepthWalker.resolve_known)
- 2026-07-10 — **In-tree WinUI ContentDialogs and full-page views do NOT close on the top-level
  reset you use for windowed popups — reset them explicitly.** Modern Paint's Edit-colours and
  Resize&Skew are IN-TREE modal dialogs (no separate HWND): a reset that only Escapes and checks
  for popup WINDOWS reports "clean" while the modal is still up and blocking all input (this hung a
  run). Close them by clicking their **Cancel** button (find its rect via the raw walker — a
  pywinauto `child_window(title="Cancel")` search takes 130s on a big dialog tree — then click the
  point), and verify BOTH no popup window AND no Cancel-in-tree remains. The **Settings** page is a
  full-page in-window view that Escape can't close either — exit via its **Back** arrow; put such
  controls LAST in a worklist so if the exit fails they don't hide the rest of the toolbar.
  (learned from kb/paint step2: driver.reset_surfaces + return_from_settings)
- 2026-07-10 — **A split button's dropdown open-point must be recomputed at press time, never
  cached.** A depth pass that computed each dropdown-zone point once when the tab was first
  activated failed to open the shared color-picker / crop split buttons ('no-surface-appeared'):
  the ribbon shifts as the object selection changes between targets, so the stale point lands on
  the PRIMARY zone (which just arms crop mode / applies the last color) and opens nothing.
  Re-enumerate the LIVE split element right before the click and use its exact `*_Dropdown`
  child rect (`split_zone_rects`), exactly as step-2/3 do. Same failure class: the pywinauto UIA
  `win` wrapper goes stale after heavy interaction (esp. after an OS file dialog) and
  `select_tab` starts raising — re-attach `Desktop(...).window(handle=frame)` and retry before
  giving up. (learned from kb/word-home-insert-v2 step5: run_step5_stragglers + tab-activate retry)

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

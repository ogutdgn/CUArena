# uia — UI Automation (pywinauto `backend="uia"` + raw IUIAutomation)

> Evidence paths below refer to the MS-Word crawler this was distilled from
> (mirrored in `references/word-crawler/`).

## Purpose

UIA is the primary *reading* tool: it exposes the app's UI as a tree of elements with a name,
control type, screen rectangle, enabled state, and (sometimes) the app's internal command id.
Use it to enumerate command surfaces (ribbons/toolbars), to walk dialog contents (fields, tabs,
buttons), and to read task panes. It is NOT a reliable *classification* tool (what a control
does when pressed) and it is blind inside owner-drawn surfaces — see `pixel.md` for the escape
hatch and `win32.md` for press-classification.

## How to use

**Attach to the app's real frame window, then force foreground:**

```python
win = Desktop(backend="uia").window(handle=frame_hwnd)   # frame found via win32 (see win32.md)
win.set_focus()
_force_foreground(frame_hwnd)                            # AttachThreadInput dance, see input.md
```

**Pin your locators from a live tree dump, never from guesses.** The Word crawler shipped a
`--dump-tree` mode first, and only then hard-coded locators that the dump proved
(`crawler/uia.py` module docstring). Word's ribbon nesting turned out to be:
`Pane 'Ribbon' > Tab 'Ribbon Tabs' (TabItems) + Pane 'Lower Ribbon' > Group '<active tab>'
(wrapper) > Group '<group label>'` — two nested Groups where you'd expect one.

**Read properties through the raw element when the wrapper lies:**

```python
raw = el.element_info.element                 # IUIAutomationElement
tooltip = raw.GetCurrentPropertyValue(30159)  # FullDescription — the ScreenTip text
label_el = raw.GetCurrentPropertyValue(30003) # LabeledBy — a field's label element
```

**Detect available patterns via `Is<Pattern>AvailablePropertyId`, never via `iface_*`:**

```python
_PATTERN_PROP = {"invoke": 30031, "toggle": 30086, "expand_collapse": 30070,
                 "selection_item": 30096, "value": 30045, "range_value": 30052,
                 "scroll": 30056, "legacy_i_accessible": 30090}
available = [n for n, pid in _PATTERN_PROP.items() if raw.GetCurrentPropertyValue(pid)]
```

**Enumerate a command surface as interactive LEAVES**, treating composites
(SplitButton, ComboBox) and in-ribbon galleries as ONE atomic control, and dedupe by
`runtime_id` (`crawler/uia.py::_leaves`, `::enumerate_tab`).

**Walk dialogs with `descendants()`** — modal dialogs expose a full tree (unlike flyouts).
Click each `TabItem` and enumerate per tab; identify anonymous fields by LabeledBy first, then
by nearest-label geometry (same row to the left, else directly above)
(`crawler/capture.py::capture_dialog`, `::_page_fields`, `::_nearest_label`).

**Expand collapsed panels before enumerating fields** — some dialogs hide their controls
behind ExpandCollapse groups. Call the pattern, but only on Button/Group elements, and verify
no popup window spawned (a dropdown-button also exposes ExpandCollapse — expanding it opens a
menu; ESC it and skip) (`crawler/capture.py::_expand_groups`).

## Known traps

- **`iface_*` attributes on pywinauto wrappers exist on EVERY element** — accessing them never
  fails, so they are useless for pattern detection. Only the raw
  `GetCurrentPropertyValue(Is<Pattern>AvailablePropertyId)` calls tell the truth
  (`crawler/uia.py` docstring).
- **Pattern availability does not tell you what a control IS.** Word's Bold exposes
  `SelectionItem`, not `Toggle`. Record patterns for an exposure map if you want, but
  classify controls by pressing and observing, never by pattern inference
  (`crawler/uia.py` docstring, `crawler/exposure.py`).
- **Owner-drawn flyouts (menus, galleries, color pickers) return an EMPTY container** from UIA
  tree walks. Their items are only reachable by `IUIAutomation.ElementFromPoint` hit-testing
  (see `pixel.md`) (`crawler/capture.py` module docstring).
- **The tooltip is NOT in HelpText.** On Office ribbons HelpText is empty even on hover; the
  ScreenTip text lives in FullDescription (property id 30159)
  (`crawler/uia.py::_props`).
- **Icon-only buttons can have an empty Name.** The Styles pane's New Style / Style Inspector /
  Manage Styles buttons have `Name == ""`; their label lives in FullDescription, then
  AutomationId as last resort. Filtering on "has a name" silently drops real controls
  (`crawler/capture.py::capture_pane`).
- **Multi-tab dialogs are left on the LAST tab you enumerated.** A button you recorded (from an
  earlier tab) will then fail `child_window` resolution. Search across tabs: on a miss,
  re-activate each TabItem and retry (`crawler/run_p0.py::_find_button_rect`).
- **Read `CurrentIsEnabled` on every item you might press.** Pressing a disabled menu item does
  nothing — but your "what opened?" detection may then latch onto the still-open flyout and
  capture garbage (`crawler/capture.py::_sample_popup` docstring, `crawler/run_p0.py::_drain_popup`).
- **UIA scrollbar part-buttons leak into item enumerations** as fake items named "Line up",
  "Page down", etc. — filter them as chrome (`crawler/textutil.py::_CHROME_NAMES`).

## Lessons learned

- 2026-07-09 — **Some apps expose their internal command id in `AutomationId`** — Office calls
  this idMso (Bold → `Bold`, the Font launcher → `FontDialog`). This is gold for binding UI
  captures to an automation API later; always record it.
  (learned from `crawler/uia.py` docstring / `::_props`)
- 2026-07-09 — **Split buttons expose BOTH zones as children** (a Button for the primary action
  + a MenuItem named `*_Dropdown` for the flyout). Prefer those child rects as click targets
  over guessing a fraction of the parent rect.
  (learned from `crawler/uia.py` docstring, `crawler/prober.py::zone_point`)
- 2026-07-09 — **Field identity: LabeledBy → nearest-label geometry → give up on the raw name.**
  Raw names like "RichEdit Control" are generic across the dialog; LabeledBy (30003) is the
  strongest signal, and a nearest-label fallback (same row left, else above) resolves the rest.
  (learned from `crawler/capture.py::_page_fields`, `::_nearest_label`)
- 2026-07-09 — **Toggle state, when you need it, has three fallbacks:** wrapper
  `get_toggle_state()` → `is_selected()` → raw `IsSelectionItemPatternAvailable` (30096) +
  `IsSelected` (30079). Office toggles report through SelectionItem.
  (learned from `crawler/prober.py::_read_toggle_state`)
- 2026-07-09 — **Descend-or-atomic needs an explicit rule.** A ribbon Group contains interactive
  nodes that themselves contain interactive nodes; the crawler descends only when a control has
  interactive descendants AND is not a composite/gallery. In-ribbon galleries are detected by a
  DataGrid/List descendant and kept whole.
  (learned from `crawler/uia.py::_leaves`, `::_is_gallery`)
- 2026-07-09 — **ExpandCollapse pattern CALLS raise when unsupported; attribute access does not.**
  Wrap the call, not the lookup — and guard expansion with a window-set check so a
  dropdown-button masquerading as an expander gets ESCed instead of polluting the capture.
  (learned from `crawler/capture.py::_expand_groups`)

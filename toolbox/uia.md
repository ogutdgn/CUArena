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
- 2026-07-09 — **A SplitButton's own AutomationId can be EMPTY even when its siblings carry idMso.**
  Re-dumped live on Word 16.0.20131 (kb/word run): `Underline`/`FontColorPicker`/`Bullets` expose
  their idMso on the SplitButton node, but `Paste`'s SplitButton has `AutomationId == ""` — its
  idMso (`Paste`) lives only on the primary-zone child Button. So when you keep a split button
  atomic, backfill its id from the primary child (`split.children()` → the Button, not the
  `*_Dropdown` MenuItem) or you get an id-less control. Name (`'Paste'`) + type still identify it.
  (learned from kb/word/scripts/tools/enumerator.py + dumps/home_enum.json)
- 2026-07-09 — **AccessKey is a FREE keyboard trigger-path, parallel to AcceleratorKey.** Every
  ribbon leaf exposes its keytip chain in `CurrentAccessKey` (Bold → "Alt, H, 1", Font dialog →
  "Alt, H, F N"), independent of the Ctrl-style shortcut in `CurrentAcceleratorKey` (Bold →
  "Ctrl+B"). The keytip chain literally IS the mouse trigger path in keyboard form (tab H →
  group → control), so it doubles as a cross-check that your ribbon-nesting locators are right.
  Harvest both fields in the same read. (learned from kb/word dump: `_props` AccessKey/AcceleratorKey)
- 2026-07-09 — **The in-ribbon QuickStyles gallery IS in the UIA tree, unlike owner-drawn
  flyouts.** `DataGrid 'Styles' > ListItem`s ('Normal', 'Heading 1', 'Title'…) are fully
  enumerable via a normal tree walk — no hit-testing needed. Its 'More' chevron button is flaky to
  click (center-click lands on a style tile and applies it), so to document the gallery, enumerate
  the DataGrid directly rather than opening the expanded dropdown.
  (learned from kb/word depth: enter_styles_gallery)
- 2026-07-09 — **To open a split button's DROPDOWN you must click its dropdown ZONE, not the
  stored control rect's center** — the center hits the PRIMARY zone (which applies the default
  action, e.g. fills red). Recover the exact zone at press time from `split_zone_rects(el)` (the
  `*_Dropdown` MenuItem child) or a ComboBox's `Open` button child; a step-2 record that stored the
  whole split-button rect as `bounds` is a trap when re-driving in depth.
  (learned from kb/word/scripts/tools/run_step5_enter.py::build_open_points)
- 2026-07-09 — **A maximized OpusApp frame's window rect starts at (-8,-8).** `GetWindowRect`
  on the maximized frame returns `[-8,-8,1928,1040]` (the invisible resize border). A window-true
  `ImageGrab.grab(bbox=rect, all_screens=True)` still captures correctly, but any control `bounds`
  you crop must be taken RELATIVE to that grabbed rect's origin, not screen (0,0), or the crop is
  off by 8px. (learned from kb/word/scripts/drive/stage.py + tools/capture.py rel_bounds)
- 2026-07-09 — **Ribbon-face gallery openers can be `MenuItem` leaves, not Buttons.** Word's
  Insert tab exposes its big gallery dropdowns (Table `TableInsertGallery`, Pictures
  `FlyoutAnchorInsertPictures`, Header, Text Box, Symbol…) as top-level `MenuItem` controls with
  no children — unlike Home, where almost everything is Button/SplitButton/ComboBox. A leaf
  enumerator whose INTERACTIVE set omits MenuItem at ribbon level silently drops most of the
  Insert tab. (learned from kb/word-home-insert dump: uia_tree_insert.txt)
- 2026-07-10 — **WinUI apps (Windows 11 Paint) expose a FULLY WALKABLE UIA tree — the opposite
  of Office owner-drawn flyouts.** Menu items (File > New/Open/Save…), colour swatches (named
  `ListItem`s: 'Black','Gray','Red'…), and shape pickers (`ListItem` 'Line'/'Oval'/'Heart'…) are
  all real tree elements — no `ElementFromPoint` hit-testing needed for menus/pickers (reserve it
  for the Edit-colours colour WHEEL and raw canvas pixels only). Stable `AutomationId`s exist on
  many controls (`PencilTool`,`EraserTool`,`CropButton`,`RotateDropdown`,`Flip`,
  `BrushesSplitButton`,`CopilotDropDownButton`,`ZoomSliderControl`,`SettingsButton`,
  `OptionsButton`,`CanvasSizeTextBlock`) — the strongest locators; record them always. The whole
  app is ~170 nodes. (learned from kb/paint step1: dumps/uia_tree.txt)
- 2026-07-10 — **Diff the tree with the RAW `IUIAutomation` ControlViewWalker, NEVER pywinauto
  `.descendants()`/`.children()` — 150s vs 1s.** A press-observe detector that snapshotted the
  main window's subtree via pywinauto wrappers took 150+ seconds PER PRESS once a rich dialog
  (Paint's Edit-colours: colour wheel + ~110 swatches) was open, because each wrapper creation
  re-queries UIA. Walking the RAW element (`win.element_info.element` → `iuia.ControlViewWalker`
  with `GetFirstChildElement`/`GetNextSiblingElement`, reading `CurrentControlType/CurrentName/
  CurrentBoundingRectangle`) is ~1s. Key nodes by `(control_type, name, rect)` — do NOT call
  `GetRuntimeId()` per node (a COM round-trip each). Cache the raw frame element ONCE and reuse it.
  (learned from kb/paint step2: surface.descendant_index / find_rect)
- 2026-07-10 — **`ElementFromHandle` (what `Desktop(backend="uia").window(handle=)` resolves to) is
  a FLAKY, slow COM call — minimise it.** It intermittently raises
  `COMError(-2146233083)` = `UIA_E_ELEMENTNOTAVAILABLE`, especially right after a modal closes or
  the window is animating. Resolve the frame's raw element ONCE (retry ~12×0.5s, re-deriving the
  hwnd from the pid each try) and cache it; re-attach a pywinauto wrapper only for control
  resolution, only on an actual miss — re-attaching every probe multiplies the flakiness.
  (learned from kb/paint step2: session.raw_frame + uia_read.attach)
- 2026-07-10 — **WinUI keytips (`CurrentAccessKey`) ARE the keyboard trigger path AND cover every
  control, even ones with no Ctrl-accelerator.** Paint exposes `Alt, T, P` (Pencil), `Alt, I, C`
  (Crop), `Alt, 1` (Color 1), `Alt, L` (Layers), `Alt, B` (Brushes) as AccessKey on each leaf,
  while only a few carry `CurrentAcceleratorKey` (Save Ctrl+S, Undo Ctrl+Z, Redo Ctrl+Y). Harvest
  BOTH in the same read; the Alt-chain doubles as a mechanical trigger path and a cross-check of
  your group nesting. (learned from kb/paint step1 dump: AccessKey on every toolbar leaf)
- 2026-07-09 — **Enumerate with a representative document state, or state-gated controls read
  DISABLED and their probes get wrongly skipped.** Insert > Drop Cap is disabled on an empty
  document and enables once the doc has a paragraph of text; Cut/Copy need a selection. Give the
  scratch fixture text + a selection BEFORE enumerating/probing, and journal any control that
  still reads disabled. (learned from kb/word-home-insert dump: DropCapInsertGallery DISABLED)

- 2026-07-12 — **In-ribbon galleries are THREE-zone controls; pressing a tile does not classify
  the gallery.** UIA exposes the visible gallery tiles as `menuitem`-ish children, so a naive
  walker presses one tile, sees a state change (a style got applied) — or nothing — and closes
  the WHOLE gallery as a single endpoint. That silently drops the full gallery flyout AND the
  commands under it ("New/Modify/Clear …" — which open dialogs). Found in the word-home-insert-v2
  audit: 11 galleries (Table/Picture/Shape/Chart/SmartArt Styles, Equation Symbols…) closed this
  way, 2 of them with `no observable effect` yet still marked as triggering. At press time,
  re-enumerate the LIVE gallery element and look for its expand zone: the gallery control
  usually advertises `ExpandCollapsePattern` (check via raw `Is<Pattern>AvailablePropertyId`,
  same trap as split buttons) and/or owns a distinct "More"/drop-arrow child at its edge — drive
  THAT to open the full flyout, and record the tile press separately. Playbook rule: R2.5.

# Writer — Deep Interaction Audit

> A detailed pass over every ribbon item, every workflow, every editor-feel
> surface, and every dialog path — to fix the gap the owner flagged:
> *"buttons like `.uno:LineSpacing` and the colour buttons don't let me change
> anything."* Companion to [`AUDIT_CODEX.md`](AUDIT_CODEX.md) (independent pass,
> written in parallel for cross-check). Last updated: 2026-05-28.

---

## 1. Symptom → diagnosis

A ribbon button that, in Word, opens a **chooser** (dropdown menu / colour
palette / preset gallery) is wired here as a plain button that just dispatches
`postUno(cmd)` with no argument. Most of those `.uno:` slots either:

- need an **argument** to do anything useful (`FontColor.Color`, `BackColor.Color`,
  `SpacePara1/15/2` for line spacing, `Zoom.Value` for zoom), or
- open an LO **sidebar floater** when the user clicks (LO ships dropdown UIs as
  sidebar widgets — they never reach LOK's JSDIALOG stream, so our renderer
  sees nothing and nothing happens).

So the dominant remaining W3 gap is **about 25 ribbon items that should be
popups / dropdowns / pickers but are plain buttons today**. The framework
(Ribbon + DialogHost + STATE_CHANGED bindings) is fine; we just need two more
control kinds (`dropdown`, `colorpicker`) and to mark these items with them.

---

## 2. Ribbon control taxonomy

Each ribbon item is one of the kinds below. Today we have 1–4; the proposal is
to add 5 and 6 (and later 8 for nicer Paste/Undo).

| # | Kind | QML / state contract | Items today |
|---|---|---|---|
| 1 | **button** (default) | `onClick → postUno(cmd, args?)`. No state. | most |
| 2 | **toggle** | `onClick → postUno`. `active` from `STATE_CHANGED ".uno:Cmd=true"` lit blue. | Bold, Italic, alignments, view toggles… |
| 3 | **dialog-opener** | `onClick → postUno(cmd)` → engine emits `LOK_CALLBACK_JSDIALOG` → `DialogHost` renders natively; round-trip via `sendDialogEvent`. | SearchDialog, PageDialog, WordCountDialog, InsertTable, FootnoteDialog, … |
| 4 | **combo** | Editable. Current value from `STATE_CHANGED CharFontName / FontHeight`. `onAccepted → postUno` with the typed/picked value. | Font name, Font size |
| 5 | **dropdown** *(new)* | Click main → primary action *or* open popup; popup = a `Menu` of `(label, cmd, args, icon)` options; selecting fires `postUno(opt.cmd, opt.args)`. | LineSpacing, PageMargin, Orientation, AttributePageSize, PageColumnType, Zoom, DefaultBullet, DefaultNumbering, TextWrap, ChangeCase, InsertBreak, Watermark, … |
| 6 | **colorpicker** *(new)* | Split-button: **icon** applies the last-picked colour (or `Automatic`); **▾** opens a palette (theme/standard swatches + Automatic + "More Colours…" → engine picker). Dispatches `postUno(cmd, {<argName>.Color:<int>})`. | FontColor, BackColor (Highlight), BackgroundColor (page bg), Border colour |
| 7 | **gallery** *(later)* | Larger preview grid: paragraph-style preview, watermark presets, header/footer presets, table size grid. | Styles, Watermark, InsertTable size grid, Header/Footer presets |
| 8 | **split-button** *(later)* | Primary action + ▾ dropdown distinct. | Paste / Paste Special, Undo / Undo history |

The two new kinds (#5, #6) account for the bulk of the user-visible quality
gap. Everything else is polish.

---

## 3. Per-item audit (all 147 items)

Rows below mark the **gap** only; items already working as expected are
omitted. Format: *current behaviour → correct kind → dispatch when picked*.

### Home

| Item | Current → Correct | Notes / args |
|---|---|---|
| `FontColor` | plain → **colorpicker** | `{FontColor.Color:{type:"long",value:<int>}}`. Palette + Automatic (= `-1`) + More Colours. **P0** |
| `BackColor` (Highlight) | plain → **colorpicker** | `{BackColor.Color:{type:"long",value:<int>}}`. Palette + No Fill + More. **P0** |
| `BackgroundColor` (¶ bg) | plain → **colorpicker** | `{BackgroundColor.Color:{type:"long",value:<int>}}`. **P1** |
| `LineSpacing` | plain → **dropdown** | 1.0 → `.uno:SpacePara1`; 1.5 → `.uno:SpacePara15`; 2.0 → `.uno:SpacePara2`; "Line Spacing Options…" → `.uno:ParaspaceIncrease`/ProportionalLineSpacing dialog. **P0 — user's named complaint.** |
| `DefaultBullet` | toggle → **dropdown** (split-toggle) | Click = toggle default bullet; ▾ = pick style → `.uno:BulletsAndNumberingDialog`. **P1** |
| `DefaultNumbering` | toggle → **dropdown** (split-toggle) | Same pattern. **P1** |
| `BorderDialog` | dialog → **dropdown** + dialog fallback | Word-style border presets (Top/Bottom/All/None/…); fallback = the existing dialog. **P2** |
| `ChangeCaseRotateCase` | plain → **dropdown** | Sentence case / lowercase / UPPER / Capitalise Each Word / tOGGLE → distinct `.uno:` (`ChangeCaseToSentenceCase`, `ChangeCaseToLower`, `ChangeCaseToUpper`, `ChangeCaseToTitleCase`, `ChangeCaseToToggleCase`). **P1** |
| `Paste` | plain → **split-button** | Primary = Paste; ▾ = Paste Special (`.uno:PasteSpecial`). **P3** |
| `Underline` | toggle → **split-button** (toggle + style ▾) | Click toggles single; ▾ = style picker (Double, Wave…). **P3** |
| `StyleApply` × 4 | dialog-arg dispatch (works) | OK — but the **gallery** kind would let us show live previews. **Later.** |

### Insert

| Item | Current → Correct |
|---|---|
| `InsertTable` | dialog → **gallery + dialog** (mini grid + "Insert Table…") |
| `InsertGraphic` | plain → **our own Qt FileDialog** (OS picker is not exposed via LOK). **P1.** |
| `BasicShapes` / `InsertDraw` | plain → **shape gallery dropdown** |
| `HyperlinkDialog` | plain (engine WINDOW-only) → **enabled.cxx patch** + dialog. **P1.** |
| `InsertPageHeader` / `InsertPageFooter` | plain → **dropdown** of presets (Blank, three-column, …). |
| `EditGlossary` | dialog → **dropdown of recent AutoText** + dialog. |

### Design

| Item | Current → Correct |
|---|---|
| `Watermark` | plain → **gallery** of presets ("Confidential", "Draft", …) + Custom. **P2.** |
| `BackgroundColor` (page) | plain → **colorpicker**. **P1.** |

### Layout — *the big one for Word feel*

| Item | Current → Correct | Dispatch |
|---|---|---|
| `PageMargin` | plain → **dropdown** | Normal / Narrow / Moderate / Wide / Mirrored / Custom (Custom → `.uno:PageDialog`); presets need argful dispatch — see §3-impl below. **P0** |
| `Orientation` | plain → **dropdown** | Portrait / Landscape. LO has no single `.uno` switch; we dispatch `.uno:PageDialog` (Page tab) or apply via `Margin`/`AttributePageSize` args. **P0 (open PageDialog as v1).** |
| `AttributePageSize` | plain → **dropdown** | Letter / A4 / Legal / A3 / Tabloid / B5 / Custom (→ PageDialog). **P0** |
| `PageColumnType` / `InsertSection` | plain → **dropdown** | One / Two / Three / Left / Right / More → `.uno:InsertColumnBreak` for breaks, `.uno:Columns` arg for layout. **P1** |
| `InsertBreak` | dialog → **dropdown** | Page break (`.uno:InsertPagebreak`), Column break (`.uno:InsertColumnBreak`), Section breaks (`.uno:InsertSection`). **P2** |
| `TextWrap` | plain → **dropdown** | None / Parallel / Through / Optimal / Before / After / Edit Contour → `.uno:WrapOff/WrapOn/WrapThrough/WrapIdeal/WrapLeft/WrapRight/ContourDialog`. **P2** |

### References

All current items dispatch directly; behaviour is acceptable. Two refinements:
- `InsertFootnote`/`InsertEndnote` could be **split-toggle** (click inserts;
  ▾ opens settings); LO already has `.uno:FootnoteDialog`. **P3.**
- `InsertAuthoritiesEntry` → opens a JSDialog (works).

### Review

All current items work. `TrackChanges`/`ShowTrackedChanges` toggles light up
correctly. **No gaps.**

### View

| Item | Current → Correct |
|---|---|
| `Zoom` | dispatches ZoomDialog (works) → **dropdown** with 50/75/100/150/200% + Page Width + Whole Page + Zoom… | `.uno:Zoom` with `{Zoom.Value:{type:"long",value:<percent>}}`. **P1.** |
| Other view toggles | OK |

### File

| Item | Current → Correct |
|---|---|
| `Open` / `SaveAs` | dispatches LO's headless picker (doesn't render) → **Qt FileDialog** in our layer. **P1.** |

### Design / Help

Already adequate.

**Gap totals: 4 colorpickers, ~12 dropdowns, 3 OS-pickers, 1 enabled.cxx
patch (Hyperlink), 4 galleries for later.**

---

## 4. Workflow traces (where the gaps actually hurt)

| Workflow | Steps a user does | Where we fail today |
|---|---|---|
| **Typing & format** | type → Bold → Italic → set Font/Size → Color → Highlight | Color/Highlight: clicking does nothing visible (the engine sidebar floater is silent). |
| **Paragraph** | select → Center → Bullets → Line Spacing 1.5 → Indent | LineSpacing button is a no-op. Bullet style not pickable (only default toggle). |
| **Page setup** | Layout → Margins → Narrow → Orientation → Landscape → Size → Letter | All three are no-ops today; user must open `.uno:PageDialog` and find them in the tab maze. |
| **Insert table** | Insert → Table → pick 4×3 grid | Today the dialog opens (works since the enabled.cxx patch), but the **grid picker** is the natural Word UX (mini 10×8 hover). |
| **Find/Replace** | Ctrl+F → Find next | Works (`SearchDialog` JSDialog renders). |
| **Header/Footer** | Insert → Header → Built-in: "Blank with three columns" | Today: clicking `.uno:InsertPageHeader` inserts a header but no preset gallery → user gets the engine's "default + cycle" UX, not Word's. |
| **Image insert** | Insert → Picture → pick file | Engine OS dialog won't open in our Qt window — `InsertGraphic` is effectively dead. |
| **Track changes flow** | toggle Record → edit → Accept → Next → Reject All | **Works fully.** |
| **Comments** | Insert → Comment → type → Reply → Delete | **Works** (engine sidebar wires comments). |
| **Zoom + view** | Status-bar zoom slider; View → Zoom 150% | No status-bar zoom slider yet. Zoom buttons work as fixed presets only. |
| **Save .docx** | Ctrl+S → pick filename → Save | Save-As OS dialog dead; we need our Qt FileDialog. |
| **Export PDF** | File → Export PDF → range options | Engine FilterOptions dialog might not surface; needs investigation. |
| **Spell check** | Review → Spelling → fix | `SpellingAndGrammarDialog` JSDIALOG works headlessly in our renderer (verified). |

---

## 5. State (`STATE_CHANGED`) binding gaps

These items reflect engine state in the UI but currently don't bind:

- **Font name / Font size combos** — already bind (verified "Liberation Serif" / "12").
- **Alignment toggles** — bind (one is always lit).
- **Bold/Italic/etc.** — bind.
- **`disabled`** — `STATE_CHANGED` sends `".uno:Copy=disabled"` when nothing is
  selected; `RibbonButton.disabled` already greys the button. **Working** but
  some new dropdowns won't honour disabled until I add the same binding.
- **Line spacing / Bullet active style** — `.uno:SpacePara1/15/2` toggle states
  exist in STATE_CHANGED → the new `LineSpacing` dropdown should show a check
  next to the currently-active value.
- **Zoom %** — `.uno:Zoom` returns the current zoom; the dropdown can show it
  ("100%") and the status-bar zoom widget binds to it.
- **PageStyleName** — already in `formatAtCursor` → the Layout / Margins button
  could surface "Default Page Style" subtle hint.

---

## 6. Editor-feel gaps

The fixes that aren't in the ribbon at all:

| Surface | State | Plan |
|---|---|---|
| Caret blink | **done** | — |
| Selection highlight | **done** | — |
| Drag-select | **done** | — |
| Double-click word | **done** | — |
| **Triple-click paragraph** | missing | `mouseDoubleClick` `count=3` for paragraph select. **P2.** |
| **Mouse wheel scroll** | works (Flickable) | But `Ctrl+Wheel` for zoom is missing. **P2.** |
| **Keyboard shortcuts** | partial — `Ctrl+B/C/V/X/Z` go through Qt → forwarded as raw keys but we don't translate to `.uno` dispatch | Add accelerator map (Ctrl+B → `.uno:Bold`, Ctrl+S → save, Ctrl+F → SearchDialog, …). **P1.** |
| **Scrollbar polish** | basic Flickable scrollbar | Word-style thin scrollbar, page indicator. **P3.** |
| **Zoom slider** | missing in status bar | Status-bar zoom widget + `Ctrl+Wheel`. **P2.** |
| **Ruler** | toggle exists, no actual ruler drawn | Draw a ruler overlay (twips → cm/inch). **P3.** |
| **IME / Turkish characters** | unverified | The current `postKey` uses `event->text()[0].unicode()`, which loses multi-codepoint input methods. Add `inputMethodEvent`. **P2.** |
| **Drag/drop into doc** | unverified | Wire `dragEnter`/`drop` → `.uno:InsertGraphic` with file URL. **P3.** |
| **Clipboard** | LO drives system clipboard via the engine — verified Copy/Cut/Paste work in the doc. Cross-app clipboard untested. **P3.** |

---

## 7. Dialog coverage status

Live audit (`tests/dialog_audit.cpp`) → `W4_DIALOG_COVERAGE.md`:

- **JSDIALOG native (renders, round-trips)**: Page, Font, Paragraph, Search,
  Columns, Break, Symbol, WordCount, indices, InsertTable, InsertBookmark.
- **WINDOW-only (D6 enabled.cxx tail)**: **HyperlinkDialog** (P1), About.
- **OS-native pickers** (need our own Qt dialog): Open/Save, InsertGraphic.

---

## 8. Performance / robustness

- **Tile cache** — none. `paint()` re-renders the entire page each call.
  At 100% for 1–few pages this is fine; pagination + scroll fluency need a tile
  pyramid. **W2-tail.**
- **Selection rect splits** — `TEXT_SELECTION` payload can be many rects on
  multi-line selection; the current renderer iterates `m_selectionTwips` and
  draws each. **Working.**
- **Dirty regions** — we ignore `INVALIDATE_TILES` rect (always full repaint).
  Acceptable for one-page docs. **W2-tail.**
- **Memory** — outcome.jsonl appends a snapshot per second (≈ 8 KB each);
  unbounded today. **Cap N sessions, rotate JSONL.** **P2.**

---

## 9. Prioritised gap list (the top 20)

| # | Item | What | Where | Pri |
|---|---|---|---|---|
| 1 | LineSpacing dropdown | 1/1.15/1.5/2 + Options | new RibbonDropdown + spec | **P0** |
| 2 | FontColor palette | swatch grid + Automatic + More | new RibbonColorButton | **P0** |
| 3 | BackColor (Highlight) palette | swatch grid + No Fill + More | RibbonColorButton | **P0** |
| 4 | PageMargin dropdown | Narrow/Normal/Wide/Mirrored/Custom→PageDialog | RibbonDropdown | **P0** |
| 5 | Orientation dropdown | Portrait/Landscape→PageDialog (v1) | RibbonDropdown | **P0** |
| 6 | AttributePageSize dropdown | Letter/A4/Legal/Custom | RibbonDropdown | **P0** |
| 7 | BackgroundColor (¶/page) | RibbonColorButton | RibbonColorButton | **P1** |
| 8 | Zoom dropdown | 50/75/100/150/200/Page Width/Whole | RibbonDropdown | **P1** |
| 9 | Bullets/Numbering dropdowns | style picker | RibbonDropdown | **P1** |
| 10 | PageColumnType dropdown | 1/2/3/Left/Right/More | RibbonDropdown | **P1** |
| 11 | ChangeCase dropdown | 5 modes | RibbonDropdown | **P1** |
| 12 | InsertGraphic file picker | Qt FileDialog → .uno:InsertGraphic args | new in main / DocumentCanvas | **P1** |
| 13 | Open / SaveAs Qt FileDialogs | Same | main wiring | **P1** |
| 14 | Keyboard shortcuts → .uno | Ctrl+B/I/U/S/F/Z/Y/X/C/V… | DocumentCanvas keyPressEvent | **P1** |
| 15 | HyperlinkDialog enabled.cxx | engine patch + rebuild vcl | enabled.cxx | **P1** |
| 16 | InsertTable mini-grid picker | gallery popup | new (later — dialog works) | **P2** |
| 17 | TextWrap dropdown | wrap modes | RibbonDropdown | **P2** |
| 18 | Watermark gallery | presets | gallery later | **P2** |
| 19 | Ctrl+Wheel zoom + status-bar zoom slider | engine `setClientZoom` | Main.qml + LokEngine | **P2** |
| 20 | Ruler overlay | twips→cm/inch ticks | DocumentCanvas overlay | **P3** |

---

## 10. Implementation plan for P0/P1 (this session)

1. **`RibbonDropdown.qml`** — generic. Props: `item`, `engine`, `stateMap`.
   `item.options:[ { label, cmd, args?, icon?, divider?, [check from stateMap] } ]`.
   Renders the button + a ▾ popup `Menu`. Selecting an option →
   `engine.postUno(opt.cmd, opt.args || "")`. Active option ticked.
2. **`RibbonColorButton.qml`** — split. Props: `item`, `engine`, `lastColorHex`.
   `item.argName` (e.g. `"FontColor.Color"`), `item.swatchColor` (red/yellow).
   Main click → `engine.postUno(item.cmd, JSON.stringify({[argName]:{type:"long",value:lastColorInt}}))`.
   ▾ → popup with 8×5 theme swatches + Automatic (`-1`) + No Fill (also `-1`) +
   More Colours… (→ engine picker fallback `.uno:FontColorPicker` / falls back
   to engine if no LOK colour-picker available).
3. **Wire into RibbonGroup** by `item.kind`: `dropdown` → `RibbonDropdown`,
   `colorpicker` → `RibbonColorButton`. Keep existing `fontcolor`/`highlight`
   kinds as **aliases** for colorpicker so existing items just light up.
4. **`build_ribbon.py` v3** — add `kind:"dropdown"` with `options:[…]` for the
   12 items above; flip `FontColor`/`BackColor`/`BackgroundColor` to `colorpicker`
   with the right `argName` + `swatchColor` and a default `lastColor`.
5. **Keyboard shortcuts** — `DocumentCanvas::keyPressEvent`: a small map
   `Ctrl+B → ".uno:Bold"`, etc., short-circuits before forwarding raw keys.
6. **Qt FileDialogs** — `InsertGraphic` button intercepts in QML: open
   `FileDialog`, on accept call `engine.postUno(".uno:InsertGraphic",
   JSON.stringify({FileName:{type:"string",value:url}}))`. Same for Open/Save/SaveAs.

### Codex parallel pass (cross-check, 2026-05-28)

Codex was asked the same audit in parallel. It confirmed the diagnosis
(every non-combo item routes through `RibbonButton`'s single `TapHandler` with
no popup/palette/gallery anywhere) and surfaced the exact LO sources to mine
for proper popup-with-args dispatch later:

- **Colours:** `svx/source/tbxctrls/tbcontrl.cxx`, `…/PaletteManager.cxx` — the
  authoritative `SvxColorMenuController` / `SvxColorWindow` that builds LO's
  Font/Highlight palettes. We can read the same item names + apply patterns to
  refine our `RibbonColorButton`.
- **Bullets/Numbering:** `svx/source/tbxctrls/bulletsnumbering.cxx` — the
  bullet/number style gallery (used to upgrade from dispatch-only toggle to a
  real style picker).
- **Line spacing:** `svx/source/sidebar/paragraph/ParaLineSpacingControl.cxx` —
  the LO floater that draws the dropdown; gives us the proportional/at-least
  args if we want them beyond Single/1.5/2.
- **Margins / Orientation / Size / Columns:** `sw/source/uibase/sidebar/*Control.cxx`
  — these sidebar widgets dispatch via `SfxItemSet` directly (not via single
  `.uno:` slots), which is why our dropdown options fall back to `PageDialog`
  for now. Wiring them through is a tail item; reach for these files when
  doing it.

No items missed by either pass; the deltas above are *future polish* sources.

---

## Appendix — engine-arg shapes used above

(All verified from `vcl/jsdialog/executor.cxx` / SfxItemSet handlers.)

```
.uno:FontColor       {"FontColor.Color":{"type":"long","value":<int 0xRRGGBB or -1>}}
.uno:BackColor       {"BackColor.Color":{"type":"long","value":<int>}}
.uno:BackgroundColor {"BackgroundColor.Color":{"type":"long","value":<int>}}
.uno:CharFontName    {"CharFontName.FamilyName":{"type":"string","value":"Arial"}}
.uno:FontHeight      {"FontHeight.Height":{"type":"float","value":12.0}}
.uno:Zoom            {"Zoom.Value":{"type":"long","value":100}}
.uno:SpacePara1      no args  (single)
.uno:SpacePara15     no args  (1.5)
.uno:SpacePara2      no args  (double)
.uno:ChangeCaseToUpper / ToLower / ToSentenceCase / ToTitleCase / ToToggleCase — no args
.uno:WrapOff / WrapOn / WrapIdeal / WrapLeft / WrapRight / WrapThrough — no args
```

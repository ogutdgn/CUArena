# Table Layout (contextual tab) — Insert > Tables

> Button-by-button feasibility for the **Table Layout** contextual tab (Word labels it plain
> **Layout** — the second of the two tabs Word raises when the selection is inside a `w:tbl`).
> Companion: `table-design-tab.md`. Parity reference: **Word for Windows 16.0** (ADR-0006).
> Every claim below is grounded in `file:line`.
>
> Clone code touchpoints:
> - Tab definition (what renders): `src/renderer/public/js/table-tools-pm.js:22-60` (`layoutTab()`).
> - Handlers (`H.tbl*`): `src/renderer/public/js/commands.js:110-178`.
> - Bridge verbs (`WC.PM.*`): `src/renderer/bridge/table.ts:21-447`.
> - Fork table commands: `src/renderer/core/superdoc-fork/extensions/table/table.js`.

## Decisions (locked as we go)

*(none yet — every control below is **Decision: TBD**.)*

---

## Intro

Real Word's **Layout** tab has **7 groups** (Table · Draw · Rows & Columns · Merge · Cell Size ·
Alignment · Data). The clone's `layoutTab()` (`table-tools-pm.js:22-60`) renders **5 groups** (Rows &
Columns / Merge / Cell Size / Alignment / Data) and is missing the **Table** and **Draw** groups
entirely. The structural ops (insert/delete row+column, merge, split-table, distribute, autofit, cell
margins, cell shading) are real bridge verbs against the SuperDoc-fork table commands; the gaps are
mostly **dialogs** (Properties, Sort, Formula, Convert-to-Text, Split/Insert/Delete Cells) and a handful
of **genuinely missing verbs** (`tableSelect`, a standalone `tableSetHeaderRow`→`w:tblHeader`, `tableSort`,
a formula-field insert). One subsection below — **On-canvas table handles** — covers the move/resize grips
Word draws on a selected table, which are part of the Layout/selection flow but are not ribbon buttons.

Each control is analyzed as: **What real Word does · Current clone state · Verdict · Required structure ·
Decision**. Verdict legend: ✅ already-works · ✅ NO-FORK (buildable without a fork-source edit) · 🟡
additive-fork or large-interaction · 🔴 hard / needs design · ⛔ out of scope.

---

# Group 1 — Table

### Select (Cell / Column / Row / Select Table)

- **What real Word does:** a dropdown that sets the selection to the current cell, the whole column, the
  whole row, or the entire table (selection-only; no document mutation).
- **Current clone state:** **absent.** The whole Table group is missing from `layoutTab()`
  (`table-tools-pm.js:24-57` has no `tl-table` group). The bridge has a *test-only* CellSelection helper
  (`tableSelectFirstRowPair`, `table.ts:323-361`) built on the fork's `setCellSelection`
  (`table.js:1440`), but no user-facing select-cell/column/row/table verb.
- **Verdict:** ✅ NO-FORK — **needs a new verb.**
- **Required structure:** new `WC.PM.tableSelect('cell'|'column'|'row'|'table')` that builds a
  `CellSelection` (column/row/table) or `TextSelection` (cell) over the target, reusing the fork's
  `setCellSelection` command (`table.js:1440`). Selection-only — no OOXML. New `tl-table` group + a
  Select dropdown in `layoutTab()`.
- **Decision: TBD.**

### View Gridlines (toggle)

- **What real Word does:** toggles the non-printing table gridline overlay (a UI affordance for borderless
  tables). No OOXML — purely a view setting.
- **Current clone state:** **absent.** No gridline toggle anywhere in `table-tools-pm.js`.
- **Verdict:** ✅ NO-FORK — **no verb** (pure UI).
- **Required structure:** a CSS class on the painted table (e.g. `.wc-show-gridlines`) toggled by a ribbon
  button. No bridge verb, no OOXML. Lowest-effort control on the tab.
- **Decision: TBD.**

### Properties (Table Properties dialog — Table / Row / Column / Cell / Alt-Text tabs)

- **What real Word does:** opens the 5-tab Table Properties dialog: Table (alignment, indent, text-wrap,
  borders/shading), Row (height, repeat-as-header, allow-break), Column (preferred width), Cell (preferred
  width, vertical alignment, cell margins), Alt-Text (title/description).
- **Current clone state:** **absent.** No Properties button, no dialog. The constituent writes mostly
  already exist as bridge verbs: `tableSetAlignment` (`table.ts:146-150`), `tableSetIndent`
  (`table.ts:152-156`), `tableSetRowHeight` (`table.ts:164-168`), `tableSetCellWidth`
  (`table.ts:158-162`), `tableSetCellVAlign` (`table.ts:117-121`), `tableSetCellMargins`
  (`table.ts:170-174`) with a prefill reader `tableGetCellMargins` (`table.ts:180-201`). Alt-text exists
  only for images (`H.imgAltText`, `commands.js:254-275`), not for tables.
- **Verdict:** 🟡 NO-FORK — **needs a new (large) dialog** + a couple of new attr writes.
- **Required structure:** a tabbed Table Properties dialog that aggregates the existing verbs above. New
  writes needed for full parity: row **Repeat-as-header** (`w:tblHeader` — see Data ▸ Repeat Header Rows),
  row **Allow break across pages** (`w:cantSplit`), and a table-level **alt-text** write. Medium-large —
  mostly wiring existing verbs into one dialog.
- **Decision: TBD.**

---

# Group 2 — Draw

### Draw Table (freehand pen)

- **What real Word does:** a pen cursor; dragging draws the table outline and internal row/column dividers
  freehand (each stroke writes a `w:gridCol`/row split or a `w:tcBorders` segment).
- **Current clone state:** **absent on this tab.** The clone only has the Insert-menu uniform-grid
  drag-builder (the `insertTable` path, `table.ts:34-40`); there is no pen/divider interaction and no Draw
  group in `layoutTab()`.
- **Verdict:** 🟡 large interaction — **SPIKE-FIRST / NEEDS-USER** for the true pen.
- **Required structure:** surfacing a "Draw Table" button is trivial; real freehand divider/merge editing
  (mapping strokes to `w:gridSpan`/`w:vMerge`/`w:tcBorders`) is a sizable interaction subsystem. Defer the
  pen; a button could route to the existing insert builder as a stop-gap.
- **Decision: TBD.**

### Eraser

- **What real Word does:** an eraser cursor; clicking an internal border removes that divider, merging the
  two adjacent cells (`w:gridSpan`/`w:vMerge`).
- **Current clone state:** **absent.** No eraser. The underlying merge verb exists (`tableMerge`,
  `table.ts:79-87`), but there is no edge-hit-test interaction to drive it from a border click.
- **Verdict:** 🟡 NO-FORK in principle — **needs an interaction layer.**
- **Required structure:** an edge-hit-test on the painted table → select the two adjacent cells → call the
  existing `mergeCells` path (`table.ts:84`). Verb exists; the click-on-border interaction is the work.
  Pairs naturally with the Draw spike.
- **Decision: TBD.**

---

# Group 3 — Rows & Columns

### Delete (Delete Cells / Columns / Rows / Table)

- **What real Word does:** a dropdown: Delete Cells… (opens a shift dialog), Delete Columns, Delete Rows,
  Delete Table.
- **Current clone state:** **3 of 4 present, flat (no dropdown).** `tblDeleteRow`/`tblDeleteColumn`/
  `tblDeleteTable` (`table-tools-pm.js:30-32`) → `H.tblDelete*` (`commands.js:118-120`) →
  `tableDeleteRow`/`tableDeleteColumn`/`tableDeleteTable` (`table.ts:61-77`). **No Delete-Cells dialog**
  (shift-left/shift-up).
- **Verdict:** ✅ NO-FORK (the 3 real deletes work; the dropdown + Delete-Cells dialog are additive).
- **Required structure:** group the 3 existing deletes into a Word-style dropdown; add a Delete Cells…
  dialog with shift-left/shift-up semantics (a new shift-aware delete variant).
- **Decision: TBD.**

### Insert Above

- **What real Word does:** inserts a row above the current row.
- **Current clone state:** ✅ `tblInsertAbove` (`table-tools-pm.js:26`) → `H.tblInsertAbove`
  (`commands.js:114`) → `tableAddRow('above')` → `addRowBefore()` (`table.ts:42-49`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Insert Below

- **What real Word does:** inserts a row below the current row.
- **Current clone state:** ✅ `tblInsertBelow` (`table-tools-pm.js:27`) → `H.tblInsertBelow`
  (`commands.js:115`) → `tableAddRow('below')` → `addRowAfter()` (`table.ts:42-49`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Insert Left

- **What real Word does:** inserts a column to the left of the current column.
- **Current clone state:** ✅ `tblInsertLeft` (`table-tools-pm.js:28`) → `H.tblInsertLeft`
  (`commands.js:116`) → `tableAddColumn('left')` → `addColumnBefore()` (`table.ts:51-59`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Insert Right

- **What real Word does:** inserts a column to the right of the current column.
- **Current clone state:** ✅ `tblInsertRight` (`table-tools-pm.js:29`) → `H.tblInsertRight`
  (`commands.js:117`) → `tableAddColumn('right')` → `addColumnAfter()` (`table.ts:51-59`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Insert Cells (group dialog-launcher → Insert Cells dialog)

- **What real Word does:** the group's dialog-launcher arrow opens the Insert Cells dialog (shift cells
  right / shift cells down / insert entire row / insert entire column).
- **Current clone state:** **absent.** No dialog launcher on `tl-rowscols`; the 4 inserts above cover only
  whole-row/whole-column, not the shift-cells modes.
- **Verdict:** ✅ NO-FORK — **needs a dialog** (+ optional shift-aware insert variant).
- **Required structure:** an Insert Cells dialog; "entire row/column" reuse the existing add verbs, the
  shift-right/shift-down modes need a new shift-aware `w:tc` insert. Low priority.
- **Decision: TBD.**

---

# Group 4 — Merge

### Merge Cells

- **What real Word does:** merges the selected cells into one (`w:gridSpan`/`w:vMerge`).
- **Current clone state:** ✅ `tblMerge` (`table-tools-pm.js:35`) → `H.tblMerge` (`commands.js:121`) →
  `tableMerge` (`table.ts:79-87`). Gated on a `CellSelection` via `requireCellSel` (`table.ts:28-32,83`),
  toasts "Select cells first" on a plain caret. Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Split Cells (dialog)

- **What real Word does:** opens a dialog (number of columns, number of rows, "merge cells before split")
  and splits the selected cell(s) accordingly.
- **Current clone state:** ✅ **1-shot only, no dialog.** `tblSplitCell` (`table-tools-pm.js:36`) →
  `H.tblSplitCell` (`commands.js:122`) → `tableSplitCell` → `splitCell()` (`table.ts:89-93`). The fork's
  `splitCell()` takes **no rows/cols params** (`table.js:1196-1204`) — it splits a merged cell back, else
  falls to `splitSingleCell` (one cell → two horizontally, `table.js:1219`).
- **Verdict:** ✅ NO-FORK — **needs a dialog** (and an N-way split loop or param).
- **Required structure:** a Split Cells dialog feeding cols/rows; since `splitCell()` is param-less, an
  N×M split needs either a bridge-side loop over `splitSingleCell`/row-add or a small fork param.
- **Decision: TBD.**

### Split Table

- **What real Word does:** splits the table into two tables at the current row (a paragraph between them).
- **Current clone state:** ✅ `tblSplitTable` (`table-tools-pm.js:37`) → `H.tblSplitTable`
  (`commands.js:123`) → `tableSplit` → `splitTableAtRow()` (`table.ts:221-225`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

---

# Group 5 — Cell Size

### AutoFit (Contents / Window / Fixed Column Width)

- **What real Word does:** a dropdown — AutoFit Contents (columns shrink to text), AutoFit Window (table
  fills the text column), Fixed Column Width (locks current widths).
- **Current clone state:** ✅ `tblAutoFit` (`table-tools-pm.js:44`, dropdown) → `H.tblAutoFit`
  (`commands.js:213-217`) → `tableAutoFit(mode)` (`table.ts:302-316`), with real per-column content
  measurement (`measureColumnContentWidths`, `table.ts:259-300`) and a page-text-width cap
  (`pageTextWidthPx`, `table.ts:246-252`). All 3 modes real.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Height (spinner)

- **What real Word does:** a spinner setting the selected row height (`w:trHeight`).
- **Current clone state:** ✅ exposed as a **dropdown/flyout, not a spinner.** `tblRowHeight`
  (`table-tools-pm.js:40`) → `H.tblRowHeight` (`commands.js:237-238`, inches `sizeFly`) →
  `tableSetRowHeight(px,'atLeast')` → `setRowHeight()` (`table.ts:164-168`). Real verb; UI is a preset
  flyout rather than a live spinner.
- **Verdict:** ✅ already-works (verb real; spinner-vs-flyout is a UI-parity nicety).
- **Required structure:** optional — swap the flyout for a true increment spinner.
- **Decision: TBD.**

### Width (spinner)

- **What real Word does:** a spinner setting the selected column width (`w:tcW`/`w:gridCol`).
- **Current clone state:** ✅ as a **flyout, not a spinner.** `tblColWidth` (`table-tools-pm.js:41`) →
  `H.tblColWidth` (`commands.js:239-240`) → `tableSetCellWidth(px)` → `setCellWidth()` (`table.ts:158-162`,
  writes per-cell `colwidth`, `table.js:1753`). Real verb.
- **Verdict:** ✅ already-works (verb real; spinner-vs-flyout is UI parity).
- **Required structure:** optional spinner.
- **Decision: TBD.**

### Distribute Rows

- **What real Word does:** equalizes the heights of the selected rows.
- **Current clone state:** ✅ `tblDistRows` (`table-tools-pm.js:42`) → `H.tblDistRows`
  (`commands.js:124`) → `tableDistributeRows` → `distributeRowsEvenly()` (`table.ts:215-219`). Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

### Distribute Columns

- **What real Word does:** equalizes the widths of the selected columns.
- **Current clone state:** ✅ `tblDistCols` (`table-tools-pm.js:43`) → `H.tblDistCols`
  (`commands.js:125`) → `tableDistributeColumns` → `distributeColumnsEvenly()` (`table.ts:209-213`).
  Real verb.
- **Verdict:** ✅ already-works.
- **Required structure:** none.
- **Decision: TBD.**

---

# Group 6 — Alignment

### The 9-button cell-alignment grid (top/middle/bottom × left/center/right)

- **What real Word does:** 9 buttons setting both the cell's **vertical** alignment (`w:vAlign`) and the
  content paragraph's **horizontal** justification (`w:jc`) in one click.
- **Current clone state:** ⚠️ **only the 3 vertical buttons.** `tblVAlignTop/Mid/Bottom`
  (`table-tools-pm.js:47-49`) → `H.tblVAlign*` (`commands.js:129-131`) → `tableSetCellVAlign` →
  `setCellAttr('verticalAlign',…)` (`table.ts:117-121`). No horizontal axis on these buttons (no 9-grid).
- **Verdict:** ✅ NO-FORK — **UI work only.**
- **Required structure:** a 9-button grid combining the existing `setCellAttr('verticalAlign',…)`
  (`table.ts:118`) with the cell paragraph's `w:jc` — paragraph-justification verbs already exist in the
  bridge. No new fork command.
- **Decision: TBD.**

### Text Direction

- **What real Word does:** cycles the cell text direction (horizontal → rotate all 90° → rotate all 270°).
- **Current clone state:** ⚠️ **single fixed value, no cycle.** `tblTextDir` (`table-tools-pm.js:50`) →
  `H.tblTextDir` (`commands.js:132`) → `tableSetTextDirection('tbRl')` (`table.ts:239-243`). Hard-coded
  `'tbRl'`. The fork's `setTextDirection(dir)` already accepts `'btLr'`/`'tbRl'`/null
  (`table.js:2138-2143`).
- **Verdict:** ✅ NO-FORK — **UI work only.**
- **Required structure:** make `H.tblTextDir` cycle through the values instead of hard-coding `'tbRl'`;
  the verb is already parameterized. No new command.
- **Decision: TBD.**

### Cell Margins (dialog)

- **What real Word does:** opens the Cell Options / Table Options dialog (default cell margins, cell
  spacing, fit-text, wrap).
- **Current clone state:** ✅ **inches flyout (4 sides), not the full dialog.** `tblCellMargins`
  (`table-tools-pm.js:51`) → `H.tblCellMargins` (`commands.js:141-178`) → `tableSetCellMargins`
  (`table.ts:170-174`), prefilled from `tableGetCellMargins` (`table.ts:180-201`). Real verb; the flyout
  covers the 4 margins but not cell spacing / fit-text.
- **Verdict:** ✅ already-works (margins); fuller Cell Options dialog optional.
- **Required structure:** optional — expand the flyout to a full Cell/Table Options dialog (cell spacing,
  fit-text).
- **Decision: TBD.**

---

# Group 7 — Data

### Sort (dialog)

- **What real Word does:** opens the Sort dialog (up to 3 keys; per-key Type = Text/Number/Date;
  ascending/descending; header-row toggle) and reorders the table's `w:tr` rows.
- **Current clone state:** **absent.** No Sort button, no dialog, no sort verb. (Note: a Home-tab sort
  exists for paragraphs, but nothing reorders table rows.)
- **Verdict:** ⚠️ NO-FORK — **needs a new verb + dialog.**
- **Required structure:** a new `WC.PM.tableSort({col,type,order})` fork command that reorders `w:tr`
  nodes by a column's text/number/date key, plus the Sort dialog. Medium.
- **Decision: TBD.**

### Repeat Header Rows (`w:tblHeader`)

- **What real Word does:** toggles `w:trPr/w:tblHeader` on the selected row(s) so they repeat at the top of
  each page when the table breaks — **without** changing the row's cell types.
- **Current clone state:** ⚠️ **the wrong toggle is surfaced.** `tblHeaderRow` (`table-tools-pm.js:55`,
  labelled "Header Row") → `H.tblHeaderRow` (`commands.js:126`) → `tableToggleHeaderRow` →
  `toggleHeaderRow()` (`table.ts:95-99`), which flips the **structural** header (cell types **and** the
  repeat flag together, `toggleHeaderRow.js:13,31`). The standalone `setRepeatHeader` helper that sets only
  `tableRowProperties.repeatHeader` (= `w:tblHeader`) **exists** (`toggleHeaderRow.js:180-194`) but is
  **only called inside `toggleHeaderRow`** — no command exposes it on its own. (Also: a clone-invented
  "Header Column" button `tblHeaderCol`, `table-tools-pm.js:56` → `table.ts:101-105`, has **no Word
  equivalent** on this tab.)
- **Verdict:** ⚠️ NO-FORK — **needs a new verb** (distinct from the structural toggle).
- **Required structure:** new `WC.PM.tableSetHeaderRow(bool)` exposing a fork command that calls the
  existing `setRepeatHeader` helper (`toggleHeaderRow.js:182`) on the selected row(s) **without** touching
  cell types — i.e. a thin standalone command around an already-written helper. Decide whether to keep,
  relabel, or retire the existing "Header Row"/"Header Column" buttons.
- **Decision: TBD.**

### Convert to Text (delimiter dialog)

- **What real Word does:** opens a dialog (separate text with: Paragraph marks / Tabs / Commas / Other) and
  converts the table to text using the chosen delimiter.
- **Current clone state:** ✅ **delimiter hard-coded to tab.** `tblToText` (`table-tools-pm.js:54`) →
  `H.tblToText` (`commands.js:128`) → `tableToText('\t')` → `convertTableToText('\t')`
  (`table.ts:227-231`). The fork's `convertTableToText(d)` is parameterized (`table.js:2020`), but the
  handler passes only a tab.
- **Verdict:** ✅ NO-FORK — **needs a dialog.**
- **Required structure:** a Convert-to-Text dialog (Paragraph/Tab/Comma/Other) passing the chosen
  separator to the already-parameterized `tableToText(delimiter)`. No new verb.
- **Decision: TBD.**

### Formula (`w:fldSimple` dialog)

- **What real Word does:** opens the Formula dialog (formula box e.g. `=SUM(ABOVE)`, number format,
  paste-function) and inserts a `w:fldSimple w:instr="=…"` field into the caret cell, evaluating the result.
- **Current clone state:** **absent.** No Formula button, no dialog, no formula-field insert verb.
- **Verdict:** 🟡 NO-FORK — **needs a new verb + dialog.**
- **Required structure:** a new verb inserting a `w:fldSimple w:instr="=…"` field into the caret cell (the
  fork already has field machinery for other field types — TOC/PAGE etc.), plus the Formula dialog (formula
  box, number-format picker, paste-function). Computing the live value is the heavier part. Medium.
- **Decision: TBD.**

---

# On-canvas table handles (selection-flow, not ribbon buttons)

When a table is selected, real Word draws **two grips** on the table itself. They are part of the Table
Layout / selection experience but are **not** ribbon controls — documenting them here so the feasibility
picture is complete.

### Top-left move handle (the ⊞ box)

- **What real Word does:** a small move box appears at the table's top-left corner; dragging it relocates
  the **entire table** to a new position (for a floating table this writes `tblpPr` positioning; for an
  inline table it moves the table to the drop point in the flow).
- **Current clone state:** **absent.** No move handle is rendered, and there is no whole-table-move
  interaction in `table-tools-pm.js` or the bridge. (The fork **does** have a `tblpPr` translator that
  round-trips floating-table positioning — `core/super-converter/v3/handlers/w/tblpPr/tblpPr-translator.js`
  — so the OOXML target exists, but nothing in the UI drives it.)
- **Verdict:** 🟡 — interaction work, **possibly additive-fork** for true floating placement.
- **Required structure:** render a move grip on the selected painted table + a drag interaction. Moving an
  **inline** table within the flow ≈ a PM transaction (cut/paste the table node) and is NO-FORK-ish;
  converting to a **floating** table at an arbitrary drop point needs the `tblpPr` write path wired up
  (the translator exists; the command/attr plumbing does not). Spike to confirm scope.
- **Decision: TBD.**

### Bottom-right proportional-resize handle (the ◢ grip)

- **What real Word does:** a resize grip at the table's bottom-right corner; dragging it resizes the
  **whole table** with **all columns and all rows scaling at the same ratio** — distinct from the clone's
  current per-column border-drag (which resizes one column at a time).
- **Current clone state:** **absent.** The painted table supports per-column resize via the
  prosemirror-tables column-resizing plugin (per-cell `colwidth`, `table.js:1753-1754`), but there is **no**
  bottom-right whole-table grip and no proportional-scale interaction.
- **Verdict:** ✅ NO-FORK — **interaction work only.**
- **Required structure:** render a bottom-right grip + a drag handler that multiplies **every** cell's
  `colwidth` (and row heights) by a single scale factor — the per-cell `colwidth` attr the resize plugin
  already uses (`table.js:948,1259,1297`) is exactly the write surface, so this is a UI/interaction layer
  over existing attrs (a loop over `setCellWidth`-style writes). No fork-source edit.
- **Decision: TBD.**

---

## Summary of new structure needed (cross-cut)

- **Genuinely missing verbs:** `tableSelect` (Select submenu), a standalone `tableSetHeaderRow`→`w:tblHeader`
  (the `setRepeatHeader` helper exists at `toggleHeaderRow.js:182` but isn't exposed), `tableSort` (reorder
  `w:tr`), a formula-field insert (`w:fldSimple`); optional shift-aware insert/delete-cells variants.
- **Already-real verbs (UI/dialog work only):** the 9-button alignment grid (`setCellAttr` + para `w:jc`),
  Text Direction cycle (`setTextDirection` already param'd), Convert-to-Text delimiter (`tableToText`
  already param'd), View Gridlines (pure UI), proportional whole-table resize (scale existing `colwidth`).
- **New dialogs:** Table Properties (5 tabs), Sort, Formula, Convert to Text, Split Cells, Insert/Delete
  Cells.

## Decision

**TBD — to be decided together, per control above.**

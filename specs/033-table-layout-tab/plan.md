# Implementation Plan: Table Layout Tab Completion

**Branch**: `parity-v2` · **Date**: 2026-07-02 · **Spec**: [spec.md](spec.md)

## Summary
Rebuild layoutTab() to Word's 7 groups and add the missing verbs/dialogs — almost entirely NO-FORK
(the whole build exists in the archive: rebuild `2369183`, Sort `61bf9e2`, Formula `d5eb977`,
Properties `ea7a5ba`, 9-way `1716101`). Two honest degrades: true shift-cells (never built, not
NO-FORK) and Eraser (no drag-erase path). Select is done NO-FORK (bridge TableMap math, avoiding the
archive's one fork edit).

## Constitution Check
- **I. No Fork Edits** — ✅ NONE. Select uses the NO-FORK bridge approach (replicate
  tableSelectFirstRowPair's TableMap math → setCellSelection). Shift-cells is honest-degraded to
  row/col (documented), NOT a fork edit. Everything else = existing verbs / new bridge verbs
  (updateAttributes / toggle-class).
- II ✅ (bridge verbs) · III ✅ · IV ✅ (fixture-verified) · V ✅ · VI ✅ · VII ✅.

## NO-FORK seam per control (research-locked)
- Select menu → NEW bridge `tableSelectScope(scope)` (TableMap corners → setCellSelection).
- View Gridlines → NEW bridge `tableViewGridlines()`/`tableGridlinesShown()` (toggle
  `.wc-show-table-gridlines` on #pm-editor + editor.css faint dashed; view-only, no export).
- Properties dialog → `D.tableProperties` wiring existing verbs (align/indent/rowHeight/repeatHeader/
  cellWidth/vAlign); Alt-Text = UI-only v1 (no persist verb — honest).
- Draw Table → reuse Insert.drawTableMode; Eraser → honest stub toast.
- Delete → `tblDelete` DROPDOWN (Delete Cells honest-degrade / Columns / Rows / Table over existing
  verbs). Insert Cells launcher → dialog that (v1) inserts a row/col with a documented note (true
  shift needs fork — out of scope).
- 9-way alignment → 9 handlers `tableSetCellAlign(v,h)` = setCellAttr('verticalAlign',v) +
  setTextAlign(h) (text-align extension exists); 'left' clears jc.
- Text Direction → cycle null→'tbRl'→'btLr'→null (fork accepts btLr/tbRl/null).
- Cell Margins → NEW bridge `tableSetTableCellMargins(m)` = updateAttributes('table',
  {'tableProperties.cellMargins': m}) → w:tblCellMar; repoint H.tblCellMargins to a Table Options dialog.
- Sort → NEW bridge `tableSort(levels, hasHeader)` + `tableColumns()` + `D.tableSort` (lift 61bf9e2).
- Repeat Header Rows → NEW bridge `tableRepeatHeaderRows(on)` = updateAttributes('tableRow',
  {'tableRowProperties.repeatHeader': on}) → w:tblHeader. Remove the wrong Header Row/Column from Layout.
- Formula → NEW bridge `tableFormula(f, fmt)` + `formulaContext()` + `D.tableFormula` (lift d5eb977;
  v1 inserts the computed VALUE).
- Convert to Text → `D.convertToText` separator dialog → existing tableToText(delim).
- Height:/Width: → relabel + keep dropdown (stepper is polish; label parity is the gap).

## Build order (single agent, lift from the archive)
1. layoutTab() 7-group rebuild (remove Header Row/Column). 2. tblDelete dropdown + Height/Width
relabel. 3. 9-way align + text-dir cycle + convert-text dialog. 4. view-gridlines + repeat-header
bridge verbs. 5. table-cell-margins bridge + Table Options dialog. 6. Sort/Formula/Properties dialogs
+ their bridge verbs. 7. Select bridge. 8. Draw reuse + Eraser stub. Then probes/twins + pm tests.

## Acceptance
Spec SC-001..005: STRUCTURE table-layout missing 16→≤3, label-differs 5→0, delete type-mismatch
resolved; tb-repeatheader/sort/cellalign/cellmargins/textdir semantic-pass; behavior journeys/twins;
gates green.

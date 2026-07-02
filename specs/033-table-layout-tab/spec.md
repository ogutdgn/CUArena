# Feature Specification: Table Layout Tab Completion

**Feature Branch**: `033-table-layout-tab` · **Created**: 2026-07-02 · **Status**: Draft

**Input**: FIX 4 of the ratified Tables fix loop — bring the Table Layout contextual tab to Word's
7 groups (§3/§4/§5/§6 gaps: Draw group, Delete menu, Insert Cells launcher, 9-way alignment, Sort,
Formula, Repeat Header Rows semantics, label mismatches, Convert dialog, Cell Margins → Table
Options).

## User Scenarios & Testing

### US1 — Word's Layout groups + labels (P1)
The Table Layout tab presents Word's 7 groups with Word's labels: Table (Select menu / View
Gridlines / Properties), Rows & Columns (4 Insert + Delete MENU + Insert Cells launcher), Merge,
Cell Size (AutoFit / Height: / Width: / Distribute), Alignment (9-way grid + Text Direction + Cell
Margins), Data (Sort / Repeat Header Rows / Convert to Text / Formula), Draw (Draw Table / Eraser).

**Acceptance**: STRUCTURE table-layout — the 16 missing controls move matched (Select menu, View
Gridlines, Properties, Draw Table, Eraser, Insert Cells, the 6 extra alignment cells, Sort,
Formula, the Select/Alignment menus); the 5 label-differs fixed (Height:/Width:/Align Top Left/
Align Bottom Left/Repeat Header Rows); the Delete type-mismatch (menu vs flat buttons) resolved.

### US2 — Correct OOXML for the data verbs (P1)
Repeat Header Rows writes `w:tblHeader` (not `<th>` conversion); Sort reorders row content; 9-way
alignment writes `w:vAlign` + paragraph `w:jc`; Cell Margins writes table-level `w:tblCellMar`
(not per-cell `tcMar`); Text Direction cycles horizontal→tbRl→btLr.

**Acceptance**: tb-repeatheader → `w:tblHeader`; tb-sort-col1 reorders (textOrder matches);
tb-cellalign-bottomright → vAlign bottom + jc right; tb-cellmargins → tblCellMar; tb-textdir first
click → tbRl. Each reaches semantic-pass on its delta.

### US3 — The dialogs (P2)
Table Properties (tabbed), Insert Cells (shift), Delete Cells (shift), Sort (by-column + header),
Formula (=SUM), Convert to Text (separator), Cell Margins → Table Options.

**Acceptance**: each opens from its Layout control; STRUCTURE/scorecard see them; the Sort/Formula/
Convert dialogs write the correct result.

### Edge cases
- Select column/row/table = selection-only (no doc change) — verify via selection state, not export.
- View Gridlines = app-state toggle (non-printing) — no OOXML.
- Draw Table / Eraser: reuse the Insert drawTableMode; Eraser = merge-by-erasing (honest stub if
  no clean geometry path — matches the archive).
- Insert/Delete Cells shift-direction: if no fork shift-cells command, the honest v1 = insert/
  delete a full row/column with a note (documented), or a new bridge verb if reachable.
- Formula v1 inserts the computed VALUE (not a live w:fldSimple field) — documented, matches archive.

## Requirements
- **FR-001**: layoutTab() = Word's 7 groups with Word's exact labels/idMso mapping.
- **FR-002**: Delete = a MENU (Delete Cells… / Delete Columns / Delete Rows / Delete Table).
- **FR-003**: Insert Cells launcher → a shift-direction dialog (right/down/row/column).
- **FR-004**: 9-way alignment grid — each cell writes vAlign + paragraph jc (reuse tableSetCellVAlign
  + a per-cell jc via the caret).
- **FR-005**: Repeat Header Rows writes `w:tblHeader` on the row trPr (not th-conversion).
- **FR-006**: Cell Margins writes table-level `w:tblCellMar` via the Table Options dialog.
- **FR-007**: Sort dialog reorders table rows by a column key (+ header toggle).
- **FR-008**: Formula dialog computes =SUM/AVERAGE/COUNT over ABOVE/LEFT and inserts the value.
- **FR-009**: Convert to Text dialog picks the separator (paragraph/tab/comma/other).
- **FR-010**: Text Direction cycles the 3 states (tbRl/btLr/horizontal).
- **FR-011**: Table group — Select menu, View Gridlines toggle, Properties dialog.
- **FR-012**: Draw group — Draw Table (reuse) + Eraser.
- **FR-013**: Height:/Width: labels + stepper-style controls.

## Success Criteria
- **SC-001**: STRUCTURE table-layout missing 16→≤3 (honest stubs for Draw/Eraser/Table-Properties
  alt-text allowed); label-differs 5→0; the Delete type-mismatch resolved.
- **SC-002**: tb-repeatheader / tb-sort-col1 / tb-cellalign-bottomright / tb-cellmargins / tb-textdir
  reach semantic-pass on their deltas (F-class base excepted → FIX 5).
- **SC-003**: BEHAVIOR — the merge-split (Split Cells dialog) + delete-menu journeys PASS; new
  generated twins for the reachable data verbs pass.
- **SC-004**: SCORECARD — the new Layout controls/menu items click alive (no dead/silent).
- **SC-005**: 3 gates + bundle green.

## Assumptions
- Draw Table reuses the Insert drawTableMode; Eraser + Table Properties Alt-Text may be honest
  stubs if no NO-FORK path (documented, matches the archive).
- Insert/Delete Cells shift = a new bridge verb if reachable; else the honest row/col reduction.
- Formula v1 = computed value, not a live field (fldSimple deferred).
- The clone-only Design Alignment group (from earlier) is out of scope here (Layout tab only).

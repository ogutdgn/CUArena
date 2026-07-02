# Implementation Plan: Insert Table Wiring + Insert-Time OOXML Defaults

**Branch**: `parity-v2` · **Date**: 2026-07-02 · **Spec**: [spec.md](spec.md)

## Summary
A bridge post-process on insertTable writes Word's exact defaults (uneven gridCol/tcW, tblW auto,
tblLook val); one data-only fork edit adds the TableGrid style pPr; the Insert button opens the
dropdown with grid-hover live preview + post-insert Table Design activation; the Insert Table dialog
gains AutoFit radios. 7 of 8 NO-FORK.

## Constitution Check
- **I. No Fork Edits** — ⚠️ ONE data-only edit: DEFAULT_LINKED_STYLES['TableGrid'] gains
  `<w:pPr><w:spacing after=0 line=240 lineRule=auto/></w:pPr>` after w:rsid / before w:tblPr (same
  FIX-1 class; unreachable by bridge — it's a hardcoded fallback def). Marked. Everything else
  bridge/public-JS.
- II ✅ · III ✅ · IV ✅ (fixture-verified distribution) · V ✅ · VI ✅ · VII ✅.

## Technical Context (research-locked)
- **Distribution** (any N, any page): `total = round((pageW − Lm − Rm) in twips) − 10`;
  `base = floor(total/N)`; `rem = total − base·N`; widths[i] = i < N−rem ? base : base+1 (remainder
  to LAST cols). Verified 9350/3 → 3116/3117/3117.
- **Bridge post-process on insertTable** (setNodeMarkup, like tableSetCellBorders):
  - table `grid` attr = `[{col: twips}, …]` (tblGrid decode reads grid[i].col twips first) → exact gridCol.
  - `tableProperties.tableWidth = {value:0, type:'auto'}` → `<w:tblW w:w="0" w:type="auto"/>`.
  - per-cell `tableCellProperties.cellWidth = {value: twips, type:'dxa'}` + clear colwidth (else the
    px→twips recompute is lossy: 3117→3118) → exact tcW.
  - `tableProperties.tblLook.val` via restampTableConditionalFormats(editor) (the FIX-2 val writer) →
    `w:val="04A0"`.
- **Insert wiring**: `H.table = (c,node) => WC.Insert.tableMenu(node)` (commands.js:109; the dropdown
  dispatch at :2080 is bypassed because Commands.run checks H[cmd] first — so change H.table itself).
- **Grid-hover preview**: new bridge `insertTablePreviewEnter(rows,cols)/Leave` = addToHistory:false
  snapshot/insert/restore (table-styles.ts pattern); wire the picker mouseenter/mouseleave.
- **Activate Table Design**: after a grid insert, WC.Ribbon.activate('table-design') (showContextualTab
  already honors activate; keep caret-entry passive).
- **AutoFit radios**: lift archive 87e63d5 into D.insertTable (Fixed/Contents/Window → tableAutoFit).

## Build order
1. TableGrid pPr fork-data edit (+ pm test). 2. insertTable bridge post-process (gridCol/tblW/tcW/
tblLook val) + pm test. 3. H.table → dropdown. 4. insertTablePreviewEnter/Leave + picker wiring +
post-insert activate. 5. D.insertTable AutoFit radios. 6. Probes/twins: the `table` task + the insert
journeys; regenerate. 7. Measure: run.py --only table + a sample of tb-* (the F-class delta should
drop everywhere); insert journeys; gates.

## Acceptance
Spec SC-001..004: F-class delta clean on `table` + removed from tb-* residuals; insert-grid journey
grid-hover + activeTabIs pass; AutoFit radios present; gates green.

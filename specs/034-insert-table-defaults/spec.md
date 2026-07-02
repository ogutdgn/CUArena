# Feature Specification: Insert Table Wiring + Insert-Time OOXML Defaults

**Feature Branch**: `034-insert-table-defaults` · **Created**: 2026-07-02 · **Status**: Draft

**Input**: FIX 5 of the ratified Tables fix loop — the Insert>Table button/menu wiring (dropdown,
grid-hover live preview, post-insert Table Design activation, AutoFit radios) AND the insert-time
OOXML defaults (tblLook val, tblW auto, Word's uneven gridCol widths, TableGrid style pPr spacing)
— the F-class base delta present in EVERY Tables OOXML task.

## User Scenarios & Testing

### US1 — A fresh table carries Word's exact hidden defaults (P1)
Inserting any table writes what real Word writes unasked: `<w:tblW w:w="0" w:type="auto"/>`, the
`w:tblLook` val bitmask, Word's UNEVEN per-column gridCol/tcW widths (3116/3117/3117 for a default
3-col table, not uniform 3120), and the TableGrid style def carries the pPr spacing block.

**Why this priority**: This F-class delta appears in EVERY table task's `missing`/`extra` — closing
it lifts the per-task `missing` counts across ALL Tables OOXML tasks at once (the single
highest-leverage fidelity fix left).

**Acceptance**: `run.py --only table` (plain insert) → the tblGrid/tblW/tblLook/TableGrid-pPr delta
is clean; the ~8-node F-class `missing` + the 3120-vs-3116/3117 `extra` disappear from every
tb-* task.

### US2 — The Insert button opens Word's dropdown with live preview (P1)
Clicking the ribbon Table button opens the dropdown (grid picker + Insert Table…/Draw Table/Convert/
Quick Tables), NOT the dialog directly. Hovering the grid live-previews the pending table in the
document (recorded Word behavior). Picking a grid inserts and activates Table Design.

**Acceptance**: H.table opens the dropdown; grid hover paints a preview table (the insert-grid
journey's paintedCellCount-6-on-hover passes); post-insert the active tab is Table Design (the
recorded activeTabIs bar passes).

### US3 — Insert Table dialog AutoFit (P2)
The Insert Table dialog offers AutoFit behavior (Fixed column width / AutoFit to contents / AutoFit
to window) + Remember dimensions.

**Acceptance**: the dialog has the AutoFit radios wired to the autofit modes; STRUCTURE/dialog axis
sees them.

### Edge cases
- Uneven distribution generalizes to any column count + page width (floor + remainder to later
  columns; total = Word's default table width for the current section).
- Grid-hover preview must not pollute undo/the saved file (addToHistory:false; revert on leave/pick).
- A styled insert (Quick Table / gallery) still carries the defaults + its style.

## Requirements
- **FR-001**: insertTable writes `<w:tblW w:w="0" w:type="auto"/>`.
- **FR-002**: insertTable emits Word's `w:tblLook` val bitmask (via the FIX-2 writer on the insert path).
- **FR-003**: gridCol/tcW widths = Word's uneven distribution (floor(total/N), remainder to later
  columns; total = the section's default table width) — not uniform.
- **FR-004**: the TableGrid style def carries `<w:pPr><w:spacing w:after="0" w:line="240"
  w:lineRule="auto"/></w:pPr>` (the one data-only fork edit, FIX-1 class).
- **FR-005**: the ribbon Table button opens the dropdown (WC.Insert.tableMenu), not the dialog.
- **FR-006**: grid-hover live-previews the pending table in the document (paint-only, no undo/file).
- **FR-007**: a fresh grid insert activates Table Design.
- **FR-008**: the Insert Table dialog has AutoFit radios (Fixed/Contents/Window) + Remember dimensions.

## Success Criteria
- **SC-001**: the F-class base delta (tblW/tblLook-val/gridCol/tcW/TableGrid-pPr) is clean on the
  `table` task AND removed from every tb-* task's residual `missing`/`extra` (the per-task counts
  drop by the shared ~8-node cluster).
- **SC-002**: BEHAVIOR insert-grid + insert-dropdown journeys — the grid-hover paintedCellCount-6
  bar + the activeTabIs Table Design bar pass (the 2 long-standing insert journey fails).
- **SC-003**: STRUCTURE/dialog — the Insert Table dialog AutoFit radios present.
- **SC-004**: 3 gates + bundle green.

## Assumptions
- The uneven-distribution total matches Word's default for US Letter 1in margins (9350 for a
  full-width table); derived from the section page/margins so it generalizes.
- Grid-hover preview uses the proven addToHistory:false snapshot/restore pattern (style-preview.ts).
- Remember dimensions is a session preference (v1 may be a no-op checkbox if no persist path).

# Feature Specification: Table Borders Engine

**Feature Branch**: `032-table-borders` · **Created**: 2026-07-02 · **Status**: Draft

**Input**: FIX 3 of the ratified Tables fix loop — the Table Design Borders group (§3/§6 gaps),
per-edge OOXML fidelity, and the border-collapse paint bug (the file-clean-screen-wrong class).

## User Scenarios & Testing

### US1 — Full Borders dropdown (P1)
The Borders dropdown offers Word's full set — Bottom/Top/Left/Right, No Border, All, Outside,
Inside, Inside-Horizontal, Inside-Vertical, Diagonal Down, Diagonal Up, Borders and Shading… —
each writing the correct per-side `w:tcBorders` in CT_TcBorders schema order, diagonals included.

**Acceptance**: applying a single edge writes only that side (merged onto existing); No Border
writes explicit per-side `w:val="nil"` (not an empty override that leaves the style border);
diagonals write `w:tl2br`/`w:tr2bl`; tb-border-top-cell/weight/color/diagdown tasks reach
semantic-pass on the border delta.

### US2 — Border pen + Border Painter (P1)
Border Styles / Line Style / Line Weight / Pen Color set a shared active pen; the Borders
dropdown draws with it; Border Painter is a real mode — clicking a rendered cell edge paints
that one side with the active pen.

**Acceptance**: pen weight 3pt → drawn border `w:sz="24"`; pen color red → `w:color="FF0000"`;
Border Painter click on the middle cell's bottom edge → that cell's bottom border painted.

### US3 — Border-collapse paint (P1, the instrument bug)
Applying All Borders to one cell paints ALL FOUR of its edges on screen — the shared bottom/right
edges are no longer swallowed by a thinner neighbor (thicker-wins, ECMA §17.4.66 / the LO rule
note).

**Acceptance**: the tb-borders-all-cell twin's four `paintedCellBorder` checks (middle cell,
top/left/bottom/right ≥1px) all pass; the No-Border twin's painted line vanishes.

### US4 — Borders and Shading dialog, cell scope (P2)
The launcher opens the existing Borders and Shading dialog extended with Apply-to: Cell (+ a Grid
setting); OK routes to the cell border writer.

**Acceptance**: the dialog opens from Table Design; Setting=All + a chosen Style/Color/Width writes
the cell's borders; STRUCTURE BordersShadingDialogWord moves missing→matched.

### Edge cases
- No Border defeats the STYLE border but NOT the table-level border (LO note B6) — v1 writes cell
  nil sides; table-border interaction arbitrated by the differ if a task surfaces it.
- Border-collapse pre-pass guards to simple unmerged uniform grids (bails on span>1 / ragged) —
  merged-cell edges are a documented v1 limit (matches the archive).
- Diagonal on a merged cell (tb-combo-diag-merged): merge works, diagonal writes tl2br on the
  merged cell.

## Requirements
- **FR-001**: Borders dropdown = the ~14 Word items; per-edge = merge onto current cell borders
  (add a `tableGetCellBorders()` bridge getter; merge chrome-side).
- **FR-002**: No Border writes explicit per-side `w:val="nil"` (val:'none', size:0, color:'auto').
- **FR-003**: Export emits `w:tcBorders` children in CT_TcBorders order
  (top,start,left,bottom,end,right,insideH,insideV,tl2br,tr2bl) and carries diagonals + inside
  sides (fix `legacyBorderMigration.js` SIDES + a translator xmlOrder).
- **FR-004**: A shared active pen (val/size/color[/themeColor]) set by Border Styles / Line Style /
  Line Weight / Pen Color; the Borders dropdown draws with it; default 1/2pt auto single.
- **FR-005**: Border Painter mode paints the clicked edge with the active pen (chrome edge
  hit-test → merged single-side write).
- **FR-006**: The paged renderer resolves shared cell edges thicker-wins (paint-only pre-pass;
  export untouched) so a single-cell border shows all four sides.
- **FR-007**: Borders and Shading dialog gains Apply-to: Cell (+ Grid setting) writing cell borders.
- **FR-008**: The new Borders group + pen controls appear on Table Design (Word labels: Border
  Styles, Line Style→Pen Style, Line Weight→Pen Weight, Pen Color, Borders, Border Painter).

## Success Criteria
- **SC-001**: tb-border-top-cell / weight-3pt / color-red / diagdown / borders-none tasks reach
  semantic-pass on the border delta (F-class base defaults excepted → FIX 5).
- **SC-002**: BEHAVIOR — tb-borders-all-cell + tb-borders-none twins PASS (the two long-standing
  fails); a Border-Painter twin passes.
- **SC-003**: STRUCTURE — Border Styles / Pen Style / Pen Weight / Pen Color / Border Painter /
  Borders and Shading… move missing→matched on table-design (6 of the 7 remaining).
- **SC-004**: VISUAL — a re-judged tabledesign ribbon pair no longer lists the absent Borders group.
- **SC-005**: 3 gates + bundle green.

## Assumptions
- Collapse pre-pass uses width-only thicker-wins (archive parity) for the uniform-single case; the
  LO full weight formula (style-rank × width) is a follow-up if a double/thick-vs-single task
  surfaces.
- Apply-to: Table (tblBorders) is v1-deferred to cell scope unless a task needs it.
- The two fork edits (SIDES order+diagonals; collapse pre-pass) are plan-authorized, marked with
  the fork-edit convention, matching archive loci (legacyBorderMigration / 47488c0).

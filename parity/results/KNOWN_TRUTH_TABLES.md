# KNOWN TRUTH — Tables (the Phase B answer key)

> Reconstructed 2026-07-02 from the `parity-pipeline` ARCHIVE branch (git-show only, no checkout),
> docs/plan history, docs/bug-hunt, and the current `parity-v2` tree, via a 7-reader parallel sweep.
> **Purpose: Phase B acceptance.** The pipeline must INDEPENDENTLY rediscover every named gap below
> (§1–§5) with zero false full-parity verdicts on hand spot-checks (§7). A miss = a PIPELINE bug.
> This file is the answer key — the pipeline run must NOT read it as input.
>
> Branch topology (verified): parity-v2 forks from main @ `19aa2e3` — BEFORE the entire archive
> Tables loop. NONE of the ~31 archive table commits is an ancestor of v2; the 10 kept OOXML fixes
> (specs 022-029) touch ZERO table code. So every archive Tables fix is absent in v2 by design.

## §1 — Style gallery: 2 / 247 [NAMED ACCEPTANCE GAP]

- **Clone (v2):** exactly **2** table styles on a blank doc — `TableGrid` + `GridTable4-Accent1`,
  minted by `addDefaultStylesIfMissing` from `DEFAULT_LINKED_STYLES` (exporter-docx-defs.js:93);
  `H.tblStyles` (commands.js:188-197) renders them as a PLAIN TEXT flyout — no thumbnails, no
  Plain/Grid/List sections, no Modify/Clear/New Table Style footer (archive's visual tile gallery
  `c498c6b` + footer `0ecbfd3` are NOT in v2).
- **Word:** **247** built-in table styles (113 modern: 49 Grid Table + 49 List Table + 5 Plain
  Table + 10 Table Grid*), ground truth `parity/oracle/table_style_catalog.json` @ `a3d3566`.
  ⚠️ catalog styleIds are SYNTHESIZED (`GridTable4Accent1`); real OOXML uses the DASH form
  (`GridTable4-Accent1`) — archive oracle-verified.
- **Never fixed on any branch** (COM bulk extraction hangs; archive iterations 4→12 BLOCKED).
- **Must be caught by:** SCORECARD (gallery item count 2), STRUCTURE (TableStylesGalleryWord
  present but content-poor — top-level matches, so the CATCH is scorecard/visual), VISUAL
  (side-by-side gallery), OOXML (applying a style the clone lacks → §6 task = full missing delta).

## §2 — cnfStyle stamping [NAMED ACCEPTANCE GAP]

- **Word:** applying `Grid Table 4 - Accent 1` writes `w:tblStyle` + **11 per-row/per-cell
  `<w:cnfStyle>`** role markers (firstRow `100000000000`, firstColumn `001000000000`…) and ZERO
  direct `w:shd`; Table Style Options toggles flip `w:tblLook` bits AND re-stamp cnfStyle.
- **Clone (v2):** cnfStyle is **never authored on ANY branch** (import round-trip preserves it —
  translator registered on tcPr+trPr — but nothing creates/updates it). `w:tblLook` is written
  with the 6 flag attrs but the **`w:val="04A0"` bitmask is MISSING** (archive fix `f828dcc` not
  cherry-picked). The **Table Style Options group (6 checkboxes) does not exist** in v2's Design
  tab; Layout>Data's "Header Row"/"Header Column" buttons do `<th>` conversion
  (toggleHeaderRow/Column) — they touch NEITHER tblLook NOR cnfStyle NOR w:tblHeader.
- **Must be caught by:** OOXML (style-apply task → missing cnfStyle nodes; insert task → missing
  tblLook val), STRUCTURE (6 checkboxes missing on table-design), SCORECARD, STATE.

## §3 — Draw Table / Eraser / Border Painter [NAMED ACCEPTANCE GAP]

- **v2 state is WORSE than the archive's honest stubs: the controls DO NOT EXIST.** No Draw group
  on Layout, no Borders(pen) group on Design (archive's tblDrawTable/tblEraser toasts +
  REAL pen samplers Border Styles/Pen Style/Pen Weight/Pen Color from `5bf5aed` all absent).
- **Three distinct "Draw Table"s — do not conflate:** (1) Insert>Table menu item → REAL-but-shallow
  drag-rectangle uniform-grid builder (insert-features.js; NOT a stub — but its instructional toast
  makes the current deep scorecard misclassify it STUB_TOAST — a known classifier pitfall);
  (2) Home>Borders menu item → `WC.notImplemented` stub (both branches); (3) Table Layout ribbon
  toggle → archive-only honest stub, ABSENT in v2.
- **Must be caught by:** STRUCTURE (missing idMso: TableDrawTable, TableEraser, pen group on both
  contextual tabs), SCORECARD (deep: Home>Borders Draw Table stub).

## §4 — Insert Cells… launcher [NAMED ACCEPTANCE GAP]

- **Never implemented on ANY branch** (even the archive's Word-parity Layout rebuild `a31fd01`
  omitted it — stayed on the archive's official MISSING list).
- **Word:** idMso `TableInsertCellsDialog`, dialogBoxLauncher of GroupTableRowsAndColumns, label
  "Insert Cells...", 4 radios (shift right / shift down / entire row / entire column);
  enabledBlankDoc=false → STATE ctx3(in-table)-enabled.
- **v2:** `tl-rowscols` group = 7 flat buttons, no `launcher` key; no Insert Cells dialog in
  dialogs.js. Sibling gap: **Delete Cells…** (`CellsDelete`) also never implemented (v2 has 3 flat
  delete buttons, not Word's Delete menu).
- **Must be caught by:** STRUCTURE (missing launcher + missing Delete-menu items), DIALOG (no
  clone dialog to inventory), STATE (ctx3 enabled-mismatch), OOXML (shift-cells task → no-op gap).

## §5 — Label mismatches [NAMED ACCEPTANCE GAP]

**The v2-current set (what the pilot must rediscover) — 5 on table-layout** (fresh v2 STRUCTURE
baseline already flags them; the pilot re-run must reproduce):
| clone cmd | clone label | Word (GetLabelMso) |
|---|---|---|
| tblRowHeight | Row Height | **Height:** (TableRowHeight) |
| tblColWidth | Column Width | **Width:** (TableColumnWidth) |
| tblVAlignTop | Align Top | **Align Top Left** (TableCellAlignTopLeft) |
| tblVAlignMid | Align Middle | **Align Center** (TableCellAlignCenter…) |
| tblVAlignBottom | Align Bottom | **Align Bottom Right** (TableCellAlignBottomRight) |

(The clone's 3 vAlign buttons stand where Word has the 9-way alignment grid — part label
mismatch, part missing-items.) The ARCHIVE-era 6 mismatches (Insert Row Above/Below + Insert
Column Left/Right wordings; Pen Style/Pen Weight) are GONE in v2 — the revert restored pre-loop
Word-correct insert labels, and the pen controls vanished entirely (→§3). Insert>Table menu item
labels match Word (fixed on main pre-fork, kept).
- **Must be caught by:** STRUCTURE label-differs bucket.

## §6 — All OTHER known Tables gaps (the anti-false-full catalog)

Any FULL-PARITY verdict touching a row below is a FALSE PASS → pipeline bug.

**OOXML / export fidelity (clone-authored tables):**
- Insert-time defaults missing (v2 re-measured @ `596c735` era, parity/results/table.json):
  `tblLook w:val=04A0`, `<w:tblW w:w=0 w:type=auto>`, TableGrid style `pPr/w:spacing
  (after=0 line=240)`, per-column `gridCol`/`tcW` widths (Word's uneven 3116/3117/3117 split).
- Cell shading exports `w:shd` with **fill only** — missing `w:val="clear" w:color="auto"`
  (archive fix `96d027e` absent).
- No theme provenance: shading has no `w:themeFill`, borders no `w:themeColor` (archive
  `67a1cad`/`44aaefa` absent); tableSetCellShading has no themeFill param.
- `legacyBorderMigration.js:17` emits tcBorders children **out of CT_TcBorders schema order**
  (top,right,bottom,left; insideH/insideV/tl2br/tr2bl dropped) — archive fix `39c61b4` absent.
- "No Border" clears the override to `{}` (style border stays visible) instead of Word's explicit
  per-side `val=nil` (archive `e96434e` absent).
- "Repeat header" semantics wrong: tblHeaderRow does `<th>` conversion, NOT `w:trPr/w:tblHeader`.
- Text Direction hardwired to `tbRl` only (Word cycles horizontal→tbRl→btLr).
- Convert to Text hardcodes TAB separator (no dialog).
- Table Formula / fldSimple: absent entirely (archive dialog `d5eb977` gone; the w:fldSimple
  emission sub-gap was never fixed anywhere).
- Floating-table authoring (Group E: tblpPr, wrap-around, anchors) — CLONE-LACKS both branches
  (import preserved). [User removed E from the archive loop scope — pilot carries 1 representative
  task; confirm scope with user at flow-card sign-off.]

**STRUCTURE / tab shape (v2 contextual tabs are the pre-loop slice-6 subset):**
- table-layout: 5 groups/21 controls vs Word's 7 groups — MISSING: Table group (Select menu,
  View Gridlines, Properties), Draw group, Delete menu (flat buttons instead), Insert Cells/Delete
  Cells launchers, Sort, Repeat Header Rows, Formula; Data group holds non-Word Header Row/Column.
- table-design: 2 groups/7 controls — MISSING: Table Style Options group (6 checkboxes), Border
  Styles/Pen Style/Pen Weight/Pen Color/Border Painter, Borders&Shading launcher; EXTRA: a
  clone-only Alignment group (Word keeps table alignment in Properties, not on Design).
- Borders dropdown: only 2 items (All Borders / No Border) vs Word's ~14 (per-edge, diagonals,
  Grid, Borders and Shading…).
- Cell Margins opens a 4-side inches flyout, NOT Word's Table Options dialog (archive
  `eff88de`/`b5923ed` absent). Table Properties dialog absent entirely (archive `ea7a5ba` gone).
- Insert Table dialog lacks Word's AutoFit radios + "Remember dimensions" (archive `87e63d5` gone).
- Quick Tables submenu = 4 FAKE presets (Calendar/Tabular List/Matrix/Double Table) — not Word's
  building blocks.

**Wiring / behavior:**
- `H.table` (commands.js:109) opens the Insert Table DIALOG directly — Word opens the dropdown
  (grid picker + 5 items). The Word-parity menu EXISTS (Insert.tableMenu) but the ribbon click
  isn't wired to it (archive one-liner `50ddfb3` reverted). ⚠️ INVISIBLE to the D2.1 declared-items
  diff — must be caught by SCORECARD/BEHAVIOR.
- Border-collapse paint bug: All Borders on a single cell paints only top+left thick (neighbor's
  thin border wins the shared edge); Word resolves thicker-wins (archive fork fix `47488c0`
  absent). FILE IS CLEAN — screen is wrong → **only BEHAVIOR/VISUAL can catch** (the D6.2
  micro-twin instrument; the LO-consult border rule note applies:
  parity/knowledge/lo-word-table-border-rules.md).
- Column-add overflow: adding columns pushes the table past the page margin (no re-fit; archive
  `70dd581` absent).
- Split Cells: works on merged cells only (no Word rows/cols dialog, can't split a plain cell).
- tableMerge toasts unless a CellSelection exists (probe must build a CellSelection;
  `tableSelectFirstRowPair` exists for this).
- 6-dead-dropdowns bug class LATENT: commands.js:1855 is back to the hand-kept tbl* allow-list
  (currently complete for the reduced 7-dropdown set — 0 dead TODAY; re-adding pen controls
  without generic /^tbl/ routing recreates it). Archive `304c4fc` + its regression test absent.
- PM right-click context menu: flat items with non-Word labels (Word nests under Insert submenu,
  "Insert Rows Above"/"Insert Columns to the Left"). Unmeasured by any current axis artifact.

**Pipeline pitfalls (measurement-side traps the pilot must not fall into):**
1. SCORECARD counts STUB_TOAST as PASS → "0 dead" on tables ≠ parity; Insert>Table "Draw Table"
   (real mode) is misclassified STUB_TOAST by the current classifier.
2. Contextual tabs are RUNTIME-INJECTED (not in ribbon-data.js) — audits reading ribbon-data miss
   all 28 controls; structure-probe.js intercepts showContextualTab (correct mechanism).
3. Catalog styleIds are synthesized (no dash) — OOXML ground truth must use real Word output, not
   the catalog ids.
4. COM ≠ ribbon for style/gallery actions (D1.4): ribbon Insert Table = COM Tables.Add +
   Style='Table Grid' (proven `_explore_tables.ps1`); bullets-class COM artifacts documented in
   the RUNBOOK apply.
5. tblStyles gallery content varies with the OPEN DOC (styles.xml-derived): measure on a blank doc.

## §7 — Expected FULL-PARITY candidates (hand spot-check set)

Rows the pipeline may legitimately grade pass — verify by hand that each pass is REAL:
- Insert row above/below, insert column left/right (real verbs, Word-correct labels in v2).
- Delete row/column/table (flat buttons; STRUCTURE still flags the missing Delete menu).
- Merge cells (with CellSelection), split table.
- Distribute rows/columns; AutoFit contents/window/fixed (Layout-tab control).
- Table alignment left/center/right (w:jc), table indent (tblInd).
- Per-cell width (tcW dxa) / row height / vAlign / tcMar / convert-to-text WITH TAB — the batch-D
  verbs verified Word-correct on the archive AND intact in v2 (bridge/table.ts).
- Convert Text to Table basic (tab/comma input → textToTable, fixed on main pre-fork).
- Insert>Table menu ITEM labels (D2.1 pass is genuine) — but the H.table wiring gap (§6) must
  still surface via SCORECARD/BEHAVIOR.

**Acceptance summary:** §1–§5 each rediscovered by at least one axis listed there + §7 spot-checks
all genuine + no §6 row graded full-parity ⇒ Phase B PASSES. Otherwise: fix pipeline → re-run.

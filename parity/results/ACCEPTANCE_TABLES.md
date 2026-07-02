# Phase B ACCEPTANCE — Tables pilot vs KNOWN TRUTH (2026-07-02)

> The test: the pipeline must INDEPENDENTLY rediscover every named gap in
> [KNOWN_TRUTH_TABLES.md](KNOWN_TRUTH_TABLES.md) with ZERO false full-parity verdicts on hand
> spot-checks. A miss or a false pass = a PIPELINE bug → fix → re-run. This file is the verdict
> evidence. Feature-level rollup: FEATURE_LEDGER.md → `Table` row =
> `OOXML GAP(48/49) · STRUCT GAP(items:1) · STATE GAP(2) · SCORE triage · VISUAL GAP(5/5) · BEHAV GAP(6/33)`.

## 1 — The five NAMED gaps: rediscovery matrix

| # | Known gap | Caught by | Evidence |
|---|---|---|---|
| §1 | Style gallery 2/247 | **SCORECARD** `tblStyles → GALLERY_UNDERFILLED(2 vs Word 113)` (triage) · **BEHAVIOR** style-gallery journey `FAIL(flyout items=2, want >=100)` · **VISUAL** table-styles-gallery pair FAIL (Word's sectioned 100+-thumbnail gallery + Modify/Clear/New footer vs the clone's 2-item text flyout) · **OOXML** `tb-style-listtable3` GAP 53 missing (whole List Table 3 definition, 39 styles-part nodes) · **STRUCTURE D2.1** gallery footer items missing (Modify/Clear/New Table Style) | scorecard.json, BEHAVIOR_LEDGER, VISUAL_LEDGER, tb-style-listtable3.json, STRUCTURE_LEDGER |
| §2 | cnfStyle + tblLook val | **OOXML** `tb-style-grid4a1` GAP — 4 cnfStyle signature classes missing (the 11 role markers) + `tblLook w:val=04A0` missing; all 6 `tb-styleopt-*` tasks GAP with cnfStyle/tblLook missing · **STRUCTURE** the 6 Table Style Options checkboxes in table-design MISSING | tb-style-grid4a1.json, tb-styleopt-*.json, structure.json |
| §3 | Draw Table / Eraser / Border Painter | **STRUCTURE** missing on table-layout: `TableDrawTable`, `TableEraser`; missing on table-design: `TablePaintBorder` (Border Painter), `BorderStylesGallery`, `TableDrawBorderPenStyle/PenWeight`, `BorderColorPicker` · **VISUAL** both ribbon pairs FAIL naming the absent groups | structure.json, VISUAL_LEDGER |
| §4 | Insert Cells… launcher | **STRUCTURE** `TableInsertCellsDialog` missing (+ sibling Delete-menu type-mismatch: Word menu vs clone flat buttons) · **OOXML** `tb-insert-cells-right` GAP 14 missing (import leg also LOSES a tcW) · **BEHAVIOR** delete-menu journey `FAIL(no control node: tblDelete)` | structure.json, tb-insert-cells-right.json, BEHAVIOR_LEDGER |
| §5 | Label mismatches (v2 set of 5) | **STRUCTURE** label-differs on table-layout, exactly the predicted 5: `TableRowHeight` "Height:" vs "Row Height", `TableColumnWidth` "Width:" vs "Column Width", `TableCellAlignTopLeft` "Align Top Left" vs "Align Top", `TableCellAlignBottomLeft` vs "Align Bottom", `TableRepeatHeaderRows` "Repeat Header Rows" vs "Header Row" | structure.json per_tab.table-layout.label_differs |

**All five named gaps rediscovered — by 2 to 5 independent axes each.**

## 2 — Anti-false-full check (§6 catalog)

Full-parity verdicts issued anywhere: **OOXML `tb-delete-table` semantic-pass** (the only TB pass) —
hand spot-check: both sides insert a 3×3 then delete it → near-blank docs, counts 0/0/0; genuine.
VISUAL: 0 pass. BEHAVIOR passes are click-level effects (counts/paint on reachable verbs), consistent
with §7's expected-genuine set; none contradicts a §6 row. **No §6 catalog row was graded full-parity.**
Notable §6 rediscoveries: border-collapse paint (twin `borders-all-cell` FAIL bottom-edge, model-caret
verified), No-Border clear-to-{} (twin FAIL "still painted solid 1px"), Split-Cells-dialog absent
(twin + journey FAIL "no dialog"), H.table wiring is SCORECARD-visible as `DIALOG`-on-dropdown? — no:
recorded via the D2.1-invisible note; the insert-table-menu VISUAL pair captures the Word dropdown the
clone button never opens (visual reason list), and the STATE row `insert.table` flags an enabled-state
mismatch. Insert-time defaults (tblLook val / tblW / gridCol / TableGrid spacing) appear as the
uniform 8-node base delta in EVERY table task — correct, since every clone table export carries them.

## 3 — Pipeline bugs FOUND by the pilot (fixed + locked this run)

1. **Differ text-blindness** — `w:t`/`w:delText` content absent from signatures → `tb-totext-comma`
   FALSE PASS (clone tab-text vs Word comma-text = 0 diff). FIX: TEXT_NODES + goldens (`6aca402`).
2. **Differ order-blindness** — node multiset invariant under permutation → table Sort invisible.
   FIX: per-part ordered `textOrder` stream signature + golden `row_order` (`6aca402`).
3. **Ground-truth no-op** — `tb-sort-col1` first capture: `SortAscending()` auto-header kept b/a/c
   unchanged → the rw fixture contained an UNSORTED table (the differ was honestly reporting
   "no difference"). FIX: c/b/a values (reorders under either header interpretation) (`6aca402`).
4. **Twin caret harness** — synthetic MouseEvents on painted cells do NOT drive PM selection →
   split-table twin false-FAIL (OOXML probe split fine). FIX: `caretIntoCellModel` verb; re-run
   flipped it to pass and made the border-collapse twin's middle-cell evidence unambiguous (`e356dd2`).
5. **VISUAL capture bugs** — (a) Word contextual tab is named "Table Layout" on this build (the
   "Layout" query captured the STANDARD Layout tab); (b) popup menus are separate hwnds invisible
   to PrintWindow AND SendKeys keytip chains dissolve → UIA ExpandCollapsePattern + CopyFromScreen;
   (c) the clone visual profile leaked a previous session's document into the shots → probes reset
   the doc (D5.4 discipline) (`e356dd2`).
6. **Scorecard classifier** — tblShading's swatch grid isn't `.fly-item`s → false SUSPECT; fixed via
   rich-selector. NEW gallery-content bar: `GALLERY_UNDERFILLED` lands under-filled galleries in
   TRIAGE instead of OK_FLYOUT (`e356dd2`/`39bfd73`).

## 4 — NEW findings the pilot surfaced (beyond known truth)

- **Import round-trip (D1.1, first ever run):** 45/48 pass but with a UNIFORM cluster — the clone
  ADDS an explicit `w:tblCellMar` block (0/108/0/108 dxa) + `w:hidden(val=0)` on import→resave of
  every Word table doc (explicit-vs-inherited fidelity; D1.2 pass-with-note candidate). **3 real
  LOSSES:** `tb-autofit-contents` loses `tcW type=auto`; `tb-convert-text-table` loses `tblPrEx` +
  `tblCellMar`; `tb-insert-cells-right` loses a `tcW`. → CLONE-source fixes via spec-kit.
- **Theme-palette divergence (VISUAL L4):** GT4A1 header fill = dark teal in real Word (the locked
  build's CURRENT Office theme) vs the clone's legacy `4472C4` royal blue — same style id, different
  effective palette. → likely affects every theme-color surface, not just tables.
- **Contextual tab NAME:** Word displays "Table Layout"; the clone displays "Layout" (the slice-6
  macOS-probe assumption does not hold on Word-for-Windows 16.0).
- **Word enabled-state nuance:** "Convert Text to Table…" is DISABLED in Word's Insert>Table menu
  while the caret is in a table; the clone doesn't gray it (insert-table-menu pair).
- **tb-totext-tab structure:** the clone writes the literal tab char inside one `w:t` where Word
  emits `<w:tab/>` elements + `w:tabs/w:ind` paragraph properties.
- `tb-colwidth-15in`: clone sets the CELL's width where Word's Width: sets the COLUMN (semantic
  scope diff, visible in the diff); `tb-cellmargins`: clone writes per-cell `tcMar` where Word's
  Cell Margins writes table-level `tblCellMar`.

## 5 — Honest limits / still open

- **D2.1 menu-item diff cannot see gallery TILE content** (the inventory's nesting stops at
  controls) — the 2/247 catch deliberately lands on SCORECARD/VISUAL/OOXML/BEHAVIOR instead. Noted
  as a permanent characteristic, not a bug.
- **3 BEHAVIOR ❓ pendings** (grid-picker live preview, caret-lands-in-first-cell, one-step undo,
  post-insert active tab) await a REAL-Word recording (computer-use session; D6.3 forbids guessing).
- **Journey cards are drafted but UNSIGNED** (D6.1 requires user sign-off; twins are generated and
  exempt). The 6 journey fails stand as findings either way.
- **D1.2 pass-with-note** mechanism not yet implemented (MERGEFORMAT-class notes still count as
  plain gaps — strictness errs in the safe direction; no false fulls possible from this).
- Tables-specific Word DIALOGS (Table Properties, Split Cells, Sort, Formula, Table Options,
  Borders&Shading) have no UIA dumps yet — their ABSENCE in the clone is already caught by
  STRUCTURE; field-level D2.2 comparison becomes possible only when the clone grows the dialogs.
- Scorecard STUB_TOAST-as-pass semantics remain (guard toasts vs honest stubs indistinguishable) —
  compensated by BEHAVIOR twins measuring the real effect; a classifier upgrade is queued for
  Phase C.

## VERDICT — USER-RATIFIED 2026-07-02

**PASS.** All five named gaps independently rediscovered (each by ≥2 axes); zero false full-parity
verdicts on spot-check; six pipeline bugs found by the pilot's own canaries were fixed and
golden-locked within the run — which is precisely the behavior Phase B was designed to prove.

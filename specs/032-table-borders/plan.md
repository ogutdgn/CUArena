# Implementation Plan: Table Borders Engine

**Branch**: `parity-v2` · **Date**: 2026-07-02 · **Spec**: [spec.md](spec.md)

## Summary
Rebuild the Table Design Borders group: full ~14-item Borders dropdown (per-edge merge via a new
`tableGetCellBorders()` getter; nil No-Border), a shared active pen + real Border Painter (chrome),
the CT_TcBorders schema-order + diagonals export fix (fork data), the border-collapse thicker-wins
paint pre-pass (fork, archive 47488c0 locus), and the Borders and Shading dialog cell scope.

## Constitution Check
- **I. No Fork Edits** — ⚠️ TWO plan-authorized edits: (c) `legacyBorderMigration.js` SIDES →
  canonical CT_TcBorders order carrying diagonals/inside + a `tcBorders/tblBorders` translator
  `xmlOrder` (correctness — key-insertion order otherwise scrambles sides); (d) a paint-only
  `resolveCollapsedCellBorders` pre-pass in `layout-adapter/converters/table.ts` (the paint decision
  is downstream of the bridge — not reachable from chrome; matches archive 47488c0, export
  untouched). Both marked with the fork-edit convention. Everything else is chrome/bridge.
- II ✅ (border writes via tableSetCellBorders + the new getter) · III ✅ · IV ✅ (fixture-derived;
  pipeline acceptance) · V ✅ · VI ✅ · VII ✅.

## Technical Context (research-locked)
- `tableSetCellBorders(b)` → fork setCellAttr('borders', b) = FULL REPLACE of the cell's borders
  attr (top/left/bottom/right/insideH/insideV/tl2br/tr2bl; each {val,color,size,space,themeColor}).
  Per-edge needs merge → new `tableGetCellBorders()` reads caret cell attrs.borders (mirrors
  tableGetCellMargins), merge chrome-side. No Border = explicit nil sides (val:'none',size:0,
  color:'auto') — the fork's own clear path uses this.
- Export runs `legacyBorderMigration.convertBordersToOoxmlFormat` (SIDES=['top','right','bottom',
  'left'] — wrong order, drops insideH/insideV/tl2br/tr2bl). Fix SIDES to
  ['top','start','left','bottom','end','right','insideH','insideV','tl2br','tr2bl']; add
  TCBORDERS_XML_ORDER to the tcBorders + tblBorders translators.
- Collapse paint: layout-adapter/converters/table.ts paints each cell's edges independently; add
  resolveCollapsedCellBorders(rows) after the rows.length===0 guard in tableNodeToBlock —
  each cell top=thicker(own top, above.bottom), left=thicker(own left, leftCell.right);
  guarded to unmerged uniform grids; ADD-only.
- Pen = chrome module-scoped {val,size(eighth-pt),color,themeColor}; H.tblLineStyle/tblLineWeight/
  tblPenColor/tblBorderStyles set it; B() reads it. Border Painter = chrome edge hit-test on the
  painted table → tableSetCellBorders({side: pen}) merged.
- B&S dialog D.bordersAndShading exists (paragraph/text) — add Apply-to: Cell + Grid, route to
  tableSetCellBorders.

## Structure / tasks
- **T1 (fork data, small):** legacyBorderMigration SIDES order+diagonals + tcBorders/tblBorders
  xmlOrder. pm test: cell with all-sides+diagonal → export order correct + tl2br present.
- **T2 (bridge):** tableGetCellBorders() getter; tableSetCellBorders keeps replace (merge is
  chrome). pm test.
- **T3 (chrome dropdown):** full ~14-item H.tblBorders (per-edge merge via getter; nil No-Border;
  diagonals; Borders and Shading… launcher). commands.js.
- **T4 (chrome pen + Border Painter):** tblPen state + 4 pen handlers + Borders group in
  table-tools-pm.js designTab (Word labels); Border Painter edge hit-test mode.
- **T5 (fork paint, archive-parity):** resolveCollapsedCellBorders pre-pass. The 2 border twins
  must flip to PASS.
- **T6 (chrome dialog):** D.bordersAndShading Apply-to: Cell + Grid → tableSetCellBorders.
- **T7 (measure, orchestrator):** run.py --only the 5 border tasks + tb-combo-diag-merged; behavior
  (2 border twins + a painter twin); structure (6 controls matched); VISUAL tabledesign re-judge;
  ledger; commit per piece; checkpoint.

Subagent split: T1+T2 mechanical (Opus); T3+T4 medium (Opus, archive code refs 5bf5aed/44aaefa);
T5 care (Opus draft + my review of the collapse edges — the twin is the gate); T6 small (Opus);
T7 orchestrator (me).

## Acceptance
Spec SC-001..005 via run.py/behavior/structure/visual (quickstart pattern of 030/031).

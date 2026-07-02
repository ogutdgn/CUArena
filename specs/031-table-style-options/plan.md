# Implementation Plan: Table Style Options + tblLook/cnfStyle Writer

**Branch**: `parity-v2` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)

## Summary

A single bridge-side writer `restampTableConditionalFormats` derives Word's markers from
`tableProperties.tblLook` (the single source of truth) + geometry: tblLook `val` (bridge-computed,
passes through the existing `w:val` handler — **NO fork edit needed**, research-verified) and
trPr/tcPr `cnfStyle` objects (all 12 boolean flags + `val` string, stamped only where a role
exists, removed elsewhere). Six checkboxes on Table Design flip the flags and restamp; structural
verbs restamp styled tables.

## Technical Context (research-locked)

- Attr paths: `attrs.tableRowProperties.cnfStyle` / `attrs.tableCellProperties.cnfStyle` — object
  of 12 boolean flags + `val` string; translator emits BOTH (no val↔flags derivation on export);
  setNodeMarkup round-trips (no whitelist). `cnfStyle` must be the FIRST key in the trPr object
  (trPr export has no xmlOrder; tcPr enforces it).
- tblLook: flags at `tableProperties.tblLook`; bridge writes `val` = OR(firstRow 0x20, lastRow
  0x40, firstColumn 0x80, lastColumn 0x100, noHBand 0x200, noVBand 0x400) as 4-hex-upper string —
  the translator's `createAttributeHandler('w:val')` passes it through.
- Word's stamping rules (fixture-verified, spec scenarios 1-4): row roles firstRow/lastRow;
  h-banding indexed from the first non-header row, ODD bands stamped `band1Horz`, even bands NO
  element; header/total rows excluded from banding. Cell roles firstColumn/lastColumn; v-banding
  indexed after the first column when firstColumn on, odd bands `band1Vert`. Emit all 12 explicit
  0/1 attrs + val (the differ signatures demand explicit zeros — verify booleanToString(false)
  emits "0"; set all 12 keys explicitly).
- Where NO role applies → NO cnfStyle element (delete the key), matching Word.
- Restamp hooks: tableSetStyle + tableAddRow/Column + tableDeleteRow/Column + tableMerge +
  tableSplitCell (bridge verbs); styled tables only (tableStyleId with tblStylePr present —
  approximate: any catalog/doc table style applied → stamp; TableGrid → strip stamps).
- Checkbox mapping (archive-verified): headerRow→firstRow, totalRow→lastRow, bandedRows→NOT
  noHBand, firstColumn→firstColumn, lastColumn→lastColumn, bandedColumns→NOT noVBand.
- Paint: the paged renderer reads cnfStyle additively — stamping is paint-safe; toggle repaint
  comes from the tblLook change (position×tblLook drives conditions).

## Constitution Check

I ✅ (NO fork edits — the val pass-through removes the last candidate) · II ✅ (bridge verbs) ·
III ✅ · IV ✅ (fixture-derived rules; pipeline acceptance) · V ✅ (pm tests + gates) · VI ✅ ·
VII ✅ (probe regeneration via gen_table_probes.py).

## Structure

```text
src/renderer/bridge/table-conditional-formats.ts  [NEW: restamp writer + tableStyleOption/State]
src/renderer/bridge/table.ts                      [EDIT: restamp hooks in 7 verbs]
src/renderer/bridge/index.ts                      [EDIT: wiring + pre-mount stubs]
src/renderer/public/js/table-tools-pm.js          [EDIT: td-styleopts group, 6 checkboxes]
src/renderer/public/js/ribbon.js                  [EDIT: checkbox group renderer (archive c498c6b shape)]
src/renderer/public/js/commands.js                [EDIT: 6 H.tblStyleOpt* handlers]
parity/tools/gen_table_probes.py                  [EDIT: 6 styleopt probes drive the real verb]
parity/tools/gen_table_twins.py                   [EDIT: 6 toggle twins]
scripts/test-suite-pm.js                          [EDIT: [031] tests]
```

## Tasks

- T1 writer+verbs (bridge): restampTableConditionalFormats(editor, tr?) + tableStyleOption(opt,
  on) + tableStyleOptionState(); hooks in the 7 verbs; index wiring.
- T2 UI: td-styleopts group (2×3 checkbox grid, Word labels) + handlers + state refresh on
  toggle/tab render.
- T3 probes/twins regenerated: styleopt probes call `PM.tableStyleOption(...)` after GT4A1 apply
  (unreachable notes removed); 6 generated toggle twins (docChanged + checkbox state flips).
- T4 pm tests [031]: (a) GT4A1 apply → export matches scenario-1 stamps (tblLook val 04A0 + row0
  100000000000 + band rows + firstColumn cells); (b) totalRow on → 04E0 + lastRow stamp; (c)
  headerRow off → 0480 + rebanded; (d) bandedCols on → 00A0 + band1Vert cells; (e) TableGrid
  table → NO cnfStyle anywhere; (f) insert row above on styled → stamps re-derived (no stale
  firstRow duplicate); (g) toggle = ONE undo step.
- T5 measure (orchestrator): run.py --only the 7 style tasks --capture-clone --import-leg;
  structure re-run (6 checkboxes matched); behavior re-run; ledger; commit; checkpoint.

## Acceptance

Spec SC-001..006 via quickstart-equivalent commands (same pattern as 030).

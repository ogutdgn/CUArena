# Quickstart / Validation — 030 Table Styles Catalog + Gallery + Theme

## Prereqs
- `npm run build` (probes load `out/`); Word CLOSED for any rw/COM step.
- Ground truth present: `parity/oracle/table_style_defs.json`, `parity/oracle/word_theme_palette.json`.

## Regenerate the catalog module
```bash
node scripts/gen-table-style-defs.js     # parity/oracle/table_style_defs.json -> src/renderer/core/generated/table-style-defs.ts
```

## Gates (every piece, before commit)
```bash
npm run build && npm run test:pm && npm run test:smoke && npm run test:roundtrip && npm run test:bundle
```

## Feature acceptance (the certified pipeline)
```bash
# SC-001: definition-side semantic-pass on a previously-absent style (+ D1.1 leg)
python parity/engines/run.py --only tb-style-listtable3 --capture-clone --import-leg
python parity/engines/run.py --only tb-style-grid4a1 --capture-clone --import-leg

# SC-002: journey card galleryItemCount>=100 passes
python parity/engines/behavior_verify.py --capture --report-only   # style-gallery journey → pass

# SC-003: GALLERY_UNDERFILLED clears
python parity/engines/scorecard_verify.py --capture --deep --report-only

# SC-004: VISUAL pairs re-captured + re-judged (records reasons)
python parity/engines/visual_verify.py --capture     # then judge + --record table-styles-gallery / doc-styled-table

# Ledger refresh
python parity/engines/feature_ledger.py
```

## Expected outcomes
- `tb-style-listtable3`: styles-part missing 39 → 0 (definition present, basedOn chain intact);
  remaining missing = cnfStyle/tblLook class only (FIX 2 scope) + base-table F-class.
- Behavior: `tables/style-gallery-journey` FAIL → PASS (items ≥ 113).
- Scorecard: `tblStyles` GALLERY_UNDERFILLED → OK_FLYOUT/gallery (count ≥ 113).
- VISUAL `doc-styled-table`: the teal-vs-royal-blue reason GONE from the judged verdict.
- Undo invariant: preview enter/leave leaves history length unchanged (pm test).
- Import precedence: opening a real-Word docx with its own def keeps that def verbatim (pm test
  + the D1.1 import leg loses nothing).

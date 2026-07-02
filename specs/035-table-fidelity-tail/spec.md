# Feature Specification: Table Fidelity Tail + Import Losses + Pass-With-Note

**Feature Branch**: `035-table-fidelity-tail` · **Created**: 2026-07-02 · **Status**: Draft

**Input**: FIX 6 (final) of the ratified Tables fix loop — close the D1.1 import losses, the
convert-to-text content bug, implement the D1.2 pass-with-note verdict so benign byte differences
are categorized honestly, and run the full 6-axis Tables re-measure + the final acceptance report.

## User Scenarios & Testing

### US1 — Opening a Word table file loses nothing (P1)
The 3 remaining D1.1 import losses are closed: opening a real-Word docx and resaving preserves
`tcW type=auto`, `tblPrEx`, `tblCellMar`, and per-cell `tcW` dxa.

**Acceptance**: the import-leg of tb-autofit-contents / tb-convert-text-table / tb-insert-cells-right
loses nothing (missing=0).

### US2 — Convert to Text writes Word's structure (P1)
Convert to Text with tabs writes `<w:tab/>` elements + the paragraph `w:tabs`/`w:ind` Word emits,
not a literal tab character inside one `w:t`.

**Acceptance**: tb-totext-tab's `body:t`/`body:tab` delta closes.

### US3 — Benign differences are pass-with-note, not gap (P1)
The differ/ledger gains the D1.2 `pass-with-note` verdict: functionally-harmless byte differences
(the clone writes an explicit border/width that equals the style default which Word absorbs; a
non-Word Quick Table preset) count as PASS with the diff recorded as a note, never deleted.

**Acceptance**: the style-absorption residuals (tb-borders-all/top explicit-vs-absorbed) +
tb-quicktable-calendar (non-Word preset) are `pass-with-note`; the ledger's honest parity count
rises to reflect true functional parity; the note list is the byte-parity backlog.

### US4 — The final re-measure + acceptance (P1)
All 6 axes re-run on Tables; the feature ledger's Table row reflects the loop's result; the final
acceptance report documents what's closed, what's pass-with-note, and the honest residuals
(paged-painter paint gaps, Alt-Text persist, true shift-cells, 134 legacy styles).

**Acceptance**: OOXML TB pass+pass-with-note ≥ 40/48; STRUCTURE table-design/layout ≤ 3 missing
each; VISUAL doc-render pass; BEHAVIOR named-gap journeys pass; the report is written.

### Edge cases
- pass-with-note must NOT hide a real gap (the hyperlink-style lesson): only explicitly-classified
  benign patterns qualify; the note is never deleted; a Word-vs-self check confirms the pattern is
  truly benign.
- Import losses must not regress the roundtrip gate (27/0).

## Requirements
- **FR-001**: Import preserves tcW auto / tblPrEx / tblCellMar / per-cell tcW dxa (the 3 losses).
- **FR-002**: Convert to Text emits `<w:tab/>` + paragraph tab stops, not a literal tab in w:t.
- **FR-003**: The differ/ledger implements `pass-with-note` (D1.2): a classified benign diff = PASS,
  the diff recorded in a note list, never deleted.
- **FR-004**: Classified benign patterns: style-default-absorption (clone writes an explicit
  border/shd/width equal to the active style's default that Word omits); non-Word Quick Table
  presets; explicit-default attrs (jc=left, tblLook explicit zeros).
- **FR-005**: The full 6-axis Tables re-measure runs and the feature ledger + acceptance report are
  regenerated.

## Success Criteria
- **SC-001**: import legs on the 3 loss tasks = missing 0; roundtrip stays 27/0.
- **SC-002**: tb-totext-tab body:t/tab delta closed.
- **SC-003**: OOXML TB pass+pass-with-note ≥ 40/48 (from 17 hard-pass); the pass-with-note note list
  is the recorded byte-parity backlog.
- **SC-004**: the final acceptance report (parity/results/FIX_LOOP_ACCEPTANCE.md) documents every
  fix's result + the honest residuals; the plan checkpoint is current.
- **SC-005**: 3 gates + bundle green.

## Assumptions
- Import losses are converter-import fidelity — bridge-preservable where the model already round-
  trips; a minimal converter-import fix where not (assessed per loss; documented if a fork edit).
- pass-with-note classification is conservative (only proven-benign patterns) and every note stays.
- The deep paged-painter paint gaps (vAlign/height/textdir) remain a documented layout-engine
  follow-up, NOT in this feature's scope (they're not OOXML/byte issues).

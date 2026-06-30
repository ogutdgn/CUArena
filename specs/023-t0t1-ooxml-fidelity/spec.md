# Feature Specification: Close the remaining T0/T1 OOXML over/under-emission gaps

**Feature Branch**: `023-t0t1-ooxml-fidelity`

**Created**: 2026-06-30

**Status**: Draft

**Input**: Parity-pipeline T0/T1 findings — four confirmed clone-vs-Word OOXML differences on the most-used Home
controls (the w14 ligatures gap was already closed by 022). All are direct-formatting actions where COM == ribbon,
so the parity ground truth is valid.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Lists carry the ListParagraph style (Priority: P1)

When a user applies Bullets or Numbering, the list paragraph must carry `<w:pStyle w:val="ListParagraph"/>` (before
`<w:numPr>`), exactly like real Word, and `<w:numPr>` children must be in schema order (`w:ilvl` then `w:numId`).

**Acceptance**: `python parity/engines/run.py --only bullets` and `--only numbering` no longer report
`missing pStyle[ListParagraph]`; the exported pPr has `pStyle` before `numPr` and `ilvl` before `numId`.

### User Story 2 - Align Left emits no explicit jc (Priority: P1)

When a user clicks Align Left (Word's default alignment), the paragraph must NOT emit `<w:jc w:val="left"/>` (real
Word omits it and emits no `pPr` at all for a default-left paragraph).

**Acceptance**: `python parity/engines/run.py --only alignleft` reaches semantic-pass (no `jc[left]`, no empty `pPr` extra).

### User Story 3 - Font face emits only ascii+hAnsi for a Latin pick (Priority: P2)

When a user picks a Latin font (e.g. Arial), the run's `<w:rFonts>` must carry only `w:ascii` + `w:hAnsi` (like Word),
not also `w:eastAsia` + `w:cs`.

**Acceptance**: `python parity/engines/run.py --only fontface` reaches semantic-pass; imported per-script fonts
(eastAsia/cs differing from ascii) still round-trip.

### User Story 4 - Font size emits only sz for a simple-script size (Priority: P2)

When a user sets a font size, the run must emit only `<w:sz>` (not also `<w:szCs>`) for a simple-script font, like Word.

**Acceptance**: `python parity/engines/run.py --only fontsize` reaches semantic-pass; imported complex-script `szCs`
(differing from `sz`) still round-trips.

### Edge Cases
- Toggle a list OFF → the `ListParagraph` pStyle must be removed (not left behind).
- A paragraph inheriting a non-left alignment from a style, then set to left → minor accepted divergence (re-inherits).
- Imported docs with genuine per-script fonts / complex-script sizes → preserved (companion-attr cases unchanged).

## Requirements *(mandatory)*

- **FR-001**: Bullets/Numbering list paragraphs MUST emit `<w:pStyle w:val="ListParagraph"/>` before `<w:numPr>`, and
  `<w:numPr>` children in order `ilvl` then `numId`. Toggling the list off MUST remove the pStyle.
- **FR-002**: Setting alignment to LEFT MUST NOT emit `<w:jc w:val="left"/>` (nor an empty `pPr`); center/right/justify MUST still emit `<w:jc>`.
- **FR-003**: A Latin font pick MUST emit `<w:rFonts>` with only `w:ascii`+`w:hAnsi`; imported per-script (eastAsia/cs) fonts MUST still round-trip.
- **FR-004**: A simple-script font size MUST emit only `<w:sz>` (no `<w:szCs>`); imported complex-script `szCs` MUST still round-trip.
- **FR-005**: Each fix ships a regression test in `scripts/test-suite-pm.js` (the assertion + a round-trip/toggle-off guard).

## Success Criteria *(mandatory)*

- **SC-001**: `run.py --only` for `bullets`, `numbering`, `alignleft`, `fontface`, `fontsize` all reach `semantic-pass` (missing = 0) on the `body` part.
- **SC-002**: The 3 clone gates (`test:pm`, `test:smoke`, `test:roundtrip`) stay green after `npm run build`.
- **SC-003**: No round-trip regression — imported per-script fonts / complex-script sizes / list toggles preserved.

## Assumptions
- Ground truth = the parity `rw-*.docx` real-Word COM captures (Constitution Principle IV).
- 2 fixes are NO-FORK (lists bridge wrapper, alignleft command remap); 2 are USER-AUTHORIZED fork edits (fontface, fontsize)
  — see `plan.md` Complexity Tracking. Investigation: workflow `whhkobjn3`.
- The bullets/numbering `numbering.xml` delta (COM≠ribbon singleLevel-vs-multilevel) is OUT OF SCOPE — acceptance is on the `body` part (document.xml), where `ListParagraph` is the real gap; numbering.xml needs a vsto ribbon ground truth.

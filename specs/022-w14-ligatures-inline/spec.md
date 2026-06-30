# Feature Specification: Stop inline w14 ligatures/cntxtAlts over-emission

**Feature Branch**: `022-w14-ligatures-inline`

**Created**: 2026-06-30

**Status**: Draft

**Input**: Parity-pipeline finding (T0 batch) — the clone over-emits `<w14:ligatures w14:val="standard"/>` and
`<w14:cntxtAlts/>` inline on every authored run; real Microsoft Word carries `<w14:ligatures w14:val="standardContextual"/>`
only in `styles.xml` docDefaults (`rPrDefault`), never inline per-run, and never writes `<w14:cntxtAlts/>` per-run.
This is the SYSTEMIC clone-side `extra` flagged by the differ on all 8 T0 Home controls.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Authored runs export byte-faithfully to Word (Priority: P1)

A user types or formats text (bold, italic, a font, a size, a bullet, an alignment) in the clone and saves to `.docx`.
The saved run's properties must match what real Word writes for the same action — in particular, the run must NOT carry
spurious inline `<w14:ligatures>`/`<w14:cntxtAlts>` that Word leaves in docDefaults.

**Why this priority**: This is the systemic over-emission surfaced on every authored run across the whole T0 batch (and
every future tier). One fix de-noises every downstream parity measurement, and the diff is also the RL reward — false
extras corrupt the signal. It is the highest-leverage fidelity fix found so far.

**Independent Test**: Run any T0 parity task (`python parity/engines/run.py --only bold`) and confirm the
`body:ligatures[('val','standard')]` and `body:cntxtAlts[]` extras are gone; bold/italic/underline reach 0 missing / 0 extra.

**Acceptance Scenarios**:

1. **Given** a new document, **When** the user bolds a word and exports `.docx`, **Then** the run's `<w:rPr>` contains
   `<w:b/>` and contains NO `<w14:ligatures>` or `<w14:cntxtAlts>`.
2. **Given** a new document, **When** the user sets a font / size / alignment / bullet and exports, **Then** no run carries
   inline `<w14:ligatures>`/`<w14:cntxtAlts>`.
3. **Given** the clone's blank document, **When** it is saved, **Then** `styles.xml` docDefaults still carries
   `<w14:ligatures w14:val="standardContextual"/>` (the fix removes the inline over-emission, not the faithful docDefault).

### User Story 2 - The ligatures feature still works (Priority: P2)

A user who deliberately picks a ligature style via Text Effects & Typography still gets it exported.

**Why this priority**: The fix must not silently disable a real feature. Guards against an over-broad suppression.

**Independent Test**: Apply an explicit ligature style to a run and assert the export contains `<w14:ligatures .../>`.

**Acceptance Scenarios**:

1. **Given** a run, **When** the user explicitly applies a ligature style (e.g. "All" / contextual), **Then** the export
   emits the corresponding `<w14:ligatures>` (and `<w14:cntxtAlts/>` for the contextual case).

### User Story 3 - Editing an opened Word doc doesn't flatten its docDefault ligatures (Priority: P3)

A user opens a real Word `.docx` whose docDefaults legitimately carry `standardContextual`, edits a run, and re-saves.

**Why this priority**: The over-emission must be fixed for opened docs too, not just new ones — otherwise the gap re-appears
on any imported document.

**Independent Test**: Open a docx whose docDefaults carry `standardContextual`, edit a run, export, and assert the edited
run did not gain inline `<w14:ligatures>`/`<w14:cntxtAlts>`.

**Acceptance Scenarios**:

1. **Given** an imported doc with `standardContextual` in docDefaults, **When** the user edits a run and re-exports,
   **Then** the edited run inherits the docDefault (no inline w14 ligatures) rather than flattening it inline.

### Edge Cases

- An empty paragraph (no run) — already clean (no run → no mark → no emission); must stay clean.
- A run that inherits the docDefault ligatures but has no explicit pick — must NOT emit inline.
- A run where the user explicitly picks "None"/a non-default ligature style — IS a genuine override → must emit inline.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An authored run that the user has NOT given an explicit ligatures / contextual-alternates style MUST NOT
  emit `<w14:ligatures>` or `<w14:cntxtAlts>` in its inline run properties on export.
- **FR-002**: The blank/default document's docDefaults MUST retain `<w14:ligatures w14:val="standardContextual"/>`
  (faithful to Word) — the fix removes the inline over-emission, not the docDefault.
- **FR-003**: When the user explicitly applies a ligature style (Text Effects & Typography), the export MUST still emit the
  corresponding `<w14:ligatures>` (and `<w14:cntxtAlts/>` for contextual).
- **FR-004**: Editing a run in an opened real-Word document whose docDefaults carry `standardContextual` MUST NOT promote
  that inherited value to the run's inline `<w:rPr>`.
- **FR-005**: The change MUST ship a regression test (in `scripts/test-suite-pm.js`) asserting BOTH the negative (a plain
  authored run has no inline `<w14:ligatures>`/`<w14:cntxtAlts>`) AND the positive (an explicit ligature pick still exports
  `<w14:ligatures>`).

### Key Entities

- **Run properties (`<w:rPr>`)**: the per-run formatting Word writes inline; the unit being made faithful.
- **docDefaults (`rPrDefault`)**: the document-default run properties in `styles.xml`; the legitimate home of the
  `standardContextual` ligatures value — must be preserved.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 8 T0 parity tasks (`bold, italic, underline, fontface, fontsize, bullets, alignleft, center`) drop the
  `body:ligatures[('val','standard')]` and `body:cntxtAlts[]` clone `extra` (`python parity/engines/run.py --only <id>`).
- **SC-002**: `bold`, `italic`, `underline` reach **0 missing / 0 extra** (full parity with Word for those controls).
- **SC-003**: The clone gates stay green with 0 regressions: `test:pm`, `test:smoke`, `test:roundtrip` (after `npm run build`).
- **SC-004**: An explicit ligature pick still exports `<w14:ligatures>` (the FR-003 positive regression test passes).

## Assumptions

- The parity `rw-*.docx` fixtures are **real Microsoft Word COM captures**, so the parity differ serves as the Word-fidelity
  oracle for this fix (Constitution Principle IV satisfied via the COM-captured ground truth).
- The implementation is the user-authorized **Fix B** (a CSS-normalized ligatures comparison in the fork's run-property
  override gate); the concrete approach + the Principle-I fork-edit exception are recorded in `plan.md`, not here.
- No new ribbon UI or user-facing control is added; this is an export-fidelity fix only.

## Known follow-up (out of scope for 022)

- **`stylisticSets` same-class latent gap** (adversarial-review finding, CONFIRMED low): `w14:stylisticSets` has the
  identical lossy round-trip (mark-decode `[{id,val:true}]` vs style/import `[{id}]`) that caused the ligatures
  over-emission, so it WOULD over-emit inline if a docDefault or character style ever carried it. It is **latent** — no
  blank-doc or real-Word default template carries `stylisticSets`, so the parity pipeline has not surfaced it and 022 is
  correctly scoped/not regressed. Per the pipeline's empirical ethos (fix measured gaps), it is recorded here as a
  follow-up: when a `stylisticSets` docDefault is measured, extend the 022 branch with a `composeFontFeatureSettings`
  comparison (same pattern). `numForm`/`numSpacing` round-trip 1:1 and are safe.

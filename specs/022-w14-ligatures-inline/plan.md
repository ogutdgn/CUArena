# Implementation Plan: Stop inline w14 ligatures/cntxtAlts over-emission

**Feature**: `022-w14-ligatures-inline` · **Spec**: [spec.md](./spec.md) · **Date**: 2026-06-30

## Summary

The clone promotes the docDefault `<w14:ligatures w14:val="standardContextual"/>` to **inline** run properties on every
authored run (and also writes a per-run `<w14:cntxtAlts/>`), because the override gate in the fork's
`getInlineRunProperties` compares the lossy round-tripped mark form (`ligatures:'standard'` + `contextualAlternates:true`)
against the resolved style form (`'standardContextual'`) with a RAW value compare — which always differs. Real Word keeps
the value in docDefaults only. Fix: compare the **CSS-normalized** forms (like the existing `fontFamily` branch), so the
pair only counts as a per-run override when it genuinely differs from the resolved style/docDefault.

## Technical Context

- **Root cause** (traced + runtime-verified): `src/renderer/core/superdoc-fork/extensions/run/calculateInlineRunPropertiesPlugin.js`
  → `getInlineRunProperties`, the `else` branch at ~line 670 (`inlineRunProperties[key] = valueFromMarks`). `ligatures`
  and `contextualAlternates` are in `RUN_PROPERTIES_DERIVED_FROM_MARKS`, take the raw-compare `else`, and get promoted.
  `fontFamily`/`fontSize` do NOT leak — they have a CSS-normalized comparison branch right above (~651-669).
- **Normalization helper**: `encodeMarksFromRPr({ligatures, contextualAlternates}, docx)` → a `textStyle` mark whose
  `attrs.fontVariantLigatures` is `composeFontVariantLigatures(ligatures, contextualAlternates)`
  (`super-converter/styles.js:256-257`). `standardContextual` and `standard`+`contextualAlternates:true` both compose to
  `'common-ligatures contextual'`. `encodeMarksFromRPr` is already imported by the plugin (line 4) and already used by the
  `fontFamily` branch — so **no `styles.js` edit is needed**; the fix is single-file.
- **Affected layer**: vendored fork (Constitution Principle I) — see Complexity Tracking.

## Constitution Check

| Principle | Status |
|---|---|
| I. No Fork Edits | ⚠️ **EXCEPTION (user-authorized)** — see Complexity Tracking. The bug lives entirely in fork export logic (`getInlineRunProperties`); no public API or owned-bridge seam can re-classify a fork-internal override decision. A no-fork alternative (Fix A: strip the docDefault ligatures) was rejected because it makes the clone's docDefaults diverge from Word (ligatures off by default) and does not fix opened docs. |
| II. Single Document-Write Path | ✅ No new write path; export-only logic change. |
| III. Page-Free Model | ✅ Unaffected. |
| IV. Real-Word Fidelity, Oracle-Validated | ✅ Validated against real Word via the parity `rw-*.docx` **COM captures** (the parity differ is the oracle gate here). |
| V. Test-Gated, Regression-Covered | ✅ New regression test in `scripts/test-suite-pm.js` (negative + positive) + the 3 gates + the 8 T0 parity gates. |
| VI. Spec-Kit-Driven | ✅ This `specs/022-*` feature. |
| VII. Generated Files | ✅ None hand-edited. |

## Approach (Fix B — single-file fork edit)

In `getInlineRunProperties`, add a branch beside the `fontFamily` one: when `key` is `ligatures` or
`contextualAlternates`, CSS-normalize BOTH the marks-side and the styles-side `(ligatures, contextualAlternates)` pair via
`encodeMarksFromRPr(...).find(m => m.type==='textStyle')?.attrs?.fontVariantLigatures` and only set
`inlineRunProperties[key] = valueFromMarks` when the two CSS strings differ. Effect:
- plain authored run: marks→`'common-ligatures contextual'` == styles→`'common-ligatures contextual'` → NOT promoted → no inline w14.
- explicit user pick (All / None / standard-only): composes to a different CSS → promoted → still exported.
- imported doc inheriting the docDefault: same equality → not flattened inline (FR-004).

The edit is marked `// MS-WORD-CLONE FORK EDIT (022, user-authorized)` and added to `superdoc-fork/NOTICE.md`.

## Test Plan

- **Regression test** (`scripts/test-suite-pm.js`, the `test:pm` gate):
  - **Negative**: author `<p>Revenue</p>`, select, `toggleBold`, export XML; assert the `Revenue` run `<w:rPr>` has `<w:b/>`
    and NO `w14:ligatures` / `w14:cntxtAlts`.
  - **Positive**: apply an explicit ligature style to a run; assert the export DOES contain `<w14:ligatures .../>`.
- **Gates** (after `npm run build`): `test:pm`, `test:smoke`, `test:roundtrip` stay green.
- **Parity acceptance** (the FIX-half proof): rebuild, re-capture the clone T0 fixtures, then
  `python parity/engines/run.py --only <id>` for all 8 — each drops `body:ligatures[('val','standard')]` + `body:cntxtAlts[]`;
  bold/italic/underline reach 0/0.
- **Adversarial review** of the fork edit before commit.

## Complexity Tracking — Principle I exception

| Violation | Why needed | No-fork alternative rejected because |
|---|---|---|
| Fork edit to `calculateInlineRunPropertiesPlugin.js` (`getInlineRunProperties`, ~6 lines) | The misclassification is a fork-internal export decision; there is no public API/bridge seam to re-classify it. User authorized Fix B. | Fix A (strip docDefault ligatures, no-fork) makes the clone's docDefaults diverge from Word (ligatures OFF by default, a rendering-fidelity regression) and does NOT fix the leak on opened real-Word docs. |

## Risks

- Over-suppression disabling the ligatures feature → mitigated by the positive regression test (FR-003) and by composing
  the full pair (an explicit pick composes differently).
- The `runPropertiesInlineKeys` / SD-2517 lost-keys preservation re-adding the keys → mitigated because Fix B prevents the
  INITIAL promotion, so the keys never enter `runProperties`/`runPropertiesInlineKeys`; the existing-props block (line ~678)
  also drops mark-derived keys. Verified by the negative test running through author→bold→(unset) sequences.

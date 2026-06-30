# Implementation Plan: Close the remaining T0/T1 OOXML gaps

**Feature**: `023-t0t1-ooxml-fidelity` · **Spec**: [spec.md](./spec.md) · **Date**: 2026-06-30

## Approach (per gap; investigation = workflow `whhkobjn3`)

1. **Lists `ListParagraph` (FR-001) — NO-FORK.** Root cause: `toggleList` (fork) seeds `numberingProperties` but never
   `styleId='ListParagraph'` on the ADD path. Fix: a bridge wrapper `src/renderer/bridge/lists.ts` —
   `toggleBulletList()`/`toggleOrderedList()` run the fork toggle then, in the SAME `editor.chain()...command(({tr})=>…)`,
   rebuild each list paragraph's `paragraphProperties` with `styleId:'ListParagraph'` as the FIRST key (pStyle exports
   before numPr since pPr has no xmlOrder) and `numberingProperties:{ilvl,numId}` (ilvl first). Guard on `numId!=null`
   (so toggle-OFF doesn't re-add). Rewire `commands.js` `H.bullets`/`H.numbering` + repoint the parity probes to the PM
   wrapper so they mirror the ribbon.
2. **Align Left `jc=left` (FR-002) — NO-FORK.** Root cause: `setTextAlign('left')` writes `justification='left'` →
   `<w:jc w:val="left"/>`. Fix: in `src/renderer/bridge/commands.ts` `cmd()`, remap `setTextAlign('left')` →
   `unsetTextAlign()` (the fork's existing public command clears justification; jc-translator then emits nothing, and the
   now-empty pPr is dropped). Covers ribbon + Ctrl+L + the Paragraph dialog at once.
3. **Font face `rFonts` over-spec (FR-003) — FORK EDIT (authorized).** Root cause: `decodeRPrFromMarks` fontFamily case
   (`styles.js`) fills all four slots from one mark value. Fix: set only `{ascii, hAnsi}`; leave the
   `eastAsiaFontFamily`/`csFontFamily` companion cases unchanged (imported per-script fonts still emit their slots).
4. **Font size `szCs` over-emit (FR-004) — FORK EDIT (authorized).** Root cause: `styles.js` fontSize case auto-syncs
   `fontSizeCs` (the SD-2912 class — they removed bCs/iCs but left fontSizeCs). Fix: delete the `fontSizeCs` sync +
   remove `'fontSizeCs'` from `RUN_PROPERTIES_DERIVED_FROM_MARKS` (so an imported run's `szCs` is preserved verbatim).

## Constitution Check

| Principle | Status |
|---|---|
| I. No Fork Edits | ⚠️ **2 USER-AUTHORIZED exceptions** (fontface, fontsize) — see Complexity Tracking; 2 fixes are NO-FORK. |
| IV. Real-Word Fidelity | ✅ parity `rw-*.docx` COM captures are the oracle. |
| V. Test-Gated | ✅ regression tests + the 3 gates + the 5 parity `--only` acceptances. |
| VI. Spec-Kit | ✅ this `specs/023-*`. |

## Complexity Tracking — Principle I exceptions (user-authorized)

| Fork edit | Why no-fork is impossible |
|---|---|
| `styles.js` `decodeRPrFromMarks` fontFamily → ascii+hAnsi only | the 4-slot fill lives in the fork decoder; the mark is a single CSS string, no mark shape suppresses eastAsia/cs; no public/bridge seam. |
| `styles.js` (+ `calculateInlineRunPropertiesPlugin.js`) drop the `fontSizeCs` auto-sync | the sync + the v3 szCs export live in fork code; the bridge only issues `setMark{fontSize}` with no seam into `decodeRPrFromMarks`. Mirrors the existing SD-2912 fork fix exactly. |

## Test Plan
- Regression tests in `scripts/test-suite-pm.js` (one per gap: the assertion + a guard — list toggle-off, alignment
  non-left still emits, imported per-script font preserved, imported complex-script szCs preserved).
- Batched: one `npm run build` then `test:pm`/`test:smoke`/`test:roundtrip`.
- Parity acceptance: re-capture clone T0 + `run.py --only {bullets,numbering,alignleft,fontface,fontsize}` → semantic-pass (body).
- Adversarial review of the fork edits + the bridge wrapper before commit.

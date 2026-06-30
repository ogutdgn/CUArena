# Tasks: Stop inline w14 ligatures/cntxtAlts over-emission

**Feature**: `022-w14-ligatures-inline` · **Plan**: [plan.md](./plan.md)

Single shippable slice (P1) — the fix is one fork branch + its regression test, gated by the 8 T0 parity tasks.

## T001 — RED: failing regression test (negative + positive)
- Add a test to `scripts/test-suite-pm.js`: author `<p>Revenue</p>`, select "Revenue", `toggleBold`, export XML; assert the
  run `<w:rPr>` has `<w:b/>` and NO `w14:ligatures`/`w14:cntxtAlts`. (Will FAIL on current code.)
- Add the positive assertion: apply an explicit ligature style; assert export contains `<w14:ligatures>`.
- `npm run build` (overlay) + `npm run test:pm` → watch the negative assertion FAIL for the right reason.

## T002 — GREEN: Fix B fork edit
- `calculateInlineRunPropertiesPlugin.js` `getInlineRunProperties`: add the `ligatures`/`contextualAlternates`
  CSS-normalized branch (compose both sides via `encodeMarksFromRPr`; promote only when CSS differs). Mark
  `// MS-WORD-CLONE FORK EDIT (022, user-authorized)`; add a `superdoc-fork/NOTICE.md` entry.
- `npm run build` + `npm run test:pm` → the new test passes; no other test:pm regressions.

## T003 — Gates
- `npm run build && npm run test:pm` (overlay) · `npm run build && npm run test:smoke` · `npm run build && npm run test:roundtrip` — all green.

## T004 — Parity acceptance (the FIX-half proof)
- Rebuild; re-capture the clone T0 fixtures; `python parity/engines/run.py --tier T0` (re-diff). Confirm every T0 task drops
  `body:ligatures[('val','standard')]` + `body:cntxtAlts[]`; bold/italic/underline = 0 missing / 0 extra.
- Re-run `python parity/engines/review_differ.py` (differ still green).

## T005 — Adversarial review + commit
- Adversarial review of the fork edit (does it suppress real picks? round-trip safe? lost-keys interaction?).
- Fix confirmed findings; commit (`fix(formatting): …`), update `docs/plan/` + NOTICE.

# 024 — T0/T1 cosmetic over-emit fixes (group 1 of the parity fix pass)

**Source:** the deep T0/T1 fidelity identification (`parity/results/DEEP_T0_T1_REPORT.md` §4a, adversarially
verified). Group 1 = the two CONFIRMED cosmetic over-emissions — the clone emits a redundant attribute/element
that Word omits, so the parity differ flags missing+extra even though the render is identical.

Branch: `parity-pipeline` (no feature branch; per the user's merge directive). IDENTIFY phase is done; this is FIX.

## Gaps

### FR-024-1 — `fd-allcaps`: bare `<w:caps/>` (drop the redundant `w:val="1"`)
- **Now:** the clone exports `<w:caps w:val="1"/>`; Word exports a **bare** `<w:caps/>`. Root: `caps-translator.js`
  decode hand-writes `w:val` on every ON case (`booleanToString(true)='1'`), unlike `strike` (strict-toggle) and
  `smallCaps` (single-boolean), which emit a **bare** element on ON.
- **Fix:** in `caps-translator.js` decode, on `textTransform === 'uppercase'` (ON) return `{ name: 'w:caps',
  attributes: {} }` (bare); keep the explicit-OFF case (`'none'`) emitting `{ 'w:val': '0' }` so OFF stays
  distinguishable; round-trip unchanged (encode already treats a missing `w:val` as `'1'`/true).
- **Acceptance:** `python parity/engines/run.py --only fd-allcaps` reaches **0 missing / 0 extra**; a new
  `scripts/test-suite-pm.js` regression asserts authored All-Caps exports `<w:caps/>` with **no** `w:val="1"`
  (and OFF still drops/zeroes it). Fork edit → NOTICE entry.

### FR-024-2 — `fd-link`: drop the redundant direct `<w:u w:val="single"/>` on a hyperlink run
- **Now:** the clone's hyperlink run carries BOTH `<w:rStyle w:val="Hyperlink"/>` **and** a direct
  `<w:u w:val="single"/>`; Word emits only the `rStyle` (the Hyperlink character style already supplies `u single`).
  Root: `link.js` `setLink` adds an `underline` mark (`autoAdded:true`) on top of the link mark.
- **Fix (prerequisite-gated):** suppress the redundant direct underline when the run is a hyperlink carrying
  `rStyle=Hyperlink` (either don't add the `autoAdded` underline mark, or omit it on export when the run links to
  the Hyperlink style). Must NOT change the visible underline (the style supplies it).
- **PREREQUISITE:** the differ's **styles.xml styleId-presence refactor** must land first — `fd-link`'s diff is
  dominated by a baseline-subtraction false-missing (the clone preloads the Hyperlink style; Word lazily adds it),
  so `--only fd-link` cannot reach 0/0 until the styles diff is sound (report §4c). Order: allcaps → engine refactor → link.
- **Acceptance:** after the engine refactor, `python parity/engines/run.py --only fd-link` reaches **0/0** (only the
  extra `body:u` remains, then cleared by this fix); a regression test asserts a hyperlink run has no direct `<w:u>`.

## Out of scope
The 8 other verified gaps (theme-color, double-strike/hidden/kerning, bullet-font/align, special-replace, margins)
— later groups. No clone behavior beyond removing the two redundant emissions.

## Gates (per fix)
`npm run build` → the new `test:pm` regression (RED→GREEN) → `test:roundtrip` → the `run.py --only <id>` acceptance
→ a focused adversarial review. Commit on `parity-pipeline`.

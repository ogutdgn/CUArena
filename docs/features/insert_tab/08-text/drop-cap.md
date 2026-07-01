# Drop Cap — Insert > Text

## What real Word does
Insert > Text > **Drop Cap** dropdown: **None** (remove), **Dropped** (enlarge the paragraph's first letter and sink it into the body so text wraps), **In margin** (enlarged letter in the left margin), and **Drop Cap Options…** (dialog: Position pictures, **Font**, **Lines to drop** (default 3, min 2), **Distance from text**). Applies to the active paragraph's first character.

OOXML: Word lifts the first character into its own **framed paragraph** — `w:pPr > w:framePr` with `w:dropCap='drop'|'margin'`, `w:lines='3'`, `w:wrap='around'`, `w:vAnchor='text'`, `w:hAnchor` (`'text'` dropped / `'margin'` in-margin), `w:hSpace` (= Distance from text, twips), `w:vSpace`; the enlarged glyph carries a large `w:sz`. `ST_DropCap = none|drop|margin`.

## Current clone state
**working (incl. Options)** — Menu None/Dropped/In Margin **and** "Drop Cap Options…" all ship. `dropCapMenu` (`commands.js:502-508`) → the 3 modes call `WC.PM.xeDropCap(kind, 3)`; "Drop Cap Options…" → `WC.Insert.dropCapDialog()` (`insert-features.js:222`, shipped in commit `6010ffa`). The dialog seeds from the live paragraph's `framePr` (`insert-features.js:229`) and collects Position + Lines-to-drop + Distance, then calls `WC.PM.xeDropCap(kind, n, { hSpace })` (`insert-features.js:240-241`). `xeDropCap` (`bridge/insert-exotica.ts:50-69`) writes real `paragraphProperties.framePr {dropCap, lines, wrap:'around', vAnchor:'text', hAnchor:'text', hSpace?}` via `setNodeMarkup`. The `w:framePr` translator round-trips every field (`v3/handlers/w/framePr/framePr-translator.js:18,22-27` handles `w:dropCap/w:hSpace/w:lines/w:vAnchor/w:wrap`). NOTE: the grounding `Text.json` lists Options as "missing" and `INSERT_TAB.md:55` still says hard-coded-3 — both are **stale**; Options shipped. Remaining gap: the dialog's **Font** picker is not yet applied to the framed glyph's `w:rFonts`/large `w:sz`.

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** This is the most complete Text-group button. The PM model uses a real `framePr` on `paragraphProperties`, and the converter has a dedicated, field-complete `framePr` translator (`v3/handlers/w/framePr/`) that imports and exports `dropCap/lines/hSpace/wrap/vAnchor` — so all three modes plus the Options dialog's Lines-to-drop and Distance-from-text genuinely round-trip to Word's `w:framePr`. The only honest gap is the dialog's **Font** field (and the enlarged-glyph `w:sz`), which is a small NO-FORK enrichment over the existing `xeDropCap` write — not an engine limitation.

## Required structures to build it
- **PM node/extension:** reuse `paragraph.paragraphProperties.framePr` (no new node).
- **Converter handler (super-converter):** exists — `v3/handlers/w/framePr/framePr-translator.js` round-trips `w:dropCap/w:lines/w:hSpace/w:wrap/w:vAnchor`.
- **OOXML target:** `w:pPr/w:framePr` (`@w:dropCap`, `@w:lines`, `@w:hSpace`) + the framed glyph's `w:rPr/w:rFonts` + large `w:sz` (for the Font option).
- **Bridge verb(s):** `WC.PM.xeDropCap(kind, lines, {hSpace})` — already exists; optionally extend with `{font}` to set the glyph's `rFonts`/`sz`.
- **Fork edit?** none.
- **Rough size:** S (only the Font-option enrichment remains) • **Dependencies:** none.

## Open questions for our discussion
- Apply the Options dialog's **Font** to the framed glyph (`w:rFonts` + large `w:sz`)? It's the last missing field; small but needs the glyph to be split into its own run.
- Update the stale docs (`INSERT_TAB.md:55`, and the grounding's "missing" verdict) to reflect that **Drop Cap Options shipped** — bookkeeping, not a build decision.
- Do we want true Word-style **first-character lift into a framed sub-paragraph** (Word actually splits the glyph into its own paragraph), or is the current paragraph-level `framePr` (whole-para frame) close enough for v1?

## Decision
**TBD — to be decided together.**

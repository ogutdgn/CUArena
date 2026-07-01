# Blank Page — Insert > Pages

## What real Word does
Blank Page is a single command button in the Insert > Pages group, between Cover Page and Page Break (KeyTip ≈ Alt, N, B). It inserts a **whole empty page at the cursor** by emitting **two consecutive page breaks**: one terminates the current page, one terminates the new blank page — so the content that followed the cursor starts on the page *after* the blank one (net +2 pages of separation around an empty sheet). No modal dialog, no contextual tab, no default chord shortcut.

OOXML: an empty paragraph plus two run-level page breaks — `w:p > w:r > w:br w:type="page"` (×2). No `w:sectPr` is added (it is not a section break).

## Current clone state
**working** — `src/renderer/public/js/commands.js:400` (`H.blankPage` → `WC.PM.insertBlankPage`). `insertBlankPage()` (`bridge/insert.ts:248`) calls `appendPageBreakParagraph()`, which inserts a real paragraph carrying `paragraphProperties.pageBreakBefore = true` via `editor.chain().insertContentAt(...).run()` just after the current block, then moves the caret onto it. A genuine document mutation — no toast / no-op.

**Deliberate deviation (documented at `insert.ts:241-247`):** the clone inserts **ONE** `pageBreakBefore` paragraph (net **+1** page), not Word's two-break building block (net +2). This was a fix for the prior "pages grow 2-by-2" bug, and gives a visible, clickable caret on the new page natively (an inline `<w:br w:type="page"/>` leaves no caret line in the paged engine).

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** It shares the exact same machinery as Page Break: the `paragraph` node carries `paragraphProperties` (`extensions/paragraph/paragraph.js:172`) and `pageBreakBefore` has a full round-trip translator (`v3/handlers/w/pageBreakBefore/pageBreakBefore-translator.js` — a `createSingleBooleanPropertyHandler('w:pageBreakBefore')`, registered in `v3/handlers/index.js:323`, wired into the pPr translator at `pPr-base-translators.js:22`). The paged PresentationEditor paints the new sheet and a caret-bearing line. The only open point is **fidelity of page count**: the clone intentionally produces +1, Word produces +2. Matching Word exactly (a truly empty middle page) is achievable NO-FORK but reintroduces the bug the deviation was chosen to avoid.

## Required structures to build it
- **PM node/extension:** reuse `paragraph` + its `paragraphProperties.pageBreakBefore` attr. (Alternatively reuse the `hardBreak` node with `lineBreakType: 'page'` to mirror Word's two-`w:br` model — both already exist.)
- **Converter handler (super-converter):** exists at `v3/handlers/w/pageBreakBefore/pageBreakBefore-translator.js` (paragraph-property route) and `v3/handlers/w/br/br-translator.js` + `attributes/w-line-break-type.js` (the run-break route → `w:br w:type="page"`).
- **OOXML target:** `w:p/w:pPr/w:pageBreakBefore` (current model) — or, for byte-faithful Word output, an empty `w:p` framed by two `w:r/w:br w:type="page"`.
- **Bridge verb(s):** `WC.PM.insertBlankPage()` already exists (`bridge/insert.ts:248`). A "+2, truly blank page" variant would adjust this verb only.
- **Fork edit?** none (NO-FORK).
- **Rough size:** S (it ships) • **Dependencies:** shares `appendPageBreakParagraph()` with Page Break; same import-normalization path (`bridge/page-breaks-import.ts`).

## Open questions for our discussion
- Keep the deliberate **+1** model, or restore Word's true **+2** empty-middle-page behavior (risk: the prior caret-visibility / "2-by-2 pages" regression)?
- If we go +2, does the empty middle page need a real caret line, or is an inline `w:br`-only blank page acceptable?
- Is the current behavior "faithful enough" to mark done permanently, or do we log a fidelity follow-up?

## Decision
**✅ DONE — keep the deliberate +1-page model. No work.**

User call (this session): the clone's +1 blank-page model is intentional — it fixed the prior "pages grow 2-by-2" bug and leaves a real, clickable caret on the new page that an inline `w:br` cannot. We accept the small fidelity gap vs Word's +2 rather than risk reintroducing that regression for a barely-visible difference. Blank Page is complete; no further work.

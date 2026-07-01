# Page Break — Insert > Pages

## What real Word does
Page Break is a single command button (rightmost of the three) in the Insert > Pages group. It inserts a **hard/manual page break** at the cursor so all content after the cursor moves to the top of the next page; it does **not** create an empty page (that is Blank Page). It has a real default chord shortcut **Ctrl+Enter** (Cmd+Return on Mac). It is a run-level break, **not** a section break (no `w:sectPr`). With Show/Hide ¶ on it renders as a labelled "Page Break" dotted line; it is removed by deleting the break mark. Equivalent to Layout > Breaks > Page.

OOXML: `w:p > w:r > w:br w:type="page"` — a single `CT_Br` run break with `w:type="page"`. (Word also emits a `w:lastRenderedPageBreak` *hint* at automatic break locations, but a manual break is the explicit `w:br w:type="page"`.) No `w:sectPr`.

## Current clone state
**working** — `src/renderer/public/js/commands.js:399` (`H.pageBreak` → `WC.PM.insertPageBreak`); Ctrl+Enter is wired at `commands.js:557` / `:2410`. `insertPageBreak()` (`bridge/insert.ts:233`) calls `appendPageBreakParagraph()`, inserting a real paragraph carrying `paragraphProperties.pageBreakBefore = true` just after the current block and placing the caret on the new page. Real PM transaction; exports a genuine page break; the paged engine paints a caret-bearing line.

**Deliberate model choice (per `docs/PAGE_BREAK_ROOT_CAUSE.md`):** the clone models the break as a `pageBreakBefore` **paragraph**, not an inline `<w:br w:type="page"/>` run — a caret-visibility fix (an inline run-break leaves no clickable caret line in the paged engine). Imported inline `<w:br w:type="page"/>` breaks are normalized to the same `pageBreakBefore`-paragraph model at import time (`bridge/page-breaks-import.ts`). Behaviorally faithful.

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** Both representations are fully supported by the fork. The `paragraph` node carries `paragraphProperties` (`extensions/paragraph/paragraph.js:172`) and `w:pageBreakBefore` has a complete round-trip translator (`v3/handlers/w/pageBreakBefore/pageBreakBefore-translator.js`, registered at `v3/handlers/index.js:323`). Separately the inline-run model is also covered: the `hardBreak` node supports `lineBreakType: 'page'` (`extensions/line-break/line-break.js:96,106`) and `br-translator.js` maps it both ways — import `encode` turns `w:br w:type="page"` → `hardBreak` (`br-translator.js`), and export `decode` forces `w:type="page"` for a `hardBreak` (`attributes/w-line-break-type.js`). So the feature ships and round-trips; the only nuance is the deliberate paragraph-vs-inline-run modeling decision, which is intentional and already reconciled on import.

## Required structures to build it
- **PM node/extension:** reuse `paragraph` + `paragraphProperties.pageBreakBefore` (current model). The `hardBreak` node with `lineBreakType:'page'` (`extensions/line-break/line-break.js`) is the inline-run alternative — both exist.
- **Converter handler (super-converter):** exists — `v3/handlers/w/pageBreakBefore/pageBreakBefore-translator.js` (paragraph route) and `v3/handlers/w/br/br-translator.js` + `attributes/w-line-break-type.js` (inline `w:br w:type="page"` route).
- **OOXML target:** current export = `w:p/w:pPr/w:pageBreakBefore`; Word's native form = `w:r/w:br w:type="page"` (also supported by the br handler).
- **Bridge verb(s):** `WC.PM.insertPageBreak()` already exists (`bridge/insert.ts:233`); import normalization in `bridge/page-breaks-import.ts`.
- **Fork edit?** none (NO-FORK).
- **Rough size:** S (it ships) • **Dependencies:** shares `appendPageBreakParagraph()` with Blank Page; import path `bridge/page-breaks-import.ts`.

## Open questions for our discussion
- Keep exporting `pageBreakBefore` paragraphs, or switch the *export* to Word's native inline `w:br w:type="page"` (the br handler already supports it) so saved files match Word byte-for-byte — while keeping the caret-friendly model live in-app?
- Is the caret-visibility tradeoff acceptable long-term, or do we want a round-trip test asserting `pageBreakBefore` ↔ `w:br page` equivalence against the Word-COM oracle?
- Anything to surface for deleting a break (Word removes the `w:br`; here you delete the empty `pageBreakBefore` paragraph) — does that need parity testing?

## Decision
**✅ DONE — no work.**

User call (this session): Page Break behaves identically to Word (insert at caret, `Ctrl+Enter`, imported inline `w:br` normalized). The internal model (a `pageBreakBefore` paragraph vs an inline `w:br`) is a deliberate, faithful-behaving choice. Locked as complete.

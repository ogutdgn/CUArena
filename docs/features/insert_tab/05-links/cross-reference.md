# Cross-reference — Insert > Links

## What real Word does
`Insert > Links > Cross-reference` (the same dialog is also on References > Captions) inserts a **field** that refers to another item — heading, numbered-list item, bookmark, footnote, endnote, or any captioned Figure/Table/Equation/custom-label — and auto-updates. The modeless dialog has:

- **Reference type:** dropdown — Numbered item, Heading, Bookmark, Footnote, Endnote, Equation, Figure, Table (+ any custom caption labels) — Word's ~7+ types.
- **Insert reference to:** dropdown whose contents change with the type (Page number, Paragraph/Heading number [+ no-context / full-context variants], Text, Above/below, Entire caption, Only label and number, Only caption text, etc.).
- **Insert as hyperlink** checkbox (default ON) → `\h`; for heading/numbered/caption targets without a bookmark, Word silently mints a hidden `_Ref########` bookmark around the target.
- **Include above/below** checkbox → `\p`.
- **Separate numbers with** box → `\d`.
- **For which …** list of candidate targets. Stays open after Insert.

**OOXML (oracle-verified, Word 16.0):** a field built from runs — `<w:r><w:fldChar w:fldCharType="begin"/></w:r>`, `<w:r><w:instrText xml:space="preserve"> REF <bookmark> [switches] </w:instrText></w:r>`, `<w:r><w:fldChar w:fldCharType="separate"/></w:r>`, the cached result run(s), `<w:r><w:fldChar w:fldCharType="end"/></w:r>`. **Field name is `PAGEREF` for page-number refs, `NOTEREF` for footnote/endnote-number refs, `REF` for everything else.** Switches: `\h` hyperlink, `\p` above/below, `\r`/`\n`/`\w` paragraph-number context variants, `\f` formatted note number, `\d` separator. Oracle-verified bookmark-text-with-hyperlink output: ` REF BM1 \h `.

## Current clone state
**shallow + one wrong-output bug** — `H.crossReference → crossRefDialogPM(WC.PM)` (`src/renderer/public/js/commands.js:447,1282`): a Type select offering only **Heading / Bookmark** (`commands.js:1283`) and an Insert-as select offering **Page number / Text / Above/below** (`commands.js:1284`) → `pm.refCrossReference({target,display})` (`src/renderer/bridge/references.ts:630`) → `d.crossRefs.insert(...)` (`crossref-wrappers.ts:78`), which creates a **real** `crossReference` field node and dispatches a transaction. So it is a genuine field write, not a stub. Two gaps:
1. **Shallow:** only 2 of Word's ~7 reference types (no Numbered item / Figure / Table / Equation / Footnote / Endnote); no "Insert as hyperlink" / "Include above/below" toggles surfaced as real options.
2. **BUG-013 (wrong output):** the "Page number" choice maps `display='pageNumber'`, and `buildRefInstruction` (`src/renderer/core/superdoc-fork/document-api-adapters/plan-engine/crossref-wrappers.ts:229`) pushes **`\p`** for it — but `\p` is Word's **above/below** switch (the `aboveBelow` branch at line 230 emits the same `\p`). A page-number cross-reference must emit a **PAGEREF** field, not `REF … \p`; today it renders "above/below" in Word, never the page number. `docs/INSERT_TAB.md:38` overstates this with a green check.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits
**Why:** The hard parts already exist. The `crossReference` node (`extensions/cross-reference/cross-reference.js`) holds `instruction`/`fieldType`/`target`/`display`, and the export translator `v3/handlers/sd/crossReference/crossReference-translator.js` emits the full `fldChar begin/separate/end` + `instrText` field; import is handled by the `ref-preprocessor.js` (REF) family. Crucially, a complete **PAGEREF** path also exists — `pageReference` node + `v3/handlers/sd/pageReference/pageReference-translator.js` + `field-references/fld-preprocessors/page-ref-preprocessor.js` — and a **NOTEREF** preprocessor (`noteref-preprocessor.js`) for note refs. So fixing BUG-013 and adding the missing types is **not** a new subsystem; it is additive wiring. The reason it's not pure NO-FORK: the page-number/note fix lives in the fork's plan-engine adapter — `crossRefsInsertWrapper` (`crossref-wrappers.ts:78`) hard-creates a `crossReference` node for every display mode, so for `display==='pageNumber'` it must instead create a `pageReference` node (and `NOTEREF` for note targets), and `buildRefInstruction` (line 224) must stop pushing `\p` for `pageNumber`. That's an additive branch in a fork file. The remaining shallowness (more reference types) is mostly **dialog** work feeding existing target kinds (`note`, `caption`, `numberedItem`, `styledParagraph` are already in `extractTargetName`, `crossref-wrappers.ts:207`).

## Required structures to build it
- **PM node/extension:** reuse `crossReference` (`extensions/cross-reference/`) for REF/NOTEREF/STYLEREF; reuse `pageReference` (`extensions/.../page reference`) for the page-number case. No new node.
- **Converter handler (super-converter):** exists — `v3/handlers/sd/crossReference/crossReference-translator.js` (REF), `v3/handlers/sd/pageReference/pageReference-translator.js` (PAGEREF), `field-references/fld-preprocessors/{ref,page-ref,noteref}-preprocessor.js` (import). No new handler.
- **OOXML target:** `w:fldChar`(begin/separate/end) + `w:instrText` with field name **REF** | **PAGEREF** | **NOTEREF** and switches `\h`/`\p`/`\r`/`\n`/`\w`/`\f`/`\d`.
- **Bridge verb(s):** `WC.PM.refCrossReference` (`references.ts:630`) stays; the dialog (`commands.js:crossRefDialogPM`) must offer the full type/insert-to matrix and pass the right `display`/target.kind; `refCrossReference` already forwards `display`.
- **Fork edit?** **additive** — in `crossref-wrappers.ts`: (a) `buildRefInstruction` must not emit `\p` for `pageNumber`; (b) `crossRefsInsertWrapper` must create a `pageReference` node (not `crossReference`) when `display==='pageNumber'`, and use `NOTEREF` for note targets (the `fieldType` switch already exists at line 112). Low-risk, both nodes/translators already present.
- **Rough size:** M (BUG-013 fix is S; full type matrix + hyperlink/above-below toggles is M) • **Dependencies:** rides the existing field-field infrastructure (TOC/PAGEREF/NOTEREF) and the heading/`listBookmarks` scans; "Insert as hyperlink" minting a `_Ref########` bookmark reuses the bookmark node.

## Open questions for our discussion
- Fix **BUG-013** (page-number → PAGEREF) first as a small, standalone correction, then decide separately whether to widen the type matrix? (The fix needs an additive edit in a fork plan-engine file.)
- How many of Word's ~7 reference types do we want — all (Numbered item / Figure / Table / Equation / Footnote / Endnote), or just add **Page number-as-PAGEREF** + **Footnote/Endnote (NOTEREF)** where the engine support is already complete?
- Expose **Insert as hyperlink** (`\h`, default ON in Word) and **Include above/below** (`\p`) as real checkboxes, including the hidden `_Ref########` bookmark auto-mint for hyperlinked heading/caption targets?
- Correct the false green-check in `docs/INSERT_TAB.md:38` as part of this work.

## Decision
**TBD — to be decided together.**

# Page Number — Insert > Header & Footer

## What real Word does
**Page Number** is a dropdown (not a split button) with these entries, each (except Format/Remove)
opening a flyout gallery of page-number Building Blocks:
- **Top of Page** — gallery of blocks placed in the HEADER (Plain Number 1/2/3, Accent Bar,
  Brackets, Bold Numbers *Page X* / *Page X of Y*, Dots, Roman Numeral, Vertical Outline, …).
- **Bottom of Page** — same gallery placed in the FOOTER.
- **Page Margins** — places the number in the left/right page margin as a **floating text box**
  (positioned shape) anchored to the page margin.
- **Current Position** — inserts the number block at the **current caret** (body, header, or footer)
  without changing the existing H/F layout.
- **Format Page Numbers…** — a dialog: Number format (1,2,3 | a,b,c | A,B,C | i,ii,iii | I,II,III |
  -1-,-2-,…), Include chapter number + "Chapter starts with style" + separator, and Page numbering
  **Continue from previous section** vs **Start at N**.
- **Remove Page Numbers** — removes the inserted page-number blocks/fields from the section.

**OOXML produced:** the galleries insert a `<w:sdt><w:sdtPr><w:docPartObj><w:docPartGallery
w:val="Page Numbers (Top of Page|Bottom of Page|Margins)"/></w:docPartObj></w:sdtPr><w:sdtContent>`
wrapping the PAGE field — `<w:fldSimple w:instr=" PAGE \* MERGEFORMAT "/>` or `fldChar`
begin/`<w:instrText>PAGE</w:instrText>`/separate/end runs — into `word/headerN.xml` /
`word/footerN.xml` (Page Margins wraps it in a `<w:drawing>`/`<wp:anchor>` floating text box).
**Format Page Numbers** writes `<w:pgNumType>` into the section `<w:sectPr>`: `w:fmt`
(ST_NumberFormat), `w:start` (Start at), `w:chapStyle`, `w:chapSep`. **Remove** deletes the
page-number `<w:sdt>`/PAGE-field blocks (it does NOT by itself remove `<w:pgNumType>`).

## Current clone state
**shallow** (root + Top/Bottom/Current), **working** (Remove), **missing** (Page Margins, Format
Page Numbers). `H.pageNumber` (`src/renderer/public/js/commands.js:474-480`) builds a flat flyout:
Top of Page → `WC.PM.insertPageNumber({position:'top'})`, Bottom → `{position:'bottom'}`,
Current Position → `{position:'current'}`, separator, Remove Page Numbers → `removePageNumbers()`.
`insertPageNumber` (`src/renderer/bridge/header-footer.ts:225-251`) inserts a **REAL OOXML PAGE
field** (`story.doc.fields.insert({instruction:'PAGE', mode:'raw'})`) into the header/footer part via
the story runtime — a genuine `fldChar`/`instrText` write, per-page-resolving (`isHeaderOrFooter:true`).
**Remove** (`removePageNumbers`, `:281-292`) is WORKING — it clears only bands that hold a PAGE field
(`slotHasPageField` guard, `:255-276`). Gaps: no design sub-galleries (one un-styled left-aligned
field), no alignment/format choice; **Current Position cannot target the body caret** — it always
lands in a header/footer part (`regionForPosition('current')` → active region else footer, `:194`);
**Page Margins** and **Format Page Numbers** have no handler at all (`ribbon-data.js:810,812` are
descriptive only).

## Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK (Format Page Numbers, gallery wrappers, alignment) — 🟡 additive
only for **Page Margins** if a margin-anchored text box is required.

**Why:** The core is already real. There is a dedicated **`page-number` PM node**
(`extensions/page-number/`) and a **`sd:autoPageNumber` translator** that imports/exports a true
PAGE `fldChar` field (`v3/handlers/sd/autoPageNumber/autoPageNumber-translator.js`) — the field
round-trips today. The gallery WRAPPER (`<w:sdt><w:docPartObj><w:docPartGallery>`) is supported via
the existing `documentPartObject` node + `w:sdt`/`docPartObj` handlers
(`v3/handlers/w/sdt/helpers/handle-doc-part-obj.js`). Crucially, **Format Page Numbers is fully
buildable NO-FORK**: a public adapter `sections.setPageNumbering` already writes `<w:pgNumType>`
`w:fmt`/`w:start` (`document-api-adapters/sections-adapter.ts:456-457` →
`writeSectPrPageNumbering`, `helpers/sections-xml.ts:308-313`); supported formats are
decimal/lowerLetter/upperLetter/lowerRoman/upperRoman/numberInDash (`sections-xml.ts:33-40`). So
Format-dialog **number format + Start-at/Continue** is wiring-only; the ONLY un-modeled bits are
`w:chapStyle`/`w:chapSep` (chapter numbering) — those need an additive sectPr field. **Page Margins**
is the one heavier piece: it needs a floating margin-anchored text box. The fork DOES have textbox
shape extensions (`extensions/shape-textbox`, `shape-container`) and `<w:drawing>`/`wp:anchor`
handlers (`v3/handlers/wp/anchor`), so it's additive (a positioned text box holding the PAGE field),
not a new subsystem. Fixing **Current Position** to insert at the BODY caret is NO-FORK — the
`page-number` node + `doc.fields.insert` can run on the body editor, not just an H/F story.

## Required structures to build it
- **PM node/extension:** reuse the `page-number` node (`extensions/page-number/`), the
  `documentPartObject` node (gallery wrapper), and `shape-textbox`/`shape-container` (Page Margins).
  No new node.
- **Converter handler (super-converter):** `sd:autoPageNumber` (PAGE field) EXISTS;
  `w:sdt`/`docPartObj`/`docPartGallery` EXISTS; `wp:anchor` floating drawing EXISTS;
  `w:pgNumType` read/write EXISTS (`sections-xml.ts`). ADD `w:chapStyle`/`w:chapSep` to the
  pgNumType writer for chapter numbering (additive).
- **OOXML target:** `<w:fldSimple/fldChar PAGE>` (exists); `<w:sdt><w:docPartObj><w:docPartGallery
  w:val="Page Numbers (…)"/>` (exists); `<w:pgNumType w:fmt= w:start= [w:chapStyle= w:chapSep=]>`
  (fmt+start exist; chapter additive); Page Margins `<w:drawing><wp:anchor>` text box (exists).
- **Bridge verb(s):** extend `WC.PM.insertPageNumber` to wrap the field in the `docPartObj` gallery
  + accept an alignment arg and a body-caret target (fix Current Position); add
  `WC.PM.setPageNumberFormat({format, start, chapStyle?, chapSep?})` → `sections.setPageNumbering`;
  add `insertPageNumberMargin({side})` for Page Margins.
- **Fork edit?** none for Top/Bottom galleries, alignment, Current-Position-at-body, and Format
  (format+start) — all NO-FORK; additive only for `w:chapStyle`/`w:chapSep` and the Page-Margins
  text box.
- **Rough size:** Format Page Numbers dialog = **M**; design sub-galleries + alignment = **M**;
  fix Current Position = **S**; Page Margins = **M-L**. • **Dependencies:** Top/Bottom ride the
  Header/Footer bands; Page Margins rides the Shapes/textbox + `wp:anchor` drawing engine.

## Open questions for our discussion
- **Format Page Numbers first?** It's the highest-value NO-FORK win (format + Start-at), already
  backed by `sections.setPageNumbering` — build the dialog and wire it?
- **Chapter numbering** (`w:chapStyle`/`w:chapSep`): in scope, or omit (the dialog's "Include chapter
  number" group) for v1?
- **Current Position semantics:** fix it to insert at the BODY caret (matches Word), or keep the
  current H/F-only behavior documented as a known limitation?
- **Page Margins:** build the margin-anchored text-box gallery (rides the Shapes engine), or defer
  / remove that item from the flyout for v1?
- **Design sub-galleries:** add the named alignment designs (Plain Number 1/2/3, Accent Bar, Bold
  Numbers *Page X of Y*…), or ship plain left/center/right alignment only?

## Decision
**TBD — to be decided together.**

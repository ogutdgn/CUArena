# Header — Insert > Header & Footer

## What real Word does
The **Header** control is a split button. The top half re-applies the last-used gallery
item; the arrow opens a flyout with:
- A **built-in design gallery** (~18 Building Blocks stored in *Built-In Building Blocks.dotx*):
  Blank, Blank (Three Columns), Austin, Banded, Facet, Filigree, Grid, Ion (Dark/Light),
  Integral, Retrospect, Semaphore, Sideline, Slice (Dark/Light), Stacks, Viewmaster, Whisp.
  Choosing one **replaces** the section's header content with that block, enters header-editing
  mode, and raises the **Header & Footer** contextual tab. Many blocks embed Document-Property
  content controls (Title, Author, Date) and a PAGE field.
- **Edit Header** — switches the caret into the existing header for free editing (no block
  inserted); equivalent to double-clicking the top margin.
- **Remove Header** — deletes the section's header content + the header part/reference.
- **Save Selection to Header Gallery** — opens *Create New Building Block* (Name, Gallery,
  Category, Description, Save in, Options) → persists a `<w:docPart>` into the template glossary
  (`word/glossary/document.xml`).
- **More Headers from Office.com** — fetches an online gallery.

**OOXML produced:** a header part `word/header1.xml` (root `<w:hdr>`, content type
`...wordprocessingml.header+xml`), with a relationship of type `.../header`, referenced from the
section's `<w:sectPr>` via `<w:headerReference w:type="default|first|even" r:id="rIdN"/>`. Header
content is normal block content (`<w:p>`, `<w:tbl>`, drawings); embedded property fields are
`<w:sdt>`/`<w:docPartObj>` content controls; page numbers use `<w:fldSimple w:instr=" PAGE ">`
or `fldChar` begin/separate/end runs. The three header types (default/first/even) are gated by
`<w:titlePg/>` (sectPr) and `<w:evenAndOddHeaders/>` (`word/settings.xml`).

## Current clone state
**shallow** — The Header dropdown opens ONLY a single-textarea plain-text **Edit Header** modal
(`headerFooterDialog('header')`, `src/renderer/public/js/commands.js:452-470`), whose OK calls
`WC.PM.setHeaderText(ta.value)` → bridge `setSlotText('header')`
(`src/renderer/bridge/header-footer.ts:85-112`). That bridge call is a REAL document write —
it materializes `word/headerN.xml` + the `sectPr w:headerReference` (+ rel + content-type) via the
story runtime and is Word-COM-validated (spec-kit 002). But the round-trip is **plain-text only**,
and the built-in gallery / Remove Header / Save Selection / Office.com flyout items
(`ribbon-data.js:777-798`) are descriptive strings that are **never rendered** as menu items —
classify those as MISSING. On-page rich editing is reachable separately via the contextual tab's
**Go to Header** (`enterHeaderFooter`, `header-footer.ts:345-373`), which IS a real editable band.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits

**Why:** The hardest pieces already exist. Header **parts** import/export as full PM stories:
the v2 importer reads `<w:headerReference>` → `converter.headers[rId] = { type:'doc', content:[…] }`
(`core/super-converter/v2/importer/docxImporter.js:815-839`), so a header band round-trips
**arbitrary block content** — paragraphs, tables, images (`w:drawing`), and PAGE fields — not just
text. The page-number building blocks rely on the **`documentPartObject` PM node**
(`extensions/structured-content/document-part-object.js`, with a `docPartGallery` attr) and the
`w:sdt`/`docPartObj` translators (`v3/handlers/w/sdt/helpers/handle-doc-part-obj.js`,
`translate-document-part-obj.js`), so the `<w:sdt><w:docPartObj>` wrapper Word uses for gallery
blocks **already round-trips**. So **Edit Header → on-page rich editing** is ✅ already works (just
re-point the dropdown's Edit item at `enterHeaderFooter('header')` instead of the plain modal), and
**Remove Header** is ✅ NO-FORK (clear the band via `setSlotText('header','')` + drop the
`headerReference` — the slot-clear path already exists). The genuinely missing engine piece is the
**built-in design gallery + the Building-Blocks store**: there is no glossary/`Building Blocks.dotx`
catalog, no `word/glossary/document.xml` export handler, and no UI gallery renderer. Building those
faithfully (especially **Save Selection** → glossary part) needs an additive `w:docPart`/glossary
import+export handler under `v3/handlers/` plus a bundled block catalog — additive, not a new engine.

## Required structures to build it
- **PM node/extension:** reuse — header parts are full PM `doc` stories; gallery blocks reuse the
  existing `documentPartObject` node and `w:sdt`/`docPartObj` content controls. No new node for
  Edit/Remove. (Save-to-gallery would need a glossary-doc model, not a PM node.)
- **Converter handler (super-converter):** header part import/export EXISTS
  (`docxImporter.js:815-839` + the exporter's header-part writer); `w:sdt`/`docPartObj` EXISTS.
  ADD an import/export handler for the **glossary document part** (`word/glossary/document.xml`,
  `<w:docPart>`/`<w:docPartPr>`/`<w:docPartBody>`) only if Save-Selection is in scope.
- **OOXML target:** `word/header1.xml` `<w:hdr>` + `<w:headerReference w:type=… r:id=…>` in
  `<w:sectPr>` (exists); gallery blocks `<w:sdt><w:docPartObj><w:docPartGallery>` (exists);
  Save-Selection `<w:docPart>` in `word/glossary/document.xml` (missing).
- **Bridge verb(s):** reuse `WC.PM.setHeaderText` / `getHeaderText` / `enterHeaderFooter('header')`;
  add `removeHeader()` (clear slot + drop reference) and, for the gallery, `applyHeaderBlock(id)`
  (insert a bundled block's PM content into the header story).
- **Fork edit?** none for Edit/Remove (NO-FORK); additive for the gallery catalog + glossary
  Save-Selection handler.
- **Rough size:** Edit/Remove = **S**; built-in gallery (with bundled designs) = **L**;
  Save-Selection-to-gallery = **L** (glossary subsystem). • **Dependencies:** the on-page band
  reuses the paged PresentationEditor header band (already painted per page); gallery blocks ride
  the existing `documentPartObject` + image/table converters.

## Open questions for our discussion
- **Scope:** ship the cheap, high-value wins now (real on-page **Edit Header** + a **Remove Header**
  menu item) and defer the design gallery? Those two are S/NO-FORK and remove the biggest fidelity gap.
- **Gallery fidelity:** if we build the built-in gallery, how many designs and how faithful — a few
  representative blocks (Blank, Banded, plain page-number), or the full ~18 from *Building Blocks.dotx*?
- **Building Blocks store:** is **Save Selection to Header Gallery** worth the glossary subsystem
  (`word/glossary/document.xml`), or keep it out-of-scope / removed from the ribbon?
- **Office.com:** drop "More Headers from Office.com" from the ribbon (no online runtime), or keep
  it as an honest stub?

## Decision
**TBD — to be decided together.**

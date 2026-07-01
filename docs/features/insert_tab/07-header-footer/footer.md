# Footer — Insert > Header & Footer

## What real Word does
The **Footer** control mirrors Header: a split button whose top half re-applies the last-used block
and whose arrow opens a flyout with:
- A **built-in design gallery** parallel to the header set (Blank, Blank (Three Columns), Austin,
  Banded, Facet, Filigree, Grid, Ion Dark/Light, Integral, Retrospect, Semaphore, Sideline, Slice
  Dark/Light, Stacks, Viewmaster, Whisp). Most footers embed a PAGE field and/or Author/Company
  property controls. Choosing one **replaces** the footer content, enters footer editing, and raises
  the **Header & Footer** contextual tab.
- **Edit Footer** — caret into the existing footer for free editing (≡ double-clicking the bottom
  margin).
- **Remove Footer** — deletes the section's footer content + part/reference.
- **Save Selection to Footer Gallery** — *Create New Building Block* → `<w:docPart>` with
  `<w:gallery w:val="ftrs"/>` into the template glossary.
- **More Footers from Office.com** — online gallery.

**OOXML produced:** a footer part `word/footer1.xml` (root `<w:ftr>`, content type
`...wordprocessingml.footer+xml`), relationship type `.../footer`, referenced from `<w:sectPr>` via
`<w:footerReference w:type="default|first|even" r:id="rIdN"/>`. Footer content is normal block
content; page-number footers embed `<w:fldSimple w:instr=" PAGE ">` (often wrapped in a Page-Numbers
`<w:sdt>`/`<w:docPartObj>`). Footer types mirror header types, gated by the same `<w:titlePg/>` /
`<w:evenAndOddHeaders/>` settings.

## Current clone state
**shallow** — The Footer dropdown opens ONLY the shared single-textarea plain-text **Edit Footer**
modal (`headerFooterDialog('footer')`, `src/renderer/public/js/commands.js:452-471`), OK →
`WC.PM.setFooterText` → bridge `setSlotText('footer')`
(`src/renderer/bridge/header-footer.ts:134, 85-112`). That is a REAL document write —
`word/footerN.xml` + the `sectPr w:footerReference` via the story runtime, Word-COM-validated
(spec-kit 002) — but **plain-text only**. The built-in gallery / Remove Footer / Save Selection /
Office.com flyout items (`ribbon-data.js`) are descriptive strings that are **never rendered** as
menu items → MISSING. Rich on-page editing is reachable via the contextual tab's **Go to Footer**
(`enterHeaderFooter('footer')`, `header-footer.ts:345-373`), a real editable band, and the
Page-Number flyout already inserts a real PAGE field into the footer (see `page-number.md`).

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits

**Why:** Identical situation to Header (the bridge and converter treat both symmetrically). Footer
**parts** round-trip as full PM stories — the v2 importer reads `<w:footerReference>` into
`converter.footers[rId] = { type:'doc', content:[…] }`
(`core/super-converter/v2/importer/docxImporter.js:857`), so a footer band round-trips arbitrary
block content including the PAGE field (`sd:autoPageNumber` → real `fldChar` runs,
`v3/handlers/sd/autoPageNumber/autoPageNumber-translator.js`). So **Edit Footer → on-page rich
editing** is ✅ already works (re-point the Edit item at `enterHeaderFooter('footer')`), and
**Remove Footer** is ✅ NO-FORK (`setSlotText('footer','')` + drop the `footerReference`). The
missing engine piece is again the **built-in design gallery + Building-Blocks store**: no bundled
catalog, no `word/glossary/document.xml` (`<w:docPart>` gallery `ftrs`) handler, no UI gallery —
additive work, not a new engine.

## Required structures to build it
- **PM node/extension:** reuse — footer parts are full PM `doc` stories; gallery blocks reuse the
  existing `documentPartObject` node + `w:sdt`/`docPartObj` content controls and the `page-number`
  node. No new node for Edit/Remove. (Save-to-gallery would need a glossary-doc model.)
- **Converter handler (super-converter):** footer part import/export EXISTS
  (`docxImporter.js:857` + the exporter's footer-part writer); PAGE-field + `w:sdt`/`docPartObj`
  EXIST. ADD a glossary document-part handler (`word/glossary/document.xml`, gallery `ftrs`) only if
  Save-Selection is in scope.
- **OOXML target:** `word/footer1.xml` `<w:ftr>` + `<w:footerReference>` in `<w:sectPr>` (exists);
  gallery blocks `<w:sdt><w:docPartObj>` + `<w:fldSimple/fldChar PAGE>` (exists);
  Save-Selection `<w:docPart w:gallery="ftrs">` in glossary (missing).
- **Bridge verb(s):** reuse `WC.PM.setFooterText` / `getFooterText` / `enterHeaderFooter('footer')`;
  add `removeFooter()` and, for the gallery, `applyFooterBlock(id)`.
- **Fork edit?** none for Edit/Remove (NO-FORK); additive for the gallery catalog + glossary
  Save-Selection handler.
- **Rough size:** Edit/Remove = **S**; built-in gallery = **L**; Save-Selection = **L**.
  • **Dependencies:** shares everything with Header (same bridge module, same paged footer band,
  same `documentPartObject`/PAGE-field converters); build Header + Footer together.

## Open questions for our discussion
- **Scope:** ship real on-page **Edit Footer** + a **Remove Footer** menu item now (S/NO-FORK) and
  defer the gallery? These remove the biggest fidelity gap cheaply.
- **Build Header + Footer as one unit?** They share the bridge module, converter path, and band
  rendering — splitting them buys nothing.
- **Gallery fidelity:** if we build it, a representative subset or the full ~18 designs?
- **Save-to-gallery + Office.com:** worth the glossary subsystem, or keep out-of-scope / remove
  those items from the ribbon?

## Decision
**TBD — to be decided together.**

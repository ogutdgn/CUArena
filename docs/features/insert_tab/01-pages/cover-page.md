# Cover Page — Insert > Pages

## What real Word does
Cover Page is a dropdown **Building Block Gallery** button on the Insert tab, Pages group (KeyTip: Alt, N, V). Clicking it opens a gallery of built-in designs (Banded, Facet, Filigree, Grid, Integral, Ion, Motion, Retrospect, Semaphore, Sideline, Slice, ViewMaster, Whisp, plus legacy Austin/Pinstripes/Conservative). Selecting a design **prepends a full cover page to page 1** regardless of cursor position, and does **not** add a page break or push existing content — it inserts a whole new sheet. Only one cover page can exist; inserting again replaces the existing one. There is no modal dialog for the main insert; the bottom of the gallery has "More Cover Pages from Office.com", "Save Selection to Cover Page Gallery…", and "Remove Current Cover Page". Right-clicking a gallery item exposes Insert-position commands + Edit Properties / Organize and Delete (Building Blocks Organizer).

OOXML: the cover is wrapped in a block-level `w:sdt` whose `w:sdtPr/w:docPartObj/w:docPartGallery w:val="Cover Pages"` (+ `w:docPartUnique`) marks it as a cover building block. Inside `w:sdtContent` Word places document-property content controls (Title/Author/Company/Date/Abstract via `w:dataBinding`), DrawingML design graphics (`w:drawing > wp:anchor > a:graphic > wps:wsp` shapes/text boxes), paragraphs, and a terminating `w:sectPr`. "Save Selection to Cover Page Gallery" writes a `w:docPart` into the building-blocks template glossary (`gallery w:val="coverPg"`).

## Current clone state
**shallow** — `src/renderer/public/js/commands.js:437` (`H.coverPage` → `WC.Insert.coverPageMenu`). The flyout (`insert-features.js:24`) renders 6 built-in design names + "Remove Current Cover Page"; items call `WC.PM.xeCoverPage(name)` / `xeRemoveCoverPage()` (`bridge/insert-exotica.ts:72,106`). `xeCoverPage` runs a real PM transaction: removes any existing `documentPartObject` (so only one cover), then inserts at doc start a `documentPartObject` node with `docPartGallery: 'Cover Pages'`, `docPartUnique: true`, and a **simplified 3-paragraph body** (bold Title, "[Subtitle]", "[Author Name] — year"). This exports to a real `w:sdt`/`docPartObj`.

## Can we build it in our engine?
**Verdict:** ✅ Already works (shallow — a richer gallery is an additive enhancement, not a fork need)
**Why:** The `documentPartObject` node exists (`extensions/structured-content/document-part-object.js:5` — `name: 'documentPartObject'`, with `id`/`docPartGallery`/`docPartUnique`/`wrapperParagraph` attrs) and a full import/export handler exists (`v3/handlers/w/sdt/helpers/translate-document-part-obj.js` builds the `w:sdt > w:sdtPr > w:docPartObj > w:docPartGallery` block; `sdt-node-type-strategy.js` + `handle-doc-part-obj.js` import it). So the SDT wrapper round-trips today. The gap is purely **content richness**: Word's covers embed DrawingML shapes/text boxes (`wps:wsp`) and data-bound property controls, while we insert 3 plain paragraphs. Those richer pieces would ride the **Shapes auto-shape engine** (`wps:sp`) and document-property content controls — which are separate, partly-missing subsystems — but the cover-page *mechanism* itself needs no fork edit.

## Required structures to build it
- **PM node/extension:** reuse `documentPartObject` (`extensions/structured-content/document-part-object.js`). A faithful design additionally needs the `shape-textbox`/`vector-shape`/`shape-container` extensions (already present) for embedded graphics, and (for true fidelity) data-bound property content controls (`structured-content` — partial).
- **Converter handler (super-converter):** exists at `v3/handlers/w/sdt/helpers/translate-document-part-obj.js` (export) + `sdt-node-type-strategy.js` / `handle-doc-part-obj.js` (import). For embedded shapes, the `wps:sp` / `w:drawing` handlers would also be exercised.
- **OOXML target:** `w:sdt > w:sdtPr > w:docPartObj > w:docPartGallery w:val="Cover Pages"` + `w:sdtContent` (+ optional `wps:wsp`, data-bound `w:sdt` controls, `w:sectPr`).
- **Bridge verb(s):** `WC.PM.xeCoverPage(name)` / `xeRemoveCoverPage()` already exist. A richer build would extend `xeCoverPage` to emit per-design content (and optionally add a "Save Selection to Cover Page Gallery" verb writing a glossary `w:docPart`).
- **Fork edit?** none (NO-FORK) for the current mechanism; a richer build is additive (more node JSON, no translator changes).
- **Rough size:** S (keep as-is) / M (add several faithful gallery designs with real placeholders) • **Dependencies:** richer designs ride the Shapes auto-shape engine (`wps:sp`) and the property-control content-control subsystem.

## Open questions for our discussion
- Keep the working-but-shallow 3-paragraph placeholder, or invest in M-sized faithful designs (real layouts, embedded shapes, property-bound placeholders)?
- How many of Word's ~16 built-in designs should we reproduce, and do we need design *thumbnails* in the flyout?
- Do we want "Save Selection to Cover Page Gallery" (a glossary `w:docPart` writer + organizer), or is that out of scope?
- Drop the never-rendered ribbon items ("More Cover Pages from Office.com", "Save Selection…") from the flyout, or wire them?

## Decision
**DEFERRED — blocked on the Shapes decision** (see [`../03-illustrations/shapes.md`](../03-illustrations/shapes.md)).

Rationale (user call, this session): real Word cover pages are **fundamentally shape-based** — every design's visual identity is a DrawingML shape (ViewMaster's full-page black fill, Banded's color bar, Facet's triangles, Motion's gradient band). There is no shape-free "simple" cover. A faithful Cover Page therefore **requires the Shapes auto-shape engine**; without it we could only fake the look with paragraph shading (a poor approximation). So the Cover Page decision waits on Shapes.

- **If Shapes = BUILD:** rebuild Cover Page on top of it — per-design background shapes + document-property content controls (Title / Subtitle / auto-filled Author / Date / Company / Abstract) + the full 16-design gallery, replacing today's 3-paragraph stub. (The cover *mechanism* — the `documentPartObject` SDT — already works NO-FORK; this adds the shape-based content.)
- **If Shapes = NO:** decide then between (a) leave the current shallow stub, or (b) a degraded paragraph-shading approximation.
- **Independent of Shapes (small, optional, can do either way):** fix the design-name-used-as-title bug and expand the flyout to the 16 real design names so the gallery stops being misleading in the meantime.

➡️ **Revisit this file once the Shapes decision is locked.**

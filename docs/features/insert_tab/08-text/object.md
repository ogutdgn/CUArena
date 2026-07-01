# Object — Insert > Text

## What real Word does
**Object** is a split button. Clicking the icon opens the **Object** dialog:
- **Create New** tab — pick a registered OLE server (Excel Worksheet/Chart, Bitmap Image, Word Document, PowerPoint Slide, Adobe Acrobat, Equation, …) → launches that server in-place to author a new embedded object; **Display as icon** (+ Change Icon…) embeds as a clickable icon.
- **Create from File** tab — Browse to an existing file to embed, or **Link to file** (updates when the source changes); **Display as icon**.

The arrow next to Object → **Text from File…** opens the Insert File browser: insert one or more files' contents **inline** (not as OLE), with a **Range…** button (named bookmark) and an **Insert / Insert as Link** split (link → INCLUDETEXT field).

OOXML: embedded OLE = `w:object > o:OLEObject (Type='Embed', ProgID, DrawAspect, r:id → /word/embeddings/oleObjectN.bin)` + a presentation image (`v:shape/v:imagedata` or `w:drawing/pic:pic`). Linked = `o:OLEObject Type='Link'` with an external relationship / LINK field. Insert-as-Link text = `INCLUDETEXT "C:\path" Bookmark` field.

## Current clone state
**stub (Create New) + shallow (Text from File)** — `objectMenu` (`insert-features.js:302-307`) has two items. **Object… (Create New)** → an inline `WC.toast('Embedding OLE objects … not available in this clone')` — a pure toast, no bridge call (the `xeObject` verb at `bridge/insert-exotica.ts:208` is also a toast-only no-op). **Text from File…** → `Insert.textFromFile` (`insert-features.js:308-313`) → `await window.wordAPI.open()` then `WC.PM.pasteHTMLString(WC.Files.sanitize(r.html))` — it **really** inserts the opened file's converted HTML at the caret (via the generic docx→HTML→paste path). No Range/encoding/Link-to-file options; fidelity is bounded by the docx→HTML conversion.

## Can we build it in our engine?
**Verdict (Create New / OLE embed):** ⛔ Needs an external runtime we don't have
**Verdict (Text from File):** ✅ Buildable NO-FORK
**Why:** **OLE embedding** has no path in the fork — grep for `OLEObject`/`oleObject` across `extensions/` and `core/super-converter/` returns **zero** matches; there is no `w:object`/`o:OLEObject` node or handler, no `/word/embeddings/` packaging, and (the deeper blocker) **no OLE host runtime** to launch Excel/PowerPoint/Acrobat servers in-place. So Create-New/Create-from-File OLE is honestly out of reach (the toast is correct). **Text from File**, by contrast, already works via the existing open→HTML→paste leg; upgrading it is NO-FORK: a real native-content merge (paste the opened doc's PM content instead of HTML) and an **Insert as Link** that writes an `INCLUDETEXT` field — and the field engine already builds real complex fields (`field-references/fld-preprocessors/build-block-field-node.js`), so INCLUDETEXT is reachable (it currently appears only in a test fixture, no live handler, so the field would insert but not resolve-as-include without an importer).

## Required structures to build it
- **PM node/extension:** Text-from-File reuses the paste/insert path + `fieldAnnotation` (for INCLUDETEXT). OLE would need a brand-new `oleObject` node (not planned).
- **Converter handler (super-converter):** Text-from-File = exists (open→convert→paste). INCLUDETEXT = field exporter exists; an importer that **resolves** the include is additive. OLE `w:object`/`o:OLEObject` handler = **missing**, and packaging `/word/embeddings/*.bin` is unbuilt.
- **OOXML target:** Text-from-File = native `w:p/w:r/w:tbl` merge, or `INCLUDETEXT "…" Bookmark` (link). OLE = `w:object/o:OLEObject` + `/word/embeddings/` (not feasible).
- **Bridge verb(s):** improve `Insert.textFromFile` (native merge + Range/bookmark); add `xeIncludeText({path, bookmark, link})`. Leave `xeObject` as the honest toast.
- **Fork edit?** none for Text-from-File; OLE = external-runtime, not attempted.
- **Rough size:** S–M (Text-from-File polish + Insert-as-Link) / ⛔ (OLE) • **Dependencies:** Text-from-File rides the existing file-open/convert/paste path and the field engine.

## Open questions for our discussion
- **OLE (Create New / Create from File):** confirm we **keep the honest toast / remove from ribbon** — there's no OLE host runtime and no `w:object` handler, so this is genuinely not buildable here.
- **Text from File:** upgrade to a **native PM-content merge** (better fidelity than HTML paste), and add **Insert as Link → INCLUDETEXT**? The link field would insert but won't resolve-as-include without an importer — acceptable?
- Add the **Range… (bookmark)** option and an **Insert File browser** (vs the generic open dialog)?
- Is **Display as icon** / linked-file behavior ever in scope, or strictly the inline text-insert path?

## Decision
**TBD — to be decided together.**

# Quick Parts — Insert > Text

## What real Word does
Quick Parts is the entry point to Word's **Building-Block system** (35 galleries). The dropdown holds: the **Quick Parts gallery** (user-saved blocks) + **Save Selection to Quick Part Gallery** (Alt+F3 → Create New Building Block: Name/Gallery/Category/Description/Save-in/Options); **AutoText** (its own gallery, F3 to insert by name); **Document Property** submenu (~15 core/extended props — Author, Title, Company, … inserted as **content controls** data-bound to `docProps`); **Field…** (the full Field dialog: ~10 categories, ~90 field codes, per-field switches, Field Codes toggle, Options…); and **Building Blocks Organizer…** (manage every block across galleries).

OOXML: building blocks persist as `w:docPart` in a **glossary document** (`glossary/document.xml`) with `w:docPartPr` (name/gallery/category/guid) + `w:docPartBody`. Document Property = `w:sdt > w:sdtPr > w:dataBinding (xpath to docProps) + w:docPartObj > w:sdtContent`. Field = `w:fldSimple w:instr='…'` or complex `w:fldChar begin / w:instrText / separate / result / end`. Ctrl+F9 inserts an empty field-code pair `{ }`.

## Current clone state
**shallow** — Real fields insert, but only a hard-coded handful, and the building-block side is absent. `quickPartsMenu()` (`insert-features.js:230-237`) renders Field, Document Property (always **Title** only), and 4 field shortcuts (page/numpages/date/author/filename). The **Field dialog** (`insert-features.js:239-243`) offers a fixed 6-item list → `Insert.insertField` → `WC.PM.xeQuickPart` → `insertField()` → `d.fields.insert({instruction, mode:'raw'})` — a **real** field via the document-api adapter (`bridge/insert-exotica.ts:43-47, 141-148`). **Missing entirely** (in `ribbon-data.js` but no handler): **Building Blocks Organizer**, **AutoText**, and **Ctrl+F9** empty field braces. Document Property inserts a plain `DOCPROPERTY Title` field, **not** a data-bound content control.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits
**Why:** Fields are solid — the fork builds real complex fields from a raw instruction (`field-references/fld-preprocessors/build-block-field-node.js` synthesizes `fldChar begin/separate/end` + `instrText`), there's an F9 field-update extension, and dedicated field nodes exist (`extensions/page-number/`, `document-stat-field/`, `sequence-field/`). So an expanded **Field dialog** (more categories/codes/switches) and **Ctrl+F9** (insert `{ }` braces) are NO-FORK bridge/UI work over the existing `insertField`. **Document Property as a real content control** is also reachable: the sdt/`docPartObj` machinery exists (`v3/handlers/w/sdt/` — `handle-doc-part-obj.js`, `translate-document-part-obj.js`, `structured-content` node), but a **data-bound** property control needs a `w:dataBinding`/`docProps` round-trip that the sdt handlers do not currently emit (additive). The **Building Blocks Organizer** + **AutoText** + **Save-to-Gallery** require a glossary-document (`w:docPart`) read/write subsystem the converter does not have — that is a NEW subsystem, not a small edit.

## Required structures to build it
- **PM node/extension:** reuse field nodes + `fieldAnnotation` for Field/Ctrl+F9; reuse `structured-content`/`document-part-object` for Document Property content controls.
- **Converter handler (super-converter):** Field = exists (`field-references/`, `exporter.js` fldChar). Document Property control = additive: extend `v3/handlers/w/sdt/helpers/handle-doc-part-obj.js` + a new translate path to emit/read `w:dataBinding` against `docProps/core.xml`/`custom.xml`. Building Blocks/AutoText = **new** glossary `w:docPart` import/export subsystem.
- **OOXML target:** `w:fldSimple`/`w:fldChar+instrText` (fields); `w:sdt/w:sdtPr/w:dataBinding+w:docPartObj` (doc property); `w:docPart` in `glossary/document.xml` (building blocks/AutoText).
- **Bridge verb(s):** extend `WC.PM.xeQuickPart` (more field codes); add `xeFieldCodeBraces()` (Ctrl+F9); add `xeDocProperty(propName)`; (later) `xeSaveBuildingBlock(...)`/`xeListBuildingBlocks()`.
- **Fork edit?** none for an expanded Field dialog + Ctrl+F9; **additive** for data-bound Document Property; **new subsystem** for Building Blocks Organizer/AutoText.
- **Rough size:** M (fields + doc-property) / **XL** (building-block subsystem) • **Dependencies:** field engine already shipped; doc-property rides the sdt handlers.

## Open questions for our discussion
- **Field dialog depth:** expand to the full ~90-code, switch-aware dialog, or just broaden the curated list (e.g. add NUMPAGES/REF/STYLEREF/SEQ/TOC) and add Ctrl+F9? Diminishing returns above the common 15.
- **Document Property:** ship the full ~15-prop submenu as real **data-bound content controls** (additive fork), or keep the simpler "real field" insert and just add more property names?
- **Building Blocks Organizer / AutoText / Save-to-Gallery:** these need a glossary `w:docPart` subsystem (XL). Build, keep honest stubs, or **remove from the ribbon** for now?
- Is per-field **Options/switches** UI (date pictures, `\* MERGEFORMAT`, etc.) in scope, or format-string-only?

## Decision
**TBD — to be decided together.**

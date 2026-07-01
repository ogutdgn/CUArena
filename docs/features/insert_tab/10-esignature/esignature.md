# eSignature / Signature Line — Insert > E-signature

> This file covers the whole "E-signature" surface of the Insert tab, which in real Word
> is **two distinct things** sharing a name:
> 1. **Microsoft Office Signature Line** — the native Word split-button (Insert ▸ Text ▸ Signature Line).
> 2. **Adobe Acrobat "Esignature" group** — a non-native add-in group ("Get Signatures") that only
>    exists when the Adobe Acrobat Sign add-in is installed.
> The clone has only the single `signatureLine` split control (cmd `signatureLine`,
> `ribbon-data.js:876-887`); there is **no** separate Adobe Esignature ribbon group. Both real-Word
> behaviors are analyzed below because the task names "Adobe + MS".

## What real Word does

### A. Microsoft Office Signature Line (native, Windows-only)
- **Insert ▸ Text ▸ Signature Line** (split button). Top item / "Microsoft Office Signature Line…"
  opens the **Signature Setup** dialog: *Suggested signer*, *Suggested signer's title*, *Suggested
  signer's e-mail address*, *Instructions to the signer* (default "Before signing the document, verify
  that the content you are signing is correct."), *Allow the signer to add comments in the Sign dialog*
  (checkbox), *Show sign date in signature line* (checkbox).
- On **OK**, Word inserts a **single inline graphic object** at the caret: a thin horizontal line with
  a black **X** at the left and the suggested signer name + title rendered beneath. It is selectable /
  cut / copy but **not freely resizable** (behaves like an inline shape). First use may pop a
  "Get signature services from the Office Marketplace?" info dialog.
- **OOXML produced** (an inline drawing inside a run):
  - **Primary VML form** — `<w:r><w:pict><v:shape …><v:imagedata o:title=…/><o:lock v:ext='edit'/>`
    `<o:signatureline v:ext='edit' issignatureline='t' id='{GUID}' provid='{GUID}'`
    `o:suggestedsigner='Name' o:suggestedsigner2='Title' o:suggestedsigneremail='a@b.com'`
    `signinginstructions='…' signinginstructionsset='t' allowcomments='t|f' showsigndate='t|f'/>`
    `</v:shape></w:pict></w:r>` (`CT_SignatureLine` per MS-ODRAWXML).
  - **DrawingML fallback** wrapped in `mc:AlternateContent`: `<w:drawing><wp:inline><a:graphic>`
    `<a:graphicData uri='…/picture'><pic:pic>…<a:extLst><a:ext uri='{F385189D-CB6C-4498-A905-10932F83BE7A}'>`
    `<a15:signatureLine …/></a:ext></a:extLst>…</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>`.
  - A generated **placeholder image** (EMF/PNG) is stored as media and referenced by `v:imagedata r:id`.
  - The `id` GUID is required so the line can later be **signed**. Inserting the placeholder raises **no**
    contextual ribbon tab — selecting it shows the normal Picture/Shape Format tab.
- **Signing** (double-click ▸ Sign) is a separate cryptographic flow that adds **OPC digital-signature
  parts** to the package — `/_xmlsignatures/origin.sigs`, `/_xmlsignatures/sigN.xml` (XML-DSig / XAdES with
  Office `SignatureInfoV1`: `SetupID` = line GUID, typed name, image, comments), plus a
  `digital-signature/origin` package relationship and a `[Content_Types].xml` override. Signing marks the
  doc **Final / read-only** and opens the right-hand **Signatures** task pane (not a ribbon tab).

### B. Adobe Acrobat "Esignature" group (add-in, NOT native Word)
- Appears in the Insert tab (or a dedicated "Acrobat" tab) **only when the Adobe Acrobat Sign add-in is
  installed**. A single big button "**Get Signatures**" / "Request signatures" launches the Adobe Acrobat
  Sign task pane (Office JS add-in) or hands the doc to Acrobat desktop.
- It **converts the document to a PDF agreement uploaded to Adobe's cloud** and runs an entirely web/cloud
  signing flow. **It writes no native `.docx` OOXML construct** — the artifact is a PDF agreement in
  Adobe's cloud, declared only by an Office Add-in manifest, not by document body content.

## Current clone state
**stub** — the picker UI is complete but inserts nothing.
- Main button + dropdown both route to `WC.Insert.signatureLine()` (`insert-features.js:281-289`), a
  "Signature Setup" dialog collecting only *Signer* + *Title*.
- On OK it calls `WC.PM.xeSignatureLine()` (`bridge/insert-exotica.ts:209`), a **no-op toast**
  ("Signature lines need the signature-provider subsystem…") that returns `true` and **mutates nothing**;
  the collected Signer/Title are discarded.
- The two dropdown item strings ("Microsoft Office Signature Line…", "Add Signature Services…",
  `ribbon-data.js:884-885`) have **no distinct handlers** — the dropdown branch
  (`commands.js:1859`) opens the same dialog.
- There is **no** Adobe Esignature ribbon group and **no** Signatures task pane / contextual surface.
- `docs/INSERT_TAB.md:56` falsely marks this ✅ "works"; multiple bug-hunt docs correctly classify it a stub.

## Can we build it in our engine?
**Verdict (placeholder Signature Line):** 🟡 Buildable with additive fork edits
**Verdict (actual cryptographic signing — MS or Adobe):** ⛔ Needs an external runtime we don't have

**Why:** The fork has **no signature-line support at all** — `grep` for `signatureline` / `o:signatureline`
/ `a15:signatureLine` / `CT_SignatureLine` across `core/super-converter/` returns **zero matches**. The
`w:pict` translator (`v3/handlers/w/pict/pict-translator.js` + `helpers/pict-node-type-strategy.js`) is a
strategy dispatcher that handles `v:rect` (contentBlock), `v:textbox` (shapeContainer), `v:textpath`
(text watermark) and `v:imagedata` (image watermark) — but it has **no branch for an `o:signatureline`
child**, so an imported signature line currently falls through to `type: 'unknown'` and is **dropped**.
The DrawingML `a:extLst` mechanism *is* parsed in `wp/helpers/encode-image-node-helpers.js`, but only for
the `adec:decorative` flag (line 419) — there is no `a15:signatureLine` extension handling, and the image
node is a **leaf** so it cannot carry round-trippable signature metadata as-is. Therefore inserting a
**visual, round-tripping placeholder** signature line is *possible* but requires **additive fork edits**:
a new node type (or reuse of `contentBlock`/image carrying signature attrs) plus a new `o:signatureline`
import/export handler. The **actual cryptographic signing** (both Microsoft XML-DSig and Adobe's cloud
flow) is out of reach: there is **zero** handling of the `/_xmlsignatures/*` OPC digital-signature parts
anywhere in `core/` (grep returns nothing), no certificate/PKI/XAdES runtime, and the Adobe path needs an
external PDF + cloud-agreement service we do not host.

## Required structures to build it

### Option 1 — Honest visual placeholder (recommended; matches Word's *unsigned* placeholder)
- **PM node/extension:** reuse **`contentBlock`** (`extensions/content-block/content-block.js`, already
  the import target of `v:rect`) or add a thin **`signatureLine`** node under `superdoc-fork/extensions/`
  carrying attrs `{ id(GUID), suggestedSigner, suggestedSigner2, suggestedSignerEmail, signingInstructions,
  allowComments, showSignDate, provId }`. A leaf inline **image** placeholder alone is *insufficient*
  because it can't round-trip the metadata.
- **Converter handler (super-converter):** **add** an import branch to `pict-node-type-strategy.js`
  (`v:shape` with an `o:signatureline` child → new handler) and a matching **export** translator under
  `v3/handlers/w/pict/helpers/` that emits the `<o:signatureline …>` VML (and ideally the
  `mc:AlternateContent` DrawingML `a15:signatureLine` fallback via the existing `a:extLst` plumbing in
  `encode-image-node-helpers.js`). Also generate/store the placeholder media image (the
  `pm()?.insertImage` data-URL pattern already exists).
- **OOXML target:** `w:pict / v:shape / o:signatureline` (primary) + `wp:inline / pic:pic / a:extLst /
  a15:signatureLine` (fallback).
- **Bridge verb(s):** rewrite **`WC.PM.xeSignatureLine(setup)`** (`bridge/insert-exotica.ts:209`) to accept
  the full Signature-Setup payload (currently dropped) and dispatch a real insert; surface the full
  Signature Setup dialog fields in `insert-features.js:281` (email, instructions, allow-comments,
  show-date) and split the dropdown into the two real items.
- **Fork edit?** **additive** (new strategy branch + export translator + optional new extension; rides the
  existing `w:pict` / `a:extLst` infrastructure — no edits to existing translators' behavior).
- **Rough size:** **L** • **Dependencies:** rides the `w:pict` VML subsystem and the `a:extLst` DrawingML
  extension plumbing; needs a placeholder-image generator.

### Option 2 — Real signing (MS digital signature OR Adobe Sign)
- **PM node/extension:** n/a (signing adds package-level parts, not body content).
- **Converter handler:** would need a brand-new **OPC digital-signature subsystem** to emit/preserve
  `/_xmlsignatures/origin.sigs`, `/_xmlsignatures/sigN.xml` (XML-DSig/XAdES + Office `SignatureInfoV1`),
  the relationships, and the content-type override — **none exists** (`grep _xmlsignatures` → 0 in `core/`).
- **OOXML/runtime target:** `/_xmlsignatures/*` + a certificate/PKI/XAdES signing runtime (MS path), **or**
  Adobe's external PDF-agreement cloud service (Adobe path).
- **Fork edit?** large **new subsystem** + an external crypto/cloud runtime we don't have.
- **Rough size:** **XL** • **Dependencies:** PKI/certificate store, XAdES signer, or Adobe cloud — out of scope.

## Open questions for our discussion
- **Build vs keep-stub vs split:** do we want the **visual placeholder** (Option 1, additive fork, L) so
  the control actually inserts a Word-faithful unsigned signature line that round-trips — or keep the honest
  toast stub and surface "signing needs a provider" clearly?
- **Faithfulness target:** is an *unsigned placeholder that round-trips* (no cryptographic signing) an
  acceptable "done" for this clone, given real signing (MS XML-DSig / Adobe cloud) is firmly ⛔ external?
- **VML vs DrawingML fallback:** emit just the primary `o:signatureline` VML, or also the
  `mc:AlternateContent` DrawingML `a15:signatureLine` fallback (Word's modern reader prefers it)? The latter
  costs more but is what Word writes.
- **Adobe group:** drop the "Add Signature Services…" item entirely (no add-in runtime), or keep it as an
  explicit "requires an external e-sign provider" placeholder so the ribbon matches Word's surface?

## Decision
**TBD — to be decided together.**

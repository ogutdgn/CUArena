# Signature Line — Insert > Text

## What real Word does
Insert > Text > **Add a Signature Line** (dropdown) > **Microsoft Office Signature Line**. First an information/disclaimer dialog about Microsoft signature services (OK), then the **Signature Setup** dialog: Suggested signer (name), title, e-mail, instructions, "Allow the signer to add comments", "Show sign date". OK inserts a signature-line graphic (an X line with signer name/title) anchored inline; double-clicking it later opens the **Sign** dialog to apply a real digital signature (requires a certificate/digital ID, and stores an XML digital signature part in the package, often switching the doc to read-only/Final).

OOXML: a picture/shape carrying `o:signatureline` (attributes `id`, `provid`, `suggestedsigner`, `suggestedsigner2` [title], `suggestedsigneremail`, `signinginstructions`, `allowcomments`, `showsigndate`, `issignatureline='t'`) inside `w:drawing > pic:pic` or VML `w:pict > v:shape`. CT_SignatureLine per MS-ODRAWXML. The signature itself, once signed, lives in `_xmlsignatures/…` referenced by the signature-line GUID.

## Current clone state
**stub** — A complete-looking dialog fronts a pure no-op. The Signature Setup dialog collects signer/title (`insert-features.js:219-227`), but OK → `WC.PM.xeSignatureLine()` whose **entire body** is `toast('Signature lines need the signature-provider subsystem — available in a future update'); return true` (`bridge/insert-exotica.ts:209`). **No document mutation** — the dialog inputs are discarded. (`docs/INSERT_TAB.md:56` falsely claims ✅; `docs/NOT_IMPLEMENTED.md:192` correctly lists it as not implemented.)

## Can we build it in our engine?
**Verdict:** 🔴 Needs a NEW subsystem/engine
**Why:** There is **no `o:signatureline` support anywhere** — a repo-wide grep across `extensions/` and `core/` returns zero matches for `signatureline`/`CT_SignatureLine`, and there is no node type for a signature-line shape. The closest reusable construct is the VML `shapeTextbox`/image path (`v:shape`), so we could **insert a visual placeholder** (a box with the X-line + signer name/title) that round-trips as VML — but that is a cosmetic facsimile, not a real `o:signatureline`. A faithful signature line needs (a) a new `o:signatureline`-carrying node + import/export handler, and (b) for actual **signing**, an XML-digital-signature subsystem (certificate store, `_xmlsignatures/` package part, signature provider) that this Electron clone has no host runtime for. The placeholder is buildable additively; real signing is out of reach.

## Required structures to build it
- **PM node/extension:** add a `signatureLine` node (or reuse `vector-shape`/`shapeTextbox` to carry the X-line + `o:signatureline` attrs) under `superdoc-fork/extensions/`.
- **Converter handler (super-converter):** **missing** — add an import/export handler for `o:signatureline` (likely under `v3/handlers/w/pict/helpers/` alongside the VML shape handlers, plus a `pic:pic`/`w:drawing` variant).
- **OOXML target:** `o:signatureline` (in `w:pict/v:shape` or `w:drawing/pic:pic`); the signed artifact = `_xmlsignatures/` digital-signature part (out of scope).
- **Bridge verb(s):** replace the toast `WC.PM.xeSignatureLine()` with a real `xeSignatureLine({signer,title,email,instructions,allowComments,showDate})` that builds the node.
- **Fork edit?** **additive** (new node + new `o:signatureline` handler) for the placeholder; the signing engine is a separate **external-runtime** problem.
- **Rough size:** L (placeholder + handler) / XL+ (real signing — likely never) • **Dependencies:** rides the VML shape encoder for the visual.

## Open questions for our discussion
- **Build vs honest stub:** is a non-signable **visual signature-line placeholder** (real `o:signatureline` markup, but no actual digital signing) useful, or does a signature line without signing mislead users?
- If we build the placeholder, do we round-trip the `o:signatureline` attributes (so Word recognizes it and can sign it later), or just draw a look-alike box?
- Real **digital signing** needs a certificate store + `_xmlsignatures/` subsystem with no Electron host runtime — confirm we **leave signing out / keep the stub honest** and possibly relabel the ribbon item.

## Decision
**TBD — to be decided together.**

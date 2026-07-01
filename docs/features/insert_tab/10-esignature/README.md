# Insert ▸ E-signature — feasibility group index

Faithful-clone feasibility for the Insert tab's "E-signature" surface. Real Word splits this into the
native **Microsoft Office Signature Line** (Insert ▸ Text ▸ Signature Line split button) and the
non-native **Adobe Acrobat "Esignature" group** (add-in only). The clone has only the single
`signatureLine` split control — analyzed together in one file.

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [eSignature / Signature Line (Adobe + MS)](./esignature.md) | 🟡 placeholder: additive fork edits • ⛔ real signing: external runtime | L (placeholder) / XL (signing) | New `o:signatureline` import/export handler on the `w:pict` subsystem + a `signatureLine`/`contentBlock` node carrying the setup attrs; rewire `WC.PM.xeSignatureLine` to stop dropping the dialog payload. Cryptographic signing (`/_xmlsignatures/*` XML-DSig / Adobe cloud) needs a subsystem/runtime we don't have. |

**Legend:** ✅ Already works · ✅ Buildable NO-FORK · 🟡 Buildable with additive fork edits ·
🔴 Needs a NEW subsystem/engine · ⛔ Needs an external runtime we don't have.

**Key grounding facts**
- The fork has **no** signature-line support: `grep signatureline|o:signatureline|a15:signatureLine|CT_SignatureLine`
  over `core/super-converter/` returns **zero** matches.
- The `w:pict` translator (`v3/handlers/w/pict/pict-translator.js`, `helpers/pict-node-type-strategy.js`)
  dispatches `v:rect`/`v:textbox`/`v:textpath`/`v:imagedata` only — no `o:signatureline` branch, so an
  imported signature line is **dropped** (`type: 'unknown'`).
- The DrawingML `a:extLst` plumbing exists in `wp/helpers/encode-image-node-helpers.js` (line 419) but only
  for the `adec:decorative` flag — no `a15:signatureLine` extension.
- **No** digital-signature OPC parts are handled anywhere: `grep _xmlsignatures|digital-signature/origin`
  over `core/` returns nothing. Real signing (MS or Adobe) is firmly out of reach.
- Current clone path: `WC.Insert.signatureLine()` dialog (`insert-features.js:281`) → `WC.PM.xeSignatureLine()`
  (`bridge/insert-exotica.ts:209`) = **no-op toast**, mutates nothing, discards Signer/Title.

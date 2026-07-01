# Insert > Text — feasibility index

Button-by-button feasibility for the **Insert > Text** ribbon group, grounded in the
SuperDoc-fork engine (`src/renderer/core/superdoc-fork/`) and the `WC.PM` bridge
(`src/renderer/bridge/*.ts`). Each row links to a full feasibility doc.

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Text Box](text-box.md) | 🟡 Buildable with additive fork edits | M | `shapeTextbox` node + VML handlers exist (insert works); additive: floating `wp:anchor` export + Shape Format contextual tab + gallery/draw UI |
| [Quick Parts](quick-parts.md) | 🟡 Buildable with additive fork edits | M / XL | Field engine exists (NO-FORK Field dialog + Ctrl+F9); additive: data-bound Document Property `w:sdt`; new subsystem: glossary `w:docPart` (Building Blocks / AutoText) |
| [WordArt](wordart.md) | ✅ Buildable NO-FORK | S / M | `vector-shape` already emits real `wps:wsp`+`w14:textFill`+`a:prstTxWarp`; parameterize presets/warp/outline (+ optional contextual tab) |
| [Drop Cap](drop-cap.md) | ✅ Already works | S | `paragraph.framePr` + `w/framePr` translator round-trip all 3 modes + Options (Lines/Distance shipped); only the Font option remains |
| [Signature Line](signature-line.md) | 🔴 Needs a NEW subsystem | L / XL+ | No `o:signatureline` node/handler anywhere — add node + `o:signatureline` handler for a placeholder; real signing needs an `_xmlsignatures/` runtime (out of reach) |
| [Date & Time](date-time.md) | ✅ Buildable NO-FORK | S | Field engine + static-text path both exist; add locale format list / Language / Calendar / Set-As-Default over `xeDateTime` |
| [Object](object.md) | ⛔ OLE: external runtime · ✅ Text-from-File: NO-FORK | S–M / ⛔ | No `o:OLEObject` node/handler + no OLE host runtime (keep toast); Text-from-File works (open→paste), upgrade to native merge + INCLUDETEXT link |

### Verdict legend
- ✅ **Already works** — ships and round-trips today.
- ✅ **Buildable NO-FORK** — bridge/UI only; the node + converter handler already exist.
- 🟡 **Buildable with additive fork edits** — needs a new (purely additive) node/extension or converter handler.
- 🔴 **Needs a NEW subsystem/engine** — a substantial missing engine piece (e.g. signature-line markup + signing).
- ⛔ **Needs an external runtime we don't have** — e.g. OLE in-place servers / `_xmlsignatures` signing.

### Cross-cutting notes
- **Shape Format / Drawing Tools contextual tab is absent** (`bridge/state-sync.ts:282-285` only matches `selection.node.type.name === 'image'`). Text Box **and** WordArt both want it — building it once unblocks fill/outline/effects/arrange for both. Treat as a shared sub-feature.
- The **field engine is strong** (`field-references/fld-preprocessors/build-block-field-node.js` builds real `fldChar`+`instrText`; `extensions/field-update/` resolves on F9). Date & Time, Quick Parts > Field, and Object > Insert-as-Link all ride it.
- **Stale docs:** `Text.json` + `docs/INSERT_TAB.md:55` mark **Drop Cap Options** as missing/hard-coded-3, but it shipped (commit `6010ffa`, `insert-features.js:222` `dropCapDialog`). `INSERT_TAB.md:56` falsely claims Signature Line ✅ (it's a toast stub).

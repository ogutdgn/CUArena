# WordArt — Insert > Text

## What real Word does
Insert > Text > **WordArt** opens a 15-thumbnail gallery (3×5 grid of theme-driven preset styles, each a stylized "A"). Picking a preset inserts a WordArt object with placeholder text ("Your text here") or applies the style to selected text. After insert, the **Shape Format (Drawing Tools)** tab's **WordArt Styles** group offers **Text Fill**, **Text Outline**, and **Text Effects** (Shadow, Reflection, Glow, Bevel, 3-D Rotation, and **Transform** — Follow Path arch/circle/button + ~40 warp presets).

OOXML: WordArt is a `wps:wsp` text box whose runs carry DrawingML text effects — `w:drawing > a:graphic/a:graphicData(wordprocessingShape) > wps:wsp > wps:txbx/w:txbxContent` with `w:rPr` containing `w14:textFill`, `w14:textOutline`, `a:effectLst`, etc.; the warp is `wps:bodyPr > a:prstTxWarp prst='textArchUp'…`. VML fallback `w:pict/v:shape/v:textpath`.

## Current clone state
**working** — `wordArtMenu` renders a 6-cell CSS-styled gallery (`insert-features.js:204-216`) → `Insert.insertWordArt` → `WC.PM.xeWordArt(txt,{color})` (`bridge/insert-exotica.ts:181-183`) → `editor.commands.insertWordArt(...)` (fork `extensions/vector-shape/vector-shape.js`). It builds a **real DrawingML blob**: `wp:inline > a:graphic/a:graphicData(uri=…/wordprocessingShape) > wps:wsp > wps:spPr(a:prstGeom rect) + wps:txbx/w:txbxContent` with `w:sz=72` + `w14:textFill/w14:solidFill/w14:srgbClr`, and `wps:bodyPr fromWordArt='1'` with `a:prstTxWarp prst='textNoShape'`. So it inserts and exports valid OOXML. Gap vs Word: only 6 CSS-approximated presets (vs 15 theme presets), no text outline/effects, and **no Transform** (warp is hard-coded `textNoShape`); selecting WordArt raises **no** contextual tab.

## Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** The hard part is already done and round-trips — `insertWordArt` synthesizes a genuine `wps:wsp` WordArt blob with a `w14:textFill` and an `a:prstTxWarp` scaffold (`vector-shape.js`), and the textOutline translator exists (`v3/handlers/w/w14-textOutline/`). Enriching it is parameterization of an existing builder, not new node/handler work: more presets = more entries in `wordArtMenu`; Transform = pass a real `prst` (e.g. `textArchUp`) into the already-emitted `a:prstTxWarp`; outline = add a `w14:textOutline` block (the handler already round-trips it); gradient fill = swap `w14:solidFill` for `w14:gradFill`. The only thing that is genuinely additive is the **WordArt Styles contextual tab** (the same `state-sync.ts:282-285` `type==='image'`-only gap as Text Box) — that is shared UI work, not a converter change.

## Required structures to build it
- **PM node/extension:** reuse `vector-shape` (the WordArt node already builds the full DrawingML blob).
- **Converter handler (super-converter):** exists — `wps:wsp`/`w14:textFill` are written by the node's own blob; `w14-textOutline` translator already round-trips outlines. No new handler needed for fill/outline/warp.
- **OOXML target:** `wps:wsp` + `w:rPr/w14:textFill` (+ `w14:textOutline`, `a:gradFill`) + `wps:bodyPr/a:prstTxWarp prst=…`.
- **Bridge verb(s):** extend `WC.PM.xeWordArt` to accept `{preset, warp, outline, gradient}` and thread them into `insertWordArt`'s blob builder; (optional) a Shape-Format-tab path in `state-sync.ts`.
- **Fork edit?** none — `vector-shape.js` already emits the blob; we pass more attributes.
- **Rough size:** S (presets + warp + outline) / M (with contextual tab) • **Dependencies:** shares the contextual-tab gap with Text Box; reuses `w14-textOutline`.

## Open questions for our discussion
- How faithful: 6 curated presets (current) vs the full 15 theme-driven grid? The CSS thumbnails won't perfectly match Word's theme rendering regardless.
- Add **Transform/warp** presets now (cheap — the `a:prstTxWarp` slot already exists, just hard-coded to `textNoShape`)? Which set — the common Follow-Path arch/circle + a few warps?
- Wire the **WordArt Styles contextual tab** in this slice (shared with Text Box / Shape Format) or defer to a unified shape-tools feature?
- Worth adding **Text Outline / gradient fill** to round-trip, given the handlers exist and Word reads them back?

## Decision
**TBD — to be decided together.**

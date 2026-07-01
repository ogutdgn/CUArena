# Icons — Insert > Illustrations

## What real Word does
Icons opens the Office Content / Stock Images picker positioned on the **Icons** collection
(with a search box and ~45 categories: Accessibility, Animals, Arrows, Business, Faces, …,
plus Cutout People / Stickers / Illustrations / Cartoon People tabs). Icons are vector SVG —
scalable with no quality loss, recolorable, and convertible to freeform shapes via
**Graphics Format > Change > Convert to Shape**. Selecting one or more and Insert embeds each
as `w:drawing > wp:inline > a:graphic > a:graphicData uri=.../picture > pic:pic` with an
`a:blip` + `a:extLst/asvg:svgBlip r:embed` → `word/media/imageN.svg` (plus a rasterized PNG
fallback blip). A selected icon raises the distinct **Graphics Format** contextual tab
(Change / Graphics Styles / Accessibility / Arrange / Size). KeyTips Alt, N, F.

## Current clone state
**working** — `H.icons` (`src/renderer/public/js/commands.js:439`) → `WC.Insert.iconsPicker`
(`insert-features.js:125`) opens a searchable grid; clicking calls `WC.PM.xeIcon(name)`
(`bridge/insert-exotica.ts:159`), which builds an SVG data-URL from the app's own
`WC.icon()` (Fluent UI set) and calls `pm().insertImage({ src, alt, width:32, height:32 })`
→ `insert.ts:45` `editor.chain().setImage().run()`. A genuine document mutation that
round-trips as an image. Gaps vs. Word: it inserts the **app's own Fluent SVGs** (not
Microsoft's licensed stock-icon library); the SVG is embedded as a plain image (not the
`asvg:svgBlip` dual-blip); and a selected icon shows the **Picture Format** tab, not a
distinct **Graphics Format** tab.

## Can we build it in our engine?
**Verdict:** ✅ Already works
**Why:** The whole insert path is real and tested — `WC.PM.xeIcon` → `insertImage` →
`setImage` → `image` node → `encode-image-node-helpers.js` emits `pic:pic`/`a:blip` + a media
part, so an inserted icon survives a Word round-trip as a picture. The only divergences from
Word are fidelity polish, not engine gaps: (1) our own SVG set rather than Microsoft's
licensed library (which we cannot legally ship); (2) embedding as a plain SVG image rather
than the `asvg:svgBlip` + PNG-fallback dual-blip — an **additive** encoder branch if we want
true Word-SVG fidelity; (3) routing a selected SVG to a dedicated **Graphics Format** tab
instead of Picture Format — a chrome/state-sync change. None of these require a new node or
subsystem.

## Required structures to build it
- **PM node/extension:** reuse `image` (`extensions/image/`) — works today. (A future "Convert to Shape" would route through `vectorShape`.)
- **Converter handler (super-converter):** exists (`encode-image-node-helpers.js`). Additive: an `asvg:svgBlip` + PNG-fallback branch for true SVG fidelity; a marker so the icon raises Graphics Format.
- **OOXML target:** `pic:pic/a:blip` + `a:extLst/asvg:svgBlip r:embed` → `word/media/imageN.svg`.
- **Bridge verb(s):** `WC.PM.xeIcon` (exists). Optional: a flag so `state-sync` shows Graphics Format vs Picture Format.
- **Fork edit?** none to keep working; additive for svgBlip + Graphics-Format routing.
- **Rough size:** S (already works; polish only) • **Dependencies:** rides the `image` node + media-part exporter; shares the Picture Format machinery.

## Open questions for our discussion
- Keep the app's Fluent SVG set as "Icons", or invest in a larger bundled icon library closer to Word's category breadth?
- Worth the additive `asvg:svgBlip` dual-blip for true Word-SVG fidelity, or is a plain SVG image good enough?
- Add a distinct **Graphics Format** contextual tab for SVGs, or is Picture Format an acceptable fallback (today's behavior)?
- Build "Convert to Shape" (icon → `vectorShape` freeform), or out of scope for v1?

## Decision
**TBD — to be decided together.**

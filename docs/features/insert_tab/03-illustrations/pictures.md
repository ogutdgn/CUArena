# Pictures (This Device / Stock / Online) — Insert > Illustrations

## What real Word does
Pictures is a menu/split button with three sources: **This Device** (the standard
"Insert Picture" file-open dialog — Insert vs "Insert and Link" vs "Link to File"),
**Stock Images** (the Office Content picker: Images / Icons / Cutout People / Stickers /
Illustrations / Cartoon People with search + multi-select), and **Online Pictures** (a
Bing image-search dialog with a Creative-Commons filter + OneDrive). All three embed a
DrawingML picture: `w:drawing > wp:inline` (in-line default) or `wp:anchor` (floating) >
`a:graphic > a:graphicData uri=.../picture > pic:pic > pic:blipFill > a:blip r:embed=rId`
→ a media part in `word/media/imageN.ext`. SVG sources carry an `a:extLst/asvg:svgBlip`
plus a rasterized PNG fallback. Selecting a raster picture raises the **Picture Format**
contextual tab (Adjust / Picture Styles / Accessibility / Arrange / Size). KeyTips Alt, N, P.

## Current clone state
**shallow** — "This Device" genuinely inserts; the other two sources are missing/degraded.
`H.pictures` (`src/renderer/public/js/commands.js:392`) awaits `window.wordAPI.pickImage()`
→ `insertPictureFromDataUrl` → `WC.PM.insertImage` → `insert.ts:45`
`editor.chain().setImage().run()` — a real document mutation. The flyout `picturesMenu`
(`commands.js:490`) offers only "This Device" + "Online Pictures"; **Online Pictures**
(`xeOnlinePicture`, `insert-exotica.ts:167`) toasts then falls back to the *local* file
picker (no web backend), and **Stock Images** is absent from the menu entirely. The
inserted picture is a real `image` node that round-trips (`extensions/image/`).

## Can we build it in our engine?
**Verdict:** ✅ Already works (This Device) / 🟡 Buildable with additive fork edits (Stock + Online faithfulness)
**Why:** The hard part already exists. The `image` node (`extensions/image/image.js`) is
registered, `insertImage` (`bridge/insert.ts:45`) mutates the doc, and the export path
(`encode-image-node-helpers.js` → `pic:pic`/`a:blip` + a media part in `word/media/`) is a
mature, tested handler — local pictures round-trip to real Word OOXML. "This Device" is
done. **Stock Images** and **Online Pictures** are not engine gaps — they are *content-source*
gaps: there is no Office Content store or Bing backend, and we cannot ship Microsoft's
licensed stock library. Both can be made to insert real pictures (the engine accepts any
data-URL), but "faithful Stock/Online" means a non-Office image source of our choosing.
SVG sources (icons/illustrations) already insert as images today but **as plain raster/SVG
images, not as `asvg:svgBlip` dual-blip** — adding the svgBlip extension is an additive
encoder change if we want true Word-SVG fidelity.

## Required structures to build it
- **PM node/extension:** reuse `image` (`extensions/image/image.js`) — no new node.
- **Converter handler (super-converter):** exists — import `decode-image-node-helpers.js`,
  export `encode-image-node-helpers.js` (emits `wp:inline > pic:pic > a:blip` + media part).
  Additive: an `asvg:svgBlip`/PNG-fallback branch for true SVG fidelity.
- **OOXML target:** `w:drawing/wp:inline(or wp:anchor)/a:graphic/a:graphicData(.../picture)/pic:pic/pic:blipFill/a:blip r:embed` → `word/media/imageN.*`.
- **Bridge verb(s):** `WC.PM.insertImage` (exists). For Stock/Online: a `WC.Insert.stockPicker`/`onlinePicker` UI that resolves a data-URL then calls the SAME `insertImage`.
- **Fork edit?** none for This Device; additive only for true svgBlip dual-encoding.
- **Rough size:** S (wire Stock/Online UI to the existing verb) • **Dependencies:** none — rides the existing `image` node + media-part exporter.

## Open questions for our discussion
- Stock Images: build our own royalty-free gallery (e.g. bundle a curated icon/illustration set), point at an open API, or remove "Stock Images" from the menu as honestly unavailable?
- Online Pictures: wire a real web image search (which provider?), or keep the honest "pick a local image instead" degrade?
- Do we care about true `asvg:svgBlip` dual-blip fidelity for SVG sources, or is inserting the SVG as a plain image acceptable for v1?
- "Link to File" / "Insert and Link" (external `a:blip r:link`) — build or skip?

## Decision
**TBD — to be decided together.**

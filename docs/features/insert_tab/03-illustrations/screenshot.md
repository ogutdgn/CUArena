# Screenshot — Insert > Illustrations

## What real Word does
Screenshot is a gallery button. The top shows live thumbnails of **Available Windows** (each
non-minimized window); clicking one inserts a full-window screenshot. Below is **Screen
Clipping**, which minimizes Word, dims the screen, and lets you drag a rectangle to capture
any region; the clip is inserted at the caret. Either way the result is a normal raster
picture — `w:drawing > wp:inline > a:graphic > a:graphicData(.../picture) > pic:pic >
pic:blipFill > a:blip r:embed` → a PNG in `word/media/imageN.png` — and selecting it raises
the **Picture Format** contextual tab. KeyTips Alt, N, SC.

## Current clone state
**shallow/working** — the capture backend is real: `insert:screenshot`
(`src/main/main.js:529`) minimizes the window, uses Electron's `desktopCapturer.getSources({
types:['screen'] })`, and returns `{ ok, dataUrl }` (a real PNG data-URL); it is exposed via
`preload.js:44` as `wordAPI.screenshot()`. The bridge verb `xeScreenshot`
(`bridge/insert-exotica.ts:151`) calls it and inserts the result via
`pm().insertImage({ src: r.dataUrl, alt: 'Screenshot' })` — a genuine `image`-node mutation
that round-trips. The grounding notes flag `xeScreenshot` as a "reserve/test verb" not wired
to a live ribbon path, and it captures the **whole primary screen** (one source), not Word's
per-window gallery or a drag-to-clip rectangle.

## Can we build it in our engine?
**Verdict:** ✅ Buildable NO-FORK
**Why:** Every engine piece exists and needs no fork edit. The main process already captures
the screen (`desktopCapturer`, `main.js:529`), the preload bridges it
(`wordAPI.screenshot`), and `insertImage` (`bridge/insert.ts:45`) inserts the PNG as an
`image` node that exports to real `pic:pic`/`a:blip` + a media part. The remaining work is
entirely renderer/main wiring, NOT the document engine: (1) **Available Windows gallery** —
call `desktopCapturer.getSources({ types:['window'] })` and render the per-window thumbnails
in the Screenshot flyout; (2) **Screen Clipping** — capture the screen then let the user drag
a crop rectangle (an overlay) and crop the PNG before insert. Both are pure UI + an IPC tweak;
the insert + export path is done and proven.

## Required structures to build it
- **PM node/extension:** reuse `image` (`extensions/image/`) — no new node.
- **Converter handler (super-converter):** exists (`encode-image-node-helpers.js` → `pic:pic`/`a:blip` + media part).
- **OOXML target:** `w:drawing/wp:inline/a:graphic/a:graphicData(.../picture)/pic:pic/pic:blipFill/a:blip r:embed` → `word/media/imageN.png`.
- **Bridge verb(s):** `WC.PM.xeScreenshot` (exists) → wire to a live Screenshot flyout; add a windows-gallery + crop step in the renderer; extend `insert:screenshot` to enumerate `'window'` sources.
- **Fork edit?** none (NO-FORK) — renderer + main-process wiring only.
- **Rough size:** M (windows gallery + screen-clipping crop overlay; the capture + insert + export already work) • **Dependencies:** rides the existing `image` node, `insertImage`, and the `desktopCapturer` IPC.

## Open questions for our discussion
- Build the full Word experience (per-window thumbnail gallery + drag-to-clip Screen Clipping), or ship the simpler "capture whole screen → insert" that already exists behind `xeScreenshot`?
- The verb isn't wired to a live ribbon flyout today — confirm we want Screenshot promoted to a real, visible control.
- Screen Clipping needs a drag-crop overlay across the whole desktop — acceptable to dim/overlay outside the app window, or keep it app-window-only?

## Decision
**TBD — to be decided together.**

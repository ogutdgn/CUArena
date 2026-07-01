# Online Video — Insert > Media

## What real Word does
Insert tab > **Media** group > **Online Videos** (a single push button, `idMso='InsertVideoOnline'`; the Media group has exactly this one control in current Word for Windows, M365 build 16.0). It opens a modal dialog *"Enter the address for the online video"* with one address field + **Insert**/**Cancel**. The field accepts either a supported provider watch URL (YouTube, Vimeo, SlideShare, TED, plus SharePoint / OneDrive for Business) **or** a pasted `<iframe …>` embed-code snippet — Word parses both.

On Insert, Word contacts the provider, fetches a **poster/thumbnail raster** image (saved as a normal `word/media/imageN.png` part) and the provider's oEmbed/iframe embed code, then inserts an **inline picture** of the poster overlaid with a circular Play glyph. The drawing is a standard `w:drawing > wp:inline > a:graphic > a:graphicData(uri=picture) > pic:pic`, where:
- `pic:blipFill > a:blip r:embed='rIdPoster'` references the poster image part;
- `wp:docPr > a:hlinkClick r:id` (and a mirrored `pic:cNvPr > a:hlinkClick`) points at the watch URL via an **External** relationship (`TargetMode='External'`);
- the live-video payload lives in a **blip extension**: `a:blip > a:extLst > a:ext uri="{web-video GUID}" > wp15:webVideoPr embeddedHtml='<iframe …>' h='…' w='…'` (namespace `wp15 = http://schemas.microsoft.com/office/word/2012/wordprocessingDrawing`, type `CT_WebVideoPr`).

Clicking the Play glyph (online) swaps the static poster for an in-document playback surface that renders the stored `wp15:webVideoPr/@embeddedHtml` iframe — a runtime behavior, not a document mutation. Because the rest state is a picture, selecting it raises **Picture Format** (Picture Tools), not a PowerPoint-style Video/Playback tab. Changing wrap to a floating mode rewrites the drawing as `wp:anchor` while keeping the same `pic:pic + a:blip + wp15:webVideoPr` payload.

## Current clone state
**shallow** — The picker UI is complete and reaches a real bridge verb that mutates the document, but the result is a placeholder poster image, NOT Word's playable web embed. Trace: `ribbon-data.js:707` → `commands.js:445` `H.onlineVideo` → `insert-features.js:314` `onlineVideoDialog` (one URL field through `WC.safeUrl`) → `insert-features.js:326` `insertVideoThumbnail` builds a self-contained SVG poster data-URL (red play button + host + truncated URL) → `commands.js:375` `insertPictureFromDataUrl` → `bridge/insert.ts:45` `insertImage` runs a real `editor.chain().setImage({src,alt,rId,size}).run()` with a valid bridge `rId`. The URL is kept only as the image `alt` (`'Online video: '+u`); there is no hyperlink and no `webVideoPr`. The honest-link verb `xeOnlineVideo` (`bridge/insert-exotica.ts:186`, calls `PM.insertLink`) exists but is **not** on the live path. Selecting the result correctly surfaces Picture Tools (`state-sync.ts:284`). Docs are honest (`INSERT_TAB.md:32`, `NOT_IMPLEMENTED.md:236`).

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits

**Why:** The rest state — an inline picture (poster) carrying an external hyperlink to the watch URL — is **already fully supported**. The `image` node has a `hyperlink` attr (`extensions/image/image.js:369`) that round-trips a real `a:hlinkClick` with `TargetMode='External'` in both directions (`decode-image-node-helpers.js:80/218` encode, `encode-image-node-helpers.js:401` decode). So a *clickable poster that opens the video in a browser* is achievable NO-FORK except for two small bridge additions. **What is missing is the live-embed payload:** `grep` for `webVideoPr`/`wp15`/`embeddedHtml` across the entire fork returns **zero hits** — there is no parser/serializer for the `a:blip > a:extLst > a:ext > wp15:webVideoPr` extension. Adding faithful round-trip of the poster+hyperlink+`webVideoPr` triplet means an **additive** edit to the image encode/decode helpers (the `a:extLst` build path already exists there for the decorative ext, so this is a sibling case — low risk). True **in-document playback** (rendering the iframe) is a separate, sandbox-blocked concern (see Open questions); the document-fidelity goal does not require it.

## Required structures to build it
- **PM node/extension:** reuse `image` (`extensions/image/image.js`). Reuse the existing `hyperlink` attr; add one new attr `webVideo` (e.g. `{ embeddedHtml, w, h }`, `rendered:false`) to carry the embed payload across import/export. Optionally render a Play-glyph overlay in `renderDOM` so the poster looks like Word's.
- **Converter handler (super-converter):** exists for the hyperlink leg at `core/super-converter/v3/handlers/wp/helpers/decode-image-node-helpers.js` (encode) and `encode-image-node-helpers.js` (decode). **Add** a `wp15:webVideoPr` read/write in those same two files — emit it inside `a:blip > a:extLst > a:ext uri="{GUID}"` on export, parse it back on import (mirror the existing decorative-ext pattern at `decode-image-node-helpers.js:114`). Register the `wp15` namespace + the `CT_WebVideoPr` GUID.
- **OOXML target:** `wp:inline > a:graphic > pic:pic` with `wp:docPr/pic:cNvPr > a:hlinkClick` (`TargetMode='External'`) **and** `pic:blipFill > a:blip > a:extLst > a:ext > wp15:webVideoPr embeddedHtml/h/w`.
- **Bridge verb(s):** add `hyperlink` (and optional `webVideo`) passthrough to `WC.PM.insertImage` / its `setImage` call (`bridge/insert.ts:99`) — or add a thin `insertOnlineVideo({url, posterSrc, embedHtml})` wrapper; repoint `H.onlineVideo`'s live path to set the poster's hyperlink instead of stashing the URL in `alt`. A real provider poster requires a fetch (CSP `img-src` currently blocks remote hosts) — keep the self-contained SVG poster to stay offline-safe, or relax CSP/proxy through main.
- **Fork edit?** additive (new image attr + new `webVideoPr` encode/decode branch beside the existing decorative-ext code — no signature breakage)
- **Rough size:** **M** • **Dependencies:** rides the existing `image` node + image hyperlink round-trip; poster fetch/CSP is the only external snag

## Open questions for our discussion
- **Fidelity target:** ship the *clickable-poster-with-external-hyperlink* (achievable cheaply, opens the video in the user's browser) as the v1 — or invest the additive fork edit to round-trip the full `wp15:webVideoPr` so a re-opened doc in real Word still plays in-document?
- **Live playback:** the Electron app sandbox/CSP blocks rendering remote iframes inline. Do we want in-app playback at all (relax CSP / open an external window), or is "click opens browser" acceptable, matching the document-fidelity goal without the security surface?
- **Provider poster vs SVG placeholder:** fetching the real thumbnail needs a network call + CSP `img-src` relaxation (or a main-process proxy). Keep the offline-safe synthetic SVG poster, or add the fetch?
- **Embed-code input:** support pasting a raw `<iframe>` snippet (Word's second flow) in the dialog, or URL-only?

## Decision
**TBD — to be decided together.**

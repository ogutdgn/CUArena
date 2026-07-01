# Insert > Media — feasibility group index

The **Media** group on the Insert tab has exactly **one** control in current Word for Windows (M365, build 16.0): **Online Videos**. (Word's separate *Pictures* and *Shapes/Icons/3D Models* sit in the **Illustrations** group, not Media.)

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Online Video](./online-video.md) | 🟡 Buildable with additive fork edits | M | Reuse `image` node + its existing external-`a:hlinkClick` hyperlink round-trip; **add** a `wp15:webVideoPr` (`a:blip > a:extLst > a:ext`) encode/decode branch in the image converter helpers + a `webVideo`/`hyperlink` passthrough on `WC.PM.insertImage`. |

## Legend
- ✅ Already works · ✅ Buildable NO-FORK · 🟡 Buildable with additive fork edits · 🔴 Needs a NEW subsystem/engine · ⛔ Needs an external runtime we don't have

## Key engine facts that drove these verdicts
- **`image` node** (`src/renderer/core/superdoc-fork/extensions/image/image.js`) already has a `hyperlink` attr (line 369) that round-trips a real external `a:hlinkClick` (`TargetMode='External'`) — encode in `decode-image-node-helpers.js`, decode in `encode-image-node-helpers.js`. So a clickable poster is nearly free.
- **`wp15:webVideoPr` is ABSENT** — `grep` for `webVideoPr`/`wp15`/`embeddedHtml` across the whole fork returns zero hits. Full Word-fidelity round-trip of the live-embed payload needs an additive branch in the image converter helpers (the `a:extLst` build path already exists there for the decorative ext, so it's a sibling case).
- **Live in-document playback** (rendering the provider iframe) is blocked by the app's CSP/sandbox and is treated as out of scope for document fidelity — open question for the user.

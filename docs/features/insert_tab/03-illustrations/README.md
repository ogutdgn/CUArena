# Insert > Illustrations — feasibility index

Button-by-button build/keep/remove feasibility for the **Insert > Illustrations** ribbon
group, grounded in what the SuperDoc-fork engine (`src/renderer/core/superdoc-fork/`) and the
`WC.PM` bridge (`src/renderer/bridge/`) actually support. Each row links to its detail doc.

| Button | Verdict | Size | Required structure (one line) |
|--------|---------|------|-------------------------------|
| [Pictures](pictures.md) | ✅ Already works (This Device) / 🟡 additive for Stock+Online | S | Reuse `image` node + `insertImage` + `encode-image-node-helpers` (works); Stock/Online need a content source, not engine work |
| [Shapes](shapes.md) | 🟡 Buildable with additive fork edits | L | Add `insertAutoShape(prst)` on the existing `vectorShape` node (mirrors `insertWordArt`); export already replays `drawingContent` |
| [Icons](icons.md) | ✅ Already works | S | Reuse `image` node + `xeIcon` → `insertImage` (works today as SVG image); svgBlip/Graphics-Format are polish |
| [3D Models](3d-models.md) | ⛔ Needs an external runtime we don't have | XL | No `model3d` node / `am3d:model3D` handler; needs a WebGL/glTF viewport outside the document engine |
| [SmartArt](smartart.md) | 🔴 Needs a NEW subsystem/engine | XL (true `dgm`) / M (degraded) | No diagram node / `dgm` handler; true SmartArt = 4-part `dgm` package + a layout engine. Degraded path reuses Shapes/`shapeGroup` |
| [Chart](chart.md) | 🟡 Buildable with additive fork edits | L | `chart` node + `parseChartXml` import + `originalXml` export-replay already exist; add a `synthesizeChartXml(type,data)` create path |
| [Screenshot](screenshot.md) | ✅ Buildable NO-FORK | M | `desktopCapturer` IPC + `xeScreenshot` + `insertImage` exist; only the windows-gallery + clip-crop UI is missing |

## Headline findings (verify vs. the repo grounding)

- The repo grounding (bridge-level) under-states the engine. The fork **already registers
  real `chart`, `vectorShape`, `shapeContainer`, `shapeTextbox`, `shapeGroup` nodes**
  (`extensions/index.js:217-231`) with import handlers and an export router
  (`exporter.js:235-240`). Shapes and Chart are therefore **additive**, not new subsystems —
  the stub toasts hide a working substrate.
- **Already real / round-trips:** Pictures (This Device), Icons, Screenshot (capture +
  insert), and chart **import** all genuinely mutate the document and export to real OOXML.
- **Additive-fork (engine substrate present):** Shapes (auto-shape `prstGeom` insert on
  `vectorShape`) and Chart (a `synthesizeChartXml` create path feeding the existing
  `chart` node + replay exporter).
- **Genuinely hard:** SmartArt (no `dgm` node/handler + needs a diagram layout engine) and
  3D Models (no node/handler + needs a WebGL runtime the engine deliberately lacks).
- **Contextual tabs:** only **Picture Format** exists (`picture-tools-pm.js`, driven by
  `state-sync.ts:282-285`), and it also serves inserted Icons. Shape Format / Graphics Format
  / SmartArt Design+Format / Chart Design+Format are all absent and would be built alongside
  their respective insert features.

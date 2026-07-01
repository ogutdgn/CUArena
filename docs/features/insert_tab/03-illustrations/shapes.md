# Shapes — Insert > Illustrations

## What real Word does
Shapes is a gallery dropdown (Recently Used / Lines / Rectangles / Basic Shapes / Block
Arrows / Equation Shapes / Flowchart / Stars and Banners / Callouts, plus "New Drawing
Canvas"). Picking a shape gives a crosshair; click-drag draws it (Shift constrains, Ctrl
draws from center). Shapes are **floating by default**, support right-click → Add Text, and
raise the **Shape Format** contextual tab (Insert Shapes / Shape Styles / WordArt Styles /
Text / Arrange / Size). Each preset is a DrawingML auto-shape: `w:drawing` (wrapped in
`mc:AlternateContent/mc:Choice Requires="wps"`) > `a:graphic > a:graphicData
uri=.../wordprocessingShape > wps:wsp` with `wps:spPr/a:prstGeom prst="<preset>"` (e.g.
`rect`, `roundRect`, `ellipse`, `triangle`, `rightArrow`, `star5`, `flowChartProcess`,
`wedgeRectCallout`). Freeform/curve use `a:custGeom/a:path`; the canvas is `wpc:wpc`. KeyTips Alt, N, S, H.

## Current clone state
**stub** (the gallery) — `WC.Insert.shapesMenu` (`src/renderer/public/js/insert-features.js:104`)
renders a full categorized SVG shape gallery, but clicking any shape calls
`Insert.insertShape` (`insert-features.js:118`), which is a `WC.toast("…isn't available on
the new engine yet")` — **no bridge verb, no mutation**. There is no `xeShape` verb.
**However the engine substrate exists:** the `vectorShape` node
(`extensions/vector-shape/vector-shape.js`) is registered and already synthesizes real
`wps:wsp` DrawingML for WordArt (`insertWordArt`) and `a:custGeom` for ink (`insertInkShape`),
and the export router maps `vectorShape → translateVectorShape` (`exporter.js:238`). The
shape *node + export pipe* are present; only an **auto-shape `prstGeom` insert command +
gallery wiring** is missing.

## Can we build it in our engine?
**Verdict:** 🟡 Buildable with additive fork edits
**Why:** This is much closer than the stub implies. The `vectorShape` node is registered and
already round-trips synthesized DrawingML — `synthesizeWordArtDrawing` (`vector-shape.js:14`)
emits a full `wps:wsp` blob (xfrm + prstGeom `rect` + bodyPr) and `translateVectorShape`
(`decode-image-node-helpers.js`) replays `drawingContent` verbatim, so it survives the
round-trip through Word AND the fork. Adding the Shapes gallery is a NEW
`insertAutoShape({ prst, w, h, fill, stroke })` command that mirrors `synthesizeWordArtDrawing`
but swaps `a:prstGeom prst="rect"` for the chosen preset and drops the txbx — an **additive**
fork-source edit (a new command on an existing extension, the exact pattern the WordArt/ink
commands already established). Import already exists: a `wps:wsp` drawing decodes to a
`vectorShape`. The in-app *paint* of arbitrary presets is the real work — `VectorShapeView`
renders a finite SVG set today and would need geometry for the ~160 presets (or a generic
fallback). NOT a no-fork job, but it is additive and well-precedented, not a new subsystem.

## Required structures to build it
- **PM node/extension:** reuse `vectorShape` (`extensions/vector-shape/`). Add an `insertAutoShape` command alongside `insertWordArt`/`insertInkShape`; extend `VectorShapeView.js` with per-`prst` SVG geometry (or a generic placeholder).
- **Converter handler (super-converter):** export exists (`translateVectorShape` replays `drawingContent`); import exists (`wps:wsp` → `vectorShape` in `encode-image-node-helpers.js`). No new handler — the synthesized `drawingContent` rides the existing replay.
- **OOXML target:** `wps:wsp` with `wps:spPr/a:prstGeom prst="<preset>"` inside `a:graphicData uri=.../wordprocessingShape`; freeform via `a:custGeom`.
- **Bridge verb(s):** add `WC.PM.xeShape(prst)` / `insertAutoShape`; rewire `Insert.insertShape` (`insert-features.js:118`) off the toast.
- **Fork edit?** additive (new command on `vectorShape` + view geometry; no schema break).
- **Rough size:** L (one preset = M; the full gallery + faithful per-preset geometry + Shape Format tab = L) • **Dependencies:** the Shape Format contextual tab (Arrange/Size) reuses the Picture Format/state-sync machinery; the same engine powers WordArt + ink.

## Open questions for our discussion
- Scope: ship a small high-value preset set (rect / roundRect / ellipse / line / arrows / star) first, or aim for the full ~160-preset gallery?
- In-app rendering: author exact per-preset SVG geometry (faithful) vs. a generic bounding-box placeholder that still exports the correct `prstGeom` (export-faithful, paint-approximate)?
- Floating-by-default (`wp:anchor`) drag-to-draw vs. inline insert at the caret for v1?
- Build the Shape Format contextual tab now, or insert-only first and defer formatting?
- "Add Text" inside a shape (`wps:txbx/w:txbxContent`) — in scope, or shapes-without-text for v1?

## Decision
**TBD — to be decided together.**

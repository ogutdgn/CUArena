# SmartArt — Insert > Illustrations

## What real Word does
SmartArt opens the "Choose a SmartArt Graphic" dialog (category list: All / List / Process /
Cycle / Hierarchy / Relationship / Matrix / Pyramid / Picture / Office.com / Other; a
thumbnail grid; a preview + description pane). Picking a layout + OK inserts a diagram with a
"Type your text here" text pane and raises **two** contextual tabs: **SmartArt Design**
(Create Graphic: Add Shape/Bullet/Promote/Demote/Move/Text Pane; Layouts gallery; SmartArt
Styles + Change Colors; Reset/Convert) and **Format** (Shapes / Shape Styles / WordArt Styles
/ Arrange / Size). The diagram is a `graphicFrame`: `a:graphicData
uri=.../diagram > dgm:relIds` referencing **four parts** — `diagrams/data1.xml`
(`dgm:dataModel` with `dgm:pt` points + `dgm:cxn` connections), `layout1.xml`
(`dgm:layoutDef`), `colors1.xml`, `quickStyle1.xml` — plus a `diagrams/drawing1.xml`
(`dsp:drawing`) presentation fallback. KeyTips Alt, N, M.

## Current clone state
**stub** — `H.smartart` (`commands.js:440`) → `WC.Insert.smartArtMenu`
(`insert-features.js:146`) lists List/Process/Cycle/Hierarchy; clicking calls
`Insert.insertSmartArt(kind)` (`insert-features.js:150`) → `WC.PM.xeSmartArt()`. That verb
(`bridge/insert-exotica.ts:207`) is purely `toast("SmartArt (dgm: diagrams) needs a diagram
subsystem — available in a future update."); return true` — no mutation, the `kind` arg is
discarded. No SmartArt node, no `dgm` handler, no SmartArt Design/Format tabs exist anywhere
in `src/renderer` (all grep to zero hits).

## Can we build it in our engine?
**Verdict:** 🔴 Needs a NEW subsystem/engine
**Why:** SmartArt is the heaviest item in the group. There is **no diagram node** in the fork
(`extensions/` has no `diagram`/`smartart`/`dgm` entry) and **no `drawingml/2006/diagram`
import or export handler** (grep finds zero in `super-converter/`). Faithful SmartArt is not
one element — it is a four-part diagram package (`dgm:dataModel`, `dgm:layoutDef`, colors,
quickStyle) PLUS a layout *engine* that turns a node/connection data model + a layout
definition into positioned shapes (the `dsp:drawing` presentation). That layout engine — the
algorithm that arranges a List/Process/Cycle/Hierarchy from data — is an entire subsystem we
do not have and that has no analogue in the paged renderer. A *degraded* path exists: build
the diagram out of our existing `vectorShape` auto-shapes (once the Shapes auto-shape command
lands) — i.e. emit a group of `wps:wsp` boxes + connector lines positioned by a small layout
helper, with NO `dgm` parts. That inserts an editable shape diagram but Word would NOT see it
as SmartArt (no "Convert to Text", no live re-layout, no SmartArt tabs). True `dgm` SmartArt
is a new subsystem.

## Required structures to build it
- **PM node/extension:** NEW `smartArt`/`diagram` node (graphicFrame) — does not exist. (Degraded path reuses `vectorShape` + `shapeGroup`.)
- **Converter handler (super-converter):** NEW import/export for `a:graphicData(.../diagram)/dgm:relIds` + the four `diagrams/*.xml` parts — does not exist. (Degraded path rides the existing `translateVectorShape`/`translateShapeGroup`.)
- **OOXML target:** `dgm:relIds` → `diagrams/data1.xml` (`dgm:dataModel`) / `layout1.xml` (`dgm:layoutDef`) / `colors1.xml` / `quickStyle1.xml` + `drawing1.xml` (`dsp:drawing`).
- **Bridge verb(s):** replace toast `xeSmartArt` with a real `insertSmartArt(layout, data)`; add the layout-engine helper.
- **Fork edit?** large/non-additive (new node + new multi-part handler + a layout engine).
- **Rough size:** XL (true `dgm`) / M (degraded shape-group diagram, depends on Shapes landing) • **Dependencies:** the degraded path rides the **Shapes** auto-shape engine + `shapeGroup`.

## Open questions for our discussion
- Faithful `dgm` SmartArt (XL: new node + 4-part handler + a layout engine) vs. a **degraded shape-group diagram** (M, reuses Shapes/`vectorShape`/`shapeGroup`) that looks right and is editable but is NOT real SmartArt to Word?
- If degraded: acceptable that round-trips lose "SmartArt-ness" (no live re-layout, no Convert-to-Text, no SmartArt tabs)?
- Which layouts matter (Word ships dozens)? A handful — Basic List / Basic Process / Basic Cycle / Org Chart — covers most real use.
- Keep the honest stub for v1 and revisit after Shapes lands (degraded path depends on it)?

## Decision
**TBD — to be decided together.**

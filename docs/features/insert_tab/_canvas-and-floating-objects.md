# The page as a canvas — floating-object layer (keystone investigation)

> Status: **investigation / spec**. Verdict at the bottom is **🟡 partial — strong
> engine, thin authoring UI**. All claims are grounded in `file:line` against the repo
> as of 2026-06-27 (`main`). This is the keystone that decides whether Shapes, Cover
> Page, Text Box, floating Pictures, WordArt, and floating/movable Tables are feasible.

## Why this matters (the keystone)

In Word, a page is not just a column of text — it is a **canvas**. Several Insert-tab
features are nothing more than "put an object on the canvas and let the user move it,
with text wrapping around it":

- **Shapes** — preset-geometry boxes/lines/arrows anchored anywhere on the page.
- **Cover Page** — a pre-composed layout of *floating* text boxes / shapes / images.
- **Text Box** — a floating, movable, text-bearing rectangle.
- **Pictures** (floating mode) — the "With Text Wrapping" / "In Front of / Behind
  Text" variants of an inserted image.
- **WordArt** — a floating shape whose text has fill/warp effects.
- **Floating / movable Tables** — a table pulled out of the text flow (`w:tblpPr`).

Every one of these rides the same substrate: a **floating-object layer** that (1) carries
position + wrap in the model, (2) round-trips it through OOXML, (3) **paints** the object
at an absolute page position, and (4) **reflows** body text around it. If that substrate
is solid, the features above are mostly "wire up a node + UI". If it is missing, every one
of them degrades to inline or a stub. So this document audits the substrate, not the
individual features.

## What real Word does (the canvas model)

A Word page has two layers:

1. **Inline text-flow layer** — runs and paragraphs flowing top-to-bottom. Inline
   drawings (`<wp:inline>`) sit in this flow like a big character.
2. **Floating-object layer** — drawings with `<wp:anchor>`. Each anchor carries:
   - **Position:** `<wp:positionH relativeFrom="...">` + `<wp:positionV relativeFrom="...">`,
     each with either a `<wp:posOffset>` (EMU offset) or a `<wp:align>` preset
     (left/center/right · top/center/bottom). `relativeFrom` can be page / margin /
     column / paragraph / character / line.
   - **Wrap:** one of `wp:wrapSquare`, `wp:wrapTight`, `wp:wrapThrough`,
     `wp:wrapTopAndBottom`, or `wp:wrapNone` (+ `behindDoc` = behind vs. in front of text).
   - **Stacking:** `relativeHeight` (z-order) and `behindDoc`.

The user can grab any floating object and drag it to an arbitrary point; body text
**reflows** around it according to the wrap mode (square = bounding box; tight/through =
the object's polygon; top-and-bottom = full-width gap; none = overlap). Tables get the
same treatment via `w:tblpPr` (`tblpX/tblpY`, `horzAnchor/vertAnchor`, `*FromText`).

## What our engine supports today

### 1. Floating vs inline in the converter — ✅ FULL round-trip (both directions)

The super-converter imports **and** exports real floating anchors, not just inline.

- **Export (PM → OOXML):** `translateAnchorNode` builds a `<wp:anchor>` with
  `<wp:simplePos>`, `<wp:positionH relativeFrom>`/`<wp:positionV relativeFrom>` carrying
  either `<wp:posOffset>` (from `marginOffset`, px→EMU) or `<wp:align>` (from
  `anchorData.alignH/alignV`), and a wrap element selected by `attrs.wrap.type`.
  - `src/renderer/core/superdoc-fork/core/super-converter/v3/handlers/wp/anchor/helpers/translate-anchor-node.js:31-70` (positionH/V + offset/align),
    `:116-196` (wrap element: Square/TopAndBottom/Through/Tight with `distT/B/L/R` + polygon, and None→`behindDoc`).
  - It even fills the CT_Anchor required attrs (`distT/B/L/R`, `simplePos`, `locked`,
    `layoutInCell`, `allowOverlap`, `behindDoc`) with Word defaults so a freshly-generated
    anchor (inline→floating toggle) opens in Word — `:103-114`. And it forces
    `@simplePos='0'` for complex positioning — `:94-101` (a real oracle-confirmed bug fix).
  - Handler entry: `.../wp/anchor/helpers/handle-anchor-node.js:8-16` →
    `handleImageNode(node, params, true)`.
- **Import (OOXML → PM):** `encode-image-node-helpers.js` parses the anchor back into the
  model: `wp:positionH`/`wp:posOffset`/`relativeFrom`/`wp:align` →
  `marginOffset` + `anchorData`
  (`.../wp/helpers/encode-image-node-helpers.js:175-189, 269-299`), and all five wrap
  elements (`wp:wrapNone/Square/Through/Tight/TopAndBottom`) + `behindDoc` → `wrap`
  (`:197-258`).

**Conclusion:** the OOXML floating model (position offsets + relativeFrom + all five wrap
types + behindDoc + z-order) round-trips losslessly for drawings. This is the strongest
part of the stack.

### 2. The frames / position bridge (Phase-4 "frames", feature 012) — 🟡 images-only, free X/Y, presets partial

All Arrange verbs live in `src/renderer/bridge/insert.ts` and are **gated to a selected
`image` node** by `selectedImage()` (`insert.ts:273-277` — returns null unless
`sel.node.type.name === 'image'`). There is no shape/textbox/table positioning path.

- **`setImagePosition({horizontal, top, relative})`** — `insert.ts:600-628`. Writes a
  **free, arbitrary X/Y offset** as `marginOffset:{horizontal, top}` (px, → `wp:posOffset`
  EMU). `relative:true` nudges; otherwise absolute. Seeds `anchorData` if absent.
  - Requires an already-floating picture (`if (!isAnchor) … bail`, `:603`).
  - **Honesty caveat:** refuses to reposition an *imported* `.docx` picture when
    `originalDrawingChildren` is present (`:609-612`), because the exporter prefers the
    verbatim imported children, so a new offset would move on screen but **be dropped on
    save**. Faithful repositioning is therefore session-inserted floats only.
- **`setImageTransform({rotate, flipH, flipV, reset})`** — `insert.ts:539-568`. Writes
  `transformData:{rotation, horizontalFlip, verticalFlip}` → `a:xfrm rot/flipH/flipV`.
  Rotation is a relative delta mod-360; flips toggle. **No scale** here (pixel resize is the
  separate `setImageSize`, `:442-479` → `wp:extent`).
- **`setImageAlign({h})`** — `insert.ts:636-648`. Horizontal preset **only** (`left/center/right`);
  computes a column-relative offset from page geometry and **delegates to
  `setImagePosition`**. **Vertical align (top/middle/bottom) is not implemented** —
  documented v1 follow-up (`:635`); the ribbon's vertical cells are toast stubs.
- **`setImageWrap(mode)`** — `insert.ts:324-372`. **This is the wrap-mode selector**, and it
  is complete: `inline / square / tight / through / topbottom / behind / front` →
  `wrap:{type,attrs}` + flips `isAnchor`, seeds `anchorData`+zero `marginOffset` for floats,
  injects a default bounding-box `wrapPolygon` for Tight/Through (`:342-347`, required or
  Word rejects the file). This is the one function that toggles inline↔floating.
- **`setImageZOrder`** — writes `relativeHeight`; but the comment is honest that z-index only
  re-stacks **absolute** (wrap=None) images — CSS-floated Square/Tight/Through images stack by
  document order regardless (`insert.ts:374-380`).
- Ribbon wiring (all `src/renderer/public/js/commands.js`): `H.position` (`:1154`),
  `H.wrapText` (`:1155`, 7 modes), `H.align` (`:1177-1181`, horizontal real / vertical+distribute
  = toast), `H.rotate`/`H.imgRotate` (`:1185`,`:307-316`), `H.imgPosition` (`:329-353`, the
  free inches X/Y flyout), `H.bringForward`/`H.sendBackward` (z-order), `H.group` (`:1182`,
  toast stub).

**Conclusion:** a session-inserted **picture** can be made floating, wrapped (all 7 modes),
moved to a free X/Y, aligned horizontally, rotated, flipped, and z-ordered — and it
exports correctly. It is **images-only**; shapes/textboxes/wordart/tables have **no**
Arrange path. Vertical-align, Group, and imported-anchor reposition are gaps.

### 3. Shape model (vectorShape / shape-textbox / WordArt / Text Box) — 🟡 nodes exist & round-trip; authoring is inline-only or stubbed

Four real ProseMirror node extensions exist (registered in `extensions/index.js:217-229`),
but the **interactive move/resize layer is image-gated**, so none of these can be moved by
the user after insertion.

- **`vectorShape`** — `extensions/vector-shape/vector-shape.js:150-405`. An **inline atom**
  (`:151-157`) with rich attrs (`kind` rect/roundRect/ellipse/circle/line/connector/custom,
  `fillColor`, `strokeColor`, `customGeometry`, `rotation`, `flipH/V`, `wrap`, `anchorData`,
  `isAnchor`, `marginOffset`, `isWordArt`, `isInk`, `drawingContent` verbatim-OOXML blob). Its
  NodeView absolutely-positions only when `wrap.type==='None'` (`VectorShapeView.js:66-86`).
  Default insert is `wrap:{type:'Inline'}` (`:260`).
- **`shapeTextbox`** / **`shapeContainer`** —
  `extensions/shape-textbox/shape-textbox.js:27-110`,
  `extensions/shape-container/shape-container.js:27-97`. **Block** nodes rendered as plain
  in-flow `<div>`s with **no anchor/position attrs at all** → inline in the text flow.
- **Insert Text Box** — `insertTextBox` (`shape-textbox.js:86-107`), bridge `xeTextBox`
  (`insert-exotica.ts:178-180`), UI `H.textBox` (`commands.js:426`). Inserts a **real editable
  VML text box** (`v:shape type="#_x0000_t202"` → `w:txbxContent`) that round-trips — but it
  is **inline / in flow, not floating, not movable**. (The ribbon tooltip's "positioned
  anywhere on the page", `ribbon-data.js:827`, is aspirational.)
- **Insert WordArt** — `insertWordArt` (`vector-shape.js:350-369`), bridge `xeWordArt`
  (`insert-exotica.ts:181-183`). Targets **real DrawingML `wps:wsp`** with `prstTxWarp`
  via `synthesizeWordArtDrawing` (`vector-shape.js:14-68`) — but inserts with
  `wrap:'Inline'`, `isAnchor` unset → **inline, not movable** (and the warp only renders in
  Word; in-app it's flat text in the SVG NodeView).
- **Insert Shapes (rect/ellipse/line/arrow/…)** — **stub.** The full Word-style gallery
  renders (`insert-features.js:126-147`) but every cell calls `Insert.insertShape`, a pure
  toast: "Inserting … shapes isn't available on the new engine yet." (`insert-features.js:148-152`).
  Note the disconnect: the `vectorShape` model + `VectorShapeView` can already render
  `kind:'rect'|'ellipse'|'line'`, but **no UI verb constructs such a node**, and the preset-SVG
  helper is stubbed (`VectorShapeView.js:1-2`, `getPresetShapeSvg = () => ''`). The only working
  `vectorShape` inserts are WordArt, ink (`draw.ts` `dInsertInk`, anchored), and the Drawing
  Canvas frame (`draw.ts:63-105`, inline).

**Conclusion:** the node model is OOXML-faithful and three of these *insert* from the UI
(Text Box, WordArt, Drawing Canvas), but **all land inline and none are user-movable** —
the move/resize handles are hard-gated to `image` (`imageresize/image-resize.ts:125,303,428`;
bridge verbs via `selectedImage()`). AutoShapes don't insert at all.

### 4. The PresentationEditor (paint) — ✅ TRUE canvas: absolute paint, z-order, AND text reflow

This is the surprising strength. The live paged engine is the real vendored SuperDoc
**layout-engine + painter-dom** (`PresentationEditor.ts` →
`PresentationPainterAdapter.ts` → `@superdoc/painter-dom`). It does **not** paint floats
inline.

- **Absolute placement:** the layout engine resolves anchor data to an absolute `(x,y)`.
  `computeAnchorX` honors `hRelativeFrom` (page/margin/column) + `alignH` + offset
  (`_vendor/superdoc/layout-engine/src/floating-objects.ts:330-381`); anchorY honors
  `vRelativeFrom`/`alignV` (`layout-paragraph.ts:330-392`). It emits an
  `ImageFragment`/`DrawingFragment` with `x`, `y`, `isAnchored:true`, `behindDoc`, `zIndex`
  (`layout-paragraph.ts:424-459`). The painter sets `position:absolute` +
  `left/top = x/y px` (`painter-dom/src/renderer.ts:2694, 3881-3883`;
  `images/image-fragment.ts:95-104`).
- **Text reflow (real):** during paragraph layout each line queries the float manager for
  available width (`layout-paragraph.ts:601` → `floatManager.computeAvailableWidth(...)`); if
  narrower, it **re-measures the whole paragraph at the reduced width**
  (`:617-631`, threaded live at `index.ts:2366`). So body text genuinely wraps around a float.
  - **Scope (honest):** only **rectangular** wrap is implemented — **Square** and
    **TopAndBottom**. **Tight/Through polygon wrap is NOT implemented** (rectangular
    fallback; polygon captured but unused — `floating-objects.ts:12, 147`). `wrap:'None'`
    (Behind / In Front) creates **no exclusion** — text overlaps by design (`:115-119`).
- **Z-order / overlap:** z-index derives from `relativeHeight` (`contracts/src/ooxml-z-index.ts:58-60`);
  `behindDoc` fragments render behind body text (`renderer.ts:2078-2142, 3928-3946`). Two
  objects can overlap and stack.
- **Move/resize interaction:** `imageresize/image-resize.ts` — resize handles commit
  `size` (`:295-312`); **moving** a floating image's body commits a free
  `setImagePosition({horizontal, top})` (`:320, 366, 382`), and the next layout pass
  reflows text (for Square). Inline images can't be body-dragged.

**Conclusion:** the PE is a genuine canvas — it paints anchored objects at absolute page
coordinates, honors z-order/behindDoc, and reflows text around them. The gap is **wrap
fidelity** (rectangular only; no polygon Tight/Through).

### 5. Floating tables (`w:tblpPr`) — 🟡 round-trips AND paints floating, but ZERO authoring UI

- **Converter:** dedicated translator
  `.../super-converter/v3/handlers/w/tblpPr/tblpPr-translator.js` — encode (import) `:15-18`,
  decode (export) `:19-23`, handling `tblpX/Y`, `horzAnchor/vertAnchor`, `tblpXSpec/YSpec`,
  `*FromText` (`:12-14`). Wired into the parent `w:tblPr` translator
  (`.../w/tblPr/tblPr-translator.js:19,41,51`). The PM table node carries it as
  `tableProperties.floatingTableProperties` (typedef `extensions/table/table.js:47-58, 118`).
  Tested both directions (`tblpPr-translator.test.js`).
- **Paint:** the layout adapter extracts it (`core/layout-adapter/converters/table.ts:762-855`
  → `anchor`/`wrap`) and the layout engine positions it off-flow
  (`_vendor/superdoc/layout-engine/src/layout-table.ts:1319-1338, 1806`;
  `anchors.ts:169-207`). (Full-width anchored tables are deliberately kept inline to avoid
  spurious extra pages — `layout-table.ts:1322-1329`.)
- **UI / bridge:** **NONE.** `src/renderer/bridge/table.ts` has zero `tblpPr`/
  `floatingTableProperties`/float/position references; no ribbon command writes it; there is no
  Table Properties → Positioning dialog. Repo-wide, `floatingTableProperties` has no setter.

**Conclusion:** floating tables are **import-only** — a `.docx` that already has `w:tblpPr`
survives open→save and renders floating, but a user **cannot make a table float** from
inside the app.

### 6. Bottom line — can the engine TODAY "insert an object and move it anywhere, with text wrapping"?

**For a Picture: yes (with caveats).** Insert a picture → Wrap Text → Square → drag it
anywhere (or type a free X/Y) → it paints at an absolute position and body text reflows
around it, and it exports correct OOXML. This is a genuine working canvas interaction —
**for images, square/top-bottom wrap, session-inserted.**

**For everything else: no.** Text boxes and WordArt insert but land inline and can't be
moved; AutoShapes don't insert (stub); tables can't be made to float from the UI. The
**model + converter + paint** substrate is largely there; what's thin is **(a) the
authoring UI** that drives non-image objects onto the floating layer, and **(b) polygon
(Tight/Through) wrap fidelity**.

## Verdict

**🟡 Partial — strong substrate (model + converter + paint), thin authoring layer.**

The "page as a canvas" lower half (OOXML round-trip, absolute paint, z-order, rectangular
text reflow) genuinely **exists and works**. The upper half (UI to put *any* object on the
canvas and move it) works **only for images**. Precise gap list to reach a real Word-grade
canvas:

| # | Gap | Where | Rough size |
|---|-----|-------|-----------|
| G1 | **Generalize the Arrange verbs beyond `image`.** `setImagePosition/Transform/Align/Wrap/ZOrder` + the resize/move overlay are hard-gated to `image` (`insert.ts:273-277`; `image-resize.ts:125,303,428`). Make them operate on `vectorShape` / `shapeContainer` (and ideally the floating table) so any object can be selected, dragged, wrapped, z-ordered. | bridge + overlay | **L** (the keystone unlock) |
| G2 | **AutoShapes insert path.** `Insert.insertShape` is a toast stub (`insert-features.js:148-152`); the `vectorShape` model + view already support `kind` geometries but `getPresetShapeSvg` is stubbed (`VectorShapeView.js:1-2`). Wire preset geometry → a real floating `vectorShape`. | bridge + view | **M** |
| G3 | **Float the inserted Text Box / WordArt.** Both insert inline today (`shape-textbox.js`, `vector-shape.js:350-369`). Give them `isAnchor`/`anchorData`/`wrap` + the Arrange UI (depends on G1). | model + bridge | **M** |
| G4 | **Polygon (Tight/Through) wrap in the paint.** Engine falls back to rectangular; polygon captured but unapplied (`floating-objects.ts:12,147`). Implement polygon exclusion in `computeAvailableWidth`. | layout-engine | **L** |
| G5 | **Floating-table authoring UI.** Converter + paint exist; no setter/dialog writes `floatingTableProperties`. Add Table Properties → Positioning (and/or drag) → write the attr. | bridge + dialog | **M** |
| G6 | **Smaller fidelity gaps:** vertical align top/middle/bottom (`setImageAlign` H-only, `insert.ts:635`); imported-anchor reposition is refused (`insert.ts:609-612`); z-order doesn't re-stack CSS-floated images (`insert.ts:374-380`); Group/Ungroup is a toast (`commands.js:1182`). | bridge/overlay | **S each** |

## What this unlocks

Each Insert feature depends on the floating layer as follows:

- **Shapes** — needs G2 (insert a preset-geometry floating `vectorShape`) + G1 (move/wrap it).
  Pure "object on the canvas"; the paint/z-order already exist.
- **Cover Page** — a template of *floating* text boxes + shapes + images. Needs G3 (floating
  text boxes) + G2 (shapes) so the composed layout lands as a canvas, not stacked inline blocks.
- **Text Box** — needs G3: anchor the existing editable VML text box + G1's Arrange UI to move it.
- **floating Pictures** — **already works** for square/top-bottom (insert → wrap → move →
  reflow → export). Improved by G4 (tight/through) and G6 (vertical align, imported reposition).
- **WordArt** — needs G3 to make the existing `wps:wsp` WordArt node floating + G1 to move it
  (model/export already faithful).
- **floating / movable Tables** — needs G5: a UI/bridge setter for `floatingTableProperties`
  (converter + paint already done).

## Open questions for our discussion

1. **Generalize or special-case?** Do we lift the `image`-gating once (G1, one general
   "selected floating object" abstraction over `image` + `vectorShape` + floating table), or
   add per-type Arrange paths? The general route is more work up front but unblocks Shapes,
   Text Box, WordArt, and floating tables together.
2. **Authoring vs. fidelity priority.** Is the bigger win (a) letting users *create* floats
   (G1–G3, G5) or (b) making existing floats wrap better (G4 polygon)? They're independent.
3. **Polygon wrap** — is rectangular Square/TopAndBottom "good enough" for v1, deferring
   Tight/Through to a later pass? The engine already round-trips the polygon; only the paint
   reflow is missing.
4. **Imported-anchor reposition (G6).** Worth solving the `originalDrawingChildren` "drop on
   save" problem so imported floats become movable, or accept session-inserted-only for v1?
5. **Drawing Canvas semantics** — the canvas frame inserts inline today; should it become a
   true floating container that other shapes nest into (Word's behavior), and does that change
   the model?

## Decision

**TBD — to be decided together.**

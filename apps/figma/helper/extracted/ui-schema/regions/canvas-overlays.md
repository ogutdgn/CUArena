# Canvas Overlays

**Region role:** On-canvas visual chrome — elements that float over / decorate the canvas itself (not inside sidebars). Includes selection affordances, guides, action bar, multiplayer indicators.

**Global behavior:**
- Overlays render above the content but do not affect the scene graph.
- Most overlays appear conditionally (presence driven by selection, mode, hover, or toggles in the view-options dropdown).
- Overlays are not selectable as layers (exception: comment pins, which are out of scope).

**Canonical reference images:**
- Most canvas-overlay imagery is scattered across the corpus. Primary references:
  - `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_01.png` — overall canvas framing
  - `helper/figma_docs/articles/Figma Design/explore-design-files/` — selection + panel interplay
  - Various tutorial articles in Projects/ reference shape-handle imagery but are out-of-corpus-scope (we only look at Figma Design).

---

### canvas-background
- **Scope flag:** functional-in-scope
- **Location:** Fills the area between sidebars and above the toolbar.
- **Default appearance:** Solid flat neutral color. Docs describe default as `#F5F5F5` in light theme, `#1E1E1E` in dark theme (qualitative: light-gray light / near-black dark). Per-page customizable via the Page section of the right panel when nothing is selected.
- **Source articles:** `change-the-background-color-of-the-canvas`, `navigating-ui3`
- **Notes:** Exact hex values belong to ThemeProvider + page background variable; this schema records "neutral background, per-page override possible".

### selection-bounding-box
- **Scope flag:** functional-in-scope
- **When shown:** A single object is selected. Different treatment when parent is selected (see dashed-parent-bounds below).
- **Default appearance:** Solid rectangular outline around the selected object's bounds. Stroke color is a signature Figma selection blue (a specific primary blue hue — exact code handled by ThemeProvider).
- **Composition:**
  - Rectangle outline (1px stroke at default zoom)
  - **W × H label** below the bounding box: small floating label rendered as text, typically with a dark background and white text (qualitative). Shows the object's width × height values.
  - Corner handles at the four corners (small filled squares) — drag to resize
  - Midpoint handles on each edge (small filled squares) — drag to resize a single dimension
  - Rotation cursor appears when the pointer moves *outside* the corners (not a handle — a cursor style change; the docs describe hovering near corners flipping the cursor to a rotation glyph)
- **States:**
  - default — static outline + W×H label
  - actively-resizing — handles may grow or change emphasis; W×H label updates live
  - actively-rotating — rotation angle readout appears near cursor (qualitative; from `adjust-alignment-rotation-position-and-dimensions`)
- **Source articles:** `adjust-alignment-rotation-position-and-dimensions`, `select-layers-and-objects`, `explore-design-files`

### multi-selection-bounding-box
- **Scope flag:** functional-in-scope
- **When shown:** Two or more objects selected simultaneously.
- **Default appearance:** A single bounding box that envelops the union of all selected objects. Individual objects may additionally have their own subdued outlines highlighting their positions inside the union box.
- **Handles:** Same corners + midpoints. Transforming the multi-selection scales / rotates / moves the group as a unit.
- **Source articles:** `select-layers-and-objects`

### dashed-parent-bounds
- **Scope flag:** functional-in-scope
- **When shown:** A child layer is selected; its parent frame / group / section's bounds render as a dashed outline around the parent.
- **Default appearance:** Dashed rectangle with a lighter color than the selection blue — visually distinct to indicate "this is the parent, not the selection".
- **Source articles:** `parent-child-and-sibling-relationships`, `explore-design-files`

### corner-radius-handles
- **Scope flag:** functional-in-scope
- **When shown:** A selected shape (rectangle or frame) has a non-zero corner radius OR the user hovers near its corners while it is editable.
- **Default appearance:** Small circular handles *inside* the shape, positioned near each corner. Dragging them changes the corner radius. When radius is in "Independent corners" mode, each corner has its own handle.
- **Source articles:** `adjust-corner-radius-and-smoothing`

### arc-handles-ellipse
- **Scope flag:** functional-in-scope (ellipse is a supported shape; arc handles are part of its standard editing affordance)
- **When shown:** An ellipse layer is selected.
- **Default appearance:** Small round handles on the ellipse — one at the top / side allowing the user to drag an arc "cut" (creating arcs / sectors) and one controlling inner-radius for ring shapes. Specific handle positions: top of ellipse (sweep) + a smaller handle on the right edge (ratio / inner radius).
- **Source articles:** `arc-tool-create-arcs-semi-circles-and-rings`

### smart-selection-pink-handles
- **Scope flag:** visual-only (smart selection is an advanced feature outside plan/00 §2)
- **When shown:** A selection of equally-distributed objects forms a smart-selection set.
- **Default appearance:** Pink center handles on each object + pink edge spacing handles between them. Clicking marks an object (solid pink); `Delete` reflows.
- **Notes:** We render objects, but we do not compute smart-selection handles. This element is visual-only; if a user arranges objects that in real Figma would trigger smart-selection, our canvas does not surface the handles.

### rotation-cursor
- **Scope flag:** functional-in-scope
- **When shown:** Pointer moves outside a corner of a selected shape (not a selection handle — the cursor itself changes).
- **Default appearance:** Cursor glyph becomes a curved-arrow (rotation) icon.
- **Notes:** This is a cursor style, not a rendered overlay per se, but it is part of the selection chrome.

### snap-and-measure-guides
- **Scope flag:** functional-in-scope (snap / smart guides per plan/00 §2)
- **When shown:** While actively moving / resizing a layer — transient overlays.
- **Default appearance:**
  - **Red guide lines** aligning the moving layer's edges / centers with nearby sibling layers' edges / centers
  - **Measurement labels** at the intersection (small boxed numeric readouts)
  - Appears across the union of alignment axes (horizontal + vertical) as the user drags
- **Source articles:** `adjust-alignment-rotation-position-and-dimensions`, `measure-distances-between-layers`

### layout-guides-canvas
- **Scope flag:** visual-only (layout guides out of functional scope per plan/00 §3)
- **When shown:** Enabled via View menu; visible on the canvas as dotted (canvas guides) or inside frames as solid lines.
- **Default appearance:** Thin dotted / solid lines extending across the canvas or within a frame. Rulers along the top and left edges of the canvas (when enabled) highlight blue when a frame is selected.
- **Notes:** Rendered as visual overlays only if the user toggles them on; we can render them but without real guide-add / guide-drag functionality.

### pixel-grid
- **Scope flag:** visual-only
- **When shown:** Zoom ≥ 400% and Pixel grid enabled in view options.
- **Default appearance:** Fine per-pixel grid overlay.

### action-bar
- **Scope flag:** visual-only (all entries are out of functional scope)
- **When shown:** An object is selected on the canvas — a small floating row of quick-actions near the bottom-center of the canvas.
- **Default appearance:** Rounded-rectangle floating bar with a few icon buttons.
- **Entries (from docs):**
  - Mark as ready for dev — `visual-only` (Dev Mode)
  - Create component (suggest) — `visual-only`
  - Suggest auto layout — `visual-only`
- **Notes:** The action bar renders when a selection exists so the canvas chrome looks like real Figma, but clicking entries is a no-op. `plan/03` decides whether we simply omit the bar entirely or render it disabled.

### mask-outlines
- **Scope flag:** visual-only
- **When shown:** Mask mode toggled in View menu (masks out of functional scope).
- **Default appearance:** Green outlines on masked layers. Not rendered.

### multiplayer-cursors
- **Scope flag:** visual-only
- **When shown:** Always (toggleable in view options) when other collaborators are in the file.
- **Default appearance:** Small arrow + a color-tinted name label anchored to each collaborator's live pointer position.
- **Notes:** Multiplayer entirely out of scope; not rendered.

### cursor-chat-bubble
- **Scope flag:** visual-only
- **Notes:** Ephemeral chat bubble anchored to own cursor during cursor-chat typing. Out of functional scope; not rendered.

### comment-pins
- **Scope flag:** visual-only
- **Notes:** Comments out of functional scope. Not rendered.

### insertion-crosshair
- **Scope flag:** functional-in-scope
- **When shown:** A shape / frame / text tool is active and the pointer is over the canvas; a small crosshair cursor appears indicating where the new object would be placed on click / click-drag.
- **Default appearance:** Plus-sign crosshair, typically rendered in a neutral tint with enough contrast to be visible on both light and dark canvases.
- **Source articles:** `frames-in-figma-design`, `basic-shape-tools-in-figma-design`

### pixel-cursor-box-select-overlay
- **Scope flag:** functional-in-scope
- **When shown:** User click-drags an empty canvas area with no modifier (drag-box / marquee selection).
- **Default appearance:** A semi-transparent rectangle with the selection-blue color, rendered as the user drags. Objects intersecting the box become selected upon release.
- **Source articles:** `select-layers-and-objects`

### canvas-zoom-and-pan
- **Scope flag:** functional-in-scope (canvas navigation per plan/00 §2)
- **Behaviors:**
  - Pan: `Space + drag`, two-finger trackpad slide, arrow keys (Shift = bigger step, scaled to zoom).
  - Zoom: `Cmd/Ctrl + scroll`, pinch, Magic Mouse double-tap, or `Shift + / - / 1 / 2`.
  - Default open: Zoom to fit.
  - Zoom % visible in top-right of the right sidebar (see `regions/right-properties.md`).
- **Source articles:** `navigating-ui3`, `adjust-your-zoom-and-view-options`

### dev-mode-overlays
- **Scope flag:** not rendered (Dev Mode out of scope)
- **Notes:** Annotation dots (green), measurement nodes, ephemeral measure lines, dev-status badges — all exclusive to Dev Mode.

### prototype-overlays
- **Scope flag:** not rendered (Prototype mode out of scope)
- **Notes:** Prototype noodles, `+` plug icons, flow-start badges — all exclusive to Prototype mode.

### spotlight-follower-border
- **Scope flag:** not rendered
- **Notes:** Multiplayer feature.

### component-set-frame-outline
- **Scope flag:** not rendered
- **Notes:** Dashed-purple stroke around component sets. Components out of scope.

### slot-region-highlight
- **Scope flag:** not rendered
- **Notes:** Pink border inside instance slots. Components out of scope.

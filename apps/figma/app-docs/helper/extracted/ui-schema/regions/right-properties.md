# Right Properties Panel

**Region role:** Property editor for the current selection; also host of the Prototype tab and the Inspect / Comment tabs on view-only. Right edge of editor, full window height. The most state-heavy panel — contents change with selection type.

**Anatomy, top → bottom:**
1. Header row — zoom %, view-options dropdown, top-of-panel collaborator chrome (avatar stack + Share button), optional play / present triangle
2. Tabs — **Design** / **Prototype** (edit access); (Comment / Properties on view-only — not rendered)
3. Sub-header — selection actions row: Mask, Create component, Boolean ops, More `…`
4. Body — selection-driven sections

**Global behavior:**
- Width resizable via drag on the left edge of the panel.
- Collapses on `Shift \` (Minimize UI). Selecting a canvas object while minimized temporarily re-expands it.
- Sections appear / hide based on selection (see `state-matrix.md`).

**Canonical reference images:**
- `helper/figma_docs/articles/Figma Design/design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png` — side-by-side Design tab vs Prototype tab
- `helper/figma_docs/articles/Figma Design/navigating-ui3/images/img_06.png` — right panel header with avatar stack and Share button (not directly inspected; referenced per analysis)

---

## 1. Header row

### zoom-percentage-display
- **Scope flag:** functional-in-scope
- **Location:** Top-right corner of panel, header row.
- **Default appearance:** Numeric zoom level (e.g. "100%") rendered as clickable text with a small chevron (`⌄`) indicating a dropdown.
- **States:**
  - default — current zoom shown
  - click on number — opens zoom/view options dropdown (same as chevron)
  - direct edit — some docs imply typing in the % field is supported; exact trigger not confirmed
- **Behavior:** Clicking opens the zoom-and-view-options dropdown. Values update live as the canvas zoom changes (via scroll-with-modifier, pinch, keyboard shortcuts).
- **Reference images:**
  - `helper/figma_docs/articles/Figma Design/design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png`
- **Source articles:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar`, `adjust-your-zoom-and-view-options`

### zoom-and-view-options-dropdown
- **Scope flag:** mixed (most entries visual-only)
- **Location:** Anchored to the zoom % area; opens as a floating menu below.
- **Dropdown entries (from docs):**
  - Zoom in / out / to fit / to selection / custom % — `functional-in-scope` (basic zoom behaviors)
  - Pixel preview (Disabled / 1x / 2x) — `visual-only` (pixel preview out of scope)
  - Pixel grid — `visual-only`
  - Snap to pixel grid — `visual-only`
  - Layout guides — `visual-only`
  - Multiplayer cursors — `visual-only`
  - Outlines (Show outlines, Include hidden layers, Include object bounds) — `visual-only`
  - Property labels — `visual-only`
  - Prototyping (for view-only users) — `visual-only`
- **Reference images:** not directly inspected; `adjust-your-zoom-and-view-options` article is the canonical source for this menu's inventory.
- **Source articles:** `adjust-your-zoom-and-view-options`
- **Notes / gaps:** The dropdown renders with all entries; clicking visual-only entries is a no-op (behavior decided in `plan/03`).

### present-button
- **Scope flag:** visual-only
- **Location:** Panel header row, left of the avatar stack.
- **Default appearance:** Play-triangle icon.
- **Behavior in real Figma:** opens Presentation view in a new browser tab.
- **Reference images:** visible in `design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png` top-center of the header (a play-triangle glyph).

---

## 2. Tabs

### design-tab
- **Scope flag:** functional-in-scope
- **Location:** Below header row, left-aligned.
- **Default appearance:** Text label "Design", active state indicated by a stronger weight / underline.
- **Behavior:** Default tab. Shows property sections according to selection type.
- **Reference images:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png`

### prototype-tab
- **Scope flag:** visual-only
- **Location:** To the right of the Design tab.
- **Trigger / shortcut:** `Shift E` (would toggle to this tab in real Figma).
- **Behavior in real Figma:** swaps the panel body to prototype property sections.
- **In our mock:** the tab button is rendered. Clicking it either does nothing or shows an empty state — decided in `plan/03`.
- **Reference images:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png` (right half of the side-by-side shows Prototype tab active)

### comment-and-properties-tabs
- **Scope flag:** not rendered (view-only variant)
- **Notes:** View-only / View-seat variant of the right panel swaps the tabs to **Comment** / **Properties**. Per `plan/00 §3a`, we always render the edit-access view, so these tabs are never rendered.

---

## 3. Sub-header — selection actions row

**Global:** A single row of buttons that appears below the tabs and changes depending on the selection. Housed to make common selection-aware actions quickly reachable.

### mask-action
- **Scope flag:** visual-only (masks out of functional scope per plan/00 §3 "masks" listed under design-system / content operations)
- **Location:** Sub-header row, left area.
- **Default appearance:** Mask icon (crescent / half-circle glyph).
- **States:** disabled when selection is invalid for masking; hover not covered.
- **Notes:** Visible whenever a selection exists that could be masked; button renders but does not execute.

### create-component-action
- **Scope flag:** visual-only
- **Location:** Sub-header row.
- **Default appearance:** Component icon (four-square rhombus or similar).

### boolean-ops-action
- **Scope flag:** visual-only
- **Location:** Sub-header row.
- **Default appearance:** Dropdown-style button with an icon representing boolean operations + chevron.
- **Dropdown entries when open:** Union / Subtract / Intersect / Exclude / Flatten. All visual-only.

### more-menu
- **Scope flag:** mixed
- **Location:** Sub-header row, far right.
- **Default appearance:** `…` three-dot glyph.
- **Dropdown entries:** overflow of selection-aware actions — copy properties, paste properties, convert to, rename layer, lock, etc. Entries align with plan/00 §2 scope for functional items and §3 for visual-only.

---

## 4. Design-tab body — no selection

### page-section
- **Scope flag:** functional-in-scope
- **Location:** Top of Design tab body when nothing is selected.
- **Default appearance:** Section header "Page" with a color swatch + hex code + Hide-in-exports eye icon.
- **Controls:**
  - Background color swatch — click opens color picker (functional for color change)
  - Hex input — editable text
  - Hide eye — `visual-only` (exports not functional; toggle is rendered)
- **Source articles:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar`, `change-the-background-color-of-the-canvas`

### local-styles-and-variables
- **Scope flag:** visual-only (styles + variables out of scope per plan/00 §3)
- **Location:** Below Page section when nothing is selected.
- **Contents:** Lists of local Text / Color / Effect / Layout-guide styles + Local variables entry + "+ Create" buttons.
- **Notes:** Render with an empty-state ("No local styles") to avoid populating styles we cannot back.

### export-page
- **Scope flag:** visual-only
- **Location:** Bottom of Design tab body (no selection).
- **Default appearance:** Standard Export section control (add `+`, row entries, Export button).

---

## 5. Design-tab body — selection active

### layout-section
- **Scope flag:** mixed
- **Location:** Near top of selection-driven sections (below sub-header).
- **Header states:**
  - default — label "Layout"; shows W / H + lock-aspect toggle + clip-content toggle (frames only)
  - auto-layout-applied — label changes to "Auto layout" (this entire mode is `visual-only` — Auto layout out of scope per plan/00 §3)
- **Controls when in default (non-auto) mode:**
  - W (width) input — `functional-in-scope`
  - H (height) input — `functional-in-scope`
  - Lock-aspect toggle — `functional-in-scope`
  - Resizing per-axis controls (Fixed / Hug / Fill / Scale) — `visual-only` (auto-layout-coupled; Fixed is the only meaningful state without auto layout)
  - Clip content (frames only) — `functional-in-scope`
  - Layout guide sub-section (frames only) — `visual-only` (layout guides out of scope)
  - "Use auto layout" button (when a frame is selected and auto layout not yet applied) — `visual-only`
- **Source articles:** `adjust-alignment-rotation-position-and-dimensions`, `frames-in-figma-design`, `guide-to-auto-layout`

### position-section
- **Scope flag:** functional-in-scope (core transform properties)
- **Controls:**
  - Alignment row (align left / center / right / top / middle / bottom + distribute horizontal / vertical + tidy up) — `functional-in-scope` for basic aligns; `visual-only` for Tidy up (smart-selection advanced).
  - X input — `functional-in-scope`
  - Y input — `functional-in-scope`
  - Rotation input (with glyph) — `functional-in-scope`
  - Flip horizontal / Flip vertical buttons — `functional-in-scope`
  - Corner radius — actually lives in Appearance section (see below); constraints live here too
  - Constraints icon (appears next to X/Y when a layer is inside a frame without auto layout) — `visual-only` (constraints coupling with auto-layout out of scope; basic fixed constraints could be functional — flag for plan/03 decision)
  - Ignore auto layout button (children of auto-layout frames) — `visual-only`
- **Reference images:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png` — shows Position values (X 0, Y 0, alignment row, rotation)
- **Source articles:** `adjust-alignment-rotation-position-and-dimensions`

### appearance-section
- **Scope flag:** mixed
- **Controls:**
  - Visibility eye — `functional-in-scope` (toggle layer hidden)
  - Blend mode dropdown — `visual-only` (blend modes advanced; keep render hook for layer with normal blend)
  - Variable mode swatch (Apply variable mode) — `visual-only` (variables out of scope)
  - Opacity input + slider — `functional-in-scope`
  - Corner radius input — `functional-in-scope` (uniform)
  - Independent corners mode toggle — `functional-in-scope`
  - Corner smoothing — `visual-only`

### typography-section
- **Scope flag:** functional-in-scope
- **Location:** Only visible when a text layer or text range is selected.
- **Controls:**
  - Text-style picker (opens style dropdown) — `visual-only` (text styles out of scope)
  - Font family picker — `functional-in-scope` (basic list of installed fonts)
  - Weight / style dropdown — `functional-in-scope`
  - Size input — `functional-in-scope`
  - Line height — `functional-in-scope`
  - Letter spacing — `functional-in-scope`
  - Horizontal alignment row — `functional-in-scope`
  - Vertical alignment row — `functional-in-scope`
  - Type-settings `…` expand (Basics / Details / Variable tabs: decoration, case, vertical trim, lists, paragraph spacing, truncation, indentation, OpenType features, variable axes) — `visual-only` for advanced tabs; basic decoration/case may be functional (flag for plan/03).
- **Source articles:** `explore-text-properties`

### fill-section
- **Scope flag:** functional-in-scope
- **Controls:**
  - List of fill rows (color swatch + hex + opacity + "Show in exports" checkbox + eye icon + `…` menu)
  - `+` to add a fill
  - Click a swatch → opens color-picker modal (see `regions/floating-overlays.md`)
  - Apply-style icon — `visual-only`
- **Per-row elements:**
  - Swatch — `functional-in-scope`
  - Hex input — `functional-in-scope`
  - Opacity input — `functional-in-scope`
  - Show-in-exports checkbox — `visual-only`
  - Eye (visibility of the fill) — `functional-in-scope`
  - `…` menu (remove, reorder, paste over) — mixed; remove + reorder `functional-in-scope`
- **Source articles:** `guide-to-fills`, `apply-styles-to-layers-and-objects`

### stroke-section
- **Scope flag:** functional-in-scope
- **Controls:**
  - List of stroke rows (color swatch + hex + opacity + eye + `…`)
  - `+` to add a stroke
  - Weight input — `functional-in-scope`
  - Alignment picker (Inside / Center / Outside) — `functional-in-scope`
  - Advanced stroke settings popover (`…` row): dashed / cap / join / end-points / advanced — mixed; basic dashed pattern `functional-in-scope` depending on depth; advanced `visual-only` if needed.
- **Source articles:** `apply-and-adjust-stroke-properties`

### effects-section
- **Scope flag:** functional-in-scope (drop shadow + blur per plan/00 §2)
- **Controls:**
  - List of effect rows (effect type dropdown + X/Y/blur/spread + color + eye + `…`)
  - `+` to add (opens picker: Drop shadow / Inner shadow / Layer blur / Background blur / Noise / Texture / Glass — plan/00 §2 lists drop shadow + blur; others `visual-only`)
- **Source articles:** `apply-effects-to-layers`

### component-section
- **Scope flag:** visual-only
- **Location:** Only visible when a component / instance is selected (which we never enter because components are out of scope); practically this section is never rendered.

### export-section
- **Scope flag:** visual-only (export out of scope per plan/00 §3)
- **Location:** Bottom of Design tab body when a selection exists.
- **Controls:**
  - List of export config rows (scale + suffix + format)
  - `+` to add
  - Gear (Advanced export settings)
  - Preview link
  - Export button
- **Behavior:** All rendering; no actual export executes.

---

## 6. Prototype-tab body (visual-only)

- Entire body is `visual-only`. Contents (per docs) include: Flow starting point, Scroll behavior (Overflow), Interactions, Device, Background, prototype settings. None executes.
- Notes: The tab button still renders. Clicking switches the body to an empty / placeholder state.

---

## 7. Panel container
- **Shape:** Full-height vertical panel docked to the right edge.
- **Background:** Distinct panel background color.
- **Left edge:** Draggable to resize the panel width.
- **Section dividers:** Each section (Layout, Position, Appearance, etc.) is separated by a subtle horizontal rule.
- **Section headers:** Include a label, an optional `+` add button, and sometimes a `…` menu.
- **Reference images:** `design-prototype-and-explore-layer-properties-in-the-right-sidebar/images/img_01.png`.
- **Notes / gaps:** Exact spacing / padding handled by ThemeProvider; qualitative layout preserved.

---

## 8. State-driven visibility summary

See `state-matrix.md` for the authoritative table. Short version:

| Selection | Sections visible (order) |
|---|---|
| Nothing | Page → Local styles → Local variables → Export page |
| Single shape (rect/ellipse/etc.) | Layout (W/H only) → Position → Appearance → Fill → Stroke → Effects → Export |
| Frame | Layout (W/H + Clip content + Layout guide) → Position → Appearance → Fill → Stroke → Effects → Export |
| Text | Layout → Position → Appearance → Typography → Fill → Stroke → Effects → Export |
| Image | Layout → Position → Appearance → (Fill = image properties) → Stroke → Effects → Export |
| Group | Layout → Position → Appearance → Export |
| Multi-mixed | Position → Appearance → Selection colors → Fill (if all have) → Stroke (if all have) → Export |
| Auto-layout frame | (visual-only — not entered) |
| Component / instance | (visual-only — not entered) |

Selection-colors section appears only on mixed selections where at least 2 selected layers share no single fill/stroke.

# Floating Overlays

**Region role:** Non-docked UI surfaces that appear on top of the canvas or anchored to a trigger element. Includes the color picker, context menus, dropdown menus, modals, and toasts.

**Global behavior:**
- Overlays do not reserve layout space — they appear above existing regions and disappear when dismissed.
- Dismissal patterns: `Esc`, click outside, explicit close (X), or completion (Submit / Done).
- Only one of most overlay categories is open at a time (multiple dropdowns can't co-exist in the same position).

**Canonical reference images:**
- Color picker imagery: referenced in `guide-to-fills`, `apply-and-adjust-stroke-properties` articles.
- Context menu imagery: scattered across multiple tutorial and feature articles.

---

### color-picker
- **Scope flag:** functional-in-scope (basic color editing) + mixed (advanced tabs visual-only)
- **Anchor:** Floats adjacent to the swatch that triggered it (Fill row, Stroke row, Effect color, Page background).
- **Trigger:** Click any color swatch in the Fill / Stroke / Effect / Page sections.
- **Default appearance:** Tall rectangular floating panel. Contents from top to bottom:
  1. **Fill-type tabs** (row of icons / short labels): Solid / Gradient (Linear/Radial/Angular/Diamond) / Pattern / Image / Video. Scope:
     - Solid — `functional-in-scope`
     - Linear / Radial / Angular / Diamond gradient — `visual-only` (gradients not in plan/00 §2)
     - Pattern — `visual-only`
     - Image (when color picker is for a fill) — `functional-in-scope` (image fill creates an image layer)
     - Video — `visual-only`
  2. **HSV palette** (2D color field) — click to pick hue / saturation / brightness
  3. **Hue slider** (vertical or horizontal rainbow bar)
  4. **Opacity slider** (checker-pattern track with alpha gradient)
  5. **Eyedropper button** (`I`) — click a pixel on canvas to sample color; `visual-only` in our mock (eyedropper is not listed in plan/00 §2)
  6. **Blend mode dropdown** (per-fill blend mode) — `visual-only`
  7. **Color-model dropdown** (Hex / RGB / CSS / HSL / HSB) — basic Hex/RGB `functional-in-scope`; others `visual-only`
  8. **Hex input** — editable text, `functional-in-scope`
  9. **Color contrast checker** — `visual-only`
  10. **Libraries tab** (styles + variables) — `visual-only`
  11. For Image fill: Fill mode (Fill / Fit / Crop / Tile) + rotation + adjustment sliders — `functional-in-scope` for Fill + Fit; `visual-only` for Crop / Tile / Adjustments (image-manipulation advanced)
  12. For Gradient / Pattern: stops list, flip, rotate, Select source, tile/scale/spacing — `visual-only`
- **Dismissal:** Click outside, press `Esc`, or click another swatch (which re-anchors the picker).
- **Source articles:** `guide-to-fills`, `apply-and-adjust-stroke-properties`, `apply-effects-to-layers`, `adjust-the-properties-of-an-image`

### dropdown-generic
- **Scope flag:** mixed (each dropdown's entries governed by their own scope)
- **Anchor:** Floats immediately below the trigger button (chevron, `…`, tab, named dropdown).
- **Default appearance:** Rectangular floating menu, entries rendered as rows. Row layout typically:
  - Optional icon on left
  - Entry label
  - Optional keyboard shortcut on right (small muted text)
  - Optional submenu indicator `›` on right
- **States:**
  - default — row baseline
  - hover — row highlighted with a subtle background fill
  - disabled — row text muted, non-interactive
  - checkbox / toggle state — leading check or filled circle if the entry is a boolean toggle
- **Examples:**
  - Move tools dropdown (toolbar)
  - Shape tools dropdown (toolbar)
  - Mode-switcher segment already described separately (not a dropdown, a segmented control)
  - Zoom + view-options dropdown (right panel header)
  - File-name dropdown (left panel)
  - Main `…` menu (left panel)
  - Pages selector expanded list
  - Various `…` menus in Fill / Stroke / Effect / Export rows
- **Dismissal:** Click outside, press `Esc`, select an entry.
- **Notes / gaps:** Exact hover animation / transition details not captured; pick a reasonable default (opacity-fade on hover) at build time.

### right-click-context-menu
- **Scope flag:** mixed
- **Anchor:** Floats at cursor position where right-click occurred.
- **Trigger:** Right-click anywhere on canvas, on a layer, or on a layers-panel row. Entries vary with the target's type.
- **Default appearance:** Rectangular menu with grouped entries separated by subtle horizontal dividers.
- **Common entries (from docs, subset):**
  - Copy / Cut / Paste — `functional-in-scope`
  - Paste here (on canvas) — `functional-in-scope`
  - Copy / Paste as code (CSS / iOS / Android) — `visual-only`
  - Copy / Paste as SVG / PNG — `visual-only`
  - Copy link / Copy properties — `visual-only`
  - Select layer / Select deeper layer / Select all with same [fill / stroke / etc.] — basic select `functional-in-scope`; variants `visual-only`
  - Frame selection (`⌥⌘G` / `Alt+Ctrl+G`) — `functional-in-scope` (creates a frame around the selection)
  - Group (`Cmd/Ctrl G`) / Ungroup (`Cmd/Ctrl Shift G`) — `functional-in-scope`
  - Rename — `functional-in-scope`
  - Lock / Unlock — `functional-in-scope`
  - Show / Hide — `functional-in-scope`
  - Delete — `functional-in-scope`
  - Wrap in new section — `functional-in-scope` (sections are in scope)
  - Create component — `visual-only`
  - Boolean ops submenu — `visual-only`
  - Flatten — `visual-only`
  - Mask / Use as mask — `visual-only`
  - Set as thumbnail / Restore default thumbnail — `visual-only`
  - Plugins submenu — `visual-only`
  - Copy/Paste as code submenu — `visual-only`
- **State:** Entries may be disabled, grayed out, or hidden depending on the selection and permissions (e.g., "restrict copying" suppresses Copy-as entries entirely).
- **Dismissal:** Click outside, press `Esc`, or choose an entry.
- **Source articles:** `copy-and-paste-objects`, `select-layers-and-objects`, `boolean-operations`, multiple feature articles
- **Notes / gaps:** Full entry matrix per selection type is not feasible to enumerate here; `plan/03` will define a context-menu registry that respects scope flags.

### rename-modal
- **Scope flag:** functional-in-scope
- **Anchor:** Floats above the canvas (centered or near the triggering element).
- **Trigger:** `Cmd/Ctrl R` with a selection, or right-click → Rename.
- **Default appearance:** Rectangular floating modal. Contents from top to bottom:
  - **Match** field (accepts regex) — `visual-only` for regex complexity; basic text match `functional-in-scope`
  - **Rename to** field — `functional-in-scope`
  - **Token buttons** inline inside the Rename-to field:
    - **Current name** token — inserts "{current_name}" placeholder
    - **Number ↑** token — ascending numeric suffix
    - **Number ↓** token — descending numeric suffix
  - **Start ascending from** number input
  - **Stop descending at** number input
  - **Live Preview** list — shows sample of the new names
  - **Rename** button (primary) + **Cancel** button
- **Source articles:** `edit-objects-on-the-canvas-in-bulk`, `bulk-rename-layers`

### bulk-export-modal
- **Scope flag:** visual-only (export out of functional scope)
- **Anchor:** Centered modal.
- **Trigger:** `Shift+Cmd/Ctrl+E`.
- **Default appearance:** Scrollable list of all configured selections on the current page with thumbnail, scale, format, dimensions, include/exclude checkbox, Export button.
- **Notes:** Rendered per real Figma appearance; Export does nothing.

### toast-notifications
- **Scope flag:** mixed
- **Anchor:** Floats at the bottom of the screen (horizontally centered).
- **Default appearance:** Small dark pill with a short text and optional action / dismiss button.
- **Examples:** "Pixel preview: 2x", "Layer renamed", error / warning messages.
- **States:**
  - appearing — slides in / fades in from bottom
  - visible — stays for a short duration (qualitative, ~2-3 seconds)
  - dismissing — fades out / slides out
- **Notes:** Our mock may use toasts for UI feedback (layer created, etc.) — `plan/03` decides which semantic events trigger toasts.

### keyboard-shortcuts-panel
- **Scope flag:** visual-only
- **Anchor:** Floating, dockable strip along the bottom of the viewport.
- **Trigger:** From Help & resources, or `Ctrl Shift ?`.
- **Default appearance:** Strip showing keyboard-shortcut entries grouped by category.
- **Notes:** Advanced help surface; render if trivial, otherwise render only the trigger.

### help-and-resources-menu
- **Scope flag:** visual-only
- **Anchor:** Bottom-right corner of the screen.
- **Default appearance:** Small floating question-mark button; clicking opens a menu with help links, keyboard shortcuts entry, community resources.
- **Notes:** Render the button; menu entries are all `visual-only`.

### main-menu-dropdown
- **Scope flag:** mixed (most entries visual-only; see `regions/left-navigation.md` → main-menu-button)
- **Anchor:** Floats below / beside the `…` main-menu trigger in the left navigation panel.

### actions-menu-panel
- **Scope flag:** visual-only
- **Anchor:** Floats above / near the Actions toolbar icon; overlays canvas.
- **Trigger:** Click Actions icon in toolbar, or `Cmd/Ctrl K`.
- **Default appearance:** Wide floating panel with a search field at top, sections of entries (AI tools, productivity actions, plugins, etc.), and a Plugins tab.
- **Notes:** Entirely visual-only; if rendered, keep as an empty search panel — else skip opening on click.

### libraries-modal
- **Scope flag:** visual-only
- **Anchor:** Centered modal.
- **Trigger:** Assets tab → Libraries button (`Alt/Opt 3` on some rollouts).
- **Default appearance:** Tabs (This file / Updates / Browse libraries), per-asset publish/swap rows.
- **Notes:** Libraries entirely out of scope; render the trigger (Libraries button), but the modal does not open — or opens as an empty state.

### variables-modal
- **Scope flag:** visual-only
- **Anchor:** Centered modal.
- **Notes:** Variables out of scope — not rendered.

### interaction-details-modal
- **Scope flag:** not rendered
- **Notes:** Prototype mode only. Not rendered.

### compare-changes-modal
- **Scope flag:** not rendered
- **Notes:** Dev Mode only. Not rendered.

### component-playground-modal
- **Scope flag:** not rendered
- **Notes:** Components out of scope.

### inline-preview-window
- **Scope flag:** not rendered
- **Notes:** Prototype feature.

### presentation-view
- **Scope flag:** not rendered
- **Notes:** Opens in new browser tab; out of scope.

### share-modal
- **Scope flag:** visual-only
- **Anchor:** Centered modal.
- **Trigger:** Share button in chrome (see `chrome.md`).
- **Default appearance:** Email invite input, role dropdown, link-sharing scope controls, Open-session controls, Copy-link button.
- **Notes:** Render the Share button in chrome; modal opening is visual-only.

### spotlight-overlay
- **Scope flag:** not rendered
- **Notes:** Multiplayer feature.

### branches-modal / branch-review-modal / conflict-resolution-view / update-from-main-modal
- **Scope flag:** not rendered
- **Notes:** Branching entirely out of scope.

### version-history-sidebar
- **Scope flag:** not rendered

### check-designs-panel
- **Scope flag:** not rendered

### advanced-export-settings-popover
- **Scope flag:** visual-only (inherits from bulk-export-modal scope)

### page-context-menu
- **Scope flag:** mixed
- **Anchor:** Floats at cursor position next to a pages-list row.
- **Trigger:** Right-click on a page row in the pages selector.
- **Entries:** Rename (`functional`), Duplicate (`functional` if within scope — pages are functional; duplicating creates a new page with copied content — flag for plan/03), Delete (`functional`), Copy link (`visual-only`).

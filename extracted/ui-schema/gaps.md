# Gaps

**Purpose:** Items where the corpus + analysis did not give enough information to fully document the UI. Each entry lists: what is missing, why it matters, where it is referenced in the schema, and how to close the gap.

Resolution for most gaps is: user provides a targeted screenshot of the missing state, or the gap is intentionally deferred until the relevant feature slice is built.

---

## Toolbar

- **Hover state** of every toolbar button.
  - Where: `regions/toolbar.md` (most elements list "hover — not covered in corpus").
  - Why it matters: hover feedback is a basic affordance; without a reference we pick a generic "slight background lighten" default.
  - Resolution: user provides a cursor-over-toolbar-button screenshot (any single button is enough to infer the pattern).

- **Vector-edit secondary toolbar — no reference image inspected.**
  - Where: `regions/toolbar.md` → secondary toolbar section.
  - Why it matters: we need this for the Enter-vector-edit feature slice.
  - Resolution: user provides a screenshot while in vector edit mode, OR we search the corpus more aggressively (e.g., `edit-vector-layers/images/*.png`) at build time.

- **Mode-switcher composition discrepancy.**
  - Where: `regions/toolbar.md` → mode-switcher.
  - Issue: `helper/analysis/ui-map.md` says "Design / Prototype / Dev Mode"; the canonical toolbar image shows **Draw / Design / Dev Mode**. Decision: trust the image. Prototype is a right-panel tab only.
  - Status: RESOLVED (no user input needed). Flagged here so the decision is discoverable.

- **Visual-only dropdown expansion behavior.**
  - Where: `regions/toolbar.md` → comment-tools-dropdown and others.
  - Why it matters: if the user clicks a visual-only dropdown (e.g., comment tools), does the menu still expand? Or does the click do nothing?
  - Resolution: `plan/03` decides the global no-op click behavior (plan/00 §8 open decision).

---

## Left navigation panel

- **Exact visual shape + placement of the main-menu (`…`) button.**
  - Where: `regions/left-navigation.md` → main-menu-button.
  - Why it matters: sometimes inline with file name, sometimes separate; corpus imagery has multiple rollout variants.
  - Resolution: user picks a target variant (inline is cleaner) or we default to inline.

- **New narrow left navigation bar — rollout state.**
  - Where: `regions/left-navigation.md` → rolling-out narrow left navigation bar section.
  - Why it matters: this bar is a rolling feature; not every user sees it. Render it in our mock or omit?
  - Resolution: user decides. Default assumption: render it, all icons visual-only.

- **Eye + padlock hover transition details** on layers-tree rows.
  - Where: `regions/left-navigation.md` → layers-tree → states.
  - Resolution: pick a clean "appear on row hover" default; user can refine if the real transition is notably different.

- **Default panel width.**
  - Where: `regions/left-navigation.md` → panel container.
  - Why it matters: we need a sensible default.
  - Resolution: pick a reasonable default (estimate from imagery); refine on build.

- **Active tab indicator** exact shape (underline vs weight vs fill) for File / Assets.
  - Where: `regions/left-navigation.md` → tabs-file-assets.
  - Resolution: pick a clean default (underline + stronger weight) unless user provides a more specific reference.

---

## Right properties panel

- **Zoom-percentage direct-edit behavior** — is typing in the % field supported? Corpus ambiguous.
  - Where: `regions/right-properties.md` → zoom-percentage-display.
  - Resolution: treat as functional (text-input for numeric zoom). Low-risk default.

- **Exact tab indicator** for Design / Prototype.
  - Where: `regions/right-properties.md` → tabs.
  - Resolution: default (underline + stronger weight). Screenshot reference can refine.

- **Section divider styling** — are dividers 1px lines, or spacing + subtle background difference?
  - Resolution: default (subtle 1px divider). Refine on build against the hero image.

- **Selection-driven section visibility when the selection changes rapidly.**
  - Where: `regions/right-properties.md` + `state-matrix.md`.
  - Why: is there a transition / fade, or instant swap?
  - Resolution: instant swap default.

- **`…` More-menu entry inventory.**
  - Where: `regions/right-properties.md` → sub-header → more-menu.
  - Why: the menu's exact entries depend on selection type; corpus doesn't enumerate all combinations.
  - Resolution: build the menu incrementally per feature slice — add entries as the corresponding feature is implemented.

---

## Canvas overlays

- **Selection-box color and handle size** exact reference.
  - Where: `regions/canvas-overlays.md` → selection-bounding-box.
  - Why: qualitative description is good but handle size relative to zoom matters for feel.
  - Resolution: default "Figma blue, small filled square handles" — refine on build.

- **Rotation readout formatting.**
  - Where: `regions/canvas-overlays.md` → selection-bounding-box → states.
  - Resolution: small text labelled "N°" near cursor default.

- **Smart-selection pink handles** — visual-only in our mock; if we choose to not render, omit entirely.
  - Where: `regions/canvas-overlays.md` → smart-selection-pink-handles.
  - Resolution: do not render (cleanest).

- **Action bar** — render (visual-only) or omit?
  - Where: `regions/canvas-overlays.md` → action-bar.
  - Resolution: `plan/03` decision. Default: omit (reduces clutter; bar is mostly Dev-Mode / component actions).

---

## Floating overlays

- **Hover animation** for dropdown rows, context menus.
  - Where: `regions/floating-overlays.md` → dropdown-generic.
  - Resolution: subtle background fill on hover default.

- **Toast duration and stacking** behavior.
  - Where: `regions/floating-overlays.md` → toast-notifications.
  - Resolution: 3-second auto-dismiss default, single-toast at a time; `plan/03` can refine.

- **Color-picker exact sub-tabs** behavior when switching fill type.
  - Where: `regions/floating-overlays.md` → color-picker.
  - Resolution: functional for Solid / Image fills; visual-only tabs for Gradient / Pattern / Video — flagged inline in the schema.

- **Context-menu full entry matrix per selection type.**
  - Where: `regions/floating-overlays.md` → right-click-context-menu.
  - Resolution: `plan/03` defines a context-menu registry; we build entries per slice.

---

## Chrome

- **Right-panel-header collaborator chrome** — image img_06 referenced but not directly inspected.
  - Where: `chrome.md` → avatar-stack + present + share layout.
  - Resolution: inspect the specific image at build time or user confirms the row order (avatar-stack → present → share).

- **Share button exact style** — fill color, padding, label.
  - Where: `chrome.md` → share-button.
  - Resolution: signature Figma primary color for fill default; user can refine.

- **"Ask to edit" button** in view-only — not rendered, documented only.
  - Where: `chrome.md` → view-only chrome variants.
  - Resolution: no action needed; noted for completeness.

---

## Theme / rendering

- **Dark-theme color tokens.**
  - Where: applies across all region files — descriptions are theme-agnostic but the corpus imagery is light-theme.
  - Resolution: user fills dark-theme tokens in the ThemeProvider. Not a UI-schema gap per se; noted for pipeline awareness.

- **UI3 vs pre-UI3 image filtering.**
  - Where: applies across all region files.
  - Status: when inspecting images, we prefer ones consistent with `navigating-ui3` and `access-design-tools-from-the-toolbar` canonical refs.
  - Resolution: resolved by convention; no open action.

---

## Meta

- **How "visual-only" is visually marked in the mock's development** (e.g., small "WIP" / "not implemented" badge in dev builds?).
  - Status: deferred to `plan/03`.

- **Logger event emission** for clicks on visual-only elements.
  - Status: deferred to `plan/03` (plan/00 §8 open decision).

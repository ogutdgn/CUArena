# View layer outlines

- **Category:** layers
- **One-line summary:** Show all layers as wireframe outlines on the canvas, including hidden layers; useful for spotting structure.

## Triggers
- Shortcut:
  - Mac: `⌘ ⇧ O`
  - Windows: `Ctrl Shift O`
- Right sidebar zoom-and-view-options dropdown → **Show outlines** entry.

## Preconditions
- Editor view active.

## Inputs
- Keyboard shortcut OR menu toggle.

## Behavior
1. Toggle on: every layer (visible or hidden) renders as a 1-px wireframe outline on the canvas, with no fill/stroke/effect.
2. Selection still functions normally (you can click outlines to select).
3. Hidden layer outlines render in a distinct dim style; they remain unselectable via canvas click unless their `visible` flag is restored.
4. Sub-options in the view dropdown:
   - **Include hidden layers** — toggle whether hidden-layer outlines render.
   - **Include object bounds** — toggle whether object-level bounds render alongside path outlines.

## Outputs
- **Scene graph changes:** none.
- **Editor state:** outline-view flag toggled.

## UI feedback
- Canvas swaps to wireframe mode.

## Side effects
- Undo stack: unaffected (view-only state).

## Related UI schema entries
- `regions/right-properties.md` → zoom-and-view-options dropdown
- `regions/canvas-overlays.md` → outline-rendering layer

## Semantic event(s) candidate
- `toggle_layer_outlines { to_state, sub_option?: "include_hidden" | "include_object_bounds", trigger: "shortcut" | "view_menu" }`

## Source articles
- `view-layer-outlines-in-figma-design`
- `toggle-visibility-to-hide-layers`

## Notes / gaps
- Outline view is a read-only render mode; edits still apply to the underlying scene graph.

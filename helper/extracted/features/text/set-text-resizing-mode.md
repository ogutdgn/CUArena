# Set text resizing mode

- **Category:** text
- **One-line summary:** Switch a text layer between Auto-width, Auto-height (wrap), and Fixed size.

## Triggers
- Right-sidebar **Layout** section → Resizing dropdown.
- Implicit: dragging the bounding box on canvas auto-switches the resizing mode to **Fixed size** (corpus warning).
- Implicit on creation: single-click sets Auto-width; click-and-drag sets Fixed size.

## Preconditions
- A text layer is selected.

## Inputs
- Pick one of:
  - `Auto width` — width grows with content; new lines only via Enter.
  - `Auto height` — width fixed, height grows; text wraps automatically when overflowing width.
  - `Fixed size` — both dimensions fixed; text wraps; vertical overflow possible.

## Behavior
1. Switching to Auto-width: width recomputes to fit content; explicit width is dropped.
2. Switching to Auto-height: width is preserved; height recomputes to fit wrapped content.
3. Switching to Fixed size: current dimensions are frozen.

## Outputs
- **Scene graph changes:** `resizingMode: "auto_width" | "auto_height" | "fixed"`. Width/height may be recomputed.
- **Selection changes:** none.

## UI feedback
- Resizing dropdown updates.
- Canvas re-renders with new bounding box behavior.

## Side effects
- Undo stack: one entry per change.
- Side dependency: vertical alignment effective only on Fixed size (see `set-text-vertical-align.md`).
- Side dependency: max-lines / truncate available on Auto-height or Auto-width.

## Related UI schema entries
- `regions/right-properties.md` → layout-section → resizing-dropdown

## Semantic event(s) candidate
- `set_text_resizing_mode { layer_id, from: mode, to: mode, trigger: "dropdown" | "auto_on_drag" }`

## Source articles
- `adjust-text-dimensions-and-resizing`

## Notes / gaps
- Auto-on-drag: dragging the canvas bounding-box changes resizing to Fixed; engine should emit the resize event AND a `set_text_resizing_mode` event so the trajectory is reproducible.

# Add canvas guide (ruler-dragged guide)

- **Category:** region-tools
- **One-line summary:** Drag from the rulers to add a horizontal or vertical guide line spanning the page.

## Triggers
- Show rulers (`⇧ R`).
- Drag from horizontal or vertical ruler onto canvas.

## Preconditions
- Rulers visible.

## Inputs
- Pointer drag from ruler.

## Behavior
1. Drag horizontal ruler down → vertical guide line at the drop X.
2. Drag vertical ruler right → horizontal guide line at the drop Y.
3. Guides snap to integer pixels.
4. To remove: drag back to ruler, or right-click → **Remove guide**.

## Outputs
- **Scene graph changes:** page's `canvas_guides` array updated.

## UI feedback
- Guide line on canvas.

## Side effects
- Undo stack: per guide-add/remove.

## Related UI schema entries
- `regions/canvas-overlays.md` → rulers, canvas-guides

## Semantic event(s) candidate
- `add_canvas_guide { axis: "x" | "y", position, trigger: "ruler_drag" }`
- `remove_canvas_guide { guide_id, trigger }`

## Source articles
- `add-guides-to-the-canvas-or-frames`

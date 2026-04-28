# Set linear gradient fill

- **Category:** fills
- **One-line summary:** Switch a fill to a linear gradient (a progressive transition between two or more color stops in a straight line).

## Triggers
- Color picker open → click **Gradient** in fill-type row → from gradient-type dropdown select **Linear**.

## Preconditions
- Picker open with the fill targeted.

## Inputs
- Fill-type click + dropdown selection.

## Behavior
1. Fill type set to `gradient` with subtype `linear`.
2. Default config: two color stops at 0% and 100% along a straight axis (default direction unspecified by docs — typical is vertical).
3. On canvas, a gradient handle (anchor + tip + perpendicular handle) appears bound to the layer. Drag endpoints to change angle and length; color stops can be edited inline (see `edit-gradient-stop.md`).
4. Picker shows the gradient color slider with stop swatches and `+` / `-` for stops, plus **Flip gradient** and **Rotate gradient** buttons.

## Outputs
- **Scene graph changes:** fill's type → `gradient`, subtype → `linear`, `gradient_handle` (start/end points), `stops: [{position, color, opacity}, ...]`.
- **Selection changes:** none.

## UI feedback
- On-canvas gradient handle visible on the selected layer while picker is open.
- Picker shows gradient slider + stop list.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → gradient-controls
- `regions/canvas-overlays.md` → gradient-handle

## Semantic event(s) candidate
- `set_fill_type { fill_index, to_type: "linear_gradient", from_type, trigger: "picker_type" }`
- `set_gradient_handle { layer_ids, fill_index, from, to, trigger: "canvas_drag" }`

## Source articles
- `use-gradients-as-a-fill-or-stroke`
- `guide-to-fills`

## Notes / gaps
- Initial direction (vertical vs horizontal vs diagonal) is not pinned by the corpus.
- Gradient applies to **strokes** as well as fills; same picker config — separate stroke spec to be added if needed.

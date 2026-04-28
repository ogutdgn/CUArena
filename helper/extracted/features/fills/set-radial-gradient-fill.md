# Set radial gradient fill

- **Category:** fills
- **One-line summary:** Switch a fill to a radial gradient (circular gradient with one color at the center transitioning to another at the edge).

## Triggers
- Color picker → fill type **Gradient** → gradient-type dropdown **Radial**.

## Preconditions
- Picker open with the fill targeted.

## Inputs
- Fill-type click + dropdown.

## Behavior
1. Fill type → `gradient`, subtype → `radial`.
2. Default config: two stops at 0% (center) and 100% (edge); default radius = layer extent.
3. On-canvas handle: center point + radius handle to drag.
4. Picker controls: stop slider + `+` / `-`, **Flip**, **Rotate**.

## Outputs
- **Scene graph changes:** fill type, subtype `radial`, center+radius handle, stops array.
- **Selection changes:** none.

## UI feedback
- Canvas: center dot + radius drag handle on the selected layer.
- Picker: gradient slider with stops.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → gradient-controls
- `regions/canvas-overlays.md` → gradient-handle

## Semantic event(s) candidate
- `set_fill_type { fill_index, to_type: "radial_gradient", from_type, trigger: "picker_type" }`
- `set_radial_handle { layer_ids, fill_index, center, radius_x, radius_y, trigger: "canvas_drag" }`

## Source articles
- `use-gradients-as-a-fill-or-stroke`

## Notes / gaps
- Whether radius is single-value or x/y separate (elliptical) is not directly stated — Figma supports stretching the radial via separate handles.

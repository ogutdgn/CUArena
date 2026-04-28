# Set angular gradient fill

- **Category:** fills
- **One-line summary:** Switch a fill to an angular (conic) gradient that progresses clockwise from a starting position.

## Triggers
- Color picker → fill type **Gradient** → gradient-type dropdown **Angular**.

## Preconditions
- Picker open with the fill targeted.

## Inputs
- Fill-type click + dropdown.

## Behavior
1. Fill type → `gradient`, subtype → `angular`.
2. Default: two stops at 0° and 360° (or 0% and 100% along the rotation).
3. Stops can be repositioned to create softer or harsher angles.
4. On-canvas handle controls: center + start-angle + radius.
5. Picker controls: stop slider, `+` / `-`, **Flip**, **Rotate**.

## Outputs
- **Scene graph changes:** fill type set; stops + handle config.
- **Selection changes:** none.

## UI feedback
- Canvas handle.
- Picker stop slider.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → gradient-controls
- `regions/canvas-overlays.md` → gradient-handle

## Semantic event(s) candidate
- `set_fill_type { fill_index, to_type: "angular_gradient", from_type, trigger: "picker_type" }`

## Source articles
- `use-gradients-as-a-fill-or-stroke`

## Notes / gaps
- Visual handle layout (where the start-angle indicator sits) not explicitly enumerated.

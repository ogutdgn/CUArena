# Use color wheel (saturation square + hue slider)

- **Category:** color
- **One-line summary:** Drag the picker's saturation/value square and hue slider to choose a color visually.

## Triggers
- Color picker open.
- Pointer-down + drag inside the saturation/value 2D square (the "color palette").
- Pointer-down + drag on the hue slider (1D vertical or horizontal strip on the side of the square).

## Preconditions
- Picker open.

## Inputs
- Pointer drag inside the SV square (selects S = X axis, B/V = Y axis).
- Pointer drag on the hue slider (selects H).
- Click without drag = jump-to-position.

## Behavior
1. Pointer-down on a position in the square sets S/B to that position.
2. Drag updates color live (every frame / throttled).
3. Pointer-up commits the drag as one undo step (with any other picker edits in the same session).
4. Hue slider works analogously; changing hue keeps S/B values intact.

## Outputs
- **Scene graph changes:** target color updated continuously during drag, finalized on release.
- **Selection changes:** none.

## UI feedback
- Selected position rendered as a small ring on the SV square.
- Hue slider handle moves to the selected hue position.
- Numeric fields (HEX/RGB/HSB/HSL/CSS) update live.
- Canvas updates live.

## Side effects
- Undo stack: one entry per picker session (continuous drag inside one picker session = one entry).

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → saturation-square, hue-slider

## Semantic event(s) candidate
- `set_color_wheel { layer_ids, target, fill_index?, from_color, to_color, trigger: "wheel_drag" | "hue_drag" | "wheel_click" }`

## Source articles
- `update-fills-using-the-color-picker`

## Notes / gaps
- Picker documents number labels in its tour ("8. Use the slider to adjust the hue.") — exact orientation (vertical vs horizontal) not stated; image references show vertical layout.
- Whether hue is a slider or a wheel: corpus consistently calls it a slider.

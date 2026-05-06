# Set diamond gradient fill

- **Category:** fills
- **One-line summary:** Switch a fill to a diamond gradient (four-pointed gradient starting from the center; width and height adjustable independently).

## Triggers
- Color picker → fill type **Gradient** → gradient-type dropdown **Diamond**.

## Preconditions
- Picker open with the fill targeted.

## Inputs
- Fill-type click + dropdown.

## Behavior
1. Fill type → `gradient`, subtype → `diamond`.
2. Default: two stops; center fixed at layer center.
3. Width and height of the diamond can be changed independently via canvas handles.
4. Picker controls: stops + flip + rotate.

## Outputs
- **Scene graph changes:** fill subtype `diamond`; handle params (center, width, height); stops.
- **Selection changes:** none.

## UI feedback
- On-canvas diamond handle (4 vertex pulls).
- Picker stop slider.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → gradient-controls
- `regions/canvas-overlays.md` → gradient-handle

## Semantic event(s) candidate
- `set_fill_type { fill_index, to_type: "diamond_gradient", from_type, trigger: "picker_type" }`

## Source articles
- `use-gradients-as-a-fill-or-stroke`

## Notes / gaps
- Independent W/H control mechanic per the article: "You can adjust the width and height of the gradient individually."

# Set solid fill

- **Category:** fills
- **One-line summary:** Set a fill to a single solid color via the color picker.

## Triggers
- Color picker open on a fill swatch → click **Solid** in the fill-type icons row → choose color.
- Or directly edit color via hex/RGB/HSB/wheel/eyedropper while the fill is already in solid mode.

## Preconditions
- Picker open with the fill targeted.

## Inputs
- See `color/*` specs for inputs (hex / RGB / HSB / HSL / CSS / wheel / eyedropper / styles / variables).

## Behavior
1. If the fill type is currently gradient/image/pattern/video, switching to **Solid** discards the type-specific config (gradient stops, image source, etc.) and keeps just a single solid color.
2. Subsequent edits set the color value through any of the picker's inputs.

## Outputs
- **Scene graph changes:** the fill's `type` set to `"solid"`; `color` and `opacity` set; gradient/image/pattern fields cleared.
- **Selection changes:** none.

## UI feedback
- Picker mode reflects "Solid".
- Canvas re-renders with the solid color.

## Side effects
- Undo stack: one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → fill-type-row, color inputs
- `regions/right-properties.md` → fill-section → fill-row swatch

## Semantic event(s) candidate
- `set_fill_type { layer_ids: [...], fill_index, from_type, to_type: "solid", trigger: "picker_type_button" }`
- `set_fill_color { layer_ids: [...], fill_index, from_color, to_color, trigger }`  // see color/ specs

## Source articles
- `guide-to-fills`
- `update-fills-using-the-color-picker`

## Notes / gaps
- Whether switching back from solid to gradient (later) restores prior gradient config is not documented; treat as a fresh gradient default.

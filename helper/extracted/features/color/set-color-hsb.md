# Set color via HSB / HSL inputs

- **Category:** color
- **One-line summary:** Set color by typing H / S / B (or H / S / L) values when the color picker's color-model dropdown is HSB or HSL.

## Triggers
- Color picker open, color-model dropdown set to **HSB** or **HSL**.
- Type into the H, S, B/L input fields.

## Preconditions
- Picker open and color-model dropdown set to HSB or HSL.

## Inputs
- Keyboard typing.
  - **HSB:** H = `0-360°`, S = `0-100%`, B = `0-100%`.
  - **HSL:** H = `0-360°`, S = `0-100%`, L = `0-100%`.

## Behavior
1. User selects HSB or HSL from color-model dropdown.
2. Three numeric fields exposed.
3. Editing a channel commits live; canvas updates.
4. Other model fields (HEX, RGB, CSS, the other of HSB/HSL) update to reflect.

## Outputs
- **Scene graph changes:** target color updated for selected layer(s) on the relevant property.
- **Selection changes:** none.

## UI feedback
- Saturation/value square (the 2D color picker) repositions its dot to match.
- Hue slider repositions its handle.
- Other model fields update.

## Side effects
- Undo stack: one entry per picker session that produces a change.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → color-model-dropdown, channel inputs, saturation-square, hue-slider

## Semantic event(s) candidate
- `set_color_hsb { layer_ids: [...], target, fill_index?, from_hsb, to_hsb, trigger: "picker_input" }`
- `set_color_hsl { ... }`

## Source articles
- `update-fills-using-the-color-picker`
- `about-color-models`

## Notes / gaps
- Real Figma exposes both HSB and HSL via the same dropdown along with RGB / HEX / CSS — confirmed in `update-fills-using-the-color-picker`. They round-trip to RGB internally.
- HSB is sometimes called HSV elsewhere; corpus uses HSB.

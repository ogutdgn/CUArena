# Set color via RGB inputs

- **Category:** color
- **One-line summary:** Set color by typing R / G / B values when the color picker's color-model dropdown is RGB.

## Triggers
- Color picker open, color-model dropdown set to **RGB**.
- Type into the R, G, or B input fields.

## Preconditions
- Picker open.
- Color-model dropdown set to RGB (default in many cases is HEX; user must switch).

## Inputs
- Keyboard typing — integers `0-255` per channel. Out-of-range values clamp.
- Commit per field on Enter / Tab / blur.

## Behavior
1. User clicks the color-model dropdown and selects RGB (or starts in RGB).
2. Three numeric fields are exposed for R, G, B.
3. Editing one channel commits its change; the canvas updates live.
4. Other model fields (HEX, HSB, HSL, CSS) update to reflect the new color.

## Outputs
- **Scene graph changes:** target color updated for selected layer(s) on the relevant property.
- **Selection changes:** none.

## UI feedback
- Live canvas update.
- HEX / HSB / HSL / CSS fields update to mirror.

## Side effects
- Undo stack: one entry per commit; rapid scrubbing across channels coalesces to one entry per picker session.

## Related UI schema entries
- `regions/floating-overlays.md` → color-picker → color-model-dropdown, channel inputs

## Semantic event(s) candidate
- `set_color_rgb { layer_ids: [...], target, fill_index?, from_rgb, to_rgb, trigger: "picker_input" }`

## Source articles
- `update-fills-using-the-color-picker`
- `about-color-models`

## Notes / gaps
- Real Figma exposes RGB integers per channel `0-255`. Float-style RGB (`0.0-1.0`) is not documented in the corpus; not supported.
- Scrubbing a channel via drag is documented in some Figma controls but not explicitly here for RGB; treat scrub as supported parallel to text input.
